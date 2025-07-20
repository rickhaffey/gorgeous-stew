"""Transformer classes for transforming JSON data from the IBA websites."""

import json

from loguru import logger

from gorgeous_stew.model import Link, Payload
from gorgeous_stew.transformers import Transformer


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

        Raises:
            ValueError: If the `payload` does not contain valid JSON content.
        """
        if payload.json_content is None:
            msg = "Payload does not contain JSON content."
            raise ValueError(msg)

        logger.info("Transforming IBA Cocktail List payload")
        obj = json.loads(payload.json_content)

        result = [
            Payload(
                link=Link(
                    href=item["url"],
                    content_type="iba-cocktail",
                    rel="external",
                )
            )
            for item in obj["cocktails"]
        ]

        if "next" in obj["links"] and obj["links"]["next"] is not None:
            result.append(
                Payload(
                    link=Link(
                        href=obj["links"]["next"],
                        content_type="iba-all-cocktails",
                        rel="next",
                    )
                )
            )

        return result
