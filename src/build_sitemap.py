"""Sitemap.xml ve robots.txt üretir."""
from __future__ import annotations

from datetime import date
from pathlib import Path

from src.config import PROCESSED_DIR, SEASON

BASE_URL = "https://metric11.com"

_PUBLIC_PAGES = [
    ("gundem_2025_2026.html", 1.0, "daily"),
    ("season_fixture_predictions_2026_2027.html", 1.0, "daily"),
    ("weekly_evaluation_2026_2027.html", 0.9, "daily"),
    ("european_predictions_2026_2027.html", 1.0, "daily"),
    ("football_intelligence_home.html", 0.9, "weekly"),
    ("all_teams_preview_dashboard_2025_2026.html", 0.9, "weekly"),
    (f"transfer_tracker_{SEASON}.html", 0.9, "daily"),
    (f"transfer_recommendation_report_{SEASON}.html", 0.8, "weekly"),
    (f"transfer_season_context_{SEASON}.html", 0.8, "weekly"),
    (f"news_intelligence_dashboard_{SEASON}.html", 0.8, "daily"),
    (f"league_intelligence_{SEASON}.html", 0.8, "weekly"),
    ("football_command_center_2025_2026.html", 0.7, "weekly"),
    ("team_scout_blueprints_2025_2026.html", 0.7, "weekly"),
    ("fm_style_scout_program_2025_2026.html", 0.7, "weekly"),
    ("position_scout_matrix_2025_2026.html", 0.7, "weekly"),
    ("league_market_value_audit_2025_2026.html", 0.6, "weekly"),
    ("big_match_report_2025_2026.html", 0.6, "weekly"),
    ("prediction_backtest_dashboard_2025_2026.html", 0.5, "monthly"),
    # Takım sayfaları
    ("alanyaspor_2025_2026_dashboard_chronological.html", 0.7, "weekly"),
    ("amed_2025_2026_dashboard_chronological.html", 0.6, "weekly"),
    ("antalyaspor_2025_2026_dashboard_chronological.html", 0.7, "weekly"),
    ("basaksehir_2025_2026_dashboard_chronological.html", 0.7, "weekly"),
    ("besiktas_2025_2026_dashboard_chronological.html", 0.8, "weekly"),
    ("corumfk_2025_2026_dashboard_chronological.html", 0.6, "weekly"),
    ("erzurumspor_2025_2026_dashboard_chronological.html", 0.6, "weekly"),
    ("eyupspor_2025_2026_dashboard_chronological.html", 0.7, "weekly"),
    ("fenerbahce_2025_2026_dashboard_chronological.html", 0.8, "weekly"),
    ("galatasaray_2025_2026_dashboard_chronological.html", 0.8, "weekly"),
    ("gaziantep_2025_2026_dashboard_chronological.html", 0.6, "weekly"),
    ("genclerbirligi_2025_2026_dashboard_chronological.html", 0.6, "weekly"),
    ("goztepe_2025_2026_dashboard_chronological.html", 0.7, "weekly"),
    ("karagumruk_2025_2026_dashboard_chronological.html", 0.6, "weekly"),
    ("kasimpasa_2025_2026_dashboard_chronological.html", 0.6, "weekly"),
    ("kayserispor_2025_2026_dashboard_chronological.html", 0.6, "weekly"),
    ("kocaelispor_2025_2026_dashboard_chronological.html", 0.6, "weekly"),
    ("konyaspor_2025_2026_dashboard_chronological.html", 0.6, "weekly"),
    ("rizespor_2025_2026_dashboard_chronological.html", 0.6, "weekly"),
    ("samsunspor_2025_2026_dashboard_chronological.html", 0.7, "weekly"),
    ("trabzonspor_2025_2026_dashboard_chronological.html", 0.7, "weekly"),
]


def build_sitemap() -> str:
    today = date.today().isoformat()
    urls = []
    for path, priority, freq in _PUBLIC_PAGES:
        full = f"{BASE_URL}/{path}"
        urls.append(
            f"  <url>\n"
            f"    <loc>{full}</loc>\n"
            f"    <lastmod>{today}</lastmod>\n"
            f"    <changefreq>{freq}</changefreq>\n"
            f"    <priority>{priority:.1f}</priority>\n"
            f"  </url>"
        )
    body = "\n".join(urls)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{body}\n"
        "</urlset>"
    )


def build_robots() -> str:
    return (
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /admin.html\n"
        "Disallow: /data_quality_scorecard_2025_2026.html\n"
        "Disallow: /data_catalog_2025_2026.html\n"
        "Disallow: /metric11_warehouse_quality.html\n"
        "Disallow: /oos_validation_2025_2026.html\n"
        "Disallow: /player_alias_quality_2025_2026.html\n"
        "Disallow: /source_watchlist_2025_2026.html\n"
        "Disallow: /transfermarkt_match_review_queue_2025_2026.html\n"
        "\n"
        f"Sitemap: {BASE_URL}/sitemap.xml\n"
    )


def main() -> None:
    sitemap_path = PROCESSED_DIR / "sitemap.xml"
    robots_path = PROCESSED_DIR / "robots.txt"
    sitemap_path.write_text(build_sitemap(), encoding="utf-8")
    robots_path.write_text(build_robots(), encoding="utf-8")
    print(f"Sitemap: {sitemap_path}")
    print(f"Robots:  {robots_path}")


if __name__ == "__main__":
    main()
