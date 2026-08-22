#!/usr/bin/env python3
"""Generate the weekend_0823 Gazebo Classic drop-off worlds (CPU only, no sim launched).

Emits eight SDF 1.6 worlds into ./worlds/ -- four hazards, each with its twin control.
Between them they cover all three visibility tiers (see worlds/README.md §8):

    gz_drop1.world       [V] descending stair into a sunken pit, 4 x 0.18 m = 0.72 m drop
    gz_drop2.world       [V] platform edge, sheer 0.80 m drop, guard rail on the +Y side only
    gz_drop3.world       [H] 0.72 m pit hidden behind a 0.61 m planter; cues stay visible
    gz_drop4.world       [E] 0.25 x 1.00 m open trench, 0.70 m deep; rim seen, interior not
    gz_drop*_ctrl.world  twin controls -- hazard geometry removed, ALL dressing kept

Design rules (why the files look the way they do)
-------------------------------------------------
1. NO `<include>`, NO `model://`, NO meshes.  `bumperbot_description/launch/gazebo.launch.py`
   *overwrites* GAZEBO_MODEL_PATH with its own models dir, so anything we reference by URI
   would have to live inside the read-only baseline repo.  Every body here is an inline
   box/cylinder with a stock `Gazebo/*` material from /usr/share/gazebo-11.  The worlds are
   therefore loadable by ANY gzserver on this machine, with or without the baseline env.

2. Twin invariant (project doctrine, "신off" generation -- see
   experiments/nightrun_0820/ctrl_dressing/README.md).  Camera poses, lighting, and every
   dressing element (guard rails, tactile warning strip, flanking walls) are byte-identical
   between the hazard arm and its ctrl arm.  ONLY the hazard geometry toggles.  That is why
   every rail post foot sits on the upper deck at z = 0 and never on a step: a post standing
   on a tread would have to move when the tread disappears, which would break the invariant.

3. Camera presets reproduce `scene_common.grid_views()` exactly:
       eye = (x_lip - d, 0, h),  pitch = -10 deg,  hFOV = 60.00 deg,  1920 x 1080
   with h in {0.3, 0.9} and d in {2, 5, 10} m.  In the Isaac corpus the drop-start edge is
   x = 0 and the eye is at x = -d; here the whole scene is shifted by X_LIP = +12 m so that
   the bumperbot's hard-coded spawn point (0, 0, 0.15) sits BEHIND the farthest camera
   (x = 2.0) and never enters a frame.

4. Two extra "rs" cameras reproduce the baseline bumperbot's own RealSense-sim optics
   (hFOV 69.0 deg, 1280x720, 15 deg down-pitch, 0.125 m eye height) for the stage-e
   YOLO-on-the-same-scene comparison.

Usage
-----
    python3 make_worlds.py                 # regenerate all eight worlds
    python3 make_worlds.py --outdir /tmp/x # elsewhere
    python3 make_worlds.py --cams h0.3_d2,h0.9_d5   # fewer cameras (lighter GPU load)

Nothing here imports ROS, Gazebo, or torch -- it is pure stdlib string building.
"""
from __future__ import annotations

import argparse
import math
import os

# --------------------------------------------------------------------------- global geometry
X_LIP = 12.0          # world x of the drop-start edge (corpus convention: x = 0, shifted +12)
NOTCH_HY = 1.10       # half-width of the stair notch in gz_drop1 (2.20 m wide stair)
DECK_HY = 8.0         # half-width of the upper deck
DECK_X0 = -16.0       # deck starts here (behind the robot spawn at x = 0)
FAR_X = 120.0         # ground runs this far so the horizon is GROUND, not background sky.
                      # At h0.3/d10 the sight line only reaches the lower level 24 m past the
                      # lip; a short apron would put sky where ground belongs and hand the
                      # network an artefact instead of a cue.
DECK_T = 1.5          # deck slab thickness (must reach below the pit floor)

