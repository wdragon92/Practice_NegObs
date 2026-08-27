# P0 — 베이스라인 클론(Baseline_NegObs) 오염 검사 (2026-08-28)

**승용 요약**: 논문 코드 클론은 upstream과 **동일 커밋**이고, 월드·구멍 모델·플러그인 파일은 **한 바이트도 안 바뀌었다**.
로컬 수정은 실행용 launch 파일 한 줄뿐이다. 그대로 재사용해도 된다(결재 ⑤ 승인분). [실측]

| 항목 | 실측 |
|---|---|
| 경로 | `/home/vislab/Desktop/work_sy/Baseline_NegObs/src/negativeobstacleavoidandance` |
| upstream | `https://github.com/OxyBloom/negativeobstacleavoidandance` (origin/main) |
| 커밋 | 로컬 HEAD `408f023` (2026-02-02 "Update README.md") = origin/main `408f023`, ahead/behind 0/0 (`git fetch` 후 확인) |
| 추적 파일 변경 | **1건** — `bumperbot_localization/launch/nav.launch.py` 1줄: nav2 `bringup_launch.py` → `navigation_launch.py` (08-19 구동 수리, 월드·모델·플러그인과 무관) |
| 미추적 | `bot_camera/bot_camera/neg_env/COLCON_IGNORE` (빌드 제외 마커 1개) |
| 월드·모델 | `git diff --quiet HEAD -- bumperbot_description/worlds bumperbot_description/models` → **동일** |

월드·모델 sha256 앞 16자리 (재사용 때마다 이 표와 대조):

| 파일 | sha256[:16] |
|---|---|
| `worlds/eworld2.world` | `9cb2a2c028cfaace` |
| `worlds/expandedworld.world` | `2a1956d3ea564a4f` |
| `worlds/smallest_world.world` | `5c88e743b07eb8f6` |
| `worlds/eworld.world` | `dc8b7a19f9895a72` |
| `models/large_holed_floor/model.sdf` | `c2751bac52bcd5dd` |
| `models/large_holed_floor/meshes/large_holed_floor.stl` | `ab75bc68feb3adae` |

**보호 규칙(창고 A트랙, 브리프 §7·P2)**: upstream 파일은 제자리에서 절대 고치지 않는다. 변형 월드·구멍 실측·렌더 스크립트는
`experiments/e1_0827/vth/` 아래 **사본**으로 만들고(08-24 창고 실험이 한 방식과 같음), 작업 전후에 위 표로 `sha256sum` 대조를 남긴다.
플러그인(`realsense_gazebo_plugin`) 설정을 바꿔야 하면 사본 월드/launch에서만 바꾸고 상수 대장에 기록한다.
