"""Google News RSS üzerinden Türk futbolu anahtar kelime haberleri toplar.

X API yerine ücretsiz alternatif: keyword başına RSS feed getirir,
RSS kaynaklarında çıkmayan transfer muhabiri haberlerini de kapsar.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import quote

import feedparser
import requests

from src.config import PROCESSED_DIR, RAW_DIR, ROOT_DIR, SEASON

GOOGLE_NEWS_BASE = "https://news.google.com/rss/search"

TEAM_QUERY_NAMES = {
    "BEŞİKTAŞ A.Ş.": "Beşiktaş",
    "GALATASARAY A.Ş.": "Galatasaray",
    "FENERBAHÇE A.Ş.": "Fenerbahçe",
    "TRABZONSPOR A.Ş.": "Trabzonspor",
    "RAMS BAŞAKŞEHİR FUTBOL KULÜBÜ": "Başakşehir",
    "CORENDON ALANYASPOR": "Alanyaspor",
    "SAMSUNSPOR A.Ş.": "Samsunspor",
    "GÖZTEPE A.Ş.": "Göztepe",
    "TÜMOSAN KONYASPOR": "Konyaspor",
    "ÇAYKUR RİZESPOR A.Ş.": "Çaykur Rizespor",
    "GAZİANTEP FUTBOL KULÜBÜ A.Ş.": "Gaziantep FK",
    "KASIMPAŞA A.Ş.": "Kasımpaşa",
    "KOCAELİSPOR": "Kocaelispor",
    "İKAS EYÜPSPOR": "Eyüpspor",
    "GENÇLERBİRLİĞİ": "Gençlerbirliği",
    "ÇORUM FK": "Çorum FK",
    "ERZURUMSPOR FK": "Erzurumspor FK",
    "AMED SFK": "Amedspor",
}


def build_search_queries() -> list[tuple[str, str]]:
    clubs_path = ROOT_DIR / "data/manual/transfermarkt_super_lig_clubs.json"
    clubs = json.loads(clubs_path.read_text(encoding="utf-8")).get("clubs", [])
    queries = [(f"{TEAM_QUERY_NAMES[club['team_name']]} transfer", "transfer") for club in clubs]
    queries.extend(
        [
            ("Süper Lig teknik direktör", "transfer"),
            ("Süper Lig bonservis imza", "transfer"),
            ("Süper Lig sakat cezalı", "injury"),
            ("Yağız Sabuncuoğlu transfer", "transfer"),
            ("Ertan Süzgün transfer", "transfer"),
            ("Sports Digitale transfer", "transfer"),
            ("Yusuf Günaydın transfer", "transfer"),
            ("Ekrem Konur Süper Lig transfer", "transfer"),
        ]
    )
    return queries


SEARCH_QUERIES = build_search_queries()


def _google_news_url(query: str) -> str:
    return f"{GOOGLE_NEWS_BASE}?q={quote(query)}&hl=tr&gl=TR&ceid=TR:tr"


def _parse_entry(entry: object, query: str, category: str) -> dict | None:
    title = getattr(entry, "title", "") or ""
    link = getattr(entry, "link", "") or ""
    if not title or not link:
        return None

    published_at = None
    if hasattr(entry, "published"):
        try:
            published_at = parsedate_to_datetime(entry.published).isoformat()
        except Exception:  # noqa: BLE001
            pass

    source_title = ""
    if hasattr(entry, "source") and entry.source:
        source_title = getattr(entry.source, "title", "") or ""

    article_id = hashlib.md5(link.encode()).hexdigest()[:12]
    return {
        "article_id": article_id,
        "source_type": "google_news",
        "source_name": source_title or "Google News",
        "source_url": link,
        "title": title,
        "link": link,
        "summary": "",
        "full_text": "",
        "published_at": published_at,
        "categories": [category],
        "super_lig_relevant": True,
        "query": query,
        "analyzed": False,
        "claude_analysis": None,
    }


def fetch_query(query: str, category: str, max_items: int) -> list[dict]:
    url = _google_news_url(query)
    headers = {"User-Agent": "Mozilla/5.0 (compatible; metric11-news/0.1; research)"}
    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()
    feed = feedparser.parse(resp.text)
    results = []
    for entry in feed.entries[:max_items]:
        parsed = _parse_entry(entry, query, category)
        if parsed:
            results.append(parsed)
    return results


def deduplicate(articles: list[dict]) -> list[dict]:
    seen: set[str] = set()
    result = []
    for a in articles:
        if a["article_id"] not in seen:
            seen.add(a["article_id"])
            result.append(a)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Google News RSS ile Türk futbol haberleri toplar.")
    parser.add_argument("--output-prefix", default=f"news_google_latest_{SEASON}")
    parser.add_argument("--delay-seconds", type=float, default=2.0)
    parser.add_argument("--max-items-per-query", type=int, default=15)
    args = parser.parse_args()

    all_articles: list[dict] = []
    query_stats = []

    for query, category in SEARCH_QUERIES:
        stat: dict = {"query": query, "category": category, "fetched": 0, "error": None}
        try:
            articles = fetch_query(query, category, args.max_items_per_query)
            all_articles.extend(articles)
            stat["fetched"] = len(articles)
            print(f"  '{query}': {len(articles)} haber")
        except Exception as exc:  # noqa: BLE001
            stat["error"] = str(exc)
            print(f"  '{query}': HATA — {exc}")
        query_stats.append(stat)
        time.sleep(args.delay_seconds)

    all_articles = deduplicate(all_articles)
    all_articles.sort(key=lambda a: a.get("published_at") or "", reverse=True)

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "season": SEASON,
        "provider": "google_news_rss",
        "total_articles": len(all_articles),
        "queries": query_stats,
        "articles": all_articles,
    }

    out_dir = RAW_DIR / "news_google"
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_path = out_dir / f"{args.output_prefix}.json"
    raw_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    processed_path = PROCESSED_DIR / f"{args.output_prefix}.json"
    processed_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    ok = sum(1 for s in query_stats if not s["error"])
    print(f"\nToplam: {len(all_articles)} haber | {ok}/{len(SEARCH_QUERIES)} sorgu başarılı")
    print(f"Çıktı: {processed_path}")


if __name__ == "__main__":
    main()
