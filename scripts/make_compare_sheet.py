#!/usr/bin/env python3
"""사실화 v1 전후 비교 시트 — 33씬을 **개선 전 / 후** 두 칸으로 나란히.

왜 필요한가: Phase1 E9 에서 확인했듯 **저수준 통계가 명백한 시각 차이를 거의
잡지 못한다**. 그래서 게이트를 "수치 + 육안 병행"으로 이원화했고, 육안 판정의
근거가 되는 물건이 이 시트다.

  좌 = 개선 전 (기존 합격 라이브러리: 본편 v8_pt/v7_pt · 배치1 ctx2/ctx1)
  우 = 개선 후 (사실화 룩 레이어 v1)

실행:
  python scripts/make_compare_sheet.py <after_round_suffix> [출력경로]
  예) python scripts/make_compare_sheet.py r2_on
"""
import os
import sys
import glob

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(ROOT, "look_check")

AFTER = sys.argv[1] if len(sys.argv) > 1 else "r2_on"
OUT = (sys.argv[2] if len(sys.argv) > 2
       else os.path.join(ROOT, "Docs", "reports",
                         f"realism_compare_{AFTER}.png"))

# 개선 전 후보 (앞에서부터 존재하는 것을 씀)
BEFORE_ROUNDS = ("v8_pt", "v7_pt", "final_pt", "ctx2_pt", "ctx2", "ctx1",
                 "v8_rt", "v7_rt", "r5")

MAIN = [(f"scene{n:02d}", t) for n, t in [
    (1, "캠퍼스 광장"), (2, "지하도"), (3, "하천 제방"), (4, "공원 산책로"),
    (5, "야외 공연장"), (6, "보행육교 나선"), (7, "산사 돌계단"), (8, "선큰 광장"),
    (9, "호수공원 수변"), (10, "공원 데크"), (11, "보도육교"), (12, "수변 데크길"),
    (13, "지하주차 진입"), (14, "대계단 착시"), (15, "골목 미로"), (16, "캐노피 그림자"),
    (17, "한강 제방"), (18, "바닷가 벽화계단"), (19, "부채꼴 winder"),
    (20, "사선 경사"), (21, "기념비")]]
BATCH1 = [("sceneN1", "그림자 띠"), ("sceneN2", "아스팔트 패치"),
          ("sceneN3", "트롱프뢰유"), ("sceneN4", "내림 램프"),
          ("sceneN5", "평면 그레이팅"), ("sceneC1", "눈"), ("sceneC2", "낙엽"),
          ("sceneC4", "젖음"), ("sceneD1", "하역장"), ("sceneD2", "바닥 개구부"),
          ("sceneD3", "측구"), ("sceneD4", "승강장")]
SCENES = MAIN + BATCH1

# 판정 1순위는 h0.3 로봇 시점 — 비교도 그 시점을 우선한다
VIEW_PRI = ["preset_h0.3_d2", "preset_h0.3_d5", "beauty", "overview"]

TW, TH = 480, 270          # 타일 크기
GAP, PAD = 8, 26
COLS = 3                   # 씬 3개 × (전/후 2칸)


def _font(sz):
    for p in ("/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
        if os.path.isfile(p):
            try:
                return ImageFont.truetype(p, sz)
            except Exception:
                pass
    return ImageFont.load_default()


def pick_dir(scene, rounds):
    for sub in rounds:
        d = os.path.join(BASE, scene, sub)
        if os.path.isdir(d) and glob.glob(os.path.join(d, "*.png")):
            return d
    return None


def pick_img(d, prefer=VIEW_PRI):
    if d is None:
        return None
    pngs = sorted(glob.glob(os.path.join(d, "*.png")))
    if not pngs:
        return None
    for key in prefer:
        for p in pngs:
            if key in os.path.basename(p):
                return p
    return pngs[0]


def tile(path):
    im = Image.new("RGB", (TW, TH), (24, 26, 30))
    if path and os.path.isfile(path):
        try:
            with Image.open(path) as s:
                s = s.convert("RGB")
                s.thumbnail((TW, TH), Image.LANCZOS)
                im.paste(s, ((TW - s.width) // 2, (TH - s.height) // 2))
        except Exception:
            pass
    return im


def main():
    f_lab, f_sm, f_ttl = _font(22), _font(17), _font(46)
    rows = (len(SCENES) + COLS - 1) // COLS
    cell_w = TW * 2 + GAP
    W = PAD * 2 + cell_w * COLS + GAP * (COLS - 1)
    H = PAD * 2 + 120 + rows * (TH + 34 + GAP * 3)
    sheet = Image.new("RGB", (W, H), (14, 15, 18))
    dr = ImageDraw.Draw(sheet)

    dr.text((PAD, PAD), "사실화 v1 — 개선 전 / 후 비교", font=f_ttl,
            fill=(238, 240, 245))
    dr.text((PAD, PAD + 62),
            f"좌 = 기존 합격 라이브러리   ·   우 = 룩 레이어 v1 ({AFTER})   ·   "
            "시점은 판정 1순위 h0.3 로봇 뷰 우선",
            font=f_lab, fill=(150, 156, 168))
    dr.text((PAD, PAD + 90),
            "저수준 통계가 시각 차이를 잘 잡지 못하므로(Phase1 E9) 게이트는 "
            "수치 + 육안 병행 판정이다.",
            font=f_sm, fill=(120, 126, 138))

    y0 = PAD + 120
    missing = []
    for i, (scene, title) in enumerate(SCENES):
        r, c = divmod(i, COLS)
        x = PAD + c * (cell_w + GAP)
        y = y0 + r * (TH + 34 + GAP * 3)

        bd = pick_dir(scene, BEFORE_ROUNDS)
        ad = pick_dir(scene, (AFTER,))
        bi, ai = pick_img(bd), pick_img(ad)
        if ai is None:
            missing.append(scene)

        sheet.paste(tile(bi), (x, y + 30))
        sheet.paste(tile(ai), (x + TW + GAP, y + 30))

        dr.text((x, y + 4), f"{scene}  {title}", font=f_lab,
                fill=(226, 230, 238))
        bl = os.path.basename(bd) if bd else "없음"
        dr.text((x, y + 30 + TH + 4), f"전 · {bl}", font=f_sm,
                fill=(130, 136, 148))
        dr.text((x + TW + GAP, y + 30 + TH + 4),
                f"후 · {AFTER}" + ("" if ai else "  (렌더 없음)"),
                font=f_sm, fill=(120, 200, 140) if ai else (200, 110, 110))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    sheet.save(OUT)
    print(f"[시트] {OUT}  ({W}x{H})")
    if missing:
        print(f"[경고] '후' 렌더 없는 씬 {len(missing)}개: {', '.join(missing)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
