from __future__ import annotations

import argparse
import json
from difflib import SequenceMatcher
from pathlib import Path

from src.config import PROCESSED_DIR, ROOT_DIR
from src.html_utils import md_to_html, page_html
from src.normalization import canonical_player_name


def main() -> None:
    parser = argparse.ArgumentParser(description="TFF, Transfermarkt ve dış API oyuncu isim eşleşme kalitesini raporlar.")
    parser.add_argument("--output-prefix", default="player_alias_quality_2025_2026")
    args = parser.parse_args()

    payload = build_payload()
    md = build_markdown(payload)
    json_path = PROCESSED_DIR / f"{args.output_prefix}.json"
    md_path = PROCESSED_DIR / f"{args.output_prefix}.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(md, encoding="utf-8")
    html_path = PROCESSED_DIR / f"{args.output_prefix}.html"
    html_path.write_text(page_html("Oyuncu Alias Kalite Raporu", md_to_html(md), noindex=True, canonical_path=html_path.name), encoding="utf-8")
    print(md)


def build_payload() -> dict:
    aliases = load_json(ROOT_DIR / "data/manual/player_aliases.json", {})
    tff_enriched = load_json(PROCESSED_DIR / "tff_player_profiles_enriched_2025_2026.json", [])
    tff_besiktas = load_json(PROCESSED_DIR / "tff_player_profiles_besiktas_2025_2026.json", [])
    tff_scout = load_json(PROCESSED_DIR / "tff_player_profiles_scout_shortlist_2025_2026.json", [])
    scout_shortlist = load_json(PROCESSED_DIR / "league_scouting_2025_2026_normalized.json", {}).get("scout_shortlist", [])
    transfermarkt = load_json(PROCESSED_DIR / "transfermarkt_besiktas_squad_2025_2026.json", {}).get("players", [])
    transfermarkt_league = load_json(PROCESSED_DIR / "transfermarkt_super_lig_squads_2025_2026.json", {})
    external = load_json(PROCESSED_DIR / "api_football_super_lig_deep_2024_analysis.json", {}).get("player_attribute_pool", [])
    scout_team_by_id = {str(item.get("player_id")): item.get("team") for item in scout_shortlist}

    sources = {
        "tff_besiktas": [{"name": item.get("name"), "team": "BEŞİKTAŞ A.Ş.", "id": item.get("external_id")} for item in tff_besiktas],
        "tff_scout": [{"name": item.get("name"), "team": scout_team_by_id.get(str(item.get("external_id"))), "id": item.get("external_id")} for item in tff_scout],
        "transfermarkt_besiktas": [{"name": item.get("name"), "team": "BEŞİKTAŞ", "id": item.get("transfermarkt_id")} for item in transfermarkt],
        "api_football_deep_2024": [{"name": item.get("name"), "team": item.get("team"), "id": item.get("player_id")} for item in external],
    }

    comparisons = {
        "league_tff_vs_transfermarkt": compare_enriched_profiles(tff_enriched),
        "besiktas_tff_vs_transfermarkt": compare_sources(sources["tff_besiktas"], sources["transfermarkt_besiktas"]),
        "scout_tff_vs_api_deep": compare_sources(sources["tff_scout"], sources["api_football_deep_2024"]),
        "besiktas_tff_vs_api_deep": compare_sources(sources["tff_besiktas"], sources["api_football_deep_2024"]),
    }
    return {
        "summary": {
            "alias_players": len(aliases.get("players", [])),
            "tff_league_profiles": len(tff_enriched),
            "transfermarkt_league_clubs": transfermarkt_league.get("summary", {}).get("clubs", 0),
            "transfermarkt_league_players": transfermarkt_league.get("summary", {}).get("players", 0),
            "tff_besiktas_players": len(sources["tff_besiktas"]),
            "tff_scout_players": len(sources["tff_scout"]),
            "transfermarkt_besiktas_players": len(sources["transfermarkt_besiktas"]),
            "api_football_deep_players": len(sources["api_football_deep_2024"]),
        },
        "comparisons": comparisons,
        "alias_entries": aliases.get("players", []),
    }


def compare_enriched_profiles(profiles: list[dict]) -> dict:
    matches = [
        {
            "left_name": item.get("name"),
            "right_name": item.get("tm_name") or item.get("name"),
            "left_team": item.get("club"),
            "right_team": item.get("tm_team_name"),
            "score": 1.0,
            "canonical": canonical_player_name(item.get("name")),
        }
        for item in profiles
        if item.get("tm_id")
    ]
    manual_mapped = [
        {
            "left_name": item.get("name"),
            "right_name": item.get("tm_name") or item.get("name"),
            "left_team": item.get("club"),
            "right_team": item.get("tm_team_name"),
            "requires_network_verify": item.get("tm_requires_network_verify", False),
        }
        for item in profiles
        if not item.get("tm_id") and item.get("tm_match_method") == "manual_alias" and item.get("tm_name")
    ]
    unmatched = [
        {"name": item.get("name"), "team": item.get("club"), "id": item.get("external_id")}
        for item in profiles
        if not item.get("tm_id") and item.get("tm_match_method") != "manual_alias"
    ]
    return {
        "left_count": len(profiles),
        "right_count": 0,
        "matched": len(matches),
        "match_rate": round(len(matches) / len(profiles), 3) if profiles else 0,
        "manual_mapped": len(manual_mapped),
        "manual_pending_network_verification": sum(
            1 for item in manual_mapped if item["requires_network_verify"]
        ),
        "operationally_mapped": len(matches) + len(manual_mapped),
        "operational_mapping_rate": round((len(matches) + len(manual_mapped)) / len(profiles), 3) if profiles else 0,
        "matches": matches,
        "manual_mappings": manual_mapped,
        "unmatched_left": unmatched,
    }


