#!/usr/bin/env python3
"""Extract the final frame of a video using ffmpeg."""

import argparse
import subprocess
import sys
from pathlib import Path


def extract_last_frame(video_path: Path, output_path: Path) -> None:
    """Extract the last frame of a video using ffmpeg."""
    print(f"Extracting last frame from: {video_path}")
    cmd = [
        "ffmpeg",
        "-sseof",
        "-0.1",
        "-i",
        str(video_path),
        "-frames:v",
        "1",
        "-pix_fmt",
        "rgb24",
        "-compression_level",
        "0",
        "-y",
        str(output_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {result.stderr}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract the final frame of a video using ffmpeg"
    )
    parser.add_argument(
        "--video",
        "-v",
        required=True,
        help="Path to the input video file",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        help="Output path for the image file (default: <video_name>_finalframe.png)",
    )

    args = parser.parse_args()
    video_path = Path(args.video)
    if not video_path.exists():
        print(f"Error: Video not found: {video_path}", file=sys.stderr)
        sys.exit(1)

    output_path = Path(args.output) if args.output else Path(f"{video_path.stem}_finalframe.png")

    try:
        extract_last_frame(video_path, output_path)
        print(f"Saved to: {output_path}")
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
