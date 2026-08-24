#!/usr/bin/env python3
"""v3_masks.py — 무시 마스크(ignore mask)의 **단일 정본 구현**.

PREREG_V3.md (FROZEN sha256 05f41322…) §5.2 / §5.3 · D91 §9.2·§9.3 의 처방을 코드로 옮긴 것.
마스크의 술어·사거리가 **이 파일 한 곳에만** 존재한다 (selection_v3.py 가 분모·점수식에
대해 하는 역할과 같다).

## 등록 채널 4종 (PREREG §5.2 표)

| 채널 | 술어 | 마스크가 덮는 칸 | 상태 |
|---|---|---|---|
| `b_arm_h`             | B팔 ∧ tier=='H'                       | **그 프레임의 GT 양성 칸** | 무조건 적용 |
| `bare_h_by_k`         | tier=='H' ∧ px_canonical6 < k (k=7,000 봉인) | **그 프레임의 GT 양성 칸** | k 봉인 완료(D91 §9.2) |
| `lever_n_zero_info_c` | C팔 ∧ (A,C) frac(\|ΔI\|>8) < 0.001      | **그 프레임의 전 칸**       | 예비채택(OPEN-2 무응답 기본값) |
| `gt_void`             | 그 칸에 void 픽셀 존재                  | **그 칸**                  | 등록 |

### 왜 채널마다 덮는 칸이 다른가 (등록 근거)

* `b_arm_h` / `bare_h_by_k` — PREREG §5.3 문면이 *"B팔의 **H 칸**은 무시 마스크"* ·
  *"맨-가림 H(단서 0)는 무시 마스크"* 이고, 철학은 *"화면에 근거가 없는 **정답**을 강요하지
  않는다"* 이다. 강요되는 정답 = **GT 양성 칸**이므로 마스크는 양성 칸을 덮는다.
  음성 칸은 화면에 근거가 있는 정상 음성이라 v2와 동일하게 지도한다.
  P4_SELECTION §2.6 이 *"**양성 칸이 전부 마스크된** H 프레임은 분모에서 사라진다"*
  라고 쓴 것이 같은 사거리다(칸 단위 마스크의 결과로 프레임이 빠지는 구성).
* `lever_n_zero_info_c` — PREREG §5.2 각주: *"A는 GT 양성, C는 사양 상수 전음성 ⇒ 같은 입력에
  반대 라벨. **모순되는 쪽(C팔 음성)을 손실에서 빼는 것**이 옳다."* C팔은 전 칸 음성이므로
  "C팔 음성"= 그 프레임 전체다 ⇒ **전 칸** 마스크.
* `gt_void` — RT-A LAB-19 / PREREG §4.4 VG-void: void 칸은 **음성이 아니다**(미지). 칸 단위.

## 사거리 (PREREG §5.2 3단)

    훈련 손실  : 적용
    선택식     : 적용 (손실과 **동일한** 마스크)
    평가       : **미적용** — 이 파일을 평가 코드 경로에서 import 하는 것 자체가 §6-3 위반이다.

## k 봉인 (D91 §9.2 · OPEN-1 해소)

k = 7,000 px, 판정량 = `cue.px_canonical6` (정본 6키 R·Ta·N·T·Sg·V 귀속 프림 픽셀 합).
**본 봉인 이후 k 변경 = 동결 위반**(§6-1). 상수는 아래 `K_CUE_PX` 하나뿐이며 CLI 로 바꿀 수 없다.

세그 부재 프레임(as-built 363)의 단서 존재는 PREREG §5.3 기하 fallback 으로 대체한다 —
매니페스트가 그 판정을 `cue.fallback_present` 에 이미 구워 두었다(A·C=1 / D=0 /
B=(ON·배선 − 그 씬의 B레버)). 본 파일은 그 값을 읽을 뿐 새로 판정하지 않는다.
"""
from __future__ import annotations

# ── 봉인 상수 (D91 §9.2) ────────────────────────────────────────────────────
K_CUE_PX = 7000
K_SEAL = ("k = 7,000 px on cue.px_canonical6 — D91 §9.2 봉인 "
          "(Youden J 0.9451 최대 ∧ D팔 거짓 존재 0의 최소 k ∧ 로그 중점 7,066의 보수 하한). "
          "PREREG §6-1: 본 봉인 이후 k 변경 = 동결 위반.")

CHANNELS = ("b_arm_h", "bare_h_by_k", "lever_n_zero_info_c", "gt_void")

MASK_SCOPE = {
    "b_arm_h": "gt_positive_cells",
    "bare_h_by_k": "gt_positive_cells",
    "lever_n_zero_info_c": "all_cells",
    "gt_void": "void_cells",
}

