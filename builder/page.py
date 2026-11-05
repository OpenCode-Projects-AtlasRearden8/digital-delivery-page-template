"""Rendering helpers for the digital-delivery static template (stdlib only)."""

from __future__ import annotations

import html
from typing import Any

CASCADE_CSS = """:root {
  --ink: #1f2933;
  --muted: #52606d;
  --canvas: #fcfcfd;
  --surface: #ffffff;
  --line: #d9e2ec;
  --accent: #1a6b52;
  --accent-soft: #e7f4ef;
  --amber: #8a5a00;
  --amber-soft: #fff6e0;
}

* { box-sizing: border-box; }

body {
  margin: 0;
  padding: 2.5rem 1rem 4rem;
  background: var(--canvas);
  color: var(--ink);
  font: 1rem/1.6 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    Helvetica, Arial, sans-serif;
}

main {
  max-width: 44rem;
  margin: 0 auto;
}

h1 { font-size: 1.7rem; line-height: 1.25; margin: 0.2rem 0 0.4rem; }
h2 { font-size: 1.15rem; margin: 2.2rem 0 0.6rem; }
h3 { font-size: 1rem; margin: 1.2rem 0 0.3rem; }
p  { margin: 0.5rem 0; }

.brand {
  color: var(--muted);
  font-weight: 600;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.tagline { color: var(--muted); font-size: 1.05rem; }

.badge {
  display: inline-block;
  background: var(--accent-soft);
  color: var(--accent);
  border-radius: 999px;
  padding: 0.15rem 0.8rem;
  font-size: 0.85rem;
  font-weight: 600;
}

.card {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 1.2rem 1.4rem;
  margin: 1rem 0;
}

.card h2 { margin-top: 0; }

.download .file {
  display: flex;
  flex-direction: column;
  border: 1px solid var(--line);
  border-radius: 10px;
  padding: 1rem 1.2rem;
  margin: 0.8rem 0;
}

.download .file-label { font-weight: 700; }

.download .file-meta { color: var(--muted); font-size: 0.9rem; margin-top: 0.1rem; }

.download .button {
  display: inline-block;
  background: var(--accent);
  color: #fff;
  text-decoration: none;
  border-radius: 8px;
  padding: 0.55rem 1.1rem;
  font-weight: 600;
  margin: 0.6rem 0 0;
}

.download .button:focus-visible,
.download .button:hover { background: #14573f; }

ol.next-steps { margin: 0.4rem 0 0; padding-left: 1.3rem; }
ol.next-steps li { margin: 0.35rem 0; }

ul.license-list { margin: 0.3rem 0; padding-left: 1.3rem; }

.may li::marker { content: "+ "; color: var(--accent); }
.may-not li::marker { content: "- "; color: var(--muted); }

.note-block {
  background: var(--amber-soft);
  border: 1px solid #f0dfae;
  border-radius: 10px;
  padding: 1rem 1.2rem;
}

.note-block h2 { margin-top: 0; }
.note-block p { color: var(--amber); font-size: 0.95rem; }

.updated {
  color: var(--muted);
  font-size: 0.85rem;
  border-top: 1px solid var(--line);
  padding-top: 1rem;
  margin-top: 2.4rem;
}

footer { margin-top: 1rem; color: var(--muted); font-size: 0.9rem; }
footer a { color: var(--accent); }

.index-list { list-style: none; padding: 0; margin: 1rem 0; }
.index-list li { margin: 0.6rem 0; }
.index-list a { color: var(--accent); font-weight: 600; text-decoration: none; }
.index-list a:hover { text-decoration: underline; }
"""


def _esc(value: Any) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def _footer(store: dict, product: dict) -> str:
    support = product.get("support") or store.get("support") or {}
    site_url = store.get("site_url", "")
    store_name = store.get("name", "")
    site_link = ""
    if site_url:
        label = _esc(store_name) if store_name else _esc(site_url)
        site_link = f' <a href="{_esc(site_url)}">{label}</a>'
    else:
        site_link = f" {_esc(store_name)}"
    return (
        f'<footer>Support:{site_link}'
        f' &middot; <a href="mailto:{_esc(support.get("email", ""))}">'
        f'{_esc(support.get("email", ""))}</a></footer>\n'
    )


def _download_block(files: list[dict]) -> str:
    lines = ['<section class="download card">', "<h2>Your download files</h2>"]
    for f in files:
        label = _esc(f["label"])
        filename = _esc(f["filename"])
        url = _esc(f["url"])
        size = _esc(f["size"])
        fmt = _esc(f["format"])
        note = _esc(f["note"])
        lines.append('<div class="file">')
        lines.append(f'<span class="file-label">{label}</span>')
        lines.append(
            f'<span class="file-meta">{filename} &middot; {size} &middot; {fmt} &middot; {note}</span>'
        )
        lines.append(
            f'<a class="button" href="{url}" download="{filename}">Download {label}</a>'
        )
        lines.append("</div>")
    lines.append("</section>")
    return "\n".join(lines)


