# Red team — W3 WINDOW 0 exit gate

> **Wave**: W3 · **Role**: WINDOW 0 exit-gate verification (Fable) · **Date**: 2026-07-30
> **Branch**: `feat/realism-v1` · **Tree verified at**: HEAD `50f7dfd` (T1 baseline commit)
> **Spec**: `Docs/briefs/w3_execution_spec_v1.md` — §5.1 WINDOW 0 exit criteria, §6 obligations.
> **Method**: nothing below is graded from a WP's own prose. Every load-bearing number was
> re-executed or re-derived with independent code (own algorithms where the WP's method could
> hide a shared mistake). Evidence tags: `[reran]` = the WP's instrument re-executed by me ·
> `[recomputed]` = my own independent implementation · `[static]` = AST/grep census by me ·
> `[viewed]` = image inspected by eye.
>
> **Scope discipline**: this report is the only file written. The T2 lane
> (`scripts/harvest_refs.py`, `Docs/reference_photos/w3/**`, `Docs/surveys/w3_evidence_close_v1.md`)
> was left untracked and untouched.

---

## 0. Verdict table

| WP / batch | Verdict | One line |
|---|---|---|
| **T1** placement linter | **CONFIRMED** | Baseline reproduces byte-identically ×3 (809 findings; ERROR 393 / WARN 385 / BLOCKED 29 / INFO 2; exit 1; 6.7 s); rules faithful to §10.3/§10.4/§1.8/§12; two documentation notes (§2) |
| **T3** geometry re-verify | **CONFIRMED** | Every number I recomputed with independent algorithms lands on T3's value — including the C-3 kill (7.46 mm) and the §10.5 fallback refutation. **CB-9's release condition is genuinely discharged** |
| **T4** urban loader | **PARTIAL** | Loader + 7 quirks + §1.11 override + refusals all verified on my own 10-asset sample; F-A/F-B/F-C reproduce. One `[measured]`-tagged claim in the report is false on this tree (§4.2) |
| **T5** GT ledger | **CONFIRMED** | 13/13 rows faithful to §8; all §6 cross-check citations I re-checked reproduce; watch items W1–W5 are real. One live process gap: GT-10's landing record (§5.2) |
| **CB-1** scene09 | **CONFIRMED** | Diff is exactly §10.5's three literal camera tuples + GT-10's post move; judge presets untouched (R-4/R-5/R-6 33/33 `[reran]`); gate numbers reproduce; 3 cuts viewed and diagnostic. Two notes (§6.2) |
| **WINDOW 0 exit (§5.1)** | **MET** | T1 ran clean on the untouched tree with the baseline recorded, nothing fixed; T3 published confirm/refute per number. Carried items in §7 |

---

## 1. What was run

```bash
# T1 — three runs, hashes compared, plus exit-code semantics
python3 scripts/placement_lint.py --scenes all                      # exit 1, 6.7 s
python3 scripts/placement_lint.py --scenes all --format json ...    # ×3 → md5 identical
python3 scripts/placement_lint.py --scenes scene15 --only LINT-6    # exit 0
python3 scripts/placement_lint.py --scenes all --enforce-lint9      # exit 2 (refuses to invent a band)
python3 scripts/placement_lint.py --scenes all --rules /nonexistent # exit 2
python3 scripts/placement_lint.py --scenes scene09 --require-placement  # exit 1

# T3/T4 — usd-core 26.8 in /tmp/usdvenv; my own measurement harnesses (scratchpad:
# rt_geom_check.py, rt_geom_check2.py, rt_t4_sample.py), shipped builders + shipped PARAMS
/tmp/usdvenv/bin/python urban_kit.py --self-check                   # PASS 275/275, 2.7 s

# tree invariants + CB-1 gate
python3 scripts/geom_invariance_check.py                            # R-4 33/33 · R-6 33/33 PASS
python3 scripts/geom_invariance_check.py --assert-no-residual-lookv1  # R-5 PASS
python3 scripts/regression_check.py --before look_check/scene09/260730_w2d_fix \
        --after look_check/scene09/260731_w3_cb1                    # 17 cuts: FAIL 0 · WARN 2 · INFO 3 · PASS 12
python3 scripts/regression_check.py --before look_check/scene09/260730_w2d_fix \
        --after look_check/_experiments/gates/scene09/260731_w3_cb1_ctl  # control: FAIL 0 · 11/14 UNCHANGED
```

