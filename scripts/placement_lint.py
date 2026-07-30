#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""placement_lint.py — geometric legality of props (LINT-1 .. LINT-10).

W3 execution spec `Docs/briefs/w3_execution_spec_v1.md` §10.4 defines ten checks over the
placement of street furniture, street trees and ground decals. This is their implementation.
The rule table itself lives in `Docs/briefs/placement_rules_v1.yaml` — thresholds are data,
not code, so a spec change is a YAML diff.

WHAT IT PROVES
  The abolition batch of §1.2 (jitter) and the species table of §1.3 are only permanent if
  something re-derives them from the assembled scene on every commit. `geom_invariance_check`
  answers "did the material layer touch geometry"; this tool answers "is the geometry legal".
  Spec §5.3 makes T1 a dependency edge of *every* scene commit for exactly that reason.

HOW IT RUNS — GPU 0
  It **imports** `scripts/geom_invariance_check.py` and drives its stub harness
  (`run_arm` / `_scene_files`). It never edits that file (spec §4.1 ownership) and never
  re-implements the stub: the fake-USD recorder is the single source of prim truth for both
  tools. One arm is assembled, `NEGOBS_LOOK_MTL=1 NEGOBS_LOOK_GEO=1` — the shipped
  configuration — and every prim's world frame is composed from the recorded xform ops.

  Consequence worth knowing: with `LOOK_GEO=1` and the vegetation assets present, `build_tree`
  takes the **asset** route, so species are readable from the bound USD reference. Without the
  assets it falls back to procedural blobs and the species checks report `nodata`. The linter
  prints which route it measured.

WHAT IT READS FROM A SCENE
  An additive, geometry-free declaration block (spec §10.4):

      PLACEMENT = dict(
          walk_edges = [((x0,y0),(x1,y1)), ...],
          kerb_lines = [((x0,y0),(x1,y1)), ...],
          anchors    = {"planterA": dict(face_bearing_deg=0.0, props=["Bench_.*"]), ...},
          routes     = {"verge_S": dict(pts=[...], species="oak_pin", pitch_m=7.0), ...},
      )

  It is read **statically** (module-level literal). A rule whose datum is undeclared does not
  silently pass: it emits a `nodata` row naming what the scene owes. Where a safe surrogate
  exists the linter may infer one, but an inferred finding is always downgraded to WARN and
  tagged `[inferred]` — an inferred datum may never fail a build.

EVIDENCE GATES (spec §1.8)
  "Prepare" = the check exists in warn mode with the scene value untouched. "Enforce" = the
  check is hard. LINT-9's setback band comes from T2's archetype panels and does not exist, so
  LINT-9 is warn-only behind `gates.LINT-9` and `--enforce-lint9` refuses to invent a band.

USAGE
    python3 scripts/placement_lint.py --scenes all
    python3 scripts/placement_lint.py --scenes scene06,scene11 --only LINT-6,LINT-8
    python3 scripts/placement_lint.py --scenes all --format json --json /tmp/lint.json
    python3 scripts/placement_lint.py --scenes all --require-placement   # WINDOW 3 posture

EXIT CODES
    0  clean          — no ERROR-severity finding
    1  violation      — at least one ERROR (or any WARN with --warn-as-error)
    2  harness error  — scene assembly failed, rules file unusable, or a gate was asked to
                        enforce a threshold that does not exist yet
"""

import argparse
import ast
import json
import math
import os
import re
import sys
from collections import Counter, OrderedDict, defaultdict

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(REPO, "scripts")
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)

DEFAULT_RULES = os.path.join("Docs", "briefs", "placement_rules_v1.yaml")

EXIT_OK, EXIT_VIOLATION, EXIT_HARNESS = 0, 1, 2

SEV_ERROR, SEV_WARN, SEV_INFO, SEV_BLOCKED = "ERROR", "WARN", "INFO", "BLOCKED"
_SEV_ORDER = {SEV_ERROR: 0, SEV_WARN: 1, SEV_BLOCKED: 2, SEV_INFO: 3}


class HarnessError(RuntimeError):
    """Anything that makes a verdict impossible rather than negative (exit 2)."""


# ===========================================================================
# [1] Findings
# ===========================================================================
class Finding(object):
    """One reported row. `basis` is the evidence tag chain, never omitted."""

    __slots__ = ("check", "severity", "scene", "subject", "measured",
                 "expected", "detail", "basis", "tags")

    def __init__(self, check, severity, scene, subject, measured="", expected="",
                 detail="", basis="", tags=()):
        self.check = check
        self.severity = severity
        self.scene = scene
        self.subject = subject
        self.measured = measured
        self.expected = expected
        self.detail = detail
        self.basis = basis
        self.tags = tuple(tags)

    def as_dict(self):
        return OrderedDict(check=self.check, severity=self.severity, scene=self.scene,
                           subject=self.subject, measured=self.measured,
                           expected=self.expected, detail=self.detail,
                           basis=self.basis, tags=list(self.tags))

    def sort_key(self):
        return (_SEV_ORDER.get(self.severity, 9), self.check, self.scene, self.subject)


# ===========================================================================
# [2] Rules
# ===========================================================================
def load_rules(path):
    try:
        import yaml
    except ImportError as e:                                  # pragma: no cover
        raise HarnessError("PyYAML is required to read the rule table: %s" % e)
    if not os.path.isabs(path):
        path = os.path.join(REPO, path)
    if not os.path.isfile(path):
        raise HarnessError("rule table not found: %s" % path)
    with open(path, "r", encoding="utf-8") as fh:
        rules = yaml.safe_load(fh)
    if not isinstance(rules, dict) or "checks" not in rules or "props" not in rules:
        raise HarnessError("rule table is not a placement_rules document: %s" % path)
    rules["_path"] = path
    return rules


def compiled_suppressions(rules):
    """`do_not_touch` entries that carry a `suppress_checks` list become active filters.

    Suppression is never silent: `run()` prints one INFO row per (check, scene, id) stating how
    many findings were withheld and quoting the rule, so a reader can always see what the linter
    decided not to say.
    """
    out = []
    for entry in (rules.get("do_not_touch") or []):
        checks = entry.get("suppress_checks")
        if not checks:
            continue
        out.append(dict(id=entry.get("id", "DNT-?"),
                        scope=entry.get("scope"),
                        prefix=entry.get("path_prefix"),
                        checks=set(checks),
                        rule=(entry.get("rule") or "").strip()))
    return out


def compiled_props(rules):
    """Compile the prop taxonomy once. Returns (suffix_rules, segment_rules, exempt_res)."""
    props = rules["props"]
    order = props.get("order") or [k for k in props if isinstance(props[k], dict)]
    suffix_rules, segment_rules = [], []
    for cls in order:
        spec = props.get(cls)
        if not isinstance(spec, dict) or "pattern" not in spec:
            continue
        rx = re.compile(spec["pattern"])
        if spec.get("mode") == "suffix":
            suffix_rules.append((cls, rx, spec))
        else:
            segment_rules.append((cls, rx, spec))
    exempt = [re.compile(p) for p in (props.get("exempt_suffixes") or [])]
    return suffix_rules, segment_rules, exempt


# ===========================================================================
# [3] Prim model — parse the stub harness inventory and compose world frames
# ===========================================================================
class Frame(object):
    """A planar similarity: p_world = s * R(theta) * p_local + t.

    Only translate / rotate-Z / scale ops move a prop in plan. RX / RY / orient /
    transform ops are recorded as `nonplanar` so a finding can say the frame was not
    fully readable instead of quietly reporting a wrong bearing.
    """

    __slots__ = ("sx", "sy", "theta", "tx", "ty", "nonplanar")

    def __init__(self, sx=1.0, sy=1.0, theta=0.0, tx=0.0, ty=0.0, nonplanar=False):
        self.sx, self.sy = sx, sy
        self.theta, self.tx, self.ty = theta, tx, ty
        self.nonplanar = nonplanar

    def copy(self):
        return Frame(self.sx, self.sy, self.theta, self.tx, self.ty, self.nonplanar)

    def then(self, kind, val):
        """Compose this frame with a child op: F_new(p) = F_old(op(p))."""
        f = self.copy()
        if kind == "T":
            vx, vy = _xy(val)
            c, s = math.cos(math.radians(f.theta)), math.sin(math.radians(f.theta))
            f.tx += f.sx * (c * vx - s * vy)
            f.ty += f.sy * (s * vx + c * vy)
        elif kind == "RZ":
            f.theta += _scalar(val)
        elif kind == "S":
            kx, ky = _xy(val, default=1.0)
            f.sx *= kx
            f.sy *= ky
        elif kind in ("RX", "RY", "RXYZ", "Q", "M"):
            # A tilt does not change the plan bearing of an axis-aligned prop, but a general
            # rotation or matrix does. Flag rather than guess.
            if kind != "RX" and kind != "RY":
                f.nonplanar = True
        return f


def _scalar(v):
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, (tuple, list)) and v:
        return float(v[0])
    return 0.0


def _xy(v, default=0.0):
    if isinstance(v, (tuple, list)):
        x = float(v[0]) if len(v) > 0 and isinstance(v[0], (int, float)) else default
        y = float(v[1]) if len(v) > 1 and isinstance(v[1], (int, float)) else default
        return x, y
    if isinstance(v, (int, float)):
        return float(v), float(v)
    return default, default


class Prim(object):
    __slots__ = ("path", "type", "ops", "attrs", "refs", "_world")

    def __init__(self, path, type_, ops, attrs, refs):
        self.path = path
        self.type = type_
        self.ops = ops
        self.attrs = attrs
        self.refs = refs
        self._world = None

    @property
    def name(self):
        return self.path.rsplit("/", 1)[-1]


def _parse_value(text):
    """Re-read the stub's `_num` rendering: a scalar, a tuple, or an opaque token."""
    t = text.strip()
    if not t:
        return None
    if t.startswith("("):
        try:
            return ast.literal_eval(t)
        except (ValueError, SyntaxError):
            return t
    try:
        return float(t)
    except ValueError:
        if t in ("True", "False"):
            return t == "True"
        return t


