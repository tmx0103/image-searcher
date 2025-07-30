"""
Copyright © 2025-2025 tmx0103.  
Licensed under the Apache-2.0 License.  
For full terms, see the LICENSE file.  
control_panel.py
"""
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QTextCursor, QImage
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QHBoxLayout, QPushButton, QFileDialog, QScrollArea

from src.app.ai.ai_agent import AiAgent
from src.app.ai.tools.img_search_tool import ImgSearchTool
from src.app.gui.exhibition_panel import ExhibitionPanel
from src.app.gui.grid_widget_image_to_search import GridWidgetImageToSearch
from src.app.log.logger import logger
from src.app.qt.image_label import ImageLabel
from src.app.qt.llm_thread import LlmThread
from src.app.qt.search_thread import SearchThread
from src.app.service.img_search_service import ImgSearchService


class ControlPanel(QWidget):
    signalSwitchOverlay = pyqtSignal(bool)
    signalClearImages = pyqtSignal()
    signalUpdateLabelImageSearchResultMultiModelMatrix = pyqtSignal(list)
    signalUpdateLabelImageSearchResultTextInfoMatrix = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.aiAgent = AiAgent()
        self.imgSearchService = ImgSearchService.get_instance()

        self.llmThread = None
        self.searchThread = None
        self.imgSearchTool = ImgSearchTool.get_instance()
        self.imgSearchTool.signal_start_img_search.connect(self.on_signal_start_img_search_by_text)
        #####################################
        # 控制区结构
        # -标签：检索
        # -大模型对话历史文本框
        # -滚动布局：待检索图片区域
        # -大模型检索文本框
        # -左右布局：新增图片按钮、清除历史、提问/停止
        # -左右布局：直接用文本检索、直接用图片检索、图文结合搜索
        #####################################
        # 控制区（上下布局）
        self.vBoxLayoutControl = QVBoxLayout()

        # -标签：检索
        self.labelTitleSearchByLlm = QLabel("检索")
        self.labelTitleSearchByLlm.setStyleSheet("font-size: 15pt; font-weight: bold;font-family: 微软雅黑;")
        self.labelTitleSearchByLlm.setFixedHeight(30)
        # -大模型对话历史文本框
        self.textEditLlmHistory = QTextEdit()
        self.textEditLlmHistory.setPlaceholderText("对话历史")
        self.textEditLlmHistory.setStyleSheet("font-size: 12pt;font-family: 微软雅黑;")
        self.textEditLlmHistory.setMinimumHeight(250)
        self.textEditLlmHistory.setReadOnly(True)
        # -滚动布局：待检索图片区域
        self.scrollAreaImageToSearch = QScrollArea()
        self.scrollAreaImageToSearch.setWidgetResizable(True)

        self.gridWidgetImageToSearch = GridWidgetImageToSearch()
        self.scrollAreaImageToSearch.setWidget(self.gridWidgetImageToSearch)

        # -大模型检索文本框
        self.textEditLlmToSearch = QTextEdit()
        self.textEditLlmToSearch.setPlaceholderText("在这里输入问题")
        self.textEditLlmToSearch.setStyleSheet("font-size: 12pt;font-family: 微软雅黑;")
        self.textEditLlmToSearch.setFixedHeight(40)
        # -左右布局：新增图片按钮、清除历史、提问/停止
        self.hBoxLayoutSearchByLlmControl = QHBoxLayout()
        # --新增图片按钮
        self.pushButtonAddImage = QPushButton("新增图片")
        self.pushButtonAddImage.setStyleSheet("font-size: 12pt;font-family: 微软雅黑;")
        self.pushButtonAddImage.setFixedHeight(30)
        self.pushButtonAddImage.clicked.connect(self.on_click_push_button_add_image)
        # --清除历史按钮
        self.pushButtonClearLlmHistory = QPushButton("清除历史")
        self.pushButtonClearLlmHistory.setStyleSheet("font-size: 12pt;font-family: 微软雅黑;")
        self.pushButtonClearLlmHistory.setFixedHeight(30)
        self.pushButtonClearLlmHistory.clicked.connect(self.on_click_push_button_clear_llm_history)
        # --提问/停止按钮
        self.pushButtonAskLlm = QPushButton("提问")
        self.pushButtonAskLlm.setStyleSheet("font-size: 12pt;font-family: 微软雅黑;")
        self.pushButtonAskLlm.setFixedHeight(30)
        self.pushButtonAskLlm.clicked.connect(self.on_click_push_button_ask_or_stop_llm)

        self.hBoxLayoutSearchByLlmControl.addWidget(self.pushButtonAddImage)
        self.hBoxLayoutSearchByLlmControl.addWidget(self.pushButtonClearLlmHistory)
        self.hBoxLayoutSearchByLlmControl.addWidget(self.pushButtonAskLlm)

        # -左右布局：直接用文本检索、直接用图片检索
        self.hBoxLayoutSearchDirectLy = QHBoxLayout()
        # --直接用文本检索按钮
        self.pushButtonSearchByText = QPushButton("纯文本搜索")
        self.pushButtonSearchByText.setStyleSheet("font-size: 12pt;font-family: 微软雅黑;")
        self.pushButtonSearchByText.setFixedHeight(30)
        self.pushButtonSearchByText.clicked.connect(self.on_click_push_button_search_by_text)
        # --直接用图片检索
        self.pushButtonSearchByImage = QPushButton("仅单一图片搜索")
        self.pushButtonSearchByImage.setStyleSheet("font-size: 12pt;font-family: 微软雅黑;")
        self.pushButtonSearchByImage.setFixedHeight(30)
        self.pushButtonSearchByImage.clicked.connect(self.on_click_push_button_search_by_image)
        # --图文结合搜索
        self.pushButtonSearchByTextAndImage = QPushButton("图文结合搜索")
        self.pushButtonSearchByTextAndImage.setStyleSheet("font-size: 12pt;font-family: 微软雅黑;")
        self.pushButtonSearchByTextAndImage.setFixedHeight(30)
        self.pushButtonSearchByTextAndImage.clicked.connect(self.on_click_push_button_search_by_text_and_image)

        self.hBoxLayoutSearchDirectLy.addWidget(self.pushButtonSearchByText)
        self.hBoxLayoutSearchDirectLy.addWidget(self.pushButtonSearchByImage)
        self.hBoxLayoutSearchDirectLy.addWidget(self.pushButtonSearchByTextAndImage)

        self.vBoxLayoutControl.addWidget(self.labelTitleSearchByLlm)
        self.vBoxLayoutControl.addWidget(self.textEditLlmHistory)
        self.vBoxLayoutControl.addWidget(self.scrollAreaImageToSearch)
        self.vBoxLayoutControl.addWidget(self.textEditLlmToSearch)
        self.vBoxLayoutControl.addLayout(self.hBoxLayoutSearchByLlmControl)
        self.vBoxLayoutControl.addLayout(self.hBoxLayoutSearchDirectLy)

        self.setLayout(self.vBoxLayoutControl)

    def on_click_push_button_add_image(self):
        # 打开文件选择对话框
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择图片", "", "图片文件 (*.png *.jpg *.jpeg *.gif)"
        )

        if file_path:
            logger.info(f"已选择图片：{file_path}")

            pixmap = QPixmap(file_path)

            # 更新主图片,按比例缩放
            # -标签：图片展示
            labelImageToSearch = ImageLabel("待检索图片")
            labelImageToSearch.setFixedSize(130, 130)
            labelImageToSearch.setAlignment(Qt.AlignCenter)
            labelImageToSearch.setPixmap(pixmap)
            labelImageToSearch.setImagePath(file_path)
            self.gridWidgetImageToSearch.add_widget(labelImageToSearch)

    def on_click_push_button_search_by_text(self):
        if self.textEditLlmToSearch.toPlainText():
            self.do_push_button_search_by_text(self.textEditLlmToSearch.toPlainText())

    def on_click_push_button_search_by_image(self):
        self.signalSwitchOverlay.emit(True)
        self.signalClearImages.emit()
        cosine_similarity = 0.0
        try:
            labelImageToSearchList = self.gridWidgetImageToSearch.labelImageToSearchList
            if len(labelImageToSearchList) > 0 and labelImageToSearchList[0].imagePath:
                similar_img_model_multi_model_list, similar_img_model_all_text_list \
                    = self.imgSearchService.search_by_img(labelImageToSearchList[0].imagePath, cosine_similarity,
                                                          ExhibitionPanel.MAX_SIMILAR_IMG_COUNT)
                # 填充展示区图片
                self.signalUpdateLabelImageSearchResultMultiModelMatrix.emit(similar_img_model_multi_model_list)
                self.signalUpdateLabelImageSearchResultTextInfoMatrix.emit(similar_img_model_all_text_list)
        except Exception as e:
            logger.error(e, exc_info=True)
        self.signalSwitchOverlay.emit(False)

    def on_click_push_button_search_by_text_and_image(self):
        self.signalSwitchOverlay.emit(True)
        self.signalClearImages.emit()
        cosine_similarity = 0.0
        try:
            labelImageToSearchList = self.gridWidgetImageToSearch.labelImageToSearchList
            if len(labelImageToSearchList) > 0 and labelImageToSearchList[0].imagePath and self.textEditLlmToSearch.toPlainText():
                similar_img_model_multi_model_list, similar_img_model_all_text_list, mixed_image_path \
                    = self.imgSearchService.search_by_text_and_img(labelImageToSearchList[0].imagePath,
                                                                   self.textEditLlmToSearch.toPlainText(),
                                                                   cosine_similarity, ExhibitionPanel.MAX_SIMILAR_IMG_COUNT)
                text_cursor: QTextCursor = self.textEditLlmHistory.textCursor()
                text_cursor.movePosition(QTextCursor.End)
                text_cursor.insertText(f"图文融合提示词: {self.textEditLlmToSearch.toPlainText()}\n")
                text_cursor.insertText(f"已生成图文融合图:\n")
                image = QImage(mixed_image_path)
                image = image.scaledToHeight(150)
                text_cursor.insertImage(image)
                text_cursor.insertText("\n")
                # 填充展示区图片
                self.signalUpdateLabelImageSearchResultMultiModelMatrix.emit(similar_img_model_multi_model_list)
                self.signalUpdateLabelImageSearchResultTextInfoMatrix.emit(similar_img_model_all_text_list)
        except Exception as e:
            logger.error(e, exc_info=True)
        self.signalSwitchOverlay.emit(False)

    def do_push_button_search_by_text(self, text: str):
        self.signalSwitchOverlay.emit(True)
        self.signalClearImages.emit()
        cosine_similarity = 0.0
        # 创建工作线程处理查询请求
        self.searchThread = SearchThread(text, cosine_similarity, ExhibitionPanel.MAX_SIMILAR_IMG_COUNT)
        self.searchThread.finished.connect(lambda search_thread=self.searchThread: self.on_signal_search_finished(search_thread))
        self.searchThread.start()

    def on_signal_search_finished(self, search_thread):
        logger.info("搜索完成")
        similar_img_model_multi_model_list = search_thread.similar_img_model_multi_model_list
        similar_img_model_all_text_list = search_thread.similar_img_model_all_text_list
        self.signalUpdateLabelImageSearchResultMultiModelMatrix.emit(similar_img_model_multi_model_list)
        self.signalUpdateLabelImageSearchResultTextInfoMatrix.emit(similar_img_model_all_text_list)
        self.signalSwitchOverlay.emit(False)

    def on_signal_start_img_search_by_text(self, text: str):
        self.do_push_button_search_by_text(text)

    def update_all_label_image_search_result_matrix(self, similar_img_model_multi_model_list, similar_img_model_all_text_list):
        self.signalClearImages.emit()
        self.signalUpdateLabelImageSearchResultMultiModelMatrix.emit(similar_img_model_multi_model_list)
        self.signalUpdateLabelImageSearchResultTextInfoMatrix.emit(similar_img_model_all_text_list)

    def on_click_push_button_clear_llm_history(self):
        self.textEditLlmHistory.clear()
        self.aiAgent.clear()

    def on_click_push_button_ask_or_stop_llm(self):
        if self.textEditLlmToSearch.toPlainText():
            ask_text = self.textEditLlmToSearch.toPlainText()
            # 启用UI
            self.pushButtonSearchByImage.setEnabled(False)
            self.pushButtonSearchByText.setEnabled(False)
            # 读取文本框中的问题
            text_cursor: QTextCursor = self.textEditLlmHistory.textCursor()
            text_cursor.movePosition(QTextCursor.End)
            text_cursor.insertText(f"提问: {ask_text}\n")
            self.textEditLlmToSearch.clear()

            # 读取待检索的图片
            image_path_list = []
            for label in self.gridWidgetImageToSearch.labelImageToSearchList:
                if label.imagePath:
                    image_path_list.append(label.imagePath)
                    image = QImage(label.imagePath)
                    image = image.scaledToHeight(150)
                    text_cursor.insertImage(image)
                    text_cursor.insertText("\n")
            text_cursor.insertText("\n回答: ")
            # 创建工作线程处理模型调用
            self.llmThread = LlmThread(self.aiAgent, ask_text, image_path_list)
            self.llmThread.model_token_generated.connect(self.on_model_token_generated)
            self.llmThread.finished.connect(self.on_model_finished)
            self.llmThread.error.connect(self.on_model_error)
            self.llmThread.start()

    def on_model_token_generated(self, chunk):
        text_cursor: QTextCursor = self.textEditLlmHistory.textCursor()
        text_cursor.movePosition(QTextCursor.End)
        text_cursor.insertText(chunk)
        # 自动滚动到底部
        scrollbar = self.textEditLlmHistory.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def on_model_finished(self):
        self.end_model_answer()
        self.textEditLlmHistory.append("\n")

    def on_model_error(self, error_msg):
        self.textEditLlmHistory.append(error_msg)
        # 自动滚动到底部
        scrollbar = self.textEditLlmHistory.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        self.end_model_answer()

    def end_model_answer(self):
        # 启用UI
        self.pushButtonSearchByImage.setEnabled(True)
        self.pushButtonSearchByText.setEnabled(True)

        # 清理工作线程
        self.llmThread = None
