"""Tests validating rendered delivery pages built from fixture JSON."""

from __future__ import annotations

import html
import html.parser
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from build import build_site  # noqa: E402
from builder.page import (  # noqa: E402
    CASCADE_CSS,
    _download_block,
    _format_block,
    _license_block,
    _refund_block,
    _support_block,
    render_index,
    render_product_page,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
VOID_TAGS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}


class WellFormedParser(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.stack: list[str] = []
        self.anchors: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID_TAGS:
            self.stack.append(tag)
        if tag == "a":
            self.anchors.append(dict(attrs).get("href", ""))

    def handle_endtag(self, tag):
        if tag in VOID_TAGS:
            return
        assert self.stack, f"unexpected closing tag {tag!r}"
        assert self.stack[-1] == tag, (
            f"mismatched </{tag}>, expected </{self.stack[-1]}>"
        )
        self.stack.pop()


def parse_well_formed(html_text: str) -> WellFormedParser:
    parser = WellFormedParser()
    parser.feed(html_text)
    parser.close()
    assert not parser.stack, f"unclosed tags: {parser.stack}"
    return parser


@pytest.fixture(scope="session")
def built(tmp_path_factory) -> Path:
    out = tmp_path_factory.mktemp("site")
    build_site(REPO_ROOT / "data" / "products.json", out)
    return out


@pytest.fixture()
def all_pages(built) -> list[tuple[str, str]]:
    pages = []
    for path in sorted(built.glob("*.html")):
        pages.append((path.name, path.read_text(encoding="utf-8")))
    return pages


# ---------------------------------------------------------------------------
# Rendered pages are valid, well-formed HTML
# ---------------------------------------------------------------------------


def test_all_pages_are_well_formed_html(all_pages):
    assert all_pages, "no HTML pages were rendered"
    for name, text in all_pages:
        parse_well_formed(text)


def test_all_pages_reference_shared_stylesheet(all_pages):
    for name, text in all_pages:
        assert '<link rel="stylesheet" href="styles.css">' in text
        assert "<script" not in text.lower(), f"{name} unexpectedly contains JS"


def test_stylesheet_written_and_nonempty(built):
    css = (built / "styles.css").read_text(encoding="utf-8")
    assert ".download" in css and ".updated" in css


def test_stylesheet_constant_matches_written_file(built):
    assert CASCADE_CSS == (built / "styles.css").read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Every product page contains the required sections
# ---------------------------------------------------------------------------


def product_pages(all_pages):
    return [(n, t) for n, t in all_pages if n != "index.html"]


def test_every_product_has_thank_you_headline(all_pages):
    data = json.loads((REPO_ROOT / "data" / "products.json").read_text())
    pages = dict(all_pages)
    for product in data["products"]:
        text = pages[f"{product['id']}.html"]
        assert product["headline"] in text
        assert product["subhead"] in text


def test_download_buttons_render_for_every_file(built):
    data = json.loads((REPO_ROOT / "data" / "products.json").read_text())
    for product in data["products"]:
        text = (built / f"{product['id']}.html").read_text(encoding="utf-8")
        for f in product["files"]:
            expected = (
                f'<a class="button" href="{f["url"]}" download="{f["filename"]}">'
            )
            assert expected in text, f"missing download button for {f['filename']}"
            assert f["size"] in text and f["format"] in text


def test_download_block_html_is_well_formed():
    files = [
        {
            "label": "Guide (PDF)",
            "filename": "guide.pdf",
            "url": "downloads/guide.pdf",
            "size": "1 MB",
            "format": "PDF",
            "note": "Ok",
        }
    ]
    parse_well_formed(_download_block(files))


# ---------------------------------------------------------------------------
# License + refund wording options
# ---------------------------------------------------------------------------


def test_license_type_and_grant_present(built):
    data = json.loads((REPO_ROOT / "data" / "products.json").read_text())
    for product in data["products"]:
        text = (built / f"{product['id']}.html").read_text(encoding="utf-8")
        assert product["license"]["type"] in text
        assert product["license"]["grant"] in text


def test_license_lists_render_may_and_may_not():
    lic = {
        "type": "Single Buyer",
        "grant": "g",
        "may": ["keep it"],
        "may_not": ["resell it"],
    }
    block = _license_block(lic)
    assert '<ul class="license-list may">' in block
    assert "<li>keep it</li>" in block
    assert '<ul class="license-list may-not">' in block
    assert "<li>resell it</li>" in block


def test_refund_policy_present_on_every_page(built):
    data = json.loads((REPO_ROOT / "data" / "products.json").read_text())
    for product in data["products"]:
        text = (built / f"{product['id']}.html").read_text(encoding="utf-8")
        assert "<h2>Refund policy</h2>" in text
        assert "all sales are final" in text.lower()


def test_refund_override_wins_over_store_default():
    store = {"default_refund_policy": "default wording", "name": "X"}
    product = {"title": "T", "headline": "h", "subhead": "s", "files": [],
               "license": {"type": "t", "grant": "g", "may": [], "may_not": []},
               "refund_policy_override": "custom no-refund wording here",
               "support": {}, "links_last_updated": "2026-01-01"}
    page = render_product_page(store, product)
    assert "custom no-refund wording here" in page
    assert "default wording" not in page


def test_refund_falls_back_to_store_default():
    store = {"default_refund_policy": "default wording", "name": "X"}
    product = {"title": "T", "headline": "h", "subhead": "s", "files": [],
               "license": {"type": "t", "grant": "g", "may": [], "may_not": []},
               "refund_policy_override": None,
               "support": {}, "links_last_updated": "2026-01-01"}
    page = render_product_page(store, product)
    assert "default wording" in page


# ---------------------------------------------------------------------------
# File-size / format notes + support block + updated stamp
# ---------------------------------------------------------------------------


def test_format_notes_block_present(built):
    data = json.loads((REPO_ROOT / "data" / "products.json").read_text())
    for product in data["products"]:
        text = (built / f"{product['id']}.html").read_text(encoding="utf-8")
        assert "<h2>File sizes &amp; formats</h2>" in text
        assert html.escape(product["format_notes"], quote=True) in text


def test_format_block_escaped():
    block = _format_block("a < b & c")
    assert "a &lt; b &amp; c" in block


def test_support_block_renders_store_contact(built):
    data = json.loads((REPO_ROOT / "data" / "products.json").read_text())
    support = data["store"]["support"]
    for product in data["products"]:
        text = (built / f"{product['id']}.html").read_text(encoding="utf-8")
        assert support["email"] in text
        assert f'mailto:{support["email"]}' in text
        assert support["response_time"] in text


def test_support_block_uses_product_override():
    support = {"title": "Custom title", "email": "a@b.c",
               "response_time": "slow", "extra": "hello"}
    store_support = {"title": "Store default", "email": "d@e.f",
                     "response_time": "fast", "extra": "x"}
    product = {"title": "T", "headline": "h", "subhead": "s", "files": [],
               "license": {"type": "t", "grant": "g", "may": [], "may_not": []},
               "support": support, "links_last_updated": "2026-01-01"}
    page = render_product_page({"name": "X", "support": store_support}, product)
    assert "Custom title" in page and "d@e.f" not in page
    parse = parse_well_formed(page)
    assert "mailto:a@b.c" in parse.anchors
    assert _support_block(support)  # smoke: helper callable


def test_links_last_updated_stamp_on_every_product_page(built):
    data = json.loads((REPO_ROOT / "data" / "products.json").read_text())
    for product in data["products"]:
        text = (built / f"{product['id']}.html").read_text(encoding="utf-8")
        assert f"Links last updated: {product['links_last_updated']}" in text


# ---------------------------------------------------------------------------
# Index page + escaping + fallbacks
# ---------------------------------------------------------------------------


def test_index_links_to_all_products(built):
    data = json.loads((REPO_ROOT / "data" / "products.json").read_text())
    text = (built / "index.html").read_text(encoding="utf-8")
    for product in data["products"]:
        assert f'href="{product["id"]}.html"' in text
    parse = parse_well_formed(text)
    assert parse.anchors, "index has no links"


def test_index_render_helper_is_well_formed():
    store = {"name": "Somewhere &amp; Sons", "site_url": "https://x.example"}
    data = {
        "products": [
            {
                "id": "p1",
                "title": "Thing <1>",
                "tagline": "a < b",
                "headline": "Thanks & enjoy!",
                "subhead": "s",
                "files": [],
                "license": {"type": "l", "grant": "g", "may": [], "may_not": []},
                "support": {},
                "links_last_updated": "2026-01-01",
            }
        ]
    }
    product_page = render_product_page(store, data["products"][0])
    parse_well_formed(product_page)
    assert "Thing &lt;1&gt;" in product_page
    assert "Thanks &amp; enjoy!" in product_page

    index_page = render_index(data)
    parse_well_formed(index_page)
    assert "Thing &lt;1&gt;" in index_page


def test_index_requires_products_list(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"store": {}}))
    from build import load_products
    with pytest.raises(ValueError):
        load_products(bad)


def test_index_rejects_empty_product_list(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"store": {}, "products": []}))
    from build import load_products
    with pytest.raises(ValueError):
        load_products(bad)


def test_footer_links_store_site():
    from builder.page import _footer
    footer = _footer({"name": "X", "site_url": "https://x.example"}, {})
    assert 'href="https://x.example"' in footer
    parse = parse_well_formed(footer)


def test_no_secrets_or_keys_in_rendered_pages(all_pages):
    banned = ["api_key", "apikey", "secret", "password", "token", "sk-"]
    for name, text in all_pages:
        lowered = text.lower()
        for word in banned:
            assert word not in lowered, f"{name} may contain {word!r}"
