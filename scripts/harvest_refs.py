#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
harvest_refs.py — reference-photo harvester for the W3 archetype panels.

WHY THIS EXISTS
---------------
`Docs/reports/real_reference_expansion.md` §7 records that the original Commons
harvest was run in a scratchpad and never committed, so the n=54 `expanded/` set
could not be reproduced or extended.  `w3_intake_policy.md` §7.5 makes rebuilding
it a blocking dependency for the 통람 v3 panels (T-1).  This is that rebuild.

WHAT IT DOES
------------
1. Resolves a query (`cat:<Category>` | `search:<terms>` | `files:<File:...,...>`)
   against the Wikimedia Commons API (`list=categorymembers` / `list=search`),
   then batches `prop=imageinfo&iiprop=extmetadata|url|size` for licence data.
2. Writes a per-directory `LICENSES.csv` using the **existing 12-column schema**
   verbatim (see `Docs/reference_photos/expanded/LICENSES.csv`) so the two sets
   concatenate:
       file,license,license_url,author,credit,date,commons_page,original_url,
       orig_w,orig_h,harvest_query,title
3. Downloads a thumbnail **only** for licences on the redistribution whitelist
   (CC0 / public domain / CC BY / KOGL Type 1).  Share-alike (BY-SA) and any
   NC/ND licence get a CSV + `SOURCES.md` row with the URL and caption but **no
   file**, so the repository never acquires a share-alike obligation.  This is
   the same rule `Docs/reference_photos/real_set_safe.txt` already established.
4. Writes `SOURCES.md` per panel: a URL list with licence, author and *what to
   look at* — the artefact `w3_intake_policy.md` §7.2 specifies.
5. Refuses road-view imagery outright (project ban): any Kakao / Naver / Google
   Street View / Daum roadview host, or a title matching a roadview marker, is
   dropped and counted in the `banned` tally.
6. Enforces a **country gate**.  Commons' fuzzy `list=search` returns Nagoya
   subway entrances for "Korea subway station entrance stairs"; a panel of
   Japanese references is worse than an empty panel, because the 통람 v3 judge
   would then score a Korean scene against Japanese vocabulary.  Files positively
   marked as another country (and never as Korea) are dropped and counted in
   `off-country`.  Files with no geographic marker at all are kept for eye review.

USAGE
-----
    # one panel
    python3 scripts/harvest_refs.py --archetype river_levee
    # all 12 archetype panels defined in ARCHETYPE_QUERIES
    python3 scripts/harvest_refs.py --archetype all
    # ad-hoc query into an explicit directory
    python3 scripts/harvest_refs.py --query 'cat:Amphitheatres in South Korea' \
        --out Docs/reference_photos/w3/amphitheatre --limit 40
    # enumerate only, download nothing (licence census / negative-result check)
    python3 scripts/harvest_refs.py --archetype rooftop --list-only

CPU + network only.  No GPU, no USD, no Isaac.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
from typing import Any

API = "https://commons.wikimedia.org/w/api.php"
UA = "NegObsRefHarvest/1.0 (research dataset reference panel; contact: repo maintainer)"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------------------
# Licence policy
# ---------------------------------------------------------------------------
# Redistributable inside the repo (thumbnail is committed).
WHITELIST = [
    re.compile(r"\bcc[\s\-]?0\b", re.I),
    re.compile(r"public\s*domain", re.I),
    re.compile(r"\bpd[\s\-]", re.I),
    re.compile(r"\bcc[\s\-]?by[\s\-]?(1|2|2\.5|3|4)(\.0)?\b(?![\s\-]?sa)", re.I),
    re.compile(r"kogl[\s\-]?type[\s\-]?1", re.I),
    re.compile(r"공공누리\s*제?1유형", re.I),
]
# Explicitly never downloaded (URL-only rows).  SA first: it must beat the
# `cc by` whitelist pattern, so blacklist is evaluated before whitelist.
BLACKLIST = [
    re.compile(r"\bsa\b", re.I),
    re.compile(r"share[\s\-]?alike", re.I),
    re.compile(r"\bnc\b|noncommercial|non[\s\-]commercial", re.I),
    re.compile(r"\bnd\b|noderiv", re.I),
    re.compile(r"fair\s*use|non[\s\-]free", re.I),
    re.compile(r"kogl[\s\-]?type[\s\-]?[234]", re.I),
]

