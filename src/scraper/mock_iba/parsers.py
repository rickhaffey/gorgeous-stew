"""Parser classes for scraping IBA cocktail data."""

import json
from pathlib import Path

from bs4 import BeautifulSoup
from loguru import logger

from scraper.fileutils import build_raw_filepath
from scraper.model import Payload
from scraper.parsers import Parser, SoupHelper


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
