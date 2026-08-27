#!/usr/bin/env bash
# negobs_paths.sh — one shell-side answer to "where does round <name> live?"
#
# Added by the 0827 reorg (Docs/reorg_0827/). `dataset/` used to be flat
# (`dataset/<round>`); it is now grouped (`dataset/<group>/<round>`). Round
# NAMES did not change, so shell callers stop writing "$REPO/dataset/$run" and
# write `negobs_round "$run"` instead. The lookup itself lives in exactly one
# place — variation_kit.round_dir() — and this is a thin wrapper over it, so
# the two never disagree.
#
# Usage
#   source "$REPO/scripts/lib/negobs_paths.sh"
#   d="$(negobs_round 260819_main_on)" || exit 1     # absolute dir on stdout
#   bash scripts/lib/negobs_paths.sh 260819_main_on  # also runnable directly
#
# On a miss the message goes to stderr and the status is 1 (non-zero), never
# an empty string on stdout: a silent empty path is the failure mode this
# whole helper exists to remove.
#
# Honours NEGOBS_DATASET_ROOT (inherited by the python child).

# Repo root = two levels up from this file (scripts/lib/ -> scripts/ -> repo).
NEGOBS_LIB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NEGOBS_REPO="$(cd "${NEGOBS_LIB_DIR}/../.." && pwd)"
export NEGOBS_REPO

negobs_round() {
    local name="$1"
    if [ -z "$name" ]; then
        echo "negobs_round: usage: negobs_round <round-name>" >&2
        return 1
    fi
    local out
    out="$(NEGOBS_REPO="$NEGOBS_REPO" python3 -c '
import os, sys
sys.path.insert(0, os.environ["NEGOBS_REPO"])
import variation_kit as vk
try:
    sys.stdout.write(vk.round_dir(sys.argv[1]))
except Exception as exc:
    sys.stderr.write(str(exc) + "\n")
    raise SystemExit(1)
' "$name")" || return 1
    printf '%s\n' "$out"
}

negobs_round_or_flat() {
    # Like negobs_round, but a round that does NOT exist yields the flat
    # "$REPO/dataset/<name>" instead of an error, and the status is 0.
    #
    # For the call sites that already guard themselves -- `[ -d "$d" ] || ...`,
    # a `[skip] absent` branch, a summary line that prints 0 png. Those keep
    # their own report; what this fixes is the other half of the 0827 problem,
    # an EXISTING round that a flat path can no longer see. Use negobs_round
    # (which fails loudly) wherever a missing round is a bug.
    local name="$1"
    if [ -z "$name" ]; then
        echo "negobs_round_or_flat: usage: negobs_round_or_flat <round-name>" >&2
        return 1
    fi
    local out
    out="$(NEGOBS_REPO="$NEGOBS_REPO" python3 -c '
import os, sys
sys.path.insert(0, os.environ["NEGOBS_REPO"])
import variation_kit as vk
sys.stdout.write(vk.round_dir_or_flat(sys.argv[1]))
' "$name")" || return 1
    printf '%s\n' "$out"
}

# Run directly (not sourced): resolve the arguments given on the command line.
if [ "${BASH_SOURCE[0]}" = "$0" ]; then
    rc=0
    for a in "$@"; do negobs_round "$a" || rc=1; done
    [ $# -eq 0 ] && { echo "usage: $0 <round-name> [...]" >&2; rc=1; }
    exit $rc
fi
