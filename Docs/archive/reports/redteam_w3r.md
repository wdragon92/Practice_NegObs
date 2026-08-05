# Red-team verification — W3-R survey wave (R1 asset map · R2 prop map · R3 building A/B)

> **Wave**: W3-R · **Task**: RT (verify) · **Date**: 2026-07-30 · **Branch**: `feat/realism-v1`
> **Targets**: `Docs/surveys/w3r_asset_map_v1.md` (R1) · `Docs/surveys/w3r_prop_mapping_v1.md` (R2) ·
> `Docs/surveys/w3r_building_ab_v1.md` (R3)
> **Method**: independent re-execution, not proofreading — live S3 HEAD/paged-list requests, licence
> pages re-fetched, USD re-measured with usd-core 0.26.8, counts recomputed from `GROUND_PROFILES ×
> SCENE_PLANS` / scene `PARAMS` via AST-exec, A/B artifacts re-read (metrics JSON, times.tsv, PNG
> mtimes, archived drivers re-run), brick texture re-measured three ways.
> **Files written**: this file only. No tracked scene file or shared module touched. No commits.
> Evidence tags: `[measured]` re-executed this session · `[law]` licence/statute text fetched or
> quoted this session · `[stat]` derived over a measured population · `[assumed]` stated inference.

---

## 0. Verdict summary

| Report | Verdict | One line |
|---|---|---|
| **R1** `w3r_asset_map_v1.md` | **PARTIAL (core confirmed, 4 errata)** | Licence tier map and catalog census reproduce **exactly** (every byte, count and tri figure I re-measured matched). Refuted: §6.5's `+7.904` Z placement row (would hang the building 7.9 m in the air — R3's correction is geometrically right). Season-rule gap: `veg_shrub_hedge_yellow_01` and `veg_tree_cherry_japanese_01` are shortlisted with no pixel verification. Count nits: 12 pole folders (not 13), 9 `rivermark_plaza_bldg_*` dirs (not 8). |
| **R2** `w3r_prop_mapping_v1.md` | **PARTIAL (35/36 rows verified, 1 refuted)** | Every recomputable count and form-template measurement reproduced exactly (139 weeds/22 scenes · 337 lobes/52 clumps · N2 crown 48 · D3 118 m fence · line refs to the digit). **Refuted: C6c's "tactile=True on 39/41"** — the true state is **12 of 42 ON** (C4 6 + N5 6); five call sites pass `tactile=False`, landed in W2-D commit `b19a1af`, before this wave. The HOLD outcome survives; its briefing numbers do not. |
| **R3** `w3r_building_ab_v1.md` | **CONFIRMED (2 corrections required before use)** | Single-variable discipline, validity gate, all 133 B-HZ numbers, prim census, buried-glazing census, and every code-level claim reproduce independently. Corrections: (1) §4.2/§7.3-(4) quote only the mildest cut for arm (d) — the measured GI leak reaches **Δmean +1.50 / Δedge% −1.69 / Δw80 +1.06 / ΔσLF −0.32 ≈ 4× the noise floor** on the other two cuts; (2) F-4's "13 courses" is method-fragile — my direct joint count gives ~16 (autocorr supports ~13.4); corrected `scale_m` spans **0.90–1.10**, so the 0.87 endpoint must not be applied without the pixel re-verification the report itself demands. |

The wave's headline decision input — **R1 §2.4 dual-root licence correction** — is **fact-checked true
in every measurable particular** (§1 below). The residual is policy (whether to re-adjudicate the ~20
`rebuild-procedural` rows), not fact; note R2 §2.2 has already adopted the correction, so the two
documents no longer prescribe opposite implementations — the live conflict is smaller than R1's
blocker text implies.

---

## 1. Licence claims — re-executed first (all sources hit live this session)

### 1.1 NVIDIA Limited Use supplement `[law]` `[measured]`

Fetched both copies (2026-07-30):
`https://omniverse-content-production.s3.us-west-2.amazonaws.com/Assets/Isaac/4.5/Isaac/Environments/environment-supplement-LICENSE.txt`
and the same path under `Assets/Isaac/5.0/` — **identical 1,463-byte file, v. November 18, 2021**.
The load-bearing sentences, verbatim as quoted by R1 §2.1 and R3 §5.6:

> "The terms in this supplement govern your use of certain NVIDIA Omniverse USD assets in the
> **/Isaac/Environments** ("Limited Use Content")" · "…license to install and use copies of the
> Limited Use Content **for your use only, without modifications**…" · "2. The license grant for
> Content as described in the Agreement **does not apply to Limited Use Content**."

