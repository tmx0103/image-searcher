"""
Copyright © 2025-2025 tmx0103.  
Licensed under the Apache-2.0 License.  
For full terms, see the LICENSE file.  
img_vector_mapper.py
"""
from datetime import datetime

from sqlalchemy import text, bindparam
from sqlalchemy.orm import Session

from src.app.db.models import ImgVectorDO


class ImgVectorMapper:
    def __init__(self, session: Session):
        self.session = session
        self.sql_template_img_vector_search = text("""
                                                   SELECT id,
                                                          file_dir,
                                                          file_name,
                                                          img_vec <=> :query_vec AS cosine_distance
                                                   FROM dev.tb_img_vector
                                                   WHERE img_vec <=> :query_vec < :max_cosine_distance
                                                   ORDER BY img_vec <=> :query_vec
                                                   LIMIT :limit
                                                   """)
        self.sql_template_ocr_text_sentence_vector_search = text("""
                                                                 SELECT id,
                                                                        file_dir,
                                                                        file_name,
                                                                        ocr_text_sentence_vec <=> :query_vec AS cosine_distance
                                                                 FROM dev.tb_img_vector
                                                                 WHERE ocr_text_sentence_vec <=> :query_vec < :max_cosine_distance
                                                                 ORDER BY ocr_text_sentence_vec <=> :query_vec
                                                                 LIMIT :limit
                                                                 """)
        self.sql_template_text_search = text("""
                                             SELECT id,
                                                    file_dir,
                                                    file_name
                                             FROM dev.tb_img_vector
                                             WHERE to_tsvector('chinese_ocr', ocr_text) @@ to_tsquery('chinese_ocr', :search_text)
                                             ORDER BY id
                                             LIMIT :limit
                                             """)

    def insert(self, file_dir, file_name, file_sha256, img_vector, ocr_text):
        img_vector_do = ImgVectorDO()
        img_vector_do.gmt_create = datetime.now()
        img_vector_do.file_dir = file_dir
        img_vector_do.file_gmt_modified = datetime.strptime(file_name.split('_')[0], "%Y%m%d-%H%M%S")
        img_vector_do.file_name = file_name
        img_vector_do.file_sha256 = file_sha256
        img_vector_do.img_vec = img_vector
        img_vector_do.ocr_text = ocr_text
        self.session.add(img_vector_do)
        self.session.commit()

    def query_by_file_sha256(self, file_sha256) -> ImgVectorDO | None:
        img_vector_do = self.session.query(ImgVectorDO).filter(ImgVectorDO.file_sha256 == file_sha256).first()
        return img_vector_do

    def query_by_file_dir_and_file_name(self, file_dir, file_name) -> ImgVectorDO | None:
        img_vector_do = self.session.query(ImgVectorDO).filter(ImgVectorDO.file_dir == file_dir,
                                                               ImgVectorDO.file_name == file_name).first()
        return img_vector_do

    def update_file_dir_by_file_name(self, file_name, file_dir):
        self.session.query(ImgVectorDO).filter(ImgVectorDO.file_name == file_name).update({ImgVectorDO.file_dir: file_dir})
        self.session.commit()

    def update_ocr_text_by_file_sha256(self, file_sha256, ocr_text):
        self.session.query(ImgVectorDO).filter(ImgVectorDO.file_sha256 == file_sha256).update({ImgVectorDO.ocr_text: ocr_text})
        self.session.commit()

    def update_ocr_text_sentence_vec_by_file_sha256(self, file_sha256, ocr_text_sentence_vec):
        self.session.query(ImgVectorDO).filter(ImgVectorDO.file_sha256 == file_sha256).update(
            {ImgVectorDO.ocr_text_sentence_vec: ocr_text_sentence_vec})
        self.session.commit()

    def search(self, img_vector: str, cosine_similarity: float, limit: int):
        max_cosine_distance = 1 - cosine_similarity
        orm_sql = self.session.query(ImgVectorDO).from_statement(
            self.sql_template_img_vector_search.bindparams(
                bindparam("query_vec", value=img_vector),
                bindparam("max_cosine_distance", value=max_cosine_distance),
                bindparam("limit", value=limit))
            .columns(ImgVectorDO.id, ImgVectorDO.file_dir, ImgVectorDO.file_name, ImgVectorDO.cosine_distance)
        )
        return orm_sql.all()

    def search_by_text(self, search_text: str, limit: int):
        orm_sql = self.session.query(ImgVectorDO).from_statement(
            self.sql_template_text_search.bindparams(
                bindparam("search_text", value=search_text),
                bindparam("limit", value=limit))
            .columns(ImgVectorDO.id, ImgVectorDO.file_dir, ImgVectorDO.file_name)
        )
        return orm_sql.all()

    def search_by_ocr_text_sentence_vector(self, text_vector: str, cosine_similarity: float, limit: int):
        max_cosine_distance = 1 - cosine_similarity
        orm_sql = self.session.query(ImgVectorDO).from_statement(
            self.sql_template_ocr_text_sentence_vector_search.bindparams(
                bindparam("query_vec", value=text_vector),
                bindparam("max_cosine_distance", value=max_cosine_distance),
                bindparam("limit", value=limit))
            .columns(ImgVectorDO.id, ImgVectorDO.file_dir, ImgVectorDO.file_name, ImgVectorDO.cosine_distance)
        )
        return orm_sql.all()
