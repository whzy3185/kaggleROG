# Discussion draft: Five submissions as an auditable agent experiment

I used today's five-submission budget as a controlled reproduction experiment
rather than a search over nearby blend weights.

Five recent public routes were rerun under new private notebook versions:

| Route | My public RMSE | Submission |
|---|---:|---:|
| Public rebuild | SCORE_1 | 54808956 |
| Dual-track calibrated | SCORE_2 | 54808958 |
| A04 residual transfer | SCORE_3 | REF_3 |
| G040/S12 gate | SCORE_4 | REF_4 |
| Safe rebuild | SCORE_5 | REF_5 |

Sources and attribution:

- [LB7295 Public Rebuild](https://www.kaggle.com/code/bernubritz/rogii-lb7295-public-rebuild) by bernubritz
- [Dual-Track Prefix-Calibrated Geosteering](https://www.kaggle.com/code/pilkwang/rogii-dual-track-prefix-calibrated-geosteering) by pilkwang
- [Another Approach](https://www.kaggle.com/code/yusuketogashi/rogii-another-approach) by yusuketogashi
- [Public 7.015 Anchor G040 S12 Visuals](https://www.kaggle.com/code/prvsiyan/rogii-public-7-015-anchor-g040-s12-visuals) by prvsiyan
- [7.016 Safe Rebuild](https://www.kaggle.com/code/kersaoyagi/rogii-7-016-safe-rebuild) by kersaoyagi

For each version I required:

1. a completed private Kaggle run with internet disabled;
2. exactly 14,151 output rows;
3. exact sample ID order;
4. only finite TVT values;
5. a saved SHA-256 hash and no fatal traceback;
6. one immutable version mapped to one submission reference.

## A useful surprise: correlation hides the real diversity

All five strong public outputs have correlations that round to 1.0 because TVT
has a large common absolute level. RMS prediction distance is more useful:

- public rebuild vs dual track: 0.01098 ft;
- public rebuild vs G040/S12: 0.22062 ft;
- public rebuild vs A04: 0.39773 ft;
- public rebuild vs safe rebuild: 0.00000 ft;
- my earlier independent particle route vs public rebuild: 9.41209 ft.

The public rebuild and safe rebuild are byte-identical on visible rows. Their
different notebooks are therefore a lineage experiment, not a visible
prediction-diversity experiment.

Among the three visible test wells, cross-candidate disagreement is largest on
`00bbac68`, followed by `00e12e8b` and `000d7d20`. I treat this only as an
uncertainty/routing diagnostic, never as a hidden-label accuracy estimate.

## What I would ask an agent to do next

- Maintain several branch hypotheses and report posterior entropy plus the gap
  between the best and second-best branch.
- Cross-fit every correction gate on masked suffixes grouped by well.
- Shrink toward a conservative fallback when learned, physical, and GR-aligned
  tracks disagree.
- Evaluate worst-decile RMSE and maximum regret, not only pooled RMSE.
- Break validation down by suffix length, Z span, GR noise, and typewell motif
  ambiguity.
- Hash input artifacts before execution and predictions after execution.
- Enforce the daily budget in a persistent ledger that rejects duplicate hashes
  and refuses a sixth submission.

I also ran an independent full 773-well true-start audit of the in-repository
particle model. With 300 particles, 16 seeds, and likelihood temperature 20,
the 65% particle blend scored 12.7989 pooled CV versus 15.9099 for anchor hold.
It was not submitted because the five audited public routes were substantially
stronger.

The accompanying public Code notebook contains the exact score ledger,
candidate-distance table, and reusable state machine:

CODE_NOTEBOOK_URL

