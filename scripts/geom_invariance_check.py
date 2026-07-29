#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""기하 불변 검사 — 규칙 R-4 / R-5 / R-6 (`t1_material_layer_spec_v1.md` §1.7.2)

**무엇을 증명하는가**
  R-5  잔존 `LOOK_V1` 참조 0 — 주석·docstring 을 제거한 토큰 기준.
       (§1.7.1 의 24건 분류표를 "산출물"이 아니라 "감사 흔적"으로 강등시키는 어서션.
        표가 틀려도 이 검사가 통과하지 못하므로 열거 누락이 구조적으로 불가능해진다.)
  R-4  `LOOK_MTL=0` / `LOOK_MTL=1` 두 팔의 **프림 인벤토리 해시**가 같다.
       재질층이 기하에 손대면(규칙 R-1 위반) 여기서 잡힌다.
  R-6  거기에 더해 `LOOK_V1=1` 단독 실행의 해시와도 같다.
       R-4 만으로는 "양팔이 똑같이 틀린" 유형(§2.5 — `:2143`·`:2187` 누락)을 못 잡는다.

**어떻게 도는가 — GPU 0**
  `pxr`·`omni`·`carb`·`isaacsim` 을 가짜 모듈로 갈아끼운다. `UsdGeom` 만
  **기록 스텁**(Cube/Cylinder/Sphere/Mesh/Xform 의 Define + xformOp Set)이고
  나머지는 MagicMock 이다. 씬 파일의 `main()` 을 `NEGOBS_CAPTURE=1` 경로로
  돌리면 조립만 하고 캡처 직전에 되돌아 나온다.
  → 프림 생성 경로가 `sc.add_box` 든 씬 로컬 헬퍼(scene01)든 킷의 직접
    `Mesh.Define` 이든 **전부 같은 그물에 걸린다.**
  (같은 방식이 `const_color_texture_map.md` §0-2 에서 33/33 성공으로 검증됐다.)

사용:
    python3 scripts/geom_invariance_check.py                  # R-5 → R-4 → R-6
    python3 scripts/geom_invariance_check.py --assert-no-residual-lookv1
    python3 scripts/geom_invariance_check.py --baseline Docs/reports/geom_baseline_w2.json
    python3 scripts/geom_invariance_check.py --scenes scene19,sceneC2
