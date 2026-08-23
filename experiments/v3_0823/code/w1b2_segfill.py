#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""w1b2_segfill.py — A팔 ID 마스크 백필의 **검사와 설치** (CPU only).

무엇을 하나 (DECISIONS D75 ④ · W1B_REPORT §9 C-2)
-------------------------------------------------
`run_260826_v3a_segfill.sh`가 A팔 816컷을 **같은 씬·시드·밴드·조건·레시피**로
다시 찍어 스크래치 트리에 넣었다(다른 것은 `NEGOBS_SEG_SIDECAR=1
NEGOBS_SEG_STRICT=1` 하나뿐). 이 파일은 씬 프로세스마다

  1. 재렌더물을 정본 A 프레임과 **sha256 대조**하고,
  2. **대응이 실증된** 씬에만 `.idseg.npz`를 정본 프레임 옆에 설치하고,
  3. 하나라도 어긋나면 **설치하지 않고 격리**한다 (`seg_unavailable`).

정본 픽셀을 조용히 갈아치우는 일은 없다 — 재렌더의 PNG·depth·heightmap은
**전부 폐기**하고 마스크만 취한다.

**D75 ④의 "PNG 바이트 동일" 문면은 만족 불가능하다 — 대조 실험으로 실증했다**
------------------------------------------------------------------------
D75 ④는 "재렌더 → **바이트 동일** 검증 → idseg만 채택"이라 적었고, 근거로
W0의 "sha256 재현성 19/19"를 들었다. 그런데 **W0가 잰 19/19는 `heightmap.npy`**
(W0_CUECLS §1 부수 검증)이지 RGB PNG가 아니다. 세그 변경이 **하나도 없는**
대조군으로 직접 쟀다 — `260825_v3w0_cuecls_A`(W0 A팔) vs 정본 `260819_main_on`,
같은 씬·시드·조건·레시피, 19씬 76컷:

    RGB PNG      sha256 동일   **0 / 76**  (평균 |Δ| 0.09–0.91 LSB · 최대 18–77 LSB)
    depth 사이드카 sha256 동일  **73 / 76**  (불일치 3컷은 scene08 하나)
    heightmap.npy sha256 동일  **19 / 19**  (= W0가 인용한 그 수)
    포즈 7키 + cam.eye 차                **0.0** (W0 §1)

즉 **PathTracing RGB는 프로세스 간 비트 재현되지 않는다**(몬테카를로 표본 잡음).
반면 **기하는 비트 재현된다.** 그리고 `instance_id_segmentation` 마스크는
조명·표본 잡음에 **의존하지 않는다** — 기하와 카메라만의 함수다. 그러므로 RGB
바이트는 "이 마스크가 이 정본 프레임의 것인가"의 증거로 **부적합**하고, depth가
그 자리에 정확히 맞는 증거다(계획 §6.1 VG-01 문면을 `cells_raw`+`polar_gt`로
바꾼 W1B_REPORT §8.3과 같은 종류의 정정이다).

⇒ **판정 기준 두 열을 나란히 인쇄하고, 설치는 기하 대응 기준으로 한다.**

    ① D75 문면 (참고 열) : PNG sha256 전 컷 동일
    ② **기하 대응 (설치 판정)** : `heightmap.npy` sha256 동일 **AND** `n_prims`
       동일 **AND** `arm_config` 동일 **AND** 컷별 포즈 7키+`cam.eye` 차 **정확히 0**
       **AND** 컷별 `.depth.npy` sha256 **동일**

②는 ①보다 **약한 기준이 아니다.** 마스크가 의존하는 모든 것(기하·카메라)을
비트 수준에서 묶고, 의존하지 않는 것(조명·PT 잡음)만 풀어 준다.
②가 하나라도 어긋나면 그 씬 프로세스는 통째로 격리한다.
설치분은 `idseg_backfill.json`이 파일 단위로 기록하므로 **되돌릴 수 있다**.

