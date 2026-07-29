# Red team — W2-D edit round verification (pre-GPU)

Date 2026-07-30 · branch `feat/realism-v1` · HEAD `0f4fced` (working tree = W2-D edits, uncommitted)
Mission: re-execute the CPU proofs, sample the edits against the §5/§12 matrix, verify the five
builder reports, and rule CONFIRMED / PARTIAL / REFUTED per builder. A REFUTED blocks the render
round. No GPU, no render, no Isaac, no SMOKE, no commit. Files touched by this mission: **this
report only.**

Verified reports:
`w2d_edit_g1.md` (scenes 01–06) · `w2d_edit_g2.md` (07–12) · `w2d_edit_g3.md` (14, 16–21) ·
`w2d_edit_gb.md` (batch1 ×10) · `w2d_translation.md` (6 shared files).

---

## 0. Verdicts

| builder | verdict | one-line basis |
|---|---|---|
| **g1** (01–06) | **CONFIRMED** | All six wired per pilot pattern; prim counts reproduce (46/46/21/7/48/32 default arm); all 5 could-not-land deviations re-derived numerically and each one is arithmetically right; blockers real. |
| **g2** (07–12) | **CONFIRMED** | 280 geometry prims exact; ON/OFF deltas re-measured +53 (08) and +129 (12) exactly; "560 scatter" reconciles as 530 plan + 30 direct rings (code verified); deviations V1–V5 and kit defects R1/R3/R4 verified in code. |
| **g3** (14,16–21) | **CONFIRMED** | All three spec-number corrections independently re-derived (trench −2.59; scene18 edge s=−0.245 in code; scene19 origin 11.6 proven from `build_views` mirror math); near-white parapet retired (only near-white constant removed in the whole diff, none added); zero `gt_changes`. |
| **gb** (batch1 ×10) | **CONFIRMED** | Explicit-zero infra overrides (F2 handled), W1→W2 manhole moves reproduce 56.1 % arithmetic, C4 position-error defect implemented, D1/D3 two-plan pattern sound; F1–F4 all confirmed, F3 re-measured live (see §5.3). |
| **translation** | **CONFIRMED** | AST-equality re-proven independently on all six files vs HEAD; string-literal multisets identical (0 changed); 0 Korean comments/docstrings remain (was 1,339/173 — exact claimed totals); 747 Korean literals preserved; `ground_kit.py` stdout byte-identical vs HEAD snapshot; the "spurious R-6 31/33" race claim resolved — settled tree now gives 33/33. |

**No REFUTED. The render round is not blocked by this verification.** Riders in §7.

---

## 1. Mandated re-executions `[실측]`

| check | result |
|---|---|
| `python3 ground_kit.py` | exit **0** · 하드게이트 **33/33** · fixture prims 1,333 · apply round-trip 33/33 · unsubstituted material refs 0 · recessed-burial 0 |
| `python3 scripts/geom_invariance_check.py` (full tree, settled) | **R-5 PASS** (LOOK_V1 residuals 0/40 files) · **R-4 33/33 PASS** · **R-6 33/33 PASS**, run twice; second run exit code 0 |
| translator race claim | The live 31/33 R-6 FAIL reported mid-round does **not** reproduce on the settled tree — it was the subprocess-arm race the translator diagnosed, now moot. |
| sceneD4 | **untouched**: not in `git diff --name-only`, file mtime Jul 27 (pre-round), and the runtime harness records **zero** `plan_ground` calls from sceneD4 (M8 deferral held). |
| file-touch discipline | Modified: exactly 29 scene files (6+6+7+10) + the translator's 6 files. Untracked: the 5 builder reports. **No brief, no spec, no fixture-bearing doc, no scene13/15/N5/D4 edit.** No new commits by builders (HEAD movement is supervisor/other work items: `7301976` translation-2nd-pass, `0f4fced` look_check cleanup — neither touches the six translated files, verified by empty `git diff 7301976 0f4fced` on them). |

### 1.1 Beyond the fixture — hard gates on the *real* scene arguments

