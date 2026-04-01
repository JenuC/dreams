import numpy as np
import time
import io
import tempfile
import os
from enum import Enum
from PIL import Image


class TestImage(str, Enum):
    CAMERA = "camera"    # 512x512 grayscale (skimage)
    RACCOON = "raccoon"  # 768x1024 RGB (scipy)
    GRADIENT = "gradient"  # synthetic fallback, always available


def _load_test_image(source: TestImage) -> np.ndarray:
    """Load a test image as an (H, W, 3) uint8 RGB array."""
    if source == TestImage.CAMERA:
        # Synthetic cameraman-like: concentric circles on gray background
        size = 512
        y, x = np.ogrid[:size, :size]
        cx, cy = size // 2, size // 2
        dist = np.sqrt((x - cx) ** 2 + (y - cy) ** 2)
        gray = (np.sin(dist / 10) * 127 + 128).astype(np.uint8)
        return np.stack([gray, gray, gray], axis=-1)

    if source == TestImage.RACCOON:
        # Synthetic color image: RGB gradient
        r = np.linspace(0, 255, 512, dtype=np.uint8)
        g = np.linspace(255, 0, 512, dtype=np.uint8)
        b = np.full(512, 128, dtype=np.uint8)
        R = np.tile(r, (512, 1))
        G = np.tile(g, (512, 1)).T[:512, :512]
        B = np.tile(b, (512, 1))
        return np.stack([R, G, B], axis=-1)

    # GRADIENT fallback
    row = np.linspace(0, 255, 512, dtype=np.uint8)
    gray = np.tile(row, (512, 1))
    return np.stack([gray, gray, gray], axis=-1)


def _array_to_png_bytes(arr: np.ndarray) -> bytes:
    img = Image.fromarray(arr.astype(np.uint8))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


class VirtualMicroscope:
    """A simulated microscope for development and testing."""

    def __init__(self, test_image: TestImage = TestImage.CAMERA):
        self.position = {"x": 0.0, "y": 0.0, "z": 0.0}
        self._image_counter = 0
        self._test_image_source = test_image
        self._image_cache: np.ndarray | None = None

    def _get_image(self) -> np.ndarray:
        if self._image_cache is None:
            self._image_cache = _load_test_image(self._test_image_source)
        return self._image_cache

    def set_test_image(self, source: TestImage) -> None:
        """Switch the test image source and clear the cache."""
        self._test_image_source = source
        self._image_cache = None

    def move_stage(self, x: float, y: float, z: float) -> dict:
        self.position = {"x": x, "y": y, "z": z}
        return self.position

    def get_stage_position(self) -> dict:
        return self.position

    def snap_image(self) -> dict:
        """Capture an image. Saves to a temp file and returns the path."""
        self._image_counter += 1
        path = os.path.join(tempfile.gettempdir(), f"microscope_{self._image_counter:04d}.png")
        Image.fromarray(self._get_image().astype(np.uint8)).save(path)
        return {
            "status": "ok",
            "filename": f"image_{self._image_counter:04d}.tif",
            "position": self.position,
            "image_path": path,
        }

    def get_image_png(self) -> bytes:
        """Return the test image as raw PNG bytes (for MCP resources)."""
        return _array_to_png_bytes(self._get_image())

    def wait(self, seconds: float) -> dict:
        time.sleep(seconds)
        return {"status": "ok", "waited_seconds": seconds}
