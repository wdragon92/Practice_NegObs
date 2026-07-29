#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""스카이라인/중경 지표 측정기 — `E_midground_profile.md` §1.6 정본.

E조 조사(통람 결함 ② "중경 진공 — 지평선 칼절단")가 의존하는 도구이며,
`t1_material_layer_spec_v1.md` v1.1 §3.4(c) 가 재작성을 지시한 3종 중 하나다.
v1 측정기는 scratchpad 세션 소멸로 부재했다.

방법 (E §1.6 축자 이행)
    열마다 **최상단이 하늘인 경우에만** 아래로 훑어 최초 비하늘 행을 찾는다.
    하늘이 안 열린 열은 스카이라인 통계에서 제외한다(벽·사면이 하늘을 막은 열).

하늘 판정 규칙 2종 — **기본은 `e`** (published 앵커가 이 규칙으로 산출됐다)
    e  : (B−R)/255 > 0.030  ∧  (B−G)/255 > 0.012  ∧  B/255 > 0.40   [E §1.6]
    t1 : (B > R) ∧ (B > G) ∧ min(R,G,B)/255 > 0.35                  [t1 §3.4(c)]
    두 규칙은 같은 컷에서 다른 값을 낸다 — scene18 `v7_pt h0.3_d5` 의 runmax 는
    `e` 844(= E 표 앵커) vs `t1` 1269 `[실측]`. 앵커 재현이 정의의 우선이므로
    `e` 를 기본값으로 두고, `t1` 은 `--sky t1` 로 남긴다.
    **HDRI 가 바뀌면 두 규칙 다 재검증할 것**(정의 고정의 대가 — t1 §3.4(c) 경고).

지표
    sky%      = 100 · mean(하늘 마스크)                     전 프레임(화소 기준)
    skycol%   = 100 · (최상단이 하늘인 열) / W              E 표의 "하늘열%"
    horizon[c]= 그 열의 최초 비하늘 행. 전부 하늘이면 H
    edge_med  = median(horizon) · edge_std = std(horizon)   스카이라인 요철
    runmax    = horizon 이 **±2행 이내로 이어지는 최장 연속 열 수**   목표 ≤ 320 px
                (연쇄 정의 · 열 인접 요구 — `runmax_of` 도크스트링 참조.
                 E §1.6 표 23개 앵커가 이 정의에서 전부 재현된다 `[실측]`)
    flat%     = 100·mean(local_std(Y/255,5) < 1/255)  상단 1/3 (= imgstats `flat_sky`)

목표값 (E §1.6) : runmax ≤ 320 px = 프레임 폭 1/6 = 10.0°.
거리대 라벨링(S1 3거리대 규칙)은 프림 거리가 필요해 **본 스크립트 범위 밖**이다.
대신 `--bands` 로 열 구간 3분할(L/M/R) 별 runmax·edge_std 를 낸다.

의존성 numpy + PIL 뿐. **GPU 0 · 부작용 0.**

사용:
    python3 scripts/skyline.py 'look_check/scene19/*/pt_noon_preset_h0.3_d*.png'
    python3 scripts/skyline.py 'look_check/scene18/v7_pt/pt_noon_preset_h0.3_d5.png' --bands
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys

import numpy as np
from PIL import Image

RUNMAX_TARGET = 320.0      # E §1.6 — 프레임 폭 1/6(10.0°). 초과 = 칼절단
SKYCOL_MIN = 20.0          # 하늘이 이만큼 안 열린 씬은 실루엣 판정 대상이 아니다
RUN_TOL = 2                # "±2행 이내"


def sky_mask(a255, rule="e"):
    """하늘 마스크. a255 = float RGB 0~255."""
    R, G, B = a255[..., 0], a255[..., 1], a255[..., 2]
    if rule == "t1":
        return (B > R) & (B > G) & (a255.min(axis=-1) / 255.0 > 0.35)
    # 기본 `e` — E §1.6 무운 puresky 전용 규칙
    return (((B - R) / 255.0 > 0.030) & ((B - G) / 255.0 > 0.012)
            & (B / 255.0 > 0.40))


def horizon_of(sky):
    """(열 인덱스, 최초 비하늘 행) — 최상단이 하늘인 열만."""
    H, W = sky.shape
    cols = np.where(sky[0])[0]
    if len(cols) == 0:
        return cols, np.zeros(0, dtype=np.int32)
    sub = sky[:, cols]
    nonsky = ~sub
    any_ns = nonsky.any(axis=0)
    first = np.where(any_ns, nonsky.argmax(axis=0), H)
    return cols, first.astype(np.int32)


