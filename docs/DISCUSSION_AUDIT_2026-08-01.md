# ROGII Discussion audit - 2026-08-01

## Decision

The final two D32 slots test ensembles, not another public-leaderboard-directed
single-well correction:

1. an equal-weight consensus of the measured D29 best plus the three exact D32
   public reproductions;
2. a row-wise four-route median, equivalent to averaging the middle two
   predictions and rejecting the two row-wise extremes.

Both formulas were fixed before their competition submissions. They use every
row, do not select a named well, and do not use the pending D32 scores.

## Discussion evidence

- [How should we choose the final two submissions?](https://www.kaggle.com/competitions/rogii-wellbore-geology-prediction/discussion/731550)
  emphasizes the mismatch between validation over 773 wells and the roughly
  50-well public slice. Reported fold-only leaderboard scores span about
  `5.2` to `6.3` for closely related models whose overall CV is `5.13`.
  The actionable recommendation is to trust broad CV and retain diversity or
  one safe/one risk route rather than rank models only by the small public set.
- [The public LB is a precise ruler and a biased one](https://www.kaggle.com/competitions/rogii-wellbore-geology-prediction/discussion/728477)
  separates same-slice comparison from private generalization. It reports a
  typical deterministic-family rerun standard deviation of roughly `0.02` to
  `0.04 ft`, warns that hard argmin selection can amplify near ties, and notes
  that averaging tied candidates is the natural variance-control operation.
- [Fork the ruler, not the model](https://www.kaggle.com/competitions/rogii-wellbore-geology-prediction/discussion/712037)
  argues that fine per-well drift is difficult to learn legally on held-out
  fields and recommends measuring the recoverable error/noise floor before
  treating a small lever as signal.
- [Question about the geologists' analysis](https://www.kaggle.com/competitions/rogii-wellbore-geology-prediction/discussion/719235)
  shows that known TVT can correct typewell interpretation, but also documents
  wells where typewell alignment is poor. This supports retaining multiple
  modelling families rather than forcing one typewell-derived correction on
  every hidden well.

## Pre-submission output audit

| Candidate | Formula | Prediction SHA after CSV reload | File SHA-256 | RMS from D29 |
|---|---|---|---|---:|
| Four-way consensus | `0.25 * (D29 + GeoAnchor + Roman + Tamerlan)` | `7e67476b...96f6` | `eb14ead0...fd0c` | `0.175213 ft` |
| Robust middle-pair consensus | `median(D29, GeoAnchor, Roman, Tamerlan)` | `f818f799...335b` | `7b3bd903...84e4` | `0.178312 ft` |

The robust candidate is `0.278461 ft` RMS from the arithmetic consensus. Its
purpose is not to choose a public-score direction: on every row it suppresses
the lowest and highest parent and averages the tied middle. Its private
Version 1 completed with 14,151 ordered unique IDs, finite predictions,
formula agreement within `1.9e-12 ft`, and no fatal log markers.

An earlier GeoAnchor/Roman anticorrelated hedge completed privately but was
rejected before competition submission. Although its full-output delta
correlation was attractive, its visible-test change was dominated by one
branch well and therefore did not have enough generalization evidence.

## Competition submission ledger

| Slot | Ref | Kaggle UTC | Candidate | Final checkpoint |
|---:|---:|---|---|---|
| 4 | `55161568` | `11:58:36.280` | Four-way arithmetic consensus v1 | failed: hidden-rerun unhandled error |
| 5 | `55162186` | `12:32:57.587` | Robust middle-pair consensus v1 | failed: hidden-rerun unhandled error |

The gaps from Slot 3 to 4 and Slot 4 to 5 are `32:00.333` and `34:21.307`.
Both exceed 31 minutes 30 seconds. D32 is final at exactly `5 / 5`.

Both failures were caused by deployment-parity mistakes: the notebooks used
fixed 14,151-row public parent files and public-output SHA contracts that do
not generalize to Kaggle's hidden rerun. Passing the visible output audit was
not evidence that these notebooks could score.
