#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""w3_extra_gates.py — W3 test-ext 본렌더의 **씬×팔 종합 회계**

`h12_gates.py` 는 **밴드라운드 하나**를 본다. test-ext 의 모집단은 씬당 **두 밴드
라운드의 합**(계획 §3.2 의 팔당 48프레임 = 24 + 24)이므로, ACCOUNTING §3.4 에 올릴
행은 이 스크립트가 두 라운드를 **합산**해서 만든다.

`h12_gates.py` 가 하지 않는 세 가지를 여기서 한다:

  ① **ALL-NEG 을 6씬 전부의 C·D 팔에** 건다. h12_gates 의 `ALLNEG` 은
     `PRIMS[scene]["ncue"]` 인 씬에서만 자동 호출된다. 그러나 PREREG §7.2
     **AC-INSTR-1** 이 등록하는 *"C팔 GT = 사양 상수 = 전 칸 음성"* 은 H·측방 씬의
     C팔에도 걸리는 주장이고, D팔(`hazard OFF · cue 전부 OFF`)도 마찬가지다.
     역쌍 라벨 (C,A)·(D,B) 를 `gate_allneg` 에 그대로 먹인다 — 계기를 새로 짜지 않고
     **같은 함수**를 쓴다.

  ② **(C,D) 광학차를 6씬 전부**에. h12_gates 의 `VG-07-CD` 도 ncue 전용이다.
     계기판 ③(단서만의 용량-반응)의 대조축이 (C,D) 이므로 H·측방 씬에서도 필요하다.

  ③ **밴드 합산 회계** — 씬×팔 컷 수, tier 분포, paired-H(밴드별·합계), 측방 섹터,
     그리고 ACCOUNTING §3.4 행 2·3·4 의 **제안값**.

정본 계기(h12_gates.py)는 한 줄도 고치지 않는다 — import 해서 쓴다.
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import h12_gates as G                                    # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
ANN = os.path.join(REPO, "experiments", "v3_0823", "annotations")

# 밴드라운드 → (스탬프, 씬 목록, 밴드 이름)
ROUNDS = [
    ("base", "260824_v3w3_extbase",
     ["sceneH1", "sceneH2", "sceneH3", "sceneL1", "sceneN9", "sceneN11"], "base"),
    ("h",    "260824_v3w3_exth",   ["sceneH1", "sceneH2", "sceneH3"], "H"),
    ("lat",  "260824_v3w3_extlat", ["sceneL1"], "LAT"),
    ("b2",   "260824_v3w3_extb2",  ["sceneN9", "sceneN11"], "base2"),
]

SCENES = ["sceneH1", "sceneH2", "sceneH3", "sceneL1", "sceneN9", "sceneN11"]
LONG = {
    "sceneH1": "sceneH1_berm_levee", "sceneH2": "sceneH2_landing_campus",
    "sceneH3": "sceneH3_bend_walk", "sceneL1": "sceneL1_lateral_canal",
    "sceneN9": "sceneN9_busstop_tactile", "sceneN11": "sceneN11_ground_pattern",
}
# 계획 §3.2 의 paired-H 기대 하한. 측방·N-cue 는 "—" (낙차 은닉 씬이 아니다).
PAIRED_H_FLOOR = {"sceneH1": 12, "sceneH2": 12, "sceneH3": 12}
PREREG_FLOOR = 10          # PREREG_CUEOFF.md:215 씬당 사전등록 하한

# B안 대기 — 씬 파일이 아직 없다(계획 §3.2 의 9씬 중 3씬).
PENDING_B = [
    ("sceneH4_berm_farm", "paired-H 둔덕형 · 농로", "base, H", "B"),
    ("sceneL2_lateral_ditch", "측방 · 농로", "base, LAT", "C"),
    ("sceneN12_weak_stack", "N-cue ★5 · 보도", "base, base2", "B"),
]


def labels(tag, pair):
    return os.path.join(ANN, f"w3_{tag}_{pair}_labels.json")


