"""The main entrypoint of the application."""

import typer
from loguru import logger
from rich.console import Console
from rich.logging import RichHandler

logger.configure(handlers=[{"sink": RichHandler(markup=True), "format": "{message}"}])
app = typer.Typer()
console = Console()


@app.command()
def run_pipeline() -> None:
    """Run the scraping process."""
    from scraper.pipeline import Pipeline  # noqa: PLC0415

    config = {
        "html_root_dir": "./data/html-data",
        "json_root_dir": "./data/json-data",
        "read_sequence": ["file"],
        "write_content": True,
        "write_backup": True,
        "parser_map": {
            "iba-all-cocktails": "scraper.mock_iba.parsers.IbaCocktailListParser",
            "iba-cocktail": "scraper.mock_iba.parsers.IbaCocktailParser",
        },
        "transformer_map": {
            "iba-all-cocktails": "scraper.iba.transformers.IbaCocktailListTransformer"
        },
    }

    pipeline = Pipeline(config)
    results = pipeline.run("https://www.example.com/all-cocktails", "iba-all-cocktails")

    for payload in results:
        console.print(payload)


@app.command()
def test_components() -> None:
    """Test the individual components of the pipeline."""
    from scraper.iba.parsers import (  # noqa: PLC0415
        IbaCocktailListParser,
        IbaCocktailParser,
    )
    from scraper.iba.transformers import IbaCocktailListTransformer  # noqa: PLC0415
    from scraper.model import Link, Payload  # noqa: PLC0415
    from scraper.scrapers import FileScraper, WebScraper  # noqa: PLC0415

    # scraper = WebScraper("./data/html-data", write_content=True, write_backup=True)  # noqa: ERA001, E501, RUF100
    scraper = FileScraper("./data/html-data")  # noqa: ERA001, E501, RUF100
    payload = scraper.scrape(
        Payload(link=Link("https://iba-world.com/cocktails/all-cocktails/", "not_used"))
    )

    parser = IbaCocktailListParser(json_root_dir="./data/json-data")
    payload = parser.parse(payload)

    transformer = IbaCocktailListTransformer()
    payloads = transformer.transform(payload)
    console.print(f"Transformed payloads: {payloads}")

    web_scraper = WebScraper("./data/html-data", write_content=True, write_backup=True)
    cocktail_parser = IbaCocktailParser(json_root_dir="./data/json-data")

    counter = 0
    for payload in payloads:
        if not payload.html_content and not payload.json_content:
            scrape_payload = web_scraper.scrape(
                Payload(link=Link(payload.link.url, "iba-cocktail"))
            )
            console.print(f"Scraped: {scrape_payload}")

            parse_payload = cocktail_parser.parse(scrape_payload)
            console.print(f"Parsed: {parse_payload}")
            counter += 1

        if counter >= 3:  # noqa: PLR2004
            break

    console.print(payloads)


if __name__ == "__main__":
    app()
