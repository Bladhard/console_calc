"""Тесты менеджера истории (history.py)."""

from history import HistoryManager


def test_add_and_get(tmp_path):
    manager = HistoryManager(tmp_path / "history.json")
    manager.add("10 + 20", "30", "addition")
    records = manager.get_all()
    assert len(records) == 1
    assert records[0]["expression"] == "10 + 20"
    assert records[0]["result"] == "30"
    assert records[0]["operation"] == "addition"
    assert records[0]["id"] == 1
    assert records[0]["timestamp"]


def test_ids_increment(tmp_path):
    manager = HistoryManager(tmp_path / "history.json")
    manager.add("1 + 1", "2", "addition")
    manager.add("2 + 2", "4", "addition")
    records = manager.get_all()
    assert [item["id"] for item in records] == [1, 2]


def test_clear(tmp_path):
    manager = HistoryManager(tmp_path / "history.json")
    manager.add("1 + 1", "2", "addition")
    manager.clear()
    assert manager.get_all() == []


def test_search(tmp_path):
    manager = HistoryManager(tmp_path / "history.json")
    manager.add("100 + 50", "150", "addition")
    manager.add("100 / 4", "25", "division")
    manager.add("5 * 8", "40", "multiplication")
    assert len(manager.search("100")) == 2
    assert len(manager.search("division")) == 1
    assert len(manager.search("40")) == 1
    assert len(manager.search("404")) == 0


def test_persist_between_instances(tmp_path):
    path = tmp_path / "history.json"
    HistoryManager(path).add("1 + 1", "2", "addition")
    records = HistoryManager(path).get_all()
    assert len(records) == 1


def test_corrupt_file(tmp_path):
    path = tmp_path / "history.json"
    path.write_text("{ not valid json", encoding="utf-8")
    manager = HistoryManager(path)
    assert manager.get_all() == []
