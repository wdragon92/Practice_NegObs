#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""근경 밴드 지표 측정기 — `t1_material_layer_spec_v1.md` v1.1 §3.4(b) 정본.

`ground_kit_spec_v1.md` §7.1 렌더 후 게이트와 부록 B, D조 조사 3편
(`D_ground_profile_{urban,natural,special}.md`) 이 인용하는 도구다.
v1 측정기는 scratchpad 세션 소멸로 부재했다 `[레드팀 §5·§8-1]` — 이 파일이 재작성본이며,
게이트 값이 **이 코드의 정의**에 걸려 있다.

밴드 (§3.4(b))
    B45 = 하단 45 %  rows[int(0.55·H):]   — sd/mean/p99/>224 %/flat %/edge
    B30 = 하단 30 %  rows[int(0.70·H):]   — wht %/σ_LF (+ D조 edge %/struct %)
휘도
    Y = 0.2126R + 0.7152G + 0.0722B  on **sRGB 표시값 0~255**
    (선형화하지 않는다 — 게이트가 표시값 기준으로 잡혀 있다)

지표와 게이트 (§3.4(b) · D조 §2.2)
    sd      = Y.std()                       B45   ≥ 32 (WARN) · 목표 45   실사 n=10 최솟값
    mean    = Y.mean()                      B45   ≤ 170                   실사 최댓값
    p99     = percentile(Y, 99)             B45   보고만
    >224 %  = 100·mean(Y > 224)             B45   ≤ 5                     실사 p90 근사
    wht %   = 100·mean(Y/255 > 0.80)        B30   < 2                     v5.1 §1 순백 규약
    flat %  = 100·mean(local_std(Y/255,5) < 1/255)  B45   < 8
    σ_LF    = 100·std(box_downsample(Y/255, 64))    B30   ≥ 5.0 (WARN) · 목표 11.0
    edge    = mean(|∇Y|) (Sobel)            B45   보고만
    flat_gnd= 100·mean(local_std(luma,5)[h//3:] < 1/255)  **긴 변 1024 리사이즈**  < 3.0
              (`imgstats.py:203` 정의 그대로 — t1 v1.1 T1 이 선언한 단독 판정 지표)

> **`wht %` 정의 2종 병기(정직 고지).** §3.4(b) 초안은 `wht%` 를 `min(R,G,B)/255 > 0.80`
> 으로 적고 "§2.2 `w80` 과 같은 정의" 라 했는데, D조 §1.4 와 §2.1 표(scene01 98.2 등)는
> **휘도 L > 0.80** 이다. 두 값은 다르다(scene01 v7_pt: L 98.2 vs min 97.1 `[실측]`).
> 본 도구는 **`wht%` = 휘도 기준**(D조 표·본 임무 지시와 일치)으로 두고,
> `w80` = min(R,G,B) 기준을 **하단 2/3**에서 따로 낸다(t1 §2.2 표와 일치). 둘 다 출력한다.

> **W2 규약 — 전부 WARN.** `ground_kit` §7.1 이 "σ_LF·sd 문턱은 실사 n=8·n=10 유도값이라
> W2 에서는 WARN 만, FAIL 로 올리지 않는다" 로 못박았다(imgstats flat%/slope 게이트가
> n=2 로 정해졌다 n=54 에서 뒤집힌 전례). 따라서 `--gate` 는 **종료코드 0**을 유지한다.

> **σ_LF·sd 의 라운드 등급 (`ground_kit_spec_v1.md` §7.5 A1).** 두 지표는 **지면 전용
> 라운드에서는 참고치(informative-only)**, **T1 재질층 반영 후 라운드부터 WARN 게이트**다.
> scene15 파일럿이 근거다 — 요소 47프림을 넣어도 σ_LF 는 0.76 → 0.80 밖에 안 움직였다.
> 보수 패치가 골목 바닥 재질에 바인딩돼 **색이 0** 이기 때문이며, 지면 전용 라운드에서
> 이걸 WARN 으로 걸면 **T1 의 미도착을 ground_kit 의 결함으로 오귀속**하게 된다.
> v1 은 이 등급 구분을 **코드에 담지 않아** 산문에만 있었다. 이제 `--round-class` 가 그
> 선언을 받는다:
>   * `post_t1` (**기본값**) — σ_LF ≥ 5.0 · sd ≥ 32 를 **WARN 으로 발화**한다.
>     T1 재질층이 존재하는 라운드(W2-C `t1_mtl_on` 이후 = 260730_w2d_judge 부터)가 여기다.
>   * `ground_only` — 두 지표를 `[i]` 접두로 **기록만** 하고 위반 목록에서 뺀다.
> 값 자체는 어느 등급에서도 항상 계산·출력·JSON 기록된다(A1 "값은 계속 기록").

의존성 numpy + PIL 뿐. **GPU 0 · 부작용 0.**

사용:
    python3 scripts/near_ground_stats.py 'look_check/scene15/*/pt_noon_preset_h0.3_d*.png'
    python3 scripts/near_ground_stats.py 'look_check/scene14/r2_on/pt_noon_preset_h0.3_d*.png' --median
    python3 scripts/near_ground_stats.py 'look_check/scene15/w2_pilot/*.png' \
        --gate --round-class ground_only        # §7.5 A1 — 지면 전용 라운드
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys

import numpy as np
from PIL import Image

# --- 게이트 (근거는 모듈 도크스트링) ---------------------------------------
G_SD_WARN = 32.0
G_SD_TARGET = 45.0
G_MEAN_MAX = 170.0
G_GT224_MAX = 5.0
G_WHT_MAX = 2.0
G_FLAT_MAX = 8.0
G_SIGLF_WARN = 5.0
G_SIGLF_TARGET = 11.0
G_FLATGND_MAX = 3.0        # imgstats.GATE_GND — 실사 n=54 중앙값 1.79 ~ 평균 3.88 사이

B45_TOP = 0.55             # 하단 45 %
B30_TOP = 0.70             # 하단 30 %
# D_ground_profile_special §1.2 · 부록 B ①이 쓴 밴드 = row 349~1080(1920×1080 전제)
# = h0.3 에서 지면거리 5 m 의 투영 행 아래 전부. 해상도 비의존이 되게 분수로 둔다.
D5M_TOP = 349.0 / 1080.0
LF_BLOCK = 64              # σ_LF 박스 다운샘플 배율
IMGSTATS_LONG = 1024       # flat_gnd 는 imgstats 규약(긴 변 1024)에서 잰다


# ---------------------------------------------------------------------------
def luma(rgb):
    """Y = 0.2126R + 0.7152G + 0.0722B. 입력 스케일을 그대로 따른다."""
    return 0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]


