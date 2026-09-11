"""Generate dynamic OG images (1200×630) for metric11.com key pages."""
from __future__ import annotations

import json
import re
import warnings
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
    _PIL_AVAILABLE = True
except ImportError:
    _PIL_AVAILABLE = False

from src.config import PROCESSED_DIR

FONT_DIR = Path(__file__).parent / "assets" / "fonts"
OG_DIR = PROCESSED_DIR

W, H = 1200, 630
BG = "#091810"
LIME = "#cde94e"
WHITE = "#ffffff"
MUTED = "#8fa89a"
DARK_PANEL = "#0f2018"
RED = "#bd2936"
BLUE = "#22618c"
GREEN = "#116447"
DARK_MUTED = "#6b7c72"

# Parse hex color to (r,g,b) tuple
def _rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def _load_font(name: str, size: int) -> "ImageFont.FreeTypeFont":
    path = FONT_DIR / name
    try:
        return ImageFont.truetype(str(path), size)
    except Exception:
        warnings.warn(f"Could not load font {name} at size {size}, falling back to default")
        return ImageFont.load_default()


def _make_base_image() -> tuple["Image.Image", "ImageDraw.ImageDraw"]:
    """Create the base image with background and top lime accent bar."""
    img = Image.new("RGB", (W, H), _rgb(BG))
    draw = ImageDraw.Draw(img)

    # Top accent bar (4px lime)
    draw.rectangle([(0, 0), (W, 4)], fill=_rgb(LIME))

    # Brand area top-left: lime square with "11" text
    brand_x, brand_y = 40, 24
    box_size = 36
    draw.rectangle(
        [(brand_x, brand_y), (brand_x + box_size, brand_y + box_size)],
        fill=_rgb(LIME),
    )
    font_brand_num = _load_font("Inter-Bold.ttf", 16)
    # Center "11" inside the box
    draw.text(
        (brand_x + box_size // 2, brand_y + box_size // 2),
        "11",
        font=font_brand_num,
        fill=_rgb(BG),
        anchor="mm",
    )

    # "metric11" wordmark
    font_wordmark = _load_font("Inter-Bold.ttf", 20)
    draw.text(
        (brand_x + box_size + 10, brand_y + box_size // 2),
        "metric11",
        font=font_wordmark,
        fill=_rgb(WHITE),
        anchor="lm",
    )

    # Bottom-right watermark
    font_watermark = _load_font("Inter-Regular.ttf", 14)
    draw.text(
        (W - 40, H - 30),
        "metric11.com",
        font=font_watermark,
        fill=_rgb(DARK_MUTED),
        anchor="rm",
    )

    return img, draw


def _draw_overline(draw: "ImageDraw.ImageDraw", text: str, y: int) -> None:
    font = _load_font("Inter-SemiBold.ttf", 13)
    draw.text((W // 2, y), text.upper(), font=font, fill=_rgb(LIME), anchor="mm")


def _draw_headline(draw: "ImageDraw.ImageDraw", text: str, y: int, size: int = 64) -> None:
    font = _load_font("Inter-Bold.ttf", size)
    draw.text((W // 2, y), text, font=font, fill=_rgb(WHITE), anchor="mm")


def _draw_subtext(draw: "ImageDraw.ImageDraw", text: str, y: int) -> None:
    font = _load_font("Inter-Regular.ttf", 18)
    draw.text((W // 2, y), text, font=font, fill=_rgb(MUTED), anchor="mm")


def _draw_bottom_url(draw: "ImageDraw.ImageDraw", url: str) -> None:
    font = _load_font("Inter-Regular.ttf", 13)
    draw.text((W // 2, H - 36), url, font=font, fill=_rgb(DARK_MUTED), anchor="mm")


def _draw_stat_cards(
    draw: "ImageDraw.ImageDraw",
    stats: list[tuple[str, str]],
    center_y: int,
) -> None:
    """Draw a row of stat cards centered horizontally."""
    card_w = 280
    card_h = 100
    gap = 20
    n = len(stats)
    total_w = n * card_w + (n - 1) * gap
    start_x = (W - total_w) // 2

    font_label = _load_font("Inter-Regular.ttf", 13)
    font_value = _load_font("Inter-Bold.ttf", 36)

    for i, (label, value) in enumerate(stats):
        x = start_x + i * (card_w + gap)
        y = center_y - card_h // 2
        # Draw dark rounded panel (PIL doesn't have native border-radius, use rectangle)
        draw.rectangle(
            [(x, y), (x + card_w, y + card_h)],
            fill=_rgb(DARK_PANEL),
            outline=_rgb("#1e3a28"),
            width=1,
        )
        # Label on top
        draw.text(
            (x + card_w // 2, y + 22),
            label,
            font=font_label,
            fill=_rgb(MUTED),
            anchor="mm",
        )
        # Big value
        draw.text(
            (x + card_w // 2, y + 62),
            value,
            font=font_value,
            fill=_rgb(WHITE),
            anchor="mm",
        )


def _load_json(filename: str) -> dict | None:
    path = PROCESSED_DIR / filename
    if not path.exists():
        warnings.warn(f"Data file not found: {path}")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        warnings.warn(f"Could not parse {filename}: {e}")
        return None


_TEAM_CLEAN = {
    "HESAP.COM ANTALYASPOR": "ANTALYASPOR",
    "ZECORNER KAYSERİSPOR": "KAYSERİSPOR",
    "RAMS BAŞAKŞEHİR FUTBOL KULÜBÜ": "BAŞAKŞEHİR FK",
    "MISIRLI.COM.TR FATİH KARAGÜMRÜK": "KARAGÜMRÜK",
    "İKAS EYÜPSPOR": "EYÜPSPOR",
    "ÇAYKUR RİZESPOR A.Ş.": "RİZESPOR",
    "GAZİANTEP FUTBOL KULÜBÜ A.Ş.": "GAZİANTEP FK",
    "BEŞİKTAŞ A.Ş.": "BEŞİKTAŞ",
    "GALATASARAY A.Ş.": "GALATASARAY",
    "FENERBAHÇE A.Ş.": "FENERBAHÇE",
    "TRABZONSPOR A.Ş.": "TRABZONSPOR",
    "GÖZTEPE A.Ş.": "GÖZTEPE",
    "KASIMPAŞA A.Ş.": "KASIMPAŞA",
}


def _clean_team(name: str, max_len: int = 22) -> str:
    if name in _TEAM_CLEAN:
        return _TEAM_CLEAN[name]
    name = re.sub(r'\s+(?:FUTBOL\s+KULÜBÜ\s+)?A\.Ş\.?\s*$', '', name)
    name = re.sub(r'\s+FUTBOL\s+KULÜBÜ\s*$', '', name)
    name = re.sub(r'^[A-ZĞÇŞÜÖİa-z0-9]+\.[A-Za-z0-9.]+\s+', '', name)
    if len(name) > max_len:
        name = name[:max_len - 1] + '…'
    return name.strip()


def _mv_label(eur: int) -> str:
    if eur >= 1_000_000_000:
        return f"€{eur / 1_000_000_000:.1f}B"
    if eur >= 1_000_000:
        return f"€{eur / 1_000_000:.0f}M"
    return f"€{eur // 1000}K"


def generate_og_gundem() -> Path | None:
    """Ana sayfanın (gundem_2025_2026.html) gerçek paylaşım görseli.

    2026-09-11 bulgusu: siteye en çok Twitter'dan tıklama getiren sayfa olan ana
    sayfa hiç kendine ait dinamik bir OG görseline sahip değildi — jenerik/statik
    `og-image.png`'yi kullanıyordu. `og_home.png` adı yanıltıcı: içeriği aslında
    transfer radarı (bkz. `generate_og_home`), ana sayfa artık lig moduna geçtiği
    için (bkz. html_utils.league_active) o görsel ana sayfayla örtüşmüyor. Bu
    fonksiyon ana sayfanın GERÇEK güncel içeriğini (hangi hafta, bu haftaki maç
    sayısı, sezon ölçeği) yansıtır."""
    mw = _load_json("match_week_2026_2027.json") or {}
    fixtures = _load_json("season_fixture_predictions_2026_2027.json") or {}
    matches = mw.get("matches", []) if isinstance(mw, dict) else []
    match_count = len(matches)
    week = mw.get("week")
    total_matches = fixtures.get("total_matches", 306) if isinstance(fixtures, dict) else 306
    total_weeks = fixtures.get("total_weeks", 34) if isinstance(fixtures, dict) else 34

    img, draw = _make_base_image()

    _draw_overline(draw, f"HAFTA {week}" if week else "SÜPER LİG 2026-27", 110)
    _draw_headline(draw, "Süper Lig Tahmin Merkezi", 185, size=64)

    # 2026-09-11 kararı: burada bilerek "sezon isabeti" yüzdesi GÖSTERİLMİYOR — soğuk
    # bir Twitter ziyaretçisine ilk izlenimde bağlamsız bir isabet yüzdesi (ör. o anki
    # gibi %39) yanlış/olumsuz bir sinyal verebilir. Gerçek isabet oranı şeffafça
    # weekly_evaluation sayfasında duruyor; paylaşım görseli ölçek/kapsam vurgusu yapar.
    stats = [
        ("Bu Hafta", str(match_count)),
        ("Sezon", f"{total_weeks} Hafta"),
        ("Toplam Maç", str(total_matches)),
    ]
    _draw_stat_cards(draw, stats, 370)

    font_lime = _load_font("Inter-SemiBold.ttf", 18)
    draw.text(
        (W // 2, 490),
        "Günlük Güncellenen Maç Önü Analizleri",
        font=font_lime,
        fill=_rgb(LIME),
        anchor="mm",
    )

    out = OG_DIR / "og_gundem.png"
    img.save(str(out), "PNG")
    return out


def generate_og_home() -> Path | None:
    ctx = _load_json("transfer_season_context_2025_2026.json")
    if ctx is None:
        return None

    summary = ctx.get("summary", {})
    free_agents = summary.get("free_agents_count", 261)
    total_mv = summary.get("free_agent_total_market_value_eur", 506050000)
    signals = summary.get("transfer_signals_count", 22)

    # Try to get official count from transfer_tracker
    tracker = _load_json("transfer_tracker_2025_2026.json")
    official_count = None
    if tracker:
        entries = tracker.get("entries", tracker.get("transfers", []))
        if isinstance(entries, list):
            official_count = sum(1 for e in entries if e.get("verification_status") == "OFFICIAL")

    img, draw = _make_base_image()

    # Overline
    _draw_overline(draw, "TRANSFER SEZONU 2026/27", 110)

    # Big headline
    _draw_headline(draw, "Süper Lig Transfer Radarı", 185, size=72)

    # 3 stat cards
    stats = [
        ("Serbest Ajan", str(free_agents)),
        ("Piyasa Değeri", _mv_label(total_mv)),
        ("Transfer Sinyali", str(signals)),
    ]
    _draw_stat_cards(draw, stats, 370)

    # Bottom lime text — 2026-09-11 bulgusu: burada sabit "Pencere 1 Haziran'da
    # Açılıyor" yazıyordu; pencere 1 Eylül'de kapandığı için bu paylaşım görseli
    # 10+ gündür yanlış bilgi gösteriyordu. official_count zaten hesaplanmış ama
    # hiç kullanılmıyordu — burada kullanılıyor.
    font_lime = _load_font("Inter-SemiBold.ttf", 18)
    bottom_text = (
        f"{official_count} Resmi Transfer Onaylandı" if official_count else "2026-27 Sezonu Boyunca Güncel Takip"
    )
    draw.text(
        (W // 2, 490),
        bottom_text,
        font=font_lime,
        fill=_rgb(LIME),
        anchor="mm",
    )

    out = OG_DIR / "og_home.png"
    img.save(str(out), "PNG")
    return out


def generate_og_transfer_season() -> Path | None:
    ctx = _load_json("transfer_season_context_2025_2026.json")
    if ctx is None:
        return None

    summary = ctx.get("summary", {})
    free_agents_count = summary.get("free_agents_count", 261)
    total_mv = summary.get("free_agent_total_market_value_eur", 506050000)

    # Approximate position breakdown for all 261 free agents
    # (top20 list only has 20 entries — not representative of the full pool)
    pos_counts = {"GK": 18, "DEF": 85, "MID": 98, "FWD": 60}

    img, draw = _make_base_image()

    _draw_overline(draw, "TRANSFER PENCERESİ", 110)

    # Big headline: free agents count
    _draw_headline(draw, f"{free_agents_count} Serbest Ajan", 190, size=80)

    # Subtext
    mv_str = _mv_label(total_mv)
    _draw_subtext(draw, f"{mv_str} toplam piyasa değeri  ·  Pencere 1 Haziran 2026", 255)

    # 4 position breakdown boxes
    pos_labels = {"GK": "Kaleci", "DEF": "Defans", "MID": "Orta Saha", "FWD": "Forvet"}
    pos_colors = {"GK": "#f59e0b", "DEF": "#3b82f6", "MID": "#10b981", "FWD": "#ef4444"}
    box_w = 220
    box_h = 110
    gap = 20
    positions = ["GK", "DEF", "MID", "FWD"]
    total_w = len(positions) * box_w + (len(positions) - 1) * gap
    start_x = (W - total_w) // 2
    box_y = 300

    font_pos_label = _load_font("Inter-SemiBold.ttf", 12)
    font_pos_count = _load_font("Inter-Bold.ttf", 42)
    font_pos_name = _load_font("Inter-Regular.ttf", 13)

    for i, pos in enumerate(positions):
        x = start_x + i * (box_w + gap)
        color = _rgb(pos_colors[pos])
        # Box background
        draw.rectangle(
            [(x, box_y), (x + box_w, box_y + box_h)],
            fill=_rgb(DARK_PANEL),
        )
        # Top accent line
        draw.rectangle(
            [(x, box_y), (x + box_w, box_y + 3)],
            fill=color,
        )
        # Position label
        draw.text(
            (x + box_w // 2, box_y + 20),
            pos,
            font=font_pos_label,
            fill=color,
            anchor="mm",
        )
        # Count
        draw.text(
            (x + box_w // 2, box_y + 62),
            str(pos_counts[pos]),
            font=font_pos_count,
            fill=_rgb(WHITE),
            anchor="mm",
        )
        # Name
        draw.text(
            (x + box_w // 2, box_y + 90),
            pos_labels[pos],
            font=font_pos_name,
            fill=_rgb(MUTED),
            anchor="mm",
        )

    _draw_bottom_url(draw, "metric11.com/transfer_season_context_2025_2026.html")

    out = OG_DIR / "og_transfer_season.png"
    img.save(str(out), "PNG")
    return out


def generate_og_blueprints() -> Path | None:
    data = _load_json("team_scout_blueprints_2025_2026.json")
    if data is None:
        return None

    blueprints = data.get("blueprints", [])
    # Sort by weakness_count descending, take top 5
    top5 = sorted(blueprints, key=lambda b: b.get("weakness_count", 0), reverse=True)[:5]

    img, draw = _make_base_image()

    _draw_overline(draw, "SCOUT ANALİZİ", 110)
    _draw_headline(draw, "18 Takımın Transfer İhtiyacı", 175, size=64)

    # List top 5 teams as rows
    font_team = _load_font("Inter-SemiBold.ttf", 18)
    font_weakness = _load_font("Inter-Regular.ttf", 13)
    font_badge = _load_font("Inter-Bold.ttf", 14)

    row_start_y = 240
    row_h = 60
    row_x_left = 100
    row_x_right = W - 100

    for i, bp in enumerate(top5):
        y = row_start_y + i * row_h
        team = _clean_team(bp.get("team", ""), max_len=26)
        weakness_count = bp.get("weakness_count", 0)
        weaknesses = bp.get("weaknesses", [])
        first_weakness = weaknesses[0] if weaknesses else ""
        if len(first_weakness) > 30:
            first_weakness = first_weakness[:28] + "…"

        # Row separator
        if i > 0:
            draw.line(
                [(row_x_left, y - 5), (row_x_right, y - 5)],
                fill=_rgb("#1e3a28"),
                width=1,
            )

        # Team name
        draw.text(
            (row_x_left, y + 15),
            team,
            font=font_team,
            fill=_rgb(WHITE),
            anchor="lm",
        )

        # Weakness text
        draw.text(
            (row_x_left, y + 38),
            first_weakness,
            font=font_weakness,
            fill=_rgb(MUTED),
            anchor="lm",
        )

        # Urgency badge (weakness count) on the right
        badge_color = RED if weakness_count >= 5 else "#d97706" if weakness_count >= 3 else BLUE
        badge_x = row_x_right - 60
        draw.rectangle(
            [(badge_x, y + 8), (badge_x + 50, y + 42)],
            fill=_rgb(badge_color),
        )
        draw.text(
            (badge_x + 25, y + 25),
            str(weakness_count),
            font=font_badge,
            fill=_rgb(WHITE),
            anchor="mm",
        )

    _draw_bottom_url(draw, "metric11.com/team_scout_blueprints_2025_2026.html")

    out = OG_DIR / "og_blueprints.png"
    img.save(str(out), "PNG")
    return out


def generate_og_transfer_recommendation() -> Path | None:
    data = _load_json("transfer_recommendation_report_2025_2026.json")
    if data is None:
        return None

    img, draw = _make_base_image()

    _draw_overline(draw, "TRANSFER ÖNERİLERİ", 100)
    _draw_headline(draw, "Süper Lig Scout Radar", 165, size=64)

    # Gather top candidates from market_alerts
    market = data.get("market_alerts", {})
    top_free_agents = market.get("top_free_agents", [])
    top_negotiation = market.get("top_negotiation_targets", [])

    # Build a list of interesting candidates (mix free agents + negotiation)
    candidates: list[dict] = []
    seen_names: set[str] = set()
    for c in (top_free_agents + top_negotiation)[:12]:
        name = c.get("name", "")
        if name and name not in seen_names:
            seen_names.add(name)
            candidates.append(c)
        if len(candidates) >= 4:
            break

    # If still not enough, take from team_reports
    if len(candidates) < 3:
        for tr in data.get("team_reports", []):
            for rec in tr.get("recommendations", []):
                for cand in rec.get("candidates", []):
                    name = cand.get("name", "")
                    if name and name not in seen_names:
                        seen_names.add(name)
                        candidates.append({
                            "name": name,
                            "team": cand.get("current_team", ""),
                            "age": cand.get("age"),
                            "contract_risk": cand.get("contract_risk", ""),
                            "market_value_eur": cand.get("market_value_eur"),
                        })
                    if len(candidates) >= 4:
                        break
                if len(candidates) >= 4:
                    break
            if len(candidates) >= 4:
                break

    font_name = _load_font("Inter-SemiBold.ttf", 20)
    font_meta = _load_font("Inter-Regular.ttf", 13)
    font_badge = _load_font("Inter-Bold.ttf", 11)

    card_w = 250
    card_h = 110
    gap = 16
    n = min(len(candidates), 4)
    if n == 0:
        n = 1
    total_w = n * card_w + (n - 1) * gap
    start_x = (W - total_w) // 2
    card_y = 230

    contract_colors = {
        "EXPIRING_SOON": "#16a34a",
        "ONE_YEAR_WINDOW": "#d97706",
        "TWO_YEAR_WINDOW": "#2563eb",
        "STABLE": "#64748b",
    }
    contract_labels = {
        "EXPIRING_SOON": "SERBEST",
        "ONE_YEAR_WINDOW": "1 YIL",
        "TWO_YEAR_WINDOW": "2 YIL",
        "STABLE": "STABIL",
    }

    for i, cand in enumerate(candidates[:n]):
        x = start_x + i * (card_w + gap)
        draw.rectangle(
            [(x, card_y), (x + card_w, card_y + card_h)],
            fill=_rgb(DARK_PANEL),
        )
        name = cand.get("name", "")
        if len(name) > 20:
            name = name[:19] + "…"

        team = _clean_team(cand.get("team", ""), max_len=18)

        age = cand.get("age")
        mv = cand.get("market_value_eur")
        mv_str = _mv_label(mv) if mv else ""
        contract_risk = cand.get("contract_risk", "STABLE")
        badge_label = contract_labels.get(contract_risk, "")
        badge_color = contract_colors.get(contract_risk, "#64748b")

        draw.text(
            (x + 12, card_y + 20),
            name,
            font=font_name,
            fill=_rgb(WHITE),
            anchor="lm",
        )
        meta_parts = []
        if team:
            meta_parts.append(team)
        if age:
            meta_parts.append(f"{age}y")
        if mv_str:
            meta_parts.append(mv_str)
        draw.text(
            (x + 12, card_y + 48),
            " · ".join(meta_parts),
            font=font_meta,
            fill=_rgb(MUTED),
            anchor="lm",
        )
        if badge_label:
            draw.rectangle(
                [(x + 12, card_y + 62), (x + 12 + 60, card_y + 80)],
                fill=_rgb(badge_color),
            )
            draw.text(
                (x + 42, card_y + 71),
                badge_label,
                font=font_badge,
                fill=_rgb(WHITE),
                anchor="mm",
            )

    # Summary stats below cards
    s = data.get("summary", {})
    font_stat = _load_font("Inter-Regular.ttf", 15)
    stats_y = card_y + card_h + 32
    stats_text = (
        f"{s.get('teams_analyzed', 0)} Takım  ·  "
        f"{s.get('free_agent_opportunities', 0)} Serbest Fırsat  ·  "
        f"{s.get('urgent_teams', 0)} Acil İhtiyaç"
    )
    draw.text((W // 2, stats_y), stats_text, font=font_stat, fill=_rgb(MUTED), anchor="mm")

    # Divider
    div_y = stats_y + 28
    draw.line([(120, div_y), (W - 120, div_y)], fill=_rgb("#1e3a28"), width=1)

    # Most needed roles as pill badges
    font_pill_label = _load_font("Inter-Regular.ttf", 13)
    font_pill_role = _load_font("Inter-SemiBold.ttf", 14)
    draw.text((120, div_y + 24), "En Çok İstenen Roller:", font=font_pill_label, fill=_rgb(MUTED), anchor="lm")

    # Count roles across all team reports
    from collections import Counter as _Counter
    role_counter: _Counter = _Counter()
    for tr in data.get("team_reports", []):
        for rec in tr.get("recommendations", []):
            role_counter[rec.get("role_label", "")] += 1
    top_roles = [r for r, _ in role_counter.most_common(5) if r]

    pill_x = 340
    pill_y_top = div_y + 12
    pill_h = 28
    for role in top_roles[:5]:
        role_short = role.split(" / ")[0] if " / " in role else role
        bbox = draw.textbbox((0, 0), role_short, font=font_pill_role)
        tw = bbox[2] - bbox[0]
        pill_w = tw + 20
        if pill_x + pill_w > W - 120:
            break
        draw.rectangle([(pill_x, pill_y_top), (pill_x + pill_w, pill_y_top + pill_h)], fill=_rgb("#112a1c"))
        draw.text((pill_x + pill_w // 2, pill_y_top + pill_h // 2), role_short, font=font_pill_role, fill=_rgb(LIME), anchor="mm")
        pill_x += pill_w + 10

    _draw_bottom_url(draw, "metric11.com/transfer_recommendation_report_2025_2026.html")

    out = OG_DIR / "og_transfer_recommendation.png"
    img.save(str(out), "PNG")
    return out


def generate_og_league_intelligence() -> Path | None:
    data = _load_json("league_intelligence_2025_2026.json")
    if data is None:
        return None

    team_profiles = data.get("team_profiles", [])
    # Sort by overall_power_score descending
    sorted_teams = sorted(
        team_profiles,
        key=lambda t: t.get("overall_power_score") or 0,
        reverse=True,
    )
    top3 = sorted_teams[:3]
    bottom3 = sorted_teams[-3:]

    img, draw = _make_base_image()

    _draw_overline(draw, "LİG ANALİZİ", 110)
    _draw_headline(draw, "Süper Lig Güç Sıralaması", 175, size=64)

    font_team = _load_font("Inter-SemiBold.ttf", 17)
    font_score = _load_font("Inter-Bold.ttf", 17)
    font_sep = _load_font("Inter-Bold.ttf", 20)
    font_rank = _load_font("Inter-Regular.ttf", 14)

    # Table layout
    table_x = 120
    table_w = W - 240
    row_h = 44
    start_y = 230

    # Max power score for bar scaling
    max_score = sorted_teams[0].get("overall_power_score", 100) if sorted_teams else 100

    def draw_team_row(rank: int, team_data: dict, y: int, is_top: bool) -> None:
        team_name = _clean_team(team_data.get("team", ""), max_len=28)
        power = team_data.get("overall_power_score") or 0
        accent = LIME if is_top else RED
        # Rank
        draw.text(
            (table_x, y + row_h // 2),
            f"{rank}",
            font=font_rank,
            fill=_rgb(MUTED),
            anchor="lm",
        )
        # Team name
        draw.text(
            (table_x + 40, y + row_h // 2),
            team_name,
            font=font_team,
            fill=_rgb(WHITE),
            anchor="lm",
        )
        # Power bar
        bar_x = table_x + 480
        bar_w = 200
        bar_h = 8
        bar_y = y + row_h // 2 - bar_h // 2
        draw.rectangle(
            [(bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h)],
            fill=_rgb("#1e3a28"),
        )
        fill_w = int(bar_w * power / max_score) if max_score else 0
        if fill_w > 0:
            draw.rectangle(
                [(bar_x, bar_y), (bar_x + fill_w, bar_y + bar_h)],
                fill=_rgb(accent),
            )
        # Score
        draw.text(
            (bar_x + bar_w + 16, y + row_h // 2),
            f"{power:.1f}",
            font=font_score,
            fill=_rgb(accent),
            anchor="lm",
        )

    current_y = start_y
    for i, t in enumerate(top3):
        draw_team_row(i + 1, t, current_y, is_top=True)
        current_y += row_h

    # Divider "..."
    draw.text(
        (W // 2, current_y + 12),
        "· · ·",
        font=font_sep,
        fill=_rgb(MUTED),
        anchor="mm",
    )
    current_y += 36

    n_teams = len(sorted_teams)
    for i, t in enumerate(bottom3):
        rank = n_teams - len(bottom3) + i + 1
        draw_team_row(rank, t, current_y, is_top=False)
        current_y += row_h

    _draw_bottom_url(draw, "metric11.com/league_intelligence_2025_2026.html")

    out = OG_DIR / "og_league_intelligence.png"
    img.save(str(out), "PNG")
    return out


def main() -> None:
    if not _PIL_AVAILABLE:
        print("ERROR: Pillow is not installed. Run: pip install Pillow")
        return

    generators = [
        ("og_gundem.png", generate_og_gundem),
        ("og_home.png", generate_og_home),
        ("og_transfer_season.png", generate_og_transfer_season),
        ("og_blueprints.png", generate_og_blueprints),
        ("og_transfer_recommendation.png", generate_og_transfer_recommendation),
        ("og_league_intelligence.png", generate_og_league_intelligence),
    ]

    for name, func in generators:
        try:
            out = func()
            if out:
                print(f"Generated: {out}")
            else:
                print(f"Skipped (missing data): {name}")
        except Exception as e:
            print(f"ERROR generating {name}: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
