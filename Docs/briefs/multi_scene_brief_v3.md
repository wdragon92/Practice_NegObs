# NegObs 씬 라이브러리 v3 — 16씬 확장 브리프 (총 21씬)

작성 2026-07-25 · 감독 Fable · 근거: `Docs/stair_typology_survey_v2.md` (T9~T21, 명소 실측치)
기존: scene01~05 (T1/T3/T5/T4/T6). 신규: scene06~21. 관례·토글·캡처 파이프라인은 v2 브리프와 동일.

## A. 회귀 방지 체크리스트 [전 씬 필수 — 룩 루프에서 확정된 표준]

1. 수관 알베도: canopy_a (0.025,0.045,0.015) / canopy_b (0.035,0.060,0.020), rough 1.0, specular_level 0.0. wood (0.30,0.20,0.12). *sRGB 감마: 알베도 0.15는 정오광에서 표시값 127로 밝다 — "어두운 색"은 0.02~0.06 대역.*
2. 잔디: scale 4.0 + tint (0.55,0.68,0.42). 상수색 만들 때 위 감마 규칙 적용.
3. **공동(피트·보울·수직낙차) 위를 주변 지면 평면이 덮지 않는지** — 개구는 4박스 분할.
4. 지평선 폐쇄: 주 카메라 축 정면에 원경 요소(건물/능선/울타리/암벽). 부지 가장자리 허공 금지(대지 y±40+).
5. USD 프림명에 좌표·음수 문자열 금지 (인덱스 명명).
6. sc.* 헬퍼는 stage 첫 인자 — py_compile로 못 잡으니 AST 감사 스크립트(scratchpad/audit_stage.py 패턴) 실행.
7. 조명: scene01 light dict + SUN_AZ_OFFSET 기본 171.5 (씬별 재정의 허용 — 사유 주석).
8. Z-파이팅: 동일평면 금지, 겹침 최소 1mm 오프셋. 계단은 +X 하강 관례(빌더), 회전 배치는 rot-group으로.

## B. scene_common v2 확장 (신규 빌더 — 수학 정의는 서베이 v2 §3)

```
build_helix_steps(stage,prefix,cx,cy,r_in,r_out,a0_deg,step_deg,n,riser,z0,mtl,ccw=True,collider=True)
    # 단 i: 환형 섹터 박스(rotZ=a0+(i+0.5)*step_deg*dir), top z=z0-(i+1)*riser (하강) — 나선·winder 공용
build_helix_ramp(stage,prefix,cx,cy,r_in,r_out,a0_deg,a1_deg,seg,z0,z1,thick,mtl)
    # 세그 박스에 rotZ + 로컬 rotY(접선 기울기 atan2(dz_seg, chord)) — 매끈한 나선 램프
build_worn_stone_stairs(stage,prefix,x0,y0,y1,n,riser_mu,tread_mu,blocks,seed,mtl,base_z, z_top=0,
                        jr=0.03,jt=0.10,jz=0.02,jyaw=3.0)
    # 단 i를 blocks개 가로 블록으로 분할, numpy RandomState(seed)로 riser/tread/z/yaw 지터(고정 시드=재현)
build_rot_group(stage,path,pivot_xy,rot_deg) -> Xform  # 하위에 기존 빌더 배치용 회전 그룹
build_open_riser_stairs(stage,prefix,x0,y0,y1,riser,tread,n,z_top,mtl_tread,mtl_stringer,
                        tread_t=0.04, gap=0.02)  # 스트링거 2본(경사 박스)+디딤판만, 라이저 없음
build_canopy(stage,prefix,x0,x1,y0,y1,z_roof,post_r,mtl_roof,mtl_post)  # 4주+지붕판
build_straight_stairs(...)에 width_pairs=None 추가  # 단별 (y0,y1) — 폭 점증(tapered) 지원
```
기존 재사용: build_arc_steps(부채꼴 단별 호출), build_slope(램프), build_water, 드레싱 일체.

## C. 신규 텍스처 (에셋 에이전트: PolyHaven/ambientCG API에서 아래 역할로 검색·선정·검증. 슬러그는 후보일 뿐 — 404면 유사 대체)

| 역할 | 후보 | canonical |
|---|---|---|
| 사원 마모석 | PH stone_tiles_03 / castle_wall? 어두운 화강 잡석 | `stone_worn_*` |
| 사암(스텝웰·가트) | PH red_sandstone_tiles / sandstone_cracks | `sandstone_*` |
| 대리석/밝은 기념석 | PH marble_01 / white_marble? | `marble_light_*` |
| 녹슨 철(비상계단·잔도 보강) | PH rusty_metal_02 / metal_plate | `metal_rust_*` |
| 회벽(골목 주택) | PH painted_plaster_wall / plastered_wall | `plaster_*` |
| 절벽 암반 | 기존 rock_wall + PH rock_face | `rock_face_*` |
| 도장 철판(예술계단 베이스) | 상수색으로 충분 — 생략 가능 | — |

