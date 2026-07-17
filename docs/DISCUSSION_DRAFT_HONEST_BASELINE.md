# Proposed Discussion title

**A reproducible 773-well floor: true-start CV 15.9099 vs LB 15.883**

# Proposed Discussion body

I published a small CPU-only notebook intended as a trustworthy floor and submission-integrity reference, not as a leaderboard claim:

**Notebook:** [ROGII Honest 773 Well Baseline Audit](https://www.kaggle.com/code/muelsyse111/rogii-honest-773-well-baseline-audit)

The predictor repeats the final visible `TVT_input` over each missing suffix. It uses no public submission artifact, train/test filename overlap, hidden target reconstruction, external model, or leaderboard-tuned constant.

## Why I think this floor is useful

The training files already provide a deployment-shaped boundary: `TVT_input` is present on one contiguous prefix and missing on the suffix, while `TVT` provides local truth. I replayed that exact boundary for all 773 training wells and pooled squared error over every evaluation row before taking the square root, matching the official metric.

Results:

| Metric | Value |
| --- | ---: |
| Wells | 773 |
| Evaluation rows | 3,783,989 |
| Local pooled RMSE | 15.9099 |
| Public LB RMSE | 15.883 |
| Absolute local/LB gap | 0.0269 |
| Macro well RMSE | 12.8125 |
| Median well RMSE | 10.6651 |
| p90 / p95 well RMSE | 22.9725 / 29.0108 |
| Worst well RMSE | 70.6394 |

The close local/LB agreement suggests that true-start replay is a useful first filter before spending submissions. The tail statistics also show why a method can look reasonable on average while still failing badly on a few branches.

## Submission integrity

The notebook builds predictions by official ID (`well_id` plus original row index) and then joins them back to `sample_submission.csv`. Before saving, it asserts:

- exact `id,tvt` columns;
- exact sample ID set and order;
- unique IDs and exact row count;
- finite predictions only.

This is deliberately more defensive than concatenating files in filesystem order.

## Three negative results worth sharing

1. A standalone fixed or linearly extrapolated `U = TVT + Z` surface was much worse than the anchor. The best tested U-tail candidate had pooled RMSE 42.25; U-hold was 107.49. U may still be the right dynamic state inside PF/HMM, but it is not sufficient by itself here.
2. A compact first-order TVT HMM won only one of five smoke-test wells and scored 26.50 versus the anchor's 10.31. I stopped it before leaderboard use.
3. Naive early-prefix multi-cut calibration can be optimistic. Cuts at 40/60/80% of the visible prefix strongly preferred larger trend coefficients, but extending them through the real suffix worsened pooled RMSE to 17.04. Synthetic cuts need to match the actual boundary regime; "more cuts" is not automatically "more honest."

## Particle follow-up

An independently implemented multi-seed particle tracker using the structural state `U`, typewell GR likelihood, and visible-prefix calibration has now been tested at the true start on all 773 wells. A fixed 62.5% particle blend improved pooled RMSE from 15.9099 to 13.1119, and five-fold out-of-well blend estimation scored 13.1544.

I also found and corrected an experimental bookkeeping trap: advancing an eight-seed ensemble base by one changes only one seed, so it is not an independent replication. A genuinely disjoint seed set scored 13.3505 for the same fixed blend, with OOF RMSE 13.3577. Its p95 improved from the anchor's 29.01 to 25.44, although the worst well remained 70.54. This is a useful reminder to report the actual seed sets, not only different base labels.

The fixed model scored 12.774 on the public leaderboard versus 15.883 for the anchor. I am not using submissions to search nearby blend weights: the original/disjoint joint optimum is 0.611, and fixed 0.625 differs by only 0.0015 RMSE on their combined local evidence. The remaining problem is stochastic wrong-branch tail risk, not another decimal place in the global blend.

I would be interested in comparisons that report true-start pooled RMSE plus p95/worst-well error, especially for PF, beam, DTW, and exact HMM variants. Please also state whether any per-well gate uses only the visible prefix.