def parse_inventory(rows):
    """`path|type|ops|attrs|refs` (geom_invariance_check.inventory) -> {path: Prim}."""
    prims = {}
    for row in rows:
        parts = row.split("|")
        if len(parts) < 5:
            continue
        path, typ, ops_s, attrs_s, refs_s = parts[0], parts[1], parts[2], parts[3], parts[4]
        ops = []
        if ops_s:
            for kv in ops_s.split(";"):
                if "=" not in kv:
                    continue
                k, v = kv.split("=", 1)
                ops.append((k, _parse_value(v)))
        attrs = {}
        if attrs_s:
            for kv in attrs_s.split(";"):
                if "=" not in kv:
                    continue
                k, v = kv.split("=", 1)
                attrs[k] = _parse_value(v)
        refs = [r for r in refs_s.split(",") if r]
        prims[path] = Prim(path, typ, ops, attrs, refs)
    return prims


def world_frame(prims, path, _depth=0):
    """World frame of `path`, composing every recorded ancestor. Undefined ancestors are
    identity — USD auto-creates them and the stub only records explicit Defines."""
    if _depth > 64:                                            # pragma: no cover
        return Frame()
    prim = prims.get(path)
    if prim is not None and prim._world is not None:
        return prim._world
    parent = path.rsplit("/", 1)[0]
    base = Frame() if ("/" not in path or not parent) else world_frame(prims, parent, _depth + 1)
    f = base.copy()
    if prim is not None:
        for kind, val in prim.ops:
            f = f.then(kind, val)
        prim._world = f
    return f


def norm_deg(a):
    """Fold an angle into [0, 360)."""
    return a % 360.0


def ang_diff(a, b):
    """Smallest absolute difference between two bearings, degrees."""
    d = abs(norm_deg(a) - norm_deg(b)) % 360.0
    return min(d, 360.0 - d)


# ===========================================================================
# [4] Prop instances
# ===========================================================================
class PropInstance(object):
    __slots__ = ("cls", "root", "prims", "spec")

    def __init__(self, cls, root, spec):
        self.cls = cls
        self.root = root
        self.prims = []
        self.spec = spec

    @property
    def name(self):
        return self.root.rsplit("/", 1)[-1]

    @property
    def label(self):
        """Reader-facing identity. A tree's instance root is the `<prefix>/Veg` prim, which is a
        useless name on its own — report the prefix that names the planting."""
        if self.cls in ("tree", "shrub"):
            return self.root.rsplit("/", 1)[0] + "  [%s]" % self.cls
        return self.root

    @property
    def short(self):
        if self.cls in ("tree", "shrub"):
            return self.root.rsplit("/", 1)[0].rsplit("/", 1)[-1]
        return self.root.rsplit("/", 1)[-1]


def scene_root_of(path):
    """`/World/Scene06/...` -> `/World/Scene06`. Batch1 scenes use their own Scene number,
    so the root is taken from the path, never from the file name."""
    seg = path.split("/")
    return "/".join(seg[:3]) if len(seg) >= 3 else path


def classify(prims, suffix_rules, segment_rules, exempt_res):
    """Group prims into prop instances.

    Resolution order: suffix rules first (a tree lives *inside* a planter, so `/Veg` must win
    over the enclosing `Planter_A`), then the shallowest matching path segment.
    """
    instances = OrderedDict()
    owner = {}
    near_miss = []

    def instance(cls, root, spec):
        key = (cls, root)
        if key not in instances:
            instances[key] = PropInstance(cls, root, spec)
        return instances[key]

    for path in sorted(prims):
        matched = None
        for cls, rx, spec in suffix_rules:
            m = rx.search(path)
            if not m:
                continue
            if spec.get("require_child_ref"):
                child = spec.get("species_from", "<self>/Asset").replace("<self>", path)
                cp = prims.get(child)
                if cp is None or not cp.refs:
                    near_miss.append((path, cls, "no bound USD reference at %s" % child))
                    continue
            matched = (cls, path, spec)
            break
        if matched is None:
            sroot = scene_root_of(path)
            tail = path[len(sroot):].strip("/")
            if tail:
                segs = tail.split("/")
                for i, seg in enumerate(segs):
                    hit = None
                    for cls, rx, spec in segment_rules:
                        if rx.match(seg):
                            hit = (cls, spec)
                            break
                    if hit:
                        cls, spec = hit
                        # `group_regex` collapses prims that a builder emits as flat siblings of
                        # ONE physical object (a pallet stack's Bot/S0/S1/S2/Top, a bag layer's
                        # four sacks). Without it a single authored yaw is reported five times.
                        name = seg
                        grx = spec.get("group_regex")
                        if grx:
                            gm = re.match(grx, seg)
                            if gm:
                                name = gm.group("key") if "key" in (gm.groupdict() or {}) \
                                    else gm.group(0)
                        root = "/".join([sroot] + segs[:i] + [name])
                        matched = (cls, root, spec)
                        break
        if matched is None:
            continue
        cls, root, spec = matched
        inst = instance(cls, root, spec)
        owner[path] = inst

    # Membership comes straight from the ownership map: the segment scan already assigns every
    # descendant (Bench_0/Seat resolves through the `Bench_0` segment), so no prefix re-scan is
    # needed — and a virtual group root that owns no prim of its own still collects its members.
    for path in sorted(prims):
        inst = owner.get(path)
        if inst is not None:
            inst.prims.append(prims[path])

    return instances, near_miss, exempt_res


