# H_RECALL_STRATIFIED — auto-generated numbers (do not hand-edit)

Source: `h_cue_table.csv` + `experiments/dayrun_0820/runs/v2/*/eval_test/per_frame_{on,val}.csv`.
τ_op = 0.5. `mean ± range/2` over seeds {42,43,44} — seed spread, **not** a CI.

### 1. HEADLINE — cued-H vs bare-H (test split, 7 test scenes, n=96)

| stratum | n | rgb mean±r/2 | rgb per seed | depth mean±r/2 | depth per seed | b2 mean±r/2 | b2 per seed |
|---|---|---|---|---|---|---|---|
| cued-H (>=1 cue visible) | 87 | 0.705 ± 0.126 | 0.621/0.874/0.621 | 0.437 ± 0.034 | 0.414/0.483/0.414 | 0.241 ± 0.167 | 0.092/0.425/0.207 |
| bare-H (0 cues visible) | 9 | 0.519 ± 0.278 | 0.333/0.889/0.333 | 0.444 ± 0.167 | 0.333/0.333/0.667 | 0.111 ± 0.111 | 0.000/0.111/0.222 |
| all test H (= headline) | 96 | 0.688 ± 0.141 | 0.594/0.875/0.594 | 0.438 ± 0.031 | 0.406/0.469/0.438 | 0.229 ± 0.156 | 0.083/0.396/0.208 |

### 2. dose-response ladder (test)

| stratum | n | rgb mean±r/2 | rgb per seed | depth mean±r/2 | depth per seed | b2 mean±r/2 | b2 per seed |
|---|---|---|---|---|---|---|---|
| cue_count=0 | 9 | 0.519 ± 0.278 | 0.333/0.889/0.333 | 0.444 ± 0.167 | 0.333/0.333/0.667 | 0.111 ± 0.111 | 0.000/0.111/0.222 |
| cue_count=3 | 21 | 0.556 ± 0.238 | 0.810/0.524/0.333 | 0.000 ± 0.000 | 0.000/0.000/0.000 | 0.270 ± 0.405 | 0.000/0.810/0.000 |
| cue_count=4 | 5 | 0.867 ± 0.200 | 1.000/1.000/0.600 | 0.133 ± 0.200 | 0.000/0.400/0.000 | 0.333 ± 0.500 | 0.000/1.000/0.000 |
| cue_count=5 | 28 | 0.655 ± 0.304 | 0.357/0.964/0.643 | 0.369 ± 0.071 | 0.321/0.464/0.321 | 0.155 ± 0.179 | 0.000/0.357/0.107 |
| cue_count=6 | 33 | 0.818 ± 0.167 | 0.667/1.000/0.788 | 0.818 ± 0.000 | 0.818/0.818/0.818 | 0.283 ± 0.152 | 0.242/0.152/0.455 |

### 3. within-scene14 (the only test scene holding both strata)

| stratum | n | rgb mean±r/2 | rgb per seed | depth mean±r/2 | depth per seed | b2 mean±r/2 | b2 per seed |
|---|---|---|---|---|---|---|---|
| scene14 cued-H | 51 | 0.739 ± 0.255 | 0.490/1.000/0.725 | 0.706 ± 0.000 | 0.706/0.706/0.706 | 0.203 ± 0.127 | 0.157/0.098/0.353 |
| scene14 bare-H | 9 | 0.519 ± 0.278 | 0.333/0.889/0.333 | 0.444 ± 0.167 | 0.333/0.333/0.667 | 0.111 ± 0.111 | 0.000/0.111/0.222 |
| scene15 (all cued) | 36 | 0.657 ± 0.167 | 0.806/0.694/0.472 | 0.056 ± 0.083 | 0.000/0.167/0.000 | 0.296 ± 0.444 | 0.000/0.889/0.000 |

### 4. guard-vocabulary cut (test) — railing_or_guard in frame or not

