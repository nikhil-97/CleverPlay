import threading

import numpy as np
import cv2

import abc

class PresenceProcessing():

    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self._avg_rate = 0.05

    def set_averaging_rate(self,float_avg_rate):
        if(float_avg_rate > 1 or float_avg_rate < 0):
            raise ValueError('Trying to set an invalid averaging rate. The rate should be a float value between 0.0 and 1.0')
        self._avg_rate = float_avg_rate

    def accumulate_frames_to_background(self, frame, avgframe):
        """Accumulate frames to get the background"""
        cv2.accumulateWeighted(frame, avgframe, self._avg_rate)
        bkg = cv2.convertScaleAbs(avgframe)
        self._background_frame = bkg

    def subtract_from_background(self):
        subtract = cv2.GaussianBlur(cv2.absdiff(frame, self._background_frame), (5, 5), 3)
        _, threshold = cv2.threshold(subtract, 50, 200, cv2.THRESH_BINARY)
        RECT_KERNEL = cv2.getStructuringElement(cv2.MORPH_RECT, (11, 11))
        thresh_closed = cv2.dilate(threshold, RECT_KERNEL, 5)
        return thresh_closed

    def add_all_frame_pixels(self,np_ndarray_frame):
        return np.sum(np.sum(np_ndarray_frame, axis=0), axis=0)

    @abc.abstractmethod
    def process_frame(self):
        pass

    @abc.abstractmethod
    def get_presence_from_frame(self):
        pass

class StaticPresenceProcessing(PresenceProcessing):

    def __init__(self):
        PresenceProcessing.__init__(self)

    def process_frame(self):
        pass

    def get_presence_from_frame(self):
        return 1

class DynamicPresenceProcessing(PresenceProcessing):

    def __init__(self):
        PresenceProcessing.__init__(self)

    def process_frame(self):
        pass

    def get_presence_from_frame(self):
        # total = np.sum(np.sum(region, axis = 0), axis = 0) / 1000
        # 1/1000 is the scaling factor
        # return int(total > minsum)
        return 2

class VideoProcessor:
    def __init__(self,processing_mode):
        self._processing_mode = processing_mode
        self._processor = None
        if(self._processing_mode == 'static_presence'):
            self._processor = StaticPresenceProcessing()
        elif(self._processing_mode == 'dynamic_presence'):
            self._processor = DynamicPresenceProcessing()
        else:
            raise NameError('VideoProcessor takes only \'static_presence\' or \'dynamic_presence\' . Provided none of these two')

    def get_processing_mode(self):
        return self._processing_mode

    def process_frame(self):
        self._processor.process_frame()

    def get_presence(self):
        return self._processor.get_presence_from_frame()

class VideoProcessingUnit(object):

    def __init__(self,processing_mode):
        self._attached_videoframe = None
        self._attached_data_bin = None

        self._my_data = 0

        self._processing_thread = threading.Thread(target=self.run_processor)
        self._is_processing_thread_running = False

        self._processor = VideoProcessor(processing_mode)

    def attach_to_frame(self,VideoFrame_frame):
        if(VideoFrame_frame is None):
            raise ValueError("Trying to attach to None frame. Check if the VideoFrame has been correctly initialized")
        self._attached_videoframe = VideoFrame_frame

    def attach_data_bin(self,DataBin_dbin):
        self._attached_data_bin = DataBin_dbin
        self._attached_data_bin.attach_to_processing_unit(self)

    def start_processing(self):
        self._is_processing_thread_running = True
        self._processing_thread.start()

    def stop_processing(self):
        self._is_processing_thread_running = False
        print "Stopping %s 's VideoProcessingThread" % self._attached_videoframe.name

    def process_current_frame(self):
        # run_processor should have already acquired the lock before calling this
        self._processor.process_frame()

    def check_presence_now(self):
        print 'checking presence'
        self._my_data = self._processor.get_presence()

    def put_my_data_in_bin(self):
        print 'my_data = ',self._my_data
        self._attached_data_bin.update_collected_data(self._my_data)

    def run_processor(self):
        while (self._is_processing_thread_running):
            #print 'in thread'
            if(self._attached_videoframe is not None):
                pass
                # TODO : all videoframes are locked when updating their frame. video processing thread should acquire lock before processing
                #self._attached_videoframe.acquire_lock(blocking=True)
                self.process_current_frame()
                print 'frame = ',self._attached_videoframe.get_current_frame()
                self.check_presence_now()
                self.put_my_data_in_bin()


if __name__ == '__main__':

    from common import VideoFrame
    from data_manager import DataBin

    cap = cv2.VideoCapture(0)
    v0 = VideoFrame('v0')

    _,initframe = cap.read()
    v0.set_init_frame(initframe)

    vp0 = VideoProcessingUnit('dynamic_presence')
    vp0.attach_to_frame(v0)
    vp0.start_processing()

    db = DataBin()
    vp0.attach_data_bin(db)

    while(True):
        _,frame = cap.read()
        v0.update_current_frame(frame)
        cv2.imshow('frame',v0.get_current_frame())
        cv2.imshow('initframe', v0.get_init_frame())
        cv2.waitKey(10) & 0xFF
        print db.get_collected_data()




