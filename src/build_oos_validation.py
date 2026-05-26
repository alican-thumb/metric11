"""
Out-of-sample validasyon: sezonu hafta bazlı ikiye böler, ilk N haftanın
birikmeli tarihiyle kalan haftaların tahmin doğruluğunu ölçer.

Mevcut backtest kronolojik (walk-forward) olduğu için teknik olarak OOS sayılır;
bu rapor ek olarak kümülatif doğruluk eğrisi, hafta bazlı kırılım ve
güven seviyesi karşılaştırması üretir.
"""
from __future__ import annotations

import json
import math
from collections import Counter, defaultdict, deque
from pathlib import Path

from src.config import PROCESSED_DIR, SEASON
from src.html_utils import md_to_html, page_html
from src.model_league_predictions import (
    DRAW_BOOST_SCALE,
    DRAW_PRED_MAX_GAP,
    DRAW_PRED_MIN_PROB,
    actual_result,
    confidence_label,
    draw_calibrated_prediction,
    poisson_result_probs,
    predict_match,
    update_elo,
    update_history,
    _main_referee,
    _referee_stats,
    brier_score,
    log_loss,
)
from src.normalization import normalize_matches

OUTPUT_JSON = PROCESSED_DIR / f"oos_validation_{SEASON}.json"
OUTPUT_MD = PROCESSED_DIR / f"oos_validation_{SEASON}.md"
OUTPUT_HTML = PROCESSED_DIR / f"oos_validation_{SEASON}.html"

WARMUP_WEEKS = 5       # minimum hafta modeli kullanmadan önce geçecek
SPLIT_WEEK = 17        # 1-17 = "ilk yarı" (birikim), 18-34 = "ikinci yarı" (test)
MIN_TEAM_HISTORY = 5


def main() -> None:
    matches = normalize_matches(
        json.loads((PROCESSED_DIR / f"tff_super_lig_enriched_{SEASON}.json").read_text(encoding="utf-8"))
    )
    matches = [m for m in matches if m["home_team"]["score"] is not None]
    matches.sort(key=lambda m: _sort_key(m))

    all_rows, by_week = run_walk_forward(matches)

    payload = build_payload(all_rows, by_week)
    md = build_markdown(payload)
    OUTPUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    OUTPUT_MD.write_text(md, encoding="utf-8")
    OUTPUT_HTML.write_text(page_html(f"OOS Validasyon — {SEASON.replace('_', '-')}", md_to_html(md)), encoding="utf-8")
    print(md)


def run_walk_forward(matches: list[dict]) -> tuple[list[dict], dict[int, list[dict]]]:
    team_history = defaultdict(lambda: deque(maxlen=8))
    referee_history: dict[str, list[dict]] = defaultdict(list)
    elo = defaultdict(lambda: 1500.0)
    all_rows = []
    by_week: dict[int, list[dict]] = defaultdict(list)

    for m in matches:
        home = m["home_team"]["name"]
        away = m["away_team"]["name"]
        home_goals = m["home_team"]["score"] or 0
        away_goals = m["away_team"]["score"] or 0
        week = m.get("fixture_week") or 0
        home_h = list(team_history[home])
        away_h = list(team_history[away])
        main_ref = _main_referee(m)
        ref_stats = _referee_stats(referee_history, main_ref)

        if len(home_h) >= MIN_TEAM_HISTORY and len(away_h) >= MIN_TEAM_HISTORY:
            pred = predict_match(home, away, home_h, away_h, elo[home], elo[away], ref_stats)
            actual = actual_result(home_goals, away_goals)
            home_p = pred["home_win_probability"]
            draw_p = pred["draw_probability"]
            away_p = pred["away_win_probability"]
            raw_predicted = max({"home": home_p, "draw": draw_p, "away": away_p}, key=lambda k: {"home": home_p, "draw": draw_p, "away": away_p}[k])
            predicted = draw_calibrated_prediction(home_p, draw_p, away_p, pred.get("strength_edge", 0.0))
            row = {
                "match_id": m["external_id"],
                "week": week,
                "home": home,
                "away": away,
                "score": f"{home_goals}-{away_goals}",
                "raw_predicted": raw_predicted,
                "predicted": predicted,
                "actual": actual,
                "correct": predicted == actual,
                "raw_correct": raw_predicted == actual,
                "confidence": confidence_label(pred),
                "home_win_probability": home_p,
                "draw_probability": draw_p,
                "away_win_probability": away_p,
            }
            all_rows.append(row)
            by_week[week].append(row)

        ss = m.get("sofascore_stats") or {}
        total_cards = len(m["cards"]["home"]) + len(m["cards"]["away"])
        if main_ref:
            referee_history[main_ref].append({"cards": total_cards, "goals": home_goals + away_goals})
        update_history(team_history, home, home_goals, away_goals, len(m["cards"]["home"]), is_home=True,
                       xg_for=ss.get("xg_home"), xg_against=ss.get("xg_away"))
        update_history(team_history, away, away_goals, home_goals, len(m["cards"]["away"]), is_home=False,
                       xg_for=ss.get("xg_away"), xg_against=ss.get("xg_home"))
        update_elo(elo, home, away, home_goals, away_goals)

    return all_rows, dict(by_week)


