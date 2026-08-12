"""Хранение истории операций в JSON."""

import json
from datetime import datetime
from pathlib import Path


class HistoryManager:
    """Управляет историей операций, сохраняя её в JSON-файл."""

    def __init__(self, filename="data/history.json"):
        self.filename = Path(filename)
        self.filename.parent.mkdir(parents=True, exist_ok=True)
        if not self.filename.exists():
            self._save([])

    def _load(self):
        try:
            with self.filename.open("r", encoding="utf-8") as file:
                return json.load(file)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _save(self, data):
        with self.filename.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def add(self, expression, result, operation):
        """Добавляет запись об успешной операции."""
        history = self._load()
        next_id = max((item["id"] for item in history), default=0) + 1
        record = {
            "id": next_id,
            "expression": expression,
            "result": str(result),
            "operation": operation,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        history.append(record)
        self._save(history)
        return record

    def get_all(self):
        """Возвращает все записи истории."""
        return self._load()

    def clear(self):
        """Полностью очищает историю."""
        self._save([])

    def search(self, query):
        """Ищет записи по выражению, операции или результату."""
        history = self._load()
        query = query.strip().lower()
        return [
            item
            for item in history
            if query in item["expression"].lower()
            or query in item["operation"].lower()
            or query in item["result"].lower()
        ]
