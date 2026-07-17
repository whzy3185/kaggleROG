"""Deterministic multi-seed particle tracking for GR-guided TVT prediction."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class ParticleConfig:
    particles: int = 400
    seeds: int = 16
    likelihood_temperature: float = 5.0
    initial_u_sigma: float = 4.5
    initial_rate_sigma: float = 0.01
    rate_momentum: float = 0.998
    rate_noise: float = 0.002
    position_noise: float = 0.005
    position_roughening: float = 0.10
    rate_roughening: float = 0.001
    resample_fraction: float = 0.50
    min_gr_sigma: float = 10.0
    max_gr_sigma: float = 60.0


@dataclass(frozen=True)
class ParticleDiagnostics:
    gr_gain: float
    gr_offset: float
    gr_sigma: float
    initial_rate: float
    effective_seed_count: float
    best_seed_weight: float


def _boundary(frame: pd.DataFrame, cut_index: int | None) -> int:
    if cut_index is not None:
        if not 2 <= cut_index < len(frame):
            raise ValueError("cut_index must leave a visible prefix and evaluation suffix")
        return int(cut_index)
    observed = frame["TVT_input"].notna().to_numpy()
    missing = np.flatnonzero(~observed)
    if not len(missing) or missing[0] < 2 or observed[missing[0] :].any():
        raise ValueError("TVT_input must have a visible prefix and contiguous missing suffix")
    return int(missing[0])


def _calibrate_gr(
    expected: np.ndarray,
    observed: np.ndarray,
    minimum_sigma: float,
    maximum_sigma: float,
) -> tuple[float, float, float]:
    mask = np.isfinite(expected) & np.isfinite(observed)
    x = expected[mask]
    y = observed[mask]
    if len(x) < 20:
        return 1.0, 0.0, 30.0
    keep = np.ones(len(x), dtype=bool)
    gain, offset = 1.0, 0.0
    for _ in range(3):
        design = np.column_stack((x[keep], np.ones(int(keep.sum()))))
        gain, offset = np.linalg.lstsq(design, y[keep], rcond=None)[0]
        gain = float(np.clip(gain, 0.35, 2.5))
        offset = float(np.median(y[keep] - gain * x[keep]))
        residual = y - (gain * x + offset)
        mad = float(1.4826 * np.median(np.abs(residual[keep] - np.median(residual[keep]))))
        if mad <= 1e-8:
            break
        new_keep = np.abs(residual - np.median(residual[keep])) <= 3.5 * mad
        if new_keep.sum() < 20 or np.array_equal(new_keep, keep):
            break
        keep = new_keep
    residual = y - (gain * x + offset)
    sigma = float(1.4826 * np.median(np.abs(residual - np.median(residual))))
    return gain, offset, float(np.clip(sigma, minimum_sigma, maximum_sigma))


def _initial_rate(md: np.ndarray, z: np.ndarray, tvt: np.ndarray, window: int = 30) -> float:
    md = md[-window:]
    u = (tvt + z[-len(tvt) :])[-window:]
    delta_md = np.diff(md)
    valid = delta_md > 0
    if valid.sum() < 3:
        return 0.0
    rates = np.diff(u)[valid] / delta_md[valid]
    return float(np.clip(np.median(rates), -0.25, 0.25))


def _systematic_resample(weights: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    cumulative = np.cumsum(weights)
    cumulative[-1] = 1.0
    positions = rng.uniform(0.0, 1.0 / len(weights)) + np.arange(len(weights)) / len(weights)
    return np.searchsorted(cumulative, positions, side="left")


def _run_seed(
    *,
    seed: int,
    md_eval: np.ndarray,
    z_eval: np.ndarray,
    gr_eval: np.ndarray,
    previous_md: float,
    anchor_u: float,
    initial_rate: float,
    tw_tvt: np.ndarray,
    expected_hgr: np.ndarray,
    gr_sigma: float,
    config: ParticleConfig,
) -> tuple[np.ndarray, float]:
    rng = np.random.default_rng(seed)
    n = config.particles
    u = anchor_u + config.initial_u_sigma * rng.standard_normal(n)
    rate = initial_rate + config.initial_rate_sigma * rng.standard_normal(n)
    weights = np.full(n, 1.0 / n, dtype=float)
    prediction = np.empty(len(md_eval), dtype=float)
    log_evidence = 0.0

    for row in range(len(md_eval)):
        delta_md = max(float(md_eval[row] - previous_md), 1.0)
        rate = config.rate_momentum * rate + config.rate_noise * rng.standard_normal(n)
        u = u + rate * delta_md + config.position_noise * rng.standard_normal(n)
        particle_tvt = u - z_eval[row]
        particle_tvt = np.clip(particle_tvt, tw_tvt[0] - 100.0, tw_tvt[-1] + 100.0)
        u = particle_tvt + z_eval[row]

        if np.isfinite(gr_eval[row]):
            expected = np.interp(particle_tvt, tw_tvt, expected_hgr)
            scaled = (gr_eval[row] - expected) / gr_sigma
            likelihood = np.exp(np.clip(-0.5 * scaled * scaled, -50.0, 0.0))
            evidence = float(np.dot(weights, likelihood))
            log_evidence += np.log(max(evidence, 1e-300))
            weights *= likelihood
            total = float(weights.sum())
            weights = weights / total if total > 1e-300 else np.full(n, 1.0 / n)

        effective = 1.0 / float(np.dot(weights, weights))
        if effective < config.resample_fraction * n:
            selected = _systematic_resample(weights, rng)
            u = u[selected] + config.position_roughening * rng.standard_normal(n)
            rate = rate[selected] + config.rate_roughening * rng.standard_normal(n)
            weights.fill(1.0 / n)
        prediction[row] = float(np.dot(weights, u - z_eval[row]))
        previous_md = md_eval[row]
    return prediction, log_evidence


def predict_particle_ensemble(
    frame: pd.DataFrame,
    typewell: pd.DataFrame,
    *,
    config: ParticleConfig = ParticleConfig(),
    cut_index: int | None = None,
    seed_base: int = 0,
) -> tuple[np.ndarray, np.ndarray, ParticleDiagnostics]:
    """Predict the suffix with likelihood-weighted independent particle seeds."""

    required = {"MD", "Z", "GR", "TVT_input"}
    if cut_index is not None:
        required.add("TVT")
    if missing := required.difference(frame.columns):
        raise ValueError(f"Horizontal well is missing columns: {sorted(missing)!r}")
    if missing := {"TVT", "GR"}.difference(typewell.columns):
        raise ValueError(f"Typewell is missing columns: {sorted(missing)!r}")
    if config.particles < 10 or config.seeds < 1:
        raise ValueError("Particle ensemble requires at least 10 particles and one seed")

    boundary = _boundary(frame, cut_index)
    known_column = "TVT" if cut_index is not None else "TVT_input"
    known_tvt = frame[known_column].to_numpy(dtype=float, copy=False)[:boundary]
    md = frame["MD"].to_numpy(dtype=float, copy=False)
    z = frame["Z"].to_numpy(dtype=float, copy=False)
    horizontal_gr = frame["GR"].to_numpy(dtype=float, copy=False)
    typewell_clean = typewell[["TVT", "GR"]].dropna().sort_values("TVT").drop_duplicates("TVT")
    tw_tvt = typewell_clean["TVT"].to_numpy(dtype=float, copy=False)
    tw_gr = typewell_clean["GR"].to_numpy(dtype=float, copy=False)
    if len(tw_tvt) < 3:
        raise ValueError("Typewell does not contain enough finite rows")

    prefix_expected = np.interp(known_tvt, tw_tvt, tw_gr)
    gain, offset, gr_sigma = _calibrate_gr(
        prefix_expected,
        horizontal_gr[:boundary],
        config.min_gr_sigma,
        config.max_gr_sigma,
    )
    expected_hgr = gain * tw_gr + offset
    rate = _initial_rate(md[:boundary], z[:boundary], known_tvt)
    anchor_u = float(known_tvt[-1] + z[boundary - 1])
    eval_indices = np.arange(boundary, len(frame), dtype=int)

    predictions: list[np.ndarray] = []
    log_evidence: list[float] = []
    for seed in range(seed_base, seed_base + config.seeds):
        prediction, evidence = _run_seed(
            seed=seed,
            md_eval=md[eval_indices],
            z_eval=z[eval_indices],
            gr_eval=horizontal_gr[eval_indices],
            previous_md=float(md[boundary - 1]),
            anchor_u=anchor_u,
            initial_rate=rate,
            tw_tvt=tw_tvt,
            expected_hgr=expected_hgr,
            gr_sigma=gr_sigma,
            config=config,
        )
        predictions.append(prediction)
        log_evidence.append(evidence)

    evidence_array = np.asarray(log_evidence, dtype=float)
    logits = (evidence_array - evidence_array.max()) / config.likelihood_temperature
    seed_weights = np.exp(np.clip(logits, -50.0, 0.0))
    seed_weights /= seed_weights.sum()
    ensemble = np.average(np.stack(predictions), axis=0, weights=seed_weights)
    diagnostics = ParticleDiagnostics(
        gr_gain=gain,
        gr_offset=offset,
        gr_sigma=gr_sigma,
        initial_rate=rate,
        effective_seed_count=1.0 / float(np.dot(seed_weights, seed_weights)),
        best_seed_weight=float(seed_weights.max()),
    )
    return eval_indices, ensemble, diagnostics
