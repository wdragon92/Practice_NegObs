# W2-D kit fix — the 7 `ground_kit` defects the edit round found

2026-07-30 · branch `feat/realism-v1` · **CPU only — no GPU, no render, no Isaac, no SMOKE, no commit**
Owned files: `ground_kit.py` · `scenes/main/scene10_park_deck_switchback.py` ·
`scenes/main/scene12_riverside_deck.py` · `scenes/batch1/sceneD2_floor_opening.py` (+ this report).
Inputs: `w2d_edit_g{1,2,3}.md` · `w2d_edit_gb.md` · `redteam_w2d_edits.md` (all four builders'
defect tables and the red team's CONFIRMED verdicts).

---

## 0. Verdict in one paragraph

All seven are fixed and every one was **re-derived numerically before it was touched** — four of
them reproduce the claiming report's arithmetic to the digit (D-1's 11.16/1.57/28.54/13.51 rows,
R1's strip centre at deck top −0.0094, R4's scene11 "2 joints where 3 are intended", F2's
`infra=dict()` no-op). Two came out differently from how they were filed: F1's fix clears the two
gates `gb` named on sceneD2 (B6 and B8) but the deferred leg is then stopped by a *different and
genuine* rule (GT-E2 at d10), and D-5 turned out to be **wider** than the missing `pool=` —
`apply_ground` was re-reading `GROUND_PROFILES` instead of the plan, so both scenes that overrode
their scatter count (07 and 10) planned one number and built another. Net effect on the tree:
**+2 geometry prims** (scene11 +1 restored joint, sceneD2 +1 restored marking leg), **−117 scatter
instances** (07 and 10, because a rock covers 1.345× the ground a leaf does at the same target
cover), and **zero** prims moved in USD terms for the two deck scenes — the R1 fix is provably
bit-identical to the workaround it replaces. All standing checks are green.

---

## 1. Verification — all green `[measured]`

| check | result |
|---|---|
| `python3 ground_kit.py` | exit **0** · hard gates **33/33** · fixture prims 1,333 → **1,324** · apply round-trip 33/33 · unsubstituted material refs 0 · recessed-burial 0 |
| `python3 scripts/geom_invariance_check.py` | **R-5 PASS** (0 residual `LOOK_V1`) · **R-4 33/33 PASS** · **R-6 33/33 PASS** · exit 0 |
| OFF arm `NEGOBS_GKIT=0` on 05/07/10/11/12/19/D1/D2 | R-4 **8/8** · R-6 **8/8** · exit 0 |
| stub harness, all 33 scenes' real `main()` | 33/33 assemble · **37 `plan_ground` calls, every one passes B6–B12** (the function raises on violation, so assembly *is* the gate proof on the wired coordinates) |
| `py_compile` | 4/4 files clean |
| determinism | two independent harness runs, plan-for-plan identical (0 drift) |
| file-touch discipline | `git status` = exactly the 4 owned files. scene15 untouched (another agent), no spec/brief/fixture-bearing doc edited, no commit. |

**New standing coverage** — four checks added to `python3 ground_kit.py` so these defects cannot
come back silently:

```
[2] R3 데칼 사다리 폭 ≤ 2 mm · 최대 양각 ≤ GT_DELTA/8   (폭 1.7 mm · 최대 2.3 mm)
[2] 산포 kind 전부 SCATTER_POOLS 등재                   (['gravel'] ⊆ ['gravel','leaf','rock'])
[4] 빈 사전 오버라이드 → ValueError (F2 무언의 무동작 차단)
[4] infra=None 명시 소거 = 명시 0 패턴 (F2 하위호환)     (소거 37 프림 = 명시0 37 프림)
[4] 미등재 산포 kind → ValueError (D-5)
```

D-6 needs no new check: with `natural=True` on the fixture, putting urban infra back on scene03
makes `plan_ground` raise inside the existing 33-scene dry run.

Harness: `scratchpad/plan_harness.py` — the fake-USD stub lifted out of `geom_invariance_check`
with `gk.plan_ground` / `gk.apply_ground` / `sc.scatter_debris` wrapped by a recorder. Rock cover
measurement: `scratchpad/measure_rocks.py`.

### 1.1 Every delta in the tree, and its cause

**Plan level (37 plans).** Nothing else moved.