`python3 ground_kit.py` validates the `SCENE_PLANS` **fixtures**, not what scenes pass (g1 D-6).
To close that gap this mission ran all 33 scenes' `main()` under the same fake-USD stub harness
`geom_invariance_check` uses, with `gk.plan_ground` / `gk.apply_ground` wrapped by a recorder
(scratchpad `plan_recorder.py`). Result `[실측]`:

* **37 real `plan_ground` calls from 32 scenes (D4: 0), every one passes B6–B12** — `plan_ground`
  raises on violation, so assembly success is gate proof on the wired coordinates.
* Toggle arms assembled clean: `cue_tactile=True` for 01/02/08/11/16; hazard-off twins for
  01/08/N1/D2; `NEGOBS_GKIT=0` for 08/12 with ON/OFF prim deltas **+53 and +129 exactly** equal to
  plan counts (g2's numbers).
* Kit prims per scene reproduce every builder table (g1 46/46/21/7/48/32 · g2 11/53/35/17/35/129
  · g3 50/52/54/51/41/49/47 · gb 45/46/42/54/43/3/48/22+24/24/34+32).
* `gt_changes` ledger: **exactly one entry in the whole tree** — scene13 ramp_curb 0.12 (M4
  approved, label owner W4). The W2-D batch itself creates **zero unlabelled drops**.

---

## 2. Sampled matrix diff (≥10 scenes, all four groups)

Machine-checked all 32 wired scenes (§1.1); deep-diffed the following 14 against the §5 rows.
드 = documented deviation in the builder's own report, verified here.

| scene | grp | matrix row conformance `[실측/계산]` |
|---|---|---|
| 01 | g1 | manhole (−3.8,−2.4) exact; gullies (−0.95,±5.10) exact; trench dropped 드(§2.1 — see §3.1); charcoal re-phase not applied 드(§2.2 — arithmetic verified); tactile band −0.90…−0.30 full width in ON arm, statutory. |
| 02 | g1 | manhole (−1.20,0.35) exact; stair-head gullies (−0.95,±3.6); trench dropped 드; gutter_L off 드(§2.8 — kerb at x=7.85 is outside every window and outside the region); underground branch untouched 드(carried W4). |
| 03 | g1 | forced `natural=True` + **all infra keys explicitly zeroed** (the F2 dict-merge trap handled); kit kinds = patch/stain/wear only; urban infra **0**. |
| 04 | g1 | region clipped at −2.40 = GT-E5 40×0.06 for gravel exposure — re-derived; wear/litter carry d2; +3 prims are direct `build_edge_break` calls (constant-x seam the composer cannot emit). |
| 05 | g1 | origin (−1.5,0,0) — §2.3 omission confirmed (§5.1 manhole −3.5 = d2 **eye**); moved manhole (−3.90,−0.40) → X=2.60 @d5 = W2 window, 21.6 % width (M9-ⓑ pattern); gully (−10.0,0) = spec sump −8.5 in forward-s; joint region cut −3.70 = D-1 workaround, tick set equals what an origin-aware guard keeps. |
| 06 | g1 | origin (3.5,−13,5) axis −y; joints via `step_y=9` → y −9/0/+9 exactly §5.3; coating band via wear_lane 드; membrane builder can't express a 2 m band 드; tactile hold per §12.4 ✔. 4 deck gullies — see rider §7.3. |
| 07 | g2 | 3-band split = region(±1.5)+edge_break pair+wear 1.2; scatter 8.04/m² vs spec 8; edge_litter dropped 드(V1 = kit defect R2). Urban infra 0 ✔. |
| 09 | g2 | joints re-tiered 1.8 (=3×0.6 cell, U2) 드(V2); silt via scene's own waterline banding widened 1.5→3.0 steps 드(V3 — §5.7's own row); patches one per W1 window (−1.3/−3.7/−8.7). Urban infra 0 ✔. |
| 11 | g2 | origin (15,0,5.5); deck gullies zeroed 드(V4 soffit-pierce, `under_grating` view); tactile skew_deg=15.0 implemented = §12.4 assigned defect ✔. |
| 12 | g2 | two plans; 119 gaps+1 butt on lifted z (recess-as-tone workaround for kit defect R1, docstring states removal condition); no road marking on natural deck 드(V5); scene12 ruling held (deck fixtures ok, road infra 0). |
| 14 | g3 | trench present at **−2.59** (corrected C-1′, near lip −2.40 → drow 16.05 ✔) — legal here because tactile is OFF (illusion identity) so the E-band single-line budget is free; manholes (−8.7,1.2) exact + (−4.5,−1.5); gullies (−0.95,±2.6) = width/2−0.40 exact. |
| 16 | g3 | entrance band (−6.0…−5.4, full walk width) unconditional = cue+/label− filler; manhole (−3.9,−0.8) exact; scene's hazard-tactile stays behind `cue_tactile` ✔. |
| 19 | g3 | origin **11.6** proven: `build_views` mirrors `sc.grid_views` about xref 5.8 → grid origin 2×5.8, eye_d2 at 13.6; edge s=7.6 = roof west lip x=4.0 (`up["x0"]`); parapet (0.90,0.90,0.87)→(0.40,0.40,0.385) — **the only near-white constant removed in the entire diff; zero added** ✔; drains (10.5,−0.6)/(6.0,−7.5) exact. |
| N1/C2/C4/D2/D3 | gb | N1: manholes → W2 window (56.1 % arithmetic reproduces), kit joints disabled to avoid double grid (D6 class), band 0.60 continuous; C2: 3 joints only + 2 direct bands clipped x≤0 (slope 0.4706 re-checked), **all infra spelled to 0**; C4: tactile at 1.00 m setback = assigned position-error defect; D2: two longitudinal legs only (F1 deferral held), 4-box GT-V split + `Slab_Fill` in SKIN_EXCLUDE; D3: two plans, joint ownership moved to kit at same period 2.5/0.04, U-gutter identity untouched, urban infra 0 ✔. |

