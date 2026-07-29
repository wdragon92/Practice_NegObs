#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""노멀맵 접선 스펙트럼 측정기 — `t1_material_layer_spec_v1.md` v1.1 §3.4(a) 정본.

이 파일이 `macro%` · `hf%` · `slope_n` · `접선 RMS` 의 **유일한 정의 원천**이다
(§1.2 표 · §3.1 합격 기준 · §3.3 β 규약이 전부 이 정의에 걸려 있다).
v1 의 측정기는 scratchpad 세션 소멸로 부재했고, 레드팀이 v1 이 적은 방법을
6개 변형으로 재현 시도해 전부 실패했다 `[redteam_w1_design.md §2.6]`.
그래서 v1.1 은 정의를 **문서가 아니라 코드로** 고정하기로 했다 — 이 파일이 그것이다.

정의(§3.4(a) 축자 이행):
  1) 로드      PIL → RGB uint8 → float32/255. **sRGB 역감마 금지**(노멀맵은 선형 데이터)
  2) 접선 성분 nx = 2R − 1 , ny = 2G − 1      (B/nz 미사용 ⇒ DX/GL 구분 불요)
  3) 크롭      네이티브 해상도에서 중앙 정사각 N=1024. **리샘플 금지**.
               원본 변이 1024 미만이면 N = min(변) 으로 낮추고 출력에 각인
  4) 창함수    분리형 Hann. **창 가중 평균을 먼저 뺀다** — 재현 실패의 주 분기점
  5) FFT       P = |F_nx|² + |F_ny|²
  6) 방사 링   r = rint(hypot(dy,dx)) 정수 픽셀
  7) 정규화    T = Σ_{r=1..N/2} sm[r]  — **링 총합 가중**(링 평균 가중 아님). DC 제외
  8) 지표      macro%(1≤r<N/32) · hf%(N/4≤r≤N/2) · slope_n(3≤r<N/4) · RMS(창 이전)
  9) 판정      --gate 시 §3.1 문턱으로 PASS/FAIL. 종료코드 = FAIL 수

의존성 numpy + PIL 뿐. **GPU 0 · 부작용 0.**

사용:
    python3 scripts/norm_spec.py 'assets/**/*_nor*.jpg' [--json out.json] [--n 1024] [--gate]
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import os
import sys

import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None          # 4096² 노멀맵은 PIL 의 폭탄 경고 대상이 아니다

# ---------------------------------------------------------------------------
# §3.1 합격 기준 (v1.1 재캘리브레이션). 숫자의 근거는 전부 스펙 §3.1 표에 있다.
# ---------------------------------------------------------------------------
GATE_MACRO_MAX = 10.0     # 모듈형 타일 맵 배제. 통과군 최대 8.7 vs 탈락군 최소 11.9
GATE_SLOPE_MIN = -0.9     # 0 에 가까울수록 백색잡음 = 진짜 미세 그레인
GATE_SLOPE_MAX = 0.3      # [v1.1 신설] 순수 텍셀 해시(+1.4) 배제 — 원경 반짝임 방지
GATE_RMS_MIN = 0.12       # 0.056(현행 concrete_wall)은 안 보인다
GATE_RMS_MAX = 0.35       # 0.5 이상은 지면이 자갈처럼 튄다
GATE_HF_MIN = 10.0        # 보조(교차 확인용). 판정 단독 근거로 쓰지 말 것

N_DEFAULT = 1024


# ---------------------------------------------------------------------------
def load_tangent(path, n_req=N_DEFAULT):
    """(nx, ny, N) — 중앙 정사각 크롭의 접선 성분. 리샘플 0단."""
    im = Image.open(path)
    if im.mode != "RGB":
        im = im.convert("RGB")
    a = np.asarray(im, dtype=np.uint8).astype(np.float32) / 255.0
    h, w = a.shape[:2]
    n = int(min(n_req, h, w))
    y0 = (h - n) // 2
    x0 = (w - n) // 2
    c = a[y0:y0 + n, x0:x0 + n]
    nx = 2.0 * c[..., 0] - 1.0
    ny = 2.0 * c[..., 1] - 1.0
    return nx, ny, n


def radial_power(nx, ny, n):
    """(sm, cnt, prof) — 링 파워 총합 · 링 화소 수 · 링 평균."""
    w = np.hanning(n)
    W = np.outer(w, w)
    sW = W.sum()
    P = None
    for x in (nx, ny):
        # §3.4(a) 4) — 창 가중 평균을 먼저 뺀 다음 창을 곱한다.
        xp = (x - float((W * x).sum() / sW)) * W
        F = np.fft.fftshift(np.fft.fft2(xp))
        p = (F.real ** 2 + F.imag ** 2)
        P = p if P is None else P + p
    cy = cx = n // 2                                   # fftshift 후 DC 위치
    yy, xx = np.ogrid[:n, :n]
    r = np.rint(np.hypot(yy - cy, xx - cx)).astype(np.int32)
    nb = int(r.max()) + 1
    sm = np.bincount(r.ravel(), weights=P.ravel(), minlength=nb)
    cnt = np.bincount(r.ravel(), minlength=nb).astype(np.float64)
    with np.errstate(invalid="ignore", divide="ignore"):
        prof = np.where(cnt > 0, sm / np.maximum(cnt, 1), 0.0)
    return sm, cnt, prof


