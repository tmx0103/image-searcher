"""
Copyright © 2025-2025 tmx0103.  
Licensed under the Apache-2.0 License.  
For full terms, see the LICENSE file.  
img_search_tool.py
"""
import time
from threading import Lock

from PyQt5.QtCore import QObject, pyqtSignal

from src.app.log.logger import logger


class ImgSearchTool(QObject):
    _instance = None
    _lock = Lock()
    signal_start_img_search = pyqtSignal(str)

    @classmethod
    def get_instance(cls):
        if cls._instance:
            return cls._instance
        with cls._lock:
            if not cls._instance:
                cls._instance = ImgSearchTool()
        return cls._instance

    def search_by_text(self, text: str):
        self.signal_start_img_search.emit(text)


def img_search_by_text_tool(text: str):
    """文本搜图函数。
    这是一个根据文本搜索图片的工具。无论搜索成功与否，最终的图片都会展示到右侧的展示区中供用户查看

    Args:
        text: 用于检索图片的文本
    Returns:
        如果成功，该工具会返回字符串“搜图完成，请查看结果。”，否则会返回其他内容。
    """
    logger.info("工具搜图,text=%s", text)
    tool = ImgSearchTool.get_instance()
    tool.search_by_text(text)
    # 等待3秒
    time.sleep(3)
    logger.info("工具搜图,OK")
    return "搜图完成，请查看结果。"
