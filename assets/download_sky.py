#!/usr/bin/env python3
"""사실화 라운드 — 구름 하늘 HDRI 조달 (PolyHaven CC0).

배경
  `Docs/reports/realism_phase1.md` §5 실측: 렌더의 죽은 픽셀(국소표준편차
  < 1/255) 중 67~74%가 하늘이었다. 원인은 기본 HDRI `qwantani_noon_puresky`
  — 이름 그대로 구름이 한 점도 없어 대면적이 완전 평탄하다.
  → 구름이 있는 정오~오후 하늘 3종을 도입한다. 선정 근거·검증은
    `Docs/reports/sky_procurement_v1.md`.

라이선스
  PolyHaven 전 에셋 CC0 (https://polyhaven.com/license):
  "All assets ... are ... licensed as CC0 ... You can use our assets for any
   purpose, including commercial work." + 라이선스 페이지가 AI 연구 활용을
  명시적으로 언급("we've heard from numerous data scientists, software
  developers, automotive engineers and AI researchers all using our assets").
  → `Docs/briefs/realism_brief_v1.md` 원칙 2(CC0/MIT-0/CC-BY만) 충족.

동작
  PolyHaven API(https://api.polyhaven.com/files/{slug})에서 hdri/4k/exr URL을
  받아 `assets/` 루트에 `{slug}_4k.exr` 로 저장한다. 기존 HDRI(qwantani_*,
  kloofendal_overcast_4k.exr)와 같은 위치이므로 씬에서는
  `light_params["hdri"] = "<파일명>"` 로 파일명만 지정하면 된다.

  재실행 안전: 이미 있고 API 보고 크기와 일치하면 skip.
  다운로드 후 EXR 헤더(매직 0x01312f76)를 직접 파싱해 해상도·채널·압축을
  검증한다. cv2 가 있으면 태양 위치까지 측정해 `hdri_sun_rotz_offset` 을
  바로 출력한다(없으면 건너뛴다 — 다운로드 자체는 성공 처리).

사용법
  python assets/download_sky.py
"""
import json
import os
import struct
import sys
import time
import urllib.request

ASSETS_DIR = os.path.dirname(os.path.abspath(__file__))
API = "https://api.polyhaven.com/files/{slug}"
RETRIES = 3
TIMEOUT = 300
# PolyHaven 은 기본 python-urllib UA 에 403 을 반환한다(download_assets.py 확인).
HEADERS = {"User-Agent": "curl/8.5.0"}

# ---------------------------------------------------------------------------
# 선정 3종 — 전부 PolyHaven "pure skies" 카테고리(지상 구조물 0, 지평선 아래는
# 하늘의 미러 그라디언트)라 우리 씬 배경과 충돌하지 않는다.
# 태양 고도/방위는 1k EXR 실측(argmax 픽셀). 씬 기본값 noon_sun_elev=49.79°.
#   slug                                   구름 유형          태양고도  방위
#   kloofendal_48d_partly_cloudy_puresky   산개 적운(청천 틈)  48.0°   214.3°
#   sunflowers_puresky                     층적운 밴드+권층운  43.1°   216.0°
#   farm_field_puresky                     부분 흐림(태양 차폐) 51.1°   216.7°
# ---------------------------------------------------------------------------
SKY_SLUGS = [
    "kloofendal_48d_partly_cloudy_puresky",
    "sunflowers_puresky",
    "farm_field_puresky",
]

# ---------------------------------------------------------------------------
# 조명 라운드 — 고도 사다리 (조건 카탈로그 L3/L4/L5 전용)
#   `Docs/briefs/lighting_camera_variation_spec_v1.md` §4.2 가 조달 대상으로
#   지정한 15종 중, §4.3 의 8조건 카탈로그가 **실제로 쓰는** 3종만 받는다.
#   나머지 6종은 사다리의 대체안이라 조건 카탈로그에 배선되지 않았다.
#   `Docs/reports/lighting_spikes_v1.md` §3.4 가 "9종 부재 = 유일한 차단 요소"
#   로 올린 항목의 해소분이다.
#
#   slug                                   조건  고도(스펙 실측)  f_dir  게이트
#   kloofendal_38d_partly_cloudy_puresky   L3    37.96°          0.438  PASS
#   kloofendal_28d_misty_puresky           L4    28.50°          0.049  SOFT
#   qwantani_late_afternoon_puresky        L5    19.07°          0.645  PASS
#
#   ⚠ kloofendal_28d_misty 만 방위가 다르다(φ 169.15 vs 216 대). 씬 상수
#     233.5 를 그대로 쓰면 그림자가 47° 틀어진다 — 카탈로그가 조건별
#     `hdri_sun_rotz_offset` 을 들고 있는 이유다(spec §4.2).
# ---------------------------------------------------------------------------
LADDER_SLUGS = [
    "kloofendal_38d_partly_cloudy_puresky",
    "kloofendal_28d_misty_puresky",
    "qwantani_late_afternoon_puresky",
]