**B6/B7/B8 recompute highlights `[계산 — gk 함수로 재유도]`**

| claim | re-derivation | verdict |
|---|---|---|
| C-1′ trench x=−2.55 is 0.04 short (g1/g3) | `trench_frame_w=0.040` is in `GROUND_DIMENSIONS`; center −2.55 → near lip −2.36 → `drow(−2.36,d10)=15.70 < 16`; −2.59 → −2.40 → **16.05** ✔ | **CONFIRMED** — spec §5.0 C-1′ ignores its own kit's frame lip |
| trench ∧ tactile mutually exclusive at d10 (g1) | tactile band boundaries at d10 are Δ 1.6/5.0 rows (GT-E2-x registered); trench at −2.59 is a second singular cross line in the same E band → B7 "2본 이상". Verified: 01 plan passes with `cue_tactile=False`, raises with `True`+trench | **CONFIRMED** |
| scene05 charcoal bands B7-blind (g1) | band world x=−2.00 = s−0.5 (origin −1.5) → `drow(−0.5,d10)=2.68` rows from edge row — deep inside GRAZE fusion; scene-owned geometry so no gate sees it | **CONFIRMED** — §7.3-class round judgement needed (§7.2 below) |
| N1 manhole spec coord defective (gb) | (−1.0,0.4) at d2 → X=1.0 → 1,077 px = **56.1 %** frame width; W1 min 28.1 % even at far end | **CONFIRMED** — move to W2 matches pilot ruling M9-ⓑ |
| C4 FP window mismatch (gb F4) | `EXPECTED_FP` rows computed at setback 0.30: d5 (348,371), d10 (297,304); actual band at 1.00: d5 (348,**374**), d10 (297,**308**) — band rows overrun the registered window | **CONFIRMED** — GRAZE adjudicator needs per-scene setbacks or a waiver |
| B8 / GT-V | D2 marking legs (−3→0, y=±1.05) clear the void; 4-box slab split intact; kit-wide AABB×void intersections 0 (self-check assertion re-run) | **CONFIRMED** |

