"""Shared HTML page utilities for metric11 report pages."""
from __future__ import annotations

import re
from html import escape


_CSS = """
    :root {
      --bg:#f3f5f4; --panel:#fff; --ink:#132018; --muted:#627067; --line:#d7ded9;
      --red:#bd2936; --green:#116447; --lime:#cde94e; --blue:#22618c; --dark:#091810; --soft:#e8eee9;
    }
    * { box-sizing:border-box; }
    body { margin:0; font-family:Inter,"Segoe UI",Arial,sans-serif; background:var(--bg); color:var(--ink); }
    .topbar { position:sticky; top:0; z-index:5; display:flex; align-items:center; justify-content:space-between; gap:20px; min-height:58px; padding:0 clamp(16px,4vw,42px); background:var(--dark); color:white; border-bottom:2px solid #1a3023; }
    .brand { display:flex; gap:10px; align-items:center; font-weight:800; font-size:18px; color:white; text-decoration:none; flex-shrink:0; letter-spacing:-0.2px; }
    .brand:visited,.brand:active,.brand:hover { color:white; }
    .brand-mark { width:28px; height:28px; display:grid; place-items:center; border-radius:6px; color:var(--dark); background:var(--lime); font-size:14px; font-weight:900; flex-shrink:0; }
    .season { color:#6b7c72; font-size:11px; font-weight:500; margin-left:2px; border-left:1px solid #2a3d30; padding-left:8px; }
    nav { display:flex; gap:2px; flex-wrap:nowrap; overflow-x:auto; overflow-y:hidden; justify-content:flex-end; -webkit-overflow-scrolling:touch; scrollbar-width:none; }
    nav::-webkit-scrollbar { display:none; }
    nav a { color:#8fa89a; text-decoration:none; font-size:13px; font-weight:600; padding:8px 11px; border-radius:6px; white-space:nowrap; flex-shrink:0; transition:background .15s,color .15s; }
    nav a:visited { color:#8fa89a; }
    nav a:hover { background:#162b20; color:white; }
    nav a.active { background:#162b20; color:white; }
    .back-link { display:inline-flex; align-items:center; gap:6px; color:var(--green); text-decoration:none; font-size:13px; font-weight:600; margin-bottom:18px; }
    .back-link::before { content:"←"; }
    .report-wrap { max-width:960px; margin:0 auto; padding:32px clamp(14px,3vw,32px) 60px; }
    .report-wrap h1 { font-size:28px; margin:0 0 6px; line-height:1.15; }
    .report-wrap h2 { font-size:19px; margin:28px 0 10px; padding-bottom:6px; border-bottom:1px solid var(--line); }
    .report-wrap h3 { font-size:15px; margin:20px 0 8px; color:var(--muted); font-weight:700; }
    .report-wrap p { line-height:1.65; margin:0 0 12px; font-size:14px; }
    .report-wrap ul { padding-left:20px; margin:0 0 14px; }
    .report-wrap li { line-height:1.65; font-size:14px; margin-bottom:4px; }
    .report-wrap code { background:var(--soft); padding:1px 5px; border-radius:3px; font-size:12px; font-family:monospace; }
    .report-wrap em { font-style:italic; color:var(--muted); }
    .report-wrap strong { font-weight:700; }
    .md-table { width:100%; border-collapse:collapse; margin:0 0 18px; font-size:13px; overflow-x:auto; display:block; }
    .md-table th { background:var(--soft); font-weight:700; text-align:left; padding:7px 10px; border:1px solid var(--line); white-space:nowrap; }
    .md-table td { padding:6px 10px; border:1px solid var(--line); }
    .md-table tr:nth-child(even) td { background:#f8faf9; }
    @media (max-width:680px) { .topbar { position:static; flex-direction:column; align-items:stretch; padding:11px 16px 0; gap:0; min-height:unset; } .brand { padding-bottom:8px; } .season { display:none; } nav { justify-content:flex-start; border-top:1px solid #1e3228; padding:7px 0 9px; } .report-wrap h1 { font-size:22px; } }
    @media (max-width:600px) { .md-table th,.md-table td { padding:5px 6px; font-size:11px; } }
"""


