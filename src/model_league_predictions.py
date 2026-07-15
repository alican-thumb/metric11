from __future__ import annotations

import argparse
import json
import math
from collections import Counter, defaultdict, deque
from datetime import datetime
from pathlib import Path

from src.config import PROCESSED_DIR
from src.normalization import normalize_matches
from src.preview.probability import head_to_head_draw_signal


def main() -> None:
    parser = argparse.ArgumentParser(description="Lig geneli kronolojik Poisson/Elo MVP tahmin modeli backtest uretir.")
    parser.add_argument("--input", default=str(PROCESSED_DIR / "tff_super_lig_enriched_2025_2026.json"))
    parser.add_argument("--output-prefix", default="league_prediction_model_2025_2026")
    parser.add_argument("--min-team-history", type=int, default=5)
    args = parser.parse_args()

    matches = normalize_matches(json.loads(Path(args.input).read_text(encoding="utf-8")))
    matches.sort(key=lambda match: parse_tff_datetime(match["match_date"]))
    payload = run_backtest(matches, args.min_team_history)

    json_path = PROCESSED_DIR / f"{args.output_prefix}.json"
    md_path = PROCESSED_DIR / f"{args.output_prefix}.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(build_markdown(payload), encoding="utf-8")
    print(md_path.read_text(encoding="utf-8"))


LEAGUE_AVG_CARDS = 4.67
LEAGUE_AVG_GOALS = 2.65
MIN_REFEREE_MATCHES = 4

DRAW_PRED_MIN_PROB = 0.26   # draw olasılığı bu eşiğin altındaysa beraberlik tahmin edilmez
DRAW_PRED_MAX_GAP = 0.18    # en iyi yönsel tahmin ile draw arasındaki maksimum fark (0.14→0.18: recall %29→%41)
DRAW_BOOST_SCALE = 0.12     # dengeli maçlarda draw olasılığına uygulanacak boost katsayısı


def draw_calibrated_prediction(home_p: float, draw_p: float, away_p: float, strength_edge: float = 0.0) -> str:
    """
    Poisson modeli draw olasılığını sistematik olarak düşük üretir (~0.24 ort,
    gerçek lig oranı ~0.295). Dengeli maçlarda (düşük strength_edge) draw
    olasılığını DRAW_BOOST_SCALE ile yukarı kalibre eder, ardından
    DRAW_PRED_MIN_PROB ve DRAW_PRED_MAX_GAP eşiklerini uygular.
    Backtest: recall %8 → %29, genel doğruluk %50.8 → %51.6.
    """
    balance = 1.0 / (1 + abs(strength_edge) * 3)
    dp_boosted = draw_p * (1 + DRAW_BOOST_SCALE * balance)
    total = home_p + dp_boosted + away_p
    home_p2, draw_p2, away_p2 = home_p / total, dp_boosted / total, away_p / total

    probs = {"home": home_p2, "draw": draw_p2, "away": away_p2}
    raw_winner = max(probs, key=probs.__getitem__)
    if raw_winner == "draw":
        return "draw"
    top_directional = max(home_p2, away_p2)
    if draw_p2 >= DRAW_PRED_MIN_PROB and (top_directional - draw_p2) <= DRAW_PRED_MAX_GAP:
        return "draw"
    return raw_winner


