"""UEFA Şampiyonlar Ligi, Avrupa Ligi ve Konferans Ligi 2026-27 maç tahminleri.

football-data.org fixtures verisi üzerinden Poisson bazlı tahmin üretir.
Form verisi: turnikedeki geçmiş maçlar + UEFA katsayısı bazlı başlangıç gücü.
Çıktı: data/processed/european_predictions_2026_2027.json
"""
from __future__ import annotations

import json
import math
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from src.config import PROCESSED_DIR, ensure_data_dirs

FIXTURES_PATH = PROCESSED_DIR / "european_fixtures_2026_2027.json"
OUTPUT_PATH   = PROCESSED_DIR / "european_predictions_2026_2027.json"

# ──────────────────────────────────────────────────────────
# UEFA katsayısı bazlı başlangıç güçleri (2024-25 sezonu)
# Kaynak: UEFA club coefficients. Lig ortalaması ≈ 30.
# ──────────────────────────────────────────────────────────
_CLUB_STRENGTH: dict[str, float] = {
    # Tier 1 (80-100)
    "Manchester City":       95, "Real Madrid":          98,
    "Bayern Munich":         92, "Liverpool":            88,
    "Arsenal":               86, "Barcelona":            85,
    "Paris Saint-Germain":   84, "Borussia Dortmund":    80,
    "Atlético de Madrid":    82, "Juventus":             75,
    "Inter Milan":           83, "AC Milan":             76,
    "Chelsea":               78, "Manchester United":    72,
    "Napoli":                74, "Porto":                70,
    "Benfica":               68, "Bayer 04 Leverkusen":  85,
    "Atalanta":              78, "RB Leipzig":           76,
    "Aston Villa":           72, "Feyenoord":            66,
    # Tier 2 (55-70)
    "Sporting CP":           65, "Sevilla FC":           60,
    "BSC Young Boys":        52, "Crvena zvezda":        55,
    "GNK Dinamo Zagreb":     50, "Galatasaray":          62,
    "Fenerbahçe":            60, "Beşiktaş":             52,
    "Trabzonspor":           48, "Başakşehir":           45,
    "Club Brugge":           60, "PSV Eindhoven":        65,
    "Celtic":                58, "Rangers":              55,
    "FC Shakhtar Donetsk":   58, "FC Salzburg":          62,
    "Girona FC":             62, "Real Sociedad":        60,
    "Sturm Graz":            50, "Slavia Praha":         52,
    "Sparta Praha":          54,
}

_DEFAULT_STRENGTH = 45.0
_HOME_ADVANTAGE   = 1.12   # ev avantajı faktörü
_BASE_GOALS       = 1.35   # lig bazı gol/maç (UCL ortalaması)
_DRAW_CALIBRATION = 1.05   # Poisson draw düzeltmesi
_MAX_GOALS        = 8


def _strength(name: str) -> float:
    for k, v in _CLUB_STRENGTH.items():
        if k.lower() in name.lower() or name.lower() in k.lower():
            return v
    return _DEFAULT_STRENGTH


def _att_lambda(team: str, form: dict | None) -> float:
    base = (_strength(team) / 60.0) * _BASE_GOALS
    if form and form.get("played", 0) >= 3:
        form_att = form.get("gf_per_match", base)
        w = min(0.6, form["played"] / 10)
        return base * (1 - w) + form_att * w
    return base


def _def_lambda(team: str, form: dict | None) -> float:
    base = (60.0 / _strength(team)) * _BASE_GOALS
    if form and form.get("played", 0) >= 3:
        form_def = form.get("ga_per_match", base)
        w = min(0.6, form["played"] / 10)
        return base * (1 - w) + form_def * w
    return base


def _poisson_prob(lam: float, k: int) -> float:
    try:
        return math.exp(-lam) * (lam ** k) / math.factorial(k)
    except (OverflowError, ValueError):
        return 0.0


def _win_draw_loss(lam_h: float, lam_a: float) -> tuple[float, float, float]:
    hw = dr = aw = 0.0
    for h in range(_MAX_GOALS + 1):
        ph = _poisson_prob(lam_h, h)
        for a in range(_MAX_GOALS + 1):
            pa = _poisson_prob(lam_a, a)
            p = ph * pa
            if h > a:
                hw += p
            elif h == a:
                dr += p
            else:
                aw += p
    dr *= _DRAW_CALIBRATION
    total = hw + dr + aw
    if total > 0:
        hw /= total; dr /= total; aw /= total
    return round(hw, 3), round(dr, 3), round(aw, 3)


def _score_prediction(lam_h: float, lam_a: float, hw: float, dr: float, aw: float) -> tuple[int, int]:
    ph = round(lam_h)
    pa = round(lam_a)
    if hw >= dr and hw >= aw:
        if ph <= pa:
            ph = pa + 1
    elif dr >= hw and dr >= aw:
        if ph != pa:
            low = min(ph, pa)
            ph = pa = low
    else:
        if pa <= ph:
            pa = ph + 1
    return max(0, ph), max(0, pa)


def _goals_over_2_5(lam_h: float, lam_a: float) -> float:
    under = sum(
        _poisson_prob(lam_h, h) * _poisson_prob(lam_a, a)
        for h in range(_MAX_GOALS + 1)
        for a in range(_MAX_GOALS + 1)
        if h + a <= 2
    )
    return round(1 - under, 3)


