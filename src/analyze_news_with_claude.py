"""
Haber makalelerini analiz eder.
Birincil: kural tabanlı Türkçe NER + sinyal çıkarımı (API key gerektirmez).
Opsiyonel: ANTHROPIC_API_KEY varsa Claude Haiku ile zenginleştirilmiş analiz.
Çıktı: transfer, sakat, cezalı, sözleşme, promosyon/küme düşme sinyalleri.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path

from src.config import PROCESSED_DIR, SEASON
from src.normalization import normalize_name

# ── Türkçe sinyal kalıpları ───────────────────────────────────────────────

TRANSFER_PATTERNS = [
    (r"transfer\s+(?:için\s+)?görüşm", "transfer_negotiation"),
    (r"bonservis(?:\s+bedeli)?", "transfer_fee"),
    (r"imzala(?:dı|yacak|yor)", "signing"),
    (r"anlaşm(?:a sağlandı|aya vardı|aya yakın)", "deal_close"),
    (r"teklif(?:\s+geldi|\s+yaptı|\s+sundu)", "offer"),
    (r"serbest\s+(?:bırakıldı|kalıyor|kalacak)", "free_agent"),
    (r"(?:ilgileniyor|peşinde|gözüne kestirdi)", "interest"),
    (r"ayrıl(?:ıyor|acak|dı|mak istiyor)", "departure"),
    (r"kiralandı|kiralık\s+(?:olarak\s+)?(?:gitti|geliyor|transfer)", "loan"),
    (r"süper\s+lig['']?e\s+(?:geliyor|transfer|dönüyor)", "super_lig_arrival"),
]

INJURY_PATTERNS = [
    (r"sakat(?:lık)?\s+(?:haberi|açıklaması|raporu)", "injury_report"),
    (r"(?:ameliyat|operasyon)\s+oldu", "surgery"),
    (r"kas\s+(?:zorlanması|yırtığı|sakatlığı)", "muscle_injury"),
    (r"(?:diz|ayak bilegi|omuz|hamstring)\s+sakatlığı", "specific_injury"),
    (r"antrenman\s+dışı\s+kald", "training_out"),
    (r"(?:2|3|4|5|6|7|8|[0-9]+)\s+hafta\s+yok", "weeks_out"),
    (r"sezon\s+(?:sonu|kapandı|bitti)", "season_ending"),
]

SUSPENSION_PATTERNS = [
    (r"kart\s+cezas(?:ı|ına)", "card_suspension"),
    (r"cezal(?:ı|ılar)\s+listesi", "suspension_list"),
    (r"(?:1|2|3)\s+maç\s+ceza", "match_ban"),
    (r"diskalifiye\s+edildi", "disqualified"),
    (r"ihraç\s+(?:edildi|cezası)", "expelled"),
]

PROMOTION_PATTERNS = [
    (r"süper\s+lig['']?e\s+(?:çıktı|yükseldi|çıkma|klasman)", "promoted"),
    (r"(?:tff\s+1\.\s+lig|birinci\s+lig)\s+(?:şampiyon|birinci)", "first_division_champion"),
    (r"playoff(?:'ı|\s+kazandı|\s+finali)", "playoff_win"),
    (r"küme\s+düş(?:tü|ücek|me)", "relegated"),
    (r"1\.\s+lig['']?e\s+(?:düştü|indi|gitti)", "relegated"),
]

CONTRACT_PATTERNS = [
    (r"sözleşme\s+(?:yeniledi|uzattı|imzaladı|yenilendi)", "renewal"),
    (r"sözleşme\s+(?:bitiyor|bitti|sona eriyor)", "expiry"),
    (r"(?:1|2|3)\s+yıllık\s+(?:sözleşme|anlaşma)", "new_contract"),
    (r"(?:bonussuz|ücretsiz|bedavaya)\s+transfer", "free_transfer"),
]

# ── Kulüp adı tespiti ─────────────────────────────────────────────────────

CLUB_PATTERNS = {
    "Beşiktaş": r"beşiktaş|bjk|siyah[-\s]beyaz",
    "Galatasaray": r"galatasaray|cim\s*bom|sarı[-\s]kırmızı",
    "Fenerbahçe": r"fenerbahçe|fenerbahce|fb|sarı[-\s]lacivert",
    "Trabzonspor": r"trabzonspor|karadeniz\s+fırtınası|bordo[-\s]mavi",
    "Başakşehir": r"başakşehir|basaksehir|medipol",
    "Alanyaspor": r"alanyaspor",
    "Samsunspor": r"samsunspor",
    "Göztepe": r"göztepe|goztepe",
    "Konyaspor": r"konyaspor",
    "Rizespor": r"rizespor",
    "Gaziantep FK": r"gaziantep\s*(?:fk|futbol)",
    "Kasımpaşa": r"kasımpaşa|kasimpasa",
    "Kocaelispor": r"kocaelispor",
    "Eyüpspor": r"eyüpspor|eyupspor",
    "Gençlerbirliği": r"gençlerbirliği|genclerbirligi",
    "Karagümrük": r"karagümrük|karagumruk",
    "Antalyaspor": r"antalyaspor",
    "Kayserispor": r"kayserispor",
    # Yükselen takımlar
    "Çorumspor": r"çorumspor|corumspor",
    "Adanaspor": r"adanaspor",
    "Sakaryaspor": r"sakaryaspor",
    "Bodrumspor": r"bodrum\s*spor",
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Haber makalelerini analiz eder (kural tabanlı + opsiyonel Claude).")
    parser.add_argument("--input", default=str(PROCESSED_DIR / f"news_rss_latest_{SEASON}.json"))
    parser.add_argument("--twitter-input", default=str(PROCESSED_DIR / f"news_twitter_latest_{SEASON}.json"))
    parser.add_argument("--output-prefix", default=f"news_intelligence_{SEASON}")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--skip-analyzed", action="store_true", default=True)
    parser.add_argument("--no-skip-analyzed", dest="skip_analyzed", action="store_false")
    parser.add_argument("--only-relevant", action="store_true")
    parser.add_argument("--delay-seconds", type=float, default=0.5)
    args = parser.parse_args()

    # Claude API mevcut mu kontrol et
    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    claude_client = None
    if api_key and not api_key.startswith("sk-ant-..."):
        try:
            import anthropic
            claude_client = anthropic.Anthropic(api_key=api_key)
            # Bağlantı testi
            claude_client.messages.create(
                model="claude-haiku-4-5-20251001", max_tokens=5,
                messages=[{"role": "user", "content": "ok"}]
            )
            print("Claude API: bağlı (zenginleştirilmiş analiz aktif)")
        except Exception:  # noqa: BLE001
            claude_client = None
            print("Claude API: devre dışı (kural tabanlı analiz)")
    else:
        print("Claude API: devre dışı (kural tabanlı analiz)")

    # Tüm kaynakları birleştir (RSS + Twitter)
    articles = _load_articles(args.input, args.twitter_input)

    if args.only_relevant:
        articles = [a for a in articles if a.get("super_lig_relevant")]
    if args.skip_analyzed:
        articles = [a for a in articles if not a.get("analyzed")]
    if args.limit:
        articles = articles[:args.limit]

    print(f"Analiz edilecek: {len(articles)} makale/tweet")

    player_index = _build_player_index()
    print(f"Oyuncu veritabanı: {len(player_index)} oyuncu")

    analyzed = []
    for i, article in enumerate(articles, 1):
        if i % 20 == 0:
            print(f"  [{i}/{len(articles)}]...")

        # Kural tabanlı analiz (her zaman çalışır)
        analysis = rule_based_analyze(article, player_index)

        # Claude zenginleştirmesi (API key varsa, sadece Süper Lig haberleri için)
        if claude_client and article.get("super_lig_relevant") and len(article.get("title", "")) > 20:
            try:
                claude_result = _claude_enhance(claude_client, article)
                if claude_result:
                    analysis = _merge_analyses(analysis, claude_result)
            except Exception:  # noqa: BLE001
                pass
            time.sleep(args.delay_seconds)

        article["claude_analysis"] = analysis
        article["analyzed"] = True
        article["analyzed_at"] = datetime.now(timezone.utc).isoformat()
        analyzed.append(article)

    # Tüm verileri birleştirip intelligence çıktısı üret
    intelligence = build_intelligence(analyzed, player_index)
    intel_path = PROCESSED_DIR / f"{args.output_prefix}.json"
    intel_path.write_text(json.dumps(intelligence, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\nTamamlandı: {len(analyzed)} analiz")
    print(f"  Transfer sinyali: {intelligence['transfer_signals']}")
    print(f"  Sakat sinyali: {intelligence['injury_signals']}")
    print(f"  Cezalı sinyali: {intelligence['suspension_signals']}")
    print(f"  Promosyon/küme düşme: {intelligence['promotion_signals']}")
    print(f"İstihbarat: {intel_path}")


def rule_based_analyze(article: dict, player_index: dict) -> dict:
    title = article.get("title", "")
    summary = article.get("summary", "") or article.get("full_text", "")[:500]
    text = f"{title} {summary}".lower()
    title_text = title.lower()
    text_orig = f"{title} {summary}"

    news_types = list(article.get("categories", []))
    players = []
    transfer_rumors = []
    injuries = []
    suspensions = []
    promotions = []
    contracts = []

    # Kulüp tespiti
    mentioned_clubs = []
    for club, pattern in CLUB_PATTERNS.items():
        if re.search(pattern, text, re.IGNORECASE):
            mentioned_clubs.append(club)
    title_clubs = [
        club for club, pattern in CLUB_PATTERNS.items()
        if re.search(pattern, title_text, re.IGNORECASE)
    ]

    # Oyuncu tespiti — veritabanı üzerinden
    mentioned_players = []
    for norm_name, player in player_index.items():
        name = player.get("name", "")
        if not name or len(name) < 4:
            continue
        # İlk isim + soyisim kombinasyonunu dene
        parts = name.split()
        if len(parts) >= 2:
            # Soyisim (son parça) metin içinde geçiyor mu?
            last = parts[-1].lower()
            if len(last) >= 4 and last in text:
                # İlk isim de geçiyorsa HIGH, sadece soyisim MEDIUM
                first = parts[0].lower()
                if first in text:
                    conf = "HIGH"
                    full = name
                else:
                    conf = "MEDIUM"
                    full = name
                mentioned_players.append({
                    "name": full,
                    "normalized": norm_name,
                    "current_club": player.get("club"),
                    "age": player.get("age"),
                    "tm_market_value_eur": player.get("tm_market_value_eur"),
                    "tff_external_id": player.get("external_id"),
                    "confidence": conf,
                    "matched_in_title": last in title_text and first in title_text,
                })

    # Deduplicate players
    seen_norms = set()
    for p in mentioned_players:
        if p["normalized"] not in seen_norms:
            seen_norms.add(p["normalized"])
            players.append(p)

    # Transfer sinyalleri
    for pattern, signal_type in TRANSFER_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            if "transfer" not in news_types:
                news_types.append("transfer")
            transfer_players = [player for player in players if player.get("matched_in_title")]
            candidate_clubs = list(title_clubs)
            if article.get("account_type") == "official" and article.get("related_team"):
                candidate_clubs.append(article["related_team"])
            for p in transfer_players[:2]:
                if p.get("confidence") in ("HIGH", "MEDIUM"):
                    to_club = _distinct_target_club(p.get("current_club"), candidate_clubs)
                    transfer_rumors.append({
                        "player_name": p["name"],
                        "from_club": p.get("current_club"),
                        "to_club": to_club,
                        "transfer_type": "loan" if "kiralık" in text else "permanent",
                        "window": _detect_window(text),
                        "signal_type": signal_type,
                        "confidence": p["confidence"],
                        "tm_market_value_eur": p.get("tm_market_value_eur"),
                        "direction_quality": "TARGET_IDENTIFIED" if to_club else "TARGET_UNRESOLVED",
                    })
            if not transfer_players and candidate_clubs:
                to_club = candidate_clubs[-1] if len(candidate_clubs) > 1 else candidate_clubs[0]
                transfer_rumors.append({
                    "player_name": None,
                    "from_club": candidate_clubs[0] if len(candidate_clubs) > 1 else None,
                    "to_club": to_club,
                    "signal_type": signal_type,
                    "window": _detect_window(text),
                    "confidence": "LOW",
                    "direction_quality": "PLAYER_UNRESOLVED",
                })
            break

    # Sakat sinyalleri
    for pattern, inj_type in INJURY_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            if "injury" not in news_types:
                news_types.append("injury")
            weeks_match = re.search(r"(\d+)\s+hafta", text)
            for p in players[:2]:
                injuries.append({
                    "player_name": p["name"],
                    "club": p.get("current_club") or (mentioned_clubs[0] if mentioned_clubs else None),
                    "injury_type": inj_type,
                    "estimated_weeks_out": int(weeks_match.group(1)) if weeks_match else None,
                    "confidence": p["confidence"],
                    "tm_market_value_eur": p.get("tm_market_value_eur"),
                })
            break

    # Cezalı sinyalleri
    for pattern, sus_type in SUSPENSION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            if "suspension" not in news_types:
                news_types.append("suspension")
            match_match = re.search(r"(\d+)\s+maç\s+ceza", text)
            for p in players[:2]:
                suspensions.append({
                    "player_name": p["name"],
                    "club": p.get("current_club") or (mentioned_clubs[0] if mentioned_clubs else None),
                    "reason": sus_type,
                    "matches_missed": int(match_match.group(1)) if match_match else None,
                    "confidence": p["confidence"],
                })
            break

    # Promosyon/küme düşme sinyalleri
    for pattern, promo_type in PROMOTION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            if "promotion_relegation" not in news_types:
                news_types.append("promotion_relegation")
            club_mention = mentioned_clubs[0] if mentioned_clubs else _extract_team_name(text_orig)
            promotions.append({
                "club": club_mention,
                "event_type": promo_type,
                "detail": title[:150],
                "confidence": "HIGH" if mentioned_clubs else "MEDIUM",
            })
            break

    # Sözleşme sinyalleri
    for pattern, cont_type in CONTRACT_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            if "contract" not in news_types:
                news_types.append("contract")
            for p in players[:2]:
                contracts.append({
                    "player_name": p["name"],
                    "club": p.get("current_club") or (mentioned_clubs[0] if mentioned_clubs else None),
                    "event_type": cont_type,
                    "confidence": p["confidence"],
                })
            break

    return {
        "news_types": _unique_in_order(news_types) or ["general"],
        "super_lig_relevant": bool(mentioned_clubs or mentioned_players),
        "mentioned_clubs": mentioned_clubs,
        "players": players[:5],
        "transfer_rumors": transfer_rumors[:3],
        "injuries": injuries[:3],
        "suspensions": suspensions[:3],
        "promotions": promotions[:2],
        "contracts": contracts[:3],
        "analysis_method": "rule_based",
        "summary_tr": "",
        "tags": _unique_in_order(mentioned_clubs + news_types, limit=8),
    }


def _detect_window(text: str) -> str:
    if "ocak" in text or "kış" in text or "winter" in text:
        return "winter_2027"
    if "yaz" in text or "haziran" in text or "temmuz" in text or "ağustos" in text:
        return "summer_2026"
    return "summer_2026"


def _extract_team_name(text: str) -> str | None:
    for club, pattern in CLUB_PATTERNS.items():
        if re.search(pattern, text, re.IGNORECASE):
            return club
    return None


def _unique_in_order(values: list[str], limit: int | None = None) -> list[str]:
    unique = list(dict.fromkeys(values))
    return unique[:limit] if limit is not None else unique


def _club_key(name: str | None) -> str:
    key = normalize_name(name)
    for suffix in (" A S", " FUTBOL KULUBU", " S K", " FK"):
        key = key.replace(suffix, "")
    return key.strip()


def _same_club(left: str | None, right: str | None) -> bool:
    left_key = _club_key(left)
    right_key = _club_key(right)
    if not left_key or not right_key:
        return False
    return left_key == right_key or left_key.startswith(f"{right_key} ") or right_key.startswith(f"{left_key} ")


def _distinct_target_club(current_club: str | None, candidates: list[str]) -> str | None:
    for club in candidates:
        if club and not _same_club(current_club, club):
            return club
    return None


def _claude_enhance(client, article: dict) -> dict | None:
    """Claude API ile kural tabanlı analizi zenginleştirir."""
    SYSTEM = "Sen Türk futbol analistsin. Haber özetini JSON olarak çıkar. Sadece JSON döndür."
    PROMPT = f"""Başlık: {article.get('title','')[:200]}
