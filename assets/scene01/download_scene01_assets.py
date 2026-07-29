#!/usr/bin/env python3
"""Scene01 캠퍼스 광장 하행계단 — CC0 텍스처 에셋 파이프라인.

설계 브리프 `Docs/scene01_design_brief.md` §3(재질)·§4(점자블록) 구현.

동작 요약
  1. ambientCG (Tiles038 / PavingStones127 / PavingStones111):
     https://ambientcg.com/get?file={ID}_4K-JPG.zip 다운로드(브라우저 UA),
     zip 해제 후 _Color/_NormalDX/_Roughness 를 canonical 파일명으로 rename,
     zip·잔여파일(AO/Displacement/Normal GL/usdc/blend 등) 삭제.
       Tiles038        -> plaza_light_{diff,nor,rough}.jpg
       PavingStones127 -> band_dark_{diff,nor,rough}.jpg
       PavingStones111 -> plaza_lower_{diff,nor,rough}.jpg
  2. PolyHaven (granite_tile / brick_wall_001):
     기존 download_assets.py API 패턴(pick_key 대소문자 혼재 대응)으로
     4k jpg diff/nor_dx/rough 다운로드.
       granite_tile   -> granite_dark_{diff,nor_dx,rough}.jpg
       brick_wall_001 -> brick_red_{diff,nor_dx,rough}.jpg
  2b. PolyHaven v2 (Docs/multi_scene_brief_v2.md §B — 신규 7세트):
     동일 패턴 확장. diff 키가 'diffuse' 소문자일 수 있어 후보에 포함,
     rough 직접 키가 없고 ARM 만 있는 에셋은 ARM G채널(Roughness) 추출로 생성.
       concrete_wall_008   -> concrete_wall_{diff,nor_dx,rough}.jpg
       brushed_concrete_03 -> concrete_floor_{...}
       weathered_planks    -> wood_dark_{...}
       park_dirt           -> dirt_park_{...}
       gravel_floor        -> gravel_{...}
       stone_tiles_02      -> stone_flag_{...}
       rock_wall_08        -> rock_wall_{...}
  3. 점자블록 절차 생성(numpy+PIL): 6x6 반구 돌기 1024^2
       tactile_yellow_diff.png / tactile_yellow_nor.png (DX 노멀)

재실행 가능: 이미 있고 크기(다운로드분)가 맞으면 skip.
ambientCG 403 시 브라우저 UA로 재시도(기본이 이미 브라우저 UA).
4K-JPG zip이 없으면 2K-JPG로 폴백하고 보고.
"""
import io
import json
import os
import shutil
import sys
import time
import urllib.request
import zipfile

import numpy as np
from PIL import Image

ASSETS_DIR = os.path.dirname(os.path.abspath(__file__))
RETRIES = 3
TIMEOUT = 300

# 기본 UA: 브라우저 문자열(ambientCG는 curl UA는 되지만 403 대비 브라우저로 통일).
BROWSER_UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
CURL_UA = "curl/8.5.0"  # PolyHaven API가 확인된 UA


def open_url(url, ua):
    req = urllib.request.Request(url, headers={"User-Agent": ua})
    return urllib.request.urlopen(req, timeout=TIMEOUT)


