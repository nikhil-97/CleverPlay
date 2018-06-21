import json
import pprint
import threading

import logging
import numpy as np
import cv2
import time
from video_processing import VideoProcessingUnit
from common import VideoFrame


class RoiController(object):
    def __init__(self):
        self._attached_videoframe = None
        self._controlling_rois = dict()
        # holds info about the rois this controller is controlling as
        # { RoiFrame : Attached VideoProcessingUnit }
        self._is_running = False
        self._rois_initialized = False

    def attach_controller_to_videoframe(self,VideoFrame_vf):
        self._attached_videoframe = VideoFrame_vf

    def cropFromImage(self,image_to_be_cropped,
                      ( (topleft_x,topleft_y),(botright_x,botright_y) ) ):
        return image_to_be_cropped[topleft_y:botright_y, topleft_x:botright_x]

    def make_roiframes(self,roi_coords_dict):
        idx = 0
        for roi_name,roi_coords in roi_coords_dict.items():
            idx+=1
            # make an roi for each coordinate pair in the list
            roi = RoiFrame(roi_name)
            roi.set_roi_coordinates(roi_coords[0],roi_coords[1])
            self._controlling_rois.update({roi:None})

    def get_roi_coords_for_attached_vframe(self):
        # get from file
        # lookup roi info using the attached video frame's name
        # return list of ( (x1,y1) , (x2,y2) )
        decoded_roidata = {}
        with open("roidata.json","r") as roidata_file:
            vf_roiinfo_list = json.load(roidata_file)
            for vf_roiinfo in vf_roiinfo_list:
                if(vf_roiinfo['VideoFrameName']==str(self._attached_videoframe.name)):
                    roidata = vf_roiinfo['ROIInfo']
                    for roidat in roidata:
                        name = roidat['ROIName']
                        coord1 = tuple(roidat['Coordinates']['Coordinate_1'])
                        coord2 = tuple(roidat['Coordinates']['Coordinate_2'])
                        decoded_roidata.update( { str(name) : ( coord1,coord2 ) } )


        print "decoded = ",decoded_roidata
        return decoded_roidata
        # return {'Roi 1':((5,5),(150,150)),'Roi 2':((150,150),(250,0)),'Roi 3':((0,0),(200,200))}

    def attach_video_processors_to_controlling_rois(self):
        for roi in self._controlling_rois.keys():
            vp = VideoProcessingUnit()
            vp.attach_to_frame(roi)
            self._controlling_rois.update( { roi : vp } )

    def get_controlling_rois(self):
        return self._controlling_rois.keys()

    def get_attached_video_processors(self):
        return self._controlling_rois.values()

    def start_roi_controller(self):
        t = threading.Thread(target=self.run,name="RoiControllerThread-VF_%s"%self._attached_videoframe.name)
        t.start()

    def update_init_frames_in_vpus(self):
        vpus = self.get_attached_video_processors()
        for vpu in vpus:
            vpu.update_initframe()

    def start_attached_video_processors(self):
        vpus = self.get_attached_video_processors()
        print "starting vpus = ",vpus
        for vpu in vpus:
            vpu.start_processing()

    def initialize_rois(self):
        roi_coords_list = self.get_roi_coords_for_attached_vframe()
        self.make_roiframes(roi_coords_list)
        self._rois_initialized = True

    def update_init_roiframes(self):
        for each_roiframe in self._controlling_rois.keys():
            eachroi_coords = each_roiframe.get_roi_coordinates()
            each_roiframe.set_init_frame(
                self.cropFromImage(self._attached_videoframe.get_init_frame_copy(), eachroi_coords))
            each_roiframe.set_init_frame_as_valid()

    def run(self):
        if(self._rois_initialized):
            self._is_running = True
            # allow thread running if roi's initialized
        else:
            raise RuntimeError(
                "ROIs have not been initialized correctly. Perhaps you forgot to call initialize_rois() ? ")

        while(self._is_running):

            for each_roiframe in self._controlling_rois.keys():
                eachroi_coords = each_roiframe.get_roi_coordinates()
                croppedOutFromVideoFrame = self.cropFromImage(self._attached_videoframe.get_current_frame_copy(), eachroi_coords)
                each_roiframe.update_current_frame(croppedOutFromVideoFrame)
                each_roiframe.set_current_frame_as_valid()
                #cv2.imshow(self._attached_videoframe.name,self._attached_videoframe.get_current_frame_copy())
                #cv2.imshow(each_roiframe.name,each_roiframe.get_current_frame_copy())
                #logging.info(str(each_roiframe.name)+"-\n"+str(each_roiframe.get_current_frame_copy()))
                #cv2.waitKey(1)
            time.sleep(0.01)

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
    from common import VideoFrame

    vf1 = VideoFrame('Main Frame')
    vf1.update_current_frame(255*ones((480, 640), uint8))

    rctrlr = RoiController()
    rctrlr.attach_controller_to_videoframe(vf1)
    rctrlr.initialize_rois()
    rctrlr.start_roi_controller()



