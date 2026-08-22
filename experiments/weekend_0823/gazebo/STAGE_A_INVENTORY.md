# STAGE a — Baseline_NegObs Gazebo 조사 (WEEKEND_BRIEF_0823 §6.7-a)

작성 2026-08-23 · CPU-5 · **시뮬레이터는 한 번도 띄우지 않았다** (전부 파일 정독 + `gz sdf -k` 정적 검사).
`Baseline_NegObs`는 **읽기 전용**으로만 다루었다 — 그 아래에는 아무것도 쓰지 않았다.

---

## 1. 한 줄 답

**Gazebo Classic 11.10.2 (ROS 2 Humble, `gazebo_ros_pkgs` 3.9.0). 신형 `gz`(Ignition/Garden) 아니다.**
우리 `.world`를 저들의 로봇·카메라와 함께 **저장소를 건드리지 않고** 띄울 수 있다 —
`world_name`에 **절대경로**를 넣으면 된다(§4).

---

## 2. 버전 실측

| 항목 | 값 | 근거 |
|---|---|---|
| Gazebo | **Classic 11.10.2** (`gazebo`, `gzserver`, `gzclient`) | `gazebo --version`; `dpkg -l` → `gazebo 11.10.2+dfsg-1` |
| 신형 gz | **없음** — `/usr/bin/gz`는 Classic의 CLI 도구(`gz sdf` 등)일 뿐 `gz sim` 아님 | `gz sim --version` → `Invalid arguments` |
| ROS 2 브리지 | `ros-humble-gazebo-ros-pkgs 3.9.0`, `gazebo-ros2-control 0.4.10` | `dpkg -l` |
| SDF | 저들 월드는 전부 `<sdf version='1.6'>` | `bumperbot_description/worlds/*.world` |
| ignition 라이브러리 | `libignition-math6/msgs5/transport8` — Classic 11의 내부 의존성이지 신형 gz 아님 | `dpkg -l` |

→ **Classic/ROS2 조합 확정.** 씬은 SDF 1.6 + Classic 기본 프리미티브/머티리얼로 쓴다.

## 3. 저들이 어떻게 띄우는가

3-터미널(또는 `./start_baseline.sh`가 tmux 세션 `baseline`에 창 3개):

| 창 | 명령 | 하는 일 |
|---|---|---|
| sim | `ros2 launch bumperbot_bringup simulated_robot.launch.py` | Gazebo + 컨트롤러 + joy/twist_mux + AMCL/map_server + RViz + `scan_merge.py` |
| nav | `ros2 launch bumperbot_localization nav.launch.py` | Nav2 (사용자가 `navigation_launch.py`로 고쳐 놓음) |
| yolo | `ros2 run bot_camera clean_yolo.py` | RGB→YOLO→깊이 검증→`/virtual_obstacles` |

런치 체인:
```
bumperbot_bringup/launch/simulated_robot.launch.py
  └─ bumperbot_description/launch/gazebo.launch.py      ← world_name 인자가 여기 있다
       ├─ gazebo_ros/launch/gzserver.launch.py  (world:=<경로>)
       ├─ gazebo_ros/launch/gzclient.launch.py
       ├─ robot_state_publisher  (xacro → robot_description)
       └─ gazebo_ros spawn_entity.py  -entity bumperbot -topic robot_description -z 0.15
```

파일: `/home/vislab/Desktop/work_sy/Baseline_NegObs/src/negativeobstacleavoidandance/bumperbot_description/launch/gazebo.launch.py`

## 4. 월드 교체 — 되는가? **된다. 절대경로로.**

`gazebo.launch.py`가 월드 경로를 만드는 방식:

```python
world_name_arg = DeclareLaunchArgument(name="world_name", default_value="smallest_world")
world_path = PathJoinSubstitution([
    bumperbot_description,                                   # install/.../share/bumperbot_description
    "worlds",
    PythonExpression(["'", LaunchConfiguration("world_name"), "'", " + '.world'"])
])
```

두 가지 사실이 맞물린다:

1. **`PathJoinSubstitution.perform()`은 `os.path.join(*performed)`** 이다
   (`/opt/ros/humble/lib/python3.10/site-packages/launch/substitutions/path_join_substitution.py`).
   `os.path.join`은 뒤 인자가 **절대경로면 앞을 전부 버린다** — 실측:
   `os.path.join('/a/share','worlds','/abs/path/gz_drop1.world')` → `/abs/path/gz_drop1.world`.
