from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from src.config import PROCESSED_DIR
from src.generate_match_preview import parse_tff_datetime
from src.normalization import normalize_matches


def main() -> None:
    parser = argparse.ArgumentParser(description="Kartlardan ve manuel dosyadan mac bazli oyuncu uygunluk raporu uretir.")
    parser.add_argument("--matches", default=str(PROCESSED_DIR / "tff_trendyol_super_lig_2025_2026_matches.json"))
    parser.add_argument("--team", default="BEŞİKTAŞ A.Ş.")
    parser.add_argument("--all-teams", action="store_true", help="Tüm Süper Lig takımları için ayrı ayrı + birleşik lig raporu üretir.")
    parser.add_argument("--manual", default="data/manual/player_availability_overrides.json")
    parser.add_argument("--news-context", default=str(PROCESSED_DIR / "news_context_snapshot_2025_2026.json"))
    parser.add_argument("--news-intelligence", default=str(PROCESSED_DIR / "news_intelligence_2025_2026.json"))
    parser.add_argument("--output-prefix", default="player_availability_besiktas_2025_2026")
    args = parser.parse_args()

    matches = normalize_matches(json.loads(Path(args.matches).read_text(encoding="utf-8")))
    news_context = load_news_context(Path(args.news_context))
    news_intel = load_news_context(Path(args.news_intelligence))

    if args.all_teams:
        build_all_teams(matches, Path(args.manual), news_context, news_intel)
        return

    availability = build_availability(matches, args.team, Path(args.manual), news_context, news_intel)

    json_path = PROCESSED_DIR / f"{args.output_prefix}.json"
    md_path = PROCESSED_DIR / f"{args.output_prefix}.md"
    json_path.write_text(json.dumps(availability, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(build_markdown(availability), encoding="utf-8")
    print(md_path.read_text(encoding="utf-8"))


def build_all_teams(matches: list[dict], manual_path: Path, news_context: dict | None, news_intel: dict | None) -> None:
    """Her Süper Lig takımı için ayrı bir availability dosyası + tek bir birleşik
    lig dosyası üretir. Beşiktaş'a özel `--team` akışıyla aynı `build_availability`
    mantığını kullanır, sadece 21 takımın hepsi için döngüye sokar."""
    from src.generate_preview_batch import ALL_TEAMS, team_slug

    league_summary = {
        "teams": 0,
        "matches_with_unavailable": 0,
        "auto_suspension_entries": 0,
        "manual_entries": 0,
        "news_context_entries": 0,
        "news_intelligence_entries": 0,
    }
    teams_payload = {}
    for team in ALL_TEAMS:
        availability = build_availability(matches, team, manual_path, news_context, news_intel)
        slug = team_slug(team)
        json_path = PROCESSED_DIR / f"player_availability_{slug}_2025_2026.json"
        md_path = PROCESSED_DIR / f"player_availability_{slug}_2025_2026.md"
        json_path.write_text(json.dumps(availability, ensure_ascii=False, indent=2), encoding="utf-8")
        md_path.write_text(build_markdown(availability), encoding="utf-8")

        summary = availability["summary"]
        teams_payload[team] = {"slug": slug, "summary": summary, "json_path": str(json_path)}
        league_summary["teams"] += 1
        for key in ("matches_with_unavailable", "auto_suspension_entries", "manual_entries",
                    "news_context_entries", "news_intelligence_entries"):
            league_summary[key] += summary.get(key, 0)
        print(f"[{team}] maç={summary['matches']} eksik-sinyalli-maç={summary['matches_with_unavailable']}")

    combined = {
        "season": "2025-2026",
        "league_summary": league_summary,
        "teams": teams_payload,
    }
    combined_path = PROCESSED_DIR / "player_availability_superlig_2025_2026.json"
    combined_path.write_text(json.dumps(combined, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Birleşik lig raporu kaydedildi: {combined_path} ({league_summary['teams']} takım)")


def build_availability(matches: list[dict], team: str, manual_path: Path, news_context: dict | None = None, news_intel: dict | None = None) -> dict:
    team_matches = [
        match
        for match in matches
        if match["home_team"]["name"] == team or match["away_team"]["name"] == team
    ]
    team_matches.sort(key=lambda match: parse_tff_datetime(match["match_date"]))

    manual_entries = load_manual_entries(manual_path)
    manual_by_match = {}
    for entry in manual_entries:
        # entry["team"] yoksa (eski kayıt) geriye dönük uyumluluk için dahil et; varsa
        # yalnızca o takıma ait maçlarda kullan — aksi halde aynı match_id'yi paylaşan
        # rakip takımın raporunda da bu oyuncu "eksik" görünür.
        if entry.get("team") and entry["team"] != team:
            continue
        manual_by_match.setdefault(entry["match_id"], []).append(entry)

    yellow_count = Counter()
    pending_next_match = []
    match_reports = []
    for match in team_matches:
        match_id = match["external_id"]
        side = "home" if match["home_team"]["name"] == team else "away"
        unavailable = []
        unavailable.extend(pending_next_match)
        unavailable.extend(manual_by_match.get(match_id, []))
        unavailable = dedupe_entries(unavailable)
        match_reports.append(
            {
                "match_id": match_id,
                "date": match["match_date"],
                "fixture": f"{match['home_team']['name']} - {match['away_team']['name']}",
                "team": team,
                "unavailable": unavailable,
                "suspended": [item for item in unavailable if item["status"] == "SUSPENDED"],
                "injured": [item for item in unavailable if item["status"] == "INJURED"],
            }
        )

        pending_next_match = []
        for card in match["cards"][side]:
            player_id = card.get("player_external_id")
            player_name = card.get("player_name")
            card_type = card.get("type")
            if not player_id:
                continue
            if card_type in {"Kırmızı Kart", "Çift Sarı Kart"}:
                pending_next_match.append(
                    card_entry(player_id, player_name, "SUSPENDED", f"{card_type} sonrası otomatik 1 maç ceza varsayımı", "AUTO_CARD_RED", "MEDIUM")
                )
            if card_type == "Sarı Kart":
                yellow_count[player_id] += 1
                if yellow_count[player_id] % 4 == 0:
                    pending_next_match.append(
                        card_entry(player_id, player_name, "SUSPENDED", f"{yellow_count[player_id]}. sarı kart sonrası 1 maç ceza varsayımı", "AUTO_YELLOW_ACCUMULATION", "LOW")
                    )

    news_entries = news_unavailability_for_team(news_context, team)
    intel_entries = news_intel_unavailability_for_team(news_intel, team)
    combined_news = _merge_news_entries(news_entries, intel_entries)
    team_manual_entries = sum(1 for entry in manual_entries if not entry.get("team") or entry["team"] == team)
    summary = {
        "matches": len(match_reports),
        "matches_with_unavailable": sum(1 for item in match_reports if item["unavailable"]),
        "auto_suspension_entries": sum(1 for item in match_reports for entry in item["unavailable"] if entry["source"].startswith("AUTO")),
        "manual_entries": team_manual_entries,
        "news_context_entries": len(news_entries),
        "news_intelligence_entries": len(intel_entries),
    }
    return {
        "team": team,
        "season": "2025-2026",
        "summary": summary,
        "rules_note": "Kırmızı/çift sarı için sonraki maç cezası varsayılır. Sarı kart birikimi 4 kartta 1 maç varsayımıdır; resmi ceza listesiyle doğrulanmalıdır.",
        "current_news_context_unavailability": combined_news,
        "matches": match_reports,
    }


def card_entry(player_id: str, player_name: str | None, status: str, reason: str, source: str, confidence: str) -> dict:
    return {
        "player_external_id": player_id,
        "player_name": player_name,
        "status": status,
        "reason": reason,
        "source": source,
        "confidence": confidence,
    }


def load_manual_entries(path: Path) -> list[dict]:
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload.get("entries", [])


def load_news_context(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


# Haber kaynakları (beIN galerisi vb.) takımı kısa/serbest Türkçe adla yazıyor
# ("Beşiktaş", "Başakşehir"), ALL_TEAMS ise tüzel/tam ad kullanıyor ("BEŞİKTAŞ A.Ş.",
# "RAMS BAŞAKŞEHİR FUTBOL KULÜBÜ"). 2026-09-11 bulgusu: eski kod bu farkı yalnızca
# Beşiktaş için hardcode edilmiş {"beşiktaş","besiktas"} alias'ıyla kapatıyordu — lig
# geneline açılınca bu, HER takımın raporuna Beşiktaş sinyallerini de bulaştırırdı.
TEAM_MEDIA_ALIASES: dict[str, tuple[str, ...]] = {
    "BEŞİKTAŞ A.Ş.": ("beşiktaş", "besiktas"),
    "GALATASARAY A.Ş.": ("galatasaray",),
    "FENERBAHÇE A.Ş.": ("fenerbahçe", "fenerbahce"),
    "TRABZONSPOR A.Ş.": ("trabzonspor",),
    "RAMS BAŞAKŞEHİR FUTBOL KULÜBÜ": ("başakşehir", "basaksehir"),
    "CORENDON ALANYASPOR": ("alanyaspor",),
    "SAMSUNSPOR A.Ş.": ("samsunspor",),
    "GÖZTEPE A.Ş.": ("göztepe", "goztepe"),
    "TÜMOSAN KONYASPOR": ("konyaspor",),
    "ÇAYKUR RİZESPOR A.Ş.": ("rizespor",),
    "GAZİANTEP FUTBOL KULÜBÜ A.Ş.": ("gaziantep",),
    "KASIMPAŞA A.Ş.": ("kasımpaşa", "kasimpasa"),
    "KOCAELİSPOR": ("kocaelispor",),
    "İKAS EYÜPSPOR": ("eyüpspor", "eyupspor"),
    "GENÇLERBİRLİĞİ": ("gençlerbirliği", "genclerbirligi"),
    "MISIRLI.COM.TR FATİH KARAGÜMRÜK": ("fatih karagümrük", "karagümrük", "karagumruk"),
    "HESAP.COM ANTALYASPOR": ("antalyaspor",),
    "ZECORNER KAYSERİSPOR": ("kayserispor",),
    "ÇORUM FK": ("çorum fk", "çorumspor", "çorum"),
    "ERZURUMSPOR FK": ("erzurumspor",),
    "AMED SFK": ("amed sfk", "amedspor", "amed"),
}


def _team_media_aliases(team: str) -> set[str]:
    return {team.casefold(), *TEAM_MEDIA_ALIASES.get(team, ())}


def news_unavailability_for_team(news_context: dict | None, team: str) -> list[dict]:
    if not news_context:
        return []
    aliases = _team_media_aliases(team)
    output = []
    for item in news_context.get("team_unavailability", []):
        item_team = (item.get("team") or "").casefold()
        if not item_team:
            continue
        if not any(alias == item_team or (len(alias) >= 4 and alias in item_team) for alias in aliases):
            continue
        output.append(
            {
                "player_external_id": None,
                "player_name": item.get("player_name"),
                "status": item.get("status"),
                "reason": "Güncel haber/sakat-cezalı bağlam sinyali",
                "source": item.get("source"),
                "confidence": item.get("confidence"),
                "url": item.get("url"),
            }
        )
    return output


def news_intel_unavailability_for_team(news_intel: dict | None, team: str) -> list[dict]:
    """Reads structured injury/suspension signals from news_intelligence output.

    2026-09-11 bulgusu: bu fonksiyon `signal.get("team")` ve `signal.get("player")`
    okuyordu ama `analyze_news_with_claude.py`'nin ürettiği gerçek şema `club` ve
    `player_name` kullanıyor. Sonuç: `signal_team` her zaman boş string oluyordu ve
    boş string her takım adının substring'i olduğu için TÜM sinyaller (ilgisiz
    kulüplerinkiler dahil) hangi takım sorgulanırsa ona atanıyordu.
    """
    if not news_intel:
        return []
    team_cf = team.casefold()
    output = []
    for signal in news_intel.get("injuries", []):
        club = (signal.get("club") or "").casefold()
        if club != team_cf:
            continue
        output.append({
            "player_external_id": None,
            "player_name": signal.get("player_name"),
            "status": "INJURED",
            "reason": "Haber istihbaratı sakat sinyali",
            "source": "news_intelligence",
            "confidence": signal.get("confidence", "MEDIUM"),
            "detail": signal.get("injury_type"),
        })
    for signal in news_intel.get("suspensions", []):
        club = (signal.get("club") or "").casefold()
        if club != team_cf:
            continue
        output.append({
            "player_external_id": None,
            "player_name": signal.get("player_name"),
            "status": "SUSPENDED",
            "reason": "Haber istihbaratı cezalı sinyali",
            "source": "news_intelligence",
            "confidence": signal.get("confidence", "MEDIUM"),
            "detail": signal.get("reason"),
        })
    return output


def _merge_news_entries(news_context_entries: list[dict], intel_entries: list[dict]) -> list[dict]:
    """Merge two news entry lists, deduplicating by player name + status."""
    seen_names: set[tuple] = set()
    merged = []
    for entry in news_context_entries + intel_entries:
        key = (
            (entry.get("player_name") or "").casefold(),
            entry.get("status"),
        )
        if key in seen_names:
            continue
        seen_names.add(key)
        merged.append(entry)
    return merged


def dedupe_entries(entries: list[dict]) -> list[dict]:
    seen = set()
    output = []
    for entry in entries:
        key = (entry.get("player_external_id"), entry.get("status"), entry.get("source"))
        if key in seen:
            continue
        seen.add(key)
        output.append(entry)
    return output


def build_markdown(payload: dict) -> str:
    summary = payload["summary"]
    lines = [
        "# Oyuncu Uygunluk / Eksik Listesi",
        "",
        f"- Takım: {payload['team']}",
        f"- Maç: {summary['matches']}",
        f"- Eksik sinyali olan maç: {summary['matches_with_unavailable']}",
        f"- Otomatik ceza sinyali: {summary['auto_suspension_entries']}",
        f"- Manuel kayıt: {summary['manual_entries']}",
        f"- Güncel haber/sakat-cezalı sinyali: {summary.get('news_context_entries', 0)}",
        f"- Haber istihbaratı sinyali: {summary.get('news_intelligence_entries', 0)}",
        f"- Not: {payload['rules_note']}",
        "",
    ]
    if payload.get("current_news_context_unavailability"):
        lines.extend(["## Güncel Haber/Sakat-Cezalı Bağlamı", ""])
        for item in payload["current_news_context_unavailability"]:
            lines.append(
                f"- {item['status']} | {item.get('player_name')} | kaynak={item.get('source')} | güven={item.get('confidence')}"
            )
        lines.append("")
    lines.extend(["## Maç Bazlı Eksikler", ""])
    for match in payload["matches"]:
        if not match["unavailable"]:
            continue
        lines.append(f"### {match['date']} | {match['fixture']}")
        for item in match["unavailable"]:
            lines.append(
                f"- {item['status']} | {item.get('player_name') or item.get('player_external_id')} | "
                f"{item.get('reason', '')} | kaynak={item.get('source')} | güven={item.get('confidence')}"
            )
        lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
