/**
 * postinstall：把应用装进 ~/Applications，并注册每日自动清理的 launchd 任务。
 *
 * 任何一步失败都只提示、不抛错 —— 不让 npm 安装整体失败。
 */

const { execFileSync } = require("child_process");
const fs = require("fs");
const os = require("os");
const path = require("path");

const APP_NAME = "废纸篓管家.app";
const LABEL = "com.gaojianqiang.trashkeeper.cleanup";
const INSTALL_DIR = path.join(os.homedir(), "Applications");
const SUPPORT_DIR = path.join(
  os.homedir(),
  "Library",
  "Application Support",
  "TrashKeeper"
);
const AGENT_DIR = path.join(os.homedir(), "Library", "LaunchAgents");
const PLIST_PATH = path.join(AGENT_DIR, `${LABEL}.plist`);

function log(message) {
  console.log(`[trashkeeper-mac] ${message}`);
}

function copyDir(from, to) {
  fs.rmSync(to, { recursive: true, force: true });
  fs.cpSync(from, to, { recursive: true });
}

function installApp() {
  const source = path.join(__dirname, "..", "vendor", APP_NAME);
  if (!fs.existsSync(source)) {
    throw new Error(`安装包内缺少 ${APP_NAME}`);
  }
  fs.mkdirSync(INSTALL_DIR, { recursive: true });
  copyDir(source, path.join(INSTALL_DIR, APP_NAME));
  log(`应用已安装到 ${INSTALL_DIR}`);
}

function installCleanupScript() {
  const source = path.join(__dirname, "..", "scripts", "cleanup.sh");
  if (!fs.existsSync(source)) {
    throw new Error("安装包内缺少 scripts/cleanup.sh");
  }
  fs.mkdirSync(SUPPORT_DIR, { recursive: true });
  const target = path.join(SUPPORT_DIR, "cleanup.sh");
  fs.copyFileSync(source, target);
  fs.chmodSync(target, 0o755);
  log("清理脚本已就位");
}

function registerLaunchAgent() {
  fs.mkdirSync(AGENT_DIR, { recursive: true });
  const plist = `<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>${LABEL}</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>${path.join(SUPPORT_DIR, "cleanup.sh")}</string>
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
    <string>${path.join(SUPPORT_DIR, "launchd.log")}</string>
    <key>StandardErrorPath</key>
    <string>${path.join(SUPPORT_DIR, "launchd.log")}</string>
</dict>
</plist>
`;
  fs.writeFileSync(PLIST_PATH, plist, "utf-8");
  try {
    execFileSync("launchctl", ["unload", PLIST_PATH], { stdio: "ignore" });
  } catch (error) {
    // 首次安装时本来就没加载过，忽略
  }
  execFileSync("launchctl", ["load", PLIST_PATH]);
  log("已注册每日 10:17 的废纸篓自动清理");
}

function main() {
  try {
    installApp();
    installCleanupScript();
    registerLaunchAgent();
    log("安装完成，运行 `trashkeeper` 启动应用");
  } catch (error) {
    log(`安装未完全成功：${error.message}`);
    log("可以手动把应用拖进「应用程序」文件夹使用");
  }
}

main();
