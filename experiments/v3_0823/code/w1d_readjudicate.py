#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""w1d_readjudicate.py — W0 판정(z_off = 구off) vs W1-D 재판정(z_off = D팔) 대조.

DECISIONS D72 ② · W0_CUECLS §8 · RENDER_PLAN_V3 §6.1 VG-CLS.

판정 규칙은 **바뀌지 않았다**. `w0_classify.py` 헤더의 사전등록 R1/R2/R3를
그대로 쓰고, 오직 **참조 z_off만** 갈아 끼웠다(구off → D팔). 이 파일은 두
산출물을 읽어 이동을 인쇄할 뿐 새 규칙을 만들지 않는다.

사용:  python3 experiments/v3_0823/code/w1d_readjudicate.py
산출:  experiments/v3_0823/w1d_readjudication.json (+ stdout 마크다운 표)
"""
import json
import os
import sys

REPO = "/home/vislab/Desktop/work_sy/Practice_NegObs"
V3 = os.path.join(REPO, "experiments/v3_0823")
SHORT = {"cue_railing": "R", "cue_nosing": "N", "cue_tactile": "Ta",
         "cue_material_break": "T", "cue_sign": "Sg", "cue_scene_dressing": "V"}


def vstr(r):
    return r["verdict"] + (f"({r['subtype']})" if r.get("subtype") else "")


def main():
    a = json.load(open(os.path.join(V3, "w0_cuecls.json"), encoding="utf-8"))
    b = json.load(open(os.path.join(V3, "w1d_cuecls.json"), encoding="utf-8"))
    A = {(r["scene"], r["cue"]): r for r in a["pairs"]}
    B = {(r["scene"], r["cue"]): r for r in b["pairs"]}
    keys = list(A)

    rows, moved, resolved, new_disputes = [], [], [], []
    trans = {}
    for k in keys:
        ra, rb = A[k], B[k]
        row = dict(scene=k[0], cue=k[1], short=SHORT.get(k[1]),
                   bond=ra.get("bond"),
                   before=dict(verdict=vstr(ra), t1=ra.get("verdict_t1"),
                               t2=ra.get("verdict_t2"),
                               cells_raw_a=ra.get("cells_raw_a"),
                               cells_raw_b=ra.get("cells_raw_b"),
                               d_cells_raw=ra.get("d_cells_raw"),
                               polar_gt_n_diff=ra.get("polar_gt_n_diff"),
                               fp_A=(ra.get("locus") or {}).get("fp_A_cells"),
                               dcue_in_fpA=(ra.get("locus") or {}).get("dcue_in_fpA"),
                               locus=(ra.get("locus") or {}).get("locus")),
                   after=dict(verdict=vstr(rb), t1=rb.get("verdict_t1"),
                              t2=rb.get("verdict_t2"),
                              cells_raw_a=rb.get("cells_raw_a"),
                              cells_raw_b=rb.get("cells_raw_b"),
                              d_cells_raw=rb.get("d_cells_raw"),
                              polar_gt_n_diff=rb.get("polar_gt_n_diff"),
                              fp_A=(rb.get("locus") or {}).get("fp_A_cells"),
                              dcue_in_fpA=(rb.get("locus") or {}).get("dcue_in_fpA"),
                              locus=(rb.get("locus") or {}).get("locus")),
                   changed=(ra["verdict"] != rb["verdict"]))
        rows.append(row)
        t = (ra["verdict"], rb["verdict"])
        trans[t] = trans.get(t, 0) + 1
        if row["changed"]:
            moved.append(row)
        if ra["verdict"] == "판정불가" and rb["verdict"] != "판정불가":
            resolved.append(row)
        if ra["verdict"] != "판정불가" and rb["verdict"] == "판정불가":
            new_disputes.append(row)

    out = dict(
        doc="w1d_readjudication", version="1.0",
        before=dict(source="w0_cuecls.json", z_off=a["off_round_for_footprint"],
                    counts=a["verdict_counts"],
                    n_forbidden=len(a["toggle_forbidden"])),
        after=dict(source="w1d_cuecls.json", z_off=b["off_round_for_footprint"],
                   counts=b["verdict_counts"],
                   n_forbidden=len(b["toggle_forbidden"])),
        rule_unchanged=(a["rules"] == b["rules"]),
        transitions={f"{x}->{y}": n for (x, y), n in sorted(trans.items())},
        n_moved=len(moved), n_resolved=len(resolved),
        n_new_disputes=len(new_disputes),
        resolved=[dict(scene=r["scene"], cue=r["cue"],
                       before=r["before"]["verdict"], after=r["after"]["verdict"])
                  for r in resolved],
        new_disputes=[dict(scene=r["scene"], cue=r["cue"],
                           before=r["before"]["verdict"], after=r["after"]["verdict"])
                      for r in new_disputes],
        toggle_forbidden_final=b["toggle_forbidden"],
        b_levers_final=b["b_levers_confirmed"],
        pairs=rows)
    op = os.path.join(V3, "w1d_readjudication.json")
    json.dump(out, open(op, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    # ---- stdout 마크다운 --------------------------------------------------
    print(f"규칙 동일: {out['rule_unchanged']} · z_off {out['before']['z_off']} "
          f"-> {out['after']['z_off']}")
    print(f"판정 집계  before {out['before']['counts']}  ->  after {out['after']['counts']}")
    print(f"이동 {out['n_moved']}쌍 · 분쟁 해소 {out['n_resolved']} · "
          f"새 분쟁 {out['n_new_disputes']}")
    print("전이:", out["transitions"])
    print()
    print("| 씬 | cue | 결속 | Δfp (구off) | fp∩ (구off) | **Δfp (D)** | **fp∩ (D)** "
          "| 궤적(D) | 판정 (구off) | **판정 (D)** | 이동 |")
    print("|---|---|---|---:|---:|---:|---:|---|---|---|---|")
    for r in rows:
        bf, af = r["before"], r["after"]
        f = lambda v: "—" if v is None else (f"{v:+d}" if isinstance(v, int) else str(v))
        print(f"| {r['scene']} | `{r['cue']}` | {r['bond']} | "
              f"{f(bf['d_cells_raw'])} | {bf['dcue_in_fpA']} | "
              f"**{f(af['d_cells_raw'])}** | **{af['dcue_in_fpA']}** | {af['locus']} | "
              f"{bf['verdict']} | **{af['verdict']}** | "
              f"{'→' if r['changed'] else '='} |")
    print(f"\n토글 금지 목록: {out['before']['n_forbidden']} -> "
          f"{out['after']['n_forbidden']}쌍")
    print(f"-> {op}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
