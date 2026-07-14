"""Avrupa kupası ön eleme/nitelendirme haber nabzını toplanmış haber kaynaklarından çıkarır.

football-data.org ücretsiz planı UEFA nitelendirme turlarını (1./2./3. tur, play-off)
kapsamıyor; bu yüzden `european_fixtures_2026_2027.json` sezon boyunca boş kalabiliyor.
Bu modül gerçek fixture verisi yerine zaten toplanan haber kaynaklarından (RSS, Google
News, resmi kulüp, Telegram) Avrupa kupası/nitelendirme sinyalini çıkarıp gerçek,
kaynaklı bir "nabız" listesi üretir — uydurma fikstür/skor içermez.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from src.config import PROCESSED_DIR, SEASON

OUTPUT_JSON = PROCESSED_DIR / f"european_news_pulse_{SEASON}.json"
OUTPUT_MD = PROCESSED_DIR / f"european_news_pulse_{SEASON}.md"

SOURCE_FILES = [
    f"news_rss_latest_{SEASON}.json",
    f"news_google_latest_{SEASON}.json",
    f"news_official_clubs_latest_{SEASON}.json",
    f"news_telegram_latest_{SEASON}.json",
]

COMPETITION_KEYWORDS = {
    "CL": ["şampiyonlar ligi", "devler ligi", "ucl"],
    "EL": ["avrupa ligi", "uel"],
    "ECL": ["konferans ligi", "uecl"],
}
# Tek başına Avrupa kupasına özgü, başka bağlamda (ör. dövüş sporları) geçmeyen anahtar kelimeler.
GENERIC_KEYWORDS = [
    "uefa", "eleme turu", "ön eleme", "nitelendirme",
]
# "rövanş"/"play-off" futbol dışında da kullanılır (ör. boks/MMA); yalnızca bir Türk
# kulübü adıyla birlikte geçtiğinde Avrupa kupası sinyali sayılır.
AMBIGUOUS_KEYWORDS = ["play-off", "playoff", "rövanş"]

# collect_european_fixtures.py ile aynı kısa ad seti + ek Süper Lig kulüpleri.
TURKISH_CLUBS = [
    "Galatasaray", "Fenerbahçe", "Beşiktaş", "Trabzonspor", "Başakşehir",
    "Samsunspor", "Göztepe", "Kocaelispor", "Gaziantep", "Karagümrük",
    "Alanyaspor", "Kayserispor", "Konyaspor", "Rizespor", "Kasımpaşa",
    "Antalyaspor", "Eyüpspor", "Gençlerbirliği",
]

MAX_ITEMS = 40


def _load_articles(name: str) -> list[dict]:
    path = PROCESSED_DIR / name
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    return payload.get("articles", [])


def _matched_competition(text: str) -> str | None:
    for code, keywords in COMPETITION_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            return code
    return None


def _matched_clubs(text: str) -> list[str]:
    return [club for club in TURKISH_CLUBS if club.lower() in text]


def _is_relevant(title_lower: str, text: str, clubs: list[str]) -> bool:
    # Tek başına yeterli: nitelendirme/eleme turuna özgü, başka bağlamda geçmeyen ifadeler.
    if any(kw in text for kw in GENERIC_KEYWORDS):
        return True
    # "rövanş"/"play-off" başka spor dallarında da geçer; yalnızca bir Türk kulübüyle
    # birlikte anıldığında Avrupa kupası sinyali sayılır.
    if clubs and any(kw in text for kw in AMBIGUOUS_KEYWORDS):
        return True
    # Kupa adı yalnızca başlıkta geçiyorsa haberin konusu kupadır (özet içinde geçen
    # tesadüfi kupa övgüsü — ör. bir transfer haberinin özetinde "Şampiyonlar Ligi'nde
    # forma giyecek" gibi bir cümle — gürültü sayılıp dışlanır).
    if clubs and _matched_competition(title_lower):
        return True
    return False


def collect_pulse() -> dict:
    seen: set[str] = set()
    items: list[dict] = []
    for fname in SOURCE_FILES:
        for article in _load_articles(fname):
            title = (article.get("title") or "").strip()
            if not title:
                continue
            link = article.get("link") or ""
            dedup_key = link or title
            if dedup_key in seen:
                continue
            title_lower = title.lower()
            text = f"{title} {article.get('summary', '')}".lower()
            clubs = _matched_clubs(text)
            if not _is_relevant(title_lower, text, clubs):
                continue
            seen.add(dedup_key)
            items.append(
                {
                    "title": title,
                    "source": article.get("source_name") or "",
                    "link": link,
                    "published_at": article.get("published_at") or "",
                    "competition": _matched_competition(text),
                    "clubs": clubs,
                }
            )
    items.sort(key=lambda a: a.get("published_at") or "", reverse=True)
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "season": SEASON,
        "total_items": len(items),
        "items": items[:MAX_ITEMS],
    }


def build_markdown(payload: dict) -> str:
    lines = [
        "# Avrupa Kupası Ön Eleme Haber Nabzı",
        "",
        f"Üretim zamanı: {payload['generated_at']}",
        f"Toplam ilgili haber: {payload['total_items']}",
        "",
        "Not: football-data.org UEFA nitelendirme fikstürlerini kapsamadığı için bu liste",
        "gerçek fikstür yerine toplanan haber kaynaklarından çıkarılan gerçek, kaynaklı sinyaldir.",
        "",
    ]
    for item in payload["items"]:
        clubs = ", ".join(item["clubs"]) if item["clubs"] else "—"
        comp = item["competition"] or "—"
        lines.append(
            f"- [{item['title']}]({item['link']}) — {item['source']} · {item['published_at']} · "
            f"turnuva={comp} · kulüp={clubs}"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    payload = collect_pulse()
    OUTPUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    OUTPUT_MD.write_text(build_markdown(payload), encoding="utf-8")
    print(f"Avrupa haber nabzı: {payload['total_items']} ilgili haber, üst {MAX_ITEMS} kaydedildi")
    print(f"JSON: {OUTPUT_JSON}")


if __name__ == "__main__":
    main()
