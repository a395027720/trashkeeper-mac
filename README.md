# trashkeeper-mac

> macOS 废纸篓管家 —— 检索全盘文件、移到废纸篓、一键恢复，废纸篓自动按天清理。

一个 macOS 桌面应用：搜索硬盘上的任何文件，删进废纸篓随时能放回原处，废纸篓里过期的东西会自动清理。

界面是原生 WebView（Python + pywebview），无 Electron，体积 23MB。

---

## 功能

| 功能 | 说明 |
|---|---|
| **全盘 / 指定目录检索** | 扫描整个磁盘、用户主目录，或用系统对话框任选一个文件夹 |
| **移到废纸篓** | 跨卷移动自动落到对应卷的 `.Trashes`，与 Finder 行为一致 |
| **一键恢复** | 记住每个文件的原路径，点一下放回原处；原位置被占用会自动改名 |
| **自动清理** | 默认保留 7 天，launchd 每天 10:17 自动清理过期内容（天数可在应用里改） |
| **兼容 Finder 删除** | 不是本工具删进废纸篓的，也能通过 Finder 的「放回原处」恢复 |

## 安装

```bash
npm install -g trashkeeper-mac
trashkeeper
```

安装脚本会把 DMG 里的应用装进 `~/Applications/`，并注册每日自动清理的 launchd 任务。

也可以直接下载 DMG 手动安装（把 app 拖进「应用程序」）：

```bash
npm pack trashkeeper-mac && open trashkeeper-mac-0.1.0.tgz
```

> 需要 macOS 10.13 或更高版本。
>
> 应用未做 Apple 公证（notarization），首次打开若提示「无法验证开发者」，
> 请在弹窗里选「仍要打开」，或在「系统设置 → 隐私与安全性」里点「仍要打开」。

## 使用

1. **文件检索** 页输入文件名关键字，选择搜索范围（全盘 / 用户目录 / 自选文件夹），点「搜索」
2. 勾选要处理的文件，点「移到废纸篓」
3. **废纸篓** 页能看到所有内容及其原位置，点「恢复到原位置」即可还原
4. 右上角可调整保留天数，或点「立即清理」马上清理过期内容

## 自动清理怎么工作

安装时注册了一个 launchd 任务：

```
~/Library/LaunchAgents/com.gaojianqiang.trashkeeper.cleanup.plist
```

每天 10:17 执行一次，删除废纸篓里修改时间超过保留天数的条目（默认 7 天），
覆盖启动盘 `~/.Trash` 和各外接卷的 `.Trashes/<uid>`。

- 保留天数在应用「废纸篓」页右上角可改，落盘在
  `~/Library/Application Support/TrashKeeper/config.json`
- 日志：`~/Library/Application Support/TrashKeeper/launchd.log`
- 不想自动清理：`bash scripts/uninstall.sh`（会一并移除应用）

## 从源码构建

```bash
git clone https://github.com/a395027720/trashkeeper-mac.git
cd trashkeeper-mac/backend

python3 -m venv .venv
./.venv/bin/pip install pywebview pyinstaller pillow
./.venv/bin/python build.py -t i   # 生成图标
./.venv/bin/python build.py -t p   # 打出 .app
./.venv/bin/python build.py -t d   # 打成 DMG 安装包
bash ../scripts/install.sh          # 安装并注册自动清理
```

自测（废纸篓被重定向到临时目录，不会碰你的真实数据）：

```bash
./.venv/bin/python tests/test_trash.py
```

打新 tag 会自动构建并发布到 npm（需先在仓库 Settings → Secrets 里配置 `NPM_TOKEN`）：

```bash
git tag v0.2.0 && git push origin v0.2.0
```

## 项目结构

```
backend/
  main.py           入口：注册 API、创建 pywebview 窗口、--cleanup 命令行模式
  api/              每个功能一个 API 类，公开方法即 action
    search.py       文件检索、目录选择、搜索进度推送
    trash.py        废纸篓列表、删除、恢复、清理、保留天数
  utilities/
    trash.py        废纸篓核心：跨卷移动、原位置记录、按天清理
    search.py       广度优先遍历，单目录条目上限与超时保护
    response.py     res200 / res400 / res500，统一 JSON 响应
    log.py          控制台 + 文件双日志
  conf/setting.py   运行时配置（保留天数、搜索上限），落盘 config.json
  web/index.html    前端单文件，零构建步骤
  assets/make_icon.py  用 Pillow 画图标
  mac_main.spec     PyInstaller 打包配置
  mac_dmg.py        原生 hdiutil 制作 DMG
npm/                npm 分发包：package.json、postinstall 安装脚本、vendor 里的 DMG
scripts/            install.sh / uninstall.sh / cleanup.sh
```

### 几个实现要点

- **API 寻址**：`{类名}__{方法名}`，前端用 `window.pywebview.api.search__find(...)` 调用，
  返回值是 JSON 字符串
- **废纸篓位置**：启动盘 `~/.Trash`，其他卷 `/Volumes/<卷名>/.Trashes/<uid>`
- **恢复记录**：删除时把「原路径 → 废纸篓路径」写进
  `~/Library/Application Support/TrashKeeper/records.json`；没有记录时回退到
  Finder 的「放回原处」（路径通过 `osascript` 的 argv 传入，不拼进脚本，避免注入）
- **搜索策略**：广度优先遍历，保证浅层目录（桌面、家目录）先被覆盖；
  深度优先会一头钻进某个大目录深处，全盘搜索几乎出不来结果

## License

MIT
