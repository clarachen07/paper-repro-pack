# Resource hunting & verification playbook

Goal: for strict reproduction the reader needs (1) official code, (2) pretrained models/checkpoints, (3) every dataset used — located, verified, and status-labeled **today**.

## Search order (official first)

1. **URLs printed in the paper** — abstract footnote, intro, conclusion, "additional materials" appendix, figure/table captions, corresponding-author footnote. Highest-precision source; start here.
2. **GitHub search** — paper title in quotes, method acronym, model name; disambiguate by author or affiliation. Check the authors' and lab's GitHub orgs.
3. **Papers with Code** — search by title; returns code + dataset links. The site may be slow or down; if unreachable, say so and move on.
4. **Hugging Face** — search Models and Datasets for the method name and for each dataset name; check the authors'/org's HF page for checkpoints.
5. **Author pages** — personal/lab homepages, the venue page. OpenReview pages often carry a supplementary zip that IS the code.
6. **Last resort** — unofficial reimplementations. Label 🔗 third-party; list the best-maintained one only; never present as official.

## Verify every link this run

Fetch each URL you intend to report — prefer the agent's built-in web-fetch capability so you can judge the page CONTENT, not just a status code; without one, `curl -sL` the page and confirm it isn't a soft-404 or a login wall (a bare `curl -sIL` status check can't tell). A repo that 404s, an empty HF org, a removed dataset page — those are ❌ (or 🔗 if a third-party mirror exists). Record the verification date in the report.

## Deep repo dive (code found — official first)

Shallow-clone into the work dir defined in SKILL.md: `git clone --depth 1 <url> ./repro-<paper-id>/official-code` — if git is unavailable or the clone fails, browse via the GitHub API (`api.github.com/repos/<owner>/<repo>/contents/` + raw README; unauthenticated budget ≈ 60 req/h).

**Check branches, not just HEAD.** If the default HEAD doesn't match the paper (README references a different paper, or the content is clearly from a later version of the project), look for paper-era branches, tags, or releases and identify which ref corresponds to this paper. Note the ref you analyzed.

Then answer, each item with file-path evidence:

- Does the README reference this exact paper (title or arXiv ID)?
- Are there reproduction instructions — exact commands, and for which experiment/table?
- Map at least every CRITICAL experiment to its script/config (e.g. "E1 ↔ `scripts/run_glue.sh` + `configs/roberta-base.json`"). If a critical experiment has no corresponding code path, say "not found" explicitly.
- Environment spec present (`requirements.txt` / `environment.yml` / `pyproject.toml`)? Python and CUDA versions?
- Are checkpoints included or linked? What sizes?
- Dangling references: README links that 404, "coming soon", empty dirs?
- License — code AND weights separately; they often differ. Last commit date. Open issues mentioning reproducibility problems?
- If the repo is a stub or placeholder — say so explicitly and downgrade the status.

Do not run any code from the repo. Do not clone full histories.

When no official code exists, apply the same deep-dive — compactly and clearly labeled 🔗 — to the most promising third-party repo: it tells the reader how much of the reproduction is already done for them. If even that doesn't exist, the deep-dive section of the report says so and the gap checklist carries the consequence.

## Status labels

- `✅ public` — fetched and verified accessible this run
- `⚠️ restricted` — gated: request form, license acceptance, institutional access, email-the-authors
- `🔗 third-party` — unofficial reimplementation or mirror (usable, not authoritative)
- `❌ not found` — full playbook searched, nothing available

## Datasets & models

- Datasets: official site or HF dataset page; note registration gates, license terms, and whether the exact splits/version the paper used are public.
- Models: HF model page or official download link; note size and license. Weight licenses are frequently more restrictive than the code license — flag when so.
- A dataset the paper created itself is also a resource: check whether the authors released it, and where.
- Baselines' artifacts can matter too: if reproduction requires a specific baseline checkpoint the paper used, list it in the same table.
