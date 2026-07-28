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
