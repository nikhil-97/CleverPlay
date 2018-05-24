import numpy as np
import cv2


class CameraManager(object):
    # CameraManager is responsible for decoding which camera belongs where(i.e. which camera sees which court on the field),
    # and reading the camera, and passing it to the video frame for further processing
    def __init__(self):
        pass

    def get_video_frames_list(self):
        return [0]

    def read_camera(self):
        cam1 = cv2.VideoCapture(0)

        pass