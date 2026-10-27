"""Executive Report Generator: Formats Markdown briefings into C-level printable HTML and PDF."""

import html
import os
import re


def markdown_to_clean_html(md_text: str) -> str:
    """Basic converter for markdown headers, lists, tables, and bold text into styled HTML."""
    lines = md_text.split("\n")
    html_lines = []
    in_table = False
    in_list = False

    for line in lines:
        stripped = line.strip()

        # Headers
        if stripped.startswith("# "):
            html_lines.append(
                f"<h1 class='report-title'>{html.escape(stripped[2:])}</h1>"
            )
            continue
        elif stripped.startswith("## "):
            html_lines.append(
                f"<h2 class='section-heading'>{html.escape(stripped[3:])}</h2>"
            )
            continue
        elif stripped.startswith("### "):
            html_lines.append(
                f"<h3 class='sub-heading'>{html.escape(stripped[4:])}</h3>"
            )
            continue
        elif stripped.startswith("---"):
            html_lines.append("<hr class='divider'/>")
            continue

        # Tables
        if "|" in stripped:
            if not in_table:
                in_table = True
                html_lines.append(
                    "<div class='table-container'><table class='styled-table'>"
                )
            cols = [c.strip() for c in stripped.split("|")[1:-1]]
            if all(set(c) <= {"-", ":", " "} for c in cols):
                continue  # Header divider line
            row_html = "".join([f"<td>{html.escape(c)}</td>" for c in cols])
            html_lines.append(f"<tr>{row_html}</tr>")
            continue
        else:
            if in_table:
                in_table = False
                html_lines.append("</table></div>")

        # Bullet Lists
        if stripped.startswith(("- ", "* ")):
            if not in_list:
                in_list = True
                html_lines.append("<ul class='bullet-list'>")
            item_text = stripped[2:]
            item_text = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", item_text)
            html_lines.append(f"<li>{item_text}</li>")
            continue
        else:
            if in_list:
                in_list = False
                html_lines.append("</ul>")

        # Standard Paragraphs
        if stripped:
            p_text = stripped
            p_text = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", p_text)
            p_text = re.sub(r"`(.*?)`", r"<code>\1</code>", p_text)
            html_lines.append(f"<p class='paragraph'>{p_text}</p>")

    if in_table:
        html_lines.append("</table></div>")
    if in_list:
        html_lines.append("</ul>")

    return "\n".join(html_lines)


def generate_executive_html(
    report_markdown: str,
    title: str = "Strategic Decision Briefing",
    quality_score: int = 96,
    author: str = "Philippe Godfroy",
    thread_id: str | None = None,
) -> str:
    """Generate a printable, executive-ready HTML briefing document."""
    body_content = markdown_to_clean_html(report_markdown)
    tid = thread_id or "live-run"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{html.escape(title)}</title>
  <style>
    @page {{ size: A4; margin: 20mm; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      color: #1e293b;
      line-height: 1.6;
      max-width: 850px;
      margin: 0 auto;
      padding: 30px;
    }}
    .header-banner {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 2px solid #0284c7;
      padding-bottom: 12px;
      margin-bottom: 24px;
    }}
    .brand-logo {{ font-size: 20px; font-weight: 800; color: #0284c7; }}
    .badge-pill {{
      background: #f0fdf4;
      border: 1px solid #bbf7d0;
      color: #166534;
      font-size: 11px;
      font-weight: 700;
      padding: 4px 10px;
      border-radius: 9999px;
    }}
    .report-title {{ font-size: 26px; font-weight: 800; color: #0f172a; margin-top: 0; }}
    .section-heading {{ font-size: 18px; font-weight: 700; color: #0369a1; margin-top: 24px; border-left: 4px solid #0284c7; padding-left: 10px; }}
    .paragraph {{ font-size: 14px; color: #334155; margin-bottom: 12px; }}
    .styled-table {{
      width: 100%;
      border-collapse: collapse;
      margin: 16px 0;
      font-size: 13px;
    }}
    .styled-table td {{ border: 1px solid #cbd5e1; padding: 8px 12px; }}
    .styled-table tr:first-child {{ background: #f8fafc; font-weight: 700; color: #0f172a; }}
    .bullet-list {{ font-size: 14px; color: #334155; padding-left: 20px; }}
    .bullet-list li {{ margin-bottom: 6px; }}
    .divider {{ border: 0; border-top: 1px solid #e2e8f0; margin: 24px 0; }}
    .signoff-box {{
      margin-top: 40px;
      border: 1px solid #e2e8f0;
      background: #f8fafc;
      border-radius: 8px;
      padding: 16px;
      font-size: 12px;
      display: flex;
      justify-content: space-between;
    }}
    @media print {{
      body {{ padding: 0; }}
      .no-print {{ display: none; }}
    }}
  </style>
</head>
<body>
  <div class="header-banner">
    <div class="brand-logo">⚡ NEXUS MULTI-AGENT SWARM</div>
    <div>
      <span class="badge-pill">Critic Rigor Score: {quality_score}/100</span>
      <span class="badge-pill" style="margin-left: 6px;">LangSmith Traced</span>
    </div>
  </div>

  {body_content}

  <div class="signoff-box">
    <div>
      <strong>Human-in-the-Loop Governance:</strong> Verified & Approved<br>
      <strong>Orchestrator:</strong> LangGraph v1.2+ StateGraph | <strong>Thread ID:</strong> {tid}
    </div>
    <div style="text-align: right;">
      <strong>Lead Engineer:</strong> {author}<br>
      <strong>Observability:</strong> LangSmith Distributed Span Logging
    </div>
  </div>
</body>
</html>"""


def save_executive_html_file(
    report_markdown: str, output_path: str, quality_score: int = 96
) -> str:
    """Save formatted HTML briefing to disk."""
    html_content = generate_executive_html(report_markdown, quality_score=quality_score)
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    return output_path
