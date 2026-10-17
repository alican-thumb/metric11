"""Yeni/değişen sayfaları IndexNow ile Bing, Yandex ve diğer katılımcı arama motorlarına bildirir.

Deploy SONRASI çalışmalı (motor sayfayı hemen tarayabilir). Sitemap'te lastmod'u son
RECENT_DAYS gün içinde olan URL'leri gönderir: canlı sayfalar + yaklaşan maç sayfaları
(lastmod = bugün) + yeni oynanmış maç sayfaları. Anahtar gizli değildir; IndexNow
protokolü gereği kök dizinde `<KEY>.txt` olarak herkese açık durur.
"""
from __future__ import annotations

import json
import re
import sys
import urllib.request
from datetime import date, timedelta

from src.config import PROCESSED_DIR

KEY = "a47553a15194bb56e611986140fe9b17"
HOST = "metric11.com"
ENDPOINT = "https://api.indexnow.org/indexnow"
RECENT_DAYS = 3
MAX_URLS = 10_000  # IndexNow istek başına üst sınır


def ensure_key_file() -> None:
    (PROCESSED_DIR / f"{KEY}.txt").write_text(KEY, encoding="utf-8")


def recent_urls() -> list[str]:
    sitemap = (PROCESSED_DIR / "sitemap.xml").read_text(encoding="utf-8")
    cutoff = (date.today() - timedelta(days=RECENT_DAYS)).isoformat()
    urls = []
    for loc, lastmod in re.findall(r"<loc>([^<]+)</loc>\s*<lastmod>([^<]+)</lastmod>", sitemap):
        if lastmod >= cutoff:
            urls.append(loc)
    return urls[:MAX_URLS]


def main() -> int:
    ensure_key_file()
    urls = recent_urls()
    if not urls:
        print("IndexNow: gönderilecek URL yok.")
        return 0
    body = json.dumps({
        "host": HOST,
        "key": KEY,
        "keyLocation": f"https://{HOST}/{KEY}.txt",
        "urlList": urls,
    }).encode("utf-8")
    request = urllib.request.Request(ENDPOINT, data=body, headers={"Content-Type": "application/json; charset=utf-8"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            print(f"IndexNow: {len(urls)} URL gönderildi, HTTP {response.status}")
    except urllib.error.HTTPError as exc:
        # 202 = kabul edildi (anahtar doğrulaması bekliyor); 4xx gerçek hata.
        print(f"IndexNow: HTTP {exc.code} — {exc.read()[:300]!r}")
        return 1 if exc.code >= 400 else 0
    except OSError as exc:
        print(f"IndexNow: ağ hatası — {exc}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
