"""
Copyright © 2025-2025 tmx0103.  
Licensed under the Apache-2.0 License.  
For full terms, see the LICENSE file.  
image_util.py
"""
from datetime import datetime

from PIL import Image
from PIL.ExifTags import TAGS

from src.app.log.logger import logger


class ImageUtil:
    @staticmethod
    def get_photo_date(image_path) -> datetime | None:
        try:
            image = Image.open(image_path)
            info = image.getexif()
            if info is not None:
                for tag, value in info.items():
                    decoded_tag = TAGS.get(tag, tag)
                    if decoded_tag == 'DateTime':
                        logger.info(value)
                        try:
                            return datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
                        except ValueError:
                            return None
        except Exception as e:
            logger.error(e, exc_info=True)
        return None

    @staticmethod
    def get_image_real_ext(file_path, allowed_formats=('JPEG', 'PNG', 'GIF', 'BMP', 'WEBP')) -> str | None:
        """ 获得图片文件的扩展名。

        Args:
            file_path: 文件路径
            allowed_formats: 允许的图片扩展名白名单

        Returns:
            如果图片校验成功，并且在白名单内，返回扩展名（小写）。
            如果图片校验失败，或者不在白名单内，返回None
        """
        try:
            with Image.open(file_path) as img:
                img.verify()  # 验证文件完整性
                if img.format in allowed_formats:
                    if img.format == "JPEG":
                        return "jpg"
                    else:
                        return img.format.lower()
        except Exception as e:
            logger.error(e, exc_info=True)
        return None
