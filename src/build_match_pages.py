"""2026-27 Süper Lig için maç başına ve hafta başına kalıcı tahmin sayfaları üretir (SEO).

Fikstür sayfası tek büyük bir sayfa; arama motorundan gelen "X - Y maç tahmini" ve
"Süper Lig N. hafta tahminleri" aramalarına karşılık gelen ayrı, kalıcı URL yoktu
(PROJECT_STATE 2026-10-17). Bu script `season_fixture_predictions_2026_2027.json`
(+ gol/kart sinyalleri, golcü tahminleri) üzerinden:

- her maç için `mac-tahmini-<ev>-<dep>-2026-27.html` (ev/dep sırası sezonda tekildir),
- her hafta için `super-lig-<n>-hafta-tahminleri-2026-27.html`

üretir. Oynanmış maçlarda dondurulmuş (pre-kickoff) tahmin + gerçek skor + isabet gösterilir.
Sayfalar düz kökte durur: page_html ve nav göreli link kullanıyor.
"""
from __future__ import annotations

import json
from datetime import datetime
from html import escape

from src.build_dashboard import TEAM_DISPLAY_NAMES
from src.build_season_fixture_predictions import OUTPUT_JSON as FIXTURE_PREDICTIONS_JSON
from src.config import PROCESSED_DIR
from src.generate_preview_batch import team_slug
from src.html_utils import _share_button, page_html

SEASON_TAG = "2026-27"
BASE_URL = "https://metric11.com"
SIGNALS_PATH = PROCESSED_DIR / "match_signals_2026_2027.json"
SCORERS_PATH = PROCESSED_DIR / "goal_scorer_predictions_2026_2027.json"
INDEX_JSON = PROCESSED_DIR / "match_pages_index_2026_2027.json"

_TR_MONTHS = ["", "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz",
              "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
_TR_DAYS = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]

# Takım arşiv sayfası olan slug'lar (build_dashboard --all-teams).
_TEAM_PAGE = "{slug}_2025_2026_dashboard_chronological.html"

_STYLE = """<style>
.mp-hero{margin:8px 0 18px}.mp-hero h1{font-size:clamp(22px,4.5vw,30px);line-height:1.2;margin:0 0 6px}
.mp-meta{color:#5b6b62;font-size:14px}
.mp-card{border:1px solid #e2e8e4;border-radius:10px;padding:16px;margin:14px 0;background:#fff}
.mp-card h2{font-size:17px;margin:0 0 10px}
.mp-bars{display:flex;flex-direction:column;gap:8px}
.mp-bar{display:grid;grid-template-columns:minmax(90px,150px) 1fr 52px;gap:8px;align-items:center;font-size:14px}
.mp-track{background:#eef3f0;border-radius:6px;height:12px;overflow:hidden}
.mp-fill{background:#116447;height:100%}.mp-fill.pick{background:#7fb800}
.mp-pick{display:inline-block;background:#116447;color:#fff;border-radius:6px;padding:4px 10px;font-weight:700;font-size:14px}
.mp-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:10px}
.mp-stat{background:#f6f9f7;border-radius:8px;padding:10px}.mp-stat .v{font-size:20px;font-weight:800}.mp-stat .l{font-size:12px;color:#5b6b62}
.mp-ok{color:#116447;font-weight:700}.mp-miss{color:#b42318;font-weight:700}
.mp-list{margin:0;padding-left:18px}.mp-list li{margin:4px 0}
.mp-links a{display:inline-block;margin:4px 8px 4px 0}
.mp-week{width:100%;border-collapse:collapse;font-size:14px}.mp-week td,.mp-week th{padding:8px 6px;border-bottom:1px solid #eef3f0;text-align:left}
.mp-cta{display:block;text-align:center;background:#cde94e;color:#060e1d;font-weight:800;border-radius:8px;padding:12px;text-decoration:none;margin:14px 0}
.mp-note{font-size:12px;color:#5b6b62}
</style>"""


def display_name(team: str) -> str:
    return TEAM_DISPLAY_NAMES.get(team_slug(team), team.title())


def match_page_path(home: str, away: str) -> str:
    return f"mac-tahmini-{_url_slug(home)}-{_url_slug(away)}-{SEASON_TAG}.html"


