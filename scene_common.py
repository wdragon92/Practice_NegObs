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
for _s in ("warn_fall", "caution_step", "exit", "info", "no_entry"):
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
_DETAIL_MAP = {
    "mineral":  ("detail_grain_mineral_nor.png",  0.85, 12.5),  # Paving, concrete, stone, curb, nosing
    "granular": ("detail_grain_granular_nor.png", 0.70,  8.0),  # Soil, gravel, asphalt, snow
    "metal":    ("detail_grain_brushed_nor.png",  0.55, 25.0),  # Metal (anisotropic scratches)
}
# When procedural generation fails or nothing was procured - what the repository already holds (0 procurement). §3.2 confirmed both families pass.
_DETAIL_FALLBACK = {
    "mineral":  ("scene01/plaster_nor_dx.jpg", 0.85, 12.5),   # macro 3.9 · slope −0.89 · RMS 0.159
    "granular": ("scene01/asphalt_nor_dx.jpg", 0.70,  8.0),   # macro 3.2 · slope −0.66 · RMS 0.294
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

LOOK_CLASS = {
    #                    bevel   sat   mdl        patch  detail
    # Individual chamfering of paving blocks **has no published domestic figure** (the body of KS F 4419 is paywalled,
    # and an exhaustive check of public documents citing it found 0 chamfer clauses - the survey concluded "do not estimate").
    # Moreover round_edges applies to the **slab prim boundary**, not to individual blocks.
    # Individual block chamfers are already handled by the texture normal map, so the value here is for the slab
    # boundary and is kept below the curb (10 mm). [no basis - conservative choice]
    "paving":   dict(bevel=0.006, sat=1.00, mdl="ground", patch=0.0, detail=True,
                     tex="paving_interlock", bump=1.4,
                     tex_alts=("stone_flag", "paving_interlock", "plaster")),
    "concrete": dict(bevel=0.020, sat=1.00, mdl="ground", patch=0.0, detail=True,
                     weather=_W_STRUCT, tex="concrete_floor", bump=1.6,
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
                     weather=_W_STONE, tex="stone_flag", bump=1.5,
                     tex_alts=("stone_flag", "marble_light")),
                     # Bevel [no basis] conservatively lowered
    "soil":     dict(bevel=0.000, sat=0.74, mdl="ground", patch=1.0, detail=True,
                     tex="dirt_park", bump=1.4,
                     tex_alts=("dirt_park", "gravel")),
    "gravel":   dict(bevel=0.000, sat=0.78, mdl="ground", patch=1.0, detail=True,
                     tex="gravel", bump=1.4),
    # tex: promote a constant-colour material to the texture of this TEX role (the intended albedo is preserved).
    # spec/bump: diagnosis P1/P3 - the road surface is excessively bright because of grazing gloss, so
    # specular_level is stated explicitly and shadow contrast is restored through normal strength.
    "asphalt":  dict(bevel=0.006, sat=0.90, mdl="ground", patch=1.0, detail=True,
                     tex="asphalt", spec=0.20, bump=1.4),
    # The 12 mm nosing is the **top of the IBC 1.6-14.3 mm range**. No domestic rule exists (exhaustively checked).
    "nosing":   dict(bevel=0.012, sat=1.00, mdl="ground", patch=0.0, detail=True,
                     weather=dict(grime=0.0, splash=0.0, wrough=0.10)),
    "curb":     dict(bevel=0.010, sat=1.00, mdl="ground", patch=0.0, detail=True,
                     weather=_W_EDGE),   # Vertical curb R=10 (directive 321, figure 2.17)
    "metal":    dict(bevel=0.002, sat=1.00, mdl="omni",   detail=True),
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
    "snow":     dict(bevel=0.000, sat=1.00, mdl="ground", patch=1.0, detail=True,
                     tex="snow", bump=1.3),
    "misc":     dict(bevel=0.003, sat=1.00, mdl="omni",   detail=False),
}

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
    "Grate": "metal", "Grating": "metal", "Gear": "metal", "Roof": "metal",
    # Wood
    "Wood": "wood", "WoodDark": "wood", "SeatWood": "wood", "Bench": "wood",
    # Vegetation
    "Grass": "veg", "GrassB": "veg", "CanopyA": "veg", "CanopyB": "veg",
    "Leaf": "veg", "LeafA": "veg", "LeafB": "veg", "Hedge": "veg",
    "Shrub": "veg", "Reed": "veg", "Moss": "veg",
    # Water
    "Water": "water",
    # Paint and markings - a constant colour is physically correct (not to be texturised)
    "Paint": "paint", "LineWhite": "paint", "LineYellow": "paint",
    "Band": "paint", "Tactile": "paint",
    # Glass, signs, emissive
    "Glass": "glass", "Window": "glass", "Panel": "sign",
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
    return (f"[룩v1] MTL={int(LOOK_MTL)} GEO={int(LOOK_GEO)} | "
            f"재질 ground={r['ground']} omni_tex={r['omni_tex']} "
            f"const={r['const']} skip={r['skipped']} | 베벨={r['bevel']} "
            f"디테일={r['detail']} 스킨={r['skin']} "
            f"승격={r.get('promoted', 0)} 상수MDL={r.get('const_mdl', 0)} "
            f"웨더={r.get('weather', 0)} 나무={r.get('veg_asset', 0)} "
            f"간살={r.get('baluster', 0)} 관목={r.get('shrub', 0)} "
            f"손잡이={r.get('handrail', 0)} "
            f"산포={r.get('debris', 0)} | 역할 "
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
    ("paint", ("paint", "linewhite", "lineyellow", "roadpaint", "tactile",
               "warn", "tape", "band", "stripe", "gauge", "joint", "cutline",
               "lane")),   # **"lane" belongs here (road marking)** - caught before asphalt
    # Vegetation
    ("veg", ("grass", "leaf", "canopy", "hedge", "shrub", "foliage", "reed",
             "tuft", "tree", "moss", "treeline", "treepit", "verge")),
    # Snow - the **largest single-material area across all 33 scenes** (sceneC1 88.5 %), yet it was stuck in misc
    # and received neither the constant-colour MDL nor a texture promotion.
    ("snow", ("snow", "frost")),
    # Water
    ("water", ("water", "sea", "tide", "wet")),
    # Metal
    ("metal", ("rail", "steel", "iron", "metal", "pole", "post", "lamp",
               "bollard", "gate", "fence", "grate", "grating", "galv",
               "rebar", "wire", "cable", "hvac", "crane", "gear", "shutter",
               "mullion", "frame", "bin", "lid", "duck", "tool", "beak")),
    # Wood
    ("wood", ("wood", "deck", "bench", "seat", "sleeper", "pallet",
              "stringer", "carton", "door")),
    # Drop edge - approved nosing 12 mm / curb 12 mm
    ("nosing", ("nosing", "tread", "step")),
    # **"verge" removed** - the Verge* materials of scene04 are grass verges (vegetation) yet were
    # receiving the curb prescription (13.4 % of the area). English verge means a shoulder or grass margin, not a curb.
    ("curb", ("curb", "coping", "cope", "kerb")),
    # Stone
    ("stone", ("stone", "granite", "marble", "rock", "flag", "cobble",
               "polish", "lightstone")),
    # Brick, rendered wall
    ("brick", ("brick", "plaster")),
    # Soil, gravel
    ("soil", ("soil", "dirt", "earth", "mud", "leafbed")),
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
    ("concrete", ("concrete", "conc", "wall", "parapet", "shell", "slab",
                  "stair", "riser", "skirt", "fascia", "ceiling", "facade",
                  "bldg", "city", "house", "shed", "tunnel", "bridge",
                  "pier", "abutment", "crest", "ridge", "trough", "valley",
                  "container", "stage", "upper", "lower", "roof", "canopy",
                  "awning", "trim", "grime", "dark", "skyline", "far",
                  "coating", "membrane", "stain", "wear", "crack", "silt",
                  "efflor", "salt")),
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
def boot(headless):
    """Boot Isaac Sim. SimulationApp is always created first, then everything else is imported.
    Applies the carb capture hygiene settings and the stage units (Z-up, metre) and returns
    sim_app. The scene can obtain stage again through
    omni.usd.get_context().get_stage().
    """
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


def add_box(stage, path, center, size, mtl=None, collider=False):
    from pxr import UsdGeom, UsdPhysics, Gf
    cube = UsdGeom.Cube.Define(stage, path)
    cube.CreateSizeAttr(2.0)
    cube.CreateExtentAttr([Gf.Vec3f(-1, -1, -1), Gf.Vec3f(1, 1, 1)])
    xf = UsdGeom.Xformable(cube)
    xf.AddTranslateOp().Set(Gf.Vec3d(*[float(c) for c in center]))
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
    if LOOK_GEO and _skin_wanted(path, size, mtl):    # A new mesh = geometry
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
                      "veg", "wood"}

# Role classes that get a displacement skin (ground family only). Stairs, curbs and nosings are excluded -
# they are drop edge geometry and are left alone under approval condition (2).
_SKIN_CLASSES = {"paving", "concrete", "asphalt", "soil", "gravel", "stone"}
# A path containing one of these tokens gets no displacement even if it is ground (drop geometry, walking safety)
#   "gkit" - all ground_kit output lives under `{ROOT}/GKit/...`. Some builders create areas over
#   4 m, such as coating and wear bands, so without this token a ground_kit element would
#   **take on a second skin over itself** [W2-0, spec §1.2].
_SKIN_DENY = ("stair", "step", "tread", "riser", "nosing", "curb", "ramp",
              "landing", "deck", "platform", "edge", "lip", "sill", "gkit")


def add_cylinder(stage, path, center, radius, height, mtl=None,
                 rotY=0.0, rotX=0.0, collider=False):
    from pxr import UsdGeom, UsdPhysics, Gf
    cyl = UsdGeom.Cylinder.Define(stage, path)
    cyl.CreateRadiusAttr(float(radius))
    cyl.CreateHeightAttr(float(height))
    cyl.CreateAxisAttr(UsdGeom.Tokens.z)
    xf = UsdGeom.Xformable(cyl)
    # Order: translate -> rotate (rotate about the prim origin, then move)
    xf.AddTranslateOp().Set(Gf.Vec3d(*[float(c) for c in center]))
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
             unit_cell=None):
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
                                    unit_cell=unit_cell, cls=cls)
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
                    unit_cell=unit_cell, cls=cls)
            LOOK_STATS["const_mdl"] = LOOK_STATS.get("const_mdl", 0) + 1
            return _make_ground_pbr(stage, path, None, None, None, scale_m,
                                    spec, tint=tint,
                                    roughness_const=roughness_const,
                                    specular_level=specular_level, bump=bump,
                                    base_color=diffuse_color,
                                    unit_cell=unit_cell, cls=cls)
        # Textured material -> bevel + detail normal.
        # **Constant-colour materials get the bevel too** - the first gate skipped constant colours
        # entirely, and constant colours are precisely the main source of flat %. Texturising is a
        # separate item (brief 2-7, awaiting a full audit) but the bevel needs no texture.
        LOOK_STATS["omni_tex" if diff is not None else "const"] += 1
        _look_omni = spec
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


