"""Ana sayfa "Bu Hafta" kahraman modülü için aktif/yaklaşan haftayı üretir.

`season_fixture_predictions_2026_2027.json`'dan oynanmamış maçı olan ilk haftayı
(tümü oynanmışsa son haftayı) seçer; bu haftanın maç kartlarını (tahmin + olasılık +
güven) ve geçen haftanın isabet özetini `match_week_2026_2027.json`'a yazar. Ayrıca
`render_hero_html()` fonksiyonuyla ana sayfaya (build_live_feed.py) doğrudan gömülebilen
bir HTML parçası sunar.
"""
from __future__ import annotations

import json
import re
from datetime import datetime
from html import escape

from src.config import PROCESSED_DIR

FIXTURE_PRED_PATH = PROCESSED_DIR / "season_fixture_predictions_2026_2027.json"
WEEKLY_EVAL_PATH = PROCESSED_DIR / "weekly_evaluation_2026_2027.json"
OUTPUT_JSON = PROCESSED_DIR / "match_week_2026_2027.json"

_TR_MONTHS = ["", "Oca", "Şub", "Mar", "Nis", "May", "Haz", "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara"]
_PICK_LABEL = {"home": "Ev Sahibi", "draw": "Beraberlik", "away": "Deplasman"}


def _fmt_date(date_str: str) -> str:
    try:
        dt = datetime.strptime(date_str.split(" ")[0], "%d.%m.%Y")
        return f"{dt.day} {_TR_MONTHS[dt.month]}"
    except (ValueError, IndexError):
        return date_str


def _select_week(weeks: list[dict]) -> dict | None:
    """Oynanmamış maçı olan ilk hafta; yoksa son hafta."""
    for week in weeks:
        if any(not m.get("is_played") for m in week.get("matches", [])):
            return week
    return weeks[-1] if weeks else None


