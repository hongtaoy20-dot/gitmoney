#!/usr/bin/env python3
"""Test all 3 agents and full pipeline"""
import os, sys, subprocess, json, re

# Read token
env_path = os.path.expanduser("~/.hermes/config/github-sync.env")
with open(env_path) as f:
    m = re.search(r'GITHUB_TOKEN=([^\s";\r\n]+)', f.read())
    github_token = m.group(1) if m else ""

os.environ["GITHUB_TOKEN"] = github_token

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(base_dir)

results = {}

for agent in ["creator", "traffic", "monetizer"]:
    print(f"\n{'='*60}")
    print(f"  Testing Agent: {agent}")
    print(f"{'='*60}")
    
    script = os.path.join(base_dir, "agents", f"agent_{agent}.py")
    try:
        result = subprocess.run(
            [sys.executable, script],
            capture_output=True, text=True, timeout=120,
            env=dict(os.environ),
        )
        output = (result.stdout + result.stderr).strip()
        print(output)
        results[agent] = {"status": "success" if result.returncode == 0 else "error", "output": output}
    except Exception as e:
        print(f"  ERROR: {e}")
        results[agent] = {"status": "error", "message": str(e)}

# Summary
print(f"\n{'='*60}")
print(f"  RESULTS SUMMARY")
print(f"{'='*60}")
for agent, r in results.items():
    status_icon = "✅" if r.get("status") == "success" else "❌"
    print(f"  {status_icon} {agent}: {r.get('status')}")

# Check monetizer report for monthly potential
report_dir = os.path.join(base_dir, "data", "analytics")
report_files = sorted([f for f in os.listdir(report_dir) if f.startswith("monetization_v2")], reverse=True)
if report_files:
    with open(os.path.join(report_dir, report_files[0])) as f:
        report = json.load(f)
    print(f"\n  💰 Total Monthly Potential: ${report.get('total_monthly_potential_usd', 'N/A')}/mo")
    print(f"  🎯 Target $500/mo: {'MET ✅' if report.get('target_met') else 'NOT YET 📈'}")
