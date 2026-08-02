# Kaggle submission failure audit - 2026-08-01

## Correction

The earlier workflow incorrectly treated a successful public/private Code run
and a competition submission with status `COMPLETE` as sufficient evidence of
a valid result. Kaggle exposes the decisive field separately:
`errorDescription`. A submission is valid only when it has a real
`publicScore`; `COMPLETE` with an error is a failed hidden rerun.

At this checkpoint the account has 77 ROGII submissions:

- 61 scored submissions;
- 13 confirmed failures;
- 3 D32 submissions still pending without a score or error.

## Confirmed failures

| Date | Refs | Failure reported by Kaggle |
|---|---|---|
| 2026-07-23 | `54918138` | hidden rerun exceeded the runtime limit |
| 2026-07-25 | `54966407` | hidden rerun exceeded the runtime limit |
| 2026-07-26 | `54988991` | hidden rerun exceeded the runtime limit |
| 2026-07-28 | `55048063 / 55048532` | hidden rerun exceeded the runtime limit |
| 2026-07-30 | `55097369 / 55098546` | submission file had incorrect hidden-run format |
| 2026-07-31 | `55129144 / 55129811 / 55130546 / 55131268` | unhandled error during hidden rerun |
| 2026-08-01 | `55161568 / 55162186` | unhandled error during hidden rerun |

D32 refs `55159859 / 55160477 / 55161022` remain pending. They are not counted
as successful and must not be described as completed experiments until a real
score appears.

## Root cause

The public Code versions ran against the three visible test wells and produced
14,151-row files. Several later post-processing notebooks then treated those
visible files as immutable parents, required exactly 14,151 rows and fixed
public IDs, and used their full file SHA-256 values as runtime contracts.

That contract is valid only for the visible Code run. During competition
scoring Kaggle reruns the notebook against a hidden dataset that can have a
different number of wells, rows, and IDs. The static D30 route emitted a file
with the wrong hidden format. The stricter D31/D32 routes failed earlier by
raising their own parent/ID contract exceptions. Public output auditing did
not test hidden-data scalability.

The runtime failures are the same deployment-parity issue in a different form:
notebooks that fit within the visible run exceeded the hidden-run time limit.

The evidence levels are deliberately separated:

- The five runtime-limit messages and two incorrect-format messages are exact
  Kaggle diagnoses.
- Kaggle exposes only a generic hidden-rerun error for the six unhandled-error
  refs, so the precise failing line is not available. The fixed-parent,
  fixed-public-ID design is the shared deployment defect and the leading root
  cause, not a claimed hidden traceback.
- The monitoring defect is exact: the workflow accepted `COMPLETE` without
  checking that `publicScore` was non-empty and `errorDescription` was empty.

## Fail-closed implementation

`scripts/preflight_competition_submission.py` now rejects a candidate unless
all of the following hold:

1. it is a private, offline GPU Code version with the competition mounted;
2. it contains a pre-model competition-mount check and validates the run-local
   sample. A fixed contract inherited unchanged from a source lineage that has
   already produced a real score is allowed; adding a new public-only row/ID
   contract is not;
3. it may read other notebooks and their `submission.csv` files during local
   research, reproduction checks, scoring analysis, and candidate design. In
   the submitted competition notebook, however, a visible public
   `submission.csv` cannot be used as the hidden prediction parent: the
   underlying method must be rerun dynamically. `kernel_sources` are allowed
   when they provide reusable models or other hidden-data-independent
   artifacts;
4. expensive CV paths are disabled and the measured D29 runtime caps are not
   exceeded;
5. its executable cells match the scored D29 lineage after only the declared
   weight, proportional clip, route-label, dynamic-audit, and preflight edits;
6. the downloaded output matches sample ID order, finite-value rules, its own
   audit SHA-256 values, and a clean execution log.

`scripts/submit_code_version.py` now requires the passing gate report. Before
it can create a ref, it re-downloads the current private source and output and
requires byte-identical hashes, refuses while any earlier ref is unresolved,
stops the day after any failed ref, enforces the five-ref budget and a minimum
30-minute interval, and defaults to a dry run unless `--execute` is explicit.

The initial gate incorrectly quarantined the completed 25% and 30% versions
solely because they inherited a row-count constant from the already-scored D29
source. That was too broad and was corrected on 2026-08-02. The real boundary
is whether a new visible-only contract or a visible parent output is introduced.
A fresh hardened private version must still pass the corrected gate.

## Mandatory rule from now on

1. Read `publicScore`, `status`, `totalBytes`, and `errorDescription` from the
   competition submission object after every ref.
2. Never call a ref successful because the source Code version is complete.
3. Never call `COMPLETE` successful when `errorDescription` is non-empty or
   `publicScore` is empty.
4. Reading public outputs for research is allowed and expected. Do not
   competition-submit a notebook that consumes a fixed public
   `submission.csv`, fixed public IDs, fixed public row count, or public-output
   SHA as its hidden-run parent.
5. Full-source notebooks must discover hidden wells dynamically and validate
   against the run-local sample submission, without a literal 14,151-row
   assertion.
6. Runtime must be projected from visible well count to the hidden workload
   before a slot is used.
7. Never bypass the gate script or call Kaggle's submission API directly. If
   any check is uncertain or the platform cannot be verified, use no slot.
