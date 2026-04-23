#!/usr/bin/env python3
"""
GitMoney Agent 1: Content Creator (V2 - Captain Edition)
=========================================================
自动创作内容, 专攻以下变现驱动领域:
1. 邮轮运营与管理 (Cruise Ops) — 吸引船务公司/审核客户
2. 海事合规与安全 (Maritime Compliance) — 展示 Auditor 专业性
3. 邮轮文化/生活方式 (Cruise Culture) — 引流自媒体粉丝
4. 美股价值投资 (US Value Investing) — 吸引投资学习用户
5. 开源自动化工具 (Open Source Tools) — 展示技术能力

每日产出: 1 篇主文章 (发布为 Issue) + 1 条社交内容草稿
"""

import os, sys, json, yaml, time, random, requests
from datetime import UTC, datetime, timedelta
from pathlib import Path

# ─── 配置 ─────────────────────────────────────────────────────────────────
CONFIG_PATH = Path(__file__).parent.parent / "config" / "settings.yaml"
DATA_DIR = Path(__file__).parent.parent / "data" / "content"
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
CREATE_CONFIG = CONFIG.get("creator_v2", {})

# ─── 变现驱动内容模板库 ───────────────────────────────────────────────────
# 每个模板直接对应 1 个变现管道
MONETIZED_TOPICS = [
    # ── 邮轮运营 (引流 → 咨询/审核) ──
    {
        "id": "cruise_turnaround_logistics",
        "title": "The Logistics of Turnaround Day: How a Cruise Ship Re-Provisions 5000 Passengers in 8 Hours",
        "channel": "cruise_consulting",
        "tags": ["maritime", "cruise", "logistics", "operations"],
        "seo_keywords": ["cruise turnaround", "ship provisioning", "cruise operations"],
        "read_time": 8,
        "cta_type": "consulting",  # 文末 CTA: 指向咨询服务
    },
    {
        "id": "emergency_drills",
        "title": "Inside a Cruise Ship Emergency Drill: What Passengers Never See",
        "channel": "cruise_content",
        "tags": ["cruise", "safety", "behind-the-scenes", "maritime"],
        "seo_keywords": ["cruise ship safety", "emergency drill", "maritime safety"],
        "read_time": 7,
        "cta_type": "content",
    },
    {
        "id": "career_chief_officer",
        "title": "From Cadet to Chief Officer: 15 Years of Lessons on the Bridge",
        "channel": "cruise_content",
        "tags": ["career", "maritime", "cruise", "mentorship"],
        "seo_keywords": ["chief officer career", "maritime career", "cruise ship jobs"],
        "read_time": 10,
        "cta_type": "content",
    },
    # ── ISM/ISPS/MLC 审核 (直接促转化) ──
    {
        "id": "audit_preparation_ism",
        "title": "ISM Audit Survival Guide: 10 Things Every Ship Manager Needs to Know",
        "channel": "maritime_auditor",
        "tags": ["ISM", "audit", "maritime", "compliance", "safety"],
        "seo_keywords": ["ISM audit", "ship management", "maritime compliance"],
        "read_time": 12,
        "cta_type": "audit",
    },
    {
        "id": "mlc_compliance_2026",
        "title": "MLC 2006 Compliance Checklist: What Changed in 2026",
        "channel": "maritime_auditor",
        "tags": ["MLC", "maritime", "crew", "compliance", "regulations"],
        "seo_keywords": ["MLC compliance", "maritime labor", "crew welfare"],
        "read_time": 9,
        "cta_type": "audit",
    },
    # ── 美股价值投资 (吸引付费订阅) ──
    {
        "id": "value_screener_python",
        "title": "Build Your Own Value Stock Screener in Python (PE<15, PB<2, RSI<30)",
        "channel": "us_stocks",
        "tags": ["investing", "python", "value", "quantitative"],
        "seo_keywords": ["value investing", "python stock screener", "oversold stocks"],
        "read_time": 15,
        "cta_type": "stock",
    },
    {
        "id": "rsi_vs_traps",
        "title": "Why Your RSI<30 Strategy Is Trapping You (And How to Fix It)",
        "channel": "us_stocks",
        "tags": ["investing", "trading", "strategy", "analysis"],
        "seo_keywords": ["RSI strategy", "value trap", "stock analysis"],
        "read_time": 10,
        "cta_type": "stock",
    },
    {
        "id": "maritime_dividend_stocks",
        "title": "The Hidden Opportunity: Maritime & Logistics Dividend Stocks in 2026",
        "channel": "us_stocks",
        "tags": ["investing", "maritime", "dividends", "stocks"],
        "seo_keywords": ["maritime stocks", "shipping stocks", "dividend investing"],
        "read_time": 8,
        "cta_type": "stock",
    },
    # ── 开源工具 (吸引 GitHub Star → 变现漏斗) ──
    {
        "id": "cruise_checklist_automation",
        "title": "Automating Cruise Ship Operational Checklists with Python + GitHub Actions",
        "channel": "cruise_tools",
        "tags": ["python", "automation", "maritime", "github"],
        "seo_keywords": ["maritime automation", "cruise tech", "python checklists"],
        "read_time": 11,
        "cta_type": "tools",
    },
    {
        "id": "value_investing_bot",
        "title": "I Built a Telegram Bot That Texts Me Oversold Stocks Daily — Here's the Code",
        "channel": "cruise_tools",
        "tags": ["python", "investing", "bot", "telegram", "automation"],
        "seo_keywords": ["stock bot", "telegram trading", "python automation"],
        "read_time": 10,
        "cta_type": "tools",
    },
]

