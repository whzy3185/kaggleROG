from scripts.audit_kaggle_submission_outcomes import classify


def test_public_score_is_the_only_success_signal():
    assert classify({"status": "COMPLETE", "publicScore": "6.455"}) == "scored"


def test_complete_with_error_is_failed():
    assert (
        classify(
            {
                "status": "COMPLETE",
                "publicScore": None,
                "errorDescription": "hidden rerun failed",
            }
        )
        == "failed"
    )


def test_scoreless_errorless_submission_is_pending():
    assert classify({"status": None, "publicScore": None}) == "pending"