---

## 3. Rulings in force — compliance

| ruling | finding |
|---|---|
| sceneD4 deferred (M8) | **Held.** No diff, no plans, tactile register entry exists but dormant. |
| natural scenes 03/04/07/09/12/D3 (+10) no-urban-infra | **Held 7/7.** Recorder shows urban-infra element count **0** on every natural plan; 03 forces `natural=True`+zeroed infra so the rule is now code-enforced on the real call; scene12 kit adds only plank gaps/stains/silt film (deck fixtures ruling honoured); scene09 park lights are props, untouched; D3 keeps U-gutter identity (no section change). |
| tactile per §12.4 only, dot Ø25 mm | **Held.** Code `TACTILE_SITES` == §12.4 register incl. per-scene non-conformance defects (01/C1 fade, 11 skew 15°, 08/13 partial loss, C4 position 1.0 m, 16 occupied-spot-left-empty); B11 passes everywhere; 06 hold honoured (no site, B11 would raise); Ø25 mm lives in the texture generator (c4e3044), untouched this round. |
| recess-as-tone via `surface_top_z` | **Held**, incl. the deck-plank scene-side z-lift workaround (R1) with its removal condition documented. |
| manhole flush / GT δ | `gt_delta_max` ≤ 0.02 for all non-exception elements (apply-time assertion re-run); weeds/gravel ride the GT-E5 ramp. |
| no seasonal assets | **Held at diff level**: added snow/leaf references exist only in sceneC1 (snow identity — SnowTrace wear/footprints = §5.1 C1 row) and sceneC2 ordering comments (leaf identity). **Open at runtime level**: kit defect D-5 (§5.1 below) makes profile "gravel" scatter render as VEG_DEBRIS fallen leaves in 04/07/10. |
| no near-white | **Held**: zero constants ≥(0.85)³ added across all 29 scene diffs; one removed (scene19 parapet). B9 albedo caps pass on all real plans (std ≤0.30, tactile ≤0.55). |

---

## 4. Translation re-proof `[실측 — 독립 재실행]`

Method: AST equality with docstrings stripped (comments never reach the AST), SHA-256 over
`ast.dump`; string-literal **multiset** comparison excluding docstrings; Hangul token census.
Baseline = HEAD `0f4fced` (== translator's claimed `7301976` for these files — diff between the
two commits on the six files is empty).

| file | AST eq | literal multiset | KR cmt/doc now | KR cmt/doc at HEAD | KR literals |
|---|---|---|---|---|---|
| scene_common.py | OK | OK | 0/0 | 669/48 | 62 |
| ground_kit.py | OK | OK | 0/0 | 222/55 | 353 |
| scripts/regression_check.py | OK | OK | 0/0 | 216/17 | 96 |
| facade_kit.py | OK | OK | 0/0 | 90/22 | 1 |
| infra_kit.py | OK | OK | 0/0 | 73/22 | 194 |
| stair_kit.py | OK | OK | 0/0 | 69/9 | 41 |

Totals: 1,339 comments + 173 docstrings translated (matches the claim to the digit), **747**
Korean runtime literals preserved verbatim (exact claim), **0 literals changed anywhere**.
`python3 ground_kit.py` stdout byte-identical between working tree and a `git archive HEAD`
snapshot run. Verdict: **CONFIRMED**; safe to commit independently of the scene work.

---

## 5. Builder-claimed kit defects — independent verification

All claimed in files the builders do not own; none is builder error. Verified in `ground_kit.py`
at the exact mechanisms claimed:

| id (claimant) | mechanism verified | status |
|---|---|---|
| D-1/R4 (g1,g2,gb) `_edge_guard_ticks` frame mixing | `xx` is world-x (`origin_x + i·step`), `se` is forward-s (proof: `_trim_region` converts `se` via `view.fwd`); `drow(xx−se,…)` mixes frames on any origin-shifted scene | **CONFIRMED** — must be fixed before wiring 11(joints)/19/D1/D4 grids; scene05 workaround verified equivalent |
| D-5 (g1) scatter kind ignored | `apply_ground` forwards only `cover`/`count`/`edge_bias` to the callback; profile `kind="gravel"` never leaves the dict; `scatter_debris` defaults `pool=VEG_DEBRIS` = 5 fall/maple/oak leaf assets | **CONFIRMED** — 04/07 tolerable by identity exception, **scene10 violates the no-seasonal rule at render time**; fix before the P11/P12/P18 GPU cuts or accept and log |
| D-6 (g1) scene03 fixture urban infra | `SCENE_PLANS["scene03"]` = plain `levee_paved` (infra manhole/gully/gutter present) with no natural forcing | **CONFIRMED** — and it generalises, see §6.1 |
| F1 (gb) `_ik_marking` yaw | AABB built by `_box_aabb(x0+L/2 …)` laying L along +X regardless of `yaw_deg`, while `line=` classifies by yaw; `_obb_aabb` exists but is not used here | **CONFIRMED** — D2 west leg deferral justified |
| F2 (gb) `overrides` dict-merge | `dict.update(v)` with empty dict keeps all profile infra; zeros must be spelled | **CONFIRMED** — C2/03 spell zeros correctly |
| F3 (gb) `_seed_key` prefix sensitivity | **Re-measured live**: sceneD3 planned 34/32 (Cover/Road), built **36/30** — totals equal only by luck, per-plan counts diverge because the seed key under `GKit/<Tag>` is `<Tag>/…` at apply vs bare path at plan | **CONFIRMED + quantified** — note B10 gates the *planned* count; a crack-heavy plan near its cap can exceed it at build time unseen |
| F4 (gb) C4 EXPECTED_FP setback | see §2 table | **CONFIRMED** |
| R1 (g2) `build_deck_planks` burial | gap strips built at top z−0.020 under a solid slab (`kit.B(..., z−0.030 center, 0.020 thick)`) — the exact defect class `surface_top_z` fixed for joints, not applied to planks | **CONFIRMED** — scene10/12 z-lift workarounds verified; must be unwound when the builder is fixed |
| R2/R3 (g2) edge_litter width + shared decal top z | wear_lane, edge_litter, stain_field all top out at `z + stain_proud` — overlapping footprints exactly coplanar; `_compose_ops` overrides litter width with the region span | **CONFIRMED (geometric)** — visibility unproven; check scene07/10 d2/d5 crops in the GPU round as g2 asks |
| B4 unreachable (g2) | long strips are frame-culled at `Xm` = forward-span **midpoint** (clamped 0.05), so corridor-length strips evaluate `cam_halfwidth` at a nonsense distance | **CONFIRMED (mechanism)** — soft gate only |

---

## 6. New findings (not in any builder report)

