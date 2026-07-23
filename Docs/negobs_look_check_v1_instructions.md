# NegObs 룩 체크 v1 — 자연 도랑 낙하 환경 (Claude Code 지시문)

## 0. 이 작업이 뭔가

NegObs 연구(RGB 맥락 단서로 은닉 낙하 위험을 추정)의 합성 데이터 파이프라인 첫 단계인 **외형 검증(룩 체크)** 씬을 만든다.
목표: 실사에 가까운 "자연 초지 + 도랑형 낙차" 씬 1개를 Isaac Sim GUI로 띄우고, 사용자가 뷰포트에서 자유 비행하며 자연스러움을 눈으로 판정할 수 있게 하는 것.
이 스크립트의 지형 생성 코드는 이후 데이터 생성기 모듈의 씨앗이 되므로, **모든 치수·강도는 코드 상단 PARAMS로 파라미터화**한다.

## 1. 실행 환경 — 고정 사실 (바꾸지 말 것)

- Isaac Sim **4.5.0** (pip 설치), conda env `env_isaaclab`, Python 3.10, RTX 4090, Ubuntu.
- 실행 시퀀스 (반드시 이 순서):
  `unset PYTHONPATH VIRTUAL_ENV` → `conda activate env_isaaclab` → `export PYTHONNOUSERSITE=1` → `python 파일.py`
- API는 4.5 기준 `isaacsim` 네임스페이스(`from isaacsim import SimulationApp` 등). 구경로 `omni.isaac.*`는 쓰지 말 것. **코딩 시작 전에 실제 설치본에서 임포트 스모크 테스트부터 할 것.**
- SimulationApp 초기화 블록(해상도 명시 + DLSS execMode)은 기존 `falling_ball_toy_v9.py`의 검증된 블록을 재사용한다. 파일 위치는 사용자에게 물어볼 것. 키보드 입력 처리(carb input) 패턴도 같은 파일에서 재사용.
- 스테이지 단위가 미터(1.0)인지 시작 시 확인.

## 2. 최종 산출물

- `negobs_look_check_v1.py` — 단일 실행 파일 (headless=False, GUI 모드)
- `assets/` — PolyHaven 텍스처·HDRI 다운로드 스크립트 + 다운로드된 파일 (전부 로컬 파일, Nucleus/클라우드 에셋 의존 금지)
- `look_check/` — S키 수동 캡처 저장 폴더
- 실행 직후 콘솔에 조작법 + 검증 체크리스트 배너 출력 (§7)

## 3. 지형 사양 — 형태가 자연스러움의 절반

### 3.1 베이스 지형 (초지)

- 30 × 30 m 하이트필드, 격자 간격 0.05 m (601×601 정점, 약 72만 삼각형 — 4090에서 무리 없음. 성능 문제 시에만 0.1 m로 낮출 것).
- 완만한 기복: 프랙탈 노이즈 2~3옥타브, 진폭 0.2~0.3 m, 최장 파장 8~15 m. "평지인데 완전히 평평하지는 않은 농경지·초지" 느낌.
- 미세 거칠기: 진폭 1~3 cm, 파장 0.2~0.5 m를 지오메트리에 추가 (근접 시 땅이 판판한 판으로 안 보이게).
- 정점 노멀은 인접 면 평균으로 **스무스 계산**해서 직접 넣을 것 (`subdivisionScheme = none`). 패싯(각진 면) 금지.

### 3.2 도랑 — 핵심 사양

실제 자연 흙 도랑의 해부학을 그대로 따른다. 콘크리트 수로가 아니라 **침식된 흙 도랑**이다.

- **경로**: 직선 금지. 지형을 가로지르는 길이 약 14 m, 중심선을 저주파 노이즈로 사행(구불거림)시킬 것 — 진폭 ±1.0 m, 파장 5~8 m.
- **단면**: 사다리꼴 기반. 자연 흙 도랑은 수직벽이 아니다.
  - 깊이 1.2 m (기본값 — 연구의 위험 판정 주기준 0.3 m를 명확히 초과하는 대표 추락형)
  - 상단 폭 2.2 m, 바닥 폭 0.7 m → 둑 경사 약 55~60°
  - 깊이·폭은 길이 방향으로 ±20% 서서히 변조. **균일 단면 절대 금지.**
- **립(가장자리)**: 날카로운 모서리 금지 — 반경 0.1~0.2 m로 둥글리고, 립 라인에 고주파 노이즈(진폭 0.1~0.15 m, 파장 0.4~0.7 m)를 더해 물어뜯긴 듯 불규칙하게.
- **붕괴 지점 2곳**: 립이 0.1~0.2 m 낮아지고 둑 경사가 완만해지는 폭 1~2 m 구간. 실제 도랑에서 가장 눈에 띄는 특징.
- **바닥**: 평평 금지. 중앙이 살짝 낮은 U형 + 5~10 cm 요철(퇴적·자갈 느낌).

