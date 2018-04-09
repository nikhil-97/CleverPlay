"""SENDING DATA TO SERVER """
import requests
# import threading
import time

REQUESTS_DELAY = 1

class httpPostman:

    def __init__(self,url,managerdict):
        self.url = url
        self.datadict = managerdict
        #todo : get cam mapping from the dict passed
        #self.cam_court_map = cam_manager
        self.http()

    def http(self):
        courtmapped = False
        court1 = 0
        court2 = 0
        court3 = 0
        court4 = 0
        while True :
            print "self.datadict http = ",self.datadict
            try:
                court1 = self.datadict[1][0]
                court2 = self.datadict[1][1]
                court3 = self.datadict[1][2]
                court4 = self.datadict[1][3]
                print "trying court1 = ", court1, "court2 = ", court2, "court3 = ", court3, "court4 = ", court4
            except KeyError as e:
                print "key error",e
            #todo : get these from dictionary passed,not hardcoded

            print "data_dict",self.datadict
            print "court1 = ",court1,"court2 = ",court2,"court3 = ",court3,"court4 = ",court4

            query_args={'count1':str(1+court1),'count2':str(1+court2),'count3':str(1+court3),'count4':str(1+court4)}
            #TODO : change PHP code, so that it subtracts 1 from the request and shows it. this will be scalable later to any number of people

            print "query_args=",query_args
            # noinspection PyBroadException
            try:
                response = requests.post(self.url,params = query_args)
                print "response = ", response
                print response.url
            except :
                print "Error sending response"
                pass

            print "end of http"
            time.sleep(REQUESTS_DELAY)


def beginPostman(site_url,mgrdict):
    print "mgrdict = ", mgrdict
    postman = httpPostman(site_url,mgrdict)

