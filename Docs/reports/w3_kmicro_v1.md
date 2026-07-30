# W3 K-micro — kit defects and tooling (`props_kit` · `scene_common` · `ground_kit` · `building_kit` · `stamp_round` · INDEX/README)

- **Lane**: K-micro (kit defects + tooling), sequential commits · **Branch**: `feat/realism-v1`
- **Baseline of record for every number below**: HEAD **`4bae470`** (verified live at lane start,
  not taken from the brief). Final HEAD **`6e19f79`**, 12 commits.
- **Dispatch**: FANOUT A's routed kit findings — S06-F1 · S08-F1 · S06-F2 · S09-F1 · S08-F2 ·
  S13-F1 · SB-F1 · S01-F1 · T4b-F2 · RT-A1 · RT-A2 · RT-A4 · ledger §7 **W9**.
- **GT rows created: none.** Nothing this lane touches is a walked surface, a drop edge, a
  hazard/collision box, or an element AABB that GT reads. The one item that owed a declaration
  under §0-1 is W9, which moves a **published number** (not geometry) — declared in
  `gt_changes_w3.md` **§12-1** *before* it landed.
- **GPU: 0 s.** No round was rendered, no `look_check` frame was written. Every instrument in this
  report is CPU and boot-free. The GPU lock was never taken.

---

## 0. Verdict

| # | Item (source) | Verdict | Commit |
|---|---|---|---|
| 1 | `build_tube_railing` / `build_glass_balustrade` bearing (**S06-F1 · S08-F1**) | **FIXED** — polyline bearing honoured, `bearing=` escape hatch | `0ffb73b` |
| 2 | 3 dead `SHRUB_SPECIES` roles + silent pool fallback (**S06-F2 · S09-F1 · S03**) | **FIXED** — 4 measured rows, loud fallback, registry gate | `f89b898` |
| 3 | `build_planter(species=)` (**S08-F2**) | **FIXED** | `9afe561` |
| 4 | `build_chevron_band` 45° (**S13-F1**) | **FIXED, default held** — docstring was right, code was wrong; capability added, default preserves scene13 | `7659a09` |
| 5 | `_gt24` gate tuple (**SB-F1**) | **FIXED** — negative control proves the gate bites | `b763afc` |
| 6 | backdrop roof furniture vs `z_ceil` (**S01-F1**) | **FIXED as `p.ridge`; clamp is opt-in on measured evidence** | `ee4e598` |
| 7 | `SCENE_PLANS` fixture drift (**ledger §7 W9**, MB-F2, SB-F2) | **CLOSED, 5/5** — and W9's own scene03 text corrected | `64f107d` → `2391ddc` → `85720cc` |
| 8 | `scene10:2426` comment (**T4b-F2**) | **FIXED** | `abe61d6` |
| 9 | `260731_w3_s06` stamp (**RT-A1**) | **AMENDED on disk** (gitignored; keys only, nothing re-rendered) | — (§9) |
| 10 | `stamp_round.py` real fix (**RT-A1 · RT-A4**) | **FIXED** — `dirty_paths` · `env_source` · `baseline_of_record` · v0 readable | `20a986b` |
| 11 | INDEX + README §4 owed rows (**RT-A2**) | **FIXED** — 8 rounds into the chain, `INDEX §3-W3` created | `6e19f79` |

**Tree-wide floor at final HEAD `6e19f79`, isolated arm** `[re-run]`:

```
geom_invariance_check   33/33 assembly · R-4 33/33 PASS · R-6 33/33 PASS
  vs the 4bae470 arm:   132/132 cells identical  (33 scenes × 3 arms + prim counts) — diffs 0
placement_lint          ERROR 21 · WARN 333 · BLOCK 29 · INFO 2
  vs the 4bae470 arm:   ERROR 21 · WARN 333 · BLOCK 29 · INFO 2  — identical, 0 introduced
props_kit               42/42   (was 32/32) · prims built 470 (was 427)
building_kit           187/187  (was 180/180)
ground_kit             all pass · fixture dry run 1137 → 1109 prims (declared, §7)
scene_common --variation PASS   · 16 PASS lines (was 13)
stamp_round --self-check  8/8   · 171/171 existing stamps on disk still read
NEGOBS_SMOKE rc0: scene01 02 06 08 10 11 13 17 · scene03 NEGOBS_SELFCHECK rc0
```

