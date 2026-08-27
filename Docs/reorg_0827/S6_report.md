# S6 — concluding the interrupted tracks (2026-08-27)

Branch `chore/reorg-0827`, repo `/home/vislab/Desktop/work_sy/Practice_NegObs`.
Nothing was committed. `Practice_NegObs_edge` was not touched. **One GPU render was
taken** (the brief's step 2), under `flock -o -w 3600 -E 201 /tmp/negobs_gpu.lock`, plus one
bounded Isaac Sim GUI boot to verify the GUI answer; nothing else used the GPU, no training.
No labeling, tier or edge-mask work was done — that is a later stage. Counts come from
`os.walk` / `ps` / `sha256sum`, never from `grep -r` (this shell's `grep` is ugrep with
`--ignore-files`).

**Status: PASS.** All 12 gates green.

| headline | measured |
|---|---:|
| track 1 — warehouse `ours` columns | `out/readout.csv` **64 rows · 12 new columns · 0 empty/NaN** |
| track 1 — report | `experiments/gazebo_wh_0824/WAREHOUSE_VARIANT.md` **107 lines** (Korean) |
| track 2 — render | scene01 **2 cuts / 25 s** (12.264 s/cut), `exit 0`, GPU lock held and released |
| track 2 — overlay | `view_overlay.py` wrote **2** `_grid.png` (1920×1080) |
| track 2 — guide | `Docs/guides/ISAAC_HANDSON.md` **120 lines**, every command executed |
| track 3 — edge labels | **not started** (owner's later stage) — row filled as *pending* only |
| ledger | `DECISIONS.md` **D102 · D103 · D104** appended (D1–D101 → D1–D104) |
| symlinks total / broken | **5,734 / 0** (S5's adjusted invariant held) |
| `PREREG_V3.md` / `PREREG_CUEOFF.md` sha256 | `05f41322…f56a` / `9c4733bb…56b1` **unchanged** |
| `import_check.py --all` | 247 modules · OK 209 · EXC 36 · SYSTEMEXIT 2 · **0 files changed**, rc 0 |
| `smoke_round_sites.py` / `test_round_dir.py` | **33 PASS · 0 FAIL** / **15 / 15** |
| `s5_residual_gate.py` / `s5_link_check.py` | **14 / 14 PASS** / **0** breakage into reorg paths |
| `__pycache__` · tmux · GPU | **0** · none · **no compute processes**, lock free |

---

## 1. Track 1 — the warehouse variant, finished and reported

### 1.1 Where it was cut, and how it was repaired

`tools/readout.py` (mtime 08-24 13:47, the token-limit minute) raised
`AttributeError: module 'project_hole' has no attribute 'APPROACH_Y'` in `gt_cells()`:
`project_hole` imports only `HOLE_X0/X1`, `HOLE_Y0/Y1`, `FLOOR_TOP_Z` from `make_wh_worlds`,
so the approach-lane constant was never there. The author had also left an open question in
that line's comment (`# +y is camera-left after yaw = pi? see below`).

The repair does **not** restore the constant. It delegates:

* the wedge test is now `labeling/labeler.py::polar_cells` — literally the function that
  produced every training label — called on a 33×33 lattice over the still-open void;
* the camera comes from the capture manifest (static camera models → exact pose), not a
  constant;
* the open question is answered by construction: `polar_cells` rotates by `-yaw` itself, and
  for `yaw = π` that yields `x_c = eye_x − x`, `y_c = −(y − eye_y)`, which is exactly
  `gridspec_v1`'s "A = image-left = +azimuth" convention. The sector/band boundary handling
  is now the labeler's `searchsorted`, not a hand-rolled comparison chain.

Sanity of the result: GT cells widen to `A1 B1 C1 D1 E1` at 0.5 m (the 0.80 m opening subtends
±38° there) and shrink to `B2 C2 D2` at ≥2.0 m — the band edges (0–2 / 2–5 m) land where the
standoffs say they should.

### 1.2 The CSV

`out/readout.csv` keeps its **64-row shape** (4 worlds × 8 approach views × 2 YOLO arms) and
every YOLO column, and gains 12: `gt_cells`, `n_gt`, and per model
`ours_<model>_{max_p,fire,p_gt,gt_hit,top_cell}` for `v2_rgb_s42` and `v3a_rgb_s42`. The `ours`
values do not depend on the YOLO arm, so they repeat on the `roi` and `full` rows by
construction; a missing per-model json would be a `KeyError`, never a blank cell — checked:
**0 empty / NaN** in all 12. Also written: `out/readout_ours.csv` (64 rows, long form),
`out/readout.json` (`rows` 64 / `yolo` 64 / `ours` 64 / `geo` 8) and `out/readout_tables.md`
(the markdown tables the report quotes).

**The only YOLO numbers that changed** against the 08-24 file are `wh_e`'s, and they changed
because of the author's own in-flight correction that the traceback interrupted: `wh_e`'s
region is the **still-open 0.18 m strip**, not the whole opening. Effect: `void_px` on 16 rows,
`void_roi_px` on 6, and `centre` 1→0 on two rows (`rs_d0.5`, `rs_d0.7`, arm `roi`) — the best
box's centre sits on the pallet-covered part, not on the open void. Every `wh0` / `wh_h` /
`wh_hc` YOLO cell is byte-identical to 08-24.

### 1.3 What the report says (and refuses to say)

`WAREHOUSE_VARIANT.md` (Korean, 107 lines) carries the two tables and then the limits, each one
measured rather than asserted:

| claim in the report | how it was measured |
|---|---|
| the floor is blown out | ≥250/255 pixels inside the node's trapezium: `wh0` **84.5 %** at 0.5 m → **99.3 %** at 1.1 m → **99.9 %** at 3.4 m |
| at 0.5 m the H worlds are a wall of pallet | **88.2 %** of the frame differs from `wh0` (22.1 % at 1.5 m); the frame opened and inspected — wood grain, no floor, no horizon |
| `wh_h` ≡ `wh_hc` | all 8 approach views: **0.0000 %** of pixels differ by >10, identical SHA256; only `overview` differs (from 7 m up the hole is visible) |
| deterministic renderer | `_000` = `_001` = `_002` on **8/8** approach views; `overview` alone has a different first frame |
| single seed, no σ | one checkpoint per model, stated as diagnostic-only |
| the paper's node gate cannot be fully reproduced | its other branch needs the aligned depth image static Gazebo cameras do not publish; the 3/8 "gate passes" are the confidence+trapezium branch alone |

The honest headline is that this rig **cannot ask** "does it detect the hole" — the H pair is
pixel-identical, so identical outputs are a construction, not a finding. What it can show is
"reacts to the pallet cue", and it does: v2 hits a GT cell in **0.000** of views in all four
worlds; v3a hits **0.000** in `wh0` where the hole is plainly visible but **0.500** in `wh_hc`
where there is no hole at all, with mean p(GT) 0.050 (`wh0`) vs 0.340 (`wh_hc`). Conclusion
recorded: a re-reproduction of D48 / D97 / D100 in the paper's own world, no new claim; plus
three requirements for a better rig (farther standoffs, exposure fix, a twin whose occluder
differs so the two images are not identical).

### 1.4 git hygiene

`.gitignore` gained `experiments/gazebo_wh_0824/frames/**/*.png`, the same shape as the
existing `experiments/weekend_0823/gazebo/frames/**/*.png` rule, with a comment saying what is
deliberately kept. Verified with `git check-ignore`: the PNGs are ignored; the per-world
`*_cap_manifest.json`, `frames/SHA256SUMS.txt` and all of `out/` are not. `git add -An` on the
directory would stage **195 files / 824 KiB, 0 PNGs** (the 108 frames are 24 MB).

## 2. Track 2 — the hands-on guide, every command executed

`Docs/guides/ISAAC_HANDSON.md` (Korean, 120 lines; `Docs/guides/` is new). Nothing in it is
guessed:

1. **Render.** `run_data_render.py --run 260827_handson --scenes scene01 --conds L0 --cams 2
   --seed 20260827` inside the GPU lock: **2 cuts, 25 s** (12.264 s/cut), manifest `exit 0`,
   `cuts 2`. The `--plan` variant was run first (no GPU). The guide warns about the
   `UnboundLocalError: local variable 'math'` that fires at teardown — a **pre-existing** defect
   that is in `HEAD` and that `run_data_render.py:594` documents in its own comment (it raises
   after every artefact is on disk); and it warns that re-using an existing `--run` name resumes
   instead of rendering (`data_root` → `round_dir_or_flat`, `--resume` defaults on).
2. **Overlay.** `view_overlay.py` run on both frames → `L0__s20260827__000{0,1}_grid.png`; the
   real console output is pasted into the guide. Its docstring example pointed at a
   `train/scene01/…` path that does not exist (the round has `val/`), so the example was
   corrected to a path that does.
3. **Galleries.** Structure `look_check/_review/{w2,w3,w4}/<round>` confirmed; the four
   unreviewed w4 galleries confirmed present; `eog <gallery dir>` launched on `DISPLAY=:1`
   (window "Image Viewer" seen, then closed).
4. **GUI — it works, verified.** With `NEGOBS_CAPTURE` unset the scene boots non-headless
   (`scenes/main/scene01_campus_stairs.py:1602`, `{"headless": capture_mode}`). Booted under the
   lock: window **`Isaac Sim Python 4.5.0`** present within ~10 s (`wmctrl -l`), the scene's own
   controls printed to the terminal (`우클릭+WASD 비행 · P 패스트레이싱 · C 스크린샷 · [ ] 태양 방위`)
   together with a 7-line per-scene checklist. Terminated deliberately (exit 143); afterwards:
   0 Isaac processes, no window, GPU back to idle, lock free.

**Filing.** `dataset/260827_handson` (10,249,930 B) → `dataset/misc/260827_handson` by
`os.rename` (gitignored tree, same filesystem asserted first), with the four bookkeeping edits:
`ROUNDS.json` **196 → 197** entries, `dataset_moves.tsv` **196 → 197** rows, the round's own
`manifest.json` `out:` field re-pointed (matching how `260824_handson` reads), and
`dataset/README.md`'s `misc/` row (1 → 2 rounds) plus its three count lines. Both resolvers
verified on the moved round: `negobs_round 260827_handson` and `variation_kit.round_dir(...)`
return `…/dataset/misc/260827_handson`.

## 3. Ledger and the living documents

* **`experiments/mainrun_0819/DECISIONS.md`** — appended **D102** (warehouse: the cut point,
  the delegation repair, the measured tables, the rig's limits, the gitignore rule),
  **D103** (the guide: every verified command, the render, the GUI finding, the filing) and
  **D104** (the 0827 tidy-up: what moved in S1–S5, 10.73 GiB deleted with rebuild recipes, the
  invariants, the re-runnable gates, where the logs live, what was deliberately not touched).
  Same one-paragraph Korean style as D96–D101. D104 deliberately does **not** spell the retired
  `Docs/experiment/` path — the first draft did, and `s5_residual_gate.py` caught it; the entry
  now names the folders instead and says why.
* **`experiments/v3_0823/STATUS.md`** — dated heartbeat `## 목 (2026-08-27)`: the campaign
  itself is still stopped (19 approvals pending, no training), this day was the tidy-up plus
  the two conclusions, and the only GPU use in this window was the one 25 s render.
* **`Docs/campaign/status/PROJECT_STATE.md`** — the 끊긴 세 갈래 table's `상태 (2026-08-27)`
  column is filled: warehouse **결론 남김 (D102)** with the report link and the one-line finding;
  guide **결론 남김 (D103)** with the guide link; edge labels **대기 — S6 범위 밖**, "Codex 구현
  폐기 예정 · 소유자의 V/E/H 재설명 후 처음부터 재구현", worktree left alone. Its reading list
  now ends at D104 and points at the new guide.
* **`Docs/INDEX.md`** — new `guides/` section, one row.

## 4. Gates

| gate | required | measured | verdict |
|---|---|---|---|
| `py_compile tools/readout.py` | clean | clean | PASS |
| `py_compile experiments/v3_0823/code/view_overlay.py` | clean | clean | PASS |
| `out/readout.csv` rows | 64 | **64** (+ header) | PASS |
| `out/readout.csv` new columns | present | **12** (`gt_cells`, `n_gt`, 5 × 2 models) | PASS |
| `ours` columns NaN/empty | 0 | **0** (all numeric values finite) | PASS |
| render produced files | yes | 2 PNG + `variation.json` + `manifest.json`, `exit 0` | PASS |
| `view_overlay` wrote `_grid.png` | yes | **2** files, 1920×1080 | PASS |
| `smoke_round_sites.py` | non-zero everywhere | **33 PASS · 0 SKIP · 0 FAIL** | PASS |
| `import_check.py --all` | rc 0, nothing moved | 247 modules, rc 0, **0 files changed content** | PASS |
| `test_round_dir.py` | 15/15 | **15/15** | PASS |
| `s5_residual_gate.py` | 14/14 PASS | **14/14** | PASS |
| `s5_link_check.py` | 0 breakage into reorg paths | **0** (49 pre-existing ghosts unchanged) | PASS |
| symlinks | 5,734 total / 0 broken | **5,734 / 0** | PASS |
| `PREREG_V3.md` / `PREREG_CUEOFF.md` | sha256 unchanged | both unchanged | PASS |
| `__pycache__` | 0 | **0** | PASS |
| GPU lock / tmux / GPU procs | released / none / none | lock free, no tmux server, no compute apps | PASS |

**One process note.** The first `import_check.py --all` run reported `!! 1 files changed
content: experiments/mainrun_0819/DECISIONS.md` and exited 1. That was **my** edit — the D104
rephrase landed while the sweep was in flight — not a defect of the tree. The run was allowed
to finish (never interrupted, per S5's warning), then a second full sweep was run with no
concurrent edits: **rc 0, 0 files changed**, `hazgate.json` / `prims2.json` created and removed
by the script itself. The table above quotes the second run. Each `--all` sweep took ≈ 9 min.

## 5. Files this stage produced or changed

```
NEW   experiments/gazebo_wh_0824/WAREHOUSE_VARIANT.md      107 lines, Korean
NEW   Docs/guides/ISAAC_HANDSON.md                         120 lines, Korean
NEW   Docs/reorg_0827/S6_report.md                         this file
EDIT  experiments/gazebo_wh_0824/tools/readout.py          gt_cells -> labeler.polar_cells; merged CSV
GEN   experiments/gazebo_wh_0824/out/readout.csv           64 rows, YOLO + 12 ours columns
GEN   experiments/gazebo_wh_0824/out/readout_ours.csv      64 rows, long form
GEN   experiments/gazebo_wh_0824/out/readout.json          rows/yolo/ours/geo
GEN   experiments/gazebo_wh_0824/out/readout_tables.md     the markdown tables
EDIT  .gitignore                                           + gazebo_wh_0824/frames/**/*.png
EDIT  experiments/v3_0823/code/view_overlay.py             docstring example -> a path that exists
EDIT  experiments/mainrun_0819/DECISIONS.md                + D102, D103, D104
EDIT  experiments/v3_0823/STATUS.md                        + 2026-08-27 heartbeat
EDIT  Docs/campaign/status/PROJECT_STATE.md                끊긴 세 갈래 status column + reading list
EDIT  Docs/INDEX.md                                        + guides/ section
EDIT  dataset/README.md                                    misc/ row 1 -> 2, counts 196 -> 197
EDIT  dataset/ROUNDS.json                                  + "260827_handson": "misc"  (197 entries)
EDIT  Docs/reorg_0827/dataset_moves.tsv                    + 1 row (197)
NEW   dataset/misc/260827_handson/                         2 PNG + 2 _grid.png + variation.json + manifest.json
NEW   look_check/logs/260827_handson.log                   the render log (gitignored tree)
```

`dataset/`, `look_check/` and `experiments/gazebo_wh_0824/` are gitignored or untracked, so the
tracked diff of this stage is: `.gitignore`, `Docs/INDEX.md`,
`experiments/mainrun_0819/DECISIONS.md`, `experiments/v3_0823/STATUS.md`.

## 6. What S6 deliberately did not do

* **No labeling, no tier classification, no edge-mask work.** Track 3 is the owner's later
  stage; its PROJECT_STATE row was filled in as *pending* and nothing else was touched.
  `Practice_NegObs_edge` is untouched.
* **No commit, no stash, no checkout.** The orchestrator commits.
* **No re-render of the panels** that S5's docstring edits will change on their next run
  (`verdict_panels.py:559` draws the grouped path into the panel footer) — still true after S6.
* **No new dated document family.** One guide, one report, one ledger, one living status file.

## 7. Notes for the orchestrator

1. **Invariant is 5,734 / 0** (S5's deliberate −10), re-verified after every S6 write.
2. **The tracked diff added by S6 is four files** (§5) — everything else is gitignored or was
   already untracked. `experiments/gazebo_wh_0824/` remains untracked in full; committing it
   now stages 195 files / 824 KiB thanks to the new ignore rule.
3. **`import_check.py --all` needs ~9 min and an idle tree** — do not edit anything while it
   runs, or it will (correctly) report your own edit as a change.
4. **New untracked paths the commit must pick up**: `Docs/guides/`, `Docs/reorg_0827/`,
   `experiments/gazebo_wh_0824/`, `experiments/v3_0823/code/view_overlay.py` — `git status`
   shows them as `??` because they are new directories/files, not because they are ignored.
5. **D-numbering continues at D105.** The next entry after the tidy-up is the edge-label
   rebuild, which is not yet started.
