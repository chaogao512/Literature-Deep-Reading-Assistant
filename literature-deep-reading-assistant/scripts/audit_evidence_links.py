#!/usr/bin/env python3
"""Audit evidence fields, Obsidian block IDs, and evidence backlinks."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

BLOCK = re.compile(r"(?m)^\^(e\d{2,})\s*$", re.IGNORECASE)
LINK = re.compile(r"\[\[03-取证#\^(e\d{2,})\]\]", re.IGNORECASE)
EVIDENCE_HEADER = re.compile(r"(?m)^###\s+(E\d{2,})\b[^\n]*$")
FIELDS = ["原文短摘录或忠实转述", "证据类型", "页码", "对应命题"]
HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)


def audit(bundle: Path) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    required_files = [f"{i:02d}-{name}.md" for i, name in enumerate(
        ["文献索引", "定位", "解构", "取证", "重构", "审辨", "迁移", "凝练"]
    )]
    for filename in required_files:
        path = bundle / filename
        if not path.is_file():
            errors.append(f"Missing required file: {filename}")
            continue
        status = re.search(r'(?m)^status:\s*["\']?([^"\'\n]+)', path.read_text(encoding="utf-8"))
        if not status or status.group(1).strip() != "completed":
            errors.append(f"Stage is not completed: {filename}")
    evidence_path = bundle / "03-取证.md"
    if not evidence_path.is_file():
        return {"ok": False, "errors": errors, "warnings": warnings, "evidence_count": 0, "link_count": 0}
    evidence_text = HTML_COMMENT.sub("", evidence_path.read_text(encoding="utf-8"))
    blocks = BLOCK.findall(evidence_text)
    duplicate_blocks = sorted(key for key, count in Counter(key.lower() for key in blocks).items() if count > 1)
    for block in duplicate_blocks:
        errors.append(f"Duplicate evidence block ID: ^{block}")

    headers = list(EVIDENCE_HEADER.finditer(evidence_text))
    for index, match in enumerate(headers):
        start = match.end()
        end = headers[index + 1].start() if index + 1 < len(headers) else len(evidence_text)
        section = evidence_text[start:end]
        eid = match.group(1)
        expected_block = f"^{eid.lower()}"
        if not re.search(rf"(?m)^{re.escape(expected_block)}\s*$", section, re.IGNORECASE):
            errors.append(f"{eid} has no matching block ID {expected_block}")
        for field in FIELDS:
            field_match = re.search(rf"(?m)^-\s*{re.escape(field)}：\s*(.*)$", section)
            if not field_match or not field_match.group(1).strip():
                errors.append(f"{eid} missing field: {field}")

    all_text = "\n".join(HTML_COMMENT.sub("", path.read_text(encoding="utf-8")) for path in bundle.rglob("*.md"))
    links = LINK.findall(all_text)
    block_set = {block.lower() for block in blocks}
    for target in sorted(set(target.lower() for target in links)):
        if target not in block_set:
            errors.append(f"Dangling evidence link: [[03-取证#^{target}]]")
    linked = {target.lower() for target in links}
    for block in sorted(block_set - linked):
        warnings.append(f"Evidence block has no backlink from another note: ^{block}")
    if not headers:
        warnings.append("No evidence entries found; the bundle cannot be marked completed.")
    return {
        "ok": not errors and bool(headers),
        "errors": errors,
        "warnings": warnings,
        "evidence_count": len(headers),
        "link_count": len(links),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = audit(args.bundle.expanduser().resolve())
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("PASS" if result["ok"] else "FAIL")
        for item in result["errors"]:
            print(f"ERROR: {item}")
        for item in result["warnings"]:
            print(f"WARNING: {item}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
