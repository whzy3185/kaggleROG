# Local Score Simulation Audit - 2026-08-01

## Outcome

The repository now has a runnable local decision aid for ROGII candidates. It
uses row-weighted RMSE on withheld target suffixes, paired bootstrap resampling
of complete wells, and a stricter spatial-field donor audit. It is useful for
rejecting weak ideas and estimating sampling uncertainty. It is not a hidden
leaderboard emulator and it does not assign a meaningful score to a static
`submission.csv` that has no labels.

No competition submission was made during this audit.

## Reproduce

```powershell
E:\anaconda\python.exe scripts\run_neighbor_profile_cv.py `
  --exclude-target-field `
  --thresholds 300 600 1200 2400 5000 `
  --blends 0.1 0.25 0.5 `
  --max-donors 5 `
  --prefilter 40 `
  --output-dir artifacts\neighbor_profile_field_holdout_cv_20260801

E:\anaconda\python.exe scripts\simulate_local_scores.py --iterations 10000
E:\anaconda\python.exe -m pytest -q
```

The simulator writes:

- `candidate_score_simulation.csv`: deterministic RMSE, tail metrics, and
  52-well/148-well paired-bootstrap intervals;
- `well_metadata_and_fields.csv`: the 773 target wells and deterministic
  five-way spatial diagnostic blocks;
- `historical_cv_lb_calibration.csv`: two honest same-pipeline CV/LB checks;
- `prior_submission_package_audit.csv`: immutable output-contract checks for
  the five measured D29 packages;
- `audit.json`: machine-readable limitations and selected diagnostics.

## Historical calibration

| Pipeline | Full local CV | Public LB | LB minus CV |
|---|---:|---:|---:|
| True-start anchor, 773 wells | 15.9099 | 15.883 | -0.0269 |
| Fixed 62.5% particle blend, 773 wells | 13.1119 | 12.774 | -0.3379 |

The sign and ordering agree for these two same-pipeline checks, so the replay
has real decision value. The offsets differ by about 0.31 RMSE, however, which
is direct evidence against fitting one global CV-to-leaderboard correction.

## Candidate replay findings

| Family | Local result | Decision |
|---|---|---|
| U extrapolation | Best tested variant 42.2488 versus anchor 15.9099 | Reject |
| First-order HMM | 26.4980 versus 10.3099 on five wells | Reject; smoke sample also too small |
| Independent particle blend | Blend 0.50 is 12.7188 versus 15.2106; private-148 delta 90% interval [-3.5528, -1.3447] | Promising, but the saved artifact has only 30 wells |
| Blacklions GBDT correction | 10.4156 versus OOF control 10.3723; improvement probability 0.265 | Do not promote |
| Neighbor transfer, leave one well out | 15.6268 versus 15.9099; private-148 delta interval [-0.5876, 0.0069] | Inconclusive and spatially unsafe |
| Neighbor transfer, leave target field out | No donor coverage through 1,200 ft; 7.1% at 5,000 ft and RMSE worsens to 15.9166 at blend 0.10 | Reject as a general hidden-field route |

### Full particle sample-size check

The saved 30-well `400 particles / 16 seeds / temperature 5` run reported
12.7188 for blend 0.50. A fresh run of the identical configuration on all 773
wells finished in 794 seconds with:

| Candidate | 30 wells | 773 wells |
|---|---:|---:|
| Anchor | 15.2106 | 15.9099 |
| Blend 0.50 | 12.7188 | 13.3350 |
| Blend 0.625 | not previously materialized | **13.2770** |
| Blend 0.65 | not previously materialized | 13.2966 |
| Particle only | 14.8302 | 14.5991 |

The 30-well point estimate was optimistic by 0.6162 RMSE for blend 0.50, but
the simulator's 30-well-derived private-148 interval, approximately
[11.4580, 13.9862], contained the full-run value. This is a useful positive
check on the uncertainty calculation and a negative check on using a small
sample point estimate by itself.

### Exact historical particle-package replay

The submitted configuration was then rerun independently on all 773 wells
with its actual settings: 300 particles, eight seeds, likelihood temperature
20, and seed base 20260717. It completed in 254 seconds:

| Candidate | Fresh RMSE |
|---|---:|
| Anchor | 15.909853 |
| Blend 0.50 | 13.235575 |
| Blend 0.625 | **13.111855** |
| Blend 0.65 | 13.116693 |
| Blend 0.75 | 13.234479 |
| Particle only | 14.180411 |

The fresh blend-0.625 value differs from the historical 13.1119 record by
only -0.000045 RMSE. Its paired private-148 delta interval versus anchor is
[-4.2925, -1.3407], with estimated improvement probability 0.9995. This is a
successful same-code local reproduction of the package that later scored
12.774 on the public leaderboard.

The newer 400-particle/16-seed/temperature-5 run is 0.1652 RMSE worse at the
same blend. More particles and seeds do not compensate for a less suitable
likelihood temperature, and there is no local reason to submit that variant.

The field-holdout detail contains 11,595 candidate/well rows for all 773 wells.
There are zero cases where a moved target's nearest donor belongs to the same
field, confirming that the strict run enforced its intended exclusion.

