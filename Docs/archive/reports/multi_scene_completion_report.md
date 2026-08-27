# NegObs 인공씬 세트 v2 — 완료 보고 (계단 유형 다양화)

작성 2026-07-24 · 감독 Claude Fable 5(유형 선정·적대 리뷰·룩 판정) · 구현 Claude Opus 에이전트 (조사 1 + 에셋 2 + 공통 라이브러리 1 + 씬 4)
사양: `Docs/briefs/multi_scene_brief_v2.md` · 유형 근거: `Docs/stair_typology_survey.md` (T1~T8 매트릭스, WebSearch 기반)

## 1. 무엇이 만들어졌나 — 씬 5종 세트 (scene01 포함)

| 씬 | 유형 | 정체성 축 (서베이 §2 다양성 축 커버) |
|---|---|---|
| scene01_campus_stairs | T1 광장 광폭 저단차 | 동일 재질 은닉 + 설비 단서 풀셋(난간·점자·재질경계 토글) |
| **scene02_underpass** | T3 지하도/지하철 입구 | 설비 최강(점자·난간·논슬립·옹벽) × **하부 무조명 암부 소실** × 낙차 3.2 m |
| **scene03_riverbank** | T5 하천 제방 접근 계단 | **무난간**(정체성) × 물면 앵커(최저부 증거) × 건너편 재출현 × 20단 장주계단 |
| **scene04_parktrail** | T4 공원 침목 계단 | **불규칙 단 테이블**(riser 0.14~0.19/tread 0.5~0.8) × 재질 융합(침목+마사토+낙엽) × 수관 앵커 |
| **scene05_amphitheater** | T6 sunken plaza 좌석단 | **대단차 0.4 × 원형 곡률(세그 32) × 설비 전무** — 무대 관람석형 |

전 씬 공통: SCENE_CONFIG 토글(hazard/railing/tactile/material_break/sign예약/dressing + **cue_nosing 신규**), `NEGOBS_SCENE_CONFIG`/`NEGOBS_PARAMS_OVERRIDE` env 오버라이드, 카메라 밴드 h 0.3~2.0·피치 −15~+5 [고정], grid 프리셋 9장 + 씬별 미장센 4컷, RT/PT 캡처 파이프라인, cue 토글의 위험 기하 불변 [고정].

## 2. 실행

```bash
conda activate env_isaaclab && cd ~/Desktop/work_sy/Practice_NegObs
python scene02_underpass.py        # GUI (P/C/[/] 키). scene03/04/05 동일
NEGOBS_CAPTURE=1 NEGOBS_CAPTURE_MODE=pt python scene02_underpass.py   # 헤드리스 캡처
```

- 공통 라이브러리: `scene_common.py` (boot/재질/기하/조명/캡처 — scene01 검증 코드의 함수화. 씬 파일은 레이아웃+PARAMS만)
- 텍스처: `assets/scene01/` 38파일(464 MB, ambientCG+PolyHaven CC0, `download_scene01_assets.py` 재현 가능)

## 3. 검증 요약 (감독 적대 루프 — 발견·수정된 결함)

- **코드 리뷰·런타임 단계**: scene02 `stage` 인자 누락 즉사(AST 감사 도구로 전 호출 검증 후 재발 차단) / scene03 브리프 수치 모순(16단×0.16≠사면 3.2 → 20단 정합) / scene04 USD 프림명에 음수 좌표(`BgTree_-32`) 불허 문자 / scene05 브리프의 외접 사각·진입계단 x0 오류를 에이전트가 역지적(내접 사각·림 기준으로 정정)
- **룩 루프(RT 전수 육안, 씬당 2~4라운드)**: scene02·05 공통 치명 — **주변 지면 평면이 위험 공동(피트/보울)을 덮는 버그** → 개구 4박스 분할로 해결 / scene03 둑마루·scene04 상부가 "흙 사막" → 잔디 기반+길 밴드로 주객 반전 / 수면 y폭 부족(화면 가장자리 하늘 구멍) / 볼라드 PVC 느낌 등
- **나무 색 사가 (기록 가치)**: 수관 알베도 (0.09,0.15,0.06)이 정오광에서 연두 파스텔로 렌더 → 재질 바인딩 버그로 오인 → USD 덤프·최소 프로브·픽셀 실측으로 추적한 결과 **렌더러는 물리적으로 정직했음** (sRGB 감마: 알베도 0.15 × 노출 1.44 → 표시값 127 정확 일치). 해결은 알베도를 실제 수풀 수준 (0.025~0.06)으로 — 잎의 자기그림자를 알베도로 근사. 전 씬 통일 적용(scene01 포함).
- **grazing 은닉 재현**: 4씬 전부 h0.3 프리셋에서 낙차 기하 완전 소실 확인 — scene02는 난간·점자만 뜬 평지, scene03은 수면·수관만, scene05는 보울 통째 소실.

## 4. 캡처 경로

씬별 `look_check/sceneNN/` 아래: `final_pt/`(PT 512spp 파이널) + `r1..r4/`(룩 루프 기록). scene01 `final_pt/`는 나무 색 통일 후 3컷(lower_lookback·beauty_overview·amphi_view) 갱신본 포함.

## 5. 알려진 한계 (전 씬 공통 + 씬별)

1. 나무 = 스피어 클러스터 양식화(색은 개선, 근접 형상 한계) / 생울타리·잔디 패치의 직선 경계
2. scene03 수면: 정적 평면+하늘 반사(잔물결·유속 없음), 트림-계단 사이 립 (r1 보고 잔존)
3. scene04 hazard_stairs=False 대조군에서 배경 소품 z 불일치(부유) — 대조 렌더는 dressing OFF 조합 권장
4. scene05 진입 계단이 rim_view 각도에서 램프처럼 읽힘(라이저 면이 카메라 반대 — 코드상 6단 정상, side 컷에서 확인 가능)
5. GUI 자유 비행 육안 검증(§9) 미실시 — 사용자 몫
6. T2(다단 기념계단)·T7/T8(부채꼴·대각)은 미구현 — 서베이 §3 후보로 문서화, scene_common의 build_arc_steps로 T7 구현 용이

## 6. 다음 단계 제안 (착수 금지 — 검수 후)

T2/T7/T8 씬 추가 / 씬별 도메인 랜덤화 파라미터화(현재 구조만) / GT 낙차 맵 모듈 / hard-negative 씬(내리막 완경사·재질 경계만 있는 평지 — 서베이 §6) / 나무 임포스터 개선.
