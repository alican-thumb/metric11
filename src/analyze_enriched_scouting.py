from __future__ import annotations

import argparse
import json
from difflib import SequenceMatcher
from pathlib import Path

from src.config import PROCESSED_DIR
from src.normalization import canonical_player_name, normalize_name


def main() -> None:
    parser = argparse.ArgumentParser(description="Scout metriklerini TFF oyuncu profil verisiyle zenginlestirir.")
    parser.add_argument("--scout", default=str(PROCESSED_DIR / "league_scouting_2025_2026_normalized.json"))
    parser.add_argument("--profiles", default=str(PROCESSED_DIR / "tff_player_profiles_enriched_2025_2026.json"))
    parser.add_argument("--attributes", default=str(PROCESSED_DIR / "player_attribute_dataset_normalized.json"))
    parser.add_argument("--attributes-fm23", default=str(PROCESSED_DIR / "player_attribute_dataset_fm2023_normalized.json"))
    parser.add_argument("--attributes-derived", default=str(PROCESSED_DIR / "player_attribute_dataset_fm_derived_2025_2026.json"))
    parser.add_argument("--external-api", default=str(PROCESSED_DIR / "api_football_super_lig_deep_2024_analysis.json"))
    parser.add_argument("--output-prefix", default="league_scouting_enriched_2025_2026")
    args = parser.parse_args()

    scout = json.loads(Path(args.scout).read_text(encoding="utf-8"))
    profiles = json.loads(Path(args.profiles).read_text(encoding="utf-8"))
    attributes = load_attributes(Path(args.attributes))
    attributes_fm23 = load_attributes(Path(args.attributes_fm23))
    attributes_derived = load_attributes(Path(args.attributes_derived))
    external_api = load_external_api(Path(args.external_api))
    payload = build_payload(scout, profiles, attributes, external_api, attributes_fm23, attributes_derived)

    json_path = PROCESSED_DIR / f"{args.output_prefix}.json"
    md_path = PROCESSED_DIR / f"{args.output_prefix}.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(build_markdown(payload), encoding="utf-8")
    print(md_path.read_text(encoding="utf-8"))


def build_payload(scout: dict, profiles: list[dict], attributes: dict | None = None, external_api: dict | None = None,
                  attributes_fm23: dict | None = None, attributes_derived: dict | None = None) -> dict:
    profile_by_id = {str(profile["external_id"]): profile for profile in profiles}
    attribute_by_name = {
        canonical_player_name(item["name_normalized"]): item
        for item in (attributes or {}).get("players", [])
        if item.get("name_normalized")
    }
    fm23_by_name, fm23_by_surname = _build_fm23_index(attributes_fm23)
    derived_by_name = _build_derived_index(attributes_derived)
    external_players = (external_api or {}).get("player_attribute_pool", [])
    enriched = []
    for player in scout.get("player_pool", scout["scout_shortlist"]):
        profile = profile_by_id.get(str(player["player_id"]))
        if not profile:
            continue
        attribute = attribute_by_name.get(canonical_player_name(player["name"]))
        fm23_match = _find_fm23(player["name"], fm23_by_name, fm23_by_surname)
        derived_match = derived_by_name.get(canonical_player_name(player["name"]))
        external_match = best_external_match(player, external_players)
        enriched.append(
            {
                **player,
                "age": profile.get("age"),
                "birth_date": profile.get("birth_date"),
                "nationality": profile.get("nationality"),
                "contract_end": profile.get("contract_end"),
                "contract_months_left": profile.get("contract_months_left"),
                "tm_position": profile.get("tm_position"),
                "tm_position_group": profile.get("tm_position_group"),
                "tm_market_value_eur": profile.get("tm_market_value_eur"),
                "tm_market_value_text": profile.get("tm_market_value_text"),
                "tm_id": profile.get("tm_id"),
                "tm_profile_url": profile.get("tm_profile_url"),
                "contract_risk": contract_risk(profile.get("contract_months_left")),
                "resale_signal": resale_signal(profile.get("age"), player.get("starts", 0), player.get("goals", 0)),
                "attribute_signal": summarize_attribute(attribute),
                "fm23_signal": summarize_fm23(fm23_match),
                "derived_signal": summarize_derived(derived_match),
                "external_api_signal": summarize_external_api(external_match),
                "opportunity_score": opportunity_score(profile, player, attribute, external_match),
            }
        )
    enriched.sort(key=lambda item: item["opportunity_score"], reverse=True)
    return {
        "summary": {
            "profiled_players": len(enriched),
            "u24_players": sum(1 for item in enriched if item.get("age") is not None and item["age"] <= 24),
            "contract_risk_players": sum(1 for item in enriched if item["contract_risk"] in {"HIGH", "MEDIUM"}),
            "attribute_source": (attributes or {}).get("source", {}).get("name"),
            "attribute_matched_players": sum(1 for item in enriched if item.get("attribute_signal", {}).get("matched")),
            "fm23_matched_players": sum(1 for item in enriched if item.get("fm23_signal", {}).get("matched")),
            "derived_matched_players": sum(1 for item in enriched if item.get("derived_signal", {}).get("matched")),
            "external_api_source": (external_api or {}).get("source", {}).get("source"),
            "external_api_matched_players": sum(1 for item in enriched if item.get("external_api_signal", {}).get("matched")),
        },
        "enriched_shortlist": enriched,
        "young_value": [item for item in enriched if item.get("age") is not None and item["age"] <= 24][:12],
        "contract_opportunities": sorted(
            [item for item in enriched if item["contract_risk"] in {"HIGH", "MEDIUM"}],
            key=lambda item: (item.get("contract_months_left") if item.get("contract_months_left") is not None else 999, -item["scout_value_score"]),
        )[:12],
    }


