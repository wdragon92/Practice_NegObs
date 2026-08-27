# CTRL_TABLE — dressing-preserving OFF arm vs the original OFF arm

tau = 0.5 · seeds 42, 43, 44 · grid PROVISIONAL-GRID-V1 (20 cells) · RGB recipe v2 checkpoints

**old off** = `dataset/v2_corpus/260819_main_off` (the toggle also deleted the leaf mound, the railing and, in N3, the mural) · **new off** = `dataset/v2_probes/260820_ctrloff` (`keep_dressing`: hazard geometry only). Both are paired against the SAME on arm, `dataset/v2_corpus/260819_main_on`. Every off frame carries an all-zero GT, so `FA_frame` is a pure false-alarm rate.

## 1. Off-arm response (per seed, then mean ±half-range)

| scene | arm | seed | frames | FA_frame | cells/frame | mean max p |
|---|---|---|---|---|---|---|
| sceneC2 | old | 42 | 24 | 0.208 | 0.25 | 0.228 |
| sceneC2 | old | 43 | 24 | 0.000 | 0.00 | 0.108 |
| sceneC2 | old | 44 | 24 | 0.000 | 0.00 | 0.009 |
| **sceneC2** | **old** | **3 seeds** | 24 | **0.069 ±0.104** | 0.08 ±0.12 | 0.115 ±0.110 |
| sceneC2 | new | 42 | 24 | 0.500 | 2.17 | 0.519 |
| sceneC2 | new | 43 | 24 | 0.625 | 1.75 | 0.631 |
| sceneC2 | new | 44 | 24 | 0.917 | 2.42 | 0.803 |
| **sceneC2** | **new** | **3 seeds** | 24 | **0.681 ±0.208** | 2.11 ±0.33 | 0.651 ±0.142 |
| sceneN3 | old | 42 | 24 | 1.000 | 5.00 | 0.915 |
| sceneN3 | old | 43 | 24 | 0.708 | 1.21 | 0.648 |
| sceneN3 | old | 44 | 24 | 0.708 | 2.71 | 0.686 |
| **sceneN3** | **old** | **3 seeds** | 24 | **0.806 ±0.146** | 2.97 ±1.90 | 0.750 ±0.133 |
| sceneN3 | new | 42 | 24 | 1.000 | 6.79 | 0.946 |
| sceneN3 | new | 43 | 24 | 0.917 | 1.96 | 0.747 |
| sceneN3 | new | 44 | 24 | 0.750 | 3.29 | 0.740 |
| **sceneN3** | **new** | **3 seeds** | 24 | **0.889 ±0.125** | 4.01 ±2.42 | 0.811 ±0.103 |

## 2. Twin delta, old vs new off arm (pose-matched pairs, tol 0.15 m)

| scene | arm | seed | pairs kept/total | d_frame | d_score |
|---|---|---|---|---|---|
| sceneC2 | old | 42 | 24/24 | 0.476 | 0.481 |
| sceneC2 | old | 43 | 24/24 | 0.738 | 0.745 |
| sceneC2 | old | 44 | 24/24 | 0.884 | 0.837 |
| **sceneC2** | **old** | **3 seeds** | 24/24 | **0.699 ±0.204** | 0.688 ±0.178 |
| sceneC2 | new | 42 | 24/24 | 0.185 | 0.149 |
| sceneC2 | new | 43 | 24/24 | 0.214 | 0.212 |
| sceneC2 | new | 44 | 24/24 | 0.090 | 0.092 |
| **sceneC2** | **new** | **3 seeds** | 24/24 | **0.163 ±0.062** | 0.151 ±0.060 |
| sceneN3 | old | 42 | 24/24 | 0.031 | n/a (no GT-positive cell on the on arm) |
| sceneN3 | old | 43 | 24/24 | 0.098 | n/a (no GT-positive cell on the on arm) |
| sceneN3 | old | 44 | 24/24 | 0.052 | n/a (no GT-positive cell on the on arm) |
| **sceneN3** | **old** | **3 seeds** | 24/24 | **0.060 ±0.033** | n/a |
| sceneN3 | new | 42 | 24/24 | 0.000 | n/a (no GT-positive cell on the on arm) |
| sceneN3 | new | 43 | 24/24 | -0.001 | n/a (no GT-positive cell on the on arm) |
| sceneN3 | new | 44 | 24/24 | -0.002 | n/a (no GT-positive cell on the on arm) |
| **sceneN3** | **new** | **3 seeds** | 24/24 | **-0.001 ±0.001** | n/a |

## 3. QC

| seed | shared on-arm rows | max abs dp (new eval vs frozen eval) |
|---|---|---|
| 42 | 48 | 0.00e+00 |
| 43 | 48 | 0.00e+00 |
| 44 | 48 | 0.00e+00 |

> The on-arm rows are the same PNGs in both evaluations; a max |dp| above ~1e-5 means the two runs did not see the same frames and the comparison is void.

## 4. How to read this

The old off arm removes the hazard AND the scene's dressing; the new one removes the hazard only. `FA_frame(new) ~ FA_frame(old)` says the firing never depended on the dressing; `FA_frame(new) > FA_frame(old)` says the dressing is what the model fires on (the shortcut reading of DIAG_V1 §3); `FA_frame(new) < FA_frame(old)` would be the surprise and needs its own investigation before it is quoted. For sceneN3 the new off arm is structurally identical to the on arm, so its twin d_frame is a NULL control: a value near 0 is the expected result and a large one is a measurement artefact, not a finding.
