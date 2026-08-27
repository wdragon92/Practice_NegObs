# probe_holes_0820 — C1 hole-type zero-shot probe

**Status: PREPARED, NOT RUN.** Every CPU-checkable thing passes; the render and
the eval need the GPU lock. One command starts the whole thing.

```bash
bash experiments/probe_holes_0820/run_probe.sh
```

**Evaluation only.** No frame produced here may enter training, ever
(`OVERNIGHT_BRIEF_0820_v1.md` §4 C1: "훈련 편입 절대 금지 — 평가 전용"). There is
no optimiser and no backward pass anywhere in this directory.

---

## 1. What this answers

The paper's claim is about the **H tier** — a drop with zero contributing pixels
is still predictable from context. Every drop in the frozen corpus is a stair or
an edge. This probe asks whether the nine frozen recipe-v2 checkpoints keep any
of that on a **hole**: a local depression surrounded by ground on all four
sides, which has no run of nosings and no linear lip to follow.

Three scenes, one question each:

| scene | file | question |
|---|---|---|
| `probeH1` | `scenes/probe/probeH1_near_hole.py` | does a hole read at all, up close, with its interior in view? (**band 1**, the weakest band) |
| `probeH2` | `scenes/probe/probeH2_offpath_hole.py` | can the model light one lateral sector and leave the corridor beside it dark? (**adjacent hazard-free sector firing**) |
| `probeH3` | `scenes/probe/probeH3_hidden_hole.py` | does H recall survive a drop TYPE it has never seen? (**the headline**) |

A null result is a result. If H recall collapses on `probeH3` while V/E survive
on H1/H2, the H claim is drop-type bound and that belongs in the limitations
section. Both outcomes satisfy the brief's Tier-3 acceptance rule.

---

## 2. Layout

```
experiments/probe_holes_0820/
  run_probe.sh          THE entry point — render -> label -> eval, or one --phase
  probe_driver.py       render driver shim (see §4); also --check-run and --scene-proc
  eval_probe.py         --step split | tiers | eval   (the zero-shot half)
  check_probe_cpu.py    nine CPU checks; run this before asking for the lock
  render_configs/       probeH{1,2,3}_{on,off}.json  = {"hazard_hole": true|false}
  logs/probe.log        appended, timestamped
  annotations/ eval/ viz/     produced by the run
scenes/probe/
  probe_common.py       the twin contract + the shared builders
  probeH1_near_hole.py  probeH2_offpath_hole.py  probeH3_hidden_hole.py
  <symlinks>            the same set scenes/batch1/ uses (assets, scene_common, kits)
```

Outputs land in `dataset/v2_probes/260821_probe_on/probe/<scene>/` and
`dataset/v2_probes/260821_probe_off/probe/<scene>/`. **`probe` is a fourth split name** —
see §4 — so a probe frame can never be mistaken for corpus train/val/test.

---

## 3. The round

* 3 scenes x 2 arms x conds **L0, L5, L7** x **8 cameras** = **144 frames**
* seed **20260822**, sidecars **ON** (per-cut `.depth.npy`, per-scene `heightmap.npy`)
* rounds `260821_probe_on` / `260821_probe_off`; `guard_run_name` refuses anything else
* labels: `labeler.py` on the round pair, **gridspec_v1** (5 sectors x 4 bands = 20 cells)
* eval: the nine frozen v2 checkpoints under `experiments/dayrun_0820/runs/v2/`,
  `tau_op = 0.5` **frozen** (absolute rule 3) and never re-fitted — `split_probe.json`
  leaves `val` empty on purpose so `--tau-star auto` is impossible
* per checkpoint: `eval_polar` (or `eval_b2_polar`) -> `split_per_frame` ->
  `twin_analysis` -> 4 `make_viz` panels

**Estimated GPU time, render only: 12–20 min.** Not from the SP-3 constants —
`probe_driver.py --plan` prints 5.4 min/arm from those and they exclude
sidecars. From the measured sidecar rounds instead: `260819_main_on` averaged
**5.9 s/cut** over 792 cuts and `260820_boost_h_on` **5.59 s/cut**, ranging
3.26 s/cut on a light scene (scene15) to 7.48 on a heavy one (scene09), wall
time including the boot. These probes are light (tens of prims, no vegetation,
no ground_kit pass), so 144 cuts x ~3.5–4.5 s ~= 9–11 min, call it 12–20 with
the six boots and lock acquisition. The brief's estimate was 30–60 min.

Zero-shot eval adds roughly 5–10 min on the GPU for all nine checkpoints
(144 frames each). It also runs on CPU in ~15 min: `PROBE_CPU_EVAL=1`.