def run_backtest(matches: list[dict], min_team_history: int) -> dict:
    team_history = defaultdict(lambda: deque(maxlen=8))
    referee_history: dict[str, list[dict]] = defaultdict(list)
    elo = defaultdict(lambda: 1500.0)
    rows = []

    for match in matches:
        home = match["home_team"]["name"]
        away = match["away_team"]["name"]
        home_goals = match["home_team"]["score"] or 0
        away_goals = match["away_team"]["score"] or 0
        home_history = list(team_history[home])
        away_history = list(team_history[away])
        main_ref = _main_referee(match)
        ref_stats = _referee_stats(referee_history, main_ref)

        prediction = None
        if len(home_history) >= min_team_history and len(away_history) >= min_team_history:
            prediction = predict_match(home, away, home_history, away_history, elo[home], elo[away], ref_stats)
            actual = actual_result(home_goals, away_goals)
            home_p = prediction["home_win_probability"]
            draw_p = prediction["draw_probability"]
            away_p = prediction["away_win_probability"]
            raw_predicted = max({"home": home_p, "draw": draw_p, "away": away_p}, key=lambda k: {"home": home_p, "draw": draw_p, "away": away_p}[k])
            predicted = draw_calibrated_prediction(home_p, draw_p, away_p, prediction.get("strength_edge", 0.0))
            rows.append(
                {
                    "match_id": match["external_id"],
                    "date": match["match_date"],
                    "home": home,
                    "away": away,
                    "score": f"{home_goals}-{away_goals}",
                    "raw_predicted": raw_predicted,
                    "predicted": predicted,
                    "actual": actual,
                    "correct": predicted == actual,
                    "confidence": confidence_label(prediction),
                    "risk_flags": risk_flags(prediction),
                    "main_referee": main_ref,
                    **prediction,
                }
            )

        ss = match.get("sofascore_stats") or {}
        total_cards = len(match["cards"]["home"]) + len(match["cards"]["away"])
        if main_ref:
            referee_history[main_ref].append({"cards": total_cards, "goals": home_goals + away_goals})
        update_history(team_history, home, home_goals, away_goals, len(match["cards"]["home"]), is_home=True, xg_for=ss.get("xg_home"), xg_against=ss.get("xg_away"))
        update_history(team_history, away, away_goals, home_goals, len(match["cards"]["away"]), is_home=False, xg_for=ss.get("xg_away"), xg_against=ss.get("xg_home"))
        update_elo(elo, home, away, home_goals, away_goals)

    summary = summarize(rows)
    return {"summary": summary, "rows": rows}


def compute_final_state(matches: list[dict]) -> dict:
    """run_backtest ile aynı kronolojik birikimi yapar, yalnızca son team_history/elo/hakem
    durumunu döner. Henüz oynanmamış (gelecek sezon) fikstürleri tahmin etmek için kullanılır.
    """
    team_history = defaultdict(lambda: deque(maxlen=8))
    referee_history: dict[str, list[dict]] = defaultdict(list)
    elo = defaultdict(lambda: 1500.0)

    for match in matches:
        home = match["home_team"]["name"]
        away = match["away_team"]["name"]
        home_goals = match["home_team"]["score"] or 0
        away_goals = match["away_team"]["score"] or 0
        main_ref = _main_referee(match)

        ss = match.get("sofascore_stats") or {}
        total_cards = len(match["cards"]["home"]) + len(match["cards"]["away"])
        if main_ref:
            referee_history[main_ref].append({"cards": total_cards, "goals": home_goals + away_goals})
        update_history(team_history, home, home_goals, away_goals, len(match["cards"]["home"]), is_home=True, xg_for=ss.get("xg_home"), xg_against=ss.get("xg_away"))
        update_history(team_history, away, away_goals, home_goals, len(match["cards"]["away"]), is_home=False, xg_for=ss.get("xg_away"), xg_against=ss.get("xg_home"))
        update_elo(elo, home, away, home_goals, away_goals)

    return {"team_history": team_history, "elo": elo, "referee_history": referee_history}


def _main_referee(match: dict) -> str | None:
    for official in (match.get("officials") or []):
        if official.get("role") == "Hakem":
            return official.get("name")
    return None


def _referee_stats(referee_history: dict, name: str | None) -> dict | None:
    if not name:
        return None
    history = referee_history.get(name, [])
    if len(history) < MIN_REFEREE_MATCHES:
        return None
    cards_per_match = sum(h["cards"] for h in history) / len(history)
    goals_per_match = sum(h["goals"] for h in history) / len(history)
    return {
        "name": name,
        "matches": len(history),
        "cards_per_match": round(cards_per_match, 2),
        "goals_per_match": round(goals_per_match, 2),
    }


def _referee_goal_adjustment(ref_stats: dict | None) -> float:
    if not ref_stats:
        return 0.0
    card_effect = (LEAGUE_AVG_CARDS - ref_stats["cards_per_match"]) * 0.018
    goal_effect = (ref_stats["goals_per_match"] - LEAGUE_AVG_GOALS) * 0.04
    return max(-0.10, min(0.10, card_effect + goal_effect))


