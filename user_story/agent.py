"""
User Story Writer Agent

Generates Gherkin user stories from feature idea files.
Follows a simple agentic pattern for educational purposes.

Usage:
    from examples.user_story.agent import agent
    from langchain_core.messages import HumanMessage

    result = agent.invoke({
        "messages": [HumanMessage(content="Generate user stories for 02-feat-refresh-button.md")]
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


class UserStoryState(TypedDict):
    """State for the user story writer agent"""

    messages: Annotated[list[AnyMessage], operator.add]
    story_generated: bool


# Define model node


def llm_call(state: UserStoryState):
    """LLM decides whether to call a tool or generate user stories"""

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
agent_builder = StateGraph(UserStoryState)

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


def save_story_to_file(content: str, filename: str) -> str:
    """
    Save generated user stories to the stories data directory.

    Args:
        content: User story content to save
        filename: Name of the file (e.g., "02-refresh-button-stories.feature")

    Returns:
        Path to saved file
    """
    stories_dir = Path(__file__).parent.parent / "data" / "stories"
    stories_dir.mkdir(parents=True, exist_ok=True)

    output_path = stories_dir / filename

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    return str(output_path)


def generate_stories(idea_filename: str, save_output: bool = True) -> dict:
    """
    Generate user stories for a feature idea file.

    Args:
        idea_filename: Name of the idea file (e.g., "02-feat-refresh-button.md")
        save_output: Whether to save the output to a file

    Returns:
        Dictionary with:
        - content: Generated user story content
        - output_file: Path to saved file (if save_output=True)
    """
    # Invoke the agent
    result = agent.invoke(
        {
            "messages": [
                HumanMessage(
                    content=f"Generate Gherkin user stories for the feature in {idea_filename}"
                )
            ],
            "story_generated": False,
        }
    )

    # Extract the final user story content (last message from assistant)
    story_content = None
    for msg in reversed(result["messages"]):
        if (
            hasattr(msg, "content") and not msg.tool_calls
            if hasattr(msg, "tool_calls")
            else True
        ):
            story_content = msg.content
            break

    response = {
        "content": story_content,
        "messages": result["messages"],
    }

    # Save to file if requested
    if save_output and story_content:
        # Generate output filename from input filename
        output_filename = idea_filename.replace("feat-", "").replace(
            ".md", "-stories.md"
        )
        output_path = save_story_to_file(story_content, output_filename)
        response["output_file"] = output_path

    return response
