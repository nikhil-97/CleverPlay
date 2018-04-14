import cv2
import numpy as np
import vidproc
from collections import defaultdict
import fileutils

savedatafile = './.data/.roidata.pkl'
FONT = cv2.FONT_HERSHEY_SIMPLEX

class VideoCalibration:
    def __init__(self,cam_ide):
        self.cam = cam_ide
        self.cap = cv2.VideoCapture(self.cam)
        self.windowname = 'Calibrating Camera %s' % str(self.cam)
        self.roidataloaded = False
        cv2.namedWindow(self.windowname, cv2.WINDOW_AUTOSIZE)

    def run(self):
        while (self.cap.isOpened()):
            self.ret, self.frame1 = self.cap.read()
            if (self.ret == False):
                self.cap.release()
                break
            self.frame = cv2.cvtColor(self.frame1, cv2.COLOR_RGB2GRAY)
            ix = 0

            print " master_dict = ", master_dict


            cv2.putText(self.frame1,str(self.cam),(20,20),FONT,0.5,(0,0,255),2,cv2.CV_AA)

            cv2.imshow(self.windowname, self.frame1)
            self.key = cv2.waitKey(100) & 0xFF

            if(self.key == ord('r')):
                print type(self.frame)
                newroiwindow = vidproc.RoiWindow(self)
                newroi = vidproc.RoiDraw(self.windowname,newroiwindow)
                master_dict[self.cam].append(newroiwindow)

            if(self.key == ord('s')):
                savethread = threading.Thread(target = fileutils.saveRoiToFile,name = 'saveThread',args=( master_dict,savedatafile))
                savethread.start()
                savethread.join()

            if(self.key == ord('d')):
                print "Deleting file"
                master_dict.clear()
                fileutils.delete_data_file(savedatafile)

            if self.key == ord('x') or self.key == ord('X'):
                self.cap.release()
                return
        pass



def calibratecam(cam_ide):
    try:
        vc = VideoCalibration(cam_ide)
    except (cv2.cv.error,cv2.error) as e:
        print e
        print 'Error for cam id %s'%str(cam_ide)
        return
    vc.run()

if __name__=='__main__':
    import threading

    print "Running ROI Calibration"

    camslist = [1]
    threadlist = []
    #datamgdict = multiprocessing.Manager().dict()
    roi_info = None
    master_dict = defaultdict(list)

    for cam_ide in camslist:
        t = threading.Thread(target=calibratecam, args = (cam_ide,))
        t.start()
        threadlist.append(t)
    for thread in threadlist:
        thread.join()

    print "ROI Data saved to %s : " % savedatafile,fileutils.readRoiFromFile(savedatafile)
