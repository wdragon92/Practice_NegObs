# Docs 색인 (2026-08-14 재편판)

> **신규 합류는 `STATUS.md` 부터.** 현재 상태·읽는 순서·인수인계 큐가 요약돼 있다.

읽는 순서: `STATUS.md` → `briefs/process_spec_v1.md`(상설 규칙) →
`reports/scene_audit_realism_survey_v1.md`(08-14 전수 감사) → `audit_v4/gt_changes_w3.md`(GT ledger)
→ `reports/critique_intent_map_v1.md`(**수정 전 필독** — 지적 요소의 원설계 의도) → 이 색인

⚠ `surveys/realism_gap_2026-07-28/ZZ_synthesis.md` 는 격차 조사 **원안**이며 서술 다수가
이후 정정됐다. 반드시 `reports/realism_v1_final.md` §3(정정 목록)을 먼저 볼 것.

## 루트
- **`STATUS.md`** — 현재 상태판. 라운드마다 여기부터 갱신한다 (직전 판 스냅샷은 `legacy/`)
- `CREDITS.md` — 외부 에셋 출처·라이선스 (CC-BY 크레딧 포함)

## briefs/ (설계 지시·사양)
- **`process_spec_v1.md`** — **상설 운영 규칙 (08-05 결재 R1~R7).** 검증 floor · ledger 법 ·
  round 규약 · do-not-touch · parked register. 구 `w3_execution_spec_v1.md` 는 전문 이관 후
  RETIRED(참조용 보존 — 코드 9곳이 조문 인용하므로 이동·삭제 금지)
- `gallery_fix_plan_v1.md` — `260805_w3_doctrine` 검수 반영 계획 (08-05 빈티지 — §0 원칙·§0-3
  "scene04 모범" 조항은 계속 인용됨)
- **`building_typology_proposal_v1.md`** — 건물 사실성 재고안(08-11). §3.8 은 08-14 룰링
  (s21=기념관)로 무효, 나머지는 건물 재작업 트랙 입력
- `realism_brief_v1.md` — 사실화 v1 지시서 + 개정 이력 rev.1 (본문과 충돌 시 **rev.1 우선**)
- `multi_scene_brief_v5.md` — 본편 21씬 구현 사양 (v2·v3 는 이력, **v3 §A 회귀 체크리스트는
  여전히 유효** — README·regression_check 가 인용)
- `ground_kit_spec_v1.md` · `t1_material_layer_spec_v1.md` · `lighting_camera_variation_spec_v1.md`
  — W2 기반 공사 사양 (지면 킷 · 재질 레이어 · 조명/카메라 변주)
- `s3_scene07_10_rebuild_spec_v1.md` · `scene05_stage_redesign_v1.md` — 씬 재건 사양
- `scene01_design_brief.md` — scene01 설계·재질·점자블록 (텍스처 소스 슬러그 표)
- `NegObs_인공씬1호_계단_구현지시서.md` — 최초 지시서 + **cue 토글 시스템 원 사양(§7)**
  (편향 있음 — `scene01_design_brief.md` 가 교정본)
- `placement_rules_v1.yaml` — placement_lint 규칙 (spec §2.2 검증 floor 입력 — **이동 금지**,
  `placement_lint.py` 가 실행 경로로 읽음)
- ※ `process_revision_proposal_v1.md`(SUPERSEDED 스텁) → `../archive/briefs/`

## audit_v4/ (감사·현실성 규약·판정·픽스로그·ledger)
- **`gt_changes_w3.md`** — **GT ledger (append-only · 선신고).** 상태 어휘·re-cache 규칙은
  §0~§2 원본. **이 문서가 인용하는 48경로(regr json·보고서·크롭·사양)는 재현성 증거 — 이동 금지**
- `user_feedback_v5_1.md` — **현실성 규약**: 전역 §1~5(나무 v2·볼라드 규정·배치 비정형·틴트
  지터·지형 곡률) + v5.2 원칙 §6~9(조경 개방감·점자블록 기본 OFF·임의 팻말 금지)
- `judge_v6_rt_*.md` · `judge_v7_rt_*.md` · `judge_v8_rt.md` — 현역 판정문 (v6_new7 = scene10/12
  지배 판정, v7A·v7B·v8 = GRAZE 임계값 근거 사슬; 각 파일 말미에 **감독 결정** 부록)
- `fixlog_*.md` — 구현 픽스로그. 현역 잔류 = 활성 큐 씬 접촉분(N1·VB·W3·W6·X2·X3 등) +
  코드 인용분(W4·W7). **인용 0 + 큐 무접촉 4건(N3·W0·W2·Y1)은 08-14 `../archive/audit_v4/` 로**
