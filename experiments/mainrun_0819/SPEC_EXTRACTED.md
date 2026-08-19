# SPEC_EXTRACTED.md — "code is truth" extraction for the 08-19 main run

Repo `/home/vislab/Desktop/work_sy/Practice_NegObs`, branch `feat/realism-v1`, HEAD `8c814db`.
Read-only recon. Every verdict below is either **[FOUND `file:line`]** with the literal
constant, or **[NOT FOUND]** with the searches that were actually run.

Baseline conventions that everything else hangs off:

* `scene_common.py:13` — *"Coordinate convention (all scenes): Z-up, metres, travel axis +X,
  drop start edge x=0."*
* `scene_common.py:4870` `grid_views(gy, heights=(0.3,0.9,1.8), dists=(2,5,10), pitch=-10)`
  — the **judge** preset grid. Eye `[-d, gy, h]` (ABSOLUTE z), target `eye + 5·(cos p, 0, sin p)`.
  Data channel does **not** use this (see (c)).
* `variation_kit.py:42` `RES_W, RES_H = 1920, 1080`; `:43` `APERTURE = 20.955`.

---

## (a) Polar hazard grid — azimuth sectors, distance bands, cell-positive rule

### **[NOT FOUND]** — no polar hazard grid exists anywhere in this repository.

Searched (whole tree minus `.git`, `*.py *.md *.json *.sh`):
`polar`, `sector`, `band`, `grid`, `\b15\b`-cell forms, `5x3`, `5×3`, `방위 섹터`,
`방위각 구간`, `극좌표`, `거리 밴드`, `밴드 경계`, `15셀`, `셀 양성`, `hazard grid`,
`occupancy` (as a label term), `label map`. Also read the ledgers
`Docs/audit_v4/gt_changes_w3.md`, `Docs/audit_v4/fixlog_W7.md`,
`Docs/reports/autonomy_run_260814_18_handover_v1.md`,
`Docs/reports/autonomy_run_extension_260816.md`,
`Docs/reports/dropoff_cue_matrix_v1.md`, `Docs/briefs/lighting_camera_variation_spec_v1.md`.

What the hits actually are, so they are not mistaken for the grid:

| Hit | What it really is |
|---|---|
| `scene_common.py:2250` `_annular_sector_mesh(...)`, `:2789` arc-step sectors | **scene geometry** — annular-sector prisms for curved stairs (s05/s06/s08/s19). Not a label grid. |
| `scenes/main/scene08_sunken_plaza.py:210` `sector=dict(cascade=(150.,210.), tier=(90.,150.), arcade=(210.,290.), wall=(290.,70.))` | scene08's own architectural plan angles. |
| `Docs/briefs/lighting_camera_variation_spec_v1.md:281` "프레임을 **5×3** 으로 나눈 15개 대표 방향 레이 중 6개 이상" | the **camera openness prefilter**, implemented at `variation_kit.py:806-807` as `for fx in (-0.8,-0.4,0.0,0.4,0.8): for fy in (-0.6,0.0,0.6)`, thresholds `variation_kit.py:663` `OPEN_RAYS, OPEN_MIN_HITS, OPEN_MIN_DIST = 15, 6, 1.0`. **A camera-rejection ray fan, not a hazard grid.** This is the single most likely false positive for "5 sectors × 3 bands = 15 cells". |
| `Docs/reports/dropoff_cue_matrix_v1.md` `h{0.3,0.9,1.8} × d{2,5,10}` | the 9 judge presets, again `grid_views`. |

Consequences: **azimuth range / sector boundaries / distance-band boundaries / cell-positive
coverage rule / azimuth origin+direction / pitch sign for a polar grid are all undefined in
code.** They must be *declared* by tonight's run, not extracted. The only sign conventions the
code does fix:

* pitch: `variation_kit.py:629` `dir_of(yaw,pitch) = (cos p cos y, cos p sin y, sin p)` →
  **negative pitch = looking down** (+Z up). `CAM_DIST["pitch"]` is centred on −10.
