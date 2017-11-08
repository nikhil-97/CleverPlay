"""SENDING DATA TO SERVER """
import requests
# import threading
import time

REQUESTS_DELAY = 60
class httpPostman:

    def __init__(self,url,managerdict,cam_manager):
        self.url = url
        self.datadict = managerdict
        #todo : get cam mappign from the dict passed
        #self.cam_court_map = cam_manager
        self.http()#self.datadict,self.cam_court_map)

    def http(self):
        courtmapped = False
        court1 = 0
        court2 = 0
        while True :

            #if(courtmapped):
            try:
                court1 = self.datadict[0]
                court2 = self.datadict[1]
            except KeyError:
                pass
            #todo : get these from dictionary passed,not hardcoded

            print "data_dict",self.datadict
            print "court1 = ",court1,"court2 = ",court2
            query_args={'count1':str(1+court1),'count2':str(1+court2)}
            #TODO : change PHP code, so that it subtracts 1 from the request and shows it. this will be scalable later to any number of people

            print "query_args=",query_args
            # noinspection PyBroadException
            try:
                #response = self.send_request(self.url, query_args)
                response = requests.post(self.url,params = query_args)
                print "response = ", response
                print response.url
            except :
                print "Error sending response"
                pass

            print "end of http"
            time.sleep(REQUESTS_DELAY)
        #t3 = threading.Timer(1.0, beginPostman, args=(self.url,self.datadict,)).start()


def beginPostman(site_url,mgrdict,cam_manager):
    postman = httpPostman(site_url,mgrdict,cam_manager)
    print "mgrdict = ",mgrdict