### Shrinking it (brief §5 fallback: "씬 3→2, 조명 3→2")

```bash
bash run_probe.sh --scenes probeH1,probeH3          # drop the off-path scene
CONDS=L0,L7 bash run_probe.sh                       # drop L5
```
Record the reduction if you use it. `probeH3` is the one to keep last: it is the
scene that carries the headline question.

---

## 4. The two blockers, and how they were resolved

`run_data_render.py` could not see these scenes for two independent reasons.
They are not equally dangerous and they were not resolved the same way.

### (a) Discovery — the glob, not the recursion

`run_data_render.scene_files()` globs `scenes/{main,batch1}/scene*.py` and keys
each hit by `basename.split("_")[0]`. It is **not recursive**, and the pattern is
`scene*`, so a file named `probe*.py` is invisible **wherever it sits** — moving
the probe files into `scenes/batch1/` would not have helped unless they were
also renamed `scene*`, which would have hidden them among the corpus scenes in
every `ls`, every gallery and every `--scenes` list.

Resolved by registering the three files explicitly in `probe_driver.install()`.
`scenes/probe/` mirrors `scenes/batch1/`'s symlink layout exactly (`assets`,
`look_check`, `scene_common.py`, the kits), because `scene_common` derives
`ASSETS_DIR` from `os.path.abspath(__file__)`, which does **not** resolve
symlinks — so the assets symlink is what makes textures resolve from the new
directory. `check_probe_cpu.py` check 1 asserts both halves: that the shim finds
all three, and that stock `scene_files()` finds none of them.

### (b) The ledger — the trap

`vk.ledger(scene)` raises `SystemExit` for an unknown scene, so the probe scenes
have to be in `vk.AZ_LEDGER`. But `vk.split_map()` builds the split by
**shuffling `sorted(AZ_LEDGER)` and slicing** (`variation_kit.py:831`), so
adding three names **at source level re-shuffles the corpus**. Measured, not
guessed — `check_probe_cpu.py` check 3 reproduces it every run:

> a SOURCE-level ledger edit would move **19 of 33** corpus scenes:
> scene01, scene02, scene05, scene06, scene09, scene10, scene12, scene16,
> scene17, scene18, scene19, scene20, scene21, sceneC1, sceneC2, sceneD1,
> sceneN1, sceneN2, sceneN5

That would change the `<split>/` directory any future corpus render files those
scenes under, and it would break `variation_kit._selfcheck`'s
`chk("33 scenes", len(AZ_LEDGER) == 33)`. Absolute rules 1, 2 and 4 forbid it,
and an exploratory track — the **first** thing on the brief's §5 discard list —
has no business leaving a scratch on the frozen corpus's provenance.

So the rows are injected **at runtime**, after `vk.split_map(0)` has already
been called once and cached. The cache hit means the 33 corpus scenes keep
byte-identical splits; the probe rows are then written into that cached map with
the split `"probe"`. `install()` re-verifies all 33 afterwards and aborts on any
movement (`SPLIT GUARD`), in the driver process **and in every per-scene
subprocess** — the subprocess re-enters through this same file because
`install()` rebinds `run_data_render.__file__`, which is what `drive()` uses to
build the `--scene-proc` command line.

**Ledger class: `C'`, borrowed from sceneD2 floor_opening**, and recorded as
borrowed in the row's own `basis` string. sceneD2 is an outdoor concrete opening
in flat paving that the SP-2 sweep measured at +-35 deg with no criterion-B
firing at any arm (`variation_kit.py:157-159` names it). The probes reuse
sceneD2's light rig verbatim (`probe_common.probe_light`), which is what makes
the borrowing defensible rather than convenient. Rejected alternatives: `_AZ_FREE`
(sceneC1/C4/D4) is for sunless or sealed-indoor scenes and these are outdoor
with a sun; `label_shadow` (sceneN1) is for a scene whose LABEL is a shadow.

Consequence, computed: **L0, L5 and L7 are all admissible on all three scenes,
and no condition substitution is needed** — unlike sceneC1/C2/N1/scene15 in the
corpus rounds. C' gives `daz_data` 35 deg, and L5's forced-off-noon minimum of
37.0 deg is covered by `DAZ_DATA_EXTRAP = 60`, granted to any scene that is
neither `label_shadow` nor `c_bound`.

`scripts/check_data_run.py` also calls `vk.ledger()` (its check 2 is the azimuth
conformance test), so it is invoked as `probe_driver.py --check-run <run>`.

