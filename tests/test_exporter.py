"""Тесты экспорта истории (exporter.py)."""

import csv
import json

from exporter import export_all, export_csv, export_json, export_txt


def _records():
    return [
        {
            "id": 1,
            "timestamp": "2026-08-11 16:20:01",
            "expression": "10 + 20",
            "result": "30",
            "operation": "addition",
        }
    ]


def test_export_txt(tmp_path):
    path = export_txt(_records(), tmp_path / "history.txt")
    content = path.read_text(encoding="utf-8")
    assert "#001 | 2026-08-11 16:20:01 | 10 + 20 = 30" in content


def test_export_json(tmp_path):
    path = export_json(_records(), tmp_path / "history.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data[0]["expression"] == "10 + 20"
    assert data[0]["result"] == "30"


def test_export_csv(tmp_path):
    path = export_csv(_records(), tmp_path / "history.csv")
    rows = list(csv.reader(path.open(encoding="utf-8")))
    assert rows[0] == ["id", "timestamp", "expression", "result", "operation"]
    assert rows[1][3] == "30"


def test_export_all(tmp_path):
    paths = export_all(_records(), tmp_path)
    assert len(paths) == 3
    assert all(path.exists() for path in paths)
