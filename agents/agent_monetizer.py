#!/usr/bin/env python3
"""
GitMoney Agent 3: Monetizer (V2 - Captain Edition)
===================================================
数据分析与变现转化 — 专精5条高价值管道:
1. 邮轮运营咨询 (Cruise Ops Consulting) — $200-300/mo
2. 邮轮文化推广/自媒体 (Cruise Content) — $50-100/mo
3. 邮轮运营工具/模板 (Ops Tools) — $50-80/mo
4. 美股价值投资指导 (US Stock Coaching) — $100-200/mo
5. ISM/ISPS/MLC 审核员服务 (Maritime Auditor) — $100-200/mo

目标: $500/mo 总变现
基于: 船长 15 年邮轮经验 + Master Mariner + 美股 3 年投资经验
"""

import os, sys, json, yaml, time, random, re, requests
from datetime import UTC, datetime, timedelta
from pathlib import Path

# ─── 配置 ─────────────────────────────────────────────────────────────────
CONFIG_PATH = Path(__file__).parent.parent / "config" / "settings.yaml"
DATA_DIR = Path(__file__).parent.parent / "data" / "analytics"
LEADS_DIR = Path(__file__).parent.parent / "data" / "leads"
LEADS_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

with open(CONFIG_PATH) as f:
    CONFIG = yaml.safe_load(f)

_raw_token = CONFIG.get("github", {}).get("token", "")
if _raw_token.startswith("${") and _raw_token.endswith("}"):
    _env_var = _raw_token[2:-1]
    GITHUB_TOKEN = os.environ.get(_env_var, "")
else:
    GITHUB_TOKEN = _raw_token
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "") or GITHUB_TOKEN
GITHUB_USER = CONFIG.get("github", {}).get("username", "")
PRIMARY_REPO = CONFIG.get("github", {}).get("primary_repo", "gitmoney")
MON_CONFIG = CONFIG.get("monetizer_v2", {})

# 你的核心资料 — 直接嵌入以便 Agent 生成专业文案
CAPTAIN_PROFILE = {
    "title": "Chief Officer / Master Mariner",
    "company": "Viking Cruises",
    "experience_years": 15,
    "certifications": ["Master Mariner", "ISM Auditor", "ISPS Auditor", "MLC Auditor"],
    "expertise": [
        "cruise operations management",
        "maritime safety & compliance (ISM/ISPS/MLC)",
        "shipboard management",
        "crew training & development",
        "US stock value investing (3yr experience)",
        "automation & AI for maritime",
    ],
    "target_role": "Marine Superintendent / Port Captain (Florida)",
    "immigration": "EB-3 EW3, PD 2026-03-05, target 2034-2038",
}

# ─── 第1管道: 邮轮运营咨询 ─────────────────────────────────────────────
class CruiseConsultingChannel:
    """管道1: 邮轮运营咨询 — 目标 $200-300/mo"""
    
    SERVICE_PACKAGES = {
        "operations_audit": {
            "name": "Cruise Operations Audit",
            "price": 150,
            "description": "One-day operational audit of cruise ship departments",
            "target": "ship managers, fleet ops directors",
        },
        "safety_compliance": {
            "name": "ISM/ISPS/MLC Compliance Check",
            "price": 200,
            "description": "Pre-audit compliance review for maritime regulations",
            "target": "cruise lines preparing for audit",
        },
        "crew_training": {
            "name": "Crew Training Program Design",
            "price": 350,
            "description": "Custom training programs for shipboard operations",
            "target": "HR directors at cruise companies",
        },
    }
    
    def estimate_potential(self) -> dict:
        """估算邮轮咨询管道月变现潜力"""
        # 保守: 每月 1-2 次小型咨询
        avg_rate = 120  # $/hr blended rate
        hrs_per_month = 2  # 保守估计每月咨询小时
        return {
            "channel": "cruise_consulting",
            "label": "邮轮运营咨询",
            "monthly_revenue_usd": avg_rate * hrs_per_month,
            "hourly_rate": avg_rate,
            "hours_per_month": hrs_per_month,
            "confidence": "medium",
            "path_to_500": "增加至每月 4 小时咨询",
            "leads_required_per_month": 3,
        }
    
    def search_leads(self) -> list:
        """搜索邮轮运营咨询线索"""
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json",
        }
        
        leads = []
        
        # GitHub: 搜索航运/邮轮相关的 Issue 和 Discussion
        queries = [
            "cruise operations management",
            "maritime compliance SOP",
            "ship management automation",
            "ISM implementation",
            "crew training program",
        ]
        
        for query in queries:
            try:
                url = f"https://api.github.com/search/issues?q={query}+state:open&sort=updated&per_page=2"
                resp = requests.get(url, headers=headers, timeout=15)
                if resp.status_code == 200:
                    for issue in resp.json().get("items", []):
                        leads.append({
                            "source": "github_issue",
                            "channel": "cruise_consulting",
                            "url": issue["html_url"],
                            "title": issue["title"],
                            "user": issue["user"]["login"],
                            "repo": issue.get("repository_url", "").split("/")[-1],
                            "potential_value": 150,
                            "persona_fit": self._score_relevance(issue["title"]),
                            "status": "new",
                            "discovered_at": datetime.now(UTC).isoformat(),
                        })
            except Exception:
                pass
        
        return leads
    
    def _score_relevance(self, text: str) -> int:
        """评估线索与邮轮运营的相关性 (0-100)"""
        keywords = ["cruise", "maritime", "ship", "vessel", "crew", "audit", 
                     "compliance", "ISM", "ISPS", "MLC", "port", "fleet",
                     "naval", "seafarer", "navigational", "safety"]
        text_lower = text.lower()
        score = sum(1 for kw in keywords if kw in text_lower) * 12
        return min(score, 100)


