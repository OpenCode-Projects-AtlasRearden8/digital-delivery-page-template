# Digital Delivery Page Template

A copy-ready, static, no-JavaScript template for delivering sold digital
products: generate thank-you / download pages from one small JSON file and
drop the output on GitHub Pages. Built by **Asdale Dynamics, LLC** and
released under the MIT License; it pairs well with the
selling-digital-products-guide and any digital-product store (Gumroad,
Payhip, KDP, itch.io, etc.).

## What each product page includes

- A warm thank-you headline and subhead
- Download buttons for every file, with filename, file size, and format shown
- A "what to do next" checklist for the buyer
- File-size and format notes in plain English
- A license block: "You may" / "You may not" wording options
- A no-refund-with-what-you-got policy block (store default or per-product override)
- A support-contact block (email, response time, extra notes)
- A "Links last updated" stamp on every page

## Project layout

```
data/products.json     <- edit this: your store info + product entries
build.py               <- builds site/ from the JSON (Python 3, stdlib only)
builder/page.py        <- HTML rendering helpers
tests/test_render.py   <- pytest checks against fixture JSON
site/                  <- generated output (GitHub Pages-ready)
```

## Usage

1. Open `data/products.json` and edit the `store` block (name, site, support
   email) plus one entry per product under `products`.
2. Build:

   ```bash
   python3 build.py
   ```

   Pages are written to `site/`. For a custom input or output path:

   ```bash
   python3 build.py -i my-products.json -o public
   ```

3. Put your real downloadable files in `site/downloads/` (or change each
   file's `url` field to your CDN/bucket link).
4. Publish the output directory — GitHub Pages works as-is:
   go to Settings → Pages, choose "Deploy from a branch", and select the
   branch/folder containing `site/` output (index.html plus styles.css),
   or point a GitHub Actions workflow at the `site/` directory. No
   JavaScript editing is ever needed; pages are plain HTML + CSS.

## Product JSON fields

| Field                    | Meaning                                                        |
| ------------------------ | -------------------------------------------------------------- |
| `id`                     | URL-safe filename for the product page                         |
| `title`, `tagline`       | Listing title and one-line description                        |
| `headline`, `subhead`    | Thank-you page opener wording                                  |
| `buyer_next_steps`       | Numbered checklist shown under the downloads                   |
| `files`                  | `label`, `filename`, `url`, `size`, `format`, `note` per file  |
| `format_notes`           | One-paragraph file-size/format explainer                       |
| `license`                | `type`, `grant`, `may[]`, `may_not[]` wording                  |
| `refund_policy_override` | Optional custom no-refund text (falls back to store default)   |
| `support`                | Optional per-product support block (falls back to store block) |
| `links_last_updated`     | ISO date stamp printed on the page                             |

## Tests

```bash
python3 -m pip install -r requirements.txt
python3 -m pytest tests/
```

The suite builds pages from the fixture JSON and validates: well-formed
HTML, no JavaScript, download buttons for every file, license
may/may-not lists, refund wording (default and override), format notes,
support blocks, the updated stamp, index links, and absence of secret
key material.

## Status

See [STATUS.md](STATUS.md) for the current state, verification results,
and known gaps.

## License & credits

MIT License — Copyright (c) 2026 Asdale Dynamics, LLC. This template is a
free, open-source tool the LLC publishes for beginner-friendly authors and
small sellers. Dylan Asdale (The Massive AI Manual) explains AI "like a
friend would" at dylanasdale.github.io.