- Quotes verbatim-accurate. Scope is **path-scoped to /Isaac/Environments** exactly as both reports read it.
- **No licence file exists at the general roots** `[measured]`: HTTP 404 for
  `…/NVIDIA/dsready_content/{LICENSE.txt,LICENSE,EULA.txt}`, `Assets/simready_content/LICENSE{,.txt}`,
  `Assets/Isaac/4.5/LICENSE.txt`; the 100,902-line published index contains **zero** licence-named
  files (all 119 `licens*` hits are `license_plates` assets) `[measured]`. R1 §7's negative claim holds.
- The "general Content" tier for `NVIDIA/dsready_content/` therefore rests on the upper NVIDIA
  agreement — the same regime `license_audit_v1.md` verified on 2026-07-28 for `Assets/Vegetation/`
  (no-ML-clause verified there against the NVIDIA SLA and Product-Specific Terms; USD redistribution
  banned incl. "publicly accessible software repositories") `[law — in-repo audit, 2 days old]`.
  Extending that regime to a sibling prefix of the same bucket is textually sound; it remains an
  interpretation, and R1's standing recommendation (decline `rivermark_plaza_bldg_*`, supervisor
  confirms) is the right posture. **Nothing measured contradicts it.**

### 1.2 Dual-root claim — every byte pair verified live `[measured]`

HEAD requests, 2026-07-30 (claimed → measured, `G` = `Assets/Isaac/4.5/NVIDIA/dsready_content/`,
`R` = `Assets/Isaac/4.5/Isaac/Environments/Outdoor/Rivermark/dsready_content/`):

| Asset | G bytes | R bytes | Match |
|---|---|---|---|
| `bollard_01.usd` | 53,841 | 43,658 | ✔ / ✔ exact |
| `bench_curved_01.usd` | 73,849 | 57,159 | ✔ / ✔ |
| `safety_railing_01.usd` | 84,690 | 75,229 | ✔ / ✔ |
| `trashcan_cylinder_01.usd` | 49,221 | 39,040 | ✔ / ✔ |
| `bike_rack_01.usd` | 64,193 | 52,294 | ✔ / ✔ |
| `planter_round_02.usd` | 51,043 | 40,757 | ✔ / ✔ |
| `streetlamp_01.usd` | 63,781 | **HTTP 404** | ✔ (exists only at G, as claimed) |

Live paged-list recounts: `props_poles` USD **1,454 vs 1,018**; `props_general` USD **2,571 vs 110**
— both exact. Overlap of relative paths between the two roots, recomputed from the full 275,368-key
listing: **18,905 — exact** `[measured]`. `rivermark_plaza_bldg_01.usd` confirmed present under the
general root (48,194 B). **R1 §2.1/§2.4's factual base is fully confirmed; R2 §2.2's adoption of it
was correct.**

### 1.3 CC0 sources `[law]` `[measured]`

- **Poly Haven** (`https://polyhaven.com/license`, fetched): all assets CC0; "use for any purpose,
  including commercial"; "**You can redistribute them** … even in a product you sell"; no attribution
  required; no AI/ML restriction. Live API count `api.polyhaven.com/assets?t=models` = **521 models**
  — exact. 13/13 spot polycounts+dimensions match the reports to the digit (incl.
  `modular_urban_apartments_facade` 118,215 · `street_lamp_01` 30,610/3,871 mm ·
  `korean_fire_extinguisher_01` 9,913 · `celandine_01` 1,746,764 · `grass_medium_02` 1,043,926 ·
  `metal_trash_can` 13,960/1,847 mm) `[measured]`.
- **ambientCG** (`https://docs.ambientcg.com/license/`, fetched): CC0 1.0 Universal; copy/modify/
  distribute incl. commercial; raw files may ship in a project; no AI clause. Live API total =
  **2,875**; `3DModel` = **34, of which 32 food-named** (non-food: `3DStick001`, `3DTreeStump001`);
  Facade 26 · Sign 26 · Leaking 39 · RoadLines 69 · LeafSet 30 · SurfaceImperfections 20 — **all
  exact** `[measured]`. *Erratum*: R1 §1's per-type row omits 4 `HDRIElement` assets (its own total
  2,875 includes them).
- **Megascans / Mixamo / RenderPeople / brand vehicles**: nothing in any of the three reports
  procures from a banned source `[measured — shortlists and procurement ledgers read in full]`.
  `honey`/`tri`/`generic` fictional-brand reading is consistent with ZZ §10.6.
