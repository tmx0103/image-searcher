"""
Copyright © 2025-2025 tmx0103.  
Licensed under the Apache-2.0 License.  
For full terms, see the LICENSE file.  
marking_window.py
"""
import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QSplitter, QVBoxLayout, QLineEdit, QPushButton, QScrollArea
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.app.db.mapper.image_info_mapper import ImageInfoMapper
from src.app.gui.grid_widget_tag_list import GridWidgetTagList
from src.app.log.logger import logger
from src.app.qt.image_label import ImageLabel
from src.app.service.repo_vector_service import RepoVectorService


class MarkingWindow(QWidget):
    engine = create_engine(f"postgresql://"
                           f"{os.getenv('POSTGRESQL_USER')}:{os.getenv('POSTGRESQL_PASSWORD')}"
                           f"@{os.getenv('POSTGRESQL_HOST')}:{os.getenv('POSTGRESQL_PORT')}/{os.getenv('POSTGRESQL_DB')}")
    Session = sessionmaker(bind=engine)
    repo_vector_service = RepoVectorService.get_instance()

    def __init__(self, file_path, file_sha256):
        super().__init__()
        self.setWindowTitle(f"图片打标 {file_path}")
        self.setGeometry(100, 100, 800, 600)

        self.hBoxLayoutMain = QHBoxLayout()
        self.setLayout(self.hBoxLayoutMain)

        self.filePath = file_path
        self.fileSha256 = file_sha256

        # 主窗体为左右结构
        self.splitterMain = QSplitter(Qt.Horizontal)
        self.splitterMain.setStyleSheet("QSplitter::handle{background-color: rgb(200, 200, 200);}")

        #####################################
        # 左侧图片展示结构-图片ImageLabel
        #####################################
        pixmap = QPixmap(file_path)
        self.imageLabel = ImageLabel("待检索图片")
        self.imageLabel.setFixedSize(300, 600)
        self.imageLabel.setAlignment(Qt.AlignCenter)
        self.imageLabel.setPixmap(pixmap)
        self.imageLabel.setImagePath(file_path)

        #####################################
        # 右侧打标区结构
        # -滚动区：上下布局：标签表
        # -左右布局：
        # -- 新增标签文本框
        # -- 新增标签按钮
        # -保存按钮
        #####################################
        # 打标区（上下布局）
        self.markingPanel = QWidget()
        self.vBoxLayoutMarking = QVBoxLayout()
        self.markingPanel.setLayout(self.vBoxLayoutMarking)

        # -滚动区：上下布局：标签表
        self.scrollAreaMarking = QScrollArea()
        self.scrollAreaMarking.setWidgetResizable(True)
        self.scrollAreaMarking.setFixedHeight(600)
        self.scrollAreaMarking.setStyleSheet("QScrollArea {background-color: white;}")
        self.gridWidgetTagList = GridWidgetTagList()
        self.scrollAreaMarking.setWidget(self.gridWidgetTagList)

        # -左右布局：
        # -- 新增标签文本框
        # -- 新增标签按钮
        self.hBoxLayoutAddTag = QHBoxLayout()
        self.lineEditAddTag = QLineEdit()
        self.lineEditAddTag.setPlaceholderText("请输入标签")
        self.pushButtonAddTag = QPushButton("新增标签")
        self.pushButtonAddTag.setStyleSheet("font-size: 12pt;font-family: 微软雅黑;")
        self.pushButtonAddTag.setFixedHeight(30)
        self.pushButtonAddTag.clicked.connect(self.on_click_push_button_add_tag)
        self.hBoxLayoutAddTag.addWidget(self.lineEditAddTag)
        self.hBoxLayoutAddTag.addWidget(self.pushButtonAddTag)

        # -保存按钮
        self.pushButtonSave = QPushButton("保存")
        self.pushButtonAddTag.setStyleSheet("font-size: 12pt;font-family: 微软雅黑;")
        self.pushButtonAddTag.setFixedHeight(30)
        self.pushButtonSave.clicked.connect(self.on_click_push_button_save)

        self.vBoxLayoutMarking.addWidget(self.scrollAreaMarking)
        self.vBoxLayoutMarking.addLayout(self.hBoxLayoutAddTag)
        self.vBoxLayoutMarking.addWidget(self.pushButtonSave)

        self.splitterMain.addWidget(self.imageLabel)
        self.splitterMain.addWidget(self.markingPanel)

        self.hBoxLayoutMain.addWidget(self.splitterMain)
        self.load_tags()

    def on_click_push_button_add_tag(self):
        logger.info("on_click_push_button_add_tag")
        if self.lineEditAddTag.text() and self.lineEditAddTag.text() != "":
            logger.info(f"添加标签：{self.lineEditAddTag.text()}")
            self.gridWidgetTagList.add_tag(self.lineEditAddTag.text())

    def on_click_push_button_save(self):
        logger.info("on_click_push_button_delete_tag")

        tags = [line_edit_tag.text() for line_edit_tag in self.gridWidgetTagList.lineEditTagList]
        logger.info(f"保存标签：{",".join(tags)}")
        with self.Session() as session:
            image_info_mapper = ImageInfoMapper(session)
            # 更新标签到数据库
            image_info_mapper.update_tag_text_by_file_path(self.filePath, ",".join(tags))
            # 更新向量到数据库
            self.repo_vector_service.update_all_text_vector(self.filePath)
            logger.info(f"保存完成")

    def load_tags(self):
        with self.Session() as session:
            image_info_mapper = ImageInfoMapper(session)
            tag_text = image_info_mapper.query_by_file_path(self.filePath).tag_text
            if tag_text is None:
                return
            tag_list = tag_text.split(",")
            for tag in tag_list:
                self.gridWidgetTagList.add_tag(tag)
