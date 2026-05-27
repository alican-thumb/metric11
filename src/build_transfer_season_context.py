"""Transfer sezonu bağlam raporu: sözleşme biten oyuncular, yükselen takımlar, transfer sinyalleri."""
from __future__ import annotations

import json
from collections import defaultdict
from datetime import date, datetime, timezone
from pathlib import Path

from src.config import PROCESSED_DIR, SEASON, TRANSFER_WATCH_SEASON_LABEL

# --------------------------------------------------------------------------- #
# constants
# --------------------------------------------------------------------------- #
OUTPUT_HTML = PROCESSED_DIR / f"transfer_season_context_{SEASON}.html"
OUTPUT_JSON = PROCESSED_DIR / f"transfer_season_context_{SEASON}.json"

PROMOTED_TEAMS = ["ÇORUM FK", "ERZURUMSPOR FK", "AMED SFK"]
RELEGATED_MARKERS = ["FATİH KARAGÜMRÜK", "ANTALYASPOR", "KAYSERİSPOR"]

POSITION_LABELS = {"GK": "Kaleci", "DEF": "Defans", "MID": "Orta Saha", "FWD": "Forvet"}

SUMMER_CUTOFF = "2026-06"
FINAL_YEAR_CUTOFF = "2027-12"

WINDOW_OPEN = "1 Haziran 2026"
WINDOW_CLOSE = "31 Ağustos 2026"
SEASON_END_DATE = date(2026, 5, 18)
WINDOW_OPEN_DATE = date(2026, 6, 1)
WINDOW_CLOSE_DATE = date(2026, 9, 1)


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
        return "&mdash;"
    if eur >= 1_000_000:
        return f"€{eur / 1_000_000:.1f}M"
    return f"€{eur // 1000}K"


def _pos_badge(pos: str | None) -> str:
    label = POSITION_LABELS.get(pos or "", pos or "?")
    colors = {"GK": "#d97706", "DEF": "#116447", "MID": "#0d9488", "FWD": "#ef4444"}
    color = colors.get(pos or "", "#627067")
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
<div style='background:#091810;border-radius:12px;padding:24px 32px;margin-bottom:24px;'>
  <h1 style='color:#fff;margin:0 0 8px 0;font-size:24px;'>Transfer Sezonu Bağlam Raporu</h1>
  <p style='color:#8fa89a;margin:0;font-size:13px;'>{TRANSFER_WATCH_SEASON_LABEL} · Yaz Penceresi: {WINDOW_OPEN} – {WINDOW_CLOSE} · Güncelleme: {now}</p>
</div>
"""


def _summary_bar(free_agents: list, final_year: list, signals: list, promotions: list) -> str:
    total_mv = sum(p.get("market_value_eur") or 0 for p in free_agents)
    mv_label = f"€{total_mv / 1_000_000:.0f}M" if total_mv >= 1_000_000 else "&mdash;"
    pills = [
        ("🔓", len(free_agents), "Serbest Kalacak", "#ef4444"),
        ("⏳", len(final_year), "Son Yıl Kontrat", "#d97706"),
        ("📡", len(signals), "Haber İddiası", "#116447"),
        ("⬆", len(promotions), "Lig Hareketi", "#0d9488"),
        ("💰", mv_label, "Toplam Değer", "#116447"),
    ]
    cells = "".join(
        f"""<div style='background:#0f2018;border-radius:10px;padding:14px 20px;text-align:center;min-width:120px;flex:1'>
  <div style='font-size:20px;font-weight:700;color:{c}'>{v}</div>
  <div style='font-size:11px;color:#8fa89a;margin-top:2px'>{lbl}</div>
