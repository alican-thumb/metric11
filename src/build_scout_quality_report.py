from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from html import escape
from pathlib import Path

from src.config import PROCESSED_DIR
from src.html_utils import _build_nav


LOW_CONFIDENCE_VALUES = {"LOW_LEAGUE_PROXY", "LOW_POSITION_UNVERIFIED", "LOW_DERIVED", "VERY_LOW", None, ""}


def main() -> None:
    parser = argparse.ArgumentParser(description="Scout adayları için veri güveni ve manuel doğrulama raporu üretir.")
    parser.add_argument("--blueprints", default=str(PROCESSED_DIR / "team_scout_blueprints_2025_2026.json"))
    parser.add_argument("--position-matrix", default=str(PROCESSED_DIR / "position_scout_matrix_2025_2026.json"))
    parser.add_argument("--output-prefix", default="scout_quality_report_2025_2026")
    args = parser.parse_args()

    blueprints = json.loads(Path(args.blueprints).read_text(encoding="utf-8"))
    position_matrix = json.loads(Path(args.position_matrix).read_text(encoding="utf-8"))
    payload = build_payload(blueprints, position_matrix)

    json_path = PROCESSED_DIR / f"{args.output_prefix}.json"
    md_path = PROCESSED_DIR / f"{args.output_prefix}.md"
    html_path = PROCESSED_DIR / f"{args.output_prefix}.html"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(build_markdown(payload), encoding="utf-8")
    html_path.write_text(build_html(payload), encoding="utf-8")
    print(md_path.read_text(encoding="utf-8"))


def build_payload(blueprints: dict, position_matrix: dict) -> dict:
    blueprint_candidates = []
    role_spread: dict[str, set[str]] = defaultdict(set)
    confidence_counts = Counter()
    missing_age_or_contract = 0
    for blueprint in blueprints.get("blueprints", []):
        for plan in blueprint.get("role_plans", []):
            for rank, candidate in enumerate(plan.get("top_candidates", []), start=1):
                item = {
                    "team": blueprint.get("team"),
                    "role_key": plan.get("role_key"),
                    "role_label": plan.get("role_label"),
                    "rank": rank,
                    **candidate,
                }
                confidence = item.get("position_confidence")
                confidence_counts[confidence or "EMPTY"] += 1
                key = item.get("player_id") or item.get("name")
                if key:
                    role_spread[str(key)].add(plan.get("role_key"))
                if item.get("age") is None or item.get("contract_months_left") is None:
                    missing_age_or_contract += 1
                blueprint_candidates.append(item)

    low_links = [
        item
        for item in blueprint_candidates
        if item.get("position_confidence") in LOW_CONFIDENCE_VALUES
    ]
    low_unique: dict[tuple[str, str], dict] = {}
    for item in low_links:
        key = (str(item.get("player_id") or item.get("name")), str(item.get("role_key")))
        enriched = {
            **item,
            "review_reason": review_reason(item),
            "next_data_need": next_data_need(item),
            "affected_team_count": 1,
            "affected_teams": [item.get("team")],
        }
        if key not in low_unique:
            low_unique[key] = enriched
            continue
        low_unique[key]["affected_team_count"] += 1
        if item.get("team") not in low_unique[key]["affected_teams"]:
            low_unique[key]["affected_teams"].append(item.get("team"))
        if (item.get("fit_score") or 0) > (low_unique[key].get("fit_score") or 0):
            low_unique[key].update({k: v for k, v in enriched.items() if k not in {"affected_team_count", "affected_teams"}})
    low_queue = list(low_unique.values())
    low_queue.sort(key=lambda item: (item.get("fit_score") or 0, item.get("rank") * -1), reverse=True)

    repeated_role_players = []
    candidate_by_key = {}
    for item in blueprint_candidates:
        key = str(item.get("player_id") or item.get("name"))
        candidate_by_key.setdefault(key, item)
    for key, roles in role_spread.items():
        if len(roles) >= 3:
            base = candidate_by_key.get(key, {})
            repeated_role_players.append(
                {
                    "player_id": base.get("player_id"),
                    "name": base.get("name"),
                    "team": base.get("team"),
                    "age": base.get("age"),
                    "roles": sorted(roles),
                    "role_count": len(roles),
                    "position_confidence": base.get("position_confidence"),
                    "action": "Doğrudan pozisyon/ayak/boy veya dış attribute verisiyle rol daraltılmalı.",
                }
            )
    repeated_role_players.sort(key=lambda item: item["role_count"], reverse=True)

    position_candidates = [
        candidate
        for role in position_matrix.get("roles", [])
        for candidate in role.get("top_candidates", [])
    ]
    position_confidence = Counter((item.get("position_confidence") or "EMPTY") for item in position_candidates)
    next_priority = (
        "Kalan düşük güvenli adaylar için Transfermarkt/API/manuel pozisyon-biyometri eşleşmesi ve rol çakışması azaltma."
        if low_queue
        else "Düşük güvenli yayın adayı kalmadı; sıradaki doğrulama TFF/Transfermarkt eşleşmeyen yüksek kullanımlı oyuncu kuyruğudur."
    )

    summary = {
        "blueprint_candidate_links": len(blueprint_candidates),
        "low_confidence_blueprint_links": len(low_links),
        "low_confidence_unique_player_roles": len(low_queue),
        "missing_age_or_contract_links": missing_age_or_contract,
        "repeated_role_players": len(repeated_role_players),
        "position_matrix_candidates": len(position_candidates),
        "confidence_counts": dict(confidence_counts),
        "position_matrix_confidence_counts": dict(position_confidence),
        "next_priority": next_priority,
    }
    return {
        "summary": summary,
        "low_confidence_review_queue": low_queue[:120],
        "repeated_role_players": repeated_role_players[:80],
    }


