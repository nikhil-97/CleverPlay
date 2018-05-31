from threading import Lock

import numpy as np
import cv2

class ImageProcessing:

    @staticmethod
    def background_subtraction(self, frame, avgframe):
        AVGRATE = 0
        cv2.accumulateWeighted(frame, avgframe, AVGRATE)
        bkg = cv2.convertScaleAbs(avgframe)
        subtract = cv2.GaussianBlur(cv2.absdiff(frame, bkg), (5, 5), 3)
        _, threshold = cv2.threshold(subtract, 50, 200, cv2.THRESH_BINARY)
        # TODO : make this threshold dynamic i.e. not hardcoded
        RECT_KERNEL = cv2.getStructuringElement(cv2.MORPH_RECT, (11, 11))
        thresh_closed = cv2.dilate(threshold, RECT_KERNEL, 5)
        return thresh_closed

class VideoProcessor(object):
    def __init__(self):
        pass

    def attach_to_frame(self,VideoFrame_frame):
        self._attached_videoframe = VideoFrame_frame

    def process_frame(self):
        # TODO : all videoframes are locked when updating their frame. video processing thread should acquire lock before processings
        self.roi_bkgsub = ImageProcessing.background_subtraction(self._attached_videoframe.frame, self.roi_avg)

    def check_presence(self,region, minsum):
        total = np.sum(np.sum(region, axis = 0), axis = 0) / 1000
        # 1/1000 is the scaling factor
        return int(total > minsum)


class VideoFrame(object):
    def __init__(self,str_name):
        self.name = str_name
        self.frame = None
        self._frame_access_lock = Lock()
        l = Lock()

    def update_video_frame(self,frame_from_camera):
        self._frame_access_lock.acquire()
        self.frame = frame_from_camera
        self._frame_access_lock.release()

    def get_video_frame(self):
        return self.frame
