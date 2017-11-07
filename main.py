import os
import vidproc
import fileutils
import http_postman
import multiprocessing

if __name__ == '__main__':

    camslist = [0]  # Add video files as strings to this list for video file from disk

    site_url = 'http://172.16.0.30/httpclient.html'
    datafile = './roidata.pkl'

    courtmapping = {0: 'court1', 1: 'court2'}

    datamgdict = multiprocessing.Manager().dict()
    cam_mgr = multiprocessing.Manager().dict(courtmapping)

    processlist = []

    roidataloaded, roi_data = fileutils.readRoiFromFile(datafile)

    for cam_ide in camslist:
        if roidataloaded:
            try:
                roi_info = roi_data[cam_ide]
            except KeyError:
                pass
        else:
            roi_info = None
        print "roi_info = ",roi_info
        p = multiprocessing.Process(target=vidproc.startcam, args = (cam_ide, datamgdict, roi_info),name = 'VideoProcess@%s'%(str(cam_ide)))
        p.start()
        processlist.append(p)

    p1 = multiprocessing.Process(target=http_postman.beginPostman, args=(site_url, datamgdict, cam_mgr), name = 'HttpPostman@%s'%(site_url))
    p1.start()
    processlist.append(p1)

    for process in processlist:
        process.join()

    print('End')