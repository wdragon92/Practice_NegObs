> Every recall claim in this paper is reported at a matched false-alarm budget, and on **both** units of detection: the frame axis (`frame_recall_H` at `frame_fa_off`) and the cell axis (`cell_recall_H` at `cell_fpr_off`). The choice of unit does not change the sign of the FA-matched result — Depth ≥ RGB at every matched point on both axes, and the margin **grows** on the cell axis (+0.319 to +0.428 versus +0.052 to +0.236, with 3-of-3 seed agreement at all four points).
>
> It does change the published operating point: **at τ = 0.5, RGB leads on the frame axis (0.688 vs 0.438) while Depth leads on the cell axis (0.537 vs 0.344)**, because an any-hit recall and an any-fire false-alarm rate stack in the same direction and reward hitting one correct cell while spraying the rest. Matching on the frame axis also hides a 2.3–2.5× difference in cell-level alarm volume.

**배치**: §5.2 본 표 각주(**의무**) + 방법 절 지표 정의. "RGB .688" 서술에는 양축 각주가 반드시 붙는다.
**출처**: `experiments/v3_0823/redteam/EVL12_CELL_AXIS.md` · `ACCOUNTING.md` §4.8 #1 · §4.9-2 · 표 T02