2. `simulated_robot.launch.py`는 `gazebo.launch.py`를 `launch_arguments` 없이 include 하지만,
   include 스코프는 부모의 LaunchConfiguration을 **상속**한다. 저자(승용)의
   `RUN_GUIDE.md`가 이미 `world_name:=eworld`가 통한다고 기록해 두었다 — 경험적 확인 완료.

→ 그래서 `world_name`에 **확장자 없는 절대경로**를 주면 런치가 `.world`를 붙여
저장소 바깥의 우리 파일을 연다. **Baseline_NegObs에 파일을 넣을 필요가 전혀 없다.**

### 우리가 쓸 정확한 명령 (실행하지 않음, 기록만)

```bash
# (A) 권장 — Gazebo + 로봇 + 우리 카메라만. Nav2/AMCL/RViz 없음 = 로그 조용, GPU 절약
source /home/vislab/Desktop/work_sy/Baseline_NegObs/setup_env.sh
ros2 launch bumperbot_description gazebo.launch.py \
  world_name:=/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/gazebo/worlds/gz_drop1
#                                                                                    ^^ .world 없음
```

```bash
# (B) 최소 — 로봇조차 안 띄움. 정지 카메라만으로 캡처할 때 가장 가볍다.
#     여기서는 world 인자가 '전체 경로 + .world'다 (다른 인자다, 헷갈리지 말 것)
ros2 launch gazebo_ros gazebo.launch.py \
  world:=/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/gazebo/worlds/gz_drop1.world
#   gui:=false 를 붙이면 gzclient 없이 서버만 (GPU 여유 확보)
```

```bash
# (C) 저들 스택 전부 (stage-e YOLO 비교용). AMCL/map은 우리 월드와 안 맞아 시끄럽지만 무해
ros2 launch bumperbot_bringup simulated_robot.launch.py \
  world_name:=/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/gazebo/worlds/gz_drop1
```

### 주의 — 저들 런치가 환경변수를 덮어쓴다
`gazebo.launch.py`는 `SetEnvironmentVariable("GAZEBO_MODEL_PATH", <저들 models 디렉터리>)`로
**GAZEBO_MODEL_PATH를 append가 아니라 overwrite** 한다. 그래서 우리 월드는
`<include>`·`model://`·메시를 **하나도 쓰지 않고** 인라인 프리미티브 + 스톡 `Gazebo/*`
머티리얼만으로 만들었다. 부작용으로 (B)처럼 저들 런치 없이 띄워도 똑같이 열린다.

## 5. 카메라 — 무엇이 붙어 있고 어디로 나오는가

로봇(bumperbot)의 카메라는 **RealSense D435 시뮬**(`realsense_gazebo_plugin`, `librealsense_gazebo_plugin.so`):

| 항목 | 값 | 출처 |
|---|---|---|
| 컬러 토픽 | `/camera/color/image_raw` (`sensor_msgs/Image`, RGB_INT8) | `realsense2.urdf.xacro` `<colorTopicName>`; `dataset.py`가 이 이름으로 구독 |
| 정렬 깊이 | `/camera/aligned_depth_to_color/image_raw` | 같은 파일 |
| 포인트클라우드 | `/camera/depth/color/points` (cutoff 0.1–2.0 m) | 같은 파일 |
| 해상도 | **1280 × 720** | `realsense2.urdf.xacro` `<image>` |
| hFOV | **1.2043 rad = 69.00°** | 같은 파일 |
| 갱신율 | color 15 Hz, depth 15 Hz, IR 30 Hz | `<colorUpdateRate>` 등 |
| 장착 | `base_link` 기준 xyz `0.074 0 0.092`, rpy `0 0.261 0` (≈ **15° 하향**) | `bumperbot.urdf.xacro:220-224` |
| **실제 눈높이** | **≈ 0.125 m** — `base_footprint→base_link` = 0.033(휠 반지름) + 0.092 | `bumperbot.urdf.xacro:41` |

> spawn의 `-z 0.15`는 낙하 시작 높이일 뿐이다. 중력으로 안착하면 `base_link`는 0.033 m로
> 내려앉으므로 **로봇 카메라는 h≈0.125 m**다. 우리 코퍼스 프리셋 h0.3/h0.9 어느 쪽과도
> 맞지 않는다 → 이것이 프리셋 정렬을 **월드 내 정지 카메라 모델**로 하기로 한 결정적 이유다(§6).

