from conf.setting import settings
from utilities.log import logger
from utilities.response import res200, res400, res500
from utilities.trash import (
    clean_trash,
    list_trash,
    move_to_trash,
    restore_from_trash,
)


class TrashAPI:
    """废纸篓操作。"""

    name = "trash"

    def list_items(self):
        """列出废纸篓中的所有条目。"""
        try:
            items = list_trash()
        except Exception as exc:  # noqa: BLE001 - 兜底
            logger.error(f"读取废纸篓失败: {exc}")
            return res500(f"读取废纸篓失败: {exc}")
        return res200(data={"items": items})

    def remove(self, paths):
        """把选中的文件或目录移到废纸篓。

        :param paths: 路径列表
        """
        if not isinstance(paths, list) or not paths:
            return res400("请先选择要删除的项目")
        succeeded, failed = [], []
        for path in paths:
            try:
                result = move_to_trash(path)
                succeeded.append(result)
            except Exception as exc:  # noqa: BLE001 - 单个失败不影响其他
                logger.error(f"移到废纸篓失败 {path}: {exc}")
                failed.append({"path": path, "error": str(exc)})
        return res200(data={"succeeded": succeeded, "failed": failed})

    def restore(self, path):
        """把废纸篓里的文件放回原位置。"""
        if not path:
            return res400("请先选择要恢复的项目")
        try:
            result = restore_from_trash(path)
        except FileNotFoundError as exc:
            return res400(str(exc))
        except Exception as exc:  # noqa: BLE001 - 兜底
            logger.error(f"恢复失败 {path}: {exc}")
            return res500(f"恢复失败: {exc}")
        if not result.get("restored"):
            return res400(result.get("message", "恢复失败"))
        return res200(data=result)

    def clean(self, days=0):
        """清理废纸篓里超过保留天数的条目。"""
        retention = int(days) if days else settings.retention_days
        try:
            result = clean_trash(retention)
        except ValueError as exc:
            return res400(str(exc))
        except Exception as exc:  # noqa: BLE001 - 兜底
            logger.error(f"清理废纸篓失败: {exc}")
            return res500(f"清理废纸篓失败: {exc}")
        return res200(data=result)

    def set_retention_days(self, days):
        """设置废纸篓自动清理的保留天数。"""
        try:
            value = int(days)
        except (TypeError, ValueError):
            return res400("保留天数必须是数字")
        if value < 1:
            return res400("保留天数至少为 1")
        settings.set("retention_days", value)
        return res200(data={"retention_days": value})
