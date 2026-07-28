# 하늘(HDRI) 조달 v1 — 구름 하늘 3종 + lookfix 파생 검증

- 작업일 2026-07-28 · 담당 "하늘 조달" · 지시 범위: **조달 + 파생 검증까지**
  (조명 분포 정책 = 시각·계절 랜덤화, 씬별 하늘 배정은 **다음 지시서** 소관 — 손대지 않았다)
- 산출물: `assets/download_sky.py`, `assets/{3종}_4k.exr`, `assets/{3종}_4k_lookfix.exr`,
  본 보고서, `Docs/CREDITS.md`(§하늘 HDRI 절만 추가)
- 배경: `Docs/reports/realism_phase1.md` §4.1·§5 — 현 HDRI `qwantani_noon_**puresky**` 는 무운(無雲)
- GPU 미사용(Isaac Sim 미실행). 전 측정 numpy/cv2 + `scripts/imgstats.py` 함수.

---

## 0. 결론 3줄

1. **PolyHaven CC0 구름 하늘 3종을 받았고 파생본까지 만들었다.** 태양 방위는 셋 다
   qwantani 와 ±2° 안이라 `hdri_sun_rotz_offset` 은 **232.8~235.8** — 현행 233.5에서 거의 안 움직인다.
2. **`ensure_noon_lookfix` 는 신규 3종 전부에서 즉시 실패한다.** 구름 때문이 아니라
   **4채널(RGBA) EXR** 이라서다. 예외를 삼키고 원본을 반환하므로 **경고 한 줄만 남기고 조용히
   무보정 하늘이 렌더된다**(돔 태양 + DistantLight 이중 태양). 한 줄 패치로 해결 — §3.1.
3. **감독 진단의 "죽은 픽셀의 67~74%가 하늘"은 과대평가다.** 하늘을 실제로 분할해 재보면
   전체 죽은 픽셀 중 하늘은 **13~39%**다("상단 1/3"의 대부분은 하늘이 아니라 벽·건물이다).
   하늘 교체의 실제 기대효과는 §5 — **전체 flat% 13.4→8.9, 상단1/3 26.9→13.5**(scene01, 최선 케이스).

---

## 1. 선정 — PolyHaven "pure skies" 3종

### 1.1 후보 선별 절차

PolyHaven API(`https://api.polyhaven.com/assets?type=hdris`, 980건)에서
`categories ⊇ {pure skies}` 59건을 뽑고 `partly cloudy` + (`midday` | `morning-afternoon`)
으로 좁힌 뒤, **1k EXR 을 실제로 내려받아 태양 고도·방위·구름 통계를 실측**해 골랐다.
`pure skies` 만 본 이유는 지시 조건("지평선에 지상 구조물이 과하게 찍힌 것 회피") 때문이다 —
PolyHaven 의 puresky 판은 지평선 아래를 하늘의 미러 그라디언트로 대체해 지물이 0이다.
같은 촬영의 비-puresky 판(`kloofendal_48d_partly_cloudy` 등)은 잔디·바위 지면이 그대로 찍혀 탈락.

### 1.2 선정 결과

