"""
Copyright © 2025-2025 tmx0103.
Licensed under the Apache-2.0 License.
For full terms, see the LICENSE file.
run_init_all_text_vector.py
第一次运行GUI应用前，【必须运行该脚本】。
该脚本的作用是，为数据库中所有文本生成特征向量，并保存到数据库中。如果未执行过OCR或特征向量已生成，则跳过。
可选：强制刷新数据库中所有文本的生成特征向量（未执行过OCR除外）。
"""
import logging.config
import os

from dotenv import load_dotenv

from src.app.utils.string_util import StringUtil

load_dotenv()

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.app.ai.qwen_embedding import QwenEmbedding
from src.app.db.mapper.image_info_mapper import ImageInfoMapper
from src.app.log.logger import logger


class InitAllTextVectorUtil:
    engine = create_engine(f"postgresql://"
                           f"{os.getenv('POSTGRESQL_USER')}:{os.getenv('POSTGRESQL_PASSWORD')}"
                           f"@{os.getenv('POSTGRESQL_HOST')}:{os.getenv('POSTGRESQL_PORT')}/{os.getenv('POSTGRESQL_DB')}")
    Session = sessionmaker(bind=engine)
    textEmbeddingUtil = QwenEmbedding.get_instance()

    @staticmethod
    def init(force_refresh: bool = False):
        with InitAllTextVectorUtil.Session() as session:
            image_info_mapper = ImageInfoMapper(session)
        # 批量处理，每次从数据库中取100条
        batch_start_id = -1
        image_info_do_list = image_info_mapper.query_by_id_range_batch(id=batch_start_id, batch_size=100)
        while image_info_do_list is not None and len(image_info_do_list) > 0:
            for image_info_do in image_info_do_list:
                file_path = image_info_do.file_path
                logger.info(f"初始化：{file_path}")
                # 如果不要求强制刷新且数据库中已有OCR文本，则跳过
                if not force_refresh and image_info_do.all_text_vector:
                    logger.info(f"该图已处理过：{file_path}")
                    continue
                # 如果不存在OCR文本表示OCR前置步骤未完成，跳过
                if image_info_do.ocr_text is None:
                    logger.info(f"该图未完成OCR，跳过：{file_path}")
                    continue
                all_text = InitAllTextVectorUtil.__build_all_text(image_info_do.ocr_text, image_info_do.tag_text)
                all_text_vector = InitAllTextVectorUtil.textEmbeddingUtil.embed_to_vector(all_text)

                image_info_mapper.update_all_text_vector_by_file_path(file_path, all_text_vector)
                logger.info(f"写表成功:{file_path}")
            batch_start_id = image_info_do_list[-1].id
            image_info_do_list = image_info_mapper.query_by_id_range_batch(id=batch_start_id, batch_size=100)

    @staticmethod
    def __build_all_text(ocr_text, tag_text) -> str:
        return StringUtil.concat(tag_text, ",", ocr_text)


def init_log(log_dir: str, log_file_name: str):
    os.makedirs(log_dir, exist_ok=True)
    logging.config.dictConfig({
        "version": 1,
        "formatters": {
            "standard_formatter": {"format": "%(asctime)s [%(levelname)s] [%(threadName)s]-%(name)s %(module)s:%(lineno)d - %(message)s"}
        },
        "handlers": {
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": f"{log_dir}/{log_file_name}",
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
                "handlers": ["file", "console"],
                "level": "INFO",
                "propagate": False,
            }
        },
        "root": {"handlers": ["file", "console"], "level": "INFO"}
    })


if __name__ == "__main__":
    init_log("logs", "init_all_text_vector.log")

    InitAllTextVectorUtil.init(True)
