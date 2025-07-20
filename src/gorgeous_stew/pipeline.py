"""Pipeline for scraping web content."""

from loguru import logger

from gorgeous_stew.factories import ParserFactory, TransformerFactory
from gorgeous_stew.model import Link, Payload, PipelineConfig
from gorgeous_stew.scrapers import FileScraper, Scraper, WebScraper


class Pipeline:
    """Scraping Pipeline."""

    def __init__(self, config: PipelineConfig) -> None:
        """
        Instantiate a new Pipeline.

        Args:
          config: A `PipelineConfig` containing various configuration
            values, as well as mappings for `Parser` and `Transformer`
            instantiation.
        """
        logger.info("Initializing Pipeline with config: {config}", config=config)
        self._validate_config(config)
        self._config = config
        self._scrapers: dict[str, Scraper] = self._build_scrapers()
        self._parser_factory = ParserFactory(
            self._config.parser_map, self._config.json_root_dir
        )
        self._transformer_factory = TransformerFactory(self._config.transformer_map)

    def _validate_config(self, config: PipelineConfig) -> None:
        """
        Validate the provided PipelineConfig.

        Args:
          config: The PipelineConfig to validate.

        Raises:
          ValueError: If the configuration is invalid.
        """
        if not config.read_sequence:
            msg = "Read sequence cannot be empty."
            raise ValueError(msg)
        if not config.parser_map:
            msg = "Parser map cannot be empty."
            raise ValueError(msg)
        if not config.transformer_map:
            msg = "Transformer map cannot be empty."
            raise ValueError(msg)
        if not config.html_root_dir:
            msg = "HTML root directory must be specified."
            raise ValueError(msg)

        # Validate that all read sources in the sequence are supported
        supported_sources = {"file", "web"}
        for source in config.read_sequence:
            if source not in supported_sources:
                msg = (
                    f"Unsupported read source: {source}. "
                    f"Supported sources are: {supported_sources}"
                )
                raise ValueError(msg)

    def _build_scrapers(self) -> dict[str, Scraper]:
        """
        Build the `Scrapers` based on the read sequence.

        Returns:
          A dictionary mapping read sources to their respective `Scraper` instances.
          - "file": `FileScraper`
          - "web": `WebScraper`

        Raises:
          ValueError: If an unknown read source is encountered.
        """
        scrapers: dict[str, Scraper] = {}

        for read_source in self._config.read_sequence:
            logger.info(
                "Building scraper for read source: {source}", source=read_source
            )

            if read_source == "file":
                scrapers[read_source] = FileScraper(self._config.html_root_dir)

            elif read_source == "web":
                scrapers[read_source] = WebScraper(
                    self._config.html_root_dir,
                    write_content=self._config.write_content,
                    write_backup=self._config.write_backup,
                    delay_ms=self._config.scrape_delay_ms,
                )

            else:
                # NOTE: the list of provided resource types was checked
                # at pipeline instantiation so we should never hit this
                # scenario; adding check as an additional backup
                msg = (
                    f"Unknown read source: {read_source}. Supported sources "
                    "are 'file' and 'web'."
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
        for read_source in self._config.read_sequence:
            logger.info(
                "Scraping via {read_source} for URL: {url}",
                read_source=read_source,
                url=payload.link.href,
            )

            scraper = self._scrapers[read_source]
            payload = scraper.scrape(payload)

            if payload.content:
                logger.info(
                    "HTML content scraped successfully for URL: {url}",
                    url=payload.link.href,
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
        if payload.content is None:
            next_payload = self._scrape(payload)
            return self._handle_payload(next_payload)

        # html payload needing parsing
        if payload.content is not None and payload.content_type == "text/html":
            parser = self._parser_factory.build(payload.link)
            next_payload = parser.parse(payload)
            return self._handle_payload(next_payload)

        # json payload needing transformation
        if payload.content is not None and payload.content_type == "application/json":
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

    def run(self, url: str, content_type: str) -> list[Payload]:
        """
        Run a pipeline instance.

        Args:
          url: The entrypoint URL to start scraping against.
          content_type: The page type of the URL.  This is used to decide which
            `Parser`s and `Transformer`s to use in processing the page.

        Returns:
            A list of `Payload` instances resulting from processing the input URL.
        """
        logger.info(
            f"Running pipeline for URL: {url} of page type: {content_type}",
            url=url,
            content_type=content_type,
        )
        link = Link(href=url, content_type=content_type, rel="external")

        return self._handle_payload(Payload(link=link))
