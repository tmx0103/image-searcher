"""
Copyright © 2025-2025 tmx0103.
Licensed under the Apache-2.0 License.
For full terms, see the LICENSE file.
__init__.py
"""
from sqlalchemy.orm import declarative_base

from ...log.logger import logger

Base = declarative_base()

from .image_info_do import ImageInfoDO

logger.info("载入数据库模块...")
