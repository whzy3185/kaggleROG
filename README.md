# Kaggle ROGII Wellbore Geology Prediction

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
