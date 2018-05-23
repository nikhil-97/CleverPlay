import numpy as np
import cv2

class DisplayManager(object):

    def __init__(self):
        pass

    def attach_to_frame(self):
        pass

    def display_frame(self,VideoFrame_frame,str_window_name):
        cv2.imshow(str_window_name,VideoFrame_frame)
        key = cv2.waitKey(1) & 0xFF
        if(key==ord('x')):
            pass
