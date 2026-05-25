from __future__ import annotations

import json
from dataclasses import dataclass

from src.http_client import get_url
from src.config import PROCESSED_DIR
from src.storage import save_raw


BASE_URL = "https://v3.football.api-sports.io"


@dataclass
class ApiFootballProbe:
    ok: bool
    skipped: bool
    endpoint: str
    status_code: int | None
    raw_path: str | None
    response_keys: list[str]
    item_count: int | None
    error: str | None = None


def probe_super_lig(key: str | None) -> list[ApiFootballProbe]:
    if not key:
        return [
            ApiFootballProbe(
                ok=False,
                skipped=True,
                endpoint="leagues?search=Super Lig",
                status_code=None,
                raw_path=None,
                response_keys=[],
                item_count=None,
                error="API_FOOTBALL_KEY bulunamadi; .env icine eklenirse test edilir.",
            )
        ]

    headers = {"x-apisports-key": key}
    probes = []
    for endpoint in ("leagues?search=Super%20Lig", "teams?league=203&season=2025"):
        url = f"{BASE_URL}/{endpoint}"
        result = get_url(url, headers=headers)
        raw_path = save_raw("api_football", endpoint.replace("?", "_").replace("&", "_"), result.json_data or result.text)
        response_keys = list(result.json_data.keys()) if isinstance(result.json_data, dict) else []
        item_count = None
        if isinstance(result.json_data, dict) and isinstance(result.json_data.get("response"), list):
            item_count = len(result.json_data["response"])
        probes.append(
            ApiFootballProbe(
                ok=result.ok,
                skipped=False,
                endpoint=endpoint,
                status_code=result.status_code,
                raw_path=str(raw_path),
                response_keys=response_keys,
                item_count=item_count,
                error=result.error,
            )
        )
    return probes


def collect_super_lig_snapshot(key: str | None, season: int = 2025, league_id: int = 203) -> dict:
    if not key:
        return {
            "source": "API-Football",
            "ok": False,
            "skipped": True,
            "season": season,
            "league_id": league_id,
            "error": "API_FOOTBALL_KEY bulunamadi.",
            "endpoints": [],
        }

    headers = {"x-apisports-key": key}
    endpoints = {
        "league": f"leagues?id={league_id}&season={season}",
        "standings": f"standings?league={league_id}&season={season}",
        "teams": f"teams?league={league_id}&season={season}",
        "fixtures": f"fixtures?league={league_id}&season={season}",
        "topscorers": f"players/topscorers?league={league_id}&season={season}",
        "topassists": f"players/topassists?league={league_id}&season={season}",
        "topcards": f"players/topyellowcards?league={league_id}&season={season}",
    }
    endpoint_reports = []
    payload = {}
    for label, endpoint in endpoints.items():
        result = get_url(f"{BASE_URL}/{endpoint}", headers=headers)
        raw_name = endpoint.replace("/", "_").replace("?", "_").replace("&", "_")
        raw_path = save_raw("api_football_snapshot", raw_name, result.json_data or result.text)
        response = result.json_data.get("response") if isinstance(result.json_data, dict) else None
        count = len(response) if isinstance(response, list) else None
        endpoint_reports.append(
            {
                "label": label,
                "endpoint": endpoint,
                "ok": result.ok,
                "status_code": result.status_code,
                "item_count": count,
                "raw_path": str(raw_path),
                "error": result.error,
            }
        )
        payload[label] = response if response is not None else result.json_data

    summary = {
        "source": "API-Football",
        "ok": any(item["ok"] for item in endpoint_reports),
        "skipped": False,
        "season": season,
        "league_id": league_id,
        "successful_endpoints": sum(1 for item in endpoint_reports if item["ok"]),
        "endpoints": endpoint_reports,
    }
    output = {"summary": summary, "data": payload}
    output_path = PROCESSED_DIR / f"api_football_super_lig_snapshot_{season}.json"
    output_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    (PROCESSED_DIR / f"api_football_super_lig_snapshot_{season}.md").write_text(build_snapshot_markdown(output), encoding="utf-8")
    return output


def build_snapshot_markdown(output: dict) -> str:
    summary = output["summary"]
    lines = [
        "# API-Football Süper Lig Snapshot",
        "",
        f"- Sezon: {summary['season']}",
        f"- League ID: {summary['league_id']}",
        f"- Başarılı endpoint: {summary['successful_endpoints']}",
        "",
        "## Endpointler",
        "",
    ]
    for endpoint in summary["endpoints"]:
        lines.append(
            f"- {endpoint['label']}: ok={endpoint['ok']}, status={endpoint['status_code']}, "
            f"item={endpoint['item_count']}, raw={endpoint['raw_path']}"
        )
        if endpoint.get("error"):
            lines.append(f"  - hata={endpoint['error'][:180]}")
    return "\n".join(lines)
