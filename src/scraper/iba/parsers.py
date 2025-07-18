"""Parser classes for scraping IBA cocktail data."""

import json
from pathlib import Path

from bs4 import BeautifulSoup, Tag
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

        divs = soup.find_all("div", {"class": "elementor-shortcode"})

        ingredients: list[str] = []
        instructions: list[str] = []
        garnishes: list[str] = []

        for div in divs:
            ul = SoupHelper.safe_find_all(div, "ul")
            if len(ul) > 0:
                ingredients.extend(
                    [li.text for li in SoupHelper.safe_find_all(ul[0], "li")]
                )

            ps = SoupHelper.safe_find_all(div, "p")
            if len(ps) > 0:
                if len(instructions) == 0:
                    instructions.extend([p.text for p in ps])
                else:
                    garnishes.extend([p.text for p in ps])

        # TODO: cocktail name
        content = {
            "ingredients": ingredients,
            "instructions": instructions,
            "garnishes": garnishes,
        }
        json_content = json.dumps(content)

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