**Isolated-arm method** (10 lanes share this worktree, so nothing tree-wide was measured in it):
`git archive <rev>` into scratch **plus the gitignored asset payloads symlinked in** —
`assets/*.exr|jpg`, `assets/scene01/`, `assets/coastal/`, `vegetation/`, `urban/`, `urban_cc0/`.
Without them `geom_invariance_check` cannot assemble scene01 or scene18 (RT-A7). Two arms were
kept live for the whole lane — `4bae470` (control) and the working arm — and every kit edit was
copied into the working arm and A/B'd before it was committed.

---

## 1. Item 1 — the two railing templates were X-axis-only (S06-F1 · S08-F1)

`build_tube_railing` computed the segment bearing and then **threw it away** (`ang = …` followed
by `del ang`), laying every rail with `rotY=90.0`, i.e. along +X. `build_glass_balustrade` had the
same defect by a different route: panels and shoe were world-axis `add_box` calls and the cap rail
a `rotY=90` cylinder. A Y-aligned polyline therefore produced elements **crossing** the run, in
silence — which is why S06 built its helix and deck bronze rails in-scene against the template's
numbers, and why S08 had to wrap every chord in a `build_rot_group`.

**The fix.**
- `scene_common.add_box` / `add_cylinder` gain `rotZ` (and, in item 4, `add_box` also `rotX`).
  The op is authored **only when non-zero**, and its position in `xformOpOrder` gives the applied
  order `scale → rotX → rotZ → translate` for boxes and `rotX → rotY → rotZ → translate` for
  cylinders — USD applies xformOps in reverse list order, the convention `build_rot_group`'s own
  comment documents. **`rotZ=0.0` leaves the prim byte-identical**, which is the property that
  makes this a zero-geometry-change addition across all 33 scenes.
  `add_box` also declines the displacement skin when rotated: `_ground_skin` authors an
  axis-aligned patch from `(center, size)` and would stick out past a spun slab's corners.
- Both templates take a signature-preserving `bearing="auto"` (K4(c)): the segment's own bearing by
  default, a constant if given a number, and **`bearing=0.0` reproduces the old X-only output
  exactly** — the escape hatch for a caller that already spins the run in a `build_rot_group`.

**Evidence.** `props_kit` self-check 32 → 37 checks here, asserting the bearing rather than
describing it (the stub now records `rotZ` per prim): a Y-aligned run lays **4 rails at rotZ 90**
and **4 panels + shoe + cap at rotZ 90**; a 45° polyline lays rotZ **45** (not snapped to an axis);
`bearing=0.0` regresses to rotZ 0; an X-aligned run is still rotZ 0.
Isolated-arm A/B: **132/132 cells identical** — scene06's and scene08's runs are in fact X-aligned
in their local frames, so the correction costs nothing today and removes the trap for the next
caller.

---

## 2. Item 2 — three `SHRUB_SPECIES` roles were dead, and the fallback was silent

`SHRUB_SPECIES` names seven roles. Three of them — `riparian` (Switchgrass), `verge_turf`
(`Grass_Short_A/B`), `edge_weed` (`Grass_Short_C`) — pointed at assets that are **on disk but had
no `VEG_SHRUBS` row**, and `place_shrubs` filters `species=` *and* `pool=` through that table. All
three resolved empty and fell through to `SHRUB_ORNAMENT` without a word, returning a healthy count
for a bed that was not what was asked for. scene06's first render put two Rhododendron beds side by
side while the scene printed *"grasses 14"*; Switchgrass was unreachable from any sanctioned call.

**Re-verified at HEAD before fixing** (`ast` over `git show 4bae470:scene_common.py`):
9 `VEG_SHRUBS` rows · **3 roles resolving to 0 rows** · **4 orphan assets** named by roles.

**The four rows, five fields each, all measured.** Source `assets/veg_manifest_w2.json`, and each
file **byte-matched to disk this session** (2 457 126 / 845 898 / 124 868 / 1 208 701 B), so the
manifest describes the file that is actually there:

| asset | width (larger XY) | zmin | tri | height (z extent) |
|---|---:|---:|---:|---:|
| `Grass_Short_A` | 1.294 | 0.023 | 32 504 | 0.162 |
| `Grass_Short_B` | 0.675 | 0.017 | 11 137 | 0.164 |
| `Grass_Short_C` | 0.304 | 0.002 | 1 598 | 0.125 |
| `Switchgrass` | 2.027 | 0.001 | 8 934 | 1.372 |

