# 문서 정합성 감사 v1 — 사실화 라운드 정정 반영 점검

- 작성 2026-07-28 · 담당: 문서 정합성 감사관 · **쓰기 파일은 이 문서 하나뿐**(다른 문서·코드 미수정)
- 대상: `README.md` · `Docs/INDEX.md` · `Docs/briefs/realism_brief_v1.md`(본문+rev.1) ·
  `Docs/audit_v4/user_feedback_v5_1.md` · `Docs/reports/` 전 13건 ·
  `Docs/surveys/realism_gap_2026-07-28/` ZZ·A~I · `scene_common.py` 주석 · `scripts/imgstats.py` 주석 ·
  `.gitignore` · `Docs/CREDITS.md` · git 상태
- 방법: 전문 대조 + 코드 실행 실측(`import scene_common` · `git ls-files` · `git log`). **GPU 미사용.**

---

## 0. 한 줄 결론

**정정 10건 중 코드에는 대부분 반영됐고, 문서에는 대부분 반영되지 않았다.**
그리고 **새 세션이 읽도록 지정된 3개 문서(README → INDEX → ZZ_synthesis)가 이 라운드의
모든 산출물보다 오래됐다** — 지정된 순서를 그대로 따르면 라운드가 존재했다는 사실 자체에
도달하지 못한다.

| 정정 항목 | 코드 | 문서 |
|---|---|---|
| 1. scene01 `make_pbr` 예외 → 리팩터로 해소 | ✅ `a66c1ad` | ❌ 4곳 잔존 |
| 2. 죽은 픽셀 하늘 67~74% → 13~39% | ❌ 주석 2곳 잔존 | ❌ 5곳 잔존 |
| 3. E4 subdiv `refinementLevel=0` 세분 없음 | — | ✅ 반영됨 |
| 4. 노이즈 플로어 씬별 | — | ✅ 제자리 정정 |
| 5. `ori_axis` 폐기 부당 | ✅ imgstats | ❌ baseline 잔존 |
| 6. `flat_gnd` 목표 근거 "실사 0.1" | ⚠ imgstats 내부 모순 | ❌ 4문서 9곳 잔존 |
| 7. 역할별 채도 "의도대로 작동" | ✅ `_SAT_KNEE` 0.30→0.18 | ❌ phase2 잔존 |
| 8. ZZ_synthesis 다수 서술 | — | ❌ 정정 표시 **0건** |
| 9. 잠정 베벨값 3/4 정정 | ⚠ 2/4만 I 권고와 일치 | ❌ brief rev.1 잔존 |
| 10. 연석 100~250 → 150~225 | — | ❌ ZZ §9.3 잔존 |

---

## 1. 치명 — 다음 세션을 잘못된 방향으로 이끄는 것

### F1. 인수인계 경로가 최신 상태에 도달하지 못한다 (도달률 0)

파일 mtime 실측:

| 문서 | mtime | 성격 |
|---|---|---|
| `Docs/surveys/.../ZZ_synthesis.md` | **07-28 13:15** | 읽는 순서 3순위 = "여기서 시작" |
| `README.md` | **07-28 13:43** | 읽는 순서 진입점 |
| `Docs/INDEX.md` | **07-28 13:43** | 색인 |
| `Docs/reports/realism_baseline.md` | 07-28 15:47 | ← 라운드 최초 산출물 |
| … 산출물 11건 … | 16:29 ~ 22:16 | |
| `Docs/reports/deadpixel_diag_0701.md` | **07-28 22:16** | 최신 |

**진입점 3개가 라운드 산출물 전부보다 오래됐다.**

- `README.md:92-101` "## 현 상태 (2026-07-28)" — *"전 33씬 최종 렌더·판정 종료. … 진행 중
  과제는 **사실성 격차**다. … 전 보고서와 실행계획: `Docs/surveys/realism_gap_2026-07-28/` —
  `ZZ_synthesis.md` 부터 읽을 것."*
  → 브랜치 `feat/realism-v1`, Phase 0/1 종료, Phase 2 게이트 미달, 신규 보고서 10건,
  코드 감사 치명 4건, 라이선스 감사 — **전부 언급 없음.**
- `README.md:105-109` 읽는 순서 3단계의 종착점이 `ZZ_synthesis.md` → **F2 로 이어진다.**
- `Docs/INDEX.md:3-4` 동일한 3단계.

**INDEX 미등재 목록 (실측 — `grep` 0건)**

| 미등재 | 비고 |
|---|---|
| `briefs/realism_brief_v1.md` | **이 라운드의 지시서 본체**. INDEX briefs 절에 없다 |
| `surveys/.../H_rtx_capability_verification.md` (1,109줄) | surveys 절이 A~G 만 나열 |
| `surveys/.../I_ks_dimension_verification.md` (590줄) | 동상 |
| `reports/realism_baseline.md` · `realism_phase1.md` · `realism_phase2.md` | reports 절이 3항목뿐 |
| `reports/deadpixel_diag_0701.md` · `deadpixel_diag_d3.md` | |
| `reports/const_color_texture_map.md` · `real_reference_expansion.md` | |
| `reports/license_audit_v1.md` · `code_audit_realism_v1.md` | |
| `reports/sky_procurement_v1.md` · `regression_tool_v1.md` | |
| `Docs/CREDITS.md` | 라이선스 원장인데 색인에 없다 |
| `Docs/reference_photos/expanded/` + `real_set_safe.txt` | INDEX:50-51 은 "참고사진 2장"만 적는다 |

**고칠 내용**
1. `README.md:92-101` 을 현 상태로 교체 — 브랜치 `feat/realism-v1`(origin/main 대비 **19 커밋 ahead**,
   미푸시), Phase 0·1 종료 / Phase 2 게이트 **미달**, 현재 `flat_gnd` = scene01 **5.59** ·
   scene07 **10.00** · sceneD3 **2.87**(라운드 `p2g4_on`), 다음 액션 = scene07 `gate_frame` 결정(§4-C1).
2. `README.md:105-109` 읽는 순서에 `Docs/briefs/realism_brief_v1.md`(본문 + **개정 이력 rev.1**)를
   2순위로 삽입하고, ZZ 는 "이력 문서(정정 있음)"로 강등.
3. `Docs/INDEX.md` 에 위 표 13건 등재 + 각 항목에 **유효 / 부분 정정 / 폐기** 표시.

---

### F2. 진입점 문서 `ZZ_synthesis.md` 에 정정 표시가 **한 건도 없다**

INDEX:31 이 *"`ZZ_synthesis.md` — **종합·실행계획. 여기서 시작**"* 이라고 지정한 문서에
이후 실측으로 반증된 서술이 최소 12건 살아 있다.

