"""hazgate.py — 씬 소스에서 `cue_*` 배선을 정적으로 수집한다.

두 모드 (W1-B2 · DECISIONS D75 ③)
---------------------------------
`--mode ifonly` (**기본 · 옛 동작 그대로**)
    cue 읽기를 **`if` 문의 조건절에서만** 수집한다. W0 프로브 → W1-D 재판정 →
    W1D §6.6 레버표 → W1-B 레시피가 전부 이 모드의 산출(`hazgate.json`)에서
    나왔으므로, 그 계보를 재현하려면 이 모드를 그대로 쓴다.

`--mode full` (**W1-B2 수리본**)
    cue 읽기를 **모든 표현식 문맥**에서 수집한다 — 삼항식
    (`mtl = A if cfg["cue_material_break"] else B`), `cfg.get(...)` 호출,
    불린 연산, 인자 등. 각 자리의 `hz`(위험 게이트 여부)는 **어휘적으로 그
    자리를 감싸는 `if` 사슬**로 판정하며, 이는 ifonly 모드의 의미와 같다.
    산출은 기본적으로 **다른 파일**(`hazgate_full.json`)에 쓴다 — w0/w1 원장은
    `hazgate.json`을 계속 가리키고, 두 파일이 나란히 남아 차이를 감사할 수 있다.

왜 필요한가 (W1B_REPORT §8.1)
-----------------------------
ifonly 모드는 라이브러리 전체에서 **23쌍**(`cue_material_break` 20 ·
`cue_tactile` 2 · `cue_nosing` 1)을 "배선無"로 오기록했고, 그 손실이 4단계를
타고 B팔 레시피에 도달해 **T키의 |r|이 0.31로 문턱 0.2를 넘겼다**.

사용:
    cd experiments/v3_0823/code
    python3 hazgate.py                       # -> hazgate.json      (옛 동작)
    python3 hazgate.py --mode full           # -> hazgate_full.json (수리본)
    python3 hazgate.py --mode full --out X   # 임의 경로
"""
import argparse, ast, os, json, sys
ROOT="/home/vislab/Desktop/work_sy/Practice_NegObs"
DIRS=[("main","scenes/main"),("batch1","scenes/batch1"),("probe","scenes/probe"),
      ("cueoff_port","experiments/weekend_0823/cue_audit/scenes_cueoff")]
KIT={"scene_common.py","batch1_common.py","probe_common.py","building_kit.py","facade_kit.py",
     "ground_kit.py","infra_kit.py","props_kit.py","stair_kit.py","urban_kit.py","variation_kit.py"}
CUE=["cue_railing","cue_tactile","cue_nosing","cue_material_break","cue_sign","cue_scene_dressing"]

_ap=argparse.ArgumentParser()
_ap.add_argument("--mode",choices=("ifonly","full"),default="ifonly")
_ap.add_argument("--out",default=None)
_A=_ap.parse_args()
FULL=(_A.mode=="full")
OUTP=_A.out or ("hazgate_full.json" if FULL else "hazgate.json")

def cs(n): return n.value if isinstance(n,ast.Constant) and isinstance(n.value,str) else None
def bn(n): return n.id if isinstance(n,ast.Name) else (n.attr if isinstance(n,ast.Attribute) else None)

def _read_key(x, keys):
    """`x` 자체가 cfg/SCENE_CONFIG의 cue 읽기이면 그 키, 아니면 None."""
    if isinstance(x,ast.Subscript) and cs(x.slice) in keys and bn(x.value) in ("cfg","SCENE_CONFIG"):
        return cs(x.slice)
    if isinstance(x,ast.Call) and isinstance(x.func,ast.Attribute) and x.func.attr=="get" \
       and x.args and cs(x.args[0]) in keys and bn(x.func.value) in ("cfg","SCENE_CONFIG"):
        return cs(x.args[0])
    return None

def key_in(test, keys):
    got=set()
    for x in ast.walk(test):
        k=_read_key(x,keys)
        if k: got.add(k)
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
            # --- full 모드: `if` 조건절 밖의 cue 읽기도 센다 (W1-B2 · D75 ③) ----
            # `ch` 자신만 본다 — 자식은 아래 재귀에서 각자 한 번씩 방문되므로
            # 자리마다 정확히 한 번 기록된다. `ast.If`의 test는 아래 If 분기가
            # 따로 처리하고 재귀하지 않으므로 중복 기록도 없다.
            if FULL:
                k = _read_key(ch, set(CUE))
                if k:
                    cueguard.append((k, getattr(ch, "lineno", -1),
                                     fstack[-1] if fstack else "<module>", hz))
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
out["__meta__"]={"doc":"hazgate","mode":_A.mode,
                 "scan":("`if` 문 조건절만" if not FULL else
                         "모든 표현식 문맥 (삼항식·cfg.get·불린·인자 포함)"),
                 "authority":"W1B_REPORT §8.1 · DECISIONS D75 ③",
                 "note":("옛 계보(W0→W1D §6.6→W1-B 레시피)의 정본" if not FULL
                         else "W1-B2 수리본 — hazgate.json과 나란히 두고 감사한다")}
json.dump(out,open(OUTP,"w"),indent=1,ensure_ascii=False)
print(f"[hazgate] mode={_A.mode} -> {OUTP}")
for n,e in out.items():
    if "::" not in n: continue          # __meta__
    tags=[]
    for k in CUE:
        r=e["cue"][k]
        if r is None: tags.append(f"{k[4:]}:-")
        else: tags.append(f"{k[4:]}:{'HZ' if r['all_hazard_gated'] else ('hz?' if r['any'] else 'free')}")
    print(f"{n:50s} hz={','.join(e['hazard_keys']):22s} " + " ".join(f"{t:20s}" for t in tags))
