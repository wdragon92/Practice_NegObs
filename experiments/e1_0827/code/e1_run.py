# -*- coding: utf-8 -*-
"""e1_run.py -- CLI over a list of (round, scene, frame).

    python3 e1_run.py --frame 260819_main_on:scene01:L0__s20260819__0000.png \
                      --out ../annotations/_smoke --overlays ../overlays/_smoke \
                      --camera-check --prim-census

    python3 e1_run.py --list frames.txt --out ... --overlays ...
        frames.txt: one `round:scene:frame.png` per line, '#' comments allowed.

Writes `<out>/edge_manifest_v1.json` + `.csv`, per-edge interior masks under
`<out>/masks/`, overlays under `<overlays>/`, and prints every measured number
it produced. It prints them raw: no parameter here is ever nudged to make an
output look better (brief §3 '침묵 수리 금지').
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import e1_const as C          # noqa: E402
import e1_label_frame as LF    # noqa: E402
import e1_overlay as OV        # noqa: E402
import e1_schema as S          # noqa: E402
import e1_visibility as V      # noqa: E402


def parse_spec(text):
    parts = text.split(":")
    if len(parts) != 3:
        raise SystemExit("[e1] --frame wants round:scene:frame.png, got %r" % text)
    return tuple(parts)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame", action="append", default=[],
                    help="round:scene:frame.png (repeatable)")
    ap.add_argument("--list", help="file of round:scene:frame.png lines")
    ap.add_argument("--out", required=True, help="annotations output dir")
    ap.add_argument("--overlays", help="overlay output dir (omit to skip)")
    ap.add_argument("--domain", default="stair", choices=list(S.DOMAIN_VALUES))
    ap.add_argument("--camera-check", action="store_true",
                    help="run the e1_camera.verify proof on every frame")
    ap.add_argument("--prim-census", action="store_true",
                    help="print every prim that blocked something, with counts")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)

    specs = [parse_spec(s) for s in a.frame]
    if a.list:
        with open(a.list, encoding="utf-8") as fh:
            for line in fh:
                line = line.split("#")[0].strip()
                if line:
                    specs.append(parse_spec(line))
    if not specs:
        raise SystemExit("[e1] no frames given")

    os.makedirs(a.out, exist_ok=True)
    classifier = V.PrimClassifier.load()
    records, problems, census = [], [], {}

    for rnd, scene, frame in specs:
        rec, ex = LF.label_frame(rnd, scene, frame, a.out, domain=a.domain,
                                 classifier=classifier,
                                 want_camera_check=a.camera_check,
                                 keep_arrays=bool(a.overlays) or a.prim_census)
        bad = S.validate(rec)
        if bad:
            problems.append((rec.frame_id, bad))
        records.append(rec)

        if a.overlays and "kept" in ex:
            OV.draw(rec, ex, os.path.join(
                a.overlays, rec.frame_id.replace("/", "__") + ".overlay.png"))

        for item in ex.get("kept", []) + ex.get("dropped", []):
            for p, n in item["diag"].get("blocker_prims", {}).items():
                census[p] = census.get(p, 0) + n

        if not a.quiet:
            _print_frame(rec)

    # §5 keeps the two domains in separate files, and a run is single-domain,
    # so the stem is chosen from the domain rather than typed.
    stem = S.MANIFEST_STEM[a.domain]
    jpath = os.path.join(a.out, stem + ".json")
    S.dump_json(records, jpath)
    S.dump_csv(records, os.path.join(a.out, stem + ".csv"))
    mixed = {r.domain for r in records}
    if len(mixed) > 1:
        print("[e1] ! frames from more than one domain in one manifest: %s" % mixed)

    unresolved = sorted({p for r in records
                         for p in r.notes["diag"].get("unresolved_occluders", [])})
    with open(os.path.join(a.out, "unresolved_occluders.txt"), "w",
              encoding="utf-8") as fh:
        fh.write("\n".join(unresolved) + ("\n" if unresolved else ""))
    with open(os.path.join(a.out, "prim_blocker_census.json"), "w",
              encoding="utf-8") as fh:
        json.dump(dict(sorted(census.items(), key=lambda kv: -kv[1])), fh,
                  ensure_ascii=False, indent=1, sort_keys=False)
        fh.write("\n")

    print("\n[e1] wrote %s (%d frames), const_fingerprint=%s"
          % (jpath, len(records), C.fingerprint()))
    print("[e1] tier_now:", {t: sum(1 for r in records if r.tier_now == t)
                             for t in S.TIER_NOW_VALUES})
    print("[e1] schema problems:", len(problems))
    for fid, bad in problems:
        for b in bad:
            print("   !", fid, b)
    if a.prim_census:
        print("[e1] blocking prims (path -> blocked sample count):")
        for p, n in sorted(census.items(), key=lambda kv: -kv[1])[:C.CENSUS_TOP_N]:
            print("   %8d  %s -> %s" % (n, classifier.classify(p), p))
    return 0 if not problems else 1


def _print_frame(rec):
    d = rec.notes["diag"]
    print("\n=== %s  tier_now=%s  edges=%d" % (rec.frame_id, rec.tier_now,
                                               len(rec.edges)))
    for m in rec.notes["messages"]:
        print("    note:", m)
    if "camera_check" in d:
        c = d["camera_check"]
        print("    camera: intrinsic_residual=%s deg | A |hm(eye)-ground_z| = %s m"
              "  (clamped=%s)"
              % (_f(c["intrinsic_residual_deg"], C.PRINT_DP_FINE),
                 _f(c["A_abs_diff_m"], C.PRINT_DP_FINE), c.get("A_clamped")))
        print("            B roundtrip px median/p90 = %s / %s  (n=%d)"
              % (_f(c["B_roundtrip_px_median"], C.PRINT_DP_FINE),
                 _f(c["B_roundtrip_px_p90"], C.PRINT_DP_FINE),
                 c["B_n"]))
        print("            C |dz| vs heightmap  all: median %s p90 %s (n=%d)"
              % (_f(c["C_dz_median_all_m"], C.PRINT_DP_COARSE),
                 _f(c["C_dz_p90_all_m"], C.PRINT_DP_COARSE),
                 c["C_n_all"]))
        for k, v in c["C_near"].items():
            print("            C |dz| within %-5s median %s p90 %s (n=%d)"
                  % (k, _f(v["dz_median_m"], C.PRINT_DP_COARSE),
                     _f(v["dz_p90_m"], C.PRINT_DP_COARSE), v["n"]))
    if "route_a" in d:
        ra = d["route_a"]
        print("    route(a): walkable %d / reachable %d / drop>=thr %d / edge cells %d"
              " -> components %d, kept %d, blocked-only %d"
              % (ra["n_walkable"], ra["n_reachable"], ra["n_drop_ge_thr"],
                 ra["n_edge_cells"], ra.get("n_components", 0),
                 ra.get("n_instances_kept", 0), ra.get("n_instances_blocked_only", 0)))
    if "route_b" in d:
        rb = d["route_b"]
        print("    route(b): jump px %d -> thinned %d -> components %d (%d px)"
              % (rb["n_jump_px"], rb["n_thin_px"], rb["n_components"],
                 rb["n_component_px"]))
    for e in rec.edges:
        print("    %s dist %s/%s m | int %d px (h%d w%d) | a-b %s/%s/%s px"
              " | occl flag=%s prim=%s frac=%s"
              % (e.edge_id, _f(e.dist_m.min), _f(e.dist_m.median), e.int_area_px,
                 e.int_h_px, e.int_w_px, _f(e.src_disagree_px.mean),
                 _f(e.src_disagree_px.median), _f(e.src_disagree_px.p90),
                 e.occluder.flag, e.occluder.prim, _f(e.occluder.occl_frac)))
    if d.get("unresolved_occluders"):
        print("    unresolved occluders:", d["unresolved_occluders"])


def _f(v, nd=None):
    nd = C.PRINT_DP_SHORT if nd is None else nd
    return "-" if v is None else ("%.*f" % (nd, v))


if __name__ == "__main__":
    raise SystemExit(main())
