"""Transfer sezonu bağlam raporu: sözleşme biten oyuncular, yükselen takımlar, transfer sinyalleri."""
from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from src.config import PROCESSED_DIR, SEASON, SEASON_LABEL

# --------------------------------------------------------------------------- #
# constants
# --------------------------------------------------------------------------- #
OUTPUT_HTML = PROCESSED_DIR / f"transfer_season_context_{SEASON}.html"
OUTPUT_JSON = PROCESSED_DIR / f"transfer_season_context_{SEASON}.json"

PROMOTED_TEAMS = ["ÇORUMSPOR", "ADANASPOR", "SAKARYASPOR", "BODRUMSPOR"]
RELEGATED_MARKERS = ["ANKARAGÜCÜ", "ALANYASPOR", "HATAYSPOR", "PENDIKSPOR", "SİVASSPOR"]

POSITION_LABELS = {"GK": "Kaleci", "DEF": "Defans", "MID": "Orta Saha", "FWD": "Forvet"}

SUMMER_CUTOFF = "2026-06"
FINAL_YEAR_CUTOFF = "2027-12"

WINDOW_OPEN = "1 Haziran 2026"
WINDOW_CLOSE = "31 Ağustos 2026"


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def _load_json(path: Path) -> dict | list | None:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return None


def _title(name: str) -> str:
    lowered = name.replace("İ", "i").replace("I", "ı").lower()
    return " ".join(word.capitalize() for word in lowered.split())


def _mv_str(eur: int | None) -> str:
    if not eur:
        return "—"
    if eur >= 1_000_000:
        return f"€{eur / 1_000_000:.1f}M"
    return f"€{eur // 1000}K"


def _pos_badge(pos: str | None) -> str:
    label = POSITION_LABELS.get(pos or "", pos or "?")
    colors = {"GK": "#f59e0b", "DEF": "#3b82f6", "MID": "#10b981", "FWD": "#ef4444"}
    color = colors.get(pos or "", "#6b7280")
    return f"<span style='background:{color};color:#fff;border-radius:4px;padding:1px 7px;font-size:11px;font-weight:600'>{label}</span>"


# --------------------------------------------------------------------------- #
# data loading & analysis
# --------------------------------------------------------------------------- #
def _load_players() -> list[dict]:
    data = _load_json(PROCESSED_DIR / f"tff_player_profiles_enriched_{SEASON}.json")
    if data is None:
        data = _load_json(PROCESSED_DIR / f"tff_player_profiles_all_priority_{SEASON}.json") or []
    return data if isinstance(data, list) else data.get("players", [])


def _categorize_players(players: list[dict]) -> dict:
    """Sort players into free agents, final year, multi-year by contract end."""
    free_agents = []
    final_year = []
    by_team: dict[str, list] = defaultdict(list)

    for p in players:
        end = str(p.get("contract_end") or "")
        if not end or end[:4] < "2020":
            continue
        name = _title(p.get("name", "?"))
        team_raw = p.get("tm_team_name") or p.get("club") or "?"
        team = _title(team_raw)
        age = p.get("age")
        pos_group = p.get("tm_position_group") or p.get("position_group")
        mv = p.get("tm_market_value_eur")
        entry = {
            "name": name,
            "name_raw": p.get("name", ""),
            "team": team,
            "age": age,
            "position_group": pos_group,
            "market_value_eur": mv,
            "market_value_text": p.get("tm_market_value_text") or _mv_str(mv),
            "contract_end": end,
            "tm_profile_url": p.get("tm_profile_url"),
        }
        if end[:7] <= SUMMER_CUTOFF:
            free_agents.append(entry)
        elif end[:7] <= FINAL_YEAR_CUTOFF:
            final_year.append(entry)

        by_team[team].append(entry)

    free_agents.sort(key=lambda x: x.get("market_value_eur") or 0, reverse=True)
    final_year.sort(key=lambda x: x.get("market_value_eur") or 0, reverse=True)

    return {"free_agents": free_agents, "final_year": final_year, "by_team": dict(by_team)}


def _team_free_agent_summary(free_agents: list[dict]) -> dict[str, list]:
    by_team: dict[str, list] = defaultdict(list)
    for p in free_agents:
        by_team[p["team"]].append(p)
    return dict(sorted(by_team.items(), key=lambda kv: sum(p.get("market_value_eur") or 0 for p in kv[1]), reverse=True))


