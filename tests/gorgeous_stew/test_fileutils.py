# ruff: noqa: D100, S101
from datetime import UTC, datetime

from gorgeous_stew.fileutils import build_raw_filepath


def test_build_raw_filepath_removes_prefixes() -> None:
    """Test that build_raw_filepath removes prefixes from the URL."""
    expected = "www-example-com-path-to-resource.html"

    # http
    url = "http://www.example.com/path/to/resource"
    extension = "html"
    filepath = build_raw_filepath(url, extension)

    assert filepath.name == expected

    # https
    url = "https://www.example.com/path/to/resource"
    extension = "html"
    filepath = build_raw_filepath(url, extension)

    assert filepath.name == expected


def test_build_raw_filepath_removes_suffixes() -> None:
    """Test that build_raw_filepath removes suffixes from the URL."""
    url = "https://www.example.com/path/to/resource/"
    extension = "html"
    filepath = build_raw_filepath(url, extension)

    assert filepath.name == "www-example-com-path-to-resource.html"


def test_build_raw_filepath_replaces_special_characters() -> None:
    """Test that build_raw_filepath replaces special characters in the URL."""
    url = "https://www.example.com/path/to/resource_with_underscores"
    extension = "html"
    filepath = build_raw_filepath(url, extension)

    assert filepath.name == "www-example-com-path-to-resource-with-underscores.html"


def test_build_raw_filepath_with_tag_includes_tag_in_filename() -> None:
    """Test that build_raw_filepath includes the tag in the filename."""
    url = "https://www.example.com/path/to/resource"
    extension = "html"
    tag = "test-tag"
    filepath = build_raw_filepath(url, extension, tag=tag)

    assert "." + tag + "." in filepath.name


def test_build_raw_filepath_with_backup_includes_timestamp_and_bak_extension() -> None:
    """Test that build_raw_filepath includes the .bak extension for backups."""
    url = "https://www.example.com/path/to/resource"
    extension = "html"
    is_backup = True

    # capture the timestamp before and after building the filepath
    # this is to ensure the timestamp is included in the filename
    timestamp_before = datetime.now(tz=UTC)
    filepath = build_raw_filepath(url, extension, is_backup=is_backup)
    timestamp_after = datetime.now(tz=UTC)

    # the filename should still contain the original extension
    assert extension in filepath.name
    # the filename should contain the timestamp
    assert (
        timestamp_before.strftime("%Y%m%d%H%M") in filepath.name
        or timestamp_after.strftime("%Y%m%d%H%M") in filepath.name
    )
    # the filename should end with .bak
    assert filepath.name.endswith(".bak")
