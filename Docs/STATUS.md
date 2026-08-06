# STATUS — 08-06 GT-64~71 착지 · 갤러리 재검수 대기 (2026-08-06)

직전 판(W3 마감 + 08-05 독트린)은 git 이력 참조. 이 판 = fix-plan §2 큐 실행 + S13 6차.

## 한 줄
**gallery_fix_plan §2 큐 전부 실행 완료.** S13 6차(GT-64: 정남향 판상 4동 그리드·남북
교차로·계단박스 개폐) + 백로그 6씬(GT-65~70) + 헤지 밀도 파일럿(GT-71) 착지 —
**갤러리 2건 사용자 검수 대기**. 구현은 Opus 5 에이전트 위임(08-06 사용자 지시, §2.6).

## 읽는 순서 (신규 합류)
1. 이 파일 → 2. `briefs/process_spec_v1.md`(상설 운영 규칙) → 3. `audit_v4/gt_changes_w3.md`
행 20~27(GT-64~71 착지기록) → 4. `briefs/gallery_fix_plan_v1.md`(§2 큐 — 본 라운드로 소화)

## 현재 상태
- **검수 대기 2건**: `look_check/_review/260806_w3_s13fix6/`(scene13 15컷 — GT-64) ·
  `look_check/_review/260806_w3_fixqueue/`(scene01·05·06·10·12·14·16 97컷 — GT-65~71)
- GT-62(s13fix5)는 08-06 검수(수정 요청)로 **GT-64 사이클에 이관** · GT-63(hedgeswap)은
  방향 승인 + 밀도 지적 → **GT-71 파일럿**(scene16 11→9주, pitch 0.62) — 확산은 검수 후
- scene13 6차 요지: A101 남향 반전 · A102/A103 E-W 판상 전환 · **A104 신설**(2×2 그리드,
  전동 정남향) · 진입로 서단 T자 남북 교차로 + 보도/횡단 정렬 · 수목 21주 도로망 추종
  (간섭 7역 드롭) · 계단박스 = 중앙벽 철거→자립 양면 가드 + 동측 강화유리문 + 고정유리
  폐합 + 코핑. watch: stair_head DARK(42.8) — 검수에서 어두우면 lamp 상향 행
- **신규 문서 2건**: `surveys/building_asset_survey_v1.md`(건물 사실성 — 08-06 "건물이
  가장 부자연스럽다" 대응, **계획 전용·결재 대기**) · `reports/continuity_audit_v1.md`
  (33씬 통행 연속성 감사 — 소견 33건, 차기 웨이브 후보)
- 검증: floor 4종 + building_kit green · HEAD 대조 기하 해시 미변경 25씬 비트동일 ·
  회귀 s13fix6 FAIL3/WARN1(전부 귀속) · fixqueue FAIL10/WARN30(전부 귀속, 원장 행별 기재)

## 다음
1. **사용자 검수**: 위 갤러리 2건 (spec §6 체크리스트) → 통과 시 GT-62~71 CLOSED,
   GT-57(갤러리 재작업) CLOSED + R4 큐 폐기 확정
2. GT-71 A/B 판정 → 헤지 밀도 확산 여부(씬별 span 재계산 필수 — 원장 행 27 주의)
3. `building_asset_survey_v1.md` 결재 → 건물 사실성 파일럿(1씬)
4. `continuity_audit_v1.md` 소견 33건 → 차기 정비 웨이브 범위 결정
5. W4 GT 재판정(scene06 로봇높이 개구 폐합 이월분 포함) → W5 hazard-off + 20k 생산 렌더

## 규율
`process_spec_v1.md` §2가 정본. 요지: 커밋 전 floor 4종 green / 같은 prim A/B / GT 선신고 /
GPU·ledger flock(-o) 배타 / round 명명 상태 주장 금지 / gallery `--out` 필수.
