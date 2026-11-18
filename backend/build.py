# -*- coding: utf-8 -*-
"""构建脚本。

用法：
    python build.py -t i   生成图标
    python build.py -t p   打出 macOS .app（dist/mac-release/废纸篓管家.app）
    python build.py -t z   打包成 zip
"""

import argparse
import os
import platform
import shutil
import sys
import subprocess
from pathlib import Path

APP_NAME = "废纸篓管家"
DIST_DIR = Path("./dist")


def run(cmd: str) -> None:
    print(f"→ {cmd}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        raise SystemExit(f"命令失败: {cmd}")


def build_icon():
    """生成 .icns 图标。"""
    iconset = Path("./assets/icon.iconset")
    if iconset.exists():
        shutil.rmtree(iconset)
    iconset.mkdir(parents=True, exist_ok=True)

    run(f"{sys.executable} assets/make_icon.py")
    source = Path("assets/icon_1024.png")

    for size in (16, 32, 128, 256, 512):
        run(f"sips -z {size} {size} {source} --out {iconset}/icon_{size}x{size}.png")
        run(
            f"sips -z {size * 2} {size * 2} {source} "
            f"--out {iconset}/icon_{size}x{size}@2x.png"
        )
    run(f"iconutil -c icns {iconset} -o assets/icon.icns")
    print(f"✓ 图标生成: assets/icon.icns")


def build_app():
    """用 PyInstaller 打出 .app。"""
    run(
        "./.venv/bin/pyinstaller --noconfirm --clean mac_main.spec "
        "--distpath dist/mac-release"
    )
    app = DIST_DIR / "mac-release" / f"{APP_NAME}.app"
    if not app.exists():
        raise SystemExit(f"未找到打包产物: {app}")
    size = sum(f.stat().st_size for f in app.rglob("*") if f.is_file())
    print(f"✓ 打包完成: {app}  ({size / 1024 / 1024:.1f} MB)")


def build_dmg():
    """打出 DMG 安装包。"""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from mac_dmg import build_dmg as make_dmg

    make_dmg()


def build_zip():
    """把 .app 压成 zip，便于分发。"""
    release = DIST_DIR / "mac-release"
    app = release / f"{APP_NAME}.app"
    if not app.exists():
        raise SystemExit("请先执行 python build.py -t p")
    archive = release / f"{APP_NAME}-mac.zip"
    if archive.exists():
        archive.unlink()
    run(f"cd {release} && zip -ry -9 {archive.name} '{APP_NAME}.app'")
    print(f"✓ 已压缩: {archive}")


def main():
    parser = argparse.ArgumentParser(description="构建废纸篓管家")
    parser.add_argument(
        "-t",
        "--type",
        default="p",
        help="i=图标 / p=打包 .app / d=打包 DMG / z=压缩",
    )
    args = parser.parse_args()

    if platform.system() != "Darwin":
        raise SystemExit("仅支持 macOS")

    if args.type == "i":
        build_icon()
    elif args.type == "p":
        build_app()
    elif args.type == "d":
        build_dmg()
    elif args.type == "z":
        build_zip()
    else:
        raise SystemExit("未知类型")


if __name__ == "__main__":
    main()
