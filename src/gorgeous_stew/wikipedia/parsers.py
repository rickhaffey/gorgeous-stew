"""Parser classes for scraping IBA cocktail data."""

import json
import typing
from pathlib import Path

from bs4 import BeautifulSoup, PageElement, Tag
from loguru import logger

from gorgeous_stew.content_types import is_html_content_type
from gorgeous_stew.fileutils import build_raw_filepath
from gorgeous_stew.model import Payload
from gorgeous_stew.parsers import Parser, SoupHelper


class CocktailListParser(Parser):
    """
    A `Parser` able to parse the Wikipedia Cocktails List page.

    https://en.wikipedia.org/wiki/List_of_cocktails
    """

    # Collection of ingredients that are included as links that
    # we want to ignore when parsing the list of _cocktails_.
    INGREDIENTS_TO_IGNORE = (
        "cachaça",
        "Port wine",
        "Sherry",
        "Vermouth",
        "advocaat",
    )

    def __init__(self, json_root_dir: str | None = None) -> None:
        """
        Instantiate a new `CocktailListParser`.

        Args:
          json_root_dir: Optional string representing the directory where
            JSON files should be written. If provided, the parser will
            use this directory to write parsed content as JSON files.
            Default is `None`, meaning no JSON writing will occur.
        """
        self.json_root_dir = json_root_dir

    def parse(self, payload: Payload) -> Payload:
        """
        Parse the HTML `content` within `payload`.

        Args:
          payload: A `Payload` containing the HTML content of the
            Wikipedia Cocktail List page.

        Returns:
          A `Payload` containing the JSON content parsed from the
            page HTML.

          An example of the JSON produced:
          ```
          {
            "cocktails": [
                {
                  "name": "Manhattan",
                  "url": "https://en.wikipedia.org/wiki/Manhattan_(cocktail)",
                  "category": [
                    "Whisky"
                  ]
                },
              ...
            ]
          }
          ```

        Raises:
            ValueError: If the payload content_type is not 'text/html'
              or the payload does not contain HTML content.
        """
        if not is_html_content_type(payload.content_type):
            msg = (
                f"Payload must have content_type: text/html (generic or "
                f"vendor specific).  Received: {payload.content_type}."
            )
            raise ValueError(msg)
        if not payload.content:
            msg = "Payload content is empty."
            raise ValueError(msg)

        logger.info(
            "Parsing Wikipedia Cocktail List page: {url}", url=payload.link.href
        )

        soup = BeautifulSoup(payload.content, features="html.parser")
        entrypoint = soup.find("div", {"class": "mw-parser-output"})

        cur_element = SoupHelper.safe_next_element(entrypoint)
        category: list[str] = []
        items: list[dict[str, typing.Any]] = []

        # Because the "hierarchy" of the headings, lists, and items on
        # the page is represented sequentially rather than as a tree of
        # nested elements, we'll need to iterate through the elements,
        # and manage the hierarchy ourselves.
        while cur_element is not None:
            # manage the current category hierarchy
            if SoupHelper.safe_parse_name(cur_element) in {
                "h1",
                "h2",
                "h3",
                "h4",
                "h5",
                "h6",
            }:
                temp_category, header_name = self._parse_category(
                    cur_element, category.copy()
                )
                if header_name == "Historical classes of cocktails":
                    # Stop processing when we reach the "Historical classes
                    # of cocktails" section
                    break
                category = temp_category

            elif SoupHelper.safe_parse_name(cur_element) in {"ul", "ol"}:
                new_items = self._parse_items(cur_element, category.copy())
                items.extend(new_items)

            cur_element = cur_element.next_element

        # reformat ahead of JSON serialization
        content = {
            "cocktails": sorted(items, key=lambda x: x["name"]),
        }
        json_content = json.dumps(content)

        # if a json_root_dir is provided, write the content to a file
        if self.json_root_dir:
            filepath = Path(self.json_root_dir) / build_raw_filepath(
                payload.link.href,
                "json",
                tag="wikipedia-all-cocktails",
                is_backup=False,
            )
            logger.info(
                "Writing parsed JSON content to file: {filepath}", filepath=filepath
            )
            filepath.write_text(json_content)

        return Payload(
            link=payload.link,
            content_type="application/vnd.gorgeous-stew.wikipedia-all-cocktails+json",
            content=json_content,
            is_complete=True,
        )

    def _parse_items(
        self, html_list: PageElement, category: list[str]
    ) -> list[dict[str, typing.Any]]:
        """
        Parse the items in a list element, extracting cocktail names and URLs.

        Args:
            html_list: A BeautifulSoup PageElement representing a list element
                (ul or ol) containing cocktail items.
            category: A list of strings representing the current category
                hierarchy for the cocktails.

        Returns:
            A list of dictionaries, each containing the name, URL, and
            category of a cocktail.

        Raises:
            ValueError: If the html_list is None or empty.
        """
        if html_list:
            html_list_tag = typing.cast("Tag", html_list)
        else:
            msg = "HTML list element is None or empty."
            raise ValueError(msg)

        result: list[dict[str, typing.Any]] = []

        # ignore image galleries
        _class = html_list_tag.get("class", None)
        if _class and "gallery" in _class:
            return result

        # parse the items in the list
        for li in html_list_tag.find_all("li", recursive=False):
            links = SoupHelper.safe_find_all(li, "a")

            for link in links:
                string, href = SoupHelper.safe_parse_link(
                    link, normalize_whitespace=True
                )

                # skip any links that are actually ingredients
                if string in self.INGREDIENTS_TO_IGNORE:
                    continue

                if href and not href.startswith("http"):
                    href = "https://en.wikipedia.org" + href

                result.append(
                    {
                        "name": string,
                        "url": href,
                        "category": category.copy(),
                    }
                )

        return result

    def _parse_category(
        self, header: PageElement, cur_category: list[str]
    ) -> tuple[list[str], str]:
        """
        Adjust the current category based on the parsed header element.

        Args:
            header: A BeautifulSoup Tag representing the header element
                (h1, h2, h3, etc.) that defines the current category.
            cur_category: The current category hierarchy as a list of strings.

        Returns:
            A tuple containing the updated category list and the name of
            the current header.

        Raises:
            ValueError: If the header element is None or empty.
        """
        if header:
            header_tag = typing.cast("Tag", header)
        else:
            msg = "Header element is None or empty."
            raise ValueError(msg)

        # parse the level from the heading tag
        level = int(header_tag.name[1])

        # pop entries from the list as we move up the
        # hierarchy, if necessary
        n_remove = min(level - len(cur_category) - 2, 0)
        if n_remove < 0:
            cur_category = cur_category[:n_remove]

        # parse the text from the current element
        header_name = SoupHelper.safe_parse_text(header_tag, normalize_whitespace=True)

        # push the new element onto the list
        cur_category.append(header_name)

        return cur_category, header_name
