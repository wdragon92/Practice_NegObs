# -*- coding: utf-8 -*-
"""urban_kit.py — the single urban-asset loader for W3 (WP-T4).

Written 2026-07-30 · target: the 33 NegObs scenes (21 main + 12 batch 1) ·
Isaac Sim 4.5 / USD · spec `Docs/briefs/w3_execution_spec_v1.md` §3.4 / §4.1 / §1.11.

## Why this file exists

`w3_execution_spec_v1.md` §3.4 lists **seven integration quirks that every asset row must
obey**. Eight scene work packages and five kit work packages consume those rows. If each of
them re-implements the quirks, the library gets thirteen slightly different answers to
"where is grade?" and "which file do I reference?". This module is the one place they are
implemented, and the one place the evidence for each of them is recorded.

    from urban_kit import add_urban_asset
    add_urban_asset(stage, f"{ROOT}/Bollard_00", "bollard_01",
                    pos_m=(-8.4, -2.6, 0.0), yaw_deg=0.0, scene="01")

## The seven quirks and where each is implemented

| # | §3.4 quirk | Implemented by |
|---|---|---|
| 1 | No Z lift on the 10 mid-tier buildings; per-asset `z_advice` | `_z_policy()` + `Z_MODE` |
| 2 | Reference `_inst.usd`, never the wrapper | `resolve_usd()` |
| 3 | `mpu` per asset (1.0 except the 8 far-tier at 0.01) | `add_urban_asset()` unit scale |
| 4 | Parent-Xform placement — the referenced root already owns T/R/S | `add_urban_asset()` |
| 5 | 240 dead `materials/textures/*.png` references are normal | documented; never resolved here |
| 6 | Mirror `nv_content/` verbatim — 3 cross-folder sublayer aliases | `resolve_usd()` + `ALIAS_OF` |
| 7 | Asset backdrops must still be dressed with `facade_kit` | not this file's job — K3 owns it |

plus the ruled far-tier albedo override (§1.11) in `_bind_far_override()`, and — added by
**W3 Lane-1 T4** — the **MDL package repair** in `ensure_mdl_package()` (section [1b]):
the procured `nv_core/materials/` package is missing `baking_annotations.mdl`, so
`SimPBR.mdl` does not compile and **every** urban asset renders flat red. It is repaired
here rather than in the asset tree because `assets/urban/` is gitignored, and here rather
than per scene because scene07 and scene10 each had to invent their own workaround before
this existed (`w3_s07_rebuild_v1.md` §5.1 · `w3_s10_rebuild_v1.md` §5.2).

## Conventions

- **Z-up, metres.** Scene stages are `metersPerUnit = 1.0` (`scene_common.py:900-903`).
- **Do not import `scene_common`.** Same rule as `infra_kit` / `ground_kit`: this module is
  imported *by* scene code and by kits, so importing back would be circular. `pxr` is imported
  lazily inside functions so the module can be introspected on a CPU-only interpreter.
- **The manifest is read-only.** `assets/urban_manifest_w3.json`, `assets/download_urban.py`
  and `assets/verify_urban.py` belong to the procurement agent (spec §0 scope discipline).
  Every disagreement with the manifest is recorded in
  `Docs/reports/w3_asset_readjudication_v1.md`, never patched into their files.
- **No number without a tag.** `[measured]` = reproduced here on usd-core 26.8 by
  `python3 urban_kit.py --self-check`; `[manifest]` = read from the procurement manifest;
  `[ruled 07-30]` = a supervisor ruling relayed by the execution spec.

## What this module deliberately does NOT do

- It does not place anything by itself and owns no scene content (§4.1: "no scene wiring").
- It does not decide *which* asset a scene wants — §3.3's role tables are advisory here
  (`SIGN_ARCHETYPE`) and the owning S-WP has the last word.
- It does not dress an asset backdrop (quirk 7). That is K3's `facade_kit` attachment layer.
"""

import os
import json

# ===========================================================================
# [0] Paths
# ===========================================================================
_HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(_HERE, "assets")
MANIFEST_PATH = os.path.join(ASSETS_DIR, "urban_manifest_w3.json")
URBAN_DIR = os.path.join(ASSETS_DIR, "urban")          # NVIDIA, redistribution forbidden
CC0_DIR = os.path.join(ASSETS_DIR, "urban_cc0")        # Poly Haven, CC0 1.0

# Where shared override materials live. Scenes put their materials under `/World/Looks/*`
# (`scene03:686-707`), so the far-tier overrides join them instead of being duplicated once
# per placement.
OVERRIDE_LOOKS_SCOPE = "/World/Looks/UrbanFar"

# OmniPBR is the project's material MDL (`scene_common.py:35-37`). Repeated here rather than
# imported so this module stays independent of `scene_common`.
OMNIPBR_PATH = os.path.expanduser(
    "~/miniconda3/envs/env_isaaclab/lib/python3.10/site-packages/"
    "omni/mdl/core/Base/OmniPBR.mdl")


class UrbanAssetError(Exception):
    """Raised when a row may not be loaded: unknown id, missing file, FAIL verdict,
    a banned path, or a season/era scope violation. Never returns None silently —
    a scene that silently loses an asset renders as a hole nobody notices."""


# ===========================================================================
# [1] Manifest access (read-only)
# ===========================================================================
_MANIFEST = None
_INDEX = None


def manifest():
    """The procurement manifest, loaded once. Read-only — this module never writes it."""
    global _MANIFEST
    if _MANIFEST is None:
        with open(MANIFEST_PATH, "r", encoding="utf-8") as fh:
            _MANIFEST = json.load(fh)
    return _MANIFEST


def _index():
    """`id -> raw manifest entry` over both supplier lists.

    The manifest keeps NVIDIA rows in `assets` and Poly Haven rows in `polyhaven`, with
    different key schemas (`keys[].key` vs `keys[].rel`). Callers should never have to know.
    """
    global _INDEX
    if _INDEX is None:
        m = manifest()
        idx = {}
        for e in m.get("assets", []):
            idx[e["id"]] = e
        for e in m.get("polyhaven", []):
            idx[e["id"]] = e
        _INDEX = idx
    return _INDEX


def ids(group=None, verdict=None):
    """Asset ids, optionally filtered by manifest `group` / `verdict`.

    Groups `[manifest]`: signs_kr 162 (156 signs + 6 material libraries) · midground 17 ·
    props 13 · poles 12 · reopened 12 · buildings_mid 11 · roadmarks_kr 9 · _core 9 ·
    buildings_far 8 · rocks_gap 3 · water 2 · polyhaven_cc0 33.
    """
    out = []
    for aid, e in _index().items():
        if group is not None and e.get("group") != group:
            continue
        if verdict is not None and e.get("verdict") != verdict:
            continue
        out.append(aid)
    return sorted(out)


# ===========================================================================
# [1b] MDL package repair — the `.::baking_annotations` defect
#
# ## The defect, measured
#
# Every `nv_content` asset binds a material whose `info:mdl:sourceAsset` is
# `assets/urban/nv_core/materials/SimPBR.mdl`. That module opens with
#
#     import  .::SimPBR_Model::*;
#     using   .::baking_annotations import *;
#
# and `baking_annotations.mdl` **is not in the procured tree**. The renderer therefore
# reports, once per material `[measured — this session, t4 probe]`:
#
#     C120 could not find module '.::baking_annotations' in module path
#     C121 imported module '::…::SimPBR_Model' contains errors
#     Failed to create MDL shade node for prim '/__Prototype_1/Looks/…'
#
# and every urban asset falls back to the shader default — **flat saturated red**
# (11.8 % of the frame at d2 in the probe). scene07 and scene10 both hit it and both
# worked around it scene-side with `instanceable=False` + a per-mesh rebind.
#
# ## Why the fix has to materialise a file, and cannot be a search path
#
# `.::x` is a **relative** MDL module path: the MDL resolver looks for it only in the
# package directory of the importing module. Re-running the probe with
# `MDL_USER_PATH` **and** `MDL_SYSTEM_PATH` pointed at the Kit core `Base` directory
# (which does contain `baking_annotations.mdl`) leaves all 8 `C120` errors in place
# `[measured]`. A search path fixes absolute imports; it cannot fix this one.
# The module has to exist **next to `SimPBR.mdl`**.
#
# ## Why it lives in the loader and not in the asset tree
#
# `assets/urban/` is gitignored (`.gitignore:52` — NVIDIA, redistribution forbidden), so a
# file copied there by hand is not a repair anybody else receives: the next clone runs
# `assets/download_urban.py` and gets the same broken package back. The durable repair is
# therefore **here**, in the one module every consumer already goes through, and it heals
# the tree from the local Kit installation (the same installation `OMNIPBR_PATH` already
# depends on) instead of redistributing NVIDIA files through the repo.
#
# Root cause, for the record: `assets/download_urban.py`'s `CORE_MDL` list enumerates the
# nine `SimPBR*.mdl` siblings by hand — its own comment says internal MDL `import`s are
# invisible to `--resolve` — and misses `baking_annotations` (needed by SimPBR ·
# SimPBR_Model · SimPBR_Buildings · SimPBR_RoadPaint) and `OmniUe4Function` / `OmniUe4Base`
# (needed by SimPBR_Road). That file belongs to the procurement agent and is read-only for
# W3 (spec §0), so the manifest row is **reported**, never patched — see
# `Docs/reports/w3_k1t4_v1.md`.
# ===========================================================================
MDL_DIR = os.path.join(URBAN_DIR, "nv_core", "materials")

