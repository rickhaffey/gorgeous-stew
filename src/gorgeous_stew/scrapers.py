"""Web scraping functionality for extracting HTML content from webpages."""

import time
from abc import ABC, abstractmethod
from pathlib import Path

import requests
from loguru import logger

from gorgeous_stew.fileutils import build_raw_filepath
from gorgeous_stew.model import Payload


class Scraper(ABC):
    """Abstract base class defining the functionality supporting scraping."""

    @abstractmethod
    def scrape(self, payload: Payload) -> Payload:
        """
        Scrape the HTML content of resource at `payload.link`.

        Args:
          payload: A `Payload` containing the `link` to scrape.

        Returns:
          A `Payload` object with `content` populated with the scraped HTML.

        """
        ...


class WebScraper(Scraper):
    """Scrapes HTML content from a webpage."""

    def __init__(
        self,
        html_root_dir: str,
        *,
        write_content: bool = True,
        write_backup: bool = True,
        delay_ms: int = 0,
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
          delay_ms: An integer representing the delay, in milliseconds, to
            wait after scraping a page before returning. This can be used to
            avoid overwhelming the server with requests.
        """
        self.html_root_dir = Path(html_root_dir)
        self.write_content = write_content
        self.write_backup = write_backup
        self.delay_ms = delay_ms

    def _backup_page_if_exists(self, url: str) -> bool:
        """Check if file corresponding to `url` exists, and backup if found."""
        filepath = self.html_root_dir / build_raw_filepath(url, "html", is_backup=False)

        if filepath.exists():
            bak_filepath = self.html_root_dir / build_raw_filepath(
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
        Scrape HTML content from the webpage at `payload.link.href`.

        If the scraper was configured with `write_content = True`, the HTML
        content will be written to a file in `html_root_dir`.

        If the scraper was configured with `write_backup = True`, a backup
        of any previously written file containing this page's contents
        will be created.  Otherwise, previous files will be overwritten.

        Args:
            payload: A `Payload` containing the `link` to scrape.

        Returns:
          A `Payload` with HTML from the page in `content`.
        """
        logger.info("Scraping HTML content for URL: {url}", url=payload.link.href)
        html = requests.get(payload.link.href, timeout=10).text

        if self.write_content:
            if self.write_backup:
                logger.info(
                    "Backing up existing HTML file for URL: {url}",
                    url=payload.link.href,
                )
                self._backup_page_if_exists(payload.link.href)

            filepath = self.html_root_dir / build_raw_filepath(
                payload.link.href, "html", is_backup=False
            )
            logger.info(
                "Writing scraped HTML content to file: {filepath}", filepath=filepath
            )
            filepath.write_text(html)

        if self.delay_ms > 0:
            logger.info(
                "Delaying for {delay_ms} milliseconds after scraping URL: {url}",
                delay_ms=self.delay_ms,
                url=payload.link.href,
            )

            time.sleep(self.delay_ms / 1000.0)

        return Payload(
            link=payload.link, content=html, content_type=payload.link.content_type
        )


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
        Scrape HTML content from the file behind `payload.link.href`.

        Args:
            payload: A `Payload` containing the `link` to scrape.

        Returns:
          A `Payload` with HTML from the file in `content`.
          If the file does not exist, `content` will be `None`.
        """
        logger.info(
            "Scraping HTML content (via file) for URL: {url}", url=payload.link.href
        )
        filepath = self.html_root_dir / build_raw_filepath(
            payload.link.href, "html", is_backup=False
        )

        # first check if the file exists
        if not filepath.exists():
            msg = f"File not found for URL {payload.link.href} at: {filepath}"
            logger.info(msg)
            return Payload(link=payload.link, content=None)

        logger.info("Reading HTML content from file: {filepath}", filepath=filepath)
        html = Path(filepath).read_text()

        return Payload(
            link=payload.link, content=html, content_type=payload.link.content_type
        )
