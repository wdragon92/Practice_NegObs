# CB-3 — batch1 furniture jitter abolition (K2 + S7/S8 call sites)

> **Wave**: W3 · **Window**: 1 · **WP**: K2 · **Commit batch**: CB-3 · **Date**: 2026-07-31
> **Branch**: `feat/realism-v1` · **Parent**: `d7494f4`
> **Spec**: `Docs/briefs/w3_execution_spec_v1.md` §1.2 · §3.1 C6 · §4.2 K2 · §5.2 CB-3 · §6.2 K2 ·
> §7.2 GATE-1 · §10.1 rows 3–4 · corrected fact C-2
> **Owned files** (the whole commit, nothing else): `scenes/batch1/batch1_common.py` +
> the narrow `bc.jit_*` call-site edits in `sceneN1` · `sceneN2` · `sceneN3` · `sceneC1` ·
> `sceneC4` · `sceneD2` · `sceneD4`.

---

## 0. Verdict

**PASS, with one declared and fully attributed FRAME delta on the sceneN3 pilot.**

| gate | result |
|---|---|
| `py_compile` × 8 touched files | **OK** |
| `geom_invariance_check` | **33/33 R-4 · 33/33 R-6 PASS**, prim count unchanged in **all 33** scenes |
| `placement_lint` LINT-7-static | **24 ERROR → 5 ERROR** (the 5 are other WPs' files) |
| `placement_lint` every other check | **no added finding**; LINT-7 dynamic −27 WARN |
| scene self-checks (`NEGOBS_GEOCHECK=1`) | N1 합격 · N2 합격 · N3 합격 (N2/N3 byte-identical to HEAD) |
| GATE-1 pilot **sceneC1** | `regression_check` **FAIL 0 · WARN 0 — 회귀 없음** |
| GATE-1 pilot **sceneN3** | FAIL 2 · WARN 4, **`FRAME` only** — adjudicated in §5 |

The one thing that did **not** land is the C6 bollard asset swap. It is **prepared, not adopted**,
against four independent blocks (§4). That is the spec's own `§1.8 "prepare"` posture, not a skip.

---

## 1. What the abolition actually required — and why "flip the defaults" is not enough

Spec §6.2-K2 orders the work: *"Flip defaults **first** (one edit, library-wide,
linter-verifiable without a render), then remove the now-inert call sites."*

Taken as a **signature**-default change (`lo`/`hi`/`amp` → 0) that instruction is a no-op:
`[measured]` **every one of C-2's 24 call sites passes its amplitude explicitly** —
`amp=0.12 / 0.15 / 0.18 / 0.20 / 0.22`, `lo=3.0, hi=5.0` or `hi=8.0`, or
`amp=j["pos_amp"]` out of PARAMS. Not one call site relies on a default. So "flip the defaults"
has to mean a **behaviour** flip, and the two readings are distinguishable by experiment:

| step | `jit_call_sites` | LINT-7-static | LINT-7 dynamic | total ERROR / WARN |
|---|---|---|---|---|
| HEAD (`d7494f4`) | 24 | 24 ERROR | 144 WARN | 393 / 385 |
| **after the behaviour flip alone** | 24 | 24 ERROR | **117 WARN** | 393 / **358** |
| after the call-site removal | **5** | **5 ERROR** + 1 census WARN | 117 WARN | **374** / 359 |

The middle row is the deliverable §6.2-K2 asked for: **the abolition is proven library-wide
before a single call site is touched and without a render** — 27 furniture prims came back onto
their anchor bearings from one edit. Both defaults were flipped to zero as well, so the declared
default and the actual behaviour agree.

`jit_scalar` and `jit_tint` are **untouched**. `jit_scalar` is not in §10.1's 13-row inventory
(which names only `batch1_common.py:248` and `:256`) and `jit_tint` is exempt by §12-15. Proof
that they really are untouched: `sceneD1`, `sceneD3` and `sceneN4` — the three batch1 scenes that
use `jit_scalar`/`jit_tint` and nothing else — come out **prim-hash identical** (§3).

---

## 2. The 19 call sites removed, and the replacement bearing for each

