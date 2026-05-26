---
name: fetch-bibtex
description: 当用户提供模糊的论文题目，要求获取、生成或查询 BibTeX 参考文献格式时触发此技能。绝对禁止 AI 编造或猜测参考文献的年份、卷号和页码。
---

# Fetch Authentic BibTeX via Crossref + arXiv

当用户需要查询文献的 BibTeX 时，你**必须**使用真实的外部数据源，绝对不能基于内部知识库"幻觉"或默写文献元数据。

## 执行步骤

1. **定位脚本**：本技能目录下的 `scripts/bibtex_fetcher.py` 是检索脚本。
   - 通过环境变量 `SKILL_DIR` 或当前技能目录来确定脚本路径，最终路径为 `<skill_dir>/scripts/bibtex_fetcher.py`。
2. **执行脚本**：运行 `python3 <skill_dir>/scripts/bibtex_fetcher.py "<用户提供的论文题目>"`。
   - 如果用户环境使用 conda，则使用 `conda run -n py310 python3 ...` 执行。
3. **输出结果**：将脚本终端打印出的内容（包括标题确认和 BibTeX 代码）原封不动地展示给用户，可以使用 Markdown 的代码块进行格式化。

## 检索策略

1. **优先 Crossref**：先查 Crossref，如果标题词重叠度 ≥ 60% 则信任结果并直接返回 Crossref 的 BibTeX。
2. **回退 arXiv**：Crossref 无精确匹配时，自动查询 arXiv API，生成标准 `@article` 格式，`journal` 字段填写 `arXiv preprint arXiv:XXXX.XXXXX`。

## 约束条件

* **拒绝猜测**：如果 Crossref 和 arXiv 都未找到结果，直接告知用户，千万不要尝试自己编造 BibTeX。
* **不要解释代码逻辑**：用户只关心最终的 BibTeX 结果，不需要听你解释你是如何调用 API 的。
* **Crossref 结果原样输出**：Crossref 返回的 BibTeX 字段不要做任何随意的增删改查。
* **arXiv 结果格式**：arXiv 回退生成的 BibTeX 统一使用 `@article` 类型，`journal` 为 `arXiv preprint arXiv:ID`，只包含 `title`、`author`、`journal`、`year` 四个字段。