| 행 | 원문 | 고칠 내용 | 근거 |
|---|---|---|---|
| ZZ:83 | "MDL displacement \| G·F팀 \| **RTX 미지원 명시** \| **불가**" | **지원된다**(Kit 106.1, RT·PT 양쪽). 결론(정점 변위 우회)만 유지, **이유가 바뀜** — OmniPBR 에 displacement 입력이 없어서다 | `realism_phase1.md:303` |
| ZZ:86 | "cameraFStop/cameraISO는 106.5에 **없음**" | 이름만 다르고 **노출 3요소 전부 존재**: `/rtx/post/tonemap/{filmIso=100, cameraShutter=50, fNumber=5.0}`. 톤매핑 `op=6`(ACES) **이미 기본 활성** | `realism_phase1.md:304` |
| ZZ:81 | "`omni.sensors.nv.camera` ISP \| **확장 자체가 없음**" | `librtx.cameraisp.plugin.so` 는 **존재하고 로드된다**. 공개 API 만 없다 | `realism_phase1.md:305` |
| ZZ:352 | "`opacityThreshold` 기본값이 **0.0** 이라 … 잎이 전부 불투명 판때기" | 진범은 **`enable_opacity=false`**. 추가 함정 `opacity_mode` 기본 `mono_average` | `realism_phase1.md:306` |
| ZZ:356 | "`/rtx/pathtracing/spp` 기본값이 **1**" | **기본값은 64**. 우리 씬 코드가 명시적으로 1로 낮추고 있었다 | `realism_phase1.md:302` |
| ZZ:37 | "`assets/NegObsGround.mdl` … **33씬 중 0개에서 사용 중**" | 현재 지면·사면·구조물 계열 전체가 경유(3단 재질 정책). **다만 전역 승격은 불가로 확정** | `realism_phase1.md:315-321` |
| ZZ:294 | "연석: 경사형 100~150 mm / 수직형 **100~250 mm**" | **수직형 150~225(표준 150)**, 교량·터널 예외 250·**200 이하 권장**. 경사형 **100~155**. 100 mm 수직형은 국내 규격이 아니다 | `I_ks_dimension_verification.md:476-493` |
| ZZ:294 | (단면 정보 없음) | **사다리꼴이다** — 수직형 상150/하175, 경사형 상150/하200~220. 박스로 만들었다면 실루엣이 틀렸다. 모서리 반경 수직형 **R=10** / 경사형 **R=50~75**(베벨 아님, 실지오메트리) | `I:142-147, 486-497` |
| ZZ:298 | "통용 규격 **200×100×60 mm**" | **실치수 199×99 + 줄눈 1 mm = 200×100 모듈**. 200×100 실크기로 깔면 **줄눈이 사라진다** | `I:297-305, 511` |
| ZZ:297 | "형상비 ≤4.0, 최단 상변 ≥50 mm" | 이 지침 본문에 없다 → 출처를 **KS F 4419 `[미검증]`** 로 표기 | `I:509-510` |
| ZZ:180 | "**목표 수치**: flat% 8% 미만, slope -2.0~-2.2, sat 0.15~0.22" | 실사 n=54 자신이 **4개 중 3개를 통과하지 못한다**. `sat_mu` 는 판별력 최하위(0.098)로 게이트 제거 권고 | `real_reference_expansion.md:212-223, 274` |
| ZZ:211 | "감독 스크립트: `scratchpad/imgstats.py`" | `scripts/imgstats.py` 로 저장소 정식 편입 | `realism_baseline.md:5` |
| ZZ:165·169 | T0-3 / T1-1 "`NegObsGround.mdl` **프로덕션 이식** — 최우선" | **전역 승격 불가로 확정**(UV 파이프라인 전무·opacity 전무·round_edges 전무, 텍스처 페치 최대 72회) → 3단 재질 정책으로 대체 | `realism_phase1.md:315-321`, `brief rev.1:110` |
| ZZ:172 | T1-4 "헥스 타일링 MDL" | **강등 — 채택하지 않음**(NegObsGround 패치 혼합과 중복) | `brief rev.1:118` |
| ZZ:176 | T1-8 "잎 노멀 트랜스퍼" | **강등 — 폴백 지위만 유지** | `brief rev.1:119` |

**최소 조치(감독)**: ZZ 서두에 배너 1개 —
> *"이 문서는 2026-07-28 13:15 스냅샷이다. §2 상충4 표 · §9.3 연석·보도블록 · §10.2 · §10.3 ·
> §6 T0/T1 우선순위는 이후 실측으로 정정됐다 → `Docs/reports/realism_phase1.md` §6.5 ·
> `Docs/surveys/.../I_ks_dimension_verification.md` §4.3 · `Docs/briefs/realism_brief_v1.md` 개정 이력 rev.1 참조."*

---

### F3. "죽은 픽셀의 67~74%가 하늘" 이 정정 없이 **7곳**에 남아 있다 (정정 #2)

| 파일:행 | 원문 |
|---|---|
| `Docs/briefs/realism_brief_v1.md:89` | "죽은 픽셀의 **67~74%가 하늘**이었다(실측). 전체 flat% 만 보면 **하늘 교체만으로 목표를 통과**해…" |
| `Docs/briefs/realism_brief_v1.md:103` | "\| **S. 하늘 처리** \| 죽은 픽셀 67~74%가 하늘. 현 HDRI가 무운 `puresky` \|" |
| `Docs/reports/realism_phase1.md:15` | "2. **죽은 픽셀의 67~74%는 하늘이었다.** 조사 6팀이 전부 전체 프레임 평균만 봐서 놓쳤다." |
| `Docs/reports/realism_phase1.md:233` | "\| **S. 하늘 처리** … \| 죽은 픽셀의 **67~74%가 하늘**. … flat% **최대 단일 레버** \|" |
| `Docs/reports/realism_phase1.md:274` | "- 죽은 픽셀의 **67~74%가 하늘**(sceneD3만 41%)." |
| `assets/download_sky.py:6` | "< 1/255) 중 67~74%가 하늘이었다. 원인은 기본 HDRI `qwantani_noon_puresky`" |
| `scripts/imgstats.py:191` | "# [P1 발견] 죽은 픽셀의 67~74% 가 하늘이었다 (감독 실측, 2026-07-28)." |

**고칠 내용**: 전부 **13~39%** 로. 씬별 실측 = scene01 **39%** · scene07 **13%** · sceneD3 **28%**.
"상단 1/3" 근사가 벽·옹벽·건물을 대량 포함했다.
근거: `sky_procurement_v1.md:19-20, 302-316` · `realism_phase2.md:237-243`.

**왜 치명인가**: 이 수치가 `brief rev.1` §3 "S. 하늘 처리" **승격의 유일한 근거**다.
3배 과대평가된 근거가 남아 있으면 다음 세션이 하늘 교체에 예산을 잘못 배분한다.
특히 **scene07 은 하늘로 해결되지 않는다** — 상단 1/3 의 비하늘부가 이미 55.5% 죽어 있고
그건 평면 석축 옹벽이다(`realism_phase2.md:242`, `sky_procurement_v1.md:315-316`).

---

### F4. `flat_gnd < 3.0` 의 근거 "실사 0.1%" 가 **4문서 9곳**에 남아 있다 (정정 #6)

| 파일:행 | 원문 |
|---|---|
| `Docs/briefs/realism_brief_v1.md:92` | "**보조 게이트: `flat_gnd < 3.0`** — 하단 2/3(지면·구조물). 실사 실측 **0.1%**" |
| `Docs/reports/realism_phase1.md:16` | "**하단 2/3(실사 0.1%)를 진짜 기준으로 삼는다.**" |
| `Docs/reports/realism_phase1.md:272` | "\| **실사** \| 3.9 \| 11.6 \| **0.1** \|" |
| `Docs/reports/realism_phase1.md:275` | "- 하단 2/3는 실사 대비 **60~300배** 나쁘다. 여기가 진짜 격차다." |
| `Docs/reports/realism_phase2.md:21` | "\| 실사 \| 3.9 \| **0.1** \| −2.10 \| 0.158 \| 11.9 \|" |
| `Docs/reports/realism_phase2.md:282` | "목표 3.0 은 실사 0.1 과 우리 현재값 사이에서 ZZ 가 정한 값이다." |
| `Docs/reports/deadpixel_diag_d3.md:26` | "\| 실사 레퍼런스 2장 \| **0.08** \| 0.03 \| 0.13 \|" |
| `Docs/reports/deadpixel_diag_d3.md:192, 217, 398, 425` | "## 4. 실사는 왜 0.1 % 인가" / "도달 가능한 한계는 0.1 % 이며" / "실사 0.1 % 에는 **도달 불가**" / "\| 실사 \| 0.08 \| 도달 불가·불필요 \|" |
| `scripts/imgstats.py:75` | "# 하단 2/3(지면·구조물) 보조 게이트 — **실사 실측 0.1%.**" |
| `scripts/imgstats.py:194` | "# 실사 기준: 상단 11.6% / **하단 0.1%** — 하단이 진짜 기준이다." |

