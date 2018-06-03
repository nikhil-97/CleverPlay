from threading import RLock

class VideoFrame(object):
    def __init__(self,str_name):
        self.name = str_name
        self.current_frame = None
        self.init_frame = None
        self._frame_write_lock = RLock()

    def set_init_frame(self,incoming_init_frame):
        self.init_frame = incoming_init_frame

    def update_current_frame(self,incoming_frame):
        self.current_frame = incoming_frame

    def get_current_frame(self):
        return self.current_frame

    def get_init_frame(self):
        return self.init_frame
