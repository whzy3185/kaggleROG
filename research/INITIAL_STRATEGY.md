# 初始建模与验证策略

## 1. 问题表述

对每口井 `w`，已知前缀 `H_w` 的 `TVT_input` 和完整轨迹/GR；需要预测后缀 `Q_w`。定义：

- `anchor_tvt`：最后已知 TVT；
- `md_since`：距 prediction start 的 MD；
- `U = TVT + Z`：地层结构 offset；
- `r = dU/dMD`：局部 dip-rate。

核心是估计 `U(md)` 或 `(U,r)` 的平滑状态路径，GR/typewell 是非线性观测，邻井是空间先验。

## 2. 数据和验证协议

### 主验证：GroupKFold by well

- 任何一口井的行只能出现在一个 fold。
- 主指标复现官方 pooled RMSE。
- 同时报 macro per-well RMSE、p90/p95/worst、按 eval length 加权和未加权分数。

### 真实任务模拟：multi-cut prefix backtest

在训练井完整 TVT 上人为选择多个 prediction start：

1. 只向模型暴露 cut 前的 `TVT_input`。
2. cut 后作为隐藏后缀。
3. cut 比例与真实测试 start 分布匹配。
4. 同井不同 cut 不能跨训练/验证泄漏。

用途：选择 PF/HMM/DTW 参数、blend weight、projection degree、gating threshold，而不是用 public LB 调这些常数。

### 分层报告

至少按以下维度切片：

- 最近邻井距离；
- typewell hash/group；
- eval length 与 `Z` span；
- heel GR/typewell 对齐质量；
- formation/contact 可用性；
- tracker disagreement 和 posterior uncertainty；
- 每井 anchor-hold、linear、quadratic oracle gap（仅诊断）。

## 3. 基线阶梯

### B0 Anchor hold

隐藏后缀全部使用最后已知 TVT。它是任何复杂模型必须击败的安全基线。

### B1 Geometry trend

- `TVT = anchor + slope * md_since`
- 在 prefix 上估计 `U=TVT+Z` 的线性/二次趋势，再还原 `TVT=U-Z`
- slope shrink 到区域/typewell group prior，避免 toe 发散

### B2 Residual Ridge/GBM

目标：`TVT - anchor` 或 `U - U_anchor`。特征包括：

- 轨迹：MD、md_since、dZ、slope、curvature、X/Y、方向；
- GR：rolling stats、差分、多尺度平滑、prefix normalization；
- typewell：插值 GR、NCC peak/lag、候选对齐成本；
- 空间：邻井距离、plane/KNN surface、typewell group；
- tracker：PF/DTW/HMM path 与 uncertainty。

GBM 是融合器和 residual learner，不作为独立逐行真值机。

## 4. 序列候选

### S1 NCC / constrained DTW

- 先在 prefix 拟合 `GR_h ≈ a*GR_tw(TVT)+b`。
- 多尺度平滑后计算 NCC anchor。
- 使用 monotonic、slope-bound、open-begin/end DTW。
- 增加 lateral-prefix self-reference 分支。

### S2 Particle filter + beam

状态 `(TVT, dip-rate)`；转移使用 `dTVT = r*dMD - dZ + noise`，观测由校准 GR 与 typewell GR 的残差给出。保留多个 likelihood scale 和 beam，避免单分支早锁死。

### S3 Exact/banded HMM smoother

在离散 `(TVT,dip-rate)` 网格上 forward-backward，输出 posterior mean/std。与 PF 做 error-correlation 和 blend 实验，不预设 HMM 一定更强。

### S4 Neighbor profile transfer

对近邻、同 typewell group 的训练井，把完整 `U(md)` 或 residual profile 做 MD 归一化迁移；比较 surface-only、profile transfer 和不使用邻井三种方案。

## 5. 融合与守门

每井保存候选：anchor、geometry、GBM、PF、beam、DTW、HMM、neighbor transfer。融合器只能使用当前井可见前缀可计算的特征：

- prefix backtest RMSE；
- GR alignment confidence；
- candidate disagreement；
- HMM posterior std；
- nearest-neighbor distance；
- eval length / z span。

任何 overlap/contact override 必须：

1. 按 MD 插值；
2. 在当前 test well 的已知 prefix 上至少 50 个点验证；
3. prefix RMSE 达到严格阈值；
4. 失败时原样回退到 base blend。

## 6. 首轮实验顺序

| 顺序 | 实验 | 进入下一步的门槛 |
| ---: | --- | --- |
| 1 | 复现 anchor、prefix-U line、row-wise Ridge/GBM | 指标与每井报告稳定 |
| 2 | 建 multi-cut harness | 无井泄漏，cut 分布可解释 |
| 3 | NCC/DTW 对齐 | 在至少一个可靠井群显著优于 anchor |
| 4 | PF/beam | pooled 与 worst-tail 同时改善 |
| 5 | HMM smoother | 与 PF 误差去相关或 uncertainty 有效 |
| 6 | 空间 surface/profile | 只在距离/群组门控下采用 |
| 7 | GBM/Ridge 融合 | OOF 与多 cut 同向增益 |
| 8 | Kaggle notebook hardening | 无网、9h 内、确定性、可审计 |

## 7. 风险登记

- Public/private gap：公开示例井重合技巧不迁移隐藏 test。
- Artifact lineage：公开高分 notebook 大量 fork，方法差异可能小于标题差异。
- LB overfit：5 次/天不应用于常数网格搜索。
- Tail risk：一个错误分支井可主导 RMSE。
- Runtime：PF/beam/HMM 的井数约 200，必须向量化/Numba/剪枝并缓存 typewell 插值。
- Leakage：同井 rows、duplicate typewell group、空间近邻都可能跨 fold 泄漏。
- Rule drift：提交前重新抓官方页面和置顶 Discussion。
