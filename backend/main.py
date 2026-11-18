import os
import sys

import webview

from api import API
from api.search import SearchAPI, _set_search_window
from api.trash import TrashAPI
from utilities.log import logger

api = API()
api.add_apis(SearchAPI)
api.add_apis(TrashAPI)


def _prepare_workdir():
    """打包后把工作目录切到 bundle 内的资源根，保证 web/index.html 能相对定位。"""
    if not getattr(sys, "frozen", False):
        return
    base = getattr(sys, "_MEIPASS", None)
    if base and os.path.isdir(os.path.join(base, "web")):
        os.chdir(base)
        logger.info(f"工作目录切换到 {base}")


def create_window():
    """创建主窗口，并把窗口实例交给需要它的 API。"""
    window = webview.create_window(
        "废纸篓管家",
        url="web/index.html",
        js_api=api,
        width=1040,
        height=700,
        min_size=(880, 540),
    )
    _set_search_window(window)
    logger.info("窗口已创建")
    return window


def on_loaded(window):
    """窗口加载完成后的收尾动作。"""
    logger.info("应用已就绪")


def run_cleanup(days=0):
    """命令行模式：清理废纸篓里超过保留天数的条目，然后退出。"""
    from conf.setting import settings
    from utilities.trash import clean_trash

    retention = int(days) if days else settings.retention_days
    result = clean_trash(retention)
    freed_mb = result["freed"] / 1024 / 1024
    print(
        f"清理完成：删除 {result['removed']} 项，释放 {freed_mb:.1f} MB"
        f"（保留 {retention} 天）"
    )
    for failure in result["failed"]:
        print(f"  失败：{failure}")
    return 0


if __name__ == "__main__":
    if "--cleanup" in sys.argv:
        days = 0
        if "--days" in sys.argv:
            index = sys.argv.index("--days")
            if index + 1 < len(sys.argv):
                days = int(sys.argv[index + 1])
        sys.exit(run_cleanup(days))
    _prepare_workdir()
    window = create_window()
    webview.start(on_loaded, window, http_server=True)
