# -*- coding: utf-8 -*-
"""
scene_common.py - NegObs synthetic scene common library (Isaac Sim 4.5)

The verified blocks of scene01_campus_stairs.py, turned into general functions.
Brief: Docs/multi_scene_brief_v2.md §A (API), §B (new textures), §C (scenes using it).

Import safety rule (important):
  This module must be safe to import **before** SimulationApp has booted.
  -> pxr / isaacsim / carb / omni are never imported at module top level
    (all are deferred imports inside functions). Only numpy/os/math/json at top level.

Coordinate convention (all scenes): Z-up, metres, travel axis +X, drop start edge x=0.
"""

import os
import glob
import math
import json
import zlib

import numpy as np

import facade_kit as fk        # Facade lower-storey kit (does not import scene_common)
import stair_kit as sk        # Stair statute kit (same - primitives are injected)


# ===========================================================================
# [0] Path and asset constants
# ===========================================================================
_HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(_HERE, "assets")
S1_DIR = os.path.join(ASSETS_DIR, "scene01")     # The texture sets are consolidated under scene01/

OMNIPBR_PATH = os.path.expanduser(
    "~/miniconda3/envs/env_isaaclab/lib/python3.10/site-packages/"
    "omni/mdl/core/Base/OmniPBR.mdl")

# Default noon HDRI (a scene can override it via light_params["hdri"])
DEFAULT_HDRI = "qwantani_noon_puresky_4k.exr"


# ===========================================================================
# [1] TEX registry - the existing scene01 set + the 7 new §B roles (canonical filenames)
#     nor suffix: ambientCG sets use _nor, PolyHaven sets use _nor_dx.
# ===========================================================================
TEX = dict(
    # --- Existing scene01 roles ---
    plaza_light=dict(dir=S1_DIR, diff="plaza_light_diff.jpg",
                     nor="plaza_light_nor.jpg", rough="plaza_light_rough.jpg"),
    band_dark=dict(dir=S1_DIR, diff="band_dark_diff.jpg",
                   nor="band_dark_nor.jpg", rough="band_dark_rough.jpg"),
    plaza_lower=dict(dir=S1_DIR, diff="plaza_lower_diff.jpg",
                     nor="plaza_lower_nor.jpg", rough="plaza_lower_rough.jpg"),
    granite_dark=dict(dir=S1_DIR, diff="granite_dark_diff.jpg",
                      nor="granite_dark_nor_dx.jpg",
                      rough="granite_dark_rough.jpg"),
    brick_red=dict(dir=S1_DIR, diff="brick_red_diff.jpg",
                   nor="brick_red_nor_dx.jpg", rough="brick_red_rough.jpg"),
    # [W2, audit B A1] Replaced `aerial_grass_rock` (PolyHaven aerial grassland, measured tile 15 m)
    # with ambientCG **Grass001** (measured tile **1.40 m**, CC0, tags lawn/park/short/dense).
    #   - Pixel density 273 px/m -> **2,926 px/m (x10.7)** - a 4-7 mm blade of Korean lawn grass
    #     is now **genuinely resolved** at 12-20 px [measured - assets/veg_manifest_w2.json textures]
    #   - Green 98.25 %, linear albedo 0.0932, pure white 0 % -> passes the seasonal convention
    #   - **`scale_m` must be 1.4** (the real tile size). Fix `scale=dict(grass=...)` in every scene at once.
    #   Alternative (for variation between scenes) = `grass_lawn_b` (ambientCG Grass004, same 1.40 m).
    grass=dict(dir=ASSETS_DIR, diff="grass_lawn_diff.jpg",
               nor="grass_lawn_nor.jpg",
               rough="grass_lawn_rough.jpg"),
    tactile=dict(dir=S1_DIR, diff="tactile_yellow_diff.png",
                 nor="tactile_yellow_nor.png"),        # No rough map
    # --- The 7 new §B roles ---
    concrete_wall=dict(dir=S1_DIR, diff="concrete_wall_diff.jpg",
                       nor="concrete_wall_nor_dx.jpg",
                       rough="concrete_wall_rough.jpg"),   # Underpass retaining wall, tunnel
    concrete_floor=dict(dir=S1_DIR, diff="concrete_floor_diff.jpg",
                        nor="concrete_floor_nor_dx.jpg",
                        rough="concrete_floor_rough.jpg"),  # Underpass stairs and floor
    wood_dark=dict(dir=S1_DIR, diff="wood_dark_diff.jpg",
                   nor="wood_dark_nor_dx.jpg",
                   rough="wood_dark_rough.jpg"),            # Sleeper (timber)
    dirt_park=dict(dir=S1_DIR, diff="dirt_park_diff.jpg",
                   nor="dirt_park_nor_dx.jpg",
                   rough="dirt_park_rough.jpg"),            # Park dirt path
    gravel=dict(dir=S1_DIR, diff="gravel_diff.jpg",
                nor="gravel_nor_dx.jpg",
                rough="gravel_rough.jpg"),                  # Decomposed granite, gravel
    stone_flag=dict(dir=S1_DIR, diff="stone_flag_diff.jpg",
                    nor="stone_flag_nor_dx.jpg",
                    rough="stone_flag_rough.jpg"),          # Natural stone flags
    rock_wall=dict(dir=S1_DIR, diff="rock_wall_diff.jpg",
                   nor="rock_wall_nor_dx.jpg",
                   rough="rock_wall_rough.jpg"),            # Stone masonry / riprap
    # --- The 6 new §C v3 roles (downloaded by the asset agent, canonical slugs) ---
    metal_rust=dict(dir=S1_DIR, diff="metal_rust_diff.jpg",
                    nor="metal_rust_nor_dx.jpg",
                    rough="metal_rust_rough.jpg"),          # Rusted steel (fire escape, cliff walkway)
    plaster=dict(dir=S1_DIR, diff="plaster_diff.jpg",
                 nor="plaster_nor_dx.jpg",
                 rough="plaster_rough.jpg"),                # Rendered wall (alley houses)
    marble_light=dict(dir=S1_DIR, diff="marble_light_diff.jpg",
                      nor="marble_light_nor_dx.jpg",
                      rough="marble_light_rough.jpg"),      # Marble / bright memorial stone
    sandstone=dict(dir=S1_DIR, diff="sandstone_diff.jpg",
                   nor="sandstone_nor_dx.jpg",
                   rough="sandstone_rough.jpg"),            # Sandstone (stepwell, ghat)
    stone_worn=dict(dir=S1_DIR, diff="stone_worn_diff.jpg",
                    nor="stone_worn_nor_dx.jpg",
                    rough="stone_worn_rough.jpg"),          # Temple worn stone
    rock_face=dict(dir=S1_DIR, diff="rock_face_diff.jpg",
                   nor="rock_face_nor_dx.jpg",
                   rough="rock_face_rough.jpg"),            # Cliff bedrock
    # --- 1 new role for batch 1 nano-banana (scene22-33) ---
    # [realism v1] Asphalt - in the sceneD3 diagnosis 89.8 % of dead pixels were the
    # constant-colour asphalt carriageway. PolyHaven asphalt_02 (3.0 m tile, CC0).
    asphalt=dict(dir=S1_DIR, diff="asphalt_diff.jpg",
                 nor="asphalt_nor_dx.jpg", rough="asphalt_rough.jpg"),
    # Snow - the largest-area material of sceneC1 (88.5 %). PolyHaven snow_01 (2.0 m tile, CC0)
    snow=dict(dir=S1_DIR, diff="snow_diff.jpg",
              nor="snow_nor_dx.jpg", rough="snow_rough.jpg"),
    leaf_ground=dict(dir=S1_DIR, diff="leaf_ground_diff.jpg",
                     nor="leaf_ground_nor_dx.jpg",
                     rough="leaf_ground_rough.jpg"),        # Fallen-leaf ground (C2)
    # [W3 K4 micro] Moss - the first moss role in the library.
    #   Until now the repo had **no moss texture, no moss material and no moss role**
    #   (`s3_scene07_10_rebuild_spec_v1.md` §3.0 C-A2); the convention was a green tint on an
    #   existing stone map plus a `moss`/`GkMoss` token in the prim path so the look layer
    #   classes it as vegetation (`:520`, `:567`). That convention is unchanged - this role is
    #   an *addition* for the cases where a real mossy-rock scan beats a tint.
    #   Source: Poly Haven `rock_moss_set_02`, **CC0 1.0** (redistributable, tier T1), already on
    #   disk under `assets/urban_cc0/` - **zero procurement**.
    #   [measured - assets/urban_manifest_w3.json /polyhaven[23].pixels[0]]
    #     1024x1024 · chroma 757,261 px (72.2 %) · yellow-green **0.9286** of chroma · orange 0.0652
    #     · albedo_lin **0.0812** · near-white 0.0 %  (independent recompute this session:
    #     mean linear albedo 0.0750 over all pixels - same order, different gate)
    #   **Three cautions for whoever binds it first** (it has no consumer as of this commit):
    #     1. It is a rock-*with*-moss scan, not a moss carpet. Structure tiles as rock, so it reads
    #        correctly as a joint / riser-base / boulder-top patch and badly as a large-area ground.
    #        Large-area moss stays on the tint convention (§3.2, fit grade **B**).
    #     2. The normal map is Poly Haven **`_nor_gl`, i.e. OpenGL convention, and EXR**. Every other
    #        role in this registry is a **DX** map (`_nor_dx`) or an ambientCG `_nor`, and every other
    #        map here is JPG/PNG. A consumer that wants the repo's normal convention must either flip
    #        green or drop `nor` from its `make_pbr` call - do not assume parity with the rows above.
    #     3. The asset USD binds a `rock_moss_set_02_rough_1k.**exr**` that was never downloaded; the
    #        roughness map that exists on disk is the **JPG** named here.
    moss=dict(dir=os.path.join(ASSETS_DIR, "urban_cc0", "rock_moss_set_02",
                               "textures"),
              diff="rock_moss_set_02_diff_1k.jpg",
              nor="rock_moss_set_02_nor_gl_1k.exr",
              rough="rock_moss_set_02_rough_1k.jpg"),
)

# Batch-1 overcast HDRI (shared by C1 snow and C4 wet stone) - selected via light_params["hdri"],
# lookfix=False recommended (no sun, so the sun cap is meaningless; use the original).
# [v5 common layer] Interlocking paving blocks + Korean sign textures (generated by assets/signs/gen_signs.py)
# [v6 verdict C-1] The old source was mossy European sett paving, i.e. not a Korean sidewalk ->
#   replaced with ambientCG CC0 **PavingStones015** (2K-JPG, Color/NormalDX/Roughness).
#   Regular interlocking basketweave blocks, grey concrete, sand joints.
#   12 repeats per tile (square unit 170 px/2048) -> the long side of a block (= 2 units) is
#   0.17/0.20/0.25 m at scene scale_m 1.0/1.2/1.5 (real paving blocks are 200x100).
#   With the old sett texture the stones were 0.4 m class at the same scale_m and dominated the frame.
#   Filenames and paths are unchanged -> no scene file needs editing (the C-1 request to
#   'reduce the UV scale' is achieved through the repeat count of the texture itself).
TEX["paving_interlock"] = dict(dir=ASSETS_DIR, diff="paving_interlock_diff.jpg",
                               nor="paving_interlock_nor.jpg",
                               rough="paving_interlock_rough.jpg")
SIGNS_DIR = os.path.join(ASSETS_DIR, "signs")
# [GT-106] "underpass" — 지하보도 guidance plate (blue class, gen_signs.py).
for _s in ("warn_fall", "caution_step", "exit", "info", "no_entry", "underpass"):
    TEX[f"sign_{_s}"] = dict(dir=SIGNS_DIR, diff=f"sign_{_s}.png")

OVERCAST_HDRI = "kloofendal_overcast_4k.exr"

# ---------------------------------------------------------------------------
# [realism P1] PT fix settings - enabled with `NEGOBS_PT_FAST=1`
#   Basis: ZZ_synthesis §10.3 (team D) + supervisor spike measurements (2026-07-28)
#   Currently spp=1 and totalSpp=512, so accumulation runs over 512 frames. Raising spp and
#   running several subframes per update via rtSubframes converges in 8 frames.
#   Measured (spike lab, 2 views): 4.89-5.14 -> 0.08-0.31 s/shot. The PNGs of the two settings are
#   **byte-identical** (infinite PSNR) - this is lossless acceleration.
#   It is also faster than RT (RT warmup 90 = 0.79-1.03 s/shot).
# ---------------------------------------------------------------------------
PT_FAST = dict(spp=16, total_spp=64, subframes=8, warmup=8)


def tex_path(role, kind):
    """Absolute path of a role and kind (diff/nor/rough)."""
    return os.path.join(TEX[role]["dir"], TEX[role][kind])


# ===========================================================================
# [1b] Realism v1 look layer - the 2-stage `NEGOBS_LOOK_MTL` / `NEGOBS_LOOK_GEO` flags
#      (the umbrella switch `NEGOBS_LOOK_V1=1` turns both ON. All OFF by default)
#
# Directive `Docs/briefs/realism_brief_v1.md` plus revision history rev.1.
# **Not a single line of any scene file is edited** (3 invariants). Instead the role is read from
# the prim path already arriving at `make_pbr` (`{ROOT}/Looks/Paving` etc.) and a look spec is injected.
#
# Why the path name: all materials in the 33 scenes go through the single `make_pbr` entry, and the
# names under `Looks/` are meaningful (Wood 20, Grass 20, Rail 17, Parapet 15, Glass 15 ...).
# It is the only channel for a per-role prescription without touching the scenes.
#
# The 3-tier material policy [Phase1 §6.5 - the H report and the supervisor measurements converged independently]:
#   ground and slope family    -> NegObsGround.mdl (soft triplanar. Required on slopes)
#   structures, vegetation, signs -> OmniPBR (needs uv_mode, opacity, detail normal)
#   emissive, glass            -> OmniPBR (the MDL has no emission input)
# Promoting NegObsGround globally was ruled out: UV pipeline and opacity are missing, plus 72 texture fetches.
# ===========================================================================
# --- The 2-stage flags (T1 §1.7.2) - structurally blocks contamination of the material A/B control (fatal C3) ---
# The single `NEGOBS_LOOK_V1` flag changes **geometry as well as** materials. Using
# "V1=0 vs 1" as a material A/B in that state mixes in geometry changes and the material effect cannot be isolated
# (2 recorded recurrences - `redteam_verification_v1.md` R3).
#   LOOK_MTL : changes only shader inputs and the `UsdShade.Material` definition (prims unchanged).
#   LOOK_GEO : changes the prim set, types, xform, points and extent.
# The material A/B control is `LOOK_MTL=0, LOOK_GEO=1` (rule R-2).
# **The 3 lines below are the only place where the `LOOK_V1` token may still appear** (rule R-5 -
# checked by `scripts/geom_invariance_check.py --assert-no-residual-lookv1`).
LOOK_V1 = os.environ.get("NEGOBS_LOOK_V1", "") == "1"          # Umbrella (backwards compatible)
LOOK_MTL = os.environ.get("NEGOBS_LOOK_MTL", "1" if LOOK_V1 else "0") == "1"
LOOK_GEO = os.environ.get("NEGOBS_LOOK_GEO", "1" if LOOK_V1 else "0") == "1"
MDL_GROUND = os.path.join(ASSETS_DIR, "NegObsGround.mdl")

# Shared source for the detail normal (mitigates texel smearing up close) - a general-purpose micro-grain map.
# **Legacy**: the single map Phase1 E3 attached to the OmniPBR branch only. `concrete_wall_nor_dx`
# is the source T1 §1.2 judged "not a detail" (macro 4.1 %, slope -0.71 = low-frequency wall relief),
# and `_DETAIL_MAP` below takes its place. It remains only as the last-resort fallback when all 3
# procedurally generated maps are missing.
_DETAIL_NOR = os.path.join(S1_DIR, "concrete_wall_nor_dx.jpg")

# ===========================================================================
# [1c] `[W2-C]` T1 §1.6(b) - attach the detail normal to **both sides of the 3-tier material policy**
# ===========================================================================
# The substance of defect (1) (T1 §1.1): the detail normal was **only configured** as `detail=True` in
# `LOOK_CLASS`, and the code path existed in the OmniPBR branch alone. The surfaces that actually fill
# the lower 2/3 of the h0.3 frame are all `mdl="ground"` (NegObsGround) family, so -
# **the 10 ground classes had never once received a detail normal.**
# W2-A5 opened 4 inputs in MDL v1.9.0 (all with inert defaults) and no agent ever did the wiring
# [measured - w2_materials_v1.md §0 "Nothing was wired", not mentioned in w2_surgeon_v1.md].
# It is wired here.
#
# The values are exactly the §1.6(b) table: (file, bump, 1/tile [1/m]).
# [GT-113 W2] mineral 12.5 -> 4.0 / granular 8.0 -> 3.0. The spec-table values put the
# texel at 0.078/0.12 mm — sub-pixel at every judged eye (the `NEGOBS_DETAIL_SCALE` note
# below already called this out and recommended 2-4), and in practice every round script
# since GT-108 masked them with a blanket `NEGOBS_DETAIL_SCALE=2` override, which in turn
# nullified the per-class `det_scale` GT-108 authored. The family defaults now sit inside
# the recommended 1-4 band themselves (matching GT-108's explicit class values: paving/
# concrete 4.0, asphalt 3.0), the standing override is removed from `run_data_render.py`,
# and the env knob returns to its designed role: an A/B sweep arm only.
# metal 25.0 is kept — brushed scratches are legitimately fine and were never flagged.
_DETAIL_MAP = {
    "mineral":  ("detail_grain_mineral_nor.png",  0.85, 4.0),   # Paving, concrete, stone, curb, nosing
    "granular": ("detail_grain_granular_nor.png", 0.70, 3.0),   # Soil, gravel, asphalt, snow
    "metal":    ("detail_grain_brushed_nor.png",  0.55, 25.0),  # Metal (anisotropic scratches)
}
# When procedural generation fails or nothing was procured - what the repository already holds (0 procurement). §3.2 confirmed both families pass.
_DETAIL_FALLBACK = {
    "mineral":  ("scene01/plaster_nor_dx.jpg", 0.85, 4.0),    # [GT-113 W2] follows _DETAIL_MAP
    "granular": ("scene01/asphalt_nor_dx.jpg", 0.70, 3.0),
    "metal":    (None, 0.0, 0.0),                             # Nothing held at all (§3.2)
}
# Class -> family. **A class absent from here is explicitly prescribed no detail**:
#   veg, water, glass, paint, sign, misc = paint and signs must stay uniform to work as cues (v5.1 §4)
#   wood = the grain is directional, so an isotropic grain on top erases it instead (§1.6(b))
_DETAIL_FAMILY = {"paving": "mineral", "concrete": "mineral", "brick": "mineral",
                  "stone": "mineral", "curb": "mineral", "nosing": "mineral",
                  "soil": "granular", "gravel": "granular", "asphalt": "granular",
                  "snow": "granular", "metal": "metal"}

# A/B sweep knobs - a render round must be able to switch arms without editing code.
#   `NEGOBS_DETAIL_SCALE`      : global override of `detail_texture_scale` [1/m].
#       Basis = w2_materials_v1.md §7 R1 - at the spec default of 12.5 (= an 8 cm tile) a texel is
#       0.078 mm, i.e. **sub-pixel** at h0.3 d2 (effective micro-slope 0.49 deg, below the 1.4 deg that §1.2
#       judged "invisible"). Lowering it to 2-4 raises the dominant band to 0.5-3 mm
#       (real concrete aggregate size).
#   `NEGOBS_DETAIL_ROUGH_GAIN` : `detail_rough_gain`. The physically correct path for carrying
#       sub-pixel microstructure through roughness variance (§7 R1 (a), MDL S5).
def _envf(name, default=0.0):
    try:
        return float(os.environ.get(name, "") or default)
    except ValueError:
        return float(default)


DETAIL_SCALE_OVERRIDE = _envf("NEGOBS_DETAIL_SCALE", 0.0)   # 0 = use the table value
DETAIL_ROUGH_GAIN = _envf("NEGOBS_DETAIL_ROUGH_GAIN", 0.0)  # 0 = off (MDL default)
#   `NEGOBS_DETAIL=0` : turns off the detail normal only (the rest of the material layer stays). The third
#       arm that isolates **how much of the LOOK_MTL effect belongs to the detail normal** - without it
#       "the material layer moved" gets misattributed to "the detail moved".
DETAIL_ON = os.environ.get("NEGOBS_DETAIL", "1") != "0"


def detail_source(cls):
    """Class name -> `(absolute path, bump, 1/tile)`. Detail-forbidden classes get `(None, 0, 0)`.

    First choice is the procedural generation (§3.3), then the fallback held in the
    repository (§3.2), then no effect.
    A missing file is **silently skipped** (per the §1.6(b) comment) - a wiring failure must
    not kill the render, and binding a nonexistent file would be harmless anyway since the
    MDL returns early, but it would leave a ghost path in the USD.
    """
    if not DETAIL_ON:
        return (None, 0.0, 0.0)
    fam = _DETAIL_FAMILY.get(cls)
    if fam is None:
        return (None, 0.0, 0.0)
    rel, bump, inv = _DETAIL_MAP.get(fam, (None, 0.0, 0.0))
    p = os.path.join(ASSETS_DIR, rel) if rel else None
    if not (p and os.path.isfile(p)):
        rel, bump, inv = _DETAIL_FALLBACK.get(fam, (None, 0.0, 0.0))
        p = os.path.join(ASSETS_DIR, rel) if rel else None
        if not (p and os.path.isfile(p)):
            return (None, 0.0, 0.0)
    # [GT-108 ②] Per-class `det_scale` [1/m]. Stated by `asphalt` only; every other class
    # keeps the `_DETAIL_MAP` family value, so this is bit-identical outside asphalt.
    # The env sweep knob still wins over both - it is the A/B arm.
    _cs = (LOOK_CLASS.get(cls) or {}).get("det_scale")
    if _cs:
        inv = float(_cs)
    if DETAIL_SCALE_OVERRIDE > 0.0:
        inv = DETAIL_SCALE_OVERRIDE
    return (p, float(bump), float(inv))

# Corrects the difference in texture_scale meaning between OmniPBR (cubic projection) and NegObsGround (triplanar).
# Getting this wrong is a **global regression that misaligns the tile scale of every ground surface**, so no guessing -
# it was measured with a dedicated calibration render (spike lab E10: interlocking paving blocks laid left and right
# at the same scale_m, comparing the autocorrelation pixel period in a vertical top-down view).
#
#   1st measurement (MDL v1.4.0): OmniPBR 23.163/23.164 px vs MDL 26.454/32.764 px
#     -> the ratio differed per axis (anisotropic) and by eye **the pattern was rotated 45 deg**.
#       The cause was not the scale but a basis-selection bug in the MDL (see below).
#   2nd measurement (MDL v1.5.0, after the fix): 23.163/23.164 vs 23.154/23.177
#     -> **ratio 1.0001. No correction needed.**
#
# So the first observation that "the scales differ" was a **misdiagnosis**; the real cause was a
# degeneracy where a 45 deg auxiliary basis was mixed in 50:50 on horizontal surfaces (fixed in MDL v1.5.0).
_GROUND_SCALE_FIX = 1.0        # Confirmed by the E10 2nd measurement (ratio 1.0001)

# --- Per-class look specs ---------------------------------------------------
# bevel[m] : round_edges_radius. Phase1 §2.1 measurement - on-screen width ~= 24*(r/d)*57.3 px.
#            The brief's original proposal (3 mm on concrete) is sub-pixel at the 2-10 m robot
#            viewpoint, so it costs without being visible.
#   **Domestic standards survey applied** (`Docs/surveys/.../I_ks_dimension_verification.md`):
#     - cast-in-place concrete corner **20-30 mm** - KCS 21 50 05:2023 3.3(10), verbatim.
#       Our concrete is retaining walls, stair risers and embankments = mostly cast in place, so **0.020**.
#       (The supervisor's provisional 10 mm was 1/2 to 1/3 too small. 10 mm is right for precast.)
#     - vertical curb **R=10** - MOLIT directive no. 321, sidewalk installation guideline, figure 2.17
#     - metal **2 mm** - KS B 0403 chamfer series, 2nd column standard value (provisional value confirmed)
#     - stair nosing - **no domestic rule** (all 4 statutory documents checked). The value uses the top of
#       the IBC 1.6-14.3 mm range, **with the source explicitly noted as non-domestic**.
#     - general stone - **no basis**. Kept conservatively low.
# sat      : saturation coefficient (MDL only). A global reduction is banned - scene01 is already at 0.146,
#            below the floor. Over-saturation is a local phenomenon of the stone, plant and soil families.
# mdl      : "ground" = NegObsGround / "omni" = OmniPBR
# patch    : NegObsGround patch rotation strength. 0 for modular paving (protects the pattern), 1 for natural.
# Per-role weathering values (MDL v1.6.0) - a missing key means all 0 (no effect).
#   **Critical warning**: the plinth grime band is referenced to **absolute world Z**. Ground prims sit at z~=0,
#   so enabling grime puts them entirely inside the band and **darkens the whole ground uniformly** (a global regression).
#   -> the ground family (paving/asphalt/soil/gravel) **must** have grime/splash at 0.
#   The band belongs only to **vertical structures standing on the ground** (retaining walls, plinths, parapets, curbs, stair risers).
# [fatal C4 fix] **World-z based weathering (grime, splash) is fully disabled.**
#   The `grime_z0` default is 0.0 and scene_common never set it, so
#   m_grime = 1 - smoothstep(0, h, z) applied uniformly to **every surface with z <= 0**.
#   Blocking by class alone was attempted, but concrete absorbs 46 of the 215 kinds and includes
#   **horizontal ground** such as `Slab`, `LowerFloor`, `Lower` and `Trough`, so the defence was breached.
#
#   This is not a mere look bug - like the sceneD3 gutter (depth 0.80, invert -1.05) it becomes a
#   **deterministic albedo rule where a deeper drop is darker**, creating a **synthetic shortcut**
#   correlated with the GT drop. That is the failure mode this project guards against most.
#
#   Reactivation condition: once there is a channel to pass a per-prim foot z as `grime_z0`.
#   Normal-based items (streak = run-down on vertical faces, dust = dust on upward faces) are z-independent and stay.
_W_STRUCT = dict(grime=0.0, splash=0.0, streak=0.12, wrough=0.15)
_W_STONE = dict(grime=0.0, splash=0.0, streak=0.08, wrough=0.12)
_W_EDGE = dict(grime=0.0, splash=0.0, wrough=0.10)

# --- `alb_max` / `alb_min` - per-class effective albedo band  [GT-108 ①②] -----
# `s04_quality_gap_survey_v1.md` §5 F2 measured the mechanism: when the display value
# clips at the top of the tone map the per-channel differences die with it, so
# **a texture laid on a near-white surface still returns local sd ~0** (t1 §5.1:
# w80 vs sat_mu Spearman **-0.630** over 33 scenes). Lowering the albedo is what brings
# saturation and local contrast back - raising saturation is the banned direction.
# The same mechanism runs the other way at the dark end: at an effective albedo of
# 0.028-0.045 (the carriageways, §3.5) the texture's own contrast is multiplied down
# with the mean and `micro_sd` collapses to **0.52**, the lowest surface in the repo.
#
# So the band is applied to the **effective linear albedo** (texture mean x base_color x
# tint) - the number that actually reaches the frame - not to whatever the scene author
# happened to type. Channels are scaled by one scalar, so **hue is preserved** (scene13's
# `asphalt_tint[2] < [0]` blue-cast self-check reads the scene parameter and is untouched).
#
# Values [computed - texture linear means measured this session, 64px thumbnails,
#         sRGB->linear per IEC 61966-2-1; physical bands from LBNL Heat Island Group /
#         ACPA RT3.05, the same source t1 §5.2 cites]:
#   ceiling **0.34**  - grey portland concrete solar reflectance: new 0.35-0.40,
#     aged 0.20-0.30; only white cement reaches 0.70-0.80. 0.34 lands just under
#     "new grey", i.e. t1 §5.2's landing point for T-1.
#     Calibration check: `plaza_light` linear luminance **0.468** [measured] x T-1's
#     approved 0.72 = **0.337** -> the ceiling reproduces T-1 to within 1 % **for all
#     9 untinted-plaza_light scenes at once**, which is exactly the "9 scenes in one
#     commit" condition t1 §5.2 attached to T-1. Anything already at or below the
#     ceiling is passed through untouched, so scene16's `Stair` (already tinted to
#     0.333) and its three street-wall shells (0.225/0.316/0.351-brick) do not move
#     and the OCCL <25 constraint on the shaded facades is not disturbed.
#   floor **0.10**    - aged asphalt concrete 0.10-0.18 (new 0.04-0.05); applied as a
#     **geometric-mean soft floor**, so it is a target the dark end is pulled towards,
#     not a value everything lands on - see `_albedo_band` for why the two ends differ.
#     Every
#     carriageway in the repo is an existing street, none is a fresh overlay, yet the
#     measured effective albedos are 0.028 (s13) / 0.045 (s11) / 0.058 (s16) - i.e. all
#     three sit **below new-laid asphalt**. This is the "등화 틴트" half of GT-107's
#     carried-over finding: the promotion multiplier preserves the mean and therefore
#     scales the texture's absolute contrast down with it.
_ALB_BAND_LUMA = (0.2126, 0.7152, 0.0722)      # Rec.709 linear luminance


def _albedo_band(cls, rgb, tex_mean=None):
    """Clamp the effective linear albedo of `rgb` into the class band.

    `rgb` is the `base_color` multiplier; `tex_mean` the bound texture's linear mean
    (None for a constant-colour material, where `rgb` *is* the albedo). Returns
    `(rgb, changed)`. Hue is preserved - one scalar on all three channels.

    **The two ends are deliberately not symmetric.**
      - The ceiling is **hard**: t1 §5.2 prescribes a definite landing value (T-1's
        x0.72 -> 0.338) rather than a direction, and the materials that hit it are
        overwhelmingly one shared kit constant repeated across scenes (17 of the 20
        `Parapet` hits are the identical 0.718), so there is no authored tonal
        structure up there to protect.
      - The floor is **soft - the geometric mean** `sqrt(eff * alb_min)`. A hard floor
        would be wrong here because scenes *do* author structure at the dark end:
        sceneN2's subject is a fresh / cured / aged asphalt patch ladder at 0.030 /
        0.050 / 0.068, and a fresh saw-cut patch really is 0.03-0.05 (GT-107 §Scope ②
        kept that vocabulary on purpose). The geometric mean is monotone and maps a
        ratio r to sqrt(r), so the ladder survives - 0.030/0.050/0.068 lifts to
        0.055/0.071/0.083 with its ordering and roughly 3/4 of its spacing intact
        `[computed]` - while the field carriageways still gain 31-62 %.
    """
    spec = LOOK_CLASS.get(cls) or {}
    hi = spec.get("alb_max")
    lo = spec.get("alb_min")
    if hi is None and lo is None:
        return rgb, False
    eff = list(rgb) if tex_mean is None else [c * m for c, m in zip(rgb, tex_mean)]
    lum = sum(c * w for c, w in zip(eff, _ALB_BAND_LUMA))
    if lum <= 1e-6:
        return rgb, False
    k = 1.0
    if hi is not None and lum > hi:
        k = hi / lum
    elif lo is not None and lum < lo:
        k = math.sqrt(lo / lum)             # geometric-mean soft floor
    if abs(k - 1.0) < 1e-4:
        return rgb, False
    LOOK_STATS["alb_band"] = LOOK_STATS.get("alb_band", 0) + 1
    return [c * k for c in rgb], True


LOOK_CLASS = {
    #                    bevel   sat   mdl        patch  detail
    # Individual chamfering of paving blocks **has no published domestic figure** (the body of KS F 4419 is paywalled,
    # and an exhaustive check of public documents citing it found 0 chamfer clauses - the survey concluded "do not estimate").
    # Moreover round_edges applies to the **slab prim boundary**, not to individual blocks.
    # Individual block chamfers are already handled by the texture normal map, so the value here is for the slab
    # boundary and is kept below the curb (10 mm). [no basis - conservative choice]
    # [GT-108 · survey §5 F3 / §7 pilot-A item 2] Grain recalibration for the two ground
    # classes the pilot names alongside `asphalt` ("`concrete`/`paving`/`asphalt` 의
    # `bump`·`detail`·`patch`·`tri_dither`·틴트 재보정"). Ledger row 64 ② states the
    # carriageway numbers, but the pass line it sets — near-field `micro_sd` >= 8 on
    # **s16, whose judged crop is plaza paving, not carriageway** — is only reachable
    # through these. Measured starting point: s16 `approach` crop `micro_sd` 4.89,
    # `tile_peak@8px` 0.843 [measured this session, `scripts/quality_metrics_probe.py`].
    #   `det_scale` **4.0**: the family default 12.5 means an 8 cm tile, i.e. a 0.078 mm
    #     texel — the `NEGOBS_DETAIL_SCALE` note above already calls that sub-pixel
    #     (effective micro-slope 0.49 deg vs the 1.4 deg §1.2 judged visible) and already
    #     recommends "2-4" to put the dominant band on real 0.5-3 mm aggregate. 4.0 is the
    #     conservative end of that band. The env knob remains the A/B arm, so a round can
    #     sweep or revoke this without a code edit.
    #   `tri_dither` 0.35 -> **0.50**: at a 0.15 m wavelength this is, with normal
    #     strength, one of only two knobs inside the 5x5 px window the metric measures
    #     (§5 F3: "14 m 매크로는 micro_sd 를 못 올린다").
    #   `bump` paving 1.4 -> 1.8 / concrete 1.6 -> 2.0: same reasoning as the existing
    #     concrete note ("in shadow the grain only comes out through normal contrast").
    #   `patch` is **not** touched for either - both are 0 on purpose (modular paving;
    #     rotating patches fragments the block pattern, supervisor measurement E9).
    #   sceneC2 is not exposed: §5 F3 warns a blanket raise would worsen its leaf ground,
    #   but that ground is `soil`/`veg`, and neither is touched here.
    "paving":   dict(bevel=0.006, sat=1.00, mdl="ground", patch=0.0, detail=True,
                     tex="paving_interlock", bump=1.8, alb_max=0.34,
                     tri_dither=0.50, det_scale=4.0, macro_wl=0.55,
                     tex_alts=("stone_flag", "paving_interlock", "plaster")),
    "concrete": dict(bevel=0.020, sat=1.00, mdl="ground", patch=0.0, detail=True,
                     weather=_W_STRUCT, tex="concrete_floor", bump=2.0,
                     alb_max=0.34, tri_dither=0.50, det_scale=4.0, macro_wl=0.55,
                     tex_alts=("concrete_floor", "concrete_wall", "plaster")),
                     # concrete_wall(c@1/16 0.0345) → concrete_floor(0.129, x3.7).
                     # Diagnosis: if the local contrast of the promoted texture is low, promotion does not bring out the grain.
                     # Cast in place 20-30 mm (KCS 21 50 05). bump 1.6 = diagnosis P3
                     # (in shadow the grain only comes out through normal contrast, not brightness)
    "brick":    dict(bevel=0.006, sat=0.88, mdl="ground", patch=0.0, detail=True,
                     tex="brick_red", bump=1.4, tex_alts=("brick_red", "plaster"),
                     weather=dict(grime=0.0, splash=0.0, streak=0.10,
                                  wrough=0.15)),
    "stone":    dict(bevel=0.004, sat=0.66, mdl="ground", patch=1.0, detail=True,
                     weather=_W_STONE, tex="stone_flag", bump=1.5, alb_max=0.34,
                     macro_wl=0.55,
                     tex_alts=("stone_flag", "marble_light")),
                     # Bevel [no basis] conservatively lowered
                     # alb_max: granite / 화강석 cladding reflectance 0.20-0.35, so the
                     # shared 0.34 ceiling sits at the top of the real band. Only
                     # `marble_light` (measured linear 0.350) is above it at all, and
                     # then by 3 % - the class is effectively pass-through today
                     # [computed]. It is stated so a future bright stone cannot walk in.
    "soil":     dict(bevel=0.000, sat=0.74, mdl="ground", patch=1.0, detail=True,
                     tex="dirt_park", bump=1.4,
                     tex_alts=("dirt_park", "gravel")),
    "gravel":   dict(bevel=0.000, sat=0.78, mdl="ground", patch=1.0, detail=True,
                     tex="gravel", bump=1.4),
    # tex: promote a constant-colour material to the texture of this TEX role (the intended albedo is preserved).
    # [GT-108 ② · GT-107 carried-over finding] Carriageway recalibration. The measured
    # body of the finding is `s04_quality_gap_survey_v1.md` §3.5: the s13 carriageway is
    # `micro_sd` **0.52** / `flat%` **65.5** - the lowest surface measured anywhere in the
    # repo - **while carrying a real texture**. So the defect is not "no map", it is that
    # every one of the four knobs that can carry grain was working against it:
    #   (a) effective albedo 0.028 [computed: gravel linear mean (0.389,0.262,0.155) x
    #       scene tint (0.148,0.150,0.154)] = darker than new-laid asphalt, so the map's
    #       own contrast is multiplied down with the mean       -> `alb_min` 0.10 (see band note)
    #   (b) `patch_mix` 1.0 at a **4.0 m** wavelength on a carriageway = rotation cells the
    #       size of a wheel track. The dry probe located the "카펫 러너" at y +-1.48 m
    #       (2.96 m apart) with **no prim there** - i.e. it was this cell grid, not geometry
    #                                                            -> patch 0.45 @ **1.8 m**,
    #       small enough that no cell can line up into a longitudinal runner, still ~5
    #       tiles per cell at the 0.35 m/tile the scenes use, so repetition break-up survives.
    #   (c) `macro_amp` 0.12 at 14 m = a half-road brightness swell, the second long-wave
    #       band the eyes read as "one lane is paler"           -> macro 0.06
    #   (d) the only knobs that live in the 5x5 px window `micro_sd` measures are
    #       `tri_dither` (0.15 m), normal strength and roughness noise (§5 F3 states this
    #       explicitly: "14 m 매크로는 micro_sd 를 못 올린다")   -> tri_dither 0.35 -> 0.55,
    #       bump 1.4 -> 2.1, rough_noise 0.22 -> 0.34, and the granular detail normal off
    #       its sub-pixel default (1/tile 8.0 = 12.5 cm tile, texel 0.12 mm) down to
    #       **3.0** = a 33 cm tile, inside the 2-4 band the `NEGOBS_DETAIL_SCALE` note
    #       already recommends for exactly this reason.
    # `asphalt_scale` is **not** touched - GT-107 §3 ruled it stays at 0.35 m/tile.
    # spec/bump: diagnosis P1/P3 - the road surface is excessively bright because of grazing gloss, so
    # specular_level is stated explicitly and shadow contrast is restored through normal strength.
    "asphalt":  dict(bevel=0.006, sat=0.90, mdl="ground", patch=0.45, detail=True,
                     tex="asphalt", spec=0.20, bump=2.1, alb_min=0.10,
                     patch_wl=1.8, macro=0.06, macro_wl=0.55, tri_dither=0.55,
                     rough_noise=0.34, det_scale=3.0),
    # [GT-114 ①] This class is now the **non-slip strip only** — GT-113 W6 moved
    # tread/step names to the concrete family, so the 12 mm IBC nosing radius (a
    # *tread-nose* figure) no longer belongs here: on a 6 mm strip it rolled the whole
    # normal ("반투명 젤리"). 3 mm ≈ strip thickness / 2. Promotion + detail open the
    # grain path for the drop edge's primary cue class; alb_max 0.50 backstops the
    # pastel-lemon default this row also retires in `build_nosing`.
    "nosing":   dict(bevel=0.003, sat=1.00, mdl="ground", patch=0.0, detail=True,
                     tex="concrete_floor", det_scale=4.0, alb_max=0.50,
                     macro_wl=0.55,
                     weather=dict(grime=0.0, splash=0.0, wrough=0.10)),
    # [GT-114 ②] The curb promotion path — the GT-108 lever-1 carry-over item. A
    # constant-colour curb could never promote (no tex role), so the second most
    # important drop-edge cue class was the least treated surface in the corpus.
    "curb":     dict(bevel=0.010, sat=1.00, mdl="ground", patch=0.0, detail=True,
                     tex="concrete_floor", det_scale=3.0, alb_max=0.34,
                     macro_wl=0.55,
                     tex_alts=("concrete_floor", "granite_dark"),
                     weather=_W_EDGE),   # Vertical curb R=10 (directive 321, figure 2.17)
    # [GT-114 ④] alb_max 0.50 — first value to flow through the GT-113 W1 omni wire.
    # Rails at 0.818 / lamp posts at 0.877 linear were the corpus' pure-white metal
    # band (galvanised/powder-coated reality is 0.35-0.55 diffuse). Painted bands,
    # signs and tactile stay constant — they are different classes.
    "metal":    dict(bevel=0.002, sat=1.00, mdl="omni",   detail=True,
                     alb_max=0.50),
    # The library has only one dark wood (wood_dark, linear luminance 0.061), so bright
    # wood gets a large multiplier. Wood grain is strongly directional and stays quiet under
    # amplification, so the cap is raised for this class only.
    "wood":     dict(bevel=0.004, sat=0.88, mdl="omni",   detail=True,
                     tex="wood_dark", bump=1.3, max_gain=7.0),
    # [W2, audit B A2] **`leaf_ground` removed from `tex_alts`** - blocks a fatal seasonal-convention violation.
    #   Promotion is accepted when `max(ratio) <= max_gain` **and** `spread = max/min <= 4.0`, but
    #   the old `grass` (aerial_grass_rock) has an empty blue channel (red/blue 7.03) and was rejected at
    #   spread 4.22 on green canopy constant colours, so `leaf_ground` (red/blue 4.09 -> spread 2.86) was
    #   chosen instead. Simulating all 33 scenes gives **50 `leaf_ground` promotions across 24 scenes** - i.e.
    #   the tree canopies of 24 scenes were being painted with **autumn leaf pixels** (a 2.3 m leaf source at 52 % size)
    #   [measured - `B_groundcover_debris.md` §8].
    #   A1 (the Grass001 replacement) alone lowers the spread enough for grass to be chosen, but as long as
    #   `leaf_ground` stays in the list **dark constant colours still fall to it.** A2 removes that path
    #   physically - both are done.
    #   `tex_scale` 1.2 -> **1.4**: the promotion path must follow the measured Grass001 tile too.
    #   `detail=False` is kept (leaves are handled by the real USD asset - §2.1).
    # [W2 fix batch F1] `max_spread` 3.0 - see `_promote_const_to_texture`. The grass
    #   texture's blue channel is nearly empty, so a **low-saturation grey-green**
    #   constant (scene11's `leaf_far_*` aerial-perspective band) promotes with a
    #   2.9-3.8x blue multiplier: the mean colour is right but the per-pixel blue noise is
    #   amplified, which is exactly the "grey-lilac granite-speckled ball clusters"
    #   the eyes round read as a stone default (`tonglam_v2.md` §2.3).
    "veg":      dict(bevel=0.000, sat=0.76, mdl="omni",   detail=False,
                     tex="grass", bump=1.2, max_gain=7.0, tex_scale=1.4,
                     max_spread=3.0, tex_alts=("grass",)),
    # [GT-118] Horizontal large-area lawn split out of `veg`. The 3-D canopy family
    # must stay omni (real USD leaves — §2.1), but a 40 m lawn slab is *ground*: it
    # needs the triplanar projection, macro modulation (mowing/dry-patch band ~1.6 m
    # [derived]), patch rotation and saturation self-correction that the omni branch
    # never ran — the audit's "녹색 사포" / F8 root. s17 had already escaped by
    # renaming its planes `TurfSoil`; this promotes that workaround to a class.
    "turf":     dict(bevel=0.000, sat=0.76, mdl="ground", patch=1.0,
                     detail=False, tex="grass", bump=1.2, max_gain=7.0,
                     tex_scale=1.4, max_spread=3.0, tex_alts=("grass",),
                     macro=0.10, macro_wl=1.6),
    "water":    dict(bevel=0.000, sat=1.00, mdl="omni",   detail=False),
    "glass":    dict(bevel=0.000, sat=1.00, mdl="omni",   detail=False),
    "paint":    dict(bevel=0.000, sat=1.00, mdl="omni",   detail=False),
    "sign":     dict(bevel=0.000, sat=1.00, mdl="omni",   detail=False),
    # Unknown role - conservative. No MDL swap, no saturation change, no detail normal.
    # The classifier catches 208 of 215 kinds, so what falls here is genuinely unknown, and
    # putting a concrete grain normal on such a material is damage, not improvement.
    # Snow: high reflectance, so it is not a bevel or saturation target. Only the texture is applied.
    # **Warning (survey)**: the current intended colour of 0.72-0.78 maps to display sRGB 221-229 and clips at
    # the top of the tone mapping, so even with a texture the local standard deviation returns to 0.
    # The intended albedo must be lowered to 0.55-0.62 before promotion for any effect (TODO: apply after procurement).
    # [GT-114 ③] alb_max 0.62 — the code's own TODO ("must be lowered to 0.55-0.62
    # before promotion for any effect"), applied at its conservative top now that the
    # snow texture is procured. C1's w80 81.6 % / flat_gnd 88.3 is this ceiling's case.
    "snow":     dict(bevel=0.000, sat=1.00, mdl="ground", patch=1.0, detail=True,
                     tex="snow", bump=1.3, alb_max=0.62),
    "misc":     dict(bevel=0.003, sat=1.00, mdl="omni",   detail=False),
}

