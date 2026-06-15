"""WC 2026 maç tahminleri — gerçek turnuva form verisiyle güçlendirilmiş Poisson modeli."""
from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path

from src.config import PROCESSED_DIR, ensure_data_dirs

# ---------------------------------------------------------------------------
# Fixture sonuçlarını yükle
# ---------------------------------------------------------------------------

def _load_fixture_results() -> dict[tuple[str, str], dict]:
    """Fixture dosyasından (home_name, away_name) → fixture dict haritası döner."""
    path = PROCESSED_DIR / "worldcup_2026_fixtures.json"
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    result: dict[tuple[str, str], dict] = {}
    for m in data.get("matches", []):
        h = m.get("home", {}).get("name", "")
        a = m.get("away", {}).get("name", "")
        if h and a:
            result[(h, a)] = m
    return result


def _enrich_with_result(prediction: dict, fixtures: dict[tuple[str, str], dict]) -> dict:
    """Tahmine fixture sonucunu ekler. Maç oynanmamışsa pending döner."""
    home_name = prediction["home"]["name"]
    away_name = prediction["away"]["name"]
    fixture = fixtures.get((home_name, away_name))

    if fixture is None or fixture.get("status") != "FINISHED":
        prediction["actual_score"] = None
        prediction["prediction_outcome"] = "pending"
        return prediction

    score = fixture.get("score", {})
    actual_h = score.get("home")
    actual_a = score.get("away")
    prediction["actual_score"] = {"home": actual_h, "away": actual_a}

    if actual_h is None or actual_a is None:
        prediction["prediction_outcome"] = "pending"
        return prediction

    if actual_h > actual_a:
        actual_outcome = "home"
    elif actual_h == actual_a:
        actual_outcome = "draw"
    else:
        actual_outcome = "away"

    pred_score = prediction["prediction"].get("predicted_score", {})
    ps_h = pred_score.get("home")
    ps_a = pred_score.get("away")
    if ps_h is not None and ps_a is not None:
        if ps_h > ps_a:
            predicted_outcome = "home"
        elif ps_h == ps_a:
            predicted_outcome = "draw"
        else:
            predicted_outcome = "away"
    else:
        pred = prediction["prediction"]
        best = max(pred.get("home_win", 0), pred.get("draw", 0), pred.get("away_win", 0))
        if best == pred.get("home_win", 0):
            predicted_outcome = "home"
        elif best == pred.get("draw", 0):
            predicted_outcome = "draw"
        else:
            predicted_outcome = "away"

    prediction["prediction_outcome"] = "correct" if predicted_outcome == actual_outcome else "wrong"
    return prediction

# ---------------------------------------------------------------------------
# Form verisi yükle (Euro 2024, Copa América, AFCON, Asian Cup, WC 2022)
# ---------------------------------------------------------------------------

_FORM_PATH = PROCESSED_DIR / "national_team_form.json"

def _load_form() -> dict[str, dict]:
    if _FORM_PATH.exists():
        data = json.loads(_FORM_PATH.read_text(encoding="utf-8"))
        return data.get("teams", {})
    return {}

TEAM_FORM: dict[str, dict] = _load_form()

# Form verisinden baseline hesapla (ağırlıklı ortalama)
def _compute_baseline() -> tuple[float, float]:
    gf_vals = [t["w_gf_per_match"] for t in TEAM_FORM.values() if t["matches"] >= 3]
    ga_vals = [t["w_ga_per_match"] for t in TEAM_FORM.values() if t["matches"] >= 3]
    if not gf_vals:
        return 1.35, 1.35
    return sum(gf_vals) / len(gf_vals), sum(ga_vals) / len(ga_vals)

_BASELINE_ATT, _BASELINE_DEF = _compute_baseline()

# WC grup aşaması gol ortalaması (2022: 2.69 toplam → 1.35 kişi başı)
WC_BASE = 1.35

