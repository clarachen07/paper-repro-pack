# Reproduction Package — LLaMA: Open and Efficient Foundation Language Models

| | |
|---|---|
| Paper | LLaMA: Open and Efficient Foundation Language Models [paper] |
| Authors | Hugo Touvron et al. (13 authors) — Meta AI [paper] |
| Venue | preprint (arXiv, Feb 2023; no venue stated in paper — LaTeX source uses the ACL 2023 template [inferred from source/]) |
| arXiv | [2302.13971](https://arxiv.org/abs/2302.13971) (v1) |
| Official code | [facebookresearch/llama](https://github.com/facebookresearch/llama) (paper-era code on `llama_v1` branch) — ✅ public, **inference only** |
| Report date | 2026-09-27 — all links in §5 verified on this date |

## 0. 中文摘要

论文提出 LLaMA 系列基础语言模型（7B/13B/33B/65B），仅用公开数据（约 1.4T token 的七源混合语料）预训练，核心主张：不依赖专有数据也能达到 SOTA——LLaMA-13B 在多数基准上超过 GPT-3 175B，LLaMA-65B 与 Chinchilla-70B、PaLM-540B 相当。关键实验为六个主结果表：零样本常识推理（Table 3）、闭卷问答 NQ/TriviaQA（Table 4/5）、RACE 阅读理解（Table 6）、数学推理 MATH/GSM8k（Table 7）、代码生成 HumanEval/MBPP（Table 8）、5-shot MMLU（Table 9）；另有指令微调 LLaMA-I、偏见/毒性/真实性评估（Tables 10–14）与碳足迹核算（Table 15）。资源可用性：官方仓库仅开源推理代码（无训练与评测代码），权重需通过 Meta 表单审批（非商业许可）；社区镜像 huggyllama 提供全量权重；全部 19 个评测数据集公开可下载；预训练语料需按论文流程自行重建，其中 Books3 已因版权问题下架，仅有第三方镜像。主要复现风险：①官方无预训练/评测代码，管道需第三方重建（如 RedPajama-Data、OpenLLaMA）；②未给随机种子、AdamW ε、dropout、微批切分，上下文长度 2048 与词表 32k 只能从官方代码推断；③需 2048×A100-80GB 量级算力；④基线数字全部引自原论文，且 TriviaQA 用的 filtered dev 划分与 GPT-3/PaLM 的 unfiltered test 不可直接对比。

## 1. Experiment Inventory 实验总览

| # | Experiment | Type | Criticality | Anchor |
|---|---|---|---|---|
| E1 | Zero-shot common sense reasoning, 8 benchmarks (LLaMA vs GPT-3/Gopher/Chinchilla/PaLM) | main comparison | CRITICAL | §3.1, Table 3 |
| E2 | Closed-book QA — NaturalQuestions, 0/1/5/64-shot | main comparison | CRITICAL | §3.2, Table 4 |
| E3 | Closed-book QA — TriviaQA, 0/1/5/64-shot | main comparison | CRITICAL | §3.2, Table 5 |
| E4 | Reading comprehension — RACE middle/high, zero-shot | main comparison | CRITICAL | §3.3, Table 6 |
| E5 | Mathematical reasoning — MATH + GSM8k, ±maj1@k | main comparison | CRITICAL | §3.4, Table 7 |
| E6 | Code generation — HumanEval (0-shot) + MBPP (3-shot), pass@k | main comparison | CRITICAL | §3.5, Table 8 |
| E7 | MMLU, 5-shot | main comparison | CRITICAL | §3.6, Table 9 |
| E8 | Instruction finetuning (LLaMA-I) — MMLU | component study | SECONDARY | §4, Table 10 |
| E9 | Training loss curves (4 model sizes) | analysis | SECONDARY | §2.4/§3.7, Figure 1 |
| E10 | Benchmark performance evolution during training | analysis | SECONDARY | §3.7, Figure 2 |
| E11 | Toxicity — RealToxicityPrompts | analysis | SECONDARY | §5.1, Table 11 |
| E12 | Bias — CrowS-Pairs | analysis | SECONDARY | §5.2, Table 12 |
| E13 | Gender bias — WinoGender co-reference | analysis | SECONDARY | §5.3, Table 13 |
| E14 | Truthfulness — TruthfulQA | analysis | SECONDARY | §5.4, Table 14 |
| E15 | Carbon footprint accounting | efficiency measurement | SECONDARY | §6, Table 15 |
| S1 | MMLU per-subject breakdown (57 subjects) | per-task breakdown | SUPPLEMENTARY | App. B, Table 16 |
| S2 | QA eval protocol + prompt formats (NQ/TriviaQA) | eval protocol detail | SUPPLEMENTARY | App. A, Figure 3 |
| S3 | Free-form generations from LLaMA-65B | case study | SUPPLEMENTARY | App. C |
| S4 | Free-form generations from LLaMA-I | case study | SUPPLEMENTARY | App. D |

## 2. Critical Experiments 关键实验

### E1 — Zero-shot common sense reasoning (§3.1, Table 3)
**Purpose** — show LLaMA-65B beats Chinchilla-70B (all benchmarks but BoolQ) and PaLM-540B (all but BoolQ/WinoGrande), and LLaMA-13B beats GPT-3 175B. [paper §3.1]
**Datasets** — BoolQ, PIQA, SIQA, HellaSwag, WinoGrande, ARC-easy, ARC-challenge, OpenBookQA; zero-shot; no task-specific preprocessing described. [paper §3.1]
**Baselines** — GPT-3 175B, Gopher 280B, Chinchilla 70B, PaLM 62B/62B-cont/540B; **all numbers taken from the corresponding papers, none re-run**. [paper §3.1]
**Metrics** — accuracy via multiple-choice likelihood; completion chosen by likelihood normalized by number of characters (following Gao et al. 2021 / lm-eval-harness), except BoolQ and OpenBookQA: `P(completion|context)/P(completion|"Answer:")`. [paper §3]
**Config & training** — zero-shot, no task config; model/optimizer settings in §4 global table. [paper Table 2]
**Compute** — pretraining: 2048×A100-80GB; 65B trains 1.4T tokens in ≈21 days at ~380 tok/s/GPU. [paper §2.4]
**Results** — accuracy, claim-carrying rows:
| Model | BoolQ | PIQA | SIQA | HellaSwag | WinoGrande | ARC-e | ARC-c | OBQA |
|---|---|---|---|---|---|---|---|---|
| GPT-3 175B | 60.5 | 81.0 | – | 78.9 | 70.2 | 68.8 | 51.4 | 57.6 |
| Chinchilla 70B | 83.7 | 81.8 | 51.3 | 80.8 | 74.9 | – | – | – |
| PaLM 540B | 88.0 | 82.3 | – | 83.4 | 81.1 | 76.6 | 53.0 | 53.4 |
| LLaMA-13B | 78.1 | 80.1 | 50.4 | 79.2 | 73.0 | 74.8 | 52.7 | 56.4 |
| LLaMA-65B | 85.3 | 82.8 | 52.3 | 84.2 | 77.0 | 78.9 | 56.0 | 60.2 |
*(Full table incl. Gopher, PaLM 62B/cont and 7B/33B rows: paper Table 3 — cited, not restated.)* Δ(65B−Chinchilla): BoolQ +1.6, PIQA +1.0, SIQA +1.0, HellaSwag +3.4, WinoGrande +2.1.
**Authors' conclusion** — LLaMA-65B outperforms Chinchilla-70B on all reported benchmarks but BoolQ and PaLM-540B everywhere but BoolQ/WinoGrande; 13B outperforms GPT-3 on most benchmarks despite 10× fewer parameters. [paper §3.1]
**要点** — 零样本常识推理上 65B 几乎全面超越 Chinchilla-70B 与 PaLM-540B，13B 以十分之一参数量超过 GPT-3。

### E2 — NaturalQuestions, closed-book QA (§3.2, Table 4)
**Purpose** — 65B achieves SOTA at 0-shot and few-shot; 13B competitive with GPT-3/Chinchilla at 5–10× smaller size. [paper §3.2]
**Datasets** — NaturalQuestions; **test split of the open-domain QA set, 3610 questions**. [paper App. A]
**Baselines** — GPT-3 175B, Gopher 280B, Chinchilla 70B, PaLM 8B/62B/540B (numbers from their papers). [paper §3.2]
**Metrics** — exact match after normalization: lowercase, remove articles/punctuation/duplicate whitespace; match against any gold alias. [paper App. A]
**Config & training** — greedy decoding; answer = generation up to first line break, final dot or comma; prompt prefixed with `Answer these questions:\n` (1-shot format in App. A Figure 3). [paper App. A]
**Compute** — see §4. **Eval protocol** — no checkpoint-selection rule stated (gap §6).
**Results** — EM, 0/1/5/64-shot:
| Model | 0-shot | 1-shot | 5-shot | 64-shot |
|---|---|---|---|---|
| GPT-3 175B | 14.6 | 23.0 | – | 29.9 |
| Chinchilla 70B | 16.6 | – | 31.5 | 35.5 |
| PaLM 540B | 21.2 | 29.3 | – | 39.6 |
| LLaMA-13B | 20.1 | 23.4 | 28.1 | 31.9 |
| LLaMA-65B | 23.8 | 31.0 | 35.0 | 39.9 |
**Authors' conclusion** — LLaMA-65B achieves SOTA in zero-shot and few-shot on NQ among compared models; 13B competitive despite 5–10× fewer params, runs on a single V100 at inference. [paper §3.2]
**要点** — NQ 闭卷问答 65B 零样本与 64-shot 均最优，13B 小 5–10 倍仍与 GPT-3/Chinchilla 相当。

### E3 — TriviaQA, closed-book QA (§3.2, Table 5)
**Purpose** — same claim as E2 on a second QA benchmark. [paper §3.2]
**Datasets** — TriviaQA **filtered dev set** — deliberately different from GPT-3/PaLM, which use the **unfiltered test set** whose online eval server is no longer available (paper footnote 5, codalab link). ⚠️ Split mismatch ⇒ not directly comparable to the GPT-3/PaLM columns. [paper §3.2 + App. A + fn.5]
**Baselines** — Gopher 280B, Chinchilla 70B (from their papers). [paper Table 5]
**Metrics / protocol** — EM, greedy decode, normalization and prompt prefix identical to E2. [paper App. A]
**Results** — EM, 0/1/5/64-shot: Gopher 43.5/–/57.0/57.2; Chinchilla 55.4/–/64.1/64.6; LLaMA-65B **68.2/71.6/72.6/73.0**.
**Authors' conclusion** — LLaMA-65B achieves SOTA in zero-shot and few-shot closed-book QA on TriviaQA. [paper §3.2]
**要点** — TriviaQA 上 65B 领先 Chinchilla 4 分以上，但 filtered dev 划分与基线的 unfiltered test 不可直接对比。

### E4 — Reading comprehension, RACE (§3.3, Table 6)
**Purpose** — reading comprehension exam data; 65B competitive with PaLM-540B. [paper §3.3]
**Datasets** — RACE middle + RACE high, zero-shot. [paper §3.3]
**Baselines** — GPT-3 175B, PaLM 8B/62B/540B (from their papers). **Protocol** — "we follow the evaluation setup from Brown et al. (2020)" — details not restated (gap §6). [paper §3.3]
**Metrics** — accuracy (zero-shot).
**Results** — RACE-middle / RACE-high: GPT-3 58.4/45.5; PaLM-540B 68.1/49.1; LLaMA-65B **67.9/51.6**; LLaMA-13B 61.6/47.2 (vs GPT-3 +3.2/+1.7).
**Authors' conclusion** — LLaMA-65B competitive with PaLM-540B; 13B outperforms GPT-3 by a few percent. [paper §3.3]
**要点** — RACE 零样本上 65B 与 PaLM-540B 相当（67.9/51.6 vs 68.1/49.1）。

### E5 — Mathematical reasoning, MATH + GSM8k (§3.4, Table 7)
**Purpose** — quantitative reasoning without math finetuning; beat Minerva-62B on GSM8k. [paper §3.4]
**Datasets** — MATH (12K problems, LaTeX), GSM8k (middle-school problems). [paper §3.4]
**Baselines** — PaLM 8B/62B/540B, Minerva 8B/62B/540B; **numbers taken from Lewkowycz et al. (2022)**. [paper §3.4]
**Metrics** — accuracy, with and without maj1@k majority voting: **k=256 for MATH, k=100 for GSM8k** (Minerva-540B used k=64/40 — different k, flagged). [paper Table 7 caption]
**Config** — sampling temperature for maj1@k not stated; "same setup as Minerva" (gap §6). [paper Table 7 caption]
**Results** —
| Model | MATH | MATH+maj1@k | GSM8k | GSM8k+maj1@k |
|---|---|---|---|---|
| Minerva 62B | 27.6 | 43.4 | 52.4 | 68.5 |
| Minerva 540B | 33.6 | 50.3 | 68.5 | 78.5 |
| LLaMA-65B | 10.6 | 20.5 | 50.9 | **69.7** |
Caveat [inferred]: raw GSM8k Minerva-62B 52.4 > LLaMA-65B 50.9; the "outperforms" claim holds only under maj1@k (69.7 vs 68.5) and with a larger k for LLaMA.
**Authors' conclusion** — LLaMA-65B outperforms Minerva-62B on GSM8k although it has not been finetuned on mathematical data. [paper §3.4]
**要点** — 无数学微调的 65B 在 GSM8k+maj1@k 上超过 Minerva-62B（69.7 vs 68.5），但注意 k 不同（100 vs 40）且原始 pass 上仍略低。

### E6 — Code generation, HumanEval + MBPP (§3.5, Table 8)
**Purpose** — code synthesis from natural language; LLaMA ≥ models with similar code-token counts. [paper §3.5]
**Datasets** — HumanEval (zero-shot, function signature + docstring), MBPP (3-shot, prompts "similar to Austin et al. (2021)"). [paper §3.5]
**Baselines** — LaMDA 137B, PaLM 8B/62B/62B-cont/540B (not finetuned on code); values marked ∗ read from figures in Chowdhery et al. (2022). [paper §3.5 + Table 8 caption]
**Metrics** — pass@1 (temperature 0.1), pass@100 HumanEval / pass@80 MBPP (temperature 0.8); unbiased pass@k estimator of Chen et al. (2021). [paper §3.5]
**Results** — HumanEval @1/@100, MBPP @1/@80: LaMDA-137B 14.0/47.3, 14.8/62.4; PaLM-62B 15.9/46.3∗, 21.4/63.2∗; LLaMA-65B **23.7/79.3, 37.7/76.8**; LLaMA-13B 15.8/52.5, 22.0/64.0.
**Authors' conclusion** — at similar parameter counts LLaMA outperforms LaMDA/PaLM (not code-tuned); ≥13B outperforms LaMDA-137B on both benchmarks. [paper §3.5]
**要点** — HumanEval pass@1 65B 达 23.7、MBPP 37.7，超过 PaLM-62B 与 LaMDA-137B。

### E7 — MMLU, 5-shot (§3.6, Table 9)
**Purpose** — knowledge benchmark; LLaMA-65B trails Chinchilla-70B/PaLM-540B, explained by limited books/academic data. [paper §3.6]
**Datasets** — MMLU, 5-shot "using the examples provided by the benchmark" (the standard dev-example set; exact list not restated — gap §6). [paper §3.6]
**Baselines** — GPT-NeoX 20B, GPT-3 175B, Gopher 280B, Chinchilla 70B, PaLM 8B/62B/540B (from their papers). [paper Table 9]
**Metrics** — 5-shot accuracy, Humanities/STEM/Social Sciences/Other/Average.
**Results** — average: GPT-3 175B 43.9; Gopher 280B 60.0; Chinchilla 70B **67.5**; PaLM 540B 69.3; LLaMA-7B 35.1; 13B 46.9; 33B 57.8; **65B 63.4**. ⚠️ Chinchilla average is 67.5 in Table 9 but 67.6 in App. Table 16's "All" row — paper-internal discrepancy, report both. [paper Table 9 vs Table 16]
**Authors' conclusion** — 65B behind Chinchilla/PaLM by a few percent across most domains; explanation: only 177GB of books+ArXiv in the mix vs up to 2TB for Gopher/Chinchilla/PaLM. [paper §3.6]
**要点** — MMLU 65B（63.4）落后 Chinchilla/PaLM 数个百分点，作者归因于书籍与论文语料仅 177GB。

## 3. Secondary & Supplementary Experiments 消融与补充实验

| # | Experiment | Anchor | Purpose | Key setting | Headline result | Conclusion |
|---|---|---|---|---|---|---|
| E8 | Instruction finetuning → LLaMA-I | §4, Table 10 | small-scale SFT boosts MMLU | single run, "same protocol as Chung et al. (2022)" — no data/epochs/LR given (gap §6) | LLaMA-I 65B MMLU **68.9** vs base 63.4, Flan-PaLM-cont 66.1, OPT-IML-Max 30B 43.2 | simple SFT outperforms similar-size instruct models, still below GPT code-davinci-002 (77.4, from Iyer et al. 2022) |
| E9 | Training loss curves | §2.4/§3.7, Fig. 1 | loss vs tokens for 4 sizes | batch 4M tokens; 7B/13B → 1.0T, 33B/65B → 1.4T | 7B still improving after 1T tokens | smaller models trained longer beat Chinchilla's compute-optimal point at inference |
| E10 | Benchmark evolution during training | §3.7, Fig. 2 | QA/commonsense tracked over training | TriviaQA, HellaSwag, NQ, SIQA, WinoGrande, PIQA | most improve steadily and track perplexity | SIQA has high variance ("may indicate that this benchmark is not reliable"); WinoGrande correlates poorly with perplexity |
| E11 | RealToxicityPrompts | §5.1, Table 11 | toxicity of generations | greedy decode on 100k prompts; PerspectiveAPI score 0–1; "respectful" = prompts prefixed with the polite-instruction string (verbatim in §4) | 65B: 0.128 basic / 0.141 respectful (7B 0.106/0.081); "0.087 for Chinchilla" cited for context | toxicity rises with size, esp. respectful prompts; cross-paper comparison unreliable (third-party API pipeline) |
| E12 | CrowS-Pairs | §5.2, Table 12 | bias in 9 categories | zero-shot, model preference for stereotypical sentence via perplexity, LLaMA-65B vs GPT-3-175B vs OPT-175B | LLaMA avg **66.6** vs GPT-3 67.2, OPT 69.5; religion 79.0 (+10 vs OPT) | slightly less biased on average; religion/age/gender worst; expected to come from CommonCrawl |
| E13 | WinoGender | §5.3, Table 13 | gender bias in co-reference | perplexity-based co-reference over 3 pronoun sets + "gotcha" cases, 4 model sizes | 65B: all 77.5; her/hers/she 78.8 vs his/him/he 72.1; gotcha errors ↑ | better on "their/them/someone" than gendered pronouns ⇒ occupational gender bias captured |
| E14 | TruthfulQA | §5.4, Table 14 | truthfulness vs hallucination | QA prompt style of Ouyang et al. (2022); answers scored by specially fine-tuned judge models via OpenAI API (gap §6) | 65B: truthful **0.57**, truthful∗informative **0.53** vs GPT-3-175B 0.28/0.25 | scores higher than GPT-3 in both, absolute rate still low ⇒ frequent hallucination |
| E15 | Carbon footprint | §6, Table 15 | energy/emissions accounting | `Wh = GPU-h × 400W × PUE(1.1)`; `tCO2eq = MWh × 0.385` (US avg); GPU-hours per model | 7B/13B/33B/65B: 82,432/135,168/530,432/1,022,362 GPU-h; 36/59/233/449 MWh; 14/23/90/173 tCO2eq | total dev ≈ 2048 A100 for ~5 months ≈ 2,638 MWh ≈ 1,015 tCO2eq |
| S1 | MMLU per-subject breakdown | App. B, Table 16 | 57-subject detail | adds GPT-3/Gopher/Chinchilla/LLaMA-I columns | LLaMA-I "All" 68.9 | per-domain view of E7/E8 (cited, not restated) |
| S2 | QA protocol + prompt formats | App. A, Fig. 3 | exact eval spec for E2/E3 | verbatim in §4 | — | protocol detail feeding E2/E3 |
| S3 | LLaMA-65B generations | App. C | qualitative capability demo | 6 hand-picked prompts | — | anecdotal, not a metric |
| S4 | LLaMA-I generations | App. D | qualitative SFT demo | 8 hand-picked prompts | — | anecdotal, not a metric |

## 4. Reproduction Settings Summary 复现设置汇总

- **Environment** — paper states nothing. Official repo `requirements.txt`: `torch, fairscale, fire, sentencepiece` — **unpinned, no CUDA version** [repo]. Inference example run via `torchrun`, model parallelism MP = 1/2/4/8 for 7B/13B/33B/65B [repo README]. [inferred] PyTorch-era (early 2023) stack.
- **Model hyperparameters — FULL transcription of Table 2** [paper Table 2] (the only complete architecture/optimization spec in the paper):

| params | dim | n heads | n layers | LR | batch (tokens) | train tokens |
|---|---|---|---|---|---|---|
| 6.7B | 4096 | 32 | 32 | 3.0e-4 | 4M | 1.0T |
| 13.0B | 5120 | 40 | 40 | 3.0e-4 | 4M | 1.0T |
| 32.5B | 6656 | 52 | 60 | 1.5e-4 | 4M | 1.4T |
| 65.2B | 8192 | 64 | 80 | 1.5e-4 | 4M | 1.4T |

- **Optimizer** — AdamW, β1=0.9, β2=0.95; cosine schedule to 10% of max LR; weight decay 0.1; gradient clipping 1.0; **2,000 warmup steps**. [paper §2.3] ε, decay scope, dropout: not specified (gap §6); ε=1e-5 and max_seq_len=2048, SwiGLU hidden rounded to multiple_of=256 from [repo `llama/model.py`].
- **Architecture deltas vs vanilla transformer** — pre-norm RMSNorm [GPT3]; SwiGLU with 2/3·4d hidden dim [PaLM]; rotary embeddings at every layer, no absolute positional embeddings [GPTNeo]. [paper §2.2]
- **Pre-training data — FULL transcription of Table 1** [paper Table 1]:

| Dataset | Sampling prop. | Epochs | Disk size |
|---|---|---|---|
| CommonCrawl | 67.0% | 1.10 | 3.3 TB |
| C4 | 15.0% | 1.06 | 783 GB |
| Github | 4.5% | 0.64 | 328 GB |
| Wikipedia | 4.5% | 2.45 | 83 GB |
| Books | 4.5% | 2.23 | 85 GB |
| ArXiv | 2.5% | 1.06 | 92 GB |
| StackExchange | 2.0% | 1.03 | 78 GB |

  ≈1.4T tokens total; 1T-token runs (7B/13B) use the same sampling proportions. [paper §2.1]
- **Per-source preprocessing** [paper §2.1] — CommonCrawl: 5 dumps 2017–2020, CCNet pipeline (line-level dedup, fastText LangID keep-English, n-gram LM quality filter, classifier keeping Wikipedia-reference-like pages); C4: dedup + LangID, heuristic quality filter (punctuation, word/sentence counts); Github: Google BigQuery public dataset, Apache/BSD/MIT licenses only, line-length/alphanumeric heuristics, boilerplate regex, **file-level exact dedup**; Wikipedia: June–Aug 2022 dumps, 20 languages (bg ca cs da de en es fr hr hu it nl pl pt ro ru sl sr sv uk), remove hyperlinks/comments/boilerplate; Books: Gutenberg + Books3 (ThePile), book-level dedup removing >90% overlap; ArXiv: strip everything before first section + bibliography, strip .tex comments, inline-expand user macros (following Lewkowycz et al. 2022); StackExchange: 28 largest sites, HTML stripped, answers sorted by score descending.
- **Tokenizer** — SentencePiece BPE; **all numbers split into individual digits**; byte fallback for unknown UTF-8. [paper §2.1] Vocab size not stated in paper; 32,000 [inferred from [repo] tokenizer/`n_words`, standard LLaMA-1 value].
- **Compute budget** — 2048×A100-80GB; 65B ≈380 tok/s/GPU ⇒ 1.4T tokens ≈21 days [paper §2.4]; per-model GPU-hours in E15 [paper Table 15]; ≈5 months wall-clock for all four models [paper §6].
- **Verbatim artifacts** —
  - QA prompt (NQ/TriviaQA, all shots) [paper App. A]: prepend the string `Answer these questions:\n`; 1-shot example: `Q: Who sang who wants to be a millionaire in high society?\nA: Frank Sinatra\nQ: ... \nA:` ; answer extraction: stop at first line break, final dot or comma; EM normalization: lowercase, remove articles/punctuation/duplicate whitespaces.
  - MC scoring rule [paper §3]: char-normalized likelihood (Gao et al. 2021) except OpenBookQA & BoolQ: `P(completion|context)/P(completion|"Answer:")` (Brown et al. 2020).
  - RealToxicityPrompts "respectful" prefix [paper Table 11 caption]: `Complete the following sentence in a polite, respectful, and unbiased manner:` — appended before each of the 100k prompts ("Basic" = without it). ⚠️ Caption prints "PerplexityAPI" while body text and fn.3 say PerspectiveAPI — paper typo, the score source is PerspectiveAPI. [paper §5.1 + Table 11 caption]
  - Carbon formulas [paper §6]: `Wh = GPU-h × (GPU power consumption) × PUE` (PUE 1.1, A100 TDP 400W); `tCO2eq = MWh × 0.385`.
  - Code gen decoding [paper §3.5]: pass@1 @ T=0.1; pass@100 (HumanEval) / pass@80 (MBPP) @ T=0.8; unbiased pass@k estimator from Chen et al. (2021).
  - maj1@k [paper Table 7 caption]: k=256 (MATH), k=100 (GSM8k); "same setup as Minerva".

## 5. Resources & Availability 资源可用性

| Resource | Type | Link | Status | Notes |
|---|---|---|---|---|
| Official code (`llama_v1` branch) | code | https://github.com/facebookresearch/llama | ✅ | inference-only; branch HEAD 57b0eb6, 2023-03-07; code license **GPL-3**; README cites arXiv 2302.13971 |
| Official weights (7B/13B/33B/65B) | checkpoint | https://www.llama.com/llama-downloads/ (form; README links https://forms.gle/jk851eBVbX1m5TAv5) | ⚠️ | gated: request form + license acceptance; signed URLs via email; weights under non-commercial bespoke license (MODEL_CARD.md) — stricter than code license |
| Community weight mirrors | checkpoint | https://huggingface.co/huggyllama/llama-7b (+ -13b, -30b, -65b) | 🔗 | unofficial mirrors, not gated, verified 200; not authoritative |
| Llama 2 on HF (successor, not this paper) | checkpoint | https://huggingface.co/meta-llama/Llama-2-7b-hf | ⚠️ | gated:manual — different model, listed only to avoid confusion |
| xformers (attention impl, fn.2) | code | https://github.com/facebookresearch/xformers | ✅ | paper's efficient-attention dependency |
| CCNet pipeline (CC preprocessing) | code | https://github.com/facebookresearch/cc_net | ✅ | referenced pipeline for CommonCrawl |
| lm-evaluation-harness (MC protocol) | code | https://github.com/EleutherAI/lm-evaluation-harness | ✅ | the Gao et al. 2021 protocol E1 depends on |
| metaseq OPT chronicles (fn.4) | data/log | https://github.com/facebookresearch/metaseq/tree/main/projects/OPT/chronicles | ✅ | source of OPT training-log figures used in §6 |
| PerspectiveAPI (fn.3) | service | https://perspectiveapi.com/ | ✅/⚠️ | site up; scoring needs API key; third-party pipeline |
| CodaLab TriviaQA eval (fn.5) | service | https://competitions.codalab.org/competitions/17208 | ✅/⚠️ | page live but legacy v1.5 platform; paper already states server unavailable for unfiltered test |
| CommonCrawl | dataset | https://commoncrawl.org/ | ✅ | dumps 2017–2020; specific dump IDs not enumerated (gap §6) |
| C4 | dataset | https://huggingface.co/datasets/allenai/c4 | ✅ | not gated |
| GitHub code corpus | dataset | BigQuery public dataset (https://cloud.google.com/blog/topics/public-datasets/github-on-bigquery-analyze-all-the-open-source-code) | ✅ | `bigquery-public-data:github_repos`; license-filtered extract must be rebuilt |
| Wikipedia (20 langs, Jun–Aug 2022) | dataset | https://dumps.wikimedia.org/ ; https://huggingface.co/datasets/wikimedia/wikipedia | ✅ | snapshot selection must match paper window |
| Gutenberg | dataset | https://www.gutenberg.org/ | ✅ | public domain |
| Books3 | dataset | https://huggingface.co/datasets/defunct-datasets/the_pile_books3 | 🔗 | original Books3 removed (copyright takedowns); third-party mirror only |
| ArXiv corpus | dataset | https://www.kaggle.com/datasets/Cornell-University/arxiv | ✅ | LaTeX source + metadata |
| StackExchange dump | dataset | https://archive.org/details/stackexchange | ✅ | "28 largest websites" selection = paper-specific |
| Benchmarks (eval) | datasets | boolq `google/boolq`; piqa `ybisk/piqa`; SIQA `allenai/social_i_qa`; HellaSwag `Rowan/hellaswag`; WinoGrande `allenai/winogrande`; ARC `allenai/ai2_arc`; OBQA `allenai/openbookqa`; NQ `google-research-datasets/natural_questions`; TriviaQA `mandarjoshi/trivia_qa`; RACE `ehovy/race`; MATH `EleutherAI/hendrycks_math`; GSM8k `openai/gsm8k`; HumanEval `openai/openai_humaneval`; MBPP `google-research-datasets/mbpp`; MMLU `cais/mmlu`; RTP `allenai/real-toxicity-prompts`; CrowS-Pairs `nyu-mll/crows_pairs`; WinoGender `oskarvanderwal/winogender`; TruthfulQA `truthfulqa/truthful_qa` (all huggingface.co/datasets/…) | ✅ | all 19 verified 200 & not gated this run; exact split/version per §2/§4 |
| TruthfulQA GPT-judge models | checkpoint | https://github.com/sylinrl/TruthfulQA | ⚠️ | judge repo public; judges were fine-tuned OpenAI endpoints — availability depends on OpenAI API history (gap §6) |
| Papers with Code | index | https://paperswithcode.com/paper/llama-open-and-efficient-foundation-language | ⚠️ | PwC sunset; URL now serves a Hugging Face shell; use https://huggingface.co/papers/2302.13971 (✅) |
| Baselines: GPT-3 / Gopher / Chinchilla / PaLM / Minerva / LaMDA / Flan-PaLM | checkpoint | — | ❌ | closed; paper quotes numbers only — not needed for metric-level reproduction of E1–E7 tables |
| Baseline: OPT-175B | checkpoint | https://huggingface.co/facebook/opt-175b | ⚠️ | API returned 401 unauthenticated this run (gated/removed); smaller OPT models public; OPT-IML `facebook/opt-iml-30b` ✅ (E8 baseline) |
| Baselines: GPT-J-6B / GPT-NeoX-20B | checkpoint | https://huggingface.co/EleutherAI/gpt-j-6b ; https://huggingface.co/EleutherAI/gpt-neox-20b | ✅ | open baselines appear in Tables 8/9 |

**Repo deep-dive** — cloned `--depth 1 --branch llama_v1 https://github.com/facebookresearch/llama` → `repro-2302.13971/official-code/` (HEAD `57b0eb6`, 2023-03-07). README explicitly references the paper and arXiv 2302.13971 [repo `README.md`]. Structure: `llama/model.py` (Transformer, RMSNorm eps 1e-5, RoPE, SwiGLU, `max_seq_len: int = 2048`), `llama/generation.py`, `llama/tokenizer.py`, `example.py`, `download.sh`, `requirements.txt`, `MODEL_CARD.md` (weights: non-commercial bespoke license; trained Dec 2022–Feb 2023), `LICENSE` (code: GPL-3). **Experiment ↔ code mapping: none of E1–E15 has an official code path — the repo ships inference only; no training loop, no data pipeline, no evaluation harness → "not found" for every critical experiment.** Environment spec present but unpinned; no Python/CUDA versions. Checkpoints are linked via presigned URLs (not included); `download.sh` expects `MODEL_SIZE="7B,13B,30B,65B"` — note the repo's "30B" naming vs the paper's 33B/32.5B. Dangling references: the README's Google-form link redirects and Meta's downloads page now fronts Llama 2/3/4 (LLaMA-1 approvals no longer visibly offered); main-branch README references Llama 2, paper-era content survives only in the `llama_v1` branch; repo deprecated in favor of newer Meta repos, `llama_v1` frozen since 2023-03-07; issue tracker (475 open) not searchable unauthenticated this run. Nothing was executed from the repo; no full history cloned.

## 6. Reproduction Gap Checklist 复现信息缺口

| Missing | Why it matters | Where to try |
|---|---|---|
| Random seeds / run variance (no error bars anywhere) | exact-number reproduction impossible; claims rest on single runs | paper gives none; ask authors / check repo issues |
| Training code & data-pipeline code | E1–E15 have no official implementation | third-party: RedPajama-Data (data recreation, ✅ verified), OpenLLaMA (training pipeline, ✅ verified) |
| Max context length | changes attention memory, packing, data epoch math | [repo] `llama/model.py`: `max_seq_len: int = 2048` |
| Vocab size | tokenizer/ embedding shape | [repo] tokenizer → 32,000 [inferred]; weights ship `tokenizer.model` |
| AdamW ε, weight-decay scope (norms/biases?), dropout | optimizer-behavior fidelity | [repo] `model.py` `norm_eps=1e-5` covers RMSNorm only; no dropout arg (⇒0 [inferred]); ε for AdamW not stated |
| How the 4M-token global batch is split (micro-batch, seq len, packing, DP/MP/SP degree) | reproducing throughput & loss curve | paper §2.4 names model+sequence parallelism (Korthikanti et al. 2022) without config; not in repo |
| Checkpoint selection rule / early stopping | which checkpoint was evaluated | not stated; assume final checkpoint [inferred] |
| Exact CommonCrawl dump IDs (5 dumps, 2017–2020) & Wikipedia snapshot IDs | bit-level data identity | CCNet repo + commoncrawl.org index; crawl-window guesswork remains |
| TriviaQA split mismatch (filtered dev vs GPT-3/PaLM unfiltered test) | baselines not strictly comparable | paper App. A admits it; fn.5 codalab server legacy |
| maj1@k sampling temperature; k=100 vs Minerva's k=40 | E5 comparison not apples-to-apples | "same setup as Minerva" → Lewkowycz et al. (2022) appendix |
| E8 finetuning details (instruction data mix, epochs, LR, seq len) | LLaMA-I 68.9 not reproducible from this paper | protocol = Chung et al. (2022) Flan; see that paper/repo |
| TruthfulQA judge models (fine-tuned via OpenAI API) | E14 needs the exact judges | sylinrl/TruthfulQA repo; OpenAI endpoint availability |
| MMLU "examples provided by the benchmark" — exact 5-shot dev set | prompt-content sensitivity | Hendrycks et al. (2020) official repo / HF `cais/mmlu` dev split |
| Baseline tuning protocol | all baseline numbers quoted, none re-run | corresponding papers only |
| PerspectiveAPI sampling window/version | E11 cross-paper comparability | paper itself flags methodology drift |
| Paper-internal inconsistencies: Table 11 caption "PerplexityAPI" vs body "PerspectiveAPI"; Chinchilla MMLU 67.5 (Table 9) vs 67.6 (Table 16); repo "30B" vs paper 33B (32.5B params) | bookkeeping hygiene | flagged here; use PerspectiveAPI, report both MMLU values |

---
*Generated by paper-repro-pack on 2026-09-27. Links verified 2026-09-27. Provenance markers: [paper] = stated in the paper · [repo] = found in the official repo · [inferred] = our inference, flagged.*
