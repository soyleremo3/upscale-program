"""Thin wrappers around ffmpeg/ffprobe for frame extraction and reassembly."""

import json
import subprocess
from pathlib import Path

from .config import FRAME_FORMAT

FRAME_PATTERN = f"frame_%08d.{FRAME_FORMAT}"
FRAME_GLOB = f"frame_*.{FRAME_FORMAT}"


class FfmpegError(RuntimeError):
    pass


def _run(cmd: list[str]) -> subprocess.CompletedProcess:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise FfmpegError(f"Command failed: {' '.join(cmd)}\n{result.stderr}")
    return result


def probe_video(video_path: Path) -> dict:
    cmd = [
        "ffprobe", "-v", "quiet", "-print_format", "json",
        "-show_streams", "-show_format", str(video_path),
    ]
    result = _run(cmd)
    info = json.loads(result.stdout)

    video_stream = next(s for s in info["streams"] if s["codec_type"] == "video")
    has_audio = any(s["codec_type"] == "audio" for s in info["streams"])

    num, den = video_stream["r_frame_rate"].split("/")
    fps = float(num) / float(den)

    return {
        "fps": fps,
        "width": video_stream.get("width"),
        "height": video_stream.get("height"),
        "has_audio": has_audio,
        "duration": float(info["format"].get("duration", 0.0)),
    }


def extract_frames(video_path: Path, frames_dir: Path) -> int:
    frames_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y", "-i", str(video_path),
        "-vsync", "0",
        str(frames_dir / FRAME_PATTERN),
    ]
    _run(cmd)
    return count_frames(frames_dir)


def count_frames(frames_dir: Path) -> int:
    return sum(1 for _ in frames_dir.glob(FRAME_GLOB))


def frames_to_video(frames_dir: Path, fps: float, output_path: Path,
                     audio_source: Path | None = None) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(fps),
        "-i", str(frames_dir / FRAME_PATTERN),
    ]
    if audio_source is not None:
        cmd += ["-i", str(audio_source)]

    cmd += ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "medium"]

    if audio_source is not None:
        cmd += ["-map", "0:v", "-map", "1:a", "-c:a", "aac", "-b:a", "192k", "-shortest"]

    cmd.append(str(output_path))
    _run(cmd)
