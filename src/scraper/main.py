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
            "iba-all-cocktails": "scraper.iba.parsers.IbaCocktailListParser",
            "iba-cocktail": "scraper.iba.parsers.IbaCocktailParser",
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
    from scraper.iba.parsers import IbaCocktailListParser  # noqa: PLC0415
    from scraper.model import Link, Payload  # noqa: PLC0415
    from scraper.scrapers import FileScraper, WebScraper  # noqa: PLC0415, F401

    # scraper = WebScraper("./data/html-data", write_content=True, write_backup=True)  # noqa: ERA001, E501, RUF100
    scraper = FileScraper("./data/html-data")  # noqa: ERA001, E501, RUF100
    payload = scraper.scrape(
        Payload(link=Link("https://iba-world.com/cocktails/all-cocktails/", "not_used"))
    )

    parser = IbaCocktailListParser()
    payload = parser.parse_v2(payload)

    console.print(payload)


if __name__ == "__main__":
    app()
