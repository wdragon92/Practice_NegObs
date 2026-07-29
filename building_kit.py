# -*- coding: utf-8 -*-
"""building_kit — 한국 건물 **매스(mass) 조립** 상위 레이어.

`facade_kit` 이 파사드 **표면 부착물**(기단·상가·실외기·간판·발코니·배관·∇)을
만든다면, 이 모듈은 그것들을 **어떤 덩어리 위에 어떤 순서로 붙일지**를 정한다.
즉 facade_kit 의 상위 조합 레이어이며, facade_kit 이 이미 구현한 것을 다시
만들지 않는다.

왜 전면 재작성인가 (현행 `scene_common.build_building` 진단)
-----------------------------------------------------------
현행 구성 = **직육면체 셸 1개 + 유리 쿼드 균일격자 + 파라펫** (+ 최근 덧붙인
문·선홈통·옥탑·기단·실외기). 실제 한국 건물과 어긋나는 지점은 셋이다.

1. **매스가 하나다.** 한국 건물은 저층 상가/상층 주거의 후퇴(setback),
   계단실·EV 코어 돌출, 필로티, 옥탑으로 최소 2~4개 덩어리다.
2. **창이 균일 격자다.** 코어는 창이 거의 없거나 세로로 길고, 주거는 발코니
   단위로 반복하고, 상가는 통유리다. `col_step` 등간격 격자는 사무소 패턴이며
   아파트·다세대에는 존재하지 않는다(조사 §3.2).
3. **지붕이 평평한 흰 뚜껑이다.** 실제로는 옥탑·물탱크(노후)·안테나·난간이 있고,
   주거지역 건물은 정북 사선제한으로 상부 매스가 계단형으로 잘려 있다.

프림 예산이 최우선 제약 (측정된 사실)
-------------------------------------
판정 1순위 시점은 카메라 h0.3 m · pitch −10° · vFOV 36° 이므로 프레임 상단은
지평 위 **+8.0°** 뿐이다. 거리 d 에서 프레임에 들어오는 최고 높이는

    z = 0.3 + d·tan(8°) ≈ 0.3 + 0.14·d
    d=10 → 1.7 · d=20 → 3.1 · d=34 → 5.1 · d=50 → 7.3 · d=90 → 12.9

33씬 창 프림이 4,173개인데 그 대부분이 이 상한 위, 즉 **프레임 밖**이었다는 것이
이 작업의 출발점이다. 그래서 이 모듈은 거리에 따라 **유형 자체를 강등**한다
(`fk.lod_tier`). d>80 m 면 어떤 유형이든 `backdrop`(프림 3~4)으로 떨어진다.

유형 × LOD 프림 예산표 (동당 · 기하 프림만) — **v1 재기준선 2026-07-29**
------------------------------------------------------------------------
`selfcheck()` 가 MockKit 으로 **실측**해 이 표와 대조한다(초과 시 실패).
표 값은 상한(budget)이고, **실측값은 괄호 안**이다. 대표 파사드 W=24 m ·
안길이 12 m · 유형별 표준 층수(shop_house 4 · apt 14 · office 9 · villa 5 ·
low_shop 1 · backdrop 10).

| kind        | near (<20 m) | mid (20~40) | far (40~80) | silhouette (>80) |
|-------------|--------------|-------------|-------------|------------------|
| `shop_house`| **59** (56)  | **30** (27) | **9** (6)   | 4 (3)            |
| `apt`       | **57** (54)  | **23** (20) | **15** (12) | 4 (4)            |
| `office`    | **31** (28)  | **15** (12) | **11** (8)  | 4 (3)            |
| `villa`     | **57** (54)  | **28** (25) | **10** (7)  | 4 (3)            |
| `low_shop`  | **36** (33)  | **17** (14) | **7** (4)   | 4 (3)            |
| `backdrop`  | 4 (3)        | 4 (3)       | 4 (3)       | 4 (3)            |

상한 = **실측 + 3** (물탱크·안테나·옥상간판이 동시에 켜지는 최악 경우, 각 1
프림 `[실측]`). `backdrop` 행과 `silhouette` 열만 예외로 **빌더 구조 상한 4**
(셸 1~2 + 파라펫 1 + 옥탑 1)를 쓴다. 표의 근거 등급은 `[추정]`이며 역할은
설계 목표가 아니라 **회귀 동결선**이다 — 자세한 사정은 `BUDGET` 주석 참조.

`backdrop` 은 거리와 무관하게 **원경 실루엣 전용**이다. 창 없음, 프림 3~4.

설계 규약 (facade_kit 과 동일 — 위반 시 과거에 실제로 터진 사고들)
-----------------------------------------------------------------
1. 좌표계 Z-up, 단위 m.
2. **`scene_common` 을 import 하지 않는다.** 프리미티브 헬퍼는 `facade_kit.Kit`
   으로 주입받는다. `pxr` 은 함수 내부에서만 지연 import 한다.
3. **RNG 100 % 결정적** — 내장 `hash()` 금지(PYTHONHASHSEED 로 프로세스마다
   바뀐다. 이 프로젝트에서 실제로 터진 버그다). `zlib.crc32` + `random.Random`.
4. **스케일 앵커 불가침** — 문 2.10 · 난간 1.20 · 실외기 0.80×0.55×0.30 ·
   주차 유효높이 2.10 · 계단 단높이 0.15~0.18. 개체차는 `_jit()` 로 **±8 % 이내**만.
5. **기존 `bd` 키만으로 동작해야 한다** (x0,x1,y0,y1,h,floors,axis,facade_x/y,
   face_dir,base_z). `kind` 는 선택 키이고 없으면 `infer_kind()` 가 추론한다.
   → **씬 파일 무수정 통합**이 가능해야 한다.
6. **v5.2 §6 "비움이 기본값"** — 기능 필수물만. 장식 금지.
7. **대기원근 없음.** 조사 2건이 독립적으로 "서울 실측 b_ext 로 90 m 원경 대비
   손실이 2.6~7 % 뿐이라 과하다"고 결론냈다.
8. 근거 없는 수치는 `[추정]`/`[지식]`/`[근거없음]` 표기 + 이유.

**총 높이 불변 규약**: `bd["h"]` 는 다른 씬 코드(차폐 검산 `obs`, 옥상 배치 등)가
읽는 값이므로 셸 상단은 반드시 `base_z + h` 로 유지한다. 층고를 비균등화할 때도
전체 높이에 맞춰 **비율로 스케일**한다(§`plan_levels`).

근거 문서
---------
* `Docs/surveys/korean_urban_backdrop.md` (2026-07-28)
  — §2 유형학 · §3.1 매스/층고 · §3.2 창 · §3.3 저층부 · §3.5 옥탑 · §4 우선순위
  · §5 씬 유형별 구성표 · §6 LOD 표 · §6.1 확정 파라미터
* `Docs/surveys/_dimension_index.md`
  — 옥탑(수평투영 ≤건축면적 1/8 · ≤12 m 면 높이·층수 불산입, 건축법 시행령 §119),
    **층수→높이 환산 4.0 m/층**(동 §119 ①9), 옥상간판(5~15층 · 최대길이 30 m ·
    높이 ≤15 m 이고 건물높이의 1/2 이하, 옥외광고물법 시행령 §15), 파라펫 1.2 m
* 정북 일조 사선제한 — **건축법 §61① → 시행령 §86①**:
  전용·일반주거지역에서 높이 **10 m 이하 부분은 인접 대지경계선에서 1.5 m 이상**,
  **10 m 초과 부분은 해당 부분 높이의 1/2 이상** 이격(2023.9.12 개정. 종전 9 m).
  등급 **법정(2차)** — law.go.kr 조문 본문이 JS 렌더링이라 원문 직접 인용은
  실패했고, 독립 2차 출처 2건(bigcase.ai · casenote.kr 검색 요약)이 일치한다.
  → `villa`(주거지역 저층 주거)에만 상부 계단형 후퇴를 기본 적용한다.
    `shop_house`/`office` 는 상업지역 전제라 §61① 적용 대상이 아니므로 적용 안 함.
"""

import math
import random
import zlib

import facade_kit as fk

__all__ = [
    "Mtls", "Plan", "KINDS",
    "build_korean_building", "infer_kind", "plan_building", "plan_levels",
    "prim_budget", "BUDGET", "selfcheck",
]

KINDS = ("shop_house", "apt", "office", "villa", "low_shop", "backdrop")

# ===========================================================================
# [0] 상수 — 스케일 앵커는 **랜덤화 금지**
# ===========================================================================
# facade_kit 이 이미 정의한 앵커는 재정의하지 않고 그대로 참조한다.
DOOR_H = fk.DOOR_H            # 2.10  법정: 피난·방화구조 규칙 §16
RAIL_H = fk.RAIL_H            # 1.20  법정: 건축법 시행령 §40
SLAB_T = fk.SLAB_T            # 0.21  법정: 주택건설기준 규정 §14의2 1호

# --- 층고 (조사 §3.1) ---------------------------------------------------
FH_APT = 2.80          # 확실: 한국PM 「아파트 층고」 현행 2.80~2.85
FH_VILLA = 2.80        # [지식]
FH_SHOP_G = 4.00       # [추정] 근생 1층 3.9~4.2 (1차 출처 미확보)
FH_SHOP_U = 3.30       # [추정] 근생 2층 이상
FH_LEGAL = 4.00        # 법정: 건축법 시행령 §119 ①9 — 층 구분 불명확 시 4 m/층
                       #       → 오피스 기본 층고로 쓴다(별도 1차 출처 없음).

# --- 필로티 (조사 §3.3(e)) ----------------------------------------------
PILOTI_CLEAR = 2.10    # **법정**: 주차장법 시행규칙 §6 주차부분 유효높이 2.1 이상
                       #   (흔히 인용되는 2.3 은 근거 없음 — 조사가 확인)
PILOTI_H = 2.90        # [추정] 필로티 층고 2.7~3.0 (유효 2.1~2.4 + 보·설비)
PILOTI_COL = 0.45      # [추정] RC 기둥 단면 0.45×0.45
PILOTI_PITCH = 5.40    # [추정] 기둥 중심 간격 — 주차구획 2.5×2 = 5.0~5.2 에서 유도
PILOTI_PORCH = 5.20    # [추정] 개방 깊이 — 주차 길이 5.0(법정 구획) + 여유

# --- 코어(계단실·EV) (조사 §3.2) ----------------------------------------
CORE_W = 3.00          # [지식] 세대 사이 코어 폭 2.5~3.5
CORE_PROUD = 0.60      # [추정] 코어 돌출. 발코니(법정 1.50)보다 작게 잡아
                       #   bd 바운딩 박스 밖으로 나가는 양을 최소화한다(통합 주의).
CORE_WIN_W = 0.90      # [추정] 계단실 세로 긴 창 폭

# --- 세대 베이 (조사 §3.2) ----------------------------------------------
BAY_APT = 9.00         # [지식] 아파트 1세대 파사드 폭 8~12
BAY_VILLA = 4.50       # [지식] 다세대 세대 폭
BAY_SHOP = 5.00        # [지식] 점포 간구 4~6

# --- 옥탑 (건축법 시행령 §119 ①5·9 — 법정) -------------------------------
PH_AREA_FRAC = 0.125   # 법정: 수평투영면적 ≤ 건축면적의 1/8 이면 층수 불산입
PH_H = 2.90            # [지식] 옥탑 높이 2.5~3.5 (법정 상한 12 — 초과분만 산입)
TANK_R = 0.90          # [지식] 고가수조 — **노후 저층 건물에만**. 신축엔 거의 없다
TANK_H = 1.60          #   (출처: 기계설비신문 「옥상 위 물탱크는 어디로 갔을까」)
ANT_H = 2.20           # [지식] 안테나 — 노후 건물 옥상

# --- 옥상간판 (옥외광고물법 시행령 §15 — 법정) ---------------------------
ROOFSIGN_LEN_MAX = 30.0    # 법정: 최대 길이 30 m
ROOFSIGN_H_MAX = 15.0      # 법정: 높이 15 m 이하 **이고** 건물높이의 1/2 이하
ROOFSIGN_FLOORS = (5, 15)  # 법정: 5~15층 건축물

