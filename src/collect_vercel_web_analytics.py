"""Vercel Web Analytics toplamlarini resmi API'den toplar."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from src.config import PROCESSED_DIR

API_BASE = "https://api.vercel.com/v1/query/web-analytics/visits/count"
OUTPUT_PATH = PROCESSED_DIR / "vercel_web_analytics_latest.json"
DEFAULT_TEAM_ID = "team_RvcQGsKVmxO8P1l6oAo8Chky"
PROJECTS = (
    {
        "key": "main",
        "domain": "metric11.com",
        "project_id": "prj_tGK6hRB5fb69R3ut2FIKsIhzQO5A",
        "token_env": "VERCEL_TOKEN",
    },
    {
        "key": "prediction_game",
        "domain": "tahmin.metric11.com",
        "project_id": "prj_y8N95iyHMm3nTxNOH66Onx3KU9DQ",
        "token_env": "VERCEL_PREDICTION_TOKEN",
    },
)


def _query_url(team_id: str, project_id: str) -> str:
    query = urllib.parse.urlencode({"teamId": team_id, "projectId": project_id})
    return f"{API_BASE}?{query}"


def fetch_with_token(url: str, token: str) -> dict:
    request = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_with_cli(url: str) -> dict:
    completed = subprocess.run(
        ["vercel", "api", url.removeprefix("https://api.vercel.com")],
        text=True,
        capture_output=True,
        check=False,
        timeout=60,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or "vercel api komutu basarisiz")
    return json.loads(completed.stdout)


def normalize_project(project: dict, response: dict) -> dict:
    data = response.get("data", {})
    query = response.get("query", {})
    return {
        "key": project["key"],
        "domain": project["domain"],
        "status": "connected",
        "measurement": {"since": query.get("since"), "until": query.get("until")},
        "visitors": int(data.get("visitors") or 0),
        "pageviews": int(data.get("pageviews") or 0),
    }


def _public_error(project: dict, exc: Exception) -> dict:
    status_code = getattr(exc, "code", None)
    if status_code == 404:
        message = "Analytics projesi bu token/team kapsamında görünmüyor; proje veya token erişimini kontrol edin."
    elif status_code in (401, 403):
        message = "Analytics tokenı bu projeyi okumaya yetkili değil."
    else:
        message = str(exc)[:300]
    return {
        "key": project["key"],
        "domain": project["domain"],
        "status": "error",
        "error_code": status_code,
        "error": message,
    }


def _previous_project(previous: dict | None, key: str) -> dict | None:
    return next((row for row in (previous or {}).get("projects", []) if row.get("key") == key), None)


def collect(
    team_id: str,
    token: str | None = None,
    use_cli: bool = False,
    *,
    project_tokens: dict[str, str] | None = None,
    previous: dict | None = None,
) -> dict:
    rows = []
    for project in PROJECTS:
        url = _query_url(team_id, project["project_id"])
        try:
            project_token = (project_tokens or {}).get(project["key"]) or token or ""
            response = fetch_with_cli(url) if use_cli else fetch_with_token(url, project_token)
            rows.append(normalize_project(project, response))
        except (OSError, RuntimeError, ValueError, json.JSONDecodeError, urllib.error.URLError) as exc:
            error = _public_error(project, exc)
            stale = _previous_project(previous, project["key"])
            if stale and stale.get("status") in {"connected", "stale"}:
                error.update(
                    {
                        "status": "stale",
                        "measurement": stale.get("measurement"),
                        "visitors": stale.get("visitors", 0),
                        "pageviews": stale.get("pageviews", 0),
                        "last_successful_at": (previous or {}).get("generated_at"),
                    }
                )
            rows.append(error)
    connected = [row for row in rows if row["status"] == "connected"]
    usable = [row for row in rows if row["status"] in {"connected", "stale"}]
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "connected" if len(connected) == len(rows) else "partial" if usable else "unavailable",
        "source": "vercel_web_analytics_api",
        "plan_note": "Kaynak ve kampanya (UTM) kırılımı ücretli Vercel planı gerektirir; bu rapor doğrulanmış toplam ziyaret ve görüntülemeleri kullanır.",
        "projects": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Vercel Web Analytics toplamlarini toplar.")
    parser.add_argument("--output", default=str(OUTPUT_PATH))
    parser.add_argument("--use-vercel-cli", action="store_true", help="Yerel Vercel CLI oturumunu kullan.")
    args = parser.parse_args()
    token = os.getenv("VERCEL_TOKEN")
    if not token and not args.use_vercel_cli:
        raise SystemExit("VERCEL_TOKEN yok. Yerelde --use-vercel-cli kullanabilirsiniz.")
    output = Path(args.output)
    try:
        previous = json.loads(output.read_text(encoding="utf-8")) if output.exists() else None
    except (json.JSONDecodeError, OSError):
        previous = None
    prediction_token = os.getenv("VERCEL_PREDICTION_TOKEN")
    project_tokens = {"prediction_game": prediction_token} if prediction_token else None
    payload = collect(
        os.getenv("VERCEL_ORG_ID", DEFAULT_TEAM_ID),
        token=token,
        use_cli=args.use_vercel_cli,
        project_tokens=project_tokens,
        previous=previous,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Vercel Analytics: {payload['status']} -> {output}")


if __name__ == "__main__":
    main()
