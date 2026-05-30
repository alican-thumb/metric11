from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

from src.config import PROCESSED_DIR, SEASON
from src.html_utils import md_to_html, page_html
from src.normalization import canonical_player_name, normalize_team_name


def main() -> None:
    parser = argparse.ArgumentParser(description="TFF/Transfermarkt eşleşmeyen oyuncuları manuel inceleme kuyruğuna alır.")
    parser.add_argument("--profiles", default=str(PROCESSED_DIR / f"tff_player_profiles_enriched_{SEASON}.json"))
    parser.add_argument("--tm-squads", default=str(PROCESSED_DIR / f"transfermarkt_super_lig_squads_{SEASON}.json"))
    parser.add_argument("--scout-quality", default=str(PROCESSED_DIR / f"scout_quality_report_{SEASON}.json"))
    parser.add_argument("--league-intelligence", default=str(PROCESSED_DIR / f"league_intelligence_{SEASON}.json"))
    parser.add_argument("--output-prefix", default=f"transfermarkt_match_review_queue_{SEASON}")
    args = parser.parse_args()

    profiles = load_json(Path(args.profiles), [])
    tm_payload = load_json(Path(args.tm_squads), {})
    scout_quality = load_json(Path(args.scout_quality), {})
    league_intelligence = load_json(Path(args.league_intelligence), {})
    payload = build_queue(profiles, tm_payload, scout_quality, league_intelligence)
    md = build_markdown(payload)
    json_path = PROCESSED_DIR / f"{args.output_prefix}.json"
    md_path = PROCESSED_DIR / f"{args.output_prefix}.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(md, encoding="utf-8")
    html_path = PROCESSED_DIR / f"{args.output_prefix}.html"
    html_path.write_text(page_html("Transfermarkt Eşleşme Kuyruğu", md_to_html(md), noindex=True), encoding="utf-8")
    print(md)


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def build_queue(profiles: list[dict], tm_payload: dict, scout_quality: dict, league_intelligence: dict) -> dict:
    clubs: dict[str, dict] = {
        normalize_team_name(club.get("team_name")) or "": club for club in tm_payload.get("clubs", [])
    }
    all_candidates = [
        {**player, "tm_team_name": club.get("team_name")}
        for club in tm_payload.get("clubs", [])
        for player in club.get("players", [])
    ]
    scout_ids = {
        str(item.get("player_id"))
        for item in scout_quality.get("low_confidence_review_queue", [])
        if item.get("player_id")
    }
    activity_by_id = {
        str(item.get("player_id")): item
        for item in league_intelligence.get("player_profiles", [])
        if item.get("player_id")
    }
    matched = [profile for profile in profiles if is_verified_match(profile)]
    manual_mapped = [profile for profile in profiles if is_manual_mapping(profile)]
    unmatched = [profile for profile in profiles if not is_verified_match(profile) and not is_manual_mapping(profile)]
    queue = [classify(profile, clubs, all_candidates, scout_ids, activity_by_id) for profile in unmatched]
    manual_verification_queue = [
        manual_verification_row(profile, activity_by_id)
        for profile in manual_mapped
        if profile.get("tm_requires_network_verify", False)
    ]
    manual_verification_queue.sort(
        key=lambda item: (
            item["priority_rank"],
            -item["season_activity"]["starts"],
            item["tff_club"],
            item["tff_name"],
        )
    )
    tier_rank = {"SCOUT_BLOCKING": 0, "HIGH_USAGE_UNRESOLVED": 1, "ROTATION_USAGE_UNRESOLVED": 2, "OUT_OF_SNAPSHOT": 3}
    queue.sort(
        key=lambda item: (
            tier_rank.get(item["review_tier"], 4),
            item["priority_rank"],
            -item["season_activity"]["starts"],
            item["tff_club"],
            item["tff_name"],
        )
    )
    categories = Counter(item["category"] for item in queue)
    review_tiers = Counter(item["review_tier"] for item in queue)
    in_scope = [profile for profile in profiles if (normalize_team_name(profile.get("club")) or "") in clubs]
    in_scope_mapped = [
        profile for profile in in_scope if is_verified_match(profile) or is_manual_mapping(profile)
    ]
    team_coverage = build_team_coverage(profiles, clubs, queue)
    return {
        "summary": {
            "tff_profiles": len(profiles),
            "tm_clubs": len(clubs),
            "tm_players": tm_payload.get("summary", {}).get("players", 0),
            "snapshot_in_scope_tff_profiles": len(in_scope),
            "matched_profiles": len(matched),
            "verified_matched_profiles": len(matched),
            "manual_alias_mapped_profiles": len(manual_mapped),
            "manual_alias_pending_network_verification": len(manual_verification_queue),
            "operationally_mapped_profiles": len(matched) + len(manual_mapped),
            "operational_in_scope_mapped_profiles": len(in_scope_mapped),
            "unmatched_profiles": len(unmatched),
            "overall_match_rate": rate(len(matched), len(profiles)),
            "in_scope_match_rate": rate(len(matched), len(in_scope)),
            "operational_mapping_rate": rate(len(matched) + len(manual_mapped), len(profiles)),
            "operational_in_scope_mapping_rate": rate(len(in_scope_mapped), len(in_scope)),
            "scout_blocking_unmatched": sum(1 for item in queue if item["blocks_scout_review"]),
            "category_counts": dict(categories),
            "review_tier_counts": dict(review_tiers),
            "rule": (
                "Doğrulanmış kapsama yalnız snapshot eşleşmesi girer; manuel alias kullanımı "
                "ayrı izlenir ve ağ teyidi tamamlanana kadar doğrulanmış sayılmaz."
            ),
        },
        "team_coverage": team_coverage,
        "priority_queue": queue,
        "manual_verification_queue": manual_verification_queue,
        "scout_blocking_queue": [item for item in queue if item["blocks_scout_review"]],
    }


