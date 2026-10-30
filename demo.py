"""Run: python demo.py  -> scores both scenario cards and plans a 4-sensor layout."""
import glob

import numpy as np

from harness.cli import main
from harness.coverage import grid, plan

main(sorted(glob.glob("scenarios/*.yaml")))
area = grid(-800, 800, -800, 800, 50)
sites = grid(-1000, 1000, -1000, 1000, 250)
chosen, cov = plan(area, sites, range_m=900, n_sensors=4, k=2)
print("sensor sites:", [tuple(int(v) for v in sites[j]) for j in chosen], "coverage:", cov)
