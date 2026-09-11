"""UEFA Şampiyonlar Ligi, Avrupa Ligi ve Konferans Ligi 2026-27 maç tahminleri.

football-data.org fixtures verisi üzerinden Poisson bazlı tahmin üretir.
Form verisi: turnuvadaki geçmiş maçlar + (2026-09-04'ten itibaren) 7 büyük iç ligin
GÜNCEL sezon puan durumuyla harmanlanmış UEFA katsayısı bazlı başlangıç gücü
(bkz. collect_domestic_league_form.py, `_strength()`) — statik 2024-25 tablosu artık
tek başına belirleyici değil, transfer/mevcut-form etkisini turnuva maçları oynanmadan
ÖNCE de yansıtır.
Çıktı: data/processed/european_predictions_2026_2027.json
"""
from __future__ import annotations

import json
import math
import re
import sys
import unicodedata
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
    # Tier 1 — Elite (88-100)
    "Real Madrid":           98, "Manchester City":      96,
    "Bayern Munich":         93, "Liverpool":            90,
    "Arsenal":               87, "Barcelona":            86,
    "Paris Saint-Germain":   85, "Inter Milan":          84,
    "Bayer 04 Leverkusen":   86, "Borussia Dortmund":    81,
    "Atlético de Madrid":    83, "Atalanta":             80,
    # Tier 2 — Strong (70-85)
    "Chelsea":               79, "Manchester United":    73,
    "Juventus":              76, "AC Milan":             77,
    "Napoli":                75, "RB Leipzig":           77,
    "Aston Villa":           74, "Real Betis":           68,
    "Porto":                 71, "Benfica":              70,
    "Sporting CP":           67, "PSV Eindhoven":        68,
    "Feyenoord":             67, "Lazio":                65,
    "Roma":                  67, "Monaco":               64,
    "Villarreal CF":         65, "Real Sociedad":        62,
    "Sevilla FC":            61, "Marseille":            66,
    "Girona FC":             64, "Lille OSC":            67,
    # Tier 3 — Competitive (50-67)
    "Galatasaray":           64, "Fenerbahçe":           62,
    "Beşiktaş":              54, "Trabzonspor":          50,
    "Başakşehir":            46, "Kasımpaşa":            40,
    "Club Brugge":           62, "Anderlecht":           52,
    "Celtic":                60, "Rangers":              57,
    "FC Salzburg":           64, "Sturm Graz":           52,
    "FC Shakhtar Donetsk":   60, "Dynamo Kyiv":          48,
    "Crvena zvezda":         57, "Partizan":             45,
    "GNK Dinamo Zagreb":     52, "Hajduk Split":         44,
    "Slavia Praha":          54, "Sparta Praha":         56,
    "BSC Young Boys":        53, "FC Basel":             50,
    "Ajax":                  68, "Utrecht":              48,
    "Eintracht Frankfurt":   70, "Wolfsburg":            60,
    "Hoffenheim":            58, "Leverkusen":           86,
    "VfB Stuttgart":         72, "SC Freiburg":          62,
    "Valencia CF":           60, "Athletic Club":        65,
    "Celta de Vigo":         55, "Getafe CF":            52,
    "Nice":                  62,
    "Rennes":                57, "Toulouse FC":          52,
    "Bologna FC":            64, "Torino FC":            55,
    "Udinese Calcio":        48, "Sassuolo":             50,
    "Hellas Verona":         46, "Genoa CFC":            48,
    "PAOK FC":               55, "Olympiakos CF":        52,
    "Panathinaikos":         48, "AEK Athens FC":        50,
    "Legia Warszawa":        48, "Rakow Czestochowa":    46,
    "Rapid Wien":            50, "Austria Wien":         44,
    "HJK Helsinki":          42, "FK RFS":               38,
    "Shamrock Rovers":       40, "FC Midtjylland":       56,
    "FC Copenhagen":         58, "Rosenborg BK":         46,
    "Malmö FF":              54, "IFK Göteborg":         48,
    "Ferencváros":           54, "MTK Budapest":         42,
    "APOEL FC":              44, "Maccabi Tel Aviv":     50,
    "Lincoln Red Imps":      32, "Hammarby IF":          50,
    "FC Lorient":            54, "Stade Brestois 29":    58,
    "RC Lens":               61, "Stade de Reims":       55,
    "Viktoria Plzen":        52, "FK Jablonec":          40,
    "Sheriff Tiraspol":      48, "FC Astana":            42,
    "Ludogorets Razgrad":    46, "CSKA Sofia":           40,
    "Paços de Ferreira":     40, "Braga":                62,
    "Vitória SC":            50, "Boavista":             46,
    "Lech Poznan":           52, "Wisla Krakow":         44,
    "AIK":                   48, "BK Häcken":            46,
    # 2026-09-07 eklendi — 2026-27 Avrupa kupası fikstüründe bu tabloda hiç karşılığı
    # olmayan (isim eşleşmesi ne substring ne token-overlap ile mümkün OLMAYAN, çünkü
    # gerçekten hiç girilmemiş) kulüpler. Tahmini, kaba tier değerleri — sabit bir resmi
    # kaynağa dayanmıyor, yalnızca 48 (jenerik varsayılan) yerine geçmiş Avrupa
    # performansına göre kabaca konumlandırma. Elit değiller ama tamamen jenerik de değiller.
    "Como 1907":             46, "FK Bodø/Glimt":        58,
    "LASK Linz":             50, "Sabah FK":             36,
    "Viking FK":             44, "ŠK Slovan Bratislava": 48,
}

