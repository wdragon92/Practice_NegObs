"""FA-MATCHED comparison: new encoders (resnet50, tu-convnext_tiny) vs the
canonical resnet34 RGB baseline.  D51 mandate: convnext's tau=0.5 operating point
is degenerate (H high because FA is high), so the ONLY honest presentation is at
matched off-arm false-alarm rate.

Read-only.  Reuses the exact rule of rt_response/code/f1_fa_matched.py
(D35 / R1-F1): tau from the empirical order statistics of the off-arm per-frame
max probability; frame recall = any GT-positive cell with p >= tau.

Inputs
  baseline : experiments/dayrun_0820/runs/v2/rgb_s{42,43,44}/eval_test/per_frame.csv
  new      : experiments/weekend_0823/newmodels/runs/{resnet50,tu-convnext_tiny}_s{42,43,44}/eval_test/per_frame.csv

Outputs
  newmodels/FA_MATCHED.md
  newmodels/fa_matched.json
"""
import csv
import json
import os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SEEDS = (42, 43, 44)
TARGETS = [0.359, 0.20, 0.10, 0.05]

ARMS = {
    "resnet34 (baseline, RGB)": [
        os.path.join(REPO, f"experiments/dayrun_0820/runs/v2/rgb_s{s}/eval_test/per_frame.csv")
        for s in SEEDS],
    "resnet50 (RGB)": [
        os.path.join(HERE, f"runs/resnet50_s{s}/eval_test/per_frame.csv") for s in SEEDS],
    "convnext_tiny (RGB)": [
        os.path.join(HERE, f"runs/tu-convnext_tiny_s{s}/eval_test/per_frame.csv") for s in SEEDS],
}
SHORT = {"resnet34 (baseline, RGB)": "resnet34", "resnet50 (RGB)": "resnet50",
         "convnext_tiny (RGB)": "convnext_tiny"}


def load_per_frame(path):
    rows = list(csv.DictReader(open(path)))
    cells = [k[2:] for k in rows[0] if k.startswith("p_")]
    return [dict(frame_id=r["frame_id"], scene_id=r["scene_id"], tier=r["tier"],
                 toggle=r["toggle_state"],
                 p=np.array([float(r["p_" + c]) for c in cells]),
                 g=np.array([int(float(r["g_" + c])) for c in cells])) for r in rows]


def max_on_gt(rows, tier):
    sel = [r for r in rows if r["tier"] == tier and r["g"].sum() > 0]
    return np.array([r["p"][r["g"] == 1].max() for r in sel])


def max_off_any(rows):
    return np.array([r["p"].max() for r in rows if r["toggle"] == "off"])


def tau_for_fa_exact(off_max, target):
    """Identical to rt_response/code/common_rt.py:tau_for_fa_exact."""
    n = len(off_max)
    s = np.sort(off_max)[::-1]
    k = int(np.floor(target * n + 1e-9))
    if k >= n:
        return 0.0, 1.0
    tau = np.nextafter(s[k], np.inf)
    return float(tau), float((off_max >= tau).mean())


def mean_hr(v):
    return float(np.mean(v))


def halfrange(v):
    return float((max(v) - min(v)) / 2)


res = {"targets": TARGETS, "runs": {}, "arm_mean": {}, "provenance": {
    "rule": "exact-quantile tau on off-arm per-frame max prob (rt_response/code/common_rt.py)",
    "recall_rule": "frame recall = any GT-positive cell with p >= tau",
    "fa_rule": "off-arm frame FA = any of 20 cells with p >= tau",
    "inputs": {k: [os.path.relpath(p, REPO) for p in v] for k, v in ARMS.items()},
}}