def build_team_coverage(profiles: list[dict], clubs: dict[str, dict], queue: list[dict]) -> list[dict]:
    unmatched_by_team: dict[str, list[dict]] = defaultdict(list)
    for item in queue:
        unmatched_by_team[item["tff_club"]].append(item)
    rows = []
    for club_name in sorted(clubs):
        team_profiles = [item for item in profiles if normalize_team_name(item.get("club")) == club_name]
        unmatched = unmatched_by_team.get(club_name, [])
        matched = sum(1 for item in team_profiles if is_verified_match(item))
        manual_mapped = sum(1 for item in team_profiles if is_manual_mapping(item))
        rows.append(
            {
                "team": club_name,
                "tff_profiles": len(team_profiles),
                "tm_players": len(clubs[club_name].get("players", [])),
                "matched_profiles": matched,
                "manual_alias_mapped_profiles": manual_mapped,
                "unmatched_profiles": len(unmatched),
                "match_rate": rate(matched, len(team_profiles)),
                "operational_mapping_rate": rate(matched + manual_mapped, len(team_profiles)),
                "categories": dict(Counter(item["category"] for item in unmatched)),
            }
        )
    return rows


def is_verified_match(profile: dict) -> bool:
    return bool(profile.get("tm_id"))


def is_manual_mapping(profile: dict) -> bool:
    return (
        not is_verified_match(profile)
        and profile.get("tm_match_method") == "manual_alias"
        and bool(profile.get("tm_name"))
    )


def manual_verification_row(profile: dict, activity_by_id: dict[str, dict]) -> dict:
    player_id = str(profile.get("external_id") or "")
    activity = activity_by_id.get(player_id, {})
    season_activity = {
        "starts": activity.get("starts", 0),
        "squad_inclusions": activity.get("squad_inclusions", 0),
        "goals": activity.get("goals", 0),
    }
    high_usage = season_activity["starts"] >= 10 or season_activity["goals"] >= 3
    return {
        "player_id": player_id,
        "tff_name": profile.get("name"),
        "tff_club": normalize_team_name(profile.get("club")),
        "category": "MANUAL_ALIAS_PENDING_NETWORK_VERIFY",
        "priority_rank": 1 if high_usage else 2,
        "blocks_scout_review": False,
        "review_tier": "MANUAL_VERIFY_HIGH_USAGE" if high_usage else "MANUAL_VERIFY",
        "season_activity": season_activity,
        "candidate": {
            "tm_name": profile.get("tm_name"),
            "tm_team_name": profile.get("tm_team_name") or profile.get("club"),
            "score": 1.0,
            "common_tokens": [],
        },
        "action": "Manuel eşleme operasyonda kullanılıyor; Transfermarkt profil bağlantısı ile ağ teyidi bekleniyor.",
    }


