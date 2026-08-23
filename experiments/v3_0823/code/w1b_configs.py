#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""w1b_configs.py — W1 B팔 씬 설정(`{scene}_B.json`) 생성기.

레시피의 출처 (권위 사슬, 뒤가 이긴다)
--------------------------------------
1. RENDER_PLAN_V3 §1.2 팔별 조달 규칙 —
   B = `{"hazard_*": true, <VG-CLS가 허락한 모든 cue_*>: false}` = **최대 제거**.
   §4.4.4가 그 이유다: 레버를 `cue_material_break` 하나로 잡으면 팔 수준 φ는
   0.005여도 **6키 중 5키의 r ≈ 0.56**으로 퇴화한다(난간이 A·B·C에 다 남고
   D에만 없으면 그 난간은 여전히 "위험의 표지"다).
2. W1D_REPORT §6.6 「씬별 확정 B팔 레버 (최종)」 + `w1d_readjudication.json`
   `toggle_forbidden_final` (15쌍) — **레버 = ON·배선 − 금지**.
   W0의 잠정표가 아니라 여기가 정본이다.
3. DECISIONS D74 ⑤ — `scene03·scene04·scene10`은 레버가 0이라 B ≡ A(바이트
   동일)가 된다 ⇒ **B팔을 찍지 않는다**(168컷 스킵). 본 파일은 그 세 씬의
   설정을 만들지 않고 `skipped`에 기록한다.

기계적 정의 (이 파일이 하는 전부)
---------------------------------
    ONWIRED(s) = { c : hazgate[s].defaults[c] is True  AND  hazgate[s].cue[c] is not None }
    LEVERS(s)  = ONWIRED(s) − FORBIDDEN(s)
    CONFIG(s)  = { h: true for h in hazard_keys(s) } ∪ { c: false for c in LEVERS(s) }

금지된 cue는 **설정에 아예 넣지 않는다** — 기본값 ON으로 남아야 하고, 그것이
"그 단서는 구조물이라 끌 수 없다"는 기록이다. 배선되지 않은 cue도 넣지 않는다
(D팔 설정과 다른 점 — D는 6키를 전부 false로 못 박는 것이 레시피 자체였다).

산출을 §6.6 표와 **대조**한 뒤에만 쓴다. 표와 어긋나면 아무것도 쓰지 않고 죽는다.

