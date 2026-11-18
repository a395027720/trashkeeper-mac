"""废纸篓操作：移到废纸篓、从废纸篓恢复、列出废纸篓、按天数清理。

macOS 的废纸篓位置规则：
- 启动盘：~/.Trash
- 其他卷：/Volumes/<卷名>/.Trashes/<uid>

为了能精确"放回原处"，删除时会把「原路径 → 废纸篓路径」记到
records.json；不是本工具删进去的文件没有记录，恢复时走 Finder 的
"放回原处"兜底。
"""

import json
import os
import shutil
import subprocess
import time
from pathlib import Path

APP_SUPPORT = Path.home() / "Library" / "Application Support" / "TrashKeeper"
RECORDS_FILE = APP_SUPPORT / "records.json"
TRASH_UID = os.getuid()

# 测试时可把废纸篓重定向到临时目录，避免动到用户真实数据
_TRASH_DIR_OVERRIDE = []


def set_trash_dirs(paths) -> None:
    """把废纸篓目录重定向到指定位置（测试用）。传空列表恢复默认。"""
    global _TRASH_DIR_OVERRIDE
    _TRASH_DIR_OVERRIDE = [Path(p) for p in paths]


def set_records_file(path) -> None:
    """把删除记录的存放位置重定向到指定文件（测试用）。"""
    global RECORDS_FILE
    RECORDS_FILE = Path(path)

# 路径通过 argv 传给 osascript，不拼接进脚本文本，避免 AppleScript 注入
FINDER_PUT_BACK_SCRIPT = """
on run argv
    set thePath to item 1 of argv
    tell application "Finder"
        set theItem to POSIX file thePath as alias
        try
            put back theItem
            return "ok"
        on error errMsg
            return "error: " & errMsg
        end try
    end tell
end run
"""