RISE = 0.18           # stair riser
TREAD = 0.30          # stair tread depth
N_RISERS = 4          # 4 x 0.18 = 0.72 m total drop  (>= 0.6 m required)
DROP1 = RISE * N_RISERS
DROP2 = 0.80          # gz_drop2 sheer platform edge

RAIL_Y = 1.30         # guard rail line (just outside the notch, so posts stand on the deck)
RAIL_X0, RAIL_X1 = 8.0, X_LIP     # rail run along the approach, terminating at the lip
RAIL_TOP_Z = 1.05
RAIL_MID_Z = 0.55
RAIL_POST_H = 1.10
RAIL_R = 0.035
POST_R = 0.030

WALL_Y = 3.5          # flanking walls (horizon / perspective reference), deck region only
WALL_H = 2.5
WALL_T = 0.20

STRIP_X0, STRIP_X1 = X_LIP - 0.30, X_LIP   # tactile warning-block strip, flush to the lip
STRIP_HY = NOTCH_HY

# --- gz_drop3 (H composition) -------------------------------------------------------------
# A planter/parapet standing ON THE DECK in front of the lip.  Its top must clear h0.3 (so
# the sight line RISES past it and nothing at or below ground is ever seen again) and must
# still sit low enough under h0.9 that the descending sight line has not reached z = 0 by the
# far side of the pit.  0.55 body + 0.06 planting cap = 0.61 m satisfies both -- see the
# derivation table in worlds/README.md §8.2.
D3_PIT_X0, D3_PIT_X1 = X_LIP, 15.0      # pit is SHORT on purpose: the far wall must stay
D3_PIT_HY = 0.90                        # inside the occluder's shadow at h0.9/d2
D3_DROP = 0.72
D3_OCC_X0, D3_OCC_X1 = 11.60, X_LIP     # planter footprint, far face flush with the lip
D3_OCC_HY = 1.10                        # wider than the pit -> no lateral leak (README §8.2)
D3_OCC_BODY_H = 0.55
D3_OCC_CAP_H = 0.06
D3_STRIP_X0, D3_STRIP_X1 = 11.30, 11.60  # warning strip IN FRONT of the planter (camera side)

# --- gz_drop4 (E composition) -------------------------------------------------------------
# Visible far-wall band = W*h/d; int_px (labeler counts on a DS=4 depth map, TAU_INT_DEF=50)
#   int_px_DS = (W*h/d) * L / (R^2 * 5.0742e-6),   R = d + W
# so E needs a SMALL opening area.  0.25 m along X x 1.00 m across = an open expansion joint
# / missing grating strip: 14 px at h0.3_d10 and 42 px at h0.9_d10, both under 50.
D4_W = 0.25                             # trench extent ALONG the walking direction
D4_HY = 0.50                            # half of the 1.00 m lateral opening
D4_DROP = 0.70
D4_STRIP_X0, D4_STRIP_X1 = 11.40, 11.70  # set back 0.30 m from the lip -- see warning_strip_model

MAT_DECK = "Gazebo/Grey"
MAT_PIT = "Gazebo/DarkGrey"
MAT_STEP = "Gazebo/Grey"
MAT_RAIL = "Gazebo/White"
MAT_WALL = "Gazebo/PaintedWall"
MAT_OCC = "Gazebo/Bricks"
MAT_OCC_CAP = "Gazebo/Grass"
MAT_STRIP = "Gazebo/Yellow"
MAT_DOT = "Gazebo/ZincYellow"

# --------------------------------------------------------------------------- camera presets
HFOV_NEGOBS = math.radians(60.00)   # Isaac default persp: focal 18.14756 / aperture 20.955
PITCH_NEGOBS = math.radians(10.0)   # SDF +pitch = nose DOWN;  corpus preset pitch = -10 deg
RES_NEGOBS = (1920, 1080)

HFOV_RS = 1.2043                    # baseline realsense2.urdf.xacro, verbatim
PITCH_RS = 0.261                    # baseline realsense_joint rpy, verbatim
RES_RS = (1280, 720)
RS_EYE_Z = 0.125                    # base_footprint->base_link 0.033 + realsense_joint 0.092