# ---------------------------------------------------------------------------
# ambientCG
# ---------------------------------------------------------------------------
# ID -> canonical prefix
AMBIENTCG = {
    "Tiles038": "plaza_light",
    "PavingStones127": "band_dark",
    "PavingStones111": "plaza_lower",
}
# v5 §공통: 한국 보도 인터로킹 블록 — assets/ 루트에 배치(scene_common TEX dir=ASSETS_DIR)
#
# [W2-A4 식생 조달 · 2026-07-29] 잔디 2세트 추가 — `TEX["grass"]` 교체용.
#   현행 grass 는 PolyHaven `aerial_grass_rock` 인데, 이건 **15 m 상공 이끼 암반
#   항공 스캔**이지 잔디가 아니다(B_groundcover_debris.md §3-a [실측]).
#   4096 px / 15 m = 273 px/m 이라 들잔디 잎 나비 4~7 mm 가 원본에서 1.1~1.9 px —
#   **잎이 원본에 기록돼 있지 않아** 어떤 scale_m 을 줘도 잔디가 나오지 않는다.
#   ambientCG Grass001/004 는 **1.40 × 1.40 m**(API dimensionX/Y = 140 cm [실측])
#   이라 4K 에서 2926 px/m — 잎이 12~20 px 로 실제 해상된다(10.7배).
#   덤으로 청 채널이 살아 있어 `LOOK_CLASS["veg"]` 승격의 spread ≤ 4.0 게이트를
#   통과한다 → 24씬 수관에 가을 낙엽이 씌워지던 규약 위반(B §8)도 같이 죽는다.
#   grass_lawn = 1순위(dark/dense/park), grass_lawn_b = 대안(lush/suburban).
#   **scale_m 은 반드시 1.4** — 배선은 테이블 담당 에이전트 소관(본 조달은 파일만).
#   Grass007(moss/weeds)은 API 가 dimension 0×0 을 반환해 물리 크기 미상 →
#   scale_m 을 근거 있게 못 정하므로 **조달 제외**(같은 실수 반복 금지).
AMBIENTCG_ROOT = {
    "PavingStones131": "paving_interlock",
    "Grass001": "grass_lawn",
    "Grass004": "grass_lawn_b",
}
# zip 내부 접미사 -> canonical 접미사
ACG_SUFFIX = {
    "_Color.jpg": "diff",
    "_NormalDX.jpg": "nor",
    "_Roughness.jpg": "rough",
}


def acg_targets(prefix, dest_dir=None):
    return [os.path.join(dest_dir or ASSETS_DIR, f"{prefix}_{s}.jpg")
            for s in ("diff", "nor", "rough")]


def download_ambientcg(asset_id, prefix, failures, dest_dir=None):
    dest_dir = dest_dir or ASSETS_DIR
    targets = acg_targets(prefix, dest_dir)
    if all(os.path.exists(t) and os.path.getsize(t) > 0 for t in targets):
        print(f"  [skip] {prefix}_* (모두 존재)")
        return
    # 4K 우선, 실패 시 2K 폴백
    for res in ("4K", "2K"):
        url = f"https://ambientcg.com/get?file={asset_id}_{res}-JPG.zip"
        print(f"  [get ] {url}")
        blob = None
        for attempt in range(1, RETRIES + 1):
            for ua in (BROWSER_UA, CURL_UA):
                try:
                    with open_url(url, ua) as r:
                        data = r.read()
                    if len(data) < 100_000:
                        raise IOError(f"응답 과소({len(data)} bytes) — zip 아님")
                    blob = data
                    break
                except Exception as e:
                    print(f"    [retry {attempt}/{RETRIES} ua={ua[:12]}..] {e}")
            if blob is not None:
                break
            time.sleep(2 * attempt)
        if blob is None:
            print(f"  [fail] {asset_id} {res}-JPG zip 다운로드 실패")
            continue
        try:
            zf = zipfile.ZipFile(io.BytesIO(blob))
        except zipfile.BadZipFile as e:
            print(f"  [fail] {asset_id} {res}: zip 손상 {e}")
            continue
        names = zf.namelist()
        placed = {}
        for suffix, canon in ACG_SUFFIX.items():
            match = next((n for n in names if n.endswith(suffix)), None)
            if match is None:
                continue
            dest = os.path.join(dest_dir, f"{prefix}_{canon}.jpg")
            with zf.open(match) as src, open(dest, "wb") as out:
                shutil.copyfileobj(src, out)
            placed[canon] = os.path.getsize(dest)
            print(f"  [ ok ] {os.path.basename(dest)} <- {match} "
                  f"({placed[canon]} bytes)")
        missing = [c for c in ("diff", "nor", "rough") if c not in placed]
        if missing:
            failures.append(f"{asset_id} {res}: 누락 {missing} "
                            f"(zip 내부: {names})")
            continue
        if res != "4K":
            print(f"  [NOTE] {asset_id}: 4K 실패 → {res} 폴백 사용")
            failures.append(f"[FALLBACK] {asset_id}: 4K-JPG 미존재/실패 → "
                            f"{res}-JPG 사용")
        return
    failures.append(f"{asset_id}: 4K/2K 모두 실패")


