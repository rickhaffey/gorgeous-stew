"""Defines the data models used in the scraping pipeline."""

from dataclasses import dataclass


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