def is_exempt(path, root, exempt_res):
    tail = path[len(root):] if path.startswith(root) else path
    for rx in exempt_res:
        if rx.search(path) or (tail and rx.search(tail)):
            return True
    return False


def instance_bearings(inst, prims, exempt_res, tol_zero):
    """Distinct plan bearings carried by an instance, with the exempt sub-trees removed."""
    out = OrderedDict()
    for p in inst.prims:
        if p.path != inst.root and is_exempt(p.path, inst.root, exempt_res):
            continue
        f = world_frame(prims, p.path)
        key = round(norm_deg(f.theta), 3)
        if key not in out:
            out[key] = [p.path, f.nonplanar]
    return out


def instance_xy(inst, prims):
    """Representative plan position: the instance root frame if it carries one, else the mean
    of its member translations."""
    f = world_frame(prims, inst.root)
    if any(k == "T" for k, _ in prims[inst.root].ops) if inst.root in prims else False:
        return f.tx, f.ty
    xs, ys = [], []
    for p in inst.prims:
        wf = world_frame(prims, p.path)
        xs.append(wf.tx)
        ys.append(wf.ty)
    if not xs:
        return f.tx, f.ty
    return sum(xs) / len(xs), sum(ys) / len(ys)


# ===========================================================================
# [5] Geometry helpers
# ===========================================================================
def seg_distance(px, py, seg):
    (x0, y0), (x1, y1) = seg
    dx, dy = x1 - x0, y1 - y0
    L2 = dx * dx + dy * dy
    if L2 <= 1e-12:
        return math.hypot(px - x0, py - y0)
    t = max(0.0, min(1.0, ((px - x0) * dx + (py - y0) * dy) / L2))
    return math.hypot(px - (x0 + t * dx), py - (y0 + t * dy))


def polyline_distance(px, py, lines):
    best, which = float("inf"), None
    for i, seg in enumerate(lines):
        d = seg_distance(px, py, seg)
        if d < best:
            best, which = d, i
    return best, which


def seg_bearing(seg):
    (x0, y0), (x1, y1) = seg
    return norm_deg(math.degrees(math.atan2(y1 - y0, x1 - x0)))


def collinear_runs(points, tol, min_n):
    """Maximal sets of >= min_n points lying within `tol` of a common line.

    Points are (key, x, y). Returns a list of runs ordered along the line direction.
    Used only when the scene declares no route — findings from it are always WARN.
    """
    n = len(points)
    if n < min_n:
        return []
    found = {}
    for i in range(n):
        for j in range(i + 1, n):
            _, xi, yi = points[i]
            _, xj, yj = points[j]
            dx, dy = xj - xi, yj - yi
            L = math.hypot(dx, dy)
            if L < 1e-9:
                continue
            ux, uy = dx / L, dy / L
            members = []
            for k, (key, x, y) in enumerate(points):
                perp = abs(-uy * (x - xi) + ux * (y - yi))
                if perp <= tol:
                    members.append((ux * (x - xi) + uy * (y - yi), key, x, y))
            if len(members) < min_n:
                continue
            members.sort()
            sig = tuple(m[1] for m in members)
            if sig not in found:
                found[sig] = [(m[1], m[2], m[3]) for m in members]
    # Drop runs fully contained in a larger run.
    sigs = sorted(found, key=lambda s: -len(s))
    keep = []
    for s in sigs:
        if any(set(s) < set(k) for k in keep):
            continue
        keep.append(s)
    return [found[s] for s in keep]


def spacings(run):
    out = []
    for a, b in zip(run, run[1:]):
        out.append(math.hypot(b[1] - a[1], b[2] - a[2]))
    return out


# ===========================================================================
# [6] PLACEMENT — static extraction
# ===========================================================================
_SAFE_CALLS = {"dict", "list", "tuple", "set", "frozenset"}


def _lit(node):
    """Evaluate a literal expression: constants, containers, unary minus, and dict()/list()/
    tuple() calls with literal arguments. Anything else raises."""
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, (ast.Tuple, ast.List)):
        vals = [_lit(e) for e in node.elts]
        return tuple(vals) if isinstance(node, ast.Tuple) else vals
    if isinstance(node, ast.Dict):
        return {_lit(k): _lit(v) for k, v in zip(node.keys, node.values)}
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
        v = _lit(node.operand)
        return -v if isinstance(node.op, ast.USub) else +v
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
            and node.func.id in _SAFE_CALLS:
        if node.func.id == "dict":
            if node.args:
                raise ValueError("dict() with positional args is not a literal")
            return {kw.arg: _lit(kw.value) for kw in node.keywords}
        if node.args:
            return list(_lit(node.args[0])) if node.func.id != "tuple" \
                else tuple(_lit(node.args[0]))
        return [] if node.func.id != "tuple" else ()
    raise ValueError("not a literal: %s" % type(node).__name__)


def read_placement(scene_path):
    """(placement_dict_or_None, error_or_None). Absence is not an error."""
    try:
        with open(scene_path, "r", encoding="utf-8") as fh:
            src = fh.read()
    except OSError as e:                                       # pragma: no cover
        return None, "unreadable: %s" % e
    if "PLACEMENT" not in src:
        return None, None
    try:
        tree = ast.parse(src)
    except SyntaxError as e:                                   # pragma: no cover
        return None, "syntax error: %s" % e
    for node in tree.body:
        targets = []
        if isinstance(node, ast.Assign):
            targets = node.targets
        elif isinstance(node, ast.AnnAssign):
            targets = [node.target]
        else:
            continue
        for t in targets:
            if isinstance(t, ast.Name) and t.id == "PLACEMENT":
                try:
                    return _lit(node.value), None
                except (ValueError, SyntaxError) as e:
                    return None, ("PLACEMENT is not a module-level literal (%s) — the "
                                  "declaration contract requires a literal block" % e)
    return None, None


def _as_lines(raw):
    """Normalise a walk_edges / kerb_lines declaration into [((x0,y0),(x1,y1)), ...]."""
    out = []
    for item in (raw or []):
        try:
            (x0, y0), (x1, y1) = item
            out.append(((float(x0), float(y0)), (float(x1), float(y1))))
        except (TypeError, ValueError):
            continue
    return out


# ===========================================================================
# [7] Runtime checks
# ===========================================================================
def check_lint1(scene, inst_by_cls, prims, placement, rules, F):
    """LINT-1 / LINT-1b — tree lateral offset from the kerb / shoulder line."""
    trees = inst_by_cls.get("tree", [])
    if not trees:
        return
    for cid, key, cfg_key in (("LINT-1", "kerb_lines", "LINT-1"),
                              ("LINT-1b", "shoulder_lines", "LINT-1b")):
        cfg = rules["checks"][cfg_key]
        lines = _as_lines((placement or {}).get(key))
        if not lines:
            if cid == "LINT-1":
                F(Finding(cid, SEV_WARN, scene, "<scene>", measured="%d tree(s)" % len(trees),
                          expected=">= %.2f m from %s" % (cfg["value_m"], key),
                          detail="nodata — the scene declares no PLACEMENT[%r]" % key,
                          basis=cfg["basis"], tags=["nodata"]))
            continue
        for inst in trees:
            x, y = instance_xy(inst, prims)
            d, idx = polyline_distance(x, y, lines)
            if d + 1e-9 < cfg["value_m"]:
                F(Finding(cid, SEV_ERROR, scene, inst.label,
                          measured="%.3f m" % d,
                          expected=">= %.2f m" % cfg["value_m"],
                          detail="trunk centre (%.3f, %.3f) vs %s[%d]" % (x, y, key, idx),
                          basis=cfg["basis"], tags=["declared"]))


