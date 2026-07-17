# 官方赛题与规则摘要

快照日期：2026-07-17。官方页面仍可能更新，提交前应重新检查 [Overview](https://www.kaggle.com/competitions/rogii-wellbore-geology-prediction/overview)、[Evaluation](https://www.kaggle.com/competitions/rogii-wellbore-geology-prediction/overview/evaluation)、[Data](https://www.kaggle.com/competitions/rogii-wellbore-geology-prediction/data) 和 [Rules](https://www.kaggle.com/competitions/rogii-wellbore-geology-prediction/rules)。

## 任务

全球每年约钻探 10,000 口水平井。参赛者需要预测水平井井筒沿线遇到的地质位置，帮助钻头保持在有利地层。每口井提供：

- 水平井轨迹与日志：`MD, X, Y, Z, GR, TVT_input`；
- 训练集额外提供六个 formation depth 列与完整 `TVT`；
- typewell 提供以 `TVT` 为轴的 `GR` 与 `Geology`；
- 评估区间的 `TVT_input` 为缺失值，需要预测目标 `tvt`。

## 指标与提交

官方指标为所有测试行上的 RMSE：

`RMSE = sqrt(mean((y - prediction)^2))`

这意味着：

- 不是每口井等权；评估行更多的井权重更高。
- 少数大漂移失败可以主导总分，应同时监控 worst-well 和尾部误差。
- 文件必须名为 `submission.csv`，列严格为 `id,tvt`。
- `id` 形式为 `{WELLNAME}_{row_index}`。

## Notebook-only 约束

- CPU Notebook 运行时间不超过 9 小时。
- GPU Notebook 运行时间不超过 9 小时。
- Internet 必须关闭。
- 允许免费且公开可用的外部数据/预训练模型。
- 最终文件必须为 `submission.csv`。

## 时间线

| 事件 | UTC | 北京时间（UTC+8） |
| --- | --- | --- |
| 开始 | 2026-05-05 | 2026-05-05/06 |
| Working Note Award 截止 | 2026-07-06 23:59 | 2026-07-07 07:59，已过 |
| Entry Deadline | 2026-07-29 23:59 | 2026-07-30 07:59 |
| Team Merger Deadline | 2026-07-29 23:59 | 2026-07-30 07:59 |
| Final Submission | 2026-08-05 23:59 | 2026-08-06 07:59 |

## 奖项与提交配额

- 第一名 $25,000；第二名 $13,000；第三名 $7,000；第四名 $5,000。
- 两项 Working Note Award 各 $2,500；公开页规定其提交日期为 2026-07-06。
- 每队最多 5 人。
- 每天最多 5 次提交。
- 最终最多选择 2 个提交。

## 规则中对仓库最重要的限制

1. 竞赛数据是 Competition use only，不得上传到本公开 GitHub 仓库，也不得提供给未接受规则的人。
2. 队伍外不得私下共享竞赛代码；公开分享应按官方规则在对应 Kaggle 区域公开，并使用不限制商业用途的 OSI-approved 许可证。
3. 外部数据/模型必须公开、合理可获得、成本合理，并能满足获奖复现和许可要求。
4. 获奖者可能需要提交训练/推理代码、完整环境说明和可复现方法文档，并授予 sponsor 非独占许可。
5. 规则接受是有法律效力的动作，本仓库自动化不会代替账号持有人接受。

## Working Note 评审维度

虽然截止日已过，其标准仍是很好的实验规范：

- 深入而非表面的多方法探索，包含负结果；
- 对数据和不同井行为的洞察；
- 物理合理性，而非只追 leaderboard；
- 每个关键想法的独立贡献；
- 不确定性估计和可靠性边界。
