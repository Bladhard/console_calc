import sys
from decimal import Decimal

from calculator import CalculatorError, format_number
from exporter import export_all, export_csv, export_json, export_txt
from history import HistoryManager
from logger import get_logger
from memory import Memory
from parser import ExpressionSyntaxError, evaluate
from statistics import compute_statistics, primary_operation
from ui import (
    EXPORT_MENU_ITEMS,
    HISTORY_MENU_ITEMS,
    MAIN_MENU_ITEMS,
    MEMORY_MENU_ITEMS,
    SEARCH_MENU_ITEMS,
    STATISTICS_MENU_ITEMS,
    build_history_table,
    build_statistics_table,
    console,
    input_line,
    press_enter,
    print_error,
    read_yes_no,
    show_export_result,
    show_goodbye,
    show_result,
    show_welcome,
    smart_menu,
)

MEMORY_ACTIONS = {1: "MR", 2: "M+", 3: "M-", 4: "MC"}


def record_success(history, logger, expression, result, operation):
    """Сохраняет успешную операцию в историю и технический лог."""
    formatted = format_number(result)
    history.add(expression, formatted, operation)
    logger.info("Operation: %s = %s", expression, formatted)


def action_expression(history, logger, last_result, expression):
    """Вычисляет выражение с подстановкой ANS.

    Возвращает (выражение, результат) для окна результата в меню.
    """
    expression = expression.strip()
    result = evaluate(expression, last_result)
    record_success(history, logger, expression, result, primary_operation(expression))
    show_result(expression, result)
    return expression, result


def run_expression(history, logger, last_result, expression_line):
    """Вычисляет выражение и обновляет окно результата, включая ошибки.

    Возвращает (новый last_result, display). display — (выражение, текст, успех).
    """
    try:
        expression, result = action_expression(
            history, logger, last_result, expression_line
        )
        return result, (expression, format_number(result), True)
    except (CalculatorError, ValueError) as error:
        logger.error("%s", error)
        print_error(error)
        return last_result, (expression_line.strip(), str(error), False)


def action_memory(memory, logger, last_result):
    """Меню памяти: окно показывает сохранённое значение, M+/M-/MR/MC.

    После каждой операции возвращаемся в меню памяти с обновлённым окном.
    """
    while True:
        display = ("Память", format_number(memory.recall()), True)
        _, value = smart_menu("ПАМЯТЬ", MEMORY_MENU_ITEMS, display=display)
        choice = int(value)
        if choice == 0:
            return
        action = MEMORY_ACTIONS[choice]
        if action == "M+":
            memory.add(last_result)
        elif action == "M-":
            memory.subtract(last_result)
        elif action == "MC":
            memory.clear()
        logger.info("Memory: %s (ANS = %s)", action, format_number(last_result))


def action_history(history, logger):
    """История: список операций виден прямо в меню, очистка — по запросу."""
    records = history.get_all()
    _, value = smart_menu(
        "ИСТОРИЯ",
        HISTORY_MENU_ITEMS,
        content=build_history_table(records, bordered=False),
    )
    if int(value) == 1:
        if read_yes_no("Точно очистить историю? (да/нет): "):
            history.clear()
            logger.info("History cleared")
            console.print("[green]История очищена.[/green]")
        else:
            console.print("[yellow]Отменено.[/yellow]")
        press_enter()


def action_statistics(history):
    """Статистика: таблица видна прямо в меню."""
    smart_menu(
        "СТАТИСТИКА",
        STATISTICS_MENU_ITEMS,
        content=build_statistics_table(compute_statistics(history.get_all()), bordered=False),
    )


def action_search(history):
    """Поиск по истории: результаты видны прямо в меню."""
    query = input_line("Введите запрос: ")
    if query is None or not query.strip():
        console.print("[yellow]Запрос не может быть пустым.[/yellow]")
        press_enter()
        return
    query = query.strip()
    results = history.search(query)
    title = f"ПОИСК: {query}"
    empty_message = f"По запросу '{query}' ничего не найдено."
    smart_menu(
        "ПОИСК",
        SEARCH_MENU_ITEMS,
        content=build_history_table(results, title, empty_message, bordered=False),
    )


def action_export(history, logger):
    """Экспорт истории в TXT, JSON, CSV."""
    records = history.get_all()
    if not records:
        console.print("[yellow]История пуста — экспортировать нечего.[/yellow]")
        press_enter()
        return
    _, value = smart_menu("ЭКСПОРТ", EXPORT_MENU_ITEMS)
    choice = int(value)
    if choice == 0:
        return
    try:
        if choice == 1:
            paths = [export_txt(records, "exports/history.txt")]
        elif choice == 2:
            paths = [export_json(records, "exports/history.json")]
        elif choice == 3:
            paths = [export_csv(records, "exports/history.csv")]
        else:
            paths = export_all(records, "exports")
    except OSError as error:
        raise CalculatorError(f"Не удалось выполнить экспорт: {error}")
    show_export_result(paths)
    for path in paths:
        logger.info("Export completed: %s", path)
    press_enter()


def main():
    """Главный цикл приложения."""
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

    logger = get_logger()
    history = HistoryManager()
    memory = Memory()
    last_result = Decimal("0")
    display = ("", "0", True)

    def preview(expression):
        """Живой предпросмотр: результат или сообщение об ошибке.

        Возвращает (успех, текст, завершено). Для ошибок: завершённое
        выражение (25/0) показывается сразу, незавершённое (10 /) —
        после паузы ввода.
        """
        try:
            value = evaluate(expression, last_result)
        except ExpressionSyntaxError as error:
            return False, str(error), False
        except (CalculatorError, ValueError) as error:
            return False, str(error), True
        return True, format_number(value), True

    show_welcome()
    logger.info("Application started")

    while True:
        try:
            kind, value = smart_menu(
                "ГЛАВНОЕ МЕНЮ",
                MAIN_MENU_ITEMS,
                expression_allowed=True,
                display=display,
                preview=preview,
            )
            if kind == "text":
                last_result, display = run_expression(
                    history, logger, last_result, value
                )
                continue
            choice = int(value)
            if choice == 0:
                break
            if choice == 1:
                action_memory(memory, logger, last_result)
            elif choice == 2:
                action_history(history, logger)
            elif choice == 3:
                action_statistics(history)
            elif choice == 4:
                action_search(history)
            elif choice == 5:
                action_export(history, logger)
        except EOFError:
            break
        except KeyboardInterrupt:
            break
        except (CalculatorError, ValueError) as error:
            logger.error("%s", error)
            print_error(error)
        except Exception as error:
            logger.exception("Unexpected error: %s", error)
            print_error(error)

    logger.info("Application stopped")
    show_goodbye()


if __name__ == "__main__":
    main()
