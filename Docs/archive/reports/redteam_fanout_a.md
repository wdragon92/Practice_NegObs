# Red-team — FANOUT A exit verification (SB · T4b · S01 · S03 · S06 · S08 · S09 · S11 · S13 · S17 · cross-lane)

- **Verifier**: independent red-team lane, this session. **Method: re-run, not re-read** — every
  number quoted below as `[re-run]` was regenerated on this machine from the committed tree or the
  stored round artefacts, not copied from the lane reports.
- **HEAD verified**: `ede174a` on `feat/realism-v1`, worktree clean at audit start.
  (The fanout brief said "~`8bf7882`"; **54 commits** landed on top of it — `git rev-list`
  cross-checked against the ten lanes' commit lists: **all 54 accounted, no foreign commit**.)
- **Isolated arm**: `git archive ede174a` into scratch, with the **gitignored asset payloads
  symlinked in** (`assets/*.jpg|exr`, `assets/scene01/*`, `assets/coastal/*`, `vegetation`,
  `urban`, `urban_cc0`) — see finding **RT-A7** for why a bare archive arm is not sufficient.
- **GPU work**: T4b probe re-run (both arms) and the scene03/scene09 SMOKE boots, all inside
  `flock -w 7200 /tmp/negobs_gpu.lock`, PT_FAST channel, frames in scratch only. No `look_check/`
  round was created; no repo file outside this report was touched.

## 0. Verdict table

| target | verdict | one line |
|---|---|---|
| SB closure batch | **CONFIRMED** | all six items re-verified against ledger + code + disk; SB-F1 gate gap is real |
| T4b | **CONFIRMED** | full GPU re-run reproduces every headline number to the decimal |
| S01 | **CONFIRMED** | ownership clean · declare<land · 431/`a9d6c2ba` reproduced · FAIL 2 all-FRAME re-parsed · stamp marker present |
| S03 | **CONFIRMED** (notes) | content of the message-swapped declaration verified; stamp key semantics differ from other lanes (RT-A4) |
| S06 | **PARTIAL** | split proof + invariance + identity all re-verified, but the claimed baseline-of-record **stamp carries no marker** (RT-A1) |
| S08 | **CONFIRMED** (note) | bowl/tiers/guard verified in crops + code gate; adjudication evidence lives in report text, no regr JSON committed |
| S09 | **CONFIRMED** (notes) | fixture edit inside frozen `ground_kit.py` — declared & scoped, letter-violation noted (RT-A5); honest crops |
| S11 | **CONFIRMED** | H-plan vs G11 verified · 14 FAIL re-parsed (FRAME + 1 adjudicated OCCL) · stamp marker present |
| S13 | **CONFIRMED** | canopy→gantry verified in crops · FRAME 14/14 re-parsed · GT-5/GT-33 LANDED · ginkgo substitution honestly documented |
| S17 | **CONFIRMED** | pair-in-one-frame + 25.6 m ramp verified · PASS 13/INFO 1 ×2 arms re-parsed · 968/`186a4907` reproduced |
| cross-lane floor | **CONFIRMED** (notes) | geom_invariance 33/33 R-4+R-6 PASS at final HEAD `[re-run]` · lint ERRORs all pre-date this fanout · no humans/vehicles · no Rhododendron misread |

**Fanout exit: PASS**, with supervisor actions listed in §4 (none blocks the exit; RT-A1/RT-A2
should land before the next regression round is judged).

## 1. Batch lanes

### 1.1 SB closure batch — CONFIRMED

- **GT-24 scope 15→11** `[re-run]`: ledger row carries the amendment with the per-scene
  reachability census (8+0+3, scene08/09/16/18/C2 excluded as scene-side authors); §11/§11-1
  explain the levee extension as amendment-not-GT-27. `ground_kit.py:1972` (`levee_paved`):
  `("patch", 4)` **gone** from `surface=`, comment carries the reach measurement.
- **GT-25** `[re-run]`: row amended to `(-11.0, -5.0)` with the hedge-intersection measurement;
  hedge NOT notched; §4 record filled; §3 flipped in the same commit (`0825f48`).
- **README §4 chain** `[re-run]`: resolution re-executed over `look_check/scene*` with the
  chain as committed — **33/33 scene dirs resolve, 0 unresolved** (a 34th glob hit is the stray
  `scene19_r5.log`, not a scene). Chain staleness vs the 8 new baselines → RT-A2.
- **`assets/assets`** `[re-run]`: absent (`ls` fails; `find` returns only `./assets`,
  `scenes/{main,batch1}/assets`). Consistent with SB's "reported absent, not deleted".
- **SB-3** `[re-run]`: `260731_w3_cb7/round_stamp.json` reads `baseline_of_record: false`,
  `superseded_by: 260731_w3_gt25`, with the MD-F5 closure note.
- **SB-F1 re-verified adversarially**: `ground_kit.py:3830` `_gt24 = ("plaza_granite",
  "plaza_water", "sidewalk_block")` — `levee_paved` is indeed NOT gated; a regression restoring
  its patch row would pass the self-check. SB's own blocker stands as written.
- **scene17 tuple arithmetic** `[re-run]`: HEAD arm gives scene17 **968 prims / `186a4907`** —
  SB's 974→970 (−4 `Patch_*`) followed by S17's −2 (manhole derivation) chains exactly.
- Commit footprints (`git show --stat` on `5e87681 f39abe0 8f402fa 0825f48 6ae7766`): ledger,
  `ground_kit.py`, own report/crops, `look_check/README.md`, `w3_mb_patch_v1.md` tail — nothing else.

### 1.2 T4b — CONFIRMED (GPU re-run)

Re-ran the lane's own probe (`t4b_probe.py`, recovered from the shared scratchpad) **verbatim,
both arms, fresh output dirs**, under the GPU lock, `env_isaaclab` python:

| metric | report | re-run |
|---|---|---|
| raw `cannot find SdrNode: ND_normalmap_float` | 4 | **4** (`rock_moss_set_01`, `tree_stump_01`, `tree_stump_02` prototypes) |
| wrap SdrNode errors | 0 | **0** |
| IsInstance | 10/10 both arms | **10/10 both arms** |
| stage prototypes raw→wrap | 4 → 5 | **4 → 5** |
| red-fallback `wrap_d3` raw→wrap | 9.02 % → 0.00 % | **9.018 % → 0.000 %** |
| red-fallback `wrap_h0.3` | 11.09 % → 0.00 % | **11.087 % → 0.000 %** |
| red-fallback `rocks_close` | 18.53 % → 0.00 % | **18.530 % → 0.000 %** |

The stored 21:54 frames and my re-rendered frames agree to ≤0.45 LSB mean (PT sampling noise);
the raw arm reproduces to 3 decimal places. Footprint of `9903399`: `urban_kit.py`, 7 wrapper
USDA files, own report/crops — no scene, no other kit. Wrapper layer count on disk = 7, as reported.

## 2. Scene lanes — common re-runs

- **Declare-before-land** `[re-run, git timestamps]`: every geometry commit is preceded by its
  ledger declaration — S17 `884d24c`(22:34:51)→`25f366c`(22:35:14) · S06 `af49ef9`(22:35:23)→
  `94dc38d`(22:37:04) · S03 `367665f`(22:35:31 author)→`e4862aa`(22:52:15) · S01 `e87b188`
  (22:37:05)→`ac7a50c`(22:37:51) · S13 `e8f2053`(22:36:50)→`1234a51`(22:37:34) · S09 `013fe8a`
  (22:45:11)→`44ad574`(22:45:43) · S11 `bf79549`(22:49:00)→`f05efb5`(22:49:21) · S08 `1edd838`
  (23:01:10)→`0af6f24`(23:01:55). No inversion anywhere.
- **Ledger §3/§4** `[re-run]`: GT-24/25/27–40 + GT-5 + GT-10 all `LANDED`, each with a §4
  landing-record row; rider rows (28/30/32/33/38/39/40) correctly reference their carrier's
  re-cache instead of duplicating commands. No interleaved half-write found in any ledger diff.
- **Ownership audits** `[re-run, `git show --stat` on all 54 lane commits]`: every scene lane
  touched only its own scene file + ledger + own report/crops/regr + own round dirs. Three
  boundary cases, all declared by the lanes themselves: S09's `ground_kit.py` fixture row
  (RT-A5), S01's `scripts/rounds/crops_260731_w3_s01.py` (RT-A6), and S06's amend incident
  (§2.3 below).
- **Stored-round re-adjudication** `[re-run, parsed the regr JSONs]`:

| lane | stored verdicts | FAIL issue codes (re-parsed) | matches report? |
|---|---|---|---|
| S01 `regr_260731_w3_s01` | FAIL 2 · WARN 3 · INFO 8 | FRAME 2 | yes ("all FRAME, declared") |
| S03 `regr_260731_w3_s03` | FAIL 14 · WARN 2 | FRAME 14 + GRAZE 1 (`h0.3_d2`) | yes — GRAZE adjudicated non-defect in report §4.2 |
| S06 `regr_260731_w3_s06` | FAIL 8 · PASS 2 · WARN 5 | FRAME 8 + PHOTO 1 + OCCL 2 (blobs 2.2 / 3.7 %) | yes — OCCL "camera swallowed" rejected per cut |
| S09 round-local regr | FAIL 10 · PASS 4 · INFO 3 · WARN 1 | FRAME 10 + WHITE 1 + GRAZE 1 | yes — WHITE carried as declared §4 violation, GRAZE negative by crop |
| S11 `regr_260731_w3_s11` | FAIL 14 · INFO 1 | FRAME 14 + OCCL 1 (`sidewalk_approach`) | yes — OCCL attributed to brick backdrop in §, kept |
| S13 `regr_260730_w3_s13` | FAIL 14 · PASS 1 | FRAME 14 | yes |
| S17 `regr_attrib` + `regr_vs_w2d_fix` | PASS 13 · INFO 1, both arms | none | yes ("FAIL 0 · WARN 0") |

  No DARK/BLOWN FAIL exists in any stored round. EXPECTED_FP citations in the lane reports all
  trace to the `ground_kit` register (layer-1 table, D14 reader) — none invented.
- **Stamps** `[re-run]`: `baseline_of_record: true` present on `260731_w3_s01`, `…_s08d`,
  `…_s09`, `…_s11`, `260730_w3_s13b`, `260731_w3_s17`. **Absent on `260731_w3_s06`** (RT-A1);
  `260731_w3_s03` uses the key with a different meaning (RT-A4).
- **Gate re-runs at final HEAD** `[re-run, isolated arm]`: scene01 (`SMOKE rows=20`), scene06,
  scene08, scene11, scene13, scene17 — rc 0 under plain `python3`; scene03 via its
  `NEGOBS_SELFCHECK=1` gate (사행 OK · 강폭 OK, rc 0, CPU); scene09 `NEGOBS_SMOKE=1` under
  `env_isaaclab` headless (rc 0, season audit 위반 0). See RT-A3 for the two deviations.
- **Crops vs targets** `[viewed, every scene]`: 03 patch-rectangles gone, honest near-white
  gravel, ruling-vs-G3 gap escalated not hidden · 01 flanks opened to kerbed lawn + backdrop,
  autumn litter · 06 bronze 4-rail + scalloped fascia + glass approach span, identity split from
  11 legible · 08 rectangular pit → circular bowl with cascade/tiers/ring-deck and rim guard,
  no ground rectangles, MD-F7 eye gate live in code (`scene08:938-972`) · 09 deck-slab unmasking
  visible, far-bank ridge blobs honestly crude (procurement blocker declared) · 11 towers
  parallel to carriageway, switchback east tower, mesh + 100 mm balusters · 13 canopy deleted,
  gantry + height bar + yellow centre line + cheek blocks, ash-for-ginkgo documented in-code
  (`scene13:439`) · 17 pair in one frame, ramp visibly 25.6 m / 12.5 %, cameras frozen between arms.

### 2.3 S06 — why PARTIAL, and what was confirmed

**Confirmed by re-run**: the GT-6 split proof was re-executed from the stored instrument
(`gt_diff.py` + sample JSONs): `17721 samples · identical 10525 (59.39 %) · moved 7196`, strata
`landing→landing 3956 @ +2.000 mm exactly · tread→tread 1584 @ −192.000 exactly · landing→tread
168 (−3070 max = the a0 ray) · fascia→tread 310 (−165.640 max)`, guard-only strata match the
`outer_r` term, **no eighth stratum** — byte-identical to the report's table, and the 5,986
headline is the final-tree walked count (3924+1584+310+168) as the report itself states.
scene05/13/19 blobs are `[re-run]` identical across all three S06 geometry commits, and R-4/R-6
33/33 at HEAD covers the library. The 6 scene06 lint ERRORs at HEAD (bollard h 0.750) exist
identically at pre-fanout `8bf7882` — "lint unchanged" is honest. The S06-F5 amend incident is
exactly as reported: `892f9b3` (S03's original declaration, correct message+content) is now
**dangling**; `367665f` carries S03's content under S06's intended message; `af49ef9` carries
S06's GT-29/30 rows under a GT-27/28 title. Content losslessness verified by diffing all three.

**Not confirmed**: the report's claim "stamped baseline-of-record" (§, line ~387). The stamp on
disk (`look_check/scene06/260731_w3_s06/round_stamp.json`) has **no `baseline_of_record` key, no
`dirty_paths`, and `env: {}`** — the same F5 class the README §4 chain calls out for scene18,
in a window when the worktree was demonstrably dirty with seven other lanes' files. The round
itself is real (15 cuts on disk, `git_head 69c6f9f` correct); only the marker convention was
dropped. → RT-A1.

## 3. Cross-lane floor at final HEAD `[re-run]`

- `geom_invariance_check.py` unscoped, isolated arm at `ede174a`: **assembly 33/33 in all three
  arms · R-4 33/33 PASS · R-6 33/33 PASS**, per-scene numbers matching the lane reports
  (scene01 431/`a9d6c2ba` · scene03 1751 · scene06 2009 · scene08 714 · scene09 1507 ·
  scene11 3788 · scene13 674 · scene17 968/`186a4907`).
- `placement_lint.py` unscoped: TOTAL **ERROR 21 · WARN 333 · BLOCK 29**. ERROR distribution:
  scene02×4 · scene05×4 · scene06×6 · scene12×2 · sceneC2×4 · sceneN5×1 — **none introduced by
  this fanout** (scene06's six verified pre-existing at `8bf7882`; the rest are out-of-scope
  scenes). scene08 is the only scene with `PLACEMENT=yes` (its declared datum), scene13 carries
  the single legitimate asphalt `patch=1`, scene03's census shows `patch` gone.
- **No humans/vehicles**: grep across `scenes/main/*.py` finds only comments/prop names
  (`bus_pole` is a stop pole); scene01's self-check asserts "사람·차량 0" as a gate.
- **Rhododendron / K4-F1**: S06/S08/S09 cite K4-F1 explicitly; S09's `season_audit` re-admits
  Burning_Bush on measurement; no lane report reads the library-wide flower loss as a regression
  to chase.

## 4. New findings (owed actions)

- **RT-A1 (MED, S06 owner or supervisor)** — `260731_w3_s06/round_stamp.json` lacks the
  `baseline_of_record: true` marker, `dirty_paths`, and a real `env` block, while the S06 report
  names it baseline-of-record. Until a keys-only stamp amendment lands (cb7/SB-3 precedent:
  amend the stamp, re-render nothing), any adjudicator reading stamps (as D14 and SB did) will
  not find scene06's baseline. The ledger §4 GT-29/30 records are currently the only authority.
- **RT-A2 (MED, supervisor sweep)** — the README §4 chain and `look_check/INDEX.md` are stale
  for **all eight** rebuilt scenes (chain still resolves 01→`mb24`, 03→`cb2`, 06/08/09/11/13/17→
  `260730_w2d_fix`/`cb1`). S11/S13/S17 flagged their own rows as owed; S01/S03/S06/S08/S09 did
  not. One supervisor commit should add all eight rows at once — the next regression round
  judged through `resolve_round` will otherwise compare against pre-W3 grids (the exact D14-B3
  failure SB just closed).
- **RT-A3 (LOW→MED, S03+S09 owners / round runners)** — the two scenes deviate from the
  boot-free gate convention in different ways, both re-verified:
  (a) **scene03 has no `NEGOBS_SMOKE` mode at all** — its CPU gate is `NEGOBS_SELFCHECK=1`
  (re-run: 사행 OK · 강폭 OK, rc 0, no boot). Invoking `NEGOBS_SMOKE=1` on scene03 is silently
  ignored and **falls through to interactive GUI mode**: it boots Isaac and parks in the app
  loop forever — measured here, where the mistaken invocation sat on the GPU lock until killed.
  A one-line "unknown smoke env" guard (or a real SMOKE alias) would remove the trap.
  (b) **scene09's SMOKE deliberately boots Isaac** (`boot(capture_mode or smoke)`,
  scene09:1660) — re-run under `env_isaaclab`, headless: rc 0, season audit prints 위반 0. Valid,
  but it needs the sim env, unlike the other six lanes' boot-free gates (GT-1's "boot-free and
  GPU-free" wording).
- **RT-A4 (LOW, tooling/convention)** — stamp key `baseline_of_record` now has two meanings in
  the wild: boolean marker (s01/s08d/s09/s11/s13b/s17, cb7 `false`) vs "path of the round this
  pilot compared against" (s03). Both are truthy for s03, so marker-readers accidentally pass,
  but the semantics should be split (e.g. `compared_against`) when `stamp_round.py` gains the
  field (S01-F3/S08-F3 already ask for this).
- **RT-A5 (recorded, no action owed beyond W9)** — S09's geometry commit edited frozen
  `ground_kit.py` (its own `SCENE_PLANS["scene09"]` fixture row only, +16 comment lines, declared
  in GT-35 before landing, region/edges/pave drift explicitly left to Lane-1). Letter-violation
  of the kit freeze, spirit-compliant; W9's remaining four instances (16/18/C2/03) stay with
  Lane-1 as SB routed them.
- **RT-A6 (INFO)** — S01 added `scripts/rounds/crops_260731_w3_s01.py`. `scripts/rounds/` has
  prior round-script precedent (`crops_260730_w2d.py`), so this reads as convention, not a
  `scripts/` violation; noted because the fanout brief's letter says "never touch scripts/".
- **RT-A7 (INFO, arm builders)** — a bare `git archive` arm **cannot assemble scene01 or
  scene18** (gitignored payloads `assets/scene01/*`, `assets/coastal/*`); geom_invariance exits
  2 with `SystemExit(1)` on those scenes until the payloads are wired in. Every lane that
  reported 33/33 from an isolated arm had wired assets (S06 §7.3 says so explicitly); anyone
  reproducing floors should know the two failure signatures are environmental, not regressions.
- **RT-A8 (INFO, observation)** — the S06 landed `overview` crop shows a small pink-blossoming
  tree at the south-east corner. No cherry reference exists in `scene06`'s code; it is most
  likely a shrub-USD crown. Flagged for the S06 owner's next look pass as a possible season
  mix-in; not measured further here.
- **Incident, this lane (recorded)** — before discovering that this scratchpad is shared across
  lane sessions, my first (failed) probe attempt overwrote two scratch log files
  (`t4b_raw.log`/`t4b_wrap.log`). The stored frames and manifests were untouched, and the re-run
  regenerated equivalent logs (`rt_t4b_*.log`) whose error census matches the T4b report. No
  repo file was affected.

## 5. Re-run inventory (for reproduction)

```
git archive ede174a → arm; symlink gitignored asset payloads (see RT-A7)
(arm) python3 scripts/geom_invariance_check.py          # 33/33 R-4+R-6 PASS
(arm) python3 scripts/placement_lint.py                 # ERROR 21, distribution as §3
(arm) NEGOBS_SMOKE=1 python3 scenes/main/<6 scenes>     # rc0; 03 → NEGOBS_SELFCHECK=1 (CPU),
(arm) 09 → NEGOBS_SMOKE=1 in env_isaaclab, headless     # rc0 · see RT-A3
flock /tmp/negobs_gpu.lock … t4b_probe.py raw|wrap      # §1.2 table
python3 gt_diff.py gt_head.json gt_post3.json           # §2.3 strata, byte-match
README §4 chain resolution re-implemented               # 33/33, 0 unresolved
regr JSON re-parse (7 rounds)                           # §2 table
git show --stat on all 54 lane commits                  # ownership §2
```