SPEC_ID = (f"v3_ignore/PREREG§5.2+§5.3 · k={K_CUE_PX} · "
           "b_arm_h→pos, bare_h→pos, lever_n→frame, gt_void→cell")


# ── 채널별 술어 ─────────────────────────────────────────────────────────────
def cue_present(rec: dict) -> tuple[bool, str]:
    """(단서가 프레임에 존재하는가, 판정 근거). PREREG §5.3.

    측정 가능(strict 세그 보유) -> px_canonical6 >= k.
    세그 부재                   -> 매니페스트가 구워둔 기하 fallback(cue.fallback_present).
    """
    c = rec.get("cue") or {}
    px = c.get("px_canonical6")
    if px is not None:
        return (int(px) >= K_CUE_PX), "px_canonical6"
    return bool(c.get("fallback_present")), "geometric_fallback"


def ch_b_arm_h(rec: dict) -> bool:
    """B팔 ∧ tier=='H' (무조건 적용). 매니페스트 사전계산값과 술어를 **둘 다** 보고 발산 시 하드 실패."""
    live = bool(rec.get("arm") == "B" and rec.get("tier") == "H")
    baked = bool((rec.get("ignore") or {}).get("b_arm_h"))
    if live != baked:
        raise AssertionError(f"[VG-mask] b_arm_h 발산 {rec['frame_id']}: live={live} baked={baked}")
    return live


def ch_bare_h(rec: dict) -> bool:
    """tier=='H' ∧ 단서 없음 (k=7,000 봉인). 맨-가림 H."""
    if rec.get("tier") != "H":
        return False
    return not cue_present(rec)[0]


def ch_lever_n(rec: dict) -> bool:
    """레버 ㄴ — C팔 ∧ 영정보 (A,C) 쌍. OPEN-2 무응답 기본값 = 등록 술어가 참인 전량 적용."""
    return bool((rec.get("ignore") or {}).get("lever_n_zero_info_c"))


# ── 칸 단위 마스크 조립 ─────────────────────────────────────────────────────
def frame_ignore(rec: dict, n_cells: int | None = None) -> list[int]:
    """그 프레임의 **칸 단위 무시 마스크** (1 = 손실·선택식에서 제외)."""
    gt = rec["polar_gt"]
    n = n_cells or len(gt)
    void = rec.get("gt_void") or [0] * n
    ign = [0] * n
    pos_scope = ch_b_arm_h(rec) or ch_bare_h(rec)
    frame_scope = ch_lever_n(rec)
    for i in range(n):
        if frame_scope or (pos_scope and int(gt[i]) > 0) or int(void[i]) > 0:
            ign[i] = 1
    return ign


def frame_channels(rec: dict) -> dict:
    """감사용 — 그 프레임에서 어느 채널이 켜졌나."""
    return {"b_arm_h": ch_b_arm_h(rec), "bare_h_by_k": ch_bare_h(rec),
            "lever_n_zero_info_c": ch_lever_n(rec),
            "gt_void": int(sum(rec.get("gt_void") or [])) > 0}


def census(records) -> dict:
    """등록 채널의 as-built 계수 (PREREG §5.2 표와 대조할 숫자)."""
    out = {c: 0 for c in CHANNELS}
    by_arm = {c: {} for c in CHANNELS}
    n_cells_masked = 0
    n_frames_any = 0
    void_cells = 0
    for r in records:
        ch = frame_channels(r)
        hit = False
        for c in CHANNELS:
            if ch[c]:
                out[c] += 1
                by_arm[c][r.get("arm")] = by_arm[c].get(r.get("arm"), 0) + 1
                hit = True
        ig = frame_ignore(r)
        n_cells_masked += sum(ig)
        n_frames_any += bool(sum(ig))
        void_cells += int(sum(r.get("gt_void") or []))
    return {"channels": out, "by_arm": by_arm, "n_frames_any_mask": n_frames_any,
            "n_cells_masked": n_cells_masked, "n_void_cells": void_cells,
            "k_cue_px": K_CUE_PX, "spec_id": SPEC_ID}


def fa_cells_v3(rec: dict, n_cells: int | None = None) -> list[int]:
    """FA 항 모집단 `v3_D_arm_cells` — D팔 칸만 1 (PREREG §5.1 · selection_v3.FA_POPULATIONS)."""
    n = n_cells or len(rec["polar_gt"])
    return [1] * n if rec.get("arm") == "D" else [0] * n


if __name__ == "__main__":
    import json
    import sys
    man = sys.argv[1] if len(sys.argv) > 1 else "dataset_manifest_v3_seg3.json"
    M = json.load(open(man))
    print(json.dumps(census(M["frames"]), ensure_ascii=False, indent=2))
