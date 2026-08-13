from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
import shutil
import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "literature-deep-reading-assistant" / "scripts"


def load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


safe_title = load("safe_title")
audit_links = load("audit_evidence_links")


class RepositoryContractTests(unittest.TestCase):
    def test_skill_metadata_and_runtime_assets(self):
        skill_root = ROOT / "literature-deep-reading-assistant"
        skill_text = (skill_root / "SKILL.md").read_text(encoding="utf-8")
        frontmatter = skill_text.split("---", 2)[1]
        self.assertIn("name: literature-deep-reading-assistant", frontmatter)
        self.assertIn("description:", frontmatter)
        self.assertNotIn("TODO", skill_text)
        self.assertIn("精读", frontmatter)
        self.assertIn("Zotero", frontmatter)
        agent_text = (skill_root / "agents" / "openai.yaml").read_text(encoding="utf-8")
        for icon in re.findall(r'icon_(?:small|large): "\./([^"]+)"', agent_text):
            self.assertTrue((skill_root / icon).is_file(), icon)

    def test_readme_local_links_exist(self):
        for readme in (ROOT / "README.md", ROOT / "README.zh-CN.md"):
            text = readme.read_text(encoding="utf-8")
            for target in re.findall(r'\[[^\]]+\]\((?!https?://|#)([^)]+)\)', text):
                self.assertTrue((ROOT / target).exists(), f"{readme.name}: {target}")

    def test_packager_source_contract(self):
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        self.assertRegex(version, r"^\d+\.\d+\.\d+$")
        self.assertIn(f"## [{version}]", (ROOT / "CHANGELOG.md").read_text(encoding="utf-8"))
        archive = ROOT / "dist" / f"literature-deep-reading-assistant-v{version}-ccswitch.zip"
        self.assertTrue(archive.is_file())
        with zipfile.ZipFile(archive) as package:
            names = package.namelist()
            self.assertIn("SKILL.md", names)
            self.assertIsNone(package.testzip())
            self.assertFalse(any("__pycache__" in name or name.endswith(".pyc") for name in names))


class SafeTitleTests(unittest.TestCase):
    def test_invalid_characters_and_reserved_name(self):
        self.assertEqual(safe_title.sanitize_title('A/B:C*D?"E<F>G|'), "A B C D E F G")
        self.assertEqual(safe_title.sanitize_title("CON"), "文献-CON")
        self.assertEqual(safe_title.sanitize_title("CON.txt"), "文献-CON.txt")

    def test_empty_and_length(self):
        self.assertEqual(safe_title.sanitize_title(" ... "), "未命名文献")
        self.assertLessEqual(len(safe_title.sanitize_title("文" * 120, 40)), 40)

    def test_collision_is_non_destructive(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "短题名").mkdir()
            self.assertRegex(safe_title.available_name(root, "短题名", "paper-1"), r"^短题名-[0-9a-f]{8}$")


