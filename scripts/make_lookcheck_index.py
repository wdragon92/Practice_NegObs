#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""`look_check/INDEX.md` 를 **디스크에서** 다시 만든다 (regenerate from disk).

`look_check/` 는 `.gitignore` 되어 있어서 INDEX.md 가 "이 렌더 머신에 무엇이 있는가"
를 남기는 **유일한 커밋 기록**이다. 07-30 판이 27일 동안 갱신되지 않아 W3-fix/W4
231 라운드를 하나도 담지 못했던 것이 이 생성기를 만든 이유다. 손으로 고치지 말고
이 스크립트를 다시 돌릴 것.

    python3 scripts/make_lookcheck_index.py            # look_check/INDEX.md 갱신
    python3 scripts/make_lookcheck_index.py --stdout   # 출력만 (파일 안 건드림)

Sections: §0 layout · §1 rollup (wave / scene) · §2 live tree with the pin reason ·
§3 archive tree with each round's old path · §4 `_experiments/` with last-write dates ·
§5 latest-round discovery, re-verified · §6 relocation map (accumulated: the rows already
in the current INDEX.md are carried forward and this run's moves are appended).

Read-only except for `look_check/INDEX.md`. No GPU, no Isaac, stdlib only.
"""
from __future__ import annotations

import argparse
import csv
import datetime as _dt
import glob
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LC = os.path.join(ROOT, "look_check")
INDEX = os.path.join(LC, "INDEX.md")
MOVES = os.path.join(ROOT, "Docs", "reorg_0827", "lookcheck_moves.tsv")
GEN = "scripts/make_lookcheck_index.py"

WAVE_ORDER = ["W2-P2", "W2-P3/P4", "W2-ladder", "W2-ctx", "W2-mode", "W2-nearfield",
              "W2", "W2-D", "W3", "W3R", "W3-fix", "W4", "special"]
ARCHIVE_DIRS = ["w2", "w2d", "w3", "w3fix"]
ARCHIVE_LABEL = {"w2": "W2 (P2 · P3/P4 · ladder · ctx · mode · nearfield · special)",
                 "w2d": "W2-D (`260730_w2d_*` · `260730_lcfreeze_*`)",
                 "w3": "W3 (`260730/260731_w3_*`, `w3r` 포함)",
                 "w3fix": "W3-fix (`260805`~`260811_w3_*`)"}


# --------------------------------------------------------------------------- #
# 라운드 이름 -> 웨이브. 07-26~08-17 실제 이름 규칙에서 뽑았고, 조사 C 의 639행
# 표(wave 열)를 639/639 재현하는 것으로 검증했다.
# --------------------------------------------------------------------------- #
def wave_of(name: str) -> str:
    if re.match(r"^2607(30|31)_w3r_", name):
        return "W3R"
    if re.match(r"^2608(0[5-9]|1[01])_w3_", name):
        return "W3-fix"
    if re.match(r"^2607(30|31)_w3_", name):
        return "W3"
    if re.match(r"^26081[3-7]_w4_", name):
        return "W4"
    if re.match(r"^260730_(w2d|lcfreeze)_", name):
        return "W2-D"
    if name.endswith(("_ptfast", "_ptlegacy")):
        return "W2-mode"
    if name in ("w2_pilot", "w2c_g2"):
        return "W2"
    if name in ("balust", "leaf3d", "handrail", "fix1", "shrub", "facade",
                "wall", "planterfix"):
        return "W2-nearfield"
    if name.startswith("ctx"):
        return "W2-ctx"
    if re.match(r"^v[5-8](_|$)", name):
        return "W2-ladder"
    if name.startswith(("p2", "pair_cues")) or name == "p0_base_pt":
        return "W2-P2"
    if re.match(r"^r[0-9]", name):
        return "W2-P3/P4"
    if name.startswith("_"):
        return "special"
    return "기타"


def archive_dir_of(wave: str) -> str:
    return {"W2-D": "w2d", "W3": "w3", "W3R": "w3", "W3-fix": "w3fix"}.get(wave, "w2")


# --------------------------------------------------------------------------- #
def du_sb(paths):
    out = {}
    for i in range(0, len(paths), 200):
        r = subprocess.run(["du", "-sb"] + paths[i:i + 200],
                           capture_output=True, text=True)
        for ln in r.stdout.splitlines():
            n, p = ln.split("\t", 1)
            out[p] = int(n)
    return out


def n_png(d):
    return len(glob.glob(os.path.join(d, "*.png")))


def newest_mtime(d):
    """Newest FILE write under `d`. Directory mtimes are deliberately ignored: a
    deletion inside a directory bumps that directory's mtime and would report a
    frozen tree as freshly written (`gates/` after the 0827 `lighting_spikes`
    deletion is the live example). Falls back to the directory mtime when empty."""
    best = 0.0
    for dp, _dns, fns in os.walk(d):
        for fn in fns:
            if fn.endswith((".s4.bak", ".pre0827.bak", ".s3.bak")):
                continue
            try:
                best = max(best, os.path.getmtime(os.path.join(dp, fn)))
            except OSError:
                pass
    return best or os.path.getmtime(d)


def gb(b):
    return f"{b / 2**30:.2f}"


def d(ts):
    return _dt.date.fromtimestamp(ts).isoformat()


# --------------------------------------------------------------------------- #
def collect():
    sys.path.insert(0, os.path.join(ROOT, "scripts", "reorg"))
    import lookcheck_pins as P                                    # noqa: E402

    scenes = P.scene_dirs()
    live, arch = [], []
    for s in scenes:
        for p in sorted(glob.glob(os.path.join(LC, s, "*"))):
            if os.path.isdir(p) and not os.path.islink(p):
                live.append((s, os.path.basename(p), p))
    for w in ARCHIVE_DIRS:
        for p in sorted(glob.glob(os.path.join(LC, "_archive", w, "*", "*"))):
            if os.path.isdir(p) and not os.path.islink(p):
                arch.append((w, os.path.basename(os.path.dirname(p)),
                             os.path.basename(p), p))

    sizes = du_sb([r[-1] for r in live] + [r[-1] for r in arch])
    vp, cp = P.valset_pins(), None
    chain = P.readme_chain() + [n for n in P.regrcheck_chain()
                                if n not in P.readme_chain()]
    cp = P.chain_pins(chain, scenes)
    sp, ap = P.stamp_pins(scenes), P.anchor_pins()
    return dict(scenes=scenes, live=live, arch=arch, sizes=sizes,
                valset=vp, chain=cp, stamp=sp, anchor=ap, chain_names=chain)


def pin_reason(key, C):
    bits = []
    if key in C["valset"]:
        bits.append("valset.py 코퍼스")
    if key in C["chain"]:
        bits.append("회귀 체인")
    if key in C["stamp"]:
        bits.append("stamp:BoR")
    if key in C["anchor"]:
        bits.append("앵커")
    if not bits and wave_of(key[1]) == "W4":
        bits.append("W4 현행 웨이브")
    return " · ".join(bits) if bits else "판정 그리드(현행 보관)"


def role_of(key, C):
    if key in C["stamp"]:
        return "baseline-of-record"
    if key in C["valset"]:
        return "corpus"
    if key in C["chain"]:
        return "regr-chain"
    if key in C["anchor"]:
        return "anchor"
    if wave_of(key[1]) == "W4":
        return "current"
    return "evidence"


# --------------------------------------------------------------------------- #
def old_relocation_rows():
    """이미 INDEX.md §6 에 있는 (old, new) 행을 그대로 물려받는다."""
    if not os.path.isfile(INDEX):
        return []
    txt = open(INDEX, encoding="utf-8").read()
    m = re.search(r"^##\s*6\..*?$(.*)\Z", txt, re.S | re.M)
    if not m:
        return []
    rows = []
    for ln in m.group(1).splitlines():
        ln = ln.strip()
        if not ln.startswith("|") or ln.startswith("|---") or ln.startswith("| ---"):
            continue
        cells = [c.strip() for c in ln.strip("|").split("|")]
        if len(cells) >= 2 and cells[0] and not cells[0].startswith("old path") \
                and cells[0] not in ("예전 경로", "옛 경로"):
            rows.append((cells[0], cells[1]))
    return rows


def move_rows():
    if not os.path.isfile(MOVES):
        return []
    out = []
    for r in csv.DictReader(open(MOVES, encoding="utf-8"), delimiter="\t"):
        out.append((f"`{r['old']}`", f"`{r['new']}`"))
    return out


# --------------------------------------------------------------------------- #
def build(C):
    S, L, A = C["sizes"], C["live"], C["arch"]
    today = _dt.date.today().isoformat()
    o = []
    w = o.append

    w("# `look_check/` INDEX — 디스크 실측 목록")
    w("")
    w(f"> **generated from disk on {today} by `{GEN}`** — 손으로 고치지 말고 "
      f"스크립트를 다시 돌릴 것. 라운드를 추가·이동·삭제했으면 매번.")
    w("")
    w("`look_check/` 는 `README.md` 와 이 파일만 빼고 전부 `.gitignore` 대상이다. "
      "그래서 **이 파일이 렌더 머신에 무엇이 있었는지를 남기는 유일한 커밋 기록**이다. "
      "라운드 이름은 절대 바뀌지 않는다(`README.md` §3). 배치 규칙은 `README.md` §1.")
    w("")

    # ---------------- §0 ----------------
    w("## 0. 구조")
    w("")
    w("```")
    w("look_check/")
    w("  <scene>/<round>/          현행 — 판정 그리드 · 코퍼스 · 앵커 · baseline-of-record")
    w("  _archive/<wave>/<scene>/<round>/   지난 웨이브의 증거 라운드 (w2 · w2d · w3 · w3fix)")
    w("  _experiments/<topic>/     크롭 · 게이트 · 트윈 · 스파이크 · 진단")
    w("  _review/<wave>/<round>/   검수 갤러리 (w2 · w3 · w4)")
    w("  logs/                     렌더 저널 (*.log · *_times.tsv · spike_results.json)")
    w("  _t0_spike   -> _experiments/t0_spike               (심볼릭 링크, 사양 인용)")
    w("  spike_probe -> _experiments/spike_p1/spike_probe   (심볼릭 링크, 사양 인용)")
    w("```")
    w("")
    w("**씬 폴더 안에는 심볼릭 링크를 만들지 않는다.** 링크는 mtime 이 새로 찍히므로 "
      "`ls -t <scene>/*/ | head -1` 최신 라운드 탐색(§5)이 즉시 깨진다. "
      "옮겨간 라운드는 §6 이동 지도로 찾는다.")
    w("")

    # ---------------- §1 ----------------
    w("## 1. 롤업")
    w("")
    w("### 1.1 웨이브별")
    w("")
    w("| 웨이브 | 라운드 | GB | 현행(scene root) | 아카이브 |")
    w("|---|---:|---:|---:|---:|")
    tot = [0, 0, 0, 0]
    for wv in WAVE_ORDER:
        lr = [r for r in L if wave_of(r[1]) == wv]
        ar = [r for r in A if wave_of(r[2]) == wv]
        if not lr and not ar:
            continue
        b = sum(S.get(r[2], 0) for r in lr) + sum(S.get(r[3], 0) for r in ar)
        w(f"| {wv} | {len(lr)+len(ar)} | {gb(b)} | {len(lr)} | {len(ar)} |")
        tot[0] += len(lr) + len(ar)
        tot[1] += b
        tot[2] += len(lr)
        tot[3] += len(ar)
    w(f"| **합계** | **{tot[0]}** | **{gb(tot[1])}** | **{tot[2]}** | **{tot[3]}** |")
    w("")
    w("### 1.2 씬별")
    w("")
    w("| 씬 | 현행 | 현행 GB | 아카이브 | 아카이브 GB |")
    w("|---|---:|---:|---:|---:|")
    for s in C["scenes"]:
        lr = [r for r in L if r[0] == s]
        ar = [r for r in A if r[1] == s]
        w(f"| `{s}` | {len(lr)} | {gb(sum(S.get(r[2],0) for r in lr))} | "
          f"{len(ar)} | {gb(sum(S.get(r[3],0) for r in ar))} |")
    w("")

    # ---------------- §2 ----------------
    w("## 2. 현행 트리 — 씬 루트에 남은 라운드")
    w("")
    w("`역할`: baseline-of-record(다음 회귀의 비교 대상) · corpus(`valset.py` 검증 코퍼스) · "
      "regr-chain(`README.md` §4 `--before-round` 체인) · anchor(발표 수치 재현) · "
      "current(W4 현행 웨이브) · evidence(보고서 증거). "
      "`왜 남았나` 열은 **코드에서 다시 뽑은 근거**다 — 이 중 하나라도 걸리면 옮기면 안 된다.")
    w("")
    for s in C["scenes"]:
        lr = sorted([r for r in L if r[0] == s], key=lambda r: r[1])
        w(f"### `{s}` — {len(lr)} 라운드 / "
          f"{gb(sum(S.get(r[2],0) for r in lr))} GB")
        w("")
        w("| 라운드 | 웨이브 | 컷 | 역할 | 왜 남았나 |")
        w("|---|---|---:|---|---|")
        for _s, rn, p in lr:
            k = (s, rn)
            w(f"| `{rn}` | {wave_of(rn)} | {n_png(p)} | {role_of(k, C)} | {pin_reason(k, C)} |")
        w("")

    # ---------------- §3 ----------------
    w("## 3. 아카이브 트리 — `_archive/<wave>/<scene>/<round>`")
    w("")
    w("옮기기 전 경로를 같이 적는다. 2026-08-27 이전에 쓰인 보고서는 옛 경로를 인용하므로 "
      "**라운드 이름으로 이 표를 검색**하면 지금 위치가 나온다. 여기 있는 라운드는 "
      "`valset.py`·회귀 체인·BoR 스탬프·앵커 어디에도 걸리지 않는다(그래서 옮길 수 있었다).")
    w("")
    for wd in ARCHIVE_DIRS:
        ar = sorted([r for r in A if r[0] == wd], key=lambda r: (r[1], r[2]))
        if not ar:
            continue
        w(f"### `_archive/{wd}/` — {ARCHIVE_LABEL[wd]} · {len(ar)} 라운드 / "
          f"{gb(sum(S.get(r[3],0) for r in ar))} GB")
        w("")
        w("| 씬 | 라운드 | 컷 | MB | 예전 경로 |")
        w("|---|---|---:|---:|---|")
        for _w, sc, rn, p in ar:
            w(f"| `{sc}` | `{rn}` | {n_png(p)} | {S.get(p,0)//2**20} | "
              f"`look_check/{sc}/{rn}` |")
        w("")

    # ---------------- §4 ----------------
    w("## 4. `_experiments/`")
    w("")
    w("경로는 **바꾸지 않았다** — 29개 파일이 `_experiments/gates` · `_experiments/twins` 를 "
      "인용한다. 2026-07-30 이후로 렌더가 한 번도 들어가지 않은 냉동 트리다. "
      "`마지막 기록` 은 **파일** 기준이다(폴더 mtime 은 삭제만으로도 갱신돼서 쓰지 않는다). "
      "`t0_spike/` 의 08-27 은 0827 재편이 그 안의 저널 한 줄을 고쳐 쓴 것이지 렌더가 아니다.")
    w("")
    w("| 토픽 | 하위 항목 | GB | 마지막 기록 |")
    w("|---|---:|---:|---|")
    for p in sorted(glob.glob(os.path.join(LC, "_experiments", "*"))):
        if not os.path.isdir(p):
            continue
        b = du_sb([p])[p]
        w(f"| `_experiments/{os.path.basename(p)}/` | "
          f"{len([x for x in os.listdir(p)])} | {gb(b)} | {d(newest_mtime(p))} |")
    w("")
    w("| 검수 갤러리 | 항목 | MB | 마지막 기록 |")
    w("|---|---:|---:|---|")
    for p in sorted(glob.glob(os.path.join(LC, "_review", "*"))):
        if not os.path.isdir(p):
            continue
        b = du_sb([p])[p]
        w(f"| `_review/{os.path.basename(p)}/` | {len(os.listdir(p))} | "
          f"{b//2**20} | {d(newest_mtime(p))} |")
    w("")

    # ---------------- §5 ----------------
    w("## 5. 최신 라운드 탐색 (baseline hygiene)")
    w("")
    w("`ls -t <scene>/*/ | head -1` 이 **판정 라운드**를 돌려주는지, "
      "`regression_check.py` 의 `resolve_round` 가 씬마다 어떤 라운드로 떨어지는지를 "
      "이 생성 시점에 실제로 확인한 값이다.")
    w("")
    w("| 씬 | `ls -t` 머리 | 컷 | `resolve_round` 결과 | 컷 |")
    w("|---|---|---:|---|---:|")
    n_ok = 0
    for s in C["scenes"]:
        ds = [p for p in glob.glob(os.path.join(LC, s, "*")) if os.path.isdir(p)]
        ds.sort(key=os.path.getmtime, reverse=True)
        head = os.path.basename(ds[0]) if ds else "(없음)"
        hc = n_png(ds[0]) if ds else 0
        rr, rc = P_resolve(os.path.join(LC, s), C["chain_names"])
        if rr:
            n_ok += 1
        w(f"| `{s}` | `{head}` | {hc} | `{rr or '(없음)'}` | {rc} |")
    w("")
    w(f"**{n_ok}/{len(C['scenes'])} 씬이 `resolve_round` 로 해소된다** "
      f"(0 unresolved). 체인은 `look_check/README.md` §4 의 "
      f"{len(C['chain_names'])}개 이름, 앞에서부터 첫 번째로 존재하는 폴더가 이긴다.")
    w("")

    # ---------------- §6 ----------------
    w("## 6. 이동 지도 (예전 경로 → 지금 경로)")
    w("")
    w("2026-07-30 정리분 + 2026-08-27 재편분을 누적한다. 이 표가 있으므로 "
      "**씬 폴더 안에 back-compat 심볼릭 링크를 만들지 않는다**(§0).")
    w("")
    w("| 예전 경로 | 지금 경로 |")
    w("|---|---|")
    seen = set()
    for a, b in old_relocation_rows() + move_rows():
        if (a, b) in seen:
            continue
        seen.add((a, b))
        w(f"| {a} | {b} |")
    w("")
    return "\n".join(o) + "\n"


def P_resolve(scene_dir, chain):
    for name in chain:
        d_ = os.path.join(scene_dir, name)
        if os.path.isdir(d_) and glob.glob(os.path.join(d_, "*.png")):
            return name, len(glob.glob(os.path.join(d_, "*.png")))
    return None, 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stdout", action="store_true")
    a = ap.parse_args()
    C = collect()
    txt = build(C)
    if a.stdout:
        sys.stdout.write(txt)
        return
    open(INDEX, "w", encoding="utf-8").write(txt)
    print(f"wrote {os.path.relpath(INDEX, ROOT)}  "
          f"({len(txt.splitlines())} lines, {len(txt.encode())} bytes) · "
          f"live {len(C['live'])} · archive {len(C['arch'])}")


if __name__ == "__main__":
    main()
