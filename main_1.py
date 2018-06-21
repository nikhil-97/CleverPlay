import multiprocessing
import os

import camera_manager
import data_manager
import logging
import roi_controller
import time

import web_postman
import display_manager

import argparse

DISPLAY_VIDEO = False

class ExecutionController(object):
    # ExecutionController class is responsible for controlling everything related to execution.
    # It's the CEO of the program.
    # .start() starts the execution
    ca = camera_manager.CameraManager()
    data_mgr = data_manager.DataManager()

    #mgr = multiprocessing.Manager()
    #mgr_dict = mgr.dict()
    mgr_dict = dict()
    shared_data_pool = mgr_dict

    postman = web_postman.WebPostman()

    def __init__(self):
        self._is_initialized = False
        self.executors  = []
        if (DISPLAY_VIDEO): self.disp_mgr = display_manager.DisplayManager()

    def initialize(self):
        self.ca.initialize_manager()

        cam_readers = self.ca.get_cam_readers_list()

        for cr in cam_readers:
            vf = cr.get_attached_videoframe()
            ex = ExecutionBranch(cam_reader=cr,videoframe=vf,data_manager=self.data_mgr,display_manager=self.disp_mgr)
            if self.disp_mgr is not None: self.disp_mgr.attach_frame_to_display(vf)
            self.executors.append(ex)
            ex.initialize()
            logging.debug("Execution Branch initialized with VideoFrame " + str(vf.name))


        self.data_mgr.set_data_pool(self.shared_data_pool)
        self.postman.set_server_url('http://127.0.0.1')
        self.postman.set_shared_data_pool(self.shared_data_pool)

    def start_execution(self):
        for exe in self.executors:
            exe.start()
            logging.debug("Execution Branch "+str(exe)+" started")

        self.data_mgr.start_data_manager()
        #self.postman.start_run()
        if self.disp_mgr is not None : self.disp_mgr.start_display()

    def stop(self):
        pass

class ExecutionBranch:

    def __init__(self,**kwargs):
        self._cam_reader = kwargs['cam_reader']
        self._videoframe = kwargs['videoframe']
        self.data_mgr = kwargs['data_manager']
        self.display_mgr = kwargs['display_manager']
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

        if (self.display_mgr is not None):
            for vpu in self._roicontroller.get_attached_video_processors():
                self.display_mgr.attach_frame_to_display(vpu.debug_frame)


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-d","--debug",help="Enable all debug messages. Check out -lf for log files",action="store_true")
    arg_parser.add_argument("-lf", "--logfile", help="Usage : --logfile filename.extension \n"
                                                     "Log all messages to specified file.\n"
                                                     "P.S. Use with --debug",type=str)
    arg_parser.add_argument("-v", "--display_video", help="Display all debug videos",action="store_true")
    args = arg_parser.parse_args()
    if(args.debug):
        if(args.logfile):
            logging.basicConfig(level=logging.DEBUG,filename=args.logfile,format='%(levelname)s : %(funcName) in %(theadName) says %(message)s')
        else:
            logging.basicConfig(level=logging.DEBUG,format='%(levelname)s::%(funcName)s in %(threadName)s : %(message)s')
            logging.debug("Debug Mode ON. All messages will be shown.")

    if(args.display_video):
        DISPLAY_VIDEO = True

    ec = ExecutionController()
    ec.initialize()
    ec.start_execution()
