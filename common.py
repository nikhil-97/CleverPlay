from threading import RLock

class VideoFrame(object):
    def __init__(self,str_name):
        self.name = str_name
        self._frame_number = 0
        self.current_frame = None
        self.init_frame = None
        self._frame_write_lock = RLock()

    def set_init_frame(self,incoming_init_frame):
        self.init_frame = incoming_init_frame
        self._frame_number += 1

    def acquire_lock(self,blocking):
        self._frame_write_lock.acquire(blocking)

    def release_lock(self):
        self._frame_write_lock.release()

    def update_current_frame(self,incoming_frame):
        self.acquire_lock(True)
        self.current_frame = incoming_frame
        self.release_lock()
        self._frame_number += 1

    def get_current_frame_number(self):
        return self._frame_number

    def get_current_frame(self):
        return self.current_frame

    def get_init_frame(self):
        return self.init_frame
