import ast, os, json
ROOT="/home/vislab/Desktop/work_sy/Practice_NegObs"
DIRS=[("main","scenes/main"),("batch1","scenes/batch1"),("probe","scenes/probe"),
      ("cueoff_port","experiments/weekend_0823/cue_audit/scenes_cueoff")]
KIT={"scene_common.py","batch1_common.py","probe_common.py","building_kit.py","facade_kit.py",
     "ground_kit.py","infra_kit.py","props_kit.py","stair_kit.py","urban_kit.py","variation_kit.py"}
CUE=["cue_railing","cue_tactile","cue_nosing","cue_material_break","cue_sign","cue_scene_dressing"]
def cs(n): return n.value if isinstance(n,ast.Constant) and isinstance(n.value,str) else None
def bn(n): return n.id if isinstance(n,ast.Name) else (n.attr if isinstance(n,ast.Attribute) else None)

def key_in(test, keys):
    got=set()
    for x in ast.walk(test):
        if isinstance(x,ast.Subscript) and cs(x.slice) in keys and bn(x.value) in ("cfg","SCENE_CONFIG"): got.add(cs(x.slice))
        if isinstance(x,ast.Call) and isinstance(x.func,ast.Attribute) and x.func.attr=="get" and x.args and cs(x.args[0]) in keys and bn(x.func.value) in ("cfg","SCENE_CONFIG"): got.add(cs(x.args[0]))
    return got

out={}
for tag,d in DIRS:
    dd=os.path.join(ROOT,d)
    for fn in sorted(os.listdir(dd)):
        if not fn.endswith(".py") or fn in KIT: continue
        p=os.path.join(dd,fn)
        if os.path.islink(p): continue
        src=open(p,encoding="utf-8",errors="replace").read(); tree=ast.parse(src)
        dflt={}
        for n in ast.walk(tree):
            if isinstance(n,ast.Assign):
                for t in n.targets:
                    if isinstance(t,ast.Name) and t.id=="SCENE_CONFIG" and isinstance(n.value,ast.Dict):
                        for k,v in zip(n.value.keys,n.value.values):
                            ks=cs(k)
                            if ks:
                                try: dflt[ks]=ast.literal_eval(v)
                                except Exception: dflt[ks]="?"
        HZ={k for k in dflt if k.startswith("hazard_")}
        # local var aliases for hazard (e.g. hazard = cfg["hazard_stairs"])
        halias=set()
        for n in ast.walk(tree):
            if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name):
                if key_in(n.value,HZ): halias.add(n.targets[0].id)
        def is_hz_test(t):
            if key_in(t,HZ): return True
            for x in ast.walk(t):
                if isinstance(x,ast.Name) and x.id in halias: return True
            return False
        # annotate: for every node, (enclosing_func_stack, hazard_gated_lexically)
        info={}   # id(node) -> dict
        calls_in_hz={}   # funcname -> list of bool (hazard-gated call site?)
        cueguard=[]      # (key, lineno, enclosing_func, hz_lex)
        def visit(ch, fstack, hz):
            """Process ONE node `ch` then recurse into its children."""
            nf, nh = fstack, hz
            if isinstance(ch, ast.FunctionDef):
                nf = fstack + [ch.name]; nh = False
                for st in ch.body: visit(st, nf, nh)
                return
            if isinstance(ch, ast.If):
                thz = is_hz_test(ch.test)
                body_hz = hz or thz
                for k in key_in(ch.test, set(CUE)):
                    cueguard.append((k, ch.lineno, fstack[-1] if fstack else "<module>", body_hz))
                for x in ast.walk(ch.test):
                    if isinstance(x, ast.Call):
                        nm = bn(x.func)
                        if nm: calls_in_hz.setdefault(nm, []).append(hz)
                for st in ch.body:   visit(st, fstack, body_hz)
                for st in ch.orelse: visit(st, fstack, hz)
                return
            if isinstance(ch, ast.Call):
                nm = bn(ch.func)
                if nm: calls_in_hz.setdefault(nm, []).append(hz)
            for sub in ast.iter_child_nodes(ch):
                visit(sub, nf, nh)

        def walk(node, fstack, hz):
            for ch in ast.iter_child_nodes(node): visit(ch, fstack, hz)
        walk(tree, [], False)
        # fixpoint: function is hazard-gated if it exists and ALL its call sites are hazard-gated
        fnames={n.name for n in ast.walk(tree) if isinstance(n,ast.FunctionDef)}
        gated={f for f in fnames if f in calls_in_hz and calls_in_hz[f] and all(calls_in_hz[f])}
        for _ in range(4):
            newg=set(gated)
            for f in fnames:
                sites=calls_in_hz.get(f)
                if not sites: continue
                if all(sites): newg.add(f)
            if newg==gated: break
            gated=newg
        rec={}
        for k in CUE:
            gs=[g for g in cueguard if g[0]==k]
            if not gs: rec[k]=None; continue
            allg = all(g[3] or (g[2] in gated) for g in gs)
            anyg = any(g[3] or (g[2] in gated) for g in gs)
            rec[k]={"n":len(gs),"all_hazard_gated":allg,"any":anyg,
                    "sites":[{"L":g[1],"fn":g[2],"lex_hz":g[3],"fn_gated":g[2] in gated} for g in gs]}
        out[tag+"::"+fn]={"defaults":dflt,"hazard_keys":sorted(HZ),"cue":rec}
json.dump(out,open("hazgate.json","w"),indent=1,ensure_ascii=False)
for n,e in out.items():
    tags=[]
    for k in CUE:
        r=e["cue"][k]
        if r is None: tags.append(f"{k[4:]}:-")
        else: tags.append(f"{k[4:]}:{'HZ' if r['all_hazard_gated'] else ('hz?' if r['any'] else 'free')}")
    print(f"{n:50s} hz={','.join(e['hazard_keys']):22s} " + " ".join(f"{t:20s}" for t in tags))
