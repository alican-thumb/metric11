from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from src.collectors.tff_player import probe_player_profile
from src.config import PROCESSED_DIR, RAW_DIR


def main() -> None:
    parser = argparse.ArgumentParser(description="TFF oyuncu profil sayfalarindan yas/sozlesme gibi profil verisi toplar.")
    parser.add_argument("--matches", default=str(PROCESSED_DIR / "tff_trendyol_super_lig_2025_2026_matches.json"))
    parser.add_argument("--team", default=None, help="Sadece belirli takim oyunculari. Ornek: BEŞİKTAŞ A.Ş.")
    parser.add_argument("--scout-input", default=None, help="Scout JSON dosyasindaki scout_shortlist oyuncularini toplar.")
    parser.add_argument("--scout-limit", type=int, default=40)
    parser.add_argument("--player-ids", default=None, help="Virgulle ayrilmis TFF oyuncu ID listesi.")
    parser.add_argument("--player-ids-file", default=None, help="Satir satir TFF oyuncu ID listesi.")
    parser.add_argument("--limit", type=int, default=80)
    parser.add_argument("--sleep", type=float, default=0.35)
    parser.add_argument("--output", default=str(PROCESSED_DIR / "tff_player_profiles_2025_2026.json"))
    args = parser.parse_args()

    matches = json.loads(Path(args.matches).read_text(encoding="utf-8"))
    players = select_players(matches, args)
    selected = players[: args.limit] if args.limit else players
    output_path = Path(args.output)
    existing = load_existing(output_path)
    raw_dir = RAW_DIR / "tff_player_profiles"
    raw_dir.mkdir(parents=True, exist_ok=True)

    profiles = dict(existing)
    errors = []
    for idx, player in enumerate(selected, start=1):
        player_id = player["external_id"]
        if player_id in profiles:
            continue
        probe = probe_player_profile(player_id, include_raw=True)
        if probe.raw_html:
            (raw_dir / f"player_{player_id}.html").write_text(probe.raw_html, encoding="utf-8")
        if probe.profile:
            profile = {**player, **probe.profile}
            profiles[player_id] = profile
            print(f"[{idx}/{len(selected)}] OK {profile.get('name') or player['name']}")
        else:
            errors.append({"player": player, "error": probe.error, "status_code": probe.status_code})
            print(f"[{idx}/{len(selected)}] ERR {player['name']}: {probe.error}")
        output_path.write_text(json.dumps(sorted(profiles.values(), key=lambda item: item["name"]), ensure_ascii=False, indent=2), encoding="utf-8")
        time.sleep(args.sleep)

    report_path = output_path.with_suffix(".md")
    report_path.write_text(build_report(list(profiles.values()), errors, args.team), encoding="utf-8")
    print(report_path)


def collect_unique_players(matches: list[dict], team_filter: str | None) -> list[dict]:
    players = {}
    for match in matches:
        for side in ("home", "away"):
            team_name = match[f"{side}_team"]["name"]
            if team_filter and team_filter.casefold() not in team_name.casefold():
                continue
            for group in ("starting", "bench"):
                for player in match["lineups"][side][group]:
                    external_id = player.get("external_id")
                    if not external_id:
                        continue
                    players[external_id] = {
                        "external_id": external_id,
                        "name": player.get("name"),
                        "team_from_match": team_name,
                    }
    return sorted(players.values(), key=lambda item: (item["team_from_match"], item["name"]))


def select_players(matches: list[dict], args: argparse.Namespace) -> list[dict]:
    if args.player_ids:
        return [{"external_id": player_id.strip(), "name": player_id.strip(), "team_from_match": None} for player_id in args.player_ids.split(",") if player_id.strip()]
    if args.player_ids_file:
        ids = [
            line.strip()
            for line in Path(args.player_ids_file).read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        return [{"external_id": player_id, "name": player_id, "team_from_match": None} for player_id in ids]
    if args.scout_input:
        scout_payload = json.loads(Path(args.scout_input).read_text(encoding="utf-8"))
        return [
            {
                "external_id": str(player["player_id"]),
                "name": player["name"],
                "team_from_match": player.get("team"),
            }
            for player in scout_payload.get("scout_shortlist", [])[: args.scout_limit]
            if str(player.get("player_id", "")).isdigit()
        ]
    return collect_unique_players(matches, args.team)


def load_existing(path: Path) -> dict:
    if not path.exists():
        return {}
    return {item["external_id"]: item for item in json.loads(path.read_text(encoding="utf-8"))}


def build_report(profiles: list[dict], errors: list[dict], team_filter: str | None) -> str:
    ages = [profile["age"] for profile in profiles if profile.get("age") is not None]
    contracts = [profile["contract_months_left"] for profile in profiles if profile.get("contract_months_left") is not None]
    expiring = [profile for profile in profiles if profile.get("contract_months_left") is not None and profile["contract_months_left"] <= 13]
    young = [profile for profile in profiles if profile.get("age") is not None and profile["age"] <= 23]
    lines = [
        "# TFF Oyuncu Profilleri",
        "",
        f"- Takım filtresi: {team_filter or 'Yok'}",
        f"- Profil sayısı: {len(profiles)}",
        f"- Hata sayısı: {len(errors)}",
        f"- Ortalama yaş: {round(sum(ages) / len(ages), 1) if ages else 'Yok'}",
        f"- Ortalama kalan sözleşme ayı: {round(sum(contracts) / len(contracts), 1) if contracts else 'Yok'}",
        f"- 23 yaş ve altı oyuncu: {len(young)}",
        f"- 13 ay içinde sözleşmesi bitecek oyuncu: {len(expiring)}",
        "",
        "## Genç Oyuncular",
        "",
    ]
    for profile in sorted(young, key=lambda item: (item.get("age") or 99, item["name"]))[:30]:
        lines.append(
            f"- {profile['name']} ({profile.get('club') or profile.get('team_from_match')}): "
            f"yaş={profile.get('age')}, sözleşme bitiş={profile.get('contract_end') or 'Yok'}"
        )
    lines.extend(["", "## Sözleşme Fırsatları", ""])
    for profile in sorted(expiring, key=lambda item: item.get("contract_months_left") or 999)[:30]:
        lines.append(
            f"- {profile['name']} ({profile.get('club') or profile.get('team_from_match')}): "
            f"kalan ay={profile.get('contract_months_left')}, bitiş={profile.get('contract_end')}"
        )
    return "\n".join(lines)


if __name__ == "__main__":
    main()