def build_cameras(keep=None):
    """-> list of dicts.  `key` is the ROS namespace token; `view` is the corpus view name."""
    cams = []
    for h in (0.3, 0.9):
        for d in (2, 5, 10):
            cams.append(dict(
                key=f"h{str(h).replace('.', '')}_d{d}",          # h03_d2  (ROS-legal, no dot)
                view=f"preset_h{h}_d{d}",                         # preset_h0.3_d2 (corpus name)
                x=X_LIP - d, y=0.0, z=h,
                pitch=PITCH_NEGOBS, hfov=HFOV_NEGOBS, res=RES_NEGOBS,
                family="negobs"))
    # Not a corpus preset: the three standoffs above put the lip in grid-V1 bands 2/3/4 and
    # NEVER in band 1 = [0, 2) m.  d = 1.2 m is the training sampler's near limit
    # (CAM_CONVENTION.md: d ~ LogU(1.2, 12.0)) and is the only cut that exercises band 1.
    cams.append(dict(
        key="h03_d12", view="extra_h0.3_d1.2",
        x=X_LIP - 1.2, y=0.0, z=0.3,
        pitch=PITCH_NEGOBS, hfov=HFOV_NEGOBS, res=RES_NEGOBS, family="negobs"))
    for d in (2, 5):
        cams.append(dict(
            key=f"rs_d{d}", view=f"rs_h0.125_d{d}",
            x=X_LIP - d, y=0.0, z=RS_EYE_Z,
            pitch=PITCH_RS, hfov=HFOV_RS, res=RES_RS,
            family="rs"))
    if keep:
        want = {k.strip() for k in keep}
        cams = [c for c in cams if c["key"] in want or c["view"] in want
                or c["view"].replace("preset_", "") in want]
    return cams


# --------------------------------------------------------------------------- SDF emitters
def _pose(x, y, z, r=0.0, p=0.0, yw=0.0):
    return f"{x:.6g} {y:.6g} {z:.6g} {r:.6g} {p:.6g} {yw:.6g}"


def box_model(name, cx, cy, cz, sx, sy, sz, material, collision=True):
    col = ""
    if collision:
        col = f"""
        <collision name="c">
          <geometry><box><size>{sx:.6g} {sy:.6g} {sz:.6g}</size></box></geometry>
          <surface><friction><ode><mu>1.0</mu><mu2>1.0</mu2></ode></friction></surface>
        </collision>"""
    return f"""
    <model name="{name}">
      <static>true</static>
      <pose>{_pose(cx, cy, cz)}</pose>
      <link name="link">{col}
        <visual name="v">
          <geometry><box><size>{sx:.6g} {sy:.6g} {sz:.6g}</size></box></geometry>
          <material><script><uri>file://media/materials/scripts/gazebo.material</uri>
            <name>{material}</name></script></material>
        </visual>
      </link>
    </model>"""


def _cyl_visual(vname, r, ln, cx, cy, cz, rr, pp, yy, material, collision):
    col = ""
    if collision:
        col = f"""
        <collision name="c_{vname}">
          <pose>{_pose(cx, cy, cz, rr, pp, yy)}</pose>
          <geometry><cylinder><radius>{r:.6g}</radius><length>{ln:.6g}</length></cylinder></geometry>
        </collision>"""
    return col + f"""
        <visual name="{vname}">
          <pose>{_pose(cx, cy, cz, rr, pp, yy)}</pose>
          <geometry><cylinder><radius>{r:.6g}</radius><length>{ln:.6g}</length></cylinder></geometry>
          <material><script><uri>file://media/materials/scripts/gazebo.material</uri>
            <name>{material}</name></script></material>
        </visual>"""


def rail_model(name, segments, material=MAT_RAIL, collision=True):
    """segments: list of (radius, length, cx, cy, cz, roll, pitch, yaw) in world coords."""
    parts = []
    for i, (r, ln, cx, cy, cz, rr, pp, yy) in enumerate(segments):
        parts.append(_cyl_visual(f"s{i}", r, ln, cx, cy, cz, rr, pp, yy, material, collision))
    return f"""
    <model name="{name}">
      <static>true</static>
      <pose>0 0 0 0 0 0</pose>
      <link name="link">{''.join(parts)}
      </link>
    </model>"""


