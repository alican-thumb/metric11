from __future__ import annotations

import json
import math
from collections import Counter

from src.normalization import normalize_name
from src.preview.constants import ACTION_LABELS

_H2H_MIN_MATCHES = 3
_h2h_cache: dict | None = None

_TRANSFER_STATUS_WEIGHT = {
    "OFFICIAL": 1.0,
    "CORROBORATED": 0.6,
    "TM_CONFIRMED": 0.6,
    "RUMOR": 0.15,
    "REVIEW_REQUIRED": 0.1,
}
_TRANSFER_CONFIRMED_STATUSES = {"OFFICIAL", "CORROBORATED", "TM_CONFIRMED"}
_TRANSFER_MIN_CONFIRMED_VALUE_EUR = 2_000_000
_TRANSFER_EDGE_CAP = 0.15
_TRANSFER_DEFAULT_SQUAD_VALUE_EUR = 50_000_000
_transfer_tracker_cache: list | None = None
_squad_value_cache: dict | None = None

# Avrupa kupası form sinyali (kontrollü, capli): Türk kulüplerinin oynanmış Avrupa
# maç SONUÇLARI takım gücüne küçük bir ek/çıkarım olarak yansır. Transfer edge ile
# aynı felsefe: düşük ağırlıklı, capli, yalnızca ileriye dönük 2026-27 tahminlerinde
# aktif; 2025-26 backtest'i etkilemez.
_EURO_EDGE_CAP = 0.15
_EURO_EDGE_PER_POINT = 0.05
_EURO_RESULT_VALUE = {"win": 1.0, "draw": 0.25, "loss": -1.0}
_EURO_OPP_WEIGHT = {"elite": 1.5, "strong": 1.2, "mid": 1.0, "weak": 0.7}
_EURO_MAX_MATCHES = 6
_EURO_RECENCY_DECAY = 0.85
_euro_results_cache: list | None = None


def _load_h2h_pairs() -> dict:
    global _h2h_cache
    if _h2h_cache is None:
        from src.config import PROCESSED_DIR, SEASON

        path = PROCESSED_DIR / f"head_to_head_history_{SEASON}.json"
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            _h2h_cache = payload.get("pairs", {})
        except (FileNotFoundError, json.JSONDecodeError):
            _h2h_cache = {}
    return _h2h_cache


def head_to_head_draw_signal(team_a: str, team_b: str) -> dict:
    """İki takımın API-Football kafa kafaya geçmişinden gerçek beraberlik oranını döner.

    Veri henüz toplanmamışsa veya örneklem çok küçükse (< 3 maç) sinyal devre dışı
    kalır — draw_calibration_signal bu durumda hiçbir ek etki uygulamaz.
    """
    pairs = _load_h2h_pairs()
    key = "|".join(sorted([team_a, team_b]))
    data = pairs.get(key)
    if not data or (data.get("matches") or 0) < _H2H_MIN_MATCHES:
        return {"available": False, "matches": 0, "draw_rate": None}
    return {
        "available": True,
        "matches": data["matches"],
        "draw_rate": data["draw_rate"],
        "last_meeting_date": data.get("last_meeting_date"),
    }


def _load_transfer_tracker() -> list:
    global _transfer_tracker_cache
    if _transfer_tracker_cache is None:
        from src.config import PROCESSED_DIR, SEASON

        path = PROCESSED_DIR / f"transfer_tracker_{SEASON}.json"
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            _transfer_tracker_cache = payload.get("transfers", [])
        except (FileNotFoundError, json.JSONDecodeError):
            _transfer_tracker_cache = []
    return _transfer_tracker_cache


def _load_squad_values() -> dict:
    global _squad_value_cache
    if _squad_value_cache is None:
        from src.config import PROCESSED_DIR, SEASON

        path = PROCESSED_DIR / f"transfermarkt_super_lig_squads_{SEASON}.json"
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            _squad_value_cache = {
                club["team_name"]: (club.get("summary") or {}).get("market_value_total_eur")
                for club in payload.get("clubs", [])
            }
        except (FileNotFoundError, json.JSONDecodeError):
            _squad_value_cache = {}
    return _squad_value_cache


def _club_matches_team(team_name: str, club_name: str | None) -> bool:
    """En az bir anlamlı (>=4 karakter) ortak token varsa aynı kulüp kabul edilir.

    Transfer haberlerindeki kısa kulüp adları ("Galatasaray") ile TFF'nin resmi
    uzun adları ("GALATASARAY A.Ş.", "RAMS BAŞAKŞEHİR FUTBOL KULÜBÜ") arasında
    tam bir alias tablosu tutmak yerine, kasıtlı olarak gevşek ama düşük riskli
    bir eşleme kullanılır: bu sinyal zaten düşük ağırlıklı ve `available=False`
    ile devre dışı kalabiliyor, yanlış eşleşme riski sinyalin genel etkisini
    aşmıyor.
    """
    if not club_name:
        return False
    team_tokens = {tok for tok in normalize_name(team_name).split() if len(tok) >= 4}
    club_tokens = {tok for tok in normalize_name(club_name).split() if len(tok) >= 4}
    return bool(team_tokens & club_tokens)