def check_lint2(scene, inst_by_cls, prims, placement, rules, F, infer):
    """LINT-2 — route pitch constant within 1 %, mean inside [6, 8] m."""
    cfg = rules["checks"]["LINT-2"]
    tol = rules["tolerances"]
    routes = (placement or {}).get("routes") or {}
    if routes:
        for rname, r in sorted(routes.items()):
            pts = [(i, float(p[0]), float(p[1])) for i, p in enumerate(r.get("pts") or [])]
            if len(pts) < 2:
                continue
            sp = spacings(pts)
            mean = sum(sp) / len(sp)
            spread = (max(sp) - min(sp)) / mean if mean > 1e-9 else 0.0
            if spread > tol["pitch_rel"] + 1e-12:
                F(Finding("LINT-2", SEV_ERROR, scene, "routes[%s]" % rname,
                          measured="pitch %.3f-%.3f m (spread %.2f %%)"
                                   % (min(sp), max(sp), 100.0 * spread),
                          expected="constant within %.0f %%" % (100.0 * tol["pitch_rel"]),
                          detail="%d spans" % len(sp), basis=cfg["basis"], tags=["declared"]))
            if not (cfg["min_m"] - 1e-9 <= mean <= cfg["max_m"] + 1e-9):
                F(Finding("LINT-2", SEV_ERROR, scene, "routes[%s]" % rname,
                          measured="mean pitch %.3f m" % mean,
                          expected="[%.1f, %.1f] m" % (cfg["min_m"], cfg["max_m"]),
                          detail="", basis=cfg["basis"], tags=["declared"]))
        return
    trees = inst_by_cls.get("tree", [])
    if not trees:
        return
    F(Finding("LINT-2", SEV_WARN, scene, "<scene>", measured="%d tree(s)" % len(trees),
              expected="PLACEMENT['routes']",
              detail="nodata — the scene declares no route; pitch cannot be gated",
              basis=cfg["basis"], tags=["nodata"]))
    if not infer:
        return
    pts = []
    for inst in trees:
        x, y = instance_xy(inst, prims)
        pts.append((inst.short, x, y))
    runs = collinear_runs(pts, tol["collinear_tol_m"], tol["min_run_n"])
    # Classification filters, not thresholds: a run whose mean spacing is far beyond the legal
    # maximum is park scatter, not a candidate street row, and reporting it is noise.
    cap_pitch = float(tol.get("infer_max_mean_pitch_m", 12.0))
    cap_n = int(tol.get("max_inferred_runs_per_scene", 4))
    keep = []
    for run in runs:
        sp = spacings(run)
        if not sp:
            continue
        if sum(sp) / len(sp) > cap_pitch:
            continue
        keep.append(run)
    keep.sort(key=len, reverse=True)
    dropped = len(keep) - cap_n
    for run in keep[:cap_n]:
        sp = spacings(run)
        mean = sum(sp) / len(sp)
        spread = (max(sp) - min(sp)) / mean if mean > 1e-9 else 0.0
        bad_spread = spread > tol["pitch_rel"] + 1e-12
        bad_band = not (cfg["min_m"] - 1e-9 <= mean <= cfg["max_m"] + 1e-9)
        if not (bad_spread or bad_band):
            continue
        why = []
        if bad_spread:
            why.append("spread %.2f %% > %.0f %%" % (100.0 * spread, 100.0 * tol["pitch_rel"]))
        if bad_band:
            why.append("mean %.3f m outside [%.1f, %.1f]" % (mean, cfg["min_m"], cfg["max_m"]))
        F(Finding("LINT-2", SEV_WARN, scene, "row %s..%s (n=%d)"
                  % (run[0][0], run[-1][0], len(run)),
                  measured="pitch %.3f-%.3f m (mean %.3f)" % (min(sp), max(sp), mean),
                  expected="constant, [%.1f, %.1f] m" % (cfg["min_m"], cfg["max_m"]),
                  detail="; ".join(why),
                  basis=cfg["basis"] + " · run inferred, not declared", tags=["inferred"]))
    if dropped > 0:
        F(Finding("LINT-2", SEV_INFO, scene, "<inferred runs>",
                  measured="%d candidate run(s) beyond the report cap" % dropped,
                  expected="", detail="cap = tolerances.max_inferred_runs_per_scene (%d); runs "
                                      "with mean pitch > %.1f m were classified as scatter"
                                      % (cap_n, cap_pitch),
                  basis="[convention] classification cap, not a threshold", tags=["inferred"]))


def check_lint3(scene, inst_by_cls, prims, placement, rules, F, exempt_res):
    """LINT-3 — route bearing vs kerb bearing, and per-tree placement yaw = 0.

    The crown bearing that `build_tree` puts on `<prefix>/Veg` is exempt (§12-15), so the yaw
    read here is the frame ABOVE the tree — the placement frame.
    """
    cfg = rules["checks"]["LINT-3"]
    tol = rules["tolerances"]
    trees = inst_by_cls.get("tree", [])
    for inst in trees:
        parent = inst.root.rsplit("/", 1)[0]
        f = world_frame(prims, parent)
        if abs(norm_deg(f.theta) if norm_deg(f.theta) <= 180 else norm_deg(f.theta) - 360.0) \
                > tol["yaw_zero_deg"]:
            th = norm_deg(f.theta)
            th = th if th <= 180.0 else th - 360.0
            F(Finding("LINT-3", SEV_ERROR, scene, inst.label,
                      measured="placement yaw %+.3f deg" % th,
                      expected="0 deg (+- %.1f)" % tol["yaw_zero_deg"],
                      detail="carried by the frame above /Veg (%s); the crown bearing on /Veg "
                             "itself is exempt (spec §12-15)" % parent,
                      basis=cfg["basis"], tags=["measured"]))
    routes = (placement or {}).get("routes") or {}
    kerbs = _as_lines((placement or {}).get("kerb_lines"))
    if routes and kerbs:
        for rname, r in sorted(routes.items()):
            pts = [(float(p[0]), float(p[1])) for p in (r.get("pts") or [])]
            if len(pts) < 2:
                continue
            rb = seg_bearing((pts[0], pts[-1]))
            best = min(kerbs, key=lambda s: seg_distance(pts[0][0], pts[0][1], s))
            kb = seg_bearing(best)
            d = min(ang_diff(rb, kb), ang_diff(rb, kb + 180.0))
            if d > tol["bearing_deg"]:
                F(Finding("LINT-3", SEV_ERROR, scene, "routes[%s]" % rname,
                          measured="route %.3f deg vs kerb %.3f deg (delta %.3f)" % (rb, kb, d),
                          expected="+- %.1f deg" % tol["bearing_deg"],
                          detail="", basis=cfg["basis"], tags=["declared"]))
    elif trees and not kerbs:
        F(Finding("LINT-3", SEV_WARN, scene, "<scene>", measured="%d tree(s)" % len(trees),
                  expected="PLACEMENT['kerb_lines'] + ['routes']",
                  detail="nodata — bearing half of PE-3 not evaluable",
                  basis=cfg["basis"], tags=["nodata"]))


