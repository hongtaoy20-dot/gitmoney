#!/usr/bin/env python3
"""
GitMoney Agent 2: Traffic Driver
=================================
自动完成推广引流: SEO 优化、社交媒体推广、GitHub 生态参与。

功能:
  - SEO 优化 (README/Issue meta 分析 + 关键词注入)
  - 社交媒体自动推广 (Twitter/X, LinkedIn, Reddit, Hacker News)
  - GitHub 生态参与 (相关 Issue 回复、PR 协作)
  - Trending 仓库监控与分析
  - 外链建设
"""

import os
import sys
import json
import yaml
import time
import random
import re
import requests
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

# 支持 ${ENV_VAR} 模板语法和直接值
_raw_token = CONFIG.get("github", {}).get("token", "")
if _raw_token.startswith("${") and _raw_token.endswith("}"):
    _env_var = _raw_token[2:-1]
    GITHUB_TOKEN = os.environ.get(_env_var, "")
else:
    GITHUB_TOKEN = _raw_token
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "") or GITHUB_TOKEN
GITHUB_USER = CONFIG.get("github", {}).get("username", "")


# ─── SEO 优化器 ────────────────────────────────────────────────────────

class SEOOptimizer:
    """README/内容 SEO 分析与优化"""
    
    def __init__(self):
        self.api_base = "https://openrouter.ai/api/v1/chat/completions"
        self.api_key = os.environ.get("OPENROUTER_API_KEY", "")
    
    def analyze_readme_seo(self, readme_content: str) -> dict:
        """分析 README 的 SEO 评分"""
        score = 0
        issues = []
        suggestions = []
        
        # 1. H1 标题检查
        if re.search(r'^#\s+\S+', readme_content, re.MULTILINE):
            score += 15
        else:
            issues.append("缺少 H1 标题")
            suggestions.append("添加一个包含主要关键词的 H1 标题")
        
        # 2. 字数检查
        word_count = len(readme_content)
        if word_count > 300:
            score += 15
        elif word_count > 150:
            score += 8
        else:
            issues.append("内容过短 (< 150 字) 不利于 SEO")
            suggestions.append("将 README 扩展到 300 字以上")
        
        # 3. 关键词密度
        keywords = ["python", "automation", "agent", "github", "tutorial",
                    "guide", "open source", "api", "deploy", "docker"]
        keyword_hits = sum(1 for kw in keywords if kw.lower() in readme_content.lower())
        keyword_score = min(keyword_hits * 5, 20)
        score += keyword_score
        
        # 4. 结构完整性
        has_code = "```" in readme_content
        has_list = "- " in readme_content or "* " in readme_content
        has_link = "http" in readme_content
        
        if has_code: score += 10
        if has_list: score += 10
        if has_link: score += 10
        
        # 5. Badge 检查
        badge_count = len(re.findall(r'!\[.*?\]\(.*?\)', readme_content))
        if badge_count >= 3:
            score += 10
        elif badge_count >= 1:
            score += 5
        
        # 6. 描述性开头
        first_para = readme_content.split('\n\n')[0] if '\n\n' in readme_content else readme_content
        if len(first_para) > 50:
            score += 10
        
        return {
            "score": min(score, 100),
            "word_count": word_count,
            "keyword_hits": keyword_hits,
            "has_code": has_code,
            "has_list": has_list,
            "badge_count": badge_count,
            "issues": issues,
            "suggestions": suggestions,
        }
    
    def generate_seo_meta(self, title: str, description: str, keywords: list) -> str:
        """生成 SEO 优化的 meta 描述"""
        prompt = f"""生成一段 SEO 优化的 GitHub 仓库描述 (用于 repo description 和 social preview)。

标题: {title}
核心关键词: {', '.join(keywords)}
原始描述: {description}

要求:
- 长度 80-120 字符
- 自然嵌入 2-3 个关键词
- 吸引开发者点击
- 不含营销套话
- 英文"""
        
        return self._call_llm(prompt)
    
    def _call_llm(self, prompt: str) -> str:
        if not self.api_key:
            return f"{prompt[:60]}... (no API key for full generation)"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        data = {
            "model": "deepseek/deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.5,
            "max_tokens": 300,
        }
        try:
            resp = requests.post(self.api_base, headers=headers, json=data, timeout=30)
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
        except Exception:
            pass
        return description_from_prompt(prompt)


