#!/usr/bin/env python3
"""R4 — CUE-OFF 팔 간 실측 픽셀 질량 (사전등록 §3의 AABB 추정치 검증).

PREREG_CUEOFF.md §3 은 플라시보 정합성 등급(GREEN / 12-30x 보수 / 18x 보수)을
`pixel_mass.py` 의 **월드 AABB 투영 상한값**으로 매겼다. 렌더가 이미 존재하므로
같은 질문을 실물 프레임에서 직접 잰다. 임계는 F7(`rt_response/F7_HPAIR_PIXDIFF.md`)
결론대로 **>=32/255** 을 정본으로 쓴다(2/255 는 렌더러 잡음 바닥).

사용:  python3 r4_pixdiff.py            (기본 8컷/쌍)
       python3 r4_pixdiff.py 24         (전 컷)
"""
import glob
import os
import sys

import numpy as np
from PIL import Image

# 0827 reorg: dataset/ is grouped (dataset/<group>/<round>) and a round is
# found by NAME, never by a flat path. See Docs/reorg_0827/S3_report.md.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))                              # noqa: E402
from variation_kit import DATASET_ROOT, round_dir_or_flat   # noqa: E402

DS = DATASET_ROOT                 # 0827: no hardcoded absolute root
N = int(sys.argv[1]) if len(sys.argv) > 1 else 8
# (씬, cueoff 라운드 안의 split 폴더, 계보 밴드 라운드)
#   밴드는 PREREG_CUEOFF §2.1 그대로: s12=boost_e · s17=boost_h · s20=boost_e2.
#   틀린 밴드끼리 비교하면 포즈가 달라 숫자가 무의미해진다.
SCENES = [("scene12", "test", "260820_boost_e"),
          ("scene17", "train", "260820_boost_h"),
          ("scene20", "train", "260820_boost_e2")]


def load(p):
    return np.asarray(Image.open(p).convert("RGB"), dtype=np.int16)


def diff_stats(dir_a, dir_b, n=N):
    """평균 (>=2, >=8, >=32) 픽셀 수와 프레임 대비 비율."""
    A = sorted(glob.glob(os.path.join(dir_a, "*.png")))
    rows = []
    for a in A[:n]:
        b = os.path.join(dir_b, os.path.basename(a))
        if not os.path.exists(b):
            continue
        d = np.abs(load(a) - load(b)).max(axis=2)
        rows.append(((d >= 2).sum(), (d >= 8).sum(), (d >= 32).sum(), d.size))
    if not rows:
        return None
    r = np.array(rows, dtype=float).mean(axis=0)
    return len(rows), r[0], r[1], r[2], r[2] / r[3] * 100.0


def main():
    print(f"threshold levels: >=2 / >=8 / >=32 (F7 정본) · n<= {N} 컷/쌍\n")
    for sc, sub, band in SCENES:
        base_a = os.path.join(round_dir_or_flat("260823_cueoff_A"), sub, sc)
        if not os.path.isdir(base_a):
            continue
        print(f"== {sc}")
        for arm in ("B1", "B2", "P", "C"):
            b = base_a.replace("cueoff_A", f"cueoff_{arm}")
            r = diff_stats(base_a, b)
            if r is None:
                print(f"   A vs {arm:2}  (팔 없음)")
                continue
            print(f"   A vs {arm:2}  n={r[0]:2}  >=2 {r[1]:9.0f}  "
                  f">=8 {r[2]:9.0f}  >=32 {r[3]:9.0f} ({r[4]:5.2f}% of frame)")
        # 계보 대조 — 잡음 바닥(A vs 정본 on)과 C vs 정본 off
        for nm, a_dir, b_dir in (
            ("A  vs lineage_on ", base_a, round_dir_or_flat(f"{band}_on")),
            ("C  vs lineage_off", base_a.replace("cueoff_A", "cueoff_C"),
             round_dir_or_flat(f"{band}_off")),
        ):
            hit = [d for d in glob.glob(f"{b_dir}/*/{sc}") if os.path.isdir(d)]
            if not hit:
                continue
            b_dir = hit[0]
            r = diff_stats(a_dir, b_dir)
            if r:
                print(f"   {nm}  n={r[0]:2}  >=2 {r[1]:9.0f}  "
                      f">=8 {r[2]:9.0f}  >=32 {r[3]:9.0f} ({r[4]:5.2f}%)")
        print()


if __name__ == "__main__":
    main()
