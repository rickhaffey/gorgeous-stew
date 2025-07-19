"""Factory base class for dynamic instantiation of objects."""

import importlib
from typing import Any

from loguru import logger

from gorgeous_stew.model import Link, Payload
from gorgeous_stew.parsers import Parser
from gorgeous_stew.transformers import Transformer


class FactoryBase:
    """
    Base class for all concrete Factory classes.

    Provides generic functionality for dynamically instantiating objects
    based on string names.
    """

    def instantiate(self, class_name: str, *args, **kwargs) -> Any:  # noqa: ANN002, ANN003, ANN401
        """
        Instantiate an instance of a class dynamically based on the name provided.

        Args:
            class_name: A string representing the fully qualified name of the class
              to be instantiated, e.g., "scraper.parsers.DemoPageParser".
            *args: Positional arguments to be passed to the class constructor.
            **kwargs: Keyword arguments to be passed to the class constructor.

        Returns:
            An instance of the class specified by `class_name`.  Because
            of the dynamic nature of this method, the return type is `Any`.
        """
        logger.info("Instantiating class: {class_name}", class_name=class_name)
        name_components = class_name.split(".")
        class_name = name_components[-1]
        module_name = ".".join(name_components[:-1])

        module = importlib.import_module(module_name)
        class_ = getattr(module, class_name)
        return class_(*args, **kwargs)


class ParserFactory(FactoryBase):
    """Factory class to instantiate HTML `Parser`s."""

    def __init__(self, mapping: dict, json_dir: str | None = None) -> None:
        """
        Instantiate the `ParserFactory`.

        Args:
          mapping: A `dict` containing mappings from page types to
            the fully qualified class names of concrete parser classes
            to be used in parsing each of those types of pages.
            e.g.: `"demo_page": "scraper.parsers.DemoPageParser"`
          json_dir: Optional string representing the directory where
            JSON files should be written.  If provided, the parsers will
            use this directory to write parsed content as JSON files.
            Default is `None`, meaning no JSON writing will occur.
        """
        self.mapping = mapping
        self.json_dir = json_dir

    def build(self, link: Link) -> Parser:
        """
        Build a `Parser` instance for the `page_type` in `link`.

        Args:
          link: a `Link` containing the `page_type` to be parsed.

        Returns:
          A `Parser` instance appropriate for parsing the specified
          page type.

        Raises:
            ValueError: If the `page_type` in `link` is not found in the mapping.
        """
        if link.page_type not in self.mapping:
            msg = f"Unexpected page_type: {link.page_type}"
            raise ValueError(msg)

        logger.info(
            "Building parser for page_type: {page_type}", page_type=link.page_type
        )
        mapped_name = self.mapping[link.page_type]
        return self.instantiate(mapped_name, self.json_dir)


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

        Raises:
            ValueError: If the `json_schema` in `payload` is not found in the mapping.
        """
        if payload.json_schema not in self.mapping:
            msg = f"Unexpected json_schema: {payload.json_schema}"
            raise ValueError(msg)

        logger.info(
            "Building transformer for json_schema: {json_schema}",
            json_schema=payload.json_schema,
        )
        mapped_name = self.mapping[payload.json_schema]
        return self.instantiate(mapped_name)
