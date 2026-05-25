from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.config import PROCESSED_DIR


def main() -> None:
    parser = argparse.ArgumentParser(description="API-Football snapshot verisini normalize edip raporlar.")
    parser.add_argument("--input", default=str(PROCESSED_DIR / "api_football_super_lig_snapshot_2024.json"))
    parser.add_argument("--output-prefix", default="api_football_super_lig_2024_analysis")
    args = parser.parse_args()

    snapshot = json.loads(Path(args.input).read_text(encoding="utf-8"))
    payload = build_payload(snapshot)
    json_path = PROCESSED_DIR / f"{args.output_prefix}.json"
    md_path = PROCESSED_DIR / f"{args.output_prefix}.md"
    html_path = PROCESSED_DIR / f"{args.output_prefix}.html"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(build_markdown(payload), encoding="utf-8")
    html_path.write_text(build_html(payload), encoding="utf-8")
    print(md_path.read_text(encoding="utf-8"))


def build_payload(snapshot: dict) -> dict:
    data = snapshot.get("data", {})
    standings = normalize_standings(data.get("standings", []))
    fixtures = normalize_fixtures(data.get("fixtures", []))
    teams = normalize_teams(data.get("teams", []))
    scorers = normalize_players(data.get("topscorers", []), "goals")
    assists = normalize_players(data.get("topassists", []), "assists")
    cards = normalize_players(data.get("topcards", []), "cards")
    team_strength = build_team_strength(standings, fixtures)
    return {
        "source": snapshot.get("summary", {}),
        "summary": {
            "teams": len(teams),
            "fixtures": len(fixtures),
            "standings_rows": len(standings),
            "top_scorers": len(scorers),
            "top_assists": len(assists),
            "top_cards": len(cards),
        },
        "teams": teams,
        "standings": standings,
        "fixtures": fixtures,
        "team_strength": team_strength,
        "top_scorers": scorers,
        "top_assists": assists,
        "top_cards": cards,
        "player_attribute_pool": build_attribute_pool(scorers, assists, cards),
    }


def normalize_standings(rows: list[dict]) -> list[dict]:
    if not rows:
        return []
    table = rows[0].get("league", {}).get("standings", [[]])[0]
    normalized = []
    for row in table:
        all_stats = row.get("all", {})
        goals = all_stats.get("goals", {})
        normalized.append(
            {
                "rank": row.get("rank"),
                "team_id": row.get("team", {}).get("id"),
                "team": row.get("team", {}).get("name"),
                "points": row.get("points"),
                "goals_diff": row.get("goalsDiff"),
                "played": all_stats.get("played"),
                "wins": all_stats.get("win"),
                "draws": all_stats.get("draw"),
                "losses": all_stats.get("lose"),
                "goals_for": goals.get("for"),
                "goals_against": goals.get("against"),
                "form": row.get("form"),
            }
        )
    return normalized


def normalize_teams(rows: list[dict]) -> list[dict]:
    return [
        {
            "team_id": row.get("team", {}).get("id"),
            "name": row.get("team", {}).get("name"),
            "code": row.get("team", {}).get("code"),
            "founded": row.get("team", {}).get("founded"),
            "venue": row.get("venue", {}).get("name"),
            "city": row.get("venue", {}).get("city"),
            "capacity": row.get("venue", {}).get("capacity"),
        }
        for row in rows
    ]


def normalize_fixtures(rows: list[dict]) -> list[dict]:
    normalized = []
    for row in rows:
        fixture = row.get("fixture", {})
        teams = row.get("teams", {})
        goals = row.get("goals", {})
        normalized.append(
            {
                "fixture_id": fixture.get("id"),
                "date": fixture.get("date"),
                "round": row.get("league", {}).get("round"),
                "referee": fixture.get("referee"),
                "venue": fixture.get("venue", {}).get("name"),
                "home": teams.get("home", {}).get("name"),
                "away": teams.get("away", {}).get("name"),
                "home_goals": goals.get("home"),
                "away_goals": goals.get("away"),
                "status": fixture.get("status", {}).get("short"),
            }
        )
    return normalized


