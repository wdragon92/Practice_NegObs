# Docs 색인

> **신규 합류는 `STATUS.md` 부터.** 현재 상태·읽는 순서·다음 할 일이 요약돼 있다.

읽는 순서: `STATUS.md` → `briefs/process_spec_v1.md`(상설 규칙) →
`briefs/gallery_fix_plan_v1.md`(당면 계획) → `audit_v4/gt_changes_w3.md`(GT ledger) → 이 색인

⚠ `surveys/realism_gap_2026-07-28/ZZ_synthesis.md` 는 격차 조사 **원안**이며 서술 다수가
이후 정정됐다. 반드시 `reports/realism_v1_final.md` §3(정정 목록)을 먼저 볼 것.

## 루트
- **`STATUS.md`** — 현재 상태판. 라운드마다 여기부터 갱신한다
- `CREDITS.md` — 외부 에셋 출처·라이선스 (CC-BY 크레딧 포함)

## briefs/ (설계 지시·사양)
- **`process_spec_v1.md`** — **상설 운영 규칙 (08-05 결재 R1~R7).** 검증 floor · ledger 법 ·
  round 규약 · do-not-touch · parked register. 구 `w3_execution_spec_v1.md` 는 전문 이관 후 RETIRED(참조용 보존)
- **`gallery_fix_plan_v1.md`** — `260805_w3_doctrine` 검수 반영 계획 (씬별 작업 + 실행 순서)
- `realism_brief_v1.md` — 사실화 v1 지시서 + 개정 이력 rev.1 (본문과 충돌 시 **rev.1 우선**)
- `multi_scene_brief_v5.md` — 본편 21씬 구현 사양 (`v2`·`../legacy/multi_scene_brief_v3.md` 는 이력,
  v3 §A 회귀 체크리스트는 여전히 유효)
- `ground_kit_spec_v1.md` · `t1_material_layer_spec_v1.md` · `lighting_camera_variation_spec_v1.md`
  — W2 기반 공사 사양 (지면 킷 · 재질 레이어 · 조명/카메라 변주)
- `s3_scene07_10_rebuild_spec_v1.md` · `scene05_stage_redesign_v1.md` — 씬 재건 사양
- `scene01_design_brief.md` — scene01 설계·재질·점자블록 (텍스처 소스 슬러그 표)
- `NegObs_인공씬1호_계단_구현지시서.md` — 최초 지시서 + **cue 토글 시스템 원 사양(§7)**
  (편향 있음 — `scene01_design_brief.md` 가 교정본)
- `placement_rules_v1.yaml` — placement_lint 규칙 (spec §2.2 검증 floor 입력)

## audit_v4/ (감사·현실성 규약·판정·픽스로그·ledger)
- **`gt_changes_w3.md`** — **GT ledger (append-only · 선신고).** 상태 어휘·re-cache 규칙은 §0~§2 원본
- `user_feedback_v5_1.md` — **현실성 규약**: 전역 §1~5(나무 v2·볼라드 규정·배치 비정형·틴트 지터·지형 곡률)
  + v5.2 원칙 §6~9(조경 개방감·점자블록 기본 OFF·임의 팻말 금지). 씬별 조치 표 포함
- `audit_scene01-05.md` … `audit_scene16-21.md` — 4팀 전수 감사
- `consolidated_fix_plan.md` — 통합 수정 계획
- `judge_v5_*.md` · `judge_v6_rt_*.md` · `judge_v7_rt_*.md` · `judge_v8_rt.md` — 라운드별 판정문
  (각 파일 말미에 **감독 결정** 부록)
- `fixlog_*.md` — 구현 픽스로그 (I1~I5, FA/FB, N1~N4, VA~VD, W0~W7, X1~X3, Y1)
- `library21_final_hq.png` — 본편 21씬 컨택트 시트 (생성기 `scripts/make_hq_sheet.py`)
- `scene_overview_v4.png` · `keep15_v5pt_hq.png` — 이전 세대 시트

## surveys/ (조사)
- **`cue_arrangement_survey.md`** — **맥락 단서 배치 조사.** 낙차 유형×동반 요소 매트릭스(§1) ·
  단서-낙차 조건부 확률과 설계 목표(§2, §2.5) · 우리 33씬 대조(§4)
- **`cue_expansion_survey_v1.md`** — 토글 단서 확장 조사+계획 (**계획 전용 — 사용자 결재 대기**)
- `korean_pedestrian_geometry.md` · `korean_urban_backdrop.md` — 국내 보행 기하·도시 배경 조사
- `era_consistency_survey_v1.md` — 연대 정합 조사 (개보수 어휘 12칸)
- `stair_typology_survey.md` (T1~T8) · `stair_typology_survey_v2.md` (T9~T21) — 계단 유형 조사
  (v2의 "명소" 노선은 v5에서 일상 공간 노선으로 폐기)
- `batch1_geophysics_realism_survey.md` — 배치1 물리 근거(태양고도·알베도·젖음/눈 광학·표준 치수)
- `scene_composition_audit.md` · `_dimension_index.md` · `s3_research_numbers_v1.md`
  — 구성 감사 · 치수 색인 · S3 조사 수치
