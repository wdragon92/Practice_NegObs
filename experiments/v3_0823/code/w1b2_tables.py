#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""w1b2_tables.py — W1B2_SEGFILL_REPORT의 측정 표를 기계 산출물에서 그대로 찍어 낸다.

손으로 옮겨 적으면 반드시 어딘가에서 숫자가 어긋난다. 표는
`w1b2_verify.json` · `w1b2_rimpact.json` · `w1b2_fuse_audit.json` ·
`w1b2_configs.json` · `w1b2_segfill.json` · `w1b2_repro_control.json`
에서만 읽는다.

사용:  python3 experiments/v3_0823/code/w1b2_tables.py
"""
import json
import os

REPO = "/home/vislab/Desktop/work_sy/Practice_NegObs"
V3 = os.path.join(REPO, "experiments/v3_0823")
NAME = {"R": "`cue_railing`", "Ta": "`cue_tactile`", "N": "`cue_nosing`",
        "T": "`cue_material_break`", "Sg": "`cue_sign`",
        "V": "`cue_scene_dressing`"}
KEYS = ("R", "Ta", "N", "T", "Sg", "V")
SEED = dict(base=20260819, h=20260820, e=20260820, e2=20260821)
CAM = dict(base="—", h="d[6,12] h[0.25,1.0]", e="d[6,12] h[1.2,1.9]",
           e2="d[4,9] h[0.3,0.9]")


def J(n):
    p = os.path.join(V3, n)
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None


C = J("w1b2_configs.json")
V = J("w1b2_verify.json")
R = J("w1b2_rimpact.json")
RB = J("w1b_rimpact.json")
F = J("w1b2_fuse_audit.json")
S = J("w1b2_segfill.json")
X = J("w1b2_repro_control.json")
sh = lambda xs: ",".join(x.replace("cue_", "") for x in xs) or "—"

# ===================== 웨이브 1 ============================================
if C:
    print("### W1 · B2 레버 지도 (12씬 · T 보충)\n")
    print("| 씬 | 밴드 | 컷 | B 레버 (착지본) | 추가 | **B2 레버** | T 자리 |")
    print("|---|---|---:|---|---|---|---|")
    for r in C["scenes"]:
        print(f"| {r['scene']} | {','.join(r['bands'])} | {r['cuts']} | "
              f"{sh(r['levers_B'])} | **{sh(r['applied'])}** | {sh(r['levers_B2'])} | "
              f"{len(r['t_sites'])} MATL_REBIND |")
    print(f"| **합** | | **{C['n_cuts']}** | | | | |")
    if C.get("held_pending_ruling"):
        print("\n결재 대기(레버에 넣지 않음): " + " · ".join(
            f"`{h['scene']}`·{h['cue'].replace('cue_', '')}"
            for h in C["held_pending_ruling"]))

if V:
    print("\n### W1 · 컷 회계\n")
    print("| 라운드 | 밴드 | 씬 | 컷 | 시드 | 카메라 밴드 | in-process s |")
    print("|---|---|---:|---:|---:|---|---:|")
    for r, v in V["rounds"].items():
        print(f"| `{r}` | {v['band']} | {v['n_scenes']} | **{v['png']}** | "
              f"{SEED[v['band']]} | {CAM[v['band']]} | {v['in_process_sec']} |")
    a = V["accounting"]
    print(f"| **소계** | | | **{a['total_cuts']}** | | | "
          f"**{a['in_process_gpu_h']} GPU-h** |")

    print("\n### W1 · 게이트 배터리\n")
    q = V["vg_01"]
    print("| 게이트 | 결과 |")
    print("|---|---|")
    print(f"| 렌더 회계 | {a['total_cuts']}/{a['planned_cuts']}컷 · "
          f"in-process {a['in_process_gpu_h']} GPU-h |")
    print(f"| **VG-01** (A/B GT 동일 · z_off = D팔) | 프레임 "
          f"**{q['n_frames_gt_equal']}/{q['n_frames']}** `polar_gt` 비트 동일 · "
          f"씬×밴드 {q['n_pass']}/{q['n_pairs']} · 격리 {len(q['quarantine'])} · "
          f"높이맵 바이트 동일 {q['n_hm_bytes_equal']} |")
    d = V["vg_datum"]
    print(f"| VG-datum | 쌍 생존 **{d['pair_survival']}** "
          f"({100 * d['pair_survival_rate']:.1f} %) · 컷 생존 {d['cut_survival']} · "
          f"컷 층 {d['cut_tiers']} · 격리 {len(d['quarantine'])} |")
    t = V["vg_10"]
    print(f"| VG-10 (트윈 정확성) | max pose delta **{t['pose_delta_max']}** m · "
          f"비영 {t['n_pairs_nonzero']} |")
    g = V["vg_08"]
    print(f"| VG-08 · per-cut 세그 판별성 | **{g['n_distinct']}/{g['n_pairs']}** · "
          f"고유 마스크 {g['n_unique_masks']} / 포즈 {g['n_poses']} / 컷 {g['n_cuts']} · "
          f"누락 사이드카 {g['n_missing_sidecars']} · stale 지문 {g['n_stale_signature']} · "
          f"포즈 간 충돌 **{g['n_pose_collisions']}** · fetch {g['fetch_paths']} |")
    lf = V["lever_firing"]
    print(f"| 레버 발화 | {lf.get('n_fired', '—')}/{lf.get('n_pairs', '—')} |")
    ct = V["corpus_tie"]
    print(f"| 코퍼스 이전 | {json.dumps(ct, ensure_ascii=False)[:180]} |")
    if q["quarantine"]:
        print("\n**VG-01 격리**: " + " · ".join(
            f"{x['scene']}/{x['band']} (cells_raw A {x['cells_raw']['A']} / "
            f"B {x['cells_raw']['B']} · polar_gt 불일치 프레임 {x['n_mismatch']})"
            for x in q["quarantine"]))
    if g.get("failures"):
        print("\n**VG-08 실패 (포즈 간 마스크 충돌)**\n")
        print("| 씬 | 밴드 | 마스크/포즈 | 충돌 | fetch |")
        print("|---|---|---:|---:|---|")
        for x in g["failures"]:
            print(f"| {x['scene']} | {x['band']} | {x['n_unique_masks']}/{x['n_poses']} | "
                  f"{x['n_pose_collisions']} | {x['fetch']} |")
    if g.get("over_discriminating"):
        print("\n**마스크 > 포즈 (관찰 · 프림 정규화로 무해)**: " + " · ".join(
            f"{x['scene']}/{x['band']} {x['n_unique_masks']}/{x['n_poses']}"
            for x in g["over_discriminating"]))
    if V.get("problems"):
        print("\n**problems**: " + json.dumps(V["problems"], ensure_ascii=False)[:800])

if R:
    print("\n### W1 · 키별 |r| — B2 착지 후\n")
    P, PB = R["policies"], (RB or {}).get("policies", {})
    print("| 키 | 단서 | 씬 수 | W1-B `PB(격리 반영)` | **W1-B2 `PB(격리 반영)`** | "
          "W1-B2 `PB(as-built)` | 판정 |")
    print("|---|---|---:|---:|---:|---:|---|")
    for k in KEYS:
        g2 = P["PB_gated"][k]
        g1 = PB.get("PB_gated", {}).get(k, {})
        ab = P["PB_asbuilt"][k]
        mark = "✅" if g2["r"] <= R["threshold"] else "❌"
        print(f"| **{k}** | {NAME[k]} | {g2['n_scenes']} | {g1.get('r', '—')} | "
              f"**{g2['r']}** | {ab['r']} | {mark} |")
    over = [k for k in KEYS if P["PB_gated"][k]["r"] > R["threshold"]]
    mx = max(P["PB_gated"][k]["r"] for k in KEYS)
    print(f"\n- 문턱 {R['threshold']} 초과 키: **{over or '없음'}** · 최대 r **{mx}**")
    print("- a/b/c/d (PB_gated): " + " · ".join(
        f"{k} {P['PB_gated'][k]['a']}/{P['PB_gated'][k]['b']}/"
        f"{P['PB_gated'][k]['c']}/{P['PB_gated'][k]['d']}" for k in KEYS))
    pt = P.get("PB_plusT")
    if pt:
        agree = all(pt[k]["r"] == P["PB_gated"][k]["r"] for k in KEYS)
        print(f"- 자기 검산: `PB_plusT`(예측) ≡ `PB_gated`(실측) → "
              f"**{'일치' if agree else '불일치'}** "
              f"(예측 T {pt['T']['r']} vs 실측 {P['PB_gated']['T']['r']})")

if F:
    print("\n### W1 · 계기 정렬 (융합)\n")
    print("| 밴드 | 씬 | 동작 | A 융합 fp | B2 융합 fp | 대칭차 |")
    print("|---|---|---|---|---|---|")
    for r in F["rows"]:
        if not r.get("corpus_on_fused"):
            continue
        rv = r.get("refuse_vs_A") or {}
        print(f"| {r['band']} | {r['scene']} | {r.get('action', '—')} | "
              f"{rv.get('fp_A', '—')} | {rv.get('fp_B', '—')} | "
              f"{rv.get('symdiff', '—')} |")

# ===================== 웨이브 2 ============================================
if X:
    print("\n### W2 · 재현성 대조 실험 (렌더 0 · 이미 있는 라운드만)\n")
    print("| 대조 | 비교 | 씬·컷 | RGB PNG | depth | idseg 원바이트 | "
          "idseg 프림정규화 | heightmap | 포즈Δ |")
    print("|---|---|---|---:|---:|---:|---:|---:|---:|")
    for c in X["controls"]:
        t = c["totals"]
        print(f"| {c['tag']} | `{c['new']}` vs `{c['ref']}` | "
              f"{t['n_scenes']}씬 {t['n']}컷 | **{t['png_eq']}/{t['n']}** | "
              f"**{t['depth_eq']}/{t['n']}** | {t['idseg_eq']}/{t['idseg_primnorm_n']} | "
              f"**{t['idseg_primnorm_eq']}/{t['idseg_primnorm_n']}** | "
              f"{t['heightmap_eq']}/{t['n_scenes']} | {t['pose_max_delta']} |")

if S:
    print("\n### W2 · sha256 동일성 · 설치 (씬 프로세스 34)\n")
    print("| 밴드 | 씬 | 컷 | RGB PNG sha | **depth sha** | hm sha | n_prims | "
          "포즈Δ | 마스크/포즈 | 승계 | 판정 |")
    print("|---|---|---:|---:|---:|:-:|---|---:|---:|---:|---|")
    for r in S["units"]:
        na = r.get("n_a", 0)
        print(f"| {r['band']} | {r['scene']} | {na} | "
              f"{r.get('n_png_identical', 0)}/{na} | "
              f"**{r.get('n_depth_identical', 0)}/{na}** | "
              f"{'=' if r.get('heightmap_sha_equal') else '≠'} | "
              f"{r.get('n_prims', '—')} | {r.get('pose_max_delta', '—')} | "
              f"{r.get('n_unique_masks', 0)}/{r.get('n_poses', 0)} | "
              f"{r.get('n_stale_carryover', 0)} | {r['status']} |")
    print(f"\n- 유닛 **{S['n_units_ok']}/{S['n_units']}** 설치 · 사이드카 "
          f"**{S['n_sidecars_installed']}**")
    print(f"- **기하 대응(설치 판정)** depth sha 동일 "
          f"**{S['n_cuts_depth_identical']}/{S['n_cuts']}** "
          f"({100 * S['geom_identity_rate']:.1f} %)")
    print(f"- 참고 열 RGB PNG sha 동일 {S['n_cuts_png_identical']}/{S['n_cuts']} "
          f"({100 * S['png_identity_rate']:.1f} %)")
    print(f"- 조건 경계 stale 승계 총 {S['stale_carryover_total']}컷 "
          f"(그중 조건 경계 {S['stale_at_cond_boundary_total']}컷)")
    if S["seg_unavailable"]:
        print("\n**seg-unavailable (격리 — 설치하지 않음)**\n")
        print("| 밴드 | 씬 | 상태 | 사유 |")
        print("|---|---|---|---|")
        for u in S["seg_unavailable"]:
            print(f"| {u['band']} | {u['scene']} | `{u['status']}` | "
                  f"{(u.get('why') or '')[:160]} |")
    else:
        print("\n**seg-unavailable: 없음 (34/34 설치)**")
    if S.get("over_discriminating"):
        print("\n마스크 > 포즈(무해 확인): " + " · ".join(
            f"{x['scene']}/{x['band']} {x['n_unique_masks']}/{x['n_poses']}"
            f"({'benign' if x.get('prim_normalized_benign') else 'CHECK'})"
            for x in S["over_discriminating"]))
