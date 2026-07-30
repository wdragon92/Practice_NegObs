# W3 · S07-EXEC — scene07 temple stone stair rebuild (CB-S3-07)

> **Wave** W3 · **Track** S3 · **Batch** CB-S3-07 · **Date** 2026-07-31 · **Branch** `feat/realism-v1`
> **Scope** `scenes/main/scene07_temple_stone_path.py` only, plus `Docs/audit_v4/gt_changes_w3.md`
> rows and this report. No other scene file was touched. S3-1 (sceneC2 hygiene) stayed deferred
> per the §8.R scope guard. No humans, no vehicles, anywhere.
>
> **Authority** `Docs/briefs/s3_scene07_10_rebuild_spec_v1.md` incl. §8.R ·
> `Docs/surveys/s3_research_numbers_v1.md` · `Docs/briefs/w3_execution_spec_v1.md` §6.1/§7/§12 ·
> `Docs/audit_v4/gt_changes_w3.md` §0/§4.
>
> **Fidelity target** G7 = `Docs/reference_photos/Generated Image - Scene07.jpg`, viewed first.

---

## 0. Result in one paragraph

scene07's stair is no longer a 디딤돌 stepping-stone path on a 19° slope. It is a **28-course
자연석 계단** of 89 bedded slabs whose **open-slope fraction is 0.000 %** by construction — the
34.0 % of bare corridor that was the scene's headline archetype failure is gone, and it is gone
through a back-overlap term rather than through a budget. Every §6.5 assertion the spec asked for
is implemented, measured and printed. The GATE-1 pilot **P07** rendered 14 cuts and returns
**2 FAILs out of 14: one FRAME (declared in advance by §6.4) and one GRAZE (adjudicated by eyes)**.
**DARK 0 · BLOWN 0 · OCCL ≤ 0.7 %**, and `near_ground_stats` on the judged h0.3 band is flat
against the baseline. Round **`260731_w3_s07` is stamped as scene07's new baseline-of-record**;
the comparison baseline for this batch was **`260731_w3_cb2`**, named per ledger §6-W4.

Three things did not go to plan and are stated up front, because each is a finding rather than a
tuning matter: the **urban asset MDL chain is broken** and rendered every kerb boulder flat red
until it was worked around; the **two framing trunks are not shipped** because an A/B proves they
are the entire DARK/OCCL delta; and `TEX["moss"]`'s raw scan had to be confined to one surface
class. §5 covers all three.

---

## 1. Commit sequence — spec §6.2, one commit each, §6.1 floor on every one

| # | Commit | What landed | Floor |
|---|---|---|---|
| S3-2 | `49732a5` | 24-gon chord polish, **near-field masks only** (3 of 9) | ✔ |
| — | `3c84961` | **GT-14…GT-17 declared** in the ledger before any of them landed (§0-1) | — |
| S3-3 | `bbf085d` | Knob deletion (24 prims) + jitter caps A6/A7 · GT-16 | ✔ |
| S3-4 | `cd2745b` | **Stair archetype rebuild — the 28-course table** · GT-14 | ✔ |
| S3-5 | `ee4af00` | Kerb 야면석 + fern margins + framing trunks + `PLACEMENT` block · GT-15 | ✔ |
| S3-6 | `120c353` | Season re-bind to summer + zone-driven moss · GT-17 | ✔ |
| S3-7 | `97e46fb` | Crest roof cluster + wooden pole (no GT) | ✔ |
| pilot-1 | `5e134f1` | 5 defects the first pilot round exposed (§5) | ✔ |
| pilot-2 | `c3cebc3` | Framing-trunk decision + albedo lift (§5.2) | ✔ |
| — | `c09fa47` | GT-14…17 **landing records** filled, status `LANDED` | — |

The §6.1 floor — `py_compile` · `NEGOBS_SMOKE=1` · `geom_invariance_check` · `placement_lint` —
ran on every one. Two notes on how it was run:

- **`geom_invariance_check` was run with `--scenes scene07`.** The unscoped 33-scene run was green
  at the start of this task and then began failing on `scene10: KeyError: 'algae'` — a concurrent
  lane's in-flight edit to a file this lane may not touch. Scoping is the only honest option;
  scene07 returns **R-4 1/1 · R-6 1/1 PASS** on every commit.
