from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from html import escape
from pathlib import Path

from src.config import PROCESSED_DIR
from src.normalization import normalize_matches


def main() -> None:
    parser = argparse.ArgumentParser(description="Super Lig takim/oyuncu/hakem istihbarat raporu uretir.")
    parser.add_argument("--input", default=str(PROCESSED_DIR / "tff_super_lig_enriched_2025_2026.json"))
    parser.add_argument("--output-prefix", default="league_intelligence_2025_2026")
    args = parser.parse_args()

    matches = normalize_matches(json.loads(Path(args.input).read_text(encoding="utf-8")))
    payload = build_report(matches)
    json_path = PROCESSED_DIR / f"{args.output_prefix}.json"
    md_path = PROCESSED_DIR / f"{args.output_prefix}.md"
    html_path = PROCESSED_DIR / f"{args.output_prefix}.html"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(build_markdown(payload), encoding="utf-8")
    html_path.write_text(build_html(payload), encoding="utf-8")
    print(md_path.read_text(encoding="utf-8"))


def build_report(matches: list[dict]) -> dict:
    team_rows = build_team_rows(matches)
    player_rows = build_player_rows(matches)
    referee_rows = build_referee_rows(matches)
    weakness_rows = build_weakness_rows(matches, team_rows)
    return {
        "summary": {
            "matches": len(matches),
            "teams": len(team_rows),
            "players": len(player_rows),
            "referees": len(referee_rows),
            "goals": sum(team["goals_for"] for team in team_rows) // 2,
            "cards": sum(team["cards_for"] for team in team_rows),
        },
        "team_profiles": team_rows,
        "player_profiles": player_rows,
        "referee_profiles": referee_rows,
        "team_weaknesses": weakness_rows,
    }


def build_team_rows(matches: list[dict]) -> list[dict]:
    stats: dict[str, Counter] = defaultdict(Counter)
    recent_results: dict[str, list[str]] = defaultdict(list)
    goal_minutes_for: dict[str, Counter] = defaultdict(Counter)
    goal_minutes_against: dict[str, Counter] = defaultdict(Counter)
    for match in matches:
        home = match["home_team"]["name"]
        away = match["away_team"]["name"]
        home_score = match["home_team"]["score"] or 0
        away_score = match["away_team"]["score"] or 0
        update_team(stats[home], home_score, away_score, "home")
        update_team(stats[away], away_score, home_score, "away")
        recent_results[home].append(result_label(home_score, away_score))
        recent_results[away].append(result_label(away_score, home_score))
        stats[home]["cards_for"] += len(match["cards"]["home"])
        stats[away]["cards_for"] += len(match["cards"]["away"])
        stats[home]["cards_against"] += len(match["cards"]["away"])
        stats[away]["cards_against"] += len(match["cards"]["home"])
        for goal in match["goals"]["home"]:
            goal_minutes_for[home][minute_bucket(goal.get("minute"))] += 1
            goal_minutes_against[away][minute_bucket(goal.get("minute"))] += 1
            if goal.get("type"):
                stats[home][f"goal_type_for_{goal['type']}"] += 1
        for goal in match["goals"]["away"]:
            goal_minutes_for[away][minute_bucket(goal.get("minute"))] += 1
            goal_minutes_against[home][minute_bucket(goal.get("minute"))] += 1
            if goal.get("type"):
                stats[away][f"goal_type_for_{goal['type']}"] += 1

    rows = []
    for team, row in stats.items():
        matches_count = row["matches"]
        points = row["wins"] * 3 + row["draws"]
        attack_score = scaled(row["goals_for"] / matches_count, 0.7, 2.0)
        defense_score = 100 - scaled(row["goals_against"] / matches_count, 0.7, 2.0)
        discipline_score = 100 - scaled(row["cards_for"] / matches_count, 1.5, 4.0)
        form_score = recent_form_score(recent_results[team][-5:])
        rows.append(
            {
                "team": team,
                "matches": matches_count,
                "points": points,
                "points_per_match": round(points / matches_count, 2),
                "wins": row["wins"],
                "draws": row["draws"],
                "losses": row["losses"],
                "goals_for": row["goals_for"],
                "goals_against": row["goals_against"],
                "goal_difference": row["goals_for"] - row["goals_against"],
                "goals_for_per_match": round(row["goals_for"] / matches_count, 2),
                "goals_against_per_match": round(row["goals_against"] / matches_count, 2),
                "clean_sheets": row["clean_sheets"],
                "failed_to_score": row["failed_to_score"],
                "cards_for": row["cards_for"],
                "cards_for_per_match": round(row["cards_for"] / matches_count, 2),
                "cards_against_per_match": round(row["cards_against"] / matches_count, 2),
                "home_points_per_match": round(row["home_points"] / row["home_matches"], 2) if row["home_matches"] else None,
                "away_points_per_match": round(row["away_points"] / row["away_matches"], 2) if row["away_matches"] else None,
                "attack_score": attack_score,
                "defense_score": defense_score,
                "discipline_score": discipline_score,
                "form_score": form_score,
                "overall_power_score": round(attack_score * 0.28 + defense_score * 0.28 + form_score * 0.24 + discipline_score * 0.1 + scaled(points / matches_count, 0.6, 2.1) * 0.1, 1),
                "late_goals_for": goal_minutes_for[team]["76-90+"],
                "late_goals_against": goal_minutes_against[team]["76-90+"],
                "main_scoring_window": most_common_label(goal_minutes_for[team]),
                "main_conceding_window": most_common_label(goal_minutes_against[team]),
                "recent_form": "".join(recent_results[team][-5:]),
            }
        )
    return sorted(rows, key=lambda item: (item["points"], item["goal_difference"], item["goals_for"]), reverse=True)


