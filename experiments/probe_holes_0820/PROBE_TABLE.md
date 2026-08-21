# PROBE_TABLE — C1 hole-type zero-shot probe

**Evaluation only. Nothing here trained, and no probe frame may ever enter training** (OVERNIGHT_BRIEF_0820 §4 C1).

* manifest `experiments/probe_holes_0820/dataset_manifest_probe.json` — 144 frames, grid **PROVISIONAL-GRID-V1** (20 cells), rounds {'on': '260821_probe_on', 'off': '260821_probe_off'}
* checkpoints: the nine FROZEN recipe-v2 runs under `experiments/dayrun_0820/runs/v2` (rgb/depth/b2 x seeds 42/43/44)
* tau_op = **0.5**, frozen by absolute rule 3 and NOT re-fitted on probe data (`val` is deliberately empty in `split_probe.json`)

## 1. headline — all probe frames as one subset

| ckpt | n frames | cell F1 | frame det | recall V | recall E | recall H | frame FA (off) | cell FPR (off) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| b2_s42 | 144 | 0.058 | 0.083 | 0.000 | 0.000 | 0.200 | 0.125 | 0.028 |
| b2_s43 | 144 | 0.174 | 0.597 | 1.000 | 0.259 | 0.700 | 0.806 | 0.240 |
| b2_s44 | 144 | 0.119 | 0.083 | 0.000 | 0.000 | 0.200 | 0.083 | 0.023 |
| depth_s42 | 144 | 0.145 | 0.250 | 0.200 | 0.111 | 0.400 | 0.333 | 0.152 |
| depth_s43 | 144 | 0.131 | 0.208 | 0.000 | 0.000 | 0.500 | 0.250 | 0.135 |
| depth_s44 | 144 | 0.114 | 0.125 | 0.000 | 0.000 | 0.300 | 0.167 | 0.098 |
| rgb_s42 | 144 | 0.074 | 0.056 | 0.133 | 0.000 | 0.067 | 0.056 | 0.017 |
| rgb_s43 | 144 | 0.121 | 0.139 | 0.200 | 0.000 | 0.233 | 0.181 | 0.032 |
| rgb_s44 | 144 | 0.055 | 0.042 | 0.000 | 0.000 | 0.100 | 0.083 | 0.010 |

## 2. per scene (tau_op = 0.50)

| ckpt | scene | n(on/off) | hazard frames | frame recall | V | E | H | frame FA (off) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| b2_s42 | probeH1 | 24/24 | 24 | 0.000 | 0.000 (15) | 0.000 (3) | 0.000 (6) | 0.000 |
| b2_s42 | probeH2 | 24/24 | 24 | 0.000 | n/a (0) | 0.000 (24) | n/a (0) | 0.042 |
| b2_s42 | probeH3 | 24/24 | 24 | 0.250 | n/a (0) | n/a (0) | 0.250 (24) | 0.333 |
| b2_s43 | probeH1 | 24/24 | 24 | 1.000 | 1.000 (15) | 1.000 (3) | 1.000 (6) | 0.917 |
| b2_s43 | probeH2 | 24/24 | 24 | 0.167 | n/a (0) | 0.167 (24) | n/a (0) | 0.750 |
| b2_s43 | probeH3 | 24/24 | 24 | 0.625 | n/a (0) | n/a (0) | 0.625 (24) | 0.750 |
| b2_s44 | probeH1 | 24/24 | 24 | 0.000 | 0.000 (15) | 0.000 (3) | 0.000 (6) | 0.000 |
| b2_s44 | probeH2 | 24/24 | 24 | 0.000 | n/a (0) | 0.000 (24) | n/a (0) | 0.000 |
| b2_s44 | probeH3 | 24/24 | 24 | 0.250 | n/a (0) | n/a (0) | 0.250 (24) | 0.250 |
| depth_s42 | probeH1 | 24/24 | 24 | 0.125 | 0.200 (15) | 0.000 (3) | 0.000 (6) | 0.125 |
| depth_s42 | probeH2 | 24/24 | 24 | 0.125 | n/a (0) | 0.125 (24) | n/a (0) | 0.375 |
| depth_s42 | probeH3 | 24/24 | 24 | 0.500 | n/a (0) | n/a (0) | 0.500 (24) | 0.500 |
| depth_s43 | probeH1 | 24/24 | 24 | 0.000 | 0.000 (15) | 0.000 (3) | 0.000 (6) | 0.125 |
| depth_s43 | probeH2 | 24/24 | 24 | 0.000 | n/a (0) | 0.000 (24) | n/a (0) | 0.000 |
| depth_s43 | probeH3 | 24/24 | 24 | 0.625 | n/a (0) | n/a (0) | 0.625 (24) | 0.625 |
| depth_s44 | probeH1 | 24/24 | 24 | 0.000 | 0.000 (15) | 0.000 (3) | 0.000 (6) | 0.000 |
| depth_s44 | probeH2 | 24/24 | 24 | 0.000 | n/a (0) | 0.000 (24) | n/a (0) | 0.000 |
| depth_s44 | probeH3 | 24/24 | 24 | 0.375 | n/a (0) | n/a (0) | 0.375 (24) | 0.500 |
| rgb_s42 | probeH1 | 24/24 | 24 | 0.083 | 0.133 (15) | 0.000 (3) | 0.000 (6) | 0.000 |
| rgb_s42 | probeH2 | 24/24 | 24 | 0.000 | n/a (0) | 0.000 (24) | n/a (0) | 0.000 |
| rgb_s42 | probeH3 | 24/24 | 24 | 0.083 | n/a (0) | n/a (0) | 0.083 (24) | 0.167 |
| rgb_s43 | probeH1 | 24/24 | 24 | 0.125 | 0.200 (15) | 0.000 (3) | 0.000 (6) | 0.000 |
| rgb_s43 | probeH2 | 24/24 | 24 | 0.000 | n/a (0) | 0.000 (24) | n/a (0) | 0.000 |
| rgb_s43 | probeH3 | 24/24 | 24 | 0.292 | n/a (0) | n/a (0) | 0.292 (24) | 0.542 |
| rgb_s44 | probeH1 | 24/24 | 24 | 0.000 | 0.000 (15) | 0.000 (3) | 0.000 (6) | 0.000 |
| rgb_s44 | probeH2 | 24/24 | 24 | 0.000 | n/a (0) | 0.000 (24) | n/a (0) | 0.000 |
| rgb_s44 | probeH3 | 24/24 | 24 | 0.125 | n/a (0) | n/a (0) | 0.125 (24) | 0.250 |

