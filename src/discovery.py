from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from src.collectors.api_football import probe_super_lig
from src.collectors.football_data_co_uk import probe_csv
from src.collectors.football_data_org import probe_competitions
from src.collectors.tff import probe_match
from src.config import PROCESSED_DIR, ensure_data_dirs, load_settings


def build_markdown(report: dict) -> str:
    lines = [
        "# Futbol Veri Kesif Raporu",
        "",
        f"Olusturma zamani: `{report['generated_at']}`",
        "",
        "## Ozet",
        "",
    ]

    for item in report["summary"]:
        lines.append(f"- {item}")
    lines.append(f"- Islenmis TFF mac veri seti: `{report['processed_outputs']['tff_matches']}`")

    lines.extend(["", "## TFF Mac Detay Testleri", ""])
    for probe in report["tff"]:
        lines.append(f"- Mac ID `{probe['match_id']}`: ok={probe['ok']}, status={probe['status_code']}")
        if probe.get("home_team") or probe.get("away_team"):
            lines.append(
                f"  - Mac: {probe.get('home_team')} {probe.get('home_score')} - "
                f"{probe.get('away_score')} {probe.get('away_team')}"
            )
        if probe.get("competition"):
            lines.append(f"  - Organizasyon: {probe.get('competition')}")
        if probe.get("raw_path"):
            lines.append(f"  - Ham dosya: `{probe['raw_path']}`")
        if probe.get("parsed_path"):
            lines.append(f"  - Parse JSON: `{probe['parsed_path']}`")
        lines.append(f"  - Hakem satiri sayisi: {len(probe.get('referee_mentions') or [])}")
        lines.append(f"  - Parse edilen hakem linki: {probe.get('referee_count')}")
        lines.append(f"  - Parse edilen ilk 11 oyuncusu: {probe.get('starting_player_count')}")
        lines.append(f"  - Parse edilen yedek oyuncu: {probe.get('bench_player_count')}")
        lines.append(f"  - Parse edilen kart olayi: {probe.get('parsed_card_count')}")
        lines.append(f"  - Parse edilen gol olayi: {probe.get('parsed_goal_count')}")
        lines.append(f"  - Sari kart metin sayimi: {probe.get('yellow_card_count')}")
        lines.append(f"  - Kirmizi kart metin sayimi: {probe.get('red_card_count')}")
        if probe.get("error"):
            lines.append(f"  - Hata: {probe['error']}")

    lines.extend(["", "## API-Football", ""])
    for probe in report["api_football"]:
        lines.append(
            f"- `{probe['endpoint']}`: ok={probe['ok']}, skipped={probe['skipped']}, "
            f"status={probe['status_code']}, item_count={probe['item_count']}"
        )
        if probe.get("raw_path"):
            lines.append(f"  - Ham dosya: `{probe['raw_path']}`")
        if probe.get("error"):
            lines.append(f"  - Not/Hata: {probe['error']}")

    lines.extend(["", "## football-data.org", ""])
    for probe in report["football_data_org"]:
        lines.append(
            f"- `{probe['endpoint']}`: ok={probe['ok']}, skipped={probe['skipped']}, "
            f"status={probe['status_code']}, item_count={probe['item_count']}"
        )
        if probe.get("raw_path"):
            lines.append(f"  - Ham dosya: `{probe['raw_path']}`")
        if probe.get("error"):
            lines.append(f"  - Not/Hata: {probe['error']}")

    fd_uk = report["football_data_co_uk"]
    lines.extend(["", "## football-data.co.uk CSV", ""])
    lines.append(f"- ok={fd_uk['ok']}, status={fd_uk['status_code']}, sample_rows={fd_uk['sample_rows']}")
    lines.append(f"- Referee kolonu: {fd_uk['has_referee']}")
    lines.append(f"- Kart kolonlari: {fd_uk['has_cards']}")
    lines.append(f"- Odds kolonlari: {fd_uk['has_odds']}")
    if fd_uk.get("raw_path"):
        lines.append(f"- Ham dosya: `{fd_uk['raw_path']}`")
    if fd_uk.get("error"):
        lines.append(f"- Hata: {fd_uk['error']}")
    lines.append("")
    lines.append("## Ilk Karar")
    lines.append("")
    lines.append(
        "Bu rapor kaynaklarin gercek cevaplarini saklar. Bir sonraki adim, API anahtarlari "
        "eklendikten sonra Super Lig fixture/lineup/player endpointlerini fixture bazinda test etmektir."
    )
    return "\n".join(lines)


def main() -> None:
    ensure_data_dirs()
    settings = load_settings()

    tff_probes = [probe_match(match_id) for match_id in settings.tff_sample_match_ids]
    parsed_tff_matches = []
    for probe in tff_probes:
        if probe.parsed_path:
            parsed_tff_matches.append(json.loads(Path(probe.parsed_path).read_text(encoding="utf-8")))

    api_football_probes = probe_super_lig(settings.api_football_key)
    football_data_probes = probe_competitions(settings.football_data_key)
    football_data_uk_probe = probe_csv()

    summary = [
        f"TFF test edilen mac sayisi: {len(tff_probes)}, basarili: {sum(1 for item in tff_probes if item.ok)}",
        f"API-Football testleri: {len(api_football_probes)}, atlanan: {sum(1 for item in api_football_probes if item.skipped)}",
        f"football-data.org testleri: {len(football_data_probes)}, atlanan: {sum(1 for item in football_data_probes if item.skipped)}",
        f"football-data.co.uk CSV testi basarili: {football_data_uk_probe.ok}",
    ]

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": summary,
        "tff": [asdict(item) for item in tff_probes],
        "api_football": [asdict(item) for item in api_football_probes],
        "football_data_org": [asdict(item) for item in football_data_probes],
        "football_data_co_uk": asdict(football_data_uk_probe),
        "processed_outputs": {
            "tff_matches": str(PROCESSED_DIR / "tff_matches.json"),
        },
    }

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    (PROCESSED_DIR / "tff_matches.json").write_text(
        json.dumps(parsed_tff_matches, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (PROCESSED_DIR / "discovery_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (PROCESSED_DIR / "discovery_report.md").write_text(build_markdown(report), encoding="utf-8")
    print(build_markdown(report))


if __name__ == "__main__":
    main()
