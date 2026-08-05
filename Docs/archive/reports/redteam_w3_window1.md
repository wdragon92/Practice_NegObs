# Red team — W3 WINDOW 1 exit gate (CB-2 · CB-3 · CB-4)

> **Wave**: W3 · **Kind**: adversarial verification, window exit · **Date**: 2026-07-31
> **Branch**: `feat/realism-v1` · **Window base**: `d7494f4` · **Commits audited**:
> `10b3946` (CB-3, 13:19) · `c2676d6` (CB-4, 13:27) · `11d1e56` (CB-2, 13:35) ·
> `0ca16d7` (docs-only intake appendix, landed mid-verification, +15 lines in one survey file — no code effect)
> **Method**: every self-check and the linter re-run on the live tree; a **pristine `d7494f4`
> worktree** rebuilt for the whole-window A/B; every pilot regression re-run from the stored
> rounds; pilot crops viewed; GT-9 recomputed from the manifest, the fixture **and the shipped
> 33-scene assembly**; the new `building_kit` check revert-tested twice (genuine-HEAD prover +
> an independent −5 mm mutation).

---

## 0. Verdicts

| Target | Verdict | One line |
|---|---|---|
| **CB-2** (K1 `ground_kit` + S3 F3 scenes) | **CONFIRMED** — with 3 census/stamp corrections (§4) | Every gate re-run green; LINT-8 295→0 exact; decals read organic in the crops; GT-9 mechanism correct and shipped-verified |
| **CB-3** (K2 `batch1_common` + S7/S8 sites) | **CONFIRMED** | Flip + 19-site removal verified in code and lint; N3 FRAME movement reproduced and correctly attributed; C6 rightly withheld |
| **CB-4** (K3 `building_kit`/`facade_kit`) | **CONFIRMED** | 180/180; RED-before/green-after independently proven; kit-swap A/B: 33/33 prim hashes identical (unwired); pilots at noise floor |
| **WINDOW 1 exit (§5.1)** | **MET, with adjudication** | All three GATE-1 pilots rendered, stamped, regression-clean except N3's 2 FRAME FAILs = the intended furniture movement + the already-ruled-dead species re-roll (§3.2) |
| Exit-gate expectation "LINT-7-static must be 0" | **NOT met numerically — 5, all inert** | 4 sites are S3's own file (H-1 was on the table when CB-2 committed); 1 is S4/CB-10 (§5.1) |

Ownership audit: `git diff d7494f4..11d1e56 --name-only` = exactly the union of the three
commits' pathspecs (22 files). No do-not-touch file moved: `scene_common.py`, `stair_kit.py`,
`variation_kit.py`, `infra_kit.py`, all of `scripts/` (incl. `scripts/rounds/` — X1's dir has
no new files), `placement_rules_v1.yaml`, and the procurement files are byte-identical to
`d7494f4`. Working tree clean; all three commits are pathspec-scoped (each `--stat` contains
only its own WP's files).

---

## 1. Instruments re-run on the live tree — all green

| Instrument | Result | Matches the reports? |
|---|---|---|
| `python3 ground_kit.py` | exit 0 · 「전 항목 통과」 33/33 | ✓ |
| `python3 building_kit.py` | **180/180** + 33-scene scan | ✓ (was 135/135) |
| `python3 scripts/geom_invariance_check.py` | R-4 **33/33** · R-6 **33/33** | ✓ |
| `python3 scripts/placement_lint.py --scenes all --rules …` | exit 1 · **79 E / 359 W / 29 B / 2 I** | ✓ |

### 1.1 Whole-window lint A/B — pristine baseline rebuilt, zero added findings

The three CB reports each isolated their own delta; nobody had measured the **window as a
whole** against a pristine base. Done here: a detached worktree at `d7494f4` (gitignored
assets symlinked in) reproduces T1's committed baseline **exactly** — `393 E / 385 W / 29 B / 2 I`,
LINT-8 = 295, LINT-7-static = 24 E, LINT-7 dynamic = 144 W.

| check | `d7494f4` | now | Δ | owner of the delta |
|---|---|---|---|---|
| **LINT-8** | 295 E | **0** | **−295** | CB-2, documented |
| **LINT-7-static** | 24 E / 0 W | **5 E / 1 W** | −19 E, +1 census WARN | CB-3, documented |
| **LINT-7** (dynamic) | 144 W | 117 W | −27 | CB-3 behaviour flip, documented |
| LINT-1/2/3/4/4b/5/6/9/10/PLACEMENT | — | — | **byte-equal counts, same scene sets** | no one |

**393 − 295 − 19 = 79 exactly.** LINT-10's 6 warnings (incl. both `sceneC2` lines) pre-exist at
the baseline — CB-2's scene edits added none (the report's `sceneD3:198` is now `:201`, line
drift from its own edit; cosmetic). **No CB added a single finding beyond its documented delta.**