- **`placement_lint` deltas were measured A/B**, not asserted: the committed file was swapped in,
  the linter re-run, and the JSON finding sets diffed. Net over the whole batch: **−1 LINT-10 WARN**
  (adjudicated, §2.2), **−1 LINT-7 WARN** and **−1 PLACEMENT WARN** (both cleared by the new
  declaration block), **0 findings added**, `LINT-4b` unchanged at the pre-existing 3.

---

## 2. What was built

### 2.1 S3-4 — the course table (GT-14)

Frozen and re-confirmed, not re-baselined: `STAIR_RUN 12.20` · `STAIR_DROP 4.20` ·
`SIDE_DROP 1.80` · `path_z()` · the junction at `x = 12.2 / z = −4.2`.

| Quantity | Before | After | Authority |
|---|---|---|---|
| Step primitive | 1 rectangular box per step, 24 total | **28 courses × 2–4 slabs = 89** | §1.A.1-1, §8.R OQ-7 |
| **Open-slope fraction** | **34.0 %** (gaps 0.050–0.276 m) | **0.000 %**, max course gap **−0.0936 m** | §1.B-1 A2 |
| Interlock | n/a | **0.0602–0.1791 m** | 표준시방서 0400-3.2 ㄷ ≥ 50 mm `[law]` |
| Visible within-course joint | n/a | **≤ 0.0482 m**, dry-laid, no pointing | §1.A.1-1 · 0400-1.3 ㄹ 건식쌓기 `[law]` |
| Rise | 0.111–0.232, mean 0.174 | **0.1270–0.1745, mean 0.1489, spread 0.0475** | declared band 0.120–0.180 |
| Rise construction | uniform draw | **dressed σ 10 mm + correlated settlement ±20 mm / 8–12 courses** | research §B4 |
| Tread | 0.270–0.384 | **0.43571** uniform | §4.1-1 |
| Slab thickness | 0.129–0.240 | **0.250** | KFS-TRAIL 13-2 가 300×300×250 `[law]` |
| Entry step | +0.002 | **+0.1456** (≈ one rise) | §1.B-1 A11 |
| Exit step | +0.201 | **+0.0300, labelled UP-STEP** | GT-14 · 조경설계기준 21.5(6) `[law]` |
| Course lateral offset | ±0.35 | **0** | A6 |
| Per-slab yaw / roll | ±4.0° / ±2.5° | **±3.0° / ±2.5°** | J-14 · research §B4 |

**The two rows that carry the whole thing.**

