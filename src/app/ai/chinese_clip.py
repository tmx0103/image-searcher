"""
Copyright © 2025-2025 tmx0103.  
Licensed under the Apache-2.0 License.  
For full terms, see the LICENSE file.  
chinese_clip.py
"""
from threading import Lock

from transformers import ChineseCLIPModel, ChineseCLIPProcessor


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
        self.model = ChineseCLIPModel.from_pretrained("OFA-Sys/chinese-clip-vit-huge-patch14").to("cuda")
        self.processor = ChineseCLIPProcessor.from_pretrained("OFA-Sys/chinese-clip-vit-huge-patch14")

    def embed_text_to_vec(self, text):
        inputs = self.processor(text=text, return_tensors="pt").to("cuda")
        feature = self.model.get_text_features(**inputs)
        feature = feature / feature.norm(p=2, dim=-1, keepdim=True)  # normalize
        return feature.cpu().detach().numpy()

    def embed_image_to_vec(self, image):
        inputs = self.processor(images=image, return_tensors="pt").to("cuda")
        feature = self.model.get_image_features(**inputs)
        feature = feature / feature.norm(p=2, dim=-1, keepdim=True)  # normalize
        return feature.cpu().detach().numpy()
