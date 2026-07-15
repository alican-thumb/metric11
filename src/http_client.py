from __future__ import annotations

import json
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

import certifi
import requests


USER_AGENT = "football-intel-data-discovery/0.1 (+local research)"

# Bazı kaynaklar (ör. www.tff.org) TLS zincirinde ara sertifikayı göndermiyor
# ("unable to get local issuer certificate"). curl/tarayıcılar sistem
# anahtarlığındaki önbelleklenmiş ara sertifikayla bunu tolere ediyor ama
# Python'un certifi tabanlı doğrulaması sunucudan eksiksiz zincir bekliyor.
# Eksik ara sertifikayı (data/manual/extra_ca_certs.pem) certifi paketiyle
# birleştirip tüm istekler için kullanıyoruz — yalnızca ekleme yapar, güvenliği
# azaltmaz.
_EXTRA_CA_PATH = Path(__file__).resolve().parents[1] / "data" / "manual" / "extra_ca_certs.pem"
_CA_BUNDLE_CACHE: str | None = None


def _ca_bundle() -> str:
    global _CA_BUNDLE_CACHE
    if _CA_BUNDLE_CACHE is None:
        if _EXTRA_CA_PATH.exists():
            combined = Path(certifi.where()).read_text(encoding="utf-8") + "\n" + _EXTRA_CA_PATH.read_text(encoding="utf-8")
            tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".pem", delete=False, encoding="utf-8")
            tmp.write(combined)
            tmp.close()
            _CA_BUNDLE_CACHE = tmp.name
        else:
            _CA_BUNDLE_CACHE = certifi.where()
    return _CA_BUNDLE_CACHE


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
        verify_arg = _ca_bundle() if verify_ssl is True else verify_ssl
        response = requests.get(url, headers=request_headers, timeout=timeout, verify=verify_arg)
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
