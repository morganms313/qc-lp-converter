#!/usr/bin/env python3
import re
import math
import argparse
from datetime import timedelta
from pathlib import Path
import pandas as pd


def _validate_fps(fps: int) -> None:
    if not isinstance(fps, (int, float)) or fps <= 0:
        raise ValueError(f"FPS must be a positive number, got {fps!r}")


def tc_to_td(tc: str, fps: int) -> timedelta | None:
    if not isinstance(tc, str):
        return None
    m = re.match(r"^(\d{2}):(\d{2}):(\d{2}):(\d{2})$", tc.strip())
    if not m:
        return None
    h, mi, s, f = map(int, m.groups())
    return timedelta(hours=h, minutes=mi, seconds=s, milliseconds=(f * 1000 / fps))


def frames_to_td(frames: int, fps: int) -> timedelta:
    return timedelta(seconds=frames / fps)


def td_to_tc(td: timedelta, fps: int) -> str:
    total = td.total_seconds()
    whole = math.floor(total)
    frac = total - whole
    frames = int(round(frac * fps))
    if frames >= fps:  # guard against floating-point rounding past the last frame
        frames = 0
        whole += 1
    h = int(whole // 3600)
    m = int((whole % 3600) // 60)
    s = int(whole % 60)
    return f"{h:02}:{m:02}:{s:02}:{frames:02}"


def build_intervals(df, fps: int, desc_col: int = 3, tc_col: int = 1,
                    lp_start_tc: str = "01:00:00:00"):
    """Scan df for 'Program Start/End - Reel X' rows and build LP interval table."""
    _validate_fps(fps)
    reel_bounds = {}
    current = None
    for i, row in df.iterrows():
        desc = str(row.get(desc_col, ""))
        tc = row.get(tc_col, None)
        if "Program Start - Reel" in desc:
            m = re.search(r"Reel\s*(\d+)", desc)
            if m and isinstance(tc, str):
                r = int(m.group(1))
                reel_bounds[r] = {"start_tc": tc, "end_tc": None, "start_row": i}
                current = r
        elif "Program End - Reel" in desc and current is not None:
            if isinstance(tc, str):
                reel_bounds[current]["end_tc"] = tc
                reel_bounds[current]["end_row"] = i
            current = None

    if not reel_bounds:
        raise RuntimeError(
            "No reel boundaries found. Expected rows with "
            "'Program Start - Reel X' / 'Program End - Reel X' in column 4 (0-based index 3)."
        )

    lp_cursor = tc_to_td(lp_start_tc, fps)
    intervals = []  # (reel, reel_start_td, reel_end_td, lp_cursor_td, duration_td)
    for r in sorted(reel_bounds.keys()):
        rs = tc_to_td(reel_bounds[r]["start_tc"], fps)
        re_ = tc_to_td(reel_bounds[r]["end_tc"], fps)
        if rs is None or re_ is None:
            raise RuntimeError(f"Invalid timecode for Reel {r} boundaries.")
        dur = re_ - rs
        intervals.append((r, rs, re_, lp_cursor, dur))
        lp_cursor = lp_cursor + dur

    first_start = min(b["start_row"] for b in reel_bounds.values())
    last_end = max(b["end_row"] for b in reel_bounds.values())
    return intervals, first_start, last_end


def convert_tc_corrected(tc_str: str, intervals: list, fps: int) -> str | None:
    """Map a reel timecode to its long-play equivalent.

    Uses closed intervals (rs <= td <= re_) so boundary frames are never silently
    dropped. Returns None only when the TC falls outside all known reel ranges.
    """
    td = tc_to_td(tc_str, fps)
    if td is None:
        return tc_str
    for r, rs, re_, lp_start, _dur in intervals:
        if rs <= td <= re_:  # closed — include the last frame of each reel
            offset = td - rs
            correction_frames = max(0, r - 1)  # Reel 1: +0f, Reel 2: +1f, …
            return td_to_tc(lp_start + offset + frames_to_td(correction_frames, fps), fps)
    return None  # TC is outside all reel intervals


def process(input_path, output_path=None, sheet_name: str = "QC Report",
            fps: int = 24, lp_start_tc: str = "01:00:00:00",
            drop_markers: bool = True) -> str:
    _validate_fps(fps)
    input_path = Path(input_path)

    # Load sheet raw (no header) to preserve layout
    df = pd.read_excel(input_path, sheet_name=sheet_name, header=None)
    intervals, first_start, last_end = build_intervals(df, fps=fps, lp_start_tc=lp_start_tc)

    # Compute the forced LP timecode for the final Program End marker
    last_reel, _last_rs, _last_re, last_lp_start, last_dur = intervals[-1]
    last_reel_correction = frames_to_td(max(0, last_reel - 1), fps)
    program_end_lp_tc = td_to_tc(
        last_lp_start + last_dur + last_reel_correction + frames_to_td(1, fps),
        fps
    )

    program_df = df.iloc[first_start:last_end + 1].copy()
    tc_pattern = re.compile(r"^\d{2}:\d{2}:\d{2}:\d{2}$")
    timecode_cols = [c for c in [1, 2] if c in program_df.columns]

    converted_rows = []
    for idx, row in program_df.iterrows():
        new_row = row.copy()
        changed = False

        for c in timecode_cols:
            val = new_row.get(c, None)
            if isinstance(val, str) and tc_pattern.match(val):
                new_tc = convert_tc_corrected(val, intervals, fps)
                new_row[c] = new_tc
                if new_tc is not None:
                    changed = True

        desc = str(new_row.get(3, ""))
        is_marker = "Program Start - Reel" in desc or "Program End - Reel" in desc
        is_final_program_end = "Program End" in desc and idx == last_end

        # Always keep the final Program End row and force its LP timecode
        if is_final_program_end:
            for c in timecode_cols:
                new_row[c] = program_end_lp_tc
            converted_rows.append(new_row)
            continue

        # Drop inter-reel markers when requested
        if drop_markers and is_marker:
            continue

        # Keep rows that had TC conversions or have non-empty descriptor columns
        has_content = changed or any(
            pd.notna(new_row.get(c)) for c in [3, 4, 5, 6] if c in new_row
        )
        if has_content:
            converted_rows.append(new_row)

    final_df = pd.DataFrame(converted_rows).reset_index(drop=True)

    if output_path is None:
        output_path = input_path.with_stem(input_path.stem + "_LongPlay")
    output_path = Path(output_path)

    with pd.ExcelWriter(output_path) as writer:
        final_df.to_excel(writer, sheet_name=f"{sheet_name} LongPlay",
                          header=False, index=False)
    return str(output_path)


def main():
    ap = argparse.ArgumentParser(
        description="Convert reel-based QC report timecodes to continuous long play."
    )
    ap.add_argument("input", help="Path to QC Excel file")
    ap.add_argument("-o", "--output", help="Optional output path (.xlsx)")
    ap.add_argument("--sheet", default="QC Report",
                    help="Sheet name (default: 'QC Report')")
    ap.add_argument("--fps", type=int, default=24,
                    help="Frames per second (default: 24)")
    ap.add_argument("--lp-start", default="01:00:00:00",
                    help="Long play start TC (default: 01:00:00:00)")
    ap.add_argument("--keep-markers", action="store_true",
                    help="Keep 'Program Start/End' reel markers in output")
    args = ap.parse_args()

    out = process(
        input_path=args.input,
        output_path=args.output,
        sheet_name=args.sheet,
        fps=args.fps,
        lp_start_tc=args.lp_start,
        drop_markers=not args.keep_markers,
    )
    print(out)


if __name__ == "__main__":
    main()
