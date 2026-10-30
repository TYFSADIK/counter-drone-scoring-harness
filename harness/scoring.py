"""Scoring: GOSPA (localisation + missed + false components), Pd, false-alarm rate, time-to-detect.

GOSPA (Rahmathullah, Garcia-Fernandez, Svensson 2017) with alpha=2 decomposes
cleanly into localisation error, missed targets, and false tracks, which is
exactly what a test report needs. Stone Soup has the same metric; this is
dependency-light so it runs in CI.
"""
from collections import defaultdict
import math

import numpy as np
from scipy.optimize import linear_sum_assignment


def gospa(truth: np.ndarray, est: np.ndarray, c=50.0, p=2):
    """truth (n,3), est (m,3). Returns dict with total, localisation, missed, false."""
    n, m = len(truth), len(est)
    if n == 0 and m == 0:
        return {"total": 0.0, "loc": 0.0, "missed": 0, "false": 0}
    if n == 0 or m == 0:
        k = n + m
        return {"total": (c ** p / 2 * k) ** (1 / p), "loc": 0.0, "missed": n, "false": m}
    d = np.linalg.norm(truth[:, None, :] - est[None, :, :], axis=2)
    cost = np.minimum(d, c) ** p
    r, col = linear_sum_assignment(cost)
    assigned = [(i, j) for i, j in zip(r, col) if d[i, j] < c]
    loc = sum(d[i, j] ** p for i, j in assigned)
    missed, false = n - len(assigned), m - len(assigned)
    total = (loc + c ** p / 2 * (missed + false)) ** (1 / p)
    return {"total": float(total), "loc": float(math.sqrt(loc / max(len(assigned), 1))),
            "missed": missed, "false": false}


def cluster(points, radius_m=60.0):
    """Baseline 'system under test': merge reports from different sensors within radius_m.

    Replace with the real fusion output (counter-drone-sensor-fusion tracks) when scoring it.
    """
    clusters = []
    for p in points:
        for c in clusters:
            if np.linalg.norm(np.mean(c, axis=0) - p) < radius_m:
                c.append(p)
                break
        else:
            clusters.append([p])
    return [tuple(np.mean(c, axis=0)) for c in clusters]


def score(scenario, reports, gate_m=50.0, step_s=1.0, fuse=True):
    """reports: (t, sensor, x, y, z, is_false). Scores the (clustered) reports in each step window."""
    raw = defaultdict(list)
    for r in reports:
        raw[int(r[0] // step_s)].append(np.array(r[2:5], dtype=float))
    by_step = {k: (cluster(v) if fuse else v) for k, v in raw.items()}
    first_detect = {}
    g_tot, loc, missed, false, truth_count = [], [], 0, 0, 0
    for k in range(int(scenario.duration_s / step_s)):
        t = k * step_s
        truth_ids, truth = [], []
        for tg in scenario.targets:
            p = tg.position(t)
            if p is not None:
                truth_ids.append(tg.id); truth.append(p)
        est = np.array(by_step.get(k, []), dtype=float).reshape(-1, 3)
        tr = np.array(truth, dtype=float).reshape(-1, 3)
        g = gospa(tr, est, c=gate_m)
        g_tot.append(g["total"]); missed += g["missed"]; false += g["false"]; truth_count += len(tr)
        if g["loc"]:
            loc.append(g["loc"])
        for tid, pos in zip(truth_ids, tr):
            if tid not in first_detect and len(est) and np.min(np.linalg.norm(est - pos, axis=1)) < gate_m:
                first_detect[tid] = t
    starts = {tg.id: tg.waypoints[0].t for tg in scenario.targets}
    ttd = {tid: first_detect[tid] - starts[tid] for tid in first_detect}
    return {
        "mean_gospa": round(float(np.mean(g_tot)), 2),
        "rmse_m": round(float(np.mean(loc)), 2) if loc else None,
        "pd": round(1 - missed / truth_count, 3) if truth_count else None,
        "false_per_min": round(false / scenario.duration_s * 60, 2),
        "time_to_detect_s": ttd,
        "undetected": [tg.id for tg in scenario.targets if tg.id not in first_detect],
    }


def check_criteria(result, criteria):
    """criteria e.g. {'pd_min': 0.8, 'false_per_min_max': 2, 'time_to_detect_max_s': 10}"""
    fails = []
    if "pd_min" in criteria and (result["pd"] or 0) < criteria["pd_min"]:
        fails.append(f"pd {result['pd']} < {criteria['pd_min']}")
    if "false_per_min_max" in criteria and result["false_per_min"] > criteria["false_per_min_max"]:
        fails.append(f"false/min {result['false_per_min']} > {criteria['false_per_min_max']}")
    if "time_to_detect_max_s" in criteria:
        for tid, v in result["time_to_detect_s"].items():
            if v > criteria["time_to_detect_max_s"]:
                fails.append(f"{tid} detected after {v}s")
        fails += [f"{tid} never detected" for tid in result["undetected"]]
    return fails
