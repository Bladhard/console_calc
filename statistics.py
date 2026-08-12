"""Статистика по истории операций.

Операции определяются "живо" — по символам в выражении, которое ввёл
пользователь (например, "25+56" — сложение, "10/2" — деление).
Одно выражение может содержать несколько операций: "2+5*3" засчитывается
и в сложение, и в умножение.
"""

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

# Порядок приоритета для выбора главной операции записи
_PRIMARY_ORDER = (
    "square_root",
    "power",
    "modulo",
    "division",
    "multiplication",
    "subtraction",
    "addition",
)


def detect_operations(expression):
    """Определяет операции по символам в выражении.

    Возвращает set ключей операций. Пустое/неразбираемое выражение —
    "expression".
    """
    expr = str(expression).replace(" ", "")
    if not expr:
        return {"expression"}
    ops = set()
    if "√" in expr or "sqrt" in expr.lower():
        ops.add("square_root")
    if "/" in expr:
        ops.add("division")
    if "%" in expr:
        ops.add("modulo")
    if "^" in expr:
        ops.add("power")
    if "*" in expr:
        ops.add("multiplication")
    if "+" in expr:
        ops.add("addition")
    if "-" in expr:
        ops.add("subtraction")
    return ops or {"expression"}


def primary_operation(expression):
    """Главная операция выражения (для записи в историю и поиска)."""
    ops = detect_operations(expression)
    if ops == {"expression"}:
        return "expression"
    for key in _PRIMARY_ORDER:
        if key in ops:
            return key
    return "expression"


def compute_statistics(records):
    """Считает статистику по записям истории."""
    counts = Counter()
    for item in records:
        for op in detect_operations(item.get("expression", "")):
            counts[op] += 1
    ordered = {
        key: counts[key]
        for key in sorted(counts, key=lambda k: OPERATION_LABELS.get(k, k))
    }
    most_frequent = None
    if ordered:
        key, count = max(ordered.items(), key=lambda pair: pair[1])
        most_frequent = (OPERATION_LABELS.get(key, key), count)
    last_timestamp = records[-1].get("timestamp", "—") if records else "—"
    return {
        "total": len(records),
        "counts": ordered,
        "most_frequent": most_frequent,
        "last_timestamp": last_timestamp,
    }
