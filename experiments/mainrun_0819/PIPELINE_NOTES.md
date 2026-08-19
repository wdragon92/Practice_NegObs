# PIPELINE_NOTES.md — run-book for the 08-19 overnight data render

Repo `/home/vislab/Desktop/work_sy/Practice_NegObs`, branch `feat/realism-v1`, HEAD `8c814db`.
Everything below is read out of the repo; nothing was executed on the GPU.

---

## 1. How to render a data round

### 1.1 Shell preamble (mandatory — copied from `scripts/rounds/run_260817_w4_regfix.sh:15-19`)

```bash
cd /home/vislab/Desktop/work_sy/Practice_NegObs || exit 1
unset PYTHONPATH VIRTUAL_ENV
source ~/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab
export PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1
```

`PYTHONNOUSERSITE=1` is not optional — every round script in `scripts/rounds/` sets it, and the
project memory records it as mandatory for this machine.

### 1.2 Dry run first (CPU only, no GPU, no Isaac boot)

```bash
python3 scripts/run_data_render.py --plan \
    --run 260819_dataall_on --conds L0,L5,L7 --cams 8 --seed 20260819
```

`--plan` returns after printing the plan and budget (`run_data_render.py:137-138`). It prints
every refused `(scene, condition)` pair with its reason, each scene's split/class/`daz_data`,
and the time budget from the measured constants (`variation_kit.py:693-697`:
`T_CUT_DATA 2.87 · T_BOOT 34.3 · T_SWAP 1.4 · R_REJECT 0.020`).

### 1.3 Arguments (`run_data_render.py:536-548`)

| Flag | Default | Notes |
|---|---|---|
| `--run` | `260730_data_mini` | round stamp `<yymmdd>_<wave>_<purpose>`; becomes `dataset/<run>/` |
| `--scenes` | **all 33** (`ALL_SCENES = sorted(vk.AZ_LEDGER)`, `:47`) | comma list |
| `--conds` | `L0` | comma list from `vk.CONDITIONS` |
| `--cams` | `8` | camera samples per (scene, condition) |
| `--seed` | `20260730` | base seed for every derived stream |
| `--plan` | off | print only |
| `--resume` / `--no-resume` | resume **ON** by default (`:546`) | |

### 1.4 Environment the driver sets for you (`run_data_render.py:173-189`)

Per scene subprocess it injects:
`NEGOBS_RENDER_ROLE=data`, `NEGOBS_SEED=<seed>`, `NEGOBS_LIGHT_COND=<conds>`,
`NEGOBS_CAM_MODE=random`, `NEGOBS_CAM_N=<cams>`, `NEGOBS_CAPTURE=1`,
`NEGOBS_CAPTURE_MODE=pt`, `NEGOBS_PT_FAST=1`, `NEGOBS_LOOK_V1=1`, `PYTHONUNBUFFERED=1`.

Do **not** set these yourself: `NEGOBS_RENDER_ROLE` other than `data` trips the role gate
(`variation_kit.py:76-104`), and a judge round carrying variation env is a hard `SystemExit`.
`NEGOBS_DETAIL_SCALE=2` was deliberately **removed** from this list by GT-113 (`:182-185`) — do
not re-add it.

It does `env = dict(os.environ)` first (`:173`), so anything you export in the shell **does**
propagate — that is how `NEGOBS_SCENE_CONFIG` (the hazard-off arm) gets in.

### 1.5 Conditions to pick — **use `L0,L5,L7`, not the pilot's `L0,L2,L7`**

Allowed-scene counts out of 33 (computed from `vk.condition_allowed(..., role=data)`):
`L0 31 · L1 31 · L2 32 · L3 32 · L4 31 · L5 30 · L6 33 · L7 33`.

