#!/usr/bin/env python3
"""Bump the version in pyproject.toml and write it to GITHUB_OUTPUT.

Usage: python scripts/bump_version.py <major|minor|patch>
"""
import os
import re
import sys
from pathlib import Path

TOML_PATH = Path(__file__).parent.parent / "pyproject.toml"
VERSION_RE = re.compile(r'^(version\s*=\s*")(\d+)\.(\d+)\.(\d+)(")', re.MULTILINE)


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] not in ("major", "minor", "patch"):
        sys.exit("Usage: bump_version.py <major|minor|patch>")

    bump = sys.argv[1]
    content = TOML_PATH.read_text(encoding="utf-8")
    m = VERSION_RE.search(content)
    if not m:
        sys.exit("Could not find version = \"X.Y.Z\" in pyproject.toml")

    major, minor, patch = int(m.group(2)), int(m.group(3)), int(m.group(4))
    if bump == "major":
        major += 1; minor = 0; patch = 0
    elif bump == "minor":
        minor += 1; patch = 0
    else:
        patch += 1

    new_version = f"{major}.{minor}.{patch}"
    new_content = VERSION_RE.sub(
        lambda _: f'{m.group(1)}{new_version}{m.group(5)}', content
    )
    TOML_PATH.write_text(new_content, encoding="utf-8")
    print(new_version)

    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a", encoding="utf-8") as f:
            f.write(f"version={new_version}\n")


if __name__ == "__main__":
    main()
