"""Split one eval per_frame.csv into its on-arm and off-arm halves.

A test eval writes ONE per_frame.csv carrying both arms (frame_id = "<arm>/<scene>/<file>").
twin_analysis.py can take that same file twice, but the queue writes the two halves explicitly so
that (a) the twin step's inputs are visible in the run dir, and (b) an aborted run can be resumed
by checking for the files.

  python split_per_frame.py --per-frame EVAL/per_frame.csv --out-dir EVAL
  -> EVAL/per_frame_on.csv, EVAL/per_frame_off.csv   (header preserved verbatim)
"""
from __future__ import annotations

import argparse
import csv
import os


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--per-frame", required=True)
    p.add_argument("--out-dir", default=None, help="default: the per-frame file's own directory")
    p.add_argument("--prefix", default="per_frame")
    a = p.parse_args(argv)
    out_dir = a.out_dir or os.path.dirname(os.path.abspath(a.per_frame))
    os.makedirs(out_dir, exist_ok=True)

    with open(a.per_frame) as f:
        rd = csv.reader(f)
        head = next(rd)
        rows = list(rd)
    try:
        col = head.index("toggle_state")
    except ValueError:
        col = None
    n = {}
    for arm in ("on", "off"):
        sel = [r for r in rows
               if (r[col] == arm if col is not None else r[0].split("/", 1)[0] == arm)]
        path = os.path.join(out_dir, f"{a.prefix}_{arm}.csv")
        with open(path, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(head)
            w.writerows(sel)
        n[arm] = len(sel)
    print(f"[split_per_frame] {len(rows)} rows -> on {n['on']} / off {n['off']} in {out_dir}")
    if not n["on"] or not n["off"]:
        print("[split_per_frame] WARNING: one arm is empty -- twin analysis will have no pairs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
