"""Память калькулятора (M+, M-, MR, MC)."""

from decimal import Decimal


class Memory:
    """Хранит одно значение, с которым можно выполнять операции."""

    def __init__(self):
        self.value = Decimal("0")

    def add(self, value):
        """M+ — добавляет значение к памяти."""
        self.value += value

    def subtract(self, value):
        """M- — вычитает значение из памяти."""
        self.value -= value

    def recall(self):
        """MR — возвращает сохранённое значение."""
        return self.value

    def clear(self):
        """MC — обнуляет память."""
        self.value = Decimal("0")
