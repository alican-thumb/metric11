from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path

from bs4 import BeautifulSoup

from src.collect_transfermarkt_squad import fetch
from src.config import PROCESSED_DIR, RAW_DIR, SEASON


def main() -> None:
    parser = argparse.ArgumentParser(description="Transfermarkt lig kadrosundaki tüm oyuncuların profil tam adlarını toplar.")
    parser.add_argument("--squads", default=str(PROCESSED_DIR / f"transfermarkt_super_lig_squads_{SEASON}.json"))
    parser.add_argument("--output", default=str(PROCESSED_DIR / f"transfermarkt_super_lig_player_profiles_{SEASON}.json"))
    parser.add_argument("--delay-seconds", type=float, default=1.0)
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument("--player-ids-file", default=None, help="İsteğe bağlı Transfermarkt ID listesi; tam koşu öncesi doğrulama/yeniden deneme için.")
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    squads = json.loads(Path(args.squads).read_text(encoding="utf-8"))
    raw_dir = RAW_DIR / "transfermarkt" / f"transfermarkt_super_lig_player_profiles_{SEASON}"
    raw_dir.mkdir(parents=True, exist_ok=True)
    existing = json.loads(Path(args.output).read_text(encoding="utf-8")) if Path(args.output).exists() else {}
    players_by_id = {str(item["transfermarkt_id"]): item for item in existing.get("players", [])}
    failed: list[dict] = []
    selected_ids = None
    if args.player_ids_file:
        selected_ids = {
            line.strip() for line in Path(args.player_ids_file).read_text(encoding="utf-8").splitlines() if line.strip()
        }
    roster = [
        (club, player)
        for club in squads.get("clubs", [])
        for player in club.get("players", [])
        if not selected_ids or str(player.get("transfermarkt_id") or "") in selected_ids
    ]
    if args.limit:
        roster = roster[: args.limit]
    for index, (club, player) in enumerate(roster, start=1):
        player_id = str(player.get("transfermarkt_id") or "")
        if not player_id:
            continue
        raw_path = raw_dir / f"{player_id}.html"
        try:
            if args.skip_existing and raw_path.exists():
                html = raw_path.read_text(encoding="utf-8")
            else:
                html = fetch(player["profile_url"])
                raw_path.write_text(html, encoding="utf-8")
                time.sleep(args.delay_seconds)
            players_by_id[player_id] = {
                **parse_profile(html),
                "transfermarkt_id": player_id,
                "squad_name": player.get("name"),
                "team_name": club.get("team_name"),
                "profile_url": player.get("profile_url"),
            }
            if index == 1 or index % 25 == 0 or index == len(roster):
                print(f"[{index}/{len(roster)}] OK {club.get('team_name')} / {player.get('name')}")
        except Exception as exc:  # noqa: BLE001 - partial collection remains useful and visible
            failed.append(
                {
                    "transfermarkt_id": player_id,
                    "squad_name": player.get("name"),
                    "team_name": club.get("team_name"),
                    "profile_url": player.get("profile_url"),
                    "error": str(exc),
                }
            )

    players = sorted(players_by_id.values(), key=lambda item: (item.get("team_name") or "", item.get("squad_name") or ""))
    with_full_name = sum(1 for player in players if player.get("full_name"))
    payload = {
        "source": "Transfermarkt player profiles",
        "source_type": "SCRAPING",
        "risk_level": "HIGH",
        "license_status": "VERIFY_TERMS_BEFORE_COMMERCIAL_USE",
        "players": players,
        "failed": failed,
        "summary": {
            "clubs": len(squads.get("clubs", [])),
            "squad_players": squads.get("summary", {}).get("players", 0),
            "requested_profiles": len(roster),
            "profiles_collected": len(players),
            "profiles_with_full_name": with_full_name,
            "failed_profiles": len(failed),
        },
    }
    output = Path(args.output)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    output.with_suffix(".md").write_text(build_markdown(payload), encoding="utf-8")
    print(output.with_suffix(".md").read_text(encoding="utf-8"))


def parse_profile(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    heading = soup.select_one("h1.data-header__headline-wrapper")
    display_name = heading.get_text(" ", strip=True) if heading else None
    full_name = None
    for label in soup.select("span.info-table__content--regular"):
        label_text = label.get_text(" ", strip=True).casefold()
        if label_text not in {"full name:", "name in home country:"}:
            continue
        sibling = label.find_next_sibling("span")
        if sibling and sibling.get_text(" ", strip=True):
            full_name = sibling.get_text(" ", strip=True)
            break
    if not full_name:
        meta = soup.find("meta", attrs={"name": "description"})
        content = meta.get("content", "") if meta else ""
        match = re.search(r"Full name:\s*([^,|]+)", content, re.IGNORECASE)
        full_name = match.group(1).strip() if match else None
    return {"display_name": display_name, "full_name": full_name}


def build_markdown(payload: dict) -> str:
    summary = payload["summary"]
    lines = [
        "# Transfermarkt Lig Geneli Oyuncu Profil Tam-Ad Katmanı",
        "",
        f"- Kadro kulübü: {summary['clubs']}/18",
        f"- Kadro oyuncusu: {summary['squad_players']}",
        f"- Bu koşuda istenen profil: {summary['requested_profiles']}",
        f"- Toplanan profil: {summary['profiles_collected']}",
        f"- Tam ad bulunan profil: {summary['profiles_with_full_name']}",
        f"- Başarısız profil: {summary['failed_profiles']}",
        f"- Risk: {payload['risk_level']}",
        f"- Lisans durumu: {payload['license_status']}",
        "",
        "## Takım Kapsamı",
        "",
    ]
    teams = sorted({item["team_name"] for item in payload["players"]})
    for team in teams:
        rows = [item for item in payload["players"] if item["team_name"] == team]
        lines.append(f"- {team}: profil={len(rows)}, tam_ad={sum(1 for item in rows if item.get('full_name'))}")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