def _load_records() -> dict:
    """读取删除记录，损坏时返回空字典。"""
    try:
        with open(RECORDS_FILE, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def _save_records(records: dict) -> None:
    """写入删除记录。"""
    APP_SUPPORT.mkdir(parents=True, exist_ok=True)
    with open(RECORDS_FILE, "w", encoding="utf-8") as handle:
        json.dump(records, handle, ensure_ascii=False, indent=2)


def trash_dir_for(path: str) -> Path:
    """返回该路径所属卷的废纸篓目录。"""
    if _TRASH_DIR_OVERRIDE:
        return _TRASH_DIR_OVERRIDE[0]
    target = Path(path)
    try:
        same_volume = os.stat(target).st_dev == os.stat("/").st_dev
    except OSError:
        same_volume = True
    if same_volume:
        return Path.home() / ".Trash"
    return Path(target.anchor) / ".Trashes" / str(TRASH_UID)


def _unique_path(directory: Path, name: str) -> Path:
    """在目录内生成不重名的目标路径，重名时追加序号。"""
    candidate = directory / name
    if not candidate.exists():
        return candidate
    stem, suffix = Path(name).stem, Path(name).suffix
    index = 1
    while True:
        candidate = directory / f"{stem} {index}{suffix}"
        if not candidate.exists():
            return candidate
        index += 1


def move_to_trash(path: str) -> dict:
    """把文件或目录移到废纸篓，返回移动结果。"""
    source = Path(path).expanduser()
    if not source.exists():
        raise FileNotFoundError(f"路径不存在: {path}")
    if source.is_dir() and not os.access(source, os.W_OK):
        raise PermissionError(f"没有写入权限: {path}")

    trash_dir = trash_dir_for(str(source))
    trash_dir.mkdir(parents=True, exist_ok=True)
    destination = _unique_path(trash_dir, source.name)

    try:
        shutil.move(str(source), str(destination))
    except (OSError, shutil.Error) as exc:
        raise RuntimeError(f"移动到废纸篓失败: {exc}") from exc

    records = _load_records()
    records[str(destination)] = {
        "original": str(source),
        "time": time.time(),
        "volume": str(Path(source.anchor)),
    }
    _save_records(records)
    return {"trash_path": str(destination), "original": str(source)}


def _finder_put_back(trash_path: str) -> tuple:
    """让 Finder 执行"放回原处"。返回 (是否成功, 说明)。"""
    try:
        result = subprocess.run(
            ["osascript", "-e", FINDER_PUT_BACK_SCRIPT, trash_path],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (subprocess.SubprocessError, OSError) as exc:
        return False, f"调用 Finder 失败: {exc}"
    output = result.stdout.strip()
    if output == "ok":
        return True, "已放回原处"
    return False, output or "Finder 未能恢复该文件"


def restore_from_trash(trash_path: str) -> dict:
    """把废纸篓里的文件放回原位置。"""
    source = Path(trash_path)
    if not source.exists():
        raise FileNotFoundError(f"废纸篓中找不到: {trash_path}")

    records = _load_records()
    record = records.get(str(source))
    if not record:
        ok, message = _finder_put_back(str(source))
        if ok:
            records.pop(str(source), None)
            _save_records(records)
        return {"restored": ok, "message": message, "via": "finder"}

    original = Path(record["original"])
    destination = original
    if destination.exists():
        destination = _unique_path(original.parent, original.name)
    original.parent.mkdir(parents=True, exist_ok=True)

    try:
        shutil.move(str(source), str(destination))
    except (OSError, shutil.Error) as exc:
        raise RuntimeError(f"恢复失败: {exc}") from exc

    records.pop(str(source), None)
    _save_records(records)
    return {
        "restored": True,
        "message": f"已恢复到 {destination}",
        "via": "record",
        "path": str(destination),
    }


def _iter_trash_dirs():
    """列出所有可访问的废纸篓目录。"""
    if _TRASH_DIR_OVERRIDE:
        yield from _TRASH_DIR_OVERRIDE
        return
    yield Path.home() / ".Trash"
    volumes_dir = Path("/Volumes")
    if not volumes_dir.is_dir():
        return
    for volume in volumes_dir.iterdir():
        if not volume.is_dir():
            continue
        candidate = volume / ".Trashes" / str(TRASH_UID)
        if candidate.is_dir():
            yield candidate


def list_trash() -> list:
    """列出所有废纸篓里的条目，附带原位置（如果有记录）。"""
    records = _load_records()
    items = []
    for trash_dir in _iter_trash_dirs():
        try:
            entries = list(trash_dir.iterdir())
        except OSError:
            continue
        for entry in entries:
            if entry.name.startswith("."):
                continue
            try:
                stat = entry.stat()
            except OSError:
                continue
            record = records.get(str(entry))
            items.append(
                {
                    "name": entry.name,
                    "path": str(entry),
                    "size": stat.st_size,
                    "is_dir": entry.is_dir(),
                    "modified": stat.st_mtime,
                    "original": record["original"] if record else "",
                    "volume": trash_dir.parent.name if trash_dir.name == ".Trashes" else "启动盘",
                }
            )
    items.sort(key=lambda item: item["modified"], reverse=True)
    return items


def _directory_size(path: Path) -> int:
    """计算文件或目录占用的字节数。"""
    if path.is_file() and not path.is_symlink():
        try:
            return path.stat().st_size
        except OSError:
            return 0
    total = 0
    for root, _dirs, files in os.walk(path):
        for name in files:
            try:
                total += (Path(root) / name).lstat().st_size
            except OSError:
                continue
    return total


def clean_trash(days: int = 7) -> dict:
    """清理废纸篓里超过指定天数的条目。"""
    if days < 1:
        raise ValueError("保留天数至少为 1")
    cutoff = time.time() - days * 86400
    removed, freed, failed = 0, 0, []

    for trash_dir in _iter_trash_dirs():
        try:
            entries = list(trash_dir.iterdir())
        except OSError:
            continue
        for entry in entries:
            if entry.name.startswith("."):
                continue
            try:
                stat = entry.stat()
            except OSError:
                continue
            if stat.st_mtime >= cutoff:
                continue
            size = _directory_size(entry)
            try:
                if entry.is_dir() and not entry.is_symlink():
                    shutil.rmtree(entry)
                else:
                    entry.unlink()
            except OSError as exc:
                failed.append(f"{entry.name}: {exc}")
                continue
            removed += 1
            freed += size

    records = _load_records()
    for key in list(records.keys()):
        if not Path(key).exists():
            records.pop(key, None)
    _save_records(records)

    return {"removed": removed, "freed": freed, "failed": failed}
