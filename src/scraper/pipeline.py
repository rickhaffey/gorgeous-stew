"""Pipeline for scraping web content."""

from loguru import logger

from scraper.factories import ParserFactory, TransformerFactory
from scraper.model import Link, Payload
from scraper.scrapers import MockScraper


class Pipeline:
    """Scraping Pipeline."""

    def __init__(self, config: dict) -> None:
        """
        Instantiate a new Pipeline.

        Args:
          config: A `dict` containing mappings for `Parser` and
            `Transformer` instantiation.
        """
        logger.info("Initializing Pipeline with config: {config}", config=config)
        self._scraper = MockScraper()
        self._parser_factory = ParserFactory(config["parser_map"])
        self._transformer_factory = TransformerFactory(config["transformer_map"])

    def _handle_payload(self, payload: Payload) -> list[Payload]:
        """
        Recursively handle a `Payload`.

        Args:
            payload: The `Payload` to handle.

        Returns:
            A list of `Payload` instances resulting from processing the input `Payload`.
        """
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

    def run(self, url: str, page_type: str) -> list[Payload]:
        """
        Run a pipeline instance.

        Args:
          url: The entrypoint URL to start scraping against.
          page_type: The page type of the URL.  This is used to decide which
            `Parser`s and `Transformer`s to use in processing the page.
        """
        logger.info(
            f"Running pipeline for URL: {url} of page type: {page_type}",
            url=url,
            page_type=page_type,
        )
        link = Link(url=url, page_type=page_type)

        return self._handle_payload(Payload(link=link))
