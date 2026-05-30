"""Analyze WC 2026 fixtures and generate match predictions."""
from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path

from src.config import PROCESSED_DIR, ensure_data_dirs

# ---------------------------------------------------------------------------
# FIFA güç tablosu (0-100, UEFA Elo benzeri skala)
# ---------------------------------------------------------------------------
FIFA_STRENGTH: dict[str, int] = {
    "Argentina": 96,
    "France": 94,
    "England": 92,
    "Brazil": 91,
    "Spain": 90,
    "Portugal": 89,
    "Belgium": 87,
    "Netherlands": 86,
    "Uruguay": 84,
    "Germany": 83,
    "Colombia": 81,
    "Croatia": 80,
    "Switzerland": 79,
    "United States": 77,
    "Mexico": 76,
    "Canada": 74,
    "Japan": 73,
    "South Korea": 72,
    "Australia": 70,
    "Turkey": 69,
    "Morocco": 68,
    "Ecuador": 66,
    "Norway": 65,
    "Senegal": 64,
    "Sweden": 63,
    "Ivory Coast": 61,
    "Serbia": 60,
    "Austria": 59,
    "Denmark": 58,
    "Iran": 56,
    "Saudi Arabia": 55,
    "Scotland": 54,
    "Ghana": 52,
    "Tunisia": 51,
    "Egypt": 50,
    "Czechia": 49,
    "Poland": 48,
    "Qatar": 47,
    "South Africa": 46,
    "Bosnia-Herzegovina": 45,
    "Paraguay": 44,
    "Iraq": 43,
    "Algeria": 42,
    "Jordan": 41,
    "Panama": 40,
    "Cape Verde Islands": 38,
    "Uzbekistan": 37,
    "New Zealand": 35,
    "Congo DR": 33,
    "Curaçao": 30,
    "Haiti": 28,
    # aliases
    "Côte d'Ivoire": 61,
    "United States of America": 77,
    "Republic of Korea": 72,
    "IR Iran": 56,
    "DR Congo": 33,
}

# Varsayılan güç (bilinmeyen takım)
_DEFAULT_STRENGTH = 50


def _lookup_strength(name: str) -> int:
    """Takım adını arar; bulamazsa kısmi eşleşme dener, sonunda default döner."""
    if name in FIFA_STRENGTH:
        return FIFA_STRENGTH[name]
    # Kısmi eşleşme
    name_lower = name.lower()
    for key, val in FIFA_STRENGTH.items():
        if key.lower() in name_lower or name_lower in key.lower():
            return val
    return _DEFAULT_STRENGTH


# ---------------------------------------------------------------------------
# Tahmin modeli
# ---------------------------------------------------------------------------

def win_prob(strength_a: int, strength_b: int) -> tuple[float, float, float]:
    """Ev sahibi kazanma, beraberlik ve deplasman kazanma olasılıklarını döner."""
    diff = (strength_a - strength_b) / 20.0
    p_a = 1 / (1 + 10 ** (-diff))
    draw_base = 0.26 - abs(strength_a - strength_b) * 0.003
    draw = max(0.10, min(0.32, draw_base))
    p_a_adj = p_a * (1 - draw)
    p_b_adj = (1 - p_a) * (1 - draw)
    return round(p_a_adj, 3), round(draw, 3), round(p_b_adj, 3)


def expected_goals(strength_att: int, strength_def: int) -> float:
    """Gol beklentisi (Poisson lambda). WC grup aşaması ortalaması ~2.6 toplam gol."""
    base = 1.35
    att_factor = 0.6 + (strength_att / 100.0) * 0.8
    def_factor = 1.4 - (strength_def / 100.0) * 0.8
    return max(0.5, round(base * att_factor * def_factor, 2))


def _poisson_pmf(lam: float, k: int) -> float:
    """P(X=k) for Poisson(lambda)."""
    if lam <= 0:
        return 1.0 if k == 0 else 0.0
    return math.exp(-lam) * (lam ** k) / math.factorial(k)


def score_prediction(lam_home: float, lam_away: float, home_win_p: float, away_win_p: float) -> tuple[int, int]:
    """Anlamlı skor tahmini: round(lambda) + sonuç tutarlılığı."""
    h = max(0, round(lam_home))
    a = max(0, round(lam_away))
    # Kazananın skoru yansıtılsın
    if home_win_p > 0.50 and h <= a:
        h = a + 1
    elif away_win_p > 0.50 and a <= h:
        a = h + 1
    return h, a


def goals_over_2_5(lam_home: float, lam_away: float) -> float:
    """P(toplam gol > 2.5)."""
    p_under = 0.0
    for total in range(3):  # 0, 1, 2
        for h in range(total + 1):
            a = total - h
            p_under += _poisson_pmf(lam_home, h) * _poisson_pmf(lam_away, a)
    return round(1.0 - p_under, 3)