| # | slug (에셋 페이지) | 파일 (assets/) | 구름 유형 | 태양 고도 | 태양 방위 φ | 4k 크기 |
|---|---|---|---|---|---|---|
| S1 | [`kloofendal_48d_partly_cloudy_puresky`](https://polyhaven.com/a/kloofendal_48d_partly_cloudy_puresky) | `kloofendal_48d_partly_cloudy_puresky_4k.exr` | **산개 적운** (청천 틈 넓음, 고대비) | **47.86°** | 214.23° | 75,640,460 B |
| S2 | [`sunflowers_puresky`](https://polyhaven.com/a/sunflowers_puresky) | `sunflowers_puresky_4k.exr` | **층적운 밴드 + 상층 권층운** (수평선까지 구름이 깔림) | **43.02°** | 216.17° | 75,188,263 B |
| S3 | [`farm_field_puresky`](https://polyhaven.com/a/farm_field_puresky) | `farm_field_puresky_4k.exr` | **부분 흐림** (층적운이 태양을 완전 차폐, 저대비) | 49.53° *(불안정 — §3.2)* | 217.22° | 73,725,736 B |

실제 파일 URL (스크립트가 API 에서 받아 사용한 것과 동일):

```
https://dl.polyhaven.org/file/ph-assets/HDRIs/exr/4k/kloofendal_48d_partly_cloudy_puresky_4k.exr
https://dl.polyhaven.org/file/ph-assets/HDRIs/exr/4k/sunflowers_puresky_4k.exr
https://dl.polyhaven.org/file/ph-assets/HDRIs/exr/4k/farm_field_puresky_4k.exr
```

EXR 헤더 직접 파싱 검증(다운로더 내장): 셋 다 `4096x2048 · v2 · ch=[A,B,G,R] · float · PIZ`.
크기는 API 보고값과 바이트 단위 일치.

기존 자산(`qwantani_noon_puresky_4k.exr`, `kloofendal_overcast_4k.exr`)과 중복 없음.
고도 49.79°(씬 기본값) 대비 편차 **−1.9° / −6.8° / −0.3°** 로 셋 다 정오대에 든다.

### 1.3 라이선스 (실제 페이지 확인)

`https://polyhaven.com/license` 원문(2026-07-28 취득):

> All assets (HDRIs, textures and 3D models) on this site are the original work of Poly Haven
> staff, or artists who willingly and directly donate/sell their work to Poly Haven.
> **Our assets are all licensed as CC0** … In other words: **You can use our assets for any
> purpose, including commercial work.** You do not need to give credit or attribution when
> using them (although it is appreciated). **You can redistribute them** …

AI 학습 용도가 라이선스 페이지에 명시적으로 언급된다:

> we've heard from numerous data scientists, software developers, automotive engineers and
> **AI researchers all using our assets in their work**, which simply wouldn't be possible with
> more restrictive (even open source) licenses.

→ `Docs/briefs/realism_brief_v1.md` 원칙 2(CC0/MIT-0/CC-BY만) 충족. 크레딧은 의무가 아니지만
`Docs/CREDITS.md` 에 기록했다.

### 1.4 탈락시킨 후보와 이유 (1k 실측 근거)

| 후보 | 고도 | 탈락 사유 |
|---|---|---|
| `kloofendal_38d_partly_cloudy_puresky` | 37.8° | 고도 편차 −12°. 엷은 고적운 시트는 매력적이나 수평선대 구름이 없어 flat% 이득 낮음(§4 표 94.2) |
| `kloppenheim_03_puresky` | 58.5° | 고도 편차 +8.7°. **1순위 예비** — flat% 84.4로 farm_field보다는 낫다 |
| `aristea_wreck_puresky` | 47.3° | 태양이 두꺼운 고층운에 완전히 묻힘(peak/cap 2.2) + 수평선대 무구조(98.6) |
| `kloofendal_28d_misty_puresky` | 28.7° | 사실상 안개 — 전 방위 무구조. puresky 만큼 평탄 |
| `kloppenheim_05_puresky` / `rustig_koppie_puresky` / `kloofendal_43d_clear_puresky` | 74.4/28.3/43.1 | 거의 청천(구름 없음) — 목적 불합 |

---

## 2. 다운로드 스크립트 `assets/download_sky.py`

기존 `assets/download_assets.py` 규약을 그대로 따랐다: PolyHaven API → `hdri/4k/exr` URL,
브라우저/curl UA(기본 python-urllib 은 403), 3회 재시도, `.part` 임시파일 후 `os.replace`,
**이미 있고 API 보고 크기와 일치하면 skip**(재실행 안전), 실패 목록 출력 후 `sys.exit(1)`.

추가한 것 2개:
- `verify_exr()` — 외부 의존성 없이 EXR 헤더(매직 `0x01312f76`)를 직접 파싱해 해상도·채널·
  픽셀형·압축을 출력. 다운로드 파손을 크기 검사만으로 못 잡는 경우를 막는다.
- `measure_sun()` — cv2 가 있으면 태양 픽셀을 찾아 `noon_sun_elev` 와
  `hdri_sun_rotz_offset` 을 바로 출력(없으면 조용히 생략, 다운로드는 성공 처리).

실행 결과(실제 수행):

```
[hdri] kloofendal_48d_partly_cloudy_puresky
  [ ok ] kloofendal_48d_partly_cloudy_puresky_4k.exr (75,640,460 bytes)
  [exr ] 4096x2048 v2 ch=['A','B','G','R'] (float) comp=PIZ
  [sun ] elev=47.86° phi=214.23° → noon_sun_elev=47.86, hdri_sun_rotz_offset=235.77
... (3/3, 224.6 MB)
```

---

## 3. lookfix 파생 검증 — **핵심**

### 3.1 [치명] 4채널 EXR 에서 `ensure_noon_lookfix` 가 통째로 실패한다

신규 3종에 `sc.ensure_noon_lookfix()` 를 직접 호출한 결과 **3/3 전부 실패**:

```
[HDRI][경고] lookfix 생성 실패(operands could not be broadcast together with
             shapes (2048,4096,4) (1,4096,3) ) — 원본 사용
```

원인은 구름이 아니라 채널 수다.

- 현행 코드: `rgb = cv2.imread(src, IMREAD_UNCHANGED)[..., ::-1]`
- PolyHaven 신규 HDRI 는 **RGBA 4채널**(A는 상수 1.0). OpenCV 는 BGRA 로 읽으므로
  `[..., ::-1]` 은 RGB 가 아니라 **`[A,R,G,B]`** 를 만든다.
  → ① 휘도가 `0.2126·A + 0.7152·R + 0.0722·G` 라는 엉터리 식이 되고
  → ② 지평 리프트의 `ref` 를 `range(3)` 로 만들다가 (h,w,4) vs (1,w,3) 브로드캐스트 예외.
- 예외는 `except Exception` 이 삼키고 **원본 경로를 반환**한다. 즉 씬은 죽지 않고
  **경고 한 줄만 남긴 채 무보정 HDRI 로 렌더된다** — HDRI 태양 디스크(초연질 그림자)와
  명시 DistantLight(경질 그림자)가 **동시에** 살아 이중 태양·이중 그림자가 된다.
- 기존 `qwantani_noon_puresky_4k.exr` 은 3채널이라 지금까지 드러나지 않았다.
  `kloofendal_overcast_4k.exr` 은 이미 4채널이지만 씬이 `lookfix=False` 라 우회돼 있었다.

**처방 (1줄, `scene_common.ensure_noon_lookfix` 안의 `cv2.imread` 행 — 2026-07-28 17:20 기준 1603행.
동시 편집으로 행번호가 움직이므로 함수명으로 찾을 것)**

```python
# 현행
rgb = cv2.imread(src_path, cv2.IMREAD_UNCHANGED)[..., ::-1]
# 처방 — 알파를 먼저 버린다
rgb = cv2.imread(src_path, cv2.IMREAD_UNCHANGED)[..., :3][..., ::-1]
```

부수 처방(권고): `except` 절에서 원본을 반환할 때 `print` 대신 **예외를 올리거나 최소한
`[HDRI][치명]` 표기**로 승격할 것. 지금은 조용한 실패가 판정 라운드 전체를 오염시킬 수 있다.

**현재 상태**: 나는 위 1줄만 고친 동일 알고리즘으로 파생본 3개를 이미 생성해
`assets/*_lookfix.exr` 에 두었다. `ensure_noon_lookfix` 는 캐시(`mtime(out) >= mtime(src)`)를
먼저 보므로 **패치 없이도 지금은 정상 동작한다.** 다만 HDRI 를 재다운로드하거나 파일을
`touch` 하는 순간 다시 깨지므로 패치는 반드시 필요하다.

파생본 검증: `4096x2048 · half · ZIP · ch=[B,G,R]`, 전 픽셀 유한, 값역
`0.042~97.1 / 0.043~40.2 / 0.103~31.2` (half 상한 65504 초과 없음). 각 16~18 MB.

### 3.2 태양 오검출 — 3종 중 1종에서 실제로 발생

지시된 최대 리스크("밝은 구름 가장자리를 태양으로 오인")를 각반경 프로파일로 판별했다.
판별 지표: **peak/cap**(최대휘도 ÷ 서컴솔라 링 p90), **sunE**(2.5° 안에 든 반구 에너지 비율),
**sep**(argmax 와 상위 0.01% 픽셀의 입체각 가중 중심 사이 각거리), **링 프로파일 단조성**.

| HDRI | peak/cap | sunE(<2.5°) | sep | 링 프로파일(0-0.27 / 0.27-0.5 / 0.5-1 / 1-1.5 / 1.5-2.5) | 판정 |
|---|---|---|---|---|---|
| qwantani(기준) | 19039 | 80.0% | 0.043° | 94692 / 3385 / 58.5 / 11.7 / 4.0 | 정상 |
| **S1** kloofendal_48d | 1473 | 51.5% | 0.024° | 53638 / 3679 / 120 / 31.4 / 19.5 | **정상** |
| **S2** sunflowers | 12507 | 47.7% | 0.012° | 55505 / 2853 / 40.5 / 9.2 / 4.3 | **정상** |
| **S3** farm_field | **3.2** | **0.3%** | **1.647°** | **16.0 / 2.4 / 3.3 / 5.6 / 5.7 (바깥이 더 밝다)** | **오검출** |

- **S1·S2 는 오검출 없음.** 최대휘도 픽셀이 실제 태양 중심이고(sep < 0.03°), 링 프로파일이
  4자릿수에 걸쳐 단조 감소한다. 구름이 있어도 태양이 뚫고 나오면 알고리즘은 성립한다.
- **S3(farm_field)는 오검출이다.** 태양이 층적운에 완전히 가려 직달이 거의 없고
  (sunE 0.3%, 전 이미지 최대값이 겨우 58.1), argmax 는 구름 가장자리의 고립된 밝은 티끌이다.
  근거 3가지: ① peak/cap 3.2 ② 링 프로파일이 **바깥으로 갈수록 밝아짐**(안쪽 2.4 < 바깥 5.7)
  ③ **동일 HDRI 의 1k 판과 4k 판에서 검출 위치가 1.6° 어긋난다**(1k: elev 51.15/az 216.74,
  4k: elev 49.53/az 217.22) — 안정된 태양이라면 있을 수 없는 흔들림이다.
  다행히 파괴적이진 않다(캡된 화소 142개, 제거 직달에너지 0.00). 그러나 이 방향으로
  DistantLight 를 정합시키면 **하늘에 없는 태양의 경질 그림자**가 생긴다.

**처방**

1. **태양 검출을 argmax 단독에서 "상위 0.01% 입체각 가중 중심"으로 바꿀 것.**
   S1·S2 에서는 결과가 사실상 동일하고(sep < 0.03°), S3 같은 티끌 오검출에 강하다.
2. **수용 판정(gate)을 넣을 것.** `peak/cap ≥ 50` **그리고** `sunE(<2.5°) ≥ 5%` 를 통과하지
   못하면 **캡을 생략하고 `noon_sun_enable=False` 를 강제**한다(= overcast 프로파일).
   실측상 정상 3종은 1473~19039, 오검출 1종은 3.2 라 경계가 3자릿수 여유로 갈린다.
3. **S3 는 지금 당장은 `lookfix=False` + `noon_sun_enable=False` 로 쓰라.** §6 스니펫 참조.
   (`sceneC1`/`sceneC4` 의 overcast 프로파일과 동일한 취급이되, 하늘은 훨씬 구조가 있다.)

### 3.3 캡 처리의 부작용 — **구름 하늘에서 "잘린 원반"이 보인다**

현행은 각반경 **1.5°** 안을 링(1.5~2.5°) p90 한 값으로 클램프한다. 태양 각반경이 0.27°인데
1.5°는 **디스크의 30배 면적**이라, 태양 주변 후광(aureole)의 자연 그라디언트까지 통째로
평탄화한다. 청천 hazy 하늘(qwantani)에서는 후광이 넓어 티가 덜 났지만, **후광이 좁은
구름 하늘에서는 지름 3°의 균일 원반 + 뚜렷한 테두리로 눈에 보인다.**

육안 확인(태양 중심 ±6° 크롭, 톤매핑 동일): S2(sunflowers)에서 가장 뚜렷 —
원본의 부드러운 광휘가 lookfix 후 **경계가 잡히는 납작한 원반**이 된다. S1도 넓게 뭉갠다.

**처방 — 캡 반경 1.5°→0.6°, 링 1.5~2.5°→0.6~1.0°.** 근거는 제거되는 직달에너지가
사실상 동일하다는 실측이다(태양 에너지의 88%가 0.27° 안, 99%가 0.5° 안):

| HDRI | 현행 1.5°/ring1.5-2.5 | 처방 0.6°/ring0.6-1.0 | 제거 직달E 보존율 |
|---|---|---|---|
| qwantani | cap 7.24, 1175 px, E=5.633 | cap 74.0, 227 px, E=5.594 | **99.3%** |
| S1 kloofendal_48d | cap 50.8, 679 px, E=3.215 | cap 169.0, 217 px, E=3.161 | **98.3%** |
| S2 sunflowers | cap 5.78, 1255 px, E=2.888 | cap 54.6, 199 px, E=2.863 | **99.1%** |

즉 **DistantLight 세기 재튜닝 없이** 원반 아티팩트만 없앨 수 있고, qwantani 기존 씬에
전역 적용해도 직달 제거량 변화가 0.7%라 회귀 위험이 거의 없다.
(육안으로는 처방판이 태양 광휘의 그라디언트를 유지해 원본에 훨씬 가깝다.)

### 3.4 지평 리프트 — 구름 하늘에서 색이 튀지 않는다

`elev −24°→−18°` 램프, `−18°~0°` 전면 적용, 인접 하늘(0.5~3.5°) 방위 11° 평활 기준으로
`max()` 리프트. puresky 계열은 지평선 아래가 이미 하늘의 미러라 리프트 폭이 작다.

| HDRI | 대역 Δ최대(선형) | Δ평균 | 상대변화 p99 | R/B 비 (원본→파생) |
|---|---|---|---|---|
| qwantani | 0.456 | 0.109 | 347% | 0.505 → 0.787 (**청→중성, 기존 동작**) |
| S1 kloofendal_48d | 0.515 | 0.102 | 209% | 0.697 → 0.764 |
| S2 sunflowers | 0.382 | 0.071 | 148% | 0.943 → 0.913 |
| S3 farm_field | 1.117 | 0.119 | 108% | 0.869 → 0.902 |

**색 튐 없음.** 신규 3종의 R/B 변화는 ±0.07 이내로, 오히려 기존 qwantani(+0.28)보다 훨씬
얌전하다. 원본 지평 아래의 세로 스트리크(미러 아티팩트)가 일부 씻기는 정도이고, 우리 씬은
지면 지오메트리가 이 대역을 대부분 가린다. **조치 불필요.**

경미한 지적 2건(수정 권고 아님, 기록만): ① `t` 램프가 `elev = 0` 에서 1→0 으로 계단
불연속이다(리프트 폭이 작아 실무상 무해). ② docstring 은 "−18°~0°"인데 실제 램프 시작은
−24°다.

### 3.5 파생 전/후 flat% — **lookfix 는 flat% 중립이다**

측정법: EXR 을 **Reinhard `x/(1+x)` + 감마 2.2** 로 8bit 변환(노출 k=1.9951 — §5.1 에서
실제 렌더의 하늘 중앙값 0.590 에 맞춰 보정한 값), `scripts/imgstats.py` 의 `load` 규약대로
긴 변 1024 로 리사이즈한 뒤 같은 `local_std(k=5) < 1/255` 로 계산.

정방위 등장방형(equirect) 기준. "상단 1/3" = 이미지 상단 1/3 = **천정~고도 30°** 대역이다.

| 파일 | 상단1/3 (elev 30~90°) | 수평선 위 전체 | 고도 0~8° 대역 |
|---|---|---|---|
| qwantani_noon_puresky_4k | 95.86 | 87.59 | 62.33 |
| qwantani … _lookfix | 95.86 | 87.59 | 62.19 |
| **kloofendal_48d** 원본 | **37.47** | **36.59** | **23.56** |
| kloofendal_48d _lookfix | 37.48 | 36.51 | 22.41 |
| **sunflowers** 원본 | **47.37** | **35.19** | **3.34** |
| sunflowers _lookfix | 47.37 | 35.17 | 3.21 |
| **farm_field** 원본 | **53.70** | **52.38** | **71.86** |
| farm_field _lookfix | 53.69 | 52.35 | 71.77 |

**파생 전후 차이는 전부 |Δ| ≤ 1.2 pp**(대부분 0.01 pp). lookfix 는 태양 디스크 1000여 화소와
지평선 아래만 건드리므로 flat% 를 사실상 바꾸지 않는다. **flat% 개선은 전적으로 HDRI 교체
자체의 효과다.** 반대로 말하면 lookfix 를 손본다고 flat% 가 좋아지지 않는다.

---

## 4. 실제로 중요한 발견 — 우리 뷰가 보는 하늘은 **고도 0~8° 띠**뿐이다

씬 카메라는 Isaac 기본 퍼스펙티브(focal 18.147 / aperture 20.955 → **수평화각 60°**),
1920×1080, `grid_views` 프리셋 **pitch −10°**다. 수직화각 36° 이므로 화면 상단 모서리가
**고도 +8°**, 화면 중앙이 −10°다. 즉 **로봇 시점 컷에 들어오는 하늘은 지평선 바로 위 8° 띠**이고,
천정 부근의 멋진 적운은 **한 픽셀도 안 들어온다.**

그래서 HDRI 를 "천정 구름이 예쁜가"로 고르면 안 되고 **"수평선대에 구름이 있는가"로 골라야
한다.** 실제 카메라 기하를 재현한 시뮬레이션 뷰(HDRI→퍼스펙티브 리샘플, 돔 회전 61.5 =
`noon_dome_rot −110 + SUN_AZ_OFFSET 171.5`, 6방위 평균)로 측정한 하늘 영역 flat%:

| HDRI | pitch −10° (로봇 시점) | 참고: pitch +5° |
|---|---|---|
| qwantani_noon_puresky (현행) | **99.8** | 99.9 |
| kloofendal_overcast (기존 C1/C4용) | 97.6 | 99.0 |
| aristea_wreck_puresky | 98.6 | 93.8 |
| **S3 farm_field_puresky** | **97.2** | 91.3 |
| kloofendal_38d_partly_cloudy_puresky | 94.2 | 74.1 |
| kloppenheim_03_puresky | 84.4 | 82.9 |
| **S1 kloofendal_48d_partly_cloudy_puresky** | **73.6** | 72.2 |
| **S2 sunflowers_puresky** | **30.2** | 49.8 |

노출을 HDRI 별로 정합(= `dome_intensity` 를 맞춘 상태)하고 RTX 실제 톤매퍼에 맞춰
ACES(op=6 기본 활성)로 바꿔 재측정하면:

| HDRI | Reinhard(노출정합) | **ACES(노출정합)** |
|---|---|---|
| qwantani _lookfix | 99.77 | **99.35** |
| S1 kloofendal_48d _lookfix | 69.27 | **55.54** |
| S2 sunflowers _lookfix | 26.91 | **16.66** |
| S3 farm_field _lookfix | 93.78 | **90.05** |
| kloofendal_overcast | 96.51 | 92.37 |

**서열: S2 ≫ S1 ≫ S3 ≈ 현행.** S2 가 압도적인 이유는 구름 밴드가 수평선까지 내려와 있기
때문이고, S3 가 거의 이득이 없는 이유는 부분 흐림의 수평선대가 균일한 회백색이기 때문이다.
**S3 는 flat% 가 아니라 조명 질(완전 확산광) 다양성을 위해 남긴 것**임을 분명히 해 둔다.
flat% 를 3종 모두에서 얻고 싶다면 S3 대신 `kloppenheim_03_puresky`(84.4, 고도 58.5°)로
교체하는 선택지가 있다 — 다만 고도 편차가 +8.7°로 커진다.

---

## 5. 예상 효과 — 씬 적용 시 flat% 는 어디까지 내려가나

### 5.1 먼저, 감독 진단의 정정: "상단 1/3"은 하늘이 아니다

`realism_phase1.md` §5 표는 상단 1/3 을 "하늘"로 부르지만, 실제 컷에서 상단 1/3은 대부분
**건물 벽·옹벽**이다. 렌더에서 하늘 화소를 실제로 분할(연결성분 + 저국소분산 + B≥R)해
재측정했다 — 각 씬의 `flat_상1/3` 은 감독 보고치와 정확히 일치하므로 분할만 추가된 것이다.

| 씬 (렌더셋) | 하늘 비율(상1/3) | 하늘 비율(전체) | flat\|하늘 | flat\|비하늘(상1/3) | flat\_상1/3 | flat\|비하늘(전체) | flat\_전체 |
|---|---|---|---|---|---|---|---|
| scene01 (`v7_pt`) | 16.9% | 5.7% | 92.6 | 12.8 | **26.9** | 8.4 | **13.4** |
| scene07 (`v8_pt`) | 9.5% | 4.1% | 89.1 | 55.5 | **61.0** | 24.0 | **27.4** |
| sceneD3 (`p0_base_pt`) | 29.4% | 9.8% | 97.5 | 18.9 | **42.4** | 27.2 | **34.1** |

→ **전체 죽은 픽셀 중 하늘이 차지하는 몫은 scene01 39% · scene07 13% · sceneD3 28%**
(감독 추정 67~74%가 아니다). 특히 **scene07 의 61.0 은 하늘 탓이 거의 아니다** — 상단 1/3의
비하늘부가 이미 55.5% 죽어 있다(거대 평면 옹벽). 하늘을 아무리 고쳐도 scene07 은 안 낫는다.

### 5.2 추정치 [추정]

`flat = f_sky·flat_sky_new + (1−f_sky)·flat_nonsky` (비하늘부 불변 가정, §5.1 실측 계수 +
§4 ACES 정합 flat_sky).

| 씬 | 지표 | 현행 | **S2 sunflowers** | **S1 kloofendal_48d** | S3 farm_field | 실사 |
|---|---|---|---|---|---|---|
| scene01 | 상단1/3 | 26.9 | **13.5** | 20.0 | 25.9 | 11.6 |
| scene01 | 전체 | 13.4 | **8.9** | 11.1 | 13.1 | 3.9 |
| scene07 | 상단1/3 | 61.0 | **51.8** | 55.5 | 58.8 | 11.6 |
| scene07 | 전체 | 27.4 | **23.7** | 25.3 | 26.7 | 3.9 |
| sceneD3 | 상단1/3 | 42.4 | **18.2** | 29.7 | 39.8 | 11.6 |
| sceneD3 | 전체 | 34.1 | **26.2** | 30.0 | 33.4 | 3.9 |

(검산: 현행 하늘 flat% 를 그대로 넣으면 scene01 13.2 / scene07 26.7 / sceneD3 34.1 이 나와
실측 13.4 / 27.4 / 34.1 과 일치한다 — 모형이 성립한다는 확인.)

불확실성: 시뮬레이션 뷰의 qwantani 값(99.35)이 실제 렌더 실측(89.1~97.5)보다 2~10 pp 높다
(PT 노이즈가 죽은 픽셀을 조금 되살린다). 같은 방향이면 위 추정은 **약간 보수적**이다.
반대로 RTX 돔 텍스처 필터링이 내 bilinear 리샘플보다 부드러우면 낙관 쪽이다. **±5 pp** 로 본다.

**정리**
- **하늘만 바꿔서 도달 가능한 상단 1/3의 하한은 scene01 12.8 / scene07 55.5 / sceneD3 18.9**
  (= 비하늘부 flat%). 하늘 flat% 를 0으로 만들어도 그 밑으로는 못 간다.
- 실사 기준 11.6 은 **scene01·sceneD3 는 S2 로 사거리 안**(13.5 / 18.2), **scene07 은 하늘로는
  불가능**하다 — 옹벽·평면 구조물 작업이 따로 필요하다.
- T1 헤드라인 게이트 `flat_pct < 8` 은 scene01 기준 하늘만으로 13.4→8.9 까지. 남은 0.9 pp 는
  지면·구조물 몫이며, 이는 §5 보조 게이트 `flat_gnd < 3.0` 의 취지와 일치한다.

### 5.3 노출·강도 대응값 (다음 지시서 입력용 참고 데이터)

신규 하늘은 qwantani 보다 **하늘이 훨씬 밝고 직달은 약하다.** 현행 노출을 유지하려면
`dome_intensity`·`noon_sun_intensity` 를 함께 내려야 한다(반구 적분 실측).

| HDRI | 제거 직달조도 (qwantani=100) | 하늘 평균휘도 (=100) | 등가 `noon_sun_intensity` | 등가 `dome_intensity` |
|---|---|---|---|---|
| qwantani_noon | 100.0% | 100.0% | 2450 (현행) | 1000 (현행) |
| S1 kloofendal_48d | 57.1% | 247.3% | ≈ **1400** | ≈ **405** |
| S2 sunflowers | 51.3% | 258.4% | ≈ **1255** | ≈ **385** |
| S3 farm_field | 0.0% | 655.1% | **0 (태양 끔)** | ≈ **155** |

이 값은 "현행 노출과 같은 밝기로 맞추는" 산술 등가치일 뿐이다. 실제 배정·랜덤화 정책은
다음 지시서 소관이므로 여기서 확정하지 않는다.

---

## 6. 감독이 바로 쓸 코드

### 6.1 `scene_common.py` 패치 (필수 1건 + 권고 2건)

```python
# [필수] ensure_noon_lookfix 내부 — 4채널(RGBA) EXR 대응
- rgb = cv2.imread(src_path, cv2.IMREAD_UNCHANGED)[..., ::-1]
+ rgb = cv2.imread(src_path, cv2.IMREAD_UNCHANGED)[..., :3][..., ::-1]

# [권고 A] 캡 반경 축소 — 구름 하늘의 "잘린 원반" 제거, 직달 제거량 보존 98~99%
- ring = (ang > 1.5) & (ang < 2.5)
+ ring = (ang > 0.6) & (ang < 1.0)
  cap  = np.percentile(lum[ring], 90)
- mask = (ang < 1.5) & (lum > cap)
+ mask = (ang < 0.6) & (lum > cap)

# [권고 B] 태양 검출 강건화 + 수용 게이트 (argmax → 상위 0.01% 입체각 가중 중심)
  thr = np.percentile(lum, 100 - 0.01)
  sel = lum >= thr
  wgt = (lum * np.sin(th)[:, None])[sel]
  v   = np.stack([dx[sel], dy[sel], dz[sel]], -1)
  s   = (v * wgt[:, None]).sum(0); s /= np.linalg.norm(s)   # ← iy,ix 대신 이걸로
  # 게이트: peak/cap < 50 이거나 sunE(<2.5°) < 5% 면 캡 생략 + 태양 비활성 권고
```

### 6.2 씬 `light_params` 예시 (파일명만 바꾸면 된다 — 파일은 `assets/` 루트)

```python
# ── S1: 산개 적운 (기본 대체안. 현행 qwantani 프로파일과 가장 가깝다) ──
light=dict(
    hdri="kloofendal_48d_partly_cloudy_puresky_4k.exr",
    lookfix=True,
    dome_intensity=405.0,           # 현행 노출 유지 등가치 (§5.3)
    noon_dome_rot=-110.0,
    noon_sun_enable=True, noon_sun_elev=47.86,     # HDRI 실측 고도
    noon_sun_intensity=1400.0, noon_sun_color=(1.0, 0.969, 0.935),
    hdri_sun_rotz_offset=235.77,
),

# ── S2: 층적운 밴드 (flat% 최대 이득 — 하늘이 많이 보이는 씬 우선) ──
light=dict(
    hdri="sunflowers_puresky_4k.exr",
    lookfix=True,
    dome_intensity=385.0,
    noon_dome_rot=-110.0,
    noon_sun_enable=True, noon_sun_elev=43.02,
    noon_sun_intensity=1255.0, noon_sun_color=(1.0, 0.969, 0.935),
    hdri_sun_rotz_offset=233.83,
),

# ── S3: 부분 흐림 (태양 완전 차폐 — 반드시 무태양 프로파일로) ──
light=dict(
    hdri="farm_field_puresky_4k.exr",
    lookfix=False,                  # 태양 오검출(§3.2) → 캡 무의미·유해
    dome_intensity=155.0,
    noon_dome_rot=-110.0,
    noon_sun_enable=False, noon_sun_elev=49.53,    # 그림자 계산식 호환용으로만 유지
    noon_sun_intensity=0.0, noon_sun_color=(1.0, 0.969, 0.935),
    hdri_sun_rotz_offset=0.0,
),
```

`sc.check_assets(ASSET_ROLES, hdri=PARAMS["light"]["hdri"])` 는 그대로 통과한다(파일 존재 확인만).

### 6.3 `hdri_sun_rotz_offset` 산출 근거

`setup_lighting` 은 `DomeLight.rotateZ = rot`, `DistantLight.rotateZ = rot + offset`,
`rotateX = 90 − elev` 로 만든다. USD 기본 DistantLight 는 −Z 를 향하므로
`rotateX(90−elev)` 후 광선 진행방향은 `(0, cos elev, −sin elev)` → **태양 위치 방위 = 270° + rotZ**.
한편 lookfix 의 등장방형 파라미터화는 `phi = 360·(ix+0.5)/w`.

qwantani 로 역산하면 `phi_sun = 216.17°`, 씬 상수 `offset = 233.5` →
`270 + 233.5 = 503.5 ≡ 143.5°`, 그리고 `360 − 216.17 = 143.83°`. **잔차 0.33°.**
즉 돔 텍스처 방위와 월드 방위는 **부호가 반대이고 상수항이 0**이다:

```
hdri_sun_rotz_offset = (90 − phi_sun) mod 360
```

검산: qwantani `(90−216.17) mod 360 = 233.83` vs 씬 상수 `233.5` (Δ0.33°, 태양 각지름 0.53°의
2/3 이내). 상수항이 깔끔하게 0으로 떨어지는 것이 이 부호 해석의 근거다 — 반대 부호를 가정하면
상수항이 −72.67° 라는 아무 의미 없는 값이 되어야 한다. [검산 1점, 잔차 0.33°]

**실무적 안전마진**: 신규 3종의 `phi_sun` 은 214.2~217.2° 로 qwantani(216.17°)와 ±2° 안이다
(PolyHaven puresky 시리즈가 방위 정렬돼 있다). 따라서 **부호 해석이 설령 틀렸더라도 오차는
최대 4.2°** 이고, 극단적으로는 **현행 233.5 를 그대로 써도 2° 이내**다. GPU 확보 시 씬 한 컷만
찍어 그림자 방위를 확인하면 확정된다.

---

## 7. 막힌 것 · 남긴 것

| 항목 | 상태 |
|---|---|
| GPU 검증 | **미실행**(지시대로 금지). 위 추정치는 전부 numpy 시뮬레이션 기반 — 실렌더 1라운드로 교차검증 필요 |
| 돔 방위 부호 | 1점 역산 + 상수항 0 논증으로 **[검산]**. 씬 1컷 렌더로 확정 가능(오차 상한 4.2°) |
| `scene_common.py` 패치 | **적용 안 함**(쓰기 금지 범위). §6.1 그대로 적용하면 된다 |
| scene07 계열 | 하늘 교체로는 개선폭 최대 9 pp. 상단 1/3 죽은 픽셀의 주범은 **평면 옹벽**이다 — 별도 과제 |
| S3(farm_field) 존치 여부 | flat% 이득 ≈ 0. 조명 다양성 목적이면 유지, flat% 우선이면 `kloppenheim_03_puresky`(84.4/고도 58.5°)로 교체 권고 |
| 씬별 하늘 배정·시각/계절 랜덤화 | **범위 밖**(다음 지시서). §5.3 등가 강도값만 입력 데이터로 남김 |
