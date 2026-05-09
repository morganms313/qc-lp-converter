# QC Long Play Converter — HTML Calculator (Design)

Date: 2026-05-09
Status: Approved (pending spec review)

## Summary

Add a browser-based version of the QC Long Play Converter alongside the existing Python CLI, tkinter GUI, and Streamlit app. It will be a static, self-contained `web/` folder that runs entirely client-side and works on locked-down machines with no internet access.

## Goals

- Match the conversion behavior of `qc_longplay_convert.py` exactly (same column indices, same reel boundary detection, same per-reel frame correction, same forced final Program End TC).
- Run on locked-down post-production machines: no server, no internet, no installer, no Python.
- Simple UX: drop the file, click convert, download the result. Settings hidden behind an "Advanced" disclosure.
- Visual style matches the post-production domain: dark theme, monospace timecode displays.

## Non-Goals

- Output folder picker (browser sandbox doesn't allow this — downloads go to the user's default Downloads folder).
- Reveal-in-Finder (browser-only).
- Multi-file batch upload (one file at a time).
- Mobile responsiveness (desktop-only tool).
- Replacing the existing Python implementations — this is an additional surface, not a replacement.

## Architecture

Static-asset only. The whole thing is a folder you can copy to any machine and open `index.html` in a browser.

### File layout

```
web/
  index.html         markup and structure
  style.css          dark studio theme
  qc_longplay.js     pure JS port of conversion logic (no DOM)
  app.js             UI wiring (file handling, form, status, download)
  vendor/
    xlsx.full.min.js SheetJS, vendored locally (~1MB)
```

### Vendored SheetJS

SheetJS (`xlsx.full.min.js`) is checked into `web/vendor/` and referenced via a relative `<script src="vendor/xlsx.full.min.js">`. Rationale: target machines are locked-down edit-bay machines with restricted or no internet — a CDN dependency would prevent the page from loading. Cost is one ~1MB file in the repo; the benefit is a truly portable artifact.

### Module boundaries

- `qc_longplay.js` — pure functions, no DOM access. Exports the conversion API. Operates on plain JS arrays-of-arrays (the shape SheetJS produces). This isolation means it can be unit-tested without a browser environment, and its responsibilities are limited to timecode math and interval logic.
- `app.js` — owns the DOM. Reads form values, listens for drag/drop and file input, calls `qc_longplay.js` functions, renders status, triggers download. No conversion logic lives here.
- `style.css` — visual presentation only. No layout-affecting JS.

## JS Conversion Module (`qc_longplay.js`)

Direct one-to-one port of `qc_longplay_convert.py`. The Python `timedelta` is replaced with plain numbers representing seconds (a float). Frame counts stay integers.

### Public API

```js
// Timecode arithmetic
tcToSeconds(tc, fps)      // "01:00:00:12" + 24 → 3600.5
secondsToTc(s, fps)       // 3600.5 + 24 → "01:00:00:12"
framesToSeconds(n, fps)   // 12 + 24 → 0.5

// Conversion pipeline
buildIntervals(rows, opts)
  // rows: 2D array (the shape SheetJS produces with {header: 1, raw: false, defval: null})
  // opts: { fps, lpStartTc, descCol = 3, tcCol = 1 }
  // returns: { intervals, firstStart, lastEnd }

convertTc(tcStr, intervals, fps)
  // returns the LP timecode for a reel timecode, or null if outside any reel

processWorkbook(workbook, opts)
  // opts: { sheetName = "QC Report", fps = 24, lpStartTc = "01:00:00:00", dropMarkers = true }
  // returns: a new SheetJS workbook with the converted sheet
  // throws Error with a clear message if the sheet is missing or has no reel boundaries
```

### Behavioral parity with Python