# --- 차양(어닝) (서울시 옥외광고물 조례 — 법정) --------------------------
AWNING_OUT_ROAD = 1.00     # 법정: 도로 점용 시 1.00 이내
AWNING_OUT_FREE = 0.70     # 법정: 미점용 시 0.70 이내
AWNING_Z = 2.60            # [지식] 하단 설치 높이 2.4~2.8

# --- 저층부 후퇴 (오피스) ------------------------------------------------
SETBACK_OFFICE = 1.20      # [추정] 저층부 대비 타워 후퇴. 1차 출처 없음
                           #   (조사 §5 "저층부 화강석 + 캐노피"의 형태적 귀결)
# --- 정북 사선제한 계단형 (건축법 시행령 §86① — 법정 2차) ---------------
DAYLIGHT_STEP_Z = 10.0     # 법정: 높이 10 m 초과 부분부터 이격 강화
DAYLIGHT_STEP_IN = 1.60    # [추정] 계단 1단의 실제 후퇴 깊이. 조문은 "높이의 1/2
                           #   이상 이격"이라 대지 형상에 따라 값이 달라진다 →
                           #   시각 서명만 남기는 대표값.

# --- 유형 추론 경계 (infer_kind) -----------------------------------------
VILLA_GFA_MAX = 660.0  # 법정: 건축법 시행령 별표1 제2호 다목 — 다세대주택은
                       #   "주택으로 쓰는 1개 동의 바닥면적 합계 660 m² 이하이고
                       #   층수 4개 층 이하". 종전 상수 600(층수 무관)은 [근거없음].
VILLA_MIN_DEPTH = 7.0  # [추정·유도] 주거 세대가 성립하는 최소 안길이.
                       #   원룸형 다세대 전용 30 m² ÷ 간구 4.50(BAY_VILLA) ≈ 6.7 m
                       #   이 하한이고, 일반형 40~60 m² 면 8.9~13.3 m 다.
                       #   안길이 6 m 짜리 4층 건물은 세대 평면이 안 나온다 →
                       #   도로변 근생/상가주택으로 본다.
RESI_FH_MAX = 3.05     # [추정] 주거 층고대의 상한. 아파트 기준층 2.80~2.85(확실)
                       #   + 필로티·기계층 여유. 초과하면 근생(1층 3.9~4.2[추정])
                       #   이나 업무(4.0 법정 환산)가 섞인 것으로 본다.
                       #   **저층·고층 갈래가 같은 값을 쓴다**(경계 일원화).

# --- LOD 층수 상한 (조사 §6 LOD 표) --------------------------------------
ROW_CAP = {"near": 8, "mid": 5, "far": 2, "silhouette": 0}


# ===========================================================================
# [1] 결정적 RNG — hash() 금지
# ===========================================================================
def _rng(*keys):
    """결정적 `random.Random`. 내장 `hash()` 는 PYTHONHASHSEED 로 프로세스마다
    바뀌므로 **절대 쓰지 않는다**. crc32 는 표준 라이브러리 고정 다항식이라
    실행·플랫폼 무관하게 동일하다."""
    s = "|".join(str(k) for k in keys)
    return random.Random(zlib.crc32(s.encode("utf-8")) & 0xFFFFFFFF)


def _seed_of(*keys):
    s = "|".join(str(k) for k in keys)
    return zlib.crc32(s.encode("utf-8")) & 0xFFFFFFFF


def _builtin_hash_uses(src=None, path=None):
    """이 소스가 **내장 hash 를 실제로 쓰는지** 전수 판정. 프림 0.

    종전 검사는 소스 문자열에서 바늘을 부분문자열로 찾았는데, 그 바늘 리터럴이
    검사 코드 자신의 줄에 들어 있어 **자기매칭으로 영구 실패**했다(자기모순).
    여기서는 문자열·주석을 아예 보지 않는 두 경로로 판정한다.

      (a) AST — `Name(id="hash", ctx=Load)` 노드. 호출 `hash(x)` 뿐 아니라
          별칭 `f = hash` 도 잡는다. 재정의(`hash = ...`, `def hash`)는
          내장이 아니므로 Store 로 따로 세어 보고만 한다.
      (b) tokenize — STRING·COMMENT 토큰을 **제거한 뒤** 남은 코드에서
          `hash(` 를 찾는다. `builtins.hash(x)` 처럼 Attribute 로 우회한
          호출까지 잡히므로 (a) 를 보완한다. 이 파일의 바늘 리터럴은
          STRING 토큰이라 제거되어 자기매칭이 **구조적으로** 불가능하다.

    한계: `getattr(builtins, "ha"+"sh")` 처럼 이름을 런타임에 조립하는 경우는
    정적으로 잡을 수 없다 `[한계 명시]`.

    반환: (ast_hits, token_hits, shadow_lines) — 앞의 둘이 비면 미사용.
    """
    import ast
    import io
    import tokenize
    if src is None:
        with open(path or __file__, encoding="utf-8") as fh:
            src = fh.read()
    name = "ha" + "sh"                      # 토큰 분리 조립 — 자기매칭 방지
    tree = ast.parse(src)
    ast_hits, shadow = [], []
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id == name:
            (ast_hits if isinstance(node.ctx, ast.Load) else shadow).append(
                f"L{node.lineno}")
        elif isinstance(node, (ast.FunctionDef, ast.ClassDef)) \
                and node.name == name:
            shadow.append(f"L{node.lineno}")
    skip = {tokenize.STRING, tokenize.COMMENT}
    for nm in ("FSTRING_START", "FSTRING_MIDDLE", "FSTRING_END"):
        if hasattr(tokenize, nm):        # 3.12+ 는 f-string 을 조각 토큰으로 준다
            skip.add(getattr(tokenize, nm))
    code_only = []
    for tok in tokenize.generate_tokens(io.StringIO(src).readline):
        if tok.type not in skip:
            code_only.append(tok.string)
    joined = "".join(code_only)
    tok_hits = [] if (name + "(") not in joined else [
        f"L{i + 1}" for i, ln in enumerate(joined.splitlines())
        if (name + "(") in ln]
    return ast_hits, tok_hits, shadow


def _jit(rng, v, frac=0.08):
    """개체차 지터. **상한 ±8 % 고정** — 스케일 앵커를 뭉개지 않기 위한 하드 캡.
    frac 을 0.08 초과로 넘겨도 0.08 로 잘린다(사고 재발 방지)."""
    f = min(abs(float(frac)), 0.08)
    return float(v) * (1.0 + rng.uniform(-f, f))


def _clamp(v, lo, hi):
    return lo if v < lo else (hi if v > hi else v)


# ===========================================================================
# [2] 재질 역할 컨테이너
# ===========================================================================
class Mtls:
    """재질 역할 묶음. 현행 호출부가 넘기는 3개(shell·glass·parapet)만으로도
    전 역할이 채워지도록 **폴백 사슬**을 둔다 — 씬 파일 무수정 통합의 조건.

    역할
      shell   외벽 본체        glass  창·통유리
      parapet 파라펫·난간·금속  stone  기단 화강석 (없으면 parapet)
      metal   실외기·배관·거치대 (없으면 parapet)
      sign    간판 패널        (없으면 parapet)
      decal   소방 ∇ 붉은 표식  (없으면 sign)
      dark    필로티 안쪽·개구부 그늘 (없으면 shell)

    재질 경로 이름 규약(scene_common `_LOOK_RULES`)에 맞춰 호출부가
    "granite"/"stone" · "sign"/"placard" 토큰을 넣어 만들어 주면 룩 레이어가
    각각 stone · sign 역할로 분류한다.
    """

    __slots__ = ("shell", "glass", "parapet", "stone", "metal", "sign",
                 "decal", "dark")

    def __init__(self, shell, glass=None, parapet=None, stone=None,
                 metal=None, sign=None, decal=None, dark=None):
        self.shell = shell
        self.glass = glass if glass is not None else shell
        self.parapet = parapet if parapet is not None else shell
        self.stone = stone if stone is not None else self.parapet
        self.metal = metal if metal is not None else self.parapet
        self.sign = sign if sign is not None else self.parapet
        self.decal = decal if decal is not None else self.sign
        self.dark = dark if dark is not None else shell

    @classmethod
    def from_legacy(cls, shell_mtl, glass_mtl, parapet_mtl):
        """현행 `build_building(stage, prefix, bd, shell, glass, parapet)`
        시그니처 그대로 받는 어댑터."""
        return cls(shell_mtl, glass_mtl, parapet_mtl)

    @classmethod
    def coerce(cls, x):
        if isinstance(x, Mtls):
            return x
        if isinstance(x, dict):
            return cls(**{k: v for k, v in x.items()
                          if k in cls.__slots__})
        if isinstance(x, (tuple, list)):
            return cls(*x[:8])
        return cls(x)


# ===========================================================================
# [3] 순수 계산 — 유형 추론 · 층 레벨 · 매스 계획 (프림 0)
# ===========================================================================
def infer_kind(bd, dist=None):
    """`bd` 에 `kind` 가 없을 때의 유형 추론. **씬 파일 무수정 통합의 핵심.**

    판정 재료는 기존 키뿐이다(층수 · 평균 층고 · 풋프린트 · 거리).

        dist > 80                          → "backdrop"  (원경 실루엣 전용)
        floors <= 1                        → "low_shop"  (단층 근린상가)
        floors <= 4 이고 바닥면적합계 > 660   → "shop_house"(다세대 법정 규모 초과)
        floors <= 4 이고 안길이 < 7.0        → "shop_house"(세대 평면 불성립)
        floors <= 4 이고 h/floors > 3.05    → "shop_house"(근생 층고가 섞임)
        floors <= 4                        → "villa"     (다세대·빌라)
        floors <= 8                        → "office"    (업무시설)
        floors >= 9 이고 h/floors <= 3.05   → "apt"       (아파트: 층고 2.8~3.0)
        floors >= 9                        → "office"    (오피스: 층고 3.1~4.0)

    9층 이상 규칙의 근거: 아파트 기준층 층고는 **2.80~2.85**(확실, 조사 §3.1)이고
    오피스는 그보다 높다. 33씬 실측으로 9층 이상 22동 중 15동을 맞춘다(68 %).
    **정확도가 필요하면 `bd["kind"]` 로 덮어쓸 것** — 추론은 어디까지나 기본값이다.

    4층 이하 갈래 (v1 수정: 종전 "풋프린트 < 600 m²" 단일 기준은 `[근거없음]`
    이었고 24×6 m·4층·h12 상가주택을 villa 로 오분류했다)::

      ① **규모** — 다세대주택은 "주택으로 쓰는 1개 동의 바닥면적 합계 **660 m²
         이하**이고 층수 **4개 층 이하**" `[법령]` 건축법 시행령 별표1 제2호 다목.
         → 층당 풋프린트 × 층수가 660 을 넘으면 다세대일 수 없다.
      ② **안길이** — 세대 안길이 = 전용면적 ÷ 간구(4.50 = `BAY_VILLA`). 원룸형
         전용 30 m² 라도 6.7 m 가 필요하다 `[추정·유도]` → **7.0 m** 미만이면
         주거가 아니라 1실 깊이의 도로변 근생이다. 24×6 m 사례를 가르는 것이
         이 기준이다(면적·층고만으로는 못 가른다).
      ③ **평균 층고** — 경계 `RESI_FH_MAX` **3.05** 는 9층 이상 갈래가 쓰는 값과
         **동일하다**(경계 일원화). 실제 다세대 평균 층고는 2.7~3.0 이라 3.05 를
         넘지 않고, 1층 근생(3.9~4.2 `[추정]`)이 섞이면 4층 기준 3.4 안팎이 된다.

    세 기준 모두 `bd` 의 기존 키(x0..y1·h·floors·axis)만 쓴다. 프림 0.
    """
    d = float(dist) if dist is not None else float(bd.get("lod_dist", 0.0))
    if d > 80.0:
        return "backdrop"
    n = max(1, int(bd.get("floors", 1)))
    h = float(bd.get("h", n * FH_LEGAL))
    area = abs(float(bd["x1"]) - float(bd["x0"])) * \
        abs(float(bd["y1"]) - float(bd["y0"]))
    if n <= 1:
        return "low_shop"
    if n <= 4:
        if area * n > VILLA_GFA_MAX:        # ① 법정 규모 초과 → 다세대 아님
            return "shop_house"
        axis_y = (bd.get("axis", "y") == "y")
        depth = abs(float(bd["y1"]) - float(bd["y0"])) if axis_y else \
            abs(float(bd["x1"]) - float(bd["x0"]))
        if depth < VILLA_MIN_DEPTH:         # ② 세대 평면이 안 나오는 안길이
            return "shop_house"
        return "villa" if (h / n) <= RESI_FH_MAX else "shop_house"   # ③ 층고
    if n <= 8:
        return "office"
    return "apt" if (h / n) <= RESI_FH_MAX else "office"