# [GT-125] 물리 파라미터 값 부여 파일럿 팔 — 기본 OFF = 전 코퍼스 비트동일.
#   GT-117 은 diff_rough/grazing 스펙 키를 개방만 했다(값 0건). 이 팔이 광물·입상
#   6클래스에 값을 주입한다: Oren-Nayar σ(광물 실측 문헌 대역 0.3~0.55)는 접지각
#   자기음영을, grazing 하한대는 h0.3 지면 하늘광택("젖은 마루") 소거를 맡는다.
#   채택(기본값 승격)은 파일럿 A/B 실측 후 별행.
PHYS_V1 = os.environ.get("NEGOBS_PHYS_V1", "") == "1"
if PHYS_V1:
    for _c, _v in {"asphalt":  dict(diff_rough=0.45, grazing=0.25),
                   "paving":   dict(diff_rough=0.40, grazing=0.30),
                   "concrete": dict(diff_rough=0.40, grazing=0.30),
                   "stone":    dict(diff_rough=0.35, grazing=0.30),
                   "soil":     dict(diff_rough=0.50, grazing=0.20),
                   "gravel":   dict(diff_rough=0.55, grazing=0.20)}.items():
        LOOK_CLASS[_c].update(_v)

# --- `Looks/<name>` -> class -------------------------------------------------
# Ordered by measured name frequency. An unlisted name falls to "misc" (the conservative default).
LOOK_ROLE = {
    # Paving, plaza
    "Paving": "paving", "PlazaLight": "paving", "PlazaLower": "paving",
    "Plaza": "paving", "Deck": "wood", "Tile": "paving",
    # Concrete structures
    "Concrete": "concrete", "ConcreteWall": "concrete", "Wall": "concrete",
    "Shell": "concrete", "ShellB": "concrete", "Parapet": "concrete",
    "Stage": "concrete", "Upper": "concrete", "Lower": "concrete",
    "Stair": "concrete", "Riser": "concrete", "Slab": "concrete",
    "Fascia": "concrete", "Pier": "concrete", "Abutment": "concrete",
    # Stone
    "Granite": "stone", "GraniteDark": "stone", "Marble": "stone",
    "Rock": "stone", "Stone": "stone", "Sandstone": "stone",
    "RockWall": "stone", "Flag": "stone",
    # Brick, rendered wall
    "Brick": "brick", "Plaster": "brick",
    # Natural ground cover
    "Soil": "soil", "Dirt": "soil", "Gravel": "gravel", "Sand": "soil",
    "Asphalt": "asphalt",
    # Drop edge - the brief §2.1 approved value (nosing 12 mm)
    "Nosing": "nosing", "Curb": "curb", "Edge": "nosing",
    # Metal
    "Rail": "metal", "Steel": "metal", "Pole": "metal", "Post": "metal",
    "Lamp": "metal", "Bollard": "metal", "BollardBand": "paint",
    # [GT-108 ④ · survey §8-4 ①] `"Roof": "metal"` **deleted here**. It was a dead dict
    #   entry - the same key is re-stated as `"Roof": "wood"` further down (the "2nd
    #   diagnosis" block), and in a dict literal the last write wins, so `Roof` has been
    #   classifying as **wood** all along. Deleting the dead half is bit-identical and
    #   stops the table from documenting a rule the code does not run. A duplicate key
    #   is invisible to `py_compile` and to `placement_lint`, which is why it survived.
    "Grate": "metal", "Grating": "metal", "Gear": "metal",
    # Wood
    "Wood": "wood", "WoodDark": "wood", "SeatWood": "wood", "Bench": "wood",
    # Vegetation — [GT-118] Grass/GrassB are lawns -> turf; canopies stay veg.
    "Grass": "turf", "GrassB": "turf", "CanopyA": "veg", "CanopyB": "veg",
    "Leaf": "veg", "LeafA": "veg", "LeafB": "veg", "Hedge": "veg",
    "Shrub": "veg", "Reed": "veg", "Moss": "veg",
    # Water
    "Water": "water",
    # Paint and markings - a constant colour is physically correct (not to be texturised)
    # [GT-113 W6] The "band" *keyword* was removed from `_LOOK_RULES` (it swallowed
    # textured stone bands like `BandDark`), so every genuinely *painted* band is
    # pinned here by exact match instead — dock markings (BandBlack/BandYellow),
    # the gas-riser yellow band, guard and lane bands.
    "Paint": "paint", "LineWhite": "paint", "LineYellow": "paint",
    "Band": "paint", "Tactile": "paint", "BandBlack": "paint",
    "BandYellow": "paint", "GasBand": "paint", "GuardBand": "paint",
    "LineBand": "paint",
    # Glass, signs, emissive
    # [GT-108 ④ · survey §8-4 ②] `"Panel": "sign"` **deleted here** - same duplicate-key
    #   trap: `"Panel": "metal"` two lines below wins, and metal is the intended answer
    #   (`_LOOK_RULES` states it verbatim: "'panel' on its own is not a sign - in reality
    #   they were guardrail panels and shelter roofs"). scene11's `Looks/Panel` is the
    #   guard infill panel, so it was already landing on metal. Bit-identical deletion.
    "Glass": "glass", "Window": "glass",
    # Of the 7 remaining classifier kinds only the clear ones are listed (Bag/Emit/Rubber/Snow are
    # deliberately left as misc = the minimal prescription - putting a concrete grain on an unknown
    # material is worse)
    "Line": "paint", "CutLine": "paint", "Pot_": "concrete",
    "Snow": "snow", "Panel": "metal", "Iron": "metal",
    # Misclassification fixes (2nd diagnosis): Roof is a temple timber tile roof, not metal, and
    # Ridge/Crest is a natural ridge, not concrete.
    "Roof": "wood", "Roof_": "wood", "Ridge": "soil", "Ridge_": "soil",
    "Crest_": "soil", "Crest": "soil",
    "Sign": "sign", "SignFace": "sign", "SignBack": "sign",
}


# Look-layer application metering - a counter that lets one see what actually got applied.
# (It is the tool that diagnosed "the look layer is on but the numbers do not move" in the first gate.
#  The cause was that constant-colour materials were skipped entirely - and they are the main source of flat %.)
LOOK_STATS = dict(ground=0, omni_tex=0, const=0, bevel=0, detail=0, skin=0,
                  skipped=0, roles={})


def look_report():
    """One-line summary of look layer application. Printed when capture_pipeline starts.

    After the 2-stage flags were introduced, **stamping both arms** is the verification
    means of rule R-2 - the MTL/GEO state must remain in the round log so the control can
    be confirmed after the fact."""
    if not (LOOK_MTL or LOOK_GEO):
        return "[룩v1] OFF (MTL=0 GEO=0)"
    r = LOOK_STATS
    top = sorted(r["roles"].items(), key=lambda kv: -kv[1])[:8]
    # [GT-113 W2] The effective detail policy must be visible in every round log —
    # a blanket env override silently nullified per-class det_scale for six rounds
    # before anyone noticed, and the unit-cell wiring sat uncalled for a version.
    det_pol = (f"detXovr={DETAIL_SCALE_OVERRIDE:g}" if DETAIL_SCALE_OVERRIDE > 0
               else "detX=class")
    return (f"[룩v1] MTL={int(LOOK_MTL)} GEO={int(LOOK_GEO)}"
            f"{' PHYS=1' if PHYS_V1 else ''} | "
            f"재질 ground={r['ground']} omni_tex={r['omni_tex']} "
            f"const={r['const']} skip={r['skipped']} | 베벨={r['bevel']} "
            f"디테일={r['detail']} 스킨={r['skin']} "
            f"승격={r.get('promoted', 0)} 상수MDL={r.get('const_mdl', 0)} "
            f"알베도밴드={r.get('alb_band', 0)} "
            f"웨더={r.get('weather', 0)} 나무={r.get('veg_asset', 0)} "
            f"간살={r.get('baluster', 0)} 관목={r.get('shrub', 0)} "
            f"손잡이={r.get('handrail', 0)} "
            f"산포={r.get('debris', 0)} | {det_pol} "
            f"유닛셀={r.get('unit_cell', 0)} "
            f"omni탈채도={r.get('omni_sat', 0)} | 역할 "
            + ", ".join(f"{k}:{v}" for k, v in top))


# --- Keyword rule classifier --------------------------------------------
# An exhaustive repository scan found **about 200 distinct** `Looks/` names, most of them a long tail
# used only once or twice (WetRock, StoneMoss, CityParapet, LboxFrame ...). With an exact-match table alone,
# more than half of all materials fell to "misc" in the first gate (21 of 33 in scene07).
# -> **Substring rules** are applied in order to absorb the long tail.
#   Rules are checked from the top, so **put the more specific ones first**
#   (e.g. "roadpaint" is paint, plain "road" is asphalt).
_LOOK_RULES = [
    # Emissive and transparent - starting with what must be excluded from the look layer
    ("glass", ("glass", "window", "lens", "shopglass", "cityglass")),
    # "panel" on its own is not a sign - in reality they were guardrail panels and shelter roofs
    # (scene11 6.0 %, scene06 5.4 %). Signs are limited to the sign/placard family.
    ("sign", ("sign", "placard", "plaque", "lbox", "mailbox")),
    # Paint and markings - a constant colour is physically correct (not to be texturised)
    # joint/cutline = joint sealant. It used to be classified as asphalt, so **an asphalt grain was being
    # laid over the joints**. The paint family is correct.
    # [GT-113 W6] "band" removed from the keyword list — scene01's `BandDark` is a
    # *textured granite* band that the token routed to paint (mdl=omni, detail off,
    # bevel 0). Painted-band materials keep their exact-match keys (`Band`,
    # `BollardBand`) and the narrowed tokens below; `BandDark` now falls through to
    # the concrete family via its "dark" token, which is the ground treatment it
    # always needed. "dancheong" added — DancheongRed is temple paintwork, not
    # concrete. "awning" added ([W6] it sat in the concrete family, so shop awnings
    # were rendering with a concrete-floor grain; fabric is closest to the paint
    # prescription: omni, constant colour, no mineral detail).
    ("paint", ("paint", "linewhite", "lineyellow", "roadpaint", "tactile",
               "warn", "tape", "warnband", "bollardband", "stripe", "gauge",
               "joint", "cutline", "lane", "dancheong", "awning")),
    # Vegetation
    # [GT-113 W6] "canopy" removed — structural shelter/roof canopies (scene16's
    # `Canopy`, bus-shelter roofs) matched it and became *grass promotion candidates*.
    # Real tree canopies keep their exact-match keys (`CanopyA`, `CanopyB`).
    # [W5] "forest", "scrub", "lily" added (scene07/09 backdrop vegetation fell to misc).
    # [GT-118] lawns before the canopy family — "grass"/"turf"/"lawn" are ground.
    ("turf", ("grass", "turf", "lawn")),
    ("veg", ("leaf", "hedge", "shrub", "foliage", "reed",
             "tuft", "tree", "moss", "treeline", "treepit", "verge",
             "forest", "scrub", "lily")),
    # Snow - the **largest single-material area across all 33 scenes** (sceneC1 88.5 %), yet it was stuck in misc
    # and received neither the constant-colour MDL nor a texture promotion.
    ("snow", ("snow", "frost")),
    # Water
    ("water", ("water", "sea", "tide", "wet")),
    # Metal
    # [GT-113 W5] "pipe" (scene15 gas risers), "gantry" (scene13 — survey §8-4 ④
    # confirmed unintended misc) added.
    ("metal", ("rail", "steel", "iron", "metal", "pole", "post", "lamp",
               "bollard", "gate", "fence", "grate", "grating", "galv",
               "rebar", "wire", "cable", "hvac", "crane", "gear", "shutter",
               "mullion", "frame", "bin", "lid", "duck", "tool", "beak",
               "pipe", "gantry")),
    # Wood
    # [GT-113 W5] "plank" (scene12's walking surface fell to misc), "joist" added.
    ("wood", ("wood", "deck", "bench", "seat", "sleeper", "pallet",
              "stringer", "carton", "door", "plank", "joist")),
    # Drop edge - approved nosing 12 mm / curb 12 mm
    # [GT-113 W6] "tread"/"step" removed — a tread is the walking slab itself
    # (concrete/stone family), and routing it here gave the whole step face the
    # nosing prescription: no texture role, no tex_alts, so constant-colour treads
    # could never promote and stayed dead flat — on the very surface this dataset
    # teaches. They now land in the concrete family (last rule, tokens added there).
    ("nosing", ("nosing",)),
    # **"verge" removed** - the Verge* materials of scene04 are grass verges (vegetation) yet were
    # receiving the curb prescription (13.4 % of the area). English verge means a shoulder or grass margin, not a curb.
    ("curb", ("curb", "coping", "cope", "kerb")),
    # Stone
    ("stone", ("stone", "granite", "marble", "rock", "flag", "cobble",
               "polish", "lightstone")),
    # Brick, rendered wall
    ("brick", ("brick", "plaster")),
    # Soil, gravel
    # [GT-113 W5] "hill"/"shore"/"terrain" — scene09's backdrop landforms fell to misc
    # and rendered as untreated constants (survey F8's code root). Landform = soil.
    ("soil", ("soil", "dirt", "earth", "mud", "leafbed", "hill", "shore",
              "terrain")),
    ("gravel", ("gravel", "ballast", "debris", "rubble")),
    # Asphalt, carriageway
    # "lane" and "joint" moved to paint (lane dashes, joint sealant).
    # Previously lane markings were classified as asphalt and became **targets for asphalt texture promotion** -
    # a head-on violation of the v5.1 §4 constant-colour rule (paint must stay uniform to work as a cue).
    ("asphalt", ("asphalt", "road", "patch")),
    # Paving
    ("paving", ("pav", "plaza", "walk", "sidewalk", "tile", "block",
                "apron", "alley", "podium", "platform")),
    # Concrete structures - the widest net, so it comes last
    # [W2 fix batch F1] **Ground-decal vocabulary added.** The whole "constant-colour
    #   family" the W2-D eyes round found (`tonglam_v2.md` §2.13-1) has a single cause:
    #   the kit's ground-class decal materials - `Coating` (scene19 roof membrane),
    #   `GKitStain` (18/19 stains, seams, wear, cracks), `GkWear` (07/10), `GKitSalt`
    #   (18 efflorescence) - matched **no rule at all** and fell to `misc`, which is
    #   excluded from `_CONST_MDL_CLASSES`, so every one of them rendered as a
    #   texture-less OmniPBR constant. scene19's membrane is the extreme case
    #   (`flat_gnd` 94.8, `edge%` 1.4 - an unlit CAD plane).
    #   These are ground-class surfaces, so they belong in the concrete family: they get
    #   texture promotion, the bevel and the detail normal like any other ground prim.
    #   Ordering safety: `concrete` is the **last** rule, so more specific earlier rules
    #   still win - `StoneStain` stays stone, `Asphalt` stays asphalt, `GkMoss` stays veg.
    # [GT-113 W5/W6] "awning" moved to paint (fabric ≠ concrete grain). "tread"/"step"
    # arrive here from the nosing rule (walking slabs are the concrete family).
    # "hill"/"shore"/"terrain" (scene09 backdrop landforms), "basement"/"booth"
    # (scene06/13 interiors), "mortar" (BedMortar) added — all were misc fall-throughs
    # rendering as untreated OmniPBR constants (survey W5). "canopy" stays here so the
    # structural canopies that used to mis-route to veg get the concrete treatment.
    ("concrete", ("concrete", "conc", "wall", "parapet", "shell", "slab",
                  "stair", "riser", "skirt", "fascia", "ceiling", "facade",
                  "bldg", "city", "house", "shed", "tunnel", "bridge",
                  "pier", "abutment", "crest", "ridge", "trough", "valley",
                  "container", "stage", "upper", "lower", "roof", "canopy",
                  "trim", "grime", "dark", "skyline", "far",
                  "coating", "membrane", "stain", "wear", "crack", "silt",
                  "efflor", "salt", "tread", "step",
                  "basement", "booth", "mortar")),
]



# --- Saturation self-correction -----------------------------------------
# Per-role coefficients alone are not enough. As Phase0 already showed, scene01 has sat_mu of
# 0.146, i.e. **already below the target floor (0.15)**, and the role coefficients know nothing about the
# scene state, so applying them directly desaturates further (measured: 0.146 -> 0.134). Over-saturation is a
# **local phenomenon** of the stone, soil and plant families, not a global one.
# -> Look at **the material's own saturation** and lower it only when over-saturated. Being self-correcting,
#   it needs no scene information and leaves already-desaturated materials alone.
# [major M5] The old 0.30 was **above the texture saturation distribution**, so the stone (0.66), asphalt (0.90)
# and paving coefficients effectively never fired. It was also a unit mismatch: a render-space sat_mu threshold
# transplanted straight into texture space.
# Real photographs (n=54) have sat_mu 0.232+-0.071 and texture saturation itself comes out lower than that.
# -> The knee is lowered to a texture-space basis.
_SAT_KNEE = 0.18
_TEXSAT_CACHE = {}


def _rgb_sat(rgb):
    mx, mn = max(rgb), min(rgb)
    return 0.0 if mx <= 1e-6 else (mx - mn) / mx


def _texture_sat(path):
    """Mean texture saturation. Computed from a downscaled PIL load and cached (a few per scene)."""
    if path in _TEXSAT_CACHE:
        return _TEXSAT_CACHE[path]
    v = None
    try:
        from PIL import Image
        with Image.open(path) as im:
            im = im.convert("RGB")
            im.thumbnail((64, 64))
            a = np.asarray(im).astype(np.float64) / 255.0
        a = np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)
        mx = a.max(-1)
        mn = a.min(-1)
        v = float(np.where(mx > 1e-6, (mx - mn) / np.maximum(mx, 1e-6), 0).mean())
    except Exception as e:
        print(f"[룩v1][경고] 텍스처 채도 계산 실패 {os.path.basename(path)}: {e}")
        v = None
    _TEXSAT_CACHE[path] = v
    return v


def _effective_sat(spec, diff, base_color):
    """Effective saturation coefficient, applying the role coefficient **only when over-saturated**.

    A return of 1.0 keeps the original. If the material saturation is unknown, it is
    conservatively 1.0 (no effect).
    """
    coef = float(spec.get("sat", 1.0))
    if coef >= 0.999:
        return 1.0
    cur = (_rgb_sat(base_color) if base_color is not None
           else (_texture_sat(diff) if diff else None))
    if cur is None or cur <= _SAT_KNEE:
        return 1.0                          # Already desaturated -> leave it alone
    # Apply only in proportion to the excess over the knee (avoids an abrupt step)
    t = min(1.0, (cur - _SAT_KNEE) / 0.20)
    return 1.0 + (coef - 1.0) * t


# Upper bound of the promotion multiplier. Above it, promotion is abandoned (colour distortion < grain gained).
# The brightness branch keeps the multiplier near 1, so it rarely triggers in practice.
_PROMOTE_MAX_GAIN = 4.0
_TEXMEAN_CACHE = {}


def _texture_mean(path):
    """Mean texture RGB (0-1). Downscaled PIL load plus cache."""
    if path in _TEXMEAN_CACHE:
        return _TEXMEAN_CACHE[path]
    v = None
    try:
        from PIL import Image
        with Image.open(path) as im:
            im = im.convert("RGB")
            im.thumbnail((64, 64))
            a = np.asarray(im).astype(np.float64) / 255.0
        # [fatal, colour space] The MDL reads diffuse with colorSpace="auto", i.e. **decodes it
        # linearly**, and then multiplies base_color. Previously the JPEG was averaged here
        # **in its sRGB-encoded values**, giving base_color = intended colour / sRGB mean.
        # That mixes two spaces, so promoted materials came out **2.06 to 3.64 times darker**.
        # It is the direct cause of scene07 regressing from 9.51 to 10.00.
        # -> Convert sRGB to linear before averaging (IEC 61966-2-1).
        lin = np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)
        v = tuple(float(x) for x in lin.reshape(-1, 3).mean(0))
    except Exception as e:
        print(f"[룩v1][경고] 텍스처 평균 계산 실패 {os.path.basename(path)}: {e}")
        v = None
    _TEXMEAN_CACHE[path] = v
    return v


def _promote_const_to_texture(spec, diffuse_color):
    """[realism v1] Promote a constant-colour material to its role texture.

    Why it is needed - a detailed sceneD3 diagnosis found that **89.8 % of dead pixels were
    a single constant-colour asphalt carriageway**, and the median local standard deviation
    of that surface was **1/4000** of the threshold. The decisive control: a grass verge on
    the same z=0 plane, under the same light, at the same distance, had **0.0 %** dead
    pixels, and the only difference was the presence of a diffuse texture.

    The constant-colour MDL mode (macro brightness modulation with a 14 m wavelength) cannot
    fix it - `flat_gnd` looks at the grain in a 5x5 pixel window, and macro modulation is in
    an entirely different frequency band.

    **Preserving the intended albedo**: to keep the colour the scene author chose, the
    texture is bound but multiplied by `base_color = intended colour / texture mean`, keeping
    the average albedo. In other words, the colour stays and only the grain is gained.

    Returns: (diff, nor, rough, base_color) - (None, None, None, original colour) when
    promotion is not possible.
    """
    cands = [r for r in (spec.get("tex_alts") or (spec.get("tex"),))
             if r and r in TEX]
    if not cands or diffuse_color is None:
        return None, None, None, diffuse_color
    try:
        # [brightness branch] **Meaning comes first, alternatives only when the budget is exceeded**.
        #   Choosing by luminance alone breaks material meaning, e.g. grass texture on fallen leaves.
        #   Previously there was one texture per role, so putting the dark concrete_floor
        #   (linear luminance 0.115) on a bright parapet (0.9) gave a multiplier of 7.8 that
        #   saturated the clamp (2.5) -> **2.5-4.8x darker than intended, with a colour bias too**.
        #   (The comment saying "the colour stays and only the grain is gained" was the opposite of the truth.)
        #   Choosing a nearby texture keeps the multiplier near 1 and the clamp never fires.
        gain_max = float(spec.get("max_gain", _PROMOTE_MAX_GAIN))
        # [W2 fix batch F1] Per-class spread cap, applied **only when the promotion
        #   brightens** (max(ratio) > 1). A darkening promotion cannot amplify channel
        #   noise, so autumn canopies (sceneC2 `CanopyA`, spread 3.34 but max ratio 0.94)
        #   keep their texture; an amplifying promotion with a wide spread does amplify it,
        #   which is the scene11 `leaf_far_*` defect. Default stays the old 4.0.
        spread_max = float(spec.get("max_spread", 4.0))
        # Candidate order = meaning priority. tex goes first.
        prim = spec.get("tex")
        order = ([prim] if prim in cands else []) + [r for r in cands if r != prim]
        role = None
        for r in order:
            pth = tex_path(r, "diff")
            if not os.path.isfile(pth):
                continue
            tm = _texture_mean(pth)
            if tm is None or min(tm) < 1e-4:
                continue
            ratio = [float(c) / m for c, m in zip(diffuse_color, tm)]
            # A large spread between per-channel multipliers pushes the colour shift into one channel (noise amplification).
            spread = max(ratio) / max(min(ratio), 1e-6)
            lim = spread_max if max(ratio) > 1.0 else 4.0
            if max(ratio) <= gain_max and spread <= lim:
                role = r
                break
        if role is None:
            return None, None, None, diffuse_color
        diff = tex_path(role, "diff")
        nor = tex_path(role, "nor") if "nor" in TEX[role] else None
        rough = tex_path(role, "rough") if "rough" in TEX[role] else None
        if nor and not os.path.isfile(nor):
            nor = None
        if rough and not os.path.isfile(rough):
            rough = None
        tm = _texture_mean(diff)
        if tm is None or min(tm) < 1e-4:
            return None, None, None, diffuse_color
        # Intended albedo / texture mean (linear). An excessive multiplier amplifies texture noise and
        # clips highlights, so **if it would hit the clamp, promotion is abandoned** and the
        # constant-colour MDL is used instead. Better to give up the grain than to get the colour wrong.
        bc = tuple(max(0.05, r) for r in ratio)
        return diff, nor, rough, bc
    except Exception as e:
        print(f"[룩v1][경고] 텍스처 승격 실패({role}): {e}")
        return None, None, None, diffuse_color


def _look_spec(path):
    """Get the look spec from a prim path. `.../Looks/Paving` -> the paving spec.

    (1) exact match table (LOOK_ROLE) -> (2) retry after stripping suffix variants
    -> (3) keyword substring rules -> (4) "misc" (the conservative default).
    An unknown gets only the minimal prescription, so there is no regression risk.
    Returns: (class name, spec dict)
    """
    name = str(path).rstrip("/").split("/")[-1]
    cls = LOOK_ROLE.get(name)
    if cls is None:
        base = name.rstrip("0123456789_")
        cls = LOOK_ROLE.get(base)
    if cls is None:
        low = name.lower()
        for c, keys in _LOOK_RULES:
            if any(k in low for k in keys):
                cls = c
                break
    if cls is None:
        cls = "misc"
    return cls, LOOK_CLASS[cls]


def check_assets(roles, hdri=None):
    """Check only that the textures of the given roles exist. On a miss, print the list and sys.exit(1).

    roles: list of texture role names. Special pseudo-roles:
        "hdri" -> the noon HDRI (DEFAULT_HDRI by default, selectable via the hdri argument),
        "mdl"  -> OmniPBR.mdl.
    """
    import sys
    missing = []
    for role in roles:
        if role == "hdri":
            p = os.path.join(ASSETS_DIR, hdri or DEFAULT_HDRI)
            if not os.path.isfile(p):
                missing.append((role, "exr", p))
            continue
        if role == "mdl":
            if not os.path.isfile(OMNIPBR_PATH):
                missing.append((role, "mdl", OMNIPBR_PATH))
            continue
        spec = TEX.get(role)
        if spec is None:
            missing.append((role, "?", f"<알 수 없는 역할 '{role}'>"))
            continue
        for kind in ("diff", "nor", "rough"):
            if kind not in spec:
                continue
            p = os.path.join(spec["dir"], spec[kind])
            if not os.path.isfile(p):
                missing.append((role, kind, p))
    if missing:
        print("=" * 64)
        print("[에러] 다음 에셋이 없습니다. assets/scene01/ 다운로드 후 재실행:")
        for role, kind, p in missing:
            print(f"  - [{role}/{kind}] {p}")
        print("=" * 64)
        sys.exit(1)


# ===========================================================================
# [2] boot - SimulationApp + carb settings + stage units (as in scene01)
# ===========================================================================
def _variation():
    """`variation_kit` on demand.

    Imported lazily, not at module scope, so `scene_common` still imports inside
    the mocked pxr-free harnesses. It is imported UNGUARDED on purpose: a gate
    that disables itself when its module is missing is worse than no gate, and
    this is the gate that stops a variation env silently contaminating the
    regression baseline. `variation_kit.py` is symlinked into `scenes/main` and
    `scenes/batch1` exactly like `ground_kit`/`stair_kit`; the realpath fallback
    below covers an invocation from anywhere else.
    """
    try:
        import variation_kit
    except ImportError:
        import sys as _s
        root = os.path.dirname(os.path.realpath(__file__))
        if root not in _s.path:
            _s.path.insert(0, root)
        import variation_kit
    return variation_kit


def boot(headless):
    """Boot Isaac Sim. SimulationApp is always created first, then everything else is imported.
    Applies the carb capture hygiene settings and the stage units (Z-up, metre) and returns
    sim_app. The scene can obtain stage again through
    omni.usd.get_context().get_stage().
    """
    # [lighting round, D1/D2] Refuse a judge render that carries variation env
    # BEFORE anything expensive happens. Checked here as well as in
    # `capture_pipeline` because that is where a mistake is cheapest to catch and
    # because the GUI path never reaches `capture_pipeline` at all.
    _variation().assert_role_gate()
    from isaacsim import SimulationApp
    sim_app = SimulationApp(
        {"headless": bool(headless), "width": 1920, "height": 1080})

    import carb
    import omni.usd
    from pxr import UsdGeom

    settings = carb.settings.get_settings()
    settings.set("/rtx/post/dlss/execMode", 2)     # DLSS Quality
    settings.set("/rtx/post/aa/op", 3)             # DLSS AA
    # [realism P1] PT acceleration - /rtx/pathtracing/spp defaults to 1, so totalSpp was being
    # accumulated over as many frames (512spp = 512 frames). Raising subframes runs several
    # samples inside one update. Supervisor measurement: 4.89 -> 0.08 s/shot (61x), with the
    # result image identical pixel for pixel. Scene files never touch this key, so enabling it
    # here applies to every scene. OFF by default (regression prevention) - enable explicitly via env.
    if os.environ.get("NEGOBS_PT_FAST", "") == "1":
        settings.set("/app/renderer/rtSubframes", PT_FAST["subframes"])
        print(f"[렌더] PT 가속 ON — {PT_FAST}")
    # Keep the viewport grid and axis guides out of the render (capture hygiene)
    settings.set("/app/viewport/grid/enabled", False)
    settings.set("/persistent/app/viewport/displayOptions", 0)
    settings.set("/app/viewport/show/grid", False)
    settings.set("/app/viewport/outline/enabled", False)

    # ------------------------------------------------------------------
    # [lighting round §5.4] Tone-mapping / exposure freeze.
    #
    # Split in two on purpose. The keys below are RE-ASSERTIONS of values the
    # runtime dump already carries (`t0_spike_report_v1.md` §7: histogram
    # enabled=False i.e. auto-exposure OFF, colorcorr/colorgrad disabled;
    # `look_check/_experiments/t0_spike/rtx_settings.json`: tonemap op=6 = ACES).
    # Setting them cannot move a pixel, so they are safe on the judge channel and
    # they nail down the one thing that would silently invalidate every A/B
    # verdict this project has made if it ever flipped.
    settings.set("/rtx/post/histogram/enabled", False)   # AE off - highest stake
    settings.set("/rtx/post/tonemap/op", 6)              # ACES (already default)
    settings.set("/rtx/post/colorcorr/enabled", False)
    settings.set("/rtx/post/colorgrad/enabled", False)
    # The rest of spec §5.4's block is data-only, because these ARE capable of
    # moving pixels and the judge channel is bit-frozen (D2). `dither` in
    # particular adds sub-LSB noise by design, and `colorMode`/`ecoMode` were
    # never in a dump so their current values are unverified.
    if os.environ.get("NEGOBS_RENDER_ROLE", "") == "data":
        settings.set("/rtx/post/tonemap/colorMode", 0)   # sRGBLinear
        settings.set("/rtx/post/tonemap/dither", 0.004)  # de-band
        settings.set("/rtx/ecoMode/enabled", False)
        print("[노출] data 역할 — §5.4 전체 고정 블록 적용")

    stage = omni.usd.get_context().get_stage()
    mpu = UsdGeom.GetStageMetersPerUnit(stage)
    if abs(mpu - 1.0) > 1e-9:
        print(f"[경고] metersPerUnit={mpu} → 1.0(미터)으로 설정")
        UsdGeom.SetStageMetersPerUnit(stage, 1.0)
    UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)
    UsdGeom.Xform.Define(stage, "/World")
    return sim_app


# ===========================================================================
# [3] Geometry helpers (stage passed in) - UsdGeom.Cube/Cylinder/Sphere
#     Note: UsdGeom.Cube defaults to size=2 (+-1) -> scale = desired dimension / 2
# ===========================================================================
def _bind_mtl(prim, mtl):
    if mtl is not None:
        from pxr import UsdShade
        UsdShade.MaterialBindingAPI.Apply(prim).Bind(mtl)