def check_lint4(scene, inst_by_cls, prims, placement, rules, F, infer):
    """LINT-4 — one species per route (S-1) / per bed (S-2); LINT-4b — retired species."""
    cfg4 = rules["checks"]["LINT-4"]
    cfg4b = rules["checks"]["LINT-4b"]
    retired = set(cfg4b.get("retired") or [])

    def species_of(inst):
        child = (inst.spec.get("species_from", "<self>/Asset")).replace("<self>", inst.root)
        p = prims.get(child)
        if p is None or not p.refs:
            return None
        return p.refs[0].rsplit(".", 1)[0]

    members = []
    for cls in ("tree", "shrub"):
        for inst in inst_by_cls.get(cls, []):
            sp = species_of(inst)
            if sp is None:
                continue
            members.append((cls, inst, sp))

    # LINT-4b needs no declaration: the bound asset name is the evidence.
    for cls, inst, sp in members:
        if sp in retired:
            F(Finding("LINT-4b", SEV_ERROR, scene, inst.label,
                      measured=sp, expected="a PASS species (§10.2 VEG_SPECIES)",
                      detail="retired species bound at %s" % cls,
                      basis=cfg4b["basis"].strip(), tags=["measured"]))

    routes = (placement or {}).get("routes") or {}
    if routes:
        for rname, r in sorted(routes.items()):
            want = r.get("species")
            pts = [(float(p[0]), float(p[1])) for p in (r.get("pts") or [])]
            got = Counter()
            for cls, inst, sp in members:
                if cls != "tree":
                    continue
                x, y = instance_xy(inst, prims)
                if pts and min(math.hypot(x - px, y - py) for px, py in pts) <= 1.0:
                    got[sp] += 1
            if len(got) > 1:
                F(Finding("LINT-4", SEV_ERROR, scene, "routes[%s]" % rname,
                          measured=" · ".join("%s x%d" % kv for kv in got.most_common()),
                          expected="one species (declared: %s)" % want,
                          detail="", basis=cfg4["basis"], tags=["declared"]))
        return
    if not members:
        return
    if not infer:
        return
    census = Counter(sp for _c, _i, sp in members)
    if len(census) > 1:
        F(Finding("LINT-4", SEV_WARN, scene, "<scene census>",
                  measured=" · ".join("%s x%d" % kv for kv in census.most_common()),
                  expected="one species per route / per bed (S-1 / S-2)",
                  detail="nodata for the route-scoped gate — the scene declares no "
                         "PLACEMENT['routes']; this is the scene-wide census, %d distinct "
                         "species over %d plantings" % (len(census), len(members)),
                  basis=cfg4["basis"] + " · census inferred, not declared",
                  tags=["inferred", "census"]))


def check_lint5(scene, inst_by_cls, prims, placement, rules, F):
    """LINT-5 — free walking width after subtracting the 표2.2 occupancy."""
    cfg = rules["checks"]["LINT-5"]
    widths = rules.get("obstacle_widths_m") or {}
    edges = _as_lines((placement or {}).get("walk_edges"))
    classes = cfg.get("applies_to") or []
    subjects = [(c, i) for c in classes for i in inst_by_cls.get(c, [])]
    if not subjects:
        return
    if not edges:
        F(Finding("LINT-5", SEV_WARN, scene, "<scene>",
                  measured="%d furniture / planting item(s)" % len(subjects),
                  expected="PLACEMENT['walk_edges']",
                  detail="nodata — no walking-zone boundary declared, so the effective width "
                         "cannot be computed",
                  basis=cfg["basis"].strip(), tags=["nodata"]))
        return
    for cls, inst in subjects:
        x, y = instance_xy(inst, prims)
        d, idx = polyline_distance(x, y, edges)
        band = widths.get(cls)
        occ = float(band[1]) if isinstance(band, (list, tuple)) and band else None
        if occ is None:
            continue
        free = d - occ / 2.0
        if free + 1e-9 < cfg["floor_m"]:
            F(Finding("LINT-5", SEV_ERROR, scene, inst.label,
                      measured="free %.3f m (centre %.3f m from edge, occupancy %.2f m)"
                               % (free, d, occ),
                      expected=">= %.1f m" % cfg["floor_m"],
                      detail="walk_edges[%d]; occupancy = 표2.2 upper bound for %s" % (idx, cls),
                      basis=cfg["basis"].strip(), tags=["declared"]))


def check_lint6(scene, inst_by_cls, prims, placement, rules, F, infer):
    """LINT-6 — bollard height / diameter / pitch, and the C-9 carrier set."""
    cfg = rules["checks"]["LINT-6"]
    tol = rules["tolerances"]
    props = rules["props"]["bollard"]
    hmin, hmax = cfg["height_m"]
    dmin, dmax = cfg["diameter_m"]
    bollards = inst_by_cls.get("bollard", [])

    carriers = set(props.get("carrier_set") or [])
    if cfg.get("carrier_set_check"):
        if bollards and scene not in carriers:
            F(Finding("LINT-6", SEV_ERROR, scene, "<scene>",
                      measured="%d bollard instance(s)" % len(bollards),
                      expected="scene in the C-9 carrier set",
                      detail="a bollard carrier that the corrected carrier set does not list — "
                             "either the set or the scene is wrong",
                      basis="corrected fact C-9", tags=["measured"]))
        if not bollards and scene in carriers:
            F(Finding("LINT-6", SEV_ERROR, scene, "<scene>", measured="0 bollard instances",
                      expected="scene is in the C-9 carrier set",
                      detail="carrier set lists this scene but no bollard prim was assembled",
                      basis="corrected fact C-9", tags=["measured"]))
    if not bollards:
        return

    pts = []
    for inst in bollards:
        post = None
        for suf in props.get("post_suffixes") or [""]:
            cand = prims.get(inst.root + suf)
            if cand is not None and ("radius" in cand.attrs or "height" in cand.attrs):
                post = cand
                break
        x, y = instance_xy(inst, prims)
        pts.append((inst.short, x, y))
        if post is None:
            F(Finding("LINT-6", SEV_WARN, scene, inst.label, measured="no post cylinder",
                      expected="a Cylinder carrying radius / height",
                      detail="height and diameter not readable from the inventory",
                      basis=cfg["basis"], tags=["nodata"]))
            continue
        r = post.attrs.get("radius")
        h = post.attrs.get("height")
        if isinstance(r, (int, float)):
            dia = 2.0 * float(r)
            if not (dmin - 1e-9 <= dia <= dmax + 1e-9):
                F(Finding("LINT-6", SEV_ERROR, scene, post.path,
                          measured="dia %.3f m" % dia,
                          expected="[%.2f, %.2f] m" % (dmin, dmax),
                          detail="", basis=cfg["basis"], tags=["measured"]))
        if isinstance(h, (int, float)):
            if not (hmin - 1e-9 <= float(h) <= hmax + 1e-9):
                F(Finding("LINT-6", SEV_ERROR, scene, post.path,
                          measured="h %.3f m" % float(h),
                          expected="[%.1f, %.1f] m" % (hmin, hmax),
                          detail="", basis=cfg["basis"], tags=["measured"]))

    # Pitch. A declared route or anchor is a gate; an inferred collinear run is advisory.
    if not infer:
        return
    want, ptol = float(cfg["pitch_m"]), float(cfg["pitch_tol_m"])
    minn = int(tol.get("bollard_min_run_n", 2))
    for run in collinear_runs(pts, tol["collinear_tol_m"], minn):
        sp = spacings(run)
        bad = [(i, s) for i, s in enumerate(sp) if abs(s - want) > ptol + 1e-9]
        if not bad:
            continue
        F(Finding("LINT-6", SEV_WARN, scene, "run %s..%s (n=%d)"
                  % (run[0][0], run[-1][0], len(run)),
                  measured="gaps " + ", ".join("%.3f" % s for s in sp),
                  expected="%.1f +- %.1f m" % (want, ptol),
                  detail="%d of %d spans out of band" % (len(bad), len(sp)),
                  basis=cfg["basis"] + " · run inferred, not declared", tags=["inferred"]))

    # PE-7's axis lock is not readable off a solid of revolution — say so once per scene.
    if not _as_lines((placement or {}).get("kerb_lines")):
        F(Finding("LINT-6", SEV_WARN, scene, "<scene>",
                  measured="%d bollard(s)" % len(bollards),
                  expected="PLACEMENT['kerb_lines'] for the PE-7 axis lock",
                  detail="nodata — a bollard is a solid of revolution and carries no readable "
                         "yaw; the 보도·차도 경계 lock needs the declared line",
                  basis=cfg["basis"], tags=["nodata"]))


