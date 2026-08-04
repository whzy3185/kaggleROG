# Kaggle ROGII Wellbore Geology Prediction

## Current experiment status (2026-08-04)

- D36 is a generalization-first five-route slate informed by the latest Code
  and Discussion refresh.  The public leaderboard covers about 26% / roughly
  50 wells and can be noisy; current competitors recommend validation trust,
  whole-model diversity, and a robust ensemble insurance route rather than a
  single public-score or single-fold bet.
- D36 is final at exactly `5 / 5`. Slots 1 through 5 are Raunak Stack ref
  `55225251`, Final Hierarchy ref `55225757`, AkiiroLabs ref `55226347`,
  Frontier Blend ref `55227570`, and Shift275 ref `55228301`.
- The five UTC timestamps are `01:01:16.617 / 01:31:53.737 / 02:02:29.937 /
  03:08:32.327 / 03:39:23.840`; gaps are
  `30:37.120 / 30:36.200 / 66:02.390 / 30:51.513`. Every ref is pending
  without an error marker; do not resubmit any ref or report a score until
  Kaggle supplies one.
- AkiiroLabs full source passed the dynamic sample-order, finite-value,
  source/metadata/output SHA, no-mounted-submission-parent, and clean-log
  gates. Frontier Blend and Shift275 passed the same deployment gates before
  their refs were created.
- Harshini remained running beyond two hours. Its 26%-to-full-test runtime
  projection approached the nine-hour hidden rerun limit, so it was not
  competition-submitted; audited Shift275 was used as the deployment-safe
  fallback for slot 5.
- Physics v48 appeared first in the CLI `scoreAscending` response, but that
  response exposes no score field and does not prove it has the best public
  score. It was not resubmitted because its artifact is a duplicate of a
  previously audited/measured route. Public outputs are research inputs only,
  never hidden prediction parents. Detailed evidence:
  [2026-08-04 results](docs/RESULTS_2026-08-04.md).

## Current experiment status (2026-08-01)

- D32 consumed exactly `5 / 5`. GeoAnchor ref `55159859`, Roman Smartest ref
  `55160477`, and Tamerlan DET AGI ref `55161022` scored
  `6.517 / 6.501 / 6.499`; none beat D29 `6.455`. Four-way arithmetic consensus ref
  `55161568` and robust middle-pair consensus ref `55162186` both failed with
  an unhandled error during Kaggle's hidden-data rerun.
- Every private output passed the 14,151 ordered unique-ID, finite-value,
  exact-parent SHA-256, pairwise-distance, and fatal-log audits. Adjacent gaps
  are `38:44.217 / 31:55.037 / 32:00.333 / 34:21.307`.
- Four differently titled high-score notebooks were rejected because they all
  emitted the already measured SHA `b192d3f3...9ded4`; the D31 Blacklions SHA
  was also not repeated. A proposed anticorrelated hedge was rejected before
  submission because one visible branch well dominated its change.
- A complete public/private Code run is not a successful competition result.
  The decisive fields are `publicScore` and `errorDescription`; the previous
  status-only audit missed 13 historical failures. See the
  [submission failure audit](docs/SUBMISSION_FAILURE_AUDIT_2026-08-01.md).
- Competition submission is now fail-closed. Public notebooks and their
  outputs remain valid research inputs. The preflight rejects only using a
  fixed visible `submission.csv` as the hidden prediction parent, plus any new
  public-only row/ID contract beyond a genuinely scored source lineage,
  unbounded runtime changes,
  source-lineage drift, output/audit hash mismatches, and fatal logs. The
  submission wrapper then rechecks the exact remote source and output, blocks
  unresolved refs or any same-day failure, enforces 30-minute spacing and the
  daily budget, and requires explicit execution. A first overly broad version
  of the gate rejected inherited D29 constants; this was corrected on
  2026-08-02 before any new competition ref was created.
- Detailed evidence: [2026-08-01 results](docs/RESULTS_2026-08-01.md).

