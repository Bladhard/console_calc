"""Тесты самодиагностики (diagnostics.py)."""

from diagnostics import run_diagnostics


def test_diagnostics_all_pass():
    results = run_diagnostics()
    assert len(results) == 10
    assert all(passed for _, passed in results)