def check_lint7(scene, inst_by_cls, prims, placement, rules, F, infer, exempt_res):
    """LINT-7 — furniture yaw against the declared anchor bearings (J-3 / J-5)."""
    cfg = rules["checks"]["LINT-7"]
    tol = rules["tolerances"]
    anchors = (placement or {}).get("anchors") or {}
    classes = cfg.get("applies_to") or []
    meander = set(cfg.get("meander_exempt_scenes") or [])

    allowed, declared = [], bool(anchors)
    if declared:
        for aname, a in sorted(anchors.items()):
            try:
                b = float(a.get("face_bearing_deg"))
            except (TypeError, ValueError):
                continue
            allowed.append((aname, b))
    else:
        allowed = [("axis", float(b)) for b in (cfg.get("infer_bearings_deg") or [])]

    subjects = [(c, i) for c in classes for i in inst_by_cls.get(c, [])]
    if not subjects:
        return
    if not declared:
        # The nodata row is emitted whether or not inference is on: a rule that cannot run must
        # always say so out loud, otherwise --no-infer would read as a clean pass.
        F(Finding("LINT-7", SEV_WARN, scene, "<scene>",
                  measured="%d furniture item(s)" % len(subjects),
                  expected="PLACEMENT['anchors']",
                  detail="nodata for the gate — %s"
                         % ("findings below fall back to the spec's own expected outcome "
                            "{0, 90, 180, 270} and are advisory" if infer
                            else "inference is off (--no-infer), so nothing further is reported"),
                  basis=cfg["basis"], tags=["nodata"]))
        if not infer:
            return

    for cls, inst in subjects:
        bearings = instance_bearings(inst, prims, exempt_res, tol["yaw_zero_deg"])
        for th, (where, nonplanar) in bearings.items():
            hits = [(nm, b) for nm, b in allowed if ang_diff(th, b) <= tol["bearing_deg"]]
            if hits:
                continue
            near = min(allowed, key=lambda nb: ang_diff(th, nb[1])) if allowed else ("-", 0.0)
            signed = th if th <= 180.0 else th - 360.0
            sev = SEV_ERROR if declared else SEV_WARN
            tags = ["declared"] if declared else ["inferred"]
            det = "prim %s" % where
            if nonplanar:
                det += " · frame carries a non-planar op — bearing partially readable"
            if scene in meander:
                det += (" · spec §10.1 meander-tangent exemption may apply; re-adjudicate "
                        "against a declared anchor before editing")
                tags.append("meander_exempt_candidate")
            F(Finding("LINT-7", sev, scene, inst.label,
                      measured="yaw %+.3f deg" % signed,
                      expected=("anchor bearings %s" % ", ".join("%s=%.1f" % ab for ab in allowed)
                                if declared else "{0, 90, 180, 270} deg"),
                      detail=det + " · nearest allowed %s (%.1f deg, delta %.3f)"
                             % (near[0], near[1], ang_diff(th, near[1])),
                      basis=cfg["basis"] + ("" if declared else " · " + "inferred bearing set"),
                      tags=tags))


def check_lint8(scene, inst_by_cls, prims, rules, F):
    """LINT-8 — no rotz on a `patch` / `stain` ground element (J-1 / J-2)."""
    cfg = rules["checks"]["LINT-8"]
    tol = rules["tolerances"]
    exempt_kinds = set(cfg.get("exempt_stain_kinds") or [])
    stain_rx = re.compile(rules["props"]["stain"]["pattern"])
    for cls in ("patch", "stain"):
        for inst in inst_by_cls.get(cls, []):
            kind = None
            if cls == "stain":
                m = stain_rx.search(inst.root)
                kind = m.group("kind") if m else None
                if kind in exempt_kinds:
                    continue
            f = world_frame(prims, inst.root)
            th = norm_deg(f.theta)
            signed = th if th <= 180.0 else th - 360.0
            if abs(signed) <= tol["yaw_zero_deg"]:
                continue
            F(Finding("LINT-8", SEV_ERROR, scene, inst.label,
                      measured="rotz %+.3f deg" % signed,
                      expected="0 deg",
                      detail="%s element%s" % (cls, (" kind=%s" % kind) if kind else ""),
                      basis=cfg["basis"], tags=["measured"]))


def check_lint9(scene, inst_by_cls, prims, placement, rules, F, enforce):
    """LINT-9 — bench / lamp / bin setback. Evidence-gated: WARN until the band lands (§1.8)."""
    cfg = rules["checks"]["LINT-9"]
    gate = (rules.get("gates") or {}).get("LINT-9") or {}
    band = gate.get("band")
    classes = cfg.get("applies_to") or []
    subjects = [(c, i) for c in classes for i in inst_by_cls.get(c, [])]
    if not subjects:
        return
    if band is None:
        if enforce:
            raise HarnessError(
                "LINT-9 was asked to enforce but gates.LINT-9.band is null "
                "(blocked_on: %s). Spec §1.8 forbids inventing the threshold."
                % gate.get("blocked_on"))
        F(Finding("LINT-9", SEV_BLOCKED, scene, "<scene>",
                  measured="%d bench / lamp / bin item(s) staged" % len(subjects),
                  expected="the M1-M6 measured setback band",
                  detail="TODO gate — blocked_on: %s. Prepared, not enforced (spec §1.8)."
                         % gate.get("blocked_on"),
                  basis=cfg["basis"], tags=["gated", "todo"]))
        return
    edges = _as_lines((placement or {}).get("walk_edges"))
    if not edges:
        F(Finding("LINT-9", SEV_WARN, scene, "<scene>", measured="%d item(s)" % len(subjects),
                  expected="PLACEMENT['walk_edges']", detail="nodata",
                  basis=cfg["basis"], tags=["nodata"]))
        return
    sev = SEV_ERROR if (enforce and gate.get("mode") == "hard") else SEV_WARN
    for cls, inst in subjects:
        lo, hi = band.get(cls, (None, None))
        if lo is None:
            continue
        x, y = instance_xy(inst, prims)
        d, idx = polyline_distance(x, y, edges)
        if not (float(lo) - 1e-9 <= d <= float(hi) + 1e-9):
            F(Finding("LINT-9", sev, scene, inst.label, measured="setback %.3f m" % d,
                      expected="[%.2f, %.2f] m" % (float(lo), float(hi)),
                      detail="walk_edges[%d]" % idx, basis=cfg["basis"], tags=["declared"]))


# ===========================================================================
# [8] Static (source) checks
# ===========================================================================
def _callee_name(node):
    f = node.func
    if isinstance(f, ast.Name):
        return f.id
    if isinstance(f, ast.Attribute):
        return f.attr
    return "<expr>"


