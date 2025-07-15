"""Factory base class for dynamic instantiation of objects."""

import importlib
from typing import Any

from scraper.model import Link, Payload
from scraper.parsers import Parser
from scraper.transformers import Transformer


class FactoryBase:
    """
    Base class for all concrete Factory classes.

    Provides generic functionality for dynamically instantiating objects
    based on string names.
    """

    def instantiate(self, fqn: str) -> Any:  # noqa: ANN401
        """Instantiate an instance of a class dynamically based on the name provided."""
        name_components = fqn.split(".")
        class_name = name_components[-1]
        module_name = ".".join(name_components[:-1])

        module = importlib.import_module(module_name)
        class_ = getattr(module, class_name)
        return class_()


class ParserFactory(FactoryBase):
    """Factory class to instantiate HTML `Parser`s."""

    def __init__(self, mapping: dict) -> None:
        """
        Instantiate the `ParserFactory`.

        Args:
          mapping: A `dict` containing mappings from page types to
            the fully qualified class names of concrete parser classes
            to be used in parsing each of those types of pages.
            e.g.: `"demo_page": "scraper.parsers.DemoPageParser"`
        """
        self.mapping = mapping

    def build(self, link: Link) -> Parser:
        """
        Build a `Parser` instance for the `page_type` in `link`.

        Args:
          link: a `Link` containing the `page_type` to be parsed.

        Returns:
          A `Parser` instance appropriate for parsing the specified
          page type.
        """
        if link.page_type not in self.mapping:
            msg = f"Unexpected page_type: {link.page_type}"
            raise ValueError(msg)

        mapped_name = self.mapping[link.page_type]
        return self.instantiate(mapped_name)


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