**The acceptance gate constrains this choice and the 260815 pilot's set does not satisfy it.**
`check_data_run.py:134-153` requires at least one pair of *sun-bearing* conditions whose net EV
(`d_ev − ev_comp`) differs by **≥ 0.3**, else the check fails with "no comparable pair". Net EV
of every sun-bearing condition:

```
L0 0.000 · L1 0.013 · L2 0.047 · L3 0.090 · L4 0.195 · L5 0.352      (L6, L7 are sunless)
```

The **only** qualifying pairs in the whole catalogue are `L0→L5 (0.352)`, `L1→L5 (0.339)`,
`L2→L5 (0.305)`. **L5 is mandatory** if the round is to pass check 1. `L7` (sunless) is what
satisfies the second half of check 1 (a sunless condition must show less deep shadow than L0).
This is exactly the set the validated mini-round used —
`scripts/rounds/run_260730_data_mini.sh:23` "*L0 ref + L7 overcast (sunless) + L5 low_sun*".

With `--conds L0,L5,L7` **5 pairs are refused**, and the driver prints each refusal rather than
substituting (spec B6, `run_data_render.py:73-83`):

```
sceneC1 x L0   season-locked (winter: elev 0-32 deg); L0 is 49.83 deg
sceneC2 x L0   season-locked (autumn: elev 35-45 deg); L0 is 49.83 deg
sceneC2 x L5   season-locked (autumn: elev 35-45 deg); L5 is 19.08 deg
scene15 x L5   L5 needs |Dz| >= 37.0 deg; scene15 allows 20 deg (class A', bounded by criterion C)
sceneN1 x L5   L5 needs |Dz| >= 37.0 deg; sceneN1 allows 0 deg (class S: the label IS the shadow)
```

Legal substitutes: `sceneC1` → `L4, L5, L6, L7`; `sceneC2` → `L2, L3, L6, L7`;
`scene15` → `L0..L4, L6, L7`; `sceneN1` → `L0..L3, L6, L7`. The 260730 mini-round handled its
refusal with a second, explicitly-declared invocation
(`scripts/rounds/run_260730_data_mini.sh:38-40`) — follow that pattern, do not silently swap,
and keep the same `--run` so the substitute cuts land in the same tree.

`L4, L6, L7` are `pt_only`; the data channel always runs `NEGOBS_CAPTURE_MODE=pt`, so that is
satisfied (guard at `run_data_render.py:315-321`).

### 1.6 GPU lock — the driver does NOT take one

`run_data_render.py` has no `flock`. The lock discipline is external. The **scene-unit lock
round script** introduced by `8c814db` is `scripts/rounds/run_260817_w4_regfix.sh` (diff
`+23/-5` on that file); its `render()` function, lines 29-45:

```bash
flock -o -w 3600 -E 201 /tmp/negobs_gpu.lock \
  nice -n 5 env NEGOBS_CAPTURE=1 NEGOBS_CAPTURE_MODE=pt NEGOBS_PT_FAST=1 NEGOBS_LOOK_V1=1 \
    NEGOBS_CAPTURE_DIR="look_check/${key}/${TAG}" \
  python "${scene}" > "/tmp/negobs_${TAG}_${key}.log" 2>&1
rc=$?
if [ "$rc" = "201" ]; then echo "${key}: 락 획득 실패(1시간) — 건너뜀"; SKIPPED="${SKIPPED} ${key}"; return; fi
```

The header (`:8-13`) states the reasoning, which is the operative rule tonight: locking the
**whole round** holds the GPU for 20–30 min, while the user's own work waits only
`flock -w 55` and dies with exit 201 — so **take and release the lock per scene**, `-o`
(no fd inheritance), `-w 3600` (give up after 1 h and skip that scene, recording it),
`nice -n 5`.

That script locks a *judge* render. For the data driver the same shape is:

```bash
for S in scene01 scene02 ... sceneN5; do
  flock -o -w 3600 -E 201 /tmp/negobs_gpu.lock nice -n 5 \
    python3 scripts/run_data_render.py --run "$RUN" --scenes "$S" \
        --conds L0,L5,L7 --cams 8 --seed 20260819 \
    >> "/tmp/negobs_${RUN}.log" 2>&1
  rc=$?; [ "$rc" = 201 ] && echo "skip $S (lock)" && continue
done
```

One driver invocation per scene = one lock acquisition per scene = one Isaac boot per scene,
which is what the driver does anyway (`run_data_render.py:190-195`, one subprocess per scene).
The manifest is merged and re-saved after every scene (`:199-204`), so this loses nothing.

### 1.7 Resume behaviour (two levels, both automatic)

* **Scene/condition level** — `run_data_render.py:165-169`: `done_conds` is read from
  `manifest.json`; a scene whose requested conditions are all done is skipped with
  `[skip] <scene> — all N conditions already done`. `done_conds` is only advanced when the
  subprocess exited 0 (`:202`).
* **Cut level** — `run_data_render.py:432-434`: if the PNG exists on disk *and* the previous
  `variation.json` recorded `ok: true` for that filename, the cut is skipped.
* `--no-resume` re-renders everything for the named scenes.
* Caveat seen in the pilot manifest: a resumed pass records `sec: 0.0` in `invocations`; the
  code explicitly refuses to quote a run-level s/cut for that reason (`:211-215`).

### 1.8 Where output lands

```
dataset/<run>/manifest.json                       run-level: seed, cams, refused, git_head/branch,
                                                  per-scene sec/exit/cuts/done_conds/sec_per_cut,
                                                  invocations[], total_cuts, t_cut_per_scene
dataset/<run>/<split>/<scene>/variation.json      per-scene: gy, conds, split, ledger, per-cut records
dataset/<run>/<split>/<scene>/<cond>__s<seed>__<nnnn>.png   1920x1080 RGB
```

Path from `vk.data_root(run)` (`variation_kit.py:107-115`) + `vk.split_of(scene)`
(`run_data_render.py:171`). Filename pattern is gated by `check_data_run.py:280-283`.
`dataset/` is structurally invisible to `regression_check.py`, which only ever globs
`look_check/scene*` — that separation is the point of spec D1/B2 and is itself checked
(`check_data_run.py:284-298`).

### 1.9 Split assignment — **read this before training**

`variation_kit.py:827-856`. Scene-level only (spec B5: splitting on a variation axis makes the
split itself the shortcut). Deterministic: shuffle `sorted(AZ_LEDGER)` with
`var_seed("__all__","split",0,0)` then slice 70/15/15 → **23 / 5 / 5**.

```
train (23): scene03 scene04 scene07 scene08 scene09 scene11 scene13 scene14 scene15 scene16
            scene17 scene20 scene21 sceneC1 sceneC4 sceneD2 sceneD3 sceneD4
            sceneN1 sceneN2 sceneN3 sceneN4 sceneN5
val   (5):  scene01 scene02 scene19 sceneC2 sceneD1
test  (5):  scene05 scene06 scene10 scene12 scene18
```

**All five hard negatives (N1–N5, GT drop = 0) are in `train`. `val` and `test` contain zero
no-drop scenes.** Any scene-level drop/no-drop evaluation on val/test is degenerate. The
hazard-off arm (§1.11) is the only way to get negatives into val/test tonight, which is another
reason to render it. The split is not parameterised on the CLI — `split_map(base=0)` is called
with the default base everywhere.

### 1.10 Seeds

`variation_kit.py:121-137`: `var_seed(scene, stream, idx, base) = zlib.crc32(f"{scene}|{stream}|{idx}|{base}") & 0x7FFFFFFF`,
streams `cam` / `light` / `expo` / `split`, each with a private `random.Random` so the global
RNG (which scene assembly uses) is never touched. `zlib.crc32`, never `hash()` — the repo was
bitten by `PYTHONHASHSEED` before (`:126-129`).