### Files touched outside this directory

`scenes/probe/` (new) only. **No existing scene, kit, script or corpus artefact
was modified.** `git status` should show additions and nothing else.

---

## 5. The twin contract

The brief demands byte-identical camera poses across the arms. These scenes go
further and make the pair **exact by construction**, which is the direct answer
to the D15/D17 defect that nightrun B5 is currently re-checking (the D20 0.15 m
pairing tolerance exists because some corpus toggles move `ground_z` under the
camera).

Five rules, implemented once in `probe_common.py` and asserted pre-boot in both
arms by `twin_audit()`:

1. ground is **four paving boxes around the opening**, never one box with a hole
   in it — there is no CSG, and a covering box is what makes a hole invisible to
   `AabbPrefilter.ground_z`;
2. the only prims that differ between arms are the 5-prim pit liner + floor (ON)
   and the 1-prim flush patch (OFF);
3. **every hazard-ON prim's top is strictly below the paving top**, so wherever
   a liner reaches back under the walked surface the paving still wins the
   `max(hi_z)` and the heightmap reading is unchanged. This is the airtight one;
4. the OFF patch is **exactly** the opening in plan, so it never overlaps a
   paving box it is flush with;
5. **no dressing is hazard-correlated.** Kerbs, bollards, planters, facade and
   even the excavation spoil heap are authored identically in both arms. In the
   C2/N3 caveat the off arm lost its leaf mound along with the drop, so the twin
   delta mixed "the drop went away" with "the decoration went away". Here any
   twin delta is attributable to the hole and to nothing else.

Belt and braces: nothing the toggle touches reaches west of `x = -1.00`, while
cameras stand at `x = -d`, `d in [1.2, 12]`. Measured margins to the closest
possible camera: probeH1 **0.29 m**, probeH2 1.29 m, probeH3 1.79 m.

Consequence: `twin_analysis.py` runs at the **default `--tol 1e-6`**, not at
D20's 0.15 m. If it reports excluded pairs, that is a finding about the scenes
and goes in the report — it does not get fixed by widening the tolerance.

### Why no `fuse_heightmap.py` step

Every prim in these scenes is an axis-aligned box, so the top-down AABB ray IS
the exact surface and `heightmap.npy` needs no depth-fusion correction. (The one
non-box is the spoil ellipsoid, whose AABB over-reads by its own height — but it
is identical in both arms, so it contributes exactly 0 to the twin difference,
and it sits outside every hazard sight wedge.) `SIDECAR_ORACLES` has no probe
entry and needs none.

---

## 6. Compositions (computed against the frozen camera draws)

The camera sampler is a pure function of `(scene, idx, seed)`, so the eight
draws per scene at seed 20260822 were computed on CPU **before** the geometry
was fixed, and the geometry was then placed against them. Each scene header
carries its own table; the summary:

| | opening | depth | result |
|---|---|---|---|
| **probeH1** | x [-0.50, 0.70] · y [-0.45, 0.45] = 1.20 x 0.90 m | 0.60 m | interior in view on **8/8** cuts (grazing-ray fall 0.11–1.35 m); **band 1 on cuts 1 and 2** = 6 frames per arm |
| **probeH2** | x [0.50, 1.30] · y [1.05, 1.85] = 0.80 x 0.80 m | 0.55 m | off the centre sector on **7/8** cuts; corridor \|y\| <= 1.0 hazard-free in every frame; cut 4 gives a **single** positive cell (B3a) with A3a and C3a empty |
| **probeH3** | x [1.00, 2.00] · y [-0.55, 0.55] = 1.00 x 1.10 m | 0.60 m | hidden behind a 0.80 m planter on **8/8** cuts (binding cut 6, margin 0.36 m) -> **tier H by construction** |

All 24 cuts put at least one GT-positive cell inside the 12 m grid, so no cut
degenerates to an empty label vector.

Two honest notes:
* **probeH1's near lip is at x = -0.50, not the conventional x = 0.** Only draws
  with d < 2.5 m can put a hole inside 2 m; at x = 0 exactly one cut reaches
  band 1, at x = -0.50 two do. Band 1 is the band the brief singles out as
  weakest, so the deviation buys double the evidence there. Nothing in the
  repository keys off the x = 0 convention — the labeller measures a twin
  heightmap difference, not an assumed edge.
* **probeH2's cut 1 (d = 9.10 m) lands in the centre sector.** A 1.45 m lateral
  offset subtends 8.6 deg at that range, which is inside sector C. That is
  geometry, and it is reported rather than engineered away: widening the offset
  to fix it pushes the mid-range cuts out to sector A, where only one adjacent
  sector exists and the false-firing measurement gets weaker on both sides.

