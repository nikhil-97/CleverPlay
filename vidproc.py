import numpy as np
import cv2
import sys
from collections import defaultdict

cv2.setUseOptimized(True)
master_dict= defaultdict(list)

AVGRATE = 0.05
min_presence = 250
max_presence_trackbar = 500
FONT = cv2.FONT_HERSHEY_SIMPLEX

class VideoProcessor:

    def __init__(self,cam_id,managerdict):
        self.cam = cam_id
        self.cap = cv2.VideoCapture(self.cam)
        self.initret, self.initframe = self.cap.read()
        self.avgframe = np.float32(cv2.cvtColor(self.initframe, cv2.COLOR_RGB2GRAY))
        self.windowname = 'Video_' + str(self.cam)
        cv2.namedWindow(self.windowname, cv2.WINDOW_AUTOSIZE)
        cv2.createTrackbar('Presence Size', self.windowname, min_presence, max_presence_trackbar, nothing)
        #self.mouse_x,self.mouse_y=0,0
        self.draw = False
        master_dict.setdefault(self.cam, [])
        self.data_dict = managerdict
        self.presence = 0

    def cannyAuto(self,image1, sigma = 0.75):
        ##From pyimagesearch
        image = cv2.GaussianBlur(image1, (3, 3), 3)
        median = np.median(image)
        low = int(max(0, (1.0 - sigma) * median))
        high = int(min(255, (1.0 + sigma) * median))
        canny = cv2.Canny(image, low, high)
        return canny

    @classmethod
    def subBkg(self,frame, avgframe, AVGRATE):
        cv2.accumulateWeighted(frame, avgframe, AVGRATE)
        bkg = cv2.convertScaleAbs(avgframe)
        subtract = cv2.GaussianBlur(cv2.absdiff(frame, bkg), (5, 5), 3)
        _, threshold = cv2.threshold(subtract, 50, 200, cv2.THRESH_BINARY)
        #TODO : make this threshold dynamic i.e. not hardcoded
        RECT_KERNEL = cv2.getStructuringElement(cv2.MORPH_RECT, (11, 11))
        thresh_closed = cv2.dilate(threshold, RECT_KERNEL, 5)
        # frame = cv2.bitwise_and(frame,thresh_closed)
        return thresh_closed

    def run(self):
        while (self.cap.isOpened()):
            self.ret, self.frame1 = self.cap.read()
            if (self.ret == False):
                self.cap.release()
                break
            self.frame = cv2.cvtColor(self.frame1, cv2.COLOR_RGB2GRAY)
            # self.cannyframe = self.cannyAuto(self.frame)
            # self.bkgsubbed = self.subBkg(self.frame, self.avgframe, AVGRATE)
            ix = 0
            self.presence = 0
            for roiinstance in master_dict[self.cam]:
                cv2.rectangle(self.frame1, (roiinstance.roi_x1, roiinstance.roi_y1),
                              (roiinstance.roi_x2, roiinstance.roi_y2), (0, 255, 0), 2)
                if (roiinstance.roi_done):
                    roiinstance.roi_croppedimg = cropBounded(roiinstance.caller.frame, roiinstance.roi_x1, roiinstance.roi_y1,
                                                          roiinstance.roi_x2, roiinstance.roi_y2)
                    cv2.imshow('Cropped_' + str(self.cam) + str(ix), roiinstance.roi_croppedimg)
                    roiinstance.roi_bkgsub = self.subBkg(roiinstance.roi_croppedimg, roiinstance.roi_avg, AVGRATE)
                    cv2.imshow('Bkg_Cropped_' + str(self.cam) + str(ix), roiinstance.roi_bkgsub)
                    cv2.waitKey(1)
                    self.presence += self.checkPresence(roiinstance.roi_bkgsub,min_presence)
                    ix += 1
            self.data_dict[self.cam] = self.presence
            cv2.putText(self.frame1,str(self.cam),(10,10),FONT,0.5,(0,0,255),2,cv2.CV_AA)
            cv2.imshow(self.windowname, self.frame1)
            self.key = cv2.waitKey(1) & 0xFF
            if(self.key==ord('r')):
                newroi = RoiDraw(self)
                master_dict[self.cam].append(newroi)
                print "master_dict = ",master_dict.items()
            if self.key == ord('x') or self.key == ord('X'):
                self.cap.release()
                sys.exit(1)

    def checkPresence(self,region, minsum):
        total = np.sum(np.sum(region, axis=0), axis=0) / 1000
        # 1/1000 is the scaling factor
        return int(total > minsum)

def cropBounded(img, x1, y1, x2, y2):
    return img[y2:y1, x2:x1] if (x1 > x2 and y1 > y2) else img[y1:y2, x1:x2]

class RoiDraw:
    def __init__(self,args):
        self.caller = args
        self.drawingwindow = self.caller.windowname
        self.point=1
        (self.roi_x1,self.roi_y1)=(0,0)
        (self.roi_x2, self.roi_y2) = (1, 1)
        self.roi_done=False
        self.roi_croppedimg=None
        self.roi_croppedimg_init = np.zeros((1,1),np.uint8)
        self.roi_avg = np.zeros((1,1),np.float32)
        self.roi_bkgsub = np.zeros((1,1),np.uint8)
        cv2.setMouseCallback(self.drawingwindow, self.drawRoi,self)


    @staticmethod
    def drawRoi(event, x, y, flags, param):
        roiclass=param
        if event == cv2.EVENT_LBUTTONDOWN and roiclass.roi_done == False:
            print 'drawing roi in %s'%(roiclass.drawingwindow)
            if roiclass.point == 1:
                roiclass.roi_x1, roiclass.roi_y1 = x, y
            elif roiclass.point == 2:
                roiclass.roi_x2, roiclass.roi_y2 = x, y
                roiclass.roi_done = True
            roiclass.point = (roiclass.point + 1 if roiclass.point <= 2 else 1)
            roiclass.roi_croppedimg_init = cropBounded(roiclass.caller.frame, roiclass.roi_x1,
                                                          roiclass.roi_y1, roiclass.roi_x2, roiclass.roi_y2)
            roiclass.roi_avg = np.float32(roiclass.roi_croppedimg_init)
            print (roiclass.roi_x1, roiclass.roi_y1), (roiclass.roi_x2, roiclass.roi_y2)

        elif event == cv2.EVENT_RBUTTONDBLCLK:
            roiclass.resetRoi()

    def resetRoi(self):
        master_dict.pop(self.caller.cam, None)

def nothing(x):
    pass

def startcam(cam_ide,queue):

    try:
        c = VideoProcessor(cam_ide,queue)
    except (cv2.cv.error,cv2.error) as e:
        print e
        print 'Error for cam id %s'%str(cam_ide)
        return

    print('Video from cam id %s Start')%str(cam_ide)
    c.run()


if __name__ == '__main__':
    import multiprocessing

    # cam = cv2.VideoCapture('C:\\Python27\\Capture.avi')
    camslist=[0,1,2,3] #Add video files as strings to this list for video file from disk

    processlist=[]

    master_dict= defaultdict(list)
    for cam_ide in camslist:
        p = multiprocessing.Process(target=startcam, args=(cam_ide,),name='VideoProcess'+str(cam_ide))
        processlist.append(p)
        p.start()

    for process in processlist:
        process.join()

    print('Video End')
    #cv2.destroyAllWindows()
