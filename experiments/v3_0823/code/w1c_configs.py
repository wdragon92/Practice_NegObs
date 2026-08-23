#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""w1c_configs.py — W1-C (C팔) 렌더 설정 생성 + 이식 상태 기계 검증.

정본 근거
---------
* `RENDER_PLAN_V3.md` §1.2 표 (팔별 조달 규칙):
      C팔 = `{"hazard_*": false, "keep_dressing": true}` — **신off 세대**
  그리고 §1.3 "`keep_dressing` 이식 15건" = s02·s03·s06·s08·s10·s12·s16·s17·
  s20·s21·C1·C4·D1·D2·D3.
* `CUE_COVERAGE.md` §2.1 결속표: 결속이 `자유`인 씬(s01·s04·s09·N1·N4·N5)은
  `hazard=False` 만으로도 단서가 남으므로 **이식이 불필요**하다.  그런 씬에
  `keep_dressing` 을 넣으면 읽는 코드가 없는 **사문 키**가 되고, 이는 §4-4 (1)
  이 금지한 것이다.  따라서 이 생성기는 **이식된 씬에만** 그 키를 넣는다.
* 무낙차 4씬(N1·N2·N4·N5)은 on팔이 그대로 C팔이므로 (§1.2 `24*`) 신규 렌더
  대상이 아니다 — 이 파일은 그 씬들의 설정을 만들지 않는다.

