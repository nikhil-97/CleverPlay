import os
import vidproc
import fileutils
import http_postman
import multiprocessing
from collections import defaultdict

def runMainScript():
    camslist = [0]  # Add video files as strings to this list for video file from disk

    site_url = 'http://www.findmysport.in/tennisfinal.php'
    datafile = './.data/.roidata.pkl'
    datamgdict = multiprocessing.Manager().dict()

    processlist = []

    roidataloaded, roi_data = fileutils.readRoiFromFile(datafile)

    for cam_ide in camslist:
        if roidataloaded:
            try:
                roi_info = roi_data[cam_ide]
            except KeyError:
                roi_info = None
        else:
            roi_info = None
        print "roi_info = ",roi_info
        p = multiprocessing.Process(target=vidproc.startcam, args = (cam_ide, datamgdict, roi_info),name = 'VideoProcess@%s'%str(cam_ide))
        p.start()
        processlist.append(p)

    print datamgdict
    p1 = multiprocessing.Process(target=http_postman.beginPostman, args=(site_url, datamgdict), name = 'HttpPostman@%s'% site_url)
    p1.start()
    processlist.append(p1)

    for process in processlist:
        process.join()

    print('End')
    return
    

if __name__ == '__main__':
    runMainScript()




