| scene / plan | delta | cause |
|---|---|---|
| scene11 | prims 35 → **36** (joints 2 → 3) | **D-1** — the guard was dropping a joint 15 m *behind* the drop edge |
| sceneD2 | prims 24 → **25**, WARN `B1,B2,B3,B5` → `B1,B2,B5` | **F1** — the west perimeter leg is restored; it scores B3 |
| scene10 plan B | plan z 0.0156 → **−0.005**, δmax 0.0200 → **0.0006** | **R1** — builder-side `surface_top_z`, scene-side lift removed |
| scene12 plan B | plan z 0.0206 → **0.0000**, δmax 0.0200 → **0.0006** | same |
| 03·04·06·07·10A·11·12A·19·D1 | δmax +0.0001 … +0.0017 | **R3** — decal ladder is real relief, so it shows in `proud` |

**Apply level (USD).**

| scene | prims | instances | cause |
|---|---|---|---|
| scene11 | 35 → **36** | 0 | D-1 |
| sceneD2 | 24 → **25** | 0 | F1 |
| scene07 | 11 (=) | 300 → **223** | D-5 — rock pool, same target cover |
| scene10 | 7 (=) | 158 → **118** | D-5 |
| scene10/12 deck plans | 10 / 120 (=) | 0 | R1 — **prim positions bit-identical**, see §4 |

Totals: plan prims 1,391 → **1,393** · applied prims 1,391 → **1,393** · applied scatter
instances 708 → **591**.

**Fixture level (`SCENE_PLANS`, what `python3 ground_kit.py` checks).** scene03 53 → **43** prims
(D-6, the 10 illegal urban-infra prims); scene11 32 → **33** (D-1); scene10/12 δmax 0.0200 →
0.0014 (R1); 04/06/07/12/19 δmax (R3). Total 1,333 → 1,324.

---

## 2. D-1 / R4 — `_edge_guard_ticks` was origin- and axis-blind

**Mechanism, re-derived.** Two frame bugs in three lines. (a) The tick's **world x** went straight
into `drow()`, which takes a **forward-s offset**; (b) the X family was guarded regardless of the
travel axis, so on a −y scene the guard examined the joints that run *parallel* to travel and never
looked at the transverse ones.

**Before / after on the scene that proves both halves.** scene05, grid origin −1.5, region run out
to the lip (i.e. the g1 workaround removed) `[measured]`:

| tick, world x | forward s | what v1.2 fed to `drow` | the truth | bound @d10 | v1.2 | v1.3 |
|---|---|---|---|---|---|---|
| −1.8 | −0.3 | 11.16 | **1.57** | 16 | drop (right answer, wrong reason) | drop |
| −3.6 | −2.1 | 28.54 | **13.51** | 16 | **keep** | **drop** |

Forcing the v1.2 skip set on that region reproduces g1's raise verbatim:

```
B7: GT-E2 위반 1: [('Joints/JX_5', 10, 13.48, 'Δ 13.5@1080 = 6.7@540 < 16@1080')]
```

With v1.3 the same plan assembles, 6 joint prims, 50 total.

**The fix.** Ticks are converted to forward s through the plan's own `_View(origin, gy, axis)`, the
guarded family is the one perpendicular to travel (`skip_x` for ±x, `skip_y` for ±y), and the test
is now **B7's own arithmetic** — ground distance inside `[0.7d, 2.2d]`, row separation against
`graze_row_sep_1080(d)`, evaluated at both joint rims (the groove width is passed in). So the guard
can no longer drop a tick B7 would pass (content loss) nor keep one B7 will reject (hard raise).
`_grid_ticks` is now a single module-level generator shared by the guard and `build_joint_grid`, so
the two can never disagree about where the ticks are — they are matched on the rounded coordinate,
not an index.

**Guard rows on every wired plan, v1.2 → v1.3** `[measured — 23 plans carry joints]`:

| scene | origin / axis | v1.2 skip_x | v1.3 skip_x / skip_y | joints |
|---|---|---|---|---|
| **05** | (−1.5,0,0) / +x | `[]` | `[]` / `[]` | 6 |
| **06** | (3.5,−13,5) / **−y** | `[]` (never looked — step_x is None) | `[]` / **`[]`** (Y family now examined) | 3 |
| **11** | (15,0,5.5) / +x | `[0.0]` | **`[]`** / `[]` | 2 → **3** |
| **19** | (11.6,0,…) / −x | — | — (roof membrane: no joint op) | — |
| **D1** ×2 | (0,0,0) / +x | `[0.0]`, `[]` | `[0.0]`, `[]` / `[]` | 4, 7 |
| **D4** | — | — | — (M8 deferral: 0 `plan_ground` calls) | — |
| 01·02·09·13·14·15·16·17·18·20·21·C1·C2·C4·D2·D3·N5 | origin 0 / +x | unchanged | unchanged | unchanged |