def _accuracy(rows: list[dict]) -> dict:
    if not rows:
        return {"matches": 0, "correct": 0, "accuracy": None, "brier": None, "log_loss": None}
    correct = sum(1 for r in rows if r["correct"])
    return {
        "matches": len(rows),
        "correct": correct,
        "accuracy": round(correct / len(rows), 3),
        "brier": round(sum(brier_score(r) for r in rows) / len(rows), 3),
        "log_loss": round(sum(log_loss(r) for r in rows) / len(rows), 3),
    }


def _confidence_breakdown(rows: list[dict]) -> dict:
    result = {}
    for label in ("HIGH", "MEDIUM", "LOW"):
        subset = [r for r in rows if r["confidence"] == label]
        result[label] = _accuracy(subset)
    return result


def _week_cumulative(by_week: dict[int, list[dict]]) -> list[dict]:
    cumulative_rows = []
    result = []
    for week in sorted(by_week.keys()):
        cumulative_rows.extend(by_week[week])
        acc = _accuracy(cumulative_rows)
        result.append({"week": week, **acc})
    return result


def _raw_accuracy(rows: list[dict]) -> dict:
    if not rows:
        return {"matches": 0, "correct": 0, "accuracy": None}
    correct = sum(1 for r in rows if r["raw_correct"])
    return {"matches": len(rows), "correct": correct, "accuracy": round(correct / len(rows), 3)}


def build_payload(all_rows: list[dict], by_week: dict[int, list[dict]]) -> dict:
    first_half = [r for r in all_rows if r["week"] <= SPLIT_WEEK]
    second_half = [r for r in all_rows if r["week"] > SPLIT_WEEK]

    return {
        "season": SEASON,
        "split_week": SPLIT_WEEK,
        "warmup_weeks": WARMUP_WEEKS,
        "note": (
            f"Walk-forward kronolojik backtest. Her tahmin yalnızca önceki maçların birikimiyle yapılır. "
            f"Hafta 1-{SPLIT_WEEK} = ısınma + ilk yarı; hafta {SPLIT_WEEK+1}-34 = bağımsız test penceresi."
        ),
        "full_season": {**_accuracy(all_rows), "confidence": _confidence_breakdown(all_rows)},
        "first_half": {**_accuracy(first_half), "confidence": _confidence_breakdown(first_half)},
        "second_half_oos": {**_accuracy(second_half), "confidence": _confidence_breakdown(second_half)},
        "raw_baseline": {
            "full_season": _raw_accuracy(all_rows),
            "second_half_oos": _raw_accuracy(second_half),
        },
        "cumulative_by_week": _week_cumulative(by_week),
        "result_type_breakdown": _result_type_breakdown(all_rows),
        "raw_result_type_breakdown": _result_type_breakdown(all_rows, use_raw=True),
    }


def _result_type_breakdown(rows: list[dict], use_raw: bool = False) -> dict:
    def acc_fn(subset: list[dict]) -> dict:
        if not subset:
            return {"matches": 0, "correct": 0, "accuracy": None}
        if use_raw:
            correct = sum(1 for r in subset if r["raw_correct"])
        else:
            correct = sum(1 for r in subset if r["correct"])
        return {"matches": len(subset), "correct": correct, "accuracy": round(correct / len(subset), 3) if subset else None}

    return {
        outcome: acc_fn([r for r in rows if r["actual"] == outcome])
        for outcome in ("home", "draw", "away")
    }


