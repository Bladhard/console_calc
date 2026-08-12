"""Статистика по истории операций."""

from collections import Counter

OPERATION_LABELS = {
    "addition": "Сложение",
    "subtraction": "Вычитание",
    "multiplication": "Умножение",
    "division": "Деление",
    "power": "Степень",
    "modulo": "Остаток",
    "square_root": "Квадратный корень",
    "expression": "Выражение",
}


def compute_statistics(records):
    """Считает статистику по записям истории."""
    counts = Counter(item.get("operation", "expression") for item in records)
    most_frequent = None
    if counts:
        key, count = counts.most_common(1)[0]
        most_frequent = (OPERATION_LABELS.get(key, key), count)
    last_timestamp = records[-1].get("timestamp", "—") if records else "—"
    return {
        "total": len(records),
        "counts": dict(counts),
        "most_frequent": most_frequent,
        "last_timestamp": last_timestamp,
    }
