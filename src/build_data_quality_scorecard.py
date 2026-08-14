from __future__ import annotations

import argparse
import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.config import PROCESSED_DIR
from src.html_utils import md_to_html, page_html


DEFAULT_WAREHOUSE = PROCESSED_DIR / "metric11_warehouse.sqlite"


@dataclass(frozen=True)
class Check:
    area: str
    metric: str
    value: Any
    status: str
    priority: str
    recommendation: str


def main() -> None:
    parser = argparse.ArgumentParser(description="Metric11 veri/istatistik saglik scorecard'i uretir.")
    parser.add_argument("--warehouse", default=str(DEFAULT_WAREHOUSE))
    parser.add_argument("--output-prefix", default="data_quality_scorecard_2025_2026")
    args = parser.parse_args()

    warehouse = Path(args.warehouse)
    if not warehouse.exists():
        raise SystemExit(f"Warehouse bulunamadi: {warehouse}")

    conn = sqlite3.connect(warehouse)
    conn.row_factory = sqlite3.Row
    try:
        payload = build_scorecard(conn, warehouse)
    finally:
        conn.close()

    md = build_markdown(payload)
    json_path = PROCESSED_DIR / f"{args.output_prefix}.json"
    md_path = PROCESSED_DIR / f"{args.output_prefix}.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(md, encoding="utf-8")
    html_path = PROCESSED_DIR / f"{args.output_prefix}.html"
    html_path.write_text(page_html("Veri Kalite Scorecard", md_to_html(md), noindex=True), encoding="utf-8")
    print(md)


def build_scorecard(conn: sqlite3.Connection, warehouse: Path) -> dict[str, Any]:
    table_counts = get_table_counts(conn)
    goal_backtest_summary = load_goal_backtest_summary()
    checks = [
        coverage_check(conn),
        referee_check(conn),
        player_profile_check(conn),
        transfermarkt_mapping_check(),
        transfermarkt_manual_verification_check(),
        transfermarkt_scout_blocker_check(),
        pipeline_freshness_check(),
        source_watchlist_check(),
        prediction_accuracy_check(conn),
        draw_recall_check(conn),
        overconfidence_check(conn),
        goal_candidate_check(conn, 5, goal_backtest_summary),
        goal_candidate_check(conn, 8, goal_backtest_summary),
        scout_confidence_check(conn),
    ]
    checks = [check for check in checks if check is not None]

    status_weights = {"PASS": 1.0, "WATCH": 0.65, "FAIL": 0.25}
    score = round(sum(status_weights[check.status] for check in checks) / max(len(checks), 1) * 100, 1)
    priorities = build_priorities(checks)

    return {
        "warehouse": str(warehouse),
        "score": score,
        "table_counts": table_counts,
        "goal_backtest_summary": goal_backtest_summary,
        "checks": [check.__dict__ for check in checks],
        "priorities": priorities,
        "prediction_confusion": query_rows(
            conn,
            """
            SELECT predicted, actual, COUNT(*) AS matches
            FROM match_predictions
            GROUP BY predicted, actual
            ORDER BY predicted, actual
            """,
        ),
        "goal_candidate_segments": query_rows(
            conn,
            """
            SELECT
              COALESCE(NULLIF(candidate_type, ''), 'unknown') AS candidate_type,
              COUNT(*) AS rows,
              SUM(CASE WHEN actual_scorer = 1 THEN 1 ELSE 0 END) AS hits
            FROM goal_candidates
            GROUP BY COALESCE(NULLIF(candidate_type, ''), 'unknown')
            ORDER BY rows DESC
            """,
        ),
        "scout_position_confidence": query_rows(
            conn,
            """
            SELECT position_confidence, COUNT(*) AS rows
            FROM team_scout_blueprints
            GROUP BY position_confidence
            ORDER BY rows DESC
            """,
        ),
    }


