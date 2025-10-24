"""
Routing node for determining whether to continue with tool calls or end.
"""

from typing import Literal

from langgraph.graph import END


def should_continue_on_tool_calls(state: dict) -> Literal["tool_node", END]:
    """
    Generic routing function that continues to tool_node if tools were called.

    Routes to:
    - "tool_node" if the last message has tool calls
    - END if no tool calls (final response)

    Args:
        state: State dict with "messages" key

    Returns:
        "tool_node" or END
    """
    messages = state["messages"]
    last_message = messages[-1]

    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tool_node"

    return END
