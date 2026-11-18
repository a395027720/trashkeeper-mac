import os

import webview

from conf.setting import settings
from utilities.log import logger
from utilities.response import res200, res400, res500
from utilities.search import search_files

# 搜索范围预设
SCOPE_DISK = "/"

# API 类的方法被挂到 API 实例上调用，self 是 API 实例而非本类实例，
# 所以窗口引用放在模块级，不依赖 self。
_window = None


def _set_search_window(window):
    """绑定 pywebview 窗口，供目录选择和进度推送使用。"""
    global _window
    _window = window


def _report_progress(count):
    """把搜索进度推给前端。"""
    if _window is None:
        return
    try:
        _window.evaluate_js(f"window.onSearchProgress && window.onSearchProgress({count})")
    except Exception:  # noqa: BLE001 - 进度推送失败不影响搜索
        pass


class SearchAPI:
    """文件检索。"""

    name = "search"

    def find(self, keyword, root=SCOPE_DISK, limit=0, include_hidden=False):
        """在指定目录内按名称搜索文件。

        :param keyword: 名称关键字
        :param root: 搜索根目录，传 "/" 表示全盘
        :param limit: 最多返回条数，0 表示用配置里的默认值
        :param include_hidden: 是否包含隐藏项
        """
        max_items = int(limit) if limit else settings.search_limit
        try:
            result = search_files(
                root=root,
                keyword=keyword or "",
                limit=max_items,
                include_hidden=bool(include_hidden),
                time_limit=settings.search_time_limit,
                on_progress=_report_progress,
            )
        except NotADirectoryError as exc:
            return res400(str(exc))
        except PermissionError as exc:
            return res400(f"没有权限访问该目录: {exc}")
        except Exception as exc:  # noqa: BLE001 - 兜底，避免整个窗口崩掉
            logger.error(f"搜索失败: {exc}")
            return res500(f"搜索失败: {exc}")
        return res200(data=result)

    def pick_folder(self):
        """弹出系统目录选择框，返回用户选中的路径。"""
        if _window is None:
            return res400("窗口尚未就绪")
        try:
            result = _window.create_file_dialog(
                dialog_type=webview.FOLDER_DIALOG,
                allow_multiple=False,
            )
        except Exception as exc:  # noqa: BLE001 - 弹窗失败不应让接口崩掉
            logger.error(f"打开目录选择框失败: {exc}")
            return res500(f"打开目录选择框失败: {exc}")
        if not result:
            return res200(data={"path": ""})
        return res200(data={"path": result[0]})

    def home_dir(self):
        """返回用户主目录，供前端切换搜索范围。"""
        return res200(data={"path": os.path.expanduser("~")})
