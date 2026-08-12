"""Безопасный разбор и вычисление математических выражений.

Вместо eval() используется разбор AST с whitelist разрешённых узлов.
Пользователь не может выполнить произвольный Python-код.
"""

import ast
import operator
import re
from decimal import Decimal, DivisionByZero, InvalidOperation

from calculator import CalculatorError, power as decimal_power, square_root

BIN_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.Pow: decimal_power,
}

UNARY_OPERATORS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


class ExpressionSyntaxError(CalculatorError):
    """Синтаксическая ошибка: выражение незавершено или неверно записано.

    Такое выражение обычно ещё набирают (например, "10 /" или "1+").
    """


def preprocess(expression: str, last_result) -> str:
    """Подготавливает строку: подставляет ANS, заменяет ^ и √."""
    expression = expression.strip()
    if not expression:
        raise CalculatorError("Выражение не может быть пустым.")
    expression = expression.replace("√", "sqrt")
    expression = re.sub(
        r"\bANS\b", str(last_result), expression, flags=re.IGNORECASE
    )
    expression = expression.replace("^", "**")
    return expression


def _evaluate(node, last_result):
    if isinstance(node, ast.Expression):
        return _evaluate(node.body, last_result)
    if isinstance(node, ast.Constant):
        if isinstance(node.value, bool) or not isinstance(
            node.value, (int, float)
        ):
            raise CalculatorError("В выражении разрешены только числа.")
        return Decimal(str(node.value))
    if isinstance(node, ast.BinOp):
        func = BIN_OPERATORS.get(type(node.op))
        if func is None:
            raise CalculatorError(
                f"Операция {type(node.op).__name__} не поддерживается."
            )
        left = _evaluate(node.left, last_result)
        right = _evaluate(node.right, last_result)
        try:
            return func(left, right)
        except DivisionByZero:
            raise CalculatorError("Деление на ноль невозможно.")
        except InvalidOperation:
            raise CalculatorError("Невозможно выполнить операцию над числами.")
    if isinstance(node, ast.UnaryOp):
        func = UNARY_OPERATORS.get(type(node.op))
        if func is None:
            raise CalculatorError("Неподдерживаемая унарная операция.")
        return func(_evaluate(node.operand, last_result))
    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name) or node.func.id.lower() != "sqrt":
            raise CalculatorError("В выражениях разрешён только вызов sqrt().")
        if len(node.args) != 1 or node.keywords:
            raise CalculatorError("sqrt() принимает ровно один аргумент.")
        return square_root(_evaluate(node.args[0], last_result))
    raise CalculatorError(
        f"Конструкция {type(node).__name__} не поддерживается."
    )


def evaluate(expression: str, last_result=Decimal("0")) -> Decimal:
    """Вычисляет математическое выражение безопасно, без eval()."""
    text = preprocess(expression, last_result)
    try:
        tree = ast.parse(text, mode="eval")
    except SyntaxError:
        raise ExpressionSyntaxError(
            "Некорректное выражение: проверьте операторы и скобки."
        )
    try:
        return _evaluate(tree, last_result)
    except (OverflowError, InvalidOperation):
        raise CalculatorError("Результат слишком велик или не определён.")