Operationally: **same `--seed` ⇒ byte-identical camera poses and `d_az` draws.** That is what
makes a paired hazard-on / hazard-off dataset possible: render both arms with the same seed and
cut *i* of scene *s* under condition *c* is the same camera in both.

### 1.11 The hazard-off arm

```bash
export NEGOBS_SCENE_CONFIG='{"hazard_stairs": false}'    # 30 of 33 scenes
python3 scripts/run_data_render.py --run 260819_dataall_off --conds L0,L5,L7 --cams 8 --seed 20260819
```

Three scenes use a different key and need their own invocation:
`sceneN1` → `{"hazard_shadow_band": false}`, `sceneN2` → `{"hazard_asphalt_patch": false}`,
`sceneN5` → `{"hazard_flush_grating": false}` (see `SPEC_EXTRACTED.md` (d)).
`_deep_update` merges, so an unknown key is silently ignored — a single
`'{"hazard_stairs":false}'` across all 33 would produce **3 scenes whose hazard never turned
off**, indistinguishable from the on arm except by hash. Check for it.

**Use a different `--run`.** Output paths and filenames are identical between arms
(`run_data_render.py:171,430`), so a shared run stamp overwrites.

**No hazard-off arm has ever been rendered.** Smoke-test 2–3 scenes first
(`NEGOBS_SMOKE=1 python3 scenes/main/sceneNN_*.py` is boot-free and GPU-free where a scene
implements it) before committing 33 scenes of GPU time.

---

## 2. The two defects named in the `8c814db` queue

Source: `Docs/reports/autonomy_run_extension_260816.md` §G (added by `8c814db`),
detail in `Docs/reports/dn_curve_260816.md` §3.

### 2.1 `spp` wiring defect — **does not corrupt tonight's data render; do not try to fix it**

*What it is.* `NEGOBS_PT_TOTAL_SPP` raises render **time** proportionally but does not reduce
capture noise. Measured (`dn_curve_260816.md` §0/§3): denoiser-OFF arms at spp 64 / 128 / 256
had residual sd **0.0230 / 0.0230 / 0.0228** while wall time went 5.0 → 9.1 → 14.9 s/cut. The
pairwise pixel-difference std ratio was 1.009 : 1 where 1/√spp predicts 1.41 : 1 — three
different noise realisations at the *same* noise level. md5s differ, so these were genuinely
separate renders.

*Where.* `scene_common.py:4937-4943` — `NEGOBS_PT_TOTAL_SPP` → `/rtx/pathtracing/totalSpp`, and
`warmup = max(8, ceil(tot / (spp16 × subframes8)))`, which evaluates to **8 for 64, 128 and 256
alike** (`ceil(256/128) = 2 < 8`). Leading hypothesis in the report (explicitly unconfirmed):
accumulation resets each frame, so the captured frame is always one frame of
`spp 16 × rtSubframes 8 = 128` samples and `totalSpp` only inflates per-frame work.

*Impact on tonight.* **None, and the data channel never touches that knob.**
`run_data_render.py:382-384` hard-codes `sc.PT_FAST` (`scene_common.py:183`
`PT_FAST = dict(spp=16, total_spp=64, subframes=8, warmup=8)`) and warms up
`sc.PT_FAST["warmup"]` = 8 updates (`:439-440`). It does not read `NEGOBS_PT_TOTAL_SPP` at all.
So every cut in the dataset gets the same effective sample count and the noise level is
**constant across the corpus** — which is what matters for training. The defect only means you
cannot *buy* less noise by raising spp.

