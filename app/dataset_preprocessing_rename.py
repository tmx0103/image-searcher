"""
Copyright © 2025-2025 tmx0103.
Licensed under the Apache-2.0 License.
For full terms, see the LICENSE file.
dataset_preprocessing_rename.py
"""
import os
import uuid
from datetime import datetime

from PIL import Image
from PIL.ExifTags import TAGS

from app.utils import sha256_util


def rename(path: str):
    for file_dir, dirs, file_names in os.walk(path):
        for file_name in file_names:
            source_path = os.path.join(file_dir, file_name)
            print("原始路径", source_path)

            # 获取文件扩展名，如果不是图片文件则将该文件移动到指定目录
            ext = os.path.splitext(file_name)[1].lower()
            if ext not in [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"]:
                target_dir = os.path.join('非图', file_dir)
                os.makedirs(target_dir, exist_ok=True)
                os.rename(source_path, os.path.join(target_dir, file_name))
                continue

            # 获得文件的拍摄日期，如果读取异常，则将该文件移动到指定目录
            try:
                photo_date = get_photo_date(source_path)
            except Exception as e:
                print(e)
                target_dir = os.path.join('异常', file_dir)
                os.makedirs(target_dir, exist_ok=True)
                os.rename(source_path, os.path.join(target_dir, file_name))
                continue

            if photo_date is None:
                # 获得文件的修改日期
                modified_time = datetime.fromtimestamp(os.path.getmtime(source_path)).strftime("%Y%m%d-%H%M%S")
            else:
                modified_time = photo_date.strftime("%Y%m%d-%H%M%S")
            # print(modified_time)

            # 生成sha256值的前16位
            sha256p16 = sha256_util.sha256_file(source_path)[:16]

            # 文件重命名，如果文件已存在，则增加“重复图”文件名前缀
            target_path = os.path.join(file_dir, f"{modified_time}_{sha256p16}{ext}")
            print("目标路径", target_path)
            try:
                os.rename(source_path, target_path)
            except FileExistsError:
                # 生成sha256值的前16位
                uid = str(uuid.uuid4()).replace("-", "")[:16]
                target_dir = os.path.join('重复图', file_dir)
                print("文件已存在，新的目标路径", target_dir)
                os.makedirs(target_dir, exist_ok=True)
                os.rename(source_path, os.path.join(target_dir, f"重复图{modified_time}_{sha256p16}_{uid}{ext}"))


def get_photo_date(image_path):
    image = Image.open(image_path)
    info = image.getexif()
    if info is not None:
        for tag, value in info.items():
            decoded_tag = TAGS.get(tag, tag)
            if decoded_tag == 'DateTime':
                print(value)
                try:
                    date_time = datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
                    return date_time
                except ValueError:
                    return None
    return None


if __name__ == "__main__":
    rename(os.path.join("resources", "dataset"))
