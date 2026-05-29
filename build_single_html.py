#!/usr/bin/env python3
"""Build a single self-contained HTML file from the web/ sources.

Inlines style.css, vendor/xlsx.full.min.js, qc_longplay.js, and app.js into
web/index.html, producing a distributable one-file tool. The web/ folder
remains the maintainable source; re-run this whenever those files change.

Usage:
    python3 build_single_html.py
    # → QC-LongPlay-Converter.html  (in the project root)
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WEB = ROOT / "web"
OUTPUT = ROOT / "QC-LongPlay-Converter.html"


def read(rel: str) -> str:
    return (WEB / rel).read_text(encoding="utf-8")


def js_safe(js: str) -> str:
    # Prevent a stray "</script>" inside inlined JS from closing the block early.
    return js.replace("</script>", "<\\/script>")


def main() -> None:
    html = read("index.html")

    replacements = {
        '<link rel="stylesheet" href="style.css">':
            f"<style>\n{read('style.css')}\n</style>",
        '<script src="vendor/xlsx.full.min.js"></script>':
            f"<script>{js_safe(read('vendor/xlsx.full.min.js'))}</script>",
        '<script src="qc_longplay.js"></script>':
            f"<script>{js_safe(read('qc_longplay.js'))}</script>",
        '<script src="app.js"></script>':
            f"<script>{js_safe(read('app.js'))}</script>",
    }

    for tag, inline in replacements.items():
        if tag not in html:
            raise SystemExit(f"Expected tag not found in index.html: {tag}")
        html = html.replace(tag, inline)

    OUTPUT.write_text(html, encoding="utf-8")
    kb = OUTPUT.stat().st_size / 1024
    print(f"Wrote {OUTPUT.name} ({kb:.0f} KB) — single self-contained file.")


if __name__ == "__main__":
    main()
