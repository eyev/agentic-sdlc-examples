"""
User Story Writer Agent

This agent generates Gherkin user stories from feature idea files.

Usage:
    from examples.user_story.agent import agent, generate_stories
    from langchain_core.messages import HumanMessage

    # Simple usage with convenience function
    result = generate_stories("02-feat-refresh-button.md", save_output=True)
    print(result["content"])

    # Direct agent invocation
    result = agent.invoke({
        "messages": [
            HumanMessage(content="Generate user stories for 02-feat-refresh-button.md")
        ],
        "llm_calls": 0,
        "story_generated": False
    })
"""

from .agent import agent, generate_stories

__all__ = ["agent", "generate_stories"]
