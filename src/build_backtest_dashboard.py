from __future__ import annotations

import argparse
import json
from html import escape
from pathlib import Path

from src.config import PROCESSED_DIR
from src.html_utils import _build_nav


def main() -> None:
    parser = argparse.ArgumentParser(description="Tahmin ve gol adayi backtestleri icin statik HTML dashboard uretir.")
    parser.add_argument("--league-model", default=str(PROCESSED_DIR / "league_prediction_model_2025_2026.json"))
    parser.add_argument("--league-market-audit", default=str(PROCESSED_DIR / "league_market_value_audit_2025_2026.json"))
    parser.add_argument("--match-backtest", default=str(PROCESSED_DIR / "match_prediction_backtest_2025_2026.json"))
    parser.add_argument("--goal-backtest", default=str(PROCESSED_DIR / "goal_candidate_backtest_2025_2026.json"))
    parser.add_argument("--draw-risk", default=str(PROCESSED_DIR / "draw_risk_audit_2025_2026.json"))
    parser.add_argument(
        "--protected-action-audit",
        default=str(PROCESSED_DIR / "protected_action_audit_2025_2026.json"),
    )
    parser.add_argument("--side-flip-audit", default=str(PROCESSED_DIR / "side_flip_audit_2025_2026.json"))
    parser.add_argument("--segment-backtest", default=str(PROCESSED_DIR / "goal_candidate_segment_backtest_2025_2026.json"))
    parser.add_argument("--output", default=str(PROCESSED_DIR / "prediction_backtest_dashboard_2025_2026.html"))
    args = parser.parse_args()

    league_model = json.loads(Path(args.league_model).read_text(encoding="utf-8"))
    league_market_audit = load_json(Path(args.league_market_audit))
    match_backtest = load_json(Path(args.match_backtest))
    goal_backtest = json.loads(Path(args.goal_backtest).read_text(encoding="utf-8"))
    draw_risk = load_json(Path(args.draw_risk))
    protected_action = load_json(Path(args.protected_action_audit))
    side_flip = load_json(Path(args.side_flip_audit))
    segment_backtest = load_json(Path(args.segment_backtest))
    output = Path(args.output)
    output.write_text(
        build_html(league_model, league_market_audit, match_backtest, goal_backtest, draw_risk, protected_action, side_flip, segment_backtest),
        encoding="utf-8",
    )
    print(output)


