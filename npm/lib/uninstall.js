/**
 * uninstall：移除 launchd 任务和应用本体。
 * 配置与删除记录保留在 ~/Library/Application Support/TrashKeeper。
 */

const { execFileSync } = require("child_process");
const fs = require("fs");
const os = require("os");
const path = require("path");

const APP_NAME = "废纸篓管家.app";
const LABEL = "com.gaojianqiang.trashkeeper.cleanup";
const PLIST_PATH = path.join(
  os.homedir(),
  "Library",
  "LaunchAgents",
  `${LABEL}.plist`
);
const SUPPORT_DIR = path.join(
  os.homedir(),
  "Library",
  "Application Support",
  "TrashKeeper"
);

function log(message) {
  console.log(`[trashkeeper-mac] ${message}`);
}

try {
  if (fs.existsSync(PLIST_PATH)) {
    try {
      execFileSync("launchctl", ["unload", PLIST_PATH], { stdio: "ignore" });
    } catch (error) {
      // 本来就没加载
    }
    fs.rmSync(PLIST_PATH, { force: true });
    log("已注销每日清理任务");
  }
  fs.rmSync(path.join(os.homedir(), "Applications", APP_NAME), {
    recursive: true,
    force: true,
  });
  fs.rmSync(path.join("/Applications", APP_NAME), { recursive: true, force: true });
  fs.rmSync(path.join(SUPPORT_DIR, "cleanup.sh"), { force: true });
  log("已移除应用本体");
  log(`配置与删除记录仍保留在 ${SUPPORT_DIR}`);
} catch (error) {
  log(`卸载时出现问题：${error.message}`);
}
