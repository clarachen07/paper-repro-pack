[中文](./README.md) · English

# 📦 paper-repro-report

#### Turn a paper into a Chinese-first, ready-to-reproduce report: every experiment, every detail, verified official resources, and an explicit gap list — in one Markdown file

[![License](https://img.shields.io/badge/License-MIT-3B82F6?style=for-the-badge)](./LICENSE)
[![Agent Skills](https://img.shields.io/badge/Standard-Agent%20Skills-8B5CF6?style=for-the-badge)](https://agentskills.io)
[![Compatible](https://img.shields.io/badge/Compatible-40%2B%20Agents-10B981?style=for-the-badge)](https://agentskills.io)

An open [Agent Skill](https://agentskills.io): hand it a paper (PDF path or arXiv link) and it gives back a Chinese-first Markdown reproduction report containing everything you would need to re-run the paper's experiments — plus an explicit list of everything the paper *fails* to tell you (proper nouns, transcribed numbers, and code paths stay in their original form).

## What it does

The skill runs six phases on a paper:

1. **Acquire** — downloads the PDF and the LaTeX e-print source (hyperparameter tables are often only exact in the source) and extracts text.
2. **Inventory** — reads the full paper including the appendix and enumerates *every* experiment the authors ran (main comparisons, ablations, sensitivity studies, case studies…), ranked `CRITICAL` / `SECONDARY` / `SUPPLEMENTARY`.
3. **Extract** — one full detail card per critical experiment: purpose, datasets + preprocessing, baselines (and which implementation the authors used), metrics, full training hyperparameters, compute, evaluation protocol, transcribed result numbers, the authors' conclusion.
4. **Hunt & verify resources** — finds official code, checkpoints, and every dataset; fetches every link to confirm it works; then **deep-dives the official repo** (shallow clone): maps paper experiments to scripts/configs, checks environment files, licenses, and maintenance status.
5. **Gap analysis** — lists everything strict reproduction needs that the paper does not provide (seeds, hardware, prompt templates…), each with a suggestion of where to recover it.
6. **Compose** — writes one self-checked Markdown report.

Every number carries an anchor (`[paper Table 2]`, `[repo configs/x.yaml]`, `[inferred]`) and every resource gets a status label: ✅ public / ⚠️ restricted / 🔗 third-party / ❌ not found. The whole report is written in Chinese; proper nouns and transcribed numbers stay in their original form.

## Report structure

| Section | Content |
|---|---|
| 0. 中文摘要 | Chinese executive summary (~300–500 字): what the paper does, headline results, resource availability, repro risks |
| 1. Experiment Inventory | every experiment, one row, ranked by criticality |
| 2. Critical Experiments | full detail cards with exact transcribed numbers + one-line 要点 takeaway |
| 3. Secondary & Supplementary | compact rows for ablations and appendix studies |
| 4. Reproduction Settings Summary | all hyperparameters (appendix tables transcribed in full), environment, compute budget, verbatim artifacts |
| 5. Resources & Availability | verified links + repo deep-dive findings |
| 6. Reproduction Gap Checklist | what's missing for strict reproduction, and where to try |

## How to trigger it

Once installed, no commands to memorize — just say it naturally, in either language:

```
Help me prepare to strictly reproduce this paper: https://arxiv.org/abs/2106.09685
```

```
List every experiment in this paper and everything I'd need to re-run it — ./downloads/paper.pdf
```

```
Is the official code and these checkpoints public? Is the experimental setup complete?
```

```
帮我严格复现这篇论文：https://arxiv.org/abs/2106.09685
```

The report lands at `./repro-report-<paper-id>.md`; intermediate artifacts (downloaded PDF, LaTeX source, cloned repo) go to `./repro-<paper-id>/`.

## Install

### Option 1: Let your agent install it (recommended)

In any Agent-Skills-capable agent (Claude Code, Codex, Cursor, Gemini CLI, ZCode, and 40+ more), just say:

```
Install this skill for me: https://github.com/clarachen07/paper-repro-report
```

The agent clones the repo into its own skills directory (`~/.claude/skills/`, `~/.codex/skills/`, `~/.agents/skills/`…) — no paths to memorize.

### Option 2: Feed it SKILL.md directly (fallback)

Your agent doesn't support Skills? Clone the repo and hand it [SKILL.md](SKILL.md) as the task brief, telling it where the repo lives — the `scripts/` and `references/` files SKILL.md references are right there in the repo. Same effect.

### Option 3: skills CLI (advanced)

```bash
npx skills add clarachen07/paper-repro-report
```

One line, installed to every agent detected on your machine.

## Example outputs

[`examples/`](examples/) contains three real runs:

- [`repro-report-2106.09685.md`](examples/repro-report-2106.09685.md) — **LoRA** (ICLR 2022): the happy path with official code. Flags 6 paper-vs-repo hyperparameter mismatches and dead checkpoint links with working alternatives.
- [`repro-report-2302.13971.md`](examples/repro-report-2302.13971.md) — **LLaMA**: restricted weights, inference-only official code (found on the paper-era `llama_v1` branch), 19 eval datasets verified, Books3 flagged as taken down.
- [`repro-report-2001.08361.md`](examples/repro-report-2001.08361.md) — **Scaling Laws**: no official code exists; a third-party reproduction is audited instead, and a misleadingly-named fake WebText2 dataset is unmasked.

## Requirements

- `pdftotext` (poppler) or the Python `pypdf` package — for text extraction (arXiv papers also yield LaTeX source, which the skill prefers for tables)
- `git` — for the official-repo deep dive
- Network access — for arXiv downloads, resource search, and link verification

## Notes & limitations

- The skill **prepares** the reproduction report; it does not run experiments or download datasets/models themselves.
- Link verification is point-in-time — the report records the date every link was checked.
- No values are ever invented: anything the paper doesn't state ends up in the gap checklist, not in a guess.

## License

[MIT](LICENSE)
