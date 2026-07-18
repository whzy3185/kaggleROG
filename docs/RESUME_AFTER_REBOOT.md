# Resume checkpoint — 2026-07-17

## Latest safe checkpoint — 2026-07-18

- Today's competition budget is exhausted: exactly `5 / 5` submissions, with
  no sixth submission allowed.
- Pending score refs: `54808956`, `54808958`, `54809311`, `54809350`,
  `54809629`.
- All five source notebooks completed privately before submission.
- All five `submission.csv` files passed exact 14,151-row sample ID order,
  finite-value, log, and SHA-256 audits.
- Full 773-well 16-seed particle audit completed: best fixed candidate is the
  65% particle blend at `12.7989` pooled RMSE; it was not submitted.
- Kaggle research notebooks `rogii-five-submission-agent-playbook`,
  `rogii-public-route-distance-atlas`, and
  `rogii-public-artifact-lineage-checklist` completed private CPU smoke runs.
- The five score-bearing reproduction notebooks and three new research
  notebooks remain private until the real scores are written into their English
  descriptions.
- Unit tests: 14 passing.
- A score-polling process may still be active. If not, rerun the submissions
  command below. Do not submit again.

## Exact next actions after restart

1. Poll the five refs until all are `COMPLETE`.
2. Replace score/reference placeholders in the five reproduction notebooks,
   three research notebooks, result log, experiment ledger, and Discussion
   draft.
3. Change notebook metadata to public and push documentation versions only.
   Never submit those later versions.
4. Update README, run the 14-test suite, commit, and push GitHub.
5. Publish the English Discussion only after it links to the completed public
   Agent Playbook.

## Previous safe state — 2026-07-17

- All local processes for experiments have finished.
- Competition data is fully downloaded and extracted under ignored `data/raw/competition/`.
- Unit tests: 12 passing.
- Generated CV details are under ignored `artifacts/`.
- Two of five daily competition submissions have been used.

## Kaggle state

- Submission ref `54778368`: complete, public score `15.883`.
- Submission ref `54779893`: complete, public score `12.774`; submitted private notebook version 1.
- Current private notebook version 2 corrects the seed-audit prose only; its output hash matches version 1.
- Private submission notebook: `muelsyse111/rogii-private-safe-particle-anchor-blend`.
- Public notebook v2: `muelsyse111/rogii-honest-773-well-baseline-audit`.
- Public idea notebook: `muelsyse111/rogii-prefix-backtest-trap-more-cuts-can-hurt`.
- Public idea notebook: `muelsyse111/rogii-particle-filter-lab-anchor-blending`.
- Public idea notebook: `muelsyse111/rogii-true-start-failure-atlas-tail-risk`.
- Public idea notebook: `muelsyse111/rogii-particle-seed-independence-audit`.
- Public idea notebook: `muelsyse111/rogii-one-coefficient-three-rmse-optima`.
- Public idea notebook: `muelsyse111/rogii-typewell-gr-motif-ambiguity-atlas`.
- Public idea notebook: `muelsyse111/rogii-boundary-geometry-score-concentration`.
- Public idea notebook: `muelsyse111/rogii-prefix-only-gr-calibration-audit`.
- Failed private DWT reproductions were not submitted. The current artifact dataset does not contain the `models.pkl` filenames expected by the pulled public notebook.

## Strongest local candidate

Configuration: U-state particle tracker, 300 particles, 8 seeds, likelihood temperature 20, fixed particle weight 0.625.

- Anchor, all 773 wells: pooled RMSE `15.9099`.
- Seed bases `20260717` and `20260718` overlap on 7/8 particle seeds; the second is not independent.
- Raw particle, original / genuinely disjoint seed base `20270717`: `14.1804 / 14.5647`.
- Fixed 62.5% particle blend: `13.1119 / 13.3505`.
- Independent optimal particle weights: `0.6253 / 0.5975`; joint optimum `0.6113`.
- Five-fold OOF learned-weight RMSE: `13.1544 / 13.3577`.
- Fixed-blend p95: `25.1211 / 25.4364`; worst: `56.0336 / 70.5435`.
- Independent-run per-well blend RMSE correlation: `0.9003`.

## Exact next actions

1. Do not submit 0.60/0.65 or other weight variants; local validation already resolves that question.
2. Investigate a genuinely independent residual or GR-alignment candidate before submission 3/5.
3. Target the remaining stochastic worst-well branch failures; do not use suffix truth for a gate.
4. Retry Discussion publication only if an authenticated browser-control channel is available; the detailed English draft is already saved.

## Commands

```powershell
cd E:\kaggleROG
python -m unittest discover -s tests -v
E:\anaconda\Scripts\kaggle.exe competitions submissions rogii-wellbore-geology-prediction
```