def update_team(row: Counter, goals_for: int, goals_against: int, side: str) -> None:
    row["matches"] += 1
    row["goals_for"] += goals_for
    row["goals_against"] += goals_against
    row["wins"] += int(goals_for > goals_against)
    row["draws"] += int(goals_for == goals_against)
    row["losses"] += int(goals_for < goals_against)
    row["clean_sheets"] += int(goals_against == 0)
    row["failed_to_score"] += int(goals_for == 0)
    row[f"{side}_matches"] += 1
    row[f"{side}_points"] += 3 if goals_for > goals_against else 1 if goals_for == goals_against else 0


def build_player_rows(matches: list[dict]) -> list[dict]:
    players: dict[str, Counter] = defaultdict(Counter)
    names: dict[str, str] = {}
    teams: dict[str, Counter] = defaultdict(Counter)
    for match in matches:
        for side in ("home", "away"):
            team = match[f"{side}_team"]["name"]
            for player in match["lineups"][side]["starting"]:
                player_id = player.get("external_id") or player["name"]
                names[player_id] = player["name"]
                teams[player_id][team] += 1
                players[player_id]["starts"] += 1
                players[player_id]["squad_inclusions"] += 1
            for player in match["lineups"][side]["bench"]:
                player_id = player.get("external_id") or player["name"]
                names[player_id] = player["name"]
                teams[player_id][team] += 1
                players[player_id]["bench"] += 1
                players[player_id]["squad_inclusions"] += 1
            for goal in match["goals"][side]:
                player_id = goal.get("player_external_id") or goal["player_name"]
                names[player_id] = goal["player_name"]
                teams[player_id][team] += 1
                players[player_id]["goals"] += 1
                if goal.get("type") == "P":
                    players[player_id]["penalty_goals"] += 1
            for card in match["cards"][side]:
                player_id = card.get("player_external_id") or card["player_name"]
                names[player_id] = card["player_name"]
                teams[player_id][team] += 1
                players[player_id]["cards"] += 1
                if "Kırmızı" in card.get("type", ""):
                    players[player_id]["red_cards"] += 1
    rows = []
    for player_id, row in players.items():
        starts = row["starts"]
        goals = row["goals"]
        cards = row["cards"]
        team = teams[player_id].most_common(1)[0][0] if teams[player_id] else None
        rows.append(
            {
                "player_id": player_id,
                "name": names.get(player_id, player_id),
                "team": team,
                "starts": starts,
                "bench": row["bench"],
                "squad_inclusions": row["squad_inclusions"],
                "goals": goals,
                "penalty_goals": row["penalty_goals"],
                "cards": cards,
                "red_cards": row["red_cards"],
                "goal_per_start": round(goals / starts, 2) if starts else 0,
                "card_per_start": round(cards / starts, 2) if starts else 0,
                "estimated_load_score": estimated_load(starts, row["bench"], cards, goals),
                "profile_tag": player_tag(starts, goals, cards),
            }
        )
    return sorted(rows, key=lambda item: (item["goals"], item["starts"], -item["cards"]), reverse=True)


