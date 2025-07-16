"""
Copyright © 2025-2025 tmx0103.  
Licensed under the Apache-2.0 License.  
For full terms, see the LICENSE file.  
paddle_ocr_util.py
"""
import numpy as np
from PIL import Image
from paddleocr import TextDetection, TextRecognition, PaddleOCR


class PaddleOCRUtil:
    def __init__(self, text_detection_model_dir, text_recognition_model_dir):
        self.ocr = PaddleOCR(text_detection_model_dir=text_detection_model_dir,
                             text_recognition_model_dir=text_recognition_model_dir,
                             use_doc_unwarping=False,
                             device="cpu")
        self.text_detection_model = TextDetection(model_dir=text_detection_model_dir, device="cpu")
        self.text_recognition_model = TextRecognition(model_dir=text_recognition_model_dir, device="cpu")

    def detect(self, image_path):
        return self.text_detection_model.predict(image_path, batch_size=1)

    # def recognize(self, image_path):
    #     return self.text_recognition_model.predict(image_path, batch_size=1)

    def recognize(self, image) -> list[str]:
        img_array = np.array(image.convert('RGB'))
        output = self.ocr.predict(img_array)
        return output[0]['rec_texts']


if __name__ == "__main__":
    ocr_util = PaddleOCRUtil("../resources/ai-models/PP-OCRv5_server_det_infer",
                             "../resources/ai-models/PP-OCRv5_server_rec_infer")

    with Image.open("20180708-093848_92ff280b46d067fa.jpg") as img:

        texts = ocr_util.recognize(img)
        for text in texts:
            print(text)
