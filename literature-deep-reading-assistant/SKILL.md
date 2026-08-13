---
name: literature-deep-reading-assistant
description: Deep-read one academic paper from a local PDF or Zotero item and create traceable Markdown notes for Obsidian through the seven stages of positioning, deconstruction, evidence extraction, reconstruction, critique, research transfer, and synthesis. Use automatically when the user asks to 精读、深读、系统阅读或批判性阅读 a single paper; analyze its research question, concepts, theory, method, evidence, mechanism, findings, conclusions, or limitations; create 文献精读笔记、证据卡、阅读卡 or Obsidian literature notes; or extract claims that must link back to original text and page numbers. Do not use for literature discovery, PDF-only conversion/OCR, citation-format-only tasks, translation, batch review, systematic review, meta-analysis, or guesses based only on a title or abstract.
---

# 文献精读助手

一次处理一篇学术文献，将原文证据、分析判断和研究迁移分层保存为可回溯的 Markdown 产物。默认使用简体中文；用户明确要求时使用其他语言。

## 自动触发边界

在以下任一情形自动执行本 Skill：

- 用户提供单篇 PDF，并要求精读、深读、系统阅读、批判性阅读或生成研究型阅读笔记；
- 用户指明一个 Zotero 条目，并要求分析全文或生成 Obsidian 笔记；
- 用户要求分析单篇论文的研究问题、概念、理论、方法、证据、机制、发现、结论或边界；
- 用户要求形成带页码、原文证据和 Obsidian 回链的观点、命题或证据卡；
- 用户显式调用 `$literature-deep-reading-assistant`。

不要因以下请求自动执行：只查找或推荐文献；只做 OCR、PDF 转换、全文翻译或引用格式；处理多篇文献的系统综述、元分析或横向综合；没有可访问全文却要求根据题名或摘要推测全文。v0.1.0 一次只处理一篇文献；收到多篇时请用户逐篇处理。

## 必读资源

执行每次精读时读取：

1. `references/document-routing.md`：输入、PDF 与 Zotero 路由；
2. `references/seven-stage-workflow.md`：七阶段任务与输出；
3. `references/evidence-contract.md`：强制证据格式与回链规则；
4. `references/obsidian-output.md`：目录、YAML 和双链规范。

根据文献画像再读取 `references/literature-type-routing.md`。生成参考文献前读取 `references/citation-policy.md`。

## 工作流

### 1. 确认输入与输出位置

- 接收一个本地 PDF，或一个 Zotero 文献条目及其 PDF 附件。
- 用户指定 Obsidian Vault 或输出目录时写入该位置。
- 本地 PDF 未指定输出目录时，写入 PDF 所在目录。
- Zotero 文献未指定输出目录时先询问用户；不得写入 Zotero 受管附件目录。
- 默认不复制、移动或重命名原始 PDF，也不永久保存私人路径。

### 2. 诊断可读性并选择读取路线

对本地 PDF 先运行：

```bash
python3 scripts/diagnose_pdf.py "/absolute/path/paper.pdf" --json
```

遵守 `references/document-routing.md`。只调用当前环境已经存在的 PDF、转换或 OCR 能力，不自动安装缺失 Skill。纯扫描 PDF 且没有可用 OCR 能力时停止并告诉用户：“该 PDF 当前不可读，请决定是否自行采用 OCR 工具。”不得根据残缺内容继续精读。

Zotero 输入只执行读取操作：检索条目、确认唯一匹配、读取题录和附件。不得修改 Zotero 条目或附件。

### 3. 建立安全目录与产物骨架

从完整题名提炼忠实、可辨识的短题名，不添加原题没有的学术判断。使用脚本安全化并初始化：

```bash
python3 scripts/init_note_bundle.py \
  --title "完整题名" \
  --short-title "短题名" \
  --paper-id "citation-key-or-stable-id" \
  --source-type local-pdf \
  --output-root "/absolute/output/root"
```

目录名称必须使用脚本返回值，不能手工保留 `/ \\ : * ? \" < > |`、控制字符、末尾空格或句点。不得覆盖已有目录。

### 4. 按七阶段精读

严格执行“定位 → 解构 → 取证 → 重构 → 审辨 → 迁移 → 凝练”。先忠实还原，后独立评价；先建立全文结构，再逐项取证。文献画像决定激活哪些分析模块，不能把理论、定量、定性、综述、政策或设计研究套入同一模板。

保持三层分离：

- 原文层：作者明确说了什么；
- 分析层：如何理解论证、关系与机制；
- 研究层：可信边界及对用户研究的意义。

### 5. 建立证据与卡片

所有可供后续引证的重要判断，必须在 `03-取证.md` 中具有真实证据项。固定格式为“原文短摘录或忠实转述＋证据类型＋页码＋对应命题”，并在证据项末尾设置唯一块标识，如 `^e01`。

其他文件使用 `[[03-取证#^e01]]` 精确回链。概念卡、命题卡、关系卡和框架卡按文献需要生成，不能为填满目录而制造空卡。

### 6. 生成引用与来源链接

默认使用 GB/T 7714—2025；用户可以指定其他格式。元数据不完整时保留“待核实”，不得臆造。Zotero 文献记录 item key、citation key、附件 key 和可用跳转链接；本地 PDF 记录绝对来源路径、文件大小和 SHA-256。

### 7. 审计后交付

运行：

```bash
python3 scripts/audit_evidence_links.py "/absolute/path/短题名目录" --json
```

只有满足以下条件才能报告“精读完成”：

- 全文可读，或 OCR 结果足以覆盖全文且已说明来源；
- `00` 至 `07` 八个阶段文件齐全；
- 关键判断均标明作者原意、分析性判断或待核实；
- 证据四字段完整；
- 块标识唯一，所有证据回链均可解析；
- 引用信息和页码没有被臆造；
- 审计退出码为 0。

若任何条件不满足，明确列出未完成项，不得以摘要或部分笔记替代完整精读。

## 学术边界

- 不发明事实、原文、页码、统计结果、作者信息、DOI 或参考文献字段。
- 直接引语保持原文；忠实转述必须标明为转述。
- PDF 文件页序与正文标注页码分开记录，无法确认时写“待核实”。
- 不把作者主张当作已验证事实，也不把模型推断当作作者结论。
- 最终引文核对、学术判断与研究写作责任属于用户。
