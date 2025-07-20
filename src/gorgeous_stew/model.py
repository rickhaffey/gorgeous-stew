"""Defines the data models used in the scraping pipeline."""

from dataclasses import dataclass, field

from pydantic import BaseModel


class PipelineConfig(BaseModel):
    """
    Represents the configuration for the scraping pipeline.

    Attributes:
        html_root_dir: The directory where HTML files will be stored.
        json_root_dir: The directory where JSON files will be stored.
        read_sequence: The sequence of sources to attempt reading from when
          attempting to scrape a Payload's link within the pipeline.
        write_content: Whether to write content to the output files.
        write_backup: Whether to write backup files.
        scrape_delay_ms: Delay in milliseconds between scraping requests.
        parser_map: Mapping of content types to parser class names.
        transformer_map: Mapping of content types to transformer class names.
    """

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
    """
    Represents a web page and the type of that page.

    Attributes:
        href: The URL of the web page.
        rel: The relationship type of the link (e.g., "external", "next").
        content_type: The MIME type of the content at the link (e.g., "text/html").
    """

    href: str
    rel: str
    content_type: str


@dataclass
class Payload:
    """
    Represents a payload moving through a scraping pipeline.

    Attributes:
        link: The `Link` object associated with the payload.
        content: The content of the payload, if available.
        content_type: The MIME type of the content.
        is_complete: A flag indicating whether processing of
          the payload is complete.
    """

    link: Link
    content: str | None = None
    content_type: str | None = None
    is_complete: bool = False
