"""
Türk futbol haber sitelerinden RSS beslemelerini toplar.
Makaleler ham JSON olarak kaydedilir; analyze_news_with_claude tarafından işlenir.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

import feedparser
import requests
from bs4 import BeautifulSoup

from src.config import PROCESSED_DIR, RAW_DIR, SEASON

RSS_SOURCES = [
    {
        "name": "Hürriyet Spor",
        "url": "https://www.hurriyet.com.tr/rss/spor",
        "language": "tr",
        "category": "general",
    },
    {
        "name": "Milliyet Spor",
        "url": "https://www.milliyet.com.tr/rss/rssNew/sporRss.xml",
        "language": "tr",
        "category": "general",
    },
    {
        "name": "Sabah Spor",
        "url": "https://www.sabah.com.tr/rss/spor.xml",
        "language": "tr",
        "category": "general",
    },
    {
        "name": "Haberturk Spor",
        "url": "https://www.haberturk.com/rss",
        "language": "tr",
        "category": "general",
    },
    {
        "name": "Anadolu Ajansı Spor",
        "url": "https://www.aa.com.tr/tr/rss/default?cat=spor",
        "language": "tr",
        "category": "general",
    },
    {
        "name": "Takvim Spor",
        "url": "https://www.takvim.com.tr/rss/spor",
        "language": "tr",
        "category": "general",
    },
    {
        "name": "Aksam Spor",
        "url": "https://www.aksam.com.tr/rss/spor",
        "language": "tr",
        "category": "general",
    },
    {
        "name": "Posta Spor",
        "url": "https://www.posta.com.tr/rss/spor",
        "language": "tr",
        "category": "general",
    },
]

SUPER_LIG_TEAMS = {
    "beşiktaş", "besiktas", "galatasaray", "fenerbahçe", "fenerbahce",
    "trabzonspor", "başakşehir", "basaksehir", "alanyaspor", "samsunspor",
    "göztepe", "goztepe", "konyaspor", "rizespor", "gaziantep",
    "kasımpaşa", "kasimpasa", "kocaelispor", "eyüpspor", "eyupspor",
    "gençlerbirliği", "genclerbirligi", "karagümrük", "karagumruk",
    "antalyaspor", "kayserispor",
}

TRANSFER_KEYWORDS = {"transfer", "bonservis", "anlaşma", "imza", "bağlantı", "teklif", "istiyor", "peşinde", "ayrılıyor", "geliyor"}
INJURY_KEYWORDS = {"sakat", "sakatlık", "yaralanma", "ameliyat", "tedavi", "antrenman dışı", "eksik"}
SUSPENSION_KEYWORDS = {"cezalı", "ceza", "kart", "diskalifiye", "men"}
LINEUP_KEYWORDS = {"kadro", "ilk 11", "muhtemel", "oynayacak", "oynamayacak", "forma"}


def main() -> None:
    parser = argparse.ArgumentParser(description="Türk futbol haber RSS beslemelerini toplar.")
    parser.add_argument("--output-prefix", default=f"news_rss_latest_{SEASON}")
    parser.add_argument("--delay-seconds", type=float, default=2.0)
    parser.add_argument("--max-items-per-source", type=int, default=50)
    parser.add_argument("--fetch-fulltext", action="store_true", help="Her makale için tam metin indir (yavaş)")
    args = parser.parse_args()

    all_articles = []
    source_stats = []

    for source in RSS_SOURCES:
        stat = {"name": source["name"], "url": source["url"], "fetched": 0, "error": None}
        try:
            articles = fetch_source(source, args.max_items_per_source, args.fetch_fulltext)
            all_articles.extend(articles)
            stat["fetched"] = len(articles)
            print(f"  {source['name']}: {len(articles)} makale")
        except Exception as exc:  # noqa: BLE001
            stat["error"] = str(exc)
            print(f"  {source['name']}: HATA — {exc}")
        source_stats.append(stat)
        time.sleep(args.delay_seconds)

    all_articles = deduplicate(all_articles)
    all_articles.sort(key=lambda a: a.get("published_at") or "", reverse=True)

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "season": SEASON,
        "total_articles": len(all_articles),
        "sources": source_stats,
        "articles": all_articles,
    }

    out_dir = RAW_DIR / "news_rss"
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_path = out_dir / f"{args.output_prefix}.json"
    raw_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    processed_path = PROCESSED_DIR / f"{args.output_prefix}.json"
    processed_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    ok_sources = sum(1 for s in source_stats if not s["error"])
    print(f"\nToplam: {len(all_articles)} makale | {ok_sources}/{len(RSS_SOURCES)} kaynak başarılı")
    print(f"Çıktı: {processed_path}")


def fetch_source(source: dict, max_items: int, fetch_fulltext: bool) -> list[dict]:
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; metric11-news/0.1; football intelligence research)",
        "Accept-Language": "tr-TR,tr;q=0.9",
    }
    response = requests.get(source["url"], headers=headers, timeout=20)
    response.raise_for_status()

    feed = feedparser.parse(response.text)
    articles = []
    for entry in feed.entries[:max_items]:
        article = parse_entry(entry, source, fetch_fulltext, headers)
        if article:
            articles.append(article)
    return articles


def parse_entry(entry, source: dict, fetch_fulltext: bool, headers: dict) -> dict | None:
    title = getattr(entry, "title", "") or ""
    link = getattr(entry, "link", "") or ""
    if not title or not link:
        return None

    summary = getattr(entry, "summary", "") or getattr(entry, "description", "") or ""
    # Only parse as HTML if it looks like markup (contains < or is long enough)
    if summary and ("<" in summary or len(summary) > 80):
        summary_text = BeautifulSoup(summary, "html.parser").get_text(" ", strip=True)[:600]
    else:
        summary_text = summary[:600]

    published_at = None
    if hasattr(entry, "published"):
        try:
            published_at = parsedate_to_datetime(entry.published).isoformat()
        except Exception:  # noqa: BLE001
            pass
    if published_at is None and hasattr(entry, "updated"):
        try:
            published_at = parsedate_to_datetime(entry.updated).isoformat()
        except Exception:  # noqa: BLE001
            pass

    full_text = ""
    if fetch_fulltext and link:
        try:
            r = requests.get(link, headers=headers, timeout=15)
            soup = BeautifulSoup(r.text, "html.parser")
            for tag in soup(["script", "style", "nav", "header", "footer", "aside"]):
                tag.decompose()
            for sel in ("article", "main", ".content", ".article-body", ".haber-detay"):
                node = soup.select_one(sel)
                if node:
                    full_text = node.get_text(" ", strip=True)[:3000]
                    break
            if not full_text:
                full_text = soup.body.get_text(" ", strip=True)[:2000] if soup.body else ""
        except Exception:  # noqa: BLE001
            pass

    text_combined = f"{title} {summary_text} {full_text}".lower()
    categories = detect_categories(text_combined)
    relevance = detect_relevance(text_combined)

    article_id = hashlib.md5(link.encode()).hexdigest()[:12]

    return {
        "article_id": article_id,
        "source_name": source["name"],
        "source_url": source["url"],
        "title": title,
        "link": link,
        "summary": summary_text,
        "full_text": full_text if fetch_fulltext else "",
        "published_at": published_at,
        "categories": categories,
        "super_lig_relevant": relevance,
        "analyzed": False,
        "claude_analysis": None,
    }


def detect_categories(text: str) -> list[str]:
    cats = []
    if any(k in text for k in TRANSFER_KEYWORDS):
        cats.append("transfer")
    if any(k in text for k in INJURY_KEYWORDS):
        cats.append("injury")
    if any(k in text for k in SUSPENSION_KEYWORDS):
        cats.append("suspension")
    if any(k in text for k in LINEUP_KEYWORDS):
        cats.append("lineup")
    if not cats:
        cats.append("general")
    return cats


def detect_relevance(text: str) -> bool:
    return any(team in text for team in SUPER_LIG_TEAMS)


def deduplicate(articles: list[dict]) -> list[dict]:
    seen = set()
    result = []
    for a in articles:
        key = a["article_id"]
        if key not in seen:
            seen.add(key)
            result.append(a)
    return result


if __name__ == "__main__":
    main()