- `library21_final_hq.png` — 본편 21씬 컨택트 시트 (생성기 `scripts/make_hq_sheet.py`)
- ※ v4 전수 감사 4건·통합 수정 계획·judge v5 6건·이전 세대 시트 PNG → `../archive/audit_v4/`

## surveys/ (조사)
- **`cue_arrangement_survey.md`** — **맥락 단서 배치 조사.** 낙차 유형×동반 요소 매트릭스 ·
  단서-낙차 조건부 확률 · 33씬 대조
- **`cue_expansion_survey_v1.md`** — 낙차 간접 단서 지도 + 탈상관 재고 (**계획 전용 — 사용자
  결재 대기**)
- `korean_pedestrian_geometry.md` · `korean_urban_backdrop.md` — 국내 보행 기하·도시 배경 조사
- `building_asset_survey_v1.md` — 건물 에셋 적용 경로 조사(계획)
- `era_consistency_survey_v1.md` — 연대 정합 조사 (개보수 어휘 12칸)
- `stair_typology_survey_v2.md` (T9~T21) — 계단 유형 조사 (§3 수학 정의 = scene_common 출처;
  v1(T1~T8)은 `../archive/surveys/`)
- `batch1_geophysics_realism_survey.md` — 배치1 물리 근거
- `scene_composition_audit.md` · `_dimension_index.md`(**코드 12곳 인용 — 이동 금지**) ·
  `s3_research_numbers_v1.md`
- `w3_intake_policy.md` · `w3_intake_01_05.md` · `w3_intake_06_10.md` · `w3_intake_v2_images.md`
- `w3r_asset_map_v1.md` · `w3r_prop_mapping_v1.md` · `w3r_building_ab_v1.md`
- `w3_evidence_close_v1.md` — W3 증거 마감
- `props_audit_w1/` — 소품 감사 (C1~C5 + 지면 프로파일 D·중경 E — C4 는 s21 재작업 종료 후
  아카이브 재판정)
- `realism_gap_2026-07-28/` — **사실성 격차 조사 (6팀 병렬 + 후속)**: `ZZ_synthesis.md`(원안 —
  정정 다수) · `00_supervisor_direct_diagnosis.md` · `A_`선행연구 · `B_`sim2real ·
  `C_`코드감사 · `D_`Isaac 역량 · `E_`측정 프로토콜 · `F_`파이프라인 · `G_`환경아트 ·
  `H_`RTX 검증(ZZ 정정 5건) · `I_`국내 규격(베벨 근거) · `_context_for_agents.md`

## reports/ (완료 보고·판정 기준·회귀 스냅샷)
- **`scene_audit_realism_survey_v1.md`** — **08-14 전수 감사 + 실세계 조사 종합.** 시스템 결함
  7건(배선·봉인) · 씬별 지적 · 조사 3편 요지 · 로드맵 R0~R6 제안. 원자료
  `scene_audit_findings_v1.json`(286건 + 판정)
- **`realism_v1_final.md`** — 사실화 v1 총괄·인수인계 (결과 수치 · 구현 · 정정 · 버그 · 결정 대기)
- **`critique_intent_map_v1.md`** — 비판-의도 지도(지적 17건의 원설계 의도 — **수정 전 필독**)
- `repo_reorg_v1.md` — 08-14 문서·디렉터리 재편 기록(상호참조 인벤토리 요지 포함)
- `s04_quality_gap_survey_v1.md` — s04 품질 격차 F1~F8 정량(08-11 — 레버1 설계 입력)
- `s03_xalign_survey_v1.md` — s03 x축 정렬 3안 실측(08-11 — 사용자 판정 대기)
- `continuity_audit_v1.md` — 전 씬 통행 연속성 감사(08-06)
- `tonglam_v2.md` — 전프레임 통람 판정(row 08·10 supersede note 추기 예정)
- `realism_baseline.md` · `realism_phase1.md` · `realism_phase2.md` — 사실화 v1 라운드
- `realism_rubric_v1.md` — 판정관용 실사성 루브릭 (전 씬 공용)
- 조달·감사: `sky_procurement_v1.md` · `real_reference_expansion.md`(실사 n=54 게이트 근거) ·
  `asset_audit_v1.md` · `lighting_spikes_v1.md` · `scene15_railing_fix_v1.md` ·
  `fix_building_kit_v1.md`(GT-12 OPEN) · `cleanup_lookcheck_v1.md`
