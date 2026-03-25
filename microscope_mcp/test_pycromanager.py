"""
Standalone test: verify pycromanager can connect to Micro-Manager and grab an image.

Prerequisites:
  - Micro-Manager 2.0 is running
  - ZMQ server is enabled (Plugins > ZMQ Server > Start)
  - Default port 4827 is open

Run with:
  .venv\Scripts\python.exe microscope_mcp\test_pycromanager.py
"""

import sys
import os
import tempfile
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))


def test_connection():
    print("1. Connecting to Micro-Manager via pycromanager...")
    from pycromanager import Core
    core = Core()
    print(f"   OK — Core version: {core.get_version_info()}")
    return core


def test_stage_position(core):
    print("2. Reading stage position...")
    x = core.get_x_position()
    y = core.get_y_position()
    z = core.get_position()
    print(f"   OK — X={x:.3f}  Y={y:.3f}  Z={z:.3f}")
    return x, y, z


def test_snap_image(core):
    print("3. Snapping image...")
    core.snap_image()
    tagged = core.get_tagged_image()

    from collections import OrderedDict
    tags = OrderedDict(sorted(tagged.tags.items()))
    pixels = tagged.pix

    height = tags["Height"]
    width  = tags["Width"]
    total  = pixels.shape[0]
    nch    = total // (height * width)

    if nch > 1:
        pixels = pixels.reshape(height, width, nch)
    else:
        pixels = pixels.reshape(height, width)

    print(f"   OK — shape={pixels.shape}  dtype={pixels.dtype}  "
          f"min={pixels.min()}  max={pixels.max()}")
    return pixels, height, width, nch


def test_save_png(pixels):
    print("4. Saving image to temp PNG...")
    from PIL import Image

    pmin, pmax = pixels.min(), pixels.max()
    if pmax > pmin:
        norm = ((pixels - pmin) / (pmax - pmin) * 255).astype(np.uint8)
    else:
        norm = np.zeros_like(pixels, dtype=np.uint8)

    path = os.path.join(tempfile.gettempdir(), "pycromanager_test.png")
    Image.fromarray(norm).save(path)
    size_kb = os.path.getsize(path) / 1024
    print(f"   OK — saved to {path}  ({size_kb:.1f} KB)")
    return path


def main():
    print("=" * 55)
    print("  pycromanager image acquisition test")
    print("=" * 55)

    try:
        core = test_connection()
        test_stage_position(core)
        pixels, h, w, nch = test_snap_image(core)
        path = test_save_png(pixels)

        print()
        print("All tests passed.")
        print(f"Image saved: {path}")

    except Exception as exc:
        print(f"\nFAILED: {exc}")
        print("\nMake sure Micro-Manager is running with the ZMQ server enabled.")
        sys.exit(1)


if __name__ == "__main__":
    main()
