"""
Copyright © 2025-2025 tmx0103.
Licensed under the Apache-2.0 License.
For full terms, see the LICENSE file.
run_delete_incomplete_entries.py
该脚本的作用是，将数据库中未完善的数据删除。

"""
import logging.config
import os

from dotenv import load_dotenv

from src.app.utils.sha256_util import Sha256Util

load_dotenv()
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.app.log.logger import logger
from src.app.db.mapper.image_info_mapper import ImageInfoMapper


class DeleteIncompleteEntriesUtil:
    engine = create_engine(f"postgresql://"
                           f"{os.getenv('POSTGRESQL_USER')}:{os.getenv('POSTGRESQL_PASSWORD')}"
                           f"@{os.getenv('POSTGRESQL_HOST')}:{os.getenv('POSTGRESQL_PORT')}/{os.getenv('POSTGRESQL_DB')}")
    Session = sessionmaker(bind=engine)

    @staticmethod
    def delete():
        with DeleteIncompleteEntriesUtil.Session() as session:
            image_info_mapper = ImageInfoMapper(session)
        # 批量处理，每次从数据库中取100条
        batch_start_id = -1
        image_info_do_list = image_info_mapper.query_by_id_range_batch(id=batch_start_id, batch_size=100)
        while image_info_do_list is not None and len(image_info_do_list) > 0:
            for image_info_do in image_info_do_list:
                file_path = image_info_do.file_path
                logger.info(f"初始化：{file_path}")
                if not os.path.exists(file_path) or not os.path.isfile(file_path):
                    logger.info(f"文件不存在，删除记录：{file_path}")
                    image_info_mapper.delete_by_file_path(file_path)

                file_sha256 = Sha256Util.sha256_file(file_path)
                if not image_info_do.file_sha256 or file_sha256 != image_info_do.file_sha256:
                    logger.info(f"文件sha256不一致，删除记录：{file_path}")
                    image_info_mapper.delete_by_file_path(file_path)
                    continue
                if not image_info_do.file_gmt_modified or not image_info_do.file_name \
                        or image_info_do.ocr_text is None or not image_info_do.image_vector or not image_info_do.all_text_vector:
                    logger.info(f"文件修改时间、文件名、OCR文本、图片向量、有文本向量异常或为空，删除记录：{file_path}")
                    image_info_mapper.delete_by_file_path(file_path)
                    continue

                logger.info(f"写表成功:{file_path}")


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
                "level": "DEBUG",
                "propagate": False,
            }
        },
        "root": {"handlers": ["file", "console"], "level": "DEBUG"}
    })


if __name__ == "__main__":
    init_log("logs", "delete_incomplete_entries.log")

    DeleteIncompleteEntriesUtil.delete()
