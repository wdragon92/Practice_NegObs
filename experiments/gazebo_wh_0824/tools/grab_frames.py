#!/usr/bin/env python3
"""Save a fixed number of RGB frames from the warehouse-variant world cameras, then exit.

Deliberately minimal:
  * no cv_bridge  -- sensor_msgs/Image is decoded with numpy alone, so a numpy ABI mismatch
    between neg_env (numpy 1.24.1, pinned) and the system-built cv_bridge cannot bite us
  * no cv2        -- PNG is written with Pillow (already in neg_env via ultralytics)
  * BEST_EFFORT subscriptions -- compatible with both a reliable and a sensor-data publisher
  * exits on its own once every requested topic has delivered its quota

Usage (after `source setup_env.sh` in Baseline_NegObs, with gzserver already up):

    python3 tools/grab_frames.py --tag gz_drop1_on --outdir frames/gz_drop1_on -n 3
    python3 tools/grab_frames.py --tag gz_drop1_on --views preset_h0.3_d2,preset_h0.9_d5

    --list      just print the Image topics that are live right now and exit
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time

import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSDurabilityPolicy, QoSHistoryPolicy, QoSProfile, QoSReliabilityPolicy
from sensor_msgs.msg import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from make_wh_worlds import build_cameras  # noqa: E402  (single source of truth for the presets)

BEST_EFFORT = QoSProfile(
    reliability=QoSReliabilityPolicy.BEST_EFFORT,
    durability=QoSDurabilityPolicy.VOLATILE,
    history=QoSHistoryPolicy.KEEP_LAST,
    depth=2,
)


def decode(msg: Image) -> np.ndarray:
    """sensor_msgs/Image -> HxWx3 uint8 RGB.  Only the encodings gazebo_ros_camera emits."""
    buf = np.frombuffer(msg.data, dtype=np.uint8)
    arr = buf.reshape(msg.height, msg.step)[:, : msg.width * 3].reshape(msg.height, msg.width, 3)
    enc = msg.encoding.lower()
    if enc == "bgr8":
        arr = arr[:, :, ::-1]
    elif enc not in ("rgb8",):
        raise SystemExit(f"[fatal] unexpected encoding {msg.encoding!r} (want rgb8/bgr8)")
    return np.ascontiguousarray(arr)


def decode_depth(msg: Image) -> np.ndarray:
    """sensor_msgs/Image (32FC1 from a Gazebo depth sensor) -> HxW float32 METRES.

    polar_dataset.load_depth_m() reads .npy as metres directly, so nothing is rescaled here.
    Gazebo writes +inf (or the far clip) where nothing was hit; those stay as-is and are
    clipped downstream by DEPTH_CLIP_M.
    """
    if msg.encoding != "32FC1":
        raise SystemExit(f"[fatal] depth encoding {msg.encoding!r}, expected 32FC1")
    a = np.frombuffer(msg.data, dtype=np.float32)
    return np.ascontiguousarray(a.reshape(msg.height, msg.step // 4)[:, : msg.width])


class Grabber(Node):
    def __init__(self, targets, outdir, tag, n, settle):
        super().__init__("gz_frame_grabber")
        self.outdir, self.tag, self.n, self.settle = outdir, tag, n, settle
        self.t0 = time.time()
        self.count = {v: 0 for _, v, _ in targets}
        self.dcount = {}
        self.saved = []
        self.subs = []
        for topic, view, dtopic in targets:
            self.subs.append(self.create_subscription(
                Image, topic, self._make_cb(topic, view), BEST_EFFORT))
            self.get_logger().info(f"subscribed  {topic}  ->  {view}")
            if dtopic:
                self.dcount[view] = 0
                self.subs.append(self.create_subscription(
                    Image, dtopic, self._make_depth_cb(dtopic, view), BEST_EFFORT))
                self.get_logger().info(f"subscribed  {dtopic}  ->  {view} (depth)")

    def _make_cb(self, topic, view):
        def cb(msg):
            # give the renderer a moment: the first frame after a lazy sensor wakes up can
            # be a half-composited buffer.
            if time.time() - self.t0 < self.settle:
                return
            i = self.count[view]
            if i >= self.n:
                return
            self.count[view] = i + 1
            img = decode(msg)
            from PIL import Image as PImage
            fn = f"{self.tag}_{view}_{i:03d}.png"
            PImage.fromarray(img).save(os.path.join(self.outdir, fn))
            self.saved.append(dict(file=fn, view=view, topic=topic, kind="rgb",
                                   w=int(msg.width), h=int(msg.height),
                                   encoding=msg.encoding))
            self.get_logger().info(f"saved {fn}  ({msg.width}x{msg.height})")
        return cb

    def _make_depth_cb(self, topic, view):
        def cb(msg):
            if time.time() - self.t0 < self.settle:
                return
            i = self.dcount[view]
            if i >= self.n:
                return
            self.dcount[view] = i + 1
            fn = f"{self.tag}_{view}_{i:03d}_depth.npy"
            np.save(os.path.join(self.outdir, fn), decode_depth(msg))
            self.saved.append(dict(file=fn, view=view, topic=topic, kind="depth_m",
                                   w=int(msg.width), h=int(msg.height),
                                   encoding=msg.encoding))
            self.get_logger().info(f"saved {fn}  ({msg.width}x{msg.height}, float32 metres)")
        return cb

    def done(self):
        return (all(v >= self.n for v in self.count.values())
                and all(v >= self.n for v in self.dcount.values()))


def live_image_topics(node):
    return sorted(t for t, types in node.get_topic_names_and_types()
                  if "sensor_msgs/msg/Image" in types)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="gz_capture", help="file-name prefix, e.g. gz_drop1_on")
    ap.add_argument("--outdir", default="frames")
    ap.add_argument("-n", "--frames", type=int, default=3, help="frames per view (default 3)")
    ap.add_argument("--views", default="", help="comma list of view names (default: all)")
    ap.add_argument("--timeout", type=float, default=90.0)
    ap.add_argument("--settle", type=float, default=3.0,
                    help="seconds to discard after subscribing (default 3)")
    ap.add_argument("--list", action="store_true", help="print live Image topics and exit")
    args = ap.parse_args()

    rclpy.init()
    probe = rclpy.create_node("gz_frame_probe")
    time.sleep(1.5)                                   # let discovery settle
    live = live_image_topics(probe)
    if args.list:
        print("\n".join(live) or "(no sensor_msgs/msg/Image topics)")
        probe.destroy_node()
        rclpy.shutdown()
        return
    probe.destroy_node()

    cams = build_cameras()
    want = {v.strip() for v in args.views.split(",") if v.strip()}
    targets, missing = [], []
    for c in cams:
        if want and c["view"] not in want and c["key"] not in want:
            continue
        # The exact leaf that gazebo_ros_camera resolves "~/image_raw" to depends on the
        # plugin's node name, so match on the namespace we control and sort by path length:
        # the shortest hit is the colour topic, ".../depth/image_raw" is the depth one.
        hits = sorted((t for t in live
                       if t.startswith(f"/gzcam/{c['key']}/") and t.endswith("image_raw")),
                      key=len)
        if hits:
            dtopic = next((t for t in hits if "/depth/" in t), None)
            colour = next((t for t in hits if "/depth/" not in t), hits[0])
            targets.append((colour, c["view"], dtopic))
        else:
            missing.append(c["key"])
    if missing:
        print(f"[warn] no live topic for: {', '.join(missing)}", file=sys.stderr)
    if not targets:
        print("[fatal] nothing to record. live Image topics were:", file=sys.stderr)
        print("  " + "\n  ".join(live), file=sys.stderr)
        rclpy.shutdown()
        raise SystemExit(2)

    os.makedirs(args.outdir, exist_ok=True)
    node = Grabber(targets, args.outdir, args.tag, args.frames, args.settle)
    t_end = time.time() + args.timeout
    while rclpy.ok() and time.time() < t_end and not node.done():
        rclpy.spin_once(node, timeout_sec=0.2)

    by_view = {c["view"]: c for c in cams}
    manifest = dict(
        tag=args.tag,
        generated=time.strftime("%Y-%m-%dT%H:%M:%S"),
        note="Gazebo Classic 11.10.2 capture; poses are exact (static camera models), "
             "so infer_photo.py --height/--pitch/--hfov are MEASURED, not assumed.",
        frames=node.saved,
        cameras={v: dict(eye=[c["x"], c["y"], c["z"]],
                         yaw_rad=c.get("yaw", 0.0),
                         pitch_rad=c["pitch"],
                         height_agl=c.get("h_agl", c["z"]),
                         standoff=c.get("standoff"),
                         family=c.get("family"),
                         pitch_deg=-round(math.degrees(c["pitch"]), 3),
                         hfov_deg=round(math.degrees(c["hfov"]), 3),
                         hfov_rad=c["hfov"],
                         res=list(c["res"]),
                         infer_photo_args=[f"--height {c.get('h_agl', c['z'])}",
                                           f"--pitch {-round(math.degrees(c['pitch']), 3)}",
                                           f"--hfov {round(math.degrees(c['hfov']), 3)}",
                                           "--fit squash"])
                 for v, c in by_view.items() if v in node.count},
    )
    with open(os.path.join(args.outdir, f"{args.tag}_manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)

    node.get_logger().info(f"done: {len(node.saved)} frames -> {args.outdir}")
    if not node.done():
        node.get_logger().warn(f"TIMEOUT, short counts: {node.count}")
    node.destroy_node()
    rclpy.shutdown()
    raise SystemExit(0 if node.saved else 3)


if __name__ == "__main__":
    main()