class BundleTests(unittest.TestCase):
    def run_init(self, root: Path) -> Path:
        command = [
            sys.executable, str(SCRIPTS / "init_note_bundle.py"),
            "--title", "测试文献：理论与证据", "--short-title", "测试/文献：理论*证据",
            "--paper-id", "tester2026", "--source-type", "local-pdf",
            "--output-root", str(root), "--json",
        ]
        completed = subprocess.run(command, text=True, capture_output=True, check=True)
        return Path(json.loads(completed.stdout)["output_dir"])

    @staticmethod
    def mark_completed(bundle: Path) -> None:
        for path in bundle.glob("[0-9][0-9]-*.md"):
            text = path.read_text(encoding="utf-8").replace('status: "in-progress"', 'status: "completed"')
            path.write_text(text, encoding="utf-8")

    def test_bundle_structure_and_collision(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            first = self.run_init(root)
            second = self.run_init(root)
            self.assertNotEqual(first, second)
            for index, name in enumerate(["文献索引", "定位", "解构", "取证", "重构", "审辨", "迁移", "凝练"]):
                self.assertTrue((first / f"{index:02d}-{name}.md").is_file())
            self.assertTrue((first / "cards").is_dir())
            self.assertEqual(list((first / "cards").iterdir()), [])
            result = audit_links.audit(first)
            self.assertFalse(result["ok"])
            self.assertTrue(any("not completed" in item for item in result["errors"]))

    def test_evidence_audit_passes_and_catches_dangling_link(self):
        with tempfile.TemporaryDirectory() as temp:
            bundle = self.run_init(Path(temp))
            self.mark_completed(bundle)
            evidence = bundle / "03-取证.md"
            evidence.write_text(evidence.read_text(encoding="utf-8") + """
### E01 核心定义

- 原文短摘录或忠实转述：忠实转述：作者将该概念界定为一个治理过程。
- 证据类型：作者定义
- 页码：PDF 第 3 页；正文标注第 11 页
- 对应命题：P01 该概念具有治理属性。

^e01
""", encoding="utf-8")
            target = bundle / "04-重构.md"
            target.write_text(target.read_text(encoding="utf-8") + "\n支持：[[03-取证#^e01]]\n", encoding="utf-8")
            self.assertTrue(audit_links.audit(bundle)["ok"])
            target.write_text(target.read_text(encoding="utf-8") + "\n[[03-取证#^e99]]\n", encoding="utf-8")
            result = audit_links.audit(bundle)
            self.assertFalse(result["ok"])
            self.assertTrue(any("Dangling" in item for item in result["errors"]))

    def test_evidence_audit_catches_missing_field_and_duplicate_block(self):
        with tempfile.TemporaryDirectory() as temp:
            bundle = self.run_init(Path(temp))
            self.mark_completed(bundle)
            evidence = bundle / "03-取证.md"
            evidence.write_text(evidence.read_text(encoding="utf-8") + """
### E01 不完整证据

- 证据类型：作者主张
- 页码：PDF 第 2 页；正文标注页码待核实
- 对应命题：P01 测试命题

^e01

### E02 重复块

- 原文短摘录或忠实转述：忠实转述：测试。
- 证据类型：作者主张
- 页码：PDF 第 3 页；正文标注页码待核实
- 对应命题：P02 测试命题

^e01
""", encoding="utf-8")
            result = audit_links.audit(bundle)
            self.assertFalse(result["ok"])
            self.assertTrue(any("missing field" in item for item in result["errors"]))
            self.assertTrue(any("Duplicate" in item for item in result["errors"]))


class PdfDiagnosisTests(unittest.TestCase):
    @staticmethod
    def write_pdf(path: Path, text: str | None) -> None:
        if text is None:
            stream = b"q Q"
        else:
            chunks = [text[index:index + 60] for index in range(0, len(text), 60)]
            body = ") Tj T* (".join(chunk.replace("(", "\\(").replace(")", "\\)") for chunk in chunks)
            stream = f"BT /F1 10 Tf 12 TL 72 720 Td ({body}) Tj ET".encode("ascii")
        objects = [
            b"<< /Type /Catalog /Pages 2 0 R >>",
            b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
            b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
            b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream",
        ]
        data = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        offsets = [0]
        for index, obj in enumerate(objects, 1):
            offsets.append(len(data))
            data.extend(f"{index} 0 obj\n".encode("ascii") + obj + b"\nendobj\n")
        xref = len(data)
        data.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
        data.extend(b"0000000000 65535 f \n")
        for offset in offsets[1:]:
            data.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
        data.extend(f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode("ascii"))
        path.write_bytes(data)

    def test_non_pdf_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            fake = Path(temp) / "fake.pdf"
            fake.write_text("not a pdf", encoding="utf-8")
            completed = subprocess.run([sys.executable, str(SCRIPTS / "diagnose_pdf.py"), str(fake), "--json"], text=True, capture_output=True)
            self.assertEqual(completed.returncode, 1)
            self.assertFalse(json.loads(completed.stdout)["valid_pdf"])

    @unittest.skipUnless(shutil.which("pdfinfo") and shutil.which("pdftotext"), "Poppler is unavailable")
    def test_text_pdf_and_image_only_pdf_are_distinguished(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            text_pdf = root / "text.pdf"
            scan_pdf = root / "scan.pdf"
            self.write_pdf(text_pdf, "Academic evidence governance " * 80)
            self.write_pdf(scan_pdf, None)
            text_result = subprocess.run([sys.executable, str(SCRIPTS / "diagnose_pdf.py"), str(text_pdf), "--json"], text=True, capture_output=True, check=True)
            scan_result = subprocess.run([sys.executable, str(SCRIPTS / "diagnose_pdf.py"), str(scan_pdf), "--json"], text=True, capture_output=True, check=True)
            self.assertEqual(json.loads(text_result.stdout)["classification"], "text-readable")
            self.assertEqual(json.loads(scan_result.stdout)["classification"], "image-only")


if __name__ == "__main__":
    unittest.main()
