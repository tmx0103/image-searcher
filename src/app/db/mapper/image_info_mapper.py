"""
Copyright © 2025-2025 tmx0103.  
Licensed under the Apache-2.0 License.  
For full terms, see the LICENSE file.  
image_info_mapper.py
"""
from datetime import datetime

from sqlalchemy import text, bindparam
from sqlalchemy.orm import Session

from src.app.db.models import ImageInfoDO
from src.app.db.models.image_info_result import ImageInfoResult


class ImageInfoMapper:
    def __init__(self, session: Session):
        self.session = session
        self.sql_template_image_vector_search \
            = text("""
                   SELECT id,
                          file_path,
                          file_name,
                          file_sha256,
                          image_vector <=> :query_vec AS cosine_distance
                   FROM dev.tb_image_info
                   WHERE image_vector <=> :query_vec < :max_cosine_distance
                   ORDER BY image_vector <=> :query_vec
                   LIMIT :limit
                   """)
        self.sql_template_text_search \
            = text("""
                   SELECT id,
                          file_path,
                          file_name,
                          file_sha256
                   FROM dev.tb_image_info
                   WHERE to_tsvector('chinese_ocr', ocr_text) @@ to_tsquery('chinese_ocr', :search_text)
                   ORDER BY id
                   LIMIT :limit
                   """)
        self.sql_template_all_text_vector_search \
            = text("""
                   SELECT id,
                          file_path,
                          file_name,
                          file_sha256,
                          all_text_vector <=> :query_vec AS cosine_distance
                   FROM dev.tb_image_info
                   WHERE all_text_vector <=> :query_vec < :max_cosine_distance
                   ORDER BY all_text_vector <=> :query_vec
                   LIMIT :limit
                   """)

    def insert(self, file_gmt_modified, file_path, file_name, file_sha256):
        image_info_do = ImageInfoDO()
        image_info_do.gmt_create = datetime.now()
        image_info_do.gmt_modified = datetime.now()
        image_info_do.file_gmt_modified = file_gmt_modified
        image_info_do.file_path = file_path
        image_info_do.file_name = file_name
        image_info_do.file_sha256 = file_sha256
        image_info_do.ocr_text = None
        image_info_do.tag_text = None
        image_info_do.image_vector = None
        image_info_do.all_text_vector = None
        self.session.add(image_info_do)
        self.session.commit()

    def delete_by_file_path(self, file_path):
        self.session.query(ImageInfoDO).filter(ImageInfoDO.file_path == file_path).delete()
        self.session.commit()

    def truncate(self):
        self.session.execute(text("TRUNCATE TABLE dev.tb_image_info"))
        self.session.commit()

    def query_by_id_range_batch(self, id: int, batch_size: int = 100):
        return (self.session.query(ImageInfoDO)
                .filter(ImageInfoDO.id > id).order_by(ImageInfoDO.id.asc())
                .limit(batch_size)
                .all())

    def query_by_file_sha256(self, file_sha256) -> ImageInfoDO | None:
        image_info_do = self.session.query(ImageInfoDO).filter(ImageInfoDO.file_sha256 == file_sha256).first()
        return image_info_do

    def query_by_file_path(self, file_path) -> ImageInfoDO | None:
        image_info_do = self.session.query(ImageInfoDO).filter(ImageInfoDO.file_path == file_path).first()
        return image_info_do

    def update_image_vector_by_file_sha256(self, file_sha256, image_vector):
        self.session.query(ImageInfoDO).filter(ImageInfoDO.file_sha256 == file_sha256).update({ImageInfoDO.image_vector: image_vector})
        self.session.commit()

    def update_ocr_text_by_file_path(self, file_path, ocr_text):
        self.session.query(ImageInfoDO).filter(ImageInfoDO.file_path == file_path).update({ImageInfoDO.ocr_text: ocr_text})
        self.session.commit()

    def update_tag_text_by_file_path(self, file_path, tag_text):
        self.session.query(ImageInfoDO).filter(ImageInfoDO.file_path == file_path).update({ImageInfoDO.tag_text: tag_text})
        self.session.commit()

    def update_image_vector_by_file_path(self, file_path, image_vector):
        vector_str = ImageInfoMapper.__vector_to_pg_str(image_vector)
        self.session.query(ImageInfoDO).filter(ImageInfoDO.file_path == file_path).update({ImageInfoDO.image_vector: vector_str})
        self.session.commit()

    def update_all_text_vector_by_file_path(self, file_path, all_text_vector):
        vector_str = ImageInfoMapper.__vector_to_pg_str(all_text_vector)
        self.session.query(ImageInfoDO).filter(ImageInfoDO.file_path == file_path).update({ImageInfoDO.all_text_vector: vector_str})
        self.session.commit()

    def search_by_image_vector(self, image_vector, cosine_similarity: float, limit: int):
        vector_str = ImageInfoMapper.__vector_to_pg_str(image_vector)
        max_cosine_distance = 1 - cosine_similarity
        execute_result = self.session.execute(self.sql_template_image_vector_search.bindparams(
            bindparam("query_vec", value=vector_str),
            bindparam("max_cosine_distance", value=max_cosine_distance),
            bindparam("limit", value=limit))).mappings().all()

        result = [ImageInfoResult(**row) for row in execute_result]
        return result

    def search_by_all_text_vector(self, text_vector, cosine_similarity: float, limit: int):
        vector_str = ImageInfoMapper.__vector_to_pg_str(text_vector)
        max_cosine_distance = 1 - cosine_similarity

        execute_result = self.session.execute(self.sql_template_all_text_vector_search.bindparams(
            bindparam("query_vec", value=vector_str),
            bindparam("max_cosine_distance", value=max_cosine_distance),
            bindparam("limit", value=limit))).mappings().all()

        result = [ImageInfoResult(**row) for row in execute_result]
        return result

    @staticmethod
    def __vector_to_pg_str(vector):
        return "[" + ",".join([str(x) for x in vector]) + "]"