def _build_derived_index(attributes_derived: dict | None) -> dict:
    if not attributes_derived:
        return {}
    result: dict[str, dict] = {}
    for item in attributes_derived.get("players", []):
        name = item.get("name_normalized") or item.get("Name") or item.get("name")
        if not name:
            continue
        key = canonical_player_name(name)
        # normalise the derived item to lowercase keys for summarize_derived
        normalized = {
            "name": name,
            "name_normalized": normalize_name(name),
            "current_ability": item.get("current_ability") or item.get("Current Ability"),
            "potential_ability": item.get("potential_ability") or item.get("Potential Ability"),
            "raw_attributes": {
                k.lower().replace(" ", "_"): v
                for k, v in item.items()
                if k not in ("Name", "Club", "Age", "Position", "Current Ability", "Potential Ability", "_external_matched")
                and v not in (None, "")
            },
        }
        result[key] = normalized
    return result


def _build_fm23_index(attributes_fm23: dict | None) -> tuple[dict, dict]:
    """Returns (exact_name_map, surname_map). Surname map stores list to handle collisions."""
    if not attributes_fm23:
        return {}, {}
    by_name: dict[str, dict] = {}
    by_surname: dict[str, list[dict]] = {}
    for item in attributes_fm23.get("players", []):
        if not item.get("name_normalized"):
            continue
        key = canonical_player_name(item["name_normalized"])
        by_name[key] = item
        tokens = key.split()
        if tokens:
            surname = tokens[-1]
            by_surname.setdefault(surname, []).append(item)
    return by_name, by_surname


def _find_fm23(player_name: str, by_name: dict, by_surname: dict) -> dict | None:
    key = canonical_player_name(player_name)
    if key in by_name:
        return by_name[key]
    tokens = key.split()
    if not tokens:
        return None
    surname = tokens[-1]
    candidates = by_surname.get(surname, [])
    if len(candidates) == 1:
        return candidates[0]
    if len(candidates) > 1 and len(tokens) >= 2:
        first = tokens[0]
        for c in candidates:
            c_tokens = canonical_player_name(c.get("name_normalized", "")).split()
            if c_tokens and c_tokens[0][:1] == first[:1]:
                return c
    return None


def contract_risk(months_left: int | None) -> str:
    if months_left is None:
        return "UNKNOWN"
    if months_left <= 6:
        return "HIGH"
    if months_left <= 13:
        return "MEDIUM"
    return "LOW"


def resale_signal(age: int | None, starts: int, goals: int) -> str:
    if age is None:
        return "UNKNOWN"
    if age <= 23 and starts >= 10:
        return "HIGH"
    if age <= 25 and (starts >= 8 or goals >= 5):
        return "MEDIUM"
    if age >= 30:
        return "LOW"
    return "MEDIUM"