</div>"""
        for icon, v, lbl, c in pills
    )
    return f"<div style='display:flex;gap:12px;flex-wrap:wrap;margin-bottom:24px'>{cells}</div>"


def _countdown_banner() -> str:
    today = date.today()
    if SEASON_END_DATE <= today < WINDOW_OPEN_DATE:
        days = (WINDOW_OPEN_DATE - today).days
        label = f"{days} gün" if days > 1 else "Yarın"
        msg = f"<strong style='color:#cde94e'>{label}</strong> içinde açılıyor"
        bg, border = "#0d2b1a", "#cde94e"
        icon = "⏰"
    elif today <= WINDOW_CLOSE_DATE:
        days = (WINDOW_CLOSE_DATE - today).days
        msg = f"<strong style='color:#116447'>Transfer penceresi açık</strong> · <span style='color:#627067'>{days} gün kaldı</span>"
        bg, border = "#0d2b1a", "#10b981"
        icon = "✅"
    else:
        msg = "<strong style='color:#627067'>Transfer penceresi kapandı</strong>"
        bg, border = "#e8eee9", "#c4cfc7"
        icon = "🔒"
    return (
        f"<div style='background:{bg};border:1px solid {border};border-radius:10px;"
        f"padding:14px 20px;margin-bottom:20px;display:flex;align-items:center;gap:12px;font-size:14px'>"
        f"<span style='font-size:20px'>{icon}</span>"
        f"<div>{msg} · <span style='color:#627067;font-size:13px'>Pencere: {WINDOW_OPEN} – {WINDOW_CLOSE}</span></div>"
        f"</div>"
    )


def _position_breakdown_section(free_agents: list[dict]) -> str:
    groups: dict[str, list] = {"GK": [], "DEF": [], "MID": [], "FWD": []}
    for p in free_agents:
        g = p.get("position_group") or ""
        if g in groups:
            groups[g].append(p)

    cols = ""
    for pos, players in groups.items():
        label = POSITION_LABELS[pos]
        colors = {"GK": "#d97706", "DEF": "#116447", "MID": "#0d9488", "FWD": "#ef4444"}
        color = colors[pos]
        rows = ""
        for p in players[:6]:
            mv = _mv_str(p.get("market_value_eur"))
            age = p.get("age") or "?"
            url = p.get("tm_profile_url")
            name = p["name"]
            name_html = f"<a href='{url}' target='_blank' style='color:#116447;text-decoration:none'>{name}</a>" if url else name
            rows += (
                f"<div style='display:flex;justify-content:space-between;align-items:center;"
                f"padding:6px 0;border-bottom:1px solid #d7ded9;font-size:12px'>"
                f"<div style='color:#132018'>{name_html}"
                f"<span style='color:#627067;font-size:11px;margin-left:6px'>{age}</span></div>"
                f"<div style='color:#116447;font-weight:600;white-space:nowrap'>{mv}</div>"
                f"</div>"
            )
        total_mv = sum(p.get("market_value_eur") or 0 for p in players)
        cols += (
            f"<div style='background:#fff;border:1px solid #d7ded9;border-radius:10px;padding:16px;flex:1;min-width:200px;border-top:3px solid {color}'>"
            f"<div style='color:{color};font-size:11px;font-weight:700;letter-spacing:.5px;margin-bottom:4px'>{label.upper()}</div>"
            f"<div style='display:flex;justify-content:space-between;margin-bottom:12px'>"
            f"<span style='color:#132018;font-size:20px;font-weight:700'>{len(players)}</span>"
            f"<span style='color:#627067;font-size:12px;align-self:flex-end'>{_mv_str(total_mv)}</span>"
            f"</div>"
            f"{rows}"
            f"</div>"
        )
    return (
        _section_title("📊 Pozisyon Bazlı Özet", "Serbest kalacak oyuncular — pozisyona göre")
        + f"<div style='display:flex;gap:12px;flex-wrap:wrap;margin-bottom:24px'>{cols}</div>"
    )


def _section_title(title: str, subtitle: str = "") -> str:
    sub = f"<span style='font-size:13px;color:#627067;margin-left:10px;font-weight:400'>{subtitle}</span>" if subtitle else ""
    return f"<h2 style='color:#132018;font-size:18px;border-bottom:1px solid #d7ded9;padding-bottom:8px;margin:28px 0 16px'>{title}{sub}</h2>"


def _player_row(p: dict, rank: int | None = None) -> str:
    mv = _mv_str(p.get("market_value_eur"))
    pos = _pos_badge(p.get("position_group"))
    age = p.get("age") or "?"
    name = p["name"]
    url = p.get("tm_profile_url")
    name_html = f"<a href='{url}' target='_blank' style='color:#116447;text-decoration:none'>{name}</a>" if url else name
    rank_html = f"<td style='color:#627067;width:28px'>{rank}.</td>" if rank is not None else ""
    contract = p.get("contract_end", "")[:10]
    contract_color = "#ef4444" if contract[:7] <= SUMMER_CUTOFF else "#d97706"
    return f"""<tr style='border-bottom:1px solid #d7ded9'>
  {rank_html}
  <td style='padding:8px 4px;color:#132018'>{name_html}</td>
  <td style='padding:8px 4px;color:#627067;font-size:12px'>{p['team']}</td>
  <td style='padding:8px 4px'>{pos}</td>
  <td style='padding:8px 4px;color:#627067;font-size:12px'>{age}</td>
  <td style='padding:8px 4px;color:#116447;font-weight:600;font-size:13px'>{mv}</td>
  <td style='padding:8px 4px;color:{contract_color};font-size:12px'>{contract}</td>
