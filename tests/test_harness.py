import unittest

import numpy as np

from harness.coverage import grid, plan
from harness.messages import DetectionReport
from harness.scenario import Scenario
from harness.scoring import gospa, score
from harness.simulate import run


class TestHarness(unittest.TestCase):
    def test_gospa_components(self):
        t = np.array([[0, 0, 0], [100, 0, 0]], float)
        self.assertEqual(gospa(t, t)["total"], 0)
        g = gospa(t, np.array([[3, 4, 0]], float), c=50)
        self.assertEqual((g["missed"], g["false"]), (1, 0))
        self.assertAlmostEqual(g["loc"], 5.0)

    def test_scenario_scores(self):
        sc = Scenario.load("scenarios/single-inbound.yaml")
        res = score(sc, run(sc))
        self.assertGreater(res["pd"], 0.6)
        self.assertIn("T1", res["time_to_detect_s"])

    def test_coverage_improves(self):
        area, sites = grid(-500, 500, -500, 500, 100), grid(-600, 600, -600, 600, 300)
        _, c1 = plan(area, sites, 600, 1)
        _, c3 = plan(area, sites, 600, 3)
        self.assertGreaterEqual(c3["k1"], c1["k1"])

    def test_message_roundtrip(self):
        r = DetectionReport("n1", 1.0, 45, -75, classification="UAV/multirotor")
        self.assertEqual(DetectionReport.from_json(r.to_json()), r)


if __name__ == "__main__":
    unittest.main()
