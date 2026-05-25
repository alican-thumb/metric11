"""X hesaplarından resmi API veya geliştirme fallback'i ile haber toplar.

`X_BEARER_TOKEN` tanımlıysa X API v2 kullanıcı timeline'ları kullanılır.
Anahtar yoksa Nitter RSS yalnız erişim denemesi/fallback olarak çalışır.
Başarısız toplama da durum snapshot'ı üretir; eksik veri sessiz kalmaz.
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

from src.config import PROCESSED_DIR, RAW_DIR, SEASON, load_settings

X_API_BASE = "https://api.x.com/2"

# Nitter instance'ları — birincisi çalışmazsa diğerine geçer
NITTER_INSTANCES = [
    "https://nitter.net",
    "https://nitter.privacydev.net",
    "https://nitter.poast.org",
    "https://nitter.1d4.us",
]

# Türk futbolu için takip edilecek hesaplar
TWITTER_ACCOUNTS = [
    # --- Resmi kulüp hesapları ---
    {"handle": "Besiktas", "name": "Beşiktaş Resmi", "team": "BEŞİKTAŞ A.Ş.", "type": "official"},
    {"handle": "GalatasaraySK", "name": "Galatasaray Resmi", "team": "GALATASARAY A.Ş.", "type": "official"},
    {"handle": "Fenerbahce", "name": "Fenerbahçe Resmi", "team": "FENERBAHÇE A.Ş.", "type": "official"},
    {"handle": "trabzonspor", "name": "Trabzonspor Resmi", "team": "TRABZONSPOR A.Ş.", "type": "official"},
    {"handle": "ibfk2014", "name": "RAMS Başakşehir Resmi", "team": "RAMS BAŞAKŞEHİR F.K.", "type": "official"},
    {"handle": "Alanyaspor", "name": "Corendon Alanyaspor Resmi", "team": "CORENDON ALANYASPOR", "type": "official"},
    {"handle": "Samsunspor", "name": "Samsunspor Resmi", "team": "SAMSUNSPOR", "type": "official"},
    {"handle": "Goztepe", "name": "Göztepe Resmi", "team": "GÖZTEPE", "type": "official"},
    {"handle": "konyaspor", "name": "TÜMOSAN Konyaspor Resmi", "team": "TÜMOSAN KONYASPOR", "type": "official"},
    {"handle": "CRizesporAS", "name": "Çaykur Rizespor Resmi", "team": "ÇAYKUR RİZESPOR", "type": "official"},
    {"handle": "gaziantepfk", "name": "Gaziantep FK Resmi", "team": "GAZİANTEP FK", "type": "official"},
    {"handle": "kasimpasa", "name": "Kasımpaşa Resmi", "team": "KASIMPAŞA S.K.", "type": "official"},
    {"handle": "Kocaelispor", "name": "Kocaelispor Resmi", "team": "KOCAELİSPOR", "type": "official"},
    {"handle": "eyupsporkulubu", "name": "ikas Eyüpspor Resmi", "team": "İKAS EYÜPSPOR", "type": "official"},
    {"handle": "kirmizikara", "name": "Gençlerbirliği Resmi", "team": "GENÇLERBİRLİĞİ S.K.", "type": "official"},
    {"handle": "karagumruk_sk", "name": "Fatih Karagümrük Resmi", "team": "FATİH KARAGÜMRÜK", "type": "official"},
    {"handle": "Antalyaspor", "name": "Hesap.com Antalyaspor Resmi", "team": "HESAP.COM ANTALYASPOR", "type": "official"},
    {"handle": "KayserisporFK", "name": "Zecorner Kayserispor Resmi", "team": "ZECORNER KAYSERİSPOR", "type": "official"},
    # --- Resmi lig / federasyon ---
    {"handle": "TFF_Org", "name": "TFF Resmi", "team": None, "type": "official"},
    {"handle": "superlig", "name": "Trendyol Süper Lig", "team": None, "type": "official"},
    # --- Medya ---
    {"handle": "fanatikgazetesi", "name": "Fanatik", "team": None, "type": "media"},
    {"handle": "hurspor", "name": "Hürriyet Spor", "team": None, "type": "media"},
    {"handle": "fotomacgazetesi", "name": "Fotomaç", "team": None, "type": "media"},
    {"handle": "BeINSPORTS_TR", "name": "beIN Sports TR", "team": None, "type": "media"},
    {"handle": "trtspor", "name": "TRT Spor", "team": None, "type": "media"},
    {"handle": "SportsDigitale", "name": "Sports Digitale", "team": None, "type": "secondary_signal"},
    # --- Transfer / muhabir ---
    {"handle": "YakinTakip", "name": "Yakın Takip (Transfer)", "team": None, "type": "transfer_news"},
    {"handle": "transfermarkt_TR", "name": "Transfermarkt TR", "team": None, "type": "transfer_news"},
    {"handle": "yagosabuncuoglu", "name": "Yağız Sabuncuoğlu", "team": None, "type": "secondary_signal"},
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
    parser = argparse.ArgumentParser(description="X API veya Nitter fallback ile Türk futbol haberlerini toplar.")
    parser.add_argument("--output-prefix", default=f"news_twitter_latest_{SEASON}")
    parser.add_argument("--delay-seconds", type=float, default=2.0)
    parser.add_argument("--max-tweets-per-account", type=int, default=20)
    parser.add_argument(
        "--provider",
        choices=("auto", "x_api", "nitter"),
        default="auto",
        help="auto: X_BEARER_TOKEN varsa resmi API, yoksa Nitter fallback.",
    )
    args = parser.parse_args()

    settings = load_settings()
    bearer_token = settings.x_bearer_token
    provider = "x_api" if args.provider == "auto" and bearer_token else args.provider
    provider = "nitter" if provider == "auto" else provider

    if provider == "x_api" and not bearer_token:
        payload = _build_payload(
            provider="x_api",
            tweets=[],
            accounts=[],
            collection_status="MISSING_CREDENTIALS",
            provider_error="X_BEARER_TOKEN bulunamadı.",
        )
    elif provider == "x_api":
        payload = collect_x_api(bearer_token, args.max_tweets_per_account, args.delay_seconds)
    else:
        payload = collect_nitter(args.max_tweets_per_account, args.delay_seconds)

    processed_path = write_snapshot(payload, args.output_prefix)
    print(
        f"\nToplandı: {payload['total_tweets']} gönderi | "
        f"{payload['successful_accounts']}/{payload['configured_accounts']} hesap başarılı | "
        f"durum={payload['collection_status']}"
    )
    if payload.get("provider_error"):
        print(f"Kaynak hatası: {payload['provider_error']}")
    print(f"Çıktı: {processed_path}")


def collect_x_api(bearer_token: str, max_items: int, delay_seconds: float) -> dict:
    print("Kaynak: X API v2")
    headers = {"Authorization": f"Bearer {bearer_token}"}
    all_tweets = []
    account_stats = []
    try:
        users = _resolve_x_users(headers)
    except requests.RequestException as exc:
        return _build_payload(
            provider="x_api",
            tweets=[],
            accounts=[],
            collection_status="FAILED",
            provider_error=_http_error_message(exc),
        )

    for account in TWITTER_ACCOUNTS:
        stat = _account_stat(account)
        user = users.get(account["handle"].lower())
        if not user:
            stat["error"] = "X API kullanıcı kimliği çözümlenemedi."
        else:
            stat["x_user_id"] = user["id"]
            try:
                tweets = fetch_x_api_account(account, user["id"], headers, max_items)
                all_tweets.extend(tweets)
                stat["fetched"] = len(tweets)
                print(f"  @{account['handle']}: {len(tweets)} gönderi")
            except requests.RequestException as exc:
                stat["error"] = _http_error_message(exc)
                print(f"  @{account['handle']}: HATA - {stat['error']}")
        account_stats.append(stat)
        if delay_seconds:
            time.sleep(delay_seconds)

    return _finalize_payload("x_api", all_tweets, account_stats)


def collect_nitter(max_items: int, delay_seconds: float) -> dict:
    working_instance = _find_working_nitter()
    if not working_instance:
        return _build_payload(
            provider="nitter",
            tweets=[],
            accounts=[],
            collection_status="FAILED",
            provider_error="Çalışan Nitter instance bulunamadı; X_BEARER_TOKEN tanımlanmalı.",
        )

    print(f"Kaynak: Nitter fallback ({working_instance})")
    all_tweets = []
    account_stats = []
    for account in TWITTER_ACCOUNTS:
        stat = _account_stat(account)
        try:
            tweets = fetch_account(account, working_instance, max_items)
            all_tweets.extend(tweets)
            stat["fetched"] = len(tweets)
            print(f"  @{account['handle']}: {len(tweets)} gönderi")
        except Exception as exc:  # noqa: BLE001
            stat["error"] = str(exc)
            print(f"  @{account['handle']}: HATA - {exc}")
        account_stats.append(stat)
        if delay_seconds:
            time.sleep(delay_seconds)

    return _finalize_payload("nitter", all_tweets, account_stats, nitter_instance=working_instance)


def write_snapshot(payload: dict, output_prefix: str) -> Path:
    out_dir = RAW_DIR / "news_twitter"
    out_dir.mkdir(parents=True, exist_ok=True)
    content = json.dumps(payload, ensure_ascii=False, indent=2)
    (out_dir / f"{output_prefix}.json").write_text(content, encoding="utf-8")
    processed_path = PROCESSED_DIR / f"{output_prefix}.json"
    processed_path.write_text(content, encoding="utf-8")
    return processed_path


def _account_stat(account: dict) -> dict:
    return {
        "handle": account["handle"],
        "name": account["name"],
        "account_type": account["type"],
        "team": account.get("team"),
        "fetched": 0,
        "error": None,
    }


def _resolve_x_users(headers: dict) -> dict[str, dict]:
    handles = ",".join(account["handle"] for account in TWITTER_ACCOUNTS)
    response = requests.get(
        f"{X_API_BASE}/users/by",
        headers=headers,
        params={"usernames": handles, "user.fields": "id,username,name,verified"},
        timeout=20,
    )
    response.raise_for_status()
    return {item["username"].lower(): item for item in response.json().get("data", [])}


def fetch_x_api_account(account: dict, user_id: str, headers: dict, max_items: int) -> list[dict]:
    response = requests.get(
        f"{X_API_BASE}/users/{user_id}/tweets",
        headers=headers,
        params={
            "max_results": max(5, min(max_items, 100)),
            "exclude": "retweets,replies",
            "tweet.fields": "created_at,lang,referenced_tweets",
        },
        timeout=20,
    )
    response.raise_for_status()
    return [_parse_api_post(post, account) for post in response.json().get("data", []) if post.get("text")]


def _parse_api_post(post: dict, account: dict) -> dict:
    link = f"https://x.com/{account['handle']}/status/{post['id']}"
    return _build_article(post["text"], link, post.get("created_at"), account)


def _find_working_nitter() -> str | None:
    for instance in NITTER_INSTANCES:
        try:
            r = requests.get(f"{instance}/Besiktas/rss", timeout=8)
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

    # Nitter links point to the selected mirror; publish the original X link.
    twitter_link = link
    for instance in NITTER_INSTANCES:
        twitter_link = twitter_link.replace(instance, "https://x.com")

    published_at = None
    if hasattr(entry, "published"):
        try:
            published_at = parsedate_to_datetime(entry.published).isoformat()
        except Exception:  # noqa: BLE001
            pass

    return _build_article(title, twitter_link or link, published_at, account)


def _build_article(title: str, link: str, published_at: str | None, account: dict) -> dict:
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

    # A club's official post is relevant even when it only names a signing
    # and does not repeat the club name in the post text.
    relevant = bool(account.get("team")) or any(team in text for team in SUPER_LIG_TEAMS)

    article_id = hashlib.md5(link.encode()).hexdigest()[:12]
    return {
        "article_id": article_id,
        "source_type": "twitter",
        "source_name": f"@{account['handle']}",
        "account_type": account["type"],
        "related_team": account.get("team"),
        "title": title,
        "link": link,
        "summary": title,
        "full_text": "",
        "published_at": published_at,
        "categories": categories,
        "super_lig_relevant": relevant,
        "analyzed": False,
        "claude_analysis": None,
    }


def _finalize_payload(provider: str, tweets: list[dict], accounts: list[dict], **extra) -> dict:
    unique_tweets = _deduplicate(tweets)
    unique_tweets.sort(key=lambda tweet: tweet.get("published_at") or "", reverse=True)
    successful_accounts = sum(1 for account in accounts if not account.get("error"))
    if unique_tweets and successful_accounts == len(TWITTER_ACCOUNTS):
        status = "SUCCESS"
    elif unique_tweets:
        status = "PARTIAL_SUCCESS"
    elif successful_accounts:
        status = "EMPTY"
    else:
        status = "FAILED"
    return _build_payload(provider, unique_tweets, accounts, status, **extra)


def _build_payload(
    provider: str,
    tweets: list[dict],
    accounts: list[dict],
    collection_status: str,
    provider_error: str | None = None,
    **extra,
) -> dict:
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "season": SEASON,
        "provider": provider,
        "collection_status": collection_status,
        "provider_error": provider_error,
        "configured_accounts": len(TWITTER_ACCOUNTS),
        "official_club_accounts": sum(1 for account in TWITTER_ACCOUNTS if account.get("team")),
        "successful_accounts": sum(1 for account in accounts if not account.get("error")),
        "total_tweets": len(tweets),
        "accounts": accounts,
        "tweets": tweets,
        **extra,
    }


def _http_error_message(exc: requests.RequestException) -> str:
    response = getattr(exc, "response", None)
    return f"X API HTTP {response.status_code}" if response is not None else "X API erişim hatası."


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