## D. 신규 16씬 사양 (scene06~21). 공통: SCENE_CONFIG 7키, grid_views(축은 씬별 명시) + 미장센 3~4컷, LOOKCHECK look_check/sceneNN/. 낙차 ≥0.3m [고정]. 씬별 "특색 포인트"가 검수 1순위.

**scene06_spiral_towerstone (T9·사용자 요청)** — 성탑/전망대 나선 석계단 하강. 중심 석주 r0.5, 계단 r_in0.5/r_out2.2, step 22.5°, 32단·riser0.18 (2회전, 낙차 5.76), 외벽 원통 셸(r2.5, 창 슬릿 3개), stone_worn. 진입은 지상 개구에서 하강(탑 지하로) — 상단 광장(화강암)+개구 연석. 특색: 곡률 자기폐색 — 2~3단 아래가 완전 은폐. 미장센: 개구 위, 나선 내부 1/2회전 지점, 슬릿 역광.
**scene07_wornstone_temple (T16·사용자 요청)** — 사찰 진입 마모 석단 18단(riser_mu0.17,tread_mu0.38, blocks5, seed=77, 지터 상한), 폭 3.2. 상부 사찰 마당(마사토+담장 힌트), 하부 진입로, 측면 노후 석축(rock_wall)+노송 2(수관 표준). 이끼 톤 tint. 특색: 비직선 단코 — 소실점 규칙 붕괴. stone_worn.
**scene08_stepwell_lattice (T11)** — 스텝웰 미니어처: 사각 우물 12×12, 깊이 3.6(3층). 양측 뱅크에 대각 미니 플라이트(rot_group 45°, 5단×0.28) 지그재그 6조/층, 중앙 수면(-3.4). sandstone. 상부 평탄 사암 테라스+파라펫 연석. 특색: 격자 반복이 낙차 경계 흡수. 미장센: 상부 모서리 부감 -12°, 뱅크 정면, 수면 근접.
**scene09_ghat_riverfront (T12)** — 수변 가트: 폭 10m, 36단 불균등(riser 0.14~0.20 테이블), 중간 참 2개(깊이 1.2), 수면(-4.2)이 하부 6단을 침수(수위선: 침수부 어두운 틴트 밴드). sandstone+물때 틴트. 배들 대신 계선주 2. 특색: 수면이 계단 중간을 자르는 경계. T5와 구분: 전면 석재·초광폭·참.
**scene10_switchback_cliff (T13)** — 산릉 갈지자: 암반 사면(45°, rock_face 대형 박스 계단식 적층) 위 철제 플라이트 6개×8단(폭 0.8, open_riser, metal_rust)+참(1.2×1.2)마다 180° 반전(rot_group), 파이프 난간 양측(cue_railing 기본 True — 산악 안전시설). 특색: 방향 반전 + 투과 디딤판 아래 계곡. 원경: 능선 실루엣(대형 rock 박스 2단).
**scene11_grating_fireescape (T19)** — 건물 외벽 비상계단: 벽돌 벽면(기존 brick), 2플라이트×10단 open_riser(metal_rust 스트링거+디딤판, 발판 사이 gap 0.025), 중간 참, 파이프 난간. 지면 아스팔트 톤. 특색: 라이저 부재 — 디딤판 틈으로 아래 투시, 격자 그림자 스트라이프(디딤판 다수 얇은 박스로 슬릿 3개씩). 
**scene12_cliff_plankwalk (T17)** — 절벽 잔도: 수직 암벽(rock_face, x-z 평면 대형), 폭 0.35 목판(weathered_planks) 캔틸레버 계단 20단(riser0.16) 벽면 따라 하강, 바깥쪽 완전 개방(수백m 낙차 느낌 — 하부 안개톤 대지 z=-30), 벽측 쇠사슬 힌트(가는 원기둥 체인 근사, cue_railing). 특색: 편측 무한낙차 — missing ground band 극단. 카메라 밴드 준수(밴드 내에서 낭떠러지 연출).
**scene13_helical_parkingramp (T10)** — 주차장 나선 램프: helix_ramp(r_in6/r_out9.5, 1.25회전, 낙차 3.2, 두께 0.35, 콘크리트) + 내측 병설 나선 계단(helix_steps r_in4.8/r_out6). 중앙 코어 원통. 연석·중앙선 도색 밴드(상수색 박스). 특색: "경사(주행 가능) vs 계단(불가)" 혼동쌍 병치.
**scene14_grandstair_illusion (T14)** — 포템킨형 착시: 40단(riser0.15), 폭 상부 6→하부 10 (width_pairs 선형), 참 3개(깊이 2.4). marble_light/밝은 화강. 측면 경사 파라펫 벽. 상부 전망 소광장+가로등 2. 특색: 상부에서 참만 보여 "평탄한 테라스"로 읽힘(은폐 착시).
**scene15_alley_labyrinth (T15)** — 감천/알파마 골목: 폭 1.2 계단 25단(riser0.17, 콘크리트) 이 좌우 파스텔 주택(회벽 plaster + 상수 파스텔 틴트 5색, 창·문 인셋) 사이로 하강, 중간 꺾임 1회(rot_group 25°), 전선줄 힌트(가는 원기둥 2). 특색: 벽 압축 원근 — 좁은 시야에서 낙차 소실. 하부 골목 이어짐.
**scene16_canopy_shadow (T20)** — 캐노피 계단: 지하상가형 입구지만 지상형 — 14단(폭 3), 위에 반투명 대신 솔리드 루프(옅은 회색)+기둥 4, 정오광에서 계단 전체가 캐노피 그림자 안. 주변 밝은 보도. 특색: T3의 반전 — 하부가 아니라 **상부 그림자 밴드**가 위험 신호. cue_nosing 기본 True.
**scene17_ramp_pair_hangang (T21)** — 한강 고수부지형: 제방 콘크리트 계단(20단 폭 4) + 바로 옆 자전거/휠체어 램프(build_slope 8%, 폭 2.5, 중앙 도색선), 하부 자전거도로(아스팔트 톤 밴드)+잔디+강물(기존 water). 특색: 같은 낙차의 '주행 가능 경사'가 인접 — 모델이 경사도와 낙차를 분리 학습해야 하는 대비쌍.
**scene18_wavy_artstair (T18)** — 예술 물결 계단: 16단, 단코가 사인파(진폭 0.35, 파장 4m — 단별 y 세그 8개 박스로 근사), 라이저 고채색 5색 교대(상수색: (0.7,0.15,0.1)/(0.9,0.6,0.1)/(0.15,0.4,0.65)/(0.8,0.75,0.7)/(0.2,0.5,0.3) — 감마 감안 중간톤), 디딤면 밝은 콘크리트. 도시 소광장 맥락. 특색: 고대비 색이 오히려 낙차 인지를 교란(위장 대비군).
**scene19_fan_winder (T7)** — 부채꼴 코너 계단: 건물 모서리 1/4회전(90°), 12단, r_in1.2/r_out4.0 (build_arc_steps 단별: 각 단 7.5° 섹터, top_z 하강), 화강암, 내측 기둥+외측 낮은 파라펫. 특색: 단코가 방사선 — 직선 소실점 부재.
**scene20_diagonal_oblique (T8)** — 대각 사교: 광장 보행축(+X)에 대해 30° 틀어진 직선 계단 14단(rot_group) — 정면 프리셋에서 낙차 경계가 화면을 사선으로 가로지름. 상부·하부 포장 상이(기존 텍스처 재사용). 특색: 정렬 가정 붕괴 — 프리셋 축은 보행축 유지 [고정].
**scene21_monumental_selfocclude (T2)** — 관공서/도서관 진입 대계단: 18단(riser0.15/tread0.32, 폭 8), 양측 석재 파라펫+중앙 난간 2선, 상부에 기둥 4주 파사드 힌트(원기둥+인방), marble_light. 특색: 다단 자기폐색 — 하부 12단이 접혀 소실, 난간 하강선+상단 1~2단코만 잔존.

## E. 공정

1. 에셋 에이전트: §C 검색·다운로드·검증 (기존 스크립트 확장).
2. 라이브러리 에이전트: §B 빌더 구현 + 기하 자기검증(수치 프린트) + AST/임포트 스모크. **감독이 수학 재검산.**
3. 배치 구현 4기 병렬: A(06,13,19,18 곡선계) B(07,09,12,10 석재·자연계) C(11,15,16,20 도시구조계) D(08,14,17,21 기념·수변계). 각 씬 = 얇은 파일(PARAMS+build+views, main 골격은 scene02~05 패턴).
4. 감독: 배치별 RT 렌더 → 그리드 판정 → 수정 라운드 → 전 씬 PT 파이널 → 보고서.
