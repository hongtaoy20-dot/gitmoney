#!/usr/bin/env python3
"""Push GitMoney to GitHub via API - bypasses git push connectivity issues."""
import requests, json, base64, os, re, sys

REPO_OWNER = "jackyZhangtt"
REPO_NAME = "gitmoney"
TOKEN_FILE = "/mnt/c/Users/df94b/.hermes/config/github-sync.env"
BASE_DIR = "/mnt/c/Users/df94b/.hermes/gitmoney"

# Read token
with open(TOKEN_FILE) as f:
    m = re.search(r'GITHUB_TOKEN=([^\s";\r\n]+)', f.read())
token = m.group(1) if m else ""
if not token:
    print("ERROR: Token not found")
    sys.exit(1)

headers = {
    "Authorization": f"token {token}",
    "Accept": "application/vnd.github.v3+json"
}
API = "https://api.github.com"

# 1. Create repo
print("Creating repo...")
r = requests.post(f"{API}/user/repos", json={
    "name": REPO_NAME,
    "description": "GitMoney - 多Agent自动化变现系统 | AI-powered content creation, traffic driving & monetization",
    "private": False,
    "auto_init": False
}, headers=headers, timeout=30)

if r.status_code == 201:
    print(f"Repo created: {r.json()['html_url']}")
elif r.status_code == 422:
    print("Repo exists, proceeding...")
else:
    print(f"Create failed: {r.status_code} {r.text[:200]}")
    sys.exit(1)

# 2. Collect files to upload
files_to_push = []
for root, dirs, files in os.walk(BASE_DIR):
    # Skip .git
    if ".git" in root:
        continue
    for fname in files:
        fpath = os.path.join(root, fname)
        relpath = os.path.relpath(fpath, BASE_DIR)
        # Skip the push scripts (they're for internal use)
        if relpath.startswith("scripts/push"):
            continue
        with open(fpath, "rb") as f:
            content = f.read()
        files_to_push.append({
            "path": relpath.replace("\\", "/"),
            "content": base64.b64encode(content).decode(),
            "sha": None  # Will be set after first commit
        })

print(f"Total files to push: {len(files_to_push)}")

# 3. Create initial commit with all files
# First, check if repo has any commits
r = requests.get(f"{API}/repos/{REPO_OWNER}/{REPO_NAME}/git/refs/heads/main", headers=headers, timeout=30)
has_commits = r.status_code == 200
print(f"Has existing commits: {has_commits}")

# Create blobs for each file
tree_items = []
for f in files_to_push:
    # Create blob
    r = requests.post(f"{API}/repos/{REPO_OWNER}/{REPO_NAME}/git/blobs", json={
        "content": f["content"],
        "encoding": "base64"
    }, headers=headers, timeout=30)
    if r.status_code != 201:
        print(f"  WARN: blob failed for {f['path']}: {r.status_code}")
        continue
    blob_sha = r.json()["sha"]
    
    # Determine mode (executable for .sh files)
    mode = "100755" if f["path"].endswith(".sh") else "100644"
    
    tree_items.append({
        "path": f["path"],
        "mode": mode,
        "type": "blob",
        "sha": blob_sha
    })
    print(f"  + {f['path']} (blob: {blob_sha[:8]}...)")

print(f"Tree items: {len(tree_items)}")

if has_commits:
    # Get latest commit SHA
    r = requests.get(f"{API}/repos/{REPO_OWNER}/{REPO_NAME}/git/refs/heads/main", headers=headers, timeout=30)
    latest_sha = r.json()["object"]["sha"]
    print(f"Latest commit: {latest_sha[:12]}...")
    
    # Get tree SHA
    r = requests.get(f"{API}/repos/{REPO_OWNER}/{REPO_NAME}/git/commits/{latest_sha}", headers=headers, timeout=30)
    base_tree_sha = r.json()["tree"]["sha"]
else:
    base_tree_sha = None
    print("No existing commits")

# Create tree
r = requests.post(f"{API}/repos/{REPO_OWNER}/{REPO_NAME}/git/trees", json={
    "base_tree": base_tree_sha,
    "tree": tree_items
}, headers=headers, timeout=30)

if r.status_code != 201:
    print(f"Tree creation failed: {r.status_code} {r.text[:300]}")
    # Try without base tree
    r = requests.post(f"{API}/repos/{REPO_OWNER}/{REPO_NAME}/git/trees", json={
        "tree": tree_items
    }, headers=headers, timeout=30)
    
if r.status_code != 201:
    print(f"Tree creation still failed: {r.status_code} {r.text[:300]}")
    sys.exit(1)

tree_sha = r.json()["sha"]
print(f"Tree SHA: {tree_sha[:12]}...")

# Get parent commit
parents = []
if has_commits:
    parents.append(latest_sha)

today = __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Create commit
commit_data = {
    "message": f"Initial commit: GitMoney multi-agent monetization system\n\nAuto-pushed on {today}\n\n3 agents + orchestrator + GitHub Actions pipeline",
    "tree": tree_sha,
    "parents": parents
}

r = requests.post(f"{API}/repos/{REPO_OWNER}/{REPO_NAME}/git/commits", json=commit_data, headers=headers, timeout=30)

if r.status_code != 201:
    print(f"Commit failed: {r.status_code} {r.text[:300]}")
    sys.exit(1)

commit_sha = r.json()["sha"]
print(f"Commit SHA: {commit_sha[:12]}...")

# Update HEAD
r = requests.patch(f"{API}/repos/{REPO_OWNER}/{REPO_NAME}/git/refs/heads/main", json={
    "sha": commit_sha,
    "force": True
}, headers=headers, timeout=30)

if r.status_code == 200:
    print(f"\n=== PUSH SUCCESS ===")
    print(f"https://github.com/{REPO_OWNER}/{REPO_NAME}")
else:
    # Try creating the ref
    r = requests.post(f"{API}/repos/{REPO_OWNER}/{REPO_NAME}/git/refs", json={
        "ref": "refs/heads/main",
        "sha": commit_sha
    }, headers=headers, timeout=30)
    
    if r.status_code == 201:
        print(f"\n=== PUSH SUCCESS ===")
        print(f"https://github.com/{REPO_OWNER}/{REPO_NAME}")
    else:
        print(f"Branch update failed: {r.status_code} {r.text[:300]}")
