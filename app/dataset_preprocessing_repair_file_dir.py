"""
Copyright © 2025-2025 tmx0103.
Licensed under the Apache-2.0 License.
For full terms, see the LICENSE file.
dataset_preprocessing_repair_file_dir.py
"""
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.img_vector import ImgVectorMapper

if __name__ == "__main__":
    # 载入数据库
    load_dotenv()
    engine = create_engine(f"postgresql://"
                           f"{os.getenv('POSTGRESQL_USER')}:{os.getenv('POSTGRESQL_PASSWORD')}"
                           f"@{os.getenv('POSTGRESQL_HOST')}:{os.getenv('POSTGRESQL_PORT')}/{os.getenv('POSTGRESQL_DB')}")
    Session = sessionmaker(bind=engine)
    with Session() as session:
        img_vector_mapper = ImgVectorMapper(session)

        for file_dir, dirs, file_names in os.walk(os.path.join("resources", "dataset")):
            for file_name in file_names:
                file_relative_path = os.path.join(file_dir, file_name)
                print(f"处理：{file_relative_path}")

                # 读取数据库中是否存在路径完全一致的文件，如果存在则跳过
                img_vector_do = img_vector_mapper.query_by_file_dir_and_file_name(file_dir, file_name)
                if img_vector_do:
                    print(f"该图已处理过：{file_relative_path}")
                    continue
                # 读取数据库中是否存在名字完全一致的文件，如果存在则更新路径
                img_vector_mapper.update_file_dir_by_file_name(file_name, file_dir)
                print(f"更新路径：{file_dir}，文件名：{file_name}")
