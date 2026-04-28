import re, math, io
from datetime import timedelta
import pandas as pd
import streamlit as st

st.set_page_config(page_title="QC Long Play Converter", layout="centered")

st.title("QC Long Play Converter")
st.caption("Convert reel-based QC timecodes to a continuous long play timeline (with per-reel frame corrections).")

FPS = st.number_input("Frames per second (fps)", min_value=1, max_value=120, value=24, step=1)
sheet_name = st.text_input("Sheet name", value="QC Report")
lp_start = st.text_input("Long play start timecode", value="01:00:00:00")
drop_markers = st.checkbox("Drop 'Program Start/End' reel markers", value=True)

uploaded = st.file_uploader("Upload QC Excel (.xlsx)", type=["xlsx"])

def tc_to_td(tc: str, fps: int):
    if not isinstance(tc, str):
        return None
    m = re.match(r"^(\\d{2}):(\\d{2}):(\\d{2}):(\\d{2})$", tc.strip())
    if not m:
        return None
    h, mi, s, f = map(int, m.groups())
    return timedelta(hours=h, minutes=mi, seconds=s, milliseconds=(f * 1000 / fps))

def frames_to_td(frames: int, fps: int):
    return timedelta(seconds=frames / fps)

def td_to_tc(td: timedelta, fps: int):
    total = td.total_seconds()
    whole = math.floor(total)
    frac = total - whole
    frames = int(round(frac * fps))
    if frames == fps:
        frames = 0
        whole += 1
    h = int(whole // 3600)
    m = int((whole % 3600) // 60)
    s = int(whole % 60)
    return f"{h:02}:{m:02}:{s:02}:{frames:02}"

def build_intervals(df, fps, desc_col=3, tc_col=1, lp_start_tc="01:00:00:00"):
    reel_bounds = {}
    current = None
    for i, row in df.iterrows():
        desc = str(row.get(desc_col, ""))
        tc = row.get(tc_col, None)
        if isinstance(desc, str) and "Program Start - Reel" in desc:
            m = re.search(r"Reel\\s*(\\d+)", desc)
            if m and isinstance(tc, str):
                r = int(m.group(1))
                reel_bounds[r] = {"start_tc": tc, "end_tc": None, "start_row": i}
                current = r
        elif isinstance(desc, str) and "Program End - Reel" in desc and current is not None:
            if isinstance(tc, str):
                reel_bounds[current]["end_tc"] = tc
                reel_bounds[current]["end_row"] = i
            current = None

    if not reel_bounds:
        raise RuntimeError("No reel boundaries found. Ensure rows contain 'Program Start - Reel X' and 'Program End - Reel X' descriptors.")

    lp_cursor = tc_to_td(lp_start_tc, fps)
    intervals = []
    for r in sorted(reel_bounds.keys()):
        rs = tc_to_td(reel_bounds[r]["start_tc"], fps)
        re_ = tc_to_td(reel_bounds[r]["end_tc"], fps)
        dur = re_ - rs
        intervals.append((r, rs, re_, lp_cursor, dur))
        lp_cursor = lp_cursor + dur

    first_start = min(b["start_row"] for b in reel_bounds.values())
    last_end = max(b["end_row"] for b in reel_bounds.values())
    return intervals, first_start, last_end

def convert_tc_corrected(tc_str, intervals, fps):
    td = tc_to_td(tc_str, fps)
    if td is None:
        return tc_str
    for r, rs, re_, lp_start, _dur in intervals:
        if rs <= td < re_:
            offset = td - rs
            correction_frames = max(0, r - 1)
            return td_to_tc(lp_start + offset + frames_to_td(correction_frames, fps), fps)
    return None

if uploaded is not None:
    df = pd.read_excel(uploaded, sheet_name=sheet_name, header=None)
    try:
        intervals, first_start, last_end = build_intervals(df, fps=FPS, lp_start_tc=lp_start)
        program_df = df.iloc[first_start:last_end+1].copy()

        # Compute final Program End LP time with per-reel correction + one extra frame
        last_reel, _rs, _re, last_lp_start, last_dur = intervals[-1]
        last_reel_correction = frames_to_td(max(0, last_reel - 1), FPS)
        program_end_lp_tc = td_to_tc(last_lp_start + last_dur + last_reel_correction + frames_to_td(1, FPS), FPS)

        tc_pattern = re.compile(r"^\\d{2}:\\d{2}:\\d{2}:\\d{2}$")
        timecode_cols = [c for c in [1,2] if c in program_df.columns]
        converted_rows = []
        for idx, row in program_df.iterrows():
            new_row = row.copy()
            changed = False
            for c in timecode_cols:
                val = new_row.get(c, None)
                if isinstance(val, str) and tc_pattern.match(val):
                    new_tc = convert_tc_corrected(val, intervals, FPS)
                    if new_tc is None:
                        new_row[c] = None
                    else:
                        new_row[c] = new_tc
                        changed = True
            desc = str(new_row.get(3, ""))
            is_marker = isinstance(desc, str) and ("Program Start - Reel" in desc or "Program End - Reel" in desc)
            is_final_program_end = isinstance(desc, str) and ("Program End" in desc) and (idx == last_end)
            if is_final_program_end:\n",
            "                # Force final Program End LP time\n",
            "                wrote = False\n",
            "                for c in timecode_cols:\n",
            "                    new_row[c] = program_end_lp_tc\n",
            "                    wrote = True\n",
            "                if not wrote and len(timecode_cols) > 0:\n",
            "                    new_row[timecode_cols[0]] = program_end_lp_tc\n",
            "                converted_rows.append(new_row)\n",
            "                continue\n",
            "            if changed or (any(pd.notna(new_row.get(c)) for c in [3,4,5,6] if c in new_row) and not (drop_markers and is_marker)):\n",
            "                if drop_markers and is_marker:\n",
            "                    continue\n",
            "                converted_rows.append(new_row)\n",
            "\n",
            "        final_df = pd.DataFrame(converted_rows).reset_index(drop=True)\n",
            "        st.success(\"Conversion complete.\")\n",
            "        st.dataframe(final_df)\n",
            "\n",
            "        outbuf = io.BytesIO()\n",
            "        with pd.ExcelWriter(outbuf, engine=\"xlsxwriter\") as writer:\n",
            "            final_df.to_excel(writer, sheet_name=f\"{sheet_name} LongPlay\", header=False, index=False)\n",
            "        st.download_button(\"Download LongPlay Excel\", data=outbuf.getvalue(), file_name=\"QC_LongPlay.xlsx\", mime=\"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet\")\n",
            "    except Exception as e:\n",
            "        st.error(str(e))\n",
            "else:\n",
            "    st.info(\"Upload a QC Excel file to begin.\")\n",
