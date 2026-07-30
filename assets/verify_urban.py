#!/usr/bin/env python3
"""W3 도시 에셋 검증기 — 지오메트리 실측 + 픽셀 규약 검사.

`download_urban.py --verify` 가 부른다. 단독 실행도 된다:

    /tmp/usdvenv/bin/python assets/verify_urban.py             # 전체
    /tmp/usdvenv/bin/python assets/verify_urban.py --only signs_kr
    /tmp/usdvenv/bin/python assets/verify_urban.py --sheet     # 표지판 컨택트시트

결과는 `assets/urban_manifest_w3.json` 의 각 자산 항목에 병합된다
(`geometry` · `pixels` · `verdict` · `quirks`). GPU·Isaac·렌더 미사용.

────────────────────────────────────────────────────────────────────────────
검사 항목
────────────────────────────────────────────────────────────────────────────
1. **구조** — USD/PNG/JPEG/MDL 헤더 바이트. usd-core 가 없어도 도는 최소 보증.
2. **로드** — usd-core 로 스테이지를 실제로 열고, 프림·메시가 나오는지 본다.
   4 파일 체인이 깨지면 여기서 `tri_unique = 0` 으로 잡힌다 (래퍼만 받았을 때의
   전형적 증상). Isaac 이 없어도 구성(composition)은 동일하게 평가된다.
3. **quirks** — `metersPerUnit`, bbox, `zmin`, 재질별 삼각형 점유율, **z_advice**.
   ⚠ 접지 판정을 bbox 의 zmin 으로 하면 안 된다. `typical_building_10` 의 전체
   zmin 은 −7.904 m 지만 그건 **기초 박스**가 내려간 값이고, 그 다음으로 낮은
   메시는 z=+0.096 에서 시작한다 [측정]. +7.904 를 들어 올리면 파사드가 공중에
   뜬다. 그래서 판정 근거를 **"지면 아래 삼각형 비율"** 로 잡았고, `typical_building_*`
   10동 전수에서 그 값이 **0.0 %** 로 나왔다 — 즉 이 tier 는 **로컬 z=0 이 노면**이
   라는 라이브러리 관행이 있고, R1 §6.5 의 Z 보정표는 tb10 한 줄이 아니라
   **tier 전체가 틀렸다**.
4. **픽셀** — 프로젝트 규약 3종. 판정 기준은 전수 1회전을 돌려 보고 교정했다:
   (a) **계절 규약** — 식생 자산에 벚꽃·단풍·황변 금지.
       gate_woody: 초록(65~170°)+황록(40~65°) ≥ 0.75 AND 적+분홍+주황 ≤ 0.06
                   AND (황록 우세면 선형 알베도 ≤ 0.55)
       gate_turf : 초록+황록 ≥ 0.75 AND 적+분홍 ≤ 0.02 AND 주황 ≤ 0.25
       (veg_manifest_w2.json 과 **같은 정의** — 두 원장이 비교 가능해야 한다.)
       판정에는 **그 텍스처를 실제로 무는 메시의 삼각형 점유율**을 붙인다.
       폴더에 있으나 아무 메시도 물지 않는 아틀라스는 `UNBOUND` 로 기록만 한다.
   (b) **대면적 근백색 금지** — 선형 휘도 > 0.8 화소 비율(상한 5 %). 지면 규약의
       `wht%` (B30 < 2 %) 와 알베도 상한 0.8 을 텍스처 레벨로 옮긴 것.
       벽·플라스터·석재 등 **대면적 컬러맵**에만 적용한다 — 러프니스/노멀/ORM 은
       밝기가 재질 파라미터지 알베도가 아니므로 `NON_COLOR_PAT` 로 제외한다.
   (c) **표지판 판면 가독** — `max(px) ≥ 1024 AND min(px) ≥ 256 AND n_tone ≥ 2
       AND glyph_frac ≥ 0.005`. 게이트는 **그 표지판 자신의 판면 텍스처**에만 건다
       (지주 재질 라이브러리를 판면으로 오인하면 156면이 통째로 FAIL 이 된다).
       `contrast < 60` 은 VMS/발광 판면이면 WARN — 확산맵이 검은 것이 설계다.
"""
import json
import math
import os
import sys

ASSETS_DIR = os.path.dirname(os.path.abspath(__file__))
URBAN_DIR = os.path.join(ASSETS_DIR, "urban")
CC0_DIR = os.path.join(ASSETS_DIR, "urban_cc0")
MANIFEST_PATH = os.path.join(ASSETS_DIR, "urban_manifest_w3.json")
VERIFY_DIR = os.path.join(URBAN_DIR, "_verify")     # gitignored

