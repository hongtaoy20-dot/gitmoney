#!/usr/bin/env python3
"""
GitMoney Release Packager - 打包海事运营工具模板并发布到 GitHub Releases
"""
import os, sys, json, yaml, subprocess, tempfile, zipfile
from pathlib import Path
from datetime import datetime, UTC

BASE_DIR = Path(__file__).resolve().parent.parent
RELEASES_DIR = BASE_DIR / "releases"
DATA_DIR = BASE_DIR / "data" / "analytics"

# Tool packages
TOOLS = {
    "cruise_checklist_pack_v1": {
        "name": "邮轮运营检查表模板包 v1.0",
        "description": "3 份专业邮轮运营检查表 (Excel格式)\n- 日常运营检查表\n- 安全审计清单\n- 船员交接事项清单",
        "files": [],
        "price": "$10",
    },
    "ship_ops_python_tools": {
        "name": "船舶运营 Python 工具集 v1.0",
        "description": "5 个船舶运营自动化的 Python 脚本\n- 航程数据自动分析\n- 合规日期计算器\n- 船员排班生成器\n- 燃油消耗追踪\n- 安全检查报告生成",
        "files": [],
        "price": "$20",
    },
    "value_investing_spreadsheet": {
        "name": "美股价值投资筛选表格 v1.0",
        "description": "专业价值投资 Excel 模板\n- 自动评分系统\n- PE/PB/ROE/RSI 多维度筛选\n- 组合跟踪\n- 回撤分析",
        "files": [],
        "price": "$15",
    },
}

def build_release():
    """Build release packages"""
    print(f"[{datetime.now(UTC).isoformat()}] Build Release - 开始\n")

    os.makedirs(RELEASES_DIR, exist_ok=True)

    for tool_id, tool in TOOLS.items():
        # Create temp dir for this package
        pkg_dir = RELEASES_DIR / tool_id
        os.makedirs(pkg_dir, exist_ok=True)

        # Write README
        readme = f"""# {tool['name']}

{tool['description']}

## 购买方式
- Gumroad: https://zhsj1221.gumroad.com/l/{tool_id}
- GitHub Sponsors (Captain Tier): 包含在 $20/mo 赞助中
- 直接联系: zsj1221@126.com

## 技术支持
- 邮件: zsj1221@126.com
- GitHub Issues: 本仓库 Issues

---

*GitMoney - {datetime.now(UTC).strftime('%Y-%m-%d')}*
"""
        (pkg_dir / "README.md").write_text(readme)

        # Write metadata
        meta = {
            "id": tool_id,
            "name": tool["name"],
            "version": "1.0.0",
            "price_usd": tool["price"],
            "created": datetime.now(UTC).isoformat(),
            "author": "Captain (Viking Cruises Chief Officer)",
        }
        (pkg_dir / "metadata.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2))

        # Zip it
        zip_path = RELEASES_DIR / f"{tool_id}.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in pkg_dir.iterdir():
                zf.write(f, arcname=f.name)

        print(f"  ✅ {tool['name']}: {zip_path} ({zip_path.stat().st_size} bytes)")

    print(f"\n✅ Build complete: {len(TOOLS)} tools")
    return True

def gumroad_products_json():
    """Generate Gumroad product JSON (for reference)"""
    products = []
    for tool_id, tool in TOOLS.items():
        products.append({
            "name": tool["name"],
            "description": tool["description"].replace("\n", " "),
            "price": tool["price"],
            "url": f"https://zhsj1221.gumroad.com/l/{tool_id}",
        })
    out = RELEASES_DIR / "gumroad_products.json"
    with open(out, "w") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    print(f"  Gumroad product list: {out}")

if __name__ == "__main__":
    build_release()
    gumroad_products_json()