# ---------------------------------------------------------------------------
# Road-view ban (project law).  Never cite, never download.
# ---------------------------------------------------------------------------
BANNED_HOSTS = (
    "map.kakao.com", "kakao.com", "map.naver.com", "naver.com", "daum.net",
    "maps.google", "google.com/maps", "streetview", "mapy.cz", "yandex",
    "instantstreetview", "openstreetcam", "mapillary",
)
BANNED_TITLE = re.compile(
    r"roadview|road[\s\-]?view|street[\s\-]?view|스트리트뷰|로드뷰|거리뷰|카카오맵|네이버지도",
    re.I,
)

# ---------------------------------------------------------------------------
# Country gate.  Every archetype in this project is a *Korean* archetype, and
# Commons' fuzzy `list=search` cheerfully returns Nagoya subway entrances for
# "Korea subway station entrance stairs" — which is worse than an empty panel,
# because a 통람 v3 judge would then score a Korean scene against Japanese
# vocabulary.  A file is kept only if nothing marks it as another country.
# ---------------------------------------------------------------------------
NOT_KOREA = re.compile(
    r"\b(japan|japanese|nagoya|tokyo|osaka|kyoto|yokohama|sapporo|fukuoka|kobe|"
    r"china|chinese|beijing|shanghai|guangzhou|shenzhen|hong\s?kong|macau|"
    r"taiwan|taipei|kaohsiung|singapore|malaysia|kuala\s?lumpur|thailand|bangkok|"
    r"vietnam|hanoi|indonesia|jakarta|philippines|manila|india|delhi|mumbai|"
    r"russia|moscow|germany|france|paris|italy|spain|netherlands|poland|czech|"
    r"united\s?states|u\.s\.a|america|canada|australia|new\s?zealand|"
    r"north\s?korea|pyongyang|dprk|"
    r"ryokuchi|prefecture|-shi\b|-ken\b|-gun\b)\b"
    r"|[ぁ-んァ-ヶ]"                      # kana → a Japanese title
    r"|地下鉄|駅|丁目",                    # JP-only kanji compounds
    re.I,
)
KOREA_HINT = re.compile(
    r"[가-힣]"                            # any hangul
    r"|\b(korea|korean|seoul|busan|daegu|incheon|gwangju|daejeon|ulsan|sejong|"
    r"gyeonggi|gangwon|chungcheong|jeolla|gyeongsang|jeju|hangang|han\s?river|"
    r"gangnam|jongno|myeongdong|insadong|bukchon|gamcheon|cheonggyecheon|"
    r"gwanghwamun|dorasan|suwon|yongin|goyang|seongnam|cheonan|okcheon|hwaseong)\b",
    re.I,
)


def wrong_country(title: str, credit: str = "") -> bool:
    """True when the file is positively marked as somewhere other than Korea.

    Conservative on purpose: a file with *no* geographic marker at all is kept
    (it is reviewed by eye in the panel), but a file that says Japan and never
    says Korea is dropped.
    """
    blob = f"{title} {credit}"
    return bool(NOT_KOREA.search(blob)) and not KOREA_HINT.search(blob)

