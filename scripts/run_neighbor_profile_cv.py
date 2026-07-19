#!/usr/bin/env python3
"""Leave-one-well-out CV for legal nearest-well trajectory-shape transfer."""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
GRID = np.linspace(0.0, 1.0, 201)


@dataclass
class WellProfile:
    well_id: str
    centroid: np.ndarray
    direction: np.ndarray
    path_xy: np.ndarray
    delta_tvt: np.ndarray
    eval_q: np.ndarray
    eval_z: np.ndarray
    eval_truth: np.ndarray
    anchor_tvt: float


def _well_id(path: Path) -> str:
    return path.name.removesuffix("__horizontal_well.csv")


def _normalized_axis(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    span = float(values[-1] - values[0])
    if not np.isfinite(span) or abs(span) < 1e-9:
        return np.linspace(0.0, 1.0, len(values))
    return (values - values[0]) / span


def _interp_grid(q: np.ndarray, values: np.ndarray) -> np.ndarray:
    q = np.asarray(q, dtype=float)
    values = np.asarray(values, dtype=float)
    valid = np.isfinite(q) & np.isfinite(values)
    if int(valid.sum()) < 2:
        raise ValueError("profile requires at least two finite points")
    q_valid = q[valid]
    values_valid = values[valid]
    order = np.argsort(q_valid)
    q_valid = q_valid[order]
    values_valid = values_valid[order]
    q_valid, unique = np.unique(q_valid, return_index=True)
    values_valid = values_valid[unique]
    return np.interp(GRID, q_valid, values_valid)


def load_profile(path: Path) -> WellProfile:
    frame = pd.read_csv(
        path,
        usecols=["MD", "X", "Y", "Z", "TVT", "TVT_input"],
    )
    missing = np.flatnonzero(frame["TVT_input"].isna().to_numpy())
    if not len(missing):
        raise ValueError(f"{path.name}: no evaluation suffix")
    boundary = int(missing[0])
    if boundary < 2 or len(frame) - boundary < 20:
        raise ValueError(f"{path.name}: unusable prefix/suffix")

    anchor_row = boundary - 1
    anchor_tvt = float(frame.loc[anchor_row, "TVT_input"])
    eval_frame = frame.iloc[boundary:]
    eval_q = _normalized_axis(eval_frame["MD"].to_numpy(dtype=float))
    eval_z = eval_frame["Z"].to_numpy(dtype=float)
    eval_truth = eval_frame["TVT"].to_numpy(dtype=float)
    delta_q = np.concatenate([[0.0], eval_q])
    delta_tvt = np.concatenate([[0.0], eval_truth - anchor_tvt])
    delta_tvt_grid = _interp_grid(delta_q, delta_tvt)

    path_x = _interp_grid(eval_q, eval_frame["X"].to_numpy(dtype=float))
    path_y = _interp_grid(eval_q, eval_frame["Y"].to_numpy(dtype=float))
    path_xy = np.column_stack([path_x, path_y])
    vector = path_xy[-1] - path_xy[0]
    norm = float(np.linalg.norm(vector))
    direction = vector / norm if norm > 1e-9 else np.array([0.0, 0.0])

    return WellProfile(
        well_id=_well_id(path),
        centroid=np.nanmean(path_xy, axis=0),
        direction=direction,
        path_xy=path_xy,
        delta_tvt=delta_tvt_grid,
        eval_q=eval_q,
        eval_z=eval_z,
        eval_truth=eval_truth,
        anchor_tvt=anchor_tvt,
    )


def _path_distance(left: WellProfile, right: WellProfile) -> float:
    distance = np.linalg.norm(left.path_xy - right.path_xy, axis=1)
    return float(np.nanmedian(distance))


def _candidate_donors(
    target_index: int,
    profiles: list[WellProfile],
    centroids: np.ndarray,
    *,
    prefilter: int,
    direction_cosine: float,
) -> list[tuple[int, float]]:
    target = profiles[target_index]
    centroid_distance = np.linalg.norm(centroids - target.centroid, axis=1)
    order = np.argsort(centroid_distance)
    candidates: list[tuple[int, float]] = []
    for donor_index in order:
        if donor_index == target_index:
            continue
        donor = profiles[int(donor_index)]
        cosine = float(np.dot(target.direction, donor.direction))
        if cosine < direction_cosine:
            continue
        candidates.append((int(donor_index), _path_distance(target, donor)))
        if len(candidates) >= prefilter:
            break
    return sorted(candidates, key=lambda item: item[1])


def _blend_donor_shape(
    target: WellProfile,
    donors: list[tuple[WellProfile, float]],
) -> np.ndarray:
    distances = np.array([distance for _, distance in donors], dtype=float)
    weights = 1.0 / np.maximum(distances, 25.0) ** 2
    weights /= weights.sum()
    donor_delta_tvt = np.stack([profile.delta_tvt for profile, _ in donors])
    delta_tvt_grid = weights @ donor_delta_tvt
    delta_tvt = np.interp(target.eval_q, GRID, delta_tvt_grid)
    return target.anchor_tvt + delta_tvt


def evaluate(
    train_dir: Path,
    *,
    thresholds: list[float],
    blends: list[float],
    max_donors: int,
    prefilter: int,
    direction_cosine: float,
    limit: int | None,
) -> tuple[pd.DataFrame, dict[str, dict[str, float | int]]]:
    paths = sorted(train_dir.glob("*__horizontal_well.csv"))
    if limit is not None:
        paths = paths[:limit]
    profiles: list[WellProfile] = []
    for number, path in enumerate(paths, start=1):
        try:
            profiles.append(load_profile(path))
        except ValueError as error:
            print(f"skip {path.name}: {error}", flush=True)
        if number % 100 == 0 or number == len(paths):
            print(f"loaded {number}/{len(paths)} wells", flush=True)
    if len(profiles) < 2:
        raise RuntimeError("neighbor CV requires at least two usable wells")

    centroids = np.stack([profile.centroid for profile in profiles])
    rows: list[dict[str, float | int | str]] = []
    for target_index, target in enumerate(profiles):
        candidates = _candidate_donors(
            target_index,
            profiles,
            centroids,
            prefilter=prefilter,
            direction_cosine=direction_cosine,
        )
        anchor_prediction = np.full_like(target.eval_truth, target.anchor_tvt)
        nearest_distance = candidates[0][1] if candidates else math.inf
        nearest_id = profiles[candidates[0][0]].well_id if candidates else ""

        for threshold in thresholds:
            selected = [
                (profiles[index], distance)
                for index, distance in candidates
                if distance <= threshold
            ][:max_donors]
            if selected:
                transfer = _blend_donor_shape(target, selected)
            else:
                transfer = anchor_prediction
            for blend in blends:
                prediction = (1.0 - blend) * anchor_prediction + blend * transfer
                error = prediction - target.eval_truth
                sse = float(np.dot(error, error))
                rows.append(
                    {
                        "well_id": target.well_id,
                        "threshold": float(threshold),
                        "blend": float(blend),
                        "n_donors": len(selected),
                        "nearest_well": nearest_id,
                        "nearest_path_distance": float(nearest_distance),
                        "n_eval": len(error),
                        "rmse": math.sqrt(sse / len(error)),
                        "sse": sse,
                    }
                )
        if (target_index + 1) % 100 == 0 or target_index + 1 == len(profiles):
            print(f"evaluated {target_index + 1}/{len(profiles)} wells", flush=True)

    detail = pd.DataFrame(rows)
    summary: dict[str, dict[str, float | int]] = {}
    for (threshold, blend), group in detail.groupby(["threshold", "blend"], sort=True):
        rows_scored = int(group["n_eval"].sum())
        key = f"distance_{threshold:g}/blend_{blend:g}"
        moved = group["n_donors"] > 0
        summary[key] = {
            "wells": int(len(group)),
            "moved_wells": int(moved.sum()),
            "coverage": float(moved.mean()),
            "rows": rows_scored,
            "pooled_rmse": math.sqrt(float(group["sse"].sum()) / rows_scored),
            "macro_rmse": float(group["rmse"].mean()),
            "median_rmse": float(group["rmse"].median()),
            "p90_rmse": float(group["rmse"].quantile(0.90)),
            "p95_rmse": float(group["rmse"].quantile(0.95)),
            "worst_rmse": float(group["rmse"].max()),
        }
    return detail, summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--train-dir",
        type=Path,
        default=REPO_ROOT / "data" / "raw" / "competition" / "train",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=REPO_ROOT / "artifacts" / "neighbor_profile_cv",
    )
    parser.add_argument("--thresholds", type=float, nargs="+", default=[150, 300, 600])
    parser.add_argument("--blends", type=float, nargs="+", default=[0.25, 0.5, 0.75, 1.0])
    parser.add_argument("--max-donors", type=int, default=3)
    parser.add_argument("--prefilter", type=int, default=30)
    parser.add_argument("--direction-cosine", type=float, default=0.0)
    parser.add_argument("--limit", type=int)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if any(threshold <= 0 for threshold in args.thresholds):
        raise ValueError("distance thresholds must be positive")
    if any(not 0.0 <= blend <= 1.0 for blend in args.blends):
        raise ValueError("blend weights must be between zero and one")
    if args.max_donors < 1 or args.prefilter < args.max_donors:
        raise ValueError("prefilter must be at least max-donors")
    if not -1.0 <= args.direction_cosine <= 1.0:
        raise ValueError("direction cosine must be between -1 and one")

    detail, summary = evaluate(
        args.train_dir,
        thresholds=args.thresholds,
        blends=args.blends,
        max_donors=args.max_donors,
        prefilter=args.prefilter,
        direction_cosine=args.direction_cosine,
        limit=args.limit,
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    detail.to_csv(args.output_dir / "neighbor_profile_detail.csv", index=False)
    (args.output_dir / "neighbor_profile_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    table = pd.DataFrame.from_dict(summary, orient="index").sort_values(
        ["pooled_rmse", "p95_rmse"]
    )
    print(table.to_string(float_format=lambda value: f"{value:.4f}"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