def _make_ground_pbr(stage, path, diff, nor, rough, scale_m, spec,
                     tint=None, roughness_const=None, specular_level=None,
                     bump=1.0, base_color=None, metallic=0.0,
                     unit_cell=None, cls=None):
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
    if base_color is not None or tint is not None:
        sh.CreateInput("base_color", C3).Set(Gf.Vec3f(*_bc))
    s = _GROUND_SCALE_FIX / float(scale_m)
    sh.CreateInput("texture_scale_a", F2).Set(Gf.Vec2f(s, s))
    sh.CreateInput("bump_factor_a", F).Set(
        float(spec.get("bump", bump)))
    sh.CreateInput("use_blend", B).Set(False)
    # Repetition break-up - modular paving uses patch 0 (protects the pattern), natural ground 1
    sh.CreateInput("patch_mix_a", F).Set(float(spec.get("patch", 1.0)))
    sh.CreateInput("patch_wavelength_a", F).Set(4.0)
    # Constant-colour mode has no texture high frequencies, so a strong macro reads as blotching.
    sh.CreateInput("macro_amp_a", F).Set(0.07 if diff is None else 0.12)
    sh.CreateInput("macro_wavelength_a", F).Set(14.0)
    sh.CreateInput("desat_bright_a", F).Set(0.0 if diff is None else 0.30)
    sh.CreateInput("saturation_a", F).Set(
        _effective_sat(spec, diff, base_color))
    sh.CreateInput("rough_noise_a", F).Set(0.22)
    sh.CreateInput("rough_noise_wavelength_a", F).Set(1.2)
    # Constant-colour mode has no texture, so no axis-transition streaking occurs ->
    # 6 dithering noise taps are pure waste. Set to 0 to cut the cost.
    sh.CreateInput("tri_dither", F).Set(0.0 if diff is None else 0.35)
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


