"""按名称递归检索文件。

只做只读遍历：不跟随符号链接，遇到无权限的目录直接跳过。
"""

import os
import time
from collections import deque
from pathlib import Path

from utilities.kinds import classify

# 默认跳过的目录。/Volumes 不在其中 —— 外接盘上的文件同样是用户要找的。
# 隐藏目录（含各卷的 .Trashes、.Spotlight 等）由 include_hidden 控制，默认已跳过。
DEFAULT_SKIP_DIRS = {
    "/System",
    "/dev",
    "/private/var/vm",
    "/Library/Developer",
}

# 单个目录下的条目数上限，防止卡在超大目录上
MAX_ENTRIES_PER_DIR = 5000


def _is_skipped(path: str, skip_dirs) -> bool:
    """判断路径是否在跳过列表里。"""
    for skip in skip_dirs:
        if path == skip or path.startswith(skip + "/"):
            return True
    return False


def _describe(entry: os.DirEntry) -> dict:
    """把目录条目转成可展示的信息。"""
    try:
        stat = entry.stat(follow_symlinks=False)
        size = stat.st_size
        modified = stat.st_mtime
    except OSError:
        size, modified = 0, time.time()
    try:
        is_dir = entry.is_dir(follow_symlinks=False)
    except OSError:
        is_dir = False
    return {
        "name": entry.name,
        "path": entry.path,
        "size": size,
        "modified": modified,
        "is_dir": is_dir,
        "kind": classify(entry.path, is_dir),
    }


def list_directory(path: str, include_hidden: bool = False) -> list:
    """列出某个目录下的直接子项（不递归），供前端树形浏览使用。"""
    target = Path(path).expanduser()
    if not target.is_dir():
        raise NotADirectoryError(f"不是有效目录: {path}")
    items = []
    with os.scandir(target) as iterator:
        for entry in iterator:
            if not include_hidden and entry.name.startswith("."):
                continue
            items.append(_describe(entry))
    items.sort(key=lambda item: (not item["is_dir"], item["name"].lower()))
    return items


def search_files(
    root: str,
    keyword: str,
    limit: int = 500,
    skip_dirs=None,
    include_hidden: bool = False,
    time_limit: float = 120.0,
    on_progress=None,
) -> dict:
    """在 root 下递归查找名称包含 keyword 的条目。

    :param root: 起始目录
    :param keyword: 名称关键字，空字符串表示列出全部条目
    :param limit: 最多返回多少条
    :param skip_dirs: 要跳过的目录前缀集合
    :param include_hidden: 是否包含以 . 开头的隐藏项
    :param time_limit: 最长扫描秒数，超时后带着已有结果返回
    :param on_progress: 进度回调，参数为已找到的条数
    :return: {"items": [...], "truncated": bool, "elapsed": 秒}
    """
    start = Path(root).expanduser()
    if not start.is_dir():
        raise NotADirectoryError(f"不是有效目录: {root}")

    skip = DEFAULT_SKIP_DIRS if skip_dirs is None else set(skip_dirs)
    needle = keyword.strip().lower()
    results = []
    # 广度优先：逐层推进，保证浅层常见位置（家目录、桌面）先被覆盖，
    # 否则深度优先会一头钻进某个大目录深处，全盘搜索几乎出不来结果
    queue = deque([str(start)])
    began = time.time()
    truncated = False
    last_report = 0.0

    while queue:
        if len(results) >= limit:
            truncated = True
            break
        if time.time() - began > time_limit:
            truncated = True
            break
        current = queue.popleft()
        if _is_skipped(current, skip):
            continue
        try:
            with os.scandir(current) as iterator:
                for index, entry in enumerate(iterator):
                    if index >= MAX_ENTRIES_PER_DIR:
                        break
                    if not include_hidden and entry.name.startswith("."):
                        continue
                    if entry.is_dir(follow_symlinks=False):
                        queue.append(entry.path)
                    if needle and needle not in entry.name.lower():
                        continue
                    results.append(_describe(entry))
                    if len(results) >= limit:
                        break
        except (OSError, PermissionError):
            continue
        if on_progress and time.time() - last_report > 0.5:
            last_report = time.time()
            on_progress(len(results))

    if on_progress:
        on_progress(len(results))
    results.sort(key=lambda item: item["modified"], reverse=True)
    return {
        "items": results,
        "truncated": truncated,
        "elapsed": round(time.time() - began, 2),
    }
