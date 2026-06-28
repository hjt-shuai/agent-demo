from langchain_core.messages import ToolMessage
from agent.state import AgentState
from agent.tools.registry import get_tools


def execute_tools(state: AgentState) -> dict:
    last_message = state["messages"][-1]
    tools_by_name = {tool.name: tool for tool in get_tools()}

    tool_messages = []
    for tool_call in last_message.tool_calls:
        tool = tools_by_name.get(tool_call["name"])
        if tool:
            try:
                result = tool.invoke(tool_call["args"])
            except Exception as e:
                result = f"工具执行出错：{str(e)}"
        else:
            result = f"未找到工具：{tool_call['name']}"
        tool_messages.append(
            ToolMessage(content=str(result), tool_call_id=tool_call["id"])
        )

    return {"messages": tool_messages}
