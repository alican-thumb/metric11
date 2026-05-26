from __future__ import annotations

import argparse
import json
from collections import defaultdict
from html import escape
from pathlib import Path

from src.config import PROCESSED_DIR
from src.html_utils import _build_nav, preview_nav_label


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
    blueprints = []
    for weakness in league.get("team_weaknesses", []):
        team = weakness["team"]
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
    allowed_positions = ROLE_POSITION_ALLOWLIST.get(role_key)
    verified_position = candidate.get("verified_position")
    if not allowed_positions:
        return True
    return bool(verified_position and verified_position in allowed_positions)


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
        "market_value_eur": candidate.get("tm_market_value_eur"),
        "market_value_text": candidate.get("tm_market_value_text"),
        "tm_id": candidate.get("tm_id"),
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


def build_html(payload: dict) -> str:
    cards = "".join(blueprint_card(item) for item in payload["blueprints"])
    nav = _build_nav("Scout")
    return f"""<!doctype html>
<html lang="tr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Takım Scout Blueprint Raporu — metric11</title>
  <meta name="description" content="Süper Lig takım zafiyetleri ve scout ihtiyaç analizi — metric11.">
  <meta property="og:title" content="Takım Scout Blueprint Raporu — metric11">
  <meta property="og:image" content="https://metric11.com/og_blueprints.png">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:image" content="https://metric11.com/og_blueprints.png">
  <meta name="theme-color" content="#091810">
  <link rel="icon" href="favicon.svg" type="image/svg+xml">
  <style>
    :root {{ --bg:#f4f6f8; --panel:#fff; --ink:#15181d; --muted:#667085; --line:#dce2ea; --dark:#091810; --red:#bf1f2f; --green:#137a4b; --blue:#185ea8; --lime:#cde94e; --shadow:0 8px 22px rgba(18,24,32,.08); }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; font-family:Inter,"Segoe UI",Arial,sans-serif; background:var(--bg); color:var(--ink); }}
    .topbar {{ position:sticky; top:0; z-index:5; display:flex; align-items:center; justify-content:space-between; gap:20px; min-height:58px; padding:0 clamp(16px,4vw,42px); background:var(--dark); color:white; border-bottom:2px solid #1a3023; }}
    .brand {{ display:flex; gap:10px; align-items:center; font-weight:800; font-size:18px; color:white; text-decoration:none; flex-shrink:0; letter-spacing:-0.2px; }}
    .brand:visited,.brand:active,.brand:hover {{ color:white; }}
    .brand-mark {{ width:28px; height:28px; display:grid; place-items:center; border-radius:6px; color:var(--dark); background:var(--lime); font-size:14px; font-weight:900; flex-shrink:0; }}
    .season {{ color:#6b7c72; font-size:11px; font-weight:500; margin-left:2px; border-left:1px solid #2a3d30; padding-left:8px; }}
    nav {{ display:flex; gap:2px; flex-wrap:nowrap; overflow-x:auto; justify-content:flex-end; scrollbar-width:none; }}
    nav::-webkit-scrollbar {{ display:none; }}
    nav a {{ color:#8fa89a; text-decoration:none; font-size:13px; font-weight:600; padding:8px 11px; border-radius:6px; white-space:nowrap; transition:background .15s,color .15s; }}
    nav a:visited {{ color:#8fa89a; }}
    nav a:hover {{ background:#162b20; color:white; }}
    nav a.active {{ background:#162b20; color:white; }}
    .page-header {{ padding:28px clamp(16px,4vw,42px) 18px; background:var(--bg); border-bottom:1px solid var(--line); }}
    .page-header h1 {{ margin:0 0 6px; font-size:26px; font-weight:800; }}
    .page-header p {{ margin:0; color:var(--muted); font-size:14px; }}
    .back-link {{ display:inline-flex; align-items:center; gap:6px; color:var(--green); text-decoration:none; font-size:13px; font-weight:600; margin-bottom:10px; }}
    .back-link::before {{ content:"←"; }}
    main {{ max-width:1420px; margin:0 auto; padding:24px; }}
    .metrics {{ display:grid; grid-template-columns:repeat(3,1fr); gap:12px; margin-bottom:18px; }}
    .metric, .team-card {{ background:white; border:1px solid var(--line); border-radius:8px; box-shadow:var(--shadow); }}
    .metric {{ padding:15px; }}
    .metric span {{ display:block; color:var(--muted); font-size:12px; }}
    .metric strong {{ display:block; font-size:26px; margin-top:5px; }}
    .cards {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:16px; }}
    .team-card {{ padding:18px; }}
    .team-card h2 {{ margin:0 0 8px; font-size:19px; }}
    .sub {{ color:var(--muted); font-size:13px; line-height:1.45; margin:0 0 12px; }}
    .roles {{ display:grid; grid-template-columns:1fr; gap:10px; }}
    .role {{ border:1px solid var(--line); border-radius:8px; padding:12px; background:#fbfcfe; }}
    .role h3 {{ margin:0 0 6px; font-size:15px; }}
    .role p {{ margin:0 0 8px; color:#424852; font-size:13px; line-height:1.45; }}
    table {{ width:100%; border-collapse:collapse; font-size:12px; }}
    th,td {{ padding:7px 5px; border-bottom:1px solid var(--line); text-align:left; vertical-align:top; }}
    th {{ color:var(--muted); }}
    .pill {{ display:inline-flex; min-height:22px; align-items:center; border-radius:999px; padding:0 8px; font-size:12px; background:#edf5ff; color:var(--blue); border:1px solid #bbd7f5; }}
    @media (max-width:980px) {{ .cards {{ grid-template-columns:1fr; }} .metrics {{ grid-template-columns:1fr 1fr; }} }}
    @media (max-width:680px) {{ .topbar {{ position:static; flex-direction:column; align-items:stretch; padding:11px 16px 0; gap:0; min-height:unset; }} .brand {{ padding-bottom:8px; }} .season {{ display:none; }} nav {{ justify-content:flex-start; border-top:1px solid #1e3228; padding:7px 0 9px; }} }}
    @media (max-width:620px) {{ main {{ padding:14px; }} .metrics {{ grid-template-columns:1fr; }} .role {{ overflow-x:auto; }} table {{ min-width:560px; }} }}
    .x-share {{ display:inline-flex; align-items:center; gap:8px; background:#000; color:#fff; text-decoration:none; font-size:14px; font-weight:700; padding:10px 18px; border-radius:8px; transition:background .15s; }}
    .x-share:hover {{ background:#1a1a1a; }}
    .share-bar {{ padding:16px 0 8px; border-top:1px solid var(--line); margin-top:24px; }}
  </style>
</head>
<body>
  {nav}
  <div class="page-header">
    <a class="back-link" href="/">Ana sayfaya dön</a>
    <h1>Takım Scout Blueprint Raporu</h1>
    <p>Lig istihbaratındaki takım zafiyetlerini scout rol ihtiyacına çevirir ve mevcut aday havuzundan takım dışı öneriler üretir.</p>
  </div>
  <main>
    <div class="metrics">
      {metric("Takım", payload["summary"]["teams"])}
      {metric("Rol havuzu", payload["summary"]["role_candidate_buckets"])}
      {metric("Aday bağlantısı", payload["summary"]["candidate_links"])}
    </div>
    <div class="cards">{cards}</div>
    <div class="share-bar">
      <a class="x-share" href="https://twitter.com/intent/tweet?text=S%C3%BCper%20Lig%27de%20kimin%20neye%20ihtiyac%C4%B1%20var%3F%20%E2%9A%BD%2018%20tak%C4%B1m%C4%B1n%20transfer%20%C3%B6ncelikleri%20ve%20aday%20analizi%20%E2%80%94%20veri%20odakl%C4%B1%20scout%20raporu%3A&url=https%3A%2F%2Fmetric11.com%2Fteam_scout_blueprints_2025_2026.html" target="_blank" rel="noopener">&#x1D54F; Paylaş</a>
    </div>
  </main>
  <script defer src="/_vercel/insights/script.js"></script>
</body>
</html>
"""