def build_html(
    league_model: dict,
    league_market_audit: dict,
    match_backtest: dict,
    goal_backtest: dict,
    draw_risk: dict,
    protected_action: dict,
    side_flip: dict,
    segment_backtest: dict,
) -> str:
    summary = league_model["summary"]
    market_summary = league_market_audit.get("summary", {})
    match_summary = match_backtest.get("summary", {})
    goal_summary = goal_backtest["summary"]
    draw_summary = draw_risk.get("summary", {})
    protected_summary = protected_action.get("summary", {})
    side_flip_summary = side_flip.get("summary", {})
    segment_summary = segment_backtest.get("summary", {})
    rank_buckets = segment_summary.get("rank_buckets", {})
    recent_rows = league_model["rows"][-60:]
    wrong_high_confidence = [
        row for row in league_model["rows"] if row["confidence"] == "HIGH" and not row["correct"]
    ][-30:]
    low_confidence = [row for row in league_model["rows"] if row["confidence"] == "LOW"][-30:]
    protected_rows = [
        row for row in draw_risk.get("rows", [])
        if row.get("recommended_model_action") != "KEEP_MAIN_PICK"
    ][-40:]
    match_rows = match_backtest.get("rows", [])[-40:]
    weak_goal_candidates = segment_backtest.get("weak_candidates", [])[:20]

    nav = _build_nav("Analiz")
    return f"""<!doctype html>
<html lang="tr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Tahmin Backtest Paneli — metric11</title>
  <meta name="description" content="Süper Lig maç ve gol tahminlerinin geçmiş sezon backtest analizi: doğruluk oranları, hata dağılımı ve model kalibrasyonu — metric11.">
  <meta property="og:title" content="Tahmin Backtest Paneli — metric11">
  <meta property="og:description" content="Süper Lig maç ve gol tahminlerinin geçmiş sezon backtest analizi — metric11.">
  <meta property="og:image" content="https://metric11.com/og-image.png">
  <meta property="og:type" content="website">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:image" content="https://metric11.com/og-image.png">
  <meta name="theme-color" content="#091810">
  <link rel="icon" href="favicon.svg" type="image/svg+xml">
  <style>
    body {{ margin:0; font-family: Inter, system-ui, sans-serif; background:#f3f5f7; color:#15181d; }}
    .topbar {{ position:sticky; top:0; z-index:5; display:flex; align-items:center; justify-content:space-between; gap:20px; min-height:58px; padding:0 clamp(16px,4vw,42px); background:#091810; color:white; border-bottom:2px solid #1a3023; }}
    .brand {{ display:flex; gap:10px; align-items:center; font-weight:800; font-size:18px; color:white; text-decoration:none; flex-shrink:0; letter-spacing:-0.2px; }}
    .brand:visited,.brand:active,.brand:hover {{ color:white; }}
    .brand-mark {{ width:28px; height:28px; display:grid; place-items:center; border-radius:6px; color:#091810; background:#cde94e; font-size:14px; font-weight:900; flex-shrink:0; }}
    .season {{ color:#6b7c72; font-size:11px; font-weight:500; margin-left:2px; border-left:1px solid #2a3d30; padding-left:8px; }}
    nav {{ display:flex; gap:2px; flex-wrap:nowrap; overflow-x:auto; justify-content:flex-end; scrollbar-width:none; }}
    nav::-webkit-scrollbar {{ display:none; }}
    nav a {{ color:#8fa89a; text-decoration:none; font-size:13px; font-weight:600; padding:8px 11px; border-radius:6px; white-space:nowrap; transition:background .15s,color .15s; }}
    nav a:visited {{ color:#8fa89a; }}
    nav a:hover {{ background:#162b20; color:white; }}
    nav a.active {{ background:#162b20; color:white; }}
    .page-header {{ background:#10151f; color:#fff; padding:26px 38px; border-bottom:4px solid #1f9d55; }}
    .back-link {{ display:inline-flex; align-items:center; gap:6px; color:#4ade80; text-decoration:none; font-size:13px; font-weight:600; margin-bottom:10px; }}
    .back-link::before {{ content:"←"; }}
    main {{ max-width:1320px; margin:0 auto; padding:24px; }}
    @media (max-width:680px) {{ .topbar {{ position:static; flex-direction:column; align-items:stretch; padding:11px 16px 0; gap:0; min-height:unset; }} .brand {{ padding-bottom:8px; }} .season {{ display:none; }} nav {{ justify-content:flex-start; border-top:1px solid #1e3228; padding:7px 0 9px; }} }}
    .grid {{ display:grid; grid-template-columns:repeat(4, 1fr); gap:14px; margin-bottom:18px; }}
    .metric, section {{ background:white; border:1px solid #dde3ea; border-radius:8px; box-shadow:0 8px 20px rgba(18,24,32,.07); }}
    .metric {{ padding:16px; }}
    .metric strong {{ display:block; font-size:28px; margin-top:5px; }}
    .metric span, p {{ color:#667085; }}
    section {{ padding:18px; margin-bottom:18px; }}
    h1 {{ margin:0 0 6px; font-size:28px; }} h2 {{ margin:0 0 14px; font-size:18px; }}
    table {{ width:100%; border-collapse:collapse; font-size:13px; }}
    th,td {{ padding:9px 7px; border-bottom:1px solid #e4e8ef; text-align:left; vertical-align:top; }}
    th {{ color:#667085; font-size:12px; }}
    .ok {{ color:#0f7a3a; font-weight:700; }} .bad {{ color:#bd1e2d; font-weight:700; }}
    .pill {{ display:inline-block; padding:3px 7px; border-radius:999px; font-size:12px; background:#eef2f7; }}
    @media (max-width: 900px) {{ .grid {{ grid-template-columns:1fr 1fr; }} }}
    @media (max-width: 620px) {{ .grid {{ grid-template-columns:1fr; }} main {{ padding:14px; }} table {{ font-size:12px; }} }}
  </style>
</head>
<body>
  {nav}
  <div class="page-header">
    <a class="back-link" href="/">Ana sayfaya dön</a>
    <h1>Tahmin Backtest Paneli</h1>
    <p>Lig geneli Poisson/Elo modelinin ve Beşiktaş gol adayı motorunun geçmiş maç performansı.</p>
  </div>
  <main>
    <div class="grid">
      {metric("BJK ekran tahmini", f"%{round(match_summary.get('accuracy', 0) * 100)}", f"{match_summary.get('correct', 0)} / {match_summary.get('report_count', 0)} maç")}
      {metric("Ham tahmine göre artış", f"+{round((match_summary.get('accuracy', 0) - match_summary.get('raw_accuracy', 0)) * 100)} puan", f"ham %{round(match_summary.get('raw_accuracy', 0) * 100)}")}
      {metric("Lig tahmin doğruluğu", f"{summary['correct']} / {summary['matches']}", f"%{round(summary['accuracy'] * 100)} doğru")}
      {metric("Lig değer kapsamı", f"{market_summary.get('covered_matches', 0)} / {market_summary.get('league_model_matches', 0)}", "18 takım piyasa değeri")}
      {metric("Değer baseline", f"%{round(market_summary.get('reporting_baseline_accuracy', 0) * 100)}", "Tanısal, üretim girdisi değil")}
      {metric("Emin olunan maçlar", f"%{round(summary['confidence_breakdown']['HIGH']['accuracy'] * 100)}", f"{summary['confidence_breakdown']['HIGH']['matches']} maç")}
      {metric("Olasılık hata puanı", summary["brier_score"], "Düşük değer daha iyi")}
      {metric("Golcü listesi isabeti", f"%{round(goal_summary['top_5_hit_rate'] * 100)}", f"{goal_summary['top_5_hits']} / {goal_summary['matches_with_besiktas_goal']} maç")}
      {metric("Beraberlik uyarısı", draw_summary.get("medium_plus_flags", 0), f"%{round(draw_summary.get('medium_plus_recall', 0) * 100)} yakalama")}
      {metric("Yüksek beraberlik alarmı", draw_summary.get("high_flags", 0), f"%{round(draw_summary.get('high_precision', 0) * 100)} isabet")}
      {metric("BJK temkinli tahmin", protected_summary.get("protected_count", 0), f"%{round(protected_summary.get('protected_draw_precision', 0) * 100)} beraberlik")}
      {metric("BJK taraf doğru kaldı", protected_summary.get("protected_side_correct", 0), f"%{round(protected_summary.get('protected_side_correct_rate', 0) * 100)} doğru")}
      {metric("Ters taraf hatası", side_flip_summary.get("side_flip_count", 0), f"{side_flip_summary.get('target_overrated_count', 0)} BJK fazla değerleme")}
      {metric("Rakip değer kapsama", f"{side_flip_summary.get('opponent_market_value_covered', 0)} / {side_flip_summary.get('side_flip_count', 0)}", "Ters taraf market edge")}
      {metric("Veri boşluğu", side_flip_summary.get("missing_data_gap_counts", {}).get("odds_baseline_missing", 0), "Odds/sakatlık/11 kalitesi")}
      {metric("Golcü segment isabeti", f"%{round(rank_buckets.get('top_5', {}).get('match_hit_rate', 0) * 100)}", "İlk 5 golcü listesi")}
      {metric("Zayıf golcü adayı", len(weak_goal_candidates), "Puan etkisi düşürülecek")}
    </div>
    <section>
      <h2>Son 60 Lig Tahmini</h2>
      {prediction_table(recent_rows)}
    </section>
    <section>
      <h2>Yanlış Yüksek Güvenli Tahminler</h2>
      <p>Bu liste modelin en çok öğrenmesi gereken maçları gösterir.</p>
      {prediction_table(wrong_high_confidence)}
    </section>
    <section>
      <h2>Düşük Güvenli Maçlar</h2>
      <p>Ürün ekranında bu maçlarda tek taraf iddiası yerine senaryo ve risk anlatısı öne çıkarılmalı.</p>
      {prediction_table(low_confidence)}
    </section>
    <section>
      <h2>Beşiktaş Ekran Tahmini Denetimi</h2>
      <p>Bu tablo kullanıcıya gösterilen kalibre edilmiş tahmin ile ham en yüksek olasılık tahminini yan yana gösterir.</p>
      {match_backtest_table(match_rows)}
    </section>
    <section>
      <h2>Korumalı Tahmin Aksiyonları</h2>
      <p>Bu liste ana tahmini değiştirmeden beraberlik senaryosunu görünür yapması gereken maçları gösterir.</p>
      {draw_risk_table(protected_rows)}
    </section>
    <section>
      <h2>Beşiktaş Korumalı Aksiyon Backtesti</h2>
      <p>Bu tablo Beşiktaş maç önü raporlarında korumalı aksiyonun gerçek sonuçla nasıl eşleştiğini gösterir.</p>
      {protected_action_table(protected_action.get("protected_rows", []))}
    </section>
    <section>
      <h2>Yanlış Taraf Denetimi</h2>
      <p>Bu tablo beraberlikten bağımsız olarak modelin taraf seçimini ters aldığı maçları ve veri boşluklarını gösterir.</p>
      {side_flip_table(side_flip.get("rows", []))}
    </section>
    <section>
      <h2>Gol Adayı Segment Denetimi</h2>
      <p>Segment backtest, hangi aday tiplerinin üst sıralarda tutulacağını ve hangilerinin ayrı senaryo olarak gösterileceğini belirler.</p>
      {segment_table(segment_backtest.get("segments", []))}
    </section>
    <section>
      <h2>Zayıf Gol Adayı Kuyruğu</h2>
      <p>Bu oyuncular tekrar tekrar Top 5'e girip gol üretmediği için sıralama etkisi azaltılmalı veya aday tipi kontrol edilmeli.</p>
      {weak_candidate_table(weak_goal_candidates)}
    </section>
  </main>
  <script defer src="/_vercel/insights/script.js"></script>
</body>
</html>
"""