# ─── 第2管道: 邮轮文化/自媒体内容 ──────────────────────────────────────
class CruiseContentChannel:
    """管道2: 邮轮文化推广/自媒体 — 目标 $50-100/mo"""
    
    PLATFORMS = {
        "linkedin": {"reach": "high", "audience": "maritime professionals"},
        "medium": {"reach": "medium", "audience": "general readers"},
        "youtube_script": {"reach": "high", "audience": "cruise enthusiasts"},
        "wechat": {"reach": "medium", "audience": "Chinese maritime community"},
    }
    
    CONTENT_TOPICS = [
        "Day in the life of a Chief Officer on a luxury cruise ship",
        "What happens behind the scenes during turnaround day",
        "How cruise ships handle medical emergencies at sea",
        "The real cost of building a modern cruise ship",
        "Environmental technologies on modern cruise vessels",
        "Career progression: From cadet to Master Mariner",
        "How cruise ships navigate through storms",
        "Food supply logistics for a 5000-passenger ship",
        "Safety drills that passengers never see",
        "The economics of cruise line operations",
    ]
    
    def estimate_potential(self) -> dict:
        """估算自媒体变现潜力"""
        # 保守起步: LinkedIn 1篇/周, Medium 2篇/月
        articles_per_month = 6
        # Medium 平均 $0.5-$2/1000 views, 初始 ~2000 views/month
        ad_revenue = 15
        # WeChat 赞赏/付费阅读
        wechat_revenue = 30
        # 知识星球/付费社群引流
        community_lead = 25
        
        return {
            "channel": "cruise_content",
            "label": "邮轮内容/自媒体",
            "monthly_revenue_usd": ad_revenue + wechat_revenue + community_lead,
            "breakdown": {
                "medium_ad_revenue": ad_revenue,
                "wechat_tips": wechat_revenue,
                "community_funnel": community_lead,
            },
            "articles_per_month": articles_per_month,
            "confidence": "medium-high",
            "path_to_500": "积累 1000 关注者后开启付费社群、专栏和咨询引流",
            "leads_required": 0,  # 不需要 lead, 需要 content volume
        }
    
    def generate_post(self, topic_index: int = None) -> str:
        """生成一篇邮轮文化内容帖子"""
        if topic_index is None:
            topic_index = random.randint(0, len(self.CONTENT_TOPICS) - 1)
        topic = self.CONTENT_TOPICS[topic_index]
        
        # 有 OpenAI key 时用 LLM 生成，否则用模板
        if os.environ.get("OPENROUTER_API_KEY"):
            return self._generate_with_llm(topic)
        return self._generate_template(topic)
    
    def _generate_with_llm(self, topic: str) -> str:
        """用 LLM 生成邮轮内容"""
        prompt = f"""你是一位有15年经验的邮轮 Chief Officer (Master Mariner)。请写一篇关于以下主题的引人入胜的LinkedIn帖子（英文）：

主题: {topic}

要求:
- 第一人称, 真诚叙事
- 200-400字
- 包含1-2个具体细节/数据来增加真实感
- 结尾有一个自然的 Call-to-Action (问题或邀请讨论)
- 加入3-5个相关 hashtags
- 专业但不失亲和

帖子风格参考: "As a Chief Officer on Viking Cruises, I've seen..."
"""
        try:
            headers = {
                "Authorization": f"Bearer {os.environ.get('OPENROUTER_API_KEY', '')}",
                "Content-Type": "application/json",
            }
            data = {
                "model": "deepseek/deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.8,
                "max_tokens": 600,
            }
            resp = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers, json=data, timeout=60
            )
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
        except Exception:
            pass
        return self._generate_template(topic)
    
    def _generate_template(self, topic: str) -> str:
        """降级模板"""
        return f"""**{topic}**

After 15 years at sea with Viking Cruises, one thing I've learned is that every cruise has a story behind the scenes that passengers never see.

{topic.split(' ')[:5]}... is one of those stories.

👇 What aspect of cruise ship life are you most curious about? Drop your questions below and I'll share more insights.

#MaritimeLife #CruiseIndustry #MasterMariner #VikingCruises #LifeAtSea"""