# 대면적 근백색 검사를 걸 텍스처 이름 패턴 (벽·바닥·석재·플라스터)
LARGE_SURFACE_PAT = ("wall", "plaster", "concrete", "brick", "stone", "roof",
                     "facade", "building", "paving", "granite", "tile")
# **색이 아닌** 맵. 색 규약(계절·근백색)은 여기 걸리면 적용하지 않는다.
# 러프니스/노멀/ORM 은 밝기가 재질 파라미터지 알베도가 아니다 —
# `brick_wall_001_Roughness.png` 를 근백색으로 잡은 오탐이 실제로 났다 [측정].
NON_COLOR_PAT = ("_n.", "_nor", "normal", "_orm", "_r.", "rough", "_m.",
                 "metallic", "specular", "_ao", "opacity", "_mask", "_s.",
                 "displacement", "_disp", "_arm", "height", "alpha")
# ("alpha" 는 "albedo" 와 겹치지 않는다 — 두 글자가 다르다. 확인했다.)
NEAR_WHITE_CAP = 0.05        # 선형휘도>0.8 화소 비율 상한 (대면적)
# 식생 자산 판별
# 계절 게이트는 **잎 색** 규약이다. 그루터기·통나무처럼 잎이 없는 목질 자산에
# 걸면 범주 오류가 된다(나무는 사철 갈색이다) — `tree_stump_01/02` 가 그렇게
# 잡혔다 [측정: green+yg 0.13~0.22]. 잎을 가진 자산만 넣는다.
VEG_PAT = ("veg_shrub", "veg_grass", "veg_tree", "sct_debris_leaves",
           "sct_leaf", "shrub", "grass_clump")
TURF_PAT = ("grass", "clump", "turf", "lawn")
# 낙엽·마른잎처럼 **계절이 곧 콘텐츠**인 자산. 계절 게이트 FAIL 이 곧 불합격이
# 아니라 "쓸 수 있는 씬이 제한된다" 는 뜻이다.
SEASON_SCOPED_PAT = ("leaves_dry", "leaf_pile", "debris_leaves", "fallcluster")


def is_season_scoped(aid):
    return any(p in aid for p in SEASON_SCOPED_PAT)


# ════════════════════════════════════════════════════════════════════════════
# 픽셀
# ════════════════════════════════════════════════════════════════════════════
def _srgb_to_linear(a):
    import numpy as np
    a = a.astype("float32") / 255.0
    return np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)


