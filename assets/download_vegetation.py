#!/usr/bin/env python3
"""Download NVIDIA Omniverse vegetation USD assets for NegObs 사실화 라운드.

현재 씬의 나무는 실린더 줄기 + 구(sphere) 수관이다. 조사 `ZZ_synthesis.md` §10.1 이
지목한 대로 NVIDIA 콘텐츠 S3 버킷에 실제 나무 에셋(나무 44종 + 관목 37종)이 있고
**인증 없이** 받을 수 있다. 이 스크립트가 그 최소 세트를 조달한다.

[에셋 감사 v1 확장 — 2026-07-28]
  나무만이 아니다. 낙엽·자갈·바위·관목도 전부 **평면 텍스처**로 때우고 있었고
  (`leaf_ground` 텍스처를 깐 `build_slope` 판 = 장판, `_oriented_box` 잡석,
   `build_hedge` 박스+블롭 = 관목), S3 에 대응하는 실제 3D 에셋이 있다.
  카탈로그 실측(`Docs/reports/asset_audit_v1.md`):
      Debris  5 USD   낙엽 낱장·클러스터   ← "장판" 을 끝내는 핵심 에셋
      Leaves  5 USD   Debris 와 **동일 지오메트리**, 재질만 다름(아래 주의)
      Rocks  15 USDA  0.13~0.31 m 잡석/호박돌
      Shrub  37 USD   관목 (한국 조경 대응종 다수)
      Trees  44 USD   교목
      Plant_Tropical 17 USD  야자·바나나·고사리 — **한국 환경 부적합, 조달 안 함**
  이 스크립트는 이제 카테고리별로 나뉘어 있고 `--only` 로 선택 조달한다.

Re-runnable: 이미 받았고 크기가 맞는 파일은 skip 한다 (`download_assets.py` 와 동일 규약).
각 다운로드는 3회까지 재시도하고 S3 HEAD 의 `Content-Length` 로 검증한다.
ETag 가 멀티파트("-" 포함)가 아니면 MD5 로 한 번 더 검증한다.

라이선스 (중요 — `Docs/CREDITS.md` 참조):
  NVIDIA Omniverse 에셋은 CC0 가 **아니다**. 렌더 이미지 공개는 가능하나
  **USD/텍스처 원본 재배포는 금지**다. 따라서 `assets/vegetation/` 은 반드시
  `.gitignore` 로 제외하고, 재현은 이 스크립트로 한다.

────────────────────────────────────────────────────────────────────────────
USD 종속 구조 (이 스크립트의 존재 이유)
────────────────────────────────────────────────────────────────────────────
`.usd` 하나만 받으면 재질이 전부 깨진다. 종속은 3단이며 전부 **상대 경로**다:

  Trees/Japanese_Cherry.usd
    └─ info:mdl:sourceAsset = @./materials/bark3.mdl@          (USD → MDL)
         └─ texture_2d("./textures/bark3_basecolor.png")        (MDL → 텍스처)

  Shrub/Boxwood.usd
    └─ @../Trees/materials/bark3.mdl@   ← **폴더를 벗어나는 상대 경로!**

즉 S3 의 `Assets/Vegetation/` 디렉터리 구조를 **그대로 미러링해야** 한다.
평평하게 펼치면 Boxwood 의 `../Trees/...` 가 깨진다. 경로 재작성은 불필요하다 —
구조만 보존하면 상대 경로가 그대로 해석된다.

추가 함정: `hollyprivet_basecolor.png` 는 `Trees/materials/textures/`(628 KB)와
`Shrub/materials/textures/`(2.6 MB)에 **같은 이름 다른 내용**으로 각각 존재한다.
반드시 참조하는 MDL 과 같은 폴더의 사본을 받아야 한다.

MANIFEST 는 아래 절차로 기계적으로 도출했다(재현 가능, pxr 필요 — Isaac 불필요.
`pip install usd-core` 로 충분하다):
  1. `Sdf.Layer.FindOrOpen(usd)` → 모든 attribute 중 `Sdf.AssetPath` 값 수집
     → `info:mdl:sourceAsset` 두 개가 나온다.
  2. 그 `.mdl` 을 텍스트로 받아 `texture_2d("...")` 를 grep.
  3. MDL 의 `./textures/...` 는 **MDL 파일 위치 기준** 상대 경로다.
`--discover Shrub/Holly.usd` 로 이 절차를 그대로 자동 실행할 수 있다(아래 참조).
남은 39 수종·32 관목을 추가할 때 추측하지 말고 이걸 쓸 것.

────────────────────────────────────────────────────────────────────────────
카테고리별 함정 (감사 v1 실측)
────────────────────────────────────────────────────────────────────────────
· **Debris vs Leaves**: 두 폴더의 5개 USD 는 바운딩박스가 **바이트 단위로 같다**
  (동일 지오메트리). 차이는 재질뿐이다.
    Debris/*.usd  → ./materials/fallleaves.mdl  + 3 텍스처(BaseColor/Normal/Rough)
    Leaves/*.usd  → ./material.mdl              + basecolor.png/normal.jpg/roughness.jpg
  그런데 `Leaves/cluster_2.usd` 는 `./basecolor.jpg` 를 참조하는데 그 파일은
  **S3 에 존재하지 않는다**(있는 건 basecolor.png). 게다가 normal/roughness 슬롯이
  서로 바뀌어 있다. → **Debris/ 쪽만 쓴다.** Leaves/ 는 조달하지 않는다.
· **Rocks**: `@OmniPBR.mdl@` 를 검색 경로로 참조한다(상대 경로 아님). Isaac 이
  기본 제공하므로 MDL 은 받을 필요가 없다 — `.usda` + 텍스처 3장이면 끝.
  원점이 **바위 중심**이라 z 최소가 음수다(예: rock_small_01 은 −0.128 m).
  지면에 놓을 때 z 를 그만큼 올려야 반쯤 묻히지 않는다.
· **Shrub 의 줄기 재질은 전부 `../Trees/materials/` 를 참조한다**(Boxwood·Privet·
  Forsythia·Juniper·Burning_Bush = bark3, Rhododendron = TreeBark_01).
  즉 Shrub 만 받으면 줄기가 깨진다. 아래 SHRUB 세트는 그 종속을 포함한다.
· `bark3_*.png` 는 Trees/ 와 Shrub/ 양쪽에 있으나 **크기가 동일**(같은 파일)이라
  어느 쪽을 받아도 되지만, hollyprivet 은 아니다(위 함정 참조).
"""
import hashlib
import os
import sys
import time
import urllib.request

