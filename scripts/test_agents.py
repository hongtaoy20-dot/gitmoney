#!/usr/bin/env python3
"""Test all GitMoney agents locally."""
import os, sys, re, subprocess

# Set environment
with open('/mnt/c/Users/df94b/.hermes/config/github-sync.env') as f:
    m = re.search(r'GITHUB_TOKEN=([^\s"\r\n]+)', f.read())
    token = m.group(1) if m else ''
os.environ['GITHUB_TOKEN'] = token

base = '/mnt/c/Users/df94b/.hermes/gitmoney'

def run_test(name, mode, agent=None):
    print(f'\n{"="*60}')
    print(f'  Testing: {name}')
    print(f'{"="*60}')
    
    cmd = [sys.executable, f'{base}/orchestrator.py', '--mode', mode]
    if agent:
        cmd.extend(['--agent', agent])
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120, cwd=base)
    
    print(result.stdout[-1200:] if result.stdout else '(no stdout)')
    if result.stderr:
        # Only show non-deprecation errors
        errors = [l for l in result.stderr.split('\n') if 'DeprecationWarning' not in l and 'UserWarning' not in l]
        if errors and ''.join(errors).strip():
            print(f'  STDERR (filtered): {errors[-3:]}')
    
    status = 'OK' if result.returncode == 0 else 'FAIL'
    print(f'  => Status: {status} (rc={result.returncode})')
    return result.returncode

# Run tests
tests = [
    ('Content Creator', 'single', 'creator'),
    ('Traffic Driver', 'single', 'traffic'),
    ('Monetizer', 'single', 'monetizer'),
]

results = []
for name, mode, agent in tests:
    rc = run_test(name, mode, agent)
    results.append((name, rc))

# Summary
print(f'\n{"="*60}')
print(f'  TEST SUMMARY')
print(f'{"="*60}')
for name, rc in results:
    print(f'  {"OK" if rc==0 else "FAIL"} | {name}')
print(f'  {"="*60}')
