"""
Copyright © 2025-2025 tmx0103.  
Licensed under the Apache-2.0 License.  
For full terms, see the LICENSE file.  
image_label.py
"""
import os

from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt


class ImageLabel(QLabel):
    def __init__(self, *__args):
        super().__init__(*__args)
        self.setAlignment(Qt.AlignCenter)  # 居中显示
        self.originalPixmap = None
        self.imagePath = None
        self.imageClipboardPath = None

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
        self.imageClipboardPath = "file:///" + os.path.abspath(image_path).replace('\\', '/')

    def clear(self):
        self.originalPixmap = None
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
