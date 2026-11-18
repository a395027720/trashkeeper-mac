#!/bin/bash
# 安装废纸篓管家：把 .app 放进 ~/Applications，并注册每日自动清理。

set -e

APP_NAME="废纸篓管家"
LABEL="com.gaojianqiang.trashkeeper.cleanup"
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
BUILT_APP="$PROJECT_DIR/backend/dist/mac-release/$APP_NAME.app"
INSTALL_DIR="$HOME/Applications"
SUPPORT_DIR="$HOME/Library/Application Support/TrashKeeper"
AGENT_DIR="$HOME/Library/LaunchAgents"
PLIST="$AGENT_DIR/$LABEL.plist"

if [ ! -d "$BUILT_APP" ]; then
  echo "✗ 找不到打包产物：$BUILT_APP"
  echo "  请先执行：cd backend && .venv/bin/python build.py -t p"
  exit 1
fi

mkdir -p "$INSTALL_DIR" "$SUPPORT_DIR" "$AGENT_DIR"

echo "→ 安装应用到 $INSTALL_DIR"
rm -rf "$INSTALL_DIR/$APP_NAME.app"
cp -R "$BUILT_APP" "$INSTALL_DIR/$APP_NAME.app"

echo "→ 安装清理脚本"
cp "$PROJECT_DIR/scripts/cleanup.sh" "$SUPPORT_DIR/cleanup.sh"
chmod +x "$SUPPORT_DIR/cleanup.sh"

echo "→ 注册每日清理任务（launchd）"
cat > "$PLIST" <<PLIST_EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>$LABEL</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>$SUPPORT_DIR/cleanup.sh</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>10</integer>
        <key>Minute</key>
        <integer>17</integer>
    </dict>
    <key>RunAtLoad</key>
    <false/>
    <key>StandardOutPath</key>
    <string>$SUPPORT_DIR/launchd.log</string>
    <key>StandardErrorPath</key>
    <string>$SUPPORT_DIR/launchd.log</string>
</dict>
</plist>
PLIST_EOF

launchctl unload "$PLIST" 2>/dev/null || true
launchctl load "$PLIST"

echo ""
echo "✓ 安装完成"
echo "  应用位置：$INSTALL_DIR/$APP_NAME.app"
echo "  每日清理：10:17，保留天数可在应用内「废纸篓」页调整"
echo "  日志：$SUPPORT_DIR/launchd.log"
