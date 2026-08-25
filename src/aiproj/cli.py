from __future__ import annotations

import argparse
import sys

from .context import compile_context
from .init_layer import initialize
from .repository import find_repo_root
from .update import create_update_proposal


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="aiproj",
        description="Project-owned cognitive context for long-term AI participation.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="Initialize the .ai/ cognitive layer")
    init.add_argument("--force", action="store_true", help="Overwrite existing generated files")

    context = sub.add_parser("context", help="Compile task-relevant project context")
    context.add_argument("task", help="Task or intent to compile context for")
    context.add_argument("--max-files", type=int, default=8, help="Maximum repository excerpts")

    sub.add_parser("update", help="Create a reviewable knowledge delta from Git changes")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        root = find_repo_root()
        if args.command == "init":
            created = initialize(root, force=args.force)
            if created:
                print("Initialized project cognitive layer:")
                for path in created:
                    print(f"  {path.relative_to(root)}")
            else:
                print("No files changed; .ai/ already exists. Use --force to overwrite generated files.")
            return 0

        if args.command == "context":
            print(compile_context(root, args.task, max_files=max(1, args.max_files)), end="")
            return 0

        if args.command == "update":
            proposal = create_update_proposal(root)
            print(f"Created knowledge delta proposal: {proposal.relative_to(root)}")
            print("Updated .ai/state.md")
            return 0
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