def add_box(stage, path, center, size, mtl=None, collider=False, rotZ=0.0,
            rotX=0.0):
    """Axis-aligned box. `rotZ` / `rotX` (deg) spin it about its own centre.

    [W3 K-micro · S06-F1 / S08-F1] `rotZ` exists so a template that lays a run
    along a **polyline** can honour that polyline's bearing without wrapping every
    element in a `build_rot_group` (an extra Xform prim per element, which moves
    prim budgets). The op is authored **only when it is non-zero**, and it is
    inserted between the translate and the scale so the applied order is
    `scale -> rotX -> rotZ -> translate` (USD applies xformOps in reverse list
    order - the same convention `build_rot_group` documents). With
    `rotZ=rotX=0.0` the prim is byte-identical to the pre-K-micro one, which is
    what makes this a zero-geometry-change addition for all 33 wired scenes.
    `rotX` exists for **in-plane** rotation of an element that lives on a
    vertical wall (thin in X): the 45 deg hazard hatch of `build_chevron_band`
    is the first customer (S13-F1).
    """
    from pxr import UsdGeom, UsdPhysics, Gf
    cube = UsdGeom.Cube.Define(stage, path)
    cube.CreateSizeAttr(2.0)
    cube.CreateExtentAttr([Gf.Vec3f(-1, -1, -1), Gf.Vec3f(1, 1, 1)])
    xf = UsdGeom.Xformable(cube)
    xf.AddTranslateOp().Set(Gf.Vec3d(*[float(c) for c in center]))
    if abs(float(rotZ)) > 1e-9:
        xf.AddRotateZOp().Set(float(rotZ))
    if abs(float(rotX)) > 1e-9:
        xf.AddRotateXOp().Set(float(rotX))
    xf.AddScaleOp().Set(Gf.Vec3f(float(size[0]) / 2.0,
                                 float(size[1]) / 2.0,
                                 float(size[2]) / 2.0))
    prim = cube.GetPrim()
    _bind_mtl(prim, mtl)
    if collider:
        UsdPhysics.CollisionAPI.Apply(prim)
    # [realism v1] Cover large horizontal ground slabs with a micro-relief skin.
    # In Phase1 E9 **vertex displacement was the largest visual contributor** (bigger than the MDL swap).
    # The slab itself is untouched, so the drop edge silhouette is unchanged (approval condition (2)).
    # `_ground_skin` authors an **axis-aligned** relief patch from (center, size);
    # it has no rotation input, so a spun slab would get an unspun skin sticking out
    # past its corners. A rotated box is never a ground slab in this library (it is a
    # railing panel or a bearing-laid element), so the skin is simply declined.
    if LOOK_GEO and abs(float(rotZ)) <= 1e-9 and abs(float(rotX)) <= 1e-9 \
            and _skin_wanted(path, size, mtl):        # A new mesh = geometry
        try:
            # The seed **must be deterministic**. Python's builtin hash() is randomised per process by
            # PYTHONHASHSEED, which would change the terrain relief on every render (this project's rule is
            # 100 % deterministic RNG). crc32 is used.
            if _ground_skin(stage, f"{path}_Skin", center, size, mtl,
                            seed=zlib.crc32(str(path).encode()) % 100000
                            ) is not None:
                LOOK_STATS["skin"] += 1
        except Exception as e:                 # A skin failure must not kill the scene
            print(f"[룩v1][경고] 지면 스킨 생성 실패 {path}: {e}")
    return cube


# [W2-0, P-A] Turn off the displacement skin on ground slabs that ground_kit decorates.
#   The skin top is +6.5 to 16.5 mm (re-measured in `_ground_skin`) while flush ground elements have
#   proud of 0.6-4.0 mm, so they are **buried entirely** - manhole dark pixels 5.88 % -> 0.02 %,
#   dot block deep-yellow pixels 2,090 -> 118 px `[measured - ground_kit_spec_v1 §1.1, §12.5]`.
#   ground_kit receives this function **as an injected callback** (keeping the no-scene_common-dependency principle).
SKIN_EXCLUDE = set()


def skin_exclude(*paths):
    """Register paths excluded from skinning. Prefix matches are excluded too. Scenes call this before applying ground_kit."""
    SKIN_EXCLUDE.update(str(p) for p in paths)


def _skin_wanted(path, size, mtl):
    """Decide whether a prim is a displacement skin target - only large, horizontal, ground-family surfaces.

    Under approval condition (2) ("the drop edge silhouette must not be shaken by displacement"),
    drop geometry such as stairs, curbs, nosings and decks is excluded wholesale by path token.
    When the decision is ambiguous, **exclusion** is the default - displacement is an
    improvement, not a requirement, so no risk is taken.
    """
    if str(path) in SKIN_EXCLUDE or any(str(path).startswith(p)
                                        for p in SKIN_EXCLUDE):
        return False
    if mtl is None:
        return False
    sx, sy, sz = [float(v) for v in size]
    if sx < 4.0 or sy < 4.0:                   # Large areas only (props and curbs excluded)
        return False
    if sz > 0.8 or sz >= min(sx, sy) * 0.5:    # Horizontal slabs only (walls and columns excluded)
        return False
    low = str(path).lower()
    if any(t in low for t in _SKIN_DENY):
        return False
    # The role is decided from the **bound material path** (`.../Looks/Paving`).
    # The geometry path (`.../Ground`) carries no role name.
    try:
        mpath = str(mtl.GetPath())
    except Exception:
        return False
    if any(t in mpath.lower() for t in _SKIN_DENY):
        return False
    cls, _spec = _look_spec(mpath)
    return cls in _SKIN_CLASSES


def _ground_skin(stage, path, center, size, mtl, amp_m=0.010,
                 spacing=0.12, taper=0.60, max_n=170, seed=17):
    """[realism v1] The **micro-relief skin** mesh laid on top of a ground slab.

    Why a skin - replacing the slab itself (a Cube) with a displaced mesh would remove its 4
    side faces and **shake the drop edge silhouette** (approval condition (2): "the drop edge
    must not be shaken by displacement"). So the original Cube is **left alone** and a
    displacement skin is laid just slightly above its top. As a result
      - the slab outline and drop edge are still determined by the original Cube (0 change)
      - only the interior of the top surface has relief -> the ground no longer reads as a
        plane at the h0.3 grazing angle
    This approach also leaves the GT drop geometry untouched.

    Two extra safeguards:
      (1) The skin is inset by `edge` from the slab boundary -> the slab rim stays original and
         the skin's own rim dies out of sight.
      (2) The displacement amplitude is multiplied by a **boundary taper** converging to 0 at
         the skin edge -> no step appears even at the inset boundary.

    Phase1 E5 measurement: without authored normals, Hydra draws with face normals and the
    result looks faceted -> vertex normals are computed directly by finite difference.
    `subdivisionScheme="none"` is authored explicitly too (unauthored means the USD default
    catmullClark - the Phase1 §2.6 landmine).
    """
    from pxr import UsdGeom, UsdShade, Gf
    cx, cy, cz = [float(v) for v in center]
    sx, sy, sz = [float(v) for v in size]
    edge = 0.05
    hx, hy = sx / 2.0 - edge, sy / 2.0 - edge
    if hx <= 0.5 or hy <= 0.5:
        return None
    nx = max(4, min(int(2 * hx / spacing), max_n))
    ny = max(4, min(int(2 * hy / spacing), max_n))
    x0, x1 = cx - hx, cx + hx
    y0, y1 = cy - hy, cy + hy
    # [major M3] The lift was 1.5 mm while the displacement amplitude was +-9.8 mm, so 25-29 % of the skin
    # **penetrated below the slab top**, exposing the original Cube plane and creating intersection contours.
    # The lift is now larger than the amplitude so the skin is always above.
    ztop = cz + sz / 2.0 + max(0.0015, amp_m * 1.15)

    rng = np.random.default_rng(seed)
    xs = np.linspace(x0, x1, nx + 1)
    ys = np.linspace(y0, y1, ny + 1)
    XX, YY = np.meshgrid(xs, ys, indexing="ij")
    ZZ = np.full_like(XX, ztop)
    # [major M4] The highest-frequency octave (0.07 m) was finer than the mesh spacing (0.12-0.24 m) and
    # therefore **always aliased** (a Nyquist violation) -> high-frequency noise in the normals. Only
    # wavelengths of at least 2.5x the spacing are used.
    _wl_min = spacing * 2.5
    for oi, wl in enumerate(w for w in (0.55, 0.19, 0.07) if w >= _wl_min):
        gx = max(2, int((x1 - x0) / wl) + 1)
        gy = max(2, int((y1 - y0) / wl) + 1)
        g = rng.random((gx + 1, gy + 1)) - 0.5
        fi = np.clip((XX - x0) / (x1 - x0) * gx, 0, gx - 1e-6)
        fj = np.clip((YY - y0) / (y1 - y0) * gy, 0, gy - 1e-6)
        i0, j0 = fi.astype(int), fj.astype(int)
        tx, ty = fi - i0, fj - j0
        sxs, sys_ = tx * tx * (3 - 2 * tx), ty * ty * (3 - 2 * ty)
        v = ((g[i0, j0] * (1 - sxs) + g[i0 + 1, j0] * sxs) * (1 - sys_)
             + (g[i0, j0 + 1] * (1 - sxs) + g[i0 + 1, j0 + 1] * sxs) * sys_)
        ZZ += v * amp_m * (0.6 ** oi)
    # Boundary taper - displacement 0 at the skin edge
    tx_ = np.clip((np.minimum(XX - x0, x1 - XX)) / max(taper, 1e-6), 0, 1)
    ty_ = np.clip((np.minimum(YY - y0, y1 - YY)) / max(taper, 1e-6), 0, 1)
    t = (tx_ * tx_ * (3 - 2 * tx_)) * (ty_ * ty_ * (3 - 2 * ty_))
    ZZ = ztop + (ZZ - ztop) * t

    pts = [Gf.Vec3f(float(XX[i, j]), float(YY[i, j]), float(ZZ[i, j]))
           for i in range(nx + 1) for j in range(ny + 1)]
    idx, cnt = [], []
    for i in range(nx):
        for j in range(ny):
            a = i * (ny + 1) + j
            idx += [a, a + 1, a + ny + 2, a + ny + 1]
            cnt.append(4)
    m = UsdGeom.Mesh.Define(stage, path)
    m.CreatePointsAttr(pts)
    m.CreateFaceVertexCountsAttr(cnt)
    m.CreateFaceVertexIndicesAttr(idx)
    m.CreateSubdivisionSchemeAttr("none")
    m.CreateExtentAttr([Gf.Vec3f(x0, y0, float(ZZ.min())),
                        Gf.Vec3f(x1, y1, float(ZZ.max()))])
    gzx, gzy = np.gradient(ZZ, (x1 - x0) / nx, (y1 - y0) / ny)
    nrm = np.stack([-gzx, -gzy, np.ones_like(ZZ)], axis=-1)
    nrm /= np.linalg.norm(nrm, axis=-1, keepdims=True)
    m.CreateNormalsAttr([Gf.Vec3f(*nrm[i, j])
                         for i in range(nx + 1) for j in range(ny + 1)])
    m.SetNormalsInterpolation(UsdGeom.Tokens.vertex)
    if mtl is not None:
        UsdShade.MaterialBindingAPI.Apply(m.GetPrim()).Bind(mtl)
    return m


# Classes whose constant-colour materials are routed to NegObsGround (base_color mode).
# Excluded: paint (lane markings, reflective bands, tactile paving), sign, glass, water, misc
#   -> for these **a constant colour is physically correct** (v5.1 §4). Adding texture or noise
#     violates the convention, and painted markings in particular must stay uniform to work as cues.
# [major M1 + policy alignment] The 3-tier material policy of report §2.2 says "vegetation, metal, wood = OmniPBR",
# yet the code put all three in this set and routed constant colours to the MDL (59 kinds mismatched).
# In particular **metal has no metallic input in the MDL at all, so metallic character is lost**.
# Per the policy, only the ground and structure families remain.
# Only metal needs excluding - the MDL is a metalness=0 reduction, so **only metallic character** is lost.
# Vegetation and wood have no metallic character and are fine in the MDL, and in the scene07
# diagnosis constant-colour vegetation (2.26 pp) and constant-colour wood (1.61 pp) were top dead-pixel sources.
_CONST_MDL_CLASSES = {"paving", "concrete", "brick", "stone", "soil",
                      "gravel", "asphalt", "nosing", "curb", "snow",
                      "veg", "wood", "turf"}

# Role classes that get a displacement skin (ground family only). Stairs, curbs and nosings are excluded -
# they are drop edge geometry and are left alone under approval condition (2).
_SKIN_CLASSES = {"paving", "concrete", "asphalt", "soil", "gravel", "stone",
                 "turf"}   # [GT-118] lawn ground undulation — not a drop edge
# A path containing one of these tokens gets no displacement even if it is ground (drop geometry, walking safety)
#   "gkit" - all ground_kit output lives under `{ROOT}/GKit/...`. Some builders create areas over
#   4 m, such as coating and wear bands, so without this token a ground_kit element would
#   **take on a second skin over itself** [W2-0, spec §1.2].
_SKIN_DENY = ("stair", "step", "tread", "riser", "nosing", "curb", "ramp",
              "landing", "deck", "platform", "edge", "lip", "sill", "gkit")


def add_cylinder(stage, path, center, radius, height, mtl=None,
                 rotY=0.0, rotX=0.0, collider=False, rotZ=0.0):
    """Z-axis cylinder. `rotZ` (deg, +Z) is applied **after** `rotY`/`rotX`.

    [W3 K-micro · S06-F1 / S08-F1] The op order in the list is
    `[translate, rotZ, rotY, rotX]`, and USD applies xformOps in **reverse** list
    order, so the actual sequence is `rotX -> rotY -> rotZ -> translate`. That is
    the order a bearing-laid tube needs: `rotY=90` lays the cylinder's local Z
    along world +X, and `rotZ` then swings that lying tube onto the polyline's
    bearing. Authored only when non-zero, so every existing call site is
    byte-identical.
    """
    from pxr import UsdGeom, UsdPhysics, Gf
    cyl = UsdGeom.Cylinder.Define(stage, path)
    cyl.CreateRadiusAttr(float(radius))
    cyl.CreateHeightAttr(float(height))
    cyl.CreateAxisAttr(UsdGeom.Tokens.z)
    xf = UsdGeom.Xformable(cyl)
    # Order: translate -> rotate (rotate about the prim origin, then move)
    xf.AddTranslateOp().Set(Gf.Vec3d(*[float(c) for c in center]))
    if abs(float(rotZ)) > 1e-9:
        xf.AddRotateZOp().Set(float(rotZ))
    if abs(rotY) > 1e-9:
        xf.AddRotateYOp().Set(float(rotY))
    if abs(rotX) > 1e-9:
        xf.AddRotateXOp().Set(float(rotX))
    prim = cyl.GetPrim()
    _bind_mtl(prim, mtl)
    if collider:
        UsdPhysics.CollisionAPI.Apply(prim)
    return cyl


# Manhole / drain disc silhouette segments. `UsdGeom.Cylinder` is an *analytic* gprim and
# Hydra tessellates it at its own low default, which is what renders the library's manhole
# covers as octagons and 12-gons (defect D4, `w2d_round_v1.md` §4.3). A polygonal prism
# mesh puts the segment count under our control at **one prim per disc**, so no prim or
# instance budget moves. 32 is comfortably above the F5 bar of 24 and matches the
# precedent scene05 already set for its arc rims (`seg=32`).
DISC_SEGMENTS = 32


def add_disc(stage, path, center, radius, height, mtl=None, seg=DISC_SEGMENTS,
             collider=False):
    """N-gon prism (a 'cylinder' whose silhouette segment count is explicit).

    Drop-in replacement for `add_cylinder` where the silhouette matters: same
    (center, radius, height) contract, Z axis, origin at the prism centre.
    Emits **one** `UsdGeom.Mesh` - side quads + two n-gon caps - with faceted side
    normals left to the renderer (a manhole rim is a machined edge, not a smooth barrel).
    """
    from pxr import UsdGeom, UsdPhysics, Gf
    n = max(3, int(seg))
    r, hz = float(radius), float(height) / 2.0
    ring = [(r * math.cos(2.0 * math.pi * k / n),
             r * math.sin(2.0 * math.pi * k / n)) for k in range(n)]
    pts = ([Gf.Vec3f(x, y, -hz) for x, y in ring]
           + [Gf.Vec3f(x, y, hz) for x, y in ring])
    counts, idx = [], []
    for k in range(n):                          # side quads (outward winding)
        k2 = (k + 1) % n
        counts.append(4)
        idx += [k, k2, k2 + n, k + n]
    counts.append(n)                            # top cap (+Z)
    idx += list(range(n, 2 * n))
    counts.append(n)                            # bottom cap (-Z)
    idx += list(range(n - 1, -1, -1))
    m = UsdGeom.Mesh.Define(stage, path)
    m.CreatePointsAttr(pts)
    m.CreateFaceVertexCountsAttr(counts)
    m.CreateFaceVertexIndicesAttr(idx)
    m.CreateSubdivisionSchemeAttr("none")
    m.CreateExtentAttr([Gf.Vec3f(-r, -r, -hz), Gf.Vec3f(r, r, hz)])
    xf = UsdGeom.Xformable(m)
    xf.AddTranslateOp().Set(Gf.Vec3d(*[float(c) for c in center]))
    prim = m.GetPrim()
    _bind_mtl(prim, mtl)
    if collider:
        UsdPhysics.CollisionAPI.Apply(prim)
    return m


def add_sphere(stage, path, center, scale3, mtl=None):
    from pxr import UsdGeom, Gf
    sph = UsdGeom.Sphere.Define(stage, path)
    sph.CreateRadiusAttr(1.0)
    xf = UsdGeom.Xformable(sph)
    xf.AddTranslateOp().Set(Gf.Vec3d(*[float(c) for c in center]))
    xf.AddScaleOp().Set(Gf.Vec3f(*[float(s) for s in scale3]))
    _bind_mtl(sph.GetPrim(), mtl)
    return sph


def _oriented_box(stage, path, center, size, mtl=None, collider=False,
                  rotz=0.0, rotx=0.0):
    """Rotatable solid Cube. op list = translate -> rotZ -> rotX -> scale.
    Under the USD row-vector convention the list applies to points in reverse: scale -> rotX ->
    rotZ -> translate. So rotX acts first in the local frame (not yet rotated to its bearing),
    and rotZ then rotates that whole local frame by the azimuth.
      build_arc_steps convention: local X = radial, Y = tangential (chord), Z = height.
      -> local X before rotZ is the radial axis at bearing 0, and becomes the true radial
        direction after rotZ. A tangential slope (rising or falling along the chord) is
        therefore a rotation about the **local X axis (rotX)**.
        (The tangent is local Y, so the axis that tilts it is perpendicular to it = local X = radial.)"""
    from pxr import UsdGeom, UsdPhysics, Gf
    cube = UsdGeom.Cube.Define(stage, path)
    cube.CreateSizeAttr(2.0)
    cube.CreateExtentAttr([Gf.Vec3f(-1, -1, -1), Gf.Vec3f(1, 1, 1)])
    xf = UsdGeom.Xformable(cube)
    xf.AddTranslateOp().Set(Gf.Vec3d(*[float(c) for c in center]))
    if abs(rotz) > 1e-12:
        xf.AddRotateZOp().Set(float(rotz))
    if abs(rotx) > 1e-12:
        xf.AddRotateXOp().Set(float(rotx))
    xf.AddScaleOp().Set(Gf.Vec3f(float(size[0]) / 2.0,
                                 float(size[1]) / 2.0,
                                 float(size[2]) / 2.0))
    prim = cube.GetPrim()
    _bind_mtl(prim, mtl)
    if collider:
        UsdPhysics.CollisionAPI.Apply(prim)
    return cube


# ===========================================================================
# [4] make_pbr - OmniPBR world-projection factory (as in scene01, plus specular_level)
# ===========================================================================
def make_pbr(stage, path, diff=None, nor=None, rough=None, scale_m=1.0,
             tint=None, metallic=0.0, roughness_const=None,
             diffuse_color=None, bump=1.0, specular_level=None,
             emission_color=None, emission_intensity=None, uv_mode=False,
             unit_cell=None, blend=None):
    """OmniPBR material. With diff given it is a world-space projected texture, otherwise a constant colour.
    With specular_level given it calls sh.CreateInput("specular_level", Float).
    With emission_color + emission_intensity it is emissive (enable_emission) - for emissive
    panels in interior scenes (D4 etc.). The RT single-bounce contribution is negligible;
    verdicts use PT with 8 bounces (lesson 7).
    uv_mode=True: sample by mesh st (UV 0..1) instead of world projection - for cases where the
    texture must map 1:1 onto the face, such as a sign panel (used only by _sign_quad of build_sign).

    [realism v1] With `NEGOBS_LOOK_MTL=1` the role is read from the prim path and a look spec is
    injected (§1b). With the flag off, the code path below is **never taken** and behaviour is
    byte-identical to before. This function only creates materials, so it belongs **entirely to
    `LOOK_MTL`** (rule R-1 - it does not change the prim set).
    """
    from pxr import UsdShade, Sdf, Gf

    _look_omni = None
    _look_cls = None
    if LOOK_MTL and not uv_mode and emission_color is None:
        cls, spec = _look_spec(path)
        _look_cls = cls
        LOOK_STATS["roles"][cls] = LOOK_STATS["roles"].get(cls, 0) + 1
        if diff is not None and spec["mdl"] == "ground":
            LOOK_STATS["ground"] += 1
            return _make_ground_pbr(stage, path, diff, nor, rough, scale_m,
                                    spec, tint=tint,
                                    roughness_const=roughness_const,
                                    specular_level=specular_level, bump=bump,
                                    unit_cell=unit_cell, cls=cls, blend=blend)
        # [realism v1] **Constant-colour materials are routed through the MDL too.**
        # More than half of all make_pbr calls in the 33 scenes pass a constant diffuse_color, and a
        # constant colour is by definition perfectly flat, i.e. the largest source of flat %. Without
        # procuring any new texture, laying the MDL world macro modulation, roughness noise and
        # weathering over a constant colour stops it being a "flat solid colour" (MDL v1.7.0 `base_color`).
        # But **roles where a constant colour is physically correct are excluded** - lane paint, reflective
        # bands, tactile paving, signs, glass, water. v5.1 §4 fixed these as constant colours.
        if (diff is None and diffuse_color is not None
                and cls in _CONST_MDL_CLASSES):
            # First try **promotion** to the role texture (preserving the intended albedo).
            # Once promoted, patch blending, tri_dither, macro and desat all turn on as well, making it
            # far stronger than constant-colour mode.
            pd, pn, pr, pbc = _promote_const_to_texture(spec, diffuse_color)
            if pd is not None:
                LOOK_STATS["promoted"] = LOOK_STATS.get("promoted", 0) + 1
                return _make_ground_pbr(
                    stage, path, pd, pn, pr,
                    scale_m if scale_m != 1.0 else spec.get("tex_scale", 1.2),
                    spec, tint=tint, roughness_const=None,
                    specular_level=(specular_level if specular_level is not None
                                    else spec.get("spec")),
                    bump=spec.get("bump", 1.0), base_color=pbc,
                    unit_cell=unit_cell, cls=cls, blend=blend)
            LOOK_STATS["const_mdl"] = LOOK_STATS.get("const_mdl", 0) + 1
            return _make_ground_pbr(stage, path, None, None, None, scale_m,
                                    spec, tint=tint,
                                    roughness_const=roughness_const,
                                    specular_level=specular_level, bump=bump,
                                    base_color=diffuse_color,
                                    unit_cell=unit_cell, cls=cls, blend=blend)
        # Textured material -> bevel + detail normal.
        # **Constant-colour materials get the bevel too** - the first gate skipped constant colours
        # entirely, and constant colours are precisely the main source of flat %. Texturising is a
        # separate item (brief 2-7, awaiting a full audit) but the bevel needs no texture.
        LOOK_STATS["omni_tex" if diff is not None else "const"] += 1
        _look_omni = spec
        # [GT-113 W1] The albedo band and self-correcting saturation now reach the
        # OmniPBR branch too. Until here both governors were called only inside
        # `_make_ground_pbr`, so every omni-routed class (metal, wood-tex, veg-tex,
        # water, glass, paint, sign, misc) was structurally outside them — GT-108's
        # "밝기 주인이 밴드 제외 대상" finding was this missing wire, not a class-table
        # choice. Guarding is by class *data*, not code: today's omni classes carry no
        # alb_max/alb_min and sat 1.0, so this block is bit-identical until a class
        # states a value (GT-114). paint/sign/glass/water stay constant by that same
        # data (v5.1 §4), which keeps cue colours untouched without a special case.
        if diff is not None:
            # Texture path — the multiplier that reaches the frame is the tint
            # (OmniPBR: diffuse_tint × texture). Saturation cannot be applied here
            # (OmniPBR has no saturation input and the texture is per-pixel), so the
            # band alone is enforced; textured desaturation stays an MDL-only tool.
            _tm = _texture_mean(diff)
            if _tm is not None:
                _t_in = list(tint) if tint is not None else [1.0, 1.0, 1.0]
                _t_new, _t_chg = _albedo_band(cls, _t_in, _tm)
                if _t_chg:
                    tint = _t_new
        elif diffuse_color is not None:
            _c_new, _c_chg = _albedo_band(cls, list(diffuse_color), None)
            if _c_chg:
                diffuse_color = _c_new
            _k = _effective_sat(spec, None, diffuse_color)
            if _k < 0.999:
                _lum = sum(c * w for c, w in
                           zip(diffuse_color, _ALB_BAND_LUMA))
                diffuse_color = [_lum + (c - _lum) * _k
                                 for c in diffuse_color]
                LOOK_STATS["omni_sat"] = LOOK_STATS.get("omni_sat", 0) + 1
    elif LOOK_MTL and not uv_mode and emission_color is not None:
        # [GT-113 W7] Emissive materials used to bypass the look layer wholesale
        # (classification, bevel, metering — everything landed in `skipped`), so a
        # D4-class scene whose only bright elements are emissive panels was fully
        # outside the layer. Emission itself must not be governed (banding a light
        # source dims the scene — the D4 darkness problem is the opposite defect),
        # so only the non-emissive channels pass: role metering + the class bevel.
        # Detail normals stay off (a light face has no mineral grain).
        cls, spec = _look_spec(path)
        _look_cls = cls
        LOOK_STATS["roles"][cls] = LOOK_STATS["roles"].get(cls, 0) + 1
        LOOK_STATS["emissive"] = LOOK_STATS.get("emissive", 0) + 1
        _look_omni = dict(bevel=float(spec.get("bevel", 0.0)), detail=False)
    elif LOOK_MTL:
        LOOK_STATS["skipped"] += 1

    mtl = UsdShade.Material.Define(stage, path)
    sh = UsdShade.Shader.Define(stage, path + "/Shader")
    sh.CreateImplementationSourceAttr(UsdShade.Tokens.sourceAsset)
    sh.SetSourceAsset(Sdf.AssetPath(OMNIPBR_PATH), "mdl")
    sh.SetSourceAssetSubIdentifier("OmniPBR", "mdl")
    F = Sdf.ValueTypeNames.Float
    C3 = Sdf.ValueTypeNames.Color3f
    A = Sdf.ValueTypeNames.Asset
    B = Sdf.ValueTypeNames.Bool
    F2 = Sdf.ValueTypeNames.Float2

    def _tex(name, path_, cs):
        i = sh.CreateInput(name, A)
        i.Set(path_)
        try:                                   # A normal map must be raw
            i.GetAttr().SetColorSpace(cs)
        except Exception:
            pass

    if diff is not None:
        _tex("diffuse_texture", diff, "auto")
        if nor is not None:
            _tex("normalmap_texture", nor, "raw")
        if rough is not None:
            _tex("reflectionroughness_texture", rough, "raw")
            sh.CreateInput("reflection_roughness_texture_influence",
                           F).Set(1.0)
        if uv_mode:
            # [v5] Mesh st sampling - the texture maps 1:1 to the face UV 0..1 (sign panel)
            sh.CreateInput("project_uvw", B).Set(False)
        else:
            # World-space projection (axis-aligned box -> no stretching). world_or_object=True means
            # world space. With False (object space) the texture on a scaled Cube gets dragged by the
            # scale and stretches.
            sh.CreateInput("project_uvw", B).Set(True)
            sh.CreateInput("world_or_object", B).Set(True)
            s = 1.0 / float(scale_m)           # texture_scale = 1/tile size [m]
            sh.CreateInput("texture_scale", F2).Set(Gf.Vec2f(s, s))
        sh.CreateInput("bump_factor", F).Set(float(bump))
    if diffuse_color is not None:
        sh.CreateInput("diffuse_color_constant",
                       C3).Set(Gf.Vec3f(*diffuse_color))
    if tint is not None:
        sh.CreateInput("diffuse_tint", C3).Set(Gf.Vec3f(*tint))
    sh.CreateInput("metallic_constant", F).Set(float(metallic))
    if roughness_const is not None:
        sh.CreateInput("reflection_roughness_constant",
                       F).Set(float(roughness_const))
    if specular_level is not None:
        sh.CreateInput("specular_level", F).Set(float(specular_level))
    if emission_color is not None and emission_intensity is not None:
        sh.CreateInput("enable_emission", B).Set(True)
        sh.CreateInput("emissive_color", C3).Set(Gf.Vec3f(*emission_color))
        sh.CreateInput("emissive_intensity", F).Set(float(emission_intensity))
    if _look_omni is not None:
        # Fake bevel - official implementation in Kit 106.1+, confirmed working in both RT and PT (Phase1 E1).
        if _look_omni["bevel"] > 0.0:
            LOOK_STATS["bevel"] += 1
            sh.CreateInput("round_edges_radius", F).Set(
                float(_look_omni["bevel"]))
            sh.CreateInput("round_edges_roundness", F).Set(1.0)
            sh.CreateInput("round_edges_across_materials", B).Set(False)
        # Detail normal - mitigates texel smearing up close (Phase1 E3)
        # [W2-C, T1 §1.6(b)] The single `_DETAIL_NOR` becomes a **per-family table**.
        # The old version applied `concrete_wall_nor_dx` (§1.2 verdict: not a detail) to every
        # class. Classes absent from the table (veg, water, glass, paint, sign, misc, wood)
        # now **deliberately** receive no detail.
        if _look_omni.get("detail") and diff is not None:
            _dp, _db, _di = detail_source(_look_cls)
            if _dp is not None:
                LOOK_STATS["detail"] += 1
                _tex("detail_normalmap_texture", _dp, "raw")
                sh.CreateInput("detail_bump_factor", F).Set(float(_db))
                sh.CreateInput("detail_texture_scale",
                               F2).Set(Gf.Vec2f(_di, _di))

    for out in ("surface", "displacement", "volume"):
        mtl.CreateOutput(f"mdl:{out}",
                         Sdf.ValueTypeNames.Token).ConnectToSource(
            sh.ConnectableAPI(), "out")
    return mtl


# ===========================================================================
# [4b] make_glass - translucent glazing, PT-oriented (GT-73)
# ===========================================================================
# Every glass prim in the 33 scenes binds a constant-colour OmniPBR, which is
# **opaque** - scene08 recorded it as "no transmission is available in this
# material stack" and scene13's `build_views` had to move an eye because of it.
# The 08-06 user instruction ("Can the glass be made slightly transparent?") is
# an explicit exception to the material freeze, and it is only meaningful under
# PT (the verdict renderer, 8 bounces).
#
# Two backends, selected by `NEGOBS_GLASS_MDL`:
#   "pbr" (default) - OmniPBR with `enable_opacity` + `opacity_constant`. The
#     path tracer resolves fractional cutout opacity stochastically, so the pane
#     reads as a tinted sheet and, having no refraction, cannot distort the
#     descent behind it - which is the cue this library's glass has to preserve.
#   "glass" - `OmniGlass.mdl` (`mtl/OmniGlass`), `thin_walled=True` so a 19 mm
#     pane is one interface instead of a 19 mm solid slab of glass (a slab
#     refracts and displaces the treads seen through it).
# `enable_opacity` is authored **only on the material this function creates**.
# The §5b vegetation note is the reason it is never turned on globally: those
# leaves are modelled geometry with no alpha channel, so a global switch breaks
# them (ZZ §10.2). Nothing here touches `make_pbr`'s code path.
#
# `NEGOBS_GLASS_V1=0` returns the caller's OPAQUE `make_pbr` material instead,
# so the arm is A/B-able without editing any scene file.
GLASS_V1 = os.environ.get("NEGOBS_GLASS_V1", "1") == "1"
GLASS_MDL = os.environ.get("NEGOBS_GLASS_MDL", "pbr").strip().lower()
OMNIGLASS_PATH = os.path.join(os.path.dirname(OMNIPBR_PATH), "OmniGlass.mdl")
GLASS_STATS = dict(omnipbr=0, omniglass=0, fallback=0)


def glass_backend():
    """One-line description of the arm `make_glass` will take - for census prints."""
    if not GLASS_V1:
        return "OFF (NEGOBS_GLASS_V1=0 - opaque make_pbr fallback)"
    if GLASS_MDL in ("glass", "omniglass") and os.path.isfile(OMNIGLASS_PATH):
        return "OmniGlass.mdl (thin_walled)"
    return "OmniPBR enable_opacity"


def make_glass(stage, path, color=(0.55, 0.66, 0.68), opacity=0.35,
               roughness=0.05, ior=1.49, specular_level=0.6,
               opaque_color=None, opaque_roughness=None):
    """Slightly transparent glazing. Returns a `UsdShade.Material`, like `make_pbr`.

    `opacity` is the OmniPBR `opacity_constant` (0 = clear, 1 = opaque); it is
    clamped to 0.05..1.0 so a caller can never author an invisible pane.
    `opaque_color` / `opaque_roughness` are what the `NEGOBS_GLASS_V1=0` arm
    hands to `make_pbr`, i.e. the pane's pre-GT-73 look - pass the scene's old
    glass constants there and the fallback is byte-identical to the old build.
    `opacity_threshold` is written as 0.0 explicitly: with a threshold > 0 the
    MDL binarises the value and the pane goes fully opaque again.
    """
    from pxr import UsdShade, Sdf, Gf

    if not GLASS_V1:
        GLASS_STATS["fallback"] += 1
        return make_pbr(
            stage, path,
            diffuse_color=(opaque_color if opaque_color is not None else color),
            roughness_const=(opaque_roughness if opaque_roughness is not None
                             else roughness))

    op = min(1.0, max(0.05, float(opacity)))
    mtl = UsdShade.Material.Define(stage, path)
    sh = UsdShade.Shader.Define(stage, path + "/Shader")
    sh.CreateImplementationSourceAttr(UsdShade.Tokens.sourceAsset)
    F = Sdf.ValueTypeNames.Float
    C3 = Sdf.ValueTypeNames.Color3f
    B = Sdf.ValueTypeNames.Bool

    if GLASS_MDL in ("glass", "omniglass") and os.path.isfile(OMNIGLASS_PATH):
        sh.SetSourceAsset(Sdf.AssetPath(OMNIGLASS_PATH), "mdl")
        sh.SetSourceAssetSubIdentifier("OmniGlass", "mdl")
        sh.CreateInput("glass_color", C3).Set(Gf.Vec3f(*color))
        sh.CreateInput("glass_ior", F).Set(float(ior))
        sh.CreateInput("frosting_roughness", F).Set(float(roughness))
        sh.CreateInput("thin_walled", B).Set(True)
        GLASS_STATS["omniglass"] += 1
    else:
        sh.SetSourceAsset(Sdf.AssetPath(OMNIPBR_PATH), "mdl")
        sh.SetSourceAssetSubIdentifier("OmniPBR", "mdl")
        sh.CreateInput("diffuse_color_constant", C3).Set(Gf.Vec3f(*color))
        sh.CreateInput("metallic_constant", F).Set(0.0)
        sh.CreateInput("reflection_roughness_constant", F).Set(float(roughness))
        if specular_level is not None:
            sh.CreateInput("specular_level", F).Set(float(specular_level))
        sh.CreateInput("enable_opacity", B).Set(True)
        sh.CreateInput("enable_opacity_texture", B).Set(False)
        sh.CreateInput("opacity_constant", F).Set(op)
        sh.CreateInput("opacity_threshold", F).Set(0.0)
        GLASS_STATS["omnipbr"] += 1

    for out in ("surface", "displacement", "volume"):
        mtl.CreateOutput(f"mdl:{out}",
                         Sdf.ValueTypeNames.Token).ConnectToSource(
            sh.ConnectableAPI(), "out")
    return mtl


# Unit-cell jitter defaults (T1 §1.8-3). sigma 0.10 / accent 7 % are the spec
# values; they only take effect once ground_kit supplies a cell period.
UNIT_CELL_DEFAULTS = dict(sigma=0.10, accent=0.07)


def _wire_unit_cell(sh, F, F2, unit_cell):
    """Pass the ground_kit unit-cell ledger through to the MDL. Default = OFF.

    Contract: `ground_kit_spec_v1.md` §4.5 (U1~U4) / `t1_material_layer_spec_v1.md`
    §1.8-3. The MDL quantises the dominant-plane coordinate into cells and gives
    each cell one log-normal albedo scalar (zero texture fetches) — that scalar
    is the principal component of sigma_LF for every paving profile.

    `unit_cell` is `None` (default) or `(cell_m, (ox, oy))`, optionally
    `(cell_m, (ox, oy), sigma, accent)`. Nothing is authored when it is None or
    when cell_m <= 0, so the shader is byte-identical to before — the wiring
    exists but the value injection waits on the ground_kit ledger (spec §8.1 P2).

    U3 is why the ORIGIN is mandatory and not optional: the MDL's default grid
    origin is the UV origin, not the scene origin, so a matching period with a
    mismatched phase produces a half-cell offset seam under the engraved joints.
    U4 (`unit_cell = None` profile + jitter on) is a T1-side FAIL, raised here:
    unmodular paving (asphalt, membrane) has no cell to jitter.
    """
    if unit_cell is None:
        return False
    try:
        cell = float(unit_cell[0])
        origin = unit_cell[1]
        sigma = float(unit_cell[2]) if len(unit_cell) > 2 else \
            UNIT_CELL_DEFAULTS["sigma"]
        accent = float(unit_cell[3]) if len(unit_cell) > 3 else \
            UNIT_CELL_DEFAULTS["accent"]
    except (TypeError, IndexError, ValueError) as e:
        raise ValueError(f"unit_cell 형식 오류 {unit_cell!r}: {e}")
    if cell <= 0.0:                       # U4 — explicitly "no module" profile
        if sigma > 0.0:
            raise ValueError(
                "unit_cell 주기가 0 이하인데 지터가 켜져 있다(계약 U4 위반) — "
                "무모듈 포장(아스팔트·도막)에 셀 지터는 물리적으로 틀렸다")
        return False
    if origin is None:                    # U3 — period without phase is not a contract
        raise ValueError(
            "unit_cell_origin 미제공(계약 U3 위반) — MDL 기본 원점은 UV 원점이지 "
            "씬 원점이 아니라서, 주기가 맞아도 위상이 어긋나면 반 칸 이음매가 생긴다")
    ox, oy = float(origin[0]), float(origin[1])
    sh.CreateInput("unit_cell_m", F2).Set(_vec2(cell, cell))
    sh.CreateInput("unit_cell_origin", F2).Set(_vec2(ox, oy))
    sh.CreateInput("unit_albedo_sigma", F).Set(sigma)
    sh.CreateInput("unit_accent_frac", F).Set(accent)
    LOOK_STATS["unit_cell"] = LOOK_STATS.get("unit_cell", 0) + 1
    return True


def _vec2(a, b):
    from pxr import Gf
    return Gf.Vec2f(float(a), float(b))


