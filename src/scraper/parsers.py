"""Parser classes for scraping IBA cocktail data."""

import json
import typing
from abc import ABC, abstractmethod
from pathlib import Path

from bs4 import BeautifulSoup, PageElement, Tag
from loguru import logger

from scraper.fileutils import build_raw_filepath
from scraper.model import Payload


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


class IbaCocktailListParser(Parser):
    """
    A `Parser` able to parse IBA Cocktails List pages.

    https://iba-world.com/cocktails/all-cocktails/
    """

    def __init__(self, json_root_dir: str | None = None) -> None:
        """
        Instantiate a new `IbaCocktailListParser`.

        Args:
          json_root_dir: Optional string representing the directory where
            JSON files should be written. If provided, the parser will
            use this directory to write parsed content as JSON files.
            Default is `None`, meaning no JSON writing will occur.
        """
        self.json_root_dir = json_root_dir

    def parse(self, payload: Payload) -> Payload:
        """
        Parse the `html_content` within `payload`.

        Args:
          payload: A `Payload` containing the HTML content of an
            IBA Cocktail List page.

        Returns:
          A `Payload` containing the JSON content parsed from the
          page HTML.

          An example of the JSON produced:
          ```
          {
            "cocktails": [
              { "name": "Martini", "url": "https://iba-world.com/iba-cocktail/martini/" },
              ...
            ],
            "links": {
               "next": "https://iba-world.com/cocktails/all-cocktails/page/2"
             }
          }
          ```
        Raises:
            ValueError: If the payload does not contain HTML content.
        """  # noqa: E501
        if payload.html_content is None:
            msg = "Payload does not contain HTML content."
            raise ValueError(msg)

        logger.info("Parsing IBA Cocktail List page: {url}", url=payload.link.url)
        soup = BeautifulSoup(payload.html_content, "html.parser")

        # parse out the cocktails on the current page
        cocktails = []
        for item in soup.css.select("li.cocktail"):
            link = item.find("a")
            tag_text, tag_href = SoupHelper.safe_parse_link(link)
            cocktails.append({"name": tag_text, "url": tag_href})

        # parse out the "next" link in the nav
        raw_link = soup.css.select("div.nav a.next")

        if raw_link is not None and len(raw_link) > 0:
            next_link = raw_link[0].get("href")
        else:
            next_link = None

        content = {
            "cocktails": cocktails,
            "links": {
                "next": next_link,
            },
        }

        json_content = json.dumps(content)

        # if a json_root_dir is provided, write the content to a file
        if self.json_root_dir:
            filepath = Path(self.json_root_dir) / build_raw_filepath(
                payload.link.url, "json", tag="iba-all-cocktails", is_backup=False
            )
            logger.info(
                "Writing parsed JSON content to file: {filepath}", filepath=filepath
            )
            filepath.write_text(json_content)

        return Payload(
            link=payload.link,
            json_content=json_content,
            json_schema="iba-all-cocktails",
        )

    def parse_v2(self, payload: Payload) -> Payload:
        """
        Parse the `html_content` within `payload`.

        Args:
          payload: A `Payload` containing the HTML content of an
            IBA Cocktail List page.

        Returns:
          A `Payload` containing the JSON content parsed from the
          page HTML.

          An example of the JSON produced:
          ```
          {
            "cocktails": [
              { "name": "Martini", "url": "https://iba-world.com/iba-cocktail/martini/" },
              ...
            ],
            "links": {
               "next": "https://iba-world.com/cocktails/all-cocktails/page/2"
             }
          }
          ```

        Raises:
            ValueError: If the payload does not contain HTML content.
        """  # noqa: E501
        if payload.html_content is None:
            msg = "Payload does not contain HTML content."
            raise ValueError(msg)

        logger.info("Parsing IBA Cocktail List page: {url}", url=payload.link.url)
        soup = BeautifulSoup(payload.html_content, features="html.parser")

        # get the next page link if present
        raw_link = soup.css.select("a.next")

        if raw_link is not None and len(raw_link) > 0:
            next_link = raw_link[0].get("href")
        else:
            next_link = None

        def _parse_cocktail(cocktail: Tag) -> dict[str, str]:
            """Parse a single cocktail element into a dictionary."""
            name = SoupHelper.safe_parse_text(cocktail.find("h2"))
            _, url = SoupHelper.safe_parse_link(cocktail.find("a"))
            category = SoupHelper.safe_parse_text(
                cocktail.find("div", {"class": "cocktail-category"})
            ).strip()
            picture_url = SoupHelper.safe_parse_src(cocktail.find("img"))
            return {
                "name": name,
                "url": url,
                "category": category,
                "picture_url": picture_url,
            }

        cocktails = [
            _parse_cocktail(cocktail) for cocktail in soup.css.select("div.cocktail")
        ]

        content = {
            "cocktails": cocktails,
            "links": {"next": next_link},
        }

        json_content = json.dumps(content)

        # if a json_root_dir is provided, write the content to a file
        if self.json_root_dir:
            filepath = Path(self.json_root_dir) / build_raw_filepath(
                payload.link.url, "json", tag="iba-all-cocktails", is_backup=False
            )
            logger.info(
                "Writing parsed JSON content to file: {filepath}", filepath=filepath
            )
            filepath.write_text(json_content)

        return Payload(link=payload.link, json_content=json_content)


