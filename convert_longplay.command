#!/bin/bash
# Drag-and-drop a .xlsx onto this .command, or run: ./convert_longplay.command "/path/to/file.xlsx"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PY="$SCRIPT_DIR/qc_longplay_convert.py"

if [ -z "$1" ]; then
  echo "Usage: $(basename "$0") \"/path/to/QC_Report.xlsx\""
  exit 1
fi

/usr/bin/env python3 "$PY" "$1"
