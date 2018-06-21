import threading
from random import Random

import time

import logging

class DataManager(object):

    def __init__(self):
        self.data_pool = None
        self._data_dict={} # stores data in the form { DataBin_reference : whatever_data_it_has_collected }
        self._data_manager_thread = threading.Thread(name="DataManagerThread",target = self.run_data_collection)
        self._is_dm_thread_running = False
        self._data_avg_rate = 0.05

    def set_data_pool(self,shared_data_pool):
        self.data_pool = shared_data_pool

    def register_data_collector(self,DataCollector_dc):
        self._data_dict.update( { DataCollector_dc : 0 } )

    def update_dict_data(self,DataCollector_dc,dc_data):
        #DataCollector_dc._data_update_lock.acquire(blocking=True)
        self._data_dict.update( { DataCollector_dc : dc_data } )
        #DataCollector_dc._data_update_lock.release()

    def collect_all_data(self):
        for data_bin in self._data_dict.keys():
            #data_bin._data_update_lock.acquire()
            new_data = self.weighted_average_data(data_bin,data_bin.get_collected_data())
            self.update_dict_data(data_bin,new_data)
            #data_bin._data_update_lock.release()

    def weighted_average_data(self,bin,incoming_data):
        current_data = self._data_dict[bin]
        if current_data is None or incoming_data is None:
            current_data = 0
            incoming_data = 0
        return (1-self._data_avg_rate)*current_data + self._data_avg_rate*incoming_data
            #self.accumulator_array = (1 - AVGRATE) * self.accumulator_array + AVGRATE * np.asarray(listi,dtype=np.double)

    def get_data_mgr_data(self):
        return self._data_dict

    def put_data_in_data_pool(self,incoming_data):
        # acquire lock on data pool before entering function
        pass

    def run_data_collection(self):
        while(self._is_dm_thread_running):
            self.collect_all_data()
            logging.info(self._data_dict)
            data_pool_data = self._data_dict
            # TODO : acquire data pool lock
            self.put_data_in_data_pool(data_pool_data)
            # release data pool lock
            time.sleep(0.05)

    def start_data_manager(self):
        self._is_dm_thread_running = True
        self._data_manager_thread.start()

    def stop_data_manager(self):
        self._is_dm_thread_running = False

class DataBin:

    def __init__(self):
        self._collected_data = None
        self._attached_to_processing_unit = None
        self._data_manager = None
        #self._data_update_lock = threading.RLock()

    def attach_to_processing_unit(self,VideoProcessingUnit_vpu):
        self._attached_to_processing_unit = VideoProcessingUnit_vpu

    def detach_attached_processing_unit(self):
        self.clear_collected_data()
        self._attached_to_processing_unit = None

    def register_with_data_manager(self,DataManager_dm):
        self._data_manager = DataManager_dm
        self._data_manager.register_data_collector(self)

    def update_collected_data(self,incoming_data):
        #self._data_update_lock.acquire()
        self._collected_data = incoming_data
        #self._data_update_lock.release()

    def get_collected_data(self):
        #if(self._collected_data is None):
        #    raise UserWarning("_collected_data = None, i.e., No data was collected. This DataBin instance has probably not been attached to any processor.")
        return self._collected_data

    def clear_collected_data(self):
        self._collected_data = None


if __name__=='__main__':

    #from video_processing import VideoProcessingUnit, VideoFrame

    dm = DataManager()

    dc1 = DataBin()
    dc2 = DataBin()
    dc3 = DataBin()
    dc4 = DataBin()

    dc1.register_with_data_manager(dm)
    dc2.register_with_data_manager(dm)
    dc3.register_with_data_manager(dm)
    dc4.register_with_data_manager(dm)

    dc_list = [dc1,dc2,dc3,dc4]
    dm.start_data_manager()

    idx = 0
    while(True):
        print "idx = ",idx
        idx += 1
        for dc in dc_list:
            dc.update_collected_data(idx+1)
            time.sleep(0.01)
            #print dc.get_collected_data()
        print dm.get_data_mgr_data().viewvalues()
        time.sleep(0.05)