def open_url(url):
    req = urllib.request.Request(url, headers=HEADERS)
    return urllib.request.urlopen(req, timeout=TIMEOUT)


def fetch_json(url):
    for attempt in range(1, RETRIES + 1):
        try:
            with open_url(url) as r:
                return json.load(r)
        except Exception as e:
            print(f"  [api retry {attempt}/{RETRIES}] {url}: {e}")
            time.sleep(2 * attempt)
    return None


def download(url, dest, expected_size):
    """url -> dest. 이미 있고 크기가 맞으면 skip."""
    if os.path.exists(dest):
        actual = os.path.getsize(dest)
        if expected_size is None or actual == expected_size:
            print(f"  [skip] {os.path.basename(dest)} ({actual:,} bytes, 존재)")
            return True
        print(f"  [redo] {os.path.basename(dest)} size {actual} != {expected_size}")
    tmp = dest + ".part"
    for attempt in range(1, RETRIES + 1):
        try:
            print(f"  [get ] {url} (attempt {attempt}/{RETRIES})")
            with open_url(url) as r, open(tmp, "wb") as f:
                while True:
                    chunk = r.read(1 << 20)
                    if not chunk:
                        break
                    f.write(chunk)
            actual = os.path.getsize(tmp)
            if expected_size is not None and actual != expected_size:
                raise IOError(f"size mismatch {actual} != {expected_size}")
            os.replace(tmp, dest)
            print(f"  [ ok ] {os.path.basename(dest)} ({actual:,} bytes)")
            return True
        except Exception as e:
            print(f"  [fail] attempt {attempt}/{RETRIES}: {e}")
            if os.path.exists(tmp):
                os.remove(tmp)
            time.sleep(2 * attempt)
    return False


# ---------------------------------------------------------------------------
# EXR 헤더 검증 (외부 의존성 없이 직접 파싱)
#   [magic 4B = 0x01312f76][version 4B][attr*][null] 구조.
#   attr = name\0 type\0 size(4B) value(size B)
# ---------------------------------------------------------------------------
EXR_MAGIC = 0x01312F76
PIXEL_TYPE = {0: "uint", 1: "half", 2: "float"}
COMPRESSION = {0: "none", 1: "RLE", 2: "ZIPS", 3: "ZIP", 4: "PIZ",
               5: "PXR24", 6: "B44", 7: "B44A", 8: "DWAA", 9: "DWAB"}


def _read_cstr(f):
    buf = bytearray()
    while True:
        c = f.read(1)
        if not c or c == b"\x00":
            return buf.decode("utf-8", "replace")
        buf += c


def verify_exr(path):
    """EXR 헤더를 파싱해 (w, h, [(채널명, 픽셀형)], 압축) 반환. 실패 시 None."""
    try:
        with open(path, "rb") as f:
            magic, version = struct.unpack("<II", f.read(8))
            if magic != EXR_MAGIC:
                print(f"  [BAD ] {os.path.basename(path)}: EXR 매직 불일치 "
                      f"(0x{magic:08x})")
                return None
            win, chans, comp = None, [], None
            while True:
                name = _read_cstr(f)
                if not name:
                    break
                _read_cstr(f)                       # attr type (미사용)
                size = struct.unpack("<I", f.read(4))[0]
                val = f.read(size)
                if name == "dataWindow":
                    x0, y0, x1, y1 = struct.unpack("<iiii", val)
                    win = (x1 - x0 + 1, y1 - y0 + 1)
                elif name == "channels":
                    off = 0
                    while off < len(val) and val[off] != 0:
                        end = val.index(b"\x00", off)
                        cname = val[off:end].decode("utf-8", "replace")
                        ptype = struct.unpack("<i", val[end + 1:end + 5])[0]
                        chans.append((cname, PIXEL_TYPE.get(ptype, ptype)))
                        off = end + 1 + 16          # pixelType,pLinear,pad,x,y
                elif name == "compression":
                    comp = COMPRESSION.get(val[0], val[0])
            if win is None or not chans:
                print(f"  [BAD ] {os.path.basename(path)}: 헤더 불완전")
                return None
            print(f"  [exr ] {os.path.basename(path)}: {win[0]}x{win[1]} "
                  f"v{version & 0xFF} ch={[c[0] for c in chans]} "
                  f"({chans[0][1]}) comp={comp}")
            return win, chans, comp
    except Exception as e:
        print(f"  [BAD ] {os.path.basename(path)}: 헤더 파싱 실패 {e}")
        return None


