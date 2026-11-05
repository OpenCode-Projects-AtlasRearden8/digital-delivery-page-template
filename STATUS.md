# STATUS.md

## What was built

A copy-ready static template for delivering sold digital products:
one small JSON file (`data/products.json`) drives `build.py` to generate
plain HTML + CSS delivery pages — no JavaScript anywhere, nothing to edit
but JSON and wording.

- **builder/page.py** — rendering helpers: download section (buttons with
  filename/size/format), buyer next-steps checklist, file-size and format
  notes, license block with "You may / You may not" wording options,
  refund-policy block (store default or per-product override), support
  contact block, and a "Links last updated" stamp on every page.
- **build.py** — stdlib-only CLI: `python3 build.py` (optional `-i`/`-o`
  flags) writes `site/` with one page per product plus an index page and a
  shared `styles.css`.
- **tests/test_render.py** — 23 pytest checks validating rendered pages
  built from the fixture JSON: well-formed HTML, zero scripts, download
  buttons for every file, license may/may-not lists, refund wording
  (default + override fallback), format notes, support blocks (store +
  per-product), updated stamps, index links, escaping, and a scan for
  secret-ish strings.
- **data/products.json** — fixture data with 3 example products
  (book chapter pack, launch kit, paperwork pack) demonstrating license
  and refund wording options.
- **README.md** (credits Asdale Dynamics, LLC), **LICENSE** (MIT,
  Copyright (c) 2026 Asdale Dynamics, LLC), **requirements.txt**,
  **.gitignore**.

## How to run

```bash
python3 build.py                 # regenerate site/ from data/products.json
python3 -m pip install -r requirements.txt
python3 -m pytest tests/        # run the validation suite
python3 -m http.server -d site  # preview locally
```

GitHub Pages: point Pages (or an Actions workflow) at the `site/`
directory. Put real files in `site/downloads/` or change each file's
`url` field.

## Verification results

- `python3 build.py` — builds 3 product pages + index + styles.css
  cleanly. (Fixed during development: store info wasn't passed to page
  renderers, and a missing `</main>` closed tag — both caught by tests.)
- `python3 -m pytest tests/` — **23 passed**.
- All 5 site files served over `http.server` return HTTP 200.
- Static check: every rendered page parses as balanced, well-formed HTML
  (custom stdlib-parser check inside the test suite).
- Security sweep: no secrets, API keys, or personal data in the repo;
  product emails are placeholder example.com addresses.

## Known gaps

- Download file URLs point to placeholder paths (`downloads/…`); no
  dummy PDFs/EPUBs are shipped — drop real files into `site/downloads/`.
- Pages are English-only, no RTL/tracking-pixel/analytics support.
- No order/purchase verification — this is a static template, so the
  thank-you URL is accessible to anyone with the link.
- Refund wording options are pre-written text the seller adapts; this
  template is education only, not legal advice.
- pytest is not pinned in requirements.txt (pinned a minimum of >=8.0);
  run against Python 3.13.
