"""Тесты памяти калькулятора (memory.py)."""

from decimal import Decimal

from memory import Memory


def test_initial_zero():
    assert Memory().recall() == Decimal("0")


def test_add():
    memory = Memory()
    memory.add(Decimal("5"))
    assert memory.recall() == Decimal("5")


def test_subtract():
    memory = Memory()
    memory.add(Decimal("10"))
    memory.subtract(Decimal("3"))
    assert memory.recall() == Decimal("7")


def test_clear():
    memory = Memory()
    memory.add(Decimal("5"))
    memory.clear()
    assert memory.recall() == Decimal("0")
