# `look_check/` — render round conventions

`look_check/<scene>/<round>/` holds one grid render per round: the preset cuts
(`{rt,pt}_noon_preset_h{eye}_d{dist}.png`), the mise-en-scène cuts, and a `manifest.json`
carrying per-view `eye`/`tgt` and the render mode. Every tool in `scripts/` reads only
those two things — no GPU, no Isaac.

This directory is **gitignored** (see `.gitignore`, "Render outputs") except for this file
and `INDEX.md`. `INDEX.md` is therefore the only committed record of what actually exists
on the render machine. Regenerate it whenever rounds are added, moved or removed.

---

## 1. Structure

```
look_check/
  <scene>/<round>/            judgement grids, corpus members, anchors, baselines-of-record
  _experiments/
    t0_spike/<round>/         T0 spike tree (incl. its conc* throughput arms)
    spike_p1/<dir>/           P1 realism spikes + the sample-count / time-budget probe
    diag/<dir>/               dead-pixel and per-scene diagnostics
    gates/<scene>/<round>/    gate probes and zoom crops
    twins/<scene>/<round>/    A/B twin arms
  _t0_spike   -> _experiments/t0_spike               (symlink, load-bearing)
  spike_probe -> _experiments/spike_p1/spike_probe   (symlink, spec-cited)
  logs/, *.log, spike_results.json                   render journals, left at root
```

**The rule that decides where a round goes.** A round sits at the **scene root** if and
only if it is one of:

- a **judgement grid** (the full preset grid a supervisor verdict was read from),
- a **corpus member** (§3 below),
- a **published measurement anchor**, or
- the scene's **baseline-of-record** (what the next regression run compares against).

Everything else — zoom crops, gate probes, single-flag A/B arms, spikes, diagnostics —
goes under `_experiments/<topic>/`. Per-scene experimental rounds keep their scene folder
(`_experiments/twins/scene19/t1_mtl_on_s2/`) so that identically named rounds in different
scenes cannot collide.

**Why this matters more than tidiness.** `ls -t <scene>/*/ | head -1` is how "the latest
round" gets found by eye and by script. Before the grouping that returned a *crop* for
scene02/07/13/14/15/N3/N5/C2 and a *veg_test twin* for scene01/04/10/19 — i.e. picking any
of those as a regression baseline would have compared a 2-cut zoom against a 13-cut grid.
After the grouping every scene's latest is a judgement round. Keep it that way: **do not
render a new gate/crop/twin into the scene root.**

### Symlink policy

Symlinks exist **only** for paths a *future* consumer resolves, and **only at root level**:

| symlink | why |
|---|---|
| `_t0_spike/` → `_experiments/t0_spike/` | `t1_material_layer_spec_v1.md` §7 cites `_t0_spike/c2_A_base/` as the A/B baseline convention |
| `spike_probe/` → `_experiments/spike_p1/spike_probe/` | `lighting_camera_variation_spec_v1.md` §513 reads `spike_probe/rtx_settings.json` |

Two constraints follow, and both are deliberate:

1. **Never put a symlink inside a scene folder.** A symlink carries a fresh mtime, so it
   would immediately re-break the latest-round discovery this structure just fixed.
2. **Corpus members are never symlinked** — they are never moved in the first place. The
   corpus commands in `w2_tools_v1.md` §6 must keep resolving to real directories.

Paths that were only *past* evidence were moved without a symlink; `INDEX.md` §6 carries
the full old-path → new-path relocation map.

---

## 2. Naming convention for **new** rounds

```
<yymmdd>_<wave>_<purpose>
```

| field | rule | examples |
|---|---|---|
| `yymmdd` | the date the round was **rendered**, so a plain `ls` sorts chronologically | `260730` |
| `wave` | the work wave that owns it | `w2d`, `w2c`, `t1ab`, `p4`, `spike` |
| `purpose` | what the round is *for*, lowercase, `_`-joined, no version numbers | `judge`, `hoff`, `gate`, `base`, `crop` |

```
look_check/scene13/260730_w2d_judge                        # the W2-D judgement grid  -> scene root
look_check/_experiments/twins/scene13/260730_w2d_hoff      # same build, ground-kit height off (A/B arm)
look_check/_experiments/twins/scene19/260730_t1ab_s2       # t1 material A/B arm
look_check/_experiments/gates/sceneC2/260730_w2d_crop      # zoom crops, not a full grid
```

The judgement grid goes to the scene root; **its arms and crops go straight into
`_experiments/`** — do not render them into the scene root and move them later.

**Twins must differ only in the trailing token** (`..._gon` / `..._goff`,
`..._on` / `..._off`, `..._a` / `..._b`). `scripts/regression_check.py --before/--after`
is fed these two paths directly, so a shared prefix is what makes the pair readable
in a report six weeks later.

**Do not** encode a version number (`v9`, `r6`) — that is what produced the current
mess. The date already orders the rounds, and the purpose already says what changed.

A crop-only round (a handful of zoomed PNGs rather than the full grid) gets the
`_crop` suffix so that `INDEX.md` and the corpus drivers can skip it: it has no
`manifest.json` geometry and cannot be regression-checked. It belongs under
`_experiments/gates/<scene>/`.

---

## 3. Why the old names stay

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

So: **old names are frozen, new names follow §2.** `INDEX.md` maps every surviving old
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
| `t1_mtl_*`, `t1_crop` | 07-29 | W2 t1 material-layer twins — now under `_experiments/{twins,gates}/` |
| `w2_pilot`, `w2c_g2` | 07-29 | W2 judgement grids — **scene root** |
| `w2_pilot_{r1,hoff,crop}`, `w2c_c2_*`, `wininset_*`, `*_crop` | 07-29 | W2 arms / gate probes / crops — `_experiments/{twins,gates}/` |
| `_t0_spike/*`, `spike_*`, `diag_*` | 07-28/29 | throwaway experiment and diagnosis grids — `_experiments/{t0_spike,spike_p1,diag}/` |
| `veg_test`, `planterfix` | 07-28 | one-off prop checks — `_experiments/twins/` |

