#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""w1c_tables.py — W1C_REPORT 의 측정 표를 **기계 산출물에서 직접 찍는다**.

W1-B 의 `w1b_tables.py` 와 같은 규율: 보고서의 숫자를 손으로 옮겨 적지 않는다.
읽는 것만 하고 아무것도 쓰지 않는다(stdout 전용).

  python3 experiments/v3_0823/code/w1c_tables.py            # 전 표
  python3 experiments/v3_0823/code/w1c_tables.py --only hashgate
"""
import argparse
import json
import os

V3 = "/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/v3_0823"


def load(name):
    p = os.path.join(V3, name)
    if not os.path.exists(p):
        return None
    return json.load(open(p, encoding="utf-8"))


def t_hashgate():
    d = load("w1c_hashgate.json")
    print("\n#### 표 A — `keep_dressing` 이식 15건 해시게이트 (D82 ② 증명 조건)\n")
    if not d:
        print("_(w1c_hashgate.json 없음)_"); return
    print(f"기준: {d['criterion']}")
    print(f"BEFORE = `{d['before_run']}` (이식 이전 코드의 출하물) · "
          f"AFTER = `{d['after_run']}` (이식 후 · 기본 설정 1컷)\n")
    print("| # | 씬 | heightmap sha256 (before → after) | n_prims | depth sha256 | 포즈 Δmax | 판정 |")
    print("|---:|---|---|---:|---|---:|---|")
    for i, r in enumerate(d["rows"], 1):
        if r["verdict"] == "MISSING":
            print(f"| {i} | `{r['scene']}` | — | — | — | — | **MISSING** {r.get('why','')} |")
            continue
        hm = (f"`{r['hm_sha_before']}` → `{r['hm_sha_after']}`"
              + (" ✅" if r["hm_equal"] else " ❌"))
        npm = (f"{r['n_prims_before']} → {r['n_prims_after']}"
               + (" ✅" if r["n_prims_equal"] else " ❌"))
        dp = (f"`{r['depth_sha_before']}` → `{r['depth_sha_after']}`"
              + (" ✅" if r["depth_equal"] else (" ⚠️면제" if r["depth_exempt"] else " ❌")))
        pd = ("%.0e" % r["pose_delta_max"]) if r["pose_delta_max"] is not None else "n/a"
        pd = "0" if r.get("pose_equal") else pd
        v = "✅ PASS" if r["verdict"] == "PASS" else f"❌ FAIL — {r.get('why','')}"
        print(f"| {i} | `{r['scene']}` | {hm} | {npm} | {dp} | {pd} | {v} |")
    print(f"\n**{d['n_pass']}/{d['n_scenes']} PASS.**")
    for k, v in (d.get("depth_exempt") or {}).items():
        print(f"- `{k}` depth sha 면제 — {v}")


def t_accounting():
    d = load("w1c_verify.json")
    print("\n#### 표 B — W1-C 렌더 회계\n")
    if not d:
        print("_(w1c_verify.json 없음)_"); return
    a = d["accounting"]
    print(f"| 항목 | 값 |\n|---|---:|")
    print(f"| 유닛 ((라운드, 씬)) | {a['n_units']} |")
    print(f"| 컷 | **{a['n_cuts']}** |")
    print(f"| ok 컷 | {a['n_ok']} |")
    print(f"| `.idseg.npz` | {a['n_idseg']} |")
    print(f"| `.idseg.STALE` 마커 (REPAIR-1 잔존) | **{a['n_stale_markers']}** |")
    print(f"| 재페치 발생 컷 (REPAIR-1) | {a['n_idseg_retry']} |")
    print(f"| in-process GPU-h | {a.get('gpu_hours')} |")
    print(f"| s/컷 중앙값 | {a.get('sec_per_cut_med')} |")
    print("\n| 밴드 | 라운드 | 유닛 | 컷 |")
    print("|---|---|---:|---:|")
    per = {}
    for r in d["rows"]:
        if "error" in r:
            continue
        k = (r["band"], r["c_round"])
        per.setdefault(k, [0, 0])
        per[k][0] += 1
        per[k][1] += r.get("n_cuts", 0)
    for (b, rn), (u, c) in sorted(per.items()):
        print(f"| {b} | `{rn}` | {u} | {c} |")
    print("\n**이식이 들었는가 — 프림 수로 본 A / C / D** "
          "(C ≤ D 이면 그 씬의 C 는 구off 이고 (A,C) 반사실이 무효다)\n")
    print("| 밴드 | 씬 | A | **C** | D | C − D |")
    print("|---|---|---:|---:|---:|---:|")
    for r in d["rows"]:
        if "error" in r or r.get("n_prims_C") is None:
            continue
        na, nc, nd = r.get("n_prims_A"), r.get("n_prims_C"), r.get("n_prims_D")
        gap = (nc - nd) if (nc is not None and nd is not None) else None
        mark = "" if (gap is None or gap > 0) else " ❌"
        print(f"| {r['band']} | `{r['scene']}` | {na} | **{nc}** | {nd} | "
              f"{gap}{mark} |")


def t_vg01ac():
    d = load("w1c_verify.json")
    print("\n#### 표 C — VG-01-AC ((A,C) 3층 · `AC-INSTR-1` C3-7)\n")
    if not d:
        print("_(w1c_verify.json 없음)_"); return
    print(f"계수 영역(as-built): {d['vg01_ac_counting_domain']}\n")
    print("| 밴드 | 씬 | 계기 A/C | fp_corpus | fp_AC | 불일치 | 여분 | 재현율 | 발자국밖 셀차 | max\\|Δz\\| | 층 |")
    print("|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|")
    for r in d["rows"]:
        g = r.get("vg01_ac") or {}
        if g.get("tier") in (None, "no_reference"):
            print(f"| {r['band']} | `{r['scene']}` | — | — | — | — | — | — | — | — | "
                  f"{g.get('tier', 'n/a')} |")
            continue
        inst = r.get("hm_instrument") or {}
        print(f"| {r['band']} | `{r['scene']}` | {inst.get('A')}/{inst.get('C')} | "
              f"{g['fp_corpus_cells']} | {g['fp_AC_cells']} | **{g['mismatch_cells']}** | "
              f"{g['extra_cells']} | {g.get('reproduction')} | {g['offprint_diff_cells']} | "
              f"{g['offprint_max_abs_dz']} | {g['tier']} |")
    v = d["vg01_ac_summary"]
    print(f"\n층 분포 **{v['tiers']}** · **계기판① 제외 쌍 {v['dashboard1_excluded_pairs']}**"
          f" — {v['excluded'] or '없음'}")
    if v.get("instrument_mismatch_pairs"):
        print(f"\n**계기 불일치(C3-1 위반) {v['instrument_mismatch_pairs']}쌍** — "
              f"{v['instrument_mismatch']} · 이 행들의 셀 수치는 판정에 쓰지 않는다")
    print(f"\n> {v['rule']}")


def _datum_block(fn, title):
    d = load(fn)
    print(f"\n{title}\n")
    if not d:
        print(f"_({fn} 없음)_"); return
    cs, it = d.get("camera_summary"), d.get("instrument_summary")
    ot = (d.get("rows") or [{}])[0].get("other_arm", "C")
    if cs:
        print(f"**구 계기(팔↔팔 `cam.ground_z`)**: 층 {cs['cut_tiers']} · 쌍 생존 "
              f"{cs['pair_survival']} · 컷 생존 {cs['cut_survival']} · 격리 "
              f"{cs['quarantine'] or '없음'}\n")
    if it:
        print(f"**REPAIR-3 계기**: 층 {it['cut_tiers']} · 청정 쌍 "
              f"{it['pair_clean']}\n")
    print(f"| 밴드 | 씬 | 구 계기 | Δground_z max | 링 walk_z | 스트립 walk_z | "
          f"링−스트립 | devA(스트립) | dev{ot}(스트립) | 스트립 기준 층 | 국소화 |")
    print("|---|---|---|---:|---:|---:|---:|---:|---:|---|---|")
    for r in d.get("rows", []):
        c = r.get("camera") or {}
        i = r.get("instrument") or {}
        star = " ⚠️" if "datum_defect_scene" in r else ""
        arms = sorted({o["arm_off"] for o in i.get("strip_off_cuts", [])}) or ["—"]
        print(f"| {r['band']} | `{r['scene']}`{star} | {c.get('verdict','—')} | "
              f"{c.get('ground_z_drift_max','—')} | {i.get('walk_z','—')} | "
              f"{i.get('walk_z_strip','—')} | {i.get('ring_vs_strip_m','—')} | "
              f"{i.get('strip_max_dev_A','—')} | {i.get('strip_max_dev_X','—')} | "
              f"{i.get('strip_verdict','—')} | {','.join(arms)} |")
    print("\n⚠️ = `W1D_REPORT` §3 의 데이텀 결함 3건(scene02 2.8236 · scene10 0.2500 · "
          "sceneN1 12.8000).")


def t_datum():
    _datum_block("w1c_datum.json", "#### 표 D — VG-datum (A,C) · **REPAIR-3** 계기")
    _datum_block("w1c_datum_AD.json",
                 "##### 표 D-2 — 같은 계기를 (A,D) 축에 · 데이텀 결함 3씬 "
                 "(sceneN1 은 C팔이 on팔 재활용이라 이 축에서만 잰다)")


def t_continuity():
    d = load("w1c_verify.json")
    print("\n#### 표 E — C팔 연속성 게이트 (D58)\n")
    if not d:
        print("_(w1c_verify.json 없음)_"); return
    th = d["thresholds"]
    print(f"등록 문턱(사전): 포즈별 단서 마스크 A↔C IoU ≥ **{th['cue_iou_min']}** ∧ "
          f"단서 픽셀질량 잔존 C/A ≥ **{th['cue_mass_min']}**\n")
    print("| 밴드 | 씬 | 포즈 | 세그 보유 | IoU min | IoU 중앙 | 질량비 min | 질량비 중앙 | 판정 |")
    print("|---|---|---:|---:|---:|---:|---:|---:|---|")
    for r in d["rows"]:
        c = r.get("continuity")
        if not c:
            continue
        print(f"| {r['band']} | `{r['scene']}` | {c['n_pose']} | {c['n_pose_with_seg']} | "
              f"{c['iou_min']} | {c['iou_med']} | {c['mass_ratio_min']} | "
              f"{c['mass_ratio_med']} | {'✅' if c['ok'] else ('—미측정' if c['ok'] is None else '❌')} |")
    s = d.get("continuity_summary")
    if s:
        print(f"\n통과 **{s['n_pass']}/{s['n_judged']}** (판정 대상) · 미측정 "
              f"{s['n_unmeasured']} · 전체 최소 IoU {s['iou_min_overall']}")
        print(f"\n> {s['note']}")
        if s["units_without_seg"]:
            print(f"세그 부재 유닛: {s['units_without_seg']}")


def t_optical():
    d = load("w1c_verify.json")
    print("\n#### 표 F — (A,C) 광학차 분포 (계기판① 영정보 층화 입력)\n")
    if not d:
        print("_(w1c_verify.json 없음)_"); return
    print("| 밴드 | 씬 | 쌍 | MAD 중앙 | p10 | p90 | min | max | RMS 중앙 | 변화픽셀비 | 영정보 쌍 |")
    print("|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for r in d["rows"]:
        o = r.get("optical_ac")
        if not o:
            continue
        print(f"| {r['band']} | `{r['scene']}` | {o['n_pairs']} | **{o['mad_med']}** | "
              f"{o['mad_p10']} | {o['mad_p90']} | {o['mad_min']} | {o['mad_max']} | "
              f"{o['rms_med']} | {o['changed_frac_med']} | {o['zero_info_pairs']} |")
    s = d.get("optical_summary")
    if s:
        print(f"\n쌍 **{s['n_pairs']}** · 유닛 MAD 중앙값 **{s['mad_med_of_units']}** "
              f"(min {s['mad_med_min']} / max {s['mad_med_max']} = **{s['spread_ratio']}배**) "
              f"· 영정보 쌍 **{s['zero_info_pairs']}**")
        print(f"\n> {s['note']}")


def t_labeler():
    d = load("w1c_labeler_invariance.json")
    print("\n#### 표 G — 라벨러 측방 사각 근본 수리 · v2 소급 불변 검증 (D82 ② 필수)\n")
    if not d:
        print("_(w1c_labeler_invariance.json 없음)_"); return
    print(f"**판정: `{d['verdict']}`** — 대조군 통과 = `{d['control_ok']}`\n")
    print("| 검사 | 프레임 비교 | 상이 프레임 | GT 상이 프레임 | 필드 차이 |")
    print("|---|---:|---:|---:|---:|")
    for tag in ("control", "test"):
        t = d[tag]
        print(f"| {t['tag']} | {t['n_frames_compared']} | {t['n_frames_differing']} | "
              f"{t['n_frames_differing_gt']} | {t['n_field_diffs']} |")
    print(f"\n모집단: 씬 {d['n_scenes']} · (밴드,씬) {d['n_band_scene_pairs']} · "
          f"씬×팔 작업 {d['n_scene_arm_tasks']} · 라운드 {len(d['rounds'])} · "
          f"누락 0 · 오류 {len(d['errors'])}\n")
    pf = d["test"]["per_field"]
    print("| 필드 | 상이 프레임 |")
    print("|---|---:|")
    for k in sorted(pf, key=lambda x: -pf[x]):
        print(f"| `{k}` | {pf[k]} |")
    an = d["analysis"].get("polar_gt") or {}
    if an:
        print(f"\n`polar_gt` {an['n_changed']}프레임 변경 — 획득만 {an['gain_only']}"
              f"(+{an['cells_gained']}칸) · 상실만 {an['loss_only']}"
              f"(−{an['cells_lost']}칸) · 혼합 {an['mixed']}")
    print(f"\n> 처분: {d['adoption']}")


TABLES = dict(hashgate=t_hashgate, accounting=t_accounting, vg01ac=t_vg01ac,
              datum=t_datum, continuity=t_continuity, optical=t_optical,
              labeler=t_labeler)


def render(key):
    import contextlib
    import io as _io
    buf = _io.StringIO()
    with contextlib.redirect_stdout(buf):
        TABLES[key]()
    return buf.getvalue().rstrip("\n")


def inject(path):
    """`<!-- TABLE:key -->` 마커를 그 표의 현재 출력으로 치환한다.

    마커는 치환 후에도 **표 바로 위에 남는다** — 그래야 표를 다시 찍을 때
    같은 자리에 다시 꽂힌다(보고서를 손으로 고치지 않는다는 규율의 기계 장치).
    """
    import re as _re
    src = open(path, encoding="utf-8").read()
    n = 0
    for key in TABLES:
        pat = _re.compile(r"(<!-- TABLE:%s -->)(?:\n<!-- BEGIN -->.*?<!-- END -->)?"
                          % _re.escape(key), _re.S)
        body = render(key)
        new, k = pat.subn(lambda m: f"{m.group(1)}\n<!-- BEGIN -->\n{body}\n<!-- END -->",
                          src)
        src, n = new, n + k
    open(path, "w", encoding="utf-8").write(src)
    print(f"injected {n} table(s) -> {path}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--inject", default="", help="W1C_REPORT.md 경로")
    a = ap.parse_args()
    if a.inject:
        inject(a.inject); return
    keys = [k for k in a.only.split(",") if k] or list(TABLES)
    for k in keys:
        TABLES[k]()


if __name__ == "__main__":
    main()
