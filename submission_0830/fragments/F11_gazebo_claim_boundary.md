> Transferred zero-shot into a second renderer with an independent scene generator, the frozen models reproduce two behaviours: they **fire on a world whose hazard geometry contributes zero pixels** (verified by a per-row leak check against a noise floor of exactly 0 differing pixels; rgb 0.524, SegFormer 0.905), and their **tier ordering follows the order of fixtures placed in the scene rather than the order of the geometry** — five of six models score the zero-pixel world above a world whose drop interior is plainly visible. We claim only these two.
>
> The collapse of the twin discrimination in transfer (+0.314 → +0.019) is **confounded with the sim-to-sim domain gap**: the second renderer's pit interiors are nearly uniform black faces, so the visual evidence for drop geometry is itself impoverished there.

**배치**: §교차-시뮬 절. 이 트랙이 §개입실험 결론의 **유일한 독립 증거**임을 밝히는 문단과 함께 배치.
**금지**: 트윈 붕괴를 "모델이 단서만 본다"의 증거로 인용하지 말 것 — 교란 자인이 이 문단의 성립 요건이다.
**출처**: `weekend_0823/gazebo/GAZEBO_TRACK.md` §4.3·§4.4·§7-2 · caveat C5 · 표 T05
