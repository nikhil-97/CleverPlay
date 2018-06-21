import threading

import common
import numpy as np
import cv2
import camera_manager
import time
from Tkinter import *
import json

QUIT_KEY = ord('q')
QUIT_ALL_KEY = ord('Q')
SAVE_KEY = ord('s')
SHOW_HELP = ord('h')
DRAW_ROIS = ord('r')
SHOW_ROIS = ord('v')
CANCEL_ROI_SETUP = ord('c')

HELP_STRING = '"h" - Show/Hide Help|"s" - Save|"q" - Quit without saving|"Q" - Quit All,doesn\'t save)|"r" - Draw ROIs|' \
              '"v" - Show ROIs|"c"-Cancel ROI'

class CalibrationManager(object):

    def __init__(self):
        self.calibration_viewer_threads=[]
        self.attached_videoframes=[]

    def attach_frame_to_display(self,VideoFrame_vframe):
        self.attached_videoframes.append(VideoFrame_vframe)

        vt = ViewThread(VideoFrame_vframe,self)
        ctrl = Controller()
        sm = SetupModel()
        vt.attach_controller(ctrl)
        vt.attach_model(sm)
        ctrl.attach_viewthread(vt)
        ctrl.attach_model(sm)
        self.calibration_viewer_threads.append(vt)

    def start_display(self):
        for dm_thread in self.calibration_viewer_threads:
            dm_thread.start()

    def stop_all_displays(self):
        print 'stopping all'
        for dm_thread in self.calibration_viewer_threads:
            dm_thread.stop()

    #TODO:
    #def removeThreadFromList(self,idx):
    #    self.display_manager_threads.remove(idx)

class ViewThread(threading.Thread):
    def __init__(self, VideoFrame_vframe, parent_DisplayManager):
        threading.Thread.__init__(self, name=VideoFrame_vframe.name + ' ViewThread')
        self._attached_frame = VideoFrame_vframe
        self._attached_frame_name = VideoFrame_vframe.name
        self.parent_display_manager = parent_DisplayManager
        self._thread_is_running = True
        self._show_help = True
        self._show_mouse_cursor = False
        self._mouse_cursor_coords = (0,0)
        self._attached_controller = None
        self._attached_model = None
        self._rois_already_setup = []
        self._setting_roi_now = False
        self._set_roi_coord1 = (0,0)
        self._show_set_rois = True

    def attach_controller(self,Controller_ctrl):
        self._attached_controller = Controller_ctrl

    def attach_model(self,SetupModel_sm):
        self._attached_model = SetupModel_sm

    def set_mouse_coords(self,mx,my):
        self._mouse_cursor_coords = (mx,my)

    def run(self):

        cv2.namedWindow(self._attached_frame_name)
        cv2.setMouseCallback(self._attached_frame_name, self._attached_controller.mouseHandler)

        while self._thread_is_running:
            copy = self._attached_frame.get_current_frame_copy()
            h,w = copy.shape[0],copy.shape[1]
            #helptext = textwrap.wrap(HELP_STRING,width = 20)
            if(self._show_help):
                helptext = HELP_STRING.split('|')
                start_x = 180
                start_y = 20
                line_spacing = 15
                for i,text in enumerate(helptext):
                    y = start_y + i*line_spacing
                    cv2.putText(copy,str(text),(w-start_x,y),cv2.FONT_HERSHEY_DUPLEX,0.4,(255,0,0),1,cv2.CV_AA)

            if (self._show_mouse_cursor):
                cv2.putText(copy,"Drawing ROIs",(int(0.4*w),int(0.9*h)),cv2.FONT_HERSHEY_DUPLEX,0.4,(255,0,0),1,cv2.CV_AA)
                cv2.putText(copy,str(self._mouse_cursor_coords),self._mouse_cursor_coords,cv2.FONT_HERSHEY_DUPLEX,0.4,(0,0,0),1,cv2.CV_AA)
                cv2.line(copy,(self._mouse_cursor_coords[0],0),(self._mouse_cursor_coords[0],h),(0,0,0),1,cv2.CV_AA)
                cv2.line(copy, (0,self._mouse_cursor_coords[1]), (w,self._mouse_cursor_coords[1]), (0, 0, 0), 1, cv2.CV_AA)
                cv2.circle(copy,self._mouse_cursor_coords,6,(0,0,0),1,cv2.CV_AA)
                if(self._setting_roi_now):
                    cv2.rectangle(copy,self._set_roi_coord1,self._mouse_cursor_coords,(0,0,0),2,cv2.CV_AA)


            if(self._show_set_rois):
                v1 = self._attached_model.get_set_rois()
                try:
                    self._rois_already_setup = v1[self._attached_frame]
                except KeyError:
                    pass
                for set_roi in self._rois_already_setup:
                    #set_roi = RoiWindow(self._attached_frame)
                    #set_roi.set_roi_name('lol')
                    #set_roi.set_coord1(100,100)
                    #set_roi.set_coord2(300, 300)

                    cv2.rectangle(copy,set_roi.get_coord1_xy(),set_roi.get_coord2_xy(),(255,0,0),2,cv2.CV_AA)
                    cv2.putText(copy, set_roi.get_roi_name(), (set_roi.get_coord1_xy()[0], set_roi.get_coord1_xy()[1] - 5),
                                cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 0, 0), 1, cv2.CV_AA)

            cv2.imshow(self._attached_frame_name, copy)

            key = cv2.waitKey(1) & 0xFF
            self._attached_controller.windowKeyHandler(key)

    def setting_roi_now(self,set,coord1_xy):
        self._setting_roi_now = set
        if(self._setting_roi_now is False):
            return
        self._set_roi_coord1 = coord1_xy

    def stop(self):
        self._thread_is_running = False
        print "Stopping %s" % self._attached_frame_name

