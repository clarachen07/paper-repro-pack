中文 · [English](./README.en.md)

# 📦 paper-repro-report

#### 把一篇论文变成一份开箱即用的中文复现报告：每个实验、全部细节、官方资源逐一核验、缺口清单一目了然

[![License](https://img.shields.io/badge/License-MIT-3B82F6?style=for-the-badge)](./LICENSE)
[![Agent Skills](https://img.shields.io/badge/标准-Agent%20Skills-8B5CF6?style=for-the-badge)](https://agentskills.io)
[![兼容](https://img.shields.io/badge/兼容-40%2B%20Agents-10B981?style=for-the-badge)](https://agentskills.io)

一个遵循 [Agent Skills](https://agentskills.io) 开放标准的通用 Skill：丢给它一篇论文（PDF 路径或 arXiv 链接），它还给你一份中文为主的 Markdown 复现报告——重跑这篇论文所需要的一切，以及一份明明白白的清单，列出论文**没告诉你**的一切（专有名词、转录数字、代码路径保留原文）。

## 它做什么

Skill 按六个阶段跑完一篇论文：

1. **获取** — 下载 PDF 和 LaTeX 源码（超参数表往往只有源码里是精确的），并抽取全文文本。
2. **盘点** — 通读全文包括附录，枚举作者做过的**每一个**实验（主对比、消融、敏感性分析、案例研究……），按 `CRITICAL` / `SECONDARY` / `SUPPLEMENTARY` 排序。
3. **提取** — 每个关键实验一张完整卡片：目的、数据集与预处理、基线（作者用的是哪个实现）、指标、完整训练超参数、算力、评测协议、逐字转录的结果数字、作者结论。
4. **资源猎取与核验** — 找到官方代码、checkpoint 和每个数据集，逐条链接当场验证；再**深入审查官方仓库**（浅克隆）：把论文实验映射到脚本/配置、检查环境文件、许可证和维护状态。
5. **缺口分析** — 列出严格复现需要、但论文没给的一切（随机种子、硬件、prompt 模板……），每条附补救建议。
6. **成稿** — 自检后产出一份 Markdown 报告。

每个数字都带出处锚点（`[paper Table 2]`、`[repo configs/x.yaml]`、`[inferred]`），每个资源都带状态标签：✅ 公开 / ⚠️ 受限 / 🔗 第三方 / ❌ 未找到。报告全文以中文撰写，专有名词与转录数字保留原文。

## 报告结构

| 章节 | 内容 |
|---|---|
| 0. 中文摘要 | 中文执行摘要（约 300–500 字）：论文做了什么、核心结果、资源可得性、复现风险 |
| 1. Experiment Inventory | 每个实验一行，按关键程度排序 |
| 2. Critical Experiments | 关键实验完整卡片，含逐字转录数字 + 一行要点 |
| 3. Secondary & Supplementary | 消融与附录研究的紧凑行 |
| 4. Reproduction Settings Summary | 全部超参数（附录表完整转录）、环境、算力预算、原始产物 |
| 5. Resources & Availability | 核验过的链接 + 仓库深查结论 |
| 6. Reproduction Gap Checklist | 严格复现还缺什么、去哪里找 |

## 怎么触发

装好后不用记任何命令，自然语言直接说，中英文都行：

```
帮我严格复现这篇论文：https://arxiv.org/abs/2106.09685
```

```
把这篇 paper 的复现报告做一份，PDF 在 ./downloads/paper.pdf
```

```
这篇论文的代码和 checkpoint 都公开吗？实验设置写得够全吗？
```

```
Prepare this paper for strict reproduction: arxiv.org/abs/2302.13971
```

报告落在 `./repro-report-<paper-id>.md`；中间产物（下载的 PDF、LaTeX 源码、克隆的仓库）在 `./repro-<paper-id>/`。

## 安装

### 方式一：让 Agent 自己装（推荐）

在支持 Agent Skills 的 agent（Claude Code、Codex、Cursor、Gemini CLI、ZCode 等 40+）里直接说：

```
帮我安装这个 skill：https://github.com/clarachen07/paper-repro-report
```

Agent 会自己把仓库克隆到它对应的 skills 目录（`~/.claude/skills/`、`~/.codex/skills/`、`~/.agents/skills/`……），不用你操心路径。

### 方式二：SKILL.md 直接投喂（兜底）

你的 agent 不支持 Skills？把整个仓库 clone 下来，把 [SKILL.md](SKILL.md) 当作任务说明交给它，并告诉它仓库所在路径——SKILL.md 里引用的 `scripts/` 和 `references/` 就在仓库里，效果一样。

### 方式三：skills CLI（进阶）

```bash
npx skills add clarachen07/paper-repro-report
```

一行装到本机检测到的所有 agent。

## 示例输出

[`examples/`](examples/) 里有三份真实产出：

- [`repro-report-2106.09685.md`](examples/repro-report-2106.09685.md) — **LoRA**（ICLR 2022）：官方代码齐全的顺利案例。揪出 6 处论文与仓库的超参数不一致，以及失效 checkpoint 链接的可用替代。
- [`repro-report-2302.13971.md`](examples/repro-report-2302.13971.md) — **LLaMA**：权重受限、官方代码只有推理部分（在论文时代的 `llama_v1` 分支上找到）、19 个评测数据集逐一核验、Books3 标记为已下架。
- [`repro-report-2001.08361.md`](examples/repro-report-2001.08361.md) — **Scaling Laws**：官方代码不存在，改为审计第三方复现，并拆穿一个名字迷惑性极强的假 WebText2 数据集。

## 环境要求

- `pdftotext`（poppler）或 Python 的 `pypdf` 包 — 用于文本抽取（arXiv 论文还会拿到 LaTeX 源码，Skill 优先用它读表格）
- `git` — 用于官方仓库深查
- 网络访问 — arXiv 下载、资源搜索、链接核验

## 说明与局限

- Skill **准备**复现报告，不替你跑实验，也不下载 数据集/模型 本体。
- 链接核验是时点性的——报告记录每个链接的核验日期。
- 从不编造数值：论文没说的一律进缺口清单，绝不瞎猜。

## License

[MIT](LICENSE)
