# -*- coding: utf-8 -*-
"""High-quality combined sheet for the finalized scenes — v5 PT final (960x540 tiles)."""
import os, glob
from PIL import Image, ImageDraw, ImageFont

BASE = "/home/vislab/Desktop/work_sy/Practice_NegObs/look_check"
OUT = "/home/vislab/Desktop/work_sy/Practice_NegObs/Docs/audit_v4/library21_final_hq.png"

SCENES = [
    (1, "캠퍼스 계단", "합격"), (2, "지하도", "합격"), (3, "하천 제방", "합격"),
    (4, "공원 침목길", "합격"), (5, "야외공연장", "합격"), (6, "보행육교 나선", "합격"),
    (7, "산사 돌계단", "합격"), (8, "선큰 광장", "합격"), (9, "호수공원 수변", "합격"),
    (10, "공원 데크 갈지자", "합격"), (11, "보도육교", "합격"), (12, "수변 데크길", "합격"),
    (13, "지하주차 진입부", "합격"), (14, "착시 대계단", "합격"), (15, "달동네 골목", "합격"),
    (16, "지하보도 입구", "합격"), (17, "한강 제방", "합격"), (18, "바닷가 벽화계단", "합격"),
    (19, "옥상 winder", "합격"), (20, "대각 사교", "합격"), (21, "기념관 대계단", "합격"),
]
VIEW_PRI = ["beauty", "overview", "roof_skyline", "entry_gate", "facade",
            "pair_compare", "h1.8_d5", "h0.9_d5"]
VIEW_OVR = {6: ["deck_entry", "spiral"], 7: ["gate_frame", "stone_rhythm"],
            10: ["reversal"], 11: ["deck_walk", "sidewalk"], 12: ["edge_void", "beauty"],
            14: ["terrace_read", "beauty"],
            18: ["color_front"], 19: ["roof_skyline", "entry_gate"],
            9: ["park_vista", "beauty"], 13: ["beauty", "approach"],
            17: ["pair_compare", "levee_walk"]}

FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
f_label = ImageFont.truetype(FONT, 42)
f_badge = ImageFont.truetype(FONT, 30)
f_title = ImageFont.truetype(FONT, 64)
f_sub = ImageFont.truetype(FONT, 30)

TW, TH, LAB = 960, 540, 68
COLS = 4
ROWS = (len(SCENES) + COLS - 1) // COLS
W, H = COLS * TW, 150 + ROWS * (TH + LAB)
sheet = Image.new("RGB", (W, H), (16, 16, 20))
dr = ImageDraw.Draw(sheet)
dr.text((24, 18), "NegObs 씬 라이브러리 21종 — v5 범용성 재설계·v5.1 현실성 라운드 완주 (전 씬 합격)",
        font=f_title, fill=(240, 240, 240))
dr.text((26, 100), "2026-07-28 · 512spp/8bounce · 판정 v6→v7→v8 3라운드 · judge_v*_rt*.md"
        " · 신규 7·재해석 3·현실화 11 — grazing 은닉 회귀 0",
        font=f_sub, fill=(150, 155, 165))

def pick(n):
    d = None
    for sub in ("v8_pt", "v7_pt", "v8_rt2", "v8_rt", "v7_rt"):
        c = os.path.join(BASE, f"scene{n:02d}", sub)
        if os.path.isdir(c) and glob.glob(os.path.join(c, "*.png")):
            d = c; break
    if d is None:
        return None
    pngs = sorted(glob.glob(os.path.join(d, "*.png")))
    if not pngs:
        return None
    for key in VIEW_OVR.get(n, []) + VIEW_PRI:
        for p in pngs:
            if key in os.path.basename(p):
                return p
    return pngs[0]

for idx, (n, name, verdict) in enumerate(SCENES):
    col, row = idx % COLS, idx // COLS
    x0, y0 = col * TW, 150 + row * (TH + LAB)
    p = pick(n)
    if p:
        im = Image.open(p).convert("RGB")
        w, h = im.size
        tar = TW / TH
        if w / h > tar:
            nw = int(h * tar); im = im.crop(((w - nw) // 2, 0, (w + nw) // 2, h))
        else:
            nh = int(w / tar); im = im.crop((0, (h - nh) // 2, w, (h + nh) // 2))
        im = im.resize((TW - 6, TH - 6), Image.LANCZOS)
        sheet.paste(im, (x0 + 3, y0 + 3))
    dr.text((x0 + 14, y0 + TH + 8), f"{n:02d}  {name}",
            font=f_label, fill=(238, 238, 238))
    bg = (34, 120, 62) if verdict == "합격" else (140, 108, 24)
    bw = dr.textlength(verdict, font=f_badge) + 28
    bx = x0 + TW - 18 - bw
    dr.rounded_rectangle([bx, y0 + TH + 12, bx + bw, y0 + TH + 56],
                         radius=10, fill=bg)
    dr.text((bx + 14, y0 + TH + 16), verdict, font=f_badge,
            fill=(245, 245, 245))

sheet.save(OUT, optimize=True)
print("saved:", OUT, sheet.size)