*Consequence to accept, not fix.* The judge round raises dark scenes to
`NEGOBS_PT_TOTAL_SPP=256` (`run_p2_all33.sh:11-13`: `sceneD4` required, `scene02`/`scene13`
recommended). **The data channel has no equivalent path**, and per the defect it would not help
anyway. Expect `sceneD4`, `scene02`, `scene13` to be the noisiest/darkest cuts in the set and
the most likely to trip acceptance check 1 (§5). Minimal safe workaround if they do fail: raise
`sc.PT_FAST["warmup"]` for those scenes via a wrapper, or simply exclude and re-render them
later — **do not attempt to fix the totalSpp wiring on a render night**, it needs a runtime
probe of the accumulation counter that the report itself scoped out.

### 2.2 `round_stamp.json` env hole — **cheap to close, close it**

*What it is.* `scripts/stamp_round.py` writes `"env": {}, "env_captured": false` when it is run
in a different shell from the render (`stamp_round.py:18-22`). The three denoiser arms have no
record of which spp they used; the only evidence is the round *name*
(`dn_curve_260816.md` §3 footnote). Named in the `8c814db` queue as item 2, "X2 구멍".

*Fix, already implemented in the tool.* `stamp_round.py:39-40`:

```bash
# INSIDE the render shell, before/at render time:
python3 scripts/stamp_round.py --capture-env dataset/260819_dataall_on
#   -> writes .negobs_env.json (ENV_SIDECAR, stamp_round.py:60) beside the frames
# afterwards, from anywhere:
python3 scripts/stamp_round.py dataset/260819_dataall_on 260819_dataall_on dataall
#   -> _resolve_env (:129-143) precedence: --env-file > render-shell sidecar > stamping shell
```

*Impact on tonight.* Low, because the data channel already records the render arm **per cut**
inside `variation.json` (`run_data_render.py:469-470`: `render=dict(mode="pt",
total_spp=64, warmup=8)`) and the run-level `manifest.json` carries `git_head`, `git_branch`,
`seed`, `cams` (`:155-156`). The hole matters for the *look* env (`NEGOBS_LOOK_V1`,
`NEGOBS_PHYS_V1`, `NEGOBS_MICRO_V1`, `NEGOBS_SCENE_CONFIG`) — and `NEGOBS_SCENE_CONFIG` is
exactly what distinguishes the on and off arms tonight. **Run `--capture-env` inside the render
shell for each arm**; it costs one command and is the only machine-readable proof of which arm
a directory is.

---

## 3. Throughput

### 3.1 Measured, from this repo's own artefacts

| Source | Scope | Wall | Derived |
|---|---|---|---|
| `look_check/logs/sp2_azsweep_times.tsv` (33 rows, 21 cuts each) | **33 scenes × 21 cuts = 693 cuts** | **2651 s = 44.2 min** | 3.83 s/cut incl. boot; per scene **60.4 s (scene04) … 98.2 s (scene16)**, median **81.4 s** |
| `dataset/260815_datapilot/manifest.json` | 5 scenes × 3 conds × 8 cams = 120 cuts | 437.1 s = 7.3 min | per-scene s/cut incl. boot **2.811 / 6.273 / 2.94 / 2.89 / 3.30** |
| the same run's `variation.json` files (in-process only) | 24 cuts/scene | — | in-process s/cut **2.027 (s04) · 4.951 (s16) · 2.246 (N1) · 2.265 (N2) · 2.288 (N3)** |
| `variation_kit.py:693-697` (constants of record) | — | — | `T_CUT_DATA 2.87 · T_BOOT 34.3 · T_SWAP 1.4 · R_REJECT 0.020` |
| `autonomy_run_260814_18_handover_v1.md:99` (judge round `260816_w4_final33_on`) | 33 scenes, 132 cuts | per scene **36–228 s** | scene assembly, not per-cut, dominates the tail |

Boot + scene assembly, isolated from the pilot (manifest wall − variation.json wall):
**scene04 18.8 s · scene16 31.7 s · N1 16.7 s · N2 15.0 s · N3 24.3 s**. The judge round's 228 s
worst case shows the heavy end is assembly, so it is paid **once per scene per arm** — which is
exactly why the driver nests conditions *inside* one boot (`run_data_render.py:9-14`: SP-2
measured **3.29×** end-to-end saving, 44.2 min in-process vs 145.2 min as 7 separate rounds).
`t_swap` for the runtime HDRI change is **1.4 s** and is paid `n_conds − 1` times per scene.