# ---------------------------------------------------------------------------
# Archetype query plan — 12 archetypes, `w3_intake_policy.md` §7.2.
# Order inside a list is the order tried; harvesting stops at --limit.
# ---------------------------------------------------------------------------
ARCHETYPE_QUERIES: dict[str, list[str]] = {
    "plaza_civic": [
        "cat:Gwanghwamun Plaza",
        "cat:Seoul Plaza",
        "cat:Squares in Seoul",
        "search:Korea plaza granite paving",
    ],
    "street_arterial": [
        "cat:Sidewalks in South Korea",
        "cat:Streets in Seoul",
    ],
    "sidewalk_local": [
        "cat:Sidewalks in South Korea",
        "search:Korea sidewalk block paving",
    ],
    # --- the five panels that were empty at intake ------------------------
    "river_levee": [
        "cat:Hangang Park",                 # 60 members  [probed 2026-07-30]
        "cat:Yeouido Hangang Park",         # 34
        "cat:Ttukseom Hangang Park",        # 13
        "search:한강공원 자전거도로",
        "cat:Han River",                    # 0 - negative result, kept on record
    ],
    "lake_park": [
        "cat:Cheonggyecheon",
        "cat:Ilsan Lake Park",
        "cat:Seokchon Lake",
        "search:Korea lake park waterside walk",
    ],
    "park_trail": [
        "cat:Benches in South Korea",
        "cat:Parks in Seoul",
        "cat:Hiking trails in South Korea",
        "search:등산로 계단",
    ],
    "amphitheatre": [
        "search:야외음악당",              # 40 hits - the productive one
        "cat:Seoul Forest",                 # 26
        "cat:Nodeulseom",                   # 15
        "search:Korea park stepped seating plaza",
        "search:Korea outdoor stage seating steps",
        "cat:Amphitheatres in South Korea",  # 0 - negative result
    ],
    "temple_precinct": [
        "cat:Buseoksa",
        "cat:Bulguksa",
        "search:Korea temple stone stairs granite",
    ],
    # NOTE: this archetype is the project's hardest.  Commons has effectively no
    # Korean 지하보도 coverage (verified: `Pedestrian underpasses in South Korea`
    # and `Underpasses in South Korea` are both empty; MediaSearch `지하보도`
    # returns zero).  The English searches DO return results — but they are
    # Nagoya subway entrances, which the country gate now drops.  A thin honest
    # panel is the correct outcome here; do not widen the queries to fill it.
    "underpass_entry": [
        "search:서울 지하철 출입구",
        "search:지하보도",
        "search:Seoul subway station entrance",
        "cat:Seoul Metropolitan Subway",
        "search:Korea subway station entrance stairs",   # 50 hits, mostly JP
        "cat:Pedestrian underpasses",                    # 39, no Korean entries
        "cat:Underpasses in South Korea",                # 0 - negative result
    ],
    "alley_hillside": [
        "cat:Bukchon Hanok Village",
        "cat:Gamcheon Culture Village",
        "search:Korea hillside alley stairs",
    ],
    # NOTE: `search:Korea rooftop view` was tried and REJECTED — it returns views
    # *from* rooftops (a long school-survey series shot from apartment roofs),
    # not the roof surface, parapet and plant the scene19 archetype needs.
    "rooftop": [
        "search:옥상 정원",
        "search:옥상",
        "cat:Roof gardens in South Korea",
        "cat:Roofs in South Korea",         # 2
        "search:Korea rooftop garden parapet",
        "search:Korea green roof building",
        "cat:Rooftops in South Korea",      # 0 - negative result
    ],
    "industrial_transit": [
        "cat:Dorasan Station",
        "cat:Railway stations in South Korea",
        "search:한국 철도역 승강장",
        "cat:Industrial buildings in South Korea",
        "search:Korea railway platform edge",
    ],
}

# ---------------------------------------------------------------------------
# Non-Commons ledger rows (government / municipal press, KOGL Type 1 etc.).
# These are recorded as attribution rows only — nothing is hot-linked or
# downloaded, because gov CMS URLs rotate and the licence is per-page.
# ---------------------------------------------------------------------------
EXTRA_SOURCES: dict[str, list[dict[str, str]]] = {}
_EXTRA_JSON = os.path.join(REPO, "Docs", "reference_photos", "w3", "extra_sources.json")


