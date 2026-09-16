"""UEFA Şampiyonlar Ligi, Avrupa Ligi ve Konferans Ligi 2026-27 tahmin sayfası üretir."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta, timezone
from html import escape
from pathlib import Path

from src.config import DATA_DIR, PROCESSED_DIR, SEASON, ensure_data_dirs
from src.html_utils import nav_links_html, telegram_cta_html

INPUT_PATH  = PROCESSED_DIR / "european_predictions_2026_2027.json"
OUTPUT_PATH = PROCESSED_DIR / "european_predictions_2026_2027.html"
PULSE_PATH  = PROCESSED_DIR / f"european_news_pulse_{SEASON}.json"
KNOWN_FIXTURES_PATH = DATA_DIR / "manual" / "european_qualifier_fixtures_2026_2027.json"

_TR_WEEKDAYS = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]

_TZ_TR = timezone(timedelta(hours=3))

_TR_MONTHS = ["", "Oca", "Şub", "Mar", "Nis", "May", "Haz",
              "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara"]

_COMP_EMOJI = {"CL": "🏆", "EL": "🟠", "ECL": "🟢"}
_COMP_COLOR = {"CL": "#f59e0b", "EL": "#f97316", "ECL": "#22c55e"}

_STAGE_TR = {
    "PRELIMINARY_ROUND":     "Ön Tur",
    "QUALIFYING":            "Nitelendirme",
    "QUALIFYING_ROUNDS":     "Nitelendirme",
    "1ST_QUALIFYING_ROUND":  "1. Nitelendirme",
    "2ND_QUALIFYING_ROUND":  "2. Nitelendirme",
    "3RD_QUALIFYING_ROUND":  "3. Nitelendirme",
    "4TH_QUALIFYING_ROUND":  "4. Nitelendirme",
    "PLAY_OFF_ROUND":        "Play-off",
    "PLAYOFF_ROUND":         "Play-off",
    "LEAGUE_PHASE":          "Lig Fazı",
    "LEAGUE_STAGE":          "Lig Aşaması",
    "GROUP_STAGE":           "Grup Aşaması",
    "LAST_32":               "Tur 32",
    "LAST_16":               "Son 16",
    "QUARTER_FINALS":        "Çeyrek Final",
    "SEMI_FINALS":           "Yarı Final",
    "THIRD_PLACE":           "3. Yer",
    "FINAL":                 "Final",
}

_CSS = """
:root {
  --bg: #09111f; --panel: #0e1929; --panel2: #13223a;
  --ink: #e2e8f0; --muted: #64748b; --border: #1e3a5f;
  --cl: #f59e0b; --el: #f97316; --ecl: #22c55e;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; }
body { font-family: Inter, "Segoe UI", Arial, sans-serif; background: var(--bg); color: var(--ink); min-height: 100vh; }

/* Nav */
.topbar { background: #060e1d; border-bottom: 2px solid #1a3023; min-height: 54px; padding: 0 clamp(12px,3vw,32px); display: flex; align-items: center; justify-content: space-between; gap: 16px; }
.brand { display: flex; align-items: center; gap: 9px; color: white; text-decoration: none; font-size: 17px; font-weight: 800; }
.brand:visited,.brand:active,.brand:hover{color:white}
.brand b { width:26px;height:26px;border-radius:5px;display:grid;place-items:center;background:#cde94e;color:#060e1d;font-size:13px;font-weight:900; }
.brand-lbl { font-size:11px;color:#4a6b72;border-left:1px solid #1e3228;padding-left:8px;margin-left:2px; }
nav { display:flex;gap:2px;overflow-x:auto;scrollbar-width:none; }
nav::-webkit-scrollbar{display:none}
nav a { white-space:nowrap;color:#64748b;padding:7px 10px;border-radius:6px;text-decoration:none;font-size:12px;font-weight:600;transition:.15s; }
nav a:visited{color:#64748b}
nav a:hover,nav a.active { background:#0f2030;color:white; }
@media(max-width:660px){.topbar{flex-direction:column;align-items:stretch;padding:10px 12px 0;min-height:unset}.brand{padding-bottom:8px}nav{border-top:1px solid #1e3228;padding:6px 0 8px}}

/* Hero */
.hero { background: linear-gradient(160deg,#0a1929 0%,#060e1d 100%); padding: 32px clamp(12px,3vw,32px) 28px; border-bottom: 1px solid var(--border); }
.hero h1 { font-size: clamp(20px,4vw,30px); font-weight: 800; color: white; margin-bottom: 6px; }
.hero p { font-size: 13px; color: var(--muted); }
.hero-badges { display:flex;gap:10px;margin-top:14px;flex-wrap:wrap; }
.hero-badge { padding:5px 13px;border-radius:20px;font-size:12px;font-weight:700; }

/* Stat bar */
.stat-bar { display:flex;gap:10px;padding:16px clamp(12px,3vw,32px);flex-wrap:wrap;max-width:1200px;margin:0 auto;border-bottom:1px solid var(--border); }
.stat-chip { background:var(--panel);border:1px solid var(--border);border-radius:8px;padding:10px 16px;text-align:center;min-width:110px; }
.stat-chip .v { font-size:20px;font-weight:800; }
.stat-chip .l { font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:.5px;margin-top:3px; }

/* Comp tabs */
.comp-tabs { display:flex;gap:6px;padding:18px clamp(12px,3vw,32px) 0;max-width:1200px;margin:0 auto;flex-wrap:wrap; }
.comp-tab { padding:7px 16px;border-radius:8px;border:1px solid var(--border);background:var(--panel);color:var(--muted);font-size:13px;font-weight:600;cursor:pointer;transition:.15s; }
.comp-tab:hover { background:var(--panel2);color:var(--ink); }
.comp-tab.active-cl { border-color:var(--cl);color:var(--cl);background:rgba(245,158,11,.1); }
.comp-tab.active-el { border-color:var(--el);color:var(--el);background:rgba(249,115,22,.1); }
.comp-tab.active-ecl { border-color:var(--ecl);color:var(--ecl);background:rgba(34,197,94,.1); }
.comp-tab.active-all { border-color:#60a5fa;color:#60a5fa;background:rgba(96,165,250,.1); }

/* Main */
.main { max-width:1200px;margin:0 auto;padding:20px clamp(12px,3vw,32px) 60px; }
.comp-section { display:none; }
.comp-section.visible { display:block; }

/* Stage header */
.stage-header { font-size:11px;font-weight:700;letter-spacing:1.2px;text-transform:uppercase;color:var(--muted);margin:28px 0 12px;display:flex;align-items:center;gap:8px; }
.stage-header::after { content:'';flex:1;height:1px;background:var(--border); }

/* Match grid */
.match-grid { display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:10px; }

/* Match card */
.match-card { background:var(--panel);border:1px solid var(--border);border-radius:10px;padding:13px 15px;display:flex;flex-direction:column;gap:8px;transition:border-color .2s; }
.match-card:hover { border-color:#2a4a6a; }
.match-card.mc-correct { border-color:rgba(74,222,128,.4); }
.match-card.mc-wrong { border-color:rgba(248,113,113,.35); }
.match-card.mc-pending { border-color:rgba(245,158,11,.2); }
.mc-meta { display:flex;justify-content:space-between;align-items:center;font-size:10px;color:var(--muted); }
.mc-date { font-weight:500; }
.mc-group { background:var(--panel2);padding:2px 7px;border-radius:4px;font-size:10px;font-weight:600; }
.mc-teams { display:flex;align-items:center;gap:8px; }
.mc-team { flex:1;font-size:13px;font-weight:700;color:white; }
.mc-team.away { text-align:right; }
.mc-team.tbd { color:#2a4a6a;font-style:italic; }
.mc-score { text-align:center;min-width:48px; }
.mc-score .result { font-size:20px;font-weight:900;color:#4ade80;letter-spacing:3px; }
.mc-score .predicted { font-size:15px;font-weight:700;color:var(--cl);letter-spacing:2px; }
.mc-score .pending-score { font-size:15px;font-weight:700;color:#f59e0b;letter-spacing:2px; }
.mc-score .tbd-score { font-size:13px;color:#2a4a6a; }
.mc-probs { display:flex;gap:8px;font-size:11px;font-weight:600; }
.mc-result-tag { font-size:10px;font-weight:700;padding:2px 8px;border-radius:4px;align-self:flex-start; }
.mc-result-tag.correct { background:rgba(74,222,128,.12);color:#4ade80; }
.mc-result-tag.wrong { background:rgba(248,113,113,.1);color:#f87171; }
.mc-tbd-note { font-size:10px;color:#2a4a6a;font-style:italic; }

/* Today section */
.today-wrap { background:rgba(245,158,11,.06);border:1px solid rgba(245,158,11,.2);border-radius:12px;padding:18px 20px;margin-bottom:24px; }
.today-lbl { font-size:11px;font-weight:700;color:#f59e0b;text-transform:uppercase;letter-spacing:1.2px;margin-bottom:12px;display:flex;align-items:center;gap:8px; }
.today-dot { width:7px;height:7px;border-radius:50%;background:#f59e0b;animation:pulse 2s infinite; }
@keyframes pulse { 0%,100%{opacity:1}50%{opacity:.3} }
.today-grid { display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:10px; }

/* Pulse (haber nabzı) */
.pulse-wrap { background:rgba(34,197,94,.05);border:1px solid rgba(34,197,94,.2);border-radius:12px;padding:18px 20px;margin-bottom:24px; }
.pulse-lbl { font-size:11px;font-weight:700;color:#4ade80;text-transform:uppercase;letter-spacing:1.2px;margin-bottom:4px;display:flex;align-items:center;gap:8px; }
.pulse-note { font-size:11px;color:var(--muted);margin-bottom:14px;line-height:1.5; }
.pulse-list { display:flex;flex-direction:column;gap:8px; }
.pulse-item { display:flex;flex-direction:column;gap:3px;padding:10px 12px;background:var(--panel);border:1px solid var(--border);border-radius:8px;text-decoration:none; }
.pulse-item:hover { border-color:#2a4a6a; }
.pulse-title { font-size:13px;font-weight:700;color:white; }
.pulse-meta { font-size:10px;color:var(--muted);display:flex;gap:8px;flex-wrap:wrap; }
.pulse-comp-tag { font-weight:700; }
.pulse-club-tag { background:var(--panel2);padding:1px 6px;border-radius:4px; }

/* Logo */
.team-logo { width:20px;height:20px;object-fit:contain;vertical-align:middle;margin-right:5px; }
.mc-logo { display:inline-flex;align-items:center;gap:5px;flex:1; }
.mc-logo.away { flex-direction:row-reverse;text-align:right; }

/* Footer */
footer { text-align:center;padding:32px 16px 24px;color:#1e3a5f;font-size:11px;border-top:1px solid var(--border);margin-top:32px; }
footer a { color:#1e3a5f; }
"""

_JS = """
<script>
function showComp(code) {
  document.querySelectorAll('.comp-section').forEach(function(el) {
    el.classList.remove('visible');
  });
  var all = document.querySelectorAll('.comp-section');
  if (code === 'ALL') {
    all.forEach(function(el){ el.classList.add('visible'); });
  } else {
    var t = document.querySelector('.comp-section[data-comp="' + code + '"]');
    if (t) t.classList.add('visible');
  }
  document.querySelectorAll('.comp-tab').forEach(function(btn){
    btn.className = btn.className.replace(/ active-\\S+/g,'');
    if (btn.dataset.comp === code) {
      btn.classList.add('active-' + (code === 'ALL' ? 'all' : code.toLowerCase()));
    }
  });
}
document.addEventListener('DOMContentLoaded', function() {
  var first = document.querySelector('.comp-tab');
  if (first) showComp(first.dataset.comp);
});
</script>
"""


def _parse_utc(s: str) -> datetime | None:
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(_TZ_TR)
    except (ValueError, AttributeError):
        return None


def _fmt_date(dt: datetime | None) -> str:
    if not dt:
        return "—"
    return f"{dt.day} {_TR_MONTHS[dt.month]}, {dt.strftime('%H:%M')}"


def _logo_img(url: str, name: str) -> str:
    if not url:
        return ""
    return f'<img src="{escape(url)}" alt="{escape(name)}" class="team-logo" loading="lazy" onerror="this.style.display=\'none\'">'


def _match_card(m: dict, comp_color: str) -> str:
    home = m.get("home", {})
    away = m.get("away", {})
    hn = home.get("name", "")
    an = away.get("name", "")
    dt = _parse_utc(m.get("utc_date", ""))
    date_str = _fmt_date(dt)
    outcome = m.get("prediction_outcome", "tbd")
    actual = m.get("actual_score")
    pred = m.get("prediction") or {}
    group = m.get("group", "")
    stage = _STAGE_TR.get(m.get("stage", ""), m.get("stage", ""))

    card_cls = "match-card"
    if outcome == "correct":
        card_cls += " mc-correct"
    elif outcome == "wrong":
        card_cls += " mc-wrong"
    elif hn and outcome == "pending":
        card_cls += " mc-pending"

    home_cls = "mc-team" + ("" if hn else " tbd")
    away_cls = "mc-team away" + ("" if an else " tbd")
    h_disp = escape(hn) if hn else "TBD"
    a_disp = escape(an) if an else "TBD"

    # Skor kutusu
    if actual and actual.get("home") is not None:
        score_html = f'<div class="result">{actual["home"]} – {actual["away"]}</div>'
    elif pred and hn:
        ps = pred.get("predicted_score", {})
        score_html = f'<div class="pending-score">{ps.get("home","?")} – {ps.get("away","?")}</div>'
    else:
        score_html = '<div class="tbd-score">? – ?</div>'

    # Olasılıklar
    probs_html = ""
    if pred and hn and not actual:
        hw = int(round(pred.get("home_win", 0) * 100))
        dr = int(round(pred.get("draw", 0) * 100))
        aw = int(round(pred.get("away_win", 0) * 100))
        probs_html = (
            f'<div class="mc-probs">'
            f'<span style="color:#4ade80">1 %{hw}</span>'
            f'<span style="color:#64748b">X %{dr}</span>'
            f'<span style="color:#f87171">2 %{aw}</span>'
            f'</div>'
        )

    result_tag = ""
    if outcome == "correct":
        result_tag = '<span class="mc-result-tag correct">✓ Doğru</span>'
    elif outcome == "wrong":
        result_tag = '<span class="mc-result-tag wrong">✗ Yanlış</span>'

    tbd_note = "" if hn else '<div class="mc-tbd-note">Takımlar henüz belirlenmedi</div>'
    group_tag = f'<span class="mc-group">{escape(group)}</span>' if group else ""

    return (
        f'<div class="{card_cls}">'
        f'<div class="mc-meta"><span class="mc-date">{escape(date_str)} · {escape(stage)}</span>{group_tag}</div>'
        f'<div class="mc-teams">'
        f'<div class="mc-logo"><span>{_logo_img(home.get("crest",""),hn)}</span><span class="{home_cls}">{h_disp}</span></div>'
        f'<div class="mc-score">{score_html}</div>'
        f'<div class="mc-logo away"><span class="{away_cls}">{a_disp}</span><span>{_logo_img(away.get("crest",""),an)}</span></div>'
        f'</div>'
        f'{probs_html}'
        f'{tbd_note}'
        f'{result_tag}'
        f'</div>'
    )


def _build_preseason_content() -> str:
    """Fixture verisi gelmeden önce gösterilecek bilgilendirici ön-sezon içeriği."""
    timeline = [
        ("Haz 24 – Tem 1", "UCL 1. Nitelendirme Turu", "#f59e0b", "🏆"),
        ("Tem 8 – Tem 15", "UCL 2. Nitelendirme Turu", "#f59e0b", "🏆"),
        ("Tem 22 – Tem 29", "UCL 3. Nitelendirme Turu · UEL 2. Tur başlangıcı", "#f59e0b", "🏆🟠"),
        ("Ağu 5 – Ağu 12", "UCL Play-off · UEL Play-off · UECL Play-off", "#e0a020", "⚔️"),
        ("Eyl 17, 2026", "UCL / UEL / UECL Lig Fazı Başlangıcı", "#4ade80", "🚀"),
        ("Oca 2027", "Lig Fazı Son Haftaları", "#60a5fa", "📊"),
        ("Şub – Mar 2027", "Eleme (Play-off + Son 16)", "#a78bfa", "🏅"),
        ("May 31, 2027", "UCL Finali — Münih", "#f59e0b", "🏆"),
    ]
    rows = "".join(
        f"""<div style="display:flex;gap:14px;align-items:flex-start;padding:12px 0;border-bottom:1px solid #1e3a5f">
          <div style="min-width:120px;font-size:11px;color:var(--muted);padding-top:2px">{date}</div>
          <div style="font-size:12px;font-weight:600;color:var(--ink)">{emoji} {label}</div>
        </div>"""
        for date, label, color, emoji in timeline
    )

    return f"""
<div style="max-width:800px;margin:0 auto;padding:20px 0">
  <div style="background:rgba(245,158,11,.06);border:1px solid rgba(245,158,11,.2);border-radius:12px;padding:20px 24px;margin-bottom:24px">
    <div style="font-size:11px;font-weight:700;color:#f59e0b;letter-spacing:1.2px;text-transform:uppercase;margin-bottom:4px">⏳ Fixture verisi bekleniyor</div>
    <div style="font-size:14px;color:var(--ink);line-height:1.6">
      UEFA nitelendirme turları oynanıyor; football-data.org ücretsiz planı bu turların fikstürünü
      kapsamıyor. Aşağıdaki <strong>haber nabzı</strong> gerçek kaynaklardan derlenen güncel durumu gösterir —
      lig fazı fikstürü API'den geldiğinde bu sayfa otomatik dolacak.
    </div>
  </div>

  <div>
    <div style="font-size:11px;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:1px;margin-bottom:14px">📅 2026-27 UEFA Takvimi (genel, yaklaşık)</div>
    {rows}
  </div>
</div>"""


def _load_pulse() -> list[dict]:
    if not PULSE_PATH.exists():
        return []
    try:
        payload = json.loads(PULSE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    return payload.get("items", [])


def _build_pulse_section(items: list[dict]) -> str:
    """football-data.org nitelendirme fikstürü sağlamadığında/eksik kaldığında haber
    kaynaklarından derlenen gerçek, kaynaklı Avrupa kupası sinyalini gösterir."""
    if not items:
        return ""
    rows = []
    for item in items[:12]:
        title = escape(item.get("title", ""))
        link = escape(item.get("link", "") or "#")
        source = escape(item.get("source", ""))
        dt = _parse_utc(item.get("published_at", ""))
        date_str = _fmt_date(dt) if dt else ""
        comp = item.get("competition")
        comp_html = (
            f'<span class="pulse-comp-tag" style="color:{_COMP_COLOR.get(comp,"#60a5fa")}">'
            f'{_COMP_EMOJI.get(comp,"")} {escape(comp)}</span>'
        ) if comp else ""
        club_tags = "".join(
            f'<span class="pulse-club-tag">{escape(c)}</span>' for c in item.get("clubs", [])
        )
        rows.append(
            f'<a class="pulse-item" href="{link}" target="_blank" rel="noopener">'
            f'<div class="pulse-title">{title}</div>'
            f'<div class="pulse-meta"><span>{source}</span><span>{escape(date_str)}</span>{comp_html}{club_tags}</div>'
            f'</a>'
        )
    return (
        '<div class="pulse-wrap">'
        '<div class="pulse-lbl"><span class="today-dot"></span>⚽ Avrupa Kupası Haber Nabzı</div>'
        '<div class="pulse-note">UEFA nitelendirme/eleme turu haberleri — gerçek kaynaklardan, günde birkaç kez güncellenir.</div>'
        f'<div class="pulse-list">{"".join(rows)}</div>'
        '</div>'
    )


def _load_known_fixtures() -> list[dict]:
    if not KNOWN_FIXTURES_PATH.exists():
        return []
    try:
        payload = json.loads(KNOWN_FIXTURES_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    return payload.get("fixtures", [])


def _relative_day_label(dt: datetime, now: datetime) -> str:
    delta = (dt.date() - now.date()).days
    if delta == 0:
        return "Bugün"
    if delta == 1:
        return "Yarın"
    if 2 <= delta <= 6:
        return _TR_WEEKDAYS[dt.weekday()]
    return f"{dt.day} {_TR_MONTHS[dt.month]}"


def _known_fixture_card(fx: dict, comp_color: str, now: datetime) -> str:
    dt = _parse_utc(fx.get("kickoff_local", ""))
    day_label = _relative_day_label(dt, now) if dt else "?"
    time_confirmed = fx.get("kickoff_time_confirmed", True)
    time_str = dt.strftime("%H:%M") if (dt and time_confirmed) else "saat teyit edilmedi"
    stage = _STAGE_TR.get(fx.get("stage", ""), fx.get("stage", ""))
    venue = escape(fx.get("venue", "") or "")
    referee = fx.get("referee")
    referee_html = f'<div class="mc-tbd-note">Hakem: {escape(referee)}</div>' if referee else ""
    next_round = fx.get("next_round_if_advance")
    next_html = f'<div class="mc-tbd-note">Turu geçerse: {escape(next_round)}</div>' if next_round else ""
    away_label = fx.get("away_team", "")
    away_country = fx.get("away_team_country")
    if away_country:
        away_label = f'{away_label} ({away_country})'
    return (
        f'<div class="match-card mc-pending">'
        f'<div class="mc-meta"><span class="mc-date">{escape(day_label)} · {escape(time_str)} · {escape(stage)}</span></div>'
        f'<div class="mc-teams">'
        f'<div class="mc-team">{escape(fx.get("home_team",""))}</div>'
        f'<div class="mc-score"><div class="tbd-score">vs</div></div>'
        f'<div class="mc-team away">{escape(away_label)}</div>'
        f'</div>'
        f'<div class="mc-tbd-note">{venue}</div>'
        f'{referee_html}'
        f'{next_html}'
        f'</div>'
    )


def _load_european_results() -> list[dict]:
    """Oynanmış Türk kulübü Avrupa eleme/playoff maçlarının gerçek skorları."""
    path = DATA_DIR / "manual" / "european_results_2026_2027.json"
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    return payload.get("results", [])


def _result_card(r: dict, comp_color: str) -> str:
    """Oynanmış maç kartı — gerçek skorla."""
    date_str = r.get("date", "")
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        date_lbl = f"{dt.day} {_TR_MONTHS[dt.month]}"
    except (ValueError, IndexError):
        date_lbl = date_str
    stage = _STAGE_TR.get(r.get("stage", ""), r.get("stage", ""))
    leg = r.get("leg")
    leg_lbl = f" · {leg}. maç" if leg else ""
    hs, as_ = r.get("home_score"), r.get("away_score")
    home, away = r.get("home_team", ""), r.get("away_team", "")
    # Kazananı vurgula
    home_w = isinstance(hs, int) and isinstance(as_, int) and hs > as_
    away_w = isinstance(hs, int) and isinstance(as_, int) and as_ > hs
    home_style = ' style="font-weight:800"' if home_w else ""
    away_style = ' style="font-weight:800"' if away_w else ""
    return (
        f'<div class="match-card">'
        f'<div class="mc-meta"><span class="mc-date">{escape(date_lbl)} · {escape(stage)}{escape(leg_lbl)}</span></div>'
        f'<div class="mc-teams">'
        f'<div class="mc-team"{home_style}>{escape(home)}</div>'
        f'<div class="mc-score"><div class="tbd-score" style="color:#e2e8f0;font-weight:800">{hs}-{as_}</div></div>'
        f'<div class="mc-team away"{away_style}>{escape(away)}</div>'
        f'</div>'
        f'</div>'
    )


def _build_known_fixtures_section(fixtures: list[dict]) -> str:
    """İki alt bölüm üretir: (1) Yaklaşan Maçlar — haber kaynaklı doğrulanmış gerçek
    fikstür (tarih/saat/mekan; skor/olasılık tahmini ÜRETİLMEZ, rakip stat tabanı yok);
    (2) Tamamlanan Maçlar — oynanmış maçların GERÇEK skorları (european_results)."""
    now = datetime.now(_TZ_TR)
    # Yaklaşan: yalnız bugün/gelecek fikstürler (oynanmışları eleme dışı bırak).
    upcoming = [
        fx for fx in fixtures
        if (_parse_utc(fx.get("kickoff_local", "")) or now).date() >= now.date()
    ]
    upcoming.sort(key=lambda f: f.get("kickoff_local", ""))
    results = sorted(_load_european_results(), key=lambda r: r.get("date", ""), reverse=True)

    blocks = []
    if upcoming:
        cards = "\n".join(
            _known_fixture_card(fx, _COMP_COLOR.get(fx.get("competition", ""), "#60a5fa"), now)
            for fx in upcoming
        )
        blocks.append(
            '<div class="today-wrap">'
            '<div class="today-lbl"><span class="today-dot"></span>🔜 Yaklaşan Maçlar (haber kaynaklı)</div>'
            '<div class="mc-tbd-note" style="margin-bottom:12px">football-data.org eleme/playoff turu fikstürünü kapsamıyor. '
            'Maç bilgisi (tarih/saat/mekan) Türk basınından doğrulanmıştır — rakipler hakkında istatistiksel veri '
            'olmadığı için skor/olasılık tahmini üretilmemiştir.</div>'
            f'<div class="today-grid">{cards}</div>'
            '</div>'
        )
    if results:
        rcards = "\n".join(
            _result_card(r, _COMP_COLOR.get(r.get("competition", ""), "#60a5fa"))
            for r in results
        )
        blocks.append(
            '<div class="today-wrap">'
            '<div class="today-lbl"><span class="today-dot" style="background:#4ade80"></span>✅ Tamamlanan Maçlar (gerçek skor)</div>'
            f'<div class="today-grid">{rcards}</div>'
            '</div>'
        )
    return "\n".join(blocks)


def _build_today_section(all_comps: dict) -> str:
    today_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    today_matches = []
    for code, comp in all_comps.items():
        for m in comp.get("predictions", []):
            if (m.get("utc_date", "")[:10] == today_utc
                    and m.get("prediction_outcome") == "pending"
                    and m.get("home", {}).get("name")):
                today_matches.append((code, m))
    if not today_matches:
        return ""
    cards = "\n".join(
        _match_card(m, _COMP_COLOR.get(code, "#60a5fa"))
        for code, m in sorted(today_matches, key=lambda x: x[1].get("utc_date", ""))
    )
    count = len(today_matches)
    return (
        f'<div class="today-wrap">'
        f'<div class="today-lbl"><span class="today-dot"></span>Bugün {count} Maç</div>'
        f'<div class="today-grid">{cards}</div>'
        f'</div>'
    )


def _build_comp_section(code: str, comp: dict) -> str:
    color = _COMP_COLOR.get(code, "#60a5fa")
    predictions = comp.get("predictions", [])

    # Aşamaya göre grupla
    by_stage: dict[str, list] = {}
    stage_order = [
        "PRELIMINARY_ROUND",
        "1ST_QUALIFYING_ROUND", "2ND_QUALIFYING_ROUND",
        "3RD_QUALIFYING_ROUND", "4TH_QUALIFYING_ROUND",
        "QUALIFYING", "QUALIFYING_ROUNDS", "PLAY_OFF_ROUND",
        "LEAGUE_PHASE", "LEAGUE_STAGE", "GROUP_STAGE",
        "LAST_32", "LAST_16", "QUARTER_FINALS",
        "SEMI_FINALS", "THIRD_PLACE", "FINAL",
    ]
    for m in predictions:
        s = m.get("stage", "OTHER")
        by_stage.setdefault(s, []).append(m)

    # Tarih içinde sırala
    for s in by_stage:
        by_stage[s].sort(key=lambda m: m.get("utc_date", ""))

    # Aşama sırasına göre çıkar
    ordered_stages = [s for s in stage_order if s in by_stage]
    for s in by_stage:
        if s not in ordered_stages:
            ordered_stages.append(s)

    parts = []
    for stage_key in ordered_stages:
        matches = by_stage[stage_key]
        label = _STAGE_TR.get(stage_key, stage_key)
        cards = "\n".join(_match_card(m, color) for m in matches)
        parts.append(
            f'<div class="stage-header" style="color:{color}">{escape(label)}</div>'
            f'<div class="match-grid">{cards}</div>'
        )

    inner = "\n".join(parts)
    return (
        f'<div class="comp-section" data-comp="{escape(code)}">'
        f'{inner}'
        f'</div>'
    )


def build_page(data: dict) -> str:
    comps = data.get("competitions", {})
    gen_at = data.get("generated_at", "")
    try:
        gen_str = datetime.fromisoformat(gen_at.replace("Z", "+00:00")).astimezone(_TZ_TR).strftime("%d.%m.%Y %H:%M")
    except Exception:
        gen_str = gen_at[:10]

    # Özet istatistikler
    total_played = total_correct = total_wrong = total_matches = 0
    for comp in comps.values():
        acc = comp.get("accuracy", {})
        total_played += acc.get("finished", 0)
        total_correct += acc.get("correct", 0)
        total_wrong += acc.get("wrong", 0)
        total_matches += len(comp.get("predictions", []))

    acc_pct = round(total_correct / total_played * 100, 1) if total_played else 0

    nav_items = nav_links_html("european_predictions_2026_2027.html")

    # Hero badges
    badges = "".join(
        f'<span class="hero-badge" style="background:rgba({{"CL":"245,158,11","EL":"249,115,22","ECL":"34,197,94"}}.get("{code}","96,165,250"),.15);color:{_COMP_COLOR.get(code,"#60a5fa")};border:1px solid {_COMP_COLOR.get(code,"#60a5fa")}40">'
        f'{_COMP_EMOJI.get(code,"")} {escape(comp["name"])}</span>'
        for code, comp in comps.items()
    )

    # Stat bar: football-data.org eleme/playoff turunu kapsamadığı için otomatik tahmin
    # (predictions) boş kalıyor. Bu durumda tahmin doğruluk çubuğu yerine haber-kaynaklı
    # bilinen maç sayımlarını göster (yaklaşan + tamamlanan) — "0 Toplam Maç" yanıltmasın.
    _now = datetime.now(_TZ_TR)
    _known = _load_known_fixtures()
    _upcoming_n = sum(
        1 for fx in _known
        if (_parse_utc(fx.get("kickoff_local", "")) or _now).date() >= _now.date()
    )
    _results = _load_european_results()
    if total_matches:
        stat_bar = (
            f'<div class="stat-chip"><div class="v">{total_matches}</div><div class="l">Toplam Maç</div></div>'
            f'<div class="stat-chip"><div class="v">{total_played}</div><div class="l">Oynandı</div></div>'
            f'<div class="stat-chip"><div class="v" style="color:#4ade80">{total_correct}</div><div class="l">Doğru</div></div>'
            f'<div class="stat-chip"><div class="v" style="color:#f87171">{total_wrong}</div><div class="l">Yanlış</div></div>'
            f'<div class="stat-chip"><div class="v" style="color:#f59e0b">%{acc_pct}</div><div class="l">Doğruluk</div></div>'
        )
    else:
        stat_bar = (
            f'<div class="stat-chip"><div class="v" style="color:#f59e0b">{_upcoming_n}</div><div class="l">Yaklaşan Maç</div></div>'
            f'<div class="stat-chip"><div class="v" style="color:#4ade80">{len(_results)}</div><div class="l">Oynanan Maç</div></div>'
            f'<div class="stat-chip"><div class="v">3</div><div class="l">Türk Kulübü (CL/EL)</div></div>'
        )

    # Comp tabs
    all_btn = '<button class="comp-tab" data-comp="ALL" onclick="showComp(\'ALL\')">🌍 Tümü</button>'
    comp_btns = "".join(
        f'<button class="comp-tab" data-comp="{escape(code)}" onclick="showComp(\'{escape(code)}\')">'
        f'{_COMP_EMOJI.get(code,"")} {escape(comp["short"])}</button>'
        for code, comp in comps.items()
    )

    # Sections
    known_fixtures_html = _build_known_fixtures_section(_load_known_fixtures())
    today_html = _build_today_section(comps)
    pulse_html = _build_pulse_section(_load_pulse())
    if comps:
        sections_html = "\n".join(_build_comp_section(code, comp) for code, comp in comps.items())
    else:
        sections_html = _build_preseason_content()

    return f"""<!doctype html>
<html lang="tr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>UEFA Şampiyonlar Ligi & Avrupa Ligi 2026-27 Tahminleri | metric11</title>
  <meta name="description" content="UEFA Şampiyonlar Ligi, Avrupa Ligi ve Konferans Ligi 2026-27 maç tahminleri — Fenerbahçe, Galatasaray, Beşiktaş takibi. Günlük güncellenen analiz platformu.">
  <meta property="og:title" content="Avrupa Kupası Tahminleri 2026-27 | metric11">
  <meta property="og:description" content="UCL, UEL, UECL 2026-27 maç tahminleri ve Türk kulüp takibi.">
  <meta property="og:image" content="https://metric11.com/og_european.png">
  <meta name="twitter:image" content="https://metric11.com/og_european.png">
  <meta property="og:type" content="website">
  <meta property="og:url" content="https://metric11.com/european_predictions_2026_2027.html">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="canonical" href="https://metric11.com/european_predictions_2026_2027.html">
  <link rel="icon" href="favicon.svg" type="image/svg+xml">
  <script type="application/ld+json">{{
    "@context": "https://schema.org",
    "@type": "WebPage",
    "name": "UEFA Avrupa Kupası Tahminleri 2026-27",
    "description": "UCL, UEL, UECL 2026-27 maç tahminleri — Fenerbahçe, Galatasaray, Beşiktaş.",
    "url": "https://metric11.com/european_predictions_2026_2027.html",
    "publisher": {{"@type": "Organization", "name": "metric11", "url": "https://metric11.com"}}
  }}</script>
  <style>{_CSS}</style>
</head>
<body>
  <div class="topbar">
    <a class="brand" href="/"><b>11</b> metric11 <span class="brand-lbl">Avrupa 2026-27</span></a>
    <nav>{nav_items}</nav>
  </div>

  <div class="hero">
    <h1>⚽ Avrupa Kupası Maç Tahminleri <span style="color:var(--cl)">2026-27</span></h1>
    <p>Şampiyonlar Ligi · Avrupa Ligi · Konferans Ligi · Türk kulüp takibi · Son güncelleme: {escape(gen_str)}</p>
    <div class="hero-badges">{badges}</div>
  </div>

  <div class="stat-bar">{stat_bar}</div>

  <div class="comp-tabs">
    {all_btn}
    {comp_btns}
  </div>

  <div class="main">
    <div style="margin-bottom:16px">{telegram_cta_html()}</div>
    {known_fixtures_html}
    {today_html}
    {pulse_html}
    {sections_html}
  </div>

  <footer>metric11 &middot; <a href="/">metric11.com</a> &middot; {escape(gen_str)}</footer>
  {_JS}
  <script defer src="/_vercel/insights/script.js"></script>
</body>
</html>"""


def main() -> None:
    ensure_data_dirs()

    if not INPUT_PATH.exists():
        print(f"HATA: {INPUT_PATH} bulunamadı. Önce analyze_european_predictions çalıştırın.")
        sys.exit(1)

    data = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    html = build_page(data)
    OUTPUT_PATH.write_text(html, encoding="utf-8")
    print(f"HTML kaydedildi: {OUTPUT_PATH}")
    print(f"Boyut: {len(html):,} karakter")


if __name__ == "__main__":
    main()
