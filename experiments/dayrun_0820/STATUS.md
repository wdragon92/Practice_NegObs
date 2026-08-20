# STATUS — dayrun_0820 (30분 갱신)

## 15:16 — 개시
- DAYRUN_BRIEF_0820 확인. GPU 유휴(3.2GB 데스크톱). 트윈 H Δ 0.2398[0.156,0.331] 검증
  (브리프 0.240 인용 정확).
- 병렬 투입 4기: P1 그리드 V1 재라벨+불변량 게이트 / P3 진단 3종 / P2 보강 렌더 준비
  (샘플러 편향 opt-in+프로브) / P4 레시피 v2 코드(20칸 일반화·선택지표·bias init·
  flip 순열·오버샘플). 척추 = P1→P2→P4.

## 16:00 — 진단 3종 착지 (narrative/diag_v1/)
- ① 사전확률-FA 결합 실증: ρ=0.96(RGB). FA 질량 87% = C2(48%)+N3(39%) 2씬 집중.
- ② 브리프 가설 반증: 트윈 쌍에서는 band3 Δ가 최대(0.348/0.559) — "증거는 트윈 있는
  씬에서, 사전은 트윈 없는 씬에서" 분리 구조. V1 분할+bias init의 정량 근거 확보.
- ③ C2 = 외관 환각 판정(off 지면 평탄 16mm) + 씬 토글 비보존 결함 발견(선신고 제안행).
  트윈 배제 원인 = ground_z 데이텀 이동 → v2부터 ≤0.15m 허용오차(D20).
- 16:10 P2 GO: 캠 밴드 opt-in 패치 검증(트윈 보존·CAM-2 캡 교차·가드레일), 프로브 H프레임 시각 확인. E 16씬까지 ~111분. P1(불변량 게이트+E후보)·P4 대기.
- 16:20 P4 착지: gridspec 모듈·N칸 일반화·H인지 선택지표·bias init·hflip순열·오버샘플·split v2(dry: scene17→val, s09 train 잔류)·큐 러너 — 20칸 스모크 green. P1 대기.

## 16:30 — P1 PASS + 보강 렌더 개시
- 불변량 게이트 PASS(1584/1584 동일, pregate 중첩법 0 위반). V1 라벨·manifest v2·
  게이트(ALL BINDING PASS) 완료. band3 질량은 3b(8-12m)에 집중(프레임당 양성
  4.92→6.84). 희소 셀 0 — 보강 가치는 셀 커버리지가 아니라 E 티어 다양성으로 확인.
- 보강 렌더 가동: H 4씬 + E 14씬 × 양팔, seed 20260820, 편향 밴드, ~100분 계획.
- 완료 후: 4라운드 통합 재라벨(V1) → manifest v2.1 → split v2 → 9런 큐.
- 16:45 Phase7·8 착지: infer_photo.py(letterbox/squash 분기 발견 — squash가 per_frame 1.6e-4 재현, 전처리 체인 검증 덤) + brief_prof_0820.md(71줄, 이미지 링크 검증). YOLO prep·보강 렌더 진행 중.
- 17:10 YOLO prep 착지(마스크 552·venv·det2cell·오라클 천장 E/H=0 증명). 보강 렌더 대기.

## 16:45 — 보강 렌더 1차 무효(팔 충돌) → 즉시 재렌더
- 버그: 라운드명에 arm 부재 → off가 on을 덮어씀(D23). 4라운드 체계로 수리, 재가동.
  1차 충돌본은 존치·제외. 완료 ~17:40 예상, 이후 통합 재라벨 → 9런 큐.
- 17:20 boost_h 조기 라벨: on팔 87/96 strict-H(90.6%) — test H 21→60 예상(목표 40 초과 달성). s09 트윈 24 불일치(데이텀, train이라 무영향). e 렌더 2/14 진행.
- 18:50 E2 렌더 가동(D24: E밴드 재설계 저고도·중거리 + seed 분리). 병합은 ::round 접미사로 유일화. 큐 ~19:40 개시 예정.

## 19:10 — 데이터 층 완결, v2 큐 개시
- E2 렌더 완료(E 24, 재설계 4배 효율). 병합 2832프레임(::round 접미사 유일화).
- split v2: test 7씬 D18 고정(--force-test 전량 핀 — 옵티마이저 재탐색 차단),
  moved=scene20(H6 규칙 최소). test H 96 · E 45 (목표 초과). 게이트 구속 전부 PASS.
