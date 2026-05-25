from __future__ import annotations

import argparse
import json
from difflib import SequenceMatcher
from pathlib import Path

from src.config import PROCESSED_DIR
from src.generate_match_preview import simulate_transfer_candidate
from src.normalization import canonical_player_name


def main() -> None:
    parser = argparse.ArgumentParser(description="Seçilen oyuncu bu maçta olsaydı tahmini skor/olasılık ne olurdu simüle eder.")
    parser.add_argument("--preview", required=True, help="Maç preview JSON dosyası.")
    parser.add_argument("--player", required=True, help="Simüle edilecek oyuncu adı.")
    parser.add_argument("--matrix", default=str(PROCESSED_DIR / "position_scout_matrix_2025_2026.json"))
    args = parser.parse_args()

    preview = json.loads(Path(args.preview).read_text(encoding="utf-8"))
    matrix = json.loads(Path(args.matrix).read_text(encoding="utf-8"))
    match = find_candidate(args.player, matrix)
    if not match:
        raise SystemExit(f"Oyuncu pozisyon scout matrisinde bulunamadı: {args.player}")
    role, candidate = match
    simulation = simulate_transfer_candidate(preview["probabilities"], role, candidate)
    if not simulation:
        raise SystemExit(f"Oyuncu için simülasyon üretilemedi: {args.player}")

    output = {
        "match": preview["match"],
        "selected_player": args.player,
        "simulation": simulation,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


def find_candidate(player_name: str, matrix: dict) -> tuple[dict, dict] | None:
    needle = canonical_player_name(player_name)
    best = None
    best_score = 0.0
    for role in matrix.get("roles", []):
        for candidate in role.get("top_candidates", []):
            candidate_name = canonical_player_name(candidate.get("name"))
            score = SequenceMatcher(None, needle, candidate_name).ratio()
            if needle in candidate_name or candidate_name in needle:
                score = max(score, 0.92)
            if score > best_score:
                best = (role, candidate)
                best_score = score
    return best if best_score >= 0.62 else None


if __name__ == "__main__":
    main()
