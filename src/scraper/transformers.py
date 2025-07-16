"""Transformer classes for transforming JSON data."""

import json
from abc import ABC, abstractmethod

from loguru import logger

from scraper.model import Link, Payload


class Transformer(ABC):
    """Abstract base class defining the functionality supporting transformation."""

    @abstractmethod
    def transform(self, payload: Payload) -> list[Payload]:
        """
        Transform the JSON in `payload.json_content`.

        Args:
          payload: A `Payload` containing the `json_content` to transform.

        Returns:
          A `list` of `Payload` objects.  Each payload will be one of three different
          logical "types":
          - A link payload intended for follow up scraping, parsing, and transformation.
          - An intermediate payload needing follow-up transformation
            (by one or more other transformers).
          - A "terminal" content payload, requiring no further actions.
        """
        ...


class IbaCocktailListTransformer(Transformer):
    """
    Transforms the HTML of the IBA Cocktail List pages to JSON.

    https://iba-world.com/cocktails/all-cocktails/
    """

    def transform(self, payload: Payload) -> list[Payload]:
        """
        Transform the JSON of the IBA Cocktail List pages.

        This involves:
        - Creating `Payload`s for each cocktail on the page.
        - Creating a "next" link `Payload` if a next page exists.

        Args:
          payload: The `Payload` with JSON content parsed from
            an IBA Cocktail List page.

        Returns:
          A `list` of `Payloads` containing one for each cocktail parsed
          from the page, as well as a payload to scrape the next page.
        """
        if payload.json_content is None:
            msg = "Payload does not contain JSON content."
            raise ValueError(msg)

        logger.info("Transforming IBA Cocktail List payload")
        obj = json.loads(payload.json_content)

        result = [
            Payload(link=Link(url=item["url"], page_type="iba-cocktail"))
            for item in obj["cocktails"]
        ]

        if "next" in obj["links"] and obj["links"]["next"] is not None:
            result.append(
                Payload(
                    link=Link(url=obj["links"]["next"], page_type="iba-all-cocktails")
                )
            )

        return result
