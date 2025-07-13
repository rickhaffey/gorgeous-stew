# ruff: noqa: D100, D103, S101
from scraper.demo.demo_component import do_something


def test_do_something() -> None:
    expected = 3 + 2
    actual = do_something(3, 2)
    assert actual == expected
