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
    return soup.find("h1").text


def extract_problem_description(soup):
    description_title_div = soup.find(
        "div", class_="panel_title", string="Problem Description"
    )
    if description_title_div:
        description_div = description_title_div.find_next_sibling(
            "div", class_="panel_content"
        )
        description = (
            "\Problem Description\n" + description_div.text if description_div else ""
        )
    else:
        description = ""

    input_title = soup.find("div", class_="panel_title", string="Input")
    if input_title:
        input_div = input_title.find_next_sibling("div", class_="panel_content")
        inputs = "\Input\n" + input_div.text if input_div else ""
    else:
        inputs = ""

    output_title = soup.find("div", class_="panel_title", string="Output")
    if output_title:
        output_div = output_title.find_next_sibling("div", class_="panel_content")
        outputs = "\Output\n" + output_div.text if output_div else ""
    else:
        outputs = ""

    return description + inputs + outputs


def extract_unprocessed_input(soup):
    input_title = soup.find("div", class_="panel_title", string="Sample Input")
    if input_title:
        input_div = input_title.find_next_sibling("div", class_="panel_content")
        inputs = input_div.text if input_div else ""
    else:
        inputs = ""

    return inputs


def extract_unprocessed_output(soup):
    output_title = soup.find("div", class_="panel_title", string="Sample Output")
    if output_title:
        output_div = output_title.find_next_sibling("div", class_="panel_content")
        outputs = output_div.text if output_div else ""
    else:
        outputs = ""

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
    panels = soup.find_all("div", class_="panel_content")
    for panel in panels:
        if panel.find("img"):
            return True
    return False


def process_row(row):
    url = row["url"]
    html = row["html"]

    soup = BeautifulSoup(html, "html.parser")

    try:
        title = extract_title(soup)
    except:
        title = ""
        logging.warning(f"Failed to extract title for URL: {url}")

    try:
        problem_description = extract_problem_description(soup)
    except:
        problem_description = ""
        logging.warning(f"Failed to extract problem description for URL: {url}")

    try:
        u_input = extract_unprocessed_input(soup)
    except:
        u_input = ""
        logging.warning(f"Failed to extract unprocessed input for URL: {url}")

    try:
        u_output = extract_unprocessed_output(soup)
    except:
        u_output = ""
        logging.warning(f"Failed to extract unprocessed output for URL: {url}")

    try:
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
    df = pd.read_parquet("hdu.parquet")

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
    with open("hdu.jsonl", "w") as f:
        for problem in results:
            f.write(json.dumps(problem) + "\n")


if __name__ == "__main__":
    main()