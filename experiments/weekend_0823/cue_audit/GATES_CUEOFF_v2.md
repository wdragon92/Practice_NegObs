# GATES_CUEOFF — 2026-08-23 09:09:28

stage `all` · rounds `['260823_cueoff2_A', '260823_cueoff2_B1', '260823_cueoff2_B2', '260823_cueoff2_C', '260823_cueoff2_P', '260823_cueoff_A', '260823_cueoff_B1', '260823_cueoff_B2', '260823_cueoff_C', '260823_cueoff_P', '260823_cueoff_s20fix_A', '260823_cueoff_s20fix_B1', '260823_cueoff_s20fix_B2', '260823_cueoff_s20fix_C', '260823_cueoff_s20fix_P']`

**FAIL 26**

> ## DEGENERATE FOOTPRINT BANNER (PREREG A1.2-3)
>
> Every recall number computed against the following scene-labelset pairs is scored on a footprint sliver, not on the hazard:
>
> - `lineage__260823_cueoff2_A__scene12 (scene12) cells_raw=50`
> - `lineage__260823_cueoff2_B1__scene12 (scene12) cells_raw=50`
> - `lineage__260823_cueoff2_B2__scene12 (scene12) cells_raw=50`
> - `lineage__260823_cueoff2_P__scene12 (scene12) cells_raw=50`
> - `lineage__260823_cueoff_A__scene12 (scene12) cells_raw=50`
> - `lineage__260823_cueoff_B1__scene12 (scene12) cells_raw=50`
> - `lineage__260823_cueoff_B2__scene12 (scene12) cells_raw=50`
> - `lineage__260823_cueoff_P__scene12 (scene12) cells_raw=50`
>
## Failures