* yaw: same line — yaw rotates about +Z, **0 = along +X = along the travel axis**, positive =
  toward +Y (CCW seen from above). Docstring `variation_kit.py:630`: *"Scenes look along +X;
  yaw rotates about +Z."*
* So if a polar grid is defined tonight, "azimuth 0 = camera forward = +X, CCW positive,
  measured in the ground plane" is the only convention consistent with existing code.

---

## (b) V / E / H tier machinery, semantic IDs, `tau_int` / `tau_edge`, per-frame raw visibility

### **[NOT FOUND]** — none of it exists in code.

Searched: `tau_int`, `tau_edge`, `rim_band`, `rim`, `interior_visible`, `edge_arc`,
`visibility tier`, `V/E/H`, `semantic`, `Semantics`, `instance_id`.

* The **only** occurrence of `V/E/H` in the whole tree is
  `experiments/mainrun_0819/realworld/PROTOCOL_SHOOT.md:22,46` — a *sibling agent's* real-shoot
  protocol written tonight, i.e. the spec side, not the repo side. Its own definition
  (`PROTOCOL_SHOOT.md:26-30`): V = hazard interior visible, E = only the rim/edge line visible,
  H = hazard contributes no pixels; tier decided in the order V→E→H.
* `rim` in code (`scene_common.py:1341,1496`) is a slab/manhole geometry word, unrelated.
* No interior-surface or rim-band semantic ID exists — see (f): the repo authors **zero**
  USD semantics.

### The commit-`9f5e584` cue-coverage matrix is NOT machinery — it is an LLM read.

* Product: `Docs/reports/dropoff_cue_matrix_v1.md` (429 lines, 28 drop scenes × 13 cues).
  Commit `9f5e584` touched **that file only** (`git show --stat 9f5e584`) — no script was added.
* Raw material: `Docs/reports/raw_260816/cue_matrix_result.json` (270 KB) and
  `cue_matrix_journal.jsonl` (207 KB). The journal is a multi-agent task log
  (`{"type":"started","agentId":...}`); the result is `["result"]["scenes"]`, per-scene
  free-text fields such as `drop_type`, `drop_summary`, plus per-cue `present` / `strength`
  (`S`/`M`/`w`/`·`) and `occluded_or_weak_at: [preset names]`.
* The report itself states the limitation (`dropoff_cue_matrix_v1.md:5-8`):
  *"이것은 측정이 아니다 … 한 회차 렌더 산출물을 한 감사자가 판독한 결과"* — one round
  (`260816_w4_final33_on`), one human/agent reader, grades are that reader's.
* Granularity is **scene × cue × judge-preset**, 9 presets only. There is no per-frame, no
  per-cut, and no pixel-count field. **It cannot be reused per-frame**; at most it is a prior
  for which scenes are cue-poor.
* Useful derived numbers it does carry: occlusion tallies 574 preset-events;
  `h0.3_d10` alone = 165 (28.7 %); 8 scenes (s04·s05·s07·s14·s17·C1·D2·D4) have **0 surviving
  cues** at `h0.3_d10`; `railing_or_guard` is the *least* occluded cue at 9.9 % — i.e. the
  corpus rewards the guard-rail shortcut (`dropoff_cue_matrix_v1.md:14-19`).

### What *does* exist that is per-cut and visibility-adjacent

`variation_kit.py:728` `class AabbPrefilter` — built once per scene process
(`run_data_render.py:363`), and its per-cut output is already written into every
`variation.json` under key `stage1`:

* `:781` `ground_z(x, y, top=60.0)` — downward ray from z=60, returns first AABB hit height.
* `:787` `check(eye, yaw, pitch, hfov)` → `nearest_solid`, `buried`, `ground_below`,
  `offground`, `open_rays` (0..15), `closed_in`, `flag`.

This is the only per-frame geometric-visibility instrument in the repo. It answers "is the
camera legal", **not** "is the hazard visible".

---

## (c) Camera sampling for the data channel

### **[FOUND]** `variation_kit.py:574-626` (sampler) + `scripts/run_data_render.py:420-437` (placement)