def classify(
    profile: dict,
    clubs: dict[str, dict],
    all_candidates: list[dict],
    scout_ids: set[str],
    activity_by_id: dict[str, dict],
) -> dict:
    name = profile.get("name") or ""
    club = normalize_team_name(profile.get("club")) or ""
    player_id = str(profile.get("external_id") or "")
    blocks_scout = player_id in scout_ids
    activity = activity_by_id.get(player_id, {})
    if club not in clubs:
        return queue_row(
            profile,
            "OUT_OF_SNAPSHOT_CLUB",
            4 if blocks_scout else 5,
            blocks_scout,
            None,
            "TFF kulübü mevcut 18 kulüp Transfermarkt snapshot'ında yok; önce transfer/kulüp kapsamı doğrulanmalı.",
            activity,
        )

    same_club = [candidate for candidate in clubs[club].get("players", [])]
    best_same = best_candidate(name, same_club)
    if best_same and name_candidate_reviewable(best_same):
        return queue_row(
            profile,
            "SAME_CLUB_NAME_REVIEW",
            1 if blocks_scout else 2,
            blocks_scout,
            best_same,
            "Aynı kulüpte güçlü ad varyantı adayı var; manuel onay sonrası alias kaydı eklenebilir.",
            activity,
        )

    other_clubs = [candidate for candidate in all_candidates if normalize_team_name(candidate.get("tm_team_name")) != club]
    best_cross = best_candidate(name, other_clubs)
    if best_cross and transfer_candidate_reviewable(best_cross):
        return queue_row(
            profile,
            "POSSIBLE_TRANSFER_OR_CLUB_MISMATCH",
            2 if blocks_scout else 3,
            blocks_scout,
            best_cross,
            "Oyuncu adı başka snapshot kulübünde güçlü eşleşiyor; transfer doğrulanmadan otomatik bağlanmamalı.",
            activity,
        )
    return queue_row(
        profile,
        "NO_RELIABLE_CANDIDATE_IN_SNAPSHOT",
        3 if blocks_scout else 4,
        blocks_scout,
        best_same if best_same and best_same["score"] >= 0.60 else None,
        "Mevcut snapshot içinde güvenilir isim adayı yok; kaynak/alias incelemesi gerekir.",
        activity,
    )


def best_candidate(name: str, candidates: list[dict]) -> dict | None:
    ranked = []
    source = canonical_player_name(name)
    source_tokens = set(source.split())
    for candidate in candidates:
        candidate_name = candidate.get("name") or ""
        target = canonical_player_name(candidate_name)
        common = source_tokens & set(target.split())
        score = SequenceMatcher(None, source, target).ratio() if source and target else 0
        ranked.append(
            {
                "tm_name": candidate_name,
                "tm_team_name": candidate.get("tm_team_name"),
                "tm_id": candidate.get("transfermarkt_id"),
                "tm_position": candidate.get("position"),
                "tm_market_value_eur": candidate.get("market_value_eur"),
                "score": round(score, 3),
                "common_tokens": sorted(common),
            }
        )
    return max(ranked, key=lambda item: item["score"], default=None)


def name_candidate_reviewable(candidate: dict) -> bool:
    return candidate["score"] >= 0.84 or (candidate["score"] >= 0.72 and len(candidate["common_tokens"]) >= 1)


def transfer_candidate_reviewable(candidate: dict) -> bool:
    return candidate["score"] >= 0.82 and len(candidate["common_tokens"]) >= 2


def queue_row(
    profile: dict,
    category: str,
    priority_rank: int,
    blocks_scout: bool,
    candidate: dict | None,
    action: str,
    activity: dict,
) -> dict:
    season_activity = {
        "starts": activity.get("starts", 0),
        "squad_inclusions": activity.get("squad_inclusions", 0),
        "goals": activity.get("goals", 0),
    }
    if blocks_scout:
        review_tier = "SCOUT_BLOCKING"
    elif category == "OUT_OF_SNAPSHOT_CLUB":
        review_tier = "OUT_OF_SNAPSHOT"
    elif season_activity["starts"] >= 10 or season_activity["goals"] >= 3:
        review_tier = "HIGH_USAGE_UNRESOLVED"
    elif season_activity["squad_inclusions"] > 0:
        review_tier = "ROTATION_USAGE_UNRESOLVED"
    else:
        review_tier = "NO_MATCH_ACTIVITY"
    return {
        "player_id": str(profile.get("external_id") or ""),
        "tff_name": profile.get("name"),
        "tff_club": normalize_team_name(profile.get("club")),
        "category": category,
        "priority_rank": priority_rank,
        "blocks_scout_review": blocks_scout,
        "review_tier": review_tier,
        "season_activity": season_activity,
        "candidate": candidate,
        "action": action,
    }


