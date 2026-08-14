# 씬 라이브러리 v3 — 상태 보고 (21씬, 2026-07-25)

감독 Fable · 구현 Opus(조사 2·에셋 3·라이브러리 2·씬 배치 4) · 근거: `stair_typology_survey.md`(T1~T8)+`_v2.md`(T9~T21), 사양 `multi_scene_brief_v3.md`
**[07-27 갱신] finalize v3 실행 완료(11:29~12:17, RT 2+PT 16 전부 EXIT 0·각 14파일).** PT 판정 결과를 아래 표에 반영. 명시 판정 대상(06/08/13/14/16/17) 외 씬(07/09/11/12/18/20/21)의 PT는 산출됐으나 육안 정밀검수는 미실시. 잔여 = 🔧 씬 코드 수정 후 **부분 재렌더**(06?·08·17·19, +10/15 소수정).

## 씬별 상태 (✅합격 ☑️조건부합격 ⏳PT/확인렌더 대기 🔧소수정 필요)

| 씬 | 유형 | RT 룩 판정 | 잔여 |
|---|---|---|---|
| scene01~05 (v2 세트) | T1/T3/T5/T4/T6 | ✅ PT 파이널까지 완료 | — |
| scene06_spiral_towerstone | T9 나선 석탑 | ☑️ 외부·개구·나선 상부 합격 | 🔧 PT 판정 **불합격**(07-27: basement_up 평균 3.9·spiral_mid 2.7 — 8바운스로도 암흑) → 발광 보강 재렌더 or 두 뷰 제외, **사용자 결정 대기** |
| scene07_wornstone_temple | T16 사원 마모석 | ✅ (이끼 마모석+석축, 태양 0°) | ⏳ PT |
| scene08_stepwell_lattice | T11 스텝웰 | ☑️ V 리듬·수면·테라스 합격 | 🔧 PT 판정(07-27): bank_front 평균 5.9 **불합격**(사광 60°에도 북뱅크 암부) → 코드 주석 대비책대로 카메라 남뱅크 플립 후 재캡처. water_close 66.9·corner_downview 94.8 정상 |
| scene09_ghat_riverfront | T12 가트 | ✅ (수면이 계단 중간 절단) | ⏳ PT |
| scene10_switchback_cliff | T13 갈지자 철제 | ☑️ 정체성 성립(그레이팅·반전) | 🔧 계곡 바닥 단색 초록→흙/암 틴트, 참 부근 난간 정렬 재점검 → ⏳ PT |
| scene11_grating_fireescape | T19 비상계단 | ✅ | ⏳ PT |
| scene12_cliff_plankwalk | T17 절벽 잔도 | ✅ (캔틸레버 목판+체인+무한낙차) | ⏳ PT |
| scene13_helical_parkingramp | T10 나선 램프 | ✅ 램프·연석·도색선 (chord 수정 후) | ☑️ PT 판정 합격(07-27: 지하 명암 대비 성립 — 입구광+램프 실루엣, 평균 21.4/p95 211) |
| scene14_grandstair_illusion | T14 착시 기념계단 | ✅ r3 확인 렌더 합격(07-27: beauty·side_reveal 접지·측면 사면 정상, 부유 없음) | — (PT 완료) |
| scene15_alley_labyrinth | T15 감천 골목 | ✅ 골목 컷 합격 (태양 153°) | 🔧 beauty_overview 카메라만 재선정(부차적) → ⏳ PT |
| scene16_canopy_shadow | T20 캐노피 암부 | ✅ PT 그림자 밴드 정합 확정(07-27: 개구+캐노피 음영이 단일 암밴드로 융합, 낙차 경계 흡수) | — (PT 완료) |
| scene17_ramp_pair_hangang | T21 계단+램프 병설 | ☑️ r3 수면 부유 해소 확인(07-27), 계단·램프 접지 정상 | 🔧 **신규 결함**: 건너편 생울타리+가로수 부유 — far_bank y±20 vs 헤지 y±36(길이24×cy∓24/0/+24) → `far_bank` y ±40 확폭 1줄 수정 후 재캡처 |
| scene18_wavy_artstair | T18 물결 예술계단 | ✅ (5색 물결, nseg24) | ⏳ PT |
| scene19_fan_winder | T7 부채꼴 | 🔧 접근성 v2 반영(07-27: 구버전은 파라펫 12sector 전체+쐐기·포켓 낙차로 보행 진입 불가 → 파라펫 2..9만·게이트 기둥·코너 슬래브·문턱·에지 가드·L벽 플러시, look_refs 시안 참고) — 렌더 미확인 | ⏳ 확인 렌더(RT entry_gate 뷰 포함) + PT 재캡처 |
| scene20_diagonal_oblique | T8 대각 사교 | ✅ (사선 낙차 경계) | ⏳ PT |
| scene21_monumental_selfocclude | T2 다단 기념 | ✅ (자기폐색·난간 하강선) | ⏳ PT |

## 세션에서 확정된 인프라·교훈 (재발 방지)

1. **scene_common v3**: 신규 빌더 7종(helix_steps/helix_ramp/worn_stone/rot_group/open_riser/canopy/width_pairs) + **chord 산정 결함 수정**(호 세그 현길이는 r_mid가 아닌 **r_out 기준×1.03** — r_mid 기준은 외경 쐐기 틈. scene05/06/13/19 파급).
2. **태양 방위 씬별화**: 월드 태양 az ≈ 33.5 + SUN_AZ_OFFSET, 그림자 az−180. 기본 171.5(az205)는 +X향 라이저 음영용(scene01 계열) — 정면 관람형은 0(07/09), 협곡 벽면은 240(-Y 정면광, 10/12), 골목 축광 153(15), 캐노피 그림자 정합 146.5(16), 스텝웰 사광 60(08).
3. **백그라운드 Bash는 cwd가 리셋됨** — 렌더 체인은 반드시 **스크립트 파일**(cd 포함)로 실행. 이 함정으로 렌더 4회 헛돌음.
4. OmniPBR 발광: enable_emission/emissive_color/emissive_intensity (MDL 실측). RT 단일바운스에서 실내 발광 기여 미미 — 실내 판정은 PT로.
5. 에셋 총 56파일 651MB (`download_scene01_assets.py` 재현). AST stage 감사 패턴 전 씬 통과.

## 재부팅 후 절차

```bash
sudo reboot   # 드라이버 재로드
cd ~/Desktop/work_sy/Practice_NegObs && bash scripts/rounds/run_finalize_v3.sh   # 60~75분
```
이후 남는 것: scene10 계곡 바닥·난간(소수정), scene15 beauty 카메라(부차), scene06/08/13 실내 PT 판정 결과에 따른 뷰 정리.
