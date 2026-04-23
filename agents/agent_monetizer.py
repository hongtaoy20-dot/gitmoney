#!/usr/bin/env python3
"""
GitMoney Agent 3: Monetizer
=============================
数据分析与变现转化: 追踪流量、识别变现机会、转化引导。

功能:
  - 流量数据分析 (Views/Stars/Forks/Clones 追踪)
  - GitHub Sponsors 优化与文案生成
  - 付费内容转化 (Gumroad/Leanpub)
  - 潜在客户线索挖掘
  - A/B 测试广告位效果
  - 收益报告生成
"""

import os
import sys
import json
import yaml
import time
import requests
from datetime import datetime, timedelta
from pathlib import Path

# ─── 配置 ─────────────────────────────────────────────────────────────────
CONFIG_PATH = Path(__file__).parent.parent / "config" / "settings.yaml"
DATA_DIR = Path(__file__).parent.parent / "data" / "analytics"
LEADS_DIR = Path(__file__).parent.parent / "data" / "leads"
DATA_DIR.mkdir(parents=True, exist_ok=True)
LEADS_DIR.mkdir(parents=True, exist_ok=True)

with open(CONFIG_PATH) as f:
    CONFIG = yaml.safe_load(f)

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN") or CONFIG.get("github", {}).get("token", "")
GITHUB_USER = CONFIG.get("github", {}).get("username", "")
PRIMARY_REPO = CONFIG.get("github", {}).get("primary_repo", "gitmoney")
MON_CONFIG = CONFIG.get("monetizer", {})


# ─── 流量分析器 ───────────────────────────────────────────────────────

class TrafficAnalyzer:
    """GitHub Repo 流量数据采集与分析"""
    
    def __init__(self):
        self.headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json",
        }
        self.base = f"https://api.github.com/repos/{GITHUB_USER}/{PRIMARY_REPO}"
    
    def get_repo_stats(self) -> dict:
        """获取仓库统计信息"""
        # 基本信息
        resp = requests.get(self.base, headers=self.headers)
        repo = resp.json() if resp.status_code == 200 else {}
        
        # 流量 (需要 push 权限)
        traffic = {}
        
        # Clones
        resp = requests.get(f"{self.base}/traffic/clones", headers=self.headers)
        if resp.status_code == 200:
            data = resp.json()
            traffic["clones"] = {
                "count": data.get("count", 0),
                "uniques": data.get("uniques", 0),
            }
        
        # Views
        resp = requests.get(f"{self.base}/traffic/views", headers=self.headers)
        if resp.status_code == 200:
            data = resp.json()
            traffic["views"] = {
                "count": data.get("count", 0),
                "uniques": data.get("uniques", 0),
            }
        
        # Referrers
        resp = requests.get(f"{self.base}/traffic/popular/referrers", headers=self.headers)
        if resp.status_code == 200:
            referrers = resp.json()
            traffic["top_referrers"] = [r.get("referrer", "") for r in referrers[:5]]
        
        return {
            "name": repo.get("full_name", f"{GITHUB_USER}/{PRIMARY_REPO}"),
            "stars": repo.get("stargazers_count", 0),
            "forks": repo.get("forks_count", 0),
            "open_issues": repo.get("open_issues_count", 0),
            "watchers": repo.get("subscribers_count", 0),
            "traffic": traffic,
            "collected_at": datetime.utcnow().isoformat(),
        }
    
    def compute_trend(self) -> dict:
        """计算趋势 (与昨天/上周对比)"""
        # 加载历史数据
        history_file = DATA_DIR / "stats_history.json"
        history = []
        if history_file.exists():
            with open(history_file) as f:
                history = json.load(f)
        
        current = self.get_repo_stats()
        history.append(current)
        
        # 保留最近 30 天
        if len(history) > 30:
            history = history[-30:]
        
        with open(history_file, "w") as f:
            json.dump(history, f, indent=2)
        
        # 计算趋势
        trend = {}
        if len(history) >= 2:
            prev = history[-2]
            
            star_change = current["stars"] - prev["stars"]
            fork_change = current["forks"] - prev["forks"]
            
            trend = {
                "star_change_24h": star_change,
                "fork_change_24h": fork_change,
                "growth_rate": (star_change / max(prev["stars"], 1)) * 100 if prev["stars"] > 0 else 0,
            }
        
        return {"current": current, "trend": trend}
    
    def estimate_monthly_views(self) -> int:
        """估算月浏览量"""
        stats = self.get_repo_stats()
        views = stats.get("traffic", {}).get("views", {}).get("count", 0)
        
        # 如果数据不足 7 天，使用保守估算
        if views < 100:
            return max(100, stats["stars"] * 30)  # 每个 star 月浏览 30 次
        
        return views


