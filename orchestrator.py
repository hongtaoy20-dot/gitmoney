#!/usr/bin/env python3
"""
GitMoney Orchestrator - 主控调度
====================================
协调 3 个子 Agent 的协作执行，管理任务队列，生成综合报告。

模式:
  - full:       完整流程 (创作 → 推广 → 变现分析)
  - daily:      仅每日内容创作 + 推广
  - analytics:  仅数据分析和变现报告
  - single:     只运行指定 Agent

用法:
  python orchestrator.py --mode daily
  python orchestrator.py --mode full
  python orchestrator.py --mode single --agent creator
"""

import os
import sys
import json
import yaml
import time
import argparse
import subprocess
from datetime import datetime
from pathlib import Path

# ─── 配置 ─────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
AGENTS_DIR = BASE_DIR / "agents"
DATA_DIR = BASE_DIR / "data"
CONFIG_PATH = BASE_DIR / "config" / "settings.yaml"

DATA_DIR.mkdir(parents=True, exist_ok=True)

with open(CONFIG_PATH) as f:
    CONFIG = yaml.safe_load(f)

ORCH_CONFIG = CONFIG.get("orchestrator", {})


# ─── Agent 执行器 ─────────────────────────────────────────────────────

class AgentRunner:
    """运行 Agent 脚本并收集结果"""
    
    def __init__(self):
        self.results = {}
    
    def run_creator(self) -> dict:
        """运行 Agent 1: Content Creator"""
        script = AGENTS_DIR / "agent_creator.py"
        if not script.exists():
            return {"status": "error", "message": f"Agent 1 not found at {script}"}
        
        print("\n" + "=" * 60)
        print("  Agent 1: Content Creator - 开始创作")
        print("=" * 60)
        
        try:
            result = subprocess.run(
                [sys.executable, str(script)],
                capture_output=True, text=True, timeout=300
            )
            output = result.stdout + result.stderr
            print(output)
            
            return {
                "status": "ok" if result.returncode == 0 else "error",
                "output": output[-1000:],
                "returncode": result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {"status": "timeout", "message": "Agent 1 执行超时"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def run_traffic(self) -> dict:
        """运行 Agent 2: Traffic Driver"""
        script = AGENTS_DIR / "agent_traffic.py"
        if not script.exists():
            return {"status": "error", "message": f"Agent 2 not found at {script}"}
        
        print("\n" + "=" * 60)
        print("  Agent 2: Traffic Driver - 开始推广")
        print("=" * 60)
        
        try:
            result = subprocess.run(
                [sys.executable, str(script)],
                capture_output=True, text=True, timeout=300
            )
            output = result.stdout + result.stderr
            print(output)
            
            return {
                "status": "ok" if result.returncode == 0 else "error",
                "output": output[-1000:],
                "returncode": result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {"status": "timeout", "message": "Agent 2 执行超时"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def run_monetizer(self) -> dict:
        """运行 Agent 3: Monetizer"""
        script = AGENTS_DIR / "agent_monetizer.py"
        if not script.exists():
            return {"status": "error", "message": f"Agent 3 not found at {script}"}
        
        print("\n" + "=" * 60)
        print("  Agent 3: Monetizer - 开始变现分析")
        print("=" * 60)
        
        try:
            result = subprocess.run(
                [sys.executable, str(script)],
                capture_output=True, text=True, timeout=300
            )
            output = result.stdout + result.stderr
            print(output)
            
            return {
                "status": "ok" if result.returncode == 0 else "error",
                "output": output[-1000:],
                "returncode": result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {"status": "timeout", "message": "Agent 3 执行超时"}
        except Exception as e:
            return {"status": "error", "message": str(e)}


# ─── 报告生成器 ───────────────────────────────────────────────────────

class ReportGenerator:
    """生成执行报告并保存"""
    
    def generate_markdown_report(self, results: dict) -> str:
        """生成 Markdown 格式的执行总结"""
        timestamp = datetime.utcnow().isoformat()
        
        lines = [
            f"# GitMoney Daily Report",
            f"",
            f"**Date:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
            f"**Mode:** Full Pipeline",
            f"",
            f"## Execution Summary",
            f"",
            f"| Agent | Status |",
            f"|-------|--------|",
        ]
        
        status_map = {
            "creator": "📝 Content Creator",
            "traffic": "📢 Traffic Driver",
            "monetizer": "💰 Monetizer",
        }
        
        for agent_key, agent_name in status_map.items():
            result = results.get(agent_key, {})
            status = result.get("status", "not_run")
            status_icon = "✅" if status == "ok" else "⚠️" if status == "timeout" else "❌"
            lines.append(f"| {agent_name} | {status_icon} {status} |")
        
        lines.append("")
        lines.append(f"## Details")
        lines.append("")
        
        # 统计总览
        ok_count = sum(1 for r in results.values() if r.get("status") == "ok")
        lines.append(f"- **Agents succeeded:** {ok_count}/3")
        lines.append(f"- **Pipeline status:** {'✅ All OK' if ok_count == 3 else '⚠️ Partial failure'}")
        lines.append("")
        
        # 变现估算（如果能从 Monetizer 输出提取）
        monetizer_result = results.get("monetizer", {}).get("output", "")
        if "$" in monetizer_result:
            # 尝试提取变现潜力数字
            for line in monetizer_result.split('\n'):
                if "月变现潜力" in line or "potential" in line:
                    lines.append(f"> {line.strip()}")
                    break
        
        lines.append("")
        lines.append("---")
        lines.append(f"*Generated by GitMoney Orchestrator at {timestamp}*")
        
        return "\n".join(lines)
    
    def save_report(self, report: str):
        """保存报告到文件"""
        report_dir = DATA_DIR / "analytics"
        report_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"daily_report_{datetime.utcnow().strftime('%Y%m%d')}.md"
        filepath = report_dir / filename
        
        with open(filepath, "w") as f:
            f.write(report)
        
        print(f"  报告已保存: {filepath}")
        return filepath


# ─── 主 Orchestrator ─────────────────────────────────────────────────

class Orchestrator:
    """GitMoney 系统主控"""
    
    def __init__(self):
        self.runner = AgentRunner()
        self.reporter = ReportGenerator()
    
    def run_full_pipeline(self) -> dict:
        """完整流程: 创作 → 推广 → 变现分析"""
        print(f"\n{'='*60}")
        print(f"  GitMoney Pipeline - Full Mode")
        print(f"  {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
        print(f"{'='*60}\n")
        
        results = {}
        
        # 步骤 1: 内容创作
        print("\n[Phase 1/3] Content Creation")
        results["creator"] = self.runner.run_creator()
        
        # 步骤 2: 推广引流
        print("\n[Phase 2/3] Traffic Driving")
        results["traffic"] = self.runner.run_traffic()
        
        # 步骤 3: 变现分析
        print("\n[Phase 3/3] Monetization Analysis")
        results["monetizer"] = self.runner.run_monetizer()
        
        # 生成总结报告
        print("\n" + "-" * 40)
        print("Generating summary report...")
        report = self.reporter.generate_markdown_report(results)
        report_path = self.reporter.save_report(report)
        
        # 汇总结果
        summary = {
            "timestamp": datetime.utcnow().isoformat(),
            "mode": "full",
            "agents": results,
            "report_path": str(report_path),
        }
        
        # 保存 JSON 日志
        log_path = DATA_DIR / "analytics" / f"pipeline_log_{datetime.utcnow().strftime('%Y%m%d')}.json"
        with open(log_path, "w") as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n{'='*60}")
        ok_count = sum(1 for r in results.values() if r.get("status") == "ok")
        print(f"  Pipeline Complete: {ok_count}/3 agents succeeded")
        print(f"  Report: {report_path}")
        print(f"{'='*60}\n")
        
        return summary
    
    def run_daily(self) -> dict:
        """每日任务 (内容创作 + 推广)"""
        print(f"\n{'='*60}")
        print(f"  GitMoney Pipeline - Daily Mode")
        print(f"{'='*60}\n")
        
        results = {}
        results["creator"] = self.runner.run_creator()
        results["traffic"] = self.runner.run_traffic()
        
        report = self.reporter.generate_markdown_report(results)
        report_path = self.reporter.save_report(report)
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "mode": "daily",
            "agents": results,
            "report_path": str(report_path),
        }
    
    def run_analytics(self) -> dict:
        """仅运行分析"""
        results = {"monetizer": self.runner.run_monetizer()}
        return results
    
    def run_single(self, agent_name: str) -> dict:
        """运行单个 Agent"""
        runner_map = {
            "creator": self.runner.run_creator,
            "traffic": self.runner.run_traffic,
            "monetizer": self.runner.run_monetizer,
        }
        
        if agent_name not in runner_map:
            print(f"Error: Unknown agent '{agent_name}'. Available: creator, traffic, monetizer")
            return {"status": "error", "message": f"Unknown agent: {agent_name}"}
        
        result = runner_map[agent_name]()
        return {agent_name: result}


# ─── CLI 入口 ─────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="GitMoney - 多 Agent 自动化变现系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python orchestrator.py --mode full        # 完整流程
  python orchestrator.py --mode daily       # 每日任务
  python orchestrator.py --mode analytics   # 仅分析
  python orchestrator.py --mode single --agent creator  # 单个Agent
        """
    )
    
    parser.add_argument(
        "--mode", "-m",
        choices=["full", "daily", "analytics", "single"],
        default="daily",
        help="执行模式 (默认: daily)"
    )
    parser.add_argument(
        "--agent", "-a",
        choices=["creator", "traffic", "monetizer"],
        help="要运行的 Agent (single 模式下必填)"
    )
    
    args = parser.parse_args()
    
    orch = Orchestrator()
    
    if args.mode == "full":
        orch.run_full_pipeline()
    elif args.mode == "daily":
        orch.run_daily()
    elif args.mode == "analytics":
        orch.run_analytics()
    elif args.mode == "single":
        if not args.agent:
            print("Error: --agent is required in single mode")
            sys.exit(1)
        orch.run_single(args.agent)


if __name__ == "__main__":
    main()
