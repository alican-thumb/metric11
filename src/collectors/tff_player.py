from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date

import requests
from bs4 import BeautifulSoup


TFF_PLAYER_URL = "https://www.tff.org/Default.aspx?pageId=30&kisiId={player_id}"

MONTHS = {
    "Ocak": 1,
    "Şubat": 2,
    "Subat": 2,
    "Mart": 3,
    "Nisan": 4,
    "Mayıs": 5,
    "Mayis": 5,
    "Haziran": 6,
    "Temmuz": 7,
    "Ağustos": 8,
    "Agustos": 8,
    "Eylül": 9,
    "Eylul": 9,
    "Ekim": 10,
    "Kasım": 11,
    "Kasim": 11,
    "Aralık": 12,
    "Aralik": 12,
}


@dataclass
class TffPlayerProfileProbe:
    player_id: str
    url: str
    status_code: int
    error: str | None
    profile: dict | None
    raw_html: str | None = None


def probe_player_profile(player_id: str, include_raw: bool = False) -> TffPlayerProfileProbe:
    url = TFF_PLAYER_URL.format(player_id=player_id)
    try:
        response = requests.get(url, timeout=25)
        response.encoding = "windows-1254"
        response.raise_for_status()
        profile = parse_player_profile(player_id, response.text)
        return TffPlayerProfileProbe(
            player_id=player_id,
            url=url,
            status_code=response.status_code,
            error=None,
            profile=profile,
            raw_html=response.text if include_raw else None,
        )
    except Exception as exc:  # noqa: BLE001
        status = getattr(getattr(exc, "response", None), "status_code", 0) or 0
        return TffPlayerProfileProbe(player_id=player_id, url=url, status_code=status, error=str(exc), profile=None)


def parse_player_profile(player_id: str, html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    lines = [line.strip() for line in soup.get_text("\n").splitlines() if line.strip()]
    title = soup.find("title")
    name = None
    if title:
        name = title.get_text(" ", strip=True).split(" - ")[0].strip()

    fields = extract_label_values(lines)
    birth_date = parse_turkish_date(fields.get("Doğum Tarihi"))
    contract_end = parse_turkish_date(fields.get("Sözleşme Bitiş T."))
    today = date.today()
    age = calculate_age(birth_date, today) if birth_date else None
    contract_months_left = months_between(today, contract_end) if contract_end else None

    return {
        "source": "TFF",
        "external_id": player_id,
        "name": name,
        "birth_place": fields.get("Doğum Yeri"),
        "birth_date": birth_date.isoformat() if birth_date else None,
        "age": age,
        "nationality": fields.get("Uyruk"),
        "agent": empty_to_none(fields.get("Futbolcu Menajeri")),
        "license_no": fields.get("Lisans No"),
        "club": fields.get("Kulüp"),
        "contract_start": iso_or_none(fields.get("Sözleşme Başlangıç T.")),
        "contract_end": contract_end.isoformat() if contract_end else None,
        "contract_months_left": contract_months_left,
        "raw_fields": fields,
    }


def extract_label_values(lines: list[str]) -> dict:
    labels = {
        "Doğum Yeri",
        "Doğum Tarihi",
        "Uyruk",
        "Futbolcu Menajeri",
        "Lisans No",
        "Kulüp",
        "Sözleşme Başlangıç T.",
        "Sözleşme Bitiş T.",
        "Yurt Dışına Çıkış T.",
    }
    stop_values = {
        "Kişisel Bilgiler",
        "Lisans Bilgileri",
        "Oyuncu Hareketleri",
        "Maçlar",
        "Milli Maçlar",
        "Attığı Goller",
        "Kartlar",
    }
    fields = {}
    for index, line in enumerate(lines):
        if line not in labels:
            continue
        value = None
        for candidate in lines[index + 1 : index + 5]:
            if candidate == ":":
                continue
            if candidate in labels or candidate in stop_values:
                break
            value = candidate
            break
        fields[line] = value
    return fields


def parse_turkish_date(value: str | None) -> date | None:
    if not value:
        return None
    match = re.match(r"(\d{1,2})\s+([A-Za-zÇĞİÖŞÜçğıöşü]+)\s+(\d{4})", value.strip())
    if not match:
        return None
    day = int(match.group(1))
    month = MONTHS.get(match.group(2))
    year = int(match.group(3))
    if not month:
        return None
    return date(year, month, day)


def iso_or_none(value: str | None) -> str | None:
    parsed = parse_turkish_date(value)
    return parsed.isoformat() if parsed else None


def calculate_age(birth_date: date, today: date) -> int:
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))


def months_between(start: date, end: date) -> int:
    return (end.year - start.year) * 12 + end.month - start.month - (1 if end.day < start.day else 0)


def empty_to_none(value: str | None) -> str | None:
    if value is None or value.strip() == "":
        return None
    return value
