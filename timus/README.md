### TIMUS.RU Problems Scraper

`timus.py` is a Python script that scrapes problems from the [Timus Problems Archive](https://acm.timus.ru/problemset.aspx). It converts plain HTML problems from parquet (in the form of `url, html`) to structured data in jsonl (`url, title, problem_description, unprocessed_input, unprocessed_output, unit_tests, language, has_image`).

To run the script, simply install the requirements and run `python timus.py`.

Any failed parses are noted with `{"Failed": true}` in the `timus.jsonl` output file.