### 3.3 카빙 구현 힌트

1. 중심선을 폴리라인으로 생성 (x 진행 + y = 사행 노이즈).
2. 각 격자점에서 중심선까지 최단거리 d 계산.
3. 단면 프로파일 f(d): d < 바닥반폭 → 최대 깊이 / 바닥반폭~상단반폭 → smoothstep 보간 / 그 밖 → 0. 상단반폭 근방에서 립 라운딩.
4. 립 노이즈는 위치별 노이즈를 상단반폭에 더하는 방식으로 (가장자리가 들쭉날쭉해짐).
5. 최종 높이 = 베이스 지형 − 도랑 깊이 프로파일. 도랑 마스크(어느 점이 도랑 내부인지)와 국소 깊이는 재질 분류(§4)를 위해 보관.

## 4. 재질 사양 — 자연스러움의 나머지 절반

### 4.1 3영역 분할 (단일 메시 + GeomSubset)

면(face) 단위로 3분류해서 `UsdGeom.Subset`(familyName="materialBind") 3개를 만들고 각각 재질 바인딩:

| 영역 | 분류 규칙 | 재질 |
|---|---|---|
| TOP (초지 윗면) | 도랑 마스크 밖 | 풀+바위 혼합 |
| WALL (둑 벽면) | 도랑 안 & 국소 깊이 < 최대깊이의 85% | 마른 노출 흙 |
| BOTTOM (도랑 바닥) | 도랑 안 & 국소 깊이 ≥ 최대깊이의 85% | 젖은 진흙 |

**경계 디더링 필수**: 분류 임계값에 공간 노이즈를 섞어 경계선이 0.2~0.4 m 폭으로 얼룩덜룩하게 섞이도록. 자로 그은 경계선이 보이면 실패.

### 4.2 텍스처 — PolyHaven 확정 슬러그 (전부 CC0)

| 용도 | 슬러그 | 선택 이유 |
|---|---|---|
| TOP | `aerial_grass_rock` | 이끼·풀 덮인 거친 표면 + 흙 패치 8K — 경계 전이가 자연스러움 |
| WALL | `brown_mud_dry` | 마르고 부슬거리는 흙, 알갱이·잔돌 — 노출 생흙 벽 |
| BOTTOM | `brown_mud_03` | 젖은 광택 패치 + 발자국·요철 — 도랑 바닥의 습기 표현 |
| 하늘(주) | `qwantani_noon_puresky` | 맑은 한낮, 강한 태양 → 도랑 안 그림자 선명 |
| 하늘(비교) | `qwantani_dawn_puresky` | 낮은 태양, 부드러운 광 → 긴 그림자 비교용 |

- 다운로드: `https://api.polyhaven.com/files/{slug}` 로 파일 URL을 해석해 받을 것 (API 응답 형식은 실제 호출로 확인). 텍스처는 4K jpg의 diffuse / **nor_dx** / rough 3종, HDRI는 4K exr.
- 네트워크가 막히면: 필요한 파일 목록(슬러그·해상도·종류)을 콘솔에 출력하고 사용자가 `assets/`에 수동 배치하도록 안내 후 대기.

### 4.3 OmniPBR 세팅 (문서로 확인된 파라미터)

- 각 재질은 OmniPBR MDL. **`project_uvw = True` + `world_or_object = True`(월드 공간 투영)** — 이 조합이면 메시에 UV를 만들 필요가 없고, 경사 벽면에서도 텍스처가 늘어나지 않는다.
- `texture_scale`로 타일 크기 조절. 시작값: TOP은 실세계 약 3.5 m 타일, WALL 1.5 m, BOTTOM 1.8 m — 값과 실크기의 대응은 화면에서 확인하며 조정 (풀잎 몇 cm, 잔돌 5~20 cm로 읽혀야 함).
- 컬러 스페이스: albedo는 sRGB(auto), normal·roughness는 raw.
- 노멀맵은 PolyHaven **`_nor_dx`(DirectX)** 버전 사용 — OmniPBR 기본 규약. 부득이 GL 버전이면 Normal Map Flip V 설정 조정.
- 정확한 MDL 입력 이름(diffuse_texture, normalmap_texture, roughness 계열 등)은 설치본의 OmniPBR.mdl에서 확인하고 쓸 것. 추측 금지.

### 4.4 함정 주의

- 텍스처 타일 반복 무늬가 3 m 이상 거리에서 보이면 스케일·회전 오프셋으로 완화.
- BOTTOM의 젖은 느낌이 약하면 roughness에 0.6~0.8 배 곱 (텍스처 자체 광택 우선, 과하면 플라스틱).

## 5. 조명·하늘

