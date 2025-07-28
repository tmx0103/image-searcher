"""
Copyright © 2025-2025 tmx0103.
Licensed under the Apache-2.0 License.
For full terms, see the LICENSE file.
run_update_all_in_one_vector.py
"""
import logging.config
import os

from dotenv import load_dotenv

load_dotenv()

from src.app.log.logger import logger
from src.app.service.repo_vector_service import RepoVectorService
from src.app.utils import sha256_util

if __name__ == "__main__":
    LOGGING_CONFIG = {
        "version": 1,
        "formatters": {"standard_formatter": {"format": "%(asctime)s [%(levelname)s] %(module)s:%(lineno)d - %(message)s"}},
        "handlers": {
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": "../logs/run_update_all_in_one_vector.log",
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

    repo_vector_service = RepoVectorService.get_instance()
    for file_dir, dirs, file_names in os.walk(os.path.join("resources", "dataset")):
        for file_name in file_names:
            file_relative_path = os.path.join(file_dir, file_name)
            logger.info(f"处理：{file_relative_path}")

            # 计算当前文件的sha256
            file_sha256 = sha256_util.sha256_file(file_relative_path)

            repo_vector_service.update_all_in_one_vector(file_sha256)
