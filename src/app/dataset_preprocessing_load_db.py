"""
Copyright © 2025-2025 tmx0103.
Licensed under the Apache-2.0 License.
For full terms, see the LICENSE file.
dataset_preprocessing_load_db.py
"""
import os
import shutil

from PIL import Image
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from transformers import ChineseCLIPModel, ChineseCLIPProcessor

from src.app.log.logger import logger
from src.app.utils import sha256_util
from src.app.db.mapper.img_vector_mapper import ImgVectorMapper

if __name__ == "__main__":
    # 载入数据库
    load_dotenv()
    engine = create_engine(f"postgresql://"
                           f"{os.getenv('POSTGRESQL_USER')}:{os.getenv('POSTGRESQL_PASSWORD')}"
                           f"@{os.getenv('POSTGRESQL_HOST')}:{os.getenv('POSTGRESQL_PORT')}/{os.getenv('POSTGRESQL_DB')}")
    Session = sessionmaker(bind=engine)
    with Session() as session:
        img_vector_mapper = ImgVectorMapper(session)
        model = ChineseCLIPModel.from_pretrained("OFA-Sys/chinese-clip-vit-huge-patch14").to("cuda")
        processor = ChineseCLIPProcessor.from_pretrained("OFA-Sys/chinese-clip-vit-huge-patch14")
        for file_dir, dirs, file_names in os.walk(os.path.join("../app/resources", "dataset")):
            for file_name in file_names:
                file_relative_path = os.path.join(file_dir, file_name)
                logger.info(f"处理：{file_relative_path}")

                # 计算当前文件的sha256
                file_sha256 = sha256_util.sha256_file(file_relative_path)
                # 读取数据库中是否存在该文件，如果存在则跳过
                img_vector_do = img_vector_mapper.query_by_file_dir_and_file_name(file_dir, file_name)
                if img_vector_do:
                    logger.info(f"该图已处理过：{file_relative_path}")
                    continue
                # 读取数据库中是否存在与该文件一致的哈希，如果存在则移除该文件
                img_vector_do = img_vector_mapper.query_by_file_sha256(file_sha256)
                if img_vector_do:
                    # 把已存入数据库的图片复制到重复哈希图目录下
                    os.makedirs('重复哈希图', exist_ok=True)
                    original_file_path = os.path.join(img_vector_do.file_dir, img_vector_do.file_name)
                    shutil.copy2(original_file_path,
                                 os.path.join('重复哈希图',
                                              f"{file_sha256}_原图_{original_file_path.replace('/', '-').replace('\\', '-')}"))

                    # 把当前图移动到重复哈希图目录下
                    logger.info(f"该图有完全相似图：{file_relative_path}")
                    os.rename(file_relative_path,
                              os.path.join('重复哈希图', f"{file_sha256}_重复图_{file_relative_path.replace('/', '-').replace('\\', '-')}"))

                else:
                    with Image.open(file_relative_path) as image:
                        # 计算当前图片的特征向量
                        try:
                            image = Image.open(file_relative_path)
                            inputs = processor(images=image, return_tensors="pt").to("cuda")
                            image_feature = model.get_image_features(**inputs)
                            image_feature = image_feature / image_feature.norm(p=2, dim=-1, keepdim=True)  # normalize
                            image_feature = image_feature.cpu().detach().numpy()
                            image_feature_pg_str = "[" + ",".join([str(x) for x in image_feature[0]]) + "]"
                        except Exception as e:
                            logger.warning(f"处理图片出错：{file_relative_path}")
                            logger.warning(e)
                            # 把已存入数据库的图片复制到重复哈希图目录下
                            os.makedirs(os.path.join('异常图', file_dir), exist_ok=True)
                            os.rename(file_relative_path, os.path.join('异常图', file_dir, file_name))
                            continue

                    img_vector_mapper.insert(file_dir=file_dir, file_name=file_name, file_sha256=file_sha256,
                                             img_vector=image_feature_pg_str,
                                             ocr_text=None)
                    logger.info(f"写表成功:{file_relative_path}")