def metric(title: str, value, detail: str) -> str:
    return f'<div class="metric"><span>{escape(title)}</span><strong>{escape(str(value))}</strong><span>{escape(detail)}</span></div>'


def prediction_table(rows: list[dict]) -> str:
    body = "".join(prediction_row(row) for row in rows)
    return (
        "<table><thead><tr><th>Tarih</th><th>Maç</th><th>Skor</th><th>Tahmin</th>"
        "<th>Gerçek</th><th>xG</th><th>Model Skor</th><th>Güven</th><th>Risk</th><th>Sonuç</th></tr></thead>"
        f"<tbody>{body}</tbody></table>"
    )


def draw_risk_table(rows: list[dict]) -> str:
    body = "".join(draw_risk_row(row) for row in rows)
    return (
        "<table><thead><tr><th>Tarih</th><th>Maç</th><th>Skor</th><th>Tahmin</th>"
        "<th>Gerçek</th><th>Risk</th><th>Aksiyon</th><th>Neden</th></tr></thead>"
        f"<tbody>{body}</tbody></table>"
    )


def match_backtest_table(rows: list[dict]) -> str:
    body = "".join(match_backtest_row(row) for row in rows)
    return (
        "<table><thead><tr><th>Tarih</th><th>Maç</th><th>Skor</th><th>Ekran</th>"
        "<th>Ham</th><th>Gerçek</th><th>Ayar</th><th>Sonuç</th></tr></thead>"
        f"<tbody>{body}</tbody></table>"
    )


