# 라이선스 컴플라이언스 감사 v1 (2026-07-28)

감사 대상: `/home/vislab/Desktop/work_sy/Practice_NegObs` — **PUBLIC GitHub**
(https://github.com/wdragon92/Practice_NegObs)

감사 범위: 추적 파일 200개 전수 · git 히스토리 전체(`--all`) · `.gitignore` 실효성
검증(`git check-ignore`) · 다운로더 4종의 외부 소스 약관 원문 대조 · `Docs/CREDITS.md`
정합성 · 커밋된 렌더 산출물 4장 육안 검수 · 미추적 신규 에셋(`Docs/reference_photos/expanded/`)

감사관 권한 제약: 본 문서 외 어떤 파일도 수정하지 않았다. git 히스토리는 읽기만 했다.
GPU/Isaac Sim 미실행.

---

## 0. 결론 요약

| # | 항목 | 판정 |
|---|---|---|
| **A** | `Docs/reference_photos/everytime-1784886395380.jpg` | **위반 가능 — 최우선.** 제3자 사진, 라이선스 없음, **이미 origin/main 에 푸시됨** |
| **B** | `look_refs/*.jpg` 17장 (Gemini 생성) | **위반 가능.** Google 생성형 AI 추가 약관 "ML 모델 개발 금지" 조항 저촉 소지. 생성 표면 [미확인] |
| **C** | `Docs/reference_photos/expanded/` 54장 | **원칙 위반(미커밋).** 36장이 CC BY-SA 계열 = 프로젝트 허용 목록 밖. **.gitignore 미적용 → `git add -A` 한 번이면 커밋됨** |
| D | NVIDIA 식생 USD (`assets/vegetation/`) | **양호.** ignore 실효 확인, 히스토리 0건, 씬 코드 참조 0건 |
| E | PolyHaven / ambientCG 텍스처·HDRI | **양호.** 전부 CC0, 원문 확인 완료, ignore 실효 |
| F | 커밋된 렌더 컨택트 시트 4장 | **양호.** 절차 지오메트리만, 외부 에셋·브랜드·인물 0 |
| G | `Docs/CREDITS.md` | **불완전.** 사용 외부 에셋 22역할 중 기재 0건(하늘·식생만 기재) |
| H | 저장소 LICENSE 파일 | **부재.** 공개 저장소에 라이선스 선언 없음 |

---

## 1. 즉시 조치 필요 (위반 또는 위반 가능)

### A-1. `Docs/reference_photos/everytime-1784886395380.jpg` — 제3자 저작물 공개 배포 [최우선]

| 항목 | 값 |
|---|---|
| 경로 | `Docs/reference_photos/everytime-1784886395380.jpg` |
| 최초 커밋 | `6dac9a1` (2026-07-28 13:44:58 +0900) |
| **푸시 상태** | **`origin/main` 에 포함됨** (`git branch -r --contains 6dac9a1` → `origin/main`). 즉 **현재 공개 배포 중** |
| 해상도 | 1280×960 |
| EXIF | **없음** (앱 업로드·리사이즈 과정에서 제거된 전형적 형태) |
| 내용 | 한국 대학 캠퍼스 광장(건물번호 "909" 판독 가능), 위험 지점에 **빨간 원 주석** |
| 파일명 근거 | 접두사 `everytime-` = 대학 커뮤니티 앱 **에브리타임** 게시물에서 받은 것으로 강하게 시사 |
| 라이선스 | **없음 / 불명.** 저작권자 미상, 이용허락 근거 문서 0건 |

**왜 문제인가**
- 저작권자를 특정할 수 없는 제3자 사진이 라이선스·출처·허락 표시 없이 공개 저장소에 재배포돼 있다.
  프로젝트 원칙(`Docs/briefs/realism_brief_v1.md` 원칙 2: CC0/MIT-0/CC-BY만)의 명백한 이탈이다.
- **논문 연쇄 위험**: 이 파일은 `scripts/imgstats.py` 의 실사 기준군 `@real`
  (`Docs/reference_photos/*.jpg`, n=2) **2장 중 1장**이다
  (`scripts/imgstats.py:22`, `Docs/reports/realism_baseline.md:35,125`).
  사실화 라운드의 게이트 기준선(flat%·slope·sat 목표치)이 이 사진 위에 서 있으므로,
  논문이 이 수치를 인용하면 무허락 저작물이 **방법론에 편입**된다.
- 커뮤니티 앱 게시물은 게시자(원저작자)가 권리를 보유하며, 플랫폼 이용수칙도
  타인 권리 침해 게시물을 금지한다. 재배포 허락으로 볼 근거가 전혀 없다.

**감독 판단 필요 사항** (감사관은 조치하지 않음)
1. 이 파일의 실제 취득 경로 확인 — 본인 촬영인가, 타인 게시물인가.
2. 타인 게시물이면 (a) 원저작자 허락 취득 + CREDITS 기재, 또는 (b) 추적 제외.
   **이미 푸시됐으므로 워킹트리 삭제만으로는 공개 상태가 해소되지 않는다.**
   히스토리 제거는 감사관 권한 밖이며 별도 승인 필요.
3. 실사 기준군 n=2 를 무허락 사진 없이 재구성해야 하는지 판단
   (→ `expanded/` 의 CC0 8장이 대체 후보, C-2 참조).

### A-2. `Docs/reference_photos/1784886529634.jpg` — 자체 촬영으로 판단, 문제 없음

EXIF 실측: `Make=samsung`, `Model=Galaxy S26 Ultra`, `DateTime=2026:07:21 15:03:44`,
5712×4284 원본 해상도. 리사이즈·재인코딩 흔적 없음 → **연구진 자체 촬영본**으로 판단.
라이선스 문제 없음. 다만 CREDITS 에 "자체 촬영, 저작권 보유"를 명시하면
동일 폴더의 A-1 과 구별돼 향후 혼동을 막는다. (실존 캠퍼스 건물이 식별 가능하나
공개 장소 촬영이므로 배포 자체는 문제 없음.)

### B. `look_refs/*.jpg` 17장 — Google Gemini(나노바나나) 생성물

| 항목 | 값 |
|---|---|
| 최초 커밋 | `22c011f` (2026-07-28) — **`origin/main` 포함, 공개 배포 중** |
| 파일 | `c1~c4`(4) · `d1`,`d1_v1`,`d1_v2_overview`,`d2~d4`(6) · `n1`,`n2`,`n2_v1_rejected`,`n3~n5`(6) · `scene19_nanobanana_fix`(1) = **17장** |
| 해상도 | 전부 1408×768 (Gemini 이미지 생성 출력 규격) |
| 생성 경로 | `look_refs/scene19_prompts.md` 서두: "**gemini.google.com 또는 aistudio.google.com** 에서 아래 프롬프트로 생성" |
| 용도 | 배치1 12씬(`scenes/batch1/`)의 재질·조명·미장센 설계 레퍼런스 (README 명시: "Gemini(나노바나나) 레퍼런스 → 코드 번역 워크플로") |

**소유권은 문제 없다.** Gemini API 추가 약관 원문:

> "Google won't claim ownership over that content."
> — https://ai.google.dev/gemini-api/terms (2026-07-28 확인)

**문제는 사용 제한 조항이다.** Google **생성형 AI 추가 서비스 약관**(현행판, 2023-08-09
개정 — https://policies.google.com/terms/generative-ai/archive 에서 현행 버전임을 확인)
"Use restrictions" 절 원문:

> "**You may not use the Services to develop machine learning models or related technology.**"
> — https://policies.google.com/terms/generative-ai/archive/20230809 (2026-07-28 확인)

이 프로젝트의 목적 자체가 **ML 학습용 합성 데이터 생성**이다. 생성 이미지를 씬 설계
레퍼런스로 삼아 학습 데이터를 만든 워크플로가 "use the Services to develop machine
learning models" 에 해당하는지는 해석 여지가 있으나, **공개 저장소 + 논문이라는
노출 조건에서 방어하기 어려운 위치**다.

**중요한 분기 — 어느 표면에서 생성했는가:**

| 생성 표면 | 적용 약관 | 판정 |
|---|---|---|
| **gemini.google.com** (소비자 Gemini 앱) | 생성형 AI 추가 서비스 약관 | **"ML 모델 개발 금지" 조항 적용 → 저촉 소지** |
| **aistudio.google.com / Gemini API** | Gemini API 추가 약관 | 제한이 "You may not use the Services to develop models that **compete with** the Services" 로 한정 → **저촉 없음** |

→ `scene19_prompts.md` 는 두 경로를 모두 안내하고 있어 **실제 사용 표면이 [미확인]**이다.
**이 한 가지 사실 확인만으로 판정이 갈린다.** 감독이 확인해 주기 바란다.

**부수 사항**
- Gemini 생성 이미지에는 **SynthID 비가시 워터마크**가 삽입된다. 논문 심사·리뷰 과정에서
  "레퍼런스가 AI 생성물"임이 기계적으로 검출될 수 있다. 은닉 의도가 없더라도
  `look_refs/nanobanana_batch1_prompts.md` 에 생성 사실이 명시돼 있으므로 은폐는 아니지만,
  **논문 본문에도 생성 사실을 명시**하는 편이 안전하다.
- 프롬프트 공통 접미사에 "no text or watermarks" 가 포함돼 있다. 이는 생성물 안에
  가짜 로고·워터마크가 찍히지 않게 하는 지시로, 타인 워터마크 제거와는 무관하다. 문제 없음.
- 육안 검수(c1/d1/d4/n3 표본): 판독 가능한 상표·로고·실존 인물 **없음**.
  `c1_snow_stairs.jpg` 우상단에 차량 일부가 보이나 차종·브랜드 식별 불가.

### C. `Docs/reference_photos/expanded/` 54장 — .gitignore 사각지대 + 허용 라이선스 밖

| 항목 | 값 |
|---|---|
| 상태 | **미추적(`??`) + `.gitignore` 미적용** — `git check-ignore` 결과 `NOT IGNORED` |
| 규모 | 54장 / 50 MB |
| 출처 | Wikimedia Commons (전 항목 `commons_page` URL 보유) |
| 대장 | `LICENSES.csv` — 54행, `file/license/license_url/author/credit/date/commons_page/original_url/orig_w/orig_h/harvest_query/title` 12열. **결측 0건**(author·license_url·commons_page 전수 채워짐), 디스크 파일과 1:1 일치(차집합 0) |

**대장 품질 자체는 우수하다.** 문제는 두 가지다.

**C-1. `.gitignore` 사각지대 — 실질 위험**

`.gitignore` 는 `assets/*.exr`, `assets/*.jpg`, `assets/scene01/*`, `assets/vegetation/`,
`look_check/` 만 막는다. `Docs/reference_photos/` 는 **어떤 규칙에도 걸리지 않는다.**
검증:

```
$ git check-ignore -v Docs/reference_photos/expanded/x.jpg
NOT IGNORED
```

즉 누군가 `git add -A` 또는 `git add Docs/` 를 한 번 실행하면 **50 MB / 54장이
그대로 공개 저장소에 들어간다.** 실제로 같은 폴더의 A-1 파일이 이미 그 경로로 커밋됐다.

**C-2. 라이선스 구성이 프로젝트 허용 목록 밖**

`Docs/briefs/realism_brief_v1.md` 원칙 2 원문:
> "**무료만**: CC0 / MIT-0 / CC-BY(크레딧 기록)만 사용."

실제 구성:

| 라이선스 | 장수 | 원칙 부합 |
|---|---:|---|
| CC0 | 8 | ✅ |
| CC BY 4.0 | 7 | ✅ (저자 크레딧 필수) |
| CC BY 2.0 | 1 | ✅ (저자 크레딧 필수) |
| **CC BY-SA 4.0** | **30** | ❌ 허용 목록 밖 |
| **CC BY-SA 3.0** | **3** | ❌ |
| **CC BY-SA 2.5 / 2.0 / 2.0 kr** | **3** | ❌ |
| **KOGL Type 1** | **2** | ⚠ 목록에 없으나 실질 CC-BY 동등 |
| **합계** | **54** | **허용 16 / 미허용 36 / 검토 2** |

- **CC BY-SA(36장)**: 저작자표시-**동일조건변경허락**. 원본 그대로의 재배포는
  저작자표시 + 라이선스 고지로 가능하지만, **2차적저작물(adaptation)에는 동일 BY-SA 적용
  의무**가 붙는다. "사진을 보고 3D 씬을 만든다"가 2차적저작물인지는 아이디어/표현 이분법상
  일반적으로 아니라고 보지만, **논문에서 "이 사진들을 참조해 씬을 제작했다"고 서술하는 순간
  심사자가 SA 전파 여부를 물을 수 있는 표면이 생긴다.** 원칙 2가 애초에 SA 를 제외한 이유가 이것이다.
- **KOGL Type 1 (2장, 한국관광공사)**: 공공누리 제1유형 원문 확인 결과
  "상업적, 비상업적 이용가능" + "변형 등 2차적 저작물 작성 가능" + **출처표시 의무**,
  "공공기관과의 후원·특수관계를 표현해선 안 됨" (https://www.kogl.or.kr/info/license.do,
  2026-07-28 확인). → **실질 CC-BY 동등. 출처표시만 지키면 사용 가능.**
  원칙 2 문면에는 없으므로 명시적 편입 판단이 필요하다.

**감독 판단 필요 사항**
1. `Docs/reference_photos/` 를 `.gitignore` 에 추가할 것인가
   (권장 — A-1 재발 방지 + `expanded/` 유출 차단). 단 `LICENSES.csv` 는 추적 유지 권장.
2. 원칙 2 를 "CC0 / MIT-0 / CC-BY / KOGL-1" 로 개정하고 BY-SA 36장을 배제할 것인가,
   아니면 "BY-SA 는 **로컬 참조 전용, 배포·재현 산출물에 미포함**" 조건으로 허용할 것인가.
3. 실사 기준군(`@real`)을 **CC0 8장**으로 재구성하면 A-1 의존이 사라지고 n 도 2→8 로 늘어
   기준선 신뢰도가 함께 개선된다. (n=2 는 `realism_baseline.md:125` 스스로 한계로 적고 있다.)

---

## 2. 추적 파일 중 외부 에셋 유래 — 전수 목록

추적 파일 200개 중 바이너리/에셋류는 **29개**(`.jpg` 19 · `.png` 9 · `.mdl` 1).
나머지 171개는 `.md`/`.py`/`.sh`/심링크로 라이선스 리스크 없음.

| 경로 | 출처 | 라이선스 | 판정 |
|---|---|---|---|
| `look_refs/*.jpg` (17) | Google Gemini 생성 | 소유권 없음 / **사용제한 조항 확인 필요** | ⚠ **§1-B 참조** |
| `Docs/reference_photos/everytime-1784886395380.jpg` | 제3자(에브리타임 추정) | **없음** | ❌ **§1-A-1 참조** |
| `Docs/reference_photos/1784886529634.jpg` | 자체 촬영 (EXIF: Galaxy S26 Ultra) | 자체 보유 | ✅ |
| `Docs/audit_v4/library21_final_hq.png` | 자체 렌더 컨택트 시트 | 자체 생성 | ✅ (§4) |
| `Docs/audit_v4/keep15_v5pt_hq.png` | 자체 렌더 | 자체 생성 | ✅ |
| `Docs/audit_v4/scene_overview_v4.png` | 자체 렌더 | 자체 생성 | ✅ |
| `Docs/audit_v4/fixlog_W0_paving_cmp.png` | 자체 렌더 비교컷 | 자체 생성 | ✅ |
| `assets/signs/sign_*.png` (5) | `assets/signs/gen_signs.py` 절차 생성 (PIL + Noto Sans CJK) | 자체 생성 | ✅ ※주1 |
| `assets/NegObsGround.mdl` | 자체 작성 MDL | 자체 — **단 §3-D 참조** | ⚠ 경미 |

※주1 — `gen_signs.py` 는 "한국 공공 사인 관행(경고=황색 삼각/흑, 안내=청색 패널/백,
금지=적테)"을 참조해 도형을 **직접 그린다**. 실제 규격 도안 파일을 복제하지 않으며,
법정 안전표지 도안은 일반적으로 저작권 보호 대상이 아니다. 폰트는 시스템의
`NotoSansCJK-Black.ttc`(SIL OFL — 렌더 결과물에 라이선스 전파 없음). **문제 없음.**
단 이 5장은 씬 코드에서 참조 흔적이 없다(`grep sign_` → `sceneD4` 의 색상 상수만 매칭).
미사용 자산이다.

### 다운로더 4종 — 외부 소스 전수 대조

#### (1) `assets/download_assets.py` — PolyHaven

| 대상 | slug | 종류 |
|---|---|---|
| 텍스처 3세트 | `aerial_grass_rock`, `brown_mud_dry`, `brown_mud_03` | 4k jpg diff/nor_dx/rough |
| HDRI 2종 | `qwantani_noon_puresky`, `qwantani_dawn_puresky` | 4k exr |

> **씬 코드 참조 0건.** 텍스처 3세트는 룩데브 v1(현 `Practice_TerrainGen`) 잔재로 보인다.
> HDRI `qwantani_noon_puresky_4k.exr` 만 `scene_common.py:36 DEFAULT_HDRI` 로 실사용.

#### (2) `assets/download_sky.py` — PolyHaven HDRI 3종 (신규)

`kloofendal_48d_partly_cloudy_puresky` · `sunflowers_puresky` · `farm_field_puresky`

#### (3) `assets/scene01/download_scene01_assets.py` — ambientCG 4 + PolyHaven 17 + HDRI 1

**ambientCG (4세트, zip → jpg 추출)**
`https://ambientcg.com/get?file={ID}_4K-JPG.zip`

| ID | canonical | 배치 |
|---|---|---|
| `Tiles038` | `plaza_light` | `assets/scene01/` |
| `PavingStones127` | `band_dark` | `assets/scene01/` |
| `PavingStones111` | `plaza_lower` | `assets/scene01/` |
| `PavingStones131` | `paving_interlock` | `assets/` 루트 |

**PolyHaven (17세트)**
`granite_tile`→granite_dark · `brick_wall_001`→brick_red ·
`concrete_wall_008`→concrete_wall · `brushed_concrete_03`→concrete_floor ·
`weathered_planks`→wood_dark · `park_dirt`→dirt_park · `gravel_floor`→gravel ·
`stone_tiles_02`→stone_flag · `rock_wall_08`→rock_wall ·
`stone_wall_05`→stone_worn · `red_sandstone_pavement`→sandstone ·
`marble_01`→marble_light · `rusty_metal_04`→metal_rust ·
`painted_plaster_wall`→plaster · `rock_surface`→rock_face ·
`forest_leaves_03`→leaf_ground · `asphalt_02`→asphalt
**HDRI**: `kloofendal_overcast` → `assets/kloofendal_overcast_4k.exr`
**절차 생성**: `tactile_yellow_diff.png` / `tactile_yellow_nor.png` (점자블록, numpy+PIL)

#### (4) `assets/download_vegetation.py` — NVIDIA Omniverse S3

`https://omniverse-content-production.s3.us-west-2.amazonaws.com/Assets/Vegetation/`
→ `Trees/Japanese_Cherry.usd`, `Trees/Yellow_Pine.usd`, `Trees/White_Pine.usd`,
`Shrub/Boxwood.usd` + `*/materials/*.mdl`(5) + `*/materials/textures/*.png`(10)
= 20 파일 / 128.2 MB

### 소스별 라이선스 원문 (웹 확인, 2026-07-28)

**Poly Haven** — https://polyhaven.com/license

> "All assets (HDRIs, textures and 3D models) on this site are the original work of Poly Haven
> staff, or artists who willingly and directly donate/sell their work to Poly Haven.
> Our assets are all licensed as CC0 […] **You can use our assets for any purpose, including
> commercial work.** You do not need to give credit or attribution when using them (although it
> is appreciated). **You can redistribute them**, share them around, include them when sharing
> your own work, or even in a product you sell."

**AI 학습 허용 여부** — 라이선스 페이지가 직접 언급한다:
> "we've heard from numerous data scientists, software developers, automotive engineers and
> **AI researchers all using our assets in their work**, which simply wouldn't be possible with
> more restrictive (even open source) licenses."

→ **CC0. 합성 학습 데이터 생성·재배포 전면 허용.** 별도 조건 없음.
(※ 페이지는 에셋 외의 사이트 콘텐츠 — 로고·홍보 렌더·본문 텍스트 — 는 저작권 보호 대상이라고
별도로 밝힌다. 우리는 에셋만 받으므로 무관.)

**ambientCG** — https://ambientcg.com/license → https://docs.ambientcg.com/license/ (302 리다이렉트)

> "All ambientCG assets are provided under the **Creative Commons CC0 1.0 Universal License**."
> "You can copy, modify, distribute and perform the assets, **even for commercial purposes**,
> all without asking permission."
> "You can include the raw files in your project, for example a video game."
> "You don't need to give credit but I would of course appreciate it, if you did it anyways."

**AI 학습 허용 여부** — **[미확인 / 명시 없음].** 라이선스 페이지는 기계학습·AI 학습을
언급하지 않는다. 다만 CC0 는 저작권·인접권의 전면 포기이므로 학습 이용을 제한할 근거가
법적으로 존재하지 않는다. PolyHaven 처럼 **명시적 허용 문구는 없다**는 점만 기록한다.

> ⚠ **ambientCG zip 내부 구성 주의**: `ZZ_synthesis.md` §10.6 이 "zip에 `.usdc` + 잎 아틀라스
> 38종 포함"이라고 적고 있다. 현재 다운로더는 `_Color/_NormalDX/_Roughness` 3종만 남기고
> "zip·잔여파일(AO/Displacement/Normal GL/usdc/blend 등) 삭제"하므로 실제로는 반입되지 않는다.
> 라이선스는 어차피 CC0 라 문제없으나, 다운로더 수정 시 이 정리 단계를 없애면 저장소에
> `.usdc` 가 흘러들 수 있다(§3-C 의 ignore 갭과 결합하면 실제 유출 경로가 된다).

**NVIDIA Omniverse S3 에셋** — 소스 버킷에 LICENSE 파일 **없음**
(`LICENSE.txt`/`LICENSE`/`license.txt`/`Assets/LICENSE.txt`/`Assets/Vegetation/LICENSE.txt`
전부 HTTP 404로 확인). 적용되는 상위 약관은 NVIDIA Software License Agreement 이며,
`docs.omniverse.nvidia.com` 은 자동 접근을 403 으로 차단해 UGC 절 원문은 확보하지 못했다
(**[미확인]** — §6 참조). 다만 **핵심 금지 조항은 nvidia.com 원문에서 직접 확인했다**:

> "Except as expressly granted in the Agreement, including the Product-Specific Terms, Customer
> may not copy, sell, resell, rent, sublicense, transfer, assign, timeshare, distribute, modify,
> or create derivative works of any portion of the Software, **including, without limitation,
> in any publicly accessible software repositories.**"
> — NVIDIA Software License Agreement,
> https://www.nvidia.com/en-us/agreements/enterprise-software/nvidia-software-license-agreement/
> (2026-07-28 확인)

**AI 학습 허용 여부** — NVIDIA 약관에 **ML 학습을 금지하는 조항은 확인되지 않았다.**
Product-Specific Terms for NVIDIA Omniverse (2026-04-15판, 전문 확인) 에도 학습 금지 조항 없음.
Replicator 제품의 존재 목적 자체가 합성 학습 데이터 생성이라는 점과 정합한다.
→ **`ZZ_synthesis.md` §9.2 의 판정(학습 ✅ / 렌더 이미지 공개 ✅ / USD 재배포 ❌)은 유효하며,
현재 저장소는 이를 정확히 지키고 있다** (§2-D 참조).

---

## 3. `.gitignore` 실효성 검증 및 git 히스토리 잔존물

### 3-A. `git check-ignore` 실측 결과

| 경로 | 결과 |
|---|---|
| `assets/vegetation/Trees/Japanese_Cherry.usd` | ✅ `.gitignore:39:assets/vegetation/` |
| `assets/qwantani_noon_puresky_4k.exr` | ✅ `.gitignore:25:assets/*.exr` |
| `assets/paving_interlock_diff.jpg` | ✅ `.gitignore:26:assets/*.jpg` |
| `assets/aerial_grass_rock_diff_4k.jpg` | ✅ `.gitignore:26:assets/*.jpg` |
| `assets/scene01/gravel_diff.jpg` | ✅ `.gitignore:27:assets/scene01/*` |
| `look_check/foo.png` | ✅ `.gitignore:19:look_check/` |
| `assets/signs/sign_exit.png` | ⚪ NOT IGNORED — **의도된 예외**(자체 생성 92 KB, 주석에 명시) |
| **`Docs/reference_photos/expanded/x.jpg`** | ❌ **NOT IGNORED** — §1-C |

### 3-B. **git 히스토리에 한 번이라도 커밋된 바이너리 전수**

`git log --all --diff-filter=A --name-only` 결과. **아래 전부 `origin/main` 에 포함 = 배포 완료 상태.**

| 커밋 | 일시 | 파일 | 현 추적 | 판정 |
|---|---|---|---|---|
| `a72af9d` | 2026-07-23 | `assets/NegObsGround.mdl` | 추적 중 | ⚠ §3-D |
| `a72af9d` | 2026-07-23 | `terrain_dev/preview_cross_sections.png` | **삭제됨(히스토리 잔존)** | ✅ 자체 생성 |
| `a72af9d` | 2026-07-23 | `terrain_dev/preview_ditch_zoom.png` | 삭제됨 | ✅ |
| `a72af9d` | 2026-07-23 | `terrain_dev/preview_face_class.png` | 삭제됨 | ✅ |
| `a72af9d` | 2026-07-23 | `terrain_dev/preview_hillshade_full.png` | 삭제됨 | ✅ |
| `a72af9d` | 2026-07-23 | `terrain_dev/preview_long_profile.png` | 삭제됨 | ✅ |
| `22c011f` | 2026-07-28 | `look_refs/*.jpg` **17장** | 추적 중 | ⚠ **§1-B** |
| `6dac9a1` | 2026-07-28 13:44 | `Docs/reference_photos/everytime-*.jpg` | 추적 중 | ❌ **§1-A-1** |
| `6dac9a1` | 2026-07-28 13:44 | `Docs/reference_photos/1784886529634.jpg` | 추적 중 | ✅ 자체 촬영 |
| `6dac9a1` | 2026-07-28 13:44 | `Docs/audit_v4/*.png` **4장** | 추적 중 | ✅ 자체 렌더 |
| — | — | `assets/signs/sign_*.png` 5장 | 추적 중 | ✅ 자체 생성 |

**핵심 결과 — 좋은 소식:**
- **NVIDIA USD·MDL·텍스처가 히스토리에 들어간 적이 단 한 번도 없다.**
  (`.usd`/`.usda`/`.usdc`/`.usdz` 확장자 추가 이력 0건. `assets/vegetation/` 경로 이력 0건.)
  식생 조달(07-28 21:30)과 동시에 `.gitignore` 조치(`45d2a3d`)가 이뤄져 유출 창이 없었다.
- **EXR HDRI 도 히스토리에 없다.** 어차피 CC0 라 무해하지만 용량 관점에서도 정상.
- 이미 삭제된 `terrain_dev/preview_*.png` 5장은 히스토리에 남아 있으나 **전부 자체 절차
  생성 지형 프리뷰**로 라이선스 리스크 없다. 조치 불요.

**나쁜 소식:** 리스크가 있는 18장(everytime 1 + look_refs 17)은 **전부 이미 공개 원격에 있다.**
워킹트리에서 지워도 `https://github.com/wdragon92/Practice_NegObs/commit/6dac9a1` 등으로
계속 접근 가능하다. 실질 해소에는 히스토리 재작성(감사관 권한 밖, 감독 승인 필요)
또는 원저작자 허락 취득이 필요하다.

### 3-C. `.gitignore` 구조적 갭 (아직 사고는 없었으나 열려 있음)

| 갭 | 위험 |
|---|---|
| `Docs/reference_photos/` 무규칙 | **§1-C. 실제 사고 1건(A-1) 이미 발생** |
| `assets/*.png` 미차단 (`*.exr`·`*.jpg` 만) | 루트에 PNG 텍스처를 받으면 커밋된다 |
| `assets/*.usd*` / `assets/*.mdl` 미차단 | **NVIDIA USD·MDL 을 `assets/` 루트에 받으면 그대로 커밋 → §2 인용 조항 정면 위반.** 현재 다운로더는 `assets/vegetation/` 아래만 쓰므로 안전하지만, 경로가 한 번 바뀌면 차단막이 없다 |
| `assets/scene01/*` 는 완전 차단이나 `assets/scene02..` 등 미래 폴더 무규칙 | 확장 시 반복 위험 |

→ 권고 방향(감독 조치 사항): 허용목록(allowlist) 방식으로 뒤집기 —
`assets/**` 를 통째로 무시하고 `!assets/**/*.py`, `!assets/*.mdl`, `!assets/signs/*.png` 만
되살리는 편이 확장에 안전하다. **감사관은 수정하지 않았다.**

### 3-D. `assets/NegObsGround.mdl` — OmniPBR 유래 표기 누락 (경미)

787줄, 저작권/라이선스 헤더 **전무**(`grep -niE 'copyright|license|SPDX'` → 0건).
파일 자체 주석이 NVIDIA MDL 유래를 명시한다:

> `* BSDF는 OmniPBRBase의 metalness=0/coat 없음 경로를 그대로 축약 이식.` (2행 헤더 21행)
> `//  BSDF — OmniPBRBase(metalness=0, coat 없음) 경로 축약 이식  //` (761행)

"그대로 축약 이식"이 **코드 이식**인지 **동작 재현**인지가 판정을 가른다.
- 동작 재현(스펙 보고 다시 씀) → 문제 없음.
- OmniPBRBase.mdl 소스를 옮겨 적은 것이라면 §2 인용 조항의
  "create derivative works of any portion of the Software … in any publicly accessible
  software repositories" 에 걸린다. MDL 자체는 표준 규격(NVIDIA 공개)이나
  **OmniPBR 구현체는 Omniverse Software 구성요소**다.

→ **감독 확인 필요.** 이식이라면 (a) 해당 BSDF 블록을 MDL 표준 `df::` 프리미티브로
독립 재작성하거나, (b) NVIDIA 배포 조건 확인 후 고지 헤더를 넣어야 한다.
현재 상태는 **출처 표기 없는 이식 주장**이라 가장 나쁜 조합이다.
(우선순위는 §1 세 건보다 낮다 — 코드 787줄 중 BSDF 결선부 일부이고,
MDL 규격 자체는 공개 스펙이다.)

---

## 4. `Docs/CREDITS.md` 정합성 — 누락 · 과잉 · 오류

현재 CREDITS.md 는 **2개 절**뿐이다: "하늘 HDRI"(담당: 하늘 조달) · "식생 에셋"(담당: 식생 조달).
둘 다 2026-07-28 작성. **두 절 모두 내용 품질은 높다** — PolyHaven 원문 인용, NVIDIA
재배포 금지 판정, 파일별 표, 수종 대조표까지 갖췄다. 문제는 **커버리지**다.

### 4-A. 누락 (심각) — 실사용 외부 에셋의 기재율 0%

씬 코드가 실제로 참조하는 텍스처 역할 22종(`grep` 실측):

```
asphalt · band_dark · brick_red · concrete_floor · concrete_wall · dirt_park ·
granite_dark · gravel · leaf_ground · marble_light · metal_rust · paving_interlock ·
plaster · plaza_light · plaza_lower · rock_face · rock_wall · sandstone ·
stone_flag · stone_worn · tactile_yellow · wood_dark
```

이 중 `tactile_yellow`(자체 절차 생성)를 뺀 **21종 전부가 외부 유래(ambientCG 4 + PolyHaven 17)**
이며 **CREDITS.md 에 단 한 줄도 없다.**

| 누락 항목 | 사유 | 심각도 |
|---|---|---|
| **ambientCG 4세트** (`Tiles038`/`PavingStones127`/`PavingStones111`/`PavingStones131`) | 절 자체가 없음. CC0 라 법적 의무는 없으나 재현성·감사 추적성 상실 | **높음** |
| **PolyHaven 텍스처 17세트** | 하늘 절이 HDRI 만 다뤄 텍스처가 통째로 빠짐 | **높음** |
| **`look_refs/` Gemini 생성물 17장** | 어디에도 기재 없음. `look_refs/nanobanana_batch1_prompts.md` 에 프롬프트는 있으나 CREDITS 연결 없음 | **높음** (§1-B) |
| **`Docs/reference_photos/` 2장** | 출처·권리 기재 없음. **A-1 이 걸러지지 못한 직접 원인** | **높음** (§1-A) |
| `assets/download_assets.py` 의 텍스처 3세트 + HDRI `qwantani_dawn` | 미사용이나 저장소가 받아오는 대상 | 중 |
| `assets/NegObsGround.mdl` 의 OmniPBR 유래 | §3-D | 중 |
| `assets/signs/*.png` 5장 + Noto Sans CJK 폰트 | 자체 생성이나 폰트 의존 기록 없음 | 낮음 |
| `Docs/reference_photos/expanded/` 54장 | 미커밋. `LICENSES.csv` 는 있으나 CREDITS 미연결 | 중 (§1-C) |

**CC-BY 항목의 저자명·URL 누락 여부**: 현재 CREDITS 에 기재된 항목은 전부 CC0(PolyHaven)
또는 NVIDIA 라 **CC-BY 항목 자체가 0건**이다. 따라서 "저자명 누락" 사례는 없다.
다만 `expanded/` 를 채택하면 **CC-BY 8장 + CC BY-SA 36장 + KOGL 2장 = 46장의
저자 크레딧이 새로 발생**하며, 이는 `LICENSES.csv` 의 `author`/`license_url`/`commons_page`
열에 이미 결측 없이 준비돼 있다(§1-C). CREDITS 로 옮기기만 하면 된다.

### 4-B. 과잉 — 기재됐으나 실사용 0건

| 항목 | 상태 |
|---|---|
| `kloofendal_48d_partly_cloudy_puresky_4k.exr` | 씬 코드 참조 **0건** |
| `sunflowers_puresky_4k.exr` | 참조 **0건** |
| `farm_field_puresky_4k.exr` | 참조 **0건** |
| 식생 USD 4종 + MDL 5 + 텍스처 10 (128 MB) | **씬 코드 참조 0건** (`grep -rn "vegetation\|Japanese_Cherry\|Boxwood\|Yellow_Pine"` → 다운로더 외 0) |

씬이 실제로 쓰는 HDRI 는 `qwantani_noon_puresky_4k.exr`(기본) · `kloofendal_overcast_4k.exr` ·
`*_lookfix.exr` 파생본 3종뿐이다. **거짓 기재는 아니고 "조달 완료·결선 대기" 상태**지만,
CREDITS 를 읽는 제3자는 이것들이 산출물에 반영됐다고 오해한다.
→ 각 항목에 **"조달 완료 / 씬 미결선(2026-07-28 기준)"** 표시를 권고.

**이 과잉이 §4-C 리스크와 직결된다**: 식생이 아직 결선되지 않았기 때문에 **현재까지의
모든 렌더 산출물에 NVIDIA 지오메트리가 한 픽셀도 없다.** 결선하는 순간 §5 체크리스트의
성격이 바뀐다.

### 4-C. 중복·모순

`CREDITS.md` 서두는 "**CC0 / MIT-0 / CC-BY 만 사용한다**"고 선언하고,
55~72행 식생 절은 "**CC0 가 아니다. 주의 필요 … 이 원칙의 예외다**"라고 스스로 밝힌다.
→ **의도된 예외이며 근거(`ZZ_synthesis` §9.2·§10.6)까지 명기돼 있어 모순이 아니다.**
담당자별 절 분리 규약도 지켜져 중복 기재는 없다. **이 항목은 문제 없음.**

### 4-D. 저장소 LICENSE 파일 부재

`LICENSE` / `COPYING` **없음**. 공개 저장소에 라이선스 선언이 없으면 기본값은
"All rights reserved" — 제3자는 코드·씬 스크립트를 재사용할 수 없다. 논문 재현성 주장과
충돌한다. 데이터셋 공개 시에는 **코드 라이선스와 데이터 라이선스를 분리 선언**해야 한다(§5).

---

## 5. 산출물(렌더 이미지) 공개 가능성 판정

**대상**: `look_check/`(13 GB, 3,759 장 — `.gitignore` 로 미추적) 및
커밋된 컨택트 시트 4장(`Docs/audit_v4/*.png`).

**육안 검수**: `library21_final_hq.png`(3840×3798, 본편 21씬 전수) 전체를 확인했다.

| 검사 항목 | 결과 |
|---|---|
| NVIDIA 에셋이 찍힌 프레임 | **0** — 나무·관목은 전부 절차 프리미티브(구·원뿔 조합). 식생 USD 미결선(§4-B)이므로 구조적으로 불가능 |
| 상표·브랜드 로고 | **0** — 건물·간판·차량 전부 무브랜드 절차 생성 |
| 실차(브랜드 차량) | **0** — 차량 프롭 자체가 없음 |
| 실존 인물 / 인체 모델 | **0** — 사람 프롭 없음 |
| 실존 장소 재현 | 한국 일상 공간의 **유형**(제방·지하도·사원 돌계단 등)이며 특정 실존 건축물의 복제는 확인되지 않음 |
| 외부 텍스처 노출 | ambientCG·PolyHaven **CC0** 텍스처만 → 렌더·재배포 무제한 |
| 문자 요소 | scene16 의 청색 안내 사인 = `assets/signs/` 자체 생성 한글 텍스처 |

**판정: `look_check/` 렌더 이미지와 커밋된 컨택트 시트 4장은 현재 상태 그대로 공개 가능하다.**
법적 제약 요소가 하나도 없다.

**단 조건부다 — 브리프 Phase 2 항목 8("나무 교체 — `build_tree` 내부를 S3 식생 에셋
인스턴싱으로")이 실행되면 판정이 바뀐다.** 그 이후 렌더는 NVIDIA 지오메트리를 포함하므로:
- **렌더 이미지 공개: 계속 ✅** (§2 확인 — NVIDIA 약관에 학습·이미지 공개 금지 없음)
- **USD/텍스처 재배포: ❌** (§2 인용 조항)
- **기관 승인 권고** (`ZZ_synthesis` §9.2)
→ 즉 "이미지는 되고 원본은 안 된다"는 경계선이 **그때 처음 실효**한다. 지금은 무관하다.

---

## 6. 데이터셋 공개 시 제외 체크리스트

"합성 데이터셋을 공개 배포한다"는 가정하의 반출 전 점검표.
각 항목은 감독이 O/X 판정할 수 있도록 작성했다. **감사관은 어떤 파일도 지우지 않았다.**

### 6-A. 반드시 제외 (배포물에 넣지 말 것)

- [ ] **`assets/vegetation/**` 전체** (USD 4 + MDL 5 + PNG 10, 128 MB) — NVIDIA 재배포 금지.
      재현은 `assets/download_vegetation.py` 로. **현재 `.gitignore` 로 이미 차단됨(유지 확인만).**
- [ ] **`Docs/reference_photos/everytime-1784886395380.jpg`** — 라이선스 없는 제3자 저작물(§1-A-1).
      **워킹트리 제거만으로는 부족 — 이미 origin/main 에 있음.**
- [ ] **`Docs/reference_photos/expanded/**` 중 CC BY-SA 36장** — 원칙 2 밖(§1-C-2).
      (CC0 8 + CC BY 8 + KOGL 2 = 18장은 크레딧 첨부 조건으로 반출 가능.)
- [ ] **`look_check/` 원본 13 GB 전량** — 배포용은 씬·뷰 선별 서브셋으로.
      (라이선스 문제가 아니라 용량·중복 관리 문제.)
- [ ] Isaac Sim 설치본에서 유래한 일체의 USD/MDL/텍스처 — 현재 0건이나 결선 후 재확인.

### 6-B. 결정 필요 (감독 판단 없이는 반출 금지)

- [ ] **`look_refs/*.jpg` 17장 (Gemini 생성)** — §1-B. **생성 표면(gemini.google.com vs
      AI Studio) 확인이 선행 조건.** 소비자 Gemini 앱이었다면 데이터셋 동봉은 물론
      "이 이미지들을 참조해 학습 데이터를 만들었다"는 논문 서술 자체를 재검토해야 한다.
- [ ] **`assets/NegObsGround.mdl`** — §3-D. OmniPBRBase "축약 이식"의 실체 확인.
      이식이면 재작성 또는 고지 후 반출.
- [ ] **실사 기준군(`@real`) 재구성** — A-1 을 빼면 n=1 이 된다.
      `expanded/` CC0 8장으로 교체하면 n=8 + 라이선스 청정 + 기준선 신뢰도 개선.
      **논문 수치를 다시 뽑아야 하므로 조기 결정이 유리하다.**

### 6-C. 반출 시 반드시 동봉

- [ ] **`CREDITS.md` 전면 개정** — §4-A 누락 8건 반영. 특히 ambientCG 4 + PolyHaven 17
      (CC0 라 법적 의무는 없으나 재현성·감사 대응에 필수) + 채택한 CC-BY/KOGL 각 장의
      **저자명·라이선스 URL·원본 페이지 URL**(→ `expanded/LICENSES.csv` 에 준비 완료).
- [ ] **`LICENSE` 파일 신설**(§4-D) — 코드/씬 스크립트용. 데이터(렌더 이미지·GT)는
      별도 `DATA_LICENSE` 로 분리 선언 권고. 렌더가 CC0 소스만 쓰므로 데이터 쪽은
      CC0 또는 CC-BY 선언이 가능하다(= 데이터셋 채택률에 직결되는 강점).
- [ ] **다운로드 스크립트 4종** — 제외 에셋의 재현 경로.
- [ ] **`assets/vegetation/` 부재 사유 고지** — README/DATASHEET 에
      "NVIDIA 약관상 재배포 불가, `download_vegetation.py` 로 재현" 명시.
- [ ] **합성 데이터 고지 + 생성 도구 명시** — Isaac Sim 4.5 / RTX PT.
      look_refs 채택 시 Gemini 사용 사실도.
- [ ] **기관 승인**(`ZZ_synthesis` §9.2 권고) — 식생 결선 후 배포 시.

### 6-D. 확인만 하면 되는 항목 (현재 청정)

- [x] 렌더 이미지 내 브랜드·실존 인물·NVIDIA 지오메트리 — §5 검수 완료, 0건
- [x] Quixel/Fab · Mixamo · RenderPeople · SMPL 계열 — 저장소 전체 참조 0건
- [x] 로드뷰 3사(네이버·카카오·구글) 이미지 — 참조 0건
- [x] NoAI 태그 에셋 — 0건 (PolyHaven·ambientCG 모두 CC0)
- [x] NC(비상업) 라이선스 — 0건
- [x] git 히스토리 내 USD/EXR/대용량 바이너리 — 0건 (§3-B)

---

## 7. `[미확인]` 항목

추측으로 메우지 않고 그대로 남긴다.

1. **`look_refs/` 이미지의 실제 생성 표면** — `gemini.google.com`(소비자 앱)인지
   `aistudio.google.com`(AI Studio)인지. `scene19_prompts.md` 가 둘 다 안내해 특정 불가.
   **§1-B 판정이 이 한 가지로 갈린다. 최우선 확인 대상.**
2. **`everytime-1784886395380.jpg` 의 실제 취득 경로** — 파일명·해상도(1280×960)·EXIF
   제거 상태가 커뮤니티 앱 경유를 강하게 시사하나, 촬영자 본인이 앱에 올렸다 되받은
   가능성도 배제할 수 없다. **본인 촬영이면 §1-A-1 은 해소된다.**
3. **NVIDIA Omniverse License Agreement 의 "User Generated Content" 절 원문** —
   `docs.omniverse.nvidia.com` 이 자동 접근을 HTTP 403 으로 차단(UA 변경·헤더 보강 모두 실패).
   상위 SLA 의 "publicly accessible software repositories" 금지 조항과
   Product-Specific Terms(2026-04-15판) 전문은 nvidia.com 에서 확보했으나,
   **"사용자가 Omniverse 로 만든 산출물을 배포할 수 있다"는 명시적 허용 문구는 원문 미확인.**
   → 현재 정책(이미지만 공개, USD 미배포)은 이 미확인과 무관하게 안전한 쪽이다.
4. **NVIDIA S3 `Assets/Vegetation/` 에 적용되는 개별 에셋 라이선스** — 버킷 내
   LICENSE 파일 부재를 404 로 확인. 개별 에셋 단위 약관이 별도로 존재하는지 미확인.
5. **ambientCG 의 AI 학습 명시 입장** — 라이선스 페이지가 기계학습을 언급하지 않는다.
   CC0 이므로 법적으로는 제한 근거가 없으나 PolyHaven 같은 **명시적 허용 문구는 없다.**
6. **`NegObsGround.mdl` BSDF 블록이 OmniPBRBase 소스 이식인지 동작 재현인지**(§3-D) —
   원본 `OmniPBRBase.mdl` 을 대조하지 못했다(Isaac Sim 설치본 미접근 · GPU 실행 금지 제약).
7. **`Docs/reference_photos/expanded/` 의 최종 용도** — 실사 기준군(`@real`) 확장용인지,
   씬 설계 참조용인지, 둘 다인지. `scripts/imgstats.py` 는 아직 `Docs/reference_photos/*.jpg`
   (최상위 2장)만 가리킨다. **용도에 따라 §1-C 의 BY-SA 판정 강도가 달라진다.**

---

## 부록 — 감사 재현 명령

```bash
cd /home/vislab/Desktop/work_sy/Practice_NegObs

# 추적 바이너리 전수
git ls-files | grep -Ei '\.(jpg|jpeg|png|exr|hdr|usd|usda|usdc|usdz|mdl|obj|fbx|gltf|glb)$'

# 히스토리에 한 번이라도 추가된 바이너리
git log --all --diff-filter=A --name-only --pretty=format:'@@%h|%ad|%s' --date=short \
  | grep -Ei '^.*\.(jpg|png|exr|usd|usdc|mdl|zip)$' | sort -u

# 푸시 여부
git branch -r --contains <commit>

# ignore 실효성
git check-ignore -v <path>

# 씬이 실제로 쓰는 텍스처 역할
grep -rhoE '"[A-Za-z0-9_]+_(diff|nor|nor_dx|rough)\.(jpg|png)"' scenes/ scene_common.py \
  | tr -d '"' | sed -E 's/_(diff|nor_dx|nor|rough)\.(jpg|png)$//' | sort -u

# 식생 결선 여부
grep -rn "vegetation\|Japanese_Cherry\|Boxwood\|Yellow_Pine" --include=*.py . \
  | grep -v download_vegetation.py

# expanded 라이선스 대장 검증
python3 -c "
import csv,os
os.chdir('Docs/reference_photos/expanded')
rows=list(csv.DictReader(open('LICENSES.csv')))
disk={f for f in os.listdir('.') if f.lower().endswith('.jpg')}
print(len(rows), 'rows;', 'diff:', disk ^ {r['file'] for r in rows})
"
```

확인한 라이선스 원문 URL (전부 2026-07-28 접속):
- https://polyhaven.com/license
- https://docs.ambientcg.com/license/ (← `https://ambientcg.com/license` 302 리다이렉트)
- https://www.nvidia.com/en-us/agreements/enterprise-software/nvidia-software-license-agreement/
- https://www.nvidia.com/en-us/agreements/enterprise-software/product-specific-terms-for-omniverse/
- https://policies.google.com/terms/generative-ai/archive/20230809
- https://ai.google.dev/gemini-api/terms
- https://www.kogl.or.kr/info/license.do

---

## [해소] B. `look_refs/` 17장 — 사용자 확인으로 종결 (2026-07-28)

**사용자 확인: Google AI Studio(`aistudio.google.com`)를 통해 생성. 소비자앱 아님, API 아님.**

감사 §1-B 가 판정을 두 갈래로 남긴 항목이 이로써 닫힌다.

| 표면 | 해당 조항 | 우리 사용에 대한 판정 |
|---|---|---|
| `gemini.google.com` (소비자앱) | 생성형 AI 추가 서비스 약관: *"You may not use the Services to **develop machine learning models** or related technology."* | 저촉 — 이 프로젝트 목적 자체가 ML 학습 데이터 생성 |
| **AI Studio / API (실제 사용 표면)** | 개발자 약관: *"models that **compete with** the Services"* 로 한정 | **무관** — 우리 모델은 로봇 비가시 낙차 추정기로 Gemini 와 경쟁 관계가 아니다 |

**결론: `look_refs/` 17장은 현행대로 유지·공개 가능.**

부기 — 이 판정의 근거는 "AI Studio 는 개발자 표면이므로 소비자앱 조항이 아니라
개발자 약관이 적용된다"는 것이다. 약관은 개정되므로 **논문 투고 시점에 재확인**할 것.
또한 나노바나나 산출물은 **레퍼런스(재질·조명·미장센 참고)로만 쓰였고 학습 데이터에
직접 들어가지 않는다** — 시점·기하·GT 는 전부 Isaac 에서 결정된다(README 규약).
이 점이 판정을 한층 더 안전하게 만든다.
