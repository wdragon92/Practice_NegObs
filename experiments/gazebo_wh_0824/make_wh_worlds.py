#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_wh_worlds.py -- LIGHT asset variants of the PAPER'S OWN warehouse world.

SOURCE (read-only, never written):
    Baseline_NegObs/src/negativeobstacleavoidandance/bumperbot_description/worlds/
        smallest_world.world          <- gazebo.launch.py's default world_name

WHAT THIS DOES
    Reads that file as TEXT and re-emits it with a small block of extra <model>
    elements spliced in immediately before the ceiling light.  Nothing in the
    paper's own text is edited, deleted or reordered -- every AWS RoboMaker asset,
    the warehouse wall, the ceiling light, <scene>, <physics> and the whole
    <state> block come through byte-identical.  The only bytes we add are:

      (a) the camera rig  -- 7 approach cameras + 1 overview, IDENTICAL in all four
          worlds, so it is instrumentation, not a variant difference;
      (b) 0-2 primitive <box> models per variant (the actual variation).

THE HAZARD
    The paper's negative obstacle is `large_holed_floor` -- a thin (0.1243 m) floor
    plate with square openings cut through it and NO ground plane underneath.  The
    world's <state> puts that plate at (-0.05136, 0.198655, 0, yaw 3.13572).  Under
    that pose the largest clean opening inside the warehouse is

        x in [-4.280, -3.480]   y in [-1.370, -0.570]    (0.800 x 0.800 m, 99.1% rect)

    measured by rasterising the up-facing triangles of large_holed_floor.stl at 1 cm.
    We approach it along y = -0.970 from +x, i.e. the near rim is at x = -3.480.

THE CAMERA
    Deliberately the paper's own robot camera, so the frames are in the detector's
    training distribution:  RealSense D435 sim, 1280x720, hfov 1.2043 rad,
    pitch 0.261 rad nose-down, eye height 0.125 m
    (= base_footprint->base_link 0.033 + realsense_joint z 0.092; see
    bumperbot.urdf.xacro:41,220-224 and realsense2.urdf.xacro).

VARIANTS  (see worlds/WORLD_DIFFS.md for the emitted per-file diff summary)
    wh0    control -- paper's world verbatim + rig.                       0 boxes
    wh_e   edge-only -- a pallet plate laid over the far 0.62 m of the
           opening; only a 0.18 m strip of void survives at the near rim. +1 box
    wh_h   hidden -- a 0.45 m stack of pallets parked at the near rim;
           from every approach pose the opening contributes 0 px.         +1 box
    wh_hc  hazard-removed twin of wh_h -- same stack, PLUS a floor patch
           that fills the opening flush with the plate.                   +2 boxes

