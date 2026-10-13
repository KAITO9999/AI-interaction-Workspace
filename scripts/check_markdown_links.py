#!/usr/bin/env python3
"""Validate repository-local Markdown links and image paths without network access."""
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", ".github"}
LINK_RE = re.compile(r"!??\[[^\]]*\]\((?:<([^>]+)>|([^\s)]+))(?:\s+[^)]*)?\)")
errors = []
checked = 0

for md in ROOT.rglob("*.md"):
    if any(part in SKIP_DIRS for part in md.relative_to(ROOT).parts):
        continue
    text = md.read_text(encoding="utf-8", errors="replace")
    for match in LINK_RE.finditer(text):
        raw = match.group(1) or match.group(2)
        if not raw or raw.startswith(("http://", "https://", "mailto:", "tel:", "#")):
            continue
        target = unquote(urlsplit(raw).path)
        if not target:
            continue
        checked += 1
        candidate = (md.parent / target).resolve()
        if not candidate.is_relative_to(ROOT):
            errors.append(f"{md.relative_to(ROOT)}: path escapes repository: {raw}")
        elif not candidate.exists():
            errors.append(f"{md.relative_to(ROOT)}: missing local target: {raw}")

if errors:
    print("\n".join(errors), file=sys.stderr)
    print(f"FAILED: {len(errors)} broken local links among {checked} checked.", file=sys.stderr)
    sys.exit(1)
print(f"OK: {checked} repository-local Markdown links checked.")
