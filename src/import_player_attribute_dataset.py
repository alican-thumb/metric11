from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from src.config import PROCESSED_DIR
from src.normalization import normalize_name


FIELD_ALIASES = {
    "name": ["name", "player", "player_name", "full_name", "Name"],
    "team": ["club", "team", "Club", "Team"],
    "age": ["age", "Age"],
    "position": ["position", "positions", "best_position", "Position"],
    "current_ability": ["ca", "current_ability", "Current Ability", "CurrentAbility", "overall", "Overall"],
    "potential_ability": ["pa", "potential_ability", "Potential Ability", "PotentialAbility", "potential", "Potential"],
    "market_value": ["value", "Value", "market_value", "market_value_eur"],
    "wage": ["wage", "Wage"],
    "pace": ["pace", "Pace"],
    "acceleration": ["acceleration", "Acceleration", "accel"],
    "stamina": ["stamina", "Stamina"],
    "work_rate": ["work_rate", "Work Rate", "workrate", "Workrate"],
    "teamwork": ["teamwork", "Teamwork"],
    "finishing": ["finishing", "Finishing"],
    "passing": ["passing", "Passing", "short_passing", "ShortPassing", "Short Passing"],
    "tackling": ["tackling", "Tackling", "standing_tackle", "StandingTackle"],
    "positioning": ["positioning", "Positioning", "Off The Ball"],
    "decisions": ["decisions", "Decisions", "Decision"],
    "technique": ["technique", "Technique"],
    "vision": ["vision", "Vision"],
    # FM2023 extended attributes
    "dribbling": ["dribbling", "Dribbling"],
    "first_touch": ["first_touch", "First Touch"],
    "heading": ["heading", "Heading"],
    "long_shots": ["long_shots", "Long Shots"],
    "crossing": ["crossing", "Crossing"],
    "marking": ["marking", "Marking"],
    "composure": ["composure", "Composure"],
    "concentration": ["concentration", "Concentration"],
    "anticipation": ["anticipation", "Anticipation"],
    "flair": ["flair", "Flair"],
    "strength": ["strength", "Strength"],
    "agility": ["agility", "Agility"],
    "balance": ["balance", "Balance"],
    "jumping": ["jumping", "Jumping Reach"],
    "natural_fitness": ["natural_fitness", "Natural Fitness"],
}


def main() -> None:
    parser = argparse.ArgumentParser(description="FM/FIFA tarzı oyuncu attribute CSV dosyasını normalize eder.")
    parser.add_argument("--input", required=True, help="CSV dosya yolu")
    parser.add_argument("--source-name", required=True)
    parser.add_argument("--source-url", default="")
    parser.add_argument("--license-status", default="VERIFY_BEFORE_COMMERCIAL_USE")
    parser.add_argument("--risk-level", choices=["LOW", "MEDIUM", "HIGH"], default="MEDIUM")
    parser.add_argument("--output", default=str(PROCESSED_DIR / "player_attribute_dataset_normalized.json"))
    args = parser.parse_args()

    payload = import_dataset(
        Path(args.input),
        source_name=args.source_name,
        source_url=args.source_url,
        license_status=args.license_status,
        risk_level=args.risk_level,
    )
    output_path = Path(args.output)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path = output_path.with_suffix(".md")
    md_path.write_text(build_markdown(payload), encoding="utf-8")
    print(md_path.read_text(encoding="utf-8"))


def import_dataset(
    input_path: Path,
    source_name: str,
    source_url: str,
    license_status: str,
    risk_level: str,
) -> dict:
    with input_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)

    normalized = []
    for row in rows:
        player = normalize_row(row)
        if not player.get("name"):
            continue
        normalized.append(player)

    return {
        "source": {
            "name": source_name,
            "url": source_url,
            "license_status": license_status,
            "risk_level": risk_level,
            "input_path": str(input_path),
        },
        "summary": {
            "rows_in": len(rows),
            "players_out": len(normalized),
            "with_current_ability": sum(1 for item in normalized if item.get("current_ability") is not None),
            "with_potential_ability": sum(1 for item in normalized if item.get("potential_ability") is not None),
            "with_physical_signal": sum(1 for item in normalized if item.get("physical_score") is not None),
        },
        "players": normalized,
    }


