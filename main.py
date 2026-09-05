"""Entry point: launches the video upscale GUI."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from upscale_video.gui import launch

if __name__ == "__main__":
    launch()
