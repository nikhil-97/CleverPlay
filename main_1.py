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
        self.whatever  = {}

    def initialize(self):
        self.ca.initialize_manager()
        videoframes_list = self.ca.get_video_frames_list()
        for videoframe in videoframes_list:
            self.whatever.update( { videoframe : None })
            roi_ctrlr = self.setup_roi_controller(videoframe)
            roi_ctrlr.attach_video_processors_to_controlling_rois()
            for vpu in roi_ctrlr.get_attached_video_processors():
                db = data_manager.DataBin()
                vpu.attach_data_bin(db)
                db.register_with_data_manager(self.data_mgr)
        #print "self.whatever after roi setup = ", self.whatever
        self._is_initialized = True

    def setup_roi_controller(self,VideoFrame_vf):
        rc = roi_controller.RoiController()
        rc.attach_controller_to_videoframe(VideoFrame_vf)
        self.whatever[VideoFrame_vf] = { rc : [] } #nested_dict
        rc.initialize_rois()
        return rc

    def start_execution(self):
        if(not self._is_initialized):
            raise RuntimeError(
                "Execution not initalized. Did you forget to call initialize() first ?")
        self.ca.start_cam_mgr()
        self.all_valid = False
        vf_list = self.whatever.keys()

        logging.info("Waiting for valid VideoFrames")
        while(not self.all_valid):
            logging.info("_")
            for vf in vf_list:
                if(vf.is_init_frame_valid() and vf.is_current_frame_valid()):
                    self.all_valid = True
                    self.disp_mgr.attach_frame_to_display(vf)
                else:
                    self.all_valid = False
                    break
                    # break ensures that no other vf can set all_valid back to true

            # check all the videoframes if each of them are valid or not.
            # if one of them is False, check everything again
            time.sleep(0.5)
        logging.info("All VideoFrames valid ! ")

        for vf in vf_list:
            my_rc = self.whatever[vf].keys()[0]
            my_rc.update_init_roiframes()
            my_rc.start_roi_controller()
            for r in my_rc.get_controlling_rois():
                self.disp_mgr.attach_frame_to_display(r)
            my_rc.update_init_frames_in_vpus()
            my_rc.start_attached_video_processors()

        self.disp_mgr.start_display()

        self.data_mgr.start_data_manager()
        self.data_mgr.set_data_pool(self.shared_data_pool)

        self.postman.set_server_url('http://127.0.0.1')
        self.postman.set_shared_data_pool(self.shared_data_pool)
        self.postman.start_run()

    def stop(self):
        pass


if __name__ == '__main__':
    ec = ExecutionController()
    ec.initialize()
    ec.start_execution()
