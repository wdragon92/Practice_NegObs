#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""w1b2_configs.py — W1-B2 보충 웨이브 설정(`{scene}_B2.json`) 생성기.

무엇을 고치나 (DECISIONS D75 ③ · W1B_REPORT §8.1)
------------------------------------------------
`hazgate.py`가 cue 배선을 **`if` 문 조건절에서만** 수집한 탓에
`mtl = M[a] if cfg["cue_material_break"] else M[b]` 형태의 **삼항 읽기 23칸**을
"배선無"로 오기록했다. 그 손실이 W0 프로브 → W1-D 재판정 → W1D §6.6 레버표 →
W1-B 레시피까지 4단계를 타고 왔고, 그 결과 B팔이 `cue_material_break`(T)를
**6씬에서만** 껐다. T가 A·B·C에 남고 D에만 없으면 그 재질전이는 여전히
"위험의 표지"이므로 **T키의 |r|이 0.3100으로 VG-09 문턱 0.2를 넘겼다**.

레시피 (B2 = B + T)
-------------------
    ONWIRED_full(s) = { c : hazgate_full[s].cue[c] is not None
                            AND hazgate_full[s].defaults[c] is True }
    LEVERS_full(s)  = ONWIRED_full(s) − FORBIDDEN(s)
    ADD(s)          = LEVERS_full(s) − LEVERS_B(s)            # 실제로 찍은 B 레버
    B2 대상         = { s : "cue_material_break" in ADD(s) }
    CONFIG_B2(s)    = CONFIG_B(s) ∪ { "cue_material_break": false }

**T 이외의 신규 노출 키는 넣지 않는다.** 사각지대가 드러낸 23쌍 중
`cue_tactile` 2쌍(sceneC1·sceneC4)과 `cue_nosing` 1쌍(sceneN3)은 **프림 생성형**
이라 VG-01을 구성상 보증할 수 없다(§8.1 "예외 3쌍만 판정이 필요하다"). 그 셋은
`held_pending_ruling`에 기록하고 **레버에 넣지 않는다** — W1B_REPORT §7.1의
`PB_plusT` 예측(T만 메움)과 정확히 같은 모집단이다.

