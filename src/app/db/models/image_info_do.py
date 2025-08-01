"""
Copyright © 2025-2025 tmx0103.
Licensed under the Apache-2.0 License.
For full terms, see the LICENSE file.
image_info_do.py
"""

from sqlalchemy import Column, BigInteger, TIMESTAMP, String

from src.app.db.models import Base


class ImageInfoDO(Base):
    __tablename__ = 'tb_image_info'
    __table_args__ = {'schema': 'dev'}

    id = Column(BigInteger, primary_key=True)
    gmt_create = Column(TIMESTAMP)
    gmt_modified = Column(TIMESTAMP)
    file_gmt_modified = Column(TIMESTAMP)

    file_path = Column(String)
    file_name = Column(String)
    file_sha256 = Column(String)

    ocr_text = Column(String)
    tag_text = Column(String)

    image_vector = Column(String)
    all_text_vector = Column(String)
