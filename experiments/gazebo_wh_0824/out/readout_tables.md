## G1 geometry per view (visible void, per world)

| view | standoff | wh0/wh_h/wh_hc opening px | wh_e visible void px | opening px inside the node's ROI | GT cells (wh0) |
|---|---|---|---|---|---|
| `rs_d0.5` | 0.5 m | 139,512 | 72,296 | 45,611 | A1 B1 C1 D1 E1 |
| `rs_d0.7` | 0.7 m | 68,400 | 31,260 | 19,813 | A1 B1 C1 D1 E1 |
| `rs_d0.9` | 0.9 m | 39,376 | 16,692 | 8,045 | A1 B1 C1 D1 E1 |
| `rs_d1.1` | 1.1 m | 24,268 | 9,480 | 1,297 | A1 B1 C1 D1 E1 |
| `rs_d1.5` | 1.5 m | 11,726 | 4,298 | 0 | B1 C1 D1 B2 C2 D2 |
| `rs_d2` | 2.0 m | 5,868 | 1,830 | 0 | B2 C2 D2 |
| `rs_d2.6` | 2.6 m | 2,872 | 858 | 0 | B2 C2 D2 |
| `rs_d3.4` | 3.4 m | 1,438 | 442 | 0 | B2 C2 D2 |

## Y1 the node's real path (trapezium-masked input)

| world | tier | views | boxes tau0.25 | boxes floor0.05 | fire | void-overlap | centre-in-void | node gate | max conf |
|---|---|---|---|---|---|---|---|---|---|
| `wh0` | V (as published) | 8 | 4 | 5 | 0.500 | 0.500 | 0.375 | 0.375 | 0.874 |
| `wh_e` | E (edge-only) | 8 | 4 | 6 | 0.500 | 0.500 | 0.125 | 0.375 | 0.844 |
| `wh_h` | H (hidden) | 8 | 0 | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.078 |
| `wh_hc` | H-ctrl (no hazard) | 8 | 0 | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.078 |

## Y2 unmasked frame (fairness control)

| world | tier | views | boxes tau0.25 | boxes floor0.05 | fire | void-overlap | centre-in-void | node gate | max conf |
|---|---|---|---|---|---|---|---|---|---|
| `wh0` | V (as published) | 8 | 36 | 84 | 1.000 | 0.625 | 0.250 | 0.000 | 0.775 |
| `wh_e` | E (edge-only) | 8 | 25 | 64 | 1.000 | 0.375 | 0.000 | 0.000 | 0.780 |
| `wh_h` | H (hidden) | 8 | 10 | 35 | 0.500 | 0.000 | 0.000 | 0.000 | 0.528 |
| `wh_hc` | H-ctrl (no hazard) | 8 | 10 | 35 | 0.500 | 0.000 | 0.000 | 0.000 | 0.528 |

## Y3 per-view, arm=roi (the node's own path)

| view | standoff | `wh0` | `wh_e` | `wh_h` | `wh_hc` |
|---|---|---|---|---|---|
| `rs_d0.5` | 0.5 m | 1box conf 0.87 HIT GATE | 1box conf 0.84 HIT GATE | silent | silent |
| `rs_d0.7` | 0.7 m | 1box conf 0.82 HIT GATE | 1box conf 0.69 HIT GATE | silent | silent |
| `rs_d0.9` | 0.9 m | 1box conf 0.72 HIT GATE | 1box conf 0.71 HIT GATE | silent | silent |
| `rs_d1.1` | 1.1 m | 1box conf 0.55 HIT | 1box conf 0.55 HIT | silent | silent |
| `rs_d1.5` | 1.5 m | silent | silent | silent | silent |
| `rs_d2` | 2.0 m | silent | silent | silent | silent |
| `rs_d2.6` | 2.6 m | silent | silent | silent | silent |
| `rs_d3.4` | 3.4 m | silent | silent | silent | silent |

## Y4 where the node would have put the obstacle (arm=roi, best box)

