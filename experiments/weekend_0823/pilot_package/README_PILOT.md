# README_PILOT.md — 실사진 파일럿 20장 실행·판독 패키지

> **목적(한 줄)**: 파일럿 20장을 **찍고 → 추론하고 → 사전등록 기준에 대입해 판독하고 →
> 본촬영 규모를 추천**하기까지의 전 과정을, 이 문서 하나만 보고 실행할 수 있게 만든다.
>
> **작성**: 2026-08-23 · Claude(CPU-6) · `Docs/experiment/WEEKEND_BRIEF_0823.md` §6.8 지시.
> **독자**: 이 프로젝트를 처음 보는 사람 또는 AI(문서 표준 = WEEKEND_BRIEF §9.2).
> **촬영 자체는 승용 몫이다.** 이 문서는 촬영 전 준비물(명령·체크리스트·판독 틀)만 제공한다.
>
> **짝 문서 2개 — 규약의 정본은 여기가 아니다**
> - 촬영 절차 → `experiments/mainrun_0819/realworld/PROTOCOL_SHOOT.md` (개정 R2, 2026-08-23)
> - 채점 규약·사전등록 판정식 → `experiments/mainrun_0819/realworld/REALWORLD_GRID_PROTOCOL.md`
>
> **스모크 검증 상태**: 아래 §2 명령은 2026-08-23에 **이 저장소에서 실제로 실행해 통과**시켰다
> (CPU, 수 초). 출력 전문은 §2.3에 그대로 붙여 두었다.

---

## 0. 순서 (이 순서를 벗어나지 말 것)

| 단계 | 무엇 | 어디 |
|---|---|---|
| 0 | **사전등록 기준을 읽고 고정 상태로 둔다** (사진 한 장도 추론 전) | §5.1 · GRID_PROTOCOL §9 |
| 1 | 스모크 — 샘플 1장으로 도구가 도는지 확인 | §2 |
| 2 | 촬영 — 캘리브레이션 컷 1장 + 파일럿 20장 | §3 체크리스트 |
| 3 | 배치 추론 — 20장 × 3시드 | §4 |
| 4 | 판독 — AUC 계산 → 사전등록 기준 대입 | §5 |
| 5 | 판독문 작성 + 본촬영 규모 추천 | §6 · §7 |

---

## 1. 환경 · 경로

```bash
# 이 머신의 ~/.local 이 env_seg 를 가리므로 PYTHONNOUSERSITE=1 은 필수다.
unset PYTHONPATH VIRTUAL_ENV
export PYTHONNOUSERSITE=1
cd /home/vislab/Desktop/work_sy/Practice_NegObs
PYBIN=/home/vislab/miniconda3/envs/env_seg/bin/python
CPU="env CUDA_VISIBLE_DEVICES= PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=8 $PYBIN"
```

| 무엇 | 경로 |
|---|---|
| 추론 도구 | `experiments/mainrun_0819/code/infer_photo.py` |
| 정본 그리드 | `experiments/mainrun_0819/code/labeling/gridspec_v1.json` (`--grid gridspec_v1.json`, 20칸) |
| 정본 체크포인트 (V1 본 표) | `experiments/dayrun_0820/runs/v2/rgb_s42/best.pt` · `rgb_s43` · `rgb_s44` |
| 사진 원본 | `experiments/mainrun_0819/realworld/raw/` (손대지 않음) |
| 리네임 사본 | `experiments/mainrun_0819/realworld/frames/` |
| 추론 산출 | `experiments/mainrun_0819/realworld/pilot_out/` (png + json) |
| 기록표 | `experiments/mainrun_0819/realworld/sites.csv` |

**⚠ RGB 전용**: `infer_photo.py`는 `model_factory.build("rgb", ...)`로 3채널 모델을 만든다.
**Depth·B2 체크포인트는 로드되지 않으며**, 실사진에 대응하는 depth를 만들 수단도 없다.
→ **실측 트랙은 RGB 단일 팔 결과**다. 판독문·논문에 이 사실을 명시한다.

