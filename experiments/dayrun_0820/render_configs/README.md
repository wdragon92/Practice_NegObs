# render_configs (dayrun_0820) — OVERRIDE directory, normally empty

`scripts/rounds/run_260820_boost.sh` reads the hazard-arm config for
`<scene>_<arm>.json` from **this** directory first and falls back to
`experiments/mainrun_0819/render_configs/` (33 scenes x 2 arms, complete).

Reuse, not copy, is deliberate: those 66 files are a per-file grep of each
scene's real hazard key — 30 scenes `hazard_stairs`, sceneN1
`hazard_shadow_band`, sceneN2 `hazard_asphalt_patch`, sceneN5
`hazard_flush_grating`. `_deep_update` merges and silently ignores an unknown
key, so a hand-written blanket `{"hazard_stairs": false}` would leave three
scenes with the hazard still on and nothing would say so. A second copy of the
table is a second thing to drift.

Drop a file here only to change ONE scene's arm config for the boost round
without touching the 08-19 evidence.