# ─── 第3管道: 邮轮运营工具/模板 ────────────────────────────────────────
class CruiseToolsChannel:
    """管道3: 邮轮运营工具/模板 — 目标 $50-80/mo"""
    
    TOOLS = [
        {
            "name": "CruiseOps Checklist Generator",
            "price": 15,
            "desc": "Auto-generate operational checklists for turnarounds, drills, inspections",
            "platform": "Gumroad",
        },
        {
            "name": "Maritime Compliance Tracker",
            "price": 25,
            "desc": "Track ISM/ISPS/MLC compliance deadlines across your fleet",
            "platform": "GitHub Sponsor",
        },
        {
            "name": "Crew Training Schedule Builder",
            "price": 10,
            "desc": "Excel-based crew rotation and training calendar",
            "platform": "Gumroad",
        },
        {
            "name": "Value Stock Screener (Maritime Focus)",
            "price": 20,
            "desc": "Stock screener pre-filtered for maritime & logistics companies",
            "platform": "GitHub Sponsor",
        },
    ]
    
    def estimate_potential(self) -> dict:
        """估算工具变现潜力"""
        return {
            "channel": "cruise_tools",
            "label": "邮轮运营工具/模板",
            "monthly_revenue_usd": sum(t["price"] for t in self.TOOLS),
            "tools_available": len(self.TOOLS),
            "avg_price": sum(t["price"] for t in self.TOOLS) / len(self.TOOLS),
            "confidence": "medium",
            "path_to_500": "扩展至 10+ 工具，每月 20+ 次下载；或开发 SaaS 订阅 ($10/mo × 50 users)",
            "leads_required": 0,  # Product-led growth
        }


# ─── 第4管道: 美股价值投资指导 ──────────────────────────────────────────
class USStockChannel:
    """管道4: 美股价值投资指导 — 目标 $100-200/mo"""
    
    OFFERINGS = [
        {
            "name": "Weekly Value Stock Watchlist",
            "price": 20,
            "type": "subscription",
            "desc": "Weekly email with oversold value picks (PE<15, PB<2, RSI<30)",
        },
        {
            "name": "Portfolio Review (One-time)",
            "price": 50,
            "type": "service",
            "desc": "Personal portfolio review with value investing lens",
        },
        {
            "name": "Value Investing Starter Kit",
            "price": 15,
            "type": "digital_product",
            "desc": "Python scripts + Excel templates for value stock screening",
        },
        {
            "name": "Monthly Investment Q&A Session",
            "price": 30,
            "type": "subscription",
            "desc": "Group coaching call on value investing strategies",
        },
    ]
    
    def estimate_potential(self) -> dict:
        """估算美股投资变现潜力"""
        return {
            "channel": "us_stocks",
            "label": "美股价值投资指导",
            "monthly_revenue_usd": 120,  # Conservative: 5 watchlist subscribers + 2 kits
            "breakdown": {
                "watchlist_subscribers_5": 100,
                "starter_kits_2": 30,
                "portfolio_reviews_1": 50,
            },
            "confidence": "medium-high",
            "path_to_500": "20 watchlist subscribers ($400) + 5 kits ($75) + periodic reviews ($50)",
            "leads_required_per_month": 5,
        }
    
    def search_leads(self) -> list:
        """发掘美股投资潜在客户"""
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json",
        }
        leads = []
        
        # GitHub 上对投资感兴趣的用户
        queries = [
            "value investing screener",
            "stock analysis python",
            "RSI strategy",
            "dividend portfolio",
            "quantitative trading beginner",
        ]
        
        for query in queries:
            try:
                url = f"https://api.github.com/search/issues?q={query}+state:open&sort=updated&per_page=2"
                resp = requests.get(url, headers=headers, timeout=15)
                if resp.status_code == 200:
                    for issue in resp.json().get("items", []):
                        leads.append({
                            "source": "github_issue",
                            "channel": "us_stocks",
                            "url": issue["html_url"],
                            "title": issue["title"],
                            "user": issue["user"]["login"],
                            "repo": issue.get("repository_url", "").split("/")[-1],
                            "potential_value": random.choice([20, 30, 50]),
                            "persona_fit": self._score_relevance(issue["title"]),
                            "status": "new",
                            "discovered_at": datetime.now(UTC).isoformat(),
                        })
            except Exception:
                pass
        
        return leads
    
    def _score_relevance(self, text: str) -> int:
        keywords = ["stock", "investing", "trading", "dividend", "portfolio",
                     "value", "screener", "quant", "RSI", "PE", "market",
                     "yield", "analysis", "backtest", "strategy"]
        text_lower = text.lower()
        score = sum(1 for kw in keywords if kw in text_lower) * 10
        return min(score, 100)


