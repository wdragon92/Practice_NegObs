# W3 · K4 micro-commit — `TEX["moss"]` + the leaf-off tree mechanism

> **Wave** W3 · **Track** K4 (the single authorised `scene_common` micro-commit) · **Date** 2026-07-31
> **Branch** `feat/realism-v1` · **Baseline HEAD** `564cd3d`
> **Authority** `Docs/briefs/s3_scene07_10_rebuild_spec_v1.md` **§8.R OQ-3** — *"K4 MICRO-COMMIT
> AUTHORIZED, executed by this lane … additive + signature-preserving … the mechanism is opt-in,
> default OFF, so the micro-commit itself must prove 33/33 prim-hash identity (96968f3 method) …
> `TEX["moss"]` registration rides the same micro-commit under the same proof."*
>
> **Files written by this task**: `scene_common.py` and this report. **Nothing else.** No scene file,
> no ledger row, no round directory, no render, no GPU.

---

## 0. Headline

| obligation (§8.R OQ-3 / §6.1 floor) | result |
|---|---|
| `TEX["moss"]` registered from `assets/urban_cc0/rock_moss_set_02/textures/`, existing schema | **done** — `dir/diff/nor/rough`, all three files verified on disk |
| `TEX["moss"]` has **zero consumers** after this commit | **0** — see the grep and its two false positives in §1.1 |
| `BARE_SUBPRIMS` table, subprim paths verified by opening the USDs | **done** — `/Root/leaves` confirmed on all 3, usd-core 26.8 |
| `_deactivate_seasonal()` called in `build_tree` **before** `SetInstanceable(True)` | **done** — `scene_common.py:2537-2542`, ahead of the instancing block at `:2543-2555` |
| exposed as a **new optional kwarg, default OFF** | **done** — `build_tree(..., bare=False)`, `scene_common.py:2480`, appended last |
| signature-preserving (§6.2-K4c) | **yes** — one appended default kwarg on `build_tree`, one appended default kwarg on the private `_deactivate_seasonal`; **no existing call site changed** |
| nothing opts in inside this commit | **confirmed** — `bare` has exactly **two executable occurrences**, the signature (`:2480`) and the dead branch (`:2537`); the other four hits are the docstring and the table comment |
| **full 33-scene prim-hash A/B against HEAD, byte-identical 33/33** (96968f3 method) | **99/99 hashes identical · 33/33 prim counts identical · 29,245 prims both arms** (§3) |
| `python3 -m py_compile scene_common.py` | **exit 0** |
| `NEGOBS_SMOKE=1` per touched scene | **vacuous — 0 scene files touched** (substitute evidence in §4.2) |
| `python3 scripts/geom_invariance_check.py` | **exit 0** · R-5 violations 0 · **R-4 33/33** · **R-6 33/33** |
| `python3 scripts/placement_lint.py --scenes all` | **delta 0** — output **byte-identical** between the two arms (§4.4) |

