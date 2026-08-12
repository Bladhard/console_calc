"""Тесты безопасного парсера выражений (parser.py)."""

from decimal import Decimal

import pytest

from calculator import CalculatorError
from parser import ExpressionSyntaxError, evaluate


def test_simple_add():
    assert evaluate("10 + 20") == Decimal("30")


def test_simple_subtract():
    assert evaluate("10 - 20") == Decimal("-10")


def test_precedence():
    assert evaluate("10 + 20 * 3") == Decimal("70")


def test_parentheses():
    assert evaluate("(10 + 20) * 3") == Decimal("90")


def test_power_caret():
    assert evaluate("2 ^ 10") == Decimal("1024")


def test_power_double_star():
    assert evaluate("2 ** 10") == Decimal("1024")


def test_modulo():
    assert evaluate("10 % 3") == Decimal("1")


def test_division():
    assert evaluate("20 / 4") == Decimal("5")


def test_division_by_zero():
    with pytest.raises(CalculatorError):
        evaluate("10 / 0")


def test_division_by_zero_is_not_syntax_error():
    """Завершённое выражение: ошибка вычисления, а не синтаксиса."""
    with pytest.raises(CalculatorError) as excinfo:
        evaluate("10 / 0")
    assert not isinstance(excinfo.value, ExpressionSyntaxError)


def test_incomplete_expression_is_syntax_error():
    """Незавершённое выражение — именно синтаксическая ошибка."""
    with pytest.raises(ExpressionSyntaxError):
        evaluate("10 /")


def test_trailing_operator_is_syntax_error():
    with pytest.raises(ExpressionSyntaxError):
        evaluate("1 +")


def test_unary_minus():
    assert evaluate("-5 + 2") == Decimal("-3")


def test_ans_substitution():
    assert evaluate("ANS + 10", Decimal("25")) == Decimal("35")


def test_sqrt_function():
    assert evaluate("sqrt(16)") == Decimal("4")


def test_sqrt_symbol():
    assert evaluate("√(16)") == Decimal("4")


def test_sqrt_negative():
    with pytest.raises(CalculatorError):
        evaluate("sqrt(-1)")


def test_decimal_arithmetic():
    assert evaluate("0.1 + 0.2") == Decimal("0.3")


def test_double_plus_is_unary():
    assert evaluate("10 ++ 20") == Decimal("30")


def test_double_division_invalid():
    with pytest.raises(CalculatorError):
        evaluate("10 / / 2")


def test_unclosed_parenthesis():
    with pytest.raises(CalculatorError):
        evaluate("(10 + 20")


def test_unknown_function():
    with pytest.raises(CalculatorError):
        evaluate("sin(10)")


def test_name_rejected():
    with pytest.raises(CalculatorError):
        evaluate("x + 1")


def test_empty_expression():
    with pytest.raises(CalculatorError):
        evaluate("   ")


def test_huge_power_invalid():
    with pytest.raises(CalculatorError):
        evaluate("2 ^ 1000000000")
