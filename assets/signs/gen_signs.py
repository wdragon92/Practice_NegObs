# -*- coding: utf-8 -*-
"""한글 사인 텍스처 생성 (공통 레이어 — 브리프 v5).
실행: python assets/signs/gen_signs.py  →  assets/signs/sign_*.png
스타일: 한국 공공 사인 관행(경고=황색 삼각/흑, 안내=청색 패널/백, 금지=적테).
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"

def panel(name, size, bg, fg, text, sub=None, border=None, tri=False):
    W, H = size
    im = Image.new("RGB", (W, H), bg)
    dr = ImageDraw.Draw(im)
    if border:
        dr.rectangle([6, 6, W - 7, H - 7], outline=border, width=14)
    if tri:  # 경고 삼각 픽토그램(상단 중앙)
        cx, ty, s = W // 2, int(H * 0.08), int(H * 0.34)
        dr.polygon([(cx, ty), (cx - s // 2, ty + s), (cx + s // 2, ty + s)],
                   outline=(20, 20, 20), width=10)
        dr.line([(cx, ty + int(s * 0.32)), (cx, ty + int(s * 0.68))],
                fill=(20, 20, 20), width=9)
        dr.ellipse([cx - 5, ty + int(s * 0.78), cx + 5, ty + int(s * 0.78) + 10],
                   fill=(20, 20, 20))
    f_main = ImageFont.truetype(FONT, int(H * (0.30 if tri else 0.34)))
    tw = dr.textlength(text, font=f_main)
    ty2 = int(H * (0.50 if tri else 0.30))
    dr.text(((W - tw) / 2, ty2), text, font=f_main, fill=fg)
    if sub:
        f_sub = ImageFont.truetype(FONT, int(H * 0.12))
        sw = dr.textlength(sub, font=f_sub)
        dr.text(((W - sw) / 2, int(H * 0.82) - 8), sub, font=f_sub, fill=fg)
    im.save(os.path.join(HERE, f"{name}.png"))
    print("saved", name)

# 경고(황) — 낙차 인접 = 설비 역추론 단서
panel("sign_warn_fall", (768, 768), (245, 197, 12), (20, 20, 20),
      "추락주의", sub="FALL HAZARD", tri=True)
panel("sign_caution_step", (768, 768), (245, 197, 12), (20, 20, 20),
      "계단주의", sub="WATCH YOUR STEP", tri=True)
# 안내(청)
panel("sign_exit", (768, 384), (16, 74, 146), (255, 255, 255), "출구  →")
panel("sign_info", (768, 512), (16, 74, 146), (255, 255, 255),
      "안내", sub="INFORMATION")
# 금지(백/적테)
panel("sign_no_entry", (768, 512), (245, 245, 245), (30, 30, 30),
      "진입금지", border=(190, 24, 24))
