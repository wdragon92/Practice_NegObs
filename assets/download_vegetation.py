#!/usr/bin/env python3
"""Download NVIDIA Omniverse vegetation USD assets for NegObs 사실화 라운드.

현재 씬의 나무는 실린더 줄기 + 구(sphere) 수관이다. 조사 `ZZ_synthesis.md` §10.1 이
지목한 대로 NVIDIA 콘텐츠 S3 버킷에 실제 나무 에셋(나무 44종 + 관목 37종)이 있고
**인증 없이** 받을 수 있다. 이 스크립트가 그 최소 세트를 조달한다.

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

SETS = [
    # (라벨, 필수 여부, [키...])
    ("벚나무 Japanese_Cherry (한국 가로수 상위 수종)", True, [
        "Trees/Japanese_Cherry.usd",
        "Trees/materials/JapaneseCherry_blossom_Mat.mdl",
        "Trees/materials/textures/cherryblossom.png",
    ] + BARK3),

    ("소나무 Yellow_Pine (성목 실루엣)", False,
     ["Trees/Yellow_Pine.usd"] + PINE_MATS),

    ("소나무 White_Pine (848 KB, 원경/LOD용 — 재질은 Yellow_Pine 과 공유)", False,
     ["Trees/White_Pine.usd"] + PINE_MATS),

    ("관목 Boxwood 회양목 (보도 화단·연석 가림 — 낙차 폐색 실험용)", False, [
        "Shrub/Boxwood.usd",
        "Shrub/materials/Boxwood_leaf_Mat.mdl",
        "Shrub/materials/textures/hollyprivet_basecolor.png",
        "Shrub/materials/textures/hollyprivet_normal.png",
        "Shrub/materials/textures/hollyprivet_roughness.png",
        # Boxwood 의 줄기는 ../Trees/materials/bark3.mdl 을 참조한다.
    ] + BARK3),
]


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
        if key.endswith(".usd") and not (head8.startswith(b"PXR-USDC")
                                         or head8.startswith(b"#usda")):
            bad.append(f"{key} (USD 헤더 아님: {head8!r})")
        elif key.endswith(".png") and not head8.startswith(b"\x89PNG\r\n\x1a\n"):
            bad.append(f"{key} (PNG 헤더 아님: {head8!r})")
        elif key.endswith(".mdl") and not head8.startswith(b"mdl "):
            bad.append(f"{key} (MDL 헤더 아님: {head8!r})")
    return bad


def main():
    only_required = "--required-only" in sys.argv
    failures = []
    fetched = []

    for label, required, keys in SETS:
        if only_required and not required:
            print(f"[skip set] {label} (--required-only)")
            continue
        print(f"[set] {label}")
        for key in keys:
            if key in fetched:
                continue  # 공유 재질(bark3 등)은 한 번만
            url = BASE + key
            size, md5 = head(url)
            if size is None:
                failures.append(f"{key} (S3 HEAD 실패)")
                continue
            if download(url, os.path.join(VEG_DIR, key), size, md5):
                fetched.append(key)
            else:
                failures.append(f"{key} ({url})")

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
