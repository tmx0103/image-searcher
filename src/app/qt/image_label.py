"""
Copyright © 2025-2025 tmx0103.  
Licensed under the Apache-2.0 License.  
For full terms, see the LICENSE file.  
image_label.py
"""

from PyQt5.QtCore import Qt, QMimeData, QByteArray, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel, QApplication, QMenu

from src.app.log.logger import logger


class ImageLabel(QLabel):
    signal_delete_image = pyqtSignal()
    signal_mark = pyqtSignal()

    def __init__(self, *__args):
        super().__init__(*__args)
        self.setAlignment(Qt.AlignCenter)  # 居中显示
        self.originalPixmap = None
        self.imagePath = None
        self.imageClipboardPath = None
        self.fileSha256 = None
        self.cosineSimilarity = None
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.on_show_context_menu)

    def setPixmap(self, pixmap):
        self.originalPixmap = pixmap
        scaled = pixmap.scaled(
            self.size(),
            Qt.KeepAspectRatio,  # 保持宽高比
            Qt.SmoothTransformation  # 平滑缩放
        )
        super().setPixmap(scaled)

    def setImagePath(self, image_path):
        self.imagePath = image_path
        self.imageClipboardPath = "file:///" + image_path.replace('\\', '/')

    def setFileSha256(self, file_sha256):
        self.fileSha256 = file_sha256

    def setCosineSimilarity(self, cosine_similarity):
        self.cosineSimilarity = cosine_similarity

    def clear(self):
        self.originalPixmap = None
        self.imagePath = None
        self.imageClipboardPath = None
        super().clear()

    def resizeEvent(self, event):
        # 窗口大小变化时触发
        if self.originalPixmap is not None:
            # 按比例缩放至标签当前尺寸
            scaled = QPixmap(self.originalPixmap).scaled(
                self.size(),
                Qt.KeepAspectRatio,  # 保持宽高比
                Qt.SmoothTransformation  # 平滑缩放
            )
            super().setPixmap(scaled)
        super().resizeEvent(event)

    def on_show_context_menu(self, pos):
        logger.info("触发右键菜单")
        image_label: ImageLabel = self.sender()
        if not image_label.pixmap():
            return

        menu = QMenu()
        if image_label.cosineSimilarity:
            menu.addAction(f"相似度: {image_label.cosineSimilarity:.2f}")
        copy_action = menu.addAction("复制图片")
        delete_action = menu.addAction("删除图片")
        mark_action = menu.addAction("打标...")
        action = menu.exec(image_label.mapToGlobal(pos))

        if action == copy_action:
            clipboard = QApplication.clipboard()
            q_mime_data = QMimeData()
            q_mime_data.setData("text/uri-list", QByteArray(image_label.imageClipboardPath.encode('utf-8')))
            logger.info("复制图片路径：%s", image_label.imageClipboardPath)
            clipboard.setMimeData(q_mime_data)
        elif action == delete_action:
            self.signal_delete_image.emit()
        elif action == mark_action:
            self.signal_mark.emit()
