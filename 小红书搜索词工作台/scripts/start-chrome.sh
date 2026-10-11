#!/bin/bash
# 起一个专供小红书词表采集的 Chrome（独立 profile + 独立调试端口 9335）
# 用前注意：不要用 open -a，不要把用户日常 Chrome 窗口调出来。
# 登录态存在 .chrome-profile 里；不关这个窗口就不用重登（实测不登录也能拿到下拉词）。
set -e
PORT="${XHS_PORT:-9335}"
# 项目目录可用环境变量覆盖，换机器/换人时不必改脚本
PROJ="${XHS_KEYWORDS_DIR:-$HOME/WorkBuddy/俱乐部工作/xhs-keywords}"
PROFILE="$PROJ/.chrome-profile"
mkdir -p "$PROFILE"

if lsof -nP -iTCP:$PORT -sTCP:LISTEN >/dev/null 2>&1; then
  echo "端口 $PORT 已在监听，复用现有实例，不重复启动。"
  exit 0
fi

"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --remote-debugging-port=$PORT --remote-allow-origins='*' \
  --user-data-dir="$PROFILE" \
  --no-first-run --no-default-browser-check \
  --no-sandbox --disable-gpu --disable-gpu-sandbox \
  --new-window "https://www.xiaohongshu.com/explore" \
  >/dev/null 2>&1 &

sleep 6
curl -s -m 5 "http://127.0.0.1:$PORT/json/version" | head -c 120
echo
echo "已启动。profile：$PROFILE"