**고칠 내용**: 실사 n=54 실측 `flat_gnd` = **3.881 ± 5.005 (중앙값 1.79, p95 13.6, 최대 26.9)**.
0.1 은 실사 분포의 **11 백분위 이상치**이고, 그 2장 중 1장은 라이선스 격리본이다.
**목표 수치 3.0 자체는 유지 가능**하나(실사 중앙값 1.79 ~ 평균 3.88 사이, 실사 통과율 53.7%),
**근거 문장을 "실사 중앙값 1.79 / 평균 3.88" 로 교체**해야 한다.
근거: `real_reference_expansion.md:11-15, 101, 240-262` · `deadpixel_diag_0701.md:148-154`.

> **같은 파일 안에서 모순**: `scripts/imgstats.py` 는 48-77행에 `REAL_N54` / `GATE_ALT` 로
> 정정을 이미 담고 있는데, 75행·194행 주석은 옛 문장 그대로다. 한 파일이 두 소리를 한다.

---

### F5. CC BY-SA 36장이 **이미 커밋돼 있는데** 모든 문서가 "미커밋"으로 적고 있다

**실측**

```
$ git ls-files Docs/reference_photos/expanded/ | grep -c jpg
54
$ git log --oneline --diff-filter=A -- 'Docs/reference_photos/expanded/*.jpg'
6acce85 P2: 실사 표본 n=2 → n=54 확대 — 게이트 근거가 무너졌다   (07-28 21:55)
$ git ls-files .../expanded/ | grep jpg | sed 's/.*wc[0-9]*_//;s/_.*//' | sort | uniq -c
   8 cc0 / 1 ccby20 / 7 ccby40 / 1 ccbysa20 / 1 ccbysa20kr / 1 ccbysa25 /
   3 ccbysa30 / 30 ccbysa40 / 2 kogltype1        ← BY-SA 합계 36장
```

**"미커밋"으로 적고 있는 곳**

| 파일:행 | 원문 | 실제 |
|---|---|---|
| `Docs/reports/license_audit_v1.md:22` | "**원칙 위반(미커밋).** … **.gitignore 미적용 → `git add -A` 한 번이면 커밋됨**" | 이미 커밋됨(`6acce85`) |
| `Docs/reports/license_audit_v1.md:123` | "상태 \| **미추적(`??`) + `.gitignore` 미적용**" | 추적 중 |
| `.gitignore:46-50` | "# Wikimedia 확대 표본 54장(50MB) — LICENSES.csv 와 **재수집 스크립트로 재현**." | 파일이 저장소에 들어 있다 |
| `Docs/reference_photos/real_set_safe.txt:10` | "**파일 실체는 .gitignore 대상**이며 LICENSES.csv 로 재수집한다." | .gitignore 는 **이미 추적 중인 파일에 효력이 없다** |

**타임라인이 원인**: 21:55 커밋(`6acce85`) → 21:59 `.gitignore` 규칙 추가(`ac29ea6`).
순서가 반대라 규칙이 무효다. `git rm --cached` 가 없었다.

**위험**: `feat/realism-v1` 은 현재 `origin/main` 대비 **19 커밋 ahead 이며 미푸시**다.
push/merge 하는 순간 프로젝트 원칙 2(`realism_brief_v1.md:13` "CC0 / MIT-0 / CC-BY(크레딧 기록)만 사용")
밖의 36장이 공개 배포된다. `license_audit_v1.md:506` 이 "반드시 제외" 목록에 넣은 바로 그 대상이다.

**고칠 내용(감독 조치)**: push 전에 ① `git rm --cached` 로 BY-SA 36장(또는 54장 전량) 언트랙 후 커밋,
또는 ② 원칙 2를 개정해 BY-SA 를 명시 허용. 어느 쪽이든 `license_audit_v1.md:22, 123` ·
`.gitignore:46-50` · `real_set_safe.txt:10` 의 "미커밋/재현" 서술을 실태에 맞게 고칠 것.

---

### F6. `_promote_const_to_texture` 의 docstring 이 사실과 반대다 — 승격 재질 대부분이 클램프에 걸린다

`deadpixel_diag_0701.md:362-364` 는 색공간 수정과 **함께** 할 일을 못박았다:

> "**주의**: 이 수정은 승격된 전 재질을 2~3.6배 **밝게** 만든다. 알베도 클램프
> `min(2.5, ...)` 에 걸리는 재질이 생길 수 있으므로 **상한을 함께 재검토**하고,
> `sceneD3` 를 포함한 전 씬 재렌더 회귀가 필요하다."

**이 재검토가 어느 문서에도 기록돼 있지 않고, 클램프는 `scene_common.py:546` 에 `2.5` 그대로다.**
동시에 `concrete` 의 승격 텍스처가 `concrete_wall` → **`concrete_floor`** 로 바뀌었는데
(`scene_common.py:235`, 0701 §S1-P2 권고), `concrete_floor` 는 훨씬 **어둡다**.

**실측** (`_texture_mean`, 선형):

| 텍스처 | 선형 평균 |
|---|---|
| `concrete_wall` (종전) | (0.265, 0.236, 0.160) |
| **`concrete_floor` (현행)** | **(0.146, 0.110, 0.073)** |
| `wood_dark` | (0.080, 0.057, 0.043) |
| `leaf_ground` | (0.061, 0.039, 0.015) |

**실행 결과** (`_promote_const_to_texture`):

| 대상 | 의도색 | 산출 `base_color` | 판정 |
|---|---|---|---|
| scene19 `Parapet` | (0.90, 0.90, 0.87) | **(2.5, 2.5, 2.5)** | 전 채널 클램프 → 실효 (0.365, 0.275, 0.183) = 의도 대비 **2.5~4.8배 어둡고 적황 편향** |
| scene14 `Parapet` | (0.62, 0.62, 0.60) | **(2.5, 2.5, 2.5)** | 동일 증상 |
| scene07 `Wood` | (0.30, 0.20, 0.12) | **(2.5, 2.5, 2.5)** | 실효 (0.200, 0.143, 0.108) |

`concrete` 는 의도색 G 채널이 **0.275 를 넘으면 클램프**된다. 우리 파라펫·건물 셸·옹벽은
대부분 0.30~0.90 대역이므로 **사실상 전부 걸린다.**

**그런데 `scene_common.py:509-512` docstring 은 이렇게 적고 있다:**

> "**의도 알베도 보존**: 씬 작성자가 고른 색을 그대로 살리기 위해 … `base_color = 의도색 / 텍스처평균`
> 으로 곱해 평균 알베도를 유지한다. 즉 **'색은 그대로, 결만 얻는다'**."

**이 문장은 현재 상태에서 거짓이다.** `const_color_texture_map.md:184-201`(§3-3)이 예측한
"클램프 + 누런 편향"이 `concrete_wall` 기준으로 이미 경고돼 있었는데, `concrete_floor` 로
바꾸면서 **더 나빠졌고 재계산이 안 됐다.** 같은 보고서 `:320-323` 이 요구한 클램프 상한
재검토(wood 3.66 배)도 미처리다.

