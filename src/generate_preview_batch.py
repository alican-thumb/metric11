from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from src.config import PROCESSED_DIR, SEASON
from src.generate_match_preview import build_markdown, build_preview, write_preview
from src.normalization import normalize_matches

ALL_TEAMS = [
    "BEŞİKTAŞ A.Ş.",
    "GALATASARAY A.Ş.",
    "FENERBAHÇE A.Ş.",
    "TRABZONSPOR A.Ş.",
    "RAMS BAŞAKŞEHİR FUTBOL KULÜBÜ",
    "CORENDON ALANYASPOR",
    "SAMSUNSPOR A.Ş.",
    "GÖZTEPE A.Ş.",
    "TÜMOSAN KONYASPOR",
    "ÇAYKUR RİZESPOR A.Ş.",
    "GAZİANTEP FUTBOL KULÜBÜ A.Ş.",
    "KASIMPAŞA A.Ş.",
    "KOCAELİSPOR",
    "İKAS EYÜPSPOR",
    "GENÇLERBİRLİĞİ",
    "MISIRLI.COM.TR FATİH KARAGÜMRÜK",
    "HESAP.COM ANTALYASPOR",
    "ZECORNER KAYSERİSPOR",
]


_TR_TABLE = str.maketrans("ğüşıöçĞÜŞİÖÇ", "gusiocgusioc")

# Hardcoded to avoid Turkish unicode normalization edge cases and preserve
# the existing besiktas output dir that other dashboards reference.
_TEAM_SLUGS: dict[str, str] = {
    "BEŞİKTAŞ A.Ş.": "besiktas",
    "GALATASARAY A.Ş.": "galatasaray",
    "FENERBAHÇE A.Ş.": "fenerbahce",
    "TRABZONSPOR A.Ş.": "trabzonspor",
    "RAMS BAŞAKŞEHİR FUTBOL KULÜBÜ": "basaksehir",
    "CORENDON ALANYASPOR": "alanyaspor",
    "SAMSUNSPOR A.Ş.": "samsunspor",
    "GÖZTEPE A.Ş.": "goztepe",
    "TÜMOSAN KONYASPOR": "konyaspor",
    "ÇAYKUR RİZESPOR A.Ş.": "rizespor",
    "GAZİANTEP FUTBOL KULÜBÜ A.Ş.": "gaziantep",
    "KASIMPAŞA A.Ş.": "kasimpasa",
    "KOCAELİSPOR": "kocaelispor",
    "İKAS EYÜPSPOR": "eyupspor",
    "GENÇLERBİRLİĞİ": "genclerbirligi",
    "MISIRLI.COM.TR FATİH KARAGÜMRÜK": "karagumruk",
    "HESAP.COM ANTALYASPOR": "antalyaspor",
    "ZECORNER KAYSERİSPOR": "kayserispor",
}


def team_slug(team: str) -> str:
    if team in _TEAM_SLUGS:
        return _TEAM_SLUGS[team]
    slug = team.lower().translate(_TR_TABLE)
    slug = re.sub(r"[^a-z0-9]+", "_", slug)
    return slug.strip("_")[:32]


def main() -> None:
    parser = argparse.ArgumentParser(description="Sezon icindeki maclar icin toplu mac onu raporu uretir.")
    parser.add_argument("--input", default=str(PROCESSED_DIR / f"tff_super_lig_enriched_{SEASON}.json"))
    parser.add_argument("--team", default="BEŞİKTAŞ A.Ş.")
    parser.add_argument("--all-teams", action="store_true", help="Tüm 18 Süper Lig takımı için çalıştır")
    parser.add_argument("--min-prior-matches", type=int, default=5)
    parser.add_argument("--availability", default=str(PROCESSED_DIR / f"player_availability_besiktas_{SEASON}.json"))
    parser.add_argument("--output-dir", default="")
    args = parser.parse_args()

    matches = normalize_matches(json.loads(Path(args.input).read_text(encoding="utf-8")))

    if args.all_teams:
        for team in ALL_TEAMS:
            avail_path = Path(args.availability) if team == "BEŞİKTAŞ A.Ş." else None
            out_dir = PROCESSED_DIR / f"previews_{team_slug(team)}_{SEASON}_chronological"
            run_for_team(matches, team, args.min_prior_matches, avail_path, out_dir)
    else:
        avail_path = Path(args.availability)
        out_dir = Path(args.output_dir) if args.output_dir else PROCESSED_DIR / f"previews_{team_slug(args.team)}_{SEASON}_chronological"
        run_for_team(matches, args.team, args.min_prior_matches, avail_path, out_dir)


