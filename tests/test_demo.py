# ruff: noqa: D100, D103, S101
from scraper.mocks import html_samples


def test_do_something() -> None:
    assert "all-cocktails" in html_samples
