#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""world_geom.py -- world-frame footprint boxes of every asset in a Gazebo .world.

Why: pose planning must not put a camera inside a shelf, and the occlusion poses
must put a shelf between camera and hole.  Both need the assets' world footprints.

Method [방법]:
  * XML-comment blocks are stripped first (eworld2 keeps many disabled models in
    comments -- they are NOT in the simulation).
  * every TOP-LEVEL <model> is taken with its <pose>; a <state> entry for the same
    model name overrides that pose (Gazebo applies <state> last).
  * the model's geometry is whichever it declares: an inline <mesh><uri>, or an
    <include><uri>model://NAME</uri> resolved against the baseline models dir.
  * a collision mesh (COLLADA) is reduced to its local axis-aligned bbox by reading
    the POSITION float_arrays and applying the file's <unit meter=...> scale.
  * the local bbox is rotated by the model yaw and re-boxed -> a world AABB.
    An AABB is deliberately conservative (never smaller than the asset).

Read-only: the baseline tree is only opened for reading.
"""
from __future__ import annotations

import json
import math
import os
import re
import sys

import numpy as np

BASE = ("/home/vislab/Desktop/work_sy/Baseline_NegObs/src/negativeobstacleavoidandance/"
        "bumperbot_description")
MODELS = os.path.join(BASE, "models")
WORLDS = os.path.join(BASE, "worlds")

_BBOX_CACHE = {}


def strip_comments(s):
    return re.sub(r"<!--.*?-->", "", s, flags=re.S)


def dae_bbox(path):
    """local-frame (xmin,ymin,zmin,xmax,ymax,zmax) of a COLLADA mesh, metres."""
    if path in _BBOX_CACHE:
        return _BBOX_CACHE[path]
    s = open(path, errors="ignore").read()
    m = re.search(r'<unit[^>]*meter="([0-9.eE+-]+)"', s)
    unit = float(m.group(1)) if m else 1.0
    pts = []
    for fa in re.finditer(r'<float_array[^>]*id="([^"]*)"[^>]*count="(\d+)"[^>]*>(.*?)</float_array>',
                          s, re.S):
        if "POSITION" not in fa.group(1).upper():
            continue
        v = np.fromstring(fa.group(3), sep=" ")
        if v.size % 3:
            continue
        pts.append(v.reshape(-1, 3))
    if not pts:
        _BBOX_CACHE[path] = None
        return None
    p = np.vstack(pts) * unit
    bb = (float(p[:, 0].min()), float(p[:, 1].min()), float(p[:, 2].min()),
          float(p[:, 0].max()), float(p[:, 1].max()), float(p[:, 2].max()))
    _BBOX_CACHE[path] = bb
    return bb


def stl_bbox(path):
    import struct
    if path in _BBOX_CACHE:
        return _BBOX_CACHE[path]
    blob = open(path, "rb").read()
    n = struct.unpack("<I", blob[80:84])[0]
    rec = np.frombuffer(blob, dtype=np.dtype([("n", "<3f4"), ("v", "<3,3f4"), ("a", "<u2")]),
                        count=n, offset=84)
    v = np.array(rec["v"], float).reshape(-1, 3)
    bb = (float(v[:, 0].min()), float(v[:, 1].min()), float(v[:, 2].min()),
          float(v[:, 0].max()), float(v[:, 1].max()), float(v[:, 2].max()))
    _BBOX_CACHE[path] = bb
    return bb


def mesh_bbox(uri):
    """resolve a Gazebo mesh uri -> local bbox"""
    p = uri.strip()
    # eworld2 includes several assets by their Ignition-Fuel URL; the same asset exists
    # in the baseline's own models/ dir, so map any ".../models/<NAME>" to models/<NAME>.
    mfuel = re.match(r"https?://.*/models/([^/]+)/?$", p)
    if mfuel:
        p = "model://" + mfuel.group(1)
    if p.startswith("model://"):
        p = os.path.join(MODELS, p[len("model://"):])
    elif p.startswith("file://models/"):
        p = os.path.join(MODELS, p[len("file://models/"):])
    elif p.startswith("file://"):
        p = p[len("file://"):]
    if not os.path.exists(p):
        return None
    if p.lower().endswith(".stl"):
        return stl_bbox(p)
    if p.lower().endswith(".dae"):
        return dae_bbox(p)
    return None


def model_local_bbox(body, depth=0):
    """union of collision-mesh bboxes declared inside a <model> body (any nesting)."""
    boxes = []
    for u in re.findall(r"<uri>([^<]+)</uri>", body):
        uu = u.strip()
        mf = re.match(r"https?://.*/models/([^/]+)/?$", uu)
        if mf:
            uu = "model://" + mf.group(1)
        if uu.startswith("model://") and not re.search(r"\.(dae|stl|obj)$", uu, re.I):
            # an <include> of another model -> descend into its model.sdf
            if depth > 2:
                continue
            d = os.path.join(MODELS, uu[len("model://"):])
            f = os.path.join(d, "model.sdf")
            if os.path.exists(f):
                bb = model_local_bbox(strip_comments(open(f, errors="ignore").read()), depth + 1)
                if bb:
                    boxes.append(bb)
            continue
        bb = mesh_bbox(u)
        if bb:
            boxes.append(bb)
    # inline <box><size>
    for sz in re.findall(r"<box>\s*<size>([^<]+)</size>", body):
        a = [float(t) for t in sz.split()]
        if len(a) == 3:
            boxes.append((-a[0] / 2, -a[1] / 2, -a[2] / 2, a[0] / 2, a[1] / 2, a[2] / 2))
    if not boxes:
        return None
    b = np.array(boxes, float)
    return (b[:, 0].min(), b[:, 1].min(), b[:, 2].min(),
            b[:, 3].max(), b[:, 4].max(), b[:, 5].max())


def top_level_models(src):
    """-> [(name, body)] for depth-0 <model> elements only."""
    out = []
    i = 0
    while True:
        m = re.compile(r"<model name=['\"]([^'\"]+)['\"]\s*>").search(src, i)
        if not m:
            break
        name = m.group(1)
        # walk to the matching </model>
        depth_ = 1
        j = m.end()
        while depth_ > 0:
            nxt = re.compile(r"<model\b[^>]*>|</model>").search(src, j)
            if not nxt:
                j = len(src)
                break
            if nxt.group(0).startswith("</"):
                depth_ -= 1
            else:
                depth_ += 1
            j = nxt.end()
        out.append((name, src[m.end():j]))
        i = j
    return out


def parse_state(src):
    """model-name -> pose list, from the <state> block (Gazebo applies it last)."""
    st = re.search(r"<state\b.*?</state>", src, re.S)
    if not st:
        return {}
    out = {}
    for name, body in top_level_models(st.group(0)):
        p = re.search(r"<pose[^>]*>([^<]+)</pose>", body)
        if p:
            out[name] = [float(t) for t in p.group(1).split()]
    return out


def load_world(world_path):
    src = strip_comments(open(world_path, errors="ignore").read())
    state = parse_state(src)
    body_src = re.sub(r"<state\b.*?</state>", "", src, flags=re.S)
    items = []
    for name, body in top_level_models(body_src):
        p = re.search(r"<pose[^>]*>([^<]+)</pose>", body)
        pose = [float(t) for t in p.group(1).split()] if p else [0, 0, 0, 0, 0, 0]
        if name in state:
            pose = state[name]
        bb = model_local_bbox(body)
        if bb is None:
            continue
        x, y, z = pose[0], pose[1], pose[2]
        yaw = pose[5] if len(pose) > 5 else 0.0
        cx = np.array([bb[0], bb[3], bb[3], bb[0]])
        cy = np.array([bb[1], bb[1], bb[4], bb[4]])
        c, s = math.cos(yaw), math.sin(yaw)
        wx = c * cx - s * cy + x
        wy = s * cx + c * cy + y
        items.append(dict(name=name, pose=pose,
                          local_bbox=[round(v, 4) for v in bb],
                          world_aabb=[round(float(wx.min()), 4), round(float(wy.min()), 4),
                                      round(float(wx.max()), 4), round(float(wy.max()), 4)],
                          z_lo=round(bb[2] + z, 4), z_hi=round(bb[5] + z, 4)))
    return items


def main():
    for w in (sys.argv[1:] or ["eworld2", "expandedworld"]):
        p = os.path.join(WORLDS, w + ".world") if not w.endswith(".world") else w
        items = load_world(p)
        print(f"===== {os.path.basename(p)}  ({len(items)} models with geometry)")
        print(f"{'name':58s} {'world AABB x0 y0 x1 y1':>40s} {'z_lo':>7s} {'z_hi':>7s}")
        for it in sorted(items, key=lambda d: d["name"]):
            a = it["world_aabb"]
            print(f"{it['name']:58s} {a[0]:9.3f} {a[1]:9.3f} {a[2]:9.3f} {a[3]:9.3f} "
                  f"{it['z_lo']:7.3f} {it['z_hi']:7.3f}")
        json.dump(items, open(os.path.join(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))), f"geom_{os.path.basename(p)[:-6]}.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
