#!/bin/bash
# 卸载废纸篓管家：移除应用、清理脚本和 launchd 任务。

set -u

APP_NAME="废纸篓管家"
LABEL="com.gaojianqiang.trashkeeper.cleanup"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
SUPPORT_DIR="$HOME/Library/Application Support/TrashKeeper"

echo "→ 注销 launchd 任务"
launchctl unload "$PLIST" 2>/dev/null || true
rm -f "$PLIST"

echo "→ 移除应用"
rm -rf "$HOME/Applications/$APP_NAME.app" "/Applications/$APP_NAME.app"

echo "→ 移除清理脚本"
rm -f "$SUPPORT_DIR/cleanup.sh"

echo ""
echo "✓ 已卸载"
echo "  配置与删除记录仍保留在：$SUPPORT_DIR"
echo "  （需要彻底清除请手动删除该目录）"
