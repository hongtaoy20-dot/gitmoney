#!/usr/bin/env python3
"""
GitMoney Marine Community Promoter - 海事社区精准推广脚本
在 Reddit/HN/GitHub 自动生成推广帖子和策略
"""
import os, sys, json, yaml, random
from datetime import datetime, UTC
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "promotion"
LEADS_DIR = BASE_DIR / "data" / "leads"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Target communities
COMMUNITIES = {
    "reddit_maritime": {
        "platform": "reddit",
        "subreddits": ["r/maritime", "r/shipping", "r/Nautical", "r/MarineEngineering"],
        "audience": "现役/退役海事从业者、轮机工程、船舶管理",
        "best_time": "08:00-10:00 UTC (欧美工作时间)",
    },
    "reddit_investing": {
        "platform": "reddit",
        "subreddits": ["r/valueinvesting", "r/dividends", "r/stocks"],
        "audience": "价值投资者、股息投资者",
        "best_time": "12:00-14:00 UTC (美股开盘时段)",
    },
    "reddit_tech": {
        "platform": "reddit",
        "subreddits": ["r/Python", "r/opensource", "r/coolgithubprojects"],
        "audience": "开发者、开源贡献者、自动化爱好者",
        "best_time": "14:00-16:00 UTC",
    },
    "hacker_news": {
        "platform": "hackernews",
        "audience": "技术创业者、工程师",
        "best_time": "13:00-15:00 UTC (硅谷工作时间)",
    },
    "github_trending": {
        "platform": "github",
        "audience": "开源社区",
        "best_time": "any",
    },
}

# Content templates per channel
POST_TEMPLATES = {
    "cruise_ops": {
        "reddit": {
            "title": "I've been a Viking Cruises Chief Officer for 15 years — here's what actually matters in cruise operations",
            "body": """After 15 years on the bridge of Viking Cruises, I've noticed the same patterns over and over.

The operators who excel aren't the ones with the fanciest tools or the most certifications. They're the ones who:

1. **Standardize everything.** Checklists aren't just for safety drills — they're for daily operations, handovers, and compliance reporting.
2. **Document the exceptions.** When something goes wrong, write it down. Patterns emerge over time that no one sees in real-time.
3. **Automate the boring stuff.** Crew scheduling, fuel tracking, compliance dates — these can be automated with simple Python scripts.

I've been slowly building a library of these tools and templates. Would anyone be interested in a structured pack?

Happy to share what I've learned. Ask me anything about cruise operations."""
        },
        "hackernews": {
            "title": "Show HN: I automated my cruise ship operations with Python",
            "body": """As a Chief Officer on Viking Cruises, I manage crew scheduling, safety compliance, fuel tracking, and dozens of operational checklists.

Last year, I started replacing Excel spreadsheets with Python scripts. The result: I save about 5 hours per week on paperwork alone.

Here's what I built:
- A crew scheduling optimizer (handles rotation, rest hours, certification expiry)
- Automated safety compliance calendar
- Fuel consumption tracker with trend analysis
- Daily operations checklist generator

Code is on GitHub: https://github.com/jackyZhangtt/gitmoney

Would be great to hear what other tools you all use in maritime operations."""
        }
    },
    "value_investing": {
        "reddit": {
            "title": "My 3-year value investing journey with $200K portfolio — what worked and what didn't",
            "body": """I've been running a value investing portfolio for 3 years now, currently at $200K. Thought I'd share what actually worked.

**What worked:**
- RSI < 30 as entry signal (but only for fundamentally solid stocks)
- PE < 15 + PB < 2 as baseline filter eliminates most noise
- 3-year holding horizon (immigration timeline alignment)

**What didn't:**
- Timing the market on broad indexes
- Chasing dividend yields above 5%
- Ignoring RSI data staleness (almost bought BAC at a bad entry because of cached RSI)

I automated the screening process with Python + Alpha Vantage. Happy to share the screener if anyone's interested.

Current top picks: BAC (PE 11.2, RSI 32), INTC (PE 8.5, RSI 28)

What's your screening criteria?""",
        },
        "github": {
            "description": "Open-source value stock screener — PE/PB/ROE/RSI multi-factor scoring with automated weekly watchlist generation",
        }
    },
    "maritime_tech": {
        "reddit": {
            "title": "Building open-source tools for maritime professionals — who wants to contribute?",
            "body": """I'm a Chief Officer by day, Python developer by night. I've been building open-source tools for the maritime industry.

Current projects:
- 🚢 Cruise ops checklist automation
- 📊 Safety compliance tracker
- 💹 Value investing screener (because we need financial independence too)

All on GitHub: https://github.com/jackyZhangtt/gitmoney

Looking for contributors who:
- Work in maritime and have ideas for useful tools
- Are developers interested in a niche domain
- Want to build their portfolio while helping the industry

What tools would make YOUR job easier?"""
        }
    }
}

def generate_promotion_plan() -> str:
    """Generate a full promotion plan for today"""
    now = datetime.now(UTC)
    
    plan = [
        f"# GitMoney 推广计划",
        f"日期: {now.strftime('%Y-%m-%d')}",
        f"UTC 时间: {now.hour}:{now.minute:02d}",
        "",
        f"## 目标社区 ({len(COMMUNITIES)} 个渠道)",
        "",
    ]
    
    for channel_id, info in COMMUNITIES.items():
        subs = info.get("subreddits", [info.get("platform")])
        plan.append(f"### {channel_id}")
        plan.append(f"- 平台: {info['platform']}")
        plan.append(f"- 子版块: {', '.join(subs)}")
        plan.append(f"- 受众: {info['audience']}")
        plan.append(f"- 最佳时间: {info['best_time']}")
        
        # Check if it's a good time to post now
        plan.append(f"- 当前适宜发帖: {'✅' if now.hour in range(8, 16) else '⚠️ 非黄金时段'}")
        plan.append("")
    
    plan.append("## 今日推荐发帖内容")
    plan.append("")
    
    # Pick a random template per channel
    channels = ["cruise_ops", "value_investing", "maritime_tech"]
    random.shuffle(channels)
    
    for channel in channels:
        templates = POST_TEMPLATES.get(channel, {})
        if "reddit" in templates:
            plan.append(f"### 📝 {channel}/reddit")
            plan.append(f"**TITLE**: {templates['reddit']['title']}")
            plan.append(f"**BODY**: (查看完整内容)")
            plan.append("")
    
    plan.append("---")
    plan.append("*GitMoney Community Promoter - 自动生成*")
    
    report = "\n".join(plan)
    filepath = DATA_DIR / f"promotion_plan_{now.strftime('%Y%m%d')}.md"
    with open(filepath, "w") as f:
        f.write(report)
    
    print(f"✅ 推广计划已保存: {filepath}")
    return report

def simulate_promotion():
    """Simulate promotion channels (placeholder for real API integration)"""
    # In production: use PRAW for Reddit, requests for GitHub API
    plan = generate_promotion_plan()
    
    stats = {
        "channels": len(COMMUNITIES),
        "content_pieces": len(POST_TEMPLATES) * 2,
        "estimated_first_month_reach": "5,000-10,000 impressions",
        "estimated_conversion_rate": "0.5-1%",
        "notes": "Reddit API (PRAW) 需要申请。第一步先手动发帖，验证内容效果。"
    }
    
    print(f"\n  📊 推广渠道统计:")
    for k, v in stats.items():
        print(f"    {k}: {v}")
    
    return stats

if __name__ == "__main__":
    simulate_promotion()
