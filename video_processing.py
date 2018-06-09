import threading

import common
import numpy as np
import cv2

import abc

import time

class PresenceProcessing(object):

    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self._init_frame = None
        self._avg_rate = 0.005
        self._avg_frame = None

    def set_init_frame(self, init_frame_from_videoframe):
        self._init_frame = init_frame_from_videoframe
        self.set_avg_frame(np.float32(self._init_frame))

    def set_averaging_rate(self,float_avg_rate):
        if(float_avg_rate > 1 or float_avg_rate < 0):
            raise ValueError('Trying to set an invalid averaging rate. The rate should be a float value between 0.0 and 1.0')
        self._avg_rate = float_avg_rate

    def set_avg_frame(self, avg_frame):
        self._avg_frame = avg_frame

    def get_avg_frame(self):
        return self._avg_frame

    def accumulate_frames_to_average(self, input_frame):
        """Accumulate frames to get the background"""
        # NOTE : For accumulateWeighted() to work properly, the depth of colourFrame and movingAverage must be one of the following options:

        # colourFrame.depth() == CV_8U && movingAverage.depth() == CV_32F
        # colourFrame.depth() == CV_8U && movingAverage.depth() == CV_64F
        # colourFrame.depth() == CV_16U && movingAverage.depth() == CV_32F
        # colourFrame.depth() == CV_16U && movingAverage.depth() == CV_64F
        # colourFrame.depth() == CV_32F && movingAverage.depth() == CV_32F
        # colourFrame.depth() == CV_32F && movingAverage.depth() == CV_64F
        # colourFrame.depth() == CV_64F && movingAverage.depth() == CV_64F
        # From : https://stackoverflow.com/questions/7059817/assertion-failed-with-accumulateweighted-in-opencv

        #print "input_frame",input_frame,"avg_frame=",self._avg_frame
        avg = np.float32(self._avg_frame)
        #print "avg = ",avg,avg.shape
        #print "input",input_frame,input_frame.shape
        cv2.accumulateWeighted(input_frame, avg, self._avg_rate)
        abs_avgframe = cv2.convertScaleAbs(avg)
        self.set_avg_frame(abs_avgframe)

    def subtract_frames(self,frame1,frame2):
        return cv2.GaussianBlur(cv2.absdiff(frame1, frame2), (5, 5), 3)

    def threshold_frame(self,frame_to_threshold):
        _, thresholded_frame = cv2.threshold(frame_to_threshold, 50, 200, cv2.THRESH_BINARY)
        RECT_KERNEL = cv2.getStructuringElement(cv2.MORPH_RECT, (11, 11))
        thresh_closed = cv2.dilate(thresholded_frame, RECT_KERNEL, 5)
        return thresh_closed

    def add_all_frame_pixels(self,np_ndarray_frame):
        return np.sum(np.sum(np_ndarray_frame, axis=0), axis=0)

    @abc.abstractmethod
    def process_frame(self,frame_to_process):
        pass

    @abc.abstractmethod
    def get_presence_from_frame(self, input_frame):
        pass

class StaticPresenceProcessing(PresenceProcessing):

    def __init__(self):
        PresenceProcessing.__init__(self)
        self._processed_frame = None
        self.minsum = 250

    def set_minsum(self,int_minsum):
        self.minsum = int_minsum

    def get_presence_from_frame(self, input_frame):
        frame_sum = np.sum(self.add_all_frame_pixels(input_frame)) / 10000
        # 1/10000 is the scaling factor
        print "frame_sum = ", frame_sum
        return int(frame_sum > self.minsum)

    def get_processed_frame(self):
        return self._processed_frame

    def process_frame(self,frame_to_process):
        self.accumulate_frames_to_average(frame_to_process)
        sub = self.subtract_frames(self._avg_frame, self._init_frame)
        self._processed_frame = self.threshold_frame(sub)

    def get_presence_from_processed_frame(self):
        #self.get_presence_from_frame(self._processed_frame)
        return 1

class DynamicPresenceProcessing(PresenceProcessing):

    def __init__(self):
        PresenceProcessing.__init__(self)
        self._processed_frame = None
        self.minsum = 150

    def set_minsum(self,int_minsum):
        self.minsum = int_minsum

    def get_presence_from_frame(self, input_frame):
        frame_sum = np.sum(self.add_all_frame_pixels(input_frame)) / 10000
        # 1/10000 is the scaling factor
        #print "frame_sum = ",frame_sum
        return int(frame_sum > self.minsum)

    def process_frame(self,frame_to_process):
        self.accumulate_frames_to_average(frame_to_process)
        #print "in ",self,"frame_to_process = ",frame_to_process,frame_to_process.shape,"self._avg_frame = ",self._avg_frame,self._avg_frame.shape
        sub = self.subtract_frames(frame_to_process,self._avg_frame)
        self._processed_frame = self.threshold_frame(sub)

    def get_processed_frame(self):
        return self._processed_frame

    def get_presence_from_processed_frame(self):
        return self.get_presence_from_frame(self._processed_frame)

