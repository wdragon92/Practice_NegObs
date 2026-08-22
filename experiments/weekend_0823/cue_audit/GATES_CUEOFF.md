# GATES_CUEOFF — 2026-08-23 07:32:56

stage `post` · rounds `['260823_cueoff2_A', '260823_cueoff2_B1', '260823_cueoff2_B2', '260823_cueoff2_C', '260823_cueoff2_P', '260823_cueoff_A', '260823_cueoff_B1', '260823_cueoff_B2', '260823_cueoff_C', '260823_cueoff_P']`

**FAIL 12**

## Failures

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
```

## Notes

- G2 BREACH-GLOBAL: 260823_cueoff scene12 B1 vs A: heightmap.npy differs. Adjudicated per-case below and in G2_ADJUDICATION.csv (D49-2); NOT inherited from a sibling case.
- G2 BREACH-GLOBAL: 260823_cueoff scene20 B1 vs A: heightmap.npy differs. Adjudicated per-case below and in G2_ADJUDICATION.csv (D49-2); NOT inherited from a sibling case.
- G2 SCENE-SCOPE ONLY: 260823_cueoff scene20 B1 vs A [lineage]: polar_gt differs on 3/24 frames ['L0__s20260821__0005.png', 'L5__s20260821__0005.png', 'L7__s20260821__0005.png'], but 0 of the 6 PAIRED-H frames. The differing frames are outside the judged population; the paired comparison stands, the scene-level footprint claim does not.
- G2 SCENE-SCOPE ONLY: 260823_cueoff scene20 B1 vs A [twin]: polar_gt differs on 3/24 frames ['L0__s20260821__0005.png', 'L5__s20260821__0005.png', 'L7__s20260821__0005.png'], but 0 of the 6 PAIRED-H frames. The differing frames are outside the judged population; the paired comparison stands, the scene-level footprint claim does not.
- G2 BREACH-GLOBAL: 260823_cueoff scene12 B2 vs A: heightmap.npy differs. Adjudicated per-case below and in G2_ADJUDICATION.csv (D49-2); NOT inherited from a sibling case.
- G2 BREACH-GLOBAL: 260823_cueoff scene20 B2 vs A: heightmap.npy differs. Adjudicated per-case below and in G2_ADJUDICATION.csv (D49-2); NOT inherited from a sibling case.
- G2 SCENE-SCOPE ONLY: 260823_cueoff scene20 B2 vs A [lineage]: polar_gt differs on 3/24 frames ['L0__s20260821__0005.png', 'L5__s20260821__0005.png', 'L7__s20260821__0005.png'], but 0 of the 6 PAIRED-H frames. The differing frames are outside the judged population; the paired comparison stands, the scene-level footprint claim does not.
- G2 SCENE-SCOPE ONLY: 260823_cueoff scene20 B2 vs A [twin]: polar_gt differs on 3/24 frames ['L0__s20260821__0005.png', 'L5__s20260821__0005.png', 'L7__s20260821__0005.png'], but 0 of the 6 PAIRED-H frames. The differing frames are outside the judged population; the paired comparison stands, the scene-level footprint claim does not.
- G2 BREACH-GLOBAL: 260823_cueoff scene12 P vs A: heightmap.npy differs. Adjudicated per-case below and in G2_ADJUDICATION.csv (D49-2); NOT inherited from a sibling case.
- G2 BREACH-GLOBAL: 260823_cueoff2 scene12 B1 vs A: heightmap.npy differs. Adjudicated per-case below and in G2_ADJUDICATION.csv (D49-2); NOT inherited from a sibling case.
- G2 BREACH-GLOBAL: 260823_cueoff2 scene12 B2 vs A: heightmap.npy differs. Adjudicated per-case below and in G2_ADJUDICATION.csv (D49-2); NOT inherited from a sibling case.
- G2 BREACH-GLOBAL: 260823_cueoff2 scene12 P vs A: heightmap.npy differs. Adjudicated per-case below and in G2_ADJUDICATION.csv (D49-2); NOT inherited from a sibling case.
- G5 VACUOUS: twin 260823_cueoff scene12 C: 24/24 all-zero GT, but in the `twin` set arm C IS the reference surface, so 0 is constitutive and carries no information (R4 F5).
- G5 VACUOUS: twin 260823_cueoff scene17 C: 24/24 all-zero GT, but in the `twin` set arm C IS the reference surface, so 0 is constitutive and carries no information (R4 F5).
- G5 VACUOUS: twin 260823_cueoff scene20 C: 24/24 all-zero GT, but in the `twin` set arm C IS the reference surface, so 0 is constitutive and carries no information (R4 F5).
- G5 VACUOUS: twin 260823_cueoff2 scene12 C: 24/24 all-zero GT, but in the `twin` set arm C IS the reference surface, so 0 is constitutive and carries no information (R4 F5).
- G7 DEGENERATE FOOTPRINT: lineage__260823_cueoff2_A__scene12 / scene12 cells_raw=50 max_diff=0.3394 -- every recall number for this scene-set is scored against that sliver and MUST carry the caveat (PREREG A1.1). Not a stop condition: the degeneracy is a finding, not a bug in this run.
- G7 DEGENERATE FOOTPRINT: lineage__260823_cueoff2_B1__scene12 / scene12 cells_raw=50 max_diff=0.3394 -- every recall number for this scene-set is scored against that sliver and MUST carry the caveat (PREREG A1.1). Not a stop condition: the degeneracy is a finding, not a bug in this run.
- G7 DEGENERATE FOOTPRINT: lineage__260823_cueoff2_B2__scene12 / scene12 cells_raw=50 max_diff=0.3394 -- every recall number for this scene-set is scored against that sliver and MUST carry the caveat (PREREG A1.1). Not a stop condition: the degeneracy is a finding, not a bug in this run.
- G7 DEGENERATE FOOTPRINT: lineage__260823_cueoff2_C__scene12 / scene12 cells_raw=0 max_diff=0.0009 -- every recall number for this scene-set is scored against that sliver and MUST carry the caveat (PREREG A1.1). Not a stop condition: the degeneracy is a finding, not a bug in this run.
- G7 DEGENERATE FOOTPRINT: lineage__260823_cueoff2_P__scene12 / scene12 cells_raw=50 max_diff=0.3394 -- every recall number for this scene-set is scored against that sliver and MUST carry the caveat (PREREG A1.1). Not a stop condition: the degeneracy is a finding, not a bug in this run.
- G7 DEGENERATE FOOTPRINT: lineage__260823_cueoff_A__scene12 / scene12 cells_raw=50 max_diff=0.3394 -- every recall number for this scene-set is scored against that sliver and MUST carry the caveat (PREREG A1.1). Not a stop condition: the degeneracy is a finding, not a bug in this run.
- G7 DEGENERATE FOOTPRINT: lineage__260823_cueoff_B1__scene12 / scene12 cells_raw=50 max_diff=0.3394 -- every recall number for this scene-set is scored against that sliver and MUST carry the caveat (PREREG A1.1). Not a stop condition: the degeneracy is a finding, not a bug in this run.
- G7 DEGENERATE FOOTPRINT: lineage__260823_cueoff_B2__scene12 / scene12 cells_raw=50 max_diff=0.3394 -- every recall number for this scene-set is scored against that sliver and MUST carry the caveat (PREREG A1.1). Not a stop condition: the degeneracy is a finding, not a bug in this run.
- G7 DEGENERATE FOOTPRINT: lineage__260823_cueoff_C__scene12 / scene12 cells_raw=0 max_diff=0.0009 -- every recall number for this scene-set is scored against that sliver and MUST carry the caveat (PREREG A1.1). Not a stop condition: the degeneracy is a finding, not a bug in this run.
- G7 DEGENERATE FOOTPRINT: lineage__260823_cueoff_C__scene17 / scene17 cells_raw=0 max_diff=0.0 -- every recall number for this scene-set is scored against that sliver and MUST carry the caveat (PREREG A1.1). Not a stop condition: the degeneracy is a finding, not a bug in this run.
- G7 DEGENERATE FOOTPRINT: lineage__260823_cueoff_C__scene20 / scene20 cells_raw=0 max_diff=0.0 -- every recall number for this scene-set is scored against that sliver and MUST carry the caveat (PREREG A1.1). Not a stop condition: the degeneracy is a finding, not a bug in this run.
- G7 DEGENERATE FOOTPRINT: lineage__260823_cueoff_P__scene12 / scene12 cells_raw=50 max_diff=0.3394 -- every recall number for this scene-set is scored against that sliver and MUST carry the caveat (PREREG A1.1). Not a stop condition: the degeneracy is a finding, not a bug in this run.
- G7 DEGENERATE FOOTPRINT: twin__260823_cueoff2_C__scene12 / scene12 cells_raw=0 max_diff=0.0 -- every recall number for this scene-set is scored against that sliver and MUST carry the caveat (PREREG A1.1). Not a stop condition: the degeneracy is a finding, not a bug in this run.
- G7 DEGENERATE FOOTPRINT: twin__260823_cueoff_C__scene12 / scene12 cells_raw=0 max_diff=0.0 -- every recall number for this scene-set is scored against that sliver and MUST carry the caveat (PREREG A1.1). Not a stop condition: the degeneracy is a finding, not a bug in this run.
- G7 DEGENERATE FOOTPRINT: twin__260823_cueoff_C__scene17 / scene17 cells_raw=0 max_diff=0.0 -- every recall number for this scene-set is scored against that sliver and MUST carry the caveat (PREREG A1.1). Not a stop condition: the degeneracy is a finding, not a bug in this run.
- G7 DEGENERATE FOOTPRINT: twin__260823_cueoff_C__scene20 / scene20 cells_raw=0 max_diff=0.0 -- every recall number for this scene-set is scored against that sliver and MUST carry the caveat (PREREG A1.1). Not a stop condition: the degeneracy is a finding, not a bug in this run.
