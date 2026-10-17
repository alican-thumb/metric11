"""2026-27 Süper Lig şampiyonluk / ilk 4 / küme düşme olasılıkları (Monte Carlo).

Oynanmış maçların gerçek sonuçlarından puan durumu kurulur; kalan maçlar
`season_fixture_predictions_2026_2027.json`'daki model 1X2 olasılıklarıyla N_SIMS kez
oynatılır. Eşitlikte averaj (mevcut) + rastgele kırıcı kullanılır (TFF'nin ikili averaj
kuralı simülasyonda gol üretilmediği için modellenmiyor). Sabit tohum: girdiler
değişmedikçe çıktı birebir aynı kalır (gereksiz commit üretmez).

Ligden düşen: 16-18. sıra (3 takım, TFF 2026-27 statüsü).
"""
from __future__ import annotations

import json
import math
import random
from collections import defaultdict
from datetime import date
from html import escape

from src.build_match_pages import _STYLE, _actual, display_name, match_page_path, week_page_path
from src.build_season_fixture_predictions import OUTPUT_JSON as FIXTURE_PREDICTIONS_JSON
from src.config import PROCESSED_DIR
from src.html_utils import _share_button, page_html

N_SIMS = 20_000
SEED = 2026
RELEGATION_SPOTS = 3
PAGE_PATH = "super-lig-sampiyonluk-oranlari-2026-27.html"
OUTPUT_JSON = PROCESSED_DIR / "season_simulation_2026_2027.json"
HISTORY_JSON = PROCESSED_DIR / "season_simulation_history_2026_2027.json"
BASE_URL = "https://metric11.com"


def _goals(score: str) -> tuple[int, int]:
    h, a = (int(x) for x in score.replace(" ", "").split("-"))
    return h, a


def current_table(weeks: list[dict]) -> dict[str, dict]:
    table: dict[str, dict] = defaultdict(lambda: {"played": 0, "w": 0, "d": 0, "l": 0, "gf": 0, "ga": 0, "pts": 0})
    for week in weeks:
        for m in week["matches"]:
            for team in (m["home_team"], m["away_team"]):
                table[team]  # her takım tabloda olsun
            if not m.get("is_played") or _actual(m.get("actual_score")) is None:
                continue
            hg, ag = _goals(m["actual_score"])
            for team, gf, ga in ((m["home_team"], hg, ag), (m["away_team"], ag, hg)):
                row = table[team]
                row["played"] += 1
                row["gf"] += gf
                row["ga"] += ga
                if gf > ga:
                    row["w"] += 1
                    row["pts"] += 3
                elif gf == ga:
                    row["d"] += 1
                    row["pts"] += 1
                else:
                    row["l"] += 1
    return dict(table)


# Uzun vadeli güç önseli: maç modeli son 8 maçlık formdan tahmin ediyor; bunu kalan 27
# haftaya aynen yaymak uç sonuç veriyordu (2026-10-17: 7. hafta sonrası yeni yükselen
# Amedspor şampiyonluk favorisi, Eyüpspor %100 düşüyor). Kalan maçlarda model olasılığı
# kadro piyasa değerinden türetilen olasılıkla harmanlanır. 2025-26 7/10/15. hafta
# kesitlerinden sezon sonu puan RMSE'si 7.25→6.41 / 6.57→5.86 / 6.13→5.30 (w=0.5, k=0.5);
# 2025-26 MV verisi sezon sonu çekildiği için bu ölçüm iyimser — bilerek temkinli ayar.
MV_PRIOR_WEIGHT = 0.5
MV_LOG_SLOPE = 0.5
MV_HOME_ADVANTAGE = 0.25
SQUADS_PATH = PROCESSED_DIR / "transfermarkt_super_lig_squads_2026_2027.json"


def _market_values() -> dict[str, float]:
    from src.generate_preview_batch import team_slug

    try:
        clubs = json.loads(SQUADS_PATH.read_text(encoding="utf-8"))["clubs"]
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return {}
    return {team_slug(c["team_name"]): sum(p.get("market_value_eur") or 0 for p in c["players"]) for c in clubs}


