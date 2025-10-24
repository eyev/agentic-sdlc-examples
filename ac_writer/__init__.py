"""
AC Writer Agent

This agent generates acceptance criteria from feature idea files.

Usage:
    from examples.ac_writer.agent import agent, generate_ac
    from langchain_core.messages import HumanMessage

    # Simple usage with convenience function
    result = generate_ac("02-feat-refresh-button.md", save_output=True)
    print(result["content"])

    # Direct agent invocation
    result = agent.invoke({
        "messages": [
            HumanMessage(content="Generate AC for 02-feat-refresh-button.md")
        ],
        "llm_calls": 0,
        "ac_generated": False
    })
"""

from .agent import agent, generate_ac

__all__ = ["agent", "generate_ac"]
