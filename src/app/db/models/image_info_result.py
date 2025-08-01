"""
Copyright © 2025-2025 tmx0103.  
Licensed under the Apache-2.0 License.  
For full terms, see the LICENSE file.  
image_info_result.py
"""
from src.app.db.models import Base


class ImageInfoResult(Base):
    __tablename__ = 'tb_image_info'
    __table_args__ = {'schema': 'dev'}

    id = None
    gmt_create = None
    gmt_modified = None
    file_gmt_modified = None

    file_path = None
    file_name = None
    file_sha256 = None

    ocr_text = None
    tag_text = None

    image_vector = None
    all_text_vector = None

    cosine_distance = None
