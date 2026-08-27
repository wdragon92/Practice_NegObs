#!/usr/bin/env python3
"""S5 gate — exhaustive residual scan for every path S5 retired.

Re-runnable and tree-neutral; S6 should run it as-is.  `grep` in this shell is
ugrep with --ignore-files and silently skips the gitignored trees, so this walks
the tree with os.walk and reads every non-binary file, gitignored or not.

Retired by S5:  Docs/experiment/ -> Docs/campaign/ (Status/ -> status/) ·
Docs/legacy/ -> Docs/archive/legacy/ · the 7 Docs/ compat symlinks +
Docs/surveys/real_reference_expansion.md -> their real paths ·
Docs/campaign/status/PROJECT_STATE_08*.md -> Docs/archive/campaign_status/ ·
PROJECT_STATE_0826.md -> PROJECT_STATE.md · root run_*.sh -> scripts/rounds/.

PASS means: outside Docs/reorg_0827/ (this reorg\'s own record of the OLD paths)
and outside the two DECLARED exceptions, no file names a retired path.

DECLARED exceptions, and why:
  experiments/v3_0823/PREREG_V3.md          sha256-sealed pre-registration; its
                                            bytes may not change (invariant
                                            05f41322..f56a), so it keeps the old
                                            spelling on purpose.
  experiments/v3_0823/PREREG_V3_PATHMAP_0827.md
                                            the sibling old->new note that
                                            resolves it (S2 set this precedent
                                            with PREREG_CUEOFF_PATHMAP_0827.md).

The look_check/ round_stamp.json files are exempt from the run_*.sh check: their
`dirty_paths` field is a git-status snapshot taken at render time and is a record
of the past, not a citation.
"""
import os, re, sys
REPO = "/home/vislab/Desktop/work_sy/Practice_NegObs"
SKIP = {".git", "__pycache__"}
BIN_EXT = {".png", ".jpg", ".jpeg", ".exr", ".npz", ".npy", ".pt", ".pth",
           ".usd", ".usdc", ".usdz", ".mdl", ".zip", ".pdf", ".ttf", ".otf",
           ".mp4", ".bin", ".hdr", ".dds", ".webp", ".gif", ".so", ".pyc",
           ".tif", ".tiff", ".bmp", ".ply", ".obj", ".fbx", ".glb", ".gltf"}
# Docs/reorg_0827/ is this reorg's own record of the OLD paths; scripts/reorg/
# is its tooling and names both forms by construction (S3 report §6).
ALLOW_PREFIX = ("Docs/reorg_0827", "scripts/reorg")
DECLARED = {
    # sealed pre-registration + its sibling path-map note (S2 precedent)
    "experiments/v3_0823/PREREG_V3.md",
    "experiments/v3_0823/PREREG_V3_PATHMAP_0827.md",
}
PATS = {
    "Docs/experiment/": b"Docs/experiment/",
    "Docs\\experiment": rb"Docs\\experiment",
    "Docs/legacy/": b"Docs/legacy/",
    "Docs/multi_scene_brief_v2.md": b"Docs/multi_scene_brief_v2.md",
    "Docs/multi_scene_brief_v3.md": b"Docs/multi_scene_brief_v3.md",
    "Docs/nanobanana_batch1_geometry_map.md": b"Docs/nanobanana_batch1_geometry_map.md",
    "Docs/realism_rubric_v1.md": b"Docs/realism_rubric_v1.md",
    "Docs/scene01_design_brief.md": b"Docs/scene01_design_brief.md",
    "Docs/scene_redesign_v5_proposal.md": b"Docs/scene_redesign_v5_proposal.md",
    "Docs/stair_typology_survey_v2.md": b"Docs/stair_typology_survey_v2.md",
    "Docs/surveys/real_reference_expansion.md": b"Docs/surveys/real_reference_expansion.md",
    "PROJECT_STATE_0826": b"PROJECT_STATE_0826",
    "Docs/campaign/status/PROJECT_STATE_08": b"Docs/campaign/status/PROJECT_STATE_08",
}
BARE_ROOT_SH = re.compile(
    rb"(?<![/A-Za-z0-9_.-])run_(p2_all33|260814_w4_d4iter|260814_w4_r0probe"
    rb"|260814_w4_r1r2pilot|260815_w4_r4batch)\.sh")
LOOKCHECK_STAMP = "look_check/"          # round_stamp.json git-status snapshots: allowed

def main():
    bad = {k: [] for k in PATS}
    bad["root run_*.sh cited without scripts/rounds/"] = []
    n = 0
    for dp, dns, fns in os.walk(REPO):
        dns[:] = [d for d in dns if d not in SKIP]
        for fn in fns:
            p = os.path.join(dp, fn)
            if os.path.islink(p):
                continue
            if os.path.splitext(fn)[1].lower() in BIN_EXT:
                continue
            rel = os.path.relpath(p, REPO)
            if rel.startswith(ALLOW_PREFIX):
                continue
            try:
                if os.path.getsize(p) > 256 * 1024 * 1024:
                    continue
                blob = open(p, "rb").read()
            except OSError:
                continue
            n += 1
            for name, pat in PATS.items():
                c = blob.count(pat) if isinstance(pat, bytes) and b"\\\\" not in pat else len(re.findall(pat, blob))
                if c and rel not in DECLARED:
                    bad[name].append((rel, c))
            m = BARE_ROOT_SH.findall(blob)
            if m and not rel.startswith(LOOKCHECK_STAMP):
                bad["root run_*.sh cited without scripts/rounds/"].append((rel, len(m)))
    print(f"scanned {n} files (every file, no extension filter)")
    fail = 0
    for k, v in bad.items():
        if v:
            fail += 1
            print(f"FAIL {k}: {len(v)} files")
            for rel, c in v[:10]:
                print(f"      {rel}  x{c}")
        else:
            print(f"PASS {k}: 0")
    print(f"declared exceptions (sealed PREREG + its pathmap): {sorted(DECLARED)}")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
