"""
Acceptance Criteria Writer Agent

Generates acceptance criteria from feature idea files.
Follows a simple agentic pattern for educational purposes.

Usage:
    from examples.ac_writer.agent import agent
    from langchain_core.messages import HumanMessage

    result = agent.invoke({
        "messages": [HumanMessage(content="Generate AC for 02-feat-refresh-button.md")]
    })
"""

import operator
from pathlib import Path
from typing import Annotated, Literal

from dotenv import load_dotenv
from langchain_core.messages import AnyMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from typing_extensions import TypedDict

from tools.file_retrieval import (
    get_idea_file,
    get_story_file,
    list_idea_files,
    list_story_files,
)
from nodes import should_continue_on_tool_calls, create_tool_executor
from .prompts import SYSTEM_PROMPT

load_dotenv()


# Initialize the LLM
model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Define available tools
tools = [get_idea_file, list_idea_files, get_story_file, list_story_files]
tools_by_name = {tool.name: tool for tool in tools}
model_with_tools = model.bind_tools(tools)


# Define state


class ACWriterState(TypedDict):
    """State for the AC writer agent"""

    messages: Annotated[list[AnyMessage], operator.add]
    ac_generated: bool


# Define model node


def llm_call(state: ACWriterState):
    """LLM decides whether to call a tool or generate AC"""

    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]

    return {
        "messages": [model_with_tools.invoke(messages)],
    }


# Define tool node

# Create tool executor using the factory function
tool_node = create_tool_executor(tools_by_name)


# Define routing logic

# Use the generic routing function
should_continue = should_continue_on_tool_calls


# Build agent

# Build workflow
agent_builder = StateGraph(ACWriterState)

# Add nodes
agent_builder.add_node("llm_call", llm_call)
agent_builder.add_node("tool_node", tool_node)

# Add edges to connect nodes
agent_builder.add_edge(START, "llm_call")
agent_builder.add_conditional_edges("llm_call", should_continue, ["tool_node", END])
agent_builder.add_edge("tool_node", "llm_call")

# Compile the agent
agent = agent_builder.compile()


# Utility functions


def save_ac_to_file(content: str, filename: str) -> str:
    """
    Save generated AC to the ac data directory.

    Args:
        content: AC content to save
        filename: Name of the file (e.g., "02-refresh-button-ac.md")

    Returns:
        Path to saved file
    """
    ac_dir = Path(__file__).parent.parent / "data" / "ac"
    ac_dir.mkdir(parents=True, exist_ok=True)

    output_path = ac_dir / filename

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    return str(output_path)


def generate_ac(
    filename: str, source_type: str = "idea", save_output: bool = True
) -> dict:
    """
    Generate acceptance criteria from a feature idea or user story file.

    Args:
        filename: Name of the file (e.g., "02-feat-refresh-button.md" or "02-refresh-button-stories.feature")
        source_type: Type of source file - "idea" or "story" (default: "idea")
        save_output: Whether to save the output to a file

    Returns:
        Dictionary with:
        - content: Generated AC content
        - output_file: Path to saved file (if save_output=True)
    """
    # Build appropriate prompt based on source type
    if source_type == "story":
        prompt = f"Generate acceptance criteria for each scenario in the user story file {filename}"
    else:
        prompt = f"Generate acceptance criteria for the feature in {filename}"

    # Invoke the agent
    result = agent.invoke(
        {
            "messages": [HumanMessage(content=prompt)],
            "ac_generated": False,
        }
    )

    # Extract the final AC content (last message from assistant)
    ac_content = None
    for msg in reversed(result["messages"]):
        if (
            hasattr(msg, "content") and not msg.tool_calls
            if hasattr(msg, "tool_calls")
            else True
        ):
            ac_content = msg.content
            break

    response = {
        "content": ac_content,
        "messages": result["messages"],
    }

    # Save to file if requested
    if save_output and ac_content:
        # Generate output filename based on source type
        if source_type == "story":
            output_filename = filename.replace("-stories.md", "-scenario-ac.md")
        else:
            output_filename = filename.replace("feat-", "").replace(".md", "-ac.md")

        output_path = save_ac_to_file(ac_content, output_filename)
        response["output_file"] = output_path

    return response
