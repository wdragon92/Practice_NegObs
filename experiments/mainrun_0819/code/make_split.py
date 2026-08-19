"""Scene-unit train/val/test split + a PROVISIONAL proposal report.

Split is BY SCENE: every frame of a scene (both the on- and the off-arm) follows its scene, which is
what keeps the hazard-off false-alarm frames from leaking a scene across splits.
test = 7±1 scenes (20-25%) with >=2 top-strict-H scenes, >=1 hard-negative scene, off-arm preferred,
and the tier histogram closest (L1) to the global one. val = 2 of the remainder, >=1 with strict-H.

--exclude-scenes (D14④) holds scenes out of EVERY split: they enter no train/val/test list, they
are dropped from the eligible pool and from the global tier histogram, and they are reported under
"PROVISIONAL-HOLD (아침 결재 대상)". Accepts a comma list or @path.json (the array gates.py writes
to annotations/hold_scenes.json). All PROOF checks are expressed against the eligible pool so a
held-out scene keeps them green instead of reading as an unassigned-scene failure.
"""
from __future__ import annotations

import argparse
import json
import math
import random
from collections import Counter

TIERS = ["V", "E", "H", "off"]


def parse_exclude(spec):
    """--exclude-scenes value -> list of scene ids.  "@path.json" reads the JSON
    array gates.py writes (a dict is tolerated: its "hold"/"scenes" key)."""
    if not spec:
        return []
    if spec.startswith("@"):
        with open(spec[1:]) as f:
            d = json.load(f)
        if isinstance(d, dict):
            d = d.get("hold") or d.get("scenes") or []
        return [str(x) for x in d]
    return [x.strip() for x in spec.split(",") if x.strip()]


def scene_stats(man):
    S = {}
    for r in man["frames"]:
        s = S.setdefault(r["scene_id"], dict(n=0, off=0, strict_h=0, tier=Counter()))
        s["n"] += 1
        t = r.get("tier") or "none"
        s["tier"][t] += 1
        if r.get("toggle_state") == "off":
            s["off"] += 1
        if t == "H" and r.get("toggle_state") == "on" and any(int(v) for v in r["polar_gt"]):
            s["strict_h"] += 1
    return S


def hist(S, scenes):
    c = Counter()
    for s in scenes:
        c.update(S[s]["tier"])
    tot = sum(c[t] for t in TIERS) or 1
    return [c[t] / tot for t in TIERS], c


def l1(a, b):
    return sum(abs(x - y) for x, y in zip(a, b))


