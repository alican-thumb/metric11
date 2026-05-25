from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from src.config import PROCESSED_DIR, RAW_DIR


DEFAULT_SOURCES = [
    {
        "name": "beIN SPORTS sakat ve cezalı listesi",
        "url": "https://beinsports.com.tr/fotogaleri/trendyol-super-ligde-sakat-ve-cezali-futbolcu-listesi/16",
        "category": "injury_suspension_news",
        "risk": "MEDIUM",
    },
    {
        "name": "FootballToday Süper Lig injuries and suspensions",
        "url": "https://www.footballtoday.net/turkey/super-lig/injured-and-suspended",
        "category": "injury_suspension_reference",
        "risk": "MEDIUM",
    },
]

KEYWORDS = [
    "beşiktaş",
    "besiktas",
    "sakat",
    "cezalı",
    "kart",
    "eksik",
    "ilk 11",
    "muhtemel",
    "transfer",
    "antrenman",
    "kadrosunda",
    "oynamayacak",
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Güncel haber/sakat-cezalı bağlamı toplar ve özetler.")
    parser.add_argument("--output-prefix", default="news_context_snapshot_2025_2026")
    parser.add_argument("--timeout", type=int, default=25)
    args = parser.parse_args()

    payload = collect_sources(DEFAULT_SOURCES, args.timeout)
    json_path = PROCESSED_DIR / f"{args.output_prefix}.json"
    md_path = PROCESSED_DIR / f"{args.output_prefix}.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(build_markdown(payload), encoding="utf-8")
    print(md_path.read_text(encoding="utf-8"))


def collect_sources(sources: list[dict], timeout: int) -> dict:
    rows = []
    for source in sources:
        row = {**source, "ok": False, "status_code": None, "raw_path": None, "signals": [], "error": None}
        try:
            response = requests.get(
                source["url"],
                headers={
                    "User-Agent": "Mozilla/5.0 (compatible; metric11-data-context/0.1; research)",
                    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.7,en;q=0.6",
                },
                timeout=timeout,
            )
            row["status_code"] = response.status_code
            response.raise_for_status()
            raw_path = save_raw(source, response.text)
            row["raw_path"] = str(raw_path)
            row["ok"] = True
            row["signals"] = extract_signals(response.text, source["url"])
        except Exception as exc:  # noqa: BLE001 - partial source failure should not break snapshot
            row["error"] = str(exc)
        rows.append(row)
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_count": len(rows),
        "ok_count": sum(1 for row in rows if row["ok"]),
        "sources": rows,
        "team_unavailability": parse_team_unavailability(rows),
        "summary": summarize(rows),
    }


def save_raw(source: dict, text: str) -> Path:
    parsed = urlparse(source["url"])
    safe_name = re.sub(r"[^a-zA-Z0-9_-]+", "_", f"{source['name']}_{parsed.netloc}")[:90]
    raw_dir = RAW_DIR / "news_context"
    raw_dir.mkdir(parents=True, exist_ok=True)
    path = raw_dir / f"{safe_name}.html"
    path.write_text(text, encoding="utf-8")
    return path


def extract_signals(html: str, url: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "svg"]):
        tag.decompose()
    candidates = []
    title = soup.find("title")
    if title:
        candidates.append(title.get_text(" ", strip=True))
    for selector in ("h1", "h2", "h3", "article", "p", "li", "figcaption"):
        for node in soup.select(selector):
            text = normalize_space(node.get_text(" ", strip=True))
            if len(text) >= 20:
                candidates.append(text)
    signals = []
    seen = set()
    for text in candidates:
        lower = text.lower()
        matched = [keyword for keyword in KEYWORDS if keyword in lower]
        if not matched:
            continue
        key = text[:180]
        if key in seen:
            continue
        seen.add(key)
        signals.append(
            {
                "text": text[:500],
                "matched_keywords": matched[:6],
                "url": url,
                "confidence": "LOW_CONTEXT" if len(matched) == 1 else "MEDIUM_CONTEXT",
            }
        )
        if len(signals) >= 30:
            break
    return signals


def normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def summarize(rows: list[dict]) -> dict:
    return {
        "signals": sum(len(row.get("signals", [])) for row in rows),
        "injury_suspension_sources_ok": sum(1 for row in rows if row["ok"] and "injury" in row.get("category", "")),
        "errors": [row["name"] for row in rows if row.get("error")],
    }


def parse_team_unavailability(rows: list[dict]) -> list[dict]:
    entries = []
    for row in rows:
        for signal in row.get("signals", []):
            text = signal.get("text", "")
            entries.extend(parse_bein_gallery_text(text, row))
    deduped = []
    seen = set()
    for entry in entries:
        key = (entry["team"], entry["status"], entry["player_name"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(entry)
    return deduped


def parse_bein_gallery_text(text: str, row: dict) -> list[dict]:
    # Example segment: "# 2 Beşiktaş | Sakat: Hyeon-gyu Oh, Kartal Yılmaz | Cezalı: - # 3 ..."
    entries = []
    pattern = re.compile(
        r"#\s*\d+\s+(?P<team>[^#|]+?)\s*\|\s*Sakat:\s*(?P<injured>.*?)\s*\|\s*Cezalı:\s*(?P<suspended>.*?)(?=\s+#\s*\d+\s+|$)",
        flags=re.IGNORECASE,
    )
    for match in pattern.finditer(text):
        team = normalize_space(match.group("team"))
        for status, raw in (("INJURED", match.group("injured")), ("SUSPENDED", match.group("suspended"))):
            for name in split_player_names(raw):
                entries.append(
                    {
                        "team": team,
                        "player_name": name,
                        "status": status,
                        "source": row["name"],
                        "url": row["url"],
                        "confidence": "MEDIUM_CONTEXT",
                    }
                )
    return entries


def split_player_names(value: str) -> list[str]:
    cleaned = normalize_space(value)
    cleaned = re.sub(r"\s+#.*$", "", cleaned).strip()
    if not cleaned or cleaned in {"-", "Yok", "yok"}:
        return []
    names = []
    for part in cleaned.split(","):
        name = normalize_space(part)
        if name and name not in {"-", "Yok", "yok"}:
            names.append(name)
    return names


def build_markdown(payload: dict) -> str:
    lines = [
        "# Haber / Sakat-Cezalı Bağlam Snapshot",
        "",
        f"- Oluşturma: {payload['generated_at']}",
        f"- Kaynak: {payload['source_count']}",
        f"- Başarılı: {payload['ok_count']}",
        f"- Sinyal: {payload['summary']['signals']}",
        f"- Yapılandırılmış eksik oyuncu kaydı: {len(payload.get('team_unavailability', []))}",
        "",
        "## Kaynaklar",
        "",
    ]
    for source in payload["sources"]:
        lines.append(
            f"- {source['name']}: ok={source['ok']}, status={source['status_code']}, "
            f"sinyal={len(source.get('signals', []))}, risk={source['risk']}"
        )
        if source.get("error"):
            lines.append(f"  - Hata: {source['error']}")
        for signal in source.get("signals", [])[:8]:
            lines.append(f"  - {signal['confidence']}: {signal['text']} | anahtar={', '.join(signal['matched_keywords'])}")
    if payload.get("team_unavailability"):
        lines.extend(["", "## Yapılandırılmış Eksik Oyuncu Sinyalleri", ""])
        for item in payload["team_unavailability"][:60]:
            lines.append(
                f"- {item['team']}: {item['status']} | {item['player_name']} | kaynak={item['source']} | güven={item['confidence']}"
            )
    return "\n".join(lines)


if __name__ == "__main__":
    main()
