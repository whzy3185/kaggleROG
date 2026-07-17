"""Deterministic, target-safe baselines for suffix TVT prediction.

The structural state ``U = TVT + Z`` separates the well trajectory from the
slowly varying geological surface.  Every estimator below uses only the TVT
prefix visible before the prediction boundary.
"""

from __future__ import annotations

from collections.abc import Mapping

import numpy as np
import pandas as pd


_CANDIDATES = (
    "anchor",
    "u_hold",
    "u_linear_30",
    "u_linear_100",
    "u_linear_300",
    "u_linear_all",
    "u_shrunk_100",
    "u_shrunk_300",
)


def candidate_names() -> tuple[str, ...]:
    """Return the stable list of implemented baseline names."""

    return _CANDIDATES


def _prediction_boundary(frame: pd.DataFrame, cut_index: int | None) -> int:
    n_rows = len(frame)
    if n_rows < 2:
        raise ValueError("A well must contain at least two rows")

    if cut_index is not None:
        if not 1 <= cut_index < n_rows:
            raise ValueError(f"cut_index must be in [1, {n_rows - 1}], got {cut_index}")
        return int(cut_index)

    observed = frame["TVT_input"].notna().to_numpy()
    missing = np.flatnonzero(~observed)
    if not len(missing):
        raise ValueError("TVT_input has no missing suffix")
    boundary = int(missing[0])
    if boundary == 0:
        raise ValueError("TVT_input has no visible prefix")
    if observed[boundary:].any():
        raise ValueError("TVT_input missing values must form one contiguous suffix")
    return boundary


def _known_tvt(frame: pd.DataFrame, boundary: int, synthetic_cut: bool) -> np.ndarray:
    column = "TVT" if synthetic_cut else "TVT_input"
    values = frame[column].to_numpy(dtype=float, copy=False)[:boundary]
    if not np.isfinite(values).all():
        raise ValueError(f"{column} contains non-finite values in the visible prefix")
    return values


def _tail_linear_slope(x: np.ndarray, y: np.ndarray, window: int | None) -> float:
    if window is not None:
        x = x[-window:]
        y = y[-window:]
    if len(x) < 2:
        return 0.0
    x_centered = x - x.mean()
    denominator = float(np.dot(x_centered, x_centered))
    if denominator <= 1e-12:
        return 0.0
    return float(np.dot(x_centered, y - y.mean()) / denominator)


def _candidate_slopes(md: np.ndarray, u: np.ndarray) -> Mapping[str, float]:
    raw = {
        "u_linear_30": _tail_linear_slope(md, u, 30),
        "u_linear_100": _tail_linear_slope(md, u, 100),
        "u_linear_300": _tail_linear_slope(md, u, 300),
        "u_linear_all": _tail_linear_slope(md, u, None),
    }
    # A deliberately broad physical guard prevents a single unstable prefix
    # fit from exploding over a long suffix. The value is not LB-tuned.
    return {name: float(np.clip(value, -0.25, 0.25)) for name, value in raw.items()}


def predict_suffix(
    frame: pd.DataFrame,
    candidate: str,
    *,
    cut_index: int | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Predict a well suffix and return ``(row_indices, predictions)``.

    When ``cut_index`` is supplied, the function simulates a synthetic prefix
    using the full training target only before the cut. This is intended for
    local backtesting and must never be used on competition test data.
    """

    if candidate not in _CANDIDATES:
        raise ValueError(f"Unknown candidate {candidate!r}; choose from {_CANDIDATES!r}")
    required = {"MD", "Z", "TVT_input"}
    if cut_index is not None:
        required.add("TVT")
    missing_columns = required.difference(frame.columns)
    if missing_columns:
        raise ValueError(f"Missing columns: {sorted(missing_columns)!r}")

    boundary = _prediction_boundary(frame, cut_index)
    known_tvt = _known_tvt(frame, boundary, synthetic_cut=cut_index is not None)
    md = frame["MD"].to_numpy(dtype=float, copy=False)
    z = frame["Z"].to_numpy(dtype=float, copy=False)
    if not np.isfinite(md).all() or not np.isfinite(z).all():
        raise ValueError("MD and Z must be finite")

    eval_indices = np.arange(boundary, len(frame), dtype=int)
    anchor_tvt = float(known_tvt[-1])
    if candidate == "anchor":
        return eval_indices, np.full(len(eval_indices), anchor_tvt, dtype=float)

    known_u = known_tvt + z[:boundary]
    anchor_u = float(known_u[-1])
    if candidate == "u_hold":
        return eval_indices, anchor_u - z[boundary:]

    slopes = _candidate_slopes(md[:boundary], known_u)
    if candidate.startswith("u_linear_"):
        slope = slopes[candidate]
    elif candidate == "u_shrunk_100":
        slope = 0.35 * slopes["u_linear_100"]
    elif candidate == "u_shrunk_300":
        slope = 0.35 * slopes["u_linear_300"]
    else:  # Defensive: all public candidate names are handled above.
        raise AssertionError(candidate)

    predicted_u = anchor_u + slope * (md[boundary:] - md[boundary - 1])
    return eval_indices, predicted_u - z[boundary:]
