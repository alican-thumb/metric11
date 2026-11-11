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
    },
    {
        "key": "prediction_game",
        "domain": "tahmin.metric11.com",
        "project_id": "prj_y8N95iyHMm3nTxNOH66Onx3KU9DQ",
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


def collect(team_id: str, token: str | None = None, use_cli: bool = False) -> dict:
    rows = []
    for project in PROJECTS:
        url = _query_url(team_id, project["project_id"])
        try:
            response = fetch_with_cli(url) if use_cli else fetch_with_token(url, token or "")
            rows.append(normalize_project(project, response))
        except (OSError, RuntimeError, ValueError, json.JSONDecodeError, urllib.error.URLError) as exc:
            rows.append({**project, "status": "error", "error": str(exc)[:300]})
    connected = [row for row in rows if row["status"] == "connected"]
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "connected" if len(connected) == len(rows) else "partial" if connected else "unavailable",
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
    payload = collect(os.getenv("VERCEL_ORG_ID", DEFAULT_TEAM_ID), token=token, use_cli=args.use_vercel_cli)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Vercel Analytics: {payload['status']} -> {output}")


if __name__ == "__main__":
    main()
