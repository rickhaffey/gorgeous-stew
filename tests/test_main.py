# ruff: noqa: D100, D103, S101


def func(x: int) -> int:
    return x + 1


def test_this_should_succeed() -> None:
    expected_value = 5
    assert func(4) == expected_value


def test_this_should_now_succeed() -> None:
    expected_value = 4
    assert func(3) == expected_value
