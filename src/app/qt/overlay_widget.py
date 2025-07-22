"""
Copyright © 2025-2025 tmx0103.  
Licensed under the Apache-2.0 License.  
For full terms, see the LICENSE file.  
overlay_widget.py
"""
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout


class OverlayWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setGeometry(parent.rect())
        self.setStyleSheet("background-color: rgba(0, 0, 0, 150);")
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)  # 拦截事件

        label = QLabel("请稍等……", self)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 24px; color: white;")

        layout = QVBoxLayout(self)
        layout.addWidget(label)

        # 监听父窗口大小变化
        parent.installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj == self.parent() and event.type() == QEvent.Resize:
            self.setGeometry(self.parent().rect())
        return super().eventFilter(obj, event)
