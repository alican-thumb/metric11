"""Build FIFA World Cup 2026 predictions HTML page."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone, timedelta
from html import escape
from pathlib import Path

from src.config import PROCESSED_DIR, ensure_data_dirs
from src.html_utils import nav_links_html, telegram_cta_html

# ---------------------------------------------------------------------------
# Inline CSS + tasarım sabitleri
# ---------------------------------------------------------------------------

_CSS = """
:root {
  --bg: #0a1628;
  --panel: #0f1f3d;
  --panel2: #142240;
  --accent: #f59e0b;
  --cyan: #22d3ee;
  --ink: #e2e8f0;
  --muted: #94a3b8;
  --border: #1e3a5f;
  --dark-nav: #060e1d;
  --green-accent: #4ade80;
  --red-accent: #f87171;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; }
body {
  font-family: Inter, "Segoe UI", Arial, sans-serif;
  background: var(--bg);
  color: var(--ink);
  min-height: 100vh;
}

/* ── Topbar ── */
.topbar {
  position: sticky;
  top: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  min-height: 58px;
  padding: 0 clamp(16px, 4vw, 42px);
  background: var(--dark-nav);
  border-bottom: 2px solid #0f2d52;
}
.brand {
  display: flex;
  gap: 10px;
  align-items: center;
  font-weight: 800;
  font-size: 18px;
  color: white;
  text-decoration: none;
  flex-shrink: 0;
  letter-spacing: -0.2px;
}
.brand:visited, .brand:hover { color: white; }
.brand-mark {
  width: 28px;
  height: 28px;
  display: grid;
  place-items: center;
  border-radius: 6px;
  color: #060e1d;
  background: var(--accent);
  font-size: 14px;
  font-weight: 900;
  flex-shrink: 0;
}
.brand-season {
  color: #4a6b8a;
  font-size: 11px;
  font-weight: 500;
  margin-left: 2px;
  border-left: 1px solid #1a3a5c;
  padding-left: 8px;
}
nav {
  display: flex;
  gap: 2px;
  flex-wrap: nowrap;
  overflow-x: auto;
  justify-content: flex-end;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
}
nav::-webkit-scrollbar { display: none; }
nav a {
  color: #6a8faa;
  text-decoration: none;
  font-size: 13px;
  font-weight: 600;
  padding: 8px 11px;
  border-radius: 6px;
  white-space: nowrap;
  flex-shrink: 0;
  transition: background .15s, color .15s;
}
nav a:visited { color: #6a8faa; }
nav a:hover { background: #0f2d52; color: white; }
nav a.active {
  background: #0f2d52;
  color: var(--accent);
}

/* ── Hero ── */
.hero {
  background: linear-gradient(135deg, #0a1628 0%, #0d2040 50%, #0a1628 100%);
  border-bottom: 1px solid var(--border);
  padding: 56px clamp(16px, 5vw, 80px) 48px;
  text-align: center;
  position: relative;
  overflow: hidden;
}
.hero::before {
  content: "";
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse 80% 60% at 50% 0%, rgba(245,158,11,.08) 0%, transparent 70%);
  pointer-events: none;
}
.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: rgba(245,158,11,.12);
  border: 1px solid rgba(245,158,11,.3);
  color: var(--accent);
  font-size: 12px;
  font-weight: 700;
  padding: 5px 14px;
  border-radius: 20px;
  letter-spacing: .5px;
  text-transform: uppercase;
  margin-bottom: 16px;
}
.hero h1 {
  font-size: clamp(28px, 6vw, 52px);
  font-weight: 900;
  letter-spacing: -1px;
  color: white;
  line-height: 1.1;
  margin-bottom: 12px;
}
.hero h1 span { color: var(--accent); }
.hero-subtitle {
  font-size: clamp(14px, 2.5vw, 18px);
  color: var(--muted);
  margin-bottom: 8px;
}
.hero-dates {
  font-size: 15px;
  color: var(--cyan);
  font-weight: 600;
}

/* ── Matchday tabs ── */
.tabs-wrap {
  max-width: 1100px;
  margin: 0 auto;
  padding: 32px clamp(12px, 3vw, 32px) 0;
}
.tabs-label {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 1px;
  text-transform: uppercase;
  color: var(--muted);
  margin-bottom: 12px;
}
.tabs {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-bottom: 32px;
}
.tab-btn {
  background: var(--panel);
  border: 1px solid var(--border);
  color: var(--muted);
  font-size: 13px;
  font-weight: 600;
  padding: 7px 16px;
  border-radius: 8px;
  cursor: pointer;
  transition: background .15s, color .15s, border-color .15s;
}
.tab-btn:hover { background: var(--panel2); color: var(--ink); border-color: #2a5a8c; }
.tab-btn.active {
  background: rgba(245,158,11,.15);
  border-color: var(--accent);
  color: var(--accent);
}

/* ── Match day content ── */
.matchday-section { display: none; }
.matchday-section.visible { display: block; }

/* ── Day group ── */
.day-group { margin-bottom: 40px; }
.day-header {
  font-size: 13px;
  font-weight: 700;
  color: var(--cyan);
  text-transform: uppercase;
  letter-spacing: .8px;
  padding: 8px 0 12px;
  border-bottom: 1px solid var(--border);
  margin-bottom: 16px;
}

/* ── Maç kartları ── */
.matches-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 16px;
}
.match-card {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 12px;
  overflow: hidden;
  transition: border-color .2s, transform .2s;
}
.match-card:hover {
  border-color: rgba(245,158,11,.4);
  transform: translateY(-2px);
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px 8px;
  background: rgba(255,255,255,.03);
  border-bottom: 1px solid var(--border);
  font-size: 11px;
  font-weight: 600;
  color: var(--muted);
  letter-spacing: .4px;
}
.card-group { color: var(--accent); }
.card-time { color: var(--cyan); }

/* ── Teams row ── */
.teams-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 14px 12px;
  gap: 8px;
}
.team-side {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  flex: 1;
  min-width: 0;
}
.team-logo-wrap {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: rgba(255,255,255,.06);
  border: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  flex-shrink: 0;
}
.team-logo-wrap img {
  width: 34px;
  height: 34px;
  object-fit: contain;
}
.team-short {
  font-size: 15px;
  font-weight: 800;
  color: white;
  letter-spacing: .5px;
}
.team-full {
  font-size: 10px;
  color: var(--muted);
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100px;
}
.score-center {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  flex-shrink: 0;
  padding: 0 8px;
}
.score-display {
  font-size: 26px;
  font-weight: 900;
  color: white;
  letter-spacing: 2px;
  line-height: 1;
}
.score-label {
  font-size: 9px;
  color: var(--muted);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: .8px;
}

/* ── Olasılık barları ── */
.prob-section {
  padding: 0 14px 12px;
}
.prob-bar-wrap {
  display: flex;
  height: 6px;
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 6px;
  gap: 2px;
}
.prob-seg-home {
  background: linear-gradient(90deg, #22d3ee, #38bdf8);
  border-radius: 3px 0 0 3px;
  transition: width .4s ease;
}
.prob-seg-draw {
  background: #475569;
  transition: width .4s ease;
}
.prob-seg-away {
  background: linear-gradient(90deg, #f87171, #ef4444);
  border-radius: 0 3px 3px 0;
  transition: width .4s ease;
}
.prob-labels {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: var(--muted);
}
.prob-labels span { font-weight: 700; }
.prob-labels .lbl-home { color: #38bdf8; }
.prob-labels .lbl-draw { color: #94a3b8; }
.prob-labels .lbl-away { color: #f87171; }

/* ── Stats row ── */
.stats-row {
  display: flex;
  gap: 6px;
  padding: 0 14px 12px;
  flex-wrap: wrap;
}
.stat-chip {
  background: rgba(255,255,255,.05);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 4px 10px;
  font-size: 11px;
  font-weight: 600;
  color: var(--muted);
  white-space: nowrap;
}
.stat-chip .chip-val { color: var(--ink); }
.stat-chip.over { border-color: rgba(74,222,128,.3); color: #4ade80; }
.stat-chip.over .chip-val { color: #4ade80; }
.stat-chip.under { border-color: rgba(248,113,113,.3); color: #f87171; }
.stat-chip.under .chip-val { color: #f87171; }

/* ── Narrative ── */
.narrative {
  padding: 10px 14px 14px;
  font-size: 12px;
  line-height: 1.6;
  color: var(--muted);
  border-top: 1px solid var(--border);
  font-style: italic;
}

/* ── Main wrap ── */
.main-wrap {
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 clamp(12px, 3vw, 32px) 80px;
}

/* ── Footer ── */
footer {
  text-align: center;
  padding: 40px 16px 28px;
  color: #3a5a7a;
  font-size: 12px;
  border-top: 1px solid var(--border);
  margin-top: 48px;
}
footer a { color: #3a5a7a; text-decoration: none; border-bottom: 1px solid #1e3a5f; }

/* ── Sonuç durumu ── */
.match-card.result-correct { border-color: rgba(74,222,128,.5); }
.match-card.result-wrong   { border-color: rgba(248,113,113,.4); }
.result-banner {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 7px 14px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: .3px;
}
.result-banner.correct {
  background: rgba(74,222,128,.1);
  border-bottom: 1px solid rgba(74,222,128,.25);
  color: #4ade80;
}
.result-banner.wrong {
  background: rgba(248,113,113,.08);
  border-bottom: 1px solid rgba(248,113,113,.2);
  color: #f87171;
}
.actual-score-row {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}
.actual-score {
  font-size: 32px;
  font-weight: 900;
  color: white;
  letter-spacing: 3px;
  line-height: 1;
}
.actual-label {
  font-size: 9px;
  color: var(--muted);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .8px;
}
.pred-score-sub {
  font-size: 11px;
  color: #4a6b8a;
  letter-spacing: 1px;
  font-weight: 600;
  margin-top: 2px;
}
.pred-score-sub-label {
  font-size: 9px;
  color: #334d66;
  text-transform: uppercase;
  letter-spacing: .5px;
}

/* ── Doğruluk özeti ── */
.accuracy-bar {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 16px 20px;
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  gap: 20px;
  flex-wrap: wrap;
}
.accuracy-stat {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.accuracy-stat .val {
  font-size: 22px;
  font-weight: 900;
  color: white;
}
.accuracy-stat .lbl {
  font-size: 10px;
  color: var(--muted);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: .6px;
}
.accuracy-divider {
  width: 1px;
  height: 36px;
  background: var(--border);
}
.accuracy-track {
  flex: 1;
  min-width: 120px;
}
.accuracy-track-bar {
  height: 8px;
  background: rgba(255,255,255,.08);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 5px;
}
.accuracy-track-fill {
  height: 100%;
  background: linear-gradient(90deg, #4ade80, #22d3ee);
  border-radius: 4px;
  transition: width .5s ease;
}
.accuracy-track-label {
  font-size: 11px;
  color: var(--muted);
}
.accuracy-track-label strong { color: var(--ink); }

/* ── Bugünkü Maçlar ── */
.today-section {
  max-width: 1100px;
  margin: 24px auto 0;
  padding: 0 clamp(12px, 3vw, 32px);
}
.today-header {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 12px;
  font-weight: 700;
  color: #f59e0b;
  text-transform: uppercase;
  letter-spacing: 1.2px;
  margin-bottom: 14px;
}
.today-dot {
  width: 8px; height: 8px; border-radius: 50%;
  background: #f59e0b;
  animation: pulse 2s infinite;
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.35} }
.today-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
  gap: 12px;
  margin-bottom: 8px;
}
.today-card {
  background: rgba(245,158,11,.07);
  border: 1px solid rgba(245,158,11,.28);
  border-radius: 10px;
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  gap: 7px;
}
.today-time {
  font-size: 21px;
  font-weight: 800;
  color: #f59e0b;
  letter-spacing: 1px;
  line-height: 1;
}
.today-teams {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}
.today-team { font-size: 13px; font-weight: 700; color: white; }
.today-vs { font-size: 11px; color: var(--muted); }
.today-pred {
  font-size: 22px;
  font-weight: 900;
  color: white;
  letter-spacing: 3px;
  line-height: 1;
}
.today-probs { display: flex; gap: 10px; font-size: 12px; font-weight: 600; }
.today-group { font-size: 10px; color: var(--muted); text-transform: uppercase; letter-spacing: .5px; }

/* ── Knockout section ── */
.ko-section { display: none; }
.ko-section.visible { display: block; }
.ko-stage { margin-bottom: 36px; }
.ko-stage-title {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 1.2px;
  text-transform: uppercase;
  color: var(--accent);
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.ko-stage-title::after {
  content: "";
  flex: 1;
  height: 1px;
  background: var(--border);
}
.ko-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 10px;
}
.ko-card {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 13px 15px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.ko-card.ko-finished { border-color: rgba(74,222,128,.35); }
.ko-card.ko-pending  { border-color: rgba(245,158,11,.25); }
.ko-date {
  font-size: 11px;
  color: var(--muted);
  font-weight: 500;
}
.ko-teams {
  display: flex;
  align-items: center;
  gap: 10px;
}
.ko-team {
  flex: 1;
  font-size: 14px;
  font-weight: 700;
  color: white;
}
.ko-team.tbd { color: #3a5a7a; font-style: italic; }
.ko-team.away-team { text-align: right; }
.ko-score {
  font-size: 20px;
  font-weight: 900;
  color: white;
  letter-spacing: 3px;
  text-align: center;
  min-width: 52px;
}
.ko-score.result { color: #4ade80; }
.ko-score.predicted { color: #f59e0b; font-size: 16px; }
.ko-probs {
  display: flex;
  gap: 8px;
  font-size: 11px;
  font-weight: 600;
}
.ko-tbd-badge {
  font-size: 11px;
  color: #3a5a7a;
  font-style: italic;
  text-align: center;
}
.ko-result-tag {
  font-size: 11px;
  font-weight: 700;
  padding: 3px 8px;
  border-radius: 4px;
  align-self: flex-start;
}
.ko-result-tag.correct { background: rgba(74,222,128,.15); color: #4ade80; }
.ko-result-tag.wrong   { background: rgba(248,113,113,.1); color: #f87171; }

/* ── Responsive ── */
@media (max-width: 680px) {
  .topbar {
    position: static;
    flex-direction: column;
    align-items: stretch;
    padding: 11px 16px 0;
    gap: 0;
    min-height: unset;
  }
  .brand { padding-bottom: 8px; }
  .brand-season { display: none; }
  nav {
    justify-content: flex-start;
    border-top: 1px solid #1a3a5c;
    padding: 7px 0 9px;
  }
  .matches-grid { grid-template-columns: 1fr; }
  .hero { padding: 36px 16px 32px; }
  .team-full { display: none; }
}
@media (max-width: 420px) {
  .score-display { font-size: 20px; }
  .team-short { font-size: 13px; }
}
"""

# ---------------------------------------------------------------------------
# Nav linkleri
# ---------------------------------------------------------------------------
def _build_topbar() -> str:
    nav_items = nav_links_html("worldcup_2026_predictions.html")
    return (
        '<div class="topbar">'
        '<a class="brand" href="/">'
        '<span class="brand-mark">11</span>'
        " metric11"
        '<span class="brand-season">D&uuml;nya Kupas&iota; 2026</span>'
        "</a>"
        f"<nav>{nav_items}</nav>"
        "</div>"
    )


# ---------------------------------------------------------------------------
# Tarih yardımcıları
# ---------------------------------------------------------------------------
_TR_MONTHS = [
    "", "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
    "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık",
]
_TR_DAYS = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]

_TZ_TURKEY = timezone(timedelta(hours=3))


def _parse_utc(utc_str: str) -> datetime | None:
    if not utc_str:
        return None
    try:
        # Handle both 'Z' and '+00:00' suffixes
        s = utc_str.replace("Z", "+00:00")
        return datetime.fromisoformat(s).astimezone(_TZ_TURKEY)
    except (ValueError, TypeError):
        return None


def _format_date_header(dt: datetime) -> str:
    day_name = _TR_DAYS[dt.weekday()]
    month_name = _TR_MONTHS[dt.month]
    return f"{dt.day} {month_name} {dt.year}, {day_name}"


def _format_time(dt: datetime) -> str:
    return dt.strftime("%H:%M")


def _date_key(dt: datetime | None) -> str:
    if dt is None:
        return "9999-99-99"
    return dt.strftime("%Y-%m-%d")


# ---------------------------------------------------------------------------
# HTML parçaları
# ---------------------------------------------------------------------------

def _logo_html(crest_url: str, team_name: str) -> str:
    safe_name = escape(team_name)
    if crest_url:
        safe_url = escape(crest_url)
        return (
            f'<div class="team-logo-wrap">'
            f'<img src="{safe_url}" alt="{safe_name}" loading="lazy" '
            f'onerror="this.style.display=\'none\'">'
            f"</div>"
        )
    return f'<div class="team-logo-wrap"></div>'


def _match_card_html(pred: dict) -> str:
    home = pred.get("home", {})
    away = pred.get("away", {})
    prediction = pred.get("prediction", {})
    group = pred.get("group", "")
    utc_date = pred.get("utc_date", "")
    dt = _parse_utc(utc_date)
    time_str = _format_time(dt) if dt else "--:--"

    home_name = escape(home.get("name", ""))
    away_name = escape(away.get("name", ""))
    home_short = escape(home.get("short", home.get("name", "")[:3].upper()))
    away_short = escape(away.get("short", away.get("name", "")[:3].upper()))

    # Tahmin skoru
    pred_score = prediction.get("predicted_score", {})
    pred_h = pred_score.get("home", "?")
    pred_a = pred_score.get("away", "?")

    # Gerçek sonuç
    actual_score = pred.get("actual_score")
    outcome = pred.get("prediction_outcome", "pending")
    is_finished = outcome != "pending"

    # Olasılıklar
    hw = prediction.get("home_win", 0.0)
    dr = prediction.get("draw", 0.0)
    aw = prediction.get("away_win", 0.0)
    hw_pct = int(round(hw * 100))
    dr_pct = int(round(dr * 100))
    aw_pct = int(round(aw * 100))

    # Gol/kart
    over_25 = prediction.get("goals_over_2_5", 0.0)
    over_25_pct = int(round(over_25 * 100))
    cards = prediction.get("expected_cards", 3.5)
    over_class = "over" if over_25 >= 0.5 else "under"
    over_label = "ÜST" if over_25 >= 0.5 else "ALT"

    # Grup etiket
    group_display = group.replace("_", " ") if group else "TBD"

    # Narrative
    narrative = escape(prediction.get("narrative", ""))
    home_str = home.get("strength", 50)
    away_str = away.get("strength", 50)

    # Kart CSS sınıfı
    card_class = ""
    if outcome == "correct":
        card_class = " result-correct"
    elif outcome == "wrong":
        card_class = " result-wrong"

    # Sonuç banner
    result_banner_html = ""
    if outcome == "correct":
        result_banner_html = '<div class="result-banner correct">&#10003; Tahmin Doğru</div>'
    elif outcome == "wrong":
        result_banner_html = '<div class="result-banner wrong">&#10007; Tahmin Yanlış</div>'

    # Skor alanı: oynandıysa gerçek skoru büyük göster
    if is_finished and actual_score is not None:
        ah = actual_score.get("home", "?")
        aa = actual_score.get("away", "?")
        score_center_html = f"""<div class="actual-score-row">
      <div class="actual-score">{ah} &ndash; {aa}</div>
      <div class="actual-label">Sonuç</div>
      <div class="pred-score-sub">{pred_h} &ndash; {pred_a}</div>
      <div class="pred-score-sub-label">tahmin</div>
    </div>"""
    else:
        score_center_html = f"""<div class="score-center">
      <div class="score-display">{pred_h} - {pred_a}</div>
      <div class="score-label">tahmin</div>
    </div>"""

    return f"""
<div class="match-card{card_class}">
  {result_banner_html}
  <div class="card-header">
    <span class="card-group">{escape(group_display)}</span>
    <span>G&uuml;&ccedil;: {home_str} - {away_str}</span>
    <span class="card-time">{escape(time_str)}</span>
  </div>
  <div class="teams-row">
    <div class="team-side">
      {_logo_html(home.get("crest", ""), home.get("name", ""))}
      <span class="team-short">{home_short}</span>
      <span class="team-full">{home_name}</span>
    </div>
    {score_center_html}
    <div class="team-side">
      {_logo_html(away.get("crest", ""), away.get("name", ""))}
      <span class="team-short">{away_short}</span>
      <span class="team-full">{away_name}</span>
    </div>
  </div>
  <div class="prob-section">
    <div class="prob-bar-wrap">
      <div class="prob-seg-home" style="width:{hw_pct}%"></div>
      <div class="prob-seg-draw" style="width:{dr_pct}%"></div>
      <div class="prob-seg-away" style="width:{aw_pct}%"></div>
    </div>
    <div class="prob-labels">
      <span class="lbl-home">Ev %{hw_pct}</span>
      <span class="lbl-draw">Ber %{dr_pct}</span>
      <span class="lbl-away">Dep %{aw_pct}</span>
    </div>
  </div>
  <div class="stats-row">
    <div class="stat-chip {over_class}">2.5 <span class="chip-val">{over_label} %{over_25_pct}</span></div>
    <div class="stat-chip">Kart <span class="chip-val">~{cards}</span></div>
  </div>
  <div class="narrative">{narrative}</div>
</div>"""


def _build_matchday_section(md_key: str, predictions: list[dict]) -> str:
    """Tek bir matchday için HTML section üretir, maçları gün bazında gruplar."""
    # Gün bazında grupla
    day_groups: dict[str, list[dict]] = {}
    day_dt_map: dict[str, datetime | None] = {}
    for pred in predictions:
        dt = _parse_utc(pred.get("utc_date", ""))
        dk = _date_key(dt)
        day_groups.setdefault(dk, []).append(pred)
        if dk not in day_dt_map:
            day_dt_map[dk] = dt

    # Günleri sırala
    sorted_days = sorted(day_groups.keys())

    day_html_parts = []
    for dk in sorted_days:
        day_preds = day_groups[dk]
        day_dt = day_dt_map.get(dk)
        header = _format_date_header(day_dt) if day_dt else escape(dk)
        cards_html = "\n".join(_match_card_html(p) for p in day_preds)
        day_html_parts.append(
            f'<div class="day-group">'
            f'<div class="day-header">{escape(header)}</div>'
            f'<div class="matches-grid">{cards_html}</div>'
            f"</div>"
        )

    inner = "\n".join(day_html_parts)
    return (
        f'<div class="matchday-section" data-matchday="{escape(md_key)}">'
        f"{inner}"
        f"</div>"
    )


def _build_tabs(md_keys: list[str]) -> str:
    group_btns = "".join(
        f'<button class="tab-btn" data-tab="{escape(k)}" onclick="showMatchday(\'{escape(k)}\')">'
        f"{escape(k)}. Hafta</button>"
        for k in md_keys
    )
    ko_btn = '<button class="tab-btn" data-tab="knockout" onclick="showMatchday(\'knockout\')">🏆 Eleme</button>'
    return (
        '<div class="tabs-label">Grup Aşaması Haftaları &amp; Eleme</div>'
        f'<div class="tabs" id="tabs-container">{group_btns}{ko_btn}</div>'
    )


_KO_STAGE_LABELS = {
    "LAST_32":       "Tur 32 — 1 Temmuz'dan itibaren",
    "LAST_16":       "Son 16 — 6 Temmuz'dan itibaren",
    "QUARTER_FINALS": "Çeyrek Final — 9 Temmuz'dan itibaren",
    "SEMI_FINALS":   "Yarı Final — 14 Temmuz",
    "THIRD_PLACE":   "3. Yer Maçı — 18 Temmuz",
    "FINAL":         "Final — 19 Temmuz",
}


def _ko_card_html(m: dict) -> str:
    home = m.get("home", {})
    away = m.get("away", {})
    home_name = home.get("name", "")
    away_name = away.get("name", "")
    dt = _parse_utc(m.get("utc_date", ""))
    date_str = ""
    if dt:
        date_str = f"{dt.day} {_TR_MONTHS[dt.month]}, {_format_time(dt)}"

    outcome = m.get("prediction_outcome", "tbd")
    actual = m.get("actual_score")
    pred = m.get("prediction")

    card_cls = "ko-card"
    if actual:
        card_cls += " ko-finished"
    elif home_name:
        card_cls += " ko-pending"

    home_cls = "ko-team" + (" tbd" if not home_name else "")
    away_cls = "ko-team away-team" + (" tbd" if not away_name else "")
    home_disp = escape(home_name) if home_name else "TBD"
    away_disp = escape(away_name) if away_name else "TBD"

    # Skor alanı
    if actual:
        score_html = f'<div class="ko-score result">{actual["home"]} – {actual["away"]}</div>'
    elif pred:
        ps = pred.get("predicted_score", {})
        score_html = f'<div class="ko-score predicted">{ps.get("home","?")} – {ps.get("away","?")}</div>'
    else:
        score_html = '<div class="ko-score" style="color:#2a4a6a">? – ?</div>'

    # Olasılıklar
    probs_html = ""
    if pred and not actual:
        hw = int(round(pred.get("home_win", 0) * 100))
        dr = int(round(pred.get("draw", 0) * 100))
        aw = int(round(pred.get("away_win", 0) * 100))
        probs_html = (
            f'<div class="ko-probs">'
            f'<span style="color:#4ade80">1 %{hw}</span>'
            f'<span style="color:#94a3b8">X %{dr}</span>'
            f'<span style="color:#f87171">2 %{aw}</span>'
            f'</div>'
        )

    # Sonuç etiketi
    result_tag = ""
    if outcome == "correct":
        result_tag = '<span class="ko-result-tag correct">✓ Doğru</span>'
    elif outcome == "wrong":
        result_tag = '<span class="ko-result-tag wrong">✗ Yanlış</span>'

    tbd_note = "" if home_name else '<div class="ko-tbd-badge">Takımlar henüz belli değil</div>'

    return (
        f'<div class="{card_cls}">'
        f'<div class="ko-date">{escape(date_str)}</div>'
        f'<div class="ko-teams">'
        f'<span class="{home_cls}">{home_disp}</span>'
        f'{score_html}'
        f'<span class="{away_cls}">{away_disp}</span>'
        f'</div>'
        f'{probs_html}'
        f'{tbd_note}'
        f'{result_tag}'
        f'</div>'
    )


def _build_knockout_section(knockout_stages: dict[str, list]) -> str:
    stage_parts = []
    for stage_key, label in _KO_STAGE_LABELS.items():
        matches = knockout_stages.get(stage_key, [])
        if not matches:
            continue
        cards_html = "\n".join(_ko_card_html(m) for m in matches)
        stage_parts.append(
            f'<div class="ko-stage">'
            f'<div class="ko-stage-title">{escape(label)}</div>'
            f'<div class="ko-grid">{cards_html}</div>'
            f'</div>'
        )
    inner = "\n".join(stage_parts)
    return (
        f'<div class="ko-section matchday-section" data-matchday="knockout">'
        f'{inner}'
        f'</div>'
    )


def _build_today_section(today_matches: list[dict]) -> str:
    """Bugün oynanacak maçları özet panel olarak gösterir."""
    upcoming = [m for m in today_matches if m.get("prediction_outcome") == "pending"]
    if not upcoming:
        return ""
    upcoming_sorted = sorted(upcoming, key=lambda m: m.get("utc_date", ""))
    cards = []
    for m in upcoming_sorted:
        home_name = escape(m.get("home", {}).get("name", ""))
        away_name = escape(m.get("away", {}).get("name", ""))
        dt = _parse_utc(m.get("utc_date", ""))
        time_str = escape(_format_time(dt) if dt else "--:--")
        pred = m.get("prediction", {})
        pred_score = pred.get("predicted_score", {})
        ph = pred_score.get("home", "?")
        pa = pred_score.get("away", "?")
        hw = int(round(pred.get("home_win", 0) * 100))
        dr = int(round(pred.get("draw", 0) * 100))
        aw = int(round(pred.get("away_win", 0) * 100))
        group = escape(m.get("group", "").replace("_", " "))
        cards.append(
            f'<div class="today-card">'
            f'<div class="today-time">{time_str}</div>'
            f'<div class="today-teams">'
            f'<span class="today-team">{home_name}</span>'
            f'<span class="today-vs">vs</span>'
            f'<span class="today-team">{away_name}</span>'
            f'</div>'
            f'<div class="today-pred">{ph} &ndash; {pa}</div>'
            f'<div class="today-probs">'
            f'<span style="color:#4ade80">1 %{hw}</span>'
            f'<span style="color:#94a3b8">X %{dr}</span>'
            f'<span style="color:#f87171">2 %{aw}</span>'
            f'</div>'
            f'<div class="today-group">{group}</div>'
            f'</div>'
        )
    cards_html = "\n".join(cards)
    count = len(upcoming)
    return (
        f'<div class="today-section">'
        f'<div class="today-header">'
        f'<span class="today-dot"></span>'
        f'Bugün {count} Maç &mdash; Tahminlerimiz'
        f'</div>'
        f'<div class="today-grid">{cards_html}</div>'
        f'</div>'
    )


def _build_js(today_md: str) -> str:
    return f"""<script>
function showMatchday(md) {{
  document.querySelectorAll('.matchday-section').forEach(function(el) {{
    el.classList.remove('visible');
  }});
  var target = document.querySelector('.matchday-section[data-matchday="' + md + '"]');
  if (target) target.classList.add('visible');
  document.querySelectorAll('.tab-btn').forEach(function(btn) {{
    btn.classList.toggle('active', btn.dataset.tab === md);
  }});
}}
document.addEventListener('DOMContentLoaded', function() {{
  var todayMd = {json.dumps(today_md)};
  var btn = todayMd
    ? document.querySelector('.tab-btn[data-tab="' + todayMd + '"]')
    : null;
  var first = btn || document.querySelector('.tab-btn');
  if (first) showMatchday(first.dataset.tab);
}});
</script>"""


def _build_accuracy_bar(stats: dict) -> str:
    finished = stats.get("finished", 0)
    correct = stats.get("correct", 0)
    wrong = stats.get("wrong", 0)
    pct = stats.get("accuracy_pct")
    if finished == 0:
        return ""
    pct_val = pct if pct is not None else 0
    fill_w = int(round(pct_val))
    pct_str = f"%{pct_val:.0f}" if pct is not None else "—"
    return f"""<div class="accuracy-bar">
  <div class="accuracy-stat">
    <span class="val">{finished}</span>
    <span class="lbl">Oynandı</span>
  </div>
  <div class="accuracy-divider"></div>
  <div class="accuracy-stat">
    <span class="val" style="color:#4ade80">{correct}</span>
    <span class="lbl">Doğru</span>
  </div>
  <div class="accuracy-divider"></div>
  <div class="accuracy-stat">
    <span class="val" style="color:#f87171">{wrong}</span>
    <span class="lbl">Yanlış</span>
  </div>
  <div class="accuracy-divider"></div>
  <div class="accuracy-track">
    <div class="accuracy-track-bar">
      <div class="accuracy-track-fill" style="width:{fill_w}%"></div>
    </div>
    <div class="accuracy-track-label">Genel doğruluk: <strong>{pct_str}</strong></div>
  </div>
</div>"""


def build_page(predictions_data: dict) -> str:
    matchday_preds: dict[str, list] = predictions_data.get("matchday_predictions", {})
    generated_at = predictions_data.get("generated_at", "")
    accuracy_stats = predictions_data.get("accuracy_stats", {})

    # Matchday anahtarlarını sayısal sıraya göre sırala, matchday 0 (eleme) dahil etme
    md_keys = sorted(
        [k for k in matchday_preds.keys() if k.isdigit() and int(k) > 0],
        key=lambda x: int(x)
    )

    # Bugünkü maçları bul (UTC tarihine göre)
    today_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    today_matches: list[dict] = []
    today_md = ""
    for k, matches in matchday_preds.items():
        for m in matches:
            if m.get("utc_date", "")[:10] == today_utc:
                today_matches.append(m)
                if not today_md:
                    today_md = k

    knockout_stages: dict[str, list] = predictions_data.get("knockout_stages", {})

    accuracy_html = _build_accuracy_bar(accuracy_stats)
    today_html = _build_today_section(today_matches)
    tabs_html = _build_tabs(md_keys)
    sections_html = "\n".join(
        _build_matchday_section(k, matchday_preds[k]) for k in md_keys
    )
    knockout_html = _build_knockout_section(knockout_stages)

    # Üretim zamanı
    try:
        gen_dt = datetime.fromisoformat(generated_at.replace("Z", "+00:00"))
        gen_str = gen_dt.astimezone(_TZ_TURKEY).strftime("%d.%m.%Y %H:%M")
    except (ValueError, AttributeError):
        gen_str = generated_at[:10] if generated_at else "—"

    total_matches = predictions_data.get("total_matches", 0)

    return f"""<!doctype html>
<html lang="tr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Dünya Kupası 2026 Maç Tahminleri ve Skor Öngörüleri | metric11</title>
  <meta name="description" content="FIFA Dünya Kupası 2026 — 104 maç için istatistiksel tahminler, skor öngörüleri, kazanma olasılıkları. Günlük güncellenen WC 2026 analiz platformu.">
  <meta property="og:title" content="Dünya Kupası 2026 Maç Tahminleri | metric11">
  <meta property="og:description" content="104 maç için istatistiksel tahminler, kazanma olasılıkları ve skor öngörüleri. Her gün güncelleniyor.">
  <meta property="og:image" content="https://metric11.com/og-image.png">
  <meta property="og:type" content="website">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:image" content="https://metric11.com/og-image.png">
  <meta name="theme-color" content="#0a1628">
  <meta property="og:url" content="https://metric11.com/worldcup_2026_predictions.html">
  <link rel="canonical" href="https://metric11.com/worldcup_2026_predictions.html">
  <link rel="icon" href="favicon.svg" type="image/svg+xml">
  <script type="application/ld+json">{{
    "@context": "https://schema.org",
    "@type": "WebPage",
    "name": "FIFA Dünya Kupası 2026 Tahminleri",
    "description": "104 maç için istatistiksel tahminler, kazanma olasılıkları ve skor öngörüleri.",
    "url": "https://metric11.com/worldcup_2026_predictions.html",
    "publisher": {{"@type": "Organization", "name": "metric11", "url": "https://metric11.com"}}
  }}</script>
  <style>{_CSS}</style>
</head>
<body>
  {_build_topbar()}

  <div class="hero">
    <div class="hero-badge">&#x26BD; FIFA D&uuml;nya Kupas&#x131; 2026</div>
    <h1>FIFA D&uuml;nya Kupas&#x131; <span>2026</span></h1>
    <p class="hero-subtitle">{total_matches} ma&ccedil; &middot; 48 tak&#x131;m &middot; &Iuml;statistiksel tahminler</p>
    <p class="hero-dates">11 Haziran — 19 Temmuz 2026</p>
  </div>

  {today_html}

  <div class="tabs-wrap">
    <div style="margin-bottom:16px">{telegram_cta_html()}</div>
    {accuracy_html}
    {tabs_html}
  </div>

  <div class="main-wrap">
    {sections_html}
    {knockout_html}
  </div>

  <footer>
    metric11 &middot; <a href="mailto:hello@metric11.com">hello@metric11.com</a>
    &nbsp;&middot;&nbsp; Son g&uuml;ncelleme: {escape(gen_str)}
  </footer>

  {_build_js(today_md)}
  <script defer src="/_vercel/insights/script.js"></script>
</body>
</html>"""


def main() -> None:
    parser = argparse.ArgumentParser(
        description="WC 2026 tahminleri için HTML sayfası üretir."
    )
    parser.add_argument(
        "--predictions",
        default=str(PROCESSED_DIR / "worldcup_2026_predictions.json"),
        help="Tahmin JSON dosyası",
    )
    parser.add_argument(
        "--output",
        default=str(PROCESSED_DIR / "worldcup_2026_predictions.html"),
        help="Çıktı HTML dosyası",
    )
    args = parser.parse_args()

    ensure_data_dirs()

    preds_path = Path(args.predictions)
    if not preds_path.exists():
        print(f"HATA: Tahmin dosyası bulunamadı: {preds_path}")
        print("Önce `python -m src.analyze_worldcup_predictions` çalıştırın.")
        raise SystemExit(1)

    predictions_data = json.loads(preds_path.read_text(encoding="utf-8"))
    html = build_page(predictions_data)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    print(f"HTML kaydedildi: {out_path}", flush=True)
    print(f"Boyut: {len(html):,} karakter", flush=True)


if __name__ == "__main__":
    main()
