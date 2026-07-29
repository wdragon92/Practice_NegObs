#!/usr/bin/env python3
"""Natural-image statistics diagnostic, render vs photo — the official
measurement tool for the realism rounds.

Sources: `Docs/surveys/realism_gap_2026-07-28/00_supervisor_direct_diagnosis.md`
      (supervisor's own measurements) + `E_realism_measurement_protocol.md`
      (L1 low-level statistics).
The former `scratchpad/imgstats.py` (untracked) was formally moved into the
repository, gaining JSON output, a sky-excluded mode and group comparison.
Dependencies are numpy + PIL only.

Metrics (all standard indicators from the natural-image statistics literature):
  slope    : radially averaged power-spectrum slope (log P vs log f).
             Natural images ~ -2.0 +- 0.3
  grad_k   : kurtosis of the gradient-magnitude distribution. Natural images
             are heavy-tailed (>> 3)
  flat%    : share of pixels with local stddev < 1/255 (= "dead" regions with
             no detail at all)
  hf       : high-frequency (>= f_nyq/4) energy ratio
  sat_mu   : mean saturation (approximating HSV S), sat_sd: its stddev
  chroma_sd: local colour variation — in photos the colour wavers even within
             one material
  ori_axis : share of edge orientations sitting exactly on the 0/90-degree axes
             (a CG tell). Uniform expectation is 0.111

T1 targets [ZZ_synthesis §6]: flat% < 8, slope -2.0~-2.2, sat_mu 0.15~0.22

Usage:
  # The photo reference group uses the **distribution-safe set** (licensing
  # audit remedy).
  #   REAL=$(sed '/^#/d;/^$/d' Docs/reference_photos/real_set_safe.txt | tr '\n' ' ')
  python scripts/imgstats.py @render 'look_check/scene01/v7_pt/pt_*.png' @real $REAL
  #
  # WARNING: do not use the former `@real 'Docs/reference_photos/*.jpg'` (n=2) —
  #   one of those two was a third-party photo with no licensing basis and has
  #   been quarantined, and the single remaining image is not a valid sample.
  # Exclude the sky (top 1/3) — when only ground and structures matter
  python scripts/imgstats.py --lower @render '...'
  # Machine-readable output
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

# T1 gate [ZZ_synthesis §6 T1 "target figures"] — supervisor-approved
# criterion. **Do not change.**
GATE = dict(flat_pct=(None, 8.0), slope=(-2.2, -2.0), sat_mu=(0.15, 0.22))

# ---------------------------------------------------------------------------
# [Recomputed from the photo distribution] `Docs/reports/real_reference_expansion.md` (n=54)
#
# The original targets were derived from **two photographs**. Re-measuring with
# the sample expanded to 54 shows that **the photos themselves fail 3 of the 4
# targets**:
#     flat_pct<8       photo pass rate 44%
#     slope -2.2~-2.0  44% (91% if the literature's interval is used)
#     sat_mu 0.15~0.22 33%
#     flat_gnd<3.0     54%  <- the number happens to be sound, but its basis
#                              ("photos measure 0.1") was an outlier
#
# Photos, n=54, measured: slope -2.033+-0.184 / flat_pct 10.23+-8.83 /
#                flat_gnd 3.881+-5.005 (median 1.79) / sat_mu 0.232+-0.071
#
# Discriminative power (AUC separation, 54 photos vs 114 renders):
#     grad_k 0.354 > slope 0.338 > ori_axis 0.168 > chroma_sd 0.138 > sat_mu 0.098
#   -> **sat_mu ranks last of all metrics yet sits in the gate** (renders land
#     mid-distribution for photos). ori_axis was dropped by the supervisor on
#     n=2 evidence, but it discriminates better than sat_mu, so **dropping it
#     was unjustified**. grad_k leads on separation yet is not in the gate.
#
# The values below are **for reference alongside** the gate. Changing the gate
# requires supervisor approval, so GATE is left as-is.
REAL_N54 = dict(slope=(-2.033, 0.184), flat_pct=(10.23, 8.83),
                flat_gnd=(3.881, 5.005), sat_mu=(0.232, 0.071),
                grad_k=(None, None), ori_axis=(0.252, 0.074))
GATE_ALT = dict(flat_gnd=(None, 3.0),      # between median 1.79 and mean 3.88 — can be kept
                slope=(-2.40, -1.75),      # photo mean +-2SD
                grad_k=(None, 20.0))       # substitutes the top-separation metric
# Metrics with large CV (flat_sky 94%, flat_gnd 129%, hf 115%, flat_pct 86%)
# must be judged on the **median, not the mean** (skew +2.38, right-tailed).
# Auxiliary gate for the lower 2/3 (ground and structures) — photos measure
# 0.1%. This is the real baseline that stops a headline metric from passing on
# a sky swap alone. [P1 supervisor measurement 2026-07-28]
GATE_GND = dict(flat_gnd=(None, 3.0))


def load(path, long_side=1024, lower=False):
    """Load, normalizing the long side to 1024. lower=True drops the top 1/3
    (the sky)."""
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
    """Square centre crop + Hanning window -> radially averaged power-spectrum
    slope."""
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
    lo, hi = 3, n // 4                     # exclude the DC and Nyquist neighbourhoods
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
    """Local standard deviation via a box filter (integral image)."""
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
    """Local variation of the approximate opponent (colour-difference) channels."""
    rg = rgb[..., 0] - rgb[..., 1]
    by = 0.5 * (rgb[..., 0] + rgb[..., 1]) - rgb[..., 2]
    return float((local_std(rg, 7).mean() + local_std(by, 7).mean()) / 2)


def ori_axis_frac(g):
    """Share of the top-10% edges falling within +-5 degrees of the 0/90-degree
    axes. Uniform-distribution expectation = 0.111."""
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
    # [P1 finding] 67~74% of dead pixels were sky (supervisor measurement,
    # 2026-07-28). Looking only at overall flat% lets a sky swap alone "meet"
    # the target, which games the metric. Always report the top 1/3 (roughly
    # sky) and the lower 2/3 (ground and structures) separately.
    # Photo reference: top 11.6% / **bottom 0.1%** — the bottom is the real one.
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
    """T1 gate verdict. Returns: (passed, per-metric strings)."""
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
            # For heavily skewed metrics the mean is dragged by outliers ->
            # report the median alongside (basis: photos, n=54)
            agg[gname].update({k + "_med": float(np.median([r[k] for r in rows]))
                               for k in METRICS})
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

    print("\n중앙값 (왜도 큰 지표는 이쪽이 대표값 — 실사 n=54 근거)")
    for gname, a in agg.items():
        print(f"  [{gname}] flat%={a['flat_pct_med']:5.1f} "
              f"gnd%={a['flat_gnd_med']:5.1f} slope={a['slope_med']:+.2f} "
              f"grad_k={a['grad_k_med']:5.1f} sat={a['sat_mu_med']:.3f} "
              f"ori={a['ori_axis_med']:.3f}")

    print("\nT1 게이트 판정 [ZZ_synthesis §6 — 승용 승인 기준, 불변]")
    for gname, a in agg.items():
        ok, lines = gate_verdict(a)
        print(f"  [{gname}] {'통과' if ok else '미달'} — " + " / ".join(lines))

    print("\n[참고] 실사 n=54 분포 기반 재산정 게이트 (승인 전 — 판정에 쓰지 말 것)")
    for gname, a in agg.items():
        out, ok_all = [], True
        for k, (lo, hi) in GATE_ALT.items():
            v = a.get(k + "_med", a.get(k))
            if v is None:
                continue
            ok = (lo is None or v >= lo) and (hi is None or v <= hi)
            ok_all = ok_all and ok
            rng = (f"< {hi}" if lo is None else f"{lo} ~ {hi}")
            out.append(f"{k}={v:.3f}({rng}){'O' if ok else 'X'}")
        print(f"  [{gname}] {'통과' if ok_all else '미달'} — " + " / ".join(out))

    if json_out:
        with open(json_out, "w") as f:
            json.dump(dict(mode="lower" if lower else "full",
                           groups=agg, images=detail), f,
                      indent=2, ensure_ascii=False)
        print(f"\n[JSON] {json_out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
