# MATERIALS_INDEX — v3-frame paper materials (`experiments/v3_0823/paper/`)

- **Created**: Claude Code (CPU-6) · 2026-08-23 · **Track**: MAIN paper (v3 frame).
- **Not this track**: the 8/30 backup submission package (`submission_0830/`, assembled by Claude AI
  from the v2 package, D58 ⑥ / `DZ §10 :363-364`). **These two tracks do not share files.** Nothing in
  this directory is written to, read by, or synchronised with the backup package.

---

## 1. Index

| # | File | One line |
|---|---|---|
| 1 | `intro_4layer_skeleton.md` | Introduction skeleton on the 4-layer framework — signal geometry (h·w/d², "risk size ∦ signal size", H tier), the human-fence inference, the two July findings (statutory cues ⇒ hazard→cue causality licenses the inverse inference; accidents concentrate where cues fail ⇒ layer ④ necessity), a full Figure-1 caption + drawing spec, and the related-work positioning paragraph (thermal pivot, no negative-obstacle class in major off-road datasets, our position). |
| 2 | `version_journey_skeleton.md` | The honest version journey as a contribution — v1 → v2 headline → three-instrument demolition (twin-conditional / CUE-OFF / Gazebo, plus the D65 unit-flip) → diagnosis A/B/C → v3 prescription (2×2 orthogonalisation, cue-conditional supervision, selection repair) → pre-registration and the three dashboards; every demolition number carries its ledger path, and §7 is the 15-row scoped-claim language checklist. |
| 3 | `nearfield_limitation_paragraph.md` | The unified near-field limitation paragraph — band-1 blindness, 3a non-response and near-field-E geometric non-existence share one root (a forward-fixed-pose observation regulation, not a property of the hazard), with the far-field 1/d² vanishing named as the real problem and video propagation as the declared roadmap; one ~250-word paragraph plus 1/2/3-sentence variants. |
| 4 | `ab_table_shells.md` | Six A/B table shells with **every number blank** — ① twin-conditional (A,C) with dual-axis FA-matched companion, ② CUE-OFF dose–response, ③ N-cue FA with FA_C/FA_D decomposition and the difficulty-ladder stratification, ④ headline test-core (corrected GT, v2 \| v3 sides), ⑤ FA-matched dual axis, ⑥ ECE / calibration / selective firing — each with caption draft, ACCOUNTING denominator source, and the pre-registered verdict rule (direction + σ ddof = 1). |
| 5 | `MATERIALS_INDEX.md` | This file. |

---

## 2. 이원화 방지 (anti-bifurcation) — read this before writing any paper prose

**Ruling being applied**: D58 ⑥ — *"산문은 Claude AI 기본, 문장 조각은 색인 표시로 이원화 방지."*
(Prose is Claude AI's by default; sentence fragments are marked in an index so that two divergent
versions of the same text never come into existence.)

**What that means operationally for this directory:**

1. **These files are materials, not drafts.** They are structure, sources, constraints and blank
   shells. **Claude AI + 승용 own the finished sentences.** If a paragraph here reads as finished
   prose, it is still a proposal.
2. **Where a finished-sounding English sentence appears, it is explicitly marked** as
   `Draft line (EN: …)` / `Draft line` / a blockquote inside a `> ` block. Those are the *only*
   fragments intended for possible lift-and-edit. Everything else is scaffolding and should be
   rewritten, not copied.
3. **Single-source rule.** Once Claude AI writes the real §Introduction, this directory's
   `intro_4layer_skeleton.md` becomes **historical** — do not edit both. The convention is
   append-only banners, matching the repo's canon rule (`PS v2 §5 :88`): if a file here is superseded,
   append a one-line banner at the top saying which file replaced it. Do **not** silently keep two
   live versions.
4. **Numbers flow one way only: ledger → materials → paper.** No number may be introduced in this
   directory that does not exist in a ledger, and no number may be edited here to match a draft.
   Denominators are `ACCOUNTING.md`, single reference (`ACC §3.4 :328-329`).
5. **Do not fill the table shells here.** When results land they go into the results ledger first,
   and the paper table is generated from that. A number typed into `ab_table_shells.md` would become
   an unsourced second origin — exactly the bifurcation this rule exists to prevent.

---

## 3. Open items these materials are waiting on

