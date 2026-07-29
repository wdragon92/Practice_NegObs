#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""라운드 스탬프 — 캡처 디렉터리에 `round_stamp.json` 을 남긴다.

`look_check/**` 는 gitignore 라 렌더 산출물 자체는 커밋되지 않는다. 그래서 "이 PNG 는
어느 HEAD·어느 MDL·어느 NEGOBS_* 팔에서 나왔는가" 를 붙여 두지 않으면 6주 뒤 그 라운드는
판독 불가가 된다(`w2c_merge_t1_v1.md` §9 가 라운드마다 이 파일을 요구하는 이유).

사용:  python3 scripts/stamp_round.py <capture_dir> <round> [scene]
GPU 0 · 저장소 파일 미변경(캡처 디렉터리에만 쓴다).
"""
from __future__ import annotations

import datetime
import glob
import hashlib
import json
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _git(*a):
    try:
        return subprocess.run(["git", "-C", REPO, *a], capture_output=True,
                              text=True, timeout=30).stdout.strip()
    except Exception:
        return ""


def _mdl():
    p = os.path.join(REPO, "assets", "NegObsGround.mdl")
    if not os.path.isfile(p):
        return None, None
    raw = open(p, "rb").read()
    ver = ""
    for ln in raw.decode("utf-8", "replace").splitlines():
        if "anno::version" in ln:
            ver = ln.strip()
            break
    return hashlib.md5(raw).hexdigest(), ver


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    out_dir, round_name = sys.argv[1], sys.argv[2]
    scene = sys.argv[3] if len(sys.argv) > 3 else ""
    if not os.path.isdir(out_dir):
        print(f"[stamp] 디렉터리 없음: {out_dir}", file=sys.stderr)
        return 2
    md5, ver = _mdl()
    stamp = dict(
        round=round_name, scene=scene,
        git_head=_git("rev-parse", "--short", "HEAD"),
        git_branch=_git("rev-parse", "--abbrev-ref", "HEAD"),
        dirty_files=len([l for l in _git("status", "--porcelain").splitlines() if l]),
        mdl_md5=md5, mdl_version_line=ver,
        cuts=len(glob.glob(os.path.join(out_dir, "*.png"))),
        stamped_at=datetime.datetime.now().isoformat(timespec="seconds"),
        env={k: v for k, v in sorted(os.environ.items())
             if k.startswith("NEGOBS_")},
    )
    with open(os.path.join(out_dir, "round_stamp.json"), "w",
              encoding="utf-8") as f:
        json.dump(stamp, f, ensure_ascii=False, indent=1)
    print(f"[stamp] {out_dir}/round_stamp.json · cuts {stamp['cuts']} · "
          f"HEAD {stamp['git_head']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
