# `look_check/` — render round conventions

`look_check/<scene>/<round>/` holds one grid render per round: the preset cuts
(`{rt,pt}_noon_preset_h{eye}_d{dist}.png`), the mise-en-scène cuts, and a `manifest.json`
carrying per-view `eye`/`tgt` and the render mode. Every tool in `scripts/` reads only
those two things — no GPU, no Isaac.

This directory is **gitignored** (see `.gitignore`, "Render outputs"). `INDEX.md` is
therefore the only committed record of what actually exists on the render machine.
Regenerate it whenever rounds are added or removed.

---

## 1. Naming convention for **new** rounds

```
<yymmdd>_<wave>_<purpose>
```

| field | rule | examples |
|---|---|---|
| `yymmdd` | the date the round was **rendered**, so a plain `ls` sorts chronologically | `260730` |
| `wave` | the work wave that owns it | `w2d`, `w2c`, `t1ab`, `p4`, `spike` |
| `purpose` | what the round is *for*, lowercase, `_`-joined, no version numbers | `judge`, `hoff`, `gate`, `base`, `crop` |

```
look_check/scene13/260730_w2d_judge      # the W2-D judgement grid
look_check/scene13/260730_w2d_hoff       # same build, ground-kit height off  (A/B twin)
look_check/scene19/260730_t1ab_scene19   # t1 material A/B for scene19
look_check/sceneC2/260730_w2d_crop       # zoom crops of the above, not a full grid
```

**Twins must differ only in the trailing token** (`..._gon` / `..._goff`,
`..._on` / `..._off`, `..._a` / `..._b`). `scripts/regression_check.py --before/--after`
is fed these two paths directly, so a shared prefix is what makes the pair readable
in a report six weeks later.

**Do not** encode a version number (`v9`, `r6`) — that is what produced the current
mess. The date already orders the rounds, and the purpose already says what changed.

A crop-only round (a handful of zoomed PNGs rather than the full grid) gets the
`_crop` suffix so that `INDEX.md` and the corpus drivers can skip it: it has no
`manifest.json` geometry and cannot be regression-checked.

---

## 2. Why the old names stay

The pre-2026-07-30 rounds keep their historical names — `final_pt`, `r1…r5`,
`r1_on`/`r2_on`, `v5_rt`…`v8_pt`, `ctx1`/`ctx2`, `p2*`, `t1_*`, `w2*`. They are **not**
renamed, and must not be, because those exact strings are load-bearing in three places:

1. **Validation corpora.** `regression_check.py` v2.1 was validated against a 94-cut
   history set (`v6_rt→v7_rt`, `v7_rt→v8_rt`) and a 157-cut false-positive set
   (mode swap · look A/B · `ctx1→ctx2` · `r1_on→r2_on` · P4 near-field) —
   `Docs/reports/w2_tools_v1.md` §4.3–4.4. Renaming a member silently changes the
   corpus and destroys the reproduction proof.
2. **Published measurement anchors.** `norm_spec.py` / `near_ground_stats.py` /
   `skyline.py` reproduce 4 + 31 + 23 published anchors that name rounds explicitly
   (`scene18/v7_pt`, `scene09/v8_pt`, `sceneC1/r2b_on`, `sceneC2/fix1`, `sceneN4/wall`, …).
3. **Committed report evidence.** `Docs/audit_v4/judge_*.md`, `Docs/reports/*.md` cite
   round paths as the frames a verdict was read from.

So: **old names are frozen, new names follow §1.** `INDEX.md` maps every surviving old
name onto its era, kind and role, which is what the old names fail to say by themselves.

### Legacy name decoder

| legacy pattern | era | meaning |
|---|---|---|
| `r1`, `r2`, `r3`, `r4`, `r5` | 07-24 … 07-27 | early P2/P3 iteration rounds (most now deleted) |
| `final_pt`, `final_pt_r2` | 07-24/27 | v3-era "final" PT grids — **deleted 07-30**, superseded by `v7_pt`/`v8_pt` |
| `v5_rt`, `v5_pt` | 07-27 | v5 judgement ladder — **deleted 07-30**, no corpus role |
| `v6_rt`, `v7_rt`, `v8_rt`, `v8_rt2` | 07-27 | judgement ladder; **history corpus** |
| `v7_pt`, `v8_pt` | 07-27 | the final judged PT grid per scene = **baseline-of-record** |
| `ctx1`, `ctx2`, `ctx*_pt` | 07-27/28 | batch1 context dressing; `ctx1→ctx2` is a corpus series |
| `r1_on`, `r2_on`, `r2b_on` | 07-28 | P4 realism pass; `r2_on` is the standing regression baseline |
| `p2g*`, `p2rf_*`, `p2mat_*`, `p2c_*`, `p2ctrl_*`, `p2det_*` | 07-28 | look-layer A/B toggles — **look A/B corpus** |
| `p2dark_*`, `*_ptfast`, `*_ptlegacy` | 07-28 | render-mode / PT-sample twins — **mode-swap corpus** |
| `balust`, `leaf3d`, `handrail`, `fix1`, `shrub`, `facade`, `planterfix`, `wall` | 07-28/29 | named near-field fix rounds — **P4 near-field corpus** |
| `t1_mtl_*`, `t1_crop` | 07-29 | W2 t1 material-layer twins |
| `w2_pilot*`, `w2c_*`, `wininset_*` | 07-29 | W2 ground pilot / merge / gate rounds |
| `_t0_spike/*`, `spike_*`, `diag_*` | 07-28/29 | throwaway experiment and diagnosis grids |

---

## 3. Standing commands

```bash
cd /home/vislab/Desktop/work_sy/Practice_NegObs

# regression of a new round against the standing baseline
python3 scripts/regression_check.py --scenes 'look_check/scene*' \
  --before-round r2_on --after-round 260730_w2d_judge \
  --fail-only --json Docs/reports/regr_260730_w2d.json

# single A/B twin
python3 scripts/regression_check.py \
  --before look_check/scene13/260730_w2d_hoff \
  --after  look_check/scene13/260730_w2d_judge
```

> `Docs/reports/regression_tool_v1.md` and the `regression_check.py` module docstring
> still show the older fallback chain `--before-round final_pt_r2,final_pt,ctx2_pt,ctx2`.
> `final_pt` / `final_pt_r2` no longer exist (cleanup 07-30); the chain now resolves to
> `ctx2_pt,ctx2` for batch1 and to nothing for the main scenes. Use `r2_on`, per
> `Docs/reports/graze_recalibration_v1.md` §9, which supersedes it.
