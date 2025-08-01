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
from src.app.db.mapper.image_info_mapper import ImageInfoMapper
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

    def update_image_vector(self, file_path: str):
        with self.Session() as session:
            image_info_mapper = ImageInfoMapper(session)
            image_info_do = image_info_mapper.query_by_file_path(file_path)
            with Image.open(image_info_do.file_path) as image:
                # 计算图片的特征向量
                image_vector = self.chineseClip.embed_image_to_vec(image)
                image_info_mapper.update_image_vector_by_file_path(file_path, image_vector)

    def update_all_text_vector(self, file_path: str):
        with self.Session() as session:
            image_info_mapper = ImageInfoMapper(session)
            image_info_do = image_info_mapper.query_by_file_path(file_path)
            all_text = StringUtil.concat(image_info_do.tag_text, ",", image_info_do.ocr_text)
            # 计算全部文本的特征向量
            all_text_vector = self.qwenEmbedding.embed_to_vector(all_text)
            image_info_mapper.update_all_text_vector_by_file_path(file_path, all_text_vector)
