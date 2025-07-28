"""
Copyright © 2025-2025 tmx0103.  
Licensed under the Apache-2.0 License.  
For full terms, see the LICENSE file.  
grid_widget_tag_list.py
"""
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QGridLayout, QLineEdit, QMenu

from src.app.log.logger import logger


class GridWidgetTagList(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.gridLayout = QGridLayout()
        self.lineEditTagList = []
        self.setLayout(self.gridLayout)

    def add_tag(self, tag: str, index: int = None):
        if index is None:
            index = len(self.lineEditTagList)
        line_edit_tag = QLineEdit()
        line_edit_tag.setText(tag)
        line_edit_tag.setReadOnly(True)
        line_edit_tag.setContextMenuPolicy(Qt.CustomContextMenu)
        line_edit_tag.customContextMenuRequested.connect(lambda _, ind=index: self.on_show_context_menu(pos=_, index=ind))
        self.gridLayout.addWidget(line_edit_tag, index, 0)

        if len(self.lineEditTagList) <= index:
            for i in range(len(self.lineEditTagList), index + 1):
                self.lineEditTagList.append(None)
        self.lineEditTagList[index] = line_edit_tag

    def on_show_context_menu2(self, pos):
        logger.info(f"触发右键菜单,{pos}")
        line_edit_tag: QLineEdit = self.sender()

        menu = QMenu()
        delete_action = menu.addAction("删除标签")
        action = menu.exec(line_edit_tag.mapToGlobal(pos))
        if action == delete_action:
            logger.info(f"删除标签,{pos}")

    def on_show_context_menu(self, pos, index: int):

        line_edit_tag: QLineEdit = self.sender()
        logger.info(f"触发右键菜单,{pos},{index},{line_edit_tag.text()}")
        menu = QMenu()
        delete_action = menu.addAction("删除标签")
        action = menu.exec(line_edit_tag.mapToGlobal(pos))

        if action == delete_action:
            self.on_delete_tag(index)

    def on_delete_tag(self, index: int):
        logger.info(f"on_delete_tag: {index}")
        # 所有控件从网格布局中移除
        for i in range(len(self.lineEditTagList)):
            # 需要移除所有槽函数，因为lambda表达式每次都会新建一个函数，且connect时老的槽函数无法被移除
            self.lineEditTagList[i].customContextMenuRequested.disconnect()
            self.gridLayout.removeWidget(self.lineEditTagList[i])
        # 重建控件索引
        new_line_edit_tag_list = []
        for i in range(len(self.lineEditTagList)):
            if i != index:
                new_line_edit_tag_list.append(self.lineEditTagList[i])
        self.lineEditTagList = new_line_edit_tag_list

        # 重新加入控件到网格布局中
        for i in range(len(self.lineEditTagList)):
            self.gridLayout.addWidget(self.lineEditTagList[i], i, 0)
            self.lineEditTagList[i].customContextMenuRequested.connect(lambda _, ind=i: self.on_show_context_menu(pos=_, index=ind))
