# 文档读取路由

## 本地 PDF

1. 运行 `scripts/diagnose_pdf.py`。
2. `classification=text-readable`：使用现有 PDF 能力读取全文；图表、跨栏、脚注或页码关系重要时渲染相关页面核验。
3. `classification=text-sparse`：先检查是否为局部扫描、公式密集或提取失败。环境中已有兼容文档转换 Skill 时可以调用；没有时直接使用可读文本，并把缺失范围列为证据限制。
4. `classification=image-only`：只在环境中已有 OCR Skill 时调用，例如 `academic-pdf-to-md` 或 MinerU。不要自动安装。
5. `classification=unreadable`：停止并报告准确原因。

`convert-documents-to-markdown` 及其 anydoc 路线不支持纯图片扫描 PDF 的 OCR。不得把转换失败误报为全文已读取。

## Zotero

1. 检查 Zotero 本地读取能力。
2. 使用题名、作者、年份或 item key 搜索；多个匹配时请用户确认。
3. 读取题录和子附件，优先选择 PDF。
4. 有 PDF 路径时按本地 PDF 路由处理；只有索引全文时可以分析，但证据页码写“页码待核实”。
5. 保存 item key、citation key、attachment key 与可用链接。Zotero item key 与 citation key 不是同一标识。
6. 不导入、删除、修改、移动或复制 Zotero 内容。

## 停止条件

- 文件不存在、不是有效 PDF、加密且无法读取；
- 纯扫描 PDF 且没有可用 OCR 能力；
- 只取得题名、摘要或严重残缺的正文；
- Zotero 匹配不唯一且用户尚未确认。

停止时保留诊断结果，不生成看似完整的七阶段产物。
