#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""통람 갤러리 — 라운드 하나에서 **씬당 4컷**을 600 px JPEG 로 줄이고 `meta.json` 을 쓴다.

왜 4컷인가. 판정 라운드는 씬당 13~16컷이라 33씬이면 450컷이 넘고, 사람이 한 번에
훑을 양이 아니다. 그래서 **로봇 눈높이 근경(h0.3 d5) · 사람 눈높이 중경(h0.9 d5) ·
원경(h1.8 d10) · 미장센 전경 1컷**으로 축약한다 — 낙차 은닉은 근경에서, 씬 정체성은
전경에서 읽히기 때문이다.

컷이 없으면 **조용히 대체하지 않는다**: 대체한 뷰 이름을 `meta.json` 에 그대로 적는다
(scene19 는 프리셋 거리가 2/3.5/5 라 `h1.8_d10` 자체가 없다 — 그런 것을 감추면 갤러리가
거짓말을 한다).

사용:
    python3 scripts/make_review_gallery.py --round 260730_w2d_judge \
        --out look_check/_review_w2 --status-json Docs/reports/regr_260730_w2d.json
GPU 0 · PIL 만 필요 · 출력은 `--out` 아래에만 쓴다.
"""
from __future__ import annotations

import argparse
import glob
import json
import os

from PIL import Image

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(REPO, "look_check")

# (슬롯 이름, 우선순위 뷰 목록) — 앞에서부터 존재하는 첫 컷을 쓴다
SLOTS = [
    ("h03d5", ["preset_h0.3_d5"]),
    ("h09d5", ["preset_h0.9_d5"]),
    ("h18d10", ["preset_h1.8_d10", "preset_h1.8_d5"]),   # 19 는 d10 이 없다
    ("beauty", []),                                       # 아래 BEAUTY 에서 씬별로
]
# 미장센 전경 — "가장 정보량이 많은" 컷을 씬마다 지정. 없으면 beauty/overview 부분일치.
BEAUTY = {
    "scene01": "beauty_overview", "scene02": "beauty_overview", "scene03": "meander_air",
    "scene04": "trail_approach", "scene05": "rim_view", "scene06": "overview",
    "scene07": "gate_frame", "scene08": "beauty_overview", "scene09": "park_vista",
    "scene10": "reversal", "scene11": "overview", "scene12": "beauty_overview",
    "scene13": "beauty_overview", "scene14": "beauty_overview", "scene15": "beauty_overview",
    "scene16": "beauty_overview", "scene17": "pair_compare", "scene18": "sea_beauty",
    "scene19": "roof_skyline", "scene20": "oblique_overview", "scene21": "facade_front",
    "sceneC1": "rail_side", "sceneC2": "beauty_side", "sceneC4": "approach",
    "sceneD1": "beauty_overview", "sceneD2": "beauty_overview", "sceneD3": "culvert_far",
    "sceneD4": "tunnel_vista", "sceneN1": "beauty_oblique", "sceneN2": "beauty_oblique",
    "sceneN3": "beauty_overview", "sceneN4": "beauty_overview", "sceneN5": "beauty_oblique",
}
NAMES = {}          # scene -> 한국어 이름 (make_hq_sheet 의 표를 재사용)
try:
    import importlib.util as _il
    _s = _il.spec_from_file_location(
        "mhs", os.path.join(REPO, "scripts", "make_hq_sheet.py"))
    _m = _il.module_from_spec(_s)
    _s.loader.exec_module(_m)
    NAMES = {k: v for k, v in (_m.MAIN21 + _m.BATCH1)}
except Exception:
    pass

PROFILES = {}       # scene -> ground_kit 프로파일 (SCENE_PLANS 픽스처가 출처)
try:
    import importlib.util as _il2
    import sys as _sys
    if REPO not in _sys.path:                 # ground_kit imports infra_kit/stair_kit
        _sys.path.insert(0, REPO)             # from the repo root, not from scripts/
    _s2 = _il2.spec_from_file_location("gk", os.path.join(REPO, "ground_kit.py"))
    _m2 = _il2.module_from_spec(_s2)
    _s2.loader.exec_module(_m2)
    PROFILES = {k: v["profile"] for k, v in _m2.SCENE_PLANS.items()}
except Exception:
    pass

WIDTH, QUALITY = 600, 80


def find_cut(d, keys):
    pngs = sorted(glob.glob(os.path.join(d, "*.png")))
    for k in keys:
        for p in pngs:
            if os.path.basename(p) == f"pt_noon_{k}.png":
                return p, k
    for k in keys:                       # 부분일치 폴백
        for p in pngs:
            if k in os.path.basename(p):
                return p, os.path.basename(p)[8:-4]
    return None, None


def status_from(regr, scene):
    """`regression_check --json` 결과에서 씬 한 줄 상태를 뽑는다."""
    if not regr:
        return "게이트 미실행", []
    rows = [r for r in regr if r.get("scene") == scene]
    if not rows:
        return "라운드 없음", []
    sev = {}
    flags = []
    for r in rows:
        for i in r.get("issues", []):
            if i["sev"] in ("FAIL", "WARN"):
                sev[i["sev"]] = sev.get(i["sev"], 0) + 1
                flags.append(f"{i['sev']} {i['code']} {r['view']}")
    if sev.get("FAIL"):
        return f"FAIL {sev['FAIL']} · WARN {sev.get('WARN', 0)}", flags
    if sev.get("WARN"):
        return f"WARN {sev['WARN']}", flags
    return "PASS", flags


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--round", required=True)
    ap.add_argument("--out", default=os.path.join(BASE, "_review_w2"))
    ap.add_argument("--status-json", default="",
                    help="regression_check --json 결과 (씬별 한 줄 상태에 쓴다)")
    ap.add_argument("--width", type=int, default=WIDTH)
    a = ap.parse_args()

    regr = None
    if a.status_json and os.path.isfile(a.status_json):
        try:
            regr = json.load(open(a.status_json, encoding="utf-8"))
            if isinstance(regr, dict):
                regr = regr.get("rows", regr.get("results"))
        except Exception as e:
            print(f"[경고] status-json 읽기 실패: {e}")

    os.makedirs(a.out, exist_ok=True)
    meta, n_thumb = [], 0
    scenes = sorted(os.path.basename(p) for p in glob.glob(os.path.join(BASE, "scene*"))
                    if os.path.isdir(p))
    for scene in scenes:
        d = os.path.join(BASE, scene, a.round)
        if not os.path.isdir(d):
            print(f"[건너뜀] {scene}: 라운드 없음")
            continue
        st, flags = status_from(regr, scene)
        cuts = {}
        for slot, keys in SLOTS:
            kk = keys or [BEAUTY.get(scene, "beauty"), "beauty", "overview"]
            p, used = find_cut(d, kk)
            if p is None:
                cuts[slot] = None
                continue
            im = Image.open(p).convert("RGB")
            w, h = im.size
            im = im.resize((a.width, max(1, round(h * a.width / w))), Image.LANCZOS)
            fp = os.path.join(a.out, f"{scene}_{slot}.jpg")
            im.save(fp, "JPEG", quality=QUALITY, optimize=True)
            n_thumb += 1
            cuts[slot] = dict(file=os.path.basename(fp), view=used,
                              substituted=(used != (keys[0] if keys else used)))
        prof = PROFILES.get(scene, "")
        st_json = os.path.join(d, "round_stamp.json")
        stamp = {}
        if os.path.isfile(st_json):
            try:
                stamp = json.load(open(st_json, encoding="utf-8"))
            except Exception:
                pass
        meta.append(dict(scene=scene, name=NAMES.get(scene, ""), round=a.round,
                         profile=prof, status=st, flags=flags[:8],
                         cuts=cuts, git_head=stamp.get("git_head", ""),
                         n_cuts_round=stamp.get("cuts")))
    with open(os.path.join(a.out, "meta.json"), "w", encoding="utf-8") as f:
        json.dump(dict(round=a.round, width=a.width, quality=QUALITY,
                       scenes=meta), f, ensure_ascii=False, indent=1)
    print(f"썸네일 {n_thumb}장 · 씬 {len(meta)} → {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
