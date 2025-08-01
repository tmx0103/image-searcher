"""
Copyright © 2025-2025 tmx0103.  
Licensed under the Apache-2.0 License.  
For full terms, see the LICENSE file.  
exhibition_panel.py
"""
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout, QFrame

from src.app.gui.marking_window import MarkingWindow
from src.app.qt.image_label import ImageLabel


class ExhibitionPanel(QWidget):
    SIMILAR_IMG_COLS = 8
    SIMILAR_IMG_ROWS = 2
    MAX_SIMILAR_IMG_COUNT = SIMILAR_IMG_COLS * SIMILAR_IMG_ROWS

    def __init__(self):
        super().__init__()
        #####################################
        # 展示区结构
        # -标签：多模态检索结果
        # -网格布局：若干个多模态模型检索图片标签
        # -分隔线
        # -标签：文本信息检索结果
        # -网格布局：若干个文本信息检索图片标签
        #####################################
        # 展示区（上下布局）
        self.vBoxLayoutExhibition = QVBoxLayout()

        # -标签：多模态检索结果，文字样式为：字体10，加粗，占整个布局的大小为定长
        self.labelTitleSearchResultMultiModel = QLabel("多模态检索结果")
        self.labelTitleSearchResultMultiModel.setStyleSheet("font-size: 15pt; font-weight: bold;font-family: 微软雅黑;")
        self.labelTitleSearchResultMultiModel.setFixedHeight(30)
        # -网格布局：若干个多模态模型检索图片标签
        self.gridLayoutMultiModel = QGridLayout()
        self.labelImageSearchResultMultiModelMatrix = []
        for row in range(ExhibitionPanel.SIMILAR_IMG_ROWS):
            label_row = []
            for col in range(ExhibitionPanel.SIMILAR_IMG_COLS):
                label = ImageLabel()
                label.setFixedSize(130, 130)
                label.setStyleSheet("border: 1px solid black;")
                label.setAlignment(Qt.AlignCenter)
                label.signal_mark.connect(self.on_signal_mark_image)
                self.gridLayoutMultiModel.addWidget(label, row, col)
                label_row.append(label)
            self.labelImageSearchResultMultiModelMatrix.append(label_row)

        # -分隔线
        self.frameBlankLineRight = QFrame()
        self.frameBlankLineRight.setLineWidth(1)
        self.frameBlankLineRight.setFrameShape(QFrame.HLine)
        self.frameBlankLineRight.setStyleSheet("background-color: black;")

        # -标签：文本信息检索结果，文字样式为：字体10，加粗，占整个布局的大小为定长
        self.labelTitleSearchResultTextInfo = QLabel("文本信息检索结果")
        self.labelTitleSearchResultTextInfo.setStyleSheet("font-size: 15pt; font-weight: bold;font-family: 微软雅黑;")
        self.labelTitleSearchResultTextInfo.setFixedHeight(30)
        # -网格布局：若干个文本信息检索图片标签
        self.gridLayoutTextInfo = QGridLayout()
        self.labelImageSearchResultTextInfoMatrix = []
        for row in range(ExhibitionPanel.SIMILAR_IMG_ROWS):
            label_row = []
            for col in range(ExhibitionPanel.SIMILAR_IMG_COLS):
                label = ImageLabel()
                label.setFixedSize(130, 130)
                label.setStyleSheet("border: 1px solid black;")
                label.setAlignment(Qt.AlignCenter)
                label.signal_mark.connect(self.on_signal_mark_image)
                self.gridLayoutTextInfo.addWidget(label, row, col)
                label_row.append(label)
            self.labelImageSearchResultTextInfoMatrix.append(label_row)

        self.vBoxLayoutExhibition.addWidget(self.labelTitleSearchResultMultiModel)
        self.vBoxLayoutExhibition.addLayout(self.gridLayoutMultiModel)
        self.vBoxLayoutExhibition.addWidget(self.frameBlankLineRight)
        self.vBoxLayoutExhibition.addWidget(self.labelTitleSearchResultTextInfo)
        self.vBoxLayoutExhibition.addLayout(self.gridLayoutTextInfo)

        self.setLayout(self.vBoxLayoutExhibition)

        self.childMarkingWindow = None

    def clear_images(self):
        # 清空网格图片
        for labelRow in self.labelImageSearchResultMultiModelMatrix:
            for label in labelRow:
                label.clear()

        for labelRow in self.labelImageSearchResultTextInfoMatrix:
            for label in labelRow:
                label.clear()

    def update_label_image_search_result_multi_model_matrix(self, similar_img_model_list):
        i = 0
        for similar_img_model in similar_img_model_list:
            row = i // ExhibitionPanel.SIMILAR_IMG_COLS
            col = i % ExhibitionPanel.SIMILAR_IMG_COLS
            image_label: ImageLabel = self.labelImageSearchResultMultiModelMatrix[row][col]
            image_label.setPixmap(QPixmap(similar_img_model.filePath))
            image_label.setImagePath(similar_img_model.filePath)
            image_label.setFileSha256(similar_img_model.fileSha256)
            image_label.setCosineSimilarity(1 - similar_img_model.cosineDistance)
            i += 1
            if i >= ExhibitionPanel.MAX_SIMILAR_IMG_COUNT:
                break

    def update_label_image_search_result_text_info_matrix(self, similar_img_model_list):
        i = 0
        for similar_img_model in similar_img_model_list:
            row = i // ExhibitionPanel.SIMILAR_IMG_COLS
            col = i % ExhibitionPanel.SIMILAR_IMG_COLS
            image_label: ImageLabel = self.labelImageSearchResultTextInfoMatrix[row][col]
            image_label.setPixmap(QPixmap(similar_img_model.filePath))
            image_label.setImagePath(similar_img_model.filePath)
            image_label.setFileSha256(similar_img_model.fileSha256)
            image_label.setCosineSimilarity(1 - similar_img_model.cosineDistance)
            i += 1
            if i >= ExhibitionPanel.MAX_SIMILAR_IMG_COUNT:
                break

    def on_signal_mark_image(self):
        image_label: ImageLabel = self.sender()
        self.childMarkingWindow = MarkingWindow(image_label.imagePath, image_label.fileSha256)
        self.childMarkingWindow.show()
