from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import parse_qs, urlparse

from bs4 import BeautifulSoup

from src.http_client import get_url
from src.storage import save_raw


TFF_MATCH_URL = "https://www.tff.org/Default.aspx?macId={match_id}&pageID=29"


@dataclass
class TffMatchProbe:
    match_id: str
    ok: bool
    status_code: int | None
    raw_path: str | None
    parsed_path: str | None
    title: str | None
    home_team: str | None
    away_team: str | None
    home_score: int | None
    away_score: int | None
    competition: str | None
    venue: str | None
    match_date: str | None
    referee_mentions: list[str]
    referee_count: int
    starting_player_count: int
    bench_player_count: int
    parsed_card_count: int
    parsed_goal_count: int
    yellow_card_count: int
    red_card_count: int
    substitution_count: int
    text_sample: str
    error: str | None = None


def probe_match(match_id: str) -> TffMatchProbe:
    url = TFF_MATCH_URL.format(match_id=match_id)
    result = get_url(url)
    if not result.ok:
        return TffMatchProbe(
            match_id=match_id,
            ok=False,
            status_code=result.status_code,
            raw_path=None,
            parsed_path=None,
            title=None,
            home_team=None,
            away_team=None,
            home_score=None,
            away_score=None,
            competition=None,
            venue=None,
            match_date=None,
            referee_mentions=[],
            referee_count=0,
            starting_player_count=0,
            bench_player_count=0,
            parsed_card_count=0,
            parsed_goal_count=0,
            yellow_card_count=0,
            red_card_count=0,
            substitution_count=0,
            text_sample="",
            error=result.error,
        )

    raw_path = save_raw("tff", f"match_{match_id}", result.text, "html")
    soup = BeautifulSoup(result.text, "html.parser")
    title = soup.get_text(" ", strip=True)[:180]
    text = soup.get_text("\n", strip=True)

    parsed = parse_match_page(match_id, soup)
    parsed_path = save_raw("tff_parsed", f"match_{match_id}", parsed)

    referee_mentions = []
    for line in text.splitlines():
        normalized = line.strip()
        if "Hakem" in normalized or "hakem" in normalized:
            referee_mentions.append(normalized)

    referee_links = soup.select("a[id*='lnkHakem']")
    starters = soup.select("a[id*='rptKadrolar'][id*='lnkOyuncu']")
    bench = soup.select("a[id*='rptYedekler'][id*='lnkOyuncu']")
    card_images = soup.select("img[id*='rptKartlar'][alt*='Kart']")
    goal_links = soup.select("a[id*='rptGoller'][id*='lblGol']")
    yellow_cards = soup.select("img[id*='rptKartlar'][alt*='Sarı Kart'], img[id*='rptKartlar'][alt*='Sari Kart']")
    red_cards = soup.select("img[id*='rptKartlar'][alt*='Kırmızı Kart'], img[id*='rptKartlar'][alt*='Kirmizi Kart']")

    return TffMatchProbe(
        match_id=match_id,
        ok=True,
        status_code=result.status_code,
        raw_path=str(raw_path),
        parsed_path=str(parsed_path),
        title=title,
        home_team=parsed["home_team"]["name"],
        away_team=parsed["away_team"]["name"],
        home_score=parsed["home_team"]["score"],
        away_score=parsed["away_team"]["score"],
        competition=parsed["competition"],
        venue=parsed["venue"],
        match_date=parsed["match_date"],
        referee_mentions=referee_mentions[:20],
        referee_count=len(referee_links),
        starting_player_count=len(starters),
        bench_player_count=len(bench),
        parsed_card_count=len(card_images),
        parsed_goal_count=len(goal_links),
        yellow_card_count=len(yellow_cards) or len(re.findall(r"Sar[ıi]\s+Kart", result.text, flags=re.IGNORECASE)),
        red_card_count=len(red_cards) or len(re.findall(r"K[ıi]rm[ıi]z[ıi]\s+Kart", result.text, flags=re.IGNORECASE)),
        substitution_count=len(re.findall(r"Oyuncu\s+De[ğg]i[şs]ikli[ğg]i", text, flags=re.IGNORECASE)),
        text_sample=text[:1200],
    )