def review_reason(item: dict) -> str:
    confidence = item.get("position_confidence")
    if confidence == "LOW_LEAGUE_PROXY":
        return "Rol maç yükü/gol/kart proxy'sinden türedi; doğrudan pozisyon doğrulaması yok."
    if confidence == "LOW_POSITION_UNVERIFIED":
        return "Oyuncu profili mevcut ancak role uygun pozisyon dış kaynakla eşleşmemiş; yayın önerisi olarak kullanılmaz."
    if confidence == "LOW_DERIVED":
        return "Pozisyon role yakın ama dış kaynak veya manuel pozisyon eşleşmesi eksik."
    if confidence in {None, "", "VERY_LOW"}:
        return "Adayın rol/pozisyon sinyali çok zayıf; otomatik scout listesinde alt sıraya alınmalı."
    return "Düşük güvenli aday."


def next_data_need(item: dict) -> str:
    needs = []
    if item.get("age") is None:
        needs.append("yaş")
    if item.get("contract_months_left") is None:
        needs.append("sözleşme")
    needs.extend(["pozisyon", "boy", "ayak"])
    return ", ".join(dict.fromkeys(needs))


def build_markdown(payload: dict) -> str:
    summary = payload["summary"]
    lines = [
        "# Scout Kalite ve Doğrulama Raporu",
        "",
        f"- Blueprint aday bağlantısı: {summary['blueprint_candidate_links']}",
        f"- Düşük güvenli blueprint bağlantısı: {summary['low_confidence_blueprint_links']}",
        f"- Tekil düşük güvenli oyuncu-rol: {summary['low_confidence_unique_player_roles']}",
        f"- Yaş/sözleşme eksiği olan bağlantı: {summary['missing_age_or_contract_links']}",
        f"- 3+ role yayılan oyuncu: {summary['repeated_role_players']}",
        f"- Pozisyon matrisi adayı: {summary['position_matrix_candidates']}",
        f"- Blueprint güven dağılımı: {summary['confidence_counts']}",
        f"- Pozisyon matrisi güven dağılımı: {summary['position_matrix_confidence_counts']}",
        f"- Sonraki öncelik: {summary['next_priority']}",
        "",
        "## Düşük Güven İnceleme Kuyruğu",
        "",
    ]
    for item in payload["low_confidence_review_queue"][:40]:
        lines.append(
            f"- {item.get('name')} ({item.get('team')}): takım={item.get('team')}, rol={item.get('role_label')}, "
            f"fit={item.get('fit_score')}, güven={item.get('position_confidence')}, etkilenen takım={item.get('affected_team_count')}, "
            f"ihtiyaç={item.get('next_data_need')}. "
            f"{item.get('review_reason')}"
        )
    lines.extend(["", "## Fazla Role Yayılan Oyuncular", ""])
    for item in payload["repeated_role_players"][:30]:
        lines.append(
            f"- {item.get('name')} ({item.get('team')}): {item.get('role_count')} rol={', '.join(item.get('roles', []))}. {item.get('action')}"
        )
    return "\n".join(lines)