### 영상 저장 경로
- 저장소에 있는 `bot_camera/bot_camera/dataset.py`는 원저자의 하드코딩 경로
  (`/home/david/nonav_ws/Dataset/...`)를 쓴다 — **쓸 수 없다**.
- `clean_yolo.py`는 화면에 `cv2.imshow`만 하고 파일로 안 남긴다.
- 시스템에 `image_view`(`ros2 run image_view image_saver`)와 `rosbag2`가 설치돼 있어 쓸 수 있으나,
  프레임 개수·파일명·프리셋 매핑을 정확히 통제하려고 **자체 캡처 도구**를 넣었다:
  `tools/grab_frames.py` (cv_bridge·cv2 미사용 → numpy ABI 사고 원천 차단).

## 6. 결론 — "우리 월드 + 저들 로봇/카메라로 RGB를 딸 수 있는가?"

**세 방식 모두 가능. 우리는 (i)을 주 경로로 쓴다.**

| # | 방식 | 장점 | 단점 |
|---|---|---|---|
| **(i)** | **월드 파일에 정지 카메라 모델**을 심는다 | 포즈가 **정확·재현 가능**하고 코퍼스 프리셋(h·d·pitch·hFOV)과 **정확히** 일치. 주행 불필요. 트윈 두 팔에서 카메라가 바이트 동일 | 로봇 카메라가 아니다 |
| (ii) | 로봇을 몰아서(teleop) 찍는다 | 진짜 baseline 시점 | h는 0.125 고정, 포즈 재현 불가, spawn이 (0,0)에 하드코딩 |
| (iii) | `spawn_entity.py`로 카메라 SDF를 런타임 주입 | 임의 포즈 추가 가능 | 매번 명령 필요 |

(i)을 택했고, 그래서 우리 월드에는 카메라 9대가 들어 있다 — 자세한 표는 `worlds/README.md`.
(ii)를 위해 **로봇 스폰 지점을 비워 두었다**: 씬 전체를 +12 m 이동시켜 lip을 `x=12`에 두었으므로
하드코딩된 스폰 `(0, 0, 0.15)`는 **가장 먼 카메라(x=2.0)보다도 2 m 뒤** — 어떤 프레임에도 안 찍힌다.

## 7. 사용 가능한 저들 월드 (참고)

`bumperbot_description/worlds/`: `smallest_world`(기본), `eworld`, `eworld2`, `expandedworld`,
`small_house`, `willowgarage`.
음의 장애물은 `models/large_holed_floor`(STL/DAE 메시로 바닥에 구멍) — **우리가 겨냥하는
계단/단차(drop-off)가 아니라 hole**이다. 우리 코퍼스와 기하 자체가 다른 위험 유형이라
그대로 재사용하지 않고 새 씬을 만들었다.
`eworld`/`eworld2`는 `https://fuel.ignitionrobotics.org/...` URI를 include 한다 → **네트워크 필요**.
우리 월드는 외부 URI가 하나도 없다.

## 8. 리스크

| 리스크 | 영향 | 완화 |
|---|---|---|
| `gazebo_ros_camera`가 `~/image_raw`를 실제로 어떤 leaf 토픽으로 푸는지 플러그인 노드 이름에 달려 있다 | 캡처 스크립트가 토픽을 못 찾음 | 우리가 통제하는 **네임스페이스 `/gzcam/<key>/`로 매칭**하고 leaf는 자동탐색. `--list`로 먼저 확인 |
| 카메라 9대가 계속 렌더링(플러그인이 프레임 커넥션을 잡으므로 `always_on 0`이어도 렌더된다) | GPU 낭비 | `update_rate` **1 Hz**로 고정. 더 줄이려면 `make_worlds.py --cams ...`로 재생성 |
| `gzserver`가 깊이 카메라 렌더 초기화에서 `Assertion px != 0`로 죽은 전력 | 실행 실패 | `setup_env.sh`가 `source /usr/share/gazebo/setup.sh`로 해결 — **반드시 source** |
| headless(`gui:=false`)여도 카메라 센서는 GL 컨텍스트가 필요 | DISPLAY 없으면 실패 | `DISPLAY=:0` 유지 |
| `simulated_robot.launch.py`는 AMCL/map_server를 우리 월드와 무관하게 띄움 | 로그 소음, 라이프사이클 경고 | 캡처엔 (A)/(B) 명령을 쓴다 |