---

## 2. Pilot regressions — all re-run by this red team from the stored rounds

| Arm | My re-run | Report claims | Match |
|---|---|---|---|
| CB-2 `scene01` w2d_fix→cb2 (5 cuts) | FAIL 0 · WARN 1 `UNCHANGED` | same | ✓ |
| CB-2 `scene03` | FAIL 0 · WARN 1 `UNCHANGED` | same | ✓ |
| CB-2 `scene07` | FAIL 0 · WARN 4 **FRAME** | same | ✓ |
| CB-2 `sceneC2` | **5/5 PASS** | same | ✓ (but not in the stamp JSON — §4.3) |
| CB-3 `sceneC1` base→cb3 (13 cuts) | FAIL 0 · WARN 0 · INFO 3 (WHITE ×3 carried, CAPTURE ×1) | 회귀 없음 | ✓ |
| CB-3 `sceneN3` base→cb3 | FAIL 2 · WARN 4 · **FRAME only**, DARK/BLOWN/OCCL = 0 | same | ✓ |
| CB-4 `scene20` w2d_fix→cb4 | FAIL 0 · WARN 1 · INFO 2 · PASS 2 | same | ✓ |
| CB-4 `scene21` w2d_fix→cb4 | FAIL 0 · WARN 2 FRAME (22 % dev 95/255 · 13 % dev 85/255) | same, attributed to CB-2's in-flight ground work | ✓ |
| CB-4 ctl→cb4, 20 & 21 | FAIL 0 · `UNCHANGED` 0.07–0.43 LSB · **block movement 0 on 10/10** | same | ✓ |

Round hygiene: CB-3/CB-4 probes live under `_experiments/gates/` (correct — gate probes);
CB-2's rounds sit at the scene root, which the README licenses **because they are the new
baselines-of-record** (GT-8). Stamps verified: C2's `round_stamp.json` reads `git_head 10b3946`
→ the C2 pilot was rendered from a tree **already containing CB-3**, exactly as CB-3's H-1
demanded; scene07's reads `c2676d6` with `NEGOBS_VIEWS` = the exact 5-cut `grid_views` prefix
(order-prefix rule honoured). CB-3's arms were rendered at `d7494f4` + 13 dirty files = the
isolated tree its report describes.

---

## 3. Eyes — pilot crops viewed

### 3.1 CB-2 (scene07 · sceneC2)

- **scene07 `h0.3_d5`**, W2 vs CB-2: the three stacked-rectangle leaf carpets and the mid-frame
  ghost rectangle are **gone**; the same masses are irregular lobes with individual feather
  cards at the boundary. Zero decal straight edges that are not joints/saw cuts.
- **scene07 `h0.3_d2`**: the near yard carpet is an organic lobe. Nit, not a gate breach: at
  ~1 m the 24-gon **chord segments are faintly readable** on the left indent — if 통람 v3
  flags it, raise `n` or feather density for near-field masks (cosmetic knob, K1).
- **sceneC2 `h0.3_d2`**, W2 vs CB-2: the report undersold its own fix — the delta **is**
  visible here. Pixel diff localises it to the far bed's exposed vertical band (rows ≈344–349):
  plan-view leaf photograph → constant `leafsec` section skin. The pressed-leaf-laminate read
  on a vertical face is gone; mound geometry untouched (5/5 PASS, no block movement).