def plan_levels(kind, total_h, floors, base_z=0.0):
    """각 층 **바닥 z** 리스트(길이 floors+1). 마지막 원소 = 최상층 천장 = 옥상.

    조사 §3.1 필수 규칙: **1층만 층고가 다르다**. 현행 `fstep = h/floors`
    등간격은 "CG로 읽히는" 큰 축이라 폐기 대상이다.

    다만 `total_h` 는 **바꾸지 않는다**(다른 씬 코드가 읽는 값이므로).
    그래서 유형별 선호 비율 `ground/typical` 만 지키고 전체 높이에 맞춰 스케일한다::

        r = ground_h_pref / floor_h_pref
        floor_h  = total_h / (r + floors - 1)
        ground_h = r * floor_h

    검산: r=1 이면 floor_h = total_h/floors 로 현행과 동일해진다.
    반환: (levels, ground_h, floor_h). 프림 0.
    """
    n = max(1, int(floors))
    H = float(total_h)
    g, t = _KIND_FH.get(kind, (FH_LEGAL, FH_LEGAL))
    r = float(g) / float(t)
    fh = H / (r + n - 1)
    gh = r * fh
    return fk.floor_levels(n, fh, gh, base_z), gh, fh


# 유형별 (1층 층고, 기준층 층고) 선호값. 비율만 쓰이고 절대값은 total_h 에 맞춰 스케일.
_KIND_FH = {
    "shop_house": (FH_SHOP_G, FH_SHOP_U),   # [추정] 근생 4.0 / 3.3
    "apt":        (PILOTI_H, FH_APT),       # 필로티 2.9[추정] / 기준층 2.80(확실)
    "office":     (FH_LEGAL + 0.5, FH_LEGAL),  # [추정] 로비층이 기준층보다 높다
    "villa":      (PILOTI_H, FH_VILLA),     # 필로티 2.9[추정] / 2.80[지식]
    "low_shop":   (FH_SHOP_G, FH_SHOP_G),
    "backdrop":   (FH_LEGAL, FH_LEGAL),     # 법정 환산 4.0 m/층
}


class Plan:
    """한 동의 **전부 순수 계산된** 배치 계획. 프림 0.

    `build_korean_building` 은 Plan 을 만든 뒤 그대로 실행만 한다. 덕분에
    프림 수·좌표를 스테이지 없이 검산할 수 있다(`selfcheck()`).
    """

    __slots__ = (
        "kind", "kind_raw", "tier", "dist", "seed",
        "x0", "x1", "y0", "y1", "base_z", "h", "top_z", "floors",
        "axis_y", "fdir", "plane", "Lx", "Ly", "W", "depth", "cx", "cy",
        "levels", "ground_h", "floor_h", "rows", "fac",
        "piloti", "n_col", "porch", "core_bays", "runs", "bay_w",
        "setback", "step_top", "rooftop", "tank", "antenna", "roof_sign",
        "shopfront", "awning", "signs", "balcony", "gas", "downpipe",
        "fire", "ac_mode", "ac_units", "opts",
    )

    def __init__(self):
        for s in self.__slots__:
            setattr(self, s, None)

    def __repr__(self):
        return (f"<Plan {self.kind}/{self.tier} d={self.dist:.0f} "
                f"W={self.W:.1f} floors={self.floors} rows={self.rows}>")


# `bd` 딕셔너리에서 그대로 읽어도 되는 **계획 스위치**. 씬이 켜고 끌 수 있는
# 값만 넣는다. 파생 기하(x0..y1·W·levels·fac)·유형(kind)·티어(tier)·거리(dist)는
# 계산 결과이므로 **절대 넣지 않는다** — 넣으면 계산을 되돌려 버린다.
_BD_SWITCHES = frozenset((
    "rows", "piloti", "porch", "n_col", "core_bays", "bay_w",
    "setback", "step_top", "rooftop", "tank", "antenna", "roof_sign",
    "shopfront", "awning", "signs", "balcony", "gas", "downpipe",
    "fire", "ac_mode", "ac_units",
))


def _bd_plane(bd, axis_y):
    """facade_x/facade_y 가 없어도 face_dir + 바운딩에서 파사드 평면을 복원한다."""
    fd = float(bd.get("face_dir", -1.0))
    if axis_y:
        if "facade_y" in bd and bd["facade_y"] is not None:
            return float(bd["facade_y"])
        return float(bd["y1"] if fd > 0 else bd["y0"])
    if "facade_x" in bd and bd["facade_x"] is not None:
        return float(bd["facade_x"])
    return float(bd["x1"] if fd > 0 else bd["x0"])


def plan_building(bd, dist=None, kind=None, seed=None, **over):
    """`bd` → `Plan`. **프림 0.** 여기서 모든 결정이 끝난다.

    `dist` 미지정 시 우선순위: `bd["lod_dist"]` → `|파사드 평면 좌표|`
    (현행 `build_building` 이 쓰던 것과 같은 근사 — 카메라가 대략 원점에 있다는 전제).

    `over` 로 어떤 계획 필드든 강제할 수 있다(`piloti=False`, `rows=3` 등).
    `bd` 에 같은 이름의 선택 키가 있으면 그것도 읽는다(씬에서 조절 가능).
    """
    p = Plan()
    p.x0 = float(min(bd["x0"], bd["x1"]))
    p.x1 = float(max(bd["x0"], bd["x1"]))
    p.y0 = float(min(bd["y0"], bd["y1"]))
    p.y1 = float(max(bd["y0"], bd["y1"]))
    p.base_z = float(bd.get("base_z", 0.0) or 0.0)
    p.h = float(bd["h"])
    p.top_z = p.base_z + p.h
    p.floors = max(1, int(bd["floors"]))
    p.Lx = p.x1 - p.x0
    p.Ly = p.y1 - p.y0
    p.cx = 0.5 * (p.x0 + p.x1)
    p.cy = 0.5 * (p.y0 + p.y1)
    p.axis_y = (bd.get("axis", "y") == "y")
    p.fdir = 1.0 if float(bd.get("face_dir", -1.0)) >= 0 else -1.0
    p.plane = _bd_plane(bd, p.axis_y)
    p.W = p.Lx if p.axis_y else p.Ly          # 파사드 가로 폭
    p.depth = p.Ly if p.axis_y else p.Lx      # 파사드에 수직인 안길이

    if dist is None:
        dist = bd.get("lod_dist")
    if dist is None:
        dist = abs(p.plane)
    p.dist = float(dist)
    p.tier = fk.lod_tier(p.dist)

    p.kind_raw = str(kind or bd.get("kind") or infer_kind(bd, p.dist))
    if p.kind_raw not in KINDS:
        p.kind_raw = infer_kind(bd, p.dist)
    # **거리에 따른 유형 강등** — 요구사항 1.
    p.kind = "backdrop" if p.tier == "silhouette" else p.kind_raw

    p.seed = int(seed) if seed is not None else _seed_of(
        p.kind, round(p.x0, 2), round(p.y0, 2), p.floors, round(p.h, 2))
    rng = _rng("plan", p.seed)

    p.levels, p.ground_h, p.floor_h = plan_levels(
        p.kind, p.h, p.floors, p.base_z)
    p.fac = fk.Facade(p.plane, p.fdir, *((p.x0, p.x1) if p.axis_y
                                         else (p.y0, p.y1)),
                      base_z=p.base_z, axis_y=p.axis_y, depth_ref=p.depth)

    # --- 창/발코니 반복 층수 (조사 §6 LOD 표 + §4 프림 재배분 규칙) ------
    cap = ROW_CAP[p.tier]
    if cap <= 0:
        p.rows = 0
    else:
        vis = fk.window_rows_visible(p.dist, p.floor_h, p.floors,
                                     ground_h=p.ground_h, base_z=p.base_z,
                                     near_dist=20.0, min_rows=2)
        p.rows = int(_clamp(min(vis, p.floors), 1, cap))

    # --- 유형별 기본 스위치 ---------------------------------------------
    k, t = p.kind, p.tier
    near = (t == "near")
    midp = (t in ("near", "mid"))

    p.piloti = (k in ("apt", "villa")) and midp and p.depth > (
        PILOTI_PORCH * 0.6 + 1.0) and p.ground_h >= PILOTI_CLEAR + 0.2
    p.porch = min(PILOTI_PORCH, max(2.0, p.depth * 0.45))
    p.n_col = int(_clamp(round(p.W / PILOTI_PITCH), 2, 5)) if p.piloti else 0

    # 코어 베이 — 아파트만. 폭 26 m 넘으면 2개소 [지식]
    p.core_bays = (1 if p.W < 26.0 else 2) if (k == "apt" and t != "silhouette") \
        else 0
    p.bay_w = {"apt": BAY_APT, "villa": BAY_VILLA}.get(k, BAY_SHOP)
    p.runs = _unit_runs(p.fac.u0, p.fac.u1, p.core_bays, CORE_W)

    p.setback = SETBACK_OFFICE if (k == "office" and p.floors >= 4) else 0.0
    # 정북 사선제한 계단형 — **주거지역 유형(villa)만**. 상업지역은 §61① 비대상.
    p.step_top = (k == "villa" and p.h > DAYLIGHT_STEP_Z + 1.0
                  and p.floors >= 4)

    p.rooftop = (k != "backdrop") or True          # 옥탑은 전 유형·전 티어
    # 노후 저층 = 물탱크·안테나 대상. 단 **3층 이상**만.
    #  · 고가수조는 상층 급수 압력 확보용이라 직결급수로 충분한 단층·2층
    #    근생 옥상에는 없다 `[지식]` (출처: 기계설비신문 — 부스터펌프 직결급수 전환).
    #  · 단층 상가 옥상의 안테나는 기능 근거가 없어 v5.2 §6 "비움이 기본값 —
    #    기능 필수물만, 장식 금지" 위반이 된다.
    old = (k in ("villa", "shop_house", "low_shop")) and p.floors >= 3
    p.tank = old and midp and rng.random() < 0.55
    p.antenna = old and near
    lo, hi = ROOFSIGN_FLOORS
    p.roof_sign = (k in ("shop_house", "office") and lo <= p.floors <= hi
                   and t in ("mid", "far") and rng.random() < 0.34)

    # 상가 파사드는 near·mid 까지만. 조사 §6 LOD 표가 **">40 m 저층부 = 기단만"**
    # 이라고 못박았는데 종전 조건(`t != "silhouette"`)은 far(40~80 m)에서도
    # 통유리·키커·출입문을 만들어 표와 어긋났고, low_shop/far 예산 초과(9>7)의
    # 직접 원인이었다. d=55 m 에서 통유리 1장의 화면 폭은 몇 픽셀이다.
    p.shopfront = k in ("shop_house", "low_shop") and t in ("near", "mid")
    p.awning = k in ("shop_house", "low_shop") and near
    p.signs = 2 if (k in ("shop_house", "low_shop") and near) else (
        1 if (k in ("shop_house", "low_shop") and t == "mid") else 0)
    p.balcony = (k == "apt" and t != "silhouette")
    p.gas = (k == "villa" and midp)         # 노출 가스배관 = 다세대 정체성
    p.downpipe = 2 if near else (1 if t == "mid" else 0)
    p.fire = midp and p.floors >= 2 and k != "backdrop"
    if k in ("shop_house", "low_shop"):
        p.ac_mode, p.ac_units = "eaves", (4 if near else (2 if t == "mid" else 0))
    elif k == "villa":
        p.ac_mode, p.ac_units = "perfloor", (5 if near else (3 if t == "mid" else 0))
    else:
        p.ac_mode, p.ac_units = None, 0     # 아파트 신축은 발코니 내장(§3.4 a)

    # bd 선택 키 · 명시 override 반영
    # **화이트리스트만** 반영한다(`_BD_SWITCHES`). 종전에는 `p.__slots__` 전체를
    # 훑어 bd 의 동명 키를 그대로 덮어썼는데, 그 루프가 바로 위에서 계산한 결과를
    # 되돌려 두 가지를 깨뜨렸다:
    #   ① `kind` — d>80 강등(`p.kind = "backdrop"`)을 bd["kind"] 가 되살려
    #      원경 건물이 near 유형 빌더로 조립됐다(자기검사 [5] 실패의 원인).
    #   ② `x0..y1` — 위에서 min/max 로 정규화한 좌표를 원본으로 되돌려,
    #      x0>x1 처럼 뒤집힌 bd 를 넘기면 음수 크기 박스가 나왔다.
    # 유형은 이미 `bd["kind"]` → `p.kind_raw` 경로로 반영돼 있으므로 손실 없다.
    for key in _BD_SWITCHES:
        if key in bd:
            setattr(p, key, bd[key])
    for key, val in over.items():
        if key in p.__slots__:
            setattr(p, key, val)
    p.opts = dict(over)
    return p


