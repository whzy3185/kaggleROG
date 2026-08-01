"""Report real Kaggle submission outcomes, including hidden-rerun failures."""

from __future__ import annotations

import argparse
import json
from collections import Counter

from kaggle.api.kaggle_api_extended import KaggleApi


def classify(record: dict) -> str:
    if record.get("publicScore") not in (None, ""):
        return "scored"
    if record.get("errorDescription"):
        return "failed"
    return "pending"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--competition", default="rogii-wellbore-geology-prediction"
    )
    parser.add_argument("--page-size", type=int, default=200)
    parser.add_argument("--date-from", default="")
    args = parser.parse_args()

    api = KaggleApi()
    api.authenticate()
    submissions = api.competition_submissions(
        args.competition, page_size=args.page_size
    )
    rows = []
    for submission in submissions:
        record = submission.to_dict()
        date = str(record.get("date", ""))[:10]
        if args.date_from and date < args.date_from:
            continue
        rows.append(
            {
                "date": date,
                "ref": int(record["ref"]),
                "outcome": classify(record),
                "status": record.get("status"),
                "public_score": record.get("publicScore"),
                "total_bytes": record.get("totalBytes"),
                "error": record.get("errorDescription"),
                "url": record.get("url"),
            }
        )

    rows.sort(key=lambda row: row["ref"], reverse=True)
    print(
        json.dumps(
            {"counts": Counter(row["outcome"] for row in rows), "rows": rows},
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
