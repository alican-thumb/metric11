from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path
from typing import Any

from src.config import PROCESSED_DIR
from src.html_utils import md_to_html, page_html
from src.normalization import normalize_matches


def main() -> None:
    parser = argparse.ArgumentParser(description="Metric11 icin sorgulanabilir SQLite veri ambari uretir.")
    parser.add_argument("--output", default=str(PROCESSED_DIR / "metric11_warehouse.sqlite"))
    parser.add_argument("--report-prefix", default="metric11_warehouse_quality")
    args = parser.parse_args()

    output = Path(args.output)
    if output.exists():
        output.unlink()
    conn = sqlite3.connect(output)
    conn.row_factory = sqlite3.Row
    try:
        create_schema(conn)
        load_all(conn)
        quality = build_quality_report(conn, output)
        report_json = PROCESSED_DIR / f"{args.report_prefix}.json"
        report_md = PROCESSED_DIR / f"{args.report_prefix}.md"
        md = build_markdown(quality)
        report_json.write_text(json.dumps(quality, ensure_ascii=False, indent=2), encoding="utf-8")
        report_md.write_text(md, encoding="utf-8")
        report_html = PROCESSED_DIR / f"{args.report_prefix}.html"
        report_html.write_text(page_html("SQLite Veri Ambarı Kalitesi", md_to_html(md)), encoding="utf-8")
        print(md)
    finally:
        conn.close()