# ---------------------------------------------------------------------------
# PolyHaven (기존 download_assets.py 패턴)
# ---------------------------------------------------------------------------
PH_API = "https://api.polyhaven.com/files/{slug}"
# slug -> canonical prefix
POLYHAVEN = {
    "granite_tile": "granite_dark",
    "brick_wall_001": "brick_red",
}
# v2 다중 씬 텍스처 (Docs/multi_scene_brief_v2.md §B) — 신규 7세트.
# 기존 PolyHaven 패턴 그대로: 4k jpg diff/nor_dx/rough 를 canonical 이름으로 배치.
POLYHAVEN_V2 = {
    "concrete_wall_008": "concrete_wall",   # 지하도 옹벽·터널
    "brushed_concrete_03": "concrete_floor",  # 지하도 계단·바닥
    "weathered_planks": "wood_dark",        # 침목(목재)
    "park_dirt": "dirt_park",               # 공원 흙길
    "gravel_floor": "gravel",               # 마사토·자갈
    "stone_tiles_02": "stone_flag",         # 자연석 판석
    "rock_wall_08": "rock_wall",            # 석축/사석
}
# v3 다중 씬 텍스처 (Docs/multi_scene_brief_v3.md §C — 신규 6역할).
# PolyHaven API 후보를 썸네일 밝기·색조 PIL 측정으로 역할 적합성 검증 후 선정.
# 전 슬러그 Diffuse/nor_dx/Rough 4k jpg 직접 보유 확인(ARM 폴백 불요).
#   slug                    -> canonical   측정치(썸네일 300px, L=luma)      대안 슬러그
#   stone_wall_05           stone_worn   L=40.8 hue33 sat24 어두운 회갈석  (alt stone_wall_04 L59)
#   red_sandstone_pavement  sandstone    L=62.6 hue30 sat22 황토·적 포장    (alt sandstone_blocks_05 L92 / red_sandstone_tiles L36)
#   marble_01               marble_light L=101  매끈 밝은 기념석(크림톤)   (alt grey_cartago_03 sat8 저채도 / marble_tiles)
#   rusty_metal_04          metal_rust   L=49.5 hue20 sat22 갈적 녹철판     (alt metal_plate_02 L41)
#   painted_plaster_wall    plaster      L=97.5 sat8.3 밝은 무채 회벽       (alt concrete_wall_001 L109 sat4.8)
#   rock_surface            rock_face    L=62.2 hue29 sat26 중명도 회 암반  (alt rock_face_03 L66 sat39 / seaside_rock)
POLYHAVEN_V3 = {
    "stone_wall_05": "stone_worn",           # 사원 마모석(어둡고 불규칙)
    "red_sandstone_pavement": "sandstone",   # 사암 계단(붉은/황토톤)
    "marble_01": "marble_light",             # 밝은 대리석/기념석재
    "rusty_metal_04": "metal_rust",          # 녹슨 철판
    "painted_plaster_wall": "plaster",       # 주택 회벽(파스텔 틴트 베이스)
    "rock_surface": "rock_face",             # 절벽 암반(대형 스케일)
}
# 배치1 나노바나나 씬(scene22~33) 텍스처 — Docs/nanobanana_batch1_geometry_map.md.
# forest_leaves_03: Diffuse/Rough/nor_dx 4k 직접 보유 확인(API 200, 07-27).
POLYHAVEN_V4 = {
    "forest_leaves_03": "leaf_ground",       # 낙엽 지면(C2 낙엽 계단 마운드)
}
# [사실화 v1] 아스팔트 — **flat_gnd 최대 발생원 대응**.
#   sceneD3 정밀 진단: 죽은 픽셀의 **89.8% 가 상수색 아스팔트 차도 한 장**이고
#   국소표준편차 중앙값이 임계의 1/4000 이었다. 같은 평면·같은 광원의 잔디 버지는
#   dead 0.0% — 유일한 차이가 디퓨즈 텍스처 유무였다.
#   실측 스케일(PolyHaven API 확인): asphalt_02 = 3.0×3.0 m 로 텍셀 밀도가 가장 높다.
#   (aerial_asphalt_01 은 30×30 m 라 137 texel/m 뿐 — 비권장.)
#   아스팔트 상수색을 쓰는 씬이 14개라 한 번의 조달로 전부에 적용된다.
POLYHAVEN_V5 = {
    "asphalt_02": "asphalt",                 # 차도·주차장 노면 (3.0 m 타일)
    # [사실화 v1] 눈 — sceneC1 의 `Snow` 는 **33씬 통틀어 단일 재질 최대 면적
    # (88.5%)** 인데 텍스처가 없어 승격이 조용히 실패하고 있었다(C1 flat_gnd 88.3).
    # 상수색 매핑 조사가 실측으로 고른 것: snow_01(2.0 m 타일, 선형평균
    # 0.488/0.474/0.466, sd 0.074, 발자국 요철). Snow002/010A 는 순백 초과,
    # Snow006 은 sd 0.027 로 개선 미미해 탈락.
    "snow_01": "snow",
}
# 배치1 HDRI — overcast(C1 눈·C4 젖은 석재 공유, 무태양 저대비 프로파일)
HDRI_BATCH1 = ["kloofendal_overcast"]        # → assets/kloofendal_overcast_4k.exr
# canonical 접미사 -> 후보 API 키(대소문자 혼재 대응; 'diffuse' 소문자 변형 포함)
PH_MAPS = {
    "diff": ["Diffuse", "diffuse", "diff"],
    "nor_dx": ["nor_dx"],
    "rough": ["Rough", "rough", "rough_ao"],
}
# rough 직접 키가 없는 에셋용 ARM 후보 키(ARM: R=AO, G=Roughness, B=Metalness)
PH_ARM_KEYS = ["arm", "Arm", "ARM", "AoRoughMetal", "arm_ao"]