class VideoProcessor:
    def __init__(self,processing_mode):
        self._processing_mode = processing_mode
        self._processing = None
        self._videoframe_to_process_on = None

        if(self._processing_mode == 'static_presence'):
            self._processing = StaticPresenceProcessing()
        elif(self._processing_mode == 'dynamic_presence'):
            self._processing = DynamicPresenceProcessing()
        else:
            raise NameError(
                "VideoProcessor takes only 'static_presence' or 'dynamic_presence' . Provided none of these two")

    def initialize_video_frame(self, VideoFrame_vf):
        self._videoframe_to_process_on = VideoFrame_vf

    def update_initframe_of_videoframe(self):
        self._processing.set_init_frame(self._videoframe_to_process_on.get_init_frame_copy())

    def get_processing_mode(self):
        return self._processing_mode

    def get_processing_avgframe(self):
        return self._processing.get_avg_frame()

    def process_frame(self,frame_to_process):
        self._processing.process_frame(frame_to_process)

    def get_presence_now(self):
        return self._processing.get_presence_from_processed_frame()


class VideoProcessingUnit(object):

    def __init__(self,**kwargs):
        self._attached_videoframe = None
        self._attached_data_bin = None

        self._my_data = 0

        self._processing_thread = threading.Thread(name='VideoProcessingThread',target=self.run_processor)
        self._is_processing_thread_running = False

        if("processing_mode" in kwargs):
            pmode = kwargs["processing_mode"]
            self._processor = VideoProcessor(pmode)
        else:
            self._processor = VideoProcessor('dynamic_presence')
        self._frame_to_process = None

        self._average_frame = None

    def attach_to_frame(self,VideoFrame_frame):
        if VideoFrame_frame is None:
            raise ValueError("Trying to attach to None frame. Check if the VideoFrame has been correctly initialized")
        self._attached_videoframe = VideoFrame_frame
        self._processor.initialize_video_frame(self._attached_videoframe)

    def update_initframe(self):
        self._processor.update_initframe_of_videoframe()

    def attach_data_bin(self,DataBin_dbin):
        self._attached_data_bin = DataBin_dbin
        self._attached_data_bin.attach_to_processing_unit(self)

    def start_processing(self):
        self._is_processing_thread_running = True
        self._processing_thread.start()

    def stop_processing(self):
        self._is_processing_thread_running = False
        print "Stopping %s 's VideoProcessingThread" % self._attached_videoframe.name

    def check_presence_now(self):
        self._my_data = self._processor.get_presence_now()

    def put_my_data_in_bin(self):
        self._attached_data_bin.update_collected_data(self._my_data)

    def run_processor(self):
        while self._is_processing_thread_running:
            self._frame_to_process = self._attached_videoframe.get_current_frame_copy()
            self._processor.process_frame(self._frame_to_process)
            self.check_presence_now()
            self._average_frame = self._processor.get_processing_avgframe()
            self.put_my_data_in_bin()
            # abc = np.hstack((self._frame_to_process,
            #                 self._processor._processing.get_processed_frame(),
            #                 self._processor._processing.get_avg_frame()
            #                 ))
            # cv2.imshow('abc_'+self._attached_videoframe.name, abc)
            # cv2.waitKey(1)
            # cv2.imshow('vpu + '+self._attached_videoframe.name,self._processor._processing.get_processed_frame())
            # cv2.imshow('vpu_avg + ' + self._attached_videoframe.name, self._processor._processing.get_avg_frame())
            # cv2.waitKey(1)



if __name__ == '__main__':

    from common import VideoFrame
    from data_manager import DataBin

    cap = cv2.VideoCapture(0)
    v0 = VideoFrame('v0')

    _, initframe = cap.read()
    print "Initializing camera",
    for i in range(1,4):
        _,initframe = cap.read()
        print ".",
        time.sleep(1)

    gray_initframe = cv2.cvtColor(initframe,cv2.COLOR_BGR2GRAY)
    v0.set_init_frame(gray_initframe)
    v0.update_current_frame(gray_initframe)

    vpu0 = VideoProcessingUnit(processing_mode='dynamic_presence')
    vpu0.attach_to_frame(v0)
    vpu0.start_processing()

    db = DataBin()
    vpu0.attach_data_bin(db)

    while(v0.get_current_frame_number()<1000):
        _,frame = cap.read()
        print frame.shape[2]
        grayframe = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        print len(frame.shape), len(grayframe.shape)
        v0.update_current_frame(grayframe)
        cv2.imshow('frame', v0.get_current_frame_copy())
        cv2.imshow('initframe', v0.get_init_frame_copy())
        cv2.imshow('avg',vpu0._average_frame)
        cv2.imshow('lol',vpu0._processor._processing.get_processed_frame())
        cv2.waitKey(1) & 0xFF
        print "db data = ",db.get_collected_data()
    vpu0.stop_processing()



