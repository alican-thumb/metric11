"""2026-27 Süper Lig haftalık tahmin karnesi üretir.

`season_fixture_predictions_2026_2027.json`'daki OYNANMIŞ maçlar için modelin
tahminini (`predicted`) gerçek sonuçla (`actual_score`) karşılaştırır: hafta bazında
isabet oranı, beraberlik yakalama ve en iyi/kötü tahminleri çıkarır. Sonuçlar zaten
`advance_season_state` + `build_season_fixture_predictions` zinciriyle bir sonraki
haftanın tahminine besleniyor; bu rapor o döngüyü kullanıcıya görünür kılar.

Çıktılar: weekly_evaluation_2026_2027.{json,md,html}
"""
from __future__ import annotations

import json
import re
from datetime import datetime

from src.config import PROCESSED_DIR
from src.html_utils import md_to_html, page_html

FIXTURE_PRED_PATH = PROCESSED_DIR / "season_fixture_predictions_2026_2027.json"
OUTPUT_JSON = PROCESSED_DIR / "weekly_evaluation_2026_2027.json"
OUTPUT_MD = PROCESSED_DIR / "weekly_evaluation_2026_2027.md"
OUTPUT_HTML = PROCESSED_DIR / "weekly_evaluation_2026_2027.html"

_PICK_LABEL = {"home": "Ev", "draw": "Beraberlik", "away": "Deplasman"}


def _actual_outcome(score: str | None) -> str | None:
    """'2-1' biçimindeki skoru 1X2 sonucuna çevirir."""
    if not score:
        return None
    m = re.match(r"\s*(\d+)\s*\D+\s*(\d+)", score)
    if not m:
        return None
    home, away = int(m.group(1)), int(m.group(2))
    if home > away:
        return "home"
    if away > home:
        return "away"
    return "draw"


def _prediction_confidence(m: dict) -> str:
    """Maç oynanmadan ÖNCEKİ model güven etiketini (HIGH/MEDIUM/LOW), o anki
    home/draw/away olasılıklarından yeniden hesaplar.

    `data_confidence` alanı oynanmış maçlarda görüntüleme amacıyla "PLAYED"
    ile eziliyor (bkz. build_season_fixture_predictions.py), bu yüzden gerçek
    güven etiketi orada saklı değil — ama olasılıkların kendisi değişmediği
    için `model_league_predictions.confidence_label` ile AYNI eşiklerle
    burada güvenilir şekilde yeniden türetilebilir.
    """
    probs = sorted([
        m.get("home_win_probability") or 0.0,
        m.get("draw_probability") or 0.0,
        m.get("away_win_probability") or 0.0,
    ], reverse=True)
    top, margin = probs[0], probs[0] - probs[1]
    if top >= 0.52 and margin >= 0.16:
        return "HIGH"
    if top >= 0.43 and margin >= 0.08:
        return "MEDIUM"
    return "LOW"


def _evaluate_match(m: dict) -> dict | None:
    if not m.get("is_played"):
        return None
    actual = _actual_outcome(m.get("actual_score"))
    if actual is None:
        return None
    predicted = m.get("predicted")
    return {
        "match_id": m.get("match_id"),
        "date_time": m.get("date_time"),
        "home_team": m.get("home_team"),
        "away_team": m.get("away_team"),
        "actual_score": m.get("actual_score"),
        "actual": actual,
        "predicted": predicted,
        "raw_predicted": m.get("raw_predicted"),
        "correct": predicted == actual,
        "data_confidence": m.get("data_confidence"),
        "prediction_confidence": _prediction_confidence(m),
        "home_win_probability": m.get("home_win_probability"),
        "draw_probability": m.get("draw_probability"),
        "away_win_probability": m.get("away_win_probability"),
    }


def _pick_probability(ev: dict) -> float:
    return {
        "home": ev.get("home_win_probability") or 0.0,
        "draw": ev.get("draw_probability") or 0.0,
        "away": ev.get("away_win_probability") or 0.0,
    }.get(ev.get("predicted"), 0.0)


def _summarize(evaluations: list[dict]) -> dict:
    total = len(evaluations)
    correct = sum(1 for e in evaluations if e["correct"])
    actual_draws = [e for e in evaluations if e["actual"] == "draw"]
    draws_caught = sum(1 for e in actual_draws if e["predicted"] == "draw")
    high_conf = [e for e in evaluations if e.get("prediction_confidence") == "HIGH"]
    high_conf_correct = sum(1 for e in high_conf if e["correct"])
    return {
        "evaluated_matches": total,
        "correct": correct,
        "accuracy": round(correct / total, 4) if total else 0.0,
        "actual_draws": len(actual_draws),
        "draws_caught": draws_caught,
        "draw_recall": round(draws_caught / len(actual_draws), 4) if actual_draws else None,
        "high_conf_matches": len(high_conf),
        "high_conf_correct": high_conf_correct,
        "high_conf_accuracy": round(high_conf_correct / len(high_conf), 4) if high_conf else None,
    }


