# -*- coding: utf-8 -*-
"""e1_const.py -- THE single source of truth for every decision-affecting number
used by the e1_0827 labeling skeleton (brief v6 §3-P1).

Rules enforced here:
  * No other e1_* module may spell a decision-affecting numeric literal.
    `e1_selftest.py --scan-consts` walks the code and fails on any literal that
    is not in STRUCTURAL_OK below.
  * Every entry carries `tag` (one of the six ledger tags), `why` (source) and
    `sens` (2-3 alternative values for the sensitivity plan, or None when the
    constant is not a threshold).
  * `CONST_LEDGER.md` in the cycle root is cross-checked AGAINST this table by
    `e1_selftest.py --ledger` (both directions: nothing missing from the ledger,
    no stale name in it), so the two cannot silently drift apart.

Tags: [문헌] [실측] [도구기본값] [기존값] [방법] [임시-결재대기]
NOTHING here is adopted. [임시-결재대기] entries are running values that exist
only so the skeleton can execute; adoption is 승용's 결재 (P1).
"""

import hashlib
import json

# --------------------------------------------------------------------------- #
# the table
# --------------------------------------------------------------------------- #
# key -> (value, tag, why, sens)
CONSTANTS = {

    # ---- image / camera model ------------------------------------------- #
    "IMG_W": (1920, "[기존값]",
              "renderer frame width; variation_kit.py:43 RES_W. Cross-checked "
              "against the shape of every rendered *.depth.npy read.", None),
    "IMG_H": (1080, "[기존값]",
              "renderer frame height; variation_kit.py:43 RES_H. Same cross-check.",
              None),
    "PRINCIPAL_POINT_MODE": ("center", "[기존값]",
                             "variation_kit.look_at_rows docstring: 'the principal "
                             "point dead centre of the 1920x1080 frame'. cx=W/2, cy=H/2.",
                             None),
    "PIXEL_ASPECT": (1.0, "[기존값]",
                     "variation.json stores only a horizontal aperture (20.955 mm) "
                     "and focal; fy=fx follows from square pixels. Verified: "
                     "2*atan(aperture/2/focal) reproduces the stored hfov to 1e-3 deg.",
                     None),
    "DEPTH_VALID_MIN_M": (0.01, "[방법]",
                          "a depth sample below this is treated as invalid (near "
                          "clip / degenerate). Sky is already inf in the stored "
                          "float16 array and is dropped by isfinite.",
                          (0.001, 0.01, 0.1)),
    "CAM_FRONT_Z_MIN_M": (0.05, "[방법]",
                          "a world point must sit at least this far in front of the "
                          "image plane before it is projected (division guard).",
                          (0.01, 0.05, 0.20)),

    # ---- camera verification (e1_camera.verify) -------------------------- #
    "CAMCHK_STRIDE_PX": (4, "[방법]",
                         "pixel stride when back-projecting the depth image for the "
                         "camera proof. Report-only; does not enter any label.",
                         (1, 4, 8)),
    "CAMCHK_RADIUS_M": (6.0, "[방법]",
                        "horizontal radius around the camera inside which the "
                        "back-projected depth is compared with the heightmap. The "
                        "heightmap is an AABB envelope (see HM_SOURCE_NOTE), so far "
                        "field / facade pixels are not a camera error. Report-only.",
                        (3.0, 6.0, 10.0)),

    # ---- route (a): heightmap edge instances ----------------------------- #
    "DROP_MIN_M": (0.30, "[문헌·기존 확정]",
                   "hazard drop threshold. brief v6 §1 '낙차 위험 문턱 0.3 m "
                   "[문헌·기존 확정]' and §2 rule 1. NOT ours to move.", None),
    "R_RUN_M": (1.0, "[기존값]",
                "run distance inside which the walkable surface must fall by "
                "DROP_MIN_M. Carried from mainrun_0819 labeler.py STEP_RUN_M = 1.0 "
                "(D10). Sensitivity is mandatory (brief §2 rule 1, §6-4).",
                (0.5, 1.0, 2.0)),
    "HM_STEP_SOURCE": ("heightmap_meta.json:step", "[기존값]",
                       "heightmap grid resolution is READ per scene, never spelled. "
                       "Measured value in the 260819_main_on corpus: 0.05 m for all "
                       "33 scenes (heightmap_meta.json). Recorded because brief §2 "
                       "rule 1 makes the grid resolution a mandatory ledger entry.",
                       None),
    "EDGE_WINDOW_SHAPE": ("disc", "[방법]",
                          "shape of the neighbourhood that implements '진행거리 "
                          "R_RUN_M 안' on the grid. 'disc' (running value) is the "
                          "literal reading -- every cell within R_RUN_M metres. "
                          "'chebyshev' is a square window: separable, ~40x faster, "
                          "but it reaches R_RUN_M*sqrt(2) = 1.41 m diagonally, i.e. "
                          "an OVER-approximation of the disc. 'cross' takes the axis "
                          "directions only (under-approximation). Requested for the "
                          "ledger by the Phase-0 census track, whose report-only "
                          "probe code/p0_edge_distance.py runs the 'chebyshev' "
                          "window -- its distances are therefore not directly "
                          "comparable with this pipeline's.",
                          ("disc", "chebyshev", "cross")),
    "BREAK_LOCAL_FALL_M": (0.05, "[임시-결재대기]",
                           "cell-to-cell fall (4-neighbour, one grid step) that marks "
                           "a LOCAL break of the surface. Separates a genuine step "
                           "from a smooth ramp that also falls 0.3 m within R_RUN.",
                           (0.02, 0.05, 0.10)),
    "WALK_FOOT_R_M": (0.30, "[임시-결재대기]",
                      "footprint radius for the walkability test. A surface counts as "
                      "walkable only if it stays flat inside this radius -- this is "
                      "what keeps a railing top / parapet / roof edge (also a 0.3 m "
                      "drop in the AABB heightmap) out of the edge population.",
                      (0.15, 0.30, 0.50)),
    "WALK_FLAT_TOL_M": (0.10, "[임시-결재대기]",
                        "max z spread allowed inside the walkability footprint.",
                        (0.05, 0.10, 0.20)),
    "WALK_SUPPORT_FRAC": (0.25, "[임시-결재대기]",
                          "a lip cell can never be flat over its whole footprint "
                          "(the footprint spans the drop), so it qualifies instead "
                          "when at least this fraction of the footprint shares its "
                          "height. A railing top is ~1-2 cells wide inside a 0.30 m "
                          "disc and falls under it; a plaza lip keeps ~half.",
                          (0.15, 0.25, 0.40)),
    "MAX_TRAVERSE_STEP_M": (0.20, "[임시-결재대기]",
                            "reachability step limit for the flood fill that defines "
                            "'walkable surface the robot is actually on'. Basis: "
                            "building-code stair risers are 0.15-0.18 m (every tread "
                            "must stay reachable) while a parapet/roof edge must not. "
                            "Not a literature value for THIS robot -- 결재 (❓B-3).",
                            (0.15, 0.20, 0.30)),
    "REACH_ANCHOR_MODE": ("largest_ground_component", "[임시-결재대기]",
                          "where the reachability flood fill starts. MEASURED "
                          "PROBLEM with the first rule ('camera_cell_clamped'): the "
                          "cameras of this corpus routinely stand OUTSIDE the "
                          "heightmap footprint (scene02 cut 0: eye x = -8.62 vs "
                          "x_range [-2.0, 14.0]), and clamping to the grid edge "
                          "landed the anchor on a 29-cell strip of ground walled off "
                          "by a 2.84 m step -- route (a) then reported 0 edge cells "
                          "for a scene whose ground level holds 83,925 walkable "
                          "cells. 'largest_ground_component' instead anchors on the "
                          "biggest 4-connected walkable component within "
                          "MAX_TRAVERSE_STEP_M of the recorded cam.ground_z. Both "
                          "modes are measured side by side in "
                          "reports/P0_CODE_SKELETON.md §4-1 -- 결재 (❓B-9).",
                          ("camera_cell_clamped", "largest_ground_component")),
    "MIN_INSTANCE_LEN_M": (0.30, "[임시-결재대기]",
                           "a connected break-line component shorter than this (in "
                           "grid cells x step) is dropped as speckle.",
                           (0.15, 0.30, 1.00)),
    "INT_ASSIGN_INFRAME_ONLY": (False, "[임시-결재대기]",
                                "who may own an interior pixel. False (running "
                                "value) = pure nearest-instance Voronoi, so no "
                                "association radius has to be invented -- but an "
                                "edge instance entirely OUT OF FRAME can then own "
                                "interior pixels (measured on scene01 cut 0: e03/e04 "
                                "hold 85,985 and 45,151 px with no in-frame edge "
                                "point at all). True = only instances with at least "
                                "one in-frame projected point may own pixels. "
                                "결재 (❓B-5).", (False, True)),
    "RDP_TOL_PX": (2.0, "[방법·표시전용]",
                   "DRAWING ONLY in the simple labeler: the stored polyline is the pixel-exact rim and this tolerance is applied only when the line is stroked, so no measured number depends on it. In route (a): Douglas-Peucker tolerance when a visible run of projected edge "
                   "points is reduced to polyline_px. Storage compaction only; the "
                   "measured numbers (dist_m, src_disagree_px) use the unsimplified "
                   "points.", (1.0, 2.0, 4.0)),

    # ---- visibility ------------------------------------------------------ #
    "VIS_TOL_M": (0.15, "[임시-결재대기]",
                  "a 3D point counts as VISIBLE when |z_cam - rendered depth| <= this. "
                  "Context, not adoption: mainrun_0819 labeler.py used RIM_TOL_M = "
                  "0.35 m with a 3x3 window; this skeleton samples the nearest pixel "
                  "only, so the two are not interchangeable.",
                  (0.05, 0.15, 0.35)),

    # ---- route (b): depth discontinuity ---------------------------------- #
    "B_REL_JUMP": (0.05, "[임시-결재대기]",
                   "route (b) relative depth jump: an edge pixel needs "
                   "|dd| >= B_REL_JUMP * d. ONE global set for every frame and every "
                   "scene (brief §4 Phase 1-3: per-scene tuning launders the contrast).",
                   (0.02, 0.05, 0.10)),
    "B_ABS_JUMP_M": (0.10, "[임시-결재대기]",
                     "route (b) absolute floor on the same jump: "
                     "|dd| >= max(B_ABS_JUMP_M, B_REL_JUMP * d). Stops the relative "
                     "test from firing on near-field texture.",
                     (0.05, 0.10, 0.30)),
    "B_MIN_COMP_PX": (20, "[임시-결재대기]",
                      "route (b) minimum connected component length in pixels after "
                      "thinning.", (10, 20, 50)),
    "B_THIN_METHOD": ("Zhang-Suen 1984", "[문헌]",
                      "thinning of the route (b) jump mask. T. Y. Zhang & C. Y. Suen, "
                      "'A fast parallel algorithm for thinning digital patterns', "
                      "CACM 27(3):236-239, 1984 -- the published rule, no tunable "
                      "parameter. Implemented in e1_depth_edges.thin() rather than "
                      "imported: skimage is NOT importable under the repo-mandated "
                      "PYTHONNOUSERSITE=1 (measured), and a route-(b) constant may "
                      "not depend on whether a user-site package happens to be "
                      "visible.", None),
    "ZS_B_MIN": (2, "[문헌]",
                "Zhang-Suen condition (a) lower bound on the number of black "
                "8-neighbours. Published rule, part of B_THIN_METHOD.", None),
    "ZS_B_MAX": (6, "[문헌]",
                "Zhang-Suen condition (a) upper bound. Published rule.", None),
    "ZS_A_TARGET": (1, "[문헌]",
                   "Zhang-Suen condition (b): exactly one 0->1 transition around "
                   "the neighbourhood. Published rule.", None),
    "B_THIN_MAX_ITERS": (64, "[방법]",
                         "safety stop for the Zhang-Suen iteration. The algorithm "
                         "converges when no pixel changes; this only bounds a "
                         "pathological input, and the achieved iteration count is "
                         "printed in the route (b) diagnostics.", None),

    # ---- comparison (a) vs (b) ------------------------------------------- #
    "CMP_METHOD": ("nearest-point EDT", "[방법]",
                   "per instance: for every VISIBLE projected (a) point, the distance "
                   "in px to the nearest route-(b) edge pixel "
                   "(scipy.ndimage.distance_transform_edt on the complement of the "
                   "(b) mask). Reported as {mean, median, p90}; no pass line (brief "
                   "§4 Phase 1).", None),

    # ---- record dump ------------------------------------------------------ #
    "JSON_DECIMALS": (4, "[방법]",
                      "fixed decimal places in the canonical JSON dump. 4 dp = 0.1 mm "
                      "in metres and 1e-4 px -- below every sensor/geometry scale "
                      "here, and enough that a float never round-trips differently. "
                      "Determinism requirement, brief §4 Phase 1 통과수치.",
                      (3, 4, 6)),
    "JSON_SORT_KEYS": (True, "[방법]",
                       "sorted keys + '\\n' terminator + ensure_ascii=False, so two "
                       "runs of the same input are byte-identical.", None),

    # ---- occluder classification ----------------------------------------- #
    "PRIM_CLASS_RULES": ("code/prim_class_rules.json", "[임시-결재대기]",
                         "path->class table for the §2 rule 3 external-occluder test. "
                         "SHIPPED EMPTY ON PURPOSE: every blocking prim therefore "
                         "resolves to 'unknown', occluder.flag stays null and the "
                         "frame is routed to the unresolved list. Populating it is "
                         "결재 (❓B-4).", None),

    # ---- simple_edge.py: the SIMPLE labeler ------------------------------ #
    # Reuses DROP_MIN_M (0.30 [문헌·기존 확정]), R_RUN_M (1.0 [기존값]),
    # WALK_FLAT_TOL_M (0.10 [임시-결재대기], the spec's FLAT_TOL_M) and
    # RDP_TOL_PX (2.0 [방법]). Only what the simple labeler adds is below.
    "DEPTH_MAX_M": (60.0, "[방법]",
                    "depth pixels farther than this are dropped before the flat / "
                    "below tests, so the surface component cannot run to the horizon "
                    "and a 0.10 m flatness tolerance stays meaningful. Matches the "
                    "60 m probe top already used to build the heightmap "
                    "(variation_kit.AabbPrefilter.ground_z(top=60.0)).",
                    (30.0, 60.0, 120.0)),
    "EDGE_BRIDGE_PX": (5, "[방법]",
                       "the danger edge is dilated by this many 3x3 steps (Chebyshev "
                       "radius, px) before asking which below-the-drop components "
                       "touch it. The dilation exists to bridge the RISER, which "
                       "belongs to neither the standing surface nor the drop floor.",
                       (2, 5, 10)),
    "BRIDGE_SWEEP_PX": ([2, 5, 10, 20, 40, 80], "[방법]",
                        "EDGE_BRIDGE_PX values that --bridge-sweep re-runs the six "
                        "review frames at, so the effect of the running value on "
                        "mask_area_px is MEASURED and printed instead of argued. "
                        "Spans the ledger alternatives (2 / 5 / 10) and the pixel "
                        "scale a DROP_MIN_M riser actually subtends in this corpus "
                        "(32-80 px, measured). Report-only: the shipped labels always "
                        "use EDGE_BRIDGE_PX.", None),
    "MASK_VERSION_DEFAULT": ("v2_surfaces", "[방법]",
                             "which drop-mask definition simple_edge.py writes when "
                             "--mask is not given. 'v1_below' = every visible pixel "
                             "below ground_z - DROP_MIN_M whose image component "
                             "touches the dilated edge (the REJECTED definition: on "
                             "scene18 it painted the beach AND the sea to the "
                             "horizon). 'v2_surfaces' = the surfaces you would land "
                             "on -- the heightmap descent footprint plus the steep "
                             "faces attached to it. v1 stays reachable behind the "
                             "flag so the two can be regenerated side by side.",
                             ("v1_below", "v2_surfaces")),
    "RAMP_MAX_SLOPE": (1.0 / 12.0, "[문헌]",
                       "the steepest gradient a pedestrian surface may have and "
                       "still be a walking surface rather than a face you fall "
                       "against. VERIFIED SOURCE: 장애인·노인·임산부 등의 편의증진 "
                       "보장에 관한 법률 시행규칙 [별표 1] 제12호 나목 (1) -- "
                       "'경사로의 기울기는 12분의 1 이하로 하여야 한다' "
                       "(보건복지부령 제1166호, 시행 2026-07-02; text read from the "
                       "법제처 국가법령정보 Open API and cross-checked against the "
                       "official 별표1 PDF on law.go.kr). Same 별표 나목 (2) allows "
                       "1/8 only when THREE conditions all hold (existing "
                       "non-new-build, height <= 1 m AND structurally infeasible at "
                       "1/12, permanent staff assistance) -- an exception for "
                       "retrofits, so the labeler uses the 1/12 ceiling. Repo copy: "
                       "Docs/surveys/cue_arrangement_survey.md:144,148. This is the "
                       "ONLY slope number the simple labeler uses -- 'walkable "
                       "level' is at or under it and a 'steep face' is anything "
                       "over it, so there is no second, invented threshold. It "
                       "replaces the labeler's earlier use of WALK_FLAT_TOL_M, an "
                       "invented 0.10 m height tolerance that admitted the top "
                       "0.10 m of a vertical wall and put the sceneD2 danger line "
                       "10 cm down the trench face.", None),
    "LANDING_MIN_M": (1.20, "[문헌]",
                      "the shortest level plateau that counts as a LANDING rather "
                      "than a tread, and so ends a descent. VERIFIED SOURCE: "
                      "건축물의 피난·방화구조 등의 기준에 관한 규칙 제15조 제1항 "
                      "제1호 -- '높이가 3미터를 넘는 계단에는 높이 3미터이내마다 "
                      "유효너비 120센티미터 이상의 계단참을 설치할 것' "
                      "(국토교통부령 제1531호, 2025-10-31). PRECISION THE LEDGER "
                      "MUST CARRY: the statute's word is 유효너비, not 깊이; that "
                      "120 cm is the dimension ALONG THE DIRECTION OF TRAVEL is "
                      "법제처 법령해석 안건번호 24-0424 (2024-07-09), "
                      "'계단참의 유효너비란 계단의 진행방향으로서의 길이를 말하는 "
                      "것으로 전제함' -- an official interpretation adopted for that "
                      "case, not statutory wording. Repo copies: "
                      "Docs/surveys/korean_pedestrian_geometry.md:160,169 and "
                      "Docs/surveys/_dimension_index.md:18 (whose '주택단지 2 m' is "
                      "mis-attributed to the same 규칙; it is 주택건설기준 등에 관한 "
                      "규정 제16조 제2항 제1호, triggered at 높이 2 m). Context, not "
                      "the criterion: 편의증진법 시행규칙 별표1 제8호 다목 puts "
                      "디딤판 >= 0.28 m and 챌면 <= 0.18 m, so a tread can never "
                      "reach 1.20 m and a flight can never be mistaken for a "
                      "landing.", None),
    "OCCL_MARGIN_PCTL": (99, "[실측]",
                         "the occlusion test needs to know how far the rendered "
                         "depth may legitimately differ from the geometry before a "
                         "difference means 'something is standing in front'. That "
                         "number is NOT invented and NOT fixed: it is MEASURED per "
                         "frame as this percentile of |rendered depth - depth of "
                         "the plane z = ground_z| over the pixels of my_surface, "
                         "whose geometry is known exactly. The measured metres are "
                         "printed and stored per frame in meta.occlusion_margin_m; "
                         "only the percentile is fixed here, so one frame's sensor "
                         "noise cannot leak into another frame's decision. A frame "
                         "with no my_surface to measure on records 정할 수 없음 and "
                         "leaves its rim points undecided rather than guessing.",
                         None),
    "FOOTPRINT_CONN": (4, "[방법]",
                       "connectivity of the descent flood fill on the heightmap. 4 "
                       "(edge-adjacent) rather than 8: a fill that may cross at a "
                       "corner leaks through single-cell diagonal gaps in a rim, and "
                       "the footprint is meant to be where poured water would go.",
                       (4, 8)),
    "SHEET_V2_LABEL_PX": (34, "[방법]",
                          "scene-name text size on the v2 contact sheet. 22 px "
                          "(SHEET_LABEL_PX) is 3.4% of a 640 px tile and was not "
                          "readable at review distance. Cosmetic.", None),
    "SHEET_V2_MAX_MB": (1.0, "[방법]",
                        "size budget for sheet_v2.jpg; the achieved size is printed "
                        "and checked against it.", None),
    "CROP_ZOOM_PX": (480, "[방법]",
                     "side of the 1:1 (unscaled) crop used to show a rim corner at "
                     "full resolution on the v1-vs-v2 comparison sheet. Evidence "
                     "only; no label depends on it.", None),
    "RISER_MAX_M": (0.20, "[문헌]",
                    "the tallest single step that may still be a STAIR rather than "
                    "a cliff, used only to type an edge. VERIFIED SOURCE: 주택건설 "
                    "기준 등에 관한 규정 제16조 제1항 -- 건축물의 옥외계단 단높이 "
                    "20센티미터 이하 (공동으로 사용하는 계단은 18 이하). Repo copy, "
                    "checked verbatim against law.go.kr: "
                    "Docs/surveys/korean_pedestrian_geometry.md:186-191 and "
                    "Docs/surveys/_dimension_index.md:19. The OUTDOOR maximum is "
                    "used because this corpus is outdoor and it is the more "
                    "permissive of the two -- a legal outdoor flight must not be "
                    "typed as a cliff.", None),
    "EDGE_RGB_STAIR": ([255, 220, 0], "[방법·표시전용]",
                       "계단형 edge colour, 8-bit RGB (yellow).", None),
    "EDGE_RGB_DROPOFF": ([0, 255, 255], "[방법·표시전용]",
                         "절벽·단차형 edge colour, 8-bit RGB (cyan).", None),
    "EDGE_RGB_HOLE": ([255, 120, 0], "[방법·표시전용]",
                      "구멍·참호형 edge colour, 8-bit RGB (orange).", None),
    "EDGE_RGB_UNKNOWN": ([255, 255, 255], "[방법·표시전용]",
                         "colour of an edge whose type the ground profile does not "
                         "determine (white). Nothing is forced into a class.",
                         None),
    "SIMPLE_EDGE_HALO_RGB": ([0, 0, 0], "[방법·표시전용]",
                             "colour of the halo stroked under the rim line so cyan "
                             "reads on pale pavement as well as on dark water.",
                             None),
    "SIMPLE_EDGE_HALO_PX": (1, "[방법·표시전용]",
                            "how many pixels the halo extends beyond the rim line "
                            "on each side.", None),
    "SIMPLE_HIDDEN_LINE_PX": (2, "[방법·표시전용]",
                              "stroke width of the HIDDEN (occluded) rim, thinner "
                              "than the visible rim so the two never read alike.",
                              None),
    "SIMPLE_HIDDEN_DASH_PX": (6, "[방법·표시전용]",
                              "dash length of the hidden-rim dotted line.", None),
    "SIMPLE_HIDDEN_GAP_PX": (6, "[방법·표시전용]",
                             "gap length of the hidden-rim dotted line.", None),
    "SIMPLE_MASK_RGB": ([255, 0, 200], "[방법·표시전용]",
                        "drop-mask fill colour on the simple overlay. MAGENTA, far "
                        "enough from the cyan rim line to be separable at a glance.",
                        None),
    "SIMPLE_MASK_OUTLINE_RGB": ([110, 0, 90], "[방법·표시전용]",
                                "thin dark-magenta outline drawn on the drop mask so "
                                "its extent is readable over pale sand and pale "
                                "pavement alike.", None),
    "SIMPLE_MASK_ALPHA": (0.35, "[방법·표시전용]",
                          "opacity of the drop-mask fill, so the pavement texture "
                          "under it stays visible for judging. Cosmetic.", None),
    "SIMPLE_CAPTION_PX": (26, "[방법·표시전용]",
                          "caption text size on the simple overlay. The 18 px of "
                          "OVERLAY_FONT_PX was unreadable in the rejected smoke "
                          "overlay once scaled to a contact sheet. Cosmetic.", None),
    "SIMPLE_FONT_PATH": ("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
                         "[도구기본값]",
                         "the system Noto CJK face used for the overlay caption and "
                         "the contact-sheet labels; PIL's bitmap default is unreadable "
                         "at 1920 px. Falls back to load_default() if absent.", None),
    "SHEET_TILE_W_PX": (640, "[방법]",
                        "width of one contact-sheet tile in pixels; 3 x 640 = 1920 px "
                        "wide, which is one screen.", None),
    "SHEET_JPEG_QUALITY": (85, "[방법]",
                           "JPEG quality of the contact sheet. Cosmetic.", None),
    "SHEET_LABEL_PX": (22, "[방법]",
                       "scene-name text size printed above each contact-sheet tile. "
                       "Cosmetic.", None),
    "SHEET_BG_RGB": ([18, 18, 18], "[방법]",
                     "contact-sheet background, dark so the bright plaza tiles read "
                     "as separate panels. Cosmetic.", None),
    "SHEET_MAX_MB": (1.5, "[방법]",
                     "size budget for contact_sheet.jpg; the achieved size is "
                     "printed and checked against it.", None),
    "BYTES_PER_MB": (1048576, "[도구기본값]",
                     "1 MiB, the unit the printed file sizes use.", None),

    # ---- cosmetics / plumbing (no effect on any measured number) ---------- #
    "OVERLAY_LINE_PX": (3, "[방법]", "overlay stroke width. Cosmetic.", None),
    "OVERLAY_FONT_PX": (18, "[방법]", "overlay annotation text size. Cosmetic.", None),
    "OVERLAY_PALETTE": ([[255, 96, 0], [0, 200, 255], [255, 220, 0], [120, 255, 120],
                         [255, 120, 255], [120, 160, 255], [255, 255, 255],
                         [255, 60, 60]], "[방법]",
                        "per-instance overlay colours, 8-bit RGB. Cosmetic; chosen "
                        "to stay separable on both bright plaza and dark underpass "
                        "backgrounds.", None),
    "SORT_KEY_DECIMALS": (6, "[방법]",
                          "rounding applied ONLY to the sort key that fixes edge "
                          "instance order, so two runs cannot order two coincident "
                          "instances differently. Never touches a stored value.",
                          None),
    "PRINT_DP_FINE": (6, "[방법]", "console decimals for residual-scale numbers. "
                      "Console only.", None),
    "PRINT_DP_COARSE": (4, "[방법]", "console decimals for metre-scale numbers. "
                        "Console only.", None),
    "PRINT_DP_SHORT": (2, "[방법]", "console decimals for report lines. Console only.",
                       None),
    "CENSUS_TOP_N": (30, "[방법]", "how many blocking prims --prim-census prints. "
                     "The full census always goes to prim_blocker_census.json.",
                     None),
    "SENS_FRAME_COL": (28, "[방법]", "characters of the frame name printed in the "
                       "sensitivity table. Console only.", None),
    "SHA_PREFIX_LEN": (16, "[방법]", "hex characters kept from a sha256 when it is "
                       "printed as an identity. Console/manifest label only.", None),
}

