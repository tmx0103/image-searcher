"""
Copyright © 2025-2025 tmx0103.
Licensed under the Apache-2.0 License.
For full terms, see the LICENSE file.
"""
import os
import sys

from PIL import Image
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLineEdit, QLabel,
                             QFileDialog, QGridLayout, QMenu)
from PyQt5.QtGui import QPixmap, QDoubleValidator
from PyQt5.QtCore import Qt, QMimeData, QByteArray
from dotenv import load_dotenv
from transformers import ChineseCLIPModel, ChineseCLIPProcessor
from app.models.img_vector import ImgVectorMapper
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class ImageGridApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("图文搜图")
        self.setGeometry(100, 100, 1000, 800)

        # 主控件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()

        # 顶部控制区
        control_layout = QHBoxLayout()
        # 顶部控制区-上传图片按钮
        self.input_img_btn = QPushButton("上传图片")
        self.input_img_btn.clicked.connect(self.on_upload_image_btn_click)
        # 顶部控制区-清除图片按钮
        self.clear_img_btn = QPushButton("清除图片")
        self.clear_img_btn.clicked.connect(self.on_clear_image_btn_click)
        # 顶部控制区-检索文本输入框
        self.input_text = QLineEdit()
        self.input_text.setPlaceholderText("输入待检索的文本")
        # 顶部控制区-余弦相似度输入框
        self.input_cosine_similarity = QLineEdit()
        self.input_cosine_similarity.setPlaceholderText("输入相似度阈值")
        self.input_cosine_similarity.setText("0.5")
        self.input_cosine_similarity.setValidator(QDoubleValidator())
        # 顶部控制区-搜索按钮
        self.search_btn = QPushButton("搜索")
        self.search_btn.clicked.connect(self.on_search_btn_click)

        control_layout.addWidget(self.input_img_btn)
        control_layout.addWidget(self.clear_img_btn)
        control_layout.addWidget(self.input_text)
        control_layout.addWidget(self.input_cosine_similarity)
        control_layout.addWidget(self.search_btn)
        main_layout.addLayout(control_layout)

        # 主图片显示区
        self.main_image = QLabel()
        self.main_image.setFixedSize(400, 300)
        self.main_image.setStyleSheet("border: 2px solid blue;")
        self.main_image.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.main_image)

        # 3x4图片网格区
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout()
        self.grid_widget.setLayout(self.grid_layout)

        self.image_labels = []
        self.image_abs_path = [None for _ in range(12)]
        for row in range(3):
            for col in range(4):
                label = QLabel()
                label.setFixedSize(150, 150)
                label.setStyleSheet("border: 1px solid black;")
                label.setAlignment(Qt.AlignCenter)
                label.setContextMenuPolicy(Qt.CustomContextMenu)
                label.customContextMenuRequested.connect(lambda pos, r=row, c=col: self.show_context_menu(pos, r, c))
                self.grid_layout.addWidget(label, row, col)
                self.image_labels.append(label)

        main_layout.addWidget(self.grid_widget)
        main_widget.setLayout(main_layout)

        # 主图片路径
        self.input_img_path = None

    def show_context_menu(self, pos, row, col):
        index = row * 4 + col
        sender = self.sender()
        if not sender.pixmap():
            return

        menu = QMenu()
        copy_action = menu.addAction("复制图片")
        action = menu.exec_(sender.mapToGlobal(pos))

        if action == copy_action:
            clipboard = QApplication.clipboard()
            q_mime_data = QMimeData()
            q_mime_data.setData("text/uri-list", QByteArray(self.image_abs_path[index].encode('utf-8')))
            print("复制图片路径", self.image_abs_path[index])
            clipboard.setMimeData(q_mime_data)

    def on_upload_image_btn_click(self):
        # 打开文件选择对话框
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择图片", "", "图片文件 (*.png *.jpg *.jpeg *.gif)"
        )

        if file_path:
            self.input_img_path = file_path
            print("入参图片相对路径", self.input_img_path)

            pixmap = QPixmap(self.input_img_path)

            # 更新主图片
            main_pixmap = pixmap.scaled(
                400, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.main_image.setPixmap(main_pixmap)

            # 清空网格图片
            for label in self.image_labels:
                label.clear()
                label.setStyleSheet("border: 1px solid black;")
            self.image_abs_path = [None for _ in range(12)]

    def on_clear_image_btn_click(self):
        self.input_img_path = None
        self.main_image.clear()

    def on_search_btn_click(self):
        if not self.input_cosine_similarity.text():
            self.input_cosine_similarity.setText("0.5")
        cosine_similarity = float(self.input_cosine_similarity.text())
        try:
            if self.input_img_path:
                # 计算输入图片的特征向量
                with Image.open(self.input_img_path) as image:
                    inputs = processor(images=image, return_tensors="pt").to("cuda")
                    feature = model.get_image_features(**inputs)
            elif self.input_text.text():
                # 计算输入文本特征向量
                inputs = processor(text=self.input_text.text(), padding=True, return_tensors="pt").to("cuda")
                feature = model.get_text_features(**inputs)
            else:
                return

            feature = feature / feature.norm(p=2, dim=-1, keepdim=True)  # normalize
            feature = feature.cpu().detach().numpy()
            feature_pg_str = "[" + ",".join([str(x) for x in feature[0]]) + "]"
            with Session() as session:
                img_vector_mapper = ImgVectorMapper(session)
                # 从Postgresql查找相似图的路径
                img_vector_do_list = img_vector_mapper.search(feature_pg_str, cosine_similarity, 12)
            # 填充网格图片
            i = 0
            for img_vector_do in img_vector_do_list:
                path = str(os.path.join(img_vector_do.file_dir, img_vector_do.file_name))
                similar_img = QPixmap(path)
                scaled_pixmap = similar_img.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.image_labels[i].setPixmap(scaled_pixmap)
                # 获取绝对路径
                self.image_abs_path[i] = "file:///" + os.path.abspath(path).replace('\\', '/')
                i += 1
                if i >= 12:
                    break

        except Exception as e:
            print(e)


if __name__ == "__main__":
    # 载入数据库
    load_dotenv()
    engine = create_engine(f"postgresql://"
                           f"{os.getenv('POSTGRESQL_USER')}:{os.getenv('POSTGRESQL_PASSWORD')}"
                           f"@{os.getenv('POSTGRESQL_HOST')}:{os.getenv('POSTGRESQL_PORT')}/{os.getenv('POSTGRESQL_DB')}")
    Session = sessionmaker(bind=engine)
    model = ChineseCLIPModel.from_pretrained("OFA-Sys/chinese-clip-vit-huge-patch14").to("cuda")
    processor = ChineseCLIPProcessor.from_pretrained("OFA-Sys/chinese-clip-vit-huge-patch14")
    app = QApplication(sys.argv)
    window = ImageGridApp()
    window.show()
    sys.exit(app.exec_())