def _blend_with_prior(home: str, away: str, ph: float, pd: float, pa: float, mv: dict[str, float]) -> tuple[float, float, float]:
    from src.generate_preview_batch import team_slug

    vh, va = mv.get(team_slug(home)), mv.get(team_slug(away))
    if not vh or not va:
        return ph, pd, pa
    e = 1 / (1 + math.exp(-(MV_LOG_SLOPE * math.log(vh / va) + MV_HOME_ADVANTAGE)))
    d = 0.28 * (1 - abs(e - 0.5))
    prior = (e * (1 - d), d, (1 - e) * (1 - d))
    w = MV_PRIOR_WEIGHT
    mixed = [(1 - w) * x + w * y for x, y in zip((ph, pd, pa), prior)]
    total = sum(mixed)
    return tuple(x / total for x in mixed)


def simulate(weeks: list[dict], table: dict[str, dict]) -> dict[str, dict]:
    mv = _market_values()
    remaining = []
    for week in weeks:
        for m in week["matches"]:
            if m.get("is_played"):
                continue
            ph, pd, _ = _blend_with_prior(
                m["home_team"], m["away_team"],
                m.get("home_win_probability") or 0, m.get("draw_probability") or 0, m.get("away_win_probability") or 0, mv,
            )
            remaining.append((m["home_team"], m["away_team"], ph, ph + pd))
    teams = sorted(table)
    n = len(teams)
    rng = random.Random(SEED)
    counts = {t: {"champion": 0, "top2": 0, "top4": 0, "relegated": 0, "pts_sum": 0, "pos_sum": 0} for t in teams}
    base_pts = {t: table[t]["pts"] for t in teams}
    gd = {t: table[t]["gf"] - table[t]["ga"] for t in teams}
    for _ in range(N_SIMS):
        pts = dict(base_pts)
        for home, away, p_home, p_home_or_draw in remaining:
            r = rng.random()
            if r < p_home:
                pts[home] += 3
            elif r < p_home_or_draw:
                pts[home] += 1
                pts[away] += 1
            else:
                pts[away] += 3
        order = sorted(teams, key=lambda t: (pts[t], gd[t], rng.random()), reverse=True)
        for pos, team in enumerate(order, start=1):
            c = counts[team]
            c["pts_sum"] += pts[team]
            c["pos_sum"] += pos
            if pos == 1:
                c["champion"] += 1
            if pos <= 2:
                c["top2"] += 1
            if pos <= 4:
                c["top4"] += 1
            if pos > n - RELEGATION_SPOTS:
                c["relegated"] += 1
    out = {}
    for team in teams:
        c = counts[team]
        out[team] = {
            "champion": round(c["champion"] / N_SIMS, 4),
            "top2": round(c["top2"] / N_SIMS, 4),
            "top4": round(c["top4"] / N_SIMS, 4),
            "relegated": round(c["relegated"] / N_SIMS, 4),
            "avg_points": round(c["pts_sum"] / N_SIMS, 1),
            "avg_position": round(c["pos_sum"] / N_SIMS, 1),
        }
    return out


def _last_completed_week(weeks: list[dict]) -> int:
    done = 0
    for week in weeks:
        if week["matches"] and all(m.get("is_played") for m in week["matches"]):
            done = week["week"]
    return done


def _previous_snapshot(history: list[dict], after_week: int) -> dict | None:
    older = [h for h in history if h.get("after_week", 0) < after_week]
    return older[-1] if older else None


def _pct(x: float) -> str:
    if x <= 0:
        return "—"
    if x < 0.005:
        return "<%1"
    return f"%{round(x * 100)}"


def _delta(now: float, before: float | None) -> str:
    if before is None:
        return ""
    diff = round((now - before) * 100)
    if diff == 0:
        return ""
    color = "#116447" if diff > 0 else "#b42318"
    return f' <span style="color:{color};font-size:11px;font-weight:700">{"▲" if diff > 0 else "▼"}{abs(diff)}</span>'


