"""Maç geneli gol & kart sinyalleri: 2.5 alt/üst, KG var/yok, beklenen kart, kırmızı kart riski.

`model_league_predictions.py`'ın zaten ürettiği `expected_home_goals`/`expected_away_goals`
(form+Elo+hakem-ayarlı, Poisson λ olarak yorumlanabilir) üzerinden saf Poisson matematiğiyle gol
sinyalleri; 2025-26 TFF maç verisindeki (`tff_trendyol_super_lig_2025_2026_matches.json`) gerçek
`goals`/`cards` olaylarından takım+hakem kart geçmişiyle kart sinyalleri üretir.

ÖNEMLİ: model_league_predictions.py'a DOKUNMAZ — 2025-26 Beşiktaş backtest doğruluğu (0.655)
etkilenmez. Bu, ayrı ve bağımsız bir türetilmiş-sinyal katmanıdır.
"""
from __future__ import annotations

import json
import math
from collections import defaultdict

from src.config import PROCESSED_DIR
from src.normalization import normalize_team_name
from src.build_season_fixture_predictions import NAME_ALIASES

FIXTURE_PATH = PROCESSED_DIR / "season_fixture_predictions_2026_2027.json"
HIST_PATH = PROCESSED_DIR / "tff_trendyol_super_lig_2025_2026_matches.json"
OUTPUT_PATH = PROCESSED_DIR / "match_signals_2026_2027.json"

RED_CARD_TYPES = {"Kırmızı Kart", "Çift Sarı Kart"}
MIN_TEAM_MATCHES = 3
MIN_REFEREE_MATCHES = 5


def _canon(name: str | None) -> str:
    """2026-27 fikstür adını 2025-26 tarihsel maç verisindeki adla hizalar — aynı
    NAME_ALIASES (sponsor adı değişiklikleri) build_season_fixture_predictions'ın kullandığı."""
    n = normalize_team_name(name) or ""
    return NAME_ALIASES.get(n, n)


def poisson_pmf(k: int, lam: float) -> float:
    return math.exp(-lam) * lam ** k / math.factorial(k)


def prob_over_2_5(lam_total: float) -> float:
    """Toplam gol Poisson(λh+λg) — iki bağımsız Poisson'un toplamı Poisson'dur."""
    p_under = sum(poisson_pmf(k, lam_total) for k in range(3))  # 0, 1, 2 gol
    return max(0.0, min(1.0, 1 - p_under))


def prob_btts(lam_home: float, lam_away: float) -> float:
    """KG VAR olasılığı — bağımsızlık yaklaşımı (P(ev≥1)·P(dep≥1))."""
    return (1 - math.exp(-lam_home)) * (1 - math.exp(-lam_away))


def build_team_card_stats(matches: list[dict]) -> dict[str, dict]:
    stats: dict[str, dict] = defaultdict(lambda: {"matches": 0, "cards": 0, "reds": 0})
    for m in matches:
        for side in ("home", "away"):
            team = _canon(m[f"{side}_team"]["name"])
            cards = m.get("cards", {}).get(side, [])
            stats[team]["matches"] += 1
            stats[team]["cards"] += len(cards)
            stats[team]["reds"] += sum(1 for c in cards if c.get("type") in RED_CARD_TYPES)
    out = {}
    for team, s in stats.items():
        if s["matches"] < MIN_TEAM_MATCHES:
            continue
        out[team] = {
            "matches": s["matches"],
            "cards_per_match": round(s["cards"] / s["matches"], 2),
            "red_rate": round(s["reds"] / s["matches"], 3),
        }
    return out


def build_referee_red_stats(matches: list[dict]) -> dict[str, dict]:
    """Hakem başı kırmızı kart oranı — model_league_predictions'taki referee_history'den
    bağımsız (o yalnız toplam kart tutar, kırmızı/sarı ayırmaz)."""
    hist: dict[str, dict] = defaultdict(lambda: {"matches": 0, "reds": 0})
    for m in matches:
        ref = next((o.get("name") for o in (m.get("officials") or []) if o.get("role") == "Hakem"), None)
        if not ref:
            continue
        reds = sum(
            1 for side in ("home", "away")
            for c in m.get("cards", {}).get(side, [])
            if c.get("type") in RED_CARD_TYPES
        )
        hist[ref]["matches"] += 1
        hist[ref]["reds"] += reds
    out = {}
    for ref, s in hist.items():
        if s["matches"] < MIN_REFEREE_MATCHES:
            continue
        out[ref] = {"matches": s["matches"], "red_rate": round(s["reds"] / s["matches"], 3)}
    return out


def build_signals() -> dict:
    if not HIST_PATH.exists() or not FIXTURE_PATH.exists():
        return {"available": False, "matches": {}}

    hist = json.loads(HIST_PATH.read_text(encoding="utf-8"))
    team_cards = build_team_card_stats(hist)
    ref_reds = build_referee_red_stats(hist)
    league_avg_cards = sum(s["cards_per_match"] for s in team_cards.values()) / len(team_cards)
    league_avg_red = sum(s["red_rate"] for s in team_cards.values()) / len(team_cards)

    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    out_matches = {}
    for week in fixture.get("weeks", []):
        for m in week.get("matches", []):
            if m.get("is_played"):
                continue
            lam_h, lam_a = m.get("expected_home_goals"), m.get("expected_away_goals")
            if lam_h is None or lam_a is None:
                continue

            # Beklenen TOPLAM kart (iki takım birden) — takım oranları PER-TEAM olduğu için
            # toplanır (ortalanmaz); eksik takım için lig ortalaması kullanılır. referee_cards_per_match
            # (model_league_predictions'tan) zaten maç-toplamı birimindedir, aynı ölçekte harmanlanır.
            home_c = team_cards.get(_canon(m.get("home_team")))
            away_c = team_cards.get(_canon(m.get("away_team")))
            home_rate = home_c["cards_per_match"] if home_c else league_avg_cards
            away_rate = away_c["cards_per_match"] if away_c else league_avg_cards
            team_total = home_rate + away_rate
            ref_card = m.get("referee_cards_per_match")
            expected_cards = round(0.5 * team_total + 0.5 * ref_card, 1) if ref_card is not None else round(team_total, 1)

            home_red = home_c["red_rate"] if home_c else league_avg_red
            away_red = away_c["red_rate"] if away_c else league_avg_red
            main_ref = m.get("main_referee")
            ref_red = ref_reds.get(main_ref) if main_ref else None
            if ref_red:
                home_red = 0.5 * home_red + 0.5 * ref_red["red_rate"]
                away_red = 0.5 * away_red + 0.5 * ref_red["red_rate"]
            red_risk = 1 - (1 - min(home_red, 0.5)) * (1 - min(away_red, 0.5))

            out_matches[str(m["match_id"])] = {
                "over_2_5_probability": round(prob_over_2_5(lam_h + lam_a), 3),
                "btts_probability": round(prob_btts(lam_h, lam_a), 3),
                "expected_total_cards": expected_cards,
                "red_card_risk": round(min(0.95, red_risk), 3),
                "home_card_data_available": bool(home_c),
                "away_card_data_available": bool(away_c),
            }

    return {
        "available": True,
        "league_avg_cards_per_match": round(league_avg_cards, 2),
        "league_avg_red_rate": round(league_avg_red, 3),
        "matches": out_matches,
    }


def main() -> None:
    payload = build_signals()
    OUTPUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    n = len(payload.get("matches", {}))
    print(f"Kaydedildi: {n} maç için gol/kart sinyali → {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