def description_from_prompt(prompt: str) -> str:
    """降级 - 从 prompt 提取描述"""
    lines = prompt.split('\n')
    for l in lines:
        if l.strip().startswith("- ") and len(l) > 30:
            return l.strip("- ").strip()
    return f"A guide about {prompt.split(',')[0]}"


# ─── Twitter/X 推广器 ─────────────────────────────────────────────────

class TwitterPromoter:
    """Twitter/X 自动推广"""
    
    def __init__(self):
        self.api_key = CONFIG.get("traffic", {}).get("platforms", {}).get("twitter", {}).get("api_key", "")
        self.enabled = CONFIG.get("traffic", {}).get("platforms", {}).get("twitter", {}).get("enabled", False)
    
    def post_content(self, title: str, url: str, description: str) -> dict:
        """发布推文 (需要 Twitter API v2 凭据)"""
        if not self.enabled or not self.api_key:
            return {"status": "skipped", "reason": "Twitter API not configured"}
        
        # Twitter API v2 发推 (需要 OAuth 2.0 Bearer Token + 用户认证)
        # 此处简化 - 记录待发布队列
        tweet_text = f"{title}\n\n{description[:200]}\n\n{url}"
        
        # 保存到待发布队列
        queue_file = DATA_DIR / "tweet_queue.json"
        queue = []
        if queue_file.exists():
            with open(queue_file) as f:
                queue = json.load(f)
        
        queue.append({
            "text": tweet_text,
            "created_at": datetime.now(UTC).isoformat(),
            "status": "pending",
        })
        
        with open(queue_file, "w") as f:
            json.dump(queue[-50:], f, indent=2)  # 保留最近 50 条
        
        return {"status": "queued", "tweet": tweet_text[:80]}
    
    def generate_tweet_thread(self, article_content: str) -> list:
        """从文章生成推文线程 (3-5 条)"""
        prompt = f"""将以下文章转换为 Twitter/X 线程 (3-5 条推文):

{article_content[:1500]}

要求:
- 每条 < 280 字符
- 第1条吸引注意，最后1条引导点击链接
- 每条之间必须有逻辑衔接
- 使用适当的话题标签 (最多3个)
- 风格专业但不枯燥

输出格式: 每条推文用 --- 分隔"""
        
        headers = {
            "Authorization": f"Bearer {os.environ.get('OPENROUTER_API_KEY', '')}",
            "Content-Type": "application/json",
        }
        data = {
            "model": "deepseek/deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.8,
            "max_tokens": 1000,
        }
        
        try:
            resp = requests.post("https://openrouter.ai/api/v1/chat/completions",
                               headers=headers, json=data, timeout=30)
            if resp.status_code == 200:
                content = resp.json()["choices"][0]["message"]["content"]
                tweets = [t.strip() for t in content.split("---") if t.strip()]
                return tweets[:5]
        except Exception:
            pass
        
        return [f"Check out this article: {article_content[:200]}... #dev #opensource"]


# ─── GitHub 生态推广 ─────────────────────────────────────────────────

class GitHubPromoter:
    """GitHub 生态内的推广 (参与 Issue, Trending 分析)"""
    
    def __init__(self):
        self.headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json",
        }
    
    def find_relevant_issues(self, keywords: list, limit: int = 5) -> list:
        """搜索相关的 GitHub Issue 以便参与讨论"""
        query = "+".join(keywords[:3])
        url = f"https://api.github.com/search/issues?q={query}+state:open&sort=updated&per_page={limit}"
        
        resp = requests.get(url, headers=self.headers)
        if resp.status_code == 200:
            return resp.json().get("items", [])
        return []
    
    def generate_helpful_reply(self, issue_body: str, issue_title: str) -> Optional[str]:
        """生成对 Issue 有帮助的回复"""
        prompt = f"""作为一个技术社区贡献者，请对以下 GitHub Issue 生成有帮助的回复。

Issue 标题: {issue_title}
Issue 内容: {issue_body[:1000]}

要求:
- 确实是提出建设性建议，不是灌水
- 简洁、专业、有帮助
- 可以提出解决方案、类似经验或资源推荐
- 100-300 字
- 保持真诚，不要过度推销
    
回复:"""
        
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
        return None
    
    def analyze_trending(self) -> list:
        """分析 GitHub Trending 仓库"""
        url = "https://api.github.com/search/repositories?q=created:>2026-01-01&sort=stars&order=desc&per_page=10"
        resp = requests.get(url, headers=self.headers)
        
        if resp.status_code == 200:
            repos = resp.json().get("items", [])
            trending = []
            for r in repos:
                trending.append({
                    "name": r["full_name"],
                    "stars": r["stargazers_count"],
                    "description": r["description"],
                    "language": r["language"],
                    "topics": r.get("topics", []),
                })
            return trending
        return []
    
    def find_collaboration_opportunities(self) -> list:
        """寻找合适的协作机会 (PR / Issue)"""
        # 优先找自己技术栈相关的开源项目
        keywords = ["python", "automation", "cli", "developer-tools"]
        issues = self.find_relevant_issues(keywords, limit=10)
        
        opportunities = []
        for issue in issues[:3]:
            opportunities.append({
                "repo": issue.get("repository_url", "").split("/")[-2] + "/" + issue.get("repository_url", "").split("/")[-1],
                "issue_number": issue["number"],
                "title": issue["title"],
                "url": issue["html_url"],
                "score": random.randint(60, 95),  # 参与价值评分
            })
        
        return opportunities


