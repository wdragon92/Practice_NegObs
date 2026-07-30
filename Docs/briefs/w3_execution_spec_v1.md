# W3 Execution Spec v1 — the single implementation source

> **Wave**: W3 · **Kind**: execution spec (this is what the W3 fleet builds from) · **Date**: 2026-07-30
> **Branch**: `feat/realism-v1` · **Repo state**: HEAD `8451eb5` (procurement) on top of `effe59e` (intake)
> **Authority**: this document **supersedes** the intake/survey documents wherever they disagree.
> Where a source row is corrected here, the correction is stated with the source ID so the
> original is still greppable.
>
> **Merged from**: `Docs/surveys/w3_intake_01_05.md` (A) · `Docs/surveys/w3_intake_06_10.md` (B) ·
> `Docs/surveys/w3_intake_policy.md` (C) · `Docs/reports/redteam_w3_intake.md` (RT-I) ·
> `Docs/surveys/w3r_asset_map_v1.md` (survey R1) · `Docs/surveys/w3r_prop_mapping_v1.md` (survey R2) ·
> `Docs/surveys/w3r_building_ab_v1.md` (survey R3) · `Docs/reports/redteam_w3r.md` (RT-R) ·
> `Docs/reports/tonglam_v2.md` (eyes) · `Docs/surveys/era_consistency_survey_v1.md` §5/§6.2 ·
> `Docs/reports/w3_procurement_v1.md` (PROC) + `assets/urban_manifest_w3.json`.
>
> **Ruling tags**: `[ruled 07-30]` = a supervisor ruling relayed into this wave. It is binding and
> it overrides any source document, including a published PASS verdict.
>
> **Scope discipline**: no agent may edit a file it does not own in §4. `assets/download_urban.py`,
> `assets/verify_urban.py`, `assets/urban_manifest_w3.json`, `.gitignore` and
> `Docs/reports/w3_procurement_v1.md` belong to the procurement agent and are **read-only for
> everyone in W3**.

---

## 0. How to read this document

§1 is the ruling set. §2 is the corrected-facts ledger — **every number the sources got wrong**,
with the value you must use instead. §3 is the asset-first re-adjudication. §4 is the work-package
table with file-disjoint ownership. §5 is the freeze-window and commit-batch order. §6 is the
per-WP verification obligation. §7 is the render-gate plan. §8 is the GT ledger. §9 is the parked
register. §10 is the merged spec-row index. §11 is the label-collision map — **read it before you
grep**, because five ID namespaces overlap across the sources.

**One rule above all others.** The W3 bar is the user's: *"실제 표본 확인해서 똑같게"* — not
"plausible". A row is shippable when it names the real sample it reproduces. A row whose sample
does not exist yet is **parked** (§9), not guessed.

---

## 1. Standing rulings

### 1.1 Asset-first doctrine `[ruled 07-30]`

> Re-adjudicate survey R2's 20 `rebuild-procedural` rows. **The asset route wins unless the Korean
> archetype is clearly broken at h0.3.**

Executed in §3, on measured millimetres from `assets/urban_manifest_w3.json`, not on catalogue
claims. Outcome: **6 rows move toward assets, 14 stay procedural with the failing dimension
recorded, 7 new asset rows appear that R2 did not have.**

### 1.2 Jitter `[ruled 07-30]`

> Abolish the 13. Fix the footprint-AABB bug. Facade AC-unit jitter = **KEEP** (real-world irregular
> per-unit installs) and document it. KEEP-class additions from RT-R stand.

- The abolish list is the **full 13-row inventory** of C §3.2(a). This **resolves C §10-Q7 against
  the ±2.5° dissent**: sceneD1's stacked crates go to the dock-edge bearing, not to a capped
  wobble.
- J-7 (`build_footprints`) **keeps** its ±6° splay; only the AABB is fixed to use the jittered
  angle (C §3.6 — a genuine registry/geometry divergence that `geom_invariance_check` cannot see
  because both arms produce the same wrong number).
- `facade_kit.py:563` AC-unit u-offset `U(−0.35, +0.35)` → **KEEP**, with a docstring stating the
  reason (per-unit installs follow room layouts, so they really are irregular). This closes RT-R
  §4-N1 and makes C's "complete inventory" claim true.
- `facade_kit.py:840` gas-valve z `U(*GAS_VALVE_Z)` → **KEEP** (it already carries a stated real
  basis: floor +1.6–2.0 m).
- KEEP-class additions from RT-R §4-N2, all to be listed in the inventory so nobody "fixes" them:
  `scene12:1277` riprap rock yaw `U(0,90)` · `sceneD2:726` debris `rotz U(0,90)` ·
  `scene17:599-604,1108-1116` far-hedge clump spacing/position · `scene09:1368-1369` reed spread ·
  `scene11:1448` distant tree-band `dx` · `ground_kit:1289` / `infra_kit:802` manhole flush ±10 mm
  (KS D 4040 tolerance — a justified keep, not an oversight).
- Also KEEP, already adjudicated: J-8 scatter jitter · J-9 `build_tree` lean/canopy/yaw ·
  J-10 `jit_tint` (explicitly out of scope) · J-14 `build_worn_stone_stairs(jyaw=3.0)` ·
  J-11 keep-at-zero params (`infra_kit:403/531`, `ground_kit:607`) with a lint ban on non-zero.
- **X2 resolved**: scene04's verge generator splits — keep `jit_scale` and `skip` (within-species
  variation and real gaps), drop `jit_pos` and `swap` (placement). A's finer ruling wins; C §3.2(b)
  row 13 is annotated, not adopted whole.
- **X4 resolved**: J-6 regularises **street rows only** (06 · 11 · 12 · D3 · N5). scene13's 8 trees
  are apartment-court landscaping, not a street row — a blanket 7.0 m pitch there would be its own
  realism error under the match-the-sample bar. scene13's planting goes to the `sidewalk_local` /
  apartment archetype panel for photo-based treatment (§9 P-6 adjacent).
- **scene03 city blocks** (J-5 row 8) are not furniture: abolish the ±4° decorative wobble but
  **re-author** each block to a stated street-grid bearing. The output is not 0°.

### 1.3 Species `[ruled 07-30]`

> One-species-per-scene table = C's mechanism + A's assignments, with their conflict resolved.
> Deterministic within-species variation only.

Resolution rule, applied in §10.2:
1. Asset base = **C's `VEG_SPECIES`, manifest-PASS rows only**. `White_Pine` / `Yellow_Pine` are
   retired from route and belt roles (neither is in `veg_manifest_w2.json`'s PASS list;
   `White_Pine` carries an uncorrected `zmin −0.351`). Every A row naming them is re-mapped.
2. Where A and C name different PASS species for the same route, **C governs** — its table is
   derived from the manifest's own `role` field and is library-wide.
3. A second species inside one scene is admissible **only** as a physically separate planting
   (a mountain belt, a far bank) — marked `▸`. C §10-Q2 is answered **yes**, bounded by the
   statutory break rule: a species change must be caused by a **route event**
   (「도시숲·생활숲·가로수 조성·관리 기준」 2-3 가: *"도로의 방향이 바뀌거나 도로가 신설·확장되는 경우"*).
4. **scene02's species row is DELETED** (RT-I R7): scene02 has **no `build_tree` call**. The row
   either hallucinated existing trees or silently proposed new planting; neither ships.
5. "Deterministic within-species variation only" = keep the existing coordinate-seeded height/form
   variation; remove the per-tree and per-shrub **species draw**. No new stochastic levers.

### 1.4 Manholes `[ruled 07-30]`

> KDS utility-line rule. **Zero-manhole scenes are ACCEPTED** — no artificial scale-anchor
> substitute. The near-window device is **retired everywhere, including the pilots**.

This answers A §9-Q6 with a "no": several scenes correctly drop to zero manholes and must not gain
a replacement prop to keep a near-field scale anchor. The near-window occupancy check survives only
as a **render-composition assertion that may reject a position and may never produce one**, and the
same retirement applies to the "near-window filler" rationale wherever it selected a patch or crack
coordinate (`scene05:116-119`, `scene08:166`) and to the scene15 M9-b pilot construction itself.

### 1.5 scene02 `[ruled 07-30]`

> ~~Canopy **Option A** (none — era-consistent, and it differentiates scene02 from scene16's
> Option-B form).~~ → **SUPERSEDED: Canopy Option B — BUILD a full-length, enclosed, soffit-lit
> canopy** `[supervisor amendment 07-31 · micro-docs batch §14 MD-1]`. **Statutory flood sill**
> (18 cm × 1–3 steps) — GT-affecting → `gt_changes` ledger
> + re-cache at its render gate. **Curb shape fix.** **DELETE the stale landing docstring
> proposal** (cancelled by the era-survey W4 re-ruling).

> **Amendment MD-1 `[07-31]`.** The Option-A clause above is struck on the user's 2nd-review
> ruling, relayed verbatim in `Docs/surveys/w3_intake_v2_images.md` §7-1: *"GT-3 REVERSED —
> CONFIRMED. §1.5 Option A (delete) → **build: full-length, enclosed, soffit-lit canopy** per
> G2/U-5. GT-3's content and prim-delta sign flip; `R-3` class survives. CB-7 is respec'd in
> Lane 1."* Image **G2** selects **Option B** of 02-A. `gt_changes_w3.md` §3 GT-3 + §9-1 already
> carry the flip and recorded the spec-side strike as **owed to the spec owner**; this is that
> strike. **Only this one clause is superseded** — the sill, the curb reshape and the
> landing-block deletion in the same ruling are untouched and all three are landed
> (`6edce66`, GT-1/GT-2/GT-3 `LANDED`). What was built, measured, is in
> `Docs/reports/w3_cb7_v1.md` §4: canopy **x −1.90 … 7.15** × y ±2.45, roof underside 2.70,
> 5 column pairs, 8 valances, 10 soffit battens, **+45 prims on the canopy line** (scene02
> 391 → 545 total).

- The landing block at `scene02_underpass.py:29-33` / `:64-79` is marked *"DESIGN PROPOSAL AND IS
  NOT YET REFLECTED IN THE CODE"*. `era_consistency_survey_v1.md:881` already ruled
  **02 landing (L1) = CANCEL** (지하보도 = 도로 부속물, outside 건축법 in every era; landings are
  geometry and are never retrofitted). RT-I §4-N4 is correct that neither A nor B cited it.
  → **Delete the block.** The pit end stays at `x1 = 7.0` (RT-I R9: A's "x ≈ 8.2" was the
  unimplemented proposal, not the as-built).
- ~~Deleting the canopy makes 02-B **mandatory**: with no roof, 「지하공공보도시설…규칙」 제8조⑤'s
  waterproofing duty falls entirely on the entrance sill, and 제8조⑦ (the roof clause) is the one
  with a waiver.~~ `[amended 07-31 · MD-1]` **The premise dies with Option A** — there is a roof
  now. **The sill requirement survives on its own footing and is unchanged**: 제8조⑤ binds the
  entrance whether or not 제8조⑦'s roof is present, and the sill is built and landed as **GT-1**
  (`6edce66`, drop edge 3.380 m, 21 drop rows + 1 `up_step`). Only the *"with no roof"* rationale
  is struck.
- Sill build: raised apron `x −1.20 … 0.00`, `y ±2.10`, top **z = +0.18**, one 0.18 m riser across
  the full apron width at `x = −1.20`; descent then begins from +0.18 so the **total drop becomes
  3.38 m**. Accessibility companion: a 1:12 ramp on one side of the apron (recommended over
  2 × 0.09 m risers — it is the real Korean detail and it reads immediately). Linear grating at
  `x = −1.30` connected to the existing gully, or the sill reads arbitrary. **No 차수판** as visible
  geometry.
- Curb fix: scene02's curb top currently stands **100 mm above the footway** (`curb_top=0.10`,
  road top −0.02) — the scene's own docstring at `:860-861` says so. Real curbs are flush to
  +20 mm relative to the footway with the step on the carriageway side only. Target: exposure above
  carriageway **150 mm**, curb top **flush … +20 mm** above the footway.
- scene02 re-caches GT **once**, covering sill + curb + ~~canopy deletion~~ **canopy rebuild**
  `[amended 07-31 · MD-1]` (§8). The one-re-cache rule itself is unchanged and was honoured in
  full at CB-7 (R-1 + R-2 `260731_cb7_recache` + R-3 `260731_w3_cb7`).

### 1.6 scene08 `[ruled 07-30]`

> tempbar / line barrier **REMOVED**. This **overrides `tonglam_v2.md` §1 row 08 PASS**; the spec
> carries the supersede note.

**Supersede note, to be reproduced verbatim in the scene08 commit message and appended to
`tonglam_v2.md` row 08 when that file is next touched:**

> `tonglam_v2.md` §1 row 08 graded scene08 **PASS** and specifically praised *"barrier tape +
> striped bollards (strong Korean cue)"*. **That verdict is superseded by the user
> `[ruled 07-30]`**: a banded post + sagging strap is Korean **temporary-works** signalling
> (공사·점검 중), not permanent plaza furniture, and nothing in the frame says maintenance is in
> progress. scene08's eyes verdict must be **re-established from scratch** in 통람 v3 against the
> `plaza_civic` panel — one of the two things that earned it a PASS has been deleted.

Consequence to plan for: scene08's PASS is not carried forward. It enters 통람 v3 unranked.

### 1.7 scene07 / scene10 `[ruled 07-30]`

> **PARKED** for user reference images — candidates staged only. scene09's diagnostic side cuts are
> added to the next gallery round.

**Scope of the park, stated precisely** — the *archetype rebuild* is parked (S07-A candidates
C1/C2/C3; S10-A candidate D1). The **decal/scatter work is not**: ruling 1.9 puts the F3 mask fix in
the same commit-batch as 03 · 07 · 10 · D3 · C2, so F2 (rock scatter) and F3 (decal boundary) land
for 07 and 10 now. This **diverges from B §9.4**, which bundled F2/F3 with the parked rebuild —
the supervisor's sequencing governs.

### 1.8 Evidence-gap rows `[ruled 07-30]`

> 01-B · 04-A · 04-B/G-6 gravel deposition · S08-B · the 6 prop-edge rows · the 5 empty archetype
> panels: **implementation may prepare, but the enforcement gates HOLD** until the evidence-closer
> agent lands its photo/PDF panels.

"Prepare" = write the builder, the kwarg, the lint check, with the check in **warn** mode and the
scene-side value unchanged. "Enforce" = flip the check to hard and change the scene value. The
register is §9; the lint checks affected are LINT-9 (setbacks) and the G-6 density template.

### 1.9 Sequencing `[ruled 07-30]`

1. The WP-1 shared-module freeze window is ordered **against** the baluster C0-7 fix
   (`scene_common.build_railing_line`, `scene_common.py:1686`) — both are `scene_common` edits, so
   they cannot be concurrent. Order in §5: **C0-7 baluster gate first inside window SMW-2, prop
   form-templates second** — the baluster fix is a narrow, already-specified P0 and the form
   templates are a large surface that would otherwise sit on top of an unmerged change.
2. The **decal-mask fix lands in the same commit-batch as the F3-affected scenes** (03 · 07 · 10 ·
   D3 · C2) — CB-2.
3. **S06-A geometry numbers are re-verified with Isaac-python / usd-core BEFORE scene06 is cut**
   (WP-T3). B §9.3 already demanded this; RT-I R4 found one figure that does not reproduce (§2).
4. The **building track starts with `building_kit` B-F1 (glazing burial) + the outward-visibility
   self-check**, then BS-1 … BS-6 per survey R3 §7.

### 1.10 Rivermark-named shared textures `[ruled 07-30]`

> Transitive **rivermark-NAMED shared textures** pulled from the **general Content root** are
> **ALLOWED**. The path-scope doctrine governs; the by-name decline applies to whole rivermark
> assets only. No silent material breakage.