# ─── 变现分析器 ──────────────────────────────────────────────────────

class MonetizationAnalyzer:
    """变现机会识别与转化"""
    
    def __init__(self):
        self.traffic = TrafficAnalyzer()
        self._llm_available = bool(os.environ.get("OPENROUTER_API_KEY", ""))
    
    def calculate_revenue_potential(self) -> dict:
        """基于流量数据计算变现潜力"""
        monthly_views = self.traffic.estimate_monthly_views()
        
        # 行业标准转化率 (保守)
        CONVERSION_RATES = {
            "github_sponsors": 0.001,      # 0.1% 浏览者成为赞助者
            "paid_content": 0.005,          # 0.5% 浏览者购买付费内容
            "consulting_lead": 0.002,       # 0.2% 浏览者成为咨询线索
            "affiliate_click": 0.02,        # 2% 浏览者点击联盟链接
        }
        
        AVERAGE_VALUES = {
            "github_sponsors": 10,          # $10/月 平均赞助
            "paid_content": 10,             # $10 平均付费内容价格
            "consulting_lead": 100,         # $100 平均咨询转化
            "affiliate_click": 0.50,        # $0.50 联盟点击
        }
        
        potential = {}
        for channel, conv in CONVERSION_RATES.items():
            conversions = int(monthly_views * conv)
            revenue = conversions * AVERAGE_VALUES[channel]
            potential[channel] = {
                "monthly_conversions": conversions,
                "monthly_revenue_usd": revenue,
            }
        
        total = sum(p["monthly_revenue_usd"] for p in potential.values())
        
        return {
            "monthly_views": monthly_views,
            "channels": potential,
            "total_potential_usd": total,
            "notes": "基于行业标准转化率估算，实际收入需 3-6 个月积累",
        }
    
    def generate_sponsor_readme(self) -> str:
        """生成 GitHub Sponsors 文案"""
        if not self._llm_available:
            return self._sponsor_template()
        
        prompt = """请为我的 GitHub 开源项目生成一个 Sponsors 页面文案。

项目: GitMoney - 多 Agent 自动化变现系统
定位: 帮助开发者通过自动化赚取额外收入

要求:
- 真诚、不营销感
- 说明赞助资金将用于: 服务器费用 + 开发时间 + 开源社区
- 包含 3 个赞助档位 ($3/mo, $10/mo, $25/mo)
- 英文
- 100-200 字"""
        
        headers = {
            "Authorization": f"Bearer {os.environ.get('OPENROUTER_API_KEY', '')}",
            "Content-Type": "application/json",
        }
        data = {
            "model": "deepseek/deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 500,
        }
        
        try:
            resp = requests.post("https://openrouter.ai/api/v1/chat/completions",
                               headers=headers, json=data, timeout=30)
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
        except Exception:
            pass
        
        return self._sponsor_template()
    
    def _sponsor_template(self) -> str:
        return """## Support GitMoney 💪

GitMoney is an open-source project that helps developers build automated income streams.

### Sponsorship Tiers

**🥉 Bronze ($3/month)** - Get listed in our README sponsors section
**🥈 Silver ($10/month)** - Priority feature requests + sponsor badge
**🥇 Gold ($25/month)** - Direct consultation + your logo in README

Your sponsorship directly supports:
- Server costs for automation infrastructure
- Development time for new features
- Open-source community contributions

[Sponsor on GitHub](https://github.com/sponsors/YOUR_USERNAME)
"""
    
    def find_consulting_leads(self) -> list:
        """从 Issue/讨论中发现潜在咨询客户"""
        # 搜索与自身专业相关的 Issue
        headers = self.traffic.headers
        queries = [
            "automation how to",
            "python script help",
            "CI/CD setup",
            "multi-agent system",
            "trading bot",
        ]
        
        leads = []
        for query in queries:
            url = f"https://api.github.com/search/issues?q={query}+state:open&sort=updated&per_page=3"
            resp = requests.get(url, headers=headers)
            if resp.status_code == 200:
                for issue in resp.json().get("items", []):
                    lead = {
                        "source": "github_issue",
                        "url": issue["html_url"],
                        "title": issue["title"],
                        "user": issue["user"]["login"],
                        "repo": issue.get("repository_url", "").split("/")[-1],
                        "potential_value": random.randint(50, 500),
                        "status": "new",
                        "discovered_at": datetime.utcnow().isoformat(),
                    }
                    leads.append(lead)
        
        # 保存线索
        if leads:
            leads_file = LEADS_DIR / f"leads_{datetime.utcnow().strftime('%Y%m%d')}.json"
            with open(leads_file, "w") as f:
                json.dump(leads, f, indent=2)
        
        return leads
    
    def generate_conversion_message(self, lead: dict) -> str:
        """生成针对性的转化消息"""
        prompt = f"""根据以下客户需求，生成一条个性化的付费咨询邀请信息。

客户 GitHub: {lead['user']}
客户问题: {lead['title']}
我对这个领域有 10+ 年经验，可以提供专业付费咨询服务。

要求:
- 真诚、有帮助、非营销 Spam
- 先免费提供一个小建议 (证明价值)
- 然后自然地提到付费咨询服务
- 英文
- 80-200 字"""
        
        if self._llm_available:
            headers = {
                "Authorization": f"Bearer {os.environ.get('OPENROUTER_API_KEY', '')}",
                "Content-Type": "application/json",
            }
            data = {
                "model": "deepseek/deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 300,
            }
            try:
                resp = requests.post("https://openrouter.ai/api/v1/chat/completions",
                                   headers=headers, json=data, timeout=30)
                if resp.status_code == 200:
                    return resp.json()["choices"][0]["message"]["content"]
            except Exception:
                pass
        
        return f"Hi @{lead['user']}, I saw your question about '{lead['title'][:50]}'. I've worked extensively on this and might be able to help. Feel free to reach out for a chat!"