usage:  python3 make_wh_worlds.py [--outdir worlds]
"""
from __future__ import annotations

import argparse
import hashlib
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = "/home/vislab/Desktop/work_sy/Baseline_NegObs"
SRC_WORLD = os.path.join(
    BASE, "src/negativeobstacleavoidandance/bumperbot_description/worlds/smallest_world.world")

# ---------------------------------------------------------------- hazard geometry (measured)
HOLE_X0, HOLE_X1 = -4.280, -3.480
HOLE_Y0, HOLE_Y1 = -1.370, -0.570
FLOOR_TOP_Z = 0.1243                 # large_holed_floor.stl top surface
APPROACH_Y = 0.5 * (HOLE_Y0 + HOLE_Y1)   # -0.970
NEAR_RIM_X = HOLE_X1                     # -3.480

# ---------------------------------------------------------------- camera rig (paper's D435)
HFOV_RS = 1.2043
PITCH_RS = 0.261
RES_RS = (1280, 720)
RS_EYE_H = 0.125                     # eye height ABOVE THE WALKING SURFACE
# ...and the walking surface in THIS world is the top of large_holed_floor, not z = 0.
# The robot's base_footprint rests on the plate, so the camera's WORLD z is plate + 0.125.
# (Getting this wrong puts the camera 0.7 mm above the floor and every frame is a smear --
#  observed on the first wh0 capture, corrected here.)
RS_EYE_Z = FLOOR_TOP_Z + RS_EYE_H
# Standoff of the camera from the NEAR RIM, metres.
# The paper's node defines its OWN operating window and it is very short: the
# trapezium ROI of clean_yolo.py starts at image row 0.3*H = 216, which for this
# camera (eye 0.125 m, 15 deg down, f 931 px) is ground distance
#     D = 0.125 / tan(15 deg - atan(144/931)) = 1.15 m.
# Anything farther than ~1.15 m is masked to black BEFORE YOLO sees it.  So the
# "typical operating distance" band is 0.5-1.1 m (inside its own ROI) and 1.5-3.4 m
# is the outside band we keep as the closer/farther controls.
STANDOFFS = (0.5, 0.7, 0.9, 1.1, 1.5, 2.0, 2.6, 3.4)


def build_cameras(keep=None):
    """-> [dict].  `key` is the ROS namespace token (no dots); `view` names the file."""
    cams = []
    for d in STANDOFFS:
        cams.append(dict(
            key="d%s" % ("%g" % d).replace(".", ""),      # d12, d15, ...
            view="rs_d%g" % d,                            # rs_d1.2
            x=NEAR_RIM_X + d, y=APPROACH_Y, z=RS_EYE_Z, h_agl=RS_EYE_H,
            pitch=PITCH_RS, yaw=math.pi, hfov=HFOV_RS, res=RES_RS,
            family="approach", standoff=d))
    # Diagnostic only -- excluded from every headline population (documented in
    # WAREHOUSE_VARIANT.md).  It exists to SHOW the hazard and the variant edit in
    # one frame, and to prove the <state> pose hypothesis for large_holed_floor.
    cams.append(dict(
        key="ov", view="overview",
        x=-2.0, y=APPROACH_Y, z=7.0, h_agl=7.0 - FLOOR_TOP_Z,
        pitch=1.40, yaw=math.pi, hfov=1.9, res=(1280, 720),
        family="overview", standoff=None))
    if keep:
        want = {k.strip() for k in keep}
        cams = [c for c in cams if c["key"] in want or c["view"] in want]
    return cams


# ---------------------------------------------------------------- SDF emitters
def _pose(x, y, z, r=0.0, p=0.0, yw=0.0):
    return f"{x:.6g} {y:.6g} {z:.6g} {r:.6g} {p:.6g} {yw:.6g}"


def box_model(name, cx, cy, cz, sx, sy, sz, material, comment=""):
    c = f"    <!-- {comment} -->\n" if comment else ""
    return f"""{c}    <model name="{name}">
      <static>true</static>
      <pose>{_pose(cx, cy, cz)}</pose>
      <link name="link">
        <collision name="c">
          <geometry><box><size>{sx:.6g} {sy:.6g} {sz:.6g}</size></box></geometry>
          <surface><friction><ode><mu>1</mu><mu2>1</mu2></ode></friction></surface>
        </collision>
        <visual name="v">
          <geometry><box><size>{sx:.6g} {sy:.6g} {sz:.6g}</size></box></geometry>
          <material><script><uri>file://media/materials/scripts/gazebo.material</uri>
            <name>{material}</name></script></material>
        </visual>
      </link>
    </model>
"""


def camera_model(cam):
    w, h = cam["res"]
    ns = f"/gzcam/{cam['key']}"
    return f"""    <model name="cam_{cam['key']}">
      <static>true</static>
      <pose>{_pose(cam['x'], cam['y'], cam['z'], 0.0, cam['pitch'], cam['yaw'])}</pose>
      <link name="link">
        <sensor name="{cam['key']}" type="camera">
          <camera name="{cam['key']}">
            <horizontal_fov>{cam['hfov']:.6f}</horizontal_fov>
            <image><width>{w}</width><height>{h}</height><format>R8G8B8</format></image>
            <clip><near>0.05</near><far>150</far></clip>
          </camera>
          <always_on>0</always_on>
          <update_rate>1.0</update_rate>
          <visualize>0</visualize>
          <plugin name="plug_{cam['key']}" filename="libgazebo_ros_camera.so">
            <ros><namespace>{ns}</namespace></ros>
            <camera_name>cam</camera_name>
            <frame_name>gzcam_{cam['key']}_optical</frame_name>
            <hack_baseline>0.0</hack_baseline>
          </plugin>
        </sensor>
      </link>
    </model>
