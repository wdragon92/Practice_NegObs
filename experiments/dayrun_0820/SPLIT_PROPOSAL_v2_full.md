# SPLIT_PROPOSAL v2 — PROVISIONAL 승인 대상

manifest: `experiments/dayrun_0820/dataset_manifest_v2_full.json` · seed 42 · 29 eligible scenes (33 in manifest − 4 held) / 2832 frames (192 held out)
hard-negative arg: ['sceneN3']
test L1-to-global tier distance (incl. off-arm preference term): 0.1162; val 0.2088

## v2 change — one train H-scene moved to val (PROVISIONAL 승인 대상)

**Why.** In split v1 val carried 0 strict-H frames, so the checkpoint selector (and tau*) could not see the headline metric at all; recipe v2 scores checkpoints with `0.5*val_cell_F1 + 0.5*val_H_frame_recall`, which needs H frames in val.

**Rule.** Among TRAIN scenes with >= 5 strict-H frames, move the one with the FEWEST to val. **test is untouched** (train -> val only), so `--force-test scene05,scene07,scene14,scene15,scene18,sceneC2,sceneN3` and the headline test set are unchanged.

**Decision.** moved `scene20` (strict-H 6) train -> val: the FEWEST strict-H among train H-scenes with >= 5 (candidates: scene20=6, scene17=33, scene12=48, scene09=60). Keeps the largest H block (scene17=33, scene12=48, scene09=60) in train for supervision while val gains 6 H frames to select checkpoints on. test untouched.

| candidate train H-scene | strict-H frames | moved |
|---|---|---|
| scene20 | 6 | **YES** |
| scene17 | 33 | no |
| scene12 | 48 | no |
| scene09 | 60 | no |

val strict-H: 0 → **6** · train strict-H: 147 → **141** · test strict-H: **96** (unchanged)

## PROVISIONAL-HOLD (아침 결재 대상)

`--exclude-scenes @experiments/dayrun_0820/annotations/hold_scenes.json` → **4 scene(s) in NO split** (not train, not val, not test). Per D14④ these are batch-1 non-stair drop scenes that came out all-negative under the D10 step gate; holding them out keeps a possibly-wrong label out of the headline metric until the morning ruling. Re-run this script without `--exclude-scenes` (or with a trimmed list) once the gate is adopted or reverted.

| scene | frames | off-arm | strict-H |
|---|---|---|---|
| scene11 | 48 | 24 | 0 |
| scene13 | 48 | 24 | 0 |
| scene19 | 48 | 24 | 0 |
| sceneD4 | 48 | 24 | 0 |

## Assignment

| split | n scenes | scenes |
|---|---|---|
| train | 19 | scene01, scene02, scene03, scene04, scene06, scene09, scene10, scene12, scene16, scene17, scene21, sceneC1, sceneC4, sceneD1, sceneD2, sceneN1, sceneN2, sceneN4, sceneN5 |
| val | 3 | scene08, scene20, sceneD3 |
| test | 7 | scene05, scene07, scene14, scene15, scene18, sceneC2, sceneN3 |
| **HOLD** | 4 | scene11, scene13, scene19, sceneD4 |

## Tier distribution (frame counts, share)

| split | V | E | H | off | frames |
|---|---|---|---|---|---|
| train | 438 (0.32) | 21 (0.02) | 141 (0.10) | 768 (0.56) | 1368 |
| val | 75 (0.32) | 6 (0.03) | 6 (0.03) | 144 (0.62) | 231 |
| test | 180 (0.25) | 45 (0.06) | 96 (0.13) | 408 (0.56) | 729 |
| **global** | 693 (0.30) | 72 (0.03) | 243 (0.10) | 1320 (0.57) | 2328 |

## Per-scene

