import multiprocessing
import threading

import logging
import numpy as np
import cv2
import time
from common import VideoFrame

CAMERA_WARMUP_TIME_SECS = 3

logging.basicConfig(level=logging.INFO,format= '%(levelname)s : %(message)s')

class CameraManager(object):
    # CameraManager is responsible for decoding which camera belongs where(i.e. which camera sees which court on the field),
    # and reading the camera, and passing it to the video frame for further processing
    video_frames_list = []
    def __init__(self):
        self._camlist = self.get_connected_cameras_list()
        self._camera_framename_map = dict()
        self._video_frames_list = list()
        self.videoframe_reader_map = dict()

        self._is_manager_initialized = False

        self._all_videoframes_valid = False

    def get_connected_cameras_list(self):
        # read /dev/video* on linux,get all cams
        # return something like ['/dev/video0','/dev/video1','/dev/video2']
        return [0]

    def map_videoframes_from_camlist(self):
        # for each cam index in camlist, get the camera name
        # from the camera name, read the map file (map file has { camera_name : videoframe_name } )
        # get this map, and merge the cam index with videoframe_name
        # return { cam_index : videoframe_name }
        self._camera_framename_map.update( { 0 : 'Main Frame' } )

    def initialize_manager(self):
        self._camlist = self.get_connected_cameras_list()
        self.map_videoframes_from_camlist()
        for cam_index,frame_name in self._camera_framename_map.items():
            v = VideoFrame(frame_name)
            cr = USBCamReader(cam_index)
            cr.attach_videoframe(v)
            self.videoframe_reader_map.update( { cr : v } )
        self._video_frames_list = list(self.videoframe_reader_map.values())
        self._is_manager_initialized = True

    def get_cam_readers_list(self):
        return self.videoframe_reader_map.keys()

    def get_video_frames_list(self):
        return self._video_frames_list

    def start_all_camreaders(self):
        for camreader in self.videoframe_reader_map.keys():
            camreader.start_camreader()

    def stop_all_camreaders(self):
        for camreader in self.videoframe_reader_map.keys():
            camreader.stop_camreader()

    def start_cam_mgr(self):
        if(not self._is_manager_initialized):
            raise RuntimeError("Camera Manager has not been initialized. Perhaps you forgot to call initialize_manager() ?")
        self.start_all_camreaders()


class USBCamReader:
    def __init__(self,cam_idx):
        self._read_from_cam = cam_idx
        self._attached_videoframe = None
        self._initial_frame = None
        self._capture_device = cv2.VideoCapture(self._read_from_cam)

        self._read_thread = threading.Thread(name='CamReaderThread_%s'%str(self._read_from_cam), target = self.run)
        self._frames_valid = False
        self._is_running = False


    def attach_videoframe(self,VideoFrame_vf):
        self._attached_videoframe = VideoFrame_vf

    def read_camera(self):
        valid, frame = self._capture_device.read()
        if ((valid is False) or (frame is None)):
            raise RuntimeError(
                "Could not read a valid frame from %s. The thread has stopped." % str(self._read_from_cam))
        return valid, frame

    def run(self):

        self._is_running = True

        while(self._is_running and self._capture_device.isOpened()):
            valid_frame, acquired_frame = self.read_camera()
            grayframe = cv2.cvtColor(acquired_frame,cv2.COLOR_RGB2GRAY)
            self._attached_videoframe.update_current_frame(grayframe)
            self._attached_videoframe.set_current_frame_as_valid()
            if(not self._frames_valid):
                self._frames_valid = True
            # cv2.imshow(str(self._read_from_cam),self._attached_videoframe.get_current_frame_copy())
            # cv2.waitKey(1)
            # Uncomment imshow if you need to test

        if(not self._is_running):
            self._capture_device.release()

    def warm_up_camera(self,warmup_time_secs):

        logging.info('Warming up camera')

        for i in range(1,warmup_time_secs+1):

            logging.info("."*i)

            valid_frame, cap_frame = self.read_camera()
            self._initial_frame = cv2.cvtColor(cap_frame, cv2.COLOR_RGB2GRAY)
            time.sleep(1)

    def start_camreader(self):

        self.warm_up_camera(CAMERA_WARMUP_TIME_SECS)
        logging.info("Camera %s started\n" % str(self._read_from_cam))

        self._attached_videoframe.set_init_frame(self._initial_frame)
        self._attached_videoframe.set_init_frame_as_valid()

        self._read_thread.start()


    def stop_camreader(self):
        self._is_running = False

if __name__ == '__main__':

    cm = CameraManager()
    cm.initialize_manager()
    cm.start_cam_mgr()
    # simple as that. :O
    time.sleep(10)
    cm.stop_all_camreaders()


