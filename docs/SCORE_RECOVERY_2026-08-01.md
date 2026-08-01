# ROGII score-recovery checkpoint - 2026-08-01

## Objective

The measured account record is `6.455` from D29 ref `55074584`. The immediate
goal is a real score below `6.455`; `5.5` remains a target, not a forecast.
No score is inferred from a private Code run or from an unlabeled output file.

## Why this route

The D29 5% centred non-branch shape is the only recent mechanism that improved
the account record. The next experiment measures the response curve at
`10 / 15 / 20 / 25 / 30%`. Each notebook clones the full source of the scored
D29 route, recomputes every trajectory from the competition data and mounted
model packages, dynamically excludes the PF-selected branch, and changes only
the centred non-branch weight and proportional clip.

These are not static blends. Their metadata has no `kernel_sources`, and they
do not read any previous `submission.csv`.

## Private Code validation

| Weight | Private Code | Version to audit | State |
|---:|---|---:|---|
| 10% | `muelsyse111/rogii-d32-full-nonbranch10-r1` | 1 | complete and audited |
| 15% | `muelsyse111/rogii-d32-full-nonbranch15-gpu-r2` | 1 | complete and audited |
| 20% | `muelsyse111/rogii-d32-full-nonbranch20-gpu-r2` | 1 | complete and audited |
| 25% | `muelsyse111/rogii-d33-full-nonbranch25-gpu-r1` | 2 | complete and audited |
| 30% | `muelsyse111/rogii-d33-full-nonbranch30-gpu-r1` | 1 | complete and output-audited; quarantined by new gate |

The 10/15/20/25/30% outputs each have exactly 14,151 sample-ordered unique IDs,
finite predictions, report-matching file and prediction SHA-256 values, and no
fatal log markers. All ten pairwise RMS distances are positive and range from
`0.091667` to `0.333531 ft`, so none is a duplicate. The 30% file SHA-256 is
`9995106ab5254d580ec1fa0fc9fb993a86bd0ef5ada888e532faf3953db708f0` and
its prediction SHA-256 is
`f21b2d62ba63d501508794aa780076f752f41179c3b4cfa258f6e489dc8d6f4c`.

The retired 30% slug failed before modelling because Kaggle mounted no
competition files; its explicit preflight reported `train=0, test=0,
sample=False`. It is not an algorithm failure and is not eligible for
submission. The fresh slug completed and proved the model route, but the new
submission gate found that the inherited final audit still contains a literal
public row count. Therefore all five outputs are research evidence only. None
is eligible until the same candidate is rebuilt and completed as a fresh
dynamic-contract private version.

## Competition gate

The 2026-08-01 budget is exhausted at `5 / 5`; no recovery notebook may be
competition-submitted today. On the next Kaggle date, a downloaded output is
still insufficient: only a fresh private version with a passing
`preflight_competition_submission.py` report is eligible. The submission
wrapper independently rechecks the exact remote source/output hashes, blocks
on unresolved refs, stops the date after any error, enforces the `5 / 5`
budget and 30-minute spacing, and requires explicit `--execute`. `COMPLETE`
alone is never success.
