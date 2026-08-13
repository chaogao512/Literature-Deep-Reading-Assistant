#!/usr/bin/env python3
"""Initialize a non-destructive Obsidian note bundle from bundled templates."""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import date
from pathlib import Path

from safe_title import available_name, sanitize_title


def yaml_quote(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def render_template(text: str, values: dict[str, str]) -> str:
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def initialize(args: argparse.Namespace) -> Path:
    root = args.output_root.expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    safe = sanitize_title(args.short_title, args.max_title_length)
    name = available_name(root, safe, args.paper_id)
    output = root / name
    output.mkdir()
    (output / "cards").mkdir()

    template_root = Path(__file__).resolve().parent.parent / "assets" / "note-templates"
    required = [f"{number:02d}-{title}.md" for number, title in enumerate(
        ["文献索引", "定位", "解构", "取证", "重构", "审辨", "迁移", "凝练"]
    )]
    missing = [name for name in required if not (template_root / name).is_file()]
    if missing:
        shutil.rmtree(output)
        raise FileNotFoundError(f"Missing templates: {', '.join(missing)}")
    values = {
        "paper_id": yaml_quote(args.paper_id),
        "title": yaml_quote(args.title),
        "source_type": yaml_quote(args.source_type),
        "generated": yaml_quote(date.today().isoformat()),
        "citation_style": yaml_quote(args.citation_style),
    }
    for filename in required:
        source = template_root / filename
        (output / filename).write_text(render_template(source.read_text(encoding="utf-8"), values), encoding="utf-8")
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", required=True)
    parser.add_argument("--short-title", required=True)
    parser.add_argument("--paper-id", required=True)
    parser.add_argument("--source-type", choices=["local-pdf", "zotero"], required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--citation-style", default="GB/T 7714—2025")
    parser.add_argument("--max-title-length", type=int, default=80)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        output = initialize(args)
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 1
    payload = {"ok": True, "output_dir": str(output), "directory_name": output.name}
    print(json.dumps(payload, ensure_ascii=False, indent=2) if args.json else str(output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
