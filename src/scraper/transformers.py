"""Transformer classes for transforming JSON data."""

import json
from abc import ABC, abstractmethod

from scraper.factories import FactoryBase
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


class TransformerFactory(FactoryBase):
    """Factory class to instantiate JSON `Transformer`s."""

    def __init__(self, mapping: dict) -> None:
        """
        Instantiate the `TransformerFactory`.

        Args:
          mapping: A `dict` containing mappings from json schema to
            the fully qualified class names of concrete transformer
            classes to be used in transforming each of those types
            of json datasets.
            e.g.: `"demo_schema": "scraper.transformers.DemoParser"`
        """
        self.mapping = mapping

    def build(self, payload: Payload) -> Transformer:
        """
        Build a `Transformer` instance for the `json_schema` in `payload`.

        Args:
          payload: a `Payload` containing the `json_schema` to be transformed.

        Returns:
          A `Transformer` instance appropriate for transforming the specified
          json schema.
        """
        if payload.json_schema not in self.mapping:
            msg = f"Unexpected json_schema: {payload.json_schema}"
            raise ValueError(msg)

        mapped_name = self.mapping[payload.json_schema]
        return self.instantiate(mapped_name)


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
