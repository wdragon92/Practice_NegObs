#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""표적 시점 캡처 드라이버 — 씬 파일 무수정으로 임의 eye/tgt 컷을 뜬다.

목적
----
검수·감사에서 나온 의심 지점(접지, 관통, 전이대, 반복 티 등)을 기존 라운드에
없는 각도로 재촬영해 육안 확정한다. 씬의 `build_views()` 결과에 추가 뷰를
합치는 방식이라 **씬 코드는 한 줄도 수정하지 않는다** (s03_xalign_probe 의
"씬을 모듈로 읽기만 한다" 원칙의 캡처판).

기전
----
씬 스크립트는 `import scene_common as sc` 후 `sc.capture_pipeline(...)` 를
호출한다. 본 드라이버는 scene_common 을 먼저 import 해 `capture_pipeline` 을
래핑(주입 뷰 merge)한 뒤, 씬 파일을 `runpy.run_path(run_name="__main__")` 로
실행한다 — 모듈 캐시 덕에 씬이 받는 sc 는 래핑된 것이다.

사용 (렌더 규율: 반드시 cd 포함 셸 스크립트로, flock -o /tmp/negobs_gpu.lock 아래)
----
    NEGOBS_CAPTURE=1 NEGOBS_CAPTURE_MODE=rt \\
    NEGOBS_CAPTURE_DIR=look_check/scene16/260814_w4_probe \\
    NEGOBS_EXTRA_VIEWS='{"probe_manhole": {"eye": [-2.0, 3.5, 0.5], "tgt": [1.0, 4.0, -0.2]}}' \\
    NEGOBS_VIEWS=probe_manhole \\
      python scripts/probe_views_capture.py scenes/main/scene16_canopy_shadow.py

  - NEGOBS_EXTRA_VIEWS : {이름: {eye:[x,y,z], tgt:[x,y,z]}} JSON. 씬 뷰에 merge.
  - NEGOBS_VIEWS 필터는 그대로 작동하므로 주입 뷰만 골라 찍을 수 있다.
  - 그 외 NEGOBS_* env 는 전부 원래 의미 그대로.

프로브 컷은 판정 라운드가 아니다 — regr baseline·갤러리 체계에 넣지 말고
라운드명에 probe 를 명기할 것 (§2.5 명명 규약의 목적 서술).
"""
import json
import os
import runpy
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: probe_views_capture.py <scene .py path> "
                 "(NEGOBS_EXTRA_VIEWS='{...}' 필요)")
    scene_path = os.path.abspath(sys.argv[1])
    if not os.path.isfile(scene_path):
        sys.exit(f"scene file not found: {scene_path}")

    extra_raw = os.environ.get("NEGOBS_EXTRA_VIEWS", "")
    extra = json.loads(extra_raw) if extra_raw else {}
    for name, v in extra.items():
        if not (isinstance(v, dict) and len(v.get("eye", [])) == 3
                and len(v.get("tgt", [])) == 3):
            sys.exit(f"NEGOBS_EXTRA_VIEWS['{name}'] 는 eye/tgt 3원소 필요")

    # 씬 폴더를 sys.path 선두에 — 씬 폴더의 scene_common 심링크가 잡히는
    # 경로 그대로를 재현한다 (씬을 직접 실행할 때와 동일 조건).
    scene_dir = os.path.dirname(scene_path)
    sys.path.insert(0, scene_dir)
    sys.path.insert(0, REPO)

    import scene_common as sc                       # noqa: E402
    _orig = sc.capture_pipeline

    def _patched(sim_app, views, out_dir_default, set_render_mode_fn,
                 look_from_fn):
        merged = dict(views)
        clash = set(merged) & set(extra)
        if clash:
            print(f"[프로브] 주의 — 씬 뷰와 이름 충돌, 주입본으로 대체: {sorted(clash)}")
        merged.update(extra)
        if extra:
            print(f"[프로브] 주입 뷰 {len(extra)}개: {list(extra)}")
        return _orig(sim_app, merged, out_dir_default, set_render_mode_fn,
                     look_from_fn)

    sc.capture_pipeline = _patched
    runpy.run_path(scene_path, run_name="__main__")


if __name__ == "__main__":
    main()
