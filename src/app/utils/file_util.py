"""
Copyright © 2025-2025 tmx0103.  
Licensed under the Apache-2.0 License.  
For full terms, see the LICENSE file.  
file_util.py
"""
import os
from datetime import datetime
from enum import Enum

from src.app.log.logger import logger


class FileUtil:
    @staticmethod
    def find_all_files_list(path: str) -> list:
        file_info_list = []
        for file_dir, dirs, file_names in os.walk(path):
            for file_name in file_names:
                file_info = FileInfo()
                source_path = os.path.abspath(os.path.join(file_dir, file_name))
                logger.info("遍历文件：%s", source_path)
                name, ext = os.path.splitext(file_name)
                file_info.sourcePath = source_path
                file_info.name = name
                file_info.ext = ext.lstrip(".")
                file_info.createTime = datetime.fromtimestamp(os.path.getctime(source_path))
                file_info.modifiedTime = datetime.fromtimestamp(os.path.getmtime(source_path))
                file_info_list.append(file_info)
        return file_info_list

    @staticmethod
    def find_all_files_dict(path: str) -> list:
        file_info_list = []
        for file_dir, dirs, file_names in os.walk(path):
            for file_name in file_names:
                file_info = FileInfo()
                source_path = os.path.abspath(os.path.join(file_dir, file_name))
                logger.info("遍历文件：%s", source_path)
                name, ext = os.path.splitext(file_name)
                file_info.sourcePath = source_path
                file_info.name = name
                file_info.ext = ext.lstrip(".")
                file_info.createTime = datetime.fromtimestamp(os.path.getctime(source_path))
                file_info_list.append(file_info)
        return file_info_list


class FileInfo:
    def __init__(self):
        self.sourcePath = None
        self.name = None
        self.ext = None
        self.createTime = None
        self.modifiedTime = None
        self.sha256 = None
        self.status = FileStatusEnum.NORMAL

    def get_full_name(self):
        return self.name + "." + self.ext

    def __lt__(self, other):
        if self.modifiedTime == other.modifiedTime:
            return self.createTime < other.createTime
        else:
            return self.modifiedTime < other.modifiedTime


class FileStatusEnum(Enum):
    NORMAL = "正常"
    DUPLICATE = "重复"
    INVALID = "无效"