def _load_intel() -> dict | None:
    return _load_json(PROCESSED_DIR / f"news_intelligence_{SEASON}.json")  # type: ignore[return-value]


def _extract_transfer_signals(intel: dict | None) -> list[dict]:
    if not intel:
        return []
    return intel.get("transfers", intel.get("transfer_rumors", []))


def _extract_promotions(intel: dict | None) -> list[dict]:
    if not intel:
        return []
    return intel.get("promotions", [])


# --------------------------------------------------------------------------- #
# HTML sections
# --------------------------------------------------------------------------- #
def _header_section() -> str:
    now = datetime.now(timezone.utc).strftime("%d.%m.%Y %H:%M")
    return f"""
<div style='background:linear-gradient(135deg,#1e3a5f,#0f172a);border-radius:12px;padding:24px 32px;margin-bottom:24px;'>
  <h1 style='color:#f1f5f9;margin:0 0 8px 0;font-size:24px;'>Transfer Sezonu Bağlam Raporu</h1>
  <p style='color:#94a3b8;margin:0;font-size:13px;'>{SEASON_LABEL} · Yaz Penceresi: {WINDOW_OPEN} – {WINDOW_CLOSE} · Güncelleme: {now}</p>
</div>
"""


def _summary_bar(free_agents: list, final_year: list, signals: list, promotions: list) -> str:
    total_mv = sum(p.get("market_value_eur") or 0 for p in free_agents)
    mv_label = f"€{total_mv / 1_000_000:.0f}M" if total_mv >= 1_000_000 else "—"
    pills = [
        ("🔓", len(free_agents), "Serbest Kalacak", "#ef4444"),
        ("⏳", len(final_year), "Son Yıl Kontrat", "#f59e0b"),
        ("📡", len(signals), "Haber İddiası", "#3b82f6"),
        ("⬆", len(promotions), "Lig Hareketi", "#a78bfa"),
        ("💰", mv_label, "Toplam Değer", "#10b981"),
    ]
    cells = "".join(
        f"""<div style='background:#1e293b;border-radius:10px;padding:14px 20px;text-align:center;min-width:120px;flex:1'>
  <div style='font-size:20px;font-weight:700;color:{c}'>{v}</div>
  <div style='font-size:11px;color:#94a3b8;margin-top:2px'>{lbl}</div>
</div>"""
        for icon, v, lbl, c in pills
    )
    return f"<div style='display:flex;gap:12px;flex-wrap:wrap;margin-bottom:24px'>{cells}</div>"


def _section_title(title: str, subtitle: str = "") -> str:
    sub = f"<span style='font-size:13px;color:#94a3b8;margin-left:10px;font-weight:400'>{subtitle}</span>" if subtitle else ""
    return f"<h2 style='color:#e2e8f0;font-size:18px;border-bottom:1px solid #334155;padding-bottom:8px;margin:28px 0 16px'>{title}{sub}</h2>"


def _player_row(p: dict, rank: int | None = None) -> str:
    mv = _mv_str(p.get("market_value_eur"))
    pos = _pos_badge(p.get("position_group"))
    age = p.get("age") or "?"
    name = p["name"]
    url = p.get("tm_profile_url")
    name_html = f"<a href='{url}' target='_blank' style='color:#60a5fa;text-decoration:none'>{name}</a>" if url else name
    rank_html = f"<td style='color:#64748b;width:28px'>{rank}.</td>" if rank is not None else ""
    contract = p.get("contract_end", "")[:10]
    contract_color = "#ef4444" if contract[:7] <= SUMMER_CUTOFF else "#f59e0b"
    return f"""<tr style='border-bottom:1px solid #1e293b'>
  {rank_html}
  <td style='padding:8px 4px;color:#e2e8f0'>{name_html}</td>
  <td style='padding:8px 4px;color:#94a3b8;font-size:12px'>{p['team']}</td>
  <td style='padding:8px 4px'>{pos}</td>
  <td style='padding:8px 4px;color:#64748b;font-size:12px'>{age}</td>
  <td style='padding:8px 4px;color:#fbbf24;font-weight:600;font-size:13px'>{mv}</td>
  <td style='padding:8px 4px;color:{contract_color};font-size:12px'>{contract}</td>
</tr>"""


