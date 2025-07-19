# ruff: noqa: D100, S101

from gorgeous_stew.model import PipelineConfig


def test_pipeline_config_defaults() -> None:
    """Test default values of PipelineConfig."""
    config = PipelineConfig()

    assert config.html_root_dir == "./data/html"
    assert config.json_root_dir == "./data/json"
    assert config.read_sequence == ["file"]
    assert config.write_content is True
    assert config.write_backup is False
    assert config.scrape_delay_ms == 0
    assert isinstance(config.parser_map, dict)
    assert isinstance(config.transformer_map, dict)


def test_pipeline_config_custom_values() -> None:
    """Test custom values in PipelineConfig."""
    scrape_delay_ms = 1000
    custom_config = PipelineConfig(
        html_root_dir="./custom/html",
        json_root_dir="./custom/json",
        read_sequence=["api", "file"],
        write_content=False,
        write_backup=True,
        scrape_delay_ms=scrape_delay_ms,
        parser_map={"page_1": "parser.Class1"},
        transformer_map={"schema_1": "transformer.Class1"},
    )

    assert custom_config.html_root_dir == "./custom/html"
    assert custom_config.json_root_dir == "./custom/json"
    assert custom_config.read_sequence == ["api", "file"]
    assert custom_config.write_content is False
    assert custom_config.write_backup is True
    assert custom_config.scrape_delay_ms == scrape_delay_ms
    assert custom_config.parser_map == {"page_1": "parser.Class1"}
    assert custom_config.transformer_map == {"schema_1": "transformer.Class1"}
