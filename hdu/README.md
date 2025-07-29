### HDU Problems Scraper

`hduedu.py` is a Python script that scrapes problems from the [HDU Problems Archive](https://acm.hdu.edu.cn/listproblem.php?vol=1). It converts plain HTML problems from parquet (in the form of `url, html`) to structured data in jsonl (`url, title, problem_description, unprocessed_input, unprocessed_output, unit_tests, language, has_image`).

To run the script, simply install the requirements and run `python hduedu.py`.

In the first run with the current `hdu.parquet`, we found several problem pages to be empty. These include:

- https://acm.hdu.edu.cn/showproblem.php?pid=1790
- https://acm.hdu.edu.cn/showproblem.php?pid=1910
- https://acm.hdu.edu.cn/showproblem.php?pid=6272
- https://acm.hdu.edu.cn/showproblem.php?pid=6269
- https://acm.hdu.edu.cn/showproblem.php?pid=6270
- https://acm.hdu.edu.cn/showproblem.php?pid=6275
- https://acm.hdu.edu.cn/showproblem.php?pid=6044
- https://acm.hdu.edu.cn/showproblem.php?pid=6268
- https://acm.hdu.edu.cn/showproblem.php?pid=6274
- https://acm.hdu.edu.cn/showproblem.php?pid=6273
- https://acm.hdu.edu.cn/showproblem.php?pid=5169
- https://acm.hdu.edu.cn/showproblem.php?pid=6266
- https://acm.hdu.edu.cn/showproblem.php?pid=6396
- https://acm.hdu.edu.cn/showproblem.php?pid=3593
- https://acm.hdu.edu.cn/showproblem.php?pid=6271
- https://acm.hdu.edu.cn/showproblem.php?pid=6265
- https://acm.hdu.edu.cn/showproblem.php?pid=6267

Aside from these pages, the script converted all other problems to the structured data in `hdu.jsonl`.