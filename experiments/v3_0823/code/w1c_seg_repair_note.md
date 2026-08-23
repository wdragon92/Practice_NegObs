# W1-C REPAIR 1 — renderer seg-stale 수리 · DIFF-OF-BEHAVIOUR NOTE

대상 파일 **`scripts/run_data_render.py`** (1255줄 → 1491줄)
근거 원장 `experiments/v3_0823/W1B2_SEGFILL_REPORT.md §3.1` ·
`experiments/mainrun_0819/DECISIONS.md` **D79 ③** (D75 ② 문면 정정)
날짜 2026-08-24 · 스크래치 라운드 `260827_v3w1c_segprobe`

이 문서의 목적은 하나다. **`NEGOBS_SEG_SIDECAR`가 unset인 기본 경로가
수정 전과 정확히 같은 문장을 실행한다는 것**을, 건드린 줄마다 논증한다.

---

## 0. 무엇을 고쳤나 (한 문단)

`NEGOBS_SEG_STRICT=1`은 **결정론적** stale(= `t0` 계단이 어노테이터를 재평가하지
않아 씬 프로세스 전 컷이 cut 0의 마스크가 되던 결함)을 없앴지만, **산발적 경합**은
남았다 — 컷 경계에서 어노테이터가 `rep.orchestrator.step()` 이후에도 *직전 평가*를
돌려주는 경우가 648컷당 1 / 576컷당 2 / 816컷당 3, 즉 **0.15–0.37 %**로 남는다
(§3.1). 라운드 단위 검출기(`run_260826_v3w1_lib_b2.sh`의 `IDSEG-STALE`: "N컷에
고유 마스크 1개")는 576분의 1을 볼 수 없고, 사후 판정이라 막지도 못한다.
그래서 **컷마다** 마스크를 검증하고, stale이면 **재페치**하고, 그래도 stale이면
**나쁜 `.idseg.npz`를 쓰지 않고 `.idseg.STALE` 마커를 대신 쓴다.** 전부 옵트인
분기 안에서.

---

## 1. 술어 — 왜 "해시가 같다"만으로는 결함이 아닌가

D75 ②가 VG-03을 정정하며 확정한 대로, **마스크 해시 비교 단독은 오설계**다:
같은 포즈·같은 기하를 보는 두 컷은 **정상적으로** 같은 마스크를 갖는다. 그래서
마스크 해시는 언제나 **목격자(witness)** 와 짝지어진다.

| | 내용 | 왜 |
|---|---|---|
| `mask_sha` | idseg 배열 내용의 sha256 16자 | dtype·shape를 다이제스트에 먼저 넣어 재해석 충돌 불가 |
| witness `depth` | **이 컷의** depth 배열 sha | 1순위. `_seg_attach`는 `_depth_attach`가 만든 render product가 있어야만 non-None이므로 seg가 살아 있으면 depth도 살아 있다 |
| witness `pose` | `(eye, yaw, pitch, hfov)` sha | depth 페치가 비었을 때의 폴백. 더 약하지만(같은 포즈가 같은 픽셀을 증명하진 않는다) **데이터를 버리는 쪽으로는 절대 틀리지 않는다** |

```
stale  :=  mask_sha == prev_mask_sha  ∧  witness_kind 동일  ∧  witness_sha 변화
```

둘 다 같으면 **진짜 동일 프레임**이므로 정상 통과(`identical-frame`).
witness 종류가 다르면(한 컷은 depth, 다른 컷은 pose) 결론을 낼 수 없으므로
**마스크를 지킨다**(`witness-kind-mismatch`).

---

## 2. 건드린 줄 — 전수 (4개 hunk, 그 외 0줄)

`diff -u`가 보고하는 hunk는 정확히 4개다. 아래 줄번호는 **수정 후** 기준.

### hunk 1 — 호출 지점 `_capture` 컷 루프 `:492-514`

| 줄 | 변경 | 기본 경로 논증 |
|---|---|---|
| 492 | `seg_name, seg_how, seg_n = None, None, None` → `seg_name, seg_how, seg_n, seg_bad = None, None, None, None` | **문장 수 불변**. 기존 상수 튜플 언팩의 arity가 3→4로 늘었을 뿐이다. 기본 경로에서 `seg_bad`는 `None`으로 묶였다가 511·556의 `is not None` 비교에만 쓰이고 아무도 읽지 않는다. 부수효과·호출·속성 접근 0 |
| 493 | `if seg_ann is not None and ok:` — **무수정** | 기본 경로에서 `seg_ann is None` → 분기 전체가 죽는다. 이 파일이 이미 채택한 옵트인 규율(`:885-888` 주석) 그대로 |
| 494-502 | 주석 9줄 신설 (분기 **안**) | 주석은 바이트코드가 없다 |
| 503-508 | `_seg_fetch(...)` → `_seg_fetch_guarded(...)` | **분기 안**. 기본 경로는 이 문장에 도달하지 않는다 |
| 509-510 | `if sarr is not None: seg_name, seg_n = _seg_write(...)` — **무수정** | 분기 안 |
| 511 | `else:` → `elif seg_bad is None:` | **분기 안**. 도달 불가. (거부된 컷은 이미 REFUSED 로그를 냈으므로 "no idseg"를 중복 출력하지 않게 하는 것뿐) |

`arr`(직전 depth 배열)을 **분기 밖 신규 문장 없이** 쓸 수 있는 이유는 구조적
불변식이다: `seg_ann`은 `_seg_attach`가 **살아 있는 render product**를 받았을
때만 non-None이고, 그 render product를 만드는 유일한 곳이 `_depth_attach`(`:391`)
이다. 따라서 `seg_ann is not None` ⟹ `depth_ann is not None`이고, 두 블록이
**같은 `ok`** 로 묶여 있으므로 depth 블록이 **이 컷에서 방금 실행되어** `arr`가
바인딩돼 있다. 그래도 `arr if depth_ann is not None else None`으로 한 겹 더
막아 뒀다(미래 리팩터 대비이지 현재 실경로가 아니다).

### hunk 2 — 컷 레코드 `:547-561`

| 줄 | 변경 | 기본 경로 논증 |
|---|---|---|
| 547-550 | `if seg_name:` 3줄 — **무수정** | 기본 경로에서 `seg_name is None` → False, 예전과 동일 |
| 551-555 | `if seg_try: cuts[fname]["idseg_retry"] = seg_try` | **`if seg_name:` 블록 안**. 도달 불가. 재페치가 실제로 있었던 컷에만 기록하므로 `idseg_fetch`는 계속 "어느 계단이 성공했나"만 뜻하고, 라운드 검증기의 `'t0' in fetch` 단언은 그대로 성립한다 |
| 556-561 | `elif seg_bad is not None: cuts[fname]["idseg_stale"] = seg_bad` | **신규 문장 아님** — 기존 `if`에 붙은 분기다. 기본 경로가 추가로 하는 일은 `None is not None` 비교 **한 번**이며 결과는 항상 False. 부수효과 0 |

거부된 컷에는 **`idseg` 키 자체가 없다.** `idseg`로 인덱싱하는 하위 소비자는 그
컷을 "페치가 비었던 컷"과 똑같이 건너뛰고, `idseg_stale`은 *왜* 인지 알고 싶은
검증기를 위한 양성 기록이다.

### hunk 3 — 상수 `:907-908` (+ 주석 3줄 `:904-906`)

```python
SEG_RETRY_ENV = "NEGOBS_SEG_RETRY"
SEG_RETRY_DEFAULT = 3
```

모듈 최상위 **리터럴 대입 2개**. 바로 위 `SEG_ENV`·`SEG_ANNOTATOR`(`:902-903`)와
문법적으로 같은 종류이며, 임포트 시 이름 2개를 묶는 것 외에 아무 일도 하지 않는다.
읽는 곳은 `_seg_retries()` 하나뿐이고 그건 `_seg_fetch_guarded`만 부른다.

### hunk 4 — 신설 헬퍼 블록 `:1041-1246` (206줄, 그중 주석/독스트링 122줄)

| 함수 | 줄 | 역할 | 유일한 호출자 |
|---|---|---|---|
| `_seg_retries` | 1086-1097 | `NEGOBS_SEG_RETRY` 기본 3, 쓰레기 값은 기본값으로 폴백(절대 raise 안 함) | `_seg_fetch_guarded` |
| `_seg_sha` | 1100-1115 | 배열 내용 sha256 16자 (dtype+shape 포함) | `_seg_fetch_guarded`, `_seg_witness` |
| `_seg_witness` | 1118-1131 | `("depth"\|"pose", sha)` | `_seg_fetch_guarded` |
| `_seg_verdict` | 1134-1154 | **순수 술어** `(is_stale, why)` — numpy·파일·어노테이터 무관 | `_seg_fetch_guarded` |
| `_seg_prev` | 1157-1176 | 직전 **채택** 컷의 triple. **첫 호출 때 생성**되어 함수 속성에 붙는다 | `_seg_fetch_guarded` |
| `_seg_stale_marker` | 1179-1196 | `<png stem>.idseg.STALE` JSON | `_seg_fetch_guarded` |
| `_seg_fetch_guarded` | 1199-1245 | 페치 + 검증 + 재페치 루프 + 마커 | `_capture` `:503` (옵트인 분기 안) |

기본 경로가 이 블록에서 실행하는 것은 **`def` 문 7개(이름 바인딩)** 가 전부다.
`import numpy`·`import hashlib`은 전부 **함수 안**에 있어(이 섹션의 기존 규율
`:731-734`) 임포트 시 아무것도 끌어오지 않는다. 상태(`_seg_prev.st`)는 **첫
호출 때** 만들어지므로 사이드카가 꺼져 있으면 **빈 dict조차 할당되지 않는다** —
이 명제는 테스트 [11]에서 기계적으로 확인한다.

### 그 외

`_seg_fetch`, `_seg_write`, `_seg_attach`, `_seg_detach`, depth 사이드카, 히트맵,
`_camband_*`, 드라이버 절반(`drive`) — **한 줄도 건드리지 않았다.**

---

## 3. 기본 경로 요약 논증 (3문장)

`NEGOBS_SEG_SIDECAR`가 unset이면 `_seg_attach`가 첫 문장에서 `None`을 반환하므로
`seg_ann is None`이고, 새 코드가 사는 `if seg_ann is not None and ok:` 블록 전체가
죽은 코드가 된다. 그 분기 밖에서 달라진 것은 (a) 기존 상수 튜플 언팩의 arity가
3→4로 늘어 `seg_bad=None`이 추가로 묶이는 것과 (b) 기존 `if seg_name:`에 붙은
`elif seg_bad is not None`이 `None is not None`을 **한 번 비교**하는 것뿐이며,
둘 다 새 문장이 아니고 호출·부수효과·파일 접근이 0이다. 모듈 최상위에는 리터럴
상수 2개와 `def` 7개가 늘었을 뿐이고, 이들이 필요로 하는 임포트는 전부 함수 본문
안에 있으므로 임포트 시간·임포트 실패 표면 모두 불변이다.

---

## 4. 기계 점검

### 4.1 AST

```
$ cd /home/vislab/Desktop/work_sy/Practice_NegObs
$ python3 -c "import ast,sys; ast.parse(open('scripts/run_data_render.py').read())"
$ echo $?
0
```

`pyflakes`는 기존 결함 2건(`:299` unused `math`, `:598` undefined `math` — 파일
`:589-593`이 스스로 문서화해 둔 선재 결함)만 보고하고 **신규 경고 0**.

### 4.2 unified diff (요약 — 전체는 4 hunk / **+216 −4**)

```diff
@@ -489,13 +489,26 @@
-                seg_name, seg_how, seg_n = None, None, None
+                seg_name, seg_how, seg_n, seg_bad = None, None, None, None
                 if seg_ann is not None and ok:
-                    sarr, smap, seg_how = _seg_fetch(seg_ann, sim_app,
-                                                     sc.PT_FAST["subframes"])
+                    # Per-cut stale validation + re-fetch (D79 ③). ...
+                    sarr, smap, seg_how, seg_try, seg_bad = _seg_fetch_guarded(
+                        seg_ann, sim_app, sc.PT_FAST["subframes"],
+                        arr if depth_ann is not None else None,
+                        dict(eye=[round(v, 4) for v in eye], yaw=s["yaw"],
+                             pitch=s["pitch"], hfov=s["hfov"]),
+                        scene_key, cid, fname, fp)
                     if sarr is not None:
                         seg_name, seg_n = _seg_write(sarr, smap, fp)
-                    else:
+                    elif seg_bad is None:
                         print(f"[sidecar] {fname}: no idseg ({seg_how})",
                               flush=True)
@@ -535,6 +548,17 @@
                     cuts[fname]["idseg_n_ids"] = seg_n
+                    if seg_try:
+                        cuts[fname]["idseg_retry"] = seg_try
+                elif seg_bad is not None:
+                    cuts[fname]["idseg_stale"] = seg_bad
@@ -877,6 +901,11 @@
 SEG_ANNOTATOR = "instance_id_segmentation"
+SEG_RETRY_ENV = "NEGOBS_SEG_RETRY"
+SEG_RETRY_DEFAULT = 3
@@ -1009,6 +1038,213 @@
+# per-cut stale guard — D79 ③ / W1B2_SEGFILL_REPORT.md §3.1 / D75 ②
+ ... (신설 헬퍼 7개, 위 §2 hunk 4 표)
```

**삭제된 4줄의 전수**: ① `seg_name, seg_how, seg_n = None, None, None`
(arity만 늘어 같은 자리에 되살아남) ② `sarr, smap, seg_how = _seg_fetch(...)`
2줄 (**옵트인 분기 안**, `_seg_fetch_guarded` 호출로 대체) ③ `else:`
(**옵트인 분기 안**, `elif seg_bad is None:`으로 대체). 즉 기본 경로가 실행하던
문장 중 **사라진 것은 0개**다.

---

## 5. 검증 A — 순수 파이썬 (GPU 불필요)

`experiments/v3_0823/code/w1c_seg_stale_test.py` — `_seg_fetch`만 가짜로 바꾸고
해시·목격자·술어·재시도 루프·마커 기록은 **정본 코드 그대로** 돌린다.

```
$ python3 experiments/v3_0823/code/w1c_seg_stale_test.py
...
52/52 checks passed — ALL PASS
```

증명 항목: ① 술어 진리표 5종 ② 해시가 dtype까지 포함 ③ 8컷 정상 경로 무재시도
④ **2회 stale 후 복구**(3회 페치, `idseg_fetch`는 여전히 `orch`) ⑤ **잔여 실패 시
`.idseg.STALE` 기록 + `.idseg.npz` 미기록** ⑥ 거부 컷이 **자기 나쁜 출력으로
재기준화하지 않음**(다음 컷도 계속 거부) ⑦ 진짜 동일 프레임은 통과 ⑧ depth 없을
때 pose 폴백 ⑨ `NEGOBS_SEG_RETRY` 예산 조정 + 쓰레기 값 폴백 ⑩ **빈 페치는
그대로 통과**(absent ≠ stale) ⑪ 사이드카 off 시 가드 상태 미할당.

`.STALE` 마커 실물 (테스트 [5]):

```json
{"annotator": "instance_id_segmentation", "cond": "L5", "fetch": "orch",
 "file": "L5__s1__0003.png", "idseg_sha": "1cd3ed4c198f7a7a",
 "prev_idseg_sha": "1cd3ed4c198f7a7a", "prev_witness_sha": "d9103a8f3dbc1f4d",
 "reason": "mask-repeat-while-frame-moved", "retries": 3, "scene": "scene04",
 "strict": null, "witness": "depth", "witness_sha": "de020491a2f4e66d",
 "marker": "L5__s1__0003.idseg.STALE"}
```

`check_data_run.py:256-261`은 `.png`만 열거해 orphan을 잡으므로 `.STALE`은 그
검사에 **보이지 않는다** — `.npy`/`.npz` 사이드카와 같은 이유.

---

## 6. 검증 B — 실기 (scene04, 스크래치 라운드 `260827_v3w1c_segprobe`)

`tmux w1c` · flock `/tmp/negobs_gpu.lock -o -w 14400 -E 201` ·
`NEGOBS_DATA_SIDECARS=1 NEGOBS_SEG_SIDECAR=1 NEGOBS_SEG_STRICT=1
NEGOBS_SCENE_CONFIG='{}'` (A 레시피 기본값).

### A팔 — 2조건 × 4카메라, seed 20260819 (조건 경계 포함) · 50 s, exit 0

| cut | idseg sha8 | depth sha8 | fetch | try | n_ids | stale? |
|---|---|---|---|---|---|---|
| `L0__s20260819__0000` | `2a07c96e` | `d6844ffa` | orch | 0 | 545 | no |
| `L0__s20260819__0001` | `6a52a5ab` | `927347c3` | orch | 0 | 947 | no |
| `L0__s20260819__0002` | `de38027e` | `4e668a79` | orch | 0 | 789 | no |
| `L0__s20260819__0003` | `12e4d02b` | `6cd217c5` | orch | 0 | 661 | no |
| `L5__s20260819__0000` | `2a07c96e` | `d6844ffa` | orch | 0 | 545 | no |
| `L5__s20260819__0001` | `6a52a5ab` | `927347c3` | orch | 0 | 947 | no |
| `L5__s20260819__0002` | `de38027e` | `4e668a79` | orch | 0 | 789 | no |
| `L5__s20260819__0003` | `12e4d02b` | `6cd217c5` | orch | 0 | 661 | no |

**이 팔이 뜻밖에 술어 자체를 실증했다.** `vk.sample_camera(scene, i, seed)`는
조건에 의존하지 않으므로 `L0__000i`와 `L5__000i`는 **같은 포즈**다. idseg도 depth도
조명 무관이라 두 컷은 **정당하게** 같은 마스크·같은 depth를 갖는다(PNG md5는 8/8
서로 다르다 — 실제로 다시 렌더된 프레임이다). 즉 마스크 반복 4쌍이 **depth 반복
4쌍과 정확히 같은 짝**을 이룬다. 해시만 보는 순진한 검출기라면 여기서 **8컷 중 4건을
오검출**했을 것이고, 두 갈래 술어는 이를 stale로 부르지 않는다 — 그리고 실제 결함이
"직전 컷 승계"이므로 비교 대상은 **직전 컷**이며 이 반복들은 4컷 떨어져 있다.

### B팔 — 1조건 × 8카메라, seed 20260820 (연속 8포즈, 결함이 사는 곳) · 48 s, exit 0

| cut | idseg sha8 | depth sha8 | fetch | try | n_ids | stale? |
|---|---|---|---|---|---|---|
| `L0__s20260820__0000` | `2dc911f3` | `dfc350e4` | orch | 0 | 678 | no |
| `L0__s20260820__0001` | `70957992` | `8a50a9c1` | orch | 0 | 700 | no |
| `L0__s20260820__0002` | `86eb34c1` | `f67504a3` | orch | 0 | 754 | no |
| `L0__s20260820__0003` | `9a93210a` | `d1045f18` | orch | 0 | 917 | no |
| `L0__s20260820__0004` | `90fd7a05` | `1f6ed433` | orch | 0 | 903 | no |
| `L0__s20260820__0005` | `4f797862` | `7b556739` | orch | 0 | 944 | no |
| `L0__s20260820__0006` | `cc6136f8` | `4bd2e227` | orch | 0 | 929 | no |
| `L0__s20260820__0007` | `6f53da08` | `42e31367` | orch | 0 | 652 | no |

```
  [ok] 8 cuts rendered
  [ok] idseg content hashes all DISTINCT — 8 unique / 8
  [ok] depth content hashes all DISTINCT — 8 unique / 8
  [ok] idseg_fetch == {'orch'} everywhere
  [ok] 0 .idseg.STALE markers on disk        (라운드 디렉터리 전체 = A+B 16컷)
  [ok] 0 idseg_stale records in variation.json
  [ok] every cut has an .idseg.npz
  [ok] no cut needed a re-fetch — [0,0,0,0,0,0,0,0]
  [ok] all captures ok
  9/9 assertions passed
```

**연속 8컷, stale 0, 재페치 0, 마커 0.** 로그의 `STALE`/`REFUSED`/`re-fetch` 줄도
0건이다. 합계 GPU **약 98초**(A 50 s + B 48 s), 16컷, 스크래치 라운드 밖 파일
생성·삭제 0.

---

## 7. 실행 방법 · 롤백

* 켜기: 기존과 동일. `NEGOBS_DATA_SIDECARS=1 NEGOBS_SEG_SIDECAR=1`
  (`NEGOBS_SEG_STRICT=1` 는 D74 ④대로 여전히 의무).
* 재시도 예산: `NEGOBS_SEG_RETRY=<n>` (기본 3, 0이면 재시도 없이 즉시 마커).
* 라운드 러너 쪽 변경 **0** — `run_260826_v3w1_lib_b2.sh`의 `IDSEG-STALE` 블록은
  그대로 두 번째 그물로 남는다. 다만 이제 그 그물에 걸리기 전에 렌더러가
  마커를 남기므로, 후속 러너는 `*.idseg.STALE` 유무와 `variation.json`의
  `idseg_stale` 키를 **유닛 실패 조건**으로 추가하는 것이 자연스럽다(별건).
* 롤백: hunk 1·2를 되돌리면 끝. hunk 3·4는 아무도 부르지 않는 죽은 코드가 된다.