## Current experiment status (2026-08-02)

- Today's pre-registered full-source response curve is D29 non-branch weight
  `10 / 15 / 20 / 25 / 30%`. Every variant recomputes predictions from the
  competition data; public submissions are read for research but are not used
  as hidden runtime parents.
- The first successful scored candidate is the deployment canary. Later
  weights must share its normalized executable lineage, pass independent
  source/output/hash/log gates, remain at least 30 minutes apart, and stop the
  slate immediately if Kaggle reports an error.
- D34 is final at exactly `5 / 5`: refs
  `55176648 / 55177095 / 55177643 / 55178232 / 55178688` correspond to
  `15 / 10 / 20 / 25 / 30%`. Kaggle UTC timestamps are
  `03:40:51.810 / 04:11:34.507 / 04:42:59.720 / 05:14:22.713 /
  05:45:49.253`; adjacent gaps are
  `30:42.697 / 31:25.213 / 31:22.993 / 31:26.540`.
- All five exact remote private versions passed source, metadata, output,
  sample-order, finite-value, log, lineage, and nonduplicate gates immediately
  before submission. The final `10 / 15 / 20 / 25 / 30%` scores are
  `6.495 / 6.532 / 6.473 / 6.535 / 6.467`. Every ref completed without an
  error; 30% was the best D34 response but did not beat D29 `6.455`.
- Detailed evidence: [2026-08-02 results](docs/RESULTS_2026-08-02.md).

## Current experiment status (2026-07-31)

- D31 treats the public leaderboard as only one quarter of the evaluation
  set. Single-well `+/-0.25 ft` coordinate probes are excluded; the remaining
  slate uses pre-registered whole-output risk blends and one previously
  measured structural delta.
- Blacklions' public Final Hierarch v6 was reproduced from unchanged modelling
  code in this account's private Version 1. The upstream and copied modelling
  code hashes both equal `46b57daa...c9422`; the output file SHA
  `9196a563...f0c4f` and prediction SHA `f9f96622...de6f1` match the public
  artifact exactly. The page-reported `6.390` is not inherited as our score.
- D31 is final at exactly `5 / 5`: refs
  `55128484 / 55129144 / 55129811 / 55130546 / 55131268` are the exact
  public-source reproduction, 75/25, 50/50, and 25/75 whole-output risk
  blends, and champion plus the measured non-branch delta.
- Kaggle UTC timestamps are
  `05:45:50.743 / 06:17:56.567 / 06:50:00.277 / 07:21:54.120 /
  07:53:49.170`; adjacent gaps are
  `32:05.824 / 32:03.710 / 31:53.843 / 31:55.050`. The minimum exceeds
  30 minutes.
- Four additional private Version 1 candidates have passed their 14,151-row
  ordered-ID, finite-value, SHA-256, pairwise-distance, and fatal-log audits:
  75/25, 50/50, and 25/75 champion/D29 risk blends, plus champion with the
  measured D29-minus-D25 non-branch delta.
- Same-name full `TVT` trajectories in the local cache contradict known
  leaderboard measurements and are treated as stale/same-well artifacts, not
  hidden-test labels. Detailed evidence:
  [2026-07-31 results](docs/RESULTS_2026-07-31.md).
- Slots 2 through 5 failed with an unhandled error during the hidden-data
  rerun. Only the exact Blacklions reproduction scored (`6.507`, not the
  page-reported `6.390`); it did not beat the D29 `6.455` record. Do not
  resubmit any D31 ref or submit a later Code version.

## Current experiment status (2026-07-23)

- D22 is final: cap `2.0 / 2.5 / 3.0` each scored `6.667`, while cap 2 and
  cap 2.5 crossed with grouped-OOF WellBias each scored **`6.638`**. The two
  orthogonal corrections therefore improved the no-WellBias tier by `0.029`.
