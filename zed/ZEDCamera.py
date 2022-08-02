"""Camera thread for images/depth/POC processing"""
import io
import socket
import string
import struct
import sys
import threading
from time import sleep
from typing import Tuple

import cv2
import numpy as np
import pyzed.sl as sl
from PIL import Image


class ZEDCamera(threading.Thread):
    def __init__(self, image_size: Tuple[int, int] = None, lock=threading.Lock) -> None:
        threading.Thread.__init__(self)
        self.active = True
        self.frame = None
        self.depth_map = None
        self.point_cloud = None
        self.image_size = image_size
        self.lock = lock

    def stop(self):
        """Stop the main funtion causing the camera to close"""
        with self.lock:
            self.active = False

    def run(self):
        """Main function executed in thread after start() method"""
        init = sl.InitParameters()
        init.camera_resolution = sl.RESOLUTION.HD2K
        init.depth_mode = sl.DEPTH_MODE.ULTRA
        cam = sl.Camera()

        status = cam.open(init)
        if status != sl.ERROR_CODE.SUCCESS:
            print(repr(status))
            sys.exit(1)

        runtime = sl.RuntimeParameters()
        # Prepare data containers
        image_size = cam.get_camera_information().camera_resolution
        if self.image_size:
            image_size.width = self.image_size[0]
            image_size.height = self.image_size[1]

        img = sl.Mat(image_size.width, image_size.height, sl.MAT_TYPE.U8_C4)
        depth_map = sl.Mat(image_size.width, image_size.height, sl.MAT_TYPE.U8_C4)
        point_cloud = sl.Mat()

        while self.active:
            err = cam.grab(runtime)
            # Retrive data from camera frame
            if err == sl.ERROR_CODE.SUCCESS:
                cam.retrieve_image(img, sl.VIEW.LEFT, sl.MEM.CPU, image_size)
                cam.retrieve_measure(depth_map, sl.MEASURE.DEPTH, sl.MEM.CPU, image_size)
                cam.retrieve_measure(point_cloud, sl.MEASURE.XYZRGBA)

            with self.lock:
                # save numpys for processing in other classes
                self.frame = img.get_data()
                self.depth_map = depth_map.get_data()
                self.point_cloud = point_cloud.get_data()

            sleep(0.01)

        cam.close()
