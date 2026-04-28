# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Project Does

Converts reel-based QC (Quality Control) report timecodes from an Excel `.xlsx` file into a continuous **long play** timeline starting at `01:00:00:00`. Applies per-reel frame corrections (Reel 1: +0f, Reel 2: +1f, Reel 3: +2f, etc.).

## Running the Converter

**CLI (primary interface):**
```bash
python qc_longplay_convert.py "My_QC_Report.xlsx" --sheet "QC Report" --fps 24 --lp-start "01:00:00:00"
# Output: My_QC_Report_LongPlay.xlsx
# Add --keep-markers to retain "Program Start/End" rows in output
```

**macOS one-click:**
```bash
chmod +x convert_longplay.command
./convert_longplay.command "/path/to/QC_Report.xlsx"
```

**Streamlit UI:** Unzip `streamlit_qc_longplay.zip`, then:
```bash
pip install -r streamlit_qc_longplay/requirements.txt
streamlit run streamlit_qc_longplay/app.py
```

**Jupyter:** Open `qc_longplay_template.ipynb` and set variables at the top (`INPUT_PATH`, `SHEET_NAME`, `FPS`, `LP_START_TC`, `DROP_MARKERS`).

## Architecture

All conversion logic lives in `qc_longplay_convert.py`. Key functions:

- `tc_to_td` / `td_to_tc` — timecode string ↔ `timedelta` conversion at a given FPS
- `build_intervals(df, fps, ...)` — scans the DataFrame for rows containing `"Program Start - Reel X"` / `"Program End - Reel X"` in **column index 3**, extracts timecodes from **column index 1**, and builds a list of `(reel, reel_start, reel_end, lp_cursor, duration)` intervals
- `convert_tc_corrected(tc_str, intervals, fps)` — maps a single reel timecode to its long-play equivalent using half-open interval matching
- `process(...)` — loads the Excel sheet (no header), converts TC columns 1 and 2, drops inter-reel marker rows by default, writes output sheet named `"<sheet> LongPlay"`

## Input Format Assumptions

- Excel sheet read with `header=None` (raw row layout preserved)
- Reel boundary descriptors in **column 3** (0-based): `"Program Start - Reel X"` / `"Program End - Reel X"`
- Timecodes in **columns 1 and 2** (0-based), format `HH:MM:SS:FF`
- Default sheet name: `"QC Report"`, default FPS: `24`

## Dependencies

`pandas`, `openpyxl` (for Excel I/O). No `requirements.txt` at root — install manually or via the Streamlit subfolder's `requirements.txt`.
