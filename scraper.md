# Scraper Design Ideas

## System Config

- html_root_dir:
- json_root_dir:
- read_order:
  - web
  OR
  - file
  OR
  - file
  - web
- write_contents: true*|false
- write_backup: true*|false

## Link Config

- url example: `https://www.example.com/foo/bar`
- page_type: demo_page_type   # need naming convention
- read_order: (sim. sys)
- write_contents: (sim. sys)
- write_backup: (sim. sys)

## Pipeline

- pipeline (entrypoint) accepts link, passes to scraper:
  - url example: `htts://www.example.com/foo/bar`
  - page_type: demo_page_type
- scraper uses details to scrape HTML (from web or file), returns:
  - url
  - page_type
  - html contents
- pipeline accepts scraper output, uses page_type to pick a parser,
  instantiates, passes scraper output to parser instance
- parser uses details to parse HTML, returns
  - url: http
  - page_type
  - json_schema/type
  - JSON contents
- pipeline accepts parser output, uses page_type and/or json_schema/type
  to pick one or more transformer, instantiates each, passes parser output
  to each instance
- transformer uses details to transform JSON, does one of the following:
  - returns any combination of 1 or more of the following:
    - entrypoint link:
      - url
      - page_type
    - transformer link:
      - url: http
      - page_type
      - json_schema/type
      - JSON contents
- pipeline accepts each transformer output:
  - for an entrypoint link, passes to pipeline entrypoint to "recursively"
    start the process
  - for a transformer link: determines the correct transformer, instantiates,
    and passes the output
