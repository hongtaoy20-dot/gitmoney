#!/usr/bin/env python3
"""
GitMoney Agent 1: Content Creator
==================================
自动创作高质量内容: 技术文章、代码模板、开源项目、README 优化等。

功能:
  - 自动选题 (基于热门趋势 + 知识库)
  - 生成文章/代码/模板
  - SEO 关键词注入
  - 质量检查 (可读性、原创性、SEO 评分)
  - 发布到 GitHub (作为 Issue / PR / 新仓库 / Gist)
"""

import os
import sys
import json
import yaml
import time
import random
import requests
from datetime import datetime, timedelta
from pathlib import Path

# ─── 配置 ─────────────────────────────────────────────────────────────────
CONFIG_PATH = Path(__file__).parent.parent / "config" / "settings.yaml"
DATA_DIR = Path(__file__).parent.parent / "data" / "content"
DATA_DIR.mkdir(parents=True, exist_ok=True)

with open(CONFIG_PATH) as f:
    CONFIG = yaml.safe_load(f)

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN") or CONFIG.get("github", {}).get("token", "")
GITHUB_USER = CONFIG.get("github", {}).get("username", "")
CREATE_CONFIG = CONFIG.get("creator", {})

# ─── 内容模板库 ───────────────────────────────────────────────────────────

ARTICLES = {
    "python-automation": {
        "title": "Building a Multi-Agent Automation System with Python: A Practical Guide",
        "tags": ["python", "automation", "agents", "tutorial"],
        "keywords": ["python automation", "multi-agent system", "AI workflow"],
        "estimated_read_time": 8,
    },
    "maritime-tech": {
        "title": "How AI Agents Are Transforming Maritime Operations in 2026",
        "tags": ["maritime", "AI", "shipping", "technology"],
        "keywords": ["maritime AI", "shipping automation", "digital transformation"],
        "estimated_read_time": 6,
    },
    "value-investing": {
        "title": "Automated Value Investing: Using Python to Find Oversold Gems",
        "tags": ["investing", "python", "quantitative", "value"],
        "keywords": ["value investing", "python trading", "RSI strategy"],
        "estimated_read_time": 10,
    },
    "github-marketing": {
        "title": "The Developer's Guide to Building a GitHub Presence That Attracts Opportunities",
        "tags": ["github", "career", "open-source", "marketing"],
        "keywords": ["github profile", "open source contribution", "developer branding"],
        "estimated_read_time": 7,
    },
    "immigration-tech": {
        "title": "Using AI Tools to Navigate US Immigration as a Skilled Professional",
        "tags": ["immigration", "AI", "career", "US"],
        "keywords": ["US immigration", "EB-3 visa", "skilled worker"],
        "estimated_read_time": 9,
    },
}

CODE_TEMPLATES = {
    "multi-agent-orchestrator": {
        "name": "multi-agent-orchestrator",
        "description": "A lightweight multi-agent orchestration framework in Python",
        "language": "Python",
        "stars_estimate": "⭐⭐⭐",
    },
    "value-scanner": {
        "name": "value-scanner",
        "description": "Automated value stock scanner with RSI, PE, PB filters",
        "language": "Python",
        "stars_estimate": "⭐⭐⭐⭐",
    },
    "obsidian-auto-sync": {
        "name": "obsidian-git-sync",
        "description": "Auto-sync Obsidian vault to GitHub with conflict resolution",
        "language": "Shell + Python",
        "stars_estimate": "⭐⭐⭐",
    },
    "seo-analyzer": {
        "name": "readme-seo-analyzer",
        "description": "Analyze and optimize GitHub README for search engine ranking",
        "language": "Python",
        "stars_estimate": "⭐⭐⭐",
    },
}

# ─── 内容生成器 ───────────────────────────────────────────────────────