- **G2-hash** — 260823_cueoff scene12 B1 vs A: heightmap.npy differs -- clause 2 of G2 FAILS at global scope. Adjudicated per-case below and in G2_ADJUDICATION.csv (D49-2); NOT inherited from a sibling case. The material question is the polar_gt clause on the judged population, printed next.
- **G2-hash** — 260823_cueoff scene20 B1 vs A: heightmap.npy differs -- clause 2 of G2 FAILS at global scope. Adjudicated per-case below and in G2_ADJUDICATION.csv (D49-2); NOT inherited from a sibling case. The material question is the polar_gt clause on the judged population, printed next.
- **G2-hash** — 260823_cueoff scene12 B2 vs A: heightmap.npy differs -- clause 2 of G2 FAILS at global scope. Adjudicated per-case below and in G2_ADJUDICATION.csv (D49-2); NOT inherited from a sibling case. The material question is the polar_gt clause on the judged population, printed next.
- **G2-hash** — 260823_cueoff scene20 B2 vs A: heightmap.npy differs -- clause 2 of G2 FAILS at global scope. Adjudicated per-case below and in G2_ADJUDICATION.csv (D49-2); NOT inherited from a sibling case. The material question is the polar_gt clause on the judged population, printed next.
- **G2-hash** — 260823_cueoff scene12 P vs A: heightmap.npy differs -- clause 2 of G2 FAILS at global scope. Adjudicated per-case below and in G2_ADJUDICATION.csv (D49-2); NOT inherited from a sibling case. The material question is the polar_gt clause on the judged population, printed next.
- **G2-hash** — 260823_cueoff2 scene12 B1 vs A: heightmap.npy differs -- clause 2 of G2 FAILS at global scope. Adjudicated per-case below and in G2_ADJUDICATION.csv (D49-2); NOT inherited from a sibling case. The material question is the polar_gt clause on the judged population, printed next.
- **G2-hash** — 260823_cueoff2 scene12 B2 vs A: heightmap.npy differs -- clause 2 of G2 FAILS at global scope. Adjudicated per-case below and in G2_ADJUDICATION.csv (D49-2); NOT inherited from a sibling case. The material question is the polar_gt clause on the judged population, printed next.
- **G2-hash** — 260823_cueoff2 scene12 P vs A: heightmap.npy differs -- clause 2 of G2 FAILS at global scope. Adjudicated per-case below and in G2_ADJUDICATION.csv (D49-2); NOT inherited from a sibling case. The material question is the polar_gt clause on the judged population, printed next.
- **G2-hash** — 260823_cueoff_s20fix scene20 B1 vs A: heightmap.npy differs -- clause 2 of G2 FAILS at global scope. Adjudicated per-case below and in G2_ADJUDICATION.csv (D49-2); NOT inherited from a sibling case. The material question is the polar_gt clause on the judged population, printed next.
- **G2** — 260823_cueoff_s20fix scene20 B1 vs A [lineage]: polar_gt differs on 6/27 PAIRED-H frames ['L0__s20260821__0005.png', 'L0__s20260821__0014.png', 'L5__s20260821__0005.png'] -- the judged population is scored on two different sheets. PREREG sec.4.5-2 VOIDS this pair.
- **G2** — 260823_cueoff_s20fix scene20 B1 vs A [twin]: polar_gt differs on 6/27 PAIRED-H frames ['L0__s20260821__0005.png', 'L0__s20260821__0014.png', 'L5__s20260821__0005.png'] -- the judged population is scored on two different sheets. PREREG sec.4.5-2 VOIDS this pair.
- **G2-hash** — 260823_cueoff_s20fix scene20 B2 vs A: heightmap.npy differs -- clause 2 of G2 FAILS at global scope. Adjudicated per-case below and in G2_ADJUDICATION.csv (D49-2); NOT inherited from a sibling case. The material question is the polar_gt clause on the judged population, printed next.
- **G2** — 260823_cueoff_s20fix scene20 B2 vs A [lineage]: polar_gt differs on 6/27 PAIRED-H frames ['L0__s20260821__0005.png', 'L0__s20260821__0014.png', 'L5__s20260821__0005.png'] -- the judged population is scored on two different sheets. PREREG sec.4.5-2 VOIDS this pair.
- **G2** — 260823_cueoff_s20fix scene20 B2 vs A [twin]: polar_gt differs on 6/27 PAIRED-H frames ['L0__s20260821__0005.png', 'L0__s20260821__0014.png', 'L5__s20260821__0005.png'] -- the judged population is scored on two different sheets. PREREG sec.4.5-2 VOIDS this pair.
- **G4** — [lineage] 260823_cueoff scene20 A/B1: paired-H 6 < 10 -- PREREG sec.4.5-3 VOIDS this scene-arm (verdict blocks included, not only table rows)
- **G4** — [lineage] 260823_cueoff scene20 A/B2: paired-H 6 < 10 -- PREREG sec.4.5-3 VOIDS this scene-arm (verdict blocks included, not only table rows)
- **G4** — [lineage] 260823_cueoff scene20 A/P: paired-H 6 < 10 -- PREREG sec.4.5-3 VOIDS this scene-arm (verdict blocks included, not only table rows)
- **G4** — [twin] 260823_cueoff scene12 A/B1: paired-H 0 < 10 -- PREREG sec.4.5-3 VOIDS this scene-arm (verdict blocks included, not only table rows)
- **G4** — [twin] 260823_cueoff scene12 A/B2: paired-H 0 < 10 -- PREREG sec.4.5-3 VOIDS this scene-arm (verdict blocks included, not only table rows)
- **G4** — [twin] 260823_cueoff scene12 A/P: paired-H 0 < 10 -- PREREG sec.4.5-3 VOIDS this scene-arm (verdict blocks included, not only table rows)
- **G4** — [twin] 260823_cueoff scene20 A/B1: paired-H 6 < 10 -- PREREG sec.4.5-3 VOIDS this scene-arm (verdict blocks included, not only table rows)
- **G4** — [twin] 260823_cueoff scene20 A/B2: paired-H 6 < 10 -- PREREG sec.4.5-3 VOIDS this scene-arm (verdict blocks included, not only table rows)
- **G4** — [twin] 260823_cueoff scene20 A/P: paired-H 6 < 10 -- PREREG sec.4.5-3 VOIDS this scene-arm (verdict blocks included, not only table rows)
- **G4** — [twin] 260823_cueoff2 scene12 A/B1: paired-H 0 < 10 -- PREREG sec.4.5-3 VOIDS this scene-arm (verdict blocks included, not only table rows)
- **G4** — [twin] 260823_cueoff2 scene12 A/B2: paired-H 0 < 10 -- PREREG sec.4.5-3 VOIDS this scene-arm (verdict blocks included, not only table rows)
- **G4** — [twin] 260823_cueoff2 scene12 A/P: paired-H 0 < 10 -- PREREG sec.4.5-3 VOIDS this scene-arm (verdict blocks included, not only table rows)

