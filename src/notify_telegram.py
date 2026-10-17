"""Transfer sinyallerini ve maç tahminlerini Telegram kanalına gönderir.

Maç gönderileri (2026-10-17): kickoff'a PRE_MATCH_WINDOW_HOURS kala tahmin + maç sayfası
linki; oynandıktan sonra (POST_MATCH_WINDOW_HOURS içinde) tuttu/tutmadı sonucu.

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
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

from src.config import PROCESSED_DIR, SEASON

TRACKER_JSON = PROCESSED_DIR / f"transfer_tracker_{SEASON}.json"
POSTED_JSON  = PROCESSED_DIR / "telegram_posted.json"

NOTIFY_STATUSES = {"CORROBORATED", "OFFICIAL", "RUMOR"}

FIXTURE_PREDICTIONS_JSON = PROCESSED_DIR / "season_fixture_predictions_2026_2027.json"
PRE_MATCH_WINDOW_HOURS = 30
POST_MATCH_WINDOW_HOURS = 72
_ISTANBUL = timezone(timedelta(hours=3))

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


def _kickoff(m: dict) -> datetime | None:
    try:
        return datetime.strptime(m["date_time"].replace(" - ", " ").strip(), "%d.%m.%Y %H:%M").replace(tzinfo=_ISTANBUL)
    except (KeyError, ValueError, AttributeError):
        return None


def _match_post_text(m: dict, kind: str) -> str:
    from src.build_match_pages import _actual, _pick_text, _pct, display_name, match_page_path

    home, away = display_name(m["home_team"]), display_name(m["away_team"])
    pick = m.get("predicted") or "home"
    url = f"{SITE_URL}/{match_page_path(m['home_team'], m['away_team'])}"
    if kind == "post":
        ok = _actual(m.get("actual_score")) == pick
        head = "✅ *Tahmin tuttu*" if ok else "❌ *Tahmin tutmadı*"
        return "\n".join([
            head,
            f"⚽ *{home} {m.get('actual_score')} {away}*",
            f"🔮 Maç öncesi tahminimiz: {_pick_text(m, pick)}",
            f"[Maç sayfası →]({url})",
        ])
    ko = _kickoff(m)
    when = f"{ko.day}.{ko.month:02d} {ko:%H:%M}" if ko else ""
    probs = {"home": m.get("home_win_probability"), "draw": m.get("draw_probability"), "away": m.get("away_win_probability")}
    rec = (m.get("recommended_scoreline") or {}).get("score")
    lines = [
        f"⚽ *{home} - {away}*" + (f" · {when}" if when else ""),
        f"🔮 Tahmin: *{_pick_text(m, pick)}* ({_pct(probs[pick])})",
        f"📊 1: {_pct(probs['home'])} · X: {_pct(probs['draw'])} · 2: {_pct(probs['away'])}",
    ]
    if rec:
        lines.append(f"🎯 Olası skor: {rec}")
    lines.append(f"[Detaylı maç analizi →]({url})")
    return "\n".join(lines)


def _send_match_posts(token: str, channel: str, posted: dict, now: datetime | None = None) -> int:
    if not FIXTURE_PREDICTIONS_JSON.exists():
        return 0
    now = now or datetime.now(timezone.utc)
    payload = json.loads(FIXTURE_PREDICTIONS_JSON.read_text(encoding="utf-8"))
    sent = 0
    for week in payload.get("weeks", []):
        for m in week.get("matches", []):
            ko = _kickoff(m)
            if ko is None:
                continue
            if m.get("is_played"):
                kind, due = "post", timedelta(0) <= now - ko <= timedelta(hours=POST_MATCH_WINDOW_HOURS)
            else:
                kind, due = "pre", timedelta(0) < ko - now <= timedelta(hours=PRE_MATCH_WINDOW_HOURS)
            key = f"match-{kind}-{m['match_id']}"
            if not due or key in posted:
                continue
            print(f"  Gönderiliyor: [{kind}] {m['home_team']} - {m['away_team']}")
            if _send(token, channel, _match_post_text(m, kind)):
                posted[key] = {"sent_at": datetime.now(timezone.utc).isoformat(), "status": f"MATCH_{kind.upper()}", "player": None, "to_club": None}
                sent += 1
                time.sleep(1.5)
    return sent


def _send_simulation_post(token: str, channel: str, posted: dict) -> int:
    """Her hafta tamamlandığında bir kez şampiyonluk/düşme olasılıkları özeti."""
    path = PROCESSED_DIR / "season_simulation_2026_2027.json"
    if not path.exists():
        return 0
    sim = json.loads(path.read_text(encoding="utf-8"))
    week = sim.get("after_week") or 0
    key = f"sim-week-{week}"
    if week < 1 or key in posted:
        return 0
    teams = sim.get("teams", [])
    title = sorted(teams, key=lambda r: -r["sim"]["champion"])[:5]
    danger = sorted(teams, key=lambda r: -r["sim"]["relegated"])[:4]
    pct = lambda x: "<%1" if 0 < x < 0.005 else f"%{round(x * 100)}"
    lines = [f"🏆 *Şampiyonluk oranları* · {week}. hafta sonrası", ""]
    lines += [f"{i}. {r['name']} {pct(r['sim']['champion'])}" for i, r in enumerate(title, start=1)]
    lines += ["", "⬇️ *Düşme riski*"]
    lines += [f"• {r['name']} {pct(r['sim']['relegated'])}" for r in danger]
    lines += ["", f"[Tüm tablo ve takım takım olasılıklar →]({SITE_URL}/{sim.get('page_path')})"]
    if _send(token, channel, "\n".join(lines)):
        posted[key] = {"sent_at": datetime.now(timezone.utc).isoformat(), "status": "SIMULATION", "player": None, "to_club": None}
        return 1
    return 0


def run() -> None:
    token   = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    channel = os.environ.get("TELEGRAM_CHANNEL_ID", "").strip()

    if not token or not channel:
        print("TELEGRAM_BOT_TOKEN veya TELEGRAM_CHANNEL_ID eksik — atlanıyor.")
        return

    posted = _load_posted()
    match_sent = _send_match_posts(token, channel, posted)
    match_sent += _send_simulation_post(token, channel, posted)
    _save_posted(posted)
    print(f"{match_sent} maç gönderisi.")

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
