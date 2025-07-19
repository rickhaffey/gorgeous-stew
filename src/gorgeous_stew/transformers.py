"""Transformer classes for transforming JSON data."""

from abc import ABC, abstractmethod

from gorgeous_stew.model import Payload


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
