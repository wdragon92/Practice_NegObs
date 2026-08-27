#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""센서 효과 후처리 증강 v1 — 렌더 재실행 0으로 저수준 도메인 갭을 닫는다.

근거 (scene_audit_realism_survey_v1 §5.1 권고 1)
----
Carlson et al., ECCV-W 2018 (arXiv:1803.07721): 물리 기반 센서 효과(색수차·블러·
노출·샷/리드 노이즈·색온도) 후처리만으로 VKITTI 검출 +7.28 AP — 증강 2,975장이
무증강 50,000장을 이겼다. 반면 일반 기하 증강(회전·크롭)은 −3.14 로 해로움.
노이즈 모델: RAW 도메인 포아송(샷)+가우스(리드) — 선형광에서 σ²(I)=k·I+r²
(Wei et al. 2020). 렌더 노이즈 플로어 실측 1.04/255 vs 실사 2.96/255 (~3배 갭).

설계 원칙
----
* **학습(data 롤) 전용.** 판정(judge) 라운드에 절대 적용하지 않는다 — regr 오염.
* 결정론: 파일명+시드에서 파라미터 유도(재현 가능, 같은 입력 = 같은 출력).
* 선형광 왕복: sRGB → linear 에서 노이즈/노출, 다시 sRGB (IEC 61966-2-1).
* 파라미터 대역은 Carlson 의 보수 대역을 IMX219(현 hFOV 62.2 기준 카메라)에
  맞춰 절반 강도로 시작 — 과증강은 실사에 없는 아티팩트를 새로 가르친다.

사용
----
    python3 scripts/sensor_augment.py --in dataset/<group>/<run>/train \
                                      --out dataset/<run>_aug/train
    python3 scripts/sensor_augment.py --in <dir> --out <dir> --seed 7 --strength 1.0

경로 규약(0827 재편): 라운드는 목적별 그룹 한 칸 아래에 산다 — `dataset/<group>/<round>`.
그룹 이름을 외울 필요는 없다. `dataset/ROUNDS.json` 또는
`variation_kit.round_dir("<라운드이름>")`(셸은 `negobs_round`)가 실제 경로를 돌려준다.
새로 렌더한 라운드는 아직 그룹이 없으므로 `dataset/<round>` 에 평평하게 떨어진다.
"""
import argparse
import glob
import hashlib
import os

import numpy as np
from PIL import Image, ImageFilter

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _srgb_to_linear(a):
    return np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)


def _linear_to_srgb(a):
    a = np.clip(a, 0.0, 1.0)
    return np.where(a <= 0.0031308, 12.92 * a,
                    1.055 * a ** (1 / 2.4) - 0.055)


def _rng_for(path, seed):
    h = hashlib.sha256(f"{os.path.basename(path)}|{seed}".encode()).digest()
    return np.random.default_rng(int.from_bytes(h[:8], "little"))


def augment(img, rng, s=1.0):
    """One image, all effects. `s` scales every effect amplitude at once."""
    a = np.asarray(img.convert("RGB")).astype(np.float64) / 255.0

    # (1) chromatic aberration — R/B 채널 반경 스케일 (Carlson 단독 +6.48 AP)
    ca = 1.0 + rng.uniform(0.0004, 0.0012) * s
    h, w, _ = a.shape
    yy, xx = np.mgrid[0:h, 0:w]
    cy, cx = (h - 1) / 2.0, (w - 1) / 2.0
    out = a.copy()
    for ch, scale in ((0, ca), (2, 1.0 / ca)):
        sy = np.clip((yy - cy) / scale + cy, 0, h - 1)
        sx = np.clip((xx - cx) / scale + cx, 0, w - 1)
        y0, x0 = sy.astype(int), sx.astype(int)
        y1, x1 = np.minimum(y0 + 1, h - 1), np.minimum(x0 + 1, w - 1)
        fy, fx = sy - y0, sx - x0
        c = a[..., ch]
        out[..., ch] = (c[y0, x0] * (1 - fy) * (1 - fx) +
                        c[y1, x0] * fy * (1 - fx) +
                        c[y0, x1] * (1 - fy) * fx + c[y1, x1] * fy * fx)
    a = out

    # (2) defocus/모션 근사 블러 (약하게 — slope 를 죽이는 주범이므로 0.3px 상한)
    r = rng.uniform(0.0, 0.3) * s
    if r > 0.05:
        a = np.asarray(Image.fromarray(
            (a * 255).astype(np.uint8)).filter(
                ImageFilter.GaussianBlur(r))).astype(np.float64) / 255.0

    lin = _srgb_to_linear(a)

    # (3) 노출 지터 (선형 배율 ±0.35 EV)
    lin = lin * (2.0 ** rng.uniform(-0.35, 0.35))

    # (4) 색온도 (von Kries 근사 — R/B 게인)
    wb = rng.uniform(-0.06, 0.06) * s
    lin[..., 0] *= (1.0 + wb)
    lin[..., 2] *= (1.0 - wb)

    # (5) 포아송-가우스: σ²(I) = k·I + r²  (실사 플로어 ~3/255 표시역 목표)
    k = rng.uniform(0.0008, 0.0024) * s
    rd = rng.uniform(0.0006, 0.0015) * s
    sigma = np.sqrt(np.clip(k * lin, 0, None) + rd * rd)
    lin = lin + rng.normal(0.0, 1.0, lin.shape) * sigma

    return Image.fromarray(
        (np.clip(_linear_to_srgb(lin), 0, 1) * 255).astype(np.uint8))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="src", required=True)
    ap.add_argument("--out", dest="dst", required=True)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--strength", type=float, default=1.0)
    args = ap.parse_args()
    files = sorted(glob.glob(os.path.join(args.src, "**", "*.png"),
                             recursive=True))
    if not files:
        raise SystemExit(f"입력 PNG 없음: {args.src}")
    n = 0
    for f in files:
        rel = os.path.relpath(f, args.src)
        of = os.path.join(args.dst, rel)
        os.makedirs(os.path.dirname(of), exist_ok=True)
        with Image.open(f) as im:
            augment(im, _rng_for(f, args.seed), args.strength).save(of)
        n += 1
    print(f"[sensor_augment] {n}컷 → {args.dst} (seed {args.seed}, "
          f"strength {args.strength})")


if __name__ == "__main__":
    main()