---

## 2. 스모크 — 샘플 1장 (촬영 전에 반드시 1회)

### 2.1 목적
도구·체크포인트·그리드가 서로 맞물리는지, 오버레이 PNG가 실제로 그려지는지 확인한다.
**모델 성능을 보는 단계가 아니다.**

### 2.2 명령 (검증됨 — 그대로 복사해 실행)

```bash
OUT=experiments/mainrun_0819/realworld/pilot_out
mkdir -p $OUT
$CPU experiments/mainrun_0819/code/infer_photo.py \
  --image dataset/260819_main_off/val/scene01/L0__s20260819__0000.png \
  --ckpt  experiments/dayrun_0820/runs/v2/rgb_s42/best.pt \
  --grid  gridspec_v1.json \
  --fit   squash \
  --height 1.65 --pitch -8 --hfov 62.2 \
  --out $OUT/smoke.png --json $OUT/smoke.json
```

인자 4개는 **선택이 아니다**(REALWORLD_GRID_PROTOCOL §3.2-(e)):
`--fit squash`(훈련 기하 재현) · `--height`·`--pitch`·`--hfov` 명시.
도구 기본값 `--pitch 0`, EXIF 부재 시 `--hfov 69`는 **코퍼스에 0건인 값**이라 쓰면 안 된다.

### 2.3 통과 판정 — 아래 5줄이 나오면 통과 (2026-08-23 실제 출력)

```
[infer_photo] PROVISIONAL-GRID-V1: 4 bands x 5 sectors = 20 cells · edges [0.0, 2.0, 5.0, 8.0, 12.0] · A1..E3b
[infer_photo] image dataset/260819_main_off/val/scene01/L0__s20260819__0000.png 1920x1080 · fit=squash · hfov=62.20deg (cli) · h=1.65m · pitch=-8.00deg
[infer_photo] ckpt experiments/dayrun_0820/runs/v2/rgb_s42/best.pt (trained n_cells=20, input=rgb)
[infer_photo] top cells: C3b=0.006, B2=0.004, B3b=0.003, D2=0.003, C2=0.002
[infer_photo] fired (p>=0.5): none
[infer_photo] max_prob=0.006475 mean_prob=0.001537 finite=True
```

체크 4개:
- [ ] `4 bands x 5 sectors = 20 cells`, 셀 id가 `A1..E3b` — **15칸 구판이면 즉시 중단**
- [ ] `trained n_cells=20` — 체크포인트와 그리드가 일치
- [ ] `finite=True`
- [ ] `pilot_out/smoke.png`이 생겼고, 열어 보면 **웨지 오버레이 + 확률 격자 2패널**이 보인다

**오버레이에 `15/20 wedges fall inside the frame`이라고 뜨는 것은 정상이다.**
카메라고 1.5–1.8 m·피치 [−15°, −3°]에서는 band 1(0–2 m)이 화면 아래로 빠진다
(band 1이 들어오려면 −18°~−23°가 필요 — 규정·코퍼스 분포 밖). 도구가 덧붙이는
`try --pitch -15` 힌트는 이 조건에서 부정확하다. 상세 = REALWORLD_GRID_PROTOCOL §3.4.

---

## 3. 촬영 체크리스트 (1장 · 인쇄용)

