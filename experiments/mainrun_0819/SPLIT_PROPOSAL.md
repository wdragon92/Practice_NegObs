# SPLIT_PROPOSAL — PROVISIONAL — 아침 승인 대상

manifest: `experiments/mainrun_0819/dataset_manifest_v1.json` · seed 42 · 29 eligible scenes (33 in manifest − 4 held) / 1584 frames (192 held out)
hard-negative arg: ['sceneN3']
test L1-to-global tier distance (incl. off-arm preference term): 0.0618; val 0.1163

## PROVISIONAL-HOLD (아침 결재 대상)

`--exclude-scenes @experiments/mainrun_0819/annotations/hold_scenes.json` → **4 scene(s) in NO split** (not train, not val, not test). Per D14④ these are batch-1 non-stair drop scenes that came out all-negative under the D10 step gate; holding them out keeps a possibly-wrong label out of the headline metric until the morning ruling. Re-run this script without `--exclude-scenes` (or with a trimmed list) once the gate is adopted or reverted.

| scene | frames | off-arm | strict-H |
|---|---|---|---|
| scene11 | 48 | 24 | 0 |
| scene13 | 48 | 24 | 0 |
| scene19 | 48 | 24 | 0 |
| sceneD4 | 48 | 24 | 0 |

## Assignment

| split | n scenes | scenes |
|---|---|---|
| train | 20 | scene01, scene02, scene03, scene04, scene06, scene08, scene09, scene12, scene16, scene17, scene20, scene21, sceneC1, sceneC4, sceneD1, sceneD2, sceneN1, sceneN2, sceneN4, sceneN5 |
| val | 2 | scene10, sceneD3 |
| test | 7 | scene05, scene07, scene14, scene15, scene18, sceneC2, sceneN3 |
| **HOLD** | 4 | scene11, scene13, scene19, sceneD4 |

## Tier distribution (frame counts, share)

| split | V | E | H | off | frames |
|---|---|---|---|---|---|
| train | 294 (0.36) | 21 (0.03) | 24 (0.03) | 480 (0.59) | 819 |
| val | 33 (0.38) | 6 (0.07) | 0 (0.00) | 48 (0.55) | 87 |
| test | 111 (0.36) | 9 (0.03) | 21 (0.07) | 168 (0.54) | 309 |
| **global** | 438 (0.36) | 36 (0.03) | 45 (0.04) | 696 (0.57) | 1215 |

## Per-scene

| scene | split | frames | off-arm | strict-H | V | E | H | off |
|---|---|---|---|---|---|---|---|---|
| scene01 | train | 48 | 24 | 0 | 24 | 0 | 0 | 24 |
| scene02 | train | 48 | 24 | 0 | 15 | 9 | 0 | 24 |
| scene03 | train | 48 | 24 | 0 | 18 | 0 | 0 | 24 |
| scene04 | train | 48 | 24 | 0 | 24 | 0 | 0 | 24 |
| scene05 | test | 48 | 24 | 0 | 24 | 0 | 0 | 24 |
| scene06 | train | 48 | 24 | 0 | 0 | 0 | 0 | 24 |
| scene07 | test | 48 | 24 | 0 | 21 | 0 | 0 | 24 |
| scene08 | train | 48 | 24 | 0 | 21 | 0 | 0 | 24 |
| scene09 | train | 48 | 24 | 15 | 6 | 0 | 15 | 24 |
| scene10 | val | 48 | 24 | 0 | 15 | 0 | 0 | 24 |
| scene11 | **HOLD** | 48 | 24 | 0 | 0 | 0 | 0 | 24 |
| scene12 | train | 48 | 24 | 0 | 24 | 0 | 0 | 24 |
| scene13 | **HOLD** | 48 | 24 | 0 | 0 | 0 | 0 | 24 |
| scene14 | test | 48 | 24 | 18 | 6 | 0 | 18 | 24 |
| scene15 | test | 48 | 24 | 3 | 21 | 0 | 3 | 24 |
| scene16 | train | 48 | 24 | 0 | 24 | 0 | 0 | 24 |
| scene17 | train | 48 | 24 | 9 | 12 | 0 | 9 | 24 |
| scene18 | test | 48 | 24 | 0 | 15 | 9 | 0 | 24 |
| scene19 | **HOLD** | 48 | 24 | 0 | 0 | 0 | 0 | 24 |
| scene20 | train | 48 | 24 | 0 | 21 | 0 | 0 | 24 |
| scene21 | train | 48 | 24 | 0 | 21 | 3 | 0 | 24 |
| sceneC1 | train | 48 | 24 | 0 | 21 | 0 | 0 | 24 |
| sceneC2 | test | 48 | 24 | 0 | 24 | 0 | 0 | 24 |
| sceneC4 | train | 48 | 24 | 0 | 24 | 0 | 0 | 24 |
| sceneD1 | train | 48 | 24 | 0 | 24 | 0 | 0 | 24 |
| sceneD2 | train | 48 | 24 | 0 | 15 | 9 | 0 | 24 |
| sceneD3 | val | 48 | 24 | 0 | 18 | 6 | 0 | 24 |
| sceneD4 | **HOLD** | 48 | 24 | 0 | 0 | 0 | 0 | 24 |
| sceneN1 | train | 48 | 24 | 0 | 0 | 0 | 0 | 24 |
| sceneN2 | train | 48 | 24 | 0 | 0 | 0 | 0 | 24 |
| sceneN3 | test | 48 | 24 | 0 | 0 | 0 | 0 | 24 |
| sceneN4 | train | 48 | 24 | 0 | 0 | 0 | 0 | 24 |
| sceneN5 | train | 48 | 24 | 0 | 0 | 0 | 0 | 24 |

## Violation proof

```
PROOF-1 scene count: 20 train + 2 val + 7 test = 29 == 29 eligible scenes (33 manifest − 4 held) -> PASS
PROOF-2 no scene in two splits: 0 duplicates -> PASS
PROOF-3 no ELIGIBLE scene unassigned: 0 -> PASS
PROOF-4 every non-held frame resolves to exactly one split: 0 bad of 1392 (192 frames held out) -> PASS
PROOF-5 both arms (on/off) of a scene share its split (split key is scene_id): 0 violations -> PASS
PROOF-6 test size 7 in 7±1 and 24.1% of the 29 eligible scenes (target 20-25%) -> PASS
PROOF-7 test contains >=2 top-strict-H scenes: ['scene14', 'scene15'] -> PASS
PROOF-8 test contains >=1 hard-negative ['sceneN3']: ['sceneN3'] -> PASS
PROOF-7b [D18] forced-into-test: ['scene14'] -> PASS
PROOF-9 [D18] val is strict-H-free (H reserved for train/test) and has >=1 positive scene: H-in-val=0, pos-scenes=['scene10', 'sceneD3'] -> PASS
PROOF-10 PROVISIONAL-HOLD scenes appear in NO split: ['scene11', 'scene13', 'scene19', 'sceneD4'], 0 leaked -> PASS
```

top-strict-H pool (top 8 by strict-H frame count): ['scene14', 'scene09', 'scene17', 'scene15']
