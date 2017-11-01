import cv2
import numpy as np
import vidproc
import http_postman
import multiprocessing

if __name__=='__main__':
    camslist=[0,1,2] #Add video files as strings to this list for video file from disk
    #camslist=['tennis2.avi','tennis3.avi']
    site_url = 'http://172.16.0.30/httpclient.html'

    courtmapping = {0: 'court1', 1: 'court2'}

    processlist=[]

    datamanager = multiprocessing.Manager()
    cameramanager = multiprocessing.Manager()
    datamgdict = datamanager.dict()
    cam_mgr = cameramanager.dict(courtmapping)

    for cam_ide in camslist:
        p = multiprocessing.Process(target=vidproc.startcam, args=(cam_ide,datamgdict,),name='VideoProcess@%s'%(str(cam_ide)))
        p.start()
        processlist.append(p)

    p1 = multiprocessing.Process(target=http_postman.beginPostman, args=(site_url,datamgdict,cam_mgr),name='HttpPostman@%s'%(site_url))
    p1.start()
    processlist.append(p1)

    for process in processlist:
        process.join()

    print('End')
    #cv2.destroyAllWindows()