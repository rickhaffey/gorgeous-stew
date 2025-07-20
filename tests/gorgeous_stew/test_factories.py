# ruff: noqa: D100, D103, S101
import pytest

from gorgeous_stew.factories import ParserFactory, TransformerFactory
from gorgeous_stew.model import Link, Payload

FAKE_URL = "https://www.test.com/fake-url"
DEFAULT_LINK = Link(content_type="fake_page", href=FAKE_URL, rel="external")


def test_parser_factory_build_success() -> None:
    """Test the build method of ParserFactory."""
    mapping = {
        "page_1": "gorgeous_stew.iba.parsers.IbaCocktailListParser",
        "page_2": "gorgeous_stew.iba.parsers.IbaCocktailParser",
    }
    factory = ParserFactory(mapping, json_dir=None)

    link = Link(content_type="page_1", href=FAKE_URL, rel="external")
    parser = factory.build(link)

    assert parser.__class__.__name__ == "IbaCocktailListParser"

    link = Link(content_type="page_2", href=FAKE_URL, rel="external")
    parser = factory.build(link)

    assert parser.__class__.__name__ == "IbaCocktailParser"


def test_parser_factory_build_failure() -> None:
    mapping = {
        "page_1": "gorgeous_stew.iba.parsers.IbaCocktailListParser",
        "page_2": "gorgeous_stew.iba.parsers.IbaCocktailParser",
    }
    factory = ParserFactory(mapping, json_dir=None)

    # Test with an unknown page type
    link_unknown = Link(content_type="unknown_page", href=FAKE_URL, rel="external")
    with pytest.raises(ValueError, match="Unexpected content_type: unknown_page"):
        factory.build(link_unknown)


def test_parser_factory_build_invalid_link() -> None:
    """Test build method with an invalid link."""
    mapping = {
        "page_1": "gorgeous_stew.iba.parsers.IbaCocktailListParser",
    }
    factory = ParserFactory(mapping, json_dir=None)

    # Test with a link that has no content_type
    link_invalid = Link(content_type="", href=FAKE_URL, rel="external")
    with pytest.raises(ValueError, match="Unexpected content_type: "):
        factory.build(link_invalid)


def test_transformer_factory_build_success() -> None:
    """Test the build method of TransformerFactory."""
    mapping = {
        "schema_1": "gorgeous_stew.iba.transformers.IbaCocktailListTransformer",
    }
    factory = TransformerFactory(mapping)

    payload = Payload(content_type="schema_1", link=DEFAULT_LINK)
    transformer = factory.build(payload)
    assert transformer.__class__.__name__ == "IbaCocktailListTransformer"


def test_transformer_factory_build_failure() -> None:
    mapping = {
        "schema_1": "gorgeous_stew.iba.transformers.IbaCocktailListTransformer",
    }
    factory = TransformerFactory(mapping)

    payload_unknown = Payload(content_type="unknown_schema", link=DEFAULT_LINK)
    with pytest.raises(ValueError, match="Unexpected content_type: unknown_schema"):
        factory.build(payload_unknown)


def test_transformer_factory_build_invalid_payload() -> None:
    """Test build method with an invalid payload."""
    mapping = {
        "schema_1": "gorgeous_stew.iba.transformers.IbaCocktailListTransformer",
    }
    factory = TransformerFactory(mapping)

    payload_invalid = Payload(content_type="", link=DEFAULT_LINK)
    with pytest.raises(ValueError, match="Unexpected content_type: "):
        factory.build(payload_invalid)