def build_evaluation() -> dict:
    payload = json.loads(FIXTURE_PRED_PATH.read_text(encoding="utf-8"))
    weeks_out = []
    all_evals: list[dict] = []
    last_played_week = None
    for week in payload.get("weeks", []):
        evals = [e for e in (_evaluate_match(m) for m in week.get("matches", [])) if e]
        if not evals:
            continue
        all_evals.extend(evals)
        week_summary = _summarize(evals)
        weeks_out.append({"week": week["week"], "summary": week_summary, "matches": evals})
        last_played_week = week["week"]

    overall = _summarize(all_evals)

    # Ana sayfa özeti için en son oynanan hafta.
    last_week_block = next((w for w in reversed(weeks_out)), None)

    return {
        "generated_at": datetime.now().isoformat(),
        "season": "2026-2027",
        "summary": overall,
        "last_played_week": last_played_week,
        "last_week": last_week_block,
        "weeks": weeks_out,
        "feedback_note": (
            "Oynanan her maçın sonucu, tahmin motorunun takım formu/Elo durumunu ilerletir; "
            "bu yüzden bir sonraki haftanın skor tahminleri geçen haftanın gerçek sonuçlarıyla "
            "güncellenir. Doğrulanan transferler de aynı şekilde güce yansır."
        ),
    }


def _pct(value: float | None) -> str:
    return "—" if value is None else f"%{round(value * 100)}"


def build_markdown(payload: dict) -> str:
    s = payload["summary"]
    lines = [
        "# 2026-27 Süper Lig — Haftalık Tahmin Karnesi",
        "",
        payload["feedback_note"],
        "",
        "## Genel Karne",
        "",
        f"- Değerlendirilen maç: **{s['evaluated_matches']}**",
        f"- İsabet: **{s['correct']}/{s['evaluated_matches']}** ({_pct(s['accuracy'])})",
        f"- Beraberlik yakalama: **{s['draws_caught']}/{s['actual_draws']}** ({_pct(s['draw_recall'])})",
        f"- Yüksek güvenli maç isabeti: **{s['high_conf_correct']}/{s['high_conf_matches']}** ({_pct(s['high_conf_accuracy'])})",
        "",
    ]
    if s["evaluated_matches"] == 0:
        lines += ["_Sezon henüz başlamadı; ilk maçlar oynandıkça karne otomatik dolacak._", ""]
        return "\n".join(lines) + "\n"

    for week in reversed(payload["weeks"]):
        ws = week["summary"]
        lines.append(f"## Hafta {week['week']} — {ws['correct']}/{ws['evaluated_matches']} isabet ({_pct(ws['accuracy'])})")
        lines.append("")
        lines.append("| Maç | Skor | Tahmin | Sonuç | Güven |")
        lines.append("| --- | --- | --- | --- | --- |")
        for e in week["matches"]:
            mark = "✅" if e["correct"] else "❌"
            lines.append(
                f"| {e['home_team']} - {e['away_team']} | {e['actual_score']} | "
                f"{_PICK_LABEL.get(e['predicted'], e['predicted'])} | {mark} | {e['prediction_confidence']} |"
            )
        lines.append("")
    return "\n".join(lines) + "\n"


def build_html(payload: dict) -> str:
    body = md_to_html(build_markdown(payload))
    return page_html(
        "2026-27 Haftalık Tahmin Karnesi",
        body,
        description="Süper Lig 2026-27 maç tahminlerinin her hafta gerçek sonuçlarla karşılaştırıldığı isabet karnesi.",
        active_nav="Haftalık Karne",
    )


def main() -> None:
    if not FIXTURE_PRED_PATH.exists():
        print(f"HATA: {FIXTURE_PRED_PATH} bulunamadı. Önce build_season_fixture_predictions çalıştırın.")
        return
    payload = build_evaluation()
    OUTPUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    OUTPUT_MD.write_text(build_markdown(payload), encoding="utf-8")
    OUTPUT_HTML.write_text(build_html(payload), encoding="utf-8")
    s = payload["summary"]
    print(f"Kaydedildi: {s['evaluated_matches']} maç değerlendirildi, isabet {_pct(s['accuracy'])}")


if __name__ == "__main__":
    main()
