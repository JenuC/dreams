import numpy as np
import time
from pycromanager import Core
from collections import OrderedDict


class Microscope:
    def __init__(self):
        self.position = {"x": 0.0, "y": 0.0, "z": 0.0}
        self.core = Core()
        self.pixels = np.random.rand(100, 100)
        self.channels = 0

    def move_stage(self, x: float, y: float, z: float):
        self.position = {"x": x, "y": y, "z": z}
        return self.position

    def get_stage_position(self):
        self.position = {
            "x": self.core.get_x_position(),
            "y": self.core.get_y_position(),
            "z": self.core.get_position(),
        }
        return self.position

    def snap_image(self):
        self.core.snap_image()
        tagged_image = self.core.get_tagged_image()

        tags = OrderedDict(sorted(tagged_image.tags.items()))
        pixels = tagged_image.pix

        total_pixels = pixels.shape[0]
        height, width = tags["Height"], tags["Width"]
        nchannels = total_pixels // (height * width)

        if nchannels > 1:
            pixels = pixels.reshape(height, width, nchannels)
        else:
            pixels = pixels.reshape(height, width)

        self.pixels = pixels
        self.channels = nchannels

        return {
            "status": "OK",
            "[H, W]": [height, width],
            "note": "Image on MM2",
        }

    def get_image(self):
        return self.pixels

    def wait(self, seconds: float):
        time.sleep(seconds)