def _unit_runs(u0, u1, n_core, core_w):
    """코어를 사이에 끼운 **세대 구간(run)** 목록 [(ua, ub), ...] 과 코어 u 중심.

    반환 (runs, core_us). n_core=0 이면 runs=[(u0,u1)], core_us=[].
    n_core=1 → [run][core][run] · n_core=2 → [run][core][run][core][run].
    코어를 균등 분배해야 파사드 리듬이 실제 판상형처럼 끊긴다(조사 §3.2).
    프림 0.
    """
    W = float(u1) - float(u0)
    n = max(0, int(n_core))
    if n == 0 or W - n * core_w < 3.0:
        return [(float(u0), float(u1))], []
    wr = (W - n * core_w) / (n + 1)
    runs, cores, u = [], [], float(u0)
    for i in range(n + 1):
        runs.append((u, u + wr))
        u += wr
        if i < n:
            cores.append(u + core_w / 2.0)
            u += core_w
    return runs, cores


# ===========================================================================
# [4] 매스 빌더 — 프림을 실제로 만든다
# ===========================================================================
def _box(K, stage, path, c, s, mtl, collider=False):
    return K.box(stage, path, c, s, mtl, collider)


def _span_center_size(a0, a1, b0, b1, z0, z1, axis_y_is_x=True):
    """(x 범위, y 범위, z 범위) → (center, size)."""
    return ((0.5 * (a0 + a1), 0.5 * (b0 + b1), 0.5 * (z0 + z1)),
            (abs(a1 - a0), abs(b1 - b0), abs(z1 - z0)))


def _inner_range(p, inset):
    """파사드 쪽으로 `inset` 만큼 들어간 풋프린트 (x0,x1,y0,y1)."""
    x0, x1, y0, y1 = p.x0, p.x1, p.y0, p.y1
    if p.axis_y:
        if p.fdir > 0:
            y1 -= inset
        else:
            y0 += inset
    else:
        if p.fdir > 0:
            x1 -= inset
        else:
            x0 += inset
    return x0, x1, y0, y1


def build_mass(K, stage, prefix, p, M):
    """매스(덩어리). 유형별로 **1~3개 박스**. 필로티·후퇴·사선 계단형 포함.

    프림
      기본 1 · 오피스 저층부 후퇴 +1 · villa 사선 계단형 +1
      · 필로티(apt/villa near·mid) 는 셸을 들어올리고 **뒤벽 1 + 기둥 n_col**
    """
    prims = []
    z_bot = p.base_z
    if p.piloti:
        z_bot = p.base_z + min(p.ground_h, PILOTI_H + 0.4)
        # 필로티 뒤벽 — 개방 깊이 `porch` 만 비우고 나머지는 실체(충돌체 유지).
        rx0, rx1, ry0, ry1 = _inner_range(p, p.porch)
        if (rx1 - rx0) > 0.4 and (ry1 - ry0) > 0.4:
            c, s = _span_center_size(rx0, rx1, ry0, ry1, p.base_z, z_bot)
            prims.append(_box(K, stage, f"{prefix}/PilotiRear", c, s,
                              M.dark, True))
        # 기둥 — 개방 끝단(파사드 쪽)에 열 지어 선다. 유효높이 2.10 법정 확보.
        for i in range(p.n_col):
            u = p.fac.u0 + (i + 0.5) * p.W / max(1, p.n_col)
            c = p.fac.world(u, PILOTI_COL * 0.5 + 0.05,
                            p.base_z + (z_bot - p.base_z) / 2.0)
            s = p.fac.size(PILOTI_COL, PILOTI_COL, z_bot - p.base_z)
            prims.append(_box(K, stage, f"{prefix}/PilotiCol_{i}", c, s,
                              M.stone, True))

    z_top = p.top_z
    if p.step_top:
        # 정북 사선제한(시행령 §86①) 계단형 — 10 m 초과 부분이 후퇴한다.
        z_step = p.base_z + DAYLIGHT_STEP_Z
        # 하부 매스
        c, s = _span_center_size(p.x0, p.x1, p.y0, p.y1, z_bot, z_step)
        prims.append(_box(K, stage, f"{prefix}/Shell", c, s, M.shell, True))
        sx0, sx1, sy0, sy1 = _inner_range(p, DAYLIGHT_STEP_IN)
        c, s = _span_center_size(sx0, sx1, sy0, sy1, z_step, z_top)
        prims.append(_box(K, stage, f"{prefix}/ShellStep", c, s, M.shell, True))
    elif p.setback > 0.0:
        # 오피스 저층부 후퇴 — 저층부(2개 층)는 풀 풋프린트, 타워는 후퇴.
        z_pod = min(p.levels[min(2, p.floors)], z_top - 0.5)
        c, s = _span_center_size(p.x0, p.x1, p.y0, p.y1, z_bot, z_pod)
        prims.append(_box(K, stage, f"{prefix}/Podium", c, s, M.shell, True))
        sx0, sx1, sy0, sy1 = _inner_range(p, p.setback)
        c, s = _span_center_size(sx0, sx1, sy0, sy1, z_bot, z_top)
        prims.append(_box(K, stage, f"{prefix}/Shell", c, s, M.shell, True))
    else:
        c, s = _span_center_size(p.x0, p.x1, p.y0, p.y1, z_bot, z_top)
        prims.append(_box(K, stage, f"{prefix}/Shell", c, s, M.shell, True))
    return prims


def build_core(K, stage, prefix, p, M):
    """계단실·EV 코어 **돌출** + 세로 긴 창 + 출입문. 코어 1개소당 프림 2~3.

    조사 §3.2: "세대 사이 계단실/EV 코어(폭 2.5~3.5)가 파사드 리듬을 끊는
    결정적 요소이며 현행에는 없다." 코어에는 창이 거의 없거나 **세로로 길다**.

    **통합 주의**: 코어는 파사드면에서 `CORE_PROUD`(0.60) 만큼 bd 바운딩 밖으로
    나간다. 같은 파사드의 발코니가 이미 법정 1.50 을 나가므로 새로 생기는
    제약은 아니지만, 차폐 검산이 bd 박스만 쓰는 씬에서는 과소평가가 된다.
    """
    prims = []
    _, core_us = p.runs if isinstance(p.runs, tuple) else (None, [])
    for i, u in enumerate(core_us):
        h = p.top_z - p.base_z
        prims.append(_box(
            K, stage, f"{prefix}/Core_{i}",
            p.fac.world(u, CORE_PROUD / 2.0, p.base_z + h / 2.0),
            p.fac.size(CORE_W, CORE_PROUD, h), M.shell, True))
        # 계단실 세로 긴 창 — 1층 위부터 옥상 아래까지 한 줄
        zw0 = p.levels[min(1, p.floors)] + 0.4
        zw1 = p.top_z - 0.5
        if zw1 - zw0 > 1.0:
            prims.append(_box(
                K, stage, f"{prefix}/CoreStrip_{i}",
                p.fac.world(u, CORE_PROUD - 0.05, (zw0 + zw1) / 2.0),
                p.fac.size(CORE_WIN_W, 0.04, zw1 - zw0), M.glass))
        if p.tier == "near":
            # 공동현관 — 높이 2.10 은 **스케일 앵커**. 랜덤화 금지.
            prims.append(_box(
                K, stage, f"{prefix}/CoreDoor_{i}",
                p.fac.world(u, CORE_PROUD + 0.02, p.base_z + DOOR_H / 2.0),
                p.fac.size(1.60, 0.06, DOOR_H), M.glass))
    return prims


def build_rooftop(K, stage, prefix, p, M):
    """파라펫 + 옥탑 + (노후 한정) 물탱크·안테나 + (5~15층 한정) 옥상간판.

    프림: 파라펫 1 + 옥탑 1~2 + 물탱크 0~1 + 안테나 0~1 + 옥상간판 0~1.

    법정 근거
      · 파라펫(옥상 난간) **1.2 m 이상** — 건축법 시행령 §40.
        현행 0.5 는 규정 미달이었고 원경 실루엣도 그만큼 납작했다.
      · 옥탑 수평투영면적 **≤ 건축면적의 1/8** 이고 높이 **≤12 m** 면 층수·높이
        불산입 — 건축법 시행령 §119 ①5·9. → 풋프린트 상한을 그대로 쓴다.
      · 옥상간판 **5~15층**, 최대 길이 **30 m**, 높이 **≤15 m 이고 건물높이의
        1/2 이하** — 옥외광고물법 시행령 §15.

    물탱크는 **노후 저층 건물에만** 얹는다. 신축 아파트 옥상에 물탱크를 얹으면
    오히려 틀린다(출처: 기계설비신문 — 부스터펌프 직결급수로 전환).
    옥탑 위치는 옥상 중앙이 아니라 **코어 축 쪽으로 치우친다**(조사 §3.5).
    """
    prims = []
    rng = _rng(prefix, "roof", p.seed)
    zt = p.top_z

    # --- 파라펫 (법정 1.20) ---------------------------------------------
    prims.append(_box(K, stage, f"{prefix}/Parapet",
                      (p.cx, p.cy, zt + RAIL_H / 2.0),
                      (p.Lx + 0.20, p.Ly + 0.20, RAIL_H), M.parapet))

    # --- 옥탑 (법정 1/8 상한) -------------------------------------------
    area_max = p.Lx * p.Ly * PH_AREA_FRAC
    side = math.sqrt(max(0.5, area_max)) * rng.uniform(0.72, 1.0)
    pw = min(side, p.Lx * 0.5, 8.0)
    pdp = min(max(0.5, area_max / max(0.5, pw)), p.Ly * 0.5, 8.0)
    if pw > 1.4 and pdp > 1.4:
        ph = _jit(rng, PH_H)                    # ±8 % — 법정 12 m 와 무관하게 소형
        # 코어 축 쪽으로 치우침
        ox = p.cx + (p.Lx * 0.5 - pw * 0.5 - 0.6) * rng.uniform(-0.8, 0.8)
        oy = p.cy + (p.Ly * 0.5 - pdp * 0.5 - 0.6) * rng.uniform(-0.8, 0.8)
        prims.append(_box(K, stage, f"{prefix}/Penthouse",
                          (ox, oy, zt + ph / 2.0), (pw, pdp, ph), M.shell))
        if p.tier in ("near", "mid"):
            prims.append(_box(K, stage, f"{prefix}/PenthouseCap",
                              (ox, oy, zt + ph + 0.09),
                              (pw + 0.24, pdp + 0.24, 0.18), M.parapet))
        if p.tank:
            prims.append(K.cyl(stage, f"{prefix}/WaterTank",
                               (ox + pw * 0.5 + TANK_R + 0.3, oy,
                                zt + 0.35 + TANK_H / 2.0),
                               TANK_R, TANK_H, M.metal))
        if p.antenna:
            prims.append(K.cyl(stage, f"{prefix}/Antenna",
                               (ox - pw * 0.4, oy + pdp * 0.3,
                                zt + ph + ANT_H / 2.0),
                               0.035, ANT_H, M.metal))

    # --- 옥상간판 (법정 치수) -------------------------------------------
    if p.roof_sign:
        ln = min(p.W * 0.8, ROOFSIGN_LEN_MAX)
        sh = min(3.5, ROOFSIGN_H_MAX, p.h * 0.5)
        if ln > 3.0 and sh > 1.0:
            prims.append(_box(
                K, stage, f"{prefix}/RoofSign",
                p.fac.world(p.fac.mid, -0.6, zt + RAIL_H + sh / 2.0),
                p.fac.size(ln, 0.25, sh), M.sign))
    return prims


