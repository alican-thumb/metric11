from __future__ import annotations

from dataclasses import dataclass

from src.http_client import get_url
from src.storage import save_raw


BASE_URL = "https://api.football-data.org/v4"


@dataclass
class FootballDataProbe:
    ok: bool
    skipped: bool
    endpoint: str
    status_code: int | None
    raw_path: str | None
    response_keys: list[str]
    item_count: int | None
    error: str | None = None


def probe_competitions(key: str | None) -> list[FootballDataProbe]:
    if not key:
        return [
            FootballDataProbe(
                ok=False,
                skipped=True,
                endpoint="competitions",
                status_code=None,
                raw_path=None,
                response_keys=[],
                item_count=None,
                error="FOOTBALL_DATA_KEY bulunamadi; .env icine eklenirse test edilir.",
            )
        ]

    headers = {"X-Auth-Token": key}
    probes = []
    for endpoint in ("competitions", "matches?dateFrom=2026-05-01&dateTo=2026-05-21"):
        url = f"{BASE_URL}/{endpoint}"
        result = get_url(url, headers=headers)
        raw_path = save_raw("football_data_org", endpoint.replace("?", "_").replace("&", "_"), result.json_data or result.text)
        response_keys = list(result.json_data.keys()) if isinstance(result.json_data, dict) else []
        item_count = None
        if isinstance(result.json_data, dict):
            for key_name in ("competitions", "matches"):
                if isinstance(result.json_data.get(key_name), list):
                    item_count = len(result.json_data[key_name])
                    break
        probes.append(
            FootballDataProbe(
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

