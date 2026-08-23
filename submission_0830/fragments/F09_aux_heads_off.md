> **All nine main-table runs were trained with the auxiliary pixel head disabled.** The single
> auxiliary run in this paper (`rgb_s42_aux`) is a one-seed appendix arm and a development-narrative
> row, not a result row; its `cell_recall_H` gain does not survive scene-cluster resampling, and its
> price — the total collapse of the E tier, 0.600 → 0.000 — is confirmed. Nothing in the main table
> depends on an amodal auxiliary objective.

**배치**: §5.1 학습 사양 + 부록 aux 절. **본 표 모델이 "aux 헤드가 학습돼 있다"고 서술하면 사실과 다르다.**
**경위**: RT-B N-5 실측 — `run_queue_v2.sh`에 aux 호출 0회. DZ §0.1의 "학습돼 있음" 서술은 본 표 모델에
대해 거짓이며, DZ 정정은 Claude AI/승용 몫으로 이관됨(결재 대기, 권고 = v3-A도 aux OFF 유지).
**출처**: `ACCOUNTING.md` §4.9-4 (D64) · `redteam/RT_LEDGER_B.md` · `SEED_TABLE.md` §5 · 표 T01/T11