Affects three procured assets (PROC §2.1): `concrete_block_01/02`
(`opaque__concrete__rivermarkConcreteBlocks_*`), `trashcan_cylinder_01`
(`urban_b_atlas_rivermark_*`), `bench_park_05` (`T_opaque__concrete__rivermarkEntranceSign_*`).
Their manifest `rivermark_named_transitive` WARN is **cleared to informational**. `rivermark_plaza_bldg_*`
(9 dirs incl. `06a`) stays declined and guard-enforced. The `.gitignore` and the guard are the
procurement agent's files — **do not edit them to record this ruling**; record it here.

### 1.11 Far-tier near-white skyline `[ruled 07-30]`

> **MATERIAL OVERRIDE** — scale the albedo into the ≤ 0.55 project band, keep the textures — rather
> than declining the tier. **Verify at the render gate**, given RT-R's σ_LF −0.32 note.
> The **0.5–1.1 m boulder band stays unfilled** — record as an open procurement row, do not block.

The eight `bldgs_01_distant/Building_*` share `house_wall_001_Diffuse.png` (linear albedo **0.874**,
99.55 % of pixels above linear 0.8) and `concrete_014_Diffuse.png` (**0.969**, 98.73 %) against a
project cap of 0.8 (PROC §6.2). They are 30–130 m skyline objects at `mpu 0.01` (scale ×0.01).
Implementation: bind an override material that keeps the diffuse map and multiplies it into the
project band (target linear albedo ≤ 0.55, matching the plinth/parapet convention), **not** a
constant colour — a constant would re-create the W2 F1 defect it is meant to avoid.
Gate: survey R3 §4.2 measured that a backdrop albedo change is **not** building-local (GI rebound,
Δ`edge%` up to −1.69, Δ`w80` +1.06, **Δσ_LF −0.32 ≈ 4× the noise floor** on `h0.9_d5`), and σ_LF is
a live W2 gate at 9/33 passing. So every far-tier binding change is re-gated on **B45/B30**, not
only on B-HZ.

---

## 2. Corrected-facts ledger — use these values, not the source's

Every row below is a source error found by a red team or by procurement. **Copying the original
number into an implementation is a defect.**

