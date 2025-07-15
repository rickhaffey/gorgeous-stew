"""The main entrypoint of the application."""

import typer
from loguru import logger
from rich.console import Console
from rich.logging import RichHandler

from scraper.model import Link, Payload
from scraper.parsers import ParserFactory
from scraper.scrapers import MockScraper, WebScraper
from scraper.transformers import TransformerFactory

logger.configure(handlers=[{"sink": RichHandler(markup=True), "format": "{message}"}])
app = typer.Typer()
console = Console()


class Pipeline:
    """Scraping Pipeline."""

    def __init__(self, config: dict) -> None:
        """
        Instantiate a new Pipeline.

        Args:
          config: A `dict` containing mappings for `Parser` and
            `Transformer` instantiation.
        """
        self._scraper = MockScraper()
        self._parser_factory = ParserFactory(config["parser_map"])
        self._transformer_factory = TransformerFactory(config["transformer_map"])

    def _handle_payload(self, payload: Payload) -> list[Payload]:
        # base case: terminal payload handling
        if payload.is_complete:
            return [payload]

        # link payload (needs to be scraped and processed further)
        if payload.html_content is None and payload.json_content is None:
            next_payload = self._scraper.scrape(payload)
            return self._handle_payload(next_payload)

        # html payload needing parsing
        if payload.html_content is not None:
            parser = self._parser_factory.build(payload.link)
            next_payload = parser.parse(payload)
            return self._handle_payload(next_payload)

        # json payload needing transformation
        if payload.json_content is not None:
            transformer = self._transformer_factory.build(payload)
            next_payloads = transformer.transform(payload)
            result = []
            for next_payload in next_payloads:
                result.extend(self._handle_payload(next_payload))
            return result

        msg = "Unexpected payload."
        raise ValueError(msg)

    def run(self, url: str, page_type: str) -> None:
        """
        Run a pipeline instance.

        Args:
          url: The entrypoint URL to start scraping against.
          page_type: The page type of the URL.  This is used to decide which
            `Parser`s and `Transformer`s to use in processing the page.
        """
        link = Link(url=url, page_type=page_type)

        results = self._handle_payload(Payload(link=link))

        for payload in results:
            console.print(payload)


# -- concrete implementations --


@app.command()
def run_pipeline() -> None:
    """Run the scraping process."""
    config = {
        "html_root_dir": "./html-data",
        "json_root_dir": "./json-data",
        "read_sequence": ["web", "file"],
        "write_content": True,
        "write_backup": True,
        "parser_map": {
            "iba-all-cocktails": "scraper.parsers.IbaCocktailListParser",
            "iba-cocktail": "scraper.parsers.IbaCocktailParser",
        },
        "transformer_map": {
            "iba-all-cocktails": "scraper.transformers.IbaCocktailListTransformer"
        },
    }

    pipeline = Pipeline(config)
    pipeline.run("https://www.example.com/all-cocktails", "iba-all-cocktails")


@app.command()
def test_components() -> None:
    """Test the individual components of the pipeline."""
    from scraper.parsers import IbaCocktailListParser  # noqa: PLC0415

    scraper = WebScraper("./data/html-data", write_content=True, write_backup=True)
    payload = scraper.scrape(
        Payload(link=Link("https://iba-world.com/cocktails/all-cocktails/", "not_used"))
    )

    parser = IbaCocktailListParser()
    payload = parser.parse_v2(payload)

    console.print(payload)


if __name__ == "__main__":
    app()