Only scene11 changes, exactly as g2's R4 predicted ("2 joints where the profile intends 3").

**Scene-side clamps that are now redundant** (listed for the round, **not edited** — not my files):

* **scene05 `PARAMS["gkit"]["x1"] = -3.70`** (`scene05_amphitheater.py:127`, comment at :120-126).
  Proven redundant `[measured]`: with the region run out to the lip (−1.50) the v1.3 guard drops
  `[-3.6, -1.8]` and keeps `-12.6, -10.8, -9.0, -7.2, -5.4` — **exactly the tick set the clamp was
  cut to preserve**, and the plan assembles with the same 6 joint prims / 50 total. Restoring
  x1 to the lip would additionally give the surface elements (patch/crack/stain/weed) the extra
  1.4 m of near field the clamp currently denies them, because `_trim_region` would then cut at
  −2.30 instead of −3.70. Whoever owns scene05 should decide; nothing breaks either way.
* No other scene carries a D-1 workaround. 11/19/D1/D4 were flagged as *at risk* by g1, not
  clamped — 11 was silently losing a joint (now restored), 19 has no joint op, D1 is unaffected
  (origin 0), D4 is dormant under M8.

---

## 3. D-5 — every profile's scatter came out of the autumn-leaf pool

**Mechanism, re-derived.** `apply_ground` called the scatter callback with no `pool=`, so all three
gravel profiles (P11 scene04, P12 scene07, P18 scene10) fell through to
`scene_common.scatter_debris`'s default — `VEG_DEBRIS`, five fallen-leaf assets. **A second
mechanism was found in the same code**: the callback's `max_count` came from
`GROUND_PROFILES[plan["profile"]]`, i.e. the **raw profile table**, not the plan. A scene that
overrode its scatter therefore planned one count and built another — measured on the shipped tree:

| scene | field count the scene prescribes | `max_count` actually passed (v1.2) |
|---|---|---|
| **scene07** | **270** (`PARAMS.gkit.gravel_n`, "8/m² × 33.6 m²") | **330** (P12 profile default) ✗ |
| **scene10** | **120** (`PARAMS.gkit.gravel_n`) | **180** (P18 profile default) ✗ |
| scene04 | *(no override)* | 250 ✓ |

Both scenes that overrode their scatter got the profile's number instead. Neither miss was
visible: the drawn count is cover-limited well under either cap, so the cap only bites when the
region is large — but B10 was budgeting one number while the USD was authorised for another.

**The fix.** `plan_ground` records the **effective, post-override** scatter spec as
`plan["scatter"]`; `apply_ground` reads it (falling back to the profile table for plans built before
v1.3) and resolves `spec["kind"]` through a new `SCATTER_POOLS` ledger.

**The pool.** The W2-A4 procured set — `Rocks/rock_small_02~07,11~14`, the 10 assets
`props_audit_w1/B_groundcover_debris.md` §10-a C3 asked for; all 10 verified present on disk.
Cover was **measured, not estimated**, by the audit's own method (project every triangle onto XY,
rasterise at 2048 px on the long side) `[measured — scratchpad/measure_rocks.py]`:

| rock | cover m² | tris | dx × dy × dz [m] | zmax |
|---|---|---|---|---|
| 02 | 0.0338 | 460 | 0.237 × 0.197 × 0.162 | 0.086 |
| 03 | 0.0301 | 432 | 0.209 × 0.186 × 0.156 | 0.077 |
| 04 | 0.0331 | 378 | 0.212 × 0.193 × 0.169 | 0.085 |
| 05 | 0.0221 | 480 | 0.209 × 0.149 × 0.140 | 0.074 |
| 06 | 0.0240 | 392 | 0.209 × 0.172 × 0.127 | 0.062 |
| 07 | 0.0119 | 496 | 0.160 × 0.122 × 0.088 | 0.047 |
| 11 | 0.0289 | 436 | 0.233 × 0.147 × 0.140 | 0.072 |
| 12 | 0.0310 | 400 | 0.228 × 0.193 × 0.142 | 0.073 |
| 13 | 0.0227 | 398 | 0.213 × 0.140 × 0.123 | 0.069 |
| 14 | 0.0330 | 428 | 0.203 × 0.195 × 0.146 | 0.077 |