def pick_key(d, candidates):
    for k in candidates:
        if k in d:
            return k
    return None


def fetch_json(url):
    for attempt in range(1, RETRIES + 1):
        try:
            with open_url(url, CURL_UA) as r:
                return json.load(r)
        except Exception as e:
            print(f"  [api retry {attempt}/{RETRIES}] {url}: {e}")
            time.sleep(2 * attempt)
    return None


def download_file(url, dest, expected_size):
    if os.path.exists(dest):
        actual = os.path.getsize(dest)
        if expected_size is None or actual == expected_size:
            print(f"  [skip] {os.path.basename(dest)} ({actual} bytes)")
            return True
        print(f"  [redo] {os.path.basename(dest)} size {actual}!={expected_size}")
    tmp = dest + ".part"
    for attempt in range(1, RETRIES + 1):
        try:
            print(f"  [get ] {url} (attempt {attempt}/{RETRIES})")
            with open_url(url, CURL_UA) as r, open(tmp, "wb") as f:
                while True:
                    chunk = r.read(1 << 20)
                    if not chunk:
                        break
                    f.write(chunk)
            actual = os.path.getsize(tmp)
            if expected_size is not None and actual != expected_size:
                raise IOError(f"size mismatch {actual} != {expected_size}")
            os.replace(tmp, dest)
            print(f"  [ ok ] {os.path.basename(dest)} ({actual} bytes)")
            return True
        except Exception as e:
            print(f"  [fail] attempt {attempt}/{RETRIES}: {e}")
            if os.path.exists(tmp):
                os.remove(tmp)
            time.sleep(2 * attempt)
    return False


