# Reproduction Package — LoRA: Low-Rank Adaptation of Large Language Models

| | |
|---|---|
| Paper | LoRA: Low-Rank Adaptation of Large Language Models [paper] |
| Authors | Edward J. Hu*, Yelong Shen*, Phillip Wallis, Zeyuan Allen-Zhu, Yuanzhi Li, Shean Wang, Lu Wang, Weizhu Chen — Microsoft Corporation [paper] |
| Venue | ICLR 2022 (LaTeX source: `iclr2022_conference.tex`) [paper source] |
| arXiv | [2106.09685v2](https://arxiv.org/abs/2106.09685) |
| Official code | https://github.com/microsoft/LoRA ✅ public (MIT) |
| Report date | 2026-09-27 — all links below verified on this date |

## 0. 中文摘要

论文提出 LoRA:冻结预训练权重,仅在 Transformer 注意力权重(主要为 Wq、Wv)旁注入低秩分解矩阵 BA,按 α/r 缩放,推理时可合并回权重、无额外延迟。核心结果:在 GLUE(RoBERTa/DeBERTa XXL)、E2E NLG(GPT-2)与 GPT-3 175B(WikiSQL/MNLI-m/SAMSum)上,LoRA 以 0.3M–4.7M 参数持平或超过全量微调,GPT-3 上参数减少约一万倍、显存降至 1/3。关键实验:Table 2(GLUE)、Table 3(E2E)、Table 4(GPT-3)、Table 1(adapter 延迟)。资源:官方代码 microsoft/LoRA(MIT)公开,含 GLUE/GPT-2 复现脚本与有效 checkpoint(部分 README 链接已 404);数据集基本公开,SAMSum 已转为受限。最大风险:GPT-3 模型与实验代码未公开,Table 4 及第 7 节分析无法外部复现;仓库脚本与论文超参多处不一致;随机种子仅部分给出;loralib 的 A 初始化与论文"高斯"表述不符。

## 1. Experiment Inventory 实验总览

| # | Experiment | Type | Criticality | Anchor |
|---|---|---|---|---|
| E1 | Adapter inference latency measurement | measurement | CRITICAL | §3 Table 1; App B Fig 5 |
| E2 | GLUE adaptation: RoBERTa base/large + DeBERTa XXL | main comparison | CRITICAL | §5.2–5.3, Table 2 |
| E3 | GPT-2 M/L on E2E NLG Challenge | main comparison | CRITICAL | §5.4, Table 3 |
| E4 | GPT-3 175B: WikiSQL / MNLI-m / SAMSum | main comparison | CRITICAL | §5.5, Table 4 |
| E5 | GPT-3 performance vs #trainable params (scalability) | analysis | SECONDARY | §5.5 Fig 2; App F.2 Table 15 |
| E6 | Which attention weights to adapt (Wq/Wk/Wv/Wo) | component analysis | SECONDARY | §7.1 Table 5 |
| E7 | Optimal LoRA rank r | sensitivity | SECONDARY | §7.2 Table 6 |
| E8 | Subspace similarity across r and seeds | analysis | SECONDARY | §7.2 Figs 3–4; App G; App H.1 Figs 6–7 |
| E9 | ∆W vs W correlation / amplification factor | analysis | SECONDARY | §7.3 Table 7; App H.3 Fig 8; App H.4 |
| S1 | GPT-3 few-shot vs fine-tuning | motivation | SUPPLEMENTARY | App A Table 8 |
| S2 | Full adapter latency sweep | measurement | SUPPLEMENTARY | App B Fig 5 |
| S3 | LoRA + PrefixEmbed / PrefixLayer combinations | combination | SUPPLEMENTARY | App E; rows of Table 15 |
| S4 | GPT-2 on DART and WebNLG | main-comparison extra | SUPPLEMENTARY | App F.1 Tables 13–14 |
| S5 | GPT-3 full hyperparameter grid | data behind Fig 2 | SUPPLEMENTARY | App F.2 Table 15 |
| S6 | Low-data regime MNLI-100/1k/10k/392K | appendix study | SUPPLEMENTARY | App F.3 Tables 16–17 |
| S7 | Effect of r on GPT-2 (E2E) | appendix sensitivity | SUPPLEMENTARY | App H.2 Table 18 |

## 2. Critical Experiments 关键实验

### E1 — Adapter inference latency (§3 Table 1; App B Fig 5)
**Purpose** — quantify the inference latency adapters add in online, small-batch scenarios, against which LoRA adds none by construction. [paper §3, §4.1]
**Setup** — single forward pass of GPT-2 medium; latency averaged over 100 trials on an NVIDIA Quadro RTX8000. [paper Table 1 caption]
**Config** — batch size {32, 16, 1}, sequence length {512, 256, 128}; adapter variants AdapterL (Lin et al. 2020 design) and AdapterH (Houlsby et al. 2019 design) with |Θ| = 0.5M (bs32) and 11M (bs16, bs1). [paper Table 1]
**Results** (ms, single forward pass) —
| Setting | Fine-Tune/LoRA | AdapterL | AdapterH |
|---|---|---|---|
| bs 32 / seq 512 (|Θ|=0.5M) | 1449.4±0.8 | 1482.0±1.0 (+2.2%) | 1492.2±1.0 (+3.0%) |
| bs 16 / seq 256 (|Θ|=11M) | 338.0±0.6 | 354.8±0.5 (+5.0%) | 366.3±0.5 (+8.4%) |
| bs 1 / seq 128 (|Θ|=11M) | 19.8±2.7 | 23.9±2.1 (+20.7%) | 25.8±2.2 (+30.3%) |
[paper Table 1]
**Authors' conclusion** — adapter latency is significant in online, short-sequence scenarios; LoRA introduces no additional inference latency (weights can be merged: W = W0 + BA). [paper §3, §4.1]
**Repro note** — no latency-measurement code in the official repo (searched this run) → must be reimplemented from the caption description. Full sweep in App B (Fig 5): slowdown up to >30% at batch 1, seq len 128. [repo search + paper App B]
**要点** — 适配器在小批量短序列在线推理时延迟增加可达 20–30%,而 LoRA 权重可合并、无额外推理延迟。

### E2 — GLUE adaptation with RoBERTa base/large + DeBERTa XXL (§5.2–5.3, Table 2)
**Purpose** — show LoRA matches or beats full fine-tuning on NLU with <1% of the trainable parameters. [paper §5.2–5.3]
**Datasets** — GLUE: MNLI, SST-2, MRPC, CoLA, QNLI, QQP, RTE, STS-B, standard splits. [paper §5.2, App C] Results are dev-set results [repo, `examples/NLU/README.md`: "We report below the dev set results, taking the medium over 5 runs"]. For MRPC/RTE/STS-B the model is initialized from the best MNLI checkpoint (following Liu et al. 2019), not from a MNLI-adapted model for the † runs. [paper §5.2, D.1]
**Baselines** — FT and BitFit and AdapterD rows marked * reuse published numbers from prior work (Liu et al. 2019; Zaken et al. 2021; Rücklé et al. 2020) [paper §5.1, Table 2 caption]; AdapterP/AdapterH † rows are the authors' own replications in the Houlsby et al. (2019) setup (seq len 128, fixed batch size across tasks) [paper §5.2, Table 2 caption].
**Metrics** — MNLI: overall (matched+mismatched) accuracy; CoLA: Matthew's correlation; STS-B: Pearson correlation; other tasks: accuracy. [paper Table 2 caption]
**Config** — LoRA applied to Wq and Wv only, r_q = r_v = 8; LoRA α = 8 (base) / 16 (large) / 8 (DeBERTa); trainable params 0.3M (base), 0.8M (large), 4.7M (DeBERTa XXL 1.5B). [paper Table 9–10, §5.1 formula |Θ| = 2·L̂·d_model·r]
**Training** — AdamW, linear LR decay, warmup ratio 0.06 (RoBERTa) / 0.1 (DeBERTa); per-task batch size / epochs / LR as transcribed in §4 below (Tables 9–10). Median over 5 random seeds; each run's result taken from the best epoch. [paper D.1–D.2]
**Compute** — NVIDIA Tesla V100 [paper §5]; NLU README: "run on 4 NVIDIA Tesla V100 GPU cards out of a DGX-1" [repo]; but per-task scripts export `num_gpus=8` [repo, `examples/NLU/roberta_base_mnli.sh`] — discrepancy, see §6.
**Results** (dev; full table = paper Table 2) —
| Method | #Params | MNLI | SST-2 | RTE | Avg. (8 tasks) |
|---|---|---|---|---|---|
| RoB_base (FT)* | 125.0M | 87.6 | 94.8 | 78.7 | 86.4 |
| RoB_base (LoRA) | 0.3M | 87.5±.3 | 95.1±.2 | 86.6±.7 | **87.2** |
| RoB_large (FT)* | 355.0M | 90.2 | 96.4 | 86.6 | 88.9 |
| RoB_large (LoRA) | 0.8M | 90.6±.2 | 96.2±.5 | 87.4±2.5 | **89.0** |
| RoB_large (AdptP)† (best adapter) | 3.0M | 90.2±.3 | 96.1±.3 | 83.8±2.9 | 88.4 |
| DeB_XXL (FT)* | 1500.0M | 91.8 | 97.2 | 93.9 | 91.1 |
| DeB_XXL (LoRA) | 4.7M | 91.9±.2 | 96.9±.2 | 94.9±.4 | **91.3** |
**Authors' conclusion** — LoRA matches or exceeds full fine-tuning at 0.3–4.7M trainable params and outperforms adapters under the restricted † setup. [paper §5.2–5.3]
**要点** — GLUE 上 LoRA 用不到 1% 的可训练参数即持平或超过全量微调,且优于同类适配器方法。

### E3 — GPT-2 medium/large on E2E NLG Challenge (§5.4, Table 3)
**Purpose** — test whether LoRA still prevails on NLG generation tasks, keeping the setup of Li & Liang (2021) for direct comparison. [paper §5.4]
**Datasets** — E2E NLG Challenge: ~42,000 train / 4,600 val / 4,600 test, restaurant domain; each input is a sequence of slot-value pairs, target is a reference text. [paper App C] (DART/WebNLG variants: S4.) The exact preprocessed data is bundled in the repo at `examples/NLG/data/e2e/`. [repo]
**Baselines** — FT, AdapterL, PreLayer, FTTop2 rows marked * are numbers published in prior work (Li & Liang 2021; Lin et al. 2020) [paper Table 3 caption, §5.1]; AdapterH (GPT-2 M) and AdapterL (GPT-2 L) rows are the authors' own runs. [paper Table 3]
**Metrics** — BLEU, NIST, METEOR, ROUGE-L, CIDEr (all higher-better); eval scripts shipped in `examples/NLG/eval/`. [paper Table 3; repo]
**Config** — LoRA r_q = r_v = 4, α = 32, dropout 0.1; beam search with beam 10, length penalty 0.9 (paper Table 11) — note the repo README command uses `--length_penalty 0.8` for E2E [repo, `examples/NLG/README.md`], discrepancy flagged in §6; no-repeat-ngram 4. [paper Table 11]
**Training** — AdamW (Loshchilov & Hutter 2017), linear LR schedule, 5 epochs, batch size 8, warmup 500 steps, LR 2e-4, weight decay 0.01, label smoothing 0.1. Baselines' hyperparameters as in Li & Liang (2021). Mean over 3 random seeds; each run's result taken from the best epoch. [paper D.3, Table 11]
**Compute** — V100 [paper §5]; repo commands run single-GPU (`--nproc_per_node=1`) in docker `nvcr.io/nvidia/pytorch:20.03-py3`. [repo, `examples/NLG/README.md`]
**Results** (test; full table = paper Table 3) —
| Method | #Params | BLEU | NIST | MET | ROUGE-L | CIDEr |
|---|---|---|---|---|---|---|
| GPT-2 M (FT)* | 354.92M | 68.2 | 8.62 | 46.2 | 71.0 | 2.47 |
| GPT-2 M (PreLayer)* | 0.35M | 69.7 | 8.81 | 46.1 | 71.4 | 2.49 |
| GPT-2 M (AdapterL)* | 11.09M | 68.9 | 8.71 | 46.1 | 71.3 | 2.47 |
| GPT-2 M (LoRA) | 0.35M | **70.4±.1** | **8.85±.02** | **46.8±.2** | **71.8±.1** | **2.53±.02** |
| GPT-2 L (FT)* | 774.03M | 68.5 | 8.78 | 46.0 | 69.9 | 2.45 |
| GPT-2 L (LoRA) | 0.77M | **70.4±.1** | **8.89±.02** | **46.8±.2** | **72.0±.2** | 2.47±.02 |
**Authors' conclusion** — LoRA outperforms all baselines with comparable or fewer trainable parameters on every metric. [paper §5.4]
**要点** — GPT-2 生成任务上 LoRA(0.35M 参数)在全部五个指标上超过全量微调与适配器/前缀基线。

### E4 — GPT-3 175B: WikiSQL / MNLI-m / SAMSum (§5.5, Table 4)
**Purpose** — final stress test: LoRA matches or exceeds full fine-tuning of GPT-3 175B on three datasets with ~0.003–0.02% of the parameters. [paper §5.5]
**Datasets** — WikiSQL (56,355/8,421 train/val; x = {table schema, query}, y = {SQL}; BSD 3-Clause) [paper App C]; MNLI (MultiNLI-matched) [paper App C]; SAMSum (14,732/819 train/test; x = utterances joined by "\n" followed by "\n\n", y = {summary}; CC BY-NC-ND 4.0) [paper App C].
**Baselines** — FT, BitFit, PreEmbed, PreLayer, AdapterH — all run by the authors on GPT-3 (internal implementation; no public GPT-3 code). [paper §5.5, Table 4]
**Metrics** — WikiSQL: logical-form validation accuracy; MNLI-m: validation accuracy; SAMSum: ROUGE-1/2/L. Reported fluctuation: WikiSQL ±0.5%, MNLI-m ±0.1%, SAMSum ±0.2/±0.2/±0.1. [paper Table 4 caption]
**Config** — two LoRA budgets: 4.7M (r_q = r_v = 1, or r_v = 2) and 37.7M (r_q = r_v = 8, or r_q = r_k = r_v = r_o = 2). PreEmbed: l_p = 256, l_i = 8 (3.2M); PreLayer: l_p = 8, l_i = 8 (20.2M). [paper D.4]
**Training** — AdamW, 2 epochs, batch size 128, weight decay 0.1, warmup 250,000 tokens, linear LR schedule; per-method LR: FT 5.00E-06, PreEmbed 5.00E-04, PreLayer 1.00E-04, BitFit 1.6E-03, AdapterH 1.00E-04, LoRA 2.00E-04; sequence length 384 (WikiSQL) / 768 (MNLI) / 2048 (SAMSum); best validation performance from each run. [paper D.4, Tables 12 + text]
**Compute** — NVIDIA V100s; VRAM 1.2TB → 350GB with LoRA; 25% training speedup (32.5 → 43.1 tokens/s per V100 at equal weight sharding). [paper §4.2, footnote 5] GPU count not stated → §6 gap.
**Results** (validation; full table = paper Table 4) —
| Method | #Params | WikiSQL Acc | MNLI-m Acc | SAMSum R1/R2/RL |
|---|---|---|---|---|
| GPT-3 (FT) | 175,255.8M | 73.8 | 89.5 | 52.0/28.0/44.5 |
| GPT-3 (BitFit) | 14.2M | 71.3 | 91.0 | 51.3/27.4/43.5 |
| GPT-3 (AdapterH) | 40.1M | 73.2 | 91.5 | 53.2/29.0/45.1 |
| GPT-3 (LoRA) | 4.7M | 73.4 | **91.7** | **53.8/29.8/45.9** |
| GPT-3 (LoRA) | 37.7M | **74.0** | 91.6 | 53.4/29.2/45.1 |
**Authors' conclusion** — LoRA matches or exceeds the fine-tuning baseline on all three datasets with ~10,000× fewer trainable parameters; not all methods benefit monotonically from more parameters (Fig 2). [paper §5.5]
**要点** — GPT-3 175B 上 LoRA 以 4.7M 参数在三个数据集上持平或超过全量微调,参数减少约一万倍;但 GPT-3 模型与代码未公开,外部无法复现。

## 3. Secondary & Supplementary Experiments 消融与补充实验

| # | Experiment | Anchor | Purpose | Key setting | Headline result | Conclusion |
|---|---|---|---|---|---|---|
| E5 | GPT-3 perf vs #params | §5.5 Fig 2; F.2 Table 15 | scalability of adaptation methods | full grid: PrefixEmbed l_p ∈ {32..512}, PrefixLayer l_p ∈ {2..64}, AdapterH r ∈ {1..64}, LoRA r ∈ {1..64} | PrefixEmbed drops 63.1→55.9 WikiSQL beyond l_p=256; LoRA stable 73.3–74.1 across 4.7M–603.8M | LoRA scales; prefix methods degrade non-monotonically [paper] |
| E6 | Which matrices to adapt | §7.1 Table 5 | best weight-type subset at fixed 18M budget on GPT-3 | r=8 single type vs r=4 two types vs r=2 four types, 96 layers | Wq alone 70.4 WikiSQL; Wq+Wv 73.7; all four 73.7; MNLI 91.0 / 91.3 / 91.7 | spread budget across Wq+Wv (or all 4) beats a single matrix at higher rank [paper] |
| E7 | Optimal rank r | §7.2 Table 6 | how small r suffices | r ∈ {1,2,4,8,64}; {Wq}, {Wq,Wv}, {Wq,Wk,Wv,Wo} | Wq+Wv: r=1 → 73.4 WikiSQL vs r=64 → 73.5; Wq alone: r=1 → 68.8, r=4 → 70.5 | r=1 nearly suffices for Wq+Wv; Wq alone needs larger r; ∆W has very low intrinsic rank [paper] |
| E8 | Subspace similarity | §7.2 Figs 3–4; App G; H.1 Figs 6–7 | do different r / seeds span the same subspace | φ(A_r=8, A_r=64, i, j) on GPT-3 layer 48 (plus 1/32/64/96 in H.1) | top singular direction of A_r=8 and A_r=64 share subspace of dim 1 with similarity >0.5; across two seeds (r=64) ∆Wq shares more directions than ∆Wv; random Gaussians share none | top directions are the useful ones — explains why r=1 works [paper] |
| E9 | ∆W vs W | §7.3 Table 7; H.3 Fig 8; H.4 | relation of ∆W to pretrained W | ‖U^T W_q V^T‖_F with U,V = top-r singular vectors of ∆W_q / W_q / random; GPT-3 layer 48 | ∆Wq 0.32 vs Wq-top-4 21.67 vs random 0.02; ‖∆W_q‖_F=6.91, ‖W_q‖_F=61.95 → amplification ≈ 21.5× at r=4, ≈2 at r=64 | ∆W amplifies task-specific directions NOT emphasized in W [paper] |
| S1 | Few-shot vs fine-tuning | App A Table 8 | motivation for adaptation | GPT-3; MNLI-m uses 2 demos/class (6 total), RTE few-shot from Brown et al. 2020 | MNLI-m 40.6 (few-shot) vs 89.5 (FT); RTE 69.0 vs 85.4 | fine-tuning beats few-shot by large margins [paper] |
| S2 | Full latency sweep | App B Fig 5 | extend Table 1 | batch 1–32 × seq 128/256/512 × adapter r ∈ {10,100,250}, Quadro RTX8000, 100 trials | slowdown up to >30% (AdapterH, batch 1, seq 128); colormap tweaked for visibility | latency worst in online small-batch regime [paper] |
| S3 | LoRA+PE / LoRA+PL | App E; Table 15 rows | combine LoRA with prefix tuning | LoRA+PE r_q=r_v ∈ {8,32,64} + l_p=8,l_i=4; LoRA+PL r_q=r_v=8 | LoRA+PE (r=64): WikiSQL 76.2 (best in paper); MNLI 91.3; LoRA+PL 52.8M: 72.9/90.2 | LoRA orthogonal to prefix-embedding on WikiSQL; LoRA+PL slightly worse than LoRA alone [paper] |
| S4 | GPT-2 DART + WebNLG | App F.1 Tables 13–14 | replicate Li & Liang setup on other NLG datasets | same as E3 config (Table 11) | DART GPT-2 M: LoRA BLEU 47.1±.2 vs FT 46.2; WebNLG (M, All): LoRA 55.3±.2 vs FT 46.5, Prefix 55.1 | LoRA ≥ prefix baselines at equal params [paper] |
| S5 | GPT-3 full grid | App F.2 Table 15 | data behind Fig 2 | 30+ rows over all method families | AdapterH r=64 (304.4M): 72.6 WikiSQL; LoRA r_q=r_v=64 (301.9M): 73.6 | LoRA's perf stabilizes with scale; adapters/prefix don't [paper] |
| S6 | Low-data MNLI-n | App F.3 Tables 16–17 | sample efficiency | MNLI subsampled to 100/1k/10k; full val set; batch 20/20/100, epochs 40/40/4 (Table 17) | MNLI-100: LoRA 63.8 vs FT 60.2, PrefixEmbed 37.6, PrefixLayer 48.3; MNLI-392K: LoRA 91.7 best | LoRA is favorable in low-data; prefix methods fail at 100 examples [paper] |
| S7 | Effect of r on GPT-2 | App H.2 Table 18 | repeat E7 on GPT-2 M | E2E; 26,000 training steps; r ∈ {1..1024} | val loss min 1.16 at r=16; BLEU max 70.38 at r=4; metrics flat for r ≥ 8 | optimal GPT-2 rank between 4 and 16; hyperparams were tuned at r=4 [paper] |

## 4. Reproduction Settings Summary 复现设置汇总

- **Environment** [repo] — NLU: Python 3.7.10, PyTorch 1.9.0+cu111 (`examples/NLU/environment.yml`), torch.distributed launch; NLG: torch 1.7.1+cu101, transformers 3.3.1 (`examples/NLG/requirement.txt`), docker `nvcr.io/nvidia/pytorch:20.03-py3`; loralib installable via `pip install loralib` (PyPI verified 200 this run). [paper] Hardware: NVIDIA Tesla V100 (all experiments §5), Quadro RTX8000 (latency only).
- **Global hyperparameters** — appendix tables are the only complete spec; transcribed in full (per-task columns in order MNLI, SST-2, MRPC, CoLA, QNLI, QQP, RTE, STS-B):

**Table 9 [paper D.1] — RoBERTa on GLUE** (optimizer AdamW, warmup ratio 0.06, linear schedule for all rows)

| Row | Batch | #Epochs | LR | LoRA cfg | α | Max seq len |
|---|---|---|---|---|---|---|
| RoB_base LoRA | 16/16/16/32/32/16/32/16 | 30/60/30/80/25/25/80/40 | 5E-4/5E-4/4E-4/4E-4/4E-4/5E-4/5E-4/4E-4 | r_q=r_v=8 | 8 | 512 |
| RoB_large LoRA | 4/4/4/4/4/4/8/8 | 10/10/20/20/10/20/20/30 | 3E-4/4E-4/3E-4/2E-4/2E-4/3E-4/4E-4/2E-4 | r_q=r_v=8 | 16 | 128/128/512/128/512/512/512/512 |
| RoB_large LoRA† | 4 (all) | 10/10/20/20/10/20/20/10 | 3E-4/4E-4/3E-4/2E-4/2E-4/3E-4/4E-4/2E-4 | r_q=r_v=8 | 16 | 128 (all) |
| RoB_large AdptP(3M)† | 32 (all) | 10/20/20/20/10/20/20/20 | 3E-5/3E-5/3E-4/3E-4/3E-4/3E-4/3E-4/3E-4 | bottleneck r=64 | — | 128 |
| RoB_large AdptP(0.8M)† | 32 (all) | 5/20/20/20/10/20/20/20 | 3E-4 (all) | r=16 | — | 128 |
| RoB_large AdptH(6M)† | 32 (all) | 10/5/10/10/5/20/20/10 | 3E-5/3E-4/3E-4/3E-4/3E-4/3E-4/3E-4/3E-4 | r=64 | — | 128 |
| RoB_large AdptH(0.8M)† | 32 (all) | 10/5/10/10/5/20/20/10 | 3E-4 (all) | r=8 | — | 128 |

**Table 10 [paper D.2] — DeBERTa XXL LoRA on GLUE** (AdamW, warmup ratio 0.1, linear): batch 8/8/32/4/6/8/4/4; epochs 5/16/30/10/8/11/11/10; LR 1E-4/6E-5/2E-4/1E-4/1E-4/1E-4/2E-4/2E-4; weight decay 0/0.01/0.01/0/0.01/0.01/0.01/0.1; CLS dropout 0.15/0/0/0.1/0.1/0.2/0.2/0.2; r_q=r_v=8; α=8; max seq len 256/128/128/64/512/320/320/128.

**Table 11 [paper D.3] — GPT-2 LoRA** (AdamW, linear, batch 8, 5 epochs, warmup 500 steps, LR 2E-4): weight decay 0.01/0.01/0.0 and dropout 0.1/0.1/0.0 and label smooth 0.1/0.1/0.0 for E2E/WebNLG/DART; r_q=r_v=4; α=32; inference: beam 10, length penalty 0.9/0.8/0.8, no-repeat-ngram 4.

**Table 12 [paper D.4] — GPT-3 adaptation methods** (AdamW, batch 128, 2 epochs, warmup 250,000 tokens, linear): LR FT 5.00E-06 / PreEmbed 5.00E-04 / PreLayer 1.00E-04 / BitFit 1.6E-03 / AdapterH 1.00E-04 / LoRA 2.00E-04; weight decay 0.1 [paper D.4 text]; seq len 384/768/2048 (WikiSQL/MNLI/SAMSum) [paper D.4 text].

**Table 17 [paper F.3] — GPT-3 MNLI-n low-data** (AdamW, warmup 250,000 tokens, linear): batch 20/20/100/128; epochs 40/40/4/2; LR FineTune 5.00E-6 (all), PrefixEmbed 2.00E-04/2.00E-04/4.00E-04/5.00E-04, PrefixLayer 5.00E-05/5.00E-05/5.00E-05/1.00E-04, LoRA 2.00E-4 (all); PrefixEmbed l_p 16/32/64/256 with l_i=8; PrefixTune l_p=l_i=8 (as printed); LoRA r_q=r_v=8.

- **Compute budget** [paper] — GPT-3: VRAM 1.2TB → 350GB (LoRA), 25% speedup, 32.5→43.1 tokens/s per V100 (§4.2, fn.5); checkpoint 350GB → 35MB at r=4 on {Wq,Wv}. GLUE runs: 4×V100 DGX-1 [repo] (scripts say `num_gpus=8` — see §6). Exact GPU counts and wall-clock times not stated → §6.
- **Verbatim artifacts** — [paper §4.1] "We use a random Gaussian initialization for A and zero for B, so ∆W = BA is zero at the beginning of training. We then scale ∆W x by α/r." — note loralib actually does `nn.init.kaiming_uniform_(self.lora_A, a=math.sqrt(5))` + `nn.init.zeros_(self.lora_B)`, `scaling = lora_alpha / r` [repo, `loralib/layers.py`]. [paper App C] WikiSQL: "We encode context as x = {table schema, query} and target as y = {SQL}"; SAMSum: "We encode context as ”\n” concatenated utterances followed by a ”\n\n”, and target as y = {summary}." [paper §5.1] LoRA param count |Θ| = 2 × L̂_LoRA × d_model × r; adapter |Θ| = L̂_Adpt × (2 × d_model × r + r + d_model) + 2 × L̂_LN × d_model.

## 5. Resources & Availability 资源可用性

| Resource | Type | Link | Status | Notes |
|---|---|---|---|---|
| Official code | code | https://github.com/microsoft/LoRA | ✅ public | MIT; last commit 2024-12-17; shallow-cloned this run |
| loralib (PyPI) | code | https://pypi.org/project/loralib/ | ✅ public | `pip install loralib`; PyTorch only [repo README] |
| RoBERTa/DeBERTa LoRA checkpoints | checkpoint | https://github.com/microsoft/LoRA/releases/download/RoBERTa-base/roberta_base_lora_mnli.bin (pattern; one per task/model) | ✅ public | Sampled RoBERTa-base/RoBERTa-large/DeBERTa assets → 200 this run; full per-task list in root README |
| GPT-2 LoRA checkpoints | checkpoint | https://github.com/microsoft/LoRA/releases/download/GPT-2/gpt2_md_lora_e2e.pt (+ dart, webnlg; gpt2_lg_*) | ✅ public | Sampled M/L E2E assets → 200 this run; 1.5–2.3 MB each [repo README] |
| Checkpoints via examples/NLU/README.md | checkpoint | https://github.com/msft-edward/LoRA_private/releases/download/... | ❌ dead | All sampled links → 404 this run; use the root-README release links instead |
| In-repo MNLI LoRA checkpoints | checkpoint | `examples/NLU/roberta_base_lora_mnli.bin`, `roberta_large_lora_mnli.bin` | ✅ in repo | 3.5 MB / 7.4 MB; MNLI only |
| GPT-3 175B | model | — | ❌ not found | Not public (OpenAI API only); GPT-3 code absent from repo → E4–E9 externally unreproducible |
| Base models GPT-2 M/L | model | https://huggingface.co/openai-community/gpt2-medium (+ gpt2-large); legacy S3 URLs in `download_pretrained_checkpoints.sh` still 200 | ✅ public | README: "You still need the original pre-trained checkpoint from Hugging Face" |
| Base models RoBERTa base/large | model | https://huggingface.co/roberta-base, https://huggingface.co/FacebookAI/roberta-large | ✅ public | Used from HF Transformers [paper §5.2] |
| Base model DeBERTa XXL 1.5B | model | https://huggingface.co/microsoft/deberta-v2-xxlarge | ✅ public | Repo warns: their MNLI init checkpoint ≠ HF `microsoft/deberta-v2-xxlarge-mnli` |
| GLUE | dataset | https://huggingface.co/datasets/nyu-mll/glue | ✅ public | QQP source https://quoradata.quora.com/First-Quora-Dataset-Release-Question-Pairs → 403 (bot-blocked); use GLUE copy |
| WikiSQL | dataset | https://huggingface.co/datasets/salesforce/wikisql | ✅ public | BSD 3-Clause [paper App C] |
| SAMSum | dataset | https://huggingface.co/datasets/samsung/samsum | ⚠️ restricted | HF returns 401/auth-required this run (gated); CC BY-NC-ND 4.0 [paper App C] |
| E2E NLG Challenge | dataset | https://github.com/tuetschek/e2e-dataset; bundled at `examples/NLG/data/e2e/` | ✅ public | CC BY-NC-SA 4.0 [paper App C]; exact preprocessed copy in repo |
| DART | dataset | https://huggingface.co/datasets/Yale-LILY/dart; bundled at `examples/NLG/data/dart/` | ✅ public | MIT [paper App C] |
| WebNLG 2017 | dataset | bundled at `examples/NLG/data/webnlg_challenge_2017/`; HF mirror https://huggingface.co/datasets/GEM/web_nlg | ✅ public | CC BY-NC-SA 4.0 [paper App C] |
| Papers with Code | index | https://paperswithcode.com/paper/lora-low-rank-adaptation-of-large-language | ✅ reachable | 200 this run |
| OpenReview (ICLR 2022) | index | https://openreview.net/forum?id=nZeVKeePf9 | ⚠️ unverified | Page/API bot-challenge-blocked this run; supplementary not fetched |

**Repo deep-dive** [repo, cloned 2026-09-27, HEAD c4593f0]:
- Structure: `loralib/` (the package: `layers.py`, `utils.py`), `examples/NLU/` (GLUE, a fork of an adapter-bert codebase: `src/transformers`, per-task shell scripts, `environment.yml`), `examples/NLG/` (GPT-2: `src/gpt2_ft.py` train, `src/gpt2_beam.py` decode, `eval/` evaluation scripts, bundled data, `requirement.txt`). Both example READMEs reference the exact paper (arXiv 2106.09685).
- Experiment ↔ script mapping for CRITICAL experiments:
  - E2 ↔ `examples/NLU/{roberta_base,roberta_large,deberta_v2_xxlarge}_{mnli,sst2,mrpc,cola,qnli,qqp,rte,stsb}.sh` calling `examples/text-classification/run_glue.py` (args incl. `--apply_lora --lora_r --lora_alpha --warmup_ratio --seed 0`). MRPC/RTE/STSB must start from the LoRA MNLI checkpoint per README.
  - E3 ↔ `examples/NLG/README.md` 4-step recipe (train `src/gpt2_ft.py` → beam-decode `src/gpt2_beam.py` → decode → `eval/eval.py`) with exact E2E commands (train batch 8, lr 2e-4, 5 epochs, warmup 500, lora_dim 4, alpha 32, seed 110).
  - E1 (latency): **no code path — not found** in repo.
  - E4 and E5–E9 (all GPT-3 experiments/analyses): **no code path — not found**; GPT-3 appears in the repo only as a topic tag and result images (`examples/NLG/figures/LoRA_GPT3.PNG`).
- Dangling references: `examples/NLU/README.md` checkpoint table links (`msft-edward/LoRA_private/releases/...`) → 404; `examples/NLG/download_pretrained_checkpoints.sh` uses legacy HF S3 URLs (still 200 today, but unmaintained); NLU README's DeBERTa column lists the MNLI `.bin` for every task (apparent copy artifact — per-task DeBERTa assets exist under the root-README release pattern).
- Consistency findings: scripts export `num_gpus=8` vs README "4 V100"; `roberta_base_mnli.sh` uses `--lora_alpha 16` while paper Table 9 says α=8; `deberta_v2_xxlarge_mnli.sh` uses `--lora_r 16 --lora_alpha 32` while paper Table 10 says r_q=r_v=8, α=8; RoBERTa scripts add `--weight_decay 0.1` (absent from Table 9); DeBERTa script uses `--warmup_steps 1000` vs paper's warmup ratio 0.1; NLG README E2E `--length_penalty 0.8` vs paper Table 11's 0.9.
- License & maintenance: code MIT (both root `LICENSE.md` and example LICENSE files); dataset licenses vary per App C. Last commit 2024-12-17. 31 open/closed issues mention reproduce/reproduction; directly relevant: #149 "Can't reproduce the results for GLUE and hyperparameter misalignment" (e.g. `roberta_large_cola.sh` lr 3e-4 vs paper 2e-4; reporter got CoLA 0 / MNLI 31.3 with the scripts), #151, #165, #138 ("Not able to reproduce the scores using provided checkpoint on NLG tasks").

## 6. Reproduction Gap Checklist 复现信息缺口

| Missing | Why it matters | Where to try |
|---|---|---|
| GPT-3 175B base model + GPT-3 adaptation code | E4 (Table 4), E5–E9 (Tables 5–7, Figs 2–8), S5/S6 unreproducible externally | Nothing public; contact authors. loralib + repo GLUE/GPT-2 code covers the rest |
| Per-task LoRA checkpoints via examples/NLU README links | 404 → cannot start GLUE MRPC/RTE/STSB from the MNLI checkpoint as instructed | Root-README release links (verified 200 this run); repo issue #138; contact authors |
| Random seeds | paper: median of 5 seeds (RoBERTa/DeBERTa), mean of 3 (GPT-2), unstated count (GPT-3) | Scripts show only `--seed 0` (NLU) / `--random_seed 110` (NLG README); remaining seeds: ask authors |
| Paper-vs-repo hyperparameter mismatches (lora_alpha 16 vs paper 8 for RoB base; DeBERTa script r=16/α=32 vs paper r=8/α=8; CoLA LR 3e-4 vs 2e-4; E2E length penalty 0.8 vs 0.9; RoBERTa weight decay & DeBERTa warmup form) | deciding which source is authoritative changes results (issue #149 reports large score drops) | Run both settings; compare against Table 2/3; ask authors; follow issue #149 |
| GPU count / wall-clock for GPT-3 and GLUE runs | budgeting + faithful throughput claims | README says 4×V100 DGX-1, scripts say num_gpus=8; GPT-3 count never stated → contact authors |
| Baseline implementations for * rows | FT/BitFit/AdptD/PreEmbed/PreLayer/FTTop2 numbers are reused from prior work — exact baseline tuning not restated | Baseline papers' repos: Houlsby 2019, Pfeiffer 2021 (AdapterFusion), Rücklé 2020 (AdapterDrop), Lin 2020, Li & Liang 2021, Zaken 2021 (BitFit) |
| Latency-measurement code (Table 1 / Fig 5) | E1/S2 not re-runnable as-is | Reimplement from caption (GPT-2 medium, 100-trial average, Quadro RTX8000) |
| LoRA A-matrix init distribution | paper says "random Gaussian"; loralib uses `kaiming_uniform_(a=√5)` for `nn.Linear` (and swaps A/B roles for Embedding) | `loralib/layers.py` [repo]; decide per layer type; ask authors if Gaussian matters |
| SAMSum access | gated on HF (401 this run) | Request access on HF dataset page; original Gliwa et al. 2019 source; CC BY-NC-ND limits redistribution |
| ROUGE implementation for SAMSum / logical-form-accuracy details for WikiSQL | metric implementation affects exact numbers | Li & Liang (2021) setup [paper D.3 dependency]; WikiSQL per Zhong et al. (2017); repo `examples/NLG/eval/` for NLG metrics |
| QQP raw source | footnote link 403 this run | Use GLUE distribution (contains QQP) |
| MNLI few-shot prompt used in Table 8 | "two demonstrations per class and six in-context examples" — exact template not given | Paper App A text; Brown et al. (2020) Appendix G for GPT-3 templates |

---
*Generated by paper-repro-pack on 2026-09-27. Links verified 2026-09-27. Provenance markers: [paper] = stated in the paper (arXiv 2106.09685v2, tables cross-checked against LaTeX source) · [repo] = found in the official repo (microsoft/LoRA @ c4593f0) · [inferred] = our inference, flagged.*