AX_X = (0.0, math.pi / 2, 0.0)      # cylinder axis -> +X
AX_Y = (math.pi / 2, 0.0, 0.0)      # cylinder axis -> +Y
AX_Z = (0.0, 0.0, 0.0)              # cylinder axis -> +Z (default)


def guard_rail_segments(y, x0, x1, *, return_leg=None):
    """A post-and-two-rail guard running along +X at lateral offset `y`.

    Every post foot is at z = 0 (upper deck) -- see design rule 2.
    `return_leg` = (x, y_from, y_to) adds an L-shaped return along the lip.
    """
    segs = []
    n_post = int(round(x1 - x0)) + 1
    for i in range(n_post):
        px = x0 + i * (x1 - x0) / (n_post - 1)
        segs.append((POST_R, RAIL_POST_H, px, y, RAIL_POST_H / 2.0, *AX_Z))
    ln = (x1 - x0) + 0.10
    cx = (x0 + x1) / 2.0
    for z in (RAIL_TOP_Z, RAIL_MID_Z):
        segs.append((RAIL_R, ln, cx, y, z, *AX_X))
    if return_leg is not None:
        rx, ya, yb = return_leg
        segs.append((POST_R, RAIL_POST_H, rx, yb, RAIL_POST_H / 2.0, *AX_Z))
        lny = abs(ya - yb) + 0.10
        cy = (ya + yb) / 2.0
        for z in (RAIL_TOP_Z, RAIL_MID_Z):
            segs.append((RAIL_R, lny, rx, cy, z, *AX_Y))
    return segs


def warning_strip_model(name, x0=None, x1=None, hy=None):
    """Tactile paving strip: one yellow base slab + a grid of raised dots.

    All of it lives in ONE link as many <visual> elements (cheap; no collision needed --
    the slab is 6 mm and the robot drives over it).

    x0/x1 default to flush-with-the-lip.  gz_drop4 sets them back by 0.30 m on purpose: a
    6 mm proud slab sitting ON the lip becomes the binding silhouette for a grazing camera
    and shrinks the visible far-wall band ~5x, which would make that world's E tier an
    artefact of the paving rather than of the trench geometry.
    """
    x0 = STRIP_X0 if x0 is None else x0
    x1 = STRIP_X1 if x1 is None else x1
    hy = STRIP_HY if hy is None else hy
    vis = [f"""
        <visual name="slab">
          <pose>{_pose((x0 + x1) / 2.0, 0.0, 0.003)}</pose>
          <geometry><box><size>{x1 - x0:.6g} {2 * hy:.6g} 0.006</size></box></geometry>
          <material><script><uri>file://media/materials/scripts/gazebo.material</uri>
            <name>{MAT_STRIP}</name></script></material>
        </visual>"""]
    xs = [x0 + 0.05, (x0 + x1) / 2.0, x1 - 0.05]
    ys = [-1.00 + 0.125 * i for i in range(17)]
    k = 0
    for x in xs:
        for y in ys:
            vis.append(f"""
        <visual name="d{k}">
          <pose>{_pose(x, y, 0.010)}</pose>
          <geometry><box><size>0.05 0.05 0.008</size></box></geometry>
          <material><script><uri>file://media/materials/scripts/gazebo.material</uri>
            <name>{MAT_DOT}</name></script></material>
        </visual>""")
            k += 1
    return f"""
    <model name="{name}">
      <static>true</static>
      <pose>0 0 0 0 0 0</pose>
      <link name="link">{''.join(vis)}
      </link>
    </model>"""


