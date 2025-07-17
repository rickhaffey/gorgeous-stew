"""Utility functions for file handling in the scraper pipeline."""

from datetime import UTC, datetime
from pathlib import Path

from loguru import logger


def _sanitize_url(url: str) -> str:
    """
    Sanitize a url for usage as a filename.

    - strip prefixes and suffixes
    - replace special characters
    """
    result = url

    for prefix in ["https://", "http://"]:
        result = result.removeprefix(prefix)

    result = result.removesuffix("/")

    for c in ["/", ".", "_"]:
        result = result.replace(c, "-")

    return result


def _build_timestamp() -> str:
    """Build a string representation of the current UTC timestamp."""
    return datetime.now(tz=UTC).strftime("%Y%m%d%H%M%S")


def build_raw_filepath(
    url: str, extension: str, *, tag: str | None = None, is_backup: bool = False
) -> Path:
    """
    Build a filename for data from the provided `url`.

    The default name of the file consists of a sanitized version of `url`
    with the `extension` provided.

    If `is_backup = True`, the name also includes a UTC timestamp and an
    additional '.bak' extension.

    Args:
      url: The URL to sanitize and use as part of the filename.
      extension: The file extension to use.
      tag: Optional tag to append to the filename. Defaults to None.
      is_backup: Whether this is a backup file. Defaults to False.
    """
    file_name = _sanitize_url(url)

    # append the tag if provided
    if tag:
        file_name = f"{file_name}.{tag}"

    # append the extension, stipping leading dot if present
    extension = extension.removeprefix(".")
    file_name = f"{file_name}.{extension}"

    # if this is a backup file, append the timestamp and '.bak' extension
    if is_backup:
        file_name = f"{file_name}.{_build_timestamp()}.bak"

    log_msg_template = (
        "Building raw filename for URL: {url} "
        "with tag: {tag} and extension: {extension} "
        " (is_backup={is_backup}), resulting filename: {file_name}"
    )
    logger.info(
        log_msg_template,
        url=url,
        tag=tag,
        extension=extension,
        is_backup=is_backup,
        file_name=file_name,
    )

    return Path(file_name)
