#!/usr/bin/env python3
"""Push GitMoney to GitHub"""
import os, requests, subprocess, sys

GITHUB_TOKEN = ""
with open("/mnt/c/Users/df94b/.hermes/config/github-sync.env") as f:
    for line in f:
        if "export GITHUB_TOKEN=" in line:
            raw = line.split("=", 1)[1].strip().strip("'\"").strip()
            GITHUB_TOKEN = raw.replace("\r", "").replace("\n", "")
            break

if not GITHUB_TOKEN:
    print("ERROR: No token found")
    sys.exit(1)

headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
REPO_NAME = "gitmoney"
REPO_OWNER = "jackyZhangtt"
REPO_URL = f"https://github.com/{REPO_OWNER}/{REPO_NAME}.git"

# Check if repo exists
r = requests.get(f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}", headers=headers)
if r.status_code == 404:
    print(f"Creating repo {REPO_NAME}...")
    r = requests.post("https://api.github.com/user/repos", headers=headers, json={
        "name": REPO_NAME,
        "description": "GitMoney - 多Agent自动化变现系统。3个子Agent自动完成内容创作、推广引流、变现转化。",
        "private": False,
        "has_issues": True,
        "has_wiki": True,
    })
    print(f"Create: {r.status_code}")
    if r.status_code in (201, 422):
        print(r.json().get("html_url", r.json().get("message", "")))
else:
    print(f"Repo exists: {r.json()['html_url']}")

# Initialize and push
os.chdir("/mnt/c/Users/df94b/.hermes/gitmoney")
subprocess.run(["git", "init"], check=True, capture_output=True)
subprocess.run(["git", "checkout", "-b", "main"], check=True, capture_output=True)
subprocess.run(["git", "config", "user.email", "gitmoney-bot@users.noreply.github.com"], capture_output=True)
subprocess.run(["git", "config", "user.name", "GitMoney Bot"], capture_output=True)

# Remove existing remote if any
subprocess.run(["git", "remote", "rm", "origin"], capture_output=True)
subprocess.run(["git", "remote", "add", "origin", f"https://{GITHUB_TOKEN}@github.com/{REPO_OWNER}/{REPO_NAME}.git"], check=True, capture_output=True)

# Add and commit
subprocess.run(["git", "add", "."], check=True, capture_output=True)
r = subprocess.run(["git", "commit", "-m", "Initial commit: GitMoney multi-agent monetization system"], capture_output=True, text=True)
print(r.stdout)
if r.stderr:
    print(r.stderr)

# Push
r = subprocess.run(["git", "push", "-u", "origin", "main", "--force"], capture_output=True, text=True)
print(r.stdout)
if r.stderr:
    print(r.stderr)

if "fatal" in (r.stdout + r.stderr).lower():
    print("Push failed!")
    sys.exit(1)

print(f"\nSuccess! https://github.com/{REPO_OWNER}/{REPO_NAME}")