def runmax_of(cols, hz):
    """±RUN_TOL 이내로 이어지는 최장 **연속 열** 수.

    연쇄 조건 2개를 **둘 다** 요구한다:
      ① |horizon[i] − horizon[i−1]| ≤ RUN_TOL   (±2행 이내로 평탄)
      ② cols[i] − cols[i−1] == 1                (열 번호가 실제로 인접)
    ②가 없으면 하늘이 안 열린 열(벽·수목)을 건너뛰어 연쇄가 이어져 버린다.
    앵커 재현으로 확정한 조건이다 — ② 없이는 scene16 132(앵커 66) ·
    scene03 160(89) · scene10 101(69) · sceneN4 429(281) 로 전부 과대평가되고,
    ②를 넣으면 E §1.6 표 **23개 앵커가 전부 일치**한다 `[실측]`.
    """
    if len(hz) == 0:
        return 0
    best = cur = 1
    for i in range(1, len(hz)):
        ok = (abs(int(hz[i]) - int(hz[i - 1])) <= RUN_TOL
              and int(cols[i]) - int(cols[i - 1]) == 1)
        cur = cur + 1 if ok else 1
        if cur > best:
            best = cur
    return int(best)


def local_std(g, k=5):
    """박스필터 기반 국소 표준편차 — `imgstats.local_std` 와 동일 구현."""
    pad = k // 2

    def boxsum(a):
        cc = np.cumsum(np.cumsum(np.pad(a, pad, mode="reflect"), 0), 1)
        cc = np.pad(cc, ((1, 0), (1, 0)))
        H, W = g.shape
        return (cc[k:k + H, k:k + W] - cc[0:H, k:k + W]
                - cc[k:k + H, 0:W] + cc[0:H, 0:W])

    s1, s2 = boxsum(g), boxsum(g * g)
    n = k * k
    return np.sqrt(np.maximum(s2 / n - (s1 / n) ** 2, 0.0))


def skyline(path, rule="e", bands=False):
    a = np.asarray(Image.open(path).convert("RGB")).astype(np.float64)
    H, W = a.shape[:2]
    sky = sky_mask(a, rule)
    cols, hz = horizon_of(sky)
    y = (0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]) / 255.0
    out = dict(
        path=path, name=os.path.basename(path), H=int(H), W=int(W), rule=rule,
        sky_pct=100.0 * float(sky.mean()),
        skycol_pct=100.0 * len(cols) / float(W),
        edge_med=float(np.median(hz)) if len(hz) else float("nan"),
        edge_std=float(hz.std()) if len(hz) else float("nan"),
        runmax=runmax_of(cols, hz),
        flat_sky=100.0 * float((local_std(y, 5)[:H // 3] < 1.0 / 255).mean()),
    )
    out["runmax_pct"] = 100.0 * out["runmax"] / float(W)
    out["verdict"] = ("n/a(하늘 미개방)" if out["skycol_pct"] < SKYCOL_MIN
                      else ("OK" if out["runmax"] <= RUNMAX_TARGET else "칼절단"))
    if bands:
        third = W // 3
        for tag, lo, hi in (("L", 0, third), ("M", third, 2 * third),
                            ("R", 2 * third, W)):
            m = (cols >= lo) & (cols < hi)
            h2 = hz[m]
            out[f"runmax_{tag}"] = runmax_of(cols[m], h2)
            out[f"edge_std_{tag}"] = float(h2.std()) if len(h2) else float("nan")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="스카이라인 지표 (E_midground_profile §1.6 정본)")
    ap.add_argument("patterns", nargs="+", help="PNG glob 패턴 (** 재귀 지원)")
    ap.add_argument("--sky", choices=("e", "t1"), default="e",
                    help="하늘 판정 규칙 (기본 e = E 표 앵커 재현)")
    ap.add_argument("--bands", action="store_true", help="열 3분할(L/M/R) 병기")
    ap.add_argument("--json", help="기계 판독용 JSON 출력 경로")
    a = ap.parse_args(argv)

    paths = []
    for pat in a.patterns:
        for p in sorted(glob.glob(pat, recursive=True)):
            if os.path.isfile(p) and p not in paths:
                paths.append(p)
    if not paths:
        print("[에러] 대상 파일 0건", file=sys.stderr)
        return 2

    rows = []
    for p in paths:
        try:
            rows.append(skyline(p, a.sky, a.bands))
        except Exception as e:
            print(f"[경고] {p}: {e}", file=sys.stderr)
    if not rows:
        return 2

    hdr = (f"{'cut':<46}{'sky%':>7}{'하늘열%':>9}{'edge_med':>10}"
           f"{'edge_std':>10}{'runmax':>8}{'폭%':>7}{'flat_sky':>10}  판정")
    if a.bands:
        hdr += "   L/M/R runmax"
    print(hdr)
    print("-" * (len(hdr) + 10))
    for s in rows:
        lbl = os.path.join(os.path.basename(os.path.dirname(s["path"])), s["name"])
        line = (f"{lbl[:45]:<46}{s['sky_pct']:>7.1f}{s['skycol_pct']:>9.1f}"
                f"{s['edge_med']:>10.0f}{s['edge_std']:>10.1f}{s['runmax']:>8}"
                f"{s['runmax_pct']:>7.1f}{s['flat_sky']:>10.1f}  {s['verdict']}")
        if a.bands:
            line += (f"   {s['runmax_L']}/{s['runmax_M']}/{s['runmax_R']}")
        print(line)

    if a.json:
        os.makedirs(os.path.dirname(os.path.abspath(a.json)) or ".", exist_ok=True)
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False, indent=1)
        print(f"\nJSON → {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
