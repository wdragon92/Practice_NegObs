#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""품질 지표 계측기 — `Docs/reports/s04_quality_gap_survey_v1.md` §1.2 지표 재현 (GT-108 ⑦)

**무엇을 위한 도구인가**
  s04 품질 격차 조사가 정의한 지표들은 세션 스크래치의 임시 스크립트로 계산됐고
  리포에 커밋되지 않았다(§1.2 말미). 그래서 파일럿 A(GT-108)의 합격선

      근경 `micro_sd` ≥ 8 · `gnd_flat%` ≤ 5 · `gnd_chroma` ≥ 0.05 ·
      `w80` ≤ 5 · `tile_peak@8px` ≤ 0.7

  을 **판정할 수단이 리포 안에 없었다.** 본 스크립트가 그 수단이다. 렌더 후
  오케스트레이터가 라운드 PNG 에 그대로 돌려 합격/불합격을 읽는다.

**`scripts/imgstats.py` 와의 관계 — 대체가 아니라 보완**
  `imgstats.py` 는 **긴 변 1024 로 다운샘플**한 뒤 계산한다(`:95-106`). 조사 §3 의
  수치는 **원본 해상도**에서 잰 것이고, §3.2 의 크롭 창 `x 300…1620, y 620…1060`
  도 원본 픽셀 좌표다. 다운샘플은 `micro_sd`(5×5 창 국소 표준편차)를 직접
  깎아먹으므로 **두 파이프라인의 수를 섞어 읽으면 안 된다.** 본 스크립트는
  기본 원본 해상도이고, `--long-side` 로만 다운샘플한다.
  커널·`lum()` 정의는 `imgstats.py` 와 동일하게 맞췄다(교차 검증 가능).

**지표 정의는 §1.2 를 그대로 옮긴 것이다**
  micro_sd    = median(local_std(luma,5x5)) x 255      — 재질 입도(8비트 레벨)
  flat%       = 100 x mean(local_std(luma,5x5) < 1/255) — 죽은 평면 픽셀 비율
  gnd_*       = **하단 35 %** 밴드에 같은 계산(보행자가 보는 노면)
  gnd_chroma  = mean(max(RGB) - min(RGB))               — 무채색이면 0
  w80 / w75   = 하단 2/3 에서 min(R,G,B) > 0.80 / 0.75 인 픽셀 비율
                (**sRGB 표시값 — 선형화하지 않는다**, t1 §2.2 정의 그대로)
  sat         = 하단 2/3 의 mean((max-min)/max)
  mean_lum    = 하단 2/3 평균 휘도
  bins50      = 채널당 16단계 양자화에서 화면의 50 %를 덮는 데 필요한 색 구간 수
  modal_tile% = 16 px 타일 평균휘도의 최빈 2 % 버킷이 차지하는 타일 비율
  tile_peak   = 자기상관 최대 피크(lag >= 8 px) — 축별로 2개(가로/세로)
  edge>0.02%  = 인접 픽셀 휘도 기울기 크기가 0.02 를 넘는 픽셀 비율
  bound/W     = 하늘/비하늘 경계 픽셀 수 / 프레임 폭 — 실루엣 복잡도
                **주의**: §1.2 는 하늘 마스크 정의를 남기지 않았다. 여기서는
                (B > R) & (luma > 0.5) 로 잡는다 — 조사 표의 재현 검증 대상이
                아니므로 참고 열로만 읽을 것.

사용:
    python3 scripts/quality_metrics_probe.py --png A.png B.png ...
    python3 scripts/quality_metrics_probe.py --png A.png --crop 300,620,1620,1060
    python3 scripts/quality_metrics_probe.py --png A.png --crop full   # 크롭 끔
    python3 scripts/quality_metrics_probe.py --png '<round>/pt_noon_*.png' --gate
    python3 scripts/quality_metrics_probe.py --selftest    # 조사 §3 수치 재현 검증

