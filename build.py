#!/usr/bin/env python3
"""Build static digital-product delivery pages from a small JSON file.

Reads `data/products.json` and writes one HTML page per product into
`site/`, plus a shared stylesheet. No JavaScript is required on the
built pages — they are plain HTML + CSS, ready for GitHub Pages.

Usage:
    python build.py                      # uses data/products.json -> site/
    python build.py -o out_dir           # custom output directory
    python build.py -i fixture.json      # custom input JSON
"""

from __future__ import annotations

import argparse
import html
import importlib.util
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent


def _load_deps():
    """Load the shared stub-free dependency modules (pure stdlib only)."""
    build_dir = REPO_ROOT / "builder"
    spec = importlib.util.spec_from_file_location(
        "builder_page", build_dir / "page.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_products(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        data = json.load(fh)
    if "products" not in data or not isinstance(data["products"], list):
        raise ValueError("JSON must contain a top-level 'products' list.")
    if not data["products"]:
        raise ValueError("At least one product entry is required.")
    return data


def build_site(input_path: Path, output_dir: Path) -> list[Path]:
    deps = _load_deps()
    data = load_products(input_path)
    store = data.get("store", {})
    output_dir.mkdir(parents=True, exist_ok=True)

    written: list[Path] = []
    css_path = output_dir / "styles.css"
    css_path.write_text(deps.CASCADE_CSS, encoding="utf-8")
    written.append(css_path)

    for product in data["products"]:
        page_html = deps.render_product_page(store, product)
        page_path = output_dir / f"{product['id']}.html"
        page_path.write_text(page_html, encoding="utf-8")
        written.append(page_path)

    index_html = deps.render_index(data)
    index_path = output_dir / "index.html"
    index_path.write_text(index_html, encoding="utf-8")
    written.append(index_path)

    return written


def main() -> int:
    parser = argparse.ArgumentParser(description="Build delivery pages.")
    parser.add_argument(
        "-i",
        "--input",
        type=Path,
        default=REPO_ROOT / "data" / "products.json",
        help="Input JSON file (default: data/products.json)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=REPO_ROOT / "site",
        help="Output directory (default: site/)",
    )
    args = parser.parse_args()
    written = build_site(args.input, args.output)
    for path in written:
        print(f"wrote {path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
