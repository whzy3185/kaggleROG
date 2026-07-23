# Resume checkpoint — 2026-07-17

## Latest active checkpoint - 2026-07-23

- D22 final scores are `6.667 / 6.667 / 6.667 / 6.638 / 6.638` for refs
  `54895366 / 54895437 / 54895837 / 54896174 / 54896197`. The two WellBias
  crosses tie for the repository best; cap 2.5 is the selected representative
  of the tied `6.667` runner-up tier.
- D23 began at exactly `0 / 5`. The pre-registered routes are A27 PF-1.3
  centered shape, A31 Toe tilt, A28 PF-1.3 `w=0.62`, U-continuity8, and A27
  crossed with grouped-OOF WellBias.
- A27, A31, A28, U-continuity8, and A27 plus WellBias private version 1 passed
  their 14,151-row exact-order, finite-value, SHA-256, and fatal-log audits and
  were submitted as refs `54917836 / 54917838 / 54918138 / 54918139 /
  54918377`. The budget is final at exactly `5 / 5`; all scores are pending and
  no later submission is allowed today.
- The first attempted longer A27-WellBias slug left no runnable notebook and
  consumed no competition submission. The valid private scorer is
  `muelsyse111/rogii-d23-a27-pf13-wb` Version 1.
- The D22 cap-2.5 English public Code completed as
  `muelsyse111/rogii-p100-cap2-5-measured-6-667`, byte-exact to the private
  scoring artifact. It must never be submitted.
- The D22 cap-2.5 runner-up public Code is a documentation rerun only. Never
  submit that later public version to the competition.
- No automation or recurring task is active or should be created.

## Latest safe checkpoint - 2026-07-21

- D20 is final at exactly `5 / 5` submissions:
  - `54845744`: MHA140SEP4 = `6.979`.
  - `54845785`: MHA160SEP4 = `6.958`.
  - `54845963`: MHA180SEP4 = `6.941`.
  - `54846028`: A12 self-log Viterbi = `6.979`.
  - `54846177`: MHA160SEP4 plus WellBias = `6.934`, the repository best.
- All D20 private artifacts passed the 14,151-row ordered-ID, finite-value,
  SHA-256, and fatal-log audits before submission.
- D21 UTC budget is final at exactly `5 / 5`; do not submit again today. The
  five submitted refs are `54869017 / 54869048 / 54869266 / 54869268 /
  54869492`; their final scores are `6.858 / 6.849 / 6.855 / 6.832 / 6.829`.
- The routes are exact MHA250SEP2, exact MHA260SEP3, derived MHA260SEP2,
  MHA250SEP2 plus WellBias, and MHA260SEP2 plus WellBias. All five private
  version-1 artifacts passed the 14,151-row ordered-ID, finite-value,
  final-file, SHA-256, probe-off, and fatal-log audits before submission.
- Never competition-submit a later public documentation version. Public Code
  versions may be created only after the exact private scoring version is
  audited and submitted.
- No automation or recurring task is active.

## Latest active checkpoint - 2026-07-22

- D21 final scores are `6.858 / 6.849 / 6.855 / 6.832 / 6.829`; ref `54869492`
  is the repository best and ref `54869268` is the runner-up selected for an
  English public Code edition.
- D22 is final at exactly `5 / 5` submissions; do not submit again today. Refs
  `54895366 / 54895437 / 54895837 / 54896174 / 54896197` are pending real
  scores.
- The five P100 routes are cap `2.0 / 2.5 / 3.0`, cap 2 plus WellBias, and cap
  2.5 plus WellBias. Every private artifact passed the 14,151-row ordered-ID,
  finite-value, final-hash, branch/WellBias-difference, and fatal-log audits.
- The D21 runner-up English public Code is
  `muelsyse111/rogii-mha250sep2-wellbias-measured-6-832` Version 1. It was
  completed publicly as Code only, byte-matched the private scoring artifact,
  and must never be competition-submitted.
- Never submit the later public documentation edition to the competition.
- No automation or recurring task is active.

## Latest safe checkpoint — 2026-07-19

- Today's competition budget: exactly `5 / 5`; do not submit again.
- Completed D19 scores (all five refs are final):
  - `54820920`: prefix-GR RF WellBias = `6.988` public RMSE; new repository best.
  - `54820459`: RobustPF sub7 lineage = `7.454` public RMSE.
  - `54820520`: Cycle8 reproduction = `7.960` public RMSE; upstream source
    claim was `6.909`.
  - `54820549`: grouped OOF Meta direct route = `7.866` public RMSE; grouped
    OOF ramped RMSE was `9.877028`.
  - `54824801`: independent LGB/ET adaptive route = `10.308` public RMSE.
- All five private kernels completed and their final `submission.csv` files
  passed 14,151-row, ordered-ID, finite-value, and log checks before submission.
- Cycle8 final SHA-256:
  `2b86386f19279e79e7184096f353ccf2b97785de67b268caa56aa5f85405a815`.
- Cycle8 score-bearing public Code version:
  `muelsyse111/rogii-cycle8-repro-measured-7-960`. Never submit this documentation
  rerun to the competition.
- OOF Meta final SHA-256:
  `981dc202697d7e06b06cc46e82aaaff9971b1c9b3f73bba29950ce72e09db00d`.
- OOF Meta score-bearing public Code version:
  `muelsyse111/rogii-oof-meta-direct-repro-measured-7-866`. Never submit this
  documentation rerun to the competition.
- OOF Meta grouped OOF RMSE is `9.877028`, versus public ridge
  `10.419669`; it is `3.372194 ft` RMS from the current A04 output.
- RobustPF and Cycle8 produced numerically identical visible predictions but
  scored `7.454` and `7.960`, a `0.506` execution-lineage gap.
- WellBias final SHA-256 is
  `54d5b3b08943e55c2c60a6fcb8b15edf5a950afa469f0978f6a40ff5c81d039d`;
  it is `0.371033 ft` RMS from A04 and improves A04 by `0.022` public RMSE.
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

1. D19 is complete; do not resubmit any D19 ref or documentation version.
2. Use WellBias `6.988` as the measured reference for new candidate triage.
3. Do not submit `gmax` micro-variants, AYO duplicates, or neighbor-transfer
   variants.
4. Run tests and JSON validation after each material result update, then commit
   and push `main`.

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
