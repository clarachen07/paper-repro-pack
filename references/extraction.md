# Per-experiment extraction guide

## Criticality ranking

- **CRITICAL** — the experiments the headline QUANTITATIVE claims rest on: the main results tables and the comparisons whose numbers the abstract quotes. The test "would an abstract claim collapse without this table?" outranks any general impression — a paper whose intro lists seven headline findings (e.g. an empirical scaling study) does not thereby make all seven critical; ask which tables/equations actually carry the quoted numbers.
- **Methodology/analysis papers**: the constitutive experiments — the fits, sweeps, or measurements that later claims are computed from — are CRITICAL even without a results table of their own; their constants go in full into the settings summary.
- **SECONDARY** — ablations, component analyses, hyperparameter sensitivity, efficiency/runtime studies in the main text.
- **SUPPLEMENTARY** — appendix-only experiments: extra datasets, per-task breakdowns, additional baselines, case studies, human-eval details.

Scope beats thoroughness: a compact CRITICAL set with full detail beats a sprawling one. When torn between two levels for a *specific* experiment, pick the higher one.

## Full schema (CRITICAL experiments)

```text
E<n>: <short name>                  e.g. "E1: GLUE fine-tuning (Table 2)"
Criticality: CRITICAL               Anchor: §4.1, Table 2
Purpose:        the question this experiment answers — one sentence
Datasets:       names + versions + splits used + preprocessing steps (anchor each)
Baselines:      compared methods AND which implementation of each the authors
                used (official repo? own reimplementation? how tuned?)
Metrics:        exact metric names; computation if non-obvious
Config:         model/method settings specific to this experiment (rank, adapters,
                prompt template, decoding params — whatever applies)
Training:       optimizer, LR + schedule + warmup, batch size, epochs/steps,
                weight decay, dropout, max length, seeds, early stopping
Compute:        GPU type + count, training time, parameter counts
Eval protocol:  checkpoint selection rule, averaging, statistical tests
Results:        rows that carry the claim — ours / strongest baseline / delta —
                transcribed exactly, each with its table anchor
Conclusion:     what the authors claim this experiment shows
要点:           one-line Chinese takeaway for the reader
```

Provenance lives in the inline `[paper]` / `[repo]` / `[inferred]` markers — no separate per-card field. Add a `Repro note` line only when the card carries an implementation caveat worth surfacing (missing code path, paper-vs-repo mismatch).

SECONDARY / SUPPLEMENTARY experiments collapse to: name, anchor, purpose (one line), key setting deltas from the critical config, headline numbers, conclusion.

## Where each piece hides (search checklist)

- Implementation details usually sit in a dedicated subsection (often §4 or Appendix A) but are ALSO scattered: LR in a table caption, batch size in a footnote, hardware in the acknowledgements. Sweep the whole paper.
- **Appendix hyperparameter tables are often the only complete spec** — transcribe them fully into the report's settings summary, not selectively.
- Which baseline implementation was used ("we use the officially released X", "our reimplementation", "as tuned by Y") is repro-critical and easy to miss — it's usually one sentence in the setup.
- Prompt templates / system messages (LLM papers) are often appendix-only — copy them verbatim into the settings summary.
- arXiv LaTeX source: `grep -n "begin{table}" *.tex` finds exact table values; hyperparameter tables survive plain-text extraction poorly, prefer the `.tex`. Searching for `learning_rate`, `batch_size`, `epochs` in the source often surfaces a config block.
- Cited papers may hold protocol details ("we follow the evaluation setup of X") — note the dependency in the gap checklist if the borrowed detail matters and isn't restated.

## Results transcription rules

- Copy numbers EXACTLY as printed — no rounding, no ± cleanup, keep the printed precision.
- Two different table types, two different rules:
  - **Results tables** (method comparisons): transcribe the rows that carry the headline claim; cite the table for the rest.
  - **Hyperparameter tables**: transcribe in FULL into the settings summary — they are the only complete spec, and selective HP transcription is how reproductions silently break.
- If a number appears differently in the text vs the table, report both occurrences and flag the discrepancy explicitly.

## Non-ML papers

Adapt, don't force: each study is an experiment; "config" = apparatus/materials/protocol; datasets = subjects/samples; seeds = randomization procedure. The goal is unchanged — a stranger could re-run the study from the report alone.