---

## 4. Standing commands

```bash
cd /home/vislab/Desktop/work_sy/Practice_NegObs

# regression of a new round against each scene's own baseline-of-record
python3 scripts/regression_check.py --scenes 'look_check/scene*' \
  --before-round 260731_w3_gt25,260731_w3_s10c,260731_w3_s07,260731_w3_s04,260731_w3_s16,260731_w3_s18,260730_w3_n2clean,260731_w3_cb1,260731_w3_mb24,260731_w3_cb2,260730_w2d_fix,260730_w2d_judge,w2c_g2,w2_pilot,r2b_on,wall,facade,r2_on \
  --after-round <new round> \
  --fail-only --json Docs/reports/regr_<new round>.json

# single A/B twin
python3 scripts/regression_check.py \
  --before look_check/_experiments/twins/sceneC4/260730_w2d_goff \
  --after  look_check/sceneC4/260730_w2d_judge
```

> **Baseline chain.** The old `--before-round final_pt_r2,final_pt,ctx2_pt,ctx2` is dead:
> `final_pt` / `final_pt_r2` were deleted by the 07-30 cleanup, so it resolved to
> `ctx2_pt,ctx2` for batch1 and **to nothing at all for the 21 main scenes** — i.e. it
> compared against no baseline. Fixed 07-30 in both `regression_check.py`'s docstring and
> `Docs/reports/regression_tool_v1.md` §6/§7. The tail of the chain is `r2_on`
> (`graze_recalibration_v1.md` §9); everything before it is a scene that has since been
> re-judged, **newest first**, so each scene resolves to its own latest judged round.
> **Add a newly judged round to the head, never the tail.**
>
> **Refreshed 2026-07-31 (SB closure batch — `gt_changes_w3.md` §11 SB-4, closing
> `w3_mc_d14_v1.md` §10 D14-B3).** The chain still had `260730_w2d_judge` at its head while
> eight W3 rounds had become baselines-of-record, so every scene that had been re-judged in
> W3 was silently compared against a pre-W3 grid — D14-B3's finding, and the reason every
> re-manufactured GRAZE in that report traced to a stale resolution. **How the order is
> chosen, because `resolve_round` returns the FIRST name in the list that exists as a
> directory containing `*.png` — list order is priority, not date** (`regression_check.py`
> `resolve_round`). Every entry below was verified on disk before it was written here:

| resolves | round | why it sits where it does |
|---|---|---|
| `scene02` | `260731_w3_gt25` | 13 cuts, stamp `baseline_of_record: true`; supersedes `260731_w3_cb7`, whose stamp now says so |
| `scene10` | `260731_w3_s10c` | 14 cuts, `baseline_of_record: true`; supersedes `260731_w3_s10` |
| `scene07` | `260731_w3_s07` | 14 cuts, `baseline_of_record: true` |
| `scene04` | `260731_w3_s04` | 13 cuts, `baseline_of_record: true` (GT-22) |
| `scene16` | `260731_w3_s16` | 13 cuts, `baseline_of_record: true` (GT-23) — **ahead of `mb24` on purpose**: `mb24` is a 5-cut micro round and pixel-null on this scene, so putting it first would drop 8 cuts and gain nothing |
| `scene18` | `260731_w3_s18` | 14 cuts, named by ledger §4 **GT-26**; its stamp carries no marker (the F5 class), so the ledger row is the authority |
| `sceneN2` | `260730_w3_n2clean` | 13 cuts, named by ledger §7 **W8** |
| `scene09` | `260731_w3_cb1` | 17 cuts — **ahead of `mb24` for the same reason as scene16**; `mb24` is pixel-null against it by construction (`w3_mb_patch_v1.md` §8) |
| `scene01` | `260731_w3_mb24` | 5 cuts, but it is scene01's **newest** round and post-dates GT-24's landing; `260731_w3_cb2` is the same 5 cuts and older |
| `scene03` · `sceneC2` | `260731_w3_cb2` | 5 cuts, their newest W3 round |
| the other 22 | `260730_w2d_fix` | the 33-scene W2-D fix batch, present for **all 33** |

> **Two things this chain does not hide.** (1) Everything after `260730_w2d_fix` —
> `260730_w2d_judge`, `w2c_g2`, `w2_pilot`, `r2b_on`, `wall`, `facade`, `r2_on` — is
> **unreachable** while that round survives on all 33 scenes. It is kept as a safety net for
> the day one of those directories is pruned, not because any scene resolves to it today;
> verified by resolution over `look_check/scene*` (33/33 resolve, 0 unresolved).
> (2) `scene17`'s 5-cut micro-pilot rounds `260731_w3_sb17{,_pre}` are **deliberately absent**
> from the chain: scene17's baseline-of-record stays `260730_w2d_fix` (14 cuts), because
> promoting a 5-cut round would drop 9 cuts from every later comparison. Both stamps say so.
> The same reasoning is why `260731_w3_mb24` sits below the full grids rather than at the head.

> **Edge integrity is never read from GRAZE alone** (`ground_kit_spec_v1.md` §7.5 A3).
> A GRAZE firing against a baseline several waves old is unattributable; the instrument
> that attributes it is a **same-session, same-HEAD `NEGOBS_GKIT=0` twin**, rendered into
> `_experiments/twins/<scene>/<round>_goff/`. `w2d_round_v1.md` §3.2 is the worked example:
> 8 GRAZE FAILs against the stale baselines, 2 attributable to the kit once the twin was run.
