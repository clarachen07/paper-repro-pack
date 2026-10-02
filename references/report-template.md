# Report template

Deliverable: `./repro-report-<paper-id>.md` — ONE file. paper-id = arXiv ID (e.g. `2106.09685`) or the sanitized PDF filename.

## Language rules

- **全文中文**：整份报告用中文撰写——正文、标题、字段标签一律中文。以下内容保留原文，不强行翻译：专有名词（模型/方法/数据集名）、指标名、超参数、逐字转录的数字、代码与配置路径、论文原文引文；术语首次出现时可在括号里附英文。
- **Section 0 (中文摘要)**: one dense paragraph of roughly 300–500 字. Must cover: what the paper does, the headline result, the critical experiments, resource availability in one breath, and the top reproduction risks (what's missing, where things may bite).
- Every CRITICAL experiment card ends with `要点:` — one line distilling what this experiment means for reproduction.

## Skeleton

````markdown
# 复现报告 — <Paper Title>

| | |
|---|---|
| 论文 | <title> [paper] |
| 作者 | <第一作者 et al. — 机构> |
| 发表 | <会议/期刊 + 年份，或 "preprint"> |
| arXiv | <id, link> |
| 官方代码 | <link + 状态标签> |
| 报告日期 | <YYYY-MM-DD> — 所有链接于此日核验 |

## 0. 中文摘要
<300–500 字：论文做什么；关键实验与核心结果；官方代码/模型/数据集可用性；复现风险点>

## 1. 实验总览
| # | 实验 | 类型 | 关键度 | 锚点 |
|---|---|---|---|---|
| E1 | GLUE 微调对比 | main comparison | CRITICAL | §4.1, Table 2 |
| E2 | Adapter 形态消融 | ablation | SECONDARY | §4.3, Table 4 |

## 2. 关键实验

### E1 — <short name> (<anchor>)
**目的** — <一句话> [paper §x]
**数据集** — <名称、版本、split、预处理> [paper §y]
**基线** — <对比方法；作者各用的是哪个实现>
**指标** — <精确指标名>
**配置与训练** — <方法配置 + 优化器/LR/schedule/batch/epochs/seeds；
                  超过 4 项就用紧凑表格>
**算力** — <GPU 型号/数量、训练时长、参数量> [paper §z / footnote]
**结果** —
| 方法 | <metric> | Δ |
|---|---|---|
| <ours> | <精确数字> | — |
| <最强基线> | <精确数字> | <delta> |
*(完整表见论文 Table N — 引用，不复写。)*
**作者结论** — <作者认为这说明了什么>
**要点** — <一行要点>

### E2 — ...

## 3. 消融与补充实验
| # | 实验 | 锚点 | 目的 | 关键设置 | 核心结果 | 结论 |
|---|---|---|---|---|---|---|
<每个实验一行紧凑记录>

## 4. 复现设置汇总
- **环境** — <python/CUDA/版本（如论文有述）>
- **全局超参数** — <各实验一致的列合并成一张总表；
  模型族之间确有差异时按模型族分列紧凑小表；
  含仅出现在附录的超参数表>
- **算力预算** — <论文有述时的总算力>
- **逐字转录产物** — <prompt 模板、公式、预处理规则——
  逐字节复制，因为复现需要它们一字不差>

## 5. 资源可用性
| 资源 | 类型 | 链接 | 状态 | 备注 |
|---|---|---|---|---|
| 官方代码 | code | <url> | ✅ | MIT; last commit 2024-08 |
| <数据集 A> | dataset | <url> | ✅ | 无需注册 |
| <模型 X> | checkpoint | <url> | ⚠️ | gated: 需接受许可协议 |

**仓库深查** — <结构概要；关键实验 ↔ 脚本映射；环境规格发现；
失效引用；代码是否真的实现了论文的实验>

## 6. 复现信息缺口
| 缺失信息 | 为什么重要 | 去哪里找 |
|---|---|---|
| random seeds | 无法精确复现数值 | repo issues / 联系作者 |
| <...> | <...> | <appendix / repo / baseline repo / contact> |

---
*本报告由 paper-repro-report 于 <date> 生成；链接核验于 <date>。出处标记：
[paper] = 论文原文 · [repo] = 官方仓库 · [inferred] = 推断，已标注。*
````

## Self-check before delivering

1. Inventory ↔ body: every row in §1 appears in §2 or §3.
2. Every number/setting has an anchor and a provenance marker where non-obvious.
3. Every link in §5 was fetched during this run; date is recorded.
4. 全文中文（专有名词、数字、路径保留原文）；§0 为 300–500 字稠密摘要；每个关键卡片有「要点」。
5. Gap checklist has an entry for every "not specified" you encountered — if it's empty, you likely missed something; re-check seeds, hardware, preprocessing, and baseline tuning.
6. Length discipline: a typical report lands between 150 and 400 lines. If longer, compress §3 and §4 first.

## Filled mini-example (excerpt, LoRA paper)

```markdown
### E1 — LoRA vs full fine-tuning on GLUE (§5.2, Table 2)
**目的** — 证明 LoRA 用远少于全量微调的可训练参数达到同等效果。 [paper]
**数据集** — GLUE benchmark (MNLI, SST-2, ...), standard splits [paper §5.1]
**基线** — 全量微调、adapters (Houlsby et al.) 官方发布版、BitFit [paper]
**配置与训练** — RoBERTa-base/large; r ∈ {1,4,8}, α scaled; AdamW ...
**结果** —
| 方法 | MNLI acc | SST-2 acc |
|---|---|---|
| LoRA (r=8, RoB_base) | 87.5±.3 | 95.1±.2 |
| Fine-tune | 87.6 | 94.8 |
**要点** — LoRA 在 GLUE 上与全量微调基本持平，可训练参数少约 1000 倍。
```