def spectrum(path, n_req=N_DEFAULT):
    """§3.4(a) 전 항목. dict 반환."""
    nx, ny, n = load_tangent(path, n_req)
    rms = float(math.sqrt(float(np.mean(nx * nx + ny * ny))))   # 9) 창·평균제거 **이전**
    sm, cnt, prof = radial_power(nx, ny, n)
    rnyq = n // 2
    tot = float(sm[1:rnyq + 1].sum())                            # 7) DC 제외 링 총합
    if tot <= 0:
        macro = hf = float("nan")
    else:
        macro = 100.0 * float(sm[1:max(2, n // 32)].sum()) / tot
        hf = 100.0 * float(sm[n // 4:rnyq + 1].sum()) / tot
    # 8) slope_n — log10 prof vs log10 r 최소제곱, 구간 3 ≤ r < N/4, prof>0 만
    lo, hi = 3, n // 4
    rr = np.arange(lo, hi)
    pv = prof[lo:hi]
    m = pv > 0
    if m.sum() >= 3:
        slope = float(np.polyfit(np.log10(rr[m]), np.log10(pv[m]), 1)[0])
    else:
        slope = float("nan")
    return dict(path=path, name=os.path.basename(path), N=n,
                slope_n=slope, macro_pct=macro, hf_pct=hf, rms=rms)


def verdict(s):
    """§3.1 문턱 판정. (PASS/FAIL, 불통과 사유 리스트)."""
    bad = []
    if not (s["macro_pct"] < GATE_MACRO_MAX):
        bad.append(f"macro%{s['macro_pct']:.1f}≥{GATE_MACRO_MAX:g}")
    if not (s["slope_n"] > GATE_SLOPE_MIN):
        bad.append(f"slope_n{s['slope_n']:.2f}≤{GATE_SLOPE_MIN:g}")
    if not (s["slope_n"] <= GATE_SLOPE_MAX):
        bad.append(f"slope_n{s['slope_n']:.2f}>{GATE_SLOPE_MAX:g}")
    if not (GATE_RMS_MIN <= s["rms"] <= GATE_RMS_MAX):
        bad.append(f"RMS{s['rms']:.3f}∉[{GATE_RMS_MIN:g},{GATE_RMS_MAX:g}]")
    if not (s["hf_pct"] >= GATE_HF_MIN):
        bad.append(f"hf%{s['hf_pct']:.1f}<{GATE_HF_MIN:g}(보조)")
    return ("FAIL" if bad else "PASS"), bad


# ---------------------------------------------------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser(
        description="노멀맵 접선 스펙트럼 (t1 spec v1.1 §3.4(a) 정본)")
    ap.add_argument("patterns", nargs="+", help="glob 패턴 (** 재귀 지원)")
    ap.add_argument("--n", type=int, default=N_DEFAULT, help="크롭 변 길이 (기본 1024)")
    ap.add_argument("--json", help="기계 판독용 JSON 출력 경로")
    ap.add_argument("--gate", action="store_true", help="§3.1 문턱 판정 + 종료코드")
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
            rows.append(spectrum(p, a.n))
        except Exception as e:                      # 한 장 실패로 전체가 죽지 않게
            print(f"[경고] {p}: {e}", file=sys.stderr)

    hdr = f"{'map':<40}{'N':>6}{'slope_n':>9}{'macro%':>8}{'hf%':>7}{'RMS':>8}"
    if a.gate:
        hdr += "  판정"
    print(hdr)
    print("-" * (len(hdr) + 20))
    fails = 0
    for s in rows:
        line = (f"{s['name'][:39]:<40}{s['N']:>6}{s['slope_n']:>9.2f}"
                f"{s['macro_pct']:>8.1f}{s['hf_pct']:>7.1f}{s['rms']:>8.3f}")
        if a.gate:
            v, bad = verdict(s)
            s["verdict"], s["fails"] = v, bad
            fails += (v == "FAIL")
            line += f"  {v}" + (("  " + ", ".join(bad)) if bad else "")
        print(line)

    if a.json:
        os.makedirs(os.path.dirname(os.path.abspath(a.json)) or ".", exist_ok=True)
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False, indent=1)
        print(f"\nJSON → {a.json}")
    return fails if a.gate else 0


if __name__ == "__main__":
    sys.exit(main())