Spec §10.1's replacement rule is structural, not deletion: *an object takes the bearing of the
thing it belongs to.* Where the call already carried `base=`, that argument **was** the anchor
bearing, so the replacement is `base` itself; where it did not, the anchor is an axis-aligned kerb,
platform edge or slab edge and the bearing is 0.

| file | sites | what they were | replacement |
|---|---|---|---|
| `sceneN1_shadow_band.py:337,338` | `jit_pos`+`jit_yaw` | bench ±0.22 m / ±3–8° | `b["yaw"]` — the planter or hedge face each bench stands in front of |
| `sceneN1:348,349` | `jit_pos`+`jit_yaw` | streetlight ±0.20 m / ±3–8° | 0° — the arm reaches over what it lights |
| `sceneN2_asphalt_patch.py:351,352` | `jit_pos`+`jit_yaw` | streetlight ±0.20 m / ±3–8° | 0° — kerb bearing |
| `sceneN2:361` | `jit_pos` | planter ±0.15 m | nominal centre (its own docstring already conceded "kept axis-aligned: the kerb") |
| `sceneN3_trompe_loeil.py:583,584` | `jit_pos`+`jit_yaw` | bench ±0.18 m / ±3–8° | `b["yaw"]` |
| `sceneN3:589` | `jit_pos` | planter ±0.15 m | nominal centre |
| `sceneC1_snow_stairs.py:811,812` | `jit_pos`+`jit_yaw` | bench ±0.18 m / ±3–8° | `bd["yaw"]` |
| `sceneC1:837` | `jit_pos` | lamp ±0.15 m | nominal centre |
| `sceneC4_wet_stairs.py:377` | `jit_pos` | planter ±0.15 m | nominal centre |
| `sceneC4:381` | `jit_pos` | plaza lamp ±0.18 m | nominal centre |
| `sceneD2_floor_opening.py:293,294` | `jit_pos`+`jit_yaw` | safety fence ±0.18 m / ±3–8° | 0° — the slab edge the run guards |
| `sceneD4_subway_platform.py:649,650` | `jit_pos`+`jit_yaw` | platform bench ±0.12 m / ±3–5° | 0° — the platform-edge set-out line, \|y\| = 7.40 exactly |

**Clearance argument, and it runs one way only.** Every one of these call sites sized its amplitude
to stay *inside* an existing clearance — `sceneC1:809` *"does not eat into the existing clearance
(0.22 m)"*, `sceneD4:646` *"\|y\| = 7.40 ± 0.12 → clearance kept"*, `sceneD2:289` *"the 3.9 m
clearance … is overwhelmingly larger than the jitter width"*. Collapsing the offset to zero
therefore **restores** each clearance to its full nominal value and can never narrow one. sceneN1's
own dressing check measured the effect: nearest camera-to-prop horizontal distance
**0.23 m → 0.28 m**.

**Two dependent deletions, declared because they are not literally call sites:**

1. `sceneN1:160` `bench_jitter=dict(yaw_lo=3.0, yaw_hi=8.0, pos_amp=0.22)` — deleted. `[measured]`
   its only consumer was the removed call. Leaving it is the re-introduction hazard §6.2-K2 warns
   about ("dead calls that read as intent").
2. `sceneN1:153-154` — the comment C-2 identifies as the 25th text hit. It said the benches *use*
   the jitter, which is now false. It is **rewritten in place, keeping the literal
   `bc.jit_yaw/jit_pos` token and the two-line shape**, so the site the rules file pins
   (`expected_comment_site: sceneN1:154`) is still exactly line 154 and still a text hit —
   satisfying both C-2 ("rewrite that comment") and the window instruction ("leave it").

---

## 3. The 24→0 target, and why it lands at 24→5

The window brief asks for LINT-7-static 24 → 0. It reaches **24 → 5**, and the gap is an ownership
boundary, not unfinished work.

Spec §5.2 assigns CB-3 to **K2 + S7 + S8**, and §4.3's own WP rows enumerate the sites those WPs
own: S7 *"N1 ×4 · N2 ×3 · N3 ×3"* and S8 *"C1 ×3 · C4 ×2 · D2 ×2 · D4 ×2"* = **19**. The other
5 sites live in files §4.3 gives to different WPs for the whole wave:

| residual site | file owner | lands in |
|---|---|---|
| `sceneC2_leaf_stairs.py:801,802,821,837` (×4) | **S3** | CB-2 (C2 is a CB-2 pilot) |
| `sceneN5_flush_grating.py:386` (×1) | **S4** | CB-10 |

§0's scope discipline (*"no agent may edit a file it does not own in §4"*) is absolute, and both
files are being edited by other agents right now (`git status` shows `sceneC2` and `sceneD3`
modified mid-window). So CB-3 removes 19 and hands over 5.

**The abolition's *effect* is nevertheless complete at 24/24.** The behaviour flip is library-wide,
so the 5 residual calls are inert: `jit_yaw` returns the anchor bearing, `jit_pos` returns `(0, 0)`.
Nothing in the tree still produces decorative angular wobble.

**Two consequences the fleet must know:**

- **CB-3 moves geometry in 9 batch1 scenes, not 7.** `sceneC2` and `sceneN5` change too, because
  their surviving calls are now inert. Prim hashes moved in exactly
  **C1 · C2 · C4 · D2 · D4 · N1 · N2 · N3 · N5**; the other **24 of 33 scenes are byte-identical**.
  **sceneC2 is a CB-2 pilot** — whoever renders CB-2 after CB-3 lands is looking at CB-3's change
  as well, and should render CB-2's C2 pilot from a tree that already has CB-3.
- **The helpers may not be deleted yet.** They are retired to inert shims with a per-process counter,
  `batch1_common.JIT_LEGACY_CALLS`, and a one-time notice. When a full 33-scene assembly reports
  zero, S3 and S4 have finished and `jit_yaw`/`jit_pos` can be deleted outright.

The one **added** lint finding, and the only one, is the census reconciliation:
`LINT-7-static <all> census — measured 5 call site(s), 6 text hit(s), expected 24 / 25`, severity
WARN. It is unavoidable and correct: `Docs/briefs/placement_rules_v1.yaml` pins C-2's
pre-abolition inventory and is **T1's file**, so K2 may not edit it. It fires the moment any
removal lands, and it should be re-pinned to `0 / 1` by T1 once S3 and S4 close their 5 sites.

---

## 4. C6 bollard asset swap — PREPARED, NOT ADOPTED

§4.2 puts the K2 half of the C6 flip in this file. **Four independent gates say it may not be
switched on in this window**, so what landed is the route, its measurements and an `asset=` kwarg
that defaults **off** — scene-side values unchanged, geometry unchanged, prim hashes unchanged.

1. **Spec §5.3 hard dependency edge** — *"K4(c) prop templates → C6 asset swap in K2"*. K4(c) is
   WINDOW 2; K2 is WINDOW 1.
2. **Spec §3.1 C6 gate** — *"an A/B h0.3 crop (asset vs current) before adoption."* No such crop
   exists; CB-3's pilots are N3 and C1.
3. **`Docs/audit_v4/gt_changes_w3.md` §0-1** — a change to a hazard/collision box may not land
   before its ledger row exists. Swapping the body changes `build_bollard_v51`'s collider and
   `bollard_v51_aabbs`, and **there is no GT row for it**. The ledger is T5's file, not K2's, so
   K2 cannot open one.
4. **Spec §3.1 C6's own residual list** — *"base plate + anchor cover + impact-absorbing band
   material"* is prop-template work, i.e. K4(c) again.

### 4.1 A correction procurement's framing needs

Measured through `urban_kit` (usd-core, instance proxies expanded) against 교통약자법 시행규칙
별표2 제7호 (h 0.80–1.00 m, Ø 0.10–0.20 m) `[law]`:

| asset | Ø | bbox h | `zmin` | **exposed h at grade** | tri | verdict |
|---|---|---|---|---|---|---|
| `bollard_01` | 139.3 mm | 1002.8 mm | −182.6 mm | **820.2 mm** ✔ | 2,564 | PASS |
| `strt_fxd_bollard_05` | 133.0 mm | 844.9 mm | −53.9 mm | **791.0 mm** ✘ | 2,628 | PASS |
| `strt_fxd_bollard_03` | 207.1 × 297.4 mm | 721.3 mm | 0.0 | 721.3 mm | 5,984 | the deliberate 부적정 variant |