# ─── CTA 文案库 ────────────────────────────────────────────────────────────
CTA_TEMPLATES = {
    "consulting": (
        "\n\n---\n"
        "*About the Author:* I'm a Chief Officer on Viking Cruises with 15 years of experience "
        "in cruise operations, maritime compliance, and ship management. I offer **cruise operations "
        "consulting** for fleet managers and cruise lines.\n\n"
        "💬 Interested in an operational audit or compliance review? "
        "DM me on [LinkedIn](https://linkedin.com/in/{username}) or open an issue in this repo."
    ),
    "audit": (
        "\n\n---\n"
        "*About the Author:* Certified **ISM/ISPS/MLC Auditor** with 15 years at sea. "
        "I help cruise lines and ship management companies prepare for audits, "
        "review documentation, and train crews.\n\n"
        "📋 Need pre-audit support or compliance training? "
        "Open an issue or reach out via [GitHub Discussions](https://github.com/{user}/{repo}/discussions)."
    ),
    "stock": (
        "\n\n---\n"
        "*About the Author:* Chief Officer by day, value investor by night. "
        "I run a **weekly value stock watchlist** with PE<15, PB<2, RSI<30 filters. "
        "3-year track record targeting 30% annual returns.\n\n"
        "📈 Get the weekly watchlist: [GitHub Sponsors](https://github.com/sponsors/{user}) ($20/mo)\n"
        "🐍 Python screener code available in this repo."
    ),
    "content": (
        "\n\n---\n"
        "Enjoyed this? I share daily stories from the bridge of Viking Cruises.\n\n"
        "🔗 Follow me on [LinkedIn](https://linkedin.com/in/{username}) for more behind-the-scenes maritime content.\n"
        "⭐ Star this repo to support open-source maritime automation tools."
    ),
    "tools": (
        "\n\n---\n"
        "*Built for the maritime community by a fellow seafarer.*\n\n"
        "🔧 All tools are open-source. Star the repo and check `/tools` for downloads.\n"
        "💡 Need a custom tool? Premium templates available via GitHub Sponsors."
    ),
}