def normalize_players(rows: list[dict], list_type: str) -> list[dict]:
    normalized = []
    for row in rows:
        player = row.get("player", {})
        stats = (row.get("statistics") or [{}])[0]
        games = stats.get("games", {})
        goals = stats.get("goals", {})
        shots = stats.get("shots", {})
        passes = stats.get("passes", {})
        tackles = stats.get("tackles", {})
        duels = stats.get("duels", {})
        dribbles = stats.get("dribbles", {})
        fouls = stats.get("fouls", {})
        cards = stats.get("cards", {})
        normalized.append(
            {
                "list_type": list_type,
                "player_id": player.get("id"),
                "name": player.get("name"),
                "age": player.get("age"),
                "nationality": player.get("nationality"),
                "height": player.get("height"),
                "weight": player.get("weight"),
                "injured": player.get("injured"),
                "team_id": stats.get("team", {}).get("id"),
                "team": stats.get("team", {}).get("name"),
                "position": games.get("position"),
                "rating": to_float(games.get("rating")),
                "appearances": games.get("appearences"),
                "lineups": games.get("lineups"),
                "minutes": games.get("minutes"),
                "goals": goals.get("total") or 0,
                "assists": goals.get("assists") or 0,
                "shots": shots.get("total") or 0,
                "shots_on": shots.get("on") or 0,
                "key_passes": passes.get("key") or 0,
                "tackles": tackles.get("total") or 0,
                "interceptions": tackles.get("interceptions") or 0,
                "duels": duels.get("total") or 0,
                "duels_won": duels.get("won") or 0,
                "dribbles": dribbles.get("attempts") or 0,
                "dribbles_success": dribbles.get("success") or 0,
                "fouls_drawn": fouls.get("drawn") or 0,
                "fouls_committed": fouls.get("committed") or 0,
                "yellow_cards": cards.get("yellow") or 0,
                "red_cards": cards.get("red") or 0,
            }
        )
    return normalized


def build_team_strength(standings: list[dict], fixtures: list[dict]) -> list[dict]:
    by_team = {row["team"]: dict(row) for row in standings}
    for team in by_team.values():
        played = team.get("played") or 1
        team["points_per_match"] = round((team.get("points") or 0) / played, 2)
        team["goals_for_per_match"] = round((team.get("goals_for") or 0) / played, 2)
        team["goals_against_per_match"] = round((team.get("goals_against") or 0) / played, 2)
        team["external_strength_score"] = round(
            team["points_per_match"] * 24
            + team["goals_for_per_match"] * 10
            - team["goals_against_per_match"] * 8
            + (team.get("goals_diff") or 0) * 0.25,
            2,
        )
    return sorted(by_team.values(), key=lambda item: item["external_strength_score"], reverse=True)


def build_attribute_pool(*groups: list[dict]) -> list[dict]:
    by_id = {}
    for group in groups:
        for player in group:
            current = by_id.setdefault(player["player_id"], dict(player))
            for key in ("goals", "assists", "shots", "shots_on", "key_passes", "tackles", "interceptions", "duels", "duels_won", "dribbles", "dribbles_success", "fouls_committed", "yellow_cards", "red_cards"):
                current[key] = max(current.get(key) or 0, player.get(key) or 0)
            current["external_role_score"] = role_score(current)
    return sorted(by_id.values(), key=lambda item: item.get("external_role_score", 0), reverse=True)


def role_score(player: dict) -> float:
    attacking = (player.get("goals") or 0) * 5 + (player.get("assists") or 0) * 4 + (player.get("shots_on") or 0) * 0.4
    creation = (player.get("key_passes") or 0) * 0.8 + (player.get("dribbles_success") or 0) * 0.7
    defensive = (player.get("tackles") or 0) * 0.35 + (player.get("interceptions") or 0) * 0.5 + (player.get("duels_won") or 0) * 0.12
    discipline = (player.get("yellow_cards") or 0) * 1.5 + (player.get("red_cards") or 0) * 5
    rating = (player.get("rating") or 6.5) * 8
    return round(attacking + creation + defensive + rating - discipline, 2)


def to_float(value) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def build_markdown(payload: dict) -> str:
    summary = payload["summary"]
    lines = [
        "# API-Football 2024 Süper Lig Analizi",
        "",
        f"- Takım: {summary['teams']}",
        f"- Fikstür: {summary['fixtures']}",
        f"- Puan durumu satırı: {summary['standings_rows']}",
        f"- Gol listesi: {summary['top_scorers']}",
        f"- Asist listesi: {summary['top_assists']}",
        f"- Kart listesi: {summary['top_cards']}",
        "",
        "## Dış API Takım Gücü",
        "",
    ]
    for team in payload["team_strength"][:10]:
        lines.append(
            f"- {team['rank']}. {team['team']}: puan={team['points']}, GF/M={team['goals_for_per_match']}, "
            f"GA/M={team['goals_against_per_match']}, dış güç={team['external_strength_score']}"
        )
    lines.extend(["", "## Dış API Oyuncu Havuzu", ""])
    for player in payload["player_attribute_pool"][:15]:
        lines.append(
            f"- {player['name']} ({player['team']}): pos={player.get('position')}, rating={player.get('rating')}, "
            f"gol={player['goals']}, asist={player['assists']}, key_pass={player['key_passes']}, "
            f"duel_won={player['duels_won']}, skor={player['external_role_score']}"
        )
    return "\n".join(lines)


