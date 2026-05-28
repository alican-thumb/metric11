from __future__ import annotations

import csv
import json
import math
from pathlib import Path

from src.config import PROCESSED_DIR

_OUT_CSV = PROCESSED_DIR / "player_attribute_dataset_fm_derived_2025_2026.csv"
_OUT_JSON = PROCESSED_DIR / "player_attribute_dataset_fm_derived_2025_2026.json"

_FIELDNAMES = [
    "Name", "Club", "Age", "Position",
    "Current Ability", "Potential Ability",
    "Pace", "Acceleration", "Stamina", "Work Rate",
    "Finishing", "Passing", "Tackling", "Technique",
    "Positioning", "Decisions", "Teamwork", "Vision",
]


def main() -> None:
    scout = json.loads((PROCESSED_DIR / "league_scouting_enriched_2025_2026.json").read_text(encoding="utf-8"))
    players = scout.get("enriched_shortlist", [])

    records = [_derive(p) for p in players]

    with _OUT_CSV.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=_FIELDNAMES)
        writer.writeheader()
        writer.writerows({k: r[k] for k in _FIELDNAMES} for r in records)

    payload = {
        "source": {
            "name": "metric11 türetilmiş FM attribute verisi",
            "method": "TFF 2025/26 maç istatistikleri + API-Football 2024 sinyali",
            "license_status": "INTERNAL_DERIVED — dış kaynak gerektirmez",
            "risk_level": "LOW",
        },
        "summary": {
            "players": len(records),
            "with_external_boost": sum(1 for r in records if r["_external_matched"]),
            "avg_ca": round(sum(r["Current Ability"] for r in records) / len(records), 1) if records else 0,
        },
        "players": records,
    }
    _OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Üretildi: {len(records)} oyuncu → {_OUT_CSV.name}")
    print(f"Dış API eşleşmesi: {payload['summary']['with_external_boost']} oyuncu")
    print(f"Ortalama CA: {payload['summary']['avg_ca']}")


def _derive(p: dict) -> dict:
    ext = p.get("external_api_signal") or {}
    matched = bool(ext.get("matched"))

    starts   = p.get("starts", 0) or 0
    bench    = p.get("bench", 0) or 0
    goals    = p.get("goals", 0) or 0
    cards    = p.get("cards", 0) or 0
    avail    = p.get("availability_score", 0) or 0
    age      = p.get("age") or 28
    pos_grp  = (p.get("tm_position_group") or "").upper()
    km_mid   = ((p.get("estimated_physical_load_km_min") or 9.5) +
                (p.get("estimated_physical_load_km_max") or 10.5)) / 2

    gps   = goals / starts if starts > 0 else 0
    cps   = cards / starts if starts > 0 else 0

    # dış API sinyali
    ext_rating      = ext.get("rating") or 0
    ext_key_passes  = ext.get("key_passes") or 0
    ext_tackles     = ext.get("tackles") or 0
    ext_intercepts  = ext.get("interceptions") or 0
    ext_duels_won   = ext.get("duels_won") or 0
    ext_assists     = ext.get("assists") or 0
    ext_minutes     = ext.get("minutes") or 0

    # --- attribute hesapları ---
    pace         = _pace(km_mid, pos_grp, age)
    acceleration = _clamp(round(pace - max(0, (age - 27) * 0.4) + (1 if pos_grp == "FWD" else 0)), 1, 20)
    stamina      = _stamina(avail, starts, km_mid, ext_minutes)
    work_rate    = _work_rate(starts, bench, km_mid, pos_grp)
    finishing    = _finishing(gps, goals, pos_grp, ext_rating, matched)
    passing      = _passing(pos_grp, ext_key_passes, ext_assists, starts, matched)
    tackling     = _tackling(pos_grp, cps, ext_tackles, ext_intercepts, ext_duels_won, matched)
    technique    = _technique(gps, pos_grp, ext_rating, matched)
    positioning  = _positioning(starts, avail, pos_grp)
    decisions    = _decisions(cps, avail, starts, ext_rating, matched)
    teamwork     = _teamwork(avail, cps, bench, starts)
    vision       = _vision(pos_grp, ext_key_passes, ext_assists, starts, matched)

    ca = _current_ability(
        finishing, passing, tackling, technique,
        positioning, decisions, stamina, pace, work_rate,
        pos_grp, ext_rating, matched,
    )
    pa = _potential_ability(ca, age)

    return {
        "Name":             p.get("name", ""),
        "Club":             p.get("team", ""),
        "Age":              age,
        "Position":         _fm_pos(pos_grp, p.get("tm_position", "")),
        "Current Ability":  ca,
        "Potential Ability": pa,
        "Pace":             pace,
        "Acceleration":     acceleration,
        "Stamina":          stamina,
        "Work Rate":        work_rate,
        "Finishing":        finishing,
        "Passing":          passing,
        "Tackling":         tackling,
        "Technique":        technique,
        "Positioning":      positioning,
        "Decisions":        decisions,
        "Teamwork":         teamwork,
        "Vision":           vision,
        "_external_matched": matched,
    }


