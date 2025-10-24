"""
Entry point for running the User Story Writer agent as a module.

Usage:
    python -m user_story 01       # Generate stories for file starting with 01
    python -m user_story 02       # Generate stories for file starting with 02
"""

import argparse
import sys
from pathlib import Path

from .agent import generate_stories


def find_idea_file(prefix: str) -> str:
    """Find idea file matching the prefix"""
    ideas_dir = Path(__file__).parent.parent / "data" / "ideas"
    pattern = f"{prefix}*.md"

    matches = list(ideas_dir.glob(pattern))

    if not matches:
        print(f"❌ No idea files found matching '{prefix}' in {ideas_dir}")
        sys.exit(1)

    if len(matches) > 1:
        print(f"⚠️  Multiple files found matching '{prefix}':")
        for m in matches:
            print(f"   - {m.name}")
        print(f"Using: {matches[0].name}")

    return matches[0].name


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate Gherkin user stories from feature ideas"
    )
    parser.add_argument(
        "file_prefix",
        help="File prefix (e.g., '01', '02') or full filename",
    )
    parser.add_argument(
        "--no-save", action="store_true", help="Don't save output to file"
    )

    args = parser.parse_args()

    # Find the file
    if args.file_prefix.endswith(".md"):
        # Full filename provided
        filename = args.file_prefix
    else:
        # Prefix provided, find matching file
        filename = find_idea_file(args.file_prefix)

    print("=" * 70)
    print("User Story Writer Agent")
    print("=" * 70)
    print(f"File: {filename}")
    print("-" * 70)

    # Generate user stories
    result = generate_stories(filename, save_output=not args.no_save)

    print(f"\n✅ Generated stories")

    if result.get("output_file"):
        print(f"📁 Saved to: {result['output_file']}")

    print("\n" + "=" * 70)
    print("Generated User Stories:")
    print("=" * 70)
    print()
    print(result["content"])

    print("\n" + "=" * 70)
    print("\nComplete!")