def _player_table(players: list[dict], limit: int = 30, show_rank: bool = True) -> str:
    rows = "".join(_player_row(p, i + 1 if show_rank else None) for i, p in enumerate(players[:limit]))
    rank_th = "<th style='width:28px'>#</th>" if show_rank else ""
    return f"""<table style='width:100%;border-collapse:collapse;font-size:13px'>
<thead><tr style='color:#94a3b8;font-size:11px;text-transform:uppercase;letter-spacing:.5px;border-bottom:1px solid #334155'>
  {rank_th}<th style='padding:6px 4px;text-align:left'>Oyuncu</th><th style='text-align:left'>Takım</th>
  <th style='text-align:left'>Pozisyon</th><th style='text-align:left'>Yaş</th>
  <th style='text-align:left'>Piyasa Değeri</th><th style='text-align:left'>Kontrat Bitiş</th>
</tr></thead>
<tbody>{rows}</tbody>
</table>"""


def _free_agents_section(free_agents: list[dict]) -> str:
    explanation = """
<div style='background:#1e293b;border-left:3px solid #ef4444;border-radius:6px;padding:12px 16px;margin-bottom:16px;font-size:13px;color:#94a3b8'>
  Kontratı 2026 yaz penceresi kapanmadan biten oyuncular. Takımları yenileme teklifini kabul etmezse yaz transferinde
  serbest kalacaklar. Yüksek değerli oyuncular için ocak penceresinde satış riski de söz konusu.
</div>"""
    by_team = _team_free_agent_summary(free_agents)
    team_blocks = ""
    for team, players in list(by_team.items())[:6]:
        total = sum(p.get("market_value_eur") or 0 for p in players)
        team_blocks += f"""
<div style='background:#1e293b;border-radius:8px;padding:12px 16px;flex:1;min-width:220px'>
  <div style='color:#e2e8f0;font-weight:600;font-size:13px;margin-bottom:6px'>{team}</div>
  <div style='color:#ef4444;font-size:12px;margin-bottom:8px'>{len(players)} oyuncu · {_mv_str(total)}</div>
  {"".join(f"<div style='color:#94a3b8;font-size:12px;padding:2px 0'>{p['name']} <span style='color:#fbbf24'>{_mv_str(p.get('market_value_eur'))}</span></div>" for p in players[:5])}
</div>"""

    return (
        _section_title("🔓 Serbest Kalacak Oyuncular", f"Yaz 2026 – {len(free_agents)} oyuncu")
        + explanation
        + f"<div style='display:flex;gap:12px;flex-wrap:wrap;margin-bottom:20px'>{team_blocks}</div>"
        + _player_table(free_agents, limit=25)
    )


def _final_year_section(final_year: list[dict]) -> str:
    explanation = """
<div style='background:#1e293b;border-left:3px solid #f59e0b;border-radius:6px;padding:12px 16px;margin-bottom:16px;font-size:13px;color:#94a3b8'>
  2026 yaz penceresi sonrasında son kontrat yılına girecek oyuncular. Bu sezon satılmazlarsa 2027 yazında
  serbest kalacaklar. Kulüpler genellikle son yılda değer kaybı yaşamamak için satmayı tercih eder.
</div>"""
    return (
        _section_title("⏳ Son Yıl Kontratı", f"2027 sonu – {len(final_year)} oyuncu")
        + explanation
        + _player_table(final_year, limit=30)
    )