| # | Source claim | Correct value | Authority |
|---|---|---|---|
| **C-1** | patch decal applies to "18 ground profiles" / "18 of 22" (A G-1, 01-A) | **`patch` in 10 of 19 profiles**: `plaza_granite, plaza_water, sidewalk_block, street_asphalt, alley_concrete, roof_membrane, ramp_parking, ramp_road, levee_paved, verge_rural`. `stain` = **19/19**. `weed` = 8/19 | RT-I R2 `[repro]` of C's AST-exec |
| **C-2** | "the exact **18** `bc.jit_yaw`/`bc.jit_pos` call sites" (C §0.1/§3.2 prose, echoed by B §1.0) | **24 sites** — C's own line list and its Appendix A already sum to 24. Sites: `N1:337,338,348,349` · `N2:351,352,361` · `N3:583,584,589` · `N5:386` · `C1:811,812,837` · `C2:801,802,821,837` · `C4:377,381` · `D2:293,294` · `D4:649,650`. **Grep precision** `[measured]`: `grep -rn "bc\.jit_yaw\|bc\.jit_pos" --include=*.py scenes/` returns **25 hits — the 25th is a comment at `sceneN1:154`**, not a call. Delete the calls; rewrite that comment | RT-I R3 |
| **C-3** | scene06 "union outer radius swings 3.3000 → 3.3990 = **99.0 mm** landing rim swing" (B S06-A A-2, quoted as a headline) | **UNCONFIRMED — do not quote.** With chord 444.6 mm the landing box corner radius is √(3.30² + 0.2223²) = **3.3075**, i.e. a **7.5 mm** swing, which the same table row already lists. 3.3990 = 3.30 × 1.03 — the tangential margin mis-applied to the radius. **Re-verify on usd-core (WP-T3) before any number is cut into code.** All other A-2 figures reproduce (2.27× · 7.08× · 17.6 mm · 12.9 mm overlap · 348 mm interpenetration · +153.6/−38.4 mm fascia lip) | RT-I R4 |
| **C-4** | scene02 has street trees assigned `Elm_Sapling` (A G-2 table) | **Row deleted.** scene02 has **no `build_tree` call** | RT-I R7 · `[ruled 07-30]` §1.3 |
| **C-5** | "korean_pedestrian_geometry.md was written **before** v5.1, so the survey was overridden" (C §0, §3.1) | **REFUTED — strike the chronology argument entirely.** kpg header: 작성 **2026-07-28**; first commit `bc87292` 07-28 23:52. v5.1 is **07-27 저녁**. The defensible framing, and the only one that may appear in a commit message: *the statute survey (07-28) documented the contradiction one day after v5.1 (07-27) and it was never reconciled; the supervisor has now reconciled it in the statute's favour* | RT-I R1 |
| **C-6** | jitter inventory is "complete" | **Two additions**: `facade_kit.py:563` (AC-unit u-offset, KEEP `[ruled 07-30]`) and `facade_kit.py:840` (gas-valve z, KEEP). Plus the six missed KEEP-class rows in §1.2 | RT-I §4-N1/N2 · `[ruled 07-30]` |
| **C-7** | scene08 materials `M["tempost"], M["tempost_b"], M["tape"]` (B S08-A) | **`M["temtape"]`** (`scene08:913`). And the six deletion line-ranges drift 3–5 lines — **re-derive them from anchors (prim names / dict keys), never from the literal ranges** | RT-I R12, §1 |
| **C-8** | scene18 benches/planters "all carry −2.57° … a scene-wide skew" (B §1.2) | **Misread.** −2.57 is the **z coordinate** (lower plaza `top_z=−2.57`, `scene18:104-105`); scene18 bench tuples are (x, y, **z**, yaw) with yaws **0.0 / 90.0** — already orthogonal. The "do not touch" instruction is right; the reason is wrong. `scene20 rot=dict(deg=30)` is correct | RT-I R5 |
| **C-9** | "13, 16, **18**, 20, N5 also carry bollards" (A 03-B) | scene18's bollards were **removed entirely** (v5.1 §2; `scene18:159-163`). **Full carrier set for the LINT-6 gate**: 02 · 03 · 05 · 06 · 08 · 11 · 12 · 13 · 14 · 16 · 20 · 21 · C4 · D1 · N1 · N2 · N3 · N4 · N5 | RT-I R6, X5 |
| **C-10** | monospecific-row probabilities: "1.8 % at n=5" (A) / "(4/11)²⁰ ≈ 1.4×10⁻⁹" (C) | **0.81 %** at n=5 (Σ(wᵢ/11)⁵ = 1301/161051) and **1.63×10⁻⁹**. Conclusions unchanged | RT-I R8 |
| **C-11** | scene02 "pit runs to x ≈ 8.2", "~7.6 m of open pit" | As-built `pit=dict(x0=0.0, x1=**7.0**)` (`scene02:132`); open pit behind the canopy ≈ **6.4 m**. 8.2 was the unimplemented v8 proposal, now deleted `[ruled 07-30]` | RT-I R9 |
| **C-12** | manhole census "extracted from `SCENE_PLANS`, the fixture that **mirrors** the shipped coordinates"; "**every** site \|y\| ≤ 2.4" | The fixture does **not** mirror scene01: plan (−8.0, **1.6**) vs shipped PARAMS (−8.40, **−2.60**) — the \|y\| bound fails on the shipped scene. N5's grating-subject manholes sit at **+x** (6.0 / 9.5), outside the census scope. **Derive every manhole edit from the scene's own `PARAMS`, never from `SCENE_PLANS`.** Clustering / x<0 / near-window conclusions are unaffected | RT-I R11 |
| **C-13** | scene03 bench yaws "+5, 172, 93" (3 values) | **4 benches** — the 187° one is missed (`scene03:197-200`: 5.0 / 172.0 / 93.0 / **187.0**) | RT-I R13 |
| **C-14** | scene07 tread depth 0.27–0.39, gap 0.05–0.29 | depth **(0.28, 0.40)**, gap **(0.05, 0.30)** | RT-I R13 |
| **C-15** | render counts for 06–10 "17 · 15 · 16 · 14 · 14 PNG" | **15 · 14 · 15 · 14 · 14**. All *named* cuts exist | RT-I R10 |
| **C-16** | `build_tree` call sites | **25 sites across 17 scenes** (20 main + 4 batch1 + `build_planter`'s internal call at `scene_common.py:2564`). B's "20 over 13" counted `scenes/main` only | RT-I §2.2 |
| **C-17** | R2 C6c: "tactile=True on **39 of 41** bollards" | **12 ON of 42** (C4 6 + N5 6). Five call sites pass `tactile=False`, landed in W2-D commit `b19a1af`. HOLD posture survives; the briefing numbers do not | RT-R §4.2 |
| **C-18** | R1 §6.5: "`typical_building_10` → translate **+7.904** in Z" | **WRONG, and wrong for the whole mid tier.** All ten `typical_building_*` measure **0.0 % of triangles below grade** despite bbox `zmin` −1.08 … **−10.34 m** — the negative extent is a foundation box and **local z = 0 IS street grade**. Applying the table would hoist every facade by up to 10.34 m. 28 *props* genuinely do need `−zmin` lift; the per-asset `z_advice` field in the manifest is the authority | PROC §5.1 (generalises RT-R Correction 2) |
| **C-19** | R3 B-F4: `brick_red` corrected `scale_m` = **0.87** | **Band 0.90 – 1.10**, not a point value. Three independent measurements of `brick_red_diff.jpg` disagree: autocorr 13.4 courses/tile, direct joint count ~16.4, visual ~16. Over-scale conclusion holds (154 mm vs the Korean 67 mm course); **do not ship 0.87** — re-derive from a mortar-grid overlay render before touching 17 scenes | RT-R §3.5 |
| **C-20** | R3 §4.2 / §7.3-(4) arm-(d) GI leak bounds (−1.34 `edge%`, +0.96 `w80`) | Those are the **`h0.3_d5` cut only**. Worst per-cut (`h0.9_d5`): Δmean **+1.50** · Δ`edge%` **−1.69** · Δ`w80` **+1.06** · **Δσ_LF −0.32** | RT-R §3.4 |
| **C-21** | RT-4 / R1: `veg_shrub_hedge_yellow_01` is a season risk by name | **Name heuristics are dead — the pixel rule is the only instrument.** Measured at the mesh-binding level: `_yellow_01` binds a **green** atlas over 89.4 % of its triangles (green 0.941, warm 0.002) → **PASS**. `veg_shrub_hedge_round_01` binds a **dry straw/orange** atlas over 74.6 % (green 0.000, yg 0.494, orange 0.467) + a **fruit** atlas → **FAIL**. Do not wire `hedge_round_01` | PROC §0-3, §6.1 |
| **C-22** | R1 §5.2: `ac_unit_04/05/06` = "the Korean facade signature" | **Rooftop chillers.** `ac_unit_04` measures **3604 × 4203 × 1984 mm** (≈4 × 4 m); a Korean wall 실외기 is ≈ 800 × 300 × 600 mm. PH `exterior_aircon_unit` (1800 × 374 × 928) is ~2× a wall unit. **Rejected for the facade-attachment role; re-tasked as rooftop plant** (§3.4) | PROC §8.1 |
| **C-23** | R2 §A3 / R1: `utility_cover_01` is a manhole cover | **1499 × 954 × 355 mm** — a utility vault, not KS D 4040 Ø648/766/918. W2's procedural manhole (F5) stands, now confirmed **by measurement** rather than by inference | PROC §8.1 |
| **C-24** | unresolved-texture blocker = 2 buildings | **3** — `typical_building_18`, `_106`, and **`_109`, which nobody flagged**. All three resolved by per-asset `--resolve`; the name-prefix heuristic loses them silently. One genuinely dead upstream ref: `typical_building_18_inst.usd` → `shared_textures/concrete_01_albedo.png` (404 at source) | PROC §0-1, §3 |
| **C-25** | reference `typical_building_10.usd` | Reference **`_inst.usd`**. The wrapper composes to **504 triangles**; `_inst.usd` composes to **21,965**. Also: `_inst.usd` wires only `diffuse_texture` + `normalmap_texture` — **no ORM/roughness input at all** (constants from MDL), so the whole facade has one specular response. A second, Korean-ness-independent reason an asset backdrop must be dressed | PROC §3 |
| **C-26** | three procured assets are what they are named | **Aliases**: `bench_park_01` → `../bench_park_03`; `bench_park_05` → **`../bench_curved_01`** (an R2 §5.3 "not procured" item, arriving under another name); `concrete_block_02` → `../concrete_block_01` | PROC §5.3 |
| **C-27** | PH polycounts from the API | 3 disagree with the local USD: `modular_urban_apartments_facade` **877,365** (API said 118,215 — **7.4×**, i.e. 40× `typical_building_10`); `stone_01` 53,520 and only **147 × 89 × 72 mm** (a pebble); `concrete_road_barrier_02` 23,822. The other 30 match exactly | PROC §5.5 |
| **C-28** | `metersPerUnit` | **1.0 everywhere measured** except the 8 far-tier `bldgs_01_distant/Building_*` at **0.01**. Read it per asset anyway | PROC §5.2 |
| **C-29** | tonglam fix IDs | §1 uses `FIX-1…FIX-6`, §3 uses `F1…F5` for the same items. **Normalise to the F-numbers.** Map: FIX-1→**F1** · FIX-2→**F1** (scene11 plate) · FIX-3→**F4** · FIX-4→**F2** · FIX-5→**F5** · FIX-6→**F3** | RT-I X3 |
| **C-30** | scene05 `seat.arcs=((80.5,99.5,3),…)` values | **Arc spans in degrees, not yaws.** Do not sweep them into the jitter abolition | RT-I §2.1 |

---

## 3. Asset-first re-adjudication `[ruled 07-30]`

**Method.** Every row is judged on the **measured** bbox from `assets/urban_manifest_w3.json`
(usd-core, instance proxies expanded) against the Korean referent the audits already established.
A `CONFIRM rebuild` verdict must name the failing dimension. A `FLIP to asset` verdict must name
the asset and its measurement. Nothing here is judged on a catalogue field.

Procurement state: **291 assets / 1,160 files / 1.301 GB local and verified — PASS 258 · WARN 17 ·
FAIL 1 · SKIP 15**, `assets/urban/` (NVIDIA, redistribution forbidden) + `assets/urban_cc0/`
(Poly Haven, CC0). Downloader is idempotent (`ok 0 · skip 2323 · fail 0` on re-run).

### 3.1 Verdicts on R2's 20 `rebuild-procedural` rows

| R2 row | Object | New verdict | Measured basis |
|---|---|---|---|
| **B1a** | hedge crown blobs, h ≤ 1.2 m | **CONFIRM rebuild** | The only hedge asset is `veg_shrub_hedge_green_01` at **5795 × 3306 × 1924 mm** — a 3.3 m-**deep** informal mass. A Korean clipped 생울타리 is 0.6–1.2 m deep and box-shaped by pruning practice. Archetype clearly broken. Fix stays: `rounded=False` + crown elements 0.08–0.12 m + a 0.6–1.2 m gap every 6–12 m + ±10 % per-segment height |
| **B2d** | scene15 alley pots | **FLIP container to asset** | PH `planter_pot_clay` + `Barrel_01` (Ø563 × 880) as the 물통; 스티로폼 박스 and 고무 대야 stay procedural (no asset). Foliage already asset (`Boxwood` / `Grass_Short_A`) |
| **C1** | `build_bench` | **CONFIRM rebuild** | All four candidates fail: `bench_park_03/_01` **1735 × 1149 × 1325** (depth **2.13×**, height **1.89×** the 등벤치 1600 × 540 × 700); `bench_park_02` 2589 × 1198 × 1347 (length 1.62×, depth 2.22×); `bench_park_05` 4091 × 2170 × 442 (a 4 m curved cluster, and an alias of the declined `bench_curved_01`); PH `painted_wooden_bench` 1165 × 496 × 889 (length −27 %, height +27 %). A bench is a near-field h0.3 object — 1.15 m depth against 0.54 m reads instantly |
| **C1b** | D4 platform bench | **CONFIRM rebuild** | No stainless/plastic gang bucket seat in any reachable catalogue |
| **C2** | streetlight | **FLIP to HYBRID — the highest-value re-opened row** | Luminaire **heads** are real cobra bodies at **256–4,184 tris**: `luminaire_head03` 1009 × 216 × 98 (256 tri) · `luminaire_head04` 469 × 471 × 495 (639) · `luminaire_head02` 728 × 303 × 240 (532) · `luminaire_head01/_01` 700 × 346 × 206/148. Arms: `luminaire_arm_{6,8,10}ft` = 1838 / 2448 / 3057 mm, 858–906 tri. Whole poles fail: `streetlamp_01` **3291 mm** (below the 4.5 m pedestrian minimum — same failure as PH `street_lamp_01` at 3871), `streetlamp_03` **7072 mm** (arterial scale); only `streetlamp_02` **6215 mm** lands, at the top edge of the band. → **asset head + asset arm on our own tapered Korean pole** (Ø139.8→Ø76.3 + 100×100×6/8/9T base plate + hand-hole). `streetlamp_02` is the whole-pole A/B control at the gate |
| **C3** | litter bin | **CONFIRM rebuild (plaza); asset for alley/yard** | `trashcan_cylinder_01` **Ø722 × 1041** (Ø 1.29–1.60× the 가로 휴지통 Ø450–560, not 2-gang); `trashcan_square_01` 586 × 796 × 1011 (deeper than wide — wrong form). PH `metal_trash_can` 1847 × 556 × 906 (width **3.30×**) → **alley/yard dressing only (15 · D1 · D2), never a plaza** |
| **C4** | `build_canopy` → pergola | **CONFIRM rebuild** | No pergola/canopy asset in any catalogue. Beams + rafters @300–450 + slope + fascia + eaves ≥ 0.15 |
| **C5** | `build_planter` | **SPLIT** | The **kerbed masonry bed** (47 instances / 12 scenes) stays procedural — no asset supplies a KS F 4006 화단경계석 150 × 150 × 1000 bed, and the defect is curb thickness (0.25 → 0.15), albedo (≤ 0.5) and soil level (at or above cap), not the form. The **free-standing container planter** is a legitimate second Korean type and **flips to asset**: `planter_lrg_01` **1500 × 1500 × 700** (1,668 tri) and `planter_round_01` **Ø1002 × 988** (728 tri) are plausible Korean plaza containers. Use containers where a scene wants a movable pot; never as a substitute for a bed |
| **C5b** | 수목보호판 tree grate | **CONFIRM rebuild** | No grate asset. Min opening **1.5 m**, cover **≥ 5 cm** below grade; N5's 1.20 → **1.50** |
| **C6** | bollards | **FLIP to asset** | Measured against 교통약자법 시행규칙 별표2 제7호 (h 0.8–1.0 m, Ø 0.1–0.2 m): **`bollard_01` 139 × 1003 mm (2,564 tri) — both in spec**; **`strt_fxd_bollard_05` 133 × 845 mm (2,628 tri) — both in spec**. Our own `scene_common.build_bollard` is **Ø120 × h750 = 6.3 % below the legal minimum**. `strt_fxd_bollard_03` (207 × 297 × 721, h below minimum, non-circular) becomes the **measured non-compliance variant** the 96.0 % 부적정 statistic calls for. `strt_fxd_bollard_01` (269 × 262 × 1293) and `bollard_02` (Mathworks, declined) are out. **Residual procedural work**: base plate + anchor cover + impact-absorbing band material — R2's form objections are about *features*, not size, and a US DriveSim bollard has none of them. Gate: an A/B h0.3 crop (asset vs current) before adoption |
| **C7b** | identity-critical signage | **SPLIT** | **Road plates flip to asset**: 156 Korean 도로교통법 plates on disk, **FAIL 0**, median 2048 px long side / contrast 232 / glyph fraction 0.317, contact sheet read by eye — every plate carries a real Hangul regulatory face. `sign_krroadname` (도로명판) is the all-scene cue. Station 역명판, platform hanging signs, ad lightboxes and D1 dock numbers **CONFIRM rebuild + texture** (no asset). Two WARN: `sign_kr224_110` + `_emissive` are a VMS speed sign whose numerals live in the emissive channel — legible only with the emissive material bound |
| **C7c** | sign-post dimensions | **CONFIRM rebuild** | `pole_fxd_pedestrian_signage_01` is **373 × 373 × 2122 mm** total — shorter than the 2.5–3.0 m panel-bottom requirement. Keep as a dimensional/mount control only |
| **RF-1** | base plate + anchor bolts | **CONFIRM rebuild** | RT-R verified the negative: no bollard/handrail/kerb/tactile/bus-shelter exists in the 521-model CC0 index. This is still the map's highest-value row and it costs no geometry |
| **RF-2** | metal age ladder | **CONFIRM rebuild (material)** | Material constants, no asset possible |
| **RF-3** | Korean stainless shape vocabulary | **CONFIRM rebuild** | Newel ball · goose-neck return · beaded rings · **the inverted-U hoop row across the stair head** — a standard Korean fixture with zero instances in 33 scenes and no asset anywhere |
| **RF-5** | nosing tiers | **CONFIRM rebuild** | No nosing profile asset. Three tiers (Al profile 60 mm / paint-only / partial-width tile) + **5Y 8.5/12 ≈ `#F0BE00`** |
| **RF-6** | scars of the operation | **CONFIRM rebuild** | Damage decals; no asset |
| **E2** | D2 aggregate piles | **FLIP partial** | The single-ellipsoid pile becomes a **scattered-rock ridge** using `rock_01` (316 mm, 3,104 tri), `rock_02` (463 mm, 4,758), `rock_03_broken` (1714 mm, 9,832). Rebar / bags / fence stay procedural |
| **E2b** | rebar / cement bags / safety fence | **CONFIRM rebuild** | Ribs + rust + grid; kraft grey-brown not white; bar pitch 250 → 100–150 |
| **E3** | D3 boundary fence | **CONFIRM rebuild** | 가설울타리 steel panel is the Korean form; PH `modular_chainlink_fence` (8115 × 2149 × 2523) is admitted **for yard boundaries only** (D1 · D2), never in a primary cut. Posts @1.8–2.4 m, panel breaks, one gate |

**Tally: 6 rows move toward assets** (B2d container · C2 hybrid · C5 split · C6 flip · C7b road
plates · E2 partial) · **14 confirmed procedural, each with the failing millimetre recorded.**

### 3.2 Rows R2 already had as assets — status

`A1` weed → `Shrub/Grass_Short_C.usd` (1,598 tri) **unchanged and still the best option**.
`A2` D-5 rock scatter **keep** (W2 F2 closed) — but the carried gap is now partly filled, see §3.3.
`A3` manhole **keep** — now confirmed by measurement (C-23), not by inference.
`B2a` / `B2b` / `B3` shrub and reed replacements unchanged (local `veg_manifest_w2.json` PASS assets).
`B1b` midground belts: `veg_shrub_hedge_green_01` (PASS, green 0.952 over 97.8 % of triangles) is
now available and is the right asset for the h 1.6–2.0 m belts that `build_hedge` is mis-modelling.
`veg_shrub_hedge_yellow_01` also PASSes (C-21) and is admissible where a second belt species is
justified. **`veg_shrub_hedge_round_01` is FAIL — do not wire it.**

### 3.3 New asset rows that R2 did not have

| ID | Row | Asset | Scenes | Pri |
|---|---|---|---|---|
| **N-A1** | Korean road plates as scene content | 156 `sign_kr*`, PASS, glyph-verified; `sign_krroadname` all-scene | per archetype: A plaza 01·08·14·21 (kr324 어린이보호구역, kr323 노인보호) · B riverside 03·09·12·17 (kr126) · C park 04·10·16 (kr302/303/333) · D underpass/footbridge 02·06·11 (kr321 보행자전용, kr322 횡단보도) · F apartment 13 (kr224, kr226, kr320, krzone30) · L yard/drainage D1·D3 (kr136, krconstruction_50) | **P0** |
| **N-A2** | Korean road-marking stencils | 9 `stencil_ko_*` (bus-only line ×4, direction arrows ×3, colour lane ×2) | carriageways in 06 · 11 · 13 · N2 · D3 | P1 |
| **N-A3** | scene19 rooftop equipment | `ac_unit_04/05/06` re-tasked as **rooftop plant** (C-22) + PH `utility_box_01/02`, `power_box_01` | 19 (the v1 처방: 물탱크·실외기·배관) | **P0** for scene19 |
| **N-A4** | far skyline / horizon closure | 8 `bldgs_01_distant/Building_*` — **`mpu 0.01` → ×0.01 scale**, **material override mandatory** `[ruled 07-30]` §1.11 | 03 · 09 · 12 · 17 + N-series backdrops; scene09's black-silhouette backdrop is the named target | P1 |
| **N-A5** | mid-tier asset backdrop | `typical_building_{03,07,08,10,11,12,13,18,106,109}` — reference **`_inst.usd`** (C-25), **no Z lift** (C-18). `_106` ships rooftop condensers = a Korean cue; `_18` is low-rise white plaster + tile roof and needs the near-white check (its `plaster_white_01_a.png` measures **0.00 %** over cap at albedo 0.365, so it is clear) | per survey R3 §7.2: 20-C · 21-#1 · C1-#0 · 01-#2 | P1 |
| **N-A6** | bike racks | `bike_rack_01` (1827 × 130 × 1073), `bike_rack_02`, `bikerack_metal03` | 01 (existing bike racks) + plaza scenes | P2 |
| **N-A7** | riprap gap fill | `rock_02` (463 mm) fills the lower half of scene12's 0.30–1.10 m band; `rock_03_broken` (1714 mm) is a boulder above the band | 12 | P2 |

**Barricade caution.** `traf_barrier_mov_type3_*` (Type-III orange/white) are **temporary-works**
objects — the exact class ruling 1.6 deleted from scene08. They are admissible **only in D2**
(construction slab). Do not reintroduce them to any finished plaza.

**Leaf-scatter caution.** `sct_debris_leaves_dry_01..04` measure green 0.000 / orange 0.343 /
red 0.655 — **SEASON-SCOPED to the leaf scenes only (C2 · 07 · 10 · D3)** and banned elsewhere
(PROC §6.1). C2's own `oakfall1/2.usd` remain the primary source there.

### 3.4 Integration quirks every asset row must obey

1. **No Z lift on the 10 mid-tier buildings** (C-18). Use the manifest's per-asset `z_advice`; the
   28 props that genuinely need `−zmin` are listed there.
2. **Reference `_inst.usd`**, never the wrapper (C-25).
3. **`mpu` per asset** — 1.0 everywhere except the 8 far-tier buildings at 0.01 (C-28).
4. **Parent-Xform placement** — the referenced root already owns
   `[xformOp:translate, rotateXYZ, scale]`, so `AddTranslateOp()` on it raises; place the reference
   under an Xform you own, or set the existing ops (survey R3 §5.6 Correction 3).
5. **240 dead references of the form `<asset>/materials/textures/<name>.png` are normal** — the
   inner `_inst_base` layer's paths, overridden by `_inst`. The one genuine miss is
   `concrete_01_albedo.png` on `typical_building_18` (404 upstream).
6. **Mirror `nv_content/` verbatim** — three assets are cross-folder sublayer aliases (C-26) and
   flattening the tree breaks them.
7. **Asset backdrops must still be dressed** with the `facade_kit` attachment layer — two
   independent reasons: Western architecture (no AC condensers, no signage band, no gas riser) and
   a flat single specular response from the missing ORM input (C-25).

---

## 4. Work packages — file-disjoint ownership

**The rule.** Every file in the tree has **at most one owner at any instant**. A WP may read
anything; it may write only its own list. Where two WPs need the same file, they are placed in
different windows (§5). Commit **batches** may span WPs — ownership is about files, batching is
about what lands and gets rendered together.

### 4.1 Track T — tooling and evidence (no scene files, no shared modules)

| WP | Owns (exact paths) | Delivers |
|---|---|---|
| **T1 · placement linter** | `scripts/placement_lint.py` *(new)* · `Docs/briefs/placement_rules_v1.yaml` *(new)* | LINT-1…LINT-10 (§10.4) on the `geom_invariance_check` harness (imports it; **does not edit it**). Exit 0 clean / 1 violation / 2 harness error |
| **T2 · reference panels (evidence closer)** | `scripts/harvest_refs.py` *(new)* · `Docs/reference_photos/w3/**` *(new)* · `Docs/reference_photos/w3/LICENSES.csv` *(new)* | 12 archetype panels; the 5 empty ones are the blocking work. CSV schema reused verbatim from `Docs/reference_photos/expanded/LICENSES.csv`. **Thumbnails only for CC0 / CC-BY / KOGL Type 1; BY-SA stays URL-only** (continues `real_set_safe.txt`) |
| **T3 · geometry re-verification** | `Docs/reports/w3_geom_reverify_v1.md` *(new)* | Re-confirm on usd-core / Isaac-python **before scene06 is cut**: the S06-A analytics (C-3 above all), scene09's waterline −5.240 (inside `compute_steps`, never recomputed), and the C0-7 baluster numbers. `pxr` is absent from the project venv — use `python3 -m venv /tmp/usdvenv && /tmp/usdvenv/bin/pip install usd-core` |
| **T4 · urban asset loader** | `/urban_kit.py` *(new)* · `scenes/main/urban_kit.py`, `scenes/batch1/urban_kit.py` *(new symlinks)* · `Docs/reports/w3_asset_readjudication_v1.md` *(new)* | The single place §3.4's seven quirks are implemented once: manifest-driven resolution, `_inst.usd` selection, per-asset `mpu`, per-asset `z_advice`, parent-Xform placement, and the far-tier albedo override `[ruled 07-30]` §1.11 |
| **T5 · GT ledger** | `Docs/audit_v4/gt_changes_w3.md` *(new)* | §8's ledger as a live file; every GT-affecting commit appends a row before it lands |

### 4.2 Track K — shared kits (serialised by window, see §5)

| WP | Owns (exact paths) | Rows |
|---|---|---|
| **K1 · ground kit** | `/ground_kit.py` | J-1 · J-2 · J-7(AABB) · DEC-1 `build_blot` · DEC-2 carpet masks · DEC-3 patch axis lock · A1 weed→asset + line-seeding contract · G-6 ground-side plumbing *(prepared, gated)* |
| **K2 · batch1 common** | `scenes/batch1/batch1_common.py` | J-3 / J-4 default flip **then** helper deprecation · `build_bollard_v51` asset swap · `jit_tint` untouched |
| **K3 · building + facade kit** | `/building_kit.py` · `/facade_kit.py` · `scenes/main/building_kit.py`, `scenes/batch1/building_kit.py` *(new symlinks)* | B-F1 glazing burial + the `out_max > 0` self-check · B-F2 bay count from `W` · B-F3 `lod_dist` from the judged eye set · BS-4 `kind="backdrop"` · facade AC-unit KEEP docstring `[ruled 07-30]` §1.2 |
| **K4 · scene common + props kit** | `/scene_common.py` · `/props_kit.py` *(new)* | **(a)** C0-7 baluster gate on `build_railing_line` **(first)** · **(b)** S-1…S-4 species (`VEG_SPECIES`, `species=` kwarg, `SCENE_SPECIES`, `place_shrubs` per-bed) · **(c)** prop form templates C1 · C1b · C3 · C4 · C5 · C6 · C7c · RF-3 · RF-5 (`build_nosing` is here, `scene_common.py:1661`) · **(d)** S06-A arc/helix convention (`build_arc_steps` :1625 · `build_helix_steps` :1835 · `build_helix_ramp` :1863) · **(e)** G-6 `scatter_debris` density template *(prepared, gated)* |
| **K5 · infra kit** | `/infra_kit.py` | `build_curb_line` (new shared builder) · `build_gutter_L` wiring · `build_ramp_curb` wiring · manhole derivation helper for the KDS rule · RF-4 `TACTILE_YELLOW` worn-state constant *(prepared, HOLD)* · J-11 keep-at-zero docstring correction |

**Unowned in W3 — do not edit**: `/stair_kit.py` · `/variation_kit.py` · `scripts/geom_invariance_check.py` ·
`scripts/regression_check.py` · `scripts/near_ground_stats.py` · `scripts/imgstats.py` ·
`scripts/const_color_audit.py` · `scripts/stamp_round.py` · `scripts/valset.py`. If a row proves to
need one, claim it at window open and record the claim here.

### 4.3 Track S — scenes (each of the 33 has exactly one owner for the whole wave)

| WP | Scenes owned (exact paths under `scenes/`) | Principal rows |
|---|---|---|
| **S1 · plaza / civic** | `main/scene01_campus_stairs.py` · `main/scene05_amphitheater.py` · `main/scene14_grandstair_illusion.py` · `main/scene20_diagonal_oblique.py` · `main/scene21_monumental_selfocclude.py` | 01-A patch snap · 01-B *(gated)* · 01-C weed→0 · 01-D bench alignment · 05-A paving module · 05-B manhole · C5 planters (P0 on 01) · C6b bollard removal (14) · B2b scene05 backdrop 337→52 · F1 ghost patches (20) · N-A1 signage · N-A6 bike racks |
| **S2 · underpass / GT** | `main/scene02_underpass.py` · `main/scene16_canopy_shadow.py` | **All of ruling 1.5** (canopy delete · sill · curb · landing-block delete) · 16 sill audit · C6b bollard removal (16) · RF-1/RF-2/RF-3/RF-5/RF-6 retrofit vocabulary (both scenes are RETROFIT-STYLE cells) |
| **S3 · decal / park-natural** *(the F3 co-landing group)* | `main/scene03_riverbank.py` · `main/scene07_temple_stone_path.py` · `main/scene10_park_deck_switchback.py` · `main/scene12_riverside_deck.py` · `batch1/sceneD3_drainage_channel.py` · `batch1/sceneC2_leaf_stairs.py` | **F3 decal boundary + F2 rock scatter for all five F3 scenes** · 03-A/03-B/03-C/03-D · C2 vertical-face leaf-texture binding bug · E3 D3 fence rebuild · B2a slope shrubs · B3 reeds (12) · N-A7 riprap (12) · 07/10 **archetype PARKED** (§9) |
| **S4 · street / bridge** | `main/scene06_overpass_spiral.py` · `main/scene11_footbridge_stairs.py` · `main/scene13_apartment_parking_entry.py` · `main/scene17_ramp_pair_hangang.py` · `batch1/sceneN5_flush_grating.py` | **S06-A spiral repair** (after T3) · S06-B curb legibility (06 · 11) and curb **build** (13) · J-6 street-row pitch · F4 scene17 grass · F5 scene17 manhole · C5b N5 grate 1.20→1.50 · N-A2 road marks |
| **S5 · water / park** | `main/scene04_parktrail.py` · `main/scene09_ghat_riverfront.py` | **S09-A three diagnostic cuts (ship first, zero risk)** · S09-C mooring posts off the stair face · 04-A verge rework *(gated)* · 04-B gravel *(gated)* · F2 rock scatter (04) · B1b midground belts |
| **S6 · sunken / alley / roof** | `main/scene08_sunken_plaza.py` · `main/scene15_alley_labyrinth.py` · `main/scene18_wavy_artstair.py` · `main/scene19_fan_winder.py` | **scene08 tempbar removal `[ruled 07-30]`** + x=−18 bollard row + road-lines-without-a-road · S08-B *(parked)* · B2d scene15 pots · E4 alley dressing (cap 3/segment) · 19 membrane rebind (F1) + **N-A3 rooftop equipment** + era rider B (rail 1.1 m) |
| **S7 · batch1 hard-negative** | `batch1/sceneN1_shadow_band.py` · `batch1/sceneN2_asphalt_patch.py` · `batch1/sceneN3_trompe_loeil.py` · `batch1/sceneN4_downhill_ramp.py` | `bc.jit_*` call-site removal (N1 ×4 · N2 ×3 · N3 ×3) · F1 constant-colour mats and N2 crack-kind rebind · C7a deletions (**N4 `wall_plates` ×3** — R2's #1 ranked item) · C5b N2 tree pit → 수목보호판 · manhole rule |
| **S8 · batch1 industrial / transit** | `batch1/sceneC1_snow_stairs.py` · `batch1/sceneC4_wet_stairs.py` · `batch1/sceneD1_loading_dock.py` · `batch1/sceneD2_floor_opening.py` · `batch1/sceneD4_subway_platform.py` | `bc.jit_*` removal (C1 ×3 · C4 ×2 · D2 ×2 · D4 ×2) · **J-5 sceneD1:855 crates → dock bearing** and `D1:153` / `D2:210` → 0 `[ruled 07-30]` · C7a deletions (C1 `signpost` · C4 `sculpture` · D2 slogan ×2) · E1 D1 apron set · E2/E2b D2 · C1b + C7b D4 · **do not clean D4's worn tactile** |

### 4.4 Track X — rounds and gates

| WP | Owns | Delivers |
|---|---|---|
| **X1 · round driver** | `scripts/rounds/run_260731_w3_pilot*.sh`, `scripts/rounds/run_2608xx_w3_full.sh` *(new)* | Pilot and full-round runners, modelled on `run_260730_w2d_fix.sh`; the **order-prefix rule** (render the full preset prefix and discard extras — PT/DLSS accumulation carries frame history) is mandatory in every runner |
| **X2 · gallery v2** | `scripts/make_review_gallery.py` · `look_check/_review_w3/**` | 4 standard tiles + **scene09's 3 diagnostic side cuts** + the archetype panel thumbnail beside each h0.3_d5 tile. Substituted views must be named in `meta.json`, never silently swapped |
| **X3 · 통람 v3** | `Docs/reports/tonglam_v3.md` *(new)* | Panel-paired verdicts (§7.3). May append a supersede note to `tonglam_v2.md` for rows 08 and 10 |

---

## 5. Freeze windows, commit batches, dependency order

### 5.1 Windows

Shared-module edits are serialised. `측정 중 공유모듈 동결` (STATUS 규율) means: **no shared module
may be edited while a round is rendering.** A window closes when its render gate passes.

```
WINDOW 0  (CPU only, no shared modules, fully parallel)
   T1 linter · T2 panels · T3 geom re-verify · T4 urban loader · T5 GT ledger
   ── exit: T1 runs clean on the untouched tree (baseline violations recorded, not fixed)
            T3 publishes the confirmed/refuted S06-A numbers

WINDOW 1  (three disjoint shared modules in parallel)
   K1 ground_kit          K2 batch1_common          K3 building_kit + facade_kit
   ── exit: GATE-1 pilots (CB-2, CB-3, CB-4)

WINDOW 2  (scene_common exclusive; infra_kit in parallel)
   K4 (a) C0-7 baluster  →  (b) species  →  (c) prop templates  →  (d) arc/helix
   K5 infra_kit
   ── exit: GATE-1 pilots (CB-5, CB-6)

WINDOW 3  (scene files; eight WPs fully parallel — every scene has one owner)
   S1 · S2 · S3 · S4 · S5 · S6 · S7 · S8
   ── exit: GATE-2 full round

WINDOW 4  (judging; no code)
   X2 gallery v2 → X3 통람 v3

WINDOW 5  (evidence-gated re-open, only after T2 lands its panels)
   K1 + K4 re-open for G-6 deposition scatter · S1 for 01-B · S5 for 04-A/04-B
   ── exit: GATE-2b partial round on the affected scenes
```

**Why K4's internal order is (a) → (b) → (c) → (d)** `[ruled 07-30]` §1.9-1: the C0-7 baluster gate
is a narrow, already-specified P0 that the prop templates would otherwise be written on top of.
Species is next because it is signature-preserving and unblocks all eight scene WPs' `veg=` PARAMS.
Prop templates are the largest surface. Arc/helix last because it has the highest blast radius
(06 · 05 · 19 · 13) and must not be in flight while anything else in `scene_common` is moving.

### 5.2 Commit batches and what lands together

| CB | Contents | WPs | Render gate |
|---|---|---|---|
| **CB-0** | Tooling + panels + re-verify + loader + ledger | T1–T5 | none (CPU) |
| **CB-1** | **S09-A three diagnostic cuts + S09-C mooring posts** — additive, zero baseline movement, ships before anything else so the user can judge the rest | S5 | GATE-1 · pilot **09** |
| **CB-2** | **ground_kit decal/jitter batch + the five F3 scenes** `[ruled 07-30]` §1.9-2: J-1 · J-2 · J-7 AABB · DEC-1/2/3 · A1 weed **and** the scene-side decal/scatter work in **03 · 07 · 10 · D3 · C2** | K1 + S3 | GATE-1 · pilots **03 · 07 · C2 · 01** |
| **CB-3** | batch1 furniture jitter: default flip, then call-site removal at all **24** sites, then helper deprecation | K2 + S7 + S8 | GATE-1 · pilots **N3 · C1** |
| **CB-4** | building kit B-F1 + `out_max > 0` self-check + B-F2 + B-F3 + BS-4 backdrop kind | K3 | GATE-1 · pilots **20 · 21** |
| **CB-5** | `scene_common`: (a) baluster → (b) species → (c) prop templates → (d) arc/helix. Four commits, one window, one gate | K4 | GATE-1 · pilots **03 · 06 · 05 · 01** |
| **CB-6** | `infra_kit`: `build_curb_line` + gutter + ramp curb + manhole derivation | K5 | GATE-1 · pilots **06 · 13 · 02** |
| **CB-7** | **scene02 GT batch** — canopy delete + sill + curb + landing-block delete, as **one** commit with **one** GT re-cache | S2 | GATE-1 · pilot **02** + GT re-cache |
| **CB-8** | **scene08 batch** — tempbar removal + bollard row + road lines, with the supersede note in the message | S6 | GATE-1 · pilot **08** + OCCL re-stamp |
| **CB-9** | scene06 spiral repair (**blocked on T3**) + S06-B curb legibility 06/11 + scene13 curb build | S4 | GATE-1 · pilots **06 · 13** + prim-hash GT proof |
| **CB-10** | Remaining scene work, all eight WPs in parallel | S1–S8 | GATE-2 full round |
| **CB-11** | Evidence-gated re-open (WINDOW 5) | K1 · K4 · S1 · S5 | GATE-2b partial |

### 5.3 Hard dependency edges

```
T3 ─────────────────────────────► CB-9 (scene06 may not be cut before the numbers are re-verified)
T1 ─────────────────────────────► every scene commit (the linter is what makes abolition permanent)
T2 ─────────────────────────────► GATE-3 통람 v3 (no scene is judged without its panel)
T2 ─────────────────────────────► CB-11 only (01-B · 04-A · 04-B · S08-B · LINT-9 enforcement)
T4 ─────────────────────────────► every asset row (C6 · C2 head · C5 container · N-A1..N-A7)
K4(b) species ──────────────────► all eight S-WPs' `veg=` PARAMS
K4(c) prop templates ───────────► C6 asset swap in K2 and in S1's scene20/21 `build_bollard_std`
K5 build_curb_line ─────────────► CB-7 (02) · CB-9 (06 · 11 · 13) · S6 (08) · S2 (16)
K1 decal batch ─────────────────► regression re-baseline (the old `regr_260730_w2d_fix.json` dies here)
K3 B-F1 ────────────────────────► BS-1..BS-6 building strategy (survey R3 §7)
CB-2 ───────────────────────────► CB-10 (scene-side decal values are written against the new masks)
```

**Known collisions, and how they are resolved.** (i) survey R2's C1/C2/C5 rebuild the *same prims*
that J-3/J-4/J-5 re-orient — they are merged into one edit per prop class inside K4(c) + the owning
S-WP, so a second pass cannot re-introduce a yaw from a stale template. (ii) R2's B1b/B2a shrub
de-proxying supplies the assets S-2 assigns — S-2 consumes it, never runs first. (iii) the C6
bollard change touches three files with three owners (`scene_common` K4 · `batch1_common` K2 ·
scene20/21 S1); files are disjoint, the row is coordinated by a single spec value in §10.

---

## 6. Per-WP verification obligations

### 6.1 The floor — every WP, every commit, before it lands

```
python3 -m py_compile <every file the WP touched>
NEGOBS_SMOKE=1 python scenes/<dir>/<scene>.py            # per scene touched
python3 scripts/geom_invariance_check.py                 # R-4/R-6 registry vs geometry
python3 scripts/placement_lint.py --scenes <touched>     # after T1 lands
```

No commit without all four green. `검증 없는 확산 금지`.

### 6.2 Per-WP additions

| WP | Additional obligation |
|---|---|
| **T1** | The linter must run on the **untouched** tree first and publish its baseline violation list. A linter that only ever ran on fixed code proves nothing |
| **T2** | Per-file licence verification with the same whitelist that produced the clean 54-row ledger. Enumerating a category is **not** verifying it |
| **T3** | Publish confirm/refute per number. C-3 (99.0 mm) must come back as a value or as a strike |
| **T4** | Load-and-traverse every asset it wires, with `Usd.TraverseInstanceProxies` — `stage.Traverse()` alone reports `bench_park_01` as 0 triangles |
| **K1** | `_obb_aabb → _box_aabb` collapse is expected to move `frame_budget` B1/B2/B5 — **re-baseline `Docs/reports/regr_*.json` and say so in the round stamp.** A1's asset scale must be driven by the **GT-E5-clamped** `proud`, not by native height; `_elem` aabb recomputed from the scaled bbox (0.10 → 0.28 m, **2.8×**); `EDGE_STANDOFF = 0.80` re-checked per instance |
| **K2** | Flip defaults **first** (one edit, library-wide, linter-verifiable without a render), then remove the now-inert call sites **in the same work package** so the tree does not accumulate dead calls that read as intent |
| **K3** | `python3 building_kit.py` → **135/135** plus the **new** check: for every prim whose material role is `glass`/`sign`/`decal`, assert `out_max > 0` against every mass box overlapping its z range. Re-run the 33-scene scan and report the new prim total against the current 4,546 → 1,855 (−59.2 %) |
| **K4** | (a) baluster: prove the ≤ 100 mm 안목 gate on every railing call site. (b) species: `SetInstanceable(True)` already shares prototypes — confirm a 20-tree monospecific row costs **one** prototype, not four. (c) templates: **signature-preserving only** — `build_tree` set the precedent; a signature change is a 33-scene edit and is not authorised. (d) arc/helix: **GT invariance is the acceptance test** — r_in, r_out, azimuths and top-face z unchanged, proven by a prim-hash / GT-delta diff as commit `96968f3` did, not asserted |
| **K5** | `build_curb_line` must emit **unit-length** blocks (real 연석 is a 1 m unit product — the joint rhythm is the single strongest cue that it is a curb and not paint) with the R = 10 mm top arris the repo's own `scene_common.py:304` note calls for |
| **S1–S8** | Each scene's own self-check must pass **after** the edit: `verge_selfcheck` (04) · `podium_step_selfcheck` (05) · `roof_normal_selfcheck` (09) · a **new `spiral_selfcheck`** (06, §10.5). Every deleted prim must be checked out of the hazard/collision box list |
| **X1** | `scripts/stamp_round.py <capture_dir> <round> [scene]` on **every** capture directory. An unstamped round is unreadable in six weeks |
| **X2** | Substituted views named in `meta.json` (scene19 has no `h1.8_d10` — hiding that makes the gallery lie) |
| **X3** | Every verdict names a photograph. **A verdict with no photo name is not a v3 verdict** |

### 6.3 Instruments that are advisory, not gates

`ori_axis` — real Korean scenes measure **0.252 ± 0.074** (p95 **0.371**) against a uniform
expectation of 0.111; our renders already measure **0.311**. Removing jitter pushes it up.
**Measure it before and after the abolition batch. Do not gate on it.** If the post-batch median
exceeds 0.371, that is a signal the scene is **under-dressed**, not that furniture should be
re-rotated — the correct source of orientation entropy in a real frame is clutter, wear and
vegetation, which is exactly what W3 is adding. Also advisory and explicitly not gates:
`sat_mu` / `sat_sd` / `chroma_sd` (measured separability 0.098 / 0.093 / 0.138 — none).

---

## 7. Render-gate plan

### 7.1 GATE-0 — CPU pre-flight

§6.1. No GPU. Blocks every commit.

### 7.2 GATE-1 — per-batch pilots

Per CB, the pilot scenes named in §5.2, **5 cuts each**: `preset_h0.3_d2`, `preset_h0.3_d5`,
`preset_h0.3_d10`, `preset_h0.9_d2`, `preset_h0.9_d5`. Channel identical to the frozen judge round:
`NEGOBS_CAPTURE_MODE=pt · NEGOBS_PT_FAST=1 · NEGOBS_LOOK_V1=1 · NEGOBS_DETAIL_SCALE=2 ·
NEGOBS_DETAIL_ROUGH_GAIN=0`. GPU exclusive, sequential, one process per scene.

**The order-prefix rule is mandatory.** The judge round renders all 13 cuts in `grid_views` order
and PT/DLSS accumulation carries frame history, so a truncated list changes the first cut. Render
the exact prefix and discard the extras.

Pass condition: `python3 scripts/regression_check.py` clean against the current baseline
(DARK / BLOWN / WHITE / OCCL / FRAME), plus the batch's own acceptance test from §6.2.

| CB | Pilots | What the pilot must show |
|---|---|---|
| CB-1 | 09 | The 36-riser stack readable in raking profile; both landings visible as breaks in the rhythm; the waterline cutting the flight |
| CB-2 | 03 · 07 · C2 · 01 | No decal with a straight edge that is not a construction joint, a saw cut or a kerb. 07's leaf carpets and C2's leaf mass stop being rectangles |
| CB-3 | N3 · C1 | Furniture reads as a single line parallel to its anchor; no object off its anchor bearing |
| CB-4 | 20 · 21 | Windows are **visible** (B-F1); bay width lands in the Korean 3.0–4.5 m band (B-F2); 21's two far buildings drop 65→8 and 86→7 prims |
| CB-5 | 03 · 06 · 05 · 01 | 03: **one silhouette class on one bank** (it currently shows five). 06/05: the arc/helix rim is a curve, not overlapping flaps. 01: benches parallel to their planter faces |
| CB-6 | 06 · 13 · 02 | The curb reads as a 150 mm step with a 1 m joint rhythm, not a painted black stripe |
| CB-7 | 02 | The sill reads as an engineered raised entrance; the canopy's four unexplained posts are gone |
| CB-8 | 08 | The plaza reads as finished without the temporary-works barrier |
| CB-9 | 06 · 13 | `pt_noon_broken_rail` no longer breaks; the landing/deck is one walking surface at one z |

### 7.3 GATE-2 — full round

`scripts/rounds/run_2608xx_w3_full.sh` — 33 scenes × 13 preset + mise-en-scène cuts, round id
`<yymmdd>_w3_full` per `look_check/README.md` §2 (`<yymmdd>_<wave>_<purpose>`). Then:

```
python3 scripts/regression_check.py --scenes 'look_check/scene*' ...   # v2.1, new baseline stamped
python3 scripts/near_ground_stats.py                                    # B45/B30 σ_LF · edge% · w80
python3 scripts/imgstats.py                                             # ori_axis, advisory
python3 scripts/stamp_round.py <dir> <round> <scene>                    # every capture dir
```

**σ_LF carry-over warning**: 9/33 currently pass. The decal masks, one-species routes, midground
fill and asset backdrops all change ground and midground content, so σ_LF will move in both
directions. **Do not attribute the movement to the lighting work.**

**Baseline note**: `regr_260730_w2d_fix.json` stops being the comparison baseline at CB-2, when
`_obb_aabb → _box_aabb` changes every patch and stain AABB. Stamp the new baseline at CB-2's gate
and say so in the round stamp.

### 7.4 GATE-3 — 통람 v3, panel-paired

**v3 changes exactly one thing from v2: the panel.** Every verdict is written next to 3–5 real
photographs of the same archetype, and against them — not against the judge's memory.

**Blocking**: **no scene may be judged without its panel.** 5 of 12 archetypes had zero photos at
intake (`river_levee` · `amphitheatre` · `underpass_entry` · `rooftop` · `industrial_transit`);
`lake_park` and `temple_precinct` had one each.

| archetype | scenes | panel state at intake |
|---|---|---|
| `plaza_civic` | 01 · 08 · 14 · 20 · 21 · N1 · N3 | 5 in-repo |
| `street_arterial` | 06 · 11 · N5 | 18 (Commons Sidewalks) |
| `sidewalk_local` | 13 · N2 · N4 · D3 | 18 + in-repo |
| `river_levee` | 03 · 12 · 17 | **0 — blocking** |
| `lake_park` | 09 | 1 — top up |
| `park_trail` | 04 · 10 · C2 | 12 |
| `amphitheatre` | 05 | **0 — blocking** |
| `temple_precinct` | 07 | 1 — top up |
| `underpass_entry` | 02 · 16 | **0 — blocking** |
| `alley_hillside` | 15 · 18 | 13 in-repo |
| `rooftop` | 19 | **0 — blocking** |
| `industrial_transit` | D1 · D2 · D4 | 1 — **blocking** |

**Protocol (T-2).** (1) Pair the scene's `pt_noon_preset_h0.3_d5` cut with the panel photo whose
ground-plane share is closest. (2) Crop both to the bottom 2/3, sky excluded. (3) Compare on six
named axes **in this order, stopping at the first FAIL**: `species & silhouette` → `alignment &
pitch` → `setback & free width` → `surface content` → `edge & boundary treatment` → `tone`.
(4) Write the verdict as a sentence naming the photo. (5) Numeric assist, advisory only, from the
n=54 set: `slope −2.03 ± 0.18` · `grad_k 10.8 ± 5.3` · `flat_pct 10.2 ± 8.8` · `flat_gnd 3.9 ± 5.0` ·
`ori_axis p95 0.371` (alarm line).

**Checklist (T-3)** — every line is yes/no with a photo reference; any **no** = FAIL. Full text in
§10.6.

**Road-view services (Kakao / Naver roadview, Google Street View) are banned as evidence** —
in the panels, in the protocol, and in any spec row.

### 7.5 GATE-4 — gallery v2

`python3 scripts/make_review_gallery.py --round <full round> --out look_check/_review_w3
--status-json Docs/reports/regr_<round>.json`

Per scene: the 4 standard tiles (h0.3_d5 robot near · h0.9_d5 human mid · h1.8_d10 far · 1 mise-en-scène)
**plus**:
- **scene09's three diagnostic side cuts** `[ruled 07-30]` §1.7 — `stair_flank_raking`,
  `stair_flank_grazing`, `landing_return`. Not one existing cut crosses the flight axis, which is
  the entire reason the user cannot judge that stair;
- the scene's **archetype panel thumbnail** beside the h0.3_d5 tile, so the gallery carries the
  comparison the 통람 v3 bar demands.

---

## 8. GT-affecting ledger and re-cache steps

**Project law**: a geometry edit without a declared GT consequence is exactly how the W2
regressions happened. RT-I §4-N3 found two rows missing their flag; both are flagged below.

**"Re-cache" means, per row**: (1) the scene's own self-check re-derives and prints the hazard/drop
registry from the changed geometry; (2) a mini data render of that scene is re-run and checked with
`scripts/check_data_run.py`; (3) the OCCL/GRAZE baseline is re-stamped in the next `regr_*.json`.
The exact data-pipeline invocation is the data owner's — **the ledger row records the command
actually used**, it does not guess it.

| # | Change | Scene(s) | GT effect | Action | CB |
|---|---|---|---|---|---|
| **GT-1** | Flood sill: raised apron top **+0.18**, one 0.18 m riser at `x = −1.20`, descent from +0.18 | 02 | Drop edge at `x = 0` carries **3.38 m** instead of 3.20 m; a **new 0.18 m up-step** appears at `x = −1.20` — **label it an up-step, not a drop** | **Full re-cache** | CB-7 |
| **GT-2** | Curb reshape: top +0.10 above footway → flush … +0.02 | 02 | 100 mm vertical change on a walked surface; below the drop threshold but adjacent to the sill | **Rides GT-1's single re-cache** | CB-7 |
| **GT-3** | ~~Canopy deletion~~ **Full-length enclosed soffit-lit canopy REBUILD** `[supervisor amendment 07-31 · §14 MD-1b]` | 02 | No walked-surface z change **(unchanged by the flip)**; **OCCL baseline moves** ~~(four posts and a 2.4 × 4.9 m slab leave every cut)~~ — **prims are ADDED, not removed; the sign of the prim delta flips** (canopy line **+45**, commit total 391 → 545) | Re-stamp OCCL only **(class survives the flip)** | CB-7 |
| **GT-4** | ~~`upper_plaza` extended to the building faces (turf z = −0.63 → paving z = 0) + ground_kit region → (−16, −8, 0, 8)~~ **RETIRED — will never land** `[supervisor amendment 07-31 · §14 MD-2b]` | 01 | ~~**Height-field change** *and* every decal AABB moves (decorated area ×1.7). RT-I §4-N3's first missing flag~~ — **no z-profile effect remains; the row is dead** | ~~**Full re-cache + regr re-baseline.** `prim_cap=60` re-checked — expect to *reduce* per-element counts, not raise the cap. **HELD** by ruling 1.8 until T2 lands 5 plaza-to-plinth frames~~ — **the full re-cache retires with the row; the §1.8 hold is discharged, not satisfied; P-5 (§9) is dead** | ~~CB-11~~ **gate released** |
| **GT-5** | scene13 `walk_north/south` `proud=0.007` → a real 150 mm curb step | 13 | Real geometry change on a walked surface. RT-I §4-N3's second missing flag | **Full re-cache** | CB-9 |
| **GT-6** | S06-A: landing top 4.998 → 5.000, landing azimuth clipped at the deck edge, fascia stepped, railing `outer_r` 3.36 → 3.24, chord margin 1.03 → 1.000 | 06 (+ 05 · 19 · 13 share the builder) | **Designed to be GT-invariant** — r_in, r_out, azimuths and top-face z unchanged | **Prove invariance with a prim-hash / GT-delta diff** (the `96968f3` method). No re-cache if the diff is empty; a non-empty diff is a defect, not a new baseline. **Archive the judge baselines for 05 · 06 · 13 · 19 before touching `scene_common`** | CB-5 / CB-9 |
| **GT-7** | scene08 tempbar deletion removes **2 `TempPost_*` collision boxes** | 08 | Hazard/collision box list changes | **Re-stamp the OCCL/GT baseline** | CB-8 |
| **GT-8** | `_obb_aabb → _box_aabb` collapse on every patch and stain | all 33 | Element-registry AABBs become exact rather than OBB envelopes; `frame_budget` B1/B2/B5 inputs move. **Not** a hazard change | **Regression re-baseline + a note in the round stamp.** `regr_260730_w2d_fix.json` is retired here | CB-2 |
| **GT-9** | A1 weed cube → `Grass_Short_C` (footprint 0.10 → 0.28 m) | 22 scenes / 139 instances | GT class stays **A** (z unchanged) as long as h ≤ 0.12. But `_elem` aabb, `EDGE_STANDOFF = 0.80` and the **GT-E5 ramp clamp** all read the footprint | Recompute `_elem` from the scaled bbox; drive the asset scale from the **clamped** `proud`, or the ramp becomes decorative | CB-2 |
| **GT-10** | scene09 mooring/land posts moved off the stair face to the terrace edge or the lowest landing | 09 | Props, not walked surface | Verify no new occlusion of a hazard row | CB-1 |
| **GT-11** | scene05 arc-step / stage-disc wedge-gap closure | 05 | Real geometry defect repair; check whether the closed wedge touches a hazard face | Declare at the gate; expect class A | CB-10 |
| **GT-12** | building_kit B-F1 glazing un-burial (glazing moves 5 mm proud) | 23 scenes | Above ground, no GT | None; OCCL re-check only | CB-4 |
| **GT-13** | Far-tier skyline albedo override `[ruled 07-30]` §1.11 | 03 · 09 · 12 · 17 + N-series | No geometry. **GI rebound moves the judged ground band** (Δσ_LF up to −0.32, ≈4× the noise floor) | **Re-gate on B45/B30, not only B-HZ** | CB-10 |

---

## 9. Parked register

Nothing below may be implemented as a finished value. Each row names its gate and its owner.

| ID | Parked item | Gate that releases it | Owner |
|---|---|---|---|
| **P-1** | **scene07 archetype rebuild** — candidates C1 장대석 (26 courses, riser 0.162, tread 0.47, 3.40 m bars, 소맷돌 + 지대석) · C2 자연석 (`build_worn_stone_stairs`, 2–4 blocks per course, timber post-and-rail) · C3 hybrid. **Staged, not chosen.** The knob (`scene07:174-179`, 24 prims) dies with whichever archetype wins | **User reference images** `[ruled 07-30]` | S3 |
| **P-2** | **scene10 archetype rebuild** — candidate D1 (2 flights × 14, riser 0.150 / tread 0.360 / width 1.80, one 1.8 × 3.0 m rest platform, galvanised frame + 방부목 tread, total drop **6.60 m unchanged**). **Explicitly keep**: plank gaps (`flights.gap = 0.02`), the stone pit / log fence, and **`rail.broken_landing = 0`** — the missing railing bay is this scene's negative-obstacle cue and must survive any rebuild | **User reference images** + the **KDS 34 00 00 단높이/단너비 verbatim text** (clause located, text never fetched) `[ruled 07-30]` | S3 |
| **P-3** | **S08-B** — what replaces the barrier at the parapet gap. Options B-1 close the gap and move the cue to the stair head (recommended) · B-2 stainless 안전난간 1.1 m · B-3 a deliberately missing railing panel with post stubs (the `scene06 railing.broken=(180,270)` pattern) | **n ≥ 5 photos of finished Korean 선큰광장 pit edges** (청계광장 · 서울광장 · 광화문 · COEX/영동대로 · 시청역/을지로), from news or municipal press releases. Commons is thin; road-view banned | T2 → S6 |
| **P-4** | **G-6 / 04-B gravel deposition** — mask to the trail polygon, `cover_fn` with edge (λ_e 0.25 m) + track (σ_t 0.35 m on the existing wear-lane centreline) + low-point terms, mean cover held at the profile's declared value, size sorting bound to the density term | **5 plates showing armouring / rill / edge deposition on a 마사토 surface** — 산림청 「등산로 정비 매뉴얼」 · 「사방기술교본」 · 서울시 「등산로 정비 매뉴얼」 `[ruled 07-30]` §1.8 | T2 → K1 · K4 · S5 |
| ~~**P-5**~~ **P-5 — DEAD** `[supervisor amendment 07-31 · §14 MD-2]` | ~~**01-B paving to the building faces** (+ the same audit on 02 · 05, and 08 · 14 · 16 · 20 · 21)~~ — **the parked item is superseded**: GT-4 is `RETIRED` (`gt_changes_w3.md` §3 GT-4 · §9-2), so there is no 01-B paving extension left to release | ~~**5 frames showing a paved plaza meeting a building plinth with no turf gap** — `Category:Hangang Park` (~60 files) + Commons university subcategories `[ruled 07-30]` §1.8~~ — **the evidence gate is DISCHARGED, not satisfied**: T2 owes S1 nothing on this row and no frame set need be harvested for it | ~~T2 → S1~~ **none** |
| **P-6** | **04-A shrub massing** — 3 tuft rows → a continuous groundcover band; 2 shrub rows → 3–4 clumps of 3–7 of one species following the slope contour. Also the vehicle for scene13's apartment-court planting (X4) | **산림청 「가로수 조성관리 매뉴얼」 planting-pattern plates** `[ruled 07-30]` §1.8 | T2 → S5 |
| **P-7** | **The 6 prop-edge rows M1–M6** — bench back-face offset and seat-axis convention · lamp pole-centre offset (interim 0.35–0.60 m, nominal 0.45, `[assumed]`) · bin offset and pairing · planter curb-vs-module registration · sign-post offset and panel clear height · whether benches sit between trees, on the tree line, or offset | **Pixel measurement on ≥ 5 frames each** from the named Commons populations, using the standard scale references (보도블록 300×300 / 200×100 · 점자블록 300×300 · 볼라드 Ø100–200 · 맨홀 Ø648). **LINT-9 stays WARN until then** `[ruled 07-30]` §1.8. Enforcing a guessed setback is worse than none | T2 → T1 |
| **P-8** | **5 empty archetype panels** + 2 top-ups (§7.4) | T2's harvest. **Blocks GATE-3 for those scenes** `[ruled 07-30]` §1.8 | T2 |
| **P-9** | Street-row tree lean cap **1.5°** (`[assumed]` — sounds right for staked nursery stock, no source found) | Photo check, or drop the row and keep `U(0°, 4°)` | T2 → K4 |
| **P-10** | **RF-4 retrofit tactile as an adhered pad** — proud +6…+12 mm, 1–2 mm dark adhesive perimeter, outline **not** aligned to the paver grid, 1–2 tiles with corner loss | **Double-blocked**: (1) tactile is default-OFF by user decision and must not be flipped by an implementer; (2) at 12 mm proud, **GT-E1′** (`\|x_e\| ≥ 40·z_e`) demands 0.48 m clearance against the statutory 0.30 m position → needs the same `GT-E2-x` / `EXPECTED_FP` registration as the flush case. **Record the spec, build nothing** | K5 |
| **P-11** | **E3b sceneD3 utility poles** → KS F 4304 PC pole, tapered grey, cross-arm, 2–6 insulators | **§2.13② is unruled**: the convention bans urban infrastructure in "natural" scenes and lists D3 as natural, while the scene header defines itself as 도시 콘크리트 측구 / 교외 아스팔트 차도 and 지중화율 (arterials 94.16 %, **all roads 59.2 %**) makes poles on a suburban back road statistically normal | supervisor |
| **P-12** | **C6c bollard front tactile pad** — **12 of 42 ON (C4 6 · N5 6)**, not 39/41 (C-17) | User owns the tactile-OFF decision. Do not touch | supervisor |
| **P-13** | Kerbless-by-design confirmation for **03 · 12 · 17** (levee crown road 1.5 mm · 자전거도로 2 mm · crown walk 6 mm) | Photo check that Hangang levee roads and 자전거도로 really are near-flush before they are locked as "correct" | T2 → S3 · S4 |
| **P-14** | **The 0.5–1.1 m single-boulder band is still unfilled** (`rock_02` reaches 0.463 m, `rock_03_broken` starts at 1.714 m, PH `stone_01` is a 147 mm pebble at 53,520 tri) | Open procurement row. **Do not block on it** `[ruled 07-30]` §1.11 | procurement |
| **P-15** | scene14 **D11 parapet haunch emission** — real geometry bug (sky and grass show *through* the V valleys, so material is genuinely absent between teeth), invisible in the h0.3 judgement cuts | tonglam §2.1 ruled **defer-W3 structural repair, keep the scene**. Not in this wave's fix budget | — |
| **P-16** | scene05 **stage black wedge gaps** | Separate stage-redesign package (`Docs/briefs/scene05_stage_redesign_v1.md`) | stage owner |
| **P-17** | `sign_kr101` measures **0.844 m** against the 900 mm 주의표지 standard (the standard itself is still `[assumed]`) | Held at the **연대 3요소** gate. **No uniform rescale** — the 2xx/3xx families have different standard sizes | S-WPs |
| **P-18** | `bench_park_05` re-imports `bench_curved_01`, which survey R2 §5.3 lists as explicitly not procured (C-26) | Supervisor: is that list binding? If yes, drop `bench_park_05` | supervisor |
| **P-19** | 507 CC0 ambientCG decals (Facade 26 · Sign 26 · Leaking 39 · RoadLines 69 · LeafSet 30 · SurfaceImperfections 20) and SimReady props | Outside this brief's named scope; a ~15-line `--only` group if W3 wants them | procurement |

---

## 10. Merged spec-row index

### 10.1 Jitter — the abolish inventory (13 rows) `[ruled 07-30]` §1.2

| # | Site | Randomises | Amplitude | ID | WP |
|---|---|---|---|---|---|
| 1 | `ground_kit.py:689` (default) → `:733` | repair-patch yaw | `U(−14°, +14°)` | J-1 | K1 |
| 2 | `ground_kit.py:1027` | free-blot yaw (`dirt/water/oil/gum/efflorescence/drip`) | `U(−22°, +22°)` | J-2 | K1 |
| 3 | `batch1_common.py:248` `jit_yaw()` | furniture yaw, random sign | default `[3°, 8°]` | J-3 | K2 |
| 4 | `batch1_common.py:256` `jit_pos()` | furniture position, isotropic | amp 0.12–0.20 m | J-4 | K2 |
| 5 | `scene01:175-177` | 6 bench yaws | −6 / +4 / −5 / +3.5 / −7 / +5 | J-5 | S1 |
| 6 | `scene06:262` | 3 bench yaws | −6 / +5 / 175 | J-5 | S4 |
| 7 | `scene11:233` | 2 bench yaws | 86 / −94 (= ⟂ ± 4°) | J-5 | S4 |
| 8 | `scene03:235,237,239,257` | 3 city-block + 1 pavilion `jyaw` | +3.5 / −4.0 / +2.5 / −3.0 | J-5 | S3 |
| 9 | `scene04:276-277` | 5 bench yaws | 96 / 94 / 4.5 / 93 / 87 | J-5 | S5 |
| 10 | `scene17:270-271` · `scene13:223,235` · `scene09:269-270` | dressing / bench yaws | ±3–8° · 174/−6/+3 · 86.5/274.0/93.5/265.5 | J-5 | S4 · S5 |
| 11 | `sceneD1:855` `rotz = yaw + crng.uniform(−9, 9)` | stacked-crate yaw | ±9° | J-5 | S8 |
| 12 | `sceneD1:153` `yaw=-14.0` · `sceneD2:210` `yaw=-22.0` | fixed off-axis site props | −14° / −22° | J-5 | S8 |
| 13 | `scene06:255-260` · `scene11:229-233` · 12 · D3 · N5 tree tuples | street-row **pitch** irregularity | 6.6–7.2 m (06) · 7.4–7.6 m (11) | J-6 | S3 · S4 |

Plus scene03's 4th bench at **187°** (C-13), and scene01/03/04's benches also carry the anchor rule
below. **Row 13 excludes scene13** (X4, §1.2).

**Replacement rule, not just deletion.** Jitter was substituting for "these look like clones". The
real cure is structural: an object takes the **bearing of the thing it belongs to** (kerb line, wall
face, planter cap face, path tangent) and varies by **size, model and interval** — never by angle.
Where a run of identical furniture reads as clones, vary the **interval against a real cause**
(a tree pit, a manhole, a doorway). For the current 33 scenes the resulting bearings are
`0 / 90 / 180 / 270` plus scene03's meander tangent, which is a legitimate alignment (the levee
curves, so the furniture on it curves with it) and must be preserved.

**Directional yaw is not jitter and must not be swept up**: `ground_kit.py:1102` (`wear_lane`),
`:1130` (`edge_litter`), `:1166` (`edge_break`), `:816/825/836` (patch cut lines), `:863/877`
(gutters) all take `yaw = atan2(...)` from a centreline. Same for `build_stain_field`'s
`grime_band` and `tire` kinds, already forced to `yaw = 0.0` by the `line is not None` branch.

### 10.2 Species — the single per-scene table `[ruled 07-30]` §1.3

`VEG_SPECIES` (replaces `VEG_TREES` as the source of truth; all ten rows are `verdict: PASS` in
`assets/veg_manifest_w2.json` with measured `zmax`):

| key | rel path | native h | role |
|---|---|---|---|
| `elm` | `Trees/Elm_Sapling.usd` | 3.0867 | street near-field |
| `oak_pin` | `Trees/Shumard_Oak.usd` | 10.8989 | street broadleaf |
| `ash` | `Trees/Fraxinus.usd` | 5.3408 | street broadleaf |
| `birch` | `Trees/Gray_Birch.usd` | 3.3294 | park / apartment |
| `poplar` | `Trees/Lombardy_Poplar.usd` | 13.6709 | riverside |
| `juniper` | `Trees/Chinese_Juniper.usd` | 2.5164 | temple / office evergreen |
| `fir` | `Trees/Douglas_Fir.usd` | 6.0263 | temple / mountain conifer |
| `oak_red` | `Trees/Scarlet_Oak.usd` | 12.4089 | park broadleaf |
| `oak_black` | `Trees/Black_Oak.usd` | 19.7389 | far-background broadleaf |
| `spruce` | `Trees/Colorado_Spruce.usd` | 3.8713 | far-background conifer **only** — `tri_effective` **15,597,637** |

**Retired**: `White_Pine` (uncorrected `zmin −0.351`, not in the PASS manifest) · `Yellow_Pine`
(not in the PASS manifest). Every A-table row naming them is re-mapped.

| scene | identity | route species | belt `▸` | why |
|---|---|---|---|---|
| 01 | 캠퍼스 계단 | **elm** | — | zelkova substitute; 3.09 m suits the 3.0 m planters and the h0.3 near field. **Resolves X1** against A's `Shumard_Oak` — a 10.9 m oak is out of scale for a 3.0 m planter |
| 03 | 하천 제방 | **poplar** | ▸ oak_black (far bank) | 양버들 is the signature Korean riverbank silhouette; kills the five-silhouette frame. **Resolves X1** — A's `Yellow_Pine` is retired |
| 04 | 공원 침목길 | **oak_red** | ▸ oak_black | park broadleaf stand. **Resolves X1** — A's `Yellow_Pine` backdrop is retired |
| 05 | 야외공연장 | **ash** | — | 이팝나무 substitute, civic-plaza standard since the 2000s. **Resolves X1** — 01 already takes elm, and 05 is civic |
| 06 | 보행육교 나선 | **oak_pin** | — | the library's flagship arterial row (20 trees, 2 verges) |
| 07 | 산사 돌계단 | **juniper** | ▸ fir | 향나무 is the temple/관공서 species; the mountain behind is a different stand |
| 09 | 호수공원 수변 | **birch** | ▸ oak_black | lake-park amenity planting |
| 10 | 공원 데크 갈지자 | **oak_red** | ▸ oak_black | same park family as 04 |
| 11 | 보도육교 | **ash** | ▸ (TreeBlob band → midground) | arterial sidewalk file, 16 trees on 2 strips |
| 12 | 수변 데크길 | **poplar** | — | riverside, matches 03 / 17 |
| 13 | 지하주차 진입부 | **birch** | — | apartment-complex landscaping (pitch untouched — X4) |
| 14 | 착시 대계단 | **ash** | — | civic |
| 17 | 한강 제방 | **poplar** | ▸ oak_black | Han river levee |
| C2 | 낙엽 매몰 계단 | **oak_red** | — | **forced by the debris asset**: `assets/vegetation/Debris/` ships `oakfall1/2.usd` — an oak leaf blanket under an oak |
| D3 | 노변 배수로 | **oak_pin** | — | rural arterial verge |
| N4 | 완경사 램프 | **elm** | — | near-field, ramp corridor |
| N5 | 플러시 그레이팅 | **ash** | — | street trees A/B/C on one verge |

**02 has no row** (C-4). Scenes with no `build_tree` call — 02 · 08 · 15 · 16 · 18 · 19 · 20 · 21 ·
C1 · C4 · D1 · D2 · D4 · N1 · N2 · N3 — are unaffected by S-1; several are affected by S-2.

**S-2 shrubs, one species per bed / band**: clipped evergreen hedge → `Holly` (1.44) or `Privet`
(1.11), one species per continuous band · formal planter accent → `Yew` (0.71) · narrow border →
`Cedar_Shrub` (0.88) · verge turf → `Grass_Short_A/B` (mixing allowed — it is turf, not planting) ·
edge weed → `Grass_Short_C` · riparian band → `Switchgrass`. `place_shrubs(...)` gains `species=`
and the `randrange` at `scene_common.py:2819` is removed. `Rhododendron` keeps its
`_deactivate_seasonal` treatment and is admissible only as a single-species ornament bed.
**Note**: `Privet`, `Boxwood` and `Holly` share one leaf texture (`hollyprivet_basecolor.png`) —
they differ by silhouette and scale only, so never place two of them side by side expecting a
species contrast. `VEG_SHRUBS` must also drop `Forsythia` and `Burning_Bush` (already adjudicated)
and gain `Holly` / `Yew` / `Cedar_Shrub`.

**S-4 within-species variation**: keep `trunk_h × 1.60 × U(0.92, 1.08)` (±8 %) · keep crown bearing
`U(0, 360)` · **add the statutory floor on street rows: height ≥ 3.5 m and trunk Ø ≥ 0.10 m at
breast height** (서울 시행규칙) · lean cap **parked** (P-9). Honest limitation to state and not
promise around: `add_vegetation` applies **one uniform scale**, so a ±8 % height instance is also
±8 % in DBH — "same species, different age" is **not expressible** with the current pipeline.

### 10.3 Prop-edge distance rules — `PROP_EDGE`

Datum: the **walking-zone edge** (보행안전공간 boundary); on a sidewalk with a carriageway, also the
**보도·차도 경계선**.

| # | Prop | Rule | Value | Basis |
|---|---|---|---|---|
| PE-1 | 가로수 | trunk centre from the kerb line | **≥ 1.00 m** | 산림청 고시 2-3(6)(가)1) `[law]` |
| PE-2 | 가로수 | longitudinal pitch, **constant** | 6–8 m (조례 제7조1가) / 4–8 m (고시) → default **7.0 m** | `[law]` |
| PE-3 | 가로수 | planting form | **row parallel to the road alignment**; no yaw, no lateral offset | 조례 제7조1나 · 고시 (나) `[law]` |
| PE-4 | 가로수 (no sidewalk) | from the shoulder end | **≥ 2.0 m** (conditionally 1–2 m) | 고시 2-3(6)(가)2) `[law]` |
| PE-5 | 수목보호판 | opening min width; cover offset below grade | **1.5 m**; **≥ 5 cm** | 고시 2-3(5)(가) `[law]` |
| PE-6 | 볼라드 | height / diameter / pitch / front tactile | **0.8–1.0 m** / **Ø0.1–0.2 m** / **1.5 m 안팎** / 0.3 m 점형블록 | 교통약자법 시행규칙 별표2 제7호 `[law]` |
| PE-7 | 볼라드 | position | **on the 보도·차도 경계 line**, axis-locked; only at vehicle-entry points | 별표2 + v5.1 §2 `[law]` |
| PE-8 | any 노상시설 | must not eat the effective walking width; furniture stands in a **노상시설대 added on top of it** | effective width **≥ 2.0 m** (national); 1.5 m is the constrained-condition floor only | 「도로의 구조·시설 기준에 관한 규칙」 제16조 `[law]` |
| PE-9 | 승차대 ↔ neighbouring 시설물 | separation | **≥ 1.5 m** | `[law]` |
| PE-10 | 점형블록 ↔ 연단 | offset | **0.30 m** | 교통약자법 `[law]` |