def protected_action_table(rows: list[dict]) -> str:
    body = "".join(protected_action_row(row) for row in rows)
    return (
        "<table><thead><tr><th>Hafta</th><th>Tarih</th><th>Maç</th><th>Skor</th>"
        "<th>Tahmin</th><th>Gerçek</th><th>Aksiyon</th><th>Risk</th><th>Neden</th></tr></thead>"
        f"<tbody>{body}</tbody></table>"
    )


def side_flip_table(rows: list[dict]) -> str:
    body = "".join(side_flip_row(row) for row in rows)
    return (
        "<table><thead><tr><th>Hafta</th><th>Maç</th><th>Skor</th><th>Tahmin</th>"
        "<th>Gerçek</th><th>xG Edge</th><th>Market Edge</th><th>Risk</th><th>Veri Boşluğu</th><th>Etiket</th></tr></thead>"
        f"<tbody>{body}</tbody></table>"
    )


def segment_table(rows: list[dict]) -> str:
    body = "".join(segment_row(row) for row in rows)
    return (
        "<table><thead><tr><th>Segment</th><th>Aday</th><th>Maç</th><th>İsabetli Maç</th>"
        "<th>Maç Hit</th><th>Top 5 Hit</th><th>Ortalama Rank</th></tr></thead>"
        f"<tbody>{body}</tbody></table>"
    )


