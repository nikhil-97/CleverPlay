import threading

import numpy as np
import cv2
import time
from common import VideoFrame

CAMERA_WARMUP_TIME_SECS = 3

class CameraManager(object):
    # CameraManager is responsible for decoding which camera belongs where(i.e. which camera sees which court on the field),
    # and reading the camera, and passing it to the video frame for further processing
    video_frames_list = []
    def __init__(self):
        self._camlist = self.get_connected_cameras_list()
        self._camera_framename_map = dict()
        self._video_frames_list = list()
        self.videoframe_readthread_map = dict()

        for cam in self._camlist:
            v = VideoFrame(str(cam))
            self.video_frames_list.append(v)

        self._is_manager_initialized = False

    def get_connected_cameras_list(self):
        # read /dev/video* on linux,get all cams
        # return something like ['/dev/video0','/dev/video1','/dev/video2']
        return [0]

    def map_videoframes_from_camlist(self):
        # for each cam index in camlist, get the camera name
        # from the camera name, read the map file (map file has { camera_name : videoframe_name } )
        # get this map, and merge the cam index with videoframe_name
        # return { cam_index : videoframe_name }
        self._camera_framename_map.update({0: 'Main Frame'})

    def initialize_manager(self):
        self._camlist = self.get_connected_cameras_list()
        self.map_videoframes_from_camlist()
        for cam_index,frame_name in self._camera_framename_map.items():
            v = VideoFrame(frame_name)
            t = CameraReadThread(cam_index,v)
            self.videoframe_readthread_map.update( { v : t } )
        self._is_manager_initialized = True

    def get_video_frames_list(self):
        return self.video_frames_list

    def startAllCamReadThreads(self):
        for camread_thread in self.videoframe_readthread_map.values():
            camread_thread.start()

    def stopAllCamReadThreads(self):
        for camread_thread in self.videoframe_readthread_map.values():
            camread_thread.stopThread()

    def startCamMgr(self):
        if(not self._is_manager_initialized):
            raise RuntimeError("Manager has not been initialized. Perhaps you forgot to call initialize_manager() ?")
        self.startAllCamReadThreads()


class CameraReadThread(threading.Thread):

    def __init__(self,cam_index,VideoFrame_vf):
        threading.Thread.__init__(self)
        self._read_from_cam_idx = cam_index
        self._videoframe = VideoFrame_vf
        self._is_thread_running = False
        self._initial_frame = None

        self._capture_device = cv2.VideoCapture(self._read_from_cam_idx)

    def run(self):
        self.warm_up_camera(CAMERA_WARMUP_TIME_SECS)
        self._videoframe.set_init_frame(self._initial_frame)
        self._is_thread_running = True
        while(self._is_thread_running and self._capture_device.isOpened()):
            valid_frame, acquired_frame = self._capture_device.read()
            if ( (valid_frame is False) or (acquired_frame is None) ):
                raise RuntimeError(
                    "Could not read a valid frame from %s. The thread has stopped."%str(self._read_from_cam_idx))
            grayframe = cv2.cvtColor(acquired_frame,cv2.COLOR_BGR2GRAY)
            self._videoframe.update_current_frame(grayframe)

    def warm_up_camera(self,warmup_time_secs):

        print 'Warming up camera ',

        for _ in range(1,warmup_time_secs+1):
            print ". ",
            valid_frame, self._initial_frame = self._capture_device.read()
            if ((valid_frame is False) or (self._initial_frame is None)):
                raise RuntimeError(
                    "Could not read a valid frame from %s while warming up. The thread has stopped." % str(self._read_from_cam_idx))

            time.sleep(1)

        print "\n"

    def stopThread(self):
        self._capture_device.release()
        self._is_thread_running = False


if __name__ == '__main__':

    cm = CameraManager()
    cm.initialize_manager()
    cm.startCamMgr()
    # simple as that. :O


