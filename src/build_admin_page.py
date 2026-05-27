"""Yönetici paneli — istemci taraflı SHA-256 parola koruması.

Parola hash üretmek için:
  python -c "import hashlib; print(hashlib.sha256('email:sifre'.encode()).hexdigest())"

Çıktıyı ADMIN_CREDENTIALS_HASH ortam değişkeni olarak .env ve GitHub Secrets'a ekle.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from html import escape
from pathlib import Path

from src.config import PROCESSED_DIR, SEASON

ADMIN_HASH = os.getenv("ADMIN_CREDENTIALS_HASH", "")


def main() -> None:
    out = PROCESSED_DIR / "admin.html"
    # Hash env var yoksa mevcut dosyayı koru — lokal çalışmada CI hash'i kaybolmasın
    if not ADMIN_HASH and out.exists():
        print(f"ADMIN_CREDENTIALS_HASH eksik, mevcut {out} korunuyor.")
        return
    out.write_text(_build_html(), encoding="utf-8")
    print(out)


def _load(path: Path):
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _fmt(iso: str | None) -> str:
    if not iso:
        return "—"
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return dt.strftime("%d.%m.%Y %H:%M UTC")
    except Exception:
        return iso[:16]


def _build_html() -> str:
    pipeline = _load(PROCESSED_DIR / "daily_pipeline_run_latest.json") or {}
    news = _load(PROCESSED_DIR / f"news_intelligence_{SEASON}.json") or {}
    league = _load(PROCESSED_DIR / f"tff_super_lig_enriched_{SEASON}.json") or []
    model = _load(PROCESSED_DIR / f"league_prediction_model_{SEASON}.json") or {}
    dq = _load(PROCESSED_DIR / f"data_quality_scorecard_{SEASON}.json") or {}
    official = _load(PROCESSED_DIR / f"news_official_clubs_latest_{SEASON}.json") or {}
    twitter = _load(PROCESSED_DIR / f"news_twitter_latest_{SEASON}.json") or {}

    matches = league if isinstance(league, list) else []
    scored = [m for m in matches if m.get("home_team", {}).get("score") is not None]

    p_ok = pipeline.get("ok_count", 0)
    p_fail = pipeline.get("failed_count", 0)
    p_total = pipeline.get("command_count", 0)
    p_run = escape(_fmt(pipeline.get("generated_at")))
    p_status = "Sağlıklı" if p_fail == 0 else ("Uyarı" if p_fail <= 3 else "Hata")
    p_color = "#22c55e" if p_fail == 0 else ("#f59e0b" if p_fail <= 3 else "#ef4444")

    tw_accounts = twitter.get("accounts", [])
    tw_total = twitter.get("total_tweets", 0)
    tw_provider = escape(twitter.get("provider", "—"))
    tw_status = escape(twitter.get("collection_status", "NO_SNAPSHOT"))
    tw_success = twitter.get("successful_accounts", 0)
    tw_gen = escape(_fmt(twitter.get("generated_at")))
    official_total = official.get("total_articles", 0)
    official_success = official.get("successful_sources", 0)
    official_configured = official.get("configured_sources", 18)
    official_status = escape(official.get("collection_status", "NO_SNAPSHOT"))

    # Twitter tablo satırları
    tw_rows = ""
    if tw_accounts:
        for acc in tw_accounts:
            err = acc.get("error")
            fetched = acc.get("fetched", 0)
            sc = "#ef4444" if err else "#22c55e"
            st = f"Hata: {escape(str(err)[:70])}" if err else f"{fetched} gönderi"
            tw_rows += (
                f"<tr>"
                f"<td>@{escape(acc['handle'])}</td>"
                f"<td style='color:#94a3b8'>{escape(acc['name'])}</td>"
                f"<td style='color:{sc}'>{st}</td>"
                f"</tr>"
            )
    else:
        from src.collect_news_twitter import TWITTER_ACCOUNTS
        for acc in TWITTER_ACCOUNTS:
            tw_rows += (
                f"<tr>"
                f"<td>@{escape(acc['handle'])}</td>"
                f"<td style='color:#94a3b8'>{escape(acc['name'])}</td>"
                f"<td style='color:#6b7280'>Henüz çekilmedi</td>"
                f"</tr>"
            )

    tw_notice = (
        f"<p class='tw-meta'>Kaynak: {tw_provider} · Durum: {tw_status} · "
        f"{tw_total} gönderi · {tw_success}/{twitter.get('configured_accounts', 30)} hesap · Son: {tw_gen}</p>"
        if twitter else
        "<p class='tw-meta tw-warn'>X collector henüz çalışmadı. "
        "Üretim erişimi için X_BEARER_TOKEN ve kontrollü API bütçesi gerekir.</p>"
    )

    admin_tools = [
        ("Veri Kalite Scorecard", f"data_quality_scorecard_{SEASON}.html"),
        ("Veri Kataloğu", f"data_catalog_{SEASON}.html"),
        ("SQLite Veri Ambarı", "metric11_warehouse_quality.html"),
        ("Kaynak İzleme Listesi", f"source_watchlist_{SEASON}.html"),
        ("Scout Kalite Denetimi", f"scout_quality_report_{SEASON}.html"),
        ("Transfermarkt Eşleşme Kuyruğu", f"transfermarkt_match_review_queue_{SEASON}.html"),
        ("Oyuncu Alias Kalite", f"player_alias_quality_{SEASON}.html"),
        ("Tahmin Backtest", f"prediction_backtest_dashboard_{SEASON}.html"),
        ("OOS Validasyon", f"oos_validation_{SEASON}.html"),
        ("Büyük Maç Raporu", f"big_match_report_{SEASON}.html"),
        ("Dış API Veri (2024)", "api_football_super_lig_2024_analysis.html"),
        ("Dış API Derin Veri", "api_football_super_lig_deep_2024_analysis.html"),
        ("Pipeline Durum", "system_status.html"),
    ]
    tool_links = "".join(
        f'<a class="tool-link" href="{href}">{escape(name)}</a>'
        for name, href in admin_tools
    )

    # Başarısız pipeline komutları
    failed_rows = [r for r in pipeline.get("rows", []) if r.get("returncode", 0) != 0]
    if failed_rows:
        fail_cards = "".join(
            f"""<div style='margin-bottom:10px;background:#0a1008;border:1px solid #2d1515;border-left:3px solid #ef4444;border-radius:6px;padding:12px 14px'>
  <div style='font-size:12px;font-weight:700;color:#ef4444;margin-bottom:6px'>{escape(" ".join(r["command"]))}</div>
  <pre style='font-size:11px;color:#94a3b8;white-space:pre-wrap;word-break:break-word;margin:0;max-height:120px;overflow-y:auto'>{escape(r.get("stderr_tail","")[-600:] or r.get("stdout_tail","")[-600:] or "—")}</pre>
