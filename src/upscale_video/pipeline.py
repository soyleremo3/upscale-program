"""Orchestrates: extract frames -> upscale each frame -> reassemble video."""

import shutil
import time
from pathlib import Path
from typing import Callable, Optional

from . import ffmpeg_utils, engine
from .config import TEMP_DIR, DEFAULT_MODEL, DEFAULT_SCALE

ProgressCallback = Callable[[str, float], None]


def _noop(stage: str, fraction: float) -> None:
    pass


def run(
    input_video: Path,
    output_video: Path,
    model_name: str = DEFAULT_MODEL,
    scale: int = DEFAULT_SCALE,
    gpu_id: str = "auto",
    keep_temp: bool = False,
    progress: Optional[ProgressCallback] = None,
) -> Path:
    progress = progress or _noop
    input_video = Path(input_video)
    output_video = Path(output_video)

    run_dir = TEMP_DIR / f"{input_video.stem}_{int(time.time())}"
    frames_in = run_dir / "in"
    frames_out = run_dir / "out"

    try:
        progress("probing", 0.0)
        info = ffmpeg_utils.probe_video(input_video)

        progress("extracting", 0.0)
        total_frames = ffmpeg_utils.extract_frames(input_video, frames_in)
        progress("extracting", 1.0)

        progress("upscaling", 0.0)
        proc = engine.upscale_frames(frames_in, frames_out, model_name, scale, gpu_id)
        while proc.poll() is None:
            time.sleep(0.5)
            done = ffmpeg_utils.count_frames(frames_out)
            fraction = done / total_frames if total_frames else 0.0
            progress("upscaling", min(fraction, 0.999))
        if proc.returncode != 0:
            output = proc.stdout.read() if proc.stdout else ""
            raise engine.EngineError(f"Upscale failed (exit {proc.returncode}):\n{output}")
        progress("upscaling", 1.0)

        progress("encoding", 0.0)
        audio_source = input_video if info["has_audio"] else None
        ffmpeg_utils.frames_to_video(frames_out, info["fps"], output_video, audio_source)
        progress("encoding", 1.0)

        return output_video
    finally:
        if not keep_temp and run_dir.exists():
            shutil.rmtree(run_dir, ignore_errors=True)