def pick(S, pool, sizes, must_h, must_hn, gh, rng, trials=20000, force=()):
    """Random search over candidate combos honouring the hard constraints; L1-to-global scored."""
    best, best_sc = None, math.inf
    hpool = [s for s in pool if s in must_h]
    npool = [s for s in pool if s in must_hn]
    for _ in range(trials):
        k = rng.choice(sizes)
        forced = set(f for f in force if f in pool)
        if hpool:
            forced |= set(rng.sample(hpool, min(2, len(hpool))))
        if npool:
            forced |= {rng.choice(npool)}
        rest = [s for s in pool if s not in forced]
        if len(forced) > k or len(rest) < k - len(forced):
            continue
        cand = sorted(forced | set(rng.sample(rest, k - len(forced))))
        if len(hpool) >= 2 and len(set(cand) & set(hpool)) < 2:
            continue
        if npool and not (set(cand) & set(npool)):
            continue
        h, _ = hist(S, cand)
        frac_off = sum(1 for s in cand if S[s]["off"] > 0) / len(cand)
        sc = l1(h, gh) + 0.10 * (1 - frac_off)
        if sc < best_sc:
            best, best_sc = cand, sc
    return best, best_sc


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--manifest", required=True)
    p.add_argument("--out", default="split_v1.json")
    p.add_argument("--report", default="SPLIT_PROPOSAL.md")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--hard-negatives", nargs="*", default=["sceneN3"],
                   help="scene ids that are hard negatives; >=1 must land in test")
    p.add_argument("--force-test", default="",
                   help="[D18] comma list of scene ids pinned into test (headline-power steering)")
    p.add_argument("--n-val", type=int, default=2)
    p.add_argument("--trials", type=int, default=20000)
    p.add_argument("--exclude-scenes", default="",
                   help="D14 PROVISIONAL-HOLD: comma list of scene ids, or @path.json "
                        "(e.g. @annotations/hold_scenes.json). Held scenes go to NO split.")
    a = p.parse_args(argv)

    rng = random.Random(a.seed)
    with open(a.manifest) as f:
        man = json.load(f)
    S = scene_stats(man)
    all_scenes = sorted(S)
    # D14: held scenes leave the eligible pool entirely -- no split, and out of the
    # global tier histogram the test set is matched against.
    excl = parse_exclude(a.exclude_scenes)
    heldset = {s for s in excl if s in S}
    held = sorted(heldset)
    missing_excl = sorted(s for s in excl if s not in S)
    scenes = [s for s in all_scenes if s not in heldset]
    N = len(scenes)
    if not scenes:
        raise SystemExit("[fatal] every scene in the manifest is on PROVISIONAL-HOLD")
    gh, gc = hist(S, scenes)

    lo, hi = max(6, math.ceil(0.20 * N)), min(8, math.floor(0.25 * N))
    sizes = list(range(lo, hi + 1)) or [max(1, min(7, N - a.n_val - 1))]
    ranked = sorted(scenes, key=lambda s: (-S[s]["strict_h"], s))
    top_k = max(3, math.ceil(0.25 * N))
    must_h = [s for s in ranked[:top_k] if S[s]["strict_h"] > 0]
    hn = [s for s in a.hard_negatives if s in S]
    missing_hn = [s for s in a.hard_negatives if s not in S]

    force_test = [s for s in a.force_test.split(",") if s] if a.force_test else []
    missing_ft = [s for s in force_test if s not in scenes]
    test, ts = pick(S, scenes, sizes, must_h, hn, gh, rng, a.trials, force=force_test)
    if test is None:
        raise SystemExit("[fatal] no test combo satisfied the constraints")
    rem = [s for s in scenes if s not in test]
    # [D18] val must NOT consume strict-H scenes: val only steers early-stop/tau*,
    # while H frames are the headline currency — they belong to train (supervision)
    # and test (evaluation). Pick val from H-free scenes; fall back only if such a
    # pool is too small. Ensure val still carries >=1 positive (V/E) scene for F1.
    val_pool = [s for s in rem if S[s]["strict_h"] == 0]
    if len(val_pool) < a.n_val:
        val_pool = rem
    val, vs = pick(S, val_pool, [a.n_val], [], [], gh, rng, a.trials)
    if val is None:
        val, vs = sorted(val_pool)[: a.n_val], float("nan")
    if not any(S[s]["tier"].get(t, 0) > 0 for s in val for t in ("V", "E")):
        cand = sorted((s for s in val_pool if s not in val
                       and any(S[s]["tier"].get(t, 0) > 0 for t in ("V", "E"))),
                      key=lambda s: -sum(S[s]["tier"].get(t, 0) for t in ("V", "E")))
        if cand:
            val = sorted([cand[0]] + list(val)[: a.n_val - 1])
    train = sorted(s for s in rem if s not in val)

    split = dict(train=train, val=sorted(val), test=sorted(test))
    with open(a.out, "w") as f:
        # `hold` is a RECORD, not a subset: consumers index the file by subset name
        # ("train"/"val"/"test"), so the held scenes are simply reachable by nobody.
        json.dump(dict(split, hold=held), f, indent=2)

    # ---- proof -------------------------------------------------------------
    where = {}
    for k, v in split.items():
        for s in v:
            where.setdefault(s, []).append(k)
    dup = {s: k for s, k in where.items() if len(k) > 1}
    unassigned = [s for s in scenes if s not in where]
    held_in_split = sorted(s for s in held if s in where)
    frame_held = [r["frame_id"] for r in man["frames"] if r["scene_id"] in heldset]
    frame_bad = [r["frame_id"] for r in man["frames"]
                 if r["scene_id"] not in heldset and len(where.get(r["scene_id"], [])) != 1]
    arms = {}
    for r in man["frames"]:
        if r["scene_id"] in heldset:
            continue
        arms.setdefault(r["scene_id"], set()).add(where.get(r["scene_id"], ["?"])[0])
    arm_bad = [s for s, v in arms.items() if len(v) != 1]
    proof = [
        f"PROOF-1 scene count: {len(train)} train + {len(val)} val + {len(test)} test "
        f"= {len(train)+len(val)+len(test)} == {N} eligible scenes "
        f"({len(all_scenes)} manifest − {len(held)} held) -> "
        f"{'PASS' if len(train)+len(val)+len(test) == N else 'FAIL'}",
        f"PROOF-2 no scene in two splits: {len(dup)} duplicates -> {'PASS' if not dup else 'FAIL ' + str(dup)}",
        f"PROOF-3 no ELIGIBLE scene unassigned: {len(unassigned)} -> "
        f"{'PASS' if not unassigned else 'FAIL ' + str(unassigned)}",
        f"PROOF-4 every non-held frame resolves to exactly one split: {len(frame_bad)} bad of "
        f"{len(man['frames']) - len(frame_held)} ({len(frame_held)} frames held out) -> "
        f"{'PASS' if not frame_bad else 'FAIL'}",
        f"PROOF-5 both arms (on/off) of a scene share its split (split key is scene_id): "
        f"{len(arm_bad)} violations -> {'PASS' if not arm_bad else 'FAIL ' + str(arm_bad)}",
        f"PROOF-6 test size {len(test)} in 7±1 and {100*len(test)/N:.1f}% of the {N} eligible "
        f"scenes (target 20-25%) -> {'PASS' if 6 <= len(test) <= 8 else 'FAIL'}",
        f"PROOF-7 test contains >=2 top-strict-H scenes: {sorted(set(test) & set(must_h))} -> "
        f"{'PASS' if len(set(test) & set(must_h)) >= 2 or len(must_h) < 2 else 'FAIL'}",
        f"PROOF-8 test contains >=1 hard-negative {hn}: {sorted(set(test) & set(hn))} -> "
        f"{'PASS' if (set(test) & set(hn)) or not hn else 'FAIL'}",
        (f"PROOF-7b [D18] forced-into-test: {force_test or 'none'}"
         + (f" (MISSING from eligible pool: {missing_ft})" if missing_ft else "") + " -> PASS"),
        f"PROOF-9 [D18] val is strict-H-free (H reserved for train/test) and has >=1 positive scene: "
        f"H-in-val={sum(S[s]['strict_h'] for s in val)}, "
        f"pos-scenes={[s for s in val if any(S[s]['tier'].get(t,0)>0 for t in ('V','E'))]} -> "
        f"{'PASS' if sum(S[s]['strict_h'] for s in val) == 0 and any(S[s]['tier'].get(t,0)>0 for s in val for t in ('V','E')) else 'WARN'}",
        f"PROOF-10 PROVISIONAL-HOLD scenes appear in NO split: "
        f"{held or 'none held'}, {len(held_in_split)} leaked -> "
        f"{'PASS' if not held_in_split else 'FAIL ' + str(held_in_split)}"
        + (f"  **--exclude-scenes ids not in manifest: {missing_excl}**" if missing_excl else ""),
    ]

    L = ["# SPLIT_PROPOSAL — PROVISIONAL — 아침 승인 대상", "",
         f"manifest: `{a.manifest}` · seed {a.seed} · {N} eligible scenes "
         f"({len(all_scenes)} in manifest − {len(held)} held) / {len(man['frames'])} frames "
         f"({len(frame_held)} held out)",
         f"hard-negative arg: {a.hard_negatives}"
         + (f"  **not found in manifest: {missing_hn}**" if missing_hn else ""),
         f"test L1-to-global tier distance (incl. off-arm preference term): {ts:.4f}; val {vs:.4f}", ""]

    L += ["## PROVISIONAL-HOLD (아침 결재 대상)", ""]
    if held:
        L += [f"`--exclude-scenes {a.exclude_scenes}` → **{len(held)} scene(s) in NO split** "
              "(not train, not val, not test). Per D14④ these are batch-1 non-stair drop "
              "scenes that came out all-negative under the D10 step gate; holding them out "
              "keeps a possibly-wrong label out of the headline metric until the morning "
              "ruling. Re-run this script without `--exclude-scenes` (or with a trimmed list) "
              "once the gate is adopted or reverted.", "",
              "| scene | frames | off-arm | strict-H |", "|---|---|---|---|"]
        L += [f"| {s} | {S[s]['n']} | {S[s]['off']} | {S[s]['strict_h']} |" for s in held]
        if missing_excl:
            L.append(f"\n**ids passed but absent from the manifest: {missing_excl}**")
        L.append("")
    else:
        L += ["none — every manifest scene is eligible"
              + (f" (ids passed but absent from the manifest: {missing_excl})"
                 if missing_excl else "")
              + ".", ""]

    L += ["## Assignment", "", "| split | n scenes | scenes |", "|---|---|---|"]
    for k in ("train", "val", "test"):
        L.append(f"| {k} | {len(split[k])} | {', '.join(split[k])} |")
    if held:
        L.append(f"| **HOLD** | {len(held)} | {', '.join(held)} |")
    L += ["", "## Tier distribution (frame counts, share)", "",
          "| split | " + " | ".join(TIERS) + " | frames |", "|" + "---|" * (len(TIERS) + 2)]
    for k in ("train", "val", "test", None):
        sel = scenes if k is None else split[k]
        h, c = hist(S, sel)
        tot = sum(c[t] for t in TIERS)
        L.append(f"| {k or '**global**'} | "
                 + " | ".join(f"{c[t]} ({h[i]:.2f})" for i, t in enumerate(TIERS))
                 + f" | {tot} |")
    L += ["", "## Per-scene", "", "| scene | split | frames | off-arm | strict-H | "
          + " | ".join(TIERS) + " |", "|" + "---|" * (5 + len(TIERS))]
    for s in all_scenes:
        st = S[s]
        w = "**HOLD**" if s in heldset else where.get(s, ["?"])[0]
        L.append(f"| {s} | {w} | {st['n']} | {st['off']} | {st['strict_h']} | "
                 + " | ".join(str(st["tier"][t]) for t in TIERS) + " |")
    L += ["", "## Violation proof", "", "```"] + proof + ["```", "",
          f"top-strict-H pool (top {top_k} by strict-H frame count): {must_h}", ""]
    with open(a.report, "w") as f:
        f.write("\n".join(L))

    for ln in proof:
        print(ln)
    print(f"[split] train={len(train)} val={len(val)} test={len(test)} "
          f"hold={len(held)}{' ' + str(held) if held else ''} -> {a.out}, {a.report}")
    return 0 if all("FAIL" not in x for x in proof) else 1


if __name__ == "__main__":
    raise SystemExit(main())