**Season pixel-check — the K4-F1 test, applied to each.** Measured this session with PIL over the
basecolor PNGs, and cross-read against the manifest's UV-weighted `foliage_uv_hue`:

| texture | green | yellow-green | orange | **red** | **magenta/pink** |
|---|---:|---:|---:|---:|---:|
| `switchgrass_basecolor.png` | 1.0000 | 0.0000 | 0.0000 | **0.0000** | **0.0000** |
| `lawngrass_a_basecolor.png` (A/B/C share it) | 0.1995 | 0.2384 | 0.5617 | **0.0003** | **0.0000** |
| `rhododendron_basecolor.png` (control) | 0.0003 | 0.2230 | 0.0023 | 0.0353 | **0.7391** |

The Rhododendron control reproduces the library's own "76.7 % magenta" finding, which is what makes
the other two rows trustworthy. Whole-texture and UV-weighted censuses **differ and both are
reported**: `lawngrass_a` is a large atlas whose straw regions the mesh UVs barely sample, so the
manifest reads green 0.535–0.542 + yellow-green 0.281–0.287 = **0.821–0.823 ≥ the 0.75 turf gate**
(the same gate `Grass_Trimmed_A~C` failed at 0.72 and were therefore never procured). The decisive
fact is identical in both: **no autumn red and no bloom magenta**, so unlike `Forsythia` /
`Burning_Bush` / `Rhododendron` these four need no seasonal strip and get no `SEASONAL_SUBPRIMS`
row.

**The fallback is now loud.** A failed `species=` prints the role, the reason (role unregistered vs
no `VEG_SHRUBS` row / absent from disk) and **the pool it actually drew from**, and counts
`LOOK_STATS["shrub_species_miss"]`; an empty `pool=` prints and counts `shrub_pool_miss`. The
fallback itself is kept — an empty bed mid-render is worse than a substituted one — but it can no
longer happen without a line in the log.

**And a gate, so this cannot recur.** `scene_common --variation` grows a section [4]: every
`SHRUB_SPECIES` role must resolve to ≥ 1 `VEG_SHRUBS` row · no role may name an orphan asset ·
the default pools must be registered. Had it existed, three scene lanes would not have found this
one at a time in three separate renders.

**Zero geometry, structurally**: no landed scene calls those three roles (scene03
`hedge_evergreen` · scene06 `border_narrow` / `ornament_bed` · scene08 `ornament_bed`), so the new
rows are unreachable from today's tree. **132/132 cells identical** confirms it.

---

## 3. Item 3 — `build_planter` could not be told a species (S08-F2)

The internal `place_shrubs` call passed `pool=` only, so a scene could not pin the species of its
own square beds: scene08's census read 3 species scene-wide although every bed it built was
monospecific, and scene13 wrote the workaround into a comment (`scene13:284` — it plants planter
trees scene-side *because* `build_planter` has no species argument). One keyword, default `None`,
K4(c)-preserving; `place_shrubs` only lets `species` beat `pool` when it is truthy, so `None` is
the old behaviour exactly. **132/132 identical.**

---

## 4. Item 4 — `build_chevron_band`: the docstring was right and the code was wrong

The docstring claimed *"Stripes run at 45 deg"*. The implementation contained **no rotation at
all** — six axis-aligned boxes spread along local Y, i.e. **vertical bars** — and no caller could
fix it from outside, because `_root` takes yaw (Z) only and an in-plane tilt on a wall needs
rotation about the wall normal.

**Decided on evidence, as instructed.**
- **LAW** — `w3_intake_v2_images.md` §2, row G13: *"yellow/black **diagonal** chevron bands and
  reflective strips on the wall ends"*.
- **The photograph** — the reference half of `Docs/reports/_w3_s13_crops/s13_ramp_marks.png`,
  **opened and viewed for this decision**: the band on the parapet wall end is an unmistakable 45°
  hatch. The vertical yellow/black in the same photograph is the **kerb block**, a different
  product — which is what S13 was seeing when it wrote *"the vertical band is also real on Korean
  ramp walls"*. It is, but not as the wall band.

So: docstring correct, implementation defective, capability added.

