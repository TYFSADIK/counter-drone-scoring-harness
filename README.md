# Counter-Drone Test and Scoring Harness (build guide)

Private research repo. A counter-drone test-and-scoring harness: a SAPIENT node interface, a TAK bridge, YAML scenario cards, Stone Soup-style metrics, and a coverage planner. Everything here is test and evaluation for detection systems.

Full write-up and phase plan: [`docs/project-page.md`](docs/project-page.md)

## What's here

| File | Purpose |
|---|---|
| `harness/messages.py` | SAPIENT-style `DetectionReport`, independent of the wire format (add protobuf bindings later) |
| `harness/scenario.py` | Loads YAML scenario cards: truth waypoints, sensors (Pd, σ, clutter rate, range), pass criteria |
| `harness/simulate.py` | Synthetic sensor reports with misses, noise, and Poisson clutter |
| `harness/scoring.py` | **GOSPA** (split into localisation, missed, and false), Pd, false alarms per minute, time to detect, criteria check |
| `harness/coverage.py` | Greedy k-coverage sensor placement |
| `harness/cot.py` | TAK bridge (CoT XML) |
| `harness/cli.py` | `python -m harness.cli scenarios/*.yaml` exits non-zero on failure, so it can run in CI |
| `scenarios/` | Example cards: single inbound, crossing swarm |
| `.github-ci-example.yml` | Workflow that re-scores every card on each push |

## Quickstart

```bash
pip install -r requirements.txt
python demo.py && python -m unittest -v
```

## Next steps
- [ ] Phase 1: generate SAPIENT protobuf bindings (BSI Flex 335 v2.0 .proto files) and build a TCP adapter that emits `DetectionReport`
- [ ] Phase 2: ground truth from real flight logs (ArduPilot `.bin` to waypoints) with a GPS-disciplined time source (chrony + PPS)
- [ ] Phase 4: run SITL swarms to produce truth at scale
- [ ] Cross-check `gospa()` against `stonesoup.metricgenerator.ospametric.GOSPAMetric`
- [ ] Score real sensor nodes: the acoustic detector, passive radar, and multi-domain COP all emit `DetectionReport`

## Current result
With the naive `cluster()` baseline, `swarm-crossing` **passes** and `single-inbound` **fails**, at about 13 false alarms per minute against a limit of 6. The noisy RF bearings (σ 25 m) don't merge with the radar plots. That failure is correct. It's the gap a proper tracker (`counter-drone-sensor-fusion`) should close, and the harness proves it when it does.
