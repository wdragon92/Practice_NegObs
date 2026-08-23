# INDEX — 8/30 백업 제출본 지원 패키지 (CPU-7 산출, D58 ⑥)

> **이 문서의 용도.** 산문은 **Claude AI**가 씁니다. 이 색인은 그 집필자가 **자료를 찾아 헤매지 않도록**
> 하는 것이 전부입니다. 각 행의 마지막 열(**중요·누락위험 메모**)은 초안 작성자가 **직접 소비**하는
> 열입니다 — 그 행을 인용할 때 반드시 함께 나가야 하는 것, 또는 빠뜨리기 쉬운 것을 한 줄로 적었습니다.
>
> **생성 규칙 준수**: 신규 파일만 · `submission_0830/` 하위 · git 명령 미사용 · 원장 수치 무편집 전사.
> 모든 수치는 원장에서 직접 확인했으며, 다른 문서의 **산문 기억으로 인용한 숫자는 없습니다.**

## 0. 먼저 읽을 것 (정본 순서)

| # | 문서 | 왜 |
|---|---|---|
| 1 | `Docs/experiment/Status/PROJECT_STATE_0823_v2.md` | **정정된 진실.** 구판 §5.1(RGB 우위)·§5.2(9/9 CI)·§6-4(H recall 해석)는 **무효** |
| 2 | `experiments/weekend_0823/MORNING_REPORT_0823.md` §2 | 확정 사실 11건 + §3 캐비앗 7건(C1–C7) = 한계 절 원재료 |
| 3 | `experiments/mainrun_0819/DECISIONS.md` **D52–D65** | v3 창의 정정들 — v2 주장을 바꾸는 것은 전부 여기 |
| 4 | `experiments/v3_0823/ACCOUNTING.md` | **분모의 단일 정본.** 모든 n은 여기서만 인용 |
| 5 | 본 색인 → `tables/` → `fragments/` | 규격본 |

