# trashkeeper-mac

> macOS 废纸篓管家 —— 检索全盘文件、移到废纸篓、一键恢复，废纸篓自动按天清理。

A macOS desktop app that searches your whole disk, moves files to the Trash, and
restores them back — with the Trash cleaned automatically on a schedule.

![功能](https://img.shields.io/badge/macOS-10.13%2B-blue) ![架构](https://img.shields.io/badge/架构-Python%20%2B%20pywebview-green)

---

## 特性

| 功能 | 说明 |
|---|---|
| **全盘 / 指定目录检索** | 支持扫描整个磁盘、用户主目录，或用系统对话框任选一个文件夹 |
| **移到废纸篓** | 跨卷移动会自动落到对应卷的 `.Trashes`，与 Finder 行为一致 |
| **一键恢复** | 记住每个文件的原路径，点一下就放回原处；原位置被占用会自动改名 |
| **自动清理** | 默认保留 7 天，launchd 每天 10:17 自动清理过期内容（天数可在应用里改） |
| **保留 Finder 删除的文件** | 不是本工具删进废纸篓的，也能通过 Finder 的「放回原处」恢复 |

## 安装

```bash
npm install -g trashkeeper-mac
trashkeeper
```

安装脚本会把应用放进 `~/Applications/`，并注册每日自动清理的 launchd 任务。

> 需要 macOS 10.13 或更高版本。

## 使用

1. **文件检索** 页输入文件名关键字，选择搜索范围，点「搜索」
2. 勾选要处理的文件，点「移到废纸篓」
3. **废纸篓** 页能看到所有内容及其原位置，点「恢复到原位置」即可还原
4. 右上角可调整保留天数，或点「立即清理」马上清理过期内容

## 卸载

```bash
npm uninstall -g trashkeeper-mac
```

应用本体、launchd 任务都会被移除；配置与删除记录保留在
`~/Library/Application Support/TrashKeeper`，需要彻底清除请手动删掉该目录。

## 从源码构建

```bash
git clone https://github.com/fuck-baby/trashkeeper-mac.git
cd trashkeeper-mac/backend

python3 -m venv .venv
./.venv/bin/pip install pywebview pyinstaller
./.venv/bin/python build.py -t i   # 生成图标
./.venv/bin/python build.py -t p   # 打出 .app
bash ../scripts/install.sh          # 安装并注册自动清理
```

自测（不会碰你的真实数据，废纸篓被重定向到临时目录）：

```bash
./.venv/bin/python tests/test_trash.py
```

## 实现要点

- **界面**：`backend/web/index.html` 单文件，前端零构建步骤
- **后端**：`backend/api/` 下按功能分文件，API 按 `{类名}__{方法名}` 暴露给前端
- **废纸篓位置**：启动盘 `~/.Trash`，其他卷 `/Volumes/<卷名>/.Trashes/<uid>`
- **恢复记录**：删除时把「原路径 → 废纸篓路径」写进
  `~/Library/Application Support/TrashKeeper/records.json`，没有记录时回退到 Finder 的「放回原处」
- **搜索**：广度优先遍历，保证浅层目录（桌面、家目录）先被覆盖；单次搜索默认 120 秒上限

## License

MIT
