"""
Copyright © 2025-2025 tmx0103.  
Licensed under the Apache-2.0 License.  
For full terms, see the LICENSE file.  
repo_vector_service.py
"""
import os
from threading import Lock

from PIL import Image
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.app.ai.chinese_clip import ChineseClip
from src.app.ai.qwen_embedding import QwenEmbedding
from src.app.db.mapper.img_vector_mapper import ImgVectorMapper
from src.app.utils.string_util import StringUtil


class RepoVectorService:
    _instance = None
    _lock = Lock()

    @classmethod
    def get_instance(cls):
        if cls._instance:
            return cls._instance
        with cls._lock:
            if not cls._instance:
                cls._instance = RepoVectorService()
        return cls._instance

    def __init__(self):
        self.chineseClip = ChineseClip.get_instance()
        self.qwenEmbedding = QwenEmbedding.get_instance()
        self.engine = create_engine(f"postgresql://"
                                    f"{os.getenv('POSTGRESQL_USER')}:{os.getenv('POSTGRESQL_PASSWORD')}"
                                    f"@{os.getenv('POSTGRESQL_HOST')}:{os.getenv('POSTGRESQL_PORT')}/{os.getenv('POSTGRESQL_DB')}")
        self.Session = sessionmaker(bind=self.engine)

    def update_img_vector(self, file_sha256: str):
        """构造图片的特征向量，使用Clip模型

        :param file_sha256:
        :return:
        """
        with self.Session() as session:
            img_vector_mapper = ImgVectorMapper(session)
            img_vector_do = img_vector_mapper.query_by_file_sha256(file_sha256)
            img_file_path = os.path.join(img_vector_do.file_dir, img_vector_do.file_name)
            with Image.open(img_file_path) as image:
                # 计算图片的特征向量
                image_vector = self.chineseClip.embed_image_to_vec(image)
                image_vector_pg_str = "[" + ",".join([str(x) for x in image_vector]) + "]"
                img_vector_mapper.update_img_vec_by_file_sha256(file_sha256, image_vector_pg_str)

    def update_all_text_vector(self, file_sha256: str):
        """构造tag_text拼接ocr_text的特征向量，使用Qwen-Embedding模型

        :param file_sha256:
        :return:
        """
        with self.Session() as session:
            img_vector_mapper = ImgVectorMapper(session)
            img_vector_do = img_vector_mapper.query_by_file_sha256(file_sha256)
            all_text = StringUtil.concat(img_vector_do.tag_text, ",", img_vector_do.ocr_text)
            # 计算全部文本的特征向量
            all_text_vector = self.qwenEmbedding.embed_to_vector(all_text)
            all_text_vector_pg_str = "[" + ",".join([str(x) for x in all_text_vector]) + "]"
            img_vector_mapper.update_all_text_vec_by_file_sha256(file_sha256, all_text_vector_pg_str)
