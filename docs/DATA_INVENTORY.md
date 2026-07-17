# 数据清单与安全边界

Kaggle API 在 2026-07-17 返回：

| 类型 | 文件数 | 字节数 | 约合 |
| --- | ---: | ---: | ---: |
| CSV | 1,553 | 649,440,867 | 619 MiB |
| PNG | 773 | 646,882,273 | 617 MiB |
| PPTX | 1 | 28,789,544 | 27 MiB |
| 合计 | 2,327 | 1,325,218,684 | 1.23 GiB |

## 目录语义

训练集共有 773 口井，每井通常有：

- `{well}.png`
- `{well}__horizontal_well.csv`
- `{well}__typewell.csv`

公开可见的 `test/` 只有少量训练井示例；提交 rerun 时会替换为约 200 口隐藏测试井。根目录另有：

- `sample_submission.csv`
- `AI_wellbore_geology_prediction_task_en.pptx`

## Horizontal well 字段

| 字段 | 含义 | 训练/测试注意事项 |
| --- | --- | --- |
| `WELLNAME` | 井 ID | 分组与 CV 主键 |
| `MD` | 井筒测深 ft | 序列轴，不等于垂直深度 |
| `X,Y` | 平面坐标 ft | 邻井、区域与空间先验 |
| `Z` | 海平面基准的真垂深 ft | 与 TVT 共同定义结构量 `U=TVT+Z` |
| `GR` | Gamma Ray API | 水平井观测序列 |
| 六个 formation 列 | 地层深度面 | 训练提供；测试隐藏，不能作为直接测试特征 |
| `TVT` | 目标 | 仅训练完整提供 |
| `TVT_input` | 已知前缀目标 | 评估后缀为 NaN；最后已知点是强锚 |

## Typewell 字段

- `TVT`：typewell 的地层位置轴。
- `GR`：用于与水平井 GR 对齐的参考 signature。
- `Geology`：formation label。

## 数据风险

1. 公开 test 示例与 train 有 well ID 重合，可能产生近乎精确的公开分技巧；隐藏 test 不保证这种重合。
2. 任何 train-copy 重建必须先在 test 自身可见前缀上按 `MD` 插值验证，不能按 row index 盲拷贝。
3. 训练 formation 列高度相关，不能把六列误认为六个独立 3D surface。
4. 逐行随机切分会把同井相邻行泄漏到验证集。
5. 数据和 submission 只能保存在本地忽略目录；Git 只保存 schema、统计和不可逆摘要。

## 官方更新

- 2026-05-05 的 rerun backend 数据问题已经修复，官方称无需重新下载。
- 2026-06-11 官方从 private scoring 中排除一口 outlier well；该井仍留在隐藏 test，因此不减少 notebook runtime。