def build_html(payload: dict) -> str:
    team_rows = "".join(
        f"<tr><td>{team['rank']}</td><td>{team['team']}</td><td>{team['points']}</td><td>{team['goals_for_per_match']}</td><td>{team['goals_against_per_match']}</td><td>{team['external_strength_score']}</td></tr>"
        for team in payload["team_strength"][:12]
    )
    player_rows = "".join(
        f"<tr><td>{player['name']}</td><td>{player['team']}</td><td>{player.get('position') or ''}</td><td>{player.get('rating') or ''}</td><td>{player['goals']}</td><td>{player['assists']}</td><td>{player['key_passes']}</td><td>{player['duels_won']}</td><td>{player['external_role_score']}</td></tr>"
        for player in payload["player_attribute_pool"][:25]
    )
    return f"""<!doctype html>
<html lang="tr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>API-Football 2024 Süper Lig Analizi</title>
  <style>
    body {{ margin:0; font-family:Inter, system-ui, sans-serif; background:#f4f6f8; color:#15181d; }}
    header {{ background:#111318; color:white; padding:28px 42px; border-bottom:4px solid #137a4b; }}
    main {{ max-width:1320px; margin:0 auto; padding:24px; }}
    .metrics {{ display:grid; grid-template-columns:repeat(5,1fr); gap:12px; margin-bottom:18px; }}
    .metric, section {{ background:white; border:1px solid #dce2ea; border-radius:8px; box-shadow:0 8px 22px rgba(18,24,32,.08); }}
    .metric {{ padding:15px; }}
    .metric span {{ display:block; color:#667085; font-size:12px; }}
    .metric strong {{ display:block; font-size:28px; margin-top:5px; }}
    section {{ padding:18px; margin-bottom:18px; }}
    h1 {{ margin:0 0 6px; }} h2 {{ margin:0 0 14px; font-size:18px; }}
    table {{ width:100%; border-collapse:collapse; font-size:14px; }}
    th,td {{ padding:9px 7px; border-bottom:1px solid #e4e8ef; text-align:left; }}
    th {{ color:#667085; font-size:12px; }}
    @media (max-width:900px) {{ .metrics {{ grid-template-columns:1fr 1fr; }} main {{ padding:14px; }} table {{ font-size:12px; }} }}
    @media (max-width:620px) {{ .metrics {{ grid-template-columns:1fr; }} header {{ padding:22px; }} }}
  </style>
</head>
<body>
  <header><h1>API-Football 2024 Süper Lig Analizi</h1><p>Geçmiş sezon dış API verisi: puan durumu, fikstür, oyuncu rating/şut/pas/duel/kart sinyalleri.</p></header>
  <main>
    <div class="metrics">
      {metric("Takım", payload["summary"]["teams"])}
      {metric("Fikstür", payload["summary"]["fixtures"])}
      {metric("Gol listesi", payload["summary"]["top_scorers"])}
      {metric("Asist listesi", payload["summary"]["top_assists"])}
      {metric("Kart listesi", payload["summary"]["top_cards"])}
    </div>
    <section><h2>Dış API Takım Gücü</h2><table><thead><tr><th>Sıra</th><th>Takım</th><th>Puan</th><th>GF/M</th><th>GA/M</th><th>Dış Güç</th></tr></thead><tbody>{team_rows}</tbody></table></section>
    <section><h2>Dış API Oyuncu Havuzu</h2><table><thead><tr><th>Oyuncu</th><th>Takım</th><th>Pozisyon</th><th>Rating</th><th>Gol</th><th>Asist</th><th>Key Pass</th><th>Duel Won</th><th>Rol Skoru</th></tr></thead><tbody>{player_rows}</tbody></table></section>
  </main>
</body>
</html>
"""


def metric(label: str, value) -> str:
    return f'<div class="metric"><span>{label}</span><strong>{value}</strong></div>'


if __name__ == "__main__":
    main()