### 6.1 Fixture drift is systemic, not a scene03 one-off
`SCENE_PLANS` disagrees with the real wiring beyond D-6: **sceneN1** fixture still carries the
defective spec manhole `(−1.0, 0.4)` (56.1 % @d2) that the scene itself moved to W2;
**scene08** fixture declares a kit-emitted `opening_ring` tactile while the scene keeps the ring
on its own path; **scene19** fixture origin `(9.04,0,0)`+edge s=0 vs the real grid origin 11.6 /
lip s=7.6 (fixture gates run against a phantom edge 5 m from the real lip). The fixtures still
*pass* their own gates, so `python3 ground_kit.py` stays green while drifting from reality.
**Recommendation**: regenerate `SCENE_PLANS` from the scenes' own `ground_plan()`/`ground_plans()`
callables (gb's pattern already closes this for 10 scenes) or demote the fixture check in favour
of a recorder harness run.

### 6.2 Default-arm tactile census vs §12.6 calibration
As wired, the **default** arms render tactile in: C1, C4, D4 (hazard scenes) + 16/N1/N2/N4/N5
(no-drop sites, unconditional). The six "ON 신설" hazard scenes 01/02/08/11/13(보도)/16(계단부)
keep their v5.2 `cue_tactile=False` default. So default-arm renders give
`P(점형|낙차) ≈ 3/28 = 0.11`, far from §12.6's target 0.30–0.45 which assumed `K_h = 9`.
This is not a builder error (§12.4 "ON" = registered site + intact toggle; no builder was told to
flip defaults), but it means **M10's variant-render plan is load-bearing, not optional** — without
cue_tactile-ON cuts for the 9 scenes, the conditional-probability design silently degrades.
Supervisor should either bless default-ON for the six scenes or size the M10 render budget now.

### 6.3 scene06 deck gullies vs the V4 precedent
g2 zeroed scene11's deck gullies because the gully body (0.640 m) pierces a 0.400 m deck soffit in
view of `under_grating`. scene06 (g1) keeps **4** deck gullies on its own deck at z=5.0. If
scene06 has any under-deck view or visible soffit, the same defect appears there. No CPU gate
models soffits — flag for the GPU round eyes pass.

### 6.4 Second-plan prefix naming is F3-fragile
Live prefixes: `GKit/Cover`+`GKit/Road` (D3), `GKitPlanks` (12), `GKitDeck` (10),
`GKit_pit` style (08). Only paths containing the literal `/GKit/` get stable seed keys; the others
survive today because their plans contain no RNG builders (planks/joints are deterministic).
Any future crack/stain added to a `GKitPlanks`-style plan resurrects F3. One naming convention
(`{ROOT}/GKit/<Tag>` — and fixing `_seed_key` to strip through `<Tag>`) closes it.

### 6.5 Report arithmetic spot-checks that came back clean
g2's "560 scatter" = 530 via plans + 30 via two direct `sc.scatter_debris` rings in scene10
(code-verified); g2 scene07 field 270 + 30 edge = applied 300 (recorder-verified); gb C2 "5 prims"
= 3 plan joints + 2 direct band builders; g1 scene04 "7+3" = 7 plan + 3 direct edge_break.
No builder number failed reproduction anywhere in the sample.

---

## 7. Riders for the GPU round (carried + new)

1. **σ_LF ≥ 5.0 WARN gate restore** (W2-C GO item 4 / §7.5 A1): T1 exists; the ground-only
   informative-only scoping ends with the next render round — all five reports agree.
2. **scene05 charcoal bands + pre-existing full-width transverse lines** (g1 blocker 5, verified
   §2): scene-owned lines inside the d10 E band need a round judgement — GRAZE will fuse them.
3. **R3 coplanar decals**: check scene07/scene10 d2/d5 crops for shimmer before dismissing.
4. **D-5 scatter kind**: decide before rendering 04/07/10, or the "gravel" rows ship as leaves
   (scene10 = seasonal-rule violation).
5. **C4 GRAZE adjudication**: extend the FP window to the actual 1.00 m setback rows
   (d5 →374, d10 →308) or waive.
6. **Supervisor items**: C-1′ trench fate on rows 01/02/14 (keep 14-style trench only where
   tactile is OFF?); default-arm tactile policy (§6.2); N5 pad+band vs N1–N4 band-only
   inconsistency (gb §4.2); `_edge_guard_ticks` fix before 11/19/D1/D4 grids (D-1).
7. **Commit hygiene** (translator blocker 4, still valid): the six translated files are provably
   comment-only vs HEAD and can be committed independently; the 29 scene files belong to the four
   scene builders — do not fold them into one commit blind.

---

## 8. Reproduce

```bash
cd /home/vislab/Desktop/work_sy/Practice_NegObs
python3 ground_kit.py                      # exit 0, 33/33
python3 scripts/geom_invariance_check.py   # R-5/R-4/R-6 all PASS on the settled tree
# real-arg gate proof + toggle arms (red-team harness, scratchpad):
#   plan_recorder.py / plan_recorder2.py — fake-USD stubs from geom_invariance_check,
#   gk.plan_ground wrapped; any B6-B12 violation raises inside the scene's own main().
# AST proof: ast_proof.py <rev> — dump-hash minus docstrings + literal multiset + Hangul census.
```
