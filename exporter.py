"""Экспорт истории в TXT, JSON и CSV."""

import csv
import json
from pathlib import Path


def export_txt(records, path):
    """Сохраняет историю в текстовом формате: #001 | дата | 10 + 20 = 30."""
    path = Path(path)
    lines = [
        f"#{item['id']:03d} | {item['timestamp']} | "
        f"{item['expression']} = {item['result']}"
        for item in records
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def export_json(records, path):
    """Сохраняет историю в формате JSON."""
    path = Path(path)
    data = [
        {
            "id": item["id"],
            "expression": item["expression"],
            "result": item["result"],
        }
        for item in records
    ]
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=4), encoding="utf-8"
    )
    return path


def export_csv(records, path):
    """Сохраняет историю в формате CSV."""
    path = Path(path)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["id", "timestamp", "expression", "result", "operation"])
        for item in records:
            writer.writerow(
                [
                    item["id"],
                    item["timestamp"],
                    item["expression"],
                    item["result"],
                    item["operation"],
                ]
            )
    return path


def export_all(records, directory="exports"):
    """Экспортирует историю во все три формата."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    return [
        export_txt(records, directory / "history.txt"),
        export_json(records, directory / "history.json"),
        export_csv(records, directory / "history.csv"),
    ]