def compare_sources(left: list[dict], right: list[dict], threshold: float = 0.72) -> dict:
    matches = []
    unmatched_left = []
    used_right = set()
    for left_item in left:
        best = None
        best_score = 0.0
        for right_item in right:
            right_key = str(right_item.get("id") or right_item.get("name"))
            if right_key in used_right:
                continue
            score = name_score(left_item.get("name"), right_item.get("name"), left_item.get("team"), right_item.get("team"))
            if score > best_score:
                best = right_item
                best_score = score
        if best and best_score >= threshold:
            matches.append(
                {
                    "left_name": left_item.get("name"),
                    "right_name": best.get("name"),
                    "left_team": left_item.get("team"),
                    "right_team": best.get("team"),
                    "score": round(best_score, 3),
                    "canonical": canonical_player_name(left_item.get("name")),
                }
            )
            used_right.add(str(best.get("id") or best.get("name")))
        else:
            unmatched_left.append(left_item)
    return {
        "left_count": len(left),
        "right_count": len(right),
        "matched": len(matches),
        "match_rate": round(len(matches) / len(left), 3) if left else 0,
        "matches": sorted(matches, key=lambda item: item["score"]),
        "unmatched_left": sorted(unmatched_left, key=lambda item: item.get("name") or ""),
    }


def name_score(left: str | None, right: str | None, left_team: str | None = None, right_team: str | None = None) -> float:
    left_norm = canonical_player_name(left)
    right_norm = canonical_player_name(right)
    if not left_norm or not right_norm:
        return 0.0
    if left_norm == right_norm:
        return 1.0
    left_list = left_norm.split()
    right_list = right_norm.split()
    left_tokens = set(left_list)
    right_tokens = set(right_list)
    common = left_tokens & right_tokens
    team_overlap = token_overlap(set(canonical_player_name(left_team).split()), set(canonical_player_name(right_team).split()))
    token_score = len(common) / max(1, min(len(left_tokens), len(right_tokens)))
    ratio = SequenceMatcher(None, left_norm, right_norm).ratio()
    initial_surname = bool(
        left_list
        and right_list
        and left_list[0][:1] == right_list[0][:1]
        and left_list[-1] == right_list[-1]
    )
    if initial_surname:
        return max(0.9, ratio)
    if not common:
        return ratio if ratio >= 0.84 else 0.0
    if team_overlap == 0 and token_score < 0.67:
        return 0.0
    return max(token_score, ratio)


def token_overlap(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    return len(left & right) / max(1, min(len(left), len(right)))


def load_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def build_markdown(payload: dict) -> str:
    summary = payload["summary"]
    lines = [
        "# Oyuncu Alias ve Eşleşme Kalitesi",
        "",
        f"- Manuel alias oyuncusu: {summary['alias_players']}",
        f"- İşlenen TFF lig profil havuzu: {summary['tff_league_profiles']}",
        f"- Transfermarkt Süper Lig kadrosu: {summary['transfermarkt_league_clubs']}/18 kulüp, {summary['transfermarkt_league_players']} oyuncu",
        f"- TFF Beşiktaş profili: {summary['tff_besiktas_players']}",
        f"- TFF scout profili: {summary['tff_scout_players']}",
        f"- Transfermarkt Beşiktaş oyuncusu: {summary['transfermarkt_besiktas_players']}",
        f"- Dış API derin oyuncusu: {summary['api_football_deep_players']}",
        "",
        "## Karşılaştırmalar",
        "",
    ]
    for name, comparison in payload["comparisons"].items():
        lines.append(
            f"- {name}: {comparison['matched']}/{comparison['left_count']} eşleşme "
            f"(%{round(comparison['match_rate'] * 100)})"
        )
        if name == "league_tff_vs_transfermarkt":
            lines.append(
                f"  - Manuel eşleme: {comparison.get('manual_mapped', 0)} "
                f"(ağ teyidi bekleyen={comparison.get('manual_pending_network_verification', 0)}); "
                f"kullanılabilir eşleme %{round(comparison.get('operational_mapping_rate', 0) * 100)}"
            )
        if name == "besiktas_tff_vs_transfermarkt":
            lines.append("  - Ham tekil kaynak karşılaştırmasıdır; operasyonel manuel eşlemeler lig karşılaştırmasında izlenir.")
    lines.extend(["", "## Düşük Skorlu Eşleşmeler", ""])
    for name, comparison in payload["comparisons"].items():
        lines.append(f"### {name}")
        for item in comparison["matches"][:10]:
            lines.append(
                f"- {item['left_name']} -> {item['right_name']} | skor={item['score']} | canonical={item['canonical']}"
            )
        lines.append("")
    lines.extend(["## Eşleşmeyen Sol Kaynak Oyuncuları", ""])
    for name, comparison in payload["comparisons"].items():
        lines.append(f"### {name}")
        for item in comparison["unmatched_left"][:20]:
            lines.append(f"- {item.get('name')} ({item.get('team') or 'takım yok'})")
        lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