# Where a missing sibling module is fetched from: the Kit core MDL tree of the *local*
# runtime. `OMNIPBR_PATH` already pins that tree, so the root is derived from it rather
# than hard-coded a second time. `NEGOBS_MDL_CORE` overrides it on a machine that keeps
# Kit somewhere else.
MDL_CORE_ROOT = os.environ.get(
    "NEGOBS_MDL_CORE",
    os.path.dirname(os.path.dirname(OMNIPBR_PATH)))     # .../omni/mdl/core

_MDL_COMMENT = None
_MDL_IMPORT = None
_MDL_FOUND = {}
_MDL_REPAIRED = None


def _mdl_rel_imports(text):
    """The relative sibling modules an MDL source imports: `.::Name` in either
    `import .::Name::*;` or `using .::Name import *;` form.

    Comments are stripped first — a copyright block that mentions an import must not
    manufacture a dependency. `..::Name` (parent package) is reported separately because
    this repair cannot satisfy it: it would have to invent a package layout.
    """
    import re
    global _MDL_COMMENT, _MDL_IMPORT
    if _MDL_COMMENT is None:
        _MDL_COMMENT = re.compile(r"/\*.*?\*/|//[^\n]*", re.S)
        _MDL_IMPORT = re.compile(
            r"(?:^|\n)\s*(?:import|using)\s+(\.{1,2})::([A-Za-z_]\w*)")
    src = _MDL_COMMENT.sub(" ", text)
    here, parent = [], []
    for dots, name in _MDL_IMPORT.findall(src):
        (here if dots == "." else parent).append(name)
    return sorted(set(here)), sorted(set(parent))


def _find_core_mdl(name):
    """Absolute path of `<name>.mdl` in the local Kit core MDL tree, or None.

    The tree is small (~60 files over Base / Ue4 / Volume / …) and the walk is cached, so
    a scene that places forty assets pays for it once.
    """
    if name in _MDL_FOUND:
        return _MDL_FOUND[name]
    hit = None
    for root, _dirs, files in os.walk(MDL_CORE_ROOT):
        if name + ".mdl" in files:
            hit = os.path.join(root, name + ".mdl")
            break
    _MDL_FOUND[name] = hit
    return hit


def ensure_mdl_package(mdl_dir=None, verbose=False):
    """Complete `assets/urban/nv_core/materials` so its MDL modules compile.

    Idempotent, cached, and **never raises**: a urban asset with a broken material is a
    look defect, but a loader that dies on a read-only asset tree is a dead scene. Returns
    a report dict `{"added": [...], "missing": [...], "unsatisfiable": [...], "ok": bool}`.

    Called automatically by `add_urban_asset` before the first reference is composed, so
    no scene and no kit has to know this defect exists. Call it directly when a stage
    references an urban asset without going through `add_urban_asset`.
    """
    global _MDL_REPAIRED
    if _MDL_REPAIRED is not None and mdl_dir is None:
        return _MDL_REPAIRED
    d = mdl_dir or MDL_DIR
    rep = dict(added=[], missing=[], unsatisfiable=[], ok=True, dir=d)
    if not os.path.isdir(d):
        rep["ok"] = False
        rep["missing"].append(f"(materials dir absent: {d})")
        if mdl_dir is None:
            _MDL_REPAIRED = rep
        return rep

    # Breadth-first: a module copied in may itself import siblings (OmniUe4Function does).
    seen = set()
    queue = sorted(f for f in os.listdir(d) if f.endswith(".mdl"))
    while queue:
        fname = queue.pop(0)
        if fname in seen:
            continue
        seen.add(fname)
        try:
            with open(os.path.join(d, fname), "r", encoding="utf-8",
                      errors="replace") as fh:
                here, parent = _mdl_rel_imports(fh.read())
        except OSError as ex:
            rep["ok"] = False
            rep["unsatisfiable"].append(f"{fname}: unreadable ({ex})")
            continue
        for nm in parent:
            rep["unsatisfiable"].append(f"{fname}: '..::{nm}' (parent package)")
            rep["ok"] = False
        for nm in here:
            tgt = os.path.join(d, nm + ".mdl")
            if os.path.isfile(tgt):
                queue.append(nm + ".mdl")
                continue
            src = _find_core_mdl(nm)
            if src is None:
                rep["missing"].append(nm)
                rep["ok"] = False
                continue
            try:
                # Atomic: write beside the target and rename. Round runners drive 33
                # scenes through one asset tree, and a half-written `.mdl` read by the
                # next process would look exactly like the defect being repaired.
                import shutil
                tmp = tgt + f".tmp{os.getpid()}"
                shutil.copyfile(src, tmp)
                os.replace(tmp, tgt)
            except OSError as ex:
                rep["unsatisfiable"].append(f"{nm}: copy failed ({ex})")
                rep["ok"] = False
                continue
            rep["added"].append(nm)
            queue.append(nm + ".mdl")

    if rep["added"] and verbose:
        print(f"[urban_kit][mdl] {d} 보완 {len(rep['added'])}건: "
              f"{', '.join(rep['added'])} ← {MDL_CORE_ROOT}")
    if not rep["ok"]:
        _warn_once("mdl:incomplete",
                   f"[urban_kit][경고] MDL 패키지 미완성 — 미해결 {rep['missing']} "
                   f"{rep['unsatisfiable']}. 도시 자산이 셰이더 폴백(단색 적색)으로 "
                   f"렌더될 수 있다. Kit 코어 MDL 경로를 NEGOBS_MDL_CORE 로 지정하거나 "
                   f"조달 담당에게 download_urban.CORE_MDL 보완을 요청하라.")
    if mdl_dir is None:
        _MDL_REPAIRED = rep
    return rep


# ===========================================================================
# [2] Guards — what may not be loaded, and why
# ===========================================================================
# The procurement guard lives in the procurement agent's files and stays there
# (`[ruled 07-30]` §1.10, §12-17: "do not edit the procurement agent's guard"). This is an
# independent, loader-side refusal so that a wrong path cannot reach a stage even if it is
# hand-written into a scene. Self-checked against all 2,323 procured files: 0 hits `[measured]`.
BANNED_SUBSTRINGS = tuple(manifest().get("banned_substrings", ()))

# `veg_shrub_hedge_round_01` binds a dry straw/orange atlas over 74.6 % of its triangles plus a
# fruit atlas → season FAIL (C-21). Spec §12-7: "do not wire it". The loader refuses it outright
# rather than leaving the decision to thirteen call sites.
REFUSED_IDS = ("veg_shrub_hedge_round_01",)

# Scene-scoped rows (§3.3 cautions). `scene=` is optional; when it is given the scope is
# enforced, when it is omitted a one-line warning is printed. Both beat a silent breach.
#   - dry-leaf scatter measures green 0.000 / orange 0.343 / red 0.655 → leaf scenes only.
#   - Type-III barricades are temporary-works objects — exactly the class ruling 1.6 deleted
#     from scene08. Admissible only on D2's construction slab.
SCENE_SCOPE = {}
for _i in ("sct_debris_leaves_dry_01", "sct_debris_leaves_dry_02",
           "sct_debris_leaves_dry_03", "sct_debris_leaves_dry_04"):
    SCENE_SCOPE[_i] = ("C2", "07", "10", "D3")
for _i in ("traf_barrier_mov_type3_4feet_stripe_orange_white_01",
           "traf_barrier_mov_type3_6feet_stripe_orange_white_01",
           "traf_barrier_mov_type3_8feet_stripe_orange_white_01"):
    SCENE_SCOPE[_i] = ("D2",)
