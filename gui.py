#!/usr/bin/env python3
"""Native tkinter GUI for QC Long Play Converter."""

import subprocess
import sys
import threading
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    _DND_AVAILABLE = True
except ImportError:
    _DND_AVAILABLE = False

from qc_longplay_convert import process

COMMON_FPS = ["24", "25", "30"]
DEFAULT_FPS = "24"
DEFAULT_SHEET = "QC Report"
DEFAULT_LP_START = "01:00:00:00"

_BaseApp = TkinterDnD.Tk if _DND_AVAILABLE else tk.Tk


class App(_BaseApp):
    def __init__(self):
        super().__init__()
        self.title("QC Long Play Converter")
        self.resizable(False, False)
        self._output_path: str | None = None
        self._build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        outer = ttk.Frame(self, padding=18)
        outer.grid(row=0, column=0, sticky="nsew")

        pad = {"padx": 8, "pady": 4}

        # ── Input file ──────────────────────────────────────────────
        ttk.Label(outer, text="Input File:").grid(row=0, column=0, sticky="e", **pad)
        self._input_var = tk.StringVar()
        input_entry = ttk.Entry(outer, textvariable=self._input_var, width=48)
        input_entry.grid(row=0, column=1, sticky="ew", **pad)
        ttk.Button(outer, text="Browse…", command=self._browse_input).grid(
            row=0, column=2, **pad
        )

        # ── Drop zone ───────────────────────────────────────────────
        drop_text = (
            "↓   drag & drop an .xlsx here   ↓"
            if _DND_AVAILABLE
            else "pip install tkinterdnd2 to enable drag & drop"
        )
        drop_fg = "#3c4a6e" if _DND_AVAILABLE else "#999999"
        drop_bg = "#e8f0fe" if _DND_AVAILABLE else "#f0f0f0"
        self._drop_zone = tk.Label(
            outer,
            text=drop_text,
            relief="groove", bd=2,
            bg=drop_bg, fg=drop_fg,
            font=(None, 10),
            pady=8, padx=10,
            cursor="hand2" if _DND_AVAILABLE else "arrow",
        )
        self._drop_zone.grid(row=1, column=1, sticky="ew", padx=8, pady=(0, 8))

        if _DND_AVAILABLE:
            for widget in (input_entry, self._drop_zone):
                widget.drop_target_register(DND_FILES)
                widget.dnd_bind("<<Drop>>", self._on_file_drop)
            self._drop_zone.dnd_bind("<<DragEnter>>", self._on_drag_enter)
            self._drop_zone.dnd_bind("<<DragLeave>>", self._on_drag_leave)

        # ── Sheet name ──────────────────────────────────────────────
        ttk.Label(outer, text="Sheet Name:").grid(row=2, column=0, sticky="e", **pad)
        self._sheet_var = tk.StringVar(value=DEFAULT_SHEET)
        ttk.Entry(outer, textvariable=self._sheet_var, width=30).grid(
            row=2, column=1, sticky="w", **pad
        )

        # ── FPS ─────────────────────────────────────────────────────
        ttk.Label(outer, text="FPS:").grid(row=3, column=0, sticky="e", **pad)
        self._fps_var = tk.StringVar(value=DEFAULT_FPS)
        ttk.Combobox(
            outer, textvariable=self._fps_var,
            values=COMMON_FPS, width=8, state="readonly"
        ).grid(row=3, column=1, sticky="w", **pad)

        # ── LP start timecode ───────────────────────────────────────
        ttk.Label(outer, text="LP Start TC:").grid(row=4, column=0, sticky="e", **pad)
        self._lp_start_var = tk.StringVar(value=DEFAULT_LP_START)
        ttk.Entry(outer, textvariable=self._lp_start_var, width=15).grid(
            row=4, column=1, sticky="w", **pad
        )

        # ── Output folder ───────────────────────────────────────────
        ttk.Label(outer, text="Output Folder:").grid(row=5, column=0, sticky="e", **pad)
        self._output_dir_var = tk.StringVar()
        ttk.Entry(outer, textvariable=self._output_dir_var, width=48).grid(
            row=5, column=1, sticky="ew", **pad
        )
        ttk.Button(outer, text="Browse…", command=self._browse_output).grid(
            row=5, column=2, **pad
        )
        ttk.Label(
            outer, text="Leave blank to save alongside source file", foreground="gray"
        ).grid(row=6, column=1, sticky="w", padx=8, pady=(0, 4))

        # ── Keep markers checkbox ───────────────────────────────────
        self._keep_markers_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            outer,
            text='Keep "Program Start/End" markers in output',
            variable=self._keep_markers_var,
        ).grid(row=7, column=1, sticky="w", **pad)

        # ── Separator ───────────────────────────────────────────────
        ttk.Separator(outer, orient="horizontal").grid(
            row=8, column=0, columnspan=3, sticky="ew", pady=10
        )

        # ── Action buttons ──────────────────────────────────────────
        btn_frame = ttk.Frame(outer)
        btn_frame.grid(row=9, column=0, columnspan=3, pady=(0, 6))

        self._convert_btn = ttk.Button(
            btn_frame, text="Convert", command=self._run_conversion, width=14
        )
        self._convert_btn.pack(side="left", padx=6)

        self._reveal_btn = ttk.Button(
            btn_frame, text="Reveal in Finder", command=self._reveal_output,
            width=16, state="disabled"
        )
        self._reveal_btn.pack(side="left", padx=6)

        # ── Log area ────────────────────────────────────────────────
        ttk.Label(outer, text="Log:").grid(row=10, column=0, sticky="ne", **pad)
        log_frame = ttk.Frame(outer)
        log_frame.grid(row=10, column=1, columnspan=2, **pad)

        self._log = tk.Text(
            log_frame, width=58, height=9,
            state="disabled", wrap="word",
            font=("Menlo", 11) if sys.platform == "darwin" else ("Courier", 10),
        )
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self._log.yview)
        self._log.configure(yscrollcommand=scrollbar.set)
        self._log.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    # ------------------------------------------------------------------
    # Drag and drop
    # ------------------------------------------------------------------

    def _parse_drop_data(self, data: str) -> str:
        """Extract a single file path from a tkinterdnd2 event.data string.

        Paths containing spaces are brace-quoted by Tk: {/my path/file.xlsx}
        Multiple files arrive space-separated; we take the first.
        """
        raw = data.strip()
        if raw.startswith("{"):
            end = raw.find("}")
            return raw[1:end] if end != -1 else raw[1:]
        return raw.split()[0]

    def _on_file_drop(self, event) -> None:
        path = self._parse_drop_data(event.data)
        if not path.lower().endswith(".xlsx"):
            messagebox.showwarning("Wrong File Type", "Please drop an .xlsx file.")
            self._reset_drop_zone()
            return
        self._set_input(path)
        self._reset_drop_zone()

    def _on_drag_enter(self, event) -> None:
        self._drop_zone.configure(bg="#c2d4fc", text="↓   release to load   ↓")

    def _on_drag_leave(self, event) -> None:
        self._reset_drop_zone()

    def _reset_drop_zone(self) -> None:
        self._drop_zone.configure(
            bg="#e8f0fe", text="↓   drag & drop an .xlsx here   ↓"
        )

    # ------------------------------------------------------------------
    # File / folder browsers
    # ------------------------------------------------------------------

    def _browse_input(self) -> None:
        path = filedialog.askopenfilename(
            title="Select QC Report",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
        )
        if path:
            self._set_input(path)

    def _browse_output(self) -> None:
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self._output_dir_var.set(folder)

    def _set_input(self, path: str) -> None:
        self._input_var.set(path)
        self._output_path = None
        self._reveal_btn.configure(state="disabled")
        self.title(f"QC Long Play Converter — {Path(path).name}")

    # ------------------------------------------------------------------
    # Logging helpers
    # ------------------------------------------------------------------

    def _log_write(self, text: str) -> None:
        self._log.configure(state="normal")
        self._log.insert("end", text + "\n")
        self._log.see("end")
        self._log.configure(state="disabled")

    def _log_clear(self) -> None:
        self._log.configure(state="normal")
        self._log.delete("1.0", "end")
        self._log.configure(state="disabled")

    # ------------------------------------------------------------------
    # Conversion
    # ------------------------------------------------------------------

    def _run_conversion(self) -> None:
        input_path = self._input_var.get().strip()
        if not input_path:
            messagebox.showwarning("No File", "Please select an input .xlsx file first.")
            return

        try:
            fps = int(self._fps_var.get())
        except ValueError:
            messagebox.showerror("Invalid FPS", f"'{self._fps_var.get()}' is not a valid FPS.")
            return

        sheet = self._sheet_var.get().strip() or DEFAULT_SHEET
        lp_start = self._lp_start_var.get().strip() or DEFAULT_LP_START
        keep_markers = self._keep_markers_var.get()

        # Resolve output path from optional destination folder
        output_dir = self._output_dir_var.get().strip()
        if output_dir:
            stem = Path(input_path).stem
            output_path = str(Path(output_dir) / f"{stem}_LongPlay.xlsx")
        else:
            output_path = None  # process() defaults to alongside the source file

        self._log_clear()
        self._output_path = None
        self._convert_btn.configure(state="disabled")
        self._reveal_btn.configure(state="disabled")

        self._log_write(f"Input:   {input_path}")
        self._log_write(f"Sheet:   {sheet}")
        self._log_write(f"FPS:     {fps}")
        self._log_write(f"Start:   {lp_start}")
        self._log_write(f"Markers: {'kept' if keep_markers else 'dropped'}")
        if output_path:
            self._log_write(f"Output:  {output_path}")
        self._log_write("")

        threading.Thread(
            target=self._worker,
            args=(input_path, sheet, fps, lp_start, keep_markers, output_path),
            daemon=True,
        ).start()

    def _worker(self, input_path: str, sheet: str, fps: int,
                lp_start: str, keep_markers: bool,
                output_path: str | None) -> None:
        try:
            out = process(
                input_path=input_path,
                output_path=output_path,
                sheet_name=sheet,
                fps=fps,
                lp_start_tc=lp_start,
                drop_markers=not keep_markers,
            )
            self.after(0, self._on_success, out)
        except Exception as exc:
            self.after(0, self._on_error, str(exc))

    def _on_success(self, output_path: str) -> None:
        self._output_path = output_path
        self._log_write(f"Done!\nOutput: {output_path}")
        self._convert_btn.configure(state="normal")
        self._reveal_btn.configure(state="normal")

    def _on_error(self, message: str) -> None:
        self._log_write(f"Error: {message}")
        self._convert_btn.configure(state="normal")
        messagebox.showerror("Conversion Failed", message)

    # ------------------------------------------------------------------
    # Reveal output
    # ------------------------------------------------------------------

    def _reveal_output(self) -> None:
        if not self._output_path:
            return
        if sys.platform == "darwin":
            subprocess.run(["open", "-R", self._output_path], check=False)
        elif sys.platform == "win32":
            subprocess.run(["explorer", "/select,", self._output_path], check=False)
        else:
            subprocess.run(["xdg-open", str(Path(self._output_path).parent)], check=False)


def main() -> None:
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
