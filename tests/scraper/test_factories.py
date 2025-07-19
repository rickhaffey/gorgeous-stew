# ruff: noqa: D100, D103, S101
import pytest

from scraper.factories import ParserFactory, TransformerFactory
from scraper.model import Link, Payload

FAKE_URL = "https://www.test.com/fake-url"
DEFAULT_LINK = Link(page_type="fake_page", url=FAKE_URL)


def test_parser_factory_build_success() -> None:
    """Test the build method of ParserFactory."""
    mapping = {
        "page_1": "scraper.iba.parsers.IbaCocktailListParser",
        "page_2": "scraper.iba.parsers.IbaCocktailParser",
    }
    factory = ParserFactory(mapping, json_dir=None)

    link = Link(page_type="page_1", url=FAKE_URL)
    parser = factory.build(link)

    assert parser.__class__.__name__ == "IbaCocktailListParser"

    link = Link(page_type="page_2", url=FAKE_URL)
    parser = factory.build(link)

    assert parser.__class__.__name__ == "IbaCocktailParser"


def test_parser_factory_build_failure() -> None:
    mapping = {
        "page_1": "scraper.iba.parsers.IbaCocktailListParser",
        "page_2": "scraper.iba.parsers.IbaCocktailParser",
    }
    factory = ParserFactory(mapping, json_dir=None)

    # Test with an unknown page type
    link_unknown = Link(page_type="unknown_page", url=FAKE_URL)
    with pytest.raises(ValueError, match="Unexpected page_type: unknown_page"):
        factory.build(link_unknown)


def test_parser_factory_build_invalid_link() -> None:
    """Test build method with an invalid link."""
    mapping = {
        "page_1": "scraper.iba.parsers.IbaCocktailListParser",
    }
    factory = ParserFactory(mapping, json_dir=None)

    # Test with a link that has no page_type
    link_invalid = Link(page_type="", url=FAKE_URL)
    with pytest.raises(ValueError, match="Unexpected page_type: "):
        factory.build(link_invalid)


def test_transformer_factory_build_success() -> None:
    """Test the build method of TransformerFactory."""
    mapping = {
        "schema_1": "scraper.iba.transformers.IbaCocktailListTransformer",
    }
    factory = TransformerFactory(mapping)

    payload = Payload(json_schema="schema_1", link=DEFAULT_LINK)
    transformer = factory.build(payload)
    assert transformer.__class__.__name__ == "IbaCocktailListTransformer"


def test_transformer_factory_build_failure() -> None:
    mapping = {
        "schema_1": "scraper.iba.transformers.IbaCocktailListTransformer",
    }
    factory = TransformerFactory(mapping)

    payload_unknown = Payload(json_schema="unknown_schema", link=DEFAULT_LINK)
    with pytest.raises(ValueError, match="Unexpected json_schema: unknown_schema"):
        factory.build(payload_unknown)


def test_transformer_factory_build_invalid_payload() -> None:
    """Test build method with an invalid payload."""
    mapping = {
        "schema_1": "scraper.iba.transformers.IbaCocktailListTransformer",
    }
    factory = TransformerFactory(mapping)

    payload_invalid = Payload(json_schema="", link=DEFAULT_LINK)
    with pytest.raises(ValueError, match="Unexpected json_schema: "):
        factory.build(payload_invalid)