```
─────────────────────────────────────────────────────────────────
 파일럿 촬영 체크리스트 v R2 (2026-08-23)   부지: ______  날짜: ____
─────────────────────────────────────────────────────────────────
[출발 전]
 □ 폰 카메라 = 후면 메인 렌즈 / 가로 / 화면비 16:9 / 최대 해상도(긴 변 ≥1920)
 □ 초광각·망원·디지털줌 OFF · HDR·야간·미화 필터 OFF · AE/AF-Lock 해제(자동 노출 유지)
 □ 수평계 격자 ON (roll |·| ≤ 3°)
 □ 보폭 캘리브레이션: 10 m = ____ 보    □ 레이저 거리계  □ 줄자  □ 기록 노트
 □ 주간 · 한산한 시간대 · 2인 1조

[부지 도착 — 첫 1장]
 □ 캘리브레이션 컷: 광축 방향 지면에 2/5/8/12 m 표식 + 폭 아는 물체 → 1장
    파일명 CALIB__<기기명>__01.jpg          (20장에 포함되지 않음)
 □ 카메라 높이 실측: ______ m   (1.5–1.8 범위인지 확인)

[매 컷 공통]
 □ 피치 −15° ~ −3° (항상 아래로. 위로 향한 컷 금지)
 □ 인물 식별 프레임 금지 · 난간 밖 금지 · 엣지에서 1 m 이격
 □ 촬영 직후 sites.csv 한 행 기록 (거리 측정법 필수 기재)

[파일럿 20장 구성]        ← 5장씩이 아니다. 4장씩이다.
 □ V     4장  내부(계단면)가 보이는 가장 가까운 안전 지점
 □ E     4장  내부는 안 보이고 엣지선(rim)만
 □ H     4장  위험이 픽셀로 전혀 안 보임 + 단서(난간·꺾임·표지)는 프레임 안 · 거리 ≤ 12 m
 □ N-turn 4장 몸만 돌려 위험 없는 방향 (같은 조명·시간대)
 □ N-cue  4장 단서는 있고 0.3 m 낙차는 없는 지점 (난간/점자블록/도색경계/연석 0.10–0.25 m)
 □ 최소 2개 부지 · 하행 계단 부지 반드시 포함

[기록 — sites.csv 한 행]
  site_id, type, dist_m, azimuth(왼쪽 +/오른쪽 −), cam_height_m, gt_cells, tier, notes
  tier ∈ {V, E, H, N-turn, N-cue, none_in_fov}
  gt_cells 예: C2;C3a     (밴드는 dist_m 실측으로 부여 — 사진에서 읽지 않는다)
  dist_m ≥ 12 → tier = none_in_fov      dist_m < 2 → 그런 컷은 만들지 않는다

[파일명]  site_id__tier__idx.jpg   (언더바 2개, idx 두 자리)
  예: SUNKEN01__V__03.jpg / SUNKEN01__H__01.jpg / PLAZA02__N-cue__01.jpg

[철수 전]
 □ 20행 전부 기록됐는지 대조   □ 원본은 케이블/"원본 보내기"로만 이송(EXIF 보존)
 □ raw/ 에 원본 그대로, frames/ 에 리네임 사본
─────────────────────────────────────────────────────────────────
```

---

## 4. 배치 추론 (20장 × 3시드)

`sites.csv`에 적어 둔 부지별 `cam_height_m`·피치를 컷마다 넣는다. 가장 단순한 형태:

```bash
OUT=experiments/mainrun_0819/realworld/pilot_out
FR=experiments/mainrun_0819/realworld/frames
HFOV=62.2          # ← 캘리브레이션 컷으로 적합한 값. EXIF 자동값에 의존하지 말 것
for SEED in s42 s43 s44; do
  mkdir -p $OUT/$SEED
  for f in $FR/*.jpg; do
    b=$(basename "$f" .jpg)
    $CPU experiments/mainrun_0819/code/infer_photo.py \
      --image "$f" --ckpt experiments/dayrun_0820/runs/v2/rgb_$SEED/best.pt \
      --grid gridspec_v1.json --fit squash \
      --height 1.65 --pitch -8 --hfov $HFOV \
      --out "$OUT/$SEED/$b.png" --json "$OUT/$SEED/$b.json"
  done
done
```

- `--height`/`--pitch`는 **컷마다 다르면 컷마다 바꿔 넣는다**(sites.csv 값 사용). 위 루프는
  전 컷 동일 포즈일 때의 최소형이다.
