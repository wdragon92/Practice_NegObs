#!/usr/bin/env python3
"""렌더 vs 실사 자연영상 통계 진단 — 사실화 라운드 공식 측정 도구.

출처: `Docs/surveys/realism_gap_2026-07-28/00_supervisor_direct_diagnosis.md`
      (감독 직접측정) + `E_realism_measurement_protocol.md` (L1 저수준 통계).
종전 `scratchpad/imgstats.py`(미추적)를 저장소에 정식 편입하면서
JSON 출력·하늘 제외 모드·그룹 비교를 추가했다. 의존성은 numpy+PIL 뿐.

측정 항목 (전부 자연영상 통계 문헌의 표준 지표):
  slope    : 방사평균 파워스펙트럼 기울기 (log P vs log f). 자연영상 ≈ -2.0 ± 0.3
  grad_k   : 그래디언트 크기 분포의 첨도. 자연영상은 heavy-tail (>> 3)
  flat%    : 국소표준편차 < 1/255 인 픽셀 비율 (= 디테일이 전혀 없는 "죽은" 영역)
  hf       : 고주파(>= f_nyq/4) 에너지 비율
  sat_mu   : 평균 채도(HSV S 근사), sat_sd: 채도 표준편차
  chroma_sd: 국소 색상 변동 — 실사는 같은 재질 안에서도 색이 흔들림
  ori_axis : 에지 방향이 정확히 0/90도 축에 몰린 비율 (CG 티). 균등 기대치 0.111

T1 목표치 [ZZ_synthesis §6]: flat% < 8 · slope -2.0~-2.2 · sat_mu 0.15~0.22

사용법:
  python scripts/imgstats.py @render 'look_check/scene01/v7_pt/pt_*.png' \
                            @real   'Docs/reference_photos/*.jpg'
  # 하늘(상단 1/3) 제외 — 지면·구조물만 보고 싶을 때
  python scripts/imgstats.py --lower @render '...'
  # 기계 판독용
  python scripts/imgstats.py --json out.json @render '...'
"""
import sys
import os
import glob
import json

import numpy as np
from PIL import Image

METRICS = ("slope", "grad_k", "flat_pct", "flat_sky", "flat_gnd", "hf", "sat_mu", "sat_sd",
           "chroma_sd", "ori_axis")

# T1 게이트 [ZZ_synthesis §6 T1 "목표 수치"]
GATE = dict(flat_pct=(None, 8.0), slope=(-2.2, -2.0), sat_mu=(0.15, 0.22))
# 하단 2/3(지면·구조물) 보조 게이트 — 실사 실측 0.1%. 하늘 교체만으로 헤드라인
# 지표를 통과하는 것을 막는 진짜 기준선이다. [P1 감독 실측 2026-07-28]
GATE_GND = dict(flat_gnd=(None, 3.0))


def load(path, long_side=1024, lower=False):
    """긴 변 1024로 정규화해 로드. lower=True면 상단 1/3(하늘) 제외."""
    im = Image.open(path).convert("RGB")
    w, h = im.size
    s = long_side / max(w, h)
    if s < 1:
        im = im.resize((int(w * s), int(h * s)), Image.LANCZOS)
    a = np.asarray(im).astype(np.float64) / 255.0
    if lower:
        a = a[a.shape[0] // 3:, :, :]
    return a


def lum(rgb):
    return 0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]


def ps_slope(g):
    """정사각 중앙 크롭 + 해닝 창 → 방사평균 파워스펙트럼 기울기."""
    n = min(g.shape)
    y0 = (g.shape[0] - n) // 2
    x0 = (g.shape[1] - n) // 2
    c = g[y0:y0 + n, x0:x0 + n]
    win = np.outer(np.hanning(n), np.hanning(n))
    F = np.fft.fftshift(np.fft.fft2((c - c.mean()) * win))
    P = np.abs(F) ** 2
    cy = cx = n // 2
    yy, xx = np.mgrid[0:n, 0:n]
    r = np.sqrt((yy - cy) ** 2 + (xx - cx) ** 2).astype(int)
    tot = np.bincount(r.ravel(), P.ravel())
    cnt = np.bincount(r.ravel())
    prof = tot / np.maximum(cnt, 1)
    lo, hi = 3, n // 4                     # DC 근방·나이퀴스트 근방 제외
    f = np.arange(lo, hi)
    y = np.log(np.maximum(prof[lo:hi], 1e-20))
    A = np.vstack([np.log(f), np.ones_like(f, dtype=float)]).T
    slope, _ = np.linalg.lstsq(A, y, rcond=None)[0]
    return float(slope), prof, n


def grads(g):
    gx = np.diff(g, axis=1)[:-1, :]
    gy = np.diff(g, axis=0)[:, :-1]
    return gx, gy


def kurt(x):
    x = x - x.mean()
    s = x.std()
    return float((x ** 4).mean() / (s ** 4 + 1e-20))


def local_std(g, k=5):
    """박스필터(적분영상) 기반 국소 표준편차."""
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


