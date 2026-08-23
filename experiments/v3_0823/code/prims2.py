import ast, os, re, json, sys
ROOT="/home/vislab/Desktop/work_sy/Practice_NegObs"
DIRS=[("main","scenes/main"),("batch1","scenes/batch1"),("probe","scenes/probe"),
      ("cueoff_port","experiments/weekend_0823/cue_audit/scenes_cueoff")]
KIT={"scene_common.py","batch1_common.py","probe_common.py","building_kit.py","facade_kit.py",
     "ground_kit.py","infra_kit.py","props_kit.py","stair_kit.py","urban_kit.py","variation_kit.py"}
CUE=["cue_railing","cue_tactile","cue_nosing","cue_material_break","cue_sign","cue_scene_dressing"]
def cs(n): return n.value if isinstance(n,ast.Constant) and isinstance(n.value,str) else None
def bn(n): return n.id if isinstance(n,ast.Name) else (n.attr if isinstance(n,ast.Attribute) else None)

def unparse_str(n):
    """Reconstruct a string-ish literal (Constant / JoinedStr / BinOp+)."""
    if isinstance(n,ast.Constant) and isinstance(n.value,str): return n.value
    if isinstance(n,ast.JoinedStr):
        out=""
        for v in n.values:
            if isinstance(v,ast.Constant) and isinstance(v.value,str): out+=v.value
            else:
                try: out+="{"+ast.unparse(v.value if isinstance(v,ast.FormattedValue) else v)+"}"
                except Exception: out+="{?}"
        return out
    if isinstance(n,ast.BinOp) and isinstance(n.op,ast.Add):
        a,b=unparse_str(n.left),unparse_str(n.right)
        if a is not None and b is not None: return a+b
    if isinstance(n,ast.Name): return "{"+n.id+"}"
    if isinstance(n,ast.Attribute):
        try: return "{"+ast.unparse(n)+"}"
        except Exception: return None
    return None

def prim_strings(node):
    """Prim-path-looking strings under `node`."""
    out=[]
    for n in ast.walk(node):
        s=None
        if isinstance(n,(ast.Constant,ast.JoinedStr)): s=unparse_str(n)
        if not s: continue
        if "/" not in s: continue
        if s.startswith(("./","assets","http")) or s.endswith((".png",".jpg",".usd",".usda",".mdl",".exr")): continue
        if s not in out: out.append(s)
    return out

res={}
for tag,d in DIRS:
    dd=os.path.join(ROOT,d)
    for fn in sorted(os.listdir(dd)):
        if not fn.endswith(".py") or fn in KIT: continue
        p=os.path.join(dd,fn)
        if os.path.islink(p): continue
        src=open(p,encoding="utf-8",errors="replace").read()
        tree=ast.parse(src)
        fdef={}
        for n in ast.walk(tree):
            if isinstance(n,ast.FunctionDef): fdef.setdefault(n.name,[]).append(n)
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
        entry={"defaults":dflt,"keys":{}}
        for key in CUE:
            if key not in dflt: entry["keys"][key]={"declared":False}; continue
            guards=[]
            reads=[]
            for n in ast.walk(tree):
                if isinstance(n,ast.Subscript) and cs(n.slice)==key and bn(n.value) in ("cfg","SCENE_CONFIG"): reads.append(n.lineno)
                if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=="get" and n.args and cs(n.args[0])==key and bn(n.func.value) in ("cfg","SCENE_CONFIG"): reads.append(n.lineno)
                if isinstance(n,ast.If):
                    hit=False
                    for x in ast.walk(n.test):
                        if isinstance(x,ast.Subscript) and cs(x.slice)==key and bn(x.value) in ("cfg","SCENE_CONFIG"): hit=True
                        if isinstance(x,ast.Call) and isinstance(x.func,ast.Attribute) and x.func.attr=="get" and x.args and cs(x.args[0])==key and bn(x.func.value) in ("cfg","SCENE_CONFIG"): hit=True
                    if hit:
                        gend=max(getattr(c,'lineno',n.lineno) for c in ast.walk(n))
                        calls=[]
                        for st in n.body:
                            for x in ast.walk(st):
                                if isinstance(x,ast.Call):
                                    nm=bn(x.func)
                                    if nm and nm not in calls: calls.append(nm)
                        prims=[]
                        for st in n.body: prims += [s for s in prim_strings(st) if s not in prims]
                        for c in calls:
                            for fd in fdef.get(c,[]):
                                prims += [s for s in prim_strings(fd) if s not in prims]
                        guards.append({"L":n.lineno,"end":gend,
                                       "test":(ast.get_source_segment(src,n.test) or "")[:90],
                                       "calls":[c for c in calls if c.startswith(("build","make","_"))][:10],
                                       "prims":prims[:14]})
            entry["keys"][key]={"declared":True,"default":dflt[key],
                                "reads":sorted(set(reads)),"guards":guards}
        res[tag+"::"+fn]=entry
json.dump(res,open("prims2.json","w"),indent=1,ensure_ascii=False)
for name,e in res.items():
    print("="*95); print(name)
    for key in CUE:
        k=e["keys"][key]
        if not k["declared"]: print(f"  {key}: NOT DECLARED"); continue
        if not k["guards"]:
            print(f"  {key}: default={k['default']} NO-IF-GUARD reads={k['reads']}"); continue
        print(f"  {key}: default={k['default']}")
        for g in k["guards"]:
            print(f"     L{g['L']}-{g['end']} if {g['test']}")
            if g['calls']: print(f"        fn: {', '.join(g['calls'])}")
            if g['prims']: print(f"        prims: {' · '.join(g['prims'][:10])}")