class IbaCocktailParser(Parser):
    """
    A `Parser` able to parse IBA Cocktail pages.

    e.g. https://iba-world.com/iba-cocktail/aviation/
    """

    def __init__(self, json_root_dir: str | None = None) -> None:
        """
        Instantiate a new `IbaCocktailListParser`.

        Args:
          json_root_dir: Optional string representing the directory where
            JSON files should be written. If provided, the parser will
            use this directory to write parsed content as JSON files.
            Default is `None`, meaning no JSON writing will occur.
        """
        self.json_root_dir = json_root_dir

    def parse(self, payload: Payload) -> Payload:
        """
        Parse the `html_content` within `payload`.

        Args:
          payload: A `Payload` containing the HTML content of an
            IBA Cocktail page.

        Returns:
          A `Payload` containing the JSON content parsed from the
          page HTML.

          An example of the JSON produced:
          ```
          {
            "name": "Martini",
            "ingredients": [],
            "instructions": [],
            "garnish": ""
          }
          ```

        Raises:
            ValueError: If the payload does not contain HTML content.
        """
        if payload.html_content is None:
            msg = "Payload does not contain HTML content."
            raise ValueError(msg)

        logger.info("Parsing IBA Cocktail page: {url}", url=payload.link.url)
        soup = BeautifulSoup(payload.html_content, "html.parser")
        content = soup.css.select("div.cocktail")[0]
        name = SoupHelper.safe_parse_text(content.find("h2"))

        ingredients = [
            item.text for item in content.css.select("ul.ingredients")[0].find_all("li")
        ]

        instructions = [
            item.text
            for item in content.css.select("ul.instructions")[0].find_all("li")
        ]

        garnish = content.css.select("p.garnish")[0].text

        cocktail = {
            "name": name,
            "ingredients": ingredients,
            "instructions": instructions,
            "garnish": garnish,
        }

        json_content = json.dumps(cocktail)

        # if a json_root_dir is provided, write the content to a file
        if self.json_root_dir:
            filepath = Path(self.json_root_dir) / build_raw_filepath(
                payload.link.url, "json", tag="iba-cocktail", is_backup=False
            )
            logger.info(
                "Writing parsed JSON content to file: {filepath}", filepath=filepath
            )
            filepath.write_text(json_content)

        return Payload(
            link=payload.link,
            json_content=json_content,
            json_schema="iba-cocktail",
            is_complete=True,
        )
