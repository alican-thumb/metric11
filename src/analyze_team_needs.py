from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from pathlib import Path

from src.config import PROCESSED_DIR
from src.normalization import canonical_player_name


def main() -> None:
    parser = argparse.ArgumentParser(description="Takim profili, sozlesme ve performans verilerinden ihtiyac raporu uretir.")
    parser.add_argument("--team", default="BEŞİKTAŞ A.Ş.")
    parser.add_argument("--matches", default=str(PROCESSED_DIR / "tff_trendyol_super_lig_2025_2026_matches.json"))
    parser.add_argument("--profiles", default=str(PROCESSED_DIR / "tff_player_profiles_besiktas_2025_2026.json"))
    parser.add_argument("--transfermarkt", default=str(PROCESSED_DIR / "transfermarkt_besiktas_squad_2025_2026.json"))
    parser.add_argument("--output-prefix", default="besiktas_team_needs_2025_2026")
    args = parser.parse_args()

    matches = json.loads(Path(args.matches).read_text(encoding="utf-8"))
    profiles = json.loads(Path(args.profiles).read_text(encoding="utf-8"))
    transfermarkt = load_optional_json(Path(args.transfermarkt))
    report = build_report(args.team, matches, profiles, transfermarkt)

    json_path = PROCESSED_DIR / f"{args.output_prefix}.json"
    md_path = PROCESSED_DIR / f"{args.output_prefix}.md"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(build_markdown(report), encoding="utf-8")
    print(md_path.read_text(encoding="utf-8"))


def build_report(team: str, matches: list[dict], profiles: list[dict], transfermarkt: dict | None = None) -> dict:
    profile_by_id = {profile["external_id"]: profile for profile in profiles}
    tm_players = transfermarkt.get("players", []) if transfermarkt else []
    tm_matches = match_transfermarkt_profiles(profiles, tm_players)
    usage = defaultdict(lambda: {"starts": 0, "bench": 0, "goals": 0, "cards": 0})

    for match in matches:
        side = side_for_team(match, team)
        if not side:
            continue
        for player in match["lineups"][side]["starting"]:
            usage[player["external_id"]]["starts"] += 1
        for player in match["lineups"][side]["bench"]:
            usage[player["external_id"]]["bench"] += 1
        for goal in match["goals"][side]:
            player_id = goal.get("player_external_id") or goal.get("external_id")
            if player_id:
                usage[player_id]["goals"] += 1
        for card in match["cards"][side]:
            player_id = card.get("player_external_id") or card.get("external_id")
            if player_id:
                usage[player_id]["cards"] += 1

    enriched = []
    for player_id, profile in profile_by_id.items():
        stats = usage[player_id]
        tm_profile = tm_matches.get(player_id)
        enriched.append(
            {
                **profile,
                **stats,
                "transfermarkt": tm_profile,
                "position": tm_profile.get("position") if tm_profile else None,
                "position_group": tm_profile.get("position_group") if tm_profile else "UNKNOWN",
                "market_value_eur": tm_profile.get("market_value_eur") if tm_profile else None,
                "market_value_text": tm_profile.get("market_value_text") if tm_profile else None,
                "availability_score": score_availability(stats["starts"], stats["bench"]),
                "asset_score": score_asset(profile, stats, tm_profile),
                "contract_risk": contract_risk(profile.get("contract_months_left")),
                "age_band": age_band(profile.get("age")),
            }
        )

    ages = [player["age"] for player in enriched if player.get("age") is not None]
    contract_months = [player["contract_months_left"] for player in enriched if player.get("contract_months_left") is not None]
    starts_by_age_band = Counter()
    starts_by_position_group = Counter()
    goals_by_player = Counter()
    for player in enriched:
        starts_by_age_band[player["age_band"]] += player["starts"]
        starts_by_position_group[player["position_group"]] += player["starts"]
        goals_by_player[player["name"]] = player["goals"]

    needs = infer_needs(enriched, starts_by_age_band, starts_by_position_group)
    return {
        "team": team,
        "summary": {
            "players": len(enriched),
            "transfermarkt_matched_players": len(tm_matches),
            "avg_age": round(sum(ages) / len(ages), 1) if ages else None,
            "avg_contract_months_left": round(sum(contract_months) / len(contract_months), 1) if contract_months else None,
            "u23_players": sum(1 for player in enriched if player.get("age") is not None and player["age"] <= 23),
            "contract_expiring_13_months": sum(1 for player in enriched if player.get("contract_months_left") is not None and player["contract_months_left"] <= 13),
            "market_value_total_eur": sum(player["market_value_eur"] or 0 for player in enriched),
        },
        "starts_by_age_band": dict(starts_by_age_band),
        "starts_by_position_group": dict(starts_by_position_group),
        "top_assets": sorted(enriched, key=lambda player: player["asset_score"], reverse=True)[:12],
        "contract_risks": sorted(
            [player for player in enriched if player["contract_risk"] != "LOW"],
            key=lambda player: (player.get("contract_months_left") if player.get("contract_months_left") is not None else 999, -player["starts"]),
        ),
        "young_assets": sorted(
            [player for player in enriched if player.get("age") is not None and player["age"] <= 23],
            key=lambda player: player["asset_score"],
            reverse=True,
        ),
        "goal_dependency": goals_by_player.most_common(10),
        "transfermarkt_unmatched": sorted([player["name"] for player in enriched if not player.get("transfermarkt")]),
        "position_action_plan": build_position_action_plan(enriched),
        "needs": needs,
    }