## G3 pose strata (per scene x arm)

```
260823_cueoff scene12 B1: exact 24/24 · tol 0 · FAIL 0
260823_cueoff scene17 B1: exact 24/24 · tol 0 · FAIL 0
260823_cueoff scene20 B1: exact 18/24 · tol 6 · FAIL 0 · worst |eye_z| 0.008500 on L0__s20260821__0000.png
260823_cueoff scene12 B2: exact 24/24 · tol 0 · FAIL 0
260823_cueoff scene20 B2: exact 24/24 · tol 0 · FAIL 0
260823_cueoff scene12 C: exact 24/24 · tol 0 · FAIL 0
260823_cueoff scene17 C: exact 24/24 · tol 0 · FAIL 0
260823_cueoff scene20 C: exact 24/24 · tol 0 · FAIL 0
260823_cueoff scene12 P: exact 24/24 · tol 0 · FAIL 0
260823_cueoff scene17 P: exact 24/24 · tol 0 · FAIL 0
260823_cueoff scene20 P: exact 24/24 · tol 0 · FAIL 0
260823_cueoff2 scene12 B1: exact 24/24 · tol 0 · FAIL 0
260823_cueoff2 scene12 B2: exact 24/24 · tol 0 · FAIL 0
260823_cueoff2 scene12 C: exact 24/24 · tol 0 · FAIL 0
260823_cueoff2 scene12 P: exact 24/24 · tol 0 · FAIL 0
260823_cueoff_s20fix scene20 B1: exact 42/48 · tol 6 · FAIL 0 · worst |eye_z| 0.008500 on L0__s20260821__0000.png
260823_cueoff_s20fix scene20 B2: exact 48/48 · tol 0 · FAIL 0
260823_cueoff_s20fix scene20 C: exact 48/48 · tol 0 · FAIL 0
260823_cueoff_s20fix scene20 P: exact 48/48 · tol 0 · FAIL 0
```

## G4 tier re-derivation + migration (per label set)