def transfer_strength_edge(team_name: str) -> dict:
    """Transfer tracker'daki gerçek transfer sinyallerinden takım gücüne küçük bir ek/çıkarım döner.

    Sinyal yalnızca en az bir OFFICIAL/CORROBORATED/TM_CONFIRMED (doğrulanmış)
    transfer varsa devreye girer — salt RUMOR/REVIEW_REQUIRED söylentileri
    (bugünkü canlı veride hepsi bu durumda) tek başına sinyali AKTİF ETMEZ,
    `available: False` ile tahmine hiç karışmaz. Doğrulanmış bir transfer
    devreye girdiğinde, henüz doğrulanmamış ek söylentiler edge büyüklüğüne
    küçük bir katkı olarak dahil edilir.
    """
    transfers = _load_transfer_tracker()
    squad_values = _load_squad_values()
    total_net_value = 0.0
    confirmed_net_value = 0.0
    top_moves: list[dict] = []
    for record in transfers:
        status = record.get("status")
        weight = _TRANSFER_STATUS_WEIGHT.get(status, 0.0)
        value = record.get("market_value_eur") or 0
        if not weight or not value:
            continue
        is_arrival = _club_matches_team(team_name, record.get("to_club"))
        is_departure = _club_matches_team(team_name, record.get("from_club"))
        if not is_arrival and not is_departure:
            continue
        weighted_value = weight * value if is_arrival else -weight * value
        total_net_value += weighted_value
        if status in _TRANSFER_CONFIRMED_STATUSES:
            confirmed_net_value += weighted_value
        top_moves.append({
            "player": record.get("player"),
            "direction": "in" if is_arrival else "out",
            "market_value_eur": value,
            "status": status,
        })

    if abs(confirmed_net_value) < _TRANSFER_MIN_CONFIRMED_VALUE_EUR:
        return {"available": False, "edge": 0.0, "signal_count": 0}

    squad_value = squad_values.get(team_name) or _TRANSFER_DEFAULT_SQUAD_VALUE_EUR
    relative_edge = total_net_value / max(squad_value, _TRANSFER_DEFAULT_SQUAD_VALUE_EUR)
    edge = max(-_TRANSFER_EDGE_CAP, min(_TRANSFER_EDGE_CAP, relative_edge))
    return {
        "available": True,
        "edge": round(edge, 4),
        "signal_count": len(top_moves),
        "confirmed_net_value_eur": round(confirmed_net_value),
        "total_net_value_eur": round(total_net_value),
        "top_moves": sorted(top_moves, key=lambda m: m["market_value_eur"], reverse=True)[:5],
    }


_CONGESTION_WINDOW_DAYS = 4
_CONGESTION_EDGE_BY_DAYS_REST = {1: -0.09, 2: -0.075, 3: -0.06, 4: -0.03}
_euro_match_index_cache: list | None = None


def _parse_flexible_iso(value: str | None):
    from datetime import datetime
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


