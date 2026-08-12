"""Интерфейс приложения: меню, таблицы и экраны на базе Rich."""

import os
import sys
import time
from decimal import Decimal

from rich import box
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from calculator import CalculatorError, format_number
from statistics import OPERATION_LABELS
from validator import parse_yes_no


def _enable_vt():
    """Включает поддержку ANSI-эскейпов в обычной консоли Windows (cmd)."""
    if os.name != "nt":
        return
    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)
        mode = ctypes.c_uint32()
        if handle and handle != -1 and kernel32.GetConsoleMode(
            handle, ctypes.byref(mode)
        ):
            kernel32.SetConsoleMode(handle, mode.value | 0x0004)
    except Exception:
        pass


def _vt_supported():
    """Проверяет, обрабатывает ли консоль ANSI-эскейпы.

    Шлёт запрос позиции курсора (\x1b[6n): консоль с поддержкой ANSI
    отвечает \x1b[r;cR, устаревшая (legacy) — молчит. Если ANSI не
    работает, цвета в Rich отключаются, иначе их последовательности
    печатались бы как мусор.
    """
    if os.name != "nt":
        return True
    try:
        import ctypes
        import msvcrt

        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)
        mode = ctypes.c_uint32()
        if not handle or handle == -1:
            return False
        if not kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            return False
        sys.stdout.write("\x1b[6n")
        sys.stdout.flush()
        deadline = time.monotonic() + 0.3
        seen = ""
        while time.monotonic() < deadline:
            if msvcrt.kbhit():
                seen += msvcrt.getwch()
                if "R" in seen:
                    return True
            time.sleep(0.02)
        return False
    except Exception:
        return False


_enable_vt()
_USE_COLORS = _vt_supported()
console = Console(color_system=None if not _USE_COLORS else "auto")


def _clear_screen():
    """Очищает видимую область консоли через WinAPI — работает в cmd без ANSI.

    ANSI-эскейпы (\x1b[2J) в некоторых консолях Windows не обрабатываются,
    из-за чего меню дублируется при каждой перерисовке. Прямой вызов
    консольного API очищает экран и ставит курсор в начало в любом случае.
    """
    if os.name != "nt":
        sys.stdout.write("\x1b[2J\x1b[H")
        sys.stdout.flush()
        return
    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32

        class Coord(ctypes.Structure):
            _fields_ = [("X", ctypes.c_short), ("Y", ctypes.c_short)]

        class SmallRect(ctypes.Structure):
            _fields_ = [
                ("Left", ctypes.c_short),
                ("Top", ctypes.c_short),
                ("Right", ctypes.c_short),
                ("Bottom", ctypes.c_short),
            ]

        class ConsoleScreenBufferInfo(ctypes.Structure):
            _fields_ = [
                ("dwSize", Coord),
                ("dwCursorPosition", Coord),
                ("wAttributes", ctypes.c_ushort),
                ("srWindow", SmallRect),
                ("dwMaximumWindowSize", Coord),
            ]

        handle = kernel32.GetStdHandle(-11)
        if not handle or handle == -1:
            return
        csbi = ConsoleScreenBufferInfo()
        if not kernel32.GetConsoleScreenBufferInfo(handle, ctypes.byref(csbi)):
            return
        width = csbi.srWindow.Right - csbi.srWindow.Left + 1
        height = csbi.srWindow.Bottom - csbi.srWindow.Top + 1
        origin = Coord(0, csbi.srWindow.Top)
        written = ctypes.c_ulong(0)
        kernel32.FillConsoleOutputCharacterW.argtypes = [
            ctypes.c_void_p, ctypes.c_wchar, ctypes.c_uint, Coord,
            ctypes.POINTER(ctypes.c_ulong),
        ]
        kernel32.SetConsoleCursorPosition.argtypes = [ctypes.c_void_p, Coord]
        kernel32.FillConsoleOutputCharacterW(
            handle, " ", width * height, origin, ctypes.byref(written)
        )
        kernel32.SetConsoleCursorPosition(handle, origin)
    except Exception:
        try:
            os.system("cls")
        except Exception:
            pass


_clear_screen()

IDLE_ERROR_SECONDS = 5
MENU_MIN_WIDTH = 40