</div>"""
            for r in failed_rows
        )
        pipeline_fail_section = f"""
    <div class="card" style="margin-bottom:20px;border-color:#3d1515">
      <div class="card-title" style="color:#ef4444">⚠ Pipeline Hataları — {len(failed_rows)} başarısız komut</div>
      {fail_cards}
    </div>"""
    else:
        pipeline_fail_section = ""

    gen_at = escape(datetime.now(timezone.utc).strftime("%d.%m.%Y %H:%M UTC"))
    hash_js = json.dumps(ADMIN_HASH)

    login_body = (
        '<div class="setup-msg">⚠ ADMIN_CREDENTIALS_HASH yapılandırılmamış.<br>'
        'Terminalde şu komutu çalıştır ve çıktıyı .env ile GitHub Secrets\'a ekle:<br>'
        '<code>python -c "import hashlib; print(hashlib.sha256(\'email:sifre\'.encode()).hexdigest())"</code></div>'
        if not ADMIN_HASH else
        '<div class="field"><label>E-posta</label>'
        '<input type="email" id="admin-email" placeholder="ornek@mail.com" autocomplete="email"></div>'
        '<div class="field"><label>Parola</label>'
        '<input type="password" id="admin-password" placeholder="••••••••" autocomplete="current-password"></div>'
        '<button class="login-btn" onclick="checkAuth()">Giriş Yap</button>'
        '<div class="login-error" id="auth-error">E-posta veya parola hatalı.</div>'
    )

    return f"""<!doctype html>
