# Docs 색인

신규 합류 시 읽는 순서: `audit_v4/user_feedback_v5_1.md` → `briefs/multi_scene_brief_v5.md`
→ `surveys/realism_gap_2026-07-28/ZZ_synthesis.md`

## 루트 (현행 기준 문서)
- `scene_redesign_v5_proposal.md` — **v5 재설계**(사용자 전면 채택): 처분표(교체 7·재해석 3·유지) + 공통 레이어
- `nanobanana_batch1_geometry_map.md` — 배치1(N/C/D 12씬) 기하 사양 + 판정 이력(§공통 3)
- `scene_library_v3_status.md` — 21씬 상태표 (v3 시점 이력)

## briefs/ (설계 지시·사양)
- `multi_scene_brief_v5.md` — **본편 21씬 현행 구현 사양**
- `multi_scene_brief_v3.md` — 이전 사양 (§A 회귀 방지 체크리스트는 여전히 유효)
- `multi_scene_brief_v2.md` — 이력
- `scene01_design_brief.md` — scene01 설계·재질·점자블록 (텍스처 소스 슬러그 표)
- `NegObs_인공씬1호_계단_구현지시서.md` — 최초 지시서 (편향 있음 — scene01_design_brief 가 교정본)

## audit_v4/ (감사·현실성 규약·판정·픽스로그)
- `user_feedback_v5_1.md` — **현실성 규약**: 전역 §1~5(나무 v2·볼라드 규정·배치 비정형·틴트 지터·지형 곡률)
  + v5.2 원칙 §6~9(조경 개방감·점자블록 기본 OFF·임의 팻말 금지). 씬별 조치 표 포함
- `audit_scene01-05.md` … `audit_scene16-21.md` — 4팀 전수 감사
- `consolidated_fix_plan.md` — 통합 수정 계획
- `judge_v5_*.md` · `judge_v6_rt_*.md` · `judge_v7_rt_*.md` · `judge_v8_rt.md` — 라운드별 판정문
  (각 파일 말미에 **감독 결정** 부록)
- `fixlog_*.md` — 구현 픽스로그 (I1~I5, FA/FB, N1~N4, VA~VD, W0~W7, X1~X3, Y1)
- `library21_final_hq.png` — **본편 21씬 최종 컨택트 시트** (생성기 `scripts/make_hq_sheet.py`)
- `scene_overview_v4.png` · `keep15_v5pt_hq.png` — 이전 세대 시트

## surveys/ (조사)
- `realism_gap_2026-07-28/` — **사실성 격차 조사 (6팀 병렬)**
  - `ZZ_synthesis.md` — **종합·실행계획. 여기서 시작**
  - `00_supervisor_direct_diagnosis.md` — 감독 직접 측정 (실측 기준선)
  - `A_prior_work_fidelity_benchmark.md` — 선행연구 충실도 벤치마크 (L1/L2/L3 등급)
  - `B_sim2real_transfer_factors.md` — sim2real 전이 요인
  - `C_current_code_audit.md` — 코드 전수 감사 (미사용 에셋·지름길 학습 조건)
  - `D_isaacsim_untapped_capabilities.md` — Isaac Sim 미활용 역량
  - `E_realism_measurement_protocol.md` — 측정 프로토콜 (도메인 판별기·PAD)
  - `F_pipeline_options_and_recipes.md` — 파이프라인 대안 (스택 유지 결론)
  - `G_env_art_techniques.md` — 환경 아트 기법
  - `_context_for_agents.md` — 조사팀 공통 컨텍스트
- `batch1_geophysics_realism_survey.md` — 배치1 물리 근거(태양고도·알베도·젖음/눈 광학·표준 치수) + 씬 파라미터 대조표
- `stair_typology_survey.md` (T1~T8) · `stair_typology_survey_v2.md` (T9~T21)
  — 계단 유형 조사. v2의 "명소" 노선은 v5에서 일상 공간 노선으로 폐기

## reports/ (완료 보고·판정 기준)
- `realism_rubric_v1.md` — 판정관용 실사성 루브릭 (전 씬 공용)
- `scene01_completion_report.md` · `multi_scene_completion_report.md`
- ※ 룩체크 v1(자연 도랑) 보고서·지시서는 `../../Practice_TerrainGen/Docs/` 로 분리(07-27)

## reference_photos/
- 캠퍼스 계단 참고사진 2장 (scene01 근거)

---
호환 심링크: `Docs/multi_scene_brief_v3.md` → `briefs/`, `Docs/realism_rubric_v1.md` → `reports/`