def create_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        PRAGMA foreign_keys = ON;

        CREATE TABLE data_sources (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            source_type TEXT NOT NULL,
            risk_level TEXT NOT NULL,
            license_status TEXT,
            confidence_score REAL,
            notes TEXT
        );

        CREATE TABLE teams (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE
        );

        CREATE TABLE players (
            id INTEGER PRIMARY KEY,
            external_id TEXT UNIQUE,
            name TEXT NOT NULL,
            team_name TEXT,
            birth_date TEXT,
            age INTEGER,
            nationality TEXT,
            contract_end TEXT,
            contract_months_left INTEGER,
            profile_source TEXT
        );

        CREATE TABLE referees (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE
        );

        CREATE TABLE matches (
            id INTEGER PRIMARY KEY,
            external_id TEXT NOT NULL UNIQUE,
            season TEXT NOT NULL,
            fixture_week INTEGER,
            match_date TEXT,
            venue TEXT,
            home_team TEXT NOT NULL,
            away_team TEXT NOT NULL,
            home_score INTEGER,
            away_score INTEGER,
            main_referee TEXT,
            is_big_match INTEGER DEFAULT 0
        );

        CREATE TABLE match_lineups (
            match_external_id TEXT NOT NULL,
            team_name TEXT NOT NULL,
            player_external_id TEXT,
            player_name TEXT NOT NULL,
            is_starting INTEGER NOT NULL,
            shirt_number INTEGER
        );

        CREATE TABLE match_goals (
            match_external_id TEXT NOT NULL,
            team_name TEXT NOT NULL,
            player_external_id TEXT,
            player_name TEXT NOT NULL,
            minute TEXT,
            goal_type TEXT,
            raw TEXT
        );

        CREATE TABLE match_cards (
            match_external_id TEXT NOT NULL,
            team_name TEXT NOT NULL,
            player_external_id TEXT,
            player_name TEXT NOT NULL,
            minute TEXT,
            card_type TEXT
        );

        CREATE TABLE team_profiles (
            team_name TEXT PRIMARY KEY,
            matches INTEGER,
            points INTEGER,
            points_per_match REAL,
            goals_for_per_match REAL,
            goals_against_per_match REAL,
            cards_for_per_match REAL,
            overall_power_score REAL,
            attack_score REAL,
            defense_score REAL,
            form_score REAL,
            main_scoring_window TEXT,
            main_conceding_window TEXT,
            recent_form TEXT
        );

        CREATE TABLE player_profiles (
            player_external_id TEXT PRIMARY KEY,
            player_name TEXT NOT NULL,
            team_name TEXT,
            starts INTEGER,
            bench INTEGER,
            goals INTEGER,
            cards INTEGER,
            red_cards INTEGER,
            goal_per_start REAL,
            card_per_start REAL,
            estimated_load_score REAL,
            profile_tag TEXT
        );

        CREATE TABLE referee_profiles (
            referee_name TEXT PRIMARY KEY,
            matches INTEGER,
            cards_per_match REAL,
            goals_per_match REAL,
            draw_rate REAL,
            home_win_rate REAL,
            away_win_rate REAL,
            high_card_match_rate REAL,
            tempo_label TEXT
        );

        CREATE TABLE match_predictions (
            match_external_id TEXT PRIMARY KEY,
            date TEXT,
            fixture TEXT,
            actual_score TEXT,
            raw_predicted TEXT,
            predicted TEXT,
            actual TEXT,
            raw_correct INTEGER,
            correct INTEGER,
            prediction_adjustment TEXT,
            recommended_action TEXT,
            confidence_probability REAL,
            card_signal TEXT,
            is_big_match INTEGER
        );

        CREATE TABLE goal_candidates (
            match_external_id TEXT NOT NULL,
            rank INTEGER NOT NULL,
            player_external_id TEXT,
            player_name TEXT NOT NULL,
            team_name TEXT,
            candidate_type TEXT,
            goal_threat_score REAL,
            actual_scorer INTEGER,
            PRIMARY KEY (match_external_id, rank)
        );

        CREATE TABLE team_scout_blueprints (
            team_name TEXT NOT NULL,
            role_key TEXT NOT NULL,
            role_label TEXT NOT NULL,
            candidate_rank INTEGER NOT NULL,
            candidate_name TEXT,
            candidate_team TEXT,
            candidate_age INTEGER,
            contract_months_left INTEGER,
            resale_signal TEXT,
            contract_risk TEXT,
            verified_position TEXT,
            height_cm INTEGER,
            preferred_foot TEXT,
            position_source TEXT,
            fit_score REAL,
            estimated_load_min REAL,
            estimated_load_max REAL,
            position_confidence TEXT,
            PRIMARY KEY (team_name, role_key, candidate_rank)
        );

        CREATE TABLE data_quality_findings (
            id INTEGER PRIMARY KEY,
            severity TEXT NOT NULL,
            area TEXT NOT NULL,
            finding TEXT NOT NULL,
            count_value INTEGER,
            recommendation TEXT
        );

        CREATE VIEW v_team_power_ranking AS
        SELECT
            team_name,
            overall_power_score,
            points_per_match,
            goals_for_per_match,
            goals_against_per_match,
            cards_for_per_match,
            recent_form
        FROM team_profiles
        ORDER BY overall_power_score DESC;

        CREATE VIEW v_referee_card_risk AS
        SELECT
            referee_name,
            matches,
            cards_per_match,
            goals_per_match,
            draw_rate,
            tempo_label
        FROM referee_profiles
        ORDER BY cards_per_match DESC;

        CREATE VIEW v_player_load_leaders AS
        SELECT
            player_name,
            team_name,
            starts,
            goals,
            cards,
            estimated_load_score,
            profile_tag
        FROM player_profiles
        ORDER BY estimated_load_score DESC;

        CREATE VIEW v_besiktas_scout_blueprint AS
        SELECT
            role_label,
            candidate_rank,
            candidate_name,
            candidate_team,
            candidate_age,
            contract_months_left,
            resale_signal,
            contract_risk,
            verified_position,
            height_cm,
            preferred_foot,
            position_source,
            fit_score,
            estimated_load_min,
            estimated_load_max,
            position_confidence
        FROM team_scout_blueprints
        WHERE team_name = 'BEŞİKTAŞ A.Ş.'
        ORDER BY role_key, candidate_rank;
        """
    )


def load_all(conn: sqlite3.Connection) -> None:
    insert_sources(conn)
    matches = normalize_matches(load_json(PROCESSED_DIR / "tff_super_lig_enriched_2025_2026.json", []))
    insert_match_core(conn, matches)
    insert_player_profile_enrichment(conn)
    insert_league_intelligence(conn, load_json(PROCESSED_DIR / "league_intelligence_2025_2026.json", {}))
    insert_match_predictions(conn, load_json(PROCESSED_DIR / "match_prediction_backtest_2025_2026.json", {}))
    insert_goal_candidates(conn, PROCESSED_DIR / "previews_besiktas_2025_2026_chronological")
    insert_team_blueprints(conn, load_json(PROCESSED_DIR / "team_scout_blueprints_2025_2026.json", {}))
    insert_quality_findings(conn)
    conn.commit()


def insert_sources(conn: sqlite3.Connection) -> None:
    rows = [
        ("TFF maç detayları", "SCRAPING", "MEDIUM", "VERIFY_TERMS", 0.82, "Fikstür, kadro, gol, kart, hakem."),
        ("TFF oyuncu profilleri", "SCRAPING", "MEDIUM", "VERIFY_TERMS", 0.72, "Yaş, uyruk, lisans ve sözleşme profilleri."),
        ("Transfermarkt kadro sayfası", "SCRAPING", "HIGH", "VERIFY_TERMS_BEFORE_COMMERCIAL_USE", 0.65, "Pozisyon ve piyasa değeri; ticari kullanım doğrulanmalı."),
        ("API-Football snapshot", "API", "MEDIUM", "API_PLAN_LIMITED", 0.68, "2024 geçmiş sezon zenginleştirme; 2025 ücretsiz plan kısıtlı."),
        ("Model türetilmiş metrikler", "DERIVED", "LOW", "INTERNAL_DERIVED", 0.78, "Tahmin, scout, fiziksel yük ve rol sinyalleri."),
    ]
    conn.executemany(
        "INSERT INTO data_sources (name, source_type, risk_level, license_status, confidence_score, notes) VALUES (?, ?, ?, ?, ?, ?)",
        rows,
    )


def insert_match_core(conn: sqlite3.Connection, matches: list[dict]) -> None:
    team_names = sorted({match["home_team"]["name"] for match in matches} | {match["away_team"]["name"] for match in matches})
    referee_names = sorted(
        {
            official["name"]
            for match in matches
            for official in match.get("officials", [])
            if official.get("role") == "Hakem" and official.get("name")
        }
    )
    conn.executemany("INSERT OR IGNORE INTO teams (name) VALUES (?)", [(team,) for team in team_names])
    conn.executemany("INSERT OR IGNORE INTO referees (name) VALUES (?)", [(referee,) for referee in referee_names])
    big_opponents = {"GALATASARAY A.Ş.", "FENERBAHÇE A.Ş.", "TRABZONSPOR A.Ş."}
    match_rows = []
    lineup_rows = []
    goal_rows = []
    card_rows = []
    player_rows = {}
    for match in matches:
        home = match["home_team"]["name"]
        away = match["away_team"]["name"]
        referee = next((official["name"] for official in match.get("officials", []) if official.get("role") == "Hakem"), None)
        match_rows.append(
            (
                match["external_id"],
                "2025-2026",
                match.get("fixture_week"),
                match.get("match_date"),
                match.get("venue"),
                home,
                away,
                match["home_team"].get("score"),
                match["away_team"].get("score"),
                referee,
                int(home in big_opponents and away == "BEŞİKTAŞ A.Ş." or away in big_opponents and home == "BEŞİKTAŞ A.Ş."),
            )
        )
        for side in ("home", "away"):
            team = match[f"{side}_team"]["name"]
            for group, is_starting in (("starting", 1), ("bench", 0)):
                for player in match["lineups"][side][group]:
                    player_id = player.get("external_id") or player["name"]
                    player_rows[player_id] = (player_id, player["name"], team, None, None, None, None, None, "TFF_MATCH_SHEET")
                    lineup_rows.append((match["external_id"], team, player.get("external_id"), player["name"], is_starting, player.get("shirt_number")))
            for goal in match["goals"][side]:
                player_id = goal.get("player_external_id") or goal["player_name"]
                player_rows[player_id] = (player_id, goal["player_name"], team, None, None, None, None, None, "TFF_GOAL")
                goal_rows.append((match["external_id"], team, goal.get("player_external_id"), goal["player_name"], goal.get("minute"), goal.get("type"), goal.get("raw")))
            for card in match["cards"][side]:
                player_id = card.get("player_external_id") or card["player_name"]
                player_rows[player_id] = (player_id, card["player_name"], team, None, None, None, None, None, "TFF_CARD")
                card_rows.append((match["external_id"], team, card.get("player_external_id"), card["player_name"], card.get("minute"), card.get("type")))

    conn.executemany(
        """
        INSERT INTO matches (
            external_id, season, fixture_week, match_date, venue, home_team, away_team,
            home_score, away_score, main_referee, is_big_match
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        match_rows,
    )
    conn.executemany(
        "INSERT OR REPLACE INTO players (external_id, name, team_name, birth_date, age, nationality, contract_end, contract_months_left, profile_source) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        list(player_rows.values()),
    )
    conn.executemany("INSERT INTO match_lineups VALUES (?, ?, ?, ?, ?, ?)", lineup_rows)
    conn.executemany("INSERT INTO match_goals VALUES (?, ?, ?, ?, ?, ?, ?)", goal_rows)
    conn.executemany("INSERT INTO match_cards VALUES (?, ?, ?, ?, ?, ?)", card_rows)


