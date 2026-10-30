"""Coverage planner: greedy sensor placement maximising k-coverage of a defended area.

Greedy submodular maximisation gives a (1 - 1/e) approximation of the best
placement, good enough to compare layouts before going to the field.
"""
import numpy as np


def grid(xmin, xmax, ymin, ymax, step):
    xs, ys = np.meshgrid(np.arange(xmin, xmax + step, step), np.arange(ymin, ymax + step, step))
    return np.column_stack([xs.ravel(), ys.ravel()])


def plan(area_pts, candidate_sites, range_m, n_sensors, k=2):
    """Choose n_sensors sites so as many area points as possible are seen by >= k sensors."""
    d = np.linalg.norm(area_pts[:, None, :] - candidate_sites[None, :, :], axis=2)
    sees = d <= range_m                    # (points, sites)
    count = np.zeros(len(area_pts), dtype=int)
    chosen = []
    for _ in range(n_sensors):
        best, best_gain = None, -1
        for j in range(len(candidate_sites)):
            if j in chosen:
                continue
            gain = np.sum(np.minimum(count + sees[:, j], k) - np.minimum(count, k))
            if gain > best_gain:
                best, best_gain = j, gain
        chosen.append(best)
        count += sees[:, best]
    return chosen, {"k1": float(np.mean(count >= 1)), f"k{k}": float(np.mean(count >= k))}