def load_attributes(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def load_external_api(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def summarize_attribute(attribute: dict | None) -> dict:
    if not attribute:
        return {"matched": False}
    current = attribute.get("current_ability")
    potential = attribute.get("potential_ability")
    growth = attribute.get("growth_room")
    role_fit = role_fit_score(attribute)
    return {
        "matched": True,
        "source_name": attribute.get("source_name"),
        "current_ability": current,
        "potential_ability": potential,
        "growth_room": growth,
        "physical_score": attribute.get("physical_score"),
        "mental_score": attribute.get("mental_score"),
        "technical_score": attribute.get("technical_score"),
        "role_fit_score": role_fit,
        "raw_attributes": attribute.get("raw_attributes"),
    }


def role_fit_score(attribute: dict) -> float | None:
    scores = [
        attribute.get("physical_score"),
        attribute.get("mental_score"),
        attribute.get("technical_score"),
    ]
    numbers = [score for score in scores if score is not None]
    if not numbers:
        return None
    return round(sum(numbers) / len(numbers), 2)


def summarize_fm23(item: dict | None) -> dict:
    if not item:
        return {"matched": False}
    return {
        "matched": True,
        "source_name": "FM2023",
        "name": item.get("name"),
        "team": item.get("team"),
        "current_ability": item.get("current_ability"),
        "potential_ability": item.get("potential_ability"),
        "growth_room": item.get("growth_room"),
        "physical_score": item.get("physical_score"),
        "mental_score": item.get("mental_score"),
        "technical_score": item.get("technical_score"),
        "raw_attributes": item.get("raw_attributes"),
    }


def summarize_derived(item: dict | None) -> dict:
    if not item:
        return {"matched": False}
    raw = item.get("raw_attributes") or {}
    return {
        "matched": True,
        "source_name": "Türetilmiş",
        "current_ability": item.get("current_ability"),
        "potential_ability": item.get("potential_ability"),
        "raw_attributes": raw,
    }


def summarize_external_api(player: dict | None) -> dict:
    if not player:
        return {"matched": False}
    return {
        "matched": True,
        "source_name": "API-Football",
        "season": 2024,
        "name": player.get("name"),
        "team": player.get("team"),
        "position": player.get("position"),
        "rating": player.get("rating"),
        "minutes": player.get("minutes"),
        "goals": player.get("goals"),
        "assists": player.get("assists"),
        "shots_on": player.get("shots_on"),
        "key_passes": player.get("key_passes"),
        "duels_won": player.get("duels_won"),
        "tackles": player.get("tackles"),
        "interceptions": player.get("interceptions"),
        "yellow_cards": player.get("yellow_cards"),
        "red_cards": player.get("red_cards"),
        "external_role_score": player.get("external_role_score"),
    }


def best_external_match(player: dict, external_players: list[dict]) -> dict | None:
    if not external_players:
        return None
    player_name = canonical_player_name(player.get("name"))
    player_team = normalize_name(player.get("team"))
    best = None
    best_score = 0.0
    for candidate in external_players:
        candidate_name = canonical_player_name(candidate.get("name"))
        candidate_team = normalize_name(candidate.get("team"))
        score = match_score(player_name, player_team, candidate_name, candidate_team)
        if score > best_score:
            best = candidate
            best_score = score
    if best_score >= 0.78:
        matched = dict(best)
        matched["match_confidence"] = round(best_score, 2)
        return matched
    return None


def match_score(player_name: str, player_team: str, candidate_name: str, candidate_team: str) -> float:
    name_ratio = SequenceMatcher(None, player_name, candidate_name).ratio()
    player_token_list = significant_token_list(player_name)
    candidate_token_list = significant_token_list(candidate_name)
    player_tokens = set(player_token_list)
    candidate_tokens = set(candidate_token_list)
    common_name = player_tokens & candidate_tokens
    team_overlap = token_overlap(significant_tokens(player_team), significant_tokens(candidate_team))
    surname_match = bool(player_token_list and candidate_tokens and player_token_list[-1] in candidate_tokens)
    initial_match = bool(
        player_token_list
        and candidate_token_list
        and player_token_list[0][:1] == candidate_token_list[0][:1]
        and (common_name or surname_match)
    )

    token_score = len(common_name) / max(1, min(len(player_tokens), len(candidate_tokens)))
    score = name_ratio * 0.42 + token_score * 0.30 + team_overlap * 0.28
    if surname_match and team_overlap > 0:
        score = max(score, 0.76)
    if initial_match and team_overlap > 0:
        score = max(score, 0.74)
    if team_overlap == 0 and player_name != candidate_name:
        score = min(score, 0.69)
    return score


def significant_tokens(value: str) -> set[str]:
    return set(significant_token_list(value))


def significant_token_list(value: str) -> list[str]:
    stopwords = {"A", "AS", "AŞ", "SK", "FK", "FC", "CF", "SPOR", "FUTBOL", "KULUBU", "KULÜBÜ", "RAMS"}
    return [token for token in normalize_name(value).split() if len(token) > 1 and token not in stopwords]


def token_overlap(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    return len(left & right) / max(1, min(len(left), len(right)))


def opportunity_score(profile: dict, player: dict, attribute: dict | None = None, external_api: dict | None = None) -> float:
    age = profile.get("age") or 30
    contract = profile.get("contract_months_left") or 0
    age_bonus = max(0, 26 - age) * 2.0 if age <= 26 else max(-8, (26 - age) * 0.8)
    contract_bonus = 12 if 0 <= contract <= 13 else min(8, contract * 0.18)
    production = player["scout_value_score"] * 0.72 + player["availability_score"] * 0.12
    discipline_penalty = 4 if player["discipline_risk"] == "HIGH" else 1 if player["discipline_risk"] == "MEDIUM" else 0
    attribute_bonus = 0.0
    if attribute:
        growth = attribute.get("growth_room") or 0
        role_fit = role_fit_score(attribute) or 0
        current = attribute.get("current_ability") or 0
        attribute_bonus = min(10, growth * 0.08) + min(8, role_fit * 0.18) + min(5, current * 0.025)
    external_bonus = external_api_bonus(external_api)
    return round(production + age_bonus + contract_bonus + attribute_bonus + external_bonus - discipline_penalty, 2)


def external_api_bonus(external_api: dict | None) -> float:
    if not external_api:
        return 0.0
    role = external_api.get("external_role_score") or 0
    rating = external_api.get("rating") or 0
    minutes = external_api.get("minutes") or 0
    contribution = min(10, role * 0.028) + min(4, max(0, rating - 6.6) * 3.5) + min(3, minutes / 900)
    return round(contribution, 2)


def build_markdown(payload: dict) -> str:
    summary = payload["summary"]
    lines = [
        "# Zenginleştirilmiş Lig Scout Havuzu",
        "",
        f"- Profilli oyuncu: {summary['profiled_players']}",
        f"- U24 oyuncu: {summary['u24_players']}",
        f"- Sözleşme riski/fırsatı: {summary['contract_risk_players']}",
        f"- Attribute kaynağı: {summary.get('attribute_source') or 'Yok'}",
        f"- Attribute eşleşen oyuncu: {summary.get('attribute_matched_players', 0)}",
        f"- Dış API kaynağı: {summary.get('external_api_source') or 'Yok'}",
        f"- Dış API eşleşen oyuncu: {summary.get('external_api_matched_players', 0)}",
        "",
        "## Fırsat Skoru",
        "",
    ]
    for player in payload["enriched_shortlist"][:20]:
        lines.append(
            f"- {player['name']} ({player['team']}): fırsat={player['opportunity_score']}, scout={player['scout_value_score']}, "
            f"yaş={player.get('age')}, gol={player['goals']}, ilk 11={player['starts']}, "
            f"sözleşme={player.get('contract_end') or 'Yok'}, resale={player['resale_signal']}, "
            f"rol-fit={player.get('attribute_signal', {}).get('role_fit_score') or 'Yok'}, "
            f"dış-api={player.get('external_api_signal', {}).get('external_role_score') or 'Yok'}"
        )
    lines.extend(["", "## Genç Değer", ""])
    for player in payload["young_value"][:12]:
        lines.append(
            f"- {player['name']} ({player['team']}): yaş={player.get('age')}, fırsat={player['opportunity_score']}, "
            f"ilk 11={player['starts']}, gol={player['goals']}, sözleşme={player.get('contract_end') or 'Yok'}"
        )
    lines.extend(["", "## Sözleşme Fırsatları", ""])
    for player in payload["contract_opportunities"][:12]:
        lines.append(
            f"- {player['name']} ({player['team']}): risk={player['contract_risk']}, kalan ay={player.get('contract_months_left')}, "
            f"fırsat={player['opportunity_score']}, scout={player['scout_value_score']}"
        )
    return "\n".join(lines)


if __name__ == "__main__":
    main()