## 3. probeH2 — adjacent hazard-free sector firing

The corridor-preserving composition: the hazard sits in ONE lateral sector and the sectors beside it, in the same band, carry no hazard. `adjacent` = one sector away, `far` = two or more. An adjacent rate far above the far rate is angular blur around a correct answer; an equal rate is a scene-level prior firing.

| ckpt | frames | adj cells | adj fired | adj cell rate | adj frame rate | far cell rate |
|---|---:|---:|---:|---:|---:|---:|
| b2_s42 | 24 | 48 | 0 | 0.000 | 0.000 | 0.000 |
| b2_s43 | 24 | 48 | 9 | 0.188 | 0.375 | 0.045 |
| b2_s44 | 24 | 48 | 0 | 0.000 | 0.000 | 0.000 |
| depth_s42 | 24 | 48 | 6 | 0.125 | 0.250 | 0.000 |
| depth_s43 | 24 | 48 | 0 | 0.000 | 0.000 | 0.000 |
| depth_s44 | 24 | 48 | 0 | 0.000 | 0.000 | 0.000 |
| rgb_s42 | 24 | 48 | 0 | 0.000 | 0.000 | 0.000 |
| rgb_s43 | 24 | 48 | 0 | 0.000 | 0.000 | 0.000 |
| rgb_s44 | 24 | 48 | 0 | 0.000 | 0.000 | 0.000 |

## 4. twin analysis

One `twin_analysis.md` per checkpoint, run at the DEFAULT pose tolerance `--tol 1e-6` (identical within float noise). The D20 rescue tolerance of 0.15 m — the one nightrun B5 is re-checking, because it admits pairs whose `ground_z` genuinely moved — is NOT used and must not be needed: these scenes are built so the hazard toggle cannot move `ground_z` under any camera (`probe_common.twin_audit`, asserted pre-boot in both arms). If a run reports excluded pairs, that is a finding about the scenes and goes in the report; it does not get fixed by widening the tolerance.

* `b2_s42` -> `experiments/probe_holes_0820/eval/b2_s42/twin/twin_analysis.md`
* `b2_s43` -> `experiments/probe_holes_0820/eval/b2_s43/twin/twin_analysis.md`
* `b2_s44` -> `experiments/probe_holes_0820/eval/b2_s44/twin/twin_analysis.md`
* `depth_s42` -> `experiments/probe_holes_0820/eval/depth_s42/twin/twin_analysis.md`
* `depth_s43` -> `experiments/probe_holes_0820/eval/depth_s43/twin/twin_analysis.md`
* `depth_s44` -> `experiments/probe_holes_0820/eval/depth_s44/twin/twin_analysis.md`
* `rgb_s42` -> `experiments/probe_holes_0820/eval/rgb_s42/twin/twin_analysis.md`
* `rgb_s43` -> `experiments/probe_holes_0820/eval/rgb_s43/twin/twin_analysis.md`
* `rgb_s44` -> `experiments/probe_holes_0820/eval/rgb_s44/twin/twin_analysis.md`

## 5. how to read a null result

A collapse of H recall on **probeH3** while V/E survive on probeH1/H2 is not a failed probe: it is the finding that the H-tier claim is drop-TYPE bound, and it belongs in the paper's limitations. A collapse everywhere including V says the checkpoints are scene-bound rather than type-bound. Both are Tier-3 outcomes under the brief's acceptance rule ('렌더까지만 되고 평가가 실패해도, 산출물과 원인이 기록되면 Tier3 성립').
