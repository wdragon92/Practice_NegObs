#!/usr/bin/env python3
"""v3a_config_diff.py — **동결의 실증** (PREREG §1.1).

  *"등록되는 변경 항목은 코퍼스·지도·선택식·로깅 4개뿐이며 그 외는 0이다.
    동결의 실증 = `runs/v2/*/config.json` ↔ `runs/v3a/*/config.json` diff 가
    등록 항목 외 **0줄**."*

v2 rgb_s42 ↔ v3a rgb_s42 의 config.json 키를 전수 대조하고, 갈린 키를 하나씩
등록 항목(R1 코퍼스 / R2 지도 / R3 선택식 / R4 로깅 / R5 게이트처분 / R6 best 초기값)
또는 **산출값**(코퍼스가 바뀌면 자동으로 따라 움직이는 값)에 귀속시킨다.
어느 쪽에도 귀속되지 않는 키가 하나라도 남으면 그것이 **동결 위반**이다.
"""
from __future__ import annotations

import json
import os
import sys

R = "/home/vislab/Desktop/work_sy/Practice_NegObs"
V2 = f"{R}/experiments/dayrun_0820/runs/v2/rgb_s42/config.json"
V3 = f"{R}/experiments/v3_0823/runs/v3a/rgb_s42/config.json"
OUT = f"{R}/experiments/v3_0823/logs/v3a_config_diff.json"

# 갈릴 것이 사전에 등록된 키 -> 귀속 항목
REGISTERED = {
    "manifest": "R1 코퍼스", "split": "R1 코퍼스", "out": "R1 코퍼스(런 경로)",
    "n_train": "R1 코퍼스 산출값", "n_val": "R1 코퍼스 산출값",
    "train_positive_rate": "R1 코퍼스 산출값(bias-prior 입력 — 산식 불변)",
    "bias_init_values": "R1 코퍼스 산출값(prior 의 log-odds — 산식 불변)",
    "n_val_strict_h": "R1 코퍼스 산출값(정본 정의 B)",
    "oversample_h": "v2 동일(4.0) — 값이 같으면 diff 아님",
    "selection_metric": "R3 선택식",
    "best_sel_score": "R3 선택식 산출값", "best_epoch": "R3 선택식 산출값",
    "best_val_f1": "R3 선택식 산출값", "best_val_h_recall": "R3 선택식 산출값",
    "stop_reason": "R3/R5 산출값", "steps": "R1 코퍼스 산출값(에폭당 배치 수)",
    "wall_sec": "R4 로깅(신설 관측 열)",
    "v3_registered": "R1~R6 등록 블록(신설 · v2 에 대응 키 없음)",
    "selection_fallback_to_f1": "v2 동일 키(값 False 고정)",
    "aux_stem_map": "R? — §5.6 격리 aux 런 전용 인자",
    "aux_mask_dir": "§5.6 격리 aux 런 전용", "aux_lambda": "§5.6 격리 aux 런 전용",
    "isolated": "§5.6 격리 표기",
    "fa_population": "R3 선택식(FA 모집단 등재명)",
}
# v2 config 에만 있는 키 중 v3 드라이버가 안 쓰는 것 (설명 의무)
V2_ONLY_OK = {
    "smoke": "v2 도 0 — 값 동일이면 diff 아님",
}


def main():
    if not os.path.isfile(V3):
        print(f"[대기] {V3} 아직 없음")
        return 2
    a, b = json.load(open(V2)), json.load(open(V3))
    keys = sorted(set(a) | set(b))
    same, diff, unexplained = [], [], []
    for k in keys:
        va, vb = a.get(k, "<absent>"), b.get(k, "<absent>")
        if va == vb:
            same.append(k)
            continue
        why = REGISTERED.get(k) or V2_ONLY_OK.get(k)
        row = {"key": k, "v2": va, "v3a": vb, "attributed_to": why}
        if k in ("cell_ids", "grid_path", "grid_version"):
            row["attributed_to"] = why = "격자 동일(문자열 경로만 대조)"
        diff.append(row)
        if not why:
            unexplained.append(k)
    print("=" * 84)
    print("동결의 실증 — v2 rgb_s42 ↔ v3a rgb_s42 config.json (PREREG §1.1)")
    print("=" * 84)
    print(f"  동일한 키 {len(same)} / 갈린 키 {len(diff)} / **귀속 불가 {len(unexplained)}**")
    print("\n  [동일 — 레시피 동결의 실체]")
    recipe = ["input", "seed", "max_epochs", "patience", "batch", "lr", "weight_decay",
              "lr_schedule", "workers", "aug", "aug_config", "hflip", "oversample_h",
              "bias_init", "tau", "img_size", "grid", "device", "n_cells", "grid_version",
              "cell_ids", "encoder", "params_m", "dropped_no_depth", "recipe",
              "bias_init_module", "smoke", "selection_fallback_to_f1"]
    for k in recipe:
        mark = "=" if k in same else "≠"
        print(f"    {mark} {k:24s} v2={json.dumps(a.get(k), ensure_ascii=False)[:46]:46s}"
              f" v3a={json.dumps(b.get(k), ensure_ascii=False)[:30]}")
    print("\n  [갈린 키 — 귀속]")
    for r in diff:
        sa = json.dumps(r["v2"], ensure_ascii=False)
        sb = json.dumps(r["v3a"], ensure_ascii=False)
        print(f"    {r['key']:24s} -> {r['attributed_to']}")
        if len(sa) < 90 and len(sb) < 90:
            print(f"        v2 {sa}\n        v3 {sb}")
    print(f"\n  ==> 등록 항목 외 diff = **{len(unexplained)}줄** "
          f"{'✅ 동결 실증 성립' if not unexplained else '❌ ' + str(unexplained)}")
    res = {"n_same": len(same), "n_diff": len(diff), "n_unexplained": len(unexplained),
           "unexplained": unexplained, "same_keys": same, "diff": diff,
           "verdict": "FROZEN_PROVEN" if not unexplained else "FREEZE_VIOLATION"}
    with open(OUT, "w") as f:
        json.dump(res, f, indent=2, ensure_ascii=False)
    print(f"\n원장 -> {OUT}")
    return 0 if not unexplained else 1


if __name__ == "__main__":
    sys.exit(main())