**3대 인용 규율 (위반 시 심사자가 먼저 찾습니다)**
1. **census는 `leg + 접기여부 + n`으로만 인용** — 맨숫자 금지 (`ACCOUNTING.md` §1.7).
2. **recall 주장은 FA 맥락 없이 절대 금지**, 그리고 **양축(프레임+칸) 병기가 의무** (§4.8 #1 / §4.9-2).
3. **분모는 손으로 계산하지 않는다** — `ACCOUNTING.md` 또는 스크립트 산출만 (D59 ⑦의 교훈).

---

## 1. 제출 자산 색인

**상태 범례** — `제출가능` = 지금 그대로 인용 가능 · `재발행 필요` = 존재하지만 제출 전 재생성 필요(§6) ·
`로컬 전용` = 리포에 있으나 `.gitignore`로 GitHub에 **없음**(공개 리포에서 접근 불가).

> **로컬 전용 판정 방법(명시)**: git 명령을 쓰지 않는다는 지시에 따라 **`.gitignore` 규칙 + 파일 실재
> 확인**으로 판정했습니다. 해당 규칙: `**/runs/**/*.png`(17행) · `**/runs/**/*.jpg` · `logs/` ·
> `dataset/` · `look_check/*` · `experiments/*/audit_samples*/` · `**/cue_audit/smoke/`.

### 1.1 헤드라인 결과

| 자료 | 경로(리포 상대) | 형식 | 상태 | **중요·누락위험 메모** |
|---|---|---|---|---|
| **본 표 4행 정본** (배너 포함) | `experiments/dayrun_0820/runs/v2/SEED_TABLE.md` | md | **재발행 필요** | **배너(:9)가 표의 일부다 — H 열을 모델 비교로 인용할 때 FA 정합표 병기는 의무.** V·det·cell 계열은 교정 GT에서 이동(§6-A), H·E·off는 9/9 바이트 불변 |
| 본 표 규격본 | `submission_0830/tables/T01_headline_seed_table.md` | md | 제출가능 | 배너 3종을 캐비앗 라인으로 분리해 붙여둠. **§5(aux)는 부록이며 본 표 5행이 아니다(결재 #2)** |
| 교정 GT 헤드라인 | `submission_0830/tables/T06_v2_rescore_corrected_gt.md` §2 | md | 제출가능 | 교정 GT 본 표(분모 V219·E45·H96·Hw9·det369). **σ 초과 이동은 depth 2건뿐이고 그중 H_weak는 인용 금지(σ=0 퇴화, 분모 9)** |
| 본문 초안 | `experiments/mainrun_0819/RESULTS_DRAFT.md` | md | **재발행 필요** | **RT-A~RT-F(:509~)가 이미 논문용 영어 문단이다 — 새로 쓰지 말고 여기서 가져올 것.** 단 §5.1–5.6은 **v1 336프레임 스코프**(불변)이고 :269 등은 교정 필요 |
| 지표 정의·계산 원장 | `experiments/mainrun_0819/METRICS.md` (§RT.1–RT.8) | md | **재발행 필요** | 방법 절의 유일 정본. **:628 "test 327 / corpus 1038"과 :1235 "V 726→657"은 각각 RESULTS_DRAFT의 짝과 동시 수정해야 함**(§6-B) |

### 1.2 FA-정합 — **이중 축 의무**

| 자료 | 경로 | 형식 | 상태 | **중요·누락위험 메모** |
|---|---|---|---|---|
| FA-정합 프레임 축 | `experiments/weekend_0823/rt_response/F1_FA_MATCHED.md` | md | **재발행 필요** | H 열은 교정 GT 불변(구조적). **:5의 "V n=180" 및 §3·§4의 V 열은 교정 필요.** 이 파일에는 캐비앗 절이 **없다** — 캐비앗은 T02가 공급 |
| **FA-정합 칸 축 (신규 · D65)** | `experiments/v3_0823/redteam/EVL12_CELL_AXIS.md` | md | 제출가능 | **최대 인용 결과: τ=0.5에서 프레임축 RGB .688>Depth .438 ↔ 칸축 Depth .537>RGB .344 — 단위가 우열을 뒤집는다.** 프레임축만 인쇄하면 이 반전이 보이지 않음 |
| 이중 축 규격본 | `submission_0830/tables/T02_fa_matched_dual_axis.md` | md | 제출가능 | 양축 + MAP-C 등록 + 경보 부담표 + 교정 GT 영향 통합. **칸/FA프레임 "4.29"는 시드 합산치이고 시드 평균은 5.50 — 추정량을 명시하지 않으면 인용 사고** |
| recall–FA 곡선 그림 | `experiments/weekend_0823/rt_response/figs/fig_f1_recall_vs_fa.png` + `.pdf` | png/pdf | 제출가능 | **리포 유일의 벡터 그림(.pdf).** τ=0.5 지점이 표시돼 있어 운용점 불일치를 한눈에 보여줌 |

### 1.3 인과 증거 3종 (세 독립 측정)

| 자료 | 경로 | 형식 | 상태 | **중요·누락위험 메모** |
|---|---|---|---|---|
| 트윈-조건부 표 | `experiments/weekend_0823/rt_response/F2_TWIN_CONDITIONAL.md` | md | **재발행 필요** | H·E 표는 교정 GT **완전 동일**. **V 표만 재발행**(kept 165→177). **"Depth 96/96 위험-조건부"가 이 논문에서 가장 강한 긍정 문장** |
| 트윈-조건부 규격본 | `submission_0830/tables/T03_twin_conditional.md` | md | 제출가능 | **b2의 "46.7 %"는 원장에 없는 수치다** — 원장 인쇄치는 0.305이고 46.7 %는 상대 하락폭. MORNING_REPORT §2.3이 이 형태로 인쇄돼 있어 그대로 옮기면 사고 |
| CUE-OFF 개입 결과 | `experiments/weekend_0823/cue_audit/CUEOFF_RESULT_v2.md` | md | 제출가능 | **§6.4가 개입실험 절의 골격으로 채택됨** — 논문 문단이 이미 거기 있음. §4.4 용량-반응표가 "단서 어휘" 독법을 죽인 실측 |
| CUE-OFF 센서스 규격본 | `submission_0830/tables/T04_cueoff_census.md` | md | 제출가능 | **30/21 병기는 사전등록 A2-7의 의무** — 헤드라인만 인쇄하면 위반. 판정은 **중립**이고 기여는 **장치+진단**(결재 #3) |
| 센서스 원 데이터 | `experiments/weekend_0823/cue_audit/VERDICT_CENSUS_v2.csv` | csv | 제출가능 | `folded` 열이 A2-7 플래그. 재집계로 5행 전부 검산 완료 |
| 사전등록 문서 | `experiments/weekend_0823/cue_audit/PREREG_CUEOFF.md` | md | 제출가능 | **A2-13(s20fix 무효)이 모델을 돌리기 전에 쓰였다는 타임스탬프 증거가 :697에 있다 — 사후 무효가 아님을 보이는 핵심 자료** |
| Gazebo 교차-시뮬 | `experiments/weekend_0823/gazebo/GAZEBO_TRACK.md` | md | 제출가능 | **§개입실험 결론의 유일한 독립 증거**(다른 렌더러). 안전 주장은 **2종뿐**(§7-2) — 트윈 붕괴는 도메인 갭과 교란 |
| Gazebo 규격본 | `submission_0830/tables/T05_gazebo_cross_sim.md` | md | 제출가능 | **사다리 역전은 5/6이다 — D48의 "4/6"은 오계수(정정 기록됨)** |
| Gazebo 정성 패널 6장 | `experiments/weekend_0823/gazebo/out/panels/` | png ×6 | 제출가능 | `out/`은 `outputs/` 규칙에 안 걸림 → **추적 가능**. 전체 432장 오버레이(76 MB)는 의도적 미커밋 |

### 1.4 교정 GT (G7) — v2 서술을 바꾸는 축

| 자료 | 경로 | 형식 | 상태 | **중요·누락위험 메모** |
|---|---|---|---|---|
| G7 수리·재라벨 | `experiments/v3_0823/G7_RELABEL.md` | md | 제출가능 | **논문에 주는 답 하나: test H 96 불변.** 48개 strict-H 손실은 전량 scene12 = **train** 씬. 결함면과 test H는 교집합 0 |
| 교정 매니페스트 (정본 B) | `experiments/v3_0823/dataset_manifest_v2corr.json` | json | 제출가능 | 240프레임(8.5 %) 교정, **픽셀 무변경**. 민감도 A는 `_roundown.json` |
| G7 규격본 | `submission_0830/tables/T07_g7_repair_tiers.md` | md | 제출가능 | **"분모 미오염"은 H행 한정 참** — V 분모는 180→219(+21.7 %)로 크게 이동. **"오라클 6씬"(D42)은 실측 3씬/5쌍** |
| v2 재채점 | `experiments/v3_0823/V2_RESCORE.md` | md | 제출가능 | **§6.2/§6.3이 공표 문서의 이동 줄/불변 줄 전수 색인이다 — 초안 작성자가 가장 먼저 볼 파일** |
| 재채점 규격본 | `submission_0830/tables/T06_v2_rescore_corrected_gt.md` | md | 제출가능 | **"분모 372"는 오기 — 정답 369.** §4.2·D55에 372가 남아 있음. 미측정 2행(YOLO·aux)은 §6 |
| 재채점 집계 원장 | `experiments/v3_0823/eval_v2corr/rescore_tables.json` | json | 제출가능 | 9런 전 지표 구/교정 대조. **분모는 여기서만 인용** |
| 모집단 규격본 | `submission_0830/tables/T15_populations.md` | md | 제출가능 | 모든 "n"의 단일 참조. **트윈 V 분모는 219가 아니라 177** |

### 1.5 통계 규율

| 자료 | 경로 | 형식 | 상태 | **중요·누락위험 메모** |
|---|---|---|---|---|
| 클러스터 부트스트랩 | `experiments/mainrun_0819/METRICS.md` §RT.5 · `rt_response/F5_CLUSTER_CI.md` | md | 제출가능 | **H·E CI는 축소가 아니라 철회.** H 2클러스터·E 1클러스터. 대체물은 "같은 씬의 off팔 FA 옆에 씬별 값" |
| 규격본 | `submission_0830/tables/T11_cluster_ci_withdrawal.md` | md | 제출가능 | **aux `cell_recall_H +0.3546` 유의 주장 철회** — SEED_TABLE §5.2가 "표에서 가장 큰 확증 효과"라고 부른 바로 그 문장 |
| 어댑터-프리 검출기 | `experiments/mainrun_0819/METRICS.md` §RT.3 | md | **재발행 필요** | **YOLO E/H=0은 `det2cell` 어댑터의 성질** — 패러다임 상한 아님. V행·none_in_fov행 재발행 필요 |
| 규격본 | `submission_0830/tables/T12_adapter_free_detector.md` | md | 제출가능 | **어댑터-프리 H 적중 0.066, 트윈-조건부 −0.010.** τ=0.10 사각(1/96 프레임) 각주가 스윕과 함께 나가야 함 |

### 1.6 부록 트랙 (결재 #8: 부록 확정)

| 자료 | 경로 | 형식 | 상태 | **중요·누락위험 메모** |
|---|---|---|---|---|
| 융합행 | `experiments/weekend_0823/fusion/FUSION_ROW.md` | md | **재발행 필요** | **E/H는 3시드 전부 +0.000(구조적)**, 상보성은 거리 축에만 실재. **RGB U-Net이 band1을 3시드×4,080슬롯에서 0회 발화** |
| 규격본 | `submission_0830/tables/T09_fusion_row_appendix.md` | md | 제출가능 | **본문 불가·생략 불가** — 이건 결과가 아니라 감사("왜 캐스케이드를 안 했나"의 답) |
| 신규 인코더 | `experiments/weekend_0823/newmodels/FA_MATCHED.md` | md | 제출가능(구 GT) | **τ=0.5 무정합 수치(H .63–1.0)는 어떤 형태로도 인용 금지**(원장 명시). 교정 덤프 없음 |
| 규격본 | `submission_0830/tables/T10_newmodels_appendix.md` | md | 제출가능 | **진짜 소득은 인코더 비교가 아니라 훈련 실패다** — 선택지표 H항 분모가 val 6프레임이고 **본 표 resnet34도 같은 식을 썼다**(캐비앗 C3) |
| 광도 스트레스 | `experiments/weekend_0823/photometric/PHOTOMETRIC_STRESS.md` | md | **재발행 필요** | **val 전용 — test 7씬은 한 프레임도 읽지 않았다**(코드가 강제). 교정 GT에서 val V 75→96이므로 val 수치 인쇄 시 재발행 |
| 규격본 | `submission_0830/tables/T08_photometric_stress.md` | md | 제출가능 | **"0.1 미만"은 3시드 평균** — 개별 시드는 −0.111까지 감. 비가역은 **과노출 한 방향뿐**(하이라이트 클리핑) |
| 광도 그림 | `experiments/weekend_0823/photometric/photometric_stress.png` | png | 제출가능 | 추적 가능 |
| 3a 시점 감사 | `experiments/weekend_0823/a3_viewpoint/3A_VIEWPOINT_AUDIT.md` (+ `.png`) | md/png | 제출가능 | **§6에 결재 #4 양안 문장(A/B, EN+KR)이 이미 작성돼 있다.** 3b 씬 집중(scene14) 한계 문장의 출처 |
| sceneC2 원인 | `experiments/weekend_0823/c2_rootcause/C2_ROOTCAUSE.md` | md | 제출가능 | **distinct-input 8개** 보고 레벨 채택(결재 #5). 장식 귀속 RGB 77 % / Depth 44 %, 신off FA **.681** = 실측 N-cue 기준점 |

### 1.7 실측(현실세계) 트랙

| 자료 | 경로 | 형식 | 상태 | **중요·누락위험 메모** |
|---|---|---|---|---|
| 촬영 프로토콜 | `experiments/mainrun_0819/realworld/PROTOCOL_SHOOT.md` | md | 제출가능 | AUC 판독선 **사전 등록**(≥.80 진행 / .60–.80 보류 / <.60 중단), 결과 보기 전 고정 |
| 관측 격자 프로토콜 | `experiments/mainrun_0819/realworld/REALWORLD_GRID_PROTOCOL.md` | md | 제출가능 | **20칸 중 15칸** 비대칭의 실측 근거(밴드1은 규정 포즈에서 프레임 밖). 결재 #7이 방법 절 명시를 요구 |
| 부지 대장 | `experiments/mainrun_0819/realworld/sites.csv` | csv | **재발행 필요** | **미수정 상태 — azimuth 부호 역전, 구 V0 칸 이름 `C3`, tier 값 미세분, 권고 4열 부재.** 촬영 직전 1회 수정(결재 #6) |
| 파일럿 패키지 | `experiments/weekend_0823/pilot_package/README_PILOT.md` | md | 제출가능 | **RGB 단일 팔만 가능**(`infer_photo`가 rgb 전용) — 논문에 명시 필요 |
| 실측 규격본 | `submission_0830/tables/T14_realworld_protocol.md` | md | 제출가능 | ⚠ **촬영분 0장. `raw/`·`frames/`·`pilot_out/`·`PILOT_READOUT.md` 전부 부재. `sites.csv`는 EX_ 예시 12행뿐.** 논문은 이 트랙을 "사전등록된 계획"으로만 서술해야 함 |
| hfov 불일치 | `ACCOUNTING.md` §4.8 #4 (SCOPE-08) | md | 제출가능 | ⚠ **차단급: 추론 기본 hfov 69° vs 훈련 62.2°, 69°는 코퍼스에 0건.** 기본값으로 돌린 결과는 채점 불가 — 촬영 전 수리 |

### 1.8 4층 프레임워크 (서론의 출처)

| 자료 | 경로 | 형식 | 상태 | **중요·누락위험 메모** |
|---|---|---|---|---|
| **4층 프레임워크 정본 해설** | `Docs/experiment/V3_DESIGN_0823.md` **§2** | md | 제출가능 | **서론의 유일한 출처.** ③사전→①존재→④신뢰저해→②심각도→행동 도해(:78-94) + "단서는 정답이 아니라 증거다" + "4층은 모델 부품이 아니라 데이터·지도·평가의 설계 원리다" |
| 연구의 기원 | `Docs/experiment/V3_DESIGN_0823.md` §1 | md | 제출가능 | h·w/d² 신호 기하 · 근거리 스코프 제외 명시 · **"법이 단서를 의무화한다 ⇒ 위험이 단서를 낳는다"는 인과 방향** · 사고는 단서가 없는 곳에 몰린다 |
| 오독 5선 | `V3_DESIGN_0823.md` §2.5 | md | 제출가능 | **"모든 recall 주장은 FA-정합 병기가 이 프로젝트의 법이다"**가 여기 명문화 — 방법 절에 인용 가치 있음 |
| 계기판 3종 정의 | `V3_DESIGN_0823.md` §7.1 | md | 제출가능 | v3 서술용. **v2 공표치 44.7 %/0 %는 구off(A,D) 세대라 v3 계기판에선 참고치로 강등**됨 — 버전 여정 서사에서 혼동 주의 |
| v2 부검 | `V3_DESIGN_0823.md` §3 | md | 제출가능 | "버전 여정" 서사의 원형 |
| 온보딩 정본 | `Docs/experiment/Status/PROJECT_STATE_0823_v2.md` | md | 제출가능 | **구판 `PROJECT_STATE_0823.md`를 대체.** 구판 §5.1·§5.2·§6-4 인용 금지 |

### 1.9 레드팀 원장 (한계 절·정오표의 원재료)

| 자료 | 경로 | 형식 | 상태 | **중요·누락위험 메모** |
|---|---|---|---|---|
| 레드팀 지적→대응→잔여 | `experiments/weekend_0823/redteam/REDTEAM_0823.md` | md | 제출가능 | RR1–RR9. **"fully occluded" 폐기 지시(:196-203)의 원문** |
| **스테일 문장 정오표** | `experiments/weekend_0823/redteam/R6_line_edits.md` | md | 제출가능 | **줄 단위 치환 목록.** (a) 완전가림 계열 **18곳** · (d) aux 유의성 잔재 9곳 · (g) H·E CI 주장 **18곳** — 집필 전 일괄 처리 대상 |
| R1 신규성 | `redteam/R1_novelty.md` | md | 제출가능 | 관련연구 배치 근거 |
| R2 방법 | `redteam/R2_method.md` | md | 제출가능 | **조건화 공개 의무(탈락 %를 같은 표에 인쇄)의 출처(:226)** |
| R3 재현 | `redteam/R3_repro.md` | md | 제출가능 | 코퍼스 2,832 독립 재검증 · 이중계상 0 |
| RT-A 원장 | `experiments/v3_0823/redteam/RT_LEDGER_A.md` | md | 제출가능 | 차단급 4건(EVL-12·LAB-19·LAB-26·SCOPE-08) |
| RT-B 원장 | `experiments/v3_0823/redteam/RT_LEDGER_B.md` | md | 제출가능 | **N-5(aux OFF 실측)가 여기서 나옴.** 과녁 분할 맹점 자인(지지 27행 미검토) |
| 가정 대장 | `experiments/v3_0823/ASSUMPTION_LEDGER.md` | md | 제출가능 | 73행. **LAB-12의 "372" 인용은 369로 읽을 것.** LAB-13은 D61로 철회됨 |
| 트윈 tol 포렌식 | `experiments/v3_0823/TWIN_TOL_RESOLUTION.md` | md | 제출가능 | **"3자 불일치"는 오인용이었고 공표 수치 이동은 0건.** 공표 트윈은 `--tol 0.15` 산물로 md5 확정 |

### 1.10 v3 창의 발견 중 **v2 서술을 바꾸는 것**

| 자료 | 경로 | 형식 | 상태 | **중요·누락위험 메모** |
|---|---|---|---|---|
| FA 센서스 | `experiments/v3_0823/FA_CENSUS.md` | md | 제출가능(구/교정 양쪽) | **v2 오경보의 정체를 바꾼다: "FA는 씬이 아니라 그리드에 고정"** — 6 m 후퇴 검정에서 발화 밴드 불이동(기울기 −0.058~+0.387, 내용추종이면 ±1) |
| 규격본 | `submission_0830/tables/T13_fa_census.md` | md | 제출가능 | **⚠ `R^1.98`에 R²는 원장에 없다** — 적합도는 ln 잔차 3개뿐. "R² 법칙"으로 쓰면 없는 통계를 인용하게 됨 |
| — 융합 여유 | `FA_CENSUS.md` §4 | md | 제출가능 | **rgb∩depth OFF FA 교집합이 정확히 공집합(Jaccard 0.000), 3모델 동시 0/362, 88.4 % 단일 아키텍처 고유** — FA 절감형 융합의 실측 근거이자 미래연구 절의 최강 문장 |
| — 거리 법칙 | `FA_CENSUS.md` §3.3 | md | 제출가능 | **FA율 ∝ R^1.98이 문헌의 1/R²와 지수까지 일치** — 우리 그리드의 인공물이 아니라 문헌이 예고한 기하의 재현 |
| — 가족 판정 | `FA_CENSUS.md` §3.3–3.5 | md | 제출가능 | **장식형 기각(lift 1.01/0.98) · 대리선형 OFF 무효과 · 조명형 U자 비단조.** 단조인 것은 **칸 내 휘도 산포(34×)** = 광학 변화량 — CUE-OFF 독법의 역방향 재확인 |
| — none_in_fov 자기격파 | `FA_CENSUS.md` §9.4 | md | 제출가능 | **"on팔 FA 절반이 회계 밖"은 결함 GT의 산물** — 56.7 %→17.5 %, lift 1.91→1.19. 에이전트가 자기 권고 N4를 자진 강등. ⚠ **1.92×/1.91× 내부 불일치 존재 — 하나로 통일할 것** |
| **aux OFF 실측 (N-5)** | `ACCOUNTING.md` §4.9-4 · `redteam/RT_LEDGER_B.md` | md | 제출가능 | ⚠ **본 표 9런 전부 aux OFF.** DZ §0.1의 "aux는 학습돼 있음" 서술은 본 표 모델에 대해 **거짓**. **논문이 본 모델에 학습된 aux 헤드가 있다고 쓰면 안 됨** |
| 커버리지 감사 | `experiments/v3_0823/CUE_COVERAGE.md` | md | 제출가능 | **v2 off팔은 비균질 세대(8씬 ≈C / 25씬 ≈D)** — "off팔 = 단서까지 지운 팔"이라는 단순 서술은 부정확 |
| FA 현실 조사 | `experiments/v3_0823/FA_REALITY.md` | md | 제출가능 | 출처 37건. **Matthies&Rankin'03이 우리 단서 채널을 선제 기각하고 열화상으로 우회 = 본 연구가 앉은 구멍의 문헌적 좌표** · RELLIS-3D/ORFD에 음의 장애물 클래스 부재 |

---

## 2. 규격본 표 (`submission_0830/tables/`) — 15건, 전부 제출가능

각 파일은 **자기 완결**입니다: 제목 · 교정 GT 상태 · 프로비넌스 경로 · 원장 주석(`<!-- LEDGER: -->`) ·
캐비앗 라인. **모든 숫자는 원장 전사이며 재계산·추정치는 없습니다.**

| 파일 | 내용 | 교정 GT 상태 |
|---|---|---|
| `T01_headline_seed_table.md` | 본 표 4행 + 트윈 Δ + 밴드 열 | 구 GT(공표) · H/E/off 불변, V 이동 |
| `T02_fa_matched_dual_axis.md` | **프레임 축 + 칸 축 + τ=0.5 단위 반전 + 경보 부담** | 양 GT 동일(실측), V행만 이동 |
| `T03_twin_conditional.md` | 트윈-조건부 H/E/V + 씬별 분해 | H·E 동일, **V는 재발행 필요(165→177)** |
| `T04_cueoff_census.md` | 센서스 30/21 + VOID 18 전수 + 인용 규약 | 판정 불변(수리는 진단 기여) |
| `T05_gazebo_cross_sim.md` | 누출 검사 · 0픽셀 발화 · 사다리 역전 5/6 · 트윈 붕괴 | 해당 없음(다른 렌더러) |
| `T06_v2_rescore_corrected_gt.md` | **이동/불변 색인 전수** + 무결성 4/4 + C/D 분해 | **본 파일이 교정 GT 원장** |
| `T07_g7_repair_tiers.md` | 결함 5쌍 · tier 재집계 · 게이트 4종 | 본 파일이 교정 GT를 정의 |
| `T08_photometric_stress.md` | 광도 11변형 + τ 재적합 + 파일럿 수칙 3 | val 전용, **재발행 권고** |
| `T09_fusion_row_appendix.md` | 티어 축 0.000 · 거리 축 band1 발견 | 구 GT, **재발행 필요** |
| `T10_newmodels_appendix.md` | FA-정합 열세 + 훈련 실패 진단 | 구 GT 전용(교정 덤프 없음) |
| `T11_cluster_ci_withdrawal.md` | off팔 CI 확대 / H·E CI 철회 / aux 정정 | 불변 |
| `T12_adapter_free_detector.md` | 어댑터-프리 IoU + 트윈-조건부 −0.010 | 구 GT, **재발행 필요** |
| `T13_fa_census.md` | 그리드 고정 · R^1.98 · 융합 여유 · 가족 판정 | **양 GT 병기** |
| `T14_realworld_protocol.md` | AUC 사전등록 · 15/20 · 촬영 사양 · 파일럿 상태 | 해당 없음(데이터 0) |
| `T15_populations.md` | 전 모집단·분모 단일 참조 | **양 GT 병기** |

---

## 3. 문장 조각 (`submission_0830/fragments/`) — 12건

> **이원화 방지 규약** `[승용 D58 ⑥: "문장 조각은 색인 표시로 이원화 방지"]`
> 아래 조각은 **레드팀을 통과한 범위 한정 문장**입니다. 같은 내용을 다시 쓰면 **철회된 주장이 되살아납니다.**
> 산문은 Claude AI의 몫이지만, **이 12개 문장에 한해서는 새로 짓지 말고 이 파일에서 가져오거나,
> 바꿀 경우 아래 "무엇을 대체하는가"를 반드시 확인**해 주십시오.

| 조각 | 무엇을 대체하는가 (= 다시 쓰면 되살아나는 폐기 주장) | 배치 | **이원화 방지** |
|---|---|---|---|
| `F01_yolo_adapter_scope.md` | R.1 "검출 패러다임 상한" 일반화 | §5.2 row 4 | 🔒 **원문 고정** — RT-D가 유일 정본 |
| `F02_rgb_surviving_claim.md` | "RGB .688 우위 / 역전이 발견" | §5.2 본 표 직후 | 🔒 **원문 고정** — RT-A가 유일 정본 |
| `F03_cluster_ci_withdrawal.md` | "9/9 CI가 0을 배제" | §5.3 + §5.6 | 🔒 **원문 고정** — 철회지 축소 아님 |
| `F04_hidden_not_fully_occluded.md` | "fully occluded / 완전가림" (18곳) | §5.1 + §5.3 | 🔒 **폐기어** — 치환 목록은 R6_line_edits (a) |
| `F05_h_claim_scoped_3b.md` | 무범위 H 주장 | §5.3 + §5.6 | ⚠ **범위 필수** — 결재 #2 안 A(3b 한정) |
| `F06_cueoff_neutral_verdict.md` | D46 "모델이 단서 어휘를 읽는다" | §개입실험 | 🔒 **원문 고정** — §6.4 골격이 정본 |
| `F07_census_citation_rule.md` | 헤드라인 30만 인쇄 | 결과표 캡션 + 방법 | ⚠ **30·21 병기 의무** (A2-7) |
| `F08_dual_axis_obligation.md` | 프레임축 단독 인쇄 | §5.2 각주 + 방법 | ⚠ **양축 병기 의무** (§4.9-2) |
| `F09_aux_heads_off.md` | "본 표 모델은 aux가 학습돼 있다" | §5.1 + 부록 | ⚠ **사실 오류 방지** — DZ §0.1 정정 대상 |
| `F10_e_tier_far_field_only.md` | 무범위 E 주장 | §5.1 + §5.6 | ⚠ **범위 필수** — 결재 #11 |
| `F11_gazebo_claim_boundary.md` | 트윈 붕괴를 단서 증거로 인용 | §교차-시뮬 | ⚠ **안전 주장 2종만** (§7-2) |
| `F12_near_range_out_of_scope.md` | 근거리 실패를 하나의 원인으로 뭉뚱그림 | §5.4 + §5.6 + 방법 | ⚠ **세 원인 구분 필수** |

---

## 4. 그림·정성 패널 자산 — **로컬 전용 판정 포함**

| 자산군 | 경로 | 수 | 상태 | **중요·누락위험 메모** |
|---|---|---|---|---|
| recall–FA 곡선 | `experiments/weekend_0823/rt_response/figs/` | 2 (png+pdf) | 제출가능 | **리포 유일의 벡터 그림.** 운용점 불일치를 한 장으로 설명 |
| strict-H 트윈 잔차 패널 | `experiments/weekend_0823/rt_response/panels/` | 7 (contact sheet + 6) | 제출가능 | **"완전가림 아님"의 시각 증거** — F04 조각과 짝. 씬별 min/median/max 쌍 |
| Gazebo 정성 패널 | `experiments/weekend_0823/gazebo/out/panels/` | 6 | 제출가능 | 0픽셀 발화 컷과 그 대조군이 **육안으로 구분 불가**한 것이 요점 |
| mainrun 정성 뷰 | `experiments/mainrun_0819/viz/` | 12 (`fa_off_*`·`hitH_*`·`missH_*`) | 제출가능 **(단, v1 스코프)** | ⚠ **추적 가능한 유일한 hit/miss 패널군이지만 `s20260819` = 야간 런 = v1 336프레임 코퍼스다.** 논문 헤드라인은 **v2**이므로, 이 컷을 v2 정성 예시로 쓰면 스코프 불일치. **v2 정성 패널은 전부 로컬 전용**(아래 행) — 이것이 이 패키지 최대의 누락위험 |
| 밤런 진단 그림 | `experiments/nightrun_0820/{narrative/diag_v2,tau_curves,figures}/` | 13 | 제출가능 | τ 곡선·트윈 forest·occupancy — 부록 후보 |
| dayrun 진단 그림 | `experiments/dayrun_0820/narrative/diag_v1/` | 4 | 제출가능 | v1 스코프 |
| 광도·시점 그림 | `photometric/photometric_stress.png` · `a3_viewpoint/a3_viewpoint.png` | 2 | 제출가능 | — |
| 홀 프로브 뷰 | `experiments/probe_holes_0820/eval/*/viz/` | 105 | 제출가능 | 디렉터리 이름이 `eval/`이라 규칙을 피해감(33 MB) |
| **본 표(v2) 런 정성 패널** | `experiments/dayrun_0820/runs/v2/*/viz/` | **119** | **🔴 로컬 전용** | ⚠ **본 패키지 최대 누락위험.** 본 표 9런 + aux의 **v2 정성 패널 전량**이 `**/runs/**/*.png`로 GitHub에 **없다.** 즉 **논문 헤드라인(v2)의 정성 예시를 공개 리포에서 뽑을 방법이 현재 없다** — 위 mainrun 12장은 v1 스코프라 대체 불가. §6-C6이 처분 항목 |
| **YOLO 런 패널** | `experiments/dayrun_0820/runs/yolo_s{42,43,44}/` | **57** | **🔴 로컬 전용** | ⚠ 같은 규칙. 검출기 행 정성 예시 필요 시 별도 조치 |
| **V2S 런 패널** | `experiments/weekend_0823/v2s/runs/*/viz/` | **104** | **🔴 로컬 전용** | V2S는 롤백이라 논문 비중 낮음 — 우선순위는 낮으나 기록 |
| CUE-OFF 스모크 | `experiments/weekend_0823/cue_audit/smoke/scene{12,17,20}/` | 3 | **🔴 로컬 전용** | `**/cue_audit/smoke/` 규칙. **cue_audit에는 그 외 정성 패널이 없다** — 개입실험 절에 쓸 그림이 부재 |
| Gazebo 원본 프레임 | `experiments/weekend_0823/gazebo/frames/` | 216 (45 MB) | 제출가능 | ⚠ **어떤 규칙에도 안 걸리는 최대 추적 blob** — 공개 리포 용량 관점의 검토 대상 |

> **v3_0823/ 에는 그림 디렉터리가 하나도 없습니다.** FA 센서스·EVL12·재채점은 전부 표/JSON 산출입니다.
> **v3 창 발견을 그림으로 보이려면 새로 그려야 합니다**(현재 미제작 — 누락위험).

---

## 5. 인용 사고 방지 — 상위 목록 (심사자가 먼저 찾을 순서)

| # | 위험 | 정답 |
|---|---|---|
| 1 | "분모 372" | **369** — `ACCOUNTING.md` §4.2·D55의 372는 오기(§4.4가 정정) |
| 2 | 트윈 V 분모 219 | **177** — 신규 39프레임 중 12쌍만 포즈 필터 통과 |
| 3 | b2 트윈-조건부 무조건부 몫 "46.7 %" | **0.305** — 46.7 %는 상대 하락폭(원장 인쇄치 아님) |
| 4 | 칸/FA프레임 "4.29" | Depth **시드 합산 4.29 / 시드 평균 5.50** — 추정량 명시 필수 |
| 5 | `R^1.98`의 "R²" | **R²는 원장에 없다** — 적합도는 ln 잔차 [+0.047, −0.115, +0.068]뿐 |
| 6 | none_in_fov lift "1.92× vs 1.91×" | 같은 수(.567/.296=1.9155…)의 두 표기 — **하나로 통일** |
| 7 | "오라클 6씬" (D42) | **3씬 / 5쌍** |
| 8 | Gazebo 사다리 역전 "4/6" (D48) | **5/6** |
| 9 | `METRICS.md:360`의 "39 cells" | **v1 스코프 · 불변** — G7의 39와 무관한 우연 동수 |
| 10 | `RESULTS_DRAFT.md:136-137`의 "39" | **v1 스텝게이트 값** — 역시 무관 |
| 11 | 1006× vs 672× (scene12 footprint) | 같은 현상, **참조 라운드가 다름** — 참조를 밝히고 인용 |
| 12 | "resnet50 ≈ resnet34 동급" (D51) | **D52가 정정** — FA-정합 전 지점에서 −0.19~−0.25 |

---

## 6. 재발행 필요 목록 (제출 전 반드시)

> 근거: **D65 ④** — "V행을 인용하는 표는 교정 GT 재발행 필요."
> 공통 전제: 교정 GT = `experiments/v3_0823/dataset_manifest_v2corr.json`(정본 B) ·
> τ_op 0.5 고정 · **τ* 재적합 금지**(공표 고정값 사용).

### A. 교정 GT 재채점이 **아직 없는** 것 (측정 필요, GPU)

| # | 자산 | 왜 | 재생성 명령 | 담당 |
|---|---|---|---|---|
| **A-1** | **YOLO 3런** (`SEED_TABLE.md` §4 V행 0.150 ± 0.028 및 :69-71, :93-95) | 본 표 4행 중 유일하게 미측정. E/H=0은 논리적 불변이나 **V행은 미측정** | `run_queue_v2.sh`의 yolo 블록을 `--manifest .../v3_0823/dataset_manifest_v2corr.json`으로 1회 재실행 (τ 0.25 고정) | Claude Code (GPU, flock) |
| **A-2** | **`rgb_s42_aux` 1런** (`SEED_TABLE.md` §5 aux 부록 V·cell_f1·cell_precision) | 부록 표가 구 GT 분모 위에 있음 | `code/rescore_v2corr.sh`에 `rgb_s42_aux` 추가 후 1런 | Claude Code (GPU) |
| **A-3** | **부록 인코더 6런** (resnet50 ×3, convnext ×3) | 교정 덤프 없음. 스크립트가 `--corr`+`--appendix`를 상호 배타로 강제 | 우선순위 **하** — FA-정합 H는 구조적 불변이므로 부록에 "구 GT 측정" 태그만 붙여도 무방 | 판단 필요 |

### B. 이미 측정됐고 **문서에 반영만 하면** 되는 것 (GPU 0)

| # | 자산 | 조치 | 원장 |
|---|---|---|---|
| **B-1** | `SEED_TABLE.md` §1 3행 · §2 twin(all) · §3 per-seed | V·det·cell_f1·cell_recall·cell_precision 교체, twin(all) rgb 0.314→**0.333** | `V2_RESCORE.md` §6.2-A · `T06` §5.1 |
| **B-2** | `F1_FA_MATCHED.md` :5, :79-81, :87-92, :38-73 | "V n=180"→**219**, §3·§4·per-seed의 **V 열만** 교체 (H·E·τ·FA는 무편집) | `V2_RESCORE.md` §3.2 |
| **B-3** | `F2_TWIN_CONDITIONAL.md` :33, :37-39, :55-79 | "V tier n=165"→**177** + V 행 9줄 | `V2_RESCORE.md` §5.3 |
| **B-4** | `METRICS.md:628` **+** `RESULTS_DRAFT.md:269` | "test 327 / corpus 1038" → **369 / 1101**. ⚠ **반드시 동시** — 하류 `/327` 전부와 파생 %가 여기 매달림 | `T15` |
| **B-5** | `METRICS.md:1235` **+** `RESULTS_DRAFT.md:146` | "corpus V 726 → 657". ⚠ **동시** — 센서스 표 밖의 유일한 corpus-V 수치 | `T15` |
| **B-6** | `METRICS.md` **§RT.4 전체**(:1103-1131) + `RESULTS_DRAFT.md:552` | none_in_fov 81→**39**, 19.9 %→**9.6 %**, scene07 51→**9**, RGB/Depth/B2 3시드 평균 재계산 | `V2_RESCORE.md` §6.3-B1 |
| **B-7** | `METRICS.md:698-699` · `:671-677` · `:1239-1247` | 96/327=29.4 % → **26.0 %** · 양성 칸 2,691→**2,856** · 코퍼스 센서스 V 801·H 195·Hw 33·none 315 | `T15` |
| **B-8** | `ACCOUNTING.md` §3.1 · §3.4 행 6 | 구 GT 라벨링 + 교정 병기(369), §3.4 행 6 기입 | ⚠ **append-only** — 오케스트레이터 직렬화(D63) |
| **B-9** | `FUSION_ROW.md` · `PHOTOMETRIC_STRESS.md` · `METRICS.md §RT.3` | 각각 V행·val 분모·V/none 행을 교정 GT로 재산출 | 재실행 명령은 각 문서 §0 |
| **B-10** | `redteam/R6_line_edits.md` (a)(d)(g) 45곳 | 완전가림 18 · aux 유의성 9 · H·E CI 18 — **집필 시작 전** 일괄 치환 | `R6_line_edits.md` |

**재생성 명령 (교정 GT 재채점 표준)**
```bash
R=/home/vislab/Desktop/work_sy/Practice_NegObs
# ① GPU 재채점 (tmux 세션, 매 런 flock -o /tmp/negobs_gpu.lock)
tmux new-session -d -s v2rescore
tmux send-keys -t v2rescore "bash $R/experiments/v3_0823/code/rescore_v2corr.sh" Enter
# ② 트윈 재분석 (CPU)
bash $R/experiments/v3_0823/code/rescore_twin.sh
# ③ 집계·게이트·전 표
PYTHONNOUSERSITE=1 CUDA_VISIBLE_DEVICES= /home/vislab/miniconda3/envs/env_seg/bin/python \
  $R/experiments/v3_0823/code/rescore_tables.py
```

### C. 데이터 자체가 없는 것 (재생성 아님 — 수집 필요)

| # | 자산 | 상태 | 담당 |
|---|---|---|---|
| **C-1** | **실측 파일럿 20컷 + 캘리브레이션 1컷** | **미촬영(0장).** 사전등록 판독선은 고정돼 있음 | **승용** (D58 · `README_PILOT.md` 순서 2) |
| **C-2** | `sites.csv` 수정 | azimuth 부호 · 칸 이름 V1화 · tier 세분 · 4열 추가 | Claude Code, **촬영 직전 1회** (결재 #6) |
| **C-3** | hfov 수리 (SCOPE-08) | 훈련 hfov를 config 기록 + infer 경고 + 안내서 명시 | **촬영 전 필수**, Claude Code |
| **C-4** | Gazebo depth 팔 | `--depth` 미빌드로 `*_depth.npy` 0건 | 다음 창 1순위 (`make_worlds.py --depth`) |
| **C-5** | v3 창 발견용 그림 | `v3_0823/`에 그림 디렉터리 부재 | 필요 시 신규 제작 |
| **C-6** | 정성 패널의 공개 경로 | 본 표 런 패널 119장이 `.gitignore`로 비공개 | 판단 필요 — 선별 컷을 추적 경로로 복사할지 |

---

## 7. 이 패키지가 **하지 않은 것** (정직 기록)

- `ACCOUNTING.md`·`SEED_TABLE.md` 등 **기존 원장을 한 글자도 수정하지 않았습니다** — 신규 파일 전용 지시 준수.
  따라서 §6-B의 반영 작업은 **아직 이뤄지지 않았습니다.**
- **git 명령을 쓰지 않았습니다.** 로컬 전용 판정은 `.gitignore` 규칙 + 파일 실재 확인에 근거하며,
  "커밋된 적 없는 추적 가능 파일"은 이 방법으로 구분되지 않습니다(해당 파일은 §4에서 '제출가능'으로 표시됨).
- **수치를 새로 계산하지 않았습니다.** 규격본의 모든 값은 원장 전사이며, 원장에 없는 통계
  (예: `R^1.98`의 R²)는 **만들지 않고 부재를 명시**했습니다.
