"""Тесты математических функций calculator.py."""

from decimal import Decimal

import pytest

from calculator import (
    CalculatorError,
    add,
    divide,
    format_number,
    modulo,
    multiply,
    power,
    square_root,
    subtract,
)


def test_add():
    assert add(Decimal("10"), Decimal("5")) == Decimal("15")


def test_subtract():
    assert subtract(Decimal("10"), Decimal("5")) == Decimal("5")


def test_multiply():
    assert multiply(Decimal("10"), Decimal("5")) == Decimal("50")


def test_divide():
    assert divide(Decimal("10"), Decimal("5")) == Decimal("2")


def test_divide_decimal():
    assert divide(Decimal("10"), Decimal("4")) == Decimal("2.5")


def test_divide_by_zero():
    with pytest.raises(CalculatorError):
        divide(Decimal("1"), Decimal("0"))


def test_power():
    assert power(Decimal("2"), Decimal("10")) == Decimal("1024")


def test_power_huge_exponent():
    with pytest.raises(CalculatorError):
        power(Decimal("2"), Decimal("1000000000"))


def test_power_negative_base():
    with pytest.raises(CalculatorError):
        power(Decimal("-2"), Decimal("0.5"))


def test_modulo():
    assert modulo(Decimal("10"), Decimal("3")) == Decimal("1")


def test_modulo_by_zero():
    with pytest.raises(CalculatorError):
        modulo(Decimal("10"), Decimal("0"))


def test_square_root():
    assert square_root(Decimal("16")) == Decimal("4")


def test_square_root_negative():
    with pytest.raises(CalculatorError):
        square_root(Decimal("-1"))


def test_decimal_precision():
    assert Decimal("0.1") + Decimal("0.2") == Decimal("0.3")


def test_format_number_integer():
    assert format_number(Decimal("18.0")) == "18"


def test_format_number_fraction():
    assert format_number(Decimal("0.3")) == "0.3"