class Controller:

    def __init__(self):
        self._attached_viewthread = None
        self._drawing_roi = False
        self.points_placed = 0
        self._first_corner = (0,0)
        self._roi_tracker_dict = {}
        self._attached_model = None

    def attach_viewthread(self,ViewThread_vt):
        self._attached_viewthread = ViewThread_vt

    def attach_model(self,SetupModel_sm):
        self._attached_model = SetupModel_sm

    def mouseHandler(self,event,x,y,flags,param):
        self._attached_viewthread.set_mouse_coords(x,y)
        if(self._attached_viewthread._show_mouse_cursor):
            if(event==cv2.EVENT_LBUTTONDOWN):

                self._drawing_roi = True
                self.points_placed += 1

                if(self.points_placed==1):
                    self._first_corner = (x,y)
                    self._attached_model.new_roi_window(self._attached_viewthread._attached_frame)
                    self._attached_model.set_active_roiwin_coord1(self._first_corner[0], self._first_corner[1])

                if(self.points_placed == 2):

                    self._attached_model.set_active_roiwin_coord2(x,y)
                    rn = self.show_roiname_user_entry_and_get_name()
                    self._attached_model.set_active_roiwin_name(rn)
                    self._attached_model.finish_roiwin_setup()
                    self.points_placed = 0
                    self._drawing_roi = False

                self._attached_viewthread.setting_roi_now(self._drawing_roi, self._first_corner)


    def windowKeyHandler(self,key):
        if key == QUIT_KEY:
            self._attached_viewthread.stop()
        elif key == QUIT_ALL_KEY:
            self._attached_viewthread.parent_display_manager.stop_all_displays()
        elif key == SHOW_HELP:
            self._attached_viewthread._show_help = not self._attached_viewthread._show_help
        elif key == DRAW_ROIS:
            self._drawing_roi = True
            self._attached_viewthread._show_mouse_cursor = not self._attached_viewthread._show_mouse_cursor
        elif key==SHOW_ROIS:
            self._attached_viewthread._show_set_rois = not self._attached_viewthread._show_set_rois
        elif key==CANCEL_ROI_SETUP:
            self._drawing_roi = False
            self.points_placed = 0
            self._attached_viewthread.setting_roi_now(self._drawing_roi, self._first_corner)
        elif key==SAVE_KEY:
            self._attached_model.save_roi_data_to_file()

    def show_roiname_user_entry_and_get_name(self):
        t = RoiNameEntryBox()
        t.mainloop()
        s = str(t.entrytext.get())
        return s

