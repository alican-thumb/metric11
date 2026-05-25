from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from html import escape
from pathlib import Path

from src.analyze_api_football_snapshot import normalize_players, role_score
from src.config import PROCESSED_DIR


def main() -> None:
    parser = argparse.ArgumentParser(description="API-Football derin snapshot verisini oyuncu, kadro ve sakatlık sinyaline çevirir.")
    parser.add_argument("--input", default=str(PROCESSED_DIR / "api_football_super_lig_deep_snapshot_2024.json"))
    parser.add_argument("--top-analysis", default=str(PROCESSED_DIR / "api_football_super_lig_2024_analysis.json"))
    parser.add_argument("--output-prefix", default="api_football_super_lig_deep_2024_analysis")
    args = parser.parse_args()

    snapshot = json.loads(Path(args.input).read_text(encoding="utf-8"))
    top_analysis = load_optional(Path(args.top_analysis))
    payload = build_payload(snapshot, top_analysis)

    json_path = PROCESSED_DIR / f"{args.output_prefix}.json"
    md_path = PROCESSED_DIR / f"{args.output_prefix}.md"
    html_path = PROCESSED_DIR / f"{args.output_prefix}.html"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(build_markdown(payload), encoding="utf-8")
    html_path.write_text(build_html(payload), encoding="utf-8")
    print(md_path.read_text(encoding="utf-8"))


def load_optional(path: str) -> dict:
    target = Path(path)
    if not target.exists():
        return {}
    return json.loads(target.read_text(encoding="utf-8"))


def build_payload(snapshot: dict, top_analysis: dict) -> dict:
    data = snapshot.get("data", {})
    squads = normalize_squads(data.get("squads", []))
    injury_summary = summarize_injuries(data.get("injuries", []))
    deep_players = normalize_players(data.get("players", []), "deep_players")
    player_pool = merge_player_pools(deep_players, top_analysis.get("player_attribute_pool", []), injury_summary["by_player"])
    return {
        "source": snapshot.get("summary", {}),
        "summary": {
            "teams": len(data.get("teams", [])),
            "squads": len(data.get("squads", [])),
            "squad_players": len(squads),
            "injury_rows": len(data.get("injuries", [])),
            "players_stat_rows": len(deep_players),
            "combined_player_pool": len(player_pool),
            "top_analysis_players_added": len(top_analysis.get("player_attribute_pool", [])),
        },
        "squads": squads,
        "injuries": injury_summary,
        "player_attribute_pool": player_pool,
    }


def normalize_squads(rows: list[dict]) -> list[dict]:
    players = []
    for row in rows:
        team = row.get("team", {})
        for player in row.get("players", []):
            players.append(
                {
                    "player_id": player.get("id"),
                    "name": player.get("name"),
                    "age": player.get("age"),
                    "number": player.get("number"),
                    "position": player.get("position"),
                    "team_id": team.get("id"),
                    "team": team.get("name"),
                }
            )
    return players


def summarize_injuries(rows: list[dict]) -> dict:
    by_player: dict[int, dict] = {}
    by_team = Counter()
    by_type = Counter()
    for row in rows:
        player = row.get("player", {})
        team = row.get("team", {})
        fixture = row.get("fixture", {})
        player_id = player.get("id")
        if not player_id:
            continue
        current = by_player.setdefault(
            player_id,
            {
                "player_id": player_id,
                "name": player.get("name"),
                "team_id": team.get("id"),
                "team": team.get("name"),
                "injury_count": 0,
                "reasons": Counter(),
                "fixture_ids": [],
            },
        )
        current["injury_count"] += 1
        reason = player.get("reason") or "UNKNOWN"
        current["reasons"][reason] += 1
        if fixture.get("id"):
            current["fixture_ids"].append(fixture.get("id"))
        by_team[team.get("name") or "UNKNOWN"] += 1
        by_type[reason] += 1

    by_player_list = []
    for item in by_player.values():
        reasons = item.pop("reasons")
        item["reasons"] = dict(reasons.most_common(5))
        by_player_list.append(item)

    return {
        "by_player": {str(item["player_id"]): item for item in by_player_list},
        "top_players": sorted(by_player_list, key=lambda item: item["injury_count"], reverse=True)[:25],
        "top_teams": by_team.most_common(20),
        "top_reasons": by_type.most_common(20),
    }


def merge_player_pools(deep_players: list[dict], top_players: list[dict], injuries_by_player: dict[str, dict]) -> list[dict]:
    by_id: dict[int, dict] = {}
    for source, players in (("deep", deep_players), ("top", top_players)):
        for player in players:
            player_id = player.get("player_id")
            if not player_id:
                continue
            current = by_id.setdefault(player_id, dict(player))
            current["source_layers"] = sorted(set(current.get("source_layers", [])) | {source})
            for key in (
                "goals", "assists", "shots", "shots_on", "key_passes", "tackles", "interceptions",
                "duels", "duels_won", "dribbles", "dribbles_success", "fouls_committed", "yellow_cards", "red_cards",
            ):
                current[key] = max(current.get(key) or 0, player.get(key) or 0)
            for key in ("name", "team", "position", "age", "nationality", "height", "weight", "rating", "appearances", "lineups", "minutes"):
                current[key] = current.get(key) if current.get(key) not in (None, "") else player.get(key)
            current["external_role_score"] = role_score(current)

    for player_id, injury in injuries_by_player.items():
        current = by_id.get(int(player_id))
        if current:
            current["historical_injury_signal_count"] = injury["injury_count"]
            current["historical_injury_reasons"] = injury["reasons"]

    return sorted(by_id.values(), key=lambda item: item.get("external_role_score", 0), reverse=True)


