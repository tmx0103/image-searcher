"""
Copyright © 2025-2025 tmx0103.
Licensed under the Apache-2.0 License.
For full terms, see the LICENSE file.
img_vector_do.py
"""

from sqlalchemy import Column, BigInteger, TIMESTAMP, String

from src.app.db.models import Base


class ImgVectorDO(Base):
    __tablename__ = 'tb_img_vector'
    __table_args__ = {'schema': 'dev'}
    id = Column(BigInteger, primary_key=True)
    gmt_create = Column(TIMESTAMP)
    file_dir = Column(String)
    file_gmt_modified = Column(TIMESTAMP)
    file_name = Column(String)
    file_sha256 = Column(String)

    ocr_text = Column(String)
    tag_text = Column(String)

    img_vec = Column(String)
    all_text_vec = Column(String)
    all_in_one_vec = Column(String)

    cosine_distance = None
