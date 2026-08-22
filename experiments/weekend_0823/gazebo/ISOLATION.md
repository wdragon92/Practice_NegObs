# STAGE b — 격리 판정 (WEEKEND_BRIEF_0823 §6.7-b)

성립 조건: **`env_isaaclab` 무접촉** (7월 환경 층화 사건 계보).
D31③ 편차에 따라 **아무것도 새로 설치하지 않았다** — 08-19에 이미 구동 검증된
`Baseline_NegObs`의 환경을 그대로 재사용한다.

## 판정: **격리 성립 — env_isaaclab 무접촉. 신규 설치 0건.**

## 근거 (실측)

`bash -lc 'source /home/vislab/Desktop/work_sy/Baseline_NegObs/setup_env.sh'` 직후 상태:

```
CONDA_PREFIX=[<unset>]            CONDA_DEFAULT_ENV=[<unset>]
VIRTUAL_ENV=[/home/vislab/Desktop/work_sy/Baseline_NegObs/neg_env]
PYTHONNOUSERSITE=[1]             ROS_LOCALHOST_ONLY=[1]
which python3 = /home/vislab/Desktop/work_sy/Baseline_NegObs/neg_env/bin/python3
LD_LIBRARY_PATH의 isaac 항목 수 : 0
PYTHONPATH의 miniconda 항목 수  : 0
```

`sys.path` 전량 (miniconda·isaac·`~/.local` 어느 것도 없음):

```
<ws>/install/*/lib(local/lib)/python3.10/{site,dist}-packages   (7개, colcon 오버레이)
/opt/ros/humble/lib/python3.10/site-packages
/opt/ros/humble/local/lib/python3.10/dist-packages
/usr/lib/python310.zip · /usr/lib/python3.10 · /usr/lib/python3.10/lib-dynload
<ws>/neg_env/lib/python3.10/site-packages
/usr/local/lib/python3.10/dist-packages · /usr/lib/python3/dist-packages
```

세 겹으로 분리돼 있다:

1. **conda 미개입** — `~/.condarc`에 `auto_activate: false`. `.bashrc`의 conda 훅은 함수만
   정의하고 base를 켜지 않는다. `setup_env.sh`에는 `conda` 문자열이 없다
   (`grep -niE 'isaac|conda' setup_env.sh build.sh start_baseline.sh` → 0 hit).
   `env_isaaclab`은 `/home/vislab/miniconda3/envs/env_isaaclab`에 있고 위 경로 어디에도 안 나온다.
2. **venv는 시스템 파이썬 기반** — `neg_env/pyvenv.cfg`: `home = /usr/bin`,
   `include-system-site-packages = true`, `version = 3.10.12`. 즉 Ubuntu 22.04 시스템
   python3.10 + ROS Humble dist-packages를 그대로 보고, conda 인터프리터와 무관하다.
3. **`~/.local` 차단** — `PYTHONNOUSERSITE=1`이 `~/.local/lib/python3.10/site-packages`를
   `sys.path`에서 제거한다(위 목록에 없음). `PATH="/usr/bin:$PATH"`가 `~/.local/bin/cmake`(4.3.0)를
   가린다. 둘 다 `setup_env.sh`가 처리.

### 시스템 파이썬 오염 여부
새 설치가 없으므로 **오염 가능성 자체가 없다**. `pip_install.log`(08-19)의 설치 대상은
전부 `neg_env` 안이며 `torch 2.5.1+cu124 / torchvision 0.20.1 / ultralytics 8.0.196 /
numpy 1.24.1`로 고정돼 있다 (torch≥2.6은 `torch.load` 기본값 변경으로 `best.pt` 로드가 깨진다).

## 이번 트랙이 쓰는 셸 프리앰블 — 이걸 그대로 복사해 쓸 것

### (1) 캡처 셸 (ROS 2 + Gazebo). GPU-6 창에서 쓰는 것.

```bash
source /home/vislab/Desktop/work_sy/Baseline_NegObs/setup_env.sh
cd /home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/gazebo
```

`setup_env.sh`가 하는 일(전문):
```bash
export PYTHONNOUSERSITE=1                  # ~/.local 사용자 패키지 오염 차단 (필수)
export PATH="/usr/bin:$PATH"               # ~/.local/bin의 cmake 4.x 회피
export ROS_LOCALHOST_ONLY=1                # 연구실 LAN의 다른 ROS2 PC와 토픽 혼선 차단
source /opt/ros/humble/setup.bash
source /usr/share/gazebo/setup.sh          # 없으면 gzserver가 렌더 초기화 중 죽는다
source <ws>/install/setup.bash
source <ws>/neg_env/bin/activate
```

> `source /usr/share/gazebo/setup.sh`는 **생략 금지**. 없이 띄우면 깊이 카메라 때문에
> gzserver가 `Assertion px != 0`으로 죽는다(RUN_GUIDE.md 기록).
> 환경변수를 바꾼 뒤 토픽이 이상하면 `ros2 daemon stop` 후 재조회(데몬이 옛 환경을 캐싱).

### (2) 추론 셸 (frozen 모델). **캡처 셸과 반드시 다른 터미널.**

```bash
export PYTHONNOUSERSITE=1
conda activate env_seg          # torch 2.5.1+cu124 / smp 0.5.0 — 확인 완료
cd /home/vislab/Desktop/work_sy/Practice_NegObs/experiments/mainrun_0819/code
```

두 셸을 섞지 말 것: `neg_env`(ROS·YOLO)와 `env_seg`(U-Net polar) 둘 다 torch를 갖고 있고
버전은 같지만, ROS 오버레이가 얹힌 `sys.path`에서 `smp`를 불러올 이유가 없다.
프레임 PNG/NPY 파일이 두 셸 사이의 유일한 인터페이스다.

## 남는 공유 자원: GPU 하나

환경은 격리됐지만 **GPU는 공유**다. Gazebo 렌더(카메라 9대 @1 Hz)와 세그 캠페인/훈련이
같은 카드를 쓴다. 캠페인의 `flock` GPU 공유 규약을 그대로 따르고, 캡처는 짧은 홀드로 끝낸다.
더 줄이려면 카메라를 줄여 재생성:

```bash
python3 make_worlds.py --cams h03_d2,h03_d5,h09_d5
```