- 9런 큐 가동(19:08 rgb_s42부터). YOLO 데이터셋 재구축(마스크 1104, 경고 0 —
  common.py 그룹핑/스템 D24 패치 2건). 다음: 큐 완료 → YOLO 3런 → aux → DAYRUN_REPORT.

## 20:15 — v2 첫 결과: RGB H 0.59~0.88 (어제 0.05~0.33)
- ep1 붕괴 소멸(best ep 9/23/25/15/30). RGB가 확장 H셋에서 Depth 역전(0.59-0.88 vs
  0.41-0.47) — 원거리 H에서 depth 신호 열화 가설, CI·트윈으로 확정 예정. Depth FA
  0.05/0.007 급감. RGB 시드 간 recall-FA 트레이드오프 편차는 평균±범위로 표기.
- 큐 순항(depth_s44 진행, B2 대기).

## 20:55 — 9런 완료(20:48) + YOLO 개시
- SEED_TABLE 착지: RGB H 0.688±0.141 / E 0.556±0.378 / FA 0.359±0.127, Depth H
  0.438±0.031 / FA 0.042, B2 H 0.229±0.156(소자료 transformer 한계). 트윈 H Δ:
  RGB 0.285 / Depth 0.407 / B2 0.110. band1 recall 0(근거리 GT 희소+무시) 주목.
- YOLO 3시드 트랙 가동(train→predict→det2cell→eval). aux 픽셀 손실 구현 에이전트
  투입(브리프 Phase 6 — P4 범위 밖이었음). 이후: aux 1런 → DAYRUN_REPORT.
- 21:10 aux 픽셀손실 구현 착지(기본 OFF 무변경 실증, run_aux.sh 대기). YOLO 진행 중 — 종료 후 aux 1런 → DAYRUN_REPORT 조립.
- 21:30 YOLO 러너 인자 수정(--pred-labels, train skip) 후 재개. s42 훈련은 재사용.

## 21:50 — DAYRUN_REPORT 조립 완료 (CPU only), GPU 2건 보류로 종료
- **GPU 양보**: 사용자가 로봇 baseline 구동 중 → `CUDA_VISIBLE_DEVICES=""`로 리포트만 조립.
  YOLO s43/s44 + aux 1런은 **의도적 PENDING**(재개 조건 = 사용자 세션 종료, 스크립트 그대로
  재실행하면 완료분은 skip).
- 산출: `DAYRUN_REPORT.md`(완료표·V0→V1·결과표·승인란 8건·캐비앗 8건·잔여 6건) /
  `narrative/brief_prof_0820.md` ⑤ 표 4행 V1 수치로 채움(YOLO는 s42 단일 시드 명기).
- Phase 최종: 1·2·3·4·7·8 완료 / 5 부분(s42만) / 6 부분(코드·드라이런 완료, 런 보류).
- **대조 중 발견한 불일치 3건**(리포트 ⑤에 명기):
  ① band1 recall 0은 **RGB·B2만**이고 Depth는 0.188±0.064 — "전 모델 0"은 부정확.
  ② YOLO 오라클 천장(V .514/det .404)은 **보강 전 코퍼스**(manifest_v2 + split_v2,
     test H21/E9)에서 잰 값 — s42 실측(v2_full, H96/E45)과 분모가 다름. 재측정 ~2분(CPU).
  ③ Phase 7 `infer_photo.py`는 dayrun_0820/code/가 아니라 `mainrun_0819/code/`에 있음.
- 추가 캐비앗: test E 45장 = scene18 단일 씬, H 96장 = scene14+15 두 씬 → E/H recall은
  일반화가 아니라 소수 씬 성적으로 읽어야 함(Depth E가 3시드 모두 정확히 0.600인 이유).
- 다음 인스턴스 할 일(GPU 불요, 지금 가능): 오라클 천장 재측정 / Depth 하락 가설을
  밴드별 recall로 검증 / `P1_GRID_V1.md` §5.3 "val 1A 양성 0" 플래그를 최종 val
  (scene08·20·D3) 기준으로 재확인.
- 21:58 오라클 천장 full 재측정(V .400/det .220, E·H=0 불변) — 보고서 갱신. GPU 잔여
  2건은 사용자 baseline 세션 종료 후 재개 규칙(clean_yolo 프로세스 부재 확인 시).
