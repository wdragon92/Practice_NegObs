# SPEC_CONFLICTS.md — where the repo contradicts the overnight-brief appendix A

Stance: **code is truth.** Each bullet states the spec assumption, the code fact with a
`file:line`, and what has to give.

---

* **The polar hazard grid does not exist and cannot be "extracted".**
  Spec assumes azimuth sectors × distance bands with a cell-positive coverage rule.
  Code: no such construct anywhere (searched `polar`/`sector`/`band`/`grid`/`5×3`/`방위`/`밴드`/
  `격자` across the whole tree, plus every ledger and report). The nearest match,
  `Docs/briefs/lighting_camera_variation_spec_v1.md:281` "프레임을 5×3 으로 나눈 15개 대표
  방향 레이", is implemented at `variation_kit.py:806-807` as the **camera-openness rejection
  fan** (`OPEN_RAYS, OPEN_MIN_HITS, OPEN_MIN_DIST = 15, 6, 1.0`, `variation_kit.py:663`).
  **Give:** the grid must be *declared* by tonight's design document, not cited as extracted.
  Only two conventions are inherited from code and must be honoured: azimuth 0 = camera forward
  = +X, CCW positive about +Z (`variation_kit.py:629-632`); negative pitch = looking down.

* **Camera pitch band: spec −15…+5°, code strictly [−20, −2].**
  `variation_kit.py:576` `pitch=(-10.0, 4.0, -20.0, -2.0)`, re-asserted as an acceptance gate at
  `check_data_run.py:238-244`. The sim **never** produces a level or upward camera, and does
  produce −20…−15 which the spec band excludes. The real-shoot protocol written tonight
  (`experiments/mainrun_0819/realworld/PROTOCOL_SHOOT.md:17`) asks for −15…+5.
  **Give:** either widen `CAM_DIST["pitch"]` for this round (a sampler change, and it invalidates
  the measured `R_REJECT = 0.020`, `variation_kit.py:691-693`), or accept that the sim-to-real
  evaluation set is pitched shallower than anything the model was trained on and say so.

* **Camera height band: spec 0.3–2.0 m, code U(0.25, 1.90) with a 1.20 m ceiling on four scenes.**
  `variation_kit.py:575` `h=(0.25, 1.90)`; `:592` `CAM2_SCENES = ("scene02","scene15","sceneD4",
  "scene11")`; `:595` `CAM2_H_MAX = 1.20`. The real-shoot protocol specifies eye height
  **1.5–1.8 m** (`PROTOCOL_SHOOT.md:16`) — a band that is never reached at all in those four
  scenes and occupies only the top ~21 % of the sampled range elsewhere.
  **Give:** state the mismatch, or add a height-stratified sub-arm; do not claim the sim covers
  the real band.

* **`260816_w4_final33_on` is not a hazard-on round.** `_on` is the realism **look layer**:
  `scripts/rounds/run_260816_w4_final33.sh:5` → `scripts/rounds/run_p2_all33.sh:29-30`
  `LOOKV=$([ "$LOOK" = "on" ] && echo 1 || echo 0)` → `:39 NEGOBS_LOOK_V1="${LOOKV}"`,
  `:41 NEGOBS_CAPTURE_DIR=".../${TAG}_${LOOK}"`. **No hazard-off render exists on disk anywhere.**
  The hazard-off twin is listed as approved-and-not-done at
  `Docs/briefs/lighting_camera_variation_spec_v1.md:742`.
  **Give:** the paired on/off arms are new work tonight, on code paths that have not been
  exercised in months — smoke-test before committing 33 scenes of GPU.

* **The hazard toggle key is not uniform across scenes.** Spec assumes one switch.
  Code: `"hazard_stairs"` on 30 scenes, but `"hazard_shadow_band"` (`sceneN1:52`),
  `"hazard_asphalt_patch"` (`sceneN2:85`), `"hazard_flush_grating"` (`sceneN5:53`).
  `_deep_update` merges silently, so a single `NEGOBS_SCENE_CONFIG='{"hazard_stairs":false}'`
  across all 33 leaves **three scenes with the hazard still on** and no error.
  **Give:** three extra invocations, or a per-scene key table.