`git diff --stat -- scene_common.py` → `1 file changed, 87 insertions(+), 3 deletions(-)`.
Of the 87 insertions, **51 are comment lines, 14 are docstring prose and 3 are blank** — the
**executable change is 19 lines**: the 5-line `moss` role, the 5-line `BARE_SUBPRIMS` table, the
6-line opt-in branch, and 3 single-line signature/lookup edits. The 3 deletions are those same 3
lines in their pre-edit form (`def _deactivate_seasonal(…)`, its `names = …` lookup, and
`build_tree`'s last signature line) — **nothing was removed from the module.**

---

## 1. What landed, exactly

### 1.1 `TEX["moss"]` — a new texture role (`scene_common.py:124-150`)

```python
moss=dict(dir=os.path.join(ASSETS_DIR, "urban_cc0", "rock_moss_set_02",
                           "textures"),
          diff="rock_moss_set_02_diff_1k.jpg",
          nor="rock_moss_set_02_nor_gl_1k.exr",
          rough="rock_moss_set_02_rough_1k.jpg"),
```

Added **inside** the `TEX` dict literal (the `grass` / `leaf_ground` form), not as a post-dict
assignment, so it is discoverable where every other role is. `TEX` goes 29 → **30** roles.

**Filenames were read off the disk, not off the spec.** The rebuild spec §3.2 names
`…_diff_1k.jpg + _nor_gl_1k.exr + _rough_1k.exr`; the roughness map that actually exists is a
**JPG**. Verified:

```
diff  exists=True  …/rock_moss_set_02_diff_1k.jpg     (1024×1024 RGB)
nor   exists=True  …/rock_moss_set_02_nor_gl_1k.exr
rough exists=True  …/rock_moss_set_02_rough_1k.jpg    (1024×1024 L)
```

**Licence**: Poly Haven, **CC0 1.0** — tier T1, redistributable, already procured
(`urban_manifest_w3.json` `/polyhaven[23]`, md5s recorded there). **Zero procurement.**

**Pixel evidence** `[measured — assets/urban_manifest_w3.json /polyhaven[23].pixels[0]]`:
1024², chroma 757,261 px (72.2 % of the image), **yellow-green 0.9286 of chroma**, orange 0.0652,
red 0.0022, **albedo_lin 0.0812**, near-white 0.0 %. Independent recomputation this session gives a
mean linear albedo of **0.0750** over all pixels and a chromatic-pixel fraction of **71.73 %** —
the chroma gate reproduces, the hue split does not, because the manifest's band edges differ from a
naïve 45–105° yellow-green window. **The manifest is the instrument of record**; the recomputation is
recorded only so nobody re-derives it and thinks the manifest is wrong.

**Three cautions are carried in the code comment**, because the role has no consumer yet and the
first consumer will otherwise trip on them:

1. It is a rock-**with**-moss scan, not a moss carpet — it tiles with rock structure. Correct as a
   joint / riser-base / boulder-top patch (fit **B**); wrong as a large-area ground. The large-area
   case keeps the existing tint convention (spec §3.0 C-A2: green tint on a stone map + a `moss`
   path token so `scene_common.py:520,567` class it as `veg`).
2. The normal map is Poly Haven **`_nor_gl`** — **OpenGL** convention **and EXR**. Every other role
   in this registry is a DX map (`_nor_dx`) or an ambientCG `_nor`, and every other map is JPG/PNG.
   A consumer wanting the repo's convention must flip green or omit `nor` from its `make_pbr` call.
   **This is the one row in `TEX` that is not convention-parallel with its neighbours.**
3. The asset USD binds a `rock_moss_set_02_rough_1k.**exr**` that was never downloaded
   (`urban_manifest_w3.json … texture_bindings`); the roughness map on disk is the JPG named above.

**Why adding a role is inert.** The only code that iterates `TEX` and asserts file existence is
`scene01_campus_stairs.py:309`, and it copies a **fixed 8-role subset** (`_ROLES`) precisely so that
"pulling in the full `sc.TEX` would make scene01 abort on textures it never binds". A new role is
therefore unreachable until a scene names it. The 33/33 proof in §3 is the formal statement of this.

**Zero-consumer check, with its two false positives stated so nobody re-runs it and worries.**
`grep -rn '"moss"' --include=*.py .` returns three lines outside the registration, and **none of them
reads the new role**:

| hit | what it actually is |
|---|---|
| `scene_common.py:547` | the path-token list that classes a prim as `veg` — the *existing* moss convention (spec §3.0 C-A2), not a `TEX` read |
| `scene09_ghat_riverfront.py:1109` | `M["moss"] = tex("plaza_light", …)` — a **scene-local material dict** key, bound to the `plaza_light` role with a green tint. Same convention, different namespace |
| `scene09_ghat_riverfront.py:1189, 1220` | reads of that same scene-local `M["moss"]` |

`sc.TEX["moss"]` and `tex_path("moss", …)` have **no reader anywhere in the tree.**

### 1.2 `BARE_SUBPRIMS` — the leaf-off registry (`scene_common.py:2328-2355`)

```python
BARE_SUBPRIMS = {
    "Trees/Gray_Birch.usd":      ("leaves",),
    "Trees/Elm_Sapling.usd":     ("leaves",),
    "Trees/Lombardy_Poplar.usd": ("leaves",),
}
```

Placed immediately after `SEASONAL_SUBPRIMS`, deliberately **as a second table rather than more rows
in the first one**: `SEASONAL_SUBPRIMS` is unconditional and strips its prims in all 33 scenes
(spec §3.4 caution 1). Leaf-off is a scene identity, not a library-wide season.

**Subprim paths verified by opening the USDs**, not assumed — usd-core 26.8, `/tmp/usdvenv/bin/python`:

| asset | `/Root` children | trunk tri | leaves tri | full zmax | trunk zmax | bare/full height | bare/full tri |
|---|---|---|---|---|---|---|---|
| `Trees/Gray_Birch.usd` | `Looks, trunk, leaves` | 118,417 | 138,208 | **3.3294 m** | **3.2960 m** | **99.00 %** | 46.1 % |
| `Trees/Elm_Sapling.usd` | `Looks, trunk, leaves` | 47,334 | 65,934 | **3.0867 m** | **3.0424 m** | **98.56 %** | 41.8 % |
| `Trees/Lombardy_Poplar.usd` | `Looks, trunk, leaves` | 101,130 | 316,776 | **13.6709 m** | **13.4221 m** | **98.18 %** | 24.2 % |

The prim is named **`leaves`, lower-case**, and it is a sibling `Mesh` of `trunk` — the branch
armature is inside `trunk`, which is why the bare form keeps 98–99 % of the canopy-top height.

**The four excluded species are excluded on measurement, not on the spec's word.** `Shumard_Oak` and
`Fraxinus` were re-opened this session: their `/Root` children are a trunk mesh plus **5–6 MASH
`PointInstancer`s**, and the leaves ride inside the same instancers as the branches, so deactivating
one removes the branch with it. `Scarlet_Oak` / `Black_Oak` are the same family and are not
registered.

### 1.3 `_deactivate_seasonal(..., table=None)` (`scene_common.py:2176`)

One appended default parameter. `table=None` → `SEASONAL_SUBPRIMS`, i.e. the sole existing call site
(`place_shrubs`, `scene_common.py:2922`) is untouched and its behaviour is bit-identical.
`BARE_SUBPRIMS` is passed only by the opt-in path below.

### 1.4 `build_tree(..., bare=False)` (`scene_common.py:2480`, body `:2531-2542`)

```python
if vx is not None:
    if bare:
        _off = _deactivate_seasonal(stage, f"{prefix}/Veg/Asset",
                                    rel, table=BARE_SUBPRIMS)
        if _off:
            LOOK_STATS["bare_tree"] = LOOK_STATS.get("bare_tree", 0) + 1
    # …then SetInstanceable(True)
```

**Ordering is the whole point** and it is spec §3.4 caution 2: once `SetInstanceable(True)` is
applied the descendants live in a shared prototype and per-instance edits are silently ignored, so a
deactivation written after it would look right in the source and do nothing on the stage. The block
sits **above** the instancing `try` and mirrors `place_shrubs`, which already documents the same trap.

A separate `LOOK_STATS["bare_tree"]` counter is incremented so scene10 can report bare trees
distinctly; `_deactivate_seasonal`'s own `seasonal_off` counter still moves too (shared mechanism).

**The kwarg is appended last**, so every existing `build_tree(` call site — positional or keyword —
is unaffected: **24 call sites across 17 of the 33 live scenes**, plus 5 more in `scenes/archive_v3/`
which is outside the 33 but still compiles. §6.2-K4(c) satisfied: signature-preserving, the
`build_tree` default-kwarg precedent. The 33/33 proof in §3 covers the 24 live call sites
empirically, not just by argument.

---

## 2. Functional test of the mechanism (real USD, GPU 0)

`bare=True` is dead code in this commit, so the 33/33 proof cannot exercise it. It was therefore
tested directly against a real `Usd.Stage` reproducing exactly the prim arithmetic `add_vegetation`
produces (`{prim_path}/Asset` holds the reference, so `/Root/leaves` → `{prim}/Asset/leaves`):

```
imported real scene_common with pxr venv
children of /Asset: ['Looks', 'trunk', 'leaves']
before: zmax 332.9409 (cm units)
deactivated: 1 | leaves active = False
after : zmax 329.5957 (cm units)
height retained: 99.00 %
default table (SEASONAL_SUBPRIMS) on a tree -> 0 | leaves active = True
unregistered species -> 0 (expected 0, silent no-op)
```

Three things are proven at once: the path arithmetic is right, the **default table is inert on trees**
(no accidental library-wide behaviour change), and an unregistered species is a **silent no-op**
rather than an exception.

---

## 3. The mandatory proof — full 33-scene prim-hash A/B against HEAD

### 3.1 Method (the `96968f3` method, with its stronger variant)

`scripts/geom_invariance_check.py` swaps `pxr`/`omni`/`carb`/`isaacsim` for a recording stub, runs
every scene's `main()` on the `NEGOBS_CAPTURE=1` path, and hashes the sorted prim inventory —
path, type, every xform op value, every shape attribute, every reference — with blake2b-128. It does
this in **three arms** (`MTL=0`, `MTL=1`, `V1=1`), so one run of the tool is **99 scene assemblies**.
GPU 0, disk writes 0.

**A frozen two-arm snapshot was used rather than a live before/after**, because this is a
multi-agent tree and a live baseline can be perturbed by another lane's commit landing mid-run
(the `w2d_translation_b3` pass-1 problem). Procedure:

1. one copy of the working tree (`cp -a` root `*.py`, `scenes/`, `scripts/`; `assets` symlinked;
   scene-dir symlinks preserved), then duplicated into `arm_a` / `arm_b` so the two arms start
   **provably identical**;
2. `arm_a/scene_common.py` ← `git show HEAD:scene_common.py`
   → sha256 `599c6eb5813d750ba280a409f092f8fe157a447c8ec1b0dda2a98d4d898510e2` (matches the HEAD blob);
   `arm_b/scene_common.py` ← the edited file
   → sha256 `77087dfb4fe2b572ff076ebb4d5b37fa64cb6a506055cb97a5692cea955b0b06` (matches the working tree);
3. `diff -r --no-dereference -q arm_a arm_b` reports **exactly one differing file: `scene_common.py`**;
4. the checker was run in each arm with `--baseline`, and the two JSONs compared.

### 3.2 Result — 99/99 hashes and 33/33 prim counts identical

```
scenes: 33
hash comparisons: 99 | mismatches: 0
prim-count comparisons: 33 | mismatches: 0
total prims (A/B): 29245 / 29245
VERDICT: 33/33 BYTE-IDENTICAL
```

Scene-row diff of the two rendered reports:

```
$ diff <(grep -E '^scene' geom_A.txt) <(grep -E '^scene' geom_B.txt)
33/33 SCENE ROWS IDENTICAL (empty diff)
```

The **only** difference anywhere in the two stdout captures is R-5's echo of the three
`LOOK_V1` compatibility-shim lines, whose **line numbers** moved 190-192 → 217-219 because the new
`TEX["moss"]` comment block sits above them, plus the `--baseline` output filename. Neither is a
scene row, a hash or a prim count:

```
5,7c5,7
<   · 허용 scene_common.py:190  LOOK_V1 = os.environ.get("NEGOBS_LOOK_V1", "") == "1"          # Umbrella (backwards compatible)
<   · 허용 scene_common.py:191  LOOK_MTL = os.environ.get("NEGOBS_LOOK_MTL", "1" if LOOK_V1 else "0") == "1"
<   · 허용 scene_common.py:192  LOOK_GEO = os.environ.get("NEGOBS_LOOK_GEO", "1" if LOOK_V1 else "0") == "1"
---
>   · 허용 scene_common.py:217  LOOK_V1 = os.environ.get("NEGOBS_LOOK_V1", "") == "1"          # Umbrella (backwards compatible)
>   · 허용 scene_common.py:218  LOOK_MTL = os.environ.get("NEGOBS_LOOK_MTL", "1" if LOOK_V1 else "0") == "1"
>   · 허용 scene_common.py:219  LOOK_GEO = os.environ.get("NEGOBS_LOOK_GEO", "1" if LOOK_V1 else "0") == "1"
57c57
< [기준선] 기록 → geom_A.json
---
> [기준선] 기록 → geom_B.json
```

### 3.3 The 33 rows, verbatim (arm A = HEAD; arm B produced these same 99 values)

| scene | prims | MTL=0 | MTL=1 | V1=1 |
|---|---:|---|---|---|
| scene01   |   354 | 8620cba36066ebfc | 8620cba36066ebfc | 8620cba36066ebfc |
| scene02   |   391 | 780686851e9692bd | 780686851e9692bd | 780686851e9692bd |
| scene03   |  1552 | d4e65cfd4be3f3bb | d4e65cfd4be3f3bb | d4e65cfd4be3f3bb |
| scene04   |   835 | fcbbde4a349c5cf2 | fcbbde4a349c5cf2 | fcbbde4a349c5cf2 |
| scene05   |  1235 | b94e95c067efe5e9 | b94e95c067efe5e9 | b94e95c067efe5e9 |
| scene06   |  1619 | 90f172dbd7aaa252 | 90f172dbd7aaa252 | 90f172dbd7aaa252 |
| scene07   |  1088 | 05ae7c1ec736c8c4 | 05ae7c1ec736c8c4 | 05ae7c1ec736c8c4 |
| scene08   |   688 | 72a2531085c94b60 | 72a2531085c94b60 | 72a2531085c94b60 |
| scene09   |   501 | 7b3a290111c1672b | 7b3a290111c1672b | 7b3a290111c1672b |
| scene10   |   888 | e5d4a6fe45804652 | e5d4a6fe45804652 | e5d4a6fe45804652 |
| scene11   |  2222 | 8db89915f7852c82 | 8db89915f7852c82 | 8db89915f7852c82 |
| scene12   |   803 | a22a1aefbaf4a5bc | a22a1aefbaf4a5bc | a22a1aefbaf4a5bc |
| scene13   |   495 | e700447b7d789a8d | e700447b7d789a8d | e700447b7d789a8d |
| scene14   |   860 | b162236b9c97e8b0 | b162236b9c97e8b0 | b162236b9c97e8b0 |
| scene15   |   433 | 3a0f63a201e5d914 | 3a0f63a201e5d914 | 3a0f63a201e5d914 |
| scene16   |   400 | 0ce01615f0632d9b | 0ce01615f0632d9b | 0ce01615f0632d9b |
| scene17   |   974 | 23a7a09eac51f449 | 23a7a09eac51f449 | 23a7a09eac51f449 |
| scene18   |  1959 | e61eee29ce752384 | e61eee29ce752384 | e61eee29ce752384 |
| scene19   |   284 | f874d81296d1e8ff | f874d81296d1e8ff | f874d81296d1e8ff |
| scene20   |   479 | 501207c8839f744d | 501207c8839f744d | 501207c8839f744d |
| scene21   |   527 | a71d79ccae5d8aef | a71d79ccae5d8aef | a71d79ccae5d8aef |
| sceneC1   |   367 | e821aa7d1d60e8a5 | e821aa7d1d60e8a5 | e821aa7d1d60e8a5 |
| sceneC2   |  3940 | c1ea9b03965f6877 | c1ea9b03965f6877 | c1ea9b03965f6877 |
| sceneC4   |   636 | c6cf17e5601c8083 | c6cf17e5601c8083 | c6cf17e5601c8083 |
| sceneD1   |   341 | f13ec42a2b4212a2 | f13ec42a2b4212a2 | f13ec42a2b4212a2 |
| sceneD2   |   236 | 68845547eedef740 | 68845547eedef740 | 68845547eedef740 |
| sceneD3   |   715 | 2989f9ae1e2a1412 | 2989f9ae1e2a1412 | 2989f9ae1e2a1412 |
| sceneD4   |   314 | b7ac84036ce9d32c | b7ac84036ce9d32c | b7ac84036ce9d32c |
| sceneN1   |   529 | 4a66c18e6ebcb93a | 4a66c18e6ebcb93a | 4a66c18e6ebcb93a |
| sceneN2   |   600 | a652946c398eb02e | a652946c398eb02e | a652946c398eb02e |
| sceneN3   |   666 | 071577e88113060d | 071577e88113060d | 071577e88113060d |
| sceneN4   |  1241 | 8e5a1971f0578bfa | 8e5a1971f0578bfa | 8e5a1971f0578bfa |
| sceneN5   |  1073 | 6e5c4aea6326ba5d | 6e5c4aea6326ba5d | 6e5c4aea6326ba5d |

**Σ prims = 29,245**, both arms. Hash column widths are the tool's full 16-hex digest (the console
table prints the first 8).

