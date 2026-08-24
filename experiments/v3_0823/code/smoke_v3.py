#!/usr/bin/env python3
"""smoke_v3.py — 1프레임/1배치 적재 + 마스크 채널 정합 검사 (학습 착수 전 필수).

지시된 3개 단언 + 항등 대조 2개를 **실측으로** 인쇄한다.

  S1  맨-가림 H(bare-H) 프레임의 손실 마스크가 그 프레임의 **H 칸(GT 양성)을 실제로 0으로 만든다**
  S2  레버 ㄴ C 프레임이 **손실에서 통째로 제외**된다 (전 칸 마스크)
  S3  gt_void 칸이 **손실에서 제외**된다 (그리고 평가 경로에는 손대지 않았다)
  S4  마스크 전량 0 -> masked_bce == nn.BCEWithLogitsLoss()  (v2 손실과 수치 항등)
  S5  shim 데이터셋의 x·y 가 원본 PolarGridDataset 과 **바이트 동일** (RNG 소비 순서 포함)
  S6  VG-denom: H 분모 두 정의 발산 0 · FA 모집단 등재명 확인 · k 봉인 인쇄
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
import torch
import torch.nn as nn

MAINRUN = "/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/mainrun_0819/code"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, MAINRUN)
sys.path.insert(0, HERE)

import gridspec                                            # noqa: E402
import selection_v3 as SV                                  # noqa: E402
import v3_masks as VM                                      # noqa: E402
from polar_dataset import PolarGridDataset                 # noqa: E402
from polar_dataset_v3 import PolarGridDatasetV3            # noqa: E402
from train_v3 import masked_bce                            # noqa: E402

ROOT = "/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/v3_0823"
MAN = f"{ROOT}/dataset_manifest_v3_seg3.json"
SPL = f"{ROOT}/split_v3_seg3.json"
GRID = gridspec.load("gridspec_v1.json")

OK = []


def check(tag, cond, msg):
    OK.append((tag, bool(cond), msg))
    print(f"  [{'PASS' if cond else 'FAIL'}] {tag}  {msg}")
    return bool(cond)


def main():
    print("=" * 78)
    print("v3-A 학습 착수 스모크 — 적재 + 마스크 채널 정합")
    print(f"  manifest {os.path.basename(MAN)}   split {os.path.basename(SPL)}")
    print(f"  {VM.K_SEAL}")
    print(f"  mask spec: {VM.SPEC_ID}")
    print("=" * 78)

    M = json.load(open(MAN))
    frames = M["frames"]
    byid = {f["frame_id"]: f for f in frames}

    # ── S1  bare-H ────────────────────────────────────────────────────────────
    print("\nS1  맨-가림 H 프레임의 손실 마스크가 H 칸을 0으로 만드는가")
    bare = [f for f in frames
            if VM.ch_bare_h(f) and any(f["polar_gt"]) and not VM.ch_b_arm_h(f)]
    bare_all = [f for f in frames if VM.ch_bare_h(f)]
    print(f"     bare-H 전체 {len(bare_all)} (A팔 {sum(1 for f in bare_all if f['arm'] == 'A')} · "
          f"B팔 {sum(1 for f in bare_all if f['arm'] == 'B')}) / "
          f"그중 b_arm_h 중복 아닌 GT양성 프레임 {len(bare)}")
    f = bare[0]
    ign = VM.frame_ignore(f)
    pos = [i for i, g in enumerate(f["polar_gt"]) if g]
    px = (f["cue"] or {}).get("px_canonical6")
    print(f"     표본 {f['frame_id']}  arm={f['arm']} tier={f['tier']} "
          f"px_canonical6={px} (< k={VM.K_CUE_PX})")
    print(f"     GT 양성 칸 {pos}")
    print(f"     ignore    {ign}")
    check("S1", all(ign[i] == 1 for i in pos) and len(pos) > 0,
          f"양성 칸 {len(pos)}개 전부 마스크됨 · 음성 칸 마스크 "
          f"{sum(ign) - len(pos)}개(=gt_void 몫)")

    # 손실 실측: 마스크된 칸은 gradient 에 기여하지 않는다
    y = torch.tensor([float(v) for v in f["polar_gt"]])[None]
    valid = 1.0 - torch.tensor([float(v) for v in ign])[None]
    lg = torch.zeros_like(y, requires_grad=True)
    masked_bce(lg, y, valid, nn.BCEWithLogitsLoss(reduction="none")).backward()
    g = lg.grad[0].numpy()
    check("S1-grad", all(abs(g[i]) < 1e-12 for i in pos),
          f"양성 칸 gradient 전부 0 (max |g| on masked = {max(abs(g[i]) for i in pos):.3e}, "
          f"unmasked = {max([abs(v) for i, v in enumerate(g) if ign[i] == 0] + [0]):.3e})")

    # ── S2  레버 ㄴ ───────────────────────────────────────────────────────────
    print("\nS2  레버 ㄴ (영정보 (A,C) 쌍의 C팔) 프레임이 손실에서 제외되는가")
    lev = [f for f in frames if VM.ch_lever_n(f)]
    con = [f for f in lev if (f.get("ignore") or {}).get("lever_n_contradiction")]
    print(f"     레버 ㄴ 플래그 {len(lev)} 프레임 (전부 C팔: "
          f"{set(x['arm'] for x in lev)}) · 진짜 라벨 모순 {len(con)}")
    f = con[0] if con else lev[0]
    ign = VM.frame_ignore(f)
    oa = f.get("optical_ac") or {}
    print(f"     표본 {f['frame_id']}  frac(|dI|>8)={oa.get('frac_gt8')} "
          f"(< 0.001) mean|dI|={oa.get('mean_abs')}")
    print(f"     ignore {ign}  (전 {len(ign)}칸)")
    check("S2", sum(ign) == len(ign),
          f"전 {len(ign)}칸 마스크 = 손실 전량 제외 · 유효 칸 0")
    valid = 1.0 - torch.tensor([float(v) for v in ign])[None]
    y = torch.zeros(1, len(ign))
    lg = torch.zeros_like(y, requires_grad=True)
    loss = masked_bce(lg, y, valid, nn.BCEWithLogitsLoss(reduction="none"))
    check("S2-loss", float(loss) == 0.0, f"그 프레임의 손실 기여 = {float(loss):.6g}")

    # ── S3  gt_void ───────────────────────────────────────────────────────────
    print("\nS3  gt_void 칸이 손실에서 제외되는가 (평가에서는 절대 빼지 않는다)")
    voidf = [f for f in frames if sum(f.get("gt_void") or []) > 0]
    vsimple = [f for f in voidf if not VM.ch_lever_n(f)
               and not (VM.ch_b_arm_h(f) or VM.ch_bare_h(f))]
    print(f"     void 보유 프레임 {len(voidf)} / 칸 "
          f"{sum(sum(f.get('gt_void') or []) for f in frames)}  (PREREG §4.4 VG-void: 765 / 4,227)")
    f = vsimple[0]
    ign = VM.frame_ignore(f)
    vc = [i for i, v in enumerate(f["gt_void"]) if v]
    print(f"     표본 {f['frame_id']}  arm={f['arm']} void 칸 {vc}")
    print(f"     ignore {ign}")
    check("S3", all(ign[i] == 1 for i in vc) and sum(ign) == len(vc),
          f"void 칸 {len(vc)}개만 마스크 · 나머지 {len(ign) - len(vc)}칸은 정상 지도")
    ev_hits = os.popen(
        f"grep -rl 'v3_masks\\|frame_ignore' {ROOT}/../mainrun_0819/code/eval_polar.py "
        f"2>/dev/null | wc -l").read().strip()
    check("S3-eval", ev_hits == "0",
          "평가 코드(eval_polar.py)의 마스크 참조 0회 — §5.2 3단 사거리 · §6-3")

    # ── S4  마스크 off -> v2 손실과 항등 ─────────────────────────────────────
    print("\nS4  마스크 전량 0 -> v2 손실(nn.BCEWithLogitsLoss)과 수치 항등")
    g = torch.Generator().manual_seed(42)
    lg = torch.randn(8, 20, generator=g)
    y = (torch.rand(8, 20, generator=g) > 0.7).float()
    a = float(masked_bce(lg, y, torch.ones_like(y), nn.BCEWithLogitsLoss(reduction="none")))
    b = float(nn.BCEWithLogitsLoss()(lg, y))
    check("S4", abs(a - b) < 1e-12, f"masked {a:.12f} vs v2 {b:.12f}  |Δ|={abs(a - b):.3e}")

    # ── S5  shim 데이터셋 == 원본 데이터셋 (x·y 바이트 동일) ─────────────────
    print("\nS5  shim 데이터셋의 x·y 가 원본 PolarGridDataset 과 바이트 동일한가")
    kw = dict(train_aug=False, img_size=512, seed=42, grid=GRID, train_hflip=True)
    d0 = PolarGridDataset(MAN, SPL, "train", "rgb", **kw)
    d3 = PolarGridDatasetV3(MAN, SPL, "train", "rgb", **kw)
    same_x = same_y = True
    for i in (0, 1, 7, 100, 1000, 2000):
        torch.manual_seed(1234 + i)
        x0, y0, m0 = d0[i]
        torch.manual_seed(1234 + i)
        x3, y3, m3, ig3 = d3[i]
        same_x &= bool(torch.equal(x0, x3))
        same_y &= bool(torch.equal(y0, y3))
    check("S5", same_x and same_y,
          f"6표본 x 동일={same_x} y 동일={same_y} (hflip 동전 위치·RNG 소비 순서 보존)")
    # hflip 시 마스크도 같이 섞이는가
    perm = torch.as_tensor(GRID.flip_perm(), dtype=torch.long)
    idx = next(i for i, r in enumerate(d3.items) if sum(d3.ign[i].tolist()) not in (0, 20))
    base = d3.ign[idx]
    d3.train_hflip = False
    _, _, _, ig_noflip = d3[idx]
    d3.train_hflip, d3.hflip_p = True, 1.0
    _, _, _, ig_flip = d3[idx]
    d3.hflip_p = 0.5
    check("S5-perm", torch.equal(ig_flip, base.index_select(-1, perm)) and
          torch.equal(ig_noflip, base),
          "hflip 시 마스크가 y 와 같은 sector permutation 을 받는다")

    # ── S6  분모·모집단·게이트 ───────────────────────────────────────────────
    print("\nS6  분모 원장 · FA 모집단 · 게이트 상수")
    S = json.load(open(SPL))
    va = [r for r in frames if r["scene_id"] in set(S["val"])]
    tr = [r for r in frames if r["scene_id"] in set(S["train"])]
    n_raw, div = SV.count_hazard_h(va)
    dv = PolarGridDatasetV3(MAN, SPL, "val", "rgb", train_aug=False, img_size=512,
                            seed=42, grid=GRID)
    IGN, GT, TI = dv.ignore_matrix(), dv.gt_matrix(), np.asarray(dv.tiers())
    n_eff = int(((TI == "H") & ((GT > 0.5) & (IGN == 0)).any(1)).sum())
    FA = dv.fa_matrix()
    print(f"     train {len(tr)} / val {len(va)}  (PREREG §5.0: 2,598 / 1,056)")
    print(f"     val hazard-H 정의B={n_raw} 정의A 발산={div} -> 마스크 후 유효 n_H={n_eff} "
          f"beta={SV.beta_weight(n_eff):.4f}")
    print(f"     FA 모집단 {SV.FA_POPULATION_DEFAULT_V3}: 유효 칸 "
          f"{int(((FA == 1) & (IGN == 0)).sum())} / D팔 프레임 {int(FA.any(1).sum())}")
    print(f"     VGCONST_SPREAD_MIN={SV.VGCONST_SPREAD_MIN} stage={SV.VGCONST_STAGE}")
    check("S6", div == 0 and len(tr) == 2598 and len(va) == 1056,
          f"VG-denom 발산 0 · 분할 실측 일치")
    print(f"\n     [census] train {json.dumps(d3.mask_census['channels'], ensure_ascii=False)}")
    print(f"     [census] val   {json.dumps(dv.mask_census['channels'], ensure_ascii=False)}")

    print("\n" + "=" * 78)
    n_pass = sum(1 for _, c, _ in OK if c)
    print(f"스모크 {n_pass}/{len(OK)} PASS")
    for t, c, m in OK:
        if not c:
            print(f"  FAILED {t}: {m}")
    print("=" * 78)
    return 0 if n_pass == len(OK) else 1


if __name__ == "__main__":
    sys.exit(main())