def wire_unit_cell_to(mtl, unit_cell):
    """[GT-113 W3] Feed a ground_kit unit-cell ledger into an ALREADY-created ground
    material, post-hoc.

    `_wire_unit_cell` existed since v1.9 but had **zero callers** — `apply_ground`
    returns `unit_cell` to the scene, the scenes print it, and nothing ever reached
    `make_pbr(unit_cell=…)` because the field material is created long before the kit
    runs. This helper closes that loop without reordering any scene: call it after
    `apply_ground` with the material object and the returned ledger value. Authoring
    shader inputs after creation is ordinary USD; nothing about the prim set changes
    (R-2). Default absent call = byte-identical corpus.

    Returns True when wired. False (with a warning) when the material's shader is not
    NegObsGround — OmniPBR has no cell inputs, so wiring it would author dead attrs.
    Contract violations (U3 origin / U4 no-module) still raise, as designed.
    """
    from pxr import UsdShade, Sdf
    if unit_cell is None or not LOOK_MTL:
        return False
    # Normalise the ground_kit ledger row: `GROUND_DIMENSIONS["unit_cell"]` rows are
    # `(cell_m, (ox, oy), source_str)` — the 3rd element is provenance, not sigma.
    # A `(None, None, …)` row is an explicit no-module profile → silently no wiring
    # (that is the U4-legal absence, distinct from the U4 *violation* of jittering it).
    if len(unit_cell) > 2 and isinstance(unit_cell[2], str):
        unit_cell = tuple(unit_cell[:2])
    if unit_cell[0] is None:
        return False
    prim = mtl.GetPrim() if hasattr(mtl, "GetPrim") else None
    if prim is None or not prim.IsValid():
        return False
    sh_prim = prim.GetStage().GetPrimAtPath(
        prim.GetPath().AppendChild("Shader"))
    if not sh_prim or not sh_prim.IsValid():
        return False
    sh = UsdShade.Shader(sh_prim)
    try:
        sub = sh.GetSourceAssetSubIdentifier("mdl")
    except Exception:
        sub = None
    if sub != "NegObsGround":
        print(f"[룩v1][경고] wire_unit_cell_to: {prim.GetPath()} 의 셰이더가 "
              f"NegObsGround 가 아니다({sub}) — 셀 지터 미배선")
        return False
    F = Sdf.ValueTypeNames.Float
    F2 = Sdf.ValueTypeNames.Float2
    return _wire_unit_cell(sh, F, F2, unit_cell)


def _make_ground_pbr(stage, path, diff, nor, rough, scale_m, spec,
                     tint=None, roughness_const=None, specular_level=None,
                     bump=1.0, base_color=None, metallic=0.0,
                     unit_cell=None, cls=None, blend=None):
    """[realism v1] NegObsGround.mdl material - for the ground and slope families only.

    The `project_uvw` of OmniPBR is not triplanar but a **cubic projection**, so on a slope the
    texture smears and stretches down the fall line (confirmed in Phase1 E2 with a split-face
    test on a 38 deg slope). This MDL uses a normal-weighted soft triplanar plus a 45 deg
    auxiliary basis and has no such defect. Our scenes are full of stair risers, ramps and
    embankments, so the defect was concentrated **exactly where the drops are**.

    Note - `texture_scale` means something different from OmniPBR (triplanar vs cubic). The same
    scale_m gives a different tile size, so it is corrected by `_GROUND_SCALE_FIX`.
    """
    from pxr import UsdShade, Sdf, Gf
    mtl = UsdShade.Material.Define(stage, path)
    sh = UsdShade.Shader.Define(stage, path + "/Shader")
    sh.CreateImplementationSourceAttr(UsdShade.Tokens.sourceAsset)
    sh.SetSourceAsset(Sdf.AssetPath(MDL_GROUND), "mdl")
    sh.SetSourceAssetSubIdentifier("NegObsGround", "mdl")
    F = Sdf.ValueTypeNames.Float
    C3 = Sdf.ValueTypeNames.Color3f
    A = Sdf.ValueTypeNames.Asset
    B = Sdf.ValueTypeNames.Bool
    F2 = Sdf.ValueTypeNames.Float2

    def _tex(name, p, cs):
        i = sh.CreateInput(name, A)
        i.Set(p)
        try:
            i.GetAttr().SetColorSpace(cs)
        except Exception:
            pass

    # With diff=None no texture is bound -> the MDL returns white and the constant colour is
    # restored by the base_color multiplication (v1.7.0 constant-colour mode).
    if diff is not None:
        _tex("diffuse_texture_a", diff, "auto")
    if nor is not None:
        _tex("normalmap_texture_a", nor, "raw")
    if rough is not None:
        _tex("roughness_texture_a", rough, "raw")
    # [fatal C1 fix] The MDL has no diffuse_tint input, so previously a tint given by a scene was
    # **warned about and then discarded wholesale**. 77 calls across 30 scenes were affected, and
    # the sceneD4 Facade lost its tint (0.14,0.14,0.15) and was rendering at **7.1x** the intended
    # albedo. The diffuse_tint of OmniPBR is an albedo multiplication, so folding it into
    # base_color is **mathematically identical**.
    _bc = list(base_color) if base_color is not None else [1.0, 1.0, 1.0]
    if tint is not None:
        _bc = [c * t for c, t in zip(_bc, tint)]
    # [GT-108 ①②] Effective-albedo band. It must sit **here** and not at the scene call
    # sites: this is the one place where all three routes (bound texture, promoted
    # constant, constant-colour MDL) have already been folded into one number, and it is
    # also the only place that knows the texture's own mean. `_bc` alone is not the
    # albedo when a texture is bound - the MDL multiplies the two - so the texture mean
    # is passed in and the clamp is computed on the product.
    _band_tm = _texture_mean(diff) if diff is not None else None
    _bc, _banded = _albedo_band(cls, _bc, _band_tm)
    if base_color is not None or tint is not None or _banded:
        # `_banded` is in the condition because an untinted textured material authors no
        # base_color at all today (scene01's `PlazaLight` is the case that matters), and
        # a ceiling that cannot author the input is a ceiling that does nothing.
        sh.CreateInput("base_color", C3).Set(Gf.Vec3f(*_bc))
    s = _GROUND_SCALE_FIX / float(scale_m)
    sh.CreateInput("texture_scale_a", F2).Set(Gf.Vec2f(s, s))
    sh.CreateInput("bump_factor_a", F).Set(
        float(spec.get("bump", bump)))
    # [GT-113 W4] `use_blend` was a hard-coded False, sealing the MDL's complete
    # texture-set-B machinery (diffuse/normal/roughness_texture_b, per-vertex
    # `blend_tw`/`blend_wb` cross-fade, edge noise) that v1.9 shipped for exactly the
    # "0 px material transition" defect (survey F6). `blend=None` (every current call)
    # stays byte-identical; a caller may pass
    #   dict(diff=…, nor=…, rough=…, scale_m=…, default=…, edge_noise=…, edge_wl=…,
    #        use_wb=…)
    # to open the B set. The weight itself comes from the mesh primvar (or
    # `blend_default`), so geometry-side painting stays the kit's job (R3 pilot).
    if blend is None:
        sh.CreateInput("use_blend", B).Set(False)
    else:
        sh.CreateInput("use_blend", B).Set(True)
        if blend.get("diff"):
            _tex("diffuse_texture_b", blend["diff"], "auto")
        if blend.get("nor"):
            _tex("normalmap_texture_b", blend["nor"], "raw")
        if blend.get("rough"):
            _tex("roughness_texture_b", blend["rough"], "raw")
        _sb = _GROUND_SCALE_FIX / float(blend.get("scale_m", scale_m))
        sh.CreateInput("texture_scale_b", F2).Set(Gf.Vec2f(_sb, _sb))
        for _bk, _bv in (("blend_default", blend.get("default")),
                         ("blend_edge_noise", blend.get("edge_noise")),
                         ("blend_edge_wavelength", blend.get("edge_wl"))):
            if _bv is not None:
                sh.CreateInput(_bk, F).Set(float(_bv))
        if blend.get("use_wb") is not None:
            sh.CreateInput("blend_use_wb", B).Set(bool(blend["use_wb"]))
        LOOK_STATS["blend"] = LOOK_STATS.get("blend", 0) + 1
    # Repetition break-up - modular paving uses patch 0 (protects the pattern), natural ground 1
    sh.CreateInput("patch_mix_a", F).Set(float(spec.get("patch", 1.0)))
    # [GT-108 ②] `patch_wl` / `macro` / `rough_noise` / `tri_dither` become per-class
    # overrides. **A class that does not state one keeps the literal that was here**, so
    # every class except `asphalt` is bit-identical to before this row.
    sh.CreateInput("patch_wavelength_a", F).Set(float(spec.get("patch_wl", 4.0)))
    # Constant-colour mode has no texture high frequencies, so a strong macro reads as blotching.
    sh.CreateInput("macro_amp_a", F).Set(
        float(spec.get("macro", 0.07 if diff is None else 0.12)))
    # [GT-114 ⑤] The 14 m literal becomes a per-class spec ("macro_wl"). RTX probe:
    # the slope metric's effective band is ground-scale 1 cm-75 cm (centre 2-10 cm);
    # every albedo-modulation knob sat above it (14 m = 19×), which is the mechanical
    # reason flat% closed while slope did not. Ground paving classes state 0.55 m —
    # in-band with a 3-6 % amp; a class that states nothing keeps 14.0 = bit-identical.
    sh.CreateInput("macro_wavelength_a", F).Set(
        float(spec.get("macro_wl", 14.0)))
    sh.CreateInput("desat_bright_a", F).Set(0.0 if diff is None else 0.30)
    sh.CreateInput("saturation_a", F).Set(
        _effective_sat(spec, diff, base_color))
    sh.CreateInput("rough_noise_a", F).Set(float(spec.get("rough_noise", 0.22)))
    # [GT-117] 1.2 하드코딩 → 스펙화(rough_wl) + v1.10 물리 파라미터 배선.
    # 값을 적는 클래스가 없는 오늘은 전부 기본값 = 비트동일.
    sh.CreateInput("rough_noise_wavelength_a", F).Set(
        float(spec.get("rough_wl", 1.2)))
    if spec.get("diff_rough") is not None:
        sh.CreateInput("diffuse_roughness_a", F).Set(float(spec["diff_rough"]))
    if spec.get("grazing") is not None:
        sh.CreateInput("grazing_reflectivity_a",
                       F).Set(float(spec["grazing"]))
    # Constant-colour mode has no texture, so no axis-transition streaking occurs ->
    # 6 dithering noise taps are pure waste. Set to 0 to cut the cost.
    sh.CreateInput("tri_dither", F).Set(
        0.0 if diff is None else float(spec.get("tri_dither", 0.35)))
    sh.CreateInput("tri_dither_wavelength", F).Set(0.15)
    sh.CreateInput("tri_weight_exp", F).Set(6.0)
    if roughness_const is not None:            # Constant roughness requested -> transplanted to floor
        # **Trap**: this path has rough_mult_a=0 and therefore ignores the roughness map entirely.
        # That is why roughness_const is not passed when promoting a texture (diagnosis P1).
        sh.CreateInput("rough_mult_a", F).Set(0.0)
        sh.CreateInput("rough_floor_a", F).Set(float(roughness_const))
    if specular_level is not None:
        sh.CreateInput("specular_level_a", F).Set(float(specular_level))
    # Weathering (MDL v1.6.0). Without a weather key in the spec everything is 0 = no effect.
    w = spec.get("weather") or {}
    if w:
        for key, val in (("grime_strength", w.get("grime", 0.0)),
                         ("grime_desat", w.get("grime_desat", 0.0)),
                         ("grime_height", w.get("grime_h", 0.35)),
                         ("splash_strength", w.get("splash", 0.0)),
                         ("streak_strength", w.get("streak", 0.0)),
                         ("dust_strength", w.get("dust", 0.0)),
                         ("dust_desat", w.get("dust_desat", 0.0)),
                         ("weather_rough", w.get("wrough", 0.0))):
            sh.CreateInput(key, F).Set(float(val))
        LOOK_STATS["weather"] = LOOK_STATS.get("weather", 0) + 1
    # [major M1] NegObsGround is a reduction that only transplanted the metalness=0 path and has no
    # metallic input. Constant-colour metals (guardrails, bollards, shutters, fences - 37 kinds,
    # 113 calls) arriving here **lose their metallic character**. -> Metal is not routed to the MDL.
    if spec.get("bevel", 0.0) > 0.0:
        sh.CreateInput("round_edges_radius", F).Set(float(spec["bevel"]))
        sh.CreateInput("round_edges_roundness", F).Set(1.0)
        sh.CreateInput("round_edges_across_materials", B).Set(False)
    # -- [W2-C, T1 §1.1 defect (1) resolved] Attach the detail normal **to the ground branch too** --
    # These 6 lines are the wiring T1 §1.6(b) called "the crux of defect (1)". MDL v1.9.0 merely
    # opened the inputs and no caller bound them, so the 10 ground classes were rendering
    # pixel-identically to v1.8.0 `[measured - round_stamp "detail_wired: false", render log
    # "detail=0"]`.
    #   - `detail_texture_scale` is a **float** in the MDL (OmniPBR uses float2) - the wrong type
    #     is silently ignored.
    #   - `detail_rough_gain` defaults to 0 (off). It is the path §7 R1 proposed for "carrying
    #     sub-pixel microstructure through roughness variance" and is enabled only via the A/B knob.
    if spec.get("detail"):
        _dp, _db, _di = detail_source(cls)
        if _dp is not None:
            _tex("detail_normalmap_texture", _dp, "raw")
            sh.CreateInput("detail_bump_factor", F).Set(float(_db))
            sh.CreateInput("detail_texture_scale", F).Set(float(_di))
            if DETAIL_ROUGH_GAIN != 0.0:
                sh.CreateInput("detail_rough_gain",
                               F).Set(float(DETAIL_ROUGH_GAIN))
            LOOK_STATS["detail"] += 1
    _wire_unit_cell(sh, F, F2, unit_cell)
    # The tint was folded into base_color above (see there).
    for out in ("surface", "displacement", "volume"):
        mtl.CreateOutput(f"mdl:{out}",
                         Sdf.ValueTypeNames.Token).ConnectToSource(
            sh.ConnectableAPI(), "out")
    return mtl


# ===========================================================================
# [5] Stair and geometry builders
# ===========================================================================
def _stair_steps(x0, riser, tread, n, z_top, riser_list, tread_list):
    """Per-step (xa, xb, ztop) list. Descends towards +X from the top surface z_top.
    With riser_list/tread_list given, steps are irregular (otherwise uniform riser/tread x n).
    The number of steps returned is the length of whichever list is present (n if neither)."""
    risers = list(riser_list) if riser_list else [riser] * n
    treads = list(tread_list) if tread_list else [tread] * n
    m = max(len(risers), len(treads))
    if len(risers) < m:
        risers += [risers[-1]] * (m - len(risers))
    if len(treads) < m:
        treads += [treads[-1]] * (m - len(treads))
    steps = []
    xa = float(x0)
    z = float(z_top)
    for i in range(m):
        z = z - float(risers[i])           # Top surface (tread) height of step i
        xb = xa + float(treads[i])
        steps.append((xa, xb, z))
        xa = xb
    return steps


def build_straight_stairs(stage, prefix, x0, y0, y1, riser, tread, n, base_z,
                          mtl, riser_list=None, tread_list=None, z_top=0.0,
                          collider=True, width_pairs=None):
    """Straight stairs (stacked solids). Each step is a box whose tread is exposed.
    riser_list/tread_list support irregular steps (scene04). z_top = the ground at the top start.
    width_pairs: per-step (y0_i, y1_i) list (supports tapered widening). None means the common
      (y0, y1) for every step. If shorter than the step count, the last value repeats (safe extension).
      *Existing calls do not pass width_pairs -> entirely unaffected.*
    Returns: list of created Cube prims."""
    prims = []
    steps = _stair_steps(x0, riser, tread, n, z_top, riser_list, tread_list)
    wp = list(width_pairs) if width_pairs else None
    for i, (xa, xb, ztop) in enumerate(steps, 1):
        if wp is not None:
            wy0, wy1 = wp[min(i - 1, len(wp) - 1)]
        else:
            wy0, wy1 = y0, y1
        cy = (wy0 + wy1) / 2.0
        Ly = wy1 - wy0
        cx = (xa + xb) / 2.0
        cz = (ztop + base_z) / 2.0
        hz = ztop - base_z
        prims.append(add_box(stage, f"{prefix}/Step_{i}", (cx, cy, cz),
                             (xb - xa, Ly, hz), mtl, collider=collider))
    return prims


# --- S06-A · the true annular-sector convention ----------------------------
# [W3 K4(d) · T3 `w3_geom_reverify_v1.md` §3 NF-2 / §4]
#
# **What is wrong with the box convention.** `build_arc_steps` / `build_helix_steps`
# approximate an annular sector with an axis-aligned Cube given the **outer** chord
# width. Because a chord is the same length at every radius while the true sector
# narrows towards the centre, the box overshoots the a0/a1 rays at the inner radius by
#     overshoot = r_out * sin(dth/2) * margin - r_in * sin(dth/2)
# and the ratio is `margin * r_out / r_in`, **independent of `seg`** - measured
# **7.08125** on scene06's landing at seg in {24, 48, 96, 165, 330, 1000}. The absolute
# figure T3 measured: **190.9 mm** of solid protruding perpendicular past the nominal
# straight edge, in 24 teeth, on the y = -13.000 line where the landing meets step 0 and
# the deck; and step 0's box corners span azimuth 172.94-198.60 deg against a nominal
# 180.00-191.54 deg (**21.10 deg of inner overshoot** against the 0.11 deg outer
# overshoot the scene06 comment records as harmless).
#
# **The §10.5 box fallback ("cap Dth so the r_in overwidth <= 1.05x") is unreachable at
# any seg** - the ratio above does not contain Dth. T3's ruling is to author the mesh.
#
# **Why it is opt-in.** GT-6's acceptance test is a prim-hash / GT-delta diff that must
# come back **empty except the enumerated +2 mm landing-top rows**, and those rows are a
# *scene06* parameter change (`top_z` 4.998 -> 5.000), not a library change. Converting
# Cube -> Mesh necessarily rewrites the inventory, so a default-ON conversion would make
# GT-6's own proof impossible to run. The mechanism therefore lands here default OFF -
# the K4M precedent - and scene06 / 05 / 19 turn it on inside their own pilots, where the
# split proof is actually judged. `mesh=True` costs (arc_seg+1)*4 points per sector.
def _annular_sector_mesh(stage, path, cx, cy, r_in, r_out, a0_deg, a1_deg,
                         z_bot, z_top, mtl=None, collider=False, arc_seg=6):
    """A closed annular-sector prism. Exact at the a0/a1 rays; arcs faceted by `arc_seg`.

    Returns the Mesh. Point order per ring index i: [inner_bot, outer_bot, inner_top,
    outer_top], so the four wall/face loops index arithmetically.
    """
    from pxr import Gf, UsdGeom, UsdPhysics, Vt
    n = max(1, int(arc_seg))
    a0, a1 = math.radians(a0_deg), math.radians(a1_deg)
    pts = []
    for i in range(n + 1):
        a = a0 + (a1 - a0) * i / float(n)
        ca, sa = math.cos(a), math.sin(a)
        ix, iy = cx + r_in * ca, cy + r_in * sa
        ox, oy = cx + r_out * ca, cy + r_out * sa
        pts += [Gf.Vec3f(ix, iy, z_bot), Gf.Vec3f(ox, oy, z_bot),
                Gf.Vec3f(ix, iy, z_top), Gf.Vec3f(ox, oy, z_top)]

    def v(i, k):                                   # k: 0 ib, 1 ob, 2 it, 3 ot
        return i * 4 + k
    counts, idx = [], []

    def quad(a, b, c, d):
        counts.append(4)
        idx.extend([a, b, c, d])
    for i in range(n):
        quad(v(i, 2), v(i, 3), v(i + 1, 3), v(i + 1, 2))     # top (+Z)
        quad(v(i, 0), v(i + 1, 0), v(i + 1, 1), v(i, 1))     # bottom (-Z)
        quad(v(i, 1), v(i + 1, 1), v(i + 1, 3), v(i, 3))     # outer wall
        quad(v(i, 0), v(i, 2), v(i + 1, 2), v(i + 1, 0))     # inner wall
    quad(v(0, 0), v(0, 1), v(0, 3), v(0, 2))                 # cap at a0
    quad(v(n, 0), v(n, 2), v(n, 3), v(n, 1))                 # cap at a1
    m = UsdGeom.Mesh.Define(stage, path)
    m.CreatePointsAttr(Vt.Vec3fArray(pts))
    m.CreateFaceVertexCountsAttr(Vt.IntArray(counts))
    m.CreateFaceVertexIndicesAttr(Vt.IntArray(idx))
    m.CreateSubdivisionSchemeAttr(UsdGeom.Tokens.none)
    lo = Gf.Vec3f(min(p[0] for p in pts), min(p[1] for p in pts), float(z_bot))
    hi = Gf.Vec3f(max(p[0] for p in pts), max(p[1] for p in pts), float(z_top))
    m.CreateExtentAttr([lo, hi])
    prim = m.GetPrim()
    _bind_mtl(prim, mtl)
    if collider:
        UsdPhysics.CollisionAPI.Apply(prim)
    return m


def build_arc_steps(stage, prefix, cx, cy, r_in, r_out, a0_deg, a1_deg, seg,
                    top_z, base_z, mtl, collider=True, mesh=False, arc_seg=6):
    """Build one tier of an arc (a0..a1) as seg approximate trapezoidal boxes.
    Each segment = a Cube with rotZ (segment centre angle) + translate. Radial thickness = r_out-r_in,
    chord length = 2*r_mid*sin(dtheta/2)*1.02 (overlap margin preventing wedge gaps between segments).
    Returns: list of created Cube prims."""
    from pxr import UsdGeom, UsdPhysics, Gf
    r_mid = (r_in + r_out) / 2.0
    radial = r_out - r_in
    height = top_z - base_z
    cz = (top_z + base_z) / 2.0
    dth = math.radians((a1_deg - a0_deg) / float(seg))
    chord = 2.0 * r_out * math.sin(dth / 2.0) * 1.03   # Cover based on the outer radius (look r1: an r_mid basis leaves an outer wedge gap)
    prims = []
    if mesh:
        # [W3 K4(d)] True sectors: no chord margin, no inner overshoot, and the
        # neighbouring sectors share their rays exactly, so the 1.03 cover the box
        # convention needs against wedge gaps is not merely reduced - it is unnecessary.
        for k in range(seg):
            ak0 = a0_deg + (a1_deg - a0_deg) * k / float(seg)
            ak1 = a0_deg + (a1_deg - a0_deg) * (k + 1) / float(seg)
            prims.append(_annular_sector_mesh(
                stage, f"{prefix}/Seg_{k}", cx, cy, r_in, r_out, ak0, ak1,
                base_z, top_z, mtl, collider=collider, arc_seg=arc_seg))
        return prims
    for k in range(seg):
        a_mid = math.radians(a0_deg) + (k + 0.5) * dth
        px = cx + r_mid * math.cos(a_mid)
        py = cy + r_mid * math.sin(a_mid)
        cube = UsdGeom.Cube.Define(stage, f"{prefix}/Seg_{k}")
        cube.CreateSizeAttr(2.0)
        cube.CreateExtentAttr([Gf.Vec3f(-1, -1, -1), Gf.Vec3f(1, 1, 1)])
        xf = UsdGeom.Xformable(cube)
        # translate -> rotZ -> scale. Local X = radial, Y = tangential (chord), Z = height.
        xf.AddTranslateOp().Set(Gf.Vec3d(float(px), float(py), float(cz)))
        xf.AddRotateZOp().Set(math.degrees(a_mid))
        xf.AddScaleOp().Set(Gf.Vec3f(float(radial) / 2.0,
                                     float(chord) / 2.0,
                                     float(height) / 2.0))
        prim = cube.GetPrim()
        _bind_mtl(prim, mtl)
        if collider:
            UsdPhysics.CollisionAPI.Apply(prim)
        prims.append(cube)
    return prims


# [GT-114 ①] Default colour (0.85,0.72,0.10) → (0.60,0.48,0.10): linear luminance
# 0.703 → 0.478. The old value tone-mapped to a pastel lemon (display ≈ (0.94,0.88,
# 0.35)) that no worn safety-yellow strip reaches; the audit band is 0.40-0.50
# [derived]. Scenes that pass their own colour are untouched here — the nosing-class
# alb_max 0.50 band catches those at material creation instead.
def build_nosing(stage, prefix, x0, y0, y1, riser, tread, n, base_z=0.0,
                 mtl=None, color=(0.60, 0.48, 0.10), width=0.05, proud=0.001,
                 riser_list=None, tread_list=None, z_top=0.0):
    """Nosing anti-slip strip. A constant-colour box strip on the front edge (+X end) of each tread.
    With mtl=None a constant-colour material is created internally from color. width = strip width (X), proud = protrusion.
    Same step definition as build_straight_stairs (x0, y0, y1, riser, tread, n or lists).
    Returns: list of created prims."""
    if mtl is None:
        mtl = make_pbr(stage, prefix + "/NosingMtl",
                       diffuse_color=color, roughness_const=0.7, metallic=0.0)
    cy = (y0 + y1) / 2.0
    Ly = y1 - y0
    thk = proud + 0.005                     # Thin strip (partly embedded, protruding by proud)
    prims = []
    steps = _stair_steps(x0, riser, tread, n, z_top, riser_list, tread_list)
    for i, (xa, xb, ztop) in enumerate(steps, 1):
        # Inward from the front edge (xb) by width. Protrudes proud above the top surface.
        bx = xb - width / 2.0
        z_hi = ztop + proud
        cz = z_hi - thk / 2.0
        prims.append(add_box(stage, f"{prefix}/Nose_{i}", (bx, cy, cz),
                             (width, Ly, thk), mtl))
    return prims


# --- C0-7 · the baluster 안목 gate -------------------------------------------
# [법령] 도로안전시설 설치·관리 지침 (난간) — the **clear opening (안목)** between adjacent
# vertical members is 100 mm or less. The quantity is a *clear* span, surface to surface, not
# a centre pitch: with cylindrical balusters of radius r at pitch p the clear opening is
# `p - 2r`, which is exactly `baluster_gap` in this builder's parameterisation.
#
# Why this is a gate and not a default. `props_audit_w1/C1_scene_props_01-05.md` **C0-7**
# graded the railing family 치명: the statutory members existed but sat behind a flag, and the
# pit railing measured a 450 mm opening — "geometry justified by a statutory requirement was
# violating that requirement". A default can be overridden silently by any of the 16 call
# sites; a gate cannot. A caller asking for more than the statute gets clamped **and told**.
BALUSTER_CLEAR_MAX = 0.100

# --- GT-74 · the picket foot ------------------------------------------------
# `foot_pickets=True` lets an infill picket end **on the surface it stands over**
# instead of on the guard's own bottom envelope (`rail line - rail_h`). On stepped
# ground the two are not the same line: the rail is a straight ramp, the treads are
# a staircase, so the envelope floats above the tread by up to one riser.
# `PICKET_EMBED` is how far the picket is socketed into that surface (a contact, not
# a coplanar touch, so nothing z-fights); `PICKET_REACH_MAX` bounds how far below the
# envelope a picket may chase a ground_fn, so a parapet whose `ground_fn` reports the
# road far below still gets a picket and not a 3 m spear.
PICKET_EMBED = 0.012
PICKET_REACH_MAX = 0.30
# Clear gap between the guard plane and the bracketed grip rail axis, used both to
# place `sk.build_handrail` and to re-derive its radius from the returned rail y.
GRIP_WALL_GAP = 0.060
# Grip-rail end standard: the slim newel that carries the statutory bottom
# extension where the guard's own post line has already ended.
GRIP_NEWEL_R = 0.015


def build_railing_line(stage, prefix, y, x_start, x_top, run, drop, ground_fn,
                       mtl, rail_h=None, post_r=0.02, spacing=None, rail_r=0.03,
                       rail_mid_r=0.018, rail_mid_drop=0.45,
                       baluster_r=0.009, baluster_gap=0.098, handrail=True,
                       cliff_adjacent=True, nsteps=None, picket_pitch=None,
                       merge_handrail=False, foot_pickets=False):
    """One guardrail line (a generalisation of scene01 build_cues). Top rail + mid rail + posts.
    [GT-105] `rail_mid_r <= 0` suppresses the mid rail (and its knuckle) entirely —
    for callers whose baluster infill already carries the screen.
      y        : rail Y position
      x_start  : x where the horizontal extension starts (x_start..x_top is horizontal)
      x_top    : x where the slope starts (descending by drop towards +X from here)
      run,drop : horizontal length and drop of the sloped section
      ground_fn: x -> ground z callback (landing height of the post foot). Stepped on stairs.

    [GT-67 1-1] Picket density is tied to the flight's own scale, opt-in:
      cliff_adjacent : True (default) = this line is a **fall-protection guard**, so the
                       statutory 안목 below binds and the pitch is 2r + baluster_gap.
                       False = the caller declares no cliff / road / water alongside;
                       combined with a sub-1.20 m `drop` (건축법 시행령 §40, the fall from
                       which a guard becomes mandatory) the line is a hand guide and its
                       infill is a rhythm, not a screen.
      nsteps         : step count of the flight. With `cliff_adjacent=False` the derived
                       pitch is `run / nsteps` — one picket per riser, which is the
                       rhythm the flight itself already has.
      picket_pitch   : explicit centre pitch [m]; overrides the derivation.
    The derivation can only make a line **sparser** than the statutory pitch, never
    denser (`max` below), and is refused for drops at or above the 1.20 m threshold.

    [GT-67 1-2] `merge_handrail` (False / +1 / -1) folds the grip rail into the guard
    instead of standing it beside it: rail knuckles at the slope transition, end returns
    tying top rail -> mid rail -> end post, and the handrail carried on **brackets** off
    the guard plane (offset to the given side) with its top extension running back to
    `x_start`, so the two horizontal extension pieces read as one member.

    [GT-74 2] **The merged line carries ONE intermediate rail, not two.** GT-67 kept the
    guard's own mid rail (`rail_mid_drop` below the top rail) *and* hung the grip rail
    at 850 mm, so a merged line ran three parallel tubes — top 1.10, grip 0.85, mid 0.58
    `[measured on scene01]` — and the two lower ones read in every cut as a doubled,
    overlapping mid rail. When the grip rail is actually built (`merge_handrail` **and**
    `LOOK_GEO` **and** `handrail` **and** `run > 0.3`) the grip rail **is** the
    intermediate member and `RailMid*` is not authored. If `sk.build_handrail` raises,
    the guard falls back to its own mid rail — a guard never ends up with a single rail.

    [GT-74 4] **Terminations.** In merged-with-grip mode the two `Return*` sleeves are
    dropped: they were `rail_r` cylinders authored **coaxial with the end posts**
    (r 0.030 over r 0.020), i.e. an interpenetrating sleeve that read as a diameter step,
    not as a return. What replaces them terminates each run for real — a domed cap on
    every free rail end, a knuckle at the grip rail's own kink, and a slim newel under
    the grip rail's statutory bottom extension so the last 300 mm is carried instead of
    cantilevered over the landing.

    [GT-74 3] `foot_pickets` (see `PICKET_EMBED` above) foots the infill on the real
    stepped surface. Off by default.

    Defaults reproduce the previous geometry exactly — no existing call site passes any
    of the five kwargs.
    Returns: list of created prims."""
    # A shared guardrail is a finished built element, not a cue that changes its
    # section according to a look-development flag. Keep the familiar 1.10 m
    # rail line and a modest 1.5 m post rhythm in every render mode.
    if rail_h is None:
        rail_h = 1.1
    if spacing is None:
        spacing = 1.5
    ground_ref = float(ground_fn(x_top))       # Ground at the top of the slope
    top0 = ground_ref + rail_h                 # Rail top z at x_top
    L = math.hypot(run, drop)
    ang = math.degrees(math.atan2(drop, run))  # Slope angle (relative to horizontal)
    prims = []

    def _seg(tag, r, z_off):
        # Horizontal extension (x_start..x_top, z=top0-z_off) - the cylinder Z axis laid along X
        if x_top - x_start > 1e-6:
            prims.append(add_cylinder(
                stage, f"{prefix}/{tag}Ext",
                ((x_start + x_top) / 2.0, y, top0 - z_off),
                r, x_top - x_start, mtl, rotY=90.0))
        # Slope (x_top..x_top+run), z: top0 -> top0-drop
        prims.append(add_cylinder(
            stage, f"{prefix}/{tag}Slope",
            (x_top + run / 2.0, y, top0 - z_off - drop / 2.0),
            r, L, mtl, rotY=90.0 + ang))

    # [GT-74 2] Will a bracketed grip rail actually be authored below? Only then is
    # the guard's own mid rail a duplicate. The four conditions are exactly the ones
    # the handrail block is gated on, so the `LOOK_GEO = 0` arm keeps `RailMid*` and
    # is byte-identical to GT-67.
    grip_wanted = bool(merge_handrail) and bool(LOOK_GEO) and bool(handrail) \
        and float(run) > 0.3
    # [GT-105] `rail_mid_r <= 0` = the caller declares NO intermediate rail: its infill
    #   already carries the statutory screen (full-height balusters), so a mid bar would
    #   only cross the panel as a foreign horizontal (scene11 "통로 중간의 바"). Guard
    #   clause only — every pre-existing call site passes a positive radius and stays
    #   byte-identical (GT-67 Scope contract).
    mid_wanted = (not grip_wanted) and float(rail_mid_r) > 0.0
    _seg("RailTop", rail_r, 0.0)
    if mid_wanted:
        _seg("RailMid", rail_mid_r, rail_mid_drop)
    x_end = x_top + run

    # Vertical balusters - the guardrail standard of the road safety facility guideline. A clear
    # opening of 100 mm or less between balusters is a statutory requirement, so real Korean
    # guardrails are dense without exception. On a slope the balusters stay **vertical** (only the
    # rail tilts), which makes the silhouette markedly different. They are part
    # of the normal railing construction, so do not hide them behind a render
    # look toggle.
    if baluster_r > 0:
        # [W3 K4(a) · C0-7 gate] Enforce the 안목 here rather than trusting 16 call sites.
        # Census at the time of writing (AST, `scenes/*/*.py` + every kit): **16 sites, none
        # of which passes `baluster_gap`** - all 16 inherit 0.098 m, and scene18 alone opts
        # out with `baluster_r=0.0`. So the clamp below is inert today, by measurement, and
        # the gate exists for the call site that has not been written yet.
        if baluster_gap > BALUSTER_CLEAR_MAX + 1e-9:
            print(f"[룩v1][경고] 간살 안목 {baluster_gap * 1000:.0f} mm "
                  f"> 법정 {BALUSTER_CLEAR_MAX * 1000:.0f} mm — {prefix} 클램프")
            baluster_gap = BALUSTER_CLEAR_MAX
        pitch = 2.0 * baluster_r + baluster_gap
        picket_relaxed = False
        # [GT-67 1-1] Scale-linked density. The gate above is the **fall-protection**
        # rule (도로안전시설 지침 · 피난방화규칙 §15④); 건축법 시행령 §40 makes a guard
        # mandatory from a 1.20 m fall. Below that, with nothing to fall into alongside,
        # the line is a hand guide and a 116 mm screen over a 0.60 m plaza flight is a
        # section borrowed from a bridge parapet. Entered only when the caller says so.
        if picket_pitch is not None or not cliff_adjacent:
            nonstat_drop_max = 1.20              # 건축법 시행령 §40 난간 의무 낙차
            if picket_pitch is not None:
                want = float(picket_pitch)
            elif float(drop) >= nonstat_drop_max - 1e-9:
                want = pitch                     # statutory case — relaxation refused
                print(f"[룩v1][경고] 낙차 {float(drop):.2f} m ≥ "
                      f"{nonstat_drop_max:.2f} m — 살대 완화 거부, 법정 피치 유지 "
                      f"{prefix}")
            elif nsteps:
                want = float(run) / float(nsteps)        # one picket per riser
            else:
                want = pitch * (nonstat_drop_max / max(float(drop), 0.15))
            picket_relaxed = want > pitch + 1e-9
            pitch = max(pitch, want)             # never denser than the statute

        def _bal(idx, bx):
            """One vertical baluster at bx. Returns True when it was tall enough to build."""
            t = max(0.0, min((bx - x_top) / run, 1.0)) if run > 1e-9 else 0.0
            ztop = top0 - drop * t - rail_r          # Underside of the top rail
            gz = float(ground_fn(bx))
            # The balusters must come down **close to the ground**. Previously they stopped at the mid
            # rail and filled only 43 % of the guardrail height, and the actual opening in the lower
            # 0.45-0.60 m violated the cited statutory 100 mm by 11 to 28 times.
            # (Geometry justified by a statutory requirement was violating that requirement.)
            #
            # [GT-74 3] "close to the ground" was still measured against the **rail's own
            # bottom envelope**, which on a flight is a straight ramp while the surface is a
            # staircase. The envelope therefore sits above the tread everywhere except at the
            # tread's downstream edge, and the picket ends in mid-air: 60 mm over each tread
            # and 40 mm over the level extension `[measured on scene01, 0.38 m pitch]`. With
            # `foot_pickets` the picket lands on `ground_fn` and is socketed `PICKET_EMBED`
            # into it, with `PICKET_REACH_MAX` bounding the chase (see the constant).
            if foot_pickets:
                zbot = max(gz - PICKET_EMBED,
                           top0 - drop * t - rail_h - PICKET_REACH_MAX)
            else:
                zbot = max(gz + 0.04, top0 - drop * t - rail_h + 0.04)
            h = ztop - zbot
            if h <= 0.05:
                return False
            prims.append(add_cylinder(
                stage, f"{prefix}/Bal_{idx}", (bx, y, zbot + h / 2.0),
                baluster_r, h, mtl))
            return True

        xb = x_start + pitch * 0.5
        b = 0
        x_last = None
        while xb <= x_end - pitch * 0.25:
            if _bal(b, xb):
                x_last = xb
            xb += pitch
            b += 1
        # [W3 K4(a) · C0-7 gate, run end] The loop terminates at `x_end - 0.25*pitch`, so the
        # clear opening left between the last baluster and the rail terminus is
        # `x_end - x_last - r`, which reaches **1.25*pitch - r = 136 mm at the default pitch**
        # `[computed]` - the very 안목 the gate enforces everywhere else, violated at the one
        # place a pedestrian meets the rail end. One terminal baluster, flush with x_end,
        # closes it. It is placed only when the span actually exceeds the statute, so a run
        # whose length happens to divide evenly gains nothing.
        # [GT-67 1-1] Skipped when the pitch was relaxed: the trigger is the 100 mm 안목,
        # which by definition does not bind that line, and the extra picket would land
        # inside the end post anyway (r 0.009 at `x_end - r` vs a post of r 0.020 at
        # `x_end`) — an invisible duplicate. The end post closes the run there.
        if (not picket_relaxed) and x_last is not None \
                and (x_end - x_last) - baluster_r > BALUSTER_CLEAR_MAX + 1e-9:
            if _bal(b, x_end - baluster_r):
                b += 1
        LOOK_STATS["baluster"] = LOOK_STATS.get("baluster", 0) + b

    # Posts: landing on the real ground (ground_fn), top = the rail line.
    # Include both termini. The old incremental loop could leave the final
    # support up to one full bay short of the rail end, making a continuous run
    # read as if it had been cut off in mid-air.
    post_xs = [x_start]
    xp = x_start + spacing
    while xp < x_end - 1e-6:
        post_xs.append(xp)
        xp += spacing
    if x_end - post_xs[-1] > 1e-6:
        post_xs.append(x_end)
    for p, xp in enumerate(post_xs):
        gz = float(ground_fn(xp))
        t = max(0.0, min((xp - x_top) / run, 1.0)) if run > 1e-9 else 0.0
        railz = top0 - drop * t
        ph = railz - gz
        if ph > 1e-3:
            prims.append(add_cylinder(
                stage, f"{prefix}/Post_{p}", (xp, y, gz + ph / 2.0),
                post_r, ph, mtl))

    # -- Terminations (GT-67 1-2) ---------------------------------------
    # The two rail runs meet at `x_top` with open cylinder ends and stop dead at both
    # termini, so the infill panel reads as a loose leaf hung beside the flight. A
    # knuckle closes the kink; an end return ties top rail -> mid rail -> end post into
    # one closed frame, which is how a real end standard terminates. No GT effect —
    # members above the walked surface, no z(x, y) changes.
    def _rail_z_at(xe):
        t = max(0.0, min((xe - x_top) / run, 1.0)) if run > 1e-9 else 0.0
        return top0 - drop * t

    if merge_handrail:
        knuckles = [("RailTop", rail_r, 0.0)]
        if mid_wanted:
            knuckles.append(("RailMid", rail_mid_r, rail_mid_drop))
        for tag, r_j, z_off in knuckles:
            prims.append(add_cylinder(
                stage, f"{prefix}/{tag}Knuckle", (x_top, y, top0 - z_off),
                r_j, 2.0 * r_j, mtl))
        if grip_wanted:
            # [GT-74 4] Domed end caps instead of the coaxial `Return*` sleeves. The
            # top rail is `rail_r` 0.030 and the end post `post_r` 0.020, so the rail's
            # flat end face stood 10 mm proud of the post as an exposed cut ring at both
            # termini `[computed]`. A hemisphere of the rail's own radius, centred on the
            # rail axis at the terminus, closes that face; the post passes through it, so
            # the pair reads as one ball-ended standard.
            for tag, xe in (("Start", x_start), ("End", x_end)):
                prims.append(add_sphere(
                    stage, f"{prefix}/RailTopCap{tag}", (xe, y, _rail_z_at(xe)),
                    (rail_r, rail_r, rail_r), mtl))
        else:
            for tag, xe in (("Start", x_start), ("End", x_end)):
                prims.append(add_cylinder(
                    stage, f"{prefix}/Return{tag}",
                    (xe, y, _rail_z_at(xe) - rail_mid_drop / 2.0), rail_r,
                    rail_mid_drop, mtl))

    # -- Handrail -------------------------------------------------------
    # Evac/fire structure rules §15(4). **Unimplemented in all 33 scenes.**
    # dia 32-38, height 850, **horizontal end extension >=300** - that end hook is
    # characteristic of the Korean stair silhouette, yet our rails simply stopped dead.
    # No GT effect: a vertical/horizontal member above the stair surface, it does not change z(x,y).
    if LOOK_GEO and handrail and run > 0.3:
        try:
            hr_kw = {}
            if merge_handrail:
                # [GT-67 1-2] Carried ON the guard, not beside it: brackets off the
                # guard plane instead of a second post line, and the top extension
                # runs back to `x_start` so the guard's horizontal piece and the grip's
                # horizontal piece are one member. `ext_bot` keeps the statutory
                # 300 mm hook — that bend is the Korean silhouette, not clutter.
                hr_kw = dict(wall_y=y,
                             wall_side=(1.0 if float(merge_handrail) >= 0
                                        else -1.0),
                             wall_gap=GRIP_WALL_GAP,
                             ext_top=max(sk.K.HANDRAIL_EXT_MIN,
                                         x_top - x_start),
                             ext_bot=sk.K.HANDRAIL_EXT_MIN)
            hr = sk.build_handrail(
                stage, f"{prefix}/Handrail", y, x_top, run, drop, mtl,
                add_cylinder, z_top=ground_ref, ground_fn=ground_fn,
                strict=False, **hr_kw)
            # `build_handrail` returns a **dict**; `prims += dict` extended the list
            # with the dict's KEYS (7 strings per line). Geometry was never affected —
            # the prims are authored on the stage — but the returned list was wrong.
            # No call site consumes the return value (18 sites, all bare statements).
            prims += hr["prims"]
            LOOK_STATS["handrail"] = LOOK_STATS.get("handrail", 0) + 1
            if grip_wanted:
                # -- [GT-74 4] grip-rail end standards -----------------------
                # `build_handrail` lays three tubes and hangs brackets on the guard
                # plane at `HANDRAIL_POST_SPACING`; the run's two ends are open cut
                # faces, and the statutory 300 mm bottom extension reaches **past**
                # the guard's own end post, so it hung unsupported over the landing.
                # Radius is re-derived from the returned rail y (arm = wall gap + r),
                # never restated, so it cannot drift from the tube actually built.
                hy = float(hr["y"])
                hx0, hx1 = float(hr["x_start"]), float(hr["x_end"])
                hz0, hz1 = float(hr["z_top_rail"]), float(hr["z_bot_rail"])
                hr_r = max(1e-4, abs(hy - y) - GRIP_WALL_GAP)
                # knuckle at the grip rail's own kink (the guard already has one)
                prims.append(add_cylinder(
                    stage, f"{prefix}/GripKnuckle", (x_top, hy, hz0),
                    hr_r, 2.0 * hr_r, mtl))
                # domed caps on both free tube ends
                for tag, hx, hz in (("Top", hx0, hz0), ("End", hx1, hz1)):
                    prims.append(add_sphere(
                        stage, f"{prefix}/GripCap{tag}", (hx, hy, hz),
                        (hr_r, hr_r, hr_r), mtl))
                # newel under the outer end of the bottom extension. It foots on
                # `ground_fn` like every guard post, so the assembly has no member
                # that stops in mid-air.
                gz_n = float(ground_fn(hx1))
                h_n = hz1 - gz_n
                if h_n > 1e-3:
                    prims.append(add_cylinder(
                        stage, f"{prefix}/GripNewel", (hx1, hy, gz_n + h_n / 2.0),
                        GRIP_NEWEL_R, h_n, mtl))
        except Exception as e:
            print(f"[룩v1][경고] 손잡이 실패 {prefix}: {e}")
            if grip_wanted and float(rail_mid_r) > 0.0:
                # [GT-74 2] Degradation: the grip rail is what replaced the guard's
                # mid rail. Without it the guard would be a single top rail, so the
                # mid rail (and its knuckle) come back rather than leaving a gap.
                # [GT-105] Unless the caller opted out of the mid rail entirely
                # (`rail_mid_r <= 0`) — a single top rail is then the declared form.
                _seg("RailMid", rail_mid_r, rail_mid_drop)
                prims.append(add_cylinder(
                    stage, f"{prefix}/RailMidKnuckle",
                    (x_top, y, top0 - rail_mid_drop), rail_mid_r,
                    2.0 * rail_mid_r, mtl))
    return prims