def check_lint10_static(scene, path, rules, F):
    """LINT-10 — `jitter=` kwarg > 0 in scene code (J-11 keep-at-zero ban)."""
    cfg = rules["checks"]["LINT-10"]
    ignore = set(cfg.get("ignore_kwargs") or [])
    locked = {d["name"]: d.get("where", "") for d in (cfg.get("zero_locked_callees") or [])}
    other_sev = SEV_WARN if cfg.get("other_callee_severity") == "warn" else SEV_ERROR
    try:
        with open(path, "r", encoding="utf-8") as fh:
            src = fh.read()
        tree = ast.parse(src)
    except (OSError, SyntaxError) as e:                        # pragma: no cover
        raise HarnessError("cannot parse %s: %s" % (path, e))
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        callee = _callee_name(node)
        for kw in node.keywords:
            if kw.arg is None or kw.arg in ignore:
                continue
            if kw.arg != "jitter":
                continue
            try:
                val = _lit(kw.value)
            except (ValueError, SyntaxError):
                val = None
            line = getattr(kw.value, "lineno", node.lineno)
            if isinstance(val, (int, float)):
                if abs(float(val)) <= 1e-12:
                    continue
                measured = "jitter=%g" % val
            elif val is None:
                measured = "jitter=<non-literal>"
            else:
                measured = "jitter=%r" % (val,)
            if callee in locked:
                F(Finding("LINT-10", SEV_ERROR, scene,
                          "%s:%d %s(...)" % (os.path.relpath(path, REPO), line, callee),
                          measured=measured, expected="jitter=0.0",
                          detail="keep-at-zero parameter (%s) — J-11 ban on non-zero"
                                 % locked[callee],
                          basis=cfg["basis"], tags=["static", "j11"]))
            else:
                F(Finding("LINT-10", other_sev, scene,
                          "%s:%d %s(...)" % (os.path.relpath(path, REPO), line, callee),
                          measured=measured, expected="adjudicate: placement or size?",
                          detail="not one of the three J-11 keep-at-zero builders. §1.2 X2 KEEPS "
                                 "size / interval variation and abolishes placement jitter, so "
                                 "the owning scene WP must classify this call",
                          basis=cfg["basis"], tags=["static", "needs-adjudication"]))


def check_lint7_static(scene, path, rules, F):
    """LINT-7 static companion — `bc.jit_yaw` / `bc.jit_pos` call sites (J-3 / J-4)."""
    cfg = rules["checks"]["LINT-7-static"]
    try:
        with open(path, "r", encoding="utf-8") as fh:
            src = fh.read()
        tree = ast.parse(src)
    except (OSError, SyntaxError) as e:                        # pragma: no cover
        raise HarnessError("cannot parse %s: %s" % (path, e))
    calls = 0
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        f = node.func
        if isinstance(f, ast.Attribute) and f.attr in ("jit_yaw", "jit_pos"):
            calls += 1
            F(Finding("LINT-7-static", SEV_ERROR, scene,
                      "%s:%d %s" % (os.path.relpath(path, REPO), node.lineno, f.attr),
                      measured="call site", expected="removed (J-3 / J-4 abolished)",
                      detail="furniture takes the bearing of the thing it belongs to; "
                             "variation goes to size / model / interval (§10.1)",
                      basis=cfg["basis"], tags=["static"]))
    # C-2's own instrument, reproduced verbatim: `grep -rn "bc\.jit_yaw\|bc\.jit_pos"`. The
    # bare-name form is deliberately NOT counted — batch1_common's own `def jit_yaw` is the
    # definition, not a call site, and counting it would inflate the census.
    text_hits = len(re.findall(r"bc\.jit_yaw|bc\.jit_pos", src))
    return calls, text_hits


# ===========================================================================
# [9] Driver
# ===========================================================================
def gather(scene_names, rules, verbose=True):
    """Assemble the scenes on the stub harness. Raises HarnessError on any assembly failure."""
    try:
        import geom_invariance_check as giv
    except ImportError as e:                                   # pragma: no cover
        raise HarnessError("cannot import the stub harness: %s" % e)
    files = giv._scene_files(set(scene_names) if scene_names else None)
    if not files:
        raise HarnessError("no scene files matched %r" % (scene_names,))
    arm = dict((rules.get("meta") or {}).get("harness_arm")
               or {"NEGOBS_LOOK_MTL": "1", "NEGOBS_LOOK_GEO": "1"})
    if verbose:
        print("[harness] geom_invariance_check stub · arm %s · %d scene(s)" % (arm, len(files)))
    res = giv.run_arm("lint", arm, files, dump=True)
    if res is None:
        raise HarnessError("the stub harness produced no inventory (see its stderr dump above)")
    errs = {k: v["error"] for k, v in res["scenes"].items() if "error" in v}
    if errs:
        for k, v in sorted(errs.items()):
            print("[harness] assembly failed %s: %s" % (k, v), file=sys.stderr)
        raise HarnessError("%d scene(s) failed to assemble — no verdict is possible" % len(errs))
    by_file = {}
    for p in files:
        name = os.path.splitext(os.path.basename(p))[0].split("_")[0]
        by_file[name] = p
    return res, by_file


def run(args):
    rules = load_rules(args.rules)
    suffix_rules, segment_rules, exempt_res = compiled_props(rules)
    suppressions = compiled_suppressions(rules)

    filt = None
    if args.scenes and args.scenes.strip().lower() not in ("all", "*"):
        filt = [s.strip() for s in args.scenes.split(",") if s.strip()]
    res, by_file = gather(filt, rules, verbose=not args.quiet)

    only = set(s.strip() for s in args.only.split(",")) if args.only else None
    skip = set(s.strip() for s in args.skip.split(",")) if args.skip else set()
    findings = []
    withheld = OrderedDict()

    def suppressor(f):
        """Return the do_not_touch entry that withholds this finding, or None."""
        for sup in suppressions:
            if f.check not in sup["checks"]:
                continue
            if sup["scope"] and sup["scope"] not in (f.scene, "all"):
                continue
            if sup["prefix"] and not str(f.subject).startswith(sup["prefix"]):
                continue
            return sup
        return None

    def F(f):
        if only is not None and f.check not in only:
            return
        if f.check in skip:
            return
        sup = suppressor(f)
        if sup is not None:
            key = (f.check, f.scene, sup["id"])
            if key not in withheld:
                withheld[key] = [0, sup["rule"]]
            withheld[key][0] += 1
            return
        findings.append(f)
    stats = OrderedDict()
    veg_asset_scenes = 0
    jit_calls_total = jit_text_total = 0

    for scene in sorted(res["scenes"]):
        inv = res["scenes"][scene].get("inv") or []
        prims = parse_inventory(inv)
        instances, near_miss, _ = classify(prims, suffix_rules, segment_rules, exempt_res)
        inst_by_cls = defaultdict(list)
        for (cls, _root), inst in instances.items():
            inst_by_cls[cls].append(inst)
        if inst_by_cls.get("tree"):
            veg_asset_scenes += 1

        path = by_file.get(scene)
        placement, perr = (None, None)
        if path:
            placement, perr = read_placement(path)
        if perr:
            F(Finding("PLACEMENT", SEV_ERROR if args.require_placement else SEV_WARN, scene,
                      os.path.relpath(path, REPO), measured="unreadable", expected="literal block",
                      detail=perr, basis="spec §10.4 declaration contract", tags=["placement"]))
        elif placement is None:
            sev = SEV_ERROR if args.require_placement else SEV_WARN
            F(Finding("PLACEMENT", sev, scene, os.path.relpath(path, REPO) if path else scene,
                      measured="absent", expected="PLACEMENT = dict(walk_edges=..., kerb_lines=..., "
                                                  "anchors=..., routes=...)",
                      detail="every hard rule that needs a datum degrades to nodata in this scene",
                      basis="spec §10.4", tags=["placement"]))

        check_lint1(scene, inst_by_cls, prims, placement, rules, F)
        check_lint2(scene, inst_by_cls, prims, placement, rules, F, not args.no_infer)
        check_lint3(scene, inst_by_cls, prims, placement, rules, F, exempt_res)
        check_lint4(scene, inst_by_cls, prims, placement, rules, F, not args.no_infer)
        check_lint5(scene, inst_by_cls, prims, placement, rules, F)
        check_lint6(scene, inst_by_cls, prims, placement, rules, F, not args.no_infer)
        check_lint7(scene, inst_by_cls, prims, placement, rules, F, not args.no_infer, exempt_res)
        check_lint8(scene, inst_by_cls, prims, rules, F)
        check_lint9(scene, inst_by_cls, prims, placement, rules, F, args.enforce_lint9)
        if path:
            check_lint10_static(scene, path, rules, F)
            c, t = check_lint7_static(scene, path, rules, F)
            jit_calls_total += c
            jit_text_total += t

        if near_miss and (rules["props"].get("near_miss_report") and not args.quiet):
            for p, cls, why in near_miss:
                F(Finding("UNCLASSIFIED", SEV_INFO, scene, p, measured=cls,
                          expected="classified prop",
                          detail="near miss, excluded from every rule: %s" % why,
                          basis="[convention] taxonomy, not a threshold", tags=["taxonomy"]))

        stats[scene] = OrderedDict(
            prims=len(prims),
            instances=OrderedDict(sorted((c, len(v)) for c, v in inst_by_cls.items())),
            placement=bool(placement))

    for (check, scene, dnt_id), (n, rule) in withheld.items():
        findings.append(Finding(check, SEV_INFO, scene, "<suppressed by %s>" % dnt_id,
                                measured="%d finding(s) withheld" % n, expected="",
                                detail=rule, basis="spec §12 do-not-touch",
                                tags=["suppressed", dnt_id]))

    # Reconcile the abolition census against corrected fact C-2.
    cfg = rules["checks"]["LINT-7-static"]
    exp_calls = int(cfg.get("expected_call_sites", 0))
    exp_text = int(cfg.get("expected_text_hits", 0))
    if filt is None and (jit_calls_total != exp_calls or jit_text_total != exp_text):
        F(Finding("LINT-7-static", SEV_WARN, "<all>", "census",
                  measured="%d call site(s), %d text hit(s)" % (jit_calls_total, jit_text_total),
                  expected="%d call site(s), %d text hit(s)" % (exp_calls, exp_text),
                  detail="corrected fact C-2 fixes the inventory at 24 calls + 1 comment "
                         "(%s). A divergence means the tree moved or the fact is stale"
                         % cfg.get("expected_comment_site"),
                  basis="C-2", tags=["census"]))

    meta = OrderedDict(
        rules=os.path.relpath(rules["_path"], REPO),
        arm=(rules.get("meta") or {}).get("harness_arm"),
        scenes=len(res["scenes"]),
        veg_route="asset (%d/%d scenes carry bound tree USDs)"
                  % (veg_asset_scenes, len(res["scenes"])),
        jit_call_sites=jit_calls_total,
        jit_text_hits=jit_text_total,
        infer="on" if not args.no_infer else "off",
        require_placement=bool(args.require_placement))
    return findings, stats, meta


