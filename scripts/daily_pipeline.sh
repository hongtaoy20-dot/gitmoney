#!/bin/bash
# GitMoney 每日管线执行入口
# 由 cron 调用，source env 文件确保环境变量可用

ENV_FILE="/home/jacky/.hermes/gitmoney.env"
PROJECT_DIR="/mnt/c/Users/df94b/.hermes/gitmoney"

# Export env vars
if [ -f "$ENV_FILE" ]; then
    set -a
    source "$ENV_FILE"
    set +a
fi

cd "$PROJECT_DIR" || exit 1

# 执行完整管线
python3 agents/agent_creator.py 2>&1
echo "--- TRAFFIC ---"
python3 agents/agent_traffic.py 2>&1
echo "--- MONETIZER ---"
python3 agents/agent_monetizer.py 2>&1

# Git commit & push
git add -A
git commit -m "Daily pipeline $(date +%Y-%m-%d)" 2>/dev/null || echo "Nothing to commit"
git push origin main 2>&1 || echo "Push failed (network issue)"