Obstacle widths, 「보도 설치 및 관리 지침」 표2.2 `[law]`: 가로등 0.8–1.0 · 교통신호등 지주 0.9–1.2 ·
교통안전표지판 0.6–1.8 · 우체통 1.0–1.1 · 공중전화박스 1.2 · 휴지통 0.9 · 지하철환기구 0.8 ·
**가로수 0.9–1.2** · **가로수보호지주 1.5** · 신문가판대 1.2–2.0.
Derived, computable form of PE-8 `[derived]`: `setback_far_edge ≤ sidewalk_width − 1.5 m` and
`setback_near_edge ≥ 0`, with the prop's occupied width taken from 표2.2.

**점형블록 note.** 별표2 requires a dot strip 0.3 m in front of a bollard, but 점자블록 is
**default-OFF by supervisor ruling** (`user_feedback_v5_1.md` §7: *"규정상 옳아도 현실 빈도 낮음"*).
That decline **stands and is restated here** so it is not re-litigated per scene.

### 10.4 The linter (T1) — `scripts/placement_lint.py`

Scenes expose a small additive block, no geometry change:

```python
PLACEMENT = dict(
    walk_edges = [((x0,y0),(x1,y1)), ...],   # walking-zone boundary polylines
    kerb_lines = [((x0,y0),(x1,y1)), ...],   # 보도·차도 경계
    anchors    = {"planterA": dict(face_bearing_deg=0.0, ...), ...},
    routes     = {"verge_S": dict(pts=[...], species="oak_pin", pitch_m=7.0), ...},
)
```

