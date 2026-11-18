import logging
import sys
from pathlib import Path

LOG_DIR = Path.home() / "Library" / "Application Support" / "TrashKeeper"


def _build_logger() -> logging.Logger:
    """建立日志器：控制台 + 文件各一份。"""
    logger = logging.getLogger("trashkeeper")
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)
    logger.addHandler(console)

    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(LOG_DIR / "app.log", encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except OSError:
        pass
    return logger


logger = _build_logger()
