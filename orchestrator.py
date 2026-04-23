#!/usr/bin/env python3
"""
GitMoney Orchestrator (V2)
==========================
主控调度器 - 协调 3 个 Agent 完成完整变现闭环。

模式:
  full     → Content Creator + Traffic Driver + Monetizer (完整闭环)
  content  → 仅 Content Creator
  traffic  → 仅 Traffic Driver
  monetize → 仅 Monetizer
  single   → 指定单个 Agent (--agent creator/traffic/monetizer)
  report   → 仅生成报告 (不运行 Agent)
"""

import os, sys, json, yaml, subprocess
from datetime import UTC, datetime
from pathlib import Path

AGENTS_DIR = Path(__file__).parent / "agents"
DATA_DIR = Path(__file__).parent / "data" / "analytics"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def run_agent(agent_name: str) -> dict:
    """运行指定 Agent 并返回结果"""
    script = AGENTS_DIR / f"agent_{agent_name}.py"
    if not script.exists():
        return {"status": "error", "message": f"Agent {agent_name} not found at {script}"}
    
    print(f"\n{'='*60}")
    print(f"  运行 Agent: {agent_name}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            [sys.executable, str(script)],
            capture_output=True, text=True, timeout=120,
            env={**os.environ},
        )
        
        output = result.stdout + result.stderr
        
        if result.returncode == 0:
            print(output)
            return {"status": "success", "output": output}
        else:
            print(output)
            return {"status": "error", "output": output, "returncode": result.returncode}
    except subprocess.TimeoutExpired:
        return {"status": "timeout"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def run_full_pipeline():
    """完整变现闭环: Creator → Traffic → Monetizer"""
    print(f"\n{'='*60}")
    print(f"  GitMoney Pipeline V2 — 完整运行")
    print(f"  {datetime.now(UTC).strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"{'='*60}")

    results = {}
    
    # Phase 1: Content Creator — 生成变现驱动内容
    print(f"\n  [Phase 1/3] Content Creation")
    results["creator"] = run_agent("creator")
    
    if results["creator"]["status"] != "success":
        print("  ⚠️ Creator 遇到问题，继续运行...")
    
    # Phase 2: Traffic Driver — 推广引流
    print(f"\n  [Phase 2/3] Traffic Driving")
    results["traffic"] = run_agent("traffic")
    
    # Phase 3: Monetizer — 变现分析
    print(f"\n  [Phase 3/3] Monetization Analysis")
    results["monetizer"] = run_agent("monetizer")

    return results


def generate_pipeline_report(results: dict):
    """生成管线执行报告"""
    all_success = all(r.get("status") == "success" for r in results.values())
    
    report = {
        "timestamp": datetime.now(UTC).isoformat(),
        "engine_version": "2.0",
        "pipeline_complete": all_success,
        "agents": {k: {"status": v.get("status")} for k, v in results.items()},
        "summary": "全部完成 ✅" if all_success else "部分完成 ⚠️",
    }
    
    report_path = DATA_DIR / f"pipeline_report_{datetime.now(UTC).strftime('%Y%m%d')}.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n{'='*60}")
    print(f"  管线报告已保存: {report_path}")
    print(f"  状态: {report['summary']}")
    print(f"{'='*60}\n")
    
    return report


def main():
    import argparse
    parser = argparse.ArgumentParser(description="GitMoney Orchestrator V2")
    parser.add_argument("--mode", choices=["full", "content", "traffic", "monetize", "single", "report"],
                        default="full", help="运行模式")
    parser.add_argument("--agent", choices=["creator", "traffic", "monetizer"],
                        help="single 模式下指定 Agent")
    args = parser.parse_args()

    if args.mode == "full":
        print("GitMoney Orchestrator V2 — 启动完整变现闭环\n")
        results = run_full_pipeline()
        generate_pipeline_report(results)
    elif args.mode == "single" and args.agent:
        result = run_agent(args.agent)
        print(f"\nAgent '{args.agent}' 运行结果: {result.get('status')}")
    elif args.mode == "content":
        result = run_agent("creator")
    elif args.mode == "traffic":
        result = run_agent("traffic")
    elif args.mode == "monetize":
        result = run_agent("monetizer")
    elif args.mode == "report":
        print("报告模式: 分析历史数据生成综合变现报告")
        # 如果 monetizer 报告已经生成，就读取它
        report_files = sorted(DATA_DIR.glob("monetization_v2_*.json"), reverse=True)
        if report_files:
            with open(report_files[0]) as f:
                data = json.load(f)
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print("尚未生成报告，请先运行 full 模式")


if __name__ == "__main__":
    main()
