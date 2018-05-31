import numpy as np
import cv2
from video_processing import VideoFrame


class CameraManager(object):
    # CameraManager is responsible for decoding which camera belongs where(i.e. which camera sees which court on the field),
    # and reading the camera, and passing it to the video frame for further processing
    video_frames_list = []
    def __init__(self):
        _camlist = self.get_cameras_list()
        for cam in _camlist:
            v = VideoFrame(str(cam))
            self.video_frames_list.append(v)

    def get_cameras_list(self):
        return [0]

    def get_video_frames_list(self):
        return self.video_frames_list

    def read_camera(self,cam):
        cam1 = cv2.VideoCapture(0)

        pass