def build_payload() -> dict:
    if not FIXTURE_PRED_PATH.exists():
        return {"available": False, "generated_at": datetime.now().isoformat()}
    fixture = json.loads(FIXTURE_PRED_PATH.read_text(encoding="utf-8"))
    week = _select_week(fixture.get("weeks", []))
    if not week:
        return {"available": False, "generated_at": datetime.now().isoformat()}

    matches = []
    for m in week["matches"]:
        pick = m.get("predicted")
        if pick == "home":
            pick_text = m["home_team"]
        elif pick == "away":
            pick_text = m["away_team"]
        else:
            pick_text = "Beraberlik"
        matches.append({
            "match_id": m.get("match_id"),
            "date": _fmt_date(m.get("date_time", "")),
            "home_team": m.get("home_team"),
            "away_team": m.get("away_team"),
            "is_played": m.get("is_played"),
            "actual_score": m.get("actual_score"),
            "predicted": pick,
            "pick_text": pick_text,
            "home_win_probability": m.get("home_win_probability"),
            "draw_probability": m.get("draw_probability"),
            "away_win_probability": m.get("away_win_probability"),
            "data_confidence": m.get("data_confidence"),
            "recommended_scoreline": (m.get("recommended_scoreline") or {}).get("score"),
            "expected_home_goals": m.get("expected_home_goals"),
            "expected_away_goals": m.get("expected_away_goals"),
        })

    last_week_summary = None
    if WEEKLY_EVAL_PATH.exists():
        try:
            ev = json.loads(WEEKLY_EVAL_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            ev = {}
        last_week = ev.get("last_week")
        if last_week:
            last_week_summary = {"week": last_week["week"], **last_week["summary"]}

    return {
        "available": True,
        "generated_at": datetime.now().isoformat(),
        "week": week["week"],
        "matches": matches,
        "last_week": last_week_summary,
    }


def _pick_class(pick: str) -> str:
    return {"home": "#116447", "away": "#bd2936", "draw": "#627067"}.get(pick, "#627067")


def render_hero_html(payload: dict | None = None) -> str:
    """Ana sayfaya gömülebilen "Bu Hafta" hero HTML parçası (self-contained inline stil)."""
    if payload is None:
        payload = build_payload()
    if not payload.get("available") or not payload.get("matches"):
        return ""

    lw = payload.get("last_week")
    last_week_pill = ""
    if lw and lw.get("evaluated_matches"):
        acc = round((lw.get("accuracy") or 0) * 100)
        last_week_pill = (
            f'<span style="display:inline-flex;align-items:center;gap:6px;background:#edf5ef;'
            f'border:1px solid #cce0d3;color:#116447;font-size:12px;font-weight:700;'
            f'padding:4px 10px;border-radius:20px;">Geçen hafta (Hafta {lw["week"]}): '
            f'{lw["correct"]}/{lw["evaluated_matches"]} isabet · %{acc} '
            f'<a href="weekly_evaluation_2026_2027.html" style="color:#116447;text-decoration:underline;">karne</a></span>'
        )

    rows = []
    for m in payload["matches"]:
        if m.get("is_played"):
            right = f'<span style="font-weight:800;color:#132018;">{escape(m.get("actual_score") or "")}</span><span style="font-size:11px;color:#8fa89a;margin-left:6px;">oynandı</span>'
        else:
            color = _pick_class(m.get("predicted"))
            probs = (
                f'<span style="color:#116447;">Ev %{round((m.get("home_win_probability") or 0)*100)}</span> · '
                f'<span style="color:#627067;">X %{round((m.get("draw_probability") or 0)*100)}</span> · '
                f'<span style="color:#bd2936;">Dep %{round((m.get("away_win_probability") or 0)*100)}</span>'
            )
            score = m.get("recommended_scoreline")
            xhg, xag = m.get("expected_home_goals"), m.get("expected_away_goals")
            score_line = ""
            if score:
                xg_part = (
                    f' · xG {xhg:.1f}–{xag:.1f}'
                    if isinstance(xhg, (int, float)) and isinstance(xag, (int, float)) else ""
                )
                score_line = (
                    f'<div style="font-size:11px;color:#627067;margin-top:3px;">Olası skor '
                    f'<span style="font-weight:800;color:#132018;">{escape(str(score))}</span>'
                    f'<span style="color:#8fa89a;">{xg_part}</span></div>'
                )
            right = (
                f'<span style="display:inline-block;font-size:12px;font-weight:700;color:#fff;'
                f'background:{color};padding:3px 9px;border-radius:5px;">{escape(m.get("pick_text") or "")}</span>'
                f'<div style="font-size:11px;color:#627067;margin-top:4px;">{probs}</div>'
                f'{score_line}'
            )
        rows.append(
            f'<div style="display:flex;justify-content:space-between;align-items:center;gap:12px;'
            f'padding:10px 0;border-bottom:1px solid #eef2ef;">'
            f'<div><div style="font-size:10px;color:#8fa89a;">{escape(m.get("date") or "")}</div>'
            f'<div style="font-size:14px;font-weight:700;color:#132018;">{escape(m.get("home_team") or "")} '
            f'<span style="color:#8fa89a;font-weight:600;font-size:11px;">vs</span> {escape(m.get("away_team") or "")}</div></div>'
            f'<div style="text-align:right;">{right}</div></div>'
        )

    return (
        '<section style="background:#fff;border:1px solid #d7ded9;border-radius:12px;'
        'padding:18px 20px;margin-bottom:18px;border-top:3px solid #116447;">'
        '<div style="display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:6px;">'
        f'<div><div style="font-size:11px;font-weight:700;color:#116447;text-transform:uppercase;letter-spacing:.06em;">Bu Hafta · Hafta {payload["week"]}</div>'
        '<div style="font-size:19px;font-weight:800;color:#132018;">Skor Tahminleri</div></div>'
        f'{last_week_pill}</div>'
        '<div style="font-size:12px;color:#627067;margin-bottom:8px;line-height:1.5;">'
        'Oynanan her maç ve doğrulanan her transfer bir sonraki haftanın tahminini besliyor; her gün güncelleniyor.</div>'
        f'{"".join(rows)}'
        '<a href="season_fixture_predictions_2026_2027.html" style="display:inline-block;margin-top:12px;'
        'color:#116447;font-weight:700;font-size:13px;text-decoration:none;">Tüm fikstür ve tahminlere git →</a>'
        '</section>'
    )


def main() -> None:
    payload = build_payload()
    OUTPUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    if payload.get("available"):
        print(f"Kaydedildi: Hafta {payload['week']}, {len(payload['matches'])} maç")
    else:
        print("Fikstür tahmini bulunamadı; Bu Hafta modülü boş.")


if __name__ == "__main__":
    main()
