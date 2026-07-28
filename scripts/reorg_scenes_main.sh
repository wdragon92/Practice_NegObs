#!/bin/bash
# 본편 21씬 → scenes/main/ 섹션화 (v5 RT 배치 종료 후 실행 전제)
#   - scene_common.py·look_check·assets 는 심링크로 연결 → 코드 수정 0
#   - 배치1(sceneN*/C*/D*)은 담당 에이전트 파이프라인 진행 중이라 루트 유지
#   - 실행 전 가드: python scene* 프로세스가 본편 씬을 돌리는 중이면 중단
cd /home/vislab/Desktop/work_sy/Practice_NegObs || exit 9

if pgrep -f "python scene0|python scene1|python scene2" > /dev/null; then
  echo "ABORT: 본편 씬 렌더 프로세스 실행 중"; exit 1
fi

mkdir -p scenes/main
for f in scene0*.py scene1*.py scene2*.py; do
  [ -e "$f" ] || continue
  git ls-files --error-unmatch "$f" >/dev/null 2>&1 && git mv "$f" scenes/main/ || mv "$f" scenes/main/
done
ln -sfn ../../scene_common.py scenes/main/scene_common.py
ln -sfn ../../look_check scenes/main/look_check
ln -sfn ../../assets scenes/main/assets
ls scenes/main/ | head -30
echo "REORG_DONE — 이후 실행은 python scenes/main/sceneNN_*.py"
