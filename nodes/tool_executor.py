"""
Tool executor node for executing LLM tool calls.
"""

from langchain_core.messages import ToolMessage


def create_tool_executor(tools_by_name: dict):
    """
    Factory function that creates a tool execution node.

    Args:
        tools_by_name: Dictionary mapping tool names to tool functions

    Returns:
        A tool_node function that executes tool calls
    """

    def tool_node(state: dict):
        """Executes the tool calls from the last message"""
        result = []
        last_message = state["messages"][-1]

        for tool_call in last_message.tool_calls:
            tool = tools_by_name[tool_call["name"]]
            observation = tool.invoke(tool_call["args"])
            result.append(
                ToolMessage(content=str(observation), tool_call_id=tool_call["id"])
            )

        return {"messages": result}

    return tool_node