# ---------------------------------------------------------------------------
# 태양 위치 측정 (선택) — hdri_sun_rotz_offset 산출
#   scene_common.setup_lighting 관례 검증(2026-07-28, qwantani 역산):
#     돔 텍스처 방위 phi(=360*(ix+0.5)/w)는 월드 방위와 부호가 반대이고,
#     DistantLight 는 rotateZ 만큼 돌면 월드 방위 270°+rotZ 를 향한다.
#     ∴ hdri_sun_rotz_offset = (90 - phi_sun) mod 360
#     검산: qwantani_noon_puresky phi=216.17 → 233.83 ≈ 씬 상수 233.5 (Δ0.33°)
# ---------------------------------------------------------------------------
def measure_sun(path):
    try:
        os.environ.setdefault("OPENCV_IO_ENABLE_OPENEXR", "1")
        import cv2
        import numpy as np
    except Exception as e:
        print(f"  [sun ] 측정 생략(cv2/numpy 없음: {e})")
        return None
    try:
        img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        rgb = img[..., :3][..., ::-1].astype(np.float64)   # BGR(A) -> RGB
        lum = (0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1]
               + 0.0722 * rgb[..., 2])
        h, w = lum.shape
        iy, ix = np.unravel_index(np.argmax(lum), lum.shape)
        elev = 90.0 - 180.0 * (iy + 0.5) / h
        phi = 360.0 * (ix + 0.5) / w
        offset = (90.0 - phi) % 360.0
        print(f"  [sun ] elev={elev:.2f}° phi={phi:.2f}° "
              f"→ noon_sun_elev={elev:.2f}, hdri_sun_rotz_offset={offset:.2f}")
        return elev, phi, offset
    except Exception as e:
        print(f"  [sun ] 측정 실패({e}) — 다운로드 자체는 정상")
        return None


def main():
    failures = []
    placed = []

    # 기본은 종전 3종. `--ladder` 는 조명 라운드 고도 사다리(L3/L4/L5)를 함께,
    # `--only-ladder` 는 사다리만 받는다(이미 있는 3종 재검증 생략).
    slugs = list(SKY_SLUGS)
    if "--ladder" in sys.argv:
        slugs += LADDER_SLUGS
    elif "--only-ladder" in sys.argv:
        slugs = list(LADDER_SLUGS)

    print("=== PolyHaven 구름 하늘 HDRI (CC0) ===")
    for slug in slugs:
        print(f"[hdri] {slug}")
        data = fetch_json(API.format(slug=slug))
        if data is None:
            failures.append(f"{slug}:hdri:4k:exr (API 응답 없음)")
            continue
        try:
            entry = data["hdri"]["4k"]["exr"]
        except KeyError as e:
            failures.append(f"{slug}:hdri:4k:exr (API 누락 {e})")
            continue
        dest = os.path.join(ASSETS_DIR, f"{slug}_4k.exr")
        if not download(entry["url"], dest, entry.get("size")):
            failures.append(f"{slug}:hdri:4k:exr ({entry['url']})")
            continue
        if verify_exr(dest) is None:
            failures.append(f"{slug}: EXR 헤더 검증 실패")
            continue
        measure_sun(dest)
        placed.append(dest)

    print("\n=== 검증 ===")
    total = 0
    for slug in slugs:
        p = os.path.join(ASSETS_DIR, f"{slug}_4k.exr")
        if os.path.exists(p) and os.path.getsize(p) > 0:
            total += os.path.getsize(p)
            print(f"  OK   {os.path.basename(p):46s} "
                  f"{os.path.getsize(p):>12,} bytes")
        else:
            print(f"  MISS {slug}_4k.exr")
    print(f"\n총 {len(placed)}/{len(slugs)} 파일, {total:,} bytes "
          f"({total/1e6:.1f} MB)")

    if failures:
        print("\n실패 (네트워크가 막혔으면 assets/ 에 직접 배치):")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    print(f"\n하늘 HDRI {len(slugs)}종 배치 완료. "
          "씬 적용은 light_params['hdri'] = '<파일명>'.")


if __name__ == "__main__":
    main()