# football-data.org'un tam resmi adı ile tablodaki kısa/yaygın ad arasında ne substring
# ne token-overlap ile çözülebilen (dil farkı: "Internazionale"≠"Inter", "AEK" gibi kısa
# kodlar) birkaç bilinen istisna. `_static_strength` önce bunu, sonra token-overlap'i dener.
_TEAM_STRENGTH_ALIASES: dict[str, str] = {
    "FC INTERNAZIONALE MILANO": "Inter Milan",
}

_DEFAULT_STRENGTH = 48.0
_HOME_ADVANTAGE   = 1.08   # UCL/UEL nötr saha oranı (Wembley, San Siro, vs.)
_BASE_GOALS       = 1.42   # UCL 2023-25 ortalama gol/takım/maç
_DRAW_CALIBRATION = 1.18   # UCL grup aşaması gerçek draw oranı ~%26 (Poisson ~%22)
_MAX_GOALS        = 8

DOMESTIC_FORM_PATH = PROCESSED_DIR / "domestic_league_form_2026_2027.json"
# Statik tablo 2024-25 UEFA katsayısına donuk kalır (transfer/form değişikliğini hiç
# yansıtmaz). Mevcutsa, ücretsiz football-data.org planında zaten erişilebilen 7 büyük
# iç ligin (bkz. collect_domestic_league_form.py) GÜNCEL sezon puan ortalaması bu statik
# değere harmanlanır — turnuvanın kendi maçları oynanmadan önce bile (`_att_lambda`/
# `_def_lambda`'daki turnuva-içi form ayrıca, bağımsız olarak devam eder).
_DOMESTIC_FORM_CACHE: dict[str, dict] | None = None
_DOMESTIC_FORM_MAX_WEIGHT = 0.5  # iç lig formu statik tabloyu en fazla yarı yarıya ağırlıklandırır


def _load_domestic_form() -> dict[str, dict]:
    global _DOMESTIC_FORM_CACHE
    if _DOMESTIC_FORM_CACHE is None:
        try:
            payload = json.loads(DOMESTIC_FORM_PATH.read_text(encoding="utf-8"))
            _DOMESTIC_FORM_CACHE = payload.get("teams", {})
        except (FileNotFoundError, json.JSONDecodeError):
            _DOMESTIC_FORM_CACHE = {}
    return _DOMESTIC_FORM_CACHE


def _domestic_form_for(name: str) -> dict | None:
    form = _load_domestic_form()
    for k, v in form.items():
        if k.lower() in name.lower() or name.lower() in k.lower():
            return v
    return None


def _strength(name: str) -> float:
    static = _static_strength(name)
    row = _domestic_form_for(name)
    if not row or row.get("played", 0) < 1:
        return static
    ppg = row.get("points_per_game", 1.0)
    domestic_strength = max(15.0, min(100.0, 30.0 + ppg * 22.0))
    weight = min(_DOMESTIC_FORM_MAX_WEIGHT, row["played"] / 8)
    return static * (1 - weight) + domestic_strength * weight


# 2026-09-07 bulgusu: eski `k.lower() in name.lower()` TAM ALT-DİZİ eşleşmesi, football-
# data.org'un tam resmi adlarının ("FC Bayern München", "FC Internazionale Milano") tablodaki
# kısa/yaygın adlarla ("Bayern Munich", "Inter Milan") HİÇ eşleşmemesine yol açıyordu — 2026-27
# Avrupa fikstüründeki 36 takımın 11'i (Bayern Münih ve Inter Milan dahil — ikisi de tabloda
# elit/93-84 puanlı!) sessizce jenerik varsayılana (48) düşüyordu, maçları ciddi çarpıtıyordu.
# Düzeltme: normalize edilmiş isim üzerinde token-overlap (kulüp isimlerindeki jenerik "FC/SK/
# 1907" gibi ekler hariç), en çok ortak token'ı olan aday kazanır (ör. "Manchester City" vs
# "Manchester United" tek "MANCHESTER" ortak tokeniyle değil, "CITY"/"UNITED" farkıyla ayrılır).
_STRENGTH_MATCH_STOPWORDS = {
    "FC", "SK", "AS", "CF", "SC", "AFC", "FK", "CD", "UD", "RC", "KV", "US",
    "PAE", "TSV", "SV", "VFB", "VFL", "BSC", "1907", "CLUB", "CLUBE", "DE",
}