def build_window_bands(K, stage, prefix, p, M, mode="bay"):
    """창. **균일 격자를 쓰지 않는다** (조사 §3.2).

    mode
      "bay"        세대 베이 단위 창. 층당 `nb` 개(nb = 구간폭/베이폭, 상한 4).
                   shop_house · villa · low_shop 상층부.
      "band"       가로 창 밴드 1개/층. **오피스 중층 LOD** — 층당 프림 1.
      "curtain"    커튼월: 통유리 1장 + 층당 멀리언 밴드. office near/mid.

    프림
      bay     → rows × nb          (nb ≤ 4)
      band    → rows
      curtain → 1 + rows

    현행 `col_step` 격자는 파사드 폭 24 m 에서 층당 8~9개였다. bay 모드는 층당
    3~4개, band/curtain 은 층당 1개다. 이것이 창 프림 절감의 본체다.
    """
    prims = []
    rows = int(p.rows or 0)
    if rows <= 0 or p.W < 2.0:
        return prims
    lv = p.levels
    f0 = 1 if p.kind in ("shop_house", "low_shop", "apt", "villa") else 0
    f0 = min(f0, max(0, p.floors - 1))
    idx = [f for f in range(f0, min(p.floors, f0 + rows))]
    if not idx:
        return prims

    if mode == "curtain":
        z0 = lv[idx[0]] + 0.6
        z1 = min(lv[idx[-1]] + p.floor_h - 0.3, p.top_z - 0.3)
        if z1 - z0 > 1.0:
            prims.append(_box(
                K, stage, f"{prefix}/CurtainGlass",
                p.fac.world(p.fac.mid, -0.10, (z0 + z1) / 2.0),
                p.fac.size(p.W - 0.8, 0.05, z1 - z0), M.glass))
        for j, f in enumerate(idx):
            zb = lv[f] - 0.10
            if zb <= p.base_z + 0.2:
                continue
            prims.append(_box(
                K, stage, f"{prefix}/Mullion_{f}",
                p.fac.world(p.fac.mid, 0.04, zb),
                p.fac.size(p.W - 0.6, 0.12, 0.30), M.parapet))
        return prims

    if mode == "band":
        for f in idx:
            zc = lv[f] + min(1.6, p.floor_h * 0.55)
            prims.append(_box(
                K, stage, f"{prefix}/WinBand_{f}",
                p.fac.world(p.fac.mid, -0.12, zc),
                p.fac.size(p.W - 2.0, 0.04, 1.40), M.glass))
        return prims

    # --- bay 모드 --------------------------------------------------------
    # 창짝 최대 1.50 × 2.70 (확실 — KCC/이건). 침실창 1.5~1.8 × 1.4~1.5 [지식].
    nb = int(_clamp(round((p.W - 1.6) / max(2.5, p.bay_w)), 1, 4))
    bw = (p.W - 1.6) / nb
    ww = min(1.70, bw * 0.55)
    wh = 1.45
    for f in idx:
        zc = lv[f] + 0.90 + wh / 2.0          # 창대 0.90 [추정]
        for b in range(nb):
            u = p.fac.u0 + 0.8 + (b + 0.5) * bw
            prims.append(_box(
                K, stage, f"{prefix}/Win_{f}_{b}",
                p.fac.world(u, -0.10, zc),
                p.fac.size(ww, 0.04, wh), M.glass))
    return prims


def build_balconies(K, stage, prefix, p, M):
    """발코니 적층. **세대 구간(run)별로 `fk.build_balcony_stack` 을 호출**한다.

    facade_kit 의 `core_every` 는 균등 베이 전제라 "코어 폭 3.0 + 세대 폭 9.0"
    혼합 리듬을 못 만든다. 그래서 코어 사이 구간을 잘라 각각 넘긴다.

    프림 = Σ_run (nb_run × (rows−1) × 2) + (상부 수직 스트립 = 총 베이 수)

    **상부 수직 스트립**: `rows` 위쪽 층은 층별 슬래브·난간 대신 **베이당 세로
    박스 1개**로 압축한다. 15층 아파트에서 층별로 만들면 세대당 30 프림인데
    스트립은 1개다. 판정 프레임 상단(d=34 m → 5.1 m)보다 한참 위 구간이라
    실루엣만 남기면 충분하다는 §1.3 의 귀결이다.
    """
    prims = []
    runs, _ = p.runs if isinstance(p.runs, tuple) else ([(p.fac.u0, p.fac.u1)], [])
    rows = int(p.rows or 0)
    if rows <= 1:
        rows = 2                                # 최소 1개 층은 실물 발코니
    n_bay_total = 0
    for i, (ua, ub) in enumerate(runs):
        if ub - ua < 3.0:
            continue
        sub = fk.Facade(p.plane, p.fdir, ua, ub, p.base_z, p.axis_y,
                        depth_ref=p.depth)
        nb = max(1, int(round((ub - ua) / max(3.0, p.bay_w))))
        n_bay_total += nb
        prims += fk.build_balcony_stack(
            K, stage, f"{prefix}/Run{i}", sub, p.levels, M.parapet, M.parapet,
            bay_w=p.bay_w, core_every=0, start_floor=1,
            max_floors=rows, balusters=False, seed=p.seed + i)
        # 상부 압축 스트립
        z0 = p.levels[min(rows, p.floors)]
        z1 = p.top_z
        if z1 - z0 > 1.5:
            bw = (ub - ua) / nb
            for b in range(nb):
                u = ua + (b + 0.5) * bw
                prims.append(_box(
                    K, stage, f"{prefix}/BalStrip_{i}_{b}",
                    sub.world(u, fk.BALCONY_DEPTH * 0.5, (z0 + z1) / 2.0),
                    sub.size(bw - 0.30, fk.BALCONY_DEPTH, z1 - z0), M.parapet))
    return prims


def build_awning(K, stage, prefix, p, M):
    """차양(어닝) — 1층 상가 위. **프림 1.**

    법정(서울시 옥외광고물 조례): 돌출 길이 도로 **점용 시 1.00 이내**,
    **미점용 시 0.70 이내**. 하단 설치 높이 2.4~2.8 `[지식]`, 경사 15~25° 아래
    `[지식]` — 경사는 회전 프림이 필요해 **구현하지 않는다**(프림 예산 우선).
    """
    out = AWNING_OUT_ROAD
    zc = p.base_z + AWNING_Z + 0.06
    if zc > p.top_z - 0.3:
        return []
    return [_box(K, stage, f"{prefix}/Awning",
                 p.fac.world(p.fac.mid, out / 2.0, zc),
                 p.fac.size(min(p.W - 1.0, 12.0), out, 0.12), M.sign)]


def build_ext_stair(K, stage, prefix, p, M):
    """노출 옥외 계단 — 상가주택·빌라의 정체성. **프림 3.**

    법정(주택건설기준 규정 §16): 옥외계단 단높이 **≤0.20**, 단너비 **≥0.24**
    (실내보다 가파르다). 계단 각 단을 프림으로 만들면 층당 15~18개라 예산을
    넘긴다 → **경사 스트링거 1 + 계단참 1 + 난간 1** 로 압축한다.
    회전 프림(`oriented_box`)이 주입돼 있으면 경사판을 실제로 기울인다.
    난간 높이 **1.20**(법정 §40)은 스케일 앵커라 랜덤화 금지.
    """
    prims = []
    z0 = p.base_z
    z1 = p.levels[min(2, p.floors)]
    if z1 - z0 < 2.0 or p.W < 6.0:
        return prims
    u = p.fac.u1 - 1.6
    run = (z1 - z0) / 0.55                      # 경사 약 29° [추정]
    run = _clamp(run, 3.0, 7.0)
    out = 1.30                                  # 계단 유효폭 1.2 + 여유 [추정]
    if K.oriented_box is not None:
        ang = math.degrees(math.atan2(z1 - z0, run))
        c = p.fac.world(u, out / 2.0, (z0 + z1) / 2.0)
        s = p.fac.size(math.hypot(run, z1 - z0), out, 0.22)
        prims.append(K.oriented_box(stage, f"{prefix}/ExtStairSlab", c, s,
                                    M.stone, False, 0.0, -ang))
    else:
        prims.append(_box(K, stage, f"{prefix}/ExtStairSlab",
                          p.fac.world(u, out / 2.0, (z0 + z1) / 2.0),
                          p.fac.size(run, out, 0.22), M.stone))
    prims.append(_box(K, stage, f"{prefix}/ExtStairLanding",
                      p.fac.world(u, out / 2.0, z1 - 0.11),
                      p.fac.size(1.30, out, 0.22), M.stone))
    prims.append(_box(K, stage, f"{prefix}/ExtStairRail",
                      p.fac.world(u, out - 0.05, (z0 + z1) / 2.0 + RAIL_H / 2.0),
                      p.fac.size(run, 0.05, RAIL_H), M.metal))
    return prims


def build_meter_box(K, stage, prefix, p, M):
    """계량기함 — 다세대 저층부. **프림 1.**
    치수 `[근거없음]`(제조사 표준 미취득) → 0.60 × 0.20 × 0.70, 하단 +1.10 `[추정]`.
    조사 §3.4(c) 가 "계량기함·소화전·송수구"를 다세대 필수 부착물로 꼽았고,
    연결송수관 송수구 설치높이 **지면 +0.50~1.00** 은 법정이라 그 위에 둔다.
    """
    return [_box(K, stage, f"{prefix}/MeterBox",
                 p.fac.world(p.fac.u0 + 1.2, 0.11, p.base_z + 1.10 + 0.35),
                 p.fac.size(0.60, 0.22, 0.70), M.metal)]


def build_entrance(K, stage, prefix, p, M, canopy=True):
    """업무시설 주출입 — 통유리 + 캐노피. **프림 1~3.**
    문 높이는 **2.10 스케일 앵커**의 2연동(자동문 2매)으로 2.40 까지만 올린다.
    캐노피 돌출 2.0 `[추정]` — 조사 §5 "저층부 화강석, 대형 캐노피".
    """
    prims = []
    u = p.fac.mid
    dh = 2.40                                   # [추정] 자동문 유효높이
    prims.append(_box(K, stage, f"{prefix}/EntryGlass",
                      p.fac.world(u, -0.10, p.base_z + dh / 2.0),
                      p.fac.size(3.60, 0.06, dh), M.glass))
    if canopy:
        out = 2.00
        prims.append(_box(K, stage, f"{prefix}/EntryCanopy",
                          p.fac.world(u, out / 2.0, p.base_z + 3.30),
                          p.fac.size(6.00, out, 0.24), M.stone))
        prims.append(K.cyl(stage, f"{prefix}/EntryPost",
                           p.fac.world(u + 2.6, out - 0.25,
                                       p.base_z + 3.30 / 2.0),
                           0.09, 3.30, M.metal))
    return prims


def build_unit_number(K, stage, prefix, p, M):
    """동번호 대형 표기 — 아파트 측벽/코어 상부. **프림 1.**
    조사 §5: 12·13·17 배경 아파트의 필수 요소. 크기는 `[지식]`(1.5~2.5 m 급).
    """
    z = min(p.top_z - 1.2, p.levels[min(p.floors, 2)] + 1.2)
    return [_box(K, stage, f"{prefix}/UnitNo",
                 p.fac.world(p.fac.u0 + 1.8, 0.06, z),
                 p.fac.size(1.80, 0.05, 1.80), M.sign)]