</tr>"""


def _player_table(players: list[dict], limit: int = 30, show_rank: bool = True) -> str:
    rows = "".join(_player_row(p, i + 1 if show_rank else None) for i, p in enumerate(players[:limit]))
    rank_th = "<th style='width:28px'>#</th>" if show_rank else ""
    return f"""<table style='width:100%;border-collapse:collapse;font-size:13px;background:#fff;border-radius:8px;border:1px solid #d7ded9;overflow:hidden'>
<thead><tr style='color:#627067;font-size:11px;text-transform:uppercase;letter-spacing:.5px;border-bottom:1px solid #d7ded9;background:#eef2ef'>
  {rank_th}<th style='padding:8px 6px;text-align:left'>Oyuncu</th><th style='text-align:left'>Takım</th>
  <th style='text-align:left'>Pozisyon</th><th style='text-align:left'>Yaş</th>
  <th style='text-align:left'>Piyasa Değeri</th><th style='text-align:left'>Kontrat Bitiş</th>
</tr></thead>
<tbody>{rows}</tbody>
</table>"""


def _free_agents_section(free_agents: list[dict]) -> str:
    explanation = """
<div style='background:#fef2f2;border-left:3px solid #ef4444;border-radius:6px;padding:12px 16px;margin-bottom:16px;font-size:13px;color:#627067'>
  Kontratı 2026 yaz penceresi kapanmadan biten oyuncular. Takımları yenileme teklifini kabul etmezse yaz transferinde
  serbest kalacaklar. Yüksek değerli oyuncular için ocak penceresinde satış riski de söz konusu.
</div>"""
    by_team = _team_free_agent_summary(free_agents)
    team_blocks = ""
    for team, players in list(by_team.items())[:6]:
        total = sum(p.get("market_value_eur") or 0 for p in players)
        team_blocks += f"""
<div style='background:#fff;border:1px solid #d7ded9;border-radius:8px;padding:12px 16px;flex:1;min-width:220px'>
  <div style='color:#132018;font-weight:600;font-size:13px;margin-bottom:6px'>{team}</div>
  <div style='color:#ef4444;font-size:12px;margin-bottom:8px'>{len(players)} oyuncu · {_mv_str(total)}</div>
  {"".join(f"<div style='color:#627067;font-size:12px;padding:2px 0'>{p['name']} <span style='color:#116447;font-weight:600'>{_mv_str(p.get('market_value_eur'))}</span></div>" for p in players[:5])}
</div>"""

    return (
        _section_title("🔓 Serbest Kalacak Oyuncular", f"Yaz 2026 – {len(free_agents)} oyuncu")
        + explanation
        + f"<div style='display:flex;gap:12px;flex-wrap:wrap;margin-bottom:20px'>{team_blocks}</div>"
        + _player_table(free_agents, limit=25)
    )


def _final_year_section(final_year: list[dict]) -> str:
    explanation = """
<div style='background:#fffbeb;border-left:3px solid #d97706;border-radius:6px;padding:12px 16px;margin-bottom:16px;font-size:13px;color:#627067'>
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
        return _section_title("📡 Transfer Sinyalleri", "haber verisi yok") + "<p style='color:#627067'>Henüz transfer haberi tespit edilmedi.</p>"

    cards = ""
    for s in signals[:20]:
        player = _title(s.get("player_name") or "?")
        from_club = _title(s.get("from_club") or "?")
        to_club = _title(s.get("to_club") or "?")
        mv = s.get("tm_market_value_eur") or s.get("market_value_eur")
        mv_html = f"      <span style='color:#116447;font-weight:600'>{_mv_str(mv)}</span>\n" if mv else ""
        status = s.get("verification_status", "REVIEW_REQUIRED")
        status_label = {
            "OFFICIAL": "RESMİ",
            "CORROBORATED": "ÇOKLU KAYNAK",
            "RUMOR": "SÖYLENTİ",
            "REVIEW_REQUIRED": "İNCELE",
        }.get(status, status)
        conf_color = {
            "OFFICIAL": "#116447",
            "CORROBORATED": "#d97706",
            "RUMOR": "#8fa89a",
            "REVIEW_REQUIRED": "#627067",
        }.get(status, "#627067")
        sources = s.get("sources") or []
        source_count = s.get("source_count", len(sources))
        source_text = ", ".join(sources[:3]) if sources else s.get("source", "?")
        window = s.get("window") or "?"
        interpretation = s.get("interpretation", "")
        cards += f"""
<div style='background:#fff;border:1px solid #d7ded9;border-radius:8px;padding:14px 16px;margin-bottom:10px;border-left:3px solid {conf_color}'>
  <div style='display:flex;justify-content:space-between;align-items:flex-start'>
    <div>
      <span style='color:#132018;font-weight:600;font-size:14px'>{player}</span>
{mv_html}    </div>
    <span style='background:{conf_color}22;color:{conf_color};border-radius:4px;padding:2px 8px;font-size:11px;font-weight:600'>{status_label}</span>
  </div>
  <div style='color:#627067;font-size:12px;margin-top:6px'>
    <span style='color:#627067'>{from_club}</span>
    <span style='color:#116447;margin:0 6px'>→</span>
    <span style='color:#116447'>{to_club}</span>
    <span style='color:#8fa89a;margin-left:10px'>· Pencere: {window}</span>
    <span style='color:#8fa89a;margin-left:10px'>· {source_count} kaynak</span>
  </div>
  <div style='color:#627067;font-size:12px;margin-top:7px'>{interpretation}</div>
  <div style='color:#8fa89a;font-size:11px;margin-top:5px'>Kaynak: {source_text}</div>
</div>"""

    note = "<p style='color:#627067;font-size:12px;margin:-8px 0 14px'>Haber iddiaları scout öneri skorunu veya maç modelini resmi teyit olmadan değiştirmez.</p>"
    return _section_title("📡 Transfer Haber İddiaları", f"{len(signals)} izlenen kayıt") + note + cards


