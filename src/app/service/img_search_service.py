"""
Copyright © 2025-2025 tmx0103.  
Licensed under the Apache-2.0 License.  
For full terms, see the LICENSE file.  
img_search_service.py
"""
import os
from threading import Lock

from PIL import Image
from numpy import ndarray
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.app.ai.chinese_clip import ChineseClip
from src.app.ai.paddle_ocr_util import PaddleOCRUtil
from src.app.ai.qwen_embedding import QwenEmbedding
from src.app.ai.stable_diffusion import StableDiffusion
from src.app.db.mapper.image_info_mapper import ImageInfoMapper
from src.app.db.models.similar_img_models import SimilarImgModel
from src.app.utils.string_util import StringUtil


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
        self.ocrUtil = PaddleOCRUtil.get_instance()
        self.qwenEmbedding = QwenEmbedding.get_instance()
        self.sd = StableDiffusion.get_instance()
        self.engine = create_engine(f"postgresql://"
                                    f"{os.getenv('POSTGRESQL_USER')}:{os.getenv('POSTGRESQL_PASSWORD')}"
                                    f"@{os.getenv('POSTGRESQL_HOST')}:{os.getenv('POSTGRESQL_PORT')}/{os.getenv('POSTGRESQL_DB')}")
        self.Session = sessionmaker(bind=self.engine)

    def search_by_img(self, img_path: str, cosine_similarity: float, img_count: int):
        with Image.open(img_path) as image:
            # 计算图片的特征向量
            image_feature = self.chineseClip.embed_image_to_vec(image)
            # 从图片中识别文字OCR
            ocr_texts = ",".join(self.ocrUtil.recognize(image))
            # 计算所有文本的特征向量
            all_text = ocr_texts + ","
            all_text_vector = self.qwenEmbedding.embed_to_vector(all_text)
        with self.Session() as session:
            image_info_mapper = ImageInfoMapper(session)
            # 使用图片特征向量进行检索
            image_info_do_list = image_info_mapper.search_by_image_vector(image_feature, cosine_similarity, img_count)
            similar_img_model_multi_model_list = []
            for image_info_do in image_info_do_list:
                similar_img_model = SimilarImgModel(image_info_do.file_path, image_info_do.file_name, image_info_do.cosine_distance,
                                                    image_info_do.file_sha256)
                similar_img_model_multi_model_list.append(similar_img_model)

            # 使用所有文本的特征向量进行检索
            image_info_do_list = image_info_mapper.search_by_all_text_vector(all_text_vector, cosine_similarity, img_count)
            similar_img_model_all_text_list = []
            for image_info_do in image_info_do_list:
                similar_img_model = SimilarImgModel(image_info_do.file_path, image_info_do.file_name, image_info_do.cosine_distance,
                                                    image_info_do.file_sha256)
                similar_img_model_all_text_list.append(similar_img_model)

            return similar_img_model_multi_model_list, similar_img_model_all_text_list

    def search_by_text(self, text: str, cosine_similarity: float, img_count: int):
        # 计算文本由多模态模型计算的特征向量
        text_feature_chinese_clip = self.chineseClip.embed_text_to_vec(text)
        # 计算文本由文本模型计算的特征向量
        text_feature_qwen = self.qwenEmbedding.embed_to_vector(text)

        with self.Session() as session:
            image_info_mapper = ImageInfoMapper(session)
            # 使用图片特征向量进行检索
            image_info_do_list = image_info_mapper.search_by_image_vector(text_feature_chinese_clip, cosine_similarity, img_count)
            similar_img_model_multi_model_list = []
            for image_info_do in image_info_do_list:
                similar_img_model = SimilarImgModel(image_info_do.file_path, image_info_do.file_name, image_info_do.cosine_distance,
                                                    image_info_do.file_sha256)
                similar_img_model_multi_model_list.append(similar_img_model)

            # 使用所有文本的特征向量进行检索
            image_info_do_list = image_info_mapper.search_by_all_text_vector(text_feature_qwen, cosine_similarity, img_count)
            similar_img_model_all_text_list = []
            for image_info_do in image_info_do_list:
                similar_img_model = SimilarImgModel(image_info_do.file_path, image_info_do.file_name, image_info_do.cosine_distance,
                                                    image_info_do.file_sha256)
                similar_img_model_all_text_list.append(similar_img_model)

            return similar_img_model_multi_model_list, similar_img_model_all_text_list

    def search_by_text_and_img(self, img_file_path: str, text: str, cosine_similarity: float, img_count: int):
        # 生成图文融合的新图
        mixed_img_file_path = self.sd.generate_image(text, img_file_path)
        # 计算融合图的特征向量
        with Image.open(mixed_img_file_path) as mixed_image:
            mixed_image_vector: ndarray = self.chineseClip.embed_image_to_vec(mixed_image)
        # 计算全部文本的特征向量，注意必须把tag_text放在前面防止被模型512token限制截断
        with Image.open(img_file_path) as image:
            # 从图片中识别文字OCR
            ocr_texts = ",".join(self.ocrUtil.recognize(image))
            # 计算特征向量
            all_text = StringUtil.concat(text, ",", ocr_texts)
            all_text_vector: ndarray = self.qwenEmbedding.embed_to_vector(all_text)

        with self.Session() as session:
            image_info_mapper = ImageInfoMapper(session)
            # 使用图文混合多模态特征向量进行检索
            image_info_do_list = image_info_mapper.search_by_image_vector(mixed_image_vector, cosine_similarity, img_count)
            similar_img_model_multi_model_list = []
            for image_info_do in image_info_do_list:
                similar_img_model = SimilarImgModel(image_info_do.file_path, image_info_do.file_name, image_info_do.cosine_distance,
                                                    image_info_do.file_sha256)
                similar_img_model_multi_model_list.append(similar_img_model)

            # 使用文本信息特征向量进行检索
            image_info_do_list = image_info_mapper.search_by_all_text_vector(all_text_vector, cosine_similarity, img_count)
            similar_img_model_all_text_list = []
            for image_info_do in image_info_do_list:
                similar_img_model = SimilarImgModel(image_info_do.file_path, image_info_do.file_name, image_info_do.cosine_distance,
                                                    image_info_do.file_sha256)
                similar_img_model_all_text_list.append(similar_img_model)

            return similar_img_model_multi_model_list, similar_img_model_all_text_list, mixed_img_file_path
