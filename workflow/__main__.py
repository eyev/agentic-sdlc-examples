"""
Entry point for running the complete SDLC workflow.

Usage:
    python -m workflow 01       # Run complete workflow for file 01
    python -m workflow 02       # Run complete workflow for file 02
"""

import argparse

from .agent import run_workflow

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run complete SDLC workflow: Idea → Stories → AC"
    )
    parser.add_argument(
        "file_prefix",
        help="File prefix (e.g., '01', '02') or full filename",
    )

    args = parser.parse_args()

    # Run the complete workflow
    result = run_workflow(args.file_prefix)

    # Exit with error code if workflow failed
    if result.get("errors"):
        exit(1)