def _license_block(lic: dict) -> str:
    may_items = "\n".join(
        f"      <li>{_esc(item)}</li>" for item in lic.get("may", [])
    )
    may_not_items = "\n".join(
        f"      <li>{_esc(item)}</li>" for item in lic.get("may_not", [])
    )
    return "\n".join(
        [
            '<section class="card">',
            "<h2>Your license</h2>",
            f'<span class="badge">{_esc(lic.get("type", ""))}</span>',
            f'<p>{_esc(lic.get("grant", ""))}</p>',
            "<h3>You may</h3>",
            '<ul class="license-list may">',
            may_items,
            "</ul>",
            "<h3>You may not</h3>",
            '<ul class="license-list may-not">',
            may_not_items,
            "</ul>",
            "</section>",
        ]
    )


def _refund_block(policy_text: str) -> str:
    return "\n".join(
        [
            '<section class="note-block">',
            "<h2>Refund policy</h2>",
            f"<p>{_esc(policy_text)}</p>",
            "</section>",
        ]
    )


def _format_block(note: str) -> str:
    return "\n".join(
        [
            '<section class="card">',
            "<h2>File sizes &amp; formats</h2>",
            f"<p>{_esc(note)}</p>",
            "</section>",
        ]
    )


def _support_block(support: dict) -> str:
    return "\n".join(
        [
            '<section class="card">',
            f"<h2>{_esc(support.get('title', 'Need support?'))}</h2>",
            f'<p>Email <a href="mailto:{_esc(support.get("email", ""))}">'
            f'{_esc(support.get("email", ""))}</a></p>',
            f"<p>{_esc(support.get('response_time', ''))}</p>",
            f"<p>{_esc(support.get('extra', ''))}</p>",
            "</section>",
        ]
    )


def render_product_page(store: dict, product: dict) -> str:
    """Render the thank-you/download page for one product entry."""
    title = _esc(product["title"])
    support = product.get("support") or store.get("support") or {}
    refund = product.get("refund_policy_override") or store.get(
        "default_refund_policy", ""
    )
    steps = "\n".join(
        f"    <li>{_esc(s)}</li>" for s in product.get("buyer_next_steps", [])
    )
    body = "\n".join(
        [
            "  <main>",
            f'  <p class="brand">{_esc(store.get("name", ""))}</p>',
            f"  <h1>{_esc(product['headline'])}</h1>",
            f'  <p class="tagline">{_esc(product["subhead"])}</p>',
            _download_block(product["files"]),
            '<section class="card">',
            "<h2>What to do next</h2>",
            '<ol class="next-steps">',
            steps,
            "</ol>",
            "</section>",
            _format_block(product.get("format_notes", "")),
            _license_block(product["license"]),
            _refund_block(refund),
            _support_block(support),
            f'  <p class="updated">Links last updated: {_esc(product["links_last_updated"])}</p>',
            "  </main>",
        ]
    )
    body += "\n" + _footer(store, product)
    head = (
        "<!DOCTYPE html>\n"
        '<html lang="en">\n'
        "<head>\n"
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"<title>{title} &mdash; {_esc(store.get('name', ''))}</title>\n"
        '<link rel="stylesheet" href="styles.css">\n'
        "</head>\n"
    )
    return head + "<body>\n" + body + "\n</body>\n</html>\n"


def render_index(store: dict) -> str:
    """Render a simple index page linking every product page."""
    items = []
    for product in store["products"]:
        items.append(
            f'    <li><a href="{_esc(product["id"])}.html">'
            f'{_esc(product["title"])}</a><br>'
            f'<small>{_esc(product["tagline"])}</small></li>'
        )
    body = "\n".join(
        [
            "  <main>",
            f'  <p class="brand">{_esc(store.get("name", ""))}</p>',
            "  <h1>Thank-you &amp; delivery pages</h1>",
            '  <p class="tagline">Pick the product page you need to share with your buyer.</p>',
            '  <ul class="index-list">',
            *items,
            "  </ul>",
            "  </main>",
        ]
    )
    head = (
        "<!DOCTYPE html>\n"
        '<html lang="en">\n'
        "<head>\n"
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"<title>Delivery pages &mdash; {_esc(store.get('name', ''))}</title>\n"
        '<link rel="stylesheet" href="styles.css">\n'
        "</head>\n"
    )
    return head + "<body>\n" + body + "\n</body>\n</html>\n"
