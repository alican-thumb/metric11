from __future__ import annotations

import argparse
import json
from collections import defaultdict
from html import escape
from pathlib import Path

from src.config import PROCESSED_DIR, ROOT_DIR
from src.html_utils import nav_links_html

CURRENT_CLUBS_PATH = ROOT_DIR / "data" / "manual" / "transfermarkt_super_lig_clubs.json"


def _current_super_lig_teams() -> set[str]:
    """2026-27 Süper Lig'in güncel 18 kulübü (küme düşenler hariç).

    `league_intelligence_2025_2026.json` geçen sezon oynayan HERKESİ içerir — küme düşen
    Antalyaspor/Karagümrük/Kayserispor dahil. Bu liste, "2026-27 transfer penceresi"
    diye sunulan scout blueprint'lerinin artık Süper Lig'de olmayan takımlar için
    üretilmesini engellemek için kullanılır (bkz. kullanıcı raporu: "antalyaspor alt
    ligde hâlâ ne arıyor").
    """
    try:
        clubs = json.loads(CURRENT_CLUBS_PATH.read_text(encoding="utf-8")).get("clubs", [])
    except FileNotFoundError:
        return set()
    return {c["team_name"] for c in clubs if c.get("team_name")}


ROLE_MAP = {
    "skor üretim sorunu": ["ST_SCORER", "LW_CREATOR"],
    "savunma kırılgan": ["GK_STABILITY", "CB_DOMINANT", "DM_SECURITY"],
    "son bölüm gol yeme riski": ["GK_STABILITY", "CM_ENGINE", "DM_SECURITY", "CB_DOMINANT"],
    "kart baskısı": ["DM_SECURITY", "CM_ENGINE"],
    "deplasman zayıf": ["CM_ENGINE", "LW_CREATOR", "FB_TWO_WAY"],
    "hücum verimsizliği": ["ST_SCORER", "LW_CREATOR"],
    "düşük şut baskısı": ["LW_CREATOR", "ST_SCORER"],
    "kadro derinliği sınırlı": ["LW_CREATOR", "FB_TWO_WAY"],
    "yeni lig takımı": ["GK_STABILITY", "CB_DOMINANT", "ST_SCORER", "DM_SECURITY"],
    "belirgin zayıflık yok": ["LOW_RISK_REGULAR", "RESALE_VALUE"],
}

ROLE_LABELS = {
    "ST_SCORER": "Santrfor / skor yükü",
    "LW_CREATOR": "Sol açık / çizgi kırıcı",
    "CM_ENGINE": "8 numara / fizik motoru",
    "DM_SECURITY": "6 numara / savunma emniyeti",
    "FB_TWO_WAY": "Bek / çift yönlü koridor",
    "CB_DOMINANT": "Stoper / hava ve temas",
    "GK_STABILITY": "Kaleci / istikrar",
    "LOW_RISK_REGULAR": "Düşük riskli düzenli oyuncu",
    "RESALE_VALUE": "Genç / resale değeri",
}