**고칠 내용**: (a) 클램프 상한 재산정 또는 밝은 중성 콘크리트를 `plaster`(0.407,0.366,0.350)로
분기(`const_color_texture_map.md:198-201, 306-318` 초안 그대로), (b) `scene_common.py:509-512`
docstring 에 "클램프에 걸리면 의도색이 보존되지 않는다"는 단서 명기, (c) `0701 §6` 의
"전 씬 재렌더 회귀" 이행 여부를 문서에 기록.

---

## 2. 중대

### M1. Phase2 §1 의 채도 인과 귀속이 틀렸는데 정정 표시가 없다 (정정 #7)

- `Docs/reports/realism_phase2.md:25` — *"채도만 목표 대역에 접근했다(석재·자연물 계열
  **역할별 하향이 의도대로 작동**)."*
- 반증: `code_audit_realism_v1.md:257-280`(M5) — `_SAT_KNEE = 0.30` 이 텍스처 채도 분포보다
  **위**라 `stone`(0.66)·`asphalt`(0.90)·`paving`(1.00) 계수가 **한 번도 발동하지 않았다.**
  실제 원인은 `desat_bright_a=0.30` + macro 채도 변조로 추정. 게다가 렌더 공간 `sat_mu` 임계를
  텍스처 알베도 공간에 옮겨 쓴 **단위 불일치**였다.
- **코드는 이미 고쳐졌다**: `scene_common.py:435` `_SAT_KNEE = 0.18`, 주석 430-434 에 M5 명기.
  **보고서만 안 고쳐졌다.**
- 파급: `realism_phase2.md:18, 20` 의 sat_mu 개선(07: 0.319→0.282 / D3: 0.306→0.278)을
  "역할별 처방의 성과"로 인용하면 안 된다. 인과가 미분리 상태다.

### M2. "3단 재질 정책" 표가 구현과 반대다

- `Docs/reports/realism_phase2.md:64` — "\| 식생·금속·목재 \| veg·metal·wood \| **OmniPBR**(+베벨·디테일 노멀) \|"
- `Docs/briefs/realism_brief_v1.md:110` — "**3단 재질 정책**: 지면·사면 = NegObsGround /
  **구조물·식생·사인 = OmniPBR** / 발광·불투명 = OmniPBR"
- 반증: `code_audit_realism_v1.md:200-213`(M2) — 이 3클래스가 `_CONST_MDL_CLASSES` 에 있어
  **상수색이면 NegObsGround 로 간다.** 게다가 현재 `scene_common.py:262-265` 는 `wood`/`veg` 에
  `tex=` 를 부여해 **승격 경로(=`_make_ground_pbr`)로 라우팅**한다.
- **미확인 위험이 그대로 실행됐다**: `deadpixel_diag_0701.md:390-392, 566-568` 이
  *"`veg` 승격은 `_make_ground_pbr` 경로로 라우팅된다 … **투명 잎 카드를 쓰는 씬이 있으면
  제외 규칙이 필요**. 전 씬 확인 후 적용할 것"* / *"**적용 전 33씬 전수 확인 필수**"* 라고
  못박았는데, **확인했다는 기록 없이 코드에 적용돼 있다.** → §4-C3 미해결 결정 사항.

### M3. "scene01 승인 대기"가 이미 해소됐는데 4곳에 남아 있다 (정정 #1)

| 파일:행 | 원문 |
|---|---|
| `Docs/reports/realism_phase2.md:38-43` | "### scene01 은 **구조적으로 도달 불가** … `sc.make_pbr` 을 타지 않기 때문이다(33씬 중 유일)" |
| `Docs/reports/realism_phase2.md:258-259` | "**준비된 패치**(미적용) … **승용 승인 필요.**" |
| `Docs/reports/realism_phase2.md:207` | "\| scene01 \| **승인 대기**(§6) \|" |
| `Docs/reports/realism_phase1.md:219-220` | "**32/33 씬 자동 적용**. scene01만 자체 캡처 블록이라 예외" |
| `Docs/briefs/realism_brief_v1.md:80` | "`scene_common.capture_pipeline` 경유 = **32/33 씬 자동 적용**. scene01만 자체 캡처 블록이라 예외" |
| `Docs/reports/regression_tool_v1.md:145-146` | "**룩 토글이 scene01 에 안 먹었다.** … `realism_phase1.md` §3.4 '**scene01만 자체 캡처 블록이라 예외**'" |

- 실제: 커밋 `a66c1ad "P2: scene01 구조 통일 + 채도 자기교정"` 으로 위임 적용 완료.
  `code_audit_realism_v1.md:539-549` 가 인자 1:1 대응·워밍업 572 일치까지 **동치성 검증 완료**.
  `deadpixel_diag_0701.md:39-41` 이 리팩터 후 수치(`p2rf_off` 7.41 / `p2rf_on` 6.70 / `p2g4_on` 5.59)를 보고.
- **고칠 내용**: 위 6곳에 "**해소(`a66c1ad`) — 33/33 경유**" 표시.
  단 `realism_phase2.md:250-256` 의 *"감독의 앞선 보고 '33씬 전 재질이 make_pbr 단일 경유'는
  틀렸다"* 라는 **정정 자체는 사실이므로 유지**한다(이력).

### M4. 게이트 현재값이 4개 문서에서 다르고, 어느 것이 최신인지 표시가 없다

| 문서:행 | scene01 | scene07 | sceneD3 | 라운드 |
|---|---|---|---|---|
| `realism_phase2.md:14-20` | 12.1 | 9.5 | 28.1 | p2g3 |
| `deadpixel_diag_d3.md:21-25` | 12.13 | 9.51 | 28.10 | p2g3 |
| `const_color_texture_map.md:116, 122` | 12.1 | 9.5 | (28.1) | p2g3 |
| **`deadpixel_diag_0701.md:32-42`** | **5.59** | **10.00** | **2.87** | **p2g4 (최신)** |

`deadpixel_diag_0701.md:44-46` 만이 라운드를 명시한다 —
*"브리프의 'scene01 6.7' 은 `p2rf_on` 값이다. 최신 `p2g4_on` 은 **5.59** 이므로 이하 판정은 5.59 를 기준으로 한다."*

**가장 위험한 결과**: sceneD3 는 `p2g4_on` 에서 **2.87 로 이미 목표 3.0 을 통과**했는데,
`realism_phase2.md:275-278` 은 여전히
> *"**sceneD3 가 가장 나쁘다**(28.1). 대면적 아스팔트·측구가 여전히 평탄하다는 뜻으로 …
> → 상수색 전수 감사의 CC0 텍스처 매핑이 **직접 표적**."*

라고 다음 단계를 지시한다. → **다음 세션이 이미 해결된 D3 아스팔트를 다시 표적으로 삼는다.**

**고칠 내용**: `realism_phase2.md` 에 rev 절을 붙이거나 `realism_phase2_rev1.md` 를 신설해
라운드 태그(`p2g1`/`g2`/`g3`/`rf`/`g4`)와 현재값을 한 표로 모으고, §7 의 다음 표적을
scene07(10.00) → scene01(5.59) 순으로 교체.

### M5. `bump_factor` 처방이 두 진단서에서 정면 충돌하고, 코드는 반증된 쪽을 채택했다

