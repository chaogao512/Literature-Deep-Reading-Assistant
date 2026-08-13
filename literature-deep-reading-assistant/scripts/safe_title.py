#!/usr/bin/env python3
"""Create a cross-platform-safe directory name from a paper short title."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from pathlib import Path

INVALID = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
WHITESPACE = re.compile(r"\s+")
RESERVED = {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}


def sanitize_title(title: str, max_length: int = 80) -> str:
    value = unicodedata.normalize("NFC", title or "")
    value = INVALID.sub(" ", value)
    value = WHITESPACE.sub(" ", value).strip(" .")
    if not value:
        value = "未命名文献"
    if value.split(".", 1)[0].upper() in RESERVED:
        value = f"文献-{value}"
    if len(value) > max_length:
        value = value[:max_length].rstrip(" .")
    return value or "未命名文献"


def available_name(root: Path, safe_title: str, stable_id: str) -> str:
    candidate = root / safe_title
    if not candidate.exists():
        return safe_title
    suffix = hashlib.sha256(stable_id.encode("utf-8")).hexdigest()[:8]
    candidate_name = f"{safe_title}-{suffix}"
    counter = 2
    while (root / candidate_name).exists():
        candidate_name = f"{safe_title}-{suffix}-{counter}"
        counter += 1
    return candidate_name


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("title")
    parser.add_argument("--max-length", type=int, default=80)
    parser.add_argument("--output-root", type=Path)
    parser.add_argument("--stable-id", default="")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if args.max_length < 12:
        parser.error("--max-length must be at least 12")
    safe = sanitize_title(args.title, args.max_length)
    if args.output_root:
        safe = available_name(args.output_root, safe, args.stable_id or args.title)
    result = {"original": args.title, "safe_title": safe}
    print(json.dumps(result, ensure_ascii=False) if args.json else safe)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
