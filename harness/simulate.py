"""Generate synthetic sensor reports from a scenario (truth + noise + misses + clutter)."""
import numpy as np

from .scenario import Scenario, in_range


def run(sc: Scenario, seed=0):
    rng = np.random.default_rng(seed)
    reports = []   # (t, sensor_id, x, y, z, is_false)
    for s in sc.sensors:
        for t in np.arange(0, sc.duration_s, s.period_s):
            for tg in sc.targets:
                p = tg.position(t)
                if p is not None and in_range(s, p) and rng.random() < s.pd:
                    n = rng.normal(0, s.sigma_m, 3)
                    reports.append((float(t), s.id, p[0] + n[0], p[1] + n[1], p[2] + n[2] * 0.3, False))
            for _ in range(rng.poisson(s.false_alarm_rate_hz * s.period_s)):
                r, a = s.range_m * np.sqrt(rng.random()), rng.uniform(0, 2 * np.pi)
                reports.append((float(t), s.id, s.x + r * np.cos(a), s.y + r * np.sin(a), rng.uniform(0, 150), True))
    return sorted(reports)