### 3.2 CB-3 (sceneN3 · sceneC1)

- **`beauty_overview` base vs cb3**: every bench sits at its nominal coordinate, seat axis
  parallel to its planter/hedge face — the §7.2 criterion, visible. The top-of-frame repaint is
  the **planter vegetation re-rolling** (different species/scale per planter), i.e. the
  coordinate-seeded draw `scene_common.py:2442` documents and spec §1.3-5 already orders K4(b)
  to delete. CB-3's FRAME adjudication is **endorsed after independent reproduction**: 0 DARK /
  0 BLOWN / 0 OCCL, movement top-sixth, totals conserved.
- **Bollards**: nothing about them changed this window — correct. batch1's shipped procedural
  bollard is `BOLLARD_V51` Ø0.12 × **h0.90** (statutory 0.8–1.0 / Ø0.1–0.2); the C6 asset swap
  is prepared, default-off, with `bollard_asset_lift()` = +9.0 mm for `strt_fxd_bollard_05`
  (which would otherwise install at 791 mm, sub-statute). The known sub-statute prop remains
  `scene_common.build_bollard` h750 — K4(c)/WINDOW 2 scope, untouched here as ordered.

### 3.3 CB-4 (scene20 · scene21)

Numerically at the noise floor (ctl→cb4 `UNCHANGED`, block 0) — the pilot proves **no
accidental wiring**, which is what the batch owed. Windows becoming visible is the BS-2
adoption gate's deliverable, not CB-4's.

---

## 4. GT ledger — GT-8 / GT-9 landing records

**GT-8**: landed as recorded. My baseline A/B reproduces the exact totals in the record
(374→79 within the same tree instant; 393→79 across the window). `regr_260730_w2d_fix.json`
retired; new stamp `regr_260731_w3_cb2.json` exists.

**GT-9 mechanism — CONFIRMED at every number I could recompute independently:**

| Claim | Independent check |
|---|---|
| native `zmax` 0.1229 · footprint (0.2789, 0.3044) | `veg_manifest_w2.json` `size_m [0.2789, 0.3044, 0.125]`, `zmax_m 0.1229` ✓ |
| ceiling scale 0.12/0.1229 = **0.9764** → exposure 0.1200 | arithmetic ✓ |
| fixture census **85 / 13** · **25 clamped, 0 dropped** · fixture max **0.1182 (scene13)** | reproduced from `_fixture_plan` over all 33 (`clamped_from` meta ×25) ✓ |
| `_elem` aabb from the scaled bbox, both plan dims | `ground_kit.py:2377` (`hx, hy` from `WEED_ASSET_XY[0/1]`), `:3310-3312` ✓ |
| h ≤ 0.12 **on the shipped tree** (the condition that keeps class A) | **verified by me on the assembled 33 scenes**: 81/81 shipped weeds reference `Grass_Short_C.usd`, max shipped exposure **0.1174 m** (`sceneN2`) ✓ |

**Corrections the ledger should absorb (bookkeeping, no GT action — the clamp is
per-instance and holds shipped-side):**