del _i


def _check_banned(path):
    for b in BANNED_SUBSTRINGS:
        if b and b in path:
            raise UrbanAssetError(
                f"banned path substring {b!r} in {path} — declined supplier or "
                f"Limited Use root (manifest.banned_substrings)")


# ===========================================================================
# [3] Quirk 1 — the Z origin
#
# §3.4-1 says: "No Z lift on the 10 mid-tier buildings (C-18). Use the manifest's per-asset
# `z_advice`; the 28 props that genuinely need `-zmin` are listed there."
#
# **The manifest's `z_advice` field contains no such rows.** `[measured]` Its four branches
# (`assets/verify_urban.py:352-366`) are driven by `tri_below_grade_frac`, and that fraction is
# computed **per mesh, all-or-nothing**: `below = sum(t for zlo, zhi, t in mesh_z if zhi < -0.05)`
# — a mesh counts only when its *top* is below grade. For every single-mesh prop the fraction is
# structurally 0.0, so the "**Z 보정 금지**" branch fires for `bollard_01`, `utility_cover_01`,
# `luminaire_head04` and 26 others regardless of the truth. The distribution of the field is
# therefore: 227 "no correction needed" · 46 "correction forbidden" · 3 "attachment" · **0 "lift"**
# `[measured]`, against PROC §5.1's prose row that names 28 lift candidates.
#
# So the two authorities the spec cites disagree, and neither can be applied blind:
#   - PROC §5.1's prose would lift `utility_cover_01` by +0.327 m — but that asset's origin is its
#     *top* face (zmax +0.028, zmin -0.327 `[measured]`); it is a vault whose cover sits at grade.
#     Lifting it hoists a utility vault out of the road.
#   - the `z_advice` field would leave `old_tyre`, `tree_stump_01/02`, `rock_moss_set_01` and the
#     other centre-origin Poly Haven scans half-buried — the exact defect `scene_common.VEG_ROCKS`
#     already documents for the S3 rock family.
#
# The loader therefore does what the spec's own bar demands ("a row whose sample does not exist
# yet is parked, not guessed"):
#   - default `z_mode='grade'` — local z = 0 is placed at the caller's ground z, no lift. This is
#     the ruled behaviour for the mid tier (C-18) and is trivially right for the 227 rows whose
#     zmin is already ~0.
#   - `z_mode='base'` — lift by `-zmin` so the lowest geometry touches the caller's ground z.
#   - `z_mode='attach'` — refuse to auto-ground; the caller must place the prim on its parent
#     asset. Set from the manifest for the 3 rows whose zmin is positive.
#   - every row whose origin is measurably inside its own body prints a one-line advisory naming
#     both numbers and the alternative call, once per process. Nothing silent, nothing guessed.
#
# `Z_REVIEW` is that advisory table: `id -> (frac_of_triangles_below_local_z0, zmin_m)`.
# `[measured 2026-07-30, usd-core 26.8]` — per-triangle centroid z under the composed
# local-to-world transform, instance proxies expanded. `python3 urban_kit.py --self-check`
# recomputes every row and fails on any drift.
# ===========================================================================
Z_REVIEW = {
    # id                              frac<0   zmin_m    class as measured
    "luminaire_head02":              (0.8628, -0.2067),  # head hangs below its mount point
    "luminaire_head04":              (0.7809, -0.4621),
    "luminaire_head_01":             (0.7630, -0.0908),
    "luminaire_head01":              (0.7474, -0.1349),
    "security_light":                (0.7215, -0.3593),  # wall-mounted, origin at the bracket
    "luminaire_head03":              (0.6562, -0.0597),
    "sidewalk_debris_02":            (0.5665, -0.0272),  # centre origin
    "rock_moss_set_01":              (0.5238, -0.6610),  # centre origin (VEG_ROCKS class)
    "old_tyre":                      (0.5000, -0.3000),  # centre origin
    "tree_stump_02":                 (0.4753, -0.2335),
    "tree_stump_01":                 (0.3887, -0.1930),
    "power_box_01":                  (0.3778, -0.2516),
    "luminaire_arm_6ft":             (0.2809, -0.0770),  # bracket arm, mounts on a pole
    "luminaire_arm_8ft":             (0.2638, -0.0770),
    "luminaire_arm_10ft":            (0.2616, -0.0770),
    "modular_fire_escape":           (0.2455, -3.6486),
    "utility_cover_01":              (0.2429, -0.3268),  # cover at grade, vault below — keep
    "sidewalk_debris_01":            (0.2242, -0.0341),
    "stone_01":                      (0.1936, -0.0146),
    "lateral_sea_marker":            (0.1750, -1.2818),
    "veg_shrub_hedge_round_01":      (0.1263, -0.0477),  # refused anyway (season FAIL)
    "ocean_buoy":                    (0.1118, -0.8094),
    "bikerack_metal03":              (0.1074, -0.0288),
    "rock_moss_set_02":              (0.0935, -0.3152),
    "modular_wooden_pier":           (0.0564, -0.9941),
    "typical_building_08":           (0.0512, -5.0000),  # mid tier — no lift `[ruled]` C-18
    "strt_fxd_bollard_05":           (0.0479, -0.0539),  # buried anchor stem
    "bollard_01":                    (0.0343, -0.1826),  # buried anchor stem
    "streetlamp_01":                 (0.0303, -0.3849),  # base plate below grade
    "exterior_aircon_unit":          (0.0200, -0.3201),
    "typical_building_18":           (0.0161, -1.0796),
    "typical_building_11":           (0.0137, -10.3403),
    "pole_fxd_pedestrian_signage_01": (0.0134, -0.1216),
    "typical_building_109":          (0.0108, -5.0031),
    "veg_shrub_hedge_yellow_01":     (0.0107, -0.0629),
    "streetlamp_02":                 (0.0086, -1.0000),
    "typical_building_07":           (0.0079, -5.0000),
    "strt_fxd_bollard_01":           (0.0062, -0.0186),
    "typical_building_13":           (0.0039, -6.1396),
    "typical_building_12":           (0.0028, -4.0000),
    "typical_building_106":          (0.0023, -5.0000),
    "modular_urban_apartments_facade": (0.0018, -2.0000),
    "typical_building_10":           (0.0011, -7.9038),
    "typical_building_03":           (0.0011, -5.0000),
    "streetlamp_03":                 (0.0000, -0.1206),
}

# A row is worth an advisory when a non-trivial share of its body is below its own origin.
# 0.15 is chosen to sit above every mid-tier building `[measured max 0.0512]` and above every
# buried-anchor row (bollards / streetlamp base plates, max 0.0479), and below the centre-origin
# scans it is meant to catch (min 0.1750). It gates a *message*, never a geometry change.
Z_REVIEW_FRAC = 0.15

# Rows whose origin sits above their base: they mount on a parent asset and must never be
# auto-grounded. Taken from the manifest's own "**부속물**" branch `[manifest]`.
#   typical_building_08_railings +11.000 m · ac_unit_06 +0.149 m · bridge_01 +0.025 m
Z_ATTACH_IDS = ("typical_building_08_railings", "ac_unit_06", "bridge_01")

# `[ruled 07-30]` C-18 / §3.4-1: the whole mid tier is grade-locked. Named as a group so that a
# future manifest re-run cannot quietly re-open it.
Z_GRADE_LOCKED_GROUPS = ("buildings_mid", "buildings_far", "signs_kr", "roadmarks_kr")


