"""2026-27 Süper Lig fikstürü için gerçek maç tahminleri üretir.

`src/collect_tff_season_fixture.py` ile toplanan resmi TFF fikstürünü (34 hafta, 306 maç)
`model_league_predictions.py`'deki aynı Poisson/Elo/h2h/transfer motoruyla tahmine çevirir.
Motor, 2025-26 sezonunun tamamı + `src/advance_season_state.py`'nin biriktirdiği 2026-27'de
ŞİMDİYE KADAR OYNANMIŞ maçlardan hesaplanan "başlangıç durumu"nu kullanır — sezon ilerledikçe
bu durum otomatik ilerler, statik kalmaz. Oynanmış haftalar gerçek skorla, kalan haftalar
güncel state ile yeniden tahmin edilerek gösterilir.
"""
from __future__ import annotations

import json
from datetime import datetime
from html import escape
from pathlib import Path

from src.config import PROCESSED_DIR, SEASON
from src.model_league_predictions import (
    compute_final_state,
    confidence_label,
    draw_calibrated_prediction,
    parse_tff_datetime,
    predict_match,
)
from src.normalization import normalize_matches

FIXTURE_PATH = PROCESSED_DIR / "tff_super_lig_fixtures_2026_2027.json"
HISTORY_INPUT_PATH = PROCESSED_DIR / f"tff_super_lig_enriched_{SEASON}.json"
PLAYED_2026_2027_PATH = PROCESSED_DIR / "tff_super_lig_matches_2026_2027.json"
OUTPUT_JSON = PROCESSED_DIR / "season_fixture_predictions_2026_2027.json"
OUTPUT_MD = PROCESSED_DIR / "season_fixture_predictions_2026_2027.md"
OUTPUT_HTML = PROCESSED_DIR / "season_fixture_predictions_2026_2027.html"

# 2025-26 -> 2026-27 sponsor/isim değişiklikleri (aynı kulüp, farklı resmi ad).
NAME_ALIASES: dict[str, str] = {
    "İSTANBUL BAŞAKŞEHİR FK": "RAMS BAŞAKŞEHİR FUTBOL KULÜBÜ",
    "KONYASPOR": "TÜMOSAN KONYASPOR",
    "EYÜPSPOR": "İKAS EYÜPSPOR",
}
# 2025-26'da Süper Lig'de olmayan, 2026-27'de yeni çıkan takımlar (1. Lig'den yükseldi).
NEW_TEAMS = {"ÇORUM FK", "ERZURUMSPOR FK", "AMED SPORTİF FAALİYETLER"}

_TR_MONTHS = ["", "Oca", "Şub", "Mar", "Nis", "May", "Haz", "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara"]


def _history_key(fixture_team_name: str) -> str:
    return NAME_ALIASES.get(fixture_team_name, fixture_team_name)


def _rekeyed_2026_27_matches() -> list[dict]:
    """2026-27'de oynanan maçları (varsa) 2025-26 ile aynı takım-adı uzayına taşır.

    `advance_season_state.py`'nin TFF'den çektiği zengin maç kayıtları, kulüplerin
    GÜNCEL (2026-27) resmi adlarını kullanır. `compute_final_state` bir takımın
    formunu/Elo'sunu isim anahtarıyla biriktirdiği için, sponsor adı değişen
    kulüplerin (`NAME_ALIASES`) 2026-27 maçları da 2025-26 ile aynı anahtara
    (`_history_key`) taşınmadan birleştirilirse form/Elo devamlılığı bozulur.
    """
    if not PLAYED_2026_2027_PATH.exists():
        return []
    raw_matches = normalize_matches(
        json.loads(PLAYED_2026_2027_PATH.read_text(encoding="utf-8"))
    )
    rekeyed = []
    for match in raw_matches:
        match = dict(match)
        home_team = dict(match["home_team"])
        away_team = dict(match["away_team"])
        home_team["name"] = _history_key(home_team["name"])
        away_team["name"] = _history_key(away_team["name"])
        match["home_team"] = home_team
        match["away_team"] = away_team
        rekeyed.append(match)
    return rekeyed


