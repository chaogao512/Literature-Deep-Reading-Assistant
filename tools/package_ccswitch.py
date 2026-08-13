#!/usr/bin/env python3
"""Build and verify a flat ccswitch-compatible Skill archive."""

from __future__ import annotations

import hashlib
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "literature-deep-reading-assistant"
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
DIST = ROOT / "dist"
ARCHIVE = DIST / f"literature-deep-reading-assistant-v{VERSION}-ccswitch.zip"
ALLOWED_ROOTS = {"SKILL.md", "agents", "references", "scripts", "assets"}
EXCLUDED_PARTS = {"__pycache__", ".DS_Store", ".pytest_cache"}


def include(path: Path) -> bool:
    relative = path.relative_to(SKILL)
    return relative.parts[0] in ALLOWED_ROOTS and not any(part in EXCLUDED_PARTS for part in relative.parts) and path.suffix != ".pyc"


def build() -> tuple[Path, str]:
    if not (SKILL / "SKILL.md").is_file():
        raise FileNotFoundError("Skill entrypoint not found")
    DIST.mkdir(exist_ok=True)
    temp_archive = ARCHIVE.with_suffix(".tmp")
    if temp_archive.exists():
        temp_archive.unlink()
    with zipfile.ZipFile(temp_archive, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(SKILL.rglob("*")):
            if path.is_file() and include(path):
                archive.write(path, path.relative_to(SKILL).as_posix())
    with zipfile.ZipFile(temp_archive) as archive:
        names = archive.namelist()
        bad = [name for name in names if name.startswith("/") or name.split("/")[0] not in ALLOWED_ROOTS]
        if "SKILL.md" not in names or bad:
            raise RuntimeError(f"Invalid archive layout: {bad}")
        if any("__pycache__" in name or name.endswith(".pyc") for name in names):
            raise RuntimeError("Archive contains cache files")
        corrupt = archive.testzip()
        if corrupt:
            raise RuntimeError(f"Corrupt archive entry: {corrupt}")
    shutil.move(temp_archive, ARCHIVE)
    digest = hashlib.sha256(ARCHIVE.read_bytes()).hexdigest()
    relative_archive = ARCHIVE.relative_to(ROOT).as_posix()
    (DIST / "SHA256SUMS").write_text(f"{digest}  {relative_archive}\n", encoding="utf-8")
    return ARCHIVE, digest


if __name__ == "__main__":
    archive, digest = build()
    print(archive)
    print(digest)