for arm, paths in ARMS.items():
    per_seed = []
    for s, path in zip(SEEDS, paths):
        rows = load_per_frame(path)
        off = max_off_any(rows)
        on = {t: max_on_gt(rows, t) for t in ("V", "E", "H")}
        e = {"n_off": len(off), "n": {t: len(v) for t, v in on.items()},
             "tau_op_0.5": {"FA": float((off >= 0.5).mean()),
                            **{t: float((v >= 0.5).mean()) for t, v in on.items()}},
             "exact": {}}
        for tgt in TARGETS:
            tau, fa = tau_for_fa_exact(off, tgt)
            e["exact"][str(tgt)] = {"tau": tau, "FA": fa,
                                    **{t: float((v >= tau).mean()) for t, v in on.items()}}
        res["runs"][f"{SHORT[arm]}_s{s}"] = e
        per_seed.append(e)
    am = {"tau_op_0.5": {}, "exact": {}}
    for k in ("FA", "H", "E", "V"):
        vals = [p["tau_op_0.5"][k] for p in per_seed]
        am["tau_op_0.5"][k] = {"mean": mean_hr(vals), "half_range": halfrange(vals),
                               "per_seed": vals}
    for tgt in TARGETS:
        cells = [p["exact"][str(tgt)] for p in per_seed]
        am["exact"][str(tgt)] = {k: {"mean": mean_hr([c[k] for c in cells]),
                                     "half_range": halfrange([c[k] for c in cells]),
                                     "per_seed": [c[k] for c in cells]}
                                 for k in ("tau", "FA", "H", "E", "V")}
    res["arm_mean"][arm] = am

json.dump(res, open(os.path.join(HERE, "fa_matched.json"), "w"), indent=1)


def f(x, nd=3):
    return f"{x:.{nd}f}"


BASE = "resnet34 (baseline, RGB)"
L = []
L.append("# FA-MATCHED — new encoders vs the canonical resnet34 RGB baseline\n")
L.append("**목적 한 줄.** D51이 남긴 숙제 — convnext_tiny의 τ=0.5 작동점은 "
         "'H가 높다'가 아니라 '거의 항상 발화한다'이므로, 세 인코더를 **같은 오경보 예산**에 "
         "세워야만 비교가 정직해진다. 이 문서가 그 표다.\n")
L.append("**작성/재현**: `experiments/weekend_0823/newmodels/fa_matched.py` (CPU, read-only). "
         "규칙은 레드팀 대응 F1(`rt_response/code/f1_fa_matched.py`, D35/R1-F1)과 **동일**: "
         "off팔 프레임 최대확률의 경험분위수에서 τ를 잡고(0.01 격자 없음), 그 τ에서 recall을 읽는다.\n")
L.append("**입력** (전부 동결 산출물, test 7씬 816행 = hazard-ON 408 + off 408; "
         "H n=96 · E n=45 · V n=180):\n")
for arm, paths in ARMS.items():
    L.append(f"- {arm}: `{os.path.relpath(os.path.dirname(os.path.dirname(paths[0])), REPO)}` 외 2시드")
L.append("\n**용어**: 프레임 recall = GT 양성 셀 중 하나라도 p ≥ τ. "
         "off팔 프레임 FA = 20칸 중 하나라도 p ≥ τ. 재훈련·재렌더·정본 수정 없음.\n")

L.append("\n## 1. 헤드라인 — FA-정합 H recall (3시드 평균 ± 반범위)\n")
L.append("| 정합 FA | resnet34 (기준) | resnet50 | convnext_tiny | Δ(r50−r34) | Δ(convnext−r34) |")
L.append("|---|---|---|---|---|---|")
for tgt in TARGETS:
    c = {a: res["arm_mean"][a]["exact"][str(tgt)] for a in ARMS}
    b = c[BASE]["H"]["mean"]
    r5 = c["resnet50 (RGB)"]["H"]["mean"]
    cx = c["convnext_tiny (RGB)"]["H"]["mean"]
    L.append(f"| {tgt:.3f} | {f(b)} ±{f(c[BASE]['H']['half_range'])} | "
             f"{f(r5)} ±{f(c['resnet50 (RGB)']['H']['half_range'])} | "
             f"{f(cx)} ±{f(c['convnext_tiny (RGB)']['H']['half_range'])} | "
             f"{r5 - b:+.3f} | {cx - b:+.3f} |")

L.append("\n달성 FA (세 팔 모두 목표 바로 아래, 해상도 1/408 = 0.0025):\n")
L.append("| 정합 FA | resnet34 | resnet50 | convnext_tiny |")
L.append("|---|---|---|---|")
for tgt in TARGETS:
    c = {a: res["arm_mean"][a]["exact"][str(tgt)] for a in ARMS}
    L.append(f"| {tgt:.3f} | {f(c[BASE]['FA']['mean'])} | {f(c['resnet50 (RGB)']['FA']['mean'])} | "
             f"{f(c['convnext_tiny (RGB)']['FA']['mean'])} |")