def build_referee_rows(matches: list[dict]) -> list[dict]:
    refs: dict[str, Counter] = defaultdict(Counter)
    for match in matches:
        ref = next((official.get("name") for official in match.get("officials", []) if official.get("role") == "Hakem"), None)
        if not ref:
            continue
        home_score = match["home_team"]["score"] or 0
        away_score = match["away_team"]["score"] or 0
        total_cards = len(match["cards"]["home"]) + len(match["cards"]["away"])
        refs[ref]["matches"] += 1
        refs[ref]["cards"] += total_cards
        refs[ref]["goals"] += home_score + away_score
        refs[ref]["home_wins"] += int(home_score > away_score)
        refs[ref]["draws"] += int(home_score == away_score)
        refs[ref]["away_wins"] += int(home_score < away_score)
        refs[ref]["high_card_matches"] += int(total_cards >= 6)
    rows = []
    for ref, row in refs.items():
        matches_count = row["matches"]
        rows.append(
            {
                "referee": ref,
                "matches": matches_count,
                "cards_per_match": round(row["cards"] / matches_count, 2),
                "goals_per_match": round(row["goals"] / matches_count, 2),
                "home_win_rate": round(row["home_wins"] / matches_count, 2),
                "draw_rate": round(row["draws"] / matches_count, 2),
                "away_win_rate": round(row["away_wins"] / matches_count, 2),
                "high_card_match_rate": round(row["high_card_matches"] / matches_count, 2),
                "tempo_label": "KARTLI" if row["cards"] / matches_count >= 5 else "AKICI" if row["cards"] / matches_count < 3.5 else "ORTA",
            }
        )
    return sorted(rows, key=lambda item: (item["cards_per_match"], item["matches"]), reverse=True)


def build_weakness_rows(matches: list[dict], team_rows: list[dict]) -> list[dict]:
    team_lookup = {team["team"]: team for team in team_rows}
    rows = []
    for team, profile in team_lookup.items():
        weaknesses = []
        if profile["goals_against_per_match"] >= 1.5:
            weaknesses.append("savunma kırılgan")
        if profile["late_goals_against"] >= 13:
            weaknesses.append("son bölüm gol yeme riski")
        if profile["cards_for_per_match"] >= 2.5:
            weaknesses.append("kart baskısı")
        if profile["failed_to_score"] >= 10:
            weaknesses.append("skor üretim sorunu")
        if profile["away_points_per_match"] is not None and profile["away_points_per_match"] <= 0.9:
            weaknesses.append("deplasman zayıf")
        if profile["goals_for_per_match"] < 1.0:
            weaknesses.append("hücum verimsizliği")
        if not weaknesses and profile["points_per_match"] >= 1.5 and profile["goals_against_per_match"] <= 1.2:
            weaknesses.append("kadro derinliği sınırlı")
        rows.append(
            {
                "team": team,
                "weakness_count": len(weaknesses),
                "weaknesses": weaknesses or ["belirgin zayıflık yok"],
                "scout_need_hint": scout_need_hint(profile, weaknesses),
            }
        )
    return sorted(rows, key=lambda item: item["weakness_count"], reverse=True)


def scout_need_hint(profile: dict, weaknesses: list[str]) -> str:
    if "savunma kırılgan" in weaknesses:
        return "Hızlı stoper, savunmacı 6 numara veya yüksek eforlu bek"
    if "son bölüm gol yeme riski" in weaknesses:
        return "Maç sonu denge sağlayan fiziksel 8 numara veya savunmacı orta saha"
    if "hücum verimsizliği" in weaknesses:
        return "Bireysel gol çözümü: düşük GF oranını kıracak bitirici forvet"
    if "skor üretim sorunu" in weaknesses:
        return "Ceza sahası koşusu ve bitiricilik üreten forvet/kanat"
    if "kart baskısı" in weaknesses:
        return "Daha kontrollü ikili mücadele profili ve pasla baskı kıran orta saha"
    if "deplasman zayıf" in weaknesses:
        return "Geçiş oyunu taşıyacak fiziksel orta saha/kanat"
    if "kadro derinliği sınırlı" in weaknesses:
        return "Kaliteli rotasyon: büyük maç baskısını karşılayacak kanat/bek derinliği"
    return "Mevcut omurgayı derinleştirecek genç rotasyon"


def result_label(gf: int, ga: int) -> str:
    return "W" if gf > ga else "D" if gf == ga else "L"


def minute_bucket(value: str | None) -> str:
    if not value:
        return "unknown"
    match = re.search(r"\d+", value)
    if not match:
        return "unknown"
    minute = int(match.group())
    if minute <= 15:
        return "0-15"
    if minute <= 30:
        return "16-30"
    if minute <= 45:
        return "31-45+"
    if minute <= 60:
        return "46-60"
    if minute <= 75:
        return "61-75"
    return "76-90+"


def scaled(value: float, low: float, high: float) -> float:
    if high == low:
        return 50
    return round(max(0, min(100, (value - low) / (high - low) * 100)), 1)