def side_for_team(match: dict, team: str) -> str | None:
    if match["home_team"]["name"] == team:
        return "home"
    if match["away_team"]["name"] == team:
        return "away"
    return None


def score_availability(starts: int, bench: int) -> float:
    return round(min(100, starts * 2.4 + bench * 0.45), 1)


def score_asset(profile: dict, stats: dict, tm_profile: dict | None = None) -> float:
    age = profile.get("age") or 30
    contract = profile.get("contract_months_left") or 0
    market_value = (tm_profile or {}).get("market_value_eur") or 0
    age_bonus = max(0, 28 - age) * 2.2 if age <= 28 else max(-12, (28 - age) * 1.1)
    contract_bonus = min(18, contract * 0.35)
    value_bonus = min(16, market_value / 1_000_000 * 0.45)
    return round(stats["starts"] * 1.6 + stats["goals"] * 4.5 - stats["cards"] * 0.8 + age_bonus + contract_bonus + value_bonus, 1)


def contract_risk(months_left: int | None) -> str:
    if months_left is None:
        return "UNKNOWN"
    if months_left <= 6:
        return "HIGH"
    if months_left <= 13:
        return "MEDIUM"
    return "LOW"


def age_band(age: int | None) -> str:
    if age is None:
        return "UNKNOWN"
    if age <= 21:
        return "U21"
    if age <= 23:
        return "U23"
    if age <= 27:
        return "24-27"
    if age <= 31:
        return "28-31"
    return "32+"


