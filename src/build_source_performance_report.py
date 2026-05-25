"""Measure transfer-news source performance against official announcements."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from src.analyze_news_with_claude import _club_key
from src.collect_news_telegram import TELEGRAM_CHANNELS
from src.collect_news_twitter import TWITTER_ACCOUNTS
from src.config import PROCESSED_DIR, SEASON
from src.html_utils import md_to_html, page_html
from src.normalization import normalize_name

OUTPUT_JSON = PROCESSED_DIR / f"source_performance_{SEASON}.json"
OUTPUT_MD = PROCESSED_DIR / f"source_performance_{SEASON}.md"
OUTPUT_HTML = PROCESSED_DIR / f"source_performance_{SEASON}.html"
HISTORY_JSON = PROCESSED_DIR / f"source_claim_history_{SEASON}.json"
MATURITY_DAYS = 14
TRACKED_X_TYPES = {"transfer_news", "secondary_signal"}
REPORTER_WATCH_QUERIES = {
    "Yağız Sabuncuoğlu": "Yağız Sabuncuoğlu transfer",
    "Ertan Süzgün": "Ertan Süzgün transfer",
    "Sports Digitale": "Sports Digitale transfer",
    "Yakın Takip": "Yakın Takip transfer",
    "Ekrem Konur": "Ekrem Konur Süper Lig transfer",
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Transfer haber kaynakları için teyit ve erken haber performansı üretir.")
    parser.add_argument("--input", default=str(PROCESSED_DIR / f"news_intelligence_{SEASON}.json"))
    parser.add_argument("--maturity-days", type=int, default=MATURITY_DAYS)
    args = parser.parse_args()

    intel = _load(Path(args.input))
    payload = build_report(
        intel,
        google=_load(PROCESSED_DIR / f"news_google_latest_{SEASON}.json"),
        telegram=_load(PROCESSED_DIR / f"news_telegram_latest_{SEASON}.json"),
        twitter=_load(PROCESSED_DIR / f"news_twitter_latest_{SEASON}.json"),
        history=_load(HISTORY_JSON),
        maturity_days=args.maturity_days,
    )
    history = payload.pop("_history")
    markdown = build_markdown(payload)
    HISTORY_JSON.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")
    OUTPUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    OUTPUT_MD.write_text(markdown, encoding="utf-8")
    OUTPUT_HTML.write_text(
        page_html("Erken Haber Kaynak Performansı", md_to_html(markdown)),
        encoding="utf-8",
    )
    print(f"Kaynak performansı: {payload['summary']['observed_sources']} gözlenen kaynak | {OUTPUT_HTML}")


def _load(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        try:
            return datetime.strptime(value, "%d.%m.%Y %H:%M:%S").replace(tzinfo=timezone.utc)
        except ValueError:
            return None


def _event_key(claim: dict) -> str | None:
    player = normalize_name(claim.get("player_name"))
    target = _club_key(claim.get("to_club"))
    if not player or not target:
        return None
    return f"{player}|{target}"


def _empty_row(source: str, source_tier: str, source_type: str | None = None) -> dict:
    return {
        "source": source,
        "source_tier": source_tier,
        "source_type": source_type,
        "observations": 0,
        "scoreable_claims": 0,
        "official_conversions": 0,
        "lead_hours": [],
        "lead_time_unavailable": 0,
        "matured_unconfirmed": 0,
        "pending_claims": 0,
        "unresolved_claims": 0,
        "status": "NO_DATA",
        "score": None,
    }


def build_report(
    intelligence: dict,
    google: dict | None = None,
    telegram: dict | None = None,
    twitter: dict | None = None,
    history: dict | None = None,
    *,
    now: datetime | None = None,
    maturity_days: int = MATURITY_DAYS,
) -> dict:
    generated = _timestamp(intelligence.get("generated_at"))
    reference_time = now or generated or datetime.now(timezone.utc)
    history = history or {}
    official_events: dict[str, datetime | None] = {
        row["event_key"]: _timestamp(row.get("official_at"))
        for row in history.get("official_events", [])
        if row.get("event_key")
    }
    for claim in intelligence.get("transfers", []):
        if claim.get("verification_status") != "OFFICIAL":
            continue
        key = _event_key(claim)
        if not key:
            continue
        times = [
            _timestamp(evidence.get("published_at"))
            for evidence in claim.get("evidence", [])
            if evidence.get("source_tier") == "OFFICIAL"
        ]
        known_times = [item for item in times if item]
        current_time = min(known_times) if known_times else None
        official_events[key] = current_time or official_events.get(key)
    official_total = len(official_events)
    official_with_time = sum(1 for value in official_events.values() if value)

    observations = {
        _observation_id(row): row for row in history.get("observations", []) if row.get("source")
    }
    for claim in intelligence.get("transfers", []):
        key = _event_key(claim)
        for evidence in claim.get("evidence", []):
            if evidence.get("source_tier") == "OFFICIAL":
                continue
            observation = {
                "source": evidence.get("source") or "Bilinmeyen kaynak",
                "source_tier": evidence.get("source_tier", "MEDIA"),
                "source_type": evidence.get("source_type"),
                "event_key": key,
                "player_name": claim.get("player_name"),
                "to_club": claim.get("to_club"),
                "published_at": evidence.get("published_at"),
                "title": evidence.get("title"),
                "link": evidence.get("link"),
            }
            observation_id = _observation_id(observation)
            previous = observations.get(observation_id)
            if not previous or (_timestamp(observation.get("published_at")) or reference_time) < (
                _timestamp(previous.get("published_at")) or reference_time
            ):
                observations[observation_id] = observation

    rows: dict[str, dict] = {}
    for observation in observations.values():
        source = observation["source"]
        key = observation.get("event_key")
        row = rows.setdefault(
            source,
            _empty_row(source, observation.get("source_tier", "MEDIA"), observation.get("source_type")),
        )
        row["observations"] += 1
        if not key:
            row["unresolved_claims"] += 1
            continue
        row["scoreable_claims"] += 1
        published = _timestamp(observation.get("published_at"))
        if key in official_events:
            row["official_conversions"] += 1
            official_time = official_events[key]
            if published and official_time and published <= official_time:
                row["lead_hours"].append(round((official_time - published).total_seconds() / 3600, 1))
            else:
                row["lead_time_unavailable"] += 1
        elif published and reference_time - published >= timedelta(days=maturity_days):
            row["matured_unconfirmed"] += 1
        else:
            row["pending_claims"] += 1

    twitter_status = (twitter or {}).get("collection_status", "NO_SNAPSHOT")
    telegram_status = (telegram or {}).get("collection_status", "NO_SNAPSHOT")
    for channel in TELEGRAM_CHANNELS:
        source = channel["name"]
        row = rows.setdefault(source, _empty_row(source, "SECONDARY", "telegram"))
        row["source_tier"] = "SECONDARY"
        row["source_type"] = "telegram"
        if not row["observations"]:
            row["status"] = "NO_TRANSFER_CLAIMS" if telegram_status == "SUCCESS" else "TELEGRAM_DATA_UNAVAILABLE"

    for account in TWITTER_ACCOUNTS:
        if account["type"] not in TRACKED_X_TYPES:
            continue
        source = f"@{account['handle']}"
        row = rows.setdefault(source, _empty_row(source, "SECONDARY", "twitter"))
        if not row["observations"] and twitter_status != "SUCCESS":
            row["status"] = "X_DATA_UNAVAILABLE"

    source_rows = [_finalize_row(row) for row in rows.values()]
    source_rows.sort(key=lambda row: (row["score"] is None, -(row["score"] or 0), -row["observations"], row["source"]))
    provider_rows = _provider_measurements(source_rows, google or {}, telegram_status, twitter_status)
    scored = [row for row in source_rows if row["score"] is not None]
    google_queries = {row.get("query"): row for row in (google or {}).get("queries", [])}
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "season": SEASON,
        "maturity_days": maturity_days,
        "summary": {
            "transfer_signals": intelligence.get("transfer_signals", 0),
            "official_events": official_total,
            "official_events_with_timestamp": official_with_time,
            "observed_sources": sum(1 for row in source_rows if row["observations"]),
            "scored_sources": len(scored),
            "measured_lead_times": sum(len(row["lead_hours"]) for row in source_rows),
            "tracked_x_sources_waiting": sum(1 for row in source_rows if row["status"] == "X_DATA_UNAVAILABLE"),
            "retained_claim_observations": len(observations),
        },
        "provider_coverage": {
            "google_news": {
                "articles": (google or {}).get("total_articles", 0),
                "queries": len((google or {}).get("queries", [])),
                "successful_queries": sum(1 for row in (google or {}).get("queries", []) if not row.get("error")),
            },
            "telegram": {
                "messages": (telegram or {}).get("total_messages", 0),
                "channels": (telegram or {}).get("total_channels", 0),
                "successful_channels": (telegram or {}).get("successful_channels", 0),
            },
            "twitter": {
                "status": twitter_status,
                "posts": (twitter or {}).get("total_tweets", 0),
                "configured_accounts": (twitter or {}).get("configured_accounts", 0),
            },
        },
        "provider_measurements": provider_rows,
        "sources": source_rows,
        "reporter_watch": [
            {
                "name": name,
                "google_query": query,
                "indexed_results": google_queries.get(query, {}).get("fetched", 0),
                "query_error": google_queries.get(query, {}).get("error"),
                "performance_status": "ATTRIBUTION_PENDING",
            }
            for name, query in REPORTER_WATCH_QUERIES.items()
        ],
        "_history": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "official_events": [
                {"event_key": key, "official_at": value.isoformat() if value else None}
                for key, value in official_events.items()
            ],
            "observations": list(observations.values()),
        },
    }


def _provider_measurements(source_rows: list[dict], google: dict, telegram_status: str, twitter_status: str) -> list[dict]:
    labels = {
        "media": "Google News / medya",
        "telegram": "Telegram",
        "twitter": "X",
    }
    aggregated = {kind: _empty_row(label, "CHANNEL", kind) for kind, label in labels.items()}
    for source in source_rows:
        kind = source.get("source_type")
        if kind in {"google_news", "rss"} or (not kind and source.get("source_tier") == "MEDIA"):
            kind = "media"
        row = aggregated.get(kind)
        if not row or not source["observations"]:
            continue
        for key in (
            "observations",
            "scoreable_claims",
            "official_conversions",
            "lead_time_unavailable",
            "matured_unconfirmed",
            "pending_claims",
            "unresolved_claims",
        ):
            row[key] += source[key]
        row["lead_hours"].extend(source["lead_hours"])
    if not aggregated["media"]["observations"] and google.get("total_articles"):
        aggregated["media"]["status"] = "NO_TRANSFER_CLAIMS"
    if not aggregated["telegram"]["observations"]:
        aggregated["telegram"]["status"] = (
            "NO_TRANSFER_CLAIMS" if telegram_status == "SUCCESS" else "TELEGRAM_DATA_UNAVAILABLE"
        )
    if not aggregated["twitter"]["observations"]:
        aggregated["twitter"]["status"] = (
            "NO_TRANSFER_CLAIMS" if twitter_status == "SUCCESS" else "X_DATA_UNAVAILABLE"
        )
    return [_finalize_row(row) for row in aggregated.values()]


def _observation_id(row: dict) -> str:
    return "|".join(
        str(value or "")
        for value in (row.get("source"), row.get("event_key"), row.get("link"), row.get("title"))
    )


def _finalize_row(row: dict) -> dict:
    completed = row["official_conversions"] + row["matured_unconfirmed"]
    lead = row["lead_hours"]
    row["average_lead_hours"] = round(sum(lead) / len(lead), 1) if lead else None
    row["official_conversion_rate_pct"] = (
        round(100 * row["official_conversions"] / row["scoreable_claims"], 1) if row["scoreable_claims"] else None
    )
    row["false_alarm_proxy_pct"] = (
        round(100 * row["matured_unconfirmed"] / completed, 1) if completed else None
    )
    if completed:
        precision = row["official_conversions"] / completed
        lead_bonus = min((row["average_lead_hours"] or 0) / 72, 1) * 20
        row["score"] = round(precision * 80 + lead_bonus, 1)
        row["status"] = "MEASURED" if lead else "PARTIAL_MEASUREMENT"
    elif row["observations"]:
        row["status"] = "OBSERVING"
    return row


def build_markdown(payload: dict) -> str:
    summary = payload["summary"]
    providers = payload["provider_coverage"]
    lines = [
        "# Erken Haber Kaynak Performansı",
        "",
        f"- Transfer sinyali: {summary['transfer_signals']}",
        f"- Resmi olaya dönüşen transfer: {summary['official_events']}",
        f"- Yayın zamanı bulunan resmi teyit: {summary['official_events_with_timestamp']}/{summary['official_events']}",
        f"- Ölçülen kaynak: {summary['scored_sources']} / gözlenen kaynak: {summary['observed_sources']}",
        f"- Hesaplanabilir erken haber süresi: {summary['measured_lead_times']}",
        f"- X verisi bekleyen izlenen kaynak: {summary['tracked_x_sources_waiting']}",
        f"- Defterde korunan ilk iddia gözlemi: {summary['retained_claim_observations']}",
        "",
        "## Kanal Kapsamı",
        "",
        f"- Google News: {providers['google_news']['articles']} haber, {providers['google_news']['successful_queries']}/{providers['google_news']['queries']} başarılı sorgu.",
        f"- Telegram: {providers['telegram']['messages']} mesaj, {providers['telegram']['successful_channels']}/{providers['telegram']['channels']} erişilebilir kanal.",
        f"- X: durum={providers['twitter']['status']}, gönderi={providers['twitter']['posts']}, yapılandırılmış hesap={providers['twitter']['configured_accounts']}.",
        "",
        "## Kanal Ölçümü",
        "",
        "| Kanal | Gözlem | Ölçülebilir İddia | Resmiye Dönüşen | Ort. Erken Saat | Vekil Yanlış Alarm | Skor | Durum |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in payload["provider_measurements"]:
        lines.append(
            "| {source} | {observations} | {scoreable} | {confirmed} | {lead} | {false_alarm} | {score} | {status} |".format(
                source=row["source"],
                observations=row["observations"],
                scoreable=row["scoreable_claims"],
                confirmed=row["official_conversions"],
                lead=_display(row["average_lead_hours"]),
                false_alarm=_percent(row["false_alarm_proxy_pct"]),
                score=_display(row["score"]),
                status=row["status"],
            )
        )
    lines.extend([
        "",
        "## Muhabir İzleme",
        "",
        "- Google News muhabir sorgusu, erken bulgu aramasıdır; haber başlığı veya kanıt kaydı muhabire açık atıf taşımadan isabet skoruna yazılmaz.",
        "",
        "| Muhabir / Ağ | Google Arama Bulgusu | Skor Durumu |",
        "|---|---:|---|",
    ])
    for row in payload["reporter_watch"]:
        lines.append(f"| {row['name']} | {row['indexed_results']} | {row['performance_status']} |")
    lines.extend([
        "",
        "## Skorlama Notu",
        "",
        f"- Resmi teyide dönüşüm, aynı oyuncu ve hedef kulüp için resmi kulüp duyurusu bulunduğunda sayılır.",
        f"- Erken haber saati yalnız hem ilk sinyal hem resmi duyuru zamanı varsa hesaplanır.",
        f"- Yanlış alarm vekili, {payload['maturity_days']} günden eski olup resmi teyide dönüşmemiş yönü belirli iddiadır; kesin yanlış bilgi hükmü değildir.",
        "",
        "## Kaynaklar",
        "",
        "| Kaynak | Katman | Gözlem | Ölçülebilir İddia | Resmiye Dönüşen | Ort. Erken Saat | Vekil Yanlış Alarm | Skor | Durum |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    for row in payload["sources"]:
        lines.append(
            "| {source} | {tier} | {observations} | {scoreable} | {confirmed} | {lead} | {false_alarm} | {score} | {status} |".format(
                source=str(row["source"]).replace("|", "/"),
                tier=row["source_tier"],
                observations=row["observations"],
                scoreable=row["scoreable_claims"],
                confirmed=row["official_conversions"],
                lead=_display(row["average_lead_hours"]),
                false_alarm=_percent(row["false_alarm_proxy_pct"]),
                score=_display(row["score"]),
                status=row["status"],
            )
        )
    return "\n".join(lines)


def _display(value) -> str:
    return "—" if value is None else str(value)


def _percent(value) -> str:
    return "—" if value is None else f"%{value}"


if __name__ == "__main__":
    main()