- The D23 grid contains five materially distinct routes: A27 centered PF-1.3
  branch shape, A31 mean-preserving Toe tilt, A28 PF-1.3 blend `w=0.62`,
  U-continuity8, and A27 crossed with grouped-OOF WellBias.
- The D23 budget is final at exactly `5 / 5`: refs `54917836 / 54917838 /
  54918138 / 54918139 / 54918377`. A27 scored **`6.476`**, A31 scored `6.546`,
  A27 plus WellBias scored `6.562`, U-continuity8 scored `6.617`, and A28
  failed the hidden-dataset runtime limit. A27 is the repository best.
- Current high-ranking public Code was audited before reuse. Six differently
  titled notebooks produced the same byte-identical P100 cap-2 artifact, so
  only genuine output changes were admitted to the D23 grid.
- The selected D22 runner-up-tier representative is cap 2.5 (`6.667`, ref
  `54895437`). Its English public Code edition completed as
  [`rogii-p100-cap2-5-measured-6-667`](https://www.kaggle.com/code/muelsyse111/rogii-p100-cap2-5-measured-6-667)
  and is byte-exact to the scoring artifact (SHA-256 `2d2d40b...778494`). It
  must never be competition-submitted.
- Detailed evidence: [2026-07-23 results](docs/RESULTS_2026-07-23.md)

## Current experiment status (2026-07-24)

- The D24 budget is final at exactly `5 / 5`: refs `54941181 / 54941242 /
  54941455 / 54941513 / 54941756`. The routes are A27 weights `0.08 / 0.12 /
  0.15`, plus weights `0.10 / 0.12` crossed with the A31-derived zero-mean
  0.18 ft Heel-to-Toe tilt. All five own outputs passed ordered-ID,
  finite-value, SHA-256, controlled-distance, non-duplicate, and log audits
  before submission. Scores were `6.539 / 6.528 / 6.549 / 6.511 / 6.525`;
  the D23 A27 record remains `6.476`.
- Current public Code was audited again. Four high-position pages still emit
  the old cap-2 SHA, while the two new frontier pages share one cap2-plus-0.522
  output. Those title duplicates are not allocated separate submission slots.
- The D23 runner-up A31 (`6.546`, ref `54917838`) completed as a detailed
  English documentation notebook and reproduced the scoring artifact
  byte-for-byte. Kaggle currently blocks making any notebook with this
  competition source public until the competition ends, so it remains
  private and ready for the permitted publication date; it will never be
  competition-submitted.
- Detailed evidence: [2026-07-24 results](docs/RESULTS_2026-07-24.md)

## Current experiment status (2026-07-25)

- The D25 budget is final at exactly `5 / 5`: refs `54966176 / 54966324 /
  54966407 / 54966525 / 54966580`. The pre-registered grid contains two
  current-source routes (GS1.30 plus Q0522 and A28 plus dynamic Q0522) and
  three A27 shape ablations: smoothing windows `15/7`, smoothing windows
  `61/21`, and a 0.25-ft clip. The measured scores were `6.547 / 6.469 /
  hidden-runtime-failure / 6.485 / 6.536`; A27 `15/7` established the new repository
  best at **`6.469`**.
- Ten current high-position Code outputs were audited. Four were byte-identical
  cap2, two were byte-identical Q0522, and only the A28/frontier branches
  contributed genuinely new full-vector outputs.
- Every D25 slot used its own private Version 1 only after it passed the
  14,151-row ordered-ID, finite-value, SHA-256, distance, non-duplicate, and
  fatal-log audits. No later Code version may be competition-submitted.
- Detailed evidence: [2026-07-25 results](docs/RESULTS_2026-07-25.md)

## Current experiment status (2026-07-26)

- The D26 budget is final at exactly `5 / 5`: refs `54988991 / 54988992 /
  54988994 / 54989268 / 54989315`. Four A27 smoothing routes were
  pre-registered around the measured `15/7` optimum: `7/3`, `11/5`, `13/7`,
  and `19/9`. They retain weight 0.10 and the measured 0.35-ft clip.
- A fresh public-Code audit found the new A28/Q0522 50:50 pair blend as the
  only distinct late update. Its source report references `6.433`, but D26
  inherits no score claim; our run-local output differed from the public-run
  artifact and is recorded under its own SHA. Exact cap2 and Q0522 duplicates
  were excluded before submission.
- All five own Version 1 outputs passed ordered-ID, finite-value, SHA-256,
  controlled-distance, pairwise non-duplicate, and fatal-log audits. The four
  scored A27 routes measured `6.555 / 6.563 / 6.593 / 6.530`; the pair blend
  failed the hidden-dataset runtime limit. None beat D25 A27 `15/7` at `6.469`,
  so further smoothing-window micro-grids are retired. No later Code version
  may be competition-submitted.
- Detailed evidence: [2026-07-26 results](docs/RESULTS_2026-07-26.md)

## Current experiment status (2026-07-27)

- D27 reserves one slot for an exact current-source reproduction of prvsiyan's
  Frontier II page and four slots for hidden-run-compatible structural routes:
  residual post-contact, GR datum posterior, adaptive branch gating, and a
  six-formation contact consensus.
- The exact reproduction matched the downloaded public artifact byte-for-byte
  (SHA-256 `bf48603d...add8`) and was submitted as ref `55015407`.
- Residual post-contact, Beam posterior without contact overwrite, and the
  adaptive branch gate passed all output contracts and were submitted as refs
  `55015697 / 55015700 / 55015791`. Their visible outputs are respectively
  `5.275397 / 3.306169 / 3.031769 ft` from the D25 A27 record and are pairwise
  materially distinct.
- A pre-contact residual draft was rejected without submission because the
  contact guard made it byte-identical to the exact reproduction. A sub-floor
  contact draft was also rejected. Six-contact consensus R2 passed at
  `0.989646 ft` from A27 and was submitted as ref `55015938`.
- D27 is final at exactly `5 / 5`: refs `55015407 / 55015697 / 55015700 /
  55015791 / 55015938` scored `7.513 / 7.570 / 8.152 / 7.661 / 7.504`.
  Every structural departure regressed against D25 A27 `15/7` at `6.469`;
  the D27 residual, posterior, adaptive-gate, and broad-contact routes are
  retired. No later Code version may be competition-submitted.
- Detailed evidence: [2026-07-27 results](docs/RESULTS_2026-07-27.md)

## Current experiment status (2026-07-30)

- D30 is final at exactly `5 / 5`: refs
  `55096121 / 55096688 / 55097369 / 55097978 / 55098546` are prefix-U drift,
  GS1.60 isolated, GS1.60 plus the measured non-branch delta, dual PF seed
  bank, and non-branch plus same-sign drift.
- Kaggle UTC timestamps are
  `01:30:27.627 / 02:02:43.047 / 02:34:32.193 / 03:06:26.123 /
  03:38:16.510`; adjacent gaps are
  `32:15.420 / 31:49.146 / 31:53.930 / 31:50.387`. The minimum is
  `31:49.146`, so every pair is strictly more than 30 minutes apart.
- Every accepted private Version 1 contains exactly 14,151 ordered unique IDs,
  finite predictions, a matching final SHA-256, a nonduplicate vector, and no
  fatal log marker in their visible private runs. Slots 1, 2, and 4 scored
  `6.526 / 6.517 / 6.502`; slots 3 and 5 failed the hidden submission-format
  check and produced no score.
- The current public-source control was rejected because its SHA
  `83284877...` was already measured. Two full refresh workers failed on an
  empty Kaggle `train` mount and consumed no competition slots; their two
  intended interactions were recovered as fail-closed lightweight R1
  notebooks pinned to exact audited parent SHAs.
- No additional D30 competition submission or later documentation rerun is
  permitted. Detailed evidence: [2026-07-30 results](docs/RESULTS_2026-07-30.md)

## Completed experiment status (2026-07-29)

- D29 is final at exactly `5 / 5`: refs
  `55072903 / 55073402 / 55073985 / 55074584 / 55075184` are the A27
  `15/7` stochastic refresh, positive half-Q, negative half-Q, non-branch
  shape R1, and boundary soft80 R1. They were submitted from audited private
  Code v1 at
  `05:28:41.713 / 05:59:45.267 / 06:30:48.863 / 07:02:04.400 /
  07:33:20.520 UTC`.
- Adjacent gaps are
  `31:03.554 / 31:03.596 / 31:15.537 / 31:16.120`; the minimum is
  `31:03.554`. Scores are `6.541 / 6.517 / 6.560 / 6.455 / 6.530`.
  Non-branch shape is the new measured record at **`6.455`**, improving D25
  A27 by `0.014`; this is below the pre-registered `0.030` parent-promotion
  threshold. No additional D29 submission or later documentation rerun is
  allowed.
- All five candidate files contain exactly 14,151 sample-ordered unique IDs,
  finite predictions, matching embedded SHA-256 values, pairwise-distinct
  vectors, and fatal-marker-free logs.
- The first non-branch and boundary workers encountered a transient empty
  competition mount and were rejected without submission. Their private R1
  slugs completed with unchanged mechanisms and full guards.
- Detailed evidence: [2026-07-29 results](docs/RESULTS_2026-07-29.md)

## Completed experiment status (2026-07-28)

- D28 is final at exactly `5 / 5`: refs `55046933 / 55047312 / 55047700 /
  55048063 / 55048532`. The routes are an exact current-source reproduction of
  Leonid's claimed `6.213` page, A27 `15/7` plus dynamic Q0522, A27 plus
  U-continuity8, A27 with a 192-seed/650-particle PF ensemble, and the
  high-resolution PF/Q0522/U-continuity interaction. The first three scores
  are `6.520 / 6.486 / 6.576`; the last two exceeded the hidden runtime limit
  and produced no scores.
- The exact reproduction emitted the old cap2 artifact byte-for-byte
  (`b192d3f3...ded4a`). The upstream `6.213` title is not inherited; this
  account measured ref `55046933` at `6.520`.
- All five accepted private Version 1 outputs passed the 14,151-row ordered-ID,
  finite-value, matching final SHA, pairwise-distance, and fatal-log audits.
  Successive competition submissions were separated by at least 20 minutes.
- The initial high-resolution drafts were rejected without submission because
  the old A27 source SHA guard correctly detected the changed PF anchor. R1
  preserved the guard and pinned the independently observed high-resolution
  prediction SHA; it did not weaken the contract.
- No additional D28 competition submission or later documentation rerun is
  allowed.
- Detailed evidence: [2026-07-28 results](docs/RESULTS_2026-07-28.md)

## Current validated status (2026-07-21)

- D21 established a new repository best: MHA260SEP2 plus grouped-OOF WellBias
  scored **`6.829`** (ref `54869492`). MHA250SEP2 plus WellBias was the
  runner-up at `6.832` (ref `54869268`).
- The five final D21 scores were `6.858 / 6.849 / 6.855 / 6.832 / 6.829`.
  WellBias improved both SEP2 alpha settings by exactly `0.026`, while alpha
  `2.6` improved alpha `2.5` by `0.003` with and without WellBias.
- The D21 UTC budget is final at exactly `5 / 5`; no further competition
  submission was made after refs `54869017 / 54869048 / 54869266 / 54869268 /
  54869492`.
- All five D21 routes completed privately and passed the 14,151-row ordered-ID,
  finite-value, final-file, and fatal-log audits before submission.
- Detailed evidence: [2026-07-21 results](docs/RESULTS_2026-07-21.md)

## Completed experiment status (2026-07-22)

- The current score-ascending public source reports `6.594`. Its public
  documentation reproduction produced a byte-identical 14,151-row output with
  SHA-256 `b192d3f348ae00680dc4df942b95cef5fd708c636a741f77dfb6b6e89b9ded4a`.
- The five pre-registered routes were cap `2.0 / 2.5 / 3.0`, plus cap
  `2.0 / 2.5` crossed with grouped-OOF WellBias. All five private outputs passed
  the 14,151-row ordered-ID, finite-value, SHA-256, branch-report, and fatal-log
  audits before submission.
- The D22 budget is final at exactly `5 / 5`; refs `54895366 / 54895437 /
  54895837 / 54896174 / 54896197` scored `6.667 / 6.667 / 6.667 / 6.638 /
  6.638`. The tied WellBias routes are the repository best.
- The D21 runner-up is published as English Code:
  [`rogii-mha250sep2-wellbias-measured-6-832`](https://www.kaggle.com/code/muelsyse111/rogii-mha250sep2-wellbias-measured-6-832).
  Version 1 completed publicly and is byte-identical to the private scoring
  artifact (SHA-256 `3d1069d2d40eeb3e508d73318aedcd8d164a1177b2075d9bc9608d3fa49a583d`).
- Detailed evidence: [2026-07-22 results](docs/RESULTS_2026-07-22.md)

## Current validated status (2026-07-19)

- Daily competition submissions: exactly `5 / 5`; no further submission is
  allowed today.
- All five D19 submissions completed:
  - Prefix-GR RF WellBias: **`6.988`** (ref `54820920`; new repository best)
  - RobustPF sub7 reproduction: `7.454` (ref `54820459`)
  - [Grouped OOF Meta reproduction](https://www.kaggle.com/code/muelsyse111/rogii-oof-meta-direct-repro-measured-7-866):
    `7.866` (ref `54820549`; grouped OOF RMSE `9.8770`)
  - [Cycle8 reproduction](https://www.kaggle.com/code/muelsyse111/rogii-cycle8-repro-measured-7-960):
    `7.960` (ref `54820520`; upstream source claim `6.909`)
  - Independent LGB/ET adaptive route: `10.308` (ref `54824801`)
- All five private runs completed before submission and passed the 14,151-row
  ID-order, finite-value, log, and final-output audits.
- WellBias improves the former A04 best (`7.010`) by `0.022` RMSE while moving
  the visible prediction by `0.3710 ft` RMS. Its final SHA-256 is
  `54d5b3b08943e55c2c60a6fcb8b15edf5a950afa469f0978f6a40ff5c81d039d`.
- RobustPF and Cycle8 produced numerically identical visible predictions but
  scored `7.454` and `7.960`, a `0.506` gap that reinforces execution lineage
  as an experimental variable.
- The LGB/ET adaptive run reports per-well adaptive CV RMSE `9.5355` but scored
  `10.308`. Its final
  SHA-256 is
  `28603fe1ad9e5a958ca237dba143b5c3af33673f85e010c5f8fd7673e798e190`,
  and its visible prediction is `10.4848 ft` RMS from A04.
- The OOF meta route reports grouped OOF RMSE `9.8770`, a `0.5426` improvement
  over its public ridge baseline, and is materially different from the A04
  visible prediction (`3.3722 ft` RMS).
- Two new model-package variants (`gmax=0.0075/0.010`) differ by only
  `0.0055 ft` RMS and sit within `0.0220 ft` RMS of Cycle8. They were rejected
  as quota candidates because the public ablation evidence puts changes this
  small inside rerun noise.
- The three agent research notebooks are now public, and the scored A04
  reproduction has been pushed as a public English documentation version.
- A legal leave-one-well-out neighbor-shape transfer improved the anchor from
  `15.9099` to `15.6153` pooled RMSE, but remained far behind the 7.x public
  stack and was correctly withheld from Kaggle submission.
- New public decision notebook:
  [Rerun Noise and Micro-Tuning Filter](https://www.kaggle.com/code/muelsyse111/rogii-rerun-noise-and-micro-tuning-filter).
- New public negative-result notebook:
  [Neighbor Profile Transfer Honest Audit](https://www.kaggle.com/code/muelsyse111/rogii-neighbor-profile-transfer-honest-audit).
- Detailed evidence: [2026-07-19 results](docs/RESULTS_2026-07-19.md)

## Current validated status (2026-07-18)

- Daily competition submissions: exactly `5 / 5`; no further submission.
- Score-bearing public-source reproductions:
  - [Public rebuild](https://www.kaggle.com/code/muelsyse111/rogii-d18-public-rebuild-7295): `9.571` (`54808956`)
  - [Dual track](https://www.kaggle.com/code/muelsyse111/rogii-d18-dual-track-calibrated): `7.123` (`54808958`)
  - [A04 residual transfer](https://www.kaggle.com/code/muelsyse111/rogii-d18-a04-residual-transfer-repro): `7.010` (`54809311`)
  - [G040/S12](https://www.kaggle.com/code/muelsyse111/rogii-d18-anchor-g040-s12-repro): `7.170` (`54809350`)
  - [Safe rebuild](https://www.kaggle.com/code/muelsyse111/rogii-d18-safe-rebuild-7016-repro): `7.130` (`54809629`)
- New public research notebooks:
  - [Five-Submission Agent Playbook](https://www.kaggle.com/code/muelsyse111/rogii-five-submission-agent-playbook)
  - [Public Route Distance Atlas](https://www.kaggle.com/code/muelsyse111/rogii-public-route-distance-atlas)
  - [Public Artifact Lineage Checklist](https://www.kaggle.com/code/muelsyse111/rogii-public-artifact-lineage-checklist)
- Independent full 773-well particle audit: 65% particle blend RMSE `12.7989`;
  retained as a local floor and not submitted.
- Best public LB: A04 residual transfer at `7.010`, improving the previous
  in-repository best `12.774` by `5.764` RMSE.
- Public rebuild and safe rebuild had byte-identical visible predictions but
  scored `9.571` and `7.130`; hidden execution lineage and fallback behavior
  must be treated as first-class experimental variables.
- Detailed evidence: [2026-07-18 results](docs/RESULTS_2026-07-18.md)
- Agent-ready research queue: [Agent playbook](research/AGENT_PLAYBOOK_2026-07-18.md)

## Current validated status (2026-07-17)

- Public notebook: [ROGII Honest 773 Well Baseline Audit](https://www.kaggle.com/code/muelsyse111/rogii-honest-773-well-baseline-audit)
- Full 773-well true-start CV: `15.9099`; public LB: `15.883`
- Daily submissions used: `2 / 5`; locally resolved weight variants are not submitted
- Particle blend public LB: `12.774` versus anchor `15.883`
- Full 773-well fixed blend on original / disjoint seed sets: `13.1119 / 13.3505`; OOF learned-weight RMSE `13.1544 / 13.3577`
- Private audited submission notebook: [ROGII Private Safe Particle Anchor Blend](https://www.kaggle.com/code/muelsyse111/rogii-private-safe-particle-anchor-blend)
- Detailed evidence: [Results log](docs/RESULTS_2026-07-17.md)
- English post ready for Discussion: [Discussion draft](docs/DISCUSSION_DRAFT_HONEST_BASELINE.md)

Public Code notebooks:

- [Honest 773-well baseline and submission audit](https://www.kaggle.com/code/muelsyse111/rogii-honest-773-well-baseline-audit)
- [Prefix backtest trap: more cuts can hurt](https://www.kaggle.com/code/muelsyse111/rogii-prefix-backtest-trap-more-cuts-can-hurt)
- [Particle filter lab: anchor blending](https://www.kaggle.com/code/muelsyse111/rogii-particle-filter-lab-anchor-blending)
- [True-start failure atlas and tail risk](https://www.kaggle.com/code/muelsyse111/rogii-true-start-failure-atlas-tail-risk)
- [Particle seed independence audit](https://www.kaggle.com/code/muelsyse111/rogii-particle-seed-independence-audit)
- [One coefficient, three RMSE optima](https://www.kaggle.com/code/muelsyse111/rogii-one-coefficient-three-rmse-optima)
- [Typewell GR motif ambiguity atlas](https://www.kaggle.com/code/muelsyse111/rogii-typewell-gr-motif-ambiguity-atlas)
- [Boundary geometry and score concentration](https://www.kaggle.com/code/muelsyse111/rogii-boundary-geometry-score-concentration)
- [Prefix-only GR calibration audit](https://www.kaggle.com/code/muelsyse111/rogii-prefix-only-gr-calibration-audit)

ROGII 前期调研与实验仓库。比赛目标是根据水平井轨迹、Gamma Ray 日志和对应 typewell，预测评估区间每一英尺的 `TVT`；官方指标是逐行 pooled RMSE，越低越好。

- Competition: [ROGII - Wellbore Geology Prediction](https://www.kaggle.com/competitions/rogii-wellbore-geology-prediction)
- Slug: `rogii-wellbore-geology-prediction`
- 资料快照：2026-07-17
- 官方开始：2026-05-05
- 参赛/组队截止：2026-07-29 23:59 UTC（北京时间 2026-07-30 07:59）
- 最终提交截止：2026-08-05 23:59 UTC（北京时间 2026-08-06 07:59）
- 主奖项：$50,000；另有两项 $2,500 Working Note Award，其 2026-07-06 截止日期已过

## 当前结论

这不是普通的逐行表格回归。正确的问题表述是：在最后已知 `TVT_input` 锚点之后，沿井轨迹估计一个平滑但可能漂移、分叉或局部非线性的地层位置状态；`GR` 与 typewell 的 `GR(TVT)` 提供带噪观测，邻井和 formation surface 提供空间先验。

首轮路线：

1. 以 well 为 group 做严格验证，禁止随机 row split。
2. 建立 anchor-hold、线性/低阶轨迹、Ridge/GBM residual 基线。
3. 增加 NCC/DTW、particle filter/beam、HMM smoother 等序列候选。
4. 用多 cut 前缀回测选择每井候选，保存不确定度和失败井画像。
5. 两条独立 pipeline 融合，并通过可见前缀守门任何 per-well override。
6. 最终 Notebook 必须无网络、9 小时内、确定性生成并审计 `submission.csv`。

## 文档

- [官方赛题与规则摘要](docs/COMPETITION_BRIEF.md)
- [数据清单与安全边界](docs/DATA_INVENTORY.md)
- [Code 区调研](research/CODE_REVIEW.md)
- [Discussion 区调研](research/DISCUSSION_REVIEW.md)
- [初始建模与验证策略](research/INITIAL_STRATEGY.md)
- [实验登记表](experiments/EXPERIMENT_LOG.csv)

## 本地开始方式

先在 Kaggle 页面由账号持有人亲自阅读并接受比赛规则。完成后再下载数据；原始数据只能放在被 `.gitignore` 排除的 `data/raw/`：

```powershell
kaggle competitions download -c rogii-wellbore-geology-prediction -p data/raw
```

本仓库不包含、也不应上传任何竞赛 CSV、PNG、PPTX、训练 artifact 或 Kaggle 凭证。

提交前可用纯标准库脚本检查文件结构、ID 顺序、重复项与非有限值：

```powershell
python scripts/verify_submission.py data/raw/sample_submission.csv submission.csv
python -m unittest discover -s tests -v
```

## 合规提醒

竞赛数据许可为 Competition use only。比赛期间不得在队伍外私下共享竞赛代码；若公开分享竞赛代码，应同时遵守官方规则中关于 Kaggle Competition Code/Discussion 和 OSI 许可证的要求。外部数据与模型必须公开、合理可获得，并保留来源和许可证证据。
