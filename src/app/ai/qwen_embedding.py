"""
Copyright © 2025-2025 tmx0103.  
Licensed under the Apache-2.0 License.  
For full terms, see the LICENSE file.  
qwen_embedding.py
"""
from threading import Lock

import torch
from transformers import AutoTokenizer, AutoModel


class QwenEmbedding:
    _instance = None
    _lock = Lock()

    @classmethod
    def get_instance(cls):
        if cls._instance:
            return cls._instance
        with cls._lock:
            if not cls._instance:
                cls._instance = QwenEmbedding()
        return cls._instance

    def __init__(self):
        self.modelName = "Qwen/Qwen3-Embedding-0.6B"
        self.tokenizer = AutoTokenizer.from_pretrained(self.modelName)
        self.model = AutoModel.from_pretrained(self.modelName).to("cuda").eval()

    def embed_to_vec(self, text: str):
        tokenized_text = self.tokenizer([text], padding=True, truncation=True,
                                        max_length=10240, return_tensors="pt").to("cuda")
        with torch.no_grad():
            outputs = self.model(**tokenized_text)
            # 使用平均池化获取整个文本的嵌入
            embeddings = outputs.last_hidden_state.mean(dim=1).squeeze()
            return embeddings.cpu().numpy()


if __name__ == "__main__":
    qwen_embedding = QwenEmbedding()
    embedding = qwen_embedding.embed_to_vec("")
    print(embedding)
