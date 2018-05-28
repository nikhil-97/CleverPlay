import threading

import numpy as np
import cv2

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
        print self.display_manager_threads

    def start_display(self):
        for dm_thread in self.display_manager_threads:
            dm_thread.start()

    def stopAllDisplays(self):
        print 'stopping all'
        for dm_thread in self.display_manager_threads:
            dm_thread.stop()

    #TODO:
    #def removeThreadFromList(self,idx):
    #    self.display_manager_threads.remove(idx)

class DisplayThread(threading.Thread):

    def __init__(self,VideoFrame_vframe,parent_DisplayManager):
        threading.Thread.__init__(self)
        self._attached_frame = VideoFrame_vframe
        self._attached_frame_name = VideoFrame_vframe.name
        self.parent_display_manager = parent_DisplayManager
        ## Saving a reference to the parent manager to use in stopAll
        self._thread_is_running = True

    def run(self):
        self.display_attached_frame()

    def display_attached_frame(self):
        while(self._thread_is_running):
            cv2.imshow(self._attached_frame_name,self._attached_frame.frame)
            key = cv2.waitKey(1) & 0xFF
            if(key==QUIT_KEY):
                self.stop()
                #TODO : self.parent_display_manager.removeThreadFromList(self._attached_frame_name)
            elif(key==QUIT_ALL_KEY):
                self.parent_display_manager.stopAllDisplays()

    def stop(self):
        self._thread_is_running = False
        print "Stopping %s"%self._attached_frame_name

if __name__=='__main__':
    import video_processing

    disp_mgr = DisplayManager()

    vf0 = video_processing.VideoFrame('Frame 0')
    vf0.update_video_frame(np.zeros((320,240),np.uint8))

    vf1 = video_processing.VideoFrame('Frame 1')
    vf1.update_video_frame(np.ones((640, 480), np.uint8))

    vf2 = video_processing.VideoFrame('Frame 2')
    vf2.update_video_frame(np.random.random_integers(low=0,high=255, size=(640,480 )))

    disp_mgr.attach_frame_to_display(vf0)
    disp_mgr.attach_frame_to_display(vf1)
    disp_mgr.attach_frame_to_display(vf2)

    disp_mgr.start_display()