**Consequence, and it is the ledger consequence**: zero geometry moved, so **no GT row is owed**
(`gt_changes_w3.md` §0-1 is triggered by a moved walked surface / drop edge / hazard box / element
AABB — none exist here). This is not a `PROOF-ONLY` row either: `PROOF-ONLY` is for a *designed*
GT-invariant geometry change, and this commit changes no geometry at all.

---

## 4. §6.1 verification floor

### 4.1 `py_compile`

```
python3 -m py_compile scene_common.py     → exit 0
```

### 4.2 `NEGOBS_SMOKE=1` per touched scene

**Vacuous: this commit touches zero scene files.** `git status --short` at commit time shows exactly
`M scene_common.py`. Stated plainly rather than skipped silently, and with a substitute, because
`scene_common` is a 33-scene dependency:

- the §3 harness executed **every scene's `main()` 3× per arm = 99 assemblies per arm, 198 in total**,
  which is a superset of what a smoke run proves about assembly, and it did so on **both** the HEAD
  and the edited module;
- the edited module was additionally imported under a **real `pxr`** (usd-core 26.8) in §2, so the
  new dict literal and the new default kwargs are exercised outside the stub harness as well.

No GPU work was performed by this task, per the ruling's *"No renders"*.

### 4.3 `geom_invariance_check.py` — on the live tree