def pose_of(fn):
    """`L0__s20260823__0000.png` → 포즈 인덱스 `0000`.

    **왜 포즈를 따로 세나.** 한 밴드 draw 의 24컷 = 8포즈 × 3조건이고, 세 조건은
    같은 시드·같은 카메라 인덱스를 쓰므로 **포즈가 동일**하다(러너 주석·
    SCENE_TEXT_BUILD §9.3 실측). 즉 24컷의 기하학적 독립 표본은 **8**이다.
    계획 §3.2 의 하한(≥12)은 *"H 밴드 24컷 × 수율 0.5"* 로 **컷 단위**에 걸려 있으므로
    판정은 컷으로 하되, 포즈 수를 **함께** 인쇄한다 — 컷 단위 수치만 보면 조건 3종이
    표본을 3배로 부풀린 것처럼 읽히기 때문이다.
    """
    base = fn.rsplit("/", 1)[-1]
    stem = base.split(".")[0]
    return stem.rsplit("__", 1)[-1]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="dataset")
    ap.add_argument("--split", default="test")
    ap.add_argument("--out", default="")
    a = ap.parse_args(argv)

    root = a.root if os.path.isabs(a.root) else os.path.join(REPO, a.root)

    # ── 라운드별 tier 적재 ────────────────────────────────────────────────
    T = {}                       # T[tag][arm][scene][file] = tier row
    for tag, stamp, scs, band in ROUNDS:
        T[tag] = dict(
            A=G.load_tiers(labels(tag, "ac"), "on"),
            B=G.load_tiers(labels(tag, "bd"), "on"),
            C=G.load_tiers(labels(tag, "ca"), "on"),
            D=G.load_tiers(labels(tag, "db"), "on"),
        )

    rep = dict(doc="w3_extra_gates", rounds=[r[1] for r in ROUNDS],
               scenes={}, totals={}, pending_b=PENDING_B)

    print("=" * 90)
    print("W3 test-ext 본렌더 — 씬 × 팔 종합 회계 (밴드 합산)")
    print("=" * 90)

    tot_cuts = collections.Counter()
    tot_paired = 0
    tot_paired_hband = 0

    for sc in SCENES:
        srow = dict(scene=sc, long=LONG[sc], bands={}, arms={})
        my = [(tag, stamp, band) for tag, stamp, scs, band in ROUNDS if sc in scs]

        # ① ALL-NEG — 네 팔 전부, 라운드별로 잰 뒤 합산
        allneg = {}
        for arm in ("A", "B", "C", "D"):
            rows_n = 0
            gtpos = prepos = 0
            craw, mx, tiers_ct = set(), [], collections.Counter()
            for tag, stamp, band in my:
                tt = T[tag][arm].get(sc, {})
                if not tt:
                    continue
                r = G.gate_allneg(tt, arm)
                rows_n += r["n_frames"]
                gtpos += r["n_frames_gt_positive"]
                prepos += r["n_frames_pregate_positive"]
                craw |= set(r["cells_raw"])
                if r["max_diff"]:
                    mx.append(r["max_diff"]["max"])
                for k, v in r["tiers"].items():
                    tiers_ct[k] += v
            allneg[arm] = dict(n_frames=rows_n, n_gt_positive=gtpos,
                               n_pregate_positive=prepos,
                               cells_raw=sorted(craw),
                               max_diff_max=(max(mx) if mx else None),
                               tiers=dict(tiers_ct),
                               all_negative=(gtpos == 0 and prepos == 0
                                             and set(craw) <= {0}))
            tot_cuts[arm] += rows_n
        srow["ALLNEG"] = allneg

        # ② (C,D) 광학차 — 라운드별
        cd = {}
        ac = {}
        for tag, stamp, band in my:
            dC = G.arm_dir(root, stamp, "C", a.split, sc)
            dD = G.arm_dir(root, stamp, "D", a.split, sc)
            dA = G.arm_dir(root, stamp, "A", a.split, sc)
            varA = G.load_variation(dA)
            if not varA:
                continue
            files = sorted({c["file"] for c in G.cuts_of(varA)})
            g = G.gate_vg07(dC, dD, files)
            g.pop("pairs", None)
            cd[band] = g
            g2 = G.gate_vg07(dA, dC, files)
            g2.pop("pairs", None)
            ac[band] = g2
        srow["OPT_AC"] = ac
        srow["OPT_CD"] = cd

        # ③ 밴드별 tier · paired-H
        ph_total = ph_hband = 0
        ph_poses = ph_poses_h = 0
        for tag, stamp, band in my:
            ta = T[tag]["A"].get(sc, {})
            tb = T[tag]["B"].get(sc, {})
            h_a = {f for f, v in ta.items() if v["tier_strict"] == "H"}
            h_b = {f for f, v in tb.items() if v["tier_strict"] == "H"}
            paired = sorted(h_a & h_b)
            n_pose = len({pose_of(f) for f in paired})
            srow["bands"][band] = dict(
                stamp=stamp, n_frames_A=len(ta), n_frames_B=len(tb),
                n_poses_A=len({pose_of(f) for f in ta}),
                strict_H_A=len(h_a), strict_H_B=len(h_b), paired_H=len(paired),
                paired_H_poses=n_pose,
                yield_A=(round(len(h_a) / len(ta), 4) if ta else None),
                tier_A=dict(collections.Counter(
                    v["tier_strict"] for v in ta.values())),
                tier_B=dict(collections.Counter(
                    v["tier_strict"] for v in tb.values())),
                tier_C=dict(collections.Counter(
                    v["tier_strict"] for v in T[tag]["C"].get(sc, {}).values())),
                tier_D=dict(collections.Counter(
                    v["tier_strict"] for v in T[tag]["D"].get(sc, {}).values())),
            )
            ph_total += len(paired)
            ph_poses += n_pose
            if band in ("H",):
                ph_hband += len(paired)
                ph_poses_h += n_pose
        srow["paired_H_total"] = ph_total
        srow["paired_H_Hband"] = ph_hband
        srow["paired_H_poses"] = ph_poses
        srow["paired_H_poses_Hband"] = ph_poses_h
        srow["paired_H_floor_plan"] = PAIRED_H_FLOOR.get(sc)
        srow["paired_H_floor_prereg"] = PREREG_FLOOR if sc in PAIRED_H_FLOOR else None
        tot_paired += ph_total
        tot_paired_hband += ph_hband

        # ④ 측방 섹터 (production 규모 = 두 라운드 합)
        if G.PRIMS.get(sc, {}).get("lateral"):
            merged_a, merged_cuts = {}, []
            for tag, stamp, band in my:
                ta = T[tag]["A"].get(sc, {})
                dA = G.arm_dir(root, stamp, "A", a.split, sc)
                varA = G.load_variation(dA)
                if not varA:
                    continue
                # 파일명이 라운드 간 겹치므로 밴드 접두사로 구분한다
                for f, v in ta.items():
                    merged_a[f"{band}/{f}"] = v
                for c in G.cuts_of(varA):
                    c2 = dict(c)
                    c2["file"] = f"{band}/{c['file']}"
                    merged_cuts.append(c2)
            srow["SECTOR_A_merged"] = G.gate_sectors(merged_a, merged_cuts)

        rep["scenes"][sc] = srow

        # ── 인쇄 ──────────────────────────────────────────────────────────
        print("-" * 90)
        print(f"[{LONG[sc]}]")
        for band, b in srow["bands"].items():
            print(f"  밴드 {band:<6s} {b['stamp']} · A {b['n_frames_A']}컷"
                  f"({b['n_poses_A']}포즈) · "
                  f"strict-H A {b['strict_H_A']} / B {b['strict_H_B']} · "
                  f"**paired-H {b['paired_H']}컷 = {b['paired_H_poses']}포즈** · "
                  f"수율_A {b['yield_A']}")
            print(f"        tier A {b['tier_A']} · B {b['tier_B']}")
            print(f"        tier C {b['tier_C']} · D {b['tier_D']}")
        fl = srow["paired_H_floor_plan"]
        print(f"  ⇒ paired-H 합계 **{ph_total}컷 = {ph_poses}포즈** "
              f"(H밴드분 {ph_hband}컷 = {ph_poses_h}포즈)"
              + (f" · 계획 §3.2 기대 ≥{fl} · 사전등록 하한 ≥{PREREG_FLOOR} → "
                 + ("통과" if ph_total >= fl else "**미달**") if fl else
                 " · (은닉 씬 아님 — 하한 없음)"))
        for arm in ("A", "B", "C", "D"):
            r = allneg[arm]
            print(f"  ALL-NEG {arm}팔 : n={r['n_frames']} · GT 양성 프레임 "
                  f"{r['n_gt_positive']} · pre-gate 양성 {r['n_pregate_positive']} · "
                  f"cells_raw {r['cells_raw']} · max_diff≤{r['max_diff_max']} · "
                  f"tier {r['tiers']}"
                  + ("  → 전음성" if r["all_negative"] else "  → **양성 있음**"))
        for band in cd:
            g, g2 = cd[band], ac.get(band, {})
            if g.get("ok"):
                print(f"  광학차 {band:<6s} (A,C) mean|ΔI| p50 "
                      f"{g2.get('mean_abs',{}).get('p50')} · 영정보 "
                      f"{g2.get('n_zero_info')}/{g2.get('n_pairs')}  ||  "
                      f"(C,D) p50 {g['mean_abs']['p50']} · 영정보 "
                      f"{g['n_zero_info']}/{g['n_pairs']}")
        s = srow.get("SECTOR_A_merged")
        if s and s.get("n_frames"):
            print(f"  섹터(합산 n={s['n_frames']}) 프레임당 양성셀 "
                  f"{s['cells_per_frame']}/20 · none_in_fov {s['none_in_fov']}")
            print("    양성률 " + " · ".join(
                f"{k} {v:.3f}" for k, v in s["pos_rate"].items()))
            print(f"    **측방 A+E {s['lateral_share']:.3f}** vs 중간 B+D "
                  f"{s['mid_share']:.3f} vs 정면 C {s['center_share']:.3f} → "
                  + ("통과" if s["ok"] else "**미달**"))

    rep["totals"] = dict(cuts_by_arm=dict(tot_cuts),
                         cuts_total=sum(tot_cuts.values()),
                         paired_H_total=tot_paired,
                         paired_H_Hband=tot_paired_hband)

    print("=" * 90)
    print("모집단 회계 — ACCOUNTING §3.4 제안행 (PROPOSE · 적용 금지, PREREG PENDING 2-4)")
    print("=" * 90)
    print(f"  행 2 · test-ext 씬 목록·프레임·4팔 분해")
    print(f"        as-built **6씬** · "
          f"**{sum(tot_cuts.values())}프레임** · A/B/C/D 각 "
          + " / ".join(f"{tot_cuts[x]}" for x in "ABCD"))
    print(f"        계획 §3.2 원문 = 9씬 · 1,728 · 각 432. "
          f"차이 = B안 대기 3씬 × 192 = **576프레임 미렌더**")
    print(f"  행 3 · test-ext paired-H (씬별)")
    for sc in SCENES:
        r = rep["scenes"][sc]
        fl = r["paired_H_floor_plan"]
        print(f"        {LONG[sc]:<26s} {r['paired_H_total']:>3d}컷 / "
              f"{r['paired_H_poses']:>2d}포즈"
              + (f"  (H밴드 {r['paired_H_Hband']}컷) 하한 {fl}" if fl else "  (—)"))
    print(f"        합계 **{tot_paired}컷** (H밴드분 {tot_paired_hband}컷) · "
          f"계획 §3.2 test-ext 합계 하한 ≥48(9씬) / as-built 3H씬 기대 ≥36")
    print(f"  행 4 · FA_C / FA_D 분모 (무위험 프레임 수, 팔별)")
    for arm in ("C", "D"):
        n = tot_cuts[arm]
        pos = sum(rep["scenes"][s]["ALLNEG"][arm]["n_gt_positive"] for s in SCENES)
        print(f"        FA_{arm} 분모 = {n} - 양성 {pos} = **{n - pos}** "
              f"(void 버킷 격리는 VG-void 결과와 함께 §6.4 규약 적용)")
    print()
    print("  B안 대기 잔여 (씬 파일 부재 — 미렌더)")
    for name, fam, bands, wv in PENDING_B:
        print(f"        {name:<26s} {fam:<22s} 밴드 {bands:<14s} 계획 Wave {wv} · "
              f"4팔 × 48 = 192컷")
    print(f"        소계 **3씬 · 576컷** (= 계획 1,728 − as-built 1,152)")

    if a.out:
        json.dump(rep, open(a.out, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        print(f"\n[out] {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
