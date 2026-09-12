"""Futbolsever odaklı canlı gündem sayfası.

Son transfer haberleri, Twitter sinyalleri, resmi transferler ve
yaz penceresi özetini tek ekranda toplar. Analiz araçlarından önce gelir.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path

from src.config import DATA_DIR, PROCESSED_DIR, SEASON, TRANSFER_WATCH_SEASON_LABEL
from src.html_utils import league_active, nav_links_html, telegram_cta_html
from src.build_match_week import render_hero_html

_TR_WEEKDAYS = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
_TR_MONTHS = ["", "Oca", "Şub", "Mar", "Nis", "May", "Haz", "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara"]

OUTPUT_HTML = PROCESSED_DIR / f"gundem_{SEASON}.html"

WINDOW_OPEN_DATE  = datetime(2026, 6, 1, tzinfo=timezone.utc)
WINDOW_CLOSE_DATE = datetime(2026, 9, 1, tzinfo=timezone.utc)

SOURCE_COLORS = {
    "official_club": ("#16a34a", "#dcfce7", "Resmi Kulüp"),
    "rss":           ("#2563eb", "#dbeafe", "Basın"),
    "google_news":   ("#2563eb", "#dbeafe", "Google News"),
    "twitter":       ("#7c3aed", "#ede9fe", "Twitter"),
    "telegram":      ("#0e7490", "#cffafe", "Telegram"),
    "official":      ("#16a34a", "#dcfce7", "Resmi"),
}

# 1-10 güven skoru: 10=resmi kulüp, 7=ana medya RSS, 5=sosyal medya, 3=bilinmeyen
SOURCE_TRUST: dict[str, int] = {
    "official_club": 10,
    "official":      10,
    "rss":           7,
    "google_news":   6,
    "twitter":       5,
    "telegram":      4,
}

TRANSFER_STATUS = {
    "OFFICIAL":        ("#16a34a", "#dcfce7", "RESMİ"),
    "CORROBORATED":    ("#2563eb", "#dbeafe", "DOĞRULANDI"),
    "TM_CONFIRMED":    ("#7c3aed", "#ede9fe", "TM KADRO"),
    "RUMOR":           ("#d97706", "#fef3c7", "SÖYLENTI"),
    "REVIEW_REQUIRED": ("#6b7280", "#f1f5f9", "İNCELEMEDE"),
}


def _load(path: Path) -> dict | list:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def _window_state() -> tuple[str, str, str, str, str | None]:
    """Returns (state, banner_css, dot_css, message, link_href) for the top banner.

    Transfer penceresi kapandıktan sonra bu şerit artık bayat bir durum bildirimi
    yerine tahmin oyununun evergreen tanıtımına dönüşüyor — sitenin en görünür
    alanı (nav'ın hemen altı) boşa gitmesin diye."""
    now = datetime.now(timezone.utc)
    if now >= WINDOW_CLOSE_DATE:
        return (
            "promo",
            "background:linear-gradient(90deg,#0f2318,#0a1a10);border-bottom:1px solid #cde94e",
            "background:#cde94e",
            "🎮 <strong>Tahmin Oyunu açık!</strong> Süper Lig maçlarına skor tahmini gir, puan topla, "
            "lider tablosunda yarış — <strong>ücretsiz</strong> →",
            "/tahmin",
        )
    if now >= WINDOW_OPEN_DATE:
        days_left = (WINDOW_CLOSE_DATE - now).days
        return (
            "open",
            "background:linear-gradient(90deg,#14532d,#166534);border-bottom:1px solid #16a34a",
            "background:#4ade80",
            f"<strong>Transfer penceresi açık</strong> — {days_left} gün kaldı (1 Haz – 31 Ağu 2026)",
            None,
        )
    days_left = (WINDOW_OPEN_DATE - now).days
    return (
        "countdown",
        "background:linear-gradient(90deg,#1e3a5f,#0f2a4a);border-bottom:1px solid #1e40af",
        "background:#60a5fa",
        f"Transfer penceresi <strong>{days_left} gün sonra</strong> açılıyor (1 Haziran 2026)",
        None,
    )


def _source_badge(source_type: str) -> str:
    color, bg, label = SOURCE_COLORS.get(source_type, ("#6b7280", "#f1f5f9", source_type))
    return f"<span style='font-size:10px;padding:1px 6px;border-radius:3px;font-weight:700;color:{color};background:{bg}'>{escape(label)}</span>"


def _transfer_badge(status: str) -> str:
    color, bg, label = TRANSFER_STATUS.get(status, ("#6b7280", "#f1f5f9", status))
    return f"<span style='font-size:10px;padding:1px 6px;border-radius:3px;font-weight:700;color:{color};background:{bg}'>{escape(label)}</span>"


def _fmt_date(published_at: str | None) -> str:
    if not published_at:
        return ""
    try:
        raw = published_at.strip()
        # Format: "21.5.2026" veya "21.5.2026 14:30"
        if raw and raw[0].isdigit() and "." in raw[:6] and not raw.startswith("202"):
            parts = raw.split(" ")[0].split(".")
            d, m, y = int(parts[0]), int(parts[1]), int(parts[2])
            dt = datetime(y, m, d, tzinfo=timezone.utc)
        # Format: RFC 2822 "Sat, 24 May 2026 ..."
        elif "," in raw[:4]:
            from email.utils import parsedate_to_datetime
            dt = parsedate_to_datetime(raw)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
        # Format: ISO 8601 "2026-05-24T14:30:00Z" veya "2026-05-24"
        else:
            dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
        diff = datetime.now(timezone.utc) - dt
        if diff.days < 0:
            return ""
        if diff.days == 0:
            h = diff.seconds // 3600
            return f"{h}sa" if h else "az önce"
        if diff.days == 1:
            return "dün"
        return f"{diff.days}g önce"
    except Exception:
        return ""


def _article_html(a: dict, source_count: int = 1, player_name: str | None = None) -> str:
    title = escape(a.get("title", "")[:120])
    link  = escape(a.get("link", "") or "")
    src   = a.get("source", "")
    stype = a.get("source_type", "rss")
    cats  = a.get("categories") or ([a.get("category")] if a.get("category") else [])
    age   = _fmt_date(a.get("published_at"))
    trust = SOURCE_TRUST.get(stype, 5)

    tag = ""
    if "transfer" in cats:
        tag = "<span style='font-size:10px;color:#d97706;font-weight:700'>⟳ TRANSFER</span> "
    elif "injury" in cats:
        tag = "<span style='font-size:10px;color:#dc2626;font-weight:700'>⚕ SAKAT</span> "
    elif "suspension" in cats:
        tag = "<span style='font-size:10px;color:#9333ea;font-weight:700'>🟥 CEZA</span> "

    title_color = "var(--ink)" if trust >= 6 else "#627067"
    age_html = f"<span style='font-size:11px;color:var(--muted);margin-left:auto'>{escape(age)}</span>" if age else ""
    anchor = f'<a href="{link}" target="_blank" style="color:{title_color};text-decoration:none;line-height:1.4">{tag}{title}</a>' if link else f"<span style='color:{title_color}'>{tag}{title}</span>"
    multi_html = f"<span style='font-size:10px;color:#7c3aed;font-weight:600;margin-left:4px'>{source_count} kaynak</span>" if source_count > 1 else ""
    player_html = f"<span style='font-size:10px;padding:1px 6px;border-radius:3px;background:#fef3c7;color:#92400e;font-weight:600;margin-left:4px'>👤 {escape(player_name)}</span>" if player_name else ""
    return f"""<div style="padding:12px 0;border-bottom:1px solid var(--line)">
  {anchor}{multi_html}{player_html}<div style="margin-top:4px;display:flex;gap:6px;align-items:center">{_source_badge(stype)}<span style="font-size:11px;color:var(--muted)">{escape(src)}</span>{age_html}</div>
</div>"""


def _transfer_html(t: dict) -> str:
    raw_player = t.get("player") or ""
    if not raw_player or raw_player == "?":
        return ""
    player = escape(raw_player)
    _frm = t.get("from_club") or ""
    _to  = t.get("to_club") or ""
    frm  = escape(_frm if _frm and _frm != "?" else "—")
    to   = escape(_to  if _to  and _to  != "?" else "—")
    mv     = escape(t.get("market_value_text", "—"))
    status = t.get("status", "REVIEW_REQUIRED")
    link   = t.get("link", "")
    badge  = _transfer_badge(status)
    inner  = f'<a href="{escape(link)}" target="_blank" style="color:var(--ink);text-decoration:none"><strong>{player}</strong></a>' if link else f"<strong>{player}</strong>"
    return f"""<div style="padding:11px 0;border-bottom:1px solid var(--line)">
  <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">{inner}{badge}</div>
  <div style="margin-top:3px;font-size:12px;color:var(--muted)">{frm} → {to} <span style="margin-left:8px;font-weight:600;color:var(--ink)">{mv}</span></div>
</div>"""


def _pill(val: str, label: str, color: str = "var(--green)") -> str:
    return f"""<div style="background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:12px 16px;text-align:center;flex:1;min-width:100px">
  <div style="font-size:20px;font-weight:700;color:{color}">{escape(val)}</div>
  <div style="font-size:11px;color:var(--muted);margin-top:2px">{escape(label)}</div>
</div>"""


def _fmt_fixture_date(date_str: str) -> str:
    months = ["", "Oca", "Şub", "Mar", "Nis", "May", "Haz", "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara"]
    try:
        dt = datetime.strptime(date_str.split(" ")[0], "%d.%m.%Y")
        return f"{dt.day} {months[dt.month]}"
    except (ValueError, IndexError):
        return date_str


def _next_fixtures_html(fixture_predictions: dict) -> str:
    weeks = fixture_predictions.get("weeks") or []
    if not weeks:
        return ""
    matches = weeks[0].get("matches", [])[:6]
    if not matches:
        return ""
    labels = {"home": "#4ade80", "draw": "#94a3b8", "away": "#f87171"}
    rows = "".join(
        f'<div style="display:flex;justify-content:space-between;align-items:center;padding:9px 0;border-bottom:1px solid var(--line);font-size:12px">'
        f'<span style="font-weight:600">{escape(m["home_team"])} <span style="color:var(--muted);font-weight:400">vs</span> {escape(m["away_team"])}</span>'
        f'<span style="display:flex;align-items:center;gap:6px;flex-shrink:0"><span style="color:var(--muted);font-size:11px">{escape(_fmt_fixture_date(m["date_time"]))}</span>'
        f'<span style="width:8px;height:8px;border-radius:50%;background:{labels.get(m["predicted"], "#64748b")}"></span></span>'
        f'</div>'
        for m in matches
    )
    return f"""<div class="panel" style="border-top:3px solid var(--lime)">
  <h2>🗓️ 2026-27 Sezonu Başlıyor</h2>
  <div class="sub">{weeks[0]["week"]}. hafta fikstürü ve tahminler · {fixture_predictions.get("total_matches", 0)} maçlık tam sezon fikstürü hazır</div>
  {rows}
  <a class="see-more" href="season_fixture_predictions_2026_2027.html">Tüm sezon fikstürü ve tahminlerine git →</a>
</div>"""


def _deduplicate_articles(articles: list[dict]) -> list[tuple[dict, int]]:
    """Başlık benzerliğine göre haberleri grupla. (en iyi haber, kaynak sayısı) döner."""
    STOP = {"ve", "ile", "de", "da", "bir", "bu", "için", "the", "a", "in", "of", "to"}
    MIN_MATCH = 3

    def keywords(title: str) -> set[str]:
        words = title.lower().split()
        return {w for w in words if len(w) > 3 and w not in STOP}

    groups: list[list[int]] = []
    used = set()

    for i, a in enumerate(articles):
        if i in used:
            continue
        kw_i = keywords(a.get("title", ""))
        group = [i]
        for j, b in enumerate(articles):
            if j <= i or j in used:
                continue
            kw_j = keywords(b.get("title", ""))
            if len(kw_i & kw_j) >= MIN_MATCH:
                group.append(j)
                used.add(j)
        used.add(i)
        groups.append(group)

    result = []
    for group in groups:
        best = max(group, key=lambda idx: SOURCE_TRUST.get(articles[idx].get("source_type", ""), 5))
        result.append((articles[best], len(group)))
    return result


def _build_player_index(transfers: list[dict]) -> dict[str, str]:
    """Transfer listesinden oyuncu adı → tam ad eşlem tablosu üretir (soyad bazlı)."""
    index: dict[str, str] = {}
    for t in transfers:
        full = (t.get("player") or "").strip()
        if not full:
            continue
        parts = full.split()
        for part in parts:
            if len(part) >= 4:
                index[part.lower()] = full
        if len(parts) >= 2:
            index[parts[-1].lower()] = full  # soyad
    return index


def _detect_player(title: str, player_index: dict[str, str]) -> str | None:
    """Haber başlığında geçen ilk bilinen oyuncu adını döner (kelime sınırı kontrolü ile)."""
    import re
    title_lower = title.lower()
    title_words = set(re.findall(r"[a-züöşıçğ]{4,}", title_lower))
    for token, full_name in player_index.items():
        if token in title_words:
            return full_name
    return None


def _nearest_known_fixture_html() -> str:
    """football-data.org nitelendirme fikstürünü kapsamadığı için haber kaynaklarından
    doğrulanmış gerçek maç bilgisini (tarih/saat/rakip) gösterir — skor/olasılık tahmini yok."""
    path = DATA_DIR / "manual" / "european_qualifier_fixtures_2026_2027.json"
    if not path.exists():
        return ""
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ""
    fixtures = payload.get("fixtures", [])
    if not fixtures:
        return ""
    now = datetime.now(timezone.utc)
    # Yalnız bugünkü/gelecekteki maçlar — oynanmış (geçmiş) elemeleri gösterme.
    # (Eski kod yalnız TEK geçmiş maçı atlıyordu; birden çok oynanmış maç varsa
    # ikinci en eski geçmiş maça düşüyordu — bayat fikstür sorunu.)
    upcoming = []
    for fx in fixtures:
        try:
            dt = datetime.fromisoformat(fx["kickoff_local"])
        except (KeyError, ValueError):
            continue
        if (dt.date() - now.astimezone(dt.tzinfo).date()).days >= 0:
            upcoming.append((dt, fx))
    if not upcoming:
        return ""
    upcoming.sort(key=lambda pair: pair[0])
    dt, fx = upcoming[0]
    delta_days = (dt.date() - now.astimezone(dt.tzinfo).date()).days
    if delta_days == 0:
        day_label = "Bugün"
    elif delta_days == 1:
        day_label = "Yarın"
    elif 2 <= delta_days <= 6:
        day_label = _TR_WEEKDAYS[dt.weekday()]
    else:
        day_label = f"{dt.day} {_TR_MONTHS[dt.month]}"
    time_str = dt.strftime("%H:%M") if fx.get("kickoff_time_confirmed", True) else "saat TBD"
    return (
        '<a href="european_predictions_2026_2027.html" style="display:flex;align-items:flex-start;gap:6px;text-decoration:none;'
        'background:rgba(74,222,128,.08);border:1px solid rgba(74,222,128,.25);border-radius:7px;padding:8px 10px;margin-bottom:10px">'
        '<span style="width:6px;height:6px;border-radius:50%;background:#4ade80;margin-top:5px;flex-shrink:0;animation:pulse 2s infinite"></span>'
        f'<span style="font-size:11px;color:#e2e8f0;line-height:1.4">{escape(day_label)} {escape(time_str)} — '
        f'{escape(fx.get("home_team",""))} - {escape(fx.get("away_team",""))}</span>'
        '</a>'
    )


def _score_sidebar_html() -> str:
    """Lig-modunda sağ sütunun üstünde skor tahminlerini öne çıkaran kompakt panel.

    Transfer stat bloğunun görsel dilini (yeşil stat kutuları) skor temasına (lime
    aksan) uyarlar; bu haftanın maç sayısı + sezon isabeti + fikstür/karne linkleri."""
    mw = _load(PROCESSED_DIR / "match_week_2026_2027.json")
    we = _load(PROCESSED_DIR / "weekly_evaluation_2026_2027.json")
    matches = mw.get("matches", []) if isinstance(mw, dict) else []
    match_count = len(matches)
    if not match_count:
        return ""
    week = mw.get("week")
    week_lbl = f"Hafta {week}" if week else "Bu Hafta"
    summ = we.get("summary", {}) if isinstance(we, dict) else {}
    evaluated = summ.get("evaluated_matches", 0)
    if evaluated:
        acc = summ.get("accuracy", 0.0) or 0.0
        second_val, second_lbl = f"%{acc * 100:.0f}", "Sezon İsabeti"
    else:
        second_val, second_lbl = "Yeni", "Sezon Başladı"
    return (
        '<div class="panel" style="border-top:3px solid var(--lime);font-size:13px">'
        '<div style="font-size:10px;font-weight:700;color:var(--lime);letter-spacing:.06em;margin-bottom:10px;text-transform:uppercase">Skor Tahminleri · 2026-27</div>'
        '<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:14px">'
        f'<div style="background:#0f2318;border-radius:6px;padding:10px 12px"><div style="font-size:22px;font-weight:800;color:white">{match_count}</div><div style="color:#8fa89a;font-size:11px;margin-top:2px">{escape(week_lbl)} Maçı</div></div>'
        f'<div style="background:#0f2318;border-radius:6px;padding:10px 12px"><div style="font-size:22px;font-weight:800;color:white">{escape(second_val)}</div><div style="color:#8fa89a;font-size:11px;margin-top:2px">{escape(second_lbl)}</div></div>'
        '</div>'
        f'<div style="display:flex;flex-direction:column;gap:7px">{_ana_link("season_fixture_predictions_2026_2027.html", "Fikstür & skor tahminleri →", bold=True)}{_ana_link("weekly_evaluation_2026_2027.html", "Haftalık isabet karnesi →")}</div>'
        '</div>'
    )


def _predict_game_sidebar_html() -> str:
    """Kullanıcı tahmin oyununu (tahmin.metric11.com, /tahmin altında) tanıtan
    öne çıkan sidebar kartı. Siteye yeni eklenen flagship özellik — en üstte gösterilir."""
    return (
        '<a href="/tahmin" style="display:block;text-decoration:none;color:inherit">'
        '<div class="panel" style="border-top:3px solid var(--lime);background:linear-gradient(165deg,#0f2318,#0a1a10);font-size:13px">'
        '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px">'
        '<div style="font-size:10px;font-weight:700;color:var(--lime);letter-spacing:.06em;text-transform:uppercase">🎮 Tahmin Oyunu</div>'
        '<span style="font-size:9px;font-weight:800;color:#091810;background:var(--lime);border-radius:4px;padding:2px 6px;letter-spacing:.04em">YENİ</span>'
        '</div>'
        '<div style="color:white;font-size:14px;font-weight:700;line-height:1.35;margin-bottom:6px">Kendi tahminini gir, metric11 ile yarış</div>'
        '<div style="color:#8fa89a;font-size:12px;line-height:1.5;margin-bottom:14px">Üye ol, her hafta skor tahminlerini gönder, otomatik puanlan ve lider tablosunda yerini al — tamamen ücretsiz.</div>'
        '<div style="display:block;text-align:center;padding:9px;background:var(--lime);border-radius:7px;color:#091810;font-size:12px;font-weight:800">Ücretsiz Katıl →</div>'
        '</div>'
        '</a>'
    )


def _kadro_kur_sidebar_html() -> str:
    """Kadro Kur (fantasy manager) oyununu tanıtan sidebar kartı — tahmin oyunu
    kartıyla aynı görsel dilde, hemen altında gösterilir (bkz. _predict_game_sidebar_html)."""
    pool = _load(PROCESSED_DIR / "fantasy_player_pool_2026_2027.json")
    player_count = pool.get("player_count", 0) if isinstance(pool, dict) else 0
    return (
        '<a href="https://tahmin.metric11.com/kadro" style="display:block;text-decoration:none;color:inherit">'
        '<div class="panel" style="border-top:3px solid var(--lime);background:linear-gradient(165deg,#0f2318,#0a1a10);font-size:13px">'
        '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px">'
        '<div style="font-size:10px;font-weight:700;color:var(--lime);letter-spacing:.06em;text-transform:uppercase">🏆 Kadro Kur</div>'
        '<span style="font-size:9px;font-weight:800;color:#091810;background:var(--lime);border-radius:4px;padding:2px 6px;letter-spacing:.04em">YENİ</span>'
        '</div>'
        '<div style="color:white;font-size:14px;font-weight:700;line-height:1.35;margin-bottom:6px">15 kişilik hayalindeki kadroyu kur</div>'
        f'<div style="color:#8fa89a;font-size:12px;line-height:1.5;margin-bottom:14px">{player_count} oyuncudan bütçeni kur, her hafta ilk 11 + kaptan seç, gerçek maç istatistikleriyle puan topla.</div>'
        '<div style="display:block;text-align:center;padding:9px;background:var(--lime);border-radius:7px;color:#091810;font-size:12px;font-weight:800">Kadronu Kur →</div>'
        '</div>'
        '</a>'
    )


def _kadro_kur_panel_html() -> str:
    """Ana sütunda, transfer penceresi kapandıktan sonra artık bayat kalan
    'Transferler' bloğunun YERİNİ alan büyük Kadro Kur tanıtım paneli."""
    pool = _load(PROCESSED_DIR / "fantasy_player_pool_2026_2027.json")
    players = pool.get("players", []) if isinstance(pool, dict) else []
    player_count = pool.get("player_count", len(players)) if isinstance(pool, dict) else len(players)
    # market_value_eur ile sırala, price DEĞİL — fiyat artık 97. persentilin üzerini
    # MAX_PRICE'a kırpıyor (bkz. build_fantasy_player_pool.py), yani birçok yıldız
    # aynı fiyatta eşitleniyor; gerçek "en değerli" sırası yalnızca piyasa değerinden
    # okunabilir (2026-09-12 bulgusu: bu olmadan Osimhen yerine rastgele bir 15.0'lık
    # oyuncu üstte görünüyordu).
    top3 = sorted(players, key=lambda p: p.get("market_value_eur", 0), reverse=True)[:3]
    top3_html = "".join(
        f'<div style="display:flex;justify-content:space-between;padding:7px 0;border-top:1px solid #1e3228">'
        f'<span style="color:#e8eee9">{escape(p.get("name", ""))} <span style="color:#8fa89a;font-size:11px">({escape(p.get("team", ""))})</span></span>'
        f'<span style="color:var(--lime);font-weight:700">{p.get("price", 0):.1f}</span></div>'
        for p in top3
    )
    # Bu panel diğer kartlardan farklı olarak koyu (lime çerçeveli, gradient) bir arka
    # plana sahip — .panel h2/.sub sınıflarının varsayılan rengi (var(--ink), açık tema
    # kartları için neredeyse siyah) burada metni görünmez kılar, bu yüzden başlık ve
    # alt yazı rengi elle açık tona zorlanıyor (bkz. 2026-09-12 kullanıcı ekran görüntüsü).
    return (
        '<div class="panel" style="margin-top:16px;border-top:3px solid var(--lime);background:linear-gradient(165deg,#0f2318,#0a1a10)">'
        '<div style="display:flex;align-items:center;justify-content:space-between">'
        '<h2 style="margin:0;color:white">🏆 Kadro Kur</h2>'
        '<span style="font-size:9px;font-weight:800;color:#091810;background:var(--lime);border-radius:4px;padding:2px 6px;letter-spacing:.04em">YENİ OYUN</span>'
        '</div>'
        f'<div class="sub" style="color:#8fa89a">100 birim bütçe · {player_count} oyuncu · 18 takım</div>'
        f'<div style="color:#c7d6cc;font-size:13px;line-height:1.6;margin:10px 0">Süper Lig&#39;den 15 kişilik kadronu kur, her hafta ilk 11 + kaptan seç. Gol, temiz sayfa ve kartlarla gerçek maçlardan puan topla, arkadaşlarınla lider tablosunda yarış.</div>'
        f'<div style="margin-bottom:8px">{top3_html}</div>'
        '<a class="see-more" style="color:var(--lime);border-top-color:#1e3228" href="https://tahmin.metric11.com/kadro">Kadronu kur →</a>'
        '</div>'
    )


def _ana_link(href: str, label: str, bold: bool = False) -> str:
    exists = (PROCESSED_DIR / href).exists()
    if exists:
        weight = "font-weight:600;" if bold else ""
        return f'<a href="{escape(href)}" style="color:var(--green);text-decoration:none;{weight}">→ {escape(label)}</a>'
    return f'<span style="color:var(--muted);cursor:not-allowed" title="Henüz oluşturulmadı">→ {escape(label)}</span>'


def build_html() -> str:
    intel    = _load(PROCESSED_DIR / f"news_intelligence_{SEASON}.json")
    tracker  = _load(PROCESSED_DIR / f"transfer_tracker_{SEASON}.json")
    ctx      = _load(PROCESSED_DIR / f"transfer_season_context_{SEASON}.json")
    eu_pulse = _load(PROCESSED_DIR / f"european_news_pulse_{SEASON}.json")
    fixture_predictions = _load(PROCESSED_DIR / "season_fixture_predictions_2026_2027.json")

    transfers_all = tracker.get("transfers", [])
    player_index = _build_player_index(transfers_all)

    raw_articles = (intel.get("recent_articles") or [])[:18]
    deduped = _deduplicate_articles(raw_articles)
    articles_with_count = [
        (a, cnt, _detect_player(a.get("title", ""), player_index))
        for a, cnt in deduped[:6]
    ]
    transfers_show = [t for t in transfers_all if t.get("status") in ("OFFICIAL", "CORROBORATED", "TM_CONFIRMED")][:8]
    if len(transfers_show) < 4:
        transfers_show = transfers_all[:8]

    ctx_summary = ctx.get("summary", {}) if isinstance(ctx, dict) else {}
    free_agents = ctx_summary.get("free_agents_count", 0)
    final_year  = ctx_summary.get("final_year_count", 0)
    signals_count = ctx_summary.get("transfer_signals_count", 0)
    tracker_summary = tracker.get("summary", {}) if isinstance(tracker, dict) else {}
    official_count = tracker_summary.get("official_count", 0)

    _state, banner_css, dot_css, window_msg, window_link = _window_state()
    _is_transfer_season = _state in ("countdown", "open")
    _league = league_active()
    # 2026-09-11 bulgusu: başlık/açıklama sabit olarak "transfer haberleri"ne odaklıydı —
    # lig başladıktan sonra (league_active) sayfanın gerçek içeriği maç/tahmin odaklı
    # olduğu halde arama/paylaşım önizlemesi hâlâ transfer sezonundan kalma metni
    # gösteriyordu.
    _gundem_description = (
        "Süper Lig maç önü tahminleri, skor öngörüleri ve haftalık isabet karnesi. Günlük güncellenen analiz platformu."
        if _league else
        "Süper Lig transfer haberleri, sakat-cezalı listesi ve güncel transfer takibi. Tüm kaynaklar tek sayfada — metric11."
    )

    mv_eur = ctx_summary.get("free_agent_total_market_value_eur", 0)
    mv_str = f"€{mv_eur / 1_000_000:.0f}M" if mv_eur >= 1_000_000 else ""

    now_str = datetime.now(timezone.utc).strftime("%d.%m.%Y %H:%M UTC")
    articles_html = "".join(_article_html(a, cnt, player) for a, cnt, player in articles_with_count) or "<p style='color:var(--muted);padding:16px 0'>Henüz sinyal yok.</p>"
    transfers_html = "".join(_transfer_html(t) for t in transfers_show) or "<p style='color:var(--muted);padding:16px 0'>Henüz transfer kaydı yok.</p>"

    if _is_transfer_season:
        transfer_sidebar_html = (
            '<div class="panel" style="border-top:3px solid var(--lime);font-size:13px">'
            '<div style="font-size:10px;font-weight:700;color:var(--lime);letter-spacing:.06em;margin-bottom:10px;text-transform:uppercase">Transfer Sezonu 2026-2027</div>'
            '<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:14px">'
            f'<div style="background:#0f2318;border-radius:6px;padding:10px 12px"><div style="font-size:22px;font-weight:800;color:white">{free_agents}</div><div style="color:#8fa89a;font-size:11px;margin-top:2px">Serbest Kalacak</div></div>'
            f'<div style="background:#0f2318;border-radius:6px;padding:10px 12px"><div style="font-size:22px;font-weight:800;color:white">{final_year}</div><div style="color:#8fa89a;font-size:11px;margin-top:2px">Son Yıl Kontrat</div></div>'
            f'<div style="background:#0f2318;border-radius:6px;padding:10px 12px"><div style="font-size:22px;font-weight:800;color:white">{signals_count}</div><div style="color:#8fa89a;font-size:11px;margin-top:2px">Transfer Sinyali</div></div>'
            f'<div style="background:#0f2318;border-radius:6px;padding:10px 12px"><div style="font-size:18px;font-weight:800;color:white">{mv_str}</div><div style="color:#8fa89a;font-size:11px;margin-top:2px">Serbest Piyasa Değeri</div></div>'
            '</div>'
            f'<div style="display:flex;flex-direction:column;gap:7px">{_ana_link(f"transfer_recommendation_report_{SEASON}.html", "Takım transfer önerileri →", bold=True)}{_ana_link(f"transfer_season_context_{SEASON}.html", "Serbest kalacak oyuncular →")}</div>'
            '</div>'
        )
    else:
        transfer_sidebar_html = ""

    # Sağ sütun sıralaması: iki oyun kartı (tahmin + kadro kur) her zaman en üstte
    # (flagship özellikler); lig-modunda skor paneli onların altında, transfer bloğu
    # alta iner; lig öncesi transfer bloğu skor panelinin yerini alır.
    predict_game_html = _predict_game_sidebar_html()
    kadro_kur_sidebar_html = _kadro_kur_sidebar_html()
    score_sidebar_html = _score_sidebar_html() if _league else ""
    sidebar_top_html = predict_game_html + kadro_kur_sidebar_html + (score_sidebar_html if _league else transfer_sidebar_html)
    sidebar_bottom_html = transfer_sidebar_html if _league else ""

    if not _is_transfer_season:
        analysis_transfer_links_html = (
            '<div style="font-size:10px;font-weight:700;color:var(--muted);letter-spacing:.06em;margin-bottom:6px;text-transform:uppercase">Transfer &amp; Kadro</div>'
            '<div style="display:flex;flex-direction:column;gap:7px;margin-bottom:14px">'
            f'{_ana_link(f"transfer_recommendation_report_{SEASON}.html", "Takım transfer önerileri", bold=True)}'
            f'{_ana_link(f"transfer_season_context_{SEASON}.html", "Serbest kalacak oyuncular")}'
            f'{_ana_link(f"transfer_tracker_{SEASON}.html", "Transfer takip listesi")}'
            '</div>'
        )
    else:
        analysis_transfer_links_html = ""

    # Sol sütun üst bloğu: lig başladıysa "Bu Hafta" skor tahmini hero'su öne çıkar;
    # öncesinde transfer istatistik pilleri + fikstür teaser gösterilir.
    if _league:
        left_top_html = render_hero_html()
        if not left_top_html and isinstance(fixture_predictions, dict):
            left_top_html = _next_fixtures_html(fixture_predictions)
    else:
        pills_html = (
            '<div class="pills">'
            f'{_pill(str(official_count), "Resmi Transfer", "#16a34a")}'
            f'{_pill(str(signals_count), "Transfer Sinyali", "#d97706")}'
            f'{_pill(str(free_agents), "Serbest Kalacak", "#2563eb")}'
            f'{_pill(str(final_year), "Son Yıl Kontrat", "#7c3aed")}'
            '</div>'
        )
        fixtures_teaser = _next_fixtures_html(fixture_predictions) if isinstance(fixture_predictions, dict) else ""
        left_top_html = pills_html + fixtures_teaser

    eu_teaser_html = _nearest_known_fixture_html()
    if not eu_teaser_html:
        eu_pulse_items = eu_pulse.get("items", []) if isinstance(eu_pulse, dict) else []
        if eu_pulse_items:
            top = eu_pulse_items[0]
            eu_teaser_html = (
                '<a href="european_predictions_2026_2027.html" style="display:flex;align-items:flex-start;gap:6px;text-decoration:none;'
                'background:rgba(74,222,128,.08);border:1px solid rgba(74,222,128,.25);border-radius:7px;padding:8px 10px;margin-bottom:10px">'
                '<span style="width:6px;height:6px;border-radius:50%;background:#4ade80;margin-top:5px;flex-shrink:0;animation:pulse 2s infinite"></span>'
                f'<span style="font-size:11px;color:#e2e8f0;line-height:1.4">{escape(top.get("title", ""))}</span>'
                '</a>'
            )

    return f"""<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Gündem — Süper Lig {TRANSFER_WATCH_SEASON_LABEL} | metric11</title>
<meta name="description" content="{_gundem_description}">
<meta property="og:title" content="Gündem — Süper Lig {TRANSFER_WATCH_SEASON_LABEL} | metric11">
<meta property="og:description" content="{_gundem_description}">
<meta property="og:image" content="https://metric11.com/og_gundem.png">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:image" content="https://metric11.com/og_gundem.png">
<meta property="og:url" content="https://metric11.com/">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="canonical" href="https://metric11.com/">
<script type="application/ld+json">{{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "metric11",
  "url": "https://metric11.com",
  "description": "Süper Lig istatistik, transfer takibi ve futbol analiz platformu.",
  "inLanguage": "tr"
}}</script>
<style>
  :root{{--bg:#f3f5f4;--panel:#fff;--ink:#132018;--muted:#627067;--line:#d7ded9;--dark:#091810;--green:#116447;--lime:#cde94e}}
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{font-family:Inter,'Segoe UI',Arial,sans-serif;background:var(--bg);color:var(--ink)}}
  .topbar{{min-height:58px;padding:0 clamp(14px,3vw,32px);display:flex;align-items:center;justify-content:space-between;gap:18px;background:var(--dark);border-bottom:2px solid #1a3023}}
  .brand{{display:flex;align-items:center;gap:10px;color:white;text-decoration:none;font-size:18px;font-weight:800;letter-spacing:-0.2px}}
  .brand:visited,.brand:active,.brand:hover{{color:white}}
  .brand b{{width:28px;height:28px;border-radius:6px;display:grid;place-items:center;color:var(--dark);background:var(--lime);font-size:14px;font-weight:900}}
  .brand .slbl{{color:#6b7c72;font-size:11px;font-weight:500;border-left:1px solid #2a3d30;padding-left:8px;margin-left:2px}}
  .topnav{{display:flex;gap:2px;overflow-x:auto;scrollbar-width:none}}
  .topnav::-webkit-scrollbar{{display:none}}
  .topnav a{{white-space:nowrap;color:#8fa89a;padding:8px 11px;border-radius:6px;text-decoration:none;font-size:13px;font-weight:600;transition:background .15s,color .15s}}
  .topnav a:visited{{color:#8fa89a}}
  .topnav a:hover{{background:#162b20;color:white}}
  .topnav a.active{{background:#162b20;color:white}}
  .window-banner{{padding:10px clamp(14px,3vw,32px);color:#d1fae5;font-size:13px;display:flex;align-items:center;gap:10px}}
  .window-dot{{width:8px;height:8px;border-radius:50%;flex-shrink:0;animation:pulse 2s infinite}}
  @keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.4}}}}
  .main{{max-width:1200px;margin:0 auto;padding:20px clamp(12px,3vw,32px) 50px;display:grid;grid-template-columns:1fr 360px;gap:24px}}
  .panel{{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:18px 20px}}
  .panel h2{{font-size:15px;font-weight:700;margin-bottom:2px;color:var(--ink)}}
  .panel .sub{{font-size:11px;color:var(--muted);margin-bottom:12px}}
  .pills{{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:24px}}
  .see-more{{display:block;text-align:center;padding:10px;font-size:12px;color:var(--green);font-weight:600;text-decoration:none;border-top:1px solid var(--line);margin-top:8px}}
  .see-more:hover{{text-decoration:underline}}
  @media(max-width:860px){{.main{{grid-template-columns:1fr}}}}
  @media(max-width:600px){{
    .topbar{{flex-direction:column;align-items:stretch;padding:11px 12px 0;gap:0;min-height:unset}}
    .brand{{padding-bottom:8px}}
    .topnav{{border-top:1px solid #1e3228;padding:7px 0 9px}}
    .pills{{display:grid;grid-template-columns:1fr 1fr;gap:8px}}
    .panel{{padding:14px 14px}}
    .main{{padding:12px 10px 40px}}
  }}
</style>
</head>
<body>
<div class="topbar">
  <a class="brand" href="/"><b>11</b> metric11<span class="slbl">Süper Lig {TRANSFER_WATCH_SEASON_LABEL}</span></a>
  <nav class="topnav">{nav_links_html("/")}</nav>
</div>
{f'<a href="{window_link}" class="window-banner" style="{banner_css};text-decoration:none;cursor:pointer">' if window_link else f'<div class="window-banner" style="{banner_css}">'}
  <div class="window-dot" style="{dot_css}"></div>
  <span>{window_msg}{"" if window_link else f" · Güncelleme: {now_str}"}</span>
{'</a>' if window_link else '</div>'}
<div class="main">
  <div>
    <div style="margin-bottom:16px">{telegram_cta_html()}</div>
    {left_top_html}
    {f'''<div class="panel" style="margin-top:16px">
      <h2>Transferler</h2>
      <div class="sub">Resmi · Doğrulanmış · TM Onaylı</div>
      {transfers_html}
      <a class="see-more" href="transfer_tracker_{SEASON}.html">Tüm transfer takibine git →</a>
    </div>''' if _is_transfer_season else _kadro_kur_panel_html()}
    <div class="panel" style="margin-top:16px">
      <h2>Haber Sinyalleri</h2>
      <div class="sub">Son 14 gün · Basın + Resmi Kulüp + Google News</div>
      {articles_html}
      <a class="see-more" href="news_intelligence_dashboard_{SEASON}.html">Detaylı haber analizi →</a>
    </div>
  </div>
  <div style="display:flex;flex-direction:column;gap:16px">
    {sidebar_top_html}
    <div class="panel" style="font-size:13px;background:#09111f;border-color:#1e3a5f">
      <div style="font-size:10px;font-weight:700;color:#f59e0b;letter-spacing:.06em;margin-bottom:10px;text-transform:uppercase">⚽ Avrupa Kupası 2026-27</div>
      {eu_teaser_html}
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:7px;margin-bottom:12px">
        <a href="european_predictions_2026_2027.html" style="display:flex;flex-direction:column;align-items:center;justify-content:center;background:#0e1929;border:1px solid rgba(245,158,11,.3);border-radius:7px;padding:10px 6px;text-decoration:none;gap:3px">
          <span style="font-size:16px">🏆</span>
          <span style="font-size:11px;font-weight:700;color:#f59e0b">UCL</span>
        </a>
        <a href="european_predictions_2026_2027.html" style="display:flex;flex-direction:column;align-items:center;justify-content:center;background:#0e1929;border:1px solid rgba(249,115,22,.3);border-radius:7px;padding:10px 6px;text-decoration:none;gap:3px">
          <span style="font-size:16px">🟠</span>
          <span style="font-size:11px;font-weight:700;color:#f97316">UEL / UECL</span>
        </a>
      </div>
      <a href="european_predictions_2026_2027.html" style="display:block;text-align:center;padding:8px;background:rgba(245,158,11,.08);border:1px solid rgba(245,158,11,.2);border-radius:7px;color:#f59e0b;font-size:12px;font-weight:700;text-decoration:none">Avrupa Tahminlerine Git →</a>
    </div>
    <div class="panel" style="font-size:13px">
      <h2 style="margin-bottom:14px">Analiz Platformu</h2>
      {analysis_transfer_links_html}
      <div style="font-size:10px;font-weight:700;color:var(--muted);letter-spacing:.06em;margin-bottom:6px;text-transform:uppercase">Maç &amp; Tahmin</div>
      <div style="display:flex;flex-direction:column;gap:7px">
        {_ana_link("season_fixture_predictions_2026_2027.html", "Fikstür ve skor tahminleri", bold=_league) if _league else ""}
        {_ana_link("weekly_evaluation_2026_2027.html", "Haftalık tahmin karnesi") if _league else ""}
        {_ana_link(f"all_teams_preview_dashboard_{SEASON}.html", "Maç önü arşivi (18 takım)", bold=not _league)}
        {_ana_link("football_intelligence_home.html", "Tüm analiz araçları")}
      </div>
    </div>
    {sidebar_bottom_html}
  </div>
</div>
<script defer src="/_vercel/insights/script.js"></script>
</body>
</html>"""


def main() -> None:
    html = build_html()
    OUTPUT_HTML.write_text(html, encoding="utf-8")
    print(OUTPUT_HTML)


if __name__ == "__main__":
    main()