def camera_model(cam):
    w, h = cam["res"]
    ns = f"/gzcam/{cam['key']}"
    # A `depth` sensor publishes BOTH the colour image and a 32FC1 metric depth image from
    # one plugin, so --depth costs one sensor, not two.  polar_dataset.load_depth_m() eats
    # float32 metres straight from .npy, so no unit conversion is needed downstream.
    stype = "depth" if cam.get("depth") else "camera"
    # NOTE: the link carries a sensor only -- no <visual>, no <collision>.  All cameras sit
    # on the y = 0 axis looking +X, so a visible body would appear in the frame of every
    # camera behind it.
    return f"""
    <model name="cam_{cam['key']}">
      <static>true</static>
      <pose>{_pose(cam['x'], cam['y'], cam['z'], 0.0, cam['pitch'], 0.0)}</pose>
      <link name="link">
        <sensor name="{cam['key']}" type="{stype}">
          <camera name="{cam['key']}">
            <horizontal_fov>{cam['hfov']:.6f}</horizontal_fov>
            <image><width>{w}</width><height>{h}</height><format>R8G8B8</format></image>
            <clip><near>0.05</near><far>150</far></clip>
          </camera>
          <!-- 1 Hz on purpose.  The gazebo_ros_camera plugin holds a frame connection, so
               the sensor renders whether or not anyone is subscribed; with 9 cameras in the
               world this is the knob that keeps the GPU cost negligible next to training.
               Regenerate with --cams to drop cameras entirely if the GPU is contended. -->
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
    </model>"""


HEADER = """<?xml version="1.0" ?>
<!-- {title}
     GENERATED by make_worlds.py -- edit the generator, not this file.
     Gazebo Classic 11.10.2 / SDF 1.6.  No <include>, no model://, no meshes.
     Drop-start edge (lip) at x = {xlip} m; +X is the walking / viewing direction.
-->
<sdf version="1.6">
  <world name="default">
    <gui>
      <camera name="gzclient_camera">
        <pose>6 -7 3.2 0 0.32 0.72</pose>
      </camera>
    </gui>

    <physics type="ode">
      <gravity>0 0 -9.81</gravity>
      <ode>
        <solver><type>quick</type><iters>20</iters><sor>1.0</sor></solver>
        <constraints>
          <cfm>0.0</cfm><erp>0.2</erp>
          <contact_max_correcting_vel>100.0</contact_max_correcting_vel>
          <contact_surface_layer>0.0</contact_surface_layer>
        </constraints>
      </ode>
      <real_time_update_rate>1000</real_time_update_rate>
      <max_step_size>0.001</max_step_size>
    </physics>

    <scene>
      <ambient>0.45 0.45 0.48 1</ambient>
      <background>0.72 0.78 0.88 1</background>
      <shadows>true</shadows>
      <grid>false</grid>
      <origin_visual>false</origin_visual>
    </scene>

    <!-- Single hard directional light.  Shadow contrast inside the drop is a real cue and
         must be identical between the hazard arm and the ctrl arm. -->
    <light name="sun" type="directional">
      <pose>0 0 12 0 0 0</pose>
      <diffuse>0.90 0.88 0.85 1</diffuse>
      <specular>0.25 0.25 0.25 1</specular>
      <direction>0.35 0.30 -0.89</direction>
      <cast_shadows>true</cast_shadows>
    </light>
"""

FOOTER = """
  </world>
</sdf>
"""


def deck_with_notch(nx0, nx1, nhy):
    """Upper deck (top z = 0) covering the whole footprint MINUS a rectangular notch.

    Four slabs: two full-length side wings, a near slab up to the notch, a far slab past it.
    The wings' inner faces (thickness DECK_T) double as the notch's side walls, which is why
    DECK_T must stay deeper than any hazard floor.
    """
    wing_hy = (DECK_HY - nhy) / 2.0
    wing_cy = nhy + wing_hy
    cx_all, sx_all = (DECK_X0 + FAR_X) / 2.0, FAR_X - DECK_X0
    return [
        box_model("deck_left", cx_all, wing_cy, -DECK_T / 2.0,
                  sx_all, 2 * wing_hy, DECK_T, MAT_DECK),
        box_model("deck_right", cx_all, -wing_cy, -DECK_T / 2.0,
                  sx_all, 2 * wing_hy, DECK_T, MAT_DECK),
        box_model("deck_near", (DECK_X0 + nx0) / 2.0, 0.0, -DECK_T / 2.0,
                  nx0 - DECK_X0, 2 * nhy, DECK_T, MAT_DECK),
        box_model("deck_far", (nx1 + FAR_X) / 2.0, 0.0, -DECK_T / 2.0,
                  FAR_X - nx1, 2 * nhy, DECK_T, MAT_DECK),
    ]