```
variation_kit.py:574  CAM_DIST = dict(
    h=(0.25, 1.90),                   # Uniform, metres ABOVE GROUND
    pitch=(-10.0, 4.0, -20.0, -2.0),  # N(mu, sd) truncated [lo, hi]
    roll=(0.0, 1.5, -5.0, 5.0),
    hfov=(62.2, 1.5, 58.0, 66.0),     # centre = measured IMX219
    yoff=(0.0, 0.35, -0.90, 0.90),
    yaw=(0.0, 8.0, -20.0, 20.0),
    d=(1.2, 12.0),                    # LogUniform, metres
)
variation_kit.py:606  def sample_camera(scene, idx, base_seed, gy=0.0)
    :615  d = exp(U(log 1.2, log 12.0))        # log-uniform in distance
    :617  h_rel = U(h_lo, h_hi)
    :618  y     = truncnorm(gy, yoff_sd, gy±0.90)
    :620-623  yaw / pitch / roll / hfov = truncated normals per CAM_DIST
```

**Tiers** — `variation_kit.py:583-595`:

| Tier | Scenes | Effect |
|---|---|---|
| `CAM-1` | everything else (22 scenes) | full band |
| `CAM-2` | `scene02, scene15, sceneD4, scene11` (`:592`) | `CAM2_H_MAX = 1.20` height ceiling, `CAM2_YOFF_SD = 0.15` lateral sigma (`:595`) |
| `CAM-3` | `scene03, scene07, scene09, scene10, scene12, scene17, scene19` (`:593-594`) | documentation-only no-op — heights are ground-relative for *every* scene, so CAM-3 records "which scenes would have broken" (`:585-591`) |

Tier string is written per cut at `run_data_render.py:455` `tier=s["tier"]`.

**How cameras are aimed** — `run_data_render.py:429-437`:

```
gz  = pre.ground_z(-s["d"], s["y"])                 # ground under the sample
eye = (-s["d"], s["y"], gz + s["h_rel"])            # eye x = -d  ==>  d = standoff from x=0
rows = vk.look_at_rows(eye, s["yaw"], s["pitch"], s["roll"])
```

* **The camera is NOT aimed at anything.** There is no target, no look-at on the drop edge and
  no look-at on the origin. It stands at `x = -d` and points along **+X rotated by the sampled
  yaw/pitch/roll**. `look_at_rows` (`variation_kit.py:635`) builds one `xformOp:transform`
  matrix (SP-7: roll error ≤ 0.005°, hFOV error ≤ 0.047°).
* **`cam.d` means: metres of standoff behind the drop-start edge `x = 0`, measured along the
  travel axis.** It is *not* range-to-hazard and *not* range-to-anything-visible. Confirmed on
  disk: `dataset/260815_datapilot/train/scene04/variation.json` cut 0 has
  `"d": 4.4596` and `"eye": [-4.4596, -0.0534, 0.8916]`.
* Lateral centre `gy` is learned per scene by monkey-patching `grid_views`
  (`run_data_render.py:328-330`) — it differs per scene (docstring `:293`: scene01 −2.75,
  scene04 0.0).
* `focalLength = APERTURE / (2·tan(hfov/2))` (`variation_kit.py:598-603`), written per cut.

**Rejection rules**

* Stage 1, analytic, `variation_kit.py:661-663`: `BURY_CLEAR = 0.15`, `GND_LO, GND_HI = 0.05, 3.0`,
  `OPEN_RAYS, OPEN_MIN_HITS, OPEN_MIN_DIST = 15, 6, 1.0`. **Advisory only** — the policy note at
  `:673-680` records 1 firing in 600 samples and it was a false positive; the sample is *not*
  dropped.
* Stage 2, image, `variation_kit.py:665-667` + `:700`: `DARK_MEAN 30.0`, `DARK_PCT 70.0`,
  `DARK_LEVEL 25`, `BLOWN_MEAN 235.0`, `CLIP_PCT 1.0`, `CLIP_LEVEL 254`, `FLAT_STD_MIN 1.0`.
* `flat_near` is explicitly **OFF on the data channel** (`run_data_render.py:445`
  `vk.image_filter(fp, flat_near=False)`; rationale `variation_kit.py:682-689`).
