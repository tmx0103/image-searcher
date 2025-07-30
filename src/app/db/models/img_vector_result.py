"""
Copyright © 2025-2025 tmx0103.  
Licensed under the Apache-2.0 License.  
For full terms, see the LICENSE file.  
img_vector_result.py
"""
from src.app.db.models import Base


class ImgVectorResult(Base):
    __tablename__ = 'tb_img_vector'
    __table_args__ = {'schema': 'dev'}
    id = None
    gmt_create = None
    file_dir = None
    file_gmt_modified = None
    file_name = None
    file_sha256 = None

    ocr_text = None
    tag_text = None

    img_vec = None
    all_text_vec = None

    cosine_distance = None