def _load_extra() -> None:
    if os.path.exists(_EXTRA_JSON):
        with open(_EXTRA_JSON, encoding="utf-8") as fh:
            EXTRA_SOURCES.update(json.load(fh))


# ---------------------------------------------------------------------------
# HTTP
# ---------------------------------------------------------------------------
# Commons returns HTTP 429 quickly under a tight loop.  One shared throttle for
# every request the module makes, plus exponential backoff that respects 429.
_MIN_INTERVAL = 1.2          # seconds between requests
_last_req = [0.0]


def _throttle() -> None:
    dt = time.time() - _last_req[0]
    if dt < _MIN_INTERVAL:
        time.sleep(_MIN_INTERVAL - dt)
    _last_req[0] = time.time()


def _get(url: str, *, binary: bool = False, retries: int = 5) -> Any:
    last = None
    for attempt in range(retries):
        _throttle()
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = resp.read()
            return data if binary else json.loads(data.decode("utf-8"))
        except urllib.error.HTTPError as exc:
            last = exc
            # 429 / 5xx are transient: back off hard.  4xx else is permanent.
            if exc.code not in (429, 500, 502, 503, 504):
                raise RuntimeError(f"GET {exc.code}: {url}") from exc
            time.sleep(min(30.0, 3.0 * (2 ** attempt)))
        except Exception as exc:  # noqa: BLE001 - network is the whole point
            last = exc
            time.sleep(2.0 * (attempt + 1))
    raise RuntimeError(f"GET failed after {retries}: {url} :: {last}")


def api(**params: Any) -> dict:
    params.setdefault("format", "json")
    params.setdefault("formatversion", "2")
    return _get(API + "?" + urllib.parse.urlencode(params))


# ---------------------------------------------------------------------------
# Query resolution
# ---------------------------------------------------------------------------
def resolve_query(query: str, limit: int) -> list[str]:
    """`cat:X` | `search:X` | `files:File:a.jpg,File:b.jpg` -> list of File: titles."""
    if query.startswith("cat:"):
        cat = query[4:].strip()
        if not cat.lower().startswith("category:"):
            cat = "Category:" + cat
        out, cont = [], None
        while len(out) < limit:
            kw = dict(action="query", list="categorymembers", cmtitle=cat,
                      cmtype="file", cmlimit=min(500, limit - len(out)))
            if cont:
                kw["cmcontinue"] = cont
            r = api(**kw)
            if "error" in r:
                return []
            members = r.get("query", {}).get("categorymembers", [])
            out += [m["title"] for m in members]
            cont = r.get("continue", {}).get("cmcontinue")
            if not cont or not members:
                break
        return out[:limit]

    if query.startswith("search:"):
        term = query[7:].strip()
        r = api(action="query", list="search", srsearch=term,
                srnamespace=6, srlimit=min(50, limit))
        return [m["title"] for m in r.get("query", {}).get("search", [])][:limit]

    if query.startswith("files:"):
        return [t.strip() for t in query[6:].split(",") if t.strip()]

    raise ValueError(f"unrecognised query form: {query!r}")


def imageinfo(titles: list[str], thumb_w: int) -> dict[str, dict]:
    """Batch imageinfo+extmetadata.  Commons caps titles at 50 per request."""
    out: dict[str, dict] = {}
    for i in range(0, len(titles), 40):
        chunk = titles[i:i + 40]
        r = api(action="query", titles="|".join(chunk),
                prop="imageinfo|categories",
                iiprop="url|size|mime|extmetadata", iiurlwidth=thumb_w,
                cllimit="max")
        for page in r.get("query", {}).get("pages", []):
            ii = (page.get("imageinfo") or [{}])[0]
            if ii:
                # Categories are the most reliable country marker on Commons —
                # far better than the filename, which for e.g.
                # "Hattori Ryokuchi open air concert hall" names no country at all.
                ii["_cats"] = " ".join(c.get("title", "")
                                       for c in page.get("categories", []))
                out[page["title"]] = ii
    return out