def build_markdown(payload: dict) -> str:
    summary = payload["summary"]
    lines = [
        "# API-Football Derin 2024 Analizi",
        "",
        f"- Takım: {summary['teams']}",
        f"- Kadro oyuncusu: {summary['squad_players']}",
        f"- Sakatlık satırı: {summary['injury_rows']}",
        f"- Oyuncu istatistik satırı: {summary['players_stat_rows']}",
        f"- Birleşik oyuncu havuzu: {summary['combined_player_pool']}",
        "",
        "## En Güçlü Dış Oyuncu Sinyalleri",
        "",
    ]
    for player in payload["player_attribute_pool"][:20]:
        lines.append(
            f"- {player['name']} ({player.get('team')}): pos={player.get('position')}, rating={player.get('rating')}, "
            f"gol={player.get('goals', 0)}, asist={player.get('assists', 0)}, duel_won={player.get('duels_won', 0)}, "
            f"sakatlık_sinyali={player.get('historical_injury_signal_count', 0)}, skor={player.get('external_role_score')}"
        )
    lines.extend(["", "## En Çok Sakatlık Sinyali Gelenler", ""])
    for player in payload["injuries"]["top_players"][:15]:
        lines.append(f"- {player['name']} ({player.get('team')}): kayıt={player['injury_count']}, neden={player['reasons']}")
    return "\n".join(lines)


def build_html(payload: dict) -> str:
    player_rows = "".join(
        f"<tr><td>{escape(player['name'])}</td><td>{escape(player.get('team') or '')}</td><td>{escape(player.get('position') or '')}</td>"
        f"<td>{player.get('rating') or ''}</td><td>{player.get('goals', 0)}</td><td>{player.get('assists', 0)}</td>"
        f"<td>{player.get('duels_won', 0)}</td><td>{player.get('historical_injury_signal_count', 0)}</td><td>{player.get('external_role_score')}</td></tr>"
        for player in payload["player_attribute_pool"][:30]
    )
    injury_rows = "".join(
        f"<tr><td>{escape(player['name'])}</td><td>{escape(player.get('team') or '')}</td><td>{player['injury_count']}</td><td>{escape(str(player['reasons']))}</td></tr>"
        for player in payload["injuries"]["top_players"][:20]
    )
    summary = payload["summary"]
    return f"""<!doctype html>
<html lang="tr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>API-Football Derin 2024 Analizi</title>
  <style>
    body {{ margin:0; font-family:Inter, system-ui, sans-serif; background:#f4f6f8; color:#15181d; }}
    header {{ background:#111318; color:white; padding:28px 42px; border-bottom:4px solid #185ea8; }}
    main {{ max-width:1320px; margin:0 auto; padding:22px; }}
    .metrics {{ display:grid; grid-template-columns:repeat(5,1fr); gap:12px; margin-bottom:18px; }}
    .metric, section {{ background:white; border:1px solid #dce2ea; border-radius:8px; box-shadow:0 8px 22px rgba(18,24,32,.08); }}
    .metric {{ padding:15px; }} .metric span {{ display:block; color:#667085; font-size:12px; }} .metric strong {{ display:block; font-size:26px; }}
    section {{ padding:18px; margin-bottom:18px; }} table {{ width:100%; border-collapse:collapse; font-size:13px; }}
    th,td {{ padding:9px 7px; border-bottom:1px solid #dce2ea; text-align:left; vertical-align:top; }} th {{ color:#667085; font-size:12px; }}
    @media (max-width:900px) {{ .metrics {{ grid-template-columns:1fr; }} header {{ padding:22px; }} main {{ padding:14px; }} table {{ font-size:12px; }} }}
  </style>
</head>
<body>
  <header><h1>API-Football Derin 2024 Analizi</h1><p>Kadro, oyuncu istatistiği ve geçmiş sakatlık sinyali birleştirme paneli.</p></header>
  <main>
    <div class="metrics">
      {metric("Takım", summary["teams"])}
      {metric("Kadro oyuncusu", summary["squad_players"])}
      {metric("Sakatlık kaydı", summary["injury_rows"])}
      {metric("İstatistik satırı", summary["players_stat_rows"])}
      {metric("Birleşik havuz", summary["combined_player_pool"])}
    </div>
    <section><h2>Birleşik Oyuncu Havuzu</h2><table><thead><tr><th>Oyuncu</th><th>Takım</th><th>Pozisyon</th><th>Rating</th><th>Gol</th><th>Asist</th><th>Duel</th><th>Sakatlık</th><th>Skor</th></tr></thead><tbody>{player_rows}</tbody></table></section>
    <section><h2>Sakatlık Sinyali</h2><table><thead><tr><th>Oyuncu</th><th>Takım</th><th>Kayıt</th><th>Neden</th></tr></thead><tbody>{injury_rows}</tbody></table></section>
  </main>
</body>
</html>"""


def metric(label: str, value) -> str:
    return f'<div class="metric"><span>{escape(str(label))}</span><strong>{escape(str(value))}</strong></div>'


if __name__ == "__main__":
    main()
