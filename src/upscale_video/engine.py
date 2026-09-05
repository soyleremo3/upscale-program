"""Wrapper around the realesrgan-ncnn-vulkan.exe binary."""

import subprocess
from pathlib import Path

from .config import ENGINE_EXE, MODELS_DIR, AVAILABLE_MODELS, FRAME_FORMAT


class EngineNotFoundError(RuntimeError):
    pass


class EngineError(RuntimeError):
    pass


def ensure_engine_available() -> None:
    if not ENGINE_EXE.exists():
        raise EngineNotFoundError(
            f"Engine not found at {ENGINE_EXE}. "
            "Run scripts/setup_engine.ps1 first."
        )


def upscale_frames(input_dir: Path, output_dir: Path, model_name: str, scale: int,
                    gpu_id: str = "auto") -> subprocess.Popen:
    """Start the upscale process and return the running Popen handle.

    Caller is responsible for waiting on it (directly, or by polling
    output_dir for progress).
    """
    ensure_engine_available()

    if model_name not in AVAILABLE_MODELS:
        raise ValueError(f"Unknown model: {model_name}")
    if scale not in AVAILABLE_MODELS[model_name]:
        raise ValueError(f"Model {model_name} does not support scale {scale}")

    output_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        str(ENGINE_EXE),
        "-i", str(input_dir),
        "-o", str(output_dir),
        "-m", str(MODELS_DIR),
        "-n", model_name,
        "-s", str(scale),
        "-f", FRAME_FORMAT,
    ]
    if gpu_id != "auto":
        cmd += ["-g", str(gpu_id)]

    return subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
    )
