from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.config import PROCESSED_DIR
from src.normalization import normalize_matches
from src.preview.engine import build_preview, write_preview
from src.preview.form import parse_tff_datetime
from src.preview.markdown import build_markdown
from src.preview.players import load_availability
from src.preview.transfer import simulate_transfer_candidate

__all__ = [
    "build_preview",
    "write_preview",
    "build_markdown",
    "parse_tff_datetime",
    "simulate_transfer_candidate",
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Secili mac icin veri tabanli mac onu raporu uretir.")
    parser.add_argument("--input", default=str(PROCESSED_DIR / "tff_besiktas_2025_2026_matches.json"))
    parser.add_argument("--team", default="BEŞİKTAŞ A.Ş.")
    parser.add_argument("--match-id", default="283844")
    parser.add_argument("--availability", default=str(PROCESSED_DIR / "player_availability_besiktas_2025_2026.json"))
    parser.add_argument("--output-prefix", default=None)
    args = parser.parse_args()

    matches = normalize_matches(json.loads(Path(args.input).read_text(encoding="utf-8")))
    availability = load_availability(Path(args.availability))
    preview = build_preview(matches, args.team, args.match_id, availability)

    output_prefix = args.output_prefix or f"match_preview_{args.match_id}"
    json_path, md_path = write_preview(preview, output_prefix, PROCESSED_DIR)
    print(md_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