| view | true near-rim distance | wh0 D_box | error | wh_e D_box | error |
|---|---|---|---|---|---|
| `rs_d0.5` | 0.50 m | 0.46 m | -0.04 m | 0.45 m | -0.05 m |
| `rs_d0.7` | 0.70 m | 0.58 m | -0.12 m | 0.60 m | -0.10 m |
| `rs_d0.9` | 0.90 m | 0.78 m | -0.12 m | 0.77 m | -0.13 m |
| `rs_d1.1` | 1.10 m | 0.81 m | -0.29 m | 0.81 m | -0.29 m |
| `rs_d1.5` | 1.50 m | - | - | - | - |
| `rs_d2` | 2.00 m | - | - | - | - |
| `rs_d2.6` | 2.60 m | - | - | - | - |
| `rs_d3.4` | 3.40 m | - | - | - | - |

## O1 ours, zero-shot (tau 0.5, gridspec_v1)

| model | world | tier | views | fire | GT-cell hit | mean max-p | mean p(GT) |
|---|---|---|---|---|---|---|---|
| `v2_rgb_s42` | `wh0` | V (as published) | 8 | 1.000 | 0.000 | 0.649 | 0.255 |
| `v2_rgb_s42` | `wh_e` | E (edge-only) | 8 | 0.625 | 0.000 | 0.601 | 0.238 |
| `v2_rgb_s42` | `wh_h` | H (hidden) | 8 | 0.625 | 0.000 | 0.537 | 0.280 |
| `v2_rgb_s42` | `wh_hc` | H-ctrl (no hazard) | 8 | 0.625 | 0.000 | 0.537 | 0.280 |
| `v3a_rgb_s42` | `wh0` | V (as published) | 8 | 0.500 | 0.000 | 0.524 | 0.050 |
| `v3a_rgb_s42` | `wh_e` | E (edge-only) | 8 | 0.625 | 0.250 | 0.649 | 0.251 |
| `v3a_rgb_s42` | `wh_h` | H (hidden) | 8 | 0.625 | 0.500 | 0.661 | 0.340 |
| `v3a_rgb_s42` | `wh_hc` | H-ctrl (no hazard) | 8 | 0.625 | 0.500 | 0.661 | 0.340 |

## O2 ours per view, p(GT cells)

| model | view | `wh0` | `wh_e` | `wh_h` | `wh_hc` |
|---|---|---|---|---|---|
| `v2_rgb_s42` | `rs_d0.5` | 0.16 | 0.19 | 0.28 | 0.28 |
| `v2_rgb_s42` | `rs_d0.7` | 0.30 | 0.21 | 0.35 | 0.35 |
| `v2_rgb_s42` | `rs_d0.9` | 0.38 | 0.18 | 0.34 | 0.34 |
| `v2_rgb_s42` | `rs_d1.1` | 0.19 | 0.23 | 0.34 | 0.34 |
| `v2_rgb_s42` | `rs_d1.5` | 0.35 | 0.18 | 0.13 | 0.13 |
| `v2_rgb_s42` | `rs_d2` | 0.16 | 0.26 | 0.21 | 0.21 |
| `v2_rgb_s42` | `rs_d2.6` | 0.17 | 0.30 | 0.20 | 0.20 |
| `v2_rgb_s42` | `rs_d3.4` | 0.33 | 0.35 | 0.41 | 0.41 |
| `v3a_rgb_s42` | `rs_d0.5` | 0.02 | 0.06 | 0.16 | 0.16 |
| `v3a_rgb_s42` | `rs_d0.7` | 0.02 | 0.12 | 0.03 | 0.03 |
| `v3a_rgb_s42` | `rs_d0.9` | 0.00 | 0.01 | 0.04 | 0.04 |
| `v3a_rgb_s42` | `rs_d1.1` | 0.01 | 0.57 | 0.04 | 0.04 |
| `v3a_rgb_s42` | `rs_d1.5` | 0.18 | 0.00 | 0.58 | 0.58 |
| `v3a_rgb_s42` | `rs_d2` | 0.06 | 0.26 | 0.75 | 0.75 |
| `v3a_rgb_s42` | `rs_d2.6` | 0.03 | 0.19 | 0.54 | 0.54 |
| `v3a_rgb_s42` | `rs_d3.4` | 0.08 | 0.79 | 0.58 | 0.58 |

wrote out/readout.csv (64 rows), out/readout_ours.csv (64 rows), out/readout.json
