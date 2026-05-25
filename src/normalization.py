from __future__ import annotations

import json
import re
import unicodedata
from functools import lru_cache
from pathlib import Path

from src.config import ROOT_DIR


TEAM_ALIASES = {
    "NATURA DÜNYASI GENÇLERBİRLİĞİ": "GENÇLERBİRLİĞİ",
    "FATİH KARAGÜMRÜK A.Ş.": "MISIRLI.COM.TR FATİH KARAGÜMRÜK",
}

LATIN_NAME_TRANSLATION = str.maketrans(
    {
        "Ø": "O",
        "ø": "o",
        "Ł": "L",
        "ł": "l",
        "Đ": "D",
        "đ": "d",
        "Ð": "D",
        "ð": "d",
        "Þ": "TH",
        "þ": "th",
        "Æ": "AE",
        "æ": "ae",
        "Œ": "OE",
        "œ": "oe",
        "ß": "ss",
    }
)


def normalize_team_name(name: str | None) -> str | None:
    if name is None:
        return None
    cleaned = re.sub(r"\s+", " ", name).strip()
    return TEAM_ALIASES.get(cleaned, cleaned)


def normalize_name(name: str | None) -> str:
    if not name:
        return ""
    cleaned = unicodedata.normalize("NFKD", str(name).translate(LATIN_NAME_TRANSLATION))
    cleaned = "".join(ch for ch in cleaned if not unicodedata.combining(ch))
    cleaned = cleaned.upper()
    cleaned = re.sub(r"[^A-Z0-9 ]+", " ", cleaned)
    return re.sub(r"\s+", " ", cleaned).strip()


@lru_cache(maxsize=1)
def player_alias_map() -> dict[str, str]:
    path = ROOT_DIR / "data" / "manual" / "player_aliases.json"
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    aliases: dict[str, str] = {}
    for player in data.get("players", []):
        canonical = player.get("canonical_name")
        canonical_norm = normalize_name(canonical)
        if not canonical_norm:
            continue
        aliases[canonical_norm] = canonical_norm
        for alias in player.get("aliases", []):
            alias_norm = normalize_name(alias)
            if alias_norm:
                aliases[alias_norm] = canonical_norm
    return aliases


def canonical_player_name(name: str | None) -> str:
    normalized = normalize_name(name)
    return player_alias_map().get(normalized, normalized)


def name_tokens(name: str | None) -> list[str]:
    return canonical_player_name(name).split()


def normalize_match_teams(match: dict) -> dict:
    copied = dict(match)
    copied["home_team"] = dict(match["home_team"])
    copied["away_team"] = dict(match["away_team"])
    copied["home_team"]["name"] = normalize_team_name(copied["home_team"]["name"])
    copied["away_team"]["name"] = normalize_team_name(copied["away_team"]["name"])
    return copied


def normalize_matches(matches: list[dict]) -> list[dict]:
    return [normalize_match_teams(match) for match in matches]
