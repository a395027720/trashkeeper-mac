from utilities.log import logger
from utilities.response import res200, res400, res500


class API:
    """API 注册中心：各 API 类的公开方法按 {类名}__{方法名} 暴露给前端。"""

    def __init__(self):
        pass

    def add_apis(self, APIClass):
        for method_name in dir(APIClass):
            method = getattr(APIClass, method_name)
            if callable(method) and not method_name.startswith("_"):
                setattr(API, f"{APIClass.name}__{method_name}", method)

    def get_system_info(self):
        """返回应用版本和配置摘要。"""
        from conf.setting import settings

        return res200(
            data={
                "version": "0.1.0",
                "retention_days": settings.retention_days,
                "search_limit": settings.search_limit,
            }
        )
