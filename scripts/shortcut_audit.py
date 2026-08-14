#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""지름길(shortcut) 감사 v1 — "깊을수록 어둡다" 계열 GT 상관 아티팩트의 코퍼스 계측.

근거
----
Geirhos et al. (Nature MI 2020): 상관이 존재하면 망은 반드시 그것을 학습한다.
이 코퍼스의 알려진 위험(README·realism_v1_final §4.2 치명 2번)은 **낙차 깊이 ↔ 픽셀
휘도**의 합성 상관이다. 본 도구는 렌더 산출물만으로(GPU 0, 모델 0) 그 상관을 세
층위에서 계측한다 — `scene_audit_realism_survey_v1.md` §5.1 권고 7의 v1 구현.

측정 3종
----
(1) **낙차 유무 × 지면대 암부 비율** (코퍼스 상관): hard negative N1~N5 는 정의상
    GT 낙차 0(발명 수치 아님 — 씬 정체성), 나머지는 낙차 보유. 판정컷 하단 밴드의
    암부 비율(선형 휘도 < 0.10)이 두 군에서 계통적으로 갈리면, 모델은 "어두우면
    낙차"를 배울 수 있다. 점이연 상관(point-biserial)과 군별 중앙값을 보고한다.
(2) **톤 클립율** (씬별): 표시 휘도 > 0.75 / < 0.10 픽셀 비율 — 시스템 감사
    (worst5-tone-ends)의 상시 계기화. 정보가 죽은 화소는 단서도 죽는다.
