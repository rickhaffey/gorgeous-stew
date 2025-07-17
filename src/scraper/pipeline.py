"""Pipeline for scraping web content."""

from loguru import logger

from scraper.factories import ParserFactory, TransformerFactory
from scraper.model import Link, Payload
from scraper.scrapers import FileScraper, MockScraper, Scraper, WebScraper


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
        self._html_root_dir = config.get("html_root_dir", "./html-data")
        self._read_sequence = config.get("read_sequence", ["file"])
        self._write_content = config.get("write_content", True)
        self._write_backup = config.get("write_backup", True)

        self._scrapers: dict[str, Scraper] = self._build_scrapers()

    def _build_scrapers(self) -> dict[str, Scraper]:
        """
        Build the `Scrapers` based on the read sequence.

        Returns:
            A dictionary mapping read sources to their respective `Scraper` instances.
            - "file": `FileScraper`
            - "web": `WebScraper`
            - "mock": `MockScraper`
        """
        scrapers: dict[str, Scraper] = {}

        for read_source in self._read_sequence:
            logger.info(
                "Building scraper for read source: {source}", source=read_source
            )

            if read_source == "file":
                scrapers[read_source] = FileScraper(self._html_root_dir)

            elif read_source == "web":
                scrapers[read_source] = WebScraper(
                    self._html_root_dir,
                    write_content=self._write_content,
                    write_backup=self._write_backup,
                )

            elif read_source == "mock":
                scrapers[read_source] = MockScraper()

            else:
                # TODO: Is ValueError the right exception here?
                #   Should this have been checked when pipeline was instantiated?
                msg = (
                    f"Unknown read source: {read_source}. Supported sources "
                    "are 'file', 'web', and 'mock'."
                )
                raise ValueError(msg)

        return scrapers

    def _scrape(self, payload: Payload) -> Payload:
        """
        Scrape the HTML content for a given `Payload`.

        This method will look through the read sequence and attempt to scrape
        from the specified sources in order. If the first source fails or does not
        provide HTML content, it will move to the next source in the sequence.

        Args:
            payload: The `Payload` to scrape.

        Returns:
            A new `Payload` with the scraped HTML content.

        Raises:
            RuntimeError: If no HTML content could be scraped from any
              source in the read sequence.
        """
        for read_source in self._read_sequence:
            logger.info(
                "Scraping via {read_source} for URL: {url}",
                read_source=read_source,
                url=payload.link.url,
            )

            scraper = self._scrapers[read_source]
            payload = scraper.scrape(payload)

            if payload.html_content:
                logger.info(
                    "HTML content scraped successfully for URL: {url}",
                    url=payload.link.url,
                )
                return payload
            logger.info("No HTML content found. Trying next source in sequence.")

        msg = "Unable to scrape HTML content from any source in the read sequence."
        raise RuntimeError(msg)

    def _handle_payload(self, payload: Payload) -> list[Payload]:
        """
        Recursively handle a `Payload`.

        Args:
            payload: The `Payload` to handle.

        Returns:
            A list of `Payload` instances resulting from processing the input `Payload`.

        Raises:
            ValueError: If the `Payload` is in an unexpected state or cannot
              be processed.
        """
        # base case: terminal payload handling
        if payload.is_complete:
            return [payload]

        # link payload (needs to be scraped and processed further)
        if payload.html_content is None and payload.json_content is None:
            next_payload = self._scrape(payload)
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

            logger.info(
                "Recursively handling {n} transformed payloads", n=len(next_payloads)
            )
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

        Returns:
            A list of `Payload` instances resulting from processing the input URL.
        """
        logger.info(
            f"Running pipeline for URL: {url} of page type: {page_type}",
            url=url,
            page_type=page_type,
        )
        link = Link(url=url, page_type=page_type)

        return self._handle_payload(Payload(link=link))
