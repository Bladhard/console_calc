"""Математическое ядро калькулятора на Decimal."""

from decimal import Decimal, InvalidOperation, Overflow


class CalculatorError(Exception):
    """Базовая ошибка калькулятора."""

    pass


def add(a: Decimal, b: Decimal) -> Decimal:
    """Сложение двух чисел."""
    return a + b


def subtract(a: Decimal, b: Decimal) -> Decimal:
    """Вычитание двух чисел."""
    return a - b


def multiply(a: Decimal, b: Decimal) -> Decimal:
    """Умножение двух чисел."""
    return a * b


def divide(a: Decimal, b: Decimal) -> Decimal:
    """Деление двух чисел."""
    if b == 0:
        raise CalculatorError("Деление на ноль невозможно.")
    return a / b


def power(a: Decimal, b: Decimal) -> Decimal:
    """Возведение числа в степень."""
    try:
        return a ** b
    except (ValueError, OverflowError, InvalidOperation, Overflow):
        raise CalculatorError(
            "Невозможно выполнить возведение в степень: "
            "слишком большая степень или отрицательное основание."
        )


def modulo(a: Decimal, b: Decimal) -> Decimal:
    """Остаток от деления."""
    if b == 0:
        raise CalculatorError("Остаток от деления на ноль невозможен.")
    return a % b


def square_root(a: Decimal) -> Decimal:
    """Квадратный корень числа."""
    if a < 0:
        raise CalculatorError(
            "Нельзя вычислить квадратный корень отрицательного числа."
        )
    return a.sqrt()


def format_number(value: Decimal) -> str:
    """Красивое строковое представление Decimal."""
    if not value.is_finite():
        return str(value)
    if abs(value) < Decimal("1e100"):
        if value == value.to_integral_value():
            return str(int(value))
        return format(value, "f")
    return format(value, "E").replace("E", "e")
