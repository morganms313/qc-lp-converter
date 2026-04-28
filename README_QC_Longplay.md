# QC Long Play Converter

Converts reel-based QC report timecodes into a continuous long play timeline
starting at `01:00:00:00`, with per-reel frame corrections applied automatically
(Reel 1: +0f, Reel 2: +1f, Reel 3: +2f, …).

---

## Active Files

| File | Purpose |
|------|---------|
| `qc_longplay_convert.py` | Core conversion logic — all other interfaces use this |
| `gui.py` | Native desktop GUI (primary interface) |
| `QC_LongPlay.spec` | PyInstaller build config for the portable `.app` / `.exe` |
| `requirements.txt` | Python dependencies |
| `convert_longplay.command` | macOS one-click CLI wrapper |
| `convert_longplay.bat` | Windows one-click CLI wrapper |

---

## 1. Desktop GUI (recommended)

Run directly:
```bash
pip install -r requirements.txt
python3 gui.py
```

Or build a self-contained portable app (no Python install required):
```bash
pip install pyinstaller
pyinstaller QC_LongPlay.spec
# → dist/QC LongPlay Converter.app  (macOS)
# → dist/QC_LongPlay.exe            (Windows)
```

The GUI lets you pick the input `.xlsx`, configure sheet name, FPS, LP start
timecode, and whether to keep inter-reel markers. After conversion it offers a
**Reveal in Finder** button to jump straight to the output file.

---

## 2. Command Line

```bash
python3 qc_longplay_convert.py "My_QC_Report.xlsx" \
  --sheet "QC Report" \
  --fps 24 \
  --lp-start "01:00:00:00"
# Output: My_QC_Report_LongPlay.xlsx
```

Add `--keep-markers` to retain the `Program Start/End - Reel X` rows in output.

### One-click wrappers

**macOS** — drag an `.xlsx` onto `convert_longplay.command` in Finder, or run:
```bash
./convert_longplay.command "/path/to/QC_Report.xlsx"
```

**Windows:**
```bat
convert_longplay.bat "C:\path\to\QC_Report.xlsx"
```

---

## Input Format

- Excel sheet read with no header row (raw layout preserved)
- Reel boundary markers in **column 4** (0-based index 3):
  `"Program Start - Reel X"` / `"Program End - Reel X"`
- Timecodes in **columns 2–3** (0-based index 1–2), format `HH:MM:SS:FF`
- Default sheet name: `"QC Report"` — change with `--sheet` or in the GUI
- Default FPS: `24` — change with `--fps` or in the GUI

---

## Dependencies

```bash
pip install pandas openpyxl
```

`tkinter` is included with the macOS system Python. If using a third-party
Python distribution and `tkinter` is missing, install it via your package
manager (e.g. `brew install python-tk`).
