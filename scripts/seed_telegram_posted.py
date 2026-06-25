"""Mevcut transfer sinyallerini 'zaten gönderildi' olarak işaretle.

İlk kurulumda bir kez çalıştır; aksi halde bot tüm geçmiş sinyalleri gönderir.
"""
import hashlib
import json
from pathlib import Path

TRACKER = Path("data/processed/transfer_tracker_2025_2026.json")
POSTED  = Path("data/processed/telegram_posted.json")

data = json.loads(TRACKER.read_text(encoding="utf-8"))
transfers = data.get("transfers", [])

posted = {}
for t in transfers:
    status = t.get("status", "")
    if status not in {"CORROBORATED", "OFFICIAL", "RUMOR"}:
        continue
    key = f"{t.get('player','')}-{t.get('to_club','')}-{t.get('published_at','')}"
    sig_id = hashlib.sha1(key.encode()).hexdigest()[:12]
    posted[sig_id] = {
        "sent_at": "pre-existing",
        "status":  status,
        "player":  t.get("player"),
        "to_club": t.get("to_club"),
    }

POSTED.write_text(json.dumps(posted, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"{len(posted)} mevcut sinyal 'gönderildi' olarak işaretlendi.")
print("Bundan sonraki yeni sinyaller Telegram'a iletilecek.")