def build_predictions() -> dict:
    fixture_payload = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    history_matches = normalize_matches(
        json.loads(HISTORY_INPUT_PATH.read_text(encoding="utf-8"))
    )
    played_2026_27 = _rekeyed_2026_27_matches()
    all_matches = history_matches + played_2026_27
    all_matches.sort(key=lambda m: parse_tff_datetime(m["match_date"]))
    state = compute_final_state(all_matches)
    team_history, elo = state["team_history"], state["elo"]

    weeks_out = []
    new_team_matches = 0
    played_matches = 0
    for week in fixture_payload["weeks"]:
        week_matches = []
        for m in week["matches"]:
            home_name, away_name = m["home_team"], m["away_team"]
            home_key, away_key = _history_key(home_name), _history_key(away_name)
            home_hist = list(team_history.get(home_key, []))
            away_hist = list(team_history.get(away_key, []))
            is_new = home_name in NEW_TEAMS or away_name in NEW_TEAMS
            if is_new:
                new_team_matches += 1
            try:
                match_dt = parse_tff_datetime(m["date_time"])
            except ValueError:
                match_dt = None
            prediction = predict_match(
                home_name, away_name, home_hist, away_hist,
                elo.get(home_key, 1500.0), elo.get(away_key, 1500.0),
                ref_stats=None,
                apply_transfer_signal=True,
                apply_fixture_congestion=True,
                apply_european_signal=True,
                match_date=match_dt,
            )
            probs = {
                "home": prediction["home_win_probability"],
                "draw": prediction["draw_probability"],
                "away": prediction["away_win_probability"],
            }
            raw_predicted = max(probs, key=probs.__getitem__)
            predicted = draw_calibrated_prediction(
                probs["home"], probs["draw"], probs["away"], prediction.get("strength_edge", 0.0)
            )
            score_text = (m.get("score") or "").strip()
            is_played = bool(score_text) and score_text != "-"
            if is_played:
                played_matches += 1
            week_matches.append({
                "match_id": m["match_id"],
                "date_time": m["date_time"],
                "home_team": home_name,
                "away_team": away_name,
                "is_played": is_played,
                "actual_score": score_text if is_played else None,
                "data_confidence": "PLAYED" if is_played else ("LOW_NEW_TEAM" if is_new else confidence_label(prediction)),
                "raw_predicted": raw_predicted,
                "predicted": predicted,
                **prediction,
            })
        weeks_out.append({"week": week["week"], "matches": week_matches})

    return {
        "generated_at": datetime.now().isoformat(),
        "season": "2026-2027",
        "source_note": (
            "Tahminler 2025-26 sezonunun tamamı ve 2026-27'de şimdiye kadar oynanmış "
            f"({played_matches} maç) sonuçlardan türetilen güncel takım formu/Elo/transfer "
            "durumuna dayanır; sezon ilerledikçe bu sayfa her gün otomatik olarak yeniden "
            "hesaplanır, statik bir anlık görüntü değildir."
        ),
        "total_weeks": len(weeks_out),
        "total_matches": sum(len(w["matches"]) for w in weeks_out),
        "played_matches": played_matches,
        "new_team_matches": new_team_matches,
        "new_teams": sorted(NEW_TEAMS),
        "weeks": weeks_out,
    }


def build_markdown(payload: dict) -> str:
    lines = [
        "# 2026-27 Süper Lig Fikstürü ve Tahminleri",
        "",
        f"Üretim zamanı: {payload['generated_at']}",
        f"Toplam hafta: {payload['total_weeks']}, toplam maç: {payload['total_matches']}",
        f"Not: {payload['source_note']}",
        f"Yeni takımlar (sınırlı veri): {', '.join(payload['new_teams'])}",
        "",
    ]
    labels = {"home": "Ev", "draw": "X", "away": "Dep"}
    for week in payload["weeks"][:3]:
        lines.append(f"## Hafta {week['week']}")
        lines.append("")
        for m in week["matches"]:
            if m["is_played"]:
                lines.append(f"- {m['date_time']} | {m['home_team']} {m['actual_score']} {m['away_team']} | OYNANDI")
                continue
            lines.append(
                f"- {m['date_time']} | {m['home_team']} - {m['away_team']} | "
                f"tahmin={labels[m['predicted']]} (Ev %{round(m['home_win_probability']*100)} · "
                f"X %{round(m['draw_probability']*100)} · Dep %{round(m['away_win_probability']*100)}) | "
                f"güven={m['data_confidence']}"
            )
        lines.append("")
    return "\n".join(lines) + "\n"


