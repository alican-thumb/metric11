"""Adsız transfer sinyallerinde oyuncu adını regex ile düzeltir."""
from __future__ import annotations
import json
from pathlib import Path
from src.config import PROCESSED_DIR, SEASON
from src.analyze_news_with_claude import _extract_player_from_title_with_club


def main() -> None:
    path = PROCESSED_DIR / f"news_intelligence_{SEASON}.json"
    if not path.exists():
        print(f"Dosya bulunamadı: {path}")
        return

    data = json.loads(path.read_text(encoding="utf-8"))
    transfers = data.get("transfers", data.get("transfer_signals", []))

    fixed = 0
    for t in transfers:
        if t.get("player_name"):
            continue
        title = t.get("title", "")
        club = t.get("to_club") or t.get("from_club")
        if not club or not title:
            continue
        name = _extract_player_from_title_with_club(title, club)
        if name:
            t["player_name"] = name
            t["direction_quality"] = t.get("direction_quality", "PLAYER_UNRESOLVED")
            print(f"  FİX: {name!r} ← {title[:80]!r}")
            fixed += 1

    if fixed:
        key = "transfers" if "transfers" in data else "transfer_signals"
        data[key] = transfers
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n{fixed} kayıt düzeltildi → {path.name}")
    else:
        print("Düzeltilecek kayıt bulunamadı.")


if __name__ == "__main__":
    main()
