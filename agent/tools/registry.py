from langchain_core.tools import BaseTool
from .weather import get_weather

_tools: list[BaseTool] = []


def register_tool(tool: BaseTool):
    _tools.append(tool)


def get_tools() -> list[BaseTool]:
    return _tools


# 注册内置工具
register_tool(get_weather)