def build_arc_steps(stage, prefix, cx, cy, r_in, r_out, a0_deg, a1_deg, seg,
                    top_z, base_z, mtl, collider=True):
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


def build_nosing(stage, prefix, x0, y0, y1, riser, tread, n, base_z=0.0,
                 mtl=None, color=(0.85, 0.72, 0.10), width=0.05, proud=0.001,
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


def build_railing_line(stage, prefix, y, x_start, x_top, run, drop, ground_fn,
                       mtl, rail_h=None, post_r=0.02, spacing=None, rail_r=0.03,
                       rail_mid_r=0.018, rail_mid_drop=0.45,
                       baluster_r=0.009, baluster_gap=0.098, handrail=True):
    """One guardrail line (a generalisation of scene01 build_cues). Top rail + mid rail + posts.
      y        : rail Y position
      x_start  : x where the horizontal extension starts (x_start..x_top is horizontal)
      x_top    : x where the slope starts (descending by drop towards +X from here)
      run,drop : horizontal length and drop of the sloped section
      ground_fn: x -> ground z callback (landing height of the post foot). Stepped on stairs.
    Returns: list of created prims."""
    # The defaults change to the statutory values **only under LOOK_GEO** (post count = geometry).
    # Previously the defaults themselves were changed to 1.1/2.0, and callers that do not state
    # these two values (scene03/14/17/21) **saw the post count change even with the look layer off**.
    # The post loop is outside the gate, so the control geometry gets contaminated -
    # the same type of recurrence as the one named "fatal C3" and fixed in bc87292.
    if rail_h is None:
        rail_h = 1.1 if LOOK_GEO else 0.9      # Road safety facility guideline 2.5
    if spacing is None:
        spacing = 2.0 if LOOK_GEO else 1.2
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

    _seg("RailTop", rail_r, 0.0)
    _seg("RailMid", rail_mid_r, rail_mid_drop)
    x_end = x_top + run

    # Vertical balusters - the guardrail standard of the road safety facility guideline. A clear
    # opening of 100 mm or less between balusters is a statutory requirement, so real Korean
    # guardrails are dense without exception. On a slope the balusters stay **vertical** (only the
    # rail tilts), which makes the silhouette markedly different. Inside the LOOK_GEO gate - A/B control preserved.
    if LOOK_GEO and baluster_r > 0:
        pitch = 2.0 * baluster_r + baluster_gap
        xb = x_start + pitch * 0.5
        b = 0
        while xb <= x_end - pitch * 0.25:
            t = max(0.0, min((xb - x_top) / run, 1.0)) if run > 1e-9 else 0.0
            ztop = top0 - drop * t - rail_r          # Underside of the top rail
            gz = float(ground_fn(xb))
            # The balusters must come down **close to the ground**. Previously they stopped at the mid
            # rail and filled only 43 % of the guardrail height, and the actual opening in the lower
            # 0.45-0.60 m violated the cited statutory 100 mm by 11 to 28 times.
            # (Geometry justified by a statutory requirement was violating that requirement.)
            zbot = max(gz + 0.04, top0 - drop * t - rail_h + 0.04)
            h = ztop - zbot
            if h > 0.05:
                prims.append(add_cylinder(
                    stage, f"{prefix}/Bal_{b}", (xb, y, zbot + h / 2.0),
                    baluster_r, h, mtl))
            xb += pitch
            b += 1
        LOOK_STATS["baluster"] = LOOK_STATS.get("baluster", 0) + b

    # Posts: landing on the real ground (ground_fn), top = the rail line.
    xp = x_start
    p = 0
    while xp <= x_end + 1e-6:
        gz = float(ground_fn(xp))
        t = max(0.0, min((xp - x_top) / run, 1.0)) if run > 1e-9 else 0.0
        railz = top0 - drop * t
        ph = railz - gz
        if ph > 1e-3:
            prims.append(add_cylinder(
                stage, f"{prefix}/Post_{p}", (xp, y, gz + ph / 2.0),
                post_r, ph, mtl))
        xp += spacing
        p += 1

    # -- Handrail -------------------------------------------------------
    # Evac/fire structure rules §15(4). **Unimplemented in all 33 scenes.**
    # dia 32-38, height 850, **horizontal end extension >=300** - that end hook is
    # characteristic of the Korean stair silhouette, yet our rails simply stopped dead.
    # No GT effect: a vertical/horizontal member above the stair surface, it does not change z(x,y).
    if LOOK_GEO and handrail and run > 0.3:
        try:
            prims += sk.build_handrail(
                stage, f"{prefix}/Handrail", y, x_top, run, drop, mtl,
                add_cylinder, z_top=ground_ref, ground_fn=ground_fn,
                strict=False)
            LOOK_STATS["handrail"] = LOOK_STATS.get("handrail", 0) + 1
        except Exception as e:
            print(f"[룩v1][경고] 손잡이 실패 {prefix}: {e}")
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
                      riser, z0, mtl, ccw=True, collider=True, base_drop=0.5):
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
        prims.append(_oriented_box(
            stage, f"{prefix}/Step_{i}", (px, py, cz),
            (radial, chord, base_drop), mtl, collider=collider, rotz=a_deg))
    return prims


