import json
from pathlib import Path

CONFIG_DIR = Path.home() / "Library" / "Application Support" / "TrashKeeper"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULTS = {
    "retention_days": 7,
    "search_limit": 500,
    "search_time_limit": 120,
}


class Settings:
    """运行时配置，落盘到 config.json。"""

    def __init__(self):
        self._data = self._load()

    def _load(self) -> dict:
        data = dict(DEFAULTS)
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as handle:
                saved = json.load(handle)
            if isinstance(saved, dict):
                data.update(saved)
        except (OSError, ValueError):
            pass
        return data

    def _save(self) -> None:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, "w", encoding="utf-8") as handle:
            json.dump(self._data, handle, ensure_ascii=False, indent=2)

    def get(self, key, default=None):
        return self._data.get(key, default)

    def set(self, key, value) -> None:
        self._data[key] = value
        self._save()

    @property
    def retention_days(self) -> int:
        return int(self._data.get("retention_days", 7))

    @property
    def search_limit(self) -> int:
        return int(self._data.get("search_limit", 500))

    @property
    def search_time_limit(self) -> int:
        return int(self._data.get("search_time_limit", 120))


settings = Settings()
