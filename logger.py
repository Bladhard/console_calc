"""Настройка логирования приложения в logs/smartcalc.log."""

import logging
from pathlib import Path


def get_logger() -> logging.Logger:
    """Возвращает единственный логгер приложения."""
    logger = logging.getLogger("smartcalc")
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        log_path = Path("logs/smartcalc.log")
        log_path.parent.mkdir(parents=True, exist_ok=True)
        handler = logging.FileHandler(log_path, encoding="utf-8")
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)s %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        logger.addHandler(handler)
        logger.propagate = False
    return logger