MAIN_MENU_ITEMS = [
    ("1", "Память"),
    ("2", "История"),
    ("3", "Статистика"),
    ("4", "Поиск по истории"),
    ("5", "Экспорт"),
    ("6", "Диагностика"),
    ("0", "Выход"),
]

MEMORY_MENU_ITEMS = [
    ("1", "MR — показать память"),
    ("2", "M+ — добавить ANS к памяти"),
    ("3", "M- — вычесть ANS из памяти"),
    ("4", "MC — очистить память"),
    ("0", "Назад"),
]

HISTORY_MENU_ITEMS = [
    ("1", "Очистить историю"),
    ("0", "Назад"),
]

STATISTICS_MENU_ITEMS = [
    ("0", "Назад"),
]

SEARCH_MENU_ITEMS = [
    ("0", "Назад"),
]

EXPORT_MENU_ITEMS = [
    ("1", "TXT"),
    ("2", "JSON"),
    ("3", "CSV"),
    ("4", "Все форматы"),
    ("0", "Назад"),
]


def input_line(prompt=""):
    """Читает строку; при EOF возвращает None."""
    try:
        return input(prompt)
    except EOFError:
        return None


def read_yes_no(prompt):
    """Читает ответ да/нет, повторяя запрос при ошибке ввода."""
    while True:
        value = input_line(prompt)
        if value is None:
            raise EOFError
        try:
            return parse_yes_no(value)
        except ValueError as error:
            print_error(error)


def press_enter():
    """Пауза, чтобы пользователь успел прочитать вывод."""
    console.print("[dim]Нажмите Enter, чтобы продолжить...[/dim]", end="")
    input_line("")


def print_error(error):
    """Экран ошибки: пользовательская ошибка не роняет программу."""
    if isinstance(error, CalculatorError):
        error_type = "Математическая ошибка"
    elif isinstance(error, ValueError):
        error_type = "Некорректный ввод"
    else:
        error_type = type(error).__name__
    console.print(
        Panel(
            f"[bold red]ОШИБКА[/bold red]\n\n"
            f"[bold]Тип:[/bold] {error_type}\n"
            f"[bold]Причина:[/bold] {error}",
            border_style="red",
        )
    )


def _read_key(timeout=0.25):
    """Читает одну клавишу; если нажатий нет, возвращает ('timeout',).

    Таймаут нужен, чтобы после паузы в вводе показать ошибку в окне.
    """
    if os.name == "nt":
        import msvcrt

        deadline = time.monotonic() + timeout
        while True:
            if msvcrt.kbhit():
                return _decode_windows_key(msvcrt.getwch())
            if time.monotonic() >= deadline:
                return ("timeout",)
            time.sleep(0.05)
    try:
        import select
        import termios
        import tty
    except ImportError:
        return ("timeout",)
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ready, _, _ = select.select([sys.stdin], [], [], timeout)
        if not ready:
            return ("timeout",)
        first = sys.stdin.read(1)
        if first == "\x1b":
            seq = sys.stdin.read(2)
            if seq == "[A":
                return ("arrow", "up")
            if seq == "[B":
                return ("arrow", "down")
            return ("unknown",)
        if first in ("\r", "\n"):
            return ("enter",)
        if first in ("\b", "\x7f"):
            return ("backspace",)
        if first == "\x03":
            raise KeyboardInterrupt
        if first.isprintable():
            return ("char", first)
        return ("unknown",)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def _decode_windows_key(first):
    """Разбирает скан-коды клавиш Windows (msvcrt)."""
    import msvcrt

    if first in ("\x00", "\xe0"):
        second = msvcrt.getwch()
        if second == "H":
            return ("arrow", "up")
        if second == "P":
            return ("arrow", "down")
        return ("unknown",)
    if first == "\r":
        return ("enter",)
    if first == "\x1b":
        return ("esc",)
    if first in ("\b", "\x7f"):
        return ("backspace",)
    if first.isprintable():
        return ("char", first)
    return ("unknown",)


def _window_panel(expression, result, ok=True):
    """Окошко результата — как дисплей калькулятора."""
    color = "green" if ok else "red"
    text = result if ok else f"! {result}"
    return Panel(
        f"[bold]{expression or '—'}[/bold]\n[bold {color}]= {text}[/bold {color}]",
        title="[dim]РЕЗУЛЬТАТ[/dim]",
        border_style=color,
        padding=(0, 1),
    )


