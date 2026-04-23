#!/usr/bin/env python3
"""
GitMoney Agent 2: Traffic Driver (V2 - Captain Edition)
=========================================================
自动化推广引流 — 专精5条变现管道的流量获取:

渠道建设:
1. LinkedIn → 邮轮运营/海事合规内容 → B2B咨询线索
2. GitHub → 开源工具/技术内容 → Star+Issue互动 → 变现漏斗
3. Reddit (r/maritime, r/investing) → 精准社区引流
4. Hacker News → 技术文章曝光 → 开源项目关注
5. 跨管道协同 → 内容一篇多发 + 互相导流
"""

import os, sys, json, yaml, time, random, re, requests
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Optional

# ─── 配置 ─────────────────────────────────────────────────────────────────
CONFIG_PATH = Path(__file__).parent.parent / "config" / "settings.yaml"
DATA_DIR = Path(__file__).parent.parent / "data" / "analytics"
LEADS_DIR = Path(__file__).parent.parent / "data" / "leads"
DATA_DIR.mkdir(parents=True, exist_ok=True)
LEADS_DIR.mkdir(parents=True, exist_ok=True)

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

# ─── LinkedIn 推广器 ────────────────────────────────────────────────────
class LinkedInPromoter:
    """LinkedIn 推广 — 核心 B2B 引流渠道"""

    # 你的固定身份信息 — 用于生成 LinkedIn 内容
    PROFILE_BIO = "Chief Officer at Viking Cruises | Master Mariner | ISM/ISPS/MLC Auditor | US Value Investor"

    CONTENT_THEMES = [
        # (theme, target_industry, cta_type)
        ("Day-to-day cruise operations insights", "cruise lines / fleet management", "consulting"),
        ("Maritime safety & compliance stories", "ship management companies", "audit"),
        ("Career growth at sea", "junior officers / maritime students", "content"),
        ("Value investing for maritime professionals", "maritime professionals", "stock"),
        ("Automation tools for ship ops", "tech-forward shipping companies", "tools"),
    ]

    def __init__(self):
        self.api_key = os.environ.get("OPENROUTER_API_KEY", "")
        self.llm_available = bool(self.api_key)

    def generate_linkedin_post(self, theme_index: int = None, topic_title: str = "") -> dict:
        """生成一篇 LinkedIn 帖子 (免费长文/短帖)"""
        if theme_index is None:
            theme_index = random.randint(0, len(self.CONTENT_THEMES) - 1)

        theme, industry, cta = self.CONTENT_THEMES[theme_index]

        if self.llm_available:
            return self._generate_with_llm(theme, industry, cta, topic_title)
        return self._generate_template(theme, industry, cta)

    def _generate_with_llm(self, theme: str, industry: str, cta: str, topic_title: str) -> dict:
        """用 LLM 生成 LinkedIn 帖子"""
        prompt = f"""你是一位有 15 年经验的 Viking Cruises Chief Officer (Master Mariner)。
请写一篇适合 LinkedIn 发布的专业帖子，主题属于: {theme}

目标行业/读者: {industry}
CTA类型: {cta} (consulting → 咨询服务, audit → 审核服务, content → 引流, stock → 投资指导, tools → 工具)

参考身份信息:
- Chief Officer, Viking Cruises (15年)
- ISM/ISPS/MLC Auditor
- US Value Investor (3年经验)
- 目标: 从中国 Tier 2 城市 → Florida USA

要求:
- 第一人称，真诚，专业
- 200-400 字
- 分享1-2个具体经验/洞察（不要泛泛而谈）
- 自然结尾 CTA（与 cta_type 匹配）
- 添加 5 个相关 hashtag（#Maritime #CruiseLife #Leadership 等）

内容风格参考:
'After 15 years at sea, one lesson stands out above all...'
'What they don't teach you in maritime academy...'
'The most underrated skill in cruise operations...'

请直接生成帖子内容。"""

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            data = {
                "model": "deepseek/deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.8,
                "max_tokens": 800,
            }
            resp = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers, json=data, timeout=60
            )
            if resp.status_code == 200:
                content = resp.json()["choices"][0]["message"]["content"]
                return {
                    "content": content,
                    "theme": theme,
                    "industry": industry,
                    "cta_type": cta,
                    "hashtags": re.findall(r'#\w+', content),
                    "generated_by": "llm",
                }
        except Exception:
            pass
        return self._generate_template(theme, industry, cta)

    def _generate_template(self, theme: str, industry: str, cta: str) -> dict:
        """降级模板"""
        return {
            "content": f"""**{theme}**

After 15 years on the bridge of Viking Cruises, I've learned that {theme.lower()} is one of the most misunderstood aspects of our industry.

Here's what I've found actually works:

1️⃣ Start with the fundamentals — don't overcomplicate it
2️⃣ Listen to your crew — they know the ship better than anyone
3️⃣ Document everything — data is your best friend in operations

The maritime industry is transforming rapidly. Those who adapt will thrive.

What's your experience been? Drop a comment below.

#Maritime #CruiseIndustry #Leadership #MarineOperations #VikingCruises""",
            "theme": theme,
            "industry": industry,
            "cta_type": cta,
            "hashtags": ["#Maritime", "#CruiseIndustry", "#Leadership", "#MarineOperations", "#VikingCruises"],
            "generated_by": "template",
        }

    def estimate_reach(self, followers: int = 0) -> int:
        """估算 LinkedIn 帖子近期可达到的触达量"""
        # 新账号起步保守估计
        base = followers or 50
        return int(base * 1.5 + random.randint(50, 200))


