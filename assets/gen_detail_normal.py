#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""디테일 그레인 노멀맵 절차 생성 — T1 재질층 §3.3 (W2-A5)

`t1_material_layer_spec_v1.md` v1.1 §3.3 이 "1순위 = 절차 생성" 으로 확정한 산출물.
저장소 보유분(`plaster_nor_dx` = mineral · `asphalt_nor_dx` = granular)은 §3.2 에서
이미 합격했으므로 **폴백**이고, 본 스크립트는 **제3계열(brushed) + 세 계열 공통 1순위**를
만든다. brushed 는 보유분 전멸(§3.2)이라 절차 외 대안이 없다.

핵심 규약 3건 (v1 과 다르다 — 반드시 지킬 것):
  1. **β 는 파워 지수**다.  power(height) ∝ f^(−β)   [v1.1 R2 · §3.3]
     v1 의 진폭 규약(amplitude ∝ f^−β)이 아니다. 두 규약은 2배 차이가 난다.
     노멀 = 높이장의 그래디언트 ⇒ 노멀 접선 파워 ∝ f^(2−β) ⇒ `slope_n ≈ 2 − β`.
  2. **나이퀴스트 컷** R > 0.45 (정규화 반경 주파수, 단위 cycles/px, 나이퀴스트 0.5).
     현행 변위 스킨이 M4 로 겪은 앨리어싱의 재발 차단.
  3. **자가검증 후에만 파일을 쓴다.** §3.1 게이트 불통과 시 exit 1 · 파일 0개.

측정 정의(`macro%`/`hf%`/`slope_n`/RMS)는 §3.4(a) 가 유일 원천이다. 본 스크립트는
`scripts/norm_spec.py` 가 있으면 그것을 쓰고, 없으면 §3.4(a) 공식을 그대로 인라인
구현한다(어느 쪽을 썼는지 stdout 에 각인한다). 인라인 구현의 정합성은 §3.4 의
**앵커 4맵**을 재측정해 소수점 1자리까지 일치하는지로 증명한다(`--verify-anchors`).

사용:
    python3 assets/gen_detail_normal.py                 # 생성 + 자가검증
    python3 assets/gen_detail_normal.py --verify-anchors # 측정기 앵커 재현만
    python3 assets/gen_detail_normal.py --dry-run       # 측정만, 파일 미저작
    python3 assets/gen_detail_normal.py --json out.json