def _window_content(display, buffer, preview, idle):
    """Панель окна результата.

    preview возвращает (успех, текст, завершено). Результат и ошибка
    завершённого выражения (25/0) показываются сразу, а ошибка
    незавершённого (10 /) — только после паузы больше IDLE_ERROR_SECONDS.
    """
    if buffer and preview and not (len(buffer) == 1 and buffer.isdigit()):
        ok, text, complete = preview(buffer)
        if ok:
            return _window_panel(buffer, text, True)
        if complete or idle:
            return _window_panel(buffer, text, False)
    if display is None:
        return None
    expression, text, ok = display
    return _window_panel(expression, text, ok)


def _menu_renderable(
    title, items, selected, buffer, expression_allowed, display,
    preview, idle, message="", content=None,
):
    """Один кадр меню: таблица, окно результата, контент, подсказки, ввод."""
    table = Table(show_header=False, box=box.DOUBLE, min_width=MENU_MIN_WIDTH)
    table.add_column()
    table.add_row(f"[bold cyan]{title}[/bold cyan]")
    window = _window_content(display, buffer, preview, idle)
    if window is not None:
        table.add_section()
        table.add_row(window)
    if content is not None:
        table.add_section()
        table.add_row(content)
    table.add_section()
    for index, (key, label) in enumerate(items):
        if index == selected:
            table.add_row(f"[bold cyan]> {key}  {label}[/bold cyan]")
        else:
            table.add_row(f"  {key}  {label}")
    lines = [table]
    if message:
        lines.append(f"[red]! {message}[/red]")
    if expression_allowed:
        lines.append(
            "[dim]Введите выражение или выберите пункт ⇅ "
            "и нажмите Enter[/dim]"
        )
    else:
        lines.append("[dim]Вверх/Вниз — выбрать пункт, Enter — подтвердить[/dim]")
    lines.append(f"[bold]> {buffer}[/bold]")
    return Group(*lines)


def _pipe_menu(title, items, expression_allowed, display=None, content=None):
    """Текстовое меню для неинтерактивного режима (перенаправленный ввод)."""
    if content is not None:
        console.print(content)
    console.print(_menu_table(title, items, display))
    while True:
        value = input_line("> ")
        if value is None:
            raise EOFError
        value = value.strip()
        if len(value) == 1 and value.isdigit():
            return ("menu", value)
        if not value:
            return ("menu", "0")
        if expression_allowed:
            return ("text", value)
        print_error(ValueError("Введите номер пункта меню цифрой."))


def smart_menu(
    title, items, expression_allowed=False, display=None, preview=None,
    content=None,
):
    """Меню с навигацией стрелками.

    Меню рисуется один раз, а при каждом нажатии клавиши экран
    очищается и рисуется заново — в консоли всегда ровно один кадр.
    display — пара (выражение, результат) для окна результата,
    preview — функция живого предпросмотра вводимого выражения,
    content — дополнительное содержимое (например, таблица истории),
    показываемое внутри меню.
    Ошибка предпросмотра показывается только после паузы ввода
    больше IDLE_ERROR_SECONDS секунд.
    Возвращает ('menu', ключ_пункта) или ('text', введённая_строка).
    """
    if not sys.stdin.isatty():
        return _pipe_menu(title, items, expression_allowed, display, content)
    selected = 0
    buffer = ""
    message = ""
    last_key_time = time.monotonic()
    error_shown = False

    def draw(idle):
        _clear_screen()
        console.print(
            _menu_renderable(
                title, items, selected, buffer, expression_allowed,
                display, preview, idle, message, content,
            )
        )

    draw(False)
    while True:
        key = _read_key()
        if key[0] == "timeout":
            if (
                not error_shown
                and time.monotonic() - last_key_time >= IDLE_ERROR_SECONDS
            ):
                error_shown = True
                draw(True)
            continue
        error_shown = False
        message = ""
        last_key_time = time.monotonic()
        if key[0] == "arrow":
            direction = 1 if key[1] == "down" else -1
            selected = (selected + direction) % len(items)
        elif key[0] == "char" and key[1]:
            buffer += key[1]
        elif key[0] == "backspace":
            buffer = buffer[:-1]
        elif key[0] == "enter":
            if buffer:
                if len(buffer) == 1 and buffer.isdigit():
                    return ("menu", buffer)
                if expression_allowed:
                    return ("text", buffer)
                message = "Введите номер пункта меню цифрой."
                buffer = ""
            else:
                return ("menu", items[selected][0])
        elif key[0] == "esc":
            return ("menu", "0")
        draw(False)