```
GEOM_LIVE_EXIT=0
[R-5] 스캔 40 파일 · 허용 3 행(호환 심) · 위반 0 건  → ✔ PASS
[R-4] MTL 0/1 해시 일치 33/33  ✔ PASS
[R-6] V1=1 3자 일치   33/33  ✔ PASS
```

### 4.4 `placement_lint.py` — the delta, documented

```
python3 scripts/placement_lint.py --scenes all --rules Docs/briefs/placement_rules_v1.yaml
```

Run in **both frozen arms** so the delta is attributable to `scene_common.py` alone:

```
diff lint_arm_a.txt lint_arm_b.txt   → EMPTY (byte-identical, 1,819 lines)
```

**My delta is 0 — every check, every scene, every row.** The live-tree run is byte-identical to
`arm_b`, confirming no other lane moved the tree between the snapshot and the commit.

Tree state at this commit, recorded so the next lane can attribute movement correctly (this is the
**pre-existing** level, not a level this commit created):

| check | ERROR | WARN | BLOCK | INFO |
|---|---:|---:|---:|---:|
| LINT-1 | 0 | 26 | 0 | 0 |
| LINT-2 | 0 | 42 | 0 | 1 |
| LINT-3 | 0 | 26 | 0 | 0 |
| LINT-4 | 0 | 27 | 0 | 0 |
| LINT-4b | 49 | 0 | 0 | 0 |
| LINT-5 | 0 | 32 | 0 | 0 |
| LINT-6 | 25 | 49 | 0 | 0 |
| LINT-7 | 0 | 117 | 0 | 1 |
| LINT-7-static | 5 | 1 | 0 | 0 |
| LINT-9 | 0 | 0 | 29 | 0 |
| LINT-10 | 0 | 6 | 0 | 0 |
| **total** | **70** | **246** | **29** | **2** |

