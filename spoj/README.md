### SPOJ.COM Problems Scraper

`spoj.py` is a Python script that scrapes problems from the [SPOJ Problems Archive](https://www.spoj.com/problems/classical/). It converts plain HTML problems from parquet (in the form of `url, html`) to structured data in jsonl (`url, title, problem_description, unprocessed_input, unprocessed_output, unit_tests, language, has_image`).

To run the script, simply install the requirements and run `python spoj.py`.

Due to inconsistent formatting and empty pages, many links were skipped. These are noted with `{"Failed": true}` in the `spoj.jsonl` output file.