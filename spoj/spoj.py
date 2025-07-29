import cohere
import json
import logging
import multiprocessing
import os
import pandas as pd
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from langdetect import detect
from tqdm import tqdm


def extract_title(soup):
    return soup.find(id="problem-name").text


def extract_problem_description(soup):
    problem_body = soup.find("div", id="problem-body")

    description = "Problem Description\n"

    for child in problem_body.find_all():
        if child.text == "Example":
            break
        description += child.text + "\n"

    return description


def extract_unprocessed_input(soup):
    examples_section = soup.find_all("pre")[-1]
    inputs = ""
    for child in examples_section.children:
        if child.string == "Input:":  # Skip the input title
            continue
        if child.string == "Output:":  # Stop at the output title
            break
        inputs += str(child)

    return inputs


def extract_unprocessed_output(soup):
    examples_section = soup.find_all("pre")[-1]
    outputs = ""
    found_output = False
    for child in examples_section.children:
        if child.string == "Output:":
            found_output = True
            continue
        if found_output:
            outputs += str(child)

    return outputs


def extract_unit_tests(inputs, outputs, problem):
    prompt = f"""
    Given the following problem with its inputs and outputs, format the inputs and outputs to a list of dictionaries of variables with ‘input’ and ‘output’ keys.
    For example, this should look like [ {{"input": {{"n”: 2, “a”: [3, 1]}}, "output": 6}},  {{"input": {{"n”: 5, “a”: [7, 3, 9, 6, 12]}}, "output": 52}} ].
    Do not include any additional text in the output aside from the list of dictionaries.

    Problem:
    {problem}

    Inputs:
    {inputs}

    Outputs:
    {outputs}
    """

    co = cohere.Client(
        base_url="https://stg.api.cohere.ai", api_key=os.getenv("cohere_key")
    )
    retries = 3
    for _ in range(retries):
        try:
            response = co.chat(
                model="command-r-plus-08-2024-synth-a100-gg",
                message=prompt,
                temperature=0.3,
            )
        except:
            continue
        if response:
            try:
                return json.loads(response.text)
            except:
                continue

    return None


def has_image(soup):
    problem_body = soup.find("div", id="problem-body")
    return bool(problem_body.find("img"))


def process_row(row):
    url = row["url"]
    html = row["html"]
    has_failed = False

    soup = BeautifulSoup(html, "html.parser")

    try:
        title = extract_title(soup)
    except:
        has_failed = True
        title = ""
        logging.warning(f"Failed to extract title for URL: {url}")

    try:
        problem_description = extract_problem_description(soup)
    except:
        has_failed = True
        problem_description = ""
        logging.warning(f"Failed to extract problem description for URL: {url}")
    if problem_description == "":
        has_failed = True

    try:
        u_input = extract_unprocessed_input(soup)
    except:
        has_failed = True
        u_input = ""
        logging.warning(f"Failed to extract unprocessed input for URL: {url}")

    try:
        u_output = extract_unprocessed_output(soup)
    except:
        has_failed = True
        u_output = ""
        logging.warning(f"Failed to extract unprocessed output for URL: {url}")

    try:
        if has_failed:
            unit_tests = None
        else:
            unit_tests = extract_unit_tests(u_input, u_output, problem_description)
    except:
        unit_tests = None
        logging.warning(f"Failed to extract unit tests for URL: {url}")

    try:
        language = detect(problem_description)
    except:
        language = "unknown"
        logging.warning(f"Failed to detect language for URL: {url}")

    try:
        has_img = has_image(soup)
    except:
        has_img = False
        logging.warning(f"Failed to detect image for URL: {url}")

    if has_failed:
        return {"Failed": True}

    return {
        "url": url,
        "title": title,
        "problem_description": problem_description,
        "unprocessed_input": u_input,
        "unprocessed_output": u_output,
        "unit_tests": unit_tests,
        "language": language,
        "has_image": has_img,
    }


def main():
    load_dotenv()
    logging.basicConfig(level=logging.WARNING)
    df = pd.read_parquet("spoj.parquet")

    num_cores = multiprocessing.cpu_count() - 1  # Leave one core free

    with multiprocessing.Pool(num_cores) as pool:
        # tqdm progress bar
        results = list(
            tqdm(
                pool.imap(process_row, df.to_dict("records")),
                total=len(df),
                desc="Processing problems",
            )
        )

    # Write results to JSONL file
    with open("spoj.jsonl", "w") as f:
        for problem in results:
            f.write(json.dumps(problem) + "\n")


if __name__ == "__main__":
    main()