# ===========================================================================
# [5] 유형별 조립
# ===========================================================================
def _fire(K, stage, prefix, p, M):
    """소방관 진입창 ∇ (법정 §18의2). pxr 미가용 환경(검산)에서는 얇은 박스로
    대체한다 — **프림 수는 동일**하므로 예산 검산이 성립한다."""
    if not p.fire:
        return []
    try:
        return fk.build_fire_access_marks(
            stage, prefix, p.fac, p.levels, M.decal,
            max_floors=max(1, int(p.rows or 1)))
    except ImportError:
        prims = []
        n_st = max(1, int(math.ceil(p.W / fk.FIRE_SPACING)))
        lv = p.levels[:-1][:max(1, int(p.rows or 1))]
        for s in range(n_st):
            u = p.fac.u0 + (s + 0.5) * (p.W / n_st)
            for f, zf in enumerate(lv):
                if not (2 <= f + 1 <= 11):
                    continue
                prims.append(_box(
                    K, stage, f"{prefix}/FireMark_{s}_{f + 1}",
                    p.fac.world(u, 0.010, zf + 0.80 + 0.60),
                    p.fac.size(fk.FIRE_TRI_D, 0.004, fk.FIRE_TRI_D), M.decal))
        return prims


def _attachments(K, stage, prefix, p, M):
    """공통 외피 부착물 — 실외기 · 우수관/가스 · 소방 ∇."""
    prims = []
    if p.ac_units:
        lv = p.levels
        if (p.ac_mode or "eaves") == "perfloor" and len(lv) > 2:
            # **1층 제외.** 근거 둘 —
            #  · 기하: `fk.build_aircon_units` 는 실외기를 층 바닥 +0.35 에 놓고
            #    냉매배관(길이 0.90)을 그 하단에서 아래로 내린다. 1층에 놓으면
            #    배관 하단 = base_z + 0.35 − 0.45 − 0.45 = **base_z − 0.55** 로
            #    지반을 뚫는다(자기검사 [7] villa d=14 실패의 원인, 실측 −0.550).
            #  · 실물: 다세대·빌라 1층은 부설주차장(필로티) 또는 근생이라 세대가
            #    없다 — 세대용 실외기가 붙는 최저 층은 2층이다 `[지식]`.
            #    주차 필로티 천장 아래에 실외기를 매다는 구성도 있으나 그것은
            #    "eaves" 모드의 일이고 perfloor 세대 배치와 섞으면 틀린다.
            lv = lv[1:]
        # "eaves" 모드의 `eaves_z` 는 fk 에서 **월드 절대 z**(기본 2.30)다.
        # 그대로 두면 base_z ≠ 0 인 건물 — 경사지·낙차 씬이 바로 그렇다 — 에서
        # 실외기가 제 건물 지반 아래에 붙는다(실측: base_z=3.4 → 배관 하단
        # base_z−2.00). **base_z 상대로 환산해서 넘긴다.**
        #   상한 2.30 = fk 기본값 `[지식]` · 하한 1.60 = 실외기 설치 높이대
        #   1.5~2.6 `[지식]` 의 아래끝 · `ground_h − 1.30` 은 실외기 상단(+0.55)이
        #   간판 밴드 하단(= ground_h − 0.85)을 넘지 않게 하는 값 `[추정]`.
        eaves_z = p.base_z + _clamp(p.ground_h - 1.30, 1.60, 2.30)
        prims += fk.build_aircon_units(
            K, stage, prefix, p.fac, M.metal, M.metal,
            levels=lv, mode=(p.ac_mode or "eaves"), eaves_z=eaves_z,
            per_level=2, count=p.ac_units, max_units=p.ac_units,
            bracket=(p.tier == "near"), pipe=(p.tier == "near"),
            seed=p.seed)
    if p.downpipe:
        prims += fk.build_downpipe_run(
            K, stage, prefix, p.fac, p.top_z, M.metal,
            n_pipes=int(p.downpipe), elbow=(p.tier == "near"),
            gas=bool(p.gas), gas_levels=p.levels, mtl_gas=M.metal,
            gas_variant="A", seed=p.seed)
    prims += _fire(K, stage, prefix, p, M)
    return prims


def _b_backdrop(K, stage, prefix, p, M):
    """원경 실루엣 전용. **프림 3~4.** 창 없음, 부착물 없음, 기단 없음.

    d>80 m 에서 프레임에 들어오는 높이는 12.9 m 이상이고 화면상 폭이 수 픽셀이라
    실루엣 외 정보는 전달되지 않는다(§1.3). 셸 + 파라펫 + 옥탑이면 충분하고,
    12층 이상만 상부 후퇴 매스 1개를 더해 스카이라인을 끊는다.
    """
    prims = []
    z_top = p.top_z
    if p.floors >= 12:
        z_mid = p.base_z + p.h * 0.72
        c, s = _span_center_size(p.x0, p.x1, p.y0, p.y1, p.base_z, z_mid)
        prims.append(_box(K, stage, f"{prefix}/Shell", c, s, M.shell, True))
        sx0, sx1, sy0, sy1 = _inner_range(p, min(2.0, p.depth * 0.2))
        c, s = _span_center_size(sx0, sx1, sy0, sy1, z_mid, z_top)
        prims.append(_box(K, stage, f"{prefix}/ShellTop", c, s, M.shell))
    else:
        c, s = _span_center_size(p.x0, p.x1, p.y0, p.y1, p.base_z, z_top)
        prims.append(_box(K, stage, f"{prefix}/Shell", c, s, M.shell, True))
    prims.append(_box(K, stage, f"{prefix}/Parapet",
                      (p.cx, p.cy, z_top + RAIL_H / 2.0),
                      (p.Lx + 0.20, p.Ly + 0.20, RAIL_H), M.parapet))
    rng = _rng(prefix, "bdrop", p.seed)
    side = math.sqrt(max(0.5, p.Lx * p.Ly * PH_AREA_FRAC)) * 0.85
    pw = min(side, p.Lx * 0.5, 8.0)
    pdp = min(side, p.Ly * 0.5, 8.0)
    if pw > 1.2 and pdp > 1.2:
        prims.append(_box(
            K, stage, f"{prefix}/Penthouse",
            (p.cx + (p.Lx * 0.5 - pw * 0.5 - 0.4) * rng.uniform(-0.8, 0.8),
             p.cy + (p.Ly * 0.5 - pdp * 0.5 - 0.4) * rng.uniform(-0.8, 0.8),
             z_top + PH_H / 2.0), (pw, pdp, PH_H), M.shell))
    return prims


def _b_low_shop(K, stage, prefix, p, M):
    """단층 근린상가. 평지붕, **간판이 파사드 대부분**."""
    prims = build_mass(K, stage, prefix, p, M)
    prims += fk.build_plinth(K, stage, prefix, p.x0, p.x1, p.y0, p.y1,
                             p.base_z, M.stone, height=1.10)
    if p.shopfront:
        nb = 3 if p.tier == "near" else 2
        prims += fk.build_shopfront(
            K, stage, prefix, p.fac, M.glass, M.parapet, M.stone,
            ground_h=p.ground_h, bay_w=max(3.0, p.W / nb),
            steps=(1 if p.tier == "near" else 0),
            shutter_box=(p.tier == "near"), max_bays=nb, seed=p.seed)
    if p.signs:
        # 간판 띠가 파사드의 대부분 — band_h 는 법정 상한 0.80 을 그대로 쓴다.
        prims += fk.build_signage(
            K, stage, prefix, p.fac, M.sign, M.sign,
            band_z=p.base_z + min(2.95, p.ground_h - 0.85), band_h=0.80,
            n_projecting=(1 if p.tier == "near" else 0), seed=p.seed)
    if p.awning:
        prims += build_awning(K, stage, prefix, p, M)
    prims += _attachments(K, stage, prefix, p, M)
    prims += build_rooftop(K, stage, prefix, p, M)
    return prims


def _b_shop_house(K, stage, prefix, p, M):
    """상가주택 — 1층 통유리 상가 + 2~4층 주거. **저층부 후퇴 없음**(대지 협소).
    간판 밴드 + 노출 계단이 정체성."""
    prims = build_mass(K, stage, prefix, p, M)
    prims += fk.build_plinth(K, stage, prefix, p.x0, p.x1, p.y0, p.y1,
                             p.base_z, M.stone, height=1.10)
    if p.shopfront:
        nb = 4 if p.tier == "near" else (3 if p.tier == "mid" else 1)
        prims += fk.build_shopfront(
            K, stage, prefix, p.fac, M.glass, M.parapet, M.stone,
            ground_h=p.ground_h, bay_w=max(3.0, p.W / nb),
            steps=(1 if p.tier == "near" else 0),
            shutter_box=(p.tier == "near"), max_bays=nb, seed=p.seed)
    if p.signs:
        prims += fk.build_signage(
            K, stage, prefix, p.fac, M.sign, M.sign,
            band_z=p.base_z + min(3.30, p.ground_h - 0.70),
            n_projecting=p.signs, seed=p.seed)
    if p.awning:
        prims += build_awning(K, stage, prefix, p, M)
    prims += build_window_bands(K, stage, prefix, p, M,
                                mode=("bay" if p.tier != "far" else "band"))
    if p.tier == "near":
        prims += build_ext_stair(K, stage, prefix, p, M)
    prims += _attachments(K, stage, prefix, p, M)
    prims += build_rooftop(K, stage, prefix, p, M)
    return prims


def _b_villa(K, stage, prefix, p, M):
    """다세대·빌라 — 4~5층, 주차 필로티, 외부 계단, 노출 가스배관(황색).
    한국 도시 보행 시점의 **최빈 배경**인데 현행 라이브러리에 0동이다(조사 §2)."""
    prims = build_mass(K, stage, prefix, p, M)
    if not p.piloti:
        prims += fk.build_plinth(K, stage, prefix, p.x0, p.x1, p.y0, p.y1,
                                 p.base_z, M.stone, height=1.10)
    prims += build_window_bands(K, stage, prefix, p, M,
                                mode=("bay" if p.tier != "far" else "band"))
    if p.tier == "near":
        prims += build_ext_stair(K, stage, prefix, p, M)
        prims += build_meter_box(K, stage, prefix, p, M)
    prims += _attachments(K, stage, prefix, p, M)
    prims += build_rooftop(K, stage, prefix, p, M)
    return prims


def _b_apt(K, stage, prefix, p, M):
    """아파트 — 발코니 적층 + **코어 돌출** + 필로티 1층 + 옥탑.
    실외기는 만들지 않는다(2021 시행령 §119 ①3 라목 개정 이후 발코니 내장 —
    조사 §3.4(a)). 창 격자도 만들지 않는다: 거실 통창은 발코니 뒤라 보이지 않는다."""
    prims = build_mass(K, stage, prefix, p, M)
    prims += build_core(K, stage, prefix, p, M)
    if not p.piloti:
        prims += fk.build_plinth(K, stage, prefix, p.x0, p.x1, p.y0, p.y1,
                                 p.base_z, M.stone, height=1.10)
    if p.balcony:
        prims += build_balconies(K, stage, prefix, p, M)
    if p.tier in ("near", "mid"):
        prims += build_unit_number(K, stage, prefix, p, M)
    prims += _attachments(K, stage, prefix, p, M)
    prims += build_rooftop(K, stage, prefix, p, M)
    return prims


def _b_office(K, stage, prefix, p, M):
    """업무시설 — 커튼월/창 밴드 + **저층부 후퇴** + 옥탑 기계실.
    저층부는 화강석 기단 + 대형 캐노피(조사 §5 의 06·08·11·14 구성)."""
    prims = build_mass(K, stage, prefix, p, M)
    prims += fk.build_plinth(K, stage, prefix, p.x0, p.x1, p.y0, p.y1,
                             p.base_z, M.stone, height=1.60)
    if p.tier in ("near", "mid"):
        prims += build_entrance(K, stage, prefix, p, M,
                                canopy=(p.tier == "near"))
    prims += build_window_bands(
        K, stage, prefix, p, M,
        mode=("curtain" if p.tier in ("near", "mid") else "band"))
    prims += _attachments(K, stage, prefix, p, M)
    prims += build_rooftop(K, stage, prefix, p, M)
    return prims


_BUILDERS = {
    "backdrop": _b_backdrop, "low_shop": _b_low_shop,
    "shop_house": _b_shop_house, "villa": _b_villa,
    "apt": _b_apt, "office": _b_office,
}