VG-01 안전이 "구성상"인 이유 — 기계 술어
----------------------------------------
추가하는 자리가 전부 **재질 재바인딩**임을 AST로 확인한다:
읽기가 `ast.IfExp`의 `test` **전체**이고 `body`·`orelse`가 **둘 다 같은
재질 딕셔너리의 첨자 읽기**이면 `MATL_REBIND`. 프림이 하나도 생성·삭제되지
않으므로 계획 §1.2의 바닥 규칙("재질 재바인딩 전용 ⇒ 높이맵 비트 동일이
구성상 보증")이 그대로 적용된다. 하나라도 `NEEDS_REVIEW`면 **아무것도 쓰지 않고
죽는다**. (구성상 보증이어도 게이트 배터리로 **실증**한다 — w1b2_verify.py)

사용:  python3 experiments/v3_0823/code/w1b2_configs.py [--write]
전제:  code/hazgate_full.json 이 있어야 한다 (`python3 hazgate.py --mode full`)
"""
import argparse
import ast
import json
import os
import sys

REPO = "/home/vislab/Desktop/work_sy/Practice_NegObs"
V3 = os.path.join(REPO, "experiments/v3_0823")
CFG = os.path.join(V3, "render_configs_v3")
CUE = ["cue_railing", "cue_tactile", "cue_nosing", "cue_material_break",
       "cue_sign", "cue_scene_dressing"]
T = "cue_material_break"

# 밴드 표 — run_260826_v3w1_lib_b.sh 의 S_BASE/S_H/S_E/S_E2 그대로
BANDS = {
    "scene01": ["base"], "scene02": ["base"], "scene06": ["base"],
    "scene08": ["base", "e"], "scene09": ["base", "h", "e"],
    "scene12": ["base", "e", "e2"], "scene16": ["base"],
    "scene17": ["base", "h", "e"], "scene20": ["base", "e", "e2"],
    "scene21": ["base"], "sceneC1": ["base", "e"],
    "sceneC4": ["base", "e", "e2"], "sceneD1": ["base"],
    "sceneD2": ["base"], "sceneD3": ["base"],
}
SCENE_FILE = {}                                    # scene -> (tag, filename)


def load_hazgate(name):
    hz = json.load(open(os.path.join(V3, "code", name), encoding="utf-8"))
    out = {}
    for k, v in hz.items():
        if "::" not in k:                          # __meta__
            continue
        tag, fn = k.split("::")
        if tag not in ("main", "batch1"):
            continue
        s = fn.split("_")[0]
        out[s] = v
        SCENE_FILE[s] = (tag, fn)
    return out


def matl_rebind_sites(scene, cue):
    """그 씬에서 `cue`를 읽는 자리를 (lineno, 분류, 소스) 로 돌려준다."""
    tag, fn = SCENE_FILE[scene]
    p = os.path.join(REPO, "scenes", "main" if tag == "main" else "batch1", fn)
    src = open(p, encoding="utf-8", errors="replace").read()
    lines = src.split("\n")
    tree = ast.parse(src)

    def is_read(x):
        if isinstance(x, ast.Subscript) and isinstance(x.slice, ast.Constant) \
                and x.slice.value == cue and isinstance(x.value, ast.Name) \
                and x.value.id in ("cfg", "SCENE_CONFIG"):
            return True
        return (isinstance(x, ast.Call) and isinstance(x.func, ast.Attribute)
                and x.func.attr == "get" and x.args
                and isinstance(x.args[0], ast.Constant)
                and x.args[0].value == cue
                and isinstance(x.func.value, ast.Name)
                and x.func.value.id in ("cfg", "SCENE_CONFIG"))

    def dict_read(n):
        """`M["x"]` 꼴이면 그 딕셔너리 이름, 아니면 None."""
        if isinstance(n, ast.Subscript) and isinstance(n.value, ast.Name) \
                and isinstance(n.slice, ast.Constant) \
                and isinstance(n.slice.value, str):
            return n.value.id
        return None

    sites = []
    for x in ast.walk(tree):
        if not isinstance(x, ast.IfExp):
            continue
        if not is_read(x.test):                    # 읽기가 test **전체**여야 한다
            continue
        db, do = dict_read(x.body), dict_read(x.orelse)
        kind = ("MATL_REBIND" if db is not None and db == do else "NEEDS_REVIEW")
        sites.append(dict(L=x.lineno, kind=kind, dict_name=db,
                          src=lines[x.lineno - 1].strip()[:200]))
    seen_l = {s["L"] for s in sites}
    # test 전체가 아닌(불린 결합·if문·인자 등) 나머지 읽기 — 전부 검토 대상
    for x in ast.walk(tree):
        if is_read(x) and getattr(x, "lineno", -1) not in seen_l:
            sites.append(dict(L=x.lineno, kind="NEEDS_REVIEW", dict_name=None,
                              src=lines[x.lineno - 1].strip()[:200]))
    return sorted(sites, key=lambda s: s["L"])


def main(write):
    old = load_hazgate("hazgate.json")
    fullp = os.path.join(V3, "code/hazgate_full.json")
    if not os.path.exists(fullp):
        print("FATAL — code/hazgate_full.json 이 없다. 먼저:\n"
              "  cd experiments/v3_0823/code && python3 hazgate.py --mode full")
        return 4
    new = load_hazgate("hazgate_full.json")

    forb = {}
    for x in json.load(open(os.path.join(V3, "w1d_readjudication.json"),
                            encoding="utf-8"))["toggle_forbidden_final"]:
        forb.setdefault(x["scene"], set()).add(x["cue"])

    landed = {r["scene"]: r for r in
              json.load(open(os.path.join(V3, "w1b_configs.json"),
                             encoding="utf-8"))["scenes"]}

    rows, problems, held, wrote = [], [], [], []
    for s, bands in BANDS.items():
        if s not in new or s not in old:
            problems.append(f"{s}: hazgate 레코드 없음")
            continue
        dN, cN = new[s]["defaults"], new[s]["cue"]
        onw_full = sorted(c for c in CUE
                          if cN.get(c) is not None and dN.get(c) is True)
        lev_full = sorted(set(onw_full) - forb.get(s, set()))
        lev_b = landed[s]["levers"]
        add = sorted(set(lev_full) - set(lev_b))
        if not add:
            continue
        for c in add:
            if c == T:
                continue
            held.append(dict(scene=s, cue=c,
                             why="프림 생성형 — VG-01 구성상 보증 불가 "
                                 "(W1B_REPORT §8.1 예외 3쌍). 결재 대기."))
        if T not in add:
            continue
        # --- VG-01 안전: 추가하는 T 자리가 전부 재질 재바인딩인가 ------------
        sites = matl_rebind_sites(s, T)
        bad = [x for x in sites if x["kind"] != "MATL_REBIND"]
        if not sites:
            problems.append(f"{s}: T 읽기 자리를 하나도 못 찾았다")
        for x in bad:
            problems.append(f"{s}:L{x['L']} T 읽기가 재질 재바인딩이 아니다 — "
                            f"{x['src']}")
        cfg2 = dict(landed[s]["config"])
        cfg2[T] = False
        rows.append(dict(scene=s, bands=bands, cuts=24 * len(bands),
                         levers_B=lev_b, add=add, applied=[T],
                         levers_B2=sorted(set(lev_b) | {T}),
                         onwired_full=onw_full,
                         forbidden=sorted(forb.get(s, set())),
                         config_B=landed[s]["config"], config=cfg2,
                         t_sites=sites))

    if problems:
        print("FATAL — B2 레시피가 구성상 안전 조건을 만족하지 않는다. "
              "아무것도 쓰지 않는다.")
        for p in problems:
            print("  -", p)
        return 3

    for r in rows:
        p = os.path.join(CFG, f"{r['scene']}_B2.json")
        if write:
            with open(p, "w", encoding="utf-8") as f:
                json.dump(r["config"], f, ensure_ascii=False)
            wrote.append(os.path.basename(p))

    out = dict(
        doc="w1b2_configs", version="1.0",
        authority=["DECISIONS D75 ③", "W1B_REPORT §8.1 · §7.1(PB_plusT)",
                   "RENDER_PLAN_V3 §1.2 바닥 규칙 (재질 재바인딩 전용)"],
        rule="CONFIG_B2 = CONFIG_B ∪ {cue_material_break: false}; "
             "T 이외의 신규 노출 키는 결재 전까지 넣지 않는다",
        hazgate_if_only="code/hazgate.json (옛 계보 · 그대로 보존)",
        hazgate_full="code/hazgate_full.json (수리본)",
        n_scenes=len(rows), n_cuts=sum(r["cuts"] for r in rows),
        held_pending_ruling=held, wrote=wrote, scenes=rows)
    op = os.path.join(V3, "w1b2_configs.json")
    json.dump(out, open(op, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    sh = lambda xs: ",".join(x.replace("cue_", "") for x in xs) or "—"
    print(f"{'scene':9s} {'밴드':14s} {'컷':>4s} {'B 레버':30s} "
          f"{'추가':22s} {'B2 레버':34s} T자리")
    print("-" * 132)
    for r in rows:
        print(f"{r['scene']:9s} {','.join(r['bands']):14s} {r['cuts']:4d} "
              f"{sh(r['levers_B']):30s} {sh(r['applied']):22s} "
              f"{sh(r['levers_B2']):34s} "
              f"{len(r['t_sites'])} MATL_REBIND")
    print(f"\nB2 대상 {out['n_scenes']}씬 · {out['n_cuts']}컷 · "
          f"신규 컷 0 (같은 씬·시드·밴드·조건을 다시 찍는다)")
    if held:
        print(f"결재 대기(레버에 넣지 않음) {len(held)}건: "
              + ", ".join(f"{h['scene']}·{h['cue'].replace('cue_','')}" for h in held))
    print(f"기록: {len(wrote)} 파일 -> {CFG}" if write else "(--write 없음 — 감사만)")
    print(f"-> {op}")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    sys.exit(main(ap.parse_args().write))
