# paper-repro-pack

A [ZCode](https://zcode.ai) skill that turns a research paper into a **complete reproduction package**: every experiment the authors ran, extracted with everything strict reproduction needs — then the official code, model checkpoints and datasets located, verified, and audited — delivered as one bilingual Markdown report.

You hand it a paper (PDF path or arXiv link). You get back everything you would need to re-run its experiments — and an explicit list of everything the paper *fails* to specify.

## What it does

Given `some-paper.pdf` or `https://arxiv.org/abs/XXXX.XXXXX`, the skill runs six phases:

1. **Acquire** — downloads the PDF and the LaTeX e-print source for arXiv papers (hyperparameter tables are often only exact in the source) and extracts text.
2. **Inventory** — reads the full paper including the appendix and enumerates *every* experiment, ranked `CRITICAL` / `SECONDARY` / `SUPPLEMENTARY`.
3. **Extract** — per critical experiment: purpose, datasets + preprocessing, baselines (and which baseline implementations the authors used), metrics, full training hyperparameters, compute, evaluation protocol, transcribed result numbers, the authors' conclusion.
4. **Hunt & verify resources** — finds official code, checkpoints, and every dataset; fetches every link to confirm it works; then **deep-dives the official repo** (shallow clone): maps paper experiments to scripts/configs, checks environment files, licenses, and maintenance status.
5. **Gap analysis** — lists everything strict reproduction needs that the paper does not provide (seeds, hardware, prompt templates, …), each with a suggestion of where to recover it.
6. **Compose** — writes one self-checked Markdown report.

Every number carries an anchor (`[paper Table 2]`, `[repo configs/x.yaml]`, `[inferred]`) and every resource gets a status label: ✅ public / ⚠️ restricted / 🔗 third-party / ❌ not found.

## Report structure

| Section | Content |
|---|---|
| 0. 中文摘要 | Chinese executive summary (~300–500 字): what the paper does, headline results, resource availability, repro risks |
| 1. Experiment Inventory | every experiment, one row, ranked by criticality |
| 2. Critical Experiments | full detail cards with exact transcribed numbers + one-line Chinese takeaway |
| 3. Secondary & Supplementary | compact rows for ablations and appendix studies |
| 4. Reproduction Settings Summary | all hyperparameters (appendix tables transcribed in full), environment, compute budget, verbatim artifacts |
| 5. Resources & Availability | verified links + repo deep-dive findings |
| 6. Reproduction Gap Checklist | what's missing for strict reproduction, and where to try |

See [`examples/`](examples/) for real outputs:

- [`repro-report-2106.09685.md`](examples/repro-report-2106.09685.md) — **LoRA** (ICLR 2022): happy path with official code. Flags 6 paper-vs-repo hyperparameter mismatches and dead checkpoint links with working alternatives.
- [`repro-report-2302.13971.md`](examples/repro-report-2302.13971.md) — **LLaMA**: restricted weights, inference-only official code (found on the paper-era `llama_v1` branch), 19 eval datasets verified, Books3 flagged as taken down.
- [`repro-report-2001.08361.md`](examples/repro-report-2001.08361.md) — **Scaling Laws**: no official code exists; third-party reproduction audited instead, and a misleadingly-named fake WebText2 dataset unmasked.

## Install

Copy the repository folder into your ZCode skills directory:

```bash
git clone https://github.com/clarachen07/paper-repro-pack.git
mkdir -p ~/.agents/skills
cp -R paper-repro-pack ~/.agents/skills/
```

(ZCode also discovers skills under `~/.zcode/skills/` or per-project `.agents/skills/`.)

## Usage

Open a new ZCode session and send a paper with a reproduction intent:

```
Help me prepare to strictly reproduce this paper: https://arxiv.org/abs/2106.09685
```

```
把 repro-report-2302.13971 里那种复现报告给我做一份 — paper.pdf 在 ./downloads/
```

The report lands at `./repro-report-<paper-id>.md`; intermediate artifacts (downloaded PDF, LaTeX source, cloned repo) go to `./repro-<paper-id>/`.

## Requirements

- `pdftotext` (poppler) or the Python `pypdf` package — for text extraction (arXiv papers also yield LaTeX source, which the skill prefers for tables)
- `git` — for the official-repo deep dive
- Network access — for arXiv downloads, resource search, and link verification

## Notes & limitations

- The skill **prepares** the reproduction package; it does not run experiments or download datasets/models themselves.
- Link verification is point-in-time — the report records the date every link was checked.
- No values are ever invented: anything the paper doesn't state ends up in the gap checklist, not in a guess.

## License

[MIT](LICENSE)