Ownership audit `[static]`: each WINDOW 0 commit touched only its WP's §4 files
(`2333699` T5 ×1 file · `f20f5ff` T3 ×1 · `50189e9` S5 ×1 · `52d5253` T4 ×4 · `50ec53c`/`50f7dfd`
T1 ×2). `scripts/geom_invariance_check.py` untouched since `29e79b2` — T1 imports it only.

---

## 2. T1 — placement linter vs §10.4

**Baseline honesty** `[reran]`. Totals, per-check errors, runtime and determinism all reproduce
exactly as committed in `placement_rules_v1.yaml` `meta.baseline`: ERROR 393 = LINT-8 295 (31
scenes; C2/D4 carry no patch/stain) + LINT-4b 49 (20 scenes) + LINT-6 25 (h 0.750 m, split
4/4/6/5/4/2 across 02·05·06·08·11·12) + LINT-7-static 24. Three JSON runs md5-identical.
Exit codes 0/1/2 behave as documented, including `--enforce-lint9` → exit 2 with `band: null`
(§1.8 "prepare, don't enforce" honoured; LINT-9 emits BLOCKED, never ERROR).

**Corrected facts reproduced by me, not taken from T1** `[static]`: C-2 — grep returns 25 hits,
`sceneN1:154` is a comment, and the linter's static census (24 sites: N1 4 · N2 3 · N3 3 · N5 1 ·
C1 3 · C2 4 · C4 2 · D2 2 · D4 2) equals the spec's list item for item. C-9 — the YAML carrier
set is exactly the 19 corrected scenes; the harness census raised nothing in either direction.
C-13 — `scene03:197-200` has 4 benches (5/172/93/187). LINT-7's 112 substantive rows contain
§10.1 rows 5–12 item for item (scene01 6 · scene06 3 · scene11 2 · scene03 8 = 4 blocks/pavilion
+ 4 benches · scene04 benches 96/94/4.5/93/87 · scene09 86.5/274/93.5/265.5 · scene13 174/−6/+3 ·
scene17 4 · D1 9), plus honest over-detection the spec does not list (two scene04 SignPost arms,
scene13 Sign_info 170°, and OQ-1's sceneD2 36 rows). OQ-1/OQ-2 verified at source:
`sceneD2:929/881/902` and `scene_common.py:2564` + scene02's Planter-borne `Yellow_Pine`
(LINT-4b ERROR on `/World/Scene02/Planter_1`) are all real.

**Design judged sound**: nodata-never-passes, inferred-always-WARN, DNT suppressions published as
INFO (the scene20 `/Diag` 30° suppression prints, quoting C-8), `[law]`-tagged thresholds match
§10.3 PE rows verbatim, LINT-8 exemptions are exactly §10.1's "directional yaw" list, and the
J-11 zero-locked callees are the three spec'd builders (verified at `ground_kit.py:606-607`,
`infra_kit.py:403`, `infra_kit.py:530-531`).

**Findings** (documentation, not blockers):

- **T1-F1 · the `per_scene` table is not "full" as its legend claims.** It tabulates one cell per
  (scene, check) at the dominant class. ERROR content is complete and exact (sums to 393,
  per-check identical), but 11 of 191 substantive-WARN rows and 39 of 190 nodata/BLOCKED rows are
  folded into dominant cells (e.g. scene06 LINT-6 shows `L66!` and drops that check's 1 nodata +
  1 substantive WARN row) `[recomputed]`. A reader summing the table reproduces ERROR but not
  WARN. Fix is one sentence in the legend ("dominant class per check") or a regenerated table.
- **T1-F2 · LINT-10 is softer than §10.4's letter.** The spec row says any `jitter=` kwarg > 0 is
  hard; the linter hard-bans only the three J-11 builders and reports the other six sites
  (scene06:276 · scene07:173 · scene11:250 · C2:166 · C2:264 · D3:198) at WARN
  `[static, reran]`. Grounded in §1.2 X2 (size/interval jitter is KEPT), disclosed as OQ-3, and I
  agree with the reading — but it is a deviation the spec owner should ratify, since a literal
  §10.4 enforcement would add 6 ERRORs.
- Minor: LINT-1b (PE-4 shoulder rule) is an addition beyond §10.4's ten — legitimate, tagged, inert.

---