* **Raw per-frame visibility (V/E/H, interior px count, edge-arc ratio, `tau_int`/`tau_edge`) has
  no producer.** Searched `tau_int`, `tau_edge`, `rim_band`, `interior_visible`, `edge_arc`,
  `visibility tier`. Zero hits in code; the only `V/E/H` in the tree is tonight's own
  `realworld/PROTOCOL_SHOOT.md`. The commit-`9f5e584` cue-coverage matrix is **not machinery** —
  `git show --stat 9f5e584` touches one `.md`; the raw file
  `Docs/reports/raw_260816/cue_matrix_result.json` is a multi-agent LLM read of **one** render
  round at **scene × cue × judge-preset** granularity, and the report says so itself
  (`dropoff_cue_matrix_v1.md:5-8`: "이것은 측정이 아니다").
  **Give:** V/E/H must be *computed* tonight from geometry (the only per-frame instrument that
  exists is `variation_kit.py:781 AabbPrefilter.ground_z` + `:766 _ray_t`), not harvested.

* **Depth, semantic and instance channels do not exist, and depth would not give the label
  anyway.** Zero Replicator/annotator/AOV code in the repo; every capture is
  `capture_viewport_to_file` → 8-bit RGB PNG (`run_data_render.py:395`,
  `scene_common.py:4916`). The design record is explicit that this is not an oversight:
  `Docs/surveys/realism_gap_2026-07-28/ZZ_synthesis.md:370-372` — *"비가시 낙차는 정의상 어떤
  렌더 pass에도 나타나지 않는다. depth·semantic·normal 전부 무력"*, and the top-down orthographic
  height-map plan was **scrapped** there in favour of raycast + back-projection.
  **Give:** depth is an auxiliary channel at best. GT must come from geometry.

* **The GT drop map is still 0 built, and the planned PhysX route is not wired.**
  `lighting_camera_variation_spec_v1.md:743` plans "GT 낙차 맵 (T3-20, PhysX 레이캐스트 2.5D +
  픽셀 역투영)"; `:860` records the count as **0**, so "타깃이 프레임에 있는가" cannot be
  positively judged and the current design only does negative rejection. Code:
  `UsdPhysics.CollisionAPI.Apply` appears 7× in `scene_common.py` (`:1258, :1476, :1525, :1567,
  :2294`, …) but there is **no `UsdPhysics.Scene` / PhysicsScene anywhere** — grepped
  `UsdPhysics.Scene`, `PhysicsScene`, `omni.physx`. PhysX scene queries would need a physics
  scene created first.
  **Give:** use `AabbPrefilter.ground_z` (already constructed per render process at
  `run_data_render.py:363`) as the 2.5-D height field instead — with the caveat below.

* **The available height field is AABB-based, and that is badly wrong on four scenes.**
  `variation_kit.py:781` samples world **axis-aligned bounding boxes**, not surfaces. Exact for
  box-per-step stairs; catastrophic for annular-sector meshes — measured in
  `Docs/reports/w3_s08_v1.md:219-221`: the AABB of a 36…52° arc at r ≈ 15 is a ~20 × 12 m box.
  Affected: **scene05, scene06, scene08, scene19** (`scene_common.py:2250 _annular_sector_mesh`,
  `:2789 build_arc_steps`). Exact analytic oracles exist for only 6 scenes
  (`scene06:1036`, `scene08:1068`, `scene11:988`, `scene12:998`, `scene19:937`,
  `scene07:782 path_z`) — s05 is not among them.
  **Give:** hand-treat or exclude s05; prefer `_solid_at` where present.

* **No machine-readable per-scene hazard registry exists.** `PARAMS` is per-scene and
  free-form (`scene01:221 stairs=dict(...)` vs `sceneD4:104-108 hall=dict(...)` vs
  `scene08:210 sector=dict(...)`). The only cross-scene drop table is prose:
  `Docs/reports/dropoff_cue_matrix_v1.md:96-127`, 28 of 33 scenes, and it is a single agent's
  read, not a re-derivation.
  **Give:** either transcribe that table into a checked-in registry tonight, or derive depths
  from the height field and cross-check against it.