**`slant_deg=`.** Stripes are spaced on the axis **perpendicular to themselves** (pitch `width/n`,
so the statutory painted width is unchanged by the slant) and each is cut to the **chord** of the
band rectangle along its own direction, so the hatch fills the rectangle instead of throwing long
bars past its corners. The stripe count rises with the slant because the band is wider across a
diagonal — 6 → **13** at 45°, which is what a real hatch does.

**The default stays `0.0`, and that is a discipline decision, stated.** scene13 shipped the
vertical form, kits are frozen against wired geometry in this window, and scene13 is not this
lane's file. The general construction is written so that **θ = 0 degenerates to the original three
expressions** — same float expressions, not merely the same value — and the self-check asserts the
six landed stripes' `center` / `size` / `rotX` by **equality** against the legacy values. The 45°
flip is the S13 owner's edit, with its own declaration. **132/132 identical · scene13 SMOKE rc0 ·
`placement_lint --scenes scene13` ERROR 0.**

---

## 5. Item 5 — the GT-24 gate was one profile short (SB-F1)

The 07-31 supervisor amendment extended GT-24 to the fourth unit-paved profile and deleted
`levee_paved`'s `("patch", 4)` row, but the gate tuple still named three. SB recorded rather than
took it, because that closure was authorised for one tuple. This is the second tuple:
`_gt24 = (plaza_granite, plaza_water, sidewalk_block, **levee_paved**)`, wording 3종 → 4종.

**Negative control** — the point of a gate is that it bites, so it was made to bite. Restoring
`("patch", 4)` on `levee_paved` in a scratch copy:

```
old gate:  passes (60/60)
new gate:  [FAIL] GT-24 단위포장 4종 patch 행 0 …
           levee_paved:['patch','crack','stain','weed']        process exit 1
```

Zero geometry, zero prim delta, **132/132 identical**.

---

## 6. Item 6 — S01-F1: the roof furniture was outside the total-height invariant

`building_kit`'s invariant is *"the shell top stays at `base_z + h`"* and backdrop policy (2) says
*"build nothing above `z_ceil`"* — but `build_rooftop` and `_b_backdrop` both emit a parapet band
and a penthouse **above** `top_z`, and policy (2) never gated them. A caller that sizes a backdrop
from `h`, which is what the invariant tells it to do, ships a mass **+2.90 m** taller than the
ceiling it just checked. scene01 measured exactly that on all six blocks, printed *"sky above roof
6/6"*, and rendered a brick wall running off the top edge of `h0.3_d10`; it carries a scene-local
`ROOF_ALLOW` constant to this day to work around the kit.

**What landed.** `Plan` gains `roof_allow` · `ridge` · `roof_under_ceil`.
`roof_allow(p)` is **exact** for `kind="backdrop"` (`_b_backdrop` uses no rng for the penthouse —
its footprint moved into `backdrop_penthouse(p)` so the plan and the builder read the same three
lines) and an **upper bound** for every other kind, because `build_rooftop` jitters the penthouse
±8 % off an rng seeded on the **prim prefix**, which does not exist at plan time. A bound is the
honest answer to *"will this break frame?"*, and the new self-check [14] proves it.

**The clamp is opt-in, and the reason is measured, not argued.** A probe was inserted into
`_b_backdrop` in the isolated arm and every backdrop block in the tree was planned:

| scene | backdrop blocks | with a judged eye set | `ridge − z_ceil` | under the ceiling |
|---|---:|---:|---|---:|
| scene01 | 6 | 6 | **−0.573 … −0.449 m** | **6** |
| scene02 | 10 | 10 | +11.485 … +22.803 m | 0 |
| scene08 | 5 | 5 | +23.472 … +38.706 m | 0 |
| scene16 | 12 | 12 | +10.645 … +22.493 m | 0 |
| scene18 | 14 | 0 | — (`z_ceil` None, no eye set) | — |

Of the **33** backdrop blocks that are planned *with* a judged eye set, only scene01's **6** are
under the ceiling; the other **27** are above it by 10.6 to 38.7 m. (The coincidence that "33
blocks" matches "33 scenes" is a coincidence — scene18's 14 blocks are planned without an eye set
and are not in that count.) **Correction to commit `ee4e598`'s message**, which quotes the lower
bound as *"8.9 m"*: the measured minimum excess is **+10.645 m** (scene16 `CityBlock_N2`). The
table here is the figure of record; the commit message is wrong and is corrected rather than
silently left.