## 3. T3 — geometry re-verification (CB-9 release)

I rebuilt the stages myself from the shipped builders and PARAMS (usd-core 26.8) and
re-measured with **different algorithms** than T3 (analytic ray/edge intersection for the rim;
my own Sutherland–Hodgman; 10 mm grid vs T3's 20 mm; 6 001-sample fascia probe).

| Claim | T3 | Mine `[recomputed]` |
|---|---|---|
| Landing union rim swing (C-3 kill) | 3.30000→3.30746, **7.46 mm** | 3.30000→3.30746, **7.46 mm** |
| Landing max corner radius | 3.307479 (+7.48 mm) | 3.307479 (+7.48 mm) |
| Landing footprint | x 0.1925…6.8075 · y −13.1904…−9.6925 | identical to 4 dp |
| NF-2 back-edge sawtooth | 190.4 mm behind y −13.0; ±190.9 mm/side at r_in | 190.4 mm; 190.9 mm |
| §10.5 fallback ratio | 7.08125 at every Δθ (seg 24…1000) | 7.08125 at all six seg values |
| Coplanar stacking | 123 pairs (23 adj) · ≥2-cover 8.551 m² = 49.4 % · depth 7 · band 12.95 mm | 123 (23) · 8.539 m² = 49.3 % (grid res) · depth 7 · 12.95 mm |
| Spiral tread | box 683.349 · ratio 2.266 · margin 1.03000 · corner +17.641 mm · step0 span 172.94°…198.60° | all identical |
| Fascia | corner 3.334159 (+4.16 mm) · NF-1 shift +16.26…+16.43 · soffit +13.03 · tilts −16.232/−21.749 · seg 150 | all identical |
| NF-3 notch | top face absent / end-face exposed over a ≈ 180.0°–181.7° at r 3.26 | reproduced — **no top face at all** over that span in my probe |
| Landing↔deck | 348.0 mm up-through · 2.0 mm top gap · bbox 9.922 m² | identical (deck x 2..5 · y −13..13 confirms bbox) |
| scene09 | 36 steps · run 13.960 · drop 6.120 · landings (3.74–4.94, −2.040) / (8.68–9.88, −4.080) · submerged 6 · water slab **top −5.190** · steps[30] top −5.240 at x 11.920 | all identical — **−5.240 is the tread, −5.190 is the water** |
| S09-A raking | 130.815° · −5.502° · 14.6017 m · eye 2.990 m over water | identical |
| C0-7 balusters | pitch 116.0 · Ø 18.0 · clear 98.0 mm uniform | identical (31 balusters on a 4 m run) |
| Call-site censuses | scene05 **12** · scene19 4 · scene06 8 · **scene13 0** · railing 16 sites/14 scenes · only `scene10:1195 baluster_r=0.0` | identical `[static]` (AST, my own walker) |

The one apparent divergence is explanatory, not numeric: T3's as-built fascia lip
(−26.20/+165.85) is measured against the **tread boxes**; my −21.96/+169.87 is design + NF-1
shift against the **tread table**. The ±4.1 mm difference is the tread boxes' own 0.245°
tangential overshoot — T3's A-1 already says exactly this ("the two defects interact").

**Also verified**: the §4-fallback refutation is provable in one line of algebra
(`ratio = margin · r_out / r_in`, sin cancels) — the spec's "seg ≈ 165" clause cannot be
satisfied by any seg and should be struck as T3 recommends. LOOK_GEO gate at
`scene_common.py:190-192` `[static]`; scene02 has zero `build_railing_line` calls (line 177 is a
comment) and pit rail 0.15 + 0.90 = 1.05 m `[static]`; `outer_r=3.36` at `scene06:238`.
`geom_invariance_check` R-4/R-6 33/33 + R-5 clean on the current tree `[reran]`.

**Verdict: CB-9's T3 gate is honestly discharged.** T3's four downstream demands (kill 99.0 mm ·
strike the fallback clause · fix NF-1 inside K4(d) · amend GT-6's affected set to 05·19 and
scene05 to 12 sites) are all supported by my independent numbers.

---

## 4. T4 — urban loader vs §3.4 + §1.11

### 4.1 Verified

- **Self-check** `[reran]`: PASS 275/275 (mpu, tri, placement, aliases, banned paths, Z_REVIEW
  drift 0), far-tier override 40 materials / **0 albedo-scaled**, 63/79 meshes bound.
- **My own 10-asset sample** `[recomputed]` (bench_park_01/05, concrete_block_02, Building_178,
  typical_building_10/109, bollard_01, strt_fxd_bollard_05, veg_shrub_hedge_green_01,
  sign_krroadname): tri/mpu/size/zmin reproduce the manifest on 9/10 by my own traversal; the
  hedge's deltas are my harness's PointInstancer double-count and instance-spread bbox, not a
  loader error (F-D's 758,206 effective count is the manifest's and T4's agreed value).
- **Quirks**: aliases resolve to C-26's three targets by manifest key list `[reran]`; parent-Xform
  op order `[translate, rotateZ, (rotX/rotY), scale]` with the reference on `/Asset` `[reran]`;
  far tier lands at metre scale (Building_178 → 5.677 m world) `[reran]`; z policy — bollard_01
  exposes 0.8202 at grade / 1.0028 at base, exactly `zmin` arithmetic `[recomputed]`.
- **§1.11 override**: keeps `diffuse_texture`/normal/roughness, multiplies `diffuse_tint` by
  `k = min(1, 0.55/eff)`, sets `metallic_constant` 0.0, leaves glass/emissive unbound (2 per
  building × 8 = the 16). **F-A reproduces**: shipped tints already put every overridden material
  inside the band (my audit of Building_178: wall 0.874×0.599 = 0.523 · walkway 0.359 · roof
  0.249 · brick 0.074 · interior 0.019), so k = 1.000 and the metallic row is the only live
  effect. Both MDL citations exact: `SimPBR_Model.mdl:91` literal tint multiply,
  `SimPBR.mdl:792` metallic lerp from `metallic_constant` `[static]`.
- **F-B** `[recomputed]`: the manifest's `z_advice` has **zero** lift rows (208 "no correction
  needed" + the "0.0 % below grade" family + 3 attachments). §3.4-1's "the 28 props that
  genuinely need −zmin are listed there" is contradicted by the manifest itself — T4-Q2 is a
  genuine spec defect.
- **F-C** `[recomputed]`: `typical_building_109.usd` (wrapper) carries `opaque__emissive__beacon_01`
  + `opaque__emissive__lights_002`; `typical_building_109_inst.usd` carries **zero**
  beacon/emissive prims. The night rig genuinely dies with quirk 2.
- **Refusals** `[reran]`: `veg_shrub_hedge_round_01` refused outright; leaves refused at
  scene=01 / placed at C2; Type-III barricade refused at 08 / placed at D2; the banned-path
  guard fires on `rivermark_plaza_bldg_06a`.
- **T4-Q3 supported** `[recomputed]`: `strt_fxd_bollard_05` manifest zmin −0.0539 → **791 mm
  exposed at grade** (non-compliant, < 800 mm) vs 845 at base; bollard_01 safe both ways.

### 4.2 Finding

- **T4-F1 · a false `[measured]` claim in the report.** §1 states *"§6.2's T4 trap is
  reproduced: `bench_park_01` reads 0 triangles under a plain `stage.Traverse()`"*. On this
  tree it reads **35,396** under plain `Traverse()` — same as with proxies `[recomputed]`, and a
  12-asset census (both buildings tiers, benches, hedges, PH props) finds **zero** assets where
  plain ≠ proxies. The loader's own conditional trap-print (`urban_kit.py` self_check) never
  fires — the code is honest, the report sentence is not. Root cause: spec §6.2's premise itself
  does not hold on the procured mirror (no `_inst.usd` in it authors `instanceable`; the trap
  would only appear on a placement that sets `instanceable=True`). **Action**: T4 strikes or
  reworda the sentence; the spec owner should amend §6.2's T4 row the same way. The
  `TraverseInstanceProxies` discipline itself stays — it is still required for
  `instanceable=True` placements and costs nothing.
- Informational: the manifest's `size_m` for `bench_park_01` is axis-swapped
  (1.149 × 1.735 vs §3.1 C1's "1735 × 1149") — procurement's field, no W3 consumer reads the
  axes individually today.

---

## 5. T5 — GT ledger vs §8

### 5.1 Verified

- **13 rows == §8's 13**, including the discipline of *not* silently correcting GT-6's
  known-stale parenthetical ("05 · 19 · 13 share the builder") — T3's correction is recorded as
  input for the spec owner, and the ledger kept the spec's text per its own §12-11-like rule.
  Status column checks out (GT-4 HELD on P-5, GT-6 PROOF-ONLY + BLOCKED-on-T3 as of its landing
  time, rest OPEN).
- **§6 cross-check citations re-verified by me** `[static]`, all exact: `ground_kit.py:2363-2370`
  gt_change guard (raises without a non-empty ledger) + `GT_DELTA 0.020:122` +
  `EDGE_STANDOFF 0.80:123` + `prim_cap=60:1440` + `_box_aabb:559`/`_obb_aabb:564` +
  `gt_changes:1416-1420`; `scene02:63` (3.200) / `:132` (pit x1=7.0) / `:222` (curb_top 0.10);
  `scene08:399-401` (exactly 2 TempPost boxes) / `:913` (`temtape`); scene13's **four**
  `proud=0.007` walks at `:181-184`; scene09's 6 mooring piles at T5's pinned HEAD `04cc85c`
  (the line numbers have since drifted +21 — CB-1 landed after T5, expected); `Grass_Short_C`
  0.279×0.304×**0.125** at `download_vegetation.py:433,447` (so **W1 is real**: native height
  breaks GT-9's h ≤ 0.12 condition and the clamped-`proud` scale instruction is load-bearing);
  `redteam_w3_intake.md:211` names **three** rows (W3's preamble-count discrepancy is real);
  `96968f3` is the prim-hash method; weeds 139/22 per `redteam_w3r.md:249`; scene05 wedge notes
  at `:192/:199/:222`.

### 5.2 Finding

- **T5-F1 · the append-before-land regime failed its first live test at the "record" step.**
  GT-10 landed in `50189e9` (CB-1) and passed its gate, but §4's landing record is still
  `— · — · —` and the row still reads OPEN. Ledger law §0-3/§4 says the landing record is
  appended "by the owning WP at the moment it commits" — but §4.1 gives the *file* to T5
  exclusively, so S5 could not have appended without violating file ownership. **Two actions**:
  (1) T5 appends GT-10's landing record now, from S5's pasted command
  (`regression_check` 260731_w3_cb1 vs 260730_w2d_fix, FAIL 0, + the R-1-class FOV/occlusion
  check in the commit message) and marks the row LANDED; (2) the spec owner resolves the
  procedure contradiction for the remaining 12 rows — the workable form is "the owning WP
  pastes the command to T5 in the commit message; T5 appends within the same window".

---

## 6. CB-1 — scene09 pilot

### 6.1 Verified

- **Diff** `[static]`: one file; S09-A appends the three views **after** `park_vista` with
  literal tuples equal to spec §10.5's table; no `sc.grid_views` change; no preset key touched;
  the first 14 `views` entries keep identity and order (pure append ⇒ order-prefix rule holds).
  S09-C rewrites `land_posts` to x −0.80 · z 0 · ys ±5.6/±12.0, prim names kept `LandPost_*`.
- **Derivations** `[recomputed]`: raking 130.815°/−5.502°/14.6017 m; grazing eye = 0.55 −
  (−0.680) = **1.23 m** over the 4th tread (x 1.02…1.36); landing_return 90.0°/−14.65°/9.096 m;
  x −0.80 = `lawns[*].x1`; ±12.0 = `lawns[*].y0/y1`; stair-head setback 0.80 − r 0.24 = **0.56 m**;
  nearest mooring pile √(0.4² + 1.5²) = **1.552 m**; worst preset bearing atan(5.6/9.2) =
  **31.3°** > 30° ⇒ 0 posts in any preset FOV. Waterline −5.190 confirmed (§3).
- **Gate** `[reran]`: 17 cuts — FAIL 0 · WARN 2 · INFO 3 · PASS 12, WARN = grazing
  [WHITE 64.9 %] + waterline [UNCHANGED 0.30 LSB]; control arm 14 cuts — FAIL 0, 11×
  [UNCHANGED] ⇒ the old-HEAD baseline is valid and the main-arm delta is CB-1-only.
  Round stamp carries the §7.2 judge channel verbatim (pt · PT_FAST 1 · LOOK_V1 1 · DETAIL 2/0).
  Tree invariants clean after CB-1: R-4/R-6 33/33, R-5 residual-LOOK_V1 0 `[reran]`.
- **The three cuts viewed** `[viewed]`: raking — full 36-riser stack against water, waterline
  cutting the flight; landings legible **as horizontal nosing-line jumps, not vertical breaks**
  (S5's judge-call blocker is accurate, the gate sentence's axis is wrong for a −5.5° raking
  camera). grazing — the flight collapses into one near-white plane, zero risers visible: the
  concealment case, proven; the 64.9 % WHITE **is the diagnosis** (same root cause as
  ghat_walk's carried WHITE; no W3 WP owns scene09 stone tone — real gap, needs an owner before
  통람 v3). landing_return — 1.20 m landing vs 0.34 m treads and the terrace junction read
  clearly; it also shows there is **no cheek/flank** because the embankment extends the same
  step table (S5's "spec row unachievable as written" blocker is correct).
- **placement_lint on scene09** `[reran]`: 9 LINT-8 + 1 LINT-4b ERRORs, all pre-existing
  (GKit stains / planter Yellow_Pine); no finding names a `LandPost_*` or either new-view code
  path. LINT-7's 4 substantive rows are the benches S5 deliberately left for CB-10 (J-5).

### 6.2 Findings

- **CB1-F1 · dangling commit hash in committed content.** The commit message and
  `scene09:977` cite T3 as commit `e0fdee4`. That object exists but is **not reachable from
  HEAD** — it is T3's pre-amend commit from the shared-index incident; the landed T3 commit is
  `f20f5ff`. After a GC the citation dereferences to nothing. Fix the comment at S5's next
  scene09 touch (commit messages are immutable; the code comment is not).
- **CB1-F2 · GT-10 landing record missing** — see T5-F1 (procedure contradiction, not S5
  negligence).
- Carried (S5 already flagged, I confirm): `look_check/INDEX.md` has no row for
  `260731_w3_cb1` and the file is unowned in §4 — an owner must be named; and whether
  260731_w3_cb1 becomes scene09's baseline-of-record needs a ruling before GATE-2.

---

## 7. WINDOW 0 exit call and carried items

**Exit criteria of §5.1 are met**: (i) T1 ran on the untouched tree, published the full baseline
(809 rows), and fixed nothing — the working tree contained only the concurrent CB-1 scene09
edit, which T1's baseline note proves moves no finding (LandPost matches no prop class;
re-verified). (ii) T3 published confirm/refute per number and the verdicts survive adversarial
recomputation. T2 landed mid-window from its external lane (`73cfd37` + `c9e6ef3`, 12 archetype
panels) — **not verified by this gate** (outside its brief); its own §6.2 obligation
(per-file licence verification) is owed to whoever gates GATE-3/CB-11, which are the only
things §5.1 conditions on T2.

**Carried items, in priority order**:

1. **T5**: append GT-10's landing record (close the row); spec owner resolves who appends for
   the other 12 (T5-F1).
2. **Spec corrections owed by the spec owner** (all with verified evidence in this report):
   GT-6 affected set "05·19·13" → **05·19** and scene05 site count 10 → **12** (§3); §10.5
   S06-A item 1 fallback clause is mathematically unsatisfiable — strike it; §8 preamble "two
   rows" → three (RT-I:211); §6.2 T4's traverse-trap sentence is false on the procured mirror
   (T4-F1); LINT-10 two-tier severity should be ratified (T1-F2).
3. **K4(d)** must fix NF-1 (`build_helix_ramp` top-face placement) in the same commit as the
   arc/helix convention, or item 3's 20–30 mm nib is authored ~16 mm high (T3 §7, verified).
4. **K1** must state GT-9's applied scale factor and resulting height in the landing record —
   native `Grass_Short_C` is 0.125 m > the 0.12 class-A ceiling (T5 W1, verified).
5. **scene09 WHITE / stone tone needs an owner** before 통람 v3 judges scene09, and the CB-1
   gate sentence about "landings as breaks in the rhythm" needs re-wording to the horizontal
   axis or a landing-specific cut (S5 blockers, confirmed by eye).
6. **Process**: the shared-index hazard is real (e0fdee4 is its fossil). Every W3 agent stages
   and commits with explicit pathspecs (`git add <own paths>; git commit -- <own paths>`).
7. Minor: T1 legend fix (T1-F1); S5 fixes the `e0fdee4` citation at next touch (CB1-F1);
   `INDEX.md` row owner (6.2).

No finding above blocks WINDOW 1 from opening.