* Nothing is re-sampled: a rejected cut is still written and still recorded; only its
  `img.reject` flag is set. Measured `R_REJECT_MEASURED = 0.020` (`variation_kit.py:693`);
  the 260815 pilot measured `r_reject = 0.0` on all 5 scenes.

**Does the sampled distribution cover the spec band (h 0.3–2.0 m, pitch −15…+5°)?**

| Axis | Code | Spec band | Verdict |
|---|---|---|---|
| height | `U(0.25, 1.90)`, and `≤1.20` on the 4 CAM-2 scenes | 0.3–2.0 | **partial** — top 1.90–2.00 never sampled; 0.25–0.30 sampled but outside spec; 4 scenes never exceed 1.20 |
| pitch | `N(−10, 4)` truncated **[−20, −2]** | −15…+5 | **no** — the code **never** produces pitch > −2°, and produces down to −20°. The whole +5…−2 half of the spec band is empty; −20…−15 is outside the spec band and *is* sampled |
| distance | LogU(1.2, 12.0) | (unstated) | — |
| roll / hFOV | ±5°, 58–66° | (unstated) | — |

Enforced again as an acceptance gate: `scripts/check_data_run.py:238-244` re-asserts
`h_rel ∈ [0.25,1.90]`, `pitch ∈ [−20,−2]`, `roll ∈ [−5,5]`, `hfov ∈ [58,66]`, `d ∈ [1.2,12]`.

---

## (d) Hazard on/off toggle

### **[FOUND]** — mechanism exists per scene, but the `_on` in `260816_w4_final33_on` is NOT it.

**`_on` means the look layer, not the hazard.**
`scripts/rounds/run_260816_w4_final33.sh:5` calls `bash run_p2_all33.sh 260816_w4_final33 on`,
and `run_p2_all33.sh:29-30`:

```
LOOK="${2:-on}";  LOOKV=$([ "$LOOK" = "on" ] && echo 1 || echo 0)
```
`:39` `NEGOBS_LOOK_V1="${LOOKV}"`, `:41` `NEGOBS_CAPTURE_DIR="look_check/${key}/${TAG}_${LOOK}"`.
So `_on` = realism look-layer v1 enabled. **`_off` would be the no-look-layer control, not a
hazard-off arm.** No hazard-off render exists anywhere on disk.

**The real toggle** is `SCENE_CONFIG`, a per-scene dict of 7 keys, overridable at runtime by
`NEGOBS_SCENE_CONFIG` (JSON, deep-merged):

```
scenes/main/scene01_campus_stairs.py:203  SCENE_CONFIG = {
    "hazard_stairs": True,   # False -> whole stair + lower plaza becomes flat z=0 (only geometry toggle)
    "cue_railing": True, "cue_tactile": False, "cue_material_break": True,
    "cue_sign": True, "cue_scene_dressing": True }
scenes/main/scene01_campus_stairs.py:864-869
    NEGOBS_SCENE_CONFIG='{"cue_railing":false}' python scene01_campus_stairs.py
    _sc_ov = os.environ.get("NEGOBS_SCENE_CONFIG", ""); _deep_update(SCENE_CONFIG, json.loads(_sc_ov))
```

The env override is present in **all 33 scene files** (verified by grep count per file).
Doctrine: `README.md:86` *"SCENE_CONFIG 7키(단서 토글 — **위험 기하는 불변**)"* — only the
`hazard_*` key changes geometry; the `cue_*` keys must leave the drop geometry bit-identical.

**Per-scene hazard key name — it is NOT uniform** (this will break a naive `--arm off` loop):

| Key | Scenes |
|---|---|
| `"hazard_stairs"` | 30 scenes: scene01–scene21 (all 21) + sceneC1, C2, C4, D1, D2, D3, D4, **N3, N4** |
| `"hazard_shadow_band"` | `sceneN1` (`sceneN1_shadow_band.py:52` — False → remove the elevated slab) |
| `"hazard_asphalt_patch"` | `sceneN2` (`sceneN2_asphalt_patch.py:85` — False → remove patch + cut lines) |
| `"hazard_flush_grating"` | `sceneN5` (`sceneN5_flush_grating.py:53` — False → remove grating + manholes) |