| 문서:행 | 서술 |
|---|---|
| `deadpixel_diag_d3.md:320-321` | "P3 1순위: **`bump_factor_a` 상향**(1.0 → 1.6~2.0). 노멀 강화는 **음영에서도 셰이딩 기울기를 만들므로 밝기에 덜 의존**한다. 비용 0" |
| `deadpixel_diag_0701.md:214, 225-227` | "**판정: 원리상 그늘에서는 통할 수 없다.** … 균일 반구 스카이돔 아래서 `∫(n·ω)⁺dω = π` 는 **n 의 방향과 무관** → **노멀 섭동의 기여가 정확히 0**" |
| `deadpixel_diag_0701.md:233-238` | 실측 — 양지 c **+10%** / 그늘 c **−3%**(노이즈). 밝기대별로도 음영 0.06–0.15 대가 **+6.6 pp 악화** |
| `deadpixel_diag_0701.md:433` | "❌ **`bump_factor` 추가 상향** — §5 실측대로 그늘에서 무효고 … 역효과다" |

**코드는 D3 쪽을 채택했다**:
`scene_common.py:235, 238-239` — `bump=1.6` + 주석
> "`# bump 1.6 = 진단 P3 (음영부는 밝기가 아니라 노멀 대비로만 결이 산다)`"

**이 주석 문장은 `0701 §5` 가 실측으로 반증한 명제 그 자체다.**

**고칠 내용**: (a) `deadpixel_diag_d3.md:320-321` 에 "**0701 §5 로 반증 — 그늘에서 무효**" 표시,
(b) `scene_common.py:239` 주석을 "양지 한정 효과(0701 §5). **그늘은 알베도 대비로만 회복된다**"로 교체,
(c) `concrete` bump 1.6 존치 여부를 재판정(0701 은 음영대 악화를 실측했다).

### M6. 베벨값 — I 조사 권고 2건이 반영되지 않았고 brief 는 옛 값 그대로다 (정정 #9)

| 클래스 | I 권고 (`I:386-395, 564-569`) | **현재 코드** | `phase2 §2.6:106-112` | `brief rev.1:111` |
|---|---|---|---|---|
| concrete | 0.020 | **0.020** ✅ | 0.020 | "콘크리트 **10**" ❌ |
| curb | 0.010 | **0.010** ✅ | 0.010 | — |
| **stone** | **0.010** | **0.004** ❌ | 0.004 "[근거 없음] 보수적 하향" | "석재 **6**" ❌ |
| **paving** | 0.010 유지 | **0.006** ❌ | 0.006 "[근거 없음]" | — |
| nosing | 0.012 + IBC 표기 | **0.012** ✅ | 0.012 | "노징 12" ✅ |
| metal | 0.002 | **0.002** ✅ | 0.002 | "금속 2" ✅ |

- `Docs/briefs/realism_brief_v1.md:111` 원문:
  > "2-2 베벨 기본값 … **콘크리트 10 / 석재 6 / 금속 2 / 계단 노징 12 mm.** … **KS 원문 확인 과제는 유지**"

  I 조사가 이 과제를 종결했다(`I:16-23, 353-357`). 이 줄이 그대로면 다음 세션이 **같은 조사를 반복**한다.
- `Docs/reports/realism_phase1.md:79` "`[추정 — 국내 표준 원문 미확인, Phase 2에서 KS 규격 확인 필요]`"
  및 `:291` 미결 목록 "연석·계단 모따기 국내 표준 `[추정]`" → `I:571-575` 체크리스트대로 **종결 표시** 필요.
- `stone`/`paving` 은 I 권고(0.010)와 코드(0.004/0.006)가 다르다. **어느 쪽이 승용 결정인지
  어느 문서에도 없다** → §4-C6 미해결 결정 사항.
- I 조사가 새로 낸 씬 제작 항목 5건(`I:585-591`: 연석 2종 프리셋 · 턱낮추기 직각 · 경계석
  차도측만 R · **계단코 논슬립 밴드 50 mm** · 볼라드 평평한 상단)은 **어느 지시서에도 편입되지 않았다.**

### M7. `ori_axis` 폐기 판정이 baseline 에 그대로 남아 있다 (정정 #5)

- `Docs/reports/realism_baseline.md:109` — "### 4.3 `ori_axis`(축정렬 에지 비율)는 이 표본에서
  **판별력이 없다** — 추적 중단 권고"
- `Docs/reports/realism_baseline.md:119` — "**이 지표로 개선을 주장하지 않는다.** 실사 표본을 확대하기 전까지 보류."
- 반증: `real_reference_expansion.md:19-21, 185, 193-203` — |AUC−0.5| = **0.168** 로,
  **게이트에 들어가 있는 `sat_mu`(0.098)·`sat_sd`(0.093)·`chroma_sd`(0.138) 보다 전부 높다.**
  판정은 "판별력 없음"이 아니라 "**약한 판별력 — 게이트 아닌 보조 지표**", 경보선 실사 p95 = **0.371**.
- `scripts/imgstats.py:62-64` 주석은 이미 정정을 반영했다. **baseline 만 안 고쳐졌다.**

### M8. baseline 의 실사 기준군이 라이선스 격리로 무효화됐는데 표시가 없다

- `Docs/reports/realism_baseline.md:8` — "**이 문서의 수치가 이후 모든 개선폭의 기준이다.**"
- `Docs/reports/realism_baseline.md:35` — 재현 명령 `@real 'Docs/reference_photos/*.jpg'`
- `Docs/reports/realism_baseline.md:51` — "\| **실사 레퍼런스** \| **2** \| −2.10 \| 11.9 \| 3.9 \| … \|"
- `Docs/reports/realism_baseline.md:125` — "실사 그룹은 **n=2** (`Docs/reference_photos/`) 다."
- 실제: 2장 중 `everytime-1784886395380.jpg` 는 `ac29ea6` 에서 `Docs/reference_photos/quarantine/` 로
  격리·언트랙됐다(디스크 확인 완료). **위 재현 명령은 이제 n=1 을 측정한다.**
- `scripts/imgstats.py:24-27` 이 명시적으로 금지한다:
  > "⚠ 종전 `@real 'Docs/reference_photos/*.jpg'` (n=2) 는 **쓰지 말 것** — 2장 중 1장이
  > 라이선스 근거 없는 제3자 사진이라 격리됐고, 나머지 1장만으로는 표본이 성립하지 않는다."
- **고칠 내용**: baseline 서두에 배너 — "실사 그룹 n=2 는 라이선스 격리로 폐기.
  배포 안전 세트 `Docs/reference_photos/real_set_safe.txt`(n=18, CC0 8 + CC BY 8 + KOGL 2)로
  **재측정 필요**. T1 게이트 3지표가 이 n=2 위에 서 있으므로 재산출 전까지 게이트 절대치를 인용하지 말 것."

### M9. "하늘은 범인이 아니다"가 일반 결론처럼 읽힌다

- `Docs/reports/deadpixel_diag_d3.md:113-117` — "### (C) 하늘은 범인이 아니다 … P1 에서 확인된
  '죽은 픽셀의 67~74 % 가 하늘' 은 **전체 프레임 `flat_pct`** 이야기이고, `flat_gnd` 에는 해당되지 않는다."
- 반례: `deadpixel_diag_0701.md:139` — scene07 `gate_frame` 은 피치 **+11.3° 상향**이라
  하늘이 하단 2/3 를 **21.7% 점유**하고, 그 컷 32.48 중 **20.40 이 하늘**이다.
  *"D3 가 '하늘은 범인이 아니다'라고 결론낸 이유는 **D3 에 상향 뷰가 한 컷도 없었기 때문**이다."*
- **고칠 내용**: d3 §2-(C) 에 "**씬 의존 — 상향 뷰가 있는 씬은 다르다(0701 §3-B, §8)**" 단서 추가.