종료코드: 0 = 전항목 통과 · 1 = 불일치/잔존참조 · 2 = 하네스 오류
"""

import argparse
import glob
import hashlib
import io
import json
import os
import subprocess
import sys
import tokenize

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------------------
# R-5 — 잔존 `LOOK_V1` 참조 0
# ---------------------------------------------------------------------------
# 정의 3줄(호환 심)만 허용한다. 행번호가 아니라 **파일 + 토큰 문맥**으로 허용해야
# 병행 편집으로 행이 밀려도 오탐이 안 난다 — §1.7.1 이 "행번호는 스냅샷"이라고
# 못박은 것과 같은 이유다.
_ALLOW_FILE = "scene_common.py"
_ALLOW_MAX = 3                       # LOOK_V1 / LOOK_MTL / LOOK_GEO 정의 3줄

_R5_SOURCES = ["scene_common.py", "facade_kit.py", "building_kit.py",
               "infra_kit.py", "stair_kit.py", "ground_kit.py",
               "batch1_common.py"]


def _r5_files():
    out = []
    for rel in _R5_SOURCES:
        p = os.path.join(REPO, rel)
        if os.path.isfile(p):
            out.append(p)
    for p in sorted(glob.glob(os.path.join(REPO, "scenes", "*", "*.py"))):
        if os.path.islink(p):        # scenes/*/scene_common.py 등 심링크 중복 제외
            continue
        if "archive_v3" in p:        # 33씬 밖 — §1.7.1 주
            continue
        out.append(p)
    return out


def check_residual_lookv1(verbose=True):
    """주석·docstring 을 제거한 뒤 남는 `LOOK_V1` 토큰을 센다.

    주석은 세지 않는다 — 경위 기록(치명 C3 의 재발 경위)은 코드에 남아야 한다.
    반환: (위반 리스트, 허용 리스트)
    """
    bad, allowed = [], []
    for path in _r5_files():
        rel = os.path.relpath(path, REPO)
        with open(path, "rb") as fh:
            src = fh.read()
        try:
            toks = list(tokenize.tokenize(io.BytesIO(src).readline))
        except tokenize.TokenError as e:      # pragma: no cover
            print(f"[R-5][오류] 토큰화 실패 {rel}: {e}")
            return [(rel, -1, "tokenize 실패")], allowed
        prev_meaningful = None
        for tok in toks:
            if tok.type == tokenize.COMMENT:
                continue
            if tok.type == tokenize.STRING:
                # docstring 여부와 무관하게 문자열 리터럴은 코드 참조가 아니다.
                # 단 `os.environ.get("NEGOBS_LOOK_V1", ...)` 는 문자열이지만
                # **동작하는 배선**이므로 아래 NAME 검사와 함께 허용 집계한다.
                if "NEGOBS_LOOK_V1" in tok.string:
                    (allowed if os.path.basename(path) == _ALLOW_FILE
                     else bad).append((rel, tok.start[0], tok.line.strip()))
                continue
            if tok.type == tokenize.NAME and tok.string in ("LOOK_V1",):
                if os.path.basename(path) == _ALLOW_FILE:
                    allowed.append((rel, tok.start[0], tok.line.strip()))
                else:
                    bad.append((rel, tok.start[0], tok.line.strip()))
            prev_meaningful = tok
        _ = prev_meaningful
    # 허용분도 "정의 3줄"을 넘어서면 위반이다(다른 곳에서 몰래 읽고 있다는 뜻).
    allow_lines = sorted({ln for _f, ln, _s in allowed})
    if len(allow_lines) > _ALLOW_MAX:
        for rel, ln, s in allowed:
            if ln not in allow_lines[:_ALLOW_MAX]:
                bad.append((rel, ln, s))
    if verbose:
        print(f"[R-5] 스캔 {len(_r5_files())} 파일 · 허용 {len(allow_lines)} 행"
              f"(호환 심) · 위반 {len(bad)} 건")
        for rel, ln, s in bad:
            print(f"  ✗ {rel}:{ln}  {s}")
        for rel, ln, s in sorted(set(allowed)):
            print(f"  · 허용 {rel}:{ln}  {s}")
    return bad, allowed


# ---------------------------------------------------------------------------
# 가짜 USD — 프림 인벤토리 기록 스텁
# ---------------------------------------------------------------------------
_FAKE = r'''
import hashlib as _hl, sys as _sys, types as _ty
from unittest.mock import MagicMock as _MM

_PRIMS = {}          # path -> record


def _num(v):
    """Gf.Vec* / 스칼라 / 시퀀스를 비교 가능한 순수 파이썬 값으로."""
    if isinstance(v, (int, float)):
        return round(float(v), 6)
    if isinstance(v, (tuple, list)):
        try:
            return tuple(_num(x) for x in v)
        except Exception:
            return "?"
    try:
        return round(float(v), 6)
    except Exception:
        return str(type(v).__name__)


class _Attr(object):
    def Set(self, *a, **k):
        return None

    def __getattr__(self, name):
        return lambda *a, **k: None


class _Op(object):
    __slots__ = ("rec", "kind")

    def __init__(self, rec, kind):
        self.rec, self.kind = rec, kind

    def Set(self, v=None, *a, **k):
        self.rec["ops"].append((self.kind, _num(v)))
        return None

    def __getattr__(self, name):
        return lambda *a, **k: None


class _Geom(object):
    """Define() 이 돌려주는 물건 — 프림이자 Xformable 이자 Gprim 이다."""

    def __init__(self, rec):
        object.__setattr__(self, "_rec", rec)

    # --- xform ops -------------------------------------------------------
    def AddTranslateOp(self, *a, **k):
        return _Op(self._rec, "T")

    def AddScaleOp(self, *a, **k):
        return _Op(self._rec, "S")

    def AddRotateXOp(self, *a, **k):
        return _Op(self._rec, "RX")

    def AddRotateYOp(self, *a, **k):
        return _Op(self._rec, "RY")

    def AddRotateZOp(self, *a, **k):
        return _Op(self._rec, "RZ")

    def AddRotateXYZOp(self, *a, **k):
        return _Op(self._rec, "RXYZ")

    def AddOrientOp(self, *a, **k):
        return _Op(self._rec, "Q")

    def AddTransformOp(self, *a, **k):
        return _Op(self._rec, "M")

    def ClearXformOpOrder(self, *a, **k):
        self._rec["ops"] = []

    # --- 형상 속성 --------------------------------------------------------
    def _attr(self, key, v):
        self._rec["attrs"][key] = _num(v)
        return _Attr()

    def CreateSizeAttr(self, v=None, *a, **k):
        return self._attr("size", v)

    def CreateRadiusAttr(self, v=None, *a, **k):
        return self._attr("radius", v)

    def CreateHeightAttr(self, v=None, *a, **k):
        return self._attr("height", v)

    def CreateAxisAttr(self, v=None, *a, **k):
        return self._attr("axis", str(v))

    def CreateExtentAttr(self, v=None, *a, **k):
        return self._attr("extent", v)

    def CreatePointsAttr(self, v=None, *a, **k):
        return self._attr("points", _digest(v))

    def CreateFaceVertexCountsAttr(self, v=None, *a, **k):
        return self._attr("fvc", _digest(v))

    def CreateFaceVertexIndicesAttr(self, v=None, *a, **k):
        return self._attr("fvi", _digest(v))

    def CreateNormalsAttr(self, v=None, *a, **k):
        return self._attr("nrm", _digest(v))

    def CreateSubdivisionSchemeAttr(self, v=None, *a, **k):
        return self._attr("subdiv", str(v))

    # --- 프림 인터페이스 --------------------------------------------------
    def GetPrim(self):
        return self

    def GetPath(self):
        return self._rec["path"]

    def GetReferences(self):
        return _Refs(self._rec)

    def SetInstanceable(self, v=True, *a, **k):
        self._rec["attrs"]["instanceable"] = bool(v)
        return True

    def IsValid(self):
        return True

    def __getattr__(self, name):
        # 그 밖의 USD API 는 전부 무해한 no-op (셰이더 바인딩·visibility 등).
        return lambda *a, **k: _Attr()


class _Refs(object):
    def __init__(self, rec):
        self.rec = rec

    def AddReference(self, asset, *a, **k):
        self.rec["refs"].append(str(asset).replace("\\", "/").split("/")[-1])
        return True

    def __getattr__(self, name):
        return lambda *a, **k: True


def _digest(seq):
    """points/indices 배열 요약 — 개수 + 반올림 좌표 해시."""
    try:
        items = list(seq)
    except Exception:
        return "?"
    h = _hl.blake2b(digest_size=8)
    for it in items:
        h.update(repr(_num(it)).encode())
    return "n%d:%s" % (len(items), h.hexdigest())


def _define(typ):
    def _f(stage, path, *a, **k):
        p = str(path)
        rec = _PRIMS.get(p)
        if rec is None:
            rec = dict(path=p, type=typ, ops=[], attrs={}, refs=[],
                       seq=len(_PRIMS))
            _PRIMS[p] = rec
        elif rec["type"] == "Xform" and typ != "Xform":
            rec["type"] = typ          # Xform 선언 후 구체 타입으로 덮어쓴 경우
        return _Geom(rec)
    return _f


class _Vec(tuple):
    """Gf.Vec* 대역 — 튜플이라 그대로 비교·직렬화된다."""

    def __new__(cls, *a):
        if len(a) == 1 and isinstance(a[0], (tuple, list)):
            a = tuple(a[0])
        return super(_Vec, cls).__new__(cls, [float(x) for x in a])

    def __mul__(self, s):
        return _Vec(*[x * float(s) for x in self])
    __rmul__ = __mul__

    def __add__(self, o):
        return _Vec(*[x + y for x, y in zip(self, o)])

    def __sub__(self, o):
        return _Vec(*[x - y for x, y in zip(self, o)])


class _UsdGeomMod(object):
    Tokens = _MM()

    class Cube(object):
        Define = staticmethod(_define("Cube"))

    class Cylinder(object):
        Define = staticmethod(_define("Cylinder"))

    class Sphere(object):
        Define = staticmethod(_define("Sphere"))

    class Cone(object):
        Define = staticmethod(_define("Cone"))

    class Capsule(object):
        Define = staticmethod(_define("Capsule"))

    class Mesh(object):
        Define = staticmethod(_define("Mesh"))

    class Xform(object):
        Define = staticmethod(_define("Xform"))

    class Scope(object):
        Define = staticmethod(_define("Scope"))

    @staticmethod
    def Xformable(o):
        return o

    @staticmethod
    def Imageable(o):
        return o if isinstance(o, _Geom) else _MM()

    @staticmethod
    def Gprim(*a, **k):
        return _MM()

    @staticmethod
    def PrimvarsAPI(*a, **k):
        return _MM()

    @staticmethod
    def PointBased(*a, **k):
        return _MM()

    @staticmethod
    def GetStageMetersPerUnit(stage):
        return 1.0

    @staticmethod
    def SetStageMetersPerUnit(stage, v):
        return True

    @staticmethod
    def SetStageUpAxis(stage, v):
        return True

    def __getattr__(self, name):
        return _MM()


class _GfMod(object):
    Vec2f = _Vec
    Vec3f = _Vec
    Vec3d = _Vec
    Vec4f = _Vec
    Vec3h = _Vec

    def __getattr__(self, name):
        return _MM()


def _install():
    """`pxr`·`omni`·`carb`·`isaacsim` 을 가짜로 갈아끼운다."""
    pxr = _ty.ModuleType("pxr")
    pxr.UsdGeom = _UsdGeomMod()
    pxr.Gf = _GfMod()
    for n in ("Usd", "UsdShade", "Sdf", "UsdPhysics", "UsdLux", "Vt",
              "UsdUtils", "Tf", "Kind", "Ar"):
        setattr(pxr, n, _MM())
    _sys.modules["pxr"] = pxr
    for n in ("Usd", "UsdShade", "Sdf", "UsdPhysics", "UsdLux", "Vt",
              "UsdGeom", "Gf"):
        _sys.modules["pxr." + n] = getattr(pxr, n)

    class _Finder(object):
        ROOTS = ("omni", "carb", "isaacsim", "omni.kit", "pxr")

        def find_module(self, name, path=None):
            return self if self._mine(name) else None

        @staticmethod
        def _mine(name):
            head = name.split(".")[0]
            return head in ("omni", "carb", "isaacsim")

        def load_module(self, name):
            if name in _sys.modules:
                return _sys.modules[name]
            m = _MM()
            m.__name__ = name
            m.__path__ = []
            m.__loader__ = self
            m.__spec__ = None
            _sys.modules[name] = m
            return m

        # PEP 451
        def find_spec(self, name, path=None, target=None):
            if not self._mine(name):
                return None
            import importlib.machinery as _im
            return _im.ModuleSpec(name, self, is_package=True)

        def create_module(self, spec):
            m = _MM()
            m.__name__ = spec.name
            m.__path__ = []
            return m

        def exec_module(self, module):
            return None

    _sys.meta_path.insert(0, _Finder())


def reset():
    _PRIMS.clear()


def inventory():
    """정렬된 프림 인벤토리 — 경로·타입·xform·형상 속성·참조."""
    rows = []
    for rec in _PRIMS.values():
        rows.append("%s|%s|%s|%s|%s" % (
            rec["path"], rec["type"],
            ";".join("%s=%s" % (k, v) for k, v in rec["ops"]),
            ";".join("%s=%s" % (k, rec["attrs"][k])
                     for k in sorted(rec["attrs"])),
            ",".join(rec["refs"])))
    rows.sort()
    return rows
'''

# ---------------------------------------------------------------------------
# 워커 — 한 팔(arm) 안에서 33씬을 순서대로 조립하고 해시를 뱉는다
# ---------------------------------------------------------------------------
_WORKER = r'''
import json, os, random, sys, traceback
sys.dont_write_bytecode = True
REPO = %(repo)r
sys.path.insert(0, os.path.join(REPO, "scenes", "batch1"))
sys.path.insert(0, os.path.join(REPO, "scenes", "main"))
sys.path.insert(0, REPO)

_fake = {}
exec(compile(%(fake)r, "<fakeusd>", "exec"), _fake)
_fake["_install"]()

import hashlib
import importlib.util
from unittest.mock import MagicMock

import scene_common as sc

# 조립만 하고 렌더·부팅·EXR 파생은 전부 잘라낸다(GPU 0 · 디스크 쓰기 0).
sc.boot = lambda headless=True: MagicMock()
sc.capture_pipeline = lambda *a, **k: None
sc.ensure_noon_lookfix = lambda p: p
sc.check_assets = lambda *a, **k: None

os.environ["NEGOBS_CAPTURE"] = "1"

SCENES = json.loads(%(scenes)r)
out = {"arm": os.environ.get("_ARM", "?"),
       "flags": {"LOOK_V1": sc.LOOK_V1, "LOOK_MTL": sc.LOOK_MTL,
                 "LOOK_GEO": sc.LOOK_GEO},
       "scenes": {}}

for path in SCENES:
    name = os.path.splitext(os.path.basename(path))[0].split("_")[0]
    _fake["reset"]()
    random.seed(0)                      # 전역 RNG 오염 차단(씬 순서 무관하게)
    try:
        spec = importlib.util.spec_from_file_location(
            "negobs_scene_" + name, path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
        if hasattr(mod, "_ensure_noon_lookfix"):
            mod._ensure_noon_lookfix = lambda p: p      # scene01 로컬 사본
        if hasattr(mod, "check_assets"):
            mod.check_assets = lambda *a, **k: None
        mod.main()
        inv = _fake["inventory"]()
        h = hashlib.blake2b("\n".join(inv).encode(), digest_size=16).hexdigest()
        out["scenes"][name] = {"hash": h, "n": len(inv)}
        if os.environ.get("_DUMP_INV"):
            out["scenes"][name]["inv"] = inv
    except SystemExit as e:
        out["scenes"][name] = {"error": "SystemExit(%%s)" %% e.code}
    except Exception as e:
        out["scenes"][name] = {"error": "%%s: %%s" %% (type(e).__name__, e),
                               "tb": traceback.format_exc()[-1200:]}

sys.stdout.write("@@JSON@@" + json.dumps(out))
'''


def _scene_files(filt=None):
    out = []
    for sub in ("main", "batch1"):
        for p in sorted(glob.glob(os.path.join(REPO, "scenes", sub, "scene*.py"))):
            b = os.path.basename(p)
            if b in ("scene_common.py",) or os.path.islink(p):
                continue
            name = os.path.splitext(b)[0].split("_")[0]
            if filt and name not in filt:
                continue
            out.append(p)
    return out


def run_arm(label, env_over, scenes, dump=False, timeout=1800):
    """한 팔을 서브프로세스로 돌린다 — 모듈 최상단에서 플래그를 읽으므로
    팔마다 **새 인터프리터**가 아니면 안 된다."""
    env = dict(os.environ)
    for k in ("NEGOBS_LOOK_V1", "NEGOBS_LOOK_MTL", "NEGOBS_LOOK_GEO"):
        env.pop(k, None)
    env.update(env_over)
    env["_ARM"] = label
    env["PYTHONHASHSEED"] = "0"
    if dump:
        env["_DUMP_INV"] = "1"
    src = _WORKER % dict(repo=REPO, fake=_FAKE,
                         scenes=json.dumps(scenes))
    p = subprocess.run([sys.executable, "-c", src], cwd=REPO, env=env,
                       capture_output=True, text=True, timeout=timeout)
    tag = "@@JSON@@"
    if tag not in p.stdout:
        print(f"[{label}] 하네스 실패 — stdout 말미:\n{p.stdout[-2000:]}")
        print(f"[{label}] stderr 말미:\n{p.stderr[-2000:]}")
        return None
    return json.loads(p.stdout.split(tag, 1)[1])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--assert-no-residual-lookv1", action="store_true",
                    help="R-5 만 검사하고 종료")
    ap.add_argument("--scenes", default="", help="쉼표 구분 씬 이름 필터")
    ap.add_argument("--baseline", default="",
                    help="기준선 해시 JSON 을 이 경로에 기록")
    ap.add_argument("--dump-inv", action="store_true",
                    help="불일치 씬의 인벤토리 diff 를 출력")
    ap.add_argument("--skip-r6", action="store_true")
    a = ap.parse_args()

    print("=" * 72)
    print("기하 불변 검사 — R-5 → R-4 → R-6  (GPU 0)")
    print("=" * 72)

    bad, _allowed = check_residual_lookv1()
    if bad:
        print("\n[R-5] ✗ FAIL — 잔존 `LOOK_V1` 참조가 있다. 치환 누락이다.")
        return 1
    print("[R-5] ✔ PASS — 호환 심 밖의 `LOOK_V1` 참조 0\n")
    if a.assert_no_residual_lookv1:
        return 0

    filt = set(x.strip() for x in a.scenes.split(",") if x.strip())
    scenes = _scene_files(filt or None)
    print(f"[대상] 씬 {len(scenes)}개")

    arms = [("mtl0", dict(NEGOBS_LOOK_MTL="0", NEGOBS_LOOK_GEO="1")),
            ("mtl1", dict(NEGOBS_LOOK_MTL="1", NEGOBS_LOOK_GEO="1"))]
    if not a.skip_r6:
        arms.append(("v1", dict(NEGOBS_LOOK_V1="1")))

    res = {}
    for label, envo in arms:
        print(f"[실행] arm={label} {envo}")
        r = run_arm(label, envo, scenes, dump=a.dump_inv)
        if r is None:
            return 2
        res[label] = r
        errs = {k: v["error"] for k, v in r["scenes"].items() if "error" in v}
        print(f"   → 조립 {len(r['scenes']) - len(errs)}/{len(r['scenes'])} 성공"
              f" · 플래그 {r['flags']}")
        for k, v in errs.items():
            print(f"     ✗ {k}: {v}")
            if a.dump_inv and "tb" in r["scenes"][k]:
                print(r["scenes"][k]["tb"])
        if errs:
            print("[하네스] 조립 실패 씬이 있다 — 판정 불가")
            return 2

    names = sorted(res["mtl0"]["scenes"])
    fail4, fail6 = [], []
    for n in names:
        h0 = res["mtl0"]["scenes"][n]["hash"]
        h1 = res["mtl1"]["scenes"][n]["hash"]
        if h0 != h1:
            fail4.append(n)
        if not a.skip_r6:
            hv = res["v1"]["scenes"][n]["hash"]
            if hv != h1:
                fail6.append(n)

    print("\n" + "-" * 72)
    print(f"{'씬':<10}{'프림':>7}  {'MTL=0':<10}{'MTL=1':<10}"
          f"{'' if a.skip_r6 else 'V1=1':<10}판정")
    print("-" * 72)
    for n in names:
        s0, s1 = res["mtl0"]["scenes"][n], res["mtl1"]["scenes"][n]
        hv = "" if a.skip_r6 else res["v1"]["scenes"][n]["hash"][:8]
        ok = (n not in fail4) and (n not in fail6)
        print(f"{n:<10}{s1['n']:>7}  {s0['hash'][:8]:<10}{s1['hash'][:8]:<10}"
              f"{hv:<10}{'✔' if ok else '✗'}")
    print("-" * 72)
    print(f"[R-4] MTL 0/1 해시 일치 {len(names) - len(fail4)}/{len(names)}"
          f"  {'✔ PASS' if not fail4 else '✗ FAIL ' + ','.join(fail4)}")
    if not a.skip_r6:
        print(f"[R-6] V1=1 3자 일치   {len(names) - len(fail6)}/{len(names)}"
              f"  {'✔ PASS' if not fail6 else '✗ FAIL ' + ','.join(fail6)}")

    if a.baseline:
        payload = {
            "note": "T1 §1.7.2 R-4/R-6 기준선 — 프림 인벤토리 해시(GPU 0)",
            "repo_head": subprocess.run(
                ["git", "rev-parse", "HEAD"], cwd=REPO,
                capture_output=True, text=True).stdout.strip(),
            "arms": {k: {n: v["scenes"][n]["hash"] for n in names}
                     for k, v in res.items()},
            "n_prims": {n: res["mtl1"]["scenes"][n]["n"] for n in names},
        }
        os.makedirs(os.path.dirname(os.path.join(REPO, a.baseline)) or ".",
                    exist_ok=True)
        with open(os.path.join(REPO, a.baseline), "w") as fh:
            json.dump(payload, fh, indent=1, ensure_ascii=False)
        print(f"[기준선] 기록 → {a.baseline}")

    return 1 if (fail4 or fail6) else 0


if __name__ == "__main__":
    sys.exit(main())