def build_rough_from_arm(data, arm_key, dest, failures, slug):
    """ARM 텍스처의 G채널(Roughness)을 추출해 rough 로 저장 (PIL)."""
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        print(f"  [skip] {os.path.basename(dest)} (존재)")
        return True
    try:
        entry = data[arm_key]["4k"]["jpg"]
    except KeyError as e:
        failures.append(f"{slug}: ARM '{arm_key}' 4k:jpg 누락 {e}")
        return False
    tmp = dest + ".arm"  # dest 와 충돌하지 않는 임시 경로
    if not download_file(entry["url"], tmp, entry.get("size")):
        failures.append(f"{slug}: ARM 다운로드 실패 ({entry['url']})")
        if os.path.exists(tmp):
            os.remove(tmp)
        return False
    try:
        with Image.open(tmp) as img:
            g = img.convert("RGB").split()[1]  # G = Roughness
            g.save(dest, quality=95)
        os.remove(tmp)
        print(f"  [ ok ] {os.path.basename(dest)} <- ARM('{arm_key}') G채널 "
              f"({os.path.getsize(dest)} bytes)")
        return True
    except Exception as e:
        failures.append(f"{slug}: ARM G채널 추출 실패 {e}")
        if os.path.exists(tmp):
            os.remove(tmp)
        return False


def download_hdri(slug, failures):
    """PolyHaven HDRI 4k exr → assets/ 루트(기존 관례: qwantani_*.exr 위치)."""
    print(f"[hdri] {slug}")
    data = fetch_json(PH_API.format(slug=slug))
    if data is None:
        failures.append(f"{slug}: API 응답 없음(hdri)")
        return
    try:
        entry = data["hdri"]["4k"]["exr"]
    except KeyError as e:
        failures.append(f"{slug}:hdri:4k:exr (API 누락 {e})")
        return
    dest = os.path.join(os.path.dirname(ASSETS_DIR), f"{slug}_4k.exr")
    if not download_file(entry["url"], dest, entry.get("size")):
        failures.append(f"{slug}:hdri:4k:exr ({entry['url']})")


def download_polyhaven(slug, prefix, failures):
    print(f"[polyhaven] {slug} -> {prefix}")
    data = fetch_json(PH_API.format(slug=slug))
    if data is None:
        failures.append(f"{slug}: API 응답 없음")
        return
    for canon, candidates in PH_MAPS.items():
        key = pick_key(data, candidates)
        dest = os.path.join(ASSETS_DIR, f"{prefix}_{canon}.jpg")
        if key is None:
            # rough 특례: 직접 rough 키가 없고 ARM 이 있으면 G채널 추출로 생성.
            if canon == "rough":
                arm_key = pick_key(data, PH_ARM_KEYS)
                if arm_key is not None:
                    if build_rough_from_arm(data, arm_key, dest, failures, slug):
                        failures.append(
                            f"[ARM-EXTRACT] {slug}: 직접 rough 키 없음 → "
                            f"'{arm_key}'(ARM) G채널 추출로 rough 생성")
                    continue
            failures.append(f"{slug}:{canon} (매칭 키 없음; "
                            f"top keys: {sorted(data.keys())})")
            continue
        try:
            entry = data[key]["4k"]["jpg"]
        except KeyError as e:
            failures.append(f"{slug}:{key}:4k:jpg (API 누락 {e})")
            continue
        if not download_file(entry["url"], dest, entry.get("size")):
            failures.append(f"{slug}:{key}:4k:jpg ({entry['url']})")


# ---------------------------------------------------------------------------
# 점자블록 절차 생성 (브리프 §4)
# ---------------------------------------------------------------------------
# 물리 치수는 여기 한 곳에만 둔다 — 픽셀 상수(`N/8.0` 같은)로 흩어 놓으면
# "타일 300 mm 에서 돌기가 몇 mm 인가" 를 아무도 못 읽는다.
TACTILE_TILE_MM = 300.0     # [법령] 교통약자법 시행규칙 별표1 2호 차목 — 300 mm 판
TACTILE_DOT_D_MM = 25.0     # [결재 B7 · 2026-07-29] 38.1 → **25 mm**
#   구판은 `dot_d = N/8.0` = 128 px = **37.5 mm**(외곽 림 포함 실측 38.1) 였다.
#   국내·국제 관행 22~25 mm 대비 1.5~1.7배로, 돌기 면적률을 19.6 % → 45.6 % 로
#   끌어올려 §12.5-4 의 "휘도 단차" 목표와 **정반대로** 작동했다
#   [실측 — w2_surgeon_v1.md §3.5 · redteam_w2_foundations.md §4].
#   25 mm 는 관행 상한이자 피치 50 mm 의 정확히 1/2 — 돌기 사이 간격 = 돌기 지름.


