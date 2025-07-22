"""
Copyright © 2025-2025 tmx0103.  
Licensed under the Apache-2.0 License.  
For full terms, see the LICENSE file.  
img_search_service.py
"""
import os
from threading import Lock

from PIL import Image
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.app.ai.chinese_bert import ChineseBert
from src.app.ai.chinese_clip import ChineseClip
from src.app.ai.paddle_ocr_util import PaddleOCRUtil
from src.app.ai.qwen_embedding import QwenEmbedding
from src.app.db.mapper.img_vector_mapper import ImgVectorMapper
from src.app.db.models.similar_img_models import SimilarImgModel


class ImgSearchService:
    _instance = None
    _lock = Lock()

    @classmethod
    def get_instance(cls):
        if cls._instance:
            return cls._instance
        with cls._lock:
            if not cls._instance:
                cls._instance = ImgSearchService()
        return cls._instance

    def __init__(self):
        self.chineseClip = ChineseClip.get_instance()
        self.chineseBert = ChineseBert.get_instance()
        self.ocrUtil = PaddleOCRUtil.get_instance()
        self.qwenEmbedding = QwenEmbedding.get_instance()
        self.engine = create_engine(f"postgresql://"
                                    f"{os.getenv('POSTGRESQL_USER')}:{os.getenv('POSTGRESQL_PASSWORD')}"
                                    f"@{os.getenv('POSTGRESQL_HOST')}:{os.getenv('POSTGRESQL_PORT')}/{os.getenv('POSTGRESQL_DB')}")
        self.Session = sessionmaker(bind=self.engine)

    def search_by_img(self, img_file_path: str, cosine_similarity: float, img_count: int):
        with Image.open(img_file_path) as image:
            # 计算图片的特征向量
            image_feature = self.chineseClip.embed_image_to_vec(image)
            image_feature_pg_str = "[" + ",".join([str(x) for x in image_feature[0]]) + "]"
            # 从图片中识别文字OCR
            ocr_texts = ",".join(self.ocrUtil.recognize(image))
            # # 计算OCR文字的特征向量
            # ocr_text_sentence_vec = self.chineseBert.embed_to_sentence_vec(ocr_texts)
            # ocr_text_sentence_vec_str = "[" + ",".join([str(x) for x in ocr_text_sentence_vec]) + "]"
            # 计算所有文本的特征向量
            all_text = ocr_texts
            all_text_vec = self.qwenEmbedding.embed_to_vec(all_text)
            all_text_vec_str = "[" + ",".join([str(x) for x in all_text_vec]) + "]"
        with self.Session() as session:
            img_vector_mapper = ImgVectorMapper(session)
            # 使用图片特征向量进行检索
            img_vector_do_list = img_vector_mapper.search(image_feature_pg_str, cosine_similarity, img_count)
            similar_img_model_multi_model_list = []
            for img_vector_do in img_vector_do_list:
                similar_img_model = SimilarImgModel(img_vector_do.file_dir, img_vector_do.file_name, img_vector_do.cosine_distance)
                similar_img_model_multi_model_list.append(similar_img_model)

            # 使用所有文本的特征向量进行检索
            img_vector_do_list = img_vector_mapper.search_by_all_text_vector(all_text_vec_str, cosine_similarity, img_count)
            similar_img_model_all_text_list = []
            for img_vector_do in img_vector_do_list:
                similar_img_model = SimilarImgModel(img_vector_do.file_dir, img_vector_do.file_name, img_vector_do.cosine_distance)
                similar_img_model_all_text_list.append(similar_img_model)

            return similar_img_model_multi_model_list, similar_img_model_all_text_list

    def search_by_text(self, text: str, cosine_similarity: float, img_count: int):
        # 计算文本由多模态模型计算的特征向量
        text_feature_chinese_clip = self.chineseClip.embed_text_to_vec(text)
        text_feature_chinese_clip_pg_str = "[" + ",".join([str(x) for x in text_feature_chinese_clip[0]]) + "]"
        # 计算文本由文本模型计算的特征向量
        # text_feature_chinese_bert = self.chineseBert.embed_to_sentence_vec(text)
        # text_feature_chinese_bert_pg_str = "[" + ",".join([str(x) for x in text_feature_chinese_bert]) + "]"
        # 计算文本由文本模型计算的特征向量
        text_feature_qwen = self.qwenEmbedding.embed_to_vec(text)
        text_feature_qwen_pg_str = "[" + ",".join([str(x) for x in text_feature_qwen]) + "]"

        with self.Session() as session:
            img_vector_mapper = ImgVectorMapper(session)
            # 使用图片特征向量进行检索
            img_vector_do_list = img_vector_mapper.search(text_feature_chinese_clip_pg_str, cosine_similarity, img_count)
            similar_img_model_multi_model_list = []
            for img_vector_do in img_vector_do_list:
                similar_img_model = SimilarImgModel(img_vector_do.file_dir, img_vector_do.file_name, img_vector_do.cosine_distance)
                similar_img_model_multi_model_list.append(similar_img_model)

            # 使用所有文本的特征向量进行检索
            img_vector_do_list = img_vector_mapper.search_by_all_text_vector(text_feature_qwen_pg_str, cosine_similarity, img_count)
            similar_img_model_all_text_list = []
            for img_vector_do in img_vector_do_list:
                similar_img_model = SimilarImgModel(img_vector_do.file_dir, img_vector_do.file_name, img_vector_do.cosine_distance)
                similar_img_model_all_text_list.append(similar_img_model)

            return similar_img_model_multi_model_list, similar_img_model_all_text_list
