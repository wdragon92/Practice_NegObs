# -*- coding: utf-8 -*-
"""통람(通覽) 시트 — 씬 라이브러리 1장 요약 PNG.

v1 은 "v5 PT 파이널" 한 라운드에 하드코딩돼 있었다(본편 21씬 · `v8_pt`/`v7_pt` 고정 ·
경로 상수 2개). W2-D 에서 **라운드·씬셋·출력경로를 인자로** 뺐다 — 배치1 12씬 시트를
같은 코드로 뽑기 위해서다(임무 A2). 시각 디자인·타일 규격(960×540)·배지는 v1 그대로.

사용:
    python3 scripts/make_hq_sheet.py --round 260730_w2d_judge --set main21
    python3 scripts/make_hq_sheet.py --round 260730_w2d_judge --set batch1
    python3 scripts/make_hq_sheet.py            # 인자 없으면 v1 기본값(main21 · v8_pt 사슬)

`--round` 는 **쉼표 폴백**이다(regression_check 와 같은 규약). 먼저 존재하는 폴더를 쓴다.
GPU 0 · PIL 만 필요.
"""
import argparse
import glob
import os

from PIL import Image, ImageDraw, ImageFont

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(REPO, "look_check")

# --- 씬셋 --------------------------------------------------------------------
MAIN21 = [
    ("scene01", "캠퍼스 계단"), ("scene02", "지하도"), ("scene03", "하천 제방"),
    ("scene04", "공원 침목길"), ("scene05", "야외공연장"), ("scene06", "보행육교 나선"),
    ("scene07", "산사 돌계단"), ("scene08", "선큰 광장"), ("scene09", "호수공원 수변"),
    ("scene10", "공원 데크 갈지자"), ("scene11", "보도육교"), ("scene12", "수변 데크길"),
    ("scene13", "지하주차 진입부"), ("scene14", "착시 대계단"), ("scene15", "달동네 골목"),
    ("scene16", "지하보도 입구"), ("scene17", "한강 제방"), ("scene18", "바닷가 벽화계단"),
    ("scene19", "옥상 winder"), ("scene20", "대각 사교"), ("scene21", "기념관 대계단"),
]
BATCH1 = [
    ("sceneC1", "C1 적설 계단"), ("sceneC2", "C2 낙엽 매몰 계단"),
    ("sceneC4", "C4 우후 젖은 계단"), ("sceneD1", "D1 하역장 도크"),
    ("sceneD2", "D2 슬래브 개구부"), ("sceneD3", "D3 노변 배수로"),
    ("sceneD4", "D4 지하철 승강장"), ("sceneN1", "N1 그림자 띠 [HN]"),
    ("sceneN2", "N2 아스팔트 패치 [HN]"), ("sceneN3", "N3 트롱프뢰유 [HN]"),
    ("sceneN4", "N4 완경사 램프 [HN]"), ("sceneN5", "N5 플러시 그레이팅 [HN]"),
]
SETS = {"main21": MAIN21, "batch1": BATCH1}

# 대표 컷 우선순위 — 미장센(전경) → 없으면 프리셋 원경
VIEW_PRI = ["beauty", "overview", "roof_skyline", "entry_gate", "facade",
            "pair_compare", "oblique", "vista", "h1.8_d5", "h1.8_d10", "h0.9_d5"]
VIEW_OVR = {
    "scene06": ["deck_entry", "spiral"], "scene07": ["gate_frame", "stone_rhythm"],
    "scene10": ["reversal"], "scene11": ["deck_walk", "sidewalk"],
    "scene12": ["edge_void", "beauty"], "scene14": ["terrace_read", "beauty"],
    "scene18": ["color_front"], "scene19": ["roof_skyline", "entry_gate"],
    "scene09": ["park_vista", "beauty"], "scene13": ["beauty", "approach"],
    "scene17": ["pair_compare", "levee_walk"], "scene05": ["rim_view", "plaza_approach"],
    "sceneC1": ["rail_side", "approach"], "sceneC2": ["beauty_side", "approach_walk"],
    "sceneC4": ["approach", "grazing_mirror"], "sceneD1": ["beauty_overview", "bay_corner"],
    "sceneD2": ["beauty_overview", "brink"], "sceneD3": ["culvert_far", "channel_reveal"],
    "sceneD4": ["tunnel_vista", "track_reveal"], "sceneN1": ["beauty_oblique", "band_grazing"],
    "sceneN2": ["beauty_oblique", "patch_confusion"], "sceneN3": ["beauty_overview", "design_eye"],
    "sceneN4": ["beauty_overview", "wall_run"], "sceneN5": ["beauty_oblique", "manhole_pair"],
}

FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
TW, TH, LAB, COLS = 960, 540, 68, 4


def pick(scene, round_spec):
    """씬 하나의 대표 PNG. `round_spec` 은 쉼표 폴백."""
    d = None
    for sub in [s.strip() for s in round_spec.split(",") if s.strip()]:
        c = os.path.join(BASE, scene, sub)
        if os.path.isdir(c) and glob.glob(os.path.join(c, "*.png")):
            d = c
            break
    if d is None:
        return None
    pngs = sorted(glob.glob(os.path.join(d, "*.png")))
    for key in VIEW_OVR.get(scene, []) + VIEW_PRI:
        for p in pngs:
            if key in os.path.basename(p):
                return p
    return pngs[0] if pngs else None


def build(scenes, round_spec, out, title, sub, verdicts=None):
    f_label = ImageFont.truetype(FONT, 42)
    f_badge = ImageFont.truetype(FONT, 30)
    f_title = ImageFont.truetype(FONT, 64)
    f_sub = ImageFont.truetype(FONT, 30)
    rows = (len(scenes) + COLS - 1) // COLS
    W, H = COLS * TW, 150 + rows * (TH + LAB)
    sheet = Image.new("RGB", (W, H), (16, 16, 20))
    dr = ImageDraw.Draw(sheet)
    dr.text((24, 18), title, font=f_title, fill=(240, 240, 240))
    dr.text((26, 100), sub, font=f_sub, fill=(150, 155, 165))

    missing = []
    for idx, (scene, name) in enumerate(scenes):
        col, row = idx % COLS, idx // COLS
        x0, y0 = col * TW, 150 + row * (TH + LAB)
        p = pick(scene, round_spec)
        if p:
            im = Image.open(p).convert("RGB")
            w, h = im.size
            tar = TW / TH
            if w / h > tar:
                nw = int(h * tar)
                im = im.crop(((w - nw) // 2, 0, (w + nw) // 2, h))
            else:
                nh = int(w / tar)
                im = im.crop((0, (h - nh) // 2, w, (h + nh) // 2))
            sheet.paste(im.resize((TW - 6, TH - 6), Image.LANCZOS), (x0 + 3, y0 + 3))
        else:
            missing.append(scene)
        n = scene.replace("scene", "")
        dr.text((x0 + 14, y0 + TH + 8), f"{n}  {name}", font=f_label,
                fill=(238, 238, 238))
        v = (verdicts or {}).get(scene, "합격")
        bg = {"합격": (34, 120, 62), "플래그": (140, 108, 24)}.get(v, (120, 40, 40))
        bw = dr.textlength(v, font=f_badge) + 28
        bx = x0 + TW - 18 - bw
        dr.rounded_rectangle([bx, y0 + TH + 12, bx + bw, y0 + TH + 56],
                             radius=10, fill=bg)
        dr.text((bx + 14, y0 + TH + 16), v, font=f_badge, fill=(245, 245, 245))

    os.makedirs(os.path.dirname(os.path.abspath(out)) or ".", exist_ok=True)
    sheet.save(out, optimize=True)
    print(f"saved: {out} {sheet.size}"
          + (f"  · 컷 없음: {missing}" if missing else ""))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--round", default="v8_pt,v7_pt,v8_rt2,v8_rt,v7_rt",
                    help="라운드 이름(쉼표 폴백). 기본값은 v1 하드코딩 사슬")
    ap.add_argument("--set", default="main21", choices=sorted(SETS))
    ap.add_argument("--out", default="")
    ap.add_argument("--title", default="")
    ap.add_argument("--sub", default="")
    ap.add_argument("--verdicts", default="",
                    help="scene=판정 쉼표 목록 (예: scene14=플래그,sceneN5=플래그)")
    a = ap.parse_args()

    rnd = a.round.split(",")[0]
    out = a.out or os.path.join(
        REPO, "Docs", "audit_v4",
        "library21_final_hq.png" if rnd == "v8_pt"
        else f"library_{a.set}_{rnd}.png")
    n = len(SETS[a.set])
    title = a.title or (
        f"NegObs 씬 라이브러리 {'본편 21종' if a.set == 'main21' else '배치1 12종'}"
        f" — 라운드 {rnd}")
    sub = a.sub or (f"{n}씬 · PT · NEGOBS_LOOK_V1=1 · detail_scale 2.0 · "
                    f"regression v2.1 · near_ground σ_LF WARN 게이트 복원 라운드")
    verds = {}
    for tok in [t for t in a.verdicts.split(",") if t.strip()]:
        k, _, v = tok.partition("=")
        verds[k.strip()] = v.strip()
    build(SETS[a.set], a.round, out, title, sub, verds)


if __name__ == "__main__":
    main()
