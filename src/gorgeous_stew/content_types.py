"""Content type utilities for Gorgeous Stew."""


def is_html_content_type(content_type: str | None) -> bool:
    """
    Check if the given content type is HTML.

    Args:
        content_type: The content type to check.

    Returns:
        bool: True if the content type is HTML, False otherwise.
    """
    if content_type is None:
        return False

    if content_type.startswith("text/html"):
        return True

    if content_type.startswith("application/xhtml"):
        return True

    if content_type.startswith("text") and content_type.endswith("+html"):  # noqa: SIM103
        # This is to support "vendor specific" HTML content types.
        # The namings on these are not official, but used internally.
        return True

    return False


def is_json_content_type(content_type: str | None) -> bool:
    """
    Check if the given content type is JSON.

    Args:
        content_type: The content type to check.

    Returns:
        bool: True if the content type is JSON, False otherwise.
    """
    if content_type is None:
        return False

    if content_type.startswith("application/json"):
        return True

    if content_type.startswith("application/vnd") and content_type.endswith("+json"):  # noqa: SIM103
        return True

    return False
