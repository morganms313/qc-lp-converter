#!/usr/bin/env python3
"""Build a single self-contained HTML file from the web/ sources.

Inlines style.css, vendor/xlsx.full.min.js, qc_longplay.js, and app.js into
web/index.html, producing a distributable one-file tool. The web/ folder
remains the maintainable source; re-run this whenever those files change.

The version is read from the footer credit in web/index.html (single source
of truth) and stamped into the output filename, e.g.
QC-LongPlay-Converter_v1.0.1.html. Any previous build (versioned or not) is
deleted first, so only the current version ever exists on disk.

Usage:
    python3 build_single_html.py
    # → QC-LongPlay-Converter_v<version>.html  (in the project root)
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WEB = ROOT / "web"
OUTPUT_PREFIX = "QC-LongPlay-Converter"
# matches "QC-LongPlay-Converter.html" and "QC-LongPlay-Converter_v1.2.3.html"
OUTPUT_GLOB = f"{OUTPUT_PREFIX}*.html"
VERSION_RE = re.compile(r"Built by MS[^<]*?v(\d+(?:\.\d+)+)")


def read(rel: str) -> str:
    return (WEB / rel).read_text(encoding="utf-8")


def js_safe(js: str) -> str:
    # Prevent a stray "</script>" inside inlined JS from closing the block early.
    return js.replace("</script>", "<\\/script>")


def extract_version(html: str) -> str:
    m = VERSION_RE.search(html)
    if not m:
        raise SystemExit(
            "Could not find version in web/index.html footer "
            "(expected a 'Built by MS … v<x.y.z>' build-note)."
        )
    return m.group(1)


def main() -> None:
    html = read("index.html")
    version = extract_version(html)

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

    # Remove any prior build so old/stale versions can't linger.
    removed = []
    for old in sorted(ROOT.glob(OUTPUT_GLOB)):
        old.unlink()
        removed.append(old.name)

    output = ROOT / f"{OUTPUT_PREFIX}_v{version}.html"
    output.write_text(html, encoding="utf-8")
    kb = output.stat().st_size / 1024

    if removed:
        print("Removed old build(s): " + ", ".join(removed))
    print(f"Wrote {output.name} ({kb:.0f} KB) — single self-contained file (v{version}).")


if __name__ == "__main__":
    main()
