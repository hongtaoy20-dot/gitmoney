#!/usr/bin/env python3
"""
GitMoney 美股超跌价值股 Watchlist 生成器 (Captain Tier 权益)
每周执行 → 筛选 PE<15, PB<2, ROE>10%, 股息>2%, RSI<45
使用 yfinance 作为主要数据源（免费、无限流）
"""
import os, sys, json, time
from datetime import datetime, UTC
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "watchlist"
DATA_DIR.mkdir(parents=True, exist_ok=True)

CORE_STOCKS = [
    "BAC", "INTC", "CSCO", "CVX", "XOM", "VZ", "T", "PFE",
    "MRK", "JPM", "WFC", "C", "GM", "F", "IBM", "HPQ",
    "DOW", "DD", "KO", "PEP", "WMT", "TGT",
    "MSFT", "AAPL", "GOOGL", "AMZN", "JNJ", "UNH", "HD", "DIS",
    "NEE", "SO", "DUK", "O", "SPG", "PLD",
]

def score_stock_yfinance(symbol: str) -> dict:
    """Fetch and score stock using yfinance"""
    try:
        import yfinance as yf
        stock = yf.Ticker(symbol)
        info = stock.info
        
        current_price = info.get("currentPrice") or info.get("previousClose") or 0
        pe = info.get("trailingPE") or info.get("forwardPE") or None
        pb = info.get("priceToBook") or None
        roe = info.get("returnOnEquity") or None
        if roe:
            roe = roe * 100  # convert to %
        div_yield = info.get("dividendYield") or None
        # yfinance dividendYield is already percentage (e.g. 2.11 = 2.11%)
        # Cap at 15% to filter out speculative stocks
        if div_yield and div_yield > 15:
            div_yield = None
        
        name = info.get("longName") or info.get("shortName") or symbol
        sector = info.get("sector", "")
        
        # RSI from yfinance (historical data)
        rsi = 50.0
        try:
            hist = stock.history(period="1mo")
            if len(hist) >= 15:
                closes = hist["Close"].values
                gains, losses = [], []
                for i in range(1, len(closes)):
                    diff = closes[i] - closes[i-1]
                    if diff >= 0: gains.append(diff); losses.append(0)
                    else: gains.append(0); losses.append(abs(diff))
                avg_gain_14 = sum(gains[-14:]) / 14 if len(gains) >= 14 else sum(gains) / len(gains)
                avg_loss_14 = sum(losses[-14:]) / 14 if len(losses) >= 14 else sum(losses) / len(losses)
                if avg_loss_14 == 0:
                    rsi = 100
                else:
                    rs = avg_gain_14 / avg_loss_14
                    rsi = 100 - (100 / (1 + rs))
        except:
            pass
        
        # Score (max 10)
        score = 0
        items = []
        if pe and 0 < pe < 15: score += 2; items.append("PE=✅")
        elif pe and 0 < pe < 20: score += 1; items.append("PE=⚠️")
        if pb and 0 < pb < 2.0: score += 2; items.append("PB=✅")
        elif pb and 0 < pb < 3.0: score += 1; items.append("PB=⚠️")
        if roe and roe > 10: score += 2; items.append("ROE=✅")
        elif roe and roe > 5: score += 1; items.append("ROE=⚠️")
        if div_yield and div_yield > 2: score += 2; items.append("DIV=✅")
        elif div_yield and div_yield > 0: score += 1; items.append("DIV=⚠️")
        if 0 < rsi < 35: score += 2; items.append("RSI=✅超跌")
        elif 0 < rsi < 45: score += 1; items.append("RSI=⚠️")
        
        return {
            "symbol": symbol,
            "price": round(current_price, 2) if current_price else "N/A",
            "pe": round(pe, 1) if pe else "N/A",
            "pb": round(pb, 2) if pb else "N/A",
            "roe": round(roe, 1) if roe else "N/A",
            "div_yield": round(div_yield, 2) if div_yield else "N/A",
            "rsi_14": round(rsi, 1),
            "score": score,
            "items": items,
            "company": name[:30] if name else symbol,
            "sector": sector[:20] if sector else "",
        }
    except Exception as e:
        return {"symbol": symbol, "error": str(e), "score": 0}