# ─── 内容生成器 V2 ─────────────────────────────────────────────────────
class ContentGeneratorV2:
    """V2 内容生成器 — 变现驱动选题 + 专业化 CTA"""

    def __init__(self):
        # Try OpenRouter first, then DeepSeek, then SiliconFlow as fallbacks
        configs = [
            ("openrouter", "https://openrouter.ai/api/v1/chat/completions",
             os.environ.get("OPENROUTER_API_KEY", ""), "deepseek/deepseek-chat"),
            ("deepseek", "https://api.deepseek.com/v1/chat/completions",
             os.environ.get("DEEPSEEK_API_KEY", ""), "deepseek-chat"),
            ("siliconflow", "https://api.siliconflow.cn/v1/chat/completions",
             os.environ.get("SILICONFLOW_API_KEY", ""), "Qwen/Qwen2.5-32B-Instruct"),
        ]
        self.api_base = ""
        self.api_key = ""
        self.model = ""
        for name, base, key, model in configs:
            if key:
                self.api_base = base
                self.api_key = key
                self.model = model
                self._provider_name = name
                break
        if not self.api_key:
            self._provider_name = "fallback"

    def _call_llm(self, prompt: str, system: str = "") -> str:
        if not self.api_key:
            return self._fallback_content(prompt, system)
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            data = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system or "你是 GitMoney 内容创作 Agent，专精海事和投资领域。请用中文输出专业、高质量的内容。"},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.7,
                "max_tokens": 2500,
            }
            resp = requests.post(self.api_base, headers=headers, json=data, timeout=60)
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
        except Exception:
            pass
        return self._fallback_content(prompt, system)

    def _fallback_content(self, prompt: str, system: str = "") -> str:
        """无 API 时的降级内容生成"""
        return f"""# {system.split(',')[0] if system else 'Content'}

## Practical Insights from 15 Years at Sea

After spending 15 years in the maritime industry—from cadet to Chief Officer on Viking Cruises—I've accumulated insights that go beyond textbooks and regulations.

This article shares real experiences from the bridge, covering:

1. **What actually works** in day-to-day ship operations
2. **Common pitfalls** that even experienced officers miss
3. **Practical frameworks** you can apply on your vessel

### Key Takeaway
The maritime industry is changing fast. Automation, new regulations, and shifting crew demographics mean that what worked 5 years ago may not work today.

Stay adaptable. Stay safe. Keep learning.

*Generated by GitMoney Content Agent V2 | Template mode*
"""

    def generate_article(self, topic: dict) -> dict:
        """生成一篇变现驱动文章"""
        # 构建 CTA
        username = GITHUB_USER or "your-username"
        repo = "gitmoney"
        cta_key = topic.get("cta_type", "content")
        cta = CTA_TEMPLATES.get(cta_key, "").format(username=username, user=GITHUB_USER, repo=repo)

        prompt = f"""请撰写一篇高质量专业文章，主题: {topic['title']}

文章定位: 这是一篇【{topic.get('channel', 'general')}】领域的引流内容，
目标读者: 海事专业人士、船务公司管理者或价值投资者
字数: 800-1500 字

要求:
- 中文或英文均可，根据内容自然选择
- 自然融入 SEO 关键词: {', '.join(topic.get('seo_keywords', []))}
- 第一人称视角（一个 15 年经验的 Chief Officer）
- 包含真实感强的细节（数据、流程、经验）
- 不是 AI 味文章，是"一个海事专业人士的分享"
- 包含引言、3 个小节、结语
- 文末留出位置给 CTA（我会添加）

文章标题: {topic['title']}"""

        system_prompt = f"""你是一位有 15 年经验的海事专业人士（Viking Cruises Chief Officer/Master Mariner）。
你擅长结合行业经验撰写专业内容，带有真诚、不浮夸的风格。

专业领域:
- 邮轮运营与管理
- ISM/ISPS/MLC 合规审核
- 船舶安全与船员管理
- 美股价值投资（量化筛选策略）

写作特点:
- 专业但不学术
- 用真实经验说话
- 对业内人士有价值
- 偶尔带一点自嘲式的幽默

标签: {', '.join(topic.get('tags', []))}"""

        content = self._call_llm(prompt, system_prompt)
        full_content = content + cta

        article = {
            "id": topic["id"],
            "title": topic["title"],
            "content": full_content,
            "tags": topic["tags"],
            "keywords": topic["seo_keywords"],
            "channel": topic.get("channel", "general"),
            "cta_type": topic.get("cta_type", "content"),
            "read_time": topic.get("read_time", 8),
            "word_count": len(full_content.split()),
            "created_at": datetime.now(UTC).isoformat(),
            "source": "llm" if self.api_key else "template",
        }

        self._save_article(article)
        return article

    def _save_article(self, article: dict):
        """保存文章到本地"""
        safe_name = article["id"]
        file_path = DATA_DIR / f"{safe_name}.json"
        history = []
        if file_path.exists():
            with open(file_path) as f:
                history = json.load(f) if isinstance(json.load(f), list) else [json.load(f)]
        history.append(article)
        with open(file_path, "w") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)

    def create_github_issue(self, repo: str, title: str, body: str, labels: list = None) -> dict:
        """发布到 GitHub Issue"""
        url = f"https://api.github.com/repos/{GITHUB_USER}/{repo}/issues"
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json",
        }
        data = {"title": title, "body": body, "labels": labels or ["content"]}
        try:
            resp = requests.post(url, headers=headers, json=data)
            if resp.status_code == 201:
                return resp.json()
            return {"error": resp.status_code, "message": resp.text[:200]}
        except Exception as e:
            return {"error": str(e)}

    def select_best_topic(self) -> dict:
        """选题轮询 — 按管道顺序轮流，确保每个变现管道都有内容产出"""
        recent_file = DATA_DIR / "recent_topics.json"
        recent = []
        if recent_file.exists():
            with open(recent_file) as f:
                recent = json.load(f)

        recent_ids = [r.get("id", r) if isinstance(r, dict) else r for r in recent[-5:]]
        available = [t for t in MONETIZED_TOPICS if t["id"] not in recent_ids]
        if not available:
            available = MONETIZED_TOPICS

        chosen = random.choice(available)
        recent.append(chosen["id"])
        if len(recent) > len(MONETIZED_TOPICS):
            recent = recent[-len(MONETIZED_TOPICS):]
        with open(recent_file, "w") as f:
            json.dump(recent, f, indent=2)

        return chosen