def predict_match(home: str, away: str, home_history: list[dict], away_history: list[dict], home_elo: float, away_elo: float, ref_stats: dict | None = None) -> dict:
    league_home_boost = 0.18
    home_gf = avg(item["goals_for"] for item in home_history)
    home_ga = avg(item["goals_against"] for item in home_history)
    away_gf = avg(item["goals_for"] for item in away_history)
    away_ga = avg(item["goals_against"] for item in away_history)
    home_ppg = avg(item["points"] for item in home_history)
    away_ppg = avg(item["points"] for item in away_history)
    home_gd = avg(item["goals_for"] - item["goals_against"] for item in home_history)
    away_gd = avg(item["goals_for"] - item["goals_against"] for item in away_history)
    home_clean = avg(1 if item["goals_against"] == 0 else 0 for item in home_history)
    away_clean = avg(1 if item["goals_against"] == 0 else 0 for item in away_history)
    home_blank = avg(1 if item["goals_for"] == 0 else 0 for item in home_history)
    away_blank = avg(1 if item["goals_for"] == 0 else 0 for item in away_history)

    # Sofascore xG: 60/40 blend ile gol ortalamasını düzelt (en az 3 xG kayıtlı maç gerekli)
    home_xg_vals = [item["xg_for"] for item in home_history if item.get("xg_for") is not None]
    home_xga_vals = [item["xg_against"] for item in home_history if item.get("xg_against") is not None]
    away_xg_vals = [item["xg_for"] for item in away_history if item.get("xg_for") is not None]
    away_xga_vals = [item["xg_against"] for item in away_history if item.get("xg_against") is not None]
    home_gf_eff = (0.6 * avg(home_xg_vals) + 0.4 * home_gf) if len(home_xg_vals) >= 3 else home_gf
    home_ga_eff = (0.6 * avg(home_xga_vals) + 0.4 * home_ga) if len(home_xga_vals) >= 3 else home_ga
    away_gf_eff = (0.6 * avg(away_xg_vals) + 0.4 * away_gf) if len(away_xg_vals) >= 3 else away_gf
    away_ga_eff = (0.6 * avg(away_xga_vals) + 0.4 * away_ga) if len(away_xga_vals) >= 3 else away_ga
    home_xg_efficiency = avg(home_xg_vals) / home_gf if home_gf and len(home_xg_vals) >= 3 else None
    away_xg_efficiency = avg(away_xg_vals) / away_gf if away_gf and len(away_xg_vals) >= 3 else None

    expected_home = max(0.15, (home_gf_eff * 0.58 + away_ga_eff * 0.42) + league_home_boost)
    expected_away = max(0.15, away_gf_eff * 0.58 + home_ga_eff * 0.42)
    strength_edge = ((home_ppg - away_ppg) * 0.24) + ((home_gd - away_gd) * 0.16)
    # League-wide backtests are noisier than the Beşiktaş-focused preview model, so keep this as a
    # mild calibration signal instead of letting short-form strength dominate xG.
    expected_home += strength_edge * 0.05 + max(0, home_clean - away_clean) * 0.03 - max(0, home_blank - away_blank) * 0.04
    expected_away -= strength_edge * 0.04 + max(0, home_clean - away_clean) * 0.025 - max(0, home_blank - away_blank) * 0.03

    elo_delta = (home_elo - away_elo) / 400
    expected_home *= max(0.75, min(1.25, 1 + elo_delta * 0.12))
    expected_away *= max(0.75, min(1.25, 1 - elo_delta * 0.12))

    # Hakem etkisi: kart profili ve gol temposu beklenen golü hafifçe ayarlar
    ref_adj = _referee_goal_adjustment(ref_stats)
    expected_home = max(0.15, expected_home + ref_adj)
    expected_away = max(0.15, expected_away + ref_adj)

    probs = poisson_result_probs(expected_home, expected_away)

    # Kafa kafaya (h2h) tarihsel beraberlik oranı: gerçek geçmiş sonuçlara dayanan bir
    # prior olarak draw olasılığına karıştırılır (bkz. collect_head_to_head_history.py).
    head_to_head = head_to_head_draw_signal(home, away)
    if head_to_head.get("available"):
        h2h_weight = min(0.35, 0.12 + head_to_head["matches"] * 0.01)
        boosted_draw = probs["draw"] * (1 - h2h_weight) + head_to_head["draw_rate"] * h2h_weight
        total = probs["home"] + boosted_draw + probs["away"]
        probs = {"home": probs["home"] / total, "draw": boosted_draw / total, "away": probs["away"] / total}

    scorelines = scoreline_probs(expected_home, expected_away)
    return {
        "expected_home_goals": round(expected_home, 2),
        "expected_away_goals": round(expected_away, 2),
        "top_scorelines": scorelines[:5],
        "recommended_scoreline": scorelines[0],
        "home_win_probability": round(probs["home"], 3),
        "draw_probability": round(probs["draw"], 3),
        "away_win_probability": round(probs["away"], 3),
        "head_to_head": head_to_head,
        "home_elo": round(home_elo, 1),
        "away_elo": round(away_elo, 1),
        "home_points_per_match": round(home_ppg, 2),
        "away_points_per_match": round(away_ppg, 2),
        "strength_edge": round(strength_edge, 3),
        "home_xg_efficiency": round(home_xg_efficiency, 3) if home_xg_efficiency is not None else None,
        "away_xg_efficiency": round(away_xg_efficiency, 3) if away_xg_efficiency is not None else None,
        "referee_adj": round(ref_adj, 3),
        "referee_cards_per_match": ref_stats["cards_per_match"] if ref_stats else None,
        "referee_goals_per_match": ref_stats["goals_per_match"] if ref_stats else None,
    }