def build_html(payload: dict, prev: dict | None) -> str:
    rows_sorted = sorted(payload["teams"], key=lambda r: (-r["pts"], -(r["gf"] - r["ga"]), -r["sim"]["avg_points"]))
    prev_by_team = (prev or {}).get("teams", {})
    rows = []
    for pos, r in enumerate(rows_sorted, start=1):
        s = r["sim"]
        before = prev_by_team.get(r["team"], {})
        rows.append(
            f'<tr><td>{pos}</td><td><a href="{team_page_path(r["team"])}"><b>{escape(r["name"])}</b></a></td><td>{r["pts"]}</td><td>{r["gf"] - r["ga"]:+d}</td>'
            f'<td>{s["avg_points"]:.0f}</td>'
            f'<td>{_pct(s["champion"])}{_delta(s["champion"], before.get("champion"))}</td>'
            f'<td>{_pct(s["top4"])}{_delta(s["top4"], before.get("top4"))}</td>'
            f'<td>{_pct(s["relegated"])}{_delta(s["relegated"], before.get("relegated"))}</td></tr>'
        )
    by_title = sorted(payload["teams"], key=lambda r: -r["sim"]["champion"])
    leader = by_title[0]
    contenders = [r for r in by_title if r["sim"]["champion"] >= 0.01]
    bars = "".join(
        f'<div class="mp-bar"><span>{escape(r["name"])}</span><div class="mp-track"><div class="mp-fill{" pick" if i == 0 else ""}" '
        f'style="width:{max(1, round(r["sim"]["champion"] * 100))}%"></div></div><b>{_pct(r["sim"]["champion"])}</b></div>'
        for i, r in enumerate(contenders)
    )
    danger = sorted(payload["teams"], key=lambda r: -r["sim"]["relegated"])[:5]
    danger_bars = "".join(
        f'<div class="mp-bar"><span>{escape(r["name"])}</span><div class="mp-track"><div class="mp-fill" '
        f'style="width:{max(1, round(r["sim"]["relegated"] * 100))}%;background:#b42318"></div></div><b>{_pct(r["sim"]["relegated"])}</b></div>'
        for r in danger
    )
    wk = payload["after_week"]
    next_week = min(wk + 1, 34)
    intro = (
        f"{wk}. hafta sonu itibarıyla metric11 modeline göre şampiyonluk favorisi "
        f"{leader['name']} ({_pct(leader['sim']['champion'])}). Kalan {payload['remaining_matches']} maç, "
        f"her maçın kazanma/beraberlik olasılığıyla {N_SIMS:,} kez simüle edildi.".replace(",", ".")
    )
    delta_note = f" Oklar {prev['after_week']}. hafta sonrasına göre değişimi gösterir." if prev else ""
    body = (
        _STYLE
        + f'<div class="mp-hero"><h1>Süper Lig şampiyonluk oranları</h1>'
        f'<div class="mp-meta">Trendyol Süper Lig 2026-27 · {wk}. hafta sonrası · güncelleme {escape(payload["generated_on"])}</div></div>'
        + f'<div class="mp-card"><p>{escape(intro)}</p></div>'
        + f'<div class="mp-card"><h2>Şampiyonluk olasılığı</h2><div class="mp-bars">{bars}</div></div>'
        + f'<div class="mp-card"><h2>Küme düşme olasılığı (son 3)</h2><div class="mp-bars">{danger_bars}</div></div>'
        + '<div class="mp-card" style="overflow-x:auto"><h2>Puan durumu ve sezon sonu olasılıkları</h2>'
        '<table class="mp-week"><tr><th>#</th><th>Takım</th><th>P</th><th>Av</th><th>Beklenen puan</th><th>Şampiyon</th><th>İlk 4</th><th>Düşme</th></tr>'
        + "".join(rows)
        + f'</table><p class="mp-note">P: puan, Av: averaj. Beklenen puan: 34 hafta sonu ortalama puan.{delta_note}</p></div>'
        + f'<a class="mp-cta" href="{week_page_path(next_week)}">⚽ {next_week}. hafta maç tahminleri →</a>'
        + '<a class="mp-cta" style="background:#116447;color:#fff" href="https://tahmin.metric11.com/">🎮 Sen de tahmin et, arkadaşlarınla yarış</a>'
        + _share_button(f"{BASE_URL}/{PAGE_PATH}", f"Süper Lig şampiyonluk oranları: {leader['name']} {_pct(leader['sim']['champion'])} — metric11")
        + '<p class="mp-note">Yöntem: oynanan maçların gerçek sonuçları + kalan her maç için modelin '
        '1X2 olasılıkları (form, xG, Elo, kadro/transfer, Avrupa yorgunluğu), uzun vadeli güç için kadro '
        'piyasa değeriyle yarı yarıya harmanlanır (kısa dönem formu tüm sezona yaymamak için). Eşit puanda averaj kullanılır; '
        'TFF ikili averaj kuralı modellenmez. Puan silme cezaları dahil değildir. Bahis tavsiyesi değildir.</p>'
    )
    title = f"Süper Lig Şampiyonluk Oranları 2026-27 ({wk}. Hafta Sonrası)"
    description = (
        f"Süper Lig 2026-27 şampiyonluk, ilk 4 ve küme düşme olasılıkları: {leader['name']} {_pct(leader['sim']['champion'])}. "
        f"{wk}. hafta sonrası {N_SIMS:,} sezon simülasyonu.".replace(",", ".")
    )
    return page_html(title, body, description=description, active_nav="season_fixture_predictions_2026_2027.html", canonical_path=PAGE_PATH)