def build_tactile(failures, force=False):
    diff_path = os.path.join(ASSETS_DIR, "tactile_yellow_diff.png")
    nor_path = os.path.join(ASSETS_DIR, "tactile_yellow_nor.png")
    if (os.path.exists(diff_path) and os.path.exists(nor_path)
            and not force):
        print("  [skip] tactile_yellow_* (존재)")
        return
    print("[tactile] 6x6 반구 돌기 절차 생성 (1024^2) "
          f"— 돌기 Ø {TACTILE_DOT_D_MM:.0f} mm / 타일 {TACTILE_TILE_MM:.0f} mm")
    try:
        N = 1024
        grid = 6                       # 6x6 돌기 [법령] 36점
        cell = N / grid                # 셀 크기 ≈ 170.7 px = 피치 50.0 mm
        dot_d = N * TACTILE_DOT_D_MM / TACTILE_TILE_MM     # 25 mm → 85.33 px
        dot_r = dot_d / 2.0

        yy, xx = np.meshgrid(np.arange(N), np.arange(N), indexing="ij")

        # 높이맵: 각 돌기를 반구로. h = sqrt(1-(d/r)^2)
        height = np.zeros((N, N), np.float32)
        for gi in range(grid):
            for gj in range(grid):
                cx = (gj + 0.5) * cell
                cy = (gi + 0.5) * cell
                d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
                mask = d < dot_r
                r_norm = np.clip(d / dot_r, 0.0, 1.0)
                dome = np.sqrt(np.clip(1.0 - r_norm ** 2, 0.0, 1.0))
                height = np.where(mask & (dome > height), dome, height)

        # ---- diff: 안전 황색 + 노이즈 + 모서리 마모 ----
        base = np.array([0xF5, 0xC4, 0x00], np.float32)  # #F5C400
        rng = np.random.default_rng(4)
        noise = rng.normal(0.0, 6.0, (N, N, 1)).astype(np.float32)
        col = np.broadcast_to(base, (N, N, 3)).copy()
        # 돌기 상단은 살짝 밝게(하이라이트), 바닥골은 살짝 어둡게
        shade = (0.90 + 0.18 * height)[..., None]
        col = col * shade + noise
        # 타일 모서리 마모(가장자리로 갈수록 어둡고 채도 낮게)
        ex = np.minimum(xx, N - 1 - xx) / (N * 0.5)
        ey = np.minimum(yy, N - 1 - yy) / (N * 0.5)
        edge = np.clip(np.minimum(ex, ey) * 4.0, 0.0, 1.0)  # 0=모서리
        wear = (0.82 + 0.18 * edge)[..., None]
        col = col * wear
        col = np.clip(col, 0, 255).astype(np.uint8)
        Image.fromarray(col, "RGB").save(diff_path)
        print(f"  [ ok ] {os.path.basename(diff_path)} "
              f"({os.path.getsize(diff_path)} bytes)")

        # ---- nor: 높이맵 그래디언트 → DX 노멀 (G채널 뒤집기) ----
        # Sobel
        kx = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], np.float32)
        ky = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], np.float32)

        def conv3(img, k):
            p = np.pad(img, 1, mode="edge")
            out = np.zeros_like(img)
            for i in range(3):
                for j in range(3):
                    out += k[i, j] * p[i:i + N, j:j + N]
            return out

        strength = 3.0
        gx = conv3(height, kx) * strength
        gy = conv3(height, ky) * strength
        nx = -gx
        # DX 규약: G 채널 뒤집기(GL은 -gy, DX는 +gy)
        ny = gy
        nz = np.ones_like(height)
        norm = np.sqrt(nx * nx + ny * ny + nz * nz)
        nx, ny, nz = nx / norm, ny / norm, nz / norm
        nmap = np.stack([nx, ny, nz], axis=-1)
        nmap = ((nmap * 0.5 + 0.5) * 255.0).clip(0, 255).astype(np.uint8)
        Image.fromarray(nmap, "RGB").save(nor_path)
        print(f"  [ ok ] {os.path.basename(nor_path)} "
              f"({os.path.getsize(nor_path)} bytes)")
    except Exception as e:
        failures.append(f"tactile 생성 실패: {e}")


