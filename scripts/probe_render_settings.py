#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""렌더 설정 프로브 드라이버 — 씬 무수정으로 RTX 설정을 덮어쓰고/덤프하며 캡처한다.

목적 (GT-113 R0 — 측정 기반 확정)
----
RTX 조사(scene_audit_realism_survey_v1 §5.3)가 지목한 두 미확정 사실을 실측한다:
  (a) PT-fast 등가성 — 스파이크의 PT 3종 md5 가 전부 동일해 "화질 동등" 근거가
      캡처 하네스 사고(설정 전환 후 같은 프레임 재캡처)였을 가능성.
  (b) PT AA 필터/디노이저 기본값 — filterRadius 1.0(실질 바이리니어)·blendFactor
      문서 모순이 slope 감쇠(블러 0.8px = −0.45)의 원인일 가능성.

기전
----
probe_views_capture 와 같은 몽키패치 계열: scene_common.capture_pipeline 을 래핑해
`set_render_mode_fn` 호출 **이후**(= 씬/PT_FAST 의 설정이 전부 끝난 뒤)에
  NEGOBS_RTX_SET  = "key=val;key=val"   carb 설정 덮어쓰기 (float/int/bool 자동 판별)
  NEGOBS_RTX_DUMP = "key;key;..."       현재 값 stdout 덤프 ([R0-DUMP] 접두)
를 적용한다. 씬 파일 무수정, 판정 라운드 체계 밖(라운드명에 probe 명기).

사용
----
    NEGOBS_CAPTURE=1 NEGOBS_CAPTURE_MODE=pt NEGOBS_CAPTURE_DIR=... \\
    NEGOBS_RTX_SET="/rtx/pathtracing/aa/filterRadius=0.5" \\
    NEGOBS_RTX_DUMP="/rtx/pathtracing/optixDenoiser/blendFactor" \\
      python scripts/probe_render_settings.py scenes/main/scene04_parktrail.py
"""
import os
import runpy
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _parse_val(s):
    sl = s.strip().lower()
    if sl in ("true", "false"):
        return sl == "true"
    try:
        return int(s)
    except ValueError:
        pass
    try:
        return float(s)
    except ValueError:
        return s


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: probe_render_settings.py <scene .py path>")
    scene_path = os.path.abspath(sys.argv[1])
    scene_dir = os.path.dirname(scene_path)
    sys.path.insert(0, scene_dir)
    sys.path.insert(0, REPO)

    import scene_common as sc                    # noqa: E402
    _orig = sc.capture_pipeline

    rtx_set = [kv.split("=", 1) for kv in
               os.environ.get("NEGOBS_RTX_SET", "").split(";") if "=" in kv]
    rtx_dump = [k for k in
                os.environ.get("NEGOBS_RTX_DUMP", "").split(";") if k.strip()]

    def _patched(sim_app, views, out_dir_default, set_render_mode_fn,
                 look_from_fn):
        def _wrapped_mode(mode):
            set_render_mode_fn(mode)
            # 씬 쪽 설정이 끝난 지점 — 여기서 덮어쓰고 덤프해야 진짜 실효값이다.
            # (capture_pipeline 의 PT_FAST 블록은 이 함수 *이후*에 도니, PT_FAST 를
            # 이기고 싶은 키는 PT_FAST 를 끄고 쓰거나 spp 계열을 피해서 쓴다.)
            import carb
            st = carb.settings.get_settings()
            for k, v in rtx_set:
                st.set(k.strip(), _parse_val(v))
                print(f"[R0-SET] {k.strip()} = {_parse_val(v)!r}")
            for k in rtx_dump:
                try:
                    print(f"[R0-DUMP] {k.strip()} = {st.get(k.strip())!r}")
                except Exception as e:                      # noqa: BLE001
                    print(f"[R0-DUMP] {k.strip()} = <error {e}>")
        return _orig(sim_app, views, out_dir_default, _wrapped_mode,
                     look_from_fn)

    sc.capture_pipeline = _patched
    runpy.run_path(scene_path, run_name="__main__")


if __name__ == "__main__":
    main()
