from threading import RLock

import logging


class VideoFrame(object):
    def __init__(self,str_name):
        self.name = str_name
        self._frame_number = 0
        self.current_frame = None
        self.init_frame = None
        self._init_frame_valid = False
        self._current_frame_valid = False
        #self._frame_write_lock = RLock()

    def set_init_frame(self,incoming_init_frame):
        self.init_frame = incoming_init_frame.copy()
        self._frame_number = 1

    def set_init_frame_as_valid(self):
        self._init_frame_valid = True

    def is_init_frame_valid(self):
        return self._init_frame_valid

    def set_current_frame_as_valid(self):
        self._current_frame_valid = True

    def is_current_frame_valid(self):
        return self._current_frame_valid

    def acquire_lock(self,blocking):
        #self._frame_write_lock.acquire(blocking)
        pass

    def release_lock(self):
        #self._frame_write_lock.release()
        pass

    def update_current_frame(self,incoming_frame):
        self.acquire_lock(True)
        self.current_frame = incoming_frame.copy()
        self.release_lock()
        self._frame_number += 1

    def get_current_frame_number(self):
        return self._frame_number

    def get_current_frame_copy(self):
        return self.current_frame.copy()

    def get_init_frame_copy(self):
        return self.init_frame.copy()
