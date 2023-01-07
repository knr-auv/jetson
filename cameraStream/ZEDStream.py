"""ZED Camera local streaming
"""
import io
import threading

import numpy as np
import pyzed.sl as sl
from PIL import Image

from cameraStream.stream import cameraStream
from zed.ZEDCamera import ZEDCamera


class ZEDStream(cameraStream):
    """Streamer using ZED camera.

    Produces byte representations of JPEG images/depth
    from camera copies, which can be further streamed to GUI.
    """

    def __init__(self, camera: ZEDCamera, lock: threading.Lock):
        threading.Thread.__init__(self)
        self.camera = camera
        self.frame = None
        self.depth_map = None
        self.point_cloud = None
        self.lock = lock

    def run(self):
        while self.active:
            with self.lock:
                self.frame = self.camera.frame
                self.depth_map = self.camera.depth_map
                self.point_cloud = self.camera.point_cloud

    def getFrame(self) -> bytes:
        """Prepares byte representation of jpeg image"""
        img = Image.fromarray(self.frame)
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format="JPEG")

        return img_byte_arr.getvalue()

    def getDepthMap(self) -> bytes:
        """Prepare byte representation of jpeg depth map"""
        depth = Image.fromarray(self.depth_map)
        depth_byte_arr = io.BytesIO()
        depth.save(depth_byte_arr, format="JPEG")

        return depth_byte_arr.getvalue()

    def getPointCloud(self) -> np.ndarray:
        """Numpy array representing cloud of points with XYZ"""
        return self.point_cloud
