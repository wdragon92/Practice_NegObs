#!/usr/bin/env python3
"""CPU-only cue_* wiring coverage audit over the Practice_NegObs scene library.

For every scene .py on disk:
  - extract SCENE_CONFIG defaults (AST)
  - find every read of each config key (cfg["k"], SCENE_CONFIG["k"], cfg.get("k"), module const)
  - for `if <key>` guards, list the function calls inside the guarded body (= what the toggle removes)
  - flag whether the guard sits INSIDE a hazard_* guard (structural coupling / 'guoff' pattern)
"""
import ast, json, os, re, sys
from collections import defaultdict

ROOT = "/home/vislab/Desktop/work_sy/Practice_NegObs"

SCENE_DIRS = [
    ("main",       os.path.join(ROOT, "scenes/main")),
    ("batch1",     os.path.join(ROOT, "scenes/batch1")),
    ("probe",      os.path.join(ROOT, "scenes/probe")),
    ("archive_v3", os.path.join(ROOT, "scenes/archive_v3")),
    ("cueoff_port", os.path.join(ROOT, "experiments/weekend_0823/cue_audit/scenes_cueoff")),
]

KIT = {"scene_common.py", "batch1_common.py", "probe_common.py", "building_kit.py",
       "facade_kit.py", "ground_kit.py", "infra_kit.py", "props_kit.py",
       "stair_kit.py", "urban_kit.py", "variation_kit.py"}


def scene_files():
    out = []
    for tag, d in SCENE_DIRS:
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            if not fn.endswith(".py"):
                continue
            if fn in KIT:
                continue
            p = os.path.join(d, fn)
            if os.path.islink(p):
                continue
            out.append((tag, fn, p))
    return out


class KeyRefFinder(ast.NodeVisitor):
    """Collect subscript/get reads of SCENE_CONFIG-ish dicts, and module-level
    constants derived from them."""

    def __init__(self, keys):
        self.keys = set(keys)
        self.refs = defaultdict(list)          # key -> [(lineno, snippet)]
        self.const_alias = {}                  # CONST_NAME -> key

    def visit_Subscript(self, node):
        k = _const_str(node.slice)
        base = _base_name(node.value)
        if k in self.keys and base in ("cfg", "SCENE_CONFIG", "C", "conf", "config", "CFG"):
            self.refs[k].append(node.lineno)
        self.generic_visit(node)

    def visit_Call(self, node):
        f = node.func
        if isinstance(f, ast.Attribute) and f.attr == "get" and node.args:
            k = _const_str(node.args[0])
            base = _base_name(f.value)
            if k in self.keys and base in ("cfg", "SCENE_CONFIG", "C", "conf", "config", "CFG"):
                self.refs[k].append(node.lineno)
        self.generic_visit(node)


def _const_str(n):
    if isinstance(n, ast.Constant) and isinstance(n.value, str):
        return n.value
    if isinstance(n, ast.Index):  # py<3.9
        return _const_str(n.value)
    return None


def _base_name(n):
    if isinstance(n, ast.Name):
        return n.id
    if isinstance(n, ast.Attribute):
        return n.attr
    return None


def keys_in_test(node, keys, alias):
    """Which config keys the expression references."""
    found = set()
    for n in ast.walk(node):
        if isinstance(n, ast.Subscript):
            k = _const_str(n.slice)
            if k in keys and _base_name(n.value) in ("cfg", "SCENE_CONFIG", "C", "conf", "config", "CFG"):
                found.add(k)
        elif isinstance(n, ast.Call):
            f = n.func
            if isinstance(f, ast.Attribute) and f.attr == "get" and n.args:
                k = _const_str(n.args[0])
                if k in keys and _base_name(f.value) in ("cfg", "SCENE_CONFIG", "C", "conf", "config", "CFG"):
                    found.add(k)
        elif isinstance(n, ast.Name) and n.id in alias:
            found.add(alias[n.id])
    return found


def calls_in(body):
    names = []
    for st in body:
        for n in ast.walk(st):
            if isinstance(n, ast.Call):
                f = n.func
                if isinstance(f, ast.Name):
                    names.append(f.id)
                elif isinstance(f, ast.Attribute):
                    names.append(f.attr)
    # keep build/make/add-ish and dedupe preserving order
    seen, out = set(), []
    for nm in names:
        if nm in seen:
            continue
        seen.add(nm)
        out.append(nm)
    return out