Selected wiring evidence (the branch is real, not decorative):
`scene11:170 / :2788 if cfg["hazard_stairs"]`, `scene21:90 / :1467`,
`scene09:302 / :3873-3881` (*"stairs and banks unified into z=0 flat ground (water kept)"*),
`scene19:216 / :2056`, `sceneD4:87` (*"False -> track trough filled (all z=0 flat, drop 0)"*),
`sceneD1:48`, `sceneN3:79-80` (*"painting removed, a pure flat mall (control)"*),
`sceneN4:86-87` (*"remove the slope, z=0 flat throughout"*).

**Caveats before using it tonight**

1. `hazard_*=False` on the 5 hard negatives (N1/N2/N3/N4/N5) does **not** create a "no-drop"
   arm — those scenes already have GT drop 0 (`scripts/shortcut_audit.py:45`
   `NO_DROP = {"sceneN1".."sceneN5"}`, README §배치1). It removes the *illusion feature*.
2. **No hazard-off arm has ever been rendered or verified.** The design doc lists it as
   approved-but-not-done: `Docs/briefs/lighting_camera_variation_spec_v1.md:742`
   *"**hazard-off 쌍둥이 렌더** (STATUS 승인 완료) — P(낙차 | 난간) = 0.944 를 0.6~0.8 로"*.
   There is no toggle-integrity regression run in `scripts/`. Expect first-run breakage on
   some scenes (each `hazard_*=False` branch is code that has not been exercised in months).
3. `run_data_render.py:173-189` does `env = dict(os.environ)` then `env.update(...)`, so
   `NEGOBS_SCENE_CONFIG` set in the parent shell **does** propagate into every scene subprocess.
   It is not in `variation_kit.VARIATION_ENV` (`:57-64`), so it does not trip the role gate.
4. Output path is `dataset/<run>/<split>/<scene>/<cond>__s<seed>__<idx>.png`
   (`run_data_render.py:171,430`) — identical for both arms. **The off arm must use a
   different `--run` stamp** or it silently overwrites the on arm.

---

## (e) Depth export

### **[NOT FOUND]** — zero depth / distance / AOV / Replicator code in the repo.

Searched `depth`, `distance_to_camera`, `distance_to_image_plane`, `annotator`, `AOV`,
`Replicator`, `omni.replicator`, `rep.` across all `*.py`. Total hits outside `look_check/`:
three, all comments (`sceneC4_wet_stairs.py:562` mentions Replicator segmentation
hypothetically; `assets/download_*.py` `grep` prose; `scripts/s03_xalign_probe.py:954` a local
variable named `rep`). Every capture in this repo is
`omni.kit.viewport.utility.capture_viewport_to_file` → 8-bit RGB PNG.

The design record already predicted this and says the important thing:
`Docs/surveys/realism_gap_2026-07-28/ZZ_synthesis.md:370-375` — *"GT 낙차 맵은 렌더러로 만들 수
없다 … 비가시 낙차는 정의상 어떤 렌더 pass에도 나타나지 않는다. depth·semantic·normal 전부
무력"*, and §10.3 quotes an NVIDIA benchmark: *"annotator를 전부 켜면 처리량 40배 붕괴"*, with
the recommendation "RGB + depth + semantic + camera_params only".

### Minimal viable opt-in depth capture (assessment only — no code written)

* **Where the PNG is written**: `scripts/run_data_render.py:388-406`, the nested function
  `cap(fp)` inside `_capture()` (defined `:351`). It calls `capture_viewport_to_file(vp,
  file_path=fp)` then polls for size stability (150 updates).
* **What is already imported there**: `run_data_render.py:352-358` — `carb`,
  `pxr.Gf/Sdf/UsdGeom`, `omni.kit.viewport.utility.{get_active_viewport,
  capture_viewport_to_file}`. The camera prim is `/World/DataCam`, defined `:367-377`, and is
  the active viewport camera (`:376-377`).
