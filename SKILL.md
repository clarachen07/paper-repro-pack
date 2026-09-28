---
name: paper-repro-pack
description: Build a complete paper reproduction package — extract every experiment the authors ran with all details strict reproduction needs (data, setup, hyperparameters, results, conclusions), rank the critical ones, then locate and verify official code, model checkpoints and datasets, including a deep dive into the official repository. Use whenever the user sends a paper (PDF path or arXiv link) and mentions experiments, reproduction, 复现, replication, ablations, experimental setup, code/dataset/model availability, or wants everything needed to re-run a paper — even if they just hand over a paper and say "prepare this for me".
---

# Paper Reproduction Package

Produce everything a reader needs to strictly reproduce a paper's experiments, delivered as ONE bilingual Markdown report (Chinese executive summary + English body). Complete, but not bloated: critical experiments get full detail cards; secondary ones get compact rows.

## Input handling

| User provides | Do |
|---|---|
| Local PDF path | Create work dir, copy the PDF in, extract text |
| arXiv ID or URL (`2106.09685`, `arxiv.org/abs/...`, `arxiv.org/pdf/...`) | Run `python3 <skill-dir>/scripts/fetch_arxiv.py <id-or-url>` |

`<skill-dir>` is this skill's directory. The script downloads the PDF **and** the LaTeX e-print source (hyperparameter tables are often only exact in the source) and extracts text into the work dir. If text extraction fails, read the PDF directly with the session's PDF reading support, in page-range chunks.

Work dir: `./repro-<paper-id>/` — paper-id is the arXiv ID, or the PDF filename without extension. Final deliverable: `./repro-report-<paper-id>.md` in the current directory. Everything else in the work dir is scaffolding; the report is the product.

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
4. Section 0 (中文摘要) exists and is in Chinese; each critical card ends with a Chinese 要点.
5. Nothing in the report contradicts the paper; uncertainties are flagged, not papered over.

## Non-negotiables

- **Never invent.** Every value comes from the paper or the official repo, with an anchor (`§4.2`, `Table 3`, `configs/sst2.yaml`). Mark provenance inline: `[paper]`, `[repo]`, `[inferred]`.
- **Missing ≠ omit.** Information the paper doesn't give goes to the gap checklist, not into a guess.
- **Verify, then claim.** A resource counts as available only after you fetched its link during this run.
- **Bilingual as specified.** Section 0 in Chinese; body in English; one-line Chinese takeaway per critical card. Do not duplicate the whole body in Chinese.
- **Complete but not bloated.** Distill, don't restate. A results table with 40 rows: transcribe the rows that carry the claim and cite the table for the rest. A hyperparameter table: transcribe in FULL — selective HP transcription is how reproductions silently break (see `references/extraction.md`).