# ─── Reddit/HN 精准推广 ───────────────────────────────────────────────
class MaritimeSocialPromoter:
    """针对海事/投资社区的精准推广"""

    MARITIME_SUBREDDITS = ["r/maritime", "r/shipping", "r/Nautical", "r/MarineEngineering"]
    INVESTING_SUBREDDITS = ["r/investing", "r/valueinvesting", "r/stocks", "r/dividends"]
    TECH_SUBREDDITS = ["r/Python", "r/opensource", "r/coolgithubprojects", "r/automation"]

    def __init__(self):
        self.api_key = os.environ.get("OPENROUTER_API_KEY", "")
        self.llm_available = bool(self.api_key)

    def find_best_subreddits(self, channel: str) -> list:
        """根据变现管道推荐发帖社区"""
        channel_map = {
            "cruise_consulting": self.MARITIME_SUBREDDITS + ["r/logistics"],
            "maritime_auditor": self.MARITIME_SUBREDDITS,
            "cruise_content": self.MARITIME_SUBREDDITS + ["r/travel"],
            "us_stocks": self.INVESTING_SUBREDDITS + ["r/algotrading"],
            "cruise_tools": self.TECH_SUBREDDITS + self.MARITIME_SUBREDDITS,
            "general": self.TECH_SUBREDDITS,
        }
        return channel_map.get(channel, self.TECH_SUBREDDITS[:2])

    def generate_reddit_post(self, title: str, subreddit: str, channel: str) -> dict:
        """生成适合特定 subreddit 的红迪帖子"""
        if not self.llm_available:
            return self._reddit_template(title, subreddit)

        prompt = f"""请生成一篇 Reddit 帖子，准备提交到 {subreddit}。

内容主题: {title}
变现管道: {channel}
作者身份: Viking Cruises Chief Officer, ISM/ISPS/MLC Auditor, Value Investor

要求:
- 符合 Reddit 社区文化和 {subreddit} 的预期
- 不要明显的营销推广语气
- 真诚分享经验或提问引导讨论
- 适合帖子（不是评论），200-500字
- 以分享专业视角为核心，而不是推销

请输出格式:
TITLE: (帖子标题, 吸引眼球)
BODY: (帖子正文)
"""

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            data = {
                "model": "deepseek/deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 800,
            }
            resp = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers, json=data, timeout=60
            )
            if resp.status_code == 200:
                content = resp.json()["choices"][0]["message"]["content"]
                return {"subreddit": subreddit, "content": content, "generated_by": "llm"}
        except Exception:
            pass
        return self._reddit_template(title, subreddit)

    def _reddit_template(self, title: str, subreddit: str) -> dict:
        return {
            "subreddit": subreddit,
            "content": f"TITLE: {title}\nBODY: I've been working in the maritime industry for 15 years and wanted to share some insights about this topic. Happy to answer questions in the comments!",
            "generated_by": "template",
        }


