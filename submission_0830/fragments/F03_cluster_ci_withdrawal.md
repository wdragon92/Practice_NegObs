> The test strict-H set is **two scenes** (scene14 n = 60, scene15 n = 36) and the test E set is **one** (scene18 n = 45). Frame-level bootstrap intervals over 96 H frames assume 96 independent samples; the frames are 60 + 36 re-photographs of two geometries, and under scene-cluster resampling the false-alarm intervals widen by ×1.7–5.6. We therefore report **no confidence interval for the H and E tiers** and print the per-scene value beside the same scene's off-arm false-alarm rate instead.
>
> Two published significance claims do not survive scene-cluster resampling: the auxiliary arm's `cell_f1` gain +0.0403 [0.0001, 0.0786] becomes [−0.258, 0.205], and its `cell_recall_H` gain of +0.3546 — described as the largest confirmed effect and the one bearing on this paper's thesis — becomes [−0.143, 0.463]. The precision and false-alarm gains do survive.

**배치**: §5.3 통계 서술 + §5.6 한계. **"9/9 CI가 0을 배제한다"를 대체**한다. CI는 **축소가 아니라 철회**.
**출처**: `RESULTS_DRAFT.md` RT-B · RT-E(c) · `METRICS.md` §RT.5 · `rt_response/F5_CLUSTER_CI.md` · 표 T11
