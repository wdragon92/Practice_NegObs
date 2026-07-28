# Scene01 캠퍼스 광장 하행계단 — 완료 보고 (지시서 §13 형식)

작성 2026-07-24 · 감독 Claude Fable 5(적대 검증·룩 판정) · 구현 Claude Opus 에이전트 ×2
사양: `Docs/scene01_design_brief.md` (지시서 편향 교정본) · 원 지시서: `Docs/NegObs_인공씬1호_계단_구현지시서.md`

---

## 1. 실행 명령 + 확인된 동작

```bash
unset PYTHONPATH VIRTUAL_ENV
conda activate env_isaaclab
export PYTHONNOUSERSITE=1
cd ~/Desktop/work_sy/Practice_NegObs
python scene01_campus_stairs.py          # GUI 룩 체크 (키: P=PT토글, C=캡처, [ ]=태양방위)
```

- 헤드리스 자동 캡처(개발 파이프라인): `NEGOBS_CAPTURE=1`, 옵션 `NEGOBS_CAPTURE_MODE=rt|pt|both`, `NEGOBS_CAPTURE_DIR`, `NEGOBS_VIEWS`, `NEGOBS_PARAMS_OVERRIDE`(JSON), `NEGOBS_SCENE_CONFIG`(JSON — cue 토글 오버라이드).
- 확인된 동작: 헤드리스 캡처 RT 13컷 26초, PT 512spp 13컷 약 3분(RTX 4090). GUI 모드는 코드 경로 동일(뷰포트 유지 + 키 핸들러) — **사용자 육안 검증 대기**.

## 2. 지시서 대비 주요 변경 (사진 기반 편향 교정)

| 항목 | 지시서 v1 | 구현 | 사유 |
|---|---|---|---|
| 씬 구도 | 보도 3m + 6단 + 아스팔트 하부 | **화강암 광장(16m 폭) + 광폭 4단(riser 0.15/tread 0.38, 낙차 0.6m) + 동계열 화강암 하부 광장** | 참고 사진 2장. 위험 본질 = "동일 재질이라 단차 소실" |
| 재질 | 절차적 격자 무늬 | PBR 텍스처: Tiles038(밝은 판재)·granite_tile(다크 화강암 밴드/경계석)·PavingStones111(하부)·brick_wall_001(벽돌) — 전부 CC0 | 룩체크 v1과 동일한 확립된 관행 (외부 대용량 메시는 여전히 금지) |
| 드레싱 | 화단 띠+벽 힌트 | 화단 3개소(경계석+캡+잔디+나무+지지대 3본), 앰피시어터 3단, 벽돌 건물 4동(창문 그리드·파라펫), 가로등, 잔디 대지 | "계단만 덩그러니 금지" 강화 |
| 낙차 | 0.96 m (6×0.16) | 0.6 m (4×0.15) | 사진의 저단차 광장 계단. [고정] 최소 0.3m 충족 |
| 점자블록 | 두께 "살짝 돌출" | 4mm 돌출 + 돌기는 절차 생성 노멀맵(1024², 6×6 반구) | 3cm 돌출은 비현실(라운드1 수정) |

고정 준수: 카메라 밴드 0.3~2.0m·피치 −15~+5° ✓ / cue 토글 기하 불변 ✓ / isaacsim.* 네임스페이스 ✓ / v9 렌더 설정 블록 ✓ / Replicator·랜덤화 미착수 ✓.

## 3. 검증 요약 (감독 적대 루프)