def insert_player_profile_enrichment(conn: sqlite3.Connection) -> None:
    profile_paths = [
        PROCESSED_DIR / "tff_player_profiles_besiktas_2025_2026.json",
        PROCESSED_DIR / "tff_player_profiles_scout_shortlist_2025_2026.json",
        PROCESSED_DIR / "tff_player_profiles_all_priority_2025_2026.json",
    ]
    for path in profile_paths:
        for profile in load_json(path, []):
            external_id = str(profile.get("external_id") or "")
            if not external_id:
                continue
            conn.execute(
                """
                INSERT INTO players (
                    external_id, name, team_name, birth_date, age, nationality,
                    contract_end, contract_months_left, profile_source
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(external_id) DO UPDATE SET
                    name = excluded.name,
                    team_name = COALESCE(excluded.team_name, players.team_name),
                    birth_date = excluded.birth_date,
                    age = excluded.age,
                    nationality = excluded.nationality,
                    contract_end = excluded.contract_end,
                    contract_months_left = excluded.contract_months_left,
                    profile_source = 'TFF_PROFILE'
                """,
                (
                    external_id,
                    profile.get("name"),
                    profile.get("club") or profile.get("team_from_match"),
                    profile.get("birth_date"),
                    profile.get("age"),
                    profile.get("nationality"),
                    profile.get("contract_end"),
                    profile.get("contract_months_left"),
                    "TFF_PROFILE",
                ),
            )


