# -*- coding: utf-8 -*-
"""
negobs_terrain.py — (셔틀) 지형 코드의 단일 소스는 ../negobs_look_check_v1.py 다.

지형 생성 코드가 메인 스크립트(단일 실행 파일 사양)에 인라인되면서,
selftest.py 등 검증 도구가 '실제 배포 코드'를 계측하도록 여기서 재수출한다.
직접 수정하지 말 것 — 수정은 negobs_look_check_v1.py [B] 섹션에서.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from negobs_look_check_v1 import (  # noqa: F401,E402
    PARAMS, DERIVED,
    build_terrain, bilinear_sample, smooth_vertex_normals,
    _build_face_indices, _face_mean, _face_minmax,
    profile_S, _profile_consts,
    _cubic, _quintic,
    _value_noise_2d, _value_noise_1d, _fractal_2d, _fractal_1d,
    _norm_amp, _norm_amp_interior, _nearest_centerline,
)