def metric(label: str, value) -> str:
    return f'<div class="metric"><span>{escape(str(label))}</span><strong>{escape(str(value))}</strong></div>'


def blueprint_card(item: dict) -> str:
    roles = "".join(role_block(plan) for plan in item["role_plans"])
    return (
        f'<article class="team-card"><h2>{escape(item["team"])}</h2>'
        f'<p class="sub">Güç {escape(str(item.get("overall_power_score")))} | GF {escape(str(item.get("goals_for_per_match")))} | '
        f'GA {escape(str(item.get("goals_against_per_match")))} | Zafiyet: {escape(", ".join(item["weaknesses"]))}</p>'
        f'<p class="sub">Scout ipucu: {escape(item.get("scout_need_hint") or "")}</p>'
        f'<div class="roles">{roles}</div></article>'
    )


def role_block(plan: dict) -> str:
    rows = "".join(candidate_row(candidate) for candidate in plan["top_candidates"][:4])
    if not rows:
        rows = '<tr><td colspan="5">Aday havuzu zayıf; pozisyon verisi artırılmalı.</td></tr>'
    return (
        f'<section class="role"><h3>{escape(plan["role_label"])}</h3><p>{escape(plan["reason"])}</p>'
        '<table><thead><tr><th>Oyuncu</th><th>Takım</th><th>Yaş</th><th>Söz.</th><th>Poz.</th><th>Fit</th><th>Yük</th></tr></thead>'
        f'<tbody>{rows}</tbody></table></section>'
    )


def candidate_row(candidate: dict) -> str:
    load_min = candidate.get("estimated_physical_load_km_min")
    load_max = candidate.get("estimated_physical_load_km_max")
    load = f"{load_min}-{load_max}" if load_min is not None and load_max is not None else "-"
    contract = candidate.get("contract_months_left")
    contract_text = f"{contract} ay" if contract is not None else "-"
    position = candidate.get("verified_position") or "-"
    return (
        f'<tr><td>{escape(candidate.get("name") or "")}</td><td>{escape(candidate.get("team") or "")}</td>'
        f'<td>{escape(str(candidate.get("age") or ""))}</td><td>{escape(contract_text)}</td>'
        f'<td>{escape(position)}</td>'
        f'<td><span class="pill">{escape(str(candidate.get("fit_score") or ""))}</span></td>'
        f'<td>{escape(load)}</td></tr>'
    )


if __name__ == "__main__":
    main()
