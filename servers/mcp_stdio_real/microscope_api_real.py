import numpy as np
import time
import io
import tempfile
import os
from collections import OrderedDict
from PIL import Image
from pycromanager import Core


class Microscope:
    def __init__(self):
        self.position = {"x": 0.0, "y": 0.0, "z": 0.0}
        self.core = Core()
        self._image_counter = 0
        self._last_pixels: np.ndarray | None = None

    def move_stage(self, x: float, y: float, z: float) -> dict:
        self.core.set_xy_position(x, y)
        self.core.set_position(z)
        self.position = {"x": x, "y": y, "z": z}
        return self.position

    def get_stage_position(self) -> dict:
        self.position = {
            "x": self.core.get_x_position(),
            "y": self.core.get_y_position(),
            "z": self.core.get_position(),
        }
        return self.position

    def snap_image(self) -> dict:
        """Capture an image via pycromanager, save to temp file, return path + metadata."""
        self.core.snap_image()
        tagged_image = self.core.get_tagged_image()

        tags = OrderedDict(sorted(tagged_image.tags.items()))
        pixels = tagged_image.pix

        height = tags["Height"]
        width = tags["Width"]
        total_pixels = pixels.shape[0]
        nchannels = total_pixels // (height * width)

        if nchannels > 1:
            pixels = pixels.reshape(height, width, nchannels)
        else:
            pixels = pixels.reshape(height, width)

        self._last_pixels = pixels
        self._image_counter += 1

        # Normalise to uint8 for saving (handles uint16 from real cameras)
        pmin, pmax = pixels.min(), pixels.max()
        if pmax > pmin:
            norm = ((pixels - pmin) / (pmax - pmin) * 255).astype(np.uint8)
        else:
            norm = np.zeros_like(pixels, dtype=np.uint8)

        path = os.path.join(tempfile.gettempdir(), f"microscope_{self._image_counter:04d}.png")
        Image.fromarray(norm).save(path)

        return {
            "status": "ok",
            "filename": f"image_{self._image_counter:04d}.tif",
            "position": self.position,
            "image_path": path,
            "shape": [height, width] if nchannels == 1 else [height, width, nchannels],
            "dtype": str(tagged_image.pix.dtype),
        }

    def get_image_png(self) -> bytes:
        """Return the last captured image as raw PNG bytes."""
        if self._last_pixels is None:
            raise RuntimeError("No image captured yet. Call snap_image() first.")
        pmin, pmax = self._last_pixels.min(), self._last_pixels.max()
        if pmax > pmin:
            norm = ((self._last_pixels - pmin) / (pmax - pmin) * 255).astype(np.uint8)
        else:
            norm = np.zeros_like(self._last_pixels, dtype=np.uint8)
        buf = io.BytesIO()
        Image.fromarray(norm).save(buf, format="PNG")
        return buf.getvalue()

    def wait(self, seconds: float) -> dict:
        time.sleep(seconds)
        return {"status": "ok", "waited_seconds": seconds}
