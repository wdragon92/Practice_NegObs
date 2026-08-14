# -*- coding: utf-8 -*-
"""Build the 21-scene contact sheet — one representative view per scene, taken
from each scene's most recent render directory."""
import os, glob
from PIL import Image, ImageDraw, ImageFont

BASE = "/home/vislab/Desktop/work_sy/Practice_NegObs/look_check"
# v4 세대 시트는 Docs/archive/audit_v4/ 로 이동됨(08-05 1차 아카이브) — 재실행 산출물도 같은 곳에.
OUT = "/home/vislab/Desktop/work_sy/Practice_NegObs/Docs/archive/audit_v4/scene_overview_v4.png"

NAMES = {
    1: "캠퍼스 계단 (T1)", 2: "지하도 (T3)", 3: "하천 제방 (T5)",
    4: "공원 침목길 (T4)", 5: "선큰 앰피 (T6)", 6: "나선 석탑 (T9)",
    7: "사원 마모석 (T16)", 8: "스텝웰 (T11)", 9: "가트 수변 (T12)",
    10: "갈지자 절벽 (T13)", 11: "비상계단 (T19)", 12: "절벽 잔도 (T17)",
    13: "나선 주차램프 (T10)", 14: "착시 대계단 (T14)", 15: "감천 골목 (T15)",
    16: "캐노피 암부 (T20)", 17: "한강 계단+램프 (T21)", 18: "물결 예술계단 (T18)",
    19: "부채꼴 winder·옥상 (T7)", 20: "대각 사교 (T8)", 21: "기념 다단 (T2)",
}
DIR_PRI = ["v5_pt", "v5_rt", "final_pt_r2", "r5", "final_pt", "r4", "r3", "r2", "r1", "auto"]
VIEW_PRI = ["beauty", "overview", "roof_context", "entry_gate", "facade",
            "h1.8_d10", "h1.8_d5", "h0.9_d10", "h0.9_d5"]
# Per-scene overrides, so the representative cut conveys the scene's identity
DIR_OVR = {}
VIEW_OVR = {7: ["stair_down", "temple_walk"], 12: ["walk_down", "across_gorge"],
            14: ["terrace_read", "beauty"], 18: ["color_front", "oblique_down"],
            19: ["roof_skyline", "entry_gate"]}

def pick(scene):
    sdir = os.path.join(BASE, f"scene{scene:02d}")
    if not os.path.isdir(sdir):
        return None
    subs = [d for d in DIR_OVR.get(scene, DIR_PRI)
            if os.path.isdir(os.path.join(sdir, d))]
    for sub in subs:
        pngs = sorted(glob.glob(os.path.join(sdir, sub, "*.png")))
        if not pngs:
            continue
        for key in VIEW_OVR.get(scene, VIEW_PRI):
            for p in pngs:
                if key in os.path.basename(p):
                    return p
        return pngs[0]
    return None

FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
f_label = ImageFont.truetype(FONT, 25)
f_src = ImageFont.truetype(FONT, 17)
f_title = ImageFont.truetype(FONT, 40)

TW, TH, LAB = 480, 270, 40
COLS, ROWS = 4, 6
W, H = COLS * TW, 70 + ROWS * (TH + LAB)
sheet = Image.new("RGB", (W, H), (18, 18, 22))
dr = ImageDraw.Draw(sheet)
dr.text((16, 12), "NegObs 씬 라이브러리 21종 — 대표 컷 (2026-07-27, 감사 v4 반영 · v5 PT 파이널)",
        font=f_title, fill=(235, 235, 235))

missing = []
for i in range(1, 22):
    col, row = (i - 1) % COLS, (i - 1) // COLS
    x0, y0 = col * TW, 70 + row * (TH + LAB)
    p = pick(i)
    if p:
        im = Image.open(p).convert("RGB")
        # center crop -> 16:9 tile
        w, h = im.size
        ar, tar = w / h, TW / TH
        if ar > tar:
            nw = int(h * tar); im = im.crop(((w - nw) // 2, 0, (w + nw) // 2, h))
        else:
            nh = int(w / tar); im = im.crop((0, (h - nh) // 2, w, (h + nh) // 2))
        im = im.resize((TW - 4, TH - 4), Image.LANCZOS)
        sheet.paste(im, (x0 + 2, y0 + 2))
        src = os.path.relpath(os.path.dirname(p), BASE)
    else:
        dr.rectangle([x0 + 2, y0 + 2, x0 + TW - 2, y0 + TH - 2], fill=(40, 40, 46))
        dr.text((x0 + 20, y0 + TH // 2 - 15), "(렌더 없음)", font=f_label, fill=(150, 150, 150))
        src = "-"
        missing.append(i)
    dr.text((x0 + 8, y0 + TH + 2), f"{i:02d}  {NAMES[i]}", font=f_label, fill=(235, 235, 235))
    dr.text((x0 + TW - 8 - dr.textlength(src, font=f_src), y0 + TH + 20), src,
            font=f_src, fill=(115, 125, 145))

sheet.save(OUT, optimize=True)
print("saved:", OUT, sheet.size, "missing:", missing)
