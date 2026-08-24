#!/usr/bin/env python3
"""train_v3.py — v3-A 학습 드라이버. **train_polar.py 를 감싸는 additive 드라이버**.

PREREG_V3.md (FROZEN · sha256 05f41322e52b8e085b4d678c57dba4ee984deff3bfcea960123ae586e9fcf56a)
§1.1 · §5.1 · §5.2 · §5.3 · §5.5 · §5.6 · §4.1 · §6 를 집행한다.

════════════════════════════════════════════════════════════════════════════
 v2 호출 대비 **차이 전수** — 각 항목이 왜 등록된 조작항인지
════════════════════════════════════════════════════════════════════════════
PREREG §1.1: "**등록되는 변경 항목은 코퍼스·지도·선택식·로깅 4개뿐이며 그 외는 0이다.**"

 [R1] 코퍼스        --manifest dataset_manifest_v3_seg3.json --split split_v3_seg3.json
                    (v2: dataset_manifest_v2_full.json / split_v2_full.json)
                    ← §1.1 조작변인 "코퍼스". D91 §9.1 "훈련 정본 = seg3".
 [R2] 지도 규칙     훈련 손실에 **칸 단위 무시 마스크** 적용 (v3_masks.py 정본).
                    loss = Σ(BCE·valid)/Σvalid   (v2: nn.BCEWithLogitsLoss() = 전 칸 평균).
                    마스크 전량 0이면 v2 손실과 **수치 항등**(smoke S4 실측).
                    ← §1.1 조작변인 "지도 규칙" · §5.2 3단 사거리의 1단.
 [R3] 선택식        S = (1−β)·F1 + β·Ĥ − λ·FPR, β=n_H/(n_H+30), Ĥ=(h+1)/(n_H+2), λ=1.0,
                    **세 항 전부 마스크된 칸 제외**, FA 모집단 = `v3_D_arm_cells`,
                    VG-const 미통과 에폭은 S = −∞. 동률 → 이른 에폭.
                    (v2: 0.5·val_f1 + 0.5·val_h_recall)
                    ← §1.1 조작변인 "체크포인트 선택식" · §5.1 · §5.2 3단 사거리의 2단.
                    구현은 selection_v3.compute_selection() **단일 진입점**을 호출할 뿐이다.
 [R4] 로깅          metrics.csv 에 v2 10열을 **그 순서 그대로** 두고 뒤에 append:
                    val_spread(§5.5ⓐ VG-const 입력) · val_frame_fa_all/val_frame_fa_d(§5.5ⓑ,
                    기록만 · 선택식 불참) · sel_* 성분 · vgconst_pass · val_loss_masked.
                    ← §1.1 조작변인 "로깅" · §5.5 로깅 의무 2건 · §4.1 전제.
 [R5] 게이트 처분   VG-const 통과 에폭이 **하나도 없으면** best.pt 를 쓰지 않고
                    `TRAINING_FAILED` 로 종료(exit 3). v2 꼬리코드의 "best.pt 가 없으면
                    마지막 state 를 저장" 경로는 **의도적으로 삭제**했다 — 그게 §6-16 이
                    금지한 조용한 폴백이고 convnext s42·s43 이 출하된 경로다.
                    ← §4.1 "거부 시 처분" · P-04 · §6-16.
 [R6] best 초기값   best = −inf (v2: −1.0). 신 선택식은 음수 S 를 낼 수 있으므로
                    −1.0 로 두면 정당한 음수 최적을 조기 탈락시킨다. 선택식 교체의 산술적
                    귀결이며 별도 조작항이 아니다.

**그 외 전부 v2 동결**: resnet34 U-Net · lr 3e-4 · AdamW · wd 0.0 · batch 8 · 512² ·
max 150ep · patience 15 · LR 선형감쇠 · AMP 없음 · hflip on · oversample-h 4.0 ·
bias-init prior · τ 0.5 · workers 4 · aug off · drop_last=True · 시드 42/43/44.
레시피 함수는 **train_polar.py 에서 import** 한다(복제 금지):
  guard_gpu_free · set_seed · is_strict_h · make_sampler · set_prior_bias · cell_stats.

**평가 코드 경로는 한 줄도 건드리지 않는다** (§5.2 3단 사거리의 3단 · §6-3).

--aux-mask-dir 는 §5.6 **격리 aux 런 1개 전용**이다. 본 A/B 판정에 혼입 금지.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import sys
import time

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

MAINRUN = "/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/mainrun_0819/code"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, MAINRUN)
sys.path.insert(0, HERE)

import gridspec                                                            # noqa: E402
import model_factory                                                       # noqa: E402
import train_polar as TP        # ← 레시피 정본. 수정하지 않고 import 만 한다.  # noqa: E402
import selection_v3 as SV       # ← 선택식·게이트·분모 정본                    # noqa: E402
import v3_masks as VM           # ← 무시 마스크 정본                          # noqa: E402
from polar_dataset_v3 import PolarGridDatasetV3                            # noqa: E402

PREREG_SHA = "05f41322e52b8e085b4d678c57dba4ee984deff3bfcea960123ae586e9fcf56a"
EXIT_TRAINING_FAILED = 3


def build_argparser():
    p = argparse.ArgumentParser(description="v3-A 학습 드라이버 (train_polar.py additive wrapper)")
    # ---- v2 레시피 인자: 기본값을 v2 config.json 과 자릿수까지 일치시킨다 ----
    p.add_argument("--manifest", required=True)
    p.add_argument("--split", required=True)
    p.add_argument("--input", choices=["rgb", "depth"], required=True)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out", required=True)
    p.add_argument("--max-epochs", type=int, default=150)
    p.add_argument("--patience", type=int, default=15)
    p.add_argument("--batch", type=int, default=8)
    p.add_argument("--lr", type=float, default=3e-4)
    p.add_argument("--weight-decay", type=float, default=0.0)
    p.add_argument("--lr-schedule", choices=["linear", "const"], default="linear")
    p.add_argument("--workers", type=int, default=4)
    p.add_argument("--aug", action="store_true")
    p.add_argument("--aug-config", default=None)
    p.add_argument("--hflip", choices=["on", "off"], default="on")
    p.add_argument("--oversample-h", type=float, default=4.0, metavar="K")
    p.add_argument("--bias-init", choices=["prior", "zero"], default="prior")
    p.add_argument("--tau", type=float, default=0.5)
    p.add_argument("--aux-mask-dir", default=None, help="[§5.6 격리 aux 런 전용]")
    p.add_argument("--aux-lambda", type=float, default=0.5)
    p.add_argument("--aux-stem-map", default=None, help="v3 frame_id -> 아모달 PNG stem (json)")
    p.add_argument("--smoke", type=int, default=0)
    p.add_argument("--img-size", type=int, default=512)
    p.add_argument("--encoder", default=getattr(model_factory, "ENCODER", "resnet34"))
    # ---- v3 등록 인자 ----
    p.add_argument("--fa-population", default=SV.FA_POPULATION_DEFAULT_V3,
                   help="selection_v3.FA_POPULATIONS 등재명. 미등록 이름은 하드 실패(§5.1)")
    p.add_argument("--isolated", action="store_true",
                   help="본 A/B 판정 비혼입 표기(격리 런). config.json 에 각인된다.")
    gridspec.add_grid_arg(p)
    return p


# ─────────────────────────────────────────────────────────── 마스크 인지 손실
def masked_bce(logits, y, valid, crit_none):
    """[R2] 무시 마스크 적용 손실. 마스크된 칸은 분자에도 분모에도 들어가지 않는다.

    valid 가 전량 1 이면 nn.BCEWithLogitsLoss() 와 **수치 항등**이다(smoke S4).
    """
    l = crit_none(logits, y)
    den = valid.sum()
    if float(den) <= 0:
        return l.sum() * 0.0
    return (l * valid).sum() / den


# ───────────────────────────────────────────────────────────────── val 평가
@torch.no_grad()
def evaluate_v3(model, loader, device, crit, crit_none, tau, IGN, FA, tiers):
    """v2 evaluate() 를 그대로 재현하고 + 선택식 입력(확률행렬)을 함께 돌려준다.

    val 로더는 shuffle=False · drop_last=False 이므로 출력 순서 = 데이터셋 순서이고,
    IGN/FA/tiers 는 같은 순서로 미리 만들어 둔 행렬이다(로더를 통과시키지 않는다).
    """
    model.eval()
    tot, tot_m, n = 0.0, 0.0, 0
    P, G = [], []
    for batch in loader:
        x, y, ign = batch[0], batch[1], batch[3]
        x, y = x.to(device, non_blocking=True), y.to(device, non_blocking=True)
        logits = model(x)
        if isinstance(logits, tuple):
            logits = logits[0]
        tot += float(crit(logits, y)) * x.size(0)          # v2 정의 그대로(비마스크)
        tot_m += float(masked_bce(logits, y, (1.0 - ign).to(device), crit_none)) * x.size(0)
        n += x.size(0)
        P.append(torch.sigmoid(logits).cpu().numpy())
        G.append(y.cpu().numpy())
    prob, gt = np.concatenate(P), np.concatenate(G)
    assert prob.shape == IGN.shape, f"val 정렬 파손: {prob.shape} vs {IGN.shape}"
    # v2 열 (비마스크 · 정의 불변)
    f1, rec, fpr = TP.cell_stats(prob, gt, tau)
    hrec, n_h_raw = TP.h_frame_recall(prob, gt, tiers, tau)
    vloss_m = tot_m / max(n, 1)
    # 프레임 단위 FA (§5.5ⓑ — 기록만, 선택식 불참)
    fired = (prob >= tau).any(1)
    neg_frame = ~(gt > 0.5).any(1)
    fa_all = float(fired[neg_frame].mean()) if neg_frame.any() else float("nan")
    d_arm = FA.any(1)
    fa_d = float(fired[d_arm].mean()) if d_arm.any() else float("nan")
    return dict(loss=tot / max(n, 1), loss_masked=vloss_m, f1=f1, recall=rec, fpr=fpr,
                h_recall=hrec, n_h_raw=n_h_raw, prob=prob, gt=gt,
                frame_fa_all=fa_all, frame_fa_d=fa_d)


def main(argv=None):
    args = build_argparser().parse_args(argv)
    if args.fa_population not in SV.FA_POPULATIONS:
        raise SystemExit(f"[VG-fa] 미등록 FA 모집단: {args.fa_population}")
    grid = gridspec.from_args(args)
    device = torch.device(TP.guard_gpu_free())
    if device.type == "cuda" and not torch.cuda.is_available():
        device = torch.device("cpu")
    TP.set_seed(args.seed)                                   # v2 동결
    os.makedirs(args.out, exist_ok=True)
    print(f"[grid] {grid.summary()}  <- {grid.path}")
    print(f"[prereg] FROZEN sha256 {PREREG_SHA[:8]}…  |  {VM.K_SEAL}")

    stem_map = json.load(open(args.aux_stem_map)) if args.aux_stem_map else None
    aux_on = bool(args.aux_mask_dir)
    dtr = PolarGridDatasetV3(args.manifest, args.split, "train", args.input,
                             train_aug=args.aug, img_size=args.img_size,
                             aug_config=TP.load_aug_config(args.aug_config),
                             seed=args.seed, grid=grid, train_hflip=(args.hflip == "on"),
                             aux_mask_dir=args.aux_mask_dir, aux_stem_map=stem_map)
    dva = PolarGridDatasetV3(args.manifest, args.split, "val", args.input,
                             train_aug=False, img_size=args.img_size, seed=args.seed, grid=grid)
    sampler = TP.make_sampler(dtr, args)                      # v2 oversample-h 4.0
    common = dict(num_workers=args.workers, pin_memory=(device.type == "cuda"),
                  persistent_workers=args.workers > 0)
    ltr = DataLoader(dtr, batch_size=args.batch, shuffle=(sampler is None), sampler=sampler,
                     drop_last=True, **common)
    lva = DataLoader(dva, batch_size=args.batch, shuffle=False, drop_last=False, **common)
    if len(ltr) == 0:
        raise SystemExit("[fatal] 0 train batches")

    # ── 분모 원장 (VG-denom: 두 정의를 둘 다 세고 발산 시 하드 실패) ──────────
    n_val_h_rawB, div = SV.count_hazard_h(dva.items)
    IGN = dva.ignore_matrix()
    FA = dva.fa_matrix()
    TIERS = np.asarray(dva.tiers())
    GTV = dva.gt_matrix()
    pos_eff = (GTV > 0.5) & (IGN == 0)
    n_val_h_eff = int(((TIERS == "H") & pos_eff.any(1)).sum())
    beta_eff = SV.beta_weight(n_val_h_eff)
    n_fa_cells = int(((FA == 1) & (IGN == 0)).sum())
    print(f"[denom] val hazard-H 정의B(원) {n_val_h_rawB} (정의A 발산 {div}) -> "
          f"마스크 후 유효 n_H {n_val_h_eff}  beta {beta_eff:.4f}")
    print(f"[denom] FA 모집단 {args.fa_population}: 유효 칸 {n_fa_cells} "
          f"(D팔 프레임 {int(FA.any(1).sum())})")
    print(f"[mask] train census {json.dumps(dtr.mask_census['channels'], ensure_ascii=False)} "
          f"cells {dtr.mask_census['n_cells_masked']}")
    print(f"[mask] val   census {json.dumps(dva.mask_census['channels'], ensure_ascii=False)} "
          f"cells {dva.mask_census['n_cells_masked']}")

    # ── 모델 (v2 동결) ────────────────────────────────────────────────────────
    fkw = {}
    if aux_on:
        fkw["use_mask_head"] = True
    if args.encoder != getattr(model_factory, "ENCODER", "resnet34"):
        fkw["encoder_name"] = args.encoder
    model = model_factory.build(args.input, classes=grid.n_cells, **fkw).to(device)
    if aux_on:
        print(f"[aux] pixel BCE ON lambda={args.aux_lambda:g} masks {dtr.n_aux_found} found / "
              f"{dtr.n_aux_missing} missing-as-empty of {len(dtr)}  dir={args.aux_mask_dir}")
    prior = dtr.positive_rate()
    bias_mod, bias_vals = (None, None)
    if args.bias_init == "prior":
        bias_mod, bias_vals = TP.set_prior_bias(model, prior, grid.n_cells)
    crit = nn.BCEWithLogitsLoss()                       # v2 정의(관측용 val_loss)
    crit_none = nn.BCEWithLogitsLoss(reduction="none")  # [R2] 마스크 손실
    crit_aux = nn.BCEWithLogitsLoss()
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    sched = torch.optim.lr_scheduler.LambdaLR(
        opt, (lambda e: max(0.0, 1.0 - e / max(args.max_epochs, 1)))
        if args.lr_schedule == "linear" else (lambda e: 1.0))

    # ── config.json — v2 키 순서 보존 + v3 등록 블록 ─────────────────────────
    argsd = {k: v for k, v in vars(args).items()
             if k not in ("encoder", "fa_population", "isolated", "aux_stem_map")}
    cfg = dict(argsd, device=device.type, n_train=len(dtr), n_val=len(dva),
               n_cells=grid.n_cells, grid_version=grid.version, grid_path=grid.path,
               cell_ids=grid.cell_ids,
               encoder=getattr(model_factory, "config_encoder_label",
                               lambda e: f"{e}-unet-aux")(args.encoder),
               params_m=round(sum(p.numel() for p in model.parameters()) / 1e6, 3),
               dropped_no_depth=dtr.n_dropped_no_depth + dva.n_dropped_no_depth,
               recipe="v2", hflip=(args.hflip == "on"), oversampled=sampler is not None,
               train_positive_rate=[round(float(x), 6) for x in prior],
               bias_init_module=bias_mod, bias_init_values=bias_vals,
               n_val_strict_h=n_val_h_rawB,
               selection_metric=SV.FORMULA_ID)
    if aux_on:
        cfg.update(aux_enabled=True, aux_masks_found=dtr.n_aux_found,
                   aux_masks_missing_as_empty=dtr.n_aux_missing,
                   aux_loss="BCE_masked(cell_logits,y) + aux_lambda*BCE(mask_logits,mask)",
                   aux_val_note="val/selection stay CELL-ONLY (v2 규약 승계)")
    else:
        cfg.pop("aux_mask_dir", None)
        cfg.pop("aux_lambda", None)
    cfg["v3_registered"] = {
        "arm": "v3-A", "prereg_sha256": PREREG_SHA,
        "isolated_from_ab": bool(args.isolated),
        "R1_corpus": {"manifest": args.manifest, "split": args.split,
                      "n_train": len(dtr), "n_val": len(dva)},
        "R2_supervision": {"ignore_spec": VM.SPEC_ID, "k_cue_px": VM.K_CUE_PX,
                           "k_seal": VM.K_SEAL, "mask_scope": VM.MASK_SCOPE,
                           "loss": "sum(BCE*valid)/sum(valid)",
                           "train_census": dtr.mask_census,
                           "val_census": dva.mask_census},
        "R3_selection": {"formula": SV.FORMULA_ID, "h_def": SV.H_DEF_ID,
                         "lam": SV.LAMBDA_FA, "a": SV.LAPLACE_A, "n0": SV.N0_HALF_TRUST,
                         "selection_fa_population": args.fa_population,
                         "n_val_H_defB_raw": n_val_h_rawB,
                         "n_val_H_effective": n_val_h_eff, "beta_effective": beta_eff,
                         "n_fa_cells_effective": n_fa_cells,
                         "vgconst_spread_min": SV.VGCONST_SPREAD_MIN,
                         "vgconst_stage": SV.VGCONST_STAGE,
                         "mask_applied_to_selection": True},
        "R4_logging": ["val_spread", "val_frame_fa_all", "val_frame_fa_d",
                       "sel_f1", "sel_fa", "sel_h_hits", "sel_n_H", "sel_beta",
                       "sel_H_hat", "vgconst_pass", "val_loss_masked"],
        "R5_gate_disposition": "no VG-const pass epoch -> TRAINING_FAILED, no best.pt (§6-16)",
        "R6_best_init": "-inf (v2: -1.0) — 신 선택식이 음수 S 를 낼 수 있어서",
        "frozen_recipe": "resnet34-unet / lr 3e-4 / AdamW / wd 0 / batch 8 / 512^2 / "
                         "max 150ep / patience 15 / linear LR / no AMP / hflip on / "
                         "oversample-h 4.0 / bias prior / tau 0.5",
    }
    with open(os.path.join(args.out, "config.json"), "w") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)
    print(f"[cfg] {args.input} enc={args.encoder} params={cfg['params_m']:g}M "
          f"train={len(dtr)} val={len(dva)} batches/ep={len(ltr)} cells={grid.n_cells} "
          f"dev={device.type}" + (f" aux={args.aux_lambda:g}" if aux_on else ""))

    # ── 학습 루프 (v2 구조 그대로 · [R2][R3][R4][R5][R6] 만 다름) ────────────
    V2_COLS = ["epoch", "train_loss", "val_loss", "val_f1", "val_recall", "val_fpr",
               "lr", "sec", "val_h_recall", "sel_score"]
    V3_COLS = ["val_spread", "vgconst_pass", "sel_f1", "sel_fa", "sel_h_hits", "sel_n_H",
               "sel_beta", "sel_H_hat", "val_frame_fa_all", "val_frame_fa_d", "val_loss_masked"]
    mcsv = open(os.path.join(args.out, "metrics.csv"), "w", newline="")
    wr = csv.writer(mcsv)
    wr.writerow(V2_COLS + V3_COLS + (["train_loss_cell", "train_loss_aux"] if aux_on else []))
    best, best_ep, bad, steps = float("-inf"), -1, 0, 0     # [R6]
    best_sel = None
    stop_reason = "max_epochs"
    t_wall = time.time()

    for ep in range(1, args.max_epochs + 1):
        t0 = time.time()
        model.train()
        run, run_cell, run_aux, seen = 0.0, 0.0, 0.0, 0
        for batch in ltr:
            if aux_on:
                x, y, _m, ign, mk = batch
            else:
                x, y, _m, ign = batch
                mk = None
            x, y = x.to(device, non_blocking=True), y.to(device, non_blocking=True)
            valid = (1.0 - ign).to(device, non_blocking=True)          # [R2]
            opt.zero_grad(set_to_none=True)
            if aux_on:
                logits, mask_logits = model(x)
                l_cell = masked_bce(logits, y, valid, crit_none)
                l_aux = crit_aux(mask_logits, mk.to(device, non_blocking=True))
                loss = l_cell + args.aux_lambda * l_aux
                run_cell += float(l_cell) * x.size(0)
                run_aux += float(l_aux) * x.size(0)
            else:
                loss = masked_bce(model(x), y, valid, crit_none)
            loss.backward()
            opt.step()
            run += float(loss) * x.size(0)
            seen += x.size(0)
            steps += 1
            if args.smoke and steps >= args.smoke:
                break
        tr_loss = run / max(seen, 1)
        tr_cell, tr_aux = run_cell / max(seen, 1), run_aux / max(seen, 1)
        va = evaluate_v3(model, lva, device, crit, crit_none, args.tau, IGN, FA, TIERS)
        # ── [R3] 선택식: selection_v3 단일 진입점 ──────────────────────────
        sc = SV.compute_selection(va["prob"], va["gt"], TIERS, args.tau,
                                  ignore=IGN.astype(bool), fa_cells=FA.astype(bool),
                                  fa_population=args.fa_population)
        sel = sc["S"]
        lr_now = opt.param_groups[0]["lr"]
        sched.step()
        sec = time.time() - t0
        ok_h = math.isfinite(va["h_recall"])
        f6 = lambda v: ("nan" if v is None or not math.isfinite(float(v)) else f"{float(v):.6f}")  # noqa: E731
        wr.writerow([ep, f"{tr_loss:.6f}", f"{va['loss']:.6f}", f"{va['f1']:.6f}",
                     f"{va['recall']:.6f}", f"{va['fpr']:.6f}", f"{lr_now:.3e}", f"{sec:.2f}",
                     (f"{va['h_recall']:.6f}" if ok_h else "nan"),
                     ("-inf" if sel == float("-inf") else f"{sel:.6f}")]
                    + [f"{sc['spread']:.6e}", int(sc["vgconst_pass"]), f6(sc["f1"]),
                       f6(sc["fa"]), sc["h_hits"], sc["n_H"], f6(sc["beta"]), f6(sc["H_hat"]),
                       f6(va["frame_fa_all"]), f6(va["frame_fa_d"]), f6(va["loss_masked"])]
                    + ([f"{tr_cell:.6f}", f"{tr_aux:.6f}"] if aux_on else []))
        mcsv.flush()
        print(f"ep {ep:3d} tr {tr_loss:.4f} val {va['loss']:.4f} f1 {va['f1']:.4f} "
              f"fpr {va['fpr']:.4f} | sel_f1 {sc['f1']:.4f} h {sc['h_hits']}/{sc['n_H']} "
              f"fa {sc['fa']:.4f} spread {sc['spread']:.2e} "
              f"{'PASS' if sc['vgconst_pass'] else 'FAIL'} S "
              f"{'-inf' if sel == float('-inf') else f'{sel:.4f}'} "
              f"lr {lr_now:.2e} {sec:.1f}s")

        ck = dict(state_dict=model.state_dict(), config=cfg, epoch=ep, val_f1=va["f1"],
                  val_h_recall=va["h_recall"], sel_score=(None if sel == float("-inf") else sel),
                  sel_components={k: v for k, v in sc.items() if k != "S"},
                  grid_version=grid.version, n_cells=grid.n_cells)
        torch.save(ck, os.path.join(args.out, "last.pt"))
        if sel > best:                       # 동률 -> 이른 에폭 (v2 :435 규칙 승계)
            best, best_ep, bad = sel, ep, 0
            best_sel = dict(sc)
            torch.save(ck, os.path.join(args.out, "best.pt"))
            np.save(os.path.join(args.out, "val_probs_best.npy"),
                    va["prob"].astype(np.float32))
        else:
            bad += 1
            if bad >= args.patience:
                stop_reason = f"early_stop@{ep}"
                break
        if args.smoke and steps >= args.smoke:
            stop_reason = "smoke"
            break

    mcsv.close()
    wall = time.time() - t_wall
    jnum = lambda v: (None if v is None or not math.isfinite(float(v)) else float(v))  # noqa: E731
    training_failed = (best_ep < 0)                                        # [R5]
    cfg.update(best_sel_score=jnum(best), best_epoch=(None if training_failed else best_ep),
               stop_reason=("TRAINING_FAILED" if training_failed else stop_reason),
               steps=steps, wall_sec=round(wall, 1),
               best_val_f1=(jnum(best_sel["f1"]) if best_sel else None),
               best_val_h_recall=None if not best_sel or not best_sel["n_H"]
               else best_sel["h_hits"] / best_sel["n_H"],
               selection_fallback_to_f1=False)
    cfg["v3_registered"]["selected"] = ({} if training_failed else {
        "epoch": best_ep, "S": jnum(best), "components": {
            k: (jnum(v) if isinstance(v, float) else v)
            for k, v in best_sel.items() if k != "S"},
        "vg1ep_flag": bool(best_ep <= 1)})
    with open(os.path.join(args.out, "config.json"), "w") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)

    if training_failed:
        # [R5] §6-16 — 조용한 폴백 출하 금지. best.pt 를 쓰지 않는다.
        with open(os.path.join(args.out, "TRAINING_FAILED"), "w") as f:
            f.write("VG-const 통과 에폭 0 -> 체크포인트 없이 종료 (PREREG §4.1 · P-04 · §6-16)\n")
        print("[TRAINING_FAILED] VG-const 통과 에폭 없음 — best.pt 미기록, 폴백 금지",
              file=sys.stderr)
        return EXIT_TRAINING_FAILED
    with open(os.path.join(args.out, "DONE"), "w") as f:
        json.dump({"run": os.path.basename(args.out), "best_epoch": best_ep, "S": jnum(best),
                   "stop_reason": stop_reason, "wall_sec": round(wall, 1), "steps": steps,
                   "vgconst_pass": True, "vg1ep_flag": bool(best_ep <= 1)}, f, indent=2)
    print(f"[done] {stop_reason} S={best:.4f} @ep{best_ep} wall={wall / 60:.1f}min -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