def get_table_counts(conn: sqlite3.Connection) -> dict[str, int]:
    tables = [
        row["name"]
        for row in conn.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            ORDER BY name
            """
        )
    ]
    return {table: scalar(conn, f"SELECT COUNT(*) FROM {table}") for table in tables}


def coverage_check(conn: sqlite3.Connection) -> Check:
    matches = scalar(conn, "SELECT COUNT(*) FROM matches")
    status = "PASS" if matches >= 300 else "WATCH" if matches >= 200 else "FAIL"
    return Check(
        area="coverage",
        metric="season_match_rows",
        value=matches,
        status=status,
        priority="HIGH" if status != "PASS" else "LOW",
        recommendation="Sezon kapsamı 306 maç civarında kalmalı; düşüş olursa collector/parser kontrol edilmeli.",
    )


def referee_check(conn: sqlite3.Connection) -> Check:
    missing = scalar(conn, "SELECT COUNT(*) FROM matches WHERE main_referee IS NULL OR main_referee = ''")
    status = "PASS" if missing == 0 else "WATCH" if missing <= 5 else "FAIL"
    return Check(
        area="coverage",
        metric="matches_missing_referee",
        value=missing,
        status=status,
        priority="MEDIUM" if missing else "LOW",
        recommendation="Hakem eksikleri kart ve büyük maç risk modelini doğrudan zayıflatır.",
    )


def player_profile_check(conn: sqlite3.Connection) -> Check:
    missing = scalar(conn, "SELECT COUNT(*) FROM players WHERE age IS NULL")
    total = scalar(conn, "SELECT COUNT(*) FROM players")
    pct = round(missing / max(total, 1) * 100, 1)
    status = "PASS" if missing == 0 else "WATCH" if pct < 10 else "FAIL"
    return Check(
        area="player_profiles",
        metric="players_missing_age_profile",
        value={"missing": missing, "total": total, "missing_pct": pct},
        status=status,
        priority="HIGH" if status == "FAIL" else "LOW",
        recommendation="Yaş/profil kapsamı scout ve kontrat fırsatı skorunun temel girdisi.",
    )


def transfermarkt_mapping_check() -> Check | None:
    payload = load_optional_json(PROCESSED_DIR / "transfermarkt_match_review_queue_2025_2026.json")
    summary = payload.get("summary", {})
    in_scope = summary.get("snapshot_in_scope_tff_profiles", 0)
    match_rate = summary.get("in_scope_match_rate")
    if not in_scope or match_rate is None:
        return None
    pct = round(match_rate * 100, 1)
    status = "PASS" if pct >= 85 else "WATCH" if pct >= 70 else "FAIL"
    return Check(
        area="player_profiles",
        metric="tff_transfermarkt_in_scope_match_rate_pct",
        value={"matched": summary.get("matched_profiles", 0), "in_scope": in_scope, "pct": pct},
        status=status,
        priority="HIGH" if status != "PASS" else "LOW",
        recommendation="Snapshot kapsamındaki eşleşmeyen oyuncular alias/transfer inceleme kuyruğunda doğrulanmadan piyasa değeri veya pozisyon olarak kullanılmamalı.",
    )


def transfermarkt_scout_blocker_check() -> Check | None:
    payload = load_optional_json(PROCESSED_DIR / "transfermarkt_match_review_queue_2025_2026.json")
    if not payload:
        return None
    blocked = payload.get("summary", {}).get("scout_blocking_unmatched", 0)
    status = "PASS" if blocked == 0 else "FAIL"
    return Check(
        area="scouting",
        metric="unmatched_players_blocking_scout_review",
        value=blocked,
        status=status,
        priority="HIGH" if blocked else "LOW",
        recommendation="Scout kuyruğunu bloke eden oyuncular için aynı kulüp Transfermarkt adı veya resmi profil doğrulanmalı; doğrulanmadan rol önerisi yayınlanmamalı.",
    )


def transfermarkt_manual_verification_check() -> Check | None:
    payload = load_optional_json(PROCESSED_DIR / "transfermarkt_match_review_queue_2025_2026.json")
    if not payload:
        return None
    pending = payload.get("summary", {}).get("manual_alias_pending_network_verification", 0)
    status = "PASS" if pending == 0 else "WATCH"
    return Check(
        area="player_profiles",
        metric="manual_alias_pending_network_verification",
        value=pending,
        status=status,
        priority="HIGH" if pending else "LOW",
        recommendation=(
            "Operasyonda kullanılan manuel pozisyon ve piyasa değeri eşlemeleri "
            "Transfermarkt profil bağlantısıyla doğrulanana kadar teyit bekliyor olarak gösterilmeli."
        ),
    )


def pipeline_freshness_check() -> Check | None:
    payload = load_optional_json(PROCESSED_DIR / "daily_pipeline_run_latest.json")
    if not payload:
        return Check(
            area="pipeline",
            metric="daily_pipeline_report_missing",
            value="missing",
            status="FAIL",
            priority="HIGH",
            recommendation="Günlük pipeline raporu yoksa siteye yansıyan veri tazeliği doğrulanamaz; pipeline çalıştırılıp rapor üretilmeli.",
        )
    age_days = age_days_from_iso(payload.get("generated_at"))
    if age_days is None:
        return Check(
            area="pipeline",
            metric="daily_pipeline_last_run_age_days",
            value="unknown",
            status="WATCH",
            priority="HIGH",
            recommendation="Pipeline generated_at alanı okunamıyor; günlük sağlık kontrolü için ISO tarih formatı korunmalı.",
        )
    failed = int(payload.get("failed_count") or 0)
    status = "PASS" if age_days <= 1 and failed == 0 else "WATCH" if age_days <= 3 and failed <= 3 else "FAIL"
    return Check(
        area="pipeline",
        metric="daily_pipeline_last_run_age_days",
        value={"age_days": age_days, "failed_count": failed, "include_network": payload.get("include_network")},
        status=status,
        priority="HIGH" if status != "PASS" else "LOW",
        recommendation="Tahmin, haber ve scout ekranları için günlük pipeline en fazla 1 gün eski olmalı; 3 günü aşarsa veri tazeliği kırmızıya alınmalı.",
    )


def source_watchlist_check() -> Check | None:
    payload = load_optional_json(PROCESSED_DIR / "source_watchlist_2025_2026.json")
    if not payload:
        return Check(
            area="sources",
            metric="source_watchlist_json_missing",
            value="missing",
            status="WATCH",
            priority="MEDIUM",
            recommendation="Kaynak radarı makine okunabilir JSON üretmeli; status ve kalite ekranları günlük kaynak kapsamını buradan izler.",
        )
    summary = payload.get("summary", {})
    daily = int(summary.get("daily_refresh_count") or 0)
    connected = int(summary.get("connected_or_partial_count") or 0)
    source_count = int(summary.get("source_count") or 0)
    status = "PASS" if daily >= 8 and connected >= 5 else "WATCH" if source_count else "FAIL"
    return Check(
        area="sources",
        metric="source_watchlist_daily_coverage",
        value={"sources": source_count, "daily": daily, "connected_or_partial": connected, "high_risk": summary.get("high_risk_count", 0)},
        status=status,
        priority="MEDIUM" if status != "PASS" else "LOW",
        recommendation="Günlük izlenecek kaynak sayısı ve bağlı kaynak kapsamı düşükse transfer/sakatlık/kadro haberleri modele geç yansır.",
    )


def prediction_accuracy_check(conn: sqlite3.Connection) -> Check | None:
    total = scalar(conn, "SELECT COUNT(*) FROM match_predictions")
    if total == 0:
        return None
    correct = scalar(conn, "SELECT COUNT(*) FROM match_predictions WHERE correct = 1")
    pct = round(correct / total * 100, 1)
    # Bu oran aynı sezon üzerinde ayarlanmış ekran kurallarını içerir; bağımsız sezonda doğrulanana kadar PASS olamaz.
    status = "WATCH" if pct >= 55 else "FAIL"
    return Check(
        area="model",
        metric="besiktas_display_prediction_accuracy_pct",
        value={"correct": correct, "total": total, "pct": pct},
        status=status,
        priority="HIGH",
        recommendation="Ekran ayarı aynı sezonda geliştirildi; yeni sezon veya ayrılmış sezonda sabit kurallarla doğrulanmadan genel başarı iddiası yapılmamalı.",
    )


def draw_recall_check(conn: sqlite3.Connection) -> Check | None:
    draw_total = scalar(conn, "SELECT COUNT(*) FROM match_predictions WHERE actual = 'draw'")
    if draw_total == 0:
        return None
    draw_predicted = scalar(
        conn,
        "SELECT COUNT(*) FROM match_predictions WHERE actual = 'draw' AND predicted = 'draw'",
    )
    pct = round(draw_predicted / draw_total * 100, 1)
    status = "PASS" if pct >= 35 else "WATCH" if pct >= 15 else "FAIL"
    return Check(
        area="model",
        metric="draw_recall_pct",
        value={"draw_predicted": draw_predicted, "draw_total": draw_total, "pct": pct},
        status=status,
        priority="HIGH",
        recommendation="Beraberlik sadece çok yüksek risk ve dar olasılık farkında ekran tahminine çekilmeli; diğer durumlarda korumalı senaryo dili kullanılmalı.",
    )


def overconfidence_check(conn: sqlite3.Connection) -> Check | None:
    total_wrong = scalar(conn, "SELECT COUNT(*) FROM match_predictions WHERE correct = 0")
    if total_wrong == 0:
        return None
    wrong_high = scalar(
        conn,
        """
        SELECT COUNT(*)
        FROM match_predictions
        WHERE correct = 0 AND confidence_probability >= 0.55
        """,
    )
    pct = round(wrong_high / total_wrong * 100, 1)
    status = "PASS" if pct <= 25 else "WATCH" if pct <= 45 else "FAIL"
    return Check(
        area="calibration",
        metric="wrong_predictions_with_high_confidence_pct",
        value={"wrong_high_confidence": wrong_high, "wrong_total": total_wrong, "pct": pct},
        status=status,
        priority="MEDIUM" if status != "FAIL" else "HIGH",
        recommendation="Yüksek güvenli hatalarda xG farkı, büyük maç ve beraberlik risk bayrakları güveni aşağı çekmeli.",
    )


def goal_candidate_check(
    conn: sqlite3.Connection,
    top_n: int,
    backtest_summary: dict[str, Any] | None,
) -> Check | None:
    if backtest_summary:
        matches = int(backtest_summary.get("matches_with_besiktas_goal") or 0)
        hits = int(backtest_summary.get(f"top_{top_n}_hits") or 0)
    else:
        matches = scalar(conn, "SELECT COUNT(DISTINCT match_external_id) FROM goal_candidates")
        hits = scalar(
            conn,
            f"""
            SELECT COUNT(DISTINCT match_external_id)
            FROM goal_candidates
            WHERE rank <= {top_n} AND actual_scorer = 1
            """,
        )
    if matches == 0:
        return None
    pct = round(hits / matches * 100, 1)
    target = 80 if top_n == 5 else 85
    status = "PASS" if pct >= target else "WATCH" if pct >= target - 8 else "FAIL"
    return Check(
        area="goal_candidates",
        metric=f"top_{top_n}_hit_pct",
        value={"hits": hits, "matches": matches, "pct": pct},
        status=status,
        priority="MEDIUM" if status != "FAIL" else "HIGH",
        recommendation="Aday tipleri ayrı backtest edilmeli: primary, penaltı, duran top/defans ve yedek etki.",
    )


def load_goal_backtest_summary() -> dict[str, Any] | None:
    path = PROCESSED_DIR / "goal_candidate_backtest_2025_2026.json"
    if not path.exists():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    summary = payload.get("summary") if isinstance(payload, dict) else None
    return summary if isinstance(summary, dict) else None


def load_optional_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def age_days_from_iso(value: str | None) -> int | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return max((datetime.now(timezone.utc) - dt.astimezone(timezone.utc)).days, 0)
    except Exception:
        return None


def scout_confidence_check(conn: sqlite3.Connection) -> Check | None:
    total = scalar(conn, "SELECT COUNT(*) FROM team_scout_blueprints")
    if total == 0:
        return None
    low = scalar(
        conn,
        """
        SELECT COUNT(*)
        FROM team_scout_blueprints
        WHERE position_confidence LIKE 'LOW%'
        """,
    )
    pct = round(low / total * 100, 1)
    status = "PASS" if pct <= 10 else "WATCH" if pct <= 30 else "FAIL"
    return Check(
        area="scouting",
        metric="low_position_confidence_pct",
        value={"low_confidence": low, "total": total, "pct": pct},
        status=status,
        priority="HIGH" if status != "PASS" else "MEDIUM",
        recommendation="Düşük güvenli scout adayları doğrudan pozisyon, boy, ayak ve aksiyon verisiyle zenginleştirilmeli.",
    )


def build_priorities(checks: list[Check]) -> list[dict[str, str]]:
    failed_or_watch = [check for check in checks if check.status != "PASS"]
    priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    failed_or_watch.sort(key=lambda check: (priority_order.get(check.priority, 9), check.area, check.metric))
    return [
        {
            "priority": check.priority,
            "area": check.area,
            "metric": check.metric,
            "recommendation": check.recommendation,
        }
        for check in failed_or_watch
    ]


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Veri Kalite ve İstatistik Scorecard",
        "",
        f"- Ambar: `{payload['warehouse']}`",
        f"- Genel skor: {payload['score']}/100",
        "",
        "## Kontroller",
        "",
        "| Alan | Metrik | Değer | Durum | Öncelik | Öneri |",
        "|---|---|---:|---|---|---|",
    ]
    _status_tr = {"PASS": "✓", "WATCH": "⚠ İzle", "FAIL": "✗ Sorun"}
    _priority_tr = {"HIGH": "Yüksek", "MEDIUM": "Orta", "LOW": "Düşük"}
    for check in payload["checks"]:
        lines.append(
            "| {area} | {metric} | {value} | {status} | {priority} | {recommendation} |".format(
                area=check["area"],
                metric=check["metric"],
                value=format_value(check["value"]),
                status=_status_tr.get(check["status"], check["status"]),
                priority=_priority_tr.get(check["priority"], check["priority"]),
                recommendation=check["recommendation"],
            )
        )

    lines.extend(["", "## Öncelikli Aksiyonlar", ""])
    if payload["priorities"]:
        for item in payload["priorities"]:
            priority_tr = {"HIGH": "Yüksek öncelik", "MEDIUM": "Orta öncelik", "LOW": "Düşük öncelik"}.get(item["priority"], item["priority"])
            lines.append(f"- **{priority_tr}** — {item['area']} / {item['metric']}: {item['recommendation']}")
    else:
        lines.append("- Kritik takip maddesi yok.")

    lines.extend(["", "## Tahmin Karışıklık Matrisi", ""])
    for row in payload["prediction_confusion"]:
        lines.append(f"- tahmin={row['predicted']} gerçek={row['actual']}: {row['matches']} maç")

    lines.extend(["", "## Gol Adayı Segmentleri", ""])
    for row in payload["goal_candidate_segments"]:
        hit_rate = round((row["hits"] or 0) / max(row["rows"], 1) * 100, 1)
        lines.append(f"- {row['candidate_type']}: {row['rows']} satır, {row['hits'] or 0} isabet satırı, %{hit_rate}")

    lines.extend(["", "## Scout Pozisyon Güveni", ""])
    for row in payload["scout_position_confidence"]:
        lines.append(f"- {row['position_confidence']}: {row['rows']}")

    lines.extend(["", "## Tablo Kapsamı", ""])
    for table, count in payload["table_counts"].items():
        lines.append(f"- {table}: {count}")
    return "\n".join(lines)


def query_rows(conn: sqlite3.Connection, query: str) -> list[dict[str, Any]]:
    return [dict(row) for row in conn.execute(query)]


def scalar(conn: sqlite3.Connection, query: str) -> Any:
    return conn.execute(query).fetchone()[0]


def format_value(value: Any) -> str:
    if isinstance(value, dict):
        return ", ".join(f"{key}={val}" for key, val in value.items())
    return str(value)


if __name__ == "__main__":
    main()