def build_water(stage, path, x0, y0, x1, y1, z, thick=0.2, mtl=None):
    """Water slab. Constant colour (0.05,0.10,0.11), roughness 0.03, metallic 0.
    A thin box whose top sits at z. Returns: the Cube prim."""
    if mtl is None:
        mtl = make_pbr(stage, path + "_mtl",
                       diffuse_color=(0.05, 0.10, 0.11),
                       roughness_const=0.03, metallic=0.0)
    cx = (x0 + x1) / 2.0
    cy = (y0 + y1) / 2.0
    return add_box(stage, path, (cx, cy, z - thick / 2.0),
                   (abs(x1 - x0), abs(y1 - y0), thick), mtl)


def build_slope(stage, path, x0, z0, run, drop, y0, y1, thick, mtl,
                margin=0.3, collider=True):
    """A rotateY-rotated box slope. The centre and angle are computed so that the top surface is the
    plane (x0,z0) -> (x0+run, z0-drop). Angle = atan2(drop,run), length = hypot(run,drop) + margin at both ends.
    Returns: the Cube prim."""
    from pxr import UsdGeom, UsdPhysics, Gf
    ang = math.atan2(drop, run)                # The + face descends towards +X
    length = math.hypot(run, drop) + margin
    # Midpoint of the top surface (x0,z0) -> (x0+run,z0-drop)
    sx = x0 + run / 2.0
    sz = z0 - drop / 2.0
    # World mapping of local -Z (the thickness direction): rotateY(+ang) -> (-sin, 0, -cos)
    cx = sx - (thick / 2.0) * math.sin(ang)
    cz = sz - (thick / 2.0) * math.cos(ang)
    cy = (y0 + y1) / 2.0
    cube = UsdGeom.Cube.Define(stage, path)
    cube.CreateSizeAttr(2.0)
    cube.CreateExtentAttr([Gf.Vec3f(-1, -1, -1), Gf.Vec3f(1, 1, 1)])
    xf = UsdGeom.Xformable(cube)
    xf.AddTranslateOp().Set(Gf.Vec3d(float(cx), float(cy), float(cz)))
    xf.AddRotateYOp().Set(math.degrees(ang))   # The +X end goes down
    xf.AddScaleOp().Set(Gf.Vec3f(float(length) / 2.0,
                                 float(abs(y1 - y0)) / 2.0,
                                 float(thick) / 2.0))
    prim = cube.GetPrim()
    _bind_mtl(prim, mtl)
    if collider:
        UsdPhysics.CollisionAPI.Apply(prim)
    return cube


# ===========================================================================
# [5c] New stair builders v3 (helical, worn stone, rotation group, open riser, canopy)
#      Mathematical definitions: Docs/stair_typology_survey_v2.md §3 / brief v3 §B
# ===========================================================================
def build_helix_steps(stage, prefix, cx, cy, r_in, r_out, a0_deg, step_deg, n,
                      riser, z0, mtl, ccw=True, collider=True, base_drop=0.5,
                      mesh=False, arc_seg=6):
    """Helical/spiral stone stairs (shared by T9 and winders). For step i (0-based):
      centre angle a_i = a0_deg + (i+0.5)*step_deg*dir  (dir=+1 ccw, -1 cw)
      annular sector box: radial width = r_out-r_in, chord length = 2*r_mid*sin(rad(step_deg)/2)*1.02
        (1.02 overlap prevents wedge gaps between segments - reused from build_arc_steps)
      top z = z0 - (i+1)*riser  (descending), bottom = top - base_drop (solid).
    Each sector is placed by translate -> rotZ(a_i) -> scale (local X = radial, Y = tangential, Z = height).
    Returns: list of created Cube prims."""
    r_mid = (r_in + r_out) / 2.0
    radial = r_out - r_in
    half_rad = math.radians(step_deg) / 2.0
    chord = 2.0 * r_out * math.sin(half_rad) * 1.03    # Cover based on the outer radius (look r1 fix)
    direction = 1.0 if ccw else -1.0
    prims = []
    for i in range(n):
        a_deg = a0_deg + (i + 0.5) * step_deg * direction
        rad = math.radians(a_deg)
        px = cx + r_mid * math.cos(rad)
        py = cy + r_mid * math.sin(rad)
        top = z0 - (i + 1) * riser
        cz = top - base_drop / 2.0
        if mesh:
            # [W3 K4(d) · NF-2] Same convention as `build_arc_steps(mesh=True)`: the
            # sector spans exactly one `step_deg` about its own centre azimuth, so the
            # tread's plan edges land on the design rays instead of 190.9 mm past them.
            prims.append(_annular_sector_mesh(
                stage, f"{prefix}/Step_{i}", cx, cy, r_in, r_out,
                a_deg - step_deg * 0.5, a_deg + step_deg * 0.5,
                top - base_drop, top, mtl, collider=collider, arc_seg=arc_seg))
            continue
        prims.append(_oriented_box(
            stage, f"{prefix}/Step_{i}", (px, py, cz),
            (radial, chord, base_drop), mtl, collider=collider, rotz=a_deg))
    return prims


def build_helix_ramp(stage, prefix, cx, cy, r_in, r_out, a0_deg, a1_deg, seg,
                     z0, z1, thick, mtl, collider=True, top_face=False):
    """A smooth helical ramp (T10 car park ramp). The arc [a0,a1] is approximated by seg chord segments.
      Segment j (0-based): centre angle a_j = a0 + (j+0.5)*dth_deg
      Linear z interpolation: segment top centre z = z0 + (j+0.5)*dz_seg, dz_seg = (z1-z0)/seg
      Segment chord length L_c = 2*r_mid*sin(dth/2)
      **Local tangential tilt**: after placing the segment at bearing rotZ(a_j), tilt it so it rises
        or falls by dz_seg along the chord (= tangent = local Y). The rotation axis that tilts the
        tangent is perpendicular to it, i.e. local X (= the radial axis) -> **rotX** (not rotY).
        Tilt angle = atan2(dz_seg, L_c).
        Derivation: rotX(theta): z' = y*sin(theta) + z*cos(theta), so dz'/dy = sin(theta). To get a
        height change rate of dz_seg/L_c along +Y (forward along the chord), sin(theta) = dz_seg/L_c,
        hence theta = atan2(dz_seg, L_c).
        With dz_seg<0 (descending) theta<0 -> the +Y end goes down (correct).
      op order translate -> rotZ -> rotX -> scale (= _oriented_box): points apply in reverse,
        scale -> rotX (local, before bearing) -> rotZ (bearing) -> translate, so the tangential tilt is
        applied exactly about each segment's radial axis.
    Returns: (prim list, segment tilt angle [deg] - a single-element list since segments are uniform)."""
    r_mid = (r_in + r_out) / 2.0
    radial = r_out - r_in
    dth_deg = (a1_deg - a0_deg) / float(seg)
    dth = math.radians(dth_deg)
    L_c = 2.0 * r_mid * math.sin(dth / 2.0)
    dz_seg = (z1 - z0) / float(seg)
    tilt_deg = math.degrees(math.atan2(dz_seg, L_c))
    # [audit v4 I-3] Segment width uses the r_out chord length x1.03 - an r_mid basis (x1.02) leaves
    #   a through slit between segments at the outer radius (0.21 m measured in scene13). Same
    #   convention as build_arc_steps (lesson 4). The tilt follows the travel path, so the r_mid chord L_c is kept.
    seg_len = 2.0 * r_out * math.sin(dth / 2.0) * 1.03
    prims = []
    for j in range(seg):
        a_deg = a0_deg + (j + 0.5) * dth_deg
        rad = math.radians(a_deg)
        px = cx + r_mid * math.cos(rad)
        py = cy + r_mid * math.sin(rad)
        z_top = z0 + (j + 0.5) * dz_seg          # Centre height of the segment top surface
        cz = z_top - thick / 2.0
        # [W3 K4(d) · NF-1 - T3 `w3_geom_reverify_v1.md` §3] **This builder displaces the
        # top face it is asked to place.** `_oriented_box` composes translate -> rotZ ->
        # rotX -> scale and the line above places the box **centre**, then tilts about
        # that centre. For a slab of thickness t tilted by theta the top-face plane in the
        # segment frame is z'(y') = y'*tan(theta) + (t/2)/cos(theta), so the surface is
        #   shifted tangentially by (t/2)*sin(theta)  and  raised by (t/2)*(1/cos - 1).
        # Measured on the shipped scene06 rings `[measured-usd]`:
        #   SpiralFascia t 0.78, tilt -16.232 deg -> 109.0 mm shift, +16.34 mm lift
        #   SpiralSoffit t 0.34, tilt -21.749 deg ->  63.0 mm shift, +13.03 mm lift
        #   RailInnerTop t 0.064, tilt -33.513 deg -> 17.7 mm shift,  +6.38 mm lift
        # The fascia ring is *lucky*, not correct: its 109.0 mm shift is 0.95 of one
        # segment pitch (114.3 mm), so the top surface still just closes (span 114.95 vs
        # pitch 114.31 mm) - any change to `thick`, `seg` or the slope opens real gaps,
        # and NF-3's 388 mm leading-end notch is the same defect already visible.
        # `top_face=True` places the top-face centre instead of the box centre. Default
        # OFF because GT-6's split proof requires this commit's prim-hash diff to be
        # empty; scene06 flips it inside its own pilot, where the 16 mm is judged.
        #
        # **Correction to T3's prescription, verified numerically.** §3 NF-1 says to
        # "compensate `cz` by (t/2)(1/cos - 1) **and** the tangential origin by
        # (t/2)*sin". Applying both **double-counts**: the tangential move slides the
        # sloped plane, changing its height at the placement azimuth by -tan(th)*ds, so
        # the pair over-corrects by (t/2)*sin*tan - measured **-23.7 mm** where the raw
        # defect is **+12.0 mm** (t 0.78, tilt -14.05 deg). Solving both conditions at
        # once - top face centred on its azimuth AND passing through `z_top` there -
        #     z(u) = cz + (t/2)/cos + (u - s)tan ,  s = (t/2) sin ,  z(0) = z_top
        #  => cz = z_top - (t/2)/cos + s*tan = z_top - (t/2)*cos
        # so the z term is **+(t/2)(1 - cos)**, not -(t/2)(1/cos - 1). Verified on the
        # fascia ring: lift +12.028 mm -> 0.000, tangential offset +94.68 mm -> 0.000.
        if top_face and abs(tilt_deg) > 1e-9:
            th = math.radians(tilt_deg)
            cz += (thick / 2.0) * (1.0 - math.cos(th))
            shift = (thick / 2.0) * math.sin(th)          # along the local tangent (+Y)
            px -= shift * math.sin(rad)                   # local +Y = (-sin a, cos a)
            py += shift * math.cos(rad)
        prims.append(_oriented_box(
            stage, f"{prefix}/Seg_{j}", (px, py, cz),
            (radial, seg_len, thick), mtl, collider=collider,
            rotz=a_deg, rotx=tilt_deg))
    return prims, [tilt_deg]


def build_worn_stone_stairs(stage, prefix, x0, y0, y1, n, riser_mu, tread_mu,
                            blocks, seed, mtl, base_z, z_top=0.0, jr=0.03,
                            jt=0.10, jz=0.02, jyaw=3.0):
    """Worn irregular stone steps (T16). numpy RandomState(seed) fixed -> reproducible.
      Step i (0-based): riser_i = riser_mu + U(-jr,+jr), the top z descends cumulatively,
        x accumulates by tread_mu (xa_i..xb_i).
      Each step is split into blocks lateral blocks (nominal width Wb=(y1-y0)/blocks, overlapping
        neighbours by 1 mm), with per-block jitter:
          top z += U(-jz,+jz),  front/back x each += U(-jt/2,+jt/2) (-> a non-straight nosing),
          yaw = U(-jyaw,+jyaw) deg (rotZ).  The bottom is solid down to base_z.
    Returns: (prim list, per-step mean top z list, total run [= n*tread_mu])."""
    rng = np.random.RandomState(int(seed))
    Wb = (y1 - y0) / float(blocks)
    prims = []
    mean_tops = []
    xa = float(x0)
    z_prev = float(z_top)
    for i in range(n):
        riser_i = riser_mu + float(rng.uniform(-jr, jr))
        top_i = z_prev - riser_i
        xb = xa + tread_mu
        block_tops = []
        for j in range(blocks):
            by0 = y0 + j * Wb - 0.0005            # 1 mm overlap (0.5 mm each side)
            by1 = y0 + (j + 1) * Wb + 0.0005
            bz = top_i + float(rng.uniform(-jz, jz))
            bxa = xa + float(rng.uniform(-jt / 2.0, jt / 2.0))
            bxb = xb + float(rng.uniform(-jt / 2.0, jt / 2.0))
            yaw = float(rng.uniform(-jyaw, jyaw))
            cx = (bxa + bxb) / 2.0
            cy = (by0 + by1) / 2.0
            cz = (bz + base_z) / 2.0
            prims.append(_oriented_box(
                stage, f"{prefix}/S{i}_B{j}", (cx, cy, cz),
                (bxb - bxa, by1 - by0, bz - base_z), mtl,
                collider=True, rotz=yaw))
            block_tops.append(bz)
        mean_tops.append(sum(block_tops) / len(block_tops))
        xa = xb
        z_prev = top_i
    run = n * tread_mu
    return prims, mean_tops, run


def build_rot_group(stage, path, pivot_xy, rot_deg):
    """A pivoting rotation Xform group. Placing existing builders under its path rotates the whole
    group by rot_deg (degrees, +Z) about pivot_xy (world XY).
      xformOps = [translate(+pivot), rotateZ, translate(-pivot)]  (an op suffix avoids the name
      clash between the two translates). Under the USD row-vector convention points apply in
      reverse: (-pivot) -> rotZ -> (+pivot) = 'move the pivot to the origin, rotate, move back' =
      an exact pivot rotation.
    Returns: the Xform path (str) - place stairs and dressing under f"{path}/..." afterwards."""
    from pxr import UsdGeom, Gf
    xform = UsdGeom.Xform.Define(stage, path)
    xf = UsdGeom.Xformable(xform)
    px, py = float(pivot_xy[0]), float(pivot_xy[1])
    xf.AddTranslateOp(opSuffix="pivot").Set(Gf.Vec3d(px, py, 0.0))
    xf.AddRotateZOp().Set(float(rot_deg))
    xf.AddTranslateOp(opSuffix="unpivot").Set(Gf.Vec3d(-px, -py, 0.0))
    return path


def build_open_riser_stairs(stage, prefix, x0, y0, y1, riser, tread, n, z_top,
                            mtl_tread, mtl_stringer, tread_t=0.04, gap=0.025,
                            slits=0):
    """Open-riser stairs (T11/T19, fire escape and grating). No risers - you can see through.
      2 stringers: a sloped box of section 0.06 (Y width) x 0.25 (thickness) (reusing build_slope),
        at y0+0.03 / y1-0.03, descending from the top (x0, z_top) by run=n*tread and drop=n*riser.
      Treads: a plate of thickness tread_t on each step top (z = z_top - i*riser), inset by gap front and back.
      slits>0: the plate is split into (slits+1) strips along y with a 0.02 gap between them (grating).
    Returns: list of created prims."""
    run = n * tread
    drop = n * riser
    prims = []
    # 2 stringers (sloped boxes - build_slope: y0,y1 = 0.06 Y width, thick = 0.25 depth)
    for tag, yc in (("L", y0 + 0.03), ("R", y1 - 0.03)):
        prims.append(build_slope(
            stage, f"{prefix}/Stringer_{tag}", x0, z_top, run, drop,
            yc - 0.03, yc + 0.03, 0.25, mtl_stringer, margin=0.0,
            collider=True))
    Ly = y1 - y0
    for i in range(1, n + 1):
        xa = x0 + (i - 1) * tread
        xb = x0 + i * tread
        px = (xa + xb) / 2.0
        plen = (xb - xa) - 2.0 * gap             # Inset by gap front and back
        ztop = z_top - i * riser
        cz = ztop - tread_t / 2.0
        if slits > 0:
            nseg = slits + 1
            strip_w = (Ly - slits * 0.02) / nseg
            for s in range(nseg):
                sy0 = y0 + s * (strip_w + 0.02)
                syc = sy0 + strip_w / 2.0
                prims.append(add_box(
                    stage, f"{prefix}/Tread_{i}_{s}", (px, syc, cz),
                    (plen, strip_w, tread_t), mtl_tread, collider=True))
        else:
            prims.append(add_box(
                stage, f"{prefix}/Tread_{i}", (px, (y0 + y1) / 2.0, cz),
                (plen, Ly, tread_t), mtl_tread, collider=True))
    return prims


def build_canopy(stage, prefix, x0, x1, y0, y1, z_roof, post_r, mtl_roof,
                 mtl_post, roof_t=0.12, base_z=0.0):
    """Canopy (T20): 1 roof slab + 4 corner columns. The roof is roof_t thick from z_roof (underside).
    The columns run from base_z (ground 0 by default) to z_roof at the four corners (inset by the radius).
    Returns: list of created prims."""
    prims = []
    cx = (x0 + x1) / 2.0
    cy = (y0 + y1) / 2.0
    prims.append(add_box(stage, f"{prefix}/Roof", (cx, cy, z_roof + roof_t / 2.0),
                         (x1 - x0, y1 - y0, roof_t), mtl_roof, collider=True))
    ph = z_roof - base_z
    corners = ((x0 + post_r, y0 + post_r, "SW"), (x0 + post_r, y1 - post_r, "NW"),
               (x1 - post_r, y0 + post_r, "SE"), (x1 - post_r, y1 - post_r, "NE"))
    for pxp, pyp, tag in corners:
        prims.append(add_cylinder(
            stage, f"{prefix}/Post_{tag}", (pxp, pyp, base_z + ph / 2.0),
            post_r, ph, mtl_post, collider=True))
    return prims


# ===========================================================================
# [5b] Scene dressing builders (transplanted from scene01 - mtl as an argument instead of the M dict)
# ===========================================================================
TACTILE_TILE_M = 0.30        # one statutory pad = 0.30 x 0.30 m (36 dots, 6x6)
TACTILE_RGB = (0.85, 0.72, 0.10)     # fallback constant only — see below


def tactile_pbr(stage, path, scale_m=None, roughness=0.70):
    """Canonical tactile-paving material — `tactile_yellow` texture, not flat colour.

    ground_kit §12.5-3 traced "batch1 tactile pads render at 0.003 % of frame"
    partly to this: the pads were authored as a CONSTANT colour, so the 36
    statutory dots produce no shading whatsoever. `TEX["tactile"]` has held
    `tactile_yellow_diff/nor` all along and simply was never bound at 8 of the
    call sites. The role key and the file names stay `tactile` /
    `tactile_yellow_*` — ground_kit and the vegetation agent address them by
    that exact name.
      texture [measured — assets/veg_manifest_w2.json]: 1024 px, 36 dots (6x6),
      pitch 50.0 mm, dot Ø 25 mm nominal (area-equiv 25.7 measured, dot-area
      share 20.8 %), linear albedo 0.4504 (below the 0.55 clamp of §12.5-4).
      [W2-C · B7 ruling] Ø was 38.1 mm = 45.9 % dot area, which worked against
      §12.5-4's own luminance-step goal. Source constant:
      `assets/scene01/download_scene01_assets.py::TACTILE_DOT_D_MM`.
    Falls back to the constant colour when the texture is absent, because
    `assets/scene01/*` is git-ignored and a missing binding renders black —
    strictly worse than the flat yellow it replaces.
    """
    sm = float(TACTILE_TILE_M if scale_m is None else scale_m)
    diff = os.path.join(TEX["tactile"]["dir"], TEX["tactile"]["diff"])
    nor = os.path.join(TEX["tactile"]["dir"], TEX["tactile"]["nor"])
    if os.path.isfile(diff):
        return make_pbr(stage, path, diff,
                        nor if os.path.isfile(nor) else None, None, sm,
                        metallic=0.0, roughness_const=roughness)
    print("[점자블록][경고] tactile_yellow 텍스처 부재 — 상수색 폴백(돌기 음영 0). "
          "assets/scene01/download_scene01_assets.py 실행 필요")
    return make_pbr(stage, path, diffuse_color=TACTILE_RGB,
                    metallic=0.0, roughness_const=roughness)


def build_tactile(stage, path, x0, x1, y0, y1, mtl, z=0.0, proud=0.004):
    """A dot-type tactile paving strip (yellow). A rectangular band x0..x1 by y0..y1. Protrudes proud
    above the top surface z, with the dots expressed by a normal map (near flush). Returns: the Cube prim."""
    cx = (x0 + x1) / 2.0
    cy = (y0 + y1) / 2.0
    z_top = z + proud
    z_bot = z - 0.01
    return add_box(stage, path, (cx, cy, (z_top + z_bot) / 2.0),
                   (abs(x1 - x0), abs(y1 - y0), z_top - z_bot), mtl)


# ===========================================================================
# [5b] Real vegetation assets (NVIDIA S3, `assets/vegetation/`)
#
# **Why it is needed**: the old `build_tree` was a cylinder trunk plus sphere blob canopy and read
# as "candy floss" no matter what texture was applied. It is the most conspicuous instance of what
# the realism survey called "only 3 representation atoms: Cube/Cylinder/Sphere".
# Touching only the material layer cannot fix this - **the geometry has to change.**
#
# Traps (measured during procurement):
#   - The assets have `metersPerUnit = 0.01` (cm). A USD reference **does not convert units**
#     -> without a scale a cherry tree arrives at 464 m.
#   - References are relative, so the S3 directory structure (`Trees/`, `Shrub/`) must be kept as is.
#   - In these 4 species the leaves are **real modelled geometry** with no alpha channel ->
#     turning on `enable_opacity` breaks them instead (ZZ §10.2 scope correction).
# ===========================================================================
VEG_DIR = os.path.join(ASSETS_DIR, "vegetation")

# (relative path, **height exposed above ground** [m], weight) - reflects Seoul street tree statistics. `[W2 rework]`
#
# **`Japanese_Cherry` deleted (deleted, not reweighted)** - audit A P0-1.
#   (1) Seasonal convention: the leaf texture is **0.0 % green pixels** (full-bloom blossom pixels). The
#      verdict is by pixels, not by species name [measured - `A_trees_shrubs.md` §9].
#   (2) Frequency: cherry is about 4th at ~7 % among Seoul street trees, yet its weight was **62.5 %** -
#      about 9x the Seoul reality and 3.4x even the national figure (18.6 %) [statistic - same §5].
#
# Basis for the new mix: the top 2 in Seoul 2019 (306,313 trees) are **ginkgo 35.8 % and London plane 20.9 %**,
# but neither can be procured (ginkgo = confirmed absent from S3 / London plane = the leaf texture is brown
# autumn foliage and would need a greened derivative first). => **Build a broadleaf-dominant mix from close substitutes**:
#   Elm_Sapling (Ulmaceae = substitute for zelkova), Shumard_Oak (oak = substitute for pin oak)
#   = broadleaf 63.6 %, conifer/evergreen 36.4 %. The current pine family drops from 37.5 % to **18.2 %**.
#   `[estimate - weight allocation]` The statistics give ratios per species but not the substitute mapping ratios.
#
# **The height used is `zmax` (exposure above ground), not the full bounding height.**
#   `add_vegetation` scales by `s = target_h / native_h`, so feeding the full height for an asset with
#   `zmin < 0` shortens the above-ground exposure by that much (the defect White_Pine suffered at -15 %,
#   A §6-c). The 3 new species use `zmax` from the start so the same defect is not repeated.
VEG_TREES = [
    # relative path                  native_h  w   note
    ("Trees/Elm_Sapling.usd",         3.0867, 4),  # Elm sapling - substitute for zelkova/fringe tree, near field 3 m
    ("Trees/Shumard_Oak.usd",        10.8989, 3),  # Oak - substitute for pin oak, mid and far field
    ("Trees/Chinese_Juniper.usd",     2.5164, 2),  # Juniper - most common in temple, government and school landscaping
    ("Trees/White_Pine.usd",          2.35,   1),  # Pine (small) - zmin -0.351 uncorrected [known defect A §6-c]
    ("Trees/Yellow_Pine.usd",        26.99,   1),  # Pine (large) - for the far field and backdrop woodland
    # [W3 K4(b)] **Pooled — this closes the K4M blocker.** The micro-commit `1346b70`
    # shipped `BARE_SUBPRIMS` for three species of which only `Elm_Sapling` was in this
    # list, so `bare=True` could never yield a uniformly leaf-off frame and every
    # consumer had to build its own table (scene04 did exactly that). With these two
    # rows the bare-capable set is fully reachable. Weights are deliberately low: this
    # list is now only the **availability probe** for `veg_available()` / `veg_pool()`
    # — species SELECTION moved to `VEG_SPECIES` + `SCENE_SPECIES` below and no longer
    # reads these weights at all.
    ("Trees/Gray_Birch.usd",          3.3294, 1),  # Birch - park/apartment, bare-capable
    ("Trees/Lombardy_Poplar.usd",    13.6709, 1),  # 양버들 - riverside, bare-capable
]
# [measured - `assets/veg_manifest_w2.json` (2026-07-29, usd-core 26.8, UV pixel verdict)]
#   Elm_Sapling     zmax 3.0867, 113,268 tri, leaf beech_leaf green 99.2 % - PASS
#   Shumard_Oak     zmax 10.8989, 99,509 tri, oakleaves 1-4 green/olive 100 % - PASS
#   Chinese_Juniper zmax 2.5164, 27,098 tri, pine_needles green 80.2 % + yellow-green 19.8 % - PASS
VEG_SHRUB = [("Shrub/Boxwood.usd", 0.74, 1)]  # Boxwood

# ===========================================================================
# K4(b) · SPECIES — one route, one species  `[intake S-1 … S-4]`
# ===========================================================================
# **The defect this replaces.** `build_tree` drew a species per tree from a weighted
# global pool seeded by a **coordinate hash** (`pool[rnd.randrange(len(pool))]`), so a
# single Korean street row came out as a five-species botanical garden. Live census at
# the time of writing, taken off the composed prim inventory of all 33 scenes
# `[measured - 259 tree instances, 26 scenes]`: scene03 **5 species over 16 trees**,
# scene06 **5 over 20**, scene07 **5 over 15**, scene11 **4 over 24**, scene13 **4 over
# 12**. A Korean tree route is one species, one crown form, one pitch - 조례 제7조1라
# and 시행규칙(수관 일정) `[law]`, Damyang metasequoia road n=12 and six ordinary
# sidewalk files `[intake_policy §4.2]`. The re-roll is therefore **deleted**, not
# reweighted, and selection becomes a per-scene declaration.
#
# `VEG_SPECIES` replaces `VEG_TREES` as the source of truth. All ten rows are
# `verdict: PASS` in `assets/veg_manifest_w2.json`; every `native` below was
# **re-measured this session** with usd-core 26.8 (BBoxCache over the default prim,
# metersPerUnit applied) and reproduces spec §10.2 to 4 dp - the table is confirmed,
# not copied.
VEG_SPECIES = {
    # key            rel path                        native_h (zmax)  role
    "elm":       ("Trees/Elm_Sapling.usd",      3.0867, "street_nearfield"),
    "oak_pin":   ("Trees/Shumard_Oak.usd",     10.8989, "street_broadleaf"),
    "ash":       ("Trees/Fraxinus.usd",         5.3408, "street_broadleaf"),
    "birch":     ("Trees/Gray_Birch.usd",       3.3294, "park_apartment"),
    "poplar":    ("Trees/Lombardy_Poplar.usd", 13.6709, "riverside"),
    "juniper":   ("Trees/Chinese_Juniper.usd",  2.5164, "temple_office_evergreen"),
    "fir":       ("Trees/Douglas_Fir.usd",      6.0263, "temple_mountain_conifer"),
    "oak_red":   ("Trees/Scarlet_Oak.usd",     12.4089, "park_broadleaf"),
    "oak_black": ("Trees/Black_Oak.usd",       19.7389, "far_background_broadleaf"),
    # far background ONLY - tri_effective 15,597,637 `[veg_manifest_w2]`
    "spruce":    ("Trees/Colorado_Spruce.usd",  3.8713, "far_background_conifer"),
}

# **Retired** `[spec §10.2]`: `White_Pine` (uncorrected `zmin -0.351`, absent from the
# PASS manifest) and `Yellow_Pine` (absent from the PASS manifest). They were drawn in
# **13 of the 26 tree scenes** by the re-roll, which is where `placement_lint`'s LINT-4b
# retired-species ERRORs come from. Not deleted from `VEG_TREES` - that list is now only
# an availability probe - but no `SCENE_SPECIES` row may name them.
VEG_RETIRED = {"Trees/White_Pine.usd": "elm", "Trees/Yellow_Pine.usd": "oak_black"}

# Per-scene assignment, keyed by the scene's **ROOT token** (`/World/<token>/...`), so
# the ~25 `build_tree` call sites need no edit `[intake_policy §4.3]`. Value is
# `(route, belt)`: `route` is the one species of the walked route, `belt` the species of
# a *physically separate* backdrop planting (far bank, mountain stand). A scene gets its
# belt only by passing `species=` explicitly - `build_tree` cannot tell a route tree from
# a belt tree by its prefix, and guessing is exactly the kind of invention this table
# exists to stop. Until the eight S-WPs pass `species=`, every tree in a scene is its
# route species; that hand-over is spec §5.3's "K4(b) -> all eight S-WPs' veg= PARAMS".
#
# Batch1 tokens are not the file names: sceneC1=Scene26 · C2=Scene27 · C4=Scene28 ·
# D2=Scene29 · D3=Scene30 · D4=Scene31 · N1=Scene22 · N2=Scene32 · N3=Scene23 ·
# N4=Scene24 · N5=Scene25 · D1=Scene33 `[measured - prim inventory]`.
SCENE_SPECIES = {
    "Scene01": ("elm",     None),        # 캠퍼스 계단 - zelkova substitute, 3.0 m planters
    "Scene02": ("elm",     None),        # 지하도 - no row in §10.2 (C-4); planter trees only
    "Scene03": ("poplar",  "oak_black"),  # 하천 제방 - 양버들 silhouette, far bank belt
    "Scene04": ("oak_red", "oak_black"),  # 공원 침목길 (scene04 pins its own table locally)
    "Scene05": ("ash",     None),        # 야외공연장 - 이팝나무 substitute, civic
    "Scene06": ("oak_pin", None),        # 보행육교 - the flagship arterial row
    "Scene07": ("juniper", "fir"),       # 산사 - 향나무 route, mountain conifer stand
    "Scene08": ("ash",     None),        # 침상광장 - civic plaza, rides 05
    "Scene09": ("birch",   "oak_black"),  # 호수공원 수변
    "Scene10": ("oak_red", "oak_black"),  # 공원 데크 (scene10 pins its own pool locally)
    "Scene11": ("ash",     None),        # 보도육교 - arterial sidewalk
    "Scene12": ("poplar",  None),        # 수변 데크길 - matches 03 / 17
    "Scene13": ("birch",   None),        # 지하주차 진입부 - apartment landscaping
    "Scene14": ("ash",     None),        # 착시 대계단 - civic
    "Scene16": ("elm",     None),        # 캐노피 그늘 - street verge, rides 01
    "Scene17": ("poplar",  "oak_black"),  # 한강 제방
    "Scene18": ("juniper", None),        # 백사장 진입 - coastal conifer (S18 lane pins locally)
    "Scene19": ("ash",     None),        # 옥상 부채꼴 - single planter tree
    "Scene20": ("elm",     None),        # 사선 계단 - granite plaza
    "Scene27": ("oak_red", None),        # C2 낙엽 - forced by the oakfall debris assets
    "Scene30": ("oak_pin", None),        # D3 노변 배수로 - rural arterial verge
    "Scene22": ("elm",     None),        # N1 그림자 띠 - plaza planters
    "Scene32": ("juniper", None),        # N2 아스팔트 패치 - street verge, 2 trees
    "Scene23": ("elm",     None),        # N3 트롱프뢰유 - plaza planters
    "Scene24": ("elm",     None),        # N4 완경사 램프 - near-field ramp corridor
    "Scene25": ("ash",     None),        # N5 플러시 그레이팅 - street trees on one verge
    "Scene28": ("elm",     None),        # C4 젖은 계단 - plaza planters
}
# Scenes with no row fall back here rather than to a random draw. `elm` is the
# near-field street default of §10.2 and the smallest broadleaf in the set, so an
# unlisted scene gets the least surprising tree, not the loudest one.
SCENE_SPECIES_DEFAULT = "elm"

