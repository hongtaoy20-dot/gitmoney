# GitMoney - 多 Agent 自动化变现系统

一个全自动化的 GitHub 开源赚钱项目。利用 3 个 AI Agent 协作完成从内容创作到流量变现的完整闭环。

## 架构

```
GitMoney/
├── agents/
│   ├── agent_creator.py      # Agent 1: 自动创作内容 (文章/代码/模板/视频脚本)
│   ├── agent_traffic.py      # Agent 2: 推广引流 (SEO/社交媒体/Issue营销/PR)
│   └── agent_monetizer.py    # Agent 3: 变现转化 (数据分析/付费转化/Sponsors)
├── orchestrator.py           # 主控调度 - 协调三个Agent
├── scripts/
│   ├── seo_optimizer.py      # SEO优化工具
│   ├── social_poster.py      # 社交媒体自动发帖
│   └── analytics.py          # 数据分析工具
├── workflows/
│   ├── daily.yml             # 每日任务
│   └── weekly.yml            # 每周复盘
├── config/
│   ├── settings.yaml         # 全局配置
│   └── strategies.yaml       # 变现策略配置
├── data/                     # 数据存储
│   ├── content/              # 已发布内容记录
│   ├── analytics/            # 流量/收益数据
│   └── leads/                # 潜在客户/合作线索
└── docs/                     # 文档
```

## 变现模式

| 模式 | 说明 | 自动化程度 |
|------|------|-----------|
| GitHub Sponsors | 开源项目赞助 | 低 (需人设积累) |
| 付费内容 | 技术文章/模板/电子书 | 高 (Agent 自动创作) |
| 咨询引流 | 通过内容吸引客户 → 付费咨询 | 中 |
| 广告/联盟 | README 广告位 / Affiliate链接 | 高 |
| 数据产品 | 聚合数据/行业报告 | 高 |
| 知识星球/社群 | 付费社群引流 | 中 |

## 快速启动

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置
cp config/settings.yaml.example config/settings.yaml
# 编辑 settings.yaml 填入 API Key 等配置

# 3. 启动每日任务
python orchestrator.py --mode daily

# 4. 启动完整流程
python orchestrator.py --mode full
```

## 子 Agent 职责

### Agent 1: Content Creator
- 自动生成高质量技术文章、开源项目、代码模板
- 支持多种内容类型: README、Issue、PR、博客、Gist
- 自动注入 SEO 关键词优化

### Agent 2: Traffic Driver
- SEO 优化 (关键词研究、内链建设、meta优化)
- 社交媒体自动推广 (Twitter/X, LinkedIn, Reddit, Hacker News)
- GitHub 生态推广 (Issue 参与、PR 贡献、Star 互推)

### Agent 3: Monetizer
- 流量数据分析与变现机会识别
- 自动生成变现文案 (Sponsors 页、付费内容)
- 客户线索挖掘与跟进
- A/B 测试广告位效果

---

> ⚠️ 注意: 本项目为自动化辅助工具，请遵守各平台的 ToS 和社区规范。
