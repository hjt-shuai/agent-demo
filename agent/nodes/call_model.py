from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage

from agent.state import AgentState
from agent.tools.registry import get_tools
from config import settings

SYSTEM_PROMPT = """你是智能助手，乐于助人且善于使用工具。

你有以下工具可用：
- get_weather：查询城市的实时天气信息

当用户提问时，先判断是否需要使用工具。如果需要，请调用对应的工具。如果不需要，直接回答即可。"""


def _build_llm():
    llm = ChatOpenAI(
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
        model=settings.llm_model_name,
        temperature=0.7,
    )
    tools = get_tools()
    if tools:
        llm = llm.bind_tools(tools)
    return llm


def call_model(state: AgentState) -> dict:
    llm = _build_llm()
    messages = [SystemMessage(content=SYSTEM_PROMPT)]
    for msg in state["messages"]:
        messages.append(msg)
    response = llm.invoke(messages)
    return {"messages": [response]}
