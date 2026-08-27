#!/usr/bin/env python3
"""Exhaustive post-move existence check over every structured path field."""
import json, os, sys, collections
REPO = "/home/vislab/Desktop/work_sy/Practice_NegObs"

def res(p):
    return p if os.path.isabs(p) else os.path.join(REPO, p)

tot = collections.Counter()
missing = []

def check(path, label, val):
    tot[label] += 1
    if not os.path.exists(res(val)):
        missing.append((path, label, val))

# --- 1. big manifests: frames[*].rgb/.depth/... -----------------------------
big = []
for root, dirs, files in os.walk(os.path.join(REPO, "experiments")):
    dirs[:] = [d for d in dirs if d not in ("__pycache__", "venv_yolo")]
    for f in files:
        if f.startswith(("dataset_manifest", "split_", "corpus_v3", "cue_extent_audit")) and f.endswith(".json"):
            big.append(os.path.join(root, f))
for p in sorted(big):
    rel = os.path.relpath(p, REPO)
    try:
        doc = json.load(open(p))
    except Exception as e:
        print("  SKIP (not json) %s: %s" % (rel, e)); continue
    frames = doc.get("frames")
    if isinstance(frames, list):
        for fr in frames:
            if not isinstance(fr, dict): continue
            for k, v in fr.items():
                if isinstance(v, str) and v.startswith(("dataset/", REPO + "/dataset/")):
                    check(rel, "manifest.frames." + k, v)
    elif isinstance(frames, dict):
        for fid, fr in frames.items():
            if not isinstance(fr, dict): continue
            for k, v in fr.items():
                if isinstance(v, str) and v.startswith(("dataset/", REPO + "/dataset/")):
                    check(rel, "manifest.frames." + k, v)

# --- 2. every dataset/*/manifest.json scenes.*.out --------------------------
n_mf = 0
for g in sorted(os.listdir(os.path.join(REPO, "dataset"))):
    gp = os.path.join(REPO, "dataset", g)
    if not os.path.isdir(gp): continue
    subs = [gp] if g != "_archive" else [os.path.join(gp, x) for x in sorted(os.listdir(gp))]
    for sp in subs:
        for rnd in sorted(os.listdir(sp)):
            mf = os.path.join(sp, rnd, "manifest.json")
            if os.path.islink(mf) or not os.path.isfile(mf): continue
            n_mf += 1
            rel = os.path.relpath(mf, REPO)
            doc = json.load(open(mf))
            sc = doc.get("scenes")
            it = sc.values() if isinstance(sc, dict) else (sc or [])
            for s in it:
                if isinstance(s, dict) and isinstance(s.get("out"), str):
                    check(rel, "round manifest scenes.out", s["out"])

# --- 3. bboxes.json rgb -----------------------------------------------------
bb = os.path.join(REPO, "experiments/dayrun_0820/annotations/amodal/bboxes.json")
doc = json.load(open(bb))
for fid, v in doc["frames"].items():
    check("annotations/amodal/bboxes.json", "bboxes.rgb", v["rgb"])

# --- 4. in-dataset sidecars -------------------------------------------------
n_side = 0
for root, dirs, files in os.walk(os.path.join(REPO, "dataset")):
    for f in files:
        if f not in ("idseg_backfill.json", "heightmap_fused_meta.json"): continue
        p = os.path.join(root, f)
        if os.path.islink(p): continue
        n_side += 1
        rel = os.path.relpath(p, REPO)
        blob = open(p, encoding="utf-8").read()
        try: doc = json.loads(blob)
        except Exception: continue
        stack = [doc]
        while stack:
            cur = stack.pop()
            if isinstance(cur, dict): stack.extend(cur.values())
            elif isinstance(cur, list): stack.extend(cur)
            elif isinstance(cur, str) and (cur.startswith("dataset/") or cur.startswith(REPO + "/dataset/")):
                check(rel, "sidecar:" + f, cur)

print("big manifests scanned : %d" % len(big))
print("round manifests       : %d" % n_mf)
print("in-dataset sidecars   : %d" % n_side)
for k, v in sorted(tot.items()):
    print("   %-34s %7d" % (k, v))
print("TOTAL path fields checked: %d" % sum(tot.values()))
print("MISSING                  : %d" % len(missing))
for m in missing[:20]:
    print("   MISSING %s | %s | %s" % m)
sys.exit(1 if missing else 0)