---

## 7. CPU validation — what has actually been proved

```
$ python3 experiments/probe_holes_0820/check_probe_cpu.py
[1] scene discovery ........... 4/4 PASS
[2] ledger admissibility ...... 12/12 PASS   (3 scenes x {class, L0, L5, L7})
[3] SPLIT GUARD ............... 4/4 PASS     (33/33 corpus scenes identical)
[4] NEGOBS_SMOKE=1 gate ....... 6/6 PASS     (3 scenes x 2 arms, exit 0, no traceback)
[5] twin contract ............. 9/9 PASS
[6] composition ............... 6/6 PASS
[7] bash -n run_probe.sh ...... PASS
[8] driver --plan ............. 3/3 PASS     (72 cuts/arm, 0 refused conditions)
[9] adjacency metric .......... PASS         (synthetic per_frame vs hand computation)
check_probe_cpu: ALL PASS
```

Also verified: `bash run_probe.sh --dry-run` walks all three phases and prints
every command it would run, exit 0.

**What is NOT proved on CPU**, and is therefore the risk list:

1. **Nothing has been rendered.** The repo's `NEGOBS_SMOKE=1` gate is a
   *pre-boot* gate (GT-89) — it proves the file parses, the params are
   consistent and the geometry audits pass, but it never boots Isaac. The
   probe scenes put their audits **above** the gate so it proves as much as it
   can, but the first real render is still the first real render. Budget the
   brief's 45-minute abort rule for it.
2. **Tier assignment is predicted, not measured.** The V/E/H expectations come
   from grazing-ray geometry; the labeller decides from reprojected depth
   pixels. probeH3's prediction is the strong one (full occlusion, 0.36 m worst
   margin); probeH1's V-vs-E boundary on the far/low cuts (4 and 6, wall
   exposure 0.25 and 0.11 m) is the soft one. Read `TIER_TABLE.md` first.
3. **L7 darkness.** L7 is a sunless overcast, PT-only condition and the data
   rejection filter drops a frame whose mean luma < 30 or whose dark share
   > 70 %. A 0.6 m pit is shallow and its floor is a mid-grey gravel material,
   so this should be comfortable, but a close cut looking into the pit at L7 is
   where a rejection would appear. It shows as `n_rejected` in `variation.json`.
4. **b2 needs its backbone offline.** The b2 evals run with `HF_HUB_OFFLINE=1`;
   if the HF cache is cold those three checkpoints fail and the other six still
   produce a table.
5. **`make_viz --tier H` default.** `make_viz.py` defaults to picking H frames.
   On probeH1/H2 there may be few or none, in which case the panels fall back to
   whatever it finds; probeH3 will have plenty.
6. **probeH2's corridor clearance is 0.05 m** (opening near edge y = +1.05 vs
   the stated corridor half-width 1.00). It is a definitional margin, not a
   physical one — the pit liner and floor sit *under* the paving there, so the
   walked surface and the heightmap are both unaffected — but if the corridor
   claim is ever quoted as a clearance, quote 1.05 m from the walk axis, not
   0.05 m from the corridor edge.

---

## 8. DECISIONS entries this track needs

Ready to paste under the nightrun's D25+ numbering:

* **Probe scenes are registered at RUNTIME, not in `variation_kit.py`.**
  Adding three rows to `AZ_LEDGER` at source level re-shuffles `split_map` and
  moves 19 of the 33 corpus scenes between splits (measured; reproduced by
  `check_probe_cpu.py` check 3). `probe_driver.install()` therefore caches the
  frozen 33-scene map first, injects afterwards, gives the probes their own
  split name `probe`, and re-verifies the 33 on every invocation.
* **Probe ledger class = `C'`, borrowed from sceneD2** and recorded as borrowed
  in the row's `basis`. Not independently measured; the probes reuse sceneD2's
  light rig verbatim. Consequence: L0/L5/L7 all admissible, no substitutions.
* **probeH1's near lip is at x = -0.50**, deviating from the repository's
  "drop start edge = x = 0" convention, to bring a second frozen camera draw
  into band 1 (6 band-1 frames per arm instead of 3).
* **All probe dressing is arm-invariant**, including the excavation spoil, so
  the twin delta cannot contain a dressing component. This is the C2/N3 caveat
  designed out rather than measured around.
* **Twin pairing runs at `--tol 1e-6`, not D20's 0.15 m.** Excluded pairs would
  be a finding, not a nuisance to be tolerated away.