L.append("\n## 2. 왜 τ=0.5 표를 쓰면 안 되는가 (무정합 작동점)\n")
L.append("| 팔 | H | E | V | off팔 FA |")
L.append("|---|---|---|---|---|")
for arm in ARMS:
    t = res["arm_mean"][arm]["tau_op_0.5"]
    L.append(f"| {arm} | {f(t['H']['mean'])} ±{f(t['H']['half_range'])} | {f(t['E']['mean'])} | "
             f"{f(t['V']['mean'])} | {f(t['FA']['mean'])} |")
cx_fa = res["arm_mean"]["convnext_tiny (RGB)"]["tau_op_0.5"]["FA"]
b_fa = res["arm_mean"][BASE]["tau_op_0.5"]["FA"]
L.append(f"\nconvnext_tiny는 H를 **FA {f(cx_fa['mean'])}**에서 읽고 resnet34는 "
         f"**FA {f(b_fa['mean'])}**에서 읽는다 — 같은 열에 인쇄하면 "
         f"{cx_fa['mean'] / b_fa['mean']:.2f}배 오경보 차이가 숨는다. "
         f"시드별 convnext FA = {', '.join(f(v) for v in cx_fa['per_seed'])} "
         f"(s43은 전 지표 1.000 = 상시발화).\n")

L.append("\n## 3. 시드별 상세 (exact 규칙)\n")
L.append("| 목표 FA | 런 | τ | 달성 FA | H | E | V |")
L.append("|---|---|---|---|---|---|---|")
for tgt in TARGETS:
    for arm in ARMS:
        for s in SEEDS:
            c = res["runs"][f"{SHORT[arm]}_s{s}"]["exact"][str(tgt)]
            L.append(f"| {tgt:.3f} | {SHORT[arm]}_s{s} | {c['tau']:.4f} | {f(c['FA'])} | "
                     f"{f(c['H'])} | {f(c['E'])} | {f(c['V'])} |")

L.append("\n## 4. 다른 티어도 같은 예산에서 (E·V)\n")
L.append("| 정합 FA | r34 V | r50 V | cnx V | r34 E | r50 E | cnx E |")
L.append("|---|---|---|---|---|---|---|")
for tgt in TARGETS:
    c = {a: res["arm_mean"][a]["exact"][str(tgt)] for a in ARMS}
    L.append("| %.3f | %s | %s | %s | %s | %s | %s |" % (
        tgt,
        f(c[BASE]["V"]["mean"]), f(c["resnet50 (RGB)"]["V"]["mean"]),
        f(c["convnext_tiny (RGB)"]["V"]["mean"]),
        f(c[BASE]["E"]["mean"]), f(c["resnet50 (RGB)"]["E"]["mean"]),
        f(c["convnext_tiny (RGB)"]["E"]["mean"])))

L.append("\n## 5. 진단 — convnext 두 시드는 '아키텍처 결과'가 아니라 **훈련 실패**다\n")
L.append("FA-정합 표만 보면 'convnext가 약하다'로 읽히지만, 원인은 인코더가 아니다. "
         "off팔 프레임 최대확률의 분포 폭을 재면 다음과 같다.\n")
L.append("| 런 | off-max 최소 | 중앙값 | 최대 | 폭 | 전 20칸 셀별 표준편차 평균 |")
L.append("|---|---|---|---|---|---|")
for arm in ARMS:
    for s in SEEDS:
        path = dict(zip(SEEDS, ARMS[arm]))[s]
        rows = load_per_frame(path)
        off = max_off_any(rows)
        P = np.stack([r["p"] for r in rows])
        L.append(f"| {SHORT[arm]}_s{s} | {off.min():.6f} | {np.median(off):.6f} | {off.max():.6f} | "
                 f"{off.max() - off.min():.2e} | {P.std(axis=0).mean():.2e} |")
L.append("\n**convnext_s42·s43은 입력과 무관하게 거의 상수를 출력한다.** "
         "off팔 408프레임의 최대확률이 s42는 0.501409–0.501490(폭 8e-5), s43은 0.631690–0.631894"
         "(폭 2e-4) 안에 전부 들어간다. 셀별 표준편차도 1e-5 수준 — 그림을 바꿔도 출력이 안 바뀐다.\n")