1. **The census in the record is fixture-only, and the shipped tree disagrees more than W7
   admits: shipped = 81 instances / 12 scenes** (03 and C2 override their surface rows to zero
   weeds; D3 overrides to 8, not the fixture's 4; **scene18 keeps 6** — next row). The record's
   "largest height actually shipped 0.1182 (scene13)" is likewise the **fixture** figure;
   shipped scene13 max is 0.1023 and the shipped library max is 0.1174 (`sceneN2`).
2. **W6's "removes 9 × 6 = 54 instances" lands as 48 on the shipped tree.** `scene18` calls
   `plan_ground("plaza_granite", …, overrides=dict(surface=(("patch", 3), …, ("weed", 6))))`
   (`scene18:831-836`) — a scene-side override that the profile-row deletion cannot reach. Of
   the nine `plaza_granite` scenes, **eight ship −7 prims exactly** (measured: 01 361→354 · 05 ·
   14 · 20 · 21 · C1 · N1 · N3 all −7); **scene18 ships +6** (its 6 weeds convert cube→asset at
   +1 prim each; patches stay 3). If A1's "no weeds in a maintained plaza" is meant to reach
   scene18's waterside art stair too, that is an S6 scene edit, not a `GROUND_PROFILES` tuple —
   but scene18's weeds/efflorescence were deliberate W2-D authoring, so more likely W6 just
   needs its arithmetic annotated.
3. Prose nit: "footprint 0.2723 m" is the **x** dimension only; y at ceiling scale is 0.2972 m.
   The registry uses both dims (code cited above), so nothing downstream is wrong — but the
   ledger number should not be quoted as *the* footprint.

**GT-12**: correctly **not** live — kit unwired, and my kit-swap A/B (below) proves zero
geometry effect, so no OCCL re-check is owed yet. Becomes live at BS-2 adoption.

---

## 5. Findings

### 5.1 LINT-7-static is 5, not 0 — and 4 of the 5 were deletable in this window

`sceneC2_leaf_stairs.py:867/868/887/903` (×4, **S3's file**) and `sceneN5_flush_grating.py:386`
(×1, S4). All five are **inert** (shims return `base` / `(0,0)`; proven by the −27 dynamic
WARNs and by C2/N5's prim movement under the flip). CB-3's ownership argument for not touching
them is valid. But **CB-2 committed S3's own `sceneC2` at 13:35, sixteen minutes after CB-3's
H-1 handoff landed in-tree, and left the four calls in place** — its report does not mention
them. Nothing broke; the exit-gate expectation "LINT-7-static must be 0" is simply not met
numerically. **Action**: S3 deletes 4 lines at its next C2 touch (CB-10 at the latest); S4
deletes 1; then T1 re-pins `expected_call_sites/text_hits` 24/25 → 0/1; then K2 deletes the
shims when `JIT_LEGACY_CALLS == {0,0}` on a 33-scene assembly.

### 5.2 `regr_260731_w3_cb2.json` omits sceneC2

The committed stamp holds 3 pairs / 15 results (01·03·07 only). C2's "5/5 PASS" exists only in
report prose — and this JSON is the **baseline-of-record stamp** GT-8 points at. My re-run
confirms C2 5/5 PASS vs `260730_w2d_fix`, so the fact is right; the record is short one scene.
**Action**: K1/X1 re-emit the stamp with the C2 pair before anything compares against it.

### 5.3 The new baselines-of-record are 5-cut rounds

`260731_w3_cb2` has 5 cuts; the retired `260730_w2d_fix` has 13. A naive 13-cut GATE-2
comparison against the new baseline will emit **8 MISSING FAILs per pilot scene** (verified:
that is exactly what `regression_check` does without `--only`; the comma fallback selects
whole rounds, it does not mix per-cut). **Action**: X1's GATE-2 runner must either compare the
5 preset cuts against `260731_w3_cb2` and the rest against `260730_w2d_fix` explicitly, or
stamp the GATE-2 round as the fresh full baseline in one step — and say which in the stamp.

### 5.4 `look_check/INDEX.md` is stale

README: "the only committed record of what actually exists on the render machine … regenerate
whenever rounds are added." None of `260731_w3_cb1/cb2/cb3/cb4(+ctl)` is listed. **Action**: X1.

### 5.5 Notes, no action owed

- **CB-2 wrote 3 sections of T5's ledger** (GT-9 §3 row amendment with strikethrough, §4
  landing records, §7 W6/W7). The ledger's own §0-1/§4 protocol orders exactly this from the
  owning WP, so it is sanctioned; recorded because §4.1's file-ownership table says the
  opposite in general.
- **`ori_axis` before/after (§6.3)** was not measured over the abolition batch — CB-3's
  deferral to GATE-2 is accepted (two pilot scenes are not the population §6.3 describes), but
  the obligation now sits with X1/X2 and should be in the GATE-2 checklist.
- **B-F7** (office curtain wall 1.255 m proud of its tower above the podium) — pre-existing,
  confirmed as recorded-not-implemented; belongs to BS-2.
- Residual lint debt is all pre-assigned: LINT-4b 49 E → K4(b) · LINT-6 25 E → K4(c)/K2/S1 ·
  LINT-9 29 BLOCK → P-7 evidence (correctly still WARN-mode).
- scene07's parked-archetype knob (P-1) and scene10's `broken_landing=0` (P-2) are intact.

---

## 6. Revert-tests of the new `building_kit` check — it bites

1. **Genuine-HEAD prover**: `prove_prefix_fail.py` runs the shipped `[11]` algorithm against
   `building_kit.py`/`facade_kit.py` blobs **md5-equal to `git show d7494f4:`** →
   **73 burial pairs / 109 visible-role prims** on the standard grid, **712** on the W×base_z
   sweep, per-element margins matching the report table (Win −0.080 ×40 · ShopGlass −0.100 ×12 ·
   FireMark **−0.588** ×8 · WinBand −0.100 ×6 · CoreStrip −0.030 ×3 · EntryGlass −0.070 ·
   CurtainGlass −0.075). RED-before is real.
2. **Independent mutation of the shipped suite** (not the prover's re-implementation): flipping
   one constant, `WALL_PROUD 0.005 → −0.005`, in a copied pair and running `python3
   building_kit.py` → **exit 1, 10 checks fail**, `[11]` reports 17 + 212 burial pairs and
   catches margins as small as **−1 mm** (`FireMark_0_2 … -0.001`). The check is
   millimetre-sensitive on the live code path, not just on the historical geometry.
3. **Unwired proof, strongest form**: detached worktree, only `building_kit.py` +
   `facade_kit.py` swapped to `d7494f4` blobs, `geom_invariance_check` re-run → per-scene prim
   hashes **identical 33/33** to the live tree. CB-4 changes no assembled geometry anywhere.

---

## 7. Reproduction

```bash
# instruments (live tree)
python3 ground_kit.py && python3 building_kit.py && python3 scripts/geom_invariance_check.py
python3 scripts/placement_lint.py --scenes all --rules Docs/briefs/placement_rules_v1.yaml

# whole-window lint A/B (pristine base; symlink gitignored assets into the worktree first)
git worktree add --detach <scratch>/wt d7494f4 && cd <scratch>/wt && ln -s <repo>/assets/... assets/...
python3 scripts/placement_lint.py --scenes all --rules Docs/briefs/placement_rules_v1.yaml   # 393/385/29/2

# pilot regressions (no GPU — images already on disk)
ONLY=preset_h0.3_d2,preset_h0.3_d5,preset_h0.3_d10,preset_h0.9_d2,preset_h0.9_d5
python3 scripts/regression_check.py --before look_check/<sc>/260730_w2d_fix --after look_check/<sc>/260731_w3_cb2 --only $ONLY   # 01 03 07 C2
python3 scripts/regression_check.py --before look_check/_experiments/gates/<sc>/260731_w3_cb3_base --after .../260731_w3_cb3     # N3 C1
python3 scripts/regression_check.py --before look_check/_experiments/gates/<sc>/260731_w3_cb4ctl  --after .../260731_w3_cb4     # 20 21

# GT-9, fixture and shipped
python3 -c "import ground_kit as gk; ..."           # _fixture_plan weed dump: 85/13, 25x clamped_from, max 0.1182
# shipped: geom_invariance run_arm(dump=True) over all 33 -> 81 weeds / 12 scenes, all Grass_Short_C, max 0.1174

# building_kit bite
cd <scratch> && python3 prove_prefix_fail.py         # 73 + 712 on md5-verified HEAD blobs
sed -i 's/^WALL_PROUD = 0.005/WALL_PROUD = -0.005/' <copy>/facade_kit.py && python3 <copy>/building_kit.py  # exit 1
```