ASSETS_DIR = os.path.dirname(os.path.abspath(__file__))
VEG_DIR = os.path.join(ASSETS_DIR, "vegetation")
BASE = ("https://omniverse-content-production.s3.us-west-2.amazonaws.com/"
        "Assets/Vegetation/")
RETRIES = 3
TIMEOUT = 300
HEADERS = {"User-Agent": "curl/8.5.0"}


def open_url(url, method="GET"):
    req = urllib.request.Request(url, headers=HEADERS, method=method)
    return urllib.request.urlopen(req, timeout=TIMEOUT)


# ── 조달 세트 ────────────────────────────────────────────────────────────────
# key = S3 키(Assets/Vegetation/ 이후) = 로컬 assets/vegetation/ 이후 경로.
# 각 나무의 종속물은 위 절차로 실제 도출한 것이며 추측이 아니다.
BARK3 = [
    "Trees/materials/bark3.mdl",
    "Trees/materials/textures/bark3_basecolor.png",
    "Trees/materials/textures/bark3_normal.png",
    "Trees/materials/textures/bark3_roughness.png",
]
PINE_MATS = [
    "Trees/materials/Pine_needles.mdl",
    "Trees/materials/textures/pine_needles.png",
    "Trees/materials/TreeBark_10.mdl",
    "Trees/materials/textures/alter49_tree10_basecolor.png",
    "Trees/materials/textures/alter49_tree10_normal.png",
    "Trees/materials/textures/alter49_tree10_roughness.png",
]