def team_page_path(team: str) -> str:
    from src.build_match_pages import _url_slug

    return f"{_url_slug(team)}-mac-tahminleri-2026-27.html"


def build_team_page(row: dict, rank: int, weeks: list[dict]) -> str:
    from src.build_match_pages import _date_text, _parse_dt, _pick_text

    team, name, s = row["team"], row["name"], row["sim"]
    rows, hits, played = [], 0, 0
    for week in weeks:
        for m in week["matches"]:
            if team not in (m["home_team"], m["away_team"]):
                continue
            is_home = m["home_team"] == team
            opp = display_name(m["away_team"] if is_home else m["home_team"])
            pick = m.get("predicted") or "home"
            dt = _parse_dt(m.get("date_time", ""))
            if m.get("is_played"):
                played += 1
                ok = _actual(m.get("actual_score")) == pick
                hits += ok
                res = f'{escape(m.get("actual_score") or "")} {"<span class=mp-ok>✓</span>" if ok else "<span class=mp-miss>✗</span>"}'
            else:
                res = escape((m.get("recommended_scoreline") or {}).get("score") or "—")
            rows.append(
                f'<tr><td>{week["week"]}</td><td>{escape(f"{dt.day}.{dt.month:02d}" if dt else "—")}</td>'
                f'<td><a href="{match_page_path(m["home_team"], m["away_team"])}">{"🏠 " if is_home else "✈️ "}{escape(opp)}</a></td>'
                f'<td>{escape(_pick_text(m, pick))}</td><td>{res}</td></tr>'
            )
    stats = [
        (f"{rank}.", "Sıralama"), (str(row["pts"]), f'Puan ({row["played"]} maç)'),
        (f'{row["w"]}-{row["d"]}-{row["l"]}', "G-B-M"), (f'{row["gf"]}-{row["ga"]}', "Atılan-yenilen"),
        (f'{s["avg_points"]:.0f}', "Beklenen sezon sonu puanı"), (_pct(s["champion"]), "Şampiyonluk"),
        (_pct(s["top4"]), "İlk 4"), (_pct(s["relegated"]), "Küme düşme"),
    ]
    cells = "".join(f'<div class="mp-stat"><div class="v">{escape(v)}</div><div class="l">{escape(l)}</div></div>' for v, l in stats)
    next_match = next(
        (m for w in weeks for m in w["matches"] if team in (m["home_team"], m["away_team"]) and not m.get("is_played")), None
    )
    next_html = ""
    if next_match:
        nm_dt = _parse_dt(next_match.get("date_time", ""))
        next_html = (
            f'<a class="mp-cta" href="{match_page_path(next_match["home_team"], next_match["away_team"])}">'
            f'⚽ Sıradaki maç: {escape(display_name(next_match["home_team"]))} - {escape(display_name(next_match["away_team"]))} '
            f'({escape(_date_text(nm_dt, with_day=False))}) — tahmini gör →</a>'
        )
    hit_note = f"<p>Bu sezon {name} maçlarında tahmin isabetimiz: {played} maçta {hits}.</p>" if played else ""
    path = team_page_path(team)
    body = (
        _STYLE
        + f'<div class="mp-hero"><h1>{escape(name)} maç tahminleri 2026-27</h1>'
        f'<div class="mp-meta">Trendyol Süper Lig · {payload_week_text(row)}</div></div>'
        + f'<div class="mp-card"><h2>Sezon durumu</h2><div class="mp-grid">{cells}</div>{hit_note}</div>'
        + next_html
        + f'<div class="mp-card" style="overflow-x:auto"><h2>{escape(name)} fikstürü ve tahminler</h2>'
        '<table class="mp-week"><tr><th>H</th><th>Tarih</th><th>Rakip</th><th>Tahmin</th><th>Skor</th></tr>'
        + "".join(rows) + "</table></div>"
        + f'<div class="mp-card mp-links"><a href="{PAGE_PATH}">🏆 Şampiyonluk oranları</a>'
        f'<a href="season_fixture_predictions_2026_2027.html">Tüm fikstür</a><a href="https://tahmin.metric11.com/taraftar">🔥 {escape(name)} taraftarı mısın? Amigo Ligi</a></div>'
        + _share_button(f"{BASE_URL}/{path}", f"{name} 2026-27: şampiyonluk {_pct(s['champion'])}, beklenen puan {s['avg_points']:.0f} — metric11")
    )
    title = f"{name} Maç Tahminleri ve Fikstürü 2026-27"
    description = (
        f"{name} 2026-27 Süper Lig fikstürü, maç maç tahminler ve sonuçlar. Şampiyonluk olasılığı {_pct(s['champion'])}, "
        f"ilk 4 {_pct(s['top4'])}, beklenen sezon sonu puanı {s['avg_points']:.0f}."
    )
    return page_html(title, body, description=description, active_nav="season_fixture_predictions_2026_2027.html", canonical_path=path)