- Reel boundary detection: rows whose column 3 contains `"Program Start - Reel N"` / `"Program End - Reel N"`, with the timecode in column 1 (0-indexed). Reel number parsed via `/Reel\s*(\d+)/`.
- Closed-interval matching: a TC is in reel N's range if `reelStart <= tc <= reelEnd` (matches Python's `closed` interval — last frame of each reel is preserved).
- Per-reel frame correction: Reel N receives `+(N-1)` frames added to its LP timecode.
- Final Program End row: kept regardless of `dropMarkers`, with its timecode forced to `lastReelLpStart + lastReelDuration + lastReelCorrection + 1 frame` (matches Python's `program_end_lp_tc` calculation in [qc_longplay_convert.py](qc_longplay_convert.py)).
- Inter-reel markers: dropped when `dropMarkers === true` (default), kept otherwise.
- Row range scanned: from the first `Program Start - Reel X` row through the last `Program End - Reel X` row (inclusive). Within that range, rows are kept if they had TC conversions or have non-empty descriptor columns (indices 3-6); otherwise dropped. Inter-reel markers and the final Program End row follow the rules above.
- Output sheet name: `"<original sheet> LongPlay"`.

### Floating-point guard

Same rounding guard as Python: when converting seconds back to a timecode, if rounding produces `frames >= fps`, increment whole seconds and reset frames to 0. Prevents off-by-one frame errors at TC boundaries.

## UI (`index.html` + `app.js`)

Single page, vertical center column, max width ~640px.

### Layout (top to bottom)

1. **Header** — Title "QC Long Play Converter" + one-line tagline ("Convert reel-based QC timecodes to a continuous long play timeline.").
2. **Drop zone** — Large card with dashed border, accepts drag/drop. Click anywhere on it to open a file picker (hidden `<input type="file" accept=".xlsx">`). After a file is selected, the card collapses to show: filename, file size, "Change file" link.
3. **Convert button** — Primary, full-width. Disabled until a file is selected. While running, shows "Converting…" with disabled state.
4. **Status panel** — Hidden until conversion is attempted. On success, shows: number of reels detected, an interval table (reel #, source range, LP range, duration), and a green "Done" line. On error, shows the error message in an error-styled card.
5. **Download button** — Hidden until success. Filled amber, downloads the result via a blob URL with filename `<originalStem>_LongPlay.xlsx`.
6. **Advanced settings** — `<details>` element, closed by default, summary "Advanced settings". When expanded:
   - Sheet name (text input, default `QC Report`)
   - FPS (`<select>`: 24, 25, 30, default 24)
   - LP start TC (text input, default `01:00:00:00`, with `HH:MM:SS:FF` placeholder and inline validation)
   - Keep markers (checkbox, default unchecked)

### Interactions

- Drag enter on drop zone → accent border glow + accent-tinted background.
- Drag leave / drop → reset.
- Drop a non-`.xlsx` → status panel shows "Please drop an .xlsx file".
- Drop multiple files → take the first one (matches the tkinter GUI).
- Convert click → reads form values, calls `processWorkbook`, renders the status panel, surfaces the download button.
- Change file → resets the status panel and the download button.

### Form validation

- LP start TC: validated against `^\d{2}:\d{2}:\d{2}:\d{2}$` on convert click; invalid input shows an inline error and blocks conversion.
- Sheet name: empty string falls back to `QC Report`.
- FPS: dropdown only, no free-text input.

## Aesthetic — Studio/Post-Production Dark

### Palette

| Role | Color |
|---|---|
| Background | `#0E1014` |
| Surface (cards) | `#181B22` |
| Border | `#272B35` |
| Text primary | `#E6E8EC` |
| Text muted | `#8A91A0` |
| Accent (amber) | `#E5A93A` |
| Accent hover | `#F4BC4E` |
| Success | `#5DBE8A` |
| Error | `#E8635A` |

### Typography

System fonts only — no web font files are shipped, since the page must work fully offline. Browser falls back through each stack until it finds an installed font.

- UI stack: `-apple-system, BlinkMacSystemFont, "Segoe UI", Inter, Roboto, sans-serif` — picks up SF Pro on macOS, Segoe UI on Windows, Inter if installed.
- Monospace stack (timecodes, interval table, file size): `ui-monospace, SFMono-Regular, "JetBrains Mono", Menlo, Consolas, monospace` — picks up SF Mono on macOS, Consolas on Windows.

### Card and button styles

- Cards: 12px border-radius, 1px border `#272B35`, `#181B22` fill, subtle inner top highlight.
- Primary button: filled amber (`#E5A93A`), black text, 8px radius, 600 weight. Hover lightens to `#F4BC4E`. Disabled state: `#272B35` fill, muted text.
- Secondary actions ("Change file"): ghost — text-only with underline on hover.
- Drop zone: 2px dashed `#3A4050` border by default. Dragover: dashed `#E5A93A` border + 8% accent-tinted background.

## Error Handling

- File type not `.xlsx` → status panel: "Please select an .xlsx file."
- SheetJS fails to parse → status panel: "Couldn't read this file. Make sure it's a valid Excel workbook."
- Sheet name not found in workbook → status panel: `"Sheet '<name>' not found. Available sheets: <list>"`.
- No reel boundaries detected → status panel: "No reel boundaries found. Expected rows with 'Program Start - Reel X' and 'Program End - Reel X' in column 4 (0-based index 3)." Matches the Python error message.
- Invalid LP start TC → inline form error before conversion runs.
- Timecodes that don't match the `HH:MM:SS:FF` pattern in the data → silently passed through (matches Python: `convert_tc_corrected` returns the original string).

## Testing

- Manual verification on a known-good QC report: confirm output matches the Python version cell-for-cell (same descriptor columns, same converted timecodes, same kept/dropped rows).
- Smoke test: cover the four error paths above (wrong type, bad workbook, missing sheet, no reels).
- Browser targets: latest Chrome, Safari, Firefox, Edge on macOS and Windows.

No automated test harness is added in this scope — the conversion logic is small enough that a single golden-file comparison covers it. If divergence from the Python version is discovered, that's the bug to fix.

## Out of Scope

- Output folder picker (browser sandbox)
- Reveal-in-Finder
- Multi-file batch
- Mobile/responsive layout
- Replacing the Python implementations
- Automated cross-implementation parity tests (manual golden-file check is sufficient for now)
