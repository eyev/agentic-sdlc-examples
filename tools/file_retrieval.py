"""
File retrieval tools for agent workflows.

These tools allow agents to retrieve context from data directories
(ideas, stories, acceptance criteria, etc.)
"""

from pathlib import Path
from typing import Literal
from langchain_core.tools import tool


# Base directory for data files
DATA_DIR = Path(__file__).parent.parent / "data"


@tool
def get_idea_file(filename: str) -> str:
    """
    Retrieve a feature idea file from the ideas directory.

    Args:
        filename: Name of the idea file (e.g., "01-feat-pagination.md")

    Returns:
        Content of the idea file as a string
    """
    file_path = DATA_DIR / "ideas" / filename

    if not file_path.exists():
        available_files = list((DATA_DIR / "ideas").glob("*.md"))
        files_list = "\n".join([f.name for f in available_files])
        return f"Error: File '{filename}' not found.\n\nAvailable files:\n{files_list}"

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return content
    except Exception as e:
        return f"Error reading file: {str(e)}"


@tool
def get_story_file(filename: str) -> str:
    """
    Retrieve a user story file from the stories directory.

    Args:
        filename: Name of the story file (e.g., "01-pagination-stories.md")

    Returns:
        Content of the story file as a string
    """
    file_path = DATA_DIR / "stories" / filename

    if not file_path.exists():
        available_files = list((DATA_DIR / "stories").glob("*.md"))
        files_list = (
            "\n".join([f.name for f in available_files]) if available_files else "None"
        )
        return f"Error: File '{filename}' not found.\n\nAvailable files:\n{files_list}"

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return content
    except Exception as e:
        return f"Error reading file: {str(e)}"


@tool
def list_idea_files() -> str:
    """
    List all available feature idea files.

    Returns:
        Newline-separated list of available idea files
    """
    ideas_dir = DATA_DIR / "ideas"

    if not ideas_dir.exists():
        return "Ideas directory not found"

    files = sorted(ideas_dir.glob("*.md"))

    if not files:
        return "No idea files found"

    return "\n".join([f.name for f in files])


@tool
def list_story_files() -> str:
    """
    List all available user story files.

    Returns:
        Newline-separated list of available story files
    """
    stories_dir = DATA_DIR / "stories"

    if not stories_dir.exists():
        return "Stories directory not found"

    files = sorted(stories_dir.glob("*.md"))

    if not files:
        return "No story files found"

    return "\n".join([f.name for f in files])