def recent_form_score(results: list[str]) -> float:
    if not results:
        return 50.0
    points = sum(3 if result == "W" else 1 if result == "D" else 0 for result in results)
    return round(points / (len(results) * 3) * 100, 1)


def most_common_label(counter: Counter) -> str:
    if not counter:
        return "unknown"
    return counter.most_common(1)[0][0]


def estimated_load(starts: int, bench: int, cards: int, goals: int) -> float:
    return round(min(100, starts * 2.2 + bench * 0.35 + cards * 1.4 + goals * 1.8), 1)


def player_tag(starts: int, goals: int, cards: int) -> str:
    if goals >= 10:
        return "skor lideri"
    if starts >= 24 and cards >= 8:
        return "yüksek yük/kart riski"
    if starts >= 24:
        return "omurga oyuncu"
    if goals >= 5:
        return "verimli skor katkısı"
    return "rotasyon"


def build_markdown(payload: dict) -> str:
    summary = payload["summary"]
    lines = [
        "# Süper Lig İstihbarat Raporu",
        "",
        f"- Maç: {summary['matches']}",
        f"- Takım: {summary['teams']}",
        f"- Oyuncu: {summary['players']}",
        f"- Hakem: {summary['referees']}",
        f"- Gol: {summary['goals']}",
        f"- Kart: {summary['cards']}",
        "",
        "## En Güçlü Takım Profilleri",
        "",
    ]
    for team in payload["team_profiles"][:8]:
        lines.append(
            f"- {team['team']}: güç={team['overall_power_score']}, PPM={team['points_per_match']}, "
            f"GF={team['goals_for_per_match']}, GA={team['goals_against_per_match']}, form={team['recent_form']}"
        )
    lines.extend(["", "## Skor Oyuncuları", ""])
    for player in payload["player_profiles"][:12]:
        lines.append(
            f"- {player['name']} ({player['team']}): gol={player['goals']}, start={player['starts']}, "
            f"kart={player['cards']}, etiket={player['profile_tag']}"
        )
    lines.extend(["", "## Hakem Profilleri", ""])
    for referee in payload["referee_profiles"][:10]:
        lines.append(
            f"- {referee['referee']}: maç={referee['matches']}, kart/maç={referee['cards_per_match']}, "
            f"gol/maç={referee['goals_per_match']}, tempo={referee['tempo_label']}"
        )
    lines.extend(["", "## Takım Zafiyetleri ve Scout İpucu", ""])
    for item in payload["team_weaknesses"][:10]:
        lines.append(f"- {item['team']}: {', '.join(item['weaknesses'])} -> {item['scout_need_hint']}")
    return "\n".join(lines)


def build_html(payload: dict) -> str:
    return f"""<!doctype html>
<html lang="tr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Süper Lig İstihbarat Raporu</title>
  <style>
    :root {{ --bg:#f4f6f8; --panel:#fff; --ink:#15181d; --muted:#667085; --line:#dce2ea; --dark:#111318; --red:#bf1f2f; --green:#137a4b; --blue:#185ea8; --shadow:0 8px 22px rgba(18,24,32,.08); }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; font-family:Inter, system-ui, sans-serif; background:var(--bg); color:var(--ink); }}
    header {{ background:var(--dark); color:white; padding:28px 42px; border-bottom:4px solid var(--red); }}
    header h1 {{ margin:0 0 7px; font-size:32px; letter-spacing:0; }}
    header p {{ margin:0; color:#c9ced8; max-width:1100px; line-height:1.5; }}
    main {{ max-width:1420px; margin:0 auto; padding:24px; }}
    .metrics {{ display:grid; grid-template-columns:repeat(6,1fr); gap:12px; margin-bottom:18px; }}
    .metric, section {{ background:white; border:1px solid var(--line); border-radius:8px; box-shadow:var(--shadow); }}
    .metric {{ padding:15px; }}
    .metric span {{ display:block; color:var(--muted); font-size:12px; }}
    .metric strong {{ display:block; font-size:26px; margin-top:5px; }}
    section {{ padding:18px; margin-bottom:18px; overflow-x:auto; }}
    h2 {{ margin:0 0 14px; font-size:18px; }}
    table {{ width:100%; min-width:720px; border-collapse:collapse; font-size:13px; }}
    th,td {{ padding:9px 7px; border-bottom:1px solid #e4e8ef; text-align:left; vertical-align:top; }}
    th {{ color:var(--muted); font-size:12px; }}
    .pill {{ display:inline-flex; min-height:23px; align-items:center; border-radius:999px; padding:0 8px; font-size:12px; background:#edf5ff; color:var(--blue); border:1px solid #bbd7f5; }}
    .grid {{ display:grid; grid-template-columns:1fr 1fr; gap:18px; }}
    @media (max-width:1100px) {{ .metrics {{ grid-template-columns:repeat(3,1fr); }} .grid {{ grid-template-columns:1fr; }} }}
    @media (max-width:680px) {{ .metrics {{ grid-template-columns:1fr; }} main {{ padding:14px; }} header {{ padding:22px; }} table {{ font-size:12px; }} }}
  </style>
</head>
<body>
  <header>
    <h1>Süper Lig İstihbarat Raporu</h1>
    <p>2025-2026 maç detaylarından takım gücü, oyuncu skor/kart profili, hakem tempo etiketi ve takım zafiyetlerinden scout ihtiyacı çıkarır.</p>
  </header>
  <main>
    <div class="metrics">
      {metric("Maç", payload["summary"]["matches"])}
      {metric("Takım", payload["summary"]["teams"])}
      {metric("Oyuncu", payload["summary"]["players"])}
      {metric("Hakem", payload["summary"]["referees"])}
      {metric("Gol", payload["summary"]["goals"])}
      {metric("Kart", payload["summary"]["cards"])}
    </div>
    <section><h2>Takım Gücü ve Stil Profili</h2>{team_table(payload["team_profiles"])}</section>
    <div class="grid">
      <section><h2>Skor ve Yük Oyuncuları</h2>{player_table(payload["player_profiles"][:40])}</section>
      <section><h2>Hakem Tempo Profili</h2>{referee_table(payload["referee_profiles"])}</section>
    </div>
    <section><h2>Takım Zafiyetleri ve Scout İpucu</h2>{weakness_table(payload["team_weaknesses"])}</section>
  </main>
  <script defer src="/_vercel/insights/script.js"></script>
</body>
</html>
"""


