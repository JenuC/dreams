import numpy as np
import time
import io
import tempfile
import os
from collections import OrderedDict
from PIL import Image
from pycromanager import Core


def _array_to_png_bytes(arr: np.ndarray) -> bytes:
    img = Image.fromarray(arr.astype(np.uint8))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _normalise_to_uint8(pixels: np.ndarray) -> np.ndarray:
    pmin, pmax = pixels.min(), pixels.max()
    if pmax > pmin:
        return ((pixels - pmin) / (pmax - pmin) * 255).astype(np.uint8)
    return np.zeros_like(pixels, dtype=np.uint8)


class RealMicroscope:
    """Wraps pycromanager Core for use as an MCP server backend."""

    def __init__(self):
        self.core = Core()
        self._image_counter = 0
        self._last_pixels: np.ndarray | None = None
        self.position = {"x": 0.0, "y": 0.0, "z": 0.0}
        # Use SimZ as focus device when SimCamera is loaded (simulation mode)
        loaded_devices = self.obj_2_list(self.core.get_loaded_devices())
        self._focus_device = "SimFocus" if "SimCam" in loaded_devices else None

    def move_stage(self, x: float, y: float, z: float) -> dict:
        self.core.set_xy_position(x, y)
        if self._focus_device:
            self.core.set_position(self._focus_device, z)
        else:
            self.core.set_position(z)
        self.position = {"x": x, "y": y, "z": z}
        return self.position

    def get_stage_position(self) -> dict:
        self.position = {
            "x": self.core.get_x_position(),
            "y": self.core.get_y_position(),
            "z": self.core.get_position(self._focus_device) if self._focus_device else self.core.get_position(),
        }
        return self.position

    def snap_image(self) -> dict:
        """Capture an image via pycromanager, save to temp PNG, return path + metadata."""
        self.core.snap_image()
        tagged = self.core.get_tagged_image()

        tags = OrderedDict(sorted(tagged.tags.items()))
        pixels = tagged.pix
        height = tags["Height"]
        width = tags["Width"]
        nchannels = pixels.shape[0] // (height * width)

        if nchannels > 1:
            pixels = pixels.reshape(height, width, nchannels)
        else:
            pixels = pixels.reshape(height, width)

        self._last_pixels = pixels
        self._image_counter += 1

        path = os.path.join(tempfile.gettempdir(), f"scope_real_{self._image_counter:04d}.png")
        Image.fromarray(_normalise_to_uint8(pixels)).save(path)

        return {
            "status": "ok",
            "filename": f"image_{self._image_counter:04d}.tif",
            "position": self.position,
            "image_path": path,
            "shape": [height, width] if nchannels == 1 else [height, width, nchannels],
            "dtype": str(tagged.pix.dtype),
        }

    def get_image_png(self) -> bytes:
        """Return the last captured image as raw PNG bytes (for MCP resource)."""
        if self._last_pixels is None:
            raise RuntimeError("No image captured yet — call snap_image() first.")
        return _array_to_png_bytes(_normalise_to_uint8(self._last_pixels))

    def wait(self, seconds: float) -> dict:
        time.sleep(seconds)
        return {"status": "ok", "waited_seconds": seconds}

    @staticmethod
    def obj_2_list(name):
        """Convert Java object to Python list."""
        return [name.get(i) for i in range(name.size())]