def _menu_table(title, items, display=None):
    table = Table(show_header=False, box=box.DOUBLE, min_width=MENU_MIN_WIDTH)
    table.add_column()
    table.add_row(f"[bold cyan]{title}[/bold cyan]")
    if display is not None:
        table.add_section()
        table.add_row(_window_panel(*display))
    table.add_section()
    for key, label in items:
        table.add_row(f"[bold]{key}[/bold]  {label}")
    return table


def show_welcome():
    """Приветственный экран при запуске."""
    console.print(
        Panel.fit(
            "[bold cyan]SMART CALC[/bold cyan]\n"
            "[cyan]Console Calculator v2.0[/cyan]",
            border_style="cyan",
        )
    )


def show_goodbye():
    """Прощальный экран при выходе."""
    console.print(Panel.fit("[bold cyan]До свидания![/bold cyan]", border_style="cyan"))


def show_result(expression, result):
    """Выводит результат вычисления."""
    console.print(f"  [bold]{expression} = {format_number(result)}[/bold]")


def show_last_result(last_result: Decimal):
    """Выводит последний результат (ANS)."""
    console.print(
        f"Последний результат: [bold green]{format_number(last_result)}[/bold green]"
    )


def build_history_table(
    records, title=None, empty_message="История пуста.", bordered=True,
):
    """Строит таблицу истории операций.

    bordered=False — без внешних границ: для показа внутри меню,
    где рамку даёт само меню.
    """
    if not records:
        return Text(empty_message, style="yellow")
    table = Table(
        title=title,
        box=box.DOUBLE if bordered else box.SIMPLE_HEAD,
    )
    table.add_column("ID", justify="right", style="cyan")
    table.add_column("Время", style="dim")
    table.add_column("Выражение")
    table.add_column("Результат", justify="right", style="bold green")
    for item in reversed(records):
        table.add_row(
            str(item["id"]),
            item["timestamp"],
            item["expression"],
            item["result"],
        )
    return table


def show_history(records, title="ИСТОРИЯ"):
    """Выводит таблицу истории операций."""
    console.print(build_history_table(records, title=title))


def build_statistics_table(stats, bordered=True):
    """Строит таблицу статистики.

    bordered=False — без внешних границ: для показа внутри меню.
    """
    table = Table(
        box=box.DOUBLE if bordered else box.SIMPLE_HEAD,
    )
    table.add_column("Показатель")
    table.add_column("Значение", justify="right")
    table.add_row("Всего операций", str(stats["total"]))
    table.add_section()
    for key, count in stats["counts"].items():
        table.add_row(OPERATION_LABELS.get(key, key), str(count))
    table.add_section()
    if stats["most_frequent"]:
        label, count = stats["most_frequent"]
        table.add_row("Самая частая операция", f"{label} ({count})")
    table.add_row("Последняя операция", stats["last_timestamp"])
    return table


def show_statistics(stats):
    """Выводит статистику операций."""
    console.print(build_statistics_table(stats))


def show_export_result(paths):
    """Выводит список созданных файлов экспорта."""
    console.print("[green]Экспорт завершён:[/green]")
    for path in paths:
        console.print(f"  [cyan]{path}[/cyan]")


def show_diagnostics(results):
    """Выводит таблицу результатов самодиагностики."""
    table = Table(title="SELF DIAGNOSTICS", box=box.ROUNDED)
    table.add_column("Проверка")
    table.add_column("Статус", justify="right")
    for name, passed in results:
        status = "[green]PASS[/green]" if passed else "[red]FAIL[/red]"
        table.add_row(name, status)
    console.print(table)
    passed = sum(1 for _, ok in results if ok)
    console.print(f"[bold]RESULT: {passed}/{len(results)} TESTS PASSED[/bold]")