def week_page_path(week: int) -> str:
    return f"super-lig-{week}-hafta-tahminleri-{SEASON_TAG}.html"


def _url_slug(team: str) -> str:
    return team_slug(team).replace("_", "-")


def _parse_dt(value: str) -> datetime | None:
    try:
        return datetime.strptime(value.replace(" - ", " ").strip(), "%d.%m.%Y %H:%M")
    except (ValueError, AttributeError):
        return None


def _date_text(dt: datetime | None, with_day: bool = True) -> str:
    if dt is None:
        return "Tarih belli değil"
    base = f"{dt.day} {_TR_MONTHS[dt.month]} {dt.year}"
    return f"{base} {_TR_DAYS[dt.weekday()]}, {dt:%H:%M}" if with_day else base


def _actual(score: str | None) -> str | None:
    try:
        h, a = (int(x) for x in (score or "").replace(" ", "").split("-"))
    except ValueError:
        return None
    return "home" if h > a else "away" if h < a else "draw"


def _pick_text(m: dict, pick: str) -> str:
    if pick == "home":
        return f"{display_name(m['home_team'])} kazanır"
    if pick == "away":
        return f"{display_name(m['away_team'])} kazanır"
    return "Beraberlik"


def _pct(x) -> str:
    return f"%{round(x * 100)}" if isinstance(x, (int, float)) else "—"


def _load(path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8")).get("matches", {})
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _json_ld(m: dict, dt: datetime | None, path: str, week: int) -> str:
    home, away = display_name(m["home_team"]), display_name(m["away_team"])
    event = {
        "@context": "https://schema.org",
        "@type": "SportsEvent",
        "name": f"{home} - {away}",
        "sport": "Soccer",
        "url": f"{BASE_URL}/{path}",
        "description": f"Trendyol Süper Lig {SEASON_TAG} {week}. hafta",
        "homeTeam": {"@type": "SportsTeam", "name": home},
        "awayTeam": {"@type": "SportsTeam", "name": away},
        "eventStatus": "https://schema.org/EventScheduled",
    }
    if dt is not None:
        event["startDate"] = dt.strftime("%Y-%m-%dT%H:%M:00+03:00")
    crumbs = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "metric11", "item": f"{BASE_URL}/"},
            {"@type": "ListItem", "position": 2, "name": f"{week}. Hafta Tahminleri", "item": f"{BASE_URL}/{week_page_path(week)}"},
            {"@type": "ListItem", "position": 3, "name": f"{home} - {away}", "item": f"{BASE_URL}/{path}"},
        ],
    }
    return "".join(
        f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in (event, crumbs)
    )


def _prob_bars(m: dict, pick: str) -> str:
    rows = [
        ("home", display_name(m["home_team"]), m.get("home_win_probability")),
        ("draw", "Beraberlik", m.get("draw_probability")),
        ("away", display_name(m["away_team"]), m.get("away_win_probability")),
    ]
    out = []
    for key, label, p in rows:
        width = round((p or 0) * 100)
        cls = "mp-fill pick" if key == pick else "mp-fill"
        out.append(
            f'<div class="mp-bar"><span>{escape(label)}</span>'
            f'<div class="mp-track"><div class="{cls}" style="width:{width}%"></div></div><b>{_pct(p)}</b></div>'
        )
    return f'<div class="mp-bars">{"".join(out)}</div>'


def _summary_sentence(m: dict, pick: str) -> str:
    home, away = display_name(m["home_team"]), display_name(m["away_team"])
    rec = (m.get("recommended_scoreline") or {}).get("score")
    probs = {"home": m.get("home_win_probability"), "draw": m.get("draw_probability"), "away": m.get("away_win_probability")}
    lead = {
        "home": f"metric11 modeline göre {home} - {away} maçında favori ev sahibi {home}",
        "away": f"metric11 modeline göre {home} - {away} maçında favori deplasman ekibi {away}",
        "draw": f"metric11 modeline göre {home} - {away} dengeli bir maç, öne çıkan sonuç beraberlik",
    }[pick]
    ph, pa = probs["home"] or 0, probs["away"] or 0
    if pick != "draw" and abs(ph - pa) < 0.04:
        side = home if pick == "home" else away
        lead = f"{home} - {away} çok dengeli bir maç; model {side} tarafını yalnızca küçük bir farkla önde görüyor"
    tail = f" (olasılık {_pct(probs[pick])})."
    if rec:
        tail += f" En olası skor {rec}."
    return lead + tail


