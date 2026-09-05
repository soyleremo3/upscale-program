"""Paths and constants shared across the upscale pipeline."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

ENGINE_DIR = PROJECT_ROOT / "tools" / "realesrgan-ncnn-vulkan"
ENGINE_EXE = ENGINE_DIR / "realesrgan-ncnn-vulkan.exe"
MODELS_DIR = ENGINE_DIR / "models"

TEMP_DIR = PROJECT_ROOT / "temp"
OUTPUT_DIR = PROJECT_ROOT / "output"

# model_name -> valid scale factors, from the models bundled with the engine
AVAILABLE_MODELS = {
    "realesr-animevideov3": [2, 3, 4],
    "realesrgan-x4plus": [4],
    "realesrgan-x4plus-anime": [4],
}

DEFAULT_MODEL = "realesr-animevideov3"
DEFAULT_SCALE = 3

FRAME_FORMAT = "png"
