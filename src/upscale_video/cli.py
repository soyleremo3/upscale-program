"""Command-line entry point, useful for scripting and quick tests."""

import argparse
import sys
from pathlib import Path

from .config import DEFAULT_MODEL, DEFAULT_SCALE, AVAILABLE_MODELS
from . import pipeline


def _print_progress(stage: str, fraction: float) -> None:
    print(f"\r{stage:12s} {fraction * 100:5.1f}%", end="", flush=True)
    if fraction >= 1.0:
        print()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Upscale a video with realesrgan-ncnn-vulkan.")
    parser.add_argument("input", type=Path, help="Input video path")
    parser.add_argument("output", type=Path, help="Output video path")
    parser.add_argument("-n", "--model", default=DEFAULT_MODEL, choices=list(AVAILABLE_MODELS))
    parser.add_argument("-s", "--scale", type=int, default=DEFAULT_SCALE)
    parser.add_argument("-g", "--gpu-id", default="auto")
    parser.add_argument("--keep-temp", action="store_true")
    args = parser.parse_args(argv)

    pipeline.run(
        args.input, args.output,
        model_name=args.model, scale=args.scale, gpu_id=args.gpu_id,
        keep_temp=args.keep_temp, progress=_print_progress,
    )
    print(f"Done: {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
