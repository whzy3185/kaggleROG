"""Submit one audited Kaggle Code version to a notebook-only competition."""

from __future__ import annotations

import argparse
import json

from kaggle.api.kaggle_api_extended import KaggleApi


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--competition", required=True)
    parser.add_argument("--kernel", required=True, help="owner/slug")
    parser.add_argument("--version", type=int, required=True)
    parser.add_argument("--file", default="submission.csv")
    parser.add_argument("--message", required=True)
    args = parser.parse_args()

    api = KaggleApi()
    api.authenticate()
    response = api.competition_submit_code(
        file_name=args.file,
        message=args.message,
        competition=args.competition,
        kernel=args.kernel,
        kernel_version=args.version,
        quiet=True,
    )
    result = {
        "ref": int(response.ref),
        "message": str(response.message or ""),
        "competition": args.competition,
        "kernel": args.kernel,
        "kernel_version": args.version,
        "file": args.file,
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
