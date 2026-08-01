from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SPEC = spec_from_file_location("run_neighbor_profile_cv", ROOT / "scripts" / "run_neighbor_profile_cv.py")
MODULE = module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def _profile(name: str, x: float):
    path = np.column_stack([np.full(3, x), np.arange(3, dtype=float)])
    return MODULE.WellProfile(
        well_id=name,
        centroid=path.mean(axis=0),
        direction=np.array([0.0, 1.0]),
        path_xy=path,
        delta_tvt=np.zeros(len(MODULE.GRID)),
        eval_q=np.linspace(0.0, 1.0, 3),
        eval_z=np.zeros(3),
        eval_truth=np.zeros(3),
        anchor_tvt=0.0,
    )


def test_candidate_donors_respect_spatial_field_exclusion():
    profiles = [
        _profile("target", 0.0),
        _profile("same_field", 1.0),
        _profile("other_field", 2.0),
    ]
    centroids = np.stack([profile.centroid for profile in profiles])
    donors = MODULE._candidate_donors(
        0,
        profiles,
        centroids,
        prefilter=3,
        direction_cosine=0.0,
        forbidden_indices={0, 1},
    )
    assert [index for index, _ in donors] == [2]
