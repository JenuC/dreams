import io

import numpy as np
from PIL import Image


def array_to_png_bytes(array: np.ndarray) -> bytes:
    image = Image.fromarray(array.astype(np.uint8))
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def normalise_to_uint8(pixels: np.ndarray) -> np.ndarray:
    pixel_min = pixels.min()
    pixel_max = pixels.max()
    if pixel_max > pixel_min:
        return ((pixels - pixel_min) / (pixel_max - pixel_min) * 255).astype(np.uint8)
    return np.zeros_like(pixels, dtype=np.uint8)
