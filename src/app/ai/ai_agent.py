"""
Copyright © 2025-2025 tmx0103.  
Licensed under the Apache-2.0 License.  
For full terms, see the LICENSE file.  
ai_agent.py
"""
import uuid

from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage
from langchain_core.tools import StructuredTool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from src.app.ai.tools.img_search_tool import img_search_by_text_tool


class AiAgent:
    SYSTEM_MESSAGE = """
    你是根据用户提问的内容来查询相关图片的机器人。
    你有查询图片的工具，但这个工具会对系统造成巨大负担，只有在非常合适的时机，并且获得用户明确的输入或者认可时才可以使用。
    任何不确定是否需要使用工具的场合，都请把工具列给用户，并让用户给出明确的信息后，再去使用。使用完成后，记得告诉用户你用了哪些工具，工具的参数填写了什么。
    有以下规则需要你遵循：
    1、如果用户的目的并非是查询图片，请告知用户你的职责，并且不要回答用户与查询图片无关的内容。
    比如，当用户询问天气时，你应该告知用户，你只能查询图片，不能查询天气。
    再比如，用户和你打招呼时，你应该告知用户，你是查询图片的机器人，并让用户给出查询图片的输入。
    2、用户输入的内容很可能就是查询图片的输入，而非在向你提问。如果不确定，请向用户确认后再做查询。
    比如，用户输入“你是谁”的时候，用户很可能是希望你查询包含“你是谁”这串文本的图片，并非在向你提问，也并不需要你告知你是查询图片的机器人。
    如果你难以理解用户的意图，请反问他，“您是否希望以【你是谁】这串文本来查询图片？”
    然后，再根据用户的反馈，来使用工具进行查询。
    3、如果用户并没有给出明确的查询文本，需要你来适当处理查询图片所使用的文本。如果查询文本作了处理，请先告知用户你的处理结果，用户确认或者重新修改后，然后再去使用工具。
    比如，用户输入“帮我查找小狗的图”，你不应该直接用“找小狗的图”或者“小狗的图”来查询图片。一般来说，用户实际想要的是查询“小狗”图。
    此时，你应该先询问用户，你将使用【小狗】来查询图片，是否接受。只有在用户认可的情况下，你才可以使用工具。
    4、在无法完全理解用户的需求时，不得擅自使用工具。
    """

    def __init__(self):
        self.memory = MemorySaver()
        self.model = init_chat_model(model_provider="ollama", model="qwen3:8b")
        tool = StructuredTool.from_function(img_search_by_text_tool)
        self.tools = [tool]
        self.agent = create_react_agent(model=self.model, tools=self.tools, checkpointer=self.memory,
                                        prompt=SystemMessage(content=self.SYSTEM_MESSAGE))
        self.chatId = str(uuid.uuid4()).replace("-", "")[:16]

    def stream(self, prompt: str):
        config = {"configurable": {"thread_id": self.chatId}}
        input_message = {"role": "user", "content": prompt}
        for step, metadata in self.agent.stream(input={"messages": [input_message]}, config=config, stream_mode="messages"):
            if metadata["langgraph_node"] == "agent" and (text := step.text()):
                yield text

    def clear(self):
        self.chatId = str(uuid.uuid4()).replace("-", "")[:16]


if __name__ == "__main__":
    ai_agent = AiAgent()
    for token in ai_agent.stream("请使用测试打印工具，参数请填写AAA。如果没有测试打印工具就不要使用。"):
        print(token, end="")
    for token in ai_agent.stream("请使用测试计算器工具，参数请填写AAA。如果没有计算器工具就不要使用。"):
        print(token, end="")