- **CC-BY ledger**: no CC-BY *asset* enters any shortlist. The one CC-BY 4.0 item touched is the
  in-repo reference photo `wc005_ccby40_…삼일공원_1.jpg`, and R2 §D6 correctly states the ledger
  obligation if a derivative is published `[law]`.

### 1.4 Third-party provenance `[measured]`

`nv_content/manifest.csv` (2,124 rows) re-parsed: `_Supplier` = NVIDIA 1,956 · Agility3 83 ·
BDesign 50 · SimAction 22 · **Mathworks_Modified 7** · Kraken/CGTrader/SpeedTree/Ford/Hum3D/
Mobiltech 1 each — matches R1 §2.3 exactly, and `safety_railing_01` + `bollard_02` are confirmed
Mathworks_Modified rows. The policy question R1 raises (does NVIDIA's grant suffice for
CGTrader/Hum3D-sourced rows) is real and stays with the supervisor; recording `_Supplier` in the
manifest is the right mitigation.

### 1.5 Licence-guard engineering notes (forward-looking, minor)

1. R1 §6.6 adds `assets/urban/` to `.gitignore` — currently **not present** (directory doesn't exist
   yet) `[measured]`. The ignore line must land **in the same commit** as `download_urban.py`, or an
   interrupted first pull could leave unignored NVIDIA USD in the tree.
2. `BANNED_SUBSTRINGS` (§6.2) is sound; note `streetlamp_01` exists *only* at the general root, so a
   guard failure would 404 rather than silently fetch Limited Use bytes for that asset — the guard's
   real value is the 18,905 dual-root keys.
3. R2 §5.2's "Poly Haven URLs return 403 without a User-Agent" did **not reproduce** today (200 with
   empty UA and with `Python-urllib/3.10` on `dl.polyhaven.org`) `[measured]`. Harmless either way —
   keep the UA header — but the `[measured]` tag on that sentence is stale.

---

## 2. Catalog spot-verification — 20+ rows, all exact `[measured]`

Everything below was re-measured this session (HEAD = live S3 byte size; tris/bbox/mpu via
usd-core on the probe files whose bytes match live):

| # | Row | Claimed | Measured | ✓ |
|---|---|---|---|---|
| 1 | `typical_building_10` chain bytes | 73.1 K / 1,771.1 K / 12.9 K / 1,737.0 K | 73,060 / 1,771,111 / 12,873 / 1,736,977 B | ✔ |
| 2 | `typical_building_10` geometry | 21,965 tris · 34.74×30.17×30.33 m · zmin −7.904 · mpu 1.0 | 21,965 · 34.743×30.172×30.332 · −7.904 · 1.0 | ✔ exact |
| 3 | wrapper-alone trap | 504 tris without instance proxies | 504 | ✔ |
| 4 | `Building_178` | 1,354 tris · mpu 0.01 · zmin 0 · 60.39×32.86×5.68 m | 1,354 · 0.01 · −0.0 · 60.393×32.863×5.677 | ✔ |
| 5 | `sign_kr101` | 104 tris · 0.002×**0.844**×0.741 m · mpu 1.0 · zmin 0 | identical | ✔ (844 mm vs 900 mm flag stands) |
| 6 | `sign_kr101.png` | 2048×1800 RGB no alpha | 2048×1800, mode RGB | ✔ |
| 7 | korea_mobiltech signs | 156 USD + 158 textures | 156 / 158 (live list) | ✔ |
| 8 | mobiltech poles | manifest-only, zero geometry | 4.5: 12 folders, only `mobiltech_manifest.csv`; 5.0: 12 folders, 0 USD | ✔ zero-geometry; **count is 12, not 13** |
| 9 | `shared_textures` per-building match | `_10`→6 · `_18`→0 · `_106`→0 | 6 / 0 / 0 | ✔ (per-asset `--discover` requirement upheld) |
| 10 | `apt_complex_assembly` | 671.86 MB | 5 keys, 671.89 MB | ✔ |
| 11 | `nv_core/materials/signs/` | 16 files / 2.15 MB | 16 / 2.15 MB | ✔ |
| 12 | group sums (thumbs excluded) | signs_kr 314 f/41.92 MB · hedges 21/13.26 · streetlamps 12/0.51 · railings 8/0.29 | 314/41.92 · 21/13.26 · 12/0.51 · 8/0.29 | ✔ all four exact |
| 13 | dual-root byte pairs + counts | §1.2 above | 7/7 pairs + 4/4 counts + overlap 18,905 | ✔ |
| 14 | Poly Haven censu s+ spot polycounts | 521 · 13 assets | 521 · 13/13 | ✔ |
| 15 | ambientCG census | 2,875 · 3DModel 34 (32 food) · 6 category counts | all exact | ✔ |
| 16 | PH negative claims | no bollard/handrail/kerb/tactile/bus-shelter | 0 hits over the 521-model index | ✔ |
| 17 | species negative claims | ginkgo/zelkova/keyaki/chionanthus/lagerstroemia/metasequoia = 0 | 0 hits over 275,368 keys + 100,902 lines | ✔ |
| 18 | SimReady dims | `metalfencing_a1` 0.23×0.23×1.07 · `_a2` 0.23×1.23×1.07 · `waitingbench` 0.66×1.77×0.84 | identical in `asset_info.json` (1,029 entries) | ✔ |
| 19 | local veg | `Grass_Short_C` 1,598 tris/0.28×0.30×0.12 PASS `edge_weed` · `Switchgrass` 8,934/2.01×2.03×1.37 PASS `riparian_grass` · Boxwood h 0.741 · Privet h 1.113 | usd-core + `veg_manifest_w2.json` identical | ✔ |
| 20 | wrapper-chain traps | `bench_park_01.usd` sublayers `../bench_park_03/…`; `_inst` carries `shared_textures` overrides; `_inst_base` points at nonexistent `materials/textures/` | `subLayerPaths=['../bench_park_03/bench_park_03.usd']`; 4 override refs vs 4 dead local refs | ✔ both traps real |