| check | rule | hard? |
|---|---|---|
| LINT-1 | tree lateral offset from `kerb_lines` ≥ 1.00 m (PE-1) | hard |
| LINT-2 | route pitch constant within 1 %, in [6.0, 8.0] m (PE-2) | hard |
| LINT-3 | route bearing = kerb bearing ± 0.5°; per-tree yaw offset = 0 (PE-3) | hard |
| LINT-4 | one species per `routes[*]` (S-1) | hard |
| LINT-5 | free walk width ≥ 1.5 m after subtracting the 표2.2 occupancy (PE-8) | hard |
| LINT-6 | bollard pitch 1.5 ± 0.1 m, Ø ∈ [0.1, 0.2], h ∈ [0.8, 1.0], yaw = kerb bearing (PE-6/7) — carrier set per C-9 | hard |
| LINT-7 | furniture yaw ∈ {declared anchor bearings} ± 0.5° (J-3 / J-5) | hard |
| LINT-8 | no `rotz ≠ 0` on any `patch` / `stain` element (J-1 / J-2) | hard |
| LINT-9 | bench / lamp / bin setback within the measured band (M1–M6) | **WARN until P-7 lands** |
| LINT-10 | any `jitter=` kwarg > 0 in scene code (J-11) | hard |

**Do not extend `frame_budget`.** It reads `plan["elements"]`, the ground-kit element registry only;
props are scene-owned prims and are structurally absent from it. The two tools answer different
questions (pixel occupancy vs geometric legality). `placement_lint` runs in the same pre-flight slot
as `geom_invariance_check`.

