# Reproduction Package — Scaling Laws for Neural Language Models

| | |
|---|---|
| Paper | Scaling Laws for Neural Language Models [paper] |
| Authors | Jared Kaplan*, Sam McCandlish* et al. — Johns Hopkins University / OpenAI (*equal contribution) |
| Venue | arXiv preprint (Jan 2020); no peer-reviewed venue |
| arXiv | [2001.08361](https://arxiv.org/abs/2001.08361) |
| Official code | ❌ not found — OpenAI released no code, checkpoints, or data for this paper |
| Report date | 2026-09-27 — all links verified on this date |

## 0. 中文摘要

本文（Kaplan 等，OpenAI/JHU，2020，arXiv 预印本）在 WebText2 语料上系统测量了自回归 Transformer 语言模型测试损失（nats/token，1024-token 上下文平均）随规模的幂律缩放：非嵌入参数量 N、数据 token 数 D、训练计算量 C 各自成幂律 L(N)=(Nc/N)^0.076、L(D)=(Dc/D)^0.095、L(Cmin)=(Ccmin/Cmin)^0.050，跨度达 6 个数量级以上；固定 N 时深度/宽度/头数等形状因素影响极小；过拟合程度由 N^0.74/D 决定（D ≥ 5×10^3·N^0.74 可基本避免）；学习曲线服从 L(N,Smin) 幂律（αS≈0.76）；固定算力下最优分配为 N∝C^0.73、B∝C^0.24、S∝C^0.03，即"训练大模型、远早于收敛即停"。关键实验为七大类全量训练扫描（约 768～1.5B 非嵌入参数）。资源方面：官方代码、模型 checkpoint、WebText2 数据集均未公开，仅有第三方 nanoGPT 小规模复现（shehper/scaling_laws）与 OpenWebText/OpenWebText2 替代语料；GPT-2 BPE 词表公开可复用。复现风险：硬件未披露、随机种子仅有统计波动（~0.02）、Adam/Adafactor 超参不全、逐 run 学习率仅给经验公式（式 D.1）、早停判据与 dropout 适用范围含糊、拟合代码缺失；严格复现只能做到统计等价，而非逐点复现。

## 1. Experiment Inventory 实验总览

| # | Experiment | Type | Criticality | Anchor |
|---|---|---|---|---|
| E1 | L(N): loss vs non-embedding parameter count (incl. embedding-counting ablation) | main scaling law | CRITICAL | §3.2, Fig 1, Fig 6 |
| E2 | L(D): loss vs dataset size at fixed model | main scaling law | CRITICAL | §3.3, Fig 1, Fig 4 (left) |
| E3 | L(C) and L(Cmin): loss vs training compute | main scaling law | CRITICAL | §3.3, §6.1, Fig 1, Fig 13 |
| E4 | Shape/hyperparameter independence at fixed N | robustness study | CRITICAL | §3.1, Fig 5 |
| E5 | L(N,D): overfitting law and data requirements | main scaling law | CRITICAL | §4, Fig 9, Table 2 |
| E6 | L(N,Smin): learning-curve law | main scaling law | CRITICAL | §5.2, Fig 4 (right), Fig 11, Table 3 |
| E7 | Optimal allocation of compute: N, B, S, D vs Cmin | main scaling law | CRITICAL | §6.1–6.2, Fig 13–14, Table 6 |
| S1 | Critical batch size Bcrit(L): batch-size scans and gradient-noise scale | component analysis | SECONDARY | §5.1, Fig 10, Fig 18, Eq 1.4 |
| S2 | Transfer to other text distributions (and depth-independence of transfer) | generalization study | SECONDARY | §3.2.2, Fig 8; App D.8, Fig 24 |
| S3 | LSTM vs Transformer comparison | baseline comparison | SECONDARY | §3.2.1, Fig 7 |
| S4 | Sample efficiency vs model size | analysis | SECONDARY | §1.1/Fig 2; App D.4, Fig 19 |
| S5 | Lower bound on early-stopping step Sstop | analysis | SECONDARY | §5.3, Fig 16 (left) |
| S6 | Suboptimal model sizes (compute/step overhead) | sensitivity study | SECONDARY | §6.1, Fig 12; App B.4, Eq B.16–B.17 |
| S7 | Learning-rate schedule scan and LR-vs-N rule | sensitivity study | SECONDARY | App D.6, Fig 22, Eq D.1 |
| S8 | Contradiction point C*, N*, D*, L* and entropy conjecture | analysis | SECONDARY | §6.3, Fig 15, Eq 6.8 |
| P1 | Recurrent/Universal Transformer comparison | appendix baseline | SUPPLEMENTARY | App D.2, Fig 17 |
| P2 | Per-token loss vs context position (incl. nctx=8 runs) | appendix analysis | SUPPLEMENTARY | App D.5, Fig 20–21 |
| P3 | Power-law vs logarithmic functional form check | appendix check | SUPPLEMENTARY | App D.7, Fig 23 |
| P4 | Train-vs-test loss divergence on subsampled datasets | appendix analysis | SUPPLEMENTARY | App D.1, Fig 16 (right) |
| P5 | Compute-efficient vs convergence training (f=10% vs 2%) | appendix analysis | SUPPLEMENTARY | App B.3, Eq B.11–B.14 |

## 2. Critical Experiments 关键实验

### E1 — L(N): loss vs non-embedding parameter count (§3.2, Fig 1, Fig 6)
**Purpose** — Establish the headline power law of loss vs model size N (non-embedding), and show that counting only non-embedding parameters is what makes the trend clean. [paper §3.2]
**Datasets** — WebText2 (§2.3: 20.3M docs, 96 GB text, 2.29×10^10 BPE tokens, 6.6×10^8 test tokens reserved; Reddit outbound links ≥3 karma through Dec 2017 + Jan–Oct 2018, extracted with Newspaper3k). Models trained to near convergence on the full dataset. [paper §2.3, §3.2]
**Baselines** — None; the "comparison" is the same fit with total parameter count (incl. embeddings), which is visibly worse (depth-dependent trend) — Fig 6 left vs right. [paper §3.2, Fig 6]
**Metrics** — Test cross-entropy loss in nats/token, averaged over the 1024-token context, on the WebText2 test split. [paper §1.3, §2]
**Config & training** — Decoder-only Transformers; N ≈ 12·nlayer·dmodel² (standard d_attn = d_ff/4 = d_model, Eq 2.1); shapes from (2,128) up to (6,4288)–(207,768); N spans 768–1.5B non-embedding params; Adam, 2.5×10^5 steps, batch 512×1024 tokens (Adafactor for >1B); LR: 3000-step linear warmup + cosine decay to zero, magnitude by Eq D.1. [paper §2.1, §2.2, §3, §3.2]
**Compute** — Hardware never stated (gap). Compute accounted as C ≈ 6NBS FLOPs, quoted in PF-days. [paper §1.3, §2.1]
**Results** — L(N) ≈ (Nc/N)^αN with αN = 0.076, Nc = 8.8×10^13 [paper Table 5, Eq 3.1]; doubling N reduces loss by factor 2^-0.076 ≈ 0.95 [paper §1.2]. Models <2 layers or extreme depth-to-width ratios deviate from the single trend [paper Fig 6 caption]. 1-layer models excluded from the fit [paper App D.7]. *(Full point cloud: Fig 6 right — cited, not restated.)*
**Authors' conclusion** — Performance depends strongly on scale and only weakly on shape; embeddings can be shrunk without hurting performance (cf. ALBERT). [paper §1.1, §3.2]
**Provenance** — All from main text + appendix D.7 of the paper; no repo exists. [paper]
**要点** — 损失对非嵌入参数量呈幂律 L(N)=(8.8×10^13/N)^0.076,统计口径必须排除 embedding,否则趋势被层数混杂。

### E2 — L(D): loss vs dataset size (§3.3, Fig 1, Fig 4 left)
**Purpose** — Establish the power law of loss vs dataset size D when model capacity is not the bottleneck. [paper §3.3]
**Datasets** — Fixed subsets of WebText2; Figure 9 legend lists 21M / 43M / 86M / 172M / 344M / 688M / 1.4B / 22.0B tokens (§3 states the overall sweep range as 22M–23B tokens). [paper §3, Fig 9]
**Baselines** — None. [paper]
**Metrics** — Same as E1 (WebText2 test loss). [paper §2]
**Config & training** — Single model shape (nlayer, d_model) = (36, 1280); trained on each fixed subset; stopped once test loss ceased to decrease (early stopping). [paper §3.3]
**Compute** — Not stated per-run (gap); C ≈ 6NBS accounting. [paper §1.3]
**Results** — L(D) ≈ (Dc/D)^αD with αD = 0.095, Dc = 5.4×10^13 [paper Table 5, Eq 3.2]. Joint-fit variant gives αD = 0.103, Dc = 1.8×10^13 (see discrepancy flag in §4). [paper Table 2]
**Authors' conclusion** — Loss is a clean power law in D; data requirements grow only sub-linearly with model size. [paper §1.1, §4]
**Provenance** — Main text. [paper]
**要点** — 固定 36×1280 模型在 8 个 WebText2 子集上早停,损失对 D 呈幂律 (5.4×10^13/D)^0.095。

### E3 — L(C) and L(Cmin): loss vs compute (§3.3, §6.1, Fig 1, Fig 13)
**Purpose** — Establish the power law of loss vs training compute, both empirical at fixed batch size and batch-corrected (Cmin). [paper §3.3, §6.1]
**Datasets** — WebText2, full dataset; the compute trend is assembled by scanning over all trained models of varying N. [paper §3.3]
**Baselines** — None. [paper]
**Metrics** — Same as E1. [paper §2]
**Config & training** — All models from the general pool; for each compute budget C the best-performing model at step S = C/(6BS) is selected; batch size B fixed at 2^19 tokens for the empirical trend (hence "not truly optimal"); the adjusted trend uses Cmin = C/(1 + B/Bcrit(L)) (Eq 5.5). [paper §3.3, §5.1]
**Compute** — C in PF-days, non-embedding, C ≈ 6NBS; 1 PF-day = 8.64×10^19 FLOPs. [paper §1.3]
**Results** — Fixed-batch: L(C) ≈ (1.6×10^7/C)^0.057 [paper Table 5, Fig 13]; adjusted: L(Cmin) ≈ (3.1×10^8/Cmin)^0.050 [paper Table 5, Eq 1.3]. Conspicuous lump at 10^-5 PF-days marks the 1→2 layer transition; 1-layer models excluded from fits. [paper Fig 13, App D.7]
**Authors' conclusion** — The L(Cmin) trend (not raw C) should be used for prediction and extrapolates reliably to larger compute. [paper Fig 13 caption]
**Provenance** — Main text + appendix D.7. [paper]
**要点** — 计算律有两版:固定 batch 的 (1.6×10^7/C)^0.057 与批校正后的 (3.1×10^8/Cmin)^0.050,预测必须用后者。

### E4 — Shape/hyperparameter independence at fixed N (§3.1, Fig 5)
**Purpose** — Test whether architecture shape (depth, width, heads, d_ff) matters when total non-embedding parameters are held fixed. [paper §3.1]
**Datasets** — WebText2. [paper §2.3]
**Baselines** — Reference point: the (nlayer, d_model) = (48, 1600) model of GPT-2 [RWC+19]. [paper Fig 5 caption]
**Metrics** — Test loss; deviations quoted relative to the L(N) fit baseline ("small differences in parameter counts are compensated for by using the fit to L(N) as a baseline"). [paper Fig 5 caption]
**Config & training** — Fix N ≈ 12·nlayer·d_model² and vary one factor at a time: feed-forward ratio d_ff/d_model, attention head dimension d_model/n_heads, aspect ratio d_model/n_layer; two sizes (≈25M and ≈50M non-embedding params). [paper §3.1, Fig 5]
**Compute** — Not stated (gap). [paper]
**Results** — Loss varies only a few percent across a wide shape range; aspect ratio varies by ×40 with slight impact; (6, 4288) reaches loss within 3% of the (48, 1600) GPT-2-shaped model. [paper Fig 5 caption]
**Authors' conclusion** — Performance depends very weakly on shape hyperparameters; scale is what matters. [paper §1.1, §3.1]
**Provenance** — Main text. [paper]
**要点** — 固定参数量下,长宽比可在 40 倍内变化,损失仅波动几个百分点,(6,4288) 与 GPT-2 的 (48,1600) 形状损失差 <3%。

### E5 — L(N,D): overfitting law (§4, Fig 9, Fig 4 left, Table 2)
**Purpose** — Determine how test loss depends on model size and dataset size jointly, i.e. how much data is needed to train a model of size N without overfitting. [paper §4]
**Datasets** — WebText2 subsamples: 21M–22.0B tokens (8 sizes, Fig 9 legend); full 22B treated as D = ∞ (no overfitting observed except largest models). [paper §4.2, Fig 9]
**Baselines** — None. [paper]
**Metrics** — Test loss; overfitting quantified as δL(N,D) = L(N,D)/L(N,∞) − 1 (Eq 4.2). [paper §4.2]
**Config & training** — All models regularized with 10% dropout [paper §4.2]; early stopping once test loss no longer decreases; models trained/optimized the same way as elsewhere (Adam etc., §2.2). Train-vs-test divergence curves use 300M-param models (Fig 16 right). [paper App D.1]
**Compute** — Not stated (gap). [paper]
**Results** — Fit of Eq 1.5 (Table 2, transcribed in §4 below): αN = 0.076, αD = 0.103, Nc = 6.4×10^13, Dc = 1.8×10^13 [paper Table 2]. Excellent fit except D reduced ×1024 (≈2×10^7 tokens, 40 updates/epoch) [paper §4.2]. Overfitting depends only on N^(αN/αD)/D (Eq 4.3, Fig 9 right). To avoid overfitting: D ≳ (5×10^3)·N^0.74 (Eq 4.4, given seed-loss variation ≈0.02). [paper §4.2]
**Authors' conclusion** — Universality of overfitting: data may grow sub-linearly (N^0.74) with model size; models <10^9 params train on 22B tokens with minimal overfitting. [paper §1.1, §4.2]
**Provenance** — Main text + Fig 16 detail in appendix D.1. [paper]
**要点** — 过拟合只看 N^0.74/D:数据按模型大小 0.74 次幂亚线性增长即可避免,4 参数联合拟合值见表 2(与表 5 略不同,勿混用)。

### E6 — L(N,Smin): learning-curve law (§5.2, Fig 4 right, Fig 11, Table 3)
**Purpose** — Show that training curves follow a predictable power law whose parameters are roughly independent of model size, enabling extrapolation of long runs from early loss. [paper §5.2]
**Datasets** — WebText2 (infinite-data limit; stable Adam-optimized runs only). [paper §5.2]
**Baselines** — None. [paper]
**Metrics** — Test loss vs Smin, the step count re-expressed at B ≫ Bcrit via Smin = S/(1 + Bcrit(L)/B) (Eq 5.4). [paper §5.1]
**Config & training** — All post-warmup training steps of the stable Adam runs are included in the fit; B = 2^19 tokens for the raw step axis. [paper §5.2]
**Compute** — Not stated (gap); compute version uses Cmin = C/(1 + B/Bcrit(L)) (Eq 5.5). [paper]
**Results** — L(N,Smin) = (Nc/N)^αN + (Sc/Smin)^αS with αN = 0.077, αS = 0.76, Nc = 6.5×10^13, Sc = 2.1×10^3 [paper Table 3, Eq 5.6]. Fits are imperfect but compelling; mediocre at very small S (transient). [paper §5.2, Fig 11 caption]
**Authors' conclusion** — Universality of training: early portions of learning curves predict final loss; power-law universality suggests model-size-independent Hessian eigenvalue density. [paper §1.1, §5.2]
**Provenance** — Main text. [paper]
**要点** — 学习曲线两参数幂律 (αS≈0.76) 跨模型尺寸通用,可用早期 loss 外推长训练的最终 loss。

### E7 — Optimal allocation of compute (§6.1–6.2, Fig 13–14, Table 6)
**Purpose** — Determine how to split a fixed compute budget between model size, batch size, serial steps, and data — the paper's headline prescription. [paper §6]
**Datasets** — WebText2 (same run pool as E3/E6, batch-corrected). [paper §6]
**Baselines** — "Typical" practice of training to f=2% above converged loss (App B.3 comparison: compute-efficient training uses 7.7× fewer updates, 2.7× more parameters, 65% less compute for the same loss). [paper App B.3]
**Metrics** — Test loss at optimally allocated compute; N(Cmin), B(Cmin), S(Cmin), D(Cmin) exponents. [paper §6]
**Config & training** — Uses Bcrit(L) and Cmin machinery of §5.1 (Eqs 5.2–5.5); empirical frontier from the run pool, theoretical frontier from minimizing L(N,Smin) at fixed C (App B, Eqs B.3–B.10). [paper §6, App B]
**Compute** — Express in Cmin (PF-days); training at B ≈ Bcrit costs C = 2·Cmin. [paper §6.3]
**Results** — Empirical: N(Cmin) ∝ Cmin^0.73 (Eq 6.1), Smin ∝ Cmin^0.03 (Eq 6.2), Bcrit ∝ Cmin^0.24 [paper §6.1]; full scales in Table 6 (Nopt = 1.3×10^9·Cmin^0.73 etc., transcribed in §4 below). Predicted from L(N,Smin): αCmin = 1/(1/αS+1/αB+1/αN) ≈ 0.054 (Eq 6.4) and N ∝ Cmin^0.71 (Eq 6.5) — matching within a few percent. Note: Figure 14 also shows a fixed-batch fit N = (1.6×10^9)·C^0.88 — distinct from the Cmin^0.73 law. [paper §6.1–6.2, Fig 14]
**Authors' conclusion** — Compute-efficient training trains very large models stopped far short of convergence; most extra compute goes to model size; D ∝ C^0.27. [paper §1.1, §6]
**Provenance** — Main text + appendix B derivations. [paper]
**要点** — 最优分配:N∝C^0.73、B∝C^0.24、S∝C^0.03、D∝C^0.27,预算加倍主要用来买更大的模型并提前停止。

## 3. Secondary & Supplementary Experiments 消融与补充实验

| # | Experiment | Anchor | Purpose | Key setting | Headline result | Conclusion |
|---|---|---|---|---|---|---|
| S1 | Critical batch size Bcrit(L) | §5.1, Fig 10, Fig 18, Eq 1.4 | Measure the loss-dependent critical batch size that powers the Cmin/Smin adjustments | Batch-size scans at fixed loss for N = 3M and 85M models (Fig 18) | Bcrit(L) = B*/L^(1/αB), B* = 2.1×10^8 tokens, αB = 0.21 [Table 5]; Bcrit doubles per 13% loss decrease; independent of model size; roughly tracks gradient noise scale [MKAT18] | Train at B ≈ Bcrit for optimal time/compute tradeoff [paper §5.1] |
| S2 | Transfer to other distributions | §3.2.2, Fig 8; App D.8, Fig 24 | Test whether OOD test loss follows in-distribution loss | Models trained only on WebText2, evaluated on Books, Wikipedia, Common Crawl, Internet Books samples | Loss on other corpora improves with N with a small, slowly growing constant offset; depends only on training-distribution loss, not training phase or depth; 12-layer 1.5B model overfit Internet Books (one-off surprise) [Fig 24] | Transfer incurs ~constant penalty and scales with in-distribution performance [paper §3.2.2] |
| S3 | LSTM vs Transformer | §3.2.1, Fig 7 | Compare architectures as function of N | LSTMs trained on same dataset/context length | LSTMs match Transformers on early context tokens only; plateau after <100 tokens; Transformers win at scale via long-context use | Transformers asymptotically outperform LSTMs [paper §3.2.1] |
| S4 | Sample efficiency vs N | §1.1, Fig 2; App D.4, Fig 19 | Show larger models need fewer tokens/steps to a target loss | Same run pool, thresholds at fixed losses | Minimum serial steps to any fixed loss falls steeply with N; sample efficiency improves ~×100 from smallest to very large model [Fig 19] | Larger models are more sample-efficient [paper §1.1] |
| S5 | Early-stopping step lower bound | §5.3, Fig 16 left | Bound when data-limited training should stop | Sstop vs Sc·[L(N,D)−L(N,∞)]^(-1/αS); empirical Sstop adjusted to mimic B ≫ Bcrit | Empirical Sstop tracks the derived lower bound (Eq 5.7) | Provides a usable stopping-step estimate for data-limited runs [paper §5.3] |
| S6 | Suboptimal model sizes | §6.1, Fig 12; App B.4 | Cost of training off the optimal size | Eq B.16–B.17 from the L(N,Smin) fit | Models 0.6×–2.2× of optimal need only +20% compute; 2.2× larger model needs 45% fewer steps | Optimal size is broad; bigger models trade steps for parallelism [paper App B.4] |
| S7 | LR schedules & LR-vs-N rule | App D.6, Fig 22, Eq D.1 | Check sensitivity to LR schedule; give the working LR rule | 3M-param model, many schedules (cosine, linear, faster/slower, no decay-to-zero in this scan) | Schedule choice mostly irrelevant (variation ≈ run-to-run noise ≈ 0.05); larger models need smaller LR; working rule LR(N) ≈ 0.003239 − 0.0001395·log(N) (Eq D.1; breaks for N > 10^10) | Warmup + final decay + sufficient summed LR is what matters [paper App D.6] |
| S8 | Contradiction point & entropy conjecture | §6.3, Fig 15, Eq 6.8 | Locate where L(Cmin) and L(D(Cmin)) trends cross | Single-epoch data usage D(Cmin) = 4×10^10·(Cmin/PF-day)^0.26 (Eq 6.7) vs overfitting-driven need D ∝ Cmin^0.54 (Eq 6.6) | Crossing at C* ~ 10^4 PF-days, N* ~ 10^12 params, D* ~ 10^12 tokens, L* ~ 1.7 nats/token (order-of-magnitude uncertain) | Scaling laws must break down by then; L* conjectured as entropy-per-token of natural language [paper §6.3] |
| P1 | Recurrent/Universal Transformers | App D.2, Fig 17 | Compare parameter-reuse models | 2×/4×/8× reuse vs non-recurrent | Slightly better per parameter, slightly worse per FLOP than standard Transformers | Re-use helps at fixed N, hurts at fixed compute [paper Fig 17] |
| P2 | Per-token loss vs context position | App D.5, Fig 20–21 | How loss varies within the 1024-token context | Also nctx = 8 models | Loss ∝ power law in position T (e.g. 2.3 + 5.4·T^0.62 for the largest model shown, Fig 20); larger models better at early tokens; tiny-context models dominate early positions | Context use improves smoothly with scale [paper App D.5] |
| P3 | Power law vs log fit | App D.7, Fig 23 | Functional-form sanity check | L(N) fit with/without 1-layer and non-converged largest models | Power law qualitatively better than logarithmic fit; exclusions change constants only marginally | Justifies power-law ansatz and fit exclusions [paper App D.7] |
| P4 | Train vs test divergence on small D | App D.1, Fig 16 right | Diagnose overfitting dynamics | 300M-param models on the 21M–22B subsamples | Test loss follows infinite-data curve then diverges; overfitting is overestimated by Ltest − Ltrain | Early stopping still recovers near-optimal loss [paper Fig 16] |
| P5 | Efficient vs convergence training | App B.3, Eq B.11–B.14 | Quantify savings of stopping at f = αN/αS ≈ 10% above converged loss vs typical f = 2% | Derived from L(N,Smin) constants | 7.7× fewer updates, 2.7× more parameters, 65% less compute for the same loss | Compute-efficient training is far more sample-efficient than convergence training [paper App B.3] |

## 4. Reproduction Settings Summary 复现设置汇总

- **Environment** — Not stated: no Python/framework/CUDA versions, no hardware description anywhere in the paper (verified by full-text and LaTeX-source search). [gap]

- **Global training hyperparameters** (union of §2.2, §3, §4.2, App D.6 — the paper has no single HP table; these sentences are the complete spec):

| Setting | Value | Anchor |
|---|---|---|
| Optimizer | Adam; Adafactor for models >1B params (memory) | [paper §2.2] |
| Adam β1/β2/ε, weight decay, grad clip | Not specified | [gap] |
| Steps | Fixed 2.5×10^5 parameter updates (unless otherwise noted) | [paper §2.2] |
| Batch size | 512 sequences × 1024 tokens = 2^19 tokens (unless otherwise noted) | [paper §2.2, §3] |
| LR schedule | 3000-step linear warmup, cosine decay to zero (default for all included runs) | [paper §2.2] |
| LR magnitude rule | LR(N) ≈ 0.003239 + (−0.0001395)·log(N) (rule of thumb "for most runs"; breaks for N > 10^10) | [paper Eq D.1] |
| Dropout | 10% ("we regularize all our models with 10% dropout" — stated in §4.2 only; scope for §3.2 convergence runs is not restated there) | [paper §4.2] |
| Early stopping | "tracking test loss and stopping once it is no longer decreasing" (no patience/window given) | [paper §4.2] |
| Context length | nctx = 1024 (except explicit short-context experiments, e.g. nctx = 8) | [paper §2.1, App D.5] |
| Vocabulary | BPE, nvocab = 50257 (GPT-2 tokenizer) | [paper §2] |
| Parameter count | N ≈ 2·d_model·nlayer·(2·d_attn + d_ff) = 12·nlayer·d_model² (excludes biases, embeddings: nvocab·d_model embed + nctx·d_model positional) | [paper Eq 2.1] |
| Compute accounting | C ≈ 6NBS FLOPs (non-embedding); C_forward ≈ 2N + 2·nlayer·nctx·d_attn; 1 PF-day = 8.64×10^19 FLOPs | [paper §1.3, §2.1, Table 1] |
| Random seeds | None listed; seed-to-seed loss variation ≈ 0.02 (§4.2); run-to-run variation in LR scan ≈ 0.05 (App D.6) | [paper §4.2, App D.6] |
| Shape pool | nlayer/d_model from (2,128) to (207,768); N from 768 to 1.5B; dataset subsets 22M–23B tokens | [paper §3] |

- **Complete fit-constant tables** (these are the paper's "hyperparameter tables" — transcribed in full; do not mix rows across tables):

Table 2 — joint fit to L(N,D) [paper §4.2]:

| Parameter | αN | αD | Nc | Dc |
|---|---|---|---|---|
| Value | 0.076 | 0.103 | 6.4×10^13 | 1.8×10^13 |

Table 3 — fit to L(N,S) [paper §5.2]:

| Parameter | αN | αS | Nc | Sc |
|---|---|---|---|---|
| Value | 0.077 | 0.76 | 6.5×10^13 | 2.1×10^3 |

Table 5 — key parameters of all trend fits [paper App A]:

| Power law | Scale (tokenization-dependent) |
|---|---|
| αN = 0.076 | Nc = 8.8×10^13 params (non-embed) |
| αD = 0.095 | Dc = 5.4×10^13 tokens |
| αC = 0.057 | Cc = 1.6×10^7 PF-days |
| αCmin = 0.050 | Ccmin = 3.1×10^8 PF-days |
| αB = 0.21 | B* = 2.1×10^8 tokens |
| αS = 0.76 | Sc = 2.1×10^3 steps |

Table 6 — compute-efficient scaling [paper App A]:

| Compute-efficient value | Power law | Scale |
|---|---|---|
| Nopt = Ne·Cmin^pN | pN = 0.73 | Ne = 1.3×10^9 params |
| Bcrit = (B*/L^(1/αB)) = Be·Cmin^pB | pB = 0.24 | Be = 2.0×10^6 tokens |
| Smin = Se·Cmin^pS (lower bound) | pS = 0.03 | Se = 5.4×10^3 steps |
| Dopt = De·Cmin^pD (1 epoch) | pD = 0.27 | De = 2×10^10 tokens |

⚠️ **Known-number discrepancies to flag** (both occurrences correct, different fits — per extraction rules):
- αD: 0.103 with Dc = 1.8×10^13 in the joint L(N,D) fit (Table 2) vs 0.095 with Dc = 5.4×10^13 in the marginal L(D) fit (Table 5, Eq 1.2). The paper notes the joint fit "differs very slightly" from the marginal fits. [paper §4.2]
- αN: 0.076 (L(N), Table 5) vs 0.077 (L(N,S), Table 3); Nc likewise 8.8×10^13 vs 6.5×10^13.
- N_opt: Figure 14 shows two distinct fits — N = (1.3×10^9)·Cmin^0.73 (batch-adjusted, the headline law) and N = (1.6×10^9)·C^0.88 (fixed-batch, empirical). Third-party writeups sometimes quote the latter as "the" N_opt law.

- **Verbatim artifacts** — the load-bearing equations, copied exactly from the paper [paper Eq numbers as printed]:
  - Eq 1.5/4.1: L(N,D) = [ (Nc/N)^(αN/αD) + Dc/D ]^αD
  - Eq 1.6/5.6: L(N,Smin) = (Nc/N)^αN + (Sc/Smin)^αS
  - Eq 1.4/5.3: Bcrit(L) = B*/L^(1/αB)
  - Eq 5.4: Smin(S) = S / (1 + Bcrit(L)/B)
  - Eq 5.5: Cmin(C) = C / (1 + B/Bcrit(L))
  - Eq 4.4: D ≳ (5×10^3)·N^0.74
  - Eq D.1: LR(N) ≈ 0.003239 + −0.0001395·log(N)
  - Eq 6.8: C* ~ 10^4 PF-days, N* ~ 10^12 params, D* ~ 10^12 tokens, L* ~ 1.7 nats/token

- **Compute budget** — Total aggregate compute of the whole study is not stated (gap).

## 5. Resources & Availability 资源可用性

All links below were fetched/verified on **2026-09-27** (HTTP status from `curl`/web fetch this run).

| Resource | Type | Link | Status | Notes |
|---|---|---|---|---|
| Official code | code | — (searched: GitHub `user:openai` repo search = 0 hits; HF papers page links no code; paper prints no code URL) | ❌ not found | OpenAI never released code for this paper |
| Official checkpoints | checkpoint | — (HF papers page links none; no download URL anywhere in paper) | ❌ not found | GPT-2 public checkpoints are different models (WebText v1), NOT this paper's models |
| WebText2 | dataset | — (described procedurally in §2.3 only; no release) | ❌ not found | Authors' own crawl; karma-threshold Reddit outbound links + Newspaper3k |
| GPT-2 BPE tokenizer (nvocab = 50257) | tokenizer | https://openaipublic.blob.core.windows.net/gpt-2/models/117M/encoder.json (200) · https://huggingface.co/openai-community/gpt2 (200) | ✅ public | The exact tokenizer family the paper uses [paper §2] |
| Common Crawl (test distribution) | dataset | https://commoncrawl.org (200) | ✅ public | Paper tests on "similarly-prepared samples" — prep not specified |
| English Wikipedia (test distribution) | dataset | https://huggingface.co/Wikipedia/datasets (200) | ✅ public | Same caveat on sample preparation |
| Books Corpus (test distribution) | dataset | https://huggingface.co/datasets/bookcorpus/bookcorpus (200) | 🔗 third-party | Original 2015 processing not available; HF copy differs from the paper's "similarly-prepared sample" |
| "Internet Books" test collection | dataset | — (no URL, no build recipe in paper) | ❌ not found | Authors' own collection |
| WebText v1 open replication | dataset | https://huggingface.co/datasets/Skylion007/openwebtext (200) | 🔗 third-party | CC0; ~8M docs; standard stand-in for WebText, not WebText2 |
| OpenWebText2 (EleutherAI) | dataset | https://github.com/EleutherAI/OpenWebText2 (200) · https://openwebtext2.readthedocs.io/en/latest/ (200) | 🔗 third-party | Common-Crawl-based recreation; different corpus than WebText2 |
| OpenWebText2 cleaned (HF mirror) | dataset | https://huggingface.co/datasets/Geralt-Targaryen/openwebtext2 (200) | 🔗 third-party | Apache-2.0; cleaned/decontaminated variant |
| Third-party reproduction of this paper | code | https://github.com/shehper/scaling_laws (200, shallow-cloned this run) | 🔗 third-party | nanoGPT-based; MIT; last push 2023-12-08; 58 stars; 0 open issues |
| OpenAI announcement page | page | https://openai.com/index/scaling-laws-for-neural-language-models/ (403 to bots this run) | ⚠️ restricted | Bot-blocked; content unverifiable this run; not needed for reproduction |
| ⚠️ Name trap: "Raziel1234/WebText-2" | dataset | https://huggingface.co/datasets/Raziel1234/WebText-2 (200) | 🔗 third-party | Unrelated "Orion-Spark-2" corpus with a misleading name — NOT the paper's WebText2 |

**Repo deep-dive — shehper/scaling_laws (third-party; no official repo exists).** Shallow-cloned to `repro-2001.08361/third-party-scaling_laws/`. [repo]
- README names the exact paper + arXiv ID 2001.08361. [repo README]
- Experiment mapping: L(N), L(N,D), L(C), N_opt(C) (its fits: αN = 0.082 for L(N); αN = 0.076/αD = 0.122 for L(N,D); N_opt ∝ C^0.90) and Bcrit estimation ↔ `train.py`/`model.py` (nanoGPT), `config/train_gpt2.py` + `config/scale_gpt.py` (sweep configs via `configurator.py`), `config/estimate_critical_batch.py` (Bcrit), analysis `kaplan_scaling_laws.ipynb`; W&B logs linked from README. **E2's L(D) fit explicitly not done** ("we did not find a fit to L(D)"); E4 shape-independence and E5-style subsample sweeps not mapped. [repo]
- Environment spec: none (no requirements.txt / environment.yml) — inherits nanoGPT's PyTorch stack; Python/CUDA versions unstated. [repo]
- Checkpoints: none. Dangling references: none found; scale caveat prominent (max 6.3M params, 3 orders of magnitude below the paper). [repo]

## 6. Reproduction Gap Checklist 复现信息缺口

| Missing | Why it matters | Where to try |
|---|---|---|
| Hardware (GPU/TPU type, count, wall-clock) | Cannot plan compute or sanity-check throughput; paper reports only FLOPs (C ≈ 6NBS) | Nowhere in paper/LaTeX source (verified); ask authors (emails on p.1); treat as FLOP-only reproduction |
| Random seeds / run manifest (which shapes × steps × subsets were run) | Exact point-cloud reproduction impossible; only statistical equivalence achievable | Contact authors; digitize figures; N = 12·nlayer·d_model² recovers shapes [inferred] |
| Adam β1/β2/ε, weight decay, gradient clipping, initialization scale | Optimizer spec incomplete; scaling results can be init-scale sensitive (authors flag this themselves) | App C caveat list admits possible un-tuned HPs; ask authors; GPT-2 paper conventions as fallback [inferred] |
| Adafactor configuration for >1B-param models | Largest-model points (up to 1.5B) not exactly reproducible | Ask authors |
| Per-run learning rates | Only the LR(N) rule of thumb (Eq D.1) + "we experimented" — divergence risk for large N | Eq D.1 + App D.6 guidance; authors |
| Dropout scope | "10% dropout for all our models" is stated only inside §4.2; whether the §3.2 convergence runs (E1) used it is not restated | Assume yes for all runs [inferred, flagged]; confirm with authors |
| Early-stopping criterion detail | "test loss ceased to decrease" — no patience/smoothing/window; directly shifts L(D)/L(N,D) points | Ask authors; pick a fixed-window rule and state it |
| WebText2 itself (URLs, dedup, karma filter implementation, 6.6×10^8-token test split) | The central dataset; no public release | Substitute OpenWebText/OpenWebText2 (constants Nc, Dc, Cc are tokenization-dependent and will shift) |
| Test-sample preparation for Books/Wikipedia/Common Crawl/Internet Books ("similarly-prepared samples") | Transfer results (S2) depend on it | GPT-2 paper [RWC+19] for WebText prep; authors for the rest |
| LSTM baseline configs (sizes, HPs) and Universal Transformer reuse configs | S3/P1 not exactly reproducible | Ask authors; shehper repo does not cover these |
| Curve-fitting code / fit uncertainties | Fit constants carry no error bars; refitting procedure ambiguous (weighting, which points) | Use shehper notebook as template [inferred]; authors |
| "Convergence" definition for L(N) runs ("near convergence"; largest models excluded from fit) | Affects αN/Nc | App D.7 gives exclusions partially; ask authors |

---
*Generated by paper-repro-pack on 2026-09-27. Links verified 2026-09-27. Provenance markers: [paper] = stated in the paper · [repo] = found in the third-party repo (no official repo exists) · [inferred] = our inference, flagged.*