# ─── 每日执行 ──────────────────────────────────────────────────────────
def run_daily_creation():
    gen = ContentGeneratorV2()

    print(f"[{datetime.now(UTC).isoformat()}] Agent 1: Content Creator V2 - 开始每日创作")

    # 1. 变现驱动选题
    topic = gen.select_best_topic()
    channel = topic.get("channel", "general")
    cta = topic.get("cta_type", "content")
    print(f"  选题: {topic['id']}")
    print(f"  管道: {channel} | CTA: {cta}")

    # 2. 生成文章
    article = gen.generate_article(topic)
    print(f"  文章已生成: {article['title'][:60]}... ({article['word_count']} 词)")

    # 3. 发布到 GitHub
    labels = ["content", "auto-generated", channel]
    result = gen.create_github_issue(
        repo=CONFIG.get("github", {}).get("primary_repo", "gitmoney"),
        title=article["title"],
        body=article["content"],
        labels=labels,
    )

    if "error" not in result:
        print(f"  发布: Issue #{result.get('number', '?')}")
    else:
        print(f"  发布状态: {result.get('message', 'unknown')}")

    print(f"[{datetime.now(UTC).isoformat()}] Agent 1: Content Creator V2 - 完成\n")
    return {"topic": topic, "article": article, "issue": result}


if __name__ == "__main__":
    run_daily_creation()
