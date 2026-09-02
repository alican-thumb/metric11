from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path

from src.collect_transfermarkt_squad import TRANSFERMARKT_BASE, build_markdown, fetch, parse_squad, summarize
from src.config import PROCESSED_DIR, RAW_DIR, ROOT_DIR, load_settings
from src.http_client import get_url
from src.normalization import normalize_name

API_FOOTBALL_BASE = "https://v3.football.api-sports.io"
API_FOOTBALL_SUPER_LIG_ID = 203

# API-Football takım adları TM'nin resmi/sponsorlu adlarından farklı (ör. "Besiktas" vs
# "BEŞİKTAŞ A.Ş."). TM tamamen boş döndüğünde (bkz. `stale_reason`) veriyi TAMAMEN
# kaybetmemek için son çare olarak API-Football kadrosuna düşülür — bu yüzden eşleşme
# KESİN bilinen isim varyantlarıyla sınırlı tutulur (bulanık/fuzzy eşleşme YOK): bir kulüp
# burada yoksa o kulüp için API-Football denenmez, mevcut eski önbellek davranışı korunur.
API_FOOTBALL_TM_ALIASES: dict[str, str] = {
    "BESIKTAS": "BEŞİKTAŞ A.Ş.",
    "GALATASARAY": "GALATASARAY A.Ş.",
    "FENERBAHCE": "FENERBAHÇE A.Ş.",
    "TRABZONSPOR": "TRABZONSPOR A.Ş.",
    "ISTANBUL BASAKSEHIR": "RAMS BAŞAKŞEHİR FUTBOL KULÜBÜ",
    "BASAKSEHIR FK": "RAMS BAŞAKŞEHİR FUTBOL KULÜBÜ",
    "ALANYASPOR": "CORENDON ALANYASPOR",
    "SAMSUNSPOR": "SAMSUNSPOR A.Ş.",
    "GOZTEPE": "GÖZTEPE A.Ş.",
    "KONYASPOR": "TÜMOSAN KONYASPOR",
    "CAYKUR RIZESPOR": "ÇAYKUR RİZESPOR A.Ş.",
    "RIZESPOR": "ÇAYKUR RİZESPOR A.Ş.",
    "GAZIANTEP": "GAZİANTEP FUTBOL KULÜBÜ A.Ş.",
    "GAZIANTEP FK": "GAZİANTEP FUTBOL KULÜBÜ A.Ş.",
    "KASIMPASA": "KASIMPAŞA A.Ş.",
    "KOCAELISPOR": "KOCAELİSPOR",
    "EYUPSPOR": "İKAS EYÜPSPOR",
    "GENCLERBIRLIGI": "GENÇLERBİRLİĞİ",
    "CORUM FK": "ÇORUM FK",
    "ERZURUMSPOR": "ERZURUMSPOR FK",
    "ERZURUMSPOR FK": "ERZURUMSPOR FK",
    "BB ERZURUMSPOR": "ERZURUMSPOR FK",
    "AMEDSPOR": "AMED SFK",
    "AMED SPORTIF FAALIYETLER": "AMED SFK",
    "AMED SK": "AMED SFK",
    "AMED": "AMED SFK",
}

API_FOOTBALL_POSITION_GROUPS = {
    "GOALKEEPER": "GK",
    "DEFENDER": "DEF",
    "MIDFIELDER": "MID",
    "ATTACKER": "FWD",
}

MIN_PLAUSIBLE_SQUAD_SIZE = 15  # bariz eksik/bozuk API yanıtını reddetmek için alt sınır


