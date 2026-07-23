#!/usr/bin/env python3
"""Download CC0 assets (PolyHaven) for NegObs look-check v1.

Re-runnable: files already downloaded with the correct size are skipped.
Each download is retried up to 3 times and verified against the size
reported by the PolyHaven API (https://api.polyhaven.com/files/{slug}).

API structure (confirmed by direct calls, 2026-07-22):
  Textures: top-level keys like 'Diffuse', 'nor_dx', 'Rough' (mixed case!)
            -> d[key]['4k']['jpg'] = {'url': ..., 'md5': ..., 'size': ...}
  HDRIs:    top-level keys 'hdri', 'tonemapped'
            -> d['hdri']['4k']['exr'] = {'url': ..., 'md5': ..., 'size': ...}
"""
import json
import os
import sys
import time
import urllib.request

ASSETS_DIR = os.path.dirname(os.path.abspath(__file__))
API = "https://api.polyhaven.com/files/{slug}"
RETRIES = 3
TIMEOUT = 120
# PolyHaven returns 403 to the default Python-urllib User-Agent.
HEADERS = {"User-Agent": "curl/8.5.0"}


def open_url(url):
    req = urllib.request.Request(url, headers=HEADERS)
    return urllib.request.urlopen(req, timeout=TIMEOUT)

TEXTURE_SLUGS = ["aerial_grass_rock", "brown_mud_dry", "brown_mud_03"]
# map: canonical name -> candidate API keys (PolyHaven mixes case per asset)
TEXTURE_MAPS = {
    "diff": ["Diffuse", "diffuse", "diff"],
    "nor_dx": ["nor_dx"],
    "rough": ["Rough", "rough", "rough_ao"],
}
HDRI_SLUGS = ["qwantani_noon_puresky", "qwantani_dawn_puresky"]


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
    """Download url -> dest. Skip if already present with correct size."""
    if os.path.exists(dest):
        actual = os.path.getsize(dest)
        if expected_size is None or actual == expected_size:
            print(f"  [skip] {os.path.basename(dest)} ({actual} bytes, already present)")
            return True
        print(f"  [redo] {os.path.basename(dest)} size mismatch "
              f"({actual} != {expected_size})")
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
            print(f"  [ ok ] {os.path.basename(dest)} ({actual} bytes)")
            return True
        except Exception as e:
            print(f"  [fail] attempt {attempt}/{RETRIES}: {e}")
            if os.path.exists(tmp):
                os.remove(tmp)
            time.sleep(2 * attempt)
    return False


def pick_key(d, candidates, slug):
    for k in candidates:
        if k in d:
            return k
    return None


def main():
    failures = []
    manifest = []  # (slug, res, kind, dest) for manual-placement fallback

    for slug in TEXTURE_SLUGS:
        print(f"[texture] {slug}")
        data = fetch_json(API.format(slug=slug))
        if data is None:
            for kind in TEXTURE_MAPS:
                failures.append(f"{slug}:{kind}:4k:jpg (API unreachable)")
                manifest.append((slug, "4k", kind, f"{slug}_{kind}_4k.jpg"))
            continue
        for kind, candidates in TEXTURE_MAPS.items():
            key = pick_key(data, candidates, slug)
            if key is None:
                failures.append(f"{slug}:{kind} (no matching API key; "
                                f"top-level keys: {sorted(data.keys())})")
                continue
            try:
                entry = data[key]["4k"]["jpg"]
            except KeyError as e:
                failures.append(f"{slug}:{key}:4k:jpg (missing in API: {e})")
                continue
            dest = os.path.join(ASSETS_DIR, f"{slug}_{kind}_4k.jpg")
            if not download(entry["url"], dest, entry.get("size")):
                failures.append(f"{slug}:{key}:4k:jpg ({entry['url']})")

    for slug in HDRI_SLUGS:
        print(f"[hdri] {slug}")
        data = fetch_json(API.format(slug=slug))
        if data is None:
            failures.append(f"{slug}:hdri:4k:exr (API unreachable)")
            manifest.append((slug, "4k", "hdri", f"{slug}_4k.exr"))
            continue
        try:
            entry = data["hdri"]["4k"]["exr"]
        except KeyError as e:
            failures.append(f"{slug}:hdri:4k:exr (missing in API: {e})")
            continue
        dest = os.path.join(ASSETS_DIR, f"{slug}_4k.exr")
        if not download(entry["url"], dest, entry.get("size")):
            failures.append(f"{slug}:hdri:4k:exr ({entry['url']})")

    print()
    if failures:
        print("FAILED files (place manually into assets/ if network is blocked):")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    print("All assets downloaded and size-verified.")


if __name__ == "__main__":
    main()