def build_html(payload: dict) -> str:
    summary = payload["summary"]
    low_rows = "".join(low_queue_row(item) for item in payload["low_confidence_review_queue"][:80])
    repeated_rows = "".join(repeated_row(item) for item in payload["repeated_role_players"][:60])
    nav = _build_nav("Analiz")
    return f"""<!doctype html>
<html lang="tr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Scout Kalite ve Doğrulama Raporu — metric11</title>
  <meta name="theme-color" content="#091810">
  <link rel="icon" href="favicon.svg" type="image/svg+xml">
  <style>
    :root {{ --bg:#f4f6f8; --panel:#fff; --ink:#15181d; --muted:#667085; --line:#dce2ea; --dark:#091810; --red:#bf1f2f; --amber:#b76b00; --blue:#185ea8; --lime:#cde94e; --shadow:0 8px 22px rgba(18,24,32,.08); }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; font-family:Inter, system-ui, sans-serif; background:var(--bg); color:var(--ink); }}
    .topbar {{ position:sticky; top:0; z-index:5; display:flex; align-items:center; justify-content:space-between; gap:20px; min-height:58px; padding:0 clamp(16px,4vw,42px); background:var(--dark); color:white; border-bottom:2px solid #1a3023; }}
    .brand {{ display:flex; gap:10px; align-items:center; font-weight:800; font-size:18px; color:white; text-decoration:none; flex-shrink:0; letter-spacing:-0.2px; }}
    .brand:visited,.brand:active,.brand:hover {{ color:white; }}
    .brand-mark {{ width:28px; height:28px; display:grid; place-items:center; border-radius:6px; color:var(--dark); background:var(--lime); font-size:14px; font-weight:900; flex-shrink:0; }}
    .season {{ color:#6b7c72; font-size:11px; font-weight:500; margin-left:2px; border-left:1px solid #2a3d30; padding-left:8px; }}
    nav {{ display:flex; gap:2px; flex-wrap:nowrap; overflow-x:auto; justify-content:flex-end; scrollbar-width:none; }}
    nav::-webkit-scrollbar {{ display:none; }}
    nav a {{ color:#8fa89a; text-decoration:none; font-size:13px; font-weight:600; padding:8px 11px; border-radius:6px; white-space:nowrap; transition:background .15s,color .15s; }}
    nav a:visited {{ color:#8fa89a; }}
    nav a:hover {{ background:#162b20; color:white; }}
    nav a.active {{ background:#162b20; color:white; }}
    .page-header {{ background:#111318; color:white; padding:28px 42px; border-bottom:4px solid var(--amber); }}
    .back-link {{ display:inline-flex; align-items:center; gap:6px; color:#4ade80; text-decoration:none; font-size:13px; font-weight:600; margin-bottom:10px; }}
    .back-link::before {{ content:"←"; }}
    main {{ max-width:1420px; margin:0 auto; padding:24px; }}
    @media (max-width:680px) {{ .topbar {{ position:static; flex-direction:column; align-items:stretch; padding:11px 16px 0; gap:0; min-height:unset; }} .brand {{ padding-bottom:8px; }} .season {{ display:none; }} nav {{ justify-content:flex-start; border-top:1px solid #1e3228; padding:7px 0 9px; }} }}
    .metrics {{ display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin-bottom:18px; }}
    .metric, section {{ background:white; border:1px solid var(--line); border-radius:8px; box-shadow:var(--shadow); }}
    .metric {{ padding:15px; }}
    .metric span {{ display:block; color:var(--muted); font-size:12px; }}
    .metric strong {{ display:block; font-size:26px; margin-top:5px; }}
    section {{ padding:18px; margin-bottom:18px; overflow-x:auto; }}
    h2 {{ margin:0 0 14px; font-size:18px; }}
    table {{ width:100%; border-collapse:collapse; font-size:13px; min-width:850px; }}
    th,td {{ padding:9px 7px; border-bottom:1px solid var(--line); text-align:left; vertical-align:top; }}
    th {{ color:var(--muted); font-size:12px; }}
    .pill {{ display:inline-flex; min-height:23px; align-items:center; border-radius:999px; padding:0 8px; font-size:12px; border:1px solid #f2d09a; color:var(--amber); background:#fff7e8; }}
    @media (max-width:900px) {{ .metrics {{ grid-template-columns:1fr 1fr; }} main {{ padding:14px; }} header {{ padding:22px; }} }}
    @media (max-width:620px) {{ .metrics {{ grid-template-columns:1fr; }} }}
  </style>
</head>
<body>
  {nav}
  <div class="page-header">
    <a class="back-link" href="/">Ana sayfaya dön</a>
    <h1>Scout Kalite ve Doğrulama Raporu</h1>
    <p>Scout adaylarının pozisyon güvenini, eksik profil alanlarını ve fazla role yayılan oyuncuları görünür yapar. Bu rapor doğrudan veri toplama önceliğidir.</p>
  </div>
  <main>
    <div class="metrics">
      {metric("Blueprint bağlantı", summary["blueprint_candidate_links"])}
      {metric("Düşük güven", summary["low_confidence_blueprint_links"])}
      {metric("Tekil kontrol", summary["low_confidence_unique_player_roles"])}
      {metric("3+ rol yayılımı", summary["repeated_role_players"])}
    </div>
    <section><h2>Düşük Güven İnceleme Kuyruğu</h2><table><thead><tr><th>Oyuncu</th><th>Takım</th><th>Rol</th><th>Fit</th><th>Güven</th><th>Etkilenen</th><th>Gerekçe</th><th>Gerekli Veri</th></tr></thead><tbody>{low_rows}</tbody></table></section>
    <section><h2>Fazla Role Yayılan Oyuncular</h2><table><thead><tr><th>Oyuncu</th><th>Takım</th><th>Rol Sayısı</th><th>Roller</th><th>Aksiyon</th></tr></thead><tbody>{repeated_rows}</tbody></table></section>
  </main>
  <script defer src="/_vercel/insights/script.js"></script>
</body>
</html>
"""


def metric(label: str, value) -> str:
    return f'<div class="metric"><span>{escape(str(label))}</span><strong>{escape(str(value))}</strong></div>'


def low_queue_row(item: dict) -> str:
    return (
        f"<tr><td>{escape(item.get('name') or '')}</td><td>{escape(item.get('team') or '')}</td>"
        f"<td>{escape(item.get('role_label') or '')}</td><td>{escape(str(item.get('fit_score') or ''))}</td>"
        f"<td><span class=\"pill\">{escape(str(item.get('position_confidence') or 'EMPTY'))}</span></td>"
        f"<td>{escape(str(item.get('affected_team_count') or 1))}</td>"
        f"<td>{escape(item.get('review_reason') or '')}</td><td>{escape(item.get('next_data_need') or '')}</td></tr>"
    )


def repeated_row(item: dict) -> str:
    return (
        f"<tr><td>{escape(item.get('name') or '')}</td><td>{escape(item.get('team') or '')}</td>"
        f"<td>{item.get('role_count')}</td><td>{escape(', '.join(item.get('roles', [])))}</td>"
        f"<td>{escape(item.get('action') or '')}</td></tr>"
    )


if __name__ == "__main__":
    main()
