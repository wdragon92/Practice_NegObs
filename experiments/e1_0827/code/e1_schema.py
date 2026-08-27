# -*- coding: utf-8 -*-
"""e1_schema.py -- the brief v6 §5 record, its canonical JSON dump, the csv
mirror and a validator.

Nothing in this module knows how a number was computed; it only fixes what a
record IS and how it is written, so that "same input -> byte-identical json"
(brief §4 Phase 1 통과수치) is a property of the schema layer alone.

Field list is §5 verbatim. Two documented readings are flagged as ❓ in
reports/P0_CODE_SKELETON.md:
  * `notes` is a dict {"messages": [str], "diag": {...}} rather than a bare
    string, so per-frame counters survive into the record instead of being lost.
  * `polyline_px` is a LIST OF VISIBLE RUNS (list of list of [x, y]); one edge
    instance can be cut into several on-screen runs by an occluder, and a single
    flat list would silently bridge the gap.
"""

import csv
import json
import math
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

import e1_const as C

SCHEMA_VERSION = "e1-record-v1"
TIER_NOW_VALUES = ("NEG", "H_cand", "VE_raw")
DOMAIN_VALUES = ("stair", "warehouse")

# §5: "파일 분리: 계단 = edge_manifest_v1.json / 창고 = vth_manifest_v1.json.
# 창고 프레임은 계단 corpus 에 편입하지 않는다." The mapping lives here so no
# caller can spell the wrong file name for a domain.
MANIFEST_STEM = {"stair": "edge_manifest_v1", "warehouse": "vth_manifest_v1"}


# --------------------------------------------------------------------------- #
# dataclasses
# --------------------------------------------------------------------------- #
@dataclass
class DistM:
    """camera -> this edge instance, in metres (§5)."""
    min: Optional[float] = None
    median: Optional[float] = None


@dataclass
class Occluder:
    """§2 rule 3 result.

    flag  : True  = an EXTERNAL prim blocks part of this instance -> H_cand
            False = nothing blocks it, or only ground/stair/hazard geometry does
                    (self-occlusion / brink -- that is the definition of E)
            None  = UNRESOLVED. No prim-id sidecar for this frame, or the
                    blocking prim matches no approved rule. Never guessed.
    prim  : the blocking prim path (or 'unknown' / 'no-seg-sidecar')
    occl_frac : fraction of this instance blocked by an EXTERNAL prim, 0..1.
            None whenever flag is None.
    """
    flag: Optional[bool] = None
    prim: str = "unknown"
    occl_frac: Optional[float] = None


@dataclass
class SrcDisagreePx:
    """route (a) vs route (b) deviation in pixels (§5)."""
    mean: Optional[float] = None
    median: Optional[float] = None
    p90: Optional[float] = None


@dataclass
class EdgeRecord:
    edge_id: str
    polyline_px: List[List[List[float]]] = field(default_factory=list)
    pts_3d: List[List[float]] = field(default_factory=list)
    dist_m: DistM = field(default_factory=DistM)
    int_area_px: int = 0
    int_h_px: int = 0
    int_w_px: int = 0
    int_mask_path: Optional[str] = None
    occluder: Occluder = field(default_factory=Occluder)
    src_disagree_px: SrcDisagreePx = field(default_factory=SrcDisagreePx)


@dataclass
class FrameRecord:
    frame_id: str
    pose_id: str
    scene_id: str
    world_id: str
    domain: str
    rgb_path: str
    depth_path: str
    tier_now: str
    tier_final: str = ""
    notes: Dict[str, Any] = field(default_factory=lambda: {"messages": [], "diag": {}})
    edges: List[EdgeRecord] = field(default_factory=list)


# --------------------------------------------------------------------------- #
# tier_now derivation -- §5 verbatim, the ONLY place it is spelled
# --------------------------------------------------------------------------- #
def derive_tier_now(edges: List[EdgeRecord]) -> str:
    """§5: edges[] empty -> NEG; any occluder.flag -> H_cand; else VE_raw.

    `flag is None` (unresolved) is NOT `flag` -- an unresolved frame does not
    become H_cand by default. It stays VE_raw and is listed for 결재 (❓B-4).
    """
    if not edges:
        return "NEG"
    if any(e.occluder.flag is True for e in edges):
        return "H_cand"
    return "VE_raw"


