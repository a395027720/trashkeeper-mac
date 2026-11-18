#!/bin/bash
# 废纸篓定时清理：由 launchd 每天调用一次。
# 会找到应用本体并以 --cleanup 模式运行。

set -u

APP_NAME="废纸篓管家"
SEARCH_PATHS=(
  "$HOME/Applications/$APP_NAME.app"
  "/Applications/$APP_NAME.app"
  "$HOME/.local/share/trashkeeper/$APP_NAME.app"
)

LOG_DIR="$HOME/Library/Application Support/TrashKeeper"
mkdir -p "$LOG_DIR"

for app in "${SEARCH_PATHS[@]}"; do
  if [ -x "$app/Contents/MacOS/TrashKeeper" ]; then
    "$app/Contents/MacOS/TrashKeeper" --cleanup >> "$LOG_DIR/cleanup.log" 2>&1
    exit $?
  fi
done

echo "$(date '+%Y-%m-%d %H:%M:%S') 未找到 $APP_NAME.app，跳过清理" >> "$LOG_DIR/cleanup.log"
exit 0
