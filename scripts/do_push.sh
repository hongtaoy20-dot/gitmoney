#!/bin/bash
# Push GitMoney to GitHub
set -e

cd "$(dirname "$0")/.."

# Extract token
TOKEN=$(python3 << 'PYEOF'
import re
with open('/mnt/c/Users/df94b/.hermes/config/github-sync.env') as f:
    content = f.read()
m = re.search(r'GITHUB_TOKEN=([^\s";\r\n]+)', content)
print(m.group(1) if m else '')
PYEOF
)

if [ -z "$TOKEN" ]; then
    echo "ERROR: Could not extract token"
    exit 1
fi

echo "Token length: ${#TOKEN}"

# Set remote with token embedded
git remote set-url origin "https://${TOKEN}@github.com/jackyZhangtt/gitmoney.git"

echo "Pushing to GitHub..."
git push --force origin main
echo "SUCCESS: Push complete!"
