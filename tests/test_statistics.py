"""Тесты статистики (statistics.py)."""

from statistics import (
    OPERATION_LABELS,
    compute_statistics,
    detect_operations,
    primary_operation,
)


def test_detect_single_operations():
    assert detect_operations("1+1") == {"addition"}
    assert detect_operations("10-3") == {"subtraction"}
    assert detect_operations("2*3") == {"multiplication"}
    assert detect_operations("10/2") == {"division"}
    assert detect_operations("5^2") == {"power"}
    assert detect_operations("10%3") == {"modulo"}
    assert detect_operations("√9") == {"square_root"}
    assert detect_operations("sqrt(16)") == {"square_root"}


def test_detect_mixed_expression():
    ops = detect_operations("2+5*3")
    assert ops == {"addition", "multiplication"}
    assert detect_operations("(10+20)*3") == {"addition", "multiplication"}
    assert detect_operations("10/2+1") == {"division", "addition"}


def test_detect_ignores_spaces():
    assert detect_operations(" 25 + 56 ") == {"addition"}
    assert detect_operations("   ") == {"expression"}


def test_detect_unknown_expression():
    assert detect_operations("") == {"expression"}
    assert detect_operations("abc") == {"expression"}


def test_primary_operation_priority():
    assert primary_operation("√9") == "square_root"
    assert primary_operation("2^10") == "power"
    assert primary_operation("10%3") == "modulo"
    assert primary_operation("10/2") == "division"
    assert primary_operation("2*3") == "multiplication"
    assert primary_operation("10-3") == "subtraction"
    assert primary_operation("1+1") == "addition"
    assert primary_operation("10/2+1") == "division"
    assert primary_operation("abc") == "expression"


def test_compute_statistics_counts_by_expression():
    records = [
        {"expression": "1+1", "result": "2", "timestamp": "t1"},
        {"expression": "2+3", "result": "5", "timestamp": "t2"},
        {"expression": "10-4", "result": "6", "timestamp": "t3"},
        {"expression": "2*3+1", "result": "7", "timestamp": "t4"},
    ]
    stats = compute_statistics(records)
    assert stats["total"] == 4
    assert stats["counts"] == {
        "addition": 3,
        "multiplication": 1,
        "subtraction": 1,
    }
    assert stats["most_frequent"] == (OPERATION_LABELS["addition"], 3)
    assert stats["last_timestamp"] == "t4"


def test_compute_statistics_empty():
    stats = compute_statistics([])
    assert stats["total"] == 0
    assert stats["counts"] == {}
    assert stats["most_frequent"] is None
    assert stats["last_timestamp"] == "—"


def test_compute_statistics_old_records_without_expression():
    stats = compute_statistics([{"result": "2", "timestamp": "t1"}])
    assert stats["counts"] == {"expression": 1}