### 10.5 Named scene-side specs

**DEC-1 `build_blot()`** — new `ground_kit` primitive, geometry only:

```python
def build_blot(kit, path, cx, cy, rx, ry, mtl, *, n=16, rough=0.35, seed=0, z, proud):
    """Irregular flat lobe. A closed N-gon whose radii are r_i = r*(1 + U(-rough, rough)),
    once-smoothed (r_i <- (r_{i-1} + 2 r_i + r_{i+1}) / 4) so no vertex spikes. 1 Mesh prim."""
```
**1 prim**, same as today → no budget change. AABB = the polygon bbox, exact. Deterministic from
`(path, seed)` via the existing `det_rng`. **No alpha, no opacity, no texture** — deliberate:
`add_vegetation`'s own comment records that `enable_opacity` breaks the vegetation assets, and an
alpha-masked ground quad adds a sorting surface at grazing angles, which is exactly the viewpoint
the dataset lives at. Rejected alternative: a procedural mask texture — it costs a generation step,
a UV convention and an alpha path for a silhouette an N-gon already gives.

**DEC-2 carpet edges** — `build_blot` at low `rough` (0.15–0.20) and high `n` (24), plus a
**feather ring**: `place_scatter` lays individual leaf cards in a band straddling the mask boundary
(inner 0.3 m / outer 0.5 m), density falling to zero outward, using the on-disk
`assets/vegetation/Debris/{oakfall1,oakfall2,maplefall1,fallcluster1,2}.usd`. **Drift bias**
(mask centroid pulled toward the nearest vertical obstruction and elongated along it) is the part
that makes it read as real — and it is **parked with P-4's evidence**: build DEC-1/DEC-3 first,
they are already evidenced. **scene C2 additionally**: the buried risers render the leaf texture as
compressed-leaf laminate on **vertical faces** — a separate binding bug (vertical faces must not
receive the plan-view leaf texture) that must be in the same package or C2 fails the same crop.