- 감사·기준: `regression_tool_v1.md` · `stair_compliance_v1.md` · `graze_recalibration_v1.md`
- 완료 보고: `scene01_completion_report.md`
- 데이터 파일: `geom_baseline_w2.json`(geom_invariance_check 기준선) ·
  `gt6_judge_baseline_manifest.json`(scene05 인용) · `regr_*.json`(라운드별 회귀 스냅샷 —
  **원장 landing 이 인용하므로 이동 금지**)
- **파일명 규칙 계열** (개별 색인 생략): `w2*.md`(현역 8건 — 종결 10건은 archive) ·
  `w3_*_v1.md` + `_w3_*_crops/`(씬별 개보수 보고·판정 크롭) · `redteam_s0710_rebuild.md`
- ⚠ 알려진 고아: `_w3_l14_crops/`·`regr_260731_w3_l14.json` 은 대응 보고서(`w3_l14_v1.md`)가
  **미작성**(scene14 코드가 3곳 인용하나 git 이력에도 없음 — L14 레인 보고서 공백)
- ※ 일회성 진단·감사·종결 w2/w3 일부 → `../archive/reports/` (`archive/README.md` 참조)
- ※ 룩체크 v1(자연 도랑) 보고서·지시서는 `../../Practice_TerrainGen/Docs/` 로 분리(07-27)

## archive/ (종결 기록 보관)
- 규칙: 원경로 `Docs/<하위>/<파일>` → `archive/<하위>/<파일>` (파일명 불변).
  1차 56건(08-05) + **2차 9건(08-14, 인용 0 실측분만 — 큐 접촉분 유보)**. 목록·근거는
  **`archive/README.md`**

## legacy/ (이력 보존 — 현행 아님)
- `scene_redesign_v5_proposal.md` · `nanobanana_batch1_geometry_map.md` ·
  `scene_library_v3_status.md` · `STATUS_pre_p4.md` · `STATUS_pre_reorg_260814.md`
- 심링크: `multi_scene_brief_v3.md` · `realism_rubric_v1.md`

## reference_photos/
- `Generated Image - SceneNN.jpg` 12장 — **씬별 충실도 표준(법)** (NN ∈ 01~04,06~11,13,18)
- 캠퍼스 계단 참고사진 1장(`1784886529634.jpg`)
- `w3/<패널>/` — 패널별 LICENSES.csv·SOURCES.md(이미지는 미추적) · `expanded/` — Wikimedia
  표본(LICENSES.csv 만 추적)

## scripts/
- `imgstats.py` — 공식 측정 도구(하늘/지면 분리·중앙값·실사 n=54 참고 게이트)
- `regression_check.py` — 회귀 검증(GPU 불요, EXPECTED_FP 지원)
- `geom_invariance_check.py` · `placement_lint.py` — 커밋 전 검증 floor (spec §2.2)
- `make_review_gallery.py`(**`--out` 필수**) · `stamp_round.py` — 검수 갤러리·라운드 스탬프
- `make_compare_sheet.py` · `make_hq_sheet.py` · `make_allview_sheet.py` · `make_overview.py`
- `quality_metrics_probe.py`(GT-108 검측) · `glass_boundary_check_s13.py` ·
  `s03_xalign_probe.py` · **`probe_views_capture.py`**(표적 시점 캡처 — 씬 무수정 뷰 주입) ·
  `near_ground_stats.py` · `const_color_audit.py` · `measure_sky.py` · `skyline.py` ·
  `norm_spec.py` · `valset.py` · `harvest_refs.py` · `spike_realism.py` · `rtx_probe.py`
- `check_data_run.py` · `run_data_render.py` — 데이터 렌더 검증·생성
- `rounds/` — 완료된 렌더 체인 보관(08-14: 구식 명명 17건 + reorg 1건 합류, v6=v7 중복 1건 제거)
- 루트 `run_p2_all33.sh` — **상설 드라이버(이동 금지** — 문서가 `:36` 줄 번호 인용)

---
호환 심링크(Docs/ 최상위 — 코드의 구경로 인용 보호용, 08-14 실제 생성):
`multi_scene_brief_v3.md` `multi_scene_brief_v2.md` `scene01_design_brief.md`
`nanobanana_batch1_geometry_map.md` `scene_redesign_v5_proposal.md` `stair_typology_survey_v2.md`
`realism_rubric_v1.md` → 각 실경로 / `surveys/real_reference_expansion.md` → `reports/`
