"""Oyuncu bazlı gol-atar (skorer) olasılığı: "kim gol atar?" sorusuna cevap.

2025-26 TFF maç verisindeki (`tff_trendyol_super_lig_2025_2026_matches.json`) gerçek gol
olaylarından (own-goal hariç) oyuncu başına gol/başlangıç-XI oranı; GÜNCEL 2026-27 kadrosuyla
(`transfermarkt_super_lig_squads_2026_2027.json`, canlı yeniden toplandı — bkz. PROJECT_STATE
2026-08-14) eşleştirilir. Takımın maç için beklenen golü (`expected_home/away_goals`), rated
oyuncular arasında tarihsel gol PAYINA göre dağıtılır; P(oyuncu ≥1 gol) = 1 − e^(−beklenen).

Oyuncu eşleştirmesi `canonical_player_name` (normalize + `data/manual/player_aliases.json`)
ile yapılır — TFF'nin tam ad formatı ile TM'nin yaygın ad formatı birebir örtüşmeyebilir;
eşleşmeyen oyuncular İÇİN TAHMİN ÜRETİLMEZ (yanlış oyuncu göstermektense veri-yok tercih edilir).

Yeni transfer/yabancı imza (2025-26 Süper Lig'de oynamamış) hücum oyuncuları (FWD/MID) için
gerçek gol oranı yoktur; bunlar tamamen hariç tutmak yerine "projected" (tahmini) bir orana
sahip olur — kendi pozisyon grubundaki değerlendirilmiş (rated) oyuncuların ortalama gol
oranı, o oyuncunun piyasa değerinin aynı pozisyon grubu ortalamasına oranıyla ölçeklenir
(bkz. `PROJECTED_VALUE_MULT_RANGE`). Piyasa değeri bilinmiyorsa ortalamanın altında sabit bir
çarpan kullanılır. Bu, örn. yeni transfer bir santrforun listede hiç görünmemesini (ve takımın
golcü olasılığının yanlışlıkla ayrılmış eski oyunculara yıkılmasını) önler; `projected: true`
alanıyla işaretlenir ve arayüzde ayrı gösterilir.

model_league_predictions.py'a DOKUNMAZ.
"""
from __future__ import annotations

import json
import math
from collections import defaultdict

from src.config import PROCESSED_DIR
from src.normalization import canonical_player_name, normalize_team_name
from src.build_season_fixture_predictions import NAME_ALIASES

FIXTURE_PATH = PROCESSED_DIR / "season_fixture_predictions_2026_2027.json"
HIST_PATH = PROCESSED_DIR / "tff_trendyol_super_lig_2025_2026_matches.json"
SQUAD_PATH = PROCESSED_DIR / "transfermarkt_super_lig_squads_2026_2027.json"
OUTPUT_PATH = PROCESSED_DIR / "goal_scorer_predictions_2026_2027.json"

OWN_GOAL_TYPE = "K"
MIN_STARTS = 3          # oran güvenilir sayılmadan önce minimum başlangıç-XI sayısı
TOP_N_PER_SIDE = 3       # kartta gösterilecek olası golcü sayısı
EXCLUDED_POSITION_GROUPS = {"GK"}  # kaleciler skorer sıralamasından hariç
PROJECTED_POSITION_GROUPS = {"FWD", "MID"}  # 2025-26'da oynamamış (yeni transfer/yabancı) hücum oyuncuları için tahmini oran
PROJECTED_VALUE_MULT_RANGE = (0.3, 3.0)  # piyasa değeri çarpanı sınırı (aşırı uç değerleri sınırlamak için)
PROJECTED_UNVALUED_MULT = 0.5  # piyasa değeri bilinmeyen yeni transferler için varsayılan (ortalamanın altı) çarpan

# TM kulüp adı fikstürdeki adla birebir örtüşmeyen kulüpler (NAME_ALIASES'a ek).
_TM_EXTRA_ALIASES = {
    "AMED SPORTİF FAALİYETLER": "AMED SFK",
    "ARCA ÇORUM FK": "ÇORUM FK",  # bkz. PROJECT_STATE: fikstürde aynı kulüp iki adla geçiyor
}


def _canon(name: str | None) -> str:
    n = normalize_team_name(name) or ""
    return _TM_EXTRA_ALIASES.get(n) or NAME_ALIASES.get(n, n)


def build_player_goal_history(matches: list[dict]) -> tuple[dict[str, int], dict[str, int]]:
    """canonical_player_name -> (2025-26 gol sayısı, başlangıç-XI sayısı)."""
    goals: dict[str, int] = defaultdict(int)
    starts: dict[str, int] = defaultdict(int)
    for m in matches:
        for side in ("home", "away"):
            for p in m.get("lineups", {}).get(side, {}).get("starting", []):
                starts[canonical_player_name(p.get("name"))] += 1
        for side in ("home", "away"):
            for g in m.get("goals", {}).get(side, []):
                if g.get("type") == OWN_GOAL_TYPE:
                    continue
                goals[canonical_player_name(g.get("player_name"))] += 1
    return dict(goals), dict(starts)


