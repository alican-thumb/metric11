"""Collect transfer and availability announcements from official club websites.

This collector has no credential dependency. Every configured Super Lig club
is probed and its access result is retained, including failures and empty
listing pages, so official coverage can be measured honestly.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from src.collect_news_rss import detect_categories
from src.config import PROCESSED_DIR, RAW_DIR, ROOT_DIR, SEASON

DEFAULT_SOURCE_PATH = ROOT_DIR / "data/manual/official_club_news_sources.json"
SIGNAL_TERMS = (
    "transfer",
    "imza",
    "anlaş",
    "hos geldin",
    "hoş geldin",
    "kamuoyuna",
    "sözleş",
    "kiralık",
    "geçici",
    "ayrıl",
    "tesekkur",
    "teşekkür",
    "sakat",
    "sağlık durumu",
    "sağlık raporu",
    "ameliyat",
    "operasyon",
    "kart cezas",
    "cezalı",
    "kadroda yok",
    "kadro dışı",
)
NON_FOOTBALL_ANNOUNCEMENT_TERMS = ("sponsor", "reklam", "stadyum isim hakkı")
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; metric11-official-news/0.1; football research)",
    "Accept-Language": "tr-TR,tr;q=0.9",
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Resmi Süper Lig kulüp haber sayfalarından duyuru toplar.")
    parser.add_argument("--sources", default=str(DEFAULT_SOURCE_PATH))
    parser.add_argument("--output-prefix", default=f"news_official_clubs_latest_{SEASON}")
    parser.add_argument("--delay-seconds", type=float, default=0.3)
    parser.add_argument("--max-items-per-source", type=int, default=20)
    parser.add_argument("--timeout-seconds", type=float, default=8)
    args = parser.parse_args()

    sources = json.loads(Path(args.sources).read_text(encoding="utf-8")).get("sources", [])
    payload = collect_sources(sources, args.max_items_per_source, args.delay_seconds, args.timeout_seconds)
    processed_path = write_snapshot(payload, args.output_prefix)
    print(
        f"Resmi kulüp kaynağı: {payload['successful_sources']}/{payload['configured_sources']} erişilebilir | "
        f"{payload['total_articles']} sinyal içerikli duyuru"
    )
    print(f"Çıktı: {processed_path}")


def collect_sources(sources: list[dict], max_items: int, delay_seconds: float, timeout_seconds: float = 8) -> dict:
    all_articles = []
    source_stats = []
    for source in sources:
        stat = {
            "team": source["team"],
            "name": source["name"],
            "url": source["url"],
            "fetched": 0,
            "warnings": [],
            "error": None,
        }
        try:
            articles, warnings = fetch_source(source, max_items, timeout_seconds)
            all_articles.extend(articles)
            stat["fetched"] = len(articles)
            stat["warnings"] = warnings
            print(f"  {source['name']}: {len(articles)} duyuru")
        except Exception as exc:  # noqa: BLE001
            stat["error"] = str(exc)[:180]
            print(f"  {source['name']}: HATA - {stat['error']}")
        source_stats.append(stat)
        if delay_seconds:
            time.sleep(delay_seconds)

    articles = deduplicate(all_articles)
    articles.sort(key=lambda article: article.get("published_at") or "", reverse=True)
    accessible = sum(1 for stat in source_stats if not stat["error"])
    status = "SUCCESS" if accessible == len(sources) else ("PARTIAL_SUCCESS" if accessible else "FAILED")
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "season": SEASON,
        "source_type": "official_club",
        "collection_status": status,
        "configured_sources": len(sources),
        "successful_sources": accessible,
        "total_articles": len(articles),
        "sources": source_stats,
        "articles": articles,
    }


def fetch_source(source: dict, max_items: int, timeout_seconds: float = 8) -> tuple[list[dict], list[str]]:
    warnings = []
    candidates = [
        (seed.get("title", ""), seed["url"])
        for seed in source.get("seed_urls", [])
        if seed.get("url")
    ]
    listing_accessible = False
    try:
        response = requests.get(source["url"], headers=HEADERS, timeout=timeout_seconds)
        response.raise_for_status()
        listing_accessible = True
        candidates.extend(extract_candidate_links(response.text, source["url"]))
    except Exception as exc:  # noqa: BLE001
        warnings.append(f"listing: {str(exc)[:120]}")

    articles = []
    detail_accessible = False
    seen_links = set()
    for title, link in candidates:
        if link in seen_links or len(articles) >= max_items:
            continue
        seen_links.add(link)
        try:
            article = fetch_article(source, title, link, timeout_seconds)
            detail_accessible = True
            if article:
                articles.append(article)
        except Exception as exc:  # noqa: BLE001
            warnings.append(f"article {link}: {str(exc)[:120]}")
    if not listing_accessible and not detail_accessible:
        raise RuntimeError("; ".join(warnings) or "resmi kaynak erişilemedi")
    return articles, warnings


def extract_candidate_links(html: str, base_url: str) -> list[tuple[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    domain = urlparse(base_url).netloc.lower().replace("www.", "")
    seen = set()
    candidates = []
    for anchor in soup.select("a[href]"):
        title = " ".join(anchor.get_text(" ", strip=True).split())
        link = urljoin(base_url, anchor.get("href", ""))
        if not title or len(title) < 7:
            continue
        if domain not in urlparse(link).netloc.lower().replace("www.", ""):
            continue
        key_text = f"{title} {link}".lower()
        if not any(term in key_text for term in SIGNAL_TERMS):
            continue
        if link not in seen:
            seen.add(link)
            candidates.append((title, link))
    return candidates


def fetch_article(source: dict, listing_title: str, link: str, timeout_seconds: float = 8) -> dict | None:
    response = requests.get(link, headers=HEADERS, timeout=timeout_seconds)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    title_node = soup.find("h1") or soup.find("title")
    title = listing_title or (title_node.get_text(" ", strip=True) if title_node else link)
    time_node = soup.select_one("time[datetime]")
    published_at = time_node.get("datetime") if time_node else None
    for tag in soup(["script", "style", "nav", "header", "footer", "aside"]):
        tag.decompose()
    detail_text = " ".join((soup.get_text(" ", strip=True) or "").split())[:3000]
    text = f"{title} {detail_text}".lower()
    if any(term in title.lower() for term in NON_FOOTBALL_ANNOUNCEMENT_TERMS):
        return None
    categories = detect_categories(text)
    if categories == ["general"]:
        return None
    published_at = published_at or extract_date(detail_text)
    return {
        "article_id": hashlib.md5(link.encode()).hexdigest()[:12],
        "source_type": "official_club",
        "source_name": source["name"],
        "account_type": "official",
        "related_team": source["team"],
        "source_url": source["url"],
        "title": title,
        "link": link,
        "summary": detail_text[:600],
        "full_text": detail_text,
        "published_at": published_at,
        "categories": categories,
        "super_lig_relevant": True,
        "analyzed": False,
        "claude_analysis": None,
    }


def extract_date(text: str) -> str | None:
    match = re.search(r"(\d{2})[./](\d{2})[./](\d{4})(?:\s+\w+\s+)?\s*(\d{2})[:.](\d{2})", text)
    if not match:
        return None
    day, month, year, hour, minute = match.groups()
    return f"{year}-{month}-{day}T{hour}:{minute}:00+03:00"


def deduplicate(articles: list[dict]) -> list[dict]:
    return list({article["article_id"]: article for article in articles}.values())


def write_snapshot(payload: dict, output_prefix: str) -> Path:
    content = json.dumps(payload, ensure_ascii=False, indent=2)
    raw_dir = RAW_DIR / "news_official_clubs"
    raw_dir.mkdir(parents=True, exist_ok=True)
    (raw_dir / f"{output_prefix}.json").write_text(content, encoding="utf-8")
    processed_path = PROCESSED_DIR / f"{output_prefix}.json"
    processed_path.write_text(content, encoding="utf-8")
    return processed_path


if __name__ == "__main__":
    main()