# 유형 × LOD 프림 상한 (동당, 기하 프림). selfcheck 가 실측과 대조한다.
#
# **이 표의 근거 등급은 `[추정]`이다.** 조사 §6 LOD 표는 거리별 *정성* 규칙
# (창/저층부/부착물을 어디까지 만들 것인가)만 주고 유형별 프림 상한 숫자는 주지
# 않는다. 즉 이 숫자들은 외부 근거가 아니라 **회귀 동결선**(freeze line)이다 —
# "여기서 더 늘어나면 누가 몰래 늘린 것"을 잡는 것이 유일한 역할이다.
#
# v1 재기준선 규칙 (2026-07-29) — 전 칸을 **하나의 규칙**으로 다시 채웠다:
#   상한 = 대표 bd(W=24 · depth=12 · 유형별 표준 층수) **실측 + 3**
#   +3 = 확률 부착물 3종(물탱크·안테나·옥상간판)이 동시에 켜지는 최악 경우.
#        각 1 프림 `[실측]`. 형상·시드 변동은 이 여유 안에 들어온다.
#   단 `backdrop` 행과 `silhouette` 열은 **빌더 구조 상한 4**를 그대로 쓴다
#   (`_b_backdrop` 이 낼 수 있는 최대 = 셸 1~2 + 파라펫 1 + 옥탑 1). 측정값이
#   아니라 코드 구조에서 나오는 값이라 헤드룸이 필요 없다.
#
# 종전 표는 코드보다 오래돼 실측과 4~8 프림씩 어긋나 있었다(모듈 docstring 의
# 괄호 "실측 대표값"도 같이 낡아 있었다). 재기준선으로 apt/mid 34→23,
# office/mid 22→15 처럼 **내려간 칸이 더 많다** — 표가 느슨해진 게 아니다.
BUDGET = {
    "shop_house": {"near": 59, "mid": 30, "far": 9, "silhouette": 4},
    "apt":        {"near": 57, "mid": 23, "far": 15, "silhouette": 4},
    "office":     {"near": 31, "mid": 15, "far": 11, "silhouette": 4},
    "villa":      {"near": 57, "mid": 28, "far": 10, "silhouette": 4},
    "low_shop":   {"near": 36, "mid": 17, "far": 7, "silhouette": 4},
    "backdrop":   {"near": 4, "mid": 4, "far": 4, "silhouette": 4},
}

# 위 표를 만든 실측값 (같은 규칙으로 재계산할 때의 기준선). selfcheck [5] 가
# 매번 이 값을 다시 재고 표와 대조하므로, 코드가 바뀌면 여기도 같이 갱신한다.
BUDGET_MEASURED = {
    "shop_house": {"near": 56, "mid": 27, "far": 6, "silhouette": 3},
    "apt":        {"near": 54, "mid": 20, "far": 12, "silhouette": 4},
    "office":     {"near": 28, "mid": 12, "far": 8, "silhouette": 3},
    "villa":      {"near": 54, "mid": 25, "far": 7, "silhouette": 3},
    "low_shop":   {"near": 33, "mid": 14, "far": 4, "silhouette": 3},
    "backdrop":   {"near": 3, "mid": 3, "far": 3, "silhouette": 3},
}


def prim_budget(kind, tier):
    """유형·LOD 티어의 **동당 프림 상한**. 프림 0."""
    return BUDGET.get(kind, BUDGET["backdrop"]).get(tier, 4)


# ===========================================================================
# [6] 최상위 API
# ===========================================================================
def build_korean_building(kit, stage, prefix, bd, mtls, dist=None, kind=None,
                          seed=None, plan=None, **over):
    """한국 건물 1동. **현행 `build_building` 의 교체 대상.**

    인자
      kit    `facade_kit.Kit(add_box, add_cylinder, oriented_box)` — 프리미티브 주입.
      stage  USD 스테이지.
      prefix 프림 경로 접두사.
      bd     기존 딕셔너리. **필수 키는 현행과 동일** (x0,x1,y0,y1,h,floors,
             axis,facade_x/y,face_dir,base_z). 선택 키: `kind`, `lod_dist`,
             그리고 `Plan.__slots__` 의 아무 필드(`piloti`, `rows`, `signs` …).
      mtls   `Mtls` · dict · 튜플 · 단일 재질 — `Mtls.coerce` 가 흡수한다.
             현행 3인자 호출은 `Mtls.from_legacy(shell, glass, parapet)`.
      dist   판정 카메라까지의 거리[m]. None 이면 `bd["lod_dist"]` → `|파사드 평면|`.
      kind   유형 강제. None 이면 `bd["kind"]` → `infer_kind()`.
      plan   미리 만든 `Plan` 을 재사용(검산·배치 최적화용).

    반환: 생성된 프림 리스트.

    거리에 따른 강등이 **유형 수준에서** 일어난다:
      d>80 m → 유형과 무관하게 `backdrop`(프림 3~4, 창 0).
      40<d≤80 → 창은 가로 밴드 1개/층, 부착물 없음, 저층부는 기단만.
      20<d≤40 → 저층부 상세 + 실외기·우수관, 반복 요소는 5개 층까지.
      d≤20 → 전부.
    """
    K = kit
    M = Mtls.coerce(mtls)
    p = plan if plan is not None else plan_building(
        bd, dist=dist, kind=kind, seed=seed, **over)
    return _BUILDERS[p.kind](K, stage, prefix, p, M)


# ===========================================================================
# [7] 자기검사 — `python3 building_kit.py`
# ===========================================================================
class _MockKit(fk.Kit):
    """프림을 만들지 않고 **세기만** 하는 Kit. 예산·좌표 검산 전용."""

    def __init__(self, oriented=False):
        self.calls = []
        self.add_box = self._box
        self.add_cylinder = self._cyl
        self.oriented_box = self._obox if oriented else None

    def _box(self, stage, path, center, size, mtl=None, collider=False):
        rec = ("box", path, tuple(float(v) for v in center),
               tuple(float(v) for v in size), collider)
        self.calls.append(rec)
        return rec

    def _cyl(self, stage, path, center, radius, height, mtl=None, **kw):
        rec = ("cyl", path, tuple(float(v) for v in center),
               (2 * float(radius), 2 * float(radius), float(height)), False)
        self.calls.append(rec)
        return rec

    def _obox(self, stage, path, center, size, mtl=None, collider=False,
              rotz=0.0, rotx=0.0):
        rec = ("obox", path, tuple(float(v) for v in center),
               tuple(float(v) for v in size), collider)
        self.calls.append(rec)
        return rec

    def box(self, stage, path, center, size, mtl=None, collider=False):
        return self._box(stage, path, center, size, mtl, collider)

    def cyl(self, stage, path, center, radius, height, mtl=None, **kw):
        return self._cyl(stage, path, center, radius, height, mtl, **kw)


def _demo_bd(kind, dist, floors=None, W=24.0, depth=12.0, base_z=0.0):
    """유형별 대표 bd. 층수는 유형의 실제 분포에서 고른다."""
    nf = floors if floors is not None else {
        "shop_house": 4, "apt": 14, "office": 9, "villa": 5,
        "low_shop": 1, "backdrop": 10}[kind]
    hh = {"shop_house": 3.3, "apt": 3.0, "office": 3.6, "villa": 2.9,
          "low_shop": 4.2, "backdrop": 4.0}[kind] * nf
    return dict(x0=-W / 2.0, x1=W / 2.0, y0=dist, y1=dist + depth,
                h=hh, floors=nf, axis="y", facade_y=dist, face_dir=-1.0,
                base_z=base_z, kind=kind)


def _run(kind, dist, **kw):
    K = _MockKit(oriented=True)
    bd = _demo_bd(kind, dist, **kw)
    p = plan_building(bd, dist=dist)
    prims = build_korean_building(K, None, "/W/B", bd, Mtls("sh", "gl", "pa"),
                                  dist=dist, plan=p)
    return p, K, prims


