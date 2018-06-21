import threading

import cv2
import logging
from numpy import ones,uint8,random, dtype, array, asarray
import numpy as np

QUIT_KEY = ord('x')
QUIT_ALL_KEY = ord('X')

class DisplayManager(object):

    def __init__(self):
        self.display_manager_threads=[]
        self.attached_videoframes=[]

    def attach_frame_to_display(self,VideoFrame_vframe):
        self.attached_videoframes.append(VideoFrame_vframe)

        dt = DisplayThread(VideoFrame_vframe,self)
        self.display_manager_threads.append(dt)

    def start_display(self):
        logging.debug("Display Manager Started")
        for dm_thread in self.display_manager_threads:
            dm_thread.start()

    def stop_all_displays(self):
        print 'stopping all'
        for dm_thread in self.display_manager_threads:
            dm_thread.stop()

    #TODO:
    #def removeThreadFromList(self,idx):
    #    self.display_manager_threads.remove(idx)

class DisplayThread(threading.Thread):

    def __init__(self,VideoFrame_vframe,parent_DisplayManager):
        threading.Thread.__init__(self,name=VideoFrame_vframe.name+'DisplayThread')
        self._attached_frame = VideoFrame_vframe
        self._attached_frame_name = VideoFrame_vframe.name
        self.parent_display_manager = parent_DisplayManager
        ## Saving a reference to the parent manager to use in stopAll
        self._thread_is_running = True

    def run(self):
        self.display_attached_frame()

    def display_attached_frame(self):
        cv2.namedWindow(self._attached_frame_name)
        while self._thread_is_running:
            #print self._attached_frame.name,self._attached_frame.get_current_frame_copy(), type(self._attached_frame.get_current_frame_copy()[0][0])
            copy = self._attached_frame.get_current_frame_copy()
            cv2.putText(copy,str(self._attached_frame.get_current_frame_number()),(100,100),cv2.FONT_HERSHEY_COMPLEX,0.5,(255,0,0),1,cv2.CV_AA)
            cv2.imshow(self._attached_frame_name,copy)
            key = cv2.waitKey(1) & 0xFF
            if key == QUIT_KEY :
                self.stop()
                #TODO : self.parent_display_manager.removeThreadFromList(self._attached_frame_name)
            elif key == QUIT_ALL_KEY :
                self.parent_display_manager.stop_all_displays()

    def stop(self):
        self._thread_is_running = False
        print "Stopping %s"%self._attached_frame_name

if __name__=='__main__':
    import common

    disp_mgr = DisplayManager()

    #vf0 = video_processing.VideoFrame('Frame 0')
    #vf0.update_video_frame(np.zeros((240,320),np.uint8))

    vf1 = common.VideoFrame('Frame 1')
    vf2 = common.VideoFrame('Frame 2')

    vf2.update_current_frame(np.asarray(255*ones((300, 400), np.uint8)))
    vf1.update_current_frame(np.asarray(random.random_integers(low=0,high=255, size=(480,640)),np.uint8))
    #disp_mgr.attach_frame_to_display(vf0)
    disp_mgr.attach_frame_to_display(vf1)
    disp_mgr.attach_frame_to_display(vf2)

    disp_mgr.start_display()


