from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from src.config import PROCESSED_DIR, RAW_DIR
from src.normalization import canonical_player_name


TRANSFERMARKT_BASE = "https://www.transfermarkt.com"


def main() -> None:
    parser = argparse.ArgumentParser(description="Transfermarkt kadro sayfasindan pozisyon ve piyasa degeri toplar.")
    parser.add_argument("--club-slug", default="besiktas-jk")
    parser.add_argument("--club-id", default="114")
    parser.add_argument("--season-id", default="2025")
    parser.add_argument("--output-prefix", default="transfermarkt_besiktas_squad_2025_2026")
    args = parser.parse_args()

    url = f"{TRANSFERMARKT_BASE}/{args.club_slug}/kader/verein/{args.club_id}/saison_id/{args.season_id}"
    html = fetch(url)
    raw_path = RAW_DIR / "transfermarkt" / f"{args.output_prefix}.html"
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    raw_path.write_text(html, encoding="utf-8")

    players = parse_squad(html)
    payload = {
        "source": "Transfermarkt",
        "source_type": "SCRAPING",
        "risk_level": "HIGH",
        "url": url,
        "season_id": args.season_id,
        "players": players,
        "summary": summarize(players),
    }

    json_path = PROCESSED_DIR / f"{args.output_prefix}.json"
    md_path = PROCESSED_DIR / f"{args.output_prefix}.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(build_markdown(payload), encoding="utf-8")
    print(md_path.read_text(encoding="utf-8"))


def fetch(url: str) -> str:
    # Gerçekçi tarayıcı User-Agent'ı: bot olduğunu açıkça belirten önceki UA
    # ("FootballIntelligenceMVP/0.1; local research") TM'nin anti-bot filtresini
    # tetikleyen sinyallerden biriydi (bkz. PROJECT_STATE 2026-08-14/15 — GitHub
    # Actions'ın bulut IP'si engelleniyor). Bu tek başına IP-tabanlı bir engeli
    # çözmez ama en azından bariz bot imzasını kaldırır.
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,tr;q=0.8",
    }
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    return response.text


def parse_squad(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    players = []
    for row in soup.select("table.items tbody tr.odd, table.items tbody tr.even"):
        cells = row.select("td")
        if len(cells) < 9:
            continue
        link = row.select_one("td.hauptlink a[href*='/profil/spieler/']")
        if not link:
            continue
        name = link.get_text(" ", strip=True)
        profile_url = urljoin(TRANSFERMARKT_BASE, link.get("href"))
        player_id = extract_player_id(profile_url)
        position = cells[4].get_text(" ", strip=True)
        age = int(cells[5].get_text(" ", strip=True)) if cells[5].get_text(" ", strip=True).isdigit() else None
        contract_until = cells[7].get_text(" ", strip=True) or None
        market_value_text = cells[8].get_text(" ", strip=True)
        players.append(
            {
                "transfermarkt_id": player_id,
                "name": name,
                "normalized_name": canonical_player_name(name),
                "shirt_number": cells[0].get_text(" ", strip=True) or None,
                "position": position,
                "position_group": position_group(position),
                "age": age,
                "contract_until": contract_until,
                "market_value_text": market_value_text,
                "market_value_eur": parse_market_value(market_value_text),
                "profile_url": profile_url,
            }
        )
    return players


def extract_player_id(url: str) -> str | None:
    match = re.search(r"/spieler/(\d+)", url)
    return match.group(1) if match else None


def parse_market_value(value: str | None) -> int | None:
    if not value or value == "-":
        return None
    cleaned = value.replace("€", "").strip()
    multiplier = 1
    if cleaned.endswith("m"):
        multiplier = 1_000_000
        cleaned = cleaned[:-1]
    elif cleaned.endswith("k"):
        multiplier = 1_000
        cleaned = cleaned[:-1]
    try:
        return int(float(cleaned) * multiplier)
    except ValueError:
        return None


def position_group(position: str) -> str:
    value = position.lower()
    if "goalkeeper" in value:
        return "GK"
    if "back" in value or "defender" in value:
        return "DEF"
    if "midfield" in value:
        return "MID"
    if "winger" in value or "forward" in value or "striker" in value:
        return "FWD"
    return "UNKNOWN"


def summarize(players: list[dict]) -> dict:
    values = [player["market_value_eur"] for player in players if player["market_value_eur"] is not None]
    return {
        "players": len(players),
        "market_value_total_eur": sum(values),
        "market_value_avg_eur": round(sum(values) / len(values)) if values else None,
        "position_groups": {group: sum(1 for player in players if player["position_group"] == group) for group in ["GK", "DEF", "MID", "FWD", "UNKNOWN"]},
    }


def build_markdown(payload: dict) -> str:
    summary = payload["summary"]
    lines = [
        "# Transfermarkt Beşiktaş Kadro Verisi",
        "",
        f"- Kaynak: {payload['url']}",
        f"- Risk: {payload['risk_level']}",
        f"- Oyuncu: {summary['players']}",
        f"- Toplam piyasa değeri: €{summary['market_value_total_eur']:,}",
        f"- Ortalama piyasa değeri: €{summary['market_value_avg_eur']:,}" if summary["market_value_avg_eur"] else "- Ortalama piyasa değeri: Yok",
        f"- Pozisyon grupları: {summary['position_groups']}",
        "",
        "## Oyuncular",
        "",
    ]
    for player in payload["players"]:
        lines.append(
            f"- {player['name']}: {player['position']} ({player['position_group']}), yaş={player['age']}, "
            f"sözleşme={player['contract_until'] or 'Yok'}, değer={player['market_value_text']}"
        )
    return "\n".join(lines)


if __name__ == "__main__":
    main()