## Previous submission-package test

The five D29 `submission.csv` files were reread from disk. Every file still
has exactly 14,151 sample-ordered unique IDs, finite predictions, no recorded
fatal marker, and a SHA-256 matching the immutable audit. Their measured public
scores remain 6.541, 6.517, 6.560, 6.455, and 6.530.

This verifies that they are technically usable submission packages. It does
not make them locally scoreable: the CSVs contain predictions for unlabeled
test rows. The Pearson correlation between their RMS output distance from the
D25 parent and public score is only 0.1285 with five observations. Output
distance is therefore a diversity/sanity diagnostic, not a score proxy.

## GeoAnchor learned-core connection

The public artifact bundle's five serialized trainers were downloaded locally
and their stored row-level OOF vectors were connected to the simulator. The
local suffix index contains 3,783,989 rows from all 773 wells. Every trainer's
recomputed RMSE matches its stored `overall_score` within `3.7e-9`, which is a
strong row-order and target-alignment check.

| Candidate | Full 773-well OOF RMSE |
|---|---:|
| LightGBM 1 | 10.7668 |
| LightGBM 2 | 10.4852 |
| LightGBM 3 | 10.4733 |
| CatBoost 1 | 10.5750 |
| CatBoost 2 | 10.5550 |
| Exact grouped positive Ridge | 10.4173 |
| Ridge plus 85-ft warm-up, without saved PF | **10.4153** |

For the warm-up candidate, complete-well bootstrap resampling gives a 52-well
median of 9.8321 with a 90% interval of [7.9745, 13.7049], and a 148-well
median of 10.2216 with a 90% interval of [8.7787, 12.3233]. These distributions
describe sampling variation of the learned OOF core. They are not estimates of
the current hidden leaderboard score.

The connection deliberately excludes the unavailable saved 9% PF feature,
selector/projection/visible-prefix transactions, guarded same-well contact
override, and the R2000 single-test-well correction. In particular, R2000 was
derived algebraically from public leaderboard responses for one named test
well and has no train-fold analogue. Therefore the reported public 5.x result
cannot honestly be converted into a 5.x local OOF estimate. The measurable
core is around 10.4; the remaining public gain is concentrated in downstream
rule/anchor transactions that still need deployment-parity, target-safe OOF.

The guarded-contact layer was then audited separately. If EGFDU is used from
each training horizontal file and its offset is fitted only on `TVT_input`, it
scores 0.006994 on all 3,783,989 held-out suffix rows. That number is **not a
valid CV result**: EGFDU and the other formation columns exist in the train
horizontal files but are absent from every test horizontal file.

The actual 6.568 anchor instead reads the overlapping full training well,
including its full `TVT` and EGFDU trajectory, then interpolates that trajectory
onto the three test-well MD grids. The local audit reconstructed all 14,151
anchor predictions with RMS difference `1.57e-12` and maximum absolute
difference `3.64e-12`. This exactly connects the scored anchor to the source
transaction while proving why the tempting near-zero train score is not a
leaderboard forecast. The measured 6.568 public score is the best calibration
for this transductive contact route; the remaining test-suffix residual is not
observable in ordinary training OOF.

Reproduce the connection with:

```powershell
E:\anaconda\python.exe scripts\replay_geoanchor_learned_oof.py
E:\anaconda\python.exe scripts\audit_geoanchor_contact_proxy.py
E:\anaconda\python.exe scripts\simulate_local_scores.py --iterations 10000
```

## Promotion gate for future candidates

A new route should be considered locally supported only when all of the
following hold:

1. predictions are genuinely out of fold for the complete modelling pipeline,
   including learned selectors and post-processing;
2. the validation target suffix is never used to construct features, donors,
   contacts, selectors, or pretrained models;
3. row-weighted RMSE improves on the same-pipeline control and the paired
   private-148 bootstrap upper delta bound is below zero;
4. spatial methods also survive a target-field holdout with useful coverage;
5. the expected gain is larger than known rerun and public-slice noise;
6. only after those checks does the final 14,151-row output contract matter.

The current public high-score reproductions and D29/D32 static outputs fail
the first requirement unless their full learned stack is retrained by fold.
They can be reproduced and structurally audited locally, but their leaderboard
score cannot be honestly simulated from the visible test files.

## Notebook preflight

`audit_full_stack_cv_notebook.py` now fails closed on the stored D29 notebook.
It finds a legitimate grouped Ridge OOF layer, but also finds four blockers:

1. the stored full-stack ablation is disabled;
2. two surface-imputer calls include the held-out well;
3. the contact candidate reloads complete training-well TVT truth;
4. the ablation does not jointly replay the model-package, guarded-contact,
   and D29 non-branch transactions.

`prepare_leak_safe_cv_notebook.py` produces a clearly labelled local component
diagnostic. It enables the ablation, points it at the local dataset, excludes
the held-out well from both spatial imputers, and derives contact offsets only
from the masked visible prefix. Its post-patch audit intentionally remains
`locally_scoreable_as_stored=false` until the missing deployment layers are
implemented with genuine fold training.
