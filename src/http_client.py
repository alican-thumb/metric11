from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Mapping

import requests


USER_AGENT = "football-intel-data-discovery/0.1 (+local research)"


@dataclass
class HttpResult:
    ok: bool
    status_code: int | None
    url: str
    content_type: str | None
    text: str
    json_data: object | None
    error: str | None = None


def get_url(
    url: str,
    headers: Mapping[str, str] | None = None,
    timeout: int = 30,
    verify_ssl: bool = True,
) -> HttpResult:
    request_headers = {"User-Agent": USER_AGENT}
    if headers:
        request_headers.update(headers)

    try:
        response = requests.get(url, headers=request_headers, timeout=timeout, verify=verify_ssl)
    except requests.RequestException as exc:
        return HttpResult(
            ok=False,
            status_code=None,
            url=url,
            content_type=None,
            text="",
            json_data=None,
            error=str(exc),
        )

    content_type = response.headers.get("content-type")
    parsed_json = None
    if "json" in (content_type or "").lower():
        try:
            parsed_json = response.json()
        except json.JSONDecodeError:
            parsed_json = None

    return HttpResult(
        ok=200 <= response.status_code < 300,
        status_code=response.status_code,
        url=str(response.url),
        content_type=content_type,
        text=response.text,
        json_data=parsed_json,
        error=None if 200 <= response.status_code < 300 else response.text[:500],
    )