### 3.2 Estimate for tonight

Target arm = 33 scenes × 3 conditions × 8 cameras = **792 cuts**.

```
per-cut render   792 × ~3.2 s (pilot mean, in-process)      ≈ 42 min
boot + assembly  33 × ~60 s (median-to-heavy, 15–230 s)     ≈ 33 min
HDRI swaps       33 × 2 × 1.4 s                             ≈  1.5 min
------------------------------------------------------------------
one arm                                                     ≈ 75 min   (range 55–110 min)
two arms (hazard on + hazard off), 1584 cuts                ≈ 2.5 h    (range 2–3.5 h)
```

Anchor check: SP-2 did 33 scenes × 21 cuts in **44.2 min** with the same nesting; scaling the
per-cut half from 21→24 cuts gives ≈ 50 min, so 75 min per arm is a comfortable margin, not an
optimistic figure.

Sensitivity: **+8 cameras per condition adds ≈ 8 × 3 × 3.2 s = 77 s per scene ≈ +14 min per
arm** — the cheap axis. **+1 condition adds ≈ 8 × 3.2 s + 1.4 s ≈ 27 s per scene ≈ +15 min per
arm.** Adding scenes is the expensive axis because it buys another boot+assembly.

Per-scene lock contention: with per-scene `flock` the wall clock grows by whatever the user's
own GPU work takes between scenes; `-w 3600` then `skip` bounds the worst case.

If depth capture is added (`SPEC_EXTRACTED.md` (e)), re-measure on one scene first — the design
record warns of up to a 40× throughput collapse with a full annotator set
(`Docs/surveys/realism_gap_2026-07-28/ZZ_synthesis.md` §10.3).

---

## 4. Scene-level caveats for a dataset render

Sourced from `Docs/reports/autonomy_run_extension_260816.md` §F/§G (the `8c814db` queue) and
`autonomy_run_260814_18_handover_v1.md` §5/§7.

| Scene | Issue | Severity for a **training set** | Recommendation |
|---|---|---|---|
| **scene08** | 3 confirmed-but-revised defects: mise-en-scène plane below horizon (needs vertical closure); a −X CBD backdrop block visibly windowless-vs-context (`backdrop` kit contract, ledger row required before any change); **arena bench row interpenetrating 1.13 m each, 5 benches on a 2.37 m arc** (`arena_benches=dict(r=3.40,a0=96,a1=136,n=5)`, `scene08:441`) | **medium** — visible artefact in mid-ground, hazard geometry untouched | **include**; the bench overlap is a mid-ground prop artefact, not on the drop edge |
| **scene09** | 1 confirmed-revised: `Cockpit` box protrudes **154 mm** through the duck-boat hull (corner case the PARAMS derivation missed) | **low** | include |
| **scene04** | user-ordered **hold** — no edits allowed (GT-129 withdrew it, `992edaf`). The extension report additionally suspects **the audit finding itself is wrong** (`build_blot` is a zero-thickness section mesh; likely a rope-handline shadow) | **low visual, high policy** | include; **change nothing in the file** |
| **scene15** | window count 2→1 on the narrow 4th block — **user decision pending** (`autonomy_run_extension_260816.md` §G item 7). Repaired and render-verified under GT-129 (`027f9ff`: cascade vanishing resolved) | low | include |
| **scene17** | fresh-audit **confirmed-high**: water surface over-scaled (`§G` item 5) | **medium** — s17 is a water-anchored drop scene, a wrong water read is a cue-level defect | include, flag |
| **scene21** | fresh-audit **confirmed-high**: decal fragments | medium | include, flag |
| **sceneN4** | fresh-audit **confirmed-high**: green wash | **medium — and it is a hard negative**, so a systematic colour cast on a no-drop scene is a textbook shortcut | include, flag; check with `shortcut_audit` |
| **scene03** | GT-129 remainder: FarBank saw-tooth, amplitude **7.58 m** — needs separate approval (bank silhouette change) | medium | include, flag |
| **scene05** | GT-129 remainder: podium decagonal silhouette — needs separate approval (would move the walked surface z) | medium | include, flag |
| **sceneD3** | 육안 remainder: shoulder grazing reads as corrugation | low | include |
| **scene07** | 육안 remainder: distant dark face retains green | low | include |
| **scene14** | 육안 remainder: facade blows to pure white (building queue) | low–medium | include |
| s05 s10 s06 s15 s03 | **repaired and render-verified** 08-17 under GT-129 (`027f9ff`: s05 four pure-black regions 0.00 %, s10 sky-through 4319→0 px, s06 single tapered pier, s03 straight water edge, s15 cascade resolved) | — | these are the *good* news; the current HEAD is the repaired state |