# ===========================================================================
# [4] The far-tier albedo override — `[ruled 07-30]` §1.11
#
# The ruling: "MATERIAL OVERRIDE — scale the albedo into the <= 0.55 project band, keep the
# textures — rather than declining the tier. Verify at the render gate."
#
# Its premise is the raw texture measurement (PROC §6.2): `house_wall_001_Diffuse.png`
# linear albedo 0.874 with 99.6 % of pixels over linear 0.8, and `concrete_014_Diffuse.png`
# 0.969 / 98.7 %. Both reproduce here exactly `[measured]`.
#
# **What the premise omits is that the shipped materials already carry a `diffuse_tint`.**
# `SimPBR_Model.mdl:91` is a literal multiply — `base_color = multiply_colors(diffuse_color,
# diffuse_tint, 1.0)` — so the albedo the renderer sees is texture x tint. Measured across all
# eight far-tier buildings and all 7 materials `[measured]`:
#
#   MI_Building_Wall_03  house_wall_001 0.874 x tint 0.611 = **0.534**   <- the tier's maximum
#   MI_Building_Wall_01  house_wall_001 0.874 x tint 0.599 = 0.524
#   MI_Building_Wall_02  house_wall_001 0.874 x tint 0.531 = 0.464
#   MI_Building_Wall_05  house_wall_001 0.874 x tint 0.446 = 0.390
#   MI_Building_Walkway_01 concrete_014 0.969 x tint 0.371 = 0.359
#   MI_Building_Roof_01  concrete_006  0.402 x tint 0.620 = 0.249
#   MI_Window_Interior_01/02 plastic_base 0.841 x tint 0.022 / 0.165 = 0.019 / 0.138
#   MI_Building_Wall_04  brick_wall_001 0.074 x tint 1.000 = 0.074
#
# i.e. the tier is **already inside the <= 0.55 band, at 0.534 worst case**, and the albedo
# scale factor the ruling asks for computes to 1.000 on every material. The override is
# retained and is not vacuous for a second, independently measured reason: every SimPBR
# material in the tier authors `metallic_constant = 1.0` with `metallic_texture_influence = 0.0`,
# and `SimPBR.mdl:792` evaluates `metallic = lerp(metallic_constant, ORM.z, influence)` = **1.0**
# `[measured]`. The eight skyline buildings therefore render as fully metallic walls. Binding an
# override material re-authors that response to a dielectric, which is what a plaster/concrete
# facade is. The mid tier does **not** share the defect (`metallic_constant` is unauthored on all
# ten, MDL default 0.0 `[measured]`) — this is a far-tier-only quirk.
#
# Both arms are exposed so the render gate can A/B them, as §1.11 requires (re-gated on B45/B30,
# not only B-HZ): `far_override="auto"` (default) and `far_override="off"`.
# ===========================================================================
FAR_ALBEDO_CAP = 0.55            # the project band `[ruled 07-30]` §1.11

# Mean linear-Rec.709 albedo of the far tier's diffuse maps. `[measured 2026-07-30, PIL]`,
# reproducing `assets/urban_manifest_w3.json` `pixels[].albedo_lin` to 3 decimals.
FAR_TEX_ALBEDO = {
    "house_wall_001_Diffuse.png":  0.874,   # 99.58 % of pixels over linear 0.8
    "concrete_014_Diffuse.png":    0.969,   # 99.41 %
    "plastic_base_Diffuse.png":    0.841,   # 99.15 % — never flagged by the near-white gate
    "concrete_006_Diffuse.png":    0.402,   # 0.15 %
    "brick_wall_001_Diffuse.png":  0.074,   # 0.00 %
}

# A metal BSDF has no diffuse lobe, so an albedo cap on a metallic material is meaningless.
# The override re-authors the far tier as a dielectric; see the block comment above.
FAR_OVERRIDE_METALLIC = 0.0


def _luma(c):
    """Rec.709 luminance of a linear colour triple. MDL colours are linear, so a
    `diffuse_tint` value multiplies the decoded texture directly."""
    return 0.2126 * float(c[0]) + 0.7152 * float(c[1]) + 0.0722 * float(c[2])


# ===========================================================================
# [5] Advisory role table — §3.3 N-A1, copied so eight WPs do not re-derive it
#
# Advisory only: the owning S-WP has the last word on what its scene carries. Reproduced
# verbatim from spec §3.3 so that the archetype assignment is at least *consistent* across
# the eight scene packages.
# ===========================================================================
SIGN_ARCHETYPE = {
    "A_plaza":      dict(scenes=("01", "08", "14", "21"),
                         signs=("sign_kr324", "sign_kr323")),      # 어린이/노인 보호구역
    "B_riverside":  dict(scenes=("03", "09", "12", "17"),
                         signs=("sign_kr126",)),
    "C_park":       dict(scenes=("04", "10", "16"),
                         signs=("sign_kr302", "sign_kr303", "sign_kr333")),
    "D_underpass":  dict(scenes=("02", "06", "11"),
                         signs=("sign_kr321", "sign_kr322")),      # 보행자전용 / 횡단보도
    "F_apartment":  dict(scenes=("13",),
                         signs=("sign_kr224", "sign_kr226", "sign_kr320", "sign_krzone30")),
    "L_yard":       dict(scenes=("D1", "D3"),
                         signs=("sign_kr136", "sign_krconstruction_50")),
}
# `sign_krroadname` (도로명판) is the all-scene cue (§3.3 N-A1).
SIGN_ALL_SCENES = ("sign_krroadname",)


# ===========================================================================
# [6] Asset resolution
# ===========================================================================
class AssetSpec(object):
    """One resolved manifest row. Everything a caller needs, nothing it has to look up twice."""

    __slots__ = ("id", "group", "source", "licence", "verdict", "verdict_notes",
                 "usd_path", "is_wrapper", "alias_of", "mpu", "size_m", "zmin_m",
                 "zmax_m", "tri", "n_meshes", "z_mode", "z_review", "note")

    def __init__(self, **kw):
        for k in self.__slots__:
            setattr(self, k, kw.get(k))

    @property
    def exposed_h(self):
        """Height above the placement plane, for `target_h=` scaling.

        `grade` mode puts local z=0 on the ground, so the exposed height is `zmax`, not the
        bbox height — the same lesson `scene_common.VEG_TREES` records after `White_Pine`
        lost 15 % of its exposure to an uncorrected `zmin`.
        """
        if self.z_mode == "base":
            return float(self.size_m[2])
        return float(self.zmax_m)

    def __repr__(self):
        return (f"<AssetSpec {self.id} {self.group} mpu={self.mpu} "
                f"z={self.z_mode} tri={self.tri}>")


_SPEC_CACHE = {}


def resolve_usd(asset_id):
    """Absolute path of the USD file to reference — quirks 2 and 6.

    **Quirk 2 — `_inst.usd`, never the wrapper.** Measured on usd-core 26.8, referencing
    `typical_building_10.usd` instead of `typical_building_10_inst.usd` costs:
      - a composition error on every open — the wrapper carries a payload to
        `nv_core/common_tools/content_tagging/thumbnail_rigs/thumb_rig_prop_large.usd`,
        which was never procured (it is a thumbnail rig, not content);
      - **+504 triangles** of duplicate non-instanced geometry (wrapper 22,469 vs `_inst`
        21,965 through `TraverseInstanceProxies`), rising to **+13,320** on
        `typical_building_08` (25,429 vs 12,109) `[measured]`.
      C-25's "the wrapper composes to 504 triangles" is the `stage.Traverse()` reading, which
      misses everything behind the wrapper's instanceable prim; the composed content is
      *larger*, not smaller. Either way `_inst.usd` is the right file.

    **Quirk 6 — cross-folder sublayer aliases.** Three rows are other assets wearing another
    name (C-26): `bench_park_01` -> `bench_park_03`, `bench_park_05` -> `bench_curved_01`,
    `concrete_block_02` -> `concrete_block_01`. Their `_inst.usd` lives in the *target's*
    folder, which is why the file is looked up in the manifest key list and never guessed
    from the id. Flattening `nv_content/` would break them.
    """
    e = _index().get(asset_id)
    if e is None:
        raise UrbanAssetError(f"unknown asset id {asset_id!r} — not in {MANIFEST_PATH}")
    root = CC0_DIR if e.get("source") == "polyhaven" else URBAN_DIR
    keys = [k.get("key") or k.get("rel") for k in e.get("keys", ())]
    inst = [k for k in keys if k.endswith("_inst.usd")]
    if inst:
        if len(inst) > 1:                      # never seen; fail loudly rather than pick one
            raise UrbanAssetError(
                f"{asset_id}: {len(inst)} `_inst.usd` candidates {inst} — ambiguous")
        rel = inst[0]
    elif e.get("root_key"):
        rel = e["root_key"]
    else:                                      # Poly Haven: the single non-texture USD
        cand = [k for k in keys
                if k.lower().endswith((".usd", ".usda", ".usdc", ".usdz"))
                and "/textures/" not in k]
        if len(cand) != 1:
            raise UrbanAssetError(f"{asset_id}: {len(cand)} USD roots {cand} — ambiguous")
        rel = cand[0]
    path = os.path.join(root, rel)
    _check_banned(path)
    return path