def insert_league_intelligence(conn: sqlite3.Connection, payload: dict) -> None:
    conn.executemany(
        """
        INSERT OR REPLACE INTO team_profiles VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                item["team"],
                item["matches"],
                item["points"],
                item["points_per_match"],
                item["goals_for_per_match"],
                item["goals_against_per_match"],
                item["cards_for_per_match"],
                item["overall_power_score"],
                item["attack_score"],
                item["defense_score"],
                item["form_score"],
                item["main_scoring_window"],
                item["main_conceding_window"],
                item["recent_form"],
            )
            for item in payload.get("team_profiles", [])
        ],
    )
    conn.executemany(
        """
        INSERT OR REPLACE INTO player_profiles VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                item["player_id"],
                item["name"],
                item.get("team"),
                item["starts"],
                item["bench"],
                item["goals"],
                item["cards"],
                item["red_cards"],
                item["goal_per_start"],
                item["card_per_start"],
                item["estimated_load_score"],
                item["profile_tag"],
            )
            for item in payload.get("player_profiles", [])
        ],
    )
    conn.executemany(
        "INSERT OR REPLACE INTO referee_profiles VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        [
            (
                item["referee"],
                item["matches"],
                item["cards_per_match"],
                item["goals_per_match"],
                item["draw_rate"],
                item["home_win_rate"],
                item["away_win_rate"],
                item["high_card_match_rate"],
                item["tempo_label"],
            )
            for item in payload.get("referee_profiles", [])
        ],
    )


