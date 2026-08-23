# CUEOFF_RESULT_v2 — CUE-OFF, re-adjudicated under PREREG amendment A2

**2026-08-23 · post-hoc corrected re-analysis · supersedes `CUEOFF_RESULT.md` (v1, preserved with a banner)**

Instrument: `readout_cueoff.py` (A2), `gates_cueoff.py` (A2), `render_mass.py` (new),
`g2_adjudicate.py` (new). Machine tables: `READOUT_V2.md`, `GATES_CUEOFF_v2.md`,
`RENDER_MASS_SUMMARY.csv`, `RENDER_MASS.csv`, `G2_ADJUDICATION.csv`,
`VERDICT_CENSUS_v2.csv`, `PREREG_HASHES.json`.
Amendment: `PREREG_CUEOFF.md § AMENDMENT A2` (+ A2-12, A2-13).
New round: `dataset/260823_cueoff_s20fix_{A,B1,B2,P,C}` — 240 cuts, 0 failures,
90 frozen-model evaluations, retraining 0 (G6: 9 checkpoints unchanged since 04:05:27).

> ## Read this before any number below
>
> **This is a post-hoc corrected re-analysis.** A1 was written before a cut rendered.
> **A2 was written after the results were read and after two red-team waves attacked
> them.** No hypothesis, arm, threshold or primary-leg lock moved — but the person
> who fixed the counting already knew which way each fix would push. The corrections
> are itemised in A2 with the direction each one pushes, and the net direction is
> **against the study**: over the same 24 primary cells, v1 read
> 0 CUE EVIDENCE / **8 SHORTCUT** / 16 UNDECIDED, and v2 reads
> 0 CUE EVIDENCE / **2 SHORTCUT** / 6 NO-EFFECT / 4 UNDECIDED / **12 VOID**.
> **All eight of v1's SHORTCUT verdicts are gone** (six to NO-EFFECT, two to VOID).
> The single clause that could add a claim (A2-6, scene20's placebo) is the one
> carrying the loudest warning, and it adds nothing to the existing rounds.
>
> ## DEGENERATE FOOTPRINT BANNER (PREREG A1.2-3, first time actually printed)
>
> Every scene12 recall number in the `lineage` label set — that is, **every scene12
> number in the primary analysis, in both bands** — is scored against a **50-cell**
> footprint: a 5 cm × 2.45 m sliver at x = 1.6 m, the quantisation residue of one
> stair riser. The same frames labelled against a correct reference (the `twin` set,
> arm C) have a **50,278-cell** footprint — **1006× larger**. `boost` rounds never
> passed through `fuse_heightmap.py`; `main` rounds did.
>
> ## And the consequence nobody had drawn from it
>
> In the `lineage` set scene12's 48 frames are **strict-H**. In the `twin` set the
> same 48 frames are **tier V** — the drop's interior is visibly projected — so
> paired-H = 0 and every scene12 verdict is VOID there. **scene12 is a strict-H
> scene only because its ground truth is a sliver at long range.** The study's main
> target scene is not a strict-H scene.

---

## 0. Verdict census v2

Primary rule, `Δ_cue = recall_H(A) − recall_H(B)` on paired strict-H frames,
placebo-corrected, A2 counting. One cell = (label set × band × scene × model).

Includes the repair round `260823_cueoff_s20fix` (§5).

| population | CUE EVIDENCE | SHORTCUT | NO-EFFECT | UNDECIDED | VOID | n |
|---|---|---|---|---|---|---|
| **primary, all blocks** | **0** | 2 | 6 | 4 | 18 | 30 |
| primary, duplicate blocks folded out (A2-7) | **0** | 2 | 4 | 3 | 12 | 21 |
| primary, judged cells only (VOID removed) | **0** | 2 | 6 | 4 | — | 12 |
| twin-conditional (R2 P3 primary metric) | **0** | 5 | 7 | 0 | 18 | 30 |
| secondary B1 leg — **promotion forbidden**, PREREG §3.1 | 4 | 1 | 0 | 1 | 18 | 24 |

**Only 12 of the 30 primary cells are judgeable at all.** The 18 VOIDs are six
scene-round-labelset groups of three models each: scene20 original (paired-H 6,
§4.5-3) ×2 sets, scene20 repair (`polar_gt` differs on 6/27 judged frames, §4.5-2)
×2 sets, and scene12 `twin` in both bands (paired-H 0, arm A is tier V there) ×2.
A study that can judge 40 % of its own cells is a study whose next version needs a
different scene set, not a different readout.

**The pre-registered primary rule has produced zero CUE EVIDENCE, in v1 and in v2.**
The four CUE EVIDENCE cells are all in the secondary B1 leg, all in scene12, all at
placebo/cue mass ratios of 0.089 and 0.065 — i.e. the placebo removes one eleventh
to one fifteenth of what the manipulation removes. The pre-registration forbade
promoting them before the numbers existed, and they are not promoted here.

### What moved from v1 to v2 — every changed cell traced

v1 primary verdicts: 8 SHORTCUT (lineage: s12·e rgb, s17 depth, s17 b2, s20 depth,
s12·e2 rgb; twin: s17 depth, s17 b2, s20 depth) and 16 UNDECIDED.

| v1 cell | v1 said | v2 says | why |
|---|---|---|---|
| s12·e rgb · s17 depth · s17 b2 · s12·e2 rgb (lineage) + s17 depth · s17 b2 (twin) | **SHORTCUT** ×6 | **NO-EFFECT** | Δ_cue was exactly `(0,0,0)`; A2-1 takes zero out of the same-sign branch and prints the power bound (p95 = 0.117 at n = 24, which does not resolve the 0.10 threshold) |
| s20 depth (lineage) + s20 depth (twin) | **SHORTCUT** ×2 | **VOID** | paired-H 6 < 10, PREREG §4.5-3, now enforced inside `verdict()` (A2-2 / R5 D-1) |
| s20 rgb, s20 b2 (both sets) | UNDECIDED ×4 | **VOID** | same gate |
| s12 twin, both bands, all models | UNDECIDED ×6 | **VOID** | paired-H 0 — arm A's frames are tier V in the corrected footprint (§3, G4) |
| **s12·e b2** (lineage) | UNDECIDED | **SHORTCUT** | Δ_cue `(0.000, +0.083, 0.000)`. v1's `same_sign` returned **False** here because not every value was positive — the same broken predicate that returned **True** for `(0,0,0)`. A2-1 corrects **both** directions, and this is the one cell where the correction adds a verdict rather than removing one |
| **s12·e2 depth** (lineage) | UNDECIDED | **SHORTCUT** | Δ_cue `(0.000, 0.000, +0.125)`, same correction |
| `tier migration \| none` | every row | **G4-verified** | G4 had never run (§3); it now confirms 0 `H→E` everywhere and finds migrations §4.2 never asked for |

A2-1 is worth being precise about because it is the clause most open to the charge of
being chosen for its effect: v1's `same_sign` was **wrong in both directions at
once** — permissive for `(0,0,0)` and strict for `(0,+x,0)` — and the corrected
definition removes six verdicts and adds two. It was not tuned.

---

## 1. Real-render pixel mass — the AABB grades are retracted

Threshold ≥32/255 (F7 canon) and ≥8/255, measured per frame on the rendered PNGs,
averaged over the **judged** frames (strict-H in both arms). Full per-frame data in
`RENDER_MASS.csv`.

**G0 noise floor — arm A vs the canonical lineage `on` round, same geometry,
different render call:** scene12 `boost_e` **8 px**, scene17 **272 px**,
scene20 **1 px**, scene12 `boost_e2` **0 px** (≥32/255). Every mass below is
10³–10⁵× the floor. The isolation and freeze are clean, and this is the part of the
apparatus that should be shipped.

| scene · band | A vs B1 | A vs B2 | A vs P | A vs C |
|---|---|---|---|---|
| scene12 · `boost_e` | 721,912 (**34.81 %**) | 110,667 (5.34 %) | 64,012 (3.09 %) | 137,588 (6.64 %) |
| scene12 · `boost_e2` | 794,278 (**38.30 %**) | 127,832 (6.17 %) | 51,242 (2.47 %) | 89,559 (4.32 %) |
| scene17 · `boost_h` | 616,554 (**29.73 %**) | — (no guard) | 342,269 (16.51 %) | 281,017 (13.55 %) |
| scene20 · `boost_e2` | 671,123 (**32.37 %**) | 173,690 (8.38 %) | 157,834 (7.61 %) | 232,132 (11.19 %) |

At ≥8/255 the same ordering holds: s12·e 57.76 / 9.12 / 4.64 / 12.16 %,
s12·e2 68.60 / 9.62 / 3.83 / 6.26 %, s17 36.00 / — / 21.70 / 17.58 %,
s20 54.72 / 12.61 / 8.81 / 14.29 %.

### 1.1 Admissibility re-graded (A2-5)

Conservative means the placebo removes **at least as much light** as the
manipulation it controls for. Ladder: ≥1.25 CONSERVATIVE · ≥0.80 MATCHED ·
≥0.25 ANTI-CONSERVATIVE · <0.25 SEVERELY ANTI-CONSERVATIVE.

| leg | PREREG §3 grade | measured ratio P/cue (≥32) | (≥8) | **A2 grade** |
|---|---|---|---|---|
| s12·e P vs B2 (**primary**) | "12–30× larger → conservative" | **0.578** | 0.509 | ANTI-CONSERVATIVE |
| s12·e2 P vs B2 (**primary**) | inherited e's constants | **0.401** | 0.398 | ANTI-CONSERVATIVE |
| s17 P vs B1 (**primary**) | "~18× larger → strongly conservative" | **0.555** | 0.603 | ANTI-CONSERVATIVE |
| s20 P vs B2 (**primary**) | "no admissible placebo" | **0.909** | 0.699 | **MATCHED** |
| s12·e P vs B1 (secondary) | "~3.2× smaller → anti-conservative" | **0.089** | 0.080 | SEVERELY ANTI-CONSERVATIVE |
| s12·e2 P vs B1 (secondary) | inherited e's constants | **0.065** | 0.056 | SEVERELY ANTI-CONSERVATIVE |
| s20 P vs B1 (secondary) | "no admissible placebo" | **0.235** | 0.161 | SEVERELY ANTI-CONSERVATIVE |

**No leg in this study is conservative.** The two grades that motivated the
pre-registration's structural choices are both inverted: s17 was promoted to the
primary placebo-corrected leg on an "18× conservative" claim and is actually 0.56×;
s12's B2 leg was made primary on a "12–30× conservative" claim and is actually 0.58×.
The AABB estimator could not see shadows, ambient occlusion, GI bounce or shading —
exactly the failure `F7_HPAIR_PIXDIFF.md` had already documented in this corpus.

### 1.2 The scene20 "0 px" — what it really was

D49 ④ and R4 F1 both call this a projection bug. **It is not a projection bug.** We
checked corner by corner, on both judged eyes (x = −5.104 and x = −6.716, yaw −3.76°
and +7.05°, looking down +X):

| scene20 group | world x | in front of camera | in frame | px |
|---|---|---|---|---|
| planters | −12.3, −12.3, −7.0 | 0/24 corners | — | **0** |
| benches | −12.9, −9.65, −5.4 | 4/24 corners | outside the 62° FOV | **0** |
| streetlights | −12.6, −7.0, −9.5 | 0/24 corners | — | **0** |
| bollards | −13.6 | 0/8 corners | — | **0** |
| hedges | −14.0 … −9.0 | 0/16 corners | — | **0** |
| **backdrop E1·E2** | 44 … 54 | 16/16 | yes | **240,329 (11.59 %)** |

Every piece of mesa furniture sits behind or beside the camera. §3.3's measurement is
correct. **The error is in the inference drawn from it**: the rendered arm P does not
remove furniture — `scene20_diagonal_oblique.py:1046` removes backdrop blocks E1 and
E2 under `placebo_remove`, and §3.3's own table put those at 240 k px. §3.3 measured
a set the arm does not touch, found it empty, and declared the arm impossible while
the code was removing 11.6 % of the frame. Measured on the renders, arm P moves
**157,834 px ≥32/255 = 7.61 %** on the six judged frames — **0.909×** arm B2, the
best-matched cue/placebo pair in the study.

**Two genuine defects in `pixel_mass.py` found while checking** (neither changes the
headline, both recorded so the tool is not reused as-is):

1. `crest_visible()` hard-codes the drop lip at the plane `x = 0` with the walked
   crest at `z = 0` for `x ≤ 0`. scene20's edge is a **30° oblique**, so the lip
   position is a function of y and the occlusion mask is geometrically wrong for
   this scene. It over-occludes: `PLA_belt_E` drops from 756,710 px to 14,485 px
   (52×) under a mask that does not describe scene20's geometry.
2. `aabb_px()` returns exactly `0.0` when fewer than 3 AABB corners survive
   `z_cam > 0.05`. A box straddling the camera plane silently scores zero instead of
   being near-clipped. Benign here (the boxes are fully behind) but a latent
   under-estimator.

The correct disposition is the one A2-5 takes: **stop using AABB projection for
admissibility at all.** The renders exist; measure them.

---

## 2. The eight G2 breaches, adjudicated individually

`GATES_CUEOFF.md` logged **FAIL 8**, every one `heightmap.npy differs — REGULATION
BREACH`. D44 examined **one** (s12 P-vs-A) and let seven inherit the verdict; R4 F4
was right to call that over-generalisation, and right that scene20's labels
contradict it. Here is every case, at the three scopes A2-8 defines. Full data:
`G2_ADJUDICATION.csv`.

| # | case | cells differing | max \|Δz\| | world extent | in drop footprint | polar_gt differs, all frames | **polar_gt differs, JUDGED frames** | verdict |
|---|---|---|---|---|---|---|---|---|
| 1 | s12·e **B1** vs A | 14,467 | 0.005 m | x −2…14, y −8…1.2 | **0** | 0/24 | **0/24** | FALSE POSITIVE |
| 2 | s12·e **B2** vs A | 54 | 0.005 m | x −2…0.05, **y 1.10…1.20** | **0** | 0/24 | **0/24** | FALSE POSITIVE |
| 3 | s12·e **P** vs A | 42 | 0.003 m | x −2…−1.9, y −3.65…−2.55 | **0** | 0/24 | **0/24** | FALSE POSITIVE (= D44's case, confirmed) |
| 4 | s12·e2 **B1** vs A | 14,467 | 0.005 m | as #1 | **0** | 0/24 | **0/24** | FALSE POSITIVE |
| 5 | s12·e2 **B2** vs A | 54 | 0.005 m | as #2 | **0** | 0/24 | **0/24** | FALSE POSITIVE |
| 6 | s12·e2 **P** vs A | 42 | 0.003 m | as #3 | **0** | 0/24 | **0/24** | FALSE POSITIVE |
| 7 | s20 **B1** vs A | 16,012 | **3.160 m** | x −2…12.15, y −8…8 | **1,624** | **3/24** | **0/6** | **REAL breach, scene scope; immaterial at judged scope** |
| 8 | s20 **B2** vs A | 12,656 | **3.160 m** | x −2…5.55, y −2.95…4.8 | **14** | **3/24** | **0/6** | **REAL breach, scene scope; immaterial at judged scope** |

Three further pairs pass outright and were never among the failures:
**s17 B1 vs A, s17 P vs A, s20 P vs A → heightmap sha256 identical, 0 cells differ,
`polar_gt` identical on all 24 frames in both label sets.**

### 2.1 Cases 1–6 (scene12) — prop cells, D44 generalises correctly *here*

All six differ by ≤ 5 mm, none touches a footprint cell, none changes a single
frame's `polar_gt`, and both arms' footprints are the same 50 cells. Case 2's 54
cells sit at **y ∈ [1.10, 1.20]** — precisely the railing line (posts at y 1.09–1.21),
i.e. the AABB shadow of the removed guard on the height grid. Case 3's 42 cells sit
at y ∈ [−3.65, −2.55], the streetlight/bench strip. Case 1's 14,467 cells are the
5 mm proud dressing skins (bike-road white lines, material-break bands). **These are
prop cells. D44's conclusion was right for scene12; D44's mistake was asserting it
for scene20 too without looking.**

### 2.2 Cases 7–8 (scene20) — a real breach, and exactly what it does

This is R4's "+8 % GT cells / different scoresheets" finding, localised.

- Removing the **cheek wall** (`cue_railing=False`, arm B2) deletes a solid structure
  standing on the hazard side. In the lineage off round that structure is also absent
  (hazard off ⇒ no stairs, no cheek walls), so the labeller's twin difference
  `z_off − z_arm ≥ 0.30` starts scoring the re-exposed ground as drop footprint.
- **Footprint `cells_raw` grows 60,659 → 61,961 (+1,302 cells, +2.15 %)** in arms B1
  and B2 in *both* label sets. Arm P is unaffected (60,659, byte-identical heightmap).
- Per-frame GT positives go **3.00 → 3.25 cells/frame** over the 24 on-frames
  (R4 measured 1.50 → 1.62 over all 48 on+off frames; same +8.3 %).
- **The entire difference is three frames**: cut `0005` in L0, L5 and L7. In arm A
  that cut is `none_in_fov` (GT all zero); in B1/B2 it becomes tier **H** with 2
  positive cells in band 3b. A frame that is `none_in_fov` in arm A **cannot enter
  the paired-H population**, which requires strict-H in both arms.
- **On all six judged frames `polar_gt` is byte-identical between A and B1, and
  between A and B2, in both label sets.** Verified directly, not inferred.

**Adjudication.** PREREG §4.5-2's criterion is `polar_gt` byte identity, and §4.2
judges on paired-H frames and nothing else. On the judged population that criterion
is met, so the paired comparison is a paired comparison and no re-scoring is
required. **No GT substitution is applied** — neither arm-A's GT nor the intersection
GT — because there is nothing to substitute: the two scoresheets are already
identical wherever the comparison is evaluated. Had they differed, A2-8 would have
required arm A's GT as the reference (arm A is the invariance target in G2's own
definition, and `recall_H_twin` already reads the twin arm's probabilities on the
evaluated arm's GT cells), with the intersection GT as a declared sensitivity check.

**What does NOT survive**: any *scene-level* statement about scene20's H census or
footprint being arm-invariant. B1 and B2 have a 1,302-cell larger footprint and three
extra H frames. R4's V1 is upheld as a finding and downgraded as a voiding condition.

**Also recorded**: scene20 is already VOID under §4.5-3 at paired-H = 6, so cases 7–8
change no verdict either way.

---

## 3. Gates G4, G5, G7 — the first time they have ever run

`GATES_CUEOFF.md` v1 said `G4: labels ... absent -- skipped` ×10,
`G5: ... absent -- skipped` ×2, `G7: no label file yet`. R4 F5 read the 27-minute gap
between the gate run (05:24) and the label files (05:51) as the cause.

**The cause is a path bug.** `gates_cueoff.py::load_labels` looked for
`labels/<stem>_<arm>.json`; the labeller writes
`labels/<set>__<stem>_<arm>__<scene>.json`. Re-running the battery a hundred times
would have produced the same "skipped". Fixed in A2; `GATES_CUEOFF_v2.md` is the
first execution.

### G4 — tier re-derivation per arm, every migration reported (A2-9)

- **`H→E` migrations: zero, everywhere.** §4.2's mandatory report is a report of
  nothing, and now it is a *verified* report of nothing. Every `tier migration | none`
  in v1 was an unverified default that happens to have been right.
- **`none_in_fov → H`, scene20 A→B1 and A→B2: 3 frames each** (§2.2 above).
- **`V → H`, `twin` / scene12 / `boost_e2`, A→B1: 18 of 24 frames.** In the corrected
  footprint, removing every cue changes the frame's *tier*, not just its score —
  stripping the guard, the material break and the dressing turns a frame whose drop
  interior was visibly projected into a strict-H frame. §4.2 never asked for this
  direction and it is arguably more damaging than an `H→E` migration would be.
  (scene12's `twin` paired-H is 0 for a simpler reason in both bands: arm A itself is
  tier **V** there. In `boost_e2` arm B1 additionally migrates the other way, so the
  two arms end up on opposite sides of the tier boundary.)
- Arm C migrates `H → none_in_fov` on every frame in every scene, which is the
  definition of arm C and confirms the surgery removed the hazard.
- Paired-H per pair, `lineage`: s12·e 24 · s12·e2 24 · s17 (B1) 24 · **s20 6**.
  `twin`: s17 24 · **s20 6** · **s12 0 (both bands)**.

### G5 — arm C's ground truth is all-zero

**Passes on the `lineage` set for all four scene-rounds, 24/24 frames each.** This is
the only machine check on the hand-patched `_solid_at` sidecar oracle (PREREG §6.1),
and it clears it: the hazard-off surgery left no drop and the oracle did not
re-impose the ON profile. On the `twin` set the same 0 is **constitutive** — arm C is
its own reference surface there — and is now labelled VACUOUS instead of counted as a
second pass.

### G7 — footprint sanity, with the boost-lineage accounting

38 scene-arm footprints tabled. Degeneracy is now split in two, because v1 lumped
them and made the banner unreadable:

- **DEGENERATE (real): 8** — every scene12 `lineage` label file, both bands, all four
  hazard-bearing arms: `cells_raw = 50`, `max_diff = 0.3394 m`.
- **BY-DESIGN: 6** — arm C files with `cells_raw = 0`. Arm C has no hazard; an empty
  footprint there is the arm's definition, not a defect.

**Boost-lineage degeneracy accounting.** The same frames, labelled from the two
references: `lineage` (boost round, never fused) **50 cells** vs `twin` (arm C of this
round, fused) **50,278 cells** — **1006×**, on all 8 scene12 arm-rounds. scene17
(65,833) and scene20 (60,659) have no sidecar oracle and are identical in both sets,
so the degeneracy is scene12's alone and its mechanism is confirmed: `boost` rounds
never ran `fuse_heightmap.py`, and scene12's hazard-blind `_solid_at` oracle then
cancels the twin difference.

---

## 4. Scene-by-scene re-adjudication

### 4.1 scene12 (train) · bands `boost_e` and `boost_e2` · primary Δ(A,B2)

| band · model | Δ_cue (A,B2) | Δ_placebo (A,P) | sign class | **v2 verdict** | v1 said |
|---|---|---|---|---|---|
| e · rgb | 0.000, 0.000, 0.000 | 0.000, 0.000, 0.000 | NO-EFFECT | **NO-EFFECT** (p95 0.117) | SHORTCUT |
| e · depth | +0.125, +0.250, −0.125 | 0.000 ×3 | MIXED | **UNDECIDED** | UNDECIDED |
| e · b2 | 0.000, +0.083, 0.000 | **+0.333, +0.208, +0.125** | SAME-SIGN 1/3nz | **SHORTCUT** (corrected −0.194) | UNDECIDED |
| e2 · rgb | 0.000 ×3 | +0.125, 0.000, 0.000 | NO-EFFECT | **NO-EFFECT** (p95 0.117) | SHORTCUT |
| e2 · depth | 0.000, 0.000, +0.125 | +0.125, 0.000, 0.000 | SAME-SIGN 1/3nz | **SHORTCUT** | UNDECIDED |
| e2 · b2 | +0.125 ×3 | **+0.167, +0.125, +0.167** | SAME-SIGN 3/3nz | **UNDECIDED** (corrected −0.028) | UNDECIDED |

**Three things to say about scene12 and none of them is the headline v1 reported.**

1. **The GT is a sliver, and worse, the strict-H label depends on it.** 50 cells in
   the primary label set, 50,278 in the corrected one — and in the corrected one the
   frames are tier **V**, not H. scene12 is the study's "highest visible cue" scene
   (8.75) and its lowest-GT scene simultaneously; the two facts are the same fact.
2. **In both cells where the placebo moves at all, it moves MORE than the cue.**
   This is the most informative thing in scene12 and v1 never surfaced it, because
   v1's placebo column was read as a correction term rather than as a result.

   | band · model | placebo mass removed | Δ_placebo (3/3 seeds) | guard mass removed | Δ_cue(A,B2) | corrected |
   |---|---|---|---|---|---|
   | `boost_e` · b2 | 3.09 % | **+0.333, +0.208, +0.125 → +0.222** | 5.34 % | +0.028 | **−0.194** |
   | `boost_e2` · b2 | 2.47 % | **+0.167, +0.125, +0.167 → +0.153** | 6.17 % | +0.125 | **−0.028** |

   Removing benches, streetlights and far hedges — objects the cue matrix gives **no
   credit at all**, on the wrong side of the walkway, at *half to two-fifths* the
   optical mass of the guard — costs b2 recall **eight times** what removing the
   guard costs it in band `boost_e`. This points away from cue-reading, not toward
   it, and it is the strongest single argument against reading the B1 collapse as a
   cue effect.
3. **The B1 collapse is real, large, and uninterpretable as cue evidence.** rgb
   +0.375 in both bands (band e seeds +0.208/+0.042/**+0.875**), b2 **+0.972** in
   band e and **+0.625** in band e2 — at placebo/cue mass ratios of **0.089** and
   **0.065**. There is no experiment in this study that
   removes ~700 k px of non-cue material, so "cues" and "a third of the picture" are
   perfectly confounded. PREREG §3.1 forbade promotion. Not promoted.

**A1.2-1 disposition** (R4 F11 asked for it). A1.2-1 says that when the two label
sets disagree, the cell is "not judgeable". v1 had scene12 rgb as `lineage` SHORTCUT
vs `twin` UNDECIDED and applied nothing. Under A2 there is no disagreement to
adjudicate, and the reason is worse than a disagreement: **the `twin` set cannot
judge scene12 at all** — paired-H = 0 in both bands, because in the corrected
footprint arm A's frames are tier V. So every scene12 verdict in this document rests
on the label set whose footprint G7 marks DEGENERATE, with no second opinion
available. That is stated, not resolved.

**H2 (arm C fires on cue vocabulary alone): ACCEPTED for scene12, both bands** —
FA(C) rgb 1.000 / b2 1.000 (band e), rgb 1.000 / b2 0.958 (band e2), against the
0.40 pre-registered bar. **With the floor now printed, the contrast is stronger than
v1 could show**: FA(off) rgb **.028** → FA(C) **1.000**; b2 **.000** → **1.000**.
The model does not fire indiscriminately in this scene — it fires on arm C
specifically.

**And the confound that eats most of it (quantified).** scene12's arm C is the only
arm in the study with a bespoke fill (`build_cueoff_fill`, PREREG §6.1). Measured:
**arm C differs from arm A by only 6.64 % of frame** (band e; 4.32 % in band e2)
while differing from the lineage off round by **36.60 %** (58.35 % in band e2). Arm C
is optically almost arm A. A model that scores recall 1.000 on arm A scoring FA 1.000
on a picture 6.6 % away from arm A is close to a tautology. On top of that, arm C
lifts the lower-level dressing by **1.36 m** (`lz = 0.0 if KEEP_DRESSING else
lo["z_top"]`, `lo["z_top"] = −1.36`): the bike-path white lines land 5 mm above the
camera-height ground plane and the reed bands split across two heights — a layout
present in no arm and no training frame. "The same cue vocabulary was preserved" is
not true of this arm.

### 4.2 scene17 (train) · band `boost_h` · primary Δ(A,B1) — A1.2-2's promoted leg

| model | Δ_cue (A,B1) | Δ_placebo (A,P) | sign class | **v2 verdict** |
|---|---|---|---|---|
| rgb | +0.250, +0.083, 0.000 | 0.000 ×3 | SAME-SIGN 2/3nz | **UNDECIDED** (Δ 0.111, corrected 0.111 < 0.15) |
| depth | 0.000 ×3 | 0.000 ×3 | NO-EFFECT | **NO-EFFECT** (p95 0.117) |
| b2 | 0.000 ×3 | 0.000 ×3 | NO-EFFECT | **NO-EFFECT** (p95 0.117) |

A1.2-2 promoted scene17 to the primary placebo-corrected leg on the strength of an
"18× conservative" placebo. **The placebo is 0.555×.** The promotion's stated reason
does not exist. The other stated reasons do (65,833-cell footprint, no sidecar
oracle, paired-H 24), so the leg stays primary — but the sentence that justified it
is retracted.

**H2 REJECTED for scene17**, decisively, and this is where the "cue vocabulary"
reading dies: arm C **preserves the full cue vocabulary** here (lamp poles, km sign,
`far_side_visible_depth`) and yet FA(C) = rgb **.042** / depth .042 / b2 .056 against
a floor of .014 / .042 / .014. **Delta ≈ +0.03.** Nothing happens. Compare arm C's
optical distance from the off round: **1.02 %** — scene17's arm C is optically almost
the *off* round, because it uses the canonical `build_flat_fill`, the same fill the
off round uses (PREREG §6.2).

### 4.3 scene20 (val) · band `boost_e2` · primary Δ(A,B2) — VOID, and why it matters

| model | Δ_cue (A,B2) | Δ_placebo (A,P) | corrected | sign class | **v2 verdict** |
|---|---|---|---|---|---|
| rgb | +0.667, 0.000, 0.000 | 0.000, 0.000, +0.167 | +0.167 | SAME-SIGN 1/3nz | **VOID** (paired-H 6) |
| depth | 0.000 ×3 | 0.000 ×3 | 0.000 | NO-EFFECT | **VOID** (paired-H 6) |
| **b2** | **+1.000, +0.667, +0.667** | 0.000, 0.000, +0.333 | **+0.667** | SAME-SIGN 3/3nz | **VOID** (paired-H 6) |

This is the study's only leg where the primary rule's cue-evidence branch would fire
on a **MATCHED** placebo (0.909×, the best in the study), with **3/3 seeds non-zero
and same-signed**, at a corrected difference of **+0.667 — 4.4× the 0.15 threshold**.
And it is VOID, because PREREG §4.5-3 disqualifies a scene at paired-H = 6 < 10, and
A2-2 now enforces that on the verdict and not only on the table row. v1 printed
twelve verdicts here, four of them positive.

**H2 REJECTED for scene20**: FA(C) rgb .361 / depth .000 / b2 .181 against a floor of
.250 / .000 / .125. And the rgb floor is itself a seed artifact — s43 fires on 16/24
*off-round* frames while s42 fires on 0.

The repair round §5 exists to answer this leg under the rules, not around them.

### 4.4 The arm-C dose–response that kills the "cue vocabulary" reading

Four points, four scene-rounds, one variable: **how far arm C's surgery moved the
picture from the hazard-off round**.

| scene · band | arm C vs off round (≥32/255) | FA(C) rgb | FA(C) b2 | cue vocabulary preserved? |
|---|---|---|---|---|
| scene12 · `boost_e2` | **58.35 %** | 1.000 | 0.958 | yes |
| scene12 · `boost_e` | **36.60 %** | 1.000 | 1.000 | yes |
| scene20 · `boost_e2` | **13.09 %** | 0.361 | 0.181 | yes |
| scene17 · `boost_h` | **1.02 %** | 0.042 | 0.056 | **yes — full vocabulary** |

Monotone in optical distance, flat in vocabulary. **Arm C's false-alarm rate measures
how different its picture is from the hazard-off round, not how many cue nouns are in
it.** D46's "the model fires on cue vocabulary" is withdrawn; D49 ① already withdrew
it and this is the mass-resolved version of the same retraction.

---

## 5. The scene20 repair round `260823_cueoff_s20fix`

Declared in A2-10 **before any cut of it existed** (0 PNGs on disk at 07:41:57;
render queued behind the GPU lock at 07:40:30). Camera band
`{"d_min":4,"d_max":8,"h_min":0.25,"h_max":0.6}`, `--cams 16`; scene, arms, toggles,
seed 20260821, frozen checkpoints and τ_op unchanged. G0 does not apply (arm A is no
longer a bit-for-bit re-render of the corpus); G1–G7 do.

### 5.1 The repair worked — and then hit a second wall

**Render:** 5 arms × 48 cuts = **240 cuts, 0 failures**, 3376 s wall (mostly waiting
for the GPU lock behind another queue), 1.6–3.7 s/cut.

**The camera repair did exactly what A2-10 said it would.** Strict-H yield rose from
**6/24 (25 %)** in the original band to **27/48 (56 %)**, and **paired-H = 27** for
all three pairs — §4.5-3's n ≥ 10 cleared with room to spare. At n = 27 the zero-flip
95 % bound drops from 0.393 to **0.105**, which is finally within a rounding error of
this study's own 0.10 threshold (n ≥ 29 would clear it outright).

**And the placebo came out CONSERVATIVE — the only one in the study.**

| pair | rendered mass on the 27 judged frames, ≥32/255 | ≥8/255 |
|---|---|---|
| A vs B1 | 733,419 px (**35.37 %**) | 994,321 px (47.95 %) |
| A vs B2 | 155,775 px (**7.51 %**) | 190,748 px (9.20 %) |
| A vs **P** | **173,379 px (8.36 %)** | 207,531 px (10.01 %) |
| A vs C | 245,532 px (11.84 %) | 300,261 px (14.48 %) |

**P / B2 = 1.113 at ≥32/255 and 1.088 at ≥8/255.** Under the A2-5 ladder that grades
as **MATCHED** (CONSERVATIVE needs ≥ 1.25) — but for the first and only time in this
study the ratio is **above 1**: the placebo removes *more* light than the guard
removal it controls for, so the mismatch finally points the safe way. (P / B1 = 0.236
— the B1 leg stays severely anti-conservative, as it is in every scene.)

**Gates.** G3 pose identity: B2, P, C **48/48 exact**; B1 42/48 exact + **6 in the
declared `pose_tol` stratum** (worst |Δeye_z| = 0.0085 m — the scene20 mesa band datum
shift PREREG §5.1 declared in advance), 12.5 % < §4.5-1's 25 % ceiling. G4: paired-H
27/27/27, **no `H→E` migration**; B1 shows `V→H_weak` on 6 frames. G5: arm C
**48/48 all-zero GT** in the `lineage` set — a real pass, not the constitutive one.
G7: `cells_raw` 60,659 (A, P) vs 61,961 (B1, B2), no degeneracy. G0 does not apply,
as declared.

**Then G2 failed on the judged population.** On **6 of the 27 judged frames**, arms B1
and B2 carry one extra positive far-band cell — `C3b` on cut 0005 and `D3b` on cut
0014, in all three light conditions, 3 → 4 positive cells. Arm P is byte-identical on
all 48. This is §4.5-2's exact criterion failing at the only scope A2-8 says can void
a pair.

### 5.2 The ruling, fixed before any model was run

`A2-13` was written at 08:30 with the labels in hand and **zero `per_frame.csv` files
on disk** for this round (checked and recorded: `find eval -path '*s20fix*' -name
per_frame.csv` → 0 at 08:29:15). So the rule below was fixed knowing the ground truth
and the tier census exactly, and knowing no recall number at all.

1. **PRIMARY: `Δ(A,B2)` and `Δ(A,B1)` are VOID under §4.5-2.** The scene is not judged
   on its primary leg — in the repair round as in the original, and for the same
   physical reason.
2. **SECONDARY / EXPLORATORY:** both arms re-scored on **arm A's GT**, so they share
   one scoresheet. Reported, never promoted.
3. **SENSITIVITY:** the same on the **intersection GT**.
4. `Δ(A,P)` is unaffected and computed normally.
5. A2-10's one-repair allowance is spent. No third camera band.

### 5.3 The numbers

**paired-H = 27 · placebo/cue mass ratio 1.113 · GT differs on 6 of the 27 judged
frames.**

| model | Δ_cue (A,B2) | Δ_placebo (A,P) | PRIMARY verdict | SECONDARY (A-GT re-scored) | SENSITIVITY (∩ GT) |
|---|---|---|---|---|---|
| rgb | +0.444, +0.000, +0.074 (mean **+0.173**) | +0.000, +0.000, +0.185 (+0.062) | **VOID** §4.5-2 | corrected **+0.111** → would be UNDECIDED | +0.111 → UNDECIDED |
| depth | 0.000 ×3 (**+0.000**) | 0.000 ×3 | **VOID** §4.5-2 | **+0.000** → would be NO-EFFECT (p95 = 0.105 at n = 27) | +0.000 → NO-EFFECT |
| **b2** | **+0.556, +0.481, +0.741** (mean **+0.593**) | +0.037, −0.037, +0.259 (+0.086) | **VOID** §4.5-2 | corrected **+0.506** → would be CUE EVIDENCE | **+0.506** → CUE EVIDENCE |

Secondary B1 leg (promotion forbidden anyway, ratio 0.236): rgb +0.778, depth +0.000,
b2 **+0.926** — also VOID under §4.5-2.
H3 guard share of the full cue effect: rgb 22 %, b2 **64 %**, depth undefined
(near-zero denominator).

**Three things to say about this, in order of how much we would like them to be true.**

1. **The primary answer is VOID.** Not "CUE EVIDENCE with caveats", not "CUE EVIDENCE
   pending". The pre-registration says a scene whose `polar_gt` is not byte-identical
   across the arms is not judged, that rule was re-fixed in A2-8 before this round
   existed, its application here was ruled in A2-13 before any model had been run on
   this round, and it is applied. **The study's primary-rule CUE EVIDENCE count is
   still zero.**
2. **The re-scored reading is strong, and the GT breach turns out not to have moved
   it at all.** Re-scoring both arms on arm A's sheet gives Δ_cue = +0.556, +0.481,
   +0.741 — **byte-identical to the own-GT numbers**, because the one extra far-band
   cell never changed a frame's hit/miss. The intersection-GT sensitivity gives the
   same. So the corrected difference of **+0.506** (3.4× the 0.15 threshold, 3/3 seeds
   non-zero and same-signed, against a placebo that removes *more* mass than the cue)
   is not an artifact of the scoresheet mismatch. **It is still not a verdict**, and
   the reason it is not is procedural rather than numerical — which is exactly the
   circumstance in which a study is most tempted to relabel its rules, and exactly why
   the rule was fixed in writing two hours earlier.
3. **R4's F14 prediction is confirmed in direction and magnitude.** R4 predicted
   Δ_cue − Δ_placebo = **+0.667** with 3/3 same sign for this leg from the 6-frame
   round; the 27-frame repair round gives **+0.506**, 3/3 same sign. The effect
   survived a 4.5× increase in sample and a change of camera band. It is real. What it
   is *evidence of* remains unsettled, because scene20's guard is structural (§5.4)
   and because the b2 model is the one encoder where B1 removal drives recall to
   exactly 0.000 on all three seeds.

**H2 for this round: ACCEPTED on paper, and the instrument now says why not to believe
it.** FA(C) rgb 0.403 clears the 0.40 bar — but the hazard-off FLOOR is already
**0.319**, so arm C's excess is **+0.083**. Seed 43 alone fires on **0.958** of the
*hazard-off, dressing-off* frames. The 0.40 bar was written for absolute FA and is
not fit for purpose; A2-3's floor column is what should be read, and the floor-corrected
excesses are rgb +0.083, depth +0.000, b2 +0.104. On the floor-corrected reading, H2
is rejected here as it is in the original scene20 round.

### 5.4 What the repair round actually taught us

The b2 leg was supposed to be the study's first primary-rule CUE EVIDENCE. Instead the
repair round produced something more useful and less welcome: **a demonstration that
scene20 cannot answer the guard question at all, under this GT definition, in any
camera band.**

`cue_railing` in scene20 removes a **cheek wall** — a solid structure standing on the
hazard. Remove it and the labeller's twin difference `z_off − z_arm ≥ 0.30` starts
counting the re-exposed ground as drop: `cells_raw` 60,659 → 61,961 (+1,302), and one
far-band polar cell lights up on 6 of 27 judged frames. **The guard is not a separable
appearance cue in this scene; it is load-bearing for the hazard's own definition.**
The pre-registration assumed `cue_railing` was appearance-only. For scene20 that
assumption is false, it was false in the original round, and no number of cameras
fixes it — the original round hid this behind a different failure (paired-H 6), and
the repair round exposed it by removing that cover.

That is a finding about the apparatus, and it is the kind worth publishing: it says
which question this design cannot ask. A guard toggle is a clean appearance
manipulation only where the guard is *ornamental* (scene12's railing: 54 heightmap
cells, all ≤ 5 mm, zero footprint cells). Where the guard is *structural*, the
intervention changes the hazard it is supposed to hold fixed. Any future use of this
instrument should classify each `cue_railing` target as ornamental or structural
**before** the arm is registered, and the classification is mechanical: run the
labeller on both arms and compare `cells_raw`.

---

## 6. Honest framing — what survives, what fell, what is new

### 6.1 What survives

- **The apparatus.** Pre-registration written before the first cut and machine-checked
  (`G_PREREG`: **696 rendered frames, all postdating the registration that covers
  them** — 456 vs the original 03:55:45, 240 vs A2's 07:42; G6: 9 checkpoints
  unchanged since 04:05:27; **but see A2-12: appending A2 moved
  the file's mtime past the original renders and permanently weakened this gate's
  strongest form. The mtime was not rewritten to restore it.**), isolated scene
  copies, frozen checkpoints re-hashed (G6), a G0 noise
  floor of 8 / 272 / 1 / 0 px against manipulations of 10³–10⁵× that, and a
  pre-registered non-promotion rule that was actually obeyed when the tempting result
  arrived. **Two red-team waves attacked the procedural record and could not land a
  hit there** — R5's 15 spot re-computations and its wide sweep matched to four
  decimals; R4's explicit "violations NOT found" list confirms no arm swap after the
  fact, no placebo re-selection, no checkpoint edit, and a pre-registration that
  genuinely predates the renders. What broke was the *instrument*, and every break is
  now itemised with the direction it pushed. One caveat belongs here rather than in
  the "survives" column: R5 D-1 found a rule this document wrote (§4.5-3) and then
  did not enforce. That is a discipline failure, not an integrity failure, but it is
  the same class of failure that integrity failures hide inside, and the fix (A2-2)
  is now in code rather than in prose.
- **Two custody failures in the repair session itself, both self-reported.**
  (i) Appending A2 to the pre-registration moved its mtime past the original renders
  and permanently weakened `G_PREREG`'s strongest form; the mtime was **not** rewritten
  to hide that (A2-12). (ii) A gate re-run launched without `--out` **overwrote the
  original 05:24:12 `GATES_CUEOFF.md`**; it is reconstructed from an earlier read in
  the same session and labelled as reconstructed, the accidental output is preserved
  outside the audit directory, and the script now refuses that filename. Neither
  changes a number. Both are the kind of thing that goes unmentioned in most methods
  sections, which is why they are here.
- **The B1-collapse direction.** Strip every cue and strict-H recall falls, in the
  same direction, in every scene where it moves at all: s12·e rgb +0.375 / b2 +0.972,
  s12·e2 rgb +0.375 / b2 +0.625, s17 rgb +0.111, s20 original rgb +0.944 / b2 +1.000,
  **s20 repair (27 judged frames, different camera band) rgb +0.778 / b2 +0.926**.
  It survived a 4.5× increase in sample and a change of viewpoint distribution. That
  is a real, large, reproducible effect. What it is **not** is attributable to cues
  (§6.2), and in scene20 the B1 leg is VOID twice over.
- **Convergent evidence for firing without a hazard.** Three independent instruments
  agree that these detectors fire on hazard-free geometry: CUE-OFF arm C
  (scene12 FA .028 → 1.000 against its own floor); sceneC2 new-off (FA .681, C2 root
  cause track); and Gazebo `gz_drop3`, a different renderer, where the hazard prism is
  verified at **0 px** by a leak check and rgb still fires on 11/21 frames and b2 on
  19/21. Two renderers (Isaac PT and Gazebo), three geometries, one behaviour — and
  the Gazebo leg is the one that is not merely a re-reading of the same pixels.
  **This is the strongest thing this weekend produced** and it does not depend on any cue taxonomy, any
  placebo, or any of the machinery A2 had to repair.

### 6.2 What fell

- **"Arm C's FA measures cue-vocabulary reading."** Dead. FA(C) is monotone in the
  optical size of arm C's surgery (58.35 % → 1.000, 36.60 % → 1.000, 13.09 % → 0.361,
  1.02 % → 0.042) and flat in vocabulary — scene17 keeps every cue noun and produces
  FA .042. D46's headline is withdrawn; D49 ① withdrew it and §4.4 supplies the
  measurement.
- **"C-arm FA = 1.000."** Scene12 only, both bands. scene17 .042, scene20 .361.
- **The scene12 arm-C surgery confound, quantified.** scene12's arm C is the only arm
  with a bespoke fill; it sits **6.64 %** of frame from arm A (band e) and **4.32 %**
  (band e2), versus **36.60 % / 58.35 %** from the off round. It also lifts the lower
  dressing **1.36 m**, putting high-contrast white line markings 5 mm above the camera
  ground plane and splitting the reed stands across two heights — a configuration in
  no other arm and no training frame. A model that fires 1.000 on arm A firing 1.000
  on a picture 6.6 % away from arm A is not evidence of cue inference.
- **Every placebo admissibility claim in PREREG §3.** Four grades, four wrong, three
  anti-conservative — including the 18× claim that justified promoting scene17 to the
  primary leg (actual 0.555×) and the 12–30× claim that made B2 scene12's primary leg
  (actual 0.578×). Retracted in A2-5.
- **"Δ_placebo = 0.000 shows the metric is mass-insensitive."** This was the best
  defence available and it does not survive its own data. In **both** scene12 cells
  where the placebo moves anything, it moves *more* than the cue removal does, from
  *less* mass: `boost_e` / b2 Δ_placebo **+0.222** (3/3 seeds, 3.09 % of frame) vs
  Δ_cue **+0.028** (5.34 %) — an eight-fold inversion; `boost_e2` / b2 Δ_placebo
  **+0.153** (2.47 %) vs Δ_cue **+0.125** (6.17 %). The metric is not
  mass-insensitive; it is *sometimes* mass-insensitive, and where it is not, the
  non-cue removal wins.
- **All eight of v1's SHORTCUT verdicts, as evidence** (five in `lineage`, three in
  `twin`). Every one was `(0.000, 0.000, 0.000)`. With 0 flips in 24 paired frames the
  one-sided 95 % bound on the per-frame flip rate is **0.117**, which does not resolve
  this study's own 0.10 threshold; resolving 0.10 with zero flips needs n ≥ 29.
  Reported as NO-EFFECT with the bound attached, never as support for H0.
- **"Gazebo independently reproduces cue-only firing."** Not supportable, and A2 does
  not try to rescue it: the Gazebo control worlds have no cue-free baseline, so their
  false-alarm rate has no floor — the same defect CUE-OFF had until A2-3 printed one.
  Two tracks sharing a defect is not independent confirmation. What survives is §6.1's
  narrower statement (0-pixel hazard, firing anyway) plus the tier-ladder inversion,
  which R5 D-2 re-counts as **5/6**, not the 4/6 D48 recorded.
- **The generality of the D44 ruling.** Correct for six cases, wrong for two. §2.

### 6.3 What is new

- **scene12's strict-H status is manufactured by the degenerate footprint.** The same
  48 frames are tier **V** under a corrected reference. The study's main target scene
  is not a strict-H scene, and no one had drawn that inference from A1.1 before.
- **G4, G5 and G2's `polar_gt` clause had never run** — a filename bug, not a timing
  race — and G5 clears the hand-patched `_solid_at` oracle now that it does run.
- **The eight G2 breaches resolve 6 false / 2 real-but-immaterial**, with the scene20
  mechanism fully localised: cheek-wall removal re-exposes ground, the footprint grows
  1,302 cells, three `none_in_fov` frames become H, and all three are outside the
  judged population.
- **scene20's placebo exists and is the study's best-matched control** (0.909×), and
  its exclusion rested on measuring objects the arm never removes.
- **The lineage-off false-alarm floor**, which was sitting in every `per_frame.csv`
  since 06:03 and makes scene12's arm-C contrast auditable (.028 → 1.000) instead of
  absolute.
- **The scene20 repair round, and the wall behind the wall.** The camera repair
  worked: strict-H yield 25 % → 56 %, paired-H 6 → **27**, and the placebo came out at
  **1.113×** the cue mass — the only ratio above 1 in the study. R4's F14 prediction
  was confirmed in direction and magnitude (+0.667 predicted from 6 frames, **+0.506**
  measured on 27, 3/3 seeds). **And the leg is still VOID**, because removing scene20's
  cheek wall changes the hazard footprint itself (`cells_raw` 60,659 → 61,961) and
  therefore fails §4.5-2 on 6 of the 27 judged frames. The primary-rule CUE EVIDENCE
  count remains **zero**.
- **`cue_railing` is not an appearance-only toggle where the guard is structural.**
  scene12's railing moves 54 heightmap cells by ≤ 5 mm and 0 footprint cells;
  scene20's cheek wall moves 12,656 cells by up to 3.16 m and 1,302 footprint cells.
  The pre-registration treated them as the same kind of manipulation. They are not,
  the difference is mechanically detectable before any model is run
  (`cells_raw` A vs B), and any future use of this instrument should classify each
  guard as ornamental or structural at registration time. This is the most portable
  thing the repair round produced.

### 6.4 The sentence this study can defend

> Two of the three scenes are training scenes and none is a test scene, and the
> pre-registered primary rule returned **zero CUE EVIDENCE** across 30 cells, of which
> only 12 were judgeable at all. The one candidate that would qualify was disqualified
> first by our own sample-size floor and then, after we spent GPU time removing that
> floor, by our own geometry-invariance rule — and we report it as disqualified both
> times, with the number it would have given (+0.506) printed next to the reason it
> does not count. What the intervention did establish is narrower than "the model reads
> cues" and worse than it:
>
> **these detectors respond to whether the picture looks like the hazard scene, not to
> whether the hazard is in it.** Delete the drop and nothing else, and the frame still
> changes by 4.3–13.6 % of its pixels — 10³–10⁵× the renderer noise floor — because a
> hazard is never optically alone. Where that hazard-free twin still resembles the
> hazard scene, the detector fires on it: scene12's arm C at **FA 1.000** against a
> hazard-off-and-cue-off floor of **.028**, and, in a different renderer with the
> hazard prism verified at **0 px** by an independent leak check, Gazebo's `gz_drop3`
> control at .524 (rgb) and .905 (b2). Where the twin instead resembles the plain
> hazard-off world — scene17's arm C, which is **1.02 %** of frame from the off round —
> the detector does not fire (**.042**), and it keeps every cue noun while not firing.
> The ordering is optical, not lexical: arm C's false-alarm rate is monotone in how far
> its surgery moved the picture (58.4 % → 1.000, 36.6 % → 1.000, 13.1 % → 0.361,
> 1.0 % → 0.042) and flat in cue inventory.
>
> We are not able to say from this study which visual property carries that response;
> "cues" and "a third of the picture" are perfectly confounded in every arm we built,
> and our best-matched placebo removes *non-cue* objects and does *more* damage than
> removing the guard does. We ship the pre-registration, the five arms, the placebo
> protocol, the datum-preservation argument and the gate suite as a reusable
> instrument — together with the places it broke in our own hands, the measurements
> that caught each break, and the amendment that repairs them.
