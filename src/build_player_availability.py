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
    parser.add_argument("--manual", default="data/manual/player_availability_overrides.json")
    parser.add_argument("--news-context", default=str(PROCESSED_DIR / "news_context_snapshot_2025_2026.json"))
    parser.add_argument("--news-intelligence", default=str(PROCESSED_DIR / "news_intelligence_2025_2026.json"))
    parser.add_argument("--output-prefix", default="player_availability_besiktas_2025_2026")
    args = parser.parse_args()

    matches = normalize_matches(json.loads(Path(args.matches).read_text(encoding="utf-8")))
    news_context = load_news_context(Path(args.news_context))
    news_intel = load_news_context(Path(args.news_intelligence))
    availability = build_availability(matches, args.team, Path(args.manual), news_context, news_intel)

    json_path = PROCESSED_DIR / f"{args.output_prefix}.json"
    md_path = PROCESSED_DIR / f"{args.output_prefix}.md"
    json_path.write_text(json.dumps(availability, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(build_markdown(availability), encoding="utf-8")
    print(md_path.read_text(encoding="utf-8"))


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
    summary = {
        "matches": len(match_reports),
        "matches_with_unavailable": sum(1 for item in match_reports if item["unavailable"]),
        "auto_suspension_entries": sum(1 for item in match_reports for entry in item["unavailable"] if entry["source"].startswith("AUTO")),
        "manual_entries": len(manual_entries),
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


def news_unavailability_for_team(news_context: dict | None, team: str) -> list[dict]:
    if not news_context:
        return []
    aliases = {team.casefold(), "beşiktaş", "besiktas"}
    output = []
    for item in news_context.get("team_unavailability", []):
        item_team = (item.get("team") or "").casefold()
        if not any(alias in item_team or item_team in alias for alias in aliases):
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
    """Reads structured injury/suspension signals from news_intelligence output."""
    if not news_intel:
        return []
    team_lower = team.casefold()
    # Build simple alias set for the team
    team_words = {w for w in team_lower.split() if len(w) >= 4}
    output = []
    for signal in news_intel.get("injuries", []):
        signal_team = (signal.get("team") or "").casefold()
        if not (team_lower in signal_team or signal_team in team_lower or
                any(w in signal_team for w in team_words)):
            continue
        output.append({
            "player_external_id": None,
            "player_name": signal.get("player"),
            "status": "INJURED",
            "reason": "Haber istihbaratı sakat sinyali",
            "source": "news_intelligence",
            "confidence": signal.get("confidence", "MEDIUM"),
            "detail": signal.get("detail"),
        })
    for signal in news_intel.get("suspensions", []):
        signal_team = (signal.get("team") or "").casefold()
        if not (team_lower in signal_team or signal_team in team_lower or
                any(w in signal_team for w in team_words)):
            continue
        output.append({
            "player_external_id": None,
            "player_name": signal.get("player"),
            "status": "SUSPENDED",
            "reason": "Haber istihbaratı cezalı sinyali",
            "source": "news_intelligence",
            "confidence": signal.get("confidence", "MEDIUM"),
            "detail": signal.get("detail"),
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