# ─── Hacker News 推广 ────────────────────────────────────────────────
class HNPromoter:
    """Hacker News 推广 — 适合技术类/开源项目"""

    def __init__(self):
        self.api_key = os.environ.get("OPENROUTER_API_KEY", "")

    def generate_hn_title(self, project_name: str, project_desc: str) -> str:
        """生成吸引 Hacker News 社区的标题"""
        if self.api_key:
            prompt = f"""为以下开源项目生成一个适合 Hacker News 的提交标题。

项目: {project_name}
描述: {project_desc}

要求:
- 吸引 HN 社区 (开发者和创业者)
- 诚实，不 clickbait
- 突出技术亮点或独特价值
- 60-80 字符
- 只是一个标题，不要解释

标题:"""
            try:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                }
                data = {
                    "model": "deepseek/deepseek-chat",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.6,
                    "max_tokens": 100,
                }
                resp = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers, json=data, timeout=30
                )
                if resp.status_code == 200:
                    return resp.json()["choices"][0]["message"]["content"].strip()
            except Exception:
                pass
        return f"Show HN: {project_name} – {project_desc[:80]}"

    def best_post_time(self) -> str:
        """HN 最佳发帖时间 (美东早 9-11am)"""
        # UTC 转换
        utc_now = datetime.now(UTC)
        # 美东 = UTC-4 (夏令时)
        et_hour = (utc_now.hour - 4) % 24
        if 8 <= et_hour <= 12:
            return "optimal"
        elif 6 <= et_hour <= 14:
            return "good"
        return "suboptimal"


# ─── GitHub 生态推广器 V2 ──────────────────────────────────────────────
class GitHubPromoterV2:
    """V2 GitHub 推广 — 海事+投资精准生态"""

    def __init__(self):
        self.headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json",
        }

    def find_trending_repos(self, language: str = None, topic: str = None) -> list:
        """发现趋势仓库 — 可按语言/主题筛选"""
        qualifiers = ["created:>2026-01-01"]
        if language:
            qualifiers.append(f"language:{language}")
        if topic:
            qualifiers.append(f"topic:{topic}")
            
        q = "+".join(qualifiers)
        url = f"https://api.github.com/search/repositories?q={q}&sort=stars&order=desc&per_page=10"
        
        try:
            resp = requests.get(url, headers=self.headers, timeout=15)
            if resp.status_code == 200:
                repos = resp.json().get("items", [])
                return [{
                    "name": r["full_name"],
                    "stars": r["stargazers_count"],
                    "description": r["description"],
                    "language": r["language"],
                    "topics": r.get("topics", []),
                    "url": r["html_url"],
                } for r in repos]
        except Exception:
            pass
        return []

    def find_external_mentions(self) -> list:
        """搜索外界提到你的项目的 Issue/Discussion"""
        query = f"\"gitmoney\" OR \"{GITHUB_USER}/gitmoney\" in:body"
        url = f"https://api.github.com/search/issues?q={query}&sort=updated&per_page=10"
        try:
            resp = requests.get(url, headers=self.headers, timeout=15)
            if resp.status_code == 200:
                items = resp.json().get("items", [])
                return [{
                    "url": i["html_url"],
                    "title": i["title"],
                    "repo": i.get("repository_url", "").split("/")[-1],
                    "user": i["user"]["login"],
                } for i in items]
        except Exception:
            pass
        return []

    def star_relevant_repos(self, topics: list = None) -> list:
        """发现并记录值得关注的同类仓库"""
        if topics is None:
            topics = ["maritime", "cruise", "stock-screener", "automation"]
        results = []
        for topic in topics:
            repos = self.find_trending_repos(topic=topic)
            results.extend(repos)
        # 去重
        seen = set()
        deduped = []
        for r in results:
            if r["name"] not in seen:
                seen.add(r["name"])
                deduped.append(r)
        return deduped[:10]

    def analyze_repo_seo(self) -> dict:
        """分析自己的仓库 SEO 表现"""
        url = f"https://api.github.com/repos/{GITHUB_USER}/gitmoney"
        try:
            resp = requests.get(url, headers=self.headers, timeout=15)
            if resp.status_code == 200:
                repo = resp.json()
                return {
                    "name": repo["full_name"],
                    "description": repo.get("description", ""),
                    "topics": repo.get("topics", []),
                    "has_website": bool(repo.get("homepage")),
                    "has_wiki": repo.get("has_wiki", False),
                    "open_issues": repo.get("open_issues_count", 0),
                    "stars": repo.get("stargazers_count", 0),
                    "seo_score": self._calc_seo_score(repo),
                }
        except Exception:
            pass
        return {"error": "could not fetch repo info"}

    def _calc_seo_score(self, repo: dict) -> int:
        """计算仓库 SEO 评分"""
        score = 0
        desc = repo.get("description", "") or ""
        topics = repo.get("topics", []) or []
        readme = repo.get("has_readme", False)
        
        if len(desc) > 30:
            score += 20
        if len(topics) >= 3:
            score += 20
        if readme:
            score += 20
        if repo.get("homepage"):
            score += 15
        if repo.get("stargazers_count", 0) > 10:
            score += 15
        if repo.get("forks_count", 0) > 3:
            score += 10
        
        return min(score, 100)


