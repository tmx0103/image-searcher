"""
Copyright © 2025-2025 tmx0103.  
Licensed under the Apache-2.0 License.  
For full terms, see the LICENSE file.  
chinese_clip.py
"""
from threading import Lock

from transformers import ChineseCLIPModel, ChineseCLIPProcessor, AutoTokenizer


class ChineseClip:
    _instance = None
    _lock = Lock()

    @classmethod
    def get_instance(cls):
        if cls._instance:
            return cls._instance
        with cls._lock:
            if not cls._instance:
                cls._instance = ChineseClip()
        return cls._instance

    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("OFA-Sys/chinese-clip-vit-huge-patch14")
        self.processor = ChineseCLIPProcessor.from_pretrained("OFA-Sys/chinese-clip-vit-huge-patch14")

        self.model = ChineseCLIPModel.from_pretrained("OFA-Sys/chinese-clip-vit-huge-patch14").to("cuda")

    def embed_text_to_vec(self, text):
        inputs = self.tokenizer(text, max_length=512, padding=True, return_tensors="pt", truncation=True).to("cuda")
        feature = self.model.get_text_features(**inputs)
        feature = feature / feature.norm(p=2, dim=-1, keepdim=True)  # normalize
        feature = feature.cpu().detach().numpy()
        return feature[0]

    def embed_image_to_vec(self, image):
        inputs = self.processor(images=image, return_tensors="pt").to("cuda")
        feature = self.model.get_image_features(**inputs)
        feature = feature / feature.norm(p=2, dim=-1, keepdim=True)  # normalize
        feature = feature.cpu().detach().numpy()
        return feature[0]


if __name__ == '__main__':
    clip = ChineseClip()
    ndarray1 = clip.embed_text_to_vec("test")
    print("test")