TREEBARK_01 = [                       # Rhododendron 줄기 (Shrub → ../Trees)
    "Trees/materials/TreeBark_01.mdl",
    "Trees/materials/textures/alter49_tree1_basecolor.png",
    "Trees/materials/textures/alter49_tree1_normal.png",
    "Trees/materials/textures/alter49_tree1_roughness.png",
]
# 낙엽 재질 1종을 Debris 의 5개 USD 가 전부 공유한다. Normal 이 47 MB 로 큰데
# 이게 낙엽 낱장의 잎맥·말림을 만드는 성분이라 줄이면 다시 '무늬'가 된다.
FALLLEAVES_MAT = [
    "Debris/materials/fallleaves.mdl",
    "Debris/materials/textures/fallleaves_1_BaseColor.png",
    "Debris/materials/textures/deadleaves_1_Normal.png",
    "Debris/materials/textures/deadleaves_1_Roughness.png",
]


def _rock(idx):
    """rock_small_NN 한 개의 키 목록. MDL 은 OmniPBR(검색경로) 라 불필요."""
    n = f"{idx:02d}"
    return [f"Rocks/rock_small_{n}.usda",
            f"Rocks/textures/rock_small_{n}_basecolor.jpg",
            f"Rocks/textures/rock_small_{n}_normal.jpg",
            f"Rocks/textures/rock_small_{n}_orm.jpg"]


# ── 카테고리 ────────────────────────────────────────────────────────────────
# CATEGORIES[이름] = [(라벨, 필수, [S3 키...]), ...]
#   `--only 이름[,이름...]` 으로 선택 조달. 인자 없으면 전 카테고리.
#   `--required-only` 는 선택된 카테고리 안에서 required=True 만 받는다.
CATEGORIES = {}

# --- trees: 교목 (기존 세트 — 하위호환 유지) --------------------------------
CATEGORIES["trees"] = [
    ("벚나무 Japanese_Cherry (한국 가로수 상위 수종)", True, [
        "Trees/Japanese_Cherry.usd",
        "Trees/materials/JapaneseCherry_blossom_Mat.mdl",
        "Trees/materials/textures/cherryblossom.png",
    ] + BARK3),

    ("소나무 Yellow_Pine (성목 실루엣)", False,
     ["Trees/Yellow_Pine.usd"] + PINE_MATS),

    ("소나무 White_Pine (848 KB, 원경/LOD용 — 재질은 Yellow_Pine 과 공유)", False,
     ["Trees/White_Pine.usd"] + PINE_MATS),
]

# --- leaf_litter: 낙엽 (Debris) ---------------------------------------------
# **최우선 카테고리.** sceneC2·07·10·D3 의 낙엽은 지금 `leaf_ground` 텍스처를
# 입힌 평판(build_slope)과 두께 6 mm 짜리 납작 타원체 900개다. 위에서 보면
# 무늬, 옆에서 보면 판 — 감독이 지적한 "장판".  아래 5종은 실제 잎 지오메트리다.
# 네이티브 치수(실측, metersPerUnit=0.01):
#   fallcluster1  0.419 × 0.395 × 0.042 m   ← 덩어리(약 40 cm 사방)
#   fallcluster2  0.241 × 0.266 × 0.042 m   ← 작은 덩어리
#   maplefall1    0.103 × 0.172 × 0.023 m   ← 단풍 낱장
#   oakfall1      0.080 × 0.175 × 0.023 m   ← 참나무 낱장
#   oakfall2      0.094 × 0.190 × 0.018 m   ← 참나무 낱장(다른 말림)
CATEGORIES["leaf_litter"] = [
    ("낙엽 클러스터 fallcluster1 (0.42 m 사방 — 퇴적 바탕 깔개)", True,
     ["Debris/fallcluster1.usd"] + FALLLEAVES_MAT),
    ("낙엽 클러스터 fallcluster2 (0.24×0.27 m — 성긴 산포)", True,
     ["Debris/fallcluster2.usd"] + FALLLEAVES_MAT),
    ("낙엽 낱장 maplefall1 (단풍, 10×17 cm)", True,
     ["Debris/maplefall1.usd"] + FALLLEAVES_MAT),
    ("낙엽 낱장 oakfall1 (참나무, 8×18 cm)", True,
     ["Debris/oakfall1.usd"] + FALLLEAVES_MAT),
    ("낙엽 낱장 oakfall2 (참나무, 9×19 cm)", True,
     ["Debris/oakfall2.usd"] + FALLLEAVES_MAT),
]

