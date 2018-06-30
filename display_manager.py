import threading

import cv2
import logging


QUIT_KEY = ord('q')
QUIT_ALL_KEY = ord('Q')

class DisplayManager(object):

	def __init__(self):
		self.attached_videoframes=[]
		self.display_thread = threading.Thread(name = 'DisplayManagerThread', target = self.show_displays)
		self._is_display_manager_running = False

	def attach_frame_to_display(self,VideoFrame_vframe):
		self.attached_videoframes.append(VideoFrame_vframe)

	def start_display(self):
		logging.debug("Display Manager Started")
		self._is_display_manager_running = True
		self.display_thread.start()

	def stop_all_displays(self):
		logging.info("Display Manager Stopped")
		self._is_display_manager_running = False

	def show_displays(self):
		while(self._is_display_manager_running):
			for vf in self.attached_videoframes:
				self.display_attached_frame(vf)
        
	def display_attached_frame(self,VideoFrame_vf):
        
		frame_name = VideoFrame_vf.name
		frame_number = VideoFrame_vf.get_current_frame_number()
		current_frame_copy = VideoFrame_vf.get_current_frame_copy()

		#print self._attached_frame.name,self._attached_frame.get_current_frame_copy(), type(self._attached_frame.get_current_frame_copy()[0][0])
		cv2.putText(current_frame_copy,str(frame_number),(100,100),cv2.FONT_HERSHEY_COMPLEX,0.5,(255,0,0),1,cv2.CV_AA)

		cv2.imshow(frame_name,current_frame_copy)
		key = cv2.waitKey(10) & 0xFF
		if key == QUIT_KEY or key== QUIT_ALL_KEY:
			self.stop_all_displays()

    #TODO:
    #def removeThreadFromList(self,idx):
    #    self.display_manager_threads.remove(idx)


if __name__=='__main__':

	import common
	from numpy import ones,uint8,random, dtype, array, asarray
	import numpy as np

	logging.basicConfig(level=logging.INFO)

	disp_mgr = DisplayManager()

	vf1 = common.VideoFrame('Frame 1')
	vf2 = common.VideoFrame('Frame 2')

	vf2.update_current_frame(np.asarray(255*ones((300, 400), np.uint8)))
	vf1.update_current_frame(np.asarray(random.random_integers(low=0,high=255, size=(480,640)),np.uint8))
	
	disp_mgr.attach_frame_to_display(vf1)
	disp_mgr.attach_frame_to_display(vf2)

	disp_mgr.start_display()