Exit code 1 in both arms, i.e. the tool's normal "errors exist" exit, identical A and B.

---

## 5. What the next lane must know

1. **`bare=True` alone does not produce a leaf-off scene.** `build_tree` draws its species from
   `VEG_TREES` by coordinate hash, and `VEG_TREES` holds five rows — `Elm_Sapling`, `Shumard_Oak`,
   `Chinese_Juniper`, `White_Pine`, `Yellow_Pine`. **Only one of the three bare-capable assets
   (`Elm_Sapling`, weight 4 of 11) is in that pool**; `Gray_Birch` and `Lombardy_Poplar` are on disk
   but unpooled. So `bare=True` on a stock `build_tree` call strips leaves on ~36 % of the draw by
   weight and leaves the rest green. A uniformly leaf-off canopy needs a **species selector** — the
   planned K4(b) `species=` kwarg (spec §1.B-2 row B4) — or scene10 calling `add_vegetation`
   directly with its own asset choice. **This is deliberately not solved here**: a species selector
   is a second mechanism, `species=` is already assigned to K4(b), and the ruling authorised one
   micro-commit doing two named things. It is flagged as the one real gap between this commit and
   scene10's need.
2. **`bare=` is a no-op on the procedural blob fallback** (`LOOK_GEO=0` or assets missing). The blob
   canopy is not a leaf asset; suppressing it would be a geometry change and is out of scope.
