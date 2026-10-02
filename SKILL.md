---
name: paper-repro-report
description: 把一篇论文整理成一份中文为主的完整复现报告（paper reproduction report）：提取作者做过的每一个实验以及严格复现所需的全部细节——数据、实验设置、超参数、结果、结论——并按关键程度排序；再找到并逐一核实官方代码、模型 checkpoint 和数据集，深入审查官方仓库。用户发来论文（paper，PDF 路径或 arXiv 链接）并提到实验、复现、复现报告、reproduce、replication、reproduction、ablation、实验设置、代码/数据集/模型是否公开，或想重跑一篇论文的所有实验时使用——哪怕只是丢来一篇论文说"帮我准备复现"。
license: MIT. See LICENSE
metadata:
  author: clarachen07
  version: "1.2.0"
---

# Paper Reproduction Report

Produce everything a reader needs to strictly reproduce a paper's experiments, delivered as ONE Markdown report written in Chinese — proper nouns, transcribed numbers, and code paths stay in their original form. Complete, but not bloated: critical experiments get full detail cards; secondary ones get compact rows.

## Input handling

| User provides | Do |
|---|---|
| Local PDF path | Create work dir, copy the PDF in, extract text |
| arXiv ID or URL (`2106.09685`, `arxiv.org/abs/...`, `arxiv.org/pdf/...`) | Run `python3 <skill-dir>/scripts/fetch_arxiv.py <id-or-url>` |

`<skill-dir>` is this skill's directory. The script downloads the PDF **and** the LaTeX e-print source (hyperparameter tables are often only exact in the source) and extracts text into the work dir. If text extraction fails, read the PDF directly in page-range chunks — most agents read PDF pages natively; if yours cannot, work from whatever text and LaTeX source you have and note the limitation in the report.

Work dir: `./repro-<paper-id>/` — paper-id is the arXiv ID, or the PDF filename without extension. Final deliverable: `./repro-report-<paper-id>.md` in the current directory. Everything else in the work dir is scaffolding; the report is the product.

## Environment & fallbacks

Agents differ in built-in tools. Use the best available and degrade gracefully — never skip a phase silently:

- **Web access — required.** arXiv downloads, resource hunting, and link verification all need the network. Prefer built-in web-search / web-fetch tools when present (they let you judge page CONTENT, not just status codes); without them, use `curl` (`-sSL` for page content, `-sIL` for status and redirects). A status check alone can't tell a real page from a soft-404 or a login wall.
- **PDF reading — optional.** If the environment reads PDFs natively, use it when text extraction fails. If not, rely on `paper.txt` and the LaTeX under `source/` — `fetch_arxiv.py` already falls back from `pdftotext` to `pypdf` on its own.
- **Shell, Python 3, git — required.** Run the fetch script (stdlib only, no pip installs), unpack arXiv sources, and shallow-clone official repos.

## Workflow

### Phase 1 — Acquire
Get PDF + extracted text (+ LaTeX source when arXiv). Skim the text to identify the paper: title, task domain, venue, and its overall shape (where experiments, implementation details, and appendix live).

### Phase 2 — Inventory
Follow `references/extraction.md` (criticality rules, schema, and search checklist) from here on. Read the FULL paper — main text AND appendix. Enumerate **every** experiment the authors ran: main comparisons, ablations, component analyses, sensitivity studies, human evaluations, case studies, efficiency measurements, appendix extras. One row each: short name, type, criticality, anchor (§ / Table / Figure). Ranking rule: an experiment is **CRITICAL** if the abstract's or intro's headline claims rest on it (usually the main results tables); **SECONDARY** for ablations and analyses; **SUPPLEMENTARY** for appendix-only extras.

### Phase 3 — Extract
For every CRITICAL experiment, fill the full per-experiment schema from `references/extraction.md`: purpose, datasets + preprocessing, baselines (and which implementation of each baseline the authors used), metrics, method config, full training hyperparameters, compute, evaluation protocol, transcribed result numbers, the authors' conclusion. SECONDARY/SUPPLEMENTARY get compact rows — but any hyperparameter that appears ONLY inside an appendix experiment still goes into the global settings summary (report §4).

### Phase 4 — Hunt & verify resources
Follow `references/resource-hunting.md`. Find official code, pretrained models/checkpoints, and every dataset the experiments use. Verify each link this run. Then deep-dive the official repo: shallow clone, map paper experiments to scripts/configs, check environment files, license, and maintenance status. Label each resource: ✅ public / ⚠️ restricted / 🔗 third-party / ❌ not found.

### Phase 5 — Gap analysis
List everything strict reproduction needs that the paper does NOT provide — e.g. random seeds, hardware, a preprocessing detail, an exact prompt template, baseline tuning protocol. Each gap gets a suggestion of where it might be recovered (appendix, official repo, baseline's repo, author contact). "Not specified" is a finding — never silently omit it.

### Phase 6 — Compose & self-check
Write `./repro-report-<paper-id>.md` following `references/report-template.md`. Then self-check:
1. Every inventory row is covered in the report body.
2. Every reported number and setting carries an anchor.
3. Every reported link was fetched this run.
4. The whole report is in Chinese (terms/numbers in original form); §0 is one dense 300–500 字 paragraph; every critical card ends with a one-line 要点.
5. Nothing in the report contradicts the paper; uncertainties are flagged, not papered over.

## Non-negotiables

- **Never invent.** Every value comes from the paper or the official repo, with an anchor (`§4.2`, `Table 3`, `configs/sst2.yaml`). Mark provenance inline: `[paper]`, `[repo]`, `[inferred]`.
- **Missing ≠ omit.** Information the paper doesn't give goes to the gap checklist, not into a guess.
- **Verify, then claim.** A resource counts as available only after you fetched its link during this run.
- **Chinese-first as specified.** Write the whole report in Chinese; keep proper nouns, dataset/metric names, hyperparameters, transcribed numbers, and code/config paths in their original form (attach the English term in parentheses on first occurrence when helpful). Each critical card ends with a one-line 要点.
- **Complete but not bloated.** Distill, don't restate. A results table with 40 rows: transcribe the rows that carry the claim and cite the table for the rest. A hyperparameter table: transcribe in FULL — selective HP transcription is how reproductions silently break (see `references/extraction.md`).
