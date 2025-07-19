"""Defines the data models used in the scraping pipeline."""

from dataclasses import dataclass, field

from pydantic import BaseModel


class PipelineConfig(BaseModel):
    """Represents the configuration for the scraping pipeline."""

    html_root_dir: str = "./data/html"
    json_root_dir: str = "./data/json"
    read_sequence: list[str] = field(default_factory=lambda: ["file"])
    write_content: bool = True
    write_backup: bool = False
    scrape_delay_ms: int = 0
    parser_map: dict[str, str] = field(default_factory=dict)
    transformer_map: dict[str, str] = field(default_factory=dict)


@dataclass
class Link:
    """Represents a web page and the type of that page."""

    url: str
    page_type: str


@dataclass
class Payload:
    """Represents a payload moving through a scraping pipeline."""

    link: Link
    html_content: str | None = None
    json_content: str | None = None
    json_schema: str | None = None
    is_complete: bool = False
