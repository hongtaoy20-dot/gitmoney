#!/usr/bin/env python3
"""
GitMoney 数据分析工具
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data" / "analytics"


class AnalyticsEngine:
    """流量/收益数据分析"""
    
    def analyze_trend(self, days: int = 7) -> dict:
        """分析近 N 天的趋势"""
        stats_file = DATA_DIR / "stats_history.json"
        if not stats_file.exists():
            return {"error": "No data available"}
        
        with open(stats_file) as f:
            history = json.load(f)
        
        # 取最近 N 天
        recent = history[-days:] if len(history) >= days else history
        
        if len(recent) < 2:
            return {"error": "Not enough data points"}
        
        first, last = recent[0], recent[-1]
        
        return {
            "period_days": len(recent),
            "star_growth": last.get("stars", 0) - first.get("stars", 0),
            "fork_growth": last.get("forks", 0) - first.get("forks", 0),
            "current_stars": last.get("stars", 0),
            "current_forks": last.get("forks", 0),
        }
    
    def estimate_monthly_revenue(self, stars: int) -> dict:
        """基于 Stars 估算月收入"""
        return {
            "github_sponsors": round(stars * 0.001 * 10, 2),
            "paid_content": round(stars * 0.005 * 10, 2),
            "consulting_leads": round(stars * 0.002 * 100, 2),
            "total_estimate": round(stars * 0.008 * 50, 2),
            "formula": "stars * conversion_rate * avg_value",
        }


def main():
    engine = AnalyticsEngine()
    
    trend = engine.analyze_trend(7)
    print("=== Trend Analysis (7 days) ===")
    for k, v in trend.items():
        print(f"  {k}: {v}")
    
    print("\n=== Revenue Estimate (100 stars benchmark) ===")
    rev = engine.estimate_monthly_revenue(100)
    for k, v in rev.items():
        if isinstance(v, float):
            print(f"  {k}: ${v:.2f}")
        else:
            print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
