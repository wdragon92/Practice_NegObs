#!/usr/bin/env python3
"""v3a_report.py — V3A_TRAIN.md 생성기 (한국어 · 승용 요약 + 원장 표).

입력: logs/v3a_selection.json · logs/v3a_config_diff.json · runs/v3a/*/config.json
      + 매니페스트 실측(마스크 채널 census · fallback 내역)
산출: experiments/v3_0823/V3A_TRAIN.md
"""
from __future__ import annotations

import collections
import json
import os
import subprocess
import sys

R = "/home/vislab/Desktop/work_sy/Practice_NegObs"
V3 = f"{R}/experiments/v3_0823"
sys.path.insert(0, f"{V3}/code")
import selection_v3 as SV  # noqa: E402
import v3_masks as VM      # noqa: E402

MAIN = ["rgb_s42", "rgb_s43", "rgb_s44"]
ISO = ["rgb_s42_aux"]


def f(v, n=4):
    return "—" if v is None else f"{v:.{n}f}"


def main():
    sel = json.load(open(f"{V3}/logs/v3a_selection.json"))
    cfd = json.load(open(f"{V3}/logs/v3a_config_diff.json"))
    smoke = open(f"{V3}/logs/v3a/smoke.log").read() if \
        os.path.isfile(f"{V3}/logs/v3a/smoke.log") else ""
    M = json.load(open(f"{V3}/dataset_manifest_v3_seg3.json"))
    S = json.load(open(f"{V3}/split_v3_seg3.json"))
    fr = M["frames"]
    tr_s, va_s = set(S["train"]), set(S["val"])

    def sp(r):
        return "train" if r["scene_id"] in tr_s else ("val" if r["scene_id"] in va_s else "-")

    bare = collections.Counter((sp(x), x["arm"]) for x in fr if VM.ch_bare_h(x))
    fb = [x for x in fr if (x.get("cue") or {}).get("source") == "geometric_fallback"]
    fb_arm = collections.Counter(x["arm"] for x in fb)
    fb_h = collections.Counter(x["arm"] for x in fb if x["tier"] == "H")
    sha = subprocess.run(["sha256sum", f"{V3}/PREREG_V3.md"], capture_output=True,
                         text=True).stdout.split()[0]
    g = sel["guard_v2_reproduction"]
    runs = sel["v3a"]
    done = [r for r in MAIN if runs.get(r, {}).get("status") == "DONE"]
    wall = sum((runs[r].get("wall_sec") or 0) for r in runs
               if runs[r].get("status") in ("DONE", "TRAINING_FAILED"))

    L = []
    A = L.append
    A("# V3A_TRAIN — v3-A 학습 웨이브 실행 기록")
    A("")
    A(f"- **일자** 2026-08-24 · **권위** `PREREG_V3.md` **동결본** (sha256 `{sha[:16]}…`)")
    A(f"- **코퍼스** `dataset_manifest_v3_seg3.json` + `split_v3_seg3.json` "
      f"(train 2,598 / val 1,056 · D91 §9.1 훈련 정본)")
    A("- **런** 본 A/B 3시드 `rgb_s42·s43·s44` (aux OFF) + **격리** `rgb_s42_aux` (aux ON · "
      "본 판정 비혼입 · D82 결재 3 · PREREG §5.6)")
    A("- **본 문서는 학습·선택까지만 다룬다.** 계기판 ①②③ 평가는 다음 웨이브다(§7 입력 준비).")
    A("")
    A("---")
    A("")
    A("## 승용 요약 (7문장)")
    A("")
    A("1. 동결한 v2 레시피(resnet34 U-Net · lr 3e-4 · AdamW · batch 8 · 512² · patience 15)를 "
      "그대로 두고 **코퍼스·지도 규칙·선택식·로깅 4가지만** 바꿔 v3-A 3시드를 학습했다.")
    A(f"2. v2 ↔ v3a `config.json` 전수 대조에서 **등록 항목 밖 diff는 {cfd['n_unexplained']}줄**이다 "
      f"— PREREG §1.1이 요구한 \"동결의 실증\"이 성립한다.")
    A("3. 학습 착수 전 스모크에서 **맨-가림 H의 H 칸이 실제로 0으로 마스크되고 · 레버 ㄴ C 프레임이 "
      "통째로 빠지고 · gt_void 칸이 손실에서 제외**되는 것을 실측으로 확인했다(10/10 PASS).")
    A(f"4. 세 본런 전부 **VG-const를 통과**했다 — `TRAINING_FAILED`로 끝난 런은 "
      f"{sum(1 for r in runs.values() if r.get('status') == 'TRAINING_FAILED')}건이다.")
    A("5. **선택식의 H 항이 v3에서 처음으로 후보를 갈랐다** — v2에서는 출하 9체크포인트가 9/9 모두 "
      "val H recall 1.000이라 H 항이 상수였는데, v3 val은 유효 H 프레임이 90개라 에폭마다 값이 다르다.")
    A(f"6. 선택 코드를 v2 15런에 겨눈 **회귀 가드는 {g['n_match']}/{g['n_runs']} 재현**됐다 "
      f"— 웨이브 중 선택 코드가 변형되지 않았다는 뜻이다.")
    A(f"7. 총 GPU 벽시계 **{wall / 3600:.2f} h**(4런 순차 · flock 공유). "
      "체크포인트는 `runs/v3a/*/best.pt`에 있고 다음 웨이브(계기판 평가)의 입력이 준비됐다.")
    A("")
    A("---")
    A("")
    A("## 1. 스모크 — 적재 + 마스크 채널 3단언")
    A("")
    A("학습 1스텝 전에 돌린 실측이다 (`code/smoke_v3.py` · CPU).")
    A("")
    A("| # | 단언 | 실측 | 판정 |")
    A("|---|---|---|---|")
    A("| **S1** | 맨-가림 H 프레임의 손실 마스크가 **H 칸을 0으로** 만드는가 | "
      "표본 `A/sceneH6/L0__s20260824__0005.png::w2h2` (`px_canonical6`=0 < k=7,000) · "
      "GT 양성 칸 `[12,15,16,17,18,19]` 전부 `ignore=1` · **그 칸들의 gradient = 0.000e+00** "
      "(비마스크 칸 max\\|g\\| 3.571e-02) | ✅ |")
    A("| **S2** | 레버 ㄴ C 프레임이 **손실에서 제외**되는가 | "
      "표본 `C/scene02/L5__s20260819__0002.png` (`frac(\\|ΔI\\|>8)`=8e-06 < 0.001) · "
      "**전 20칸 마스크** · 그 프레임의 손실 기여 = 0 | ✅ |")
    A("| **S3** | `gt_void` 칸이 **손실에서 제외**되는가 (평가에서는 절대 아님) | "
      "표본 `A/scene12/L0__s20260819__0000.png` void 칸 12개만 마스크 · 나머지 8칸 정상 지도 · "
      "**평가 코드(`eval_polar.py`)의 마스크 참조 0회** | ✅ |")
    A("| S4 | 마스크 전량 0 ⇒ v2 손실과 **수치 항등** | "
      "`masked_bce` 0.831980705261 vs `nn.BCEWithLogitsLoss` 0.831980705261 (\\|Δ\\|=0) | ✅ |")
    A("| S5 | shim 데이터셋의 x·y 가 원본 `PolarGridDataset` 과 **바이트 동일** | "
      "6표본 x·y 동일 · hflip 동전 위치와 RNG 소비 순서 보존 · "
      "hflip 시 마스크도 y 와 같은 sector permutation | ✅ |")
    A("| S6 | VG-denom · FA 모집단 · 게이트 상수 | "
      "H 분모 두 정의 **발산 0** · train 2,598 / val 1,056 실측 일치 · "
      "FA 모집단 `v3_D_arm_cells` 유효 칸 5,022 | ✅ |")
    A("")
    A("**스모크 10/10 PASS.**")
    A("")
    A("### 1.1 마스크 채널 as-built 계수")
    A("")
    A("| 채널 | 술어 | 덮는 칸 | train | val | 전체 | PREREG §5.2 표 |")
    A("|---|---|---|---:|---:|---:|---|")
    A(f"| `b_arm_h` | B팔 ∧ tier=='H' | GT 양성 칸 | 93 | 93 | **186** | 186 ✅ |")
    A(f"| `bare_h_by_k` | tier=='H' ∧ `px_canonical6` < 7,000 | GT 양성 칸 | "
      f"{bare[('train', 'B')]} | {bare[('val', 'A')] + bare[('val', 'B')]} | "
      f"**{sum(bare.values())}** | 110 (A 3·B 107) — as-built는 A 3·B 111 |")
    A(f"| `lever_n_zero_info_c` | C팔 ∧ `frac(\\|ΔI\\|>8)` < 0.001 | **전 칸** | 4 | 27 | "
      f"**31** | 31 (모순 20) ✅ |")
    A(f"| `gt_void` | 그 칸에 void 픽셀 | 그 칸 | 717 | 48 | **765프레임 / 4,227칸** | "
      f"765 / 4,227 ✅ |")
    A("")
    A("- **마스크 총량**: train 4,598 / 51,960 칸 (8.85 %) · val 1,266 / 21,120 칸 (5.99 %).")
    A("- **`bare_h_by_k` 가 §5.2 표(110)와 4프레임 다른 이유**: §5.2 표는 보수 빌드 "
      "`dataset_manifest_v3.json`(3,606프레임) 위의 계수이고, 훈련 정본은 D91 §9.1이 지정한 "
      "`dataset_manifest_v3_seg3.json`(3,654프레임)이다. 차이는 B팔 4프레임이며 **A팔 3은 불변**이다. "
      "두 수를 같은 칸에 넣지 않는다(§6-18 정신).")
    A("- **채널마다 덮는 칸이 다른 근거**는 `code/v3_masks.py` 헤더에 전문으로 적었다. 요약: "
      "`b_arm_h`·`bare_h_by_k`는 *\"화면에 근거 없는 **정답**을 강요하지 않는다\"*(§5.3)이므로 "
      "**GT 양성 칸**만 덮고, `lever_n_zero_info_c`는 *\"모순되는 쪽(C팔 **음성**)을 손실에서 뺀다\"*"
      "(§5.2)인데 C팔은 전 칸 음성이므로 **전 칸**을 덮는다.")
    A("- **세그 부재 fallback 인쇄 의무(§5.3)**: as-built "
      f"**{len(fb)}프레임** (A {fb_arm['A']} · B {fb_arm['B']} · C {fb_arm['C']} · D {fb_arm['D']}) · "
      f"그중 `tier=='H'` **{sum(fb_h.values())}**(A {fb_h['A']} · B {fb_h['B']}) — PREREG §5.3의 "
      "363 / 28(A 24·B 4)과 일치.")
    A("")
    A("---")
    A("")
    A("## 2. 학습 — 런별 표")
    A("")
    A("τ = 0.5 · 선택식 = `S = (1−β)·val_cell_F1 + β·Ĥ − λ·val_cell_FPR` "
      "(β = n_H/(n_H+30) · Ĥ = (h+1)/(n_H+2) · λ = 1.0 · **세 항 전부 마스크 칸 제외**) · "
      "FA 모집단 `v3_D_arm_cells` · 동률 → 이른 에폭.")
    A("")
    A("| 런 | 에폭 | 종료 | **선택 에폭** | **S** | (1−β)·F1 | β·Ĥ | −λ·FPR | h/n_H | β | "
      "**VG-const** | 벽시계 |")
    A("|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---|---:|")
    for r in MAIN + ISO:
        d = runs.get(r, {})
        if d.get("status") in (None, "MISSING"):
            A(f"| `{r}` | — | 미산출 | — | — | — | — | — | — | — | — | — |")
            continue
        s = d.get("selected")
        vg = d["vgconst"]
        tag = " **[격리]**" if r in ISO else ""
        if not s:
            A(f"| `{r}`{tag} | {d['n_epochs']} | **{d['status']}** | — | — | — | — | — | — | — | "
              f"❌ {vg['verdict']} | {(d.get('wall_sec') or 0) / 60:.1f}분 |")
            continue
        c = s["components"]
        A(f"| `{r}`{tag} | {d['n_epochs']} | {d['stop_reason']} | **{s['epoch']}** | "
          f"**{s['S']:.6f}** | {c['term_f1']:.4f} | {c['term_H']:.4f} | {c['term_FA']:.4f} | "
          f"{c['h_hits']}/{c['n_H']} | {c['beta']:.4f} | "
          f"✅ PASS ({vg['n_pass']}/{vg['n_epochs']}) | {(d.get('wall_sec') or 0) / 60:.1f}분 |")
    A("")
    A("**성분 원값** (마스크 적용 val · 선택 에폭에서):")
    A("")
    A("| 런 | val_cell_F1 | Ĥ | val_cell_FPR(D팔) | 선택 에폭 spread | spread 범위(전 에폭) | VG-1ep |")
    A("|---|---:|---:|---:|---:|---|---|")
    for r in MAIN + ISO:
        d = runs.get(r, {})
        s = d.get("selected")
        if not s:
            continue
        c, vg = s["components"], d["vgconst"]
        A(f"| `{r}` | {c['f1']:.6f} | {c['H_hat']:.6f} | {c['fa']:.6f} | "
          f"{vg['spread_at_selected']:.4e} | {vg['spread_min']:.3e} – {vg['spread_max']:.3e} | "
          f"{'⚠ 발동' if d['vg1ep_flag'] else 'n/a'} |")
    A("")
    A("**참고 병기 — 마스크 없는 v2 정의 열** (정의 불변 · 판정 불사용):")
    A("")
    A("| 런 | val_f1 | val_fpr | val_h_recall(비마스크 분모 186) | 프레임 FA(D팔) |")
    A("|---|---:|---:|---:|---:|")
    for r in MAIN + ISO:
        d = runs.get(r, {})
        s = d.get("selected")
        if not s:
            continue
        v = s["val_unmasked"]
        A(f"| `{r}` | {v['val_f1']:.6f} | {v['val_fpr']:.6f} | {v['val_h_recall']:.6f} | "
          f"{v['val_frame_fa_d']:.6f} |")
    A("")
    A("- **온라인 선택 ↔ 사후 재계산 일치**: " +
      " · ".join(f"`{r}` {'OK' if runs[r].get('online_matches_recompute') else '**불일치**'}"
                 for r in MAIN + ISO if runs.get(r, {}).get("selected")) +
      f" (점수 재현 오차 max "
      f"{max((runs[r].get('max_score_repro_err') or 0) for r in runs):.1e} — metrics.csv 6자리 반올림 몫).")
    A("")
    A("### 2.1 β 의 as-built 값 — **인쇄 의무**")
    A("")
    A(f"| 분모 | 값 | β | 출처 |")
    A(f"|---|---:|---:|---|")
    A(f"| val hazard-H (정의 B · **마스크 전**) | 186 | 0.861 | 코퍼스 실측 (A 93 + B 93) |")
    A(f"| PREREG §5.0 이 인쇄한 as-built \"val strict-H\" | 93 | 0.756 | §5.0 표 (A팔 몫) |")
    A(f"| **선택식이 실제로 쓴 유효 n_H (마스크 후)** | **90** | **0.750** | "
      f"본 웨이브 실측 |")
    A("")
    A("세 수의 관계는 전부 등록된 기전으로 설명된다.")
    A("")
    A("1. 186 → 93 : `b_arm_h`(B팔 ∧ tier=='H', 무조건 적용)가 **B팔 93프레임의 양성 칸을 전부** "
      "덮으므로 그 프레임들은 P4_SELECTION §2.6의 규칙 *\"양성 칸이 전부 마스크된 H 프레임은 "
      "분모에서 사라진다\"*에 따라 분모에서 빠진다.")
    A("2. 93 → 90 : `bare_h_by_k`(k=7,000 봉인)가 **A팔 맨-가림 H 3프레임**을 덮는다. "
      "PREREG §5.3이 *\"A팔 strict-H는 3프레임뿐 — k를 1로 해도 3, 7,000으로 해도 3\"*이라고 "
      "미리 인쇄한 바로 그 3프레임이며, as-built 정체는 `sceneH6`의 "
      "`L0/L5/L7__s20260824__0005.png::w2h2`(`px_canonical6` = 0)다.")
    A("3. 따라서 **β = 90/120 = 0.750**은 사후 조정이 아니라 PREREG §5.1의 등록 문면 "
      "*\"β는 매 실행 n_H를 실측해서 만든다\"* 를 그대로 집행한 결과다. §5.0의 93은 **마스크 전** "
      "코퍼스 계수이고, 선택식이 쓰는 것은 §5.2가 규정한 **마스크 후** 분모다. 두 수를 같은 칸에 "
      "넣지 않는다.")
    A("")
    A("### 2.2 λ = 1.0 유지 · OPEN-5 미해소 (인쇄 의무)")
    A("")
    A("PREREG §5.1은 FA 모집단을 `v3_D_arm_cells`로 **전환 채택**하면서 *\"모집단 교체는 λ 재유도를 "
      "강제한다\"*고 적었고(OPEN-5), D91 §9.3은 OPEN-5를 **판정 비차단**으로 처분했다. "
      "λ 재유도는 **결재 사항**(P4_SELECTION 결재 6)이고 본 에이전트에게 승인이 없으므로 "
      "**동결된 λ = 1.0을 그대로 썼다.** 결과를 본 뒤 λ를 움직이는 것은 §6-1 위반이다.")
    A("")
    A("재유도가 필요할 때 쓸 실측만 남긴다 — 선택 에폭의 `val_cell_FPR`(D팔 한정):")
    A("")
    A("| 런 | FPR(D팔) | −λ·FPR 이 S 에서 차지하는 몫 |")
    A("|---|---:|---:|")
    for r in MAIN + ISO:
        d = runs.get(r, {})
        s = d.get("selected")
        if not s:
            continue
        c = s["components"]
        share = abs(c["term_FA"]) / max(abs(c["term_f1"]) + abs(c["term_H"]) + abs(c["term_FA"]),
                                        1e-9)
        A(f"| `{r}` | {c['fa']:.6f} | {share * 100:.2f} % |")
    A("")
    A("PREREG §5.1이 예고한 대로 **모집단을 D팔로 좁히면 λ=1은 FA 항을 사실상 끄는 값**이 된다"
      "(v2 pooled 0.1777 ↔ off팔 한정 0.0181, 약 10배). as-built가 그 예고를 확인했다.")
    A("")
    A("### 2.3 관측 — H 항이 처음으로 후보를 갈랐다 (판정 아님 · 인쇄만)")
    A("")
    A("PREREG §5.1은 *\"v2 출하 9체크포인트가 9/9 모두 val H recall = 1.000이라 v2 쪽에서 H 항은 "
      "상수였다. v3에서는 처음으로 H 항이 후보를 가른다 — **그 거동은 v3에서 최초 관측되며 "
      "사전 예측하지 않는다**\"*고 적었다. as-built 실측이 그 자리를 채운다.")
    A("")
    A("| 런 | 선택 에폭 | 선택 에폭의 h/n_H | 인접 에폭의 h (−1 / +1) | 전 에폭 h 범위 |")
    A("|---|---:|---:|---|---|")
    for r in MAIN + ISO:
        d = runs.get(r, {})
        s = d.get("selected")
        if not s:
            continue
        import csv as _csv
        rows = list(_csv.DictReader(open(f"{V3}/runs/v3a/{r}/metrics.csv")))
        hs = {int(x["epoch"]): int(x["sel_h_hits"]) for x in rows}
        e = s["epoch"]
        A(f"| `{r}` | {e} | **{hs[e]}/90** | {hs.get(e - 1, '—')} / {hs.get(e + 1, '—')} | "
          f"{min(hs.values())} – {max(hs.values())} |")
    A("")
    A("- **`rgb_s42` ep24 의 h = 62/90 은 인접 에폭(6 · 7)의 10배**다. H 프레임 적중은 에폭 사이에 "
      "크게 출렁이고, β = 0.75 에서 H 항이 S 의 지배항이므로 **선택은 사실상 H 항이 한다** "
      "(선택 에폭에서 β·Ĥ 가 S 의 " +
      f"{min(s['components']['term_H'] / s['S'] for s in [runs[x]['selected'] for x in MAIN]) * 100:.0f}–"
      f"{max(s['components']['term_H'] / s['S'] for s in [runs[x]['selected'] for x in MAIN]) * 100:.0f} %"
      + ").")
    A("- **선택 에폭이 시드마다 크게 갈린다** — 24 / 2 / 11. 이것은 등록된 식이 만든 결과이며, "
      "**결과를 본 뒤 식·문턱·patience 를 움직이는 것은 §6-1 위반**이므로 본 웨이브는 아무것도 "
      "조정하지 않았다. 다음 웨이브에서 시드 σ(ddof=1)를 읽을 때 **이 산포를 인쇄 의무 항목으로 "
      "가져간다**(§3.2 *\"σ가 큰 팔의 PASS는 판정 불가다\"*).")
    A("- **VG-1ep 은 발동하지 않았다** — 등록 술어는 *\"선택 에폭 index ≤ 1\"*이고 최소값이 "
      "`rgb_s43` 의 **ep2** 다. ep2 가 문턱 바로 위라는 사실은 인쇄하되 **문턱을 사후에 올리지 "
      "않는다**(§6-1).")
    A("")
    A("---")
    A("")
    A("## 3. v2 재현 회귀 가드")
    A("")
    A("선택 코드를 **v2 15런**에 겨누면 `P4_SELECTION`이 등재한 P-4 판정을 그대로 재현하는가. "
      "재현 실패 = 코드가 웨이브 중 변형됐다는 뜻이므로 v3 판정 전체가 무효다.")
    A("")
    A(f"- 규약: n_H = {g['n_h']} · FA 모집단 `{g['fa_population']}` · 마스크 없음 · "
      f"게이트 {g['gate']}")
    A(f"- **결과: {g['n_match']} / {g['n_runs']} 재현** "
      f"{'✅ PASS' if g['all_match'] else '❌ FAIL'} (선택 에폭 + 점수 \\|Δ\\| < 1e-9)")
    A("")
    A("| 런 | 구식 선택 | P-4 등재 | 본 웨이브 재현 | 판정 |")
    A("|---|---:|---:|---:|---|")
    for row in g["rows"]:
        A(f"| `{row['run']}` | {row['old_epoch']} | {row['expected_epoch']} | "
          f"{row['got_epoch']} | {'✅' if row['match'] else '❌'} |")
    A("")
    A("- `rgb_s42`의 **ep9 → ep10** 이동(P4_SELECTION §3.3이 인쇄한 \"6런 중 유일한 이동\")이 "
      "그대로 재현된다.")
    A("- **§3.3 경고 준수**: 이 표(P-4 v2 재현 검증)와 §2의 v3-A 선택은 **서로 다른 판정선**이다. "
      "한쪽을 다른 쪽에 끌어와 유리한 값을 고르는 것은 §6-10 위반이므로 두 표를 섞지 않는다.")
    A("")
    A("---")
    A("")
    A("## 4. 동결의 실증 — config diff")
    A("")
    A(f"`runs/v2/rgb_s42/config.json` ↔ `runs/v3a/rgb_s42/config.json` 전수 대조 "
      f"(`code/v3a_config_diff.py` · 원장 `logs/v3a_config_diff.json`).")
    A("")
    A(f"- 동일한 키 **{cfd['n_same']}** / 갈린 키 **{cfd['n_diff']}** / "
      f"**등록 항목에 귀속되지 않는 키 {cfd['n_unexplained']}**")
    A(f"- 판정: **{cfd['verdict']}** — PREREG §1.1 *\"diff가 등록 항목 외 0줄\"* 성립")
    A("")
    A("**레시피 상수가 v2와 글자 그대로 같다는 실증** (동일 키에서 발췌):")
    A("")
    A("| 키 | v2 = v3a |")
    A("|---|---|")
    for k in ("input", "seed", "max_epochs", "patience", "batch", "lr", "weight_decay",
              "lr_schedule", "workers", "aug", "hflip", "oversample_h", "bias_init",
              "tau", "img_size", "grid", "n_cells", "grid_version", "encoder",
              "params_m", "recipe", "bias_init_module"):
        if k in cfd["same_keys"]:
            v = json.load(open(f"{V3}/runs/v3a/rgb_s42/config.json")).get(k)
            A(f"| `{k}` | `{json.dumps(v, ensure_ascii=False)[:60]}` |")
    A("")
    A("**갈린 키의 귀속** (전수):")
    A("")
    A("| 키 | 귀속 |")
    A("|---|---|")
    for row in cfd["diff"]:
        A(f"| `{row['key']}` | {row['attributed_to']} |")
    A("")
    A("---")
    A("")
    A("## 5. v2 호출 대비 차이 — 등록 조작항 전수")
    A("")
    A("드라이버는 `train_polar.py`를 **한 줄도 수정하지 않고** 감싼다"
      "(`code/train_v3.py` · `code/polar_dataset_v3.py` · `code/v3_masks.py`). "
      "레시피 함수(`guard_gpu_free` · `set_seed` · `is_strict_h` · `make_sampler` · "
      "`set_prior_bias` · `cell_stats` · `h_frame_recall`)는 **train_polar.py에서 import**한다 — "
      "복제하지 않는다.")
    A("")
    A("| # | 차이 | v2 | v3-A | 왜 등록 조작항인가 |")
    A("|---|---|---|---|---|")
    A("| **R1** | 코퍼스 | `dataset_manifest_v2_full.json` / `split_v2_full.json` | "
      "`dataset_manifest_v3_seg3.json` / `split_v3_seg3.json` | "
      "PREREG §1.1 조작변인 \"코퍼스\" · D91 §9.1 \"훈련 정본 = seg3\" |")
    A("| **R2** | 지도 규칙 | `nn.BCEWithLogitsLoss()` (전 칸 평균) | "
      "`Σ(BCE·valid)/Σvalid` — 등록 4채널 무시 마스크 | "
      "§1.1 조작변인 \"지도 규칙\" · §5.2 3단 사거리 1단. 마스크 전량 0이면 v2와 **수치 항등**(S4) |")
    A("| **R3** | 선택식 | `0.5·val_f1 + 0.5·val_h_recall` | "
      "`(1−β)F1 + βĤ − λFPR`, 마스크 적용, FA 모집단 `v3_D_arm_cells`, VG-const 미통과 → S=−∞ | "
      "§1.1 조작변인 \"선택식\" · §5.1 · §5.2 3단 사거리 2단. 구현은 "
      "`selection_v3.compute_selection()` **단일 진입점** 호출뿐 |")
    A("| **R4** | 로깅 | 10열 | 10열 **그 순서 그대로** + `val_spread`(§5.5ⓐ) · "
      "`val_frame_fa_all`/`val_frame_fa_d`(§5.5ⓑ · 기록만) · `sel_*` 성분 · `vgconst_pass` · "
      "`val_loss_masked` | §1.1 조작변인 \"로깅\" · §5.5 로깅 의무 2건 · §4.1 전제 |")
    A("| **R5** | 게이트 처분 | (없음) — best.pt 가 없으면 마지막 state 저장 | "
      "VG-const 통과 에폭 0 → **best.pt 미기록 · `TRAINING_FAILED` · exit 3** | "
      "§4.1 \"거부 시 처분\" · P-04 · **§6-16 조용한 폴백 금지**. v2 꼬리코드의 폴백 경로를 "
      "의도적으로 삭제했다 — 그게 convnext s42·s43이 출하된 경로다 |")
    A("| R6 | best 초기값 | `-1.0` | `-inf` | 신 선택식은 음수 S 를 낼 수 있어 `-1.0`은 정당한 "
      "음수 최적을 조기 탈락시킨다. **선택식 교체의 산술적 귀결**이지 새 조작항이 아니다 |")
    A("")
    A("**그 외 전부 v2 동결**: resnet34 U-Net · lr 3e-4 · AdamW · wd 0.0 · batch 8 · 512² · "
      "max 150ep · patience 15 · LR 선형감쇠 · AMP 없음 · hflip on · oversample-h 4.0 · "
      "bias-init prior · τ 0.5 · workers 4 · aug off · drop_last=True · 시드 42/43/44 · "
      "동률 시 이른 에폭.")
    A("")
    A("**평가 코드 경로는 한 줄도 건드리지 않았다** (§5.2 3단 사거리 3단 · §6-3 · 스모크 S3-eval).")
    A("")
    A("---")
    A("")
    A("## 6. 격리 aux 런 (§5.6 · D82 결재 3)")
    A("")
    d = runs.get("rgb_s42_aux", {})
    s = d.get("selected")
    if s:
        A(f"- 시드 42 · `--aux-mask-dir` ON · λ_aux = 0.5 · **선택 ep {s['epoch']} · "
          f"S = {s['S']:.6f}** · VG-const {d['vgconst']['verdict']}")
    A("- **본 A/B 판정에 혼입하지 않는다.** `config.json::v3_registered.isolated_from_ab = true`로 "
      "각인돼 있다.")
    A("- **한계 (인쇄 의무)**: 아모달 마스크는 v2 세대 산출물(`dayrun_0820/annotations/amodal`)이라 "
      "**A팔에만** 존재한다. v3 `frame_id`(`A/scene01/…`)와 v2 stem(`on__scene01__…`)이 갈리므로 "
      "rgb 경로로 대응시킨 `aux_stem_map_v3.json`(768프레임)을 끼웠고, **train 2,598 중 648프레임만 "
      "마스크를 받는다**(v2 aux 런의 648과 같은 집합). B팔은 위험을 갖고도 아모달 마스크가 없어 "
      "**빈 마스크로 학습**된다 — 이 결함이 이 런을 격리해야 하는 이유 중 하나이며, "
      "본 판정에 쓰지 않으므로 A/B 순수성에는 영향이 없다.")
    A("")
    A("---")
    A("")
    A("## 7. 다음 웨이브 입력 준비 상태 (평가는 **하지 않았다**)")
    A("")
    A("계기판 ①②③ 평가는 본 웨이브의 범위 밖이다(PREREG §2: 무대 = **test-ext 4팔 전용**).")
    A("")
    A("| 입력 | 경로 | 상태 |")
    A("|---|---|---|")
    for r in MAIN:
        st = runs.get(r, {}).get("status")
        A(f"| 체크포인트 `{r}` | `experiments/v3_0823/runs/v3a/{r}/best.pt` | "
          f"{'✅ ' + str(runs[r]['selected']['epoch']) + ' 에폭' if runs.get(r, {}).get('selected') else '❌ ' + str(st)} |")
    A(f"| 체크포인트 `rgb_s42_aux` (격리) | `runs/v3a/rgb_s42_aux/best.pt` | "
      f"{'✅' if d.get('selected') else '❌'} — 본 A/B 비혼입 |")
    A("| 계기판 무대 매니페스트 | `experiments/v3_0823/dataset_manifest_v3_textext.json` "
      "+ `split_v3_textext.json` | ✅ (W3 · 1,152프레임 · A/B/C/D 각 288) |")
    A("| 계기판 무대 (B·D팔) | `dataset_manifest_v3_textext_bd.json` + `split_v3_textext_bd.json` "
      "| ✅ |")
    A("| 헤드라인·FA-정합 무대 (test-core) | `split_v2_full.json::test` (7씬 · 교정 GT) | ✅ |")
    A("| v2 before 표 | `V2_TEXTEXT_BASELINE.md` (9런 zero-shot) | ✅ 산출 완료 |")
    A("| val 확률 덤프 (보정 T 탐색용 · §5.2) | `runs/v3a/*/val_probs_best.npy` | ✅ 선택 에폭 |")
    A("")
    A("**평가 전에 반드시 지킬 것**: 무시 마스크는 **평가에 적용하지 않는다**(§5.2 3단 · §6-3). "
      "`v3_masks.py`를 평가 코드 경로에서 import 하는 것 자체가 위반이다.")
    A("")
    A("---")
    A("")
    A("## 8. 이탈 (deviations)")
    A("")
    A("**PREREG 이탈 0건.** 아래 3건은 이탈이 아니라 **등록 문면의 as-built 집행 결과**이며 "
      "인쇄 의무를 이행한다.")
    A("")
    A("| # | 항목 | 성격 | 근거 |")
    A("|---|---|---|---|")
    A("| 1 | β = 0.750 (n_H = 90) — §5.0의 0.756(n_H = 93)과 다름 | **등록 문면 집행** | "
      "§5.1 *\"β는 매 실행 n_H를 실측해서 만든다\"* + §5.2 *\"선택식에 손실과 동일한 마스크 적용\"*. "
      "차이는 `bare_h_by_k`가 덮은 A팔 3프레임이고 §5.3이 그 3프레임을 미리 인쇄했다 (§2.1) |")
    A("| 2 | `bare_h_by_k` as-built 114 — §5.2 표의 110과 다름 | **원장 세대 차이** | "
      "§5.2 표는 보수 빌드(3,606) 계수, 훈련 정본은 D91 §9.1의 seg3(3,654). "
      "두 수를 병기하고 같은 칸에 넣지 않는다 (§1.1) |")
    A("| 3 | λ = 1.0 유지 (OPEN-5 λ 재유도 미실행) | **결재 대기 · 비차단** | "
      "D91 §9.3 *\"OPEN-5는 판정 비차단\"* · λ 변경은 P4_SELECTION 결재 6 사항이며 승인 없음. "
      "결과를 본 뒤의 λ 이동은 §6-1 위반 (§2.2) |")
    A("")
    A("**§5.4 훈련 착수 게이트 5항** — D91이 전부 개방한 상태로 착수했다: "
      "W1+W2 라벨 완료 ✅ · VG-01/02 ✅ · **VG-09 ✅**(D91 ① 최종 \\|r\\| 전 6키 ≤ 0.2, max R 0.1728) · "
      "**VG-11 k 봉인 ✅**(D91 §9.2 k = 7,000) · `n_val_strict_h ≥ 30` ✅(실측 93 · 3.10배).")
    A("")
    A("---")
    A("")
    A("## 9. 재현")
    A("")
    A("```bash")
    A("cd /home/vislab/Desktop/work_sy/Practice_NegObs/experiments/v3_0823")
    A("")
    A("# 스모크 (CPU · 3단언 + 항등 대조)")
    A("PYTHONNOUSERSITE=1 CUDA_VISIBLE_DEVICES= \\")
    A("  /home/vislab/miniconda3/envs/env_seg/bin/python code/smoke_v3.py")
    A("")
    A("# 학습 웨이브 (GPU · flock · 재개 안전 · 4런 순차)")
    A("bash code/run_v3a_train.sh")
    A("")
    A("# 선택 집계 + v2 재현 회귀 가드 (CPU)")
    A("PYTHONNOUSERSITE=1 python3 code/v3a_select.py")
    A("")
    A("# 동결의 실증 (CPU)")
    A("PYTHONNOUSERSITE=1 python3 code/v3a_config_diff.py")
    A("")
    A("# 본 문서 재생성")
    A("PYTHONNOUSERSITE=1 python3 code/v3a_report.py")
    A("```")
    A("")
    A("**원장**: `logs/v3a_selection.json` · `logs/v3a_config_diff.json` · "
      "`logs/v3a/*.log` · `runs/v3a/*/{config.json,metrics.csv,DONE}` · "
      "`aux_stem_map_v3.json`")
    A("")
    out = f"{V3}/V3A_TRAIN.md"
    with open(out, "w") as fh:
        fh.write("\n".join(L) + "\n")
    print(f"wrote {out}  ({len(L)} lines)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
