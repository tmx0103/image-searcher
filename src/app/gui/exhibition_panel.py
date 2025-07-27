"""
Copyright © 2025-2025 tmx0103.  
Licensed under the Apache-2.0 License.  
For full terms, see the LICENSE file.  
exhibition_panel.py
"""
from PyQt5.QtCore import Qt, QMimeData, QByteArray
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout, QFrame, QMenu, QApplication

from src.app.log.logger import logger
from src.app.qt.image_label import ImageLabel


class ExhibitionPanel(QWidget):
    SIMILAR_IMG_COLS = 8
    SIMILAR_IMG_ROWS = 2
    MAX_SIMILAR_IMG_COUNT = SIMILAR_IMG_COLS * SIMILAR_IMG_ROWS

    def __init__(self):
        super().__init__()
        #####################################
        # 展示区结构
        # -标签：多模态模型检索结果
        # -网格布局：若干个多模态模型检索图片标签
        # -分隔线
        # -标签：OCR检索结果
        # -网格布局：若干个OCR检索图片标签
        #####################################
        # 展示区（上下布局）
        self.vBoxLayoutExhibition = QVBoxLayout()

        # -标签：多模态模型检索结果，文字样式为：字体10，加粗，占整个布局的大小为定长
        self.labelTitleSearchResultMultiModel = QLabel("多模态模型检索结果")
        self.labelTitleSearchResultMultiModel.setStyleSheet("font-size: 15pt; font-weight: bold;font-family: 微软雅黑;")
        self.labelTitleSearchResultMultiModel.setFixedHeight(30)
        # -网格布局：若干个多模态模型检索图片标签
        self.gridLayoutMultiModel = QGridLayout()
        self.labelImageSearchResultMultiModelMatrix = []
        for row in range(ExhibitionPanel.SIMILAR_IMG_ROWS):
            label_row = []
            for col in range(ExhibitionPanel.SIMILAR_IMG_COLS):
                label = ImageLabel()
                label.setFixedSize(150, 150)
                label.setStyleSheet("border: 1px solid black;")
                label.setAlignment(Qt.AlignCenter)
                label.setContextMenuPolicy(Qt.CustomContextMenu)
                label.customContextMenuRequested.connect(self.on_show_context_menu)
                self.gridLayoutMultiModel.addWidget(label, row, col)
                label_row.append(label)
            self.labelImageSearchResultMultiModelMatrix.append(label_row)

        # -分隔线
        self.frameBlankLineRight = QFrame()
        self.frameBlankLineRight.setLineWidth(1)
        self.frameBlankLineRight.setFrameShape(QFrame.HLine)
        self.frameBlankLineRight.setStyleSheet("background-color: black;")

        # -标签：OCR检索结果，文字样式为：字体10，加粗，占整个布局的大小为定长
        self.labelTitleSearchResultOcr = QLabel("OCR检索结果")
        self.labelTitleSearchResultOcr.setStyleSheet("font-size: 15pt; font-weight: bold;font-family: 微软雅黑;")
        self.labelTitleSearchResultOcr.setFixedHeight(30)
        # -网格布局：若干个OCR检索图片标签
        self.gridLayoutOcr = QGridLayout()
        self.labelImageSearchResultOcrMatrix = []
        for row in range(ExhibitionPanel.SIMILAR_IMG_ROWS):
            label_row = []
            for col in range(ExhibitionPanel.SIMILAR_IMG_COLS):
                label = ImageLabel()
                label.setFixedSize(150, 150)
                label.setStyleSheet("border: 1px solid black;")
                label.setAlignment(Qt.AlignCenter)
                label.setContextMenuPolicy(Qt.CustomContextMenu)
                label.customContextMenuRequested.connect(self.on_show_context_menu)
                self.gridLayoutOcr.addWidget(label, row, col)
                label_row.append(label)
            self.labelImageSearchResultOcrMatrix.append(label_row)

        self.vBoxLayoutExhibition.addWidget(self.labelTitleSearchResultMultiModel)
        self.vBoxLayoutExhibition.addLayout(self.gridLayoutMultiModel)
        self.vBoxLayoutExhibition.addWidget(self.frameBlankLineRight)
        self.vBoxLayoutExhibition.addWidget(self.labelTitleSearchResultOcr)
        self.vBoxLayoutExhibition.addLayout(self.gridLayoutOcr)

        self.setLayout(self.vBoxLayoutExhibition)

    def on_show_context_menu(self, pos):
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

    def clear_images(self):
        # 清空网格图片
        for labelRow in self.labelImageSearchResultMultiModelMatrix:
            for label in labelRow:
                label.clear()

        for labelRow in self.labelImageSearchResultOcrMatrix:
            for label in labelRow:
                label.clear()

    def update_label_image_search_result_multi_model_matrix(self, similar_img_model_multi_model_list):
        i = 0
        for similar_img_model_multi_model in similar_img_model_multi_model_list:
            row = i // ExhibitionPanel.SIMILAR_IMG_COLS
            col = i % ExhibitionPanel.SIMILAR_IMG_COLS
            image_label: ImageLabel = self.labelImageSearchResultMultiModelMatrix[row][col]
            image_label.setPixmap(QPixmap(similar_img_model_multi_model.file_relative_path))
            image_label.setImagePath(similar_img_model_multi_model.file_relative_path)
            i += 1
            if i >= ExhibitionPanel.MAX_SIMILAR_IMG_COUNT:
                break

    def update_label_image_search_result_ocr_matrix(self, similar_img_model_all_text_list):
        i = 0
        for similar_img_model_all_text in similar_img_model_all_text_list:
            row = i // ExhibitionPanel.SIMILAR_IMG_COLS
            col = i % ExhibitionPanel.SIMILAR_IMG_COLS
            image_label: ImageLabel = self.labelImageSearchResultOcrMatrix[row][col]
            image_label.setPixmap(QPixmap(similar_img_model_all_text.file_relative_path))
            image_label.setImagePath(similar_img_model_all_text.file_relative_path)
            i += 1
            if i >= ExhibitionPanel.MAX_SIMILAR_IMG_COUNT:
                break