def run_for_team(
    matches: list[dict],
    team: str,
    min_prior_matches: int,
    availability_path: Path | None,
    output_dir: Path,
) -> dict:
    availability = None
    if availability_path and availability_path.exists():
        availability = json.loads(availability_path.read_text(encoding="utf-8"))

    output_dir.mkdir(parents=True, exist_ok=True)

    index: list[dict] = []
    skipped: list[dict] = []
    target_matches = [
        m for m in matches
        if m["home_team"]["name"] == team or m["away_team"]["name"] == team
    ]

    for idx, match in enumerate(target_matches):
        try:
            preview = build_preview(matches, team, match["external_id"], availability)
        except SystemExit as exc:
            skipped.append({"match_id": match["external_id"], "reason": "no_chronological_prior_matches", "error": str(exc)})
            continue
        prior_count = preview["data_window"]["prior_match_count"]
        if prior_count < min_prior_matches:
            skipped.append({"match_id": match["external_id"], "reason": "not_enough_chronological_prior_matches", "prior_matches": prior_count})
            continue

        prefix = f"week_{idx + 1:02d}_{match['external_id']}"
        json_path, md_path = write_preview(preview, prefix, output_dir)
        prob = preview["probabilities"]
        index.append({
            "week": idx + 1,
            "match_id": match["external_id"],
            "date": preview["match"]["date"],
            "home_team": preview["match"]["home_team"],
            "away_team": preview["match"]["away_team"],
            "actual_score": preview["match"]["actual_score"],
            "main_referee": preview["match"]["main_referee"],
            "is_big_match": preview["match"]["is_big_match"],
            "target_win_probability": prob["target_win_probability"],
            "draw_probability": prob["draw_probability"],
            "opponent_win_probability": prob["opponent_win_probability"],
            "recommended_scoreline": prob.get("recommended_scoreline", {}).get("score"),
            "recommended_action": prob.get("recommended_call", {}).get("action"),
            "raw_prediction": prob.get("display_prediction", {}).get("raw_result"),
            "final_prediction": prob.get("display_prediction", {}).get("final_result"),
            "final_prediction_label": prob.get("display_prediction", {}).get("label"),
            "prediction_adjustment": prob.get("display_prediction", {}).get("adjustment"),
            "card_signal": prob["card_signal"],
            "team_card_expectation": prob["team_card_expectation"],
            "confidence": prob["confidence"],
            "json_path": str(json_path),
            "markdown_path": str(md_path),
        })

    summary = build_summary(index, skipped, team)
    payload = {"team": team, "summary": summary, "reports": index, "skipped": skipped}
    (output_dir / "index.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (output_dir / "index.md").write_text(build_index_markdown(payload, team), encoding="utf-8")
    print(f"[{team}] {len(index)} rapor → {output_dir}")
    return payload


def build_summary(index: list[dict], skipped: list[dict], team: str) -> dict:
    if not index:
        return {"generated_reports": 0, "skipped_reports": len(skipped)}
    high_card = [item for item in index if item["card_signal"] == "HIGH"]
    big_matches = [item for item in index if item["is_big_match"]]
    highest_card = max(index, key=lambda item: item["team_card_expectation"])
    highest_win = max(index, key=lambda item: item["target_win_probability"])
    correct = [
        item for item in index
        if item.get("final_prediction") and item.get("actual_score")
        and _prediction_correct(item, team)
    ]
    return {
        "team": team,
        "generated_reports": len(index),
        "skipped_reports": len(skipped),
        "big_match_reports": len(big_matches),
        "high_card_signal_reports": len(high_card),
        "prediction_accuracy": round(len(correct) / len(index), 3) if index else 0,
        "highest_card_expectation": {
            "match_id": highest_card["match_id"],
            "fixture": f"{highest_card['home_team']} - {highest_card['away_team']}",
            "team_card_expectation": highest_card["team_card_expectation"],
        },
        "highest_target_win_probability": {
            "match_id": highest_win["match_id"],
            "fixture": f"{highest_win['home_team']} - {highest_win['away_team']}",
            "probability": highest_win["target_win_probability"],
        },
    }


def _prediction_correct(item: dict, target_team: str) -> bool:
    score = item.get("actual_score", "")
    pred = item.get("final_prediction", "")
    if not score or "-" not in score or not pred:
        return False
    try:
        h, a = map(int, score.split("-", 1))
    except ValueError:
        return False
    is_home = item.get("home_team") == target_team
    if h == a:
        actual = "draw"
    elif is_home:
        actual = "target_win" if h > a else "opponent_win"
    else:
        actual = "target_win" if a > h else "opponent_win"
    return actual == pred


def build_index_markdown(payload: dict, team: str) -> str:
    summary = payload["summary"]
    lines = [
        f"# {team} {SEASON.replace('_', '-')} Maç Önü Rapor Arşivi",
        "",
        f"- Üretilen rapor: {summary['generated_reports']}",
        f"- Atlanan erken sezon maçı: {summary['skipped_reports']}",
        f"- Büyük maç raporu: {summary.get('big_match_reports', 0)}",
        f"- HIGH kart sinyali: {summary.get('high_card_signal_reports', 0)}",
        f"- Tahmin doğruluğu: %{round(summary.get('prediction_accuracy', 0) * 100)}",
        "",
    ]
    if summary["generated_reports"]:
        high_card = summary["highest_card_expectation"]
        highest_win = summary["highest_target_win_probability"]
        lines.extend([
            f"- En yüksek kart beklentisi: {high_card['fixture']} ({high_card['team_card_expectation']})",
            f"- En yüksek kazanma sinyali: {highest_win['fixture']} (%{round(highest_win['probability'] * 100)})",
            "",
        ])
    lines.extend(["## Raporlar", ""])
    for item in payload["reports"]:
        lines.append(
            f"- {item['week']}. hafta | {item['date']} | {item['home_team']} - {item['away_team']} "
            f"| %{round(item['target_win_probability'] * 100)} / X %{round(item['draw_probability'] * 100)} "
            f"/ Rakip %{round(item['opponent_win_probability'] * 100)} | skor {item.get('recommended_scoreline') or '-'} "
            f"| ekran tahmini {item.get('final_prediction_label') or '-'} | aksiyon {item.get('recommended_action') or '-'} "
            f"| kart {item['card_signal']} | [md]({item['markdown_path']})"
        )
    return "\n".join(lines)


if __name__ == "__main__":
    main()