def generate_watchlist():
    """Generate weekly value stock watchlist"""
    print(f"[{datetime.now(UTC).isoformat()}] Watchlist Generator - 开始\n")

    results = []
    for i, symbol in enumerate(CORE_STOCKS):
        print(f"  [{i+1}/{len(CORE_STOCKS)}] {symbol}...", end=" ", flush=True)
        result = score_stock_yfinance(symbol)
        results.append(result)
        score = result.get("score", 0)
        items = result.get("items", [])
        print(f"评分={score}" + (f" {' '.join(items)}" if items else ""))

    # Sort by score descending
    results.sort(key=lambda x: x.get("score", 0), reverse=True)

    value_picks = [r for r in results if r.get("score", 0) >= 4]
    watch_picks = [r for r in results if 2 <= r.get("score", 0) < 4]

    date_str = datetime.now(UTC).strftime("%Y-%m-%d")
    md = [
        f"# GitMoney 美股超跌价值股 Watchlist\n",
        f"**生成日期**: {date_str}  |  **策略**: 超跌价值 (PE<15, PB<2, ROE>10%, 股息>2%, RSI<45)\n",
        f"**筛选范围**: {len(CORE_STOCKS)} 只高流动性股票\n\n",
    ]

    md.append(f"## 🔥 核心推荐 (评分 ≥ 4)\n\n")
    if value_picks:
        md.append("| 股票 | 公司(板块) | 评分 | PE | PB | ROE% | 股息% | RSI(14) |\n")
        md.append("|------|------------|------|----|----|------|-------|--------|\n")
        for r in value_picks:
            md.append(f"| {r['symbol']} | {r.get('company','')[:20]} | **{r['score']}**★ | {r['pe']} | {r['pb']} | {r['roe']}% | {r['div_yield']}% | {r['rsi_14']} |\n")
    else:
        md.append("_当前无符合条件的核心推荐。_\n")

    md.append(f"\n## 📋 观察清单 (评分 2-4)\n\n")
    if watch_picks:
        md.append("| 股票 | 公司(板块) | 评分 | PE | PB | ROE% | 股息% | RSI(14) |\n")
        md.append("|------|------------|------|----|----|------|-------|--------|\n")
        for r in watch_picks:
            md.append(f"| {r['symbol']} | {r.get('company','')[:20]} | {r['score']}★ | {r['pe']} | {r['pb']} | {r['roe']}% | {r['div_yield']}% | {r['rsi_14']} |\n")

    md.append(f"\n## 📊 完整排名\n\n")
    md.append("| # | 股票 | 评分 | PE | PB | ROE% | 股息% | RSI(14) | 指标 |\n")
    md.append("|---|------|------|----|----|------|-------|--------|------|\n")
    for idx, r in enumerate(results, 1):
        items_str = " ".join(r.get("items", []))
        md.append(f"| {idx} | {r['symbol']} | {r.get('score',0)}★ | {r.get('pe','N/A')} | {r.get('pb','N/A')} | {r.get('roe','N/A')}% | {r.get('div_yield','N/A')}% | {r.get('rsi_14','N/A')} | {items_str} |\n")

    md.append(f"\n---\n*Captain Tier 权益 - GitMoney Sponsors 专享*\n")

    report = "\n".join(md)
    filepath = DATA_DIR / f"watchlist_{date_str}.md"
    with open(filepath, "w") as f:
        f.write(report)

    print(f"\n✅ Watchlist 已保存: {filepath}")
    print(f"   核心推荐: {len(value_picks)} 只")
    print(f"   观察清单: {len(watch_picks)} 只\n")

    return report

if __name__ == "__main__":
    generate_watchlist()
