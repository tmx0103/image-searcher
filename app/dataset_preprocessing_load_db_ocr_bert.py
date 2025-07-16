"""
Copyright © 2025-2025 tmx0103.
Licensed under the Apache-2.0 License.
For full terms, see the LICENSE file.
dataset_preprocessing_load_db_ocr_bert.py
"""
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.bert.chinese_bert import ChineseBert
from app.utils import sha256_util
from models.img_vector import ImgVectorMapper

if __name__ == "__main__":
    # 载入数据库
    load_dotenv()
    engine = create_engine(f"postgresql://"
                           f"{os.getenv('POSTGRESQL_USER')}:{os.getenv('POSTGRESQL_PASSWORD')}"
                           f"@{os.getenv('POSTGRESQL_HOST')}:{os.getenv('POSTGRESQL_PORT')}/{os.getenv('POSTGRESQL_DB')}")
    Session = sessionmaker(bind=engine)
    with (Session() as session):
        img_vector_mapper = ImgVectorMapper(session)
        chinese_bert = ChineseBert()
        for file_dir, dirs, file_names in os.walk(os.path.join("resources", "dataset")):
            for file_name in file_names:
                file_relative_path = os.path.join(file_dir, file_name)
                print(f"处理：{file_relative_path}")

                # 计算当前文件的sha256
                file_sha256 = sha256_util.sha256_file(file_relative_path)

                # 读取数据库中是否存在与该文件一致的哈希，如果存在则移除该文件
                img_vector_do = img_vector_mapper.query_by_file_sha256(file_sha256)
                if img_vector_do \
                        and img_vector_do.ocr_text is not None and img_vector_do.ocr_text != "" \
                        and img_vector_do.ocr_text_sentence_vec is None:
                    ocr_text_sentence_vec = chinese_bert.embed_to_sentence_vec(img_vector_do.ocr_text)
                    ocr_text_sentence_vec_str = "[" + ",".join([str(x) for x in ocr_text_sentence_vec]) + "]"
                    img_vector_mapper.update_ocr_text_sentence_vec_by_file_sha256(file_sha256, ocr_text_sentence_vec_str)
                    print(f"已完成处理：{file_relative_path}")
                else:
                    print(f"跳过：{file_relative_path}")