def insert_match_predictions(conn: sqlite3.Connection, payload: dict) -> None:
    conn.executemany(
        "INSERT OR REPLACE INTO match_predictions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        [
            (
                row["match_id"],
                row["date"],
                row["fixture"],
                row["actual_score"],
                row.get("raw_predicted", row["predicted"]),
                row["predicted"],
                row["actual"],
                int(row.get("raw_correct", row["correct"])),
                int(row["correct"]),
                row.get("prediction_adjustment", "none"),
                row["recommended_action"],
                row["confidence_probability"],
                row["card_signal"],
                int(row["is_big_match"]),
            )
            for row in payload.get("rows", [])
        ],
    )


def insert_goal_candidates(conn: sqlite3.Connection, preview_dir: Path) -> None:
    rows = []
    for path in sorted(preview_dir.glob("week_*.json")):
        preview = load_json(path, {})
        match_id = preview.get("match", {}).get("match_id")
        if not match_id:
            continue
        for rank, candidate in enumerate(preview.get("goal_candidates", {}).get("candidates", []), start=1):
            rows.append(
                (
                    match_id,
                    rank,
                    candidate.get("player_id"),
                    candidate.get("name"),
                    preview.get("match", {}).get("target_team"),
                    candidate.get("candidate_type"),
                    candidate.get("goal_threat_score", candidate.get("goal_candidate_score")),
                    int(bool(candidate.get("actual_scorer"))),
                )
            )
    conn.executemany("INSERT OR REPLACE INTO goal_candidates VALUES (?, ?, ?, ?, ?, ?, ?, ?)", rows)


def insert_team_blueprints(conn: sqlite3.Connection, payload: dict) -> None:
    rows = []
    for blueprint in payload.get("blueprints", []):
        for plan in blueprint.get("role_plans", []):
            for rank, candidate in enumerate(plan.get("top_candidates", []), start=1):
                rows.append(
                    (
                        blueprint["team"],
                        plan["role_key"],
                        plan["role_label"],
                        rank,
                        candidate.get("name"),
                        candidate.get("team"),
                        candidate.get("age"),
                        candidate.get("contract_months_left"),
                        candidate.get("resale_signal"),
                        candidate.get("contract_risk"),
                        candidate.get("verified_position"),
                        candidate.get("height_cm"),
                        candidate.get("preferred_foot"),
                        candidate.get("position_source"),
                        candidate.get("fit_score"),
                        candidate.get("estimated_physical_load_km_min"),
                        candidate.get("estimated_physical_load_km_max"),
                        candidate.get("position_confidence"),
                    )
                )
    conn.executemany("INSERT OR REPLACE INTO team_scout_blueprints VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", rows)