```
lineage  260823_cueoff   scene12  A : V 0 · E 0 · H 24 · H_weak 0 · none_in_fov 0
lineage  260823_cueoff   scene17  A : V 0 · E 0 · H 24 · H_weak 0 · none_in_fov 0
lineage  260823_cueoff   scene20  A : V 9 · E 0 · H 6 · H_weak 0 · none_in_fov 9
lineage  260823_cueoff   scene12  B1: V 0 · E 0 · H 24 · H_weak 0 · none_in_fov 0
lineage  260823_cueoff   scene17  B1: V 0 · E 0 · H 24 · H_weak 0 · none_in_fov 0
lineage  260823_cueoff   scene20  B1: V 9 · E 0 · H 9 · H_weak 0 · none_in_fov 6
lineage  260823_cueoff   scene12  B2: V 0 · E 0 · H 24 · H_weak 0 · none_in_fov 0
lineage  260823_cueoff   scene20  B2: V 9 · E 0 · H 9 · H_weak 0 · none_in_fov 6
lineage  260823_cueoff   scene12  C : V 0 · E 0 · H 0 · H_weak 0 · none_in_fov 24
lineage  260823_cueoff   scene17  C : V 0 · E 0 · H 0 · H_weak 0 · none_in_fov 24
lineage  260823_cueoff   scene20  C : V 0 · E 0 · H 0 · H_weak 0 · none_in_fov 24
lineage  260823_cueoff   scene12  P : V 0 · E 0 · H 24 · H_weak 0 · none_in_fov 0
lineage  260823_cueoff   scene17  P : V 0 · E 0 · H 24 · H_weak 0 · none_in_fov 0
lineage  260823_cueoff   scene20  P : V 9 · E 0 · H 6 · H_weak 0 · none_in_fov 9
lineage  260823_cueoff2  scene12  A : V 0 · E 0 · H 24 · H_weak 0 · none_in_fov 0
lineage  260823_cueoff2  scene12  B1: V 0 · E 0 · H 24 · H_weak 0 · none_in_fov 0
lineage  260823_cueoff2  scene12  B2: V 0 · E 0 · H 24 · H_weak 0 · none_in_fov 0
lineage  260823_cueoff2  scene12  C : V 0 · E 0 · H 0 · H_weak 0 · none_in_fov 24
lineage  260823_cueoff2  scene12  P : V 0 · E 0 · H 24 · H_weak 0 · none_in_fov 0
lineage  260823_cueoff_s20fix scene20  A : V 12 · E 0 · H 27 · H_weak 0 · none_in_fov 9
lineage  260823_cueoff_s20fix scene20  B1: V 6 · E 0 · H 27 · H_weak 6 · none_in_fov 9
lineage  260823_cueoff_s20fix scene20  B2: V 12 · E 0 · H 27 · H_weak 0 · none_in_fov 9
lineage  260823_cueoff_s20fix scene20  C : V 0 · E 0 · H 0 · H_weak 0 · none_in_fov 48
lineage  260823_cueoff_s20fix scene20  P : V 12 · E 0 · H 27 · H_weak 0 · none_in_fov 9
lineage  260823_cueoff   scene12  A->B1: paired-H 24 · no tier movement
lineage  260823_cueoff   scene12  A->B2: paired-H 24 · no tier movement
lineage  260823_cueoff   scene12  A->C : paired-H 0 · migrations {'H->none_in_fov': 24}
lineage  260823_cueoff   scene12  A->P : paired-H 24 · no tier movement
lineage  260823_cueoff   scene17  A->B1: paired-H 24 · no tier movement
lineage  260823_cueoff   scene17  A->C : paired-H 0 · migrations {'H->none_in_fov': 24}
lineage  260823_cueoff   scene17  A->P : paired-H 24 · no tier movement
lineage  260823_cueoff   scene20  A->B1: paired-H 6 · migrations {'none_in_fov->H': 3}
lineage  260823_cueoff   scene20  A->B2: paired-H 6 · migrations {'none_in_fov->H': 3}
lineage  260823_cueoff   scene20  A->C : paired-H 0 · migrations {'H->none_in_fov': 6, 'V->none_in_fov': 9}
lineage  260823_cueoff   scene20  A->P : paired-H 6 · no tier movement
lineage  260823_cueoff2  scene12  A->B1: paired-H 24 · no tier movement
lineage  260823_cueoff2  scene12  A->B2: paired-H 24 · no tier movement
lineage  260823_cueoff2  scene12  A->C : paired-H 0 · migrations {'H->none_in_fov': 24}
lineage  260823_cueoff2  scene12  A->P : paired-H 24 · no tier movement
lineage  260823_cueoff_s20fix scene20  A->B1: paired-H 27 · migrations {'V->H_weak': 6}
lineage  260823_cueoff_s20fix scene20  A->B2: paired-H 27 · no tier movement
lineage  260823_cueoff_s20fix scene20  A->C : paired-H 0 · migrations {'H->none_in_fov': 27, 'V->none_in_fov': 12}
lineage  260823_cueoff_s20fix scene20  A->P : paired-H 27 · no tier movement
twin     260823_cueoff   scene12  A : V 24 · E 0 · H 0 · H_weak 0 · none_in_fov 0
twin     260823_cueoff   scene17  A : V 0 · E 0 · H 24 · H_weak 0 · none_in_fov 0
twin     260823_cueoff   scene20  A : V 9 · E 0 · H 6 · H_weak 0 · none_in_fov 9
twin     260823_cueoff   scene12  B1: V 24 · E 0 · H 0 · H_weak 0 · none_in_fov 0
twin     260823_cueoff   scene17  B1: V 0 · E 0 · H 24 · H_weak 0 · none_in_fov 0
twin     260823_cueoff   scene20  B1: V 9 · E 0 · H 9 · H_weak 0 · none_in_fov 6
twin     260823_cueoff   scene12  B2: V 24 · E 0 · H 0 · H_weak 0 · none_in_fov 0
twin     260823_cueoff   scene20  B2: V 9 · E 0 · H 9 · H_weak 0 · none_in_fov 6
twin     260823_cueoff   scene12  C : V 0 · E 0 · H 0 · H_weak 0 · none_in_fov 24
twin     260823_cueoff   scene17  C : V 0 · E 0 · H 0 · H_weak 0 · none_in_fov 24
twin     260823_cueoff   scene20  C : V 0 · E 0 · H 0 · H_weak 0 · none_in_fov 24
twin     260823_cueoff   scene12  P : V 24 · E 0 · H 0 · H_weak 0 · none_in_fov 0
twin     260823_cueoff   scene17  P : V 0 · E 0 · H 24 · H_weak 0 · none_in_fov 0
twin     260823_cueoff   scene20  P : V 9 · E 0 · H 6 · H_weak 0 · none_in_fov 9
twin     260823_cueoff2  scene12  A : V 24 · E 0 · H 0 · H_weak 0 · none_in_fov 0
twin     260823_cueoff2  scene12  B1: V 6 · E 0 · H 18 · H_weak 0 · none_in_fov 0
twin     260823_cueoff2  scene12  B2: V 24 · E 0 · H 0 · H_weak 0 · none_in_fov 0
twin     260823_cueoff2  scene12  C : V 0 · E 0 · H 0 · H_weak 0 · none_in_fov 24
twin     260823_cueoff2  scene12  P : V 24 · E 0 · H 0 · H_weak 0 · none_in_fov 0
twin     260823_cueoff_s20fix scene20  A : V 12 · E 0 · H 27 · H_weak 0 · none_in_fov 9
twin     260823_cueoff_s20fix scene20  B1: V 6 · E 0 · H 27 · H_weak 6 · none_in_fov 9
twin     260823_cueoff_s20fix scene20  B2: V 12 · E 0 · H 27 · H_weak 0 · none_in_fov 9
twin     260823_cueoff_s20fix scene20  C : V 0 · E 0 · H 0 · H_weak 0 · none_in_fov 48
twin     260823_cueoff_s20fix scene20  P : V 12 · E 0 · H 27 · H_weak 0 · none_in_fov 9
twin     260823_cueoff   scene12  A->B1: paired-H 0 · no tier movement
twin     260823_cueoff   scene12  A->B2: paired-H 0 · no tier movement
twin     260823_cueoff   scene12  A->C : paired-H 0 · migrations {'V->none_in_fov': 24}
twin     260823_cueoff   scene12  A->P : paired-H 0 · no tier movement
twin     260823_cueoff   scene17  A->B1: paired-H 24 · no tier movement
twin     260823_cueoff   scene17  A->C : paired-H 0 · migrations {'H->none_in_fov': 24}
twin     260823_cueoff   scene17  A->P : paired-H 24 · no tier movement
twin     260823_cueoff   scene20  A->B1: paired-H 6 · migrations {'none_in_fov->H': 3}
twin     260823_cueoff   scene20  A->B2: paired-H 6 · migrations {'none_in_fov->H': 3}
twin     260823_cueoff   scene20  A->C : paired-H 0 · migrations {'H->none_in_fov': 6, 'V->none_in_fov': 9}
twin     260823_cueoff   scene20  A->P : paired-H 6 · no tier movement
twin     260823_cueoff2  scene12  A->B1: paired-H 0 · migrations {'V->H': 18}
twin     260823_cueoff2  scene12  A->B2: paired-H 0 · no tier movement
twin     260823_cueoff2  scene12  A->C : paired-H 0 · migrations {'V->none_in_fov': 24}
twin     260823_cueoff2  scene12  A->P : paired-H 0 · no tier movement
twin     260823_cueoff_s20fix scene20  A->B1: paired-H 27 · migrations {'V->H_weak': 6}
twin     260823_cueoff_s20fix scene20  A->B2: paired-H 27 · no tier movement
twin     260823_cueoff_s20fix scene20  A->C : paired-H 0 · migrations {'H->none_in_fov': 27, 'V->none_in_fov': 12}
twin     260823_cueoff_s20fix scene20  A->P : paired-H 27 · no tier movement
```