### M10. `scene_common.py` 안에 서로 모순되는 서술·**중복 키 2건**

실측(`python3` 로 `LOOK_ROLE` 키 중복 검사): **`['Roof', 'Panel']`**

| 위치 | 문제 |
|---|---|
| `scene_common.py:322-324` | 주석 "나머지 Bag/Emit/Rubber/**Snow** 는 **의도적으로 misc**" ↔ 바로 다음 줄 `:326` `"Snow": "snow"`. **주석이 정반대다.** (`const_color_texture_map.md:238-243` 권고를 적용하면서 주석을 안 고쳤다) |
| `:308` `"Roof": "metal"` ↔ `:329` `"Roof": "wood"` | 뒤가 이긴다(wood). **앞 줄은 죽은 코드**이며 0701 이 지적한 "Roof→metal 오분류"를 아직 유지하는 것처럼 읽힌다 |
| `:321` `"Panel": "sign"` ↔ `:326` `"Panel": "metal"` | 뒤가 이긴다(metal). 그러나 `const_color_texture_map.md:245-249` 권고는 **`DeckPanel` 한정**이었지 `Panel` 전체가 아니다. 사인 패널까지 금속 처방을 받을 수 있다 → §4-C5 |
| `:303` | "낙차 에지 — 브리프 §2.1 **승인값(노징 12 mm)**" ↔ `code_audit_realism_v1.md:379-384`(m6): 실제 계단 재질 대부분(`Stair`/`Riser_`/`Slab`/`Concrete`)이 `concrete`(**0.020**)로 가서 **승인값의 1.67배** 베벨을 받는다. 주석이 실태와 다르다 |
| `:277-278` + `:274-276` | `LOOK_CLASS["snow"]["tex"] = "snow"` 인데 **`TEX` 레지스트리에 `snow` 가 없다**(실측: `'snow' in sc.TEX` → `False`, 디스크에도 `assets/**/snow*` 0건). `_promote_const_to_texture` 가 `(None,None,None,원색)` 을 조용히 반환 → **sceneC1 의 지면프레임 88.5% 가 여전히 상수색.** `const_color_texture_map.md:276-280` 의 `TEX["snow"]` 추가·다운로더 확장이 **미적용**이고, 주석 `:276` 은 "TODO: 조달 후 적용"으로만 남아 있다 |

### M11. `code_audit` 치명 4건의 반영 상태가 어느 문서에도 없다 (실측 결과 전부 반영됨)

`code_audit_realism_v1.md:638-645` "조치 우선순위"에 체크박스가 없고, 커밋
`93e290a "치명 4건 + 중대 4건 수정"` 이 무엇을 고쳤는지 문서에 없다. **본 감사가 코드로 확인했다:**

| 항목 | 상태 | 근거 |
|---|---|---|
| C1 `tint` 소실(77건/30씬) | ✅ 수정 | `scene_common.py:1092-1099` — `base_color` 에 접어 넣음 + 주석에 "[치명 C1 수정]" |
| C2 `Lane` → asphalt 승격 | ✅ 수정 | `scene_common.py:374` — `"lane"` 이 `paint` 규칙으로 이동 |
| C3 `SillBand` 무게이트 | ✅ 수정 | `scene_common.py:1705` — `ins = … if LOOK_V1 else 0.0` |
| C4 웨더링 월드 z<0 전면 | ✅ 수정 | `scene_common.py:209-221` + `_W_STRUCT/_W_STONE/_W_EDGE` 의 `grime=0.0, splash=0.0` |
| §6 색공간 불일치 | ✅ 수정 | `scene_common.py:497-503` (sRGB→선형) |
| 4채널 EXR lookfix | ✅ 수정 | `scene_common.py:1920` `[..., :3]` |

- **다만 `code_audit:641` 이 요구한 "고친 뒤 게이트를 다시 돌려야 한다"의 이행 기록이 없다.**
  현재 `p2g4_on` 수치가 C1~C4 수정 **후**인지 **전**인지 문서로 판별할 수 없다.
- 미조치로 남은 것: **M1**(상수색 금속 `metallic` 소실 113건) · **M3**(변위 스킨 28% 침투) ·
  **M6**(`_effective_sat` 가 비율을 채도로 오독) · **M7**(클램프 2.5 → §F6) · 경미 9건.
  → §4-G4.

---

## 3. 경미

| # | 위치 | 내용 |
|---|---|---|
| m1 | `realism_phase1.md:289` · `regression_tool_v1.md:260` | "`Docs/reports/material_audit_realism_v1.md` **예정**" — 실제 산출물명은 `const_color_texture_map.md` + `code_audit_realism_v1.md`. **없는 파일을 가리킨다** |
| m2 | `realism_phase1.md:290` | "RTX 기능 문서 근거 \| **진행 중**" → 완료(H 보고서 1,109줄, 16:29) |
| m3 | `realism_phase1.md:288` | "실험 3(나무 임포트) \| **미완** — 조달 진행 중" → 조달 완료(`45d2a3d`, `CREDITS.md` §식생). **씬 결선은 여전히 0건**(`license_audit_v1.md:440`) — 상태를 "조달 완료 / 결선 미실시"로 |
| m4 | `Docs/CREDITS.md` | `license_audit_v1.md:402-425`(§4-A)가 지적한 **누락 8건 전부 미반영**. 현재 절은 하늘 / 식생 / 실사 3개뿐(`grep '^##'` 확인). 실사용 텍스처 역할 22종(ambientCG 4 + PolyHaven 17) 기재 **0건** |
| m5 | `Docs/CREDITS.md` | `license_audit_v1.md:433-445`(§4-B) "과잉" — 하늘 HDRI 3종·식생 USD 4종은 **씬 참조 0건**인데 "조달 완료 / 씬 미결선(2026-07-28)" 표시가 없다 |
| m6 | `deadpixel_diag_0701.md:488` | "scene01 은 이미 **0.138** 로 하한 미달" ↔ `realism_baseline.md:47`·`realism_phase2.md:15` 는 **0.146**. 라운드가 달라 생긴 차이지만 병기가 없다 |
| m7 | `ZZ_synthesis.md:211` | "E팀: `scratchpad/pilot_stats.py`" — 저장소 미편입. `imgstats.py` 만 `scripts/` 로 편입됐다. E팀 스크립트 행방 미기록 |
| m8 | `realism_baseline.md:149-150` | "`capture_pipeline` 폴링 상한(40회)을 60회로 … **Phase 2 정비 항목으로 미룬다**" → 미처리(`scene_common.py` 현행 40). 이월 표시 필요 |
| m9 | `sky_procurement_v1.md:137` | "2026-07-28 17:20 기준 **1603행**" — 현재 1920행. 본인이 "함수명으로 찾을 것"이라 부기했으므로 경미하나, 행번호 인용은 제거가 낫다 |
| m10 | `user_feedback_v5_1.md` 전체 | 이번 라운드 정정과 **충돌 없음**(전역 규약 §1~5 · v5.2 §6~9 전부 유효). 다만 §4 "순백(>0.8) 대면적 금지"의 **명백한 위반**이 `const_color_texture_map.md:211-212`에서 발견됐다(scene19 `Parapet` 0.90, 1,046 m², gnd 10.0%) — 규약 문서 쪽엔 반영 불필요하나 §4-C8 로 결정 대기 |

---

## 4. 미해결 결정 사항 — 통합 목록

문서 곳곳에 흩어진 "사용자/감독 결정 대기" 전량. **총 41건.**

