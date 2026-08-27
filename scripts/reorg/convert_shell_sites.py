#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""S3 -- convert the flat `dataset/<round>` SHELL sites to the round helper.

Companion of convert_code_sites.py, same reasoning (survey B ss2 / ss6.3 R3):
a path built from a shell variable -- "$REPO/dataset/$run", "$D/$1",
"dataset/${stamp}_A" -- cannot be fixed by a string rewrite and resolves to
nothing after the 0827 regrouping.

Two functions from scripts/lib/negobs_paths.sh replace them:
  negobs_round <name>          absolute dir, non-zero + stderr on a miss
  negobs_round_or_flat <name>  same, but a missing round yields the flat path

WHAT IS DELIBERATELY LEFT FLAT
  The renderers write a NEW round to `dataset/<STAMP>/<split>/<scene>` and go
  on doing so -- `local outdir="$REPO/dataset/${run}/${split}/${scene}"` is a
  WRITE and stays. `variation_kit.data_root()` has the same rule: a new stamp
  is created flat and the reorg's move script groups it afterwards. The
  "refusing run stamp" guards are `case` patterns on $1 and are untouched, as
  are the `[dry] ... -> dataset/${run}/...` progress messages (they are text).
  Every READ of a round, including the verification pass a renderer runs over
  the round it just wrote, goes through the helper.

usage
  python3 scripts/reorg/convert_shell_sites.py --dry-run
  python3 scripts/reorg/convert_shell_sites.py --apply     # .s3.bak per file
