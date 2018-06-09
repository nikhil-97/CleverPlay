import os

import camera_manager
import data_manager
import logging
import roi_controller
import time

import sys
import web_postman
import display_manager
from video_processing import VideoProcessingUnit

logging.basicConfig(level = logging.INFO)

class ExecutionController(object):
    # ExecutionController class is responsible for controlling everything related to execution.
    # It's the CEO of the program.
    # .start() starts the execution
    ca = camera_manager.CameraManager()
    data_mgr = data_manager.DataManager()
    shared_data_pool = None
    postman = web_postman.WebPostman()
    disp_mgr = display_manager.DisplayManager()

    def __init__(self):
        self._is_initialized = False
        self.executors  = []

    def initialize(self):
        self.ca.initialize_manager()

        cam_readers = self.ca.get_cam_readers_list()

        for cr in cam_readers:
            ex = ExecutionBranch(cam_reader=cr,videoframe=cr._attached_videoframe,data_manager=self.data_mgr)
            self.disp_mgr.attach_frame_to_display(cr._attached_videoframe)
            self.executors.append(ex)
            ex.initialize()

        self.data_mgr.set_data_pool(self.shared_data_pool)
        self.postman.set_server_url('http://127.0.0.1')
        self.postman.set_shared_data_pool(self.shared_data_pool)

    def start_execution(self):
        for exe in self.executors:
            exe.start()

        self.data_mgr.start_data_manager()

        #self.postman.start_run()

    def stop(self):
        pass

class ExecutionBranch:

    def __init__(self,**kwargs):
        self._cam_reader = kwargs['cam_reader']
        self._videoframe = kwargs['videoframe']
        self.data_mgr = kwargs['data_manager']
        self._initialized = False

    def initialize(self):
        self._roicontroller = roi_controller.RoiController()
        self._roicontroller.attach_controller_to_videoframe(self._videoframe)
        self._roicontroller.initialize_rois()
        self._roicontroller.attach_video_processors_to_controlling_rois()
        for vpu in self._roicontroller.get_attached_video_processors():
            new_databin = data_manager.DataBin()
            vpu.attach_data_bin(new_databin)
            new_databin.register_with_data_manager(self.data_mgr)

    def start(self):
        self._cam_reader.start_camreader()
        logging.info("Waiting for valid VideoFrames")

        while (not self._cam_reader._frames_valid):
            logging.info("_")
            time.sleep(0.5)
        logging.info("VideoFrames valid!")

        self._roicontroller.update_init_roiframes()
        self._roicontroller.start_roi_controller()
        self._roicontroller.update_init_frames_in_vpus()
        self._roicontroller.start_attached_video_processors()


if __name__ == '__main__':
    ec = ExecutionController()
    ec.initialize()
    ec.start_execution()