**R1 errata found**: (a) `rivermark_plaza_bldg_*` = **9** folders (01–08 **+ 06a**), not 8 — no
consequence, all declined; (b) pole folders **12**, not 13; (c) §6.5 placement row — see §5.

---

## 3. R3 A/B audit

### 3.1 Repo hygiene — clean `[measured]`

`git status`: only the three W3-R survey reports (now + this file) untracked; last commit is the
supervisor's lighting-round commit `328fe4a`. `scenes/main/_w3r_scene20_arms.py` absent, no stale
`__pycache__` entry. `look_check/*` is gitignored (`.gitignore:23`), so the 7 arm dirs, crops,
drivers and logs are round artefacts, exactly as §11 states. **No tracked file changed.** ✔

### 3.2 Design and execution — single-variable discipline upheld `[measured]`

- **Arm chain** (a→b geometry · b→b2 glazing · b→c materials · c→c2 shell family · a→d one
  building · a_rep2 floor) is a valid isolation chain. One caveat worth recording: **(b)→(c) is a
  composite change** (shell+stone+parapet+metal+dark in one step). F-5's attribution to the *shell
  family* is nonetheless supported, because (c) and (c2) differ only in shell and collapse
  `edge%` identically (10.9/13.0/4.9 in both) — but the plinth/metal contributions are never
  isolated. Minor; conclusions unaffected.
- **Render order**: PNG mtimes prove every arm wrote `d2 → d5 → d10 → h0.9_d2 → h0.9_d5` — the
  §1.2 order-prefix claim holds for **all** arms. (The `manifest.json` of arms a/b/c lists shots in
  judged-cuts-first order — a bookkeeping artefact; mtimes are authoritative. Log timestamps are
  UTC; mtimes KST.) Execution was strictly sequential, 08:08–08:33 KST, one process at a time. ✔
- **times.tsv** reproduces §4.3 exactly, **including the failed arm-d row (7.7 s / 0 cuts)** — the
  honest artefact of §5.6 Correction 3. *Gap*: no `a_rep2` row exists, yet §4.3 quotes 27.6 s for
  it `[measured]`. Bookkeeping only.

### 3.3 Numbers — independently reproduced `[measured]`

- **Validity gate**, recomputed from pixels with my own metric (RGB-channel-mean |diff|):
  0.136 / 0.428 / 0.279 vs noise floor 0.477 / 0.443 / 0.284 → **gate passes on all three cuts**,
  same structure as the report (their absolute values use a different channel reduction). Note the
  margins on `h0.3_d10` and `h0.9_d5` are **3.4 % and 1.8 %** — narrow in their numbers too
  (0.641/0.661, 0.478/0.486). The gate is honest but thin; a third rep would have cost 30 s.
- **All 133 B-HZ table numbers** match `_metrics.json` at rounding tolerance (0 mismatches).
  Noise floor: worst B-HZ band-metric |a_rep2 − a| = **0.0602** (claim ≤ 0.08). ✔
