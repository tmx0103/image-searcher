"""
Copyright © 2025-2025 tmx0103.  
Licensed under the Apache-2.0 License.  
For full terms, see the LICENSE file.  
chinese_bert.py
"""
import torch
from transformers import BertTokenizer, BertModel


class ChineseBert:
    def __init__(self):
        self.modelName = "bert-base-chinese"
        self.tokenizer = BertTokenizer.from_pretrained(self.modelName)
        self.model = BertModel.from_pretrained(self.modelName).to("cuda").eval()

    def embed_to_sentence_vec(self, text):
        tokenized_text = self.tokenizer([text], padding=True, truncation=True,
                                        max_length=512, return_tensors="pt").to("cuda")
        with torch.no_grad():
            outputs = self.model(**tokenized_text)
            embeddings = outputs.last_hidden_state
            mask = tokenized_text.attention_mask.unsqueeze(-1)  # 扩展掩码维度
            sentence_vectors = (embeddings * mask).sum(dim=1) / mask.sum(dim=1)
            return sentence_vectors[0].cpu().numpy()