# ---------------------------------------------------------------------------
def main():
    os.makedirs(ASSETS_DIR, exist_ok=True)
    failures = []

    print("=== ambientCG ===")
    for asset_id, prefix in AMBIENTCG.items():
        print(f"[ambientcg] {asset_id} -> {prefix}")
        download_ambientcg(asset_id, prefix, failures)

    root_dir = os.path.dirname(ASSETS_DIR)
    for asset_id, prefix in AMBIENTCG_ROOT.items():
        print(f"[ambientcg] {asset_id} -> ../{prefix}")
        download_ambientcg(asset_id, prefix, failures, dest_dir=root_dir)

    print("\n=== PolyHaven ===")
    for slug, prefix in POLYHAVEN.items():
        download_polyhaven(slug, prefix, failures)

    print("\n=== PolyHaven v2 (multi_scene §B — 신규 7세트) ===")
    for slug, prefix in POLYHAVEN_V2.items():
        download_polyhaven(slug, prefix, failures)

    print("\n=== PolyHaven v3 (multi_scene_v3 §C — 신규 6역할) ===")
    for slug, prefix in POLYHAVEN_V3.items():
        download_polyhaven(slug, prefix, failures)

    print("\n=== PolyHaven v4 (나노바나나 배치1 scene22~33) ===")
    for slug, prefix in POLYHAVEN_V5.items():
        download_polyhaven(slug, prefix, failures)

    for slug, prefix in POLYHAVEN_V4.items():
        download_polyhaven(slug, prefix, failures)
    for slug in HDRI_BATCH1:
        download_hdri(slug, failures)

    print("\n=== Tactile block (PIL) ===")
    build_tactile(failures)

    print("\n=== 검증 ===")
    expected = []
    for prefix in AMBIENTCG.values():
        expected += [f"{prefix}_diff.jpg", f"{prefix}_nor.jpg",
                     f"{prefix}_rough.jpg"]
    for prefix in (list(POLYHAVEN.values()) + list(POLYHAVEN_V2.values())
                   + list(POLYHAVEN_V3.values()) + list(POLYHAVEN_V4.values())
                   + list(POLYHAVEN_V5.values())):
        expected += [f"{prefix}_diff.jpg", f"{prefix}_nor_dx.jpg",
                     f"{prefix}_rough.jpg"]
    expected += ["tactile_yellow_diff.png", "tactile_yellow_nor.png"]

    # assets/ 루트에 놓이는 항목(HDRI·인터로킹 블록)
    expected_root = [f"{slug}_4k.exr" for slug in HDRI_BATCH1]
    for prefix in AMBIENTCG_ROOT.values():
        expected_root += [f"{prefix}_{s}.jpg" for s in ("diff", "nor", "rough")]
    checks = ([(ASSETS_DIR, n) for n in expected]
              + [(os.path.dirname(ASSETS_DIR), n) for n in expected_root])
    expected = expected + expected_root

    total = 0
    missing = []
    for base, name in checks:
        p = os.path.join(base, name)
        if os.path.exists(p) and os.path.getsize(p) > 0:
            total += os.path.getsize(p)
            print(f"  OK   {name:32s} {os.path.getsize(p):>12,} bytes")
        else:
            missing.append(name)
            print(f"  MISS {name}")

    print(f"\n총 {len(expected)-len(missing)}/{len(expected)} 파일, "
          f"{total:,} bytes ({total/1e6:.1f} MB)")

    # 소프트 실패(폴백 등)와 하드 실패 구분
    hard = [f for f in failures if not f.startswith("[FALLBACK]")]
    if failures:
        print("\n특이사항:")
        for f in failures:
            print(f"  - {f}")
    if missing or hard:
        sys.exit(1)
    print("\n모든 필수 에셋 배치 완료.")


if __name__ == "__main__":
    main()