mean cover **0.02706 m²**, mean zmax **0.0721 m**. `rock_small_01` is excluded: it carries a root
`rotateXYZ`, so its silhouette is not measurable in point space (the W1 five, 01/08/09/10/15, are
not in the pool). `kind="leaf"` maps to `None` = the callback's own default, which is what sceneC2
already uses on its own path (sceneC2 injects **no** scatter callback into `apply_ground`, so its
leaf identity is untouched by any of this).

**Seating.** The rock origin is the rock **centre**, so dropping one at ground z leaves ~72 mm
standing proud — above the `scatter_expose_max` 0.06 m the trail statistic gives. `apply_ground`
now passes `sink = mean_zmax − expose = 0.0121 m`, i.e. half-buried, which is what
`[통계] 등산로 6/6 — φ≤0.12 반매몰 노출 ≤0.06` describes.

**Before / after** `[measured — n = A·(−ln(1−cover)) / mean_cov, capped]`:

| call | area m² | cover | leaf pool | **rock pool** |
|---|---|---|---|---|
| scene04 field | 38.4 | 0.18 | 379 → cap **250** | 282 → cap **250** |
| scene07 field | 33.6 | 0.14 | **252** | **187** |
| scene07 edge ×2 | 4.64 | 0.10 | **24** each | **18** each |
| scene10 field | 17.68 | 0.12 | **112** | **84** |
| scene10 edge ×2 | 4.32 | 0.10 | **23** each | **17** each |

Applied totals: scene04 250 → 250, scene07 300 → **223**, scene10 158 → **118**. The drop is the
formula holding *target cover* constant while the per-instance footprint grows 1.345×; the ground
looks the same, it is just made of fewer, larger objects. Seasonal-rule status: **07 and 10 no
longer place a single autumn leaf** through the kit.

**Contract note.** The scatter callback contract now includes `pool=` and `sink=`. `apply_ground`
inspects the injected callable's signature and degrades to v1.2 behaviour with a printed warning if
it does not take them, rather than crashing a render on a signature mismatch. An unknown
`kind` raises at plan time — a new prescription cannot silently fall back to leaves.

---

## 4. R1 — `build_deck_planks` buried its own output

**Mechanism, re-derived.** The gap strip's top was `z − 0.020`, i.e. **below** the deck surface,
and scene decks are solid boxes — the identical burial mode `cb40ae8` fixed for joints and manholes
with `surface_top_z()`. 120 of scene12's prims and 10 of scene10's rendered zero pixels at the
deck's own z.

**The fix.** The builder now does what `build_joint_grid` does: `cz = surface_top_z(z) − thick/2`,
`proud = +GROUND_PROUD_MIN`, and the nominal −0.020 groove depth is kept in the ledger as
`recess_nominal` so B6/B7 still judge it as a recess (B6 takes `min(0, recess_nominal)`, B7 skips
`exc="plank_gap"` outright). Then the scene-side lifts were removed:

* `scene10.ground_plan_deck()` — `z=gk.surface_top_z(z_deck) + 0.020` → `z=z_deck`
* `scene12.ground_plan_deck()` — `z=gk.surface_top_z(d["z_top"]) + 0.020` → `z=d["z_top"]`

**The strips do not move.** Both routes put the strip centre at `deck_top − 0.0094`
`[calc: (z+0.0006+0.020) − 0.030 = z − 0.0094 = (z+0.0006) − 0.010]`. Verified by running the new
builder against a verbatim re-implementation of the v1.2 formula fed the worked-around z, on both
scenes' real arguments `[measured]`:

| scene | prims new / old | every path, centre and size identical | element top z |
|---|---|---|---|
| scene10 entry deck | 10 / 10 | **True** | −0.0044 (deck top −0.005) |
| scene12 deck | 120 / 120 | **True** | +0.0006 (deck top 0.000) |

So R1 costs **zero** render delta on 10 and 12 — it is a correctness fix to the *ledger* (which used
to claim a −20 mm buried plate) and to every **other** consumer of the builder. P13 `levee_paved`
also carries `deck_planks`, so any future scene taking that profile's extras gets a visible gap
instead of a buried one for free. The scene docstrings now record the history and that the lift is
gone.