GPU 0 · numpy + PIL 만 · 부작용은 `assets/detail_grain_*_nor.png` 3개뿐.
"""

import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)

# ---------------------------------------------------------------------------
# §3.1 합격 기준 (v1.1 재캘리브레이션)
# ---------------------------------------------------------------------------
# macro% 는 두 값을 함께 본다: 스펙 §3.1 문턱(10)이 정본이고, W2-A5 임무서가 준
# 완화 문턱(15)은 참고용이다. 게이트는 **엄격한 쪽(10)** 으로 건다 — 절차 생성은
# 예측 macro% 가 1 %대라 여유가 크므로 완화할 이유가 없다.
GATE = dict(
    macro_max=10.0,        # §3.1 — 모듈형 타일 맵 배제 필터
    macro_max_relaxed=15.0,  # 임무서 완화값(참고 열)
    slope_min=-0.9,        # §3.1 하한 — 0 에 가까울수록 백색잡음
    slope_max=+0.3,        # §3.1 [v1.1 신설] 상한 — 텍셀 해시 배제
    rms_min=0.12,
    rms_max=0.35,
    hf_min=10.0,           # 보조(교차 확인용). 판정에는 쓰지 않는다
)

# §3.4 검증 앵커 — 인라인 측정기가 반드시 재현해야 하는 값 (소수점 1자리)
ANCHORS = {
    "assets/scene01/concrete_wall_nor_dx.jpg": (-0.71, 4.1, 18.9, 0.056),
    "assets/scene01/asphalt_nor_dx.jpg":       (-0.66, 3.2, 13.3, 0.294),
    "assets/scene01/stone_flag_nor_dx.jpg":    (-2.46, 58.4, 2.5, 0.192),
    "assets/paving_interlock_nor.jpg":         (-1.98, 52.3, 4.8, 0.449),
}

# ---------------------------------------------------------------------------
# 생성 레시피 (§3.3 표)
# ---------------------------------------------------------------------------
# aniso = (ax, ay) — 진폭 성형에 쓰는 축별 주파수 스케일. 1.0/1.0 = 등방.
#   brushed 는 u 축 ×0.25 이방 필터: fx 를 0.25 로 나눠(=×4) 쓰면 x 방향 고주파가
#   더 빨리 감쇠 ⇒ **결이 u(=x) 축을 따라 길게 늘어난다**(브러시드 금속 스크래치).
RECIPES = [
    dict(name="mineral",  beta=2.0, rms=0.18, seed=7,
         aniso=(1.0, 1.0),
         note="포장·콘크리트·석재·연석·노징. plaster_nor_dx(RMS 0.159) 근방·등방"),
    dict(name="granular", beta=1.8, rms=0.28, seed=17,
         aniso=(1.0, 1.0),
         note="흙·자갈·아스팔트·눈. asphalt_nor_dx(RMS 0.294) 근방·등방"),
    dict(name="brushed",  beta=2.0, rms=0.14, seed=29,
         aniso=(0.25, 1.0),
         note="금속(이방 스크래치). 보유분 전멸이라 절차 외 대안 없음(§3.2)"),
]

N_DEFAULT = 1024
NYQ_CUT = 0.45


# ===========================================================================
# 측정기 — §3.4(a) 인라인 구현 (scripts/norm_spec.py 부재 시 폴백)
# ===========================================================================
def _crop_center(a, n):
    """네이티브 해상도에서 중앙 정사각 n 크롭. **리샘플 금지**."""
    h, w = a.shape[:2]
    y0 = (h - n) // 2
    x0 = (w - n) // 2
    return a[y0:y0 + n, x0:x0 + n]


def measure_tangent(nx, ny):
    """§3.4(a) 4)~8) — 접선 성분 2장에서 지표 4종을 낸다.

    nx, ny 는 **크롭이 끝난 정사각 float 배열**(값역 −1..1)이어야 한다.
    """
    n = nx.shape[0]
    # 4) 분리형 Hann 창 + **창 가중 평균 선차감**(재현 실패의 주 분기점)
    w1 = np.hanning(n)
    W = np.outer(w1, w1)
    sW = W.sum()

    def _prep(x):
        mu = float((W * x).sum() / sW)
        return (x - mu) * W

    # 5) FFT — 두 접선 성분 파워 합
    Fx = np.fft.fftshift(np.fft.fft2(_prep(nx)))
    Fy = np.fft.fftshift(np.fft.fft2(_prep(ny)))
    P = (np.abs(Fx) ** 2 + np.abs(Fy) ** 2)

    # 6) 방사 링 — fftshift 후 DC 는 인덱스 n//2
    iy, ix = np.indices((n, n))
    r = np.rint(np.hypot(iy - n // 2, ix - n // 2)).astype(np.int64)
    rmax = int(r.max())
    cnt = np.bincount(r.ravel(), minlength=rmax + 1).astype(np.float64)
    sm = np.bincount(r.ravel(), weights=P.ravel(), minlength=rmax + 1)
    prof = np.divide(sm, np.maximum(cnt, 1.0))

    r_nyq = n // 2
    # 7) 정규화 — **링 총합 가중**, DC(r=0) 제외
    T = float(sm[1:r_nyq + 1].sum())

    # 8) 지표
    r_macro = max(n // 32, 2)                       # N=1024 → r ∈ [1, 31]
    macro = 100.0 * float(sm[1:r_macro].sum()) / T
    hf = 100.0 * float(sm[n // 4:r_nyq + 1].sum()) / T

    rr = np.arange(3, n // 4)
    pp = prof[3:n // 4]
    ok = pp > 0
    slope = float(np.polyfit(np.log10(rr[ok]), np.log10(pp[ok]), 1)[0])

    rms = float(np.sqrt(np.mean(nx ** 2 + ny ** 2)))
    return dict(n=n, slope_n=slope, macro=macro, hf=hf, rms=rms)


def measure_file(path, n=N_DEFAULT):
    """§3.4(a) 1)~3) — 파일 로드 → 접선 성분 → 중앙 크롭 → measure_tangent."""
    im = Image.open(path).convert("RGB")
    a = np.asarray(im, dtype=np.float32) / 255.0     # **sRGB 역감마 금지**
    nn = min(n, a.shape[0], a.shape[1])
    a = _crop_center(a, nn)
    nx = 2.0 * a[:, :, 0] - 1.0
    ny = 2.0 * a[:, :, 1] - 1.0                      # B/nz 는 쓰지 않는다
    out = measure_tangent(nx, ny)
    out["path"] = path
    return out


def load_measurer():
    """`scripts/norm_spec.py` 가 있으면 그것을 정본 측정기로 쓴다(임무서 규약).

    병행 에이전트가 저작 중이라 API 가 확정돼 있지 않다 — 아래 후보 이름을 순서대로
    찾고, 어느 것도 없으면 인라인(§3.4(a) 직접 구현)으로 폴백한다.
    반환: (measure_file 함수, 출처 문자열)
    """
    cand = os.path.join(REPO, "scripts", "norm_spec.py")
    if not os.path.exists(cand):
        return measure_file, "inline(§3.4a 직접 구현) — scripts/norm_spec.py 부재"
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("norm_spec", cand)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    except Exception as e:                            # 임포트 실패는 치명 아님
        return measure_file, "inline — scripts/norm_spec.py 임포트 실패(%s)" % e
    # `spectrum` 이 병행 에이전트가 실제로 낸 진입점(2026-07-29 확인). 나머지는
    # API 확정 전에 대비해 둔 후보군 — 먼저 찾히는 것을 쓴다.
    for fn in ("spectrum", "measure_file", "measure", "analyze", "norm_spec"):
        f = getattr(mod, fn, None)
        if callable(f):
            def _wrap(path, n=N_DEFAULT, _f=f):
                d = _f(path)
                if not isinstance(d, dict):
                    raise TypeError("norm_spec.%s 반환형이 dict 가 아니다" % fn)
                # 키 이름 정규화 (slope/slope_n · macro/macro_pct 등 허용)
                g = lambda *ks: next(d[k] for k in ks if k in d)
                return dict(n=d.get("n", n), slope_n=g("slope_n", "slope"),
                            macro=g("macro", "macro_pct", "macro%"),
                            hf=g("hf", "hf_pct", "hf%"),
                            rms=g("rms", "tangent_rms", "RMS"), path=path)
            return _wrap, "scripts/norm_spec.%s (외부 정본)" % fn
    return measure_file, "inline — scripts/norm_spec.py 에 사용 가능한 진입점 없음"


# ===========================================================================
# 생성기 — §3.3 대역제한 백색잡음 → 높이장 → 노멀
# ===========================================================================
def synth_normal(n, beta, rms_target, seed, aniso=(1.0, 1.0), nyq_cut=NYQ_CUT):
    """파워 규약 β 로 높이장을 만들고 **스펙트럼 미분**으로 노멀 접선을 낸다.

    스펙트럼 미분(주파수 영역에서 i·2πf 곱)을 쓰는 이유:
      · 유한차분은 자체가 저역통과 필터라 β 와 실측 slope_n 의 관계를 흐린다.
      · 주기 경계가 정확히 보존된다 ⇒ **완전 타일러블**(§3.3 요건).
    """
    rng = np.random.default_rng(seed)
    Fw = np.fft.fft2(rng.standard_normal((n, n)))     # 백색잡음의 스펙트럼

    f1 = np.fft.fftfreq(n)                            # cycles/px, [−0.5, 0.5)
    FY = f1[:, None]
    FX = f1[None, :]
    f_iso = np.hypot(FX, FY)
    # 진폭 성형용 이방 반경 — brushed 는 ax=0.25 로 x 고주파를 더 깎는다
    f_sh = np.hypot(FX / aniso[0], FY / aniso[1])

    amp = np.zeros((n, n))
    nz = f_sh > 0
    amp[nz] = f_sh[nz] ** (-0.5 * beta)               # power ∝ f^−β ⇒ |H| ∝ f^(−β/2)
    amp[f_iso > nyq_cut] = 0.0                        # 나이퀴스트 근방 컷(등방 판정)
    amp[0, 0] = 0.0                                   # DC 제거

    H = Fw * amp
    # 노멀 접선 = ∂h/∂x, ∂h/∂y (부호는 규약 문제 — 통계적으로 대칭이라 무관)
    gx = np.real(np.fft.ifft2(H * (2j * np.pi * FX)))
    gy = np.real(np.fft.ifft2(H * (2j * np.pi * FY)))

    # RMS 를 진폭으로 **직접 지정**(§3.3 "제어 가능성 실증")
    cur = float(np.sqrt(np.mean(gx ** 2 + gy ** 2)))
    k = rms_target / max(cur, 1e-12)
    return gx * k, gy * k


def encode_normal(nx, ny):
    """접선 2성분 → 8bit RGB 노멀맵. 단위구 이탈 텍셀만 길이 0.999 로 되돌린다."""
    m = np.hypot(nx, ny)
    over = m > 0.999
    n_over = int(over.sum())
    if n_over:
        s = np.where(over, 0.999 / np.maximum(m, 1e-12), 1.0)
        nx = nx * s
        ny = ny * s
    nzc = np.sqrt(np.clip(1.0 - nx ** 2 - ny ** 2, 0.0, 1.0))
    rgb = np.stack([nx, ny, nzc], axis=-1) * 0.5 + 0.5
    return np.clip(np.rint(rgb * 255.0), 0, 255).astype(np.uint8), n_over


def aniso_ratio(nx, ny):
    """이방성 실증 지표 — 방사평균(§3.4)은 방향을 지워버리므로 별도로 잰다.

    fx 축 ±30° 쐐기 파워 / fy 축 ±30° 쐐기 파워 (r ∈ [3, N/4)).
    등방이면 ≈ 1.0. brushed(u 축 이방)는 fx 성분이 억제되므로 **< 1** 이어야 하고,
    그것이 곧 "결이 u 축을 따라 길게 늘어났다"는 뜻이다.
    """
    n = nx.shape[0]
    w1 = np.hanning(n)
    W = np.outer(w1, w1)
    sW = W.sum()
    P = 0.0
    for x in (nx, ny):
        F = np.fft.fftshift(np.fft.fft2((x - float((W * x).sum() / sW)) * W))
        P = P + np.abs(F) ** 2
    iy, ix = np.indices((n, n))
    dy = iy - n // 2
    dx = ix - n // 2
    r = np.hypot(dy, dx)
    band = (r >= 3) & (r < n // 4)
    ang = np.abs(np.degrees(np.arctan2(np.abs(dy), np.abs(dx))))
    wx = band & (ang < 30.0)          # fx 축 근방 = x 방향 변화
    wy = band & (ang > 60.0)          # fy 축 근방 = y 방향 변화
    return float(P[wx].mean() / max(P[wy].mean(), 1e-30))


def seam_ratio(nx, ny):
    """타일러블 실증 — 이음매 차분 에너지 / 내부 인접 차분 에너지.

    FFT 합성이라 주기 경계가 정확히 보존된다 ⇒ 1.0 근방이어야 한다.
    (1.0 을 크게 넘으면 이음매에 계단이 보인다는 뜻이다.)
    """
    out = []
    for x in (nx, ny):
        seam = np.mean((x[0, :] - x[-1, :]) ** 2) + np.mean((x[:, 0] - x[:, -1]) ** 2)
        inner = np.mean(np.diff(x, axis=0) ** 2) + np.mean(np.diff(x, axis=1) ** 2)
        out.append(seam / max(inner, 1e-30))
    return float(np.mean(out))


def gate(m):
    """§3.1 판정. 반환: (pass, 실패 사유 리스트)"""
    bad = []
    if not (m["macro"] < GATE["macro_max"]):
        bad.append("macro%% %.2f >= %.1f" % (m["macro"], GATE["macro_max"]))
    if not (m["slope_n"] > GATE["slope_min"]):
        bad.append("slope_n %.3f <= %.1f" % (m["slope_n"], GATE["slope_min"]))
    if not (m["slope_n"] <= GATE["slope_max"]):
        bad.append("slope_n %.3f > +%.1f" % (m["slope_n"], GATE["slope_max"]))
    if not (GATE["rms_min"] <= m["rms"] <= GATE["rms_max"]):
        bad.append("RMS %.3f 밖 [%.2f, %.2f]"
                   % (m["rms"], GATE["rms_min"], GATE["rms_max"]))
    return (not bad), bad


# ===========================================================================
def verify_anchors(measure, tol=0.06):
    """§3.4 앵커 4맵 재현 — 측정기 정의가 정본과 같은지의 증명."""
    print("\n[앵커 재현] §3.4 표와 소수점 1자리 일치 여부")
    print("%-46s %8s %8s %8s %8s  %s"
          % ("map", "slope_n", "macro%", "hf%", "RMS", "판정"))
    rows, allok = [], True
    for rel, exp in ANCHORS.items():
        p = os.path.join(REPO, rel)
        if not os.path.exists(p):
            print("%-46s  (파일 없음 — 건너뜀)" % rel)
            continue
        m = measure(p)
        got = (m["slope_n"], m["macro"], m["hf"], m["rms"])
        ok = (abs(got[0] - exp[0]) <= tol and abs(got[1] - exp[1]) <= 0.06
              and abs(got[2] - exp[2]) <= 0.06 and abs(got[3] - exp[3]) <= 0.0006)
        allok &= ok
        print("%-46s %8.2f %8.1f %8.1f %8.3f  %s  (표: %.2f/%.1f/%.1f/%.3f)"
              % (rel, got[0], got[1], got[2], got[3],
                 "OK" if ok else "MISMATCH", exp[0], exp[1], exp[2], exp[3]))
        rows.append(dict(path=rel, got=got, expected=exp, ok=bool(ok)))
    return allok, rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=N_DEFAULT, help="해상도 (기본 1024)")
    ap.add_argument("--out-dir", default=HERE)
    ap.add_argument("--dry-run", action="store_true", help="측정만, 파일 미저작")
    ap.add_argument("--verify-anchors", action="store_true",
                    help="§3.4 앵커 재현만 하고 종료")
    ap.add_argument("--json", default=None)
    a = ap.parse_args()

    measure, src = load_measurer()
    print("측정기 = %s" % src)
    print("게이트  = macro%% < %.1f (임무서 완화 %.1f) · %.1f < slope_n <= +%.1f · "
          "RMS %.2f~%.2f · hf%% >= %.1f(보조)"
          % (GATE["macro_max"], GATE["macro_max_relaxed"], GATE["slope_min"],
             GATE["slope_max"], GATE["rms_min"], GATE["rms_max"], GATE["hf_min"]))

    anchor_ok, anchor_rows = verify_anchors(measure)
    if a.verify_anchors:
        return 0 if anchor_ok else 1
    if not anchor_ok:
        # 앵커가 안 맞으면 이후 판정 수치의 의미가 없다 — 생성 자체를 막는다.
        print("\n[FAIL] 앵커 재현 실패 — 측정 정의가 §3.4 와 다르다. 생성 중단.")
        return 1

    print("\n[생성] N=%d · nyq_cut=%.2f · seed 고정 · 스펙트럼 미분" % (a.n, NYQ_CUT))
    print("%-10s %5s %6s %8s %8s %8s %8s %6s %7s %6s  %s"
          % ("family", "beta", "rmsTgt", "slope_n", "macro%", "hf%", "RMS",
             "clip", "aniso", "seam", "판정"))

    results, blobs, failed = [], [], []
    for rc in RECIPES:
        nx, ny = synth_normal(a.n, rc["beta"], rc["rms"], rc["seed"],
                              aniso=rc["aniso"])
        rgb, n_over = encode_normal(nx, ny)
        # **인코딩된 8bit 결과**를 측정한다 — 렌더러가 실제로 읽는 값이 정본.
        dec = rgb.astype(np.float32) / 255.0
        dnx = 2.0 * dec[:, :, 0] - 1.0
        dny = 2.0 * dec[:, :, 1] - 1.0
        m = measure_tangent(dnx, dny)
        m["aniso"] = aniso_ratio(dnx, dny)
        m["seam"] = seam_ratio(dnx, dny)
        ok, why = gate(m)
        if not ok:
            failed.append((rc["name"], why))
        print("%-10s %5.1f %6.2f %8.3f %8.2f %8.1f %8.3f %6d %7.3f %6.2f  %s%s"
              % (rc["name"], rc["beta"], rc["rms"], m["slope_n"], m["macro"],
                 m["hf"], m["rms"], n_over, m["aniso"], m["seam"],
                 "PASS" if ok else "FAIL",
                 "" if ok else " (" + "; ".join(why) + ")"))
        results.append(dict(family=rc["name"], beta=rc["beta"],
                            rms_target=rc["rms"], seed=rc["seed"],
                            aniso_filter=list(rc["aniso"]), clipped_texels=n_over,
                            note=rc["note"], **{k: m[k] for k in
                            ("n", "slope_n", "macro", "hf", "rms", "aniso",
                             "seam")},
                            passed=bool(ok), fail_reason=why))
        blobs.append((rc["name"], rgb))

    if failed:
        print("\n[FAIL] %d 계열 불통과 — **파일을 남기지 않는다**(§3.3 규약)." % len(failed))
        return 1

    if a.dry_run:
        print("\n[dry-run] 전 계열 PASS — 파일 미저작.")
    else:
        for name, rgb in blobs:
            p = os.path.join(a.out_dir, "detail_grain_%s_nor.png" % name)
            Image.fromarray(rgb, mode="RGB").save(p, optimize=True)
            print("저작: %s (%d bytes)" % (p, os.path.getsize(p)))

    if a.json:
        with open(a.json, "w") as f:
            json.dump(dict(measurer=src, gate=GATE, anchors=anchor_rows,
                           maps=results), f, indent=1, ensure_ascii=False)
        print("json: %s" % a.json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
