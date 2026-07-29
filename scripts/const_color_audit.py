#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""상수색 감사 — "지면류 프림에 텍스처 없는 상수색 금지" 규약의 자동 검사.

**무엇을 증명하는가**
  W2-D 판정 라운드에서 눈 에이전트가 찾아낸 최대 결함군(`tonglam_v2.md` §2.13-1
  "constant-colour kit prims")은 원인이 하나다. ground_kit 의 **지면류 데칼 역할**
  (patch·crack·wear·stain_*·membrane…)에 씬이 **paint / metal / misc** 계열 재질을
  물리면, 그 세 계열은 `scene_common._CONST_MDL_CLASSES` 에서 **의도적으로 제외**돼
  있으므로(도료·금속은 상수색이 물리적으로 옳다) 텍스처가 전혀 붙지 않고
  **죽은 평면**이 된다. scene19 막(`flat_gnd` 94.8)·scene11 판·sceneN2 균열 리본이
  전부 같은 경로다.

  이 스크립트는 렌더 없이 그 결합을 정적으로 재구성해서 잡는다.
    (1) 각 씬 파일에서 재질 팩토리 호출(`make_pbr` / 씬 로컬 `PBR` 계열)을 모아
        `M["키"] → (Looks 이름, 텍스처 여부, 상수색)` 표를 만든다.
    (2) `M2.update(역할=M["키"], ...)` 를 파싱해 **킷 역할 → 재질** 배선을 얻는다.
    (3) 지면류 역할마다 `scene_common._look_spec` 으로 클래스를 뽑고
        `_promote_const_to_texture` 로 승격까지 시뮬레이션해서 **최종 모드**를 판정한다.
        `FLAT-OMNI`(텍스처 없는 상수) 가 하나라도 남으면 FAIL.
    (4) 같은 역할에 대해 **알베도 상한 0.30**(규약 "회색 잔해 0.18~0.30" / 순백 금지)을
        본다. scene20 이 근백색 연석 상수(0.75)를 마모·오염 데칼에 물려 "빛나는 판"으로
        읽힌 사례가 이 검사에 걸린다.

사용:
    python3 scripts/const_color_audit.py            # 전 씬 감사, 위반 시 종료코드 1
    python3 scripts/const_color_audit.py --verbose  # 통과 항목까지 전부 출력
    python3 scripts/const_color_audit.py --json out.json
종료코드: 0 = 위반 0 · 1 = 위반 있음 · 2 = 하네스 오류
"""

import argparse
import ast
import glob
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

import scene_common as sc                                        # noqa: E402

# --- 규약 ------------------------------------------------------------------
# ground_kit 역할 중 **지면 표면 그 자체**인 것들. 여기 물리는 재질은 반드시
# 텍스처를 얻어야 한다(승격 또는 직접 텍스처).
GROUND_ROLES = {
    "patch", "crack", "wear", "silt", "litter", "edge_break", "debris",
    "membrane", "membrane_wear", "membrane_seam", "groove",
    "stain_dirt", "stain_water", "stain_drip", "stain_tire", "stain_oil",
    "stain_gum", "stain_grime_band", "stain_efflorescence",
}
# 상수색이 물리적으로 옳은 역할 — 검사 대상이 아니다.
#   joint/marking/tactile = 도료·줄눈 실런트, manhole/gully/trench* = 주철,
#   deck = 널판 사이 어두운 틈(그림자 선), weed = 식생 자산.
CONSTANT_OK_ROLES = {
    "joint", "marking", "tactile", "manhole", "gully", "gutter",
    "gutter_cover", "trench", "trench_frame", "deck", "weed", "curb",
    "patch_cut",                       # cutline 기본 OFF (F3) — 프림이 안 난다
}
ALBEDO_MAX = 0.30                      # 규약: 회색 잔해 0.18~0.30 · 순백 금지
_FACTORIES = ("make_pbr", "PBR", "PBR_ALBEDO", "tex")


def _tail(node):
    """경로 표현식에서 `Looks/<이름>` 의 이름만 뽑는다. f-string 도 처리."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        s = node.value
    elif isinstance(node, ast.JoinedStr):
        s = "".join(str(v.value) for v in node.values
                    if isinstance(v, ast.Constant))
    elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        a, b = _tail(node.left), _tail(node.right)
        s = (a or "") + "/" + (b or "")
    else:
        return None
    return s.rstrip("/").split("/")[-1] or None


def _literals(tree):
    """`이름=(a,b,c)` 형태의 색 리터럴을 전부 모은다(PARAMS 안의 색 이름 해석용)."""
    out = {}
    for n in ast.walk(tree):
        if isinstance(n, ast.keyword) and n.arg and isinstance(n.value, ast.Tuple):
            try:
                v = tuple(float(ast.literal_eval(e)) for e in n.value.elts)
            except Exception:
                continue
            if len(v) == 3 and all(0.0 <= x <= 1.0 for x in v):
                out.setdefault(n.arg, v)
    return out


def _colour(node, lits):
    if isinstance(node, ast.Tuple):
        try:
            v = tuple(float(ast.literal_eval(e)) for e in node.elts)
            return v if len(v) == 3 else None
        except Exception:
            return None
    if isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Constant):
        return lits.get(str(node.slice.value))
    return None