def main() -> None:
    parser = argparse.ArgumentParser(description="Transfermarkt lig kadrolarını kontrollü şekilde toplar.")
    parser.add_argument("--clubs", default=str(ROOT_DIR / "data/manual/transfermarkt_super_lig_clubs.example.json"))
    parser.add_argument("--season-id", default=None)
    parser.add_argument("--output-prefix", default="transfermarkt_super_lig_squads_2025_2026")
    parser.add_argument("--delay-seconds", type=float, default=8.0)
    parser.add_argument("--only-verified", action="store_true", help="Sadece verified=true kulüpleri toplar.")
    parser.add_argument("--cache-only", action="store_true", help="Ağ çağrısı yapmadan mevcut raw HTML cache dosyalarından üretir.")
    args = parser.parse_args()

    club_payload = json.loads(Path(args.clubs).read_text(encoding="utf-8"))
    season_id = args.season_id or club_payload.get("season_id") or "2025"
    collected = []
    skipped = []
    for club in club_payload.get("clubs", []):
        if args.only_verified and not club.get("verified"):
            skipped.append({**club, "reason": "not_verified"})
            continue
        if not club.get("club_slug") or not club.get("club_id"):
            skipped.append({**club, "reason": "missing_slug_or_id"})
            continue
        url = f"{TRANSFERMARKT_BASE}/{club['club_slug']}/kader/verein/{club['club_id']}/saison_id/{season_id}"
        raw_path = RAW_DIR / "transfermarkt" / args.output_prefix / f"{club['club_id']}.html"
        if args.cache_only:
            players = parse_cached_squad(raw_path)
            if players:
                source_mode = "cache_only"
            else:
                skipped.append({**club, "url": url, "reason": "cache_missing_or_empty"})
                continue
        else:
            try:
                html = fetch(url)
                players = parse_squad(html)
                if not players:
                    # Boş sonuç geçici rate-limit olabilir (kalıcı IP engeli de olabilir,
                    # bu durumda ikinci deneme de boş döner) — tek bir bekleyip yeniden dene.
                    time.sleep(max(args.delay_seconds, 5.0))
                    html = fetch(url)
                    players = parse_squad(html)
                if players:
                    raw_path.parent.mkdir(parents=True, exist_ok=True)
                    raw_path.write_text(html, encoding="utf-8")
                    source_mode = "live"
                else:
                    cached_players = parse_cached_squad(raw_path)
                    if cached_players:
                        players = cached_players
                        source_mode = "cache_after_empty_live"
                    else:
                        skipped.append({**club, "url": url, "reason": "empty_squad"})
                        continue
            except Exception as exc:  # noqa: BLE001 - collector must keep partial progress
                players = parse_cached_squad(raw_path)
                if players:
                    source_mode = "cache_after_fetch_failed"
                else:
                    skipped.append({**club, "url": url, "reason": f"fetch_failed: {exc}"})
                    continue
        collected.append(
            {
                "team_name": club.get("team_name"),
                "club_slug": club["club_slug"],
                "club_id": club["club_id"],
                "verified": club.get("verified", False),
                "url": url,
                "source_mode": source_mode,
                "players": players,
                "summary": summarize(players),
            }
        )
        time.sleep(args.delay_seconds)

    now_iso = datetime.now(timezone.utc).isoformat()
    payload = {
        "source": "Transfermarkt",
        "source_type": "SCRAPING",
        "risk_level": "HIGH",
        "license_status": "VERIFY_TERMS_BEFORE_COMMERCIAL_USE",
        "season_id": season_id,
        "clubs_collected": len(collected),
        "clubs_skipped": len(skipped),
        "clubs": collected,
        "skipped": skipped,
        "summary": summarize_league(collected),
        "run_at": now_iso,
        "data_as_of": now_iso,
    }
    if not collected:
        fallback_clubs = api_football_fallback_clubs(club_payload.get("clubs", []))
        previous = load_previous_nonempty(PROCESSED_DIR / f"{args.output_prefix}.json")
        if fallback_clubs:
            # Fallback'in eşleştiremediği kulüpler için TAMAMEN kaybetmek yerine önceki
            # (bayat ama mevcut) önbellek kaydını koru — regresyon yok, yalnız iyileşme.
            fallback_by_name = {c["team_name"] for c in fallback_clubs}
            merged = list(fallback_clubs)
            if previous:
                for prev_club in previous.get("clubs", []):
                    if prev_club.get("team_name") not in fallback_by_name:
                        merged.append(prev_club)
            payload = {
                "source": "Transfermarkt (TM boş döndü, API-Football'a düşüldü)",
                "source_type": "SCRAPING+API_FALLBACK",
                "risk_level": "HIGH",
                "license_status": "VERIFY_TERMS_BEFORE_COMMERCIAL_USE",
                "season_id": season_id,
                "clubs_collected": len(merged),
                "clubs_skipped": len(club_payload.get("clubs", [])) - len(merged),
                "clubs": merged,
                "skipped": skipped,
                "summary": summarize_league(merged),
                "run_at": now_iso,
                "data_as_of": now_iso,
                "stale_reason": "transfermarkt_empty_used_api_football_fallback",
            }
        elif previous:
            previous["stale_reason"] = "collector_produced_no_nonempty_clubs"
            previous["skipped_latest"] = skipped
            previous["run_at"] = now_iso
            previous.setdefault("data_as_of", previous.get("run_at"))
            payload = previous

    json_path = PROCESSED_DIR / f"{args.output_prefix}.json"
    md_path = PROCESSED_DIR / f"{args.output_prefix}.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(build_league_markdown(payload), encoding="utf-8")
    print(md_path.read_text(encoding="utf-8"))