## Notes

- G_PREREG A2-12: PREREG_CUEOFF.md carries a POST-HOC amendment (A2, declared 2026-08-23 07:42:00), so its mtime (2026-08-23 09:09:20) is later than the pre-A2 renders and is NO LONGER a usable registration time. This gate now compares against the timestamps the document DECLARES, and the mtime-based form of the proof is not available for the pre-A2 rounds. Independent corroboration on record: red-team R4 verified the 03:55 prereg / 05:01 render ordering before A2 existed. PREREG_HASHES.json freezes the file from here on.
- G0: no lineage mapping for 260823_cueoff_s20fix/scene20 -- skipped
- 260823_cueoff scene20 B1: exact 18/24 · tol 6 · FAIL 0 · worst |eye_z| 0.008500 on L0__s20260821__0000.png  -> declared TOL stratum (PREREG sec.5.1); primary readout runs on pose_exact only
- 260823_cueoff_s20fix scene20 B1: exact 42/48 · tol 6 · FAIL 0 · worst |eye_z| 0.008500 on L0__s20260821__0000.png  -> declared TOL stratum (PREREG sec.5.1); primary readout runs on pose_exact only
- G2 SCENE-SCOPE ONLY: 260823_cueoff scene20 B1 vs A [lineage]: polar_gt differs on 3/24 frames ['L0__s20260821__0005.png', 'L5__s20260821__0005.png', 'L7__s20260821__0005.png'], but 0 of the 6 PAIRED-H frames. The differing frames are outside the judged population; the paired comparison stands, the scene-level footprint claim does not.
- G2 SCENE-SCOPE ONLY: 260823_cueoff scene20 B1 vs A [twin]: polar_gt differs on 3/24 frames ['L0__s20260821__0005.png', 'L5__s20260821__0005.png', 'L7__s20260821__0005.png'], but 0 of the 6 PAIRED-H frames. The differing frames are outside the judged population; the paired comparison stands, the scene-level footprint claim does not.
- G2 SCENE-SCOPE ONLY: 260823_cueoff scene20 B2 vs A [lineage]: polar_gt differs on 3/24 frames ['L0__s20260821__0005.png', 'L5__s20260821__0005.png', 'L7__s20260821__0005.png'], but 0 of the 6 PAIRED-H frames. The differing frames are outside the judged population; the paired comparison stands, the scene-level footprint claim does not.
- G2 SCENE-SCOPE ONLY: 260823_cueoff scene20 B2 vs A [twin]: polar_gt differs on 3/24 frames ['L0__s20260821__0005.png', 'L5__s20260821__0005.png', 'L7__s20260821__0005.png'], but 0 of the 6 PAIRED-H frames. The differing frames are outside the judged population; the paired comparison stands, the scene-level footprint claim does not.
- G5 VACUOUS: twin 260823_cueoff scene12 C: 24/24 all-zero GT, but in the `twin` set arm C IS the reference surface, so 0 is constitutive and carries no information (R4 F5).
- G5 VACUOUS: twin 260823_cueoff scene17 C: 24/24 all-zero GT, but in the `twin` set arm C IS the reference surface, so 0 is constitutive and carries no information (R4 F5).
- G5 VACUOUS: twin 260823_cueoff scene20 C: 24/24 all-zero GT, but in the `twin` set arm C IS the reference surface, so 0 is constitutive and carries no information (R4 F5).
- G5 VACUOUS: twin 260823_cueoff2 scene12 C: 24/24 all-zero GT, but in the `twin` set arm C IS the reference surface, so 0 is constitutive and carries no information (R4 F5).
- G5 VACUOUS: twin 260823_cueoff_s20fix scene20 C: 48/48 all-zero GT, but in the `twin` set arm C IS the reference surface, so 0 is constitutive and carries no information (R4 F5).
- G7 DEGENERATE FOOTPRINT: lineage__260823_cueoff2_A__scene12 / scene12 cells_raw=50 max_diff=0.3394 -- every recall number for this scene-set is scored against that sliver and MUST carry the caveat (PREREG A1.1). Not a stop condition: the degeneracy is a finding, not a bug in this run.
- G7 DEGENERATE FOOTPRINT: lineage__260823_cueoff2_B1__scene12 / scene12 cells_raw=50 max_diff=0.3394 -- every recall number for this scene-set is scored against that sliver and MUST carry the caveat (PREREG A1.1). Not a stop condition: the degeneracy is a finding, not a bug in this run.
- G7 DEGENERATE FOOTPRINT: lineage__260823_cueoff2_B2__scene12 / scene12 cells_raw=50 max_diff=0.3394 -- every recall number for this scene-set is scored against that sliver and MUST carry the caveat (PREREG A1.1). Not a stop condition: the degeneracy is a finding, not a bug in this run.
- G7 DEGENERATE FOOTPRINT: lineage__260823_cueoff2_P__scene12 / scene12 cells_raw=50 max_diff=0.3394 -- every recall number for this scene-set is scored against that sliver and MUST carry the caveat (PREREG A1.1). Not a stop condition: the degeneracy is a finding, not a bug in this run.
- G7 DEGENERATE FOOTPRINT: lineage__260823_cueoff_A__scene12 / scene12 cells_raw=50 max_diff=0.3394 -- every recall number for this scene-set is scored against that sliver and MUST carry the caveat (PREREG A1.1). Not a stop condition: the degeneracy is a finding, not a bug in this run.
- G7 DEGENERATE FOOTPRINT: lineage__260823_cueoff_B1__scene12 / scene12 cells_raw=50 max_diff=0.3394 -- every recall number for this scene-set is scored against that sliver and MUST carry the caveat (PREREG A1.1). Not a stop condition: the degeneracy is a finding, not a bug in this run.
- G7 DEGENERATE FOOTPRINT: lineage__260823_cueoff_B2__scene12 / scene12 cells_raw=50 max_diff=0.3394 -- every recall number for this scene-set is scored against that sliver and MUST carry the caveat (PREREG A1.1). Not a stop condition: the degeneracy is a finding, not a bug in this run.
- G7 DEGENERATE FOOTPRINT: lineage__260823_cueoff_P__scene12 / scene12 cells_raw=50 max_diff=0.3394 -- every recall number for this scene-set is scored against that sliver and MUST carry the caveat (PREREG A1.1). Not a stop condition: the degeneracy is a finding, not a bug in this run.
- G7 BOOST-LINEAGE DEGENERACY ACCOUNTING (A1.1): the `lineage` reference is the boost round, which never ran fuse_heightmap.py; the `twin` reference is arm C of this round, which did. Where they disagree, the lineage footprint is the degenerate one: 260823_cueoff2_A scene12: lineage 50 vs twin 50278 cells (1006x) · 260823_cueoff2_B1 scene12: lineage 50 vs twin 50278 cells (1006x) · 260823_cueoff2_B2 scene12: lineage 50 vs twin 50278 cells (1006x) · 260823_cueoff2_P scene12: lineage 50 vs twin 50278 cells (1006x) · 260823_cueoff_A scene12: lineage 50 vs twin 50278 cells (1006x) · 260823_cueoff_B1 scene12: lineage 50 vs twin 50278 cells (1006x) · 260823_cueoff_B2 scene12: lineage 50 vs twin 50278 cells (1006x) · 260823_cueoff_P scene12: lineage 50 vs twin 50278 cells (1006x)
