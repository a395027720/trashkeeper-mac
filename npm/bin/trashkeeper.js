#!/usr/bin/env node
/** 启动已安装的「废纸篓管家」应用。 */

const { execFile } = require("child_process");
const fs = require("fs");
const os = require("os");
const path = require("path");

const APP_NAME = "废纸篓管家.app";

function findApp() {
  const candidates = [
    path.join(os.homedir(), "Applications", APP_NAME),
    path.join("/Applications", APP_NAME),
  ];
  return candidates.find((item) => fs.existsSync(item));
}

const app = findApp();
if (!app) {
  console.error("没有找到「废纸篓管家」应用。");
  console.error("请重新安装：npm install -g trashkeeper-mac");
  process.exit(1);
}

execFile("open", [app], (error) => {
  if (error) {
    console.error(`启动失败：${error.message}`);
    process.exit(1);
  }
});