def expected_cards(strength_home: int, strength_away: int) -> float:
    """Tahmini kart sayısı."""
    base = 3.5
    # Her iki takım da güçlüyse (+0.5)
    if strength_home >= 70 and strength_away >= 70:
        base += 0.5
    # Büyük güç farkı varsa zayıf takım daha az kart (savunmada kalır)
    diff = abs(strength_home - strength_away)
    if diff > 25:
        base -= 0.3
    return round(base, 1)


def _narrative(
    home_name: str,
    away_name: str,
    home_str: int,
    away_str: int,
    lam_home: float,
    lam_away: float,
    cards: float,
    pred_home: int,
    pred_away: int,
) -> str:
    """Türkçe rule-based açıklama üret."""
    diff = home_str - away_str
    abs_diff = abs(diff)
    strong = home_name if diff >= 0 else away_name
    weak = away_name if diff >= 0 else home_name

    if abs_diff > 30:
        base = f"{strong}, FIFA güç endeksinde tartışmasız favori; {weak} savunmada kalacak."
    elif abs_diff >= 15:
        base = f"{strong} avantajlı, ancak sürpriz ihtimal dışı değil."
    else:
        base = f"Dengeli bir karşılaşma bekleniyor; her iki takım da gol şansı yaratacak."

    gol_text = (
        f"Ev sahibi {lam_home:.2f}, deplasman {lam_away:.2f} gol beklentisiyle sahaya çıkıyor. "
        f"En olası sonuç {pred_home}-{pred_away}."
    )
    kart_text = f"Maçta yaklaşık {cards} kart bekleniyor."

    return f"{base} {gol_text} {kart_text}"


# ---------------------------------------------------------------------------
# Ana analiz
# ---------------------------------------------------------------------------

def analyze_match(match: dict) -> dict:
    home = match.get("home", {})
    away = match.get("away", {})
    home_name = home.get("name", "")
    away_name = away.get("name", "")

    home_str = _lookup_strength(home_name)
    away_str = _lookup_strength(away_name)

    hw, dr, aw = win_prob(home_str, away_str)
    lam_home = expected_goals(home_str, away_str)
    lam_away = expected_goals(away_str, home_str)
    pred_h, pred_a = score_prediction(lam_home, lam_away, hw, aw)
    over_25 = goals_over_2_5(lam_home, lam_away)
    cards = expected_cards(home_str, away_str)
    narr = _narrative(
        home_name, away_name,
        home_str, away_str,
        lam_home, lam_away,
        cards, pred_h, pred_a,
    )

    return {
        "match_id": match.get("id"),
        "matchday": match.get("matchday"),
        "group": match.get("group", ""),
        "utc_date": match.get("utc_date", ""),
        "home": {
            "name": home_name,
            "short": home.get("short", ""),
            "crest": home.get("crest", ""),
            "strength": home_str,
        },
        "away": {
            "name": away_name,
            "short": away.get("short", ""),
            "crest": away.get("crest", ""),
            "strength": away_str,
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
    parser = argparse.ArgumentParser(
        description="WC 2026 maçları için tahmin üretir."
    )
    parser.add_argument(
        "--fixtures",
        default=str(PROCESSED_DIR / "worldcup_2026_fixtures.json"),
        help="Fixture JSON dosyası",
    )
    parser.add_argument(
        "--output",
        default=str(PROCESSED_DIR / "worldcup_2026_predictions.json"),
        help="Çıktı tahmin JSON dosyası",
    )
    args = parser.parse_args()

    ensure_data_dirs()

    fixtures_path = Path(args.fixtures)
    if not fixtures_path.exists():
        print(f"HATA: Fixture dosyası bulunamadı: {fixtures_path}")
        print("Önce `python -m src.collect_worldcup_fixtures` çalıştırın.")
        raise SystemExit(1)

    data = json.loads(fixtures_path.read_text(encoding="utf-8"))
    matches: list[dict] = data.get("matches", [])

    # Sadece grup aşaması (matchday 1-3) — eleme aşamasında takımlar henüz belli değil
    group_matches = [
        m for m in matches
        if m.get("matchday") and m.get("matchday") > 0
        and m.get("home", {}).get("name")
        and m.get("away", {}).get("name")
    ]
    print(f"{len(group_matches)} grup aşaması maçı analiz ediliyor…", flush=True)

    matchday_predictions: dict[str, list] = {}
    for match in group_matches:
        prediction = analyze_match(match)
        md_key = str(match.get("matchday"))
        matchday_predictions.setdefault(md_key, []).append(prediction)

    # Her matchday içinde tarihe göre sırala
    for md_key in matchday_predictions:
        matchday_predictions[md_key].sort(key=lambda m: m.get("utc_date", ""))

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_matches": len(matches),
        "matchday_predictions": matchday_predictions,
    }

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Kaydedildi: {out_path}", flush=True)
    print(f"Toplam tahmin: {len(matches)}, matchday sayısı: {len(matchday_predictions)}", flush=True)


if __name__ == "__main__":
    main()
