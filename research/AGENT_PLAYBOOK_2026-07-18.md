# ROGII Agent Experiment and Submission Playbook

Date: 2026-07-18

This note turns the current ROGII work into a repeatable workflow for coding
agents. It separates public-source reproduction, local evidence, competition
submission, and public notebook publishing so that a score can always be traced
back to one immutable notebook version.

## Non-negotiable state

- Metric: pooled row-level RMSE, lower is better.
- Daily competition budget: five submissions.
- A local or visible-test check does not estimate the hidden score. It is a
  safety gate that prevents broken or redundant submissions.
- Every candidate must retain its source URL, author attribution, notebook
  version, output hash, submission reference, and public score.
- A score belongs to an exact notebook version. Never attach a score to a later
  code version unless the generated `submission.csv` is byte-identical.

## Agent state machine

1. **Discover**: list recent public notebooks and Discussions, then record the
   claimed score and all external inputs.
2. **Reproduce**: fork privately with internet disabled and unchanged
   dependencies. Do not submit an upstream CSV directly.
3. **Audit**: require a completed run, 14,151 rows, exact sample ID order, no
   duplicate IDs, finite predictions, a SHA-256 hash, and no fatal traceback.
4. **Differentiate**: compare predictions against already tested candidates.
   Exact duplicates should not spend a submission unless their hidden execution
   lineage is materially different and that distinction is documented.
5. **Submit once**: bind one competition submission to one immutable notebook
   version and decrement the daily budget exactly once.
6. **Observe**: wait for completion and record the submission reference, public
   score, timestamp, and delta from the current best.
7. **Publish**: make the reproducible notebook public only after adding source
   attribution, the exact measured score, output hash, and an honest
   interpretation.
8. **Stop**: when the daily budget reaches zero, continue local and Code
   research only.

## Candidate routing on 2026-07-18

Five public-source routes were selected because their implementations differ:

| Route | Main distinguishing decision |
|---|---|
| Public rebuild | Likelihood-weighted particle filter, pretrained tree blend, physical projection, and visible-prefix selection |
| Dual track | Adds a very small disagreement-gated model-package correction |
| A04 residual transfer | Adds bounded prefix-validated residual-shape transfer and a measured global bias |
| G040/S12 | Uses a larger model-package gate and scale-12 selector profile |
| Safe rebuild | Uses the balanced visible-prefix profile and preserves a conservative fallback |

The visible-test outputs are very close to one another. Public rebuild and safe
rebuild are byte-identical on the visible rows; public rebuild and dual track
have only `0.01098 ft` RMS prediction distance. A04 differs from public rebuild
by `0.39773 ft` RMS, while G040/S12 differs by `0.22062 ft`. These small
distances are calibration experiments, not independent model families.

The earlier in-repository particle model is genuinely different: its RMS
distance from the five strong public routes is approximately `9.4-9.6 ft`.
Candidate correlation alone is misleading here because all predictions share a
large absolute TVT level; use RMS delta and per-well range instead.

## Prediction-disagreement map

Run:

```powershell
python scripts/analyze_candidate_disagreement.py `
  --sample data/raw/competition/sample_submission.csv `
  --candidate particle=artifacts/kaggle_particle_v2/submission.csv `
  --candidate public_rebuild=artifacts/upstream_20260718/lb7295/submission.csv `
  --candidate dual_track=artifacts/upstream_20260718/dual_track/submission.csv `
  --candidate residual_transfer=artifacts/upstream_20260718/another_approach/submission.csv `
  --candidate g040_s12=artifacts/upstream_20260718/public7015/submission.csv `
  --candidate safe7016=artifacts/upstream_20260718/safe7016/submission.csv `
  --output-dir artifacts/candidate_disagreement_20260718
```

The script ranks rows and wells by standard deviation and range across
candidates. This is an uncertainty signal, not a hidden-label score estimator.
For the three visible test wells, `00bbac68` has the largest disagreement,
followed by `00e12e8b` and `000d7d20`. A useful next agent should therefore
inspect branch ambiguity and prefix evidence per well instead of applying a new
global blend coefficient.

## Local particle stability result

A full 773-well true-start replay using 300 particles, 16 seeds, likelihood
temperature 20, and an independent seed base produced:

| Candidate | Pooled RMSE |
|---|---:|
| Anchor | 15.9099 |
| Particle | 13.7321 |
| 50% particle blend | 12.9927 |
| 65% particle blend | 12.7989 |
| 75% particle blend | 12.8717 |

The 65% blend won `61.97%` of wells against the anchor and is a useful
independent floor. It should not consume a submission while audited public
routes are expected to be near 7 RMSE.

## High-value tasks for the next agents

### Per-well branch posterior

Replace a single final path with a small set of branch hypotheses. Score each
branch using only the visible prefix, typewell GR alignment, physical
smoothness, and neighbor consistency. Emit posterior mean, entropy, and the gap
between the best two branches. Apply corrections only when the margin is large.

### Cross-fitted correction gate

Treat every late correction as a model-selection problem. On training wells,
mask the suffix at the official boundary, create base and corrected
predictions, and train a gate on prefix-only features. Use grouped,
out-of-fold predictions so the gate never learns from its own well's target.

### Disagreement-aware fallback

Use candidate disagreement as a routing feature. When learned, physical, and
GR-alignment tracks agree, allow a modest correction. When they disagree,
shrink toward a conservative anchor or posterior average. Evaluate pooled RMSE,
per-well win rate, worst-decile RMSE, and maximum regret.

### Boundary-regime validation

Report results separately for suffix length, Z span, GR residual noise,
typewell motif ambiguity, and visible-prefix length. A globally good correction
may be harmful in one regime, and that regime can dominate pooled RMSE.

### Artifact and lineage verifier

Before a run, hash every dataset/model input and check that expected files
exist. After a run, save the prediction hash and a compact manifest. This avoids
silently assigning a leaderboard score to a notebook that fell back to a
different model path.

### Submission-budget controller

Maintain a persistent ledger keyed by competition date. The controller should
reject duplicate hashes, reject candidates without a completed private run, and
stop at five submissions. Score polling and Code publication are separate
actions and do not spend the competition budget.

## Publication checklist

- English title and detailed English introduction.
- Clear "public-source reproduction" label and link to the original author.
- Exact public score and submission reference from this account.
- Exact notebook version and `submission.csv` SHA-256.
- Description of what changed and what did not.
- No claim that visible-test agreement proves hidden-test quality.
- No private competition data, credentials, or unlicensed external artifact.

