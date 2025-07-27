"""
Copyright © 2025-2025 tmx0103.  
Licensed under the Apache-2.0 License.  
For full terms, see the LICENSE file.  
grid_widget_image_to_search.py
"""
from PyQt5.QtWidgets import QWidget, QGridLayout

from src.app.log.logger import logger


class GridWidgetImageToSearch(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.gridLayout = QGridLayout()
        self.labelImageToSearchList = []
        self.setLayout(self.gridLayout)

    def add_widget(self, widget, row: int = None, col: int = None):
        if row is None and col is None:
            row = len(self.labelImageToSearchList) // 2
            col = len(self.labelImageToSearchList) % 2
        if row is None or col is None:
            row = len(self.labelImageToSearchList) // 2
            col = len(self.labelImageToSearchList) % 2
        if row == 0 and col == 0:
            widget.setStyleSheet("border: 2px solid red;")
        else:
            widget.setStyleSheet("border: 2px solid blue;")
        self.gridLayout.addWidget(widget, row, col)
        if len(self.labelImageToSearchList) <= row * 2 + col:
            for i in range(len(self.labelImageToSearchList), row * 2 + col + 1):
                self.labelImageToSearchList.append(None)
        self.labelImageToSearchList[row * 2 + col] = widget
        widget.signal_delete_image.connect(lambda r=row, c=col: self.on_delete_image(r, c))

    def on_delete_image(self, row, col):
        logger.info(f"on_delete_image: {row}, {col}")
        # 所有控件从网格布局中移除
        for i in range(len(self.labelImageToSearchList)):
            self.gridLayout.removeWidget(self.labelImageToSearchList[i])
        # 重建控件索引
        new_label_image_to_search = []
        for i in range(len(self.labelImageToSearchList)):
            if i != row * 2 + col:
                new_label_image_to_search.append(self.labelImageToSearchList[i])
        self.labelImageToSearchList = new_label_image_to_search

        # 修正控件样式
        if len(self.labelImageToSearchList) != 0:
            self.labelImageToSearchList[0].setStyleSheet("border: 2px solid red;")
        # 重新加入控件到网格布局中
        for i in range(len(self.labelImageToSearchList)):
            self.gridLayout.addWidget(self.labelImageToSearchList[i], i // 2, i % 2)
            self.labelImageToSearchList[i].signal_delete_image.connect(lambda r=row, c=col: self.on_delete_image(i // 2, i % 2))