사용:  python3 experiments/v3_0823/code/w1b_configs.py [--write]
"""
import argparse
import json
import os
import sys

REPO = "/home/vislab/Desktop/work_sy/Practice_NegObs"
V3 = os.path.join(REPO, "experiments/v3_0823")
CFG = os.path.join(V3, "render_configs_v3")

# --- W1D_REPORT §6.6 표를 그대로 옮긴 것 (기계 산출과 대조할 독립 사본) -------
K = dict(T="cue_material_break", R="cue_railing", N="cue_nosing",
         V="cue_scene_dressing", Sg="cue_sign", Ta="cue_tactile")
TABLE_66 = {                       # 씬 -> (ON·배선, B팔 레버(최종))
    "scene01": ("T R V Sg", "T Sg"),
    "scene02": ("N R V Sg", "N R Sg"),
    "scene03": ("V", ""),                       # B ≡ A → 스킵 (D74 ⑤)
    "scene04": ("V", ""),                       # B ≡ A → 스킵 (D74 ⑤)
    "scene06": ("T R V", "T R V"),              # D72 ③ 보류 해제
    "scene08": ("R V Sg", "V Sg"),
    "scene09": ("V Sg", "Sg"),
    "scene10": ("R V", ""),                     # B ≡ A → 스킵 (D74 ⑤)
    "scene12": ("R V", "R V"),
    "scene16": ("N R V Sg", "N R V Sg"),
    "scene17": ("V", "V"),
    "scene20": ("R V", "V"),
    "scene21": ("N R V Sg", "V Sg"),
    "sceneC1": ("N R V", "N"),
    "sceneC4": ("R V", "R"),
    "sceneD1": ("N V", "N V"),
    "sceneD2": ("T V", "T V"),
    "sceneD3": ("V", "V"),
}
# B팔이 존재하지 않는 씬: 무낙차 4씬(N1·N2·N4·N5)은 on팔이 이미 C팔이라
# A/B 자체가 성립하지 않는다 (계획 §1.1 첫 항목).
NO_B_ARM = ["sceneN1", "sceneN2", "sceneN4", "sceneN5"]
SKIP_D74 = ["scene03", "scene04", "scene10"]


def load_hazgate():
    hz = json.load(open(os.path.join(V3, "code/hazgate.json"), encoding="utf-8"))
    out = {}
    for k, v in hz.items():
        tag, fn = k.split("::")
        if tag not in ("main", "batch1"):
            continue
        out[fn.split("_")[0]] = v
    return out


def main(write):
    hz = load_hazgate()
    forb = {}
    for x in json.load(open(os.path.join(V3, "w1d_readjudication.json"),
                            encoding="utf-8"))["toggle_forbidden_final"]:
        forb.setdefault(x["scene"], set()).add(x["cue"])

    rows, problems, wrote = [], [], []
    for s, (onw_t, lev_t) in TABLE_66.items():
        v = hz.get(s)
        if v is None:
            problems.append(f"{s}: hazgate 레코드 없음")
            continue
        d, cue = v["defaults"], v["cue"]
        onwired = sorted(c for c, r in cue.items()
                         if r is not None and d.get(c) is True)
        levers = sorted(set(onwired) - forb.get(s, set()))
        # --- §6.6 표와 대조 ------------------------------------------------
        want_on = sorted(K[t] for t in onw_t.split())
        want_lv = sorted(K[t] for t in lev_t.split()) if lev_t else []
        if onwired != want_on:
            problems.append(f"{s}: ON·배선 불일치 hazgate={onwired} vs §6.6={want_on}")
        if levers != want_lv:
            problems.append(f"{s}: 레버 불일치 derived={levers} vs §6.6={want_lv}")
        cfg = {h: True for h in v["hazard_keys"]}
        cfg.update({c: False for c in levers})
        rows.append(dict(scene=s, hazard_keys=v["hazard_keys"], onwired=onwired,
                         forbidden=sorted(forb.get(s, set())), levers=levers,
                         n_levers=len(levers), config=cfg,
                         disposition=("SKIP (B ≡ A · D74 ⑤)" if not levers else "render")))

    if problems:
        print("FATAL — 파생 레버가 W1D_REPORT §6.6 표와 어긋난다. 아무것도 쓰지 않는다.")
        for p in problems:
            print("  -", p)
        return 3

    for r in rows:
        if not r["levers"]:
            continue
        p = os.path.join(CFG, f"{r['scene']}_B.json")
        if write:
            with open(p, "w", encoding="utf-8") as f:
                json.dump(r["config"], f, ensure_ascii=False)
            wrote.append(os.path.basename(p))

    out = dict(doc="w1b_configs", version="1.0",
               rule="LEVERS = ONWIRED(hazgate) − FORBIDDEN(w1d_readjudication."
                    "toggle_forbidden_final); CONFIG = {hazard: true} + {lever: false}",
               authority=["RENDER_PLAN_V3 §1.2 · §4.4.4", "W1D_REPORT §6.6",
                          "w1d_readjudication.json toggle_forbidden_final (15)",
                          "DECISIONS D74 ⑤ (레버 0 → 스킵)"],
               table_66_crosscheck="PASS (18/18 씬 ON·배선·레버 일치)",
               skipped_d74=SKIP_D74, no_b_arm=NO_B_ARM,
               n_render_scenes=sum(1 for r in rows if r["levers"]),
               n_levers_total=sum(r["n_levers"] for r in rows),
               wrote=wrote, scenes=rows)
    op = os.path.join(V3, "w1b_configs.json")
    json.dump(out, open(op, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    print(f"{'scene':9s} {'ON·배선':38s} {'금지':26s} {'레버 (B팔 설정)':38s} 처분")
    print("-" * 128)
    for r in rows:
        sh = lambda xs: ",".join(x.replace("cue_", "") for x in xs) or "—"
        print(f"{r['scene']:9s} {sh(r['onwired']):38s} {sh(r['forbidden']):26s} "
              f"{sh(r['levers']):38s} {r['disposition']}")
    print(f"\n§6.6 대조: PASS · 렌더 대상 {out['n_render_scenes']}씬 · "
          f"레버 {out['n_levers_total']}개 · 스킵 {SKIP_D74}")
    print(f"기록: {len(wrote)} 파일 -> {CFG}" if write else "(--write 없음 — 감사만)")
    print(f"-> {op}")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    sys.exit(main(ap.parse_args().write))