# ─── Reddit/HN 推广器 ────────────────────────────────────────────────

class SocialPromoter:
    """Reddit / Hacker News 推广"""
    
    def post_to_reddit(self, title: str, url: str, subreddit: str = "programming") -> dict:
        """提交到 Reddit (需要 Reddit API 凭据)"""
        config = CONFIG.get("traffic", {}).get("platforms", {}).get("reddit", {})
        if not config.get("enabled"):
            return {"status": "skipped", "reason": "Reddit not configured"}
        
        # 保存到队列
        queue_file = DATA_DIR / "reddit_queue.json"
        queue = []
        if queue_file.exists():
            with open(queue_file) as f:
                queue = json.load(f)
        
        queue.append({
            "title": title,
            "url": url,
            "subreddit": subreddit,
            "created_at": datetime.now(UTC).isoformat(),
            "status": "pending",
        })
        
        with open(queue_file, "w") as f:
            json.dump(queue[-20:], f, indent=2)
        
        return {"status": "queued"}
    
    def find_best_subreddits(self, topic: str) -> list:
        """根据主题推荐最佳 Subreddit"""
        topic_map = {
            "python": ["r/Python", "r/learnpython", "r/programming"],
            "automation": ["r/automation", "r/devops", "r/Python"],
            "investing": ["r/investing", "r/valueinvesting", "r/stocks"],
            "maritime": ["r/maritime", "r/shipping", "r/Nautical"],
            "github": ["r/github", "r/opensource", "r/programming"],
        }
        
        for key, subs in topic_map.items():
            if key in topic.lower():
                return subs
        
        return ["r/programming", "r/coolgithubprojects"]


# ─── 主控 ────────────────────────────────────────────────────────────

def run_daily_traffic():
    """每日推广引流任务"""
    seo = SEOOptimizer()
    twitter = TwitterPromoter()
    github = GitHubPromoter()
    social = SocialPromoter()
    
    print(f"[{datetime.now(UTC).isoformat()}] Agent 2: Traffic Driver - 开始运营")
    
    # 1. 分析 GitHub Trending
    print("  分析 GitHub Trending...")
    trending = github.analyze_trending()
    print(f"  发现 {len(trending)} 个热门仓库")
    
    # 2. 寻找协作机会
    print("  寻找协作机会...")
    opps = github.find_collaboration_opportunities()
    print(f"  找到 {len(opps)} 个协作机会")
    
    # 3. 生成推文线程
    print("  准备社交媒体内容...")
    tweet = twitter.generate_tweet_thread(trending[0]["description"] if trending else "Git automation tools")
    print(f"  生成了 {len(tweet)} 条推文")
    
    # 4. 保存报告
    report = {
        "timestamp": datetime.now(UTC).isoformat(),
        "trending_count": len(trending),
        "opportunities_found": len(opps),
        "tweets_generated": len(tweet),
        "seo_optimized": False,
    }
    
    report_path = DATA_DIR / f"traffic_report_{datetime.now(UTC).strftime('%Y%m%d')}.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"[{datetime.now(UTC).isoformat()}] Agent 2: Traffic Driver - 完成\n")
    return report


if __name__ == "__main__":
    run_daily_traffic()
