"""Проверка и преобразование пользовательского ввода."""

from decimal import Decimal, InvalidOperation


def parse_number(value: str) -> Decimal:
    """Преобразует строку в Decimal с понятной ошибкой."""
    value = value.strip().replace(",", ".")
    if not value:
        raise ValueError("Число не может быть пустым.")
    try:
        return Decimal(value)
    except InvalidOperation:
        raise ValueError(f"Некорректное число: '{value}'. Ожидалось число, например: 10, -15, 12.5")


def parse_choice(value: str, max_choice: int) -> int:
    """Проверяет, что введён номер пункта меню от 0 до max_choice."""
    value = value.strip()
    if not value.isdigit():
        raise ValueError("Введите номер пункта меню цифрой.")
    choice = int(value)
    if not 0 <= choice <= max_choice:
        raise ValueError(f"Пункт меню должен быть от 0 до {max_choice}.")
    return choice


def parse_yes_no(value: str) -> bool:
    """Преобразует ответ да/нет в булево значение."""
    value = value.strip().lower()
    if value in ("y", "yes", "да", "д", "1"):
        return True
    if value in ("n", "no", "нет", "н", "0"):
        return False
    raise ValueError("Ответьте 'да' или 'нет'.")