# ─── 第5管道: ISM/ISPS/MLC 审核员服务 ─────────────────────────────────
class MaritimeAuditorChannel:
    """管道5: ISM/ISPS/MLC 审核员资格变现 — 目标 $100-200/mo"""
    
    def estimate_potential(self) -> dict:
        return {
            "channel": "maritime_auditor",
            "label": "ISM/ISPS/MLC 审核服务",
            "monthly_revenue_usd": 120,
            "breakdown": {
                "part_time_audit_work": 200,   # 偶尔接审核单
                "pre_audit_document_review": 100,
                "audit_training_material": 50,
            },
            "confidence": "high",
            "notes": "ISM/ISPS/MLC Auditor 是硬资格认证，每单 $500-2000。每月即使只做 1 次小审核也能远超 $500",
            "path_to_500": "1次小型pre-audit咨询($200) + 审核手册模板销售($50) + LinkedIn 引流线索($100)+美股投资指导($150)",
            "leads_required_per_month": 2,
        }
    
    def search_leads(self) -> list:
        """搜索海事审核相关线索"""
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json",
        }
        leads = []
        
        queries = [
            "ISM audit preparation",
            "maritime safety management",
            "ship inspection checklist",
            "port state control",
            "MLC compliance",
        ]
        
        for query in queries:
            try:
                url = f"https://api.github.com/search/issues?q={query}+state:open&sort=updated&per_page=2"
                resp = requests.get(url, headers=headers, timeout=15)
                if resp.status_code == 200:
                    for issue in resp.json().get("items", []):
                        leads.append({
                            "source": "github_issue",
                            "channel": "maritime_auditor",
                            "url": issue["html_url"],
                            "title": issue["title"],
                            "user": issue["user"]["login"],
                            "repo": issue.get("repository_url", "").split("/")[-1],
                            "potential_value": random.choice([100, 150, 200]),
                            "persona_fit": self._score_relevance(issue["title"]),
                            "status": "new",
                            "discovered_at": datetime.now(UTC).isoformat(),
                        })
            except Exception:
                pass
        return leads
    
    def _score_relevance(self, text: str) -> int:
        keywords = ["ISM", "ISPS", "MLC", "IMO", "SOLAS", "MARPOL", "audit",
                     "inspection", "compliance", "safety", "ship", "vessel",
                     "maritime", "port", "flag state", "classification"]
        text_lower = text.lower()
        score = sum(1 for kw in keywords if kw in text_lower) * 12
        return min(score, 100)


