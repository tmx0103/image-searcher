"""
Copyright © 2025-2025 tmx0103.  
Licensed under the Apache-2.0 License.  
For full terms, see the LICENSE file.  
run.py
"""
import logging.config
import os

from dotenv import load_dotenv

load_dotenv()


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
        "root": {"handlers": ["file", "console"], "level": "DEBUG"}
    })


if __name__ == '__main__':
    init_log("logs", "app.log")
    try:
        from src.app import run

        run()
    except Exception as e:
        logging.error(e, exc_info=True)
