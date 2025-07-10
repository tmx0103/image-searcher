"""
Copyright © 2025-2025 tmx0103.
Licensed under the Apache-2.0 License.
For full terms, see the LICENSE file.
"""
from datetime import datetime

from sqlalchemy import Column, BigInteger, TIMESTAMP, String, bindparam, Float, Integer
from sqlalchemy.orm import Session
from sqlalchemy.sql import text

from app.models import Base


class ImgVectorDO(Base):
    __tablename__ = 'tb_img_vector'
    __table_args__ = {'schema': 'dev'}
    id = Column(BigInteger, primary_key=True)
    gmt_create = Column(TIMESTAMP)
    img_vec = Column(String)
    file_dir = Column(String)
    file_gmt_modified = Column(TIMESTAMP)
    file_name = Column(String)
    file_sha256 = Column(String)
    cosine_distance = Column(Float)


class ImgVectorMapper:
    def __init__(self, session: Session):
        self.session = session
        self.sql_template = text("""
                                 SELECT id,
                                        file_dir,
                                        file_name,
                                        img_vec <=> :query_vec AS cosine_distance
                                 FROM dev.tb_img_vector
                                 WHERE img_vec <=> :query_vec < :max_cosine_distance
                                 ORDER BY img_vec <=> :query_vec
                                 LIMIT :limit
                                 """)

    def insert(self, img_vector, file_dir, file_name, file_sha256):
        img_vector_do = ImgVectorDO()
        img_vector_do.gmt_create = datetime.now()
        img_vector_do.img_vec = img_vector
        img_vector_do.file_dir = file_dir
        img_vector_do.file_gmt_modified = datetime.strptime(file_name.split('_')[0], "%Y%m%d-%H%M%S")
        img_vector_do.file_name = file_name
        img_vector_do.file_sha256 = file_sha256
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

    def search(self, img_vector: str, cosine_similarity: float, limit: int):
        max_cosine_distance = 1 - cosine_similarity
        orm_sql = self.session.query(ImgVectorDO).from_statement(
            self.sql_template.bindparams(
                bindparam("query_vec", value=img_vector),
                bindparam("max_cosine_distance", value=max_cosine_distance),
                bindparam("limit", value=limit))
            .columns(ImgVectorDO.id, ImgVectorDO.file_dir, ImgVectorDO.file_name, ImgVectorDO.cosine_distance)
        )
        return orm_sql.all()