def deck_solid():
    """The ctrl arm's ground: one continuous slab, same top surface, no hole."""
    return [box_model("deck", (DECK_X0 + FAR_X) / 2.0, 0.0, -DECK_T / 2.0,
                      FAR_X - DECK_X0, 2 * DECK_HY, DECK_T, MAT_DECK)]


def planter_model(name):
    """The gz_drop3 occluder: a brick planter box with a planting cap on top.

    DRESSING, not hazard -- it stands on the deck at z = 0 and is byte-identical in both
    twin arms.  Body and cap share a footprint so the silhouette the occlusion maths uses
    is a clean rectangle of height D3_OCC_BODY_H + D3_OCC_CAP_H.
    """
    cx = (D3_OCC_X0 + D3_OCC_X1) / 2.0
    sx = D3_OCC_X1 - D3_OCC_X0
    sy = 2 * D3_OCC_HY
    body = box_model(name, cx, 0.0, D3_OCC_BODY_H / 2.0, sx, sy, D3_OCC_BODY_H, MAT_OCC)
    cap = box_model(name + "_cap", cx, 0.0, D3_OCC_BODY_H + D3_OCC_CAP_H / 2.0,
                    sx, sy, D3_OCC_CAP_H, MAT_OCC_CAP, collision=False)
    return [body, cap]


def flanking_walls():
    """Perspective / horizon reference.  Deck region only, so both twin arms match."""
    out = []
    cx = (DECK_X0 + X_LIP) / 2.0
    sx = X_LIP - DECK_X0
    for sgn in (+1, -1):
        out.append(box_model(f"wall_{'p' if sgn > 0 else 'm'}y", cx, sgn * WALL_Y,
                             WALL_H / 2.0, sx, WALL_T, WALL_H, MAT_WALL))
    return out


# --------------------------------------------------------------------------- world builders
def world_drop1(hazard: bool):
    """Descending stair into a sunken pit (hazard) / continuous deck (ctrl)."""
    m = []
    if hazard:
        # deck split around the notch: left / right wings run the full length, the near slab
        # stops at the lip, and a far slab closes the pit at x = 20.
        pit_x1 = 20.0
        m += deck_with_notch(X_LIP, pit_x1, NOTCH_HY)
        # treads 1..N-1 (the last riser lands straight on the pit floor)
        bot = -(DROP1 + 0.48)
        for i in range(1, N_RISERS):
            top = -RISE * i
            x0 = X_LIP + TREAD * (i - 1)
            m.append(box_model(f"tread{i}", x0 + TREAD / 2.0, 0.0, (top + bot) / 2.0,
                               TREAD, 2 * NOTCH_HY, top - bot, MAT_STEP))
        # pit floor, starting where the last riser lands
        pit_x0 = X_LIP + TREAD * (N_RISERS - 1)
        m.append(box_model("pit_floor", (pit_x0 + pit_x1) / 2.0, 0.0, -DROP1 - 0.24,
                           pit_x1 - pit_x0, 2 * NOTCH_HY, 0.48, MAT_PIT))
    else:
        m += deck_solid()      # ctrl arm: same footprint, same top surface, no hole

    m += flanking_walls()
    # --- dressing (identical in both arms) ---
    m.append(rail_model("rail_py", guard_rail_segments(+RAIL_Y, RAIL_X0, RAIL_X1)))
    m.append(rail_model("rail_my", guard_rail_segments(-RAIL_Y, RAIL_X0, RAIL_X1)))
    m.append(warning_strip_model("warn_strip"))
    return m


