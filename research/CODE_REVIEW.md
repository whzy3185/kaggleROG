# Kaggle Code 区调研

采集时间：2026-07-17；排序：vote count。票数为快照，只用于确定阅读优先级，不能代表私榜有效性。

## 高票 Code 快照

| Notebook | 票数 | 公开信号 |
| --- | ---: | --- |
| [DWT-based](https://www.kaggle.com/code/nihilisticneuralnet/9-251-rogii-wellbore-geology-prediction-dwt-based) | 675 | DWT 特征、LightGBM/CatBoost、hill climbing 和后处理的早期主线。 |
| [ROGII LB7295 Public Rebuild](https://www.kaggle.com/code/bernubritz/rogii-lb7295-public-rebuild) | 553 | 高 public-LB artifact 重建；应审计来源和私榜迁移性。 |
| [Dual Pipeline + Self-Verifying](https://www.kaggle.com/code/lightningv08/rogii-dual-pipeline-self-verifying) | 289 | PF/beam/GBM/Ridge 双流水线、robust projection、可见前缀守门 override。 |
| [Wellbore Geology Prediction - Ridge](https://www.kaggle.com/code/ravaghi/wellbore-geology-prediction-ridge) | 279 | LightGBM/CatBoost 基模型与 Ridge meta，融合物理 tracker。 |
| [Dual-Track Prefix-Calibrated Geosteering](https://www.kaggle.com/code/pilkwang/rogii-dual-track-prefix-calibrated-geosteering) | 266 | `U=TVT+Z` 投影、双轨融合、heel GR 校准、prefix backtest。 |
| [Dual Pipeline Blend](https://www.kaggle.com/code/pixiux/rogii-dual-pipeline-blend) | 233 | 两个公开 pipeline 的加权融合。 |
| [Public Score 7.159](https://www.kaggle.com/code/degnonguidi/public-score-rogii-lb-7-159) | 224 | 公开高分 artifact 路线。 |
| [7.091 Public](https://www.kaggle.com/code/AmgedAlfaqih/7-091-public) | 221 | 公开高分迭代，需做 lineage 与真实方法增量审计。 |
| [Target-Free TVT Geosteering](https://www.kaggle.com/code/pilkwang/rogii-target-free-tvt-geosteering) | 219 | 不依赖隐藏 target 的物理/跟踪路线。 |
| [XGB Starter - CV 15](https://www.kaggle.com/code/cdeotte/xgb-starter-cv-15) | 205 | 简单、可复现的表格基线和下限。 |
| [Hill Climbing](https://www.kaggle.com/code/ravaghi/wellbore-geology-prediction-hill-climbing) | 198 | 对公开候选做权重/组合搜索；私榜过拟合风险较高。 |
| [Geology-Aware Ensembling](https://www.kaggle.com/code/romanrozen/rogii-geology-aware-ensembling-lb-7-129) | 127 | 按地质/井型选择或融合候选。 |
| [Exact HMM Smoother](https://www.kaggle.com/code/amerhu/rogii-wellbore-geology-exact-hmm-smoother) | 60 | 二阶 HMM forward-backward、posterior mean/std、多 cut 验证。 |

## 公开代码的共识架构

### 1. 状态量应是结构残差

多份代码使用 `U = TVT + Z` 或相对最后已知 `TVT` 的残差。`U` 往往比原始 TVT 平滑，更接近缓慢变化的 formation dip；直接拟合绝对 TVT 容易把区域 datum 与井内运动混在一起。

### 2. 物理 tracker + 学习残差

常见组合是：

- PF/beam/HMM 根据 `GR_h(md)` 与 `GR_tw(tvt)` 的匹配追踪多个 TVT 路径；
- 空间 KNN/formation plane 提供邻井结构先验；
- LightGBM/CatBoost 学习 tracker 残差和候选选择；
- Ridge 或固定权重融合多个 booster 和物理候选；
- per-well 平滑或 robust polynomial projection 消除抖动和错误分支。

### 3. 可见前缀是每井验证集

高质量公开 pipeline 不会盲目使用 train/test overlap 或某个 tracker。它们在当前 test well 的非缺失 `TVT_input` 前缀上：

- 校准水平井 GR 与 typewell GR 的 gain/offset；
- 回测候选 tracker；
- 检查 train-copy formation-contact 重建；
- 只有达到阈值才把修正延伸到隐藏后缀。

### 4. HMM smoother 是有价值的去随机候选

公开 HMM notebook 把 state 设为 `(TVT, dip-rate)`，使用二阶动力学和整条 GR 序列做 forward-backward，输出 posterior mean 与 posterior std。它的价值不在于保证单模型最强，而在于：

- 条件化未来观测，区别于 forward-only PF；
- 保留多峰不确定性；
- 给出可用于 gating 的逐行置信度；
- 与 PF 的误差可能去相关，适合融合。

### 5. Public artifact lineage 是主要风险

大量高票 notebook 是相同公开 artifact/pipeline 的 fork、重新打包或常数微调。高票和高 public-LB 并不等于方法独立。每个候选必须记录：

- 直接 parent 和 notebook version；
- 训练 artifact 来源与许可证；
- 与 parent 的真实代码差异；
- grouped CV、多 cut CV 和 private-safe 假设；
- 是否利用公开 test/train overlap。

## 对本仓库的采用策略

只提炼公开思想与可复现代码结构，不直接提交未知 lineage 的 `submission.csv`、pickle booster 或 train/test overlap artifact。首版必须从本地数据重建 baseline，并用 well-group 和 prefix-cut 验证决定是否采用每个公开组件。