# ---------------------------------------------------------------------------
# FIFA güç tablosu — form verisi olmayan takımlar için fallback
# ---------------------------------------------------------------------------
FIFA_STRENGTH: dict[str, int] = {
    "Argentina": 96, "France": 94, "England": 92, "Brazil": 91, "Spain": 90,
    "Portugal": 89, "Belgium": 87, "Netherlands": 86, "Uruguay": 84, "Germany": 83,
    "Colombia": 81, "Croatia": 80, "Switzerland": 79, "United States": 77,
    "Mexico": 76, "Canada": 74, "Japan": 73, "South Korea": 72, "Australia": 70,
    "Turkey": 69, "Morocco": 68, "Ecuador": 66, "Norway": 65, "Senegal": 64,
    "Sweden": 63, "Ivory Coast": 61, "Serbia": 60, "Austria": 59, "Denmark": 58,
    "Iran": 56, "Saudi Arabia": 55, "Scotland": 54, "Ghana": 52, "Tunisia": 51,
    "Egypt": 50, "Czechia": 49, "Poland": 48, "Qatar": 47, "South Africa": 46,
    "Bosnia-Herzegovina": 45, "Paraguay": 44, "Iraq": 43, "Algeria": 42,
    "Jordan": 41, "Panama": 40, "Cape Verde Islands": 38, "Uzbekistan": 37,
    "New Zealand": 35, "Congo DR": 33, "Curaçao": 30, "Haiti": 28,
    "Côte d'Ivoire": 61, "United States of America": 77,
    "Republic of Korea": 72, "IR Iran": 56, "DR Congo": 33,
}


def _lookup_strength(name: str) -> int:
    if name in FIFA_STRENGTH:
        return FIFA_STRENGTH[name]
    name_lower = name.lower()
    for key, val in FIFA_STRENGTH.items():
        if key.lower() in name_lower or name_lower in key.lower():
            return val
    return 50


def _get_form(name: str) -> dict | None:
    """Takımın form verisini döner; alias deneyerek bulur."""
    if name in TEAM_FORM:
        return TEAM_FORM[name]
    # Kısmi eşleşme
    name_l = name.lower()
    for key, val in TEAM_FORM.items():
        if key.lower() in name_l or name_l in key.lower():
            return val
    return None


def _att_lambda(name: str) -> float:
    """Hücum lambdası: form verisi ile FIFA prior blending (WC_BASE ölçekli)."""
    s = _lookup_strength(name)
    fifa_val = WC_BASE * (0.55 + (s / 100.0) * 0.9)
    form = _get_form(name)
    if form and form["matches"] >= 3:
        form_val = WC_BASE * (form["w_gf_per_match"] / _BASELINE_ATT)
        # Maç sayısı arttıkça forma ağırlığı artar (max %65)
        w = min(0.65, form["matches"] / 12 * 0.9)
        return max(0.5, round(w * form_val + (1 - w) * fifa_val, 3))
    return max(0.5, round(fifa_val, 3))


def _def_lambda(name: str) -> float:
    """Savunma lambdası: düşük = iyi savunma (rakibe bırakılan gol, WC_BASE ölçekli)."""
    s = _lookup_strength(name)
    fifa_val = WC_BASE * (1.5 - (s / 100.0) * 0.9)
    form = _get_form(name)
    if form and form["matches"] >= 3:
        form_val = WC_BASE * (form["w_ga_per_match"] / _BASELINE_DEF)
        w = min(0.65, form["matches"] / 12 * 0.9)
        return max(0.35, round(w * form_val + (1 - w) * fifa_val, 3))
    return max(0.35, round(fifa_val, 3))


# ---------------------------------------------------------------------------
# Poisson yardımcıları
# ---------------------------------------------------------------------------

def _pmf(lam: float, k: int) -> float:
    if lam <= 0:
        return 1.0 if k == 0 else 0.0
    return math.exp(-lam) * (lam ** k) / math.factorial(k)


