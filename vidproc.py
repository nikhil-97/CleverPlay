import threading

import fileutils
import http_postman
import numpy as np
import cv2
import sys
import multiprocessing
from collections import defaultdict
import threading


cv2.setUseOptimized(True)
master_dict= defaultdict(list)

AVGRATE = 0.005
min_presence = 150
max_presence_trackbar = 500
FONT = cv2.FONT_HERSHEY_SIMPLEX

savedatafile = './.data/.roidata.pkl'

site_url = '127.0.0.1'

class VideoProcessor:

    def __init__(self,cam_id,managerdict,roiinfo):
        self.cam = cam_id
        self.cap = cv2.VideoCapture(self.cam)
        self.initret, self.initframe = self.cap.read()
        self.avgframe = np.float32(cv2.cvtColor(self.initframe, cv2.COLOR_RGB2GRAY))
        self.windowname = 'Video_' + str(self.cam)
        cv2.namedWindow(self.windowname, cv2.WINDOW_AUTOSIZE)
        self.draw = False
        master_dict.setdefault(self.cam, [])
        self.data_dict = managerdict
        self.presence = 0
        self.roidataloaded = False
        self.roi_xyz = roiinfo # todo : Change this variable name ASAP
        self.rois_loaded = False # todo : CHange this variable name ASAP


    def cannyAuto(self,image1, sigma = 0.75):
        ##From pyimagesearch
        image = cv2.GaussianBlur(image1, (3, 3), 3)
        median = np.median(image)
        low = int(max(0, (1.0 - sigma) * median))
        high = int(min(255, (1.0 + sigma) * median))
        canny = cv2.Canny(image, low, high)
        return canny

    @classmethod
    def subBkg(self,frame, avgframe):
        cv2.accumulateWeighted(frame, avgframe, AVGRATE)
        bkg = cv2.convertScaleAbs(avgframe)
        subtract = cv2.GaussianBlur(cv2.absdiff(frame, bkg), (5, 5), 3)
        _, threshold = cv2.threshold(subtract, 50, 200, cv2.THRESH_BINARY)
        #TODO : make this threshold dynamic i.e. not hardcoded
        RECT_KERNEL = cv2.getStructuringElement(cv2.MORPH_RECT, (11, 11))
        thresh_closed = cv2.dilate(threshold, RECT_KERNEL, 5)
        # frame = cv2.bitwise_and(frame,thresh_closed)
        return thresh_closed

    @classmethod
    def checkPresence(self,region, minsum):
        total = np.sum(np.sum(region, axis = 0), axis = 0) / 1000
        # 1/1000 is the scaling factor
        return int(total > minsum)

    def getCurrentFrame(self):
        return self.frame

    def run(self):
        overwrite_authorized = False
        while (self.cap.isOpened()):
            self.ret, self.frame1 = self.cap.read()
            if (self.ret == False):
                self.cap.release()
                break
            self.frame = cv2.cvtColor(self.frame1, cv2.COLOR_RGB2GRAY)
            ix = 0
            self.presence = 0
            if (self.roi_xyz != None and self.rois_loaded==False):
                for rois in self.roi_xyz:
                    newroi = RoiWindow(self)
                    newroi.setRoiBounds((rois[0], rois[1]), (rois[2], rois[3]))
                    #newroi.roi_done = True
                    newroi.run()
                    print "newroi = ", newroi
                    master_dict[self.cam].append(newroi)

                self.rois_loaded = True

            for x in master_dict:
                listi = []
                for m in master_dict[x]:
                    cv2.rectangle(self.frame1, m.getRoiBounds()[0],m.getRoiBounds()[1], (255, 0, 0), 2, cv2.CV_AA)
                    listi.append(m.presence)

            print "listi = ",listi

            self.data_dict[self.cam] = listi[:]
            print "self.data_dict = ", self.data_dict


            cv2.putText(self.frame1,str(self.cam),(20,20),FONT,0.5,(0,0,255),2,cv2.CV_AA)
            if(self.roi_xyz==None):
                cv2.putText(self.frame1, "Doesn't look like there are any ROIs. Run calibrateROI.py first", (50, 350), FONT, 0.5, (0, 0, 255), 1, cv2.CV_AA)

            cv2.imshow(self.windowname, self.frame1)
            self.key = cv2.waitKey(50) & 0xFF

            if self.key == ord('x') or self.key == ord('X'):
                self.cap.release()
                sys.exit(1)

def cropBounded(img, x1, y1, x2, y2):
    # global function because it is shared by both VideoProcessor and RoiDraw.
    return img[y2:y1, x2:x1] if (x1 > x2 and y1 > y2) else img[y1:y2, x1:x2]

