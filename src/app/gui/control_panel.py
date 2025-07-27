"""
Copyright © 2025-2025 tmx0103.  
Licensed under the Apache-2.0 License.  
For full terms, see the LICENSE file.  
control_panel.py
"""
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QTextCursor
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QHBoxLayout, QPushButton, QFrame, QFileDialog

from src.app.ai.ai_agent import AiAgent
from src.app.ai.tools.img_search_tool import ImgSearchTool
from src.app.gui.exhibition_panel import ExhibitionPanel
from src.app.log.logger import logger
from src.app.qt.image_label import ImageLabel
from src.app.qt.llm_thread import LlmThread
from src.app.qt.search_thread import SearchThread
from src.app.service.img_search_service import ImgSearchService


class ControlPanel(QWidget):
    signalSwitchOverlay = pyqtSignal(bool)
    signalClearImages = pyqtSignal()
    signalUpdateLabelImageSearchResultMultiModelMatrix = pyqtSignal(list)
    signalUpdateLabelImageSearchResultOcrMatrix = pyqtSignal(list)

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
        # -标签：大模型检索
        # -大模型对话历史文本框
        # -大模型检索文本框
        # -左右布局：清除历史、提问/停止、直接用文本检索
        # -分隔线
        # -标签：图片检索
        # -左右布局：选择图片按钮、清除图片按钮
        # -标签：图片展示
        # -图片检索按钮
        #####################################
        # 控制区（上下布局）
        self.vBoxLayoutControl = QVBoxLayout()

        # -标签：大模型检索
        self.labelTitleSearchByLlm = QLabel("通过大模型检索")
        self.labelTitleSearchByLlm.setStyleSheet("font-size: 15pt; font-weight: bold;font-family: 微软雅黑;")
        self.labelTitleSearchByLlm.setFixedHeight(30)
        # -大模型对话历史文本框
        self.textEditLlmHistory = QTextEdit()
        self.textEditLlmHistory.setPlaceholderText("对话历史")
        self.textEditLlmHistory.setStyleSheet("font-size: 12pt;font-family: 微软雅黑;")
        self.textEditLlmHistory.setMinimumHeight(250)
        self.textEditLlmHistory.setReadOnly(True)
        # -大模型检索文本框
        self.textEditLlmToSearch = QTextEdit()
        self.textEditLlmToSearch.setPlaceholderText("在这里输入问题")
        self.textEditLlmToSearch.setStyleSheet("font-size: 12pt;font-family: 微软雅黑;")
        self.textEditLlmToSearch.setFixedHeight(40)
        # -左右布局：清除历史、提问/停止
        self.hBoxLayoutSearchByLlmControl = QHBoxLayout()
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
        # --直接用文本检索按钮
        self.pushButtonSearchByText = QPushButton("文本搜索")
        self.pushButtonSearchByText.setStyleSheet("font-size: 12pt;font-family: 微软雅黑;")
        self.pushButtonSearchByText.setFixedHeight(30)
        self.pushButtonSearchByText.clicked.connect(self.on_click_push_button_search_by_text)

        self.hBoxLayoutSearchByLlmControl.addWidget(self.pushButtonClearLlmHistory)
        self.hBoxLayoutSearchByLlmControl.addWidget(self.pushButtonAskLlm)
        self.hBoxLayoutSearchByLlmControl.addWidget(self.pushButtonSearchByText)

        # -分隔线
        self.frameBlankLineLeft1 = QFrame()
        self.frameBlankLineLeft1.setLineWidth(1)
        self.frameBlankLineLeft1.setFrameShape(QFrame.HLine)
        self.frameBlankLineLeft1.setStyleSheet("background-color: black;")

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

        self.vBoxLayoutControl.addWidget(self.labelTitleSearchByLlm)
        self.vBoxLayoutControl.addWidget(self.textEditLlmHistory)
        self.vBoxLayoutControl.addWidget(self.textEditLlmToSearch)
        self.vBoxLayoutControl.addLayout(self.hBoxLayoutSearchByLlmControl)
        self.vBoxLayoutControl.addWidget(self.frameBlankLineLeft1)
        self.vBoxLayoutControl.addWidget(self.labelTitleSearchByImage)
        self.vBoxLayoutControl.addLayout(self.hBoxLayoutSearchByImageControl)
        self.vBoxLayoutControl.addWidget(self.labelImageToSearch)
        self.vBoxLayoutControl.addWidget(self.pushButtonSearchByImage)

        self.setLayout(self.vBoxLayoutControl)

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
        self.signalClearImages.emit()

    def on_click_push_button_search_by_image(self):
        # 清空展示区图片
        self.signalClearImages.emit()
        cosine_similarity = 0.0
        try:
            if self.labelImageToSearch.imagePath:
                similar_img_model_multi_model_list, similar_img_model_all_text_list \
                    = self.imgSearchService.search_by_img(self.labelImageToSearch.imagePath, cosine_similarity,
                                                          ExhibitionPanel.MAX_SIMILAR_IMG_COUNT)
                # 填充展示区图片
                self.signalUpdateLabelImageSearchResultMultiModelMatrix.emit(similar_img_model_multi_model_list)
                self.signalUpdateLabelImageSearchResultOcrMatrix.emit(similar_img_model_all_text_list)

            else:
                return
        except Exception as e:
            logger.error(e)

    def on_click_push_button_search_by_text(self):
        if self.textEditLlmToSearch.toPlainText():
            self.do_push_button_search_by_text(self.textEditLlmToSearch.toPlainText())

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
        self.signalUpdateLabelImageSearchResultOcrMatrix.emit(similar_img_model_all_text_list)
        self.signalSwitchOverlay.emit(False)

    def on_signal_start_img_search_by_text(self, text: str):
        self.do_push_button_search_by_text(text)

    def update_all_label_image_search_result_matrix(self, similar_img_model_multi_model_list, similar_img_model_all_text_list):
        self.signalClearImages.emit()
        self.signalUpdateLabelImageSearchResultMultiModelMatrix.emit(similar_img_model_multi_model_list)
        self.signalUpdateLabelImageSearchResultOcrMatrix.emit(similar_img_model_all_text_list)

    def on_click_push_button_clear_llm_history(self):
        self.textEditLlmHistory.clear()
        self.aiAgent.clear()

    def on_click_push_button_ask_or_stop_llm(self):
        if self.textEditLlmToSearch.toPlainText():
            ask_text = self.textEditLlmToSearch.toPlainText()
            # 启用UI
            self.pushButtonSearchByText.setEnabled(False)
            self.pushButtonSearchByText.setEnabled(False)
            self.textEditLlmHistory.append(f"提问: {ask_text}\n")
            self.textEditLlmToSearch.clear()
            self.textEditLlmHistory.append("回答: ")
            # 创建工作线程处理模型调用
            self.llmThread = LlmThread(self.aiAgent, ask_text)
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
        self.pushButtonSearchByText.setEnabled(True)
        self.pushButtonSearchByText.setEnabled(True)

        # 清理工作线程
        self.llmThread = None
