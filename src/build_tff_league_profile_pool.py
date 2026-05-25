from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.collect_tff_player_profiles import collect_unique_players
from src.config import PROCESSED_DIR, SEASON


def main() -> None:
    parser = argparse.ArgumentParser(description="Mevcut TFF profil parçalarını lig-geneli tek havuzda birleştirir.")
    parser.add_argument("--matches", default=str(PROCESSED_DIR / "tff_trendyol_super_lig_2025_2026_matches.json"))
    parser.add_argument("--output", default=str(PROCESSED_DIR / f"tff_player_profiles_league_all_{SEASON}.json"))
    parser.add_argument(
        "--inputs",
        nargs="*",
        default=[
            str(PROCESSED_DIR / f"tff_player_profiles_all_priority_{SEASON}.json"),
            str(PROCESSED_DIR / f"tff_player_profiles_besiktas_{SEASON}.json"),
        ],
    )
    args = parser.parse_args()

    output = Path(args.output)
    input_paths = [Path(value) for value in args.inputs]
    if output.exists():
        input_paths.append(output)
    profiles: dict[str, dict] = {}
    for path in input_paths:
        if not path.exists():
            continue
        for profile in json.loads(path.read_text(encoding="utf-8")):
            player_id = str(profile.get("external_id") or "")
            if player_id:
                profiles[player_id] = {**profiles.get(player_id, {}), **profile}

    matches = json.loads(Path(args.matches).read_text(encoding="utf-8"))
    match_players = collect_unique_players(matches, None)
    match_ids = {str(player["external_id"]) for player in match_players}
    missing = [player for player in match_players if str(player["external_id"]) not in profiles]
    rows = sorted(profiles.values(), key=lambda item: (item.get("club") or "", item.get("name") or ""))
    output.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    ids_path = output.with_name(f"{output.stem}_missing_ids.txt")
    ids_path.write_text("\n".join(str(item["external_id"]) for item in missing), encoding="utf-8")
    output.with_suffix(".md").write_text(
        build_markdown(rows, match_ids, missing, [path for path in input_paths if path.exists()]),
        encoding="utf-8",
    )
    print(output.with_suffix(".md").read_text(encoding="utf-8"))


def build_markdown(profiles: list[dict], match_ids: set[str], missing: list[dict], input_paths: list[Path]) -> str:
    present_match_profiles = sum(1 for item in profiles if str(item.get("external_id")) in match_ids)
    lines = [
        "# TFF Lig Geneli Oyuncu Profil Havuzu",
        "",
        f"- Kaynak parça dosyası: {len(input_paths)}",
        f"- Birleşik profil: {len(profiles)}",
        f"- Maç kadrosunda benzersiz oyuncu: {len(match_ids)}",
        f"- Maç kadrosunda profili bulunan: {present_match_profiles}",
        f"- Henüz profil eksik maç-kadrosu oyuncusu: {len(missing)}",
        "",
        "## Eksik Profiller",
        "",
    ]
    for item in missing:
        lines.append(f"- {item.get('name')} ({item.get('team_from_match')}): TFF ID={item.get('external_id')}")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