The procurement note reads both adopted rows as *"both in spec"*. That is true of the **bbox** and
false of the **installed** object: `urban_kit` places these at `z_mode="grade"` (local z = 0 is
street grade), so the exposed height is `zmax`, not the bbox height — and `strt_fxd_bollard_05`
then stands **791.0 mm, 9.0 mm below the 800 mm statutory floor**. `batch1_common.bollard_asset_lift()`
returns exactly that lift (`0.0090 m` for `_05`, `0.0` for `bollard_01`) and both the builder and
the AABB helper apply it, so the prepared route is compliant on adoption rather than 9 mm short.

A fifth, softer reason to wait: the raw asset carries **no reflective band**, which 별표2 제7호
requires. batch1's current procedural bollard is Ø120 × h900 — already inside the statutory band,
unlike `scene_common.build_bollard` (Ø120 × h750, 6.3 % below, spec §3.1 C6). **This flip buys
fidelity, not compliance**, so nothing is lost by waiting for its gates.

---

## 5. GATE-1 — pilots N3 · C1, and the FRAME adjudication

### 5.1 Method

Four renders, **13 cuts each** (the full `grid_views` list — the order-prefix rule taken literally:
render the whole prefix, discard the extras at judgement time, never truncate, because PT/DLSS
accumulation carries frame history). Channel identical to the frozen judge round:
`NEGOBS_CAPTURE_MODE=pt · NEGOBS_PT_FAST=1 · NEGOBS_LOOK_V1=1 · NEGOBS_DETAIL_SCALE=2 ·
NEGOBS_DETAIL_ROUGH_GAIN=0`. GPU exclusive under `flock -w 7200 /tmp/negobs_gpu.lock`, sequential,
one process per scene, 54–59 s per scene.

Round dirs `look_check/_experiments/gates/<scene>/260731_w3_cb3{,_base}/` — a two-arm gate probe is
**not** a judgement grid, and `look_check/README.md` §1 says gate probes never go to the scene root.

**Both arms were rendered by this WP**, from **isolated trees**, because a concurrent K1 agent is
mid-edit on `ground_kit.py` (`147 insertions`, and at one point a transient
`NameError: yaw_max` that broke whole-tree assembly for 25 scenes). Every number in this report was
produced in a tree pinned to HEAD for every file except this WP's own eight — so the deltas are
attributable to CB-3 and to nothing else. The isolated HEAD baseline reproduces the real tree's
lint totals exactly (393 / 385 / 29 / 2), which is what validates the isolation.

### 5.2 Results

| pilot | verdict | issue codes over 13 cuts |
|---|---|---|
| **sceneC1** | FAIL 0 · WARN 0 · INFO 3 · PASS 10 — **회귀 없음** | `WHITE` ×3 (이월, pre-existing) · `CAPTURE` ×1 |
| **sceneN3** | FAIL 2 · WARN 4 · INFO 3 · PASS 4 | **`FRAME` ×6 · `CAPTURE` ×4 — nothing else** |

Of §7.2's five regression classes (DARK / BLOWN / WHITE / OCCL / FRAME), CB-3 moves **exactly one**,
on **one** pilot. **Zero** DARK, **zero** BLOWN, **zero** OCCL anywhere.

### 5.3 Is the FRAME movement render noise? No — measured

Control arm: HEAD code re-rendered in a new session versus the published `260730_w2d_fix` round.

| control | result |
|---|---|
| sceneC1, HEAD vs published | FAIL 0 · **12 of 13 cuts `UNCHANGED`** (bit-identical) |
| sceneN3, HEAD vs published | FAIL 0 · WARN 2 (`UNCHANGED`) · PASS 7 · INFO 4 |

The renderer is deterministic and the noise floor produces **no FRAME FAIL**. The N3 movement is
therefore caused by the code change, and the question becomes *which part of it*.

### 5.4 What actually moved — prim-level attribution

`sceneN3`: **59 of 673 prims changed; 673 → 673, not one prim created or destroyed.** The 59 are
exactly the 4 benches and the 4 planters with their children:

```
- /World/Scene23/Bench_A|Xform|T=(-2.132959, 3.579199, 0.0);RZ=-5.122067||
+ /World/Scene23/Bench_A|Xform|T=(-2.0, 3.5, 0.0)||
```

The `RZ` op is **gone** and the translate is exactly the nominal PARAMS coordinate — which is
precisely CB-3's acceptance test (§7.2: *"Furniture reads as a single line parallel to its anchor;
no object off its anchor bearing"*). `sceneC1`: **12 of 374** prims changed — 2 benches + 10 lamp
prims, no vegetation, which is why C1 came back clean.

### 5.5 The real cause of the N3 FRAME FAILs — a coupling the fleet must know about

Pixel forensics put the change in the **top** of the frame, not at bench height: on
`preset_h0.3_d5`, 85,203 of 89,000 changed pixels sit in the **top sixth** and essentially none
below the second sixth. Benches at a 0.3 m eye height are not in the top sixth. Trees are.

The inventory diff names the mechanism:

```
- /World/Scene23/Planter_A/Veg/Asset|Xform|||Shumard_Oak.usd
- /World/Scene23/Planter_A/Veg|Xform|T=(-4.436054, 3.508683, 0.38);RZ=116.879541;S=(0.30654,…)||
+ /World/Scene23/Planter_A/Veg/Asset|Xform|||Chinese_Juniper.usd
+ /World/Scene23/Planter_A/Veg|Xform|T=(-4.5, 3.6, 0.38);RZ=193.504843;S=(1.443922,…)||
```

`build_tree`'s **species draw is seeded from the planter's coordinates**. Moving the planter back
to its nominal centre re-rolls the draw: a different species asset at a different scale
(**0.307 → 1.444, 4.7×**, because the scale solves for a target height against the species' native
height). The same happens to `place_shrubs`' per-shrub yaw and scale draw. That, not the bench
nudge, is what repaints 14.6 % of `preset_h1.8_d10`.

Species census delta, from LINT-4's own instrument — **totals conserved in every scene**, only the
draw changes:

| scene | HEAD | CB-3 |
|---|---|---|
| sceneN3 | Rhododendron ×6 · Shumard_Oak ×2 · Juniper ×2 · **White_Pine ×1** · Elm_Sapling ×1 | Juniper ×5 · Rhododendron ×3 · Chinese_Juniper ×1 · Elm_Sapling ×1 · Yellow_Pine ×1 · Shumard_Oak ×1 |
| sceneN2 | Juniper ×3 · Chinese_Juniper ×1 · Elm_Sapling ×1 · Rhododendron ×1 | Juniper ×3 · Chinese_Juniper ×2 · Rhododendron ×1 |
| sceneC4 | Rhododendron ×8 · Juniper ×4 | Rhododendron ×6 · Juniper ×6 |
| **sceneN5** | Rhododendron ×4 · Elm_Sapling ×2 · Yellow_Pine ×2 · Shumard_Oak ×1 · Juniper ×1 | Rhododendron ×3 · Elm_Sapling ×2 · Yellow_Pine ×2 · Juniper ×2 · Shumard_Oak ×1 |

`sceneN5` is in that table although CB-3 does not edit it — the library-wide flip reaches it
through its residual call site (§3).

**Adjudication.** The FRAME movement is (a) the intended furniture re-alignment plus (b) a
**transient** re-roll of a species draw that spec §1.3-5 has already ruled must be **deleted**:
*"remove the per-tree and per-shrub species draw"* (S-1…S-4, K4(b), WINDOW 2). Judging N3's
vegetation against these frames is pointless — K4(b) replaces the draw with a deterministic
per-scene table and will move it again. The furniture, which is what CB-3 is gated on, is
verifiably on its anchor bearings at its nominal coordinates.

**Standing warning for every S-WP**: until K4(b) lands, **moving any planter, bed or tree
coordinate by any amount re-rolls that bed's species and shrub draw**, and the frame change will be
dominated by the vegetation, not by the thing you moved. Do not read a FRAME FAIL as a defect
without a prim-level diff.

---

## 6. Instruments and reproduction