### A. 라이선스·배포 (8)

| # | 항목 | 출처 |
|---|---|---|
| A1 | **`look_refs/` 17장의 Gemini 생성 표면** — `gemini.google.com`(소비자 앱, "ML 모델 개발 금지" 적용) vs `aistudio`(적용 없음). **이 하나로 판정이 갈린다.** 이미 origin/main 에 푸시됨 | `license_audit_v1.md:99-107, 553-555` |
| A2 | `everytime-*.jpg` **git 히스토리 정리** — 워킹트리 격리(`ac29ea6`)로는 공개 상태가 해소되지 않는다(`6dac9a1` 이 origin/main 에 있음). 히스토리 재작성은 승인 필요 | `license_audit_v1.md:57-62, 355-358` · `.gitignore:42` |
| A3 | **`expanded/` BY-SA 36장 언트랙 여부** — 이미 커밋됨·미푸시. push 전 결정 필수 | **본 감사 신규 발견 §F5** |
| A4 | **원칙 2 개정 여부** — KOGL Type1 편입? BY-SA 를 "로컬 참조 전용"으로 허용? | `license_audit_v1.md:176-177` · `real_reference_expansion.md:314-325` |
| A5 | `LICENSE` / `DATA_LICENSE` 파일 신설 (현재 부재 = All rights reserved) | `license_audit_v1.md:458-462, 528-530` |
| A6 | `NegObsGround.mdl` 의 OmniPBRBase "축약 이식" 실체 — 코드 이식이면 재작성 또는 고지 헤더 | `license_audit_v1.md:373-392, 517-518` |
| A7 | `CREDITS.md` 전면 개정(누락 8건) | `license_audit_v1.md:525-527` |
| A8 | `.gitignore` allowlist 전환(`assets/**` 통째 무시 + 예외 되살리기) | `license_audit_v1.md:369-371` |

### B. 게이트·지표 (7) — 전부 `real_reference_expansion.md` §4.4

| # | 항목 | 현행 → 권고 |
|---|---|---|
| B1 | **`sat_mu` 게이트 제거** (판별력 최하위 0.098, 렌더가 실사 분포 한가운데) | 0.15~0.22 → **제거, 기록만** (`:274, 297`) |
| B2 | `slope` 구간 확대 (현행은 실사의 44%만 통과, **E팀 −1.94 가 미달 판정**) | −2.2~−2.0 → **−2.30~−1.75** (`:237-238, 270`) |
| B3 | `flat_pct` 완화 | <8 (평균) → **중앙값 <12** (`:272`) |
| B4 | `grad_k` 게이트 **신설** (분리도 최고 0.354인데 게이트에 없다) | 없음 → **중앙값 4~20** (`:273`) |
| B5 | **평균 판정 → 중앙값 판정 전환** (flat_* 는 왜도 +2.38) | (`:258, 305`) |
| B6 | `flat_gnd 3.0` 근거 문장 교체 (§F4) | (`:271`) |
| B7 | `ori_axis` 보조 지표 복권 + 경보선 **0.371** | (`:275`) · §M7 |
| — | ※ `scripts/imgstats.py:45` 는 `GATE` 에 "**변경하지 않는다**"로 잠겨 있고 `:70 GATE_ALT` 가 "승인 전"으로 병존한다. **B1~B7 을 한 번에 결정해야 이 이중 상태가 풀린다.** | |

### C. 씬·룩 (12)

| # | 항목 | 출처 |
|---|---|---|
| C1 | **scene07 `gate_frame` 하늘 1.46** — ①예산 인정 ②뷰 피치 하향(GT 시퀀스 영향) ③HDRI 교체(33씬 회귀). **이 결정 없이는 scene07 의 3.0 통과 여부가 결정되지 않는다** | `deadpixel_diag_0701.md:423-429, 621-622` |
| C2 | §6 색공간 수정의 **전 씬 재렌더 회귀 예산** — 수정은 커밋됐으나 재렌더 기록 없음 | `deadpixel_diag_0701.md:362-364, 623-624` |
| C3 | **`veg` 텍스처 승격의 라우팅 위험** — 투명 잎 카드 사용 씬 **전수 확인 후 적용**. **확인 기록 없이 이미 적용됨**(`scene_common.py:264-265`) | `deadpixel_diag_0701.md:390-392, 566-568, 625` |
| C4 | `Roof` 전용 역할(`tile`) 신설 여부 — 현재 `wood` 로 임시 처리, 중복 키 잔존 | `deadpixel_diag_0701.md:396-397, 626` · §M10 |
| C5 | `LOOK_ROLE["Panel"]` 을 **metal 로 일괄** 바꾼 것이 의도인지 (권고는 `DeckPanel` 한정) | `const_color_texture_map.md:245-249` vs `scene_common.py:326` |
| C6 | **`stone`/`paving` 베벨** — I 권고 0.010 vs 현재 0.004/0.006 | §M6 · `I:386-395` |
| C7 | sceneC1 `Snow` 의도 알베도 **0.72→0.55~0.62 하향** + **`TEX["snow"]` 실제 조달**(현재 미조달 = 승격 무효) | `const_color_texture_map.md:206-210, 276-280` · §M10 |
| C8 | scene19 `Parapet` 0.90 — **v5.1 §4 "순백(>0.8) 대면적 금지" 명백한 위반**, 1,046 m²·gnd 10.0% | `const_color_texture_map.md:211-212` |
| C9 | `metal_galv` 신규 조달 여부 (누적 87.9%p, 현재 `metal` 에 `tex` 없음) | `const_color_texture_map.md:163-173` |
| C10 | 수면 4씬 **잔물결 노멀 절차 생성** (외부 CC0 전무) | `const_color_texture_map.md:176-182` |
| C11 | `nosing` · `Joint`/`CutLine` 을 텍스처화 금지 목록에 추가 (`Joint`/`CutLine` 은 `_LOOK_RULES:374` 에서 **이미 paint 로 이동됨** — `nosing` 만 미결) | `const_color_texture_map.md:257-266` |
| C12 | **`base_color` 클램프 상한 2.5 재검토** — 색공간 수정 후 대부분이 클램프에 걸린다 | §F6 · `deadpixel_diag_0701.md:362-364` · `const_color_texture_map.md:320-323` |

### D. 하늘 (5)

| # | 항목 | 출처 |
|---|---|---|
| D1 | **하늘 HDRI 씬 배정** — 조달·검증만 완료, 씬 적용 미실시(브리프상 "다음 지시서" 소관) | `realism_phase2.md:208, 229-231` · `sky_procurement_v1.md:463` |
| D2 | `ensure_noon_lookfix` 4채널 EXR 패치 — **적용 확인됨**(`scene_common.py:1920`). **문서에 반영 기록만 없음** | `sky_procurement_v1.md:369-371` |
| D3 | 캡 반경 **1.5°→0.6°**[권고 A] · 태양 검출 강건화 + 수용 게이트[권고 B] | `sky_procurement_v1.md:373-386` |
| D4 | `NEGOBS_SUN_CAP_DEG` 캐시 무효화(파일명에 파라미터 삽입) | `code_audit_realism_v1.md:338-345`(M9) |
| D5 | S3(`farm_field`) 존치 vs `kloppenheim_03` 교체 (flat% 이득 ≈ 0) | `sky_procurement_v1.md:462` |

### E. 측정·표본 (5)

