"""Public Telegram kanallarından haber toplar (t.me/s/channel scraping).

API key gerektirmez; yalnızca public preview sayfasına erişir.
Yağız Sabuncuoğlu, transferhaber gibi kanallar dahil.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from src.config import PROCESSED_DIR, RAW_DIR, SEASON

MAX_AGE_DAYS = 14


def _is_recent(published_at: str | None) -> bool:
    if not published_at:
        return True
    try:
        pub = datetime.fromisoformat(published_at)
        if pub.tzinfo is None:
            pub = pub.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - pub).days <= MAX_AGE_DAYS
    except Exception:
        return True

TELEGRAM_CHANNELS = [
    # Transfer / genel sinyal kanalları
    {"handle": "transferhaber", "name": "Transfer Haber", "type": "secondary_signal"},
    {"handle": "superligson", "name": "Süper Lig Son Dakika", "type": "secondary_signal"},
    {"handle": "sporxhaber", "name": "Sporx Haber", "type": "secondary_signal"},
    {"handle": "futbolhaber", "name": "Futbol Haber", "type": "secondary_signal"},
    {"handle": "transferturkiye", "name": "Transfer Türkiye", "type": "secondary_signal"},
    {"handle": "superligtransfer", "name": "Süper Lig Transfer", "type": "secondary_signal"},
    # Kulüp bazlı kanallar
    {"handle": "besiktashaberleri", "name": "Beşiktaş Haberleri", "team": "BEŞİKTAŞ A.Ş.", "type": "secondary_signal"},
    {"handle": "fenerbahcehaberleri", "name": "Fenerbahçe Haberleri", "team": "FENERBAHÇE A.Ş.", "type": "secondary_signal"},
    {"handle": "galatasarayhaberleri", "name": "Galatasaray Haberleri", "team": "GALATASARAY A.Ş.", "type": "secondary_signal"},
    {"handle": "trabzonsporhaberleri", "name": "Trabzonspor Haberleri", "team": "TRABZONSPOR A.Ş.", "type": "secondary_signal"},
    {"handle": "basaksehirhaberleri", "name": "Başakşehir Haberleri", "team": "RAMS BAŞAKŞEHİR FUTBOL KULÜBÜ", "type": "secondary_signal"},
]

TRANSFER_KW = {
    "transfer", "bonservis", "anlaşma", "imza", "teklif", "istiyor",
    "ayrılıyor", "geliyor", "resmileşti", "teknik direktör", "hoca",
    "signs", "signed", "deal", "joins", "loan", "here we go",
}
INJURY_KW = {"sakat", "sakatlık", "ameliyat", "injured", "injury"}


def _parse_message(msg_div, channel: dict) -> dict | None:
    text_el = msg_div.select_one(".tgme_widget_message_text")
    if not text_el:
        return None
    text = text_el.get_text(" ", strip=True)
    if not text or len(text) < 15:
        return None

    # Tarih
    published_at = None
    time_el = msg_div.select_one("time")
    if time_el and time_el.get("datetime"):
        try:
            published_at = datetime.fromisoformat(
                time_el["datetime"].replace("Z", "+00:00")
            ).isoformat()
        except Exception:  # noqa: BLE001
            pass

    # Link
    link = ""
    msg_link = msg_div.select_one(".tgme_widget_message_date")
    if msg_link and msg_link.get("href"):
        link = msg_link["href"]
        # t.me/channel/123 -> x.com benzeri canonical link
    elif msg_div.get("data-post"):
        link = f"https://t.me/{msg_div['data-post']}"

    text_lower = text.lower()
    categories = []
    if any(k in text_lower for k in TRANSFER_KW):
        categories.append("transfer")
    if any(k in text_lower for k in INJURY_KW):
        categories.append("injury")
    if not categories:
        categories.append("general")

    article_id = hashlib.md5((channel["handle"] + text[:80]).encode()).hexdigest()[:12]
    return {
        "article_id": article_id,
        "source_type": "telegram",
        "source_name": channel["name"],
        "account_type": channel["type"],
        "source_url": f"https://t.me/s/{channel['handle']}",
        "title": text[:200],
        "link": link,
        "summary": text[:500],
        "full_text": "",
        "published_at": published_at,
        "categories": categories,
        "super_lig_relevant": True,
        "related_team": channel.get("team"),
        "analyzed": False,
        "claude_analysis": None,
    }


def fetch_channel(channel: dict, max_items: int) -> list[dict]:
    url = f"https://t.me/s/{channel['handle']}"
    headers = {"User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1)"}
    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    msg_divs = soup.select(".tgme_widget_message")[-max_items:]

    articles = []
    for div in msg_divs:
        parsed = _parse_message(div, channel)
        if parsed and _is_recent(parsed.get("published_at")):
            articles.append(parsed)
    return articles


def deduplicate(articles: list[dict]) -> list[dict]:
    seen: set[str] = set()
    result = []
    for a in articles:
        if a["article_id"] not in seen:
            seen.add(a["article_id"])
            result.append(a)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Public Telegram kanallarından haber toplar.")
    parser.add_argument("--output-prefix", default=f"news_telegram_latest_{SEASON}")
    parser.add_argument("--delay-seconds", type=float, default=3.0)
    parser.add_argument("--max-items-per-channel", type=int, default=20)
    args = parser.parse_args()

    all_articles: list[dict] = []
    channel_stats = []

    for channel in TELEGRAM_CHANNELS:
        stat: dict = {"handle": channel["handle"], "name": channel["name"], "fetched": 0, "error": None}
        try:
            articles = fetch_channel(channel, args.max_items_per_channel)
            all_articles.extend(articles)
            stat["fetched"] = len(articles)
            print(f"  @{channel['handle']}: {len(articles)} mesaj")
        except Exception as exc:  # noqa: BLE001
            stat["error"] = str(exc)
            print(f"  @{channel['handle']}: HATA — {exc}")
        channel_stats.append(stat)
        time.sleep(args.delay_seconds)

    all_articles = deduplicate(all_articles)
    all_articles.sort(key=lambda a: a.get("published_at") or "", reverse=True)

    ok = sum(1 for s in channel_stats if not s["error"])
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "season": SEASON,
        "provider": "telegram_web",
        "collection_status": "SUCCESS" if ok > 0 else "FAILED",
        "successful_channels": ok,
        "total_channels": len(TELEGRAM_CHANNELS),
        "total_messages": len(all_articles),
        "channels": channel_stats,
        "articles": all_articles,
    }

    out_dir = RAW_DIR / "news_telegram"
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_path = out_dir / f"{args.output_prefix}.json"
    raw_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    processed_path = PROCESSED_DIR / f"{args.output_prefix}.json"
    processed_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\nToplam: {len(all_articles)} mesaj | {ok}/{len(TELEGRAM_CHANNELS)} kanal başarılı")
    print(f"Çıktı: {processed_path}")


if __name__ == "__main__":
    main()