`--crop` 무지정 = §3.2 근경 지면 크롭 창 `300,620,1620,1060` **기본 적용**(전 컷 동일
창). 조사 §3.2 표와 직접 비교되는 열은 `crop_*` 접두 열이다.
종료코드: 0 = 정상(또는 --gate 전항목 통과) · 1 = --gate 불합격 · 2 = 입력 오류
"""

import argparse
import glob
import os
import sys

import numpy as np
from PIL import Image

# §3.2 근경 지면 크롭 창 (x0, y0, x1, y1) — 전 컷 동일
CROP_NEAR_GROUND = (300, 620, 1620, 1060)

# §7 파일럿 A 합격선. (하한, 상한) — None = 제한 없음
PASS_A = dict(
    crop_micro_sd=(8.0, None),
    gnd_flat=(None, 5.0),
    gnd_chroma=(0.05, None),
    w80=(None, 5.0),
    crop_tile_peak=(None, 0.7),
)


# ---------------------------------------------------------------------------
# 기본 연산 — `imgstats.py` 와 같은 정의
# ---------------------------------------------------------------------------
def lum(rgb):
    return 0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]


def local_std(g, k=5):
    """박스필터(적분영상) 국소 표준편차 — `imgstats.local_std` 와 동일."""
    pad = k // 2

    def boxsum(a):
        cc = np.cumsum(np.cumsum(np.pad(a, pad, mode="reflect"), 0), 1)
        cc = np.pad(cc, ((1, 0), (1, 0)))
        H, W = g.shape
        return (cc[k:k + H, k:k + W] - cc[0:H, k:k + W]
                - cc[k:k + H, 0:W] + cc[0:H, 0:W])

    s1 = boxsum(g)
    s2 = boxsum(g * g)
    n = k * k
    var = np.maximum(s2 / n - (s1 / n) ** 2, 0)
    return np.sqrt(var)


def load(path, long_side=0):
    """sRGB 표시값 0~1 배열. long_side>0 이면 긴 변을 그 값으로 다운샘플."""
    with Image.open(path) as im:
        im = im.convert("RGB")
        if long_side and max(im.size) > long_side:
            s = long_side / float(max(im.size))
            im = im.resize((int(im.size[0] * s), int(im.size[1] * s)),
                           Image.LANCZOS)
        return np.asarray(im).astype(np.float64) / 255.0


# ---------------------------------------------------------------------------
# 지표
# ---------------------------------------------------------------------------
def micro(g):
    """(micro_sd, flat%) — 5×5 국소 표준편차 기반."""
    ls = local_std(g, 5)
    return float(np.median(ls) * 255.0), float(100.0 * (ls < 1.0 / 255.0).mean())


def chroma(rgb):
    return float((rgb.max(-1) - rgb.min(-1)).mean())


def sat_mean(rgb):
    mx, mn = rgb.max(-1), rgb.min(-1)
    return float(np.where(mx > 1e-6, (mx - mn) / np.maximum(mx, 1e-6), 0).mean())


def white_frac(rgb, thr):
    """min(R,G,B) > thr 인 픽셀 비율 [%] — sRGB 표시값 기준(선형화 없음)."""
    return float(100.0 * (rgb.min(-1) > thr).mean())


def bins50(rgb):
    """채널당 16단계 양자화. 화면의 50 %를 덮는 데 필요한 색 구간 수."""
    q = np.clip((rgb * 16).astype(np.int32), 0, 15)
    key = (q[..., 0] * 256 + q[..., 1] * 16 + q[..., 2]).ravel()
    cnt = np.sort(np.bincount(key))[::-1]
    return int(np.searchsorted(np.cumsum(cnt), 0.5 * key.size) + 1)


def modal_tile(g, tile=16):
    """16 px 타일 평균휘도의 최빈 2 % 버킷이 차지하는 타일 비율 [%]."""
    H, W = g.shape
    h, w = H // tile, W // tile
    if h < 1 or w < 1:
        return float("nan")
    t = g[:h * tile, :w * tile].reshape(h, tile, w, tile).mean(axis=(1, 3))
    b = np.clip((t * 50).astype(np.int32), 0, 49)      # 2 % 폭 버킷 50개
    return float(100.0 * np.bincount(b.ravel(), minlength=50).max() / b.size)


def tile_peak(g, min_lag=8):
    """축별 정규화 자기상관의 lag>=min_lag 최대 피크. (가로, 세로, lag_x, lag_y)."""
    out = []
    for axis in (1, 0):
        x = g - g.mean(axis=axis, keepdims=True)
        n = x.shape[axis]
        if n <= min_lag + 1:
            out.extend([float("nan"), 0])
            continue
        # 축을 따라 lag 상관을 직접 계산(평균 프로파일이 아니라 2D 상관의 평균)
        var = (x * x).mean()
        if var <= 1e-12:
            out.extend([0.0, 0])
            continue
        lags = range(min_lag, min(n // 2, 128))
        best, bl = -1.0, min_lag
        for L in lags:
            if axis == 1:
                c = (x[:, :-L] * x[:, L:]).mean()
            else:
                c = (x[:-L, :] * x[L:, :]).mean()
            r = float(c / var)
            if r > best:
                best, bl = r, L
        out.extend([best, bl])
    return out[0], out[1], out[2], out[3]        # (peak_x, lag_x, peak_y, lag_y)


def edge_frac(g, thr=0.02):
    gy, gx = np.gradient(g)
    return float(100.0 * (np.sqrt(gx * gx + gy * gy) > thr).mean())


def sky_bound(rgb):
    """(하늘 %, bound/W). 하늘 마스크는 근사 — 모듈 docstring의 주의 참조."""
    g = lum(rgb)
    sky = (rgb[..., 2] > rgb[..., 0]) & (g > 0.5)
    H, W = sky.shape
    b = (sky[:, :-1] != sky[:, 1:]).sum() + (sky[:-1, :] != sky[1:, :]).sum()
    return float(100.0 * sky.mean()), float(b / float(W))


def measure(path, crop=CROP_NEAR_GROUND, long_side=0):
    rgb = load(path, long_side)
    H, W = rgb.shape[:2]
    g = lum(rgb)
    m = dict(png=os.path.basename(path), w=W, h=H)
    m["micro_sd"], m["flat"] = micro(g)
    m["edge"] = edge_frac(g)
    # 하단 35 % — 노면 밴드
    gnd = rgb[int(H * 0.65):]
    m["gnd_micro_sd"], m["gnd_flat"] = micro(lum(gnd))
    m["gnd_chroma"] = chroma(gnd)
    # 하단 2/3 — 톤·순백·채도
    low = rgb[H // 3:]
    m["w80"] = white_frac(low, 0.80)
    m["w75"] = white_frac(low, 0.75)
    m["sat"] = sat_mean(low)
    m["mean_lum"] = float(lum(low).mean())
    m["modal_tile"] = modal_tile(g)
    m["bins50"] = bins50(rgb)
    m["sky"], m["bound_w"] = sky_bound(rgb)
    # §3.2 크롭 창
    if crop:
        x0, y0, x1, y1 = crop
        x0, y0 = max(0, x0), max(0, y0)
        x1, y1 = min(W, x1), min(H, y1)
        if x1 - x0 >= 32 and y1 - y0 >= 32:
            c = rgb[y0:y1, x0:x1]
            cg = lum(c)
            m["crop_micro_sd"], m["crop_flat"] = micro(cg)
            m["crop_sd"] = float(cg.std() * 255.0)
            m["crop_chroma"] = chroma(c)
            px, lx, py, ly = tile_peak(cg)
            m["crop_tile_peak"] = max(px, py)
            m["crop_tp_x"], m["crop_tp_lx"] = px, lx
            m["crop_tp_y"], m["crop_tp_ly"] = py, ly
        else:
            m["crop_note"] = "크롭 창이 이미지 밖 — 생략"
    return m


# ---------------------------------------------------------------------------
# 출력
# ---------------------------------------------------------------------------
_COLS = [("png", "%-26s", "%-26s"), ("micro_sd", "%9s", "%9.2f"),
         ("flat", "%7s", "%7.1f"), ("edge", "%7s", "%7.1f"),
         ("gnd_micro_sd", "%9s", "%9.2f"), ("gnd_flat", "%9s", "%9.1f"),
         ("gnd_chroma", "%11s", "%11.3f"), ("w80", "%6s", "%6.1f"),
         ("w75", "%6s", "%6.1f"), ("sat", "%6s", "%6.3f"),
         ("mean_lum", "%9s", "%9.3f"), ("modal_tile", "%11s", "%11.1f"),
         ("bins50", "%7s", "%7d")]
_CCOLS = [("crop_micro_sd", "%14s", "%14.2f"), ("crop_flat", "%10s", "%10.1f"),
          ("crop_sd", "%8s", "%8.1f"), ("crop_chroma", "%12s", "%12.3f"),
          ("crop_tile_peak", "%15s", "%15.3f")]


def table(rows, crop):
    cols = list(_COLS) + (list(_CCOLS) if crop else [])
    print(" ".join(h % k for k, h, _ in cols))
    print("-" * (sum(int(h[1:-1]) for _k, h, _f in cols) + len(cols) - 1))
    for r in rows:
        cells = []
        for k, h, f in cols:
            v = r.get(k)
            cells.append((h % "-") if v is None else (f % v))
        print(" ".join(cells))
    if crop:
        print(f"\n[크롭 창] x {crop[0]}…{crop[2]}, y {crop[1]}…{crop[3]} "
              f"(조사 §3.2 근경 지면 창)")
        for r in rows:
            if "crop_tp_x" in r:
                print(f"  {r['png']:<26s} tile_peak "
                      f"{r['crop_tp_x']:.2f}@{r['crop_tp_lx']} / "
                      f"{r['crop_tp_y']:.2f}@{r['crop_tp_ly']}")


def gate(rows):
    bad = 0
    print("\n[합격선] 파일럿 A(조사 §7)")
    for r in rows:
        for k, (lo, hi) in PASS_A.items():
            v = r.get(k)
            if v is None:
                print(f"  ? {r['png']:<26s} {k:<15s} 측정 없음")
                continue
            ok = (lo is None or v >= lo) and (hi is None or v <= hi)
            bad += 0 if ok else 1
            lim = (f">= {lo}" if hi is None else
                   (f"<= {hi}" if lo is None else f"{lo}~{hi}"))
            print(f"  {'OK ' if ok else 'FAIL'} {r['png']:<26s} "
                  f"{k:<15s} {v:9.3f}  ({lim})")
    print(f"[합격선] 불합격 {bad} 건")
    return bad


# ---------------------------------------------------------------------------
# 자기검증 — 조사 §3 의 수치를 기존 라운드 PNG 로 재현한다
# ---------------------------------------------------------------------------
# 조사 §3 게재값을 §1.1 provenance 의 라운드 PNG 로 재현한다.
#   A군 = **재현 성립** — 어서션. 색공간·밴드 정의·크롭 창·문턱이 전부 맞아야 통과한다.
#   B군 = **재현 불성립** — 보고만. 조사 §1.2 말미가 밝혔듯 게재 수치를 낸 스크립트
#         (`imgstat.py` / `region.py`)는 커밋되지 않았고, §1.2 에 적힌 정의를 그대로
#         구현해도 `flat` 계열과 매끄러운 컷의 전화면 `micro_sd` 는 재현되지 않는다
#         [실측 — 본 세션에서 luma 4종(709/601/평균/PIL-L) × 커널 3/5 × 원본/1024/1280/
#         1536 다운샘플 × 선형화 유무 × 적분영상/정확창/채널평균/레인지 전수 시도, 전부
#         불일치]. 게재 표가 **두 스크립트**에서 나왔다는 §1.2 의 기술이 §3.1 과 §3.2
#         의 flat 이 서로 어긋나는 이유로 보인다(s13 은 게재값이 본 계측보다 **낮고**
#         s16/s01/s04 는 **높다** — 한 방향 오프셋이 아니다).
#   ⇒ 판정 규약: 합격선은 **본 스크립트가 낸 baseline 라운드 값과 신규 라운드 값의
#     비교**로 읽는다. 조사 표의 절대값과 직접 대조하지 말 것. B군의 baseline 값을
#     아래에 박아 두는 이유가 그것이다 — 계측기 자체가 흔들리면 여기서 먼저 잡힌다.
_ST_REPRO = [
    ("scene04/260806_w3_allview5", "pt_noon_trail_approach.png",
     [("gnd_micro_sd", 15.28, 0.6), ("gnd_chroma", 0.208, 0.01),
      ("w80", 0.2, 0.2), ("mean_lum", 0.402, 0.02), ("sat", 0.400, 0.02),
      ("micro_sd", 15.07, 0.8), ("crop_micro_sd", 15.43, 0.8),
      ("crop_sd", 38.7, 2.0), ("crop_chroma", 0.207, 0.01),
      ("crop_tile_peak", 0.64, 0.08)]),
    ("scene04/260806_w3_allview5", "pt_noon_step_detail.png",
     [("micro_sd", 12.39, 0.8), ("gnd_chroma", 0.239, 0.01), ("w80", 0.0, 0.2),
      ("crop_micro_sd", 14.44, 0.8), ("crop_tile_peak", 0.42, 0.08)]),
    ("scene16/260811_w3_s16under", "pt_noon_approach.png",
     [("gnd_chroma", 0.008, 0.01), ("w80", 1.4, 0.6), ("mean_lum", 0.641, 0.02),
      ("sat", 0.047, 0.02), ("crop_tile_peak", 0.86, 0.08)]),
    ("scene16/260811_w3_s16under", "pt_noon_shadow_band.png",
     [("gnd_chroma", 0.010, 0.01), ("w80", 2.3, 0.6), ("mean_lum", 0.615, 0.02),
      ("crop_tile_peak", 0.42, 0.08)]),
    ("scene13/260811_w3_s13frost_c", "pt_noon_entry_approach.png",
     [("w80", 1.6, 0.6), ("mean_lum", 0.387, 0.02), ("sat", 0.242, 0.02),
      ("crop_tile_peak", 0.86, 0.10)]),
    ("scene11/260811_w3_s11clean", "pt_noon_stair_head.png",
     [("w80", 9.3, 1.0), ("w75", 63.7, 3.0), ("mean_lum", 0.749, 0.02),
      ("gnd_chroma", 0.025, 0.01), ("crop_micro_sd", 10.03, 0.8)]),
    ("scene11/260811_w3_s11clean", "pt_noon_deck_walk.png",
     [("micro_sd", 17.53, 0.8), ("gnd_chroma", 0.060, 0.01), ("w80", 0.4, 0.3),
      ("mean_lum", 0.530, 0.02)]),
]

# B군 — 본 계측기의 baseline 값 [실측 2026-08-13, 위 라운드 PNG 원본 해상도].
#   (게재값은 참고로 병기). 드리프트 감시용이므로 허용오차는 좁다.
_ST_BASELINE = [
    ("scene04/260806_w3_allview5", "pt_noon_trail_approach.png",
     [("flat", 4.4, 9.6), ("gnd_flat", 0.0, 1.5), ("crop_flat", 0.0, 1.0)]),
    ("scene16/260811_w3_s16under", "pt_noon_approach.png",
     [("micro_sd", 3.60, 4.22), ("flat", 16.9, 36.9),
      ("gnd_micro_sd", 5.19, 5.69), ("gnd_flat", 5.2, 19.7),
      ("crop_micro_sd", 4.89, 5.40)]),
    ("scene13/260811_w3_s13frost_c", "pt_noon_entry_approach.png",
     [("micro_sd", 1.23, 2.55), ("flat", 44.2, 41.4), ("gnd_flat", 35.3, 39.0),
      ("crop_micro_sd", 0.91, 1.35), ("crop_flat", 52.0, 45.5)]),
    ("scene11/260811_w3_s11clean", "pt_noon_stair_head.png",
     [("micro_sd", 4.25, 8.09), ("gnd_flat", 6.5, 17.8),
      ("crop_flat", 6.2, 15.8)]),
]


def selftest(root):
    print("=" * 72)
    print("자기검증 — 조사 §3 게재값 재현 (원본 해상도 · 크롭 창 §3.2)")
    print("=" * 72)
    npass = nfail = nskip = 0
    print("\n── A군: 재현 성립(어서션) ───────────────────────────────────")
    for rel, png, checks in _ST_REPRO:
        p = os.path.join(root, "look_check", rel, png)
        if not os.path.isfile(p):
            print(f"[skip] {rel}/{png} 없음")
            nskip += len(checks)
            continue
        m = measure(p)
        print(f"\n{rel}/{png}")
        for key, want, tol in checks:
            got = m.get(key)
            if got is None:
                print(f"  ? {key:<16s} 측정 없음")
                nskip += 1
                continue
            ok = abs(got - want) <= tol
            npass += ok
            nfail += (not ok)
            print(f"  {'OK ' if ok else '✗  '}{key:<16s} 계측 {got:9.3f} "
                  f"vs 게재 {want:9.3f}  (허용 ±{tol})")
    print("\n── B군: 재현 불성립 — 계측기 baseline 감시(보고) ─────────────")
    for rel, png, checks in _ST_BASELINE:
        p = os.path.join(root, "look_check", rel, png)
        if not os.path.isfile(p):
            print(f"[skip] {rel}/{png} 없음")
            continue
        m = measure(p)
        print(f"\n{rel}/{png}")
        for key, base, pub in checks:
            got = m.get(key)
            if got is None:
                continue
            drift = abs(got - base) > max(0.05, 0.02 * abs(base))
            npass += (not drift)
            nfail += drift
            print(f"  {'OK ' if not drift else '✗  '}{key:<16s} 계측 {got:9.3f} "
                  f"vs 본기 baseline {base:8.3f}  (조사 게재 {pub:7.2f} — 재현 불가)")
    print(f"\n[자기검증] 일치 {npass} · 불일치 {nfail} · 건너뜀 {nskip}")
    if nfail == 0:
        print("[자기검증] A군 통과 = 색공간·밴드·크롭 창·문턱 정의 정합 확인. "
              "B군 통과 = 계측기 드리프트 0.")
    return 0 if nfail == 0 else 1


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="조사 §1.2 품질 지표 계측 (numpy+PIL, GPU 0)")
    ap.add_argument("--png", nargs="*", default=[],
                    help="PNG 경로. 글롭 패턴 가능")
    ap.add_argument("--crop", default="",
                    help="x0,y0,x1,y1 (기본 = §3.2 창 300,620,1620,1060). "
                         "'full'/'none' 이면 크롭 끔")
    ap.add_argument("--long-side", type=int, default=0,
                    help="긴 변 다운샘플 [px]. 0 = 원본(기본). "
                         "imgstats.py 와 교차 검증할 때만 1024 를 쓸 것")
    ap.add_argument("--gate", action="store_true",
                    help="파일럿 A 합격선 판정을 함께 출력")
    ap.add_argument("--selftest", action="store_true",
                    help="조사 §3 게재값 재현 검증만 하고 종료")
    a = ap.parse_args(argv)

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if a.selftest:
        return selftest(root)

    crop = CROP_NEAR_GROUND
    if a.crop.lower() in ("full", "none", "off"):
        crop = None
    elif a.crop:
        try:
            crop = tuple(int(v) for v in a.crop.split(","))
            assert len(crop) == 4
        except Exception:
            print("[오류] --crop 은 x0,y0,x1,y1 형식이어야 한다")
            return 2

    paths = []
    for pat in a.png:
        hits = sorted(glob.glob(pat)) if any(c in pat for c in "*?[") else [pat]
        paths.extend(hits)
    paths = [p for p in paths if os.path.isfile(p)]
    if not paths:
        print("[오류] 대상 PNG 가 없다 — --png 또는 --selftest 를 쓸 것")
        return 2

    rows = [measure(p, crop, a.long_side) for p in paths]
    table(rows, crop)
    if a.gate:
        return 1 if gate(rows) else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
