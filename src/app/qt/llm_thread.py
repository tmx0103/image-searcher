"""
Copyright © 2025-2025 tmx0103.  
Licensed under the Apache-2.0 License.  
For full terms, see the LICENSE file.  
llm_thread.py
"""
from PyQt5.QtCore import QThread, pyqtSignal

from src.app.ai.ai_agent import AiAgent
from src.app.log.logger import logger


class LlmThread(QThread):
    # 定义信号：文本块、完成信号、错误信号
    model_token_generated = pyqtSignal(str)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, ai_agent: AiAgent, prompt, image_path_list: list = None):
        super().__init__()
        self.aiAgent = ai_agent
        self.prompt = prompt
        self.imagePathList = image_path_list

    def run(self):
        try:
            # 流式调用模型
            logger.info("开始调用模型...")
            for chunk in self.aiAgent.stream(self.prompt, self.imagePathList):
                logger.info("模型输出:%s", chunk)
                self.model_token_generated.emit(chunk)  # 发送每个文本块
            self.finished.emit()
            logger.info("模型调用完成")
        except Exception as e:
            logger.error(e, exc_info=True)
            self.error.emit("模型执行异常")
