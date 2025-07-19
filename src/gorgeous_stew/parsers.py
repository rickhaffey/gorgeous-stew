"""Parser base classes and helpers."""

import typing
from abc import ABC, abstractmethod

from bs4 import PageElement, Tag

from gorgeous_stew.model import Payload


class Parser(ABC):
    """Abstract base class defining the functionality supporting parsing."""

    json_root_dir: str | None = None

    @abstractmethod
    def parse(self, payload: Payload) -> Payload:
        """
        Parse the HTML in `payload.html_content`.

        Args:
          payload: A `Payload` containing the `html_content` to parse.

        Returns:
          A `Payload` object with the `json_content` populated with
          data from the parsed HTML.
        """


class SoupHelper:
    """
    Helper class for BeautifulSoup operations.

    Provides methods to safely parse links and extract text from BS4 elements,
    while satisfying type hints and ensuring safe operations.
    """

    @staticmethod
    def safe_find_all(element: PageElement | None, name: str) -> list[PageElement]:
        """Safely find all elements in a BeautifulSoup element."""
        if element:
            tag = typing.cast("Tag", element)
            return tag.find_all(name)

        msg = "Element is None or empty."
        raise ValueError(msg)

    @staticmethod
    def safe_parse_text(element: PageElement | None) -> str:
        """Safely parse text from a BeautifulSoup element."""
        if element:
            tag = typing.cast("Tag", element)
            return tag.text

        msg = "Element is None or empty."
        raise ValueError(msg)

    @staticmethod
    def safe_parse_src(element: PageElement | None) -> str:
        """Safely parse `src` from a BeautifulSoup element."""
        if element:
            tag = typing.cast("Tag", element)
            return str(tag.get("src"))

        msg = "Element is None or empty."
        raise ValueError(msg)

    @staticmethod
    def safe_parse_link(link: PageElement | None) -> tuple[str, str]:
        """Safely parse a link from a BeautifulSoup element."""
        if link:
            tag = typing.cast("Tag", link)
            return tag.text, str(tag.get("href"))

        msg = "Link is None or empty."
        raise ValueError(msg)