**DEC-3 patch axis lock** — keep the rectangle (real 절삭·덧씌우기 patches **are** saw-cut
rectangles) and take the yaw from the profile's `unit_cell` axis (`ground_kit.py:288-289` already
carries the per-profile ledger), else 0. Keep `cutline=False`. **Additionally snap to the paving
module** where the profile declares one: quantise `w`, `h` to an integer multiple (600 mm for P1)
and quantise `cx`, `cy` so the patch edges land on joint lines — a real repair in flagstone paving
is an integer number of whole or half flags. scene01's plaza patch count drops 2 → **1**.

**A1 weed placement contract** — the builder's own docstring already states the correct rule and
the code ignores it (`ground_kit.py:2782`: *"Boundary weed band — clump by clump in joint lines and
gutter cover gaps"*), while `:2797` pins `cy` to the **region bounding box**, which for scene01 is
an invisible line in the middle of a 16 m plaza. Fix: `_build_weed_band(..., lines=[...])` sampling
along real discontinuities (joint lines from `build_joint_grid`, the kerb polyline, manhole/gully
frame perimeters). scene01's `plaza_granite` weed count → **0** (a maintained campus plaza has no
weeds in the field).

**S06-A spiral repair** (scene06; blocked on T3):
1. Replace the constant-chord box in `build_arc_steps` / `build_helix_steps` / `build_helix_ramp`
   with a **true annular-sector mesh** (4 radial corners per segment). Fallback if a prim-budget
   rule forbids meshes: cap Δθ so the r_in overwidth ≤ 1.05× — but for the landing (r_in 0.48 /
   r_out 3.30, a 6.9:1 ratio) that needs `seg ≈ 165`, i.e. boxes are simply the wrong primitive.
   **Recommend the mesh.**
2. Drop the **1.03** margin to 1.000 once the sector lands — the margin exists only to close wedge
   gaps a true sector does not have, and it is what creates the 23 coplanar 12.9 mm overlap bands.
3. **Fascia**: stepped top line, one segment per tread, top z = that tread's z + a fixed 20–30 mm
   nib, riser face vertical. This is also what a real RC spiral looks like (a stepped 옆판 line, not
   a helicoid). Delete `z_off` or repurpose it as the nib height. It currently produces a
   **+153.6 / −38.4 mm sawtooth, 26 times round the helix** — a documented design device that the
   renders show failing.
4. **Landing ↔ deck**: clip the landing azimuth at the deck edge (or subtract the deck footprint).
   **One walking surface at one z** across x 2..5, y −13..−9.7. Set landing `top_z = 5.000` equal to
   the deck — the 2 mm was a Z-fight dodge that no longer applies once the 348 mm interpenetration
   over 9.9 m² is gone.
5. **Railing** `outer_r` 3.36 → **3.24** (post centres 60 mm inboard of the nosing). Re-derive
   `_pipe_arc` radii from it.
6. New **`spiral_selfcheck()`** in the house style, asserting: rim radius spread < 5 mm · no two
   slabs with |Δz_top| < 20 mm sharing a footprint · fascia top ≥ tread top over the whole span ·
   every post centre ≤ r_out − 0.05.
7. The convention fix also touches **05** (10 `build_arc_steps` sites), **19** (4), **13**
   (`build_helix_ramp`) — re-render and re-judge all four in the same round, and **archive the
   judge baselines before touching `scene_common`**.

**S06-B curb** — new `infra_kit.build_curb_line(kit, path, p0, p1, mtl, height=0.15, width=0.20,
unit=1.0, arris_r=0.010, gutter=True, drop_spans=[...])`. Height rule: exposure above carriageway
**150 mm default / 250 max / 100 min**; curb top **flush … +20 mm** relative to the footway.
New material role **`curb_granite_light`** — do **not** reuse `granite_dark` (scene01 already
recorded that it "reads as a black hole"). Segment the monolith: scene06's curb is currently **one
box 140 m long**. **턱낮춤**: wherever a crossing, a bollard row or a plaza entry meets the
carriageway, drop the curb to ≤ 20 mm over the crossing width — scene06 has a bollard row at
`y = −9.30` with no corresponding drop. Per-scene: **02** shape fix · **06 · 11** legibility
(material, segmentation, L-gutter) · **13** build outright (call the existing uncalled
`build_ramp_curb`, 10–15 cm per 주차장법 시행규칙 §6①5다, and raise `walk_north/south` from
`proud=0.007` to a real 150 mm step) · **08** delete the lane markings painted on a plaza with no
road slab, or build the road · **16** material without geometry · **03 · 12 · 17** verify, do not
auto-fix (**P-13**).

**S08-A scene08 tempbar removal** `[ruled 07-30]` — six edits, **all ranges re-derived from anchors,
never from the literal line numbers** (C-7): the `build_tempbar(M)` call under `cfg["cue_sign"]`;
the `build_tempbar` builder; the `tempbar=dict(...)` params; the three materials
`M["tempost"]`, `M["tempost_b"]`, **`M["temtape"]`**; the **2 `TempPost_*` collision boxes**
(→ GT-7); the v6 C-6 dimension self-check block. `cue_sign` still governs `build_signs(M)`, so the
toggle keeps a job. Same commit: the **5-bollard row at x = −18** (mid-plaza, no carriageway in
front of it) is deleted under the C6b rule, and the `road_lines` at y = ±30 painted on a plaza with
**no road slab** are deleted.

**S09-A three diagnostic cuts** (additive `out["<name>"] = dict(eye=[...], tgt=[...])` inside
`build_views`, after `views["park_vista"]`; **no `sc.grid_views` change, no preset touched**, so the
13 preset cuts stay byte-identical and the judgement baseline is unaffected):

| name | eye | tgt | proves |
|---|---|---|---|
| `stair_flank_raking` | `[15.00, −11.00, −2.20]` | `[5.50, 0.00, −3.60]` | **Primary.** Bearing 130.8°, pitch −5.5°, range 14.60 m; eye over water 3.04 m up (a boat/mast height). The whole 36-riser stack in raking profile against the water, both landings visible as breaks in the rhythm, waterline cutting the flight |
| `stair_flank_grazing` | `[1.20, 4.60, 0.55]` | `[11.00, 4.60, −4.60]` | Eye on step 3, 1.23 m above the tread, looking down the flight. The risers face **away** — the concealment case, the same read the h0.3 grid tests, without touching a preset. Does the nosing line collapse into one plane? |
| `landing_return` | `[4.34, −8.20, 0.20]` | `[4.34, 0.60, −2.10]` | Cross-flight close-up on landing 1: the 1.20 m landing tread against the 0.34 m steps, the flank/cheek condition, the terrace junction. **Verify against the side-slope profile (`scene09:185`) before committing** — the eye is set at z +0.20 so the south slope cannot occlude |

Lighting constraint, derived not assumed: `scene09` sets `SUN_AZ_OFFSET = 0.0` with
`hdri_sun_rotz_offset = 233.5`; mooring-post shadows fall toward +Y, so **the sun is on the −Y
side** and a flank camera must sit at **+X and −Y** to keep both the risers and the flank front-lit.

### 10.6 T-3 "identical to sample" checklist

**All scenes** — [ ] every object class visible in the panel photos is present, and no class is
present that is absent from all panel photos ("no invented objects") · [ ] no built object is
rotated off its anchor's bearing · [ ] no decal has a straight edge that is not a construction
joint, a saw cut or a kerb · [ ] surfaces the panel shows as worn are worn, and surfaces it shows
as clean are clean.

**Tree-route scenes** (01·03·04·05·06·07·09·10·11·12·13·14·17·C2·D3·N4·N5) — [ ] **one species** on
the route; a second only as a declared separate belt · [ ] pitch constant, 6–8 m, gaps only at
crossings / driveways / entrances · [ ] trunk centres ≥ 1 m from the kerb line, on one straight or
one smoothly curving line · [ ] 수목보호판 where the tree stands in paving: ≥ 1.5 m opening, cover
≥ 5 cm below grade · [ ] street-tree height ≥ 3.5 m, trunk Ø ≥ 0.10 m.

**Sidewalk scenes** (02·06·11·13·16·D3·N2·N4·N5) — [ ] free walking band ≥ 1.5 m after every
노상시설 · [ ] furniture forms a **single line** parallel to the kerb, not a scatter · [ ] bollards
only where a vehicle could enter; pitch 1.5 m; Ø 0.1–0.2 m; h 0.8–1.0 m.

**Plaza scenes** (01·05·08·14·20·21·N1·N3) — [ ] benches sit against an edge (planter, wall, level
change) with the seat axis parallel to it · [ ] the central axis is empty (v5.1 씬21 ruling) unless
the panel shows otherwise.

**Water scenes** (03·09·12·17) — [ ] bank vegetation is one species along the reach · [ ] water is
not a mirror plane (carried W3 item).

**Stair scenes** (all hazard scenes) — [ ] nosing, handrail and tactile treatment match the panel's
**era vocabulary** (`era_consistency_survey_v1.md` §6.2).

### 10.7 Era riders folded in (`era_consistency_survey_v1.md` §5 / §6.2)