| scene | split | frames | off-arm | strict-H | V | E | H | off |
|---|---|---|---|---|---|---|---|---|
| scene01 | train | 48 | 24 | 0 | 24 | 0 | 0 | 24 |
| scene02 | train | 48 | 24 | 0 | 15 | 9 | 0 | 24 |
| scene03 | train | 144 | 72 | 0 | 57 | 0 | 0 | 72 |
| scene04 | train | 144 | 72 | 0 | 72 | 0 | 0 | 72 |
| scene05 | test | 144 | 72 | 0 | 72 | 0 | 0 | 72 |
| scene06 | train | 48 | 24 | 0 | 0 | 0 | 0 | 24 |
| scene07 | test | 144 | 72 | 0 | 21 | 0 | 0 | 72 |
| scene08 | val | 96 | 48 | 0 | 21 | 0 | 0 | 48 |
| scene09 | train | 144 | 72 | 60 | 6 | 0 | 60 | 72 |
| scene10 | train | 48 | 24 | 0 | 15 | 0 | 0 | 24 |
| scene11 | **HOLD** | 48 | 24 | 0 | 0 | 0 | 0 | 24 |
| scene12 | train | 144 | 72 | 48 | 24 | 0 | 48 | 72 |
| scene13 | **HOLD** | 48 | 24 | 0 | 0 | 0 | 0 | 24 |
| scene14 | test | 144 | 72 | 60 | 6 | 0 | 60 | 72 |
| scene15 | test | 144 | 72 | 36 | 30 | 0 | 36 | 72 |
| scene16 | train | 48 | 24 | 0 | 24 | 0 | 0 | 24 |
| scene17 | train | 144 | 72 | 33 | 27 | 0 | 33 | 72 |
| scene18 | test | 144 | 72 | 0 | 27 | 45 | 0 | 72 |
| scene19 | **HOLD** | 48 | 24 | 0 | 0 | 0 | 0 | 24 |
| scene20 | val | 144 | 72 | 6 | 36 | 0 | 6 | 72 |
| scene21 | train | 48 | 24 | 0 | 21 | 3 | 0 | 24 |
| sceneC1 | train | 96 | 48 | 0 | 45 | 0 | 0 | 48 |
| sceneC2 | test | 48 | 24 | 0 | 24 | 0 | 0 | 24 |
| sceneC4 | train | 144 | 72 | 0 | 69 | 0 | 0 | 72 |
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
PROOF-1 scene count: 19 train + 3 val + 7 test = 29 == 29 eligible scenes (33 manifest − 4 held) -> PASS
PROOF-2 no scene in two splits: 0 duplicates -> PASS
PROOF-3 no ELIGIBLE scene unassigned: 0 -> PASS
PROOF-4 every non-held frame resolves to exactly one split: 0 bad of 2640 (192 frames held out) -> PASS
PROOF-5 both arms (on/off) of a scene share its split (split key is scene_id): 0 violations -> PASS
PROOF-6 test size 7 in 7±1 and 24.1% of the 29 eligible scenes (target 20-25%) -> PASS
PROOF-7 test contains >=2 top-strict-H scenes: ['scene14', 'scene15'] -> PASS
PROOF-8 test contains >=1 hard-negative ['sceneN3']: ['sceneN3'] -> PASS
PROOF-7b [D18] forced-into-test: ['scene05', 'scene07', 'scene14', 'scene15', 'scene18', 'sceneC2', 'sceneN3'] -> PASS
PROOF-9 [v2] val carries strict-H (selector can see the headline metric) and >=1 positive scene: H-in-val=6, pos-scenes=['scene08', 'scene20', 'sceneD3'] -> PASS
PROOF-10 PROVISIONAL-HOLD scenes appear in NO split: ['scene11', 'scene13', 'scene19', 'sceneD4'], 0 leaked -> PASS
PROOF-11 [v2] H-scene moved train->val: moved=scene20 (strict-H 6; candidates scene20=6, scene17=33, scene12=48, scene09=60), val strict-H now 6 (was 0), train strict-H 141, test UNCHANGED ['scene05', 'scene07', 'scene14', 'scene15', 'scene18', 'sceneC2', 'sceneN3'] -> PASS
```

top-strict-H pool (top 8 by strict-H frame count): ['scene09', 'scene14', 'scene12', 'scene15', 'scene17', 'scene20']
