# NegObs 인공씬 세트 v2 — 계단 유형 다양화 브리프 (구현용)

작성 2026-07-24 · 감독 Claude Fable 5 · 구현 Claude Opus 에이전트
근거: `Docs/stair_typology_survey.md` (유형 매트릭스 T1~T8) · 기존: scene01(T1) 완료
목적: "정형화된 계단 1종" 편향 제거 — 단서 조합 공간(설비 유무 × 재질 대비 × 단높이 × 기하 정렬 × 자연물 × 조명)을 씬 세트로 격자 표본. **핵심은 해당 유형의 학습이 가능하도록 유형별 시각 단서가 정직하게 재현되는 것.**

이번 구현: **scene02(T3 지하도) · scene03(T5 제방) · scene04(T4 공원) · scene05(T6 앰피시어터)**. T2(기념계단)·T7/8(곡선/대각)은 후속.

공통 관례는 scene01과 동일(Z-up·m·진행축 +X·낙차 시작 모서리 x=0, Isaac Sim 4.5 `isaacsim.*`, 실행 시퀀스, 카메라 밴드 h 0.3~2.0 / 피치 −15~+5 [고정], cue 토글은 위험 기하 불변 [고정], Replicator·랜덤화 금지).

---

## A. scene_common.py — 공통 라이브러리 (신규)

scene01_campus_stairs.py의 **검증된 블록을 함수화**해 추출한다. scene01 파일 자체는 수정 금지(완료 산출물). 모듈은 SimulationApp 부팅 전 임포트 안전해야 함(임포트 시 pxr 접근 금지 — 함수 내부에서 import).

```
boot(headless) -> sim_app                     # SimulationApp + carb settings + 스테이지 단위 (scene01 그대로)
make_pbr(stage, path, ...) -> Material        # OmniPBR 월드투영 팩토리 (scene01 그대로 + specular_level 인자 추가)
ensure_noon_lookfix(src)                      # scene01 그대로
setup_lighting(stage, light_params, sun_az_offset) -> apply_dome_rot   # scene01 그대로
add_box / add_cylinder / add_sphere           # scene01 그대로 (stage 인자화)
build_straight_stairs(stage, prefix, x0, y0, y1, riser, tread, n, base_z, mtl, riser_list=None)
                                              # riser_list로 불규칙 단 지원(scene04)
build_arc_steps(stage, prefix, cx, cy, r_in, r_out, a0, a1, seg, top_z, base_z, mtl)
                                              # 호를 seg개 사다리꼴 박스(rotZ)로 근사 — 티어 1개분
build_nosing(stage, prefix, ...)              # 단코 논슬립 띠: 폭 0.05, 1mm 돌출, 각 단 전연부 (색 인자)
build_railing_line(...)                       # scene01 레일(상단+중간+포스트, 단면 착지) 일반화: y 임의, 시작/끝 x·z
build_tactile(...) / build_planter(...) / build_tree(...) / build_building(...)   # scene01 이식
build_hedge(stage, prefix, x0,y0,x1,y1,h)     # 생울타리: 박스, grass 텍스처 진녹 틴트(0.35,0.45,0.28), scale 1.2
build_bench(...)                              # 좌판+다리(weathered_planks), 등받이 없음 1.8×0.4×h0.45
build_bollard(...)                            # r0.06 h0.75 스테인리스
build_water(stage, path, x0,y0,x1,y1,z)       # 수면: 상수색 (0.05,0.10,0.11), roughness 0.03, metallic 0
build_slope(stage, path, ...)                 # 회전 박스 사면(rotateY), 잔디/흙 재질
capture_pipeline(sim_app, stage, views, lookcheck_dir, apply_dome_rot)   # scene01 헤드리스 캡처 블록 일반화
grid_views(gy, ...) -> dict                   # h{0.3,0.9,1.8}×d{2,5,10} 프리셋 생성기 (+미장센은 씬별 추가)
```

TEX 레지스트리는 common에 통합(기존 scene01 세트 + 신규 §B), `check_assets(roles)`로 씬별 필요분만 검사.

## B. 신규 텍스처 (감독 썸네일 선별 완료 — `assets/scene01/download_scene01_assets.py`에 추가·실행)

| 역할 | 소스 (PolyHaven 4k jpg) | canonical |
|---|---|---|
| 지하도 옹벽·터널 | concrete_wall_008 | `concrete_wall_{diff,nor_dx,rough}.jpg` |
| 지하도 계단·바닥 | brushed_concrete_03 | `concrete_floor_{...}` |
| 침목(목재) | weathered_planks | `wood_dark_{...}` |
| 공원 흙길 | park_dirt | `dirt_park_{...}` |
| 마사토·자갈 | gravel_floor | `gravel_{...}` |
| 자연석 판석 | stone_tiles_02 | `stone_flag_{...}` |
| 석축/사석 | rock_wall_08 | `rock_wall_{...}` |