(3) **지평선 픽셀 행 분포** (데이터 런): variation.json 의 컷별 cam 에서 지평선
    행을 해석적으로 재구성(행 = H/2 − f_px·tan(pitch), f_px = (H/2)/tan(vFOV/2)).
    분포가 한 값에 붕괴하면 수직 위치 지름길(van Dijk ICCV'19)이 열린다.

사용
----
    python3 scripts/shortcut_audit.py --round 260806_w3_allview5          # (1)(2)
    python3 scripts/shortcut_audit.py --data dataset/260730_data_mini    # (3)
    python3 scripts/shortcut_audit.py --round R --json out.json          # 기계 판독
"""
import argparse
import glob
import json
import math
import os
import sys

import numpy as np
from PIL import Image

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# GT 낙차 부재 씬 — 발명 수치가 아니라 씬 정체성(README §배치1: "hard negative 5
# (N1~N5, GT = 낙차 없음)"). 나머지 전 씬은 낙차 보유가 정체성이다.
NO_DROP = {"sceneN1", "sceneN2", "sceneN3", "sceneN4", "sceneN5"}

# 판정 1순위 시점 우선(h0.3), 없으면 라운드의 아무 pt/rt 컷.
_PRIORITY = ("pt_noon_preset_h0.3_d5.png", "pt_noon_preset_h0.3_d2.png",
             "pt_noon_preset_h0.3_d10.png")


def _srgb_to_linear(a):
    return np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)


def _load_lum(path):
    with Image.open(path) as im:
        a = np.asarray(im.convert("RGB")).astype(np.float64) / 255.0
    lin = _srgb_to_linear(a)
    return lin @ (0.2126, 0.7152, 0.0722)


def _cuts_for_scene(scene_dir, round_name):
    d = os.path.join(scene_dir, round_name)
    if not os.path.isdir(d):
        return []
    for p in _PRIORITY:
        f = os.path.join(d, p)
        if os.path.isfile(f):
            return [f]
    return sorted(glob.glob(os.path.join(d, "pt_noon_*.png")))[:1] or \
        sorted(glob.glob(os.path.join(d, "rt_noon_*.png")))[:1]


def audit_round(round_name):
    rows = []
    for scene_dir in sorted(glob.glob(os.path.join(REPO, "look_check",
                                                   "scene*"))):
        scene = os.path.basename(scene_dir)
        cuts = _cuts_for_scene(scene_dir, round_name)
        if not cuts:
            continue
        lum = _load_lum(cuts[0])
        h = lum.shape[0]
        ground = lum[int(h * 0.55):, :]          # 하단 45 % = 지면대 근사
        disp = np.where(lum <= 0.0031308, 12.92 * lum,
                        1.055 * lum ** (1 / 2.4) - 0.055)
        rows.append(dict(
            scene=scene, cut=os.path.basename(cuts[0]),
            has_drop=scene not in NO_DROP,
            dark_frac=float((ground < 0.10).mean()),
            deep_dark_frac=float((ground < 0.02).mean()),
            clip_hi=float((disp > 0.75).mean()),
            clip_lo=float((disp < 0.10).mean()),
            ground_median=float(np.median(ground)),
        ))
    return rows


def point_biserial(rows, key):
    a = np.array([r[key] for r in rows if r["has_drop"]])
    b = np.array([r[key] for r in rows if not r["has_drop"]])
    allv = np.array([r[key] for r in rows])
    if len(a) < 2 or len(b) < 2 or allv.std() < 1e-12:
        return None
    p = len(a) / len(allv)
    return float((a.mean() - b.mean()) / allv.std() *
                 math.sqrt(p * (1 - p)))


def audit_data_run(run_dir):
    rows = []
    for vj in sorted(glob.glob(os.path.join(run_dir, "*", "*",
                                            "variation.json"))):
        v = json.load(open(vj))
        for c in v.get("cuts", []):
            cam = c.get("cam") or {}
            pitch = cam.get("pitch")
            vfov = cam.get("vfov") or cam.get("vFOV")
            if pitch is None and "tgt" in cam and "eye" in cam:
                dx = np.subtract(cam["tgt"], cam["eye"])
                pitch = math.degrees(math.atan2(dx[2],
                                                math.hypot(dx[0], dx[1])))
            if pitch is None:
                continue
            H = 1080.0
            if vfov is None:
                # hFOV 58~66 · 16:9 → vFOV = 2·atan(tan(hFOV/2)·9/16)
                hfov = cam.get("hfov", 62.2)
                vfov = math.degrees(2 * math.atan(
                    math.tan(math.radians(hfov) / 2) * 9.0 / 16.0))
            f_px = (H / 2) / math.tan(math.radians(vfov) / 2)
            row = H / 2 - f_px * math.tan(math.radians(pitch))
            rows.append(dict(scene=v["scene"], cond=c.get("cond"),
                             horizon_row=float(row)))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--round")
    ap.add_argument("--data")
    ap.add_argument("--json")
    args = ap.parse_args()
    out = {}

    if args.round:
        rows = audit_round(args.round)
        out["round"] = args.round
        out["scenes"] = rows
        out["r_pb_dark"] = point_biserial(rows, "dark_frac")
        out["r_pb_deep"] = point_biserial(rows, "deep_dark_frac")
        drop = [r for r in rows if r["has_drop"]]
        nod = [r for r in rows if not r["has_drop"]]
        print(f"[shortcut] round {args.round} — 씬 {len(rows)} "
              f"(낙차 {len(drop)} / 무낙차 {len(nod)})")
        print(f"  지면대 암부(<0.10) 중앙값: 낙차군 "
              f"{np.median([r['dark_frac'] for r in drop]):.3f} vs 무낙차군 "
              f"{np.median([r['dark_frac'] for r in nod]):.3f}")
        print(f"  점이연 상관 r_pb: dark {out['r_pb_dark']} · "
              f"deep {out['r_pb_deep']}")
        print(f"  {'scene':12s} {'drop':4s} {'dark%':>6s} {'deep%':>6s} "
              f"{'clipHi%':>7s} {'clipLo%':>7s}")
        for r in sorted(rows, key=lambda x: -x["dark_frac"]):
            print(f"  {r['scene']:12s} {'O' if r['has_drop'] else '·':4s} "
                  f"{100*r['dark_frac']:6.1f} {100*r['deep_dark_frac']:6.1f} "
                  f"{100*r['clip_hi']:7.1f} {100*r['clip_lo']:7.1f}")

    if args.data:
        rows = audit_data_run(args.data)
        out["data_run"] = args.data
        if rows:
            hr = np.array([r["horizon_row"] for r in rows])
            out["horizon"] = dict(n=len(rows), mean=float(hr.mean()),
                                  sd=float(hr.std()),
                                  p5=float(np.percentile(hr, 5)),
                                  p95=float(np.percentile(hr, 95)),
                                  n_unique_px=int(len(np.unique(
                                      np.round(hr)))))
            h = out["horizon"]
            print(f"[shortcut] data {args.data} — 컷 {h['n']}: 지평선 행 "
                  f"{h['mean']:.0f}±{h['sd']:.0f} px (p5 {h['p5']:.0f} / "
                  f"p95 {h['p95']:.0f} / 고유 픽셀행 {h['n_unique_px']})")
            if h["n_unique_px"] <= 3:
                print("  ⚠ 지평선이 사실상 한 값 — 수직 위치 지름길 열림 "
                      "(van Dijk ICCV'19)")
        else:
            print("[shortcut] variation.json 에서 카메라 각을 찾지 못함")

    if args.json:
        json.dump(out, open(args.json, "w"), ensure_ascii=False, indent=1)
        print(f"[shortcut] json → {args.json}")


if __name__ == "__main__":
    main()