def local_std(g, k=5):
    """박스필터(적분영상) 기반 국소 표준편차 — `imgstats.local_std` 와 동일 구현."""
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
    return np.sqrt(np.maximum(s2 / n - (s1 / n) ** 2, 0.0))


def box_downsample(a, k):
    """k× 박스 평균 다운샘플. **보간 금지 · 패딩 금지** (§3.4(b) σ_LF 규약).

    H,W 가 k 로 안 나눠떨어지면 **우/하단을 잘라낸다** — 패딩은 가장자리에
    가짜 저주파를 만들어 σ_LF 를 오염시킨다.
    """
    h, w = a.shape
    h -= h % k
    w -= w % k
    if h < k or w < k:
        return None
    return a[:h, :w].reshape(h // k, k, w // k, k).mean(axis=(1, 3))


def sobel_mag(g):
    """Sobel 그래디언트 크기. 경계는 edge 반사 패딩."""
    p = np.pad(g, 1, mode="edge")
    kx = np.array([[-1., 0., 1.], [-2., 0., 2.], [-1., 0., 1.]])
    ky = kx.T
    gx = sum(kx[i, j] * p[i:i + g.shape[0], j:j + g.shape[1]]
             for i in range(3) for j in range(3) if kx[i, j])
    gy = sum(ky[i, j] * p[i:i + g.shape[0], j:j + g.shape[1]]
             for i in range(3) for j in range(3) if ky[i, j])
    return np.hypot(gx, gy)


def flat_gnd_of(path):
    """`imgstats.py` 규약(긴 변 1024 LANCZOS 리사이즈)에서 잰 하단 2/3 죽은픽셀 %.

    t1 v1.1 T1 이 선언한 **단독 판정 지표**라 다른 지표와 밴드/해상도가 다르다.
    같은 정의를 그대로 옮겨 놔야 `imgstats` 출력과 숫자가 맞는다.
    """
    im = Image.open(path).convert("RGB")
    w, h = im.size
    s = IMGSTATS_LONG / max(w, h)
    if s < 1:
        im = im.resize((int(w * s), int(h * s)), Image.LANCZOS)
    a = np.asarray(im).astype(np.float64) / 255.0
    g = luma(a)
    H = g.shape[0]
    fg = 100.0 * float((local_std(g, 5)[H // 3:] < 1.0 / 255).mean())
    w80 = 100.0 * float((a[H // 3:].min(axis=-1) > 0.80).mean())
    return fg, w80


def stats(path):
    """PNG 1장 → 지표 dict."""
    rgb255 = np.asarray(Image.open(path).convert("RGB")).astype(np.float64)
    H = rgb255.shape[0]
    b45 = rgb255[int(B45_TOP * H):]
    b30 = rgb255[int(B30_TOP * H):]
    y45 = luma(b45)
    y30 = luma(b30)
    y30n = y30 / 255.0

    lf = box_downsample(y30n, LF_BLOCK)
    sig_lf = 100.0 * float(lf.std()) if lf is not None else float("nan")

    # D조 §1.4 의 결/구조 지표 — 원해상 |∇L|>0.02 · 8× 다운샘플 후 동일 임계
    gy, gx = np.gradient(y30n)
    edge_pct = 100.0 * float((np.hypot(gx, gy) > 0.02).mean())
    d8 = box_downsample(y30n, 8)
    if d8 is not None:
        sy, sx = np.gradient(d8)
        struct_pct = 100.0 * float((np.hypot(sx, sy) > 0.02).mean())
    else:
        struct_pct = float("nan")

    fg, w80 = flat_gnd_of(path)

    # D_special §1.2 밴드(0~5 m) — 그 조사 표의 `flat %`·`>0.8 %` 재현용
    y5 = luma(rgb255[int(D5M_TOP * H):]) / 255.0
    flat5 = 100.0 * float((local_std(y5, 5) < 1.0 / 255).mean())
    wht5 = 100.0 * float((y5 > 0.80).mean())

    return dict(
        path=path, name=os.path.basename(path), H=int(H), W=int(rgb255.shape[1]),
        # --- B45 (§3.4(b)) ---
        sd=float(y45.std()), mean=float(y45.mean()),
        p99=float(np.percentile(y45, 99)),
        gt224=100.0 * float((y45 > 224).mean()),
        flat=100.0 * float((local_std(y45 / 255.0, 5) < 1.0 / 255).mean()),
        edge=float(sobel_mag(y45).mean()),
        # --- B30 (§3.4(b) + D조 §1.4) ---
        L_mu=float(y30n.mean()),
        wht=100.0 * float((y30n > 0.80).mean()),
        wht_min=100.0 * float((b30.min(axis=-1) / 255.0 > 0.80).mean()),
        sigma_LF=sig_lf, edge_pct=edge_pct, struct_pct=struct_pct,
        # --- 0~5 m 밴드 (D_special §1.2) ---
        flat5m=flat5, wht5m=wht5,
        # --- 전 프레임 하단 2/3 (imgstats 규약) ---
        flat_gnd=fg, w80=w80,
    )


ROUND_CLASSES = ("post_t1", "ground_only")
# §7.5 A1 이 재범위 지정한 두 지표. `ground_only` 등급에서만 위반 목록에서 빠진다.
T1_SCOPED = ("sd", "σ_LF")


def warns(s, round_class="post_t1"):
    """게이트 위반 목록(전부 WARN — W2 규약).

    `round_class="ground_only"` 면 §7.5 A1 대로 σ_LF·sd 를 위반으로 세지 않고
    `[i]` 접두를 붙여 참고치로만 남긴다. 값은 어느 등급에서도 그대로 계산된다.
    """
    if round_class not in ROUND_CLASSES:
        raise ValueError(f"round_class 는 {ROUND_CLASSES} 중 하나: {round_class!r}")
    info_only = (round_class == "ground_only")
    out = []
    if s["sd"] < G_SD_WARN:
        out.append(("[i] " if info_only else "") + f"sd {s['sd']:.1f}<{G_SD_WARN:g}")
    if s["mean"] > G_MEAN_MAX:
        out.append(f"mean {s['mean']:.0f}>{G_MEAN_MAX:g}")
    if s["gt224"] > G_GT224_MAX:
        out.append(f">224% {s['gt224']:.1f}>{G_GT224_MAX:g}")
    if s["wht"] >= G_WHT_MAX:
        out.append(f"wht% {s['wht']:.1f}≥{G_WHT_MAX:g}")
    if s["flat"] >= G_FLAT_MAX:
        out.append(f"flat% {s['flat']:.1f}≥{G_FLAT_MAX:g}")
    if s["sigma_LF"] < G_SIGLF_WARN:
        out.append(("[i] " if info_only else "")
                   + f"σ_LF {s['sigma_LF']:.2f}<{G_SIGLF_WARN:g}")
    if s["flat_gnd"] >= G_FLATGND_MAX:
        out.append(f"flat_gnd {s['flat_gnd']:.1f}≥{G_FLATGND_MAX:g}")
    return out


def n_warns(s, round_class="post_t1"):
    """참고치 `[i]` 를 뺀 실제 WARN 개수 — 라운드 표에 세는 수치."""
    return sum(1 for w in warns(s, round_class) if not w.startswith("[i] "))


COLS = [("sd", "{:>7.1f}"), ("mean", "{:>6.0f}"), ("p99", "{:>6.0f}"),
        (">224%", "{:>7.2f}"), ("flat%", "{:>7.2f}"), ("edge", "{:>6.1f}"),
        ("L_mu", "{:>6.3f}"), ("wht%", "{:>7.1f}"), ("σ_LF", "{:>7.2f}"),
        ("edg%", "{:>6.1f}"), ("str%", "{:>6.1f}"),
        ("f5m", "{:>6.1f}"), ("w5m", "{:>6.1f}"), ("f_gnd", "{:>7.1f}")]
KEYS = ["sd", "mean", "p99", "gt224", "flat", "edge",
        "L_mu", "wht", "sigma_LF", "edge_pct", "struct_pct",
        "flat5m", "wht5m", "flat_gnd"]


def _row(label, s, gate, round_class="post_t1"):
    line = f"{label[:44]:<45}"
    for (h, f), k in zip(COLS, KEYS):
        line += f.format(s[k])
    if gate:
        w = warns(s, round_class)
        line += ("  " + ", ".join(w)) if w else "  ok"
    return line


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="근경 밴드 지표 (t1 spec v1.1 §3.4(b) 정본)")
    ap.add_argument("patterns", nargs="+", help="PNG glob 패턴 (** 재귀 지원)")
    ap.add_argument("--json", help="기계 판독용 JSON 출력 경로")
    ap.add_argument("--gate", action="store_true",
                    help="게이트 위반 표시(W2 규약상 WARN 만 — 종료코드는 항상 0)")
    ap.add_argument("--median", action="store_true",
                    help="입력 전체의 컷별 중앙값 1행만 낸다(t1 §2.2 의 'h0.3 3컷 중앙값')")
    ap.add_argument("--round-class", default="post_t1", choices=ROUND_CLASSES,
                    help="§7.5 A1 라운드 등급. post_t1(기본) = σ_LF·sd WARN 발화 · "
                         "ground_only = 둘을 [i] 참고치로 격하")
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
            rows.append(stats(p))
        except Exception as e:
            print(f"[경고] {p}: {e}", file=sys.stderr)
    if not rows:
        return 2

    hdr = f"{'cut':<45}" + "".join(
        f.replace(".1f", "s").replace(".2f", "s").replace(".0f", "s")
         .replace(".3f", "s").format(h) for h, f in COLS)
    print(hdr)
    print("-" * (len(hdr) + 4))

    if a.median:
        med = {k: float(np.median([r[k] for r in rows])) for k in KEYS}
        med.update(name="(median)", path="", H=rows[0]["H"], W=rows[0]["W"],
                   wht_min=float(np.median([r["wht_min"] for r in rows])),
                   w80=float(np.median([r["w80"] for r in rows])))
        print(_row(f"(중앙값 · {len(rows)}컷)", med, a.gate, a.round_class))
        rows = [med]
    else:
        for s in rows:
            lbl = os.path.join(os.path.basename(os.path.dirname(s["path"])),
                               s["name"])
            print(_row(lbl, s, a.gate, a.round_class))

    if a.json:
        os.makedirs(os.path.dirname(os.path.abspath(a.json)) or ".", exist_ok=True)
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False, indent=1)
        print(f"\nJSON → {a.json}")
    return 0                              # W2 규약: WARN 만, 종료코드로 막지 않는다


if __name__ == "__main__":
    sys.exit(main())