| Rider | Content | WP |
|---|---|---|
| **RF-1** (§5.0) | **The post does not grow out of the ground; it stands on a plate bolted to the ground.** Plate **100 × 100 mm in 6T / 8T / 9T** (market stock — preferred over the repo's 120 × 120 × t9), 4 × Ø16 anchors at 90 mm pitch `[no source — keep the tag]`, one levelling-nut course, a 5–15 mm mortar/epoxy bedding smear, a tone break in the slab and the drill-dust ring that never cleans off. Apply to the **retrofit** posts of 02 · 11 · 15 · 16 · 17; leave the EXPECTED scenes (01 · 06 · 08 · 13 · 14 · 20 · 21) embedded with a mortar collar — **the contrast between the two is the deliverable, not the plate** | K4 + S2 · S3 · S4 · S6 |
| **RF-2** (§5.1, §6.2-C) | Three-rung age ladder: 1970s–80s painted mild steel (albedo 0.20–0.35, rough 0.55–0.75, chip/rust at joints and feet) · 1990s–2000s hot-dip galvanized (albedo 0.45–0.55, **rough 0.45–0.60**, faint spangle, white bloom in crevices) · 2000s–2010s STS304 (metallic 0.9 but **rough 0.30–0.40**, brushed anisotropy along the tube axis). Our universal `metallic 0.9 / roughness 0.35` mirror stainless is wrong **as a default**. Two more rules: repaint **does not reach behind brackets or under the top rail** → model as a tonal split; **galvanizing fails at welds and feet first** → rust-map those, not the whole member. Grip: Ø34 stays the compliant default, **Ø42.4 STS304 is the retrofit variation value, not an error**. Do **not** over-apply the matt-galvanized default to stair handrails — bright green and white-and-blue are both real and current | K4 |
| **RF-3** (§5.0b) | Polished spherical **newel ball** · curved **goose-neck return** · turned/beaded **ring grooves** on balusters · balusters at ~100 mm centres · **a row of inverted-U stainless hoop guide rails across the stair head**, perpendicular to travel — a standard Korean fixture with **zero instances in 33 scenes**, and the highest-value new prop in the map | K4 |
| **RF-5** (§5.4, §6.1-11) | Three nosing tiers, currently collapsed into one chrome yellow: **retrofit metal** (Al profile 60 mm wide, 600–790 mm in 10 mm increments, ceramic-grit insert; tells = a regular row of screw heads *or* adhesive squeeze-out along both edges, a height step casting a shadow at the uphill edge, the strip ending short of the tread ends, wear mismatch) · **paint only** (흰여울: white paint on every nosing, no railing, a white-painted open gutter as the only safety measure) · **partial-width tile** (Gamcheon: anti-slip tile over only the front ~150 mm). And the statutory alternative that licenses absence: 편의증진법 별표1 제8호 마.(2) accepts **cast-in 줄눈 grooves with no strip at all**, so a visible strip is almost always an add-on. Era-conditional application: **pre-code 02·11·15·18 → applied strip; 2010s 08·10·12·14 → cast/grooves; stone & natural 07·03·04·09 → absent.** Colour **5Y 8.5/12 ≈ `#F0BE00`** (산업안전보건법 별표8), not an invented yellow — this also discharges tonglam's chrome-yellow flags on 16 · C4 · N4 | K4 + S-WPs |
| **RF-6** (§5.5) | The scars, not the fixture: a 100–200 mm **mortar patch** where an old post was cut off and a new one set beside it · the **cut stub** of the previous rail left in the parapet (this repo logs "허공 파이프 스텁" as a *defect* in scene15 — placed deliberately it becomes a feature) · **core-drill dust halo** + four small spalls around a base plate · **two generations meeting mid-run** with a mismatched joint sleeve (scene12's 훼손 스팬 is the in-repo precedent) · a **colour break in the tactile run** · **rust staining streaking down the stone from the steel fixings**. Look target, already in-repo: `Docs/reference_photos/expanded/wc005_ccby40_caddc6_삼일공원_1.jpg` — four fixture generations, none matching, none removed | S2 · S3 · S4 · S6 |
| **§6.2-B** | **Rail height 0.90 m outdoors is the wrong default.** Outdoor = 1.10 m; 옥상·노대 = 1.1 m pre-2005-07-18 / 1.2 m after. Make it era-driven; **scene19 → 1.1 m** | S6 |
| **§6.2-D** | **Uniformly saturated tactile yellow is the look of a brand-new installation only.** The ≥ 8 mm colour layer abrades along the walked line, leaving **grey concrete with yellow surviving only at the edges** and ring outlines where the dots are. Statutory replacement threshold: dot height ≤ 3.5 mm — use it as the worn-state target. **sceneD4's worn grey-ochre strip is the library's only correct worn tactile and is the reference — do not clean it up** | K5 + S8 |
| **§6.2-A** | Tactile dot **Ø25 mm vs KS F 4561's Ø35 mm** — **do not revert yet**; procure KS F 4561:2022 first. The current value sits on the **Japanese** figure and contradicts the project's own no-Japanese-assets rule | parked |
| **§6.1-3** | **06 landing EXECUTE, reason replaced** — 육교 is outside 건축법, so "post-dates the statute" is withdrawn; it survives because a 2000s footbridge under 도로/교통약자 guidance does not get built as a 5 m continuous spiral with no rest landing. W4 item, noted here so CB-9 does not foreclose it | W4 |
| **§6.1-1/2/5/8/9/10** | Landings CANCELLED for **02 · 03 · 17**; mid-rails CANCELLED for **09 · 18 · 05**; **02 mid-rail CONVERTS** to retrofit-style (a single centre stainless pipe on base plates, no infill — the most common real form, 5/11 of railed cases in the alley survey). 09's 무난간 water-viewing steps are documented practice; three rails across a 10 m viewing terrace would be a code-correct fabrication | W4 (02's conversion informs S2's vocabulary now) |

### 10.8 Building track (survey R3 §7, after K3's B-F1)

| # | Action | Measured reason | WP |
|---|---|---|---|
| **BS-1** | `brick_red` `scale_m` **2.0 → 0.90–1.10** in **17 scenes** (01·02·05·06·11·14·16·18·19·20·21·C1·C4·D3·N1·N2·N5), after a pixel re-verification from a **mortar-grid overlay render**, then re-gate B-HZ + B30 | rendered course **154 mm = 2.30 ×** the Korean 67 mm (KS L 4201: 190 × 90 × 57 + 10 mm bed). **Do not ship 0.87** (C-19) | K3 → all S-WPs |
| **BS-2** | Fix B-F1 / B-F2 / B-F3, then adopt `building_kit` for the mass + LOD layer | −46.6 % prims on the 5 scenes, −59.2 % over 33, with mass / plinth / attachment / rooftop layers already correct | K3 |
| **BS-3** | Asset backdrop for the **1–2 buildings per scene that actually occupy a judged frame** — general Content root only | the only arm that moves σ_LF (5.73 → **20.20**) and sd (45.8 → **76.0**); 2.25 × render cost for one building | K3 + S1 · S8 |
| **BS-4** | Explicit `kind="backdrop"` for out-of-frame buildings | **4 of 12** are outside the ±30° frame in every judged cut; backdrop = 3–4 prims (negative prim cost) | K3 |
| **BS-5** | Keep the **granite plinth** half of the material upgrade; **drop the shell-texture swap** | both shell swaps collapsed B-HZ `edge%` 54–56 → 5–13 — at 26–32 m the features are sub-pixel, so the wall averages to a flat field. **A facade material upgrade that only swaps the diffuse family cannot work at backdrop distance** | K3 |
| **BS-6** | Dress asset buildings with the `facade_kit` attachment layer (AC condensers, signage band, downpipes, gas riser) | the asset is Western and has none of the top Korean cues — and has no ORM input (C-25) | K3 |

**Backdrop policy** (one paragraph, binding): a building earns geometry only for the band it can
occupy. For every bd compute `d_true` (nearest judged eye to the nearest point of the facade
rectangle) and `z_ceil = 0.3 + 0.1405 · d_true`. (1) If no point of the facade falls inside ±30° of
any judged eye, `kind="backdrop"`. (2) Otherwise build **nothing above `z_ceil`** and spend the
freed budget in `z ∈ [base_z, z_ceil]`. (3) One or at most two in-frame buildings per scene may be
an asset building, dressed with `facade_kit`. (4) **Any backdrop albedo change is re-gated on
B45/B30** — measured GI leak up to Δ`edge%` −1.69, Δ`w80` +1.06, **Δσ_LF −0.32** (C-20).

**Per-scene assignment**: **20** — C → asset backdrop (the measured best arm); D → `building_kit`
near tier after B-F1/B-F2 (out of frame in the three preset cuts but computed in frame for
`oblique_overview` 11.1° and `along_diagonal` 9.7°); E → `kind="backdrop"`. **21** — the biggest
procedural win in the wave: #0 65 → 8 prims and #2 86 → 7 at 41–49 m where the visible band is only
6.1–7.2 m → `building_kit` far tier; #1 mid → asset or kit-mid. **C1** — #0 asset backdrop, but C1
is a **snow scene**: any asset must be pixel-verified for roof/ledge snow and green foliage first
(`typical_building_10` has neither, verified in the R3 arm-(d) crops); #1 → backdrop. **01** — does
**not** call `sc.build_building`; it has a bespoke inline builder with a per-building `mat` key, so
integrating there is a rewrite, not a one-line swap; #0's ceiling is **1.63 m**, so only the
plinth/shopfront band is ever visible — an asset is wasted there. **C2 has zero buildings and must
not be given any** — its horizon is hedge rows and it goes to the midground package.

---

## 11. Label-collision map — read before grepping

Five ID namespaces overlap across the sources. This document uses the right-hand column.

| Source label | Where it lives | Means | **Use in this spec** |
|---|---|---|---|
| `P-1` / `P-2` | doc B §1 / §2 | jitter and species **policies** | **POL-J** / **POL-S** |
| `P-1` … `P-10` | doc C §5.3 | **linter checks** | **LINT-1 … LINT-10** |
| `R1` / `R2` / `R3` | wave W3-R | **survey agents** | "survey R1/R2/R3" |
| `R1` … `R10` | doc C §5.2 | **prop-edge rules** | **PE-1 … PE-10** |
| `R1` … `R13` | RT-I §3 | **refuted claims** | **RT-I R1 … R13** (and the merged facts are **C-1 … C-30**) |
| `F-1` … `F-6` | survey R3 §5 | **building findings** | **B-F1 … B-F6** |
| `F1` … `F5` / `FIX-1` … `FIX-6` | tonglam §3 / §1 | **eyes fix batch** | **F1 … F5** (map in C-29) |
| `S-1` … `S-4` | doc C §4 | **species rows** | unchanged (**S-1 … S-4**) |
| `S1` … `S6` | survey R3 §7.1 | **building strategy** | **BS-1 … BS-6** |
| `D-1` … `D-3` | doc C §6 | **decal rows** | **DEC-1 … DEC-3** |
| `D1` … `D6` | survey R2 §D | **retrofit vocabulary** | **RF-1 … RF-6** |
| `S1` … `S8` | — | — | **scene work packages** (this doc §4.3) |
| `WP-0` … `WP-9` | survey R2 §4 | prop work packages | superseded by §4's **T/K/S/X** packages; mapping: R2 WP-0 → S6·S7·S8 deletions · WP-1 → K4(c) · WP-2 → K1 · WP-3 → S1 · WP-4 → S2·S3·S4·S6 · WP-5 → S3·S5 · WP-6 → S6 · WP-7 → S8 · WP-8 → S8 · WP-9 → S6 |

---

## 12. Do-not-touch line

An implementer who "fixes" any of these introduces a regression.

1. **Angular hedge box form** — deliberate (Korean 전정 관행). Only the crown blobs and the missing
   breaks are in scope.
2. **scene17 stairs with no handrail** — 한강 제방 practice; `cue_railing=False` stays.
3. **scene18 has no bollards** — no carriageway, so the v5.1 deletion was correct (C-9).
4. **Equal streetlight spacing is correct** — the "no equal spacing" convention is about decorative
   placement, not photometric design. Street trees are legally 4–8 m on centre.
5. **No water tank on scene19** — the evidence runs the other way.
6. **Do not switch tactile ON**, and do not add tactile pads under bollards (P-10, P-12).
7. **No seasonal or event-specific element** in any prop. Every plant row uses a pixel-verified
   PASS asset; `veg_shrub_hedge_round_01` is FAIL (C-21) and `sct_debris_leaves_dry_*` are
   season-scoped to the leaf scenes.
8. **No atmospheric perspective** to hide far detail — measured Seoul extinction gives only 2.6–7 %
   contrast loss at 90 m.
9. **No poles on 17 / 20** (arterial and plaza; 지중화율 94.16 %). 15 and 18 only.
10. **No people, no vehicles** — including forklifts and trucks in D1.
11. **Manhole silhouette is closed** (W2 F5) and **D-5 scatter is closed** (W2 F2/F3). W3 changes
    manhole *position*, not the prop. Do not re-litigate the prop.
12. **ISO container dimensions in D1 are exactly right** — add corrugation and corner castings, do
    not adjust the box.
13. **sceneD4's worn grey-ochre tactile strip is the library's only correct worn tactile** and is
    the reference target for §6.2-D. Do not clean it up.
14. **Triangle count is not the budget — instanceability is.** +845 instances / +5.13 M logical
    triangles measured **−0.255 s** per cut against a round-to-round σ of 0.109; restoring
    instancing cut unique data 595 MB → 0.69 MB (**863×**). Do not reject a row on instance count.
15. **`build_tree`'s `yaw_deg = U(0, 360)`, its lean, and `jit_tint` are explicitly exempt** from
    the jitter abolition. A tree crown has no front; a fallen leaf has no axis; tint is out of
    scope by instruction.
16. **scene05's `seat.arcs` values are arc spans in degrees, not yaws** (C-30).
17. **The `rivermark_plaza_bldg_*` decline stands** and is guard-enforced; only the *transitive
    shared textures* are cleared (§1.10). Do not edit the procurement agent's guard to record it.

---

## 13. Reproduction

```bash
# CPU pre-flight (every WP, every commit)
python3 -m py_compile <touched files>
NEGOBS_SMOKE=1 python scenes/main/<scene>.py
python3 scripts/geom_invariance_check.py
python3 scripts/placement_lint.py --scenes all --rules Docs/briefs/placement_rules_v1.yaml

# building kit
python3 building_kit.py                       # 135/135 + 33-scene scan + the new out_max>0 check

# usd-core for T3 / T4 (pxr is NOT in the project venv)
python3 -m venv /tmp/usdvenv && /tmp/usdvenv/bin/pip install usd-core

# asset inventory (read-only — the procurement agent owns these files)
python assets/download_urban.py --list
/tmp/usdvenv/bin/python assets/verify_urban.py --sheet

# render (GPU exclusive, sequential, order-prefix mandatory)
bash scripts/rounds/run_260731_w3_pilot<N>.sh
bash scripts/rounds/run_2608xx_w3_full.sh
python3 scripts/stamp_round.py look_check/<scene>/<round> <round> <scene>

# gates
python3 scripts/regression_check.py --scenes 'look_check/scene*' ...
python3 scripts/near_ground_stats.py
python3 scripts/imgstats.py                    # ori_axis — advisory, never a gate
python3 scripts/make_review_gallery.py --round <round> --out look_check/_review_w3 \
        --status-json Docs/reports/regr_<round>.json
```

---

## 14. Supervisor amendment log

**What this section is.** The spec is authority over `Docs/audit_v4/gt_changes_w3.md` (§0 of that
file: *"This file never overrides it"*). When a user ruling reverses a spec clause, the ledger
records the supersession and the **spec owner carries the strike** — the 07-31 ledger batch
(`d71e1e3`) recorded two such strikes as owed (`w3_ledger_batch_v1.md` §6), and the Lane-1 exit
red team re-verified both were still owed at `535926e` (`redteam_lane1.md` §9-1). This is where
they land.

**Method, GT-6 precedent.** *Annotate in place, never silently rewrite.* Every superseded clause
keeps its text struck through beside the replacement and carries a `[supervisor amendment 07-31]`
marker back to the item below. **Nothing in this file has been deleted.**

| id | Clause struck | Where | Authority | Verified against |
|---|---|---|---|---|
| **MD-1** | §1.5 **Canopy Option A (none)** → Option B, build full-length enclosed soffit-lit canopy | §1.5 ruling quote + the *"Deleting the canopy makes 02-B mandatory"* bullet + the *"canopy deletion"* phrase in the one-re-cache bullet | `w3_intake_v2_images.md` §7-1 (user 2nd review, G2/U-5) | `gt_changes_w3.md` §3 GT-3 (`LANDED`) + §9-1; built figures from `w3_cb7_v1.md` §4 |
| **MD-1b** | §8 GT-3 row — *"Canopy deletion"* and *"four posts and a 2.4 × 4.9 m slab leave every cut"* | §8 | same ruling | same; prim delta **+45 canopy line / 391 → 545 scene total** `[measured]` |
| **MD-2** | §9 **P-5** — the whole parked row and its 5-frame evidence gate | §9 | `w3_intake_v2_images.md` §7-6 (GT-4 RETIRED; *"P-5's evidence gate dies with the row"*) | `gt_changes_w3.md` §3 GT-4 (`RETIRED`) + §9-2 |
| **MD-2b** | §8 GT-4 row — the change, the z-effect, the full re-cache and the `HELD`/CB-11 gate | §8 | same ruling | same |

**MD-1b / MD-2b are an extension of MD-1 / MD-2, stated rather than done silently.** The two
items the ledger declared owed name §1.5 and §9 only. §8's GT-3 and GT-4 rows carry the *same*
superseded content, and leaving them would make this document contradict itself on exactly the
clauses it was told to strike — with the spec outranking the ledger, a reader following §8 would
still delete the canopy that CB-7 has already built. Both edits are strikethrough, so the original
text is intact and the extension is revertible in one edit if the supervisor did not want it.

**What deliberately did NOT change.** §1.5's sill build, curb fix and landing-block deletion (all
three landed at `6edce66`); the one-re-cache rule for scene02; GT-3's re-cache class (`R-3` only)
and its CB-7 gate; every other §8 row; every other §9 parked row; §1.8's ruling text, which is the
*source* of P-5's gate and stays as the record of why the hold existed.