def tex_stats(path, max_side=1024):
    """텍스처 1장 → 색상각 분포 · 선형 알베도 · 근백색 비율 · 가독 지표."""
    import numpy as np
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None
    try:
        im = Image.open(path)
        im.load()
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}
    px = list(im.size)
    if im.mode not in ("RGB", "RGBA", "L"):
        im = im.convert("RGB")
    alpha = None
    if im.mode == "RGBA":
        alpha = np.asarray(im.split()[-1])
        im = im.convert("RGB")
    elif im.mode == "L":
        im = im.convert("RGB")
    if max(im.size) > max_side:
        s = max_side / max(im.size)
        im = im.resize((max(1, int(im.size[0] * s)), max(1, int(im.size[1] * s))),
                       Image.LANCZOS)
        if alpha is not None:
            from PIL import Image as _I
            alpha = np.asarray(_I.fromarray(alpha).resize(im.size, _I.LANCZOS))
    rgb = np.asarray(im)
    lin = _srgb_to_linear(rgb)
    lum = 0.2126 * lin[..., 0] + 0.7152 * lin[..., 1] + 0.0722 * lin[..., 2]
    mask = np.ones(lum.shape, bool) if alpha is None else (alpha > 8)
    if mask.sum() == 0:
        mask = np.ones(lum.shape, bool)

    # HSV (채도 > 0.15 만 유채색으로 센다 — veg 규약과 동일)
    mx = rgb.max(2).astype("float32")
    mn = rgb.min(2).astype("float32")
    d = mx - mn
    sat = np.where(mx > 0, d / np.maximum(mx, 1e-6), 0.0)
    r, g, b = (rgb[..., i].astype("float32") for i in range(3))
    hue = np.zeros_like(mx)
    nz = d > 0
    with np.errstate(invalid="ignore"):
        h_r = ((g - b) / np.where(d == 0, 1, d)) % 6
        h_g = (b - r) / np.where(d == 0, 1, d) + 2
        h_b = (r - g) / np.where(d == 0, 1, d) + 4
    hue = np.where(mx == r, h_r, np.where(mx == g, h_g, h_b)) * 60.0
    hue = np.where(nz, hue % 360.0, 0.0)

    chroma = mask & (sat > 0.15)
    n = int(chroma.sum())

    def frac(sel):
        return round(float((chroma & sel).sum()) / n, 4) if n else 0.0

    bands = {
        "green": frac((hue >= 65) & (hue < 170)),
        "yellow_green": frac((hue >= 40) & (hue < 65)),
        "orange": frac((hue >= 25) & (hue < 40)),
        "red": frac((hue < 25) | (hue >= 340)),
        "pink": frac((hue >= 280) & (hue < 340)),
        "cyan_blue": frac((hue >= 170) & (hue < 280)),
    }
    out = {"px": px, "chroma_px": n, "hue": bands,
           "albedo_lin": round(float(lum[mask].mean()), 4),
           "near_white_frac": round(float((lum[mask] > 0.8).mean()), 4),
           "w80_srgb": round(float(((rgb[mask].astype("float32") @
                                     [0.2126, 0.7152, 0.0722]) / 255 > 0.8).mean()), 4)}
    # 가독 지표 (표지판용이지만 전 텍스처에 싸게 낼 수 있다)
    y = (rgb.astype("float32") @ [0.2126, 0.7152, 0.0722])
    gy = np.abs(np.diff(y, axis=0)).mean() if y.shape[0] > 1 else 0.0
    gx = np.abs(np.diff(y, axis=1)).mean() if y.shape[1] > 1 else 0.0
    out["edge"] = round(float((gx + gy) / 2), 3)
    out["contrast"] = round(float(np.percentile(y[mask], 95) -
                                  np.percentile(y[mask], 5)), 1)
    out["ink_frac"] = round(float((lum[mask] < 0.06).mean()), 4)
    # `n_tone` = 32-bin 휘도 히스토그램에서 **1 % 이상** 차지하는 계조 수.
    # 판면이 비었으면(단색 판 + 테두리) 1~2, 실제 표지판이면 ≥3 이 나온다.
    # 에지밀도만으로는 안 된다 — 삼각 주의표지처럼 넓은 단색 면이 지배하는
    # 판면은 글리프가 또렷해도 edge 가 1.0 아래로 희석된다 [측정: sign_kr101
    # edge 0.843 인데 contrast 255 · ink 6.3 % 로 명백히 가독].
    hist, _ = np.histogram(y[mask], bins=32, range=(0, 255))
    out["n_tone"] = int((hist / max(1, hist.sum()) >= 0.01).sum())
    # `glyph_frac` = 판면의 **최빈 계조에서 멀리 떨어진** 화소 비율.
    # 어두운 잉크(`ink_frac`)만 세면 **파란 원판 위의 흰 화살표**(지시표지
    # kr305~kr316·kr332)가 전부 "빈 판면" 으로 오판된다 — 실제로 그렇게
    # 오판됐다 [측정: 13/158 오탐]. 최빈값 기준이면 밝은 글리프도 잡힌다.
    mode = int(np.argmax(hist))
    far = np.abs((y[mask] / 8.0) - mode) >= 8      # 8 bin = 64 luma
    out["glyph_frac"] = round(float(far.mean()), 4)
    return out


def gate_woody(s):
    h = s["hue"]
    gg = h["green"] + h["yellow_green"]
    warm = h["red"] + h["pink"] + h["orange"]
    if gg < 0.75:
        return "FAIL", f"green+yg {gg:.3f} < 0.75"
    if warm > 0.06:
        return "FAIL", f"red+pink+orange {warm:.3f} > 0.06"
    if h["yellow_green"] > 0.5 and s["albedo_lin"] > 0.55:
        return "FAIL", f"황록 우세 + albedo_lin {s['albedo_lin']:.3f} > 0.55 (가을 황변)"
    return "PASS", ""


def gate_turf(s):
    h = s["hue"]
    gg = h["green"] + h["yellow_green"]
    if gg < 0.75:
        return "FAIL", f"green+yg {gg:.3f} < 0.75"
    if h["red"] + h["pink"] > 0.02:
        return "FAIL", f"red+pink {h['red']+h['pink']:.3f} > 0.02"
    if h["orange"] > 0.25:
        return "FAIL", f"orange {h['orange']:.3f} > 0.25"
    return "PASS", ""


# ════════════════════════════════════════════════════════════════════════════
# 지오메트리 (usd-core)
# ════════════════════════════════════════════════════════════════════════════
def _material_textures(stage, mat_path):
    """머티리얼 프림 아래의 모든 AssetPath 입력 → 텍스처 파일명 집합."""
    from pxr import Usd, Sdf
    out = set()
    prim = stage.GetPrimAtPath(mat_path)
    if not prim:
        return out
    for q in Usd.PrimRange(prim):
        for a in q.GetAttributes():
            try:
                v = a.Get()
            except Exception:
                continue
            vals = ([v] if isinstance(v, Sdf.AssetPath)
                    else list(v) if isinstance(v, Sdf.AssetPathArray) else [])
            for p in vals:
                if p.path:
                    out.add(os.path.basename(p.path))
    return out


