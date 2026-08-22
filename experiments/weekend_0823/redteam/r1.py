import csv, glob, os, numpy as np
BASE='experiments/dayrun_0820/runs/v2'
def load(run):
    p=f'{BASE}/{run}/eval_test/per_frame.csv'
    rows=list(csv.DictReader(open(p)))
    cells=[k[2:] for k in rows[0] if k.startswith('p_')]
    out=[]
    for r in rows:
        pv=np.array([float(r['p_'+c]) for c in cells])
        gv=np.array([int(float(r['g_'+c])) for c in cells])
        out.append((r['scene_id'], r['tier'], r['toggle_state'], pv, gv))
    return out
def recall(rows,tier,tau,scene=None):
    sel=[r for r in rows if r[1]==tier and (scene is None or r[0]==scene)]
    if not sel: return None,0
    hit=sum(1 for r in sel if (r[3][r[4]==1]>=tau).any())
    return hit/len(sel), len(sel)
def fa(rows,tau,scene=None):
    sel=[r for r in rows if r[2]=='off' and (scene is None or r[0]==scene)]
    if not sel: return None,0
    f=sum(1 for r in sel if (r[3]>=tau).any())
    return f/len(sel), len(sel)

runs=[f'{m}_s{s}' for m in ('rgb','depth','b2') for s in (42,43,44)]
print("=== A. per-scene H recall vs SAME-scene off-arm FA (tau=0.5) ===")
print(f"{'run':12} {'s14_Hrec':>9}{'s14_offFA':>10} {'s15_Hrec':>9}{'s15_offFA':>10} {'allH':>7}{'allFA':>7}")
for run in runs:
    rows=load(run)
    a=recall(rows,'H',0.5,'scene14')[0]; b=fa(rows,0.5,'scene14')[0]
    c=recall(rows,'H',0.5,'scene15')[0]; d=fa(rows,0.5,'scene15')[0]
    e=recall(rows,'H',0.5)[0]; f=fa(rows,0.5)[0]
    print(f"{run:12} {a:9.3f}{b:10.3f} {c:9.3f}{d:10.3f} {e:7.3f}{f:7.3f}")

print()
print("=== B. FA-matched H recall (per-run tau chosen so overall off-arm frame FA <= target) ===")
for target in (0.20,0.10,0.05):
    print(f"-- target FA <= {target} --")
    for run in runs:
        rows=load(run)
        taus=np.arange(0.01,1.00,0.01)
        best=None
        for t in taus:
            f=fa(rows,t)[0]
            if f<=target: best=t; break
        if best is None: print(f"{run:12} unreachable"); continue
        h=recall(rows,'H',best)[0]; v=recall(rows,'V',best)[0]; f=fa(rows,best)[0]
        print(f"{run:12} tau={best:.2f}  H={h:.3f}  V={v:.3f}  FA={f:.3f}")