3. **Height bookkeeping.** `add_vegetation` scales by `target_h / native_h` and `VEG_TREES` carries
   the **leafed** zmax, so a bare tree lands 0.8–1.8 % short of the requested height — inside the
   ±8 % per-instance jitter `build_tree` already applies. No compensation was added; adding one would
   change the scale arithmetic for the leafed path too.
4. **`TEX["moss"]`'s normal map is GL/EXR, not DX/JPG** (§1.1 caution 2). scene07 is its intended
   first consumer; it must decide green-flip vs `nor`-omit rather than copy a neighbouring row.
5. **Triangle head-room, for the budget line of whoever enables it**: bare forms are 46.1 % /
   41.8 % / 24.2 % of the leafed triangle count (Gray_Birch / Elm_Sapling / Lombardy_Poplar). Per
   §12-14 the budget is instanceability, not triangles — and instancing is untouched here, it simply
   now happens **after** the deactivation instead of being the only thing in the block.

---

## 6. Scope statement

Per the freeze and §8.R's scope guard: this task changed **`scene_common.py` only**, plus this
report. No scene file, no kit module, no `ground_kit`, no `assets/`, no `look_check/` round, no
`scripts/rounds/`, no GT ledger row, no render, no GPU lock taken. `sceneC2` hygiene (S3-1) was not
touched — it is deferred. No human and no vehicle was added anywhere, in any form.

**Evidence artefacts** (scratchpad, not committed):
`k4m_ab/arm_a/geom_A.json` · `k4m_ab/arm_b/geom_B.json` · `k4m_ab/geom_A.txt` · `k4m_ab/geom_B.txt` ·
`k4m_ab/geom_live.txt` · `k4m_ab/lint_arm_a.txt` · `k4m_ab/lint_arm_b.txt` · `k4m_ab/lint_live.txt`.