설치 경로 규약
--------------
    dataset/<정본 A 라운드>/<split>/<scene>/<PNG stem>.idseg.npz     ← 마스크
    dataset/<정본 A 라운드>/<split>/<scene>/idseg_backfill.json      ← 계보 원장

정본 `variation.json`은 **건드리지 않는다**(D72 ⑤ "A팔 바이트 불변"의 전제를
지킨다). 컷별 `idseg` / `idseg_fetch` / `idseg_n_ids`와 출처 라운드·sha256은
`idseg_backfill.json`에 둔다. `.idseg.npz`는 파일명 규약(`<stem>.idseg.npz`)으로
찾게 되어 있으므로(`w1b_verify.py:202,335`) 소비자 쪽 수정은 필요 없다.

같이 재는 것 — 알려진 세그 함정 둘
----------------------------------
  · **조건 경계 stale 승계** (W1B_REPORT §5.2, D75 ② 1컷 결함) — 렌더 순서에서
    바로 앞 컷과 `.idseg.npz`가 **바이트 동일**인데 포즈는 다른 컷을 센다.
    그것이 조건의 **첫 컷**에서 나오면 조건 경계 결함이다.
  · **`마스크 > 포즈`는 stale의 반대** — 인스턴스 ID는 평가마다 재번호되므로
    같은 장면에서도 해시가 갈린다. `idToLabels`로 **프림 경로 정규화**해
    경로 집합과 경로별 픽셀 수가 같으면 무해(benign)로 센다.

바이트가 갈렸을 때를 위한 진단(설치 판정에는 쓰지 않는다)
--------------------------------------------------------
`heightmap.npy` sha256 · `n_prims` · 포즈 7키 + `cam.eye` 최대 차 · 갈린 컷의
PNG 픽셀 최대/평균 절대차. 기하가 같은데 픽셀만 갈렸다면 원인은 PathTracing
누적 상태이고, 그 경우 마스크 자체는 유효할 수 있으나 **판정은 보수적으로
격리**하고 사용자 결재로 넘긴다.

사용:
    python3 experiments/v3_0823/code/w1b2_segfill.py            # 검사만
    python3 experiments/v3_0823/code/w1b2_segfill.py --install  # 통과분 설치