# ─── 主控 ────────────────────────────────────────────────────────────

def run_daily_monetization():
    """每日变现任务"""
    traffic = TrafficAnalyzer()
    monetizer = MonetizationAnalyzer()
    
    print(f"[{datetime.utcnow().isoformat()}] Agent 3: Monetizer - 开始分析")
    
    # 1. 流量分析
    print("  采集仓库统计数据...")
    stats = traffic.get_repo_stats()
    print(f"  Stars: {stats['stars']} | Forks: {stats['forks']} | Views: {stats['traffic'].get('views', {}).get('count', 'N/A')}")
    
    # 2. 变现潜力估算
    print("  计算变现潜力...")
    potential = monetizer.calculate_revenue_potential()
    print(f"  月变现潜力: ${potential['total_potential_usd']}/mo")
    for channel, data in potential['channels'].items():
        print(f"    - {channel}: ${data['monthly_revenue_usd']}/mo")
    
    # 3. 生成 Sponsors 文案
    print("  生成 Sponsors 文案...")
    sponsor_text = monetizer.generate_sponsor_readme()
    
    # 4. 寻找咨询线索
    print("  挖掘潜在客户线索...")
    leads = monetizer.find_consulting_leads()
    print(f"  发现 {len(leads)} 个潜在线索")
    
    # 5. 生成每日报告
    report = {
        "timestamp": datetime.utcnow().isoformat(),
        "stats": stats,
        "revenue_potential": potential,
        "leads_found": len(leads),
    }
    
    report_path = DATA_DIR / f"monetization_report_{datetime.utcnow().strftime('%Y%m%d')}.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"[{datetime.utcnow().isoformat()}] Agent 3: Monetizer - 完成\n")
    return report


if __name__ == "__main__":
    run_daily_monetization()