- 20장 × 3시드 = 60회, CPU에서 수 분.
- 산출 json에는 `probs`(20칸) · `cell_ids` · 사용된 포즈·hfov·워터마크가 전부 들어간다.

---

## 5. 판독 절차

### 5.1 사전등록 기준 (결과 보기 전에 이 문단을 읽고 고정한다)

> **프레임 통계량은 그 프레임의 20칸 예측확률 최댓값 `max_cell_prob`이다. 위험군 = V·E·H 컷
> 12장(n₁ = 12), 대조군 = N-turn·N-cue 컷 8장(n₂ = 8)에 대해 Mann–Whitney U 검정을 수행하고
> AUC = U/(n₁·n₂)를 계산한다. AUC ≥ 0.80 이면 "sim→real 전이 신호 있음"으로 판정하고 본촬영을
> 진행한다. 0.60 ≤ AUC < 0.80 이면 보류·재설계, AUC < 0.60 이면 중단·보고한다. 이 문턱은
> 파일럿 결과를 보기 전에 고정되었으며, 결과를 본 뒤에는 변경하지 않는다.**

- 1차 판정 = **3시드 AUC의 중앙값** 하나. 다중 판정·사후 문턱 변경 금지.
- **N-cue 단독 AUC**(n₁=12, n₂=4)와 **N-turn 단독 AUC**는 별도 보고하되 **게이트가 아니다**.
- 사전 선언된 해석: **N-turn AUC는 높은데 N-cue AUC가 0.5 근처면, 실세계에서도 "단서 지름길"이
  살아 있다는 증거**다(sim sceneC2 신off FA .681과 나란히 놓는다).
- 부속 규정 전문(동점 처리·결측 제외·τ 고정) = REALWORLD_GRID_PROTOCOL §9.

### 5.2 계산 (검증된 스니펫 — `pilot_out/<seed>/`에서 실행)

```bash
cd experiments/mainrun_0819/realworld/pilot_out/s42
$CPU - <<'PY'
import glob, json, os
HAZ = ("V", "E", "H")
rows = []
for p in sorted(glob.glob("*.json")):
    tier = os.path.basename(p).split("__")[1]          # site__tier__idx.json
    rows.append((tier, max(json.load(open(p))["probs"])))
def auc(pos, neg):
    if not pos or not neg: return None, len(pos), len(neg)
    U = sum((a > b) + 0.5 * (a == b) for a in pos for b in neg)
    return U / (len(pos) * len(neg)), len(pos), len(neg)
haz = [m for t, m in rows if t in HAZ]
for label, ctl in (("ALL (N-turn+N-cue)", [m for t, m in rows if t.startswith("N")]),
                   ("N-turn only       ", [m for t, m in rows if t == "N-turn"]),
                   ("N-cue  only       ", [m for t, m in rows if t == "N-cue"])):
    a, n1, n2 = auc(haz, ctl)
    print(f"{label}  n1={n1} n2={n2}  AUC={a:.3f}" if a is not None else f"{label}  (empty)")
for t in ("V", "E", "H", "N-turn", "N-cue"):
    v = [m for tt, m in rows if tt == t]
    if v:
        print(f"  {t:<7} n={len(v)} max-prob mean={sum(v)/len(v):.3f} min={min(v):.3f} max={max(v):.3f}")
PY
```

출력 형태(더미 데이터로 동작 검증 완료):
```
ALL (N-turn+N-cue)  n1=12 n2=8  AUC=0.958
N-turn only         n1=12 n2=4  AUC=1.000
N-cue  only         n1=12 n2=4  AUC=0.917
  V       n=4 max-prob mean=... min=... max=...
```

**대응하는 U 문턱**: n₁=12·n₂=8 → U_max = 96, **AUC ≥ 0.80 ⟺ U ≥ 76.8**.
완전분리 시 단측 p = 1/C(20,8) = **7.9 × 10⁻⁶** — n=12/8로도 충분히 판정된다.

