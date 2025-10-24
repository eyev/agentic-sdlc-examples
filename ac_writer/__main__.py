"""
Entry point for running the AC Writer agent as a module.

Usage:
    python -m ac_writer 01           # Generate AC from stories for file 01
    python -m ac_writer 02           # Generate AC from stories for file 02
    python -m ac_writer 02 --idea    # Generate AC directly from idea (skip stories)
"""

import argparse
import sys
from pathlib import Path

from .agent import generate_ac


def find_file(prefix: str, source_type: str) -> str:
    """Find file matching the prefix in the appropriate directory"""
    data_dir = Path(__file__).parent.parent / "data"

    if source_type == "story":
        search_dir = data_dir / "stories"
        pattern = f"{prefix}*.md"
    else:
        search_dir = data_dir / "ideas"
        pattern = f"{prefix}*.md"

    matches = list(search_dir.glob(pattern))

    if not matches:
        print(f"❌ No files found matching '{prefix}' in {search_dir}")
        sys.exit(1)

    if len(matches) > 1:
        print(f"⚠️  Multiple files found matching '{prefix}':")
        for m in matches:
            print(f"   - {m.name}")
        print(f"Using: {matches[0].name}")

    return matches[0].name


def check_story_exists(prefix: str) -> bool:
    """Check if a story file exists for the given prefix"""
    data_dir = Path(__file__).parent.parent / "data"
    stories_dir = data_dir / "stories"
    pattern = f"{prefix}*-stories.md"

    matches = list(stories_dir.glob(pattern))
    return len(matches) > 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate acceptance criteria from user stories (recommended) or feature ideas"
    )
    parser.add_argument(
        "file_prefix",
        help="File prefix (e.g., '01', '02') or full filename",
    )
    parser.add_argument(
        "--idea",
        action="store_true",
        help="Generate AC directly from feature idea (skip user stories check)",
    )
    parser.add_argument(
        "--no-save", action="store_true", help="Don't save output to file"
    )

    args = parser.parse_args()

    # Extract prefix from input
    if args.file_prefix.endswith((".md", ".feature")):
        # Extract prefix from full filename (e.g., "02-feat-login.md" -> "02")
        prefix = args.file_prefix.split("-")[0]
    else:
        prefix = args.file_prefix

    # Determine source type
    if args.idea:
        # User explicitly wants to generate from idea
        source_type = "idea"
        filename = find_file(prefix, "idea")
    else:
        # Default: check if stories exist first
        if not check_story_exists(prefix):
            print("=" * 70)
            print("❌ No user stories found!")
            print("=" * 70)
            print(f"\nCannot generate AC for '{prefix}' - no story file exists.")
            print("\nRecommended workflow:")
            print(f"  1. Generate user stories first:  python -m user_story {prefix}")
            print(f"  2. Then generate AC:             python -m ac_writer {prefix}")
            print("\nAlternatively, generate AC directly from the idea:")
            print(f"  python -m ac_writer {prefix} --idea")
            print()
            sys.exit(1)

        source_type = "story"
        filename = find_file(prefix, "story")

    print("=" * 70)
    print("Acceptance Criteria Writer Agent")
    print("=" * 70)
    print(f"File: {filename}")
    print(f"Source: {source_type}")
    print("-" * 70)

    # Generate AC
    result = generate_ac(
        filename, source_type=source_type, save_output=not args.no_save
    )

    print(f"\n✅ Generated AC")

    if result.get("output_file"):
        print(f"📁 Saved to: {result['output_file']}")

    print("\n" + "=" * 70)
    print("Generated Acceptance Criteria:")
    print("=" * 70)
    print()
    print(result["content"])

    print("\n" + "=" * 70)
    print("\nComplete!")