# --- rocks: 잡석·호박돌 ------------------------------------------------------
# scene12 호안 잡석 96개 = 랜덤 회전 박스, scene03 riprap = 평판.
# 아래 5종은 크기 대역을 고르게 덮도록 15종 실측치에서 뽑았다(장변 기준):
#   rock_small_01  0.314 × 0.302 × 0.253 m  (최대)
#   rock_small_15  0.228 × 0.224 × 0.173 m
#   rock_small_08  0.223 × 0.197 × 0.162 m
#   rock_small_10  0.162 × 0.151 × 0.116 m
#   rock_small_09  0.128 × 0.113 × 0.067 m  (최소, 자갈)
# 나머지 10종(02~07,11~14)은 0.16~0.24 m 대역에 몰려 있어 대표성이 낮다.
CATEGORIES["rocks"] = [
    ("잡석 rock_small_01 (0.31 m — 호안 대석)", True, _rock(1)),
    ("잡석 rock_small_15 (0.23 m)", True, _rock(15)),
    ("잡석 rock_small_08 (0.22 m)", True, _rock(8)),
    ("잡석 rock_small_10 (0.16 m)", True, _rock(10)),
    ("자갈 rock_small_09 (0.13 m — 최소)", True, _rock(9)),
]

# --- shrub: 관목 (한국 조경 대응종) -----------------------------------------
# 네이티브 치수(실측, 폭X × 폭Y × 높이Z):
#   Boxwood       1.01 × 1.01 × 0.74 m   회양목
#   Juniper       0.46 × 0.45 × 0.90 m   향나무류(직립 소형)
#   Privet        1.70 × 1.64 × 1.11 m   쥐똥나무 — 생울타리 최다종
#   Rhododendron  2.55 × 2.37 × 2.01 m   철쭉/진달래  (z 최소 −0.42 m 주의!)
#   Burning_Bush  2.64 × 2.60 × 1.60 m   화살나무(가을 홍엽)
#   Forsythia     3.54 × 3.65 × 2.32 m   개나리
CATEGORIES["shrub"] = [
    ("관목 Boxwood 회양목 (보도 화단·연석 가림 — 낙차 폐색 실험용)", True, [
        "Shrub/Boxwood.usd",
        "Shrub/materials/Boxwood_leaf_Mat.mdl",
        "Shrub/materials/textures/hollyprivet_basecolor.png",
        "Shrub/materials/textures/hollyprivet_normal.png",
        "Shrub/materials/textures/hollyprivet_roughness.png",
        # Boxwood 의 줄기는 ../Trees/materials/bark3.mdl 을 참조한다.
    ] + BARK3),

    ("관목 Privet 쥐똥나무 (한국 생울타리 1위 — build_hedge 직접 대체)", True, [
        "Shrub/Privet.usd",
        "Shrub/materials/HollyPrivet_Mat.mdl",
        "Shrub/materials/textures/hollyprivet_basecolor.png",
        "Shrub/materials/textures/hollyprivet_normal.png",
        "Shrub/materials/textures/hollyprivet_roughness.png",
    ] + BARK3),

    ("관목 Rhododendron 철쭉 (공원·아파트 화단 최다)", True, [
        "Shrub/Rhododendron.usd",
        "Shrub/materials/Rhododendron.mdl",
        "Shrub/materials/textures/rhododendron_basecolor.png",
        "Shrub/materials/textures/rhododendron_normal.png",
        "Shrub/materials/textures/rhododendron_roughness.png",
    ] + TREEBARK_01),

    ("관목 Juniper 향나무 (상록 — 겨울 씬 C1 에서 유일하게 안 죽는 식생)", True,
     ["Shrub/Juniper.usd"] + PINE_MATS[:2] + BARK3),

    ("관목 Burning_Bush 화살나무 (가을 홍엽 — 낙엽 씬 C2 와 계절 정합)", True, [
        "Shrub/Burning_Bush.usd",
        "Shrub/materials/BurningBush_leaf_Mat.mdl",
        "Shrub/materials/textures/burningbush_leaf_basecolor.png",
        "Shrub/materials/textures/burningbush_leaf_normal.png",
        "Shrub/materials/textures/burningbush_leaf_roughness.png",
    ] + BARK3),

    ("관목 Forsythia 개나리 (사면 녹화·봄 — 3.5 m 로 크다, 스케일 필수)", False, [
        "Shrub/Forsythia.usd",
        "Shrub/materials/Meadowlark_flowers.mdl",
        "Shrub/materials/textures/forsythiaflower_basecolor.png",
        "Shrub/materials/textures/forsythiaflower_normal.png",
    ] + BARK3),
]