* **The 0.3 m minimum-hazard-depth threshold is documentation, not code.**
  `Docs/briefs/NegObs_인공씬1호_계단_구현지시서.md:84` "연구 최소 위험 깊이 0.3 m 이상일 것
  [고정]"; applied as prose judgement at `Docs/reports/w3_s11_v1.md:205`. The only thresholds
  in code are `ground_kit.py:124 GT_DELTA = 0.020` and the 0.10 m minor-step
  (`infra_kit.py:564,1404,1504`).
  **Give:** declare 0.30 explicitly in tonight's GT code; do not assume a helper enforces it.
  It matters — sub-threshold steps do exist inside drop scenes (s16 carries a 0.15 m road curb).

* **The train/val/test split is scene-level, fixed, and puts every hard negative in `train`.**
  `variation_kit.py:827-856`, deterministic 23/5/5:
  `val = {scene01, scene02, scene19, sceneC2, sceneD1}`,
  `test = {scene05, scene06, scene10, scene12, scene18}` — **all ten are drop scenes**;
  N1–N5 (GT drop 0, `shortcut_audit.py:45`) are all in `train`. There is no CLI override; the
  base is hard-wired to 0 everywhere.
  **Give:** a scene-level drop/no-drop metric on val/test is degenerate. Either evaluate
  cell-level only, or make the hazard-off arm supply the negatives for val/test.

* **Acceptance gate check 1 forces a condition choice the pilot did not make.**
  `check_data_run.py:134-153` needs a sun-bearing pair ≥ 0.3 net EV apart; the only qualifying
  pairs in the catalogue are `L5` with `L0`/`L1`/`L2` (net EV `L0 0.000 · L1 0.013 · L2 0.047 ·
  L3 0.090 · L4 0.195 · L5 0.352`). The 260815 pilot's `L0,L2,L7` cannot satisfy it.
  **Give:** render `L0,L5,L7` (the validated `run_260730_data_mini.sh` set) and declare the
  5 refused pairs' substitutions.

* **The data channel has no per-scene spp raise, and the raise would not work if it had one.**
  `scripts/rounds/run_p2_all33.sh:11-13` raises dark scenes to `NEGOBS_PT_TOTAL_SPP=256` (`sceneD4` required,
  `scene02`/`scene13` recommended). `run_data_render.py:382-384` hard-codes
  `sc.PT_FAST` (`scene_common.py:183` `spp=16, total_spp=64, subframes=8, warmup=8`) and never
  reads that env var — and per `Docs/reports/dn_curve_260816.md` §3 the knob does not reach the
  captured pixels anyway (noise sd 0.0230/0.0230/0.0228 at spp 64/128/256, time 5.0/9.1/14.9
  s/cut).
  **Give:** accept a uniform-noise, uniform-spp corpus; expect `sceneD4`, `scene02`, `scene13`
  to be the cuts most likely to trip the dark/blown gate.

* **`cam.d` is not range-to-hazard.** `run_data_render.py:429-431` places the eye at
  `x = -d` and points it along +X with sampled yaw/pitch/roll — there is **no look-at target**,
  not on `x = 0`, not on the origin. `d` is the along-travel-axis standoff from the drop-start
  edge. Any spec text that reads `d` as a distance to a visible target is wrong.

* **Camera height band: spec A7 0.3–2.0 m, code U(0.25, 1.90) with a 1.20 m cap on 4 scenes.**
  `variation_kit.py:574-626` — CAM-2 scenes (scene02, scene15, sceneD4, scene11) cap h ≤ 1.20.
  Code is truth for tonight's data; the spec band's upper 1.90–2.0 m and the sub-0.30 m sliver
  0.25–0.30 m are the only deltas. Recorded per user directive (08-20 00:00), no code change.