# ─── 每日执行 ──────────────────────────────────────────────────────────
def run_daily_traffic():
    linkedin = LinkedInPromoter()
    social = MaritimeSocialPromoter()
    hn = HNPromoter()
    github = GitHubPromoterV2()

    print(f"[{datetime.now(UTC).isoformat()}] Agent 2: Traffic Driver V2 - 开始流量运营")

    # 1. LinkedIn 帖子生成
    print("  生成 LinkedIn 帖子...")
    post = linkedin.generate_linkedin_post()
    print(f"  LinkedIn: {post['theme'][:50]}")
    est_reach = linkedin.estimate_reach()
    print(f"  预估触达: ~{est_reach} 人")

    # 2. GitHub 生态分析
    print("\n  分析 GitHub 生态...")
    seo = github.analyze_repo_seo()
    print(f"  仓库 SEO 评分: {seo.get('seo_score', 'N/A')}/100")
    
    trending = github.find_trending_repos(language="Python")
    print(f"  趋势仓库: {len(trending)} 个")
    
    mentions = github.find_external_mentions()
    if mentions:
        print(f"  外部提及: {len(mentions)} 条")
    else:
        print(f"  外部提及: 0 条 (新项目正常)")

    # 3. 推广策略推荐
    print("\n  推广策略:")
    channels_to_push = ["cruise_consulting", "maritime_auditor", "us_stocks", "cruise_content"]
    for ch in channels_to_push:
        subs = social.find_best_subreddits(ch)
        print(f"    {ch}: 推荐发帖 → {', '.join(subs[:2])}")

    hn_time = hn.best_post_time()
    print(f"    HN: {'当前是黄金时间 ✅' if hn_time == 'optimal' else f'最佳时机: {hn_time}'}")

    # 4. 保存报告
    report = {
        "timestamp": datetime.now(UTC).isoformat(),
        "linkedin_post_theme": post["theme"],
        "linkedin_estimated_reach": est_reach,
        "github_seo_score": seo.get("seo_score", 0),
        "trending_repos_found": len(trending),
        "external_mentions": len(mentions),
        "recommended_subreddits": {ch: social.find_best_subreddits(ch) for ch in channels_to_push},
        "hn_post_time_optimal": hn_time == "optimal",
    }

    report_path = DATA_DIR / f"traffic_report_{datetime.now(UTC).strftime('%Y%m%d')}.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n  报告已保存: {report_path}")
    print(f"[{datetime.now(UTC).isoformat()}] Agent 2: Traffic Driver V2 - 完成\n")
    return report


if __name__ == "__main__":
    run_daily_traffic()
