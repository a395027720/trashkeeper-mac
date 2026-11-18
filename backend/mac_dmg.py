# -*- coding: utf-8 -*-
"""用原生 hdiutil 制作 DMG 安装包（不依赖 appdmg 等第三方工具）。

产物结构：把 .app 和「应用程序」软链放进镜像里，
用户双击 DMG 后把 app 拖进「应用程序」即可。
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

APP_NAME = "废纸篓管家"
VERSION = "0.1.0"
DIST_DIR = Path("./dist/mac-release")
APP_PATH = DIST_DIR / f"{APP_NAME}.app"
DMG_PATH = DIST_DIR / f"{APP_NAME}-{VERSION}.dmg"
VOLUME_NAME = f"{APP_NAME} {VERSION}"


def _run(cmd: list) -> None:
    print(f"→ {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise SystemExit(f"命令失败：{result.stderr.strip()}")


def _set_finder_layout(mount_point: str) -> None:
    """在 Finder 里摆放图标位置，让 DMG 打开时排版好看。"""
    script = f'''
    tell application "Finder"
        tell disk "{VOLUME_NAME}"
            open
            set current view of container window to icon view
            set toolbar visible of container window to false
            set statusbar visible of container window to false
            set the bounds of container window to {{200, 150, 760, 460}}
            set position of item "{APP_NAME}.app" of container window to {{170, 150}}
            set position of item "Applications" of container window to {{490, 150}}
            close
            open
            update without registering applications
            delay 1
        end tell
    end tell
    '''
    try:
        subprocess.run(["osascript", "-e", script], capture_output=True, timeout=30)
    except (subprocess.SubprocessError, OSError):
        # 排版失败不影响 DMG 本身
        pass


def build_dmg() -> Path:
    """生成 DMG，返回文件路径。"""
    if not APP_PATH.exists():
        raise SystemExit(f"找不到应用：{APP_PATH}（先执行 build.py -t p）")

    staging = Path(tempfile.mkdtemp(prefix="trashkeeper_dmg_"))
    try:
        print(f"→ 准备镜像内容")
        shutil.copytree(APP_PATH, staging / f"{APP_NAME}.app", symlinks=True)
        (staging / "Applications").symlink_to("/Applications")

        if DMG_PATH.exists():
            DMG_PATH.unlink()

        print(f"→ 制作 DMG：{DMG_PATH.name}")
        _run(
            [
                "hdiutil", "create",
                "-srcfolder", str(staging),
                "-volname", VOLUME_NAME,
                "-fs", "HFS+",
                "-format", "UDZO",
                "-ov",
                str(DMG_PATH),
            ]
        )

        print("→ 设置 Finder 图标布局")
        mount_point = tempfile.mkdtemp(prefix="trashkeeper_mount_")
        _run(["hdiutil", "attach", str(DMG_PATH), "-nobrowse", "-mountpoint", mount_point])
        try:
            _set_finder_layout(mount_point)
        finally:
            _run(["hdiutil", "detach", mount_point])
            shutil.rmtree(mount_point, ignore_errors=True)
    finally:
        shutil.rmtree(staging, ignore_errors=True)

    size = DMG_PATH.stat().st_size / 1024 / 1024
    print(f"✓ DMG 生成完成：{DMG_PATH}（{size:.1f} MB）")
    return DMG_PATH


if __name__ == "__main__":
    build_dmg()
