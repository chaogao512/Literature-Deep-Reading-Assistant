<div align="center">
  <img src="assets/readme/literature-deep-reading-assistant-icon.png" width="180" alt="文献精读助手图标">

# 文献精读助手

把一篇学术文献整理成可回溯的 Obsidian 精读笔记。

[English](README.md) · [下载 ccswitch 安装包](dist/literature-deep-reading-assistant-v0.1.0-ccswitch.zip) · [版本记录](CHANGELOG.md)
</div>

## 它解决什么问题

文献精读助手是一个 Codex Skill。它一次处理一篇本地 PDF 或 Zotero 文献，按照“定位、解构、取证、重构、审辨、迁移、凝练”七个阶段生成 Markdown 文件，而不是交付一篇难以复用的长摘要。

这个 Skill 最看重证据定位。凡是后续可能用于引证的判断，都应回到 `03-取证.md` 中的具体证据块。证据块记录原文短摘录或忠实转述、证据类型、PDF 页序与正文页码，以及它所支持的命题。

它可以减轻整理工作，但不能替代原文阅读、引文核对和研究者的最终判断。

## 何时自动触发

用户提供或指向**一篇学术文献**，并提出以下任一要求时，应自动触发本 Skill：

- 精读、深读、系统阅读或批判性阅读文献；
- 分析论文的研究问题、概念、理论、方法、证据、机制、发现、结论或局限；
- 生成文献精读笔记、阅读卡、证据卡或 Obsidian 文献笔记；
- 从 Zotero 读取一篇文献并形成可追溯的精读产物；
- 提取能够回链到原文和页码的学术命题。

也可以显式调用：

```text
使用 $literature-deep-reading-assistant 精读这篇 PDF。
```

以下任务不应自动触发：只查找或推荐文献，只做 PDF 转换、OCR、全文翻译或参考文献格式，多篇文献的系统综述、元分析和横向综合，以及在没有全文时根据题名或摘要猜测论文内容。

## 七阶段精读

| 阶段 | 要回答的问题 | 主要产物 |
|---|---|---|
| 01 定位 | 这是什么类型的文献，应该怎样读？ | 文献画像、阅读策略卡 |
| 02 解构 | 作者如何搭建论证？ | 论证链、文章骨架 |
| 03 取证 | 每个重要观点凭什么成立？ | 页码级原始证据 |
| 04 重构 | 可以重新建立怎样的知识结构？ | 概念卡、命题卡、关系卡、框架卡 |
| 05 审辨 | 作者提出、论证和实际证明了什么？ | 概念、逻辑、方法、证据与边界审查 |
| 06 迁移 | 这篇文献如何进入具体研究？ | `CITE`、`CONCEPT`、`FRAMEWORK`、`METHOD`、`EVIDENCE`、`GAP` 等标签 |
| 07 凝练 | 去掉摘要式复述后，真正留下什么？ | 核心命题、知识增量、可信边界与下一步 |

文献类型决定精读模块。理论论文不会被强行套入“样本、量表、显著性”模板，实证论文也不会只剩概念罗列。

## 产物目录

```text
安全化短题名/
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

一项原始证据采用固定格式：

```markdown
### E01 核心定义

- 原文短摘录或忠实转述：忠实转述：作者将该概念界定为……
- 证据类型：作者定义
- 页码：PDF 第 8 页；正文标注第 126 页
- 对应命题：P01 ……

^e01
```

其他文件使用 `[[03-取证#^e01]]` 直接回到该证据，而不是只链接到整个文件。

## 输入与文档读取

### 本地 PDF

用户没有指定输出目录时，产物放在 PDF 所在目录。Skill 不复制、不移动，也不重命名原始 PDF。

处理前会先检查 PDF 是否有可用文本层。普通 PDF 直接读取；当前环境已经安装兼容的转换或 OCR Skill 时，可以按需调用。Skill 不自行安装这些依赖。

如果 PDF 完全由扫描图片组成，且当前没有 OCR 能力，任务会停止并明确说明文档不可读。它不会拿残缺文本继续生成“完整精读”。

### Zotero

Zotero 路线只读取，不修改条目和附件。Skill 记录 item key、citation key 和附件 key，优先读取 PDF 附件。用户没有指定输出目录时，Skill 会先询问，不把笔记写进 Zotero 的受管存储目录。

## 引用格式

默认采用 GB/T 7714—2025，用户可以指定其他格式。元数据缺失时保留“待核实”，不补造作者、卷期、页码或 DOI。

## 通过 ccswitch 安装

1. 下载 [`literature-deep-reading-assistant-v0.1.0-ccswitch.zip`](dist/literature-deep-reading-assistant-v0.1.0-ccswitch.zip)。
2. 在 ccswitch 中导入 ZIP。
3. 新建任务，上传一篇 PDF，或指定一条 Zotero 文献。

安装包只包含运行所需文件。解压后，`SKILL.md` 直接位于根目录，另有 `agents/`、`references/`、`scripts/` 和 `assets/`。

## 调用示例

```text
使用 $literature-deep-reading-assistant 精读这篇文献，产物放入 /path/to/vault/Literature。
```

```text
从 Zotero 读取《……》，第六阶段围绕教育数据治理进行迁移分析，引用格式采用 GB/T 7714—2025。
```

```text
批判性精读这篇定量研究。每项结论都要回链到页码级原始证据。
```

## 仓库结构

- `literature-deep-reading-assistant/`：可安装 Skill 源文件；
- `tests/`：确定性脚本测试；
- `tools/package_ccswitch.py`：打包并校验 ccswitch 安装包；
- `assets/readme/`：GitHub 展示资源；
- `dist/`：带版本号的 ZIP 和 SHA-256 校验文件；
- `examples/`：用于说明格式的虚构小样；
- `docs/superpowers/specs/`：经确认的设计规格。

## 当前边界

- v0.1.0 每次只处理一篇文献。
- 不执行系统综述、元分析或跨文献综合。
- OCR 是可选能力，依赖当前环境已经存在的兼容 Skill。
- OCR 结果或 Zotero 索引全文中的页码仍需回到 PDF 核对。
- 精读产物是研究辅助材料。研究者核对对应页面后，才能把其中内容作为正式引文使用。

## 许可证

[MIT](LICENSE) © 2026 chao