| stratum | n | rgb mean±r/2 | rgb per seed | depth mean±r/2 | depth per seed | b2 mean±r/2 | b2 per seed |
|---|---|---|---|---|---|---|---|
| railing visible | 51 | 0.739 ± 0.255 | 0.490/1.000/0.725 | 0.706 ± 0.000 | 0.706/0.706/0.706 | 0.203 ± 0.127 | 0.157/0.098/0.353 |
| railing absent | 45 | 0.630 ± 0.144 | 0.711/0.733/0.444 | 0.133 ± 0.067 | 0.067/0.200/0.133 | 0.259 ± 0.367 | 0.000/0.733/0.044 |

### 5. cue family cuts (test)

| stratum | n | rgb mean±r/2 | rgb per seed | depth mean±r/2 | depth per seed | b2 mean±r/2 | b2 per seed |
|---|---|---|---|---|---|---|---|
| direct-depth cue >=1 | 87 | 0.705 ± 0.126 | 0.621/0.874/0.621 | 0.437 ± 0.034 | 0.414/0.483/0.414 | 0.241 ± 0.167 | 0.092/0.425/0.207 |
| direct-depth cue 0 | 9 | 0.519 ± 0.278 | 0.333/0.889/0.333 | 0.444 ± 0.167 | 0.333/0.333/0.667 | 0.111 ± 0.111 | 0.000/0.111/0.222 |
| installed cue >=1 | 51 | 0.739 ± 0.255 | 0.490/1.000/0.725 | 0.706 ± 0.000 | 0.706/0.706/0.706 | 0.203 ± 0.127 | 0.157/0.098/0.353 |
| installed cue 0 | 45 | 0.630 ± 0.144 | 0.711/0.733/0.444 | 0.133 ± 0.067 | 0.067/0.200/0.133 | 0.259 ± 0.367 | 0.000/0.733/0.044 |

### 6. viewpoint preset (test) — the confound A control

| stratum | n | rgb mean±r/2 | rgb per seed | depth mean±r/2 | depth per seed | b2 mean±r/2 | b2 per seed |
|---|---|---|---|---|---|---|---|
| h0.3_d10 | 30 | 0.544 ± 0.167 | 0.667/0.633/0.333 | 0.133 ± 0.050 | 0.100/0.100/0.200 | 0.222 ± 0.300 | 0.000/0.600/0.067 |
| h0.3_d5 | 6 | 1.000 ± 0.000 | 1.000/1.000/1.000 | 0.333 ± 0.500 | 0.000/1.000/0.000 | 0.333 ± 0.500 | 0.000/1.000/0.000 |
| h0.9_d10 | 27 | 0.617 ± 0.315 | 0.333/0.963/0.556 | 0.333 ± 0.000 | 0.333/0.333/0.333 | 0.148 ± 0.167 | 0.000/0.333/0.111 |
| h0.9_d5 | 18 | 0.889 ± 0.083 | 0.833/1.000/0.833 | 1.000 ± 0.000 | 1.000/1.000/1.000 | 0.389 ± 0.111 | 0.389/0.278/0.500 |
| h1.8_d10 | 12 | 0.667 ± 0.333 | 0.333/1.000/0.667 | 0.500 ± 0.000 | 0.500/0.500/0.500 | 0.111 ± 0.125 | 0.083/0.000/0.250 |
| h1.8_d5 | 3 | 1.000 ± 0.000 | 1.000/1.000/1.000 | 1.000 ± 0.000 | 1.000/1.000/1.000 | 0.333 ± 0.500 | 0.000/0.000/1.000 |

### 7. band-fixed subset (test, frames whose GT positives are 3b only)

| stratum | n | rgb mean±r/2 | rgb per seed | depth mean±r/2 | depth per seed | b2 mean±r/2 | b2 per seed |
|---|---|---|---|---|---|---|---|
| 3b-only cued-H | 54 | 0.586 ± 0.185 | 0.444/0.815/0.500 | 0.278 ± 0.000 | 0.278/0.278/0.278 | 0.167 ± 0.176 | 0.019/0.370/0.111 |
| 3b-only bare-H | 9 | 0.519 ± 0.278 | 0.333/0.889/0.333 | 0.444 ± 0.167 | 0.333/0.333/0.667 | 0.111 ± 0.111 | 0.000/0.111/0.222 |
| 3a+3b cued-H | 33 | 0.899 ± 0.076 | 0.909/0.970/0.818 | 0.697 ± 0.091 | 0.636/0.818/0.636 | 0.364 ± 0.152 | 0.212/0.515/0.364 |