def build_markdown(payload: dict) -> str:
    full = payload["full_season"]
    first = payload["first_half"]
    oos = payload["second_half_oos"]

    def pct(d: dict) -> str:
        a = d.get("accuracy")
        return f"%{a*100:.1f} ({d['correct']}/{d['matches']})" if a is not None else "—"

    def conf_row(d: dict, label: str) -> str:
        c = d.get("confidence", {}).get(label, {})
        return f"| {label} | {pct(c)} | Brier: {c.get('brier','—')} |"

    lines = [
        f"# Out-of-Sample Validasyon Raporu — {SEASON.replace('_','-')}",
        "",
        f"Split: Hafta 1-{payload['split_week']} birikimli tarih, Hafta {payload['split_week']+1}+ bağımsız test.",
        f"_Not: {payload['note']}_",
        "",
        "## Özet",
        "",
        f"| Dönem | Doğruluk | Brier | Log Loss |",
        f"|---|---:|---:|---:|",
        f"| Tüm sezon | {pct(full)} | {full.get('brier','—')} | {full.get('log_loss','—')} |",
        f"| İlk yarı (hafta 1-{payload['split_week']}) | {pct(first)} | {first.get('brier','—')} | {first.get('log_loss','—')} |",
        f"| **İkinci yarı OOS (hafta {payload['split_week']+1}-34)** | **{pct(oos)}** | {oos.get('brier','—')} | {oos.get('log_loss','—')} |",
        "",
        "## Güven Seviyesi Kırılımı (Tüm Sezon)",
        "",
        "| Güven | Doğruluk | |",
        "|---|---:|---|",
        conf_row(full, "HIGH"),
        conf_row(full, "MEDIUM"),
        conf_row(full, "LOW"),
        "",
        "## Güven Seviyesi Kırılımı (OOS — İkinci Yarı)",
        "",
        "| Güven | Doğruluk | |",
        "|---|---:|---|",
        conf_row(oos, "HIGH"),
        conf_row(oos, "MEDIUM"),
        conf_row(oos, "LOW"),
        "",
        "## Sonuç Tipi Kırılımı (Tüm Sezon)",
        "",
        "| Gerçek Sonuç | Model Doğruluğu |",
        "|---|---:|",
    ]
    for outcome, label in (("home", "Ev sahibi kazandı"), ("draw", "Beraberlik"), ("away", "Deplasman kazandı")):
        d = payload["result_type_breakdown"].get(outcome, {})
        lines.append(f"| {label} | {pct(d)} |")

    lines.extend([
        "",
        "## Kümülatif Doğruluk (son 10 hafta)",
        "",
        "| Hafta | Kümülatif Doğruluk | Maç |",
        "|---:|---:|---:|",
    ])
    for item in payload["cumulative_by_week"][-10:]:
        a = item.get("accuracy")
        lines.append(f"| {item['week']} | {f'%{a*100:.1f}' if a else '—'} | {item['matches']} |")

    raw_full = payload.get("raw_baseline", {}).get("full_season", {})
    raw_oos = payload.get("raw_baseline", {}).get("second_half_oos", {})
    raw_rtb = payload.get("raw_result_type_breakdown", {})
    cal_rtb = payload.get("result_type_breakdown", {})

    lines.extend([
        "",
        "## Draw Kalibrasyon Karşılaştırması",
        "",
        "| | Ham argmax | Kalibre |",
        "|---|---:|---:|",
        f"| Tüm sezon doğruluk | {pct(raw_full)} | {pct(full)} |",
        f"| OOS ikinci yarı doğruluk | {pct(raw_oos)} | {pct(oos)} |",
        f"| Beraberlik doğruluğu (tüm sezon) | {pct(raw_rtb.get('draw', {}))} | {pct(cal_rtb.get('draw', {}))} |",
        f"| Ev sahibi doğruluğu | {pct(raw_rtb.get('home', {}))} | {pct(cal_rtb.get('home', {}))} |",
        f"| Deplasman doğruluğu | {pct(raw_rtb.get('away', {}))} | {pct(cal_rtb.get('away', {}))} |",
        "",
        "## Yorumlama",
        "",
        "- Tüm sezon doğruluğu walk-forward kronolojik tahmindir; gelecek sonuçlar o anda görülmüyor.",
        f"- Hafta {payload['split_week']+1}+ (ikinci yarı OOS) gerçek bağımsız test penceresine en yakın ölçüm.",
        "- Hiperparametreler (K faktör, blend oranı) bu sezon verisine göre ayarlanmadı; genel futbol pratiğine dayanıyor.",
        f"- Draw kalibrasyon eşikleri: min draw_p={DRAW_PRED_MIN_PROB}, max gap={DRAW_PRED_MAX_GAP}, boost={DRAW_BOOST_SCALE} (draw_calibrated_prediction).",
        "- Canlı kullanım için: HIGH güven → güvenilir sinyal, LOW güven → bilgi amaçlı.",
    ])
    return "\n".join(lines)


def _sort_key(m: dict):
    from src.model_league_predictions import parse_tff_datetime
    return parse_tff_datetime(m["match_date"])


if __name__ == "__main__":
    main()
