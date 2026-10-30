#!/usr/bin/env python3
"""Generate a bounded, read-only directory tree for repository onboarding."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Sequence


IGNORE_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".agents",
    ".claude",
    ".idea",
    ".vscode",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "bin",
    "obj",
    "dist",
    "build",
    "out",
    "coverage",
    "TestResults",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
}

IGNORE_EXTS = {
    ".exe",
    ".dll",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".pdf",
    ".zip",
    ".tar",
    ".gz",
    ".pdb",
    ".so",
    ".pyc",
    ".class",
    ".svg",
    ".ico",
}

DEFAULT_MAX_LINES = 1000


def positive_int(value: str) -> int:
    """Accept a positive integer for the output line limit."""
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            "must be a positive integer"
        ) from exc

    if parsed < 1:
        raise argparse.ArgumentTypeError("must be a positive integer")

    return parsed


def non_negative_int(value: str) -> int:
    """Accept a non-negative integer for traversal depth."""
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            "must be a non-negative integer"
        ) from exc

    if parsed < 0:
        raise argparse.ArgumentTypeError("must be a non-negative integer")

    return parsed


def generate_tree(
    start_path: Path,
    max_depth: int,
    max_lines: int,
) -> int:
    """
    Print a directory tree without reading file contents.

    Depth semantics:
    - Root directory is depth 0.
    - A direct child directory is depth 1.
    - Files are shown inside directories whose depth is <= max_depth.
    - Subdirectories beyond max_depth are not traversed.

    Returns:
    - 0: scan completed.
    - 1: scan failed or was incomplete because of an access error.
    - 2: path is invalid.
    - 3: output was truncated at max_lines.
    """
    if not start_path.exists():
        print(f"[Error] Path does not exist: {start_path}", file=sys.stderr)
        return 2

    if not start_path.is_dir():
        print(f"[Error] Path is not a directory: {start_path}", file=sys.stderr)
        return 2

    scan_errors: list[str] = []
    lines_written = 0

    def on_error(error: OSError) -> None:
        # Report the path and error type without printing file contents.
        location = error.filename or "<unknown>"
        scan_errors.append(f"{type(error).__name__}: {location}")

    def emit(line: str) -> bool:
        nonlocal lines_written

        if lines_written >= max_lines:
            return False

        print(line)
        lines_written += 1
        return True

    print(
        f"--- Project Tree "
        f"(max depth: {max_depth}, max tree lines: {max_lines}) ---"
    )

    try:
        for root, dirs, files in os.walk(
            start_path,
            topdown=True,
            onerror=on_error,
            followlinks=False,
        ):
            root_path = Path(root)
            relative = root_path.relative_to(start_path)
            level = len(relative.parts)

            # Sort and filter before os.walk traverses children.
            dirs[:] = sorted(
                directory
                for directory in dirs
                if directory not in IGNORE_DIRS
                and not (root_path / directory).is_symlink()
            )

            # Stop traversal at the requested boundary.
            if level >= max_depth:
                dirs[:] = []

            folder_name = root_path.name or str(root_path)
            indent = " " * 4 * level

            if not emit(f"{indent}{folder_name}/"):
                print(
                    f"[Truncated] Reached the limit of {max_lines} tree lines.",
                    file=sys.stderr,
                )
                return 3

            subindent = " " * 4 * (level + 1)

            for filename in sorted(files):
                file_path = root_path / filename

                # Do not display symlinks; do not inspect their targets.
                if file_path.is_symlink():
                    continue

                if file_path.suffix.lower() in IGNORE_EXTS:
                    continue

                if not emit(f"{subindent}{filename}"):
                    print(
                        f"[Truncated] Reached the limit of "
                        f"{max_lines} tree lines.",
                        file=sys.stderr,
                    )
                    return 3

    except OSError as error:
        print(
            f"[Error] Scan failed: {type(error).__name__}: "
            f"{error.filename or '<unknown>'}",
            file=sys.stderr,
        )
        return 1

    if scan_errors:
        for error in scan_errors:
            print(f"[Error] Could not scan: {error}", file=sys.stderr)
        return 1

    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate a bounded directory tree for AI onboarding."
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Target directory to scan; defaults to the current directory.",
    )
    parser.add_argument(
        "--depth",
        type=non_negative_int,
        default=3,
        help="Maximum directory depth; root is depth 0 (default: 3).",
    )
    parser.add_argument(
        "--max-lines",
        type=positive_int,
        default=DEFAULT_MAX_LINES,
        help=(
            "Maximum number of tree lines, excluding the header "
            f"(default: {DEFAULT_MAX_LINES})."
        ),
    )

    args = parser.parse_args(argv)

    # Make depth calculation independent of ".", "..", and repeated names.
    start_path = Path(args.path).resolve()

    return generate_tree(
        start_path=start_path,
        max_depth=args.depth,
        max_lines=args.max_lines,
    )


if __name__ == "__main__":
    sys.exit(main())