# ---------------------------------------------------------------------------
# Licence classification
# ---------------------------------------------------------------------------
def _meta(ii: dict, key: str, default: str = "") -> str:
    v = (ii.get("extmetadata") or {}).get(key, {}).get("value", default)
    v = re.sub(r"<[^>]+>", " ", str(v))          # strip the HTML Commons embeds
    v = re.sub(r"&[a-z]+;|&#\d+;", " ", v)
    return re.sub(r"\s+", " ", v).strip()


def classify(license_text: str) -> str:
    """-> 'download' | 'urlonly' | 'reject'."""
    t = license_text or ""
    for pat in BLACKLIST:
        if pat.search(t):
            return "urlonly" if re.search(r"\bsa\b|share", t, re.I) else "reject"
    for pat in WHITELIST:
        if pat.search(t):
            return "download"
    return "urlonly"


def banned(title: str, url: str) -> bool:
    if BANNED_TITLE.search(title or ""):
        return True
    low = (url or "").lower()
    return any(h in low for h in BANNED_HOSTS)


# ---------------------------------------------------------------------------
# Filenames — mirrors the `expanded/` convention: <pfx><nnn>_<lic>_<hash6>_<slug>
# ---------------------------------------------------------------------------
def lic_slug(lic: str) -> str:
    s = unicodedata.normalize("NFKD", lic).lower()
    s = re.sub(r"[^a-z0-9]", "", s)
    return (s or "unk")[:14]


def name_slug(title: str) -> str:
    s = title.replace("File:", "")
    s = os.path.splitext(s)[0]
    s = re.sub(r"[^\w가-힣]+", "_", s, flags=re.UNICODE).strip("_")
    return s[:60] or "img"


def out_name(prefix: str, idx: int, lic: str, title: str, ext: str) -> str:
    h = hashlib.sha1(title.encode("utf-8")).hexdigest()[:6]
    return f"{prefix}{idx:03d}_{lic_slug(lic)}_{h}_{name_slug(title)}{ext}"


# ---------------------------------------------------------------------------
# Harvest
# ---------------------------------------------------------------------------
CSV_COLS = ["file", "license", "license_url", "author", "credit", "date",
            "commons_page", "original_url", "orig_w", "orig_h",
            "harvest_query", "title"]


