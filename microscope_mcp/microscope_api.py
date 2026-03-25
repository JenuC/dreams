import numpy as np
import time
from PIL import Image
import io


class VirtualMicroscope:
    """A simulated microscope for development and testing."""

    def __init__(self):
        self.position = {"x": 0.0, "y": 0.0, "z": 0.0}
        self._image_counter = 0

    def move_stage(self, x: float, y: float, z: float) -> dict:
        self.position = {"x": x, "y": y, "z": z}
        return self.position

    def get_stage_position(self) -> dict:
        return self.position

    def snap_image(self) -> dict:
        self._image_counter += 1
        pos = self.position
        return {
            "status": "ok",
            "filename": f"image_{self._image_counter:04d}.tif",
            "position": pos,
        }

    def get_image_png(self) -> bytes:
        """Return a random noise image as PNG bytes."""
        arr = np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8)
        img = Image.fromarray(arr)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()

    def wait(self, seconds: float) -> dict:
        time.sleep(seconds)
        return {"status": "ok", "waited_seconds": seconds}