def normalize_row(row: dict) -> dict:
    item = {field: get_value(row, aliases) for field, aliases in FIELD_ALIASES.items()}
    name = str(item.get("name") or "").strip()
    current_ability = to_float(item.get("current_ability"))
    potential_ability = to_float(item.get("potential_ability"))
    physical_score = average_present([
        item.get("pace"), item.get("acceleration"), item.get("stamina"),
        item.get("strength"), item.get("agility"), item.get("natural_fitness"),
    ])
    mental_score = average_present([
        item.get("teamwork"), item.get("positioning"), item.get("decisions"),
        item.get("vision"), item.get("anticipation"), item.get("concentration"), item.get("composure"),
    ])
    technical_score = average_present([
        item.get("finishing"), item.get("passing"), item.get("tackling"),
        item.get("technique"), item.get("dribbling"), item.get("first_touch"),
    ])

    return {
        "name": name,
        "name_normalized": normalize_name(name),
        "team": clean_text(item.get("team")),
        "age": to_int(item.get("age")),
        "position": clean_text(item.get("position")),
        "current_ability": current_ability,
        "potential_ability": potential_ability,
        "growth_room": round(potential_ability - current_ability, 2)
        if current_ability is not None and potential_ability is not None
        else None,
        "market_value": clean_text(item.get("market_value")),
        "wage": clean_text(item.get("wage")),
        "physical_score": physical_score,
        "mental_score": mental_score,
        "technical_score": technical_score,
        "raw_attributes": {
            key: to_float(item.get(key))
            for key in (
                "pace", "acceleration", "stamina", "work_rate",
                "teamwork", "finishing", "passing", "tackling",
                "positioning", "decisions", "technique", "vision",
                "dribbling", "first_touch", "heading", "long_shots",
                "crossing", "marking", "composure", "concentration",
                "anticipation", "flair", "strength", "agility",
                "balance", "jumping", "natural_fitness",
            )
            if item.get(key) not in (None, "")
        },
    }


def get_value(row: dict, aliases: list[str]):
    lower_map = {key.lower().strip(): value for key, value in row.items()}
    for alias in aliases:
        if alias in row and row[alias] not in (None, ""):
            return row[alias]
        value = lower_map.get(alias.lower().strip())
        if value not in (None, ""):
            return value
    return None


def clean_text(value) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def to_float(value) -> float | None:
    if value is None or value == "":
        return None
    text = str(value).strip().replace(",", ".")
    text = text.replace("€", "").replace("£", "").replace("$", "").replace("M", "").replace("m", "")
    try:
        return float(text)
    except ValueError:
        return None


def to_int(value) -> int | None:
    number = to_float(value)
    if number is None:
        return None
    return int(number)


def average_present(values: list) -> float | None:
    numbers = [to_float(value) for value in values]
    numbers = [number for number in numbers if number is not None]
    if not numbers:
        return None
    return round(sum(numbers) / len(numbers), 2)


def build_markdown(payload: dict) -> str:
    summary = payload["summary"]
    source = payload["source"]
    lines = [
        "# Oyuncu Attribute Import Raporu",
        "",
        f"- Kaynak: {source['name']}",
        f"- Lisans durumu: {source['license_status']}",
        f"- Risk: {source['risk_level']}",
        f"- Ham satır: {summary['rows_in']}",
        f"- Normalize oyuncu: {summary['players_out']}",
        f"- Current ability bulunan: {summary['with_current_ability']}",
        f"- Potential ability bulunan: {summary['with_potential_ability']}",
        f"- Fiziksel sinyal bulunan: {summary['with_physical_signal']}",
        "",
        "## İlk 20",
        "",
    ]
    for player in payload["players"][:20]:
        lines.append(
            f"- {player['name']} ({player.get('team') or 'Yok'}): pos={player.get('position') or 'Yok'}, "
            f"CA={player.get('current_ability')}, PA={player.get('potential_ability')}, "
            f"fizik={player.get('physical_score')}, mental={player.get('mental_score')}"
        )
    return "\n".join(lines)


if __name__ == "__main__":
    main()