def world_drop3(hazard: bool):
    """H composition: a 0.72 m pit whose rim AND interior are hidden by a planter in front.

    The hazard must stay INFERABLE (PS §6-3), so three cues survive in every frame:
    the warning strip in front of the planter, the planter itself (edge protection), and the
    guard rails terminating exactly at the lip.  See worlds/README.md §8.2 for the per-preset
    occlusion derivation.
    """
    m = []
    if hazard:
        m += deck_with_notch(D3_PIT_X0, D3_PIT_X1, D3_PIT_HY)
        m.append(box_model("pit_floor", (D3_PIT_X0 + D3_PIT_X1) / 2.0, 0.0,
                           -D3_DROP - 0.24, D3_PIT_X1 - D3_PIT_X0, 2 * D3_PIT_HY,
                           0.48, MAT_PIT))
    else:
        m += deck_solid()

    m += flanking_walls()
    # --- dressing (identical in both arms) ---
    m += planter_model("planter")
    m.append(rail_model("rail_py", guard_rail_segments(+RAIL_Y, RAIL_X0, RAIL_X1)))
    m.append(rail_model("rail_my", guard_rail_segments(-RAIL_Y, RAIL_X0, RAIL_X1)))
    m.append(warning_strip_model("warn_strip", D3_STRIP_X0, D3_STRIP_X1, STRIP_HY))
    return m


def world_drop4(hazard: bool):
    """E composition: a narrow open trench across the walkway -- rim visible, interior not.

    0.25 m along X x 1.00 m across x 0.70 m deep.  The size is set by the tier arithmetic,
    not by taste: int_px_DS = (W*h/d)*L / (R^2 * 5.0742e-6) has to fall under TAU_INT_DEF=50
    at the d10 presets while the rim stays fully visible (edge_ratio ~ 1.0 >> TAU_EDGE 0.05).
    """
    m = []
    if hazard:
        m += deck_with_notch(X_LIP, X_LIP + D4_W, D4_HY)
        m.append(box_model("trench_floor", X_LIP + D4_W / 2.0, 0.0, -D4_DROP - 0.15,
                           D4_W, 2 * D4_HY, 0.30, MAT_PIT))
    else:
        m += deck_solid()

    m += flanking_walls()
    # --- dressing (identical in both arms) ---
    m.append(rail_model("rail_py", guard_rail_segments(+RAIL_Y, RAIL_X0, RAIL_X1)))
    m.append(rail_model("rail_my", guard_rail_segments(-RAIL_Y, RAIL_X0, RAIL_X1)))
    m.append(warning_strip_model("warn_strip", D4_STRIP_X0, D4_STRIP_X1, STRIP_HY))
    return m


def world_drop2(hazard: bool):
    """Sheer platform edge, 0.80 m (hazard) / flush floor (ctrl).  Guard rail on +Y only."""
    m = []
    m.append(box_model("deck", (DECK_X0 + X_LIP) / 2.0, 0.0, -DECK_T / 2.0,
                       X_LIP - DECK_X0, 2 * DECK_HY, DECK_T, MAT_DECK))
    if hazard:
        m.append(box_model("lower_floor", (X_LIP + FAR_X) / 2.0, 0.0, -DROP2 - 0.30,
                           FAR_X - X_LIP, 2 * DECK_HY, 0.60, MAT_PIT))
    else:
        m.append(box_model("lower_floor", (X_LIP + FAR_X) / 2.0, 0.0, -0.30,
                           FAR_X - X_LIP, 2 * DECK_HY, 0.60, MAT_PIT))

    m += flanking_walls()
    # --- dressing (identical in both arms): rail on the +Y side ONLY, with a short return
    #     along the lip covering y in [+0.35, +1.30].  The whole -Y half of the lip is open.
    m.append(rail_model("rail_py", guard_rail_segments(
        +RAIL_Y, RAIL_X0, RAIL_X1, return_leg=(X_LIP - 0.05, RAIL_Y, 0.35))))
    return m