| # | Blocked item | Where it is tracked |
|---|---|---|
| 1 | **k** — the cue-presence pixel threshold, must be gate-fixed and hashed **before** cue-conditional supervision begins | `ACC §2-5 :217`, `ACC §3.4` item 1 |
| 2 | test-ext scene list / frame counts / 4-arm decomposition; paired-H per scene; FA_C·FA_D denominators | `ACC §3.4` items 2–4 |
| 3 | `none_in_fov`-equivalent tier handling in v3 (residual 39 frames are in no published denominator; `labeler.py:526` post-gate attribution unresolved) | `ACC §3.4` item 8, `ACC §4.7 :461-464` |
| 4 | **DZ §0.1 correction** — "the aux amodal head is trained" is false for all 9 main-table runs (measured aux OFF). Correction is Claude AI/승용's to make; until then no paper sentence may describe the main-table models as carrying a trained aux head | `ACC §4.9-4 :497-501` |
| 5 | cells-per-FA-frame estimator (seed-pooled 4.29 vs seed-averaged 5.50 for Depth) — one must be made canonical | `E12 §3 :96-99`, `E12 §6-3 :156-157` |
| 6 | **Matthies & Rankin 2003 verbatim quote** — the ledger carries only the fragment *"great potential for false alarms"*; the "intensity cues pre-emptively dismissed → thermal pivot" formulation is a paraphrase (D54 ⑤), not a quotation in the repo. Requires one pass over the S1 PDF before any quotation mark is printed | `intro_4layer_skeleton.md §6` Move 2 warning; `FA_REALITY.md §5.1 S1 :234` |
| 7 | N-cue ladder: how many of the 12 rungs enter test-ext, in what ratio and pairing | `FA_REALITY.md §6 :313` |
| 8 | Selective-firing coverage grid {100, 75, 50, 25} % — provisional, must be pre-registered | `ab_table_shells.md §6.4` |
| 9 | Figure-1 density: whether the layer→instrument mapping rides in Fig. 1 or becomes Fig. 2 | `intro_4layer_skeleton.md §5.2` |
| 10 | **P-4 unit of "성적"** — the reproduction check PASSes at model-average and FAILs for run `rgb_s42` (2.63σ); `ACC §2-7` never fixed whether the pass criterion is per-model or per-run. Both verdicts recorded, escalated for ruling | `experiments/v3_0823/P4_SELECTION.md` (landed concurrently with these materials) |
| 11 | **P-4 selection formula approval** — `S = (1−β)·val_F1 + β·Ĥ − 1.0·val_FPR`, β = n_H/(n_H+30), plus gate VG-1; explicitly **not self-adopted** | same |

---

## 4. Source ledgers these materials draw on (read-only; nothing here was modified)

| Alias | Path |
|---|---|
| DZ | `Docs/campaign/V3_DESIGN_0823.md` |
| PS v2 | `Docs/archive/campaign_status/PROJECT_STATE_0823_v2.md` |
| ACC | `experiments/v3_0823/ACCOUNTING.md` |
| FAR | `experiments/v3_0823/FA_REALITY.md` |
| FAC | `experiments/v3_0823/FA_CENSUS.md` |
| E12 | `experiments/v3_0823/redteam/EVL12_CELL_AXIS.md` |
| RS | `experiments/v3_0823/V2_RESCORE.md` |
| CC | `experiments/v3_0823/CUE_COVERAGE.md` |
| — | `experiments/v3_0823/G7_RELABEL.md`, `TWIN_TOL_RESOLUTION.md`, `ASSUMPTION_LEDGER.md`, `RENDER_PLAN_V3.md`, `redteam/RT_LEDGER_{A,B}.md` |
| DEC | `experiments/mainrun_0819/DECISIONS.md` (D52–D65 tail) |
| ST | `experiments/dayrun_0820/runs/v2/SEED_TABLE.md` |
| F1 / F2 | `experiments/weekend_0823/rt_response/F1_FA_MATCHED.md` · `F2_TWIN_CONDITIONAL.md` |
| CO | `experiments/weekend_0823/cue_audit/CUEOFF_RESULT_v2.md` |
| GZ | `experiments/weekend_0823/gazebo/GAZEBO_TRACK.md` |
| MR23 | `experiments/weekend_0823/MORNING_REPORT_0823.md` |

**No file outside `experiments/v3_0823/paper/` was created or modified by CPU-6.**