def build_match_page(m: dict, week: int, signals: dict, scorers: dict, week_matches: list[dict]) -> tuple[str, str, dict]:
    home_raw, away_raw = m["home_team"], m["away_team"]
    home, away = display_name(home_raw), display_name(away_raw)
    path = match_page_path(home_raw, away_raw)
    dt = _parse_dt(m.get("date_time", ""))
    pick = m.get("predicted") or "home"
    played = bool(m.get("is_played"))
    rec = (m.get("recommended_scoreline") or {}).get("score")
    title = f"{home} - {away} Maç Tahmini ve Skor Tahmini ({_date_text(dt, with_day=False)})"
    if played:
        description = (
            f"{home} {m.get('actual_score')} {away} — Süper Lig {week}. hafta. Maç öncesi metric11 tahmini: "
            f"{_pick_text(m, pick)} ({_pct(m.get(pick + '_win_probability') if pick != 'draw' else m.get('draw_probability'))})."
        )
    else:
        description = (
            f"{home} - {away} maç tahmini: {home} {_pct(m.get('home_win_probability'))}, beraberlik "
            f"{_pct(m.get('draw_probability'))}, {away} {_pct(m.get('away_win_probability'))}."
            + (f" Olası skor {rec}." if rec else "")
            + f" Süper Lig {week}. hafta, {_date_text(dt)}."
        )

    parts = [_STYLE, _json_ld(m, dt, path, week)]
    parts.append(
        f'<div class="mp-hero"><h1>{escape(home)} - {escape(away)} maç tahmini</h1>'
        f'<div class="mp-meta">Trendyol Süper Lig {SEASON_TAG} · {week}. hafta · {escape(_date_text(dt))}</div></div>'
    )

    if played:
        actual = _actual(m.get("actual_score"))
        ok = actual == pick
        verdict = '<span class="mp-ok">✓ Tahmin tuttu</span>' if ok else '<span class="mp-miss">✗ Tahmin tutmadı</span>'
        parts.append(
            f'<div class="mp-card"><h2>Sonuç: {escape(home)} {escape(m.get("actual_score") or "")} {escape(away)}</h2>'
            f'<p>Maç öncesi tahminimiz: <span class="mp-pick">{escape(_pick_text(m, pick))}</span> &nbsp;{verdict}</p>'
            '<p class="mp-note">Aşağıdaki olasılıklar maç başlamadan önce dondurulmuş haliyle gösterilir; '
            'sonradan değiştirilmez. Tüm sonuçlar <a href="weekly_evaluation_2026_2027.html">haftalık isabet karnesinde</a>.</p></div>'
        )
    else:
        parts.append(
            f'<div class="mp-card"><h2>Tahmin: <span class="mp-pick">{escape(_pick_text(m, pick))}</span></h2>'
            f'<p>{escape(_summary_sentence(m, pick))}</p></div>'
        )

    parts.append(f'<div class="mp-card"><h2>1X2 olasılıkları</h2>{_prob_bars(m, pick)}</div>')

    sig = signals.get(str(m["match_id"])) or {}
    stats = []
    if rec:
        stats.append((rec, "En olası skor"))
    xh, xa = m.get("expected_home_goals"), m.get("expected_away_goals")
    if isinstance(xh, (int, float)) and isinstance(xa, (int, float)):
        stats.append((f"{xh:.1f} - {xa:.1f}", "Beklenen gol (xG)"))
    if sig.get("over_2_5_probability") is not None:
        stats.append((_pct(sig["over_2_5_probability"]), "2.5 üst olasılığı"))
    if sig.get("btts_probability") is not None:
        stats.append((_pct(sig["btts_probability"]), "Karşılıklı gol (KG var)"))
    if sig.get("home_scores_first_probability") is not None:
        stats.append((_pct(sig["home_scores_first_probability"]), f"İlk golü {home} atar"))
    if sig.get("expected_total_cards") is not None:
        stats.append((f'{sig["expected_total_cards"]:.1f}', "Beklenen kart"))
    if stats:
        cells = "".join(f'<div class="mp-stat"><div class="v">{escape(str(v))}</div><div class="l">{escape(l)}</div></div>' for v, l in stats)
        parts.append(f'<div class="mp-card"><h2>Gol ve skor beklentisi</h2><div class="mp-grid">{cells}</div></div>')

    sc = scorers.get(str(m["match_id"])) or {}
    scorer_rows = []
    for side, team in (("home_scorers", home), ("away_scorers", away)):
        for s in (sc.get(side) or [])[:3]:
            scorer_rows.append(f"<li><b>{escape(s.get('player', ''))}</b> ({escape(team)}) — gol olasılığı {_pct(s.get('scores_probability'))}</li>")
    if scorer_rows and not played:
        parts.append(f'<div class="mp-card"><h2>Muhtemel golcüler</h2><ul class="mp-list">{"".join(scorer_rows)}</ul></div>')

    form = [
        (f"{m.get('home_points_per_match', 0):.2f}", f"{home} maç başı puan (son 8)"),
        (f"{m.get('away_points_per_match', 0):.2f}", f"{away} maç başı puan (son 8)"),
        (f"{m.get('home_elo', 0):.0f}", f"{home} Elo"),
        (f"{m.get('away_elo', 0):.0f}", f"{away} Elo"),
    ]
    cells = "".join(f'<div class="mp-stat"><div class="v">{v}</div><div class="l">{escape(l)}</div></div>' for v, l in form)
    h2h = m.get("head_to_head") or {}
    h2h_txt = ""
    if h2h.get("available"):
        h2h_txt = f'<p class="mp-note">Aralarındaki son {h2h.get("matches")} maçta beraberlik oranı {_pct(h2h.get("draw_rate"))}.</p>'
    parts.append(f'<div class="mp-card"><h2>Form ve güç karşılaştırması</h2><div class="mp-grid">{cells}</div>{h2h_txt}</div>')

    if not played:
        parts.append('<a class="mp-cta" href="https://tahmin.metric11.com/">🎮 Sen de bu maçı tahmin et — ücretsiz tahmin oyununa katıl</a>')

    others = [x for x in week_matches if x["match_id"] != m["match_id"]]
    other_links = "".join(
        f'<a href="{match_page_path(x["home_team"], x["away_team"])}">{escape(display_name(x["home_team"]))} - {escape(display_name(x["away_team"]))}</a>'
        for x in others
    )
    team_links = "".join(
        f'<a href="{_TEAM_PAGE.format(slug=team_slug(t))}">{escape(display_name(t))} sayfası</a>' for t in (home_raw, away_raw)
    )
    parts.append(
        f'<div class="mp-card mp-links"><h2>{week}. haftanın diğer maçları</h2>{other_links}'
        f'<p><a href="{week_page_path(week)}"><b>Süper Lig {week}. hafta tüm tahminler →</b></a></p>'
        f'<p>{team_links}<a href="season_fixture_predictions_2026_2027.html">Tüm sezon fikstürü</a></p></div>'
    )
    parts.append(_share_button(f"{BASE_URL}/{path}", f"{home} - {away} maç tahmini: {_pick_text(m, pick)} — metric11"))
    parts.append(
        '<p class="mp-note">Tahminler, takımların son maç formu, gol ve xG ortalamaları, Elo gücü, transfer/kadro '
        'değişimi ve Avrupa yorgunluğu sinyallerini birleştiren istatistiksel bir modelden üretilir; '
        'maç başlayana kadar her gün güncellenir. Bahis tavsiyesi değildir.</p>'
    )

    html = page_html(title, "\n".join(parts), description=description, active_nav="season_fixture_predictions_2026_2027.html", og_image="og-image.png", canonical_path=path)
    meta = {"path": path, "week": week, "home": home, "away": away, "date_time": m.get("date_time"), "played": played}
    return path, html, meta