기존 재사용: plaza_light(화강암)·plaza_lower(판석 보도)·granite_dark·brick_red·grass·tactile·HDRI.

## C. 씬 사양 4종

모든 씬: SCENE_CONFIG 키는 scene01과 동일 6종(유형상 무의미한 단서는 기본 False — 단 코드 경로는 존재), `NEGOBS_*` 환경변수 파이프라인 동일, 캡처 프리셋 = grid_views + 미장센 3~4컷, 콜라이더는 보행면 전부.

### scene02_underpass.py — T3 지하도/지하철 입구 (설비 완비 × 하부 암부)

- 지상: 보도 평면 z=0 (plaza_lower 보도블록, x −18..+16, y −8..8), 주변 잔디 대지 −0.03, 우측 벽돌 건물 1동(y 9..13, h 10), 생울타리 띠(보도 y=−6 경계), 가로등.
- **하강 피트**: x 0→7.0, 폭 y −1.75..+1.75 (유효 3.5m). 계단 20단 × riser 0.16 · tread 0.32 (총 낙차 3.2m, run 6.4m) + 하부 랜딩 x 6.4..7.0(z=−3.2). 재질 brushed_concrete(계단·랜딩).
- 피트 옹벽: 양측+후면 concrete_wall_008, 두께 0.3, 지상 위 파라펫 0.15 돌출(경계 立上り), 피트 안쪽 면이 보이는 구조.
- **터널 포탈**: 랜딩 후면(x=7.0)에 3.5×2.3 개구 — 깊이 4m 박스 내부(어두운 콘크리트, dome 차폐로 자연 암부). 개구 상단 인방보.
- 단서(토글): cue_tactile(상단 x=−0.3 띠 + 하부 랜딩), cue_railing(계단 양측 벽부착 레일 + 피트 지상 둘레 3면 난간 — 낙하 방지), **cue_nosing 신규 키**(전 단 황색 논슬립 띠 — 지하철 관행), cue_material_break(보도↔콘크리트 대비; OFF면 계단도 보도블록재), cue_scene_dressing(건물·울타리·가로등), cue_sign 예약.
- 미장센: approach(보도에서 피트로), pit_edge(모서리 위에서 아래로 −15°), inside_looking_up(랜딩에서 지상 역광), grazing 시리즈는 grid_views(gy=0 — 이 씬은 중앙 난간 없음).
- 판정 포인트: h0.3 원거리에서 피트가 **완전한 평지로 보이고** 난간·점자블록만 떠 있는 그림. PT에서 피트 내부 깊이감(암부 그라디언트).

### scene03_riverbank.py — T5 하천 제방 (무난간 × 물면 앵커)

- 지형: 둑마루 평탄로 z=0 (x −20..0, y −10..10, gravel 또는 dirt_park — 둑길), **사면**: x 0..6.4에서 z 0→−3.2 (1:2 경사, grass), 하부 둔치 z=−3.2 (x 6.4..20, grass+dirt 혼합 띠), **수면** z=−3.35 (x 14..40, y 전폭, build_water) + 대안(건너편) 낮은 둔치 띠 z=−3.2(x 40..46, grass) — "건너편 재출현" 단서.
- **계단**: 콘크리트 직선 16단 × riser 0.16 · tread 0.35, 폭 1.5m (y −0.75..0.75), 사면을 절개해 하강(양측에 사면 잔디가 계단 측벽면까지 옴 — 측면 소단 0.2m 콘크리트 테두리). **난간 없음이 이 유형의 정체성** (cue_railing 기본 False, True면 한쪽 파이프 레일 1선).
- 소품: 둑마루에 볼라드 2개(차량 진입 방지)·벤치 1, 사면에 관목(hedge 소형 블록) 3~4개 산개, 둔치에 나무 2그루(수관이 둑마루 눈높이 아래 — 계열③ 앵커!), 수면 인접부 사석 띠(rock_wall 텍스처 낮은 박스).
- 조명: SUN_AZ_OFFSET 동일 기본. 수면은 PT에서 하늘 반사 확인.
- 미장센: levee_walk(둑마루에서 진행방향 — 계단이 사면에 접혀 소실+물면만 보임), stair_down(계단 위에서), beach_lookup(둔치에서 역방향), across_river(수면 너머 조망).
- 판정 포인트: h0.3~0.9 둑길 시점에서 계단·사면 완전 소실, **수면(최저부 증거)과 건너편 둔치, 눈높이 아래 수관**이 낙차를 시사하는 그림.