# **S-4 statutory floor for street rows** `[law - 서울 시행규칙]`: height >= 3.5 m and
# trunk O >= 0.10 m at breast height. Honest limitation, stated rather than promised
# around: `add_vegetation` applies **one uniform scale**, so a +-8 % height instance is
# also +-8 % in DBH - "same species, different age" is not expressible in this pipeline.
STREET_TREE_MIN_H = 3.5
STREET_TREE_MIN_DBH = 0.10

# **Longitudinal pitch of a street row.** 조례 제7조1가 gives 6-8 m, 고시 4-8 m `[law]`;
# the lane ruling for W3 is the **8.0 m** end of that band (intake_policy §4.2's own
# proposal was 7.0 m - superseded, both are inside the statute and 8.0 m is what the
# supervisor set). Successive pitches must not differ by more than 1 % (linter gate D).
TREE_PITCH_M = 8.0

# **Three-band placement.** A frame reads as a real route when the planting is
# stratified, not when it is scattered: the route band carries the pitch and the
# species, the verge band carries the shrubs/turf, and the belt band carries a
# *different* stand at a distance where its crown cannot roof the walked corridor.
# `d_min` is the lateral distance from the walk centreline at which a band may start;
# the belt figure is derived in `CANOPY_TUNNEL_RECIPE` below, not guessed.
TREE_BANDS = {
    "route": dict(d_min=1.00, pitch=TREE_PITCH_M, species="route"),
    "verge": dict(d_min=0.30, pitch=None,          species=None),
    "belt":  dict(d_min=7.50, pitch=None,          species="belt"),
}

# --- Crown geometry, and the scene07 canopy-tunnel recipe -------------------
# `[measured this session - usd-core 26.8, leaf-mesh bbox against the full bbox]`
#     species            H (m)     R_crown   R/H     crown base   base/H
#     Gray_Birch          3.3322    1.336    0.401     0.648 m     0.195
#     Elm_Sapling         3.0871    0.875    0.283     0.884 m     0.286
#     Lombardy_Poplar    13.6709    2.419    0.177     1.936 m     0.142
# Only the three trunk+leaves assets can be crown-measured this way. `Shumard_Oak`,
# `Fraxinus`, `Douglas_Fir`, `Scarlet_Oak`, `Black_Oak` and `Colorado_Spruce` carry
# their foliage in MASH `PointInstancer`s whose prototypes sit at the origin, so a
# mesh-points bbox under-reports them (`Shumard_Oak` returns H 9.257 against a true
# zmax of 10.8989). **Do not quote a crown radius for a MASH species from this method.**
#
# **CANOPY_TUNNEL_RECIPE — for scene07's E7-8, recorded here, NOT applied.**
# `w3_s07_rebuild_v1.md` §5.2 shipped an A/B proving two near-field framing trunks were
# **the entire DARK/OCCL delta** of the rebuild (`side_slope` 87.9 -> 10.1 mean
# luminance; `h0.9_d2` 98.1 -> 48.0), and diagnosed the cause as structural: the
# corridor is **3.4 m** wide (half-width 1.70 m), the south margin is **1.8 m below**
# the walk, and a broadleaf big enough to read as old growth roofs the walk from 30-40 %
# of its own height. The geometric statement of "does not roof the corridor" is
#     d  >  half_width + R_crown  =  1.70 + (R/H) * h
# so at a 12 m target height a broad crown (R/H ~ 0.48, the report's figure for
# `Shumard_Oak`) needs **d > 7.46 m**, while a columnar high-crown species needs
# **d > 3.82 m** at the measured `Lombardy_Poplar` ratio 0.177 - and its crown does not
# even begin until 0.142 h = 1.70 m above its own base, which on a margin 1.8 m below
# the walk puts the first leaf **at walk level**. That is the whole recipe: the tunnel
# read must come from crowns closing in **image space** on a belt beyond the judged
# near-ground cones, never from near-field crowns physically over the walk (H16 forbids
# trading a live gate for a dressing item).
CANOPY_TUNNEL_RECIPE = dict(
    corridor_w=3.40, half_w=1.70, south_margin_dz=-1.80,
    d_min_broadleaf=7.50,        # 1.70 + 0.48*12.0 = 7.46, rounded up
    d_min_columnar=4.00,         # 1.70 + 0.177*12.0 = 3.82, rounded up
    columnar_species="poplar",   # measured R/H 0.177, crown base 0.142*h
    belt_species="fir",          # scene07's declared mountain stand (SCENE_SPECIES)
    note="belt only, beyond the h0.3/h0.9 d2-d5 cones; no near-field framing trunks",
)


def scene_token(prim_path):
    """`/World/Scene06/Verge/Tree_3` -> `Scene06`. Empty string when not a scene path."""
    parts = str(prim_path).split("/")
    return parts[2] if len(parts) > 2 and parts[1] == "World" else ""


def resolve_species(prefix, species=None, belt=False):
    """(rel, native_h) for the species this prim should be. **No random draw.**

    species : an explicit `VEG_SPECIES` key (a scene pinning a belt or a second route),
              or None to take the scene default from `SCENE_SPECIES`.
    belt    : with species=None, take the scene's belt species instead of its route
              species. Falls back to the route when the scene declares no belt.

    Resolution never fails: an unknown key, an unlisted scene and a missing asset all
    fall back down the same chain to `SCENE_SPECIES_DEFAULT`, and finally to the first
    available `VEG_TREES` row, so a species typo can never cost a scene its vegetation.
    """
    key = species
    if key is None:
        route, blt = SCENE_SPECIES.get(scene_token(prefix), (None, None))
        key = (blt or route) if belt else route
    row = VEG_SPECIES.get(key) or VEG_SPECIES.get(SCENE_SPECIES_DEFAULT)
    if row and os.path.isfile(os.path.join(VEG_DIR, row[0])):
        return row[0], row[1]
    for rel, native, _w in VEG_TREES:                  # last-resort availability walk
        if os.path.isfile(os.path.join(VEG_DIR, rel)):
            return rel, native
    return (row[0], row[1]) if row else (None, None)


def veg_pool():
    """Weighted pool containing only the species actually present on disk.

    Deleting `Japanese_Cherry` changed one row, so judging availability by "the first row exists"
    would **wipe the vegetation out of 30 scenes** depending on procurement state. Only what
    exists is used.
    """
    return [t for t in VEG_TREES
            if os.path.isfile(os.path.join(VEG_DIR, t[0]))]


def veg_available():
    """Whether the vegetation assets actually exist. If not, fall back to procedural blobs."""
    return bool(veg_pool())


def _deactivate_seasonal(stage, asset_path, usd_rel, table=None):
    """Turn off season-specific sub-prims of a referenced vegetation asset.

    The season convention is judged on leaf/flower TEXTURE PIXELS, not on the
    species name. `Rhododendron` is a full-bloom scan (76.7 % of the basecolor
    is magenta), so the shrub itself is season-neutral only once `/Root/Flowers`
    is deactivated. Deactivation removes the prim from composition, so the
    flower geometry is never drawn and costs nothing.
    Silent no-op when the asset has no registered seasonal prims.

    table: which registry to read. Default `None` -> `SEASONAL_SUBPRIMS`, the
      library-wide unconditional one, so the existing call site is unchanged.
      `BARE_SUBPRIMS` is passed by the **opt-in** leaf-off path of `build_tree`.
    """
    names = (SEASONAL_SUBPRIMS if table is None else table).get(usd_rel)
    if not names:
        return 0
    off = 0
    for nm in names:
        try:
            p = stage.GetPrimAtPath(f"{asset_path}/{nm}")
            if p and p.IsValid():
                p.SetActive(False)
                off += 1
        except Exception as e:                 # never let this kill the scene
            print(f"[룩v1][경고] 계절 프림 비활성 실패 {asset_path}/{nm}: {e}")
    if off:
        LOOK_STATS["seasonal_off"] = LOOK_STATS.get("seasonal_off", 0) + off
    return off


def add_vegetation(stage, prim_path, usd_rel, pos_m, yaw_deg=0.0,
                   target_h=None, native_h=None, tilt_deg=(0.0, 0.0),
                   scale_mul=1.0):
    """Attach a vegetation USD as a reference. The cm -> m unit conversion is automatic.

    With target_h given it is scaled to that height - the tree height the scene intended via
    `trunk_h` must be preserved or the shadow and occlusion composition breaks.
    """
    from pxr import Usd, UsdGeom, Gf
    asset = os.path.join(VEG_DIR, usd_rel)
    if not os.path.isfile(asset):
        return None
    unit = 0.01                                # Asset metersPerUnit (measured)
    try:
        src = Usd.Stage.Open(asset)
        unit = (UsdGeom.GetStageMetersPerUnit(src)
                / UsdGeom.GetStageMetersPerUnit(stage))
    except Exception:
        pass
    # The reference is attached to a **child**. The Debris family USDs carry their own xformOps
    # (translate/rotateXYZ/scale) on the root, so calling AddTranslateOp again on the prim that
    # holds the reference dies with "already exists in xformOpOrder".
    # (The Trees family has no root op and merely passed by luck.)
    xf = UsdGeom.Xform.Define(stage, prim_path)
    UsdGeom.Xform.Define(stage, prim_path + "/Asset") \
        .GetPrim().GetReferences().AddReference(asset)
    xf.AddTranslateOp().Set(Gf.Vec3d(*[float(v) for v in pos_m]))
    xf.AddRotateZOp().Set(float(yaw_deg))      # Order matters: T -> R -> S
    # Slope following and per-instance tilt. Without it, leaves and rubble lie flat and float in
    # mid-air on a slope - yaw alone is not enough for scatter.
    tx, ty = (float(tilt_deg[0]), float(tilt_deg[1])) if tilt_deg else (0.0, 0.0)
    if abs(tx) > 1e-6:
        xf.AddRotateXOp().Set(tx)
    if abs(ty) > 1e-6:
        xf.AddRotateYOp().Set(ty)
    s = unit * ((float(target_h) / float(native_h))
                if (target_h and native_h) else 1.0) * float(scale_mul)
    xf.AddScaleOp().Set(Gf.Vec3f(s, s, s))
    return xf



# --- 3D scatter (leaves, gravel, debris, rocks) -----------------------------
# **Why it is needed**: leaves, gravel and debris laid on a plane as texture read as "lino".
# User feedback: *"get the leaves out of looking like laid lino as well"*
# Asphalt and concrete are correctly flat, but **a solid object faked as a plane** must be 3D.
# S3 `Assets/Vegetation/` holds Debris 26, Leaves 16 and Rocks 75 kinds.
# (relative path, effective area covered by one instance [m2], triangle count)
#   The effective area is not an estimate but a **measurement made by projecting the triangles onto XY and rasterising**.
#   The existing leaves of sceneC2 were 900 flattened ellipsoids 6 mm thick, yet the total cover
#   was **only 0.96 m2**, so the leaves visible on screen were effectively all texture pattern.
#   -> The exact cause of the "lino" look, and why cover must be handled as area, not count.
#   [correction 2026-07-29, red team R8 -> W1 re-judgement] `oakfall2` was first corrected from (0.0030/520) to
#   (0.0038/582), but the W1 ground-cover audit fixed the cover at **0.0054 m2** by independent
#   re-rasterisation with usd-core (rasteriser interpretation validated, invariant in N, silhouette inspected;
#   `Docs/surveys/props_audit_w1/B_groundcover_debris.md` §6, redteam_w1_assets ruled in favour).
#   **0 render impact** - the only call site, `sceneC2_leaf_stairs.py:563`, filters for `fallcluster`
#   only, so this row never enters the scatter count formula `n = A*(-ln(1-cover))/mean_cov`.
#   Warning: single leaves maplefall1 (measured 0.0081) and oakfall1 (0.0048) and the 2 cluster rows (0.0584/0.0239)
#   also show systematic deviation - the fallcluster rows that do enter the sceneC2 count formula **do affect
#   the render**, so they are replaced together with the render gate in the W2 leaf globalisation (G2) (audit B A3).
# [W2, audit B A3 - **all 5 rows replaced**] Effective cover is unified to team B's independent re-rasterisation.
#   The source of the old values (`asset_audit_v1.md`) has no calculation code in the repository, so the cause cannot be established,
#   whereas team B's values passed (1) rasteriser interpretation validation (unit square 1.0000 / circle 0.7840 vs theoretical 0.7854)
#   (2) invariance for N=256-2048 and (3) visual inspection of silhouette PNGs [measured - B §6, §12 A3].
#   The triangle counts already matched on all 5 rows (not subject to correction).
#   Magnitude of change: the 3 single leaves were **underestimated by 40-60 %** (maplefall1 +59 %, oakfall1 +60 %),
#   while the 2 clusters were slightly overestimated (-7.0 %, -1.2 %).
#   => The `mean_cov` of `scatter_debris` changes, so **the scatter count changes** (a before/after item outside
#     the material A/B - it applies identically to both arms).
VEG_DEBRIS = [
    ("Debris/fallcluster1.usd", 0.0584, 9175),
    ("Debris/fallcluster2.usd", 0.0239, 2980),
    ("Debris/maplefall1.usd",   0.0081,  631),
    ("Debris/oakfall1.usd",     0.0048,  496),
    ("Debris/oakfall2.usd",     0.0054,  582),
]

# (relative path, representative width [m], **depth from the origin to the bottom [m]**)
#   For Rocks the origin is the *centre* of the rock, so placing it directly at the ground z buries half of it.
#   It must be lifted by z_min to sit properly, and lifted less when deliberate burial is wanted.
# (relative path, native width [m], origin-to-bottom depth [m], triangle count, **native height [m]**)
#   Species real to Korean landscaping. Privet = the standard hedge species; Rhododendron and
#   Juniper = flower-bed shrubs.
#   **Triangles are expensive** (55k-400k each) - use them in the near field only and keep blobs for the far field.
#
# [W2, audit A 6-b] **A 5th field (native height) has been added.** `place_shrubs` was computing the height scale
#   **from the width**, but the measured aspect ratio (height/width) is spread over **0.607-1.973, a factor of 3.2**,
#   so a request of `target_h=0.85` came out **-39 % to +97 %** off
#   (Boxwood at 0.62 m standing next to Juniper at 1.68 m in the same bed) [measured - A §6-b].
#   The docstring of that very function states "shrub height is a scale anchor, so randomisation is +-8 %" while
#   deterministically introducing 12x that error - **a defect that erases a cue axis**.
VEG_SHRUBS = [
    # relative path               width  zmin    triangles  height [measured A §6-b]
    ("Shrub/Privet.usd",        1.704, 0.067, 147000, 1.114),
    ("Shrub/Boxwood.usd",       1.009, 0.019, 178000, 0.741),
    ("Shrub/Juniper.usd",       0.455, 0.013, 200000, 0.898),
    ("Shrub/Rhododendron.usd",  2.547, 0.416,  55000, 2.013),
    ("Shrub/Burning_Bush.usd",  2.642, 0.193, 141000, 1.604),
    ("Shrub/Forsythia.usd",     3.539, 0.007, 404000, 2.317),
    # [W3 K4(b) · S-2] Three rows the spec requires and the library never wired in.
    # All five fields **measured this session** (usd-core 26.8; width = the larger XY
    # extent, zmin = origin-to-bottom, height = z extent, triangles = summed
    # `faceVertexCounts - 2` through instance proxies):
    #   Holly        w 2.378  zmin -0.084  h 1.5262  tri 361,070   (§10.2 quotes 1.44 = its zmax 1.4422)
    #   Yew          w 1.235  zmin -0.013  h 0.7270  tri 144,320   (§10.2 0.71 = zmax 0.7142)
    #   Cedar_Shrub  w 0.288  zmin -0.000  h 0.8763  tri 186,446   (§10.2 0.88 ✓)
    # `Cedar_Shrub` **has no usable extent hint**: `BBoxCache` returns an empty range on
    # its default prim AND on its one child, so its row had to be derived from raw mesh
    # points. Anything else that bbox-caches this asset will silently get garbage.
    ("Shrub/Holly.usd",         2.378, 0.084, 361070, 1.526),
    ("Shrub/Yew.usd",           1.235, 0.013, 144320, 0.727),
    ("Shrub/Cedar_Shrub.usd",   0.288, 0.000, 186446, 0.876),
    # [W3 K-micro · S06-F2 / S09-F1 / S03 §9-7] **The four grass rows the three
    # dead `SHRUB_SPECIES` roles have always named.** `riparian` (Switchgrass),
    # `verge_turf` (Grass_Short_A/B) and `edge_weed` (Grass_Short_C) pointed at
    # assets that are on disk but had **no `VEG_SHRUBS` row**, and `place_shrubs`
    # filters `species=` *and* `pool=` through this table — so all three roles
    # resolved empty and fell back to `SHRUB_ORNAMENT` **silently**. scene06's
    # first render put two Rhododendron beds side by side while the scene printed
    # "grasses 14"; Switchgrass was unreachable from any sanctioned call.
    #   Five fields `[measured — assets/veg_manifest_w2.json, byte-matched to the
    #   files on disk this session: 2457126 / 845898 / 124868 / 1208701 B]`.
    #   width = the larger XY extent · zmin = |origin-to-bottom| · height = the z
    #   extent (zmax + |zmin|), the same convention the Holly/Yew/Cedar rows use.
    #     Grass_Short_A  1.2893x1.2939x0.1618  zmin -0.0228  tri  32,504
    #     Grass_Short_B  0.6615x0.6752x0.1636  zmin -0.0172  tri  11,137
    #     Grass_Short_C  0.2789x0.3044x0.1250  zmin -0.0021  tri   1,598
    #     Switchgrass    2.0090x2.0268x1.3717  zmin -0.0005  tri   8,934
    # **Season pixel-check, the K4-F1 test applied to each** `[measured this
    #   session, PIL over the basecolor PNGs, and cross-read against the
    #   manifest's UV-weighted `foliage_uv_hue`]`: `switchgrass_basecolor.png`
    #   green **1.0000**, red 0.0000, magenta 0.0000; `lawngrass_a_basecolor.png`
    #   (shared by A/B/C) red **0.0003**, magenta **0.0000** — whole-texture
    #   green+yellow-green 0.438 with the balance in dry straw (the manifest's
    #   UV-weighted figures are green 0.535-0.542 + yellow-green 0.281-0.287
    #   = **0.821-0.823 >= the 0.75 turf gate**, which is why these passed
    #   procurement and `Grass_Trimmed_A~C` at 0.72 did not). Neither texture
    #   carries autumn red or bloom magenta, so unlike `Forsythia` /
    #   `Burning_Bush` / `Rhododendron` these four need **no** seasonal strip and
    #   have no `SEASONAL_SUBPRIMS` row.
    # Triangles are cheap here (1.6k-32.5k against 55k-404k for the woody rows),
    # so a turf band is affordable in the near field where a shrub blob is not.
    ("Shrub/Grass_Short_A.usd", 1.294, 0.023,  32504, 0.162),
    ("Shrub/Grass_Short_B.usd", 0.675, 0.017,  11137, 0.164),
    ("Shrub/Grass_Short_C.usd", 0.304, 0.002,   1598, 0.125),
    ("Shrub/Switchgrass.usd",   2.027, 0.001,   8934, 1.372),
]
# A clipped hedge really is box-shaped (it is trimmed). What the blob gets wrong is the
# **untrimmed shrubs of a flower bed** - those are what get replaced with real assets.
SHRUB_HEDGE = ["Shrub/Privet.usd", "Shrub/Boxwood.usd"]
# [W2, audit A P0-2] `Forsythia` and `Burning_Bush` **removed**.
#   The seasonal convention is judged by leaf texture pixels, not species names [measured - B §9]:
#     - `forsythiaflower_basecolor.png` - a blossom-only texture (green 0.0 %). Flowering March-April.
#     - `burningbush_leaf_basecolor.png` - **red 30.2 %** (autumn colour). Fine for C2, but banned in
#       summer and all-season scenes, so it is dropped from the global pool.
#   `Rhododendron` stays **only on the premise that the flower prims are disabled** -
#   **76.7 % of the pixels** of `rhododendron_basecolor.png` **are magenta** (a full-bloom scan), so leaving it as is
#   embeds spring flowering in every scene. `place_shrubs` disables `/Asset/Flowers` (below).
SHRUB_ORNAMENT = ["Shrub/Rhododendron.usd", "Shrub/Juniper.usd"]

# [W3 K4(b) · S-2] **One species per bed / per continuous band.** The rule is the shrub
# half of S-1 and the same evidence carries it: a Korean planting bed is a single species
# clipped to one form, not a mixed border. `place_shrubs` used to draw per point
# (`avail[rnd.randrange(len(avail))]`), so one 3-point bed could hold three species at
# three aspect ratios. The draw is now **per bed**, from the pool, on the bed's own seed.
# Roles are the spec's `[§10.2 S-2]`; `Privet` / `Boxwood` / `Holly` share one leaf
# texture (`hollyprivet_basecolor.png`) and differ only by silhouette and scale, so never
# put two of them side by side expecting a species contrast.
SHRUB_SPECIES = {
    "hedge_evergreen": ["Shrub/Holly.usd", "Shrub/Privet.usd"],   # clipped band
    "planter_accent":  ["Shrub/Yew.usd"],                          # formal planter
    "border_narrow":   ["Shrub/Cedar_Shrub.usd"],                  # narrow border
    "verge_turf":      ["Shrub/Grass_Short_A.usd",                 # turf - mixing allowed
                        "Shrub/Grass_Short_B.usd"],
    "edge_weed":       ["Shrub/Grass_Short_C.usd"],
    "riparian":        ["Shrub/Switchgrass.usd"],
    "ornament_bed":    ["Shrub/Rhododendron.usd"],                 # single-species only
}

# Season-specific prims - disabled with `SetActive(False)` right after referencing. The asset root (`/Root`)
# maps to the referencing prim, so `/Root/Flowers` becomes `{prim}/Asset/Flowers`.
# [measured - `strings assets/vegetation/Shrub/Rhododendron.usd` = Branches, Flowers, Leaves]
SEASONAL_SUBPRIMS = {
    "Shrub/Rhododendron.usd": ("Flowers",),
}

# [W3 K4 micro · spec `s3_scene07_10_rebuild_spec_v1.md` §3.4, ruling §8.R OQ-3]
# **Leaf-off (bare) trees at zero procurement cost.**
#   Every tree in the catalogue is a green-foliage scan - all 10 measured `veg_manifest_w2`
#   tree/shrub rows read green 74-100 %, orange 0.000, red 0.000. There is no leafless, no
#   bare-branch and no winter tree asset anywhere. But three tree USDs split trunk and leaves
#   into **separate sibling meshes under `/Root`, with the whole branch armature living in the
#   trunk mesh**, so deactivating `/Root/leaves` leaves a real bare tree, not a bare pole.
#   [measured this session - usd-core 26.8, `Usd.Stage.Open` + BBoxCache + faceVertexCounts]
#     asset               /Root children        trunk tri   leaves tri   full zmax   trunk zmax
#     Gray_Birch.usd      Looks, trunk, leaves    118,417      138,208     3.3294 m    3.2960 m
#     Elm_Sapling.usd     Looks, trunk, leaves     47,334       65,934     3.0867 m    3.0424 m
#     Lombardy_Poplar.usd Looks, trunk, leaves    101,130      316,776    13.6709 m   13.4221 m
#   The bare form keeps **98.2-99.2 % of the canopy-top height** and costs **24-46 %** of the
#   triangles. `Fraxinus` / `Shumard_Oak` / `Scarlet_Oak` / `Black_Oak` are **deliberately absent**:
#   their leaves ride inside MASH `PointInstancer`s that also carry the branches, so killing an
#   instancer removes the branch with it (verified on `Shumard_Oak` and `Fraxinus` this session).
# **Why this is a separate table and not more rows in `SEASONAL_SUBPRIMS`**: that table is
#   unconditional - it strips its prims in all 33 scenes. Leaf-off is a *scene identity*, not a
#   library-wide season, so it is **opt-in** via `build_tree(..., bare=True)` and is applied
#   nowhere in this commit (33/33 prim-hash identity is the acceptance test of the ruling).
# Scale note for the first consumer: `add_vegetation` scales by `target_h / native_h` and
#   `VEG_TREES` carries the **full** (leafed) zmax, so a bare tree lands 0.8-1.8 % short of the
#   requested height - inside the +-8 % per-instance jitter `build_tree` already applies.
BARE_SUBPRIMS = {
    "Trees/Gray_Birch.usd":      ("leaves",),
    "Trees/Elm_Sapling.usd":     ("leaves",),
    "Trees/Lombardy_Poplar.usd": ("leaves",),
}

# --- Reference-wrapper layers — the ONLY route that survives instancing ------
# [W3 K4(0) · red-team finding **F1** (`redteam_s0710_rebuild.md` §1.2)]
#
# **The bug this replaces.** Both leaf-off (`BARE_SUBPRIMS`) and the unconditional
# season strip (`SEASONAL_SUBPRIMS`) used to be applied by calling `SetActive(False)`
# on `{prim}/Asset/<name>` and then `SetInstanceable(True)` on `{prim}/Asset`.
# Measured on usd-core 26.8 - **USD discards opinions on descendants of an instance,
# regardless of authoring order**:
#     plain reference, leaves deactivated     -> visible meshes ['trunk']            (works)
#     deactivate FIRST, then SetInstanceable  -> visible meshes ['trunk', 'leaves']  (silently undone)
#     SetInstanceable first, deactivate after -> hard error, "authoring to an instance proxy"
# Ordering only converts the loud failure into a silent one. The old code comments
# ("Leaf-off BEFORE instancing... order matters") were wrong **as semantics**, and the
# `n_off` counters they printed counted *authored opinions*, never composed results.
# Blast radius when it was found: scene10's 12 "leaf-off" trees rendered in full green
# leaf, and - the live half nobody had noticed - **every `place_shrubs` bed on the
# default `SHRUB_ORNAMENT` pool rendered a full-bloom magenta `Rhododendron`** in a
# library whose own comment says the species is admissible "only on the premise that
# the flower prims are disabled".
#
# **The route that works** (proven by scene04, commit `024a985`): compose the
# deactivation **inside the prototype** by referencing a thin wrapper layer that
# carries the `over ... (active = false)`. The wrapper composes normally - it is not
# an instance - and the scene then instances the wrapper, so all instances share one
# prototype that never had the sub-prim.
#
# The wrapper files live in `assets/veg_bare/` (deliberately **outside** the gitignored
# `assets/vegetation/` tree: they hold one relative reference and one `over`, no asset
# content, so they are trackable while the geometry stays untracked and procured).
# `_veg_wrapper_write` authors a missing one on demand so a newly registered species
# needs no manual file; the four in use are pre-authored and committed, so the author
# path is a no-op on a clean checkout.
VEG_BARE_DIR = os.path.join(ASSETS_DIR, "veg_bare")

# Bare (leaf-off) `zmax` per species `[measured - usd-core 26.8, K4 micro `1346b70` §1.2]`.
# `add_vegetation` scales by `target_h / native_h`, and `VEG_TREES` carries the **leafed**
# zmax, so a wrapper row must hand its own native height or every bare tree lands 0.8-1.8 %
# tall. (scene04's `TREES04` carries the same three numbers - they agree.)
BARE_NATIVE = {
    "Trees/Gray_Birch.usd":       3.2960,
    "Trees/Elm_Sapling.usd":      3.0424,
    "Trees/Lombardy_Poplar.usd": 13.4221,
}

# suffix per registry, so one species can carry both a bare and a season-off wrapper
WRAP_SUFFIX = {"bare": "_bare", "season": "_noflower"}

_WRAP_CACHE = {}


def _veg_wrapper_write(path, usd_rel, names):
    """Author one wrapper layer as text. Returns True on success.

    Text, not `Usd.Stage.CreateNew`, on purpose: this module is imported by the
    CPU-only invariance harness where `pxr` is a recording stub, and a wrapper must be
    authorable there too. `metersPerUnit` is pinned to the asset convention (0.01,
    measured on all 17 vegetation USDs) - layer units are advisory in USD, so a wrong
    value would not rescale anything, it would only lie to `add_vegetation`'s probe.
    """
    over = "\n".join('    over "%s" (\n        active = false\n    )\n    {\n    }'
                     % nm for nm in names)
    body = ('#usda 1.0\n(\n    """Auto-authored by `scene_common.veg_wrapper_rel` '
            '(W3 K4(0), red-team F1).\n\n'
            '    Deactivates %s INSIDE the prototype, which is the only place the\n'
            '    opinion survives `SetInstanceable(True)`. See `BARE_SUBPRIMS` in\n'
            '    `scene_common.py` for the measurement that forced this route.\n'
            '    """\n    defaultPrim = "Root"\n    metersPerUnit = 0.01\n'
            '    upAxis = "Z"\n)\n\n'
            'def Xform "Root" (\n    prepend references = @../vegetation/%s@\n)\n'
            '{\n%s\n}\n'
            % (" + ".join("/Root/%s" % n for n in names), usd_rel, over))
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as fh:
            fh.write(body)
        return True
    except Exception as e:                     # read-only tree, sandbox, ...
        print(f"[룩v1][경고] 래퍼 레이어 작성 실패 {path}: {e}")
        return False


def veg_wrapper_rel(usd_rel, names, kind="bare"):
    """`add_vegetation`-ready rel path to the wrapper that strips `names`, or None.

    usd_rel: source path relative to `VEG_DIR`, e.g. `Trees/Gray_Birch.usd`
    names  : the sub-prims to deactivate (a `BARE_SUBPRIMS` / `SEASONAL_SUBPRIMS` value)
    kind   : which suffix to use, so bare and season-off wrappers can coexist

    Returns None when there is nothing to strip, when the source asset is absent, or
    when the wrapper could not be authored - **every caller must fall back**, because
    a missing wrapper must never cost a scene its vegetation.
    """
    if not names:
        return None
    key = (usd_rel, kind)
    if key in _WRAP_CACHE:
        return _WRAP_CACHE[key]
    stem = os.path.splitext(os.path.basename(usd_rel))[0]
    fname = stem + WRAP_SUFFIX.get(kind, "_bare") + ".usda"
    path = os.path.join(VEG_BARE_DIR, fname)
    rel = os.path.join("..", "veg_bare", fname)      # relative to VEG_DIR
    ok = os.path.isfile(path)
    if not ok:
        if not os.path.isfile(os.path.join(VEG_DIR, usd_rel)):
            _WRAP_CACHE[key] = None                  # nothing to wrap
            return None
        ok = _veg_wrapper_write(path, usd_rel, names)
    _WRAP_CACHE[key] = rel if ok else None
    return _WRAP_CACHE[key]

VEG_ROCKS = [
    ("Rocks/rock_small_01.usda", 0.314, 0.128),
    ("Rocks/rock_small_08.usda", 0.196, 0.072),
    ("Rocks/rock_small_09.usda", 0.164, 0.061),
    ("Rocks/rock_small_10.usda", 0.128, 0.044),
    ("Rocks/rock_small_15.usda", 0.238, 0.031),
]


def scatter_debris(stage, prefix, x0, y0, x1, y1, z, cover=0.35,
                   pool=None, seed=1234, scale_jitter=(0.75, 1.25),
                   edge_bias=0.0, max_count=400, ground_fn=None,
                   tilt_max=8.0, sink=0.0, mtl=None):
    """[realism v1] Scatter 3D objects over a region - leaves, debris, gravel, rocks.

    cover: **target ground cover fraction 0-1** (not a count). Random scatter overlaps, so the
      required count is back-computed as n = A*(-ln(1-cover)) / (effective area per instance)
      (dividing the area outright while ignoring overlap yields less cover than the target).
      The effective area per instance is measured and stored in VEG_DEBRIS.
    edge_bias: >0 pushes instances towards edges and corners [m]. Real leaves are swept into
      corners by the wind while the walking line stays clear, and a uniform scatter does the
      opposite, which looks unnatural. 0 means uniform.
    ground_fn: (x,y) -> z callback. When given, each instance is seated on the ground and laid
      along the local slope - without it they float in mid-air and lie flat on a slope.
    sink: depth to lower below the ground [m]. For half-buried rocks.
      **Sign**: the asset origin is the object centre, so `sink = 0` is exactly 50 %
      buried; a *negative* sink lifts the instance and buries it less. `scale_mul` is
      authored as a scale op **after** the translate, so `sink` is an absolute metre
      offset and does not follow the instance size - which is why ground_kit computes it
      from a burial *fraction* and the mean scale jitter (`_scatter_pool_kw`).
    mtl: [W2 fix batch F2] optional material bound over the whole instance with
      `strongerThanDescendants`, so it wins against the referenced asset's own binding
      even though `/Asset` is instanceable. Used to bring the procured rock albedo onto
      the project's grey-debris band. `None` keeps the asset's own material.
    seed **must be deterministic** - this project's rule is 100 % deterministic RNG.

    Returns: the number of instances placed.
    """
    pool = pool or VEG_DEBRIS
    avail = [p for p in pool
             if os.path.isfile(os.path.join(VEG_DIR, p[0]))]
    if not avail:
        return 0
    rng = np.random.default_rng(int(seed) & 0x7FFFFFFF)
    w, h = abs(x1 - x0), abs(y1 - y0)
    area = w * h
    cover = max(0.0, min(0.97, float(cover)))
    mean_cov = sum(float(p[1]) for p in avail) / len(avail)
    if area <= 0 or mean_cov <= 0 or cover <= 0:
        return 0
    n = int(round(area * (-math.log(1.0 - cover)) / mean_cov))
    if n > max_count:
        print(f"[룩v1] 산포 상한: {prefix} 목표피복 {cover:.2f} → {n}개 필요, "
              f"{max_count}개로 자름(실제 피복 "
              f"{1.0 - math.exp(-max_count * mean_cov / area):.2f})")
        n = max_count
    if n <= 0:
        return 0
    xa, ya = min(x0, x1), min(y0, y1)
    placed = 0
    for i in range(n):
        px = xa + rng.random() * w
        py = ya + rng.random() * h
        if edge_bias > 1e-6:
            dx = min(px - xa, xa + w - px)
            dy = min(py - ya, ya + h - py)
            if min(dx, dy) > edge_bias and rng.random() > 0.35:
                continue                    # The interior is skipped with 65 % probability
        rel, _cov = avail[int(rng.integers(len(avail)))][:2]
        pz = float(z)
        tilt = (0.0, 0.0)
        if ground_fn is not None:
            try:
                # d must be **smaller than the tread (0.24-0.34 m)**. The old 0.15 gave a
                # half-width approaching half the tread, so 89.5 % of the leaves on a horizontal tread
                # picked up the z of the adjacent step and tilted by 28 deg on average, floating or sinking by 6.6 cm.
                d = 0.04
                pz = float(ground_fn(px, py))
                # Local slope -> lay the instance along the slope
                gx = (float(ground_fn(px + d, py)) - float(ground_fn(px - d, py))) / (2 * d)
                gy = (float(ground_fn(px, py + d)) - float(ground_fn(px, py - d))) / (2 * d)
                # The slope explodes at discontinuities (nosings, curbs), so it is clamped.
                _cl = lambda a: max(-15.0, min(15.0, math.degrees(math.atan(a))))
                tilt = (_cl(gy), -_cl(gx))
            except Exception:
                pass
        j = float(rng.uniform(-tilt_max, tilt_max))
        tilt = (tilt[0] + j, tilt[1] + float(rng.uniform(-tilt_max, tilt_max)))
        try:
            if add_vegetation(stage, f"{prefix}/Deb_{i}", rel,
                              (px, py, pz - float(sink)),
                              yaw_deg=float(rng.uniform(0, 360)),
                              tilt_deg=tilt,
                              scale_mul=float(rng.uniform(*scale_jitter))) is not None:
                # Scatter comes in large numbers, so instancing is essential - share the prototype.
                try:
                    stage.GetPrimAtPath(f"{prefix}/Deb_{i}/Asset").SetInstanceable(True)
                except Exception:
                    pass
                if mtl is not None:
                    # Bound on the Xform *above* `/Asset`; `strongerThanDescendants` is what
                    # makes it beat the prototype's own mesh-level binding (a plain Bind
                    # would lose). Failure is non-fatal - the asset keeps its own look.
                    try:
                        from pxr import UsdShade
                        UsdShade.MaterialBindingAPI.Apply(
                            stage.GetPrimAtPath(f"{prefix}/Deb_{i}")).Bind(
                                mtl, UsdShade.Tokens.strongerThanDescendants)
                    except Exception as e:
                        if i == 0:
                            print(f"[룩v1][경고] 산포 재질 상위 바인딩 실패 {prefix}: {e}")
                placed += 1
        except Exception as e:
            print(f"[룩v1][경고] 산포물 배치 실패 {prefix}/Deb_{i}: {e}")
            break
    if placed:
        LOOK_STATS["debris"] = LOOK_STATS.get("debris", 0) + placed
    return placed