<html lang="tr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Yönetici Paneli — metric11</title>
  <meta name="robots" content="noindex,nofollow">
  <meta name="theme-color" content="#091810">
  <link rel="icon" href="favicon.svg" type="image/svg+xml">
  <style>
    :root {{
      --bg:#0d1b14; --panel:#0f2018; --ink:#e2e8e4; --muted:#6b8070; --line:#1e3228;
      --green:#22c55e; --lime:#cde94e; --dark:#091810; --red:#ef4444; --amber:#f59e0b;
    }}
    *{{box-sizing:border-box;margin:0;padding:0;}}
    body{{font-family:Inter,"Segoe UI",Arial,sans-serif;background:var(--bg);color:var(--ink);min-height:100vh;}}
    #login-gate{{min-height:100vh;display:flex;align-items:center;justify-content:center;padding:24px;}}
    .login-box{{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:32px;width:min(380px,100%);}}
    .login-logo{{display:flex;align-items:center;gap:10px;margin-bottom:28px;}}
    .login-mark{{width:34px;height:34px;display:grid;place-items:center;border-radius:8px;background:var(--lime);color:#091810;font-weight:800;font-size:16px;}}
    .login-title{{font-weight:800;font-size:18px;color:white;}}
    .login-sub{{font-size:12px;color:var(--muted);margin-top:2px;}}
    .field{{margin-bottom:14px;}}
    .field label{{display:block;font-size:11px;color:var(--muted);margin-bottom:5px;font-weight:700;text-transform:uppercase;letter-spacing:.05em;}}
    .field input{{width:100%;background:#091810;border:1px solid var(--line);border-radius:6px;padding:10px 12px;color:var(--ink);font-size:14px;outline:none;}}
    .field input:focus{{border-color:#116447;}}
    .login-btn{{width:100%;background:var(--lime);color:#091810;border:none;border-radius:6px;padding:11px;font-weight:700;font-size:14px;cursor:pointer;margin-top:6px;}}
    .login-btn:hover{{opacity:.9;}}
    .login-error{{display:none;color:var(--red);font-size:12px;margin-top:10px;text-align:center;}}
    .setup-msg{{color:var(--amber);font-size:12px;line-height:1.6;background:#1a1200;border:1px solid #3d2e00;border-radius:7px;padding:14px;}}
    .setup-msg code{{display:block;margin-top:8px;background:#0a0a00;padding:6px 8px;border-radius:4px;font-size:11px;word-break:break-all;}}
    #admin-content{{display:none;}}
    .topbar{{position:sticky;top:0;z-index:5;display:flex;align-items:center;justify-content:space-between;gap:16px;min-height:60px;padding:0 clamp(16px,3vw,36px);background:var(--dark);border-bottom:1px solid var(--line);}}
    .brand{{display:flex;gap:10px;align-items:center;font-weight:800;font-size:18px;color:white;text-decoration:none;flex-shrink:0;}}
    .brand-mark{{width:30px;height:30px;display:grid;place-items:center;border-radius:7px;color:var(--dark);background:var(--lime);font-size:14px;}}
    nav{{display:flex;gap:4px;overflow-x:auto;overflow-y:hidden;-webkit-overflow-scrolling:touch;scrollbar-width:none;}}
    nav::-webkit-scrollbar{{display:none;}}
    nav a{{color:#d5ded8;text-decoration:none;font-size:13px;font-weight:600;padding:9px 10px;border-radius:6px;white-space:nowrap;flex-shrink:0;}}
    nav a:hover{{background:#162b20;color:white;}}
    .topbar-right{{display:flex;align-items:center;gap:12px;flex-shrink:0;}}
    .topbar-badge{{font-size:11px;color:var(--muted);font-weight:600;white-space:nowrap;}}
    .logout-btn{{background:transparent;border:1px solid var(--line);color:var(--muted);padding:6px 12px;border-radius:5px;font-size:12px;cursor:pointer;font-weight:600;}}
    .logout-btn:hover{{color:white;border-color:#627067;}}
    .wrap{{max-width:1200px;margin:0 auto;padding:28px clamp(14px,3vw,32px) 60px;}}
    .page-title{{font-size:22px;font-weight:800;margin-bottom:4px;color:white;}}
    .page-sub{{color:var(--muted);font-size:13px;margin-bottom:24px;}}
    .pills{{display:grid;grid-template-columns:repeat(auto-fill,minmax(148px,1fr));gap:10px;margin-bottom:24px;}}
    .pill{{background:var(--panel);border:1px solid var(--line);border-radius:9px;padding:14px 16px;}}
    .pill-val{{font-size:26px;font-weight:800;line-height:1;margin-bottom:4px;}}
    .pill-lbl{{font-size:11px;color:var(--muted);}}
    .two-col{{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:20px;}}
    .card{{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:18px 20px;}}
    .card-title{{font-size:13px;font-weight:700;color:white;margin-bottom:14px;padding-bottom:10px;border-bottom:1px solid var(--line);}}
    .rrow{{display:flex;justify-content:space-between;padding:7px 0;border-bottom:1px solid var(--line);font-size:13px;}}
    .rrow:last-child{{border-bottom:none;}}
    .rrow-lbl{{color:var(--muted);}}
    .rrow-val{{font-weight:600;}}
    .tw-table{{width:100%;border-collapse:collapse;font-size:13px;}}
    .tw-table th{{background:#091810;padding:8px 10px;text-align:left;color:var(--muted);font-weight:600;border-bottom:1px solid var(--line);white-space:nowrap;}}
    .tw-table td{{padding:7px 10px;border-bottom:1px solid #0a1812;}}
    .tw-meta{{font-size:12px;color:var(--muted);margin-bottom:12px;}}
    .tw-warn{{color:var(--amber);}}
    .tools-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(190px,1fr));gap:8px;}}
    .tool-link{{display:block;padding:10px 14px;background:#091810;border:1px solid var(--line);border-radius:6px;color:var(--lime);text-decoration:none;font-size:13px;font-weight:600;}}
    .tool-link:hover{{background:#0f2018;border-color:#116447;}}
    .ext-row{{display:flex;gap:10px;flex-wrap:wrap;}}
    .ext-btn{{display:inline-flex;align-items:center;padding:10px 16px;border-radius:7px;font-size:13px;font-weight:600;text-decoration:none;border:1px solid var(--line);color:var(--ink);background:#091810;}}
    .ext-btn:hover{{background:#0f2018;border-color:#116447;}}
    @media(max-width:680px){{
      .topbar{{flex-direction:column;align-items:stretch;padding:11px 16px 0;gap:0;min-height:unset;}}
      .brand{{padding-bottom:8px;}}
      nav{{border-top:1px solid var(--line);padding:7px 0 0;justify-content:flex-start;}}
      .topbar-right{{border-top:1px solid var(--line);padding:7px 0 9px;justify-content:space-between;}}
      .two-col{{grid-template-columns:1fr;}}
      .pills{{grid-template-columns:repeat(2,1fr);}}
    }}
  </style>
</head>
<body>

<div id="login-gate">
  <div class="login-box">
    <div class="login-logo">
      <span class="login-mark">11</span>
      <div><div class="login-title">metric11</div><div class="login-sub">Yönetici Girişi</div></div>
    </div>
    {login_body}
  </div>
</div>

<div id="admin-content">
  <div class="topbar">
    <a class="brand" href="football_intelligence_home.html"><span class="brand-mark">11</span> metric11</a>
    <nav>
      <a href="football_intelligence_home.html">Merkez</a>
      <a href="football_command_center_2025_2026.html">Analiz</a>
      <a href="besiktas_2025_2026_dashboard_chronological.html">Maç Önü</a>
      <a href="transfer_recommendation_report_2025_2026.html">Scout</a>
      <a href="all_teams_preview_dashboard_2025_2026.html">Lig</a>
    </nav>
    <div class="topbar-right">
      <span class="topbar-badge">Yönetici</span>
      <button class="logout-btn" onclick="logout()">Çıkış</button>
    </div>
  </div>

  <div class="wrap">
    <div class="page-title">Yönetici Paneli</div>
    <div class="page-sub">Son güncelleme: {gen_at}</div>

    <div class="pills">
      <div class="pill">
        <div class="pill-val" style="color:{p_color}">{p_ok}/{p_total}</div>
        <div class="pill-lbl">Pipeline başarılı</div>
      </div>
      <div class="pill">
        <div class="pill-val" style="color:{'#ef4444' if p_fail > 0 else '#22c55e'}">{p_fail}</div>
        <div class="pill-lbl">Hatalı komut</div>
      </div>
      <div class="pill">
        <div class="pill-val" style="color:{p_color};font-size:14px;padding-top:4px">{p_status}</div>
        <div class="pill-lbl">Pipeline durumu</div>
      </div>
      <div class="pill">
        <div class="pill-val" style="color:#22c55e">{news.get("total_articles", 0)}</div>
        <div class="pill-lbl">Toplam haber</div>
      </div>
      <div class="pill">
        <div class="pill-val" style="color:#3b82f6">{news.get("transfer_signals", 0)}</div>
        <div class="pill-lbl">Transfer iddiası</div>
      </div>
      <div class="pill">
        <div class="pill-val" style="color:#ef4444">{news.get("injury_signals", 0)}</div>
        <div class="pill-lbl">Sakat sinyali</div>
      </div>
      <div class="pill">
        <div class="pill-val" style="color:#cde94e">{dq.get("score", 0)}/100</div>
        <div class="pill-lbl">Veri kalite skoru</div>
      </div>
      <div class="pill">
        <div class="pill-val" style="color:#22c55e">{official_total}</div>
        <div class="pill-lbl">Resmi web duyurusu</div>
      </div>
      <div class="pill">
        <div class="pill-val" style="color:#a78bfa">{tw_total}</div>
        <div class="pill-lbl">X gönderisi</div>
      </div>
    </div>

    <div class="two-col">
      <div class="card">
        <div class="card-title">Pipeline Detayları</div>
        <div class="rrow"><span class="rrow-lbl">Durum</span><span class="rrow-val" style="color:{p_color}">{p_status}</span></div>
        <div class="rrow"><span class="rrow-lbl">Başarılı / Toplam</span><span class="rrow-val">{p_ok} / {p_total}</span></div>
        <div class="rrow"><span class="rrow-lbl">Hatalı komut</span><span class="rrow-val" style="color:{'#ef4444' if p_fail > 0 else 'inherit'}">{p_fail}</span></div>
        <div class="rrow"><span class="rrow-lbl">Son çalışma</span><span class="rrow-val">{p_run}</span></div>
      </div>
      <div class="card">
        <div class="card-title">Veri Özeti</div>
        <div class="rrow"><span class="rrow-lbl">Toplam maç</span><span class="rrow-val">{len(matches)}</span></div>
        <div class="rrow"><span class="rrow-lbl">Skorlu maç</span><span class="rrow-val">{len(scored)}</span></div>
        <div class="rrow"><span class="rrow-lbl">Tahmin kaydı</span><span class="rrow-val">{len(model.get("rows", []))}</span></div>
        <div class="rrow"><span class="rrow-lbl">Haber / Analiz</span><span class="rrow-val">{news.get("analyzed_articles", 0)} / {news.get("total_articles", 0)}</span></div>
        <div class="rrow"><span class="rrow-lbl">Resmi web taraması</span><span class="rrow-val">{official_total} duyuru · {official_success}/{official_configured} site · {official_status}</span></div>
        <div class="rrow"><span class="rrow-lbl">Haber son güncelleme</span><span class="rrow-val">{escape(_fmt(news.get("generated_at")))}</span></div>
      </div>
    </div>

    {pipeline_fail_section}

    <div class="card" style="margin-bottom:20px">
      <div class="card-title">Ziyaretçi Analitiği</div>
      <p style="font-size:13px;color:var(--muted);margin-bottom:14px">Sayfa görüntüleme, benzersiz ziyaretçi ve coğrafi dağılım Vercel Analytics'te.</p>
      <div class="ext-row">
        <a class="ext-btn" href="https://vercel.com/alicans-projects-02042cb7/metric11/analytics" target="_blank">Vercel Analytics'i Aç →</a>
        <a class="ext-btn" href="https://github.com/alican-thumb/metric11/actions" target="_blank">GitHub Actions →</a>
      </div>
    </div>

    <div class="card" style="margin-bottom:20px">
      <div class="card-title">Twitter/X Kaynakları — {len(tw_accounts) or "30 yapılandırılmış"} hesap</div>
      {tw_notice}
      <div style="overflow-x:auto">
        <table class="tw-table">
          <thead><tr><th>Handle</th><th>Hesap</th><th>Durum</th></tr></thead>
          <tbody>{tw_rows}</tbody>
        </table>
      </div>
    </div>

    <div class="card" style="margin-bottom:20px">
      <div class="card-title">Yönetici Araçları</div>
      <div class="tools-grid">{tool_links}</div>
    </div>
  </div>
</div>

<script>
const HASH = {hash_js};

async function sha256(text) {{
  const enc = new TextEncoder();
  const buf = await crypto.subtle.digest('SHA-256', enc.encode(text));
  return Array.from(new Uint8Array(buf)).map(b => b.toString(16).padStart(2,'0')).join('');
}}

async function checkAuth() {{
  if (!HASH) return;
  const email = (document.getElementById('admin-email').value || '').toLowerCase().trim();
  const pw = document.getElementById('admin-password').value;
  const h = await sha256(email + ':' + pw);
  if (h === HASH) {{
    sessionStorage.setItem('m11_admin', '1');
    showAdmin();
  }} else {{
    document.getElementById('auth-error').style.display = 'block';
  }}
}}

function showAdmin() {{
  document.getElementById('login-gate').style.display = 'none';
  document.getElementById('admin-content').style.display = 'block';
}}

function logout() {{
  sessionStorage.removeItem('m11_admin');
  document.getElementById('login-gate').style.display = 'flex';
  document.getElementById('admin-content').style.display = 'none';
}}

document.addEventListener('keydown', e => {{
  if (e.key === 'Enter' && HASH) {{
    const pw = document.getElementById('admin-password');
    if (pw && document.activeElement === pw) checkAuth();
  }}
}});

if (sessionStorage.getItem('m11_admin') === '1' && HASH) showAdmin();
</script>
  <script defer src="/_vercel/insights/script.js"></script>
</body>
</html>"""


if __name__ == "__main__":
    main()