def harvest(queries: list[str], outdir: str, *, limit: int, thumb_w: int,
            prefix: str, list_only: bool, notes: str = "") -> dict:
    os.makedirs(outdir, exist_ok=True)
    rows: list[dict] = []
    seen: set[str] = set()
    stats = dict(found=0, downloaded=0, urlonly=0, rejected=0, banned=0,
                 offcountry=0, empty_queries=[], per_query={})

    idx = 0
    for q in queries:
        try:
            titles = resolve_query(q, limit)
        except Exception as exc:  # noqa: BLE001
            print(f"  ! query failed {q}: {exc}", file=sys.stderr)
            titles = []
        titles = [t for t in titles if t not in seen]
        stats["per_query"][q] = len(titles)
        if not titles:
            stats["empty_queries"].append(q)
            print(f"  · {q:52s} -> 0 files  [negative result, recorded]")
            continue
        print(f"  · {q:52s} -> {len(titles)} files")
        info = imageinfo(titles, thumb_w)

        for t in titles:
            if len(rows) >= limit:
                break
            ii = info.get(t)
            if not ii or not str(ii.get("mime", "")).startswith("image"):
                continue
            seen.add(t)
            stats["found"] += 1
            orig = ii.get("url", "")
            if banned(t, orig):
                stats["banned"] += 1
                print(f"    BAN  {t}")
                continue
            cred = (_meta(ii, "Credit") + " " + _meta(ii, "ImageDescription")
                    + " " + ii.get("_cats", ""))
            if wrong_country(t, cred):
                stats["offcountry"] += 1
                print(f"    GEO  {t}")
                continue

            lic = _meta(ii, "LicenseShortName") or _meta(ii, "License") or "unknown"
            verdict = classify(lic)
            if verdict == "reject":
                stats["rejected"] += 1
                continue

            idx += 1
            row = {
                "file": "",
                "license": lic,
                "license_url": _meta(ii, "LicenseUrl"),
                "author": _meta(ii, "Artist"),
                "credit": _meta(ii, "Credit"),
                "date": _meta(ii, "DateTimeOriginal") or _meta(ii, "DateTime"),
                "commons_page": ii.get("descriptionurl", ""),
                "original_url": orig,
                "orig_w": ii.get("width", ""),
                "orig_h": ii.get("height", ""),
                "harvest_query": q,
                "title": t,
            }

            if verdict == "download" and not list_only:
                ext = os.path.splitext(orig)[1].lower() or ".jpg"
                if ext not in (".jpg", ".jpeg", ".png"):
                    ext = ".jpg"
                fn = out_name(prefix, idx, lic, t, ext)
                thumb = ii.get("thumburl") or orig
                try:
                    blob = _get(thumb, binary=True)
                    with open(os.path.join(outdir, fn), "wb") as fh:
                        fh.write(blob)
                    row["file"] = fn
                    stats["downloaded"] += 1
                except Exception as exc:  # noqa: BLE001
                    print(f"    ! download failed {t}: {exc}", file=sys.stderr)
                    stats["urlonly"] += 1
            elif verdict == "download" and list_only:
                stats["downloaded"] += 1
            else:
                stats["urlonly"] += 1
            rows.append(row)
        if len(rows) >= limit:
            break

    if not list_only:
        with open(os.path.join(outdir, "LICENSES.csv"), "w", newline="",
                  encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=CSV_COLS)
            w.writeheader()
            for r in rows:
                w.writerow(r)
        write_sources_md(outdir, rows, stats, queries, notes)
    stats["rows"] = len(rows)
    return stats


