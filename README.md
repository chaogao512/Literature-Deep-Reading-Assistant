<div align="center">
  <img src="assets/readme/literature-deep-reading-assistant-icon.png" width="180" alt="Literature Deep Reading Assistant icon">

# Literature Deep Reading Assistant

Turn one academic paper into a traceable set of Obsidian notes.

[简体中文](README.zh-CN.md) · [Download for ccswitch](dist/literature-deep-reading-assistant-v0.1.0-ccswitch.zip) · [Changelog](CHANGELOG.md)
</div>

## What it does

This Codex Skill reads one paper at a time from a local PDF or a Zotero item. It separates source evidence from interpretation, follows a seven-stage reading process, and writes the result as a small Markdown folder rather than a single long summary.

The central rule is simple: a claim worth citing must lead back to an identifiable evidence block in `03-取证.md`. Each block records a short quotation or faithful paraphrase, evidence type, PDF and printed page numbers, and the proposition it supports.

The Skill helps with research reading. It does not replace checking the original paper or making the final academic judgment.

## When it triggers

The Skill is designed to trigger automatically when a user provides or points to **one academic paper** and asks to:

- deep-read, closely read, systematically read, or critically read it;
- analyze its research question, concepts, theory, method, evidence, mechanism, findings, conclusions, or limitations;
- create literature notes, evidence cards, reading cards, or Obsidian notes;
- extract claims that must link back to original text and page numbers;
- read a paper from Zotero and produce a traceable note bundle.

Explicit invocation also works:

```text
Use $literature-deep-reading-assistant to deeply read this PDF.
```

It should **not** trigger for literature discovery, PDF conversion alone, OCR alone, full-text translation, citation formatting alone, batch reviews, systematic reviews, meta-analyses, or attempts to infer a full paper from only its title or abstract.

## The seven stages

| Stage | Question | Main output |
|---|---|---|
| 01 Position | What kind of paper is this, and how should it be read? | Paper profile and reading strategy |
| 02 Deconstruct | How is the argument built? | Argument chain and paper skeleton |
| 03 Evidence | What supports each important claim? | Page-level evidence blocks |
| 04 Reconstruct | What conceptual and relational structure can be rebuilt? | Concept, proposition, relation, and framework cards |
| 05 Critique | What has the author proposed, argued, or actually demonstrated? | Evidence and boundary audit |
| 06 Transfer | How can this paper be used in a research context? | `CITE`, `CONCEPT`, `FRAMEWORK`, `METHOD`, `EVIDENCE`, and `GAP` notes |
| 07 Synthesize | What remains after the summary is removed? | Core proposition, knowledge gain, credibility boundary, and next step |

The workflow adapts its reading modules to the paper type. A theoretical paper is not forced into a sample–instrument–significance template, and an empirical paper is not reduced to a list of concepts.

## Output folder

```text
Safe short title/
├── 00-文献索引.md
├── 01-定位.md
├── 02-解构.md
├── 03-取证.md
├── 04-重构.md
├── 05-审辨.md
├── 06-迁移.md
├── 07-凝练.md
└── cards/
```

An evidence block looks like this:

```markdown
### E01 Core definition

- 原文短摘录或忠实转述：忠实转述：作者将该概念界定为……
- 证据类型：作者定义
- 页码：PDF 第 8 页；正文标注第 126 页
- 对应命题：P01 ……

^e01
```

Other notes link to the exact block with `[[03-取证#^e01]]`.

## Inputs and document handling

### Local PDF

If no output directory is given, the note folder is created beside the PDF. The source PDF is not copied or renamed.

The Skill first checks whether the PDF has a usable text layer. It reads accessible PDFs directly. If a compatible conversion or OCR Skill is already available, it may use that tool when needed. It never installs those dependencies on its own.

For an image-only scan with no available OCR capability, the run stops and tells the user that the document is currently unreadable. It does not continue from partial text.

### Zotero

The Zotero route is read-only. It records item, citation, and attachment keys, then reads the PDF attachment when available. If the user has not selected an output directory, the Skill asks before writing; it does not place notes inside Zotero's managed storage.

## Citation style

GB/T 7714—2025 is the default. Another style can be requested. Missing bibliographic fields remain visibly marked for verification; the Skill does not invent author names, issue numbers, pages, or DOIs.

## Install with ccswitch

1. Download [`literature-deep-reading-assistant-v0.1.0-ccswitch.zip`](dist/literature-deep-reading-assistant-v0.1.0-ccswitch.zip).
2. Import the ZIP through ccswitch.
3. Start a new task and attach one PDF, or point the assistant to one Zotero item.

The archive contains only runtime files. `SKILL.md` is at the ZIP root, followed by `agents/`, `references/`, `scripts/`, and `assets/`.

## Example prompts

```text
Use $literature-deep-reading-assistant to read this paper. Put the notes in my Obsidian vault at /path/to/vault/Literature.
```

```text
Read the Zotero paper “...” and focus the transfer stage on educational data governance. Use GB/T 7714—2025.
```

```text
Critically read this quantitative study. Keep every conclusion linked to its page-level evidence.
```

## Repository layout

- `literature-deep-reading-assistant/` — installable Skill source;
- `tests/` — deterministic script tests;
- `tools/package_ccswitch.py` — release packager and archive verifier;
- `assets/readme/` — GitHub presentation assets;
- `dist/` — versioned ccswitch ZIP and SHA-256 checksum;
- `examples/` — small, fictional format examples;
- `docs/superpowers/specs/` — approved design specification.

## Limitations

- Version 0.1.0 handles one paper per run.
- It does not perform systematic review or cross-paper synthesis.
- OCR is optional and depends on a compatible Skill already being present.
- Page numbers extracted from OCR or Zotero full-text indexes still require checking against the PDF.
- A completed note is a research aid, not a verified quotation database until the researcher checks the cited pages.

## License

[MIT](LICENSE) © 2026 chao