- **Prim census** (`…_census.txt`): arm a 164/161 gprims, stage 527; arm b 101/98, stage 464 —
  exact per-building (44/62/58 vs 28/57/16). ✔
- **Buried-glazing census re-run by me** (`_buried_audit.py`, CPU): scene20 C 12 · D 17 · E 2
  buried, D's 32 non-glazing attachments outward-correct — matches §5.1 prim-for-prim, and the
  root cause is in source: `Win_* out=−0.10 (face −0.08)` · `WinBand −0.12 (−0.10)` ·
  `CurtainGlass −0.10 (−0.075)` · `ShopGlass −inset (−0.10)` / `ShopDoor (−0.07)` ·
  `EntryGlass −0.10 (−0.07)` against `build_mass`'s solid `Shell` box. **F-1 confirmed.** ✔
- **Self-check + scan re-run**: `python3 building_kit.py` → **135/135**, 33-scene scan **4,546
  (2,137 windows) → 1,855 (−59.2 %)**, 89 bd, and the two budget warnings incl. scene21
  `office/mid 16 > 15`. ✔ `lod_dist` default `dist = abs(p.plane)` confirmed at
  `building_kit.py:571`; `frame_ceiling` = +8° line confirmed in `facade_kit.py`; `WIN_EPS = 0.005`
  convention confirmed at `scene_common.py:2644`; **24 `sc.build_building` call sites over 23
  scenes (scene18 ×2)**; `building_kit.py` not symlinked in `scenes/main/`. ✔
- **sceneC2 has zero `buildings`** — confirmed (`sceneC2_leaf_stairs.py`, 0 hits). ✔

### 3.4 Finding RT-1 (correction required) — §4.2/§7.3-(4) understate the arm-(d) GI leak

The printed arm-(d) row equals the `h0.3_d5` cut only. Recomputed per cut `[measured]`:

| cut | B45 Δsd | B45 Δmean | B30 ΔσLF | B30 Δedge% | B30 Δw80 |
|---|---|---|---|---|---|
| h0.3_d5 (the printed row) | −0.21 | +0.57 | −0.02 | −1.34 | +0.96 |
| h0.3_d10 | −1.12 | +1.43 | **−0.29** | −1.42 | +0.44 |
| h0.9_d5 | −1.13 | **+1.50** | **−0.32** | **−1.69** | **+1.06** |

Against a ≤ 0.08 floor, the asset backdrop moves the judged ground band's **σ_LF by up to −0.32
(≈ 4×the floor)** — σ_LF is a live W2 gate (9/33 passing, STATUS carry-over), so this is not
cosmetic. The report's own rule ("backdrop albedo changes must be re-gated") is *strengthened* by
the correction; but §7.3-(4)'s quoted bounds (−1.34 / +0.96) and §9-9's "no judged-region change
beyond the §4.2 leak" must be restated with the h0.9_d5 values before S3 (asset backdrop) ships.

### 3.5 Finding RT-2 (correction required) — F-4's course count is method-fragile

Re-measured `assets/scene01/brick_red_diff.jpg` (4096²) three ways `[measured]`:
- high-passed row-profile autocorrelation, per 512-px column block: lags **283–411 px, median 306**
  → **13.4 courses/tile** — *supports* R3's 315.1 px / 13.0;
- direct mortar-joint peak count on the gradient profile: **~16.4 courses (spacing ≈ 250 px)**;
- visual count on a numbered strip: **~16 joints**.

