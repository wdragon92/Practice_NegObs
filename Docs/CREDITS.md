# CREDITS — 외부 에셋 출처·라이선스

`Docs/briefs/realism_brief_v1.md` 원칙 2에 따라 **CC0 / MIT-0 / CC-BY** 만 사용한다.
담당자별로 자기 절(節)에만 추가할 것 — 다른 담당자 절은 수정하지 않는다.

---

## 하늘 HDRI (담당: 하늘 조달, 2026-07-28)

조달 스크립트 `assets/download_sky.py` · 선정·검증 보고서 `Docs/reports/sky_procurement_v1.md`

### 출처

**Poly Haven** (https://polyhaven.com) — 전 에셋 **CC0 1.0 (Public Domain Dedication)**.

라이선스 페이지 https://polyhaven.com/license 원문 인용 (2026-07-28 확인):

> All assets (HDRIs, textures and 3D models) on this site are the original work of Poly Haven
> staff, or artists who willingly and directly donate/sell their work to Poly Haven.
> Our assets are all licensed as CC0, which is effectively Public Domain even in jurisdictions
> that do not support the Public Domain. […] In other words: **You can use our assets for any
> purpose, including commercial work.** You do not need to give credit or attribution when
> using them (although it is appreciated). **You can redistribute them**, share them around,
> include them when sharing your own work, or even in a product you sell.

기계학습 활용이 라이선스 페이지에 명시적으로 언급된다:

> we've heard from numerous data scientists, software developers, automotive engineers and
> **AI researchers all using our assets in their work**, which simply wouldn't be possible with
> more restrictive (even open source) licenses.

CC0 는 저작자 표시 의무가 없다. 아래 표기는 의무가 아니라 **감사 표시이자 재현성 기록**이다.

### 사용 파일

| 파일 (`assets/`) | Poly Haven slug / 에셋 페이지 | 라이선스 | 비고 |
|---|---|---|---|
| `qwantani_noon_puresky_4k.exr` | [`qwantani_noon_puresky`](https://polyhaven.com/a/qwantani_noon_puresky) | CC0 1.0 | 기존 기본 HDRI(무운 청천) |
| `qwantani_dawn_puresky_4k.exr` | [`qwantani_dawn_puresky`](https://polyhaven.com/a/qwantani_dawn_puresky) | CC0 1.0 | 기존 |
| `kloofendal_overcast_4k.exr` | [`kloofendal_overcast`](https://polyhaven.com/a/kloofendal_overcast) | CC0 1.0 | 기존(배치1 C1·C4 무태양 프로파일) |
| **`kloofendal_48d_partly_cloudy_puresky_4k.exr`** | [`kloofendal_48d_partly_cloudy_puresky`](https://polyhaven.com/a/kloofendal_48d_partly_cloudy_puresky) | CC0 1.0 | **신규** 산개 적운 · 태양고도 47.86° |
| **`sunflowers_puresky_4k.exr`** | [`sunflowers_puresky`](https://polyhaven.com/a/sunflowers_puresky) | CC0 1.0 | **신규** 층적운 밴드+권층운 · 43.02° |
| **`farm_field_puresky_4k.exr`** | [`farm_field_puresky`](https://polyhaven.com/a/farm_field_puresky) | CC0 1.0 | **신규** 부분 흐림(태양 차폐) · 49.53° |

파생본 `*_lookfix.exr` 은 위 원본을 `scene_common.ensure_noon_lookfix`
(태양 디스크 캡 + 지평 리프트)로 가공한 것이며, CC0 원본의 2차 저작물이므로 배포 제약이 없다.
`*_sunless.exr` 도 동일하다.

---

## 식생 에셋 — 나무·관목 USD (담당: 식생 조달, 2026-07-28)

조달 스크립트 `assets/download_vegetation.py` · 저장 위치 `assets/vegetation/`

### 출처 및 라이선스 — **CC0 가 아니다. 주의 필요**

**NVIDIA Omniverse 콘텐츠 S3 버킷** (인증 없이 공개 열람·다운로드 가능):
`https://omniverse-content-production.s3.us-west-2.amazonaws.com/Assets/Vegetation/`

이 문서 서두의 "CC0 / MIT-0 / CC-BY 만 사용한다" 원칙의 **예외**다.
`ZZ_synthesis.md` §9.2 · §10.6 의 판정을 그대로 따른다:

| 항목 | 판정 |
|---|---|
| ML 학습 데이터 생성 | **✅ 허용** — NVIDIA 약관에 ML 학습 금지 조항 없음(Replicator 의 제품 목적 자체가 합성학습데이터) |
| 렌더 이미지 공개 | **✅ 가능** |
| **USD·텍스처 원본 재배포** | **❌ 금지** — "publicly accessible repositories" 배포 금지 조항 |

**→ `assets/vegetation/` 은 반드시 `.gitignore` 로 제외한다.**
공개 시에는 **이미지 + 씬 스크립트만** 포함하고 USD 는 넣지 않는다. 기관 승인 권고.
(주의: `Assets/Isaac/*/Environments` 의 Rivermark 등은 별도로 **"수정 금지" Limited Use Content**
다. 지금 받은 `Assets/Vegetation/` 은 그 범주가 아니지만, 다른 폴더로 확장할 때 재확인할 것.)

### 사용 파일

| 파일 (`assets/vegetation/`) | 수종 | 크기 | 높이 | 삼각형 | 비고 |
|---|---|---|---|---|---|
| `Trees/Japanese_Cherry.usd` | 벚나무 | 35.5 MB | 4.64 m | 269,945 | **1단계 목표물.** 꽃이 실제 지오메트리 |
| `Trees/Yellow_Pine.usd` | 소나무류 | 15.9 MB | 26.99 m | 112,736 | 성목. PointInstancer 8개 |
| `Trees/White_Pine.usd` | 소나무류 | 0.8 MB | 2.35 m | 10,846 | 유목/원경 LOD. Yellow_Pine 과 재질 공유 |
| `Shrub/Boxwood.usd` | 회양목 | 24.2 MB | 0.74 m | 177,721 | 보도 화단·연석 폐색용 |
| `Trees/materials/*.mdl` (4) | — | 5.7 KB | | | OmniPBR 래퍼 |
| `Shrub/materials/*.mdl` (1) | — | 1.5 KB | | | |
| `*/materials/textures/*.png` (10) | — | 51.0 MB | | | 8/16-bit PNG |

합계 20 파일 / 128.2 MB. 전 파일 헤더 검증(`PXR-USDC` / `\x89PNG` / `mdl `) 및
USD→MDL→텍스처 3단 참조 해석 확인 완료.

### 디렉터리 구조를 바꾸지 말 것

종속 참조가 전부 **상대 경로**이며, `Shrub/Boxwood.usd` 는 폴더를 벗어나
`../Trees/materials/bark3.mdl` 을 참조한다. S3 의 `Assets/Vegetation/` 구조를
그대로 미러링해야 하며, 평평하게 펼치면 깨진다. 자세한 내용은
`assets/download_vegetation.py` 의 모듈 docstring 참조.

### 한국 가로수 수종 대조표 (S3 보유 여부 — 직접 열거 확인)

| 한국 수종 | S3 대응 | 판정 |
|---|---|---|
| 벚나무 | `Trees/Japanese_Cherry.usd` | ✅ **확보** |
| 양버즘나무(플라타너스) | `Trees/Sycamore.usd` | ✅ 있음 — 수피 텍스처가 Platanus 특유의 얼룩 박리피로 확인됨 |
| 향나무 | `Trees/Chinese_Juniper.usd` | ✅ 있음 (*Juniperus chinensis* — 동일 종) |
| 단풍나무류 | `Japanese_Maple` / `Red_Maple` / `Sugar_Maple` (+`_Fall`) | ✅ 있음 |
| 소나무 | `Yellow_Pine` / `White_Pine` | ✅ **확보** (단 *P. densiflora* 는 아님 — 적갈색 상부 수피 미재현) |
| 회양목(관목) | `Shrub/Boxwood.usd` | ✅ **확보** |
| 개나리(관목) | `Shrub/Forsythia.usd` | ✅ 있음 |
| 무궁화 | `Shrub/Hibiscus.usd` | ✅ 있음 |
| 목련 | `Shrub/Magnolia.usd` | ✅ 있음 |
| 철쭉·영산홍 | `Shrub/Rhododendron.usd` | ✅ 있음 |
| **은행나무** | — | ❌ **없음** (`ginkgo`/`maidenhair` 전체 목록 0건) |
| **느티나무** | — | ❌ **없음** (`zelkova`/`keyaki` 0건). 동과(느릅나무과) `Elm_Sapling` 이 최근사 |
| **이팝나무** | — | ❌ **없음** (`chionanthus`/`fringe` 0건). 흰 꽃차례는 `Kousa_Dogwood`/`Service_Berry` 로 대체 가능 |
| **배롱나무** | — | ❌ **없음** (`lagerstroemia`/`crape` 0건) |
| **메타세쿼이아** | — | ❌ **없음** (`metasequoia`/`sequoia`/`redwood` 0건) |

부족분(특히 은행·느티)은 별도 조달 또는 절차 생성이 필요하다.
`ZZ_synthesis.md` §10.1 의 "목록이 온대 서구종 중심"이라는 정직한 한계 서술과 일치한다.
