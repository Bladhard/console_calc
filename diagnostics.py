"""Самодиагностика всех модулей калькулятора."""

import tempfile
from decimal import Decimal
from pathlib import Path

from calculator import (
    CalculatorError,
    add,
    divide,
    multiply,
    subtract,
)
from exporter import export_txt
from history import HistoryManager
from memory import Memory
from parser import evaluate


def _test_addition():
    assert add(Decimal("2"), Decimal("3")) == Decimal("5")


def _test_subtraction():
    assert subtract(Decimal("10"), Decimal("4")) == Decimal("6")


def _test_multiplication():
    assert multiply(Decimal("3"), Decimal("4")) == Decimal("12")


def _test_division():
    assert divide(Decimal("20"), Decimal("4")) == Decimal("5")


def _test_division_by_zero():
    try:
        divide(Decimal("1"), Decimal("0"))
    except CalculatorError:
        return
    raise AssertionError("Ожидалась ошибка деления на ноль")


def _test_decimal_numbers():
    assert Decimal("0.1") + Decimal("0.2") == Decimal("0.3")


def _test_history():
    with tempfile.TemporaryDirectory() as tmp:
        manager = HistoryManager(Path(tmp) / "history.json")
        manager.add("2 + 2", "4", "addition")
        assert len(manager.get_all()) == 1
        assert manager.search("2 + 2")
        manager.clear()
        assert manager.get_all() == []


def _test_expression_parser():
    assert evaluate("(10 + 5) * 2") == Decimal("30")
    assert evaluate("2 ^ 10") == Decimal("1024")


def _test_memory():
    memory = Memory()
    memory.add(Decimal("5"))
    memory.subtract(Decimal("2"))
    assert memory.recall() == Decimal("3")
    memory.clear()
    assert memory.recall() == Decimal("0")


def _test_export():
    record = {
        "id": 1,
        "timestamp": "2026-08-11 16:20:01",
        "expression": "10 + 20",
        "result": "30",
        "operation": "addition",
    }
    with tempfile.TemporaryDirectory() as tmp:
        path = export_txt([record], Path(tmp) / "history.txt")
        assert path.exists()
        assert "10 + 20 = 30" in path.read_text(encoding="utf-8")


TESTS = [
    ("Addition", _test_addition),
    ("Subtraction", _test_subtraction),
    ("Multiplication", _test_multiplication),
    ("Division", _test_division),
    ("Division by zero", _test_division_by_zero),
    ("Decimal numbers", _test_decimal_numbers),
    ("History", _test_history),
    ("Expression parser", _test_expression_parser),
    ("Memory", _test_memory),
    ("Export", _test_export),
]


def run_diagnostics():
    """Запускает все проверки и возвращает список (имя, пройдено)."""
    results = []
    for name, test in TESTS:
        try:
            test()
        except Exception:
            results.append((name, False))
        else:
            results.append((name, True))
    return results