def _normalize_club_name(name: str) -> str:
    cleaned = unicodedata.normalize("NFKD", name or "")
    cleaned = "".join(ch for ch in cleaned if not unicodedata.combining(ch))
    cleaned = re.sub(r"[^A-Za-z0-9 ]+", " ", cleaned).upper()
    return re.sub(r"\s+", " ", cleaned).strip()


def _strength_tokens(name: str) -> set[str]:
    return {t for t in _normalize_club_name(name).split() if len(t) >= 3 and t not in _STRENGTH_MATCH_STOPWORDS}


_club_strength_tokens_cache: dict[str, set[str]] | None = None


def _club_strength_tokens() -> dict[str, set[str]]:
    global _club_strength_tokens_cache
    if _club_strength_tokens_cache is None:
        _club_strength_tokens_cache = {k: _strength_tokens(k) for k in _CLUB_STRENGTH}
    return _club_strength_tokens_cache


def _static_strength(name: str) -> float:
    alias = _TEAM_STRENGTH_ALIASES.get(_normalize_club_name(name))
    if alias:
        return _CLUB_STRENGTH[alias]
    name_tokens = _strength_tokens(name)
    if name_tokens:
        scored = [
            (len(name_tokens & candidate_tokens), key)
            for key, candidate_tokens in _club_strength_tokens().items()
            if name_tokens & candidate_tokens
        ]
        if scored:
            scored.sort(key=lambda item: item[0], reverse=True)
            best_score = scored[0][0]
            winners = [key for score, key in scored if score == best_score]
            if len(winners) == 1:
                return _CLUB_STRENGTH[winners[0]]
            # 2026-09-08 kod incelemesi bulgusu: birden fazla aday eşit skorla eşleşirse
            # (ör. yalnız "Milan" gelirse "AC Milan" ve "Inter Milan" ikisi de tek ortak
            # tokenle eşleşir) eskiden aşağıdaki BAĞIMSIZ alt-dizi son çaresine düşülüyordu —
            # bu, eşleşen adaylardan HİÇBİRİNE bakmadan kendi sözlük sırasına göre rastgele
            # (ve yanlış olabilecek) bir kulüp seçebiliyordu. Belirsiz kalınca dürüstçe
            # jenerik varsayılana düş — yanlış kesin bir kulüp seçmekten daha güvenli.
            return _DEFAULT_STRENGTH
    # Alt-dizi (substring) son çare — yukarıdaki token eşleşmesi hiçbir aday bulamadıysa
    # (ör. tamamen kısa/tek kelimelik adlar) eski davranış korunur.
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
    """En olası kazananın (hw/dr/aw) skor grubu içinde en yüksek Poisson ortak
    olasılıklı skoru seçer.

    2026-09-11 bulgusu: eski sürüm λ'ları en yakın tam sayıya yuvarlayıp kazananı
    tutturmak için sadece +1 dürtüyordu. UCL/UEL maçlarında λ neredeyse hep 1.0-1.6
    aralığına düştüğünden (BASE_GOALS=1.42, home advantage 1.08) bu mekanik olarak
    144 tahminin %90'ını 2-1/1-2'ye sabitliyordu; 0-0, 1-0, 1-1, 2-0 gibi gerçekçi
    skorlar hiç çıkmıyordu. Artık gerçek ortak olasılık dağılımından o kazanma
    grubundaki (ev/berabere/deplasman) en olası skor seçiliyor — skorlar takımların
    gerçek gol beklentisine göre çeşitleniyor.
    """
    if hw >= dr and hw >= aw:
        outcome = "home"
    elif dr >= hw and dr >= aw:
        outcome = "draw"
    else:
        outcome = "away"

    best_score = (0, 0)
    best_prob = -1.0
    for h in range(_MAX_GOALS + 1):
        for a in range(_MAX_GOALS + 1):
            if outcome == "home" and h <= a:
                continue
            if outcome == "away" and a <= h:
                continue
            if outcome == "draw" and h != a:
                continue
            p = _poisson_prob(lam_h, h) * _poisson_prob(lam_a, a)
            if p > best_prob:
                best_prob = p
                best_score = (h, a)
    return best_score


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
