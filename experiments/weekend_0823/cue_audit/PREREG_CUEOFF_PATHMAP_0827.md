# PREREG_CUEOFF.md 경로 대조표 (08-27 dataset/ 재편)

`PREREG_CUEOFF.md` 는 sha256 `9c4733bb…56b1` 로 봉인되어 있어 **바이트를 고치지 않았다.**
그래서 그 안의 `dataset/…` 표기 4곳은 08-27 재편 이후의 실제 위치와 다르다. 아래가 대조표다.
라운드 **이름은 그대로**이고 앞에 그룹 폴더 한 칸이 붙었을 뿐이다.

| 줄 | 문서에 적힌 경로 | 지금 실제 위치 |
|---|---|---|
| 5 | `dataset/260823_cueoff*` | `dataset/cueoff/260823_cueoff*` |
| 54 | `dataset/260820_boost_e2_*/*/scene*/variation.json` | `dataset/v2_corpus/260820_boost_e2_*/*/scene*/variation.json` |
| 598 | `dataset/260823_cueoff_s20fix_*` | `dataset/cueoff/260823_cueoff_s20fix_*` |
| 599 | `find dataset/260823_cueoff_s20fix_* -name '*.png'` | `find dataset/cueoff/260823_cueoff_s20fix_* -name '*.png'` |

`ACCOUNTING.md` §4.5 각주가 598줄을 그대로 인용하는데, 봉인 문장과 글자가 어긋나면 안 되므로
그 인용도 일부러 고치지 않았다. 이름으로 폴더를 찾을 때는 `dataset/ROUNDS.json` 또는
`variation_kit.round_dir("<라운드이름>")` 을 쓰면 위치를 몰라도 된다.