# ── attribute fonksiyonları ──────────────────────────────────────────────────

def _pace(km_mid: float, pos_grp: str, age: int) -> int:
    base = _sigmoid_scale(km_mid, center=10.5, steepness=1.8, lo=6, hi=18)
    pos_bonus = {"FWD": 1.5, "MID": 0.5, "DEF": -0.5, "GK": -3}.get(pos_grp, 0)
    age_penalty = max(0, (age - 29) * 0.35)
    return _clamp(round(base + pos_bonus - age_penalty), 1, 20)


def _stamina(avail: float, starts: int, km_mid: float, ext_minutes: int) -> int:
    base = avail / 100 * 10 + 5
    starts_bonus = min(3, starts / 34 * 3)
    km_bonus = min(2, (km_mid - 9.5) * 0.8)
    ext_bonus = 1 if ext_minutes >= 2500 else 0
    return _clamp(round(base + starts_bonus + km_bonus + ext_bonus), 1, 20)


def _work_rate(starts: int, bench: int, km_mid: float, pos_grp: str) -> int:
    activity = (starts * 1.2 + bench * 0.4) / 40
    base = _sigmoid_scale(activity, center=0.9, steepness=4, lo=6, hi=17)
    km_bonus = min(1.5, (km_mid - 10.0) * 0.8)
    pos_bonus = {"MID": 1, "FWD": 0.5, "DEF": 0, "GK": -3}.get(pos_grp, 0)
    return _clamp(round(base + km_bonus + pos_bonus), 1, 20)


def _finishing(gps: float, goals: int, pos_grp: str, ext_rating: float, matched: bool) -> int:
    base = _sigmoid_scale(gps, center=0.25, steepness=8, lo=2, hi=18)
    if goals >= 15:
        base += 1.5
    elif goals >= 10:
        base += 0.8
    if pos_grp == "GK":
        return _clamp(round(base * 0.2 + 1), 1, 5)
    if pos_grp == "DEF":
        base = min(base, 11)
    ext_bonus = min(1.5, max(0, (ext_rating - 7.0) * 0.8)) if matched else 0
    return _clamp(round(base + ext_bonus), 1, 20)


def _passing(pos_grp: str, key_passes: int, assists: int, starts: int, matched: bool) -> int:
    if matched and starts > 0:
        kp_per_match = key_passes / max(starts, 1)
        base = _sigmoid_scale(kp_per_match, center=1.2, steepness=3, lo=6, hi=17)
        base += min(1.5, assists / max(starts, 1) * 6)
    else:
        base = {"MID": 12, "FWD": 10, "DEF": 9, "GK": 8}.get(pos_grp, 9)
    return _clamp(round(base), 1, 20)


def _tackling(pos_grp: str, cps: float, tackles: int, intercepts: int,
              duels_won: int, matched: bool) -> int:
    if matched:
        defensive_score = tackles * 0.06 + intercepts * 0.09 + duels_won * 0.012
        base = _sigmoid_scale(defensive_score, center=5, steepness=0.5, lo=4, hi=17)
    else:
        base = {"DEF": 13, "MID": 9, "FWD": 5, "GK": 3}.get(pos_grp, 8)
    discipline_bonus = max(-2, -cps * 6)
    return _clamp(round(base + discipline_bonus), 1, 20)


