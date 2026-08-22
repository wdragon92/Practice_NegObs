import csv, numpy as np
BASE='experiments/dayrun_0820/runs/v2'
def load(run):
    rows=list(csv.DictReader(open(f'{BASE}/{run}/eval_test/per_frame.csv')))
    cells=[k[2:] for k in rows[0] if k.startswith('p_')]
    return [(r['scene_id'],r['tier'],r['toggle_state'],
             np.array([float(r['p_'+c]) for c in cells]),
             np.array([int(float(r['g_'+c])) for c in cells])) for r in rows]
runs=[f'{m}_s{s}' for m in ('rgb','depth','b2') for s in (42,43,44)]
D={r:load(r) for r in runs}
def fa(rows,tau): 
    s=[r for r in rows if r[2]=='off']; return sum(1 for r in s if (r[3]>=tau).any())/len(s)
def rec(rows,tier,tau):
    s=[r for r in rows if r[1]==tier]; return sum(1 for r in s if (r[3][r[4]==1]>=tau).any())/len(s) if s else None
print("=== B summary: 3-seed mean H recall at matched FA ===")
print(f"{'FA target':>10} {'RGB':>8} {'Depth':>8} {'B2':>8}")
for tgt in (0.359,0.20,0.10,0.05):
    out={}
    for m in ('rgb','depth','b2'):
        hs=[]
        for s in (42,43,44):
            rows=D[f'{m}_s{s}']; tau=next((t for t in np.arange(0.01,1.0,0.01) if fa(rows,t)<=tgt), None)
            hs.append(rec(rows,'H',tau) if tau else np.nan)
        out[m]=np.mean(hs)
    print(f"{tgt:>10.3f} {out['rgb']:8.3f} {out['depth']:8.3f} {out['b2']:8.3f}")
print()
print("=== C. UNCOUNTED negatives: fire rate on none_in_fov on-arm frames (tau=0.5) ===")
print("(hazard exists in the scene but NO positive cell in the 20-cell grid -> every fire is a FP,")
print(" and these frames are in NEITHER the recall denominator NOR the FA denominator)")
print(f"{'run':12} {'none_fire':>10} {'off_FA':>8} {'n':>5}")
for r in runs:
    rows=D[r]; s=[x for x in rows if x[1]=='none_in_fov']
    nf=sum(1 for x in s if (x[3]>=0.5).any())/len(s)
    print(f"{r:12} {nf:10.3f} {fa(rows,0.5):8.3f} {len(s):5d}")
