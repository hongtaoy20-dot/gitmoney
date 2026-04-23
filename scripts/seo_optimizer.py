#!/usr/bin/env python3
"""
SEO 优化器 - 用于 README 和 GitHub 内容的搜索引擎优化
"""

import re
import json
from pathlib import Path

class SEOAnalyzer:
    """GitHub README SEO 分析与优化"""
    
    def __init__(self):
        self.content = ""
    
    def analyze(self, content: str) -> dict:
        """完整 SEO 分析"""
        self.content = content
        return {
            "score": self._calculate_score(),
            "word_count": self._word_count(),
            "heading_structure": self._check_headings(),
            "keyword_density": self._keyword_density(),
            "link_analysis": self._link_analysis(),
            "missing_elements": self._missing_elements(),
            "suggestions": self._suggestions(),
        }
    
    def _calculate_score(self) -> int:
        """计算 SEO 总分 (0-100)"""
        score = 0
        
        # 标题
        if re.search(r'^#\s+\S', self.content, re.MULTILINE): score += 10
        
        # 字数
        wc = self._word_count()
        if wc > 500: score += 15
        elif wc > 200: score += 10
        else: score += 5
        
        # 结构
        if "## " in self.content: score += 10
        if "- " in self.content or "* " in self.content: score += 5
        if "```" in self.content: score += 5
        if "![" in self.content: score += 5
        
        # 关键词
        kw = self._check_keywords()
        score += min(len(kw) * 5, 20)
        
        # 链接
        links = re.findall(r'\[.*?\]\(.*?\)', self.content)
        score += min(len(links) * 3, 10)
        
        # Badge
        badges = re.findall(r'!\[.*?\]\(https://img\.shields\.io', self.content)
        score += min(len(badges) * 5, 20)
        
        return min(score, 100)
    
    def _word_count(self) -> int:
        return len(self.content.split())
    
    def _check_headings(self) -> dict:
        h1 = len(re.findall(r'^#\s', self.content, re.MULTILINE))
        h2 = len(re.findall(r'^##\s', self.content, re.MULTILINE))
        h3 = len(re.findall(r'^###\s', self.content, re.MULTILINE))
        return {"h1": h1, "h2": h2, "h3": h3, "total": h1 + h2 + h3}
    
    def _keyword_density(self) -> dict:
        keywords = ["guide", "tutorial", "python", "automation", "github",
                    "how", "install", "setup", "api", "deploy", "docker",
                    "cli", "open source", "beginner", "example"]
        total_words = self._word_count()
        hits = {}
        for kw in keywords:
            count = len(re.findall(re.escape(kw), self.content, re.IGNORECASE))
            if count > 0:
                hits[kw] = count
        return {"total_keywords": sum(hits.values()), "keyword_count": len(hits), "keywords": hits}
    
    def _check_keywords(self) -> list:
        found = []
        priority_keywords = ["python", "github", "automation", "tutorial",
                            "open source", "developer tools", "cli"]
        for kw in priority_keywords:
            if kw.lower() in self.content.lower():
                found.append(kw)
        return found
    
    def _link_analysis(self) -> dict:
        links = re.findall(r'\[([^\]]+)\]\(([^\)]+)\)', self.content)
        return {"total_links": len(links), "links": links[:10]}
    
    def _missing_elements(self) -> list:
        missing = []
        if not re.search(r'^#\s+\S', self.content, re.MULTILINE):
            missing.append("H1 标题")
        if "description" not in self.content.lower() and "about" not in self.content.lower():
            missing.append("项目描述段")
        if "## " not in self.content:
            missing.append("H2 子标题")
        if "![" not in self.content:
            missing.append("图片/Badge")
        if len(re.findall(r'\[.*?\]\(.*?\)', self.content)) < 2:
            missing.append("外部链接")
        return missing
    
    def _suggestions(self) -> list:
        suggestions = []
        score = self._calculate_score()
        if score < 30:
            suggestions.append("添加 H1 标题和项目描述")
            suggestions.append("扩展内容至 500 字以上")
        if score < 50:
            suggestions.append("添加 Badge (CI/CD, Python 版本, License)")
            suggestions.append("增加 H2 子标题以改善结构")
        if score < 70:
            suggestions.append("添加"快速开始"章节")
            suggestions.append("在 README 开头自然嵌入主要关键词")
        return suggestions
    
    def optimize_readme(self, original: str, keywords: list) -> str:
        """自动优化 README (添加 meta 等)"""
        optimized = original
        
        # 在顶部添加 Badge 行 (如果没有)
        badges_match = re.search(r'!\[.*?\]\(https://img\.shields\.io', original)
        if not badges_match:
            badge_line = f"[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)\n"
            badge_line += f"[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)\n"
            badge_line += f"[![GitHub Stars](https://img.shields.io/github/stars/YOUR-REPO)](https://github.com/YOUR-REPO)\n\n"
            optimized = badge_line + optimized
        
        return optimized


def main():
    analyzer = SEOAnalyzer()
    
    # 测试用例
    test_content = """# My Project
    
This is a Python automation tool.

## Features
- Feature 1
- Feature 2

## Installation
```bash
pip install my-project
```
"""
    
    result = analyzer.analyze(test_content)
    print(f"SEO Score: {result['score']}/100")
    print(f"Word Count: {result['word_count']}")
    print(f"Missing: {', '.join(result['missing_elements'])}")
    print(f"Suggestions:")
    for s in result['suggestions']:
        print(f"  - {s}")


if __name__ == "__main__":
    main()