def hf_ratio(prof, n):
    lo = n // 8
    tot = prof[1:n // 2].sum()
    hi = prof[lo:n // 2].sum()
    return float(hi / max(tot, 1e-20))


def sat_stats(rgb):
    mx = rgb.max(-1)
    mn = rgb.min(-1)
    s = np.where(mx > 1e-6, (mx - mn) / np.maximum(mx, 1e-6), 0)
    return float(s.mean()), float(s.std())


def chroma_local_sd(rgb):
    """대략적 색차 채널(opponent) 의 국소 변동."""
    rg = rgb[..., 0] - rgb[..., 1]
    by = 0.5 * (rgb[..., 0] + rgb[..., 1]) - rgb[..., 2]
    return float((local_std(rg, 7).mean() + local_std(by, 7).mean()) / 2)


def ori_axis_frac(g):
    """상위 10% 에지 중 0/90도 ±5도에 몰린 비율. 균등분포 기대치 = 0.111."""
    gx, gy = grads(g)
    mag = np.sqrt(gx ** 2 + gy ** 2)
    m = mag > np.percentile(mag, 90)
    if m.sum() < 100:
        return float("nan")
    ang = np.degrees(np.arctan2(gy[m], gx[m])) % 180.0
    near = ((ang < 5) | (ang > 175) | (np.abs(ang - 90) < 5))
    return float(near.mean())


def analyze(path, lower=False):
    rgb = load(path, lower=lower)
    g = lum(rgb)
    slope, prof, n = ps_slope(g)
    gx, gy = grads(g)
    mag = np.sqrt(gx ** 2 + gy ** 2)
    ls = local_std(g, 5)
    smu, ssd = sat_stats(rgb)
    # [P1 발견] 죽은 픽셀의 67~74% 가 하늘이었다 (감독 실측, 2026-07-28).
    # 전체 flat% 만 보면 하늘 교체만으로 목표를 "달성"할 수 있어 지표를 속이게
    # 된다. 상단 1/3(대략 하늘)·하단 2/3(지면·구조물)을 항상 분리 보고한다.
    # 실사 기준: 상단 11.6% / **하단 0.1%** — 하단이 진짜 기준이다.
    h = g.shape[0]
    return dict(
        name=os.path.basename(path),
        path=path,
        slope=slope,
        grad_k=kurt(mag.ravel()),
        flat_pct=100.0 * float((ls < 1.0 / 255).mean()),
        flat_sky=100.0 * float((ls[:h // 3] < 1.0 / 255).mean()),
        flat_gnd=100.0 * float((ls[h // 3:] < 1.0 / 255).mean()),
        hf=hf_ratio(prof, n),
        sat_mu=smu, sat_sd=ssd,
        chroma_sd=chroma_local_sd(rgb),
        ori_axis=ori_axis_frac(g),
    )


def gate_verdict(agg):
    """T1 게이트 판정. 반환: (통과여부, 항목별 문자열)."""
    out, ok_all = [], True
    for k, (lo, hi) in list(GATE.items()) + list(GATE_GND.items()):
        v = agg.get(k)
        if v is None:
            continue
        ok = (lo is None or v >= lo) and (hi is None or v <= hi)
        ok_all = ok_all and ok
        rng = (f"< {hi}" if lo is None else f"{lo} ~ {hi}")
        out.append(f"{k}={v:.3f} (목표 {rng}) {'통과' if ok else '미달'}")
    return ok_all, out


HDR = (f"{'group':<10} {'image':<34} {'slope':>7} {'grad_k':>7} {'flat%':>7} "
       f"{'sky%':>6} {'gnd%':>6} {'hf':>6} {'sat_mu':>7} {'chr_sd':>7} {'ori':>6}")


def _row(gname, r):
    return (f"{gname:<10} {r['name'][:34]:<34} {r['slope']:>7.2f} "
            f"{r['grad_k']:>7.1f} {r['flat_pct']:>7.1f} {r['flat_sky']:>6.1f} "
            f"{r['flat_gnd']:>6.1f} {r['hf']:>6.3f} {r['sat_mu']:>7.3f} "
            f"{r['chroma_sd']:>7.4f} {r['ori_axis']:>6.3f}")


def main(argv):
    lower = "--lower" in argv
    argv = [a for a in argv if a != "--lower"]
    json_out = None
    if "--json" in argv:
        i = argv.index("--json")
        json_out = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]

    groups, cur = {}, None
    for a in argv:
        if a.startswith("@"):
            cur = a[1:]
            groups.setdefault(cur, [])
        else:
            if cur is None:
                print("[에러] 첫 인자는 @그룹이름 이어야 합니다.")
                return 1
            groups[cur].extend(sorted(glob.glob(a)))

    print(f"# 모드: {'하단 2/3(하늘 제외)' if lower else '전체 프레임'}")
    print(HDR)
    print("-" * len(HDR))
    agg, detail = {}, {}
    for gname, paths in groups.items():
        rows = []
        for p in paths:
            try:
                r = analyze(p, lower=lower)
            except Exception as e:
                print(f"  [skip] {p}: {e}")
                continue
            rows.append(r)
            print(_row(gname, r))
        if rows:
            agg[gname] = {k: float(np.mean([r[k] for r in rows]))
                          for k in METRICS}
            agg[gname]["n"] = len(rows)
            detail[gname] = rows

    print("\n" + "=" * len(HDR))
    print("그룹 평균")
    print(HDR.replace("image", "n    "))
    for gname, a in agg.items():
        cnt = f"({a['n']} imgs)"
        print(f"{gname:<10} {cnt:<34} {a['slope']:>7.2f} {a['grad_k']:>7.1f} "
              f"{a['flat_pct']:>7.1f} {a['flat_sky']:>6.1f} {a['flat_gnd']:>6.1f} "
              f"{a['hf']:>6.3f} {a['sat_mu']:>7.3f} {a['chroma_sd']:>7.4f} "
              f"{a['ori_axis']:>6.3f}")

    print("\nT1 게이트 판정 [ZZ_synthesis §6]")
    for gname, a in agg.items():
        ok, lines = gate_verdict(a)
        print(f"  [{gname}] {'통과' if ok else '미달'} — " + " / ".join(lines))

    if json_out:
        with open(json_out, "w") as f:
            json.dump(dict(mode="lower" if lower else "full",
                           groups=agg, images=detail), f,
                      indent=2, ensure_ascii=False)
        print(f"\n[JSON] {json_out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