And scene16 argues its case in its own source:
*"policy (2) is written for a building the camera faces, not for a wall it travels along"* — a
downtown street wall that exists to close the horizon. Defaulting the clamp on would delete 27 of
33 blocks' skylines to enforce a rule those scenes have talked their way out of on the record. So
the kit's default duty is to **state the truth** (`p.ridge` — precisely the number scene01 had to
derive by hand), and `roof_under_ceil=True` is there for a caller who wants policy (2) enforced
rather than merely checked. The statutory 1.20 m parapet is never clamped: a shell whose parapet
already breaks the ceiling is too tall, and the fix for that is the caller's `h`.

**Self-check [14]** (180 → 187 checks): over `kind × tier × W(3) × floors(4) × base_z(3)`, the
highest emitted prim is **≤ `p.ridge`** everywhere (slack ≤ 0.464 m) and **exactly** `p.ridge` for
`kind="backdrop"`; `roof_allow` is the **+2.90** scene01 measured; both clamp arms' declared ridge
equals their emitted top; and a shell that already breaks the ceiling keeps its parapet and says so
through `ridge > z_ceil` rather than faking compliance. **132/132 identical.**

---

## 7. Item 7 — W9: `SCENE_PLANS` fixture drift, five instances, closed

`SCENE_PLANS`'s stated doctrine (v1.4) is *"now mirrors the wired call"*. Four fixtures no longer
did (scene09 was synced by its own lane, RT-A5): each omitted the `overrides=dict(surface=…)` its
scene actually passes, so **a census taken from `ground_kit.py` alone could not see the override** —
which is exactly how GT-24 came to declare 15 in-scope scenes when 11 were reachable.

**Declared before it landed** (§0-1): `64f107d` writes ledger **§12-1**, `2391ddc` marks §7 W9
LANDED, `85720cc` lands the code. The declared number:

| | fixture prims before → after |
|---|---|
| 33-scene dry run | **1137 → 1109 (−28)** · scatter instances **670 → 670** |
| scene03 | 35 → 22 (−13) |
| scene16 | 43 → 45 (+2) |
| scene18 | 34 → 45 (+11) |
| sceneC2 | 40 → 12 (−28) |

**W9's own replacement text for scene03 is stale and was not followed.** It prescribes
`surface=(("patch", 8), ("stain", …))` from `:900-916`; the S03 rebuild that landed in FANOUT A
**deleted the patch row** (§3(ii) rectangle ban) and raised the weed row to 8. The fixture mirrors
the file as it is at `4bae470` — which is the doctrine W9 exists to enforce. The correction is
recorded in the code comment, in §12-1 and beside W9's own bullet.

**Proof the drift is closed rather than merely edited**: the `surface=` literal was parsed out of
each of the five scene files with `ast` and compared against
`SCENE_PLANS[scene]["overrides"]["surface"]` — **5/5 MATCH** (03 · 16 · 18 · C2 · 09).

**Zero geometry, structurally**: `SCENE_PLANS` is read by `ground_kit._selfcheck` and by
`scripts/make_review_gallery.py` (profile name only) and by **no wired scene** — grep across the
tree. **132/132 identical** confirms it.

**Residual, named not hidden** (the S09 precedent): `region` / `edges` / `origin` are still fixture
approximations, sceneC2's `infra` zeroing and `pave` override are not mirrored, and scene09's `pave`
step override is still absent. They move the dry-run **joint** count — a second declaration with
its own number — and stay with `ground_kit`'s owner. W9's rule remains in force for them.

---

## 8. Item 8 — T4b-F2: one comment, one revert trap