# ─── 变现引擎 V2 ──────────────────────────────────────────────────────
class MonetizationEngineV2:
    """V2 变现引擎 — 5管道并行分析"""
    
    def __init__(self):
        self.channels = {
            "cruise_consulting": CruiseConsultingChannel(),
            "cruise_content": CruiseContentChannel(),
            "cruise_tools": CruiseToolsChannel(),
            "us_stocks": USStockChannel(),
            "maritime_auditor": MaritimeAuditorChannel(),
        }
    
    def run_full_analysis(self) -> dict:
        """运行全管道变现分析"""
        print(f"[{datetime.now(UTC).isoformat()}] Monetization Engine V2 - 开始全管道分析")
        
        results = {}
        total_potential = 0
        
        for key, channel in self.channels.items():
            print(f"\n  {'='*50}")
            est = channel.estimate_potential()
            results[key] = est
            total_potential += est["monthly_revenue_usd"]
            print(f"  管道: {est['label']}")
            print(f"  月估: ${est['monthly_revenue_usd']}/mo")
            
            # 如果管道有线索挖掘能力
            if hasattr(channel, 'search_leads'):
                leads = channel.search_leads()
                results[key]["leads_found"] = len(leads)
                print(f"  线索: {len(leads)} 个")
                
                # 保存线索
                if leads:
                    leads_file = LEADS_DIR / f"{key}_leads_{datetime.now(UTC).strftime('%Y%m%d')}.json"
                    with open(leads_file, "w") as f:
                        json.dump(leads, f, indent=2, ensure_ascii=False)
        
        print(f"\n  {'='*50}")
        print(f"  V2 总月变现潜力: ${total_potential}/mo")
        
        # 生成变现策略建议
        strategies = self._generate_strategies(results, total_potential)
        
        report = {
            "timestamp": datetime.now(UTC).isoformat(),
            "engine_version": "2.0",
            "profile": {
                "name": CAPTAIN_PROFILE["title"],
                "certifications": CAPTAIN_PROFILE["certifications"],
                "expertise_areas": CAPTAIN_PROFILE["expertise"],
            },
            "total_monthly_potential_usd": total_potential,
            "channels": results,
            "strategies": strategies,
            "target_gap": max(0, 500 - total_potential),
            "target_met": total_potential >= 500,
            "notes": [
                "所有管道基于保守估计（最低转化率假设）",
                "实际成熟后每管道的 $/mo 可提升 2-5x",
                "ISM/ISPS/MLC Auditor 单次审核费 $500-2000，一次即可达成月目标",
                "建议优先发力 Marine Auditor + US Stock 双管道",
            ],
        }
        
        # 保存报告
        report_path = DATA_DIR / f"monetization_v2_{datetime.now(UTC).strftime('%Y%m%d')}.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n  报告已保存: {report_path}")
        print(f"[{datetime.now(UTC).isoformat()}] V2 全管道分析完成")
        
        return report
    
    def _generate_strategies(self, results: dict, total: float) -> list:
        """基于分析结果生成变现策略建议"""
        strategies = []
        
        if total < 200:
            strategies.append("短期: 先做投流内容 (LinkedIn 每日邮轮故事)，快速建立个人品牌")
            strategies.append("短期: 在 GitMoney 仓库上架价值投资模板 (Gumroad $15)")
        elif total < 400:
            strategies.append("中期: 申请 ISM/ISPS MLC 审核兼职 (每单 $500+)")
            strategies.append("中期: 招募美股投资 watchlist 订阅用户 (reach目标: 20人)")
        else:
            strategies.append("长期: 启动付费社群 (知识星球/小鹅通) — 邮轮+美投双主题")
            strategies.append("长期: 开发 Maritime Ops SaaS 工具 MVP ($10/mo 订阅)")
        
        strategies.append("跨管道协同: 邮轮内容 → 引流到 LinkedIn → 转化为咨询/审核客户")
        strategies.append(f"当前总估 ${total:.0f}/mo，差 ${max(0, 500-total):.0f}/mo 达到 $500 目标")
        
        return strategies


# ─── 每日执行 ──────────────────────────────────────────────────────────
def run_daily_monetization():
    engine = MonetizationEngineV2()
    report = engine.run_full_analysis()
    
    # 打印摘要
    print("\n" + "=" * 60)
    print("  GitMoney Monetizer V2 — 每日变现报告")
    print("=" * 60)
    
    for key, data in report["channels"].items():
        bar_len = int(data["monthly_revenue_usd"] / 5)
        bar = "█" * min(bar_len, 40)
        print(f"  {data['label']:<20s} ${data['monthly_revenue_usd']:<6.0f} {bar}")
    
    print("-" * 60)
    total = report["total_monthly_potential_usd"]
    bar = "█" * min(int(total / 5), 40)
    print(f"  {'总计':<20s} ${total:<6.0f} {bar}")
    
    if report["target_met"]:
        print(f"\n  ✅ 已超过 $500/mo 目标！")
    else:
        gap = report["target_gap"]
        print(f"\n  📈 距离 $500/mo 目标还差 ${gap}/mo")
    
    print(f"\n  报告路径: {DATA_DIR}/monetization_v2_{datetime.now(UTC).strftime('%Y%m%d')}.json")
    print(f"  ({datetime.now(UTC).strftime('%H:%M UTC')})")
    print()
    
    return report


if __name__ == "__main__":
    run_daily_monetization()
