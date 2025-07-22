"""
Copyright © 2025-2025 tmx0103.  
Licensed under the Apache-2.0 License.  
For full terms, see the LICENSE file.  
paddle_ocr_util.py
"""
import logging
from threading import Lock

import numpy as np
from PIL import Image
from paddleocr import TextDetection, TextRecognition, PaddleOCR

from src.app.log.logger import logger


class PaddleOCRUtil:
    _instance = None
    _lock = Lock()

    @classmethod
    def get_instance(cls):
        if cls._instance:
            return cls._instance
        with cls._lock:
            if not cls._instance:
                cls._instance = PaddleOCRUtil("resources/ai-models/PP-OCRv5_server_det_infer",
                                              "resources/ai-models/PP-OCRv5_server_rec_infer")
        return cls._instance

    def __init__(self, text_detection_model_dir, text_recognition_model_dir):
        self.ocr = PaddleOCR(text_detection_model_dir=text_detection_model_dir,
                             text_recognition_model_dir=text_recognition_model_dir,
                             use_doc_unwarping=False,
                             device="cpu")
        self.text_detection_model = TextDetection(model_dir=text_detection_model_dir, device="cpu")
        self.text_recognition_model = TextRecognition(model_dir=text_recognition_model_dir, device="cpu")
        # 兼容paddle ocr中，修改了root logger日志级别的bug
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        logging.debug("PaddleOCRUtil init")

    def detect(self, image_path):
        return self.text_detection_model.predict(image_path, batch_size=1)

    def recognize(self, image) -> list[str]:
        img_array = np.array(image.convert('RGB'))
        output = self.ocr.predict(img_array)
        return output[0]['rec_texts']


if __name__ == "__main__":
    ocr_util = PaddleOCRUtil("../resources/ai-models/PP-OCRv5_server_det_infer",
                             "../resources/ai-models/PP-OCRv5_server_rec_infer")

    with Image.open("../resources/test.jpg") as img:

        texts = ocr_util.recognize(img)
        for text in texts:
            logger.info(text)