이 생성기는 **쓰기 전에 죽는다**: 이식 대상 15씬 각각에 대해 씬 파일에
`KEEP_DRESSING` 심볼이 실제로 존재하는지 AST 로 확인하고, 하나라도 없으면
아무것도 쓰지 않는다.  W1-B2 `w1b2_configs.py` 의 "재질 재바인딩 AST 검사"
와 같은 규율이다 — 설정이 씬이 이해하지 못하는 키를 담고 렌더가 24컷을 찍은
뒤 지표표에서 발견되는 일이 없어야 한다.
"""
import argparse
import ast
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))
CFGDIR = os.path.join(REPO, "experiments", "v3_0823", "render_configs_v3")

# --- 계획 §1.3 이식 15건 ---------------------------------------------------
PORTED = ["scene02", "scene03", "scene06", "scene08", "scene10", "scene12",
          "scene16", "scene17", "scene20", "scene21", "sceneC1", "sceneC4",
          "sceneD1", "sceneD2", "sceneD3"]
# --- 결속 `자유` — 이식 불요, C팔은 hazard=False 하나로 성립 (§1.3) --------
FREE = ["scene01", "scene04", "scene09"]

# --- 계획 §1.2 밴드 배정 (A팔이 v2에서 실제로 가진 라운드) -----------------
BANDS = {
    "scene01": ["base"],
    "scene02": ["base"],
    "scene03": ["base", "e", "e2"],
    "scene04": ["base", "e", "e2"],
    "scene06": ["base"],
    "scene08": ["base", "e"],
    "scene09": ["base", "h", "e"],
    "scene10": ["base"],
    "scene12": ["base", "e", "e2"],
    "scene16": ["base"],
    "scene17": ["base", "h", "e"],
    "scene20": ["base", "e", "e2"],
    "scene21": ["base"],
    "sceneC1": ["base", "e"],
    "sceneC4": ["base", "e", "e2"],
    "sceneD1": ["base"],
    "sceneD2": ["base"],
    "sceneD3": ["base"],
}

SCENE_FILES = {}


def _scene_paths():
    import glob
    out = {}
    for d in ("main", "batch1"):
        for p in glob.glob(os.path.join(REPO, "scenes", d, "scene*.py")):
            b = os.path.basename(p)
            key = b.split("_")[0]
            if key.startswith("scene"):
                out.setdefault(key, p)
    return out


def has_keep_dressing(path):
    """AST 로 `KEEP_DRESSING` 대입이 모듈 스코프에 있는지 본다.

    문자열 grep 이 아니라 AST 인 이유: 주석·독스트링 안의 언급이 통과를
    선언하면 안 된다.  모듈 스코프 대입만 센다 — 함수 안의 지역 변수는
    `SCENE_CONFIG` 를 읽는 옵트인 스위치가 아니다.
    """
    try:
        tree = ast.parse(open(path, encoding="utf-8").read())
    except Exception as e:
        return False, f"parse failed: {type(e).__name__}: {e}"
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == "KEEP_DRESSING":
                    src = ast.dump(node.value)
                    if "keep_dressing" not in src:
                        return False, ("KEEP_DRESSING assigned but does not "
                                       "read SCENE_CONFIG['keep_dressing']")
                    return True, "ok"
    return False, "no module-scope KEEP_DRESSING assignment"


_SEM_NAMES = {"KEEP_DRESSING", "PLACEBO_REMOVE", "_ARM"}
_SEM_CFGS = {
    "absent": {},
    "A": {"hazard_stairs": True},
    "D": {"hazard_stairs": False, "cue_railing": False, "cue_tactile": False,
          "cue_nosing": False, "cue_material_break": False, "cue_sign": False,
          "cue_scene_dressing": False},
    "C": {"hazard_stairs": False, "keep_dressing": True},
    "bad_hazard_on": {"hazard_stairs": True, "keep_dressing": True},
    "bad_dressing_off": {"hazard_stairs": False, "keep_dressing": True,
                         "cue_scene_dressing": False},
}
_SEM_EXPECT = {"absent": (False, None), "A": (False, None), "D": (False, None),
               "C": (True, None), "bad_hazard_on": (None, "SystemExit"),
               "bad_dressing_off": (None, "SystemExit")}


def _sem_wanted(n):
    if isinstance(n, ast.Assign):
        return any(getattr(t, "id", None) in _SEM_NAMES for t in n.targets)
    src = ast.dump(n)
    return "KEEP_DRESSING" in src or "PLACEBO_REMOVE" in src or "keep_dressing" in src


def semantics(scene, path):
    """이식 블록의 **의미**를 6개 설정으로 실행해 확인한다 (Isaac 불요).

    AST 로 `KEEP_DRESSING` 대입 이후의 포트 관련 노드만 뽑아 격리 실행한다.
    확인 항목: 키 부재 · A 팔 · D 팔에서 `False` · C 팔에서 `True` · 두 모순
    설정에서 `SystemExit`.  존재(AST)만으로는 "이식됐다" 를 말할 수 없고,
    **켰을 때 켜지고 껐을 때 꺼지는가**가 이식의 정의다.
    """
    import contextlib
    import io as _io
    try:
        tree = ast.parse(open(path, encoding="utf-8").read())
    except Exception as e:
        return False, {"parse": f"{type(e).__name__}: {e}"}
    idx = [i for i, n in enumerate(tree.body) if isinstance(n, ast.Assign)
           and any(getattr(t, "id", None) == "KEEP_DRESSING" for t in n.targets)]
    if not idx:
        return False, {"block": "no module-scope KEEP_DRESSING assignment"}
    blk = [n for n in tree.body[idx[0]:idx[0] + 12] if _sem_wanted(n)]
    code = compile(ast.Module(body=blk, type_ignores=[]), "<port>", "exec")
    res = {}
    for tag, cfg in _SEM_CFGS.items():
        g = {"SCENE_CONFIG": dict(cfg), "_CUEOFF_SCENE": scene}
        try:
            with contextlib.redirect_stdout(_io.StringIO()):
                exec(code, g)
            res[tag] = [g.get("KEEP_DRESSING"), None]
        except SystemExit:
            res[tag] = [None, "SystemExit"]
        except Exception as e:
            res[tag] = [None, f"{type(e).__name__}: {str(e)[:60]}"]
    ok = all(tuple(res[t]) == _SEM_EXPECT[t] for t in _SEM_EXPECT)
    return ok, res


def build():
    paths = _scene_paths()
    report, fatal = [], []
    for s in PORTED:
        p = paths.get(s)
        if p is None:
            fatal.append(f"{s}: scene file not found")
            report.append(dict(scene=s, ported=False, why="file not found"))
            continue
        ok, why = has_keep_dressing(p)
        sem_ok, sem = semantics(s, p)
        report.append(dict(scene=s, file=os.path.relpath(p, REPO),
                           ported=ok, why=why,
                           semantics_ok=sem_ok, semantics=sem))
        if not ok:
            fatal.append(f"{s}: {why}")
        elif not sem_ok:
            fatal.append(f"{s}: semantics check failed -> {sem}")
    for s in FREE:
        p = paths.get(s)
        report.append(dict(scene=s, file=os.path.relpath(p, REPO) if p else None,
                           ported=None, why="free binding — no port required "
                                            "(CUE_COVERAGE §2.1)"))
    cfgs = {}
    for s in PORTED:
        cfgs[s] = {"hazard_stairs": False, "keep_dressing": True}
    for s in FREE:
        cfgs[s] = {"hazard_stairs": False}
    return cfgs, report, fatal


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--out", default=os.path.join(
        REPO, "experiments", "v3_0823", "w1c_configs.json"))
    a = ap.parse_args()
    cfgs, report, fatal = build()
    n_cuts = {b: 0 for b in ("base", "h", "e", "e2")}
    for s, bands in BANDS.items():
        for b in bands:
            n_cuts[b] += 24
    out = dict(plan="RENDER_PLAN_V3 §1.2 · §1.3 · CUE_COVERAGE §2.1 §4-4",
               arm="C", recipe_ported={"hazard_stairs": False,
                                       "keep_dressing": True},
               recipe_free={"hazard_stairs": False},
               ported=PORTED, free=FREE, bands=BANDS,
               cuts_per_band=n_cuts, cuts_total=sum(n_cuts.values()),
               port_check=report, fatal=fatal, configs=cfgs)
    print(json.dumps(dict(cuts_per_band=n_cuts, cuts_total=sum(n_cuts.values()),
                          n_ported_ok=sum(1 for r in report
                                          if r["ported"] is True),
                          n_semantics_ok=sum(1 for r in report
                                             if r.get("semantics_ok") is True),
                          n_ported_expected=len(PORTED), fatal=fatal),
                     ensure_ascii=False, indent=2))
    for r in report:
        flag = "OK " if r["ported"] is True else ("--  " if r["ported"] is None
                                                 else "FAIL")
        sem = ("" if r.get("semantics_ok") is None
               else ("  · semantics OK" if r["semantics_ok"]
                     else f"  · semantics FAIL {r.get('semantics')}"))
        print(f"  {flag} {r['scene']:9s} {r['why']}{sem}")
    if fatal:
        print("\n[FATAL] 이식 미완 — 아무것도 쓰지 않았다:", *fatal, sep="\n  ")
        sys.exit(3)
    if a.write:
        os.makedirs(CFGDIR, exist_ok=True)
        for s, c in cfgs.items():
            with open(os.path.join(CFGDIR, f"{s}_C.json"), "w",
                      encoding="utf-8") as f:
                json.dump(c, f, ensure_ascii=False)
        with open(a.out, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)
        print(f"\nwrote {len(cfgs)} configs -> {CFGDIR}\n      ledger -> {a.out}")


if __name__ == "__main__":
    main()
