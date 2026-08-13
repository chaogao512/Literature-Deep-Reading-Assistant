#!/usr/bin/env python3
"""Diagnose whether a PDF has enough machine-readable text for deep reading."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, text=True, capture_output=True, check=False)


def diagnose(path: Path) -> dict:
    result = {
        "path": str(path.resolve()),
        "valid_pdf": False,
        "encrypted": None,
        "pages": None,
        "characters": 0,
        "characters_per_page": 0.0,
        "classification": "unreadable",
        "reader": None,
        "message": "",
    }
    if not path.is_file():
        result["message"] = "File not found."
        return result
    try:
        with path.open("rb") as stream:
            signature = stream.read(5)
        if signature != b"%PDF-":
            result["message"] = "File does not have a PDF signature."
            return result
    except OSError as exc:
        result["message"] = str(exc)
        return result
    result["valid_pdf"] = True

    pdfinfo = shutil.which("pdfinfo")
    pdftotext = shutil.which("pdftotext")
    if pdfinfo and pdftotext:
        info = run([pdfinfo, str(path)])
        if info.returncode != 0:
            result["message"] = info.stderr.strip() or "pdfinfo could not read the file."
            return result
        for line in info.stdout.splitlines():
            key, _, value = line.partition(":")
            if key == "Pages":
                try:
                    result["pages"] = int(value.strip())
                except ValueError:
                    pass
            elif key == "Encrypted":
                result["encrypted"] = value.strip().lower().startswith("yes")
        with tempfile.TemporaryDirectory(prefix="literature-reader-") as temp_dir:
            text_path = Path(temp_dir) / "paper.txt"
            extract = run([pdftotext, "-layout", str(path), str(text_path)])
            if extract.returncode != 0:
                result["message"] = extract.stderr.strip() or "pdftotext could not extract text."
                return result
            text = text_path.read_text(encoding="utf-8", errors="replace")
        result["reader"] = "poppler"
    else:
        try:
            from pypdf import PdfReader  # type: ignore
        except ImportError:
            result["message"] = "Neither Poppler nor pypdf is available for diagnosis."
            return result
        try:
            reader = PdfReader(str(path))
            result["pages"] = len(reader.pages)
            result["encrypted"] = bool(reader.is_encrypted)
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
            result["reader"] = "pypdf"
        except Exception as exc:  # pypdf exposes multiple parser errors
            result["message"] = f"pypdf could not read the file: {exc}"
            return result

    characters = sum(1 for char in text if not char.isspace())
    pages = result["pages"] or 1
    density = characters / pages
    result["characters"] = characters
    result["characters_per_page"] = round(density, 1)
    if characters == 0 or density < 10:
        result["classification"] = "image-only"
        result["message"] = "The PDF has no usable text layer; OCR is required."
    elif density < 200:
        result["classification"] = "text-sparse"
        result["message"] = "The PDF has a sparse text layer; inspect missing pages or conversion quality."
    else:
        result["classification"] = "text-readable"
        result["message"] = "The PDF has a usable text layer."
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = diagnose(args.pdf)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"{result['classification']}: {result['message']}")
    return 0 if result["classification"] in {"text-readable", "text-sparse", "image-only"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