Corpus-level caveats that matter more than any single scene:

* **Guard-rail shortcut.** `dropoff_cue_matrix_v1.md:14-16` — `railing_or_guard` is the least
  occluded cue in the corpus (9.9 %) while the cues that actually describe the drop die much
  faster (`edge_line_contrast` 30.9 %, `texture_change_across_edge` 34.2 %,
  `nosing_strip` 73.0 %). `lighting_camera_variation_spec_v1.md:742` records
  **P(drop | railing) = 0.944**. The hazard-off arm is the declared remedy.
* **Scene identity → label.** `lighting_camera_variation_spec_v1.md:735-739` (D9): the drop
  label is constant per scene, so image → scene-id → label is open and camera/lighting variation
  does not close it. With split-by-scene this is partly mitigated for val/test, but see §1.9.
* **`h0.3_d10` kills the corpus.** 165 of 574 occlusion events (28.7 %) sit on that one preset;
  8 scenes have zero surviving cues there. The random sampler covers `d` up to 12 m and `h` down
  to 0.25 m, so this region *will* be sampled.
* **8-bit RGB only.** No depth, no semantics, no GT map exists (`SPEC_EXTRACTED.md` (e)(f)(h)).

---

## 5. Acceptance gate and the pilot chain

### 5.1 `scripts/check_data_run.py <run>` — five checks, run it after every arm

```bash
python3 scripts/check_data_run.py 260819_dataall_on      # GPU 0
```
Exit 0 = `DATA RUN CHECK PASS`, exit 1 lists the failing tags (`:318-322`).

1. **Exposure sanity** (`:76-172`)
   * every cut carries an `img` measurement;
   * `30 ≤ mean ≤ 235`, `dark ≤ 70 %`, `clip ≤ 1 %` — **per cut, so one bad cut fails the
     round**, and the driver never re-samples a rejected cut;
   * among sun-bearing conditions, the **ground band** darkens with net EV, asserted per scene
     — needs ≥ 1 pair of conditions ≥ 0.3 net EV apart, and **only `L5` paired with `L0`/`L1`/`L2`
     qualifies** (see §1.5). Without `L5` this check fails with "no comparable pair";
   * a sunless condition must show **less** deep shadow than its L0 reference (proof the sky
     swap took effect). `L7` supplies this.
2. **Azimuth ledger** (`:174-203`) — every `|d_az|` inside the SP-2 measured allowance and above
   the D6 astronomical floor; each condition carries its own `hdri_sun_rotz_offset`;
   `sun_elev` matches the sky's measured elevation (no double shadow).
