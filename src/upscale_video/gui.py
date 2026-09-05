"""Minimal Tkinter GUI: pick a video, pick a model/scale, run, watch progress."""

import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from . import pipeline
from .config import AVAILABLE_MODELS, DEFAULT_MODEL, DEFAULT_SCALE


class UpscaleApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Video Upscale")
        self.root.geometry("560x260")
        self.root.resizable(False, False)

        self._progress_queue: queue.Queue = queue.Queue()
        self._worker: threading.Thread | None = None

        self._build_widgets()
        self.root.after(100, self._poll_progress_queue)

    def _build_widgets(self) -> None:
        pad = {"padx": 10, "pady": 6}

        # Input file
        row = tk.Frame(self.root)
        row.pack(fill="x", **pad)
        tk.Label(row, text="Girdi video:", width=12, anchor="w").pack(side="left")
        self.input_var = tk.StringVar()
        tk.Entry(row, textvariable=self.input_var).pack(side="left", fill="x", expand=True)
        tk.Button(row, text="Sec...", command=self._pick_input).pack(side="left", padx=(6, 0))

        # Output file
        row = tk.Frame(self.root)
        row.pack(fill="x", **pad)
        tk.Label(row, text="Cikti video:", width=12, anchor="w").pack(side="left")
        self.output_var = tk.StringVar()
        tk.Entry(row, textvariable=self.output_var).pack(side="left", fill="x", expand=True)
        tk.Button(row, text="Sec...", command=self._pick_output).pack(side="left", padx=(6, 0))

        # Model + scale
        row = tk.Frame(self.root)
        row.pack(fill="x", **pad)
        tk.Label(row, text="Model:", width=12, anchor="w").pack(side="left")
        self.model_var = tk.StringVar(value=DEFAULT_MODEL)
        model_combo = ttk.Combobox(
            row, textvariable=self.model_var, values=list(AVAILABLE_MODELS),
            state="readonly", width=22,
        )
        model_combo.pack(side="left")
        model_combo.bind("<<ComboboxSelected>>", self._on_model_change)

        tk.Label(row, text="Olcek:").pack(side="left", padx=(16, 4))
        self.scale_var = tk.StringVar(value=str(DEFAULT_SCALE))
        self.scale_combo = ttk.Combobox(
            row, textvariable=self.scale_var,
            values=[str(s) for s in AVAILABLE_MODELS[DEFAULT_MODEL]],
            state="readonly", width=4,
        )
        self.scale_combo.pack(side="left")

        # Start button
        row = tk.Frame(self.root)
        row.pack(fill="x", **pad)
        self.start_button = tk.Button(row, text="Baslat", command=self._start, width=14)
        self.start_button.pack(side="left")

        # Progress
        row = tk.Frame(self.root)
        row.pack(fill="x", **pad)
        self.progress_bar = ttk.Progressbar(row, mode="determinate", maximum=100)
        self.progress_bar.pack(fill="x")

        self.status_var = tk.StringVar(value="Hazir")
        tk.Label(self.root, textvariable=self.status_var, anchor="w").pack(fill="x", padx=10)

    def _on_model_change(self, _event=None) -> None:
        model = self.model_var.get()
        scales = [str(s) for s in AVAILABLE_MODELS[model]]
        self.scale_combo["values"] = scales
        if self.scale_var.get() not in scales:
            self.scale_var.set(scales[0])

    def _pick_input(self) -> None:
        path = filedialog.askopenfilename(
            title="Video sec",
            filetypes=[("Video", "*.mp4 *.mkv *.mov *.avi *.webm"), ("Tumu", "*.*")],
        )
        if not path:
            return
        self.input_var.set(path)
        if not self.output_var.get():
            input_path = Path(path)
            default_out = input_path.with_name(f"{input_path.stem}_upscaled.mp4")
            self.output_var.set(str(default_out))

    def _pick_output(self) -> None:
        path = filedialog.asksaveasfilename(
            title="Cikti dosyasi",
            defaultextension=".mp4",
            filetypes=[("MP4", "*.mp4")],
        )
        if path:
            self.output_var.set(path)

    def _start(self) -> None:
        input_path = self.input_var.get().strip()
        output_path = self.output_var.get().strip()
        if not input_path or not output_path:
            messagebox.showerror("Eksik bilgi", "Girdi ve cikti dosyasini secin.")
            return

        self.start_button.config(state="disabled")
        self.progress_bar["value"] = 0
        self.status_var.set("Basliyor...")

        self._worker = threading.Thread(
            target=self._run_pipeline,
            args=(Path(input_path), Path(output_path), self.model_var.get(), int(self.scale_var.get())),
            daemon=True,
        )
        self._worker.start()

    def _run_pipeline(self, input_path: Path, output_path: Path, model: str, scale: int) -> None:
        def on_progress(stage: str, fraction: float) -> None:
            self._progress_queue.put(("progress", stage, fraction))

        try:
            pipeline.run(input_path, output_path, model_name=model, scale=scale, progress=on_progress)
            self._progress_queue.put(("done", output_path, None))
        except Exception as exc:  # surfaced to the user via messagebox
            self._progress_queue.put(("error", str(exc), None))

    def _poll_progress_queue(self) -> None:
        try:
            while True:
                kind, a, b = self._progress_queue.get_nowait()
                if kind == "progress":
                    stage, fraction = a, b
                    self.progress_bar["value"] = fraction * 100
                    self.status_var.set(f"{stage} ({fraction * 100:.0f}%)")
                elif kind == "done":
                    self.progress_bar["value"] = 100
                    self.status_var.set("Tamamlandi")
                    self.start_button.config(state="normal")
                    messagebox.showinfo("Bitti", f"Video hazir:\n{a}")
                elif kind == "error":
                    self.status_var.set("Hata")
                    self.start_button.config(state="normal")
                    messagebox.showerror("Hata", a)
        except queue.Empty:
            pass
        self.root.after(100, self._poll_progress_queue)


def launch() -> None:
    root = tk.Tk()
    UpscaleApp(root)
    root.mainloop()