# --------------------------------------------------------------------------- main
SPECS = [
    ("gz_drop1", world_drop1, True,
     "gz_drop1 -- descending stair, 4 x 0.18 m risers = 0.72 m drop into a sunken pit"),
    ("gz_drop1_ctrl", world_drop1, False,
     "gz_drop1_ctrl -- TWIN CONTROL of gz_drop1: stair + pit removed, dressing identical"),
    ("gz_drop2", world_drop2, True,
     "gz_drop2 -- platform edge, sheer 0.80 m drop, guard rail on the +Y side only"),
    ("gz_drop2_ctrl", world_drop2, False,
     "gz_drop2_ctrl -- TWIN CONTROL of gz_drop2: lower level raised flush, dressing identical"),
    ("gz_drop3", world_drop3, True,
     "gz_drop3 -- H composition: 0.72 m pit hidden behind a 0.61 m planter, cues left visible"),
    ("gz_drop3_ctrl", world_drop3, False,
     "gz_drop3_ctrl -- TWIN CONTROL of gz_drop3: pit removed, planter + cues identical"),
    ("gz_drop4", world_drop4, True,
     "gz_drop4 -- E composition: 0.25 x 1.00 m open trench, 0.70 m deep; rim seen, interior not"),
    ("gz_drop4_ctrl", world_drop4, False,
     "gz_drop4_ctrl -- TWIN CONTROL of gz_drop4: trench filled, dressing identical"),
]


def main():
    global D3_OCC_BODY_H, D4_HY
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                     "worlds"))
    ap.add_argument("--cams", default="", help="comma list of camera keys to keep (default all)")
    ap.add_argument("--d3-occ", type=float, default=None, metavar="M",
                    help="gz_drop3 parapet BODY height (default %.2f; +%.2f cap on top). "
                         "Raising it widens the H margin; lowering it below h0.9 - (pit "
                         "length)*... starts leaking the far wall at h0.9_d2 first."
                         % (D3_OCC_BODY_H, D3_OCC_CAP_H))
    ap.add_argument("--d4-lat", type=float, default=None, metavar="M",
                    help="gz_drop4 trench lateral opening (default %.2f m). int_px scales "
                         "linearly with it: 0.45 m also buys E at preset_h0.3_d5, at the "
                         "cost of the trench no longer spanning the walkway."
                         % (2 * D4_HY))
    ap.add_argument("--depth", action="store_true",
                    help="make the negobs cameras depth sensors (RGB + 32FC1 metric depth "
                         "from one plugin) so the frozen Depth/B2 models can be fed too. "
                         "Off by default: costs extra render, and infer_photo.py is RGB-only.")
    args = ap.parse_args()

    if args.d3_occ is not None:
        D3_OCC_BODY_H = args.d3_occ
    if args.d4_lat is not None:
        D4_HY = args.d4_lat / 2.0

    keep = [c for c in args.cams.split(",") if c.strip()] or None
    cams = build_cameras(keep)
    if args.depth:
        for c in cams:
            if c["family"] == "negobs":
                c["depth"] = True
    os.makedirs(args.outdir, exist_ok=True)

    cam_sdf = "\n    <!-- ===== capture cameras (sensor-only links, no visible body) ===== -->" \
              + "".join(camera_model(c) for c in cams)

    for name, fn, hazard, title in SPECS:
        body = "".join(fn(hazard))
        txt = HEADER.format(title=title, xlip=X_LIP) + body + cam_sdf + FOOTER
        path = os.path.join(args.outdir, name + ".world")
        with open(path, "w") as f:
            f.write(txt)
        print(f"[wrote] {path}  ({len(txt)} bytes)")

    print("\ncameras:")
    for c in cams:
        print(f"  {c['key']:<10} view={c['view']:<18} eye=({c['x']:.2f}, {c['y']:.2f}, "
              f"{c['z']:.3f})  pitch={-math.degrees(c['pitch']):.1f} deg  "
              f"hfov={math.degrees(c['hfov']):.2f} deg  {c['res'][0]}x{c['res'][1]}  "
              f"topic=/gzcam/{c['key']}/cam/image_raw (verify with `ros2 topic list`)")


if __name__ == "__main__":
    main()