"""
from __future__ import annotations

import argparse
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SOURCE_LINE = (
    "\n# 0827 reorg: dataset/ is grouped (dataset/<group>/<round>). A round is\n"
    "# found by NAME: negobs_round (strict) / negobs_round_or_flat (tolerant).\n"
    "source \"$REPO/scripts/lib/negobs_paths.sh\"\n")
REPO_LINE = "REPO=/home/vislab/Desktop/work_sy/Practice_NegObs\n"

# the labeler wrapper shared, character for character, by the five label runners
LABEL_OLD = ('  ( cd "$LAB" && $PY labeler.py --on-round "$D/$1" '
             '--off-round "$D/$2" \\\n')
LABEL_NEW = ('  local _on _off                      # 0827: rounds are grouped\n'
             '  _on="$(negobs_round "$1")"  || return 1\n'
             '  _off="$(negobs_round "$2")" || return 1\n'
             '  ( cd "$LAB" && $PY labeler.py --on-round "$_on" '
             '--off-round "$_off" \\\n')

RULES = []          # (rel, old, new, count)


def R(rel, old, new, n=1):
    RULES.append((rel, old, new, n))


# ---------------------------------------------------------------- label runners
for rel in ("experiments/v3_0823/code/run_h12_label.sh",
            "experiments/v3_0823/code/run_h3l1_label.sh",
            "experiments/v3_0823/code/run_w2_label.sh",
            "experiments/v3_0823/code/run_w3_label.sh",
            "experiments/v3_0823/code/run_n911_label.sh"):
    R(rel, LABEL_OLD, LABEL_NEW)
for rel in ("experiments/v3_0823/code/run_h12_label.sh",
            "experiments/v3_0823/code/run_h3l1_label.sh"):
    R(rel, 'if [ -d "$D/${N}_A" ]; then',
         'if [ -d "$(negobs_round_or_flat "${N}_A")" ]; then')
    R(rel, '    --on "dataset/${S}_A" --off "dataset/${S}_C" --band H --split ext',
         '    --on "$(negobs_round "${S}_A")" --off "$(negobs_round "${S}_C")" '
         '--band H --split ext')
    R(rel, '      --on "dataset/${N}_A" --off "dataset/${N}_C" --band base --split ext',
         '      --on "$(negobs_round "${N}_A")" --off "$(negobs_round "${N}_C")" '
         '--band base --split ext')
R("experiments/v3_0823/code/run_w2_label.sh",
  '      --on "dataset/${stamp}_A" --off "dataset/${stamp}_C" \\',
  '      --on "$(negobs_round "${stamp}_A")" --off "$(negobs_round "${stamp}_C")" \\')
R("experiments/v3_0823/code/run_w3_label.sh",
  '        --on "dataset/${stamp}_A" --off "dataset/${stamp}_C" \\',
  '        --on "$(negobs_round "${stamp}_A")" --off "$(negobs_round "${stamp}_C")" \\')

# ---------------------------------------------------------------- other labellers
R("experiments/v3_0823/code/w0_label.sh",
  '  have=$(ls -d "$REPO/dataset/260825_v3w0_cuecls_${arm}"/*/*/ 2>/dev/null | wc -l)',
  '  have=$(ls -d "$(negobs_round_or_flat "260825_v3w0_cuecls_${arm}")"/*/*/ '
  '2>/dev/null | wc -l)')
R("experiments/v3_0823/code/w0_label.sh",
  '  python3 "$LAB" --on-round "$REPO/dataset/260825_v3w0_cuecls_${arm}" \\',
  '  python3 "$LAB" --on-round "$(negobs_round "260825_v3w0_cuecls_${arm}")" \\')

R("experiments/v3_0823/code/w1d_label.sh",
  '  have=$(ls -d "$REPO/dataset/${on}"/*/*/ 2>/dev/null | wc -l)',
  '  have=$(ls -d "$(negobs_round_or_flat "${on}")"/*/*/ 2>/dev/null | wc -l)')
R("experiments/v3_0823/code/w1d_label.sh",
  '  python3 "$LAB" --on-round "$REPO/dataset/$on" --off-round "$REPO/dataset/$off" \\',
  '  python3 "$LAB" --on-round "$(negobs_round "$on")" '
  '--off-round "$(negobs_round "$off")" \\')
R("experiments/v3_0823/code/w1d_label.sh",
  'NDBASE=$(ls -d "$REPO/dataset/${D_BASE}"/*/*/ 2>/dev/null | wc -l)',
  'NDBASE=$(ls -d "$(negobs_round_or_flat "${D_BASE}")"/*/*/ 2>/dev/null | wc -l)')
R("experiments/v3_0823/code/w1d_label.sh",
  '  have=$(ls -d "$REPO/dataset/260825_v3w0_cuecls_${arm}"/*/*/ 2>/dev/null | wc -l)',
  '  have=$(ls -d "$(negobs_round_or_flat "260825_v3w0_cuecls_${arm}")"/*/*/ '
  '2>/dev/null | wc -l)')
R("experiments/v3_0823/code/w1d_label.sh",
  '  python3 "$LAB" --on-round "$REPO/dataset/260825_v3w0_cuecls_${arm}" \\\n'
  '      --off-round "$REPO/dataset/${D_BASE}" --grid "$GRID" --out "$out" \\',
  '  python3 "$LAB" --on-round "$(negobs_round "260825_v3w0_cuecls_${arm}")" \\\n'
  '      --off-round "$(negobs_round "${D_BASE}")" --grid "$GRID" --out "$out" \\')

R("experiments/weekend_0823/cue_audit/eval_cueoff.sh",
  '  local on="$REPO/dataset/${stem}_${arm}"',
  '  local on; on="$(negobs_round_or_flat "${stem}_${arm}")"')
R("experiments/weekend_0823/cue_audit/eval_cueoff.sh",
  '            offdir="$REPO/dataset/${stem}_C"',
  '            offdir="$(negobs_round_or_flat "${stem}_C")"')

R("experiments/weekend_0823/v2s/code/relabel_v2s.sh",
  '  local tag="$1" on="$2" off="$3"\n',
  '  local tag="$1" on="$2" off="$3"\n'
  '  local on_dir off_dir                # 0827: rounds are grouped\n'
  '  on_dir="$(negobs_round "$on")"\n'
  '  off_dir="$(negobs_round "$off")"\n')
R("experiments/weekend_0823/v2s/code/relabel_v2s.sh",
  '    --on-round  "$REPO/dataset/$on" \\', '    --on-round  "$on_dir" \\', 2)
R("experiments/weekend_0823/v2s/code/relabel_v2s.sh",
  '    --off-round "$REPO/dataset/$off" \\', '    --off-round "$off_dir" \\', 2)

# ---------------------------------------------------------------- probe runners
R("experiments/probe_holes_0820/run_probe.sh",
  '  python3 - "$REPO/dataset/$1/manifest.json" "$2" "$3" <<\'PY\'',
  '  python3 - "$(negobs_round_or_flat "$1")/manifest.json" "$2" "$3" <<\'PY\'')
R("experiments/probe_holes_0820/run_probe.sh",
  '    d="$REPO/dataset/$run"', '    d="$(negobs_round_or_flat "$run")"')
R("experiments/probe_holes_0820/run_probe.sh",
  '  local LAB="$REPO/experiments/mainrun_0819/code/labeling"\n',
  '  local LAB="$REPO/experiments/mainrun_0819/code/labeling"\n'
  '  local ON_DIR OFF_DIR                # 0827: rounds are grouped\n'
  '  ON_DIR="$(negobs_round_or_flat "$RUN_ON")"\n'
  '  OFF_DIR="$(negobs_round_or_flat "$RUN_OFF")"\n')
R("experiments/probe_holes_0820/run_probe.sh",
  "'$REPO/dataset/$RUN_ON'", "'$ON_DIR'", 2)
R("experiments/probe_holes_0820/run_probe.sh",
  "'$REPO/dataset/$RUN_OFF'", "'$OFF_DIR'", 2)

for rel, split in (("experiments/v3_0823/code/run_n911_probe.sh", "$SPLIT"),
                   ("experiments/v3_0823/code/run_h12_probe.sh", "$SPLIT"),
                   ("experiments/v3_0823/code/run_h3l1_probe.sh", "$SPLIT"),
                   ("experiments/v3_0823/code/run_h67_probe.sh", "val")):
    R(rel, '  local d="$REPO/dataset/$run/%s/$scene"' % split,
         '  local d; d="$(negobs_round_or_flat "$run")/%s/$scene"' % split)
    R(rel, '  d="$REPO/dataset/$r"', '  d="$(negobs_round_or_flat "$r")"')

R("experiments/v3_0823/code/p5_seg_smoke.sh",
  "d = '$REPO/dataset/$RUN'", "d = '$(negobs_round_or_flat \"$RUN\")'")

# ---------------------------------------------------------------- text/h67 waves
R("experiments/v3_0823/code/run_w3_text.sh",
  '  local d="$REPO/dataset/$run/$SPLIT/$scene"',
  '  local d; d="$(negobs_round_or_flat "$run")/$SPLIT/$scene"')
R("experiments/v3_0823/code/run_w3_text.sh",
  '          d="$REPO/dataset/${pre}_${arm}/$SPLIT/$s"',
  '          d="$(negobs_round_or_flat "${pre}_${arm}")/$SPLIT/$s"')
for rel in ("experiments/v3_0823/code/run_w3_text.sh",
            "experiments/v3_0823/code/run_w3_text2.sh",
            "experiments/v3_0823/code/run_w2_h67.sh"):
    R(rel, '    d="$REPO/dataset/${pre}_${arm}"',
         '    d="$(negobs_round_or_flat "${pre}_${arm}")"')
R("experiments/v3_0823/code/run_w3_text2.sh",
  '  python3 - "$REPO/dataset/$1/$SPLIT/$2" "$3" <<\'PYEOF\'',
  '  python3 - "$(negobs_round_or_flat "$1")/$SPLIT/$2" "$3" <<\'PYEOF\'')
R("experiments/v3_0823/code/run_w2_h67.sh",
  '  python3 - "$REPO/dataset/$1/$SPLIT/$2" "$3" "$4" <<\'PYEOF\'',
  '  python3 - "$(negobs_round_or_flat "$1")/$SPLIT/$2" "$3" "$4" <<\'PYEOF\'')
for rel in ("experiments/v3_0823/code/run_w3_text2.sh",
            "experiments/v3_0823/code/run_w2_h67.sh"):
    R(rel, '          [ -d "$REPO/dataset/${pre}_${arm}/$SPLIT/$s" ] \\',
         '          [ -d "$(negobs_round_or_flat "${pre}_${arm}")/$SPLIT/$s" ] \\')

# ---------------------------------------------------------------- round renderers
# READ sites only; every `local outdir=` WRITE stays flat.
R("experiments/nightrun_0820/ctrl_dressing/run_ctrl_dressing.sh",
  '  python3 - "$REPO/dataset/$1/manifest.json" "$2" "$3" <<\'PY\'',
  '  python3 - "$(negobs_round_or_flat "$1")/manifest.json" "$2" "$3" <<\'PY\'')
R("experiments/nightrun_0820/ctrl_dressing/run_ctrl_dressing.sh",
  'say "  dataset/${RUN}: $(find "$REPO/dataset/${RUN}" -name \'*.png\' 2>/dev/null | wc -l) png · '
  '$(find "$REPO/dataset/${RUN}" -name \'*.depth.npy\' 2>/dev/null | wc -l) depth · '
  '$(find "$REPO/dataset/${RUN}" -name \'heightmap.npy\' 2>/dev/null | wc -l) heightmap"',
  'RUN_DIR="$(negobs_round_or_flat "${RUN}")"\n'
  'say "  dataset/${RUN}: $(find "$RUN_DIR" -name \'*.png\' 2>/dev/null | wc -l) png · '
  '$(find "$RUN_DIR" -name \'*.depth.npy\' 2>/dev/null | wc -l) depth · '
  '$(find "$RUN_DIR" -name \'heightmap.npy\' 2>/dev/null | wc -l) heightmap"')

R("scripts/rounds/run_260819_main.sh",
  '  python3 - "$REPO/dataset/$1/manifest.json" "$2" "$3" <<\'PY\'',
  '  python3 - "$(negobs_round_or_flat "$1")/manifest.json" "$2" "$3" <<\'PY\'')
R("scripts/rounds/run_260819_main.sh",
  '  say "  dataset/260819_main_${arm}: $(find "$REPO/dataset/260819_main_${arm}" -name \'*.png\' 2>/dev/null | wc -l) png · '
  '$(find "$REPO/dataset/260819_main_${arm}" -name \'*.depth.npy\' 2>/dev/null | wc -l) depth · '
  '$(find "$REPO/dataset/260819_main_${arm}" -name \'heightmap.npy\' 2>/dev/null | wc -l) heightmap"',
  '  d="$(negobs_round_or_flat "260819_main_${arm}")"\n'
  '  say "  dataset/260819_main_${arm}: $(find "$d" -name \'*.png\' 2>/dev/null | wc -l) png · '
  '$(find "$d" -name \'*.depth.npy\' 2>/dev/null | wc -l) depth · '
  '$(find "$d" -name \'heightmap.npy\' 2>/dev/null | wc -l) heightmap"')

R("scripts/rounds/run_260820_boost.sh",
  '  python3 - "$REPO/dataset/$1/manifest.json" "$2" "$3" <<\'PY\'',
  '  python3 - "$(negobs_round_or_flat "$1")/manifest.json" "$2" "$3" <<\'PY\'')
R("scripts/rounds/run_260820_boost.sh",
  '  d="$REPO/dataset/260820_boost_${boost}"',
  '  d="$(negobs_round_or_flat "260820_boost_${boost}")"')

# the seven wave runners: an in-heredoc python manifest read, and a summary loop
MF_OLD = 'mf = os.path.join(repo, "dataset", run, "manifest.json")'
MF_NEW = ('sys.path.insert(0, repo)                     # 0827: grouped dataset/\n'
          'from variation_kit import round_dir_or_flat\n'
          'mf = os.path.join(round_dir_or_flat(run), "manifest.json")')
for rel in ("scripts/rounds/run_260826_v3w1_lib_b.sh",
            "scripts/rounds/run_260826_v3w1_lib_b2.sh",
            "scripts/rounds/run_260826_v3w1_lib_d.sh",
            "scripts/rounds/run_260827_v3w1_lib_b3.sh",
            "scripts/rounds/run_260827_v3w1_lib_c.sh",
            "scripts/rounds/run_260826_v3a_segfill.sh",
            "scripts/rounds/run_260825_v3w0_cuecls.sh"):
    R(rel, MF_OLD, MF_NEW)
for rel in ("scripts/rounds/run_260826_v3w1_lib_b.sh",
            "scripts/rounds/run_260826_v3w1_lib_b2.sh",
            "scripts/rounds/run_260826_v3w1_lib_d.sh",
            "scripts/rounds/run_260827_v3w1_lib_b3.sh",
            "scripts/rounds/run_260826_v3a_segfill.sh"):
    R(rel, '  d="$REPO/dataset/$r"', '  d="$(negobs_round_or_flat "$r")"')


# ---------------------------------------------------------------- write sites
# `outdir` is NOT purely a write. It is `mkdir -p`'d, then `stamp_round.py
# --capture-env` writes the env sidecar into it, and run_cueoff /
# run_260827_v3w1c_hashgate READ it back (`ls "$outdir"/*.png`, `scene_ok`).
# The frames themselves are written by `run_data_render.py --run <stamp>`,
# which resolves the root through `variation_kit.data_root()` -- and that
# returns the GROUPED directory for a stamp that already exists.
#
# So a flat `outdir` would disagree with the renderer it precedes: on a re-run
# of an existing round the frames would land in the group while the sidecar and
# the verification looked at an empty flat directory -- and the stray flat
# directory would make `round_dir()` ambiguous for every reader.
# `negobs_round_or_flat` IS `data_root`'s rule: a NEW stamp still yields the
# flat `dataset/<STAMP>/...`, an existing one yields where it actually lives.
OUTDIR_OLD = '  local outdir="$REPO/dataset/${run}/${split}/${scene}"'
OUTDIR_NEW = ('  local outdir\n'
              '  outdir="$(negobs_round_or_flat "${run}")/${split}/${scene}"')
for rel in ("scripts/rounds/run_260819_main.sh",
            "scripts/rounds/run_260820_boost.sh",
            "scripts/rounds/run_260825_v3w0_cuecls.sh",
            "scripts/rounds/run_260826_v3w1_lib_b.sh",
            "scripts/rounds/run_260826_v3w1_lib_b2.sh",
            "scripts/rounds/run_260826_v3w1_lib_d.sh",
            "scripts/rounds/run_260827_v3w1_lib_b3.sh",
            "scripts/rounds/run_260827_v3w1_lib_c.sh",
            "scripts/rounds/run_260826_v3a_segfill.sh"):
    R(rel, OUTDIR_OLD, OUTDIR_NEW)
R("scripts/rounds/run_260827_v3w1c_hashgate.sh",
  '  outdir="$REPO/dataset/${STAMP}/${split}/${s}"',
  '  outdir="$(negobs_round_or_flat "${STAMP}")/${split}/${s}"')
R("experiments/probe_holes_0820/run_probe.sh",
  '  local outdir="$REPO/dataset/${run}/probe/${scene}"',
  '  local outdir\n  outdir="$(negobs_round_or_flat "${run}")/probe/${scene}"')
R("experiments/nightrun_0820/ctrl_dressing/run_ctrl_dressing.sh",
  '  local outdir="$REPO/dataset/${RUN}/${split}/${scene}"',
  '  local outdir\n  outdir="$(negobs_round_or_flat "${RUN}")/${split}/${scene}"')
R("experiments/weekend_0823/cue_audit/run_cueoff.sh",
  '             "$REPO/dataset/$run/$split/$scene"',
  '             "$(negobs_round_or_flat "$run")/$split/$scene"')

# run_260730_data_mini.sh has no REPO= line: it `cd`s to the repo first.
R("scripts/rounds/run_260730_data_mini.sh",
  'cd /home/vislab/Desktop/work_sy/Practice_NegObs || exit 9\n',
  'cd /home/vislab/Desktop/work_sy/Practice_NegObs || exit 9\n'
  '# 0827 reorg: a round is found by NAME (dataset/<group>/<round>).\n'
  'source scripts/lib/negobs_paths.sh\n')
R("scripts/rounds/run_260730_data_mini.sh",
  'python3 scripts/stamp_round.py dataset/${RUN} $RUN mini 2>&1 | tee -a $LOG',
  'python3 scripts/stamp_round.py "$(negobs_round_or_flat "$RUN")" $RUN mini '
  '2>&1 | tee -a $LOG')


def main(argv=None):
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--apply", action="store_true")
    a = ap.parse_args(argv)

    texts, log = {}, {}
    for rel, old, new, want in RULES:
        p = os.path.join(REPO, rel)
        t = texts.get(rel) or io.open(p, encoding="utf-8", newline="").read()
        n = t.count(old)
        assert n == want, "%s: matched %d, want %d for\n%r" % (rel, n, want, old[:120])
        texts[rel] = t.replace(old, new, want)
        log.setdefault(rel, 0)
        log[rel] += want

    # every converted script must source the helper, exactly once
    for rel in sorted(texts):
        t = texts[rel]
        if "negobs_paths.sh" in t:
            continue
        assert t.count(REPO_LINE) == 1, "%s: REPO line x%d" % (rel, t.count(REPO_LINE))
        texts[rel] = t.replace(REPO_LINE, REPO_LINE + SOURCE_LINE, 1)

    for rel in sorted(log):
        print("  %2d sites  %s" % (log[rel], rel))
    print("\n%d shell files · %d sites" % (len(log), sum(log.values())))

    if a.apply:
        for rel, new in sorted(texts.items()):
            p = os.path.join(REPO, rel)
            src = io.open(p, encoding="utf-8", newline="").read()
            io.open(p + ".s3.bak", "w", encoding="utf-8", newline="").write(src)
            tmp = p + ".s3tmp"
            io.open(tmp, "w", encoding="utf-8", newline="").write(new)
            os.replace(tmp, p)
        print("applied to %d files (.s3.bak kept)" % len(texts))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