def measure(usd_path):
    """스테이지 1개 → mpu · bbox · 메시별 zmin · 삼각형 수 · **재질별 삼각형 점유율**.

    재질별 점유율이 있어야 픽셀 판정이 정직해진다. 한 자산 폴더에 마른 잎
    아틀라스가 들어 있다고 해서 그게 실제로 보이는 메시에 물려 있다는 뜻은
    아니다 [측정: `veg_shrub_hedge_round_01` 은 초록 잎 아틀라스와 주황
    마른-식물 아틀라스를 **둘 다** 담고 있다]. veg_manifest_w2 의 규율
    ("판정은 수종명이 아니라 메시가 실제로 샘플하는 픽셀") 을 그대로 잇는다.
    """
    from pxr import Usd, UsdGeom, UsdShade, Gf
    try:
        stage = Usd.Stage.Open(usd_path)
    except Exception as e:
        return {"error": f"open: {type(e).__name__}: {e}"}
    if stage is None:
        return {"error": "Usd.Stage.Open returned None"}
    mat_tris = {}
    mpu = UsdGeom.GetStageMetersPerUnit(stage)
    # 폴더를 벗어나는 서브레이어 = **별칭(alias)**. `bench_park_05.usd` 는
    # 자기 지오메트리가 없고 `../bench_curved_01/` 을 통째로 물고 온다 [측정].
    # 이걸 모르면 "조달하지 않기로 한 자산" 이 다른 이름으로 트리에 들어온다.
    alias = [x for x in (stage.GetRootLayer().subLayerPaths or [])
             if x.startswith("../")]
    bbc = UsdGeom.BBoxCache(Usd.TimeCode.Default(),
                            ["default", "render", "proxy"], useExtentsHint=False)
    tri_u = 0
    n_mesh = 0
    mesh_z = []
    n_inst = 0
    tri_eff = 0
    protos = {}
    # **인스턴스 프록시까지 순회해야 한다.** `stage.Traverse()` 만 쓰면
    # 크로스폴더 서브레이어 래퍼(`bench_park_01.usd` → `../bench_park_03/…`)가
    # 삼각형 0 으로 나온다 [측정: 0 → 35,396]. `_inst.usd` 를 직접 열 때는
    # 값이 동일해서 이중 계상 위험도 없다 [측정: 21,965 = 21,965].
    for p in Usd.PrimRange.Stage(stage,
                                 Usd.TraverseInstanceProxies(Usd.PrimDefaultPredicate)):
        if p.IsA(UsdGeom.Mesh):
            m = UsdGeom.Mesh(p)
            fvc = m.GetFaceVertexCountsAttr().Get()
            t = sum(max(0, c - 2) for c in (fvc or []))
            tri_u += t
            n_mesh += 1
            protos[p.GetPath().pathString] = t
            try:
                b = UsdShade.MaterialBindingAPI(p).ComputeBoundMaterial()[0]
                if b:
                    mp = b.GetPath().pathString
                    mat_tris[mp] = mat_tris.get(mp, 0) + t
            except Exception:
                pass
            try:
                bb = bbc.ComputeWorldBound(p).ComputeAlignedRange()
                if not bb.IsEmpty():
                    mesh_z.append((bb.GetMin()[2] * mpu, bb.GetMax()[2] * mpu, t))
            except Exception:
                pass
        elif p.IsA(UsdGeom.PointInstancer):
            pi = UsdGeom.PointInstancer(p)
            idx = pi.GetProtoIndicesAttr().Get() or []
            n_inst += len(idx)
            tgts = pi.GetPrototypesRel().GetTargets() or []
            per = []
            for t in tgts:
                s = 0
                pr = stage.GetPrimAtPath(t)
                if pr:
                    for q in Usd.PrimRange(pr):
                        if q.IsA(UsdGeom.Mesh):
                            fvc = UsdGeom.Mesh(q).GetFaceVertexCountsAttr().Get()
                            s += sum(max(0, c - 2) for c in (fvc or []))
                per.append(s)
            for i in idx:
                if 0 <= i < len(per):
                    tri_eff += per[i]
    try:
        wb = bbc.ComputeWorldBound(stage.GetPseudoRoot()).ComputeAlignedRange()
        lo, hi = wb.GetMin(), wb.GetMax()
        size = [round((hi[i] - lo[i]) * mpu, 4) for i in range(3)]
        zmin = round(lo[2] * mpu, 4)
        zmax = round(hi[2] * mpu, 4)
    except Exception:
        size, zmin, zmax = [0, 0, 0], 0.0, 0.0
    out = {"mpu": mpu, "size_m": size, "zmin_m": zmin, "zmax_m": zmax,
           "tri_unique": tri_u, "tri_effective": tri_eff or tri_u,
           "n_instances": n_inst, "n_meshes": n_mesh,
           "n_prims": len(list(stage.Traverse()))}
    out["size_mm"] = [round(v * 1000) for v in size]
    if alias:
        out["cross_folder_sublayer"] = alias
        out["alias_of"] = [a.split("/")[1] for a in alias]
    # 텍스처 → 그 텍스처를 물고 있는 메시의 삼각형 점유율
    if mat_tris and tri_u:
        binds = {}
        for mp, t in mat_tris.items():
            for tex in _material_textures(stage, mp):
                binds[tex] = round(binds.get(tex, 0.0) + t / tri_u, 4)
        out["texture_bindings"] = binds
        # 같은 이름의 머티리얼 프림이 여러 경로에 존재한다(인스턴스 프록시).
        # leaf 이름으로 **합산**해야 한다 — 덮어쓰면 점유율이 통째로 사라진다.
        agg = {}
        for k, v in mat_tris.items():
            agg[k.rsplit("/", 1)[-1]] = agg.get(k.rsplit("/", 1)[-1], 0) + v
        out["material_tris"] = dict(sorted(agg.items(), key=lambda x: -x[1]))
        out["material_tri_sum"] = sum(agg.values())
    # ── 접지(Z) 판정 ────────────────────────────────────────────────────
    # bbox 의 zmin 을 그대로 접지 보정에 쓰면 안 된다. dsready 건물군은
    # **로컬 z=0 이 노면**이고 기초/지하층 박스가 그 아래로 −1 ~ −10 m 뻗어
    # 있는 것이 라이브러리 관행이다 [측정: typical_building_* 10동 전수].
    # 판정 근거는 "zmin 이 음수인가" 가 아니라 **삼각형의 몇 %가 지면 아래인가**다.
    if mesh_z:
        zs = sorted(z for z, _, _ in mesh_z)
        tri_tot = sum(t for _, _, t in mesh_z) or 1
        below = sum(t for zlo, zhi, t in mesh_z if zhi < -0.05)
        frac = below / tri_tot
        out["mesh_zmin_min_m"] = round(zs[0], 4)
        out["mesh_zmin_2nd_m"] = round(zs[1] if len(zs) > 1 else zs[0], 4)
        out["tri_below_grade_frac"] = round(frac, 4)
        out["foundation_outlier"] = bool(zmin < -0.5 and frac < 0.25)
        if zmin > 0.01:
            out["z_advice"] = (
                f"zmin {zmin:+.3f} m — **부속물**이다(모체 자산 위에 얹힌다). "
                f"단독 접지 금지.")
        elif zmin >= -0.01:
            out["z_advice"] = "zmin ≈ 0 — 접지 보정 불필요."
        elif frac < 0.25:
            out["z_advice"] = (
                f"zmin {zmin:+.3f} m 이지만 지면 아래 삼각형은 전체의 "
                f"{frac*100:.1f} % 뿐이다(기초/지하 박스). **로컬 z=0 이 노면** — "
                f"**Z 보정 금지**(올리면 파사드가 뜬다).")
        else:
            out["z_advice"] = (
                f"zmin {zmin:+.3f} m, 지면 아래 삼각형 {frac*100:.1f} % — "
                f"원점이 실제로 아래에 있다. 접지 시 +{-zmin:.3f} m 올릴 것.")
    return out