PRIM_RE = re.compile(r'["\']((?:/World/|[A-Za-z_]*(?:Rail|Guard|Wall|Post|Nos|Tact|Sign|Curb|Kerb|Band|Bollard|Fence|Parapet|Coping|Hedge|Bench|Lamp|Light)[A-Za-z0-9_]*))["\']')


def prims_in(src_lines, lo, hi, limit=14):
    out, seen = [], set()
    for i in range(lo - 1, min(hi, len(src_lines))):
        for m in PRIM_RE.finditer(src_lines[i]):
            v = m.group(1)
            if v in seen:
                continue
            seen.add(v)
            out.append(v)
            if len(out) >= limit:
                return out
    return out


def analyse(path):
    src = open(path, encoding="utf-8", errors="replace").read()
    lines = src.splitlines()
    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        return {"error": f"SyntaxError {e}"}

    # --- SCENE_CONFIG defaults --------------------------------------------
    defaults, cfg_lineno = {}, None
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == "SCENE_CONFIG" and isinstance(node.value, ast.Dict):
                    cfg_lineno = node.lineno
                    for k, v in zip(node.value.keys, node.value.values):
                        ks = _const_str(k)
                        if ks is None:
                            continue
                        try:
                            defaults[ks] = ast.literal_eval(v)
                        except Exception:
                            defaults[ks] = "<expr>"
    keys = set(defaults)

    # module-level constants aliasing a key, e.g. KEEP_DRESSING = SCENE_CONFIG.get("keep_dressing", False)
    alias = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            kk = keys_in_test(node.value, keys, {})
            if len(kk) == 1:
                alias[node.targets[0].id] = list(kk)[0]

    # --- reads -------------------------------------------------------------
    f = KeyRefFinder(keys)
    f.visit(tree)
    reads = {k: sorted(set(v)) for k, v in f.refs.items()}
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id in alias:
            reads.setdefault(alias[node.id], []).append(node.lineno)
    for k in reads:
        reads[k] = sorted(set(reads[k]))

    # --- if-guards ---------------------------------------------------------
    guards = defaultdict(list)
    hz_keys = {k for k in keys if k.startswith("hazard_") or k in ("snow_cover", "leaf_cover", "wet_surface")}

    class G(ast.NodeVisitor):
        def __init__(self):
            self.stack = []  # keys of enclosing if-tests

        def visit_If(self, node):
            kk = keys_in_test(node.test, keys, alias)
            neg = "not " in ast.dump(node.test)[:200] or isinstance(node.test, ast.UnaryOp)
            end = max([node.lineno] + [getattr(n, "lineno", node.lineno) for n in ast.walk(node)])
            for k in kk:
                enclosing = [e for lvl in self.stack for e in lvl]
                guards[k].append({
                    "line": node.lineno,
                    "end": end,
                    "negated": bool(neg),
                    "test": ast.get_source_segment(src, node.test) or "",
                    "calls": calls_in(node.body)[:16],
                    "prims": prims_in(lines, node.lineno, end),
                    "inside": sorted(set(enclosing)),
                    "inside_hazard": sorted(set(enclosing) & hz_keys),
                })
            self.stack.append(kk)
            for st in node.body:
                self.visit(st)
            self.stack.pop()
            self.stack.append(set())
            for st in node.orelse:
                self.visit(st)
            self.stack.pop()

    G().visit(tree)

    # ternary / boolean uses outside if-guards
    return {
        "defaults": defaults,
        "cfg_lineno": cfg_lineno,
        "reads": reads,
        "guards": {k: v for k, v in guards.items()},
        "alias": alias,
        "nlines": len(lines),
    }


def main():
    res = {}
    for tag, fn, p in scene_files():
        r = analyse(p)
        r["tag"] = tag
        r["path"] = p
        res[tag + "::" + fn] = r
    json.dump(res, open(sys.argv[1], "w"), indent=1, ensure_ascii=False)
    print(f"scenes analysed: {len(res)}")
    for fn, r in res.items():
        if "error" in r:
            print("  ERR", fn, r["error"])


if __name__ == "__main__":
    main()