def _technique(gps: float, pos_grp: str, ext_rating: float, matched: bool) -> int:
    base = _sigmoid_scale(gps, center=0.2, steepness=7, lo=5, hi=17)
    pos_adjust = {"FWD": 1, "MID": 0.5, "DEF": -1, "GK": -3}.get(pos_grp, 0)
    ext_bonus = min(2, max(0, (ext_rating - 6.8) * 1.2)) if matched else 0
    return _clamp(round(base + pos_adjust + ext_bonus), 1, 20)


def _positioning(starts: int, avail: float, pos_grp: str) -> int:
    consistency = (starts / 34) * (avail / 100)
    base = _sigmoid_scale(consistency, center=0.6, steepness=5, lo=6, hi=16)
    pos_adjust = {"FWD": 1.5, "MID": 0.5, "DEF": 0, "GK": -1}.get(pos_grp, 0)
    return _clamp(round(base + pos_adjust), 1, 20)


def _decisions(cps: float, avail: float, starts: int, ext_rating: float, matched: bool) -> int:
    discipline = max(0, 16 - cps * 18)
    avail_bonus = min(2, avail / 100 * 2)
    exp_bonus = min(1.5, starts / 34 * 1.5)
    ext_bonus = min(2, max(0, (ext_rating - 7.0) * 1.5)) if matched else 0
    return _clamp(round(discipline + avail_bonus + exp_bonus + ext_bonus), 1, 20)


def _teamwork(avail: float, cps: float, bench: int, starts: int) -> int:
    base = avail / 100 * 10 + 5
    discipline = max(-2, -cps * 5)
    bench_bonus = min(1, bench / 20)
    return _clamp(round(base + discipline + bench_bonus), 1, 20)


def _vision(pos_grp: str, key_passes: int, assists: int, starts: int, matched: bool) -> int:
    if matched and starts > 0:
        creative = (key_passes + assists * 2) / max(starts, 1)
        base = _sigmoid_scale(creative, center=1.5, steepness=2.5, lo=5, hi=17)
    else:
        base = {"MID": 11, "FWD": 9, "DEF": 7, "GK": 6}.get(pos_grp, 8)
    return _clamp(round(base), 1, 20)


def _current_ability(finishing: int, passing: int, tackling: int, technique: int,
                     positioning: int, decisions: int, stamina: int, pace: int,
                     work_rate: int, pos_grp: str, ext_rating: float, matched: bool) -> int:
    key = {
        "FWD": [finishing, technique, positioning, decisions, stamina, pace],
        "MID": [passing, decisions, technique, work_rate, stamina, positioning],
        "DEF": [tackling, decisions, positioning, stamina, pace, work_rate],
        "GK":  [decisions, positioning, stamina, work_rate],
    }.get(pos_grp, [finishing, passing, tackling, decisions, stamina, positioning])

    avg = sum(key) / len(key)
    ca = round(65 + avg * 4.0)
    if matched and ext_rating >= 7.0:
        ca += round((ext_rating - 6.8) * 5)
    return _clamp(ca, 60, 165)


def _potential_ability(ca: int, age: int) -> int:
    if age <= 20:
        growth = 35
    elif age <= 22:
        growth = 25
    elif age <= 24:
        growth = 18
    elif age <= 26:
        growth = 10
    elif age <= 29:
        growth = 4
    else:
        growth = 0
    return _clamp(ca + growth, ca, 190)


def vision_proxy(pos_grp: str) -> int:
    return {"MID": 11, "FWD": 9, "DEF": 7, "GK": 6}.get(pos_grp, 8)


def teamwork_proxy(pos_grp: str) -> int:
    return {"DEF": 12, "MID": 11, "FWD": 10, "GK": 12}.get(pos_grp, 10)


def _fm_pos(pos_grp: str, tm_pos: str) -> str:
    if tm_pos:
        return tm_pos
    return {"FWD": "ST", "MID": "MC", "DEF": "DC", "GK": "GK"}.get(pos_grp, "MC")


def _sigmoid_scale(x: float, center: float, steepness: float, lo: float, hi: float) -> float:
    sig = 1 / (1 + math.exp(-steepness * (x - center)))
    return lo + (hi - lo) * sig


def _clamp(value: int | float, lo: int, hi: int) -> int:
    return max(lo, min(hi, int(round(value))))


if __name__ == "__main__":
    main()
