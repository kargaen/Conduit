#!/usr/bin/env python3
"""Flag project-specific content in an AGENTS.md.

A linter, not an oracle. It catches mechanical leaks — paths, identifiers, vendor
names. It cannot catch semantic ones ("the app uses an MVC pattern"). Read the file.

Usage:  python leak_check.py AGENTS.md
Exit:   0 = clean, 1 = leaks found
"""
import re
import sys

# Documents any repo is allowed to reference by name.
DOC_WHITELIST = {"AGENTS.md", "ARCHITECTURE.md", "README.md", "CODEOWNERS"}

VENDORS = [
    "react", "vue", "svelte", "angular", "next.js", "nextjs", "django", "flask",
    "fastapi", "celery", "redis", "postgres", "postgresql", "mysql", "sqlite",
    "mongodb", "expo", "firebase", "supabase", "stripe", "vercel", "netlify",
    "aws", "gcp", "azure", "docker", "kubernetes", "dokploy", "qt", "pyside",
    "pyqt", "tkinter", "numpy", "scipy", "pandas", "matplotlib", "pytest",
    "jest", "vitest", "typescript", "rust", "golang", "app store", "play store",
]

CHECKS = [
    ("literal file path",
     re.compile(r"(?<![\w`])(?:\./|/)?(?:[\w.-]+/){1,}[\w.-]+\.\w{1,5}\b")),
    ("code identifier (camelCase/PascalCase)",
     re.compile(r"\b(?:[a-z]+[A-Z]\w*|[A-Z][a-z]+[A-Z]\w*)\b")),
    ("named skill",
     re.compile(r"\.claude/skills/[\w-]+")),
    ("vendor or framework name",
     re.compile(r"\b(" + "|".join(re.escape(v) for v in VENDORS) + r")\b", re.I)),
]

DOC_RE = re.compile(r"\b([A-Z][A-Z0-9_]*\.md)\b")
FENCE_RE = re.compile(r"^\s*```")


def scan(path):
    """Scan every line. Fenced blocks are tagged, never skipped.

    Skipping fences is tempting — example blocks are illustrative, not normative.
    But an unbalanced fence then silently hides the rest of the file, and a leaked
    vendor name in an example is still copied into every repo. Tag, don't skip.
    """
    lines = open(path, encoding="utf-8").read().splitlines()
    fences = sum(1 for l in lines if FENCE_RE.match(l))
    warnings = []
    if fences % 2:
        warnings.append(
            f"{fences} code-fence markers (odd) — a fence is unbalanced or malformed. "
            "Fix it: markdown renderers will misparse this file too.")

    findings, in_fence = [], False
    for n, line in enumerate(lines, 1):
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        where = "example" if in_fence else "prose"

        for label, rx in CHECKS:
            for m in rx.finditer(line):
                findings.append((n, where, label, m.group(0)))

        for m in DOC_RE.finditer(line):
            if m.group(1) not in DOC_WHITELIST:
                findings.append((n, where, "non-whitelisted document", m.group(1)))
    return findings, warnings


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    path = sys.argv[1]
    findings, warnings = scan(path)

    for w in warnings:
        print(f"WARNING: {w}\n")

    if not findings:
        print(f"{path}: clean — no mechanical leaks found.")
        print("Semantic leaks (declared architecture, assumed toolchain, domain "
              "examples) are not detectable here. Read the file.")
        return 1 if warnings else 0

    prose = [f for f in findings if f[1] == "prose"]
    example = [f for f in findings if f[1] == "example"]

    print(f"{path}: {len(prose)} leak(s) in prose, {len(example)} in examples\n")
    for group, title in ((prose, "PROSE — normative, fix these"),
                         (example, "EXAMPLES — illustrative, but still broadcast")):
        if not group:
            continue
        print(f"{title}")
        for n, _, label, text in group:
            print(f"  line {n:>4}  {label:<38} {text!r}")
        print()

    print("Each is a candidate, not a verdict. For each, decide:")
    print("  universal            -> keep")
    print("  general + local noun -> parameterize, move noun to ARCHITECTURE.md")
    print("  project fact         -> route out (see SKILL.md destination table)")
    return 1


if __name__ == "__main__":
    sys.exit(main())
