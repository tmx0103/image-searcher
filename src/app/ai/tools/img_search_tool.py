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
    signal_start_img_search_by_text = pyqtSignal(str)
    signal_start_img_search_by_img = pyqtSignal()
    signal_start_img_search_by_text_and_img = pyqtSignal(str)

    @classmethod
    def get_instance(cls):
        if cls._instance:
            return cls._instance
        with cls._lock:
            if not cls._instance:
                cls._instance = ImgSearchTool()
        return cls._instance

    def search_by_text(self, text: str):
        self.signal_start_img_search_by_text.emit(text)

    def search_by_img(self):
        self.signal_start_img_search_by_img.emit()

    def search_by_text_and_img(self, text: str):
        self.signal_start_img_search_by_text_and_img.emit(text)


def img_search_by_text_tool(text: str):
    """文本搜图工具。
    这是一个根据文本搜索图片的工具。无论搜索成功与否，最终的图片都会展示到右侧的展示区中供用户查看

    Args:
        text: 用于检索图片的文本
    Returns:
        如果成功，该工具会返回字符串“搜图完成，请查看结果。”，否则会返回其他内容。
    """
    logger.info("LLM文本搜图工具,text=%s", text)
    tool = ImgSearchTool.get_instance()
    tool.search_by_text(text)
    # 等待3秒
    time.sleep(3)
    logger.info("LLM文本搜图工具,OK")
    return "搜图完成，请查看结果。"


def img_search_by_image_tool():
    """以图搜图工具。
    这是一个根据图片搜索图片的工具。无论搜索成功与否，最终的图片都会展示到右侧的展示区中供用户查看。
    注意，这个工具不需要传入图片作为入参，因为该工具一旦调用，工具会自动获取用户最近一次向机器人发送的图片。

    Returns:
        如果成功，该工具会返回字符串“搜图完成，请查看结果。”，否则会返回其他内容。
    """
    logger.info("LLM以图搜图工具")
    tool = ImgSearchTool.get_instance()
    tool.search_by_img()
    # 等待3秒
    time.sleep(3)
    logger.info("LLM以图搜图工具,OK")
    return "搜图完成，请查看结果。"


def img_search_by_text_and_image_tool(text: str):
    """图文融合搜图工具。
    这是一个根据文本和图片搜索图片的工具，它在内部会调用stable diffusion，使用用户输入文本的描述信息来局部重绘用户输入的图片。
    最后，使用这张重绘后的图片再在图库中进行以图搜图。
    无论搜索成功与否，最终的图片都会展示到右侧的展示区中供用户查看。
    注意：
    1、这个工具不需要传入图片作为入参，因为该工具一旦调用，工具会自动获取用户最近一次向你发送的图片。
    2、输入的文本text必须是适配stable diffusion图生图工具的正向提示词。
    3、提示词除了需要从用户请求的文本中提取之外，也需要从用户输入的图片中提取，但是如果文本和图片的特征产生冲突，以文本为准。文本中未出现，但是图片中非常显著，具有鲜明特色的特征，必须提取。
    比如，用户请求“帮我在这张图的基础上修改图中人物的发色为黄色、瞳色为绿色”（同时附带一张具有1个女性人物（发色为白色，瞳色为蓝色）的图片），
    你需要将其转换为“yellow hair,green eyes,1girl”作为提示词文本text。其中，yellow hair和green eyes提示词是基于用户文本生成，1girl是基于图片生成

    Args:
        text: 适配stable diffusion图生图工具的正向提示词
    Returns:
        如果成功，该工具会返回字符串“搜图完成，请查看结果。”，否则会返回其他内容。
    """
    logger.info("LLM图文融合搜图工具")
    tool = ImgSearchTool.get_instance()
    tool.search_by_text_and_img(text)
    # 等待3秒
    time.sleep(3)
    logger.info("LLM图文融合搜图工具,OK")
    return "搜图完成，请查看结果。"