def write_sources_md(outdir: str, rows: list[dict], stats: dict,
                     queries: list[str], notes: str) -> None:
    arche = os.path.basename(outdir.rstrip("/"))
    extra = EXTRA_SOURCES.get(arche, [])
    lines = [
        f"# Reference panel — `{arche}`",
        "",
        f"Harvested by `scripts/harvest_refs.py` on {time.strftime('%Y-%m-%d')}.",
        "Thumbnails are committed **only** for CC0 / public-domain / CC BY / KOGL Type 1.",
        "Share-alike rows are URL-only, so the repo takes on no share-alike obligation",
        "(`Docs/reference_photos/real_set_safe.txt` rule). Road-view sources are banned",
        f"and dropped by the harvester ({stats['banned']} dropped here).",
        "",
        f"**Counts** — rows {len(rows)} · thumbs {stats['downloaded']} · "
        f"URL-only {stats['urlonly']} · rejected(NC/ND) {stats['rejected']} · "
        f"dropped as off-country {stats['offcountry']}",
        "",
    ]
    if notes:
        lines += ["**What to look at**: " + notes, ""]
    lines += ["| # | file / URL-only | licence | author | title |", "|---|---|---|---|---|"]
    for i, r in enumerate(rows, 1):
        ref = f"`{r['file']}`" if r["file"] else f"[URL-only]({r['commons_page']})"
        au = (r["author"] or "—")[:40]
        lines.append(f"| {i} | {ref} | {r['license']} | {au} | {r['title'].replace('File:','')} |")
    if extra:
        lines += ["", "## Non-Commons sources (attribution rows, no local copy)", "",
                  "| source | licence | what to look at | URL |", "|---|---|---|---|"]
        for e in extra:
            lines.append(f"| {e.get('source','')} | {e.get('license','')} | "
                         f"{e.get('look','')} | {e.get('url','')} |")
    if stats["empty_queries"]:
        lines += ["", "## Negative results (recorded so they are not re-attempted)", ""]
        for q in stats["empty_queries"]:
            lines.append(f"- `{q}` → 0 files")
    lines.append("")
    with open(os.path.join(outdir, "SOURCES.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


PANEL_NOTES = {
    "river_levee": "levee crown surface, bank slope revetment, kerbless bike-path edge, one-species bank planting",
    "amphitheatre": "seating-tier riser/tread proportion, radial vs fan paving in the bowl, aisle position",
    "underpass_entry": "entrance flood sill (침수방지턱) step count, canopy presence, handrail, wall-to-paving joint",
    "rooftop": "parapet height and cap, roof-membrane surface, plant/duct massing, drain positions",
    "industrial_transit": "platform edge line, tactile strip, bay/dock lip, surface wear bands",
    "plaza_civic": "paving runs to the building face, bench-against-edge rule, empty central axis",
    "street_arterial": "tree pitch and lateral offset from kerb, single furniture line, free walking band",
    "sidewalk_local": "block module, patch/saw-cut shape, bollard placement at vehicle entries",
    "lake_park": "waterside edge treatment, single-species bank planting, deck-to-ground joint",
    "park_trail": "gravel deposition (armour/rill/edge), clumped shrub massing, bench-tree relationship",
    "temple_precinct": "장대석 course stairs, no gaps, 소맷돌 cheek stones, worn-stone tone",
    "alley_hillside": "stair run-and-landing rhythm, hand-rail vocabulary, wall-to-step joint",
}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--archetype", help="one of ARCHETYPE_QUERIES, or 'all'")
    ap.add_argument("--query", action="append", default=[],
                    help="cat:X | search:X | files:File:a.jpg,File:b.jpg")
    ap.add_argument("--out", help="output directory (required with --query)")
    ap.add_argument("--limit", type=int, default=40)
    ap.add_argument("--thumb-width", type=int, default=800,
                    help="committed panels use 800 px; keeps the repo footprint sane")
    ap.add_argument("--prefix", default="w3")
    ap.add_argument("--list-only", action="store_true",
                    help="enumerate + classify licences, download nothing")
    args = ap.parse_args()

    _load_extra()
    base = os.path.join(REPO, "Docs", "reference_photos", "w3")
    jobs: list[tuple[str, list[str], str]] = []

    if args.archetype == "all":
        for a, qs in ARCHETYPE_QUERIES.items():
            jobs.append((os.path.join(base, a), qs, PANEL_NOTES.get(a, "")))
    elif args.archetype:
        a = args.archetype
        if a not in ARCHETYPE_QUERIES:
            print(f"unknown archetype {a}; known: {', '.join(ARCHETYPE_QUERIES)}")
            return 2
        jobs.append((os.path.join(base, a), ARCHETYPE_QUERIES[a], PANEL_NOTES.get(a, "")))
    elif args.query:
        if not args.out:
            print("--query needs --out")
            return 2
        out = args.out if os.path.isabs(args.out) else os.path.join(REPO, args.out)
        jobs.append((out, args.query, ""))
    else:
        ap.print_help()
        return 2

    grand = dict(rows=0, downloaded=0, urlonly=0, banned=0, offcountry=0, rejected=0)
    for outdir, qs, notes in jobs:
        print(f"\n== {os.path.basename(outdir)} ==")
        st = harvest(qs, outdir, limit=args.limit, thumb_w=args.thumb_width,
                     prefix=args.prefix, list_only=args.list_only, notes=notes)
        print(f"  rows {st['rows']} · thumbs {st['downloaded']} · urlonly {st['urlonly']}"
              f" · banned {st['banned']} · off-country {st['offcountry']}"
              f" · rejected {st['rejected']}")
        for k in grand:
            grand[k] += st.get(k, 0)
    print(f"\nTOTAL rows {grand['rows']} · thumbs {grand['downloaded']} · "
          f"urlonly {grand['urlonly']} · banned {grand['banned']} · "
          f"off-country {grand['offcountry']} · rejected {grand['rejected']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