- **코드 리뷰**: 결함 8건 발견·수정 — 앰피 공중부양(F1), 창문 전면 Z-파이팅(F2), 주변 지면 부재(F3), 점자블록/밴드 과다 돌출(F4/5), 난간 포스트 부유(F6), 평지 대조군 Z-파이팅(F7), 토글 env 오버라이드 부재(F8). `world_or_object=True`(월드 투영)는 MDL 원문으로 사전 확정.
- **룩 루프 3라운드** (RT 13컷 전수 육안 판정 → 수정): 중앙 난간의 프리셋 가림(y=0→−2.75), 나무 만화풍(올리브 2톤 6스피어), 잔디 체커보드(스케일 4m+틴트), 원경 차단 건물 C/D 신설, 중간 레일 추가, 태양 방위 171.5° 오프셋(정면광+라이저 음영), 밴드 재질 교체(PavingStones127→granite_tile: 나무 데크로 오독됨).
- **성공 기준 판정** (브리프 §8): ① 캠퍼스 광장 인상 ✓ ② grazing 은닉 — h0.3·d5/d10에서 계단 완전 소실, 하부 시점에선 명확 ✓ ③ 토글 무결성 — cue 전부 OFF 렌더에서 위험 기하 동일(대응쌍 확인, 코드 구조상 cue 함수는 신규 프림 Define만) ✓ ④ Z-파이팅·늘어남 없음(수정 후) ✓ ⑤ 단일 명령 실행 ✓.

## 4. 참고 사진 대비 차이 / 판단

- 사진의 곡선(호) 계단·앰피 대신 직선 계단 — v1 범위(박스 프림). 곡선은 후속 후보.
- 사진의 줄무늬 밴드는 재질만 다르고 플러시 — 구현은 1.5mm 미세 돌출(Z-파이팅 회피 타협).
- 나무는 스피어 조합의 양식화 표현 — 원거리(≥8m)에서만 무난. 근접 실사성은 미달(알려진 한계).
- 사진 속 군중·자전거·표지판 등 소품 없음 — cue_sign은 config 키만 예약(미구현).

## 5. 알려진 한계

1. 나무 수관이 근접에서 스피어 티가 남 (v2 후보: 카드 크로스 임포스터 또는 저폴리 에셋).
2. brick_wall_001의 백색 페인트 잔흔이 근접 파사드에서 낡은 인상 (원거리에선 무난).
3. 창문이 유리 패널 1장 표현(프레임·인방 없음).
4. grazing 각(h0.3)에서 하부 광장 원경이 얇은 띠로 뭉개짐 — DLSS 한계, PT에서는 완화.
5. GUI 육안 검증(§9 자유 비행) 미실시 — 사용자 확인 대기.

## 6. 캡처 경로 + 대표 이미지

`look_check/scene01/` 아래 (전부 1920×1080):
- **`final_pt/`** — 최종 PT 512spp 13컷 + manifest.json: 프리셋 9(h{0.3,0.9,1.8}×d{2,5,10}, y=−2.75, 피치 −10°) + beauty_overview / lower_lookback / edge_closeup / amphi_view
- **`pair_cues_off/`** — cue 전부 OFF 대응쌍(RT): preset_h0.9_d5 · preset_h0.3_d5 · lower_lookback → **위험 판별 대응쌍 구조 실증**
- `auto/`(r1) · `r2/` · `r3/` — 룩 루프 라운드별 기록
- 대표컷: `final_pt/pt_noon_lower_lookback.png`(계단 정면), `pt_noon_amphi_view.png`(좌석단+측벽), `pt_noon_preset_h0.3_d5.png`(grazing 은닉), `pt_noon_edge_closeup.png`(점자블록 돌기)

## 7. 산출물 파일

- `scene01_campus_stairs.py` — 단일 실행 파일 (SCENE_CONFIG 토글 6종 + PARAMS 전치수 + 캡처 파이프라인)
- `assets/scene01/` — 텍스처 17파일(186MB, `download_scene01_assets.py`로 재현 가능) — 주의: band_dark_*(PavingStones127)는 룩 판정에서 교체되어 현재 미사용(보관)
- `Docs/scene01_design_brief.md` — 설계 사양(편향 교정 기록 포함)

## 8. 다음 단계 제안 (착수 금지 — 승용 검수 후)

곡선 계단 변형 / cue_sign 구현 / 나무 개선 / dawn 라이팅 프리셋 이식 / GT 모듈(레이캐스트 낙차 맵) — 전부 다음 모듈.
