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

---

## 실사 레퍼런스 사진 — 한국 보행환경 54장 (담당: 실사 레퍼런스 확보, 2026-07-28)

저장 위치 `Docs/reference_photos/expanded/` · 기계판독 대장 `Docs/reference_photos/expanded/LICENSES.csv` · 보고서 `Docs/reports/real_reference_expansion.md`

### 출처

**Wikimedia Commons** (https://commons.wikimedia.org) 단일 출처. MediaWiki API `action=query&prop=imageinfo&iiprop=extmetadata` 로 **파일별 라이선스·저작자·촬영일을 이미지와 함께 수집**했다. 각 파일의 Commons 파일설명 페이지 URL 이 대장 CSV 의 `commons_page` 컬럼에 있다.

수집 대상은 **한국 도시 보행환경**(보도·계단·골목·광장·공원·하천 제방·캠퍼스), 주간·보행자 눈높이·옥외로 한정했다. 후보 2,637장 → 라이선스/해상도/메타 필터 1,860장 → 상위 150장 다운로드 → **육안 전수 심사** → 54장. 심사에서 실내·야간·항공부감·박무·설경·과보정(HDR)·일출/황혼·인물사진, 그리고 검색질의에 섞여 들어온 **일본 사진 3장**을 배제했다.

**로드뷰(구글·네이버·카카오)는 한 장도 사용하지 않았다** — 3사 모두 약관상 저장·DB화 금지(근거: `Docs/surveys/realism_gap_2026-07-28/E_realism_measurement_protocol.md` §5.2).

### 라이선스 — **CC-BY-SA 포함. 이 문서 서두 원칙의 예외다**

서두 원칙은 "CC0 / MIT-0 / CC-BY 만" 이지만, 아래 54장 중 **35장이 CC BY-SA(동일조건변경허락)** 다. 식생 에셋 절과 동일하게 **명시적 예외**로 기록한다.

| 라이선스 | 장수 | 재배포 | 비고 |
|---|---|---|---|
| CC BY-SA 4.0 | 30 | ✅ | SA — 2차적저작물은 동일 조건 |
| CC0 | 8 | ✅ | 제약 없음 |
| CC BY 4.0 | 7 | ✅ | 출처표시 |
| CC BY-SA 3.0 | 3 | ✅ | SA |
| KOGL Type 1 | 2 | ✅ | 공공누리 1유형 — 출처표시, 상업이용 가능 |
| CC BY 2.0 | 1 | ✅ | 출처표시 |
| CC BY-SA 2.0 kr | 1 | ✅ | SA (한국 포팅) |
| CC BY-SA 2.5 | 1 | ✅ | SA |
| CC BY-SA 2.0 | 1 | ✅ | SA |

- 비상업(NC)·변경금지(ND)·라이선스 불명 파일은 **0장**이다. 수집 단계에서 화이트리스트 정규식으로 선차단하고 `Restrictions` 필드가 비어있지 않은 파일도 전부 폐기했다.

- ⚠️ **취급 주의**: (a) 통계량 측정은 2차적저작물 작성이 아니므로 SA 조항이 발동하지 않는다. (b) 그러나 수집본은 Commons 가 생성한 **리사이즈본(장변 1600px)** 이므로 엄밀히는 2차적저작물이며, 재배포 시 BY-SA 로 배포해야 한다. (c) **논문 figure 게재 시 BY-SA 표기 의무**가 있다.

- **권고**: 공개 배포·논문 figure 에는 **CC0/CC BY/KOGL 18장만** 사용하고 BY-SA 36장은 내부 측정 참조용으로 둔다. 이 분리가 측정 결론을 바꾸지 않음은 보고서 §2.4 에서 확인했다.

### 사용 파일 (54장)

`LICENSES.csv` 가 정본이며 아래는 사람이 읽기 위한 요약이다. `original_url` 컬럼으로 전량 재수집이 가능하다.

| 파일 (`Docs/reference_photos/expanded/`) | 라이선스 | 저작자 | 촬영일 |
|---|---|---|---|
| `wc001_ccby20_3a419a_Korea_Damyang_Juknogwon_Bamboo_Garden_04.jpg` | CC BY 2.0 | Byungjoon Kim | 2008-11-01 0… |
| `wc005_ccby40_caddc6_삼일공원_1.jpg` | CC BY 4.0 | 씽푸미니 | Taken on 31 … |
| `wc007_ccbysa40_276551_Korean_War_Veterans_Plaza_1.jpg` | CC BY-SA 4.0 | Louis Minsky | 2023-10-25 0… |
| `wc010_cc0_120ca9_Hwaseong_City_Hwaseong_ro_Road_Crosswalk_Sign_20240803.jpg` | CC0 | LandAndTree | Taken on 3 A… |
| `wc011_cc0_00294c_20200806_164648_things_places_in_south_korea_IMG_9615.jpg` | CC0 | Choi Kwang-mo | 2020-08-07 1… |
| `wc012_ccbysa40_48846b_Stairs_of_Pyeongchon_Central_Park.jpg` | CC BY-SA 4.0 | BoeunKim | 2018-04-21 1… |
| `wc015_ccbysa40_948e17_Stairs_of_Pyeongchon_Central_Park4.jpg` | CC BY-SA 4.0 | BoeunKim | 2018-04-21 1… |
| `wc016_ccbysa40_bf9d96_Stairs_of_Pyeongchon_Central_Park5.jpg` | CC BY-SA 4.0 | BoeunKim | 2018-04-21 1… |
| `wc018_ccbysa40_0bbb83_Stairs_of_Pyeongchon_Central_Park7.jpg` | CC BY-SA 4.0 | BoeunKim | 2018-04-21 1… |
| `wc022_ccbysa20kr_67222d_보성체육공원_축구경기장_02.jpg` | CC BY-SA 2.0 kr | Hwan | Taken on 19 … |
| `wc023_ccby40_d30a1d_행당역_대현산공원_4.jpg` | CC BY 4.0 | kepper | Taken on 20 … |
| `wc024_ccby40_f9b447_행당역_대현산공원_5.jpg` | CC BY 4.0 | kepper | Taken on 20 … |
| `wc025_ccby40_2bb71b_행당역_대현산공원_8.jpg` | CC BY 4.0 | kepper | Taken on 20 … |
| `wc026_cc0_88f760_20200806_165202_things_places_in_south_korea_IMG_9627.jpg` | CC0 | Choi Kwang-mo | 2020-08-07 1… |
| `wc036_ccbysa40_ebeedb_Seoul_7017_Skypark_East_Entrance.jpg` | CC BY-SA 4.0 | Keneckert | Taken on 21 … |
| `wc040_ccbysa40_e3e016_Jeongdong_gil_정동길_One_of_the_most_popular_pedestrian_alleys.jpg` | CC BY-SA 4.0 | Joongwon Lee - SKKU DOA | 2019-06-24 1… |
| `wc041_cc0_6c17b1_Jeongwangsingil_ro_Singil_dong_20240719.jpg` | CC0 | LandAndTree | 2024-07-19 |
| `wc042_cc0_52052e_Okcheon_County_Jungang_ro_Okcheon_Bridge_20240730_02.jpg` | CC0 | LandAndTree | 2024-07-30 |
| `wc043_cc0_ead8bb_Okcheon_County_Jungang_ro_Okcheon_Bridge_20240730_03.jpg` | CC0 | LandAndTree | 2024-07-30 |
| `wc047_cc0_a694ef_Row_of_trees_on_sidewalk.jpg` | CC0 | 최광모 | 2015-04-18 1… |
| `wc048_ccby40_7937de_Yeonamyulgeum_ro_Sidewalk_in_Cheonan_City_20270720.jpg` | CC BY 4.0 | LandAndTree | 2024-07-20 |
| `wc049_ccbysa25_52ecfd_Around_Samneung_Park.jpg` | CC BY-SA 2.5 | Jérôme Banal ( Eden2004 ) | 2005-09-10 |
| `wc055_cc0_45a890_Cheonggyecheon_Seoul_Cheonggyecheon2321.jpg` | CC0 | lumoplank | 2024-09-28 |
| `wc065_ccbysa40_d5e921_Daejeon_Seo_gu_Munjeong_ro_20260315_01.jpg` | CC BY-SA 4.0 | Treeinkr | 2026-03-15 |
| `wc067_ccbysa40_5b6998_Gwanghwamun_Square_4.jpg` | CC BY-SA 4.0 | kallerna | 2022-11-29 1… |
| `wc072_ccbysa40_74112b_Insa_dong_인사동_October_1_2020_10.jpg` | CC BY-SA 4.0 | S h y numis | 2020-10-01 1… |
| `wc073_ccbysa40_2a296b_Insa_dong_인사동_October_1_2020_16.jpg` | CC BY-SA 4.0 | S h y numis | 2020-10-01 1… |
| `wc074_ccbysa40_6f92aa_Insa_dong_인사동_October_1_2020_21.jpg` | CC BY-SA 4.0 | S h y numis | 2020-10-01 1… |
| `wc076_ccbysa40_44b4a5_Insa_dong_인사동_October_1_2020_6.jpg` | CC BY-SA 4.0 | S h y numis | 2020-10-01 1… |
| `wc077_ccbysa40_a08cf2_Insa_dong_인사동_October_1_2020_7.jpg` | CC BY-SA 4.0 | S h y numis | 2020-10-01 1… |
| `wc078_ccbysa40_f07bff_Insa_dong_인사동_October_1_2020_8.jpg` | CC BY-SA 4.0 | S h y numis | 2020-10-01 1… |
| `wc080_ccbysa40_dbd180_Bukchon_Hanok_Village_북촌_한옥마을_October_1_2020_15.jpg` | CC BY-SA 4.0 | S h y numis | 2020-10-01 1… |
| `wc081_ccbysa40_19851c_Hongdae_Main_Road_Seoul.jpg` | CC BY-SA 4.0 | Ken Eckert | 2015-06-12 1… |
| `wc083_ccbysa30_86f14b_Korea_Seoul_Changdeokgung_Donginmun_01.jpg` | CC BY-SA 3.0 | Alain Seguin at Flickr , from Ottawa, Canada | 2008-04-15 |
| `wc084_ccbysa40_ee344e_A_paper_wholesaler_in_Euljiro_printing_alley_paper_delivery.jpg` | CC BY-SA 4.0 | Aaaatu | 2021-10-21 1… |
| `wc087_ccbysa40_2cb04a_Bukchon_Hanok_Village_북촌_한옥마을_October_1_2020_10.jpg` | CC BY-SA 4.0 | S h y numis | 2020-10-01 1… |
| `wc088_ccbysa40_08f8b7_Bukchon_Hanok_Village_북촌_한옥마을_October_1_2020_11.jpg` | CC BY-SA 4.0 | S h y numis | 2020-10-01 1… |
| `wc091_ccbysa40_323022_Bukchon_Hanok_Village_북촌_한옥마을_October_1_2020_16.jpg` | CC BY-SA 4.0 | S h y numis | 2020-10-01 1… |
| `wc093_ccbysa40_2dd1ca_Bukchon_Hanok_Village_북촌_한옥마을_October_1_2020_18.jpg` | CC BY-SA 4.0 | S h y numis | 2020-10-01 1… |
| `wc107_ccbysa40_c20150_KAIST_s_campus_road.jpg` | CC BY-SA 4.0 | AhmadElq | 2019-09-08 1… |
| `wc108_ccbysa30_1c35fa_Buildings_near_konkuk_university_01.jpg` | CC BY-SA 3.0 | myself ( User:Piotrus ) | 2013-04-11 1… |
| `wc110_ccbysa20_8fdc88_Street_in_Seoul_unidentified.jpg` | CC BY-SA 2.0 | Korea.net / Korean Culture and Information Servi… | 2010-10-15 1… |
| `wc115_ccbysa30_f0a0bb_Plastic_bottles_on_wooden_road.jpg` | CC BY-SA 3.0 | Clementina | 2010-09-16 |
| `wc129_ccbysa40_60c8e4_Bukchon_ro_11_gil_03.jpg` | CC BY-SA 4.0 | Tristan Surtel | 2019-08-01 1… |
| `wc130_ccbysa40_39482f_Bukchon_ro_11_gil_04.jpg` | CC BY-SA 4.0 | Tristan Surtel | 2019-08-01 1… |
| `wc131_ccbysa40_faa870_Bukchon_ro_11_gil.jpg` | CC BY-SA 4.0 | Tristan Surtel | 2019-08-01 1… |
| `wc133_ccbysa40_a2faea_Stairs_in_the_Gamcheon_Culture_Village_1.jpg` | CC BY-SA 4.0 | Christophe95 | 2018-09-28 0… |
| `wc134_ccbysa40_f87edc_Stairs_in_the_Gamcheon_Culture_Village_2.jpg` | CC BY-SA 4.0 | Christophe95 | 2018-09-28 0… |
| `wc135_ccby40_6b9f08_Lee_Han_Yeol_Memorial_on_Yonsei_Campus.jpg` | CC BY 4.0 | Thinkinglex | 2024-12-17 2… |
| `wc136_ccbysa40_09e976_Yonsei_University_campus.jpg` | CC BY-SA 4.0 | Christian Bolz | 2015-12-13 1… |
| `wc137_ccby40_f7669b_Yonsei_University_International_Campus_Underwood_Memorial_Li.jpg` | CC BY 4.0 | 기나ㅏㄴ | 2024-05-20 1… |
| `wc140_ccbysa40_a31fec_Sidewalk_and_Yeomgokdong_Guryongsa_BS_in_Yangjaedaero_Yeomgo.jpg` | CC BY-SA 4.0 | Jhcbs1019 | 2019-07-12 1… |
| `wc144_kogltype1_2f9c2b_Jongno_Seoul_South_Korea_01.jpg` | KOGL Type 1 | KOREA TOURISM ORGANIZATION (한국관광공사) | 2016-06-18 |
| `wc145_kogltype1_dfb314_Jongno_Seoul_South_Korea_02.jpg` | KOGL Type 1 | KOREA TOURISM ORGANIZATION (한국관광공사) | 2016-06-18 |

## 식생·잔해 에셋 확장 — 낙엽·잡석·관목 USD (담당: 에셋 전수 조사·조달, 2026-07-28)

조달 스크립트 `assets/download_vegetation.py` (카테고리별 `--only` 지원) ·
저장 위치 `assets/vegetation/` · 감사 보고 `Docs/reports/asset_audit_v1.md`

### 출처 및 라이선스

위 "식생 에셋" 절과 **동일한 NVIDIA Omniverse S3 버킷 · 동일한 라이선스 판정**이다.
즉 ML 학습 데이터 생성 ✅ / 렌더 이미지 공개 ✅ / **USD·텍스처 원본 재배포 ❌**.
`.gitignore` 의 `assets/vegetation/` 규칙이 신규 `Debris/`·`Rocks/` 하위도
그대로 커버함을 `git check-ignore` 로 확인했다.

### 추가 조달 파일

**낙엽 (`Debris/`) — 평면 텍스처 `leaf_ground` 를 대체하는 실제 잎 지오메트리**

| 파일 | 크기 | 네이티브 치수 (X×Y×Z, m) | 삼각형 | 유효 피복 |
|---|---|---|---|---|
| `Debris/fallcluster1.usd` | 0.51 MB | 0.419 × 0.395 × 0.042 | 9,175 | 0.0628 m² (15.9개/m²) |
| `Debris/fallcluster2.usd` | 0.18 MB | 0.241 × 0.266 × 0.042 | 2,980 | 0.0242 m² (41.4개/m²) |
| `Debris/maplefall1.usd` | 0.05 MB | 0.103 × 0.172 × 0.023 | 631 | 0.0051 m² |
| `Debris/oakfall1.usd` | 0.04 MB | 0.080 × 0.175 × 0.023 | 496 | 0.0030 m² |
| `Debris/oakfall2.usd` | 0.04 MB | 0.094 × 0.190 × 0.018 | 582 | 0.0038 m² |
| `Debris/materials/fallleaves.mdl` + 텍스처 3 | 66.4 MB | — | | 5종 공유 |

**잡석 (`Rocks/`) — `_oriented_box` 랜덤 박스를 대체**

| 파일 | 네이티브 치수 (m) | z최소 | 삼각형 |
|---|---|---|---|
| `Rocks/rock_small_01.usda` | 0.314 × 0.302 × 0.253 | −0.128 | 268 |
| `Rocks/rock_small_15.usda` | 0.228 × 0.224 × 0.173 | −0.084 | 410 |
| `Rocks/rock_small_08.usda` | 0.223 × 0.197 × 0.162 | −0.086 | 438 |
| `Rocks/rock_small_10.usda` | 0.162 × 0.151 × 0.116 | −0.055 | 374 |
| `Rocks/rock_small_09.usda` | 0.128 × 0.113 × 0.067 | −0.031 | 426 |
| `Rocks/textures/*.jpg` (15) | | | basecolor/normal/orm |

`Rocks/*.usda` 는 재질을 `@OmniPBR.mdl@` 로 **검색 경로 참조**한다(상대 경로 아님).
Isaac 이 동봉하므로 MDL 조달 불요. 원점이 **바위 중심**이라 z최소가 음수다 —
지면 배치 시 보정 필요.

**관목 (`Shrub/`) — `build_hedge`(20씬)·`build_planter`(17씬) 대체**

| 파일 | 국명 | 크기 | 네이티브 치수 (m) | 삼각형 |
|---|---|---|---|---|
| `Shrub/Privet.usd` | 쥐똥나무 | 19.6 MB | 1.704 × 1.638 × 1.113 | 147,380 |
| `Shrub/Rhododendron.usd` | 철쭉 | 7.15 MB | 2.547 × 2.372 × 2.013 | 54,704 |
| `Shrub/Juniper.usd` | 향나무 | 29.7 MB | 0.455 × 0.451 × 0.898 | 199,580 |
| `Shrub/Burning_Bush.usd` | 화살나무 | 18.7 MB | 2.642 × 2.601 × 1.604 | 140,570 |
| `Shrub/Forsythia.usd` | 개나리 | 53.7 MB | 3.539 × 3.650 × 2.317 | 403,841 |
| `Shrub/materials/*.mdl` (4 신규) + 텍스처 8 | | 25.4 MB | | |
| `Trees/materials/TreeBark_01.mdl` + 텍스처 3 | | 16.4 MB | | Rhododendron 줄기 |

관목 5종 전부 줄기 재질로 **`../Trees/materials/`** 를 참조한다
(Privet·Juniper·Burning_Bush·Forsythia → `bark3.mdl`, Rhododendron → `TreeBark_01.mdl`).
디렉터리 구조를 평평하게 펼치면 깨진다 — 위 절의 경고가 그대로 적용된다.

### 합계

`assets/vegetation/` = USD 19개 포함 **353 MB**
(Debris 67.3 · Rocks 1.9 · Shrub 172.0 · Trees 111.4 MB).
전 파일 헤더 검증(`PXR-USDC`/`#usda`/`\x89PNG`/`\xff\xd8\xff`/`mdl `) 통과.
USD→MDL→텍스처 3단 참조 **113개 전부 해석 성공, 미해결 0건**.

### 조달하지 않은 것과 그 사유

| 대상 | 사유 |
|---|---|
| `Leaves/` 5종 | `Debris/` 와 **동일 지오메트리**인데 `cluster_2.usd` 가 S3 에 없는 `./basecolor.jpg` 를 참조하고 normal/roughness 슬롯이 교차돼 있다 |
| `Plant_Tropical/` 17종 | 야자·바나나·열대 양치·용설란 — 한국 노지 환경 부적합 (종별 사유는 감사 보고 §3-b) |
| `Shrub/Century`·`Thevetia`·`Oleander`·`Acacia` | 사막 다육 / 열대 / 남부 한정 / 사바나 아카시아(한국 아까시나무와 다른 나무) |
| `Trees/` 41종 | 이번 범위 밖. 추가 우선순위는 감사 보고 §3-d (1위 `Sycamore` 7.8 MB, 2위 `Chinese_Juniper` 3.7 MB — 둘 다 초경량인데 미보유) |

---