def payload_week_text(row: dict) -> str:
    return f'{row["played"]} maç oynandı · {row["pts"]} puan'


def main() -> None:
    fixture = json.loads(FIXTURE_PREDICTIONS_JSON.read_text(encoding="utf-8"))
    weeks = fixture["weeks"]
    table = current_table(weeks)
    sim = simulate(weeks, table)
    after_week = _last_completed_week(weeks)
    teams = [
        {"team": t, "name": display_name(t), **{k: table[t][k] for k in ("played", "w", "d", "l", "gf", "ga", "pts")}, "sim": sim[t]}
        for t in sorted(table)
    ]
    payload = {
        "generated_on": date.today().isoformat(),
        "after_week": after_week,
        "n_sims": N_SIMS,
        "remaining_matches": sum(1 for w in weeks for m in w["matches"] if not m.get("is_played")),
        "page_path": PAGE_PATH,
        "teams": teams,
    }
    history = json.loads(HISTORY_JSON.read_text(encoding="utf-8")) if HISTORY_JSON.exists() else []
    # Hafta başına tek kayıt: hafta tamamlandığında o haftanın son hali saklanır.
    snapshot = {"after_week": after_week,
                "teams": {r["team"]: {k: r["sim"][k] for k in ("champion", "top4", "relegated")} for r in teams}}
    history = [h for h in history if h.get("after_week") != after_week] + [snapshot]
    history.sort(key=lambda h: h["after_week"])
    prev = _previous_snapshot(history, after_week)
    OUTPUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    HISTORY_JSON.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")
    (PROCESSED_DIR / PAGE_PATH).write_text(build_html(payload, prev), encoding="utf-8")
    standings = sorted(teams, key=lambda r: (-r["pts"], -(r["gf"] - r["ga"]), -r["sim"]["avg_points"]))
    for rank, row in enumerate(standings, start=1):
        (PROCESSED_DIR / team_page_path(row["team"])).write_text(build_team_page(row, rank, weeks), encoding="utf-8")
    leader = max(teams, key=lambda r: r["sim"]["champion"])
    print(f"Simülasyon: {after_week}. hafta sonrası, lider favori {leader['name']} {leader['sim']['champion']:.1%}")


if __name__ == "__main__":
    main()