* **Availability**: `omni.replicator.core-1.11.35+106.5.0.lx64.r.cp310` is present in
  `~/miniconda3/envs/env_isaaclab/lib/python3.10/site-packages/isaacsim/extscache/`.
  Isaac Sim 4.5.0 / Kit 106.5. It may need
  `omni.kit.app.get_app().get_extension_manager().set_extension_enabled_immediate("omni.replicator.core", True)`
  after `sc.boot()` (`scene_common.py:1145`) since the scenes boot a bare
  `SimulationApp({"headless":..,"width":1920,"height":1080})` (`:1157`).
* **Insertion point, opt-in, default behaviour unchanged**:
  1. After `:377` (camera made active) and before `set_render_mode_fn("PathTracing")` at `:380`,
     gate on a **new** env var (e.g. `NEGOBS_DATA_DEPTH=1`, read once): create
     `rp = rep.create.render_product("/World/DataCam", (vk.RES_W, vk.RES_H))` and
     `ann = rep.AnnotatorRegistry.get_annotator("distance_to_image_plane"); ann.attach(rp)`.
     (`distance_to_image_plane` = orthogonal Z depth, the U-Net-friendly one;
     `distance_to_camera` = radial range.)
  2. Inside the per-cut loop, immediately after `ok = cap(fp)` (`:441`), fetch
     `ann.get_data()` (float32 H×W, +inf for sky) and write it beside the PNG as
     `<same stem>.depth.npy` (lossless) or a 16-bit PNG in mm (clipped, lossy at range).
     Record the extra file in the cut dict at `:448-471` so `check_data_run.py:256-261`
     ("no orphan PNG outside the manifest") does not fail — that check only globs `*.png`,
     so `.npy` is safe; a 16-bit **PNG** sidecar would trip it.
  3. Everything stays byte-identical when the env var is unset: no render product, no
     annotator, no extra `sim_app.update()`.
* **Risks to validate on ONE cut before committing a round**: (i) a Replicator render product on
  the same camera can force a second render pass and re-set `/rtx/pathtracing/*` — the settings
  block at `:381-384` would then need re-asserting after the render product is created;
  (ii) annotator freshness under PathTracing accumulation — the safe pattern is
  `rep.orchestrator.step(rt_subframes=sc.PT_FAST["subframes"])` instead of relying on the
  viewport capture's own updates; (iii) throughput — measure s/cut on one scene, budget for the
  ZZ §10.3 warning.
* **Do not expect depth to give the label.** Depth is a *visible-surface* signal; the negative
  obstacle is by construction the thing that is not visible. Depth is useful as an auxiliary
  head / sanity channel, not as GT.

---

## (f) Semantic ID / instance segmentation export

### **[NOT FOUND]** — no semantics are authored and no segmentation is exported.

Searched `Semantics`, `add_update_semantics`, `semantic_segmentation`, `instance_id`,
`instance_segmentation`, `class_id`. Result: **zero** `Semantics` API calls in the tree. The
only prose hit is `scenes/batch1/sceneC4_wet_stairs.py:562-564`, which *reasons about* what
Replicator segmentation would do — it does not call it.

Assessment for an opt-in add:

* The Replicator plumbing is identical to (e): same render product, annotator
  `"semantic_segmentation"` (or `"instance_id_segmentation"`).
* **The blocker is upstream of the annotator**: the annotator returns per-pixel *labels*, and
  there are no labels. Every scene would need `Semantics` applied to its prims. Cost is a
  per-scene authoring pass across 33 files — not a tonight job.
* Cheapest automatic proxy if a coarse mask is wanted later: label by **prim-path token**, the
  pattern the repo already uses at `variation_kit.py:668` (`VEG_TOK = ("veg","tree","canopy",
  "leaf","shrub","hedge","grass","planter","flower","bush")`) and that the material classifier
  vocabulary uses. A one-pass `stage.Traverse()` mapping path tokens → class, applied right
  after scene assembly (i.e. inside the same `_capture` monkey-patch, before the render
  product), would yield a usable-but-noisy class map without touching any scene file.
* Instance segmentation would separate stair treads only if each tread is its own prim — true
  for box-per-step scenes, false where a flight is one `_annular_sector_mesh`
  (`scene_common.py:2250`).

