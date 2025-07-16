"""
Copyright © 2025-2025 tmx0103.
Licensed under the Apache-2.0 License.
For full terms, see the LICENSE file.
gui.py
"""
import os
import sys

from PIL import Image
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel,
                             QFileDialog, QGridLayout, QMenu, QTextEdit, QFrame)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QMimeData, QByteArray
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.app.bert.chinese_bert import ChineseBert
from src.app.clip.chinese_clip import ChineseClip
from src.app.db.mapper.img_vector_mapper import ImgVectorMapper
from src.app.log.logger import logger
from src.app.ocr.paddle_ocr_util import PaddleOCRUtil
from src.app.qt.image_label import ImageLabel


class ImageGridApp(QMainWindow):
    SIMILAR_IMG_COLS = 8
    SIMILAR_IMG_ROWS = 2
    MAX_SIMILAR_IMG_COUNT = SIMILAR_IMG_COLS * SIMILAR_IMG_ROWS

    def __init__(self):
        super().__init__()
        logger.info("init gui")
        engine = create_engine(f"postgresql://"
                               f"{os.getenv('POSTGRESQL_USER')}:{os.getenv('POSTGRESQL_PASSWORD')}"
                               f"@{os.getenv('POSTGRESQL_HOST')}:{os.getenv('POSTGRESQL_PORT')}/{os.getenv('POSTGRESQL_DB')}")
        self.Session = sessionmaker(bind=engine)
        self.chinese_clip = ChineseClip()
        self.ocr_util = PaddleOCRUtil("resources/ai-models/PP-OCRv5_server_det_infer",
                                      "resources/ai-models/PP-OCRv5_server_rec_infer")
        self.chinese_bert = ChineseBert()

        self.setWindowTitle("图文搜图")
        self.setGeometry(100, 100, 1200, 800)

        # 主控件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        # 主窗体：水平布局（左右布局）
        self.hBoxLayoutMain = QHBoxLayout()

        #####################################
        # 主窗体左侧控制区结构
        # -标签：文本检索
        # -检索文本框
        # -文本检索按钮
        # -分隔线
        # -标签：图片检索
        # -左右布局：选择图片按钮、清除图片按钮
        # -标签：图片展示
        # -图片检索按钮
        #####################################

        # 主窗体左侧控制区（上下布局）
        self.vBoxLayoutControl = QVBoxLayout()
        # -标签：文本检索，文字样式为：字体10，加粗，占整个布局的大小为定长
        self.labelTitleSearchByText = QLabel("通过文本检索")
        self.labelTitleSearchByText.setStyleSheet("font-size: 15pt; font-weight: bold;font-family: 微软雅黑;")
        self.labelTitleSearchByText.setFixedHeight(30)
        # -检索文本框，支持多行，字体10
        self.textEditTextToSearch = QTextEdit()
        self.textEditTextToSearch.setPlaceholderText("输入待检索的文本")
        self.textEditTextToSearch.setStyleSheet("font-size: 12pt;font-family: 微软雅黑;")
        self.textEditTextToSearch.setFixedHeight(100)

        # -文本检索按钮
        self.pushButtonSearchByText = QPushButton("搜索")
        self.pushButtonSearchByText.setStyleSheet("font-size: 12pt;font-family: 微软雅黑;")
        self.pushButtonSearchByText.setFixedHeight(30)
        self.pushButtonSearchByText.clicked.connect(self.on_click_push_button_search_by_text)

        # -分隔线
        self.labelBlankLineLeft = QFrame()
        self.labelBlankLineLeft.setLineWidth(1)
        self.labelBlankLineLeft.setFrameShape(QFrame.HLine)
        self.labelBlankLineLeft.setStyleSheet("background-color: black;")

        # -标签：图片检索
        self.labelTitleSearchByImage = QLabel("通过图片检索")
        self.labelTitleSearchByImage.setStyleSheet("font-size: 15pt; font-weight: bold;font-family: 微软雅黑;")
        self.labelTitleSearchByImage.setFixedHeight(30)

        # -左右布局：选择图片按钮、清除图片按钮、检索按钮
        self.hBoxLayoutSearchByImageControl = QHBoxLayout()
        # --选择图片按钮
        self.pushButtonChooseImage = QPushButton("选择图片")
        self.pushButtonChooseImage.setStyleSheet("font-size: 12pt;font-family: 微软雅黑;")
        self.pushButtonChooseImage.setFixedHeight(30)
        self.pushButtonChooseImage.clicked.connect(self.on_click_push_button_choose_image)
        # --清除图片按钮
        self.pushButtonClearImage = QPushButton("清除图片")
        self.pushButtonClearImage.setStyleSheet("font-size: 12pt;font-family: 微软雅黑;")
        self.pushButtonClearImage.setFixedHeight(30)
        self.pushButtonClearImage.clicked.connect(self.on_click_push_button_clear_image)

        self.hBoxLayoutSearchByImageControl.addWidget(self.pushButtonChooseImage)
        self.hBoxLayoutSearchByImageControl.addWidget(self.pushButtonClearImage)

        # -标签：图片展示
        self.labelImageToSearch = ImageLabel("待检索图片")
        self.labelImageToSearch.setMinimumWidth(300)
        self.labelImageToSearch.setMinimumHeight(300)
        self.labelImageToSearch.setMaximumHeight(500)
        self.labelImageToSearch.setStyleSheet("border: 2px solid blue;")
        self.labelImageToSearch.setAlignment(Qt.AlignCenter)

        # -图片检索按钮
        self.pushButtonSearchByImage = QPushButton("搜索")
        self.pushButtonSearchByImage.setStyleSheet("font-size: 12pt;font-family: 微软雅黑;")
        self.pushButtonSearchByImage.setFixedHeight(30)
        self.pushButtonSearchByImage.clicked.connect(self.on_click_push_button_search_by_image)

        self.vBoxLayoutControl.addWidget(self.labelTitleSearchByText)
        self.vBoxLayoutControl.addWidget(self.textEditTextToSearch)
        self.vBoxLayoutControl.addWidget(self.pushButtonSearchByText)
        self.vBoxLayoutControl.addWidget(self.labelBlankLineLeft)
        self.vBoxLayoutControl.addWidget(self.labelTitleSearchByImage)
        self.vBoxLayoutControl.addLayout(self.hBoxLayoutSearchByImageControl)
        self.vBoxLayoutControl.addWidget(self.labelImageToSearch)
        self.vBoxLayoutControl.addWidget(self.pushButtonSearchByImage)

        self.hBoxLayoutMain.addLayout(self.vBoxLayoutControl)

        #####################################
        # 主窗体右侧展示区结构
        # -标签：多模态模型检索结果
        # -网格布局：若干个多模态模型检索图片标签
        # -分隔线
        # -标签：OCR检索结果
        # -网格布局：若干个OCR检索图片标签
        #####################################
        # 主窗体右侧展示区（上下布局）
        self.vBoxLayoutShow = QVBoxLayout()
        # -标签：多模态模型检索结果，文字样式为：字体10，加粗，占整个布局的大小为定长
        self.labelTitleSearchResultMultiModel = QLabel("多模态模型检索结果")
        self.labelTitleSearchResultMultiModel.setStyleSheet("font-size: 15pt; font-weight: bold;font-family: 微软雅黑;")
        self.labelTitleSearchResultMultiModel.setFixedHeight(30)
        # -网格布局：若干个多模态模型检索图片标签
        self.gridLayoutMultiModel = QGridLayout()
        self.labelImageSearchResultMultiModelMatrix = []
        for row in range(ImageGridApp.SIMILAR_IMG_ROWS):
            label_row = []
            for col in range(ImageGridApp.SIMILAR_IMG_COLS):
                label = ImageLabel()
                label.setFixedSize(150, 150)
                label.setStyleSheet("border: 1px solid black;")
                label.setAlignment(Qt.AlignCenter)
                label.setContextMenuPolicy(Qt.CustomContextMenu)
                label.customContextMenuRequested.connect(self.show_context_menu)
                self.gridLayoutMultiModel.addWidget(label, row, col)
                label_row.append(label)
            self.labelImageSearchResultMultiModelMatrix.append(label_row)

        # -分隔线
        self.labelBlankLineRight = QFrame()
        self.labelBlankLineRight.setLineWidth(1)
        self.labelBlankLineRight.setFrameShape(QFrame.HLine)
        self.labelBlankLineRight.setStyleSheet("background-color: black;")

        # -标签：OCR检索结果，文字样式为：字体10，加粗，占整个布局的大小为定长
        self.labelTitleSearchResultOcr = QLabel("OCR检索结果")
        self.labelTitleSearchResultOcr.setStyleSheet("font-size: 15pt; font-weight: bold;font-family: 微软雅黑;")
        self.labelTitleSearchResultOcr.setFixedHeight(30)
        # -网格布局：若干个OCR检索图片标签
        self.gridLayoutOcr = QGridLayout()
        self.labelImageSearchResultOcrMatrix = []
        for row in range(ImageGridApp.SIMILAR_IMG_ROWS):
            label_row = []
            for col in range(ImageGridApp.SIMILAR_IMG_COLS):
                label = ImageLabel()
                label.setFixedSize(150, 150)
                label.setStyleSheet("border: 1px solid black;")
                label.setAlignment(Qt.AlignCenter)
                label.setContextMenuPolicy(Qt.CustomContextMenu)
                label.customContextMenuRequested.connect(self.show_context_menu)
                self.gridLayoutOcr.addWidget(label, row, col)
                label_row.append(label)
            self.labelImageSearchResultOcrMatrix.append(label_row)

        self.vBoxLayoutShow.addWidget(self.labelTitleSearchResultMultiModel)
        self.vBoxLayoutShow.addLayout(self.gridLayoutMultiModel)
        self.vBoxLayoutShow.addWidget(self.labelBlankLineRight)
        self.vBoxLayoutShow.addWidget(self.labelTitleSearchResultOcr)
        self.vBoxLayoutShow.addLayout(self.gridLayoutOcr)

        self.hBoxLayoutMain.addLayout(self.vBoxLayoutShow)

        main_widget.setLayout(self.hBoxLayoutMain)

    def show_context_menu(self, pos):
        image_label: ImageLabel = self.sender()
        if not image_label.pixmap():
            return

        menu = QMenu()
        copy_action = menu.addAction("复制图片")
        action = menu.exec_(image_label.mapToGlobal(pos))

        if action == copy_action:
            clipboard = QApplication.clipboard()
            q_mime_data = QMimeData()
            q_mime_data.setData("text/uri-list", QByteArray(image_label.imageClipboardPath.encode('utf-8')))
            logger.info("复制图片路径：%s", image_label.imageClipboardPath)
            clipboard.setMimeData(q_mime_data)

    def on_click_push_button_choose_image(self):
        # 打开文件选择对话框
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择图片", "", "图片文件 (*.png *.jpg *.jpeg *.gif)"
        )

        if file_path:
            logger.info(f"已选择图片：{file_path}")

            pixmap = QPixmap(file_path)

            # 更新主图片,按比例缩放
            self.labelImageToSearch.setPixmap(pixmap)
            self.labelImageToSearch.setImagePath(file_path)

    def on_click_push_button_clear_image(self):
        self.labelImageToSearch.clear()

    def on_click_push_button_search_by_image(self):
        # 清空网格图片
        self.clear_images()
        cosine_similarity = 0.0
        try:
            if self.labelImageToSearch.imagePath:
                with Image.open(self.labelImageToSearch.imagePath) as image:
                    # 计算输入图片的特征向量
                    image_feature = self.chinese_clip.embed_image_to_vec(image)
                    image_feature_pg_str = "[" + ",".join([str(x) for x in image_feature[0]]) + "]"
                    # 从图片中识别文字OCR
                    ocr_texts = ",".join(self.ocr_util.recognize(image))
                    # 计算OCR文字的特征向量
                    ocr_text_sentence_vec = self.chinese_bert.embed_to_sentence_vec(ocr_texts)
                    ocr_text_sentence_vec_str = "[" + ",".join([str(x) for x in ocr_text_sentence_vec]) + "]"
            else:
                return

            with self.Session() as session:
                img_vector_mapper = ImgVectorMapper(session)
                # 从Postgresql查找相似图的路径
                img_vector_do_list = img_vector_mapper.search(image_feature_pg_str,
                                                              cosine_similarity, ImageGridApp.MAX_SIMILAR_IMG_COUNT)
                # 填充网格图片
                i = 0
                for img_vector_cos_distance_do in img_vector_do_list:
                    row = i // ImageGridApp.SIMILAR_IMG_COLS
                    col = i % ImageGridApp.SIMILAR_IMG_COLS
                    path = str(os.path.join(img_vector_cos_distance_do.file_dir, img_vector_cos_distance_do.file_name))
                    image_label: ImageLabel = self.labelImageSearchResultMultiModelMatrix[row][col]
                    image_label.setPixmap(QPixmap(path))
                    image_label.setImagePath(path)
                    i += 1
                    if i >= ImageGridApp.MAX_SIMILAR_IMG_COUNT:
                        break

                # 从Postgresql查找相似图的路径
                img_vector_do_list = img_vector_mapper.search_by_ocr_text_sentence_vector(ocr_text_sentence_vec_str,
                                                                                          cosine_similarity,
                                                                                          ImageGridApp.MAX_SIMILAR_IMG_COUNT)
                # 填充网格图片
                i = 0
                for img_vector_cos_distance_do in img_vector_do_list:
                    row = i // ImageGridApp.SIMILAR_IMG_COLS
                    col = i % ImageGridApp.SIMILAR_IMG_COLS
                    path = str(os.path.join(img_vector_cos_distance_do.file_dir, img_vector_cos_distance_do.file_name))
                    image_label: ImageLabel = self.labelImageSearchResultOcrMatrix[row][col]
                    image_label.setPixmap(QPixmap(path))
                    image_label.setImagePath(path)
                    i += 1
                    if i >= ImageGridApp.MAX_SIMILAR_IMG_COUNT:
                        break



        except Exception as e:
            logger.error(e)

    def on_click_push_button_search_by_text(self):
        # 清空网格图片
        self.clear_images()
        cosine_similarity = 0.0
        try:
            if self.textEditTextToSearch.toPlainText():
                # 计算输入文本特征向量
                text_feature_chinese_clip = self.chinese_clip.embed_text_to_vec(self.textEditTextToSearch.toPlainText())
                text_feature_chinese_clip_pg_str = "[" + ",".join([str(x) for x in text_feature_chinese_clip[0]]) + "]"
                text_feature_chinese_bert = self.chinese_bert.embed_to_sentence_vec(self.textEditTextToSearch.toPlainText())
                text_feature_chinese_bert_pg_str = "[" + ",".join([str(x) for x in text_feature_chinese_bert]) + "]"
            else:
                return

            with self.Session() as session:
                img_vector_mapper = ImgVectorMapper(session)
                # 从Postgresql查找相似图的路径
                img_vector_do_list = img_vector_mapper.search(text_feature_chinese_clip_pg_str,
                                                              cosine_similarity, ImageGridApp.MAX_SIMILAR_IMG_COUNT)
                # 填充网格图片
                i = 0
                for img_vector_cos_distance_do in img_vector_do_list:
                    row = i // ImageGridApp.SIMILAR_IMG_COLS
                    col = i % ImageGridApp.SIMILAR_IMG_COLS
                    path = str(os.path.join(img_vector_cos_distance_do.file_dir, img_vector_cos_distance_do.file_name))
                    image_label: ImageLabel = self.labelImageSearchResultMultiModelMatrix[row][col]
                    image_label.setPixmap(QPixmap(path))
                    image_label.setImagePath(path)
                    i += 1
                    if i >= ImageGridApp.MAX_SIMILAR_IMG_COUNT:
                        break

                # 从Postgresql查找相似图的路径
                # img_vector_do_list = img_vector_mapper.search_by_text(self.textEditTextToSearch.toPlainText(),
                #                                                       ImageGridApp.MAX_SIMILAR_IMG_COUNT)
                img_vector_do_list = img_vector_mapper.search_by_ocr_text_sentence_vector(text_feature_chinese_bert_pg_str,
                                                                                          cosine_similarity,
                                                                                          ImageGridApp.MAX_SIMILAR_IMG_COUNT)
                # 填充网格图片
                i = 0
                for img_vector_cos_distance_do in img_vector_do_list:
                    row = i // ImageGridApp.SIMILAR_IMG_COLS
                    col = i % ImageGridApp.SIMILAR_IMG_COLS
                    path = str(os.path.join(img_vector_cos_distance_do.file_dir, img_vector_cos_distance_do.file_name))
                    image_label: ImageLabel = self.labelImageSearchResultOcrMatrix[row][col]
                    image_label.setPixmap(QPixmap(path))
                    image_label.setImagePath(path)
                    i += 1
                    if i >= ImageGridApp.MAX_SIMILAR_IMG_COUNT:
                        break



        except Exception as e:
            logger.error(e)

    def clear_images(self):
        # 清空网格图片
        for labelRow in self.labelImageSearchResultMultiModelMatrix:
            for label in labelRow:
                label.clear()

        for labelRow in self.labelImageSearchResultOcrMatrix:
            for label in labelRow:
                label.clear()


def gui():
    # 载入数据库
    load_dotenv()
    app = QApplication(sys.argv)
    window = ImageGridApp()
    window.show()
    sys.exit(app.exec_())
