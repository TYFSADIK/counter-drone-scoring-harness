"""python -m harness.cli scenarios/*.yaml   -> run, score, and exit non-zero if any card fails (for CI)."""
import json
import sys

from .scenario import Scenario
from .scoring import check_criteria, score
from .simulate import run


def main(paths):
    failed = 0
    for p in paths:
        sc = Scenario.load(p)
        res = score(sc, run(sc))
        fails = check_criteria(res, sc.criteria)
        print(f"{'PASS' if not fails else 'FAIL'}  {sc.name}: {json.dumps(res)}")
        for f in fails:
            print("   -", f)
        failed += bool(fails)
    return failed


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