Özet: {article.get('summary','')[:400]}

JSON döndür (boşsa [] veya null):
{{"summary_tr": "1 cümle özet Türkçe", "tags": ["takım/konu etiketleri"], "confidence_boost": "HIGH|MEDIUM|LOW"}}"""

    try:
        msg = client.messages.create(
            model="claude-haiku-4-5-20251001", max_tokens=256,
            system=SYSTEM, messages=[{"role": "user", "content": PROMPT}]
        )
        raw = msg.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw.strip())
    except Exception:  # noqa: BLE001
        return None


def _merge_analyses(rule_result: dict, claude_result: dict) -> dict:
    merged = dict(rule_result)
    if claude_result.get("summary_tr"):
        merged["summary_tr"] = claude_result["summary_tr"]
    if claude_result.get("tags"):
        merged["tags"] = _unique_in_order(merged.get("tags", []) + claude_result.get("tags", []), limit=10)
    merged["analysis_method"] = "rule_based+claude"
    return merged


def _load_articles(rss_path_str: str, twitter_path_str: str) -> list[dict]:
    articles = []
    rss_path = Path(rss_path_str)
    if rss_path.exists():
        payload = json.loads(rss_path.read_text(encoding="utf-8"))
        articles.extend(payload.get("articles", []))

    twitter_path = Path(twitter_path_str)
    if twitter_path.exists():
        payload = json.loads(twitter_path.read_text(encoding="utf-8"))
        articles.extend(payload.get("tweets", []))

    return articles


def _build_player_index() -> dict[str, dict]:
    enriched_path = PROCESSED_DIR / f"tff_player_profiles_enriched_{SEASON}.json"
    all_path = PROCESSED_DIR / f"tff_player_profiles_all_priority_{SEASON}.json"

    players: dict[str, dict] = {}

    def load_and_merge(path: Path) -> None:
        if not path.exists():
            return
        for p in json.loads(path.read_text(encoding="utf-8")):
            name = p.get("name", "")
            if not name:
                continue
            norm = normalize_name(name)
            if norm:
                existing = players.get(norm, {})
                players[norm] = {**existing, **{k: v for k, v in p.items() if v is not None}}

    load_and_merge(all_path)
    load_and_merge(enriched_path)
    return players


def build_intelligence(articles: list[dict], player_index: dict) -> dict:
    transfer_mentions, injuries, suspensions, promotions, player_news = [], [], [], [], []

    for a in articles:
        ca = a.get("claude_analysis") or {}
        meta = {
            "article_id": a["article_id"],
            "title": a["title"],
            "link": a["link"],
            "source": a["source_name"],
            "source_type": a.get("source_type", "rss"),
            "account_type": a.get("account_type"),
            "source_tier": _source_tier(a),
            "published_at": a.get("published_at"),
            "summary_tr": ca.get("summary_tr", a.get("summary", ""))[:200],
        }

        for tr in ca.get("transfer_rumors", []):
            if tr.get("player_name") or tr.get("to_club"):
                transfer_mentions.append({**tr, **meta})
        for inj in ca.get("injuries", []):
            injuries.append({**inj, **meta})
        for sus in ca.get("suspensions", []):
            suspensions.append({**sus, **meta})
        for promo in ca.get("promotions", []):
            promotions.append({**promo, **meta})
        for p in ca.get("players", []):
            if p.get("name"):
                player_news.append({**p, **meta})

    transfers = _aggregate_transfer_mentions(transfer_mentions)
    conf_ord = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    injuries.sort(key=lambda x: conf_ord.get(x.get("confidence", "LOW"), 2))

    recent = sorted(
        [a for a in articles if a.get("super_lig_relevant") or a.get("source_type") == "twitter"],
        key=lambda a: a.get("published_at") or "",
        reverse=True,
    )

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "season": SEASON,
        "total_articles": len(articles),
        "analyzed_articles": len([a for a in articles if a.get("analyzed")]),
        "transfer_signals": len(transfers),
        "raw_transfer_mentions": len(transfer_mentions),
        "transfer_status_counts": _status_counts(transfers),
        "injury_signals": len(injuries),
        "suspension_signals": len(suspensions),
        "promotion_signals": len(promotions),
        "player_mentions": len(player_news),
        "transfers": transfers[:50],
        "injuries": injuries[:30],
        "suspensions": suspensions[:30],
        "promotions": promotions[:20],
        "player_news": player_news[:100],
        "recent_articles": [
            {
                "article_id": a["article_id"],
                "title": a["title"],
                "link": a["link"],
                "source": a["source_name"],
                "source_type": a.get("source_type", "rss"),
                "published_at": a.get("published_at"),
                "categories": a.get("categories", []),
                "super_lig_relevant": a.get("super_lig_relevant"),
                "summary_tr": (a.get("claude_analysis") or {}).get("summary_tr", a.get("summary", ""))[:200],
                "tags": (a.get("claude_analysis") or {}).get("tags", a.get("categories", [])),
                "mentioned_clubs": (a.get("claude_analysis") or {}).get("mentioned_clubs", []),
            }
            for a in recent[:80]
        ],
    }


def _source_tier(article: dict) -> str:
    if article.get("source_type") == "twitter":
        return {
            "official": "OFFICIAL",
            "secondary_signal": "SECONDARY",
            "transfer_news": "SECONDARY",
            "media": "MEDIA",
        }.get(article.get("account_type"), "SECONDARY")
    if article.get("source_name") == "Anadolu Ajansı Spor":
        return "AGENCY"
    return "MEDIA"


def _aggregate_transfer_mentions(mentions: list[dict]) -> list[dict]:
    grouped: dict[tuple[str, str, str, str], list[dict]] = {}
    for mention in mentions:
        normalized = dict(mention)
        if _same_club(normalized.get("from_club"), normalized.get("to_club")):
            normalized["to_club"] = None
            normalized["direction_quality"] = "TARGET_MATCHES_CURRENT_CLUB"
        player_key = normalize_name(normalized.get("player_name")) or f"ARTICLE:{normalized.get('article_id')}"
        key = (
            player_key,
            _club_key(normalized.get("from_club")),
            _club_key(normalized.get("to_club")),
            normalized.get("signal_type") or "unknown",
        )
        grouped.setdefault(key, []).append(normalized)

    claims = [_build_transfer_claim(rows) for rows in grouped.values()]
    status_order = {"OFFICIAL": 0, "CORROBORATED": 1, "RUMOR": 2, "REVIEW_REQUIRED": 3}
    claims.sort(key=lambda row: row.get("published_at") or "", reverse=True)
    claims.sort(key=lambda row: status_order.get(row["verification_status"], 9))
    return claims


def _build_transfer_claim(rows: list[dict]) -> dict:
    rows = sorted(rows, key=lambda row: row.get("published_at") or "", reverse=True)
    head = dict(rows[0])
    distinct_sources = list(dict.fromkeys(row.get("source", "?") for row in rows))
    evidence = [
        {
            "source": row.get("source"),
            "source_tier": row.get("source_tier"),
            "title": row.get("title"),
            "link": row.get("link"),
            "published_at": row.get("published_at"),
        }
        for row in rows
    ]
    official = any(row.get("source_tier") == "OFFICIAL" for row in rows)
    has_direction = bool(head.get("player_name") and head.get("to_club"))

    if not has_direction:
        status = "REVIEW_REQUIRED"
        interpretation = "Oyuncu veya hedef kulüp net doğrulanamadı; transfer önerisine giremez."
    elif official:
        status = "OFFICIAL"
        interpretation = "Resmi hesap duyurusu bulundu; işlem resmi transfer bağlamında izlenebilir."
    elif len(distinct_sources) >= 2:
        status = "CORROBORATED"
        interpretation = "Birden fazla kaynak aynı yönlü iddiayı taşıyor; resmi açıklama beklenir."
    else:
        status = "RUMOR"
        interpretation = "Tek kaynaklı transfer iddiası; yalnız transfer radarında izlenir."

    status_confidence = {
        "OFFICIAL": "HIGH",
        "CORROBORATED": "MEDIUM",
        "RUMOR": "LOW",
        "REVIEW_REQUIRED": "LOW",
    }
    head.update(
        {
            "entity_confidence": max(
                (row.get("confidence", "LOW") for row in rows),
                key={"LOW": 0, "MEDIUM": 1, "HIGH": 2}.get,
            ),
            "confidence": status_confidence[status],
            "verification_status": status,
            "interpretation": interpretation,
            "source_count": len(distinct_sources),
            "sources": distinct_sources,
            "evidence": evidence,
            "model_use": status == "OFFICIAL",
        }
    )
    return head


def _status_counts(transfers: list[dict]) -> dict[str, int]:
    counts = {"OFFICIAL": 0, "CORROBORATED": 0, "RUMOR": 0, "REVIEW_REQUIRED": 0}
    for row in transfers:
        status = row.get("verification_status", "REVIEW_REQUIRED")
        counts[status] = counts.get(status, 0) + 1
    return counts


if __name__ == "__main__":
    main()