def infer_needs(players: list[dict], starts_by_age_band: Counter, starts_by_position_group: Counter) -> list[dict]:
    needs = []
    total_starts = sum(starts_by_age_band.values()) or 1
    veteran_share = (starts_by_age_band["28-31"] + starts_by_age_band["32+"]) / total_starts
    expiring_starters = [player for player in players if player["starts"] >= 8 and player["contract_risk"] in {"HIGH", "MEDIUM"}]
    goal_scorers = [player for player in players if player["goals"] >= 5]
    position_starters = {
        group: [player for player in players if player["position_group"] == group and player["starts"] >= 8]
        for group in ("GK", "DEF", "MID", "FWD")
    }

    if veteran_share >= 0.48:
        needs.append(
            {
                "priority": "HIGH",
                "need": "Daha genç ve ilk 11 seviyesine yakın rotasyon",
                "reason": f"İlk 11 yükünün %{round(veteran_share * 100)} bölümü 28+ yaş bandından geliyor.",
            }
        )
    if expiring_starters:
        needs.append(
            {
                "priority": "HIGH",
                "need": "Sözleşme riski olan düzenli oyuncular için yenileme veya ikame planı",
                "reason": ", ".join(player["name"] for player in expiring_starters[:5]),
            }
        )
    if len(goal_scorers) <= 3:
        needs.append(
            {
                "priority": "MEDIUM",
                "need": "Gol katkısını daha çok oyuncuya yayan hücum profili",
                "reason": "5+ gol katkısı veren oyuncu sayısı sınırlı; skor yükü dar bir gruba binebilir.",
            }
        )
    for group, label in (("DEF", "savunma"), ("MID", "orta saha"), ("FWD", "hücum")):
        risky = [player for player in position_starters[group] if player["contract_risk"] in {"HIGH", "MEDIUM"}]
        if risky:
            needs.append(
                {
                    "priority": "MEDIUM",
                    "need": f"{label.title()} hattında sözleşme riski için alternatif plan",
                    "reason": ", ".join(player["name"] for player in risky[:4]),
                }
            )
    needs.append(
        {
            "priority": "MEDIUM",
            "need": "Pozisyon verisiyle tamamlanacak hedef scout havuzu",
            "reason": "TFF profilleri yaş/sözleşme veriyor ancak mevki vermiyor; Transfermarkt/TFF kulüp sayfası veya başka açık kaynakla pozisyon eşleştirme gerekiyor.",
        }
    )
    return needs


def match_transfermarkt_profiles(tff_profiles: list[dict], tm_players: list[dict]) -> dict:
    matches = {}
    used_tm_ids = set()
    for profile in tff_profiles:
        best = None
        best_score = 0.0
        for tm_player in tm_players:
            tm_key = tm_player.get("transfermarkt_id") or tm_player.get("name")
            if tm_key in used_tm_ids:
                continue
            score = name_match_score(profile["name"], tm_player["name"])
            if score > best_score:
                best = tm_player
                best_score = score
        if best and best_score >= 0.58:
            matches[profile["external_id"]] = {**best, "tff_match_score": round(best_score, 3)}
            used_tm_ids.add(best.get("transfermarkt_id") or best.get("name"))
    return matches


def name_match_score(left: str, right: str) -> float:
    left_norm = canonical_player_name(left)
    right_norm = canonical_player_name(right)
    if left_norm == right_norm:
        return 1.0
    left_tokens = set(left_norm.split())
    right_tokens = set(right_norm.split())
    if not left_tokens or not right_tokens:
        return 0.0
    token_score = len(left_tokens & right_tokens) / min(len(left_tokens), len(right_tokens))
    ratio = SequenceMatcher(None, left_norm, right_norm).ratio()
    return max(token_score, ratio)


def load_optional_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def build_position_action_plan(players: list[dict]) -> list[dict]:
    plan = []
    for group, label in (("GK", "Kaleci"), ("DEF", "Savunma"), ("MID", "Orta saha"), ("FWD", "Hücum")):
        group_players = [player for player in players if player["position_group"] == group]
        regulars = [player for player in group_players if player["starts"] >= 8]
        expiring = [player for player in regulars if player["contract_risk"] in {"HIGH", "MEDIUM"}]
        young_assets = [player for player in group_players if player.get("age") is not None and player["age"] <= 23]
        total_value = sum(player["market_value_eur"] or 0 for player in group_players)
        if expiring:
            priority = "HIGH" if len(expiring) >= 2 else "MEDIUM"
            recommendation = f"{label} hattında sözleşme riski bulunan düzenli oyuncular için yenileme/ikame planı."
        elif len(young_assets) == 0 and regulars:
            priority = "MEDIUM"
            recommendation = f"{label} hattında genç değer üretimi zayıf; U23 rotasyon oyuncusu aranmalı."
        else:
            priority = "LOW"
            recommendation = f"{label} hattında acil sinyal yok; fırsat transferi kovalanabilir."
        plan.append(
            {
                "position_group": group,
                "label": label,
                "priority": priority,
                "players": len(group_players),
                "regulars": len(regulars),
                "young_assets": len(young_assets),
                "expiring_regulars": [player["name"] for player in expiring],
                "market_value_total_eur": total_value,
                "recommendation": recommendation,
            }
        )
    return plan