```bash
# CPU pre-flight
python3 -m py_compile scenes/batch1/batch1_common.py scenes/batch1/scene{N1_shadow_band,\
N2_asphalt_patch,N3_trompe_loeil,C1_snow_stairs,C4_wet_stairs,D2_floor_opening,D4_subway_platform}.py
python3 scripts/geom_invariance_check.py                       # 33/33 · 33/33
python3 scripts/placement_lint.py --scenes all --rules Docs/briefs/placement_rules_v1.yaml
NEGOBS_GEOCHECK=1 python3 scenes/batch1/sceneN1_shadow_band.py  # and N2, N3

# GATE-1 (GPU exclusive; C1/C4/D2/D4 have no GEOCHECK entry point)
flock -w 7200 /tmp/negobs_gpu.lock bash <runner>                # 4 arms x 13 cuts, PT_FAST
python3 scripts/regression_check.py \
  --before look_check/_experiments/gates/sceneN3/260731_w3_cb3_base \
  --after  look_check/_experiments/gates/sceneN3/260731_w3_cb3
```

Advisory note (§6.3): `ori_axis` was **not** used as a gate and is not reported as one. Spec §6.3
asks for a before/after measurement across the abolition batch; the meaningful reading is over the
whole 33-scene round at GATE-2, not over two pilot scenes, so it is left to X1/X2 with the flag that
removing jitter is expected to push it **up**, and that a post-batch median above p95 0.371 means
**under-dressed**, not "re-rotate the furniture".

---

## 7. Handoffs

| # | To | Item |
|---|---|---|
| H-1 | **S3 / CB-2** | `sceneC2_leaf_stairs.py:801,802,821,837` — 4 inert `bc.jit_*` calls to delete. Benches/bins/lamps take their anchor bearing; C2's prim hash **already moved** in CB-3, so its CB-2 pilot must be rendered from a tree containing CB-3 |
| H-2 | **S4** | `sceneN5_flush_grating.py:386` — 1 inert `bc.jit_pos` to delete (planters). N5's prim hash already moved |
| H-3 | **T1** | Re-pin `placement_rules_v1.yaml` `LINT-7-static` from `expected_call_sites: 24 / expected_text_hits: 25` to `0 / 1` once H-1 and H-2 land. Until then the census WARN is expected, not a defect |
| H-4 | **K2 successor / K4(c)** | Delete `jit_yaw` and `jit_pos` outright when a 33-scene assembly reports `JIT_LEGACY_CALLS == {0, 0}` |
| H-5 | **K4(c) + T5** | Adopt the C6 bollard route: flip `asset=BOLLARD_ASSET["primary"]`, add the base plate / anchor cover / reflective band, **open a GT row first** (collision box change), and run the §3.1 A/B h0.3 crop |
| H-6 | **K4(b)** | The species-draw coupling in §5.5. Also `White_Pine` was live in sceneN3 at HEAD and spec §1.3-1 retires it — CB-3 happened to drop it by re-roll, which is luck, not a fix |
| H-7 | **S8 (note only, untouched)** | OQ-1 — `sceneD2:929` sack yaw and `:881/:902` batten bearings are S8 scope and were not touched. Adjacent, also untouched, also not in §10.1's inventory: `sceneD2:301 formpanel_xs` uses `bc.jit_scalar` for ±0.16 m **placement** jitter on 3 formwork panels. `jit_scalar` is out of CB-3's scope by §10.1; if placement jitter via `jit_scalar` is meant to fall under J-4, that is a spec widening, not an implementer's call |
| H-8 | **X1 / whoever renders next** | `look_check/_experiments/gates/scene{N3,C1}/260731_w3_cb3{,_base}/` are stamped and available as the CB-3 A/B pair |

---

## 8. Do-not-touch compliance

§12-6 tactile not switched on and no pad added under a bollard — the prepared asset route keeps
the existing `tactile=` toggle and adds nothing. §12-14 instanceability respected — the prepared
asset route passes `instanceable=True`. §12-15 `jit_tint` untouched. §12-13 sceneD4's worn tactile
strip untouched. `assets/`, `scripts/rounds/`, `placement_rules_v1.yaml`, `gt_changes_w3.md`,
`geom_invariance_check.py`, `regression_check.py` — read only, never written.