class RoiNameEntryBox(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.entrytext = StringVar()
        self.l = Label(self, text="Enter a name for this ROI.", font="serif 10").grid(column=0, row=0, pady=(5, 5),columnspan = 3)
        self.entry = Entry(self, relief=SUNKEN, bg="white", font="serif 10", textvariable=self.entrytext)
        self.entry.grid(column=1, row=1, padx=5,pady=5)

        self.okbutton = Button(self,text = "OK",command = self.destroy).grid(column = 2, row = 2,padx = 5,pady = 5)

class RoiWindow:
    def __init__(self,parent_VideoFrame):
        self.parent_videoframe = parent_VideoFrame
        self.coord1 = (0,0)
        self.coord2 = (1,1)
        self.roi_name = 'no roi name set'

    def set_roi_name(self,str_name):
        self.roi_name = str(str_name)

    def get_roi_name(self):
        return self.roi_name

    def set_coord1(self,x1,y1):
        self.coord1 = (x1,y1)

    def set_coord2(self,x1,y1):
        self.coord2 = (x1,y1)

    def get_coord1_xy(self):
        return self.coord1

    def get_coord2_xy(self):
        return self.coord2

class SetupModel:
    def __init__(self):
        self.rois_setup = {}     #of the form { parent_VideoFrame : [list of RoiWindows] }
        self.active_roiwin = None

    def get_set_rois(self):
        return self.rois_setup

    def new_roi_window(self,parent_VideoFrame):
        r = RoiWindow(parent_VideoFrame)
        self.active_roiwin = r

    def set_active_roiwin_coord1(self,x1,y1):
        self.active_roiwin.set_coord1(x1,y1)

    def set_active_roiwin_coord2(self, x2, y2):
        self.active_roiwin.set_coord2(x2, y2)

    def set_active_roiwin_name(self, str_name):
        if(len(str_name)==0):
            str_name = "No name set"
        self.active_roiwin.set_roi_name(str_name)

    def finish_roiwin_setup(self):
        try:
            self.rois_setup[self.active_roiwin.parent_videoframe].append(self.active_roiwin)
        except KeyError:
            self.rois_setup.update( { self.active_roiwin.parent_videoframe : [self.active_roiwin] })
        self.active_roiwin = None

    def save_roi_data_to_file(self):
        self.list_of_dicts_for_json = []
        for vf,roiwin_list in self.rois_setup.items():
            #print vf.name
            self.roiwins_list = []
            for each_roiwin in roiwin_list:
                self.roiwins_list.append( { "ROIName" : each_roiwin.get_roi_name(),
                                            "Coordinates" : {
                                                "Coordinate_1" : each_roiwin.get_coord1_xy() ,
                                                "Coordinate_2" : each_roiwin.get_coord2_xy()
                                                }
                                            })

            self.list_of_dicts_for_json.append( { "VideoFrameName" : vf.name, "ROIInfo" : self.roiwins_list} )

        # print "self.list_of_dicts_for_json = ",self.list_of_dicts_for_json
        print "Saved roi.json as "
        print json.dumps(self.list_of_dicts_for_json, indent=4,separators=(',', ': '))
        with open("roidata.json","w") as write_file:
            json.dump(self.list_of_dicts_for_json, write_file)


if __name__=='__main__':
    cm = camera_manager.CameraManager()
    cm.initialize_manager()

    calmgr = CalibrationManager()

    cam_readers = cm.get_cam_readers_list()

    for cr in cam_readers:
        vf = cr.get_attached_videoframe()
        calmgr.attach_frame_to_display(vf)
        cr.start_camreader()
        print("Waiting for valid VideoFrames")
        #logging.info("Waiting for valid VideoFrames")

        while (not cr._frames_valid):
            #logging.info("_")
            print("_ ")
            time.sleep(0.5)
        #logging.info("VideoFrames valid!")
        print("VideoFrames valid")

    calmgr.start_display()