def _promotions_section(promotions: list[dict]) -> str:
    context_box = """
<div style='background:#f3f0ff;border-left:3px solid #7c3aed;border-radius:6px;padding:12px 16px;margin-bottom:16px;font-size:13px;color:#627067'>
  <strong style='color:#7c3aed'>Transfer Sezonu Etkisi:</strong>
  Süper Lig'e yeni çıkan takımlar oyuncu takviyesi yapması, düşen takımlar ise yüksek maaşlı oyuncuları
  satması gerekiyor. Yeni takımların ihtiyaçları piyasada ek talep oluşturuyor.
</div>"""

    need_cards = ""
    for team_name in PROMOTED_TEAMS:
        need_cards += f"""
<div style='background:#fff;border:1px solid #d7ded9;border-radius:8px;padding:14px 16px;flex:1;min-width:200px;border-top:3px solid #116447'>
  <div style='color:#116447;font-size:11px;font-weight:600;letter-spacing:.5px'>⬆ YENİ TAKIM</div>
  <div style='color:#132018;font-weight:600;margin:6px 0 8px;font-size:14px'>{team_name.capitalize()}</div>
  <div style='color:#627067;font-size:12px;line-height:1.6'>
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
            news_items += f"""<div style='background:#f8faf9;border:1px solid #d7ded9;border-radius:6px;padding:10px 14px;margin-bottom:8px;font-size:13px;color:#132018'>
  {text}
  <span style='color:#8fa89a;font-size:11px;margin-left:8px'>{source}</span>
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
        ("1 Haziran", "Yaz transfer penceresi açılıyor", "#116447"),
        ("30 Haziran", "Sözleşmesi bitenler resmen serbest kalıyor", "#ef4444"),
        ("1 Temmuz", "Yeni sezon hazırlık kampları başlıyor", "#0d9488"),
        ("31 Ağustos", "Yaz transfer penceresi kapanıyor", "#d97706"),
        ("1 Ocak 2027", "Kış transfer penceresi açılacak", "#627067"),
    ]
    items = "".join(
        f"""<div style='display:flex;align-items:flex-start;gap:12px;margin-bottom:12px'>
  <div style='width:10px;height:10px;border-radius:50%;background:{c};flex-shrink:0;margin-top:3px'></div>
  <div><span style='color:#132018;font-size:13px;font-weight:600'>{date}</span>
  <span style='color:#627067;font-size:13px;margin-left:8px'>{desc}</span></div>
</div>"""
        for date, desc, c in milestones
    )
    return (
        _section_title("📅 Transfer Takvimi 2026")
        + f"<div style='background:#fff;border:1px solid #d7ded9;border-radius:8px;padding:16px 20px'>{items}</div>"
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
        "<meta name='viewport' content='width=device-width,initial-scale=1'>",
        f"<title>Transfer Sezonu – Süper Lig {TRANSFER_WATCH_SEASON_LABEL} | metric11</title>",
        f"<meta name='description' content='Süper Lig {TRANSFER_WATCH_SEASON_LABEL} transfer sezonu: sözleşmesi bitenler, serbest kalacaklar, yükselen takım ihtiyaçları ve transfer penceresi takvimi &mdash; metric11.'>",
        "<meta property='og:title' content='Transfer Sezonu &mdash; metric11'>",
        "<meta property='og:description' content='Süper Lig transfer sezonu: sözleşmesi bitenler, serbest kalacaklar ve pencere takvimi.'>",
        "<meta property='og:image' content='https://metric11.com/og_transfer_season.png'>",
        "<meta name='twitter:card' content='summary_large_image'>",
        "<meta name='twitter:image' content='https://metric11.com/og_transfer_season.png'>",
        "<link rel='icon' href='/favicon.svg' type='image/svg+xml'>",
        "<style>*{box-sizing:border-box}body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;",
        "background:#f3f5f4;color:#132018;margin:0;padding:20px}",
        "a{color:#116447}table td,table th{padding:8px 4px;text-align:left}",
        "tr:hover{background:#f7faf7}",
        ".x-share{display:inline-flex;align-items:center;gap:8px;background:#000;color:#fff;text-decoration:none;font-size:14px;font-weight:700;padding:10px 18px;border-radius:8px;transition:background .15s;}",
        ".x-share:hover{background:#1a1a1a;}",
        ".share-bar{padding:16px 0 8px;border-top:1px solid #d7ded9;margin-top:24px;}</style>",
        "</head><body>",
        "<div style='min-height:58px;padding:0 clamp(12px,3vw,28px);display:flex;align-items:center;justify-content:space-between;gap:16px;background:#091810;position:sticky;top:0;z-index:10;border-bottom:2px solid #1a3023'>"
        "<a style='display:flex;align-items:center;gap:10px;color:white;text-decoration:none;font-size:18px;font-weight:800;letter-spacing:-0.2px' href='/'>"
        "<b style='width:28px;height:28px;border-radius:6px;display:grid;place-items:center;color:#091810;background:#cde94e;font-size:14px;font-weight:900'>11</b>"
        " metric11"
        f"<span style='color:#6b7c72;font-size:11px;font-weight:500;border-left:1px solid #2a3d30;padding-left:8px;margin-left:2px'>Süper Lig {TRANSFER_WATCH_SEASON_LABEL}</span>"
        "</a>"
        "<nav style='display:flex;gap:2px;overflow-x:auto;scrollbar-width:none'>"
        "<a style='white-space:nowrap;color:#8fa89a;padding:8px 11px;border-radius:6px;text-decoration:none;font-size:13px;font-weight:600' href='/'>Gündem</a>"
        "<a style='white-space:nowrap;background:#162b20;color:white;padding:8px 11px;border-radius:6px;text-decoration:none;font-size:13px;font-weight:600' href='transfer_tracker_2025_2026.html'>Transferler</a>"
        "<a style='white-space:nowrap;color:#8fa89a;padding:8px 11px;border-radius:6px;text-decoration:none;font-size:13px;font-weight:600' href='all_teams_preview_dashboard_2025_2026.html'>Maç Önü</a>"
        "<a style='white-space:nowrap;color:#8fa89a;padding:8px 11px;border-radius:6px;text-decoration:none;font-size:13px;font-weight:600' href='transfer_recommendation_report_2025_2026.html'>Scout</a>"
        "<a style='white-space:nowrap;color:#8fa89a;padding:8px 11px;border-radius:6px;text-decoration:none;font-size:13px;font-weight:600' href='football_intelligence_home.html'>Analiz</a>"
        "</nav></div>",
        "<div style='max-width:1100px;margin:24px auto'>",
        _header_section(),
        _countdown_banner(),
        _summary_bar(free_agents, final_year, signals, promotions),
        _position_breakdown_section(free_agents),
        _window_timeline_section(),
        _free_agents_section(free_agents),
        _final_year_section(final_year),
        _signals_section(signals),
        _promotions_section(promotions),
        "<div class='share-bar'><a class='x-share' href='https://twitter.com/intent/tweet?text=Transfer%20penceresi%20a%C3%A7%C4%B1l%C4%B1yor%20%F0%9F%94%94%20261%20serbest%20ajan%2C%20%E2%82%AC506M%20piyasa%20de%C4%9Feri.%20S%C3%BCper%20Lig%20transfer%20sezonu%20analizi%3A&url=https%3A%2F%2Fmetric11.com%2Ftransfer_season_context_2025_2026.html' target='_blank' rel='noopener'>&#x1D54F; Paylaş</a></div>",
        "</div>",
        "  <script defer src=\"/_vercel/insights/script.js\"></script>",
        "</body></html>",
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