def build_week_page(week: int, matches: list[dict]) -> tuple[str, str]:
    path = week_page_path(week)
    dts = [d for d in (_parse_dt(m.get("date_time", "")) for m in matches) if d]
    span = ""
    if dts:
        lo, hi = min(dts), max(dts)
        span = f"{lo.day} {_TR_MONTHS[lo.month]}" + (f" - {hi.day} {_TR_MONTHS[hi.month]}" if hi.date() != lo.date() else "") + f" {hi.year}"
    played = [m for m in matches if m.get("is_played")]
    title = f"Süper Lig {week}. Hafta Tahminleri ve Skor Tahminleri ({span})" if span else f"Süper Lig {week}. Hafta Tahminleri"
    description = f"Trendyol Süper Lig {SEASON_TAG} {week}. hafta {len(matches)} maçın tahminleri: 1X2 olasılıkları, olası skorlar ve gol beklentileri."
    rows = []
    for m in sorted(matches, key=lambda x: _parse_dt(x.get("date_time", "")) or datetime.max):
        pick = m.get("predicted") or "home"
        rec = (m.get("recommended_scoreline") or {}).get("score") or "—"
        if m.get("is_played"):
            ok = _actual(m.get("actual_score")) == pick
            res = f'{escape(m.get("actual_score") or "")} {"<span class=mp-ok>✓</span>" if ok else "<span class=mp-miss>✗</span>"}'
        else:
            res = escape(rec)
        dt = _parse_dt(m.get("date_time", ""))
        rows.append(
            f'<tr><td>{escape(f"{dt.day} {_TR_MONTHS[dt.month][:3]} {dt:%H:%M}" if dt else "—")}</td>'
            f'<td><a href="{match_page_path(m["home_team"], m["away_team"])}">{escape(display_name(m["home_team"]))} - {escape(display_name(m["away_team"]))}</a></td>'
            f'<td>{escape(_pick_text(m, pick))}</td><td>{res}</td></tr>'
        )
    head = "<tr><th>Tarih</th><th>Maç</th><th>Tahmin</th><th>" + ("Skor" if played else "Olası skor") + "</th></tr>"
    summary = ""
    if played:
        hits = sum(_actual(m.get("actual_score")) == (m.get("predicted") or "home") for m in played)
        summary = f"<p>Bu haftanın oynanan {len(played)} maçında {hits} isabet.</p>"
    nav = []
    if week > 1:
        nav.append(f'<a href="{week_page_path(week - 1)}">← {week - 1}. hafta</a>')
    if week < 34:
        nav.append(f'<a href="{week_page_path(week + 1)}">{week + 1}. hafta →</a>')
    body = (
        _STYLE
        + f'<div class="mp-hero"><h1>Süper Lig {week}. hafta tahminleri</h1><div class="mp-meta">Trendyol Süper Lig {SEASON_TAG}{" · " + escape(span) if span else ""}</div></div>'
        + summary
        + f'<div class="mp-card" style="overflow-x:auto"><table class="mp-week">{head}{"".join(rows)}</table></div>'
        + '<a class="mp-cta" href="https://tahmin.metric11.com/">🎮 Bu haftanın maçlarını sen de tahmin et</a>'
        + f'<div class="mp-card mp-links">{"".join(nav)}<a href="season_fixture_predictions_2026_2027.html">Tüm sezon fikstürü</a><a href="weekly_evaluation_2026_2027.html">Haftalık isabet karnesi</a></div>'
        + _share_button(f"{BASE_URL}/{path}", f"Süper Lig {week}. hafta tahminleri — metric11")
    )
    html = page_html(title, body, description=description, active_nav="season_fixture_predictions_2026_2027.html", canonical_path=path)
    return path, html


def main() -> None:
    payload = json.loads(FIXTURE_PREDICTIONS_JSON.read_text(encoding="utf-8"))
    signals, scorers = _load(SIGNALS_PATH), _load(SCORERS_PATH)
    index = {"generated_at": datetime.now().isoformat(), "season": SEASON_TAG, "weeks": [], "matches": []}
    written = 0
    for week in payload["weeks"]:
        n, matches = week["week"], week["matches"]
        for m in matches:
            path, html, meta = build_match_page(m, n, signals, scorers, matches)
            (PROCESSED_DIR / path).write_text(html, encoding="utf-8")
            index["matches"].append(meta)
            written += 1
        path, html = build_week_page(n, matches)
        (PROCESSED_DIR / path).write_text(html, encoding="utf-8")
        index["weeks"].append({"week": n, "path": path, "played": all(m.get("is_played") for m in matches)})
    INDEX_JSON.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Maç sayfaları: {written}, hafta sayfaları: {len(index['weeks'])}")


if __name__ == "__main__":
    main()