def build_helix_ramp(stage, prefix, cx, cy, r_in, r_out, a0_deg, a1_deg, seg,
                     z0, z1, thick, mtl, collider=True):
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
]
# [measured - `assets/veg_manifest_w2.json` (2026-07-29, usd-core 26.8, UV pixel verdict)]
#   Elm_Sapling     zmax 3.0867, 113,268 tri, leaf beech_leaf green 99.2 % - PASS
#   Shumard_Oak     zmax 10.8989, 99,509 tri, oakleaves 1-4 green/olive 100 % - PASS
#   Chinese_Juniper zmax 2.5164, 27,098 tri, pine_needles green 80.2 % + yellow-green 19.8 % - PASS
VEG_SHRUB = [("Shrub/Boxwood.usd", 0.74, 1)]  # Boxwood


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


def _deactivate_seasonal(stage, asset_path, usd_rel):
    """Turn off season-specific sub-prims of a referenced vegetation asset.

    The season convention is judged on leaf/flower TEXTURE PIXELS, not on the
    species name. `Rhododendron` is a full-bloom scan (76.7 % of the basecolor
    is magenta), so the shrub itself is season-neutral only once `/Root/Flowers`
    is deactivated. Deactivation removes the prim from composition, so the
    flower geometry is never drawn and costs nothing.
    Silent no-op when the asset has no registered seasonal prims.
    """
    names = SEASONAL_SUBPRIMS.get(usd_rel)
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