def build_markdown(report: dict) -> str:
    summary = report["summary"]
    lines = [
        f"# {report['team']} Takım İhtiyaç Analizi",
        "",
        f"- Oyuncu profili: {summary['players']}",
        f"- Transfermarkt eşleşen oyuncu: {summary['transfermarkt_matched_players']}",
        f"- Ortalama yaş: {summary['avg_age']}",
        f"- Ortalama kalan sözleşme ayı: {summary['avg_contract_months_left']}",
        f"- U23 oyuncu: {summary['u23_players']}",
        f"- 13 ay içinde sözleşmesi bitecek oyuncu: {summary['contract_expiring_13_months']}",
        f"- Eşleşen toplam piyasa değeri: €{summary['market_value_total_eur']:,}",
        f"- İlk 11 yaş bandı dağılımı: {report['starts_by_age_band']}",
        f"- İlk 11 pozisyon grubu dağılımı: {report['starts_by_position_group']}",
        "",
        "## İhtiyaç Sinyalleri",
        "",
    ]
    for item in report["needs"]:
        lines.append(f"- {item['priority']}: {item['need']} — {item['reason']}")
    lines.extend(["", "## Pozisyon Aksiyon Planı", ""])
    for item in report["position_action_plan"]:
        lines.append(
            f"- {item['priority']} | {item['label']}: oyuncu={item['players']}, düzenli={item['regulars']}, "
            f"genç={item['young_assets']}, değer=€{item['market_value_total_eur']:,} — {item['recommendation']} "
            f"Riskli düzenliler: {', '.join(item['expiring_regulars']) or 'Yok'}"
        )
    lines.extend(["", "## Elde Değer / Gelişim Varlığı", ""])
    for player in report["top_assets"][:10]:
        lines.append(
            f"- {player['name']}: asset={player['asset_score']}, yaş={player.get('age')}, "
            f"pozisyon={player.get('position') or 'Yok'}, değer={player.get('market_value_text') or 'Yok'}, "
            f"ilk 11={player['starts']}, gol={player['goals']}, sözleşme={player.get('contract_end') or 'Yok'}"
        )
    lines.extend(["", "## Genç Varlıklar", ""])
    for player in report["young_assets"][:12]:
        lines.append(
            f"- {player['name']}: yaş={player.get('age')}, asset={player['asset_score']}, "
            f"pozisyon={player.get('position') or 'Yok'}, değer={player.get('market_value_text') or 'Yok'}, "
            f"ilk 11={player['starts']}, sözleşme={player.get('contract_end') or 'Yok'}"
        )
    lines.extend(["", "## Sözleşme Riski", ""])
    for player in report["contract_risks"][:12]:
        lines.append(
            f"- {player['name']}: risk={player['contract_risk']}, kalan ay={player.get('contract_months_left')}, "
            f"pozisyon={player.get('position') or 'Yok'}, değer={player.get('market_value_text') or 'Yok'}, "
            f"ilk 11={player['starts']}, bitiş={player.get('contract_end') or 'Yok'}"
        )
    lines.extend(["", "## Transfermarkt Eşleşmeyen Oyuncular", ""])
    for name in report["transfermarkt_unmatched"][:20]:
        lines.append(f"- {name}")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