3. **Camera placement** (`:205-248`) — ground found under every camera;
   `|ground_below − h_rel| < 0.02` (proof the CAM-3 ground-relative fix landed);
   nothing buried; `nearest_solid ≥ 0.15`; tier recorded; and the sampler truncations re-asserted
   (`h_rel ∈ [0.25,1.90] · pitch ∈ [−20,−2] · roll ∈ [−5,5] · hfov ∈ [58,66] · d ∈ [1.2,12]`);
   `focalLength` consistent with `hFOV`.
4. **File / manifest integrity** (`:250-298`) — 1:1 manifest↔disk; **no orphan PNG in the scene
   directories** (any sidecar you add must not be a `.png`); every cut content-unique by md5
   (catches a stale or duplicated frame); all captures `ok`; every frame exactly 1920×1080;
   filename pattern `<cond>__s<seed>__<nnnn>.png`; nothing written under `look_check/`; the data
   tree outside `regression_check`'s only glob.
5. **Throughput** (`:300-316`) — per-scene s/cut printed and gated at `< 2 × T_CUT_DATA`
   i.e. **< 5.74 s/cut**. Note `scene16` measured **6.273 s/cut in the 260815 pilot**, which
   would fail this gate; expect it, and read it as an advisory rather than a stop.

`260731_s08_recache` is the reference of a clean pass (`Docs/audit_v4/gt_changes_w3.md:182`):
24 cuts / 3 conditions / 8 cameras, worst `|err|` 0.0000 m, nearest solid 0.505 m, 2.73 s/cut.

### 5.2 The rest of the datapilot chain

* **`scripts/shortcut_audit.py`** — the corpus shortcut instrument, GPU 0, no model.
  `:45 NO_DROP = {"sceneN1".."sceneN5"}` (scene identity, not an invented number). Three
  measurements: (1) point-biserial correlation between drop-presence and the ground-band dark
  fraction; (2) per-scene tone clip rates; (3) **horizon-row distribution from the data run** —
  reconstructed analytically from `variation.json` cam records as
  `row = H/2 − f_px·tan(pitch)`, `f_px = (H/2)/tan(vFOV/2)`; a collapsed distribution opens the
  vertical-position shortcut (van Dijk, ICCV'19).
  ```bash
  python3 scripts/shortcut_audit.py --data dataset/260819_dataall_on --json out.json   # (3)
  python3 scripts/shortcut_audit.py --round 260816_w4_final33_on                       # (1)(2)
  ```
  Current corpus state (handover §3): `r_pb dark 0.098 · deep 0.089`, drop-group dark median
  0.012 vs no-drop 0.047 (**inverted** — the "deeper = darker" signal is structurally
  dismantled). Re-measure after the render: the 260815 data-roll figure was disowned as
  scene-identity-confounded on a 5-scene sample (`handover §3`, last bullet:
  *"정측정은 전 씬 렌더 필요"*) — **tonight's full render is exactly that measurement.**
* **`scripts/sensor_augment.py`** — post-hoc sensor-effect augmentation (chromatic aberration,
  blur, exposure, shot/read noise, colour temperature), zero re-render.
  `:16 "학습(data 롤) 전용. 판정(judge) 라운드에 절대 적용하지 않는다 — regr 오염."`
  Deterministic from filename + seed. Basis: Carlson et al. ECCV-W 2018 (+7.28 AP from sensor
  effects alone; geometric augmentation measured **−3.14**, i.e. harmful). Measured noise floor
  gap: render 1.04/255 vs real 2.96/255 (~3×).
  ```bash
  python3 scripts/sensor_augment.py --in dataset/260819_dataall_on/train \
                                    --out dataset/260819_dataall_on_aug/train
  ```
  `dataset/260815_datapilot_aug/` is the existing example of the output shape.
* **`scripts/stamp_round.py`** — see §2.2. Run `--capture-env` inside the render shell, then
  stamp each arm.
* **Do not run `scripts/regression_check.py` on the dataset.** It is a judge-channel tool and is
  only ever pointed at `look_check/scene*`; check 4 of `check_data_run.py` exists to prove the
  two trees never meet.
