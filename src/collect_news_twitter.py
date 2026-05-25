"""
Twitter/X takip hesaplarından nitter RSS aracılığıyla spor haberlerini toplar.
Resmi API gerektirmez. Nitter instance'ları otomatik denenir.
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

from src.config import PROCESSED_DIR, RAW_DIR, SEASON

# Nitter instance'ları — birincisi çalışmazsa diğerine geçer
NITTER_INSTANCES = [
    "https://nitter.net",
    "https://nitter.privacydev.net",
    "https://nitter.poast.org",
    "https://nitter.1d4.us",
]

# Türk futbolu için takip edilecek hesaplar
TWITTER_ACCOUNTS = [
    {"handle": "bjkcom", "name": "Beşiktaş Resmi", "team": "BEŞİKTAŞ A.Ş.", "type": "official"},
    {"handle": "galatasaray", "name": "Galatasaray Resmi", "team": "GALATASARAY A.Ş.", "type": "official"},
    {"handle": "Fenerbahce", "name": "Fenerbahçe Resmi", "team": "FENERBAHÇE A.Ş.", "type": "official"},
    {"handle": "trabzonspor", "name": "Trabzonspor Resmi", "team": "TRABZONSPOR A.Ş.", "type": "official"},
    {"handle": "TFForg", "name": "TFF Resmi", "team": None, "type": "official"},
    {"handle": "fanatikgazetesi", "name": "Fanatik", "team": None, "type": "media"},
    {"handle": "hurspor", "name": "Hürriyet Spor", "team": None, "type": "media"},
    {"handle": "fotomacgazetesi", "name": "Fotomaç", "team": None, "type": "media"},
    {"handle": "BeINSPORTS_TR", "name": "beIN Sports TR", "team": None, "type": "media"},
    {"handle": "YakinTakip", "name": "Yakın Takip (Transfer)", "team": None, "type": "transfer_news"},
    {"handle": "transfermarkt_TR", "name": "Transfermarkt TR", "team": None, "type": "transfer_news"},
    {"handle": "TurkishFootball", "name": "Turkish Football", "team": None, "type": "media"},
]

SUPER_LIG_TEAMS = {
    "beşiktaş", "besiktas", "galatasaray", "fenerbahçe", "fenerbahce",
    "trabzonspor", "başakşehir", "basaksehir", "alanyaspor", "samsunspor",
    "göztepe", "goztepe", "konyaspor", "rizespor", "gaziantep",
    "kasımpaşa", "kasimpasa", "kocaelispor", "eyüpspor", "eyupspor",
    "gençlerbirliği", "genclerbirligi", "karagümrük", "karagumruk",
    "antalyaspor", "kayserispor",
    # 2026-2027 promosyon adayları
    "çorumspor", "corumspor", "adanaspor", "sakaryaspor", "bodrumspor",
    "manisaspor", "erzurumspor", "altay", "altinordu",
}

TRANSFER_KW = {"transfer", "bonservis", "anlaşma", "imza", "teklif", "istiyor", "ayrılıyor", "geliyor", "görüşme"}
INJURY_KW = {"sakat", "sakatlık", "yaralanma", "ameliyat", "tedavi"}
PROMOTION_KW = {"çıktı", "yükseldi", "şampiyon", "playoff", "süper lig'e", "1. lig", "tff 1"}


def main() -> None:
    parser = argparse.ArgumentParser(description="Twitter/nitter üzerinden Türk futbol haberlerini toplar.")
    parser.add_argument("--output-prefix", default=f"news_twitter_latest_{SEASON}")
    parser.add_argument("--delay-seconds", type=float, default=2.0)
    parser.add_argument("--max-tweets-per-account", type=int, default=20)
    args = parser.parse_args()

    working_instance = _find_working_nitter()
    if not working_instance:
        print("UYARI: Çalışan nitter instance bulunamadı. Atlanıyor.")
        return

    print(f"Nitter instance: {working_instance}")

    all_tweets = []
    account_stats = []

    for account in TWITTER_ACCOUNTS:
        stat = {"handle": account["handle"], "name": account["name"], "fetched": 0, "error": None}
        try:
            tweets = fetch_account(account, working_instance, args.max_tweets_per_account)
            all_tweets.extend(tweets)
            stat["fetched"] = len(tweets)
            print(f"  @{account['handle']}: {len(tweets)} tweet")
        except Exception as exc:  # noqa: BLE001
            stat["error"] = str(exc)
            print(f"  @{account['handle']}: HATA — {exc}")
        account_stats.append(stat)
        time.sleep(args.delay_seconds)

    all_tweets = _deduplicate(all_tweets)
    all_tweets.sort(key=lambda t: t.get("published_at") or "", reverse=True)

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "season": SEASON,
        "nitter_instance": working_instance,
        "total_tweets": len(all_tweets),
        "accounts": account_stats,
        "tweets": all_tweets,
    }

    out_dir = RAW_DIR / "news_twitter"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"{args.output_prefix}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    processed_path = PROCESSED_DIR / f"{args.output_prefix}.json"
    processed_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    ok = sum(1 for s in account_stats if not s["error"])
    print(f"\nToplandı: {len(all_tweets)} tweet | {ok}/{len(TWITTER_ACCOUNTS)} hesap başarılı")
    print(f"Çıktı: {processed_path}")


def _find_working_nitter() -> str | None:
    for instance in NITTER_INSTANCES:
        try:
            r = requests.get(f"{instance}/bjkcom/rss", timeout=8)
            if r.status_code == 200 and "<rss" in r.text[:200]:
                return instance
        except Exception:  # noqa: BLE001
            pass
    return None


def fetch_account(account: dict, nitter_base: str, max_items: int) -> list[dict]:
    url = f"{nitter_base}/{account['handle']}/rss"
    headers = {"User-Agent": "Mozilla/5.0 (compatible; metric11-news/0.1; research)"}
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()

    feed = feedparser.parse(response.text)
    tweets = []
    for entry in feed.entries[:max_items]:
        tweet = _parse_entry(entry, account)
        if tweet:
            tweets.append(tweet)
    return tweets


def _parse_entry(entry, account: dict) -> dict | None:
    title = getattr(entry, "title", "") or ""
    link = getattr(entry, "link", "") or ""
    if not title:
        return None

    # Nitter links point to nitter; convert back to twitter.com
    twitter_link = link.replace(NITTER_INSTANCES[0], "https://twitter.com") if link else ""

    published_at = None
    if hasattr(entry, "published"):
        try:
            published_at = parsedate_to_datetime(entry.published).isoformat()
        except Exception:  # noqa: BLE001
            pass

    text = title.lower()
    categories = []
    if any(k in text for k in TRANSFER_KW):
        categories.append("transfer")
    if any(k in text for k in INJURY_KW):
        categories.append("injury")
    if any(k in text for k in PROMOTION_KW):
        categories.append("promotion_relegation")
    if not categories:
        categories.append("general")

    relevant = any(team in text for team in SUPER_LIG_TEAMS)

    article_id = hashlib.md5(link.encode()).hexdigest()[:12]
    return {
        "article_id": article_id,
        "source_type": "twitter",
        "source_name": f"@{account['handle']}",
        "account_type": account["type"],
        "related_team": account.get("team"),
        "title": title,
        "link": twitter_link or link,
        "summary": title,
        "full_text": "",
        "published_at": published_at,
        "categories": categories,
        "super_lig_relevant": relevant,
        "analyzed": False,
        "claude_analysis": None,
    }


def _deduplicate(tweets: list[dict]) -> list[dict]:
    seen = set()
    result = []
    for t in tweets:
        if t["article_id"] not in seen:
            seen.add(t["article_id"])
            result.append(t)
    return result


if __name__ == "__main__":
    main()
