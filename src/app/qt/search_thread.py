"""
Copyright © 2025-2025 tmx0103.  
Licensed under the Apache-2.0 License.  
For full terms, see the LICENSE file.  
search_thread.py
"""
from PyQt5.QtCore import QThread, pyqtSignal

from src.app.log.logger import logger
from src.app.service.img_search_service import ImgSearchService


class SearchThread(QThread):
    # 定义信号：文本块、完成信号、错误信号
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, text: str, cosine_similarity: float, img_count: int):
        super().__init__()
        self.imgSearchService = ImgSearchService.get_instance()
        self.text = text
        self.cosineSimilarity = cosine_similarity
        self.imgCount = img_count
        self.similar_img_model_multi_model_list = None
        self.similar_img_model_all_text_list = None

    def run(self):
        try:
            similar_img_model_multi_model_list, similar_img_model_all_text_list \
                = self.imgSearchService.search_by_text(self.text, self.cosineSimilarity, self.imgCount)
            self.similar_img_model_multi_model_list, self.similar_img_model_all_text_list = similar_img_model_multi_model_list, similar_img_model_all_text_list
            logger.info(similar_img_model_multi_model_list)
            logger.info(similar_img_model_all_text_list)
            self.finished.emit()
        except Exception as e:
            logger.error(e)
            self.error.emit()
