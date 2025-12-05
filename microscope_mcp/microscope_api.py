import numpy as np
import time


class Microscope:
    def __init__(self):
        self.position = {"x": 0.0, "y": 0.0, "z": 0.0}

    def move_stage(self, x: float, y: float, z: float):
        self.position = {"x": x, "y": y, "z": z}
        return self.position

    def get_stage_position(self):
        return self.position

    def snap_image(self):
        return {
            "status": "ok",
            "filename": "image_0001.tif",
            "note": "Mock image captured",
        }

    def get_image(self):
        return np.random.rand(1024, 1024)

    def wait(self, seconds: float):
        time.sleep(seconds)
