#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""h67_probe.py — sceneH6 / sceneH7 의 스모크 · H밴드 프로브 렌더 드라이버 (P-5)

왜 이 파일이 필요한가
---------------------
정본 드라이버 `scripts/run_data_render.py` 의 부모 절반(`drive()`)은 씬 목록을
`variation_kit.AZ_LEDGER`(33씬)에서 가져오고, 자식 절반(`scene_proc()`)은
`vk.ledger(scene)` · `vk.split_of(scene)` 를 부른다. 신설 씬은 아직 그 원장에 없다.

원장에 두 줄을 넣는 것은 **정본 kit 수정**이고, 더 나쁜 것은 `split_map()` 이
`sorted(AZ_LEDGER)` 를 시드 셔플하므로 **씬 하나만 추가해도 기존 33씬의 디렉터리
분할이 전부 재배치된다**는 점이다. 그래서 이 프로브는 원장을 **런타임에만** 확장한다:

  1. 먼저 `vk.split_map(0)` 을 호출해 **기존 33씬의 분할을 캐시에 확정**시키고,
  2. 그 캐시에 sceneH6/H7 을 `val` 로 **핀**한 뒤(계획 §2.1 배정),
  3. `AZ_LEDGER` 에 두 행을 넣는다.
  ⇒ 기존 씬의 `split_of()` 반환은 **비트 동일**하게 유지된다(아래 `_assert_split_frozen`).

그리고 `run_data_render.scene_proc()` 를 **같은 프로세스 안에서** 직접 부른다
(CUE_COVERAGE §4-4 (6): *"신설 씬을 정본 라이브러리에 넣기 전까지는 이 경로가 유일하다"*).
부모 `drive()` 가 자식을 새 인터프리터로 띄우면 런타임 패치가 전달되지 않기 때문이다.

정본 파일은 **한 바이트도 고치지 않는다.**

사용
----
    python3 experiments/v3_0823/code/h67_probe.py \
        --scene sceneH6 --run 260823_v3p5_h67smoke_A --conds L0 --cams 1 \
        --seed 20260823 --config '{"hazard_stairs": true}'

환경변수는 호출자(셸)가 세팅한다 — `NEGOBS_DATA_SIDECARS=1 NEGOBS_SEG_SIDECAR=1` 등.
이 스크립트는 `drive()` 가 자식에게 넘기던 렌더 팔 변수만 스스로 채운다.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "scripts"))

# 신설 씬 원장 행. `daz_data` 는 C' 등급(기준 B 미발화)의 표준값을 그대로 쓴다 —
#   두 씬 다 옥외 주광 씬이고 방위 스윕 제약을 낼 구조(협곡 골목·무일광)가 아니다.
NEW_SCENES = {
    "sceneH6": dict(split="val", cls="C'",
                    basis="v3 P-5 신설 (RENDER_PLAN_V3 §2.1 sceneH6_berm_levee2). "
                          "SP-2 스윕 미실시 — C' 기본값 승계, 방위 제약 미측정"),
    "sceneH7": dict(split="val", cls="C'",
                    basis="v3 P-5 신설 (RENDER_PLAN_V3 §2.1 sceneH7_bend_walk2). "
                          "SP-2 스윕 미실시 — C' 기본값 승계, 방위 제약 미측정"),
    # ── W3 test-ext (2차 빌더 런) ─────────────────────────────────────────────
    #   `split="test"` 는 **디렉터리 배치**일 뿐이고, test-core 7씬과 섞이지 않는다
    #   (씬 키가 다르다). test-ext 의 무대 순도(§12-9)는 훈련 매니페스트가 이 씬 키를
    #   포함하지 않는 것으로 강제되며, 그 강제는 W3 매니페스트 빌더 소관이다.
    "sceneH1": dict(split="test", cls="C'",
                    basis="v3 P-5 신설 (RENDER_PLAN_V3 §2.1 sceneH1_berm_levee, test-ext). "
                          "SP-2 스윕 미실시 — C' 기본값 승계, 방위 제약 미측정"),
    "sceneH2": dict(split="test", cls="C'",
                    basis="v3 P-5 신설 (RENDER_PLAN_V3 §2.1 sceneH2_landing_campus, "
                          "test-ext). SP-2 스윕 미실시 — C' 기본값 승계, 방위 제약 미측정"),
    # ── W3 test-ext (3차 빌더 런) — A안 순서의 다음 두 씬 ─────────────────────
    #   §8 결재 1 A안 = H1·H2·H3 · H6·H7 · L1 · N9·N11. H6/H7(1차) · H1/H2(2차)가
    #   착지했으므로 이 런은 **H3(복도 굴절형 test-ext) + L1(측방 test-ext)** 이다.
    "sceneH3": dict(split="test", cls="C'",
                    basis="v3 P-5 신설 (RENDER_PLAN_V3 §2.1 sceneH3_bend_walk, "
                          "test-ext). SP-2 스윕 미실시 — C' 기본값 승계, 방위 제약 미측정"),
    "sceneL1": dict(split="test", cls="C'",
                    basis="v3 P-5 신설 (RENDER_PLAN_V3 §2.3 sceneL1_lateral_canal, "
                          "측방 test-ext). SP-2 스윕 미실시 — C' 기본값 승계, "
                          "방위 제약 미측정"),
}