| # | 항목 | 출처 |
|---|---|---|
| E1 | **실사 기준군 재구성** — `real_set_safe.txt`(n=18)로 baseline 재측정 + 게이트 수치 재산출 | `license_audit_v1.md:519-521` · §M8 |
| E2 | **Mapillary 토큰 발급**(계정 가입 필요) — 실사 표본 확대 1순위. Commons 는 규모 상한(2.0% 통과율) | `real_reference_expansion.md:331-340` |
| E3 | AI Hub(Track C) 계정 — 내국인 가입·승인 | `real_reference_expansion.md:349` |
| E4 | **`slope` 리사이즈 체인 통일 후 재측정**(논문 게재 전). 실사 6000px vs 렌더 1920px 축소 배율 불일치로 0.08 편차 실측 | `real_reference_expansion.md:151-155, 310-312` |
| E5 | **로봇 시점(0.3~0.9 m) 실사 참조 전무** — 현 `flat_gnd` 실사 기준선은 1.5~1.7 m 시점 한정임을 명시 | `real_reference_expansion.md:345-348` |

### F. ZZ §5 원안 — 아직 미결 (3)

| # | 항목 | 출처 |
|---|---|---|
| F1 | **점자블록 정책** — ①되돌림 ②확률적(p≈0.5) ③유지. **v5.2 §7 "기본 OFF" 와 정면 충돌**하며 어느 쪽도 종결되지 않았다 | `ZZ:139-145` vs `user_feedback_v5_1.md:51-52` |
| F2 | 사람·차량 도입 범위 → §9.2 가 답을 좁힘(MPFB CC0 주력 + Isaac DH 보조 + honey/tri 차량, Mixamo·RenderPeople 금지) | `ZZ:147-149, 257` |
| F3 | Fab 유료 에셋 구매 여부 → §9.1 이 "**재검토 대상**"으로 되돌림(Isaac 4.5 가 이미 한국 표지판 156종·차량·인체 보유) | `ZZ:151-153, 244` |

### G. 회귀·도구 (4)

| # | 항목 | 출처 |
|---|---|---|
| G1 | GRAZE **검출력 미검증** — 라벨된 "은닉 파괴" 양성 사례가 데이터에 없다(검증된 건 오탐률뿐) | `regression_tool_v1.md:115-117, 257` |
| G2 | 하늘 교체 라운드용 **하늘/지면 분리 정규화** — 백분위 매칭이 하늘 면적 변화에 오염된다 | `regression_tool_v1.md:258` |
| G3 | `capture_pipeline` 폴링 상한 40→60 (Phase 2 정비 항목으로 미룬 채 미처리) | `realism_baseline.md:149-150` |
| G4 | **`code_audit` 미조치분** — M1(금속 `metallic` 소실 113건) · M3(스킨 28% 침투) · M6(`_effective_sat` 비율 오독) · M7(클램프) + 경미 9건 · `[추정]` 8건 | `code_audit_realism_v1.md:186-394, 624-645` |

---

## 5. 인수인계 경로 평가 — 판정: **불합격**

| 질문 | 판정 |
|---|---|
| 읽는 순서가 명확한가 | ✅ 명확하다(README:105-109 = INDEX:3-4, 3단계) |
| **최신 상태에 도달하는가** | ❌ **도달률 0.** 지정된 3문서가 라운드 산출물 **전부보다 오래됐다**(§F1) |
| 이번 라운드 산출물이 INDEX 에 등재됐는가 | ❌ **13건 전부 미등재**(§F1) |
| "지금 어디까지 됐고 다음에 뭘 해야 하는가"가 한 곳에 있는가 | ❌ 가장 가까운 `realism_phase2.md:263-283` 이 **p2g3 시점**이라 이미 해결된 sceneD3 를 최우선 표적으로 지시한다(§M4) |

**새 세션이 지시대로 읽으면 벌어지는 일 (재현 시나리오)**
1. `README.md` → "33씬 21/21 합격, 진행 중 과제는 사실성 격차, ZZ 부터 읽을 것"
2. `Docs/INDEX.md` → 같은 3단계. `realism_brief_v1.md` 도 phase 보고서도 안 보인다
3. `ZZ_synthesis.md` → §6 T1 목록을 실행 계획으로 채택 →
   **이미 폐기된 처방(NegObsGround 전역 이식 · 헥스 타일링 · 잎 노멀 트랜스퍼)을 착수**하고,
   **이미 반증된 사실(MDL displacement 미지원 · spp 기본값 1 · cameraFStop 부재)을 전제**로 설계하며,
   **정정된 규격(연석 100~250, 보도블록 200×100)으로 기하를 만든다.**

**최소 복구 3단계 (감독 조치)**
1. `README.md:92-101` 교체 + 읽는 순서에 `realism_brief_v1.md`(본문+rev.1) 2순위 삽입
2. `Docs/INDEX.md` 에 13건 등재 + 유효/정정 표시
3. `ZZ_synthesis.md` 서두 정정 배너(§F2)

---

## 6. 문서 구조 개선 제안

1. **`Docs/STATUS.md` 신설 (20줄)** — "현재 브랜치·커밋 / 현 게이트 수치와 라운드 태그 /
   다음 액션 3개 / 승인 대기 목록" 만. README·INDEX 는 **목차**이지 **상태판**이 아니다.
   이번 라운드에서 상태가 8개 보고서에 흩어졌고, 그래서 §M4 가 발생했다.
2. **`Docs/CORRECTIONS.md` (정정 원장)** — `폐기된 서술 | 문서:행 | 대체 내용 | 근거 문서` 4열.
   이번 라운드에만 10건이 나왔고 **전부 원문서에 미반영**이다. 원문서 수정이 부담스러우면
   최소한 원장에서 역참조가 되게 할 것. (이 감사 보고서 §1~2 가 그 초안이다.)
3. **보고서 서두 상태 배너 규약** — 모든 `Docs/reports/*.md` 첫 줄에
   `상태: 유효 | 부분 정정(→X) | 폐기` 강제. **지금은 mtime 말고는 최신성을 알 방법이 없다.**
4. **ZZ_synthesis 를 진입점에서 내리기** — 조사 스냅샷은 이력 문서로 강등하고,
   진입점은 `STATUS.md` + `realism_brief_v1.md`(본문+rev.1)로. ZZ 는 정정 배너를 달아 참조용으로만.
5. **코드 주석의 근거 문장에 출처 문서·절 병기를 규약화** — 현재 일부만 지켜진다.
   `scene_common.py:239` 처럼 **반증된 명제가 주석에 남으면 다음 리뷰가 그것을 근거로 삼는다**(§M5).
6. **라운드 태그 명명 규약 문서화** — `p2g1/g2/g3/rf/g4` 가 무엇인지 정의한 곳이 없다.
   `look_check/<scene>/<round>/` 의 라운드 이름과 그 시점 코드 커밋을 매핑한 표가 필요하다.

---

## 7. 이 감사의 한계

- **GPU 미실행** — 렌더 수치는 전부 기존 보고서 인용이다. `p2g4_on` 이 `code_audit` 치명 4건
  수정 전인지 후인지는 **문서로도 코드로도 판별하지 못했다**(§M11).
- `_LOOK_RULES` 전체 순서 충돌(code_audit §4.4의 10건)은 재검증하지 않았다 — `Lane` 1건만 확인했다.
- `Docs/audit_v4/` 의 판정문·픽스로그 40여 건, `surveys/` 의 A~H 원보고서 본문은
  **대상 목록에 없어 전문 대조하지 않았다.** ZZ 를 경유해 인용된 부분만 확인했다.
- `look_refs/`·`assets/` 하위 스크립트 주석은 `download_sky.py:6` 1건만 grep 으로 걸렸다.
  다른 다운로더 주석의 정합성은 미확인.