The texture (reclaimed brick, heavily cracked) has an **irregular course module** — a single
"courses per tile" number is not well-defined to better than ±20 %. Consequences: at `scale_m 2.0`
the rendered course is **122–150 mm = 1.8–2.3× the Korean 67 mm** (over-scale conclusion **holds**),
but the corrected `scale_m` spans **0.90–1.10 m**, so applying the report's low endpoint 0.87 could
overshoot ~20 % the other way. R3 already demands pixel re-verification before S1 and flags the
vendor metadata conflict; my re-measurement shows the *pixel side* is fragile too. Extra fact: Poly
Haven's own metadata is self-contradictory — `dimensions: 3000 mm` vs `scale: "1.5x1.5"` `[measured
— API]` — reinforcing "pixels are the only authority" and, frankly, that this texture is a poor
metrology target; consider re-deriving from a mortar-grid overlay render instead of the diffuse map.

---

## 4. Prop verdicts vs project rules

### 4.1 Recomputed counts — R2's arithmetic is excellent `[measured]`

| Claim | Recomputed | Result |
|---|---|---|
| weed cubes: 8 of 19 profiles carry `("weed", n)`; ×`SCENE_PLANS` = **22 scenes / 139 cubes**, per-profile n = 6/8/8/6/5/4/4/4 | executed `GROUND_PROFILES × SCENE_PLANS` | **exact**, incl. every scene list |
| weed cube form: Box 0.10×0.10×U(0.5,1.0)·0.12, albedo 0.15, `exc="weed"` | `ground_kit.py:2781 ff` | exact |
| scene05 backdrop: **337 lobes / 52 clumps** | `backdrop_instances()` AST-exec'd | **exact** (27×6 + 25×7) |
| N2 hedge: 48 crowns over one unbroken 52 m band | `PARAMS` y −26…26, h 0.9; `build_hedge` `crown_max=48` cap | exact — 48 **is the cap**, band is 52 m unbroken |
| bench 5 prims, 1.8×0.4 seat t 0.06 top 0.45, 4 legs 0.06² | `scene_common.py:2913` | exact |
| bollard r 0.060 / h 0.750 (−6.25 % vs 0.80 legal), mirror `metallic 0.9/rough 0.35` | `scene_common.py:2936` | exact |
| planter curb t 0.25 / h 0.45, cap 0.05, soil 0.10 below cap top | `build_planter` defaults | exact (soil = grass_h 0.40 vs cap top 0.50) |
| canopy = 1 flat slab + 4 posts, slope 0 | `scene_common.py:2011` | form exact; *default* `roof_t=0.12` — the claimed 0.14 is caller-side, unchecked |
| D3 fence: one box x −22…+96 (118 m), t 0.12, h 1.75, no posts | `PARAMS["fence"]` | exact |
| scene01: 6 benches · 4 streetlights · 5 planters in `PARAMS` | AST-exec | exact |
| C7a targets exist (N4 `wall_plates` · C1 `signpost` · C4 `sculpture` · D2 slogan ×2) | greps | all present |
| line refs 2781/2796/2852/2913/2011 | sed | all five to the digit |
| leaf budget quote (−0.255 s/cut, σ 0.109, 595→0.69 MB = 863×) | `leaf_globalization_budget_v2.md` | verbatim |
| era §6.2-E "12 cells … zero built … largest single realism lever" | line 908 | verbatim |
| 수목보호판 min 1.5 m / 5 cm clearance `[law]` | kpg §5.3 | present |
| place_shrubs exists and auto-disables seasonal/flower prims | `_deactivate_seasonal` call in body | confirmed |

Convention sources verified: v5.2 §8 (only real 도로교통법 plates + facility signage), §6 (조형물/
가구 상한 — openness), §9 (scene05 bench-ring removal) all present in `user_feedback_v5_1.md`
`[measured]` — C7a/E4/B2b rest on real rules.

### 4.2 Finding RT-3 (**refuted claim**) — C6c's "tactile=True on 39/41"

Recomputed from the scenes' own placement functions (`bc.bollard_line` executed, lists parsed)
`[measured]`:

| Scene | Units | `tactile` at the call |
|---|---|---|
| D1 | 2 | **False** (`bollard.tactile=False` in PARAMS) |
| C4 | 6 | True (default) |
| N1 | 5 | **False** (explicit kwarg) |
| N2 | 9 | **False** (explicit) |
| N3 | 10 | **False** (explicit) |
| N4 | 4 | **False** (explicit) |
| N5 | 6 | True (default) |
| **Total** | **42** | **ON = 12, OFF = 30** |

`git log -S "tactile=False"` dates all four N-scene flags to **W2-D commit `b19a1af`** — they
pre-date this wave; the call-site kwargs sit on the *last line* of multi-line calls, which is
presumably how they were missed. The in-code comments show W2 §12.5-(2) deliberately replaced the
per-unit pads with ground_kit's continuous 0.60 m band in those scenes.

**What survives**: the §2.13① conflict is real but 4× smaller (12 units in 2 scenes, not 39 in 5);
N5's "55 px invisible" measurement is consistent (N5 is ON); the HOLD posture ("user owns
tactile-OFF; do not touch") remains correct. **What must change**: the supervisor briefing numbers,
R2's blocker bullet, and the unit total (42, not 41). The ruling itself may get *easier*: the
remaining ON population is C4+N5 only.

### 4.3 Season-pixel rule

- **R2 complies.** All five plant rows resolve to local, `veg_manifest_w2.json`-PASS assets
  (re-measured, §2 row 19). The 16 CC0 candidates were *rejected*; the atlas-level (not UV-sampled)
  screen is disclosed and only ever used in the rejecting direction — a conservative screen is an
  acceptable instrument for rejection, not for clearance, and R2 uses it only to reject. ✔
- **R1 gap (Finding RT-4).** §4 row C and §5.2 shortlist **`veg_tree_cherry_japanese_01`** and the
  hedge trio incl. **`veg_shrub_hedge_yellow_01`** with **no pixel verification** — against the wave
  rule ("pixel-verify foliage/props before recommending") and against W2's own removal of 벚꽃/계절
  관목 (STATUS: "벚꽃·계절 관목 제거… 픽셀 검증"). A blossoming cherry or an autumn-yellow hedge
  would re-introduce exactly what W2 purged. R1 *did* apply the rule to sign plates and flagged the
  `.dds` render question, so this is an omission, not a method error. **Procurement of those two
  rows must be pixel-gated** (the `hedge_yellow` name alone is a season flag); note R1's `sct_leaf_pile`
  recommendation is scoped to C2, the leaf scene, which is season-consistent. ✔ elsewhere.
- **R3 complies** for its single asset (arm-d crops eyeballed for C1's snow question, §7.2, carried
  as a precondition not a clearance — correct posture).

### 4.4 No people / no vehicles `[measured]`

R1 catalogues then **defers** `Isaac/People`, Reallusion, `ncap_*`; bans ford/volvo/piaggio/hero;
keeps fictional honey/tri available-but-unused. R2's E1 explicitly excludes forklift/truck; nothing
in any shortlist or work package places a person or vehicle. Consistent with STATUS 규율 and ZZ
§10.6. ✔

### 4.5 Bollard law and the 연대 3요소 discipline

The statutory numbers used (h 0.8–1.0 m · Ø0.1–0.2 · spacing 1.5 m · 충격흡수 재료 · 0.3 m 점형블록,
교통약자법 시행규칙 별표2 제7호) are the same values already established in the project's own
`korean_pedestrian_geometry.md` and stair-compliance audits `[law — in-repo verification chain]`;
`build_bollard`'s 0.75 m / mirror-stainless deviations are real (§4.1). The 96.0 % 부적정 figure is
carried as `[stat]` with source (한국시각장애인연합회 2023, n=337) — used to justify *non-compliance
jitter*, i.e. in the direction the 실사례-우선 discipline prefers. The 844 mm vs 900 mm sign issue is
correctly held at the 연대-3요소 gate by both R1 and R2 rather than auto-rescaled. ✔

---

## 5. Cross-report consistency

1. **R1 §2.4 vs R2 §2.2** — facts verified (§1.2); R2 adopted the correction before delivery, so the
   packages agree on licence and disagree only on *whether Korean-ness alone* keeps the ~20 rows
   procedural. That is a design call, not a factual conflict. R1's blocker phrasing ("currently
   prescribe opposite implementations") overstates the live state.
2. **R3 Corrections 1–3 to R1 §6.4/§6.5 — all three verified** `[measured]`:
   - C1: wrapper alone = 504 tris (no instance proxies), `_inst.usd` = 61 prims / 21,965 tris —
     reproduced; `_inst` is also the layer carrying the real `shared_textures` overrides (4 refs)
     while `_inst_base`'s `materials/textures/...` targets don't exist. Reference `_inst.usd`.
   - **C2: R1 §6.5's "translate +7.904 in Z" is wrong** — decisive mesh-level evidence: only the
     foundation mesh (`opaque__concrete__base_014`) spans −7.90…21.8; **every wall/window mesh
     starts at z ≈ +0.10** → local z=0 *is* street grade; +7.904 would hoist the facade 7.9 m.
     R1 §6.5's own caveat ("measure per asset") does not rescue the row; fix it before
     `download_urban.py` carries the table.
   - C3: the failed `AddXformOp` attempt is honestly logged in times.tsv (7.7 s / 0 cuts row).
3. **R2's B1b/B2c hand-offs and R3's C2-to-midground hand-off are mutually consistent** (C2 has no
   buildings; its horizon is hedge rows — both reports say so, and the file confirms).

---

## 6. Blocker adjudication (what the supervisor actually needs to rule on)

| Blocker | Status after verification |
|---|---|
| R1 §2.4 / R2 conflict on street-furniture route | **Facts settled by measurement** (this file §1.2). Remaining: policy on re-adjudicating ~20 rows + the luminaire-head borrow option. R2's Korean-ness rejections stand on live-verified dimensions. |
| `rivermark_plaza_bldg_*` under general root | Exists (9 dirs). Decline recommendation is sound and free; confirm. |
| `sign_kr101` 844 mm vs 900 mm | Measurement re-verified exact. Keep at the 연대-3요소 gate; no uniform rescale. |
| Third-party suppliers (CGTrader/Hum3D/Mathworks_Modified) | Rows verified in manifest. Policy call stands; `safety_railing_01` is the only shortlist item affected. |
| `typical_building_18/106` textures resolve elsewhere | Verified (0 prefix matches). Per-asset `--discover` is mandatory; do not finalize the manifest before it. |
| R2 §2.13① tactile | **Re-brief with corrected numbers: 12/42 ON (C4·N5), not 39/41**; W2 already converted N1/N2/N3/N4/D1. |
| R2 §2.13② D3 classification | Untouched by my findings; still a genuine convention-vs-header conflict. |
| WP-1 freeze window / collision with `build_railing_line` P0 | Real; sequencing requirement consistent with STATUS 규율 (공유모듈 동결). |
| R2 D4 double-block (tactile-OFF + GT-E1′ 0.48 m > 0.30 m) | Consistent with era §5.3 and the D14 carry-over; HOLD is right. |
| R3 F-1 fix before integration + new self-check (`out_max > 0`) | Root cause verified in source; the proposed check is the correct invariant. |
| usd-core absent from project venv (R2 method note) | True for the project venv; a working usd-core 0.26.8 venv exists at `/tmp/usdvenv` (session-scoped, not a repo asset). |

---

## 7. Corrections list (actionable, by owner)

1. **R2**: rewrite C6c/blocker numbers → 42 units, 12 ON (C4 6 · N5 6), OFF flags landed in W2-D
   `b19a1af`; adjust §0's "3 HOLD" framing text where it cites 39/41. (Verdict `HOLD` itself: keep.)
2. **R3**: restate §4.2 arm-(d) row and §7.3-(4) with per-cut ranges (worst: Δmean +1.50, Δedge%
   −1.69, Δw80 +1.06, ΔσLF −0.32); re-derive F-4's `scale_m` from a cleaner measurement before S1
   (my three-method band: 0.90–1.10; do not ship 0.87 as-is).
3. **R1**: fix §6.5 tb10 row (no Z lift; R3 Correction 2), pole folders 13→12, plaza dirs 8→9
   (+06a), add `HDRIElement 4` to the ambientCG type row; **add pixel-gates for
   `veg_shrub_hedge_yellow_01` and `veg_tree_cherry_japanese_01`** before they enter any manifest;
   land the `assets/urban/` gitignore line in the same commit as the downloader.
4. **Bookkeeping (any owner)**: add the missing `a_rep2` row to times.tsv convention next round;
   note the manifests' `shots` ordering is not render order (mtimes are).

## 8. What I did NOT verify (scope honesty)

- R1 §2.2's `Assets/ArchVis/` tier row (not spot-checked; same-bucket inference).
- R3's 16/89 wrong-LOD-tier figure and the 223/359 unseeable-prim split (mechanism verified in code
  — `dist = abs(p.plane)` — and the 5-scene census driver is archived; the specific tallies were
  not re-run).
- R2's 58/53/47 PARAMS totals beyond the scene01 spot (arithmetic of the stated per-scene lists
  sums correctly to 58/53/47; only scene01 re-executed).
- The 90-day-old-standard side of the 900 mm 주의표지 figure (both reports already tag it
  `[assumed]` and gate it).
- Any GPU render of my own (no re-render was needed; all pixel claims were verifiable from the
  archived round artefacts).

## Appendix — reproduction

```bash
# licence + dual-root + catalog (live)
python3 <scratchpad>/rt_s3_verify.py            # HEADs, supplement fetch, recounts
# usd-core measurements
/tmp/usdvenv/bin/python  (tris/bbox/mpu on probe files; bytes matched live first)
# A/B numbers
python3 - < _metrics.json cross-check           # 133/133
python3 look_check/scene20/260730_w3r_bldgab/_buried_audit.py
python3 building_kit.py                          # 135/135, −59.2 %
# counts
/tmp/usdvenv/bin/python  AST-exec of GROUND_PROFILES×SCENE_PLANS, scene05 backdrop_instances,
                          batch1 bollard placement functions
# brick
FFT/autocorr/joint-count on assets/scene01/brick_red_diff.jpg (3 methods, §3.5)
```
