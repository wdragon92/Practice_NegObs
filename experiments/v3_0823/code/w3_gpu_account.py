#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""w3_gpu_account.py — W3 라운드의 **GPU-시간 정직 회계**

두 수를 구분해서 낸다. 이 창에서는 C 웨이브(w1c)가 같은 `flock` 을 공유하므로
**벽시계 ≠ GPU 점유**다. 벽시계만 보고하면 남의 렌더 시간을 W3 예산에 청구하게 된다.

  wall   러너 로그의 `[render]` → `[ok]` 델타 합 = **락 대기 포함** (상한)
  gpu    Σ(씬 프로세스의 `variation.json:sec`) + 프로세스 수 × BOOT
         `sec` 는 in-process 캡처 시간이라 부팅·어셈블리·사이드카가 빠져 있고
         (계획 §4.1 이 CUE_COVERAGE 의 "4.0–4.7 s/컷" 을 그 이유로 기각했다),
         그 빠진 몫이 계획 §4.1 의 실측 상수 **21.2 s/프로세스**다.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))

# 0827 reorg: dataset/ is grouped (dataset/<group>/<round>) and a round is
# found by NAME, never by a flat path. See Docs/reorg_0827/S3_report.md.
sys.path.insert(0, REPO)                              # noqa: E402
from variation_kit import round_dir_or_flat   # noqa: E402
BOOT = 21.2      # 계획 §4.1: 부팅 6.7 + 어셈블리·사이드카 = 21.2 s/프로세스 (74회 평균)

STAMPS = ["260824_v3w3_extsmoke_A"] + [
    f"260824_v3w3_ext{b}_{a}" for b in ("base", "h", "lat", "b2") for a in "ABCD"]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", default=os.path.join(
        REPO, "experiments/v3_0823/logs/w3_text_render.log"))
    ap.add_argument("--out", default="")
    a = ap.parse_args(argv)

    rows, n_cuts, sec_sum, n_proc = [], 0, 0.0, 0
    for st in STAMPS:
        for vp in sorted(glob.glob(os.path.join(
                round_dir_or_flat(st), "*", "*", "variation.json"))):
            v = json.load(open(vp, encoding="utf-8"))
            n = int(v.get("n_ok") or v.get("n") or 0)
            s = float(v.get("sec") or 0.0)
            rows.append(dict(stamp=st, scene=v.get("scene"), n=n, sec=s,
                             sec_per_cut=v.get("sec_per_cut")))
            n_cuts += n
            sec_sum += s
            n_proc += 1

    # 벽시계 = 락 대기 포함. v1 러너는 팔 단위 `[ok] … rc=N NNNs`, v2 러너는 쌍 단위
    #   `[batch] … 종료 rc=N NNNs` 로 찍는다 — 두 형식을 다 받는다.
    wall = 0.0
    if os.path.isfile(a.log):
        for ln in open(a.log, encoding="utf-8", errors="replace"):
            m = re.search(r"\[ok\]\s+\S+\s+(\S+)\s+rc=\d+\s+(\d+)s", ln)
            if m and m.group(1) in STAMPS:
                wall += float(m.group(2))
                continue
            m = re.search(r"\[batch\].*종료 rc=\d+\s+(\d+)s", ln)
            if m:
                wall += float(m.group(1))

    gpu_s = sec_sum + n_proc * BOOT
    rep = dict(n_processes=n_proc, n_cuts=n_cuts,
               sec_in_process=round(sec_sum, 1),
               boot_const_s=BOOT,
               gpu_seconds=round(gpu_s, 1), gpu_hours=round(gpu_s / 3600, 3),
               wall_seconds_incl_lock=round(wall, 1),
               wall_hours_incl_lock=round(wall / 3600, 3),
               s_per_cut_gpu=(round(gpu_s / n_cuts, 3) if n_cuts else None),
               s_per_cut_wall=(round(wall / n_cuts, 3) if n_cuts else None),
               plan_s_per_cut=5.84, rows=rows)
    print(f"프로세스 {n_proc} · 컷 {n_cuts}")
    print(f"  in-process Σsec       {sec_sum:9.1f} s")
    print(f"  + 부팅·어셈블리 상수  {n_proc} × {BOOT} = {n_proc * BOOT:7.1f} s")
    print(f"  ⇒ **GPU {gpu_s / 3600:.3f} h** ({gpu_s / n_cuts if n_cuts else 0:.2f} s/컷 · "
          f"계획 실측 단가 5.84)")
    print(f"  벽시계(락 대기 포함)  {wall / 3600:.3f} h "
          f"({wall / n_cuts if n_cuts else 0:.2f} s/컷) "
          f"— 차액 {(wall - gpu_s) / 3600:.3f} h 는 C 웨이브 대기")
    if a.out:
        json.dump(rep, open(a.out, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        print(f"[out] {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