def build_tree(stage, prefix, cx, cy, gz, wood_mtl, canopy_a_mtl, canopy_b_mtl,
               trunk_r=0.09, trunk_h=2.2, stake_r=0.015, stake_h=1.5,
               stake_off=0.5, stakes=False, canopy_blobs=10,
               canopy_spread=1.0, bare=False, species=None, belt=False):
    """[v5.1 realism] Trunk (2-stage taper + slight lean) + canopy (irregular ellipsoid blobs,
    deterministically varied per tree) + 3 stakes (OFF by default). Seeded by a coordinate hash,
    so it is identical on re-running the same scene while each tree differs in form, size and
    lean - removing the 'cloned lollipop' impression.

    [v6 verdict C-4] At distance it clumped into a 'thin trunk + spherical canopy' (lollipop) ->
    satellite blobs 7 -> `canopy_blobs` (10 by default), with a larger scatter radius and vertical
    distribution to break the silhouette. `canopy_spread` allows per-scene fine tuning (1.0 = default).
    [mod6 §1(c)] `trunk_r` default 0.06 -> 0.09 (diameter 18 cm) - corrects an over-slender trunk.
    (Calls that state it explicitly are unaffected.)
    [realism v1] With `NEGOBS_LOOK_GEO=1` and the vegetation assets present, it is replaced by a
    **real tree USD** (the prim set changes, so it belongs to geometry). The signature is unchanged,
    so 30 scenes switch over with no edits. Without the assets it falls back to the procedural
    blobs below (0 regression).

    [W3 K4 micro, **reworked in K4(0) after red-team F1**] `bare=False` - **opt-in leaf-off
    tree**, default OFF. When True and the drawn species is registered in `BARE_SUBPRIMS`,
    the reference target is swapped for that species' **wrapper layer** in
    `assets/veg_bare/`, which carries the `/Root/leaves` deactivation *inside* the
    prototype. The original route - deactivate the descendant, then instance - is
    composition-inert (USD discards opinions on descendants of an instance) and rendered
    trees in full leaf while reporting success; see the `BARE_SUBPRIMS` block for the
    measurement. `BARE_NATIVE` supplies the bare `zmax` so the canopy-top cue is preserved.
    Two limits the caller must know:
      - It is a **silent no-op for an unregistered species**. `build_tree` draws from `VEG_TREES`
        by coordinate hash, and only `Elm_Sapling` of the three bare-capable assets is in that
        pool, so `bare=True` alone yields a *mixed* frame. A scene that needs a uniformly leaf-off
        canopy needs a species selector as well (the planned K4(b) `species=` kwarg), or must
        call `add_vegetation` itself.
      - It is a **no-op on the procedural blob fallback** (assets absent or `LOOK_GEO=0`); the
        blob canopy is not a leaf asset and is left alone.

    [W3 K4(b)] `species=None` / `belt=False` - **the species is a declaration, not a draw.**
    `species` takes a `VEG_SPECIES` key and overrides everything; with `species=None` the
    scene's own row in `SCENE_SPECIES` decides, and `belt=True` asks for that scene's
    backdrop-stand species instead of its route species. Both are appended last with
    inert defaults, so no existing call site changes shape. Note that the +-8 % height
    and the 0-360 deg yaw are still drawn per instance (J-9 is exempt from the jitter
    abolition); what is gone is the species draw.

    Returns: None (prims are created under prefix)."""
    import random as _random
    rnd = _random.Random((int(round(cx * 100)) * 73856093)
                         ^ (int(round(cy * 100)) * 19349663))

    if LOOK_GEO and veg_available():
        # [W3 K4(b) · S-1] **The coordinate-seeded species re-roll is DELETED.** It used
        # to be `pool[rnd.randrange(len(pool))]` over a weighted global pool, which made
        # every Korean street row a five-species botanical garden (see `VEG_SPECIES`).
        # Species is now a per-scene declaration; the RNG keeps its other jobs (yaw,
        # +-8 % height, lean, canopy blobs) - J-9/J-10 are explicitly exempt from the
        # jitter abolition, and this is not a jitter change, it is a species change.
        rel, native = resolve_species(prefix, species=species, belt=belt)
        if not rel:
            return
        # **Tree height is a cue.** Cue family (3) (scale anchors) uses the "absolute height of the canopy top",
        # so randomising it widely erases the very axis that must be learnt.
        # The old uniform(1.45,1.85) was an unfounded magic number (red team finding - accepted).
        # -> A fixed ratio of 1.60 (total height to trunk height) with only +-8 % per-instance variation.
        target = float(trunk_h) * 1.60 * rnd.uniform(0.92, 1.08)
        # [W3 K4(0) · F1 fix] Leaf-off is resolved **before** the reference is made, by
        # swapping the reference target for a wrapper layer that carries the `over`
        # inside the prototype. The old route (reference the source, `SetActive(False)`
        # on the descendant, then instance) is composition-inert - see `BARE_SUBPRIMS`.
        # The wrapper's own bare `zmax` replaces the leafed one so the canopy-top cue
        # stays where the caller asked for it.
        if bare:
            _wrel = veg_wrapper_rel(rel, BARE_SUBPRIMS.get(rel), kind="bare")
            if _wrel:
                native = BARE_NATIVE.get(rel, native)
                rel = _wrel
                LOOK_STATS["bare_tree"] = LOOK_STATS.get("bare_tree", 0) + 1
            else:
                # Silent no-op for an unregistered species is the documented limit of
                # `bare=` (see the docstring); count it so a caller can see the gap.
                LOOK_STATS["bare_miss"] = LOOK_STATS.get("bare_miss", 0) + 1
        try:
            # **Attach to a child path.** Attaching to prefix itself would, as in `build_planter`,
            # apply the scale (about 0.0078) to sibling prims already created under the same prefix
            # (Curb/Cap/Grass) and **shrink the flower bed to 0.8 % of its size**.
            # 12 scenes take this path (found by the red team - a supervisor bug).
            vx = add_vegetation(stage, f"{prefix}/Veg", rel, (cx, cy, gz),
                                yaw_deg=rnd.uniform(0, 360),
                                target_h=target, native_h=native)
            if vx is not None:
                # The same asset is referenced many times, so instancing saves memory and time.
                # (About 30 M extra triangles across the 33 scenes - red team estimate.)
                # Instancing must be set on **the prim that holds the reference**. USD requires
                # "a prim must use at least one composition arc in order to be
                # eligible for instancing", so once the reference was moved down to the /Asset child,
                # leaving the flag on the parent is **silently inert**.
                # (The instancing measure of one commit was neutralised this way by the next, and it is
                #  the kind of regression that cannot in principle be spotted by eye.)
                try:
                    stage.GetPrimAtPath(f"{prefix}/Veg/Asset") \
                        .SetInstanceable(True)
                except Exception:
                    pass
                LOOK_STATS["veg_asset"] = LOOK_STATS.get("veg_asset", 0) + 1
                return
        except Exception as e:
            print(f"[룩v1][경고] 식생 에셋 배치 실패 {prefix}: {e} — 블롭 폴백")
    th = trunk_h * rnd.uniform(0.85, 1.25)
    lean_a = rnd.uniform(0.0, 2 * math.pi)
    lean = rnd.uniform(0.0, 4.0)               # Lean (degrees)
    lx, ly = math.cos(lean_a), math.sin(lean_a)
    # Trunk in 2 stages (taper): lower r -> upper 0.7r, the top offset in the lean direction
    off = th * math.sin(math.radians(lean))
    # [v6 verdict] Sign fix: the rotation consistent with the top offset (+lx) is rotY=+lean*lx,
    #   rotX=-lean*ly (the old signs added the mismatch -> the trunk rendered in two pieces)
    add_cylinder(stage, f"{prefix}/Trunk", (cx, cy, gz + th * 0.35),
                 trunk_r, th * 0.7, wood_mtl,
                 rotX=-lean * ly, rotY=lean * lx)
    add_cylinder(stage, f"{prefix}/TrunkUp",
                 (cx + lx * off * 0.5, cy + ly * off * 0.5, gz + th * 0.78),
                 trunk_r * 0.7, th * 0.55, wood_mtl,
                 rotX=-lean * ly, rotY=lean * lx)
    # Canopy: 1 large central blob + canopy_blobs satellites (random radius, position and flatness, 2 random colours)
    cs = rnd.uniform(0.85, 1.25)               # Overall canopy scale
    sp = float(canopy_spread)
    ccx, ccy = cx + lx * off, cy + ly * off
    czb = gz + th
    # The central blob also gets an axis-ratio jitter (avoids a spherical silhouette)
    add_sphere(stage, f"{prefix}/Canopy_0",
               (ccx, ccy, czb + 0.35 * cs),
               (0.74 * cs * sp * rnd.uniform(0.92, 1.08),
                0.74 * cs * sp * rnd.uniform(0.92, 1.08),
                0.58 * cs * rnd.uniform(0.92, 1.10)),
               canopy_a_mtl if rnd.random() < 0.5 else canopy_b_mtl)
    for i in range(int(canopy_blobs)):
        a = rnd.uniform(0, 2 * math.pi)
        d = rnd.uniform(0.18, 0.68) * cs * sp   # Scatter radius raised (was 0.15-0.55)
        dz = rnd.uniform(-0.05, 0.95) * cs      # Vertical distribution widened (was 0.05-0.85)
        r = rnd.uniform(0.30, 0.58) * cs * sp   # Blob radius raised (was 0.30-0.55)
        mtl = canopy_a_mtl if rnd.random() < 0.5 else canopy_b_mtl
        add_sphere(stage, f"{prefix}/Canopy_{i + 1}",
                   (ccx + d * math.cos(a), ccy + d * math.sin(a), czb + dz),
                   (r, r * rnd.uniform(0.80, 1.0), r * rnd.uniform(0.65, 0.85)),
                   mtl)
    # 3 stakes - [v6 verdict] OFF by default (the "tripod mushroom" impression): only with stakes=True
    if not stakes:
        return
    tilt = 15.0
    for i, a in enumerate((90.0, 210.0, 330.0)):
        rad = math.radians(a)
        bx = cx + stake_off * math.cos(rad)
        by = cy + stake_off * math.sin(rad)
        add_cylinder(stage, f"{prefix}/Stake_{i}",
                     (bx, by, gz + stake_h / 2.0), stake_r, stake_h, wood_mtl,
                     rotY=-tilt * math.cos(rad), rotX=tilt * math.sin(rad))


def build_planter(stage, prefix, cx, cy, base_z, curb_mtl, grass_mtl,
                  tree_mtls=None, size=3.0, curb_h=0.45, curb_t=0.25,
                  cap_over=0.05, cap_h=0.05, grass_h=0.40, species=None,
                  shrubs=True):
    """Flower bed: 4 kerb walls + cap (overhang) + grass top surface (+ an optional tree).
    With tree_mtls=(wood, canopy_a, canopy_b) a tree is placed in the centre. Transplanted from scene01.

    [W3 K-micro · S08-F2] `species=` names a `SHRUB_SPECIES` role and is handed
    straight to `place_shrubs`. Before this the internal call passed `pool=`
    only, so a scene **could not pin the species of its own square beds**:
    scene08's census read 3 species scene-wide although every bed it built was
    monospecific, and K4(b) S-1's one-species-per-bed rule was unreachable
    through this builder. Signature-preserving (K4(c)): a keyword with a default
    of `None`, which is exactly the old behaviour — `place_shrubs` only lets
    `species` win over `pool` when it is truthy.
    """
    S, h, t = size, curb_h, curb_t
    over, gh = cap_over, grass_h
    half = S / 2.0
    top = base_z + h
    walls = [
        ("S", cx, cy - half + t / 2.0, S, t),
        ("N", cx, cy + half - t / 2.0, S, t),
        ("W", cx - half + t / 2.0, cy, t, S - 2 * t),
        ("E", cx + half - t / 2.0, cy, t, S - 2 * t),
    ]
    for tag, wx, wy, sx, sy in walls:
        add_box(stage, f"{prefix}/Curb_{tag}", (wx, wy, base_z + h / 2.0),
                (sx, sy, h), curb_mtl, collider=True)
        add_box(stage, f"{prefix}/Cap_{tag}", (wx, wy, top + cap_h / 2.0),
                (sx + 2 * over if sx < sy else sx,
                 sy + 2 * over if sy <= sx else sy, cap_h), curb_mtl)
    add_box(stage, f"{prefix}/Grass", (cx, cy, base_z + gh / 2.0),
            (S - 2 * t, S - 2 * t, gh), grass_mtl)
    # Bed shrubs - untrimmed bed shrubs are the real body of the "candy floss" problem.
    # (A trimmed hedge being box-shaped is the result of clipping and is actually correct.)
    # If there is a tree, keep the centre clear and seat them towards the corners.
    # [GT-115 ⑧] `shrubs=False` opt-out — sceneN1 reuses this builder for its
    # reflecting pool (grass slab swapped for water) and the unconditional planting
    # put 3 shrubs in open water. Default True = byte-identical everywhere else.
    if LOOK_GEO and shrubs and veg_available():
        inner = S / 2.0 - t - 0.25
        if inner > 0.35:
            r = inner * 0.62
            pts = [(cx + r, cy + r, base_z + gh), (cx - r, cy - r, base_z + gh)]
            if tree_mtls is None:
                pts.append((cx, cy, base_z + gh))
            place_shrubs(stage, f"{prefix}/Shrub", pts,
                         target_h=min(0.85, max(0.45, inner * 0.9)),
                         pool=SHRUB_ORNAMENT, species=species,
                         seed=zlib.crc32(f"{cx:.2f}_{cy:.2f}".encode()))
    if tree_mtls is not None:
        build_tree(stage, prefix, cx, cy, base_z + gh, *tree_mtls)


_FIRE_MTL_CACHE = {}


def _fire_decal_mtl(stage, prefix):
    """Fire entry window marking material - **only one per scene**.
    Creating one per building would give 82 buildings x materials and blow up the material table.
    Red is inviolable constant colour under v5.1 §4, so the name is given as
    `Looks/FkFireSignRed` to exclude it from texture promotion (it matches the sign rule of the
    role classifier).
    """
    root = prefix.split("/Looks")[0].rsplit("/", 2)[0] if "/Looks" in prefix \
        else "/".join(prefix.split("/")[:3])
    key = (id(stage), root)
    m = _FIRE_MTL_CACHE.get(key)
    if m is None:
        m = make_pbr(stage, f"{root}/Looks/FkFireSignRed",
                     diffuse_color=(0.55, 0.045, 0.035),
                     roughness_const=0.55)
        _FIRE_MTL_CACHE[key] = m
    return m


# [GT-115 ⑧] Door width shared by the entrance door and the plinth door gap.
_DOOR_W = 1.8


def build_building(stage, prefix, bd, shell_mtl, glass_mtl, parapet_mtl,
                   window=None):
    """One building. bd dictionary (x0,x1,y0,y1,h,floors,axis,facade_*,face_dir).
    axis="y" -> the facade is a y plane (windows arrayed along x); "x" -> an x plane (windows along y).
    Transplanted from scene01.
    bd["base_z"] (optional, default 0.0): world z of the building plinth - prevents floating in
    scenes whose ground is not at z=0 (h, window and parapet z are relative to base_z).
    Returns: list of created prims.

    [realism v1, composition audit] The old composition was **box + glass quad + parapet** and
    nothing else, so in 24 scenes a "facade billboard" occupied 30-50 % of the upper frame. The
    audit found:
      - 0 entrances, 0 window frames, 0 rooftop structures, 0 downpipes
      - **essentially 0 doors a person could walk through across all 33 scenes** ->
        the direct cause of "there is a stage but nobody lives there"
    Under LOOK_GEO the following 3-tier composition is added (all functionally required, so it
    passes v5.2 §6):
      (1) lower storeys - entrance door (h2.1, doubling as a scale anchor), plinth finish
      (2) typical floors - window sills, floor bands
      (3) rooftop - stair-tower box, guardrail (frees the distant silhouette from a straight lid)
    Downpipes create vertical facade articulation and break the billboard impression.
    """
    if window is None:
        window = dict(w=1.2, h=1.6, inset=0.15, col_step=2.5, margin=2.0)
    wd = window
    base = float(bd.get("base_z", 0.0))
    cx = (bd["x0"] + bd["x1"]) / 2.0
    cy = (bd["y0"] + bd["y1"]) / 2.0
    Lx = bd["x1"] - bd["x0"]
    Ly = bd["y1"] - bd["y0"]
    hh = bd["h"]
    prims = []
    prims.append(add_box(stage, f"{prefix}/Shell",
                         (cx, cy, base + (hh - 1.0) / 2.0),
                         (Lx, Ly, hh + 1.0), shell_mtl, collider=True))
    fstep = hh / bd["floors"]
    ins = float(wd.get("inset", 0.0)) if LOOK_GEO else 0.0
    band_t = min(max(ins, 0.0), 0.15)
    band_h = 0.12
    # -- [T1-10] Window recess - the bug where `window["inset"]` was defined but never read --
    # Previously: the centre of the glass slab (thickness WIN_T=0.03) sat 5 mm outside the facade plane,
    #   so **its outer face was 20 mm proud of the wall** = a glass sheet stuck onto the wall.
    #   A real window is set back from the wall and its reveal casts a shadow line.
    # But **the shell is a solid box** - the facade plane (facade_x/y) is one face of the shell and
    #   everything behind it is filled (verified by AST across all 101 buildings in the scenes, 0 exceptions).
    #   So pushing the glass in by the full inset (=0.15) would bury it inside the shell and
    #   **all the windows of 23 scenes would disappear**. Without opening (reveal) geometry, the
    #   maximum expressible recess is "pull the outer face back to the wall plane", and to avoid
    #   coplanar z-fighting WIN_EPS must remain (the current convention per the scene01 comment:
    #   *"a 0.03 thick panel protruding 2 cm and embedded 1 cm from the facade - avoids coplanar
    #   z-fighting, no boolean needed"*).
    # -> Here it is pulled back only from **20 mm proud to 5 mm**. The remainder (0.135) requires a facade
    #   opening and belongs to the `building_kit` spandrel decomposition (T2).
    # With LOOK_GEO=0, ins=0 -> recess=0 -> the window coordinates are **exactly as before**.
    WIN_T = 0.03                                 # Glass slab thickness (current value)
    WIN_EPS = 0.005                              # Margin avoiding coplanarity with the wall
    recess = max(0.0, min(ins, 0.005 + WIN_T / 2.0 - WIN_EPS))
    axis_y = bd.get("axis", "y") == "y"
    fdir = bd["face_dir"]
    if axis_y:
        gy = bd["facade_y"] + fdir * 0.005
        gy_win = (gy - fdir * recess) if recess > 1e-9 else gy
        usable = Lx - 2 * wd["margin"]
    else:
        gx = bd["facade_x"] + fdir * 0.005
        gx_win = (gx - fdir * recess) if recess > 1e-9 else gx
        usable = Ly - 2 * wd["margin"]
    ncols = max(1, int(usable / wd["col_step"]))

    # -- Window cap -----------------------------------------------------
    # Measured: the 33 scenes hold **4,173 window prims and most of them are off-frame**.
    # At the primary evaluation viewpoint (h0.3, pitch -10 deg, vFOV 36 deg) the top of the frame is only
    # +8.0 deg above the horizon, so the highest visible point at distance d is 0.3 + 0.14*d.
    #   d=20m → 3.1m · d=34m → 5.1m · d=90m → 12.9m
    # In other words even a 34 m apartment facade only puts **5.1 m above ground = 1.7 floors** on screen.
    # 19 % of all prims were spent where they cannot be seen, while the 0-5 m band that fills the
    # frame had nothing but one face of a shell box.
    # -> Windows on invisible floors are not built and that budget is reinvested in the lower storeys.
    nrows = bd["floors"]
    # The **number of window and SillBand prims** changes, so this is geometry (T1 §1.7.1 #21 - one of the 2 v1 enumeration omissions).
    if LOOK_GEO:
        try:
            nrows = fk.window_rows_visible(
                float(bd.get("lod_dist",
                             abs(bd["facade_y"] if axis_y else bd["facade_x"]))),
                fstep, bd["floors"], base_z=base,
                near_dist=20.0, min_rows=2)
        except Exception as e:
            print(f"[룩v1][경고] 창 상한 계산 실패 {prefix}: {e}")
            nrows = bd["floors"]

    # [GT-122] Window reveal frames — near tier only. The shell is a solid box, so
    # a real recess is capped at 15 mm (see the recess note above) and noon facades
    # read as zero-thickness prints. The audit's minimal prescription: 4 frame
    # members per window (2 jambs, head, sill), 30 mm proud of the facade plane —
    # the shadow line and the sill drip seat appear without moving the glass.
    _near_frame = LOOK_GEO and float(
        bd.get("lod_dist",
               abs(bd["facade_y"] if axis_y else bd["facade_x"]))) <= 30.0
    _FW, _FP = 0.06, 0.03           # member width · proudness [derived — audit band]

    def _reveal(f, c, wx, wy, zc):
        hw, hh_ = wd["w"] / 2.0, wd["h"] / 2.0
        if axis_y:
            yb = gy + fdir * _FP / 2.0
            for tag, (bx, bz, sx, sz) in (
                    ("J0", (wx - hw - _FW / 2.0, zc, _FW, wd["h"] + 2 * _FW)),
                    ("J1", (wx + hw + _FW / 2.0, zc, _FW, wd["h"] + 2 * _FW)),
                    ("H", (wx, zc + hh_ + _FW / 2.0, wd["w"], _FW)),
                    ("S", (wx, zc - hh_ - _FW / 2.0, wd["w"], _FW))):
                prims.append(add_box(stage, f"{prefix}/WinFrm_{f}_{c}_{tag}",
                                     (bx, yb, bz), (sx, _FP, sz),
                                     parapet_mtl))
        else:
            xb = gx + fdir * _FP / 2.0
            for tag, (by, bz, sy, sz) in (
                    ("J0", (wy - hw - _FW / 2.0, zc, _FW, wd["h"] + 2 * _FW)),
                    ("J1", (wy + hw + _FW / 2.0, zc, _FW, wd["h"] + 2 * _FW)),
                    ("H", (wy, zc + hh_ + _FW / 2.0, wd["w"], _FW)),
                    ("S", (wy, zc - hh_ - _FW / 2.0, wd["w"], _FW))):
                prims.append(add_box(stage, f"{prefix}/WinFrm_{f}_{c}_{tag}",
                                     (xb, by, bz), (_FP, sy, sz),
                                     parapet_mtl))

    for f in range(nrows):
        zc = base + fstep * f + fstep * 0.5
        if band_t > 1e-4:
            zb = zc - wd["h"] / 2.0 - band_h / 2.0
            if axis_y:
                prims.append(add_box(
                    stage, f"{prefix}/SillBand_{f}",
                    (cx, gy + fdir * band_t / 2.0, zb),
                    (Lx - 0.4, band_t, band_h), parapet_mtl))
            else:
                prims.append(add_box(
                    stage, f"{prefix}/SillBand_{f}",
                    (gx + fdir * band_t / 2.0, cy, zb),
                    (band_t, Ly - 0.4, band_h), parapet_mtl))
        for c in range(ncols):
            if axis_y:
                xc = bd["x0"] + wd["margin"] + (c + 0.5) * (usable / ncols)
                prims.append(add_box(stage, f"{prefix}/Win_{f}_{c}",
                                     (xc, gy_win, zc), (wd["w"], WIN_T, wd["h"]),
                                     glass_mtl))
                if _near_frame:
                    _reveal(f, c, xc, None, zc)
            else:
                yc = bd["y0"] + wd["margin"] + (c + 0.5) * (usable / ncols)
                prims.append(add_box(stage, f"{prefix}/Win_{f}_{c}",
                                     (gx_win, yc, zc), (WIN_T, wd["w"], wd["h"]),
                                     glass_mtl))
                if _near_frame:
                    _reveal(f, c, None, yc, zc)

    # Parapet: Building Act Enforcement Decree §40 requires a rooftop guardrail of **at least 1.2 m**.
    # The old 0.5 fell short of the rule, and the distant silhouette was that much flatter.
    par_h = 1.20 if LOOK_GEO else 0.5
    prims.append(add_box(stage, f"{prefix}/Parapet",
                         (cx, cy, base + hh + par_h / 2.0),
                         (Lx + 0.2, Ly + 0.2, par_h), parapet_mtl))

    # Everything below this is inside the gate - the plinth stone band, AC outdoor units and the whole
    # lower-storey facade kit are new geometry and therefore `LOOK_GEO` (T1 §1.7.1 #23 - the other of the 2 v1 enumeration omissions.
    # Missing this one line makes the lower storeys of buildings disappear **in both A/B arms**).
    if not LOOK_GEO:
        return prims

    # -- (0) Plinth stone band -------------------------------------------
    # **1 prim per building** yet it lands directly on the bottom of the h0.3 frame - the best ROI.
    # The lower storeys of Korean buildings are finished in granite or tile plinths without exception.
    try:
        fac = fk.facade_from_bd(bd)
        K = fk.Kit(add_box, add_cylinder)
        # [GT-115 ⑧] The plinth band used to cross the entrance and cut the door
        # in half at 1.10 m (N1~N4 audit). The gap is the door width + 0.30 jamb
        # margin, on the door facade computed below (DW hoisted to here).
        _dg = (("y", gy, cx, _DOOR_W + 0.30) if axis_y
               else ("x", gx, cy, _DOOR_W + 0.30))
        prims += fk.build_plinth(K, stage, prefix, bd["x0"], bd["x1"],
                                 bd["y0"], bd["y1"], base, parapet_mtl,
                                 height=1.10, door_gap=_dg)
        # AC outdoor units - the **strongest Korean identification cue** named by the survey, and their
        # mounting height of 1.5-2.6 m is straight ahead at the robot viewpoint.
        prims += fk.build_aircon_units(K, stage, prefix, fac,
                                       parapet_mtl, parapet_mtl,
                                       mode="eaves", count=4,
                                       seed=zlib.crc32(prefix.encode()))
        # Fire entry window red inverted triangle - statutorily mandatory on floors 2-11, so present 100 % of the time,
        # and **a thin quad, so effectively free in prims**. The cheapest Korean signal.
        lv = fk.floor_levels(bd["floors"], fstep, base_z=base)
        prims += fk.build_fire_access_marks(stage, prefix, fac, lv,
                                            _fire_decal_mtl(stage, prefix),
                                            max_floors=nrows)
    except Exception as e:
        print(f"[룩v1][경고] 파사드 저층부 실패 {prefix}: {e}")

    # -- (1) Lower storeys: entrance door ---------------------------------
    # The 2.1 m door height doubles as a **scale anchor**. The composition audit's central point was that
    # in a library with 0 people and 0 vehicles there is almost no cue for reading absolute size.
    DW, DH = _DOOR_W, 2.1
    if axis_y:
        prims.append(add_box(stage, f"{prefix}/Door",
                             (cx, gy + fdir * 0.02, base + DH / 2.0),
                             (DW, 0.06, DH), glass_mtl))
        prims.append(add_box(stage, f"{prefix}/DoorHead",
                             (cx, gy + fdir * 0.10, base + DH + 0.12),
                             (DW + 0.5, 0.22, 0.24), parapet_mtl))
    else:
        prims.append(add_box(stage, f"{prefix}/Door",
                             (gx + fdir * 0.02, cy, base + DH / 2.0),
                             (0.06, DW, DH), glass_mtl))
        prims.append(add_box(stage, f"{prefix}/DoorHead",
                             (gx + fdir * 0.10, cy, base + DH + 0.12),
                             (0.22, DW + 0.5, 0.24), parapet_mtl))

    # -- (2) Downpipe - vertical facade articulation ----------------------
    # The cheapest way to break the billboard impression. Present on Korean buildings without exception.
    span = Lx if axis_y else Ly
    ndp = max(2, int(span / 12.0) + 1)
    for i in range(ndp):
        t = (i + 0.5) / ndp
        if axis_y:
            px = bd["x0"] + t * Lx
            prims.append(add_cylinder(stage, f"{prefix}/Downpipe_{i}",
                                      (px, gy + fdir * 0.09, base + hh / 2.0),
                                      0.055, hh, parapet_mtl))
        else:
            py = bd["y0"] + t * Ly
            prims.append(add_cylinder(stage, f"{prefix}/Downpipe_{i}",
                                      (gx + fdir * 0.09, py, base + hh / 2.0),
                                      0.055, hh, parapet_mtl))

    # -- (3) Rooftop - stair tower + water tank stand ---------------------
    # The distant silhouette escapes being "a box with a white lid". The basic composition of a Korean rooftop.
    ph_w = min(4.2, Lx * 0.34)
    ph_d = min(3.4, Ly * 0.34)
    if ph_w > 1.2 and ph_d > 1.2:
        ph_h = 2.6
        ox = cx - Lx * 0.18
        oy = cy + Ly * 0.12
        prims.append(add_box(stage, f"{prefix}/Penthouse",
                             (ox, oy, base + hh + 0.5 + ph_h / 2.0),
                             (ph_w, ph_d, ph_h), shell_mtl))
        prims.append(add_box(stage, f"{prefix}/PenthouseCap",
                             (ox, oy, base + hh + 0.5 + ph_h + 0.09),
                             (ph_w + 0.24, ph_d + 0.24, 0.18), parapet_mtl))
    return prims


def place_shrubs(stage, prefix, pts, target_h, pool=None, seed=1234,
                 overlap=0.0, tag="Sh", species=None):
    """[realism v1] Stand real shrub USDs at the given coordinates.

    pts: [(x, y, z_ground), ...]
    target_h: target height [m]. **Randomisation is bounded to +-8 %** - shrub height is a scale
      anchor, so shaking it hard erases the cue (preventing a repeat of the tree-height magic
      number incident).
    overlap: >0 means the caller has computed a width-based placement so that neighbours overlap,
      and only the size is increased. For hedges.
    Returns: the number placed.
    """
    if not (LOOK_GEO and veg_available()):
        return 0
    names = pool or SHRUB_ORNAMENT
    avail = [s for s in VEG_SHRUBS
             if s[0] in names and os.path.isfile(os.path.join(VEG_DIR, s[0]))]
    if not avail:
        # [W3 K-micro · S06-F2] Loud, not silent. A `pool=` that resolves to
        # nothing used to return 0 without a word, so a bed simply did not exist
        # and the scene's own census printed the number it asked for.
        if pool:
            print(f"[관목][경고] pool 이 VEG_SHRUBS 에서 0종으로 해석됐다 — "
                  f"{prefix} 는 비어 있다 · 요청 {list(names)}")
            LOOK_STATS["shrub_pool_miss"] = \
                LOOK_STATS.get("shrub_pool_miss", 0) + 1
        return 0
    import random as _random
    rnd = _random.Random(int(seed) & 0x7FFFFFFF)
    # [W3 K4(b) · S-2] **One species per bed.** The per-point `randrange` is deleted: it
    # is drawn ONCE here, off the bed's own seed, so a bed is monospecific and stays
    # deterministic per scene. `species=` names a `SHRUB_SPECIES` role and wins over
    # `pool=`; a role whose members are all absent falls back to `pool`/`avail` rather
    # than emptying the bed.
    if species:
        want = SHRUB_SPECIES.get(species, [])
        role = [s for s in VEG_SHRUBS if s[0] in want
                and os.path.isfile(os.path.join(VEG_DIR, s[0]))]
        if role:
            avail = role
        else:
            # [W3 K-micro · S06-F2 / S09-F1] **The fallback is now loud.** This is
            # the branch that made three roles inert for a whole wave: the bed came
            # back with a healthy count of the *wrong* species and nothing said so.
            # The fallback itself is kept (an empty bed is worse than a substituted
            # one mid-render), but it now names the role, the reason and the pool
            # it actually drew from, and it is counted so a round can be audited
            # from the log alone.
            why = ("역할 미등록" if species not in SHRUB_SPECIES
                   else ("VEG_SHRUBS 행 없음/디스크 부재: "
                         + ", ".join(w for w in want
                                     if not any(s[0] == w for s in VEG_SHRUBS))
                         or "디스크 부재"))
            print(f"[관목][경고] species='{species}' 해석 실패({why}) — "
                  f"{prefix} 는 대신 {[s[0] for s in avail]} 로 채워진다")
            LOOK_STATS["shrub_species_miss"] = \
                LOOK_STATS.get("shrub_species_miss", 0) + 1
    bed = avail[rnd.randrange(len(avail))]
    placed = 0
    for i, (px, py, pz) in enumerate(pts):
        rel, nat_w, zmin, _tri, nat_h = bed
        # [W2, audit A 6-b fix] **The height scale is based on the native 'height'.**
        # It used to be based on width ("shrubs are roughly as wide as they are tall" [estimate]), and the measured
        # aspect ratios spread over 0.607-1.973 gave -39 % to +97 % error against the requested height.
        # `overlap` is an argument meant to create **overlap in the width direction**, so after moving to a
        # height basis it is applied with the same factor to preserve the previous hedge density.
        s = (float(target_h) * (1.0 + overlap) / max(nat_h, 1e-6)
             * rnd.uniform(0.92, 1.08))
        # [W3 K4(0) · F1 fix, shrub half] Resolve the season strip **before** referencing.
        # This is the branch that was actually live: the default `SHRUB_ORNAMENT` pool
        # carries `Rhododendron`, whose `/Root/Flowers` strip has been inert under
        # instancing in every `build_planter` bed since realism-v1 - a 76.7 %-magenta
        # full-bloom scan rendering in a library that declares itself season-neutral.
        # Scale is deliberately still driven by the **flowered** `VEG_SHRUBS` row: those
        # numbers are what every existing bed was authored against, and the strip is
        # dressing, so the fix must not also move shrub heights.
        rel_ref = veg_wrapper_rel(rel, SEASONAL_SUBPRIMS.get(rel),
                                  kind="season") or rel
        try:
            # zmin is a native dimension and must be scaled by the same factor for the bottom to sit on the ground.
            # Forgetting this buries 41 cm of Rhododendron (zmin -0.416) underground.
            xf = add_vegetation(stage, f"{prefix}/{tag}_{i}", rel_ref,
                                (px, py, float(pz) + zmin * s),
                                yaw_deg=rnd.uniform(0, 360),
                                scale_mul=s)
            if xf is not None:
                if rel_ref is rel:
                    # No wrapper was available (species has no seasonal prims, or the
                    # layer could not be authored). Keep the legacy stage-side strip as
                    # the fallback: it is a genuine no-op under instancing, but it is
                    # correct for any future NON-instanced consumer and costs nothing.
                    _deactivate_seasonal(stage, f"{prefix}/{tag}_{i}/Asset", rel)
                try:
                    stage.GetPrimAtPath(f"{prefix}/{tag}_{i}/Asset").SetInstanceable(True)
                except Exception:
                    pass
                placed += 1
        except Exception as e:
            print(f"[룩v1][경고] 관목 배치 실패 {prefix}/{tag}_{i}: {e}")
            break
    if placed:
        LOOK_STATS["shrub"] = LOOK_STATS.get("shrub", 0) + placed
    return placed


def build_hedge(stage, prefix, x0, y0, x1, y1, h, mtl=None, base_z=0.0,
                scale_m=1.2, tint=(0.35, 0.45, 0.28), rounded=True,
                crown_max=48, bulge=1.03):
    """Hedge or pampas grass band. With mtl=None it is created internally from the grass texture with a
    dark green tint (0.35,0.45,0.28) at scale 1.2.

    [v6 verdict C-5] A single cuboid renders as a 'haystack / mud brick box' (12 pampas grass,
    13 hedge). With rounded=True (the default) the body box is lowered to h*0.72 and a row of
    flattened ellipsoids (crown blobs) is overlaid on top to round and roughen the top.
      - The body box path is `prefix/Box` (collider retained) - compatible with existing references and signatures.
      - The crown is seeded by a coordinate hash, so it is identical on re-running and the relief differs per band.
      - Blob size ~= the canopy height. For a wide band (e.g. a pampas grass band) they are staggered
        over 2-3 rows in the short direction (`Crown_{row}_{i}`) to avoid a horizontal sausage look.
      - Top z ~= base_z+h (+-6 % relief per blob), with side protrusion <=5 cm on the long side and
        <= 0.1x the row width on the short side - no floating misread even on a wall top or opening edge.
    With rounded=False, or when h or the length is tiny, the old behaviour (a single box) is kept.
    Returns: the Cube prim (the body) - unchanged from before."""
    import random as _random
    if mtl is None:
        mtl = make_pbr(stage, prefix + "/HedgeMtl", tex_path("grass", "diff"),
                       tex_path("grass", "nor"), tex_path("grass", "rough"),
                       scale_m, tint=tint)
    cx = (x0 + x1) / 2.0
    cy = (y0 + y1) / 2.0
    sx, sy = abs(x1 - x0), abs(y1 - y0)
    L, W = max(sx, sy), min(sx, sy)          # Long and short sides
    if (not rounded) or h <= 0.06 or L <= 0.05 or W <= 1e-6:
        return add_box(stage, prefix + "/Box", (cx, cy, base_z + h / 2.0),
                       (sx, sy, h), mtl, collider=True)

    body_h = h * 0.72                        # Body (the blobs take care of the 0.28h of top rounding)
    box = add_box(stage, prefix + "/Box", (cx, cy, base_z + body_h / 2.0),
                  (sx, sy, body_h), mtl, collider=True)
    rnd = _random.Random((int(round(cx * 100)) * 73856093)
                         ^ (int(round(cy * 100)) * 19349663)
                         ^ (int(round(L * 100)) * 83492791))
    # Blob size ~= the canopy height (or the width if narrow) - a long band is filled by count, a wide one by rows
    pitch0 = max(0.30, min(W, h * 1.2)) * 0.9
    n = max(2, min(crown_max, int(round(L / max(pitch0, 1e-3)))))
    pitch = L / n
    rows = max(1, min(3, int(round(W / max(pitch, 1e-3)))))
    row_w = W / rows
    along_x = sx >= sy
    t0 = (cx - L / 2.0) if along_x else (cy - L / 2.0)
    u0 = (cy - W / 2.0) if along_x else (cx - W / 2.0)   # Origin in the short direction
    for j in range(rows):
        for i in range(n):
            rz = h * rnd.uniform(0.26, 0.34)      # Apex ~= base_z + h (+-6 %)
            rl = pitch * rnd.uniform(0.56, 0.70)  # Long-side radius (so neighbours overlap)
            rw = (row_w / 2.0) * bulge * rnd.uniform(0.94, 1.06)
            # Long-side end protrusion clamped to <=5 cm (avoids a floating misread on wall tops and edges)
            t = min(max(t0 + (i + 0.5) * pitch + (0.5 * pitch if j % 2 else 0.0),
                        t0 + rl - 0.05), t0 + L - rl + 0.05)
            u = u0 + (j + 0.5) * row_w + rnd.uniform(-0.05, 0.05) * row_w
            bx, by = (t, u) if along_x else (u, t)
            add_sphere(stage, f"{prefix}/Crown_{j}_{i}",
                       (bx, by, base_z + body_h),
                       (rl if along_x else rw, rw if along_x else rl, rz), mtl)
    return box


def place_hedge_row(stage, prefix, x0, y0, x1, y1, h, seed,
                    pool=None, base_z=0.0, pitch_frac=0.53, overlap=0.10,
                    end_margin=0.50, jit_along=0.06, jit_across=0.04,
                    fallback_mtl=None, fallback_tint=(0.35, 0.45, 0.28)):
    """[GT-63] A clipped hedge band as a fused row of real shrub USDs.

    Drop-in successor to `build_hedge` for FOREGROUND clipped bands only — the
    box+crown-blob idiom stays for distant masses (FarHedge / RidgeCrest /
    BackHedge / BgHedge / Overhang / TreeLine families), where it is the
    intended cheap silhouette (v6 C-5). Pattern established by GT-62 on
    scene13: the user's verdict was that the blob surface, not the trimmed
    band form, is what fails to read as a bush (§4-1 keeps the form).

    The band rect and the legacy band height `h` keep their old meaning:
    place_shrubs scales by (1+overlap), so target_h = h/(1+overlap) lands the
    exposed height back on ~h. Pitch = scaled shrub width × pitch_frac
    (default 0.53) so neighbours always fuse into one continuous clipped band,
    never discrete balls. Long axis is auto-detected; `seed` should come from
    the scene's det_seed(...) so beds stay deterministic per band.

    Falls back to the legacy `build_hedge` under the same prim root when the
    assets are absent or LOOK_GEO=0 — a missing asset degrades, it never
    empties the verge (scene03 03-D). Returns shrubs placed (0 = fallback).
    """
    import random as _random
    names = list(pool or SHRUB_HEDGE[:1])   # default single species: Privet
    row = next((s for s in VEG_SHRUBS if s[0] in names), None)
    placed = 0
    if row is not None:
        _rel, nat_w, _zmin, _tri, nat_h = row
        target_h = float(h) / (1.0 + overlap)
        pitch = max(0.30, (nat_w / max(nat_h, 1e-6)) * float(h) * pitch_frac)
        sx, sy = abs(x1 - x0), abs(y1 - y0)
        along_x = sx >= sy
        L = max(sx, sy)
        m = min(float(end_margin), L / 4.0)
        span = max(L - 2.0 * m, 1e-6)
        n = max(2, int(math.ceil(span / pitch)) + 1)
        step = span / (n - 1)
        jr = _random.Random((int(seed) & 0x7FFFFFFF) ^ 0x1E0B63)
        t0 = (min(x0, x1) if along_x else min(y0, y1)) + m
        u_c = ((y0 + y1) / 2.0) if along_x else ((x0 + x1) / 2.0)
        pts = []
        for k in range(n):
            t = t0 + k * step + jr.uniform(-jit_along, jit_along)
            u = u_c + jr.uniform(-jit_across, jit_across)
            pts.append((t, u, float(base_z)) if along_x
                       else (u, t, float(base_z)))
        placed = place_shrubs(stage, prefix, pts, target_h, pool=names,
                              seed=seed, overlap=overlap)
    if not placed:
        build_hedge(stage, prefix, x0, y0, x1, y1, h, mtl=fallback_mtl,
                    base_z=base_z, tint=fallback_tint)
    return placed