def spec(asset_id):
    """Resolved `AssetSpec` for an id. Raises `UrbanAssetError` on anything unusable."""
    if asset_id in _SPEC_CACHE:
        return _SPEC_CACHE[asset_id]
    e = _index().get(asset_id)
    if e is None:
        raise UrbanAssetError(f"unknown asset id {asset_id!r} — not in {MANIFEST_PATH}")
    if asset_id in REFUSED_IDS:
        raise UrbanAssetError(
            f"{asset_id} is refused by ruling — season FAIL (C-21), spec §12-7 "
            f"'do not wire it'")
    if e.get("verdict") == "FAIL":
        raise UrbanAssetError(f"{asset_id}: manifest verdict FAIL — {e.get('verdict_notes')}")
    g = e.get("geometry")
    if not g:
        raise UrbanAssetError(
            f"{asset_id} has no geometry (verdict {e.get('verdict')}: "
            f"{e.get('verdict_reason')}) — it is a material library, not a placeable asset")
    path = resolve_usd(asset_id)
    if not os.path.isfile(path):
        raise UrbanAssetError(
            f"{asset_id}: {path} is absent — run `python assets/download_urban.py`")

    if asset_id in Z_ATTACH_IDS:
        z_mode = "attach"
    else:
        z_mode = "grade"
    frac = Z_REVIEW.get(asset_id, (0.0, 0.0))[0]

    s = AssetSpec(
        id=asset_id, group=e.get("group"), source=e.get("source"),
        licence=e.get("licence") or manifest()["licence"].get(e.get("source", ""), ""),
        verdict=e.get("verdict"), verdict_notes=e.get("verdict_notes") or [],
        usd_path=path, is_wrapper=path.endswith(os.path.basename(e.get("root_key") or "")),
        alias_of=(g.get("alias_of") or []), mpu=float(g.get("mpu", 1.0)),
        size_m=[float(v) for v in g["size_m"]], zmin_m=float(g["zmin_m"]),
        zmax_m=float(g["zmax_m"]), tri=int(g.get("tri_effective", 0)),
        n_meshes=int(g.get("n_meshes", 0)), z_mode=z_mode,
        z_review=(frac >= Z_REVIEW_FRAC), note=e.get("note", ""))
    _SPEC_CACHE[asset_id] = s
    return s


def available(asset_id):
    """True when the row can be loaded. Mirrors `scene_common.veg_available`'s posture:
    a scene may branch on procurement state, but it may not fail silently."""
    try:
        spec(asset_id)
        return True
    except UrbanAssetError:
        return False


# ===========================================================================
# [7] Load statistics — the same posture as `scene_common.LOOK_STATS`
# ===========================================================================
LOAD_STATS = dict(placed=0, by_group={}, far_override_mats=0, far_override_scaled=0,
                  instanced=0, z_review_hits=[], warn_rows=[], scope_unchecked=[])
_WARNED = set()


def _warn_once(key, msg):
    if key in _WARNED:
        return
    _WARNED.add(key)
    print(msg)


def load_report():
    """One-line-per-fact summary for a scene's build log."""
    g = " · ".join(f"{k} {v}" for k, v in sorted(LOAD_STATS["by_group"].items()))
    lines = [f"[urban_kit] placed {LOAD_STATS['placed']} — {g}"]
    if LOAD_STATS["far_override_mats"]:
        lines.append(f"[urban_kit] far-tier override: {LOAD_STATS['far_override_mats']} "
                     f"materials bound, {LOAD_STATS['far_override_scaled']} albedo-scaled "
                     f"(cap {FAR_ALBEDO_CAP})")
    if LOAD_STATS["instanced"]:
        lines.append(f"[urban_kit] instanceable: {LOAD_STATS['instanced']}")
    if LOAD_STATS["z_review_hits"]:
        lines.append(f"[urban_kit] z-review rows placed at grade: "
                     f"{sorted(set(LOAD_STATS['z_review_hits']))}")
    if LOAD_STATS["warn_rows"]:
        lines.append(f"[urban_kit] manifest WARN rows placed: "
                     f"{sorted(set(LOAD_STATS['warn_rows']))}")
    return "\n".join(lines)


# ===========================================================================
# [8] Placement
# ===========================================================================
def add_urban_asset(stage, prim_path, asset_id, pos_m=(0.0, 0.0, 0.0), yaw_deg=0.0,
                    target_h=None, scale_mul=1.0, tilt_deg=(0.0, 0.0),
                    z_mode=None, z_lift_m=None, scene=None, instanceable=False,
                    far_override="auto"):
    """Reference an urban asset under an Xform this function owns. Returns the parent `Xform`.

    Args:
      stage        an open `Usd.Stage` at `metersPerUnit = 1.0`.
      prim_path    the parent Xform path. The reference lands on `<prim_path>/Asset`.
      asset_id     a manifest id (`urban_kit.ids()` lists them).
      pos_m        (x, y, z) in scene metres. `z` is the **placement plane**, see `z_mode`.
      yaw_deg      rotation about +Z, applied after the translate (T -> R -> S).
      target_h     scale the asset so its exposed height matches this, in metres.
      scale_mul    extra uniform multiplier, applied on top of `target_h`.
      tilt_deg     (rx, ry) slope-following tilt, authored only when non-zero.
      z_mode       None = the row's default (`grade`, or `attach` for the 3 mounted rows);
                   'grade' = local z=0 lands on `pos_m[2]`; 'base' = the lowest geometry lands
                   on `pos_m[2]`; 'attach' = refuse (the caller must place it on its parent).
      z_lift_m     explicit extra lift in asset-native metres, added after `z_mode`.
      scene        scene tag ('01', 'C2', 'D2' ...) — enforces the §3.3 season/era scopes.
      instanceable set `/Asset` instanceable so repeated placements share one prototype.
      far_override 'auto' (default) or 'off' — the §1.11 A/B arms for the 8 far-tier buildings.

    Quirk 4 — **parent-Xform placement.** The referenced roots already own
    `[xformOp:translate, rotateXYZ, scale]` on 78 of the 243 measurable rows (every `_inst.usd`
    that carries them), so calling `AddTranslateOp()` on the prim that holds the reference dies
    with "already exists in xformOpOrder". The reference therefore lands on a `/Asset` child and
    every op is authored on the parent — the same shape `scene_common.add_vegetation` settled on
    after the Debris family hit exactly this trap.

    Quirk 3 — **`mpu` per asset.** The scale carries `mpu_asset / mpu_stage`. A USD reference
    does not convert units, so the 8 far-tier buildings (`mpu 0.01`) arrive 100x oversized
    without it `[manifest]` C-28.
    """
    from pxr import Usd, UsdGeom, Gf   # noqa: F401  (lazy — CPU-only import of this module)

    # Complete the MDL package before the first reference composes (section [1b]).
    # Cached after the first call, so this is one `os.listdir` for the whole run.
    ensure_mdl_package()

    s = spec(asset_id)

    # --- scene scope (§3.3 cautions) ---------------------------------------
    scope = SCENE_SCOPE.get(asset_id)
    if scope is not None:
        if scene is None:
            LOAD_STATS["scope_unchecked"].append(asset_id)
            _warn_once("scope:" + asset_id,
                       f"[urban_kit][경고] {asset_id} is scene-scoped to {scope} but no "
                       f"`scene=` was given — the scope could not be enforced")
        elif str(scene) not in scope:
            raise UrbanAssetError(
                f"{asset_id} is scope-limited to scenes {scope} (§3.3) — refusing scene "
                f"{scene!r}")

    if s.verdict == "WARN":
        LOAD_STATS["warn_rows"].append(asset_id)

    # --- z policy (quirk 1) -------------------------------------------------
    mode = z_mode or s.z_mode
    if mode == "attach":
        raise UrbanAssetError(
            f"{asset_id} is an attachment (zmin {s.zmin_m:+.3f} m — it sits on its parent "
            f"asset). Place it explicitly with `z_mode='grade'` and a pos_m z that names the "
            f"parent surface.")
    if mode not in ("grade", "base"):
        raise UrbanAssetError(f"unknown z_mode {mode!r} — expected 'grade' or 'base'")
    if mode == "grade" and s.z_review:
        LOAD_STATS["z_review_hits"].append(asset_id)
        frac, zmin = Z_REVIEW[asset_id]
        _warn_once("zrev:" + asset_id,
                   f"[urban_kit][z] {asset_id}: {frac*100:.1f} % of its triangles sit below "
                   f"its own origin (zmin {zmin:+.3f} m) — placed at grade (no lift). If the "
                   f"reference photo shows it resting on the surface, call with z_mode='base'.")

    # --- scale --------------------------------------------------------------
    unit = s.mpu / float(UsdGeom.GetStageMetersPerUnit(stage) or 1.0)
    geom_scale = float(scale_mul)
    if target_h:
        native = s.exposed_h
        if native <= 1e-6:
            raise UrbanAssetError(
                f"{asset_id}: exposed height {native} m — target_h cannot be applied")
        geom_scale *= float(target_h) / native
    s_total = unit * geom_scale

    lift = 0.0
    if mode == "base":
        lift += -s.zmin_m
    if z_lift_m:
        lift += float(z_lift_m)

    # --- prims (quirk 4) ----------------------------------------------------
    xf = UsdGeom.Xform.Define(stage, prim_path)
    asset_prim = UsdGeom.Xform.Define(stage, prim_path + "/Asset").GetPrim()
    asset_prim.GetReferences().AddReference(s.usd_path)

    x, y, z = (float(v) for v in pos_m)
    xf.AddTranslateOp().Set(Gf.Vec3d(x, y, z + lift * geom_scale))
    xf.AddRotateZOp().Set(float(yaw_deg))          # order matters: T -> R -> S
    tx, ty = (float(tilt_deg[0]), float(tilt_deg[1])) if tilt_deg else (0.0, 0.0)
    if abs(tx) > 1e-6:
        xf.AddRotateXOp().Set(tx)
    if abs(ty) > 1e-6:
        xf.AddRotateYOp().Set(ty)
    xf.AddScaleOp().Set(Gf.Vec3f(s_total, s_total, s_total))

    # --- far-tier material override (`[ruled 07-30]` §1.11) -----------------
    did_override = False
    if s.group == "buildings_far" and far_override == "auto":
        did_override = _bind_far_override(stage, asset_prim, s)

    if instanceable:
        if did_override:
            # An instanceable prim's descendants live in a prototype and cannot carry the
            # per-mesh binding. The tier costs 1,354-9,963 triangles per building
            # `[manifest]`, so the instancing is worth nothing here anyway.
            _warn_once("inst:" + asset_id,
                       f"[urban_kit][경고] {asset_id}: instanceable ignored — the §1.11 "
                       f"override binds per mesh and cannot live inside a prototype")
        else:
            asset_prim.SetInstanceable(True)
            LOAD_STATS["instanced"] += 1

    LOAD_STATS["placed"] += 1
    LOAD_STATS["by_group"][s.group] = LOAD_STATS["by_group"].get(s.group, 0) + 1
    return xf