### scene04_parktrail.py — T4 공원 침목 계단 (불규칙 × 자연물)

- 지형: 완경사 공원 사면 — 상부 평탄(z=0, x −15..0) / 사면 x 0..5.5, z 0→−1.5 / 하부 평탄(z=−1.5, x 5.5..20). 지표 dirt_park, 좌우로 잔디(grass) 패치 — 경계는 겹침 박스 오프셋로 단순 처리.
- **침목 계단**: 9단, riser 고정 테이블 [0.16,0.14,0.18,0.15,0.19,0.14,0.17,0.15,0.17]·tread 테이블 [0.55,0.7,0.5,0.8,0.6,0.55,0.75,0.5,0.6] (합=run 5.55), 폭 1.8m. 각 단 = 침목 riser(wood_dark, 높이=riser+0.02, 두께 0.15) + 디딤면 gravel(마사토). 침목 고정말뚝(r 0.025, 침목 전면 양단).
- 길: 상부·하부로 이어지는 흙길 띠(폭 1.8, dirt_park 밝은 틴트) — 세그먼트 박스 3~4개로 완만히 꺾임.
- 자연물: 나무 5그루(상부 1·사면 옆 1·**하부 3 — 수관 상단이 상부 눈높이 근처**), 관목 hedge 블록 5~6 산개, 하부에 벤치 1. 난간·점자·논슬립 전부 기본 False (cue_railing True 시 통나무 손스침 1선 — wood).
- 판정 포인트: 단코 절단선이 흙·자갈 융합으로 **모호**해지는가(의도), 낙엽 흙 텍스처와 침목 대비, 수관 앵커 구도.

### scene05_amphitheater.py — T6 sunken plaza (대단차 × 곡률 × 설비 전무)

- 상부 광장: z=0, x −18..+18, y −14..+14, plaza_light + 차콜 밴드(scene01 모티프 재사용, 간격 3.2).
- **선큰 보울**: 중심 (6, 0), 부채 호 안쪽 방향(−X쪽으로 개방 180°+): build_arc_steps로 **3티어 × riser 0.40 · tread 0.85** (좌석 규격), 반경: 티어 상연 r = 7.5 / 6.65 / 5.8, 호 각도 a0=95°..a1=265° (상부 광장에서 −X쪽으로 열린 반원), 세그 24. 바닥 스테이지: 반경 5.0 원반(z=−1.2, 세그 32 원통 박스 또는 Cylinder h 0.1) plaza_lower 재질.
- 진입: 호 남단(a≈265° 쪽)에 폭 2.2m 방사 방향 일반 계단 6단×0.2(스테이지까지) — 좌석단과 대비되는 "통행용" 계단.
- **설비 전무가 정체성**: cue_railing·cue_tactile 기본 False. cue_material_break는 티어석(밝은 화강암) vs 스테이지(회청)로 기본 True. 대신 상부 광장 쪽 단서: 보울 립 0.45m 밖에 화강암 연석 링(폭 0.3, 다크) — 재질 경계 단서(토글 cue_material_break에 묶음).
- 드레싱: 림 주변 화단 2 + 생울타리 호(보울 반대편), 벤치 2, 가로등 1, 원경 건물 2동(기존 R/C 배치 재사용 가능), 벽돌/잔디 대지.
- 미장센: plaza_approach(광장에서 보울 방향 — grazing에서 보울 완전 소실!), rim_view(림에서 스테이지 부감 −15°), stage_lookup(스테이지에서 티어 올려봄), side_arc(호 접선 방향 — 곡선 단코 원근).
- 판정 포인트: **곡선 단코**가 세그먼트 각짐 없이 읽히는가(세그 24 충분?), h0.3 광장 시점에서 1.2m 보울이 통째로 사라지는 그림.

## D. 공정·검수 (scene01과 동일 체계)

1. Opus: 다운로드 스크립트 확장·실행 (§B 7세트).
2. Opus: scene_common.py + `python3 -c "import scene_common"` 스모크.
3. Opus ×4 병렬: 씬 구현 (본 브리프 §C가 유일 사양. scene01·scene_common 코드를 읽고 관례 유지).
4. 감독: 씬별 적대 리뷰(기하 수치 재계산 — 특히 호 세그 각도·사면 회전·피트 심도) → RT 룩 루프(전 컷 육안) → PT 512spp 파이널 → 보고서.

성공 기준(씬 공통): ① 유형 정체성이 첫눈에 읽힘 ② grazing 은닉 재현 ③ cue 토글 무결성 ④ Z-파이팅·부유·허공 없음 ⑤ 단일 명령 GUI 로드. 씬별 판정 포인트는 §C 각 항.