# Values that may appear as bare literals anywhere in the e1 code without a
# ledger row: array indices, axis numbers, halving, percentile spellings and the
# 8-bit colour range. Anything else must come from CONSTANTS.
# 0..8 also cover the 8-neighbourhood indices P1..P9 used by the Zhang-Suen
# thinning; 90 is the percentile spelling, 100 a percent, 255 the 8-bit range.
STRUCTURAL_OK = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 90, 100, 255,
                 0.0, 1.0, 2.0, 0.5, 3.0, 1e-9, 1e-12}

# --------------------------------------------------------------------------- #
# access
# --------------------------------------------------------------------------- #
def value(key):
    return CONSTANTS[key][0]


def tag(key):
    return CONSTANTS[key][1]


def as_dict():
    return {k: v[0] for k, v in sorted(CONSTANTS.items())}


def fingerprint():
    """sha256 over the resolved constant table -- stamped into every manifest so a
    record can never be confused with one produced under a different set."""
    blob = json.dumps(as_dict(), sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:value("SHA_PREFIX_LEN")]


def sensitivity_plan():
    """[(key, running value, alternatives)] for every threshold that has one."""
    return [(k, v[0], v[3]) for k, v in sorted(CONSTANTS.items()) if v[3]]


# convenience module-level names (read-only by convention)
IMG_W = value("IMG_W")
IMG_H = value("IMG_H")
DEPTH_VALID_MIN_M = value("DEPTH_VALID_MIN_M")
CAM_FRONT_Z_MIN_M = value("CAM_FRONT_Z_MIN_M")
CAMCHK_STRIDE_PX = value("CAMCHK_STRIDE_PX")
CAMCHK_RADIUS_M = value("CAMCHK_RADIUS_M")
DROP_MIN_M = value("DROP_MIN_M")
R_RUN_M = value("R_RUN_M")
BREAK_LOCAL_FALL_M = value("BREAK_LOCAL_FALL_M")
EDGE_WINDOW_SHAPE = value("EDGE_WINDOW_SHAPE")
WALK_FOOT_R_M = value("WALK_FOOT_R_M")
WALK_FLAT_TOL_M = value("WALK_FLAT_TOL_M")
WALK_SUPPORT_FRAC = value("WALK_SUPPORT_FRAC")
MAX_TRAVERSE_STEP_M = value("MAX_TRAVERSE_STEP_M")
MIN_INSTANCE_LEN_M = value("MIN_INSTANCE_LEN_M")
REACH_ANCHOR_MODE = value("REACH_ANCHOR_MODE")
RDP_TOL_PX = value("RDP_TOL_PX")
INT_ASSIGN_INFRAME_ONLY = value("INT_ASSIGN_INFRAME_ONLY")
VIS_TOL_M = value("VIS_TOL_M")
B_REL_JUMP = value("B_REL_JUMP")
B_ABS_JUMP_M = value("B_ABS_JUMP_M")
B_MIN_COMP_PX = value("B_MIN_COMP_PX")
B_THIN_MAX_ITERS = value("B_THIN_MAX_ITERS")
ZS_B_MIN = value("ZS_B_MIN")
ZS_B_MAX = value("ZS_B_MAX")
ZS_A_TARGET = value("ZS_A_TARGET")
JSON_DECIMALS = value("JSON_DECIMALS")
OVERLAY_LINE_PX = value("OVERLAY_LINE_PX")
OVERLAY_FONT_PX = value("OVERLAY_FONT_PX")
OVERLAY_PALETTE = value("OVERLAY_PALETTE")
SORT_KEY_DECIMALS = value("SORT_KEY_DECIMALS")
PRINT_DP_FINE = value("PRINT_DP_FINE")
PRINT_DP_COARSE = value("PRINT_DP_COARSE")
PRINT_DP_SHORT = value("PRINT_DP_SHORT")
CENSUS_TOP_N = value("CENSUS_TOP_N")
SHA_PREFIX_LEN = value("SHA_PREFIX_LEN")
SENS_FRAME_COL = value("SENS_FRAME_COL")
DEPTH_MAX_M = value("DEPTH_MAX_M")
EDGE_BRIDGE_PX = value("EDGE_BRIDGE_PX")
BRIDGE_SWEEP_PX = value("BRIDGE_SWEEP_PX")
MASK_VERSION_DEFAULT = value("MASK_VERSION_DEFAULT")
FOOTPRINT_CONN = value("FOOTPRINT_CONN")
OCCL_MARGIN_PCTL = value("OCCL_MARGIN_PCTL")
RAMP_MAX_SLOPE = value("RAMP_MAX_SLOPE")
LANDING_MIN_M = value("LANDING_MIN_M")
SIMPLE_EDGE_HALO_RGB = value("SIMPLE_EDGE_HALO_RGB")
SIMPLE_EDGE_HALO_PX = value("SIMPLE_EDGE_HALO_PX")
SIMPLE_HIDDEN_LINE_PX = value("SIMPLE_HIDDEN_LINE_PX")
SIMPLE_HIDDEN_DASH_PX = value("SIMPLE_HIDDEN_DASH_PX")
SIMPLE_HIDDEN_GAP_PX = value("SIMPLE_HIDDEN_GAP_PX")
SHEET_V2_LABEL_PX = value("SHEET_V2_LABEL_PX")
SHEET_V2_MAX_MB = value("SHEET_V2_MAX_MB")
CROP_ZOOM_PX = value("CROP_ZOOM_PX")
RISER_MAX_M = value("RISER_MAX_M")
EDGE_RGB_STAIR = value("EDGE_RGB_STAIR")
EDGE_RGB_DROPOFF = value("EDGE_RGB_DROPOFF")
EDGE_RGB_HOLE = value("EDGE_RGB_HOLE")
EDGE_RGB_UNKNOWN = value("EDGE_RGB_UNKNOWN")
SIMPLE_MASK_RGB = value("SIMPLE_MASK_RGB")
SIMPLE_MASK_OUTLINE_RGB = value("SIMPLE_MASK_OUTLINE_RGB")
SIMPLE_MASK_ALPHA = value("SIMPLE_MASK_ALPHA")
SIMPLE_CAPTION_PX = value("SIMPLE_CAPTION_PX")
SIMPLE_FONT_PATH = value("SIMPLE_FONT_PATH")
SHEET_TILE_W_PX = value("SHEET_TILE_W_PX")
SHEET_JPEG_QUALITY = value("SHEET_JPEG_QUALITY")
SHEET_LABEL_PX = value("SHEET_LABEL_PX")
SHEET_BG_RGB = value("SHEET_BG_RGB")
SHEET_MAX_MB = value("SHEET_MAX_MB")
BYTES_PER_MB = value("BYTES_PER_MB")

HM_SOURCE_NOTE = (
    "heightmap.npy = variation_kit.AabbPrefilter.ground_z(top=60.0): the first "
    "downward hit on the world AABB set. It is an ENVELOPE, not the mesh: for "
    "box-major scenes heightmap_meta.aabb_grid reports worst_abs 0.0, but a "
    "railing / parapet / roof contributes its own AABB top, and a floor opening "
    "spanned by a box AABB is NOT dug out. Both are measured facts about the "
    "corpus, not bugs in this code -- see reports/P0_CODE_SKELETON.md §4."
)
