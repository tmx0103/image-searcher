"""
Copyright © 2025-2025 tmx0103.  
Licensed under the Apache-2.0 License.  
For full terms, see the LICENSE file.  
__init__.py
"""
__all__ = ['run']

from src.app.log.logger import logger


def run():
    import sys

    from PyQt5.QtWidgets import QApplication
    from dotenv import load_dotenv

    from src.app.gui.main_window import MainWindow
    load_dotenv()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    try:
        return_value = app.exec()
        sys.exit(return_value)
    except Exception as e:
        logger.error(e, exc_info=True)
        logger.error("程序异常退出")