1. **The back edge is not jittered.** Only the front edge is, at `U(−0.06, +0.06)`. That single
   asymmetry produces both required properties at once: neighbouring slabs in a course differ by up
   to 0.12 m at the **nosing** (G7's ragged front, the real negative-obstacle cue), while the
   realised interlock is `0.12 + U(−0.06, +0.06) = 0.06…0.18 m` and therefore always above the
   50 mm heritage floor. The spec's `ov = 0.12` and its ≥50 mm interlock are only simultaneously
   satisfiable this way — with the back edge jittered too, the minimum interlock is 0.
2. **The flight runs the whole frozen run, `x 0.00 → 12.20`.** The old flight stopped at 12.05, and
   that 0.15 m shortfall plus `proud` **is** the +0.201 m orphan exit lip: `path_z(11.85) + 0.08 =
   −3.999` against a road at −4.200. Extending to the junction turns the lip into a 30 mm up-step
   and makes the entry step a real 0.146 m riser at the drop edge `x = 0`.

**One consequence that had to be declared rather than discovered.** A course tread is *level*
(조경설계기준 21.8(1) "지면과 수평이 되게"), so its back edge sits up to one rise below the 19.0°
plane. Leaving `PathCorridor` on that plane would push it up through the back of every tread.
`PathCorridor` and `SouthScarp` therefore drop **`z0 −0.33 m`** as the stair's bed. **`path_z()`
itself — the datum every other plate, all the dressing and `ground_z()` read — is untouched.**
The self-check asserts the result numerically: tread-back clearance over the bed **+0.0526 m**
(nothing pierces a tread) and 속채움 underside **−0.0976 m** below the bed top (nothing floats).

Also built: one **속채움 core slab per course** (0400-3.2 ㄹ) so a lateral joint bottoms out on
stone rather than on air; **54 고임돌·틈메우기돌 shims** at the riser feet (KFS 13-2 나); and the
statutory **돌깔기 aprons**, 1.00 m below and 0.60 m above (KFS p.72).

**2H + B is recorded, not gated.** 2(0.1489) + 0.4357 = **0.7336 m**, i.e. +24 mm on 〈표 13-1〉's
20° row (0.710) and outside KCS 34 50 10 3.2.8(3)'s 600–650. With `run` and `drop` frozen, `n`
alone fixes it (`20.39/n`), and `n = 28` is §8.R OQ-7's ruling. The arithmetic is printed in SMOKE
so nobody has to re-derive it: 600–650 would need n = 31–34 and a rise of 0.124–0.135.

### 2.2 S3-3 — knob deletion and jitter caps (GT-16)

24 `StoneKnob_*` prims deleted; the geom prim census moves **1090 → 1066, exactly −24**. The
seeded stream still draws the abolished `u`, so **the SMOKE rise / gap / entry / exit table is
bit-identical across the commit** — the walked surface provably did not move, which is what the
row claimed rather than promised. `LINT-10`'s `jitter=` token was adjudicated by the owning WP
(material tint, out of scope by §12-15) and renamed `tint_jit`; the WARN is gone.

### 2.3 S3-5 — kerb, ferns, framing trunks (GT-15)

30 야면석 boulders, 15 per flank, from `rock_03_broken` / `rock_02` / `rock_01`, **0.423–0.864 m**
across standing **0.203–0.306 m** proud, `z_mode='base'`, sink 0.035 (F2's no-sink-ring limit is
0.05). Discontinuous: max gap 3.65 / 3.63 m per flank.

**Two declared deviations from §4.1-2, both forced by this scene's own geometry.**

- The fixed line `y = ±1.55` is replaced by an **edge anchor** — outer edge at `y = ±1.68`, so
  `cy = ±(1.68 − across/2)`. At `±1.55` a 0.6–0.9 m boulder spans past the corridor edge `±1.70`:
  on the south that overhangs the unguarded 1.8 m drop, which H8 forbids softening, and on the
  north the `NorthWall` slope already occupies `y 1.70…2.15`. Measured result: nearest inner edge
  **0.816 m** against the §6.5 floor of 0.32, outer edge **1.680 ≤ 1.70**.
- §4.1-2's own two rows disagree — "mean 1.6 m centre-to-centre" against "12–16 per flank over
  12.2 m" (12.2/1.6 = 7.6). The **count** row is the visual one and is what G7 shows, so pitch is
  0.46 m in the occupied stretches with one ≥3 m and two ~1.1 m gaps.

Fern band: 26 `Shrub/Switchgrass.usd` stand-ins on both margins. Gap **G2** is real — 0 fern hits
across 291 manifest rows and 44 vegetation USDs — and this is recorded as a stand-in, not as a
fern; the fix is a CC0 fern atlas (R7-3). Framing trunks: **not shipped**, see §5.2.

`PLACEMENT` was added (§6.6). `kerb_lines` and `walk_edges` are **deliberately empty and that is a
finding**: declaring the corridor shoulders as walk edges was tried and measured, and it raises
**LINT-5 to 2 ERROR** by applying PE-8 (「도로의 구조·시설 기준에 관한 규칙」 제16조's 1.5 m
effective-width floor) to trees standing outside the corridor. 제16조 governs a 도로 보도; this
scene's south shoulder is a cliff edge and its north shoulder is the foot of a retaining wall.
The datum is declared absent rather than mis-declared — the same reasoning §4.0 F-1/F-3 used to
refuse PIRAN-15 and HOUSE-18 on a trail deck.

### 2.4 S3-6 — summer re-bind and moss zones (GT-17)

`leaf_ground`-bound plates and slopes **5 → 0**. Corridor lobes re-sited to `|cy| ≥ 1.20` and sized
to land inside one tread; corridor feather cover 0.06 → 0.035; `sct_debris_leaves_dry_*`
**0 placements** — the `SCENE_SCOPE` permission is not a recommendation (H10).

Achieved moss coverage against §4.1-3, all **IN** band, printed and not gated (research §B4b: no
Korean document quantifies tread moss, so the targets are `[ref]` + `[assumed]`):

| zone | target | achieved |
|---|---|---|
| walked centre band `\|y\| ≤ 0.35` | 0.00–0.10 | **0.037** |
| tread outer | 0.35–0.55 | **0.411** |
| riser faces | 0.60–0.85 | **0.848** |
| joints / 속채움 | 1.00 | **1.000** |
| boulder tops | 0.70–0.90 | **0.767** |

The riser zone is delivered by splitting each slab into a **cap** (the walked top) and a **body**
(whose front face is the riser). That is the only way to give a tread and its own riser different
moss **without authoring a proud strip along the nosing** — and a proud strip along the nosing is
exactly what H2 / RF-5 forbid on this scene. The body centre is displaced in the slab's own frame
and the offset is rotated by the same rotX→rotZ `_oriented_box` applies; a world-z displacement
would slide the body sideways by `h·sin(roll)` (up to 5.5 mm) and open a ledge under the cap.

The walked band is filled by **quota, not by probability**: at a 0.00–0.10 target over 28 courses
the Bernoulli variance *is* the whole budget (two hits already overshoot by area weighting).

### 2.5 S3-7 — crest cluster and pole (no GT)

Procedural, `gate_frame`-tier only. Gap **G1** confirmed: the only tile-roofed asset in 291 + 33
rows is a generic Western low-rise. Three roof masses, an upturned 처마 (+0.35 m over the last
0.80 m of run, taken out of the drop so the roof's x extent — and therefore its shadow — is
unchanged), a 22-box rafter dentil row on the near roof's +X eave only, one 단청-red wall fragment,
`tile_roof_01` 기와 maps, and one Ø110 mm × 4.5 m timber pole.

**The sightline is computed, not eyeballed**, as §4.1-4 demanded. From `gate_frame`'s eye
(7.00, −0.91) the crest sightline over the yard shoulder rises 0.13 m/m going −X, so it stands at
z 3.31 at cx −25.5 and z 4.42 at cx −34: flat-ground 0.85×/0.70× clones (ridge 4.42 / 3.64) would
be **behind the crest and invisible**. Each clone therefore gets a stepped 축대 terrace
(z0 1.20 / 2.70) and the clearances are asserted: **+2.86 / +2.31 / +1.92 m**.

H16 was obeyed: `gate_frame` is 1 of 14 cuts and none of the 5 preset cuts, and no stair fidelity
was traded for it.

---

## 3. GATE-1 pilot P07

**Round `260731_w3_s07`**, `look_check/scene07/260731_w3_s07`, stamped, `git_head c3cebc3`.
14 cuts = the **full preset prefix in `build_views()` order** (9 grid cuts, then `temple_walk` ·
`stone_rhythm` · `gate_frame` · `side_slope` · `grazing_edge`). `NEGOBS_VIEWS` was left **unset**
so nothing truncated the list — PT/DLSS accumulation carries frame history and a truncated list
changes the first cut (§4.4 X1). Channel identical to the frozen judge round: `pt` · `PT_FAST=1` ·
`LOOK_V1=1` · `DETAIL_SCALE=2` · `DETAIL_ROUGH_GAIN=0`. The whole segment ran inside
`flock -w 7200 /tmp/negobs_gpu.lock`. The round script was written to the scratchpad, **not** under
`scripts/rounds/`, per this task's lane law.

**Comparison baseline: `260731_w3_cb2`** (5 cuts, the CB-2-stamped baseline; `regr_260730_w2d_fix`
is retired). The other 9 cuts are `NEW-VIEW` against it and are reported against
`260730_w2d_fix` where a figure is quoted. **This round is stamped as scene07's new
baseline-of-record.**

### 3.1 Result — 14 cuts, FAIL 2 · PASS 1 · INFO 11 · WARN 0

`Docs/reports/regr_260731_w3_s07.json`.

| cut | verdict | reason |
|---|---|---|
| `preset_h0.9_d2` | **FAIL** | **FRAME** 51 % moved blocks — **the declared result** (§6.4) |
| `preset_h0.3_d2` | **FAIL** | **GRAZE** `[의심] 은닉`, 단차 85.4 → 40.9 — adjudicated below |
| `preset_h0.3_d10` | PASS | — |
| the other 11 | INFO | NEW-VIEW / CAPTURE |

**DARK 0 · BLOWN 0 · OCCL max 0.7 % new dark, largest connected blob 0.2 %.** These are the gates
§6.4 says still mean something, and none of them moved.

`near_ground_stats` on the judged h0.3 band, new vs baseline — **flat**:

| cut | σ_LF | edge % | w80 |
|---|---|---|---|
| `h0.3_d2` | 13.69 → **13.69** | 80.8 → **79.3** | 2.4 → **2.2** |
| `h0.3_d5` | 22.88 → **22.97** | 50.6 → **50.3** | 0.5 → **0.7** |
| `h0.3_d10` | 4.08 → **4.10** | 90.3 → **90.3** | 3.2 → **3.1** |

### 3.2 The GRAZE FAIL, adjudicated

`regression_check` cannot close this one itself — it says so: *"그 대역만 잘라서 육안 확인
(자동 확정 불가)"*. The band was cropped for both rounds:
`look_check/scene07/260731_w3_s07/crops/graze_band_h0.3_d2.png`.

**Verdict: declared consequence, not concealment.** Before, the shoulder was one high-contrast
line — gravel yard against a 34 %-bare corridor immediately past it. After, the same band carries
the statutory 돌깔기 apron and then articulated courses stepping down. The metric measures the
contrast of *one* line and that line was an artefact of the defect being removed. Three independent
facts say the drop is more readable, not less:

1. The shoulder step went **0.002 → 0.146 m**, i.e. **73× bigger**; a 2 mm step was not a step.
2. Total drop 4.200 and `SIDE_DROP` 1.800 are unchanged and asserted in SMOKE.
3. `OCCL` new-dark is 0.2 % on this cut — nothing was buried.

---

## 4. h0.3 eyes, side by side with G7

`look_check/scene07/260731_w3_s07/crops/h03_eyes_vs_G7.png` — before / after / target at equal
size. The h0.3 grid cuts do not see the stair by design (the drop vanishes below the sightline —
that is the scene's hazard), so the h0.3 **eyes** view of the stair is `stone_rhythm`, whose eye
sits at z 0.256 ≈ h0.3.

**What now matches G7**: courses of 2–4 slabs read as one rising surface with a ragged front; the
treads are level and deep and the rises low; nothing cantilevers over shadow; litter sits in the
joints and at the margins, never on the walk; a discontinuous boulder line flanks the flight;
dappled light on stone.

**What still does not, stated plainly**:

| gap | why | route |
|---|---|---|
| Moss reads pale and dry against G7's heavy green crust | the zone fractions are met, but the tint convention on `rock_face` cannot carry a crust | a real moss atlas / decal layer — procurement, not tuning |
| Slabs are rectangular in plan; G7's are riven and irregular | `_oriented_box` is a box | `rock_03_broken` per slab (§3.2 lists it as the upgrade path, `instanceable` — blocked by the same MDL defect as §5.1) |
| No canopy tunnel | the framing trunks are not shipped | §5.2 — needs a distant belt or a high-crown species |
| Ferns read as grass tufts | `Switchgrass` is a stand-in; gap G2 is real | R7-3, CC0 fern atlas |
| The north masonry wall has no G7 counterpart | pre-existing v6/v7 geometry | out of scope: H12 |

---

## 5. Three findings

### 5.1 The urban asset MDL chain is broken, and scene07 is the first scene to find out

scene07 is **the first scene in the tree that actually loads an urban asset** — spec §3.0 records
that the only call site is `batch1_common.py:185` and that nothing reaches it. The first pilot
round therefore discovered, in a judged frame, that
`assets/urban/nv_core/materials/SimPBR.mdl` fails to compile:

```
comp error: SimPBR.mdl(29,7): C120 could not find module '.::baking_annotations' in module path
Failed to create MDL shade node for prim '/__Prototype_1/Looks/opaque__stone__rock_03_broken/...'
```

**Every kerb boulder rendered flat bright red** in `preset_h0.3_d2`, `temple_walk` and
`side_slope`. It was **not** fixable by binding over the asset while `instanceable=True`: the
broken binding lives inside `/__Prototype_N/…` and an ancestor `strongerThanDescendants` binding
does not reach into an instance prototype. `scatter_debris`'s docstring claims that pattern works —
it does, for the vegetation `.usda` assets it was measured on, which carry no MDL.

**In-lane cure**: `instanceable=False` plus the ancestor bind, which makes the referenced prims
real descendants. Cost ≈ 30 × 3–10 k unique triangles, which §12-14 explicitly does not budget on.
**The MDL search-path defect itself is not fixed and is not this lane's to fix** — it belongs to
whoever owns `assets/urban` / `urban_kit`. Anyone else adopting the asset-first route for
geometry (as opposed to textures) will hit it immediately.

### 5.2 The framing trunks are not shipped, and the A/B says why

Three placements were rendered: `|cy|` 2.6, then 5.6 / 7.5, then 3.6 / −4.8. An A/B with
`frame_trees` forced empty — same commit, same round, same channel — isolates the two trees as
**the entire DARK / OCCL delta of the rebuild** `[measured]`:

| cut | with trees | without | baseline |
|---|---|---|---|
| `preset_h0.3_d2` | 94.0 / 34.8 % | **114.5 / 13.8 %** | 115.9 / 13.9 % (cb2) |
| `preset_h0.9_d2` | 48.0 / 64.4 % | **98.1 / 19.5 %** | 86.8 / 19.5 % (cb2) |
| `side_slope` | 10.1 / 93.9 % | **87.9 / 24.4 %** | 82.5 / 26.4 % (w2d_fix) |
| `stone_rhythm` | 73.3 / 48.5 % | **127.9 / 7.3 %** | 97.8 / 6.2 % (w2d_fix) |

(mean luminance / dark %). A ground- and stone-albedo lift was tried first and moved `side_slope`
by 0.5 of a point — the darkness was never the albedo.

The cause is structural, not a placement mistake. `Shumard_Oak`'s crown radius is ≈ 0.48× its
height, the corridor is 3.4 m wide, and the south margin is **1.8 m below** the walk, so any tree
big enough to read as G7's old growth also roofs the walk line from 30–40 % of its own height.
**E7-8's canopy tunnel needs a distant belt or a high-crown species, not two near-field trunks.**
Trading a live gate for a dressing item is what H16 forbids, so it is recorded as a follow-up. The
builder path is intact and driven by the (now empty) `frame_trees` list — re-enabling is one line.

### 5.3 `TEX["moss"]` — first consumer, and the caution was right

K4's caution 1 is exact. `rock_moss_set_02` is a 1k scan of an **8 m rock group**; under
`make_pbr`'s world projection it repeats into a hard-edged green camouflage patchwork on
slab-sized faces, and smears into a wet-plastic sheet on a 0.4–0.9 m rounded boulder at every
projection scale tried (0.55 → 2.40 m). It now has exactly one job — the **flat 속채움 bed seen
through a 0–60 mm joint**, where a world-projected rock-with-moss scan reads as damp mottled fill.
Everything else uses the repo's existing green-tint-on-stone convention (§3.0 C-A2). `nor` is
dropped per K4's caution 2 (Poly Haven `_nor_gl` EXR against a DX registry) — dropping it cannot
silently invert the lighting on a judged surface, flipping green can.

Three smaller pilot findings, fixed in `5e134f1`: the 고임돌 scatter placed **0** instances
(`cover` is a fraction, and 0.16 over a 0.30 m² band rounds to zero — 0.80 gives 54 and is also the
physically right number for a 틈메우기돌 band); the 돌깔기 aprons read as **cast concrete paving**
as a 3-cell grid and are now 4×4 with size and yaw jitter; and the mask `z_fn` had to follow the
slab, not the course, because the shoulder lobes sit on non-walk slabs that carry bedding jitter.

---

## 6. Verification ledger

| instrument | result |
|---|---|
| `python3 -m py_compile` | clean, every commit |
| `NEGOBS_SMOKE=1` | every assertion OK/IN; no FAIL, CHECK, OUT or MISS in the final tree |
| `geom_invariance_check --scenes scene07` | **R-4 1/1 · R-6 1/1 PASS**, every commit |
| `placement_lint --scenes scene07` | A/B measured; net −3 WARN, **0 added** |
| `regression_check` vs `260731_w3_cb2` | 14 cuts, FAIL 2 (1 declared FRAME, 1 adjudicated GRAZE), DARK/BLOWN/OCCL clean |
| `near_ground_stats` h0.3 band | flat against baseline |
| `run_data_render` + `check_data_run` (R-2) | 8 cuts; sections [1]–[5] **all PASS** (3.16 s/cut vs SP-3's 2.87). The run's 2 FAILs are zero-sample cross-condition checks needing `--conds` > 1 — an artefact of the mini scope, not of the geometry |

Prim census `1066 → 1424` over the batch (89 slab caps + 89 bodies + 28 beds + 30 boulders +
26 ferns + aprons + roof cluster, against 24 stones + 24 knobs removed). §12-14: instanceability is
the budget, not triangle count — and the one place instancing had to be given up is §5.1.

---

## 7. Owed after this batch

1. **MDL search path for `assets/urban`** — §5.1. Blocks the `rock_03_broken`-per-slab upgrade and
   any other urban-geometry adoption. Not this lane's file.
2. **Canopy tunnel (E7-8)** — §5.2. Needs a distant belt or a high-crown species.
3. **G1 hanok roof · G2 fern atlas · a moss crust layer** — open procurement rows; G1 and G2 were
   already open, the moss crust is added by §4's gap table.
4. **通覽 v3 panel** — GATE-3 is suspended under the per-scene-image doctrine (§8.R OQ-4), and the
   temple_precinct panel is still n = 1.