class RoiWindow:
    def __init__(self,parent):
        self.parent = parent
        self.parentframe = self.parent.frame
        self.roi_croppedimg=None
        self.roi_croppedimg_init = np.zeros((1,1),np.uint8)
        self.roi_avg = np.zeros((1,1),np.float32)
        self.roi_bkgsub = np.zeros((1,1),np.uint8)
        self.presence = 0

    def setRoiBounds(self,(roix1,roiy1),(roix2,roiy2)):
        (self.roi_x1, self.roi_y1) = (roix1, roiy1)
        (self.roi_x2, self.roi_y2) = (roix2, roiy2)
        self.roi_croppedimg_init = cropBounded(self.parentframe,self.roi_x1,self.roi_y1,self.roi_x2,self.roi_y2)
        self.roi_avg = np.float32(self.roi_croppedimg_init)

    def getRoiBounds(self):
        return ((self.roi_x1, self.roi_y1),(self.roi_x2, self.roi_y2))

    def run(self):
        t = threading.Thread(target=self.runRoi)
        t.start()
        #t.join()

    def runRoi(self):
        while(1):
            cv2.rectangle(self.parentframe, (self.roi_x1, self.roi_y1), (self.roi_x2, self.roi_y2), (0, 255, 0), 2)
            self.roi_croppedimg = cropBounded(VideoProcessor.getCurrentFrame(self.parent), self.roi_x1, self.roi_y1, self.roi_x2, self.roi_y2)
            #cv2.imshow('Cropped_'+str(hash(self)),self.roi_croppedimg)
            self.roi_bkgsub = VideoProcessor.subBkg(self.roi_croppedimg, self.roi_avg)
            cv2.imshow('Bkg_Cropped_'+str(hash(self)),self.roi_bkgsub)
            cv2.waitKey(50)
            self.presence = VideoProcessor.checkPresence(self.roi_bkgsub, 150)
            #print "presence = ",self.presence

class RoiDraw:
    def __init__(self,callerwindow,roiwindow):
        self.drawingwindow = callerwindow
        #cv2.createTrackbar('Presence Size', self.drawingwindow, min_presence, max_presence_trackbar, nothing)
        cv2.setMouseCallback(self.drawingwindow, self.drawRoi,self)

        self.newRoiInstance = roiwindow
        self.newRoiInstance.setRoiBounds((10,10),(20,20))
        self.roi_done = False
        self.point=1
        (self.roi_x1,self.roi_y1)=(0,0)
        (self.roi_x2, self.roi_y2) = (1, 1)

    @staticmethod
    def drawRoi(event, x, y, flags, param):
        roiDrawClass=param
        if event == cv2.EVENT_LBUTTONDOWN and roiDrawClass.roi_done == False:
            print 'drawing roi in %s'%(roiDrawClass.drawingwindow)
            if roiDrawClass.point == 1:
                roiDrawClass.roi_x1, roiDrawClass.roi_y1 = x, y
            elif roiDrawClass.point == 2:
                roiDrawClass.roi_x2, roiDrawClass.roi_y2 = x, y
                roiDrawClass.roi_done = True
            roiDrawClass.point = (roiDrawClass.point + 1 if roiDrawClass.point <= 2 else 1)
            if(roiDrawClass.roi_done==True):
                roiDrawClass.initRoi()

        elif event == cv2.EVENT_RBUTTONDBLCLK:
            roiDrawClass.resetRoi()

    def initRoi(self):
        self.newRoiInstance.setRoiBounds((self.roi_x1, self.roi_y1), (self.roi_x2, self.roi_y2))
        print "initRoi",(self.roi_x1, self.roi_y1), (self.roi_x2, self.roi_y2)

def nothing(x):
    pass

def startcam(cam_ide,datamanager,roi_info):
    try:
        c = VideoProcessor(cam_ide,datamanager,roi_info)
    except (cv2.cv.error,cv2.error) as e:
        print 'Error %s for cam id %s' % (str(e),str(cam_ide))
        return

    print('Video from cam id %s Start')%str(cam_ide)
    c.run()


if __name__ == '__main__':
    import multiprocessing

    # cam = cv2.VideoCapture('C:\\Python27\\Capture.avi')
    camslist=[0] #Add video files as strings to this list for video file from disk

    processlist=[]
    datamgdict = multiprocessing.Manager().dict()

    master_dict= defaultdict(list)
    datafile = './.data/.roidata.pkl'
    roidataloaded, roi_data = fileutils.readRoiFromFile(datafile)

    for cam_ide in camslist:
        if roidataloaded:
            try:
                roi_info = roi_data[cam_ide]
            except KeyError:
                roi_info = None
        else:
            roi_info = None
        print "roi_info = ", roi_info

    for cam_ide in camslist:
        p = multiprocessing.Process(target=startcam, args=(cam_ide,datamgdict,roi_info),name='VideoProcess'+str(cam_ide))
        processlist.append(p)
        p.start()

    for process in processlist:
        process.join()

    print('Video End')
    #cv2.destroyAllWindows()
