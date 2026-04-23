#!/usr/bin/env python3
"""Push GitMoney repo to GitHub - standalone script."""
import os, subprocess, sys, re

repo_dir = '/mnt/c/Users/df94b/.hermes/gitmoney'
env_path = '/mnt/c/Users/df94b/.hermes/config/github-sync.env'

# Read token
with open(env_path) as f:
    content = f.read()
m = re.search(r'GITHUB_TOKEN=([^\s";\r\n]+)', content)
token = m.group(1) if m else ''
if not token:
    print("ERROR: Token not found")
    sys.exit(1)

print(f"Token OK: len={len(token)}")

# Build remote URL
remote = f"https://{token}@github.com/jackyZhangtt/gitmoney.git"

# Push
result = subprocess.run(
    ['git', '-C', repo_dir, 'push', '--force', 'origin', 'main'],
    env={**os.environ, 'GIT_TERMINAL_PROMPT': '0'},
    capture_output=True, text=True, timeout=300
)

print(result.stdout)
print(result.stderr)
print(f"Return code: {result.returncode}")

if result.returncode == 0:
    print("\n=== PUSH SUCCESS ===")
else:
    print("\n=== PUSH FAILED ===")
