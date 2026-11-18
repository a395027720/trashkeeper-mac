"""按扩展名判定文件类型，用于列表里的「类型」列。"""

import os
from pathlib import Path

KIND_BY_EXT = {
    "图片": {
        ".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".heic", ".heif",
        ".bmp", ".tiff", ".tif", ".ico", ".raw", ".psd", ".ai",
    },
    "视频": {
        ".mp4", ".mov", ".mkv", ".avi", ".wmv", ".flv", ".m4v", ".webm",
        ".mpg", ".mpeg", ".rmvb",
    },
    "音频": {
        ".mp3", ".wav", ".flac", ".aac", ".m4a", ".ogg", ".wma", ".ape",
        ".aiff", ".au",
    },
    "文档": {
        ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt",
        ".md", ".rtf", ".csv", ".pages", ".numbers", ".key", ".epub",
    },
    "压缩包": {
        ".zip", ".tar", ".gz", ".tgz", ".bz2", ".xz", ".7z", ".rar", ".dmg",
        ".pkg", ".zst", ".iso",
    },
    "代码": {
        ".py", ".js", ".mjs", ".ts", ".tsx", ".jsx", ".java", ".c", ".cpp",
        ".h", ".hpp", ".m", ".mm", ".go", ".rs", ".rb", ".php", ".swift",
        ".kt", ".scala", ".sh", ".bash", ".zsh", ".pl", ".lua", ".vue",
        ".html", ".htm", ".css", ".scss", ".less", ".sql", ".r",
    },
    "数据": {
        ".json", ".yaml", ".yml", ".toml", ".xml", ".ini", ".conf", ".plist",
        ".db", ".sqlite", ".sqlite3", ".csv",
    },
    "字体": {".ttf", ".otf", ".woff", ".woff2", ".eot"},
    "电子书": {".epub", ".mobi", ".azw3"},
    "模型文件": {".onnx", ".pt", ".pth", ".gguf", ".safetensors", ".bin", ".ckpt", ".mlmodel"},
}

# 常见的可执行程序（无扩展名）
EXECUTABLE_NAMES = {"python", "python3", "node", "npm", "git", "ruby", "php", "java"}


def classify(path, is_dir: bool = False) -> str:
    """返回文件类型的中文名。"""
    target = Path(path)
    if is_dir:
        if target.suffix == ".app":
            return "应用程序"
        return "文件夹"

    suffix = target.suffix.lower()
    if suffix:
        for kind, extensions in KIND_BY_EXT.items():
            if suffix in extensions:
                return kind

    if target.name.lower() in EXECUTABLE_NAMES:
        return "可执行程序"
    if os.access(str(target), os.X_OK) and target.is_file():
        return "可执行程序"
    if not suffix and target.is_file():
        return "无扩展名文件"
    return "文件"
