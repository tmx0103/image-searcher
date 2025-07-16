"""
Copyright © 2025-2025 tmx0103.  
Licensed under the Apache-2.0 License.  
For full terms, see the LICENSE file.  
run.py
"""
import logging.config
import os

if __name__ == '__main__':
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    LOGGING_CONFIG = {
        "version": 1,
        "formatters": {"standard_formatter": {"format": "%(asctime)s [%(levelname)s] %(module)s:%(lineno)d - %(message)s"}},
        "handlers": {
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": "logs/app.log",
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
                "handlers": ["file", "console"], "level": "DEBUG",
            }
        },
        "root": {"handlers": ["file", "console"], "level": "DEBUG"}
    }
    logging.config.dictConfig(LOGGING_CONFIG)
    logger = logging.getLogger(__name__)
    from src.app import run

    run()