SCENE_FILE = {
    "sceneH6": os.path.join(REPO, "scenes", "main", "sceneH6_berm_levee2.py"),
    "sceneH7": os.path.join(REPO, "scenes", "main", "sceneH7_bend_walk2.py"),
    "sceneH1": os.path.join(REPO, "scenes", "main", "sceneH1_berm_levee.py"),
    "sceneH2": os.path.join(REPO, "scenes", "main", "sceneH2_landing_campus.py"),
    "sceneH3": os.path.join(REPO, "scenes", "main", "sceneH3_bend_walk.py"),
    "sceneL1": os.path.join(REPO, "scenes", "main", "sceneL1_lateral_canal.py"),
}


def register(vk):
    """기존 33씬의 분할을 얼린 뒤 신설 2씬을 원장에 넣는다."""
    before = dict(vk.split_map(0))          # 캐시 확정 (`_SPLIT_CACHE[0]`)
    for name, row in NEW_SCENES.items():
        if name in vk.AZ_LEDGER:
            continue
        vk.AZ_LEDGER[name] = vk._ledger_row(
            name, row["cls"], vk.DAZ_SAMPLER_MAX, False, row["basis"])
        vk._SPLIT_CACHE[0][name] = row["split"]
    after = vk.split_map(0)
    moved = [s for s in before if before[s] != after.get(s)]
    if moved:
        raise SystemExit(f"[h67_probe] 기존 씬 분할이 움직였다: {moved}")
    print(f"[h67_probe] 원장 확장 {len(NEW_SCENES)}씬 · 기존 {len(before)}씬 분할 "
          f"불변 확인 · 신설 분할 "
          + " ".join(f"{k}={after[k]}" for k in NEW_SCENES))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--scene", required=True, choices=sorted(SCENE_FILE))
    ap.add_argument("--run", required=True)
    ap.add_argument("--conds", default="L0")
    ap.add_argument("--cams", type=int, default=1)
    ap.add_argument("--seed", type=int, default=20260823)
    ap.add_argument("--config", default="{}",
                    help="NEGOBS_SCENE_CONFIG JSON")
    ap.add_argument("--band", default="",
                    help="NEGOBS_CAM_BAND_OVERRIDE JSON (빈 문자열이면 미설정)")
    ap.add_argument("--seg-strict", action="store_true",
                    help="ID 마스크 페치에서 t0/t1/t4 단을 건너뛰고 곧장 orchestrator "
                         "step 으로 간다 (아래 결함 주석 참조)")
    a = ap.parse_args(argv)

    # 라운드명 가드 (VG-12) — 이 스크립트가 쓸 수 있는 스탬프만 허용한다.
    allowed = ("260823_v3p5_h67smoke_A", "260823_v3p5_h67smoke_C",
               "260823_v3p5_h67probe_A", "260823_v3p5_h67probe_C",
               "260823_v3p5_h67rev_A", "260823_v3p5_h67rev_C",
               # ── W3 test-ext 2차 빌더 런 (sceneH1 · sceneH2) ──────────────
               #   4팔 완비가 test-ext 의무이므로 B·D 스탬프도 허용목록에 있다(§3.1).
               "260823_v3p5_h12smoke_A",
               "260823_v3p5_h12probe_A", "260823_v3p5_h12probe_B",
               "260823_v3p5_h12probe_C", "260823_v3p5_h12probe_D",
               "260823_v3p5_h12rev_A", "260823_v3p5_h12rev_B",
               "260823_v3p5_h12rev_C", "260823_v3p5_h12rev_D",
               # 근거리 비-H 대조 라운드 (퇴화 아님을 실렌더로 확인)
               "260823_v3p5_h12near_A", "260823_v3p5_h12near_C",
               # ── W3 test-ext 3차 빌더 런 (sceneH3 · sceneL1) ───────────────
               #   4팔 완비가 test-ext 의무이므로 B·D 스탬프도 허용목록에 있다(§3.1).
               "260823_v3p5_h3l1smoke_A",
               "260823_v3p5_h3l1probe_A", "260823_v3p5_h3l1probe_B",
               "260823_v3p5_h3l1probe_C", "260823_v3p5_h3l1probe_D",
               "260823_v3p5_h3l1rev_A", "260823_v3p5_h3l1rev_B",
               "260823_v3p5_h3l1rev_C", "260823_v3p5_h3l1rev_D",
               "260823_v3p5_h3l1near_A", "260823_v3p5_h3l1near_C")
    if a.run not in allowed:
        raise SystemExit(f"[h67_probe] 라운드 스탬프 {a.run!r} 거부 — 허용 {allowed}")

    import variation_kit as vk
    register(vk)

    import run_data_render as rdr
    rdr.ALL_SCENES = sorted(vk.AZ_LEDGER)

    if a.seg_strict:
        # ── ID 마스크 stale-frame 결함 우회 (프로브 로컬. 정본 드라이버 무수정) ──────
        # 실측 [260823_v3p5_h67probe_A]: 씬당 8컷을 찍었는데 `.idseg.npz` **8개가 바이트
        #   동일**했다(blake2b 47a05438f412 ×8 / 1b18fb37a803 ×8). 같은 라운드의
        #   `.depth.npy` 는 컷마다 다르다 — 즉 깊이는 갱신되고 **ID 마스크만 첫 컷에
        #   고정**된다.
        # 원인: `_seg_fetch` 의 사다리 첫 단 `t0`(추가 tick 0회)가 `instance_id_
        #   segmentation` 애노테이터를 **다시 평가시키지 않는다**. shape 이 맞고
        #   `max()>0` 이므로 사다리는 성공으로 보고 다음 단으로 올라가지 않는다.
        #   `sim_app.update()` 만으로는 이 애노테이터가 갱신되지 않고 Replicator
        #   orchestrator step 이 필요하다(depth 는 `"orch"` 가 필요했다고 §6.3 이 이미
        #   적어 두었다 — 세그만 t0 로 끝난 것이 오히려 신호였다).
        # 왜 P-5 스모크가 못 잡았나: 그 스모크는 **1컷**이었다. 1컷 라운드에서는
        #   stale 과 fresh 가 구별되지 않는다.
        # 파급: VG-06(모서리 소속)과 DZ §12-5 의 단서 임계 k 는 **컷별** 마스크를
        #   요구한다. 이 결함이 남으면 두 게이트가 조용히 첫 컷 하나만 검사하게 된다.
        _orig = rdr._seg_fetch

        def _seg_fetch_strict(ann, sim_app, subframes):
            import numpy as np
            try:
                import omni.replicator.core as rep
                rep.orchestrator.step(rt_subframes=int(subframes))
            except Exception as e:
                print(f"[seg-strict] orchestrator.step 실패: {e}", flush=True)
                return _orig(ann, sim_app, subframes)
            try:
                raw = ann.get_data()
            except Exception as e:
                print(f"[seg-strict] get_data 실패: {e}", flush=True)
                return None, None, "fail"
            info = None
            if isinstance(raw, dict):
                info = raw.get("info") or {}
                raw = raw.get("data")
            arr = np.asarray(raw)
            if arr.ndim == 3:
                arr = arr[..., 0]
            if arr.shape != (vk.RES_H, vk.RES_W) or int(arr.max()) <= 0:
                return None, None, "empty"
            id2l = (info or {}).get("idToLabels") or (info or {}).get("idToPrims")
            return arr, id2l, "orch_forced"

        rdr._seg_fetch = _seg_fetch_strict
        print("[h67_probe] seg-strict ON — ID 마스크를 컷마다 orchestrator step 으로 갱신")

    # `drive()` 가 자식에게 넘기던 팔 변수. 여기서는 자식이 곧 이 프로세스다.
    os.environ.update(
        NEGOBS_RENDER_ROLE="data",
        NEGOBS_SEED=str(a.seed),
        NEGOBS_LIGHT_COND=a.conds,
        NEGOBS_CAM_MODE="random",
        NEGOBS_CAM_N=str(a.cams),
        NEGOBS_CAPTURE="1", NEGOBS_CAPTURE_MODE="pt",
        NEGOBS_PT_FAST="1", NEGOBS_LOOK_V1="1",
        PYTHONUNBUFFERED="1",
        NEGOBS_SCENE_CONFIG=a.config,
    )
    if a.band:
        os.environ["NEGOBS_CAM_BAND_OVERRIDE"] = a.band
    else:
        os.environ.pop("NEGOBS_CAM_BAND_OVERRIDE", None)

    conds = [c for c in a.conds.split(",") if c]
    made = rdr.prepare_assets(conds)
    if made:
        print(f"[h67_probe] assets {made}")

    root = vk.data_root(a.run)
    out_dir = os.path.join(root, vk.split_of(a.scene), a.scene)
    os.makedirs(out_dir, exist_ok=True)
    print(f"[h67_probe] {a.scene} → {out_dir}\n"
          f"            conds={a.conds} cams={a.cams} seed={a.seed}\n"
          f"            config={a.config}\n"
          f"            band={a.band or '(기본 CAM_DIST)'}")
    rc = rdr.scene_proc(SCENE_FILE[a.scene], a.scene, out_dir, a.conds,
                        a.cams, a.seed)
    return rc or 0


if __name__ == "__main__":
    sys.exit(main())