# ════════════════════════════════════════════════════════════════════════════
# 실행
# ════════════════════════════════════════════════════════════════════════════
def _local(asset, k):
    root = CC0_DIR if asset.get("source") == "polyhaven" else URBAN_DIR
    return os.path.join(root, k.get("key") or k["rel"])


def _root_local(asset):
    """측정 대상 레이어.

    ⚠ dsready 자산은 **래퍼가 아니라 `_inst.usd` 를 재야 한다.** 래퍼를
    `Usd.Stage.Open` 하면 인스턴스 프록시가 구성되지 않아 `typical_building_10`
    이 21,965 이 아니라 **504 tri** 로 나온다 [측정]. 그리고 `_inst.usd` 는
    실제 `shared_textures/` 오버라이드를 들고 있는 레이어이기도 하므로,
    W3 배치기가 참조해야 할 대상도 이쪽이다(building A/B §7.3-5 와 동일 결론).
    """
    if asset.get("source") == "polyhaven":
        return os.path.join(CC0_DIR, asset["keys"][0]["rel"])
    rk = asset["root_key"]
    if rk.endswith(".usd"):
        inst = os.path.join(URBAN_DIR, rk[:-4] + "_inst.usd")
        if os.path.exists(inst):
            return inst
    return os.path.join(URBAN_DIR, rk)