def weak_candidate_table(rows: list[dict]) -> str:
    body = "".join(weak_candidate_row(row) for row in rows)
    return (
        "<table><thead><tr><th>Oyuncu</th><th>Aday Tipi</th><th>Satır</th><th>Top 5</th>"
        "<th>İsabet</th><th>Aksiyon</th></tr></thead>"
        f"<tbody>{body}</tbody></table>"
    )


def prediction_row(row: dict) -> str:
    labels = {"home": "Ev", "draw": "X", "away": "Dep"}
    status = '<span class="ok">Doğru</span>' if row["correct"] else '<span class="bad">Yanlış</span>'
    risk = ", ".join(row["risk_flags"]) if row["risk_flags"] else "-"
    match = f"{row['home']} - {row['away']}"
    xg = f"{row['expected_home_goals']} - {row['expected_away_goals']}"
    scoreline = (row.get("recommended_scoreline") or {}).get("score") or "-"
    return (
        f"<tr><td>{escape(row['date'])}</td><td>{escape(match)}</td><td>{escape(row['score'])}</td>"
        f"<td>{labels[row['predicted']]}</td><td>{labels[row['actual']]}</td><td>{escape(xg)}</td>"
        f"<td>{escape(scoreline)}</td><td><span class=\"pill\">{escape(row['confidence'])}</span></td><td>{escape(risk)}</td><td>{status}</td></tr>"
    )


def match_backtest_row(row: dict) -> str:
    labels = {"target_win": "BJK", "draw": "X", "opponent_win": "Rakip"}
    status = '<span class="ok">Doğru</span>' if row.get("correct") else '<span class="bad">Yanlış</span>'
    return (
        f"<tr><td>{escape(row.get('date', ''))}</td><td>{escape(row.get('fixture', ''))}</td>"
        f"<td>{escape(row.get('actual_score', ''))}</td>"
        f"<td>{escape(labels.get(row.get('predicted'), row.get('predicted', '')))}</td>"
        f"<td>{escape(labels.get(row.get('raw_predicted'), row.get('raw_predicted', '')))}</td>"
        f"<td>{escape(labels.get(row.get('actual'), row.get('actual', '')))}</td>"
        f"<td>{escape(adjustment_label(row.get('prediction_adjustment')))}</td><td>{status}</td></tr>"
    )


def draw_risk_row(row: dict) -> str:
    labels = {"home": "Ev", "draw": "X", "away": "Dep"}
    action_labels = {
        "PROTECT_SIDE_PICK_SHOW_DRAW_SCENARIO": "Korumalı taraf tahmini",
        "KEEP_PICK_WITH_DRAW_WARNING": "Beraberlik uyarılı tahmin",
        "KEEP_MAIN_PICK": "Ana tahmini koru",
    }
    match = f"{row.get('home')} - {row.get('away')}"
    reasons = ", ".join(row.get("draw_risk_reasons", [])[:4]) or "-"
    return (
        f"<tr><td>{escape(row.get('date', ''))}</td><td>{escape(match)}</td><td>{escape(row.get('score', ''))}</td>"
        f"<td>{escape(labels.get(row.get('predicted'), ''))}</td><td>{escape(labels.get(row.get('actual'), ''))}</td>"
        f"<td><span class=\"pill\">{escape(row.get('draw_risk_level', 'LOW'))} / {row.get('draw_risk_score', 0)}</span></td>"
        f"<td>{escape(action_labels.get(row.get('recommended_model_action'), row.get('recommended_model_action', '')))}</td>"
        f"<td>{escape(reasons)}</td></tr>"
    )


