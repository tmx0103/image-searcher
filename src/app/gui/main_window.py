"""
Copyright © 2025-2025 tmx0103.  
Licensed under the Apache-2.0 License.  
For full terms, see the LICENSE file.  
main_window.py
"""
from multiprocessing import Lock

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QMainWindow, QSplitter
from PyQt5.sip import isdeleted

from src.app.gui.control_panel import ControlPanel
from src.app.gui.exhibition_panel import ExhibitionPanel
from src.app.log.logger import logger
from src.app.qt.overlay_widget import OverlayWidget


class MainWindow(QMainWindow):
    SIMILAR_IMG_COLS = 8
    SIMILAR_IMG_ROWS = 2
    MAX_SIMILAR_IMG_COUNT = SIMILAR_IMG_COLS * SIMILAR_IMG_ROWS
    OVERLAY_LOCK = Lock()

    def __init__(self):
        super().__init__()
        logger.info("初始化GUI")

        self.overlay = None

        self.setWindowTitle("图文搜图")
        self.setGeometry(100, 100, 1200, 800)

        # 主控件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        # 主窗体：水平布局（左右布局）
        self.hBoxLayoutMain = QHBoxLayout()
        self.splitterMain = QSplitter(Qt.Horizontal)
        self.splitterMain.setStyleSheet("QSplitter::handle{background-color: rgb(200, 200, 200);}")

        self.controlPanel = ControlPanel()
        self.exhibitionPanel = ExhibitionPanel()

        self.controlPanel.signalSwitchOverlay.connect(self.switch_overlay)
        self.controlPanel.signalClearImages.connect(self.clear_images)
        self.controlPanel.signalUpdateLabelImageSearchResultMultiModelMatrix.connect(
            self.update_label_image_search_result_multi_model_matrix)
        self.controlPanel.signalUpdateLabelImageSearchResultTextInfoMatrix.connect(self.update_label_image_search_result_text_info_matrix)

        self.splitterMain.addWidget(self.controlPanel)
        self.splitterMain.addWidget(self.exhibitionPanel)

        self.hBoxLayoutMain.addWidget(self.splitterMain)

        main_widget.setLayout(self.hBoxLayoutMain)

    def switch_overlay(self, show: bool):
        logger.info(f"收到信号[switch_overlay]show={show}")
        with self.OVERLAY_LOCK:
            if show:
                logger.info("开始添加覆盖层")
                # 只有覆盖层不存在时才添加覆盖层
                if not self.overlay or isdeleted(self.overlay):
                    self.overlay = OverlayWidget(self.exhibitionPanel)
                    self.overlay.show()
                else:
                    logger.info("已存在覆盖层")
            else:
                logger.info("开始删除覆盖层")
                # 只有覆盖层存在并且未销毁时才删除覆盖层
                if self.overlay and not isdeleted(self.overlay):
                    logger.info("删除覆盖层")
                    self.overlay.deleteLater()  # 安全移除覆盖层

    def clear_images(self):
        logger.info("收到信号[clear_images]")
        self.exhibitionPanel.clear_images()

    def update_label_image_search_result_multi_model_matrix(self, similar_img_model_list):
        logger.info("收到信号[update_label_image_search_result_multi_model_matrix]")
        self.exhibitionPanel.update_label_image_search_result_multi_model_matrix(similar_img_model_list)

    def update_label_image_search_result_text_info_matrix(self, similar_img_model_list):
        logger.info("收到信号[update_label_image_search_result_text_info_matrix]")
        self.exhibitionPanel.update_label_image_search_result_text_info_matrix(similar_img_model_list)
