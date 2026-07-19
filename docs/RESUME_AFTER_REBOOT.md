# Resume checkpoint — 2026-07-17

## Latest safe checkpoint — 2026-07-19

- Today's competition budget: exactly `5 / 5`; do not submit again.
- Pending score refs:
  - `54820459`: RobustPF sub7 lineage
  - `54820520`: Cycle8 public 6.909 exact reproduction
  - `54820549`: grouped OOF meta-residual direct route
  - `54820920`: prefix-GR RF well-bias correction
  - `54824801`: independent LGB/ET adaptive route
- All five private kernels completed and their final `submission.csv` files
  passed 14,151-row, ordered-ID, finite-value, and log checks before submission.
- Cycle8 final SHA-256:
  `2b86386f19279e79e7184096f353ccf2b97785de67b268caa56aa5f85405a815`.
- OOF Meta final SHA-256:
  `981dc202697d7e06b06cc46e82aaaff9971b1c9b3f73bba29950ce72e09db00d`.
- OOF Meta grouped OOF RMSE is `9.877028`, versus public ridge
  `10.419669`; it is `3.372194 ft` RMS from the current A04 output.
- New `gmax=0.0075/0.010` public variants were downloaded and rejected:
  only `0.005488 ft` RMS apart and within `0.021953 ft` of Cycle8.
- Public Code versions completed for the three agent research notebooks.
- A04 scored documentation version 2 was pushed public and is running. Never
  submit that documentation version to the competition.
- LGB v40 adaptive private version 1 completed successfully and used the final
  daily slot after its exact-output audit passed. Its per-well adaptive CV RMSE
  is `9.5355`; final SHA-256 is
  `28603fe1ad9e5a958ca237dba143b5c3af33673f85e010c5f8fd7673e798e190`.
- LGB visible RMS distances are `10.484754 / 10.371602 / 9.402353 /
  10.684860 ft` versus A04 / Cycle8 / OOF Meta / WellBias. It is
  `8.126623 ft` RMS from the downloaded upstream output.
- Neighbor TVT-shape transfer CV completed on all 773 wells. Best fixed route:
  five donors within 750 ft, 30% blend, pooled RMSE `15.6153`; not submitted.
- Detailed state: `docs/RESULTS_2026-07-19.md`.

## Exact next actions after restart — 2026-07-19

1. Poll competition submissions; do not resubmit any pending ref.
2. As each real score arrives, update README, the D19 result log, experiment
   log, and the candidate notebook score cell before publishing its
   documentation version.
3. Do not competition-submit documentation versions, `gmax` micro-variants,
   AYO duplicates, or neighbor-transfer variants.
4. Run tests and JSON validation, then commit and push `main`.

## Latest safe checkpoint — 2026-07-18

- Today's competition budget is exhausted: exactly `5 / 5` submissions, with
  no sixth submission allowed.
- Completed scores: `54808956=9.571`, `54808958=7.123`,
  `54809311=7.010`, `54809350=7.170`, `54809629=7.130`.
- All five source notebooks completed privately before submission.
- All five `submission.csv` files passed exact 14,151-row sample ID order,
  finite-value, log, and SHA-256 audits.
- Full 773-well 16-seed particle audit completed: best fixed candidate is the
  65% particle blend at `12.7989` pooled RMSE; it was not submitted.
- Kaggle research notebooks `rogii-five-submission-agent-playbook`,
  `rogii-public-route-distance-atlas`, and
  `rogii-public-artifact-lineage-checklist` completed private CPU smoke runs.
- The five score-bearing reproduction notebooks and three new research
  notebooks have completed private smoke runs. Their English descriptions now
  contain the measured scores and they are ready for public documentation
  versions.
- Unit tests: 14 passing.
- A score-polling process may still be active. If not, rerun the submissions
  command below. Do not submit again.

## Exact next actions after restart

1. Change notebook metadata to public and push documentation versions only.
   Never submit those later versions.
2. Review new Code routes against the `7.010` A04 best before using any
   2026-07-19 submission.
3. Update README, run the 14-test suite, commit, and push GitHub.
4. Publish the English Discussion only after it links to the completed public
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
