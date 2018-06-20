from threading import RLock

import logging


class VideoFrame(object):
    def __init__(self,str_name):
        """Constructor
        :param str_name: The name to set to this VideoFrame instance
        """
        self.name = str_name
        self._frame_number = 0
        self.current_frame = None
        self.init_frame = None
        self._init_frame_valid = False
        self._current_frame_valid = False

    def set_init_frame(self,incoming_init_frame):
        """
        Sets the init_frame for this VideoFrame instance
        :param incoming_init_frame:
        :return: None
        """
        self.init_frame = incoming_init_frame.copy()
        self._frame_number = 1

    def set_init_frame_as_valid(self):
        self._init_frame_valid = True

    def is_init_frame_valid(self):
        return self._init_frame_valid

    def update_current_frame(self,incoming_frame):
        self.current_frame = incoming_frame.copy()
        self._frame_number += 1

    def set_current_frame_as_valid(self):
        self._current_frame_valid = True

    def is_current_frame_valid(self):
        return self._current_frame_valid

    def get_current_frame_number(self):
        return self._frame_number

    def get_init_frame_copy(self):
        if self.init_frame is None :
            return None
        return self.init_frame.copy()

    def get_current_frame_copy(self):
        if self.current_frame is None :
            return None
        return self.current_frame.copy()