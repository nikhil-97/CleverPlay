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

    def attach_to_frame(self):
        pass

    def process_frame(self):
        pass

    def check_presence(self,region, minsum):
        total = np.sum(np.sum(region, axis = 0), axis = 0) / 1000
        # 1/1000 is the scaling factor
        return int(total > minsum)


class VideoFrame(object):
    def __init__(self):
        pass

    def update_video_frame(self,frame_from_camera):
        self.frame = frame_from_camera

class RoiClass(VideoFrame):
    def __init__(self):
        super(RoiClass, self).__init__()
