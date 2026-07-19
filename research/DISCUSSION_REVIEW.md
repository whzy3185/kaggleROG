# Kaggle Discussion 区调研

采集时间：2026-07-17；增量复查：2026-07-19。官方/host 信息与参赛者假设分开记录；参赛者公布的 CV、LB、百分比和“证明失败”等说法在本仓库重现实验前都视为线索。

## 官方更新

| 主题 | 结论 |
| --- | --- |
| [Dataset issue - Fixed](https://www.kaggle.com/competitions/rogii-wellbore-geology-prediction/discussion/697400) | 2026-05-05 rerun backend 问题已修复；官方称无需重下文件。 |
| [Private Test Update and Rescore](https://www.kaggle.com/competitions/rogii-wellbore-geology-prediction/discussion/707695) | 一口 private outlier well 被移出计分，但仍存在于 test，运行时间不变。 |
| [Working Note Awards](https://www.kaggle.com/competitions/rogii-wellbore-geology-prediction/discussion/709495) | 强调不同方法、负结果、物理解释、组件贡献和不确定性；截止已过。 |

## 地质与数据结构

### Host 给出的解释技巧

[How Geologists Interpret Wells](https://www.kaggle.com/competitions/rogii-wellbore-geology-prediction/discussion/698825) 的 host 评论强调：

- 邻井的 formation dip 应相似；
- 水平井自身 GR 可能比 typewell GR 分辨率更高；
- 当井在 TVT 域向负方向移动时，prediction start 前的 lateral GR 可成为比 typewell 更好的相关参考。

### Formation 列不是六个独立 surface

[Formation Columns Are Derived from Typewell](https://www.kaggle.com/competitions/rogii-wellbore-geology-prediction/discussion/708167) 报告：井内各 formation 间距几乎恒定，754/773 口井的 typewell 与 horizontal-well 厚度在 1 ft 内一致；七口井的 ANCC 顶部疑似截断。需要本地复现，但它提示六列的有效自由度接近一条基面加固定 offset。

### Duplicate typewell

[Duplicate type wells](https://www.kaggle.com/competitions/rogii-wellbore-geology-prediction/discussion/698449) 列出多组完全相同的 typewell。它们可能代表共享区域 template，因此 typewell hash/group 应成为分组、特征和误差分析维度。

## 方法讨论

### 序列对齐，而非逐行回归

- [DWT / time warping](https://www.kaggle.com/competitions/rogii-wellbore-geology-prediction/discussion/697431)：把 lateral `MD-GR` 拉伸/折叠到 typewell `TVT-GR`。
- [MTP with deep CNN](https://www.kaggle.com/competitions/rogii-wellbore-geology-prediction/discussion/699853)：热力图 + CNN/MDN 产生多轨迹假设，再在关键点之间选择路径。
- [Why pure tabular hits a wall](https://www.kaggle.com/competitions/rogii-wellbore-geology-prediction/discussion/699289)：建议 particle/beam 和空间邻井先验。
- [Literature review](https://www.kaggle.com/competitions/rogii-wellbore-geology-prediction/discussion/701041)：比较 cross-correlation、NCC、DTW/Soft-DTW、状态空间和深度时序方法。

### 当前社区诊断线索

[Where does the top-team signal come from](https://www.kaggle.com/competitions/rogii-wellbore-geology-prediction/discussion/726465) 报告了一个竞争者的诊断：近邻井可能达到更低误差，远邻井主导失败；简单 GR fine-structure 匹配和远距离 dip transfer 在其管线中无效。该帖给出三个值得验证的问题：

1. 是否应迁移邻井完整 TVT profile，而非只拟合结构面？
2. 多尺度/自日志参考/约束 warp 是否能救回 GR 对齐？
3. 井是否存在两个或多个需要不同模型的自然 group？

2026-07-19 复查评论区后增加四条线索：

- 有参赛者建议近邻 `<150 ft` 时迁移完整 TVT 曲线形状，而不是只迁移结构面；
- 方位相反的井应拆分处理，避免把正反钻进方向混在一个模型；
- 另有参赛者称不使用邻井也能把单模型 pooled CV 做到 `<5 ft`，因此“近邻复制是唯一信号”不能当成定论；
- 需要严格区分随机 grouped-by-well CV 与更困难的 field-grouped CV。

本地 leave-one-well-out 复现只取得有限收益：750 ft 内最多五口同向邻井、30% TVT 形状迁移，把 pooled RMSE 从约 `15.9099` 降到 `15.6153`。这说明简单的归一化 MD 曲线复制有信号，但远不足以解释 sub-7，更不能直接提交。

[Six independently-trained architectures, same blind spot](https://www.kaggle.com/competitions/rogii-wellbore-geology-prediction/discussion/726834) 报告六种不同架构在约 2,600 ft 区间紧密收敛到同一错误分支，真值相对模型单调漂移到约 `-90 ft`。这支持把周期分支歧义作为结构性错误，而不是靠普通 ensemble 方差解决。

[Is the sub-6 regime end-to-end learned, or engineered alignment?](https://www.kaggle.com/competitions/rogii-wellbore-geology-prediction/discussion/727149) 进一步提出三个关键审计问题：sub-6 是端到端学习还是显式 warp/PF/HMM 坐标对齐；formation top 是否提供绝对层位锚；随机井分组的 5.x 与 field holdout 的约 10 是否来自场内结构泄漏。当前帖子尚无回答，保留为验证设计约束。

[Worst performing well](https://www.kaggle.com/competitions/rogii-wellbore-geology-prediction/discussion/723815) 展示序列模型早期选错分支后持续漂移的典型失败。评估不能只看 pooled score，必须保存每井曲线和最坏井报告。

[Beginner's map](https://www.kaggle.com/competitions/rogii-wellbore-geology-prediction/discussion/726751) 报告 anchor-hold OOF 约 16.1，而简单 row-wise LightGBM 约 17.463。数值尚需复现，但负结果支持“先击败物理锚点，再相信表格模型”。

## 直接转化为实验的假设

1. `U=TVT+Z` 的一阶/二阶动力学优于直接预测 TVT。
2. GR 的 affine calibration + 多尺度 NCC/DTW 优于原始幅值匹配。
3. 预测 start 前 lateral GR 可作为自参考 template。
4. typewell hash/group 与近邻距离决定 tracker 可靠性。
5. posterior std、候选 disagreement 和 prefix backtest error 能预测未来误差，可用于 per-well gating。
6. 多 cut prefix validation 比单一 GroupKFold 更接近真实后缀外推。
