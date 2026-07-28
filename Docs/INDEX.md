# Docs 색인

> **신규 합류는 `STATUS.md` 부터.** 현재 상태·읽는 순서·다음 할 일이 20줄에 있다.

읽는 순서: `STATUS.md` → `reports/realism_v1_final.md` → `briefs/realism_brief_v1.md`(+개정이력)
→ `audit_v4/user_feedback_v5_1.md` → 이 색인

⚠ `surveys/realism_gap_2026-07-28/ZZ_synthesis.md` 는 격차 조사 **원안**이며 서술 다수가
이후 정정됐다. 반드시 `reports/realism_v1_final.md` §3(정정 목록)을 먼저 볼 것.

## 루트
- **`STATUS.md`** — 현재 상태판. 라운드마다 여기부터 갱신한다
- `CREDITS.md` — 외부 에셋 출처·라이선스 (CC-BY 크레딧 포함)

## reports/ — 사실화 v1 라운드 (2026-07-28)
- **`realism_v1_final.md`** — **총괄·인수인계 1순위.** 결과 수치 · 구현 · 정정 · 버그 · 결정 대기
- `realism_baseline.md` — Phase 0 기준선(측정 도구 정식화·3씬 기준선)
- `realism_phase1.md` — Phase 1 "검증의 날"(스파이크 7종·렌더 예산·RTX 능력)
- `realism_phase2.md` — Phase 2 룩 레이어(구현·게이트·MDL 이력)
- 진단: `deadpixel_diag_d3.md`(D3 죽은 픽셀 89.8%가 상수색 아스팔트) ·
  `deadpixel_diag_0701.md`(07/01 — 그늘에서 노멀맵이 원리적으로 무효인 이유)
- 조달·매핑: `const_color_texture_map.md` · `sky_procurement_v1.md` · `real_reference_expansion.md`
- 감사: `code_audit_realism_v1.md`(치명 4·중대 10) · `license_audit_v1.md` ·
  `doc_consistency_audit_v1.md` · `regression_tool_v1.md`

## legacy/ (이력 보존 — 현행 아님)
- `scene_redesign_v5_proposal.md` · `nanobanana_batch1_geometry_map.md` ·
  `scene_library_v3_status.md` · `multi_scene_brief_v3.md` · `realism_rubric_v1.md`

## briefs/ (설계 지시·사양)
- **`realism_brief_v1.md`** — **사실화 v1 지시서 + 개정 이력 rev.1.**
  본문과 rev.1 이 충돌하면 **rev.1 이 우선**한다
- `multi_scene_brief_v5.md` — 본편 21씬 구현 사양
- `../legacy/multi_scene_brief_v3.md` — 이전 사양 (§A 회귀 체크리스트는 여전히 유효)
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


## surveys/realism_gap_2026-07-28/ (격차 조사 6팀 + 후속)
- `ZZ_synthesis.md` — 종합·실행계획. **원안이며 정정 다수** (위 경고 참조)
- `00`(감독 직접측정) `A`~`G`(6팀 원보고서)
- `H_rtx_capability_verification.md` — RTX 능력 검증. ZZ 서술 5건 정정
- `I_ks_dimension_verification.md` — 국내 규격(KS·KCS·법령 도면 판독). 베벨값 근거

## scripts/
- `imgstats.py` — **공식 측정 도구**(하늘/지면 분리·중앙값·실사 n=54 참고 게이트)
- `regression_check.py` — 회귀 검증(478컷 23초, GPU 불요)
- `spike_realism.py` · `rtx_probe.py` — Phase 1 스파이크 랩
- `make_compare_sheet.py` — 전후 비교 시트 · `make_hq_sheet.py` — 21씬 HQ 시트
- `rounds/` — 완료된 렌더 체인 보관