def _build_form(matches: list[dict]) -> dict[str, dict]:
    """Geçmiş maç sonuçlarından takım başına form hesaplar."""
    form: dict[str, dict] = defaultdict(lambda: {"played": 0, "gf": 0, "ga": 0})
    for m in matches:
        if m.get("status") != "FINISHED":
            continue
        score = m.get("score", {})
        sh = score.get("home")
        sa = score.get("away")
        if sh is None or sa is None:
            continue
        hn = m.get("home", {}).get("name", "")
        an = m.get("away", {}).get("name", "")
        if hn:
            form[hn]["played"] += 1
            form[hn]["gf"] += sh
            form[hn]["ga"] += sa
        if an:
            form[an]["played"] += 1
            form[an]["gf"] += sa
            form[an]["ga"] += sh
    result = {}
    for team, f in form.items():
        p = f["played"] or 1
        result[team] = {
            "played": f["played"],
            "gf_per_match": round(f["gf"] / p, 3),
            "ga_per_match": round(f["ga"] / p, 3),
        }
    return result


def _enrich_result(pred: dict) -> dict:
    """Oynanan maçların tahmin doğruluğunu işaretle."""
    score = pred.get("actual_score")
    if not score or score.get("home") is None:
        pred["prediction_outcome"] = "pending"
        return pred
    sh, sa = score["home"], score["away"]
    if sh > sa:
        actual = "home"
    elif sh == sa:
        actual = "draw"
    else:
        actual = "away"
    ps = pred["prediction"]["predicted_score"]
    if ps["home"] > ps["away"]:
        predicted = "home"
    elif ps["home"] == ps["away"]:
        predicted = "draw"
    else:
        predicted = "away"
    pred["prediction_outcome"] = "correct" if predicted == actual else "wrong"
    return pred


def analyze_competition(comp: dict) -> dict:
    matches_raw = comp.get("matches", [])
    form = _build_form(matches_raw)

    predictions = []
    correct = wrong = 0
    for m in matches_raw:
        home = m.get("home", {})
        away = m.get("away", {})
        hn = home.get("name", "")
        an = away.get("name", "")

        # Takımlar TBD ise atla
        if not hn or not an:
            predictions.append({
                "match_id": m.get("id"),
                "stage": m.get("stage", ""),
                "group": m.get("group", ""),
                "utc_date": m.get("utc_date", ""),
                "status": m.get("status", "TIMED"),
                "home": home, "away": away,
                "actual_score": None,
                "prediction": None,
                "prediction_outcome": "tbd",
            })
            continue

        lam_h = _att_lambda(hn, form.get(hn)) * _def_lambda(an, form.get(an)) / _BASE_GOALS
        lam_a = _att_lambda(an, form.get(an)) * _def_lambda(hn, form.get(hn)) / _BASE_GOALS
        lam_h = round(max(0.3, lam_h) * _HOME_ADVANTAGE, 3)
        lam_a = round(max(0.3, lam_a), 3)

        hw, dr, aw = _win_draw_loss(lam_h, lam_a)
        ph, pa = _score_prediction(lam_h, lam_a, hw, dr, aw)
        over25 = _goals_over_2_5(lam_h, lam_a)

        score_raw = m.get("score", {})
        sh = score_raw.get("home")
        sa = score_raw.get("away")
        actual_score = {"home": sh, "away": sa} if sh is not None else None

        entry = {
            "match_id": m.get("id"),
            "stage": m.get("stage", ""),
            "group": m.get("group", ""),
            "matchday": m.get("matchday"),
            "utc_date": m.get("utc_date", ""),
            "status": m.get("status", "TIMED"),
            "home": home, "away": away,
            "actual_score": actual_score,
            "prediction": {
                "home_win": hw, "draw": dr, "away_win": aw,
                "predicted_score": {"home": ph, "away": pa},
                "goals_over_2_5": over25,
                "lam_home": lam_h, "lam_away": lam_a,
            },
        }
        entry = _enrich_result(entry)
        if entry["prediction_outcome"] == "correct":
            correct += 1
        elif entry["prediction_outcome"] == "wrong":
            wrong += 1
        predictions.append(entry)

    return {
        "code": comp["code"],
        "short": comp["short"],
        "name": comp["name"],
        "predictions": predictions,
        "accuracy": {
            "finished": correct + wrong,
            "correct": correct,
            "wrong": wrong,
            "pct": round(correct / (correct + wrong) * 100, 1) if (correct + wrong) > 0 else None,
        },
    }


def main() -> None:
    ensure_data_dirs()

    if not FIXTURES_PATH.exists():
        print(f"UYARI: {FIXTURES_PATH} bulunamadı — boş tahmin dosyası oluşturuluyor.")
        payload = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "season": "2026-2027",
            "competitions": {},
        }
        OUTPUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return

    data = json.loads(FIXTURES_PATH.read_text(encoding="utf-8"))
    competitions = data.get("competitions", {})

    results = {}
    for code, comp in competitions.items():
        print(f"\n{comp['name']} analiz ediliyor…", flush=True)
        results[code] = analyze_competition(comp)
        acc = results[code]["accuracy"]
        print(f"  Doğruluk: {acc['correct']}/{acc['finished']} "
              f"({acc['pct']}%)" if acc["pct"] is not None else "  Henüz sonuç yok")

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "season": data.get("season", "2026-2027"),
        "competitions": results,
    }

    OUTPUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nKaydedildi: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