def _signals_section(signals: list[dict]) -> str:
    if not signals:
        return _section_title("📡 Transfer Sinyalleri", "haber verisi yok") + "<p style='color:#64748b'>Henüz transfer haberi tespit edilmedi.</p>"

    cards = ""
    for s in signals[:20]:
        player = _title(s.get("player_name") or "?")
        from_club = _title(s.get("from_club") or "?")
        to_club = _title(s.get("to_club") or "?")
        mv = s.get("tm_market_value_eur") or s.get("market_value_eur")
        mv_html = f"      <span style='color:#fbbf24;font-weight:600'>{_mv_str(mv)}</span>\n" if mv else ""
        status = s.get("verification_status", "REVIEW_REQUIRED")
        status_label = {
            "OFFICIAL": "RESMİ",
            "CORROBORATED": "ÇOKLU KAYNAK",
            "RUMOR": "SÖYLENTİ",
            "REVIEW_REQUIRED": "İNCELE",
        }.get(status, status)
        conf_color = {
            "OFFICIAL": "#10b981",
            "CORROBORATED": "#f59e0b",
            "RUMOR": "#3b82f6",
            "REVIEW_REQUIRED": "#6b7280",
        }.get(status, "#6b7280")
        sources = s.get("sources") or []
        source_count = s.get("source_count", len(sources))
        source_text = ", ".join(sources[:3]) if sources else s.get("source", "?")
        window = s.get("window") or "?"
        interpretation = s.get("interpretation", "")
        cards += f"""
<div style='background:#1e293b;border-radius:8px;padding:14px 16px;margin-bottom:10px;border-left:3px solid {conf_color}'>
  <div style='display:flex;justify-content:space-between;align-items:flex-start'>
    <div>
      <span style='color:#e2e8f0;font-weight:600;font-size:14px'>{player}</span>
{mv_html}    </div>
    <span style='background:{conf_color}22;color:{conf_color};border-radius:4px;padding:2px 8px;font-size:11px;font-weight:600'>{status_label}</span>
  </div>
  <div style='color:#94a3b8;font-size:12px;margin-top:6px'>
    <span style='color:#64748b'>{from_club}</span>
    <span style='color:#60a5fa;margin:0 6px'>→</span>
    <span style='color:#60a5fa'>{to_club}</span>
    <span style='color:#475569;margin-left:10px'>· Pencere: {window}</span>
    <span style='color:#475569;margin-left:10px'>· {source_count} kaynak</span>
  </div>
  <div style='color:#94a3b8;font-size:12px;margin-top:7px'>{interpretation}</div>
  <div style='color:#64748b;font-size:11px;margin-top:5px'>Kaynak: {source_text}</div>
</div>"""

    note = "<p style='color:#94a3b8;font-size:12px;margin:-8px 0 14px'>Haber iddiaları scout öneri skorunu veya maç modelini resmi teyit olmadan değiştirmez.</p>"
    return _section_title("📡 Transfer Haber İddiaları", f"{len(signals)} izlenen kayıt") + note + cards


def _promotions_section(promotions: list[dict]) -> str:
    context_box = """
<div style='background:#1e293b;border-left:3px solid #a78bfa;border-radius:6px;padding:12px 16px;margin-bottom:16px;font-size:13px;color:#94a3b8'>
  <strong style='color:#a78bfa'>Transfer Sezonu Etkisi:</strong>
  Süper Lig'e yeni çıkan takımlar oyuncu takviyesi yapması, düşen takımlar ise yüksek maaşlı oyuncuları
  satması gerekiyor. Yeni takımların ihtiyaçları piyasada ek talep oluşturuyor.
</div>"""

    need_cards = ""
    for team_name in PROMOTED_TEAMS:
        need_cards += f"""
<div style='background:#1e293b;border-radius:8px;padding:14px 16px;flex:1;min-width:200px;border-top:3px solid #10b981'>
  <div style='color:#10b981;font-size:11px;font-weight:600;letter-spacing:.5px'>⬆ YENİ TAKIM</div>
  <div style='color:#e2e8f0;font-weight:600;margin:6px 0 8px;font-size:14px'>{team_name.capitalize()}</div>
  <div style='color:#94a3b8;font-size:12px;line-height:1.6'>
    <div>• Süper Lig deneyimli oyuncu ihtiyacı</div>
    <div>• Bütçe kısıtlı → serbest ajan ve kiralık</div>
    <div>• Düşen takımların oyuncuları hedef</div>
  </div>
</div>"""

    news_items = ""
    if promotions:
        for promo in promotions[:8]:
            text = promo.get("title") or promo.get("text") or ""
            source = promo.get("source", "")
            news_items += f"""<div style='background:#1e293b;border-radius:6px;padding:10px 14px;margin-bottom:8px;font-size:13px;color:#c4b5fd'>
  {text}
  <span style='color:#475569;font-size:11px;margin-left:8px'>{source}</span>
</div>"""

    news_block = (
        f"<h3 style='color:#a78bfa;font-size:14px;margin:16px 0 8px'>Son Haberler</h3>{news_items}" if news_items else ""
    )

    return (
        _section_title("⬆ Lig Hareketleri & Etkileri")
        + context_box
        + f"<div style='display:flex;gap:12px;flex-wrap:wrap;margin-bottom:20px'>{need_cards}</div>"
        + news_block
    )