- DomeLight 1개에 HDRI exr 텍스처. 별도 태양 라이트는 기본 불필요 (HDRI가 unclipped 고휘도 태양 포함). 그림자가 너무 흐릴 때만 보조 DistantLight(각도 0.53°) 허용.
- intensity는 화면 노출이 자연스러운 야외 사진처럼 보이게 조정 (과노출·회색 낮 금지).
- **L 키**: noon ↔ dawn HDRI 전환 (DomeLight 텍스처 교체).
- **[ / ] 키**: DomeLight Z축 회전 ±15° (태양 방위 → 도랑 그림자 방향 조절).

## 6. 렌더·뷰포트·키 조작

- 기본 렌더: RTX Real-Time (비행용). 안티앨리어싱은 DLSS (`/rtx/post/aa/op = 3`), execMode는 v9 블록 값.
- **P 키**: `/rtx/rendermode`를 "PathTracing" ↔ "RaytracedLighting" 토글. PathTracing 세팅: `/rtx/pathtracing/spp = 1`, `/rtx/pathtracing/totalSpp = 512`, 디노이저 켬. 콘솔 배너에 "패스 트레이싱은 멈춰 서서 볼 때, 이동은 실시간 모드 권장" 안내.
- **S 키**: 현재 뷰포트를 `look_check/negobs_YYYYmmdd_HHMMSS.png`로 캡처 (omni.kit.viewport 계열 캡처 API — 실제 이름 확인해서 사용).
- 시작 카메라: 도랑 중앙에서 6 m 떨어진 지점, 높이 1.2 m, 피치 −8°, 도랑을 바라보게.
- 메인 루프: `while simulation_app.is_running(): update()`. **물리 불필요** — 렌더 전용이므로 World/물리 씬·콜라이더 생성 생략.

## 7. 실행 시 콘솔 배너 (사용자 확인용 — 그대로 출력)

```
[조작] 우클릭+WASD 비행 · 우클릭+스크롤 속도 · P 패스트레이싱 토글 · S 스크린샷 · L 하늘 전환 · [ ] 태양 방위
[체크리스트]
 1. 높이 2m 정면    — 도랑이 실제 사진처럼 읽히는가
 2. 높이 0.5m·8~10m — 낙차가 시야에서 자연스럽게 사라지는가 (grazing angle 은닉)
 3. 립 라인         — 직선 티 없이 물어뜯긴 불규칙성이 보이는가
 4. 재질            — 타일 반복 무늬 / 벽면 늘어남 / 경계선 부자연 없는가
 5. 그림자          — noon과 dawn(L키)에서 도랑 안 음영이 자연스러운가
 6. 근접 0.3m       — 노멀 디테일이 살아 있는가
```

## 8. 진행 방식

**Phase A (지금)**: §3~7 전부. 완료 시 아래 보고 후 **사용자 확인 대기**. 먼저 나가지 말 것.
**Phase B (사용자 승인 후에만)**: ① 경계 디더링 미세조정 ② 잔돌 스캐터 15~25개 (5~20 cm, 변형 프리미티브 + 흙 재질, 도랑 안팎) ③ 립 바깥 0~0.3 m 대역에 풀 클럼프 20~30개 (PolyHaven ground cover 모델 활용 가능) ④ WALL 상부 어두운 틴트 (상/하 subset 분할, albedo 0.6배 — 토양 유기물 층 표현).

**금지 사항**
- 물 표면 넣지 말 것 — 수역 위험은 별도 클래스라 v1은 순수 추락형으로 유지.
- 펜스·덮개·표지판·구조물 없음 (다음 단계 소관).
- 도메인 랜덤화 없음 — 단일 고정 씬.
- 문제 발생 시 임의로 사양 축소하지 말고 보고할 것.

**완료 보고 형식**: ① 실제 확인된 API 경로 목록 ② 에셋 다운로드 결과 ③ 실행 명령 ④ 알려진 한계·타협점. 에러 공유는 전체 로그 대신 핵심 줄만.

**PARAMS 스켈레톤** (코드 상단에 이 구조로):

```python
PARAMS = dict(
    terrain=dict(size=30.0, cell=0.05, base_amp=0.25, base_wavelength=12.0,
                 micro_amp=0.02, micro_wavelength=0.3, seed=42),
    ditch=dict(length=14.0, depth=1.2, depth_jitter=0.2,
               top_width=2.2, bottom_width=0.7,
               meander_amp=1.0, meander_wavelength=6.0,
               lip_round=0.15, lip_noise_amp=0.12, lip_noise_wavelength=0.5,
               collapse_zones=2),
    material=dict(top_tile=3.5, wall_tile=1.5, bottom_tile=1.8,
                  boundary_dither=0.3, bottom_depth_ratio=0.85),
    light=dict(hdri_main="qwantani_noon_puresky", hdri_alt="qwantani_dawn_puresky",
               dome_rotation_step=15.0),
    render=dict(pt_total_spp=512),
)
```
