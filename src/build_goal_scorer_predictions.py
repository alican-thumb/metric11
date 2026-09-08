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

KRİTİK GÜVENLİK KOŞULU (2026-09-04, kullanıcı bulgusu — bkz. PROJECT_STATE): "projected"
oranı yalnızca oyuncu bu sezon (2026-27) EN AZ BİR resmi lig maçının kadrosunda (11 veya
yedek) GERÇEKTEN yer almışsa uygulanır (`tff_super_lig_matches_2026_2027.json`'dan). TM
kadro sayfasında görünmek transfer olduğu/piyasa değeri olduğu anlamına gelir ama O MAÇ
İÇİN kayıtlı/uygun olduğu anlamına GELMEZ (uluslararası transfer belgesi, lisans, tescil
gecikmesi vb.) — Galatasaray'a yeni transfer olup henüz hiç resmi maç kadrosunda yer
almamış bir oyuncu (ör. bu tespitte Rafael Leão) "olası golcü" olarak gösterilmişti,
oysa o akşamki maçın kadrosunda bile yoktu. Bu koşul olmadan "projected" tamamen KALDIRILIR
(hiç tahmin üretilmez) — yanlış oyuncu göstermektense veri-yok tercih edilir ilkesi
korunur. Bu koşul, ligde zaten oynamaya başlamış transferleri (ör. Vlahović, Miretti,
Poku — hepsi ilk 3 haftada kadroya girdi) hâlâ doğru şekilde gösterir.

MAÇ GÜNÜ KADRO TAKİBİ (2026-09-04): `collect_live_lineups.py` kickoff'tan birkaç saat
önce TFF'nin sayfasında kadro yayınlanıp yayınlanmadığını dener; yayınlanmışsa
(`live_lineups_2026_2027.json`) o maçın golcü adayları SADECE o günkü kadroda (11 veya
yedek) olan oyuncularla sınırlanır — yalnızca yeni transferler için değil, herkes için:
2025-26'da çok gol atmış ama bugün sakat/cezalı/rotasyonda olan bir oyuncu da artık
gösterilmez. Kadro henüz yayınlanmamışsa (çoğu maç için — kickoff'a saatler var) eski
davranış (sezonluk TM kadrosu + görünürlük koşulları) aynen sürer. `lineup_confirmed`
alanı bu maç için kadronun doğrulanıp doğrulanmadığını gösterir.

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
CURRENT_SEASON_MATCHES_PATH = PROCESSED_DIR / "tff_super_lig_matches_2026_2027.json"
OUTPUT_PATH = PROCESSED_DIR / "goal_scorer_predictions_2026_2027.json"

OWN_GOAL_TYPE = "K"
MIN_STARTS = 3          # oran güvenilir sayılmadan önce minimum başlangıç-XI sayısı
TOP_N_PER_SIDE = 3       # kartta gösterilecek olası golcü sayısı
EXCLUDED_POSITION_GROUPS = {"GK"}  # kaleciler skorer sıralamasından hariç
PROJECTED_POSITION_GROUPS = {"FWD", "MID"}  # 2025-26'da oynamamış (yeni transfer/yabancı) hücum oyuncuları için tahmini oran
PROJECTED_VALUE_MULT_RANGE = (0.3, 3.0)  # piyasa değeri çarpanı sınırı (aşırı uç değerleri sınırlamak için)
PROJECTED_UNVALUED_MULT = 0.5  # piyasa değeri bilinmeyen yeni transferler için varsayılan (ortalamanın altı) çarpan
# 2026-09-08 bulgusu: oran SADECE 2025-26 tam sezonundan geliyordu — Vlahović gibi 2025-26'da
# hiç oynamamış ama 2026-27'de 4 maçta 4 gol atan bir oyuncu, gerçek golcü formu tamamen
# GÖRMEZDEN GELİNİP piyasa-değeri-bazlı jenerik "projected" orana düşürülüyordu. 2025-26'dan
# daha kısa bir eşik (sezon henüz birkaç hafta) + gerçek 2025-26 oranıyla ağırlıklı harman.
CURRENT_SEASON_MIN_STARTS = 2   # 2026-27 kısa sezon için MIN_STARTS'tan (3) daha gevşek eşik
CURRENT_SEASON_BLEND_MAX_WEIGHT = 0.7  # güncel form, yeterince maç birikince en fazla %70 ağırlık alır
CURRENT_SEASON_BLEND_STARTS_FOR_MAX = 8  # bu kadar 2026-27 başlangıçta tam ağırlığa ulaşır

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


def players_with_2026_27_appearance() -> set[str]:
    """canonical_player_name kümesi: bu sezon EN AZ BİR resmi maç kadrosunda (11/yedek) yer almış oyuncular.

    "projected" (tahmini) skorer oranının uygulanabilmesi için zorunlu ön koşul — bkz.
    modül docstring'i (2026-09-04 kullanıcı bulgusu). TM kadrosunda olmak tescilli/uygun
    olduğu anlamına gelmez; bu sezon gerçekten bir maç kadrosuna girmiş olmak daha güçlü
    bir sinyaldir.
    """
    if not CURRENT_SEASON_MATCHES_PATH.exists():
        return set()
    matches = json.loads(CURRENT_SEASON_MATCHES_PATH.read_text(encoding="utf-8"))
    appeared: set[str] = set()
    for m in matches:
        for side in ("home", "away"):
            lineup = m.get("lineups", {}).get(side, {})
            for group in ("starting", "bench"):
                for p in lineup.get(group, []) or []:
                    appeared.add(canonical_player_name(p.get("name")))
    return appeared


def load_live_lineup_names() -> dict[str, dict[str, set[str]]]:
    """match_id(str) -> {"home": {canonical_player_name...}, "away": {...}}.

    `collect_live_lineups.py`'nin maç başlamadan yakaladığı kadrolar — mevcutsa bu, elimizdeki
    EN KESİN sinyaldir: yalnızca "bu sezon oynadı mı" değil, "BUGÜN o maçın kadrosunda mı"
    diye bakar. Bir maç için varsa, o maçın golcü adayları BUNUNLA sınırlanır (2025-26'da
    çok gol atmış ama bugün kadroda/11'de olmayan — ör. sakat/cezalı/rotasyon — bir oyuncu
    da artık gösterilmez, yalnız yeni transferler için değil).
    """
    path = PROCESSED_DIR / "live_lineups_2026_2027.json"
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    out: dict[str, dict[str, set[str]]] = {}
    for match_id, m in payload.get("matches", {}).items():
        sides: dict[str, set[str]] = {}
        for side in ("home", "away"):
            lineup = m.get("lineups", {}).get(side, {})
            names = {
                canonical_player_name(p.get("name"))
                for group in ("starting", "bench")
                for p in (lineup.get(group, []) or [])
            }
            sides[side] = names
        out[match_id] = sides
    return out


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
    current_goals: dict[str, int] = {}
    current_starts: dict[str, int] = {}
    if CURRENT_SEASON_MATCHES_PATH.exists():
        current_matches = json.loads(CURRENT_SEASON_MATCHES_PATH.read_text(encoding="utf-8"))
        current_goals, current_starts = build_player_goal_history(current_matches)
    rosters = build_team_rosters()
    appeared_this_season = players_with_2026_27_appearance()
    live_lineups = load_live_lineup_names()

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

    def _side_candidates(team_fixture_name: str, lam: float, allowed_names: set[str] | None = None) -> list[dict]:
        roster = rosters.get(_canon(team_fixture_name), [])
        rated = []
        for p in roster:
            key = canonical_player_name(p.get("name"))
            if allowed_names is not None and key not in allowed_names:
                continue
            n_starts = starts.get(key, 0)
            cur_starts = current_starts.get(key, 0)
            cur_goals = current_goals.get(key, 0)
            # Güncel form ağırlığı: 0 maçla 0, CURRENT_SEASON_BLEND_STARTS_FOR_MAX maçta tavana
            # ulaşır — 2026-09-08 düzeltmesi öncesi yalnız 2025-26 sezonu kullanılıyordu (ör.
            # Vlahović 2026-27'de 2 başlangıçta 4 gol atmışken tamamen görmezden geliniyordu).
            # Az maçlı örneklemin gürültüsünü (2 maç 4 gol = ham oran 2.0, gerçekçi değil)
            # bastırmak için HAM oran hiçbir zaman tek başına kullanılmıyor — her zaman bir
            # taban orana (geçmiş sezon veya pozisyon ortalaması) karışık ağırlıkla eklenir.
            cur_weight = min(CURRENT_SEASON_BLEND_MAX_WEIGHT, cur_starts / CURRENT_SEASON_BLEND_STARTS_FOR_MAX) if cur_starts > 0 else 0.0
            cur_rate = (cur_goals / cur_starts) if cur_starts > 0 else 0.0
            if n_starts >= MIN_STARTS:
                n_goals = goals.get(key, 0)
                hist_rate = n_goals / n_starts
                rate = hist_rate * (1 - cur_weight) + cur_rate * cur_weight
                rated.append({
                    "name": p.get("name"), "rate": rate, "goals_2025_26": n_goals, "starts_2025_26": n_starts,
                    "goals_2026_27": cur_goals, "starts_2026_27": cur_starts, "projected": False,
                })
                continue
            pg = p.get("position_group")
            base_rate = pg_avg_rate.get(pg) if pg in PROJECTED_POSITION_GROUPS else None
            if base_rate and cur_starts >= CURRENT_SEASON_MIN_STARTS:
                # 2025-26'da hiç oynamamış (yeni transfer/yabancı) ama 2026-27'de gerçek
                # golcü formu birikmeye başlamış — pozisyon ortalamasıyla (taban, gürültüyü
                # bastırır) harmanlanır; hâlâ "projected" değil çünkü artık GERÇEK maç verisi
                # ağırlıklı belirleyici (cur_weight >= CURRENT_SEASON_MIN_STARTS/8). `base_rate`
                # zorunlu ön koşul (2026-09-08 düzeltmesi) — aksi halde savunma oyuncusu gibi
                # PROJECTED_POSITION_GROUPS dışı biri için taban orana hiç sahip olmadan ham,
                # dampinglenmeMİŞ güncel-sezon oranına düşülüyordu (küçük örneklem gürültüsü).
                rate = base_rate * (1 - cur_weight) + cur_rate * cur_weight
                rated.append({
                    "name": p.get("name"), "rate": rate, "goals_2025_26": 0, "starts_2025_26": n_starts,
                    "goals_2026_27": cur_goals, "starts_2026_27": cur_starts, "projected": False,
                })
                continue
            if not base_rate or key not in appeared_this_season:
                continue
            mv = p.get("market_value_eur")
            avg_mv = pg_avg_value.get(pg)
            if mv and avg_mv:
                lo, hi = PROJECTED_VALUE_MULT_RANGE
                mult = max(lo, min(hi, mv / avg_mv))
            else:
                mult = PROJECTED_UNVALUED_MULT
            rated.append({
                "name": p.get("name"), "rate": base_rate * mult, "goals_2025_26": 0, "starts_2025_26": n_starts,
                "goals_2026_27": cur_goals, "starts_2026_27": cur_starts, "projected": True,
            })
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
                "goals_2026_27": p.get("goals_2026_27", 0),
                "starts_2026_27": p.get("starts_2026_27", 0),
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
            live = live_lineups.get(str(m["match_id"]))
            home_allowed = live["home"] if live else None
            away_allowed = live["away"] if live else None
            home_c = _side_candidates(m.get("home_team"), lam_h, home_allowed)
            away_c = _side_candidates(m.get("away_team"), lam_a, away_allowed)
            if not home_c and not away_c:
                continue
            out_matches[str(m["match_id"])] = {
                "home_scorers": home_c,
                "away_scorers": away_c,
                "home_roster_rated": bool(home_c),
                "away_roster_rated": bool(away_c),
                "lineup_confirmed": bool(live),
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
