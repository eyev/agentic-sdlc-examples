"""
Complete SDLC Workflow Agent

Orchestrates the full workflow: Feature Idea → User Stories → Acceptance Criteria

This demonstrates how to compose multiple agents into a single workflow graph.
"""

import operator
from pathlib import Path
from typing import Annotated

from langchain_core.messages import AnyMessage
from langgraph.graph import END, START, StateGraph
from typing_extensions import TypedDict

from user_story.agent import generate_stories
from ac_writer.agent import generate_ac


# State Definition


class WorkflowState(TypedDict):
    """State for the complete SDLC workflow"""

    file_prefix: str
    idea_filename: str
    story_filename: str | None
    ac_filename: str | None
    stories_generated: bool
    ac_generated: bool
    errors: list[str]


def find_idea_file(prefix: str) -> str:
    """Find idea file matching the prefix"""
    ideas_dir = Path(__file__).parent.parent / "data" / "ideas"
    pattern = f"{prefix}*.md"

    matches = list(ideas_dir.glob(pattern))

    if not matches:
        raise FileNotFoundError(f"No idea files found matching '{prefix}'")

    return matches[0].name


def generate_stories_node(state: WorkflowState) -> dict:
    """Node that generates user stories from the feature idea"""
    print(f"📝 Generating user stories for: {state['idea_filename']}")

    try:
        result = generate_stories(state["idea_filename"], save_output=True)

        return {
            "story_filename": result.get("output_file"),
            "stories_generated": True,
            "errors": [],
        }
    except Exception as e:
        return {
            "stories_generated": False,
            "errors": [f"Failed to generate stories: {str(e)}"],
        }


def generate_ac_node(state: WorkflowState) -> dict:
    """Node that generates AC from the user stories"""

    if not state["stories_generated"]:
        return {
            "ac_generated": False,
            "errors": state.get("errors", [])
            + ["Cannot generate AC: Stories not generated"],
        }

    # Extract filename from full path
    story_path = Path(state["story_filename"])
    story_filename = story_path.name

    print(f"✅ Generating acceptance criteria from: {story_filename}")

    try:
        result = generate_ac(story_filename, source_type="story", save_output=True)

        return {
            "ac_filename": result.get("output_file"),
            "ac_generated": True,
        }
    except Exception as e:
        return {
            "ac_generated": False,
            "errors": state.get("errors", []) + [f"Failed to generate AC: {str(e)}"],
        }


# Build Workflow Graph


def build_workflow() -> StateGraph:
    """Build the complete SDLC workflow graph"""

    graph = StateGraph(WorkflowState)

    # Add nodes
    graph.add_node("generate_stories", generate_stories_node)
    graph.add_node("generate_ac", generate_ac_node)

    # Define flow: Idea → Stories → AC → End
    graph.add_edge(START, "generate_stories")
    graph.add_edge("generate_stories", "generate_ac")
    graph.add_edge("generate_ac", END)

    return graph.compile()


# Compile the workflow
workflow = build_workflow()


# Convenience Function


def run_workflow(file_prefix: str) -> dict:
    """
    Run the complete SDLC workflow for a feature file.

    Args:
        file_prefix: File prefix (e.g., '01', '02') or full filename

    Returns:
        Dictionary with results and file paths
    """
    # Find the idea file
    if file_prefix.endswith(".md"):
        idea_filename = file_prefix
        prefix = file_prefix.split("-")[0]
    else:
        prefix = file_prefix
        idea_filename = find_idea_file(prefix)

    print("=" * 70)
    print("Running Full Workflow:  Idea -> User Stories -> Acceptance Criteria")
    print("=" * 70)
    print(f"Feature: {idea_filename}")
    print("-" * 70)
    print()

    # Initialize state
    initial_state = WorkflowState(
        file_prefix=prefix,
        idea_filename=idea_filename,
        story_filename=None,
        ac_filename=None,
        stories_generated=False,
        ac_generated=False,
        errors=[],
    )

    # Run the workflow
    result = workflow.invoke(initial_state)

    # Display results
    print()
    print("=" * 70)
    print("Workflow Complete!")
    print("=" * 70)

    if result.get("stories_generated"):
        print(f"✅ User Stories: {result['story_filename']}")
    else:
        print("❌ User Stories: Failed")

    if result.get("ac_generated"):
        print(f"✅ Acceptance Criteria: {result['ac_filename']}")
    else:
        print("❌ Acceptance Criteria: Failed")

    if result.get("errors"):
        print("\n⚠️  Errors:")
        for error in result["errors"]:
            print(f"   - {error}")

    print()

    return result