def _src_shader(stage, mat_prim):
    """The `Shader` child of a `Material` prim, or None."""
    from pxr import UsdShade
    for c in mat_prim.GetChildren():
        if c.GetTypeName() == "Shader":
            return UsdShade.Shader(c)
    return None


def _abs_tex(shader, name):
    """Absolute path of a texture input, resolved against the layer that authored it.

    The referenced asset's inputs are relative (`../../shared_textures/x.png`). A material
    authored in the *scene's* root layer would resolve those against the scene, so the path is
    made absolute here. Quirk 5: the `<asset>/materials/textures/<name>.png` variants are the
    inner `_inst_base` layer's paths and are dead by design — this only ever reads the
    composed, winning value from `_inst`.
    """
    i = shader.GetInput(name)
    if i is None:
        return None
    v = i.Get()
    if v is None or not getattr(v, "path", ""):
        return None
    if getattr(v, "resolvedPath", ""):
        return v.resolvedPath
    layer = i.GetAttr().GetPropertyStack(0.0)[0].layer
    return os.path.normpath(os.path.join(os.path.dirname(layer.realPath), v.path))


def _bind_far_override(stage, asset_prim, s):
    """Bind the §1.11 override on a far-tier building. Returns True when anything was bound.

    One override material per distinct source material that binds a diffuse texture, shared
    across every placement of that asset (`OVERRIDE_LOOKS_SCOPE`). Materials without a diffuse
    texture — the glass and the interior-cubemap emissive — are **left alone**: replacing a
    translucent or emissive material with an opaque OmniPBR would be a worse defect than the one
    being fixed.

    What the override keeps: `diffuse_texture`, `normalmap_texture`, `reflectionroughness_texture`
    and the source `reflection_roughness_constant`, with `project_uvw = False` so the asset's own
    UVs are used — a world-space projection would smear a 60 m facade.
    What it changes: `diffuse_tint` scaled so texture x tint <= `FAR_ALBEDO_CAP` (factor 1.000 on
    all eight buildings today `[measured]`), and `metallic_constant` 1.0 -> 0.0.
    """
    from pxr import Usd, UsdShade, Sdf, Gf

    n_bound = 0
    made = {}
    for pr in Usd.PrimRange(asset_prim, Usd.TraverseInstanceProxies(
            Usd.PrimAllPrimsPredicate)):
        if pr.GetTypeName() != "Mesh":
            continue
        if pr.IsInstanceProxy():
            # Would need a `strongerThanDescendants` collection binding; the far tier has no
            # internal instancing `[measured: 0 instances in all 8 _inst.usd]`, so this is a
            # tripwire for a future asset revision rather than a supported path.
            raise UrbanAssetError(
                f"{s.id}: {pr.GetPath()} is an instance proxy — the §1.11 override cannot "
                f"bind inside a prototype")
        src_mat = UsdShade.MaterialBindingAPI(pr).ComputeBoundMaterial()[0]
        if not src_mat:
            continue
        name = src_mat.GetPath().name
        if name not in made:
            made[name] = _make_far_override_mtl(stage, s, src_mat)
        ovr = made[name]
        if ovr is None:
            continue
        UsdShade.MaterialBindingAPI.Apply(pr).Bind(ovr)
        n_bound += 1
    return n_bound > 0


_FAR_MTL_CACHE = {}


def _make_far_override_mtl(stage, s, src_mat):
    """Create (or reuse) one override material. None when the source has no diffuse texture."""
    from pxr import UsdShade, Sdf, Gf

    key = (s.id, src_mat.GetPath().name)
    if key in _FAR_MTL_CACHE:
        return _FAR_MTL_CACHE[key]

    sh_src = _src_shader(stage, src_mat.GetPrim())
    if sh_src is None:
        _FAR_MTL_CACHE[key] = None
        return None
    diff = _abs_tex(sh_src, "diffuse_texture")
    if diff is None:                      # glass / emissive cubemap — leave untouched
        _FAR_MTL_CACHE[key] = None
        return None

    tint_in = sh_src.GetInput("diffuse_tint")
    tint = tint_in.Get() if tint_in is not None else None
    tint = (float(tint[0]), float(tint[1]), float(tint[2])) if tint else (1.0, 1.0, 1.0)
    alb = FAR_TEX_ALBEDO.get(os.path.basename(diff))
    if alb is None:
        raise UrbanAssetError(
            f"{s.id}/{src_mat.GetPath().name}: {os.path.basename(diff)} is not in "
            f"FAR_TEX_ALBEDO — measure it before binding an albedo override")
    eff = alb * _luma(tint)
    k = min(1.0, FAR_ALBEDO_CAP / eff) if eff > 1e-6 else 1.0
    if k < 1.0:
        LOAD_STATS["far_override_scaled"] += 1

    path = f"{OVERRIDE_LOOKS_SCOPE}/{s.id}__{src_mat.GetPath().name}"
    mtl = UsdShade.Material.Define(stage, path)
    sh = UsdShade.Shader.Define(stage, path + "/Shader")
    sh.CreateImplementationSourceAttr(UsdShade.Tokens.sourceAsset)
    sh.SetSourceAsset(Sdf.AssetPath(OMNIPBR_PATH), "mdl")
    sh.SetSourceAssetSubIdentifier("OmniPBR", "mdl")
    F, C3, A, B = (Sdf.ValueTypeNames.Float, Sdf.ValueTypeNames.Color3f,
                   Sdf.ValueTypeNames.Asset, Sdf.ValueTypeNames.Bool)

    def _tex(name, val, cs):
        i = sh.CreateInput(name, A)
        i.Set(Sdf.AssetPath(val))
        try:
            i.GetAttr().SetColorSpace(cs)
        except Exception:
            pass

    _tex("diffuse_texture", diff, "auto")
    nor = _abs_tex(sh_src, "normalmap_texture")
    if nor:
        _tex("normalmap_texture", nor, "raw")
    rgh = _abs_tex(sh_src, "reflectionroughness_texture")
    if rgh:
        _tex("reflectionroughness_texture", rgh, "raw")
    sh.CreateInput("project_uvw", B).Set(False)          # asset UVs, not world projection
    sh.CreateInput("diffuse_tint", C3).Set(
        Gf.Vec3f(tint[0] * k, tint[1] * k, tint[2] * k))
    sh.CreateInput("metallic_constant", F).Set(FAR_OVERRIDE_METALLIC)
    rc = sh_src.GetInput("reflection_roughness_constant")
    if rc is not None and rc.Get() is not None:
        sh.CreateInput("reflection_roughness_constant",
                       F).Set(min(1.0, max(0.0, float(rc.Get()))))
    for out in ("surface", "displacement", "volume"):
        mtl.CreateOutput(f"mdl:{out}", Sdf.ValueTypeNames.Token).ConnectToSource(
            sh.ConnectableAPI(), "out")

    LOAD_STATS["far_override_mats"] += 1
    _FAR_MTL_CACHE[key] = mtl
    return mtl


