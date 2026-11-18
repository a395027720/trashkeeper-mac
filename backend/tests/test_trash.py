# -*- coding: utf-8 -*-
"""核心逻辑自测：搜索、移到废纸篓、恢复、清理。

只在本机临时目录里造测试文件，不会碰用户的真实数据。
"""

import shutil
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utilities.search import search_files
from utilities.trash import (
    clean_trash,
    list_trash,
    move_to_trash,
    restore_from_trash,
    set_records_file,
    set_trash_dirs,
)

PASSED = []
FAILED = []


def check(name, condition, detail=""):
    if condition:
        PASSED.append(name)
        print(f"  ✓ {name}")
    else:
        FAILED.append(f"{name} {detail}")
        print(f"  ✗ {name} {detail}")


def test_search(root):
    print("\n[搜索]")
    (root / "目标文件.txt").write_text("hello", encoding="utf-8")
    (root / "sub").mkdir(exist_ok=True)
    (root / "sub" / "另一个目标.dat").write_text("x" * 100, encoding="utf-8")

    result = search_files(str(root), "目标")
    names = sorted(item["name"] for item in result["items"])
    check("按名称匹配到文件", "目标文件.txt" in names, str(names))
    check("递归进入子目录", "另一个目标.dat" in names, str(names))

    empty = search_files(str(root), "不存在的关键字zzz")
    check("无匹配时返回空列表", empty["items"] == [])

    hit = search_files(str(root), "目标文件")
    check("返回大小", hit["items"][0]["size"] == 5, str(hit["items"][0]["size"]))


def test_trash_roundtrip(root):
    print("\n[移到废纸篓 + 恢复]")
    target = root / "待删除.txt"
    target.write_text("content", encoding="utf-8")

    result = move_to_trash(str(target))
    trash_path = result["trash_path"]
    check("原文件已不在原位", not target.exists())
    check("文件出现在废纸篓", Path(trash_path).exists(), trash_path)

    items = list_trash()
    check("废纸篓列表包含该文件", any(i["path"] == trash_path for i in items))
    entry = next((i for i in items if i["path"] == trash_path), None)
    check("记录了原位置", entry and entry["original"] == str(target), str(entry))

    restored = restore_from_trash(trash_path)
    check("恢复成功", restored["restored"], str(restored))
    check("文件回到原位且内容不变", target.exists() and target.read_text(encoding="utf-8") == "content")


def test_trash_collision(root):
    print("\n[重名处理]")
    dir_a = root / "dir_a"
    dir_b = root / "dir_b"
    dir_a.mkdir(exist_ok=True)
    dir_b.mkdir(exist_ok=True)
    first = dir_a / "同名.txt"
    second = dir_b / "同名.txt"
    first.write_text("first", encoding="utf-8")
    second.write_text("second", encoding="utf-8")

    r1 = move_to_trash(str(first))
    r2 = move_to_trash(str(second))
    check("两次移动到不同路径", r1["trash_path"] != r2["trash_path"], r2["trash_path"])
    check("第二个文件带序号", " 1" in Path(r2["trash_path"]).name, r2["trash_path"])
    check("两个文件内容各自独立",
          Path(r1["trash_path"]).read_text(encoding="utf-8") == "first"
          and Path(r2["trash_path"]).read_text(encoding="utf-8") == "second")


def test_clean(root):
    print("\n[按天数清理]")
    old = root / "很久以前.txt"
    old.write_text("old", encoding="utf-8")
    result = move_to_trash(str(old))
    trash_file = Path(result["trash_path"])
    ancient = time.time() - 30 * 86400
    import os
    os.utime(trash_file, (ancient, ancient))

    outcome = clean_trash(days=7)
    check("清掉了超过 7 天的条目", not trash_file.exists(), str(outcome))
    check("清掉了至少一项", outcome["removed"] >= 1, str(outcome))


def main():
    root = Path(tempfile.mkdtemp(prefix="trashkeeper_test_"))
    fake_trash = root / "_trash"
    fake_trash.mkdir()
    # 把废纸篓和记录文件都隔离到临时目录，绝不碰用户真实的 ~/.Trash
    set_trash_dirs([fake_trash])
    set_records_file(root / "_records.json")
    try:
        test_search(root)
        test_trash_roundtrip(root)
        test_trash_collision(root)
        test_clean(root)
    finally:
        set_trash_dirs([])
        shutil.rmtree(root, ignore_errors=True)

    print(f"\n通过 {len(PASSED)} 项，失败 {len(FAILED)} 项")
    for item in FAILED:
        print(f"  失败: {item}")
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())
