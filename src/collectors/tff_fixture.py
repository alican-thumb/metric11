from __future__ import annotations

from dataclasses import dataclass, asdict
from urllib.parse import parse_qs, urlparse

from bs4 import BeautifulSoup

from src.http_client import get_url
from src.storage import save_raw


@dataclass
class FixtureMatch:
    week: int
    match_id: str
    date_time: str | None
    home_team: str
    away_team: str
    score: str | None


def fetch_week_matches(seed_match_id: str, week: int, page_id: int = 198) -> list[FixtureMatch]:
    url = f"https://www.tff.org/Default.aspx?macId={seed_match_id}&pageId={page_id}&hafta={week}"
    result = get_url(url, timeout=20)
    if not result.ok:
        raise RuntimeError(f"TFF fixture week fetch failed: week={week}, status={result.status_code}, error={result.error}")

    save_raw("tff_fixture", f"week_{week}", result.text, "html")
    return parse_week_matches(result.text, week)


def parse_week_matches(html: str, week: int) -> list[FixtureMatch]:
    soup = BeautifulSoup(html, "html.parser")
    matches: list[FixtureMatch] = []
    seen: set[str] = set()

    for tr in soup.select("tr.haftaninMaclariTr"):
        home = tr.select_one(".haftaninMaclariEv")
        away = tr.select_one(".haftaninMaclariDeplasman")
        score = tr.select_one(".haftaninMaclariSkor a[href]")
        date = tr.select_one(".haftaninMaclariTarih")
        if not (home and away and score):
            continue

        match_id = _match_id_from_href(score.get("href"))
        if not match_id or match_id in seen:
            continue

        seen.add(match_id)
        matches.append(
            FixtureMatch(
                week=week,
                match_id=match_id,
                date_time=date.get_text(" ", strip=True) if date else None,
                home_team=home.get_text(" ", strip=True),
                away_team=away.get_text(" ", strip=True),
                score=score.get_text(" ", strip=True),
            )
        )
    return matches


def _match_id_from_href(href: str | None) -> str | None:
    if not href:
        return None
    query = parse_qs(urlparse(href).query)
    return (query.get("macId") or query.get("macID") or [None])[0]


def fixture_to_dict(match: FixtureMatch) -> dict:
    return asdict(match)

