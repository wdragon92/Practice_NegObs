#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_vth_worlds.py -- world COPIES carrying a batch of static RGB-D cameras.

The baseline tree is read-only.  Each output world is the paper's own world file,
byte-for-byte, with ONE block spliced in immediately before the closing </world>:
N static <model>s, each holding one `type="depth"` sensor.  A depth sensor gives
colour and depth from the SAME sensor, so RGB and depth are pixel-aligned by
construction (no cross-sensor extrinsics to get wrong).

usage: python3 make_vth_worlds.py [--batch 30]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = ("/home/vislab/Desktop/work_sy/Baseline_NegObs/src/negativeobstacleavoidandance/"
       "bumperbot_description/worlds")
ANCHOR = "  </world>"


def cam_model(key, p):
    w, h = p["res"]
    return f"""    <model name="cam_{key}">
      <static>true</static>
      <pose>{p['x']:.6f} {p['y']:.6f} {p['z']:.6f} 0 {p['sdf_pitch_rad']:.6f} {p['yaw_rad']:.6f}</pose>
      <link name="link">
        <sensor name="s_{key}" type="depth">
          <camera name="c_{key}">
            <horizontal_fov>{p['hfov_rad']:.4f}</horizontal_fov>
            <image><width>{w}</width><height>{h}</height><format>R8G8B8</format></image>
            <clip><near>0.1</near><far>100</far></clip>
          </camera>
          <always_on>1</always_on>
          <update_rate>2.0</update_rate>
          <visualize>0</visualize>
          <plugin name="plug_{key}" filename="libgazebo_ros_camera.so">
            <ros><namespace>/gzcam/{key}</namespace></ros>
            <camera_name>cam</camera_name>
            <frame_name>gzcam_{key}_optical</frame_name>
            <hack_baseline>0.0</hack_baseline>
            <min_depth>0.1</min_depth>
            <max_depth>100.0</max_depth>
          </plugin>
        </sensor>
      </link>
    </model>
"""


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", type=int, default=30)
    ap.add_argument("--plan", default="plan.json")
    ap.add_argument("--tag", default="b", help="batch letter in the world-copy name")
    ap.add_argument("--index", default="batches.json")
    a = ap.parse_args()
    outdir = os.path.join(HERE, "worlds")
    os.makedirs(outdir, exist_ok=True)
    plan = json.load(open(os.path.join(HERE, a.plan)))

    md = ["# VTH world copies -- what was added to the paper's worlds", "",
          "Source (read-only, never written):", ""]
    for w in ("eworld2", "expandedworld"):
        sp = os.path.join(SRC, w + ".world")
        md.append(f"- `{sp}`  sha256 `{sha(sp)[:16]}`  ({os.path.getsize(sp)} bytes)")
    md += ["",
           "Every copy = that file verbatim + one spliced block placed immediately before",
           "the closing `</world>`.  Nothing existing is edited, deleted or reordered: no",
           "light, no material, no `<scene>`, no asset pose, no `<state>` entry is touched.",
           "The block holds only static camera models (instrumentation).", "",
           "| world copy | cameras | added lines | bytes | sha256[:16] |",
           "|---|---:|---:|---:|---|"]

    index = {}
    for w in ("eworld2", "expandedworld"):
        src = open(os.path.join(SRC, w + ".world")).read()
        if ANCHOR not in src:
            raise SystemExit(f"[fatal] anchor missing in {w}")
        poses = [p for p in plan if p["world"] == w]
        if not poses:
            continue
        batches = [poses[i:i + a.batch] for i in range(0, len(poses), a.batch)]
        for bi, batch in enumerate(batches):
            cams = {}
            block = ["", "    <!-- ===== ADDED BY make_vth_worlds.py: VTH camera batch "
                     f"{w} {a.tag}{bi:02d} ({len(batch)} static RGB-D cameras) ===== -->"]
            for ci, p in enumerate(batch):
                key = f"c{ci:03d}"
                cams[key] = p
                block.append(cam_model(key, p))
            block.append("    <!-- ===== END ADDED BLOCK ===== -->")
            block.append("")
            add = "\n".join(block)
            out = src.replace(ANCHOR, add + "\n" + ANCHOR, 1)
            name = f"{w}_{a.tag}{bi:02d}"
            wp = os.path.join(outdir, name + ".world")
            open(wp, "w").write(out)
            json.dump(cams, open(os.path.join(outdir, name + ".cams.json"), "w"),
                      indent=1, sort_keys=True)
            md.append(f"| `{name}.world` | {len(batch)} | {len(add.splitlines())} | "
                      f"{os.path.getsize(wp)} | `{sha(wp)[:16]}` |")
            index.setdefault(w, []).append(name)
            print(f"[make_vth_worlds] {name}.world  {len(batch)} cameras")
    json.dump(index, open(os.path.join(outdir, a.index), "w"), indent=1)
    dp = os.path.join(outdir, "VTH_WORLD_DIFFS.md")
    open(dp, "a" if a.tag != "b" else "w").write("\n".join(md) + "\n")
    print(f"[make_vth_worlds] {sum(len(v) for v in index.values())} world copies -> {outdir}")


if __name__ == "__main__":
    main()