def _fmt_date(date_str: str) -> str:
    try:
        dt = datetime.strptime(date_str.split(" ")[0], "%d.%m.%Y")
        return f"{dt.day} {_TR_MONTHS[dt.month]} {dt.year}"
    except (ValueError, IndexError):
        return date_str


_NAV_LINKS = [
    ("Gündem", "/"),
    ("Transferler", "transfer_tracker_2025_2026.html"),
    ("Maç Önü", "all_teams_preview_dashboard_2025_2026.html"),
    ("2026-27 Fikstür", "season_fixture_predictions_2026_2027.html"),
    ("Scout", "transfer_recommendation_report_2025_2026.html"),
    ("Avrupa", "european_predictions_2026_2027.html"),
]

_CSS = """
:root { --bg:#09111f; --panel:#0e1929; --panel2:#13223a; --ink:#e2e8f0; --muted:#64748b; --border:#1e3a5f; --lime:#cde94e; }
* { box-sizing:border-box; margin:0; padding:0; }
body { font-family:Inter,"Segoe UI",Arial,sans-serif; background:var(--bg); color:var(--ink); min-height:100vh; }
.topbar { background:#060e1d; border-bottom:2px solid #1a3023; min-height:54px; padding:0 clamp(12px,3vw,32px); display:flex; align-items:center; justify-content:space-between; gap:16px; }
.brand { display:flex; align-items:center; gap:9px; color:white; text-decoration:none; font-size:17px; font-weight:800; }
.brand b { width:26px; height:26px; border-radius:5px; display:grid; place-items:center; background:var(--lime); color:#060e1d; font-size:13px; font-weight:900; }
nav { display:flex; gap:2px; overflow-x:auto; scrollbar-width:none; }
nav a { white-space:nowrap; color:#64748b; padding:7px 10px; border-radius:6px; text-decoration:none; font-size:12px; font-weight:600; }
nav a:hover, nav a.active { background:#0f2030; color:white; }
.hero { background:linear-gradient(160deg,#0a1929 0%,#060e1d 100%); padding:28px clamp(12px,3vw,32px) 22px; border-bottom:1px solid var(--border); }
.hero h1 { font-size:clamp(20px,4vw,28px); font-weight:800; color:white; margin-bottom:6px; }
.hero p { font-size:13px; color:var(--muted); max-width:760px; line-height:1.6; }
.stat-bar { display:flex; gap:10px; padding:16px clamp(12px,3vw,32px); flex-wrap:wrap; max-width:1200px; margin:0 auto; }
.stat-chip { background:var(--panel); border:1px solid var(--border); border-radius:8px; padding:10px 16px; text-align:center; min-width:110px; }
.stat-chip .v { font-size:20px; font-weight:800; }
.stat-chip .l { font-size:10px; color:var(--muted); text-transform:uppercase; letter-spacing:.5px; margin-top:3px; }
.main { max-width:1200px; margin:0 auto; padding:10px clamp(12px,3vw,32px) 60px; }
.week-header { font-size:12px; font-weight:700; color:var(--lime); text-transform:uppercase; letter-spacing:1px; margin:24px 0 10px; display:flex; align-items:center; gap:8px; }
.week-header::after { content:''; flex:1; height:1px; background:var(--border); }
.match-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(270px,1fr)); gap:10px; }
.match-card { background:var(--panel); border:1px solid var(--border); border-radius:10px; padding:12px 14px; display:flex; flex-direction:column; gap:7px; }
.mc-date { font-size:10px; color:var(--muted); }
.mc-teams { display:flex; justify-content:space-between; align-items:center; font-size:13px; font-weight:700; color:white; gap:6px; }
.mc-teams .vs { font-size:10px; color:var(--muted); font-weight:600; }
.mc-pick { font-size:12px; font-weight:700; padding:3px 9px; border-radius:5px; align-self:flex-start; }
.mc-pick.home { background:rgba(74,222,128,.12); color:#4ade80; }
.mc-pick.draw { background:rgba(148,163,184,.14); color:#94a3b8; }
.mc-pick.away { background:rgba(248,113,113,.1); color:#f87171; }
.mc-probs { display:flex; gap:8px; font-size:11px; color:var(--muted); }
.mc-conf { font-size:10px; color:#475569; }
footer { text-align:center; padding:32px 16px 24px; color:#1e3a5f; font-size:11px; border-top:1px solid var(--border); margin-top:32px; }
footer a { color:#1e3a5f; }
"""