### 5.3 판정 대입표 (빈칸을 채운다)

| 시드 | 통합 AUC (n₁=12,n₂=8) | N-turn AUC | N-cue AUC | 위험군 max-prob 중앙값 | 대조군 max-prob 중앙값 |
|---|---|---|---|---|---|
| rgb_s42 | | | | | |
| rgb_s43 | | | | | |
| rgb_s44 | | | | | |
| **중앙값** | **← 1차 판정값** | | | | |

| 중앙 AUC | 판정 | 다음 행동 |
|---|---|---|
| ≥ 0.80 | **전이 신호 있음** | 본촬영 진행 (§7 규모 추천) |
| 0.60 – 0.80 | **보류** | 재설계 — 포즈·부지·대조컷 구성 점검 후 파일럿 재실시 |
| < 0.60 | **중단** | 보고. 사진을 더 찍어 해결되는 문제가 아님(모델/도메인 문제) |

---

## 6. 판독문 초안 틀 (파일럿 후 그대로 채워 쓴다)

> 저장 위치 제안: `experiments/mainrun_0819/realworld/PILOT_READOUT.md`

```markdown
# PILOT_READOUT — 실사진 파일럿 20장 판독 (YYYY-MM-DD)

## 1. 무엇을 했나
- 촬영: __개 부지 / __장 (V _ · E _ · H _ · N-turn _ · N-cue _), 캘리브레이션 컷 _장
- 촬영 규격 준수: 16:9 __ · 피치 범위 __ · 카메라고 __ m · roll __
- 규격 위반으로 판정 전 제외한 컷: __장 (사유: ____)
- 추론: rgb_s42/43/44 × 20장, `--fit squash --height _ --pitch _ --hfov _`
- 산출 경로: `experiments/mainrun_0819/realworld/pilot_out/`

## 2. 사전등록 기준 (결과 보기 전 고정 — REALWORLD_GRID_PROTOCOL §9)
> AUC(위험 12장 vs 대조 8장, max_cell_prob) ≥ 0.80 → 진행 / 0.60–0.80 → 보류 / < 0.60 → 중단

## 3. 결과
| 시드 | 통합 AUC | N-turn AUC | N-cue AUC |
|---|---|---|---|
| s42 | | | |
| s43 | | | |
| s44 | | | |
| 중앙값 | | | |

티어별 max-prob (평균 / 최소 / 최대): V _ · E _ · H _ · N-turn _ · N-cue _

## 4. 판정
**중앙 AUC = ____ → [진행 / 보류 / 중단]**

## 5. 부지표 읽기 (지름길 여부)
- N-turn AUC ____ vs N-cue AUC ____ .
- (사전 선언) N-cue AUC가 0.5 근처면 실세계에서도 단서 지름길 — sim sceneC2 신off FA .681과 병기.
- 해석: ____

## 6. 보조 관찰 (판정 아님)
- V 프레임 정답 칸 부근(섹터 strict·밴드 ±1) 반응: __/4
- 반응 세기 V ≥ E ≥ H 경향: [예 / 아니오] (H가 0이어도 실패 아님)
- 관측 격자: 20칸 중 15칸만 프레임 안(band 1 구조적 제외, GRID_PROTOCOL §3.4)

## 7. 캐비앗 (반드시 적는다)
- RGB 단일 팔. depth·b2는 실사진 평가 불가.
- n = 20. 정성 증거이며 논문 헤드라인 표에 들어가지 않는다.
- GT 주석은 __인 블라인드 코딩, Cohen's κ = ____ (κ<0.6이면 규칙 재정의 후 재실시).
- recall류를 적었다면 분모와 none_in_fov 장수를 같은 줄에 병기했는가: [예/아니오]

## 8. 다음 행동
- ____
```

---

## 7. 본촬영 규모 추천안 틀 (파일럿 판정이 "진행"일 때만 채운다)