# ===========================================================================
# [9] Self-check — §6.2's T4 obligation
#
#   "Load-and-traverse every asset it wires, with `Usd.TraverseInstanceProxies` —
#    `stage.Traverse()` alone reports `bench_park_01` as 0 triangles."
#
#   /tmp/usdvenv/bin/python urban_kit.py --self-check
# ===========================================================================
def _tri_count(stage, proxies=True, expand_instancers=True):
    """(effective triangles, mesh prims). Mirrors the manifest's method note exactly:
    "Σ(faceVertexCount−2); PointInstancer 는 protoIndices 전개".

    `expand_instancers=False` returns the *unique* count. The two differ by up to **37x**:
    `veg_shrub_hedge_green_01` is 20,894 unique / **758,206 effective** across 4 PointInstancers
    (27 + 13 + 69 + 13 instances), `veg_shrub_hedge_yellow_01` 16,116 / 80,580 `[measured]`.
    Six midground vegetation rows carry PointInstancers; nothing else in the library does.
    """
    from pxr import Usd, UsdGeom
    pred = (Usd.TraverseInstanceProxies(Usd.PrimAllPrimsPredicate) if proxies
            else Usd.PrimAllPrimsPredicate)
    per_prim = {}
    instancers = []
    n = 0
    for pr in Usd.PrimRange.Stage(stage, pred):
        if pr.GetTypeName() == "Mesh":
            fv = pr.GetAttribute("faceVertexCounts").Get() or []
            per_prim[pr.GetPath().pathString] = sum(c - 2 for c in fv)
            n += 1
        elif pr.GetTypeName() == "PointInstancer":
            instancers.append(pr)
    if not expand_instancers or not instancers:
        return sum(per_prim.values()), n

    def _subtree(root):
        rs = root.pathString.rstrip("/") + "/"
        return sum(t for p, t in per_prim.items() if p == root.pathString or p.startswith(rs))

    consumed, total = set(), 0
    for pi_prim in instancers:
        pi = UsdGeom.PointInstancer(pi_prim)
        protos = pi.GetPrototypesRel().GetTargets()
        counts = {}
        for i in (pi.GetProtoIndicesAttr().Get() or []):
            counts[int(i)] = counts.get(int(i), 0) + 1
        for i, root in enumerate(protos):
            consumed.add(root.pathString)
            total += counts.get(i, 0) * _subtree(root)
    for p, t in per_prim.items():
        if not any(p == c or p.startswith(c.rstrip("/") + "/") for c in consumed):
            total += t
    return total, n


def _measure_frac_below(path):
    """Fraction of triangles whose centroid sits below the asset's own local z = 0, and the
    measured zmin in metres. The honest form of `tri_below_grade_frac` (see section [3]).

    PointInstancer prototypes are expanded through every instance transform, so the six
    vegetation rows are weighted by where their branches actually sit, not by where the
    unused prototype happens to be authored.
    """
    import numpy as np
    from pxr import Usd, UsdGeom
    st = Usd.Stage.Open(path)
    mpu = UsdGeom.GetStageMetersPerUnit(st)
    xc = UsdGeom.XformCache(Usd.TimeCode.Default())

    def _mesh_geom(pr):
        """(points Nx3 in stage-local space, triangle index array Mx3) for one Mesh."""
        mesh = UsdGeom.Mesh(pr)
        pts = mesh.GetPointsAttr().Get()
        fvc = mesh.GetFaceVertexCountsAttr().Get()
        fvi = mesh.GetFaceVertexIndicesAttr().Get()
        if not pts or not fvc:
            return None, None
        M = np.array(xc.GetLocalToWorldTransform(pr)).T
        P = (np.array([[p[0], p[1], p[2]] for p in pts], dtype=np.float64)
             @ M[:3, :3].T) + M[:3, 3]
        idx = np.array(fvi, dtype=np.int64)
        cnt = np.array(fvc, dtype=np.int64)
        offs = np.concatenate([[0], np.cumsum(cnt)[:-1]])
        tris = []
        for c, o in zip(cnt, offs):
            f = idx[o:o + c]
            for i in range(1, c - 1):                 # fan triangulation
                tris.append((f[0], f[i], f[i + 1]))
        return P, (np.array(tris, dtype=np.int64) if tris else None)

    meshes = {}
    instancers = []
    for pr in Usd.PrimRange.Stage(st, Usd.TraverseInstanceProxies(
            Usd.PrimAllPrimsPredicate)):
        if pr.GetTypeName() == "Mesh":
            P, T = _mesh_geom(pr)
            if T is not None:
                meshes[pr.GetPath().pathString] = (P, T)
        elif pr.GetTypeName() == "PointInstancer":
            instancers.append(pr)

    def _subtree(root):
        rs = root.pathString.rstrip("/") + "/"
        return [v for p, v in meshes.items()
                if p == root.pathString or p.startswith(rs)]

    tot = below = 0
    zmin = float("inf")

    def _tally(P, T):
        nonlocal tot, below, zmin
        cz = P[T][:, :, 2].mean(axis=1)
        tot += int(cz.size)
        below += int((cz < 0.0).sum())
        zmin = min(zmin, float(P[:, 2].min()))

    consumed = set()
    for pi_prim in instancers:
        pi = UsdGeom.PointInstancer(pi_prim)
        protos = pi.GetPrototypesRel().GetTargets()
        pidx = list(pi.GetProtoIndicesAttr().Get() or [])
        xforms = pi.ComputeInstanceTransformsAtTime(Usd.TimeCode.Default(),
                                                    Usd.TimeCode.Default())
        for k, pi_i in enumerate(pidx):
            root = protos[int(pi_i)]
            consumed.add(root.pathString)
            X = np.array(xforms[k]).T          # instance transform, on top of the prototype's
            for P, T in _subtree(root):
                _tally((P @ X[:3, :3].T) + X[:3, 3], T)
    for p, (P, T) in meshes.items():
        if any(p == c or p.startswith(c.rstrip("/") + "/") for c in consumed):
            continue
        _tally(P, T)
    return ((below / tot if tot else 0.0),
            (0.0 if zmin == float("inf") else zmin * mpu))