def scan_scene(path):
    """씬 하나 → (재질표, 역할배선). 재질표: 키 -> dict(name, textured, colour)."""
    tree = ast.parse(open(path, encoding="utf-8").read())
    lits = _literals(tree)
    mats, wiring = {}, {}
    for n in ast.walk(tree):
        # (1) M["키"] = <factory>(...)
        if (isinstance(n, ast.Assign) and len(n.targets) == 1
                and isinstance(n.targets[0], ast.Subscript)
                and isinstance(n.targets[0].value, ast.Name)
                and n.targets[0].value.id == "M"
                and isinstance(n.targets[0].slice, ast.Constant)
                and isinstance(n.value, ast.Call)):
            call = n.value
            fn = call.func
            fname = (fn.attr if isinstance(fn, ast.Attribute)
                     else fn.id if isinstance(fn, ast.Name) else None)
            if fname not in _FACTORIES:
                continue
            key = str(n.targets[0].slice.value)
            args = list(call.args)
            if fname == "make_pbr" and isinstance(fn, ast.Attribute):
                args = args[1:]                      # sc.make_pbr(stage, path, ...)
            if fname == "tex":                       # tex(role, path, scale, ...)
                name = _tail(args[1]) if len(args) > 1 else None
                mats[key] = dict(name=name, textured=True, colour=None,
                                 line=n.lineno)
                continue
            if not args:
                continue
            name = _tail(args[0])
            kw = {k.arg: k.value for k in call.keywords if k.arg}
            textured = ("diff" in kw) or len(args) > 1
            col = _colour(kw["diffuse_color"], lits) if "diffuse_color" in kw else None
            mats[key] = dict(name=name, textured=textured, colour=col,
                             line=n.lineno)
        # (2) M2.update(역할=M["키"], ...)
        if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                and n.func.attr == "update"
                and isinstance(n.func.value, ast.Name)
                and n.func.value.id.startswith("M")):
            for k in n.keywords:
                v = k.value
                if (k.arg and isinstance(v, ast.Subscript)
                        and isinstance(v.value, ast.Name) and v.value.id == "M"
                        and isinstance(v.slice, ast.Constant)):
                    wiring.setdefault(k.arg, (str(v.slice.value), n.lineno))
    return mats, wiring


def resolve(mat):
    """재질 dict -> (클래스, 최종모드). 모드: TEXTURED / PROMOTED / constMDL / FLAT-OMNI."""
    if mat is None or not mat.get("name"):
        return ("?", "UNRESOLVED")
    cls, spec = sc._look_spec(mat["name"])
    if mat["textured"]:
        return (cls, "TEXTURED" if spec["mdl"] == "ground" else "TEXTURED-omni")
    if cls not in sc._CONST_MDL_CLASSES:
        return (cls, "FLAT-OMNI")
    if mat["colour"] is None:
        return (cls, "constMDL")           # 색을 정적으로 못 읽음 — MDL 경로는 확정
    d, _, _, _ = sc._promote_const_to_texture(spec, mat["colour"])
    return (cls, "PROMOTED" if d else "constMDL")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--json")
    a = ap.parse_args()

    files = [f for f in
             sorted(glob.glob(os.path.join(REPO, "scenes", "main", "scene*.py"))
                    + glob.glob(os.path.join(REPO, "scenes", "batch1",
                                            "scene*.py")))
             if not os.path.islink(f)]      # scene_common.py 심링크 제외
    rows, violations = [], []
    for f in files:
        scene = os.path.basename(f).split("_")[0]
        try:
            mats, wiring = scan_scene(f)
        except SyntaxError as e:
            print(f"[감사][오류] 파싱 실패 {f}: {e}")
            return 2
        for role, (key, line) in sorted(wiring.items()):
            if role not in GROUND_ROLES:
                continue
            mat = mats.get(key)
            cls, mode = resolve(mat)
            lum = None
            if mat and mat.get("colour"):
                c = mat["colour"]
                lum = 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
            bad = []
            if mode == "FLAT-OMNI":
                bad.append("텍스처 없는 상수색")
            if lum is not None and lum > ALBEDO_MAX:
                bad.append(f"알베도 {lum:.2f} > {ALBEDO_MAX:.2f}")
            r = dict(scene=scene, role=role, key=key,
                     mtl=(mat or {}).get("name"), cls=cls, mode=mode,
                     lum=(None if lum is None else round(lum, 3)),
                     line=line, violations=bad)
            rows.append(r)
            if bad:
                violations.append(r)

    hdr = f"{'scene':9s} {'role':20s} {'material':14s} {'class':9s} {'mode':13s} lum"
    if a.verbose:
        print(hdr)
        for r in rows:
            lum = "-" if r["lum"] is None else f"{r['lum']:.2f}"
            print(f"{r['scene']:9s} {r['role']:20s} {str(r['mtl']):14s} "
                  f"{r['cls']:9s} {r['mode']:13s} {lum}")
    print(f"[감사] 지면류 배선 {len(rows)}건 · 위반 {len(violations)}건 "
          f"(씬 {len(files)})")
    if violations:
        print(hdr)
        for r in violations:
            lum = "-" if r["lum"] is None else f"{r['lum']:.2f}"
            print(f"{r['scene']:9s} {r['role']:20s} {str(r['mtl']):14s} "
                  f"{r['cls']:9s} {r['mode']:13s} {lum}   ← "
                  + " / ".join(r["violations"]))
    if a.json:
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump(dict(rows=rows, violations=violations), fh,
                      ensure_ascii=False, indent=1)
    if violations:
        print("[감사] ✗ FAIL — 지면류 프림에 텍스처 없는 상수색 / 규약 초과 알베도가 남았다.")
        return 1
    print("[감사] ✔ PASS — 지면류 프림에 텍스처 없는 상수색 0, 알베도 규약 초과 0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