ROLE_POSITION_ALLOWLIST = {
    "ST_SCORER": {"Centre-Forward", "Second Striker"},
    "LW_CREATOR": {"Left Winger", "Right Winger", "Attacking Midfield"},
    "CM_ENGINE": {"Central Midfield", "Defensive Midfield", "Attacking Midfield"},
    "DM_SECURITY": {"Defensive Midfield", "Central Midfield"},
    "FB_TWO_WAY": {"Left-Back", "Right-Back", "Left Midfield", "Right Midfield"},
    "CB_DOMINANT": {"Centre-Back"},
    "GK_STABILITY": {"Goalkeeper"},
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Takım zafiyetlerinden rol bazlı scout blueprint üretir.")
    parser.add_argument("--league-intelligence", default=str(PROCESSED_DIR / "league_intelligence_2025_2026.json"))
    parser.add_argument("--position-matrix", default=str(PROCESSED_DIR / "position_scout_matrix_2025_2026.json"))
    parser.add_argument("--fm-scout", default=str(PROCESSED_DIR / "fm_style_scout_program_2025_2026.json"))
    parser.add_argument(
        "--player-profiles",
        action="append",
        default=[
            str(PROCESSED_DIR / "tff_player_profiles_besiktas_2025_2026.json"),
            str(PROCESSED_DIR / "tff_player_profiles_scout_shortlist_2025_2026.json"),
            str(PROCESSED_DIR / "tff_player_profiles_all_priority_2025_2026.json"),
            str(PROCESSED_DIR / "tff_player_profiles_enriched_2025_2026.json"),
        ],
        help="TFF profil dosyası. Birden fazla kez verilebilir; son gelen profil aynı ID için önceki alanları günceller.",
    )
    parser.add_argument("--role-overrides", default=str(PROCESSED_DIR.parent / "manual" / "player_role_overrides.json"))
    parser.add_argument("--output-prefix", default="team_scout_blueprints_2025_2026")
    args = parser.parse_args()

    league = json.loads(Path(args.league_intelligence).read_text(encoding="utf-8"))
    position_matrix = json.loads(Path(args.position_matrix).read_text(encoding="utf-8"))
    fm_scout = json.loads(Path(args.fm_scout).read_text(encoding="utf-8"))
    player_profiles = load_player_profiles([Path(path) for path in args.player_profiles])
    role_overrides = load_role_overrides(Path(args.role_overrides))
    payload = build_payload(league, position_matrix, fm_scout, player_profiles, role_overrides)

    json_path = PROCESSED_DIR / f"{args.output_prefix}.json"
    md_path = PROCESSED_DIR / f"{args.output_prefix}.md"
    html_path = PROCESSED_DIR / f"{args.output_prefix}.html"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(build_markdown(payload), encoding="utf-8")
    html_path.write_text(build_html(payload), encoding="utf-8")
    print(md_path.read_text(encoding="utf-8"))


def load_optional_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def load_player_profiles(paths: list[Path]) -> list[dict]:
    profiles: dict[str, dict] = {}
    for path in paths:
        for profile in load_optional_json(path, []):
            external_id = str(profile.get("external_id") or "")
            if not external_id:
                continue
            current = profiles.get(external_id, {})
            profiles[external_id] = {**current, **{k: v for k, v in profile.items() if v is not None}}
    return list(profiles.values())


def load_role_overrides(path: Path) -> dict[str, dict]:
    data = load_optional_json(path, {})
    return {str(item.get("external_id")): item for item in data.get("players", []) if item.get("external_id")}


def build_payload(
    league: dict,
    position_matrix: dict,
    fm_scout: dict,
    player_profiles: list[dict] | None = None,
    role_overrides: dict[str, dict] | None = None,
) -> dict:
    profile_index = {str(item.get("external_id")): item for item in (player_profiles or []) if item.get("external_id")}
    role_candidates = build_role_candidate_index(position_matrix, fm_scout, league, profile_index, role_overrides or {})
    team_profiles = {item["team"]: item for item in league.get("team_profiles", [])}
    current_teams = _current_super_lig_teams()
    blueprints = []
    for weakness in league.get("team_weaknesses", []):
        team = weakness["team"]
        if current_teams and team not in current_teams:
            continue  # 2025/26'da oynadı ama küme düştü — 2026-27 transfer planlamasının dışında
        profile = team_profiles.get(team, {})
        required_roles = roles_for_weaknesses(weakness.get("weaknesses", []))
        role_plans = []
        for role_key in required_roles[:4]:
            candidates = [
                candidate for candidate in role_candidates.get(role_key, [])
                if candidate.get("team") != team and candidate_matches_role(candidate, role_key)
            ][:5]
            role_plans.append(
                {
                    "role_key": role_key,
                    "role_label": ROLE_LABELS.get(role_key, role_key),
                    "reason": role_reason(role_key, weakness.get("weaknesses", []), profile),
                    "top_candidates": candidates,
                }
            )
        blueprints.append(
            {
                "team": team,
                "overall_power_score": profile.get("overall_power_score"),
                "points_per_match": profile.get("points_per_match"),
                "goals_for_per_match": profile.get("goals_for_per_match"),
                "goals_against_per_match": profile.get("goals_against_per_match"),
                "cards_for_per_match": profile.get("cards_for_per_match"),
                "main_scoring_window": profile.get("main_scoring_window"),
                "main_conceding_window": profile.get("main_conceding_window"),
                "weakness_count": weakness.get("weakness_count", 0),
                "weaknesses": weakness.get("weaknesses", []),
                "scout_need_hint": weakness.get("scout_need_hint"),
                "required_roles": required_roles,
                "role_plans": role_plans,
            }
        )
    # Yükselen takımlar: sezon verisi yok, ihtiyaç tahmini template'den
    promoted_teams = {"ÇORUM FK", "ERZURUMSPOR FK", "AMED SFK"}
    existing_teams = {b["team"] for b in blueprints}
    for promo_team in promoted_teams:
        if promo_team not in existing_teams:
            promo_weakness = "yeni lig takımı"
            required_roles = roles_for_weaknesses([promo_weakness])
            role_plans = []
            for role_key in required_roles[:4]:
                candidates = [
                    c for c in role_candidates.get(role_key, [])
                    if c.get("team") not in promoted_teams and candidate_matches_role(c, role_key)
                ][:5]
                role_plans.append({
                    "role_key": role_key,
                    "role_label": ROLE_LABELS.get(role_key, role_key),
                    "reason": f"Süper Lig'e yeni çıkan takım; {ROLE_LABELS.get(role_key, role_key)} pozisyonunda deneyimli takviye kritik.",
                    "top_candidates": candidates,
                })
            blueprints.append({
                "team": promo_team,
                "overall_power_score": None,
                "points_per_match": None,
                "goals_for_per_match": None,
                "goals_against_per_match": None,
                "cards_for_per_match": None,
                "main_scoring_window": None,
                "main_conceding_window": None,
                "weakness_count": 4,
                "weaknesses": [promo_weakness],
                "scout_need_hint": "Süper Lig deneyimli kaleci, stoper ve santrfor takviyesi — serbest ajan ve kiralık öncelikli.",
                "required_roles": required_roles,
                "role_plans": role_plans,
            })

    blueprints.sort(key=lambda item: (item["weakness_count"], -(item.get("overall_power_score") or 0)), reverse=True)
    return {
        "summary": {
            "teams": len(blueprints),
            "role_candidate_buckets": len(role_candidates),
            "candidate_links": sum(len(plan["top_candidates"]) for blueprint in blueprints for plan in blueprint["role_plans"]),
            "model_note": "Takım zafiyetleri TFF sezon verisinden türetilir; aday eşleşmeleri mevcut FM/pozisyon scout havuzundan gelir ve lisanslı/pozisyon verisi arttıkça keskinleşir.",
        },
        "blueprints": blueprints,
    }


def candidate_matches_role(candidate: dict, role_key: str) -> bool:
    # If candidate already validated by position_scout_matrix for this role, trust it
    if candidate.get("role_key") == role_key:
        return True
    # Exact TM position match
    allowed_positions = ROLE_POSITION_ALLOWLIST.get(role_key)
    if not allowed_positions:
        return True
    verified_position = candidate.get("verified_position")
    if verified_position and verified_position in allowed_positions:
        return True
    # Inferred group fallback (from new position scout matrix)
    inferred_group = candidate.get("inferred_group") or candidate.get("position_group")
    role_group_map = {
        "ST_SCORER": "FWD", "LW_CREATOR": "FWD",
        "CM_ENGINE": "MID", "DM_SECURITY": "MID",
        "FB_TWO_WAY": "DEF", "CB_DOMINANT": "DEF",
        "GK_STABILITY": "GK",
    }
    return bool(inferred_group and inferred_group == role_group_map.get(role_key))


def build_role_candidate_index(
    position_matrix: dict,
    fm_scout: dict,
    league: dict,
    profile_index: dict[str, dict],
    role_overrides: dict[str, dict],
) -> dict[str, list[dict]]:
    index: dict[str, list[dict]] = defaultdict(list)
    for role in position_matrix.get("roles", []):
        role_key = role["role_key"]
        for candidate in role.get("top_candidates", []):
            index[role_key].append(apply_role_override(simplify_candidate(candidate, candidate.get("role_fit_score", 0), role_key), role_key, role_overrides))
    bucket_map = {
        "immediate_scorer": "ST_SCORER",
        "physical_engine": "CM_ENGINE",
        "resale_value": "RESALE_VALUE",
        "contract_opportunity": "LOW_RISK_REGULAR",
        "low_risk_regular": "LOW_RISK_REGULAR",
    }
    for bucket, role_key in bucket_map.items():
        for candidate in fm_scout.get("role_buckets", {}).get(bucket, []):
            index[role_key].append(apply_role_override(simplify_candidate(candidate, candidate.get("overall_fm_fit_score", 0), role_key), role_key, role_overrides))
    for player in league.get("player_profiles", []):
        for role_key, fit_score in league_proxy_roles(player):
            index[role_key].append(
                apply_role_override(
                    simplify_league_player(player, fit_score, role_key, profile_index.get(str(player.get("player_id")))),
                    role_key,
                    role_overrides,
                )
            )
    for role_key, candidates in index.items():
        deduped = {}
        for candidate in candidates:
            key = candidate.get("player_id") or candidate["name"]
            if key not in deduped or candidate["fit_score"] > deduped[key]["fit_score"]:
                deduped[key] = candidate
        index[role_key] = sorted(deduped.values(), key=lambda item: item["fit_score"], reverse=True)
    return dict(index)


def league_proxy_roles(player: dict) -> list[tuple[str, float]]:
    starts = player.get("starts", 0)
    goals = player.get("goals", 0)
    cards = player.get("cards", 0)
    load = player.get("estimated_load_score", 0)
    roles = []
    defensive_dominant = starts >= 20 and goals <= 4 and cards >= 5
    central_security = starts >= 18 and goals <= 6 and cards >= 4 and load >= 48
    attacking_or_box_mid = 3 <= goals <= 10 and cards <= 8
    if defensive_dominant:
        roles.append(("CB_DOMINANT", load + starts * 1.4 + cards * 3.2 - goals * 2.0))
    if central_security:
        roles.append(("DM_SECURITY", load + starts * 1.3 + cards * 2.5 - goals * 1.6))
    if starts >= 22 and load >= 58 and attacking_or_box_mid and not defensive_dominant:
        roles.append(("CM_ENGINE", load + starts * 1.2 + min(18, cards * 1.5)))
    if starts >= 20 and goals <= 5 and 3 <= cards <= 9 and not defensive_dominant:
        roles.append(("FB_TWO_WAY", load + starts * 1.1 + max(0, 8 - goals)))
    # GK proxy: çok maç oynadı, hiç gol atmadı, çok az kart — pozisyon filtresi candidate_matches_role'da uygulanır
    if starts >= 20 and goals == 0 and cards <= 2:
        roles.append(("GK_STABILITY", load + starts * 2.0))
    return [(role_key, round(max(0, score), 2)) for role_key, score in roles if score >= 70]


def simplify_league_player(player: dict, fit_score: float, role_key: str, profile: dict | None = None) -> dict:
    load_score = player.get("estimated_load_score", 0)
    load_min = round(max(7.4, 8.2 + min(2.0, load_score / 100 * 2.2) - 0.55), 1)
    load_max = round(min(12.6, load_min + 1.35), 1)
    profile = profile or {}
    age = profile.get("age")
    contract_months = profile.get("contract_months_left")
    resale_signal = "UNKNOWN"
    if age is not None:
        if age <= 23:
            resale_signal = "HIGH"
        elif age <= 26:
            resale_signal = "MEDIUM"
        else:
            resale_signal = "LOW"
    contract_risk = "UNKNOWN"
    if contract_months is not None:
        if contract_months <= 7:
            contract_risk = "EXPIRING_SOON"
        elif contract_months <= 13:
            contract_risk = "ONE_YEAR_WINDOW"
        else:
            contract_risk = "STABLE"
    confidence = "MEDIUM_DERIVED_ROLE" if profile.get("tm_position") else "LOW_POSITION_UNVERIFIED"
    return {
        "player_id": player.get("player_id"),
        "name": player.get("name"),
        "team": profile.get("club") or player.get("team"),
        "age": age,
        "nationality": profile.get("nationality"),
        "contract_months_left": contract_months,
        "verified_position": profile.get("tm_position"),
        "height_cm": None,
        "preferred_foot": None,
        "position_source": "transfermarkt" if profile.get("tm_position") else None,
        "goals": player.get("goals", 0),
        "starts": player.get("starts", 0),
        "cards": player.get("cards", 0),
        "fit_score": round(fit_score, 2),
        "role_key": role_key,
        "estimated_physical_load_km_min": load_min,
        "estimated_physical_load_km_max": load_max,
        "resale_signal": resale_signal,
        "contract_risk": contract_risk,
        "position_confidence": confidence,
        "market_value_eur": profile.get("tm_market_value_eur"),
        "market_value_text": profile.get("tm_market_value_text"),
        "tm_id": profile.get("tm_id"),
        "commercial_note": f"Pozisyon doğrulaması gerekir; maç yükü/kart/gol sinyali {ROLE_LABELS.get(role_key, role_key)} rolüne işaret ediyor. Yaş/sözleşme profili scout risk skoruna bağlandı.",
    }


def simplify_candidate(candidate: dict, fit_score: float, role_key: str) -> dict:
    return {
        "player_id": candidate.get("player_id"),
        "name": candidate.get("name"),
        "team": candidate.get("team"),
        "age": candidate.get("age"),
        "nationality": candidate.get("nationality"),
        "contract_months_left": candidate.get("contract_months_left"),
        "verified_position": candidate.get("verified_position") or candidate.get("position") or candidate.get("tm_position"),
        "inferred_group": candidate.get("inferred_group"),
        "position_group": candidate.get("position_group"),
        "height_cm": candidate.get("height_cm"),
        "preferred_foot": candidate.get("preferred_foot"),
        "position_source": candidate.get("position_source") or ("transfermarkt" if candidate.get("tm_position") else None),
        "goals": candidate.get("goals", 0),
        "starts": candidate.get("starts", 0),
        "cards": candidate.get("cards", 0),
        "fit_score": round(fit_score, 2),
        "role_key": role_key,
        "estimated_physical_load_km_min": candidate.get("estimated_physical_load_km_min"),
        "estimated_physical_load_km_max": candidate.get("estimated_physical_load_km_max"),
        "resale_signal": candidate.get("resale_signal"),
        "contract_risk": candidate.get("contract_risk"),
        "position_confidence": candidate.get("position_confidence", candidate.get("physical_load_confidence")),
        "market_value_eur": candidate.get("tm_market_value_eur") or candidate.get("market_value_eur"),
        "market_value_text": candidate.get("tm_market_value_text") or candidate.get("market_value_text"),
        "tm_id": candidate.get("tm_id"),
        "tm_profile_url": candidate.get("tm_profile_url"),
        "commercial_note": candidate.get("commercial_note") or candidate.get("recommendation"),
    }


def apply_role_override(candidate: dict, role_key: str, role_overrides: dict[str, dict]) -> dict:
    override = role_overrides.get(str(candidate.get("player_id") or ""))
    if not override or override.get("verified_status") != "VERIFIED":
        return candidate
    compatible_roles = set(override.get("compatible_roles") or [])
    copied = dict(candidate)
    copied["verified_position"] = override.get("position")
    copied["height_cm"] = override.get("height_cm")
    copied["preferred_foot"] = override.get("preferred_foot")
    copied["position_source"] = override.get("source_name")
    copied["position_source_url"] = override.get("source_url")
    copied["position_source_risk"] = override.get("source_risk")
    copied["position_group"] = override.get("position_group")
    if role_key in compatible_roles:
        copied["position_confidence"] = "HIGH_EXTERNAL_PROFILE"
        copied["commercial_note"] = (
            f"Pozisyon/biyometri doğrulandı: {override.get('position')}, "
            f"{override.get('height_cm')} cm, ayak={override.get('preferred_foot')}. "
            f"Kaynak riski: {override.get('source_risk')}."
        )
    else:
        copied["position_confidence"] = "MEDIUM_EXTERNAL_ROLE_MISMATCH"
        copied["fit_score"] = round((copied.get("fit_score") or 0) * 0.72, 2)
        copied["commercial_note"] = (
            f"Dış profil pozisyonu {override.get('position')} olarak doğrulandı; "
            f"{role_key} rolüyle tam eşleşmediği için fit skoru düşürüldü."
        )
    return copied


def roles_for_weaknesses(weaknesses: list[str]) -> list[str]:
    roles = []
    for weakness in weaknesses:
        for role in ROLE_MAP.get(weakness, []):
            if role not in roles:
                roles.append(role)
    return roles or ["LOW_RISK_REGULAR"]


def role_reason(role_key: str, weaknesses: list[str], profile: dict) -> str:
    if role_key == "ST_SCORER":
        return f"Skor üretim problemi için bitirici profil; mevcut gol ortalaması {profile.get('goals_for_per_match')}."
    if role_key == "LW_CREATOR":
        if "kadro derinliği sınırlı" in weaknesses:
            return "Büyük maç rotasyonunu besleyecek ve kanat derinliğini artıracak yaratıcı profil."
        return "Deplasman veya üretim zafiyetinde çizgi kıran/taşıyıcı hücum profili gerekir."
    if role_key == "CM_ENGINE":
        return "Son bölüm gol yeme ve deplasman kırılganlığı için tempo taşıyan merkez oyuncu gerekir."
    if role_key == "DM_SECURITY":
        return "Savunma önü emniyet ve kart baskısını düşürecek denge profili gerekir."
    if role_key == "GK_STABILITY":
        return f"Savunma kırılganlığında kaleci istikrarı önceliği; GA ortalaması {profile.get('goals_against_per_match')} — güvenilir kaleci pozisyonu kritik."
    if role_key == "CB_DOMINANT":
        return f"Savunma kırılganlığı için temas/hava üstünlüğü; mevcut GA {profile.get('goals_against_per_match')}."
    if role_key == "FB_TWO_WAY":
        if "kadro derinliği sınırlı" in weaknesses:
            return "Koridor derinliğini artıracak, büyük maç baskısında rotasyon sağlayacak çift yönlü bek."
        return "Kanat savunması ve geçiş gücünü aynı anda destekleyecek çift yönlü bek profili gerekir."
    if role_key == "RESALE_VALUE":
        return "Belirgin zafiyet yoksa genç değer ve al-sat fırsatı önceliklendirilebilir."
    return "Düşük riskli rotasyon ve kadro derinliği."


def build_markdown(payload: dict) -> str:
    summary = payload["summary"]
    lines = [
        "# Takım Scout Blueprint Raporu",
        "",
        f"- Takım: {summary['teams']}",
        f"- Rol aday havuzu: {summary['role_candidate_buckets']}",
        f"- Takım-rol-aday bağlantısı: {summary['candidate_links']}",
        f"- Not: {summary['model_note']}",
        "",
    ]
    for blueprint in payload["blueprints"]:
        lines.extend(
            [
                f"## {blueprint['team']}",
                "",
                f"- Güç: {blueprint.get('overall_power_score')} | GF: {blueprint.get('goals_for_per_match')} | GA: {blueprint.get('goals_against_per_match')} | kart: {blueprint.get('cards_for_per_match')}",
                f"- Zafiyet: {', '.join(blueprint['weaknesses'])}",
                f"- Scout ipucu: {blueprint['scout_need_hint']}",
            ]
        )
        for plan in blueprint["role_plans"]:
            candidate_names = ", ".join(candidate["name"] for candidate in plan["top_candidates"][:3])
            lines.append(f"- {plan['role_label']}: {plan['reason']} Adaylar: {candidate_names or 'aday havuzu zayıf'}")
        lines.append("")
    return "\n".join(lines)


def _dark_nav() -> str:
    return (
        '<div class="topbar">'
        '<a class="brand" href="/"><b>11</b> metric11</a>'
        f'<nav class="topnav">{nav_links_html("transfer_recommendation_report_2025_2026.html")}</nav>'
        '</div>'
    )


def build_html(payload: dict) -> str:
    cards = "".join(blueprint_card(item) for item in payload["blueprints"])
    summary = payload["summary"]
    return f"""<!doctype html>
<html lang="tr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Takım Scout Blueprint Raporu 2026-2027 | metric11</title>
  <meta name="description" content="Süper Lig takım zafiyetleri ve 2026-27 transfer öncelikleri — metric11.">
  <meta property="og:title" content="Takım Scout Blueprint Raporu — metric11">
  <meta property="og:image" content="https://metric11.com/og_blueprints.png">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:image" content="https://metric11.com/og_blueprints.png">
  <meta name="theme-color" content="#09111f">
  <link rel="icon" href="/favicon.svg" type="image/svg+xml">
  <style>
    :root{{--bg:#09111f;--panel:#0e1929;--panel2:#13223a;--ink:#e2e8f0;--muted:#64748b;--border:#1e3a5f;}}
    *{{box-sizing:border-box;margin:0;padding:0}}
    body{{font-family:Inter,"Segoe UI",Arial,sans-serif;background:var(--bg);color:var(--ink);min-height:100vh}}
    .topbar{{min-height:54px;padding:0 clamp(12px,3vw,32px);display:flex;align-items:center;justify-content:space-between;gap:16px;background:#060e1d;border-bottom:2px solid #1a3023}}
    .brand{{display:flex;align-items:center;gap:9px;color:white;text-decoration:none;font-size:17px;font-weight:800}}
    .brand:visited,.brand:hover{{color:white}}
    .brand b{{width:26px;height:26px;border-radius:5px;display:grid;place-items:center;background:#cde94e;color:#060e1d;font-size:13px;font-weight:900}}
    nav{{display:flex;gap:2px;overflow-x:auto;scrollbar-width:none}}
    nav::-webkit-scrollbar{{display:none}}
    nav a{{white-space:nowrap;color:#64748b;padding:7px 10px;border-radius:6px;text-decoration:none;font-size:12px;font-weight:600;transition:.15s}}
    nav a:visited{{color:#64748b}}
    nav a:hover,nav a.active{{background:#0f2030;color:white}}
    .hero{{background:linear-gradient(160deg,#0a1929,#060e1d);padding:24px clamp(12px,3vw,32px) 20px;border-bottom:1px solid var(--border)}}
    .hero h1{{font-size:clamp(18px,3vw,24px);font-weight:800;margin-bottom:6px}}
    .hero p{{font-size:13px;color:var(--muted)}}
    .stat-bar{{display:flex;gap:10px;padding:14px clamp(12px,3vw,32px);flex-wrap:wrap;border-bottom:1px solid var(--border)}}
    .stat-chip{{background:var(--panel);border:1px solid var(--border);border-radius:8px;padding:9px 14px;text-align:center;min-width:90px}}
    .stat-chip .v{{font-size:18px;font-weight:800}}
    .stat-chip .l{{font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:.5px;margin-top:2px}}
    main{{padding:16px clamp(12px,3vw,32px) 60px}}
    .cards-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(420px,1fr));gap:14px}}
    .team-card{{background:var(--panel);border:1px solid var(--border);border-radius:10px;overflow:hidden}}
    .team-header{{padding:14px 16px;border-bottom:1px solid var(--border)}}
    .team-header h2{{font-size:15px;font-weight:700;margin-bottom:4px}}
    .team-meta{{font-size:12px;color:var(--muted)}}
    .team-hint{{font-size:11px;color:#f59e0b;margin-top:3px}}
    .roles{{display:flex;flex-direction:column;gap:0}}
    .role{{border-top:1px solid rgba(30,58,95,.4);padding:12px 16px}}
    .role h3{{font-size:13px;font-weight:700;margin-bottom:4px;color:#60a5fa}}
    .role p{{font-size:12px;color:var(--muted);margin-bottom:8px;line-height:1.4}}
    table{{width:100%;border-collapse:collapse;font-size:11px}}
    th{{color:var(--muted);font-size:10px;text-transform:uppercase;letter-spacing:.4px;padding:5px 6px;border-bottom:1px solid var(--border)}}
    td{{padding:6px 6px;border-bottom:1px solid rgba(30,58,95,.3);vertical-align:middle}}
    .fit-badge{{font-size:10px;font-weight:700;color:#60a5fa}}
    .mv-chip{{color:#f59e0b;font-weight:700}}
    .contract-high{{color:#f87171}}
    .contract-med{{color:#f59e0b}}
    .empty-msg{{font-size:12px;color:var(--muted);padding:8px 0}}
    @media(max-width:600px){{.cards-grid{{grid-template-columns:1fr}}}}
  </style>
</head>
<body>
{_dark_nav()}
<div class="hero">
  <h1>Takım Scout Blueprint Raporu <span style="color:#cde94e">2026-2027</span></h1>
  <p>Lig verisi bazlı takım zafiyetleri → 2026-27 transfer penceresi için rol öncelikleri ve aday eşleşmesi</p>
</div>
<div class="stat-bar">
  <div class="stat-chip"><div class="v">{summary["teams"]}</div><div class="l">Takım</div></div>
  <div class="stat-chip"><div class="v">{summary["role_candidate_buckets"]}</div><div class="l">Rol Havuzu</div></div>
  <div class="stat-chip"><div class="v">{summary["candidate_links"]}</div><div class="l">Aday Bağlantısı</div></div>
</div>
<main>
  <div class="cards-grid">{cards}</div>
</main>
<footer style="text-align:center;padding:40px 16px 28px;color:var(--muted);font-size:12px;border-top:1px solid var(--border);margin-top:24px">
  metric11 &middot; <a href="mailto:hello@metric11.com" style="color:var(--muted);text-decoration:none">hello@metric11.com</a>
</footer>
<script defer src="/_vercel/insights/script.js"></script>
</body>
</html>
"""


def blueprint_card(item: dict) -> str:
    roles = "".join(role_block(plan) for plan in item["role_plans"])
    pwr = item.get("overall_power_score")
    gf = item.get("goals_for_per_match")
    ga = item.get("goals_against_per_match")
    meta_parts = []
    if pwr is not None:
        meta_parts.append(f"Güç {pwr}")
    if gf is not None:
        meta_parts.append(f"GF {gf}")
    if ga is not None:
        meta_parts.append(f"GA {ga}")
    meta_parts.append(f"Zafiyet: {escape(', '.join(item['weaknesses']))}")
    return (
        f'<div class="team-card">'
        f'<div class="team-header">'
        f'<h2>{escape(item["team"])}</h2>'
        f'<div class="team-meta">{" | ".join(meta_parts)}</div>'
        f'<div class="team-hint">{escape(item.get("scout_need_hint") or "")}</div>'
        f'</div>'
        f'<div class="roles">{roles}</div>'
        f'</div>'
    )


def role_block(plan: dict) -> str:
    rows = "".join(candidate_row(candidate) for candidate in plan["top_candidates"][:4])
    if not rows:
        empty = '<div class="empty-msg">Aday verisi yetersiz — pozisyon havuzu genişledikçe dolacak.</div>'
        return (
            f'<div class="role"><h3>{escape(plan["role_label"])}</h3>'
            f'<p>{escape(plan["reason"])}</p>{empty}</div>'
        )
    return (
        f'<div class="role"><h3>{escape(plan["role_label"])}</h3>'
        f'<p>{escape(plan["reason"])}</p>'
        f'<table><thead><tr><th>Oyuncu</th><th>Takım</th><th>Yaş</th><th>TM Değeri</th><th>Fit</th></tr></thead>'
        f'<tbody>{rows}</tbody></table></div>'
    )


def _mv_str(eur) -> str:
    if not eur:
        return "—"
    if eur >= 1_000_000:
        return f"€{eur/1_000_000:.1f}M"
    if eur >= 1_000:
        return f"€{eur//1000}K"
    return f"€{eur}"


def candidate_row(candidate: dict) -> str:
    mv = _mv_str(candidate.get("market_value_eur") or candidate.get("tm_market_value_eur"))
    fit = candidate.get("fit_score") or 0
    risk = candidate.get("contract_risk") or ""
    risk_class = "contract-high" if risk in {"HIGH", "EXPIRING_SOON"} else ("contract-med" if risk in {"MEDIUM", "ONE_YEAR_WINDOW", "FINAL_YEAR"} else "")
    tm_url = candidate.get("tm_profile_url") or ""
    name = escape(candidate.get("name") or "")
    name_html = (
        f'<a href="{escape(tm_url)}" target="_blank" rel="noopener" '
        f'style="color:var(--ink);text-decoration:none;border-bottom:1px dotted var(--border)">{name}</a>'
        if tm_url else name
    )
    return (
        f'<tr>'
        f'<td style="font-weight:600">{name_html}</td>'
        f'<td style="color:var(--muted);font-size:10px">{escape(candidate.get("team") or "")}</td>'
        f'<td class="{risk_class}">{escape(str(candidate.get("age") or "—"))}</td>'
        f'<td class="mv-chip">{mv}</td>'
        f'<td><span class="fit-badge">{fit:.1f}</span></td>'
        f'</tr>'
    )


if __name__ == "__main__":
    main()
