import threading

import numpy as np
import cv2
from video_processing import VideoFrame, VideoProcessor


class RoiController(object):
    def __init__(self):
        self._attached_videoframe = None
        self._controlling_rois = dict()
        # holds info about the rois this controller is controlling as { RoiFrame : Attached VideoProcessor }
        self._is_running = True

    def attach_controller_to_videoframe(self,VideoFrame_vf):
        self._attached_videoframe = VideoFrame_vf

    def cropFromImage(self,image_to_be_cropped,( (topleft_x, topleft_y), (botright_x, botright_y) ) ):
        return image_to_be_cropped[topleft_y:botright_y, topleft_x:botright_x]

    def make_roiframes(self,roi_coords_dict):
        idx = 0
        for roi_name,roi_coords in roi_coords_dict.items():
            idx+=1
            # make an roi for each coordinate pair in the list
            roi = RoiFrame(roi_name)
            print roi.name
            roi.set_roi_coordinates(roi_coords[0],roi_coords[1])
            self._controlling_rois.update({roi:None})

    def get_roi_coords_for_attached_vframe(self):
        # get from file
        # lookup roi info using the attached video frame's name
        # return list of ( (x1,y1) , (x2,y2) )
        return {'Roi 1':((5,5),(50,50)),'Roi 2':((55,55),(50,50)),'Roi 3':((15,65),(50,50))}

    def attach_video_processors_to_controlling_rois(self):
        for roi in self._controlling_rois.keys():
            vp = VideoProcessor()
            vp.attach_to_frame(roi)
            self._controlling_rois.update({roi:vp})

    def start(self):
        t = threading.Thread(target=self.run)
        t.start()

    def initialize_rois(self):
        roi_coords_list = self.get_roi_coords_for_attached_vframe()
        self.make_roiframes(roi_coords_list)
        self.attach_video_processors_to_controlling_rois()

    def run(self):
        self.initialize_rois()
        while(self._is_running):
            #for each roi, crop roi from main videoframe
            self._attached_videoframe._access_lock.acquire()
            self._attached_videoframe_frame = self._attached_videoframe.get_video_frame()
            self._attached_videoframe._access_lock.release()
            for each_roiframe in self._controlling_rois.keys():
                #each_roiframe = RoiFrame('lol')
                # TODO : Lock each roiframe when updating. videoprocessing thread should be kept on hold while it is updating
                eachroi_coords = each_roiframe.get_roi_coordinates()
                croppedOutFromVideoFrame = self.cropFromImage(self._attached_videoframe.frame,eachroi_coords)
                each_roiframe.update_video_frame(croppedOutFromVideoFrame)

    def stop(self):
        self._is_running = False


class RoiFrame(VideoFrame):
    def __init__(self,str_roi_name):
        super(RoiFrame, self).__init__(str_roi_name)
        ( self._roi_topleft_x,self._roi_topleft_y ) = (0,0)
        ( self._roi_botright_x, self._roi_botright_y ) = (1, 1)

        # If you don't see the following grids properly, draw it on a piece of paper (-_-)
        # or adjust your IDE settings properly :/
        # Legend  : Me 8) 8) 8) :P :P :P

        # Legend for the grid? : X = (x1,y1) , O = (x2,y2)

    def set_roi_coordinates(self,(x1,y1),(x2,y2)):
        if (x2 > x1 and y2 > y1):

            # Case 1
            # (0,0)--1---2---3---> x-axis
            #  1|____|___|___|___
            #  2|____X___|___|___
            #  3|____|___|___|___
            #  4|____|___|___O___
            #  5|____|___|___|___

            ( self._roi_topleft_x, self._roi_topleft_y ) = (x1, y1)
            ( self._roi_botright_x, self._roi_botright_y ) = (x2, y2)
        elif (x2 < x1 and y2 < y1):

            # Case 2
            # (0,0)--1---2---3---
            #  1|____|___|___|___
            #  2|____O___|___|___
            #  3|____|___|___|___
            #  4|____|___|___X___
            #  5|____|___|___|___

            ( self._roi_topleft_x, self._roi_topleft_y ) = (x2, y2)
            ( self._roi_botright_x, self._roi_botright_y ) = (x1, y1)
        elif (x2 < x1 and y2 > y1):

            # Case 3
            # (0,0)--1---2---3---
            #  1|____|___|___|___
            #  2|____$___|___O___
            #  3|____|___|___|___
            #  4|____X___|__ $$___
            #  5|____|___|___|___
            # here $ and $$ should be top-left and bottom-right

            ( self._roi_topleft_x, self._roi_topleft_y ) = (x2, y1)
            ( self._roi_botright_x, self._roi_botright_y ) = (x1, y2)
        elif (x2 > x1 and y2 < y1):

            # Case 4
            # (0,0)--1---2---3---
            #  1|____|___|___|___
            #  2|____$___|___X___
            #  3|____|___|___|___
            #  4|____O___|__ $$___
            #  5|____|___|___|___
            # here $ and $$ should be top-left and bottom-right

            ( self._roi_topleft_x, self._roi_topleft_y ) = (x1, y2)
            ( self._roi_botright_x, self._roi_botright_y ) = (x2, y1)
        else:
            # Case 4
            # (0,0)--1---2---3---
            #  1|____|___|___|___
            #  2|____X___|___|___
            #  3|____|___|___|___
            #  4|____O___|__ |___
            #  5|____|___|___|___
            # in this case X,O lie on the same line XOXO XD
            # can't make a rectangle in such a case (# ._.)
            raise ArithmeticError

    def get_roi_coordinates(self):
        return ( ( self._roi_topleft_x, self._roi_topleft_y ) , ( self._roi_botright_x, self._roi_botright_y ) )

if __name__=='__main__':
    from numpy import ones,uint8

    vf1 = VideoFrame('Frame 1')
    vf1.update_video_frame(ones((300, 400), uint8))

    rctrlr = RoiController()
    rctrlr.attach_controller_to_videoframe(vf1)
    rctrlr.run()