- `w3_intake_policy.md` · `w3_intake_01_05.md` · `w3_intake_06_10.md` · `w3_intake_v2_images.md`
  — W3 레퍼런스 이미지 수용 정책·씬별 판독
- `w3r_asset_map_v1.md` · `w3r_prop_mapping_v1.md` · `w3r_building_ab_v1.md`
  — 에셋 전수 지도 · 소품 매핑 · 건물 전략 A/B
- `w3_evidence_close_v1.md` — W3 증거 마감
- `props_audit_w1/` — 소품 감사 (C1~C5)
- `realism_gap_2026-07-28/` — **사실성 격차 조사 (6팀 병렬 + 후속)**
  - `ZZ_synthesis.md` — 종합·실행계획 (**원안 — 정정 다수**, 상단 경고 참조)
  - `00_supervisor_direct_diagnosis.md` — 감독 직접 측정 (실측 기준선)
  - `A_prior_work_fidelity_benchmark.md` — 선행연구 충실도 벤치마크 (L1/L2/L3 등급)
  - `B_sim2real_transfer_factors.md` — sim2real 전이 요인
  - `C_current_code_audit.md` — 코드 전수 감사 (미사용 에셋·지름길 학습 조건)
  - `D_isaacsim_untapped_capabilities.md` — Isaac Sim 미활용 역량
  - `E_realism_measurement_protocol.md` — 측정 프로토콜 (도메인 판별기·PAD)
  - `F_pipeline_options_and_recipes.md` — 파이프라인 대안 (스택 유지 결론)
  - `G_env_art_techniques.md` — 환경 아트 기법
  - `H_rtx_capability_verification.md` — RTX 능력 검증 (ZZ 서술 5건 정정)
  - `I_ks_dimension_verification.md` — 국내 규격 원문 검증 (베벨값 근거)
  - `_context_for_agents.md` — 조사팀 공통 컨텍스트

## reports/ (완료 보고·판정 기준·회귀 스냅샷)
- **`realism_v1_final.md`** — **총괄·인수인계 1순위.** 결과 수치 · 구현 · 정정 · 버그 · 결정 대기
- `realism_baseline.md` · `realism_phase1.md` · `realism_phase2.md` — 사실화 v1 라운드 (07-28)
- `realism_rubric_v1.md` — 판정관용 실사성 루브릭 (전 씬 공용)
- 진단: `deadpixel_diag_d3.md` · `deadpixel_diag_0701.md`
- 조달·매핑: `const_color_texture_map.md` · `sky_procurement_v1.md` · `real_reference_expansion.md`
- 감사: `code_audit_realism_v1.md`(치명 4·중대 10) · `license_audit_v1.md` ·
  `doc_consistency_audit_v1.md` · `regression_tool_v1.md` · `stair_compliance_v1.md`
- 완료 보고: `scene01_completion_report.md` · `multi_scene_completion_report.md`
- **파일명 규칙 계열** (개별 색인 생략):
  - `w2*_v1.md` — W2 기반 공사 보고 (ground kit·재질·도구·수술·판정)
  - `w3_*_v1.md` + `_w3_*_crops/` — W3 씬별 개보수 보고·판정 크롭
  - `redteam_*.md` — red-team 검증 보고
  - `regr_*.json` — 라운드별 회귀 스냅샷 (`regression_check.py --json` 출력)
- ※ 룩체크 v1(자연 도랑) 보고서·지시서는 `../../Practice_TerrainGen/Docs/` 로 분리(07-27)

## legacy/ (이력 보존 — 현행 아님)
- `scene_redesign_v5_proposal.md` · `nanobanana_batch1_geometry_map.md` ·
  `scene_library_v3_status.md` · `multi_scene_brief_v3.md` · `realism_rubric_v1.md`

## reference_photos/
- `Generated Image - SceneNN.jpg` 12장 — **씬별 충실도 표준(법)** (NN ∈ 01~04,06~11,13,18)
- 캠퍼스 계단 참고사진 2장 (scene01 근거)

## scripts/
- `imgstats.py` — 공식 측정 도구(하늘/지면 분리·중앙값·실사 n=54 참고 게이트)
- `regression_check.py` — 회귀 검증(478컷 23초, GPU 불요, EXPECTED_FP 지원)
- `geom_invariance_check.py` · `placement_lint.py` — 커밋 전 검증 floor (spec §2.2)
- `make_review_gallery.py` — 검수 갤러리 (**`--out` 필수**) · `stamp_round.py` — 라운드 스탬프
- `make_compare_sheet.py` · `make_hq_sheet.py` — 비교·HQ 시트
- `spike_realism.py` · `rtx_probe.py` — Phase 1 스파이크 랩
- `rounds/` — 완료된 렌더 체인 보관

---
호환 심링크: `Docs/multi_scene_brief_v3.md` → `briefs/`, `Docs/realism_rubric_v1.md` → `reports/`
