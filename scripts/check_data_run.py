#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate a data run — the acceptance gate for `role=data` output.

Five checks, all on the run's own artefacts (no reference render, because the
data channel has none by design — spec B2):

  1  exposure sanity        every cut inside criterion C's absolute readability
                            band; the GROUND band darkens with net EV among
                            sun-bearing conditions (per scene, so albedo cancels);
                            and a sunless condition has less deep shadow than the
                            L0 reference. Deliberately NOT "frame mean orders by
                            net EV" — see the comment at check 1 for why that is
                            physically wrong.
  2  azimuth ledger         |d_az| inside the SP-2 measured allowance for that
                            (scene, condition), and above the D6 astronomical
                            floor where one applies.
  3  camera placement       ground-relative height actually landed
                            (`ground_below` == `h_rel`), nothing buried, and the
                            `ground_kit.frame_budget` advisory summarised.
  4  file / manifest        1:1 between manifest and disk, unique content,
                            1920x1080, and NOTHING written under look_check/.
  5  throughput             measured s/cut against SP-3's 2.87 s.

usage: python3 scripts/check_data_run.py [run]        (default 260730_data_mini)
GPU 0.
"""
from __future__ import annotations

import glob
import hashlib
import json
import os
import statistics as st
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)
import variation_kit as vk                                        # noqa: E402

FAILS = []


def chk(tag, ok, msg=""):
    print(f"  [{'PASS' if ok else 'FAIL'}] {tag}" + (f" — {msg}" if msg else ""))
    if not ok:
        FAILS.append(tag)
    return ok


def main(run="260730_data_mini"):
    root = vk.data_root(run)
    mf_path = os.path.join(root, "manifest.json")
    if not os.path.isfile(mf_path):
        raise SystemExit(f"[check] no manifest at {mf_path}")
    mf = json.load(open(mf_path, encoding="utf-8"))
    cuts, per_scene = [], {}
    for p in sorted(glob.glob(os.path.join(root, "*", "*", "variation.json"))):
        v = json.load(open(p, encoding="utf-8"))
        per_scene[v["scene"]] = v
        for c in v["cuts"]:
            c["_dir"] = os.path.dirname(p)
            cuts.append(c)
    print("=" * 78)
    print(f"data run {run} — {len(cuts)} cuts, {len(per_scene)} scenes, "
          f"HEAD {mf.get('git_head')}")
    print("=" * 78)
    print(f"scenes: " + ", ".join(
        f"{s} ({v['split']}, class {v['ledger']['cls']})"
        for s, v in sorted(per_scene.items())))
    for r in mf.get("refused", []):
        print(f"refused: {r['scene']} x {r['cond']}")

    conds = sorted({c["cond"] for c in cuts})

    # ---------------------------------------------------------------- 1
    print("\n[1] exposure sanity — criterion C band + the diffuse/direct signature")
    band = [c for c in cuts if c.get("img")]
    chk("every cut carries a photometric measurement",
        len(band) == len(cuts), f"{len(band)}/{len(cuts)}")
    bad = [f"{c['file']} mean {c['img']['mean']}" for c in band
           if not (vk.DARK_MEAN <= c["img"]["mean"] <= vk.BLOWN_MEAN)]
    chk(f"mean luma in [{vk.DARK_MEAN:.0f}, {vk.BLOWN_MEAN:.0f}]",
        not bad, "; ".join(bad[:4]))
    badd = [f"{c['file']} dark {c['img']['dark']}" for c in band
            if c["img"]["dark"] > vk.DARK_PCT]
    chk(f"dark share <= {vk.DARK_PCT:.0f} %", not badd, "; ".join(badd[:4]))
    badc = [f"{c['file']} clip {c['img']['clip']}" for c in band
            if c["img"]["clip"] > vk.CLIP_PCT]
    chk(f"clip share <= {vk.CLIP_PCT:.1f} %", not badc, "; ".join(badc[:4]))
    # WHAT NOT TO ASSERT, and why. "A condition that is N EV darker must have a
    # lower frame mean" is physically wrong and this run proved it: sceneN1
    # shadow_band goes from ground mean 160.4 at L0 to 206.4 at L7 even though L7
    # is 0.86 EV darker in horizontal illuminance. sceneN1's ground is
    # deliberately half in cast shadow, and overcast REMOVES that shadow — which
    # raises the mean far more than the illuminance drop lowers it. The frame mean
    # also mixes in sky pixels, and an overcast sky is brighter than a clear one
    # (measured Esky 4.05 vs 0.52).
    #
    # The two signatures that ARE physically sound:
    #   (a) among conditions that still have a sun disc, the GROUND band darkens
    #       with net EV — asserted per scene, so scene albedo cancels;
    #   (b) a sunless condition must have LESS deep shadow than the clear
    #       reference — that is the direct/diffuse ratio showing up in the image,
    #       and it is the cheapest proof that the sky swap really took effect.
    from PIL import Image
    import numpy as np
    for c in band:
        a = np.asarray(Image.open(os.path.join(c["_dir"], c["file"]))
                       .convert("RGB")).astype(np.float32)
        g = 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]
        h = g.shape[0]
        c["_ground"] = float(g[int(h * 2 / 3):].mean())
        c["_sky"] = float(g[:int(h / 3)].mean())
    print("       per condition (net EV = dEV - ev_comp = how much less light "
          "reaches the ground):")
    stats = {}
    for cid in conds:
        cc = vk.CONDITIONS[cid]
        sub = [c for c in band if c["cond"] == cid]
        stats[cid] = dict(net_ev=cc["d_ev"] - cc["ev_comp"], n=len(sub),
                          mean=st.mean(c["img"]["mean"] for c in sub),
                          ground=st.mean(c["_ground"] for c in sub),
                          sky=st.mean(c["_sky"] for c in sub),
                          dark=st.mean(c["img"]["dark"] for c in sub),
                          clip=max(c["img"]["clip"] for c in sub),
                          f_dir=cc["f_dir"], sunless=cc["sunless"])
        v = stats[cid]
        print(f"       {cid} {cc['name']:16s} n={v['n']:3d} "
              f"net {v['net_ev']:+.3f} EV  f_dir {v['f_dir']:.3f}  "
              f"iso {100 * 2 ** cc['ev_comp']:6.1f}  frame {v['mean']:6.1f}  "
              f"ground {v['ground']:6.1f}  sky {v['sky']:6.1f}  "
              f"deep-shadow {v['dark']:5.2f} %")
    # (a) sun-bearing conditions, per scene, ground band, pairs >= 0.3 EV apart.
    sunny = [c for c in conds if not vk.CONDITIONS[c]["sunless"]]
    pairs, wrong = 0, []
    for sc in sorted(per_scene):
        have = [c for c in sunny
                if any(x["scene"] == sc and x["cond"] == c for x in band)]
        for a in have:
            for b in have:
                if stats[a]["net_ev"] + 0.3 > stats[b]["net_ev"]:
                    continue
                ga = st.mean(x["_ground"] for x in band
                             if x["scene"] == sc and x["cond"] == a)
                gb = st.mean(x["_ground"] for x in band
                             if x["scene"] == sc and x["cond"] == b)
                pairs += 1
                if ga <= gb:
                    wrong.append(f"{sc} {a}({ga:.1f}) !> {b}({gb:.1f})")
    chk(f"sun-bearing: ground darkens with net EV, per scene "
        f"({pairs} pairs >= 0.3 EV apart)", pairs > 0 and not wrong,
        "; ".join(wrong) if wrong else "no comparable pair" if not pairs else "")
    # (b) sunless conditions kill the deep shadow.
    ref_dark = {sc: st.mean(x["img"]["dark"] for x in band
                            if x["scene"] == sc and x["cond"] == "L0")
                for sc in per_scene
                if any(x["scene"] == sc and x["cond"] == "L0" for x in band)}
    bad2, n2 = [], 0
    for cid in conds:
        if not vk.CONDITIONS[cid]["sunless"]:
            continue
        for sc, rd in ref_dark.items():
            sub = [x["img"]["dark"] for x in band
                   if x["scene"] == sc and x["cond"] == cid]
            if not sub:
                continue
            n2 += 1
            if st.mean(sub) >= rd:
                bad2.append(f"{sc} {cid} dark {st.mean(sub):.2f} >= L0 {rd:.2f}")
    chk(f"sunless: less deep shadow than the L0 reference ({n2} scene-pairs)",
        n2 > 0 and not bad2, "; ".join(bad2))

    # ---------------------------------------------------------------- 2
    print("\n[2] azimuth ledger (SP-2 measured) respected")
    viol = []
    for c in cuts:
        s, cid = c["scene"], c["cond"]
        allow = vk.daz_allow(s, cid, role=vk.ROLE_DATA)
        floor = (0.0 if (vk.ledger(s)["az_free"] or vk.CONDITIONS[cid]["sunless"])
                 else vk.CONDITIONS[cid]["min_abs_daz"])
        a = abs(c["light"]["d_az"])
        if a > allow + 1e-6 or a < floor - 1e-6:
            viol.append(f"{c['file']} |daz| {a:.1f} not in [{floor:.1f},{allow:.1f}]")
    chk("every d_az inside its allowance and above its floor", not viol,
        "; ".join(viol[:4]))
    for s in sorted(per_scene):
        L = vk.ledger(s)
        for cid in sorted({c["cond"] for c in cuts if c["scene"] == s}):
            a = [abs(c["light"]["d_az"]) for c in cuts
                 if c["scene"] == s and c["cond"] == cid]
            print(f"       {s:9s} {cid} |daz| {min(a):5.1f}-{max(a):5.1f} "
                  f"(allow {vk.daz_allow(s, cid, vk.ROLE_DATA):4.0f}, "
                  f"floor {vk.CONDITIONS[cid]['min_abs_daz']:4.1f}, "
                  f"class {L['cls']})")
    # The rotz that goes with the sky must be the sky's own, not the scene's.
    rz = {c["cond"]: c["light"]["hdri_sun_rotz_offset"] for c in cuts}
    chk("each condition carries its own hdri_sun_rotz_offset",
        all(abs(rz[k] - vk.CONDITIONS[k]["hdri_sun_rotz_offset"]) < 1e-6
            for k in rz), str(rz))
    chk("sun elevation tracks the sky's measured elevation (no double shadow)",
        all(abs(c["light"]["sun_elev"]
                - vk.CONDITIONS[c["cond"]]["sun_elev"]) < 1e-6 for c in cuts))

    # ---------------------------------------------------------------- 3
    print("\n[3] camera placement — ground-relative height, nothing buried")
    gb = [c for c in cuts if c["stage1"].get("ground_below") is not None]
    chk("ground found under every camera", len(gb) == len(cuts),
        f"{len(gb)}/{len(cuts)}")
    err = [abs(c["stage1"]["ground_below"] - c["cam"]["h_rel"]) for c in gb]
    chk("ground_below == sampled h_rel (the CAM-3 fix actually landed)",
        max(err) < 0.02 if err else False,
        f"worst |err| {max(err):.4f} m over {len(err)} cuts" if err else "")
    buried = [c["file"] for c in cuts if c["stage1"]["buried"]]
    chk("no camera inside or within 0.15 m of geometry", not buried,
        f"{len(buried)}: {buried[:3]}")
    closed = [c["file"] for c in cuts if c["stage1"]["closed_in"]]
    print(f"       stage-1 flags: buried {len(buried)} · closed_in "
          f"{len(closed)} · offground "
          f"{sum(1 for c in cuts if c['stage1']['offground'])} "
          f"(advisory only — SP-3 measured 1 firing in 600 and it was wrong)")
    nr = min(c["stage1"]["nearest_solid"] for c in cuts)
    chk("nearest solid to any eye >= 0.15 m", nr >= vk.BURY_CLEAR,
        f"min {nr:.3f} m")
    fb = [c for c in cuts if c.get("frame_budget")
          and not c["frame_budget"].get("error")]
    if fb:
        hard = sum(1 for c in fb if c["frame_budget"]["hard_fail"])
        soft = sum(1 for c in fb if c["frame_budget"]["soft_fail"])
        print(f"       frame_budget advisory on {len(fb)} cuts: hard-gate flags "
              f"{hard}, fill-target flags {soft} (recorded, not enforced)")
    else:
        print(f"       frame_budget advisory unavailable on "
              f"{len(cuts) - len(fb)} cuts "
              f"({(cuts[0].get('frame_budget') or {}).get('error', 'no plan')})")
    tiers = {c["cam"]["tier"] for c in cuts}
    chk("camera tier recorded per cut", tiers and None not in tiers, str(tiers))
    for k, (lo, hi) in (("h_rel", (0.25, 1.90)), ("pitch", (-20.0, -2.0)),
                        ("roll", (-5.0, 5.0)), ("hfov", (58.0, 66.0)),
                        ("d", (1.2, 12.0))):
        v = [c["cam"][k] for c in cuts]
        chk(f"{k} within the sampler's truncation [{lo}, {hi}]",
            lo - 1e-6 <= min(v) and max(v) <= hi + 1e-6,
            f"{min(v):.3f} .. {max(v):.3f}")
    foc = max(abs(c["cam"]["focal"] - vk.focal_for_hfov(c["cam"]["hfov"]))
              for c in cuts)
    chk("focalLength consistent with hFOV (SP-7 formula)", foc < 1e-4,
        f"worst {foc:.2e}")

    # ---------------------------------------------------------------- 4
    print("\n[4] file and manifest integrity")
    miss = [c["file"] for c in cuts
            if not os.path.isfile(os.path.join(c["_dir"], c["file"]))]
    chk("every manifest record has a file on disk", not miss,
        f"{len(miss)}: {miss[:3]}")
    on_disk = set()
    for d in {c["_dir"] for c in cuts}:
        on_disk |= {os.path.join(d, f) for f in os.listdir(d)
                    if f.endswith(".png")}
    chk("no orphan PNG outside the manifest",
        len(on_disk) == len(cuts), f"{len(on_disk)} files / {len(cuts)} records")
    md5 = {}
    for c in cuts:
        p = os.path.join(c["_dir"], c["file"])
        if os.path.isfile(p):
            md5.setdefault(hashlib.md5(open(p, "rb").read()).hexdigest(),
                           []).append(c["file"])
    dup = {k: v for k, v in md5.items() if len(v) > 1}
    chk("every cut is content-unique (no stale or duplicated frame)", not dup,
        str(list(dup.values())[:2]))
    chk("all captures reported ok", all(c["ok"] for c in cuts),
        f"{sum(1 for c in cuts if not c['ok'])} not ok")
    try:
        from PIL import Image
        sizes = {Image.open(os.path.join(c["_dir"], c["file"])).size
                 for c in cuts}
        chk("every frame is 1920x1080", sizes == {(1920, 1080)}, str(sizes))
    except Exception as e:
        chk("PNG decode", False, str(e))
    pat_bad = [c["file"] for c in cuts
               if c["file"] != f"{c['cond']}__s{c['seed']}__{c['idx']:04d}.png"]
    chk("filenames follow <cond>__s<seed>__<nnnn>.png", not pat_bad,
        str(pat_bad[:3]))
    # The whole point of D1.
    leak = []
    for s in per_scene:
        for d in glob.glob(os.path.join(REPO, "look_check", s, "*")):
            for f in glob.glob(os.path.join(d, "*.png")):
                if os.path.basename(f).startswith(tuple(vk.COND_IDS[1:])):
                    leak.append(f)
    chk("nothing written into look_check/<scene>/ (D1 tree separation)",
        not leak, str(leak[:3]))
    reg_seen = glob.glob(os.path.join(REPO, "look_check", "scene*"))
    chk("the data tree is outside regression_check's only glob "
        "(look_check/scene*)",
        not any(os.path.realpath(root).startswith(os.path.realpath(p))
                for p in reg_seen),
        os.path.relpath(root, REPO))

    # ---------------------------------------------------------------- 5
    print("\n[5] throughput vs SP-3")
    inv = mf.get("invocations", [])
    print(f"       {mf.get('total_cuts')} cuts over {len(inv)} invocation(s), "
          f"{mf.get('total_sec')} s wall total including {len(per_scene)} boots"
          f" — a run-level s/cut is not quoted, because dividing a resumed "
          f"pass's wall time by the cumulative cut count is meaningless")
    for s, v in sorted(per_scene.items()):
        print(f"       {s:9s} {v['n']:3d} cuts  {v['sec']:7.1f} s  "
              f"{v['sec_per_cut']:.2f} s/cut  r_reject {v['r_reject']}")
    inner = [v["sec_per_cut"] for v in per_scene.values()]
    chk("in-scene s/cut within 2x of SP-3's 2.87 s",
        max(inner) < 2 * vk.T_CUT_DATA,
        f"{min(inner):.2f}-{max(inner):.2f} vs {vk.T_CUT_DATA}")
    rr = [v["r_reject"] for v in per_scene.values()]
    print(f"       r_reject per scene {rr} "
          f"(flat_near intentionally OFF on the data channel — SP-3 rider 2)")

    print("\n" + "=" * 78)
    print(("DATA RUN CHECK PASS" if not FAILS
           else f"DATA RUN CHECK FAIL — {len(FAILS)}: {FAILS}"))
    print("=" * 78)
    return 0 if not FAILS else 1


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