---

## (g) The 0.3 m minimum-hazard-depth threshold

### **[NOT FOUND in code]** — it is a documented research constant, never a code constant.

Searched `0.3`, `0.28`, `0.32`, `depth threshold`, `min_drop`, `drop_min`, `hazard_min`,
`최소 위험 깊이`, `minimum hazard depth` across `*.py` and `*.md`.

* Doc origin: `Docs/briefs/NegObs_인공씬1호_계단_구현지시서.md:84` —
  *"총 낙차 … 파생값. **연구 최소 위험 깊이 0.3 m 이상일 것 [고정]**"*.
* Applied as a judgement, in prose: `Docs/reports/w3_s11_v1.md:205` — a 0.168 m element is
  *"이 저장소의 0.30 m 부(負)장애물 임계 미만 → 단차(step)이지 낙차(drop)가 아니다"*.
* Restated tonight in the shoot protocol (`experiments/mainrun_0819/realworld/PROTOCOL_SHOOT.md:5`):
  *"위험 정의: 깊이 0.3 m 이상 하강 … 연석 0.10–0.25 m 는 위험 아님"*.
* The thresholds that **are** in code are different numbers and different jobs:
  `ground_kit.py:124` `GT_DELTA = 0.020` (max |dz| any dressing element may add, *"1/5 of the
  0.10 minor step"*), `ground_kit.py:125` `EDGE_STANDOFF = 0.80`, and the **0.10 m minor-step
  threshold** quoted at `infra_kit.py:564,1404,1504`. Nothing in code tests `>= 0.30`.

Practical reading: every one of the 28 drop scenes is far above 0.30 m (smallest is
scene05 at 0.398 m rim; see (h)), so the threshold does not currently exclude any scene — but
a cell-level polar GT will need it as an explicit declared constant, because sub-0.30 steps
(curbs at 0.15 m, s16's road curb) do exist inside scenes.

---

## (h) Per-scene hazard geometry ground truth

### **[NOT FOUND]** as a machine-readable registry. **[FOUND]** as three partial substitutes.

Searched `scenes/*/*.py` for a common schema: `drop`, `hazard extents`, `depth`, `GT`,
`registry`, plus `SCENE_CONFIG` / `PARAMS` structure across all 33 files.

**What does not exist**: there is no `HAZARD = dict(...)`, no per-scene extents table, no
shared key schema. `PARAMS` is per-scene and free-form — `scene01:221`
`stairs=dict(x0=0.0, riser=0.15, tread=0.38, nsteps=4, y0=-5.5, y1=5.5, base_z=-0.7)` versus
`sceneD4:104-108` `hall=dict(x0=-16.0, x1=46.0, plat_out=8.0, edge=2.0, z_walk=0.0,
z_base=-1.60)` versus `scene08:210` `sector=dict(...)`. Reading them programmatically means 33
bespoke readers.

**Substitute 1 — the convention.** `scene_common.py:13`: drop start edge is at **x = 0** in
every scene, travel along +X. That plus the sampled `d` gives, for free, the along-axis
standoff of every camera from the drop line (`run_data_render.py:430`).

**Substitute 2 — a human-readable drop table for 28 of 33 scenes.**
`Docs/reports/dropoff_cue_matrix_v1.md:96-127`, "씬 키 (낙차 유형·낙차량)". Verbatim depths:

```
s01 0.60 (4×0.15, width 11 m)   s02 3.38   s03 3.2 (20×0.16)   s04 1.45 (9 steps)
s05 0.398 rim → tiers → stage −1.2/−1.6    s06 5.005   s07 4.2 + 1.8 (unguarded S wall)
s08 −4.500 bowl floor           s09 ~5.5 (36 steps, lower 6 submerged)
s10 6.60 + unguarded 30° slope −2.3         s11 5.505 (E mid-landing 2.755)
s12 1.80 concealed cantilever + 1.36        s13 3.96 trench   s14 6.0 (40 steps)
s15 4.25   s16 3.0 + 0.15 curb   s17 3.2    s18 2.560   s19 1.8 (lower terrace −1.95)
s20 2.1    s21 2.7   C1 2.04   C2 2.24   C4 2.10   D1 1.2   D2 3.0 (opening 1.5×2.0)
D3 0.8 (drainage: top 1.0 / bottom 0.5 / depth 0.8, PARALLEL to travel axis)
D4 1.15 (platform → track, indoor, unguarded)
```
The 5 hard negatives are absent from that table by construction; their GT is drop 0
(`scripts/shortcut_audit.py:45`). **Caveat**: these numbers are an agent's read of scene code +
one render round, not a re-derivation; the report says so itself (`:5-8`).

**Substitute 3 — runtime geometry oracles.**

* Universal, already running inside the render process:
  `variation_kit.py:781 AabbPrefilter.ground_z(x, y, top=60.0)` — a downward ray from z = 60
  over **world AABBs of every Gprim** (built `:735-764`, prims wider than 400 m skipped as sky
  domes). This *is* a 2.5-D height-field sampler and it is the cheapest existing path to the
  T3-20 "PhysX raycast 2.5D + pixel back-projection" plan.
  **Accuracy caveat, decisive for scene choice**: it returns the top of an *axis-aligned
  bounding box*, not the surface. Exact for box-per-step stairs; badly wrong for annular-sector
  meshes — `Docs/reports/w3_s08_v1.md:219-221` measured that the AABB of a 36…52° arc at
  r ≈ 15 is a ~20 × 12 m box. Affected scenes: **s05, s06, s08, s19** (and any scene using
  `scene_common.py:2250 _annular_sector_mesh` / `:2789 build_arc_steps`).
* Exact, but only for 6 scenes: `_solid_at(x, y, z)` in
  `scene06:1036`, `scene08:1068`, `scene11:988`, `scene12:998`, `scene19:937`, plus
  `scene07:782 path_z(x)` and `sceneC2:895 surface_z(x,y)`. The variation spec already
  anticipated exactly this split (`lighting_camera_variation_spec_v1.md:724-725,742`:
  *"`_solid_at` 이 있는 5개 씬은 등록만 해 두면 …그 함수로 대체(더 정확)"*).
* **PhysX is not available as-is.** `UsdPhysics.CollisionAPI.Apply` appears 7× in
  `scene_common.py` (e.g. `:1258, :1476, :1525, :1567, :2294`) and in scene01/06/17, but there
  is **no `UsdPhysics.Scene` / PhysicsScene anywhere** (grepped `UsdPhysics.Scene`,
  `PhysicsScene`, `omni.physx`). So the T3-20 "PhysX raycast" plan needs a physics scene to be
  created first; the AABB ray in `AabbPrefilter` needs nothing.

### Recommended way to fill a polar cell for a given camera pose

Analytic + AABB height-field, **not** PhysX, **not** a render pass:

1. Camera ground frame: eye `(-d, y0, gz+h)`, forward azimuth = sampled `yaw` about +Z
   (`variation_kit.py:629`). Define the polar grid in that frame.
2. For each cell, take its centre (or a small set of sample points) in world XY and evaluate
   `pre.ground_z(x, y)` (already constructed at `run_data_render.py:363` — zero extra cost per
   cut beyond the rays).
3. Cell is hazard-positive when the height field inside the cell drops by more than the
   declared threshold relative to the camera's own standing ground `gz` (or relative to the
   cell's near edge, whichever rule is declared). Use the 0.30 m constant from (g) —
   **it must be declared tonight, it is not in code.**
4. Cross-check against the two anchors that *are* solid: (i) the drop line is `x = 0`
   (`scene_common.py:13`), so any cell whose footprint crosses `x = 0` with a descending step
   is positive; (ii) per-scene depth from the table above.
5. Exclude or hand-treat **s05, s06, s08, s19** (annular-sector AABB inflation), and prefer
   their `_solid_at` where it exists (s06, s08, s19 have one; s05 does not).
6. Visibility (V/E/H) is a **separate** question from cell occupancy and has no producer at all
   (see (b)); occlusion between eye and cell would need the same AABB ray
   (`AabbPrefilter._ray_t`, `variation_kit.py:766`) fired eye→cell.
