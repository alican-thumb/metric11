"""Sitemap.xml ve robots.txt üretir."""
from __future__ import annotations

from datetime import date
from pathlib import Path

from src.config import PROCESSED_DIR, SEASON

BASE_URL = "https://metric11.com"

# 2026-09-07: canlı/güncel (2026-27 sezonu, günlük yenilenen) sayfalar üst öncelikte;
# tamamlanmış 2025-26 sezonu arşiv/backtest sayfaları düşük öncelik + "monthly"/"yearly"
# changefreq ile işaretlendi — önceden hepsi "weekly"/yüksek öncelikliydi, bu da arama
# motorlarına donuk arşiv içeriğinin canlı içerik kadar sık değiştiği yanlış sinyalini
# veriyordu (bkz. PROJECT_STATE — "Maç Önü" nav'ının aynı kafa karışıklığı yarattığı bulgusu).
_PUBLIC_PAGES = [
    # --- Canlı, 2026-27 sezonu, günlük yenilenen ---
    ("gundem_2025_2026.html", 1.0, "daily"),
    ("season_fixture_predictions_2026_2027.html", 1.0, "daily"),
    ("weekly_evaluation_2026_2027.html", 0.9, "daily"),
    ("european_predictions_2026_2027.html", 1.0, "daily"),
    (f"transfer_tracker_{SEASON}.html", 0.9, "daily"),
    (f"news_intelligence_dashboard_{SEASON}.html", 0.8, "daily"),
    (f"transfer_recommendation_report_{SEASON}.html", 0.8, "weekly"),
    (f"transfer_season_context_{SEASON}.html", 0.8, "weekly"),
    ("team_scout_blueprints_2025_2026.html", 0.7, "weekly"),
    ("position_scout_matrix_2025_2026.html", 0.7, "weekly"),
    ("football_intelligence_home.html", 0.7, "weekly"),
    # --- 2025-26 sezonu arşivi / backtest (tamamlanmış, güncellenmiyor) ---
    (f"league_intelligence_{SEASON}.html", 0.4, "monthly"),
    ("all_teams_preview_dashboard_2025_2026.html", 0.4, "monthly"),
    ("football_command_center_2025_2026.html", 0.3, "monthly"),
    ("fm_style_scout_program_2025_2026.html", 0.3, "monthly"),
    ("league_market_value_audit_2025_2026.html", 0.3, "yearly"),
    ("big_match_report_2025_2026.html", 0.3, "yearly"),
    ("prediction_backtest_dashboard_2025_2026.html", 0.3, "yearly"),
    # Takım sayfaları (2025-26 sezonu arşivi)
    ("alanyaspor_2025_2026_dashboard_chronological.html", 0.3, "monthly"),
    ("amed_2025_2026_dashboard_chronological.html", 0.3, "monthly"),
    ("antalyaspor_2025_2026_dashboard_chronological.html", 0.3, "monthly"),
    ("basaksehir_2025_2026_dashboard_chronological.html", 0.3, "monthly"),
    ("besiktas_2025_2026_dashboard_chronological.html", 0.4, "monthly"),
    ("corumfk_2025_2026_dashboard_chronological.html", 0.3, "monthly"),
    ("erzurumspor_2025_2026_dashboard_chronological.html", 0.3, "monthly"),
    ("eyupspor_2025_2026_dashboard_chronological.html", 0.3, "monthly"),
    ("fenerbahce_2025_2026_dashboard_chronological.html", 0.4, "monthly"),
    ("galatasaray_2025_2026_dashboard_chronological.html", 0.4, "monthly"),
    ("gaziantep_2025_2026_dashboard_chronological.html", 0.3, "monthly"),
    ("genclerbirligi_2025_2026_dashboard_chronological.html", 0.3, "monthly"),
    ("goztepe_2025_2026_dashboard_chronological.html", 0.3, "monthly"),
    ("karagumruk_2025_2026_dashboard_chronological.html", 0.3, "monthly"),
    ("kasimpasa_2025_2026_dashboard_chronological.html", 0.3, "monthly"),
    ("kayserispor_2025_2026_dashboard_chronological.html", 0.3, "monthly"),
    ("kocaelispor_2025_2026_dashboard_chronological.html", 0.3, "monthly"),
    ("konyaspor_2025_2026_dashboard_chronological.html", 0.3, "monthly"),
    ("rizespor_2025_2026_dashboard_chronological.html", 0.3, "monthly"),
    ("samsunspor_2025_2026_dashboard_chronological.html", 0.3, "monthly"),
    ("trabzonspor_2025_2026_dashboard_chronological.html", 0.3, "monthly"),
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