def run(man, only=None, sheet=False):
    if not man:
        print("매니페스트가 없다. `download_urban.py --resolve` 먼저.")
        sys.exit(2)
    assets = man["assets"] + man.get("polyhaven", [])
    if only:
        assets = [a for a in assets if a["group"] in only]
    os.makedirs(VERIFY_DIR, exist_ok=True)

    tally = {"PASS": 0, "WARN": 0, "FAIL": 0, "SKIP": 0}
    sign_rows = []
    print(f"검증 대상 {len(assets)} 자산")
    for a in assets:
        rp = _root_local(a)
        if not rp.endswith((".usd", ".usda", ".usdc")) or not os.path.exists(rp):
            a["verdict"] = "SKIP"
            a["verdict_reason"] = "USD 루트 없음(재질 라이브러리 등)"
            tally["SKIP"] += 1
            continue
        # 재질/셰이더 라이브러리(`nv_core/materials/**`)는 **지오메트리가 없는
        # 것이 정상**이다. 표지판 6종 재질 USD 를 지오메트리 자산으로 재면
        # tri 0 → FAIL 이 되고, 빈 bbox 때문에 치수도 쓰레기값이 나온다 [측정].
        if a.get("root_key", "").startswith("nv_core/materials/"):
            a.pop("geometry", None)      # 빈 bbox 쓰레기값을 원장에 남기지 않는다
            a.pop("pixels", None)
            a["verdict"] = "SKIP"
            a["verdict_reason"] = "재질 라이브러리 — 지오메트리 없음이 정상"
            tally["SKIP"] += 1
            print(f" [-] {a['id'][:44]:44s} 재질 라이브러리(지오메트리 없음)")
            continue
        g = measure(rp)
        a["geometry"] = g
        notes = []
        verdict = "PASS"
        if g.get("error"):
            verdict, notes = "FAIL", [g["error"]]
        elif g.get("tri_unique", 0) == 0 and g.get("tri_effective", 0) == 0:
            verdict, notes = "FAIL", ["삼각형 0 — 체인이 끊겼다(래퍼만 받았을 때의 증상)"]

        # ── 픽셀 ────────────────────────────────────────────────────────
        # `.dds` 를 빼면 안 된다 — `props_vegetation/` 의 잎 아틀라스는 전부
        # DDS 라서, 확장자 목록에서 누락하면 **식생 계절 게이트가 통째로
        # 무음 통과한다**. 실제로 그렇게 통과했다 [측정]. PIL 은 DDS 를 읽는다.
        texs = [k for k in a["keys"]
                if (k.get("key") or k["rel"]).lower().endswith(
                    (".png", ".jpg", ".jpeg", ".dds", ".tga"))]
        aid = a["id"].lower()
        is_veg = any(p in aid for p in VEG_PAT)
        is_sign = aid.startswith("sign_kr") or aid.startswith("stencil_ko")
        pixels = []
        for k in texs[:24]:
            p = _local(a, k)
            if not os.path.exists(p):
                continue
            s = tex_stats(p)
            s["tex"] = os.path.basename(p)
            if s.get("error"):
                pixels.append(s)
                continue
            name = s["tex"].lower()
            # 이 텍스처를 실제로 물고 있는 메시의 삼각형 점유율.
            # None = 바인딩을 못 읽음(측정 실패), 0.0 = 폴더에 있으나 미사용.
            s["bound_tri_frac"] = (g.get("texture_bindings") or {}).get(s["tex"])
            unbound = (g.get("texture_bindings") is not None
                       and not s["bound_tri_frac"])
            # (a) 계절 규약
            if is_veg and not any(x in name for x in NON_COLOR_PAT):
                gate = "turf" if any(t in aid for t in TURF_PAT) else "woody"
                v, why = (gate_turf if gate == "turf" else gate_woody)(s)
                s["gate"] = gate
                s["gate_verdict"] = v
                if v == "FAIL" and unbound:
                    # 폴더에 있지만 어떤 메시도 물지 않는 아틀라스. 렌더에
                    # 나오지 않으므로 자산을 죽이지 않는다 — 기록만 한다.
                    s["gate_verdict"] = "UNBOUND"
                    s["gate_reason"] = why
                    notes.append(f"미바인딩 아틀라스 — {s['tex']}: {why} "
                                 f"(메시 점유 0 %, 렌더에 나오지 않음)")
                elif v == "FAIL" and is_season_scoped(aid):
                    # 낙엽 자체가 콘텐츠인 자산(마른 잎 산포·낙엽 더미)은 계절
                    # 게이트로 죽이는 게 아니라 **씬을 제한**한다. R1 §5.3 이
                    # sct_leaf_pile 을 C2(낙엽 씬) 한정으로 스코프한 것과 같은 처분.
                    s["gate_verdict"] = "SEASON_SCOPED"
                    s["gate_reason"] = why
                    if verdict == "PASS":
                        verdict = "WARN"
                    notes.append(
                        f"계절 특정 자산 — {s['tex']}: {why}. **낙엽 씬 한정** "
                        f"(C2·07·10·D3). 상록/봄여름 씬 배치 금지.")
                elif v == "FAIL":
                    s["gate_reason"] = why
                    share = s["bound_tri_frac"]
                    verdict = "FAIL"
                    notes.append(
                        f"계절 규약 {gate} FAIL — {s['tex']}: {why}"
                        + (f" (메시 점유 {share*100:.1f} %)" if share else ""))
            # (b) 대면적 근백색
            if (any(x in name for x in LARGE_SURFACE_PAT)
                    and not any(x in name for x in NON_COLOR_PAT)):
                if s["near_white_frac"] > NEAR_WHITE_CAP:
                    s["near_white_verdict"] = "WARN"
                    if verdict == "PASS":
                        verdict = "WARN"
                    notes.append(
                        f"대면적 근백색 {s['tex']}: 선형휘도>0.8 화소 "
                        f"{s['near_white_frac']*100:.1f} % > {NEAR_WHITE_CAP*100:.0f} % "
                        f"(알베도 {s['albedo_lin']:.3f})")
                else:
                    s["near_white_verdict"] = "PASS"
            # (c) 표지판 판면
            # 표지판 게이트는 **그 표지판 자신의 판면**에만 건다. 지주/배면
            # 재질 라이브러리(`metal__steel_galvanized_basecolor.png` 512²)를
            # 판면으로 오인해 156면 전부를 FAIL 로 만든 오탐이 실제로 났다 [측정].
            if is_sign and os.path.basename(p)[:-4].startswith(a["id"]):
                # 판정 기준은 156면 전수를 한 번 돌려 보고 교정했다 [측정]:
                #  · `min(px) ≥ 512` 는 틀렸다 — `sign_krroadname` 은 2048×463
                #    의 **가로로 긴 도로명판**이고 판면은 멀쩡하다. 짧은 변이
                #    아니라 **긴 변**이 해상도를 지배한다.
                #  · `n_tone ≥ 3` 도 틀렸다 — 흑백 2색 규제표지(kr4xx 다수)는
                #    1 % 이상 차지하는 계조가 2 개뿐인데 ink 0.25~0.31 로 명백히
                #    가독이다. 진짜 빈 판면은 계조 1 개다.
                #  · **잉크 비율만으로도 안 된다** — 남색/녹색 바탕에 흰 글씨인
                #    이정표(`krroadname`, `kr410_*`)는 ink ≈ 0 이지만 edge 4~5 다.
                #    "어두운 글리프" 와 "밝은 글리프" 를 둘 다 잡으려면 OR 이어야 한다.
                bad = []
                if max(s["px"]) < 1024 or min(s["px"]) < 256:
                    bad.append(f"해상도 {s['px']} (긴변<1024 또는 짧은변<256)")
                if s["n_tone"] < 2:
                    bad.append(f"계조 {s['n_tone']} < 2 (단색 판면 — 비었다)")
                if s["glyph_frac"] < 0.005:
                    bad.append(f"글리프 {s['glyph_frac']:.4f} < 0.005 (판면이 비었다)")
                # 대비 미달은 **가변정보표지(VMS)** 에서 정상이다: 확산맵이 검고
                # 발광 채널이 글자를 켠다(`sign_kr224_110{,_emissive}`) [측정].
                # 이런 판은 불합격이 아니라 "발광 재질 바인딩 필요" 로 표시한다.
                if s["contrast"] < 60:
                    if "emissive" in name or "vms" in aid or "_110" in name:
                        s["vms_emissive"] = True
                        if verdict == "PASS":
                            verdict = "WARN"
                        notes.append(
                            f"VMS/발광 판면 — {s['tex']}: 확산 대비 "
                            f"{s['contrast']:.0f} (설계상 어둡다). **발광 재질 "
                            f"바인딩 없이는 판독 불가**.")
                    else:
                        bad.append(f"대비 {s['contrast']:.0f} < 60")
                s["legible"] = not bad
                if bad:
                    s["legible_reason"] = "; ".join(bad)
                    verdict = "FAIL"
                    notes.append(f"판면 가독 FAIL — {s['tex']}: {'; '.join(bad)}")
                sign_rows.append((a["id"], p, s))
            pixels.append(s)
        if pixels:
            a["pixels"] = pixels
        # 감독 판정은 "rivermark 이름 항목 제외" 였다. 그 판정은
        # `rivermark_plaza_bldg_*` **자산**을 겨눈 것이고, 아래는 일반 Content
        # 루트의 **공유 텍스처**가 전이 종속으로 딸려 온 것이다(경로 기준
        # Limited Use 범위 밖). 이름 기준으로 막으면 재질이 조용히 깨지므로
        # 막지 않고 **명시적으로 기록**해 감독이 판단하게 한다.
        rm = sorted({(k.get("key") or k["rel"]).rsplit("/", 1)[-1]
                     for k in a["keys"]
                     if "rivermark" in (k.get("key") or k["rel"]).lower()})
        if rm:
            a["rivermark_named_transitive"] = rm
            if verdict == "PASS":
                verdict = "WARN"
            notes.append(f"rivermark 이름 공유 텍스처 {len(rm)}건이 전이 종속으로 "
                         f"포함됐다(일반 Content 루트, 경로상 Limited Use 아님) "
                         f"— 감독 확인 필요: {', '.join(rm)}")
        if g.get("alias_of"):
            notes.append(f"**별칭 자산** — 자기 지오메트리 없이 "
                         f"{g['alias_of']} 을 서브레이어로 물고 온다.")
        a["verdict"] = verdict
        if notes:
            a["verdict_notes"] = notes
        tally[verdict] += 1
        flag = {"PASS": " ", "WARN": "!", "FAIL": "X", "SKIP": "-"}[verdict]
        print(f" [{flag}] {a['id'][:44]:44s} mpu {g.get('mpu', 0):<5} "
              f"tri {g.get('tri_unique', 0):>8,} "
              f"{'×'.join(f'{v:.2f}' for v in g.get('size_m', [0, 0, 0]))}"
              + (f"   {notes[0][:70]}" if notes else ""))

    if sheet and sign_rows:
        make_sheet(sign_rows)
    full = {}
    for a in man["assets"] + man.get("polyhaven", []):
        v = a.get("verdict")
        if v:
            full[v] = full.get(v, 0) + 1
    man["verification"] = {
        "date": __import__("time").strftime("%Y-%m-%d"),
        "tool": "usd-core + PIL, CPU only",
        "tally": full or tally,
        "tally_this_run": tally,
        "near_white_cap": NEAR_WHITE_CAP,
        "gates": {"woody": "green+yg ≥ 0.75 AND red+pink+orange ≤ 0.06 "
                           "AND (yg 우세면 albedo_lin ≤ 0.55)",
                  "turf": "green+yg ≥ 0.75 AND red+pink ≤ 0.02 AND orange ≤ 0.25",
                  "sign": "max(px) ≥ 1024 AND min(px) ≥ 256 AND n_tone ≥ 2 "
                          "AND glyph_frac ≥ 0.005; contrast < 60 은 VMS/발광 "
                          "판면이면 WARN, 아니면 FAIL"},
    }
    print(f"\n판정: PASS {tally['PASS']} · WARN {tally['WARN']} · "
          f"FAIL {tally['FAIL']} · SKIP {tally['SKIP']}")
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(man, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"→ {MANIFEST_PATH}")
    return man