# ===========================================================================
# [10] Report
# ===========================================================================
def render_text(findings, stats, meta, max_rows):
    out = []
    w = out.append
    w("=" * 100)
    w("placement_lint — LINT-1..LINT-10  (W3 execution spec §10.4)")
    w("=" * 100)
    for k, v in meta.items():
        w("  %-18s %s" % (k, v))
    w("")

    by_check = defaultdict(list)
    for f in findings:
        by_check[f.check].append(f)
    sev_count = Counter(f.severity for f in findings)

    w("-" * 100)
    w("%-16s %7s %7s %7s %7s   %s" % ("check", "ERROR", "WARN", "BLOCK", "INFO", "scenes"))
    w("-" * 100)
    for check in sorted(by_check):
        fs = by_check[check]
        c = Counter(f.severity for f in fs)
        scenes = sorted({f.scene for f in fs})
        tail = ", ".join(scenes[:8]) + (" (+%d)" % (len(scenes) - 8) if len(scenes) > 8 else "")
        w("%-16s %7d %7d %7d %7d   %s"
          % (check, c[SEV_ERROR], c[SEV_WARN], c[SEV_BLOCKED], c[SEV_INFO], tail))
    w("-" * 100)
    w("%-16s %7d %7d %7d %7d" % ("TOTAL", sev_count[SEV_ERROR], sev_count[SEV_WARN],
                                 sev_count[SEV_BLOCKED], sev_count[SEV_INFO]))
    w("")

    for check in sorted(by_check):
        fs = sorted(by_check[check], key=lambda f: f.sort_key())
        w("=" * 100)
        w("%s  —  %d finding(s)" % (check, len(fs)))
        w("-" * 100)
        shown = fs if max_rows <= 0 else fs[:max_rows]
        for f in shown:
            w("  [%-7s] %-10s %s" % (f.severity, f.scene, f.subject))
            w("             measured : %s" % f.measured)
            w("             expected : %s" % f.expected)
            if f.detail:
                w("             detail   : %s" % f.detail)
            w("             basis    : %s%s"
              % (f.basis, ("  [%s]" % ",".join(f.tags)) if f.tags else ""))
        if len(fs) > len(shown):
            w("  ... %d more (raise --max-rows or use --format json)" % (len(fs) - len(shown)))
        w("")

    w("=" * 100)
    w("per-scene inventory")
    w("-" * 100)
    for scene, s in stats.items():
        inst = " ".join("%s=%d" % kv for kv in s["instances"].items()) or "-"
        w("  %-10s prims=%-6d PLACEMENT=%-5s %s"
          % (scene, s["prims"], "yes" if s["placement"] else "NO", inst))
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Geometric legality of props — LINT-1..LINT-10 (W3 spec §10.4).")
    ap.add_argument("--scenes", default="all",
                    help="'all' or a comma-separated scene-name filter (scene06,sceneN5)")
    ap.add_argument("--rules", default=DEFAULT_RULES, help="rule table (YAML)")
    ap.add_argument("--only", default="", help="run only these checks (LINT-6,LINT-8)")
    ap.add_argument("--skip", default="", help="skip these checks")
    ap.add_argument("--format", default="text", choices=("text", "json"))
    ap.add_argument("--json", default="", help="also write the full JSON report here")
    ap.add_argument("--max-rows", type=int, default=40,
                    help="max rows printed per check in text mode (0 = all)")
    ap.add_argument("--require-placement", action="store_true",
                    help="a scene with no PLACEMENT block is an ERROR (WINDOW 3 posture)")
    ap.add_argument("--warn-as-error", action="store_true")
    ap.add_argument("--no-infer", action="store_true",
                    help="disable inferred datums; report nodata instead")
    ap.add_argument("--enforce-lint9", action="store_true",
                    help="flip the LINT-9 gate to hard — refuses while the band is null (§1.8)")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)

    try:
        findings, stats, meta = run(a)
    except HarnessError as e:
        print("[placement_lint][harness] %s" % e, file=sys.stderr)
        return EXIT_HARNESS

    payload = OrderedDict(meta=meta,
                          findings=[f.as_dict() for f in sorted(findings, key=lambda x: x.sort_key())],
                          stats=stats)
    if a.json:
        dest = a.json if os.path.isabs(a.json) else os.path.join(REPO, a.json)
        os.makedirs(os.path.dirname(dest) or ".", exist_ok=True)
        with open(dest, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=1, ensure_ascii=False)
        if not a.quiet:
            print("[report] %s" % dest)
    if a.format == "json":
        print(json.dumps(payload, indent=1, ensure_ascii=False))
    else:
        print(render_text(findings, stats, meta, a.max_rows))

    n_err = sum(1 for f in findings if f.severity == SEV_ERROR)
    n_warn = sum(1 for f in findings if f.severity == SEV_WARN)
    if n_err or (a.warn_as_error and n_warn):
        return EXIT_VIOLATION
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