def _match_card(m: dict) -> str:
    if m.get("is_played"):
        return f"""<div class="match-card">
  <div class="mc-date">{escape(_fmt_date(m['date_time']))}</div>
  <div class="mc-teams"><span>{escape(m['home_team'])}</span><span class="vs">{escape(m['actual_score'])}</span><span>{escape(m['away_team'])}</span></div>
  <div class="mc-pick draw" style="background:rgba(148,163,184,.14);color:#94a3b8">OYNANDI</div>
</div>"""
    labels = {"home": "Ev Sahibi", "draw": "Beraberlik", "away": "Deplasman"}
    pick = m["predicted"]
    pick_text = labels[pick] if pick != "home" and pick != "away" else (m["home_team"] if pick == "home" else m["away_team"])
    if pick == "draw":
        pick_text = "Beraberlik"
    return f"""<div class="match-card">
  <div class="mc-date">{escape(_fmt_date(m['date_time']))}</div>
  <div class="mc-teams"><span>{escape(m['home_team'])}</span><span class="vs">vs</span><span>{escape(m['away_team'])}</span></div>
  <div class="mc-pick {pick}">{escape(pick_text)}</div>
  <div class="mc-probs"><span style="color:#4ade80">Ev %{round(m['home_win_probability']*100)}</span><span>X %{round(m['draw_probability']*100)}</span><span style="color:#f87171">Dep %{round(m['away_win_probability']*100)}</span></div>
  <div class="mc-conf">Güven: {escape(m['data_confidence'])}</div>
</div>"""


def build_html(payload: dict) -> str:
    nav_items = "".join(
        f'<a href="{escape(href)}" class="active">{escape(label)}</a>' if label == "2026-27 Fikstür"
        else f'<a href="{escape(href)}">{escape(label)}</a>'
        for label, href in _NAV_LINKS
    )
    stat_bar = (
        f'<div class="stat-chip"><div class="v">{payload["total_matches"]}</div><div class="l">Toplam Maç</div></div>'
        f'<div class="stat-chip"><div class="v">{payload["total_weeks"]}</div><div class="l">Hafta</div></div>'
        f'<div class="stat-chip"><div class="v">3</div><div class="l">Yeni Takım</div></div>'
    )
    weeks_html = "\n".join(
        f'<div class="week-header">Hafta {week["week"]}</div>'
        f'<div class="match-grid">{"".join(_match_card(m) for m in week["matches"])}</div>'
        for week in payload["weeks"]
    )
    return f"""<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>2026-27 Süper Lig Fikstürü ve Tahminleri | metric11</title>
<meta name="description" content="Trendyol Süper Lig 2026-27 sezonu resmi fikstürü ve 34 haftalık 306 maç için tahminler.">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<style>{_CSS}</style>
</head>
<body>
<div class="topbar">
  <a class="brand" href="/"><b>11</b> metric11</a>
  <nav>{nav_items}</nav>
</div>
<div class="hero">
  <h1>🗓️ 2026-27 Süper Lig Fikstürü <span style="color:var(--lime)">ve Tahminleri</span></h1>
  <p>{escape(payload['source_note'])}</p>
</div>
<div class="stat-bar">{stat_bar}</div>
<div class="main">{weeks_html}</div>
<footer>metric11 &middot; <a href="/">metric11.com</a></footer>
<script defer src="/_vercel/insights/script.js"></script>
</body>
</html>"""


def main() -> None:
    if not FIXTURE_PATH.exists():
        print(f"HATA: {FIXTURE_PATH} bulunamadı. Önce collect_tff_season_fixture çalıştırın.")
        return
    payload = build_predictions()
    OUTPUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    OUTPUT_MD.write_text(build_markdown(payload), encoding="utf-8")
    OUTPUT_HTML.write_text(build_html(payload), encoding="utf-8")
    print(f"Kaydedildi: {payload['total_weeks']} hafta, {payload['total_matches']} maç")


if __name__ == "__main__":
    main()
