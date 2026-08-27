#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""grab_vth.py -- one RGB + one depth frame per camera of a VTH world batch, then exit.

Same minimal recipe as gazebo_wh_0824/tools/grab_frames.py (no cv_bridge, no cv2 --
numpy + Pillow only, BEST_EFFORT subs) but keyed off the batch's cams.json so each
file lands under its planning pose_id.

    <outdir>/<pose_id>.png         RGB, 1280x720 uint8
    <outdir>/<pose_id>.depth.npy   float32 METRES (Gazebo 32FC1, unscaled)
    <outdir>/<pose_id>.pose.json   the pose record + measured image facts
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSDurabilityPolicy, QoSHistoryPolicy, QoSProfile, QoSReliabilityPolicy
from sensor_msgs.msg import Image

BEST_EFFORT = QoSProfile(reliability=QoSReliabilityPolicy.BEST_EFFORT,
                         durability=QoSDurabilityPolicy.VOLATILE,
                         history=QoSHistoryPolicy.KEEP_LAST, depth=2)


def decode_rgb(msg):
    buf = np.frombuffer(msg.data, dtype=np.uint8)
    arr = buf.reshape(msg.height, msg.step)[:, : msg.width * 3].reshape(
        msg.height, msg.width, 3)
    enc = msg.encoding.lower()
    if enc == "bgr8":
        arr = arr[:, :, ::-1]
    elif enc != "rgb8":
        raise SystemExit(f"[fatal] unexpected RGB encoding {msg.encoding!r}")
    return np.ascontiguousarray(arr)


def decode_depth(msg):
    if msg.encoding != "32FC1":
        raise SystemExit(f"[fatal] depth encoding {msg.encoding!r}, expected 32FC1")
    a = np.frombuffer(msg.data, dtype=np.float32)
    return np.ascontiguousarray(a.reshape(msg.height, msg.step // 4)[:, : msg.width])


class Grabber(Node):
    def __init__(self, cams, outdir, settle):
        super().__init__("vth_grabber")
        self.cams, self.outdir, self.settle = cams, outdir, settle
        self.t0 = time.time()
        self.rgb, self.dep = {}, {}
        self.subs = []
        for key in cams:
            self.subs.append(self.create_subscription(
                Image, f"/gzcam/{key}/cam/image_raw", self._rgb_cb(key), BEST_EFFORT))
            self.subs.append(self.create_subscription(
                Image, f"/gzcam/{key}/cam/depth/image_raw", self._dep_cb(key), BEST_EFFORT))

    def _rgb_cb(self, key):
        def cb(msg):
            if time.time() - self.t0 < self.settle or key in self.rgb:
                return
            self.rgb[key] = decode_rgb(msg)
        return cb

    def _dep_cb(self, key):
        def cb(msg):
            if time.time() - self.t0 < self.settle or key in self.dep:
                return
            self.dep[key] = decode_depth(msg)
        return cb

    def done(self):
        return len(self.rgb) >= len(self.cams) and len(self.dep) >= len(self.cams)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cams", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--settle", type=float, default=6.0)
    ap.add_argument("--timeout", type=float, default=180.0)
    args = ap.parse_args()

    cams = json.load(open(args.cams))
    os.makedirs(args.outdir, exist_ok=True)
    rclpy.init()
    node = Grabber(cams, args.outdir, args.settle)
    t_end = time.time() + args.timeout
    while rclpy.ok() and time.time() < t_end and not node.done():
        rclpy.spin_once(node, timeout_sec=0.2)

    from PIL import Image as PImage
    saved, missing = [], []
    for key, p in sorted(cams.items()):
        if key not in node.rgb or key not in node.dep:
            missing.append((key, p["pose_id"]))
            continue
        pid = p["pose_id"]
        rgb, dep = node.rgb[key], node.dep[key]
        PImage.fromarray(rgb).save(os.path.join(args.outdir, pid + ".png"))
        np.save(os.path.join(args.outdir, pid + ".depth.npy"), dep.astype(np.float32))
        fin = np.isfinite(dep)
        rec = dict(p)
        rec["cam_key"] = key
        rec["rgb_file"] = pid + ".png"
        rec["depth_file"] = pid + ".depth.npy"
        rec["depth_units"] = "metres (Gazebo 32FC1, saved unscaled)"
        rec["depth_finite_frac"] = round(float(fin.mean()), 5)
        rec["depth_min_m"] = round(float(dep[fin].min()), 4) if fin.any() else None
        rec["depth_max_m"] = round(float(dep[fin].max()), 4) if fin.any() else None
        rec["rgb_mean"] = round(float(rgb.mean()), 2)
        rec["rgb_sat_frac"] = round(float((rgb >= 250).all(axis=2).mean()), 5)
        json.dump(rec, open(os.path.join(args.outdir, pid + ".pose.json"), "w"),
                  indent=1, sort_keys=True)
        saved.append(pid)
    print(f"[grab_vth] saved {len(saved)}/{len(cams)}  missing {len(missing)}", flush=True)
    for k, pid in missing:
        print(f"[grab_vth] MISSING {k} {pid}", file=sys.stderr)
    sys.stdout.flush()
    sys.stderr.flush()
    # rclpy shutdown with ~60 live subscriptions can sit for minutes on this install;
    # everything is already on disk, so leave hard.
    os._exit(0 if not missing else 4)


if __name__ == "__main__":
    main()