def selfcheck(verbose=True):
    """프림 수 · 좌표 · 결정성 검산. 렌더/GPU 를 쓰지 않는다. 실패 시 AssertionError."""
    ok = []

    def chk(name, cond, extra=""):
        ok.append(bool(cond))
        if verbose:
            print(f"  [{'OK ' if cond else 'FAIL'}] {name}{(' — ' + extra) if extra else ''}")
        return bool(cond)

    print("=" * 74)
    print("building_kit 자기검사")
    print("=" * 74)

    # --- 1. 결정적 RNG -----------------------------------------------------
    print("\n[1] 결정적 RNG (hash() 미사용)")
    a = [_rng("x", 1).random() for _ in range(3)]
    b = [_rng("x", 1).random() for _ in range(3)]
    chk("_rng 재현성", a == b)
    chk("_rng 키 분리", _rng("x", 1).random() != _rng("x", 2).random())
    # 문자열 부분검색은 검사 코드 자신의 리터럴에 자기매칭돼 영구 실패했다.
    # → AST(이름 로드) + tokenize(문자열·주석 제거 후 호출 형태) 이중 전수.
    h_ast, h_tok, h_shadow = _builtin_hash_uses(path=__file__)
    chk("소스에 내장 hash 호출·별칭 없음 (AST+토큰 전수)",
        not h_ast and not h_tok,
        f"AST 이름로드 {len(h_ast)}건 · 토큰 {len(h_tok)}건 · 재정의 {len(h_shadow)}건"
        + (f" {(h_ast + h_tok)[:4]}" if (h_ast or h_tok) else ""))
    r = random.Random(0)
    chk("_jit ±8 % 하드캡", all(
        0.92 - 1e-9 <= _jit(r, 1.0, 0.5) <= 1.08 + 1e-9 for _ in range(500)))

    # --- 2. 프레임 상한 (facade_kit 과 동일해야) ---------------------------
    print("\n[2] 판정 프레임 상한 z = 0.3 + 0.14·d")
    for d, want in ((10, 1.71), (20, 3.11), (34, 5.08), (90, 12.94)):
        got = fk.frame_ceiling(d)
        chk(f"d={d} m → {got:.2f} m", abs(got - want) < 0.02)

    # --- 3. 층 레벨: 총 높이 보존 + 1층만 다른 층고 -------------------------
    print("\n[3] plan_levels — 총 높이 불변 + 1층 비균등")
    for kind in KINDS:
        for (H, n) in ((10.0, 4), (45.0, 15), (4.2, 1), (22.0, 7)):
            lv, gh, fh = plan_levels(kind, H, n, base_z=3.0)
            if not chk(f"{kind} H={H} n={n} 상단 일치",
                       abs(lv[-1] - (3.0 + H)) < 1e-9,
                       f"lv[-1]={lv[-1]:.6f}"):
                break
    lv, gh, fh = plan_levels("shop_house", 20.0, 5)
    chk("shop_house 1층 층고 > 기준층", gh > fh, f"{gh:.2f} vs {fh:.2f}")
    lv, gh, fh = plan_levels("backdrop", 20.0, 5)
    chk("backdrop 은 등간격(법정 4 m/층 비율)", abs(gh - fh) < 1e-9)

    # --- 4. 유형 추론 -------------------------------------------------------
    print("\n[4] infer_kind")
    cases = [
        (dict(x0=0, x1=12, y0=0, y1=5.5, h=4.2, floors=1), 13.5, "low_shop"),
        (dict(x0=0, x1=24, y0=0, y1=6, h=12.0, floors=4), 26.0, "shop_house"),
        (dict(x0=0, x1=10, y0=0, y1=8, h=11.0, floors=4), 16.0, "villa"),
        (dict(x0=0, x1=10, y0=0, y1=18, h=26.0, floors=8), 24.0, "office"),
        (dict(x0=0, x1=12, y0=0, y1=22.4, h=45.0, floors=15), 34.0, "apt"),
        (dict(x0=0, x1=12, y0=0, y1=30, h=38.0, floors=10), 54.0, "office"),
        (dict(x0=0, x1=20, y0=0, y1=8, h=44.0, floors=15), 84.0, "backdrop"),
    ]
    for bd, d, want in cases:
        got = infer_kind(bd, d)
        chk(f"floors={bd['floors']} d={d} → {got}", got == want, f"기대 {want}")

    # --- 5. 프림 예산 -------------------------------------------------------
    print("\n[5] 유형 × LOD 프림 예산 (동당, 파사드 24 m)")
    dists = {"near": 14.0, "mid": 30.0, "far": 55.0, "silhouette": 95.0}
    print(f"    {'kind':12s} {'near':>12s} {'mid':>12s} {'far':>12s} {'sil':>12s}")
    table = {}
    for kind in KINDS:
        row = []
        for tier, d in dists.items():
            p, K, prims = _run(kind, d)
            n = len(K.calls)
            eff = p.kind
            cap = prim_budget(eff, p.tier)
            row.append((n, cap, eff))
            table[(kind, tier)] = n
        print(f"    {kind:12s} " + " ".join(
            f"{n:4d}/{cap:<3d}({e[:3]})" for n, cap, e in row))
    # 표를 만든 기준선(BUDGET_MEASURED)과의 드리프트를 알려만 준다(검사 아님).
    drift = [(k, t, table[(k, t)], BUDGET_MEASURED[k][t])
             for k in KINDS for t in dists
             if table[(k, t)] != BUDGET_MEASURED[k].get(t)]
    print("    기준선 드리프트: " + ("없음" if not drift else
                                     f"{len(drift)}칸 {drift[:4]} → BUDGET 재기준선 필요"))
    bad = []
    for kind in KINDS:
        for tier, d in dists.items():
            p, K, _ = _run(kind, d)
            if len(K.calls) > prim_budget(p.kind, p.tier):
                bad.append((kind, tier, len(K.calls),
                            prim_budget(p.kind, p.tier)))
    chk("전 유형·전 티어가 예산 이내", not bad, str(bad))
    chk("backdrop 프림 3~5", 3 <= table[("backdrop", "far")] <= 5)
    chk("d>80 은 유형 무관 강등",
        all(_run(k, 95.0)[0].kind == "backdrop" for k in KINDS))

    # --- 6. 스케일 앵커 좌표 ------------------------------------------------
    print("\n[6] 스케일 앵커 (랜덤화 금지 대상)")
    _, K, _ = _run("shop_house", 14.0)
    doors = [c for c in K.calls if "Door" in c[1] and "Head" not in c[1]]
    chk("상가 출입문 높이 = 2.10", doors and
        all(abs(max(c[3]) - DOOR_H) < 1e-6 or abs(c[3][2] - DOOR_H) < 1e-6
            for c in doors), str([c[3] for c in doors]))
    _, KA, _ = _run("apt", 30.0)
    rails = [c for c in KA.calls if "BalconyRail" in c[1]]
    chk("발코니 난간 높이 = 1.20", rails and
        all(abs(c[3][2] - RAIL_H) < 1e-6 for c in rails),
        f"{len(rails)}개")
    _, KV, _ = _run("villa", 14.0)
    acs = [c for c in KV.calls if "/AcUnit_" in c[1]]

    def _within(v, ref):
        return abs(v - ref) <= ref * 0.08 + 1e-9
    chk("실외기 0.80×0.55×0.30 ±8 % 이내", acs and all(
        _within(c[3][0], fk.AC_W) and _within(c[3][2], fk.AC_H)
        and _within(c[3][1], fk.AC_D) for c in acs), f"{len(acs)}대")
    cols = [c for c in KV.calls if "PilotiCol" in c[1]]
    chk("필로티 기둥 유효높이 ≥ 2.10(법정)", cols and
        all(c[3][2] >= PILOTI_CLEAR - 1e-9 for c in cols),
        f"{len(cols)}본 h={cols[0][3][2]:.2f}" if cols else "없음")

    # --- 7. 기하 정합 -------------------------------------------------------
    print("\n[7] 기하 정합")
    for kind in KINDS:
        for d in (14.0, 30.0, 55.0, 95.0):
            p, K, _ = _run(kind, d)
            shells = [c for c in K.calls if c[1].endswith(("/Shell",
                                                           "/ShellStep",
                                                           "/ShellTop"))]
            top = max(c[2][2] + c[3][2] / 2.0 for c in shells)
            if not chk(f"{kind} d={d:.0f} 셸 상단 = base+h",
                       abs(top - p.top_z) < 1e-6, f"{top:.3f} vs {p.top_z:.3f}"):
                break
            # **전 프림**을 본다(종전에는 "Step" 경로를 제외했다). 실측 최저는
            # `ShopStep`(계단판 두께 여유 0.02 로 인한 1 cm 매입) 하나뿐이고
            # 나머지는 정확히 base_z 다 → 허용치를 −0.35 에서 **−0.05** 로 조인다.
            # 종전 −0.35 는 −0.30 짜리 관통을 놓치는 과대 여유였다.
            bot = min(c[2][2] - c[3][2] / 2.0 for c in K.calls)
            if not chk(f"{kind} d={d:.0f} 지반 아래 프림 없음",
                       bot >= p.base_z - 0.05, f"최저 {bot:.3f}"):
                break
    # 옥탑 법정 상한 (건축면적 1/8)
    for kind in KINDS:
        p, K, _ = _run(kind, 30.0)
        ph = [c for c in K.calls if c[1].endswith("/Penthouse")]
        if ph:
            area = ph[0][3][0] * ph[0][3][1]
            chk(f"{kind} 옥탑 수평투영 ≤ 건축면적/8",
                area <= p.Lx * p.Ly * PH_AREA_FRAC + 1e-6,
                f"{area:.1f} ≤ {p.Lx * p.Ly / 8:.1f} m²")
    # 파라펫 1.2 (법정)
    for kind in KINDS:
        _, K, _ = _run(kind, 30.0)
        par = [c for c in K.calls if c[1].endswith("/Parapet")]
        chk(f"{kind} 파라펫 1.20(법정 §40)",
            par and abs(par[0][3][2] - RAIL_H) < 1e-9)

    # --- 8. 경로 충돌 -------------------------------------------------------
    print("\n[8] 프림 경로 유일성")
    for kind in KINDS:
        for d in (14.0, 30.0, 55.0, 95.0):
            _, K, _ = _run(kind, d)
            paths = [c[1] for c in K.calls]
            if not chk(f"{kind} d={d:.0f} 경로 중복 없음",
                       len(paths) == len(set(paths)),
                       str([q for q in paths if paths.count(q) > 1][:3])):
                break

    # --- 9. bd 호환 (신규 키 없이) ------------------------------------------
    print("\n[9] 기존 bd 키만으로 동작")
    legacy = dict(x0=34.0, x1=46.0, y0=-15.0, y1=7.4, h=45.0, floors=15,
                  axis="x", facade_x=34.0, face_dir=-1.0, base_z=0.0)
    K = _MockKit()
    prims = build_korean_building(K, None, "/W/B", legacy,
                                  Mtls.from_legacy("sh", "gl", "pa"))
    p = plan_building(legacy)
    chk("scene13 A101 (kind 키 없음) 동작",
        len(prims) > 0 and p.kind in KINDS,
        f"kind={p.kind} tier={p.tier} 프림={len(prims)}")
    minimal = dict(x0=0, x1=20, y0=10, y1=18, h=12.0, floors=4)
    K2 = _MockKit()
    prims2 = build_korean_building(K2, None, "/W/B2", minimal, "single_mtl")
    chk("facade_*·face_dir·base_z 결측도 동작", len(prims2) > 0,
        f"프림={len(prims2)}")

    # --- 10. 결정성 (2회 실행 동일) ------------------------------------------
    print("\n[10] 빌드 결정성")
    same = True
    for kind in KINDS:
        _, K1, _ = _run(kind, 30.0)
        _, K2, _ = _run(kind, 30.0)
        same = same and (K1.calls == K2.calls)
    chk("동일 입력 → 동일 프림·좌표", same)

    print("\n" + "=" * 74)
    n_ok, n = sum(ok), len(ok)
    print(f"검사 {n_ok}/{n} 통과")
    print("=" * 74)
    if n_ok != n:
        raise AssertionError(f"자기검사 실패 {n - n_ok}건")
    return True


# ---------------------------------------------------------------------------
# 33씬 실측 — scenes/ 가 옆에 있으면 현행 대비 프림 증감을 계산한다.
# ---------------------------------------------------------------------------
def _scan_scenes(verbose=True):
    import ast
    import glob
    import os
    root = os.path.dirname(os.path.abspath(__file__))
    dirs = [os.path.join(root, "scenes", "main"),
            os.path.join(root, "scenes", "batch1")]
    if not any(os.path.isdir(d) for d in dirs):
        if verbose:
            print("\n[33씬 실측] scenes/ 없음 — 건너뜀")
        return None
    REQ = {"x0", "x1", "y0", "y1", "h", "floors"}
    DEF_WIN = dict(w=1.2, h=1.6, inset=0.15, col_step=2.5, margin=2.0)

    def _lit(n):
        try:
            return ast.literal_eval(n)
        except Exception:
            return None

    def _as_dict(node):
        if isinstance(node, ast.Dict):
            o = {}
            for k, v in zip(node.keys, node.values):
                kk = _lit(k)
                if isinstance(kk, str):
                    o[kk] = _lit(v)
            return o
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
                and node.func.id == "dict":
            return {kw.arg: _lit(kw.value) for kw in node.keywords if kw.arg}
        return None

    rows = []
    for d in dirs:
        for f in sorted(glob.glob(os.path.join(d, "scene*.py"))):
            tree = ast.parse(open(f, encoding="utf-8").read())
            win = None
            bds = []
            for node in ast.walk(tree):
                dd = _as_dict(node)
                if not dd:
                    continue
                if REQ.issubset(dd.keys()):
                    if any(dd[k] is None for k in REQ):
                        continue
                    bds.append(dd)
                elif win is None and set(dd.keys()) >= {"w", "h", "inset",
                                                        "col_step", "margin"}:
                    win = dd
            for b in bds:
                b["_scene"] = os.path.basename(f)
                b["_win"] = win or DEF_WIN
            rows += bds
    if not rows:
        return None

    def cur_prims(bd, wd):
        """현행 build_building(LOOK_V1=True) 프림 수 재현."""
        base = float(bd.get("base_z", 0.0) or 0.0)
        Lx, Ly = bd["x1"] - bd["x0"], bd["y1"] - bd["y0"]
        hh, nfl = float(bd["h"]), int(bd["floors"])
        fstep = hh / nfl
        ay = bd.get("axis", "y") == "y"
        usable = (Lx if ay else Ly) - 2 * wd["margin"]
        ncols = max(1, int(usable / wd["col_step"]))
        dist = float(bd.get("lod_dist",
                            abs(bd.get("facade_y" if ay else "facade_x", 0.0))))
        nrows = fk.window_rows_visible(dist, fstep, nfl, base_z=base,
                                       near_dist=20.0, min_rows=2)
        W = Lx if ay else Ly
        n = 1 + nrows * ncols + nrows + 1 + 1 + 12 + 2
        n += max(1, int(math.ceil(W / 40.0))) * sum(
            1 for i in range(min(nrows, nfl)) if 2 <= i + 1 <= 11)
        n += max(2, int(W / 12.0) + 1)
        if min(4.2, Lx * 0.34) > 1.2 and min(3.4, Ly * 0.34) > 1.2:
            n += 2
        return n, nrows * ncols

    tot_cur = tot_new = win_cur = 0
    kinds = {}
    tiers = {}
    for b in rows:
        c, w = cur_prims(b, b["_win"])
        tot_cur += c
        win_cur += w
        K = _MockKit(oriented=True)
        p = plan_building(b)
        build_korean_building(K, None, "/W/B", b, Mtls("s", "g", "p"), plan=p)
        tot_new += len(K.calls)
        kinds[p.kind] = kinds.get(p.kind, 0) + 1
        tiers[p.tier] = tiers.get(p.tier, 0) + 1
        if len(K.calls) > prim_budget(p.kind, p.tier):
            print(f"    [예산초과] {b['_scene']} {p.kind}/{p.tier} "
                  f"{len(K.calls)} > {prim_budget(p.kind, p.tier)}")
    if verbose:
        print("\n" + "=" * 74)
        print(f"33씬 실측 ({len(rows)}동, scene18 town 13동은 튜플 생성이라 제외)")
        print("=" * 74)
        print(f"  현행 build_building 총 프림 : {tot_cur:6d} (그중 창 {win_cur})")
        print(f"  building_kit  총 프림       : {tot_new:6d}")
        print(f"  증감                        : {tot_new - tot_cur:+6d} "
              f"({100.0 * (tot_new - tot_cur) / max(1, tot_cur):+.1f} %)")
        print(f"  추론 유형 분포 : {kinds}")
        print(f"  LOD 티어 분포  : {tiers}")
    return tot_cur, tot_new


if __name__ == "__main__":
    selfcheck()
    _scan_scenes()
