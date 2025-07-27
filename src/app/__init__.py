"""
Copyright © 2025-2025 tmx0103.  
Licensed under the Apache-2.0 License.  
For full terms, see the LICENSE file.  
__init__.py
"""
__all__ = ['run']

import sys

from PyQt5.QtWidgets import QApplication
from dotenv import load_dotenv

from src.app.gui.main_window import MainWindow


def run():
    load_dotenv()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