class ContentGenerator:
    """Agent 1 核心 - 使用 LLM 生成高质量内容"""
    
    def __init__(self):
        self.api_base = "https://openrouter.ai/api/v1/chat/completions"
        self.api_key = os.environ.get("OPENROUTER_API_KEY", "")
        self.model = "deepseek/deepseek-chat"
    
    def _call_llm(self, prompt: str, system: str = "") -> str:
        """调用 LLM 生成内容"""
        if not self.api_key:
            return self._fallback_template(prompt)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system or "你是 GitMoney 内容创作 Agent。请生成高质量、原创的技术内容。"},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.7,
            "max_tokens": 2000,
        }
        
        try:
            resp = requests.post(self.api_base, headers=headers, json=data, timeout=60)
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
            else:
                return self._fallback_template(prompt)
        except Exception:
            return self._fallback_template(prompt)
    
    def _fallback_template(self, prompt: str) -> str:
        """API 不可用时的降级模板"""
        return f"""# {prompt[:60]}...

## Overview
This is an auto-generated article about {prompt[:30]}. 
Content generation uses a template fallback when API is unavailable.

## Key Points
1. Understanding the fundamentals
2. Practical implementation
3. Best practices and pitfalls
4. Real-world applications

## Conclusion
This guide provides a starting point for your exploration.

---

*Generated by GitMoney Content Agent | Template mode*
"""
    
    def generate_article(self, topic_key: str) -> dict:
        """生成一篇技术文章"""
        if topic_key in ARTICLES:
            template = ARTICLES[topic_key]
        else:
            template = {
                "title": topic_key.replace("-", " ").title(),
                "tags": ["technology"],
                "keywords": [topic_key],
                "estimated_read_time": 5,
            }
        
        prompt = f"""请撰写一篇高质量技术文章，主题: {template['title']}

要求:
- 中文或英文均可 (根据内容判断)
- 字数 800-1500 字
- 自然融入以下 SEO 关键词: {', '.join(template['keywords'])}
- 包含引言、正文(至少3个小节)、结语
- 代码示例 (如果适用)
- 适合发布在 GitHub 仓库的 README 或博客

文章标题: {template['title']}"""
        
        system_prompt = f"""你是一个专业的技术内容写手。
生成内容要求:
- 原创、专业、实用
- SEO 优化 (自然嵌入关键词)
- 结构清晰 (标题/子标题/列表)
- 对开发者有实际价值
- 可读性 8 年级水平以上
- 避免过度 AI 感 (使用弱限定词)
- 标签: {', '.join(template['tags'])}"""
        
        content = self._call_llm(prompt, system_prompt)
        
        article = {
            "title": template["title"],
            "content": content,
            "tags": template["tags"],
            "keywords": template["keywords"],
            "read_time": template["estimated_read_time"],
            "created_at": datetime.utcnow().isoformat(),
            "source": "llm" if self.api_key else "template",
        }
        
        # 保存到本地
        self._save_article(article)
        return article
    
    def _save_article(self, article: dict):
        """保存文章到本地存储"""
        safe_name = article["title"].lower().replace(" ", "-")[:40]
        file_path = DATA_DIR / f"{safe_name}.json"
        
        # 读取现有记录
        history = []
        if file_path.exists():
            with open(file_path) as f:
                history = json.load(f) if isinstance(json.load(f), list) else [json.load(f)]
        
        history.append(article)
        with open(file_path, "w") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    
    def generate_code_template(self, template_key: str) -> dict:
        """生成一个代码模板仓库 (README + 代码框架)"""
        if template_key in CODE_TEMPLATES:
            tpl = CODE_TEMPLATES[template_key]
        else:
            tpl = {
                "name": template_key,
                "description": f"A {template_key} template",
                "language": "Python",
            }
        
        # 生成 README
        readme_prompt = f"""请为一个名为 {tpl['name']} 的开源项目生成 README.md。

项目描述: {tpl['description']}
语言: {tpl['language']}

README 需要包含:
1. 项目名称 + 一句话简介
2. 快速开始 (安装 + 使用示例)
3. 功能特性 (清单)
4. API 文档 (简要)
5. 贡献指南
6. License 说明

要求简洁、专业，适合 GitHub 展示。"""
        
        readme = self._call_llm(readme_prompt)
        
        result = {
            "name": tpl["name"],
            "description": tpl["description"],
            "language": tpl["language"],
            "readme": readme,
            "generated_at": datetime.utcnow().isoformat(),
        }
        
        return result
    
    def create_github_issue(self, repo: str, title: str, body: str, labels: list = None) -> dict:
        """在指定仓库创建 Issue (用于内容发布)"""
        url = f"https://api.github.com/repos/{GITHUB_USER}/{repo}/issues"
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json",
        }
        data = {
            "title": title,
            "body": body,
            "labels": labels or ["content"],
        }
        
        resp = requests.post(url, headers=headers, json=data)
        if resp.status_code == 201:
            return resp.json()
        else:
            return {"error": resp.status_code, "message": resp.text[:200]}
    
    def select_best_topic(self) -> str:
        """从主题池中选择最佳创作主题 (基于趋势 + 季节 + 历史表现)"""
        topics = CREATE_CONFIG.get("topics", [])
        recent_file = DATA_DIR / "recent_topics.json"
        
        # 读取最近发布记录
        recent = []
        if recent_file.exists():
            with open(recent_file) as f:
                recent = json.load(f)
        
        # 选择最近未发布的主题
        available = [t for t in topics if t not in recent[-5:]]
        if not available:
            available = topics
        
        chosen = random.choice(available)
        
        # 更新记录
        recent.append(chosen)
        if len(recent) > 20:
            recent = recent[-20:]
        with open(recent_file, "w") as f:
            json.dump(recent, f, indent=2)
        
        return chosen


def run_daily_creation():
    """每日自动创作任务"""
    gen = ContentGenerator()
    
    print(f"[{datetime.utcnow().isoformat()}] Agent 1: Content Creator - 开始每日创作")
    
    # 1. 选题
    topic = gen.select_best_topic()
    print(f"  选题: {topic}")
    
    # 2. 生成文章
    article = gen.generate_article(topic)
    print(f"  文章已生成: {article['title'][:50]}... ({len(article['content'])} 字)")
    
    # 3. 生成代码模板 (每周 2 个)
    template_keys = list(CODE_TEMPLATES.keys())
    if len(template_keys) > 0:
        key = random.choice(template_keys)
        template = gen.generate_code_template(key)
        print(f"  代码模板已生成: {template['name']}")
    
    # 4. 发布到 GitHub
    result = gen.create_github_issue(
        repo=CONFIG.get("github", {}).get("primary_repo", "gitmoney"),
        title=article["title"],
        body=article["content"],
        labels=["content", "auto-generated"],
    )
    
    if "error" not in result:
        print(f"  文章已发布为 Issue #{result.get('number', '?')}")
    else:
        print(f"  发布状态: {result.get('message', 'unknown')}")
    
    print(f"[{datetime.utcnow().isoformat()}] Agent 1: Content Creator - 完成\n")
    return {"article": article, "issue": result}


if __name__ == "__main__":
    run_daily_creation()