def protected_action_row(row: dict) -> str:
    labels = {"target_win": "BJK", "draw": "X", "opponent_win": "Rakip"}
    reasons = ", ".join(row.get("draw_risk_reasons", [])[:4]) or "-"
    risk = f"{row.get('draw_risk_level') or '-'} / {row.get('draw_risk_score') or '-'}"
    return (
        f"<tr><td>{row.get('week', '')}</td><td>{escape(row.get('date', ''))}</td>"
        f"<td>{escape(row.get('fixture', ''))}</td><td>{escape(row.get('actual_score', ''))}</td>"
        f"<td>{escape(labels.get(row.get('predicted'), ''))}</td>"
        f"<td>{escape(labels.get(row.get('actual'), ''))}</td>"
        f"<td>{escape(row.get('action_label', ''))}</td><td><span class=\"pill\">{escape(risk)}</span></td>"
        f"<td>{escape(reasons)}</td></tr>"
    )


def side_flip_row(row: dict) -> str:
    labels = {"target_win": "BJK", "draw": "X", "opponent_win": "Rakip"}
    gaps = ", ".join(row.get("data_gaps", [])[:4]) or "-"
    tags = ", ".join(row.get("signal_tags", [])[:4]) or "-"
    risk = f"{row.get('draw_risk_level') or '-'} / {row.get('draw_risk_score') or '-'}"
    market_edge = row.get("market_value_edge_million_eur")
    market_edge_text = f"€{market_edge}m" if market_edge is not None else "-"
    return (
        f"<tr><td>{row.get('week', '')}</td><td>{escape(row.get('fixture', ''))}</td>"
        f"<td>{escape(row.get('actual_score', ''))}</td>"
        f"<td>{escape(labels.get(row.get('predicted'), ''))}</td>"
        f"<td>{escape(labels.get(row.get('actual'), ''))}</td>"
        f"<td>{row.get('xg_edge')}</td><td>{escape(market_edge_text)}</td><td><span class=\"pill\">{escape(risk)}</span></td>"
        f"<td>{escape(gaps)}</td><td>{escape(tags)}</td></tr>"
    )


def adjustment_label(value: str | None) -> str:
    labels = {
        "none": "Yok",
        "protected_side": "Temkinli taraf",
        "high_draw_risk_override": "Beraberlik kalibrasyonu",
        "big_match_opponent_edge": "Derbi rakip üstünlüğü",
        "big_match_negative_strength_high_card": "Derbi rakip/kart düzeltmesi",
    }
    return labels.get(value or "none", value or "Yok")


def segment_row(row: dict) -> str:
    return (
        f"<tr><td><span class=\"pill\">{escape(row.get('segment', ''))}</span></td>"
        f"<td>{row.get('candidate_rows', 0)}</td><td>{row.get('matches', 0)}</td>"
        f"<td>{row.get('hit_matches', 0)}</td><td>%{round(row.get('match_hit_rate', 0) * 100, 1)}</td>"
        f"<td>%{round(row.get('top5_match_hit_rate', 0) * 100, 1)}</td>"
        f"<td>{row.get('avg_rank', 0)}</td></tr>"
    )


def weak_candidate_row(row: dict) -> str:
    return (
        f"<tr><td>{escape(row.get('player_name', ''))}</td>"
        f"<td><span class=\"pill\">{escape(row.get('candidate_type', ''))}</span></td>"
        f"<td>{row.get('rows', 0)}</td><td>{row.get('top5_rows', 0)}</td>"
        f"<td>{row.get('hits', 0)}</td><td>{escape(row.get('recommendation', ''))}</td></tr>"
    )


def load_json(path: Path) -> dict:
    if not path.exists():
        return {"summary": {}, "rows": []}
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