산출: experiments/v3_0823/w1b2_segfill.json (+ stdout 표)
"""
import argparse
import glob
import hashlib
import json
import os
import shutil
import sys

REPO = "/home/vislab/Desktop/work_sy/Practice_NegObs"
V3 = os.path.join(REPO, "experiments/v3_0823")
S = "260826_v3a_segfill"

# 밴드 -> (백필 라운드, 정본 A 라운드, 그 밴드의 A 씬)
# = RENDER_PLAN_V3 §1.2 표의 A팔 재활용 816프레임, 밴드별로 쪼갠 것.
BANDS = {
    "base": (S, "260819_main_on",
             "scene01 scene02 scene03 scene04 scene06 scene08 scene09 scene10 "
             "scene12 scene16 scene17 scene20 scene21 sceneC1 sceneC4 sceneD1 "
             "sceneD2 sceneD3".split()),
    "h":    (f"{S}_h", "260820_boost_h_on", "scene09 scene17".split()),
    "e":    (f"{S}_e", "260820_boost_e_on",
             "scene03 scene04 scene08 scene09 scene12 scene17 scene20 sceneC1 "
             "sceneC4".split()),
    "e2":   (f"{S}_e2", "260820_boost_e2_on",
             "scene03 scene04 scene12 scene20 sceneC4".split()),
}
POSE_KEYS = ("d", "h_rel", "yaw", "pitch", "roll", "hfov", "ground_z")
# G7_RELABEL 정본(변형 B)의 g7fixM 오버레이 트리는 **파일 단위 심링크**다. 정본
# 라운드에 사이드카를 깔아도 저절로 보이지 않으므로, 설치분과 짝이 되는 심링크를
# 같이 만든다 (오버레이 트리의 설계 그대로 — 실체는 정본에만 있다).
OVERLAY = {("e", "scene08"): "260820_boost_e_on_g7fixM",
           ("e", "scene12"): "260820_boost_e_on_g7fixM",
           ("e2", "scene12"): "260820_boost_e2_on_g7fixM"}


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def sdir(run, scene):
    g = glob.glob(os.path.join(REPO, "dataset", run, "*", scene, "variation.json"))
    return os.path.dirname(g[0]) if g else None


def cuts_of(d):
    v = json.load(open(os.path.join(d, "variation.json"), encoding="utf-8"))
    cu = v["cuts"]
    cu = list(cu.values()) if isinstance(cu, dict) else cu
    return v, {c["file"]: c for c in cu}


def pose_of(c):
    cam = c.get("cam") or {}
    return tuple(round(float(cam.get(k, 0.0)), 6) for k in POSE_KEYS) + \
        tuple(round(float(x), 6) for x in (cam.get("eye") or [0, 0, 0]))


def render_order(v, cuts):
    """렌더 순서 = variation.json의 conds 순서 × idx 오름차순."""
    conds = v.get("conds") or sorted({c.get("cond") for c in cuts.values()})
    out = []
    for cid in conds:
        out += sorted((f for f, c in cuts.items() if c.get("cond") == cid),
                      key=lambda f: cuts[f].get("idx", 0))
    for f in cuts:                                     # 표에 없는 것은 뒤에
        if f not in out:
            out.append(f)
    return out


def prim_norm(p):
    """(`{prim_path: n_px}`, n_ids) — 인스턴스 ID 재번호를 지운 정규형."""
    import numpy as np
    z = np.load(p, allow_pickle=False)
    a = z["idseg"]
    try:
        id2l = json.loads(str(z["idToLabels"]))
    except Exception:
        id2l = {}
    ids, cnt = np.unique(a, return_counts=True)
    out = {}
    for i, n in zip(ids.tolist(), cnt.tolist()):
        lab = id2l.get(str(i), id2l.get(i, f"<id{i}>"))
        if isinstance(lab, dict):
            lab = lab.get("class") or json.dumps(lab, sort_keys=True)
        out[str(lab)] = out.get(str(lab), 0) + int(n)
    return out, int(ids.size)


def px_delta(pa, pb):
    try:
        import numpy as np
        from PIL import Image
        a = np.asarray(Image.open(pa).convert("RGB"), np.int16)
        b = np.asarray(Image.open(pb).convert("RGB"), np.int16)
        if a.shape != b.shape:
            return dict(shape_a=list(a.shape), shape_b=list(b.shape))
        d = np.abs(a - b)
        return dict(max=int(d.max()), mean=round(float(d.mean()), 5),
                    n_px_differing=int((d.max(axis=2) > 0).sum()),
                    frac_px=round(float((d.max(axis=2) > 0).mean()), 6))
    except Exception as e:
        return dict(error=f"{type(e).__name__}: {str(e)[:120]}")


def check_unit(band, scene, install):
    srun, arun, _ = BANDS[band]
    sd, ad = sdir(srun, scene), sdir(arun, scene)
    r = dict(band=band, scene=scene, seg_round=srun, a_round=arun,
             seg_dir=None if sd is None else os.path.relpath(sd, REPO),
             a_dir=None if ad is None else os.path.relpath(ad, REPO))
    if ad is None:
        return dict(r, status="A_MISSING", why="정본 A 씬 디렉터리가 없다")
    if sd is None:
        return dict(r, status="NOT_RENDERED", why="백필 재렌더가 아직 없다")

    av, ac = cuts_of(ad)
    sv, sc = cuts_of(sd)
    apng = sorted(f for f in ac if f.endswith(".png"))
    spng = sorted(f for f in sc if f.endswith(".png"))
    r["n_a"], r["n_seg"] = len(apng), len(spng)
    if set(apng) != set(spng):
        return dict(r, status="CUTSET_MISMATCH",
                    why=f"컷 집합 불일치 — A만 {sorted(set(apng)-set(spng))[:3]} · "
                        f"백필만 {sorted(set(spng)-set(apng))[:3]}")

    # --- ① D75 문면: RGB PNG sha256 (참고 열 — 설치 판정에 쓰지 않는다) --------
    same, diff = [], []
    for f in apng:
        pa, pb = os.path.join(ad, f), os.path.join(sd, f)
        if not (os.path.isfile(pa) and os.path.isfile(pb)):
            diff.append(dict(file=f, why="파일 없음"))
            continue
        ha, hb = sha256(pa), sha256(pb)
        (same if ha == hb else diff).append(
            f if ha == hb else dict(file=f, sha_a=ha[:16], sha_seg=hb[:16]))
    r["n_png_identical"], r["n_png_differing"] = len(same), len(diff)
    r["png_identical"] = (len(diff) == 0 and len(same) == len(apng) > 0)

    # --- ② 기하 대응 (설치 판정) ----------------------------------------------
    hma, hmb = os.path.join(ad, "heightmap.npy"), os.path.join(sd, "heightmap.npy")
    r["heightmap_sha_equal"] = (os.path.isfile(hma) and os.path.isfile(hmb)
                                and sha256(hma) == sha256(hmb))
    dsame, ddiff = 0, []
    for f in apng:
        nm = os.path.splitext(f)[0] + ".depth.npy"
        pa, pb = os.path.join(ad, nm), os.path.join(sd, nm)
        if not (os.path.isfile(pa) and os.path.isfile(pb)):
            ddiff.append(dict(file=nm, why="depth 파일 없음"))
            continue
        if sha256(pa) == sha256(pb):
            dsame += 1
        else:
            e = dict(file=nm)
            try:
                import numpy as np
                A, Bb = np.load(pa).astype(np.float32), np.load(pb).astype(np.float32)
                m = np.isfinite(A) & np.isfinite(Bb)
                e["max_abs_m"] = round(float(np.abs(A[m] - Bb[m]).max()), 5) \
                    if m.any() else None
                e["n_finite_mask_diff"] = int((np.isfinite(A) != np.isfinite(Bb)).sum())
                e["n_px_diff"] = int((A != Bb).sum())
            except Exception as ex:
                e["error"] = f"{type(ex).__name__}: {str(ex)[:80]}"
            ddiff.append(e)
    r["n_depth_identical"], r["n_depth_differing"] = dsame, len(ddiff)
    r["depth_diff_sample"] = ddiff[:4]
    try:
        ma = json.load(open(os.path.join(ad, "heightmap_meta.json"), encoding="utf-8"))
        mb = json.load(open(os.path.join(sd, "heightmap_meta.json"), encoding="utf-8"))
        r["n_prims"] = [ma.get("n_prims"), mb.get("n_prims")]
        r["n_prims_equal"] = ma.get("n_prims") == mb.get("n_prims")
        r["arm_config"] = [ma.get("arm_config"), mb.get("arm_config")]
        r["arm_config_equal"] = ma.get("arm_config") == mb.get("arm_config")
    except Exception as e:
        r["meta_error"] = f"{type(e).__name__}: {str(e)[:100]}"
    dp = 0.0
    for f in apng:
        if f in ac and f in sc:
            pa, pb = pose_of(ac[f]), pose_of(sc[f])
            dp = max(dp, max(abs(x - y) for x, y in zip(pa, pb)))
    r["pose_max_delta"] = round(dp, 9)
    if diff:
        r["px_delta_sample"] = [dict(file=d["file"],
                                     **px_delta(os.path.join(ad, d["file"]),
                                                os.path.join(sd, d["file"])))
                                for d in diff[:3] if isinstance(d, dict) and "file" in d]
        r["png_differing_files"] = [d["file"] for d in diff if isinstance(d, dict)][:8]
    # ---- 설치 판정: 기하 대응 -------------------------------------------------
    r["geom_match"] = bool(
        r["heightmap_sha_equal"] and r.get("n_prims_equal")
        and r.get("arm_config_equal") and r["pose_max_delta"] == 0.0
        and r["n_depth_differing"] == 0 and r["n_depth_identical"] == len(apng) > 0)

    # --- ③ 세그 건전성 (설치 여부와 무관하게 늘 잰다) --------------------------
    segp = {f: os.path.join(sd, os.path.splitext(f)[0] + ".idseg.npz") for f in spng}
    have = {f: p for f, p in segp.items() if os.path.isfile(p)}
    r["n_idseg"] = len(have)
    hs = {f: sha256(p) for f, p in have.items()}
    poses = {f: pose_of(sc[f]) for f in have}
    r["n_unique_masks"] = len(set(hs.values()))
    r["n_poses"] = len(set(poses.values()))
    # 포즈 간 충돌 = 다른 포즈가 같은 마스크 (= stale의 지문)
    bypose = {}
    for f, h in hs.items():
        bypose.setdefault(h, set()).add(poses[f])
    collide = {h: v for h, v in bypose.items() if len(v) > 1}
    r["n_mask_pose_collisions"] = len(collide)
    r["fetch"] = sorted({sc[f].get("idseg_fetch") for f in have
                         if sc[f].get("idseg_fetch")})
    r["n_ids"] = sorted({sc[f].get("idseg_n_ids") for f in have
                         if sc[f].get("idseg_n_ids") is not None})
    # 조건 경계 stale 승계 — 렌더 순서에서 앞 컷과 마스크 동일 · 포즈는 다름
    order = [f for f in render_order(sv, sc) if f in have]
    carry = []
    for i in range(1, len(order)):
        f, g = order[i], order[i - 1]
        if hs[f] == hs[g] and poses[f] != poses[g]:
            carry.append(dict(file=f, prev=g,
                              cond=sc[f].get("cond"), prev_cond=sc[g].get("cond"),
                              at_cond_boundary=sc[f].get("cond") != sc[g].get("cond")))
    r["stale_carryover"] = carry
    r["n_stale_carryover"] = len(carry)
    r["n_stale_at_cond_boundary"] = sum(1 for c in carry if c["at_cond_boundary"])
    # 마스크 > 포즈 — 프림 경로 정규화로 무해성 확인
    r["over_discriminating"] = r["n_unique_masks"] > r["n_poses"]
    if r["over_discriminating"]:
        bad = 0
        by = {}
        for f in have:
            by.setdefault(poses[f], []).append(f)
        for _p, fs in by.items():
            if len(fs) < 2:
                continue
            base = None
            for f in fs:
                nm, _ = prim_norm(have[f])
                if base is None:
                    base = nm
                elif nm != base:
                    bad += 1
        r["prim_normalized_benign"] = (bad == 0)
        r["n_prim_normalized_mismatch"] = bad

    # --- ④ 판정 · 설치 --------------------------------------------------------
    if not r["geom_match"]:
        r["status"] = "QUARANTINE_GEOM_MISMATCH"
        bits = []
        if not r["heightmap_sha_equal"]:
            bits.append("heightmap sha 불일치")
        if not r.get("n_prims_equal"):
            bits.append(f"n_prims {r.get('n_prims')}")
        if not r.get("arm_config_equal"):
            bits.append("arm_config 불일치")
        if r["pose_max_delta"] != 0.0:
            bits.append(f"포즈 Δ {r['pose_max_delta']:.3g}")
        if r["n_depth_differing"]:
            bits.append(f"depth sha {r['n_depth_identical']}/{len(apng)}")
        r["why"] = "기하 대응 실패 — " + " · ".join(bits)
        return r
    if r["n_idseg"] != len(apng):
        r["status"] = "QUARANTINE_SEG_INCOMPLETE"
        r["why"] = f".idseg.npz {r['n_idseg']}/{len(apng)}"
        return r
    if r["n_mask_pose_collisions"]:
        r["status"] = "QUARANTINE_STALE"
        r["why"] = f"포즈 간 마스크 충돌 {r['n_mask_pose_collisions']}건 (stale)"
        return r
    r["status"] = "INSTALLABLE"
    if install:
        led = dict(doc="idseg_backfill", version="1.0",
                   authority="DECISIONS D75 ④ · W1B_REPORT §9 C-2",
                   procedure="A팔과 같은 씬·시드·밴드·조건·레시피로 재렌더 → "
                             "**기하 대응** 확인(heightmap sha · n_prims · arm_config · "
                             "포즈 7키+eye Δ=0 · 컷별 depth sha) → .idseg.npz만 설치. "
                             "재렌더의 PNG·depth·heightmap은 폐기했다. "
                             "RGB PNG sha256은 참고 열로만 기록한다 — PathTracing은 "
                             "프로세스 간 비트 재현되지 않는다(대조 실험 0/76).",
                   png_sha_identical=r["n_png_identical"],
                   png_sha_note="설치 판정에 쓰지 않는다 (D75 ④ 문면 정정 — 보고서 참조)",
                   scene=scene, band=band, source_round=srun,
                   source_dir=os.path.relpath(sd, REPO),
                   canonical_round=arun, n_cuts=len(apng),
                   seg_env=dict(NEGOBS_SEG_SIDECAR="1", NEGOBS_SEG_STRICT="1"),
                   cuts=[])
        for f in apng:
            dst = os.path.join(ad, os.path.splitext(f)[0] + ".idseg.npz")
            shutil.copy2(have[f], dst)
            led["cuts"].append(dict(
                file=f, idseg=os.path.basename(dst),
                idseg_fetch=sc[f].get("idseg_fetch"),
                idseg_n_ids=sc[f].get("idseg_n_ids"),
                canonical_png_sha256=sha256(os.path.join(ad, f)),
                canonical_depth_sha256=sha256(os.path.join(
                    ad, os.path.splitext(f)[0] + ".depth.npy")),
                idseg_sha256=hs[f]))
        json.dump(led, open(os.path.join(ad, "idseg_backfill.json"), "w",
                            encoding="utf-8"), ensure_ascii=False, indent=1)
        r["installed"] = len(apng)
        r["status"] = "INSTALLED"
        ov = OVERLAY.get((band, scene))
        if ov:
            od = sdir(ov, scene)
            if od:
                n = 0
                for f in apng + ["idseg_backfill.json"]:
                    nm = (os.path.splitext(f)[0] + ".idseg.npz"
                          if f.endswith(".png") else f)
                    src, dst = os.path.join(ad, nm), os.path.join(od, nm)
                    if os.path.lexists(dst):
                        os.remove(dst)
                    os.symlink(src, dst)
                    n += 1
                r["overlay_linked"] = dict(round=ov, n=n)
    return r


def main(install, only):
    rows = []
    for band, (_srun, _arun, scs) in BANDS.items():
        for s in scs:
            if only and s not in only:
                continue
            rows.append(check_unit(band, s, install))

    n_units = len(rows)
    ok = [r for r in rows if r["status"] in ("INSTALLED", "INSTALLABLE")]
    unavail = [r for r in rows if r["status"] not in ("INSTALLED", "INSTALLABLE")]
    n_cuts = sum(r.get("n_a", 0) for r in rows)
    n_ident = sum(r.get("n_png_identical", 0) for r in rows)
    n_dep = sum(r.get("n_depth_identical", 0) for r in rows)
    n_inst = sum(r.get("installed", 0) for r in rows)

    print(f"{'밴드':6s} {'씬':9s} {'컷':>4s} {'PNG sha':>9s} {'depth sha':>10s} "
          f"{'hm':>3s} {'프림':>9s} {'포즈Δ':>8s} {'마스크/포즈':>11s} {'승계':>4s} 판정")
    print("-" * 120)
    for r in rows:
        na = r.get("n_a", 0)
        print(f"{r['band']:6s} {r['scene']:9s} {na:4d} "
              f"{r.get('n_png_identical', 0):4d}/{na:<4d} "
              f"{r.get('n_depth_identical', 0):5d}/{na:<4d} "
              f"{('=' if r.get('heightmap_sha_equal') else '≠'):>3s} "
              f"{str(r.get('n_prims', '—')):>9s} "
              f"{r.get('pose_max_delta', float('nan')):8.1e} "
              f"{r.get('n_unique_masks', 0):5d}/{r.get('n_poses', 0):<5d} "
              f"{r.get('n_stale_carryover', 0):4d} {r['status']}")
    print("-" * 120)
    print(f"유닛 {len(ok)}/{n_units} 설치가능 · **기하 대응(설치 판정)** depth sha 동일 "
          f"{n_dep}/{n_cuts} ({100.0 * n_dep / max(1, n_cuts):.1f} %) · "
          f"참고 열 RGB PNG sha 동일 {n_ident}/{n_cuts} "
          f"({100.0 * n_ident / max(1, n_cuts):.1f} %) · 설치 사이드카 {n_inst}")
    if unavail:
        print("\nseg-unavailable (격리 — 설치하지 않음):")
        for r in unavail:
            print(f"  {r['band']:5s} {r['scene']:9s} {r['status']:26s} "
                  f"{r.get('why', '')}")

    out = dict(doc="w1b2_segfill", version="1.0",
               authority=["DECISIONS D75 ④", "W1B_REPORT §9 C-2 · §10 W1B-3"],
               procedure="A팔 재렌더(SEG_SIDECAR+SEG_STRICT) → 전 컷 PNG sha256 "
                         "바이트 동일 검증 → 동일한 씬에만 .idseg.npz 설치 "
                         "(PNG·depth 폐기) · 불일치는 격리(무단 대체 금지)",
               install_path="dataset/<정본 A 라운드>/<split>/<scene>/"
                            "<stem>.idseg.npz  (+ idseg_backfill.json 원장; "
                            "정본 variation.json은 건드리지 않는다. g7fixM 오버레이 "
                            "트리에는 같은 이름의 심링크를 건다)",
               install_criterion="기하 대응 — heightmap sha256 동일 AND n_prims 동일 "
                                 "AND arm_config 동일 AND 포즈 7키+cam.eye Δ=0 "
                                 "AND 컷별 depth sha256 동일",
               criterion_note="D75 ④ 문면의 'PNG 바이트 동일'은 만족 불가능하다 — "
                              "PathTracing RGB는 프로세스 간 비트 재현되지 않는다. "
                              "대조 실험(260825_v3w0_cuecls_A vs 260819_main_on, "
                              "세그 변경 0, 19씬 76컷): PNG 0/76 · depth 73/76 · "
                              "heightmap 19/19. 마스크는 조명·PT 잡음에 의존하지 "
                              "않으므로 depth가 올바른 대응 증거다.",
               installed=install,
               n_units=n_units, n_units_ok=len(ok),
               n_cuts=n_cuts,
               n_cuts_png_identical=n_ident,
               png_identity_rate=round(n_ident / max(1, n_cuts), 6),
               n_cuts_depth_identical=n_dep,
               geom_identity_rate=round(n_dep / max(1, n_cuts), 6),
               n_sidecars_installed=n_inst,
               seg_unavailable=[dict(band=r["band"], scene=r["scene"],
                                     status=r["status"], why=r.get("why"),
                                     n_png_differing=r.get("n_png_differing"),
                                     n_depth_differing=r.get("n_depth_differing"),
                                     depth_diff_sample=r.get("depth_diff_sample"))
                                for r in unavail],
               stale_carryover_total=sum(r.get("n_stale_carryover", 0) for r in rows),
               stale_at_cond_boundary_total=sum(
                   r.get("n_stale_at_cond_boundary", 0) for r in rows),
               over_discriminating=[dict(band=r["band"], scene=r["scene"],
                                         n_unique_masks=r.get("n_unique_masks"),
                                         n_poses=r.get("n_poses"),
                                         prim_normalized_benign=r.get(
                                             "prim_normalized_benign"))
                                    for r in rows if r.get("over_discriminating")],
               units=rows)
    op = os.path.join(V3, "w1b2_segfill.json")
    json.dump(out, open(op, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"-> {op}")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--install", action="store_true")
    ap.add_argument("--scenes", default="")
    a = ap.parse_args()
    sys.exit(main(a.install, [x for x in a.scenes.split(",") if x]))