def insert_quality_findings(conn: sqlite3.Connection) -> None:
    findings = []
    match_count = scalar(conn, "SELECT COUNT(*) FROM matches")
    missing_referees = scalar(conn, "SELECT COUNT(*) FROM matches WHERE main_referee IS NULL OR main_referee = ''")
    players_without_age = scalar(conn, "SELECT COUNT(*) FROM players WHERE age IS NULL")
    blueprint_low_proxy = scalar(conn, "SELECT COUNT(*) FROM team_scout_blueprints WHERE position_confidence LIKE 'LOW%'")
    prediction_accuracy = scalar(conn, "SELECT ROUND(AVG(correct) * 100, 1) FROM match_predictions")
    top_goal_candidate_rows = scalar(conn, "SELECT COUNT(*) FROM goal_candidates")
    findings.extend(
        [
            ("LOW", "matches", "Warehouse match rows loaded", match_count, "Bu sayı sezon kapsamıyla tutarlı kalmalı."),
            ("MEDIUM" if missing_referees else "LOW", "referees", "Matches missing main referee", missing_referees, "Eksikse TFF parser veya kaynak değişimi kontrol edilmeli."),
            ("HIGH" if players_without_age else "LOW", "players", "Players without age/profile enrichment", players_without_age, "TFF/Transfermarkt/API profil toplama kapsamı genişletilmeli."),
            ("MEDIUM" if blueprint_low_proxy else "LOW", "scouting", "Blueprint candidates with low proxy position confidence", blueprint_low_proxy, "Doğrudan pozisyon, boy, ayak ve aksiyon verisiyle güçlendirilmeli."),
            ("MEDIUM", "predictions", "Beşiktaş match prediction accuracy percent", int(prediction_accuracy or 0), "Daha fazla sezon, sakatlık ve odds baseline ile kalibre edilmeli."),
            ("LOW", "goal_candidates", "Goal candidate rows loaded", top_goal_candidate_rows, "Top 8/10 performansı ürün için güçlü sinyal."),
        ]
    )
    conn.executemany(
        "INSERT INTO data_quality_findings (severity, area, finding, count_value, recommendation) VALUES (?, ?, ?, ?, ?)",
        findings,
    )


def build_quality_report(conn: sqlite3.Connection, output: Path) -> dict:
    table_counts = {
        row["name"]: scalar(conn, f"SELECT COUNT(*) FROM {row['name']}")
        for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    }
    view_names = [row["name"] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='view' ORDER BY name")]
    findings = [dict(row) for row in conn.execute("SELECT severity, area, finding, count_value, recommendation FROM data_quality_findings ORDER BY id")]
    sample_queries = {
        "top_team_power": rows(conn, "SELECT team_name, overall_power_score, points_per_match FROM team_profiles ORDER BY overall_power_score DESC LIMIT 5"),
        "besiktas_blueprint": rows(
            conn,
            """
            SELECT role_label, candidate_name, candidate_team, fit_score, position_confidence
            FROM team_scout_blueprints
            WHERE team_name = 'BEŞİKTAŞ A.Ş.'
            ORDER BY role_key, candidate_rank
            LIMIT 12
            """,
        ),
        "card_heavy_referees": rows(conn, "SELECT referee_name, cards_per_match, tempo_label FROM referee_profiles ORDER BY cards_per_match DESC LIMIT 5"),
    }
    return {
        "warehouse_path": str(output),
        "table_counts": table_counts,
        "views": view_names,
        "findings": findings,
        "sample_queries": sample_queries,
    }


def build_markdown(report: dict) -> str:
    lines = [
        "# Metric11 SQLite Veri Ambarı Kalite Raporu",
        "",
        f"- Dosya: `{report['warehouse_path']}`",
        "",
        "## Tablo Sayıları",
        "",
    ]
    for table, count in report["table_counts"].items():
        lines.append(f"- {table}: {count}")
    lines.extend(["", "## Hazır Görünümler", ""])
    for view in report.get("views", []):
        lines.append(f"- {view}")
    lines.extend(["", "## Kalite Bulguları", ""])
    for finding in report["findings"]:
        lines.append(
            f"- {finding['severity']} / {finding['area']}: {finding['finding']} = {finding['count_value']} -> {finding['recommendation']}"
        )
    lines.extend(["", "## Örnek Sorgu Çıktıları", ""])
    for label, rows_ in report["sample_queries"].items():
        lines.append(f"### {label}")
        for row in rows_:
            lines.append(f"- {row}")
        lines.append("")
    return "\n".join(lines)


def scalar(conn: sqlite3.Connection, sql: str) -> Any:
    return conn.execute(sql).fetchone()[0]


def rows(conn: sqlite3.Connection, sql: str) -> list[dict]:
    return [dict(row) for row in conn.execute(sql)]


def load_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