def build_team_rosters() -> dict[str, list[dict]]:
    """_canon(takım adı) -> [{"name", "position_group", "rate"} ...] — yalnız kaleci-dışı."""
    if not SQUAD_PATH.exists():
        return {}
    squads = json.loads(SQUAD_PATH.read_text(encoding="utf-8"))
    out: dict[str, list[dict]] = {}
    for club in squads.get("clubs", []):
        team = _canon(club.get("team_name"))
        out[team] = [
            p for p in club.get("players", [])
            if p.get("position_group") not in EXCLUDED_POSITION_GROUPS
        ]
    return out


def build_predictions() -> dict:
    if not HIST_PATH.exists() or not FIXTURE_PATH.exists() or not SQUAD_PATH.exists():
        return {"available": False, "matches": {}}

    hist = json.loads(HIST_PATH.read_text(encoding="utf-8"))
    goals, starts = build_player_goal_history(hist)
    rosters = build_team_rosters()

    # Pozisyon grubu başına, değerlendirilmiş (rated) oyunculardan ortalama gol oranı ve
    # ortalama piyasa değeri — yeni transferler için "projected" oranı ölçeklemekte kullanılır.
    pg_rates: dict[str, list[float]] = defaultdict(list)
    pg_values: dict[str, list[float]] = defaultdict(list)
    for roster in rosters.values():
        for p in roster:
            n_starts = starts.get(canonical_player_name(p.get("name")), 0)
            if n_starts < MIN_STARTS:
                continue
            n_goals = goals.get(canonical_player_name(p.get("name")), 0)
            rate = n_goals / n_starts
            if rate <= 0:
                continue
            pg = p.get("position_group")
            pg_rates[pg].append(rate)
            mv = p.get("market_value_eur")
            if mv:
                pg_values[pg].append(mv)
    pg_avg_rate = {pg: sum(v) / len(v) for pg, v in pg_rates.items() if v}
    pg_avg_value = {pg: sum(v) / len(v) for pg, v in pg_values.items() if v}

    def _side_candidates(team_fixture_name: str, lam: float) -> list[dict]:
        roster = rosters.get(_canon(team_fixture_name), [])
        rated = []
        for p in roster:
            key = canonical_player_name(p.get("name"))
            n_starts = starts.get(key, 0)
            if n_starts >= MIN_STARTS:
                n_goals = goals.get(key, 0)
                rated.append({"name": p.get("name"), "rate": n_goals / n_starts, "goals_2025_26": n_goals, "starts_2025_26": n_starts, "projected": False})
                continue
            pg = p.get("position_group")
            base_rate = pg_avg_rate.get(pg) if pg in PROJECTED_POSITION_GROUPS else None
            if not base_rate:
                continue
            mv = p.get("market_value_eur")
            avg_mv = pg_avg_value.get(pg)
            if mv and avg_mv:
                lo, hi = PROJECTED_VALUE_MULT_RANGE
                mult = max(lo, min(hi, mv / avg_mv))
            else:
                mult = PROJECTED_UNVALUED_MULT
            rated.append({"name": p.get("name"), "rate": base_rate * mult, "goals_2025_26": 0, "starts_2025_26": n_starts, "projected": True})
        total_rate = sum(p["rate"] for p in rated)
        if total_rate <= 0 or lam is None:
            return []
        candidates = []
        for p in rated:
            if p["rate"] <= 0:
                continue
            share = p["rate"] / total_rate
            expected = lam * share
            candidates.append({
                "player": p["name"],
                "scores_probability": round(1 - math.exp(-expected), 3),
                "goals_2025_26": p["goals_2025_26"],
                "starts_2025_26": p["starts_2025_26"],
                "projected": p["projected"],
            })
        candidates.sort(key=lambda c: c["scores_probability"], reverse=True)
        return candidates[:TOP_N_PER_SIDE]

    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    out_matches = {}
    for week in fixture.get("weeks", []):
        for m in week.get("matches", []):
            if m.get("is_played"):
                continue
            lam_h, lam_a = m.get("expected_home_goals"), m.get("expected_away_goals")
            home_c = _side_candidates(m.get("home_team"), lam_h)
            away_c = _side_candidates(m.get("away_team"), lam_a)
            if not home_c and not away_c:
                continue
            out_matches[str(m["match_id"])] = {
                "home_scorers": home_c,
                "away_scorers": away_c,
                "home_roster_rated": bool(home_c),
                "away_roster_rated": bool(away_c),
            }

    return {
        "available": True,
        "method": "2025-26 gol/başlangıç-XI oranı × 2026-27 güncel kadro (TM) × bu haftanın beklenen golü (Poisson pay dağıtımı)",
        "min_starts_threshold": MIN_STARTS,
        "matches": out_matches,
    }


def main() -> None:
    payload = build_predictions()
    OUTPUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    n = len(payload.get("matches", {}))
    print(f"Kaydedildi: {n} maç için skorer tahmini → {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