def _load_european_match_index() -> list[tuple[str, "datetime"]]:
    """Süper Lig takımlarının Avrupa kupası maç tarihlerini iki kaynaktan birleştirir:
    otomatik lig fazı/eleme fikstürü (football-data.org, sezon ilerledikçe dolar) ve
    haber kaynaklı ön eleme turu fikstürü (data/manual — API'nin kapsamadığı Haziran-Ağustos dönemi).
    """
    global _euro_match_index_cache
    if _euro_match_index_cache is not None:
        return _euro_match_index_cache

    from datetime import timedelta, timezone
    from src.config import DATA_DIR, PROCESSED_DIR

    tr_tz = timezone(timedelta(hours=3))
    index: list[tuple[str, "datetime"]] = []

    auto_path = PROCESSED_DIR / "european_fixtures_2026_2027.json"
    if auto_path.exists():
        try:
            payload = json.loads(auto_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            payload = {}
        for comp in payload.get("competitions", {}).values():
            for m in comp.get("matches", []):
                dt = _parse_flexible_iso(m.get("utc_date"))
                if not dt:
                    continue
                dt_local = dt.astimezone(tr_tz).replace(tzinfo=None)
                for side in ("home", "away"):
                    name = (m.get(side) or {}).get("name")
                    if name:
                        index.append((name, dt_local))

    manual_path = DATA_DIR / "manual" / "european_qualifier_fixtures_2026_2027.json"
    if manual_path.exists():
        try:
            payload = json.loads(manual_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            payload = {}
        for fx in payload.get("fixtures", []):
            dt = _parse_flexible_iso(fx.get("kickoff_local"))
            if not dt:
                continue
            dt_local = dt.astimezone(tr_tz).replace(tzinfo=None)
            for key in ("home_team", "away_team"):
                name = fx.get(key)
                if name:
                    index.append((name, dt_local))

    _euro_match_index_cache = index
    return index


def fixture_congestion_edge(team_name: str, match_date) -> dict:
    """Bir takımın lig maçından hemen önce Avrupa kupası maçı oynayıp oynamadığını
    kontrol eder; oynadıysa küçük bir yorgunluk/rotasyon ceza sinyali döner.

    Henüz backtest edilmemiş yeni bir sinyaldir — `apply_fixture_congestion=True` ile
    yalnızca ileriye dönük tahminlerde (bkz. build_season_fixture_predictions.py)
    devreye girer; kalibre edilmiş backtest sistemini etkilemez.
    """
    if match_date is None:
        return {"available": False, "edge": 0.0, "days_rest": None, "opponent": None}
    best: tuple[int, str] | None = None
    for name, euro_dt in _load_european_match_index():
        if not _club_matches_team(team_name, name):
            continue
        days_rest = (match_date.date() - euro_dt.date()).days
        if 0 < days_rest <= _CONGESTION_WINDOW_DAYS:
            if best is None or days_rest < best[0]:
                best = (days_rest, name)
    if best is None:
        return {"available": False, "edge": 0.0, "days_rest": None, "opponent": None}
    days_rest, opponent = best
    edge = _CONGESTION_EDGE_BY_DAYS_REST.get(days_rest, 0.0)
    return {"available": True, "edge": edge, "days_rest": days_rest, "opponent": opponent}


def _load_european_results() -> list[dict]:
    """Türk kulüplerinin oynanmış (skoru dolu) Avrupa maçlarını iki kaynaktan birleştirir:
    elle/collector doldurulan `data/manual/european_results_2026_2027.json` ve
    otomatik `european_fixtures_2026_2027.json` içindeki FINISHED maçlar.

    Her kayıt: {home_team, away_team, home_score, away_score, opponent_strength, date}.
    Skoru olmayan (None) veya `_example` işaretli kayıtlar atlanır — sonuç girilene
    kadar sinyal `available=False` kalır.
    """
    global _euro_results_cache
    if _euro_results_cache is not None:
        return _euro_results_cache

    from src.config import DATA_DIR, PROCESSED_DIR

    results: list[dict] = []

    manual_path = DATA_DIR / "manual" / "european_results_2026_2027.json"
    if manual_path.exists():
        try:
            payload = json.loads(manual_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            payload = {}
        for r in payload.get("results", []):
            if r.get("_example"):
                continue
            if r.get("home_score") is None or r.get("away_score") is None:
                continue
            results.append({
                "home_team": r.get("home_team"),
                "away_team": r.get("away_team"),
                "home_score": r.get("home_score"),
                "away_score": r.get("away_score"),
                "opponent_strength": r.get("opponent_strength") or "mid",
                "date": r.get("date"),
            })

    auto_path = PROCESSED_DIR / "european_fixtures_2026_2027.json"
    if auto_path.exists():
        try:
            payload = json.loads(auto_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            payload = {}
        for comp in payload.get("competitions", {}).values():
            for m in comp.get("matches", []):
                # collect_european_fixtures._build_match şeması: score.home / score.away.
                if m.get("status") and m.get("status") != "FINISHED":
                    continue
                score = m.get("score") or {}
                home_score = score.get("home")
                away_score = score.get("away")
                if home_score is None or away_score is None:
                    continue
                results.append({
                    "home_team": (m.get("home") or {}).get("name"),
                    "away_team": (m.get("away") or {}).get("name"),
                    "home_score": home_score,
                    "away_score": away_score,
                    "opponent_strength": "mid",
                    "date": m.get("utc_date"),
                })

    _euro_results_cache = results
    return results


def european_form_edge(team_name: str) -> dict:
    """Bir Süper Lig takımının oynanmış Avrupa maç SONUÇLARINDAN küçük, capli bir
    güç sinyali döner.

    Galibiyet/beraberlik/mağlubiyet, rakip seviyesi ağırlığı (`opponent_strength`)
    ve zaman yakınlığı (son maçlar daha ağır) ile puanlanır; toplam `±_EURO_EDGE_CAP`
    aralığına sıkıştırılır. Takımın hiç oynanmış Avrupa sonucu yoksa `available=False`
    ile tahmine karışmaz. Yalnızca `apply_european_signal=True` (bkz.
    build_season_fixture_predictions.py) ile ileriye dönük tahminlerde devreye girer.
    """
    matches = []
    for r in _load_european_results():
        is_home = _club_matches_team(team_name, r.get("home_team"))
        is_away = _club_matches_team(team_name, r.get("away_team"))
        if is_home == is_away:  # ne ev ne deplasman (ya da her ikisi — belirsiz), atla
            continue
        gf = r["home_score"] if is_home else r["away_score"]
        ga = r["away_score"] if is_home else r["home_score"]
        if gf > ga:
            outcome = "win"
        elif gf == ga:
            outcome = "draw"
        else:
            outcome = "loss"
        opponent = r.get("away_team") if is_home else r.get("home_team")
        matches.append({
            "outcome": outcome,
            "opponent": opponent,
            "opponent_strength": r.get("opponent_strength") or "mid",
            "date": r.get("date"),
            "score": f"{gf}-{ga}",
        })

    if not matches:
        return {"available": False, "edge": 0.0, "match_count": 0}

    # En yeni maçlar önce; recency decay ile ağırlıklandır.
    matches.sort(key=lambda m: (m.get("date") or ""), reverse=True)
    net = 0.0
    wins = draws = losses = 0
    for i, m in enumerate(matches[:_EURO_MAX_MATCHES]):
        result_value = _EURO_RESULT_VALUE.get(m["outcome"], 0.0)
        opp_weight = _EURO_OPP_WEIGHT.get(m["opponent_strength"], 1.0)
        recency = _EURO_RECENCY_DECAY ** i
        net += result_value * opp_weight * recency
        if m["outcome"] == "win":
            wins += 1
        elif m["outcome"] == "draw":
            draws += 1
        else:
            losses += 1

    edge = max(-_EURO_EDGE_CAP, min(_EURO_EDGE_CAP, net * _EURO_EDGE_PER_POINT))
    return {
        "available": True,
        "edge": round(edge, 4),
        "match_count": len(matches),
        "record": {"w": wins, "d": draws, "l": losses},
        "recent": matches[:_EURO_MAX_MATCHES],
    }


def poisson_pmf(k: int, lam: float) -> float:
    return math.exp(-lam) * lam**k / math.factorial(k)


def poisson_outcome_probabilities(target_xg: float, opponent_xg: float, max_goals: int = 7) -> dict:
    totals = Counter()
    for target_goals in range(max_goals + 1):
        for opponent_goals in range(max_goals + 1):
            probability = poisson_pmf(target_goals, target_xg) * poisson_pmf(opponent_goals, opponent_xg)
            if target_goals > opponent_goals:
                totals["target"] += probability
            elif target_goals == opponent_goals:
                totals["draw"] += probability
            else:
                totals["opponent"] += probability
    total = totals["target"] + totals["draw"] + totals["opponent"]
    return {key: totals[key] / total for key in ("target", "draw", "opponent")}


def scoreline_probabilities(target_xg: float, opponent_xg: float, max_goals: int = 5) -> list[dict]:
    rows = []
    for target_goals in range(max_goals + 1):
        for opponent_goals in range(max_goals + 1):
            probability = poisson_pmf(target_goals, target_xg) * poisson_pmf(opponent_goals, opponent_xg)
            rows.append(
                {
                    "target_goals": target_goals,
                    "opponent_goals": opponent_goals,
                    "score": f"{target_goals}-{opponent_goals}",
                    "probability": round(probability, 3),
                }
            )
    return sorted(rows, key=lambda item: item["probability"], reverse=True)


def action_label(action: str | None) -> str:
    return ACTION_LABELS.get(action or "", action or "Senaryo anlat")


def draw_calibration_signal(
    goal_edge: float,
    strength_edge: float,
    expected_goals_for: float,
    expected_goals_against: float,
    is_big_match: bool,
    team_form: dict,
    opponent_recent_form: dict,
    head_to_head: dict | None = None,
) -> dict:
    reasons = []
    lift = 0.0
    total_xg = expected_goals_for + expected_goals_against
    if abs(goal_edge) <= 0.22:
        lift += 0.09
        reasons.append("xG farkı çok dar")
    elif abs(goal_edge) <= 0.38:
        lift += 0.055
        reasons.append("xG farkı dar")
    if abs(strength_edge) <= 0.04:
        lift += 0.045
        reasons.append("takım gücü dengede")
    elif abs(strength_edge) <= 0.08:
        lift += 0.025
        reasons.append("takım gücü yakın")
    if 2.15 <= total_xg <= 2.85:
        lift += 0.025
        reasons.append("orta gol bandı")
    team_draw_rate = team_form.get("draws", 0) / team_form.get("last_n", 1) if team_form.get("last_n") else 0
    opponent_draw_rate = opponent_recent_form.get("draws", 0) / opponent_recent_form.get("last_n", 1) if opponent_recent_form.get("last_n") else 0
    if team_draw_rate >= 0.35 or opponent_draw_rate >= 0.35:
        lift += 0.03
        reasons.append("son formda beraberlik eğilimi")
    if is_big_match:
        lift += 0.025
        reasons.append("büyük maç denge etkisi")

    # --- Sofascore sinyalleri ---
    # Favori xG israfı: bir taraf beklenen gol farkında önde ama son maçlarda xG'sini gole çeviremiyor
    if abs(goal_edge) >= 0.3:
        favored_form = team_form if goal_edge > 0 else opponent_recent_form
        fav_xg = favored_form.get("xg_for_per_match")
        fav_goals = favored_form.get("goals_for_per_match") or 0
        if fav_xg and fav_goals and fav_xg > fav_goals * 1.35:
            lift += 0.04
            reasons.append("favori xG israfı")

    # Düşük şuta isabet ortamı: iki taraf da kaleciyi az zorluyor → gol zor → beraberlik eğilimi
    team_sot = team_form.get("sot_per_match")
    opp_sot = opponent_recent_form.get("sot_per_match")
    if team_sot is not None and opp_sot is not None and (team_sot + opp_sot) < 7.5:
        lift += 0.025
        reasons.append("düşük şuta isabet ortamı")

    # Genel düşük xG bağlamı: her iki takımın son maçları da az xG üretiyor
    team_xg_ctx = team_form.get("xg_for_per_match")
    opp_xg_ctx = opponent_recent_form.get("xg_for_per_match")
    team_xga_ctx = team_form.get("xg_against_per_match")
    opp_xga_ctx = opponent_recent_form.get("xg_against_per_match")
    if team_xg_ctx and opp_xg_ctx and team_xga_ctx and opp_xga_ctx:
        avg_xg_ctx = (team_xg_ctx + team_xga_ctx + opp_xg_ctx + opp_xga_ctx) / 4
        if avg_xg_ctx < 1.1:
            lift += 0.03
            reasons.append("genel düşük xG ortamı")

    # Kafa kafaya (h2h) tarihsel beraberlik oranı: en az 3 önceki eşleşme varsa gerçek
    # geçmiş veriye dayanır (API-Football), tahmini/türetilmiş bir oran değildir.
    if head_to_head and head_to_head.get("available"):
        h2h_rate = head_to_head["draw_rate"]
        if h2h_rate >= 0.40:
            lift += 0.06
            reasons.append("h2h_yüksek_beraberlik_geçmişi")
        elif h2h_rate >= 0.30:
            lift += 0.035
            reasons.append("h2h_beraberlik_geçmişi")

    return {
        "lift": round(min(0.18, lift), 3),
        "risk_level": "HIGH" if lift >= 0.12 else "MEDIUM" if lift >= 0.07 else "LOW" if lift > 0 else "NONE",
        "reasons": reasons,
    }


def big_match_profile_signal(
    is_big_match: bool,
    target_side: str,
    goal_edge: float,
    strength_edge: float,
    draw_calibration: dict,
    referee_signal: dict,
) -> dict:
    if not is_big_match:
        return {"available": False, "risk_level": "NONE", "adjustment": "not_big_match", "notes": []}
    notes = ["büyük maç taban riski", "büyük maç varyansı yüksek"]
    volatility = 0.42
    if abs(goal_edge) <= 0.35:
        volatility += 0.25
        notes.append("xG farkı dar")
    if abs(strength_edge) <= 0.08:
        volatility += 0.2
        notes.append("takım gücü yakın")
    if draw_calibration.get("risk_level") in {"HIGH", "MEDIUM"}:
        volatility += 0.15
        notes.append("beraberlik riski canlı")
    if referee_signal.get("cards_per_match", 0) >= 5:
        volatility += 0.15
        notes.append("hakem kart profili yüksek")
    if target_side == "away":
        volatility += 0.08
        notes.append("deplasman büyük maçı")
    volatility = min(1.0, volatility)
    if volatility >= 0.72:
        risk_level = "HIGH"
        adjustment = "taraf güvenini düşür, kart ve beraberlik senaryosunu öne çıkar"
    elif volatility >= 0.5:
        risk_level = "MEDIUM"
        adjustment = "ana tarafı koru ama alternatif senaryoyu görünür tut"
    else:
        risk_level = "MEDIUM"
        adjustment = "büyük maç taban riski nedeniyle normal maç gibi okunmaz"
    return {
        "available": True,
        "risk_level": risk_level,
        "volatility_score": round(volatility, 2),
        "adjustment": adjustment,
        "notes": notes,
    }


def preview_draw_risk_signal(
    target_win: float,
    draw: float,
    opponent_win: float,
    expected_goals_for: float,
    expected_goals_against: float,
    strength_edge: float,
    confidence: str,
    scorelines: list[dict],
    draw_calibration: dict,
    big_match_profile: dict,
) -> dict:
    score = 0
    reasons = []
    xg_margin = abs(expected_goals_for - expected_goals_against)
    probabilities = sorted([target_win, draw, opponent_win], reverse=True)
    probability_margin = probabilities[0] - probabilities[1]
    side_probability = max(target_win, opponent_win)

    if draw >= 0.28:
        score += 24
        reasons.append("draw_probability_high")
    elif draw >= 0.265:
        score += 18
        reasons.append("draw_probability_live")
    elif draw >= 0.25:
        score += 10
        reasons.append("draw_probability_watch")

    if xg_margin < 0.15:
        score += 24
        reasons.append("xg_margin_very_narrow")
    elif xg_margin < 0.30:
        score += 17
        reasons.append("xg_margin_narrow")
    elif xg_margin < 0.50:
        score += 9
        reasons.append("xg_margin_watch")

    if scorelines and scorelines[0].get("target_goals") == scorelines[0].get("opponent_goals"):
        score += 16
        reasons.append("top_draw_scoreline")
    elif any(item.get("target_goals") == item.get("opponent_goals") for item in scorelines[:2]):
        score += 9
        reasons.append("draw_scoreline_top_two")

    if probability_margin < 0.06:
        score += 20
        reasons.append("probability_margin_very_narrow")
    elif probability_margin < 0.12:
        score += 12
        reasons.append("probability_margin_narrow")
    elif probability_margin < 0.18:
        score += 6
        reasons.append("probability_margin_watch")

    if abs(strength_edge) < 0.12:
        score += 10
        reasons.append("strength_edge_very_narrow")
    elif abs(strength_edge) < 0.25:
        score += 6
        reasons.append("strength_edge_narrow")

    if confidence.startswith("LOW"):
        score += 10
        reasons.append("low_confidence_side_pick")
    elif confidence == "MEDIUM":
        score += 5
        reasons.append("medium_confidence_side_pick")

    if draw_calibration.get("risk_level") == "HIGH":
        score += 12
        reasons.append("draw_calibration_high")
    elif draw_calibration.get("risk_level") == "MEDIUM":
        score += 7
        reasons.append("draw_calibration_medium")
    if big_match_profile.get("risk_level") == "HIGH":
        score += 8
        reasons.append("big_match_high_volatility")
    if side_probability >= 0.52:
        score -= 10
        reasons.append("strong_side_probability_penalty")

    score = max(0, min(100, score))
    if score >= 35:
        level = "HIGH"
        action = "PROTECT_SIDE_PICK_SHOW_DRAW_SCENARIO"
    elif score >= 25:
        level = "MEDIUM"
        action = "KEEP_PICK_WITH_DRAW_WARNING"
    else:
        level = "LOW"
        action = "KEEP_MAIN_PICK"
    return {
        "score": score,
        "risk_level": level,
        "reasons": reasons,
        "protected_prediction": level in {"HIGH", "MEDIUM"},
        "recommended_model_action": action,
        "note": "Ana 1X2 tahminini değiştirmeden beraberlik senaryosunu görünür yapan risk katmanıdır.",
    }


def recommended_call(target_win: float, draw: float, opponent_win: float, scorelines: list[dict], confidence: str, is_big_match: bool) -> dict:
    probabilities = {"target_win": target_win, "draw": draw, "opponent_win": opponent_win}
    predicted = max(probabilities, key=probabilities.get)
    top = probabilities[predicted]
    second = sorted(probabilities.values(), reverse=True)[1]
    risk = []
    if draw >= 0.28:
        risk.append("Beraberlik güçlü alternatif")
    if top - second < 0.08:
        risk.append("Taraflar arası fark dar")
    if is_big_match:
        risk.append("Büyük maç oynaklığı")
    action = "senaryo_anlat"
    if confidence in {"HIGH", "MEDIUM"} and top - second >= 0.1:
        action = "taraf_eğilimi"
    if draw >= 0.3 and top - draw < 0.1:
        action = "beraberlik_korumalı_senaryo"
    return {
        "result": predicted,
        "probability": round(top, 3),
        "scoreline": scorelines[0]["score"] if scorelines else None,
        "action": action,
        "action_label": action_label(action),
        "risk_notes": risk,
    }


def calibrated_display_prediction(
    call: dict,
    draw_risk: dict,
    target_win: float,
    draw: float,
    opponent_win: float,
    *,
    is_big_match: bool,
    strength_edge: float,
    expected_goals_for: float,
    expected_goals_against: float,
    card_signal: str,
    target_team: str,
    opponent_name: str,
    enable_calibration: bool,
) -> dict:
    probabilities = {"target_win": target_win, "draw": draw, "opponent_win": opponent_win}
    raw_result = call.get("result") or max(probabilities, key=probabilities.get)
    sorted_probs = sorted(probabilities.values(), reverse=True)
    margin = sorted_probs[0] - sorted_probs[1]
    final_result = raw_result
    adjustment = "none"
    note = "Ana olasılık tahmini gösterildi."
    if not enable_calibration:
        return {
            "raw_result": raw_result,
            "final_result": raw_result,
            "probability": round(probabilities[raw_result], 3),
            "margin": round(margin, 3),
            "adjustment": "raw_unvalidated_team",
            "label": result_label(raw_result, target_team, opponent_name),
            "raw_label": result_label(raw_result, target_team, opponent_name),
            "note": "Bu takım için ekran kalibrasyonu henüz doğrulanmadığı için ham model tahmini gösterilir.",
        }
    # Backtestte Beşiktaş özelinde en iyi temkin eşiği: çok yüksek beraberlik riski ve dar olasılık farkı.
    if draw_risk.get("score", 0) >= 90 and margin <= 0.12:
        final_result = "draw"
        adjustment = "high_draw_risk_override"
        note = "Çok yüksek beraberlik riski ve dar olasılık farkı nedeniyle ekran tahmini beraberlik senaryosuna çekildi."
    elif draw_risk.get("protected_prediction"):
        adjustment = "protected_side"
        note = "Taraf tahmini korunur, ancak beraberlik senaryosu kullanıcıya açık gösterilir."
    xg_edge = expected_goals_for - expected_goals_against
    if is_big_match and raw_result == "opponent_win" and final_result == "draw" and xg_edge <= -0.28:
        final_result = "opponent_win"
        adjustment = "big_match_opponent_edge"
        note = "Büyük maçta rakip gol beklentisi belirgin üstün kaldığı için beraberlik temkini yerine rakip tarafı gösterildi."
    if (
        is_big_match
        and raw_result == "target_win"
        and strength_edge < 0
        and card_signal == "HIGH"
        and draw_risk.get("score", 0) >= 80
    ):
        final_result = "opponent_win"
        adjustment = "big_match_negative_strength_high_card"
        note = f"Büyük maçta güç sinyali rakibe dönük ve kart/oynaklık yüksek olduğu için {target_team} tarafı düşürüldü."
    return {
        "raw_result": raw_result,
        "final_result": final_result,
        "probability": round(probabilities[final_result], 3),
        "margin": round(margin, 3),
        "adjustment": adjustment,
        "label": result_label(final_result, target_team, opponent_name),
        "raw_label": result_label(raw_result, target_team, opponent_name),
        "note": note,
    }


def result_label(result: str, target_team: str, opponent_name: str) -> str:
    return {
        "target_win": f"{target_team} kazanır",
        "draw": "Beraberlik",
        "opponent_win": f"{opponent_name} kazanır",
    }.get(result, result)


def _blend_xg_goals(xg: float | None, goals: float, xg_weight: float = 0.6) -> float:
    if xg is None:
        return goals
    return round(xg * xg_weight + goals * (1 - xg_weight), 3)


def estimate_probabilities(
    team_form: dict,
    opponent_recent_form: dict,
    opponent_history: dict,
    referee_signal: dict,
    is_big_match: bool,
    availability_signal: dict | None = None,
    target_side: str = "home",
    team_strength: dict | None = None,
    opponent_strength: dict | None = None,
    target_team: str = "Hedef takım",
    opponent_name: str = "Rakip",
    enable_display_calibration: bool = False,
) -> dict:
    # Sofascore xG varsa goals proxy yerine xG kullan (60/40 blend)
    attack = _blend_xg_goals(team_form.get("xg_for_per_match"), team_form["goals_for_per_match"])
    defense = _blend_xg_goals(team_form.get("xg_against_per_match"), team_form["goals_against_per_match"])
    opponent_attack = _blend_xg_goals(
        opponent_recent_form.get("xg_for_per_match"),
        opponent_recent_form.get("goals_for_per_match") or defense,
    )
    opponent_defense = _blend_xg_goals(
        opponent_recent_form.get("xg_against_per_match"),
        opponent_recent_form.get("goals_against_per_match") or attack,
    )
    xg_data_available = bool(team_form.get("xg_data_matches"))
    card_base = team_form["cards_per_match"]
    if opponent_history.get("matches"):
        attack = attack * 0.82 + opponent_history["goals_for_per_match"] * 0.18
        defense = defense * 0.82 + opponent_history["goals_against_per_match"] * 0.18
        card_base = (card_base + opponent_history["cards_for_per_match"]) / 2

    expected_goals_for_raw = attack * 0.6 + opponent_defense * 0.4
    expected_goals_against_raw = opponent_attack * 0.6 + defense * 0.4
    if target_side == "home":
        expected_goals_for_raw += 0.14
        expected_goals_against_raw -= 0.06
    else:
        expected_goals_for_raw -= 0.06
        expected_goals_against_raw += 0.12
    if is_big_match:
        expected_goals_for_raw *= 0.96
        expected_goals_against_raw *= 1.04

    strength_edge = 0.0
    if (team_strength or {}).get("available") and (opponent_strength or {}).get("available"):
        strength_edge = (team_strength["strength_score"] - opponent_strength["strength_score"]) / 100
        attack_edge = (team_strength["attack_score"] - opponent_strength["defense_score"]) / 100
        defense_edge = (team_strength["defense_score"] - opponent_strength["attack_score"]) / 100
        expected_goals_for_raw += strength_edge * 0.22 + attack_edge * 0.18
        expected_goals_against_raw -= strength_edge * 0.16 + defense_edge * 0.14

    expected_goals_for = round(max(0.3, expected_goals_for_raw), 2)
    expected_goals_against = round(max(0.2, expected_goals_against_raw), 2)
    missing_count = len((availability_signal or {}).get("unavailable", []))
    missing_regulars = len([item for item in (availability_signal or {}).get("unavailable", []) if item.get("impact") == "REGULAR"])
    # Use squad-importance-based xg adjustment if available; fall back to crude count heuristic
    squad_xg_adj = (availability_signal or {}).get("squad_xg_adjustment")
    if squad_xg_adj is not None:
        # squad_xg_adj is already negative (penalty)
        expected_goals_for = round(max(0.25, expected_goals_for + squad_xg_adj), 2)
    elif missing_count:
        expected_goals_for = round(max(0.25, expected_goals_for - missing_count * 0.05 - missing_regulars * 0.08), 2)
    goal_edge = expected_goals_for - expected_goals_against
    poisson = poisson_outcome_probabilities(expected_goals_for, expected_goals_against)

    heuristic_target = 0.42 + goal_edge * 0.08 + strength_edge * 0.1
    heuristic_draw = 0.28 - abs(goal_edge) * 0.02
    if is_big_match:
        heuristic_draw += 0.03
        heuristic_target -= 0.02
    head_to_head = head_to_head_draw_signal(target_team, opponent_name)
    if head_to_head.get("available"):
        # Gerçek kafa kafaya beraberlik oranını örneklem büyüklüğüne göre ağırlıklandırarak
        # draw olasılığına bir prior olarak karıştırır (bkz. PROJECT_STATE.md: bu proje
        # uzun süredir "kafa kafaya tarihsel beraberlik oranı gerekir" tespitindeydi).
        h2h_weight = min(0.35, 0.12 + head_to_head["matches"] * 0.01)
        heuristic_draw = heuristic_draw * (1 - h2h_weight) + head_to_head["draw_rate"] * h2h_weight
    heuristic_target = min(max(heuristic_target, 0.18), 0.68)
    heuristic_draw = min(max(heuristic_draw, 0.18), 0.36)
    heuristic_opp = max(0.08, 1 - heuristic_target - heuristic_draw)
    heuristic_total = heuristic_target + heuristic_draw + heuristic_opp
    heuristic = {
        "target": heuristic_target / heuristic_total,
        "draw": heuristic_draw / heuristic_total,
        "opponent": heuristic_opp / heuristic_total,
    }
    blended = {
        key: poisson[key] * 0.62 + heuristic[key] * 0.38
        for key in ("target", "draw", "opponent")
    }
    total = sum(blended.values())
    target_win = blended["target"] / total
    draw = blended["draw"] / total
    opponent_win = blended["opponent"] / total
    draw_calibration = draw_calibration_signal(
        goal_edge=goal_edge,
        strength_edge=strength_edge,
        expected_goals_for=expected_goals_for,
        expected_goals_against=expected_goals_against,
        is_big_match=is_big_match,
        team_form=team_form,
        opponent_recent_form=opponent_recent_form,
        head_to_head=head_to_head,
    )
    big_match_profile = big_match_profile_signal(
        is_big_match=is_big_match,
        target_side=target_side,
        goal_edge=goal_edge,
        strength_edge=strength_edge,
        draw_calibration=draw_calibration,
        referee_signal=referee_signal,
    )

    referee_cards = referee_signal.get("cards_per_match") if referee_signal.get("prior_matches") else None
    card_expectation = card_base
    if referee_cards:
        card_expectation = (card_expectation + referee_cards / 2) / 2
    if is_big_match:
        card_expectation += 0.6

    top_probability = max(target_win, draw, opponent_win)
    sorted_probs = sorted([target_win, draw, opponent_win], reverse=True)
    margin = sorted_probs[0] - sorted_probs[1]
    confidence = "LOW"
    if top_probability >= 0.5 and margin >= 0.14:
        confidence = "MEDIUM"
    if top_probability >= 0.58 and margin >= 0.22:
        confidence = "HIGH"
    if missing_count >= 2:
        confidence = "LOW_AVAILABILITY"
    scorelines = scoreline_probabilities(expected_goals_for, expected_goals_against)
    call = recommended_call(target_win, draw, opponent_win, scorelines, confidence, is_big_match)
    draw_risk = preview_draw_risk_signal(
        target_win=target_win,
        draw=draw,
        opponent_win=opponent_win,
        expected_goals_for=expected_goals_for,
        expected_goals_against=expected_goals_against,
        strength_edge=strength_edge,
        confidence=confidence,
        scorelines=scorelines,
        draw_calibration=draw_calibration,
        big_match_profile=big_match_profile,
    )
    if draw_risk["protected_prediction"]:
        call["action"] = draw_risk["recommended_model_action"]
        call["action_label"] = action_label(draw_risk["recommended_model_action"])
        call["risk_notes"] = list(dict.fromkeys(call["risk_notes"] + draw_risk["reasons"]))
    display_prediction = calibrated_display_prediction(
        call,
        draw_risk,
        target_win,
        draw,
        opponent_win,
        is_big_match=is_big_match,
        strength_edge=strength_edge,
        expected_goals_for=expected_goals_for,
        expected_goals_against=expected_goals_against,
        card_signal="HIGH" if card_expectation >= 3 else "MEDIUM" if card_expectation >= 2 else "LOW",
        target_team=target_team,
        opponent_name=opponent_name,
        enable_calibration=enable_display_calibration,
    )
    return {
        "target_win_probability": round(target_win, 3),
        "draw_probability": round(draw, 3),
        "opponent_win_probability": round(opponent_win, 3),
        "expected_goals_for": expected_goals_for,
        "expected_goals_against": expected_goals_against,
        "top_scorelines": scorelines[:6],
        "recommended_scoreline": scorelines[0],
        "recommended_call": call,
        "display_prediction": display_prediction,
        "over_2_5_signal": "HIGH" if expected_goals_for + expected_goals_against >= 2.7 else "MEDIUM",
        "team_card_expectation": round(card_expectation, 2),
        "card_signal": "HIGH" if card_expectation >= 3 else "MEDIUM" if card_expectation >= 2 else "LOW",
        "availability_missing_count": missing_count,
        "strength_edge": round(strength_edge, 3),
        "draw_calibration": draw_calibration,
        "head_to_head": head_to_head,
        "draw_risk": draw_risk,
        "big_match_profile": big_match_profile,
        "confidence": confidence,
        "xg_data_available": xg_data_available,
        "note": "Poisson, form, rakip savunma, hakem, eksik oyuncu ve takım gücü sinyaliyle çalışan MVP tahmin modelidir.",
    }