def self_check(deep_z=True, verbose=True):
    """Load every placeable manifest row through this loader. Returns (n_ok, failures)."""
    from pxr import Usd, UsdGeom, UsdShade, Gf
    os.environ.setdefault("PXR_USDC_EMIT_DEPRECATION_WARNINGS", "0")

    fails = []

    # --- 0. the MDL package compiles at all (section [1b]) -------------------
    #     Ahead of everything else: with `baking_annotations` missing, every row below
    #     still loads, traverses and measures perfectly — and every one of them renders
    #     flat red. A self-check that only counts triangles cannot see that, which is
    #     exactly how the defect reached a judged frame in scene07's first pilot.
    mdl = ensure_mdl_package(verbose=verbose)
    if not mdl["ok"]:
        fails.append(("mdl_package",
                      f"unresolved {mdl['missing']} {mdl['unsatisfiable']}"))
    if verbose:
        print(f"[self-check] MDL package {'OK' if mdl['ok'] else 'INCOMPLETE'} — "
              f"added {mdl['added'] or 'none (already complete)'}")

    rows = [a for a in ids() if a not in REFUSED_IDS]
    placeable = []
    for aid in rows:
        try:
            placeable.append(spec(aid))
        except UrbanAssetError as ex:
            if "no geometry" in str(ex) or "verdict FAIL" in str(ex):
                continue                                    # the 15 _core + the 1 FAIL row
            fails.append((aid, f"spec: {ex}"))
    if verbose:
        print(f"[self-check] manifest rows {len(rows)} -> placeable {len(placeable)}")

    # --- 1. every asset opens, mpu and triangles reproduce the manifest ------
    stage = Usd.Stage.CreateInMemory()
    UsdGeom.SetStageMetersPerUnit(stage, 1.0)
    UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)
    UsdGeom.Xform.Define(stage, "/World")
    n_tri_ok = n_mpu_ok = 0
    for s in placeable:
        try:
            src = Usd.Stage.Open(s.usd_path)
        except Exception as ex:
            fails.append((s.id, f"stage open: {ex}"))
            continue
        mpu = UsdGeom.GetStageMetersPerUnit(src)
        if abs(mpu - s.mpu) > 1e-9:
            fails.append((s.id, f"mpu {mpu} != manifest {s.mpu}"))
        else:
            n_mpu_ok += 1
        tri, _ = _tri_count(src, proxies=True)
        if s.tri and tri != s.tri:
            fails.append((s.id, f"tri {tri} != manifest {s.tri}"))
        else:
            n_tri_ok += 1
        plain, _ = _tri_count(src, proxies=False)
        if plain == 0 and tri > 0 and verbose and s.id == "bench_park_01":
            print(f"[self-check] §6.2 trap reproduced — bench_park_01: "
                  f"stage.Traverse() {plain} tri vs TraverseInstanceProxies {tri} tri")
    if verbose:
        print(f"[self-check] mpu ok {n_mpu_ok}/{len(placeable)} · "
              f"tri ok {n_tri_ok}/{len(placeable)}")

    # --- 2. place every asset through the loader ----------------------------
    n_placed = 0
    for i, s in enumerate(placeable):
        kw = dict(pos_m=(i * 3.0, 0.0, 0.0), yaw_deg=17.0)
        if s.z_mode == "attach":
            kw["z_mode"] = "grade"
        if s.id in SCENE_SCOPE:
            kw["scene"] = SCENE_SCOPE[s.id][0]
        try:
            xf = add_urban_asset(stage, f"/World/Chk/A{i:03d}", s.id, **kw)
        except Exception as ex:
            fails.append((s.id, f"add_urban_asset: {ex}"))
            continue
        ops = [o.GetOpName() for o in xf.GetOrderedXformOps()]
        if ops[:2] != ["xformOp:translate", "xformOp:rotateZ"] or \
                ops[-1] != "xformOp:scale":
            fails.append((s.id, f"parent xformOpOrder {ops}"))
        ap = stage.GetPrimAtPath(f"/World/Chk/A{i:03d}/Asset")
        if not ap or not ap.IsValid() or not ap.GetChildren():
            fails.append((s.id, "reference composed to nothing"))
            continue
        n_placed += 1
    if verbose:
        print(f"[self-check] placed {n_placed}/{len(placeable)}")

    # --- 3. mpu 0.01 really lands as metres ---------------------------------
    bb = UsdGeom.BBoxCache(Usd.TimeCode.Default(),
                           [UsdGeom.Tokens.default_, UsdGeom.Tokens.render])
    for s in placeable:
        if s.group != "buildings_far":
            continue
        p = None
        for i, t in enumerate(placeable):
            if t.id == s.id:
                p = f"/World/Chk/A{i:03d}"
                break
        r = bb.ComputeWorldBound(stage.GetPrimAtPath(p)).ComputeAlignedRange()
        got = r.GetMax()[2] - r.GetMin()[2]
        if abs(got - s.size_m[2]) > max(0.02, 0.01 * s.size_m[2]):
            fails.append((s.id, f"world height {got:.3f} m != manifest {s.size_m[2]:.3f} m "
                                f"(mpu {s.mpu} not applied?)"))
    if verbose:
        print(f"[self-check] far-tier world height ok "
              f"({len([s for s in placeable if s.group == 'buildings_far'])} rows)")

    # --- 4. the §1.11 override actually binds -------------------------------
    n_ovr = n_mesh = 0
    for i, s in enumerate(placeable):
        if s.group != "buildings_far":
            continue
        root = stage.GetPrimAtPath(f"/World/Chk/A{i:03d}/Asset")
        for pr in Usd.PrimRange(root):
            if pr.GetTypeName() != "Mesh":
                continue
            n_mesh += 1
            b = UsdShade.MaterialBindingAPI(pr).ComputeBoundMaterial()[0]
            if b and b.GetPath().pathString.startswith(OVERRIDE_LOOKS_SCOPE):
                n_ovr += 1
    if n_ovr == 0:
        fails.append(("far_override", "no mesh bound to an override material"))
    # every override material's effective albedo must land inside the band
    for pr in stage.GetPrimAtPath(OVERRIDE_LOOKS_SCOPE).GetChildren() \
            if stage.GetPrimAtPath(OVERRIDE_LOOKS_SCOPE) else []:
        sh = _src_shader(stage, pr)
        if sh is None:
            continue
        d = _abs_tex(sh, "diffuse_texture")
        t = sh.GetInput("diffuse_tint").Get()
        eff = FAR_TEX_ALBEDO[os.path.basename(d)] * _luma(t)
        if eff > FAR_ALBEDO_CAP + 1e-6:
            fails.append((pr.GetName(), f"effective albedo {eff:.3f} > {FAR_ALBEDO_CAP}"))
        m = sh.GetInput("metallic_constant").Get()
        if m is None or float(m) != FAR_OVERRIDE_METALLIC:
            fails.append((pr.GetName(), f"metallic_constant {m} != {FAR_OVERRIDE_METALLIC}"))
    if verbose:
        print(f"[self-check] far-tier override bound on {n_ovr}/{n_mesh} meshes")

    # --- 5. aliases (C-26) and banned paths ---------------------------------
    want = {"bench_park_01": "bench_park_03", "bench_park_05": "bench_curved_01",
            "concrete_block_02": "concrete_block_01"}
    for a, target in want.items():
        s = spec(a)
        if target not in s.alias_of:
            fails.append((a, f"alias_of {s.alias_of} does not name {target} (C-26)"))
        if f"/{target}/" not in s.usd_path:
            fails.append((a, f"resolved {s.usd_path} is not in {target}'s folder"))
    for s in placeable:
        try:
            _check_banned(s.usd_path)
        except UrbanAssetError as ex:
            fails.append((s.id, str(ex)))
    if verbose:
        print(f"[self-check] aliases + banned-path guard ok "
              f"({len(placeable)} paths, {len(BANNED_SUBSTRINGS)} patterns)")

    # --- 6. the Z_REVIEW table still reproduces -----------------------------
    if deep_z:
        drift = 0
        for aid, (frac, zmin) in sorted(Z_REVIEW.items()):
            if aid in REFUSED_IDS:
                continue
            f2, z2 = _measure_frac_below(resolve_usd(aid))
            if abs(f2 - frac) > 5e-4 or abs(z2 - zmin) > 1e-3:
                fails.append((aid, f"Z_REVIEW drift: measured ({f2:.4f}, {z2:.4f}) "
                                   f"vs table ({frac:.4f}, {zmin:.4f})"))
                drift += 1
        if verbose:
            print(f"[self-check] Z_REVIEW {len(Z_REVIEW)} rows re-measured, drift {drift}")

    if verbose:
        print(f"[self-check] {'PASS' if not fails else 'FAIL'} — "
              f"{len(placeable) - len(fails)} ok, {len(fails)} problems")
        for a, msg in fails:
            print(f"   FAIL {a}: {msg}")
        print(load_report())
    return len(placeable), fails


def _sheet():
    """One line per placeable row — the table the readjudication report is built from."""
    print(f"{'id':44s} {'group':16s} {'mpu':>5s} {'tri':>8s} "
          f"{'size_mm (x,y,z)':>26s} {'zmin':>8s} {'z_mode':>7s} {'file'}")
    for aid in ids():
        try:
            s = spec(aid)
        except UrbanAssetError:
            continue
        sz = "x".join(f"{v*1000:.0f}" for v in s.size_m)
        print(f"{s.id:44s} {s.group:16s} {s.mpu:5.2f} {s.tri:8d} {sz:>26s} "
              f"{s.zmin_m:8.3f} {s.z_mode:>7s} "
              f"{os.path.relpath(s.usd_path, _HERE)}")


if __name__ == "__main__":
    import sys
    if "--sheet" in sys.argv:
        _sheet()
    elif "--list" in sys.argv:
        for aid in ids():
            print(aid)
    else:
        n, f = self_check(deep_z="--fast" not in sys.argv)
        sys.exit(1 if f else 0)
