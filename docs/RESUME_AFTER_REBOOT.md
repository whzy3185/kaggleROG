# Resume checkpoint — 2026-07-17

## Safe state

- All local processes for experiments have finished.
- Competition data is fully downloaded and extracted under ignored `data/raw/competition/`.
- Unit tests: 12 passing.
- Generated CV details are under ignored `artifacts/`.
- Only one of five daily competition submissions has been used.

## Kaggle state

- Submission ref `54778368`: complete, public score `15.883`.
- Public notebook v2: `muelsyse111/rogii-honest-773-well-baseline-audit`.
- Public idea notebook: `muelsyse111/rogii-prefix-backtest-trap-more-cuts-can-hurt`.
- Public idea notebook: `muelsyse111/rogii-particle-filter-lab-anchor-blending`.
- Public idea notebook: `muelsyse111/rogii-true-start-failure-atlas-tail-risk`.
- Failed private DWT reproductions were not submitted. The current artifact dataset does not contain the `models.pkl` filenames expected by the pulled public notebook.

## Strongest local candidate

Configuration: U-state particle tracker, 300 particles, 8 seeds, likelihood temperature 20, deterministic seed base `20260717`.

- Anchor, all 773 wells: pooled RMSE `15.9099`.
- Raw particle: `14.1804`.
- Fixed 65% particle blend: `13.1167`.
- Full-fit optimal particle weight `0.6253`: `13.1119`.
- Five-fold out-of-well learned weights: `0.6272, 0.6294, 0.6632, 0.5872, 0.6169`.
- Five-fold OOF learned-weight RMSE: `13.1544`.
- Blend65 p95/worst: `25.1560 / 56.5684`, versus anchor `29.0108 / 70.6394`.

## Exact next actions

1. Run the same full 773-well particle CV with seed base `20260718` to test stochastic stability.
2. Compare fixed 0.625/0.65 blends across both runs; do not retune on the leaderboard.
3. If replicated, build a private deterministic inference notebook that generates and audits `submission.csv` on hidden rerun wells.
4. Execute the notebook on Kaggle, inspect logs/output, then consider using submission 2/5.
5. Retry Discussion publication only if an authenticated browser-control channel is available; the detailed English draft is already saved.

## Commands

```powershell
cd E:\kaggleROG
python -m unittest discover -s tests -v
python scripts\run_particle_cv.py --sample-size 773 --particles 300 --seeds 8 --temperature 20 --jobs 4 --seed 20260718 --output-dir artifacts\particle_cv_full_t20_seed2
```
