from __future__ import annotations

import csv
from dataclasses import dataclass
from io import StringIO

from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning

from src.http_client import get_url
from src.storage import save_raw


CSV_URL = "https://www.football-data.co.uk/mmz4281/2526/E0.csv"


@dataclass
class FootballDataUkProbe:
    ok: bool
    status_code: int | None
    raw_path: str | None
    columns: list[str]
    sample_rows: int
    has_referee: bool
    has_cards: bool
    has_odds: bool
    error: str | None = None


def probe_csv() -> FootballDataUkProbe:
    disable_warnings(InsecureRequestWarning)
    result = get_url(CSV_URL, timeout=8, verify_ssl=False)
    if not result.ok:
        return FootballDataUkProbe(False, result.status_code, None, [], 0, False, False, False, result.error)

    raw_path = save_raw("football_data_co_uk", "epl_2526_sample", result.text, "csv")
    first_line = result.text.splitlines()[0].strip().lower() if result.text.splitlines() else ""
    if first_line.startswith("<html") or "erisime_engellenmis" in result.text or "has been blocked" in result.text:
        return FootballDataUkProbe(
            ok=False,
            status_code=result.status_code,
            raw_path=str(raw_path),
            columns=[],
            sample_rows=0,
            has_referee=False,
            has_cards=False,
            has_odds=False,
            error="CSV yerine erisim engeli/HTML sayfasi dondu.",
        )

    reader = csv.DictReader(StringIO(result.text))
    columns = reader.fieldnames or []
    sample_rows = sum(1 for _, _row in zip(range(25), reader))
    return FootballDataUkProbe(
        ok=True,
        status_code=result.status_code,
        raw_path=str(raw_path),
        columns=columns,
        sample_rows=sample_rows,
        has_referee="Referee" in columns,
        has_cards=any(col in columns for col in ("HY", "AY", "HR", "AR")),
        has_odds=any(col.startswith(("B365", "PS", "Max", "Avg")) for col in columns),
    )