---

## 5. R3 — every decal builder emitted the same top z

**Mechanism, re-derived.** `build_stain_field`, `build_footprints`, `build_wear_lane`,
`build_edge_litter`, `build_edge_break` and `build_silt_band` all put their box top at exactly
`z + stain_proud`. Wherever two overlap in XY the top plane is coincident and the renderer has no
ordering. Measured across the 37 shipped plans: **71 overlapping coplanar decal pairs**, of which
**60 are between different materials** (the visible kind) — including the `Stain_dirt` ×
`Stain_water` × `Wear` pile-up in scene07 that g2 located by hand.

**The fix.** A deterministic ladder, bottom-up by what physically lies under what. Families step by
`DECAL_Z_EPS = 0.2 mm`; inside `build_stain_field`, which is one builder emitting eight different
materials, each `kind` steps by a further `DECAL_Z_SUB = 0.1 mm` (dirt-over-water is the commonest
overlap there is — 9 of the 60).

| rank | family | proud [mm] |
|---|---|---|
| 0 | `edge_break` (it *is* the ground) | 0.6 |
| 1 | `silt_band` | 0.8 |
| 2 | `edge_litter` | 1.0 |
| 3 | `wear_lane` | 1.2 |
| 4 | `footprint` | 1.4 |
| 5 + kind index | `stain` (tire … drip) | 1.6 … 2.3 |

**Span 1.7 mm**, inside the 2 mm ceiling and under a tenth of `GT_DELTA`. It is real relief, not an
epsilon trick, so it is reported in `proud`; GT-E1′ then needs `EDGE_K × 0.0023 = 0.092 m` of edge
clearance at worst, against a **measured minimum decal edge gap of 0.60 m** across all 37 plans
(6.5× margin) — B6 stays green everywhere, which the 33/33 runs confirm.

**Before → after** `[measured]`: cross-material coplanar overlaps **60 → 0**. The 11 remaining
coplanar pairs are all *same-material* (`Stain_dirt/dirt_1` over `Stain_dirt/dirt_3`), where a
depth fight is between two identical surfaces and cannot be seen.

---

## 6. F1 — `_ik_marking` built the AABB ignoring yaw

**Mechanism, re-derived.** `_box_aabb(x0 + L/2, y0, …, L, w, …)` laid the length along **+X
regardless of `yaw_deg`**, while the same function classified the line `cross`/`long` **using** the
yaw. `infra_kit` lays every marking with +X = length, +Y = width and rotates about `(x0, y0)`, so
the correct AABB is that local box rotated — `_obb_aabb` already existed and was simply not used
here.

**The fix.** `_marking_local_box()` returns the local extent per `kind` (line / parking /
crosswalk); `_marking_aabb()` rotates its four corners about the anchor and takes min/max. Exact,
not a `max(L,w)` square (that approximation is what wrongly made scene13's entry trench "visible"
at d10 — the same class of error the `_obb_aabb` docstring records).

**It corrects a live misjudgement in the shipped tree**, not just a hypothetical: sceneD1's
`Marking_2` is a yaw-90 line at (10.0, 0.0), length 5.8 `[measured]`:

| | AABB x | AABB y | `line` |
|---|---|---|---|
| v1.2 | **10.000 … 15.800** | −0.075 … 0.075 | `cross` |
| v1.3 | 9.925 … 10.075 | **0.000 … 5.800** | `cross` |

The element was being judged as a 5.8 m longitudinal run 5.8 m *downrange* of where it is. D1's
yard plan carries no edges, so no gate fired — but every s-span, t-span and frame-budget number for
that element was wrong. scene13/N4's yaw-0 lane lines are unchanged, which is why this survived.

### 6.1 sceneD2's deferred west leg — restored, but not where `gb` intended

With the AABB fixed, **the two gates `gb` named are clear.** Reproducing gb's intended placement
(a yaw-90 band 0.15 m in front of the lip, `mark_lines` entry `(-0.225, -1.125, 90.0, 2.25)`)
gives AABB x [−0.300, −0.150] × y [−1.125, 1.125] → edge gap **0.15 m ≥ EDGE_K × 0.003 = 0.12 m**
(B6 ✓) and x1 = −0.15 < void x0 = 0 (B8 ✓). `plan_ground` now raises on **B7 alone** `[measured]`:

```
B7: GT-E2 위반 3: [('Marking_2', 2, 19.75, 'Δ 19.7@1080 = 9.9@540 < 32@1080'),
                   ('Marking_2', 5,  3.11, 'Δ  3.1@1080 = 1.6@540 < 32@1080'),
                   ('Marking_2', 10, 0.77, 'Δ  0.8@1080 = 0.4@540 < 16@1080')]
```

That is not a misjudgement — it is GT-E2 doing its job. A full-width transverse line hugging the
lip fuses with the lip under GRAZE at every shot, and the d10 E band (ground distance 7–22 m) is so
shallow that the near rim must retreat **2.60 m** from the lip before the separation reaches the
16-row footprint `[calc]`.

**What shipped.** The leg is restored at `x = −3.00`, spanning y −1.125 … +1.125 — the west ends of
the two longitudinal legs — closing the painted zone into a **ㄷ shape open toward the opening**.
Legal at every cut (d2/d5 out of the E band; d10 Δ **21.0 ≥ 16** `[measured]`), edge gap 2.925 m,
no void intersection, and it reads as the wear order §5.8 prescribes (the lip side of an opening
marking is what gets walked off first — "황색 잔존 20~30 %"). sceneD2 goes 24 → **25** prims and
clears its B3 WARN.

**Side benefit worth keeping:** the shipped tree now contains a yaw-90 marking on a scene with a
void and an edge, so a regression that reverts F1 trips B8 on sceneD2 immediately. Before this
round nothing in the 33 scenes exercised the rotated path under a gate.

**Supervisor item.** If the marking is wanted *hugging* the lip, the mechanism already exists and is
the one tactile paving uses: **GT-E2-x registration** (`EXPECTED_FP`), which tells the GRAZE
adjudicator which rows the mandatory transverse element occupies so it is not mistaken for the edge.
That is the adjudicator's file, not the kit's, and it belongs with the C4 FP-window item already on
the red team's rider list.

---

## 7. F2 — `overrides` merged dicts, so `infra=dict()` cleared nothing

**Mechanism, re-derived.** `d = dict(prof[k]); d.update(v)` — an empty dict merges to a no-op that
*looks* like a clear. sceneC2 asked for `infra=dict()` and still got 1 manhole + 2 gullies + 1
L-gutter on a row whose spec says "urban infrastructure 0".

**The fix — two halves.**

1. **Explicit clear.** `overrides[k] = None` empties the key, to the right empty value per key
   (`_OVERRIDE_EMPTY`: `pave`/`infra` → `{}`, `surface`/`extras` → `()`, `scatter` → `None`, and
   anything else → `None`). So `scatter=None` keeps meaning exactly what scene10/12 already rely on.
2. **The silent no-op is now loud.** An empty dict override raises with the fix in the message
   ("프로파일 값을 비우려면 `k=None`, 일부만 끄려면 0/() 를 명시하라"). Nothing in the tree passes
   one, so this breaks nothing and closes the trap for good.

**Back-compat with the explicit-zero pattern `gb` used** `[measured]` — `sidewalk_block`,
scene16 region:

| override | prims | element kinds |
|---|---|---|
| *(none)* | 46 | crack, **gully**, **gutter_l**, joint, **manhole**, patch, patch_cut, stain, weed |
| `infra=dict(manhole=0, gully=0, gutter_L=0)` (gb's pattern) | **37** | crack, joint, patch, patch_cut, stain, weed |
| `infra=None` (new) | **37** | *identical* |
| `infra=dict()` | **ValueError** | — |

---

## 8. D-6 — the scene03 fixture ran urban infra on a natural scene

**Mechanism, re-derived.** `SCENE_PLANS["scene03"]` was plain `levee_paved`, so the CPU self-check
green-lit manhole + 2 gullies + an L-gutter on a natural scene. The gate structurally cannot see it:
`natural` is a **profile** flag and the fixture never set one. The real scene forces
`natural=True` and spells its zeros; the fixture did not follow.

**The fix.** `_S()` gained an `overrides` field, and — because a new fixture field wired into some
self-check passes and not others is exactly how this class of bug happens — all four call sites now
go through one `_fixture_plan(scene)` helper. scene03's fixture is
`overrides=dict(natural=True, infra=None)`, which also exercises F2's new clear inside the standing
check.

**Before / after** `[measured]`:

| | prims | δmax | WARN | urban infra |
|---|---|---|---|---|
| v1.2 fixture | 53 | 0.1182 | B3,B5 | **manhole 1 · gully 2 · gutter_L 1** |
| v1.3 fixture | **43** | 0.1182 | B1,B2,B3,B4,B5 | **0** |

The extra WARNs are the point: B1/B2 (near-window area element, screen width 100 %) and B4 were
being satisfied **by the illegal manhole and gutter**. A natural riverbank has no manhole to fill
the frame, and the fixture now says so. And the gate now bites — `natural=True` without the infra
clear raises:

```
ground_kit: natural=True 프로파일 'levee_paved' 에 도시 인프라 ['manhole', 'gully', 'gutter_L'] 를 넣을 수 없다.
```

**Not fixed here (out of scope, still open):** the red team's §6.1 finding that fixture drift is
systemic — sceneN1 still carries the defective spec manhole (−1.0, 0.4) the scene moved to W2;
scene08's fixture declares a kit-emitted `opening_ring` the scene keeps on its own path;
scene19's fixture origin 9.04 / edge s=0 versus the real 11.6 / 7.6; **scene05's fixture uses
origin (0,0,0)**, which is why the fixture never exercised D-1 for scene05 at all. The right closure
is the red team's own recommendation — generate `SCENE_PLANS` from each scene's `ground_plan()`, or
demote the fixture in favour of a recorder harness run like §1's.

---

## 9. For the GPU round

1. **R3 shimmer — still worth a crop, but the question changed.** Coplanar cross-material decal
   pairs are 0, so the *original* R3 concern (redteam rider 3: "check scene07/scene10 d2/d5 crops
   for shimmer before dismissing") is answered geometrically. What is left to eyeball is the
   opposite: the smallest step in the ladder is the **0.1 mm between two stain kinds**, and
   scene07/scene10 d2 is where the largest decal overlap sits. One crop each confirms the step is
   big enough; if it is not, raising `DECAL_Z_SUB` to 0.0002 costs 0.7 mm of span and still fits
   under 2.5 mm.
2. **D-5 rock look.** The pool is *rubble*, not pea gravel: native width 0.16–0.24 m against the
   `φ ≤ 0.12` the trail statistic describes, and one `sink` has to serve every draw while the
   callback's `scale_jitter` is (0.75, 1.25), so per-instance exposure spreads **0.023–0.095 m**
   around the 0.060 m target. Scenes 04/07/10 d2/d5 will show it. If it reads too coarse, the lever
   is `scale_jitter` (a look call, not a gate one) or dropping rows 02/04/14 (the three widest) from
   the pool.
3. **scene10's `LeafRing` is deliberately still leaves** and was left alone: §13.4 10-2 puts that
   scatter there specifically to break the outline of the scene's own leaf decals, so gravel would
   be wrong. Flagging it only so nobody reads "scene10 still scatters leaves" as a missed D-5.
4. **scene05's region clamp is now redundant** (§2). Un-clamping gives the near field 1.4 m more
   surface content; it is scene05's owner's call and needs no kit change.
5. **sceneD2's lip-hugging marking** needs a GT-E2-x ruling if it is wanted (§6.1) — supervisor.
6. Carried unchanged from the edit round: σ_LF ≥ 5.0 WARN gate restore; scene05 charcoal bands in
   the d10 E band; C4 GRAZE FP window; default-arm tactile policy (§6.2 of the red team report).
   None of them is touched by this fix round.

---

## 10. Reproduce

```bash
cd /home/vislab/Desktop/work_sy/Practice_NegObs
unset PYTHONPATH VIRTUAL_ENV
source ~/miniconda3/etc/profile.d/conda.sh && conda activate env_isaaclab
export PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1

python3 ground_kit.py                                   # exit 0, 33/33, fixture prims 1324
python3 scripts/geom_invariance_check.py                # R-5 / R-4 33/33 / R-6 33/33
NEGOBS_GKIT=0 python3 scripts/geom_invariance_check.py \
    --scenes scene05,scene07,scene10,scene11,scene12,scene19,sceneD1,sceneD2

# real-argument gate proof + all the deltas in Sec.1.1 (scratchpad, not committed):
#   plan_harness.py <out.json> ALL   — fake-USD stub from geom_invariance_check with
#                                      plan_ground / apply_ground / scatter_debris recorded
#   measure_rocks.py                 — XY-silhouette rasterisation of the 15 rock assets
```