def parse_match_page(match_id: str, soup: BeautifulSoup) -> dict:
    home_team = _team_info(soup, team_number=1)
    away_team = _team_info(soup, team_number=2)
    return {
        "source": "TFF",
        "external_id": match_id,
        "home_team": home_team,
        "away_team": away_team,
        "competition": _text_by_id_contains(soup, "lblOrganizasyonAdi"),
        "match_code": _text_by_id_contains(soup, "lblKod"),
        "venue": _text_by_id_contains(soup, "lnkStad"),
        "match_date": _text_by_id_contains(soup, "lblTarih"),
        "officials": [_official_from_link(link) for link in soup.select("a[id*='lnkHakem']")],
        "lineups": {
            "home": {
                "starting": _players_by_selector(soup, "grdTakim1_rptKadrolar"),
                "bench": _players_by_selector(soup, "grdTakim1_rptYedekler"),
            },
            "away": {
                "starting": _players_by_selector(soup, "grdTakim2_rptKadrolar"),
                "bench": _players_by_selector(soup, "grdTakim2_rptYedekler"),
            },
        },
        "cards": {
            "home": _cards_by_selector(soup, "grdTakim1_rptKartlar"),
            "away": _cards_by_selector(soup, "grdTakim2_rptKartlar"),
        },
        "goals": {
            "home": _goals_by_selector(soup, "grdTakim1_rptGoller"),
            "away": _goals_by_selector(soup, "grdTakim2_rptGoller"),
        },
    }


def _team_info(soup: BeautifulSoup, team_number: int) -> dict:
    name = _text_by_id_contains(soup, f"lnkTakim{team_number}")
    score_id = "lblTakim1Skor" if team_number == 1 else "Label12"
    score_text = _text_by_id_contains(soup, score_id)
    return {
        "name": name,
        "external_id": _query_param_by_id_contains(soup, f"lnkTakim{team_number}", "kulupId"),
        "score": int(score_text) if score_text and score_text.isdigit() else None,
    }


def _official_from_link(link) -> dict:
    text = link.get_text(" ", strip=True)
    match = re.match(r"^(?P<name>.+?)\((?P<role>.+?)\)$", text)
    return {
        "name": match.group("name").strip() if match else text,
        "role": match.group("role").strip() if match else None,
        "external_id": _query_param(link.get("href"), "hakemId"),
    }


def _players_by_selector(soup: BeautifulSoup, id_fragment: str) -> list[dict]:
    players = []
    for link in soup.select(f"a[id*='{id_fragment}'][id*='lnkOyuncu']"):
        row_text = link.parent.get_text(" ", strip=True) if link.parent else link.get_text(" ", strip=True)
        shirt_match = re.match(r"^(?P<number>\d+)\.", row_text)
        players.append(
            {
                "name": link.get_text(" ", strip=True),
                "external_id": _query_param(link.get("href"), "kisiId"),
                "shirt_number": int(shirt_match.group("number")) if shirt_match else None,
            }
        )
    return players


def _cards_by_selector(soup: BeautifulSoup, id_fragment: str) -> list[dict]:
    cards = []
    for image in soup.select(f"img[id*='{id_fragment}'][alt*='Kart']"):
        parent = image.parent
        link = parent.select_one("a[id*='lblKart']") if parent else None
        minute = parent.select_one("span[id*='_d']") if parent else None
        cards.append(
            {
                "type": image.get("alt"),
                "player_name": link.get_text(" ", strip=True) if link else None,
                "player_external_id": _query_param(link.get("href"), "kisiId") if link else None,
                "minute": minute.get_text(" ", strip=True) if minute else None,
            }
        )
    return cards


def _goals_by_selector(soup: BeautifulSoup, id_fragment: str) -> list[dict]:
    goals = []
    for link in soup.select(f"a[id*='{id_fragment}'][id*='lblGol']"):
        text = link.get_text(" ", strip=True)
        name, minute, goal_type = _parse_goal_text(text)
        goals.append(
            {
                "player_name": name,
                "player_external_id": _query_param(link.get("href"), "kisiId"),
                "minute": minute,
                "type": goal_type,
                "raw": text,
            }
        )
    return goals


def _parse_goal_text(text: str) -> tuple[str, str | None, str | None]:
    match = re.match(r"^(?P<name>.+?),(?P<minute>\d+(?:\+\d+)?)\.dk(?:\s+\((?P<type>[^)]+)\))?$", text)
    if not match:
        return text, None, None
    return match.group("name").strip(), f"{match.group('minute')}.dk", match.group("type")


def _text_by_id_contains(soup: BeautifulSoup, fragment: str) -> str | None:
    node = soup.select_one(f"[id*='{fragment}']")
    if not node:
        return None
    return node.get_text(" ", strip=True)


def _query_param_by_id_contains(soup: BeautifulSoup, fragment: str, param: str) -> str | None:
    node = soup.select_one(f"a[id*='{fragment}']")
    return _query_param(node.get("href"), param) if node else None


def _query_param(href: str | None, param: str) -> str | None:
    if not href:
        return None
    parsed = urlparse(href)
    values = parse_qs(parsed.query).get(param)
    return values[0] if values else None
