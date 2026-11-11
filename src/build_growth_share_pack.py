"""Güncel model çıktılarını ölçülebilir sosyal dağıtım metinlerine dönüştürür.

Bu modül otomatik paylaşım yapmaz. X, Telegram ve Instagram için hazır metinler
ve UTM etiketli bağlantılar üretir; yayın kararı insanda kalır.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from urllib.parse import urlencode

from src.build_match_pages import _parse_dt, _pick_text, display_name, match_page_path, week_page_path
from src.config import PROCESSED_DIR

BASE_URL = "https://metric11.com"
FIXTURES_PATH = PROCESSED_DIR / "season_fixture_predictions_2026_2027.json"
SIMULATION_PATH = PROCESSED_DIR / "season_simulation_2026_2027.json"
SIMULATION_HISTORY_PATH = PROCESSED_DIR / "season_simulation_history_2026_2027.json"
SCENARIOS_PATH = PROCESSED_DIR / "season_scenarios_2026_2027.json"
WEEKLY_PATH = PROCESSED_DIR / "weekly_evaluation_2026_2027.json"
OUTPUT_JSON = PROCESSED_DIR / "growth_share_pack_2026_2027.json"
OUTPUT_MD = PROCESSED_DIR / "growth_share_pack_2026_2027.md"


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _pct(value: float) -> str:
    return f"%{round(value * 100)}"


def _url(path: str, source: str, campaign: str, content: str) -> str:
    query = urlencode({
        "utm_source": source,
        "utm_medium": "social",
        "utm_campaign": campaign,
        "utm_content": content,
    })
    return f"{BASE_URL}/{path}?{query}"


def _next_week(fixtures: dict) -> dict | None:
    return next(
        (week for week in fixtures.get("weeks", []) if any(not m.get("is_played") for m in week.get("matches", []))),
        None,
    )


def _strongest_match(week: dict | None) -> dict | None:
    if not week:
        return None
    scheduled = [m for m in week.get("matches", []) if not m.get("is_played") and _parse_dt(m.get("date_time", ""))]
    if not scheduled:
        return None
    return max(
        scheduled,
        key=lambda m: max(
            m.get("home_win_probability") or 0,
            m.get("draw_probability") or 0,
            m.get("away_win_probability") or 0,
        ),
    )


def _largest_title_movement(simulation: dict, history: list[dict]) -> dict | None:
    current_week = simulation.get("after_week", 0)
    previous = next((item for item in reversed(history) if item.get("after_week", 0) < current_week), None)
    if not previous:
        return None
    previous_teams = previous.get("teams", {})
    movements = []
    for row in simulation.get("teams", []):
        old = (previous_teams.get(row["team"]) or {}).get("champion")
        if old is None:
            continue
        movements.append({
            "team": row["name"],
            "before": old,
            "now": row["sim"]["champion"],
            "delta": row["sim"]["champion"] - old,
        })
    return max(movements, key=lambda item: abs(item["delta"])) if movements else None


def build_payload(fixtures: dict, simulation: dict, history: list[dict], scenarios: dict, weekly: dict) -> dict:
    week = _next_week(fixtures)
    week_no = week["week"] if week else simulation.get("after_week", 0) + 1
    campaign = f"super_lig_week_{week_no}"
    leaders = sorted(simulation.get("teams", []), key=lambda row: -row["sim"]["champion"])
    leader = leaders[0] if leaders else None
    runner_up = leaders[1] if len(leaders) > 1 else None
    movement = _largest_title_movement(simulation, history)
    leader_scenario = next((s for s in scenarios.get("scenarios", []) if leader and s["team"] == leader["team"]), None)
    strongest = _strongest_match(week)
    last_week = weekly.get("last_week") or {}
    last_summary = last_week.get("summary") or {}

    campaigns = []
    if leader:
        scenario_line = ""
        if leader_scenario:
            outcome = leader_scenario["outcomes"]
            scenario_line = (
                f" Sıradaki maçını kazanırsa {_pct(outcome['win']['champion'])}, "
                f"kaybederse {_pct(outcome['loss']['champion'])}."
            )
        movement_line = ""
        if movement:
            direction = "yükseldi" if movement["delta"] > 0 else "düştü"
            movement_line = f" En büyük değişim: {movement['team']} {abs(round(movement['delta'] * 100))} puan {direction}."
        base = (
            f"Süper Lig şampiyonluk yarışında yeni tablo: {leader['name']} {_pct(leader['sim']['champion'])}"
            + (f", {runner_up['name']} {_pct(runner_up['sim']['champion'])}." if runner_up else ".")
            + scenario_line
            + movement_line
        )
        path = scenarios.get("page_path") or "super-lig-sampiyonluk-senaryolari-2026-27.html"
        campaigns.append({
            "id": "championship_race",
            "hook": "Kazanırsa şampiyonluk ihtimali ne oluyor?",
            "target_path": path,
            "x": f"{base}\n\n{_url(path, 'x', campaign, 'championship_race')}",
            "telegram": f"🏆 <b>Şampiyonluk yarışı güncellendi</b>\n\n{base}\n\nDetaylı senaryolar: {_url(path, 'telegram', campaign, 'championship_race')}",
            "instagram": f"🏆 Şampiyonluk yarışı güncellendi\n\n{base}\n\nTüm senaryolar metric11.com'da.\n\n#SüperLig #FutbolAnaliz #Şampiyonluk",
        })

    if strongest and week:
        pick = strongest.get("predicted") or "home"
        top_probability = max(
            strongest.get("home_win_probability") or 0,
            strongest.get("draw_probability") or 0,
            strongest.get("away_win_probability") or 0,
        )
        home, away = display_name(strongest["home_team"]), display_name(strongest["away_team"])
        score = (strongest.get("recommended_scoreline") or {}).get("score") or "—"
        path = match_page_path(strongest["home_team"], strongest["away_team"])
        base = (
            f"{week_no}. haftanın en güçlü model sinyali: {home} - {away}. "
            f"Tahmin: {_pick_text(strongest, pick)} ({_pct(top_probability)}), olası skor {score}."
        )
        campaigns.append({
            "id": "strongest_match",
            "hook": f"{week_no}. haftanın en güçlü tahmini",
            "target_path": path,
            "x": f"{base}\n\n{_url(path, 'x', campaign, 'strongest_match')}",
            "telegram": f"⚽ <b>{week_no}. haftanın öne çıkan maçı</b>\n\n{base}\n\nMaç analizi: {_url(path, 'telegram', campaign, 'strongest_match')}",
            "instagram": f"⚽ {week_no}. haftanın öne çıkan maçı\n\n{base}\n\n#SüperLig #MaçTahmini #Futbol",
        })

    if last_summary:
        evaluated = last_summary.get("evaluated_matches", 0)
        correct = last_summary.get("correct", 0)
        accuracy = round((last_summary.get("accuracy") or 0) * 100)
        path = "weekly_evaluation_2026_2027.html"
        base = (
            f"Model karnesini saklamıyoruz: {last_week.get('week')}. haftada {evaluated} maçta "
            f"{correct} doğru tahmin, %{accuracy} isabet. Doğrular ve hatalar tek tek yayında."
        )
        campaigns.append({
            "id": "transparent_scorecard",
            "hook": "Tahmin karnemiz açık",
            "target_path": path,
            "x": f"{base}\n\n{_url(path, 'x', campaign, 'scorecard')}",
            "telegram": f"📊 <b>Haftalık tahmin karnesi</b>\n\n{base}\n\nKarne: {_url(path, 'telegram', campaign, 'scorecard')}",
            "instagram": f"📊 Tahmin karnemiz açık\n\n{base}\n\n#FutbolAnaliz #SüperLig #Veri",
        })

    return {
        "generated_at": datetime.now().astimezone().isoformat(),
        "season": fixtures.get("season", "2026-2027"),
        "week": week_no,
        "campaign": campaign,
        "publication_mode": "manual_review_required",
        "campaigns": campaigns,
    }


def build_markdown(payload: dict) -> str:
    lines = [
        "# metric11 Haftalık Dağıtım Paketi",
        "",
        f"- Hafta: {payload['week']}",
        f"- Üretim: {payload['generated_at']}",
        "- Yayın modu: Editör kontrolünden sonra manuel paylaşım",
        "",
    ]
    for item in payload["campaigns"]:
        lines.extend([
            f"## {item['hook']}",
            "",
            "### X",
            item["x"],
            "",
            "### Telegram",
            item["telegram"],
            "",
            "### Instagram",
            item["instagram"],
            "",
        ])
    return "\n".join(lines)


def main() -> None:
    payload = build_payload(
        _load(FIXTURES_PATH),
        _load(SIMULATION_PATH),
        _load(SIMULATION_HISTORY_PATH),
        _load(SCENARIOS_PATH),
        _load(WEEKLY_PATH),
    )
    OUTPUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    OUTPUT_MD.write_text(build_markdown(payload), encoding="utf-8")
    print(f"Dağıtım paketi: {len(payload['campaigns'])} kampanya, hafta {payload['week']}")


if __name__ == "__main__":
    main()
