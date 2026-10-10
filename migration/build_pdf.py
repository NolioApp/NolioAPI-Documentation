"""Render v1-to-v2.md to v1-to-v2.pdf (headless Chromium, Markdown parsed by marked)."""
import json
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).parent
SOURCE = HERE / 'v1-to-v2.md'
TARGET = HERE / 'migration-v1-to-v2.pdf'

CSS = """
@page { size: A4; margin: 16mm 14mm 18mm 14mm; }
:root { --primary: #1E64E6; --primary-lighter: #E8EFFC; --text: #333333; --muted: #797979; --line: #E8E8E8; }
* { box-sizing: border-box; }
body { font-family: 'Inter', system-ui, -apple-system, sans-serif; color: var(--text); font-size: 10pt; line-height: 1.5; margin: 0; }
.cover { display: flex; align-items: center; justify-content: space-between; border-bottom: 3px solid var(--primary); padding-bottom: 12px; margin-bottom: 8px; }
.cover img { height: 30px; }
.cover span { color: var(--muted); font-size: 9pt; }
h1 { color: var(--primary); font-size: 22pt; line-height: 1.2; margin: 16px 0 8px; }
h2 { color: var(--primary); font-size: 15pt; margin: 24px 0 8px; padding-top: 4px; break-after: avoid; }
h3 { font-size: 11.5pt; margin: 16px 0 6px; break-after: avoid; }
p, ul, ol { margin: 6px 0; }
li { margin: 2px 0; }
a { color: var(--primary); text-decoration: none; }
hr { border: none; border-top: 1px solid var(--line); margin: 16px 0; }
code { font-family: 'JetBrains Mono', ui-monospace, Menlo, monospace; font-variant-ligatures: none; font-size: 8.4pt; background: #F2F2F2; padding: 1px 4px; border-radius: 4px; overflow-wrap: anywhere; }
pre { background: #F8F8F8; border: 1px solid var(--line); border-radius: 8px; padding: 10px 12px; white-space: pre-wrap; overflow-wrap: anywhere; }
pre code { background: none; padding: 0; font-size: 8pt; }
table { width: 100%; border-collapse: collapse; margin: 8px 0 12px; font-size: 8.4pt; }
thead { display: table-header-group; }
tr { break-inside: avoid; }
th { background: var(--primary-lighter); color: var(--primary); text-align: left; font-weight: 600; }
th, td { border: 1px solid var(--line); padding: 5px 6px; vertical-align: top; overflow-wrap: break-word; }
td:first-child { min-width: 64px; }
td code, th code { font-size: 7.8pt; }
strong { color: #1A1A1A; }
"""

FOOTER = ('<div style="font-family:system-ui,-apple-system,sans-serif;font-size:7pt;color:#AAAAAA;width:100%;padding:0 14mm;display:flex;justify-content:space-between;">'
          '<span>Nolio API: migration guide from v1 to v2</span>'
          '<span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>')


def build() -> None:
    markdown_source = SOURCE.read_text()
    logo = (HERE / 'nolio_logo.svg').read_text()
    html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&family=JetBrains+Mono&display=swap" rel="stylesheet">
<style>{CSS}</style>
<script src="https://cdnjs.cloudflare.com/ajax/libs/marked/12.0.2/marked.min.js"></script></head>
<body><div class="cover">{logo.replace('<svg ', '<svg style="height:30px;width:auto" ', 1)}<span>API v2 migration guide</span></div>
<main id="content"></main>
<script>document.getElementById('content').innerHTML = marked.parse({json.dumps(markdown_source)}, {{gfm: true}});</script>
</body></html>"""
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel='chrome')
        page = browser.new_page()
        page.set_content(html, wait_until='networkidle')
        page.pdf(path=str(TARGET), format='A4', print_background=True, display_header_footer=True,
                 header_template='<div></div>', footer_template=FOOTER,
                 margin={'top': '16mm', 'bottom': '18mm', 'left': '14mm', 'right': '14mm'})
        browser.close()


if __name__ == '__main__':
    build()
