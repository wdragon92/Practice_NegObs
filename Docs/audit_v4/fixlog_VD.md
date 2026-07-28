# fixlog_VD — v5.2 사인 정리 (임의 경고 팻말 제거)

담당 : VD
일자 : 2026-07-27
근거 : 사용자 지시 — "계단주의라던지 임의로 설치한 팻말들 별로인 거 같아.
       그냥 도로교통법에 존재하는 팻말 아니면 가능한 경고 팻말 없애주면 좋겠어."

## 방침
- **제거** : `sign_warn_fall`(추락주의) · `sign_caution_step`(계단주의)
  — 도로교통법/시설 관행에 근거 없는 임의 설치 경고 팻말.
- **유지** : `sign_no_entry`(규제표지 실존) · `sign_exit`(지하보도·터널 출구 표지)
  · `sign_info`(사찰/공원 안내, 주차 요금판, 육교 안내 등 실존 관행물).
  기타 실존 관행 구조물(지하도 입구 사인, 목재 이정표, 버스정류장 표지)도 유지.
- **위험 지점 표시 겸용부** : 팻말만 삭제하고 실존 관행물(임시 안전봉·경고 테이프·
  잔존 포스트 밑동)은 **그대로 존치**.
- 사인 외 요소·위험 기하 변경 없음. 렌더/Isaac 미실행.
- 코드 흔적은 `[v5.2 사용자] 임의 경고 팻말 제거` 주석 1줄로 남김.

## 파일별 처리

| 파일 | 제거 | 유지 | 비고 |
|---|---|---|---|
| scene01_campus_stairs.py | signs[] 의 `("Caution","sign_caution_step",−1.0,−6.6)`, TEX_DIR `sign_caution_step` 항목, 좌표/카메라 검산 주석 | `("Info","sign_info",−7.5,−6.8)`, TEX `sign_info` | cue_sign True 유지(안내 1매) |
| scene02_underpass.py | signs[] 의 `("Caution","sign_caution_step",−0.8,2.9)`, ASSET_ROLES `sign_caution_step`, 검산 주석 | `("Exit","sign_exit",7.8,−1.4,−3.2)`, D4 지하도 입구 사인(기둥2+판) | cue_sign True 유지(출구 1매) |
| scene05_amphitheater.py | — (무수정) | — | 감독이 v5.2 에서 이미 `cue_sign=False`·`signs=[]` 처리 |
| scene06_overpass_spiral.py | `PARAMS["sign"]`, ASSET_ROLES `sign_caution_step`, `M["sign"]` 패널 재질, `sc.build_sign` 호출, 체크리스트 7번 문구, 헤더 build_sign 표기 | 버스정류장 표지(BusSign, 드레싱) | `cue_sign` → False(키만 예약). 씬 내 잔여 사인 없음 |
| scene08_sunken_plaza.py | `PARAMS["sign_fall"]`·`sign_step`, ASSET_ROLES `sign_warn_fall`/`sign_caution_step`, 재질 루프 키 2종, build_signs 항목 2종, 차폐 AABB `SignFall`/`SignStep`, 헤더 목표 ④ 문구 | `sign_exit`(북측 출구) 1매, **임시 표지 존치**(안전봉 2 + 경고 테이프 1선 = `build_tempbar`) | 개방 구간 위험 표시는 임시 안전봉·테이프만으로 유지. cue_sign True(임시표지+exit) |
| scene10_park_deck_switchback.py | `PARAMS["sign"]`(계단주의), ASSET_ROLES `sign_caution_step`, `M["sign_face"]`/`M["sign_back"]` 재질, material `sign_back` 색상 상수, `build_sign()` 함수, 호출부, 스모크 AABB `Sign` | 목재 이정표(`signpost`, 기둥+방향판 2) | `cue_sign` → False(키만 예약) |
| scene12_riverside_deck.py | `PARAMS["sign_fall"]`·`sign_step`, ASSET_ROLES 2종, material `sign_back_color`/`sign_back_rough`, 재질 루프, `build_signs()` 함수·호출부, 스모크 AABB 2종, 헤더 목표 ⑥·검증표·뷰/체크리스트 문구 | **훼손 스팬 실존 관행물 존치** — 잔존 포스트 밑동(`stub_xs`) + 경고 테이프 1선(`Rail/Tape`), 난간 결손 기하 불변 | `cue_sign` → False(키만 예약). broken_span 뷰는 밑동·테이프 피사체로 재조준(좌표 불변) |
| scene13_apartment_parking_entry.py | `PARAMS["sign_step"]`(계단주의), ASSET_ROLES `sign_caution_step`, 재질 루프 키, build_signs 항목 | `sign_info`(주차 요금 안내판, 지주식) | cue_sign True 유지(요금판 1매). stair_head 뷰는 계단 되돌음이 피사체 — 재조준 불필요 |
| scene19_fan_winder.py | — (무수정) | — | 감독 소유. `cue_sign=False`·사인 배치 없음 확인 |
| scene20_diagonal_oblique.py | `PARAMS["signs"]`(계단주의 1매), ASSET_ROLES `sign_caution_step`, `build_signs()` 함수·호출부, 체크리스트 7번 문구 | — | `cue_sign` → False(키만 예약) |

### 무수정(사인 유지만 확인)
- scene03/04/15/17/18 : `cue_sign=False`, 사인 배치 없음.
- scene07 : `sign_info`(사찰 안내판, 일주문 앞) — 유지.
- scene09 : `sign_info`(호수공원 안내) — 유지.
- scene11 : `sign_info`(육교 안내) — 유지.
- scene14 : `sign_info`(광장 안내) — 유지.
- scene16 : `sign_exit`(지하보도 출구) — 유지.
- scene21 : `sign_info`(광장 안내) — 유지.
- `sign_no_entry` : 현재 main 씬 21종에서 사용처 없음(에셋만 존재).

## 검증
- `grep -rn "sign_caution_step|sign_warn_fall" scenes/main/*.py` → 0건.
- 수정 8개 파일 전부 `python3 -m py_compile` 통과
  (01, 02, 06, 08, 10, 12, 13, 20).
- `NEGOBS_SMOKE=1` 기하 자기검증 통과 : scene06 / 08 / 10 / 12 / 13
  (회랑·차폐·난간 결손·보행 연속성 항목 전부 이전과 동일 판정).
  scene01/02/20 은 스모크 경로가 Isaac 부팅을 요구 — 기존과 동일(미실행).
- 위험 기하(계단·피트·난간 결손·낙차) 트랜스폼 변경 0건.
