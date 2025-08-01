"""
Copyright © 2025-2025 tmx0103.
Licensed under the Apache-2.0 License.
For full terms, see the LICENSE file.
run_init_db.py
第一次运行GUI应用前，【必须运行该脚本】。
该脚本的作用是，将指定目录（包括子目录）的所有图片文件基本信息载入数据库中。
可选：
【高危操作】清除数据库中所有数据
"""
import logging.config
import os

from dotenv import load_dotenv

from src.app.utils.image_util import ImageUtil

load_dotenv()
from src.app.utils.file_util import FileUtil
from src.app.utils.sha256_util import Sha256Util

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.app.log.logger import logger
from src.app.db.mapper.image_info_mapper import ImageInfoMapper


class InitDBUtil:
    engine = create_engine(f"postgresql://"
                           f"{os.getenv('POSTGRESQL_USER')}:{os.getenv('POSTGRESQL_PASSWORD')}"
                           f"@{os.getenv('POSTGRESQL_HOST')}:{os.getenv('POSTGRESQL_PORT')}/{os.getenv('POSTGRESQL_DB')}")
    Session = sessionmaker(bind=engine)

    @staticmethod
    def init(path: str, clear_db: bool = False):
        with InitDBUtil.Session() as session:
            image_info_mapper = ImageInfoMapper(session)
        if clear_db:
            logger.warning("清空数据库")
            image_info_mapper.truncate()
        # 遍历path文件夹中所有文件，并添加到文件列表
        file_info_list = FileUtil.find_all_files_list(path)
        for file_info in file_info_list:
            file_path = file_info.sourcePath
            logger.info(f"初始化：{file_path}")

            # 计算当前文件的sha256
            file_sha256 = Sha256Util.sha256_file(file_path)
            # 读取数据库中是否存在该文件，如果存在则跳过
            image_info_do = image_info_mapper.query_by_file_path(file_path)
            if image_info_do and image_info_do.file_sha256 == file_sha256:
                logger.info(f"图片已初始化过：{file_path}")
                continue
            # 数据异常，先删除数据库中的记录
            if image_info_do:
                image_info_mapper.delete_by_file_path(file_path)
                logger.info(f"数据库记录异常，删除记录：{file_path}")

            # 读取图片的拍摄时间，如果不存在或者图片异常则使用修改时间。
            photo_date = ImageUtil.get_photo_date(file_info.sourcePath)
            if photo_date:
                file_info.modifiedTime = photo_date
                logger.info(f"使用文件拍摄时间：{file_info.modifiedTime}")
            # 插入新数据
            image_info_mapper.insert(file_gmt_modified=file_info.modifiedTime,
                                     file_path=file_path,
                                     file_name=file_info.get_full_name(),
                                     file_sha256=file_sha256)
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
    init_log("logs", "init_db.log")
    paths = os.getenv("IMAGE_PATHS").split(",")
    for path in paths:
        InitDBUtil.init(path, True)