_NAV = (
    '<div class="topbar">'
    '<a class="brand" href="/">'
    '<span class="brand-mark">11</span>'
    ' metric11'
    '<span class="season">S&#xfc;per Lig 2025/26</span>'
    '</a>'
    '<nav>'
    '<a href="/">G&#xfc;ndem</a>'
    '<a href="transfer_tracker_2025_2026.html">Transferler</a>'
    '<a href="all_teams_preview_dashboard_2025_2026.html">Ma&#xe7; &#xd6;n&#xfc;</a>'
    '<a href="transfer_recommendation_report_2025_2026.html">Scout</a>'
    '<a href="football_intelligence_home.html">Analiz</a>'
    '</nav>'
    '</div>'
)


def page_html(title: str, body_html: str, description: str = "Süper Lig maç tahminleri, scout analizleri ve transfer istihbaratı — metric11.") -> str:
    _t = escape(title)
    _d = escape(description)
    return (
        "<!doctype html>\n"
        '<html lang="tr">\n'
        "<head>\n"
        '  <meta charset="utf-8">\n'
        '  <meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"  <title>{_t} — metric11</title>\n"
        f'  <meta name="description" content="{_d}">\n'
        f'  <meta property="og:title" content="{_t} — metric11">\n'
        f'  <meta property="og:description" content="{_d}">\n'
        '  <meta property="og:image" content="/og-image.svg">\n'
        '  <meta property="og:type" content="website">\n'
        '  <meta name="twitter:card" content="summary_large_image">\n'
        '  <meta name="theme-color" content="#091810">\n'
        '  <link rel="icon" href="favicon.svg" type="image/svg+xml">\n'
        f"  <style>{_CSS}  </style>\n"
        "</head>\n"
        "<body>\n"
        f"  {_NAV}\n"
        '  <div class="report-wrap">\n'
        f'    <a class="back-link" href="/">Ana sayfaya d&#xf6;n</a>\n'
        f"    {body_html}\n"
        "  </div>\n"
        '  <script defer src="/_vercel/insights/script.js"></script>\n'
        "</body>\n"
        "</html>"
    )


def md_to_html(text: str) -> str:
    """Convert basic Markdown to HTML (headers, tables, lists, bold, italic, code, links)."""
    lines = text.split("\n")
    out: list[str] = []
    in_table = False
    header_closed = False
    in_list = False

    for line in lines:
        s = line.strip()

        if in_table and (not s or not s.startswith("|")):
            out.append("</tbody></table>")
            in_table = False
            header_closed = False
        if in_list and (not s or not s.startswith("- ")):
            out.append("</ul>")
            in_list = False

        if not s:
            out.append("")
            continue

        if s.startswith("### "):
            out.append(f"<h3>{_inline(s[4:])}</h3>")
        elif s.startswith("## "):
            out.append(f"<h2>{_inline(s[3:])}</h2>")
        elif s.startswith("# "):
            out.append(f"<h1>{_inline(s[2:])}</h1>")
        elif s.startswith("|"):
            cells = [c.strip() for c in s.split("|")[1:-1]]
            is_sep = all(re.match(r"^[-: ]+$", c) for c in cells if c)
            if is_sep:
                if not header_closed:
                    out.append("</tr></thead><tbody>")
                    header_closed = True
            elif not in_table:
                in_table = True
                header_closed = False
                out.append('<table class="md-table"><thead><tr>')
                for c in cells:
                    out.append(f"<th>{_inline(c)}</th>")
            else:
                out.append("<tr>")
                for c in cells:
                    out.append(f"<td>{_inline(c)}</td>")
                out.append("</tr>")
        elif s.startswith("- "):
            if not in_list:
                in_list = True
                out.append("<ul>")
            out.append(f"<li>{_inline(s[2:])}</li>")
        else:
            out.append(f"<p>{_inline(s)}</p>")

    if in_table:
        out.append("</tbody></table>")
    if in_list:
        out.append("</ul>")

    return "\n".join(out)


def _inline(text: str) -> str:
    text = escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![a-zA-Z0-9])_(.+?)_(?![a-zA-Z0-9])", r"<em>\1</em>", text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    return text