def make_sheet(rows, cell=96, cols=16):
    """표지판 판면 컨택트시트 — 사람이 눈으로 한 번 훑기 위한 것."""
    from PIL import Image
    os.makedirs(VERIFY_DIR, exist_ok=True)
    rows = sorted(rows, key=lambda r: r[0])
    n = len(rows)
    r = math.ceil(n / cols)
    sheet = Image.new("RGB", (cols * cell, r * cell), (24, 24, 24))
    for i, (aid, path, _s) in enumerate(rows):
        try:
            im = Image.open(path).convert("RGB")
            im.thumbnail((cell - 4, cell - 4), Image.LANCZOS)
            sheet.paste(im, ((i % cols) * cell + 2, (i // cols) * cell + 2))
        except Exception:
            pass
    out = os.path.join(VERIFY_DIR, "sign_contact_sheet.png")
    sheet.save(out)
    print(f"컨택트시트 {n}장 → {out}")
    return out


if __name__ == "__main__":
    argv = sys.argv[1:]
    only = None
    if "--only" in argv:
        only = [x.strip() for x in argv[argv.index("--only") + 1].split(",")]
    with open(MANIFEST_PATH, encoding="utf-8") as f:
        m = json.load(f)
    run(m, only, sheet="--sheet" in argv)
