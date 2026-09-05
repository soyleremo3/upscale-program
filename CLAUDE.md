# Upscale Program

Local Windows tool to upscale personal videos (e.g. 360p -> 1080p) on hardware
with no dedicated GPU: Intel i9-13900H (CPU) + Intel Iris Xe (integrated GPU).

## Approach

- Upscale engine: `realesrgan-ncnn-vulkan.exe` (from xinntao/Real-ESRGAN releases,
  tag v0.2.5.0). Uses Vulkan compute, which Iris Xe supports well — no CUDA/GPU
  driver setup needed beyond the Intel graphics driver already on the machine.
- Not using PyTorch/ONNX Runtime DirectML: avoids Python ML stack version
  headaches (this machine runs Python 3.14, too new for many ML wheels) and
  the ncnn-vulkan binary is self-contained and fast on integrated GPUs.
- Pipeline: ffmpeg extracts frames -> realesrgan-ncnn-vulkan upscales each
  frame -> ffmpeg re-encodes frames back into video and muxes original audio.

## Layout

- `tools/realesrgan-ncnn-vulkan/` — downloaded engine binary + models.
  **Gitignored** (binary, ~45MB). Fetched by `scripts/setup_engine.ps1`.
- `src/upscale_video/` — Python package:
  - `ffmpeg_utils.py` — frame extraction, frame->video re-encode, audio mux.
  - `engine.py` — thin wrapper around `realesrgan-ncnn-vulkan.exe`.
  - `pipeline.py` — orchestrates extract -> upscale -> reassemble.
  - `gui.py` — Tkinter GUI (stdlib only, no extra deps) to pick input file,
    model, scale, and run with a progress bar.
  - `cli.py` — command-line entry point for scripting/testing.
- `main.py` — launches the GUI.
- `temp/`, `output/` — runtime working dirs, gitignored.

## Available models (bundled with the engine, pick per content type)

- `realesr-animevideov3-x2` / `-x3` / `-x4` — tuned for real-world video,
  fast, good default for personal/phone footage. Native x3 model is a
  direct fit for 360p -> 1080p without an extra downscale step.
- `realesrgan-x4plus` — general-purpose photo/video x4, higher quality, slower.
- `realesrgan-x4plus-anime` — for animated/cartoon content.

## Hardware constraints to keep in mind

- No dedicated GPU. Iris Xe via Vulkan is the acceleration path; CPU fallback
  works but is much slower.
- 16GB RAM: process video frame-by-frame (temp files on disk), never load an
  entire video's frames into memory at once.
- Long CPU/GPU-bound runs heat up a laptop — pipeline should support
  processing in chunks/resumable steps rather than one giant blocking run.

## Setup

```bash
powershell -ExecutionPolicy Bypass -File scripts/setup_engine.ps1
python main.py
```

## Commit convention

Small, incremental commits per logical change (Conventional Commits style:
`feat:`, `fix:`, `chore:`, `docs:`).
