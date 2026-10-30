"""Scenario cards: YAML files describing truth trajectories, sensors, and pass criteria."""
from dataclasses import dataclass
import math

try:
    import yaml
except ImportError:   # JSON is valid YAML subset; fall back for zero-dep use
    yaml = None
import json


@dataclass
class Waypoint:
    t: float
    x: float
    y: float
    z: float


@dataclass
class Target:
    id: str
    kind: str
    waypoints: list

    def position(self, t):
        wps = self.waypoints
        if t < wps[0].t or t > wps[-1].t:
            return None
        for a, b in zip(wps, wps[1:]):
            if a.t <= t <= b.t:
                f = (t - a.t) / (b.t - a.t) if b.t > a.t else 0
                return (a.x + f * (b.x - a.x), a.y + f * (b.y - a.y), a.z + f * (b.z - a.z))
        return (wps[-1].x, wps[-1].y, wps[-1].z)


@dataclass
class Sensor:
    id: str
    kind: str
    x: float
    y: float
    range_m: float
    pd: float = 0.9
    sigma_m: float = 10.0
    false_alarm_rate_hz: float = 0.01
    period_s: float = 1.0


@dataclass
class Scenario:
    name: str
    duration_s: float
    targets: list
    sensors: list
    criteria: dict

    @staticmethod
    def load(path) -> "Scenario":
        text = open(path).read()
        d = yaml.safe_load(text) if yaml else json.loads(text)
        targets = [Target(t["id"], t.get("kind", "multirotor"),
                          [Waypoint(*w) for w in t["waypoints"]]) for t in d["targets"]]
        sensors = [Sensor(**s) for s in d["sensors"]]
        return Scenario(d["name"], d["duration_s"], targets, sensors, d.get("criteria", {}))


def in_range(sensor: Sensor, pos) -> bool:
    return math.hypot(pos[0] - sensor.x, pos[1] - sensor.y) <= sensor.range_m
