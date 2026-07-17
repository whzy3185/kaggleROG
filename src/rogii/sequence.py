"""A compact first-order GR/typewell HMM smoother.

This implementation is intentionally independent and modest: it calibrates the
typewell GR curve on the visible prefix, tracks TVT on a bounded grid, and uses
forward-backward smoothing over the complete hidden-zone GR sequence.  It is a
research candidate, not an assertion that a public leaderboard recipe transfers
to the private test set.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class HMMConfig:
    step: float = 0.5
    half_width: float = 140.0
    position_sigma: float = 0.32
    drift_window: int = 300
    max_abs_drift: float = 0.02
    emission_scale: float = 1.0
    min_gr_sigma: float = 10.0
    max_gr_sigma: float = 45.0


@dataclass(frozen=True)
class HMMDiagnostics:
    gr_gain: float
    gr_offset: float
    gr_sigma: float
    drift: float
    mean_posterior_std: float
    max_edge_mass: float


def _boundary(frame: pd.DataFrame, cut_index: int | None) -> int:
    if cut_index is not None:
        if not 2 <= cut_index < len(frame):
            raise ValueError("cut_index must leave at least two prefix rows and one eval row")
        return int(cut_index)
    missing = np.flatnonzero(frame["TVT_input"].isna().to_numpy())
    if not len(missing) or missing[0] == 0:
        raise ValueError("TVT_input must contain a visible prefix and missing suffix")
    boundary = int(missing[0])
    if frame["TVT_input"].iloc[boundary:].notna().any():
        raise ValueError("TVT_input missing values must be a contiguous suffix")
    return boundary


def _fit_affine(expected: np.ndarray, observed: np.ndarray) -> tuple[float, float, float]:
    mask = np.isfinite(expected) & np.isfinite(observed)
    x = expected[mask]
    y = observed[mask]
    if len(x) < 20:
        return 1.0, 0.0, 30.0

    keep = np.ones(len(x), dtype=bool)
    gain, offset = 1.0, 0.0
    for _ in range(4):
        design = np.column_stack((x[keep], np.ones(int(keep.sum()))))
        gain, offset = np.linalg.lstsq(design, y[keep], rcond=None)[0]
        gain = float(np.clip(gain, 0.35, 2.5))
        offset = float(np.median(y[keep] - gain * x[keep]))
        residual = y - (gain * x + offset)
        center = float(np.median(residual[keep]))
        mad = float(1.4826 * np.median(np.abs(residual[keep] - center)))
        if mad <= 1e-6:
            break
        new_keep = np.abs(residual - center) <= 3.5 * mad
        if new_keep.sum() < 20 or np.array_equal(new_keep, keep):
            break
        keep = new_keep

    residual = y - (gain * x + offset)
    sigma = float(1.4826 * np.median(np.abs(residual - np.median(residual))))
    return gain, offset, sigma


def _linear_slope(x: np.ndarray, y: np.ndarray, window: int) -> float:
    x = x[-window:]
    y = y[-window:]
    centered = x - x.mean()
    denominator = float(np.dot(centered, centered))
    if denominator <= 1e-12:
        return 0.0
    return float(np.dot(centered, y - y.mean()) / denominator)


def _diffuse(values: np.ndarray, q: float) -> np.ndarray:
    if q <= 0.0:
        return values
    result = (1.0 - 2.0 * q) * values.copy()
    result[1:] += q * values[:-1]
    result[:-1] += q * values[1:]
    # Reflect rather than lose probability at the physical state-grid edge.
    result[0] += q * values[0]
    result[-1] += q * values[-1]
    return result


def _forward_transition(
    values: np.ndarray,
    grid_index: np.ndarray,
    shift_steps: float,
    q: float,
) -> np.ndarray:
    shifted = np.interp(grid_index - shift_steps, grid_index, values, left=0.0, right=0.0)
    return _diffuse(shifted, q)


def _backward_transition(
    values: np.ndarray,
    grid_index: np.ndarray,
    shift_steps: float,
    q: float,
) -> np.ndarray:
    diffused = _diffuse(values, q)
    return np.interp(grid_index + shift_steps, grid_index, diffused, left=0.0, right=0.0)


def predict_gr_hmm(
    frame: pd.DataFrame,
    typewell: pd.DataFrame,
    *,
    config: HMMConfig = HMMConfig(),
    cut_index: int | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, HMMDiagnostics]:
    """Return eval indices, posterior-mean TVT, posterior std, and diagnostics."""

    required_hw = {"MD", "GR", "TVT_input"}
    if cut_index is not None:
        required_hw.add("TVT")
    required_tw = {"TVT", "GR"}
    if missing := required_hw.difference(frame.columns):
        raise ValueError(f"Horizontal well is missing columns: {sorted(missing)!r}")
    if missing := required_tw.difference(typewell.columns):
        raise ValueError(f"Typewell is missing columns: {sorted(missing)!r}")
    if config.step <= 0 or config.half_width <= config.step:
        raise ValueError("Invalid state-grid configuration")

    boundary = _boundary(frame, cut_index)
    known_column = "TVT" if cut_index is not None else "TVT_input"
    known_tvt = frame[known_column].to_numpy(dtype=float, copy=False)[:boundary]
    md = frame["MD"].to_numpy(dtype=float, copy=False)
    horizontal_gr = frame["GR"].to_numpy(dtype=float, copy=False)
    tw = typewell[["TVT", "GR"]].dropna().sort_values("TVT")
    tw_tvt = tw["TVT"].to_numpy(dtype=float, copy=False)
    tw_gr = tw["GR"].to_numpy(dtype=float, copy=False)
    if len(tw_tvt) < 3 or np.any(np.diff(tw_tvt) <= 0):
        raise ValueError("Typewell TVT grid must be finite, sorted, and unique")

    expected_prefix_gr = np.interp(known_tvt, tw_tvt, tw_gr)
    gain, offset, raw_sigma = _fit_affine(expected_prefix_gr, horizontal_gr[:boundary])
    gr_sigma = float(np.clip(raw_sigma, config.min_gr_sigma, config.max_gr_sigma))
    expected_hgr = gain * tw_gr + offset

    anchor = float(known_tvt[-1])
    lower = max(float(tw_tvt[0]), anchor - config.half_width)
    upper = min(float(tw_tvt[-1]), anchor + config.half_width)
    grid = np.arange(lower, upper + 0.5 * config.step, config.step, dtype=float)
    if len(grid) < 5:
        raise ValueError("Typewell does not cover a sufficient TVT range around the anchor")
    grid_index = np.arange(len(grid), dtype=float)
    grid_expected_hgr = np.interp(grid, tw_tvt, expected_hgr)

    drift = _linear_slope(md[:boundary], known_tvt, config.drift_window)
    drift = float(np.clip(drift, -config.max_abs_drift, config.max_abs_drift))
    eval_indices = np.arange(boundary, len(frame), dtype=int)
    n_eval = len(eval_indices)
    forward = np.empty((n_eval, len(grid)), dtype=np.float32)
    shifts = np.empty(n_eval, dtype=float)
    qs = np.empty(n_eval, dtype=float)

    start = np.exp(-0.5 * ((grid - anchor) / max(0.35, config.step)) ** 2)
    start /= start.sum()
    previous = start
    max_edge_mass = 0.0
    previous_md = md[boundary - 1]
    for row, index in enumerate(eval_indices):
        delta_md = max(float(md[index] - previous_md), 0.0)
        shifts[row] = drift * delta_md / config.step
        variance = config.position_sigma**2 * max(delta_md, 1e-6)
        qs[row] = min(0.45, 0.5 * variance / (config.step**2))
        prior = _forward_transition(previous, grid_index, shifts[row], qs[row])
        if np.isfinite(horizontal_gr[index]):
            scaled = (horizontal_gr[index] - grid_expected_hgr) / gr_sigma
            likelihood = np.exp(np.clip(-0.5 * config.emission_scale * scaled * scaled, -50.0, 0.0))
            current = prior * likelihood
        else:
            current = prior
        total = float(current.sum())
        if total <= 1e-30 or not np.isfinite(total):
            current = prior
            total = float(current.sum())
        current /= total
        forward[row] = current
        edge_mass = float(current[:3].sum() + current[-3:].sum())
        max_edge_mass = max(max_edge_mass, edge_mass)
        previous = current
        previous_md = md[index]

    prediction = np.empty(n_eval, dtype=float)
    posterior_std = np.empty(n_eval, dtype=float)
    beta = np.ones(len(grid), dtype=float)
    beta /= beta.sum()
    for row in range(n_eval - 1, -1, -1):
        posterior = forward[row].astype(float) * beta
        posterior /= posterior.sum()
        mean = float(np.dot(posterior, grid))
        prediction[row] = mean
        posterior_std[row] = float(np.sqrt(np.dot(posterior, (grid - mean) ** 2)))
        if row > 0:
            index = eval_indices[row]
            if np.isfinite(horizontal_gr[index]):
                scaled = (horizontal_gr[index] - grid_expected_hgr) / gr_sigma
                likelihood = np.exp(
                    np.clip(-0.5 * config.emission_scale * scaled * scaled, -50.0, 0.0)
                )
                weighted = beta * likelihood
            else:
                weighted = beta
            beta = _backward_transition(weighted, grid_index, shifts[row], qs[row])
            total = float(beta.sum())
            beta = beta / total if total > 1e-30 and np.isfinite(total) else np.ones(len(grid)) / len(grid)

    diagnostics = HMMDiagnostics(
        gr_gain=gain,
        gr_offset=offset,
        gr_sigma=gr_sigma,
        drift=drift,
        mean_posterior_std=float(posterior_std.mean()),
        max_edge_mass=max_edge_mass,
    )
    return eval_indices, prediction, posterior_std, diagnostics