`scene10:2426-2431`'s conclusion (an ancestor `strongerThanDescendants` bind does not reach inside
a prototype) is correct; its **cited cause** was not. It named the SimPBR/**MDL** fallback, which
T4's `ensure_mdl_package()` fixed. Today the fallback on `Outcrop_0` is **MaterialX**:
`rock_moss_set_01` is a Poly Haven CC0 row, and all 33 CC0 rows / 50 materials reach an
`ND_normalmap_float` node missing from this runtime's Sdr registry. An owner reading "MDL, therefore
fixed upstream" and reverting lands FU-1's measured **0.02 % → 4.50 %** red. The corrected comment
also records that `Outcrop_1..3` are NVIDIA assets with no MaterialX gap, so for those three the
workaround function really is gone and only the `rockface_tint` art decision remains — and that the
clean migration (the `urban_kit` `treatment=` wrapper) is the scene owner's call, not this lane's.
Comment-only: **132/132 identical · scene10 SMOKE rc0 · lint ERROR 0.**

---

## 9. Item 9 — the `260731_w3_s06` stamp (RT-A1)

`look_check/**` is gitignored, so this is an **on-disk amendment with no commit**, on the cb7/SB-3
precedent: **keys only, nothing re-rendered, no pixel touched.** The round is real (15 cuts on
disk, `git_head 69c6f9f` correct); only the marker convention was dropped, in a window when the
worktree was demonstrably dirty with seven other lanes' files.

Added: `baseline_of_record: true` · `supersedes_baseline_of_record: 260730_w2d_fix` ·
`schema: round_stamp/v1` · the render `env` · `dirty_paths` · an `amendment` note.

**Both recovered values are sourced, and their limits are stated in the file itself.**
The env and the dirty-path list come from `w3_s06_v1.md` §8, which records both — so nothing is
invented. But recovery is not capture: the stamp carries `env_captured: false` **and**
`env_recovered: true`, with `env_source` naming the report and explaining that the render arm was an
env-prefix on the render command while `stamp_round.py` ran as a **separate** command, so the render
shell's environment was already gone. That is precisely the defect item 10 now prevents. The report
lists **10** dirty paths against the tool's observed `dirty_files: 11`; the 11th is **not**
reconstructed and not padded — the count stands as the tool's own record and the gap is written
into `dirty_paths_source`.

**Still owed, not by this lane**: `260731_w3_s03`'s stamp spends `baseline_of_record` on RT-A4's
other meaning. `stamp_round.read_stamp` now normalises it so no marker-reader is fooled, but the
stamp itself wants a keys-only amendment from the S03 owner.

---

## 10. Item 10 — `stamp_round.py`, the real fix

The tool's job is to make a round readable in six weeks, and FANOUT A showed it was producing
**unreadable stamps** in three separate ways.

1. **`dirty_files` was a count.** "7 dirty files" does not answer *which* — the only question that
   matters when ten lanes share one worktree. → **`dirty_paths`** (with the status letters), count
   kept for older readers.
2. **`env` was captured in the stamping shell.** The render runs inside the GPU lock; the stamp is
   normally a separate command afterwards. `260731_w3_s06`'s `env: {}` is that. Worse, `{}` does
   not distinguish *"no flags"* from *"not captured"*. → **`--capture-env <dir>`, called from the
   render shell**, drops a sidecar that any later stamping run picks up automatically;
   `--env-file` accepts one explicitly; `env_source` always names the origin and `env_captured`
   is false when it could not be had (plus a stderr warning). `PT_FAST` /
   `CUDA_VISIBLE_DEVICES` are captured alongside `NEGOBS_*` — they change frames too.
3. **`baseline_of_record` did not exist as a field.** Six lanes hand-appended it and S06 forgot. →
   first-class, with `--baseline-of-record` / `--not-baseline` / `--superseded-by` / `--note`.
4. **RT-A4: one key, two meanings** (boolean marker vs "the round this pilot compared against";
   both truthy, so marker-readers pass by accident). → split into **`compared_against`**.

**Old stamps stay readable**, which was a hard requirement: `read_stamp()` tags schema-less files
`round_stamp/v0` and normalises a *string* `baseline_of_record` into `compared_against`.
Verified against real data, not fixtures: **all 171 `round_stamp.json` files on disk read
successfully** — 159 v0 unmarked · 11 boolean markers · **1 string**, which is exactly RT-A4's s03
stamp and which normalises correctly. `--self-check` 8/8, including a negative case proving an
uncapturable env is *labelled* rather than silently empty.

---

## 11. Item 11 — RT-A2: the chain and the INDEX were stale for all eight rebuilt scenes

SB's chain refresh landed **before** FANOUT A's eight rebuilds were judged, so the chain still
resolved `01→mb24` (5 cuts) · `03→cb2` (5 cuts) · `09→cb1` (17 cuts) ·
`06·08·11·13·17→260730_w2d_fix`. The next regression round would have repeated, on eight scenes,
the exact D14-B3 failure SB had just closed. Five of the eight lanes did not flag their own row.

**README §4** — the eight rounds were added at the head, plus eight table rows and an amended note.
**Verified by simulating `resolve_round` over all 33 scene directories with the chain exactly as
committed** (parsed back out of the README, not retyped): **33/33 resolve · 0 unresolved · exactly
the eight FANOUT A scenes move · no scene loses a cut** (01 5→13 · 03 5→16 · 06 15→15 · 08 15→15 ·
09 17→18 · 11 14→15 · 13 15→15 · 17 14→14). Each of the eight round names exists under exactly one
scene directory, so head position cannot shadow another scene. Note (2) is amended — scene17's
baseline is now its own 14-cut grid, so the "don't promote a 5-cut round" argument is untouched —
and note (1) is extended: `cb1` and `mb24` are now unreachable too.

**`INDEX.md`** — §3 is a 07-30 snapshot and carried **no W3 round at all**, which is why the README
chain had become the only committed record of the W3 grids. New **§3-W3** (46 rounds, 1 918 MB) and
**§3-W3-1** (19 gate/twin entries) are enumerated **from the stamps and PNGs on disk**; every
`git_head` is read out of that round's own stamp. Status is **derived, not asserted**: a round is
marked baseline-of-record iff `resolve_round` actually returns it under the committed chain. The 16
scenes that now have a W3 baseline had their `260730_w2d_fix` rows un-marked in the same edit
(16/16).

Three gaps are recorded rather than left to be inferred: scene08's `260731_w3_s08` / `_s08b` /
`_s08c` carry **no `round_stamp.json`** at all (spec §6.2 **X1**: *"an unstamped round is unreadable
in six weeks"*); scene03's stamp is the RT-A4 case above; scene18 still carries no marker and ledger
§4 GT-26 remains its authority. `gates/scene13/260730_w3_s13_pre` — the row S13 flagged as owed — is
in §3-W3-1, since without it `260730_w3_s13b` has no before-arm on record.

---

## 12. New findings, handed on

| # | Sev | Finding | Owner |
|---|---|---|---|
| **KM-F1** | **MED** | **18 of 33 scenes boot Isaac on `NEGOBS_SMOKE=1`** — `09 · 15 · 16 · 18 · 19 · 20 · C1 · C2 · C4 · D1 · D2 · D3 · D4 · N1 · N2 · N3 · N4 · N5` (grep for `boot(capture_mode or smoke)`). RT-A3(b) reported this as scene09's peculiarity; it is the majority of batch1 and a third of main. Any lane asked for a "boot-free `NEGOBS_SMOKE` per scene touched" floor **cannot** deliver it on those 18 without the sim env and the GPU lock, and today it fails with a bare `ModuleNotFoundError`. Either the floor's wording or those scenes' smoke path should change; a one-line "this scene's SMOKE requires `env_isaaclab`" message would at least stop the failure reading like a regression | spec §6.1 owner / scene owners |
| **KM-F2** | **MED** | **`scene08`'s `260731_w3_s08` · `_s08b` · `_s08c` have no `round_stamp.json`.** Spec §6.2 **X1** requires one on *every* capture directory. They are superseded pilots, so nothing depends on them today — but three unstamped 15-cut rounds sitting in a scene root are indistinguishable from a baseline in six weeks | scene08 owner |
| **KM-F3** | **LOW** | **`260731_w3_s03`'s stamp is RT-A4's ambiguous case and is still on disk.** `read_stamp` normalises it, so no reader is misled, but the round that `w3_s03_v1.md` names scene03's baseline-of-record carries **no** boolean marker. One keys-only amendment (cb7/SB-3 precedent) closes it | S03 owner |
| **KM-F4** | **LOW** | **`build_planter` still cannot pin its *tree* species.** Item 3 fixed the shrub half; `build_tree` is called with no `species=`, so a planter tree falls back to the scene's `SCENE_SPECIES` row. scene13 documents the workaround in-code (`scene13:284`) and plants its planter trees scene-side to avoid it. A `tree_species=` kwarg is the same one-line, signature-preserving shape as item 3 — deliberately **not** taken here because the dispatch named `place_shrubs` only | K-track / `scene_common` |
| **KM-F5** | **LOW** | **`build_chevron_band`'s 45° arm has no wired consumer.** The capability exists and is self-checked, but until scene13 (or another ramp scene) passes `slant_deg=45.0` the library still ships only the vertical form the reference does not show on wall ends. This is a **held** capability, not a landed look | S13 owner |
| **KM-F6** | **INFO** | The `roof_under_ceil` clamp is written and self-checked but **wired nowhere**, by design (§6). scene01 still carries its scene-local `ROOF_ALLOW` constant; it can now read `p.ridge` instead, which would delete a hand-derived number from a scene file. Not taken — scene01 is not this lane's file | scene01 owner |
| **INFO** | — | `placement_lint` at final HEAD reads **ERROR 21 · WARN 333 · BLOCK 29 · INFO 2**, byte-identical to the `4bae470` arm. The red-team's §3 census quotes the same ERROR/WARN/BLOCK triple with INFO 0; the INFO 2 is present in **both** arms here, so it pre-dates this lane whatever its origin | recorded |

---

## 13. Files this lane wrote

* `props_kit.py` — `_seg_bearing` · `bearing=` on two templates · `slant_deg=` on `build_chevron_band` · self-check 32 → 42
* `scene_common.py` — `rotZ`/`rotX` on `add_box`, `rotZ` on `add_cylinder` · 4 `VEG_SHRUBS` rows · loud `place_shrubs` fallback · `build_planter(species=)` · `--variation` section [4]
* `ground_kit.py` — `_gt24` gate tuple · 4 `SCENE_PLANS` fixture rows
* `building_kit.py` — `Plan.roof_allow`/`ridge`/`roof_under_ceil` · `backdrop_penthouse` · `backdrop_ph_h` · `roof_allow` · self-check [14]
* `scripts/stamp_round.py` — rewritten (see §10)
* `scenes/main/scene10_park_deck_switchback.py` — **one comment**, no code
* `look_check/INDEX.md` · `look_check/README.md` §4
* `Docs/audit_v4/gt_changes_w3.md` — §12 + the §7 W9 marker, **both inside `flock -w 600
  /tmp/negobs_ledger.lock`**, re-reading the file inside the lock before each append
* `look_check/scene06/260731_w3_s06/round_stamp.json` — gitignored, keys only (§9)
* `Docs/reports/w3_kmicro_v1.md` — this file

**Not touched, by instruction**: every other scene file · every other script · every other lane's
report · `Docs/surveys/w3_intake_v2_images.md` (quoted, never edited) · every other kit
(`facade_kit` · `infra_kit` · `stair_kit` · `urban_kit` · `variation_kit`) · every other round
stamp.

## 14. Reproduction

```bash
# isolated arms (10 lanes share the worktree — never measure tree-wide numbers in it)
git archive 4bae470 | tar -x -C base/     # control
git archive 6e19f79 | tar -x -C final/    # this lane
# wire the gitignored payloads into BOTH (RT-A7), else scene01/scene18 cannot assemble:
#   assets/*.exr|jpg  assets/scene01/  assets/coastal/  vegetation/  urban/  urban_cc0/

(arm) python3 scripts/geom_invariance_check.py --baseline out.json   # 33/33 R-4+R-6
      # then diff base vs final: 132/132 cells identical
(arm) python3 scripts/placement_lint.py                              # ERROR 21 both arms
(arm) python3 props_kit.py && python3 building_kit.py \
      && python3 ground_kit.py && python3 scene_common.py --variation
(arm) python3 scripts/stamp_round.py --self-check
(arm) NEGOBS_SMOKE=1 python3 scenes/main/scene{01,02,06,08,10,11,13,17}*.py   # rc0
(arm) NEGOBS_SELFCHECK=1 python3 scenes/main/scene03_riverbank.py             # rc0

# item 5 negative control (scratch copy — restores the deleted patch row)
#   old gate passes · new gate FAILs with exit 1

# item 2 pre-state, item 7 drift proof (both `ast`, both CPU)
python3 - <<'PY'   # 4bae470: 9 VEG_SHRUBS rows, 3 roles → 0, 4 orphans
python3 - <<'PY'   # surface= literals: scene file vs SCENE_PLANS → 5/5 MATCH

# item 11 chain proof — parse the chain back out of README §4, resolve over 33 scene dirs
#   33/33 resolve · 0 unresolved · only the 8 FANOUT A scenes move · no cut lost
```
