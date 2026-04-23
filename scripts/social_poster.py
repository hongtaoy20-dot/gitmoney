#!/usr/bin/env python3
"""
社交媒体自动发布脚本 - 配合 Twitter/LinkedIn/Reddit API
"""

import json
import os
import requests
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data" / "analytics"


class SocialPoster:
    """社交媒体推文管理"""
    
    def __init__(self):
        self.queue_file = DATA_DIR / "social_queue.json"
        self.history_file = DATA_DIR / "post_history.json"
    
    def add_to_queue(self, platform: str, content: str, url: str = ""):
        """添加到发布队列"""
        queue = []
        if self.queue_file.exists():
            with open(self.queue_file) as f:
                queue = json.load(f)
        
        queue.append({
            "platform": platform,
            "content": content,
            "url": url,
            "created_at": datetime.utcnow().isoformat(),
            "status": "pending",
        })
        
        with open(self.queue_file, "w") as f:
            json.dump(queue[-100:], f, indent=2)  # 最多 100 条
    
    def get_pending_posts(self) -> list:
        """获取待发布内容"""
        if not self.queue_file.exists():
            return []
        with open(self.queue_file) as f:
            queue = json.load(f)
        return [p for p in queue if p["status"] == "pending"]
    
    def mark_posted(self, post_id: int):
        """标记为已发布"""
        if not self.queue_file.exists():
            return
        with open(self.queue_file) as f:
            queue = json.load(f)
        
        if post_id < len(queue):
            queue[post_id]["status"] = "posted"
            queue[post_id]["posted_at"] = datetime.utcnow().isoformat()
        
        with open(self.queue_file, "w") as f:
            json.dump(queue, f, indent=2)


if __name__ == "__main__":
    poster = SocialPoster()
    pending = poster.get_pending_posts()
    print(f"待发布: {len(pending)} 条")
    for p in pending[:5]:
        print(f"  [{p['platform']}] {p['content'][:60]}...")