def metric(label: str, value) -> str:
    return f'<div class="metric"><span>{escape(str(label))}</span><strong>{escape(str(value))}</strong></div>'


def team_table(rows: list[dict]) -> str:
    body = "".join(
        f"<tr><td>{escape(row['team'])}</td><td>{row['overall_power_score']}</td><td>{row['points_per_match']}</td>"
        f"<td>{row['goals_for_per_match']}</td><td>{row['goals_against_per_match']}</td><td>{row['cards_for_per_match']}</td>"
        f"<td>{escape(row['recent_form'])}</td><td>{escape(row['main_scoring_window'])}</td><td>{escape(row['main_conceding_window'])}</td></tr>"
        for row in rows
    )
    return "<table><thead><tr><th>Takım</th><th>Güç</th><th>PPM</th><th>GF</th><th>GA</th><th>Kart</th><th>Form</th><th>Gol penceresi</th><th>Yeme penceresi</th></tr></thead><tbody>" + body + "</tbody></table>"


def player_table(rows: list[dict]) -> str:
    body = "".join(
        f"<tr><td>{escape(row['name'])}<br><span class=\"pill\">{escape(row.get('team') or '')}</span></td>"
        f"<td>{row['goals']}</td><td>{row['starts']}</td><td>{row['cards']}</td><td>{row['estimated_load_score']}</td><td>{escape(row['profile_tag'])}</td></tr>"
        for row in rows
    )
    return "<table><thead><tr><th>Oyuncu</th><th>Gol</th><th>Start</th><th>Kart</th><th>Yük</th><th>Etiket</th></tr></thead><tbody>" + body + "</tbody></table>"


def referee_table(rows: list[dict]) -> str:
    body = "".join(
        f"<tr><td>{escape(row['referee'])}</td><td>{row['matches']}</td><td>{row['cards_per_match']}</td><td>{row['goals_per_match']}</td>"
        f"<td>{round(row['draw_rate'] * 100)}%</td><td><span class=\"pill\">{escape(row['tempo_label'])}</span></td></tr>"
        for row in rows
    )
    return "<table><thead><tr><th>Hakem</th><th>Maç</th><th>Kart</th><th>Gol</th><th>X</th><th>Tempo</th></tr></thead><tbody>" + body + "</tbody></table>"


def weakness_table(rows: list[dict]) -> str:
    body = "".join(
        f"<tr><td>{escape(row['team'])}</td><td>{escape(', '.join(row['weaknesses']))}</td><td>{escape(row['scout_need_hint'])}</td></tr>"
        for row in rows
    )
    return "<table><thead><tr><th>Takım</th><th>Zafiyet</th><th>Scout İpucu</th></tr></thead><tbody>" + body + "</tbody></table>"


if __name__ == "__main__":
    main()
