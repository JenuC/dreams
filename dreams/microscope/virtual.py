import os
import tempfile
import time
from enum import Enum

import numpy as np
from PIL import Image

from .common import array_to_png_bytes


class TestImage(str, Enum):
    CAMERA = "camera"
    RACCOON = "raccoon"
    RINGS = "rings"
    SPECTRUM = "spectrum"
    GRADIENT = "gradient"


def load_test_image(source: TestImage) -> np.ndarray:
    """Load a test image as an (H, W, 3) uint8 RGB array."""
    if source in (TestImage.CAMERA, TestImage.RINGS):
        size = 512
        y_coords, x_coords = np.ogrid[:size, :size]
        center_x, center_y = size // 2, size // 2
        distance = np.sqrt(
            (x_coords - center_x) ** 2 + (y_coords - center_y) ** 2
        )
        grayscale = (np.sin(distance / 10) * 127 + 128).astype(np.uint8)
        return np.stack([grayscale, grayscale, grayscale], axis=-1)

    if source in (TestImage.RACCOON, TestImage.SPECTRUM):
        red = np.linspace(0, 255, 512, dtype=np.uint8)
        green = np.linspace(255, 0, 512, dtype=np.uint8)
        blue = np.full(512, 128, dtype=np.uint8)
        red_grid = np.tile(red, (512, 1))
        green_grid = np.tile(green, (512, 1)).T[:512, :512]
        blue_grid = np.tile(blue, (512, 1))
        return np.stack([red_grid, green_grid, blue_grid], axis=-1)

    row = np.linspace(0, 255, 512, dtype=np.uint8)
    grayscale = np.tile(row, (512, 1))
    return np.stack([grayscale, grayscale, grayscale], axis=-1)


class VirtualMicroscope:
    """A simulated microscope for development and testing."""

    def __init__(self, test_image: TestImage = TestImage.CAMERA):
        self.position = {"x": 0.0, "y": 0.0, "z": 0.0}
        self._image_counter = 0
        self._test_image_source = test_image
        self._image_cache: np.ndarray | None = None

    def _get_image(self) -> np.ndarray:
        if self._image_cache is None:
            self._image_cache = load_test_image(self._test_image_source)
        return self._image_cache

    def set_test_image(self, source: TestImage) -> None:
        self._test_image_source = source
        self._image_cache = None

    def move_stage(self, x: float, y: float, z: float) -> dict:
        self.position = {"x": x, "y": y, "z": z}
        return self.position

    def get_stage_position(self) -> dict:
        return self.position

    def snap_image(self) -> dict:
        self._image_counter += 1
        path = os.path.join(
            tempfile.gettempdir(),
            f"microscope_{self._image_counter:04d}.png",
        )
        Image.fromarray(self._get_image().astype(np.uint8)).save(path)
        return {
            "status": "ok",
            "filename": f"image_{self._image_counter:04d}.tif",
            "position": self.position,
            "image_path": path,
        }

    def get_image_png(self) -> bytes:
        return array_to_png_bytes(self._get_image())

    def wait(self, seconds: float) -> dict:
        time.sleep(seconds)
        return {"status": "ok", "waited_seconds": seconds}
