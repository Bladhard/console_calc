"""Тесты проверки пользовательского ввода (validator.py)."""

from decimal import Decimal

import pytest

from validator import parse_choice, parse_number, parse_yes_no


def test_parse_number_integer():
    assert parse_number("10") == Decimal("10")


def test_parse_number_float():
    assert parse_number("10.5") == Decimal("10.5")


def test_parse_number_comma():
    assert parse_number("10,5") == Decimal("10.5")


def test_parse_number_negative():
    assert parse_number("-15.75") == Decimal("-15.75")


def test_parse_number_spaces():
    assert parse_number("  10  ") == Decimal("10")


def test_parse_number_empty():
    with pytest.raises(ValueError):
        parse_number("")


def test_parse_number_text():
    with pytest.raises(ValueError):
        parse_number("hello")


def test_parse_number_mixed():
    with pytest.raises(ValueError):
        parse_number("10abc")


def test_parse_choice_valid():
    assert parse_choice("3", 9) == 3


def test_parse_choice_zero():
    assert parse_choice("0", 9) == 0


def test_parse_choice_not_digit():
    with pytest.raises(ValueError):
        parse_choice("abc", 9)


def test_parse_choice_out_of_range():
    with pytest.raises(ValueError):
        parse_choice("10", 9)


def test_parse_yes_no_yes():
    assert parse_yes_no("да") is True


def test_parse_yes_no_no():
    assert parse_yes_no("n") is False


def test_parse_yes_no_invalid():
    with pytest.raises(ValueError):
        parse_yes_no("maybe")