"""


# ---------------------------------------------------------------- the variant edits
# Every dimension below is a EUR-pallet-scale warehouse object (1.20 x 0.80 m footprint)
# so that the addition is plausible for THIS environment; no new mesh/asset file is
# introduced and no existing asset, light or material is touched.
PALLET_STACK = dict(                       # wh_h / wh_hc occluder
    name="wh_pallet_stack",
    sx=0.30, sy=1.20, sz=0.45,
    cx=NEAR_RIM_X + 0.15,                  # -3.33  -> spans x [-3.48, -3.18], flush with the rim
    cy=APPROACH_Y,
    material="Gazebo/Wood",
    comment="WH-H: three stacked pallets parked at the near rim of the opening. "
            "0.45 m tall vs a 0.125 m eye height -> the opening subtends 0 px from "
            "every approach pose.")
PALLET_COVER = dict(                       # wh_e cover
    name="wh_pallet_cover",
    sx=0.62, sy=1.20, sz=0.144,
    cx=HOLE_X0 + 0.31,                     # -3.97 -> spans x [-4.28, -3.66]
    cy=APPROACH_Y,
    material="Gazebo/Wood",
    comment="WH-E: one pallet laid over the FAR 0.62 m of the 0.80 m opening, resting "
            "on the plate at both y overhangs.  A 0.18 m strip of void survives at the "
            "near rim -> the drop is present as an EDGE only.")
FLOOR_PATCH = dict(                        # wh_hc hazard removal
    name="wh_floor_patch",
    sx=0.90, sy=0.90, sz=FLOOR_TOP_Z,
    cx=0.5 * (HOLE_X0 + HOLE_X1),
    cy=APPROACH_Y,
    material="Gazebo/Grey",
    comment="WH-Hc: fills the opening flush with the floor plate (top at z=0.1243). "
            "This is the ONLY difference from wh_h -- the hazard is gone, the scene is not.")


def _b(spec):
    z = spec["sz"] / 2.0 if spec["name"] == "wh_floor_patch" else FLOOR_TOP_Z + spec["sz"] / 2.0
    return box_model(spec["name"], spec["cx"], spec["cy"], z,
                     spec["sx"], spec["sy"], spec["sz"], spec["material"], spec["comment"])


VARIANTS = {
    "wh0":   dict(boxes=[],                             tier="control (V, as published)"),
    "wh_e":  dict(boxes=[PALLET_COVER],                 tier="E (edge-only)"),
    "wh_h":  dict(boxes=[PALLET_STACK],                 tier="H (hidden)"),
    "wh_hc": dict(boxes=[PALLET_STACK, FLOOR_PATCH],    tier="H-ctrl (hazard removed twin of wh_h)"),
}

ANCHOR = "    <light name='Warehouse_CeilingLight_003' type='point'>"


def sha16(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()[:16]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default=os.path.join(HERE, "worlds"))
    ap.add_argument("--cams", default="")
    a = ap.parse_args(argv)
    os.makedirs(a.outdir, exist_ok=True)

    src = open(SRC_WORLD, "r").read()
    if ANCHOR not in src:
        raise SystemExit("[fatal] anchor not found -- the source world changed?")
    cams = build_cameras([c for c in a.cams.split(",") if c.strip()] or None)

    rig = "".join(camera_model(c) for c in cams)
    lines = []
    for name, spec in VARIANTS.items():
        add = (f"\n    <!-- ================= ADDED BY make_wh_worlds.py ({name}) ================= -->\n"
               f"    <!-- instrumentation: {len(cams)} static cameras, identical in all 4 worlds -->\n"
               + rig)
        for spec_box in spec["boxes"]:
            add += "\n" + _b(spec_box)
        add += "    <!-- ======================= END ADDED BLOCK ======================= -->\n\n"
        out = src.replace(ANCHOR, add + ANCHOR, 1)
        p = os.path.join(a.outdir, name + ".world")
        with open(p, "w") as f:
            f.write(out)
        n_added = len(add.splitlines())
        lines.append((name, spec["tier"], len(spec["boxes"]), n_added, sha16(p),
                      os.path.getsize(p)))
        print(f"[make_wh_worlds] {p}  (+{n_added} lines, {len(spec['boxes'])} box models)")

    # ------------------------------------------------------------ diff summary doc
    md = ["# WORLD_DIFFS -- what each variant changes, line by line",
          "",
          f"source (read-only): `{SRC_WORLD}`",
          f"source sha256[:16]: `{sha16(SRC_WORLD)}`  ({os.path.getsize(SRC_WORLD)} bytes, "
          f"{len(src.splitlines())} lines)",
          "",
          "Every variant is produced by ONE text splice: a block inserted immediately before",
          "`<light name='Warehouse_CeilingLight_003'>`.  Nothing else in the paper's file is",
          "touched -- `diff` against the source shows a single added hunk and zero deletions.",
          "",
          "## measured hazard (from large_holed_floor.stl, 1 cm raster, state pose applied)",
          "",
          f"| opening | x [{HOLE_X0}, {HOLE_X1}] | y [{HOLE_Y0}, {HOLE_Y1}] | "
          f"{HOLE_X1-HOLE_X0:.2f} x {HOLE_Y1-HOLE_Y0:.2f} m | plate top z = {FLOOR_TOP_Z} |",
          "|---|---|---|---|---|",
          f"| approach | y = {APPROACH_Y:.3f} | looking -x (yaw pi) | near rim x = {NEAR_RIM_X} | |",
          "",
          "## camera rig (identical in all four worlds -- instrumentation, not a variant)",
          "",
          "| view | key | eye (x,y,z) | standoff from near rim | pitch | hfov | res |",
          "|---|---|---|---|---|---|---|"]
    for c in cams:
        so = "-" if c["standoff"] is None else f"{c['standoff']:.1f} m"
        md.append(f"| `{c['view']}` | `{c['key']}` | ({c['x']:.3f}, {c['y']:.3f}, {c['z']:.3f}) | "
                  f"{so} | {math.degrees(c['pitch']):.1f} deg down | "
                  f"{math.degrees(c['hfov']):.2f} deg | {c['res'][0]}x{c['res'][1]} |")
    md += ["",
           "The approach cameras copy the paper's own robot camera verbatim "
           "(RealSense D435 sim: 1280x720, hfov 1.2043 rad, 0.261 rad nose-down, eye 0.125 m).",
           "",
           "## per-variant added geometry",
           "",
           "| world | tier | box models added | added lines | sha256[:16] |",
           "|---|---|---|---|---|"]
    for name, tier, nb, nl, sh, sz in lines:
        md.append(f"| `{name}.world` | {tier} | {nb} | {nl} | `{sh}` |")
    md += ["", "### box specs", "",
           "| model | world(s) | size (x,y,z) m | centre (x,y,z) m | material | why |",
           "|---|---|---|---|---|---|"]
    for spec, worlds in ((PALLET_COVER, "wh_e"),
                         (PALLET_STACK, "wh_h, wh_hc"),
                         (FLOOR_PATCH, "wh_hc")):
        z = spec["sz"] / 2.0 if spec["name"] == "wh_floor_patch" else FLOOR_TOP_Z + spec["sz"] / 2.0
        md.append(f"| `{spec['name']}` | {worlds} | "
                  f"{spec['sx']:.2f}, {spec['sy']:.2f}, {spec['sz']:.4g} | "
                  f"{spec['cx']:.3f}, {spec['cy']:.3f}, {z:.4f} | {spec['material']} | "
                  f"{spec['comment']} |")
    md += ["",
           "**Unchanged in every variant**: the floor plate and its pose, all 24 AWS RoboMaker",
           "warehouse assets and their poses, `aws_robomaker_warehouse_WallB_01_001`, the single",
           "`Warehouse_CeilingLight_003` point light (pose 0 0 9, diffuse 0.5), `<scene>` ambient",
           "0.4 / background 0.7 / shadows 1, `<physics>`, and the whole `<state>` block.",
           ""]
    with open(os.path.join(a.outdir, "WORLD_DIFFS.md"), "w") as f:
        f.write("\n".join(md))
    print(f"[make_wh_worlds] wrote {os.path.join(a.outdir, 'WORLD_DIFFS.md')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
