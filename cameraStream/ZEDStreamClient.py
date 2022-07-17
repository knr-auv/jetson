"""ZED Camera streaming
"""
import io
import math
import threading
import time

import cv2
import numpy as np
import pyzed.sl as sl
from PIL import Image
from typing_extensions import Self

import communicationThreads.Simulation.simulationClient as sc
import variable
from cameraStream.stream import cameraStream


class ZEDSenderThread:
    """Local streaming of ZED processed data"""

    def __init__(self) -> None:
        threading.Thread.__init__(self)
        self.active = True

    def run(self):
        init = sl.InitParameters()
        init.camera_resolution = sl.RESOLUTION.HD2K
        init.depth_mode = sl.DEPTH_MODE.ULTRA
        cam = sl.Camera()

        status = cam.open(init)
        if status != sl.ERROR_CODE.SUCCESS:
            print(repr(status))
            exit(1)

        runtime = sl.RuntimeParameters()

        stream = sl.StreamingParameters()
        stream.codec = sl.STREAMING_CODEC.H265
        stream.bitrate = 7000
        status = cam.enable_streaming(stream)
        if status != sl.ERROR_CODE.SUCCESS:
            print(repr(status))
            exit(1)

        while self.active:
            cam.grab(runtime)

        cam.disable_streaming()
        cam.close()


class ZEDStreamClient(cameraStream):
    """Stream client using ZED camera"""

    def __init__(self):
        threading.Thread.__init__(self)
        self.frame = None
        self.depth_map = None
        self.point_cloud = None

    def run(self):
        init = sl.InitParameters()
        init.camera_resolution = sl.RESOLUTION.HD2K
        init.depth_mode = sl.DEPTH_MODE.ULTRA
        cam = sl.Camera()
        status = cam.open(init)
        if status != sl.ERROR_CODE.SUCCESS:
            print(repr(status))
            exit(1)

        runtime = sl.RuntimeParameters()
        img = sl.Mat()
        depth_map = sl.Mat()
        point_cloud = sl.Mat()

        while self.active:
            err = cam.grab(runtime)
            if err == sl.ERROR_CODE.SUCCESS:
                cam.retrieve_image(img, sl.VIEW.LEFT)
                cam.retrieve_measure(depth_map, sl.MEASURE.DEPTH)
                cam.retrieve_measure(point_cloud, sl.MEASURE.XYZRGBA)

                # save numpys ?
                self.frame = img.get_data()
                self.depth_map = depth_map.get_data()
                self.point_cloud = point_cloud.get_data()

    def getFrame(self):
        img = Image.fromarray(self.frame)
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format="JPEG")

        return img_byte_arr.getvalue()

    def get_depth_map(self):
        depth = Image.fromarray(self.depth_map)
        depth_byte_arr = io.BytesIO()
        depth.save(depth_byte_arr, format="JPEG")

        return depth_byte_arr.getvalue()

    def getPointCloud(self):
        return self.point_cloud
