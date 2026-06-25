"""Transfer sinyallerini Telegram kanalına gönderir.

CORROBORATED ve RUMOR statüsündeki yeni sinyalleri metric11 Telegram kanalına iletir.
Gönderilen sinyaller data/processed/telegram_posted.json'da takip edilir; tekrar gönderilmez.

Gerekli çevre değişkenleri:
  TELEGRAM_BOT_TOKEN  — BotFather'dan alınan bot token
  TELEGRAM_CHANNEL_ID — @metric11tr gibi kanal kullanıcı adı veya -100xxxxxxxxxx ID
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

from src.config import PROCESSED_DIR, SEASON

TRACKER_JSON = PROCESSED_DIR / f"transfer_tracker_{SEASON}.json"
POSTED_JSON  = PROCESSED_DIR / "telegram_posted.json"

NOTIFY_STATUSES = {"CORROBORATED", "OFFICIAL", "RUMOR"}

STATUS_LABEL = {
    "OFFICIAL":     "✅ RESMİ TRANSFER",
    "CORROBORATED": "✅ DOĞRULANDI",
    "RUMOR":        "🔵 SÖYLENTI",
}

SITE_URL = "https://metric11.com"


def _signal_id(transfer: dict) -> str:
    key = f"{transfer.get('player','')}-{transfer.get('to_club','')}-{transfer.get('published_at','')}"
    return hashlib.sha1(key.encode()).hexdigest()[:12]


def _load_posted() -> dict:
    if POSTED_JSON.exists():
        try:
            return json.loads(POSTED_JSON.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def _save_posted(posted: dict) -> None:
    POSTED_JSON.write_text(json.dumps(posted, ensure_ascii=False, indent=2), encoding="utf-8")


def _format_message(t: dict) -> str:
    label = STATUS_LABEL.get(t.get("status", ""), "📌")
    player   = t.get("player") or "?"
    to_club  = t.get("to_club") or "?"
    from_club = t.get("from_club")
    mv       = t.get("market_value_text") or "—"
    source   = t.get("source") or "?"
    link     = t.get("link") or f"{SITE_URL}/transfer_tracker_{SEASON}.html"
    date_str = (t.get("published_at") or "")[:10]

    lines = [f"*{label}*", f"👤 *{player}*"]
    if from_club:
        lines.append(f"🏟 {from_club} → {to_club}")
    else:
        lines.append(f"🏟 → {to_club}")
    if mv and mv != "—":
        lines.append(f"💰 {mv}")
    lines.append(f"📰 {source}" + (f" · {date_str}" if date_str else ""))
    lines.append(f"[metric11.com →]({link})")
    return "\n".join(lines)


def _send(token: str, channel: str, text: str) -> bool:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    resp = requests.post(url, json={
        "chat_id": channel,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False,
    }, timeout=15)
    if resp.status_code == 200:
        return True
    print(f"  Telegram hata {resp.status_code}: {resp.text[:200]}", file=sys.stderr)
    return False


def run() -> None:
    token   = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    channel = os.environ.get("TELEGRAM_CHANNEL_ID", "").strip()

    if not token or not channel:
        print("TELEGRAM_BOT_TOKEN veya TELEGRAM_CHANNEL_ID eksik — atlanıyor.")
        return

    if not TRACKER_JSON.exists():
        print(f"Tracker dosyası bulunamadı: {TRACKER_JSON}")
        return

    data      = json.loads(TRACKER_JSON.read_text(encoding="utf-8"))
    transfers = data.get("transfers", [])
    posted    = _load_posted()

    new_count = sent = 0

    for t in transfers:
        status = t.get("status", "")
        if status not in NOTIFY_STATUSES:
            continue
        sig_id = _signal_id(t)
        if sig_id in posted:
            continue

        new_count += 1
        msg = _format_message(t)
        player  = t.get("player") or "adsız"
        to_club = t.get("to_club") or "?"
        print(f"  Gönderiliyor: [{status}] {player} → {to_club}")

        if _send(token, channel, msg):
            posted[sig_id] = {
                "sent_at": datetime.now(timezone.utc).isoformat(),
                "status":  status,
                "player":  t.get("player"),
                "to_club": t.get("to_club"),
            }
            sent += 1

    _save_posted(posted)

    if new_count == 0:
        print("Yeni sinyal yok.")
    else:
        print(f"{sent}/{new_count} sinyal gönderildi.")


if __name__ == "__main__":
    run()