> 승용 결재 #6은 **본촬영 규모 미확정 유지**이며, 파일럿 판독문에 규모 추천안을 첨부하는 것이
> 조건이다(WEEKEND_BRIEF §4.1-6). 아래 틀을 **파일럿 수치로** 채워 제출한다.

```markdown
## 본촬영 규모 추천안 (파일럿 결과 기입 후 작성)

### 입력 (파일럿에서 관측된 값)
- 티어당 max-prob 산포: V ±__ · E ±__ · H ±__ · N-turn ±__ · N-cue ±__
- 1부지 소요시간(이동 포함): __분 → 반나절(4 h)에 __부지 / __장
- 규격 위반 재촬영률: __%
- 부지 확보 난이도: N-cue 지점이 있는 부지 비율 __%

### 추천 (셋 중 하나를 고르고 근거를 적는다)
| 안 | 규모 | 언제 고르나 |
|---|---|---|
| 소 | __부지 / __장 (티어당 __) | 파일럿 AUC가 문턱을 크게 넘고(≥0.90) 산포가 작을 때 |
| 중 | __부지 / __장 | 기본 권고 |
| 대 | __부지 / __장 | H·N-cue 산포가 커서 층별 n이 더 필요할 때 |

### 배분 원칙 (파일럿과 동일하게 유지)
- 티어 균등(V:E:H:N-turn:N-cue = 1:1:1:1:1)을 유지한다 — 판정식이 균등 n을 전제한다.
- 하행 계단이 부지의 절반 이상. 그 외 유형은 전부 `탐색` 라벨.
- 부지 수 ≥ __ (한 부지가 결과를 떠받치지 않도록. sim에서 H 인과 증거가 씬 1개에
  의존했던 사고 — R2 §4.3-F1 — 의 실측판 재발 방지).

### 필요 자원
- 촬영 __인 × __일 · 주석 2인 블라인드 __시간 · 추론 CPU __분

### 추천 근거 3줄
1. ____
2. ____
3. ____
```

---

## 8. 트러블슈팅

| 증상 | 원인 · 조치 |
|---|---|
| `checkpoint ... was trained on 20 cells but --grid says 15` | `--grid gridspec_v1.json`을 빠뜨렸다. 기본값은 V0 15칸이다 |
| `--hfov ... is not a plausible horizontal FOV` | 숫자 또는 `auto`만 받는다. 캘리브레이션 값을 넣을 것 |
| `hfov=69.0deg (default,no EXIF)` 가 찍힘 | EXIF가 지워진 사진(메신저 경유). **그 컷은 쓰지 않는다** — 원본 재이송 |
| 오버레이 웨지가 화면 밖으로 나감 | 피치·카메라고를 실제 값으로 넣었는지 확인. `15/20`은 정상(§2.3) |
| `ModuleNotFoundError` / 버전 충돌 | `PYTHONNOUSERSITE=1` 누락. §1 프리앰블을 그대로 쓸 것 |
| 확률이 전부 0.5 근처로 뭉갬 | `--fit letterbox`(기본값)로 돌렸을 가능성. **반드시 `--fit squash`** |

---

## 9. 다음 행동

1. **`sites.csv` 헤더·허용값 갱신** (촬영 직전 1회): `tier`에 `N-turn`/`N-cue`/`none_in_fov` 추가,
   `azimuth` 부호를 **왼쪽 +**로 정정, 열 추가 `dist_method`·`aspect`·`pitch_deg`·`calib_shot`,
   `EX_` 예시 행 삭제. **2026-08-23 현재 미수정.**
2. **파일럿 촬영** — 승용 몫. §3 체크리스트 인쇄.
3. **판독** — §5 → §6 판독문 → §7 규모 추천안.
4. **결재 상신** — 판독문과 규모 추천안을 `MORNING_REPORT_0823.md` 결재란에 첨부
   (형식: 이렇게 해뒀다 → 근거(경로) → Claude 예비 판정·권고 → 무응답 시 기본값).