# 하위호환: 예전에 `from download_vegetation import SETS` 를 쓴 코드가 있을 수 있다.
SETS = CATEGORIES["trees"] + CATEGORIES["shrub"][:1]


def head(url):
    """(size, md5_or_None) — S3 HEAD. ETag 가 멀티파트면 md5 는 None."""
    for attempt in range(1, RETRIES + 1):
        try:
            with open_url(url, method="HEAD") as r:
                size = int(r.headers["Content-Length"])
                etag = (r.headers.get("ETag") or "").strip('"')
                md5 = etag if (len(etag) == 32 and "-" not in etag) else None
                return size, md5
        except Exception as e:
            print(f"  [head retry {attempt}/{RETRIES}] {url}: {e}")
            time.sleep(2 * attempt)
    return None, None


def md5sum(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def download(url, dest, expected_size, expected_md5):
    """Download url -> dest. Skip if already present with correct size."""
    name = os.path.relpath(dest, VEG_DIR)
    if os.path.exists(dest):
        actual = os.path.getsize(dest)
        if expected_size is None or actual == expected_size:
            print(f"  [skip] {name} ({actual} bytes, already present)")
            return True
        print(f"  [redo] {name} size mismatch ({actual} != {expected_size})")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    tmp = dest + ".part"
    for attempt in range(1, RETRIES + 1):
        try:
            print(f"  [get ] {name} (attempt {attempt}/{RETRIES})")
            with open_url(url) as r, open(tmp, "wb") as f:
                while True:
                    chunk = r.read(1 << 20)
                    if not chunk:
                        break
                    f.write(chunk)
            actual = os.path.getsize(tmp)
            if expected_size is not None and actual != expected_size:
                raise IOError(f"size mismatch {actual} != {expected_size}")
            if expected_md5 is not None:
                got = md5sum(tmp)
                if got != expected_md5:
                    raise IOError(f"md5 mismatch {got} != {expected_md5}")
            os.replace(tmp, dest)
            print(f"  [ ok ] {name} ({actual} bytes)")
            return True
        except Exception as e:
            print(f"  [fail] attempt {attempt}/{RETRIES}: {e}")
            if os.path.exists(tmp):
                os.remove(tmp)
            time.sleep(2 * attempt)
    return False


def verify(keys):
    """받은 파일의 헤더를 확인한다. USD 는 PXR-USDC 또는 #usda 여야 한다."""
    bad = []
    for key in keys:
        path = os.path.join(VEG_DIR, key)
        if not os.path.exists(path):
            bad.append(f"{key} (없음)")
            continue
        with open(path, "rb") as f:
            head8 = f.read(8)
        if key.endswith((".usd", ".usda")) and not (
                head8.startswith(b"PXR-USDC") or head8.startswith(b"#usda")):
            bad.append(f"{key} (USD 헤더 아님: {head8!r})")
        elif key.endswith(".png") and not head8.startswith(b"\x89PNG\r\n\x1a\n"):
            bad.append(f"{key} (PNG 헤더 아님: {head8!r})")
        elif key.endswith(".jpg") and not head8.startswith(b"\xff\xd8\xff"):
            bad.append(f"{key} (JPEG 헤더 아님: {head8!r})")
        elif key.endswith(".mdl") and not head8.startswith(b"mdl "):
            bad.append(f"{key} (MDL 헤더 아님: {head8!r})")
    return bad


# ── 카테고리 조달 함수 ───────────────────────────────────────────────────────
def fetch_category(name, only_required=False, fetched=None, failures=None):
    """카테고리 하나를 조달한다. 감독이 개별 호출할 수 있게 함수로 분리.

        python -c "import download_vegetation as d; d.fetch_category('rocks')"

    fetched/failures 를 넘기면 여러 카테고리에 걸쳐 중복 다운로드를 막는다.
    반환: (fetched, failures)."""
    if name not in CATEGORIES:
        raise KeyError(f"모르는 카테고리 {name!r} — {sorted(CATEGORIES)}")
    fetched = [] if fetched is None else fetched
    failures = [] if failures is None else failures
    print(f"══ 카테고리 {name} ══")
    for label, required, keys in CATEGORIES[name]:
        if only_required and not required:
            print(f"[skip set] {label} (--required-only)")
            continue
        print(f"[set] {label}")
        for key in keys:
            if key in fetched:
                continue  # 공유 재질(bark3·fallleaves 등)은 한 번만
            url = BASE + key
            size, md5 = head(url)
            if size is None:
                failures.append(f"{key} (S3 HEAD 실패)")
                continue
            if download(url, os.path.join(VEG_DIR, key), size, md5):
                fetched.append(key)
            else:
                failures.append(f"{key} ({url})")
    return fetched, failures


def discover(usd_key):
    """S3 의 USD 하나에서 종속(MDL·텍스처) 키 목록을 **기계적으로** 도출한다.

    남은 39 수종·32 관목을 MANIFEST 에 추가할 때 쓴다. 추측 금지.
    pxr 필요 (`pip install usd-core`, Isaac 불필요). 결과를 그대로 붙여넣으면 된다.

        python assets/download_vegetation.py --discover Shrub/Holly.usd
    """
    import posixpath
    import re
    import tempfile
    try:
        from pxr import Sdf
    except ImportError:
        print("[discover] pxr 가 없다. Isaac 은 필요 없고 아래로 충분하다:\n"
              "  python3 -m venv /tmp/usdvenv && /tmp/usdvenv/bin/pip install usd-core\n"
              "  /tmp/usdvenv/bin/python assets/download_vegetation.py "
              "--discover " + usd_key)
        sys.exit(2)

    def _norm(base_key, rel):
        return posixpath.normpath(posixpath.join(
            posixpath.dirname(base_key), rel.lstrip("./") if
            rel.startswith("./") else rel))

    tmpdir = tempfile.mkdtemp(prefix="negobs_discover_")
    local = os.path.join(tmpdir, os.path.basename(usd_key))
    size, md5 = head(BASE + usd_key)
    if not download(BASE + usd_key, local, size, md5):
        print(f"[discover] {usd_key} 받기 실패")
        return []

    lay = Sdf.Layer.FindOrOpen(local)
    mdls, direct = [], []

    def walk(spec):
        for a in spec.attributes:
            v = a.default
            vals = ([v] if isinstance(v, Sdf.AssetPath)
                    else list(v) if isinstance(v, Sdf.AssetPathArray) else [])
            for p in vals:
                if not p.path:
                    continue
                k = _norm(usd_key, p.path)
                (mdls if k.endswith(".mdl") else direct).append(k)
        for c in spec.nameChildren:
            walk(c)
    for c in lay.rootPrims:
        walk(c)

    keys = [usd_key]
    for m in sorted(set(mdls)):
        if m.count("/") == 0:      # @OmniPBR.mdl@ 등 검색경로 MDL — 조달 불필요
            print(f"[discover] 검색경로 MDL(조달 불필요): {m}")
            continue
        keys.append(m)
        mlocal = os.path.join(tmpdir, m.replace("/", "_"))
        s2, h2 = head(BASE + m)
        if s2 is None or not download(BASE + m, mlocal, s2, h2):
            print(f"[discover] MDL 받기 실패: {m}")
            continue
        with open(mlocal, "r", errors="replace") as f:
            body = f.read()
        for t in sorted(set(re.findall(r'texture_2d\("([^"]+)"', body))):
            keys.append(_norm(m, t))
    keys.extend(sorted(set(direct)))

    out, seen = [], set()
    for k in keys:
        if k not in seen:
            seen.add(k)
            out.append(k)
    print(f"\n# --- {usd_key} 종속 {len(out)}개 (그대로 CATEGORIES 에 붙여넣기) ---")
    for k in out:
        s, _ = head(BASE + k)
        print(f'    "{k}",'.ljust(72) + f"# {(s or 0) / 1e6:.2f} MB")
    return out


USAGE = """사용법:
  python assets/download_vegetation.py                 # 전 카테고리 조달
  python assets/download_vegetation.py --only leaf_litter,rocks
  python assets/download_vegetation.py --only trees --required-only
  python assets/download_vegetation.py --list          # 카테고리·용량 표
  python assets/download_vegetation.py --discover Shrub/Holly.usd
카테고리: """ + ", ".join(CATEGORIES)


def main():
    argv = sys.argv[1:]
    if "-h" in argv or "--help" in argv:
        print(USAGE)
        return
    if "--discover" in argv:
        i = argv.index("--discover")
        if i + 1 >= len(argv):
            print("--discover 뒤에 S3 키가 필요하다 (예: Shrub/Holly.usd)")
            sys.exit(2)
        discover(argv[i + 1])
        return
    if "--list" in argv:
        for name, sets in CATEGORIES.items():
            print(f"{name}:")
            for label, required, keys in sets:
                mark = "필수" if required else "선택"
                print(f"  [{mark}] {label}  ({len(keys)} 파일)")
        return

    only_required = "--required-only" in argv
    if "--only" in argv:
        i = argv.index("--only")
        if i + 1 >= len(argv):
            print("--only 뒤에 카테고리가 필요하다.\n" + USAGE)
            sys.exit(2)
        names = [n.strip() for n in argv[i + 1].split(",") if n.strip()]
        unknown = [n for n in names if n not in CATEGORIES]
        if unknown:
            print(f"모르는 카테고리: {unknown}\n" + USAGE)
            sys.exit(2)
    else:
        names = list(CATEGORIES)

    fetched, failures = [], []
    for name in names:
        fetch_category(name, only_required, fetched, failures)

    print()
    bad = verify(fetched)
    if bad:
        print("검증 실패 (헤더 불일치):")
        for b in bad:
            print(f"  - {b}")
        failures.extend(bad)

    total = sum(os.path.getsize(os.path.join(VEG_DIR, k)) for k in fetched
                if os.path.exists(os.path.join(VEG_DIR, k)))
    print(f"파일 {len(fetched)}개, 합계 {total / 1e6:.1f} MB → {VEG_DIR}")

    if failures:
        print()
        print("FAILED (네트워크가 막혔다면 아래 키를 S3 에서 수동으로 받아")
        print(f"        같은 상대 경로로 {VEG_DIR} 아래에 놓을 것):")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    print("All vegetation assets downloaded and verified.")


if __name__ == "__main__":
    main()