def _win_draw_loss(lam_h: float, lam_a: float, max_g: int = 9) -> tuple[float, float, float]:
    """Poisson dağılımından kazanma/beraberlik/kaybetme olasılığı."""
    ph = pd = pa = 0.0
    for h in range(max_g + 1):
        for a in range(max_g + 1):
            p = _pmf(lam_h, h) * _pmf(lam_a, a)
            if h > a:
                ph += p
            elif h == a:
                pd += p
            else:
                pa += p
    total = ph + pd + pa
    return round(ph / total, 3), round(pd / total, 3), round(pa / total, 3)


def _score_prediction(lam_h: float, lam_a: float, hw: float, aw: float) -> tuple[int, int]:
    h = max(0, round(lam_h))
    a = max(0, round(lam_a))
    if hw > 0.50 and h <= a:
        h = a + 1
    elif aw > 0.50 and a <= h:
        a = h + 1
    return h, a


def _goals_over_2_5(lam_h: float, lam_a: float) -> float:
    p_under = sum(
        _pmf(lam_h, h) * _pmf(lam_a, t - h)
        for t in range(3)
        for h in range(t + 1)
    )
    return round(1.0 - p_under, 3)


def _expected_cards(home_name: str, away_name: str) -> float:
    hs = _lookup_strength(home_name)
    as_ = _lookup_strength(away_name)
    base = 3.5
    if hs >= 70 and as_ >= 70:
        base += 0.5
    if abs(hs - as_) > 25:
        base -= 0.3
    return round(base, 1)


# ---------------------------------------------------------------------------
# Narrative
# ---------------------------------------------------------------------------

def _narrative(
    home: str, away: str,
    lam_h: float, lam_a: float,
    hw: float, aw: float,
    cards: float,
    pred_h: int, pred_a: int,
    home_form: dict | None, away_form: dict | None,
) -> str:
    diff = hw - aw
    if diff > 0.35:
        strong, weak = home, away
        base = f"{strong} belirgin favori"
    elif diff < -0.35:
        strong, weak = away, home
        base = f"{strong} (deplasman) belirgin favori"
    else:
        base = "Dengeli bir karşılaşma bekleniyor"

    parts = [base + "."]

    if home_form and home_form["matches"] >= 3:
        parts.append(
            f"{home}, son {home_form['matches']} maçta %{round(home_form['win_rate']*100)} galibiyet "
            f"ve maç başı {home_form['w_gf_per_match']:.2f} gol ortalamasıyla geliyor."
        )
    if away_form and away_form["matches"] >= 3:
        parts.append(
            f"{away}, {away_form['matches']} maçta %{round(away_form['win_rate']*100)} galibiyet "
            f"ve {away_form['w_gf_per_match']:.2f} gol/maç ile sahaya çıkıyor."
        )

    parts.append(
        f"Gol beklentisi: ev {lam_h:.2f} — dep {lam_a:.2f}. "
        f"En olası skor: {pred_h}-{pred_a}. Tahmini kart: ~{cards}."
    )

    return " ".join(parts)


# ---------------------------------------------------------------------------
# Ana analiz
# ---------------------------------------------------------------------------

