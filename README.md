# Kaggle ROGII Wellbore Geology Prediction

## Current experiment status (2026-07-23)

- D22 is final: cap `2.0 / 2.5 / 3.0` each scored `6.667`, while cap 2 and
  cap 2.5 crossed with grouped-OOF WellBias each scored **`6.638`**. The two
  orthogonal corrections therefore improved the no-WellBias tier by `0.029`.
- The D23 grid contains five materially distinct routes: A27 centered PF-1.3
  branch shape, A31 mean-preserving Toe tilt, A28 PF-1.3 blend `w=0.62`,
  U-continuity8, and A27 crossed with grouped-OOF WellBias.
- The D23 budget is final at exactly `5 / 5`: refs `54917836 / 54917838 /
  54918138 / 54918139 / 54918377`. A27 scored **`6.476`**, A31 scored `6.546`,
  A27 plus WellBias scored `6.562`, U-continuity8 scored `6.617`, and A28
  completed without a published score. A27 is the repository best.
- Current high-ranking public Code was audited before reuse. Six differently
  titled notebooks produced the same byte-identical P100 cap-2 artifact, so
  only genuine output changes were admitted to the D23 grid.
- The selected D22 runner-up-tier representative is cap 2.5 (`6.667`, ref
  `54895437`). Its English public Code edition completed as
  [`rogii-p100-cap2-5-measured-6-667`](https://www.kaggle.com/code/muelsyse111/rogii-p100-cap2-5-measured-6-667)
  and is byte-exact to the scoring artifact (SHA-256 `2d2d40b...778494`). It
  must never be competition-submitted.
- Detailed evidence: [2026-07-23 results](docs/RESULTS_2026-07-23.md)

## Current experiment status (2026-07-24)

- The D24 budget is final at exactly `5 / 5`: refs `54941181 / 54941242 /
  54941455 / 54941513 / 54941756`. The routes are A27 weights `0.08 / 0.12 /
  0.15`, plus weights `0.10 / 0.12` crossed with the A31-derived zero-mean
  0.18 ft Heel-to-Toe tilt. All five own outputs passed ordered-ID,
  finite-value, SHA-256, controlled-distance, non-duplicate, and log audits
  before submission; scores are pending.
- Current public Code was audited again. Four high-position pages still emit
  the old cap-2 SHA, while the two new frontier pages share one cap2-plus-0.522
  output. Those title duplicates are not allocated separate submission slots.
- The D23 runner-up A31 (`6.546`, ref `54917838`) completed as a detailed
  English documentation notebook and reproduced the scoring artifact
  byte-for-byte. Kaggle currently blocks making any notebook with this
  competition source public until the competition ends, so it remains
  private and ready for the permitted publication date; it will never be
  competition-submitted.
- Detailed evidence: [2026-07-24 results](docs/RESULTS_2026-07-24.md)

## Current validated status (2026-07-21)

- D21 established a new repository best: MHA260SEP2 plus grouped-OOF WellBias
  scored **`6.829`** (ref `54869492`). MHA250SEP2 plus WellBias was the
  runner-up at `6.832` (ref `54869268`).
- The five final D21 scores were `6.858 / 6.849 / 6.855 / 6.832 / 6.829`.
  WellBias improved both SEP2 alpha settings by exactly `0.026`, while alpha
  `2.6` improved alpha `2.5` by `0.003` with and without WellBias.
- The D21 UTC budget is final at exactly `5 / 5`; no further competition
  submission was made after refs `54869017 / 54869048 / 54869266 / 54869268 /
  54869492`.
- All five D21 routes completed privately and passed the 14,151-row ordered-ID,
  finite-value, final-file, and fatal-log audits before submission.
- Detailed evidence: [2026-07-21 results](docs/RESULTS_2026-07-21.md)

## Completed experiment status (2026-07-22)

- The current score-ascending public source reports `6.594`. Its public
  documentation reproduction produced a byte-identical 14,151-row output with
  SHA-256 `b192d3f348ae00680dc4df942b95cef5fd708c636a741f77dfb6b6e89b9ded4a`.
- The five pre-registered routes were cap `2.0 / 2.5 / 3.0`, plus cap
  `2.0 / 2.5` crossed with grouped-OOF WellBias. All five private outputs passed
  the 14,151-row ordered-ID, finite-value, SHA-256, branch-report, and fatal-log
  audits before submission.
- The D22 budget is final at exactly `5 / 5`; refs `54895366 / 54895437 /
  54895837 / 54896174 / 54896197` scored `6.667 / 6.667 / 6.667 / 6.638 /
  6.638`. The tied WellBias routes are the repository best.
- The D21 runner-up is published as English Code:
  [`rogii-mha250sep2-wellbias-measured-6-832`](https://www.kaggle.com/code/muelsyse111/rogii-mha250sep2-wellbias-measured-6-832).
  Version 1 completed publicly and is byte-identical to the private scoring
  artifact (SHA-256 `3d1069d2d40eeb3e508d73318aedcd8d164a1177b2075d9bc9608d3fa49a583d`).
- Detailed evidence: [2026-07-22 results](docs/RESULTS_2026-07-22.md)

## Current validated status (2026-07-19)

- Daily competition submissions: exactly `5 / 5`; no further submission is
  allowed today.
- All five D19 submissions completed:
  - Prefix-GR RF WellBias: **`6.988`** (ref `54820920`; new repository best)
  - RobustPF sub7 reproduction: `7.454` (ref `54820459`)
  - [Grouped OOF Meta reproduction](https://www.kaggle.com/code/muelsyse111/rogii-oof-meta-direct-repro-measured-7-866):
    `7.866` (ref `54820549`; grouped OOF RMSE `9.8770`)
  - [Cycle8 reproduction](https://www.kaggle.com/code/muelsyse111/rogii-cycle8-repro-measured-7-960):
    `7.960` (ref `54820520`; upstream source claim `6.909`)
  - Independent LGB/ET adaptive route: `10.308` (ref `54824801`)
- All five private runs completed before submission and passed the 14,151-row
  ID-order, finite-value, log, and final-output audits.
- WellBias improves the former A04 best (`7.010`) by `0.022` RMSE while moving
  the visible prediction by `0.3710 ft` RMS. Its final SHA-256 is
  `54d5b3b08943e55c2c60a6fcb8b15edf5a950afa469f0978f6a40ff5c81d039d`.
- RobustPF and Cycle8 produced numerically identical visible predictions but
  scored `7.454` and `7.960`, a `0.506` gap that reinforces execution lineage
  as an experimental variable.
- The LGB/ET adaptive run reports per-well adaptive CV RMSE `9.5355` but scored
  `10.308`. Its final
  SHA-256 is
  `28603fe1ad9e5a958ca237dba143b5c3af33673f85e010c5f8fd7673e798e190`,
  and its visible prediction is `10.4848 ft` RMS from A04.
- The OOF meta route reports grouped OOF RMSE `9.8770`, a `0.5426` improvement
  over its public ridge baseline, and is materially different from the A04
  visible prediction (`3.3722 ft` RMS).
- Two new model-package variants (`gmax=0.0075/0.010`) differ by only
  `0.0055 ft` RMS and sit within `0.0220 ft` RMS of Cycle8. They were rejected
  as quota candidates because the public ablation evidence puts changes this
  small inside rerun noise.
- The three agent research notebooks are now public, and the scored A04
  reproduction has been pushed as a public English documentation version.
- A legal leave-one-well-out neighbor-shape transfer improved the anchor from
  `15.9099` to `15.6153` pooled RMSE, but remained far behind the 7.x public
  stack and was correctly withheld from Kaggle submission.
- New public decision notebook:
  [Rerun Noise and Micro-Tuning Filter](https://www.kaggle.com/code/muelsyse111/rogii-rerun-noise-and-micro-tuning-filter).
- New public negative-result notebook:
  [Neighbor Profile Transfer Honest Audit](https://www.kaggle.com/code/muelsyse111/rogii-neighbor-profile-transfer-honest-audit).
- Detailed evidence: [2026-07-19 results](docs/RESULTS_2026-07-19.md)

## Current validated status (2026-07-18)

- Daily competition submissions: exactly `5 / 5`; no further submission.
- Score-bearing public-source reproductions:
  - [Public rebuild](https://www.kaggle.com/code/muelsyse111/rogii-d18-public-rebuild-7295): `9.571` (`54808956`)
  - [Dual track](https://www.kaggle.com/code/muelsyse111/rogii-d18-dual-track-calibrated): `7.123` (`54808958`)
  - [A04 residual transfer](https://www.kaggle.com/code/muelsyse111/rogii-d18-a04-residual-transfer-repro): `7.010` (`54809311`)
  - [G040/S12](https://www.kaggle.com/code/muelsyse111/rogii-d18-anchor-g040-s12-repro): `7.170` (`54809350`)
  - [Safe rebuild](https://www.kaggle.com/code/muelsyse111/rogii-d18-safe-rebuild-7016-repro): `7.130` (`54809629`)
- New public research notebooks:
  - [Five-Submission Agent Playbook](https://www.kaggle.com/code/muelsyse111/rogii-five-submission-agent-playbook)
  - [Public Route Distance Atlas](https://www.kaggle.com/code/muelsyse111/rogii-public-route-distance-atlas)
  - [Public Artifact Lineage Checklist](https://www.kaggle.com/code/muelsyse111/rogii-public-artifact-lineage-checklist)
- Independent full 773-well particle audit: 65% particle blend RMSE `12.7989`;
  retained as a local floor and not submitted.
- Best public LB: A04 residual transfer at `7.010`, improving the previous
  in-repository best `12.774` by `5.764` RMSE.
- Public rebuild and safe rebuild had byte-identical visible predictions but
  scored `9.571` and `7.130`; hidden execution lineage and fallback behavior
  must be treated as first-class experimental variables.
- Detailed evidence: [2026-07-18 results](docs/RESULTS_2026-07-18.md)
- Agent-ready research queue: [Agent playbook](research/AGENT_PLAYBOOK_2026-07-18.md)

## Current validated status (2026-07-17)

- Public notebook: [ROGII Honest 773 Well Baseline Audit](https://www.kaggle.com/code/muelsyse111/rogii-honest-773-well-baseline-audit)
- Full 773-well true-start CV: `15.9099`; public LB: `15.883`
- Daily submissions used: `2 / 5`; locally resolved weight variants are not submitted
- Particle blend public LB: `12.774` versus anchor `15.883`
- Full 773-well fixed blend on original / disjoint seed sets: `13.1119 / 13.3505`; OOF learned-weight RMSE `13.1544 / 13.3577`
- Private audited submission notebook: [ROGII Private Safe Particle Anchor Blend](https://www.kaggle.com/code/muelsyse111/rogii-private-safe-particle-anchor-blend)
- Detailed evidence: [Results log](docs/RESULTS_2026-07-17.md)
- English post ready for Discussion: [Discussion draft](docs/DISCUSSION_DRAFT_HONEST_BASELINE.md)

Public Code notebooks:

- [Honest 773-well baseline and submission audit](https://www.kaggle.com/code/muelsyse111/rogii-honest-773-well-baseline-audit)
- [Prefix backtest trap: more cuts can hurt](https://www.kaggle.com/code/muelsyse111/rogii-prefix-backtest-trap-more-cuts-can-hurt)
- [Particle filter lab: anchor blending](https://www.kaggle.com/code/muelsyse111/rogii-particle-filter-lab-anchor-blending)
- [True-start failure atlas and tail risk](https://www.kaggle.com/code/muelsyse111/rogii-true-start-failure-atlas-tail-risk)
- [Particle seed independence audit](https://www.kaggle.com/code/muelsyse111/rogii-particle-seed-independence-audit)
- [One coefficient, three RMSE optima](https://www.kaggle.com/code/muelsyse111/rogii-one-coefficient-three-rmse-optima)
- [Typewell GR motif ambiguity atlas](https://www.kaggle.com/code/muelsyse111/rogii-typewell-gr-motif-ambiguity-atlas)
- [Boundary geometry and score concentration](https://www.kaggle.com/code/muelsyse111/rogii-boundary-geometry-score-concentration)
- [Prefix-only GR calibration audit](https://www.kaggle.com/code/muelsyse111/rogii-prefix-only-gr-calibration-audit)

ROGII 前期调研与实验仓库。比赛目标是根据水平井轨迹、Gamma Ray 日志和对应 typewell，预测评估区间每一英尺的 `TVT`；官方指标是逐行 pooled RMSE，越低越好。

- Competition: [ROGII - Wellbore Geology Prediction](https://www.kaggle.com/competitions/rogii-wellbore-geology-prediction)
- Slug: `rogii-wellbore-geology-prediction`
- 资料快照：2026-07-17
- 官方开始：2026-05-05
- 参赛/组队截止：2026-07-29 23:59 UTC（北京时间 2026-07-30 07:59）
- 最终提交截止：2026-08-05 23:59 UTC（北京时间 2026-08-06 07:59）
- 主奖项：$50,000；另有两项 $2,500 Working Note Award，其 2026-07-06 截止日期已过

## 当前结论

这不是普通的逐行表格回归。正确的问题表述是：在最后已知 `TVT_input` 锚点之后，沿井轨迹估计一个平滑但可能漂移、分叉或局部非线性的地层位置状态；`GR` 与 typewell 的 `GR(TVT)` 提供带噪观测，邻井和 formation surface 提供空间先验。

首轮路线：

1. 以 well 为 group 做严格验证，禁止随机 row split。
2. 建立 anchor-hold、线性/低阶轨迹、Ridge/GBM residual 基线。
3. 增加 NCC/DTW、particle filter/beam、HMM smoother 等序列候选。
4. 用多 cut 前缀回测选择每井候选，保存不确定度和失败井画像。
5. 两条独立 pipeline 融合，并通过可见前缀守门任何 per-well override。
6. 最终 Notebook 必须无网络、9 小时内、确定性生成并审计 `submission.csv`。

## 文档

- [官方赛题与规则摘要](docs/COMPETITION_BRIEF.md)
- [数据清单与安全边界](docs/DATA_INVENTORY.md)
- [Code 区调研](research/CODE_REVIEW.md)
- [Discussion 区调研](research/DISCUSSION_REVIEW.md)
- [初始建模与验证策略](research/INITIAL_STRATEGY.md)
- [实验登记表](experiments/EXPERIMENT_LOG.csv)

## 本地开始方式

先在 Kaggle 页面由账号持有人亲自阅读并接受比赛规则。完成后再下载数据；原始数据只能放在被 `.gitignore` 排除的 `data/raw/`：

```powershell
kaggle competitions download -c rogii-wellbore-geology-prediction -p data/raw
```

本仓库不包含、也不应上传任何竞赛 CSV、PNG、PPTX、训练 artifact 或 Kaggle 凭证。

提交前可用纯标准库脚本检查文件结构、ID 顺序、重复项与非有限值：

```powershell
python scripts/verify_submission.py data/raw/sample_submission.csv submission.csv
python -m unittest discover -s tests -v
```

## 合规提醒

竞赛数据许可为 Competition use only。比赛期间不得在队伍外私下共享竞赛代码；若公开分享竞赛代码，应同时遵守官方规则中关于 Kaggle Competition Code/Discussion 和 OSI 许可证的要求。外部数据与模型必须公开、合理可获得，并保留来源和许可证证据。
