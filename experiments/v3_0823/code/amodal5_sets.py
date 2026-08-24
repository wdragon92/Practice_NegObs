#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""amodal5_sets.py — GPU-5 아모달 판독의 **프레임 집합 확정 + test-ext 아모달 GT 생성** (CPU 전용).

    PYTHONNOUSERSITE=1 CUDA_VISIBLE_DEVICES= \
      python3 experiments/v3_0823/code/amodal5_sets.py [--force]

산출
    experiments/v3_0823/amodal5/frames.json          — 결정적 프레임 목록(전 집합)
    experiments/v3_0823/annotations/amodal_ext/*.png — test-ext A팔 아모달 GT (신규 생성)

[격리·진단] 본 산출물은 PREREG A/B 판정에 혼입하지 않는다. 새 학습 0 · 새 렌더 0.

프레임 집합 (전부 결정적 — 난수 없음)
    panel   4장   PANELS_VERDICT §7 의 panel_f 4행과 **같은 컷**
    core_H  96장  test-core(=split_v2_full::test 7씬) · tier=='H' (엄격 은닉)
    core_E  45장  동 · tier=='E'
    core_V  45장  동 · tier=='V' ∧ 아모달 PNG 존재(180장) 중 **4칸마다 1장** (정렬 후 ::4)
    ext_H   72장  test-ext (A,C) 매니페스트의 A팔(on) tier=='H'  — v3 세대, 아모달 GT 신규 생성
    cueoff  576장 test-ext sceneH1/H2/H3 의 A·B·C·D 4팔 전량 (계기판② 반응 표용)

아모달 GT
    v2 세대: `experiments/dayrun_0820/annotations/amodal/<stem>.png` (D 웨이브 산출물, 재사용)
    v3 세대: 본 스크립트가 `amodal_masks.py` 의 기하(SceneGeom·prism_points·frame_masks)를
             **한 줄도 바꾸지 않고 import** 해서 생성한다. 가림 무시 프리즘 실루엣 · 960×540.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

ROOT = "/home/vislab/Desktop/work_sy/Practice_NegObs"
V3 = os.path.join(ROOT, "experiments/v3_0823")
DAY = os.path.join(ROOT, "experiments/dayrun_0820")
OUTD = os.path.join(V3, "amodal5")
EXTGT = os.path.join(V3, "annotations/amodal_ext")
os.makedirs(OUTD, exist_ok=True)
os.makedirs(EXTGT, exist_ok=True)

sys.path.insert(0, os.path.join(DAY, "code/yolo"))
sys.path.insert(0, os.path.join(ROOT, "experiments/mainrun_0819/code"))
sys.path.insert(0, os.path.join(ROOT, "experiments/mainrun_0819/code/labeling"))

import amodal_masks as AM                                    # noqa: E402
from common import LB, load_grid                             # noqa: E402

GRID, GSPEC, GPATH = load_grid(None)
HZ = float(GSPEC["hazard_depth_m"])

MAN_CORE = os.path.join(V3, "dataset_manifest_v2corr.json")
SPLIT_CORE = os.path.join(DAY, "split_v2_full.json")
MAN_AC = os.path.join(V3, "dataset_manifest_v3_textext.json")
MAN_BD = os.path.join(V3, "dataset_manifest_v3_textext_bd.json")
AMODAL_V2 = os.path.join(DAY, "annotations/amodal")

PANEL_FIDS = [                       # PANELS_VERDICT §7.1 표와 바이트 동일
    ("on/scene14/L7__s20260819__0002.png", "V"),
    ("on/scene14/L5__s20260819__0006.png", "H"),
    ("on/scene15/L0__s20260820__0006.png::boost_h", "H"),
    ("on/scene18/L7__s20260821__0000.png::boost_e2", "E"),
]
CUEOFF_SCENES = ("sceneH1", "sceneH2", "sceneH3")


def v2_stem(fid):
    """'on/scene14/L5__x__0006.png::boost_h' -> 'on__scene14__L5__x__0006__boost_h'."""
    arm, scene, fn = fid.split("/", 2)
    suf = "__" + fid.split("::", 1)[1] if "::" in fid else ""
    return f"{arm}__{scene}__{os.path.splitext(fn.split('::', 1)[0])[0]}{suf}"


def ext_stem(fid):
    """'base/on/sceneH1/L0__x__0000.png' -> 'base__on__sceneH1__L0__x__0000'."""
    return os.path.splitext(fid)[0].replace("/", "__")


def cam_of(rgb_path):
    sdir, fn = os.path.dirname(rgb_path), os.path.basename(rgb_path)
    cuts = json.load(open(os.path.join(sdir, "variation.json")))["cuts"]
    cuts = list(cuts.values()) if isinstance(cuts, dict) else cuts
    return next(c["cam"] for c in cuts if c["file"] == fn)


# ------------------------------------------------------------------ test-ext GT
def build_ext_gt(frames, force):
    """A팔 프레임의 아모달 마스크를 (A, C) 쌍 기하로 생성. -> {fid: (png, mask_px)}"""
    by_scene = {}
    for f in frames:
        by_scene.setdefault((f["round"], f["scene_id"]), []).append(f)
    out, warn = {}, []
    for (rnd, scene), fl in sorted(by_scene.items()):
        sdir = os.path.dirname(fl[0]["rgb"])
        if not rnd.endswith("_A"):
            raise SystemExit(f"[fatal] A팔 라운드가 아니다: {rnd}")
        off_dir = sdir.replace(f"/{rnd}/", f"/{rnd[:-2]}_C/")
        if not os.path.isdir(off_dir):
            raise SystemExit(f"[fatal] C팔 쌍 없음: {off_dir}")
        g = AM.SceneGeom(sdir, off_dir)
        fp_raw, comp, n_comp = g.raw_footprint(HZ)
        for f in fl:
            cam = cam_of(f["rgb"])
            full, parts, gstat, splat, fp = AM.frame_masks(
                g, fp_raw, comp, n_comp, cam, HZ, GSPEC, False, (AM.OUT_W, AM.OUT_H), AM.R_MAX)
            stem = ext_stem(f["frame_id"])
            p = os.path.join(EXTGT, stem + ".png")
            npx = int(full.sum())
            if npx and (force or not os.path.exists(p)):
                Image.fromarray((full.astype(np.uint8) * 255), "L").save(p, optimize=True)
            if not npx:
                warn.append(f["frame_id"])
            out[f["frame_id"]] = (p if npx else None, npx)
        print(f"  [ext-gt] {rnd}/{scene:9s} {len(fl):3d}프레임 · "
              f"footprint {int(fp.sum())}칸 · 마스크 있음 "
              f"{sum(1 for f in fl if out[f['frame_id']][1])}")
    if warn:
        print(f"  [ext-gt] 경고: 마스크 0픽셀 프레임 {len(warn)}장 {warn[:5]}")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()

    core = json.load(open(MAN_CORE))
    test_scenes = set(json.load(open(SPLIT_CORE))["test"])
    bbx = json.load(open(os.path.join(AMODAL_V2, "bboxes.json")))["frames"]

    def core_rec(f, group):
        e = bbx.get(f["frame_id"]) or {}
        png = os.path.join(AMODAL_V2, e["mask"]) if e.get("mask") else None
        return dict(group=group, gen="v2", frame_id=f["frame_id"], scene=f["scene_id"],
                    tier=f.get("tier"), arm=f["toggle_state"], rgb=f["rgb"], depth=f["depth"],
                    polar_gt=[int(v) for v in f["polar_gt"]], gt_mask=png,
                    gt_mask_px=int(e.get("mask_px") or 0), key=f["frame_id"])

    ctest = [f for f in core["frames"] if f["scene_id"] in test_scenes]
    byid = {f["frame_id"]: f for f in ctest}
    recs = []

    for fid, tier in PANEL_FIDS:                       # panel
        f = byid[fid]
        assert f.get("tier") == tier, (fid, f.get("tier"), tier)
        recs.append(core_rec(f, "panel"))

    H = sorted([f for f in ctest if f.get("tier") == "H"], key=lambda f: f["frame_id"])
    E = sorted([f for f in ctest if f.get("tier") == "E"], key=lambda f: f["frame_id"])
    Vm = sorted([f for f in ctest if f.get("tier") == "V"
                 and (bbx.get(f["frame_id"]) or {}).get("mask")], key=lambda f: f["frame_id"])
    assert (len(H), len(E), len(Vm)) == (96, 45, 180), (len(H), len(E), len(Vm))
    for f in H:
        recs.append(core_rec(f, "core_H"))
    for f in E:
        recs.append(core_rec(f, "core_E"))
    for f in Vm[::4]:
        recs.append(core_rec(f, "core_V"))

    # H 96장의 **off팔 트윈** (같은 씬·같은 컷·같은 카메라 · 낙차만 없음).
    # (b) 의 대조군: 낙차가 없는데도 같은 자리를 칠하면 그것은 「은닉 낙차 묘사」가 아니라
    # 「장면 기하 칠하기」다. GT 아모달 영역은 트윈 A팔 것을 **반사실 영역**으로 빌려 쓴다.
    for f in H:
        tw = byid["off/" + f["frame_id"].split("/", 1)[1]]
        e = bbx.get(f["frame_id"]) or {}
        recs.append(dict(group="core_Htwin", gen="v2", frame_id=tw["frame_id"],
                         scene=tw["scene_id"], tier="off", arm="off", rgb=tw["rgb"],
                         depth=tw["depth"], polar_gt=[int(v) for v in tw["polar_gt"]],
                         gt_mask=os.path.join(AMODAL_V2, e["mask"]) if e.get("mask") else None,
                         gt_mask_px=int(e.get("mask_px") or 0), key=tw["frame_id"],
                         twin_of=f["frame_id"]))

    ac = json.load(open(MAN_AC))
    ext_h = sorted([f for f in ac["frames"]
                    if f["toggle_state"] == "on" and f.get("tier") == "H"],
                   key=lambda f: f["frame_id"])
    assert len(ext_h) == 72, len(ext_h)
    extgt = build_ext_gt(ext_h, a.force)
    for f in ext_h:
        png, npx = extgt[f["frame_id"]]
        recs.append(dict(group="ext_H", gen="v3", frame_id=f["frame_id"], scene=f["scene_id"],
                         tier="H", arm="A", rgb=f["rgb"], depth=f["depth"],
                         polar_gt=[int(v) for v in f["polar_gt"]], gt_mask=png,
                         gt_mask_px=npx, key="A|" + f["frame_id"]))

    bd = json.load(open(MAN_BD))
    # 4팔은 (A,C)/(B,D) 가 같은 컷·같은 카메라다 -> A팔의 아모달 GT 를 **반사실 영역**으로
    # B·C·D 에도 그대로 붙인다. 그래야 「같은 자리에서 팔별 질량」을 견줄 수 있다.
    cf = {f["frame_id"]: extgt.get(f["frame_id"], (None, 0)) for f in ext_h}
    ARMS = {(MAN_AC, "on"): "A", (MAN_AC, "off"): "C", (MAN_BD, "on"): "B", (MAN_BD, "off"): "D"}
    for mp, man in ((MAN_AC, ac), (MAN_BD, bd)):
        for f in sorted(man["frames"], key=lambda f: f["frame_id"]):
            if f["scene_id"] not in CUEOFF_SCENES:
                continue
            arm = ARMS[(mp, f["toggle_state"])]
            a_fid = f["frame_id"].replace("/off/", "/on/", 1)
            png, npx = cf.get(a_fid, (None, 0))
            recs.append(dict(group="cueoff", gen="v3", frame_id=f["frame_id"], scene=f["scene_id"],
                             tier=f.get("tier"), arm=arm, rgb=f["rgb"], depth=f["depth"],
                             polar_gt=[int(v) for v in f["polar_gt"]], gt_mask=png,
                             gt_mask_px=npx, key=arm + "|" + f["frame_id"],
                             band_round=f["band_round"], cond=f["cond"],
                             file=os.path.basename(f["rgb"]), cf_of=a_fid if png else None))

    seen, uniq = set(), []
    for r in recs:                                    # panel 4장은 core_* 와 중복 → key 로 접기
        if r["key"] in seen:
            uniq.append(dict(r, dup=True))
            continue
        seen.add(r["key"])
        uniq.append(dict(r, dup=False))
    for r in uniq:
        if r["gt_mask"] and not os.path.exists(r["gt_mask"]):
            raise SystemExit(f"[fatal] GT 마스크 파일 없음: {r['gt_mask']}")

    doc = dict(meta=dict(created="2026-08-24", grid=GPATH, grid_version=GSPEC["version"],
                         hazard_depth_m=HZ, manifests=dict(core=MAN_CORE, ac=MAN_AC, bd=MAN_BD),
                         split_core=SPLIT_CORE, amodal_v2=AMODAL_V2, amodal_ext=EXTGT,
                         isolated_from_ab=True,
                         note="[격리·진단] GPU-5 아모달 판독 전용 · PREREG A/B 판정 비혼입"),
               frames=uniq)
    p = os.path.join(OUTD, "frames.json")
    json.dump(doc, open(p, "w"), indent=1)
    import collections
    c = collections.Counter((r["group"], r["arm"]) for r in uniq if not r["dup"])
    g = collections.Counter(r["group"] for r in uniq)
    print(f"\n[frames] 총 {len(uniq)}행 · 유니크 {len(seen)}프레임 -> {p}")
    for k, v in sorted(g.items()):
        n_gt = sum(1 for r in uniq if r["group"] == k and r["gt_mask"])
        print(f"   {k:8s} {v:4d}장 · 아모달 GT {n_gt}장")
    print("   팔별:", dict(sorted(c.items(), key=str)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