def analyze_match(match: dict) -> dict:
    home = match.get("home", {})
    away = match.get("away", {})
    home_name = home.get("name", "")
    away_name = away.get("name", "")

    home_form = _get_form(home_name)
    away_form = _get_form(away_name)

    # Çarpımsal model: att * def_zayıflığı / WC_BASE (bölme DEĞİL çarpma)
    lam_h = _att_lambda(home_name) * _def_lambda(away_name) / WC_BASE
    lam_a = _att_lambda(away_name) * _def_lambda(home_name) / WC_BASE
    lam_h = max(0.4, round(lam_h, 3))
    lam_a = max(0.4, round(lam_a, 3))

    hw, dr, aw = _win_draw_loss(lam_h, lam_a)
    pred_h, pred_a = _score_prediction(lam_h, lam_a, hw, aw)
    over_25 = _goals_over_2_5(lam_h, lam_a)
    cards = _expected_cards(home_name, away_name)
    narr = _narrative(home_name, away_name, lam_h, lam_a, hw, aw, cards, pred_h, pred_a, home_form, away_form)

    return {
        "match_id": match.get("id"),
        "matchday": match.get("matchday"),
        "group": match.get("group", ""),
        "utc_date": match.get("utc_date", ""),
        "home": {
            "name": home_name,
            "short": home.get("short", ""),
            "crest": home.get("crest", ""),
            "strength": _lookup_strength(home_name),
            "data_source": "form" if (home_form and home_form["matches"] >= 3) else "ranking",
        },
        "away": {
            "name": away_name,
            "short": away.get("short", ""),
            "crest": away.get("crest", ""),
            "strength": _lookup_strength(away_name),
            "data_source": "form" if (away_form and away_form["matches"] >= 3) else "ranking",
        },
        "prediction": {
            "home_win": hw,
            "draw": dr,
            "away_win": aw,
            "predicted_score": {"home": pred_h, "away": pred_a},
            "goals_over_2_5": over_25,
            "expected_cards": cards,
            "narrative": narr,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="WC 2026 maçları için tahmin üretir.")
    parser.add_argument("--fixtures", default=str(PROCESSED_DIR / "worldcup_2026_fixtures.json"))
    parser.add_argument("--output", default=str(PROCESSED_DIR / "worldcup_2026_predictions.json"))
    args = parser.parse_args()

    ensure_data_dirs()

    fixtures_path = Path(args.fixtures)
    if not fixtures_path.exists():
        print(f"HATA: {fixtures_path} bulunamadı. Önce collect_worldcup_fixtures çalıştırın.")
        raise SystemExit(1)

    data = json.loads(fixtures_path.read_text(encoding="utf-8"))
    matches: list[dict] = data.get("matches", [])

    group_matches = [
        m for m in matches
        if m.get("matchday") and m.get("matchday") > 0
        and m.get("home", {}).get("name")
        and m.get("away", {}).get("name")
    ]

    form_count = len(TEAM_FORM)
    print(f"Form verisi: {form_count} takım (baseline att={_BASELINE_ATT:.3f} def={_BASELINE_DEF:.3f})")
    print(f"{len(group_matches)} grup aşaması maçı analiz ediliyor…", flush=True)

    fixtures = _load_fixture_results()
    print(f"Fixture sonuçları: {sum(1 for f in fixtures.values() if f.get('status') == 'FINISHED')} maç tamamlandı", flush=True)

    matchday_predictions: dict[str, list] = {}
    for match in group_matches:
        prediction = analyze_match(match)
        prediction = _enrich_with_result(prediction, fixtures)
        md_key = str(match.get("matchday"))
        matchday_predictions.setdefault(md_key, []).append(prediction)

    for md_key in matchday_predictions:
        matchday_predictions[md_key].sort(key=lambda m: m.get("utc_date", ""))

    # Genel doğruluk istatistikleri
    all_preds = [p for plist in matchday_predictions.values() for p in plist]
    finished = [p for p in all_preds if p["prediction_outcome"] != "pending"]
    correct = [p for p in finished if p["prediction_outcome"] == "correct"]
    accuracy_stats = {
        "finished": len(finished),
        "correct": len(correct),
        "wrong": len(finished) - len(correct),
        "accuracy_pct": round(len(correct) / len(finished) * 100, 1) if finished else None,
    }
    print(f"Doğruluk: {len(correct)}/{len(finished)} ({accuracy_stats['accuracy_pct']}%)", flush=True)

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_matches": len(matches),
        "form_teams_used": form_count,
        "accuracy_stats": accuracy_stats,
        "matchday_predictions": matchday_predictions,
    }

    out_path = Path(args.output)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Kaydedildi: {out_path}", flush=True)
    print(f"Matchday sayısı: {len(matchday_predictions)}", flush=True)


if __name__ == "__main__":
    main()