L.append("훈련 로그가 같은 말을 한다 (`runs/<run>/metrics.csv`):\n")
L.append("| 런 | 총 epoch | 선택된 epoch | 그 epoch의 val_f1 | val_H recall | 종료 |")
L.append("|---|---|---|---|---|---|")
for arm in ("resnet50 (RGB)", "convnext_tiny (RGB)"):
    for s in SEEDS:
        mpath = os.path.join(HERE, f"runs/{'resnet50' if 'resnet50' in arm else 'tu-convnext_tiny'}_s{s}/metrics.csv")
        rs = list(csv.DictReader(open(mpath)))
        b = max(rs, key=lambda r: float(r["sel_score"]))
        L.append(f"| {SHORT[arm]}_s{s} | {len(rs)} | {b['epoch']} | {float(b['val_f1']):.3f} | "
                 f"{float(b['val_h_recall']):.3f} | early_stop |")
L.append("\n- **convnext_s43은 epoch 1의 체크포인트가 선택됐다.** 1 에폭짜리 모델이다.\n"
         "- 선택 지표는 `0.5·val_f1 + 0.5·val_H_frame_recall`이고 "
         "**val의 strict-H 프레임은 6장뿐이다**(`runs/*/config.json::n_val_strict_h = 6`). "
         "6장짜리 분모에서 H recall은 0 / .167 / .333 / .5 / .833 / 1.0의 여섯 단계로만 움직이는 "
         "동전 던지기이고, 그 항이 지표의 절반을 차지한다. **'전부 발화'하면 H recall = 1.0이 "
         "공짜로 나오므로, 지표는 상시발화 체크포인트를 적극적으로 선호한다.**\n"
         "- 이 선택 규칙은 레시피 v2의 것이고 resnet34 기준선도 **똑같이** 썼다. 즉 이것은 "
         "신규모델의 결함이 아니라 **레시피의 알려진 약점**이며, 덜 안정적인 인코더에서 먼저 터진 것이다.\n")
L.append("\n### 5.1 그래서 convnext에 대해 말할 수 있는 것과 없는 것\n")
L.append("| 말할 수 있다 | 말할 수 없다 |\n|---|---|")
L.append("| 이 레시피·이 선택 지표로 convnext_tiny를 돌리면 3시드 중 2시드가 상수 출력으로 붕괴했다 | "
         "convnext_tiny 아키텍처가 이 과제에 부적합하다 |")
L.append("| 붕괴하지 않은 유일한 시드(s44)도 FA-정합 전 지점에서 resnet34보다 낮다 | "
         "n=1로 아키텍처 순위를 매길 수 있다 |")
L.append("| 선택 지표의 H 항이 6프레임 분모라 상시발화를 보상한다 | "
         "붕괴가 인코더 탓인지 학습률·스케줄 탓인지 |")
L.append("\n**논문 처리 권고**: convnext 행은 **아키텍처 비교로 인쇄하지 않는다.** "
         "부록에 넣는다면 표제를 '동일 레시피 이식 시의 훈련 안정성'으로 달고 §5의 붕괴 진단을 "
         "함께 싣는다. τ=0.5 무정합 수치(H .63–1.0)는 **어떤 형태로도 인용 금지**다.\n")

L.append("\n## 6. 한 줄 판정\n")
L.append("> **같은 오경보 예산에 세우면 두 신규 인코더 모두 resnet34 기준선보다 낮다** — "
         "resnet50 −0.19 ~ −0.25, convnext −0.21 ~ −0.37 (FA .05–.359 전 지점). "
         "**용량을 키우거나 계열을 바꿔서 얻은 H recall은 없다.** "
         "덧붙여 convnext의 겉보기 고성능(τ0.5에서 H .82)은 FA 0.909의 상시발화이고, "
         "3시드 중 2시드는 상수 출력으로 붕괴한 훈련 실패다.\n")
L.append("이는 D51의 잠정 서술 \"resnet50 ≈ resnet34 동급\"을 **정정한다**: "
         "τ0.5 무정합에서 비슷해 보였을 뿐이고, 오경보를 맞추면 resnet50이 명확히 아래다. "
         "D45가 던진 질문 \"cue 학습이 백본 용량·계열에 일반적인가\"의 답은 "
         "**\"이 레시피에서 인코더를 바꿔 얻는 것은 없다 — 표는 resnet34 3행 그대로 간다\"**이다.\n")

open(os.path.join(HERE, "FA_MATCHED.md"), "w").write("\n".join(L) + "\n")
print("\n".join(L[-40:]))
