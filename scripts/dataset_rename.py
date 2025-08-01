"""
Copyright © 2025-2025 tmx0103.
Licensed under the Apache-2.0 License.
For full terms, see the LICENSE file.
dataset_rename.py

【高危操作，注意数据备份】该脚本可以直接运行，将指定目录（包括子目录）下的图片文件重命名为"拍摄时间或修改时间_sha256前16位.扩展名"。
1、如果存在sha256相同的文件，那么修改时间靠后的文件将被移动到指定的异常目录中。这样，该脚本运行后，指定目录中每个文件的sha256值都是独一无二的。
2、重命名后的文件扩展名将是为文件实际格式所对应的扩展名。

可选：将非图片文件和读取异常的图片文件移动到异常目录中，或者保留不动。
"""
import logging.config
import os

from src.app.log.logger import logger
from src.app.utils.file_util import FileStatusEnum, FileUtil
from src.app.utils.image_util import ImageUtil
from src.app.utils.sha256_util import Sha256Util


class RenameUtil:
    @staticmethod
    def rename(path: str, except_dir: str | None = None, is_move_invalid_file: bool = False):
        # 遍历path文件夹中所有文件，并添加到文件列表
        file_info_list = FileUtil.find_all_files_list(path)
        # 读取文件信息并标记分组
        result_duplicate_file_list, result_invalid_file_list, result_normal_file_list = RenameUtil.__group_files(file_info_list)

        # 【高危操作】将标记为非图片文件、读取异常的图片文件、重复文件移动到异常目录中
        if except_dir:
            os.makedirs(except_dir, exist_ok=True)
            if is_move_invalid_file:
                for file_info in result_invalid_file_list:
                    original_path = file_info.sourcePath
                    target_name = f"无效-{file_info.sourcePath.replace(":", "").replace("\\", "-").replace("/", "-")}"
                    logger.info(f"重命名文件：%s -> %s", original_path, target_name)
                    os.rename(file_info.sourcePath, os.path.join(except_dir, target_name))
            for file_info in result_duplicate_file_list:
                original_path = file_info.sourcePath
                target_name = f"重复-{file_info.sourcePath.replace(":", "").replace("\\", "-").replace("/", "-")}"
                logger.info(f"重命名文件：%s -> %s", original_path, target_name)
                os.rename(file_info.sourcePath, os.path.join(except_dir, target_name))
        # 【高危操作】将正常文件重命名
        for file_info in result_normal_file_list:
            original_path = file_info.sourcePath
            target_dir = os.path.dirname(file_info.sourcePath)
            target_name = file_info.modifiedTime.strftime("%Y%m%d-%H%M%S") + "_" + file_info.sha256[:16] + "." + file_info.ext
            target_path = os.path.join(target_dir, target_name)
            if original_path == target_path:
                logger.info(f"文件无需重命名：%s", original_path)
            else:
                logger.info(f"重命名文件：%s -> %s", original_path, target_name)
                os.rename(file_info.sourcePath, os.path.join(target_dir, target_name))

    @staticmethod
    def __group_files(file_info_list: list) -> tuple:
        # 读取所有文件，验证文件合法性
        # 1、标记非图片文件和读取异常的图片文件
        # 2、修正正常文件的扩展名
        # 3、读取正常文件的拍摄日期，作为文件的修改日期。如果读取失败，则直接使用文件的修改日期
        # 4、计算正常文件的sha256值
        for file_info in file_info_list:
            # 1、2
            real_ext = ImageUtil.get_image_real_ext(file_info.sourcePath)
            if not real_ext:
                file_info.status = FileStatusEnum.INVALID
                logger.warning(f"文件无效：{file_info.sourcePath}")
            else:
                file_info.ext = real_ext
            # 3
            photo_date = ImageUtil.get_photo_date(file_info.sourcePath)
            if photo_date:
                file_info.modifiedTime = photo_date
                logger.info(f"使用文件拍摄时间：{file_info.modifiedTime}")
            # 4
            file_info.sha256 = Sha256Util.sha256_file(file_info.sourcePath)

        # 将正常文件按sha256值分组，每个sha256值对应一个文件列表，该文件列表按修改日期进行排序
        grouped_file_info = {}
        for file_info in file_info_list:
            if file_info.sha256 not in grouped_file_info:
                group = []
                grouped_file_info[file_info.sha256] = group
            group = grouped_file_info[file_info.sha256]
            group.append(file_info)
        # 将每个文件列表中第一个文件以外的所有文件标记为重复文件

        for sha256, group in grouped_file_info.items():
            if len(group) > 1:
                group.sort()
                for i in range(1, len(group)):
                    file_info = group[i]
                    file_info.status = FileStatusEnum.DUPLICATE
                    logger.warning(f"文件已存在：{file_info.sourcePath}, sha256={file_info.sha256}")
        # 将标记为非图片文件、读取异常的图片文件、重复文件分组区分
        result_duplicate_file_list = []
        result_invalid_file_list = []
        result_normal_file_list = []
        for file_info in file_info_list:
            if file_info.status == FileStatusEnum.DUPLICATE:
                result_duplicate_file_list.append(file_info)
            elif file_info.status == FileStatusEnum.INVALID:
                result_invalid_file_list.append(file_info)
            else:
                result_normal_file_list.append(file_info)
        # 将未被进行任何标记的文件按修改日期排序
        result_normal_file_list.sort()
        return result_duplicate_file_list, result_invalid_file_list, result_normal_file_list


def init_log(log_dir: str, log_file_name: str):
    os.makedirs(log_dir, exist_ok=True)
    logging.config.dictConfig({
        "version": 1,
        "formatters": {
            "standard_formatter": {"format": "%(asctime)s [%(levelname)s] [%(threadName)s]-%(name)s %(module)s:%(lineno)d - %(message)s"}
        },
        "handlers": {
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": f"{log_dir}/{log_file_name}",
                "maxBytes": 10 * 1024 * 1024,
                "formatter": "standard_formatter",
            },
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "standard_formatter",
            }
        },
        "loggers": {
            "standard_logger": {
                "handlers": ["file", "console"],
                "level": "DEBUG",
                "propagate": False,
            }
        },
        "root": {"handlers": ["file", "console"], "level": "DEBUG"}
    })


if __name__ == "__main__":
    init_log("../logs", "dataset_rename.log")
    RenameUtil.rename(path="../resources/dataset",
                      except_dir="../resources/dataset_exception",
                      is_move_invalid_file=True)
