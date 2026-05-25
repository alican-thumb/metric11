from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from src.collectors.api_football import BASE_URL
from src.config import PROCESSED_DIR, load_settings
from src.http_client import get_url
from src.storage import save_raw


def main() -> None:
    parser = argparse.ArgumentParser(description="API-Football için oyuncu, takım kadrosu ve sakatlık derin snapshot toplar.")
    parser.add_argument("--season", type=int, default=2024)
    parser.add_argument("--league-id", type=int, default=203)
    parser.add_argument("--max-player-pages", type=int, default=40)
    parser.add_argument("--delay-seconds", type=float, default=7.0)
    parser.add_argument("--retry-seconds", type=float, default=12.0)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--output-prefix", default=None)
    args = parser.parse_args()

    settings = load_settings()
    payload = collect_deep_snapshot(
        key=settings.api_football_key,
        season=args.season,
        league_id=args.league_id,
        max_player_pages=args.max_player_pages,
        delay_seconds=args.delay_seconds,
        retry_seconds=args.retry_seconds,
        retries=args.retries,
    )
    prefix = args.output_prefix or f"api_football_super_lig_deep_snapshot_{args.season}"
    json_path = PROCESSED_DIR / f"{prefix}.json"
    md_path = PROCESSED_DIR / f"{prefix}.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(build_markdown(payload), encoding="utf-8")
    print(md_path.read_text(encoding="utf-8"))


def collect_deep_snapshot(
    key: str | None,
    season: int,
    league_id: int,
    max_player_pages: int,
    delay_seconds: float,
    retry_seconds: float,
    retries: int,
) -> dict:
    if not key:
        return {
            "summary": {
                "source": "API-Football",
                "ok": False,
                "season": season,
                "league_id": league_id,
                "error": "API_FOOTBALL_KEY bulunamadi.",
            },
            "endpoint_reports": [],
            "data": {},
        }

    headers = {"x-apisports-key": key}
    endpoint_reports: list[dict] = []

    request_options = {"delay_seconds": delay_seconds, "retry_seconds": retry_seconds, "retries": retries}
    teams_result = request_endpoint(headers, f"teams?league={league_id}&season={season}", "teams", endpoint_reports, **request_options)
    teams = teams_result if isinstance(teams_result, list) else []
    squads = collect_squads(headers, teams, endpoint_reports, **request_options)
    injuries = request_endpoint(headers, f"injuries?league={league_id}&season={season}", "injuries", endpoint_reports, **request_options)
    players = collect_player_pages(headers, league_id, season, max_player_pages, endpoint_reports, **request_options)

    data = {
        "teams": teams,
        "squads": squads,
        "injuries": injuries if isinstance(injuries, list) else [],
        "players": players,
    }
    summary = {
        "source": "API-Football",
        "ok": any(item["ok"] for item in endpoint_reports),
        "season": season,
        "league_id": league_id,
        "successful_endpoints": sum(1 for item in endpoint_reports if item["ok"]),
        "team_count": len(teams),
        "squad_count": len(squads),
        "squad_player_count": sum(len(item.get("players", [])) for item in squads),
        "injury_count": len(data["injuries"]),
        "player_stat_rows": len(players),
        "max_player_pages": max_player_pages,
        "delay_seconds": delay_seconds,
        "retry_seconds": retry_seconds,
        "retries": retries,
    }
    return {"summary": summary, "endpoint_reports": endpoint_reports, "data": data}


def collect_squads(
    headers: dict,
    teams: list[dict],
    endpoint_reports: list[dict],
    delay_seconds: float,
    retry_seconds: float,
    retries: int,
) -> list[dict]:
    squads = []
    for team in teams:
        team_id = team.get("team", {}).get("id")
        if not team_id:
            continue
        response = request_endpoint(
            headers,
            f"players/squads?team={team_id}",
            f"squad_{team_id}",
            endpoint_reports,
            delay_seconds=delay_seconds,
            retry_seconds=retry_seconds,
            retries=retries,
        )
        if isinstance(response, list):
            squads.extend(response)
    return squads


def collect_player_pages(
    headers: dict,
    league_id: int,
    season: int,
    max_pages: int,
    endpoint_reports: list[dict],
    delay_seconds: float,
    retry_seconds: float,
    retries: int,
) -> list[dict]:
    players = []
    page = 1
    while page <= max_pages:
        endpoint = f"players?league={league_id}&season={season}&page={page}"
        response = request_endpoint(
            headers,
            endpoint,
            f"players_page_{page}",
            endpoint_reports,
            delay_seconds=delay_seconds,
            retry_seconds=retry_seconds,
            retries=retries,
        )
        if not isinstance(response, list) or not response:
            break
        players.extend(response)
        paging = endpoint_reports[-1].get("paging") or {}
        total_pages = paging.get("total")
        if total_pages and page >= int(total_pages):
            break
        page += 1
    return players


def request_endpoint(
    headers: dict,
    endpoint: str,
    label: str,
    endpoint_reports: list[dict],
    delay_seconds: float,
    retry_seconds: float,
    retries: int,
) -> object:
    result = None
    attempts = 0
    while attempts <= retries:
        if delay_seconds > 0:
            time.sleep(delay_seconds)
        result = get_url(f"{BASE_URL}/{endpoint}", headers=headers)
        if result.status_code != 429:
            break
        attempts += 1
        if attempts <= retries:
            time.sleep(retry_seconds)
    assert result is not None
    raw_name = endpoint.replace("/", "_").replace("?", "_").replace("&", "_")
    raw_path = save_raw("api_football_deep_snapshot", raw_name, result.json_data or result.text)
    response = result.json_data.get("response") if isinstance(result.json_data, dict) else None
    paging = result.json_data.get("paging") if isinstance(result.json_data, dict) else None
    errors = result.json_data.get("errors") if isinstance(result.json_data, dict) else None
    endpoint_reports.append(
        {
            "label": label,
            "endpoint": endpoint,
            "ok": result.ok,
            "status_code": result.status_code,
            "item_count": len(response) if isinstance(response, list) else None,
            "paging": paging,
            "raw_path": str(raw_path),
            "error": result.error,
            "api_errors": errors,
            "attempts": attempts + 1,
        }
    )
    return response if response is not None else result.json_data


def build_markdown(payload: dict) -> str:
    summary = payload["summary"]
    lines = [
        "# API-Football Derin Süper Lig Snapshot",
        "",
        f"- Sezon: {summary.get('season')}",
        f"- League ID: {summary.get('league_id')}",
        f"- Başarılı endpoint: {summary.get('successful_endpoints', 0)}",
        f"- Takım: {summary.get('team_count', 0)}",
        f"- Kadro kaydı: {summary.get('squad_count', 0)}",
        f"- Kadro oyuncusu: {summary.get('squad_player_count', 0)}",
        f"- Sakatlık kaydı: {summary.get('injury_count', 0)}",
        f"- Oyuncu istatistik satırı: {summary.get('player_stat_rows', 0)}",
        "",
        "## Endpointler",
        "",
    ]
    for item in payload.get("endpoint_reports", []):
        lines.append(
            f"- {item['label']}: ok={item['ok']}, status={item['status_code']}, "
            f"item={item['item_count']}, raw={item['raw_path']}"
        )
        if item.get("api_errors"):
            lines.append(f"  - api_errors={str(item['api_errors'])[:220]}")
        if item.get("error"):
            lines.append(f"  - hata={str(item['error'])[:220]}")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
