"""Web scraping functionality for extracting HTML content from webpages."""

from abc import ABC, abstractmethod
from datetime import UTC, datetime
from pathlib import Path

import requests
from loguru import logger

from scraper.mocks import html_samples
from scraper.model import Payload


class Scraper(ABC):
    """Abstract base class defining the functionality supporting scraping."""

    @abstractmethod
    def scrape(self, payload: Payload) -> Payload:
        """
        Scrape the HTML content of resource at `payload.link`.

        Args:
          payload: A `Payload` containing the `link` to scrape.

        Returns:
          A `Payload` object with `html_content` populated with the scraped HTML.

        """
        ...

    def _sanitize_url(self, url: str) -> str:
        """
        Sanitize a url for usage as a filename.

        - strip prefixes and suffixes
        - replace special characters
        """
        result = url

        for prefix in ["https://", "http://"]:
            result = result.removeprefix(prefix)

        result = result.removesuffix("/")

        for c in ["/", ".", "_"]:
            result = result.replace(c, "-")

        return result

    def _build_timestamp(self) -> str:
        """Build a string representation of the current UTC timestamp."""
        return datetime.now(tz=UTC).strftime("%Y%m%d%H%M%S")

    def _build_raw_filename(
        self, url: str, extension: str, *, is_backup: bool = False
    ) -> Path:
        """
        Build a filename for the raw data from the provided `url`.

        The default name of the file consists of a sanitized version of `url`
        with the `extension` provided.

        If `is_backup = True`, the name also includes a UTC timestamp and an
        additional '.bak' extension.
        """
        file_name = self._sanitize_url(url)

        file_name = (
            f"{file_name}.{extension}.{self._build_timestamp()}.bak"
            if is_backup
            else f"{file_name}.{extension}"
        )

        log_msg_template = (
            "Building raw filename for URL: {url} with extension: {extension} "
            " (is_backup={is_backup}), resulting filename: {file_name}"
        )
        logger.info(
            log_msg_template,
            url=url,
            extension=extension,
            is_backup=is_backup,
            file_name=file_name,
        )

        return Path(file_name)


class WebScraper(Scraper):
    """Scrapes HTML content from a webpage."""

    def __init__(
        self,
        html_root_dir: str,
        *,
        write_content: bool = True,
        write_backup: bool = True,
    ) -> None:
        """
        Instantiate a `WebScraper`.

        Args:
          html_root_dir: A string representing the path to where HTML content
            should be stored.
          write_content: A boolean flag indicating whether scraped content
            should be written to local storage.
          write_backup: A boolean flag indicating whether the process should
            backup previously written files (rather than overwriting.)
        """
        self.html_root_dir = Path(html_root_dir)
        self.write_content = write_content
        self.write_backup = write_backup

    def _backup_page_if_exists(self, url: str) -> bool:
        """Check if file corresponding to `url` exists, and backup if found."""
        filepath = self.html_root_dir / self._build_raw_filename(
            url, "html", is_backup=False
        )

        if filepath.exists():
            bak_filepath = self.html_root_dir / self._build_raw_filename(
                url, "html", is_backup=True
            )
            logger.info(
                "Backing up existing file: {filepath} to {bak_filepath}",
                filepath=filepath,
                bak_filepath=bak_filepath,
            )
            filepath.replace(bak_filepath)
            return True

        return False

    def scrape(self, payload: Payload) -> Payload:
        """
        Scrape HTML content from the webpage at `payload.link.url`.

        If the scraper was configured with `write_content = True`, the HTML
        content will be written to a file in `html_root_dir`.

        If the scraper was configured with `write_backup = True`, a backup
        of any previously written file containing this page's contents
        will be created.  Otherwise, previous files will be overwritten.

        Args:
            payload: A `Payload` containing the `link` to scrape.

        Returns:
          A `Payload` with HTML from the page in `html_content`.
        """
        logger.info("Scraping HTML content for URL: {url}", url=payload.link.url)
        html = requests.get(payload.link.url, timeout=10).text

        if self.write_content:
            if self.write_backup:
                logger.info(
                    "Backing up existing HTML file for URL: {url}",
                    url=payload.link.url,
                )
                self._backup_page_if_exists(payload.link.url)

            filepath = self.html_root_dir / self._build_raw_filename(
                payload.link.url, "html", is_backup=False
            )
            logger.info(
                "Writing scraped HTML content to file: {filepath}", filepath=filepath
            )
            filepath.write_text(html)

        return Payload(link=payload.link, html_content=html)


class FileScraper(Scraper):
    """Mocks scraping by loading HTML from a file."""

    def __init__(
        self,
        html_root_dir: str,
    ) -> None:
        """
        Instantiate a `FileScraper`.

        Args:
          html_root_dir: A string representing the path to where HTML content
            is stored.
        """
        self.html_root_dir = Path(html_root_dir)

    def scrape(self, payload: Payload) -> Payload:
        """
        Scrape HTML content from the file behind `payload.link.url`.

        Args:
            payload: A `Payload` containing the `link` to scrape.

        Returns:
          A `Payload` with HTML from the file in `html_content`.
          If the file does not exist, `html_content` will be `None`.
        """
        logger.info(
            "Scraping HTML content (via file) for URL: {url}", url=payload.link.url
        )
        filepath = self.html_root_dir / self._build_raw_filename(
            payload.link.url, "html", is_backup=False
        )

        # first check if the file exists
        if not filepath.exists():
            msg = f"File not found for URL {payload.link.url} at: {filepath}"
            logger.info(msg)
            return Payload(link=payload.link, html_content=None)

        logger.info("Reading HTML content from file: {filepath}", filepath=filepath)
        html = Path(filepath).read_text()

        return Payload(link=payload.link, html_content=html)


class MockScraper(Scraper):
    """Mocks scraping of HTML based on the provided URLs."""

    def scrape(self, payload: Payload) -> Payload:
        """Return the mock scraped HTML."""
        logger.info("Mock scraping HTML content for URL: {url}", url=payload.link.url)
        if "all-cocktails" in payload.link.url:
            if payload.link.url == "https://www.example.com/all-cocktails":
                html = html_samples["all-cocktails"]
            elif payload.link.url == "https://www.example.com/all-cocktails/page/2":
                html = html_samples["all-cocktails-pg2"]
            elif payload.link.url == "https://www.example.com/all-cocktails/page/3":
                html = html_samples["all-cocktails-pg3"]
        elif "manhattan" in payload.link.url:
            html = html_samples["manhattan"]
        elif "margarita" in payload.link.url:
            html = html_samples["margarita"]
        elif "negroni" in payload.link.url:
            html = html_samples["negroni"]
        elif "old-fashioned" in payload.link.url:
            html = html_samples["old-fashioned"]
        elif "paper-plane" in payload.link.url:
            html = html_samples["paper-plane"]
        else:
            msg = f"Unexpected URL: {payload.link.url}"
            raise ValueError(msg)

        return Payload(link=payload.link, html_content=html)