# Season-specific prims - disabled with `SetActive(False)` right after referencing. The asset root (`/Root`)
# maps to the referencing prim, so `/Root/Flowers` becomes `{prim}/Asset/Flowers`.
# [measured - `strings assets/vegetation/Shrub/Rhododendron.usd` = Branches, Flowers, Leaves]
SEASONAL_SUBPRIMS = {
    "Shrub/Rhododendron.usd": ("Flowers",),
}

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
               canopy_spread=1.0):
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

    Returns: None (prims are created under prefix)."""
    import random as _random
    rnd = _random.Random((int(round(cx * 100)) * 73856093)
                         ^ (int(round(cy * 100)) * 19349663))

    if LOOK_GEO and veg_available():
        # The species is decided by a coordinate hash - identical on re-running the same scene, and different per tree.
        pool = [t for t in veg_pool() for _ in range(t[2])]
        rel, native, _ = pool[rnd.randrange(len(pool))]
        # **Tree height is a cue.** Cue family (3) (scale anchors) uses the "absolute height of the canopy top",
        # so randomising it widely erases the very axis that must be learnt.
        # The old uniform(1.45,1.85) was an unfounded magic number (red team finding - accepted).
        # -> A fixed ratio of 1.60 (total height to trunk height) with only +-8 % per-instance variation.
        target = float(trunk_h) * 1.60 * rnd.uniform(0.92, 1.08)
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
                  cap_over=0.05, cap_h=0.05, grass_h=0.40):
    """Flower bed: 4 kerb walls + cap (overhang) + grass top surface (+ an optional tree).
    With tree_mtls=(wood, canopy_a, canopy_b) a tree is placed in the centre. Transplanted from scene01."""
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
    if LOOK_GEO and veg_available():
        inner = S / 2.0 - t - 0.25
        if inner > 0.35:
            r = inner * 0.62
            pts = [(cx + r, cy + r, base_z + gh), (cx - r, cy - r, base_z + gh)]
            if tree_mtls is None:
                pts.append((cx, cy, base_z + gh))
            place_shrubs(stage, f"{prefix}/Shrub", pts,
                         target_h=min(0.85, max(0.45, inner * 0.9)),
                         pool=SHRUB_ORNAMENT,
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
            else:
                yc = bd["y0"] + wd["margin"] + (c + 0.5) * (usable / ncols)
                prims.append(add_box(stage, f"{prefix}/Win_{f}_{c}",
                                     (gx_win, yc, zc), (WIN_T, wd["w"], wd["h"]),
                                     glass_mtl))

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
        prims += fk.build_plinth(K, stage, prefix, bd["x0"], bd["x1"],
                                 bd["y0"], bd["y1"], base, parapet_mtl,
                                 height=1.10)
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
    DW, DH = 1.8, 2.1
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
                 overlap=0.0, tag="Sh"):
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
        return 0
    import random as _random
    rnd = _random.Random(int(seed) & 0x7FFFFFFF)
    placed = 0
    for i, (px, py, pz) in enumerate(pts):
        rel, nat_w, zmin, _tri, nat_h = avail[rnd.randrange(len(avail))]
        # [W2, audit A 6-b fix] **The height scale is based on the native 'height'.**
        # It used to be based on width ("shrubs are roughly as wide as they are tall" [estimate]), and the measured
        # aspect ratios spread over 0.607-1.973 gave -39 % to +97 % error against the requested height.
        # `overlap` is an argument meant to create **overlap in the width direction**, so after moving to a
        # height basis it is applied with the same factor to preserve the previous hedge density.
        s = (float(target_h) * (1.0 + overlap) / max(nat_h, 1e-6)
             * rnd.uniform(0.92, 1.08))
        try:
            # zmin is a native dimension and must be scaled by the same factor for the bottom to sit on the ground.
            # Forgetting this buries 41 cm of Rhododendron (zmin -0.416) underground.
            xf = add_vegetation(stage, f"{prefix}/{tag}_{i}", rel,
                                (px, py, float(pz) + zmin * s),
                                yaw_deg=rnd.uniform(0, 360),
                                scale_mul=s)
            if xf is not None:
                # Seasonal sub-prims off BEFORE instancing. Order matters:
                # once SetInstanceable(True) is applied the descendants live in
                # a shared prototype and per-instance edits are ignored.
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


def setup_lighting(stage, light_params, sun_az_offset):
    """DomeLight (noon HDRI lookfix) + a DistantLight aligned with the HDRI sun direction.
    light_params: hdri, dome_intensity, noon_dome_rot, noon_sun_enable,
      noon_sun_elev, noon_sun_intensity, noon_sun_color, hdri_sun_rotz_offset.
    Returns: the apply_dome_rot(user_off) callback (updates the dome and auxiliary sun Z rotation)."""
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
    sxf.AddRotateXOp().Set(90.0 - float(lp["noon_sun_elev"]))
    if not lp.get("noon_sun_enable", True):
        UsdGeom.Imageable(sun.GetPrim()).MakeInvisible()

    def apply_dome_rot(user_off):
        # Dome rotation = noon_dome_rot + sun_az_offset (scene) + the [ ] key offset
        rot = (float(lp["noon_dome_rot"]) + float(sun_az_offset)
               + float(user_off))
        rot_op.Set(rot)
        sun_rz.Set(rot + float(lp["hdri_sun_rotz_offset"]))

    apply_dome_rot(0.0)
    return apply_dome_rot


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
            ok, prev_sz = False, -1
            for _ in range(40):
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


if __name__ == "__main__":
    _geometry_selfcheck()