def rate(part: int, total: int) -> float:
    return round(part / total, 3) if total else 0


def build_markdown(payload: dict) -> str:
    summary = payload["summary"]
    lines = [
        "# Transfermarkt Oyuncu Eşleşme İnceleme Kuyruğu",
        "",
        f"- TFF profil: {summary['tff_profiles']}",
        f"- Transfermarkt snapshot: {summary['tm_clubs']}/18 kulüp, {summary['tm_players']} oyuncu",
        f"- Snapshot kapsamındaki TFF profil: {summary['snapshot_in_scope_tff_profiles']}",
        f"- Doğrulanmış snapshot eşleşmesi: {summary['verified_matched_profiles']}",
        f"- Manuel eşleme ile kullanılan profil: {summary['manual_alias_mapped_profiles']}",
        f"- Ağ teyidi bekleyen manuel eşleme: {summary['manual_alias_pending_network_verification']}",
        f"- Çözülmemiş profil: {summary['unmatched_profiles']}",
        f"- Doğrulanmış genel eşleşme oranı: %{round(summary['overall_match_rate'] * 100, 1)}",
        f"- Doğrulanmış snapshot içi eşleşme oranı: %{round(summary['in_scope_match_rate'] * 100, 1)}",
        f"- Manuel eşleme dahil kullanılabilir snapshot içi kapsama: %{round(summary['operational_in_scope_mapping_rate'] * 100, 1)}",
        f"- Scout incelemesini bloke eden eşleşmeyen oyuncu: {summary['scout_blocking_unmatched']}",
        f"- Sınıf dağılımı: {summary['category_counts']}",
        f"- Kullanım önceliği dağılımı: {summary['review_tier_counts']}",
        f"- Kural: {summary['rule']}",
        "",
        "## Scout Bloke Eden Kuyruk",
        "",
    ]
    for item in payload["scout_blocking_queue"]:
        lines.append(render_row(item))
    lines.extend(["", "## Manuel Eşleme Ağ Teyidi Bekleyenler", ""])
    for item in payload["manual_verification_queue"]:
        lines.append(render_row(item))
    lines.extend(["", "## 18 Takım Kapsama Tablosu", ""])
    lines.append("| Takım | TFF Profil | TM Kadro | Doğrulanmış | Manuel | Açık | Doğrulanmış Oran | Kullanılabilir Oran |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|")
    for item in payload["team_coverage"]:
        lines.append(
            f"| {item['team']} | {item['tff_profiles']} | {item['tm_players']} | "
            f"{item['matched_profiles']} | {item['manual_alias_mapped_profiles']} | {item['unmatched_profiles']} | "
            f"%{round(item['match_rate'] * 100, 1)} | %{round(item['operational_mapping_rate'] * 100, 1)} |"
        )
    lines.extend(["", "## Tüm Eşleşmeyen Kayıtlar (Takım Bazında)", ""])
    queue_by_team: dict[str, list[dict]] = defaultdict(list)
    for item in payload["priority_queue"]:
        queue_by_team[item["tff_club"]].append(item)
    for team in sorted(queue_by_team):
        lines.extend([f"### {team}", ""])
        for item in queue_by_team[team]:
            lines.append(render_row(item))
        lines.append("")
    return "\n".join(lines)


def render_row(item: dict) -> str:
    candidate = item.get("candidate")
    suggestion = "-"
    if candidate:
        suggestion = (
            f"{candidate['tm_name']} ({candidate.get('tm_team_name') or item['tff_club']}, "
            f"skor={candidate['score']}, ortak={','.join(candidate['common_tokens']) or '-'})"
        )
    return (
        f"- {item['tff_name']} ({item['tff_club']}): sınıf={item['category']}, "
        f"öncelik={item['review_tier']}, ilk11={item['season_activity']['starts']}, "
        f"gol={item['season_activity']['goals']}, scout_blok={item['blocks_scout_review']}, "
        f"aday={suggestion}. {item['action']}"
    )


if __name__ == "__main__":
    main()
