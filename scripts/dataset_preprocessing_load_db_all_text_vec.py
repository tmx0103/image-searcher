"""
Copyright © 2025-2025 tmx0103.
Licensed under the Apache-2.0 License.
For full terms, see the LICENSE file.
dataset_preprocessing_load_db_all_text_vec.py
"""
import logging.config
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.app.ai.qwen_embedding import QwenEmbedding
from src.app.db.mapper.img_vector_mapper import ImgVectorMapper
from src.app.log.logger import logger
from src.app.utils import sha256_util

if __name__ == "__main__":
    LOGGING_CONFIG = {
        "version": 1,
        "formatters": {"standard_formatter": {"format": "%(asctime)s [%(levelname)s] %(module)s:%(lineno)d - %(message)s"}},
        "handlers": {
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": "../logs/dataset_preprocessing_load_db_all_text_vec.log",
                "maxBytes": 10 * 1024 * 1024,
                "formatter": "standard_formatter",
            },
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "standard_formatter",
            }
        },
        "loggers": {
            "standard_logger": {
                "handlers": ["file"], "level": "DEBUG",
            }
        },
        "root": {"handlers": ["console"], "level": "DEBUG"}
    }
    log_dir = "../logs"
    os.makedirs(log_dir, exist_ok=True)

    logging.config.dictConfig(LOGGING_CONFIG)
    # 载入数据库
    load_dotenv()
    engine = create_engine(f"postgresql://"
                           f"{os.getenv('POSTGRESQL_USER')}:{os.getenv('POSTGRESQL_PASSWORD')}"
                           f"@{os.getenv('POSTGRESQL_HOST')}:{os.getenv('POSTGRESQL_PORT')}/{os.getenv('POSTGRESQL_DB')}")
    Session = sessionmaker(bind=engine)
    with (Session() as session):
        img_vector_mapper = ImgVectorMapper(session)
        qwen_embedding = QwenEmbedding()
        for file_dir, dirs, file_names in os.walk(os.path.join("../resources", "dataset")):
            for file_name in file_names:
                file_relative_path = os.path.join(file_dir, file_name)
                logger.info(f"处理：{file_relative_path}")

                # 计算当前文件的sha256
                file_sha256 = sha256_util.sha256_file(file_relative_path)

                # 读取数据库中是否存在与该文件一致的哈希，如果存在则移除该文件
                img_vector_do = img_vector_mapper.query_by_file_sha256(file_sha256)
                if img_vector_do and img_vector_do.all_text_vec is None:
                    text_to_embed: str = ""
                    if img_vector_do.ocr_text is not None and img_vector_do.ocr_text != "":
                        text_to_embed = img_vector_do.ocr_text + "\n"
                    if img_vector_do.tag_text is not None and img_vector_do.tag_text != "":
                        text_to_embed += "自定义标签：" + img_vector_do.tag_text
                    logger.info(f"处理：{text_to_embed}")
                    all_text_vec = qwen_embedding.embed_to_vec(text_to_embed)
                    all_text_vec_str = "[" + ",".join([str(x) for x in all_text_vec]) + "]"
                    img_vector_mapper.update_all_text_vec_by_file_sha256(file_sha256, all_text_vec_str)
                    logger.info(f"已完成处理：{file_relative_path}")
                else:
                    logger.info(f"跳过：{file_relative_path}")