def build_bench(stage, prefix, cx, cy, base_z, mtl, length=1.8, width=0.4,
                height=0.45, yaw=0.0):
    """A backless bench (seat + 4 legs). Default 1.8 x 0.4 x h0.45, weathered_planks.
    Rotated on placement by yaw (degrees). Children are in the parent Xform local frame. Returns: the root Xform prim."""
    from pxr import UsdGeom, Gf
    root = UsdGeom.Xform.Define(stage, prefix)
    xf = UsdGeom.Xformable(root)
    xf.AddTranslateOp().Set(Gf.Vec3d(float(cx), float(cy), float(base_z)))
    if abs(yaw) > 1e-9:
        xf.AddRotateZOp().Set(float(yaw))
    seat_t = 0.06
    add_box(stage, prefix + "/Seat", (0.0, 0.0, height - seat_t / 2.0),
            (length, width, seat_t), mtl, collider=True)
    lx = length / 2.0 - 0.08
    ly = width / 2.0 - 0.06
    legh = height - seat_t
    for sx, sy, tag in ((lx, ly, "PP"), (lx, -ly, "PN"),
                        (-lx, ly, "NP"), (-lx, -ly, "NN")):
        add_box(stage, prefix + f"/Leg_{tag}", (sx, sy, legh / 2.0),
                (0.06, 0.06, legh), mtl)
    return root


def build_bollard(stage, path, cx, cy, base_z, mtl=None, radius=0.06,
                  height=0.75):
    """Bollard r0.06 h0.75, stainless. With mtl=None it is created internally. Returns: the Cylinder prim."""
    if mtl is None:
        mtl = make_pbr(stage, path + "/Mtl", diffuse_color=(0.80, 0.82, 0.85),
                       metallic=0.9, roughness_const=0.35)
    return add_cylinder(stage, path, (cx, cy, base_z + height / 2.0),
                        radius, height, mtl, collider=True)


# ===========================================================================
# [6] Lighting - noon HDRI lookfix + DomeLight + auxiliary sun (as in scene01)
# ===========================================================================
def build_sign(stage, prefix, cx, cy, base_z, yaw_deg, panel_mtl,
               w=0.8, h=0.8, panel_z=None, pole_h=2.2, pole_r=0.04,
               pole_mtl=None, back_mtl=None):
    """[v5 common layer] Korean sign: 1 post + an st-UV quad panel (+ a thin backing plate).
      panel_mtl should be created with make_pbr(tex_path("sign_*","diff"), uv_mode=True).
      yaw_deg: panel normal bearing (0 = facing +X). panel_z: panel centre z
      (default = base_z + pole_h - h/2 - 0.05, hung at the top of the post).
    Returns: list of created prims."""
    from pxr import UsdGeom, Gf, Sdf
    prims = []
    if panel_z is None:
        panel_z = base_z + pole_h - h / 2.0 - 0.05
    # Post
    prims.append(add_cylinder(stage, f"{prefix}/Pole",
                              (cx, cy, base_z + pole_h / 2.0),
                              pole_r, pole_h,
                              pole_mtl if pole_mtl is not None else back_mtl))
    # Panel quad (direct world coordinates - tangent t = the left of the normal)
    a = math.radians(yaw_deg)
    nx, ny = math.cos(a), math.sin(a)
    tx, ty = -ny, nx
    off = pole_r + 0.015                       # Slightly proud of the front of the post
    cxp, cyp = cx + nx * off, cy + ny * off
    pts = [Gf.Vec3f(cxp - tx * w / 2, cyp - ty * w / 2, panel_z - h / 2),
           Gf.Vec3f(cxp + tx * w / 2, cyp + ty * w / 2, panel_z - h / 2),
           Gf.Vec3f(cxp + tx * w / 2, cyp + ty * w / 2, panel_z + h / 2),
           Gf.Vec3f(cxp - tx * w / 2, cyp - ty * w / 2, panel_z + h / 2)]
    mesh = UsdGeom.Mesh.Define(stage, f"{prefix}/Panel")
    mesh.CreatePointsAttr(pts)
    mesh.CreateFaceVertexCountsAttr([4])
    mesh.CreateFaceVertexIndicesAttr([0, 1, 2, 3])
    # [realism P1] Not authoring subdivisionScheme means the USD default catmullClark. The
    # Catmull-Clark limit surface of a quad pulls the corner vertices inward, so the panel shrinks
    # and the st(0..1) alignment breaks. It is currently latent because refinementLevel defaults to 0,
    # but the moment that setting changes every sign goes out of alignment. Pinned by authoring it explicitly.
    # (scene09 and sceneN3 already authored "none" for the same reason.)
    mesh.CreateSubdivisionSchemeAttr("none")
    mesh.CreateDoubleSidedAttr(True)
    pv = UsdGeom.PrimvarsAPI(mesh.GetPrim()).CreatePrimvar(
        "st", Sdf.ValueTypeNames.TexCoord2fArray, UsdGeom.Tokens.vertex)
    pv.Set([Gf.Vec2f(0, 0), Gf.Vec2f(1, 0), Gf.Vec2f(1, 1), Gf.Vec2f(0, 1)])
    if panel_mtl is not None:
        _bind_mtl(mesh.GetPrim(), panel_mtl)
    prims.append(mesh.GetPrim())
    # Backing plate (hides mirrored text on the back) - a box with the same yaw as the panel
    if back_mtl is not None:
        prims.append(_oriented_box(stage, f"{prefix}/Back",
                                   (cxp - nx * 0.013, cyp - ny * 0.013,
                                    panel_z),
                                   (0.022, w + 0.01, h + 0.01),
                                   back_mtl, rotz=yaw_deg))
    return prims


_SUN_CAP_DEG_DEFAULT = 0.6       # see ensure_noon_lookfix; env-overridable


def ensure_noon_lookfix(src_path):
    """Create/cache the noon HDRI derivative (_lookfix.exr) - transplanted unchanged from scene01.

    (1) Cap the sun disc (angular radius 1.5 deg) at the p90 luminance of the circumsolar ring
       (1.5-2.5 deg): removes the ultra-soft cast shadow produced by the sun blur of RTX dome
       sampling. The removed direct component is replaced by a DistantLight (0.53 deg) aligned
       with the HDRI sun direction.
    (2) Lift the -18 deg to 0 deg band below the horizon to the luminance of the adjacent sky
       (elev 0.5-3.5 deg).
    On failure (e.g. cv2 missing) the original path is returned (with a warning only)."""
    # Solar cap angular radius. The true solar radius is 0.27 deg; clamping a
    # full 1.5 deg leaves a visible "cut disc" (a 3 deg uniform patch with a
    # rim) on cloudy skies. sky_procurement recommendation A: 0.6 deg, which
    # preserves 98.3~99.3 % of the removed direct energy, so the DistantLight
    # needs no retuning. [W2] Default moved 1.5 -> 0.6 per
    # `lighting_camera_variation_spec_v1.md` §7 item 3, which requires the
    # change to ride along in the W2 round so one regression pass covers it.
    # `NEGOBS_SUN_CAP_DEG=1.5` restores the previous look exactly.
    cap_deg = float(os.environ.get("NEGOBS_SUN_CAP_DEG",
                                   str(_SUN_CAP_DEG_DEFAULT)))
    # The cap radius MUST be part of the cache key. It was not, so setting the
    # env var used to return the 1.5 deg derivative that was already on disk —
    # the knob existed and did nothing. Legacy name is kept for 1.5 so the
    # already-generated `*_lookfix.exr` files stay valid.
    suffix = "_lookfix.exr" if abs(cap_deg - 1.5) < 1e-9 \
        else f"_lookfix_cap{cap_deg:g}.exr"
    out_path = src_path[:-4] + suffix
    try:
        if (os.path.isfile(out_path)
                and os.path.getmtime(out_path) >= os.path.getmtime(src_path)):
            return out_path
        os.environ.setdefault("OPENCV_IO_ENABLE_OPENEXR", "1")
        import cv2
        # [realism v1, bug fix] **Error handling 4-channel (RGBA) EXR.**
        # The old `[..., ::-1]` reverses BGRA into [A,R,G,B] -> the alpha lands in the R
        # slot and the subsequent horizon lift raises a broadcast exception, which the except
        # swallows before **returning the original path**. The sun cap is then never applied while
        # a DistantLight is still added, giving **two suns** (all the more dangerous for being silent).
        # The existing qwantani is 3-channel so it stayed latent, and overcast is bypassed with
        # lookfix=False. Most of the PolyHaven puresky family are RGBA.
        rgb = cv2.imread(src_path, cv2.IMREAD_UNCHANGED)[..., :3][..., ::-1]
        rgb = rgb.astype(np.float64)
        h, w = rgb.shape[:2]
        lum = (0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1]
               + 0.0722 * rgb[..., 2])
        iy, ix = np.unravel_index(np.argmax(lum), lum.shape)
        vv = (np.arange(h) + 0.5) / h
        th = np.pi * vv
        ph = 2.0 * np.pi * (np.arange(w) + 0.5) / w
        st, ct = np.sin(th)[:, None], np.cos(th)[:, None]
        dx = st * np.cos(ph)[None, :]
        dy = st * np.sin(ph)[None, :]
        dz = np.broadcast_to(ct, (h, w))
        s = np.array([dx[iy, ix], dy[iy, ix], dz[iy, ix]])
        ang = np.degrees(np.arccos(
            np.clip(dx * s[0] + dy * s[1] + dz * s[2], -1.0, 1.0)))
        ring = (ang > cap_deg) & (ang < cap_deg + 1.0)
        cap = np.percentile(lum[ring], 90)
        mask = (ang < cap_deg) & (lum > cap)
        scl = np.ones_like(lum)
        scl[mask] = cap / lum[mask]
        out = rgb * scl[..., None]
        elev = 90.0 - 180.0 * vv
        ref = out[(elev > 0.5) & (elev < 3.5)].mean(axis=0)      # (w, 3)
        k = np.ones(129) / 129.0
        ref = np.stack(
            [np.convolve(np.r_[ref[-64:, c], ref[:, c], ref[:64, c]],
                         k, mode="same")[64:-64] for c in range(3)], axis=-1)
        t = np.clip((elev + 24.0) / 6.0, 0.0, 1.0) * (elev < 0.0)
        lift = np.maximum(out, ref[None, :, :])
        out += (lift - out) * t[:, None, None]
        cv2.imwrite(out_path, out[..., ::-1].astype(np.float32),
                    [cv2.IMWRITE_EXR_TYPE, cv2.IMWRITE_EXR_TYPE_HALF,
                     cv2.IMWRITE_EXR_COMPRESSION, cv2.IMWRITE_EXR_COMPRESSION_ZIP])
        print(f"[HDRI] noon lookfix 생성 (태양 캡 {int(mask.sum())}px, "
              f"cap L={cap:.2f}): {out_path}")
        return out_path
    except Exception as e:                       # pragma: no cover
        print(f"[HDRI][경고] lookfix 생성 실패({e}) — 원본 사용")
        return src_path


class LightingControl:
    """The callback `setup_lighting` returns — a callable that is also an object.

    Calling it is exactly the old `apply_dome_rot(user_off)`, so all 33 scene
    files keep working unchanged (`apply_dome_rot = sc.setup_lighting(...)` then
    `apply_dome_rot(off)`). Spec §6.3 asked for a second returned callback
    `apply_light_cond`; returning a tuple instead would have broken every scene
    file, and "no structural change to 33 scenes for one feature" is worth more
    than matching the sketch literally. `.apply_cond()` is that callback.

    Why the condition switch has to live here at all: putting lighting on the
    process boundary multiplies `t_boot` by `N_light`. SP-4 measured a runtime
    HDRI swap at **t_swap = 1.4 s** against a 30 s split threshold, and SP-2
    measured the end-to-end saving of keeping the loop inside one boot at
    **3.29x** (693 cuts: 44.2 min in-process vs 145.2 min as 7 rounds).
    """

    def __init__(self, dome, sun, rot_op, sun_rz, sun_rx, tex_attr,
                 light_params, sun_az_offset, scene_key=None):
        self._dome, self._sun = dome, sun
        self._rot_op, self._sun_rz, self._sun_rx = rot_op, sun_rz, sun_rx
        self._tex = tex_attr
        self.lp = dict(light_params)
        self.sun_az_offset = float(sun_az_offset)
        self.scene_key = scene_key
        self.user_off = 0.0
        self.cond_id = "L0"
        self._base = dict(
            hdri=light_params.get("hdri", DEFAULT_HDRI),
            dome_intensity=float(light_params["dome_intensity"]),
            sun_intensity=float(light_params["noon_sun_intensity"]),
            sun_elev=float(light_params["noon_sun_elev"]),
            rotz=float(light_params["hdri_sun_rotz_offset"]),
            lookfix=bool(light_params.get("lookfix", True)),
            sun_enable=bool(light_params.get("noon_sun_enable", True)),
        )

    # -- the legacy interface, byte-for-byte ------------------------------
    def __call__(self, user_off):
        """Dome rotation = noon_dome_rot + sun_az_offset (scene) + [ ] key offset."""
        self.user_off = float(user_off)
        rot = (float(self.lp["noon_dome_rot"]) + self.sun_az_offset
               + self.user_off)
        self._rot_op.Set(rot)
        self._sun_rz.Set(rot + float(self.lp["hdri_sun_rotz_offset"]))
        return rot

    apply_dome_rot = __call__

    # -- the condition switch (role=data) --------------------------------
    def apply_cond(self, cond, exposure=True):
        """Swap sky, intensities, sun elevation, sun angle and exposure in one go.

        A scene-specific lighting tuning always wins (spec §4.3): sceneC1 snow
        800/420, sceneC4 wet 1150/600, sceneD4 indoor 8.0/0 are hand-balanced and
        the catalogue must not overwrite them. What the catalogue still applies to
        those scenes is the RELATIVE change - the condition's illuminance ratio
        against the reference - so a snow scene under overcast still gets darker
        without losing its own balance.
        """
        vk = _variation()
        c = vk.CONDITIONS[cond] if isinstance(cond, str) else cond
        self.cond_id = c["id"]
        override = (self.scene_key in vk.SCENE_LIGHT_OVERRIDE_WINS)

        # --- sky ---------------------------------------------------------
        path = os.path.join(ASSETS_DIR, c["hdri"])
        if c["lookfix"]:
            # MUST be pre-generated: the first call per new sky costs 1.97-2.00 s
            # of CPU and writes an 18 MB derivative (SP-4 §3.2). Inside a data run
            # that shows up as a silent stall on the first cut of each condition.
            path = ensure_noon_lookfix(path)
        self._tex.Set(path)
        self._dome.GetIntensityAttr().Set(
            float(self._base["dome_intensity"] * c["dome_intensity"] / 1000.0)
            if override else float(c["dome_intensity"]))

        # --- sun ---------------------------------------------------------
        self._sun.GetIntensityAttr().Set(
            float(self._base["sun_intensity"] * c["sun_intensity"] / 2450.0)
            if override else float(c["sun_intensity"]))
        # Elevation must track the HDRI's own measured sun: the disc is baked into
        # the dome, so a DistantLight at a different elevation gives two sets of
        # shadows (spec §4.4, deviation ceiling +-3 deg).
        self._sun_rx.Set(90.0 - float(c["sun_elev"]))
        self._sun.GetAngleAttr().Set(float(c["sun_angle_deg"]))
        # `lp` carries the condition's rotz so `__call__` keeps the dome and the
        # DistantLight coherent for the rest of the run.
        self.lp["hdri_sun_rotz_offset"] = float(c["hdri_sun_rotz_offset"])
        vis = _cond_sun_visible(c)
        from pxr import UsdGeom as _UG
        img = _UG.Imageable(self._sun.GetPrim())
        (img.MakeVisible if vis else img.MakeInvisible)()
        self(self.user_off)                       # re-apply rotation coherently

        if exposure:
            self.apply_exposure(c["ev_comp"])
        return c

    def apply_exposure(self, ev, iso_base=100.0):
        """Exposure compensation through `filmIso`.

        Deviation from spec §5.4, declared: the spec drives exposure with
        `exposureTime`, but the only exposure key MEASURED to work in this
        repository is `filmIso` (`t0_spike_report_v1.md` §7: ISO 100 -> 800 moved
        the frame mean 127 -> 214 with AE off). `exposureTime` does not appear in
        any runtime dump - what the dump carries is the legacy alias
        `cameraShutter = 50.0` - so writing 1/500 s to a key whose live name is
        unverified risks a 100x exposure error. ISO is exact, monotone and
        already validated, and exposure compensation is a pure stop offset, so
        which of the three exposure controls carries it is immaterial to the
        image. `fNumber` stays at 5.0 so no depth of field is introduced (§3.5).
        """
        import carb
        st = carb.settings.get_settings()
        st.set("/rtx/post/tonemap/filmIso", float(iso_base * (2.0 ** ev)))
        st.set("/rtx/post/tonemap/fNumber", 5.0)
        return iso_base * (2.0 ** ev)


def _cond_sun_visible(c):
    """Whether the DistantLight should be visible for this condition.

    Sunless conditions keep a visible, WIDENED sun rather than none: a fully
    non-directional dome makes relief shading vanish (a real phenomenon, but an
    unjudgeable cut), so spec §4.6 substitutes a cloud-transmitted soft direct at
    about 1/6 of clear-sky. sceneC1's own 420 is the precedent.
    """
    return bool(c["sun_intensity"] > 0.0)


def setup_lighting(stage, light_params, sun_az_offset, scene_key=None):
    """DomeLight (noon HDRI lookfix) + a DistantLight aligned with the HDRI sun direction.
    light_params: hdri, dome_intensity, noon_dome_rot, noon_sun_enable,
      noon_sun_elev, noon_sun_intensity, noon_sun_color, hdri_sun_rotz_offset.
    Returns: a `LightingControl` — callable as the old apply_dome_rot(user_off),
      and carrying .apply_cond(cond) for role=data condition switching."""
    from pxr import UsdGeom, UsdLux, Gf
    lp = light_params
    dome = UsdLux.DomeLight.Define(stage, "/World/DomeLight")
    dome.CreateIntensityAttr(float(lp["dome_intensity"]))
    dome.CreateTextureFormatAttr("latlong")
    tex_attr = dome.CreateTextureFileAttr()
    hdri = os.path.join(ASSETS_DIR, lp.get("hdri", DEFAULT_HDRI))
    if lp.get("lookfix", True):
        hdri = ensure_noon_lookfix(hdri)       # Sun cap + horizon haze lift
    else:
        print("[하늘] lookfix 스킵(overcast 등 무태양 프로파일) — 원본 사용")
    print(f"[하늘] noon: {os.path.basename(hdri)} "
          f"(exists={os.path.isfile(hdri)})")
    tex_attr.Set(hdri)
    # The RTX dome has its polar axis correctly at +Z on a Z-up stage (no rotateX needed)
    rot_op = UsdGeom.Xformable(dome.GetPrim()).AddRotateZOp()
    rot_op.Set(0.0)

    # An explicit DistantLight (0.53 deg) aligned with the HDRI sun direction - responsible for hard shadows
    sun = UsdLux.DistantLight.Define(stage, "/World/NoonSun")
    sun.CreateAngleAttr(0.53)
    sun.CreateIntensityAttr(float(lp["noon_sun_intensity"]))
    sun.CreateColorAttr(Gf.Vec3f(*[float(c) for c in lp["noon_sun_color"]]))
    sxf = UsdGeom.Xformable(sun.GetPrim())
    sun_rz = sxf.AddRotateZOp()
    sun_rz.Set(0.0)
    sun_rx = sxf.AddRotateXOp()
    sun_rx.Set(90.0 - float(lp["noon_sun_elev"]))
    if not lp.get("noon_sun_enable", True):
        UsdGeom.Imageable(sun.GetPrim()).MakeInvisible()

    ctl = LightingControl(dome, sun, rot_op, sun_rz, sun_rx, tex_attr,
                          lp, sun_az_offset, scene_key=scene_key)
    ctl(0.0)
    return ctl


# ===========================================================================
# [7] Camera presets
# ===========================================================================
def grid_views(gy, heights=(0.3, 0.9, 1.8), dists=(2, 5, 10), pitch=-10):
    """The h x d grid presets (the grid part of scene01 build_views). Looks along +X at pitch degrees.
    Returns: {"preset_h{h}_d{d}": dict(eye, tgt)}. Mise-en-scene shots are added per scene."""
    views = {}
    p = math.radians(pitch)
    for hh in heights:
        for dd in dists:
            eye = [-float(dd), float(gy), float(hh)]
            tgt = [eye[0] + 5.0 * math.cos(p), float(gy),
                   eye[2] + 5.0 * math.sin(p)]
            views[f"preset_h{hh}_d{dd}"] = dict(eye=eye, tgt=tgt)
    return views


# ===========================================================================
# [8] Headless capture pipeline (a generalisation of the scene01 capture block)
# ===========================================================================
def capture_pipeline(sim_app, views, out_dir_default, set_render_mode_fn,
                     look_from_fn):
    """Headless capture driven by NEGOBS_* env vars.
      NEGOBS_CAPTURE_DIR : output folder (default out_dir_default)
      NEGOBS_CAPTURE_MODE: rt | pt | both (default rt)
      NEGOBS_VIEWS       : comma-separated view name filter (default all)
      NEGOBS_WARMUP      : override for the number of warm-up updates
    set_render_mode_fn(mode): callback setting "PathTracing"/"RaytracedLighting".
    look_from_fn(eye, tgt)  : camera placement callback (eye and target as positional arguments)."""
    from omni.kit.viewport.utility import (get_active_viewport,
                                           capture_viewport_to_file)
    # [lighting round, D1] The judge channel is the regression baseline. A data
    # render never reaches this function - `run_data_render.py` replaces it - so
    # arriving here with variation env set means a judge round is about to be
    # contaminated. Fail, do not proceed (spec §2.3).
    _variation().assert_role_gate()
    out_dir = os.environ.get("NEGOBS_CAPTURE_DIR", out_dir_default)
    os.makedirs(out_dir, exist_ok=True)
    mode_sel = os.environ.get("NEGOBS_CAPTURE_MODE", "rt")
    modes = ["rt", "pt"] if mode_sel == "both" else [mode_sel]

    VIEWS = dict(views)
    view_f = os.environ.get("NEGOBS_VIEWS", "")
    if view_f:
        keep = {v.strip() for v in view_f.split(",") if v.strip()}
        VIEWS = {k: v for k, v in VIEWS.items() if k in keep}

    def _capture(fp):
        vp = get_active_viewport()
        capture_viewport_to_file(vp, file_path=fp)

    manifest = []
    print(look_report())
    print(f"[캡처] 모드={modes} 뷰={list(VIEWS)}")
    for _ in range(30):                        # Initial loading warm-up
        sim_app.update()

    pt_fast = os.environ.get("NEGOBS_PT_FAST", "") == "1"

    for mode in modes:
        set_render_mode_fn("PathTracing" if mode == "pt"
                           else "RaytracedLighting")
        warm_default = 572 if mode == "pt" else 90
        if pt_fast and mode == "pt":
            # The scene's set_render_mode resets spp=1/totalSpp=512, so the override must come
            # **after** it (the call order is the point).
            import carb
            st = carb.settings.get_settings()
            # Per-scene raise knob - a dark scene living on indirect light alone (D4 etc.) may find 64
            # insufficient. Raise it per scene, e.g. `NEGOBS_PT_TOTAL_SPP=256`.
            tot = int(os.environ.get("NEGOBS_PT_TOTAL_SPP",
                                     PT_FAST["total_spp"]))
            st.set("/rtx/pathtracing/spp", PT_FAST["spp"])
            st.set("/rtx/pathtracing/totalSpp", tot)
            st.set("/app/renderer/rtSubframes", PT_FAST["subframes"])
            warm_default = max(PT_FAST["warmup"],
                               -(-tot // (PT_FAST["spp"] * PT_FAST["subframes"])))
            print(f"[렌더] PT 가속 적용 (totalSpp {tot}, warmup {warm_default})")
        warm = int(os.environ.get("NEGOBS_WARMUP", str(warm_default)))
        for vname, v in VIEWS.items():
            look_from_fn(v["eye"], v["tgt"])
            for _ in range(warm):              # Without warm-up the image is black
                sim_app.update()
            fp = os.path.join(out_dir, f"{mode}_noon_{vname}.png")
            _capture(fp)
            # Capture is asynchronous -> wait until the file size stabilises
            # [GT-89] 40 update loops lost the race on heavy PT cuts (GT-88: 3 cuts
            # logged '[캡처] FAIL' with complete files on disk). Raised 4x and made
            # tunable; the loop still breaks as soon as the size is stable, so the
            # extra headroom costs nothing on the happy path.
            ok, prev_sz = False, -1
            for _ in range(int(os.environ.get("NEGOBS_CAPTURE_WAIT", "160"))):
                sim_app.update()
                if os.path.isfile(fp):
                    sz = os.path.getsize(fp)
                    if sz > 0 and sz == prev_sz:
                        ok = True
                        break
                    prev_sz = sz
            manifest.append(dict(file=fp, mode=mode, sky="noon",
                                 view=vname, ok=ok))
            print(f"[캡처] {os.path.basename(fp)} {'OK' if ok else 'FAIL'}")

    # Merge the manifest (across fragmented runs - entries with the same file are updated)
    mf_path = os.path.join(out_dir, "manifest.json")
    prev = dict(views={}, shots=[])
    if os.path.isfile(mf_path):
        try:
            with open(mf_path) as f:
                prev = json.load(f)
        except Exception:
            pass
    shots = {s["file"]: s for s in prev.get("shots", [])}
    for s in manifest:
        shots[s["file"]] = s
    prev.get("views", {}).update({k: v for k, v in VIEWS.items()})
    with open(mf_path, "w") as f:
        json.dump(dict(views=prev.get("views", VIEWS),
                       shots=list(shots.values())),
                  f, indent=2, ensure_ascii=False)


# ===========================================================================
# [9] Pure-maths self-verification (no pxr needed - reproduces and checks the builder placement maths only)
#     Run: python3 scene_common.py
# ===========================================================================
def _geometry_selfcheck():
    print("=" * 68)
    print("scene_common v3 신규 빌더 — 순수 수학 자기검증")
    print("=" * 68)

    # (1) build_helix_steps: 32 steps x 22.5 deg = 2 turns, total drop
    n, step_deg, riser, z0 = 32, 22.5, 0.18, 0.0
    total_sweep = n * step_deg
    total_drop = n * riser
    top_last = z0 - n * riser
    print("[1] helix_steps  n=%d step=%.1f°" % (n, step_deg))
    print("    총 회전각 = %.1f° = %.3f 회전" % (total_sweep, total_sweep / 360.0))
    print("    낙차 합 = %d*%.2f = %.2f m  (마지막 단 상면 z=%.2f)"
          % (n, riser, total_drop, top_last))
    r_in, r_out = 0.5, 2.2
    r_mid = (r_in + r_out) / 2.0
    chord = 2.0 * r_out * math.sin(math.radians(step_deg) / 2.0) * 1.03  # Cover based on the outer radius (look r1 fix)
    r_w = r_in + (2.0 / 3.0) * (r_out - r_in)     # Walkline radius (survey §3-1)
    print("    r_mid=%.3f 현길이=%.4f m  walkline r_w=%.3f (tread깊이 %.4f m)"
          % (r_mid, chord, r_w, r_w * math.radians(step_deg)))

    # (2) build_helix_ramp: segment tilt angle
    ri, ro = 6.0, 9.5
    a0, a1, seg = 0.0, 450.0, 36               # 1.25 turns
    z0r, z1r = 0.0, -3.2
    rm = (ri + ro) / 2.0
    dth = math.radians((a1 - a0) / seg)
    L_c = 2.0 * rm * math.sin(dth / 2.0)
    dz_seg = (z1r - z0r) / seg
    tilt = math.degrees(math.atan2(dz_seg, L_c))
    print("[2] helix_ramp  r_in=%.1f r_out=%.1f sweep=%.0f° seg=%d 낙차=%.1f"
          % (ri, ro, a1 - a0, seg, z1r - z0r))
    print("    r_mid=%.3f  세그 현길이 L_c=%.4f m  dz/세그=%.4f m"
          % (rm, L_c, dz_seg))
    print("    세그 접선경사각(rotX) = atan2(%.4f, %.4f) = %.4f°  (음수=하강)"
          % (dz_seg, L_c, tilt))
    print("    검산: 전체 경사 sin = 낙차/호길이 = %.4f (세그 sinθ=%.4f 근사일치)"
          % ((z1r - z0r) / (rm * math.radians(a1 - a0)),
             math.sin(math.radians(tilt))))

    # (3) build_worn_stone_stairs: total run + jitter reproduction (fixed seed)
    n, riser_mu, tread_mu, blocks, seed, jr = 18, 0.17, 0.38, 5, 77, 0.03
    rng = np.random.RandomState(seed)
    risers = [riser_mu + rng.uniform(-jr, jr) for _ in range(n)]
    run = n * tread_mu
    drop = sum(risers)
    print("[3] worn_stone  n=%d tread_mu=%.2f seed=%d" % (n, tread_mu, seed))
    print("    총 run = %d*%.2f = %.2f m" % (n, tread_mu, run))
    print("    지터 낙차 합(seed 재현) = %.4f m  (평균 riser=%.4f)"
          % (drop, drop / n))
    print("    처음 3단 riser = %s" % ["%.4f" % r for r in risers[:3]])

    # (4) width_pairs linear interpolation example (tapered_grand W_i)
    n, w_top, w_bot = 40, 6.0, 10.0
    cyc = 0.0
    def _wp(i):
        w = w_top + (w_bot - w_top) * i / (n - 1)
        return (cyc - w / 2.0, cyc + w / 2.0)
    print("[4] width_pairs 보간(tapered)  n=%d W_top=%.1f→W_bot=%.1f" %
          (n, w_top, w_bot))
    for i in (0, 10, 20, 39):
        y0i, y1i = _wp(i)
        print("    i=%2d  폭=%.3f m  (y0=%.3f, y1=%.3f)"
              % (i, y1i - y0i, y0i, y1i))
    print("=" * 68)


def _variation_selfcheck():
    """Preset / reference-lighting freeze check — spec §2.6. Pure maths, no pxr.

    Item 3 of the spec's list is the important one: "with NEGOBS_RENDER_ROLE
    unset, the lighting and camera code paths return the same values as the old
    code". That is the assertion that turns "the default reproduces today's
    output" from an intention into a test.
    """
    import re
    ok = True

    def chk(tag, cond, msg=""):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  [{'PASS' if cond else 'FAIL'}] {tag}"
              + (f" — {msg}" if msg else ""))

    print("=" * 74)
    print("scene_common — lighting/camera freeze self-check (spec §2.6)")
    print("=" * 74)

    # (1) grid_views must be byte-identical to the hardcoded expectation.
    print("\n[1] grid_views preset coordinates are frozen")
    p = math.radians(-10)
    exp = {}
    for hh in (0.3, 0.9, 1.8):
        for dd in (2, 5, 10):
            eye = [-float(dd), 0.0, float(hh)]
            exp[f"preset_h{hh}_d{dd}"] = (
                eye, [eye[0] + 5.0 * math.cos(p), 0.0,
                      eye[2] + 5.0 * math.sin(p)])
    got = grid_views(0.0)
    chk("9 keys, exact names", sorted(got) == sorted(exp), str(sorted(got)[:3]))
    bad = [k for k in exp
           if got[k]["eye"] != exp[k][0] or got[k]["tgt"] != exp[k][1]]
    chk("all 9 eye/tgt bit-identical", not bad, str(bad))
    # Two absolute anchors, independent of the generator above.
    chk("preset_h0.3_d2 eye == [-2.0, 0.0, 0.3]",
        got["preset_h0.3_d2"]["eye"] == [-2.0, 0.0, 0.3])
    chk("preset_h0.3_d2 tgt x == 2.9240387650610398",
        got["preset_h0.3_d2"]["tgt"][0] == 2.9240387650610398,
        repr(got["preset_h0.3_d2"]["tgt"][0]))
    chk("gy shifts y only",
        grid_views(-2.75)["preset_h0.9_d5"]["eye"] == [-5.0, -2.75, 0.9])
    chk("view names still carry the h token is_graze_view() greps for",
        all("h0.3" in k for k in got if k.startswith("preset_h0.3")))

    # (2) every scene's PARAMS["light"] must agree with catalogue L0, field by
    #     field. This is what makes "L0 == today" checkable rather than asserted.
    print("\n[2] all 33 scenes' light dict vs catalogue L0")
    try:
        import variation_kit as vk
    except Exception as e:                      # pragma: no cover
        chk("variation_kit importable", False, str(e))
        return 1
    L0 = vk.CONDITIONS["L0"]
    root = os.path.dirname(os.path.abspath(__file__))
    files = sorted(glob.glob(os.path.join(root, "scenes", "main", "scene*.py"))
                   + glob.glob(os.path.join(root, "scenes", "batch1",
                                            "scene*.py")))
    files = [f for f in files if "scene_common" not in f]
    pat = {
        "hdri": re.compile(r'hdri\s*=\s*"([^"]+)"'),
        "dome_intensity": re.compile(r"dome_intensity\s*=\s*([-\d.]+)"),
        "noon_sun_elev": re.compile(r"noon_sun_elev\s*=\s*([-\d.]+)"),
        "noon_sun_intensity": re.compile(r"noon_sun_intensity\s*=\s*([-\d.]+)"),
        "noon_dome_rot": re.compile(r"noon_dome_rot\s*=\s*([-\d.]+)"),
        "hdri_sun_rotz_offset": re.compile(
            r"hdri_sun_rotz_offset\s*=\s*([-\d.]+)"),
    }
    n_match, diffs = 0, []
    for f in files:
        key = os.path.basename(f).split("_")[0]
        src = open(f, encoding="utf-8").read()
        got_v = {}
        for k, rx in pat.items():
            m = rx.search(src)
            if m:
                got_v[k] = m.group(1)
        if got_v.get("hdri") != L0["hdri"]:
            # C1/C4 use OVERCAST_HDRI, and the three override scenes carry their
            # own balance — expected, listed, not a failure.
            diffs.append(f"{key}: hdri {got_v.get('hdri')}")
            continue
        mism = []
        if float(got_v.get("dome_intensity", -1)) != L0["dome_intensity"]:
            mism.append(f"dome {got_v.get('dome_intensity')}")
        if float(got_v.get("noon_sun_intensity", -1)) != L0["sun_intensity"]:
            mism.append(f"sun {got_v.get('noon_sun_intensity')}")
        if abs(float(got_v.get("noon_sun_elev", -1)) - L0["sun_elev"]) > 0.05:
            mism.append(f"elev {got_v.get('noon_sun_elev')}")
        if abs(float(got_v.get("hdri_sun_rotz_offset", -1))
               - L0["hdri_sun_rotz_offset"]) > 0.4:
            mism.append(f"rotz {got_v.get('hdri_sun_rotz_offset')}")
        if mism:
            diffs.append(f"{key}: " + ", ".join(mism))
        else:
            n_match += 1
    chk(f"{n_match} scenes match L0 exactly", n_match >= 28, f"{n_match}/33")
    expected_div = {"sceneC1", "sceneC2", "sceneC4", "sceneD4"}
    unexpected = [d for d in diffs if d.split(":")[0] not in expected_div]
    chk("only the 4 known-divergent scenes differ", not unexpected,
        str(unexpected) if unexpected else f"divergent: {sorted(expected_div)}")
    for d in diffs:
        print(f"         · {d}")

    # (3) role unset -> no variation applied anywhere.
    print("\n[3] role unset reproduces the old code path")
    keep = {k: os.environ.get(k)
            for k in list(vk.VARIATION_ENV) + ["NEGOBS_RENDER_ROLE"]}
    try:
        for k in keep:
            os.environ.pop(k, None)
        chk("render_role() == judge", vk.render_role() == vk.ROLE_JUDGE)
        chk("gate passes with a clean env",
            vk.assert_role_gate() == vk.ROLE_JUDGE)
        chk("L0 dome/sun are literally the 33-scene constants",
            (L0["dome_intensity"], L0["sun_intensity"]) == (1000.0, 2450.0))
        chk("L0 lookfix True and sun angle 0.53 (the current DistantLight)",
            L0["lookfix"] is True and L0["sun_angle_deg"] == 0.53)
        chk("_SUN_CAP_DEG_DEFAULT still 0.6 (W2 value)",
            _SUN_CAP_DEG_DEFAULT == 0.6)

        # (4) [W3 K-micro · S06-F2 / S09-F1] every SHRUB_SPECIES role must
        #     resolve to at least one VEG_SHRUBS row. This is the gate that
        #     would have caught three dead roles at landing time instead of
        #     three scene lanes finding them one at a time in a render.
        print("\n[4] SHRUB_SPECIES 역할 → VEG_SHRUBS 해석 (S06-F2 게이트)")
        _reg = {s[0] for s in VEG_SHRUBS}
        _dead = {r: [w for w in ws if w not in _reg]
                 for r, ws in SHRUB_SPECIES.items()}
        _dead = {r: m for r, m in _dead.items() if len(m) == len(SHRUB_SPECIES[r])}
        chk(f"{len(SHRUB_SPECIES)} roles all resolve to >=1 VEG_SHRUBS row",
            not _dead, str(_dead) if _dead else
            " · ".join(f"{r}:{len([w for w in ws if w in _reg])}"
                       for r, ws in sorted(SHRUB_SPECIES.items())))
        _orph = sorted({w for ws in SHRUB_SPECIES.values() for w in ws} - _reg)
        chk("no role names an asset with no registry row",
            not _orph, str(_orph) if _orph else "0")
        _pools = sorted(set(SHRUB_HEDGE) | set(SHRUB_ORNAMENT))
        chk("SHRUB_HEDGE / SHRUB_ORNAMENT are registered too",
            all(p in _reg for p in _pools), str(_pools))
        _disk = [s[0] for s in VEG_SHRUBS
                 if os.path.isfile(os.path.join(VEG_DIR, s[0]))]
        print(f"         · VEG_SHRUBS {len(VEG_SHRUBS)}행 · 디스크 존재 "
              f"{len(_disk)}종 (부재는 조달 상태이지 결함이 아니다)")
    finally:
        for k, v in keep.items():
            os.environ.pop(k, None)
            if v is not None:
                os.environ[k] = v

    print("\n" + "=" * 74)
    print("FREEZE SELF-CHECK " + ("PASS" if ok else "FAIL"))
    print("=" * 74)
    return 0 if ok else 1


if __name__ == "__main__":
    import sys as _sys
    if "--variation" in _sys.argv:
        raise SystemExit(_variation_selfcheck())
    _geometry_selfcheck()
    raise SystemExit(_variation_selfcheck())
