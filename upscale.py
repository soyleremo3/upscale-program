"""Command-line entry point: python upscale.py input.mp4 output.mp4 [options]"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from upscale_video.cli import main

if __name__ == "__main__":
    sys.exit(main())