# --------------------------------------------------------------------------- #
# canonical dump
# --------------------------------------------------------------------------- #
def _round(obj):
    """Recursively fix every float to JSON_DECIMALS places.

    -0.0 is normalised to 0.0 and non-finite floats to None: both are ways the
    same computation can print two different bytes on two runs.
    """
    nd = C.JSON_DECIMALS
    if isinstance(obj, float):
        if not math.isfinite(obj):
            return None
        r = round(obj, nd)
        return 0.0 if r == 0 else r
    if isinstance(obj, bool) or obj is None or isinstance(obj, (int, str)):
        return obj
    if isinstance(obj, dict):
        return {k: _round(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_round(v) for v in obj]
    raise TypeError("e1_schema: cannot serialise %r" % type(obj))


def record_to_dict(rec: FrameRecord) -> dict:
    return _round(asdict(rec))


def manifest_dict(records: List[FrameRecord]) -> dict:
    """The file wrapper. No timestamps, no host names, no paths outside the repo
    -- anything that changes between two runs of the same input would break the
    byte-identity check."""
    return {
        "schema_version": SCHEMA_VERSION,
        "const_fingerprint": C.fingerprint(),
        "constants": _round(C.as_dict()),
        "frames": [record_to_dict(r) for r in
                   sorted(records, key=lambda r: r.frame_id)],
    }


def dump_json(records: List[FrameRecord], path: str) -> str:
    blob = json.dumps(manifest_dict(records), sort_keys=C.value("JSON_SORT_KEYS"),
                      ensure_ascii=False, indent=1) + "\n"
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(blob)
    return blob


CSV_COLUMNS = [
    "frame_id", "pose_id", "scene_id", "world_id", "domain", "tier_now",
    "tier_final", "rgb_path", "depth_path", "n_edges", "edge_id",
    "n_polyline_runs", "n_polyline_pts", "n_pts_3d", "dist_min_m",
    "dist_median_m", "int_area_px", "int_h_px", "int_w_px", "int_mask_path",
    "occl_flag", "occl_prim", "occl_frac", "disagree_mean_px",
    "disagree_median_px", "disagree_p90_px",
]


def dump_csv(records: List[FrameRecord], path: str) -> None:
    """csv mirror: 1 edge = 1 row. A frame with no edges (NEG) still gets one
    row, with the edge columns empty -- otherwise NEG frames vanish from the
    mirror and the two files stop agreeing on the population."""
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(CSV_COLUMNS)
        for rec in sorted(records, key=lambda r: r.frame_id):
            base = [rec.frame_id, rec.pose_id, rec.scene_id, rec.world_id,
                    rec.domain, rec.tier_now, rec.tier_final, rec.rgb_path,
                    rec.depth_path, len(rec.edges)]
            if not rec.edges:
                w.writerow(base + [""] * (len(CSV_COLUMNS) - len(base)))
                continue
            for e in rec.edges:
                d = _round(asdict(e))
                w.writerow(base + [
                    d["edge_id"], len(d["polyline_px"]),
                    sum(len(run) for run in d["polyline_px"]), len(d["pts_3d"]),
                    d["dist_m"]["min"], d["dist_m"]["median"],
                    d["int_area_px"], d["int_h_px"], d["int_w_px"],
                    d["int_mask_path"] or "",
                    "" if d["occluder"]["flag"] is None else d["occluder"]["flag"],
                    d["occluder"]["prim"],
                    "" if d["occluder"]["occl_frac"] is None else d["occluder"]["occl_frac"],
                    d["src_disagree_px"]["mean"], d["src_disagree_px"]["median"],
                    d["src_disagree_px"]["p90"],
                ])


# --------------------------------------------------------------------------- #
# validator
# --------------------------------------------------------------------------- #
def validate(rec: FrameRecord) -> List[str]:
    """Returns a list of problems; empty list = valid. Never raises, never
    repairs -- a bad record is reported, not fixed (brief §3 '침묵 수리 금지')."""
    p = []
    for f in ("frame_id", "pose_id", "scene_id", "world_id", "rgb_path", "depth_path"):
        if not getattr(rec, f):
            p.append("empty required field: %s" % f)
    if rec.domain not in DOMAIN_VALUES:
        p.append("domain %r not in %s" % (rec.domain, DOMAIN_VALUES))
    if rec.tier_now not in TIER_NOW_VALUES:
        p.append("tier_now %r not in %s" % (rec.tier_now, TIER_NOW_VALUES))
    if rec.tier_now != derive_tier_now(rec.edges):
        p.append("tier_now %r contradicts §5 derivation %r"
                 % (rec.tier_now, derive_tier_now(rec.edges)))
    if rec.tier_final != "":
        p.append("tier_final must stay empty until G3 (§5)")
    if not isinstance(rec.notes, dict) or "messages" not in rec.notes:
        p.append("notes must be a dict with a 'messages' key")
    ids = [e.edge_id for e in rec.edges]
    if len(set(ids)) != len(ids):
        p.append("duplicate edge_id in frame")
    for e in rec.edges:
        if not e.edge_id:
            p.append("empty edge_id")
        if len(e.pts_3d) == 0:
            p.append("%s: pts_3d empty" % e.edge_id)
        for pt in e.pts_3d[:1]:
            if len(pt) != 3:
                p.append("%s: pts_3d entries must be [x,y,z]" % e.edge_id)
        for run in e.polyline_px:
            for pt in run[:1]:
                if len(pt) != 2:
                    p.append("%s: polyline_px entries must be [x,y]" % e.edge_id)
        if e.int_area_px < 0 or e.int_h_px < 0 or e.int_w_px < 0:
            p.append("%s: negative interior px" % e.edge_id)
        if e.int_area_px == 0 and e.int_mask_path:
            p.append("%s: int_mask_path set but int_area_px == 0 (§5)" % e.edge_id)
        if e.int_area_px > 0 and not e.int_mask_path:
            p.append("%s: int_area_px > 0 but no int_mask_path (§5)" % e.edge_id)
        of = e.occluder.occl_frac
        if e.occluder.flag is None and of is not None:
            p.append("%s: occl_frac given while flag is unresolved" % e.edge_id)
        if of is not None and not (0.0 <= of <= 1.0):
            p.append("%s: occl_frac %r outside [0,1]" % (e.edge_id, of))
    return p