### 8. val reference (scene20, n=6 — below the n>=10 preregistered floor)

| stratum | n | rgb mean±r/2 | rgb per seed | depth mean±r/2 | depth per seed | b2 mean±r/2 | b2 per seed |
|---|---|---|---|---|---|---|---|
| scene20 cued-H | 6 | 1.000 ± 0.000 | 1.000/1.000/1.000 | 1.000 ± 0.000 | 1.000/1.000/1.000 | 1.000 ± 0.000 | 1.000/1.000/1.000 |

### 9. cell recall on the same strata (test) — secondary metric

| stratum | n frames | pos cells | rgb | depth | b2 |
|---|---|---|---|---|---|
| cued-H | 87 | 426 | 0.351 ± 0.128 | 0.563 ± 0.053 | 0.103 ± 0.069 |
| bare-H | 9 | 45 | 0.274 ± 0.278 | 0.289 ± 0.267 | 0.030 ± 0.033 |

### 10. scene14 with the GT band ALSO fixed (confound A + B controlled)

The bare-H stratum is 3b-only by construction, so this is the only comparison in which neither scene identity nor GT band differs between arms.

| stratum | n | rgb mean±r/2 | rgb per seed | depth mean±r/2 | depth per seed | b2 mean±r/2 | b2 per seed |
|---|---|---|---|---|---|---|---|
| s14 3b-only cued-H | 30 | 0.622 ± 0.383 | 0.233/1.000/0.633 | 0.500 ± 0.000 | 0.500/0.500/0.500 | 0.078 ± 0.100 | 0.033/0.000/0.200 |
| s14 3b-only bare-H | 9 | 0.519 ± 0.278 | 0.333/0.889/0.333 | 0.444 ± 0.167 | 0.333/0.333/0.667 | 0.111 ± 0.111 | 0.000/0.111/0.222 |
| s14 3a+3b cued-H (near band also positive) | 21 | 0.905 ± 0.071 | 0.857/1.000/0.857 | 1.000 ± 0.000 | 1.000/1.000/1.000 | 0.381 ± 0.167 | 0.333/0.238/0.571 |

### 11. paired seed-wise Δ = R_cued − R_bare (preregistered sign test)

| comparison | model | Δ s42 | Δ s43 | Δ s44 | mean Δ | range/2 | signs agree? |
|---|---|---|---|---|---|---|---|
| test cued vs bare (n 87/9) | rgb | +0.287 | -0.015 | +0.287 | +0.186 | 0.151 | **NO** |
| test cued vs bare (n 87/9) | depth | +0.080 | +0.149 | -0.253 | -0.008 | 0.201 | **NO** |
| test cued vs bare (n 87/9) | b2 | +0.092 | +0.314 | -0.015 | +0.130 | 0.165 | **NO** |
| scene14 cued vs bare (n 51/9) | rgb | +0.157 | +0.111 | +0.392 | +0.220 | 0.141 | YES |
| scene14 cued vs bare (n 51/9) | depth | +0.373 | +0.373 | +0.039 | +0.261 | 0.167 | YES |
| scene14 cued vs bare (n 51/9) | b2 | +0.157 | -0.013 | +0.131 | +0.092 | 0.085 | **NO** |
| scene14 3b-only cued vs bare (n 30/9) | rgb | -0.100 | +0.111 | +0.300 | +0.104 | 0.200 | **NO** |
| scene14 3b-only cued vs bare (n 30/9) | depth | +0.167 | +0.167 | -0.167 | +0.056 | 0.167 | **NO** |
| scene14 3b-only cued vs bare (n 30/9) | b2 | +0.033 | -0.111 | -0.022 | -0.033 | 0.072 | **NO** |
