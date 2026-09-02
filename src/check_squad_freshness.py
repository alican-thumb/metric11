"""2026-27 Süper Lig kadro verisinin tazeliğini kontrol eder; CI'da görünür şekilde uyarır.

TM'nin GitHub Actions'ın bulut IP'sini engellemesi durumunda `collect_transfermarkt_league_squads`
sessizce eski önbelleğe düşer (bkz. PROJECT_STATE 2026-08-14/15/09-02) — GH Actions job'u yine de
"başarılı" görünür ve kimse fark etmeden haftalarca bayat kalabilir (tam olarak 2026-08-15 ile
2026-09-02 arasında olan). Bu script CI'da ayrı bir adım olarak çalışır: gerçek "hiçbir taze veri
yok" durumunda job'u kırmızıya çevirir (GitHub'ın varsayılan başarısız-workflow e-postasını
tetikler), API-Football fallback'in devrede olduğu daha hafif durumda ise yalnızca uyarı basar.
"""
from __future__ import annotations

import json
import sys

from src.config import PROCESSED_DIR

SQUAD_PATH = PROCESSED_DIR / "transfermarkt_super_lig_squads_2026_2027.json"

HARD_FAIL_REASON = "collector_produced_no_nonempty_clubs"
SOFT_WARN_REASON = "transfermarkt_empty_used_api_football_fallback"


def main() -> int:
    if not SQUAD_PATH.exists():
        print(f"::warning::{SQUAD_PATH} bulunamadı, tazelik kontrolü atlandı.")
        return 0
    payload = json.loads(SQUAD_PATH.read_text(encoding="utf-8"))
    stale_reason = payload.get("stale_reason")
    clubs_collected = payload.get("clubs_collected", 0)
    if stale_reason == HARD_FAIL_REASON:
        print(
            "::error::2026-27 Süper Lig kadro verisi bayat — Transfermarkt hiç kulüp döndürmedi "
            "ve API-Football fallback'i de devreye giremedi (API_FOOTBALL_KEY yok/başarısız olabilir). "
            f"Gösterilen veri eski önbellek (data_as_of={payload.get('data_as_of')}). "
            "Yerelden `python -m src.collect_transfermarkt_league_squads ...` ile manuel yenileme gerekebilir."
        )
        return 1
    if stale_reason == SOFT_WARN_REASON:
        print(
            "::warning::Transfermarkt boş döndü, API-Football fallback'e düşüldü "
            f"({clubs_collected}/18 kulüp). Veri güncel ama TM scraping'in kendisi bozuk — "
            "kalıcı çözüm (proxy/farklı IP) gerekebilir."
        )
        return 0
    print(f"OK: kadro verisi taze, {clubs_collected}/18 kulüp, data_as_of={payload.get('data_as_of')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