def _window_timeline_section() -> str:
    milestones = [
        ("1 Haziran", "Yaz transfer penceresi açılıyor", "#10b981"),
        ("30 Haziran", "Sözleşmesi bitenler resmen serbest kalıyor", "#ef4444"),
        ("1 Temmuz", "Yeni sezon hazırlık kampları başlıyor", "#3b82f6"),
        ("31 Ağustos", "Yaz transfer penceresi kapanıyor", "#f59e0b"),
        ("1 Ocak 2027", "Kış transfer penceresi açılacak", "#64748b"),
    ]
    items = "".join(
        f"""<div style='display:flex;align-items:flex-start;gap:12px;margin-bottom:12px'>
  <div style='width:10px;height:10px;border-radius:50%;background:{c};flex-shrink:0;margin-top:3px'></div>
  <div><span style='color:#e2e8f0;font-size:13px;font-weight:600'>{date}</span>
  <span style='color:#94a3b8;font-size:13px;margin-left:8px'>{desc}</span></div>
</div>"""
        for date, desc, c in milestones
    )
    return (
        _section_title("📅 Transfer Takvimi 2026")
        + f"<div style='background:#1e293b;border-radius:8px;padding:16px 20px'>{items}</div>"
    )


# --------------------------------------------------------------------------- #
# JSON output
# --------------------------------------------------------------------------- #
def _build_json_payload(free_agents: list, final_year: list, signals: list, promotions: list) -> dict:
    status_counts = {
        status: sum(1 for row in signals if row.get("verification_status") == status)
        for status in ("OFFICIAL", "CORROBORATED", "RUMOR", "REVIEW_REQUIRED")
    }
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "season": SEASON,
        "summary": {
            "free_agents_count": len(free_agents),
            "final_year_count": len(final_year),
            "transfer_signals_count": len(signals),
            "transfer_status_counts": status_counts,
            "promotion_events_count": len(promotions),
            "free_agent_total_market_value_eur": sum(p.get("market_value_eur") or 0 for p in free_agents),
        },
        "free_agents_top20": free_agents[:20],
        "final_year_top20": final_year[:20],
        "transfer_signals": signals,
        "league_movements": {"promoted": PROMOTED_TEAMS, "relegated_watch": RELEGATED_MARKERS},
    }


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #
def main() -> None:
    players = _load_players()
    categorized = _categorize_players(players)
    free_agents = categorized["free_agents"]
    final_year = categorized["final_year"]

    intel = _load_intel()
    signals = _extract_transfer_signals(intel)
    promotions = _extract_promotions(intel)

    html_parts = [
        "<!DOCTYPE html><html lang='tr'><head><meta charset='utf-8'>",
        f"<title>Transfer Sezonu Bağlam – {SEASON_LABEL}</title>",
        "<style>*{box-sizing:border-box}body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;",
        "background:#0f172a;color:#e2e8f0;margin:0;padding:20px}",
        "a{color:#60a5fa}table td,table th{padding:8px 4px;text-align:left}",
        "tr:hover{background:#1e293b22}</style>",
        "</head><body><div style='max-width:1100px;margin:0 auto'>",
        _header_section(),
        _summary_bar(free_agents, final_year, signals, promotions),
        _window_timeline_section(),
        _free_agents_section(free_agents),
        _final_year_section(final_year),
        _signals_section(signals),
        _promotions_section(promotions),
        "</div>
  <script defer src="/_vercel/insights/script.js"></script>
</body></html>",
    ]

    OUTPUT_HTML.write_text("".join(html_parts), encoding="utf-8")

    payload = _build_json_payload(free_agents, final_year, signals, promotions)
    OUTPUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Free agents (2026): {len(free_agents)}")
    print(f"Final year (2027):  {len(final_year)}")
    print(f"Transfer signals:   {len(signals)}")
    print(f"HTML: {OUTPUT_HTML}")
    print(f"JSON: {OUTPUT_JSON}")


if __name__ == "__main__":
    main()