def api_football_fallback_clubs(tm_clubs: list[dict]) -> list[dict]:
    """TM tamamen boş döndüğünde son çare: API-Football'dan kadro çeker.

    Yalnız `API_FOOTBALL_TM_ALIASES`'ta KESİN bilinen bir isim eşleşmesi varsa ve
    dönen kadro `MIN_PLAUSIBLE_SQUAD_SIZE`'ı geçiyorsa kabul edilir — eşleşmeyen veya
    şüpheli (çok küçük) kadrolar sessizce atlanır, hiçbir zaman TM'den daha eski ama
    doğru bilinen bir kadronun yerine yanlış eşleşmiş veri koymaz.
    """
    try:
        key = load_settings().api_football_key
        if not key:
            return []
        headers = {"x-apisports-key": key}
        teams_result = get_url(f"{API_FOOTBALL_BASE}/teams?league={API_FOOTBALL_SUPER_LIG_ID}&season={datetime.now(timezone.utc).year}", headers=headers)
        if not teams_result.ok or not isinstance(teams_result.json_data, dict):
            return []
        api_teams = teams_result.json_data.get("response") or []
        tm_by_name = {c.get("team_name"): c for c in tm_clubs}
        out: list[dict] = []
        for entry in api_teams:
            team = entry.get("team") or {}
            api_id = team.get("id")
            api_name = team.get("name")
            if not api_id or not api_name:
                continue
            tm_name = API_FOOTBALL_TM_ALIASES.get(normalize_name(api_name))
            if not tm_name or tm_name not in tm_by_name:
                continue
            time.sleep(1.5)
            squad_result = get_url(f"{API_FOOTBALL_BASE}/players/squads?team={api_id}", headers=headers)
            if not squad_result.ok or not isinstance(squad_result.json_data, dict):
                continue
            squad_response = squad_result.json_data.get("response") or []
            raw_players = squad_response[0].get("players", []) if squad_response else []
            players = []
            for p in raw_players:
                if not p.get("name"):
                    continue
                players.append({
                    "transfermarkt_id": None,
                    "api_football_id": p.get("id"),
                    "name": p.get("name"),
                    "normalized_name": normalize_name(p.get("name")),
                    "shirt_number": str(p.get("number")) if p.get("number") is not None else "-",
                    "position": p.get("position"),
                    "position_group": API_FOOTBALL_POSITION_GROUPS.get((p.get("position") or "").upper(), "UNKNOWN"),
                    "age": p.get("age"),
                    "contract_until": None,
                    "market_value_text": "-",
                    "market_value_eur": None,
                    "profile_url": None,
                })
            if len(players) < MIN_PLAUSIBLE_SQUAD_SIZE:
                continue
            tm_club = tm_by_name[tm_name]
            out.append({
                "team_name": tm_name,
                "club_slug": tm_club.get("club_slug"),
                "club_id": tm_club.get("club_id"),
                "verified": tm_club.get("verified", False),
                "url": f"{API_FOOTBALL_BASE}/players/squads?team={api_id}",
                "source_mode": "api_football_fallback",
                "players": players,
                "summary": summarize(players),
            })
        return out
    except Exception:  # noqa: BLE001 - fallback en kötü ihtimalle hiçbir şey döndürmemeli
        return []


def parse_cached_squad(path: Path) -> list[dict]:
    if not path.exists():
        return []
    try:
        players = parse_squad(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001 - corrupt cache should not stop collection
        return []
    return players


def load_previous_nonempty(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    if payload.get("summary", {}).get("players", 0) > 0:
        return payload
    return None


def summarize_league(clubs: list[dict]) -> dict:
    players = [player for club in clubs for player in club.get("players", [])]
    values = [player.get("market_value_eur") for player in players if player.get("market_value_eur") is not None]
    return {
        "clubs": len(clubs),
        "players": len(players),
        "market_value_total_eur": sum(values),
        "market_value_avg_eur": round(sum(values) / len(values)) if values else None,
        "position_groups": {
            group: sum(1 for player in players if player.get("position_group") == group)
            for group in ("GK", "DEF", "MID", "FWD", "UNKNOWN")
        },
    }


def build_league_markdown(payload: dict) -> str:
    summary = payload["summary"]
    lines = [
        "# Transfermarkt Süper Lig Kadro Snapshot",
        "",
        f"- Risk: {payload['risk_level']}",
        f"- Lisans durumu: {payload['license_status']}",
        f"- Toplanan kulüp: {payload['clubs_collected']}",
        f"- Atlanan kulüp: {payload['clubs_skipped']}",
        f"- Oyuncu: {summary['players']}",
        f"- Toplam piyasa değeri: €{summary['market_value_total_eur']:,}",
        f"- Ortalama piyasa değeri: €{summary['market_value_avg_eur']:,}" if summary["market_value_avg_eur"] else "- Ortalama piyasa değeri: Yok",
        f"- Pozisyon grupları: {summary['position_groups']}",
        "",
        "## Kulüpler",
        "",
    ]
    for club in payload["clubs"]:
        lines.append(
            f"- {club['team_name']}: oyuncu={club['summary']['players']}, "
            f"değer=€{club['summary']['market_value_total_eur']:,}, verified={club.get('verified')}, "
            f"mode={club.get('source_mode', 'unknown')}, url={club['url']}"
        )
    if payload.get("stale_reason"):
        lines.extend(["", "## Stale Koruma", ""])
        lines.append(f"- Sebep: {payload['stale_reason']}")
    if payload["skipped"]:
        lines.extend(["", "## Atlananlar", ""])
        for item in payload["skipped"]:
            lines.append(f"- {item.get('team_name')}: {item.get('reason')}")
    lines.extend(["", "## Beşiktaş Tekil Rapor Formatı", ""])
    if payload["clubs"]:
        sample = {
            "url": payload["clubs"][0]["url"],
            "risk_level": payload["risk_level"],
            "players": payload["clubs"][0]["players"],
            "summary": payload["clubs"][0]["summary"],
        }
        lines.append(build_markdown(sample))
    return "\n".join(lines)


if __name__ == "__main__":
    main()