def poisson_result_probs(home_xg: float, away_xg: float, max_goals: int = 7) -> dict:
    probs = Counter()
    for h in range(max_goals + 1):
        for a in range(max_goals + 1):
            p = poisson_pmf(h, home_xg) * poisson_pmf(a, away_xg)
            if h > a:
                probs["home"] += p
            elif h == a:
                probs["draw"] += p
            else:
                probs["away"] += p
    total = probs["home"] + probs["draw"] + probs["away"]
    return {key: probs[key] / total for key in ("home", "draw", "away")}


def scoreline_probs(home_xg: float, away_xg: float, max_goals: int = 5) -> list[dict]:
    rows = []
    for h in range(max_goals + 1):
        for a in range(max_goals + 1):
            rows.append(
                {
                    "score": f"{h}-{a}",
                    "home_goals": h,
                    "away_goals": a,
                    "probability": round(poisson_pmf(h, home_xg) * poisson_pmf(a, away_xg), 3),
                }
            )
    return sorted(rows, key=lambda item: item["probability"], reverse=True)


def poisson_pmf(k: int, lam: float) -> float:
    return math.exp(-lam) * lam**k / math.factorial(k)


def update_history(team_history, team: str, gf: int, ga: int, cards: int, is_home: bool, xg_for: float | None = None, xg_against: float | None = None) -> None:
    points = 3 if gf > ga else 1 if gf == ga else 0
    team_history[team].append({"goals_for": gf, "goals_against": ga, "cards": cards, "is_home": is_home, "points": points, "xg_for": xg_for, "xg_against": xg_against})


def update_elo(elo, home: str, away: str, home_goals: int, away_goals: int) -> None:
    k = 24
    home_advantage = 60
    expected_home = 1 / (1 + 10 ** ((elo[away] - (elo[home] + home_advantage)) / 400))
    actual_home = 1.0 if home_goals > away_goals else 0.5 if home_goals == away_goals else 0.0
    goal_margin = abs(home_goals - away_goals)
    margin_factor = 1 + min(goal_margin, 4) * 0.12
    change = k * margin_factor * (actual_home - expected_home)
    elo[home] += change
    elo[away] -= change


def summarize(rows: list[dict]) -> dict:
    if not rows:
        return {"matches": 0}
    correct = sum(1 for row in rows if row["correct"])
    by_actual = Counter(row["actual"] for row in rows)
    by_pred = Counter(row["predicted"] for row in rows)
    by_confidence = {}
    for label in ("HIGH", "MEDIUM", "LOW"):
        items = [row for row in rows if row["confidence"] == label]
        by_confidence[label] = {
            "matches": len(items),
            "accuracy": round(sum(1 for row in items if row["correct"]) / len(items), 3) if items else 0,
        }
    return {
        "matches": len(rows),
        "correct": correct,
        "accuracy": round(correct / len(rows), 3),
        "actual_distribution": dict(by_actual),
        "prediction_distribution": dict(by_pred),
        "avg_top_probability": round(avg(max(row["home_win_probability"], row["draw_probability"], row["away_win_probability"]) for row in rows), 3),
        "brier_score": round(avg(brier_score(row) for row in rows), 3),
        "log_loss": round(avg(log_loss(row) for row in rows), 3),
        "confidence_breakdown": by_confidence,
    }


