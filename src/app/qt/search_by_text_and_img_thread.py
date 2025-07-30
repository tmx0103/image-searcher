"""
Copyright © 2025-2025 tmx0103.  
Licensed under the Apache-2.0 License.  
For full terms, see the LICENSE file.  
search_by_text_and_img_thread.py
"""
from PyQt5.QtCore import QThread, pyqtSignal

from src.app.log.logger import logger
from src.app.service.img_search_service import ImgSearchService


class SearchByTextAndImgThread(QThread):
    # 定义信号：文本块、完成信号、错误信号
    signal_mixed_img_generated = pyqtSignal(str, str)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, image_path: str, text: str, cosine_similarity: float, img_count: int):
        super().__init__()
        self.imgSearchService = ImgSearchService.get_instance()
        self.imagePath = image_path
        self.text = text
        self.cosineSimilarity = cosine_similarity
        self.imgCount = img_count
        self.similar_img_model_multi_model_list = None
        self.similar_img_model_all_text_list = None
        self.mixed_image_path = None

    def run(self):
        try:
            self.similar_img_model_multi_model_list, self.similar_img_model_all_text_list, mixed_image_path \
                = self.imgSearchService.search_by_text_and_img(self.imagePath, self.text, self.cosineSimilarity, self.imgCount)
            logger.info("[SearchByTextAndImgThread]已完成")
            self.signal_mixed_img_generated.emit(self.text, mixed_image_path)
            self.finished.emit()
        except Exception as e:
            logger.error(e, exc_info=True)
            self.error.emit()