def actual_result(home_goals: int, away_goals: int) -> str:
    if home_goals > away_goals:
        return "home"
    if home_goals == away_goals:
        return "draw"
    return "away"


def avg(values) -> float:
    values = list(values)
    return sum(values) / len(values) if values else 0


def confidence_label(prediction: dict) -> str:
    probabilities = [
        prediction["home_win_probability"],
        prediction["draw_probability"],
        prediction["away_win_probability"],
    ]
    probabilities.sort(reverse=True)
    top_probability = probabilities[0]
    margin = probabilities[0] - probabilities[1]
    if top_probability >= 0.52 and margin >= 0.16:
        return "HIGH"
    if top_probability >= 0.43 and margin >= 0.08:
        return "MEDIUM"
    return "LOW"


def risk_flags(prediction: dict) -> list[str]:
    flags = []
    expected_margin = abs(prediction["expected_home_goals"] - prediction["expected_away_goals"])
    if expected_margin < 0.25:
        flags.append("xG farkı dar")
    if prediction["draw_probability"] >= 0.27:
        flags.append("beraberlik olasılığı canlı")
    if max(prediction["home_win_probability"], prediction["away_win_probability"]) < 0.44:
        flags.append("taraf tahmini düşük güven")
    # Favori takım xG'sini gole çeviremiyor: draw riski artar
    home_favored = prediction["expected_home_goals"] > prediction["expected_away_goals"]
    fav_eff = prediction.get("home_xg_efficiency") if home_favored else prediction.get("away_xg_efficiency")
    if fav_eff is not None and fav_eff > 1.35:
        flags.append("favori xG israfı")
    # Hakem kart profili: yüksek kart hakemi kart beklentisini artırır
    ref_cards = prediction.get("referee_cards_per_match")
    if ref_cards is not None and ref_cards > 5.5:
        flags.append("yüksek kart hakemi")
    return flags


def brier_score(row: dict) -> float:
    probs = {
        "home": row["home_win_probability"],
        "draw": row["draw_probability"],
        "away": row["away_win_probability"],
    }
    return sum((probs[key] - (1 if row["actual"] == key else 0)) ** 2 for key in probs)


def log_loss(row: dict) -> float:
    probs = {
        "home": row["home_win_probability"],
        "draw": row["draw_probability"],
        "away": row["away_win_probability"],
    }
    probability = max(0.001, min(0.999, probs[row["actual"]]))
    return -math.log(probability)


def parse_tff_datetime(value: str) -> datetime:
    return datetime.strptime(value.replace(" - ", " ").strip(), "%d.%m.%Y %H:%M")


def build_markdown(payload: dict) -> str:
    summary = payload["summary"]
    lines = [
        "# Lig Geneli Poisson/Elo MVP Backtest",
        "",
        f"- Test edilen maç: {summary.get('matches', 0)}",
        f"- Doğru tahmin: {summary.get('correct', 0)} (%{round(summary.get('accuracy', 0) * 100)})",
        f"- Gerçek dağılım: {summary.get('actual_distribution', {})}",
        f"- Tahmin dağılımı: {summary.get('prediction_distribution', {})}",
        f"- Ortalama en yüksek olasılık: {summary.get('avg_top_probability', 0)}",
        f"- Brier skoru: {summary.get('brier_score', 0)}",
        f"- Log loss: {summary.get('log_loss', 0)}",
        f"- Güven kırılımı: {summary.get('confidence_breakdown', {})}",
        "",
        "## Son 40 Tahmin",
        "",
    ]
    labels = {"home": "Ev", "draw": "X", "away": "Dep"}
    for row in payload["rows"][-40:]:
        lines.append(
            f"- {row['date']} | {row['home']} - {row['away']} | skor {row['score']} | "
            f"tahmin={labels[row['predicted']]} gerçek={labels[row['actual']]} doğru={row['correct']} | "
            f"xG {row['expected_home_goals']}-{row['expected_away_goals']} | skor={row.get('recommended_scoreline', {}).get('score')} | güven={row['confidence']} | "
            f"risk={', '.join(row['risk_flags']) if row['risk_flags'] else '-'}"
        )
    return "\n".join(lines)


if __name__ == "__main__":